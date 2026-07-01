<!--
module:
  parent: database
  slug: database/nosql
  type: index
  category: 主模块子文章
  summary: NoSQL 涵盖键值、文档、列存储、图、搜索 5 大类型,天生支持分布式扩展,以最终一致性换取扩展性;NewSQL 融合 SQL + NoSQL 优势。
-->

# NoSQL 数据库

> NoSQL(Not Only SQL)泛指非关系型数据库,涵盖键值、文档、列存储、图、搜索 5 大类型,天生支持分布式扩展,适用于大规模数据存储和高并发场景;但普遍以最终一致性换取扩展性。

> 最后更新: 2026-07-01

---

## 📚 核心内容

| 主题 | 内容 | 关键点 |
|------|------|--------|
| 一、NoSQL 的四大优势 | 灵活 Schema / 水平扩展 / 高性能 / 丰富 API | 适合大规模与高并发 |
| 二、五种 NoSQL 类型 | 键值 / 文档 / 列存储 / 图 / 搜索 | 5 大代表产品对比 |
| 三、SQL vs NoSQL 对比 | 数据模型 / Schema / 事务 / 扩展 / 一致性 | SQL 强一致,NoSQL 多最终一致 |
| 四、选型指南 | 场景 → 类型 → 产品 | 混合使用 Polyglot Persistence |
| 五、MongoDB 简要介绍 | BSON / Collection / `$lookup` | 4.0+ 部分支持多文档 ACID |
| 六、MongoDB 深入 | 副本集 / 分片集群 / Write/Read Concern / 索引 / 聚合管道 | 副本集 + 分片是高可用与扩展基础 |
| 七、Cassandra 数据模型 | Keyspace / Partition Key / Clustering Key / Wide Row | Query-first Design |
| 八、HBase 架构 | HMaster / RegionServer / MemStore / HFile / WAL | LSM Tree 顺序写 |
| 九、Elasticsearch 倒排索引 | 正排 vs 倒排 / 与 B+ 树对比 | BM25 相关度评分 |
| 十、Neo4j 与图查询 | 节点 / 关系 / 属性 / 标签 + Cypher | N 度查询毫秒级 |
| 十一、NewSQL | TiDB / CockroachDB / Spanner / PolarDB | 兼具 ACID + 水平扩展 |
| 十二、CAP 定理与 NoSQL 选型 | P 必须满足,C/A 取舍 | MongoDB CP,Redis AP |

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

## 五、MongoDB 简要介绍

MongoDB 是最流行的文档型数据库，使用 BSON（Binary JSON）格式存储数据。

| 概念 | SQL 类比 | MongoDB |
|------|---------|---------|
| 数据库 | Database | Database |
| 表 | Table | Collection |
| 行 | Row | Document |
| 列 | Column | Field |
| 主键 | Primary Key | `_id` |
| JOIN | JOIN | `$lookup` |

```javascript
// 插入文档
db.users.insertOne({
    name: "张三",
    age: 25,
    address: { city: "北京", zip: "100000" }
});

// 查询
db.users.find({ age: { $gt: 20 } }).sort({ age: -1 }).limit(10);
```

**MongoDB 4.0+ 支持多文档 ACID 事务**,但与 MySQL 的事务能力仍有差距(性能开销更大)。

---

## 六、MongoDB 深入

### 1. 副本集(Replica Set)

MongoDB 副本集提供**高可用 + 数据冗余**,由 1 个 Primary 和多个 Secondary 组成。

```
┌──────────┐
│  Primary │  ← 所有写操作
└────┬─────┘
     │ 异步复制 oplog
     ├──→ Secondary 1 (可读,默认)
     ├──→ Secondary 2 (可读,默认)
     └──→ Arbiter (仅投票,不存数据)
```

- **自动故障转移**:Primary 宕机时,Secondary 选举新 Primary
- **读写分离**:Secondary 节点可读(需开启 `readPreference`)
- **oplog**:操作日志(类 MySQL binlog),增量同步

### 2. 分片集群(Sharded Cluster)

数据量超过单节点承载(通常 2TB+)时,使用分片。

```
客户端 → mongos(路由) → Config Server(元数据)
                              ↓
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
          Shard 1         Shard 2         Shard 3
        (副本集)         (副本集)         (副本集)
```

- **分片键**(Shard Key):必须包含在唯一索引中
- **Chunk**:默认 64MB,自动分裂与均衡
- **Hash 分片 vs Range 分片**:Hash 均匀但范围查询需扫所有分片

### 3. 写关注(Write Concern)与读关注(Read Concern)

