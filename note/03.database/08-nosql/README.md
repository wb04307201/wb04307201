<!--
module:
  parent: database
  slug: database/nosql
  type: index
  category: 主模块子文章
  summary: NoSQL 涵盖键值、文档、列存储、图、搜索 5 大类型,天生支持分布式扩展,以最终一致性换取扩展性;NewSQL 融合 SQL + NoSQL 优势。
-->

# NoSQL 数据库

> NoSQL（Not Only SQL）泛指非关系型数据库，涵盖键值、文档、列存储、图、搜索 5 大类型，天生支持分布式扩展，适用于大规模数据存储和高并发场景；但普遍以最终一致性换取扩展性。

---

## 📚 核心内容

| 主题 | 内容 | 关键点 |
|------|------|--------|
| 一、NoSQL 的四大优势 | 灵活 Schema / 水平扩展 / 高性能 / 丰富 API | 适合大规模与高并发 |
| 二、五种 NoSQL 类型 | 键值 / 文档 / 列存储 / 图 / 搜索 | 5 大代表产品对比 |
| 三、SQL vs NoSQL 对比 | 数据模型 / Schema / 事务 / 扩展 / 一致性 | SQL 强一致，NoSQL 多最终一致 |
| 四、选型指南 | 场景 → 类型 → 产品 | 混合使用 Polyglot Persistence |
| MongoDB 专题 | BSON / 副本集 / 分片 / 聚合管道 | → [mongodb/](mongodb/README.md) |
| Cassandra 专题 | 列存储 / Query-first Design / 可调一致性 | → [cassandra/](cassandra/README.md) |
| HBase 架构 | HMaster / RegionServer / LSM Tree | 本页面内 |
| Elasticsearch 专题 | 倒排索引 / BM25 / ELK / 向量检索 | → [elasticsearch/](elasticsearch/README.md) |
| Neo4j 专题 | 图数据库 / Cypher / N 度关系查询 | → [neo4j/](neo4j/README.md) |
| NewSQL | TiDB / CockroachDB / Spanner | 兼具 ACID + 水平扩展 |
| CAP 定理 | P 必须满足，C/A 取舍 | MongoDB CP，Redis AP |

---

## 一、NoSQL 的四大优势

| 优势 | 说明 |
|------|------|
| **灵活 Schema** | 无需预定义表结构，支持半结构化和非结构化数据 |
| **水平扩展** | 通过增加服务器横向扩展，而非升级单机硬件 |
| **高性能** | 针对特定数据模型和访问模式优化 |
| **丰富的 API** | 提供专用的数据类型和查询接口 |

---

## 二、五种 NoSQL 类型

| 类型 | 数据模型 | 代表产品 | 典型场景 |
|------|---------|---------|---------|
| **键值存储** | Key → Value | Redis、DynamoDB、Riak | 缓存、Session、计数器 |
| **文档型** | JSON/BSON 文档 | MongoDB、CouchDB | Web 应用、CMS、用户画像 |
| **列存储** | 列族（Column Family） | Cassandra、HBase、Bigtable | 时序数据、日志、物联网 |
| **图数据库** | 节点 + 边 | Neo4j、Amazon Neptune | 社交网络、推荐系统、知识图谱 |
| **搜索引擎** | 倒排索引 | Elasticsearch、Solr | 全文搜索、日志分析 |

### 各类型优缺点

| 类型 | 优点 | 缺点 |
|------|------|------|
| 键值 | 查询速度极快，易扩展 | 无结构化，只支持简单操作 |
| 文档 | Schema 灵活，JSON 友好 | 查询语法不统一，JOIN 困难 |
| 列存储 | 大规模写入性能好，易扩展 | 功能局限，不适合复杂查询 |
| 图 | 关系查询高效（N 度关系） | 分布式集群困难 |
| 搜索 | 全文检索能力强 | 不适合事务处理 |

---

## 三、SQL vs NoSQL 对比

