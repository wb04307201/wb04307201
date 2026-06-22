# 03 数据层

> 最后更新: 2026-06-22
> ⬅️ [返回 Spring 顶层](../README.md)

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
| **MyBatis 整合** | [mybatis-integration/README.md](mybatis-integration/README.md) | Spring 如何整合 MyBatis？事务、Mapper、多数据源、缓存？ | 90 min |
| ├─ 经典 XML 整合 | [01-classic-integration.md](mybatis-integration/01-classic-integration.md) | SqlSessionFactoryBean + MapperScannerConfigurer 配置演进 | 15 min |
| ├─ @MapperScan 与 Boot | [02-mapper-scan-and-boot.md](mybatis-integration/02-mapper-scan-and-boot.md) | @MapperScan 原理 + mybatis-spring-boot-starter 自动装配 | 18 min |
| ├─ @Transactional 事务边界 | [03-transaction-with-mybatis.md](mybatis-integration/03-transaction-with-mybatis.md) | Spring 事务如何接管 SqlSession？同线程约束与失效场景 | 15 min |
| ├─ 多数据源路由 | [04-multi-datasource.md](mybatis-integration/04-multi-datasource.md) | AbstractRoutingDataSource + MyBatis SqlSessionTemplate 联动 | 20 min |
| └─ 二级缓存与 Redis/Caffeine | [05-secondary-cache-integration.md](mybatis-integration/05-secondary-cache-integration.md) | MyBatis 二级缓存整合分布式缓存 | 15 min |

---

## 🧭 知识地图

```mermaid
graph TB
    D[数据层]
    
    D --> TX[事务管理]
    D --> Cache[缓存]
    D --> DAO[数据访问]
    D --> MyBatis[MyBatis 整合]
    
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
    
    MyBatis --> M1[经典 XML 整合]
    MyBatis --> M2[@MapperScan + Boot]
    MyBatis --> M3[@Transactional 事务边界]
    MyBatis --> M4[多数据源路由]
    MyBatis --> M5[二级缓存整合]
    
    classDef root fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef leaf fill:#fff3e0,stroke:#f57c00
    class D root
    class TX,Cache,DAO,MyBatis,T1,T2,T3,T4,T5,T6,T6a,T6b,T6c,T6d,T6e,C1,C2,C3,C4,M1,M2,M3,M4,M5 leaf
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
| **SqlSessionFactoryBean** | 创建 MyBatis SqlSessionFactory 的 FactoryBean | [MyBatis 整合](mybatis-integration/01-classic-integration.md) |
| **@MapperScan** | 批量扫描 Mapper 接口的注解 | [MyBatis 整合](mybatis-integration/02-mapper-scan-and-boot.md) |
| **SqlSessionTemplate** | Spring 管理的线程安全 SqlSession 包装 | [MyBatis 整合](mybatis-integration/03-transaction-with-mybatis.md) |
| **AbstractRoutingDataSource** | 基于 ThreadLocal 动态切换数据源 | [MyBatis 整合](mybatis-integration/04-multi-datasource.md) |

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
- [04.system-design/02-distributed/distributed-transaction](../04.system-design/02-distributed/distributed-transaction/README.md) — 分布式事务理论
- [08.mybatis/README.md](../../08.mybatis/README.md) — MyBatis 核心原理

---

> 🚀 从 [事务管理总览](transaction/README.md) 开始，或直接看 [MyBatis 整合专题](mybatis-integration/README.md)
