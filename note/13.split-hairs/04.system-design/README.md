# 系统设计咬文嚼字

> 系统设计高频面试题与难点深挖，对齐主模块 [`04.system-design`](../../04.system-design/)

---

## 文章清单（共 8 篇）

### 高性能 - 消息队列
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [MQ 消息积压](high-performance/mq/mq-backlog/) | ⭐⭐⭐⭐ | 原因分析 + 紧急止血 + 长期优化 |
| [为什么还要 RocketMQ](high-performance/mq/still-need-rocketmq/) | ⭐⭐⭐ | Kafka vs RocketMQ vs RabbitMQ 选型 |

### 高性能 - 缓存
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [缓存与数据库双写一致性](high-performance/cache-consistency/) | ⭐⭐⭐⭐⭐ | 延迟双删 vs 监听 binlog |

### 高性能 - 限流
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [限流算法](high-performance/rate-limiting/) | ⭐⭐⭐⭐ | 计数器 / 滑动窗口 / 漏桶 / 令牌桶 |

### 分布式
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [分布式 ID 生成方案](distributed/distributed-id/) | ⭐⭐⭐⭐ | UUID / 数据库 / 雪花算法 / Leaf |
| [分布式事务](distributed/distributed-transaction/) | ⭐⭐⭐⭐⭐ | 2PC / TCC / Saga / 本地消息表 |
| [CAP 定理实际应用](cap-theorem/) | ⭐⭐⭐⭐ | CP vs AP 选型决策 |
| [分布式锁](high-performance/distributed-lock/) | ⭐⭐⭐⭐⭐ | Redis SETNX / Redisson / ZooKeeper |

### 高并发
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [幂等性设计 6 大方案](idempotency/) | ⭐⭐⭐⭐⭐ | Token / 状态机 / 唯一索引 / 去重表 |
| [熔断降级实战](circuit-breaker/) | ⭐⭐⭐⭐ | Sentinel / Resilience4j 落地 |

---

## 待补充的高频面试题

### 缓存（必考）
- **缓存穿透 / 击穿 / 雪崩**（三件套必问，移至 `03.database`）
- **缓存热点 Key 问题**（本地缓存 + 分布式锁）
- **缓存预热策略**

### 高并发
- **异步化方案**（CompletableFuture / 消息队列）

### 数据库扩展
- **分库分表策略**（ShardingSphere / MyCat）
- **读写分离方案**
- **数据迁移方案**

---

## 学习路径

1. **入门**（3 天）：MQ 积压处理 + 选型对比
2. **进阶**（2 周）：缓存一致性 + 限流算法 + 分布式 ID + 分布式锁 + 幂等性设计
3. **冲刺面试**：重点看"分布式事务"、"熔断降级"、"分布式锁"、"幂等性设计"

## 相关章节

- 主模块：[`note/04.system-design`](../../04.system-design/) — 系统设计知识体系
- 相关章节：[`03.database`](../03.database/)（数据库细节）/ [`06.spring`](../06.spring/)（框架实现）
- 待补充主题的深度阅读：
  - 缓存穿透/击穿/雪崩 → [`03.database/06-cache`](../../03.database/06-cache/README.md)
  - 分库分表 → [`03.database`](../../03.database/README.md) 数据迁移与同步
  - 异步化方案 → [`01.java/concurrency`](../../01.java/concurrency/README.md) CompletableFuture
