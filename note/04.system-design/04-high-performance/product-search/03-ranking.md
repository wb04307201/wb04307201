<!--
module:
  parent: system-design/product-search
  slug: system-design/04-high-performance/product-search/03-ranking
  type: topic
  category: 排序与相关性
  summary: BM25 公式详解 + 多阶段排序管道（召回→粗排→精排）+ 业务信号混合 + A/B 测试
-->

# 排序与相关性 · 让用户看到最想要的商品

> **一句话**：搜索排序 = **BM25 文本相关性（召回层）+ 业务信号混合（粗排层）+ ML 精排模型（精排层）**，3 层管道从 100 万候选筛到 20 条结果。

← [返回: product-search](../README.md)

---

## 1. 相关性评分：从 TF-IDF 到 BM25

### 1.1 TF-IDF（ES 5.x 之前默认）

```text
score(D, Q) = Σ TF(qi, D) × IDF(qi)

TF(qi, D)  = 词 qi 在文档 D 中出现的次数（归一化后）
IDF(qi)    = log(N / df(qi))  ← N=总文档数, df=包含该词的文档数
```

**问题**：TF 线性增长 → 一个词出现 100 次的文档得分是 10 次的 10 倍，不合理。

### 1.2 BM25（ES 5.x+ 默认，Best Matching 25）

```text
score(D, Q) = Σ IDF(qi) × [f(qi,D) × (k1+1)] / [f(qi,D) + k1 × (1 - b + b × |D|/avgdl)]
```

**3 个核心参数**：

| 参数 | 默认值 | 含义 |
|------|--------|------|
| **k1** | 1.2 | 词频饱和度：值越大，高频词的加分越多（但有上界） |
| **b** | 0.75 | 文档长度归一化：0=不归一，1=完全归一 |
| **IDF** | — | 逆文档频率：稀有词（"运动鞋"）权重高，常见词（"的"）权重低 |

**BM25 vs TF-IDF 对比**：

```text
词频 → 得分
  1    TF-IDF: 1.0   BM25: 0.8
  5    TF-IDF: 5.0   BM25: 2.1    ← BM25 饱和效应
  10   TF-IDF: 10.0  BM25: 2.4
  50   TF-IDF: 50.0  BM25: 2.6    ← 几乎不再增长
```

**饱和效应**：词频从 1 → 5 贡献大，从 5 → 50 贡献微小。这更符合直觉——一个词出现 50 次不比 5 次相关 10 倍。

### 1.3 ES function_score：混合排序

```json
{
  "query": {
    "function_score": {
      "query": { "match": { "title": "运动鞋" } },
      "functions": [
        { "field_value_factor": { "field": "sales", "factor": 0.001, "modifier": "log1p" } },
        { "field_value_factor": { "field": "rating", "factor": 0.2 } },
        { "gauss": { "created_at": { "origin": "now", "scale": "30d" } } }
      ],
      "score_mode": "sum",
      "boost_mode": "multiply"
    }
  }
}
```

**业务信号权重**（典型电商配置）：

| 信号 | 权重 | 说明 |
|------|------|------|
| BM25 文本相关性 | 0.4 | 基础分 |
| 销量（log 归一化） | 0.3 | 销量越高排越前 |
| 评分 | 0.15 | 4.5+ 加分 |
| 新鲜度（高斯衰减） | 0.1 | 30 天内新品加分 |
| 促销标记 | 0.05 | 大促期间加权 |

### 1.4 字段长度归一化：错误配置 vs 调优后配置

BM25 的字段长度归一化会比较 `|D| / avgdl`。如果同一业务语义在不同商品上的 `title` 长度跨度为 5～50 个 token，长标题即使命中同一个关键词，也会因长度惩罚得到更低分；若再把 `title` 与 `description` 不加区分地混在同一字段中，分数偏差会进一步放大。

#### ❌ 错误：字段未归一化，所有文本挤进一个字段

