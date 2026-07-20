<!--
question:
  id: 03.database-redis-persistence
  topic: 03.database
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [03.database, Redis, redis]
-->

# Redis 持久化深度对比

## 引子：Redis 重启后，数据去哪了？

```
Redis 是内存数据库。
如果服务器宕机、Redis 进程被 kill——
内存里的数据就全没了？
```

是的，除非你开启了持久化。

Redis 提供两种持久化方式：
- **RDB（快照）**：定时把内存数据 dump 到磁盘 → 恢复快，但可能丢最近几分钟的数据
- **AOF（日志）**：记录每一次写操作 → 数据最完整，但文件大、恢复慢
- **混合持久化**：RDB 基线 + AOF 增量 → 两全其美

选哪种？看你能容忍丢多少数据。

---

> 📚 **前置知识**：[Redis](../../../03.database/07-redis/README.md)

## 一、核心原理

**RDB（内存快照）**：在某个时间点将内存数据集完整 dump 到磁盘生成二进制文件（`dump.rdb`）。本质是全量数据的"照片"，文件紧凑、恢复快，但两次快照间数据会丢失。

**AOF（命令日志）**：记录所有写操作命令，以协议文本格式追加到文件（`appendonly.aof`）。重启时重放命令重建数据。本质是写操作的"录像"，数据安全性高（最多丢1秒），但文件大、恢复慢。

**混合持久化（Redis 4.0+）**：AOF 重写时将当前数据以 RDB 格式写入开头，后续增量以 AOF 格式追加。本质是 RDB 基线 + AOF 增量，兼顾恢复速度和数据安全。

---

## 二、RDB 详解

### 2.1 bgsave 流程（fork + COW）

```
1. 主进程 fork() 创建子进程（阻塞，采用 COW 机制）
2. 子进程遍历数据库，序列化 key-value 写入临时 RDB 文件
3. 完成后原子替换旧 RDB 文件
```

**关键点**：`fork()` 期间主进程阻塞，无法处理请求。

### 2.2 COW 内存影响
父子进程共享物理内存页，父进程写时内核复制被修改的页。

| 场景 | COW 额外内存占用 |
|------|------------------|
| 写操作极少 | ~0% |
| 正常业务负载 | 10%-30% |
| 高频写操作 | 50%-100% |

> ⚠️ **陷阱**：32GB+ 内存且写频繁时，COW 可能触发 OOM Killer。

### 2.3 RDB 触发方式

```bash
SAVE    # 阻塞式（生产慎用）
BGSAVE  # 后台异步（推荐）
```

自动触发（redis.conf）：
```conf
save 900 1     # 900秒内至少1个key被修改
save 300 10    # 300秒内至少10个key被修改
save 60 10000  # 60秒内至少10000个key被修改
```

其他触发：主从复制初始化、FLUSHALL 前、Redis 关闭时。

### 2.4 RDB 文件格式

```
+------------------+
|  REDIS           |  ← Magic String (5字节)
+------------------+
|  version         |  ← RDB 版本号
+------------------+
|  辅助信息区       |
+------------------+
|  0xFE + db_num   |  ← 数据库标识
+------------------+
|  键值对数据区     |  ← 类型+key+value+过期时间
+------------------+
|  EOF (0xFF)      |
+------------------+
|  checksum        |  ← CRC64 校验和
+------------------+
```

| 类型标识 | 含义 |
|----------|------|
| 0x00-0x04 | String/List/Set/ZSet/Hash |
| 0x05-0x06 | ZipList/IntSet |
| 0x07 | QuickList/ListPack（7.0+） |

### 2.5 优缺点

**优点**：文件紧凑、恢复快、性能影响小、适合大规模数据
**缺点**：数据安全性低、fork 阻塞、COW 内存开销、无法细粒度控制

---

## 三、AOF 详解

### 3.1 工作机制与配置

```
客户端写命令 → 主进程执行 → 追加到 aof_buf → 根据 appendfsync 刷盘
```

```conf
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-use-rdb-preamble yes
```

### 3.2 三种刷盘策略

| 策略 | 说明 | 数据安全性 | 性能 | 适用场景 |
|------|------|------------|------|----------|
| `always` | 每个命令立即 fsync | ⭐⭐⭐⭐⭐ | ⭐⭐ | 金融级一致性 |
| `everysec` | 每秒 fsync 一次 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 大多数业务 |
| `no` | OS 决定何时刷盘 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 不敏感场景 |

### 3.3 AOF 重写（bgrewriteaof）

**为什么需要**：AOF 不断膨胀（100万次 INCR 实际只需一个 SET）。

**触发**：手动 `BGREWRITEAOF` 或自动（超过阈值且 > 64MB）。

**流程**：
```
1. 主进程 fork() 创建子进程
2. 子进程遍历内存，为每个 key 生成 SET/HSET 等写入临时文件
3. 主进程继续接收写命令，追加到原 AOF 和 aof_rewrite_buf
4. 子进程完成后，主进程将增量追加到临时文件
5. 原子替换原 AOF 文件
```

### 3.4 修复命令

```bash
redis-check-aof appendonly.aof       # 检查
redis-check-aof --fix appendonly.aof # 修复（截断损坏部分）
```

