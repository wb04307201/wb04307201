# 系统设计咬文嚼字

> 系统设计高频面试题与难点深挖，对齐主模块 [`04.system-design`](../../04.system-design/)

---

## 文章清单

### 高性能 - 消息队列
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [MQ 消息积压](high-performance/mq/mq-backlog/) | ⭐⭐⭐⭐ | 原因分析 + 紧急止血 + 长期优化 |
| [为什么还要 RocketMQ](high-performance/mq/still-need-rocketmq/) | ⭐⭐⭐ | Kafka vs RocketMQ vs RabbitMQ 选型 |

---

## 待补充的高频面试题

### 缓存（必考）
- **缓存穿透 / 击穿 / 雪崩**（三件套必问）
- **缓存与数据库双写一致性**（延迟双删 vs 监听 binlog）
- **缓存热点 Key 问题**（本地缓存 + 分布式锁）
- **缓存预热策略**

### 分布式
- **分布式 ID 生成方案**（UUID / 数据库 / 雪花算法 / Leaf）
- **分布式事务**（2PC / TCC / Saga / 本地消息表）
- **分布式锁**（Redis SETNX / Redisson / ZooKeeper）
- **CAP 定理实际应用**（CP vs AP 选型）

### 高并发
- **限流算法**（计数器 / 滑动窗口 / 漏桶 / 令牌桶）
- **幂等性设计**（Token / 状态机 / 唯一索引）
- **降级与熔断**（Sentinel / Hystrix）
- **异步化方案**（CompletableFuture / 消息队列）

### 数据库扩展
- **分库分表策略**（ShardingSphere / MyCat）
- **读写分离方案**
- **数据迁移方案**

---

## 学习路径

1. **入门**（3 天）：MQ 积压处理 + 选型对比
2. **进阶**（2 周）：缓存三件套 + 分布式 ID + 分布式锁
3. **冲刺面试**：重点看"缓存一致性"、"限流算法"、"分布式事务"（待补）

## 交叉引用

- 主模块：[`note/04.system-design`](../../04.system-design/) — 系统设计知识体系
- 相关章节：[`03.database`](../03.database/)（数据库细节）/ [`06.spring`](../06.spring/)（框架实现）