下面的配置可以直接创建索引，但 `title` 既承载商品名，又混入卖点和属性；同一个 `title` 字段长度从 5 到 50 个 token，BM25 的长度归一化会让短标题天然占优。

```json
PUT /products_bad
{
  "settings": {
    "index": {
      "similarity": {
        "product_bm25": {
          "type": "BM25",
          "k1": 1.2,
          "b": 0.75
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "ik_max_word",
        "search_analyzer": "ik_smart",
        "similarity": "product_bm25"
      },
      "sales": { "type": "long" },
      "rating": { "type": "float" }
    }
  }
}

POST /products_bad/_bulk?refresh=true
{"index":{"_id":"short-title"}}
{"title":"耐克 男 跑步鞋 透气","sales":800,"rating":4.7}
{"index":{"_id":"long-title"}}
{"title":"耐克 官方旗舰 男士 春夏 轻便 透气 缓震 防滑 网面 运动 休闲 马拉松 专业 跑步鞋 黑白 多尺码","sales":800,"rating":4.7}

GET /products_bad/_search
{
  "query": {
    "match": {
      "title": "耐克 透气 跑步鞋"
    }
  }
}
```

> 两条商品的销量、评分和核心词命中相同，长标题却会受到更强的 BM25 长度惩罚。不要靠把 `b` 直接调成 `0` 掩盖建模问题，否则会同时丢失合理的长度归一化。

#### ✅ 正确：字段语义归一化，再做权重均衡

把稳定、短小的商品名放入 `title`，把卖点与规格拆到 `subtitle`、`attributes_text`；查询时用 `cross_fields` 平衡跨字段命中，并为标题保留适度权重。以下请求可直接在已安装 IK 分词器的 Elasticsearch 上运行。

```json
PUT /products_v2
{
  "settings": {
    "index": {
      "similarity": {
        "title_bm25": {
          "type": "BM25",
          "k1": 1.2,
          "b": 0.3
        },
        "content_bm25": {
          "type": "BM25",
          "k1": 1.2,
          "b": 0.75
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "ik_max_word",
        "search_analyzer": "ik_smart",
        "similarity": "title_bm25"
      },
      "subtitle": {
        "type": "text",
        "analyzer": "ik_max_word",
        "search_analyzer": "ik_smart",
        "similarity": "content_bm25"
      },
      "attributes_text": {
        "type": "text",
        "analyzer": "ik_max_word",
        "search_analyzer": "ik_smart",
        "similarity": "content_bm25"
      },
      "sales": { "type": "long" },
      "rating": { "type": "float" }
    }
  }
}

POST /products_v2/_bulk?refresh=true
{"index":{"_id":"short-title"}}
{"title":"耐克男士跑步鞋","subtitle":"春夏轻便透气缓震","attributes_text":"网面 防滑 黑白 多尺码","sales":800,"rating":4.7}
{"index":{"_id":"long-title"}}
{"title":"耐克男士跑步鞋","subtitle":"官方旗舰春夏专业马拉松款","attributes_text":"轻便 透气 缓震 防滑 网面 黑白 多尺码","sales":800,"rating":4.7}

GET /products_v2/_search
{
  "query": {
    "multi_match": {
      "query": "耐克 透气 跑步鞋",
      "type": "cross_fields",
      "fields": [
        "title^2.0",
        "subtitle^1.0",
        "attributes_text^0.8"
      ],
      "operator": "and"
    }
  }
}
```

**调优原则**：

| 项目 | ❌ 未归一化 | ✅ 归一化 + 权重均衡 |
|------|-------------|----------------------|
| 字段职责 | 商品名、卖点、属性全塞进 `title` | `title` / `subtitle` / `attributes_text` 各司其职 |
| 长度分布 | `title` 约 5～50 token，BM25 偏向短标题 | `title` 保持短且稳定，长文本独立归一化 |
| BM25 参数 | 所有字段统一 `b=0.75` | 短标题 `b=0.3`，正文类字段 `b=0.75` |
| 查询权重 | 单字段匹配，无法表达业务优先级 | `title^2.0`、`subtitle^1.0`、`attributes_text^0.8` |
| 验收方式 | 凭单条 `_score` 调参 | 固定标注集上比较 NDCG@10，并用 `_explain` 抽查分数组成 |

