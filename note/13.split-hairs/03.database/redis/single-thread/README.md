<!--
question:
  id: 03.database-redis-single-thread
  topic: 03.database
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 反直觉性能
  tags: [03.database, Redis, 单线程, epoll, Reactor, IO多路复用, 多线程]
-->

# Redis 单线程为什么速度碾压多线程数据库？

> 一句话定位：**Redis 面试第一题**。考察的不是"Redis 用内存所以快"，而是 **5 大因素的系统性理解** + **epoll/Reactor 底层原理** + **Redis 6.0 网络 IO 多线程** + **与 MySQL 多线程的本质区别**。完整 Redis 体系见 [Redis 主模块](../../../../03.database/07-redis/README.md)。

> **系列定位**：高频 Redis 面试题（必考）。配套兄弟题：[缓存三件套](cache-penetration-breakdown-avalanche/README.md)、[Redis 大 Key](../../redis-big-key/README.md)。

---

⭐⭐⭐⭐ 深度级别（中高级）
📚 前置知识：网络 IO / 多路复用 / 线程模型

---

## 引子：面试官的经典开场

面试官："Redis 是单线程的，MySQL 是多线程的，为什么 Redis 反而更快？"

大多数人答："因为 Redis 用内存。"

面试官追问：
1. "内存快是快，但 Memcached 也用内存还多线程，为什么 Redis 单线程反而更受欢迎？"
2. "epoll 和 select 有什么区别？Reactor 模式是什么？"
3. "Redis 6.0 引入了多线程，跟之前的单线程矛盾吗？"

大多数人卡在追问上。**这道题考察的不是"知道内存快"，而是"理解单线程高并发的底层原理 + 架构权衡"。**

---

## 一、核心原理：5 大因素

### 1.1 因素总览

| 因素 | 贡献 | 说明 |
|------|------|------|
| **1. 纯内存操作** | ~100x | 内存访问 ~100ns vs 磁盘 ~10ms |
| **2. 单线程无锁** | ~10x | 无线程切换、无锁竞争、无死锁 |
| **3. IO 多路复用** | ~100x | 单线程处理数万并发连接 |
| **4. 高效数据结构** | ~10x | 跳表/压缩列表/SDS 等底层优化 |
| **5. RESP 协议** | ~2x | 协议简单，解析极快 |

### 1.2 纯内存操作

```
内存访问延迟：~100 ns
SSD 随机读：  ~100 μs（1000 倍）
HDD 随机读：  ~10 ms（100,000 倍）
网络 RTT：    ~1 ms（跨机房）
```

Redis 所有数据在内存中，读写操作不涉及磁盘 IO。这是最根本的优势。

### 1.3 单线程为什么不怕并发？

**反直觉**：单线程处理请求不需要加锁、不需要线程切换、不需要处理竞态条件。

| 维度 | 多线程（MySQL） | 单线程（Redis） |
|------|---------------|----------------|
| 锁竞争 | 需要行锁/表锁/读写锁 | 无锁 |
| 线程切换 | 上下文切换 ~5μs/次 | 无切换 |
| 死锁 | 可能发生 | 不可能 |
| 原子性 | 需要事务保证 | 天然原子 |
| CPU 利用 | 多核并行 | 单核跑满（命令执行部分） |

**关键**：Redis 的瓶颈通常不是 CPU 而是**网络带宽和内存**。单核处理命令执行绰绰有余。

### 1.4 IO 多路复用 + Reactor 模式

这是单线程能处理高并发的**核心秘密**：

```
                    ┌─────────────────────────┐
                    │      Redis 主线程        │
                    │                         │
  客户端连接 ──────→│  Event Loop（epoll）     │
  (数万个)         │    ↓                     │
                    │  1. epoll_wait() 等待    │
                    │     可读/可写事件        │
                    │    ↓                     │
                    │  2. 遍历就绪事件        │
                    │    ↓                     │
                    │  3. 读取请求 → 执行命令  │
                    │    → 写入响应            │
                    │    ↓                     │
                    │  4. 回到 1              │
                    └─────────────────────────┘
```

**Reactor 模式**：
- **Reactor**（反应器）：监听 IO 事件，分发到对应 handler
- **Handler**（处理器）：处理具体的读写操作
- Redis 的 Reactor 由 `ae` 事件循环库实现（基于 epoll/kqueue/select）

**epoll vs select/poll**：

| 特性 | select/poll | epoll |
|------|------------|-------|
| 连接数上限 | 1024（FD_SETSIZE） | 无上限（受内存限制） |
| 事件检测 | O(n) 遍历所有 fd | O(1) 回调通知就绪 fd |
| 内存拷贝 | 每次调用拷贝 fd 集合 | mmap 共享内核空间 |
| 适用 | 低并发 | **高并发（Redis 首选）** |

