# Redis

> Redis(REmote DIctionary Server)是基于内存的键值数据库,支持丰富的数据结构,凭借 RDB+AOF 持久化、Cluster 集群、灵活的淘汰策略和 Lua/事务能力,广泛用作缓存、消息队列和实时数据存储。

> 最后更新: 2026-06-09

## 目录

- [一、Redis 为什么快](#一redis-为什么快)
- [二、数据类型与应用场景](#二数据类型与应用场景)
- [三、持久化机制](#三持久化机制)
- [四、集群与高可用](#四集群与高可用)
- [五、内存管理](#五内存管理)
- [六、Redis vs Memcached](#六redis-vs-memcached)
- [七、缓存选型对比](#七缓存选型对比)

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

Redis 本应该很简单，Redis(REmote DIctionary Server)是基于内存的键值数据库,支持丰富的数据结构,凭借 RDB+AOF 持久化、Cluster 集群、灵活的淘汰策略和 Lua/事务能力,广泛用作缓存、消息队列和实时数据存储

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、Redis 为什么快

| 因素 | 说明 |
|------|------|
| **内存存储** | 内存访问速度比磁盘快 100~1000 倍 |
| **单线程模型** | 避免上下文切换和锁竞争（6.0+ 网络 IO 多线程） |
| **IO 多路复用** | 基于 Reactor 模式，epoll 实现高并发连接 |
| **高效数据结构** | 跳表、压缩列表、SDS 等底层优化 |
| **RESP 协议** | 协议简单，解析高效 |

> Redis 6.0 引入了**多线程网络 IO**，但命令执行仍是单线程的，保证了原子性。

---

## 二、数据类型与应用场景

### 5 种基础类型 + 4 种特殊类型

| 类型 | 底层结构 | 典型场景 |
|------|---------|---------|
| **String** | SDS（简单动态字符串） | 缓存、计数器、分布式锁 |
| **Hash** | ziplist 或 hashtable | 用户信息、商品属性、Session |
| **List** | quicklist（ziplist + 双向链表） | 消息队列、最新动态、待办事项 |
| **Set** | intset 或 hashtable | 标签、去重、好友关系（交/并/差集） |
| **Sorted Set** | ziplist 或 skiplist + hashtable | 排行榜、延时队列、优先级队列 |
| **Bitmap** | String 的位操作 | 签到、在线状态、A/B 测试 |
| **HyperLogLog** | HyperLogLog 算法 | UV 统计、基数估计（误差 0.81%） |
| **Geospatial** | Sorted Set + GeoHash | 附近搜索、距离计算、地理围栏 |
| **Stream** | Stream 结构 | 消息队列、日志收集、事件溯源 |

### 各类型关键操作

```bash
# String
SET user:1001 '{"name":"张三","age":25}'    # 设置
GET user:1001                                # 获取
INCR article:1001:views                      # 计数器 +1

# Hash
HSET user:1001 name "张三" age 25           # 设置字段
HGET user:1001 name                          # 获取字段
HGETALL user:1001                            # 获取全部字段

# List
LPUSH queue:task "send_email"                # 左侧入队
RPOP queue:task                              # 右侧出队（FIFO）
BRPOP queue:task 30                          # 阻塞出队（超时30秒）

# Set
SADD tags:article:1 "java" "redis"          # 添加标签
SINTER tags:article:1 tags:article:2        # 共同标签（交集）

# Sorted Set
ZADD leaderboard 100 "player1" 200 "player2"
ZREVRANGE leaderboard 0 9                    # Top 10
```

---

## 三、持久化机制

### 1. RDB（快照）

定时将内存数据序列化为二进制文件。

| 优点 | 缺点 |
|------|------|
| 文件紧凑，恢复速度快 | 两次快照之间的数据可能丢失 |
| 适合备份和灾难恢复 | fork 子进程时可能阻塞（大内存） |

```bash
# 手动触发
BGSAVE          # 后台异步（推荐）
SAVE            # 前台同步（阻塞）

# 配置自动触发
save 900 1      # 900 秒内至少 1 次修改则触发
save 300 10     # 300 秒内至少 10 次修改
save 60 10000   # 60 秒内至少 10000 次修改
```

### 2. AOF（追加文件）

记录每条写命令到日志文件。

| 刷盘策略 | 性能 | 数据安全性 |
|---------|:---:|:---------:|
| `always` | 最低 | 不丢数据 |
| `everysec` | 中等 | 最多丢 1 秒（推荐） |
| `no` | 最高 | 由 OS 决定 |

**AOF 重写**：当 AOF 文件过大时，Redis 会 fork 子进程，将当前内存数据重写为最小命令集。

### 3. 混合持久化（Redis 4.0+）

AOF 重写时，前半段为 RDB 格式（恢复快），后半段为 AOF 增量命令（不丢数据）。

```
混合文件 = [RDB 快照] + [AOF 增量命令]
```

> **生产环境推荐**：开启 AOF（`everysec`）+ 混合持久化，兼顾恢复速度和数据安全。

---

## 四、集群与高可用

### 1. 主从复制

```
Master（读写）
    ├── Slave1（只读）
    └── Slave2（只读）
```

- **全量同步**：Slave 首次连接时，Master 发送 RDB 快照
- **增量同步**：Master 通过传播写命令保持数据一致

### 2. 哨兵模式（Sentinel）

Sentinel 负责监控 Master 和 Slave 的健康状态，实现**自动故障转移**。

| 功能 | 说明 |
|------|------|
| 监控 | 定期 PING 检测节点是否存活 |
| 自动故障转移 | Master 宕机 → 选举 Slave 提升为新 Master |
| 通知 | 故障转移后通知客户端新的 Master 地址 |

```
Sentinel1 ──┐
Sentinel2 ──┼── 监控 ──→ Master / Slave1 / Slave2
Sentinel3 ──┘

Master 宕机 → Sentinel 投票选举 → Slave1 提升为 Master → 通知客户端
```

### 3. Redis Cluster（集群）

Redis 3.0+ 原生支持分布式集群，数据自动分片。

| 特性 | 说明 |
|------|------|
| 数据分片 | 16384 个 Hash Slot，分配到不同节点 |
| 去中心化 | 节点间通过 Gossip 协议通信 |
| 自动故障转移 | 主节点故障时从节点自动晋升 |
| 最低配置 | 3 主 + 3 从（6 节点） |

```
客户端 → 任意节点 → 计算 key 的 Slot → 转发到正确节点
                    ↓
              CRC16(key) % 16384 = slot
```

### 4. 高可用方案对比

| 方案 | 分片 | 自动故障转移 | 数据容量 | 适用场景 |
|------|:---:|:----------:|---------|---------|
| 单机 | ❌ | ❌ | 单节点内存上限 | 开发/测试 |
| 主从 | ❌ | ❌ | 单节点 | 读多写少 |
| 哨兵 | ❌ | ✅ | 单节点 | 中等规模，自动 HA |
| Cluster | ✅ | ✅ | 横向扩展 | 大规模，高可用 |

---

## 五、内存管理

### 1. 8 种淘汰策略

当内存达到 `maxmemory` 限制时，Redis 按策略淘汰数据：

| 策略 | 范围 | 说明 |
|------|------|------|
| `noeviction` | - | 不淘汰，写入返回错误（默认） |
| `allkeys-lru` | 所有 key | 淘汰最久未访问的 key（**推荐**） |
| `volatile-lru` | 有过期时间的 key | 淘汰最久未访问的 |
| `allkeys-lfu` | 所有 key | 淘汰访问频率最低的（Redis 4.0+） |
| `volatile-lfu` | 有过期时间的 key | 淘汰访问频率最低的 |
| `allkeys-random` | 所有 key | 随机淘汰 |
| `volatile-random` | 有过期时间的 key | 随机淘汰 |
| `volatile-ttl` | 有过期时间的 key | 淘汰 TTL 最短的 |

```bash
# 配置淘汰策略
CONFIG SET maxmemory-policy allkeys-lru
CONFIG SET maxmemory 2gb
```

### 2. 大 Key 问题

单个 key 的 value 过大（如 > 10MB）会阻塞 Redis 单线程，影响整体性能。

| 类型 | 优化方式 |
|------|---------|
| String 过大 | 拆分为多个 key，或压缩后存储 |
| Hash 字段过多 | 拆分为多个 Hash，设置合理的 `hash-max-ziplist-entries` |
| Set/List 元素过多 | 拆分为多个集合，控制单个集合大小 |

**检测大 Key**：

```bash
# Redis 4.0+ 内存分析
redis-cli --bigkeys

# 使用 RDB 分析工具
redis-rdb-tools（Python）
```

### 3. 热 Key 问题

单个 key 被大量请求（如秒杀活动商品），可能导致单节点压力过大。

| 方案 | 说明 |
|------|------|
| 本地缓存 | 热点数据缓存在应用进程内存（Caffeine） |
| 读写分离 | 分散读请求到多个 Slave |
| Key 拆分 | 将 `product:1001` 拆分为 `product:1001:1`、`product:1001:2` |

---

## 六、Redis vs Memcached

| 特性 | Redis | Memcached |
|------|-------|-----------|
| 数据结构 | String/Hash/List/Set/ZSet 等 | 仅 String |
| 持久化 | RDB + AOF | 不支持 |
| 集群 | 原生支持 Cluster | 客户端分片 |
| 线程模型 | 单线程（6.0+ 网络多线程） | 多线程 |
| 发布订阅 | ✅ | ❌ |
| Lua 脚本 | ✅ | ❌ |
| 事务 | 基础支持（MULTI/EXEC） | ❌ |
| 内存管理 | 8 种淘汰策略 | LRU |

---

## 七、缓存选型对比

| 工具 | 类型 | 特点 | 适用场景 |
|------|------|------|---------|
| **Caffeine** | 本地缓存 | Java 最快本地缓存，W-TinyLFU | 单机热点数据 |
| **Ehcache** | 本地+分布式 | 与 Spring 集成好 | 需要多级缓存 |
| **Redis** | 分布式缓存 | 功能丰富，持久化，集群 | 分布式缓存首选 |
| **Memcached** | 分布式缓存 | 多线程，高吞吐 | 纯 KV 缓存 |
| **Dragonfly** | 分布式缓存 | 兼容 Redis API,性能更高 | 高吞吐场景 |

---

## 八、Redis 底层数据结构

| 数据类型 | 编码方式(底层) | 触发条件 |
|---------|----------------|---------|
| `String` | `int` / `embstr` / `raw` | 值是整数 / 短字符串 / 长字符串 |
| `List` | `ziplist` (压缩列表) / `linkedlist` → **7.0 起统一 `quicklist`** | 元素少 / 多 |
| `Hash` | `listpack` / `hashtable` | 字段少 / 多 |
| `Set` | `intset` / `hashtable` | 全是整数且少 / 其他 |
| `ZSet` | `listpack` / `skiplist + hashtable` | 元素少 / 多 |

### 1. SDS(简单动态字符串)

`struct sdshdr`:
```
┌──────────┬─────┬──────┬────────┐
│  len     │ free│ buf  │  ...   │
│  已用长度 │ 空闲 │ 字节  │ 实际数据 │
└──────────┴─────┴──────┴────────┘
```

**优势**:
- O(1) 取长度(无 `strlen`)
- 预分配空间,减少重分配次数
- 二进制安全(可存 `\0`)

### 2. ziplist / listpack(压缩列表)

- 连续内存,节省空间
- 元素少时(< 128 字节、< 64 项)使用
- 缺点:**级联更新**,改一个元素可能连锁影响后续

### 3. skiplist(跳表)

- 多级索引,O(log N) 查找
- 比红黑树实现简单,支持范围操作
- ZSet 范围查询 `ZRANGEBYSCORE` 高效

### 4. quicklist(7.0+ List 底层)

- ziplist + linkedlist 组合
- 每个节点是一个 ziplist
- 平衡空间与修改效率

---

## 九、Redis 分布式锁

### 1. 最简实现(SETNX + EXPIRE)

```bash
SET lock:order:1001 "uuid-abc" NX EX 30
```

- `NX` = 仅当 key 不存在时设置
- `EX 30` = 30 秒过期,防止死锁
- value 用 UUID 标识,避免误删他人的锁

### 2. 释放锁(Lua 脚本原子化)

```lua
-- KEYS[1] = lock key, ARGV[1] = UUID
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

### 3. Redisson 客户端(Java 首选)

```java
@Resource
RedissonClient redisson;

public void doBusiness() {
    RLock lock = redisson.getLock("lock:order:1001");
    try {
        lock.lock(10, TimeUnit.SECONDS);  // 10 秒自动释放
        // 业务逻辑
    } finally {
        lock.unlock();
    }
}
```

**特性**:看门狗自动续期、可重入、公平锁、联锁(MultiLock)、读写锁。

### 4. RedLock 算法(多 Redis 实例强一致锁)

```
1. 获取当前时间 T1
2. 依次向 N(≥3)个独立 Redis 实例申请锁
3. 计算获取锁总耗时 = T2 - T1
4. 当且仅当 (a) 在 ≥N/2+1 个实例上获得锁
         (b) 总耗时 < 锁 TTL
   → 视为获取成功
5. 失败时,向所有实例发送释放锁请求
```

**争议**:Martin Kleppmann(《数据密集型应用系统设计》作者)指出 RedLock **依赖精确时钟同步**,故障切换场景可能不安全。Antirez(Redis 作者)反驳认为工程上可接受。

> **生产实践**:**单 Redis 实例 + Redisson 看门狗** 是 90% 场景的推荐;RedLock 仅在金融、库存等强一致场景考虑。

---

## 十、Pipeline / 事务 / Lua 对比

| 机制 | 用途 | 原子性 | 是否阻塞其他命令 |
|------|------|--------|----------------|
| **Pipeline** | 批量发送命令,减少 RTT | ❌ 不保证原子 | 否 |
| **MULTI/EXEC 事务** | 命令打包执行 | ✅ 原子(但不支持回滚) | 是(其他命令等待) |
| **Lua 脚本** | 服务端执行复杂逻辑 | ✅ 原子(单线程执行) | 是 |

### 1. Pipeline 示例

```bash
# 1 次 RTT 发送多条命令
(echo -e "SET k1 v1\r\nSET k2 v2\r\nGET k1\r\nGET k2\r\n"; sleep 1) | nc localhost 6379
```

### 2. 事务示例

```bash
MULTI
SET balance 100
DECRBY balance 30
INCRBY balance 30
EXEC  # 一次执行 3 条命令
```

> Redis 事务**不支持回滚**:若其中某条命令语法错误,EXEC 后其他命令继续执行(不满足原子性要求时 Redis 选择"继续执行")。

### 3. Lua 脚本(最强大)

```bash
EVAL "
    local cur = redis.call('GET', KEYS[1])
    if cur and tonumber(cur) > tonumber(ARGV[1]) then
        return redis.call('DECRBY', KEYS[1], ARGV[1])
    end
    return 0
" 1 balance 30
```

---

## 十一、Redis 客户端对比(Java)

| 客户端 | 线程模型 | 性能 | 集群 | 推荐度 |
|--------|---------|------|------|--------|
| **Jedis** | 阻塞 I/O,线程不安全(需连接池) | 中 | ✅ | ⭐⭐ 老项目 |
| **Lettuce** | Netty 异步,线程安全 | 高 | ✅ | ⭐⭐⭐⭐ Spring Boot 默认 |
| **Redisson** | 基于 Netty,功能丰富 | 高 | ✅ | ⭐⭐⭐⭐⭐ 分布式锁首选 |

> **Spring Boot 2.x+ 默认使用 Lettuce**,分布式锁场景推荐 **Redisson**。

---

## 十二、Redis 监控指标

### 1. INFO 命令

```bash
redis-cli INFO
```

关键 sections:
| Section | 关键指标 |
|---------|---------|
| `Server` | `redis_version`、`uptime_in_seconds` |
| `Memory` | `used_memory_human`、`mem_fragmentation_ratio` |
| `Stats` | `total_connections_received`、`instantaneous_ops_per_sec` |
| `Replication` | `master_link_status`、`repl_lag` |
| `Keyspace` | 各 db 的 key 数量与命中数 |

### 2. 慢查询

```bash
# 设置阈值(微秒)
CONFIG SET slowlog-log-slower-than 10000

# 查看最近 10 条慢查询
SLOWLOG GET 10

# 慢查询数量
SLOWLOG LEN
```

### 3. 内存碎片率

```
mem_fragmentation_ratio = used_memory_rss / used_memory
```

| 值 | 含义 |
|------|------|
| `1.0 ~ 1.5` | 正常 |
| `> 1.5` | 碎片过多,执行 `MEMORY PURGE` 或重启 |
| `< 1.0` | 内存换出到 swap,性能极差 |

### 4. Prometheus + redis_exporter

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

Grafana 官方提供 Redis 仪表盘,关键告警指标:
- `redis_memory_used_bytes / redis_memory_max_bytes > 0.8`
- `redis_connected_clients > 5000`
- `redis_keyspace_hits / (redis_keyspace_hits + redis_keyspace_misses) < 0.9`(命中率)

---

## 十三、Redis 7.0 新特性

| 特性 | 说明 |
|------|------|
| **Function** | 用 Lua 替代 EVAL,更好的函数管理 |
| **Sharded Pub/Sub** | 集群模式下分片发布订阅,降低跨节点流量 |
| **Multi-Part AOF** | AOF 文件按大小分片,清理更高效 |
| **ACL v2** | 细粒度权限控制(支持选择器) |
| **Client-Side Caching** | 客户端缓存(Tracking)增强 |

---

## 相关章节

- [数据库基础知识](../01-fundamentals/README.md) — 数据库核心概念
- [MySQL](../05-mysql/README.md) — MySQL 主从复制与 Redis 集群对比
- [缓存](../06-cache/README.md) — 缓存三大问题与一致性
- [NoSQL](../08-nosql/README.md) — Redis 是 NoSQL 键值存储代表
- [系统设计 · 分布式锁](../../04.system-design/02-distributed/distributed-lock/README.md) — Redis 分布式锁深入

## 参考资料

- [Redis Official Documentation](https://redis.io/docs/)
- [Redis 7.0 Release Notes](https://github.com/redis/redis/releases/tag/7.0.0)
- [《Redis 设计与实现》黄健宏](http://redisbook.com/) — 国内最经典 Redis 源码解析
- [Redis 6.0 Multi-Thread I/O](https://redis.io/docs/manual/client-side-caching/) — 官方 I/O 多线程说明
- [Antirez (Salvatore Sanfilippo) Blog](http://antirez.com/) — Redis 作者博客
