# 数据库

数据库是按照数据结构来组织、存储和管理数据的仓库。本章节从关系型数据库基础出发，逐步深入到 SQL、事务、索引、MySQL 内部机制，再扩展到缓存、Redis 和 NoSQL 数据库。

---

## 知识体系

| 序号 | 主题 | 说明 |
|------|------|------|
| 1 | [数据库基础知识](01-fundamentals/README.md) | 核心概念、ER 图、范式、设计步骤 |
| 2 | [SQL](02-sql/README.md) | SQL 语法、执行顺序、慢查询分析与优化 |
| 3 | [事务与并发控制](03-transaction/README.md) | ACID、隔离级别、锁机制、MVCC |
| 4 | [索引](04-index/README.md) | B+ 树、聚簇/非聚簇索引、覆盖索引、最左前缀、索引失效 |
| 5 | [MySQL](05-mysql/README.md) | 架构、存储引擎、InnoDB 内部机制、主从复制、日志系统 |
| 6 | [缓存](06-cache/README.md) | 缓存分类、穿透/击穿/雪崩、缓存与数据库一致性 |
| 7 | [Redis](07-redis/README.md) | 数据类型、持久化、集群高可用、内存管理 |
| 8 | [NoSQL 数据库](08-nosql/README.md) | NoSQL 分类、SQL vs NoSQL 对比、选型指南 |
| 9 | [数据库连接池](09-connection-pool/README.md) | HikariCP、Druid、参数配置、监控 |

---

## 学习路线

```
数据库基础 → SQL → 事务与并发 → 索引 → MySQL 深入
                                         ↓
                                    缓存策略 → Redis → 连接池
                                         ↓
                                       NoSQL
```
