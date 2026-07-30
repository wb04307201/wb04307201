<!--
question:
  id: 03.database-sharding-distributed-tx
  topic: 03.database
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构困境
  tags: [03.database, sharding, distributed-transaction]
-->

# 分库分表后分布式事务怎么搞？

> 分库分表后数据分散在多个数据库，单机事务无法跨库——这就是分库分表带来的分布式事务问题。与[通用分布式事务](../../04.system-design/distributed-transaction/)的区别：本题聚焦**同库多表 / 多库多表**场景，不是跨微服务。

---

## 引子：一个订单跨 2 个库

```text
场景：order 表按 user_id % 4 分成 4 库
一个"组合支付"操作：
  - 扣用户 A 的余额（在 order_0 库）
  - 扣用户 B 的余额（在 order_2 库）
  - 创建合并订单记录

本地事务搞不定——数据在 2 个物理库！
```

面试官问："分库后跨库事务你怎么做？" 如果你只回答"用 Seata"——面试就结束了。

---

## 一、问题本质

分库分表后，**数据不再属于同一个事务边界**：

```text
分库前：所有数据在同一个 MySQL 实例
  BEGIN;
  UPDATE account SET balance = balance - 100 WHERE user_id = 1;
  UPDATE account SET balance = balance - 50  WHERE user_id = 2;
  COMMIT;  ← 单机 ACID，天然保证

分库后：user_1 在 DB-A，user_2 在 DB-B
  DB-A 的 COMMIT 成功了，DB-B 网络超时 → 数据不一致
```

**核心矛盾**：分库提高了扩展性，但牺牲了事务的原子性。

**3 种分库分表事务场景**：

| 场景 | 示例 | 难度 |
|------|------|------|
| 同库同表 | `user_id % 4` 都在 DB-0 | ✅ 本地事务即可 |
| 同库多表 | `user_id % 16`，4 表在同一库 | ✅ 本地事务可跨表 |
| **多库多表** | `user_id % 16`，分 4 库 × 4 表 | ❌ 本地事务无法跨库 |

> 只有**多库多表**才需要分布式事务。同库多表（即使 16 张表）仍然可以一个本地事务搞定。

---

## 二、4 大方案对比

| 方案 | 一致性 | 性能 | 复杂度 | 适用场景 |
|------|--------|------|--------|---------|
| **2PC/XA** | 强一致 | ❌ 差（同步阻塞 + 长锁） | 中 | 几乎不用（性能太差） |
| **TCC** | 强一致 | ⭐⭐⭐ 中（无长事务锁） | ❌ 高（3 个接口 × N 服务） | 金融 / 交易强一致场景 |
| **Saga** | 最终一致 | ⭐⭐⭐⭐ 好 | 中（补偿逻辑） | 长流程 / 跨多分片 |
| **本地消息表 + MQ** | 最终一致 | ⭐⭐⭐⭐⭐ 优 | ✅ 低 | **分库分表场景首选** |

> 与[通用分布式事务](../../04.system-design/distributed-transaction/)的 4 方案一致，但**侧重点不同**：分库分表场景通常不涉及跨服务 RPC，而是同服务内跨 DB 的物理分片，所以本地消息表方案更轻量。

---

## 三、生产推荐方案：本地消息表 + MQ 事务消息

### 3.1 架构

```text
┌─────────────┐     ┌──────────────────┐     ┌──────────┐
│  业务服务    │     │  本地消息表       │     │ RocketMQ │
│  (跨 2 个库) │────▶│  (与业务同库同事务) │────▶│ 事务消息  │
└─────────────┘     └──────────────────┘     └──────────┘
                                                │
                                          ┌─────┴─────┐
                                          ▼           ▼
                                     补偿服务     下游服务消费
                                     (定时重试)   (扣库存/发通知)
```

### 3.2 核心流程

```text
Step 1: 本地事务
  BEGIN;
  -- 业务操作（在 DB-A 扣用户 A 余额）
  UPDATE account_db_a SET balance = balance - 100 WHERE user_id = 1;
  -- 写消息表（在同一事务中）
  INSERT INTO msg_table (msg_id, topic, payload, status)
    VALUES ('m001', 'DEDUCT_B', '{userId:2,amount:50}', 'PENDING');
  COMMIT;  ← 本地事务保证业务 + 消息要么都写、都不写

Step 2: 发送 MQ
  扫描 msg_table WHERE status = 'PENDING'
  → 发送 RocketMQ 事务消息
  → 更新 status = 'SENT'

Step 3: 下游消费
  消费者收到消息 → 扣用户 B 余额（DB-B）
  → ACK 确认

Step 4: 补偿兜底
  定时任务扫描 status = 'SENT' 超过 30s 的消息
  → 查询下游状态 → 未消费则重发（幂等保障）
```

