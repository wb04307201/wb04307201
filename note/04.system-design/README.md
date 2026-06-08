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
   技术债       RPC/网关       容灾演练          多级缓存
               服务发现
               分布式缓存
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
5. [CAP 定理](02-distributed/cap-and-base/cap/README.md) — 分布式系统的理论基石
6. [分布式事务](02-distributed/distributed-transaction/README.md) — 跨服务数据一致性
7. [分布式锁](02-distributed/distributed-lock/README.md) — 分布式协调基础
8. [限流](03-high-availability/rate-limiting/README.md) — 保护系统的第一道防线
9. [熔断](03-high-availability/circuit-break/README.md) — 防止级联故障

### 高级阶段
10. [微服务架构](01-foundation/system-design-basics/microservices/README.md) — 拆分/通信/契约/数据一致性/演进 5 大设计主题
11. [分库分表](04-high-performance/database-optimization/db-sharding/README.md) — 数据库水平扩展
12. [多级缓存](04-high-performance/cache-patterns/README.md) — 极致性能优化
13. [混沌工程](03-high-availability/chaos-engineering/README.md) — 主动注入故障
14. [可观测性](07-deployment/observability/README.md) — 系统运行可视化

### 专项深入
- [OAuth2.0 与 OIDC](05-security/oauth2-oidc/README.md) — 现代鉴权方案
- [服务注册与发现](02-distributed/service-discovery/README.md) — 微服务基础设施
- [幂等设计](06-idempotency/README.md) — 分布式系统可靠性保障
- [容量规划与压测](07-deployment/capacity-planning/README.md) — 系统容量评估

## 📂 模块导航

| 模块 | 内容数 | 说明 |
|------|--------|------|
| [01 基础篇](01-foundation/README.md) | 16 | 软件工程、OOD/DDD/TOGAF、技术债 |
| [02 分布式篇](02-distributed/README.md) | 13 | CAP、共识算法、分布式事务、RPC |
| [03 高可用篇](03-high-availability/README.md) | 9 | 限流、熔断、重试、降级、冗余、混沌 |
| [04 高性能篇](04-high-performance/README.md) | 11 | 负载均衡、缓存、数据库优化、消息队列 |
| [05 安全篇](05-security/README.md) | 4 | JWT、OAuth2、权限模型、API安全 |
| [06 幂等设计](06-idempotency/README.md) | 1 | 幂等性设计与实现方案 |
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
