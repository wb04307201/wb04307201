# Redis

Redis（REmote DIctionary Server）是基于 C 语言开发的开源内存数据库，支持丰富的数据结构，广泛用作缓存、消息队列和实时数据存储。

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
| **Dragonfly** | 分布式缓存 | 兼容 Redis API，性能更高 | 高吞吐场景 |
