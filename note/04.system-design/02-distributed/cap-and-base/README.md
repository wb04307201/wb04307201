<!--
module:
  parent: system-design
  slug: system-design/cap-and-base
  type: article
  category: 主模块子文章
  summary: "CAP 定理（三选二不可能兼得）与 BASE 理论（放弃强一致性换取可用性）的工程实践。"
-->

# CAP & BASE

> ⬅️ [返回分布式](../README.md) | [共识算法](../consensus-algorithms/README.md) | [分布式事务](../distributed-transaction/README.md)

分布式系统一致性与可用性的核心理论基石——CAP 揭示了三者不可兼得的根本矛盾，BASE 给出放弃强一致性后的工程实践方案。

---
---

## 🎯 一句话定位

**CAP 告诉你"分布式三选二"，BASE 告诉你"放弃 C 后怎么落地"**——CAP 是理论边界（你不能同时拥有 CA/CP/AP 之外的系统），BASE 是工程妥协（用最终一致性换高可用）。

---

## 📚 章节导航

| 章节 | 文件 | 核心问题 |
|:----:|:----|:---------|
| [CAP 定理](cap/README.md) | Consistency / Availability / Partition tolerance 三者只能取其二 | 分布式系统的理论边界 |
| [BASE 模型](base/README.md) | Basically Available + Soft state + Eventually consistent | 放弃强一致性的工程方案 |

---

## ⚡ 核心速查

| 维度 | CAP | BASE |
|------|-----|------|
| **提出者** | Eric Brewer (2000) | Dan Pritchett (eBay, 2008) |
| **性质** | 理论边界（不可能三角） | 工程妥协（实践方案） |
| **核心论点** | 分布式系统三选二 | 放弃强一致，换高可用 |
| **一致性** | 强一致或弱一致 | **最终一致** |
| **适用系统** | 所有分布式系统 | 高可用优先场景（电商、社交） |
| **典型实现** | ZooKeeper (CP) / Eureka (AP) | 电商订单、NoSQL 存储 |

---

## 🤝 CAP 与 BASE 的关系

```text
CAP 定理告诉我们：分布式系统 P 必选（网络分区无法避免），只能在 C 和 A 之间取舍。

┌────────────┐                ┌────────────┐
│   CP 系统   │                │   AP 系统   │
│  (一致优先) │                │  (可用优先) │
│  ZooKeeper  │                │   Eureka   │
│  etcd       │                │   Cassandra│
└─────┬──────┘                └──────┬─────┘
      │                              │
      │ 放弃 A                       │ 放弃 C
      │                              │
      ▼                              ▼
   强一致方案                     弱一致方案
   (X/Open XA)                   (BASE 模型)
                                  消息队列
                                  Saga
                                  TCC
```

- **CAP 是理论**：告诉你"做不到"
- **BASE 是方案**：教你"怎么做到"
- **现代分布式系统**：大多选择 **AP + BASE**（用最终一致性换可用性）

---

## 🤔 思考

1. **CAP 真的只能三选二吗？** 严格说是"分区发生时三选二"；无分区时 C+A 都可满足。
2. **BASE 就是不用事务吗？** 不是，是"事务弱化"——把全局事务拆为本地事务 + 补偿。
3. **Eureka 为什么是 AP？** 服务发现场景下宁可暂时不一致（拿到旧地址），也要保证可用性。
4. **什么时候该选 CP？** 强一致场景：金融、库存扣减、分布式锁。

---

## 相关章节

- ⬅️ [返回分布式](../README.md)
- [CAP 定理](cap/README.md) — 理论详解
- [BASE 模型](base/README.md) — 工程方案
- [共识算法](../consensus-algorithms/README.md) — Paxos / Raft / Gossip
- [分布式事务](../distributed-transaction/README.md) — Seata / TCC / Saga

← [返回分布式系统](../README.md)