### 3.5 优缺点

**优点**：数据安全性高、可审计、无 fork 阻塞风险（刷盘）、顺序写 IO 效率高
**缺点**：文件体积大、恢复慢、fsync 可能引起延迟、重写有 fork 开销

---

## 四、混合持久化（Redis 4.0+）

### 4.1 设计动机

| 问题 | RDB | AOF | 混合持久化 |
|------|-----|-----|------------|
| 数据安全性 | ❌ 间隔期丢失 | ✅ 高 | ✅ 高 |
| 恢复速度 | ✅ 快 | ❌ 慢 | ✅ 快 |
| 文件大小 | ✅ 小 | ❌ 大 | ⚠️ 中等 |

### 4.2 混合格式

```conf
aof-use-rdb-preamble yes  # Redis 4.0+ 默认开启
```

```
+---------------------------+
|   RDB preamble（基线）     |  ← RDB 快照
+---------------------------+
|   AOF 增量命令区          |  ← 写命令
+---------------------------+
```

前半部分 RDB 快速加载，后半部分 AOF 保证完整性，Redis 自动识别。

### 4.3 加载顺序

```
1. AOF 开启？→ 是 → 加载 AOF
   ├── 有 RDB preamble → 先加载 RDB 基线，再重放 AOF 增量
   └── 无 → 纯 AOF 逐条重放
2. AOF 未开启 → 加载 RDB
3. AOF 和 RDB 同时存在 → 优先使用 AOF
```

### 4.4 优势

1. **恢复速度提升**：RDB 基线加载快，AOF 增量通常很小
2. **数据安全保障**：AOF 增量保证不丢失任何写操作
3. **文件大小适中**：比纯 AOF 小，比纯 RDB 大
4. **向后兼容**：关闭后可生成纯 AOF 文件

---

## 五、对比表格 + 选型建议

### 5.1 全方位对比

| 维度 | RDB | AOF（everysec） | 混合持久化 |
|------|-----|-----------------|------------|
| **数据安全性** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **恢复速度** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **文件大小** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **性能影响** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **备份便利性** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **可审计性** | ❌ | ✅ | ⚠️ 部分 |
| **版本要求** | 所有 | 所有 | 4.0+ |

### 5.2 选型决策树

```
数据丢失容忍度？
├── 完全不能容忍 → AOF always + 主从集群
├── 可容忍秒级丢失 → AOF everysec（默认）
└── 可容忍分钟级丢失 → RDB 或 混合持久化

数据规模？
├── < 1GB → AOF
├── 1GB - 50GB → 混合持久化
└── > 50GB → RDB + 评估 fork 耗时
```

### 5.3 生产配置

**通用型**：
```conf
save 900 1; save 300 10; save 60 10000
appendonly yes; appendfsync everysec; aof-use-rdb-preamble yes
auto-aof-rewrite-percentage 100; auto-aof-rewrite-min-size 64mb
```

**高安全**（金融）：`appendfsync always`
**高性能**（缓存）：`save ""; appendonly no`

---

## 六、常见陷阱

### 6.1 fork 阻塞

**现象**：bgsave/bgrewriteaof 时 Redis 秒级卡顿。

**原因**：fork 耗时 ≈ 内存(GB) × 20ms。32GB 实例可能 600ms+。

**解决**：单实例 ≤ 10GB、低峰期执行、监控 `latest_fork_usec`。

### 6.2 COW 内存翻倍

**现象**：bgsave 期间触发 OOM Killer。

**示例**：Redis 20GB + COW 10GB = 30GB，系统 24GB → OOM！

**解决**：系统内存 ≥ Redis × 2、监控 `cow_memory`、用 pipeline 减少触发。

### 6.3 AOF 损坏修复

```bash
systemctl stop redis
cp appendonly.aof appendonly.aof.bak
redis-check-aof --fix appendonly.aof
systemctl start redis
```

**预防**：UPS、everysec、定期备份、RAID/SSD。

### 6.4 其他陷阱

- **优先级**：重启时优先加载 AOF
- **重写抖动**：bgrewriteaof 同样有 fork 开销
- **主从复制**：从节点配置独立于主节点
- **Cluster**：建议所有节点开启 AOF 或混合持久化

---

## 七、面试话术（30 秒版）

> Q: 介绍 Redis 持久化机制。
>
> "Redis 有三种持久化：**RDB**（内存快照）通过 bgsave 生成 dump.rdb，文件小恢复快，但间隔期数据丢失且 fork 大内存会阻塞。**AOF**（命令日志）记录写操作，三种策略 always/everysec/no，数据安全可审计，但文件大恢复慢。**混合持久化**（4.0+）AOF 重写时 RDB 基线 + AOF 增量，兼顾速度和安全性，是生产最佳实践。选型：多数场景混合+everysec；金融级用 always；纯缓存可关闭。"

---

## 八、交叉引用

- 主模块：[`03.database`](../../../03.database/)
- 相关：[Redis大Key问题](../redis-big-key/README.md)、[Redis集群](../redis-cluster/README.md)
- [官方文档](https://redis.io/docs/manual/persistence/)

## 相关章节

- 深度阅读：[`03.database`](../../03.database/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · redis-persistence](../README.md)
