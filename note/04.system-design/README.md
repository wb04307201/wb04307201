# 系统设计笔记

> 系统设计的知识体系图谱，从基础理论到工程实践的完整学习路径。

## 📚 知识地图

```
                    ┌─────────────────────────────────────┐
                    │        04.system-design             │
                    │         系统设计笔记                │
                    └─────────────────┬───────────────────┘
                                      │
        ┌─────────────┬───────────────┼───────────────┬─────────────┐
        ▼             ▼               ▼               ▼             ▼
   ┌─────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐
   │ 01.基础  │  │ 02.分布式  │  │ 03.高可用  │  │ 04.高性能  │  │ 05.安全  │
   │Foundation│  │Distributed│  │  HA       │  │  HP       │  │ Security │
   └─────────┘  └───────────┘  └───────────┘  └───────────┘  └──────────┘
        │             │               │               │             │
        ▼             ▼               ▼               ▼             ▼
   软件工程      CAP/BASE        限流/熔断/重试    负载均衡/CDN    JWT/OAuth2
   开发流程      共识算法        冗余/弹性        缓存/数据库优化  RBAC/API安全
   系统设计      分布式事务      混沌工程          消息队列/Java   权限模型
   OOD/DDD/TOGAF 分布式锁/ID     代码质量          序列化/连接池   数据脱敏
   /ArchiMate   RPC/网关       容灾演练          多级缓存
   /IT4IT      服务发现
   技术债       分布式缓存
```

## 🗺️ 学习路线

### 入门阶段
1. [软件工程](01-foundation/software-engineering/README.md) — 了解软件开发的全貌
2. [开发流程与方法](01-foundation/software-engineering/development-process/README.md) — 瀑布、敏捷、原型模型
3. [系统设计基础](01-foundation/system-design-basics/README.md) — 系统设计的核心步骤

### 进阶阶段
4. [面向对象设计](01-foundation/system-design-basics/ood/README.md) — SOLID/GRASP 原则、类与职责分配
5. [领域驱动设计 DDD](01-foundation/system-design-basics/ddd/README.md) — 以业务为核心的建模
6. [企业架构 TOGAF 10](01-foundation/system-design-basics/togaf/README.md) — 业务能力地图、ADM 9 阶段、模块化架构治理
6a. [架构描述语言 ArchiMate 3.2](01-foundation/system-design-basics/archimate/README.md) — 30+ 视点的企业架构建模语言，与 TOGAF 同源
6b. [IT 价值流参考架构 IT4IT 3.0](01-foundation/system-design-basics/it4it/README.md) — 4 价值流 + 9 功能组件，IT 运营层的"业务模型"
7. [CAP 定理](02-distributed/cap-and-base/cap/README.md) — 分布式系统的理论基石
8. [分布式事务](02-distributed/distributed-transaction/README.md) — 跨服务数据一致性
9. [分布式锁](02-distributed/distributed-lock/README.md) — 分布式协调基础
10. [限流](03-high-availability/rate-limiting/README.md) — 保护系统的第一道防线
11. [熔断](03-high-availability/circuit-break/README.md) — 防止级联故障

### 高级阶段
10. [微服务架构](01-foundation/system-design-basics/microservices/README.md) — 拆分/通信/契约/数据一致性/演进 5 大设计主题
11. [分库分表](04-high-performance/database-optimization/db-sharding/README.md) — 数据库水平扩展
12. [多级缓存](04-high-performance/cache-patterns/README.md) — 极致性能优化
13. [混沌工程](03-high-availability/chaos-engineering/README.md) — 主动注入故障
14. [可观测性](07-deployment/observability/README.md) — 系统运行可视化

### 专项深入
- [OAuth2.0 与 OIDC](05-security/oauth2-oidc/README.md) — 现代鉴权方案
- [架构描述语言 ArchiMate 3.2](01-foundation/system-design-basics/archimate/README.md) — 与 TOGAF 同源的架构建模语言
- [IT 价值流参考架构 IT4IT 3.0](01-foundation/system-design-basics/it4it/README.md) — 4 价值流 + 9 功能组件，IT 运营层的"业务模型"
- [服务注册与发现](02-distributed/service-discovery/README.md) — 微服务基础设施
- [幂等设计](06-idempotency/README.md) — 分布式系统可靠性保障
- [容量规划与压测](07-deployment/capacity-planning/README.md) — 系统容量评估

## 📂 模块导航

| 模块 | 内容数 | 说明 |
|------|--------|------|
| [01 基础篇](01-foundation/README.md) | 18 | 软件工程、OOD/DDD/TOGAF/ArchiMate/IT4IT、技术债 |
| [02 分布式篇](02-distributed/README.md) | 13 | CAP、共识算法、分布式事务、RPC |
| [03 高可用篇](03-high-availability/README.md) | 9 | 限流、熔断、重试、降级、冗余、混沌 |
| [04 高性能篇](04-high-performance/README.md) | 12 | 负载均衡、CDN、缓存、数据库优化、消息队列、连接池、序列化、Java 优化 |
| [05 安全篇](05-security/README.md) | 7 | JWT、OAuth2、API安全、OWASP、加密、密钥管理、访问控制 |
| [06 幂等设计](06-idempotency/README.md) | 5 | 幂等键、乐观锁、状态机、去重表、与分布式事务的关系 |
| [07 部署与运维](07-deployment/README.md) | 3 | 部署架构、可观测性、容量规划 |

## 🆕 最近更新

- 2025-06-04: 全面重构目录结构，新增 7 个章节
- [服务注册与发现](02-distributed/service-discovery/README.md)
- [分布式缓存设计](02-distributed/distributed-cache/README.md)
- [混沌工程](03-high-availability/chaos-engineering/README.md)
- [缓存设计模式](04-high-performance/cache-patterns/README.md)
- [OAuth2.0 与 OIDC](05-security/oauth2-oidc/README.md)
- [可观测性](07-deployment/observability/README.md)
- [容量规划与压测](07-deployment/capacity-planning/README.md)
- 2026-06-10: 新增 [架构描述语言 ArchiMate 3.2](01-foundation/system-design-basics/archimate/README.md) — 与 TOGAF 10 同源的企业架构建模语言，覆盖 30+ 视点
- 2026-06-10: 新增 [IT 价值流参考架构 IT4IT 3.0](01-foundation/system-design-basics/it4it/README.md) — 4 价值流 + 9 功能组件，Open Group 标准组合第三件套