### 3.3 关键保障

| 保障点 | 实现方式 | 说明 |
|--------|---------|------|
| **消息幂等** | 下游用 `msg_id` 做唯一索引 / 去重表 | 防止 MQ 重复投递 |
| **定时补偿** | XXL-Job 每 10s 扫描，重试 3 次 | 超过 3 次转人工告警 |
| **Canal 优化** | Canal 监听 Binlog → MQ | 业务代码零侵入，去掉消息表 |
| **消息顺序性** | 同一订单消息路由到同一 Partition | 避免乱序导致重复扣款 |
| **对账脚本** | 每日凌晨对比分库总账 | 发现不一致立即告警 |

### 3.4 RocketMQ 事务消息示例

```java
// 半消息（Half Message）— 消费者此时看不到
TransactionMQProducer producer = new TransactionMQProducer("tx_producer");
producer.setTransactionListener(new TransactionListener() {
    @Override
    public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
        // 本地事务执行（与业务同事务）
        return LocalTransactionState.COMMIT_MESSAGE; // 提交消息
    }
    @Override
    public LocalTransactionState checkLocalTransaction(MessageExt msg) {
        // 回查本地事务状态（防止本地事务超时未决）
        return LocalTransactionState.COMMIT_MESSAGE;
    }
});
```

> **半消息机制**：MQ 先收到"半消息"（对消费者不可见），等本地事务返回 COMMIT 才对下游可见——天然防止"消息发了但本地事务回滚"。

---

## 四、Seata 框架速览

Seata 是阿里开源的分布式事务框架，支持 4 种模式：

| 模式 | 原理 | 性能 | 侵入性 | 分库分表适用性 |
|------|------|------|--------|----------------|
| **AT**（默认） | 自动生成 undo_log，二阶段自动回滚 | ⭐⭐⭐⭐ | 低（只需加注解） | ⚠️ 分库后需配多数据源 |
| **TCC** | 手动实现 Try/Confirm/Cancel | ⭐⭐⭐ | 高 | 可控性好，但工作量大 |
| **Saga** | 状态机编排 + 补偿 | ⭐⭐⭐⭐ | 中 | 适合跨多分片长流程 |
| **XA** | 数据库原生 XA 协议 | ⭐ 差 | 无 | 不推荐（性能太差） |

**生产建议**：AT 模式上手最快，但分库场景需注意 undo_log 表要部署在每个分库。

**分库场景注意事项**：
- Seata Server（TC）必须高可用部署
- 每个分库都要有 `undo_log` 表（AT 模式）
- 分支事务超时默认 60s，长流程需调大
- TCC 模式需要手动处理**空回滚**和**悬挂**问题

---

## 五、面试话术（30 秒版）

> "分库分表后跨库事务，核心思路是用**最终一致**代替强一致。
>
> **4 种方案**：2PC/XA（强一致但性能差，基本不用）、TCC（强一致但代码复杂，金融场景用）、Saga（长事务友好，补偿逻辑难写）、本地消息表 + MQ（最终一致，实现简单，**主流方案**）。
>
> **生产推荐**：本地消息表 + RocketMQ 事务消息。关键保障 3 件事——消息幂等（唯一索引去重）、定时补偿（3 次重试）、Canal 监听 Binlog 可代替消息表。
>
> **框架层面**：Seata 的 AT 模式最轻量（只需加 `@GlobalTransactional`），但 undo_log 要部署到每个分库。
>
> 核心取舍：**一致性 vs 性能 vs 复杂度，没有银弹。**"

---

## 六、交叉引用

- 通用方案：[分布式事务](../../04.system-design/distributed-transaction/) — 微服务视角的分布式事务 4 方案
- 同模块：[分表扩容策略](../sharding-resize/) — 分库分表 + 在线 resharding 方案
- 同模块：[分库分表分页查询](../sharding-pagination/) — 分库分表后分页 4 大方案 + 生产推荐
- 跨模块：[微服务数据一致性](../../../04.system-design/01-foundation/system-design-basics/microservices/data-consistency/) — 微服务间数据一致性保障

## 相关章节

- 深度阅读：[`03.database`](../../03.database/README.md) — 数据库咬文嚼字全景（MySQL / Redis / 分库分表）

← [返回: 咬文嚼字 · sharding-distributed-tx](../README.md)
