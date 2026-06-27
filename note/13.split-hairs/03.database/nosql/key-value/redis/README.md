# Redis 细节 — 咬文嚼字

> Redis 面试中那些"看似简单实则暗藏陷阱"的问题。
>
> Redis 远不止 `SET`/`GET`——它的数据结构底层实现（SDS、ziplist、quicklist、skiplist、intset、hashtable）、持久化机制（RDB fork、AOF rewrite）、内存淘汰策略（8 种）、集群方案（Sentinel、Cluster），每一层都有大量值得深挖的细节。

---

## 文章清单

| 主题 | 核心问题 | 难度 |
|------|---------|:----:|
| [Redis 搜索能力](search/README.md) | Redis 如何做全文搜索？RediSearch 模块的倒排索引实现 | ⭐⭐⭐ |

---

## Redis 核心知识图谱

```
Redis
├── 数据结构
│   ├── String  → SDS（Simple Dynamic String）
│   ├── Hash    → ziplist / hashtable
│   ├── List    → quicklist（ziplist + 双向链表）
│   ├── Set     → intset / hashtable
│   ├── ZSet    → ziplist / skiplist + hashtable
│   └── Stream  → Radix Tree + 消费者组
├── 持久化
│   ├── RDB     → fork + COW（Copy-On-Write）
│   ├── AOF     → 追加写 + rewrite 压缩
│   └── 混合    → RDB 头 + AOF 增量（Redis 4.0+）
├── 高可用
│   ├── 主从复制 → 全量 + 增量（replication offset）
│   ├── Sentinel → 自动故障转移
│   └── Cluster  → 16384 哈希槽 + Gossip 协议
├── 内存管理
│   ├── 淘汰策略 → noeviction / allkeys-lru / volatile-lfu 等 8 种
│   └── 内存碎片 → active defrag（jemalloc）
└── 高级特性
    ├── 事务      → MULTI / EXEC（乐观锁 WATCH）
    ├── Lua 脚本  → 原子执行
    ├── Pub/Sub   → 发布订阅
    └── Module    → RediSearch / RedisJSON / RedisTimeSeries
```

## 相关章节

- 返回：[`NoSQL 总览`](../../README.md) → [`03.database 总览`](../../../README.md)
- 主模块：[`03.database/07-redis`](../../../../../03.database/07-redis/README.md) — Redis 深度解析
- 咬文嚼字系列：
  - [`缓存穿透/击穿/雪崩`](../../../redis/cache-penetration-breakdown-avalanche/) — 面试必考三件套
  - [`Redis 持久化`](../../../redis-persistence/) — RDB / AOF 详解
  - [`Redis 内存淘汰`](../../../redis-eviction/) — 8 种淘汰策略
  - [`Redis 集群`](../../../redis-cluster/) — Sentinel vs Cluster
  - [`Redis 大 Key`](../../../redis-big-key/) — 发现与治理
