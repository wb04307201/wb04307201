<!--
question:
  id: 03.database-nosql
  topic: 03.database
  difficulty: ⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [03.database, SQL, nosql]
-->

# NoSQL — 咬文嚼字

> NoSQL 数据库面试细节深挖。聚焦那些"看起来都懂、但说不清楚就会丢分"的问题。
>
> 与关系型数据库不同，NoSQL 的核心在于**数据模型的选择**：Key-Value 追求极致读写，Document 追求灵活 Schema，Column-Family 追求海量写入与压缩，Graph 追求关系遍历。面试常考的不只是"用什么"，更是"为什么选它"。

---

## 文章导航

| 分类 | 核心话题 | 入口 |
|------|---------|------|
| **Key-Value** | Redis 搜索、数据结构底层 | [key-value/](key-value/README.md) |

### 本板块文章清单

| 主题 | 核心问题 | 难度 |
|------|---------|:----:|
| [Redis 搜索能力](key-value/redis/search/README.md) | Redis 如何做全文搜索？RediSearch 模块原理 | ⭐⭐⭐ |

---

## 知识地图

```
NoSQL
├── Key-Value        ← Redis、Memcached、DynamoDB
├── Document         ← MongoDB、Couchbase
├── Column-Family    ← Cassandra、HBase
└── Graph            ← Neo4j、JanusGraph
```

## NoSQL vs RDBMS 速查

| 维度 | RDBMS | NoSQL |
|------|-------|-------|
| Schema | 固定、强约束 | 灵活、Schema-free 或弱约束 |
| 扩展方式 | 纵向（Scale-Up） | 横向（Scale-Out） |
| 事务 | 强一致性（ACID） | 最终一致性（BASE），部分支持 ACID |
| 查询语言 | SQL（标准化） | 各厂商自定义 API |
| 适用场景 | 金融、订单、强一致业务 | 缓存、会话、日志、内容管理、推荐 |

## 相关章节

- 返回：[`03.database 总览`](../README.md)
- 主模块：[`03.database/08-nosql`](../../../03.database/08-nosql/README.md) — NoSQL 知识体系
- 咬文嚼字：[`关系型数据库`](../relational-database/README.md) — RDBMS 细节深挖
