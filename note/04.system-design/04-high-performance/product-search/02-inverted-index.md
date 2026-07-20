<!--
module:
  parent: system-design/product-search
  slug: system-design/04-high-performance/product-search/02-inverted-index
  type: topic
  category: 索引与分词
  summary: 倒排索引原理 + IK 中文分词 + 同义词扩展 + 多维筛选（Faceted Search）
-->

# 倒排索引与分词 · 搜索的核心引擎

> **一句话**：倒排索引 = **term → doc list** 的反向映射，让搜索从"逐文档扫描"变成"查字典"。中文分词决定了"红色运动鞋"被拆成什么，直接影响搜索质量。

← [返回: product-search 总目录](README.md)

---

## 1. 倒排索引原理

### 1.1 正排索引 vs 倒排索引

**正排索引**（Forward Index）：doc → terms

```yaml
doc1: [nike, 红色, 运动鞋, 42, 码]
doc2: [adidas, 白色, 跑步鞋, 41, 码]
doc3: [nike, 黑色, 篮球鞋, 43, 码]
```

搜索"运动鞋"需要遍历所有文档 → O(n)。

**倒排索引**（Inverted Index）：term → docs

```text
nike     → [doc1, doc3]
红色     → [doc1]
运动鞋   → [doc1]
adidas   → [doc2]
白色     → [doc2]
跑步鞋   → [doc2]
篮球鞋   → [doc3]
42       → [doc1]
41       → [doc2]
43       → [doc3]
码       → [doc1, doc2, doc3]
```

搜索"运动鞋"直接查 posting list → O(1)。

### 1.2 Posting List 结构

```text
term "运动鞋":
┌──────────────────────────────────────────────┐
│ doc_id: [1, 5, 15, 23, 87, ...]             │  ← 文档 ID 列表
│ tf:     [2, 1, 3,  1,  1, ...]              │  ← 词频（用于 BM25）
│ pos:    [[0,3], [5], [1,4,7], [2], [8]]     │  ← 位置（用于短语查询）
└──────────────────────────────────────────────┘
```

**压缩优化**：ES 使用 **Frame Of Reference (FOR)** 编码压缩 doc_id 列表，100 万文档的 posting list 压缩后仅几 KB。

### 1.3 布尔查询的执行

```text
查询："nike 运动鞋"
→ term1(nike): [1, 3, 7, 15, 23, ...]
→ term2(运动鞋): [1, 5, 15, 23, 87, ...]
→ AND 操作（跳表合并）: [1, 15, 23]
```

ES 用**跳表**（skip list）加速 posting list 的交集运算，大列表的 AND 操作可在微秒级完成。

---

## 2. 中文分词

### 2.1 为什么中文分词比英文难？

```text
英文： "Nike red running shoes" → 天然空格分隔 → [nike, red, running, shoes]
中文： "Nike红色运动鞋42码"     → 无分隔符     → 需要分词算法
```

### 2.2 IK 分词器的两种模式

**ik_smart**（智能分词，搜索时使用）：

```text
"Nike红色运动鞋42码"
→ [nike, 红色, 运动鞋, 42, 码]
```

**ik_max_word**（最细粒度分词，索引时使用）：

```text
"Nike红色运动鞋42码"
→ [nike, 红色, 运动, 运动鞋, 动鞋, 42, 码]
```

**策略**：索引时用 `ik_max_word`（多切词，提高召回率），搜索时用 `ik_smart`（智能切词，提高准确率）。

### 2.3 自定义词典

电商场景有大量领域词汇，默认分词器会切错：

```text
默认分词： "雅诗兰黛" → [雅诗, 兰, 黛]  ❌
自定义词典后： "雅诗兰黛" → [雅诗兰黛]    ✅
```

**词典格式**（`custom/mydict.dic`）：

```text
雅诗兰黛
兰蔻
SK-II
优衣库
airpods
```

**热更新**：IK 支持通过 API 动态加载词典，无需重启 ES：

```bash
# 更新词典文件后，调用 IK 的热更新接口
curl -X POST "localhost:9200/_plugins/_ik/hot_update"
```

