<!--
question:
  id: 04.system-design-product-search
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [04.system-design, 搜索, Elasticsearch, 倒排索引, BM25, 系统设计]
-->

# 设计一个商品搜索系统 —— 从 DB LIKE 到 Elasticsearch 完整方案

> 一句话定位：**后端 / 架构面试经典系统设计题**。考察的不是"Elasticsearch 怎么用"，而是 **架构演进判断** + **搜索引擎原理** + **排序策略设计** + **数据一致性**。深度实战见 [主模块深度章节](../../../../04.system-design/04-high-performance/product-search/README.md)。

> **系列定位**：高频系统设计题（社招必考）。配套兄弟题：[缓存一致性](../cache-consistency/README.md)、[分布式锁](../distributed-lock/README.md)。

---

⭐⭐⭐⭐ 深度级别（高级工程师 / 架构师级）
📚 前置知识：Elasticsearch 基础 / 倒排索引 / MySQL binlog / 缓存设计

---

## 引子：面试经典开场

面试官："设计一个商品搜索系统，100 万 SKU，支持关键词搜索 + 品牌/价格筛选 + 排序，QPS 1 万。"

大多数人答："用 Elasticsearch。"

面试官追问：
1. "ES 的倒排索引是怎么工作的？"
2. "BM25 和 TF-IDF 有什么区别？"
3. "商品数据从 MySQL 到 ES 怎么保证同步一致性？"
4. "如果只要相关性排序不够，怎么混入销量、评分等业务信号？"

大多数人卡在追问上。**这道题考察的不是"知道用 ES"，而是"理解 ES 底层原理 + 排序策略 + 数据同步"。**

---

## 一、核心原理

### 1.1 架构选型决策树

```
搜索需求？
├─ SKU < 1 万 + QPS < 100 → DB LIKE（MVP 够用）
├─ SKU 1 万~50 万 + QPS < 5000 → 单节点 ES
├─ SKU 50 万+ + QPS 1 万+ → ES 集群（分片 + 副本 + 缓存）
└─ SKU 千万+ + 个性化 → ES 集群 + ML 精排 + 向量召回
```

### 1.2 倒排索引（Inverted Index）

**正排索引**：doc → terms（已知文档查内容）
**倒排索引**：term → docs（已知关键词查文档）

```
商品标题："Nike 红色运动鞋"
    ↓ IK 分词
Terms: [nike, 红色, 运动鞋]
    ↓ 写入倒排索引
nike     → [doc1, doc5, ...]
红色     → [doc1, doc3, ...]
运动鞋   → [doc1, doc2, doc15, ...]
```

搜索"运动鞋"时，直接查 posting list → O(1)，不需要遍历所有文档。

### 1.3 BM25 vs TF-IDF

| 特性 | TF-IDF | BM25（ES 5.x+ 默认） |
|------|--------|---------------------|
| 词频处理 | 线性增长 | **饱和效应**（k1 参数控制） |
| 文档长度 | 简单归一化 | **参数化归一化**（b 参数控制） |
| 直觉符合度 | 差（100 次 = 10 倍得分） | 好（5 次以后几乎不加分） |

**BM25 公式**（简化版）：
```
score(D, Q) = Σ IDF(qi) × f(qi,D) × (k1+1) / [f(qi,D) + k1 × (1 - b + b × |D|/avgdl)]
```

- **k1 = 1.2**：词频饱和速度
- **b = 0.75**：文档长度影响程度

---

## 二、7 道精选面试题

### Q1：为什么不能直接用 DB LIKE 做商品搜索？

**答**：4 个硬伤——

1. **全表扫描**：`LIKE '%运动鞋%'` 无法走索引，100 万行要逐行扫描
2. **无法分词**："红色运动鞋" 搜不到"运动鞋 红色"（顺序依赖）
3. **无相关性排序**：只能按 sales/price 等硬字段排序，无法按"相关性"排序
4. **不支持多维筛选**：品牌+价格+颜色的组合筛选性能急剧下降

### Q2：IK 分词器的 ik_smart 和 ik_max_word 有什么区别？什么时候用哪个？

**答**：

| 模式 | 分词结果（"红色运动鞋"） | 使用时机 |
|------|------------------------|---------|
| `ik_smart` | [红色, 运动鞋] | **搜索时**（精确匹配） |
| `ik_max_word` | [红色, 运动, 运动鞋, 动鞋] | **索引时**（最大召回） |

**原理**：索引时多切词（"运动"和"运动鞋"都入索引），搜索时智能切词（"红色运动鞋" → "红色 + 运动鞋"），兼顾召回率和准确率。

### Q3：商品数据从 MySQL 同步到 ES，怎么保证一致性？

**答**：3 层保障——

1. **实时同步**：Canal 监听 MySQL binlog → RocketMQ → ES Consumer（延迟 < 5 秒）
2. **顺序保证**：同一商品的变更用 `product_id` 作为 MQ 分区 key，保证顺序消费
3. **补偿机制**：定时任务全量对比（MySQL count vs ES doc count），差异自动修复

**关键细节**：
- ES 写入用 `version` 字段防止旧数据覆盖新数据（乐观锁）
- 消费失败的消息进死信队列，人工介入
- 监控 binlog 到 ES 的延迟（P99 < 5 秒），超时告警

### Q4：搜索结果排序只用 BM25 够吗？怎么混入业务信号？

**答**：不够。纯 BM25 会让"销量 0 但标题高度匹配的新品"排第一，用户体验差。

