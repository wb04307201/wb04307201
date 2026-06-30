<!--
module:
  parent: system-design
  slug: system-design/consensus-algorithms
  type: article
  category: 主模块子文章
  summary: 共识算法 本应该很简单，在分布式系统中，多个节点需要就某个值达成一致，这就是共识问题。共识算法是分布式系统的核心基础
-->

# 共识算法

## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

共识算法 本应该很简单，在分布式系统中，多个节点需要就某个值达成一致，这就是共识问题。共识算法是分布式系统的核心基础

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---


> 在分布式系统中，多个节点需要就某个值达成一致，这就是共识问题。共识算法是分布式系统的核心基础。

## 算法对比

| 算法 | 提出年份 | 复杂度 | 容错能力 | 应用场景 |
|------|---------|--------|---------|---------|
| Paxos | 1989 | 高 | F个节点故障 | Google Chubby |
| Raft | 2013 | 低 | F个节点故障 | Etcd、Consul、TiKV |
| Gossip | 1987 | 低 | 最终一致 | Cassandra、Riak、Dynamo |

## 核心概念

- **多数派(Quorum)**：超过半数的节点同意即可确认
- **Leader 选举**：选出协调节点负责决策
- **日志复制**：将状态变更同步到所有节点
- **安全性保证**：已提交的状态不会丢失

## 子章节

- [Paxos](paxos/README.md) — Basic Paxos、Multi Paxos
- [Raft](raft/README.md) — Leader 选举、日志复制、安全性
- [Gossip](gossip/README.md) — 反熵、谣言传播协议

## 参考链接

- [Paxos Made Simple（Lamport 原文）](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf)
- [In Search of an Understandable Consensus Algorithm（Raft 论文）](https://raft.github.io/raft.pdf)
- [etcd 官方文档](https://etcd.io/docs/)