### 1.5 高效数据结构

| 数据结构 | 用途 | 性能优势 |
|---------|------|---------|
| **SDS**（简单动态字符串） | String 底层 | 预分配 + O(1) 获取长度 |
| **跳表**（skiplist） | ZSet 底层 | O(log N) 插入/查找，比平衡树更友好 |
| **压缩列表**（ziplist） | 小 Hash/List/ZSet | 连续内存，减少碎片 |
| **整数集合**（intset） | 纯整数 Set | 紧凑存储 + 二分查找 |
| **quicklist** | List 底层（7.0+） | ziplist + 双向链表混合 |

### 1.6 RESP 协议

```
*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n
```

RESP（REdis Serialization Protocol）是纯文本协议，解析不需要复杂的状态机，比 HTTP/二进制协议快得多。

---

## 二、Redis 6.0 网络 IO 多线程

### 2.1 为什么引入多线程？

Redis 6.0 之前，单线程同时处理**网络 IO + 命令执行**。高并发下网络 IO（read/write syscall）成为瓶颈——单核处理网络 read/write 的能力有限。

**Redis 6.0 的改进**：把网络 IO 拆分为多线程，命令执行仍然是单线程。

### 2.2 架构变化

```
Redis 5.x（纯单线程）：
  主线程：accept → read → 执行命令 → write

Redis 6.0+（网络 IO 多线程）：
  IO 线程池：read（多线程并行读取请求）
  主线程：执行命令（单线程，保证原子性）
  IO 线程池：write（多线程并行写回响应）
```

### 2.3 关键设计

| 特性 | 说明 |
|------|------|
| 命令执行仍然单线程 | 保证原子性，Lua 脚本、事务不需要锁 |
| IO 线程数可配 | `io-threads 4`（推荐 CPU 核数的 3/4） |
| 默认关闭 | 需要显式开启 `io-threads-do-reads yes` |
| 适用场景 | 网络 IO 是瓶颈（大 value、高 QPS） |

```conf
# redis.conf
io-threads-do-reads yes
io-threads 4
```

---

## 三、Redis vs MySQL 多线程对比

| 维度 | Redis（单线程命令执行） | MySQL（多线程） |
|------|----------------------|----------------|
| **数据存储** | 内存 | 磁盘（Buffer Pool 缓存） |
| **锁机制** | 无锁（单线程天然串行） | 行锁/表锁/MDL 锁 |
| **事务** | 单命令原子 / Lua 原子 | ACID 完整事务 |
| **并发模型** | 单线程处理所有请求 | 每连接一线程 / 线程池 |
| **瓶颈** | 网络带宽 / 内存 | 磁盘 IO / 锁竞争 |
| **QPS** | 10 万+（单机） | 1-5 万（单机） |
| **延迟** | < 1ms | 1-10ms |

**核心区别**：Redis 是 **CPU 计算密集型**（内存操作极快），MySQL 是 **IO 密集型**（磁盘读写多）。IO 密集型需要多线程隐藏 IO 延迟，CPU 密集型用单线程避免锁开销反而更快。

---

## 四、7 道精选面试题

### Q1：Redis 单线程处理所有请求，为什么还能支持高并发？

**答**：3 个原因——

1. **IO 多路复用（epoll）**：单线程通过 epoll 同时监听数万连接，只有就绪的连接才处理，不会阻塞
2. **纯内存操作**：每条命令执行时间 < 1μs，单线程每秒可处理 10 万+ 命令
3. **无锁无切换**：没有线程切换开销、没有锁竞争，CPU 利用率极高

### Q2：epoll 的水平触发（LT）和边缘触发（ET）有什么区别？Redis 用哪个？

**答**：
- **水平触发（LT）**：fd 可读时，每次 epoll_wait 都通知（可能重复通知）
- **边缘触发（ET）**：只在状态变化时通知一次（新数据到来时）

Redis 使用**水平触发**——实现简单，配合非阻塞 IO 不会遗漏事件。Nginx 使用边缘触发——减少重复通知，性能更高但实现更复杂。

### Q3：Redis 6.0 引入了多线程，是不是说明单线程不好？

**答**：不是。Redis 6.0 的多线程**只用于网络 IO 的 read/write**，命令执行仍然是单线程。

```
Redis 6.0 线程模型：
  IO 线程 A ──→ read 客户端 1 的请求 ──→ 放入队列
  IO 线程 B ──→ read 客户端 2 的请求 ──→ 放入队列
  主线程 ──────────→ 从队列取请求 → 执行命令（单线程！）
  IO 线程 A ──→ write 客户端 1 的响应
  IO 线程 B ──→ write 客户端 2 的响应
```

命令执行单线程保证了原子性（Lua 脚本、MULTI/EXEC 不需要锁）。