**混合排序方案**：

```
最终得分 = BM25 × 0.4 + log(sales+1) × 0.3 + rating × 0.15 + freshness × 0.1 + promo × 0.05
```

ES 实现用 `function_score` query：
- `field_value_factor`：销量、评分等业务字段
- `gauss` / `exp`：时间衰减（新品加分）
- `weight`：促销标记加权

### Q5：Faceted Search（多维筛选面板）怎么实现？

**答**：ES 的 **聚合（Aggregation）** API——

```json
{
  "query": { "match": { "title": "运动鞋" } },
  "aggs": {
    "brands": { "terms": { "field": "brand", "size": 20 } },
    "prices": { "range": { "field": "price", "ranges": [{"to":200},{"from":200,"to":500},{"from":500}] } }
  }
}
```

**关键**：商品属性（颜色、尺码）用 `nested` 类型，避免属性交叉匹配错误（"红色包 + 42 码鞋" ≠ "红色 42 码鞋"）。

### Q6：搜索建议（Autocomplete）怎么做到毫秒级响应？

**答**：ES **Completion Suggester**——

- 底层用 **FST**（Finite State Transducer）数据结构，全部在内存中
- 前缀匹配复杂度 O(len)，与文档数量无关
- 延迟 < 1ms

```json
"suggest": { "type": "completion", "analyzer": "ik_smart" }
```

**备选方案**：Redis Sorted Set（适合自定义排序权重）。

### Q7：大促期间搜索 QPS 从 1 万涨到 5 万，怎么应对？

**答**：4 层防御——

1. **Query 缓存**：热门 query（"运动鞋""连衣裙"）结果缓存到 Redis，TTL 30 秒。50% 请求命中缓存
2. **ES 副本扩容**：临时增加副本数（1 → 3），读吞吐线性增长
3. **降级策略**：关闭精排层（ML 模型），只用 BM25 + function_score 粗排
4. **限流**：搜索 API 令牌桶限流，超出返回缓存结果或默认推荐

---

## 三、常见陷阱

**陷阱 1：索引时和搜索时用同一个分词器**

```json
// ❌ 都用 ik_smart → 召回率低
"title": { "type": "text", "analyzer": "ik_smart" }

// ✅ 索引最细 + 搜索智能
"title": { "type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart" }
```

**陷阱 2：商品属性用 flat 字段而非 nested**

```json
// ❌ flat → "红色包" + "42码鞋" 会匹配 "红色 42码 鞋"
"attributes": { "type": "object" }

// ✅ nested → 精确匹配每个属性的 key-value 对
"attributes": { "type": "nested" }
```

**陷阱 3：数据同步不做幂等**

```
// ❌ 消息重试导致 ES 写入旧数据
// ✅ 用 ES 的 version 或 external version 做乐观锁
```

---

## 四、面试话术（30 秒版）

> "商品搜索系统核心是 ES 倒排索引 + IK 中文分词 + BM25 相关性排序。
>
> 架构上，MySQL 做主存储，Canal 监听 binlog 通过 MQ 实时同步到 ES。搜索走 ES 集群，热门 query 缓存到 Redis。
>
> 排序用多阶段管道：BM25 召回 1000 条 → 业务信号混合粗排到 100 条 → ML 精排出 20 条。
>
> 多维筛选用 ES 聚合 API，商品属性用 nested 类型避免交叉匹配。
>
> 一致性靠 Canal + MQ 顺序消费 + ES version 乐观锁 + 定时全量对比补偿。"

### 90 秒版（展开）

> "商品搜索我会分五层讲。
>
> **存储与同步**：MySQL 是唯一真源，Canal 监听 binlog → RocketMQ → ES Consumer 实时同步，延迟控制在秒级；MQ 按商品 ID 分区保证同一商品的更新顺序消费。
>
> **检索**：ES 倒排索引 + IK 中文分词解决"运动鞋"能命中"男士运动跑鞋"；相关性用 BM25 打底，商品属性用 nested 类型避免"红色 + XL"跨商品误匹配。
>
> **排序**：多阶段管道——BM25 召回 1000 条 → 融合销量/CTR/库存等业务信号粗排到 100 条 → ML 模型精排出 20 条，兼顾相关性与转化。
>
> **性能**：热门 query 结果缓存 Redis（TTL 30s），Autocomplete 用前缀索引/RUM 做到毫秒级；大促用限流保护 ES 集群。
>
> **一致性兜底**：ES version 乐观锁防乱序覆盖，再加定时全量对比补偿漏消费的数据。整体是'实时同步为主 + 定时对账为辅'。"

---

## 五、交叉引用

- **深度实战**：[商品搜索系统设计](../../../../04.system-design/04-high-performance/product-search/README.md) — 架构演进 + 源码级实现
- 🆕 **相关面试题**：[短链系统设计](../../url-shortener/README.md) — Base62 + 发号器 + 302 重定向 + 缓存
- **相关面试题**：[缓存一致性](../cache-consistency/README.md) — 搜索缓存失效策略
- **相关面试题**：[分布式锁](../distributed-lock/README.md) — 并发写入保护
- **相关面试题**：[限流算法](../rate-limiting/README.md) — 大促期间搜索限流
- **主模块**：[`04.system-design`](../../../../04.system-design/) — 系统设计知识体系

## 相关章节

- 深度阅读：[`04.system-design`](../../../../04.system-design/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · product-search](README.md)
