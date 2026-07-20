<!--
module:
  parent: database/nosql
  slug: database/nosql/neo4j
  type: article
  category: 主模块子文章
  summary: Neo4j 图数据库：节点/关系/属性模型、Cypher 查询语言、N 度关系毫秒级查询
-->

# Neo4j 图数据库

> Neo4j 是最流行的原生图数据库，采用属性图（Property Graph）模型，节点和关系均可携带属性，使用声明式 Cypher 查询语言。在关系密集型数据（社交网络、知识图谱、欺诈检测、推荐系统）上，N 度关联查询始终保持毫秒级响应，远超关系型数据库的 N 次 JOIN。

---

## 📚 核心内容

| 主题 | 关键点 |
|------|--------|
| 核心概念 | Node / Relationship / Property / Label |
| Cypher 语言 | CREATE / MATCH / MERGE / DELETE |
| 原生图存储 | 指针直连，免 JOIN，O(1) 遍历 |
| GDS 图算法 | PageRank / 社区检测 / 最短路径 |
| APOC 工具库 | 数据导入、树操作、批量处理 |
| 典型场景 | 社交网络 / 知识图谱 / 反欺诈 / 推荐系统 |

---

## 一、核心概念

| 概念 | 说明 | 示例 |
|------|------|------|
| **节点（Node）** | 实体，用 `()` 表示 | `(p:Person {name: '张三'})` |
| **关系（Relationship）** | 节点间的有向连接，用 `-[r]->` 表示 | `-[:FRIEND {since: 2020}]->` |
| **属性（Property）** | 键值对，附加在节点或关系上 | `{name: '张三', age: 30}` |
| **标签（Label）** | 节点的分类标记，用 `:Label` 表示 | `:Person`、`:Movie`、`:Company` |
| **关系类型** | 关系的语义标识 | `:FRIEND`、`:ACTED_IN`、`:TRANSFERRED_TO` |

> **属性图 vs RDF 三元组**：Neo4j 用属性图（LPG），节点和关系均可带属性；RDF 只能描述"主语-谓语-宾语"三元组，属性需额外建模。LPG 更直观，RDF 更适合语义网标准。

---

## 二、Cypher 查询语言

Cypher 是 Neo4j 的声明式查询语言，语法接近 ASCII 图形：

```cypher
// 创建节点和关系
CREATE (a:Person {name: '张三', age: 30})
CREATE (b:Person {name: '李四', age: 25})
CREATE (c:Person {name: '王五', age: 28})
CREATE (a)-[:FRIEND {since: 2020}]->(b)
CREATE (b)-[:FRIEND {since: 2021}]->(c)

// 查询：张三的朋友
MATCH (a:Person {name: '张三'})-[:FRIEND]-(friend)
RETURN friend.name, friend.age

// 查询：2 度关系（朋友的朋友）
MATCH path = (a:Person {name: '张三'})-[:FRIEND*1..2]-(other)
WHERE a <> other  -- 排除自己
RETURN other.name, length(path) AS degree

// MERGE：存在则匹配，不存在则创建（类似 UPSERT）
MERGE (p:Person {name: '赵六'})
ON CREATE SET p.age = 22, p.createdAt = datetime()
ON MATCH SET p.lastSeen = datetime()

// 聚合：统计每个人的朋友数
MATCH (p:Person)-[:FRIEND]-(friend)
RETURN p.name, count(friend) AS friendCount
ORDER BY friendCount DESC
```

**常用 Cypher 关键字**：

| 关键字 | 功能 | SQL 等价 |
|--------|------|---------|
| `MATCH` | 模式匹配 | FROM + WHERE |
| `WHERE` | 过滤条件 | WHERE |
| `RETURN` | 返回结果 | SELECT |
| `CREATE` | 创建节点/关系 | INSERT |
| `MERGE` | 匹配或创建 | UPSERT |
| `SET` | 更新属性 | UPDATE SET |
| `DELETE` / `DETACH DELETE` | 删除节点/关系 | DELETE |
| `WITH` | 中间结果传递（管道） | 子查询 / CTE |
| `CALL` | 调用过程/函数 | 存储过程 |

---

## 三、原生图存储 vs 双数据库

Neo4j 采用**原生图存储**，与"在关系数据库上模拟图"有本质差异：

| 维度 | Neo4j（原生图） | 关系数据库（JOIN 模拟） |
|------|----------------|----------------------|
| 存储结构 | 节点通过指针直连邻居 | 外键 + JOIN 临时关联 |
| N 度遍历 | O(N) 指针跳转，毫秒级 | N 次自连接，指数级恶化 |
| 深度查询（5 度+） | 始终可用 | 5 度 JOIN 通常超时 |
| 动态关系 | 直接加边 | 需改表结构 |
| 事务 | 完整 ACID | 完整 ACID |