| 维度 | SQL（关系型） | NoSQL（非关系型） |
|------|-------------|-----------------|
| 数据模型 | 结构化表格（行+列） | 文档/键值/列族/图 |
| Schema | 固定，需预先定义 | 灵活，可动态变更 |
| 事务 | 完整 ACID 支持 | 多数不支持完整 ACID（MongoDB 4.0+ 部分支持） |
| 扩展方式 | 垂直扩展（升级硬件）+ 分库分表 | 水平扩展（增加节点） |
| 查询语言 | 标准 SQL | 各产品自有 API |
| 一致性 | 强一致性 | 最终一致性（多数） |
| 发展历程 | 1970 年代 | 2000 年代后期 |
| 典型产品 | MySQL、PostgreSQL、Oracle | Redis、MongoDB、Cassandra |

---

## 四、选型指南

| 场景 | 推荐类型 | 推荐产品 |
|------|---------|---------|
| 电商订单、金融交易 | 关系型 | MySQL、PostgreSQL |
| 缓存、Session 管理 | 键值存储 | Redis |
| 用户画像、内容管理 | 文档型 | MongoDB |
| 物联网时序数据 | 列存储 | Cassandra、TDengine |
| 社交关系、推荐系统 | 图数据库 | Neo4j |
| 全文搜索、日志分析 | 搜索引擎 | Elasticsearch |
| 高并发读写、海量数据 | 键值/列存储 | Redis + Cassandra |

### 混合使用（Polyglot Persistence）

实际项目中通常混合使用多种数据库：

```
MySQL    → 核心业务数据（订单、用户）
Redis    → 缓存 + 计数器 + 分布式锁
MongoDB  → 日志 + 用户行为数据
ES       → 搜索 + 日志分析
```

---

## 📚 子专题

| 数据库 | 核心内容 | 入口 |
|--------|---------|------|
| MongoDB | BSON 文档存储、副本集、分片集群、聚合管道 | [mongodb/](mongodb/README.md) |
| Cassandra | 列存储、Query-first Design、可调一致性 | [cassandra/](cassandra/README.md) |
| Elasticsearch | 倒排索引、BM25、ELK、向量检索 | [elasticsearch/](elasticsearch/README.md) |
| Neo4j | 图数据库、Cypher、N 度关系查询 | [neo4j/](neo4j/README.md) |

---

## 八、HBase 架构

### 1. 整体架构

```
       Client
          ↓
    ┌─────────────┐
    │   ZooKeeper │  ← 集群协调
    └─────────────┘
          ↓
   ┌──────────────┐         ┌──────────────┐
   │   HMaster    │  ← 元数据、Region 管理
   └──────────────┘         └──────────────┘
          ↓                       ↓
   ┌──────────────────────────────────────────┐
   │           RegionServer                    │
   │  ┌──────┐  ┌──────┐  ┌──────┐            │
   │  │Region│  │Region│  │Region│            │
   │  │(Store)│  │(Store)│  │(Store)│           │
   │  └──┬───┘  └──┬───┘  └──┬───┘            │
   │     │HFile    │HFile    │HFile            │
   │     │MemStore │MemStore │MemStore         │
   │     │WAL      │WAL      │WAL              │
   └─────┼─────────┼─────────┼─────────────────┘
         ↓         ↓         ↓
         HDFS (3 副本存储)
```

### 2. 关键组件

| 组件 | 职责 |
|------|------|
| **HMaster** | Region 分配、负载均衡、DDL |
| **RegionServer** | 读写请求、Store 管理 |
| **MemStore** | 内存写入缓冲（写满后 flush 到 HFile） |
| **HFile** | 实际存储文件（类 SSTable） |
| **WAL** | Write-Ahead Log，崩溃恢复 |
| **ZooKeeper** | 选主、心跳、配置 |

### 3. 写流程

1. Client 写 WAL（顺序写）
2. 写入 MemStore（内存）
3. MemStore 满后异步 flush 到 HFile
4. 周期性 Compaction（合并小 HFile）

