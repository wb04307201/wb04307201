<!--
module:
  number: 03
  slug: database
  topic: 数据库
  audience: 后端工程师 / DBA / 求职面试者
  category: 主模块
  summary: 数据库从关系型基础到 NoSQL、缓存、迁移与云原生,涵盖 SQL、事务、索引、MySQL 内部机制、Redis、NoSQL 与监控告警全链路核心知识。
-->

# 数据库

> 数据库是按照数据结构来组织、存储和管理数据的仓库。本章节从关系型数据库基础出发,逐步深入到 SQL、事务、索引、MySQL 内部机制,再扩展到缓存、Redis、NoSQL 与连接池。


---

## 📚 目录导航

### 🟢 关系型理论基础

> 数据库无关的核心概念，任何 RDBMS 通用的基础知识。

| 序号 | 分类 | 核心内容 | 子 README |
|:----:|------|---------|-----------|
| 01 | [数据库基础知识](01-fundamentals/README.md) | 核心概念、ER 图、范式、设计步骤、数据类型与字符集 | [子入口](01-fundamentals/README.md) |
| 02 | [SQL](02-sql/README.md) | DDL/DML/DQL、语法、执行顺序、慢查询分析与 EXPLAIN、CTE 与窗口函数 | [子入口](02-sql/README.md) |
| 03 | [事务与并发控制](03-transaction/README.md) | ACID、隔离级别、锁机制、MVCC、死锁、Spring 事务传播 | [子入口](03-transaction/README.md) |
| 04 | [索引](04-index/README.md) | B+ 树、聚簇/非聚簇索引、覆盖索引、最左前缀、索引失效与 ICP | [子入口](04-index/README.md) |

### 🔵 引擎深潜

> 特定数据库产品的架构与内部机制。

| 序号 | 分类 | 核心内容 | 子 README |
|:----:|------|---------|-----------|
| 05 | [MySQL](05-mysql/README.md) | 架构、InnoDB 内部机制、主从复制、日志系统、备份与 8.0 新特性 | [子入口](05-mysql/README.md) |
| 07 | [Redis](07-redis/README.md) | 数据类型、持久化、集群高可用、内存管理、分布式锁、Pipeline/Lua | [子入口](07-redis/README.md) |
| 08 | [NoSQL 数据库](08-nosql/README.md) | 5 大类型对比、MongoDB / Cassandra / HBase / ES / Neo4j 与 NewSQL | [子入口](08-nosql/README.md) |

### 🟡 数据访问层

> 应用与数据库之间的中间层技术。

| 序号 | 分类 | 核心内容 | 子 README |
|:----:|------|---------|-----------|
| 06 | [缓存](06-cache/README.md) | 三大经典问题、缓存-数据库一致性、布隆过滤器、热点 Key、多级缓存 | [子入口](06-cache/README.md) |
| 09 | [数据库连接池](09-connection-pool/README.md) | HikariCP、Druid、参数配置、监控、连接泄漏、分库分表场景 | [子入口](09-connection-pool/README.md) |

### 🟣 运维与扩展

> 数据库上线后的运营、监控与演进。

| 序号 | 分类 | 核心内容 | 子 README |
|:----:|------|---------|-----------|
| 10 | [数据迁移与同步](10-data-migration/README.md) | DataX 全量、Canal/Maxwell Binlog 订阅、Flink CDC、迁移实战要点 | [子入口](10-data-migration/README.md) |
| 11 | [数据库监控告警](11-monitoring/README.md) | Prometheus + Grafana + AlertManager、慢查询分析、生产事故案例 | [子入口](11-monitoring/README.md) |
| 12 | [云数据库](12-cloud-database/README.md) | AWS RDS/Aurora、阿里云 PolarDB、TiDB Cloud、自建 vs 云、迁移策略 | [子入口](12-cloud-database/README.md) |

---

## 🎯 适用人群

- **后端工程师**：日常写 SQL、调连接池、对接 ORM，索引与事务是必会基础
- **DBA / SRE**：负责参数调优、主从架构、备份恢复、监控告警与容量规划
- **求职面试者**：ACID、MVCC、索引失效、缓存三大问题是高频考点
- **架构师**：做技术选型与容量评估，需要权衡 MySQL / NoSQL / NewSQL / 云数据库

---

## 🧭 学习路径

- **新人入门**：01 基础 → 02 SQL → 09 连接池（建立日常开发与 CRUD 基础）
- **后端进阶**：04 索引 → 03 事务 → 05 MySQL 内部机制（理解性能与一致性根因）
- **架构方向**：06 缓存 → 07 Redis → 08 NoSQL → 10 数据迁移 → 11 监控 → 12 云数据库（体系化能力）
- **面试冲刺**：03 + 04 + 06 三大高频考点专题背诵

---

## 🗺️ 知识脉络

