# NoSQL 数据库

NoSQL（Not Only SQL）泛指非关系型数据库，天生支持分布式，适用于大规模数据存储和高并发场景。

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

**MongoDB 4.0+ 支持多文档 ACID 事务**，但与 MySQL 的事务能力仍有差距（性能开销更大）。
