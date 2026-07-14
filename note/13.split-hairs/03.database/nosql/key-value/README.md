<!--
question:
  id: 03.database-key-value
  topic: 03.database
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 架构困境
  tags: [03.database, key, value]
-->

<!-- index-only -- 此为分类/导览页，链接到下属子章节，非内容占位 -->

# Key-Value 数据库 — 咬文嚼字

> Key-Value 是最简单的 NoSQL 数据模型：一个 Key 对应一个 Value。但"简单"不等于"没有深度"——Redis 的 5 种基础数据结构、持久化策略、内存淘汰、集群方案，每一个都是面试高频考点。

---

## 文章导航

| 分类 | 核心话题 | 入口 |
|------|---------|------|
| **Redis** | 搜索、数据结构底层 | [redis/](redis/README.md) |

### 本分类文章清单

| 主题 | 核心问题 | 难度 |
|------|---------|:----:|
| [Redis 搜索能力](redis/search/README.md) | Redis 如何做全文搜索？RediSearch 模块原理 | ⭐⭐⭐ |

---

## Key-Value 数据库选型速查

| 数据库 | 数据结构 | 持久化 | 集群 | 典型场景 |
|--------|---------|--------|------|---------|
| **Redis** | String / Hash / List / Set / ZSet / Stream | RDB + AOF | Sentinel / Cluster | 缓存、排行榜、分布式锁、会话 |
| **Memcached** | 纯 String | 无 | 客户端分片 | 简单缓存、Session 共享 |
| **DynamoDB** | Key-Value / Document | 托管 | 全托管 | AWS 生态、游戏、IoT |
| **RocksDB** | 嵌入式 KV（LSM） | 本地磁盘 | 无 | 嵌入式存储引擎（Kafka、Flink 内部） |

## 相关章节

- 返回：[`NoSQL 总览`](../README.md)
- 主模块：[`03.database/07-redis`](../../../../03.database/07-redis/README.md) — Redis 深度解析
- 咬文嚼字：[`Redis 持久化`](../../redis-persistence/)、[`Redis 大 Key`](../../redis-big-key/)、[`Redis 集群`](../../redis-cluster/)

← [返回: 咬文嚼字 · key-value](README.md)
