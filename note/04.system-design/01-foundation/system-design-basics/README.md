<!--
module:
  parent: system-design
  slug: system-design/system-design-basics
  type: article
  category: 主模块子文章
  summary: 系统设计基础 本应该很简单，系统设计是构建高效、可扩展、可靠软件系统的核心过程
-->

<!-- index-only -- 此为分类/导览页，链接到下属子章节，非内容占位 -->

# 系统设计基础

---

> 系统设计是构建高效、可扩展、可靠软件系统的核心过程。

## 核心知识

- [系统设计总览](README.md) — 需求分析、架构设计、数据设计、接口设计、安全设计
- [架构图绘制](architecture-diagram/) — 用标准化方式表达系统架构
    - [4+1 视图模型](architecture-diagram/4+1/README.md)
    - [C4 模型](architecture-diagram/c4-model/README.md)
- [API 设计](api/README.md) — [RESTful](api/rest/README.md) | [GraphQL](api/graphql/README.md) | [RPC](api/rpc/README.md)

## 架构演进

- [架构认知的演进](architecture-evolution/README.md) — OOD → DDD → TOGAF 的认知升级 + Level 1-7 成熟度评估
- [面向对象设计](ood/README.md) — SOLID/GRASP 原则、类与职责分配
- [领域驱动设计](ddd/README.md) — 以业务领域为核心的建模方法
- [企业架构 TOGAF 10](togaf/README.md) — 业务能力地图、ADM 9 阶段、模块化架构治理
- [架构描述语言 ArchiMate 3.2](archimate/README.md) — 与 TOGAF 同源的架构建模语言，30+ 视点给不同人看不同图
- [IT 价值流参考架构 IT4IT 3.0](it4it/README.md) — 4 价值流 + 9 功能组件，IT 运营层的"业务模型"

## 架构模式

- [设计模式](design-patterns/README.md) — GoF 23 种经典模式
- [微服务架构](microservices/README.md) — 服务拆分、通信、契约、数据一致性、演进 5 大设计主题
    - [服务拆分策略](microservices/service-decomposition/README.md) — 业务能力 → 限界上下文 → 服务边界
    - [服务间通信](microservices/service-communication/README.md) — 同步 vs 异步、API 版本管理
    - [服务契约](microservices/service-contract/README.md) — OpenAPI/Protobuf/契约测试
    - [数据一致性](microservices/data-consistency/README.md) — Saga/CQRS/Event Sourcing
    - [演进与组织](microservices/migration-and-organization/README.md) — 单体迁移、团队拓扑
    - [微服务与 DDD](microservices/microservices-and-ddd/README.md) — 业务能力 → 限界上下文 → 服务
- [云设计模式](cloud-design-patterns/README.md) — 云原生架构模式
- [多租户 SaaS 架构](multi-tenant-architecture/README.md) — 6 大数据隔离模型 + 4 大应用层关注点 + PostgreSQL RLS + 飞书/钉钉/Salesforce 生产实践
- [事件驱动 vs 异步](eda-vs-async/README.md) — 两种解耦模式的选择

---

← [返回 基础篇](../README.md)
