<!--
module:
  parent: system-design
  slug: system-design/06-idempotency
  type: article
  category: 主模块子文章
  summary: 幂等性（Idempotence）是分布式系统和 API 设计中的核心概念，指**对同一操作的多次重复执行与单次执行的效果完全一致**。在不可靠的网络、重复请求或...
-->

# 幂等设计

> 幂等性（Idempotence）是分布式系统和 API 设计中的核心概念，指**对同一操作的多次重复执行与单次执行的效果完全一致**。在不可靠的网络、重复请求或并发操作的场景下，幂等性设计能避免数据不一致、重复扣款等严重问题。

## 目录

- [为什么需要幂等性](#为什么需要幂等性)
- [五大策略总览](#五大策略总览)
- [选型决策树](#选型决策树)
- [策略详解](#策略详解)
- [参考资料](#参考资料)

---
---

## 为什么需要幂等性

### 1. 解决的典型问题

- **网络重试**：HTTP 请求超时后客户端重试，可能导致服务端重复处理。
- **消息队列重复消费**：如 Kafka / RabbitMQ 消费者崩溃后重启，可能重新消费消息。
- **用户重复操作**：如用户多次点击提交按钮，或前端防抖失效。
- **分布式事务**：如 TCC（Try-Confirm-Cancel）模式中 Confirm 阶段重复调用。

### 2. 业务场景示例

- **支付系统**：用户重复点击支付按钮，应只扣款一次。
- **订单系统**：创建订单接口被重复调用，应返回相同订单号而非生成新订单。
- **库存系统**：减库存操作被重复执行，应避免超卖。

---

## 五大策略总览

| 策略 | 核心思想 | 适用场景 | 实现成本 | 一致性强度 |
|------|----------|----------|----------|------------|
| **Idempotency-Key** | 客户端携带唯一 Key，服务端去重 | 写操作、API 接口 | 中 | 强 |
| **乐观锁（Version）** | 版本号控制并发更新 | 并发更新同一资源 | 低 | 中 |
| **状态机** | 限制合法状态转移 | 订单 / 审批等状态流转 | 低 | 强 |
| **去重表** | 单独维护已处理 ID 表 | MQ 消费、异步任务 | 中 | 强 |
| **悲观锁 / 分布式锁** | 串行化关键操作 | 强一致短事务 | 高 | 最强 |

### 详细对比

| **方案** | **适用场景** | **优点** | **缺点** |
|----------|------------|----------|----------|
| Idempotency-Key | 写操作、API 接口 | 实现简单，通用性强 | 需存储幂等记录，占用资源 |
| 乐观锁 | 并发更新数据 | 无锁竞争，性能好 | 需处理冲突重试 |
| 状态机 | 订单状态流转 | 业务逻辑清晰 | 状态定义需覆盖所有场景 |
| 去重表 | 消息队列消费 | 独立存储，不影响主业务 | 需额外维护表结构 |
| 分布式锁 | 强一致短事务 | 实现简单 | 性能差，可能死锁 |

---

## 选型决策树

```
                            你要做什么操作？
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
         写 API 接口        并发更新同一资源       MQ 消费 / 异步任务
              │                    │                    │
              ▼                    ▼                    ▼
        客户端能否携带           数据有版本号吗？       消息有唯一 ID 吗？
        唯一 Key？                  │                    │
           │                       │                    │
       ┌───┴───┐              ┌────┴────┐               │
       ▼       ▼              ▼         ▼               ▼
   可以     不可以           有 version  无 version     → 去重表
       │       │              │         │             (deduplication-table)
       ▼       ▼              ▼         ▼
  Idempotency-Key  状态机    乐观锁   状态机 +
   (idempotency-key)         (optimistic)  分布式锁

        状态流转？  ──Yes──▶  状态机  (state-machine)

        需要强一致？──Yes──▶  分布式锁 + 上述任一
```

### 组合使用建议

实际生产中常见组合：

- **支付扣款**：Idempotency-Key + 数据库唯一索引（双保险）
- **MQ 消费**：去重表 + 乐观锁
- **订单状态流转**：状态机 + Idempotency-Key（HTTP 入口）
- **库存扣减**：乐观锁 + 分布式锁（高竞争场景）

---

## 策略详解

- [Idempotency-Key 唯一标识](idempotency-key/README.md)
- [乐观锁 / Version](optimistic-lock/README.md)
- [状态机](state-machine/README.md)
- [去重表（Deduplication Table）](deduplication-table/README.md)
- [与分布式事务的关系](vs-distributed-transaction/README.md)

---

## 幂等性设计注意事项

1. **性能权衡**：唯一标识校验可能增加数据库查询或 Redis 访问，需评估 QPS 影响。
2. **过期清理**：幂等记录（如 Redis 中的 `IdempotencyKey`）需设置过期时间，避免内存泄漏。
3. **与分布式事务的关系**：幂等性不能替代分布式事务；面对复杂多服务场景，需结合 [TCC / Saga](../02-distributed/distributed-transaction/README.md) 等模式。详见 [与分布式事务的关系](vs-distributed-transaction/README.md)。
4. **测试覆盖**：通过压测工具（如 JMeter）模拟重复请求，验证幂等性是否生效。

---

## 参考资料

- [Stripe API - Idempotent Requests](https://stripe.com/docs/api/idempotent_requests)
- [IETF Draft - The Idempotency-Key HTTP Header Field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
- [Microsoft Azure - Idempotency patterns](https://learn.microsoft.com/azure/architecture/microservices/design/idempency)


---

## 📊 本节统计

| 子目录 | leaf 主题数 | 备注 |
|:-------|:-----------:|:-----|
| `06-idempotency/`（本文） | 5 | 幂等键 · 乐观锁 · 状态机 · 去重表 · 与分布式事务的关系 |
| ├─ `idempotency-key/` | 1 | 客户端唯一 Key · 服务端去重 |
| ├─ `optimistic-lock/` | 1 | 版本号控制并发更新 |
| ├─ `state-machine/` | 1 | 状态机限制合法转移 |
| ├─ `deduplication-table/` | 1 | 已处理 ID 表 |
| └─ `vs-distributed-transaction/` | 1 | 幂等与事务的关系 |
| **README 覆盖** | 5 depth-2 leaf + 1 顶层 = **6** | 100% frontmatter |
| **聚合主题数** | 5（五大策略） | 全部聚合在本章及子 README |

> 数字基线：以子目录 leaf README 数 + 顶层章节主题数统计

---

← [返回 04.system-design 主模块](../README.md)