```mermaid
flowchart TD
    A["1. 数据库基础知识<br/>入门口，先建立全局视野"] --> B["2. SQL 语法"]
    A --> C["9. 连接池"]
    A --> D["8. NoSQL 概览"]
    B --> E["4. 索引（B+ 树）<br/>性能优化基础"]
    E --> F["3. 事务与并发控制<br/>隔离级别 + 锁 + MVCC"]
    F --> G["5. MySQL 深入<br/>InnoDB 引擎、复制、参数"]
    G --> H["6. 缓存<br/>三大问题"]
    G --> I["7. Redis<br/>深入"]
    H --> J["10. 数据迁移<br/>Canal 等"]
    H --> K["11. 监控<br/>Prometheus"]
    H --> L["12. 云数据库<br/>RDS / Aurora"]
```

---

## 📊 速查表

| 概念 | 核心要点 | 典型场景 |
|------|---------|---------|
| **ACID** | 原子性、一致性、隔离性、持久性 | 事务保证 |
| **隔离级别** | RU < RC < RR < Serializable，越高越安全但越慢 | 并发控制选型 |
| **MVCC** | 多版本并发控制，Read View + Undo Log | RR 级别下读写不冲突 |
| **B+ 树索引** | 叶子节点形成有序链表，适合范围查询 | 关系数据库默认索引 |
| **聚簇索引** | 索引和数据存一起，InnoDB 主键索引 | 主键查询直接返回行 |
| **最左前缀** | 联合索引 (a,b,c) 支持 a / a,b / a,b,c | 索引设计原则 |
| **缓存穿透** | 查询不存在数据，击穿到数据库 | 空值缓存 / 布隆过滤器 |
| **缓存击穿** | 热点 key 过期，大量请求打到数据库 | 互斥锁 / 永不过期 |
| **缓存雪崩** | 大量 key 同时过期 | 过期时间加随机值 |
| **HikariCP** | 高性能连接池，默认 Spring Boot 2.x+ | 数据库连接管理 |

---

## 🎯 前置知识

- 任意一门后端语言基础(Java/Python/Go)
- 基本的计算机网络(TCP 三次握手)
- 数据结构基础(B+ 树、Hash 表)

---

## 🔗 相关章节

数据库章节的多个主题与 [04.system-design](../04.system-design/README.md) 深度联动:

- **缓存**: [04.system-design · 缓存设计模式](../04.system-design/04-high-performance/cache-patterns/README.md) 详解 Cache-Aside/Read-Through/Write-Through/Write-Behind
- **Redis**: [04.system-design · 分布式缓存](../04.system-design/02-distributed/distributed-cache/README.md) 讲解缓存架构
- **连接池**: [04.system-design · 连接池](../04.system-design/04-high-performance/connection-pool/README.md) 架构视角的调优
- **主从复制**: 与 [04.system-design · CAP 定理](../04.system-design/02-distributed/cap-and-base/cap/README.md) 共同理解分布式一致性

---

## 🎯 高频面试题（咬文嚼字）

针对面试中反复深挖的细节问题，见 [13.split-hairs/03.database](../13.split-hairs/03.database/)：

| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [缓存穿透 / 击穿 / 雪崩](../13.split-hairs/03.database/redis/cache-penetration-breakdown-avalanche/) | ⭐⭐⭐⭐⭐ | 面试必考三件套 |
| [索引失效的 10 种场景](../13.split-hairs/03.database/mysql/index-failure/) | ⭐⭐⭐⭐⭐ | LIKE 左通配 / 函数 / 类型转换 / OR / 最左前缀 |
| [COUNT(*) vs COUNT(1) vs COUNT(字段)](../13.split-hairs/03.database/relational-database/mysql/count/) | ⭐⭐ | 性能差异 |
| [事务隔离级别](../13.split-hairs/03.database/relational-database/mysql/isolation/) | ⭐⭐⭐⭐ | RU / RC / RR / Serializable |

---

## 📊 本节统计

- **顶层 README 维护状态**：✅ 已对齐 CONTRIBUTING §12（2026-07-01 复检）
- **子分类总数**：12 个（01-fundamentals / 02-sql / 03-transaction / 04-index / 05-mysql / 06-cache / 07-redis / 08-nosql / 09-connection-pool / 10-data-migration / 11-monitoring / 12-cloud-database）
- **子 README 数**：12 个（每个分类 1 个独立 README，无嵌套子目录）
- **frontmatter 覆盖率**：13/13 = 100%
- **配套面试题**：见 `13.split-hairs/03.database/` 子模块
- **统计口径**：子分类按一级目录统计；leaf README 数 = 12（一级子目录 README）

---

## 📖 开源参考

| 项目 | 说明 | 链接 |
|------|------|------|
| MySQL | 最流行的开源关系数据库 | [dev.mysql.com](https://dev.mysql.com) |
| Redis | 高性能内存键值数据库 | [redis.io](https://redis.io) |
| HikariCP | 高性能 JDBC 连接池 | [github.com/brettwooldridge/HikariCP](https://github.com/brettwooldridge/HikariCP) |
| Canal | 阿里开源 MySQL Binlog 订阅 | [github.com/alibaba/canal](https://github.com/alibaba/canal) |
| DataX | 离线数据同步工具 | [github.com/alibaba/DataX](https://github.com/alibaba/DataX) |
| CHMCache | 基于 ConcurrentHashMap 的 LRU 缓存 | [gitee.com/wb04307201/CHMCache](https://gitee.com/wb04307201/CHMCache) |

---

← [返回笔记目录](../README.md)