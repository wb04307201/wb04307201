# 03 数据层

> 最后更新: 2026-06-22
> ⬅️ [返回 Spring 顶层](../README.md)

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

03 数据层 本应该很简单，最后更新: 2026-06-22

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 🎯 一句话定位

**Spring 数据层 = 事务管理 + 缓存抽象 + 数据访问（JDBC/JPA/MyBatis）**——本章聚焦"事务"和"缓存"两大支柱，前者保证数据一致性，后者提升性能；新增 **MyBatis 整合**专题，覆盖 Spring × MyBatis 的工程实战。

---

## 📚 章节导航

| 章节 | 文件 | 核心问题 | 建议时长 |
|:----:|:----|:---------|:--------:|
| **事务管理总览** | [transaction/README.md](transaction/README.md) | 声明式事务 vs 编程式事务？事务失效怎么办？ | 30 min |
| **分布式事务** | [transaction/distributed/](transaction/distributed/) | 微服务下如何保证跨服务数据一致性？ | 45 min |
| ├─ 理论 | [theory-and-patterns.md](transaction/distributed/theory-and-patterns.md) | 2PC / TCC / Saga / 本地消息表 | 25 min |
| └─ Seata | [seata.md](transaction/distributed/seata.md) | Seata AT/TCC/XA/SAGA 4 种模式 | 25 min |
| **缓存总览** | [cache/README.md](cache/README.md) | Spring Cache 如何统一多种缓存实现？ | 20 min |
| **MyBatis 全栈** | [mybatis/README.md](mybatis/README.md) | 从架构原理到 Spring 整合到 MyBatis-Plus，一站到底 | 330 min |
| ├─ 架构与原理 | [01-architecture/](mybatis/01-architecture/) | MyBatis 框架原理：架构/初始化/执行/组件/缓存 | 90 min |
| ├─ 扩展能力 | [02-extension/](mybatis/02-extension/) | TypeHandler/拦截器/数据库厂商/存储过程 | 60 min |
| ├─ Spring 整合 | [03-spring-integration/](mybatis/03-spring-integration/) | Spring 如何接管 SqlSessionFactory、Mapper、事务 | 90 min |
| │  ├─ 装配与启动 | [01-assembly-and-startup.md](mybatis/03-spring-integration/01-assembly-and-startup.md) | SqlSessionFactoryBean + MapperScannerConfigurer 配置演进 | 15 min |
| │  ├─ Mapper 与 Boot | [02-mapper-and-boot.md](mybatis/03-spring-integration/02-mapper-and-boot.md) | @MapperScan 原理 + mybatis-spring-boot-starter 自动装配 | 18 min |
| │  ├─ 事务边界 | [03-transaction-boundary.md](mybatis/03-spring-integration/03-transaction-boundary.md) | Spring 事务如何接管 SqlSession？同线程约束与失效场景 | 15 min |
| │  ├─ 多数据源路由 | [04-multi-datasource.md](mybatis/03-spring-integration/04-multi-datasource.md) | AbstractRoutingDataSource + MyBatis SqlSessionTemplate 联动 | 20 min |
| │  └─ 二级缓存与 Redis/Caffeine | [05-secondary-cache-integration.md](mybatis/03-spring-integration/05-secondary-cache-integration.md) | MyBatis 二级缓存整合分布式缓存 | 15 min |
| └─ MyBatis-Plus | [04-mybatis-plus/](mybatis/04-mybatis-plus/) | MP 全家桶：CRUD/Wrapper/分页/生成器 | 90 min |

---

## 🧭 知识地图