```text
关系数据库 5 度查询：
SELECT ... FROM users u1
JOIN friends f1 ON u1.id = f1.user_id
JOIN users u2 ON f1.friend_id = u2.id
JOIN friends f2 ON u2.id = f2.user_id
... （5 次 JOIN，行数爆炸）

Neo4j 5 度查询：
MATCH path = (a:Person {name:'张三'})-[:FRIEND*5]-(other)
RETURN other
// 指针直连，遍历即得
```

---

## 四、GDS 图数据科学库（Graph Data Science）

Neo4j GDS 提供 60+ 图算法，直接在数据库内执行，无需导出数据：

| 算法类别 | 代表算法 | 用途 |
|---------|---------|------|
| **中心性** | PageRank、Betweenness | 找出最有影响力的节点 |
| **社区检测** | Louvain、Label Propagation | 发现社群/团伙 |
| **路径** | Dijkstra、A*、Yen's k-shortest | 最短路径、最优路由 |
| **相似度** | Jaccard、Cosine、Node2Vec | 推荐系统、去重 |
| **链路预测** | Adamic-Adar、Common Neighbors | 好友推荐、关系补全 |

```cypher
// 示例：PageRank 找出社交网络中影响力最大的用户
CALL gds.pageRank.stream('social-graph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC LIMIT 10

// 社区检测（Louvain）
CALL gds.louvain.stream('social-graph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name AS name, communityId
ORDER BY communityId
```

---

## 五、APOC 工具库

APOC（Awesome Procedures on Cypher）是 Neo4j 官方扩展库，提供 300+ 实用函数：

| 类别 | 示例 | 用途 |
|------|------|------|
| **数据导入** | `apoc.load.csv`、`apoc.load.jdbc` | 从 CSV/SQL 批量导入 |
| **树操作** | `apoc.convert.toTree`、`apoc.path.expand` | 层级结构查询 |
| **批量处理** | `apoc.periodic.iterate` | 百万级数据批量更新 |
| **图投影** | `apoc.create.vNode`、`apoc.create.vRelationship` | 虚拟节点（不持久化） |
| **日期/字符串** | `apoc.date.format`、`apoc.text.regexGroups` | 工具函数 |

```cypher
// 批量更新（每批 10000 条，避免内存溢出）
CALL apoc.periodic.iterate(
    'MATCH (p:Person) WHERE p.city IS NULL RETURN p',
    'SET p.city = "未知"',
    { batchSize: 10000, parallel: true }
)
```

---

## 六、典型应用场景

### 6.1 社交网络

- **好友推荐**：共同好友数（`Common Neighbors`）+ 相似度排序
- **N 度人脉**：`MATCH path = (a)-[:FRIEND*1..6]-(b)`（六度分隔验证）
- **社群发现**：Louvain 算法自动识别圈子

### 6.2 知识图谱

- **实体关系推理**：`(:公司)-[:控股]->(:子公司)-[:法人]->(:Person)`
- **路径推理**：两个实体之间的关联路径
- **RAG 增强**：知识图谱 + LLM 结合（Graph RAG），提供结构化上下文

### 6.3 反欺诈（金融风控）

```cypher
// 检测循环转账（可疑洗钱链路）
MATCH cycle = (a:Account)-[:TRANSFERRED_TO*2..5]->(a)
WHERE ALL(r IN relationships(cycle) WHERE r.amount > 10000)
RETURN cycle
LIMIT 100
```

- **异常关联检测**：多个账户共用同一设备/手机号/地址
- **团伙识别**：社区检测算法找出紧密关联账户群

### 6.4 推荐系统

- **基于路径的推荐**：用户 → 购买 → 商品 ← 购买 ← 相似用户 → 购买 → 推荐商品
- **协同过滤图化**：Jaccard / Cosine 相似度 + kNN

---

## 七、生产部署注意

| 主题 | 建议 |
|------|------|
| **内存规划** | 图数据需全部加载到内存（Page Cache），数据量 ≈ 内存需求 |
| **集群** | Neo4j Enterprise 支持 Fabric（多数据库联邦）和 Causal Cluster（读写分离） |
| **索引** | 必须为高频查询字段建索引（`CREATE INDEX FOR (p:Person) ON (p.name)`） |
| **数据建模** | 避免超级节点（Degree > 10000），需拆分或引入中间节点 |
| **事务** | 短事务优先，大批量写入用 `apoc.periodic.iterate` 分批 |

---

## 🔗 相关章节

- [NoSQL 总览](../README.md) — NoSQL 类型对比与选型指南
- [MongoDB](../mongodb/README.md) — 文档型，关系查询弱
- [系统设计 · 知识图谱](../../../04.system-design/) — Graph RAG 架构

---

← [返回 NoSQL 数据库](../README.md)

## Frontmatter 类型与定位

**当前 frontmatter**：
```yaml
module:
  parent: database
  slug: database/nosql/neo4j
  type: article
  ...
```

定位句（第 12 行）：**Neo4j 是原生图数据库，使用 Cypher 查询语言——核心是节点-关系-属性模型而非表-行-列模型。**（75 字内）

> **P1 修正**：原定位句 ~95 字略冗，已压缩至 75 字。
