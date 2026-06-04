# 分布式篇

> 分布式系统是构建大规模、高可用服务的核心技术。本模块涵盖分布式系统的理论基础、共识算法、事务协调、唯一标识等关键主题。

## 理论基础

1. [CAP 定理](cap-and-base/cap/README.md) — 一致性、可用性、分区容错性的权衡
2. [BASE 模型](cap-and-base/base/README.md) — 基本可用、软状态、最终一致性

## 共识算法

3. [共识算法综述](consensus-algorithms/README.md) — 从 Paxos 到 Raft 的演进
4. [Paxos](consensus-algorithms/paxos/README.md) — 最基础的分布式共识算法
5. [Raft](consensus-algorithms/raft/README.md) — 易于理解的共识算法
6. [Gossip](consensus-algorithms/gossip/README.md) — 病毒式传播协议

## 核心组件

7. [分布式事务](distributed-transaction/README.md) — 2PC/3PC/TCC/SAGA/本地消息表
8. [分布式锁](distributed-lock/README.md) — Redis/ZooKeeper/Etcd 实现方案
9. [分布式 ID](distributed-id/README.md) — [UUID](distributed-id/uuid/README.md) | [ULID](distributed-id/ulid/README.md) | [UUID-v7](distributed-id/uuid-v7/README.md) | Snowflake/Leaf

## 服务通信

10. [RPC](rpc/README.md) — [RPC vs REST](rpc/rpc-and-rest/README.md) | [Apache Dubbo](rpc/apache-dubbo/README.md)
11. [API 网关](api-gateway/README.md) — 网关的核心功能与选型
12. [服务注册与发现](service-discovery/README.md) — Eureka/Nacos/Consul

## 数据存储

13. [分布式缓存](distributed-cache/README.md) — Redis Cluster/缓存穿透·击穿·雪崩