> `b=0.3` 与字段权重只是可复现实验起点，不是通用最优值。上线前应统计每个字段的 token 长度分布，在同一份 query-document 标注集上做网格搜索，再通过 A/B 测试确认 CTR 与转化率没有退化。

---

## 2. 多阶段排序管道

### 2.1 为什么需要多阶段？

100 万 SKU 全部跑精排模型太慢（ML 模型推理 ~10ms/条 × 100 万 = 10,000 秒）。

**解决**：逐层过滤，每层用更重的模型但更少的候选：

```text
全量索引（100 万 SKU）
    │
    ▼ 召回层（BM25 + 筛选条件）—— 毫秒级
候选集（1,000 条）
    │
    ▼ 粗排层（轻量模型：线性加权）—— 毫秒级
精排候选（100 条）
    │
    ▼ 精排层（重模型：GBDT / DNN）—— 百毫秒级
最终结果（20 条）
    │
    ▼ 重排层（多样性 + 业务规则）
展示给用户
```

### 2.2 召回层

**目标**：从 100 万中快速筛选出 ~1000 条相关候选。

**策略**：
- **BM25**：文本匹配（标题 + 描述 + 属性）
- **筛选条件**：品牌、价格区间、分类（ES filter，不参与评分）
- **向量召回**（可选）：用户 embedding × 商品 embedding，topK 补充

```text
// ES 召回查询
{
  "bool": {
    "must": [
      { "multi_match": { "query": "红色运动鞋", "fields": ["title^3", "description"] } }
    ],
    "filter": [
      { "term": { "status": "on_sale" } },
      { "range": { "price": { "gte": 100, "lte": 1000 } } }
    ]
  }
}
```

### 2.3 粗排层

**目标**：从 1000 → 100，用轻量模型快速打分。

**模型**：线性加权（function_score）

```text
粗排分 = BM25 × 0.4 + log(sales+1) × 0.3 + rating × 0.15 + freshness × 0.1 + promo × 0.05
```

延迟：< 5ms（ES function_score 内置计算）。

### 2.4 精排层

**目标**：从 100 → 20，用重模型精细排序。

**特征**（每条候选 ~50 维）：

| 类别 | 特征示例 |
|------|---------|
| 文本 | BM25 分、query-doc 编辑距离、标题命中率 |
| 商品 | 销量、评分、价格、上架天数、退货率 |
| 用户 | 历史购买品类、价格偏好、品牌偏好 |
| 上下文 | 时间（晚上推睡衣）、地域、设备（iOS 推高价） |

**模型选型**：

| 模型 | 延迟 | 效果 | 适用 |
|------|------|------|------|
| **GBDT**（XGBoost） | ~5ms | ⭐⭐⭐⭐ | 中小规模（首选） |
| **DNN** | ~10ms | ⭐⭐⭐⭐⭐ | 大规模 + 特征丰富 |
| **LTR**（Learning to Rank） | ~8ms | ⭐⭐⭐⭐⭐ | 专业搜索排序 |

### 2.5 重排层

**目标**：最终 20 条结果的展示优化。

**策略**：
- **多样性**：同品牌不超过 3 条连续展示（避免"耐克刷屏"）
- **业务规则**：广告位插入、置顶商品、新品推荐
- **去重**：同款不同店铺只展示最低价

---

## 3. A/B 测试与评估

### 3.1 搜索质量指标

| 指标 | 含义 | 参考值（示例） |
|------|------|----------------|
| **NDCG@10** | 归一化折损累积增益（离线排序质量） | > 0.8 |
| **MRR** | 首个相关结果的排名倒数的均值 | > 0.7 |
| **CTR** | 搜索结果点击率 | > 15% |
| **无结果率** | 搜索返回 0 条的比例 | < 5% |
| **搜索转化率** | 搜索 → 购买的比例 | 相对业务基线持续提升 |