| 级别 | 写关注 | 读关注 |
|------|--------|--------|
| `{w: 0}` | 不确认 | - |
| `{w: 1}` | Primary 写入即返回 | - |
| `{w: "majority"}` | **多数节点确认**(推荐) | - |
| `{level: "majority"}` | - | 读已确认的多数节点数据 |
| `{level: "linearizable"}` | - | 读最新数据(强一致) |

### 4. 索引类型

| 索引 | 用途 |
|------|------|
| **单字段** | `{name: 1}` |
| **复合** | `{name: 1, age: -1}`(顺序重要) |
| **多键** | 自动对数组字段建立 |
| **地理空间** | `2dsphere`(球面)、`2d`(平面) |
| **文本** | `{content: "text"}` |
| **Hash** | `{name: "hashed"}`(分片键用) |
| **TTL** | `{createdAt: 1}, expireAfterSeconds: 3600` |

### 5. 聚合管道(Aggregation Pipeline)

```javascript
// 各年龄段用户数 + 平均消费
db.users.aggregate([
    { $match: { status: 'active' } },
    { $group: {
        _id: { $switch: {
            branches: [
                { case: { $lt: ['$age', 18] }, then: '未成年' },
                { case: { $lt: ['$age', 30] }, then: '青年' }
            ],
            default: '其他'
        }},
        count: { $sum: 1 },
        avgSpending: { $avg: '$spending' }
    }},
    { $sort: { count: -1 } }
]);
```

---

## 七、Cassandra 数据模型

### 1. 核心概念

| 概念 | 类比 SQL | 说明 |
|------|---------|------|
| **Keyspace** | Database | 命名空间,定义复制策略 |
| **Column Family (Table)** | Table | 列族 |
| **Partition Key** | 主键 | 决定数据分布到哪个节点 |
| **Clustering Key** | - | 决定分区内排序 |
| **Wide Row** | 多个独立行的合并 | 一行可有上百万列 |

### 2. 数据模型示例

```cql
CREATE TABLE user_activity (
    user_id    UUID,        -- Partition Key
    year_month text,        -- Clustering Key (按月分簇)
    day        int,
    event      text,
    timestamp  timestamp,
    PRIMARY KEY ((user_id, year_month), day, timestamp)
) WITH CLUSTERING ORDER BY (day DESC, timestamp DESC);
```

**查询模式**:
- ✅ `WHERE user_id = ? AND year_month = ?`(分区查询,快)
- ❌ `WHERE year_month = ?`(全分区扫描,**Cassandra 禁止**)

> **Cassandra 设计原则**:**基于查询模式反推表结构**(Query-first Design),而非先建模后查询。

### 3. 一致性级别(可调)

| Level | 含义 | 性能 |
|-------|------|------|
| `ONE` | 1 个副本确认 | 最高 |
| `QUORUM` | 多数副本确认 | 中等 |
| `ALL` | 所有副本确认 | 最低 |
| `LOCAL_QUORUM` | 同机房多数 | 推荐(多机房) |

> **可调一致性是 NoSQL 的核心优势**:业务可按场景选 ONE(性能) 或 QUORUM(一致)。

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
| **MemStore** | 内存写入缓冲(写满后 flush 到 HFile) |
| **HFile** | 实际存储文件(类 SSTable) |
| **WAL** | Write-Ahead Log,崩溃恢复 |
| **ZooKeeper** | 选主、心跳、配置 |

### 3. 写流程

1. Client 写 WAL(顺序写)
2. 写入 MemStore(内存)
3. MemStore 满后异步 flush 到 HFile
4. 周期性 Compaction(合并小 HFile)

**特点**:
- **LSM Tree**(Log-Structured Merge Tree):顺序写、随机读
- **写入极快**(只追加),**读取需 Bloom Filter 加速**

---

## 九、Elasticsearch 倒排索引

### 1. 正排 vs 倒排

| 类型 | 结构 | 用途 |
|------|------|------|
| **正排索引** | 文档 ID → 词条列表 | 通过 ID 找内容(类主键) |
| **倒排索引** | 词条 → 文档 ID 列表 | 通过词条找文档(全文搜索) |

### 2. 倒排索引结构

```
词项     |  文档 ID 列表(文档频率)
--------+--------------------
"redis" |  [doc1, doc3, doc7, doc15] (df=4)
"mysql" |  [doc2, doc3] (df=2)
"index" |  [doc1, doc4, doc5, doc7, doc8, doc15] (df=6)
```

每个词项对应一个**倒排列表**(Posting List),按文档 ID 排序。

### 3. 与 B+ 树对比