### 2.4 同义词扩展

**同义词词典**（`synonyms.txt`）：

```text
# 等价同义词（双向扩展）
手机, 智能手机, mobile, phone
运动鞋, 跑鞋, 跑步鞋, sneaker

# 单向扩展（→ 左边扩展为右边）
苹果 => apple, 苹果手机
```

**应用时机**：

```text
用户搜索："phone"
    ↓ 同义词扩展
实际查询："手机 OR 智能手机 OR mobile OR phone"
    ↓ 倒排索引查询
返回所有匹配文档
```

**注意**：同义词扩展会**降低精确度**（搜"phone"会返回"手机壳"），需要配合相关性排序控制结果质量。

---

## 3. 多维筛选（Faceted Search）

### 3.1 什么是 Faceted Search？

用户搜索"运动鞋"后，左侧显示筛选面板：

```text
搜索结果：运动鞋（共 1,234 件）

品牌：    Nike (456)  Adidas (321)  新百伦 (123)  ...
价格：    <200 (234)  200-500 (567)  500-1000 (321)  ...
颜色：    黑色 (345)  白色 (289)  红色 (123)  ...
尺码：    40 (89)  41 (156)  42 (234)  43 (178)  ...
```

每个筛选维度显示**该维度下各值的文档数量**，这就是 Faceted Search。

### 3.2 ES 聚合实现

```json
{
  "query": {
    "match": { "title": "运动鞋" }
  },
  "aggs": {
    "brand_facet": {
      "terms": { "field": "brand", "size": 20 }
    },
    "price_facet": {
      "range": {
        "field": "price",
        "ranges": [
          { "to": 200 },
          { "from": 200, "to": 500 },
          { "from": 500, "to": 1000 },
          { "from": 1000 }
        ]
      }
    },
    "color_facet": {
      "nested": { "path": "attributes" },
      "aggs": {
        "color": {
          "filter": { "term": { "attributes.key": "颜色" } },
          "aggs": {
            "values": { "terms": { "field": "attributes.value" } }
          }
        }
      }
    }
  }
}
```

### 3.3 Nested vs Flat 属性对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **Nested**（嵌套对象） | 精确匹配（颜色=红 AND 尺码=42 不会匹配"红色包 + 42 码鞋"） | 查询复杂、索引大 |
| **Flat**（扁平字段） | 查询简单、索引小 | 可能错误匹配（属性交叉） |

**推荐**：商品属性用 `nested`（精确筛选），简单标签用 `keyword`（快速聚合）。

---

## 4. 搜索建议与纠错

### 4.1 Completion Suggester（搜索建议）

```json
// 索引中添加 suggest 字段
"suggest": {
  "type": "completion",
  "analyzer": "ik_smart"
}

// 查询
{
  "suggest": {
    "product-suggest": {
      "prefix": "运动",
      "completion": { "field": "suggest" }
    }
  }
}
```

**原理**：Completion Suggester 使用 **FST**（Finite State Transducer），在内存中实现 O(len) 的前缀匹配，延迟 < 1ms。

### 4.2 拼写纠错

**方案 1：Fuzzy Query**（编辑距离）

```json
{
  "query": {
    "fuzzy": {
      "title": { "value": "苹果手记", "fuzziness": 1 }
    }
  }
}
```

**方案 2：拼音纠错**

```text
用户输入："ya shi lan dai"
    ↓ pinyin analyzer
匹配："雅诗兰黛"
```

需要安装 `elasticsearch-analysis-pinyin` 插件。

---

## 5. 系列导航

| 文章 | 核心内容 |
|------|---------|
| [总目录](README.md) | 需求分析 + 架构概览 + 面试话术 |
| [架构演进](01-architecture.md) | 3 阶段架构 + 5 大组件 |
| **本文** | 倒排索引 + 分词 + 多维筛选 |
| [排序与相关性](03-ranking.md) | BM25 公式 + 多阶段排序 + 业务信号 |

← [返回: product-search 总目录](README.md)
