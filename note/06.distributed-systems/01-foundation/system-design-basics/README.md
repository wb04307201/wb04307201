<!--
module:
  parent: system-design
  slug: system-design-basics
  type: article
  category: 主模块子文章
  summary: 系统设计基础：架构图绘制、API 设计、架构演进、高可用防线、设计模式与微服务全景导览
-->

<!-- index-only -- 此为分类/导览页，链接到下属子章节，非内容占位 -->

# 系统设计基础

> **定位**：从架构图到微服务的全景导览，覆盖 API 设计、架构演进、高可用防线与设计模式。

---

> 系统设计是构建高效、可扩展、可靠软件系统的核心过程。

## 如何使用本模块

- **建议阅读顺序**：先读[架构图绘制](architecture-diagram/)建立表达方式 → 再读 [API 设计](api/README.md)掌握接口规范 → 再读[架构演进](architecture-evolution/README.md)理解认知升级 → 按需读[微服务](microservices/README.md)/[云设计模式](cloud-design-patterns/README.md)。
- **快速入口**：面试备战优先读[高并发与高可用 5 大防线](high-concurrency-and-high-availability-defenses.md)；架构评审优先读 [C4 模型](architecture-diagram/c4-model/README.md)。

## 核心知识

- [系统设计总览](README.md) — 需求分析、架构设计、数据设计、接口设计、安全设计
- [架构图绘制](architecture-diagram/) — 用标准化方式表达系统架构
    - [4+1 视图模型](architecture-diagram/4+1/README.md) — 逻辑/开发/进程/物理/场景五视图，覆盖不同干系人关切
    - [C4 模型](architecture-diagram/c4-model/README.md) — Context/Container/Component/Code 四层抽象，适合从 CTO 到开发者的多层沟通
- [API 设计](api/README.md) — [RESTful](api/rest/README.md) | [GraphQL](api/graphql/README.md) | [RPC](api/rpc/README.md)

## 架构演进

- [架构认知的演进](architecture-evolution/README.md) — OOD → DDD → TOGAF 的认知升级 + Level 1-7 成熟度评估
- [从面条代码到整洁架构](architecture-evolution/from-spaghetti-to-clean.md) — 分层 → 整洁 → 六边形 → 洋葱的代码组织演进史
- [面向对象设计](ood/README.md) — SOLID/GRASP 原则、类与职责分配
- [领域驱动设计](ddd/README.md) — 以业务领域为核心的建模方法
- [企业架构 TOGAF 10](togaf/README.md) — 业务能力地图、ADM 9 阶段、模块化架构治理
- [架构描述语言 ArchiMate 3.2](archimate/README.md) — 与 TOGAF 同源的架构建模语言，30+ 视点给不同人看不同图
- [IT 价值流参考架构 IT4IT 3.0](it4it/README.md) — 4 价值流 + 9 功能组件，IT 运营层的"业务模型"

## 高可用防线

- [高并发与高可用 5 大防线](high-concurrency-and-high-availability-defenses.md) — 缓存/限流/熔断/降级/负载均衡 5 大防线综述 + 决策树 + 落地路线

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

## 反向链

- [functional-components](it4it/functional-components.md)
- [business-capability](togaf/business-capability.md)

← [返回 基础篇](../README.md)
