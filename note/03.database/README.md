# 数据库

> 数据库是按照数据结构来组织、存储和管理数据的仓库。本章节从关系型数据库基础出发,逐步深入到 SQL、事务、索引、MySQL 内部机制,再扩展到缓存、Redis、NoSQL 与连接池。

> 最后更新: 2026-06-09

---

## 知识体系

| 序号 | 主题 | 难度 | 说明 |
|------|------|------|------|
| 1 | [数据库基础知识](01-fundamentals/README.md) | ⭐ 入门 | 核心概念、ER 图、范式、设计步骤 |
| 2 | [SQL](02-sql/README.md) | ⭐ 入门 | SQL 语法、执行顺序、慢查询分析与优化 |
| 3 | [事务与并发控制](03-transaction/README.md) | ⭐⭐ 进阶 | ACID、隔离级别、锁机制、MVCC |
| 4 | [索引](04-index/README.md) | ⭐⭐ 进阶 | B+ 树、聚簇/非聚簇索引、覆盖索引、最左前缀、索引失效 |
| 5 | [MySQL](05-mysql/README.md) | ⭐⭐ 进阶 | 架构、存储引擎、InnoDB 内部机制、主从复制、日志系统 |
| 6 | [缓存](06-cache/README.md) | ⭐⭐ 进阶 | 缓存分类、穿透/击穿/雪崩、缓存与数据库一致性 |
| 7 | [Redis](07-redis/README.md) | ⭐⭐ 进阶 | 数据类型、持久化、集群高可用、内存管理 |
| 8 | [NoSQL 数据库](08-nosql/README.md) | ⭐⭐ 进阶 | NoSQL 分类、SQL vs NoSQL 对比、选型指南 |
| 9 | [数据库连接池](09-connection-pool/README.md) | ⭐ 入门 | HikariCP、Druid、参数配置、监控 |
| 10 | [数据迁移与同步](10-data-migration/README.md) | ⭐⭐ 进阶 | DataX 全量同步、Canal/Maxwell Binlog 订阅、Flink CDC |
| 11 | [数据库监控告警](11-monitoring/README.md) | ⭐⭐ 进阶 | Prometheus + Grafana + AlertManager、慢查询分析 |
| 12 | [云数据库](12-cloud-database/README.md) | ⭐⭐ 进阶 | AWS RDS/Aurora、阿里云 PolarDB、TiDB Cloud、自建 vs 云 |

---

## 学习路线

```
                           ┌──────────────────────┐
                           │  1. 数据库基础知识    │ ← 入门口,先建立全局视野
                           └──────────┬───────────┘
                                      │
                  ┌───────────────────┼───────────────────┐
                  ▼                   ▼                   ▼
        ┌─────────────────┐ ┌────────────────┐ ┌────────────────┐
        │ 2. SQL 语法      │ │ 9. 连接池        │ │ 8. NoSQL 概览   │
        └────────┬────────┘ └────────────────┘ └────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ 4. 索引(B+ 树)      │ ← 性能优化基础
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ 3. 事务与并发控制   │ ← 隔离级别 + 锁 + MVCC
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ 5. MySQL 深入       │ ← InnoDB 引擎、复制、参数
        └────────┬───────────┘
                 │
        ┌────────┴──────────┐
        ▼                   ▼
  ┌──────────┐        ┌──────────┐
  │ 6. 缓存   │        │ 7. Redis  │
  │ 三大问题  │        │ 深入      │
  └──────────┘        └──────────┘
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
   ┌─────────┐ ┌──────┐ ┌──────────┐
   │10.数据迁移│ │11.监控│ │12.云数据库│
   │ Canal等 │ │Prometheus│ │RDS/Aurora│
   └─────────┘ └──────┘ └──────────┘
```

## 前置知识

- 任意一门后端语言基础(Java/Python/Go)
- 基本的计算机网络(TCP 三次握手)
- 数据结构基础(B+ 树、Hash 表)

## 跨章节关联

数据库章节的多个主题与 [04.system-design](../04.system-design/README.md) 深度联动:

- **缓存**: [04.system-design · 缓存设计模式](../04.system-design/04-high-performance/cache-patterns/README.md) 详解 Cache-Aside/Read-Through/Write-Through/Write-Behind
- **Redis**: [04.system-design · 分布式缓存](../04.system-design/02-distributed/distributed-cache/README.md) 讲解缓存架构
- **连接池**: [04.system-design · 连接池](../04.system-design/04-high-performance/connection-pool/README.md) 架构视角的调优
- **主从复制**: 与 [04.system-design · CAP 定理](../04.system-design/02-distributed/cap-and-base/cap/README.md) 共同理解分布式一致性
