<!--
module:
  parent: system-design/product-search
  slug: system-design/04-high-performance/product-search/01-architecture
  type: topic
  category: 系统架构
  summary: 商品搜索 3 阶段架构演进（DB LIKE → 单节点 ES → ES 集群 + 缓存）+ 5 大组件
-->

# 商品搜索系统架构 · 3 阶段演进

> **一句话**：商品搜索架构 = **搜索引擎 + 分词器 + 排序管道 + 数据同步 + 缓存层**，从 DB LIKE 的 100 QPS 到 ES 集群的 5 万 QPS，需要 3 阶段演进。

← [返回: product-search 总目录](README.md)

---

## 1. 阶段 1：DB LIKE（< 1 万 SKU）

```text
┌──────────────┐     ┌──────────┐
│   前端/App    │────→│  后端 API  │
└──────────────┘     └────┬─────┘
                          │ SQL
                     ┌────▼─────┐
                     │  MySQL    │
                     │ LIKE '%…%'│
                     └──────────┘
```

**实现**：
```sql
SELECT * FROM products
WHERE title LIKE '%运动鞋%' OR description LIKE '%运动鞋%'
ORDER BY sales DESC
LIMIT 20 OFFSET 0;
```

**瓶颈**：
- 全表扫描：100 万行 × 每行扫描 = O(n)，10 秒+
- 无法分词："红色运动鞋" 无法匹配"运动鞋 红色"
- 无相关性排序：只有 sales / price 等硬排序
- LIKE '%前缀' 无法走索引（`%` 开头导致全扫描）

**适用场景**：SKU < 1 万、QPS < 100 的内部系统或 MVP。

---

## 2. 阶段 2：单节点 Elasticsearch（1 万 ~ 50 万 SKU）

```text
┌──────────┐   ┌───────────┐   ┌─────────────┐
│  前端/App  │──→│ Search API │──→│ Elasticsearch│
└──────────┘   └─────┬─────┘   └──────▲──────┘
                     │                │
                     │  ┌─────────────┤
                     │  │             │
                ┌────▼──▼──┐   ┌─────┴──────┐
                │  MySQL    │──→│ Canal + MQ  │
                │ (主存储)  │   │ (数据同步)   │
                └──────────┘   └────────────┘
```

**5 大组件**：

| 组件 | 职责 | 技术选型 |
|------|------|---------|
| **搜索引擎** | 倒排索引 + 全文检索 | Elasticsearch / OpenSearch |
| **分词器** | 中文分词 + 同义词扩展 | IK Analyzer + 自定义词典 |
| **排序管道** | 多阶段排序（召回→粗排→精排） | ES function_score + 外部 ML 模型 |
| **数据同步** | MySQL → ES 实时同步 | Canal + RocketMQ / Kafka |
| **API 层** | 搜索接口 + query 改写 + 日志 | Spring Boot + ES High Level Client |

**性能指标**：
- 搜索延迟：P99 < 100ms（单节点，10 万 SKU）
- QPS：3000-5000（单节点）
- 数据新鲜度：< 5 秒

**ES 索引设计**：

```json
{
  "mappings": {
    "properties": {
      "product_id": { "type": "keyword" },
      "title": {
        "type": "text",
        "analyzer": "ik_max_word",
        "search_analyzer": "ik_smart",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "description": { "type": "text", "analyzer": "ik_smart" },
      "brand": { "type": "keyword" },
      "category": { "type": "keyword" },
      "price": { "type": "scaled_float", "scaling_factor": 100 },
      "sales": { "type": "integer" },
      "rating": { "type": "float" },
      "attributes": {
        "type": "nested",
        "properties": {
          "key": { "type": "keyword" },
          "value": { "type": "keyword" }
        }
      },
      "created_at": { "type": "date" },
      "status": { "type": "keyword" }
    }
  }
}
```

**关键设计决策**：
- `title` 用 `ik_max_word`（索引时最细粒度分词）+ `ik_smart`（搜索时智能分词），最大化召回率
- `attributes` 用 `nested` 类型，支持多维筛选（颜色=红色 AND 尺码=42）
- `price` 用 `scaled_float` 避免浮点精度问题

---

## 3. 阶段 3：ES 集群 + 缓存 + 降级（50 万 ~ 千万 SKU）

```text
                    ┌────────────┐
                    │    CDN      │ ← 热门搜索结果缓存
                    └─────┬──────┘
                          │
┌──────────┐   ┌─────────▼──────────┐
│  前端/App  │──→│    API Gateway     │
└──────────┘   └─────────┬──────────┘
                         │
                ┌────────▼─────────┐
                │   Search Service  │
                │  ┌─────────────┐ │
                │  │ Query 缓存   │ │ ← Redis，热门 query TTL 30s
                │  │ Query 改写   │ │ ← 同义词 + 纠错 + NLP
                │  └──────┬──────┘ │
                └─────────┼────────┘
                          │
              ┌───────────▼────────────┐
              │    ES 集群（3+ 节点）    │
              │  ┌──────┐  ┌──────┐   │
              │  │分片 1 │  │分片 2 │   │ ← 按品类分片
              │  └──────┘  └──────┘   │
              │  ┌──────┐  ┌──────┐   │
              │  │副本 1 │  │副本 2 │   │ ← 读负载均衡
              │  └──────┘  └──────┘   │
              └───────────▲────────────┘
                          │
┌──────────┐   ┌─────────┴──────────┐
│  MySQL    │──→│ Canal → MQ → 消费者 │ ← 实时数据同步
│ (主存储)  │   │ + 定时全量对比      │ ← 补偿机制
└──────────┘   └────────────────────┘
```

**分片策略**：

| 策略 | 优点 | 缺点 |
|------|------|------|
| **按品类分片** | 跨分片查询少（用户通常搜单一品类） | 品类不均（服装 >> 珠宝） |
| **按 ID 哈希分片** | 分布均匀 | 跨分片查询多 |
| **混合策略** | 热门品类独占分片，冷门合并 | 复杂度高 |

**推荐**：100 万 SKU 以下用 3 分片 + 1 副本（共 6 个 shard）；百万以上按品类路由。

**Query 缓存设计**：

```java
// 缓存 key = normalize(query) + filter_hash
String cacheKey = "search:" + normalize(query) + ":" + hash(filters);
List<Product> cached = redis.get(cacheKey);
if (cached != null) return cached;

// 缓存未命中 → 查 ES
List<Product> result = esClient.search(query, filters, sort);
redis.setex(cacheKey, 30, result);  // TTL 30 秒

// 数据变更 → 异步失效相关缓存
mqConsumer.on("product.update", event -> {
    // 失效该商品相关的所有 query 缓存
    // 实际用 Bloom Filter 或 LRU 策略近似失效
});
```

**降级策略**：

```text
ES 集群健康？
├─ 是 → 正常搜索
├─ 部分分片不可用 → 降级搜索（只查可用分片，结果可能不完整）
└─ 全部不可用 → 回退 DB 搜索（LIKE 查询，加 LIMIT 100 保护）
```

---

## 4. 系列导航

| 文章 | 核心内容 |
|------|---------|
| [总目录](README.md) | 需求分析 + 架构概览 + 面试话术 |
| **本文** | 3 阶段架构演进 + 5 大组件 |
| [倒排索引与分词](02-inverted-index.md) | 倒排索引原理 + IK 分词 + 多维筛选 |
| [排序与相关性](03-ranking.md) | BM25 公式 + 多阶段排序 + 业务信号 |

← [返回: product-search 总目录](README.md)
