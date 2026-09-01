<!--
module:
  number: 03
  slug: data-stack
  topic: 数据栈（数据库 + 缓存 + 消息队列 + 大数据生态）
  audience: 后端工程师 / DBA / 数据架构师 / 求职面试者
  category: 主模块
  summary: 数据栈模块覆盖数据库基础、SQL/事务/索引、MySQL/PostgreSQL/Redis/NoSQL、连接池/迁移/监控/云数据库，以及大数据数仓/实时计算/数据湖/OLAP/调度/治理/同步工具全链路。
  depth: ⭐⭐⭐
-->

# 03. Data Stack（数据栈）

> **定位**：覆盖数据库（关系型 + NoSQL + NewSQL）、数据访问层（连接池 / 缓存 / 迁移 / 监控）、以及大数据生态（数仓 / 实时计算 / 数据湖 / OLAP / 调度 / 治理 / 同步工具）的全链路知识地图。
> **继承规范**：[SPEC.md](./SPEC.md)

---

## 目录导航

| # | 子模块 | 主题 | 子目录数 |
|---|--------|------|----------|
| 1 | [01-database](./01-database/) | 数据库（基础 / SQL / 事务 / 索引 / MySQL / PostgreSQL / Redis / NoSQL / 连接池 / 迁移 / 监控 / 云数据库） | 13 个分类 + 4 个 leaf |
| 2 | [02-big-data](./02-big-data/) | 大数据（数仓架构 / Hadoop 生态 / 实时计算 / 数据湖 / OLAP / 调度 / 数据治理 / 同步工具） | 8 个分类 + 3 个 leaf |

> 缓存与消息队列的专题内容规划在 Phase 2+ 单独沉淀，本模块 Phase 1 优先沉淀数据库与大数据两大主轴。

---

## 子模块速览

### 01-database（数据库）

> 从关系型数据库基础出发，覆盖 SQL、事务、索引、MySQL 内部机制，再扩展到 Redis、NoSQL 与连接池。

- **关系型理论基础**：数据库基础、SQL、事务、索引
- **引擎深潜**：MySQL、PostgreSQL、Redis、NoSQL（MongoDB / Cassandra / Elasticsearch / Neo4j）
- **数据访问层**：缓存、连接池
- **运维与扩展**：数据迁移、监控告警、云数据库

详见：[01-database/README.md](./01-database/README.md)

### 02-big-data（大数据）

> 从数仓架构到 OLAP、数据湖、治理——大数据技术栈的完整地图。

- **数仓架构**：Lambda / Kappa / 湖仓一体
- **Hadoop 生态**：HDFS / YARN / Hive / Trino
- **实时计算**：Flink / Spark Streaming
- **数据湖**：Iceberg / Hudi / Delta Lake
- **OLAP**：Doris / StarRocks / ClickHouse
- **调度**：Airflow / DolphinScheduler / Azkaban
- **数据治理**：Atlas / DataHub / 数据血缘 / 数据质量
- **同步工具**：DataX / SeaTunnel / Sqoop / Flume

详见：[02-big-data/README.md](./02-big-data/README.md)

---

## 适用人群

- **后端工程师**：日常 SQL、连接池、缓存、迁移同步是基础能力
- **DBA / SRE**：参数调优、主从架构、备份恢复、监控告警、容量规划
- **数据工程师**：数仓分层、实时计算、ETL/CDC 管道、调度编排
- **数据架构师**：Lambda/Kappa/湖仓一体选型，OLAP/Data Lake/治理体系搭建
- **求职面试者**：ACID、MVCC、索引失效、缓存三大问题、Hive/Spark/Flink 内部机制是高频考点

---

## 学习路径

### 数据库方向

- **新人入门**：01 基础 → 02 SQL → 09 连接池
- **后端进阶**：04 索引 → 03 事务 → 05 MySQL 内部机制
- **架构方向**：06 缓存 → 07 Redis → 08 NoSQL → 10 数据迁移 → 11 监控 → 12 云数据库

### 大数据方向

- **新人入门**：01 数仓架构 → 02 Hadoop 生态 → 03 实时计算 → 06 调度 → 05 OLAP
- **离线数仓方向**：02 Hadoop 生态 → 01 数仓架构 → 06 调度 → 07 数据治理
- **实时计算方向**：03 实时计算 → 01 Kappa 架构 → 04 数据湖 → 05 OLAP
- **数据架构师**：01 → 02 → 03 → 04 → 05 → 07 全链路贯通

---

## 🔗 相关章节

- **上游基础**：[02.cs-foundations](../02.cs-foundations/README.md)（算法 / OS / 网络 / 运维）
- **应用层**：[04.spring-backend](../04.spring-backend/README.md)（Spring 集成数据库 / 实时数仓）
- **分布式联动**：[06.distributed-systems](../06.distributed-systems/README.md)（分布式事务 / 共识 / 高可用）
- **AI 数据**：[08.ai-foundations](../08.ai-foundations/README.md)（训练数据湖 / 特征工程）

> 上述章节当前部分仍在 Phase 2+ 沉淀中，部分链接可能指向 note/ 旧模块。短期落地可参考对应 note/ 子模块（Phase 1 兼容）。

---

## 📊 本节统计

| 统计维度 | 数值 | 口径 |
|----------|------|------|
| 子模块数 | 2 | `01-database` + `02-big-data` |
| 子 README 总数 | 31 | 19（database）+ 12（big-data），含 1 顶层 + 12 分类 + 5 leaf + ... |
| database 分类 | 13 | 01-fundamentals / 02-sql / 03-transaction / 04-index / 05-mysql / 06-cache / 07-redis / 08-nosql / 09-connection-pool / 10-data-migration / 11-monitoring / 12-cloud-database / 13-postgresql |
| big-data 分类 | 8 | 01-data-warehouse / 02-hadoop-ecosystem / 03-realtime-compute / 04-data-lake / 05-olap / 06-scheduling / 07-data-governance / 08-sync-tools |
| frontmatter 覆盖率 | 31 / 31 = 100% | 全部迁移自 note/ 已带 frontmatter |
| 配套面试题 | 见 `13.split-hairs/03.database` 与 `13.split-hairs/10.big-data` | 沿用旧模块挂载 |
| 顶层 README 字数 | database 191 行 / big-data 248 行 | 保持叶子层不动 |

> **统计时间戳**：2026-08-12（Plan 2 Task 2 完成）

---

## 📌 后续计划（Phase 2+）

- 单独沉淀 **03-cache**（缓存专题，从 01-database/06-cache 提升）与 **03-mq**（消息队列）
- 修复所有跨 note/ 旧模块的反向链接（链接到 note 同名模块）
- 与 11.interview / 12.story 联动，补齐咬文嚼字面试题与阿明餐厅故事章节

---

← [返回 note 总目录](../README.md)