### Q4：为什么 Memcached 多线程但没有 Redis 受欢迎？

**答**：

| 维度 | Memcached | Redis |
|------|-----------|-------|
| 数据结构 | 仅 String | 9 种（String/Hash/List/Set/ZSet 等） |
| 持久化 | 无 | RDB + AOF |
| 集群 | 客户端分片 | Cluster 原生支持 |
| 线程模型 | 多线程（需锁） | 单线程（无锁） |
| 功能 | 纯缓存 | 缓存 + 消息队列 + 分布式锁 |

Memcached 多线程需要内部锁保护数据，增加了复杂度。Redis 单线程 + 丰富数据结构 + 持久化 = 更实用的选择。

### Q5：什么操作会阻塞 Redis 单线程？

**答**：

| 操作 | 阻塞时间 | 解决方案 |
|------|---------|---------|
| `KEYS *` | 1 亿 key 可能阻塞数秒 | 用 `SCAN` 替代 |
| `HGETALL` 大 Hash | 百万字段 → 数百 ms | 用 `HSCAN` 或控制字段数 |
| `DEL` 大 Key | 删除百万元素 → 数百 ms | 用 `UNLINK`（异步删除，Redis 4.0+） |
| `FLUSHALL` | 清空所有数据 → 秒级 | 生产环境禁用 |
| 慢查询 | 复杂 Lua / 大 ZSet 排序 | 监控 SLOWLOG，优化脚本 |

### Q6：Redis Pipeline 为什么能提升性能？

**答**：减少**网络 RTT 次数**。

```
普通模式（3 条命令）：
  Client → SET key1 val1 → Server → Client（1 RTT）
  Client → SET key2 val2 → Server → Client（1 RTT）
  Client → SET key3 val3 → Server → Client（1 RTT）
  共 3 RTT

Pipeline 模式（3 条命令）：
  Client → SET key1 + SET key2 + SET key3 → Server → Client
  共 1 RTT
```

Pipeline 将多条命令打包一次发送，减少网络往返。1000 条命令从 1000 RTT → 1 RTT，延迟降低 99%。

### Q7：如何判断 Redis 的性能瓶颈在哪？

**答**：

```bash
# 1. 查看实时延迟
redis-cli --latency

# 2. 查看慢查询
redis-cli SLOWLOG GET 10

# 3. 查看 INFO 关键指标
redis-cli INFO | grep -E "instantaneous_ops|used_memory|connected_clients"

# 4. 查看事件循环延迟
redis-cli --intrinsic-latency 5
```

| 指标 | 健康值 | 异常说明 |
|------|--------|---------|
| instantaneous_ops_per_sec | 根据业务 | 突降可能有慢查询 |
| used_memory / maxmemory | < 80% | 超 80% 考虑扩容 |
| connected_clients | < maxclients | 接近上限需扩容 |
| keyspace_hits / (hits+misses) | > 90% | 命中率低需优化缓存策略 |

---

## 五、面试话术（30 秒版）

> "Redis 快的核心是 5 个因素叠加：纯内存操作（比磁盘快 1000 倍）+ 单线程无锁（无切换无竞争）+ IO 多路复用（epoll 单线程处理数万连接）+ 高效数据结构（跳表/SDS/压缩列表）+ RESP 简单协议。
>
> 单线程能高并发的秘密是 Reactor 模式——主线程用 epoll 监听所有连接的 IO 事件，只有就绪的连接才处理，命令执行时间 < 1μs，单线程每秒可处理 10 万+ 命令。
>
> Redis 6.0 引入了多线程网络 IO（read/write 多线程并行），但命令执行仍然是单线程，保证了原子性。这是和 MySQL 多线程的本质区别——MySQL 是 IO 密集型（磁盘读写多），需要多线程隐藏 IO 延迟；Redis 是 CPU 密集型（内存操作极快），单线程避免锁开销反而更快。"

---

## 六、交叉引用

- **Redis 体系**：[Redis 主模块](../../../../03.database/07-redis/README.md) — 为什么快 / 数据类型 / 持久化 / 集群
- **相关面试题**：[缓存三件套](cache-penetration-breakdown-avalanche/README.md) — 穿透/击穿/雪崩
- **相关面试题**：[Redis 大 Key](../../redis-big-key/README.md) — 大 Key 阻塞单线程的危害
- **相关面试题**：[Redis 持久化](../../redis-persistence/README.md) — RDB/AOF 对性能的影响
- **Java NIO**：[Java NIO](../../../../01.java/io/nio/README.md) — epoll/selector 的 Java 实现
- **主模块**：[`03.database`](../../../../03.database/) — 数据库知识体系

## 相关章节

- 深度阅读：[`03.database`](../../03.database/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · Redis single-thread](README.md)