```mermaid
graph TB
    D[数据层]
    
    D --> TX[事务管理]
    D --> Cache[缓存]
    D --> DAO[数据访问]
    D --> MyBatis[MyBatis 全栈]
    
    TX --> T1[声明式 @Transactional]
    TX --> T2[编程式 TransactionTemplate]
    TX --> T3[传播行为 7 种]
    TX --> T4[隔离级别 4 种]
    TX --> T5[事务失效场景]
    TX --> T6[分布式事务]
    
    T6 --> T6a[2PC 两阶段提交]
    T6 --> T6b[TCC 补偿事务]
    T6 --> T6c[Saga 长事务]
    T6 --> T6d[本地消息表]
    T6 --> T6e[Seata]
    
    Cache --> C1[@Cacheable/@CachePut/@CacheEvict]
    Cache --> C2[Caffeine 本地]
    Cache --> C3[Redis 分布式]
    Cache --> C4[Ehcache]
    
    MyBatis --> A[架构与原理]
    MyBatis --> E[扩展能力]
    MyBatis --> S[Spring 整合]
    MyBatis --> P[MyBatis-Plus]
    A --> A1[初始化/执行/组件/缓存...]
    E --> E1[TypeHandler/拦截器/存储过程]
    S --> S1[装配/Mapper/事务/多数据源/二级缓存]
    P --> P1[CRUD/Wrapper/分页/生成器]
    
    classDef root fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef leaf fill:#fff3e0,stroke:#f57c00
    class D root
    class TX,Cache,DAO,MyBatis,T1,T2,T3,T4,T5,T6,T6a,T6b,T6c,T6d,T6e,C1,C2,C3,C4,A,E,S,P,A1,E1,S1,P1 leaf
```

---

## ⚡ 核心概念速查

| 概念 | 一句话定义 | 章节 |
|------|----------|:----:|
| **@Transactional** | 声明式事务注解，基于 AOP 实现 | [事务](transaction/README.md) |
| **REQUIRED** | 默认传播行为：加入当前事务或新建 | [事务](transaction/README.md) |
| **REQUIRES_NEW** | 总是新建独立事务，挂起当前事务 | [事务](transaction/README.md) |
| **@Cacheable** | 方法结果缓存（命中缓存则不执行方法） | [缓存](cache/README.md) |
| **@CachePut** | 总是执行方法，并更新缓存 | [缓存](cache/README.md) |
| **@CacheEvict** | 清除缓存 | [缓存](cache/README.md) |
| **Seata** | 阿里开源的分布式事务解决方案 | [Seata](transaction/distributed/seata.md) |
| **AT 模式** | Seata 默认模式：基于 SQL 解析的自动回滚 | [Seata](transaction/distributed/seata.md) |
| **TCC** | Try-Confirm-Cancel 补偿型事务 | [理论](transaction/distributed/theory-and-patterns.md) |
| **Saga** | 长事务拆分多个子事务 + 补偿 | [理论](transaction/distributed/theory-and-patterns.md) |
| **SqlSessionFactoryBean** | 创建 MyBatis SqlSessionFactory 的 FactoryBean | [MyBatis 整合](mybatis/03-spring-integration/01-assembly-and-startup.md) |
| **@MapperScan** | 批量扫描 Mapper 接口的注解 | [MyBatis 整合](mybatis/03-spring-integration/02-mapper-and-boot.md) |
| **SqlSessionTemplate** | Spring 管理的线程安全 SqlSession 包装 | [MyBatis 整合](mybatis/03-spring-integration/03-transaction-boundary.md) |
| **AbstractRoutingDataSource** | 基于 ThreadLocal 动态切换数据源 | [MyBatis 整合](mybatis/03-spring-integration/04-multi-datasource.md) |

---

## 🤔 思考

1. **声明式事务 vs 编程式事务？** 90% 场景用声明式；复杂回滚逻辑用编程式。
2. **事务失效的常见原因？** 非 public 方法、自调用（this 调）、异常被吞、引擎不支持事务。
3. **@Cacheable key 怎么设计？** 业务唯一键，避免高基数（如 userId 单数）。
4. **本地缓存 vs 分布式缓存？** Caffeine 适合单机、高频；Redis 适合集群、数据一致。
5. **分布式事务选型？** 强一致用 Seata AT/2PC；最终一致用消息队列 + 本地消息表。

---

## 相关章节

- ⬅️ [返回 Spring 顶层](../README.md)
- ⬅️ [01 核心容器](../01-core/README.md) — 事务和缓存都基于 AOP 实现
- ➡️ [04 Spring Boot](../04-spring-boot/README.md) — Spring Data JPA 简化数据访问
- [04.system-design/02-distributed/distributed-transaction](../../04.system-design/02-distributed/distributed-transaction/README.md) — 分布式事务理论
- [MyBatis 全栈](mybatis/README.md) — MyBatis 核心原理与 Spring 整合

---

> 🚀 从 [事务管理总览](transaction/README.md) 开始，或直接看 [MyBatis 全栈](mybatis/README.md)
