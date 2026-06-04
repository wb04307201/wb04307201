# 共识算法

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