| 维度 | B+ 树(关系数据库) | 倒排索引(ES) |
|------|------------------|-------------|
| 适用查询 | 等值、范围、前缀 | 全文、模糊、相关度 |
| 写入 | 随机 I/O | 顺序 I/O(LSM) |
| 空间 | 中等 | 较大(词项字典) |
| 排序 | 字段值 | 相关度评分(TF-IDF/BM25) |

### 4. 经典应用

- 全文搜索:电商商品、博客文章
- 日志分析:ELK(Elasticsearch + Logstash + Kibana)
- 向量检索:ES 8.0+ 支持 `dense_vector` 字段 + kNN 查询

---

## 十、Neo4j 与图查询

### 1. 核心概念

| 概念 | 说明 |
|------|------|
| **节点(Node)** | 实体(如人、电影) |
| **关系(Relationship)** | 节点间的有向连接(如"朋友"、"出演") |
| **属性(Property)** | 键值对,可附加在节点或关系 |
| **标签(Label)** | 节点的分类(如 `:Person`、`:Movie`) |

### 2. Cypher 查询语言

```cypher
// 创建
CREATE (a:Person {name: '张三', age: 30})
CREATE (b:Person {name: '李四', age: 25})
CREATE (a)-[:FRIEND {since: 2020}]->(b)

// 查询:张三的朋友及朋友的朋友(2 度关系)
MATCH (a:Person {name: '张三'})-[:FRIEND*1..2]-(friend)
RETURN friend.name, friend.age
```

### 3. 适用场景

- 社交网络(好友推荐、N 度关系)
- 知识图谱(实体关系推理)
- 反欺诈(发现异常关联)
- 推荐系统(基于关系路径的推荐)

> **关系数据库建模 N 度关系**需要 N 次自连接,性能急剧下降;图数据库 N 度查询始终是毫秒级。

---

## 十一、NewSQL(融合 SQL + NoSQL)

NewSQL 兼具关系型数据库的 ACID 与 NoSQL 的水平扩展能力。

| 产品 | 架构 | 特点 |
|------|------|------|
| **TiDB** | 兼容 MySQL 协议,计算存储分离 | HTAP(同时支持 OLTP + OLAP) |
| **CockroachDB** | 兼容 PostgreSQL 协议,Shared-nothing | 强一致、全球部署 |
| **Google Spanner** | 全球分布式,Paxos + TrueTime | 外部一致时钟 |
| **YugabyteDB** | 兼容 PostgreSQL 协议,DocDB 存储 | 多模(KV/SQL/CQL) |
| **PolarDB(阿里)** | 存储计算分离,RDMA 网络 | 阿里云原生 |

### 何时选择 NewSQL

- 单库 MySQL/PostgreSQL 容量/性能到达瓶颈
- 需要强 ACID 事务 + 水平扩展
- 不想放弃 SQL 编程范式
- 业务量在 100TB 以下(超过仍需考虑 HBase/Cassandra)

---

## 十二、CAP 定理与 NoSQL 选型

CAP 定理由 Eric Brewer(2000 年)提出,分布式系统**最多同时满足**以下 3 个中的 **2 个**:

| 特性 | 含义 |
|------|------|
| **C**onsistency | 一致性:所有节点同一时刻看到同一数据 |
| **A**vailability | 可用性:每个请求都得到响应(非错误) |
| **P**artition tolerance | 分区容错:节点间网络断开仍能继续工作 |

> **实践**:分布式系统**P 必须满足**(网络不可靠),因此只能在 **C 和 A 之间取舍**。

### NoSQL 的取舍

| 数据库 | 倾向 | 原因 |
|--------|------|------|
| **Redis** | AP | 高可用优先,接受最终一致 |
| **Cassandra** | AP(可调) | 可配成 CP(QUORUM) |
| **MongoDB** | CP(默认) | 副本集默认强一致 |
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

- **leaf README 数**：1（本文即为分类 leaf，单 README 长文聚合 12 主题）
- **本节主题数**：12（4 大优势、5 种类型、SQL vs NoSQL、选型指南、MongoDB 简要、MongoDB 深入、Cassandra、HBase、ES、Neo4j、NewSQL、CAP）
- **frontmatter 状态**：✅ 已对齐 CONTRIBUTING §12 标准（summary ≤ 80 字 / type=index）
- **统计口径**：本目录无嵌套子目录，所有内容聚合在本 README；最后更新 2026-07-01

---

## 📖 参考资料

- [NoSQL Databases - Wikipedia](https://en.wikipedia.org/wiki/NoSQL)
- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [Cassandra Documentation](https://cassandra.apache.org/doc/latest/)
- [HBase Reference Guide](https://hbase.apache.org/book.html)
- [Neo4j Developer Guides](https://neo4j.com/developer/)

---

← [返回 03.database 主模块](../README.md)