> 上表是用于演示指标方向的**参考值，不是公开 SOTA 或通用上线门槛**。NDCG / MRR 必须注明标注数据集、相关性等级、查询分布和 `K`；CTR / 转化率必须注明曝光口径、位置偏差、端别、品类、时间窗及当前线上基线。不同数据集和业务之间不能直接横向比较。

一个可审计的目标定义应写成：`内部 5 万条头部/腰部/长尾查询标注集（0～3 级相关性），NDCG@10 从 0.76 提升到 0.78；移动端自然搜索流量 14 天 A/B，CTR 相对线上基线提升 ≥ 2%，且转化率不下降`。若没有公开论文或生产报告来源，应明确标为“内部示例”，不要写成“SOTA 指标”。

### 3.2 A/B 测试框架

```text
用户请求 → Hash(user_id) % 100
├─ 0-49: 对照组（当前排序模型）
└─ 50-99: 实验组（新排序模型）

对比指标：NDCG@10 / CTR / 转化率
统计显著性：p < 0.05 + 至少 1 周数据
```

---

## 5. 工业级 BM25 调参实践

### 5.1 Elasticsearch 查询示例

```json
GET /products/_search
{
  "query": {
    "multi_match": {
      "query": "运动鞋 透气",
      "fields": ["title^3", "description", "tags^2"],
      "type": "best_fields",
      "tie_breaker": 0.3
    }
  }
}
```

### 5.2 调参方法

1. **离线评估**：用历史 query 集合 + 人工标注的相关性，跑 BM25 不同参数组合，找 NDCG@10 最优
2. **A/B 验证**：在线 5%-10% 流量，对照组 vs 实验组至少 1 周数据
3. **监控指标**：CTR、NDCG@10、跳出率、无结果率

### 5.3 常见调参误区

- **过度调参**：BM25 + 业务信号混合已能覆盖 80% 场景，剩下 20% 需 ML 精排
- **忽视字段加权**：title 字段加权 3x 通常比调 BM25 本身更有效
- **盲目 k1=1.2 默认值**：长文档场景 b=0.3，短查询场景 b=0.9

## 6. 业务信号混合公式

```text
final_score(D, Q) = α × BM25(D, Q) + β × business_score(D)

其中：
  α + β = 1
  α ∈ [0.3, 0.7]  (文本相关性权重)
  β ∈ [0.3, 0.7]  (业务信号权重)
```

### 6.1 常见业务信号

| 信号 | 权重参考 | 说明 |
|------|---------|------|
| CTR (历史点击率) | 0.3-0.5 | 7/30 天点击率，归一化 |
| CVR (转化率) | 0.2-0.4 | 购买转化率 |
| 新品 boost | 0.1-0.2 | 上架 < 7 天的商品 |
| 库存充足 | 0.05-0.1 | 避免推荐无货商品 |
| 价格区间匹配 | 0.05-0.1 | 用户画像与商品价位 |

### 6.2 调整建议

- 启动期：α=0.7, β=0.3（让相关性主导）
- 成熟期：α=0.4, β=0.6（让业务信号主导）
- 季节性促销：临时提升 β 至 0.8

---

## 7. 系列导航

| 文章 | 核心内容 |
|------|---------|
| [总目录](../README.md) | 需求分析 + 架构概览 + 面试话术 |
| [架构演进](01-architecture.md) | 3 阶段架构 + 5 大组件 |
| [倒排索引与分词](02-inverted-index.md) | 倒排索引原理 + IK 分词 + 多维筛选 |
| **本文** | BM25 公式 + 多阶段排序 + 业务信号 |

← [返回: product-search](../README.md) | [返回: 04-high-performance](../../README.md) | [返回: 04.system-design](../../../README.md)
