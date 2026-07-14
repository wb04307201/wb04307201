<!--
module:
  parent: spring
  slug: spring/transaction/distributed
  type: article
  category: 主模块子文章
  summary: Spring 分布式事务：理论 + Seata 落地
-->

# Spring 分布式事务

> ⬅️ [返回 03 数据层/事务](../README.md) | [返回 Spring 主页](../../README.md)

> **一句话定位**：单库事务用 `@Transactional`，**跨库跨服务事务**用 **Seata + Saga/TCC/2PC** 三件套。本节聚焦 Spring 集成层，理论深度见 [`04.system-design/02-distributed/distributed-transaction`](../../../../04.system-design/02-distributed/distributed-transaction/README.md)。

---

## 🎯 学习目标

完成本节后，你能够：

- **理论**：说清 2PC / 3PC / TCC / Saga / 本地消息表 5 大方案的核心差异与选型
- **落地**：用 Seata AT/TCC/Saga 三种模式集成 Spring Boot 微服务
- **避坑**：识别分布式事务的 6 大反模式（同步阻塞 / 空回滚 / 幂等悬挂 / 脑裂 / 锁膨胀 / 长事务）
- **监控**：配置 Seata TC + RM + TM 三大组件的可观测性

---

## 📚 文章清单（2 篇）

| 主题 | 核心内容 | 阅读时长 |
|------|---------|---------|
| [分布式事务理论与模式](theory-and-patterns.md) | 2PC / 3PC / TCC / Saga / 本地消息表 5 大方案 + 6 大反模式 | 35 min |
| [Seata 分布式事务框架](seata.md) | TC/TM/RM 核心组件 + AT/TCC/Saga/XA 4 种模式 + Spring Boot 集成 | 40 min |

---

## 🔗 兄弟章节

- **理论深度**：[`04.system-design/02-distributed/distributed-transaction`](../../../../04.system-design/02-distributed/distributed-transaction/README.md) — 共识算法 / CAP / BASE 理论
- **工作流视角**：[`07.workflow`](../../../../07.workflow/README.md) — Saga/TCC 也是分布式协作模式
- **咬文嚼字**：[`13.split-hairs/03.database`](../../../../13.split-hairs/03.database/README.md) — 数据库事务隔离级别
- **面试深挖**：[`13.split-hairs/06.spring`](../../../../13.split-hairs/06.spring/README.md) — Spring 事务高频题

---

## ⚠️ 反模式速查

| # | 反模式 | 后果 | 修复 |
|---|--------|------|------|
| 1 | **同步阻塞** | TC 单点 → 全链路雪崩 | TC 集群化 + 异步化 |
| 2 | **空回滚** | TCC Try 未执行 → Cancel 报空 | 记录 Try 状态 + 幂等 |
| 3 | **幂等悬挂** | 重复 Try → Cancel 状态错乱 | 主键去重 + 状态机 |
| 4 | **脑裂** | 网络分区导致双 TC 决策 | 多数派 + 租约机制 |
| 5 | **锁膨胀** | 长事务占用数据库锁 | 异步化 + 补偿 + 最终一致 |
| 6 | **大事务** | 一锁 N 张表 → 性能塌方 | 拆小 + Saga + 异步消息 |

← [返回: Spring 事务](../README.md)