**特点**：
- **LSM Tree**（Log-Structured Merge Tree）：顺序写、随机读
- **写入极快**（只追加），**读取需 Bloom Filter 加速**

> **适用场景**：超大规模（PB 级）写入场景，如阿里/字节的日志平台、用户行为埋点存储。与 Cassandra 相比，HBase 强一致但运维依赖 Hadoop 生态，复杂度更高。

---

## 十一、NewSQL（融合 SQL + NoSQL）

NewSQL 兼具关系型数据库的 ACID 与 NoSQL 的水平扩展能力。

| 产品 | 架构 | 特点 |
|------|------|------|
| **TiDB** | 兼容 MySQL 协议，计算存储分离 | HTAP（同时支持 OLTP + OLAP） |
| **CockroachDB** | 兼容 PostgreSQL 协议，Shared-nothing | 强一致、全球部署 |
| **Google Spanner** | 全球分布式，Paxos + TrueTime | 外部一致时钟 |
| **YugabyteDB** | 兼容 PostgreSQL 协议，DocDB 存储 | 多模（KV/SQL/CQL） |
| **PolarDB（阿里）** | 存储计算分离，RDMA 网络 | 阿里云原生 |

### 何时选择 NewSQL

- 单库 MySQL/PostgreSQL 容量/性能到达瓶颈
- 需要强 ACID 事务 + 水平扩展
- 不想放弃 SQL 编程范式
- 业务量在 100TB 以下（超过仍需考虑 HBase/Cassandra）

---

## 十二、CAP 定理与 NoSQL 选型

CAP 定理由 Eric Brewer（2000 年）提出，分布式系统**最多同时满足**以下 3 个中的 **2 个**：

| 特性 | 含义 |
|------|------|
| **C**onsistency | 一致性：所有节点同一时刻看到同一数据 |
| **A**vailability | 可用性：每个请求都得到响应（非错误） |
| **P**artition tolerance | 分区容错：节点间网络断开仍能继续工作 |

> **实践**：分布式系统**P 必须满足**（网络不可靠），因此只能在 **C 和 A 之间取舍**。

### NoSQL 的取舍

| 数据库 | 倾向 | 原因 |
|--------|------|------|
| **Redis** | AP | 高可用优先，接受最终一致 |
| **Cassandra** | AP（可调） | 可配成 CP（QUORUM） |
| **MongoDB** | CP（默认） | 副本集默认强一致 |
| **HBase** | CP | 基于 HDFS+ZooKeeper 强一致 |
| **ZooKeeper/etcd** | CP | 协调服务优先一致 |
| **Eureka** | AP | 服务发现优先可用 |

---

## 🔗 相关章节

- [数据库基础知识](../01-fundamentals/README.md) — 关系型 vs 非关系型基础
- [SQL](../02-sql/README.md) — SQL 查询范式
- [Redis](../07-redis/README.md) — Redis 作为键值型 NoSQL
- [系统设计 · 分布式缓存](../../04.system-design/02-distributed/distributed-cache/README.md) — 缓存架构深入

---

## 📊 本节统计

- **leaf README 数**：5（本索引页 + mongodb/ + cassandra/ + elasticsearch/ + neo4j/）
- **本节主题数**：12（4 大优势、5 种类型、SQL vs NoSQL、选型指南、MongoDB、Cassandra、HBase、ES、Neo4j、NewSQL、CAP、子专题导航）
- **frontmatter 状态**：✅ 已对齐 CONTRIBUTING §12 标准（summary ≤ 80 字 / type=index）

---

## 📖 参考资料

- [NoSQL Databases - Wikipedia](https://en.wikipedia.org/wiki/NoSQL)
- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [Cassandra Documentation](https://cassandra.apache.org/doc/latest/)
- [HBase Reference Guide](https://hbase.apache.org/book.html)
- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Neo4j Developer Guides](https://neo4j.com/developer/)

---

← [返回 03.database 主模块](../README.md)
