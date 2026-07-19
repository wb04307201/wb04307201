<!--
module:
  parent: high-performance
  slug: system-design/04-high-performance/product-search
  type: deep-dive
  category: 商品搜索系统
  summary: 商品搜索系统设计 —— 倒排索引 + BM25 + 多阶段排序 + 多维筛选 + 高可用架构，从 DB LIKE 到 Elasticsearch 完整演进
-->

# 商品搜索系统设计 · 从 DB 到 Elasticsearch 完整方案

> **一句话答案**：商品搜索 = **倒排索引（Elasticsearch）+ 中文分词（IK）+ BM25 相关性 + 多阶段排序（召回→粗排→精排）+ 多维筛选（faceted search）+ 数据同步（Canal + MQ）+ 缓存（热门 query 结果缓存）**。10 万 SKU 用单机 ES 即可，百万级需要集群 + 分片。

← [返回: 高性能设计](../README.md) · 面试题：[13.split-hairs/product-search](../../../13.split-hairs/04.system-design/product-search/README.md)

---

## 0. 面试高频拷问

```
Q：设计一个商品搜索系统，支持关键词搜索 + 多维筛选 + 排序，QPS 1 万？
Q：Elasticsearch 的倒排索引是怎么工作的？BM25 和 TF-IDF 有什么区别？
Q：商品数据从 MySQL 到 ES 怎么保证同步一致性？
```

**回答框架（4 层递进）**：

1. **需求分析**：关键词搜索 + 多维筛选（品牌/价格/分类）+ 排序（相关性/销量/价格）+ 搜索建议 + 纠错
2. **3 大核心组件**：倒排索引引擎 + 分词器 + 多阶段排序管道
3. **架构演进**：DB LIKE → 单节点 ES → ES 集群 + 分片 + 缓存
4. **5 反模式**：DB LIKE 模糊查询 / 不配分词器 / 忽略数据同步延迟 / 排序只用相关性 / 没做 query 缓存

完整面试题见 [13.split-hairs/04.system-design/product-search](../../../13.split-hairs/04.system-design/product-search/README.md)。

---

## 1. 需求拆解

### 1.1 功能需求

| 功能 | 说明 | 技术挑战 |
|------|------|---------|
| **关键词搜索** | 用户输入"红色运动鞋 42 码"，返回匹配商品 | 分词 + 多字段匹配（标题/描述/属性） |
| **多维筛选** | 品牌、价格区间、分类、颜色、尺码 | Faceted search（聚合查询） |
| **排序** | 相关性 / 销量 / 价格 / 最新 | 多阶段排序管道 |
| **搜索建议** | 输入"运动"提示"运动鞋""运动裤" | Suggest API + 前缀匹配 |
| **纠错** | "苹果手记" → "苹果手机" | 编辑距离 + 拼音纠错 |
| **同义词** | "手机" = "手机壳" ≠ "手机" | 同义词词典 + 扩展查询 |

### 1.2 性能需求

| 指标 | 要求 |
|------|------|
| **搜索延迟** | P99 < 200ms |
| **QPS** | 1 万（日常）/ 5 万（大促） |
| **数据新鲜度** | 商品信息变更 < 5 秒可搜到 |
| **索引规模** | 100 万 SKU（典型电商） |

---

## 2. 架构演进

> 📖 **深度阅读**：[01-architecture.md](01-architecture.md) — 3 阶段架构演进详解

### 2.1 阶段 1：DB LIKE（< 1 万 SKU）

```sql
SELECT * FROM products WHERE title LIKE '%运动鞋%' ORDER BY sales DESC;
```

**问题**：全表扫描、无法分词、不支持相关性排序、性能随数据量线性下降。

### 2.2 阶段 2：单节点 Elasticsearch（1 万 ~ 50 万 SKU）

```
MySQL → Canal → MQ → ES Index
用户 → Search API → ES Query → 排序 → 返回
```

**优势**：倒排索引 O(1) 查询、BM25 相关性、中文分词、聚合查询。

### 2.3 阶段 3：ES 集群 + 缓存（50 万 ~ 千万 SKU）

```
用户 → CDN → Search API → Query 缓存 → ES 集群（多分片）→ 排序 → 返回
                                      → MQ → 数据同步
```

**关键设计**：
- **分片策略**：按品类分片（减少跨分片查询）
- **缓存层**：热门 query 结果缓存（Redis，TTL 30s）
- **降级**：ES 不可用时回退 DB 搜索

---

## 3. 核心技术

### 3.1 倒排索引与分词

> 📖 **深度阅读**：[02-inverted-index.md](02-inverted-index.md) — 倒排索引 + 分词 + 多维筛选详解

```
文档："Nike 红色运动鞋 42 码"
     ↓ IK 分词
Terms: [nike, 红色, 运动鞋, 42, 码]
     ↓ 倒排索引
nike → doc1, doc5, doc99
红色 → doc1, doc3, doc7
运动鞋 → doc1, doc2, doc15
```

**中文分词选型**：
- **IK**：最常用，支持自定义词典，适合电商场景
- **Jieba**：Python 生态首选，Java 可通过 JNI 调用
- **HanLP**：NLP 功能最全，但启动慢

### 3.2 排序与相关性

> 📖 **深度阅读**：[03-ranking.md](03-ranking.md) — BM25 + 多阶段排序详解

**BM25 公式**（简化版）：

```
score(D, Q) = Σ IDF(qi) × f(qi,D) × (k1+1) / (f(qi,D) + k1×(1 - b + b×|D|/avgdl))
```

- **IDF**：逆文档频率，"运动鞋"比"的"权重高
- **f(qi,D)**：词频，出现越多越相关（但有饱和效应）
- **|D|/avgdl**：文档长度归一化，短文档中出现更有价值

**多阶段排序管道**：

```
全量索引（100 万）
    ↓ 召回（BM25 + 筛选条件）
候选集（1000 条）
    ↓ 粗排（轻量模型：BM25 + 销量 + 评分）
精排候选（100 条）
    ↓ 精排（重模型：特征向量 + ML 模型）
最终结果（20 条）
```

---

## 4. 数据同步

商品数据的主存储在 MySQL，搜索索引在 ES，需要保证两者一致：

```
MySQL (主存储)
    ↓ Canal 监听 binlog
MQ (RocketMQ / Kafka)
    ↓ 消费者
ES Index (搜索索引)
```

**一致性保证**：
- **顺序消费**：同一商品的变更按顺序消费（分区 key = product_id）
- **幂等写入**：ES 用 `version` 字段防止旧数据覆盖新数据
- **补偿机制**：定时全量对比（MySQL count vs ES doc count），差异自动修复
- **延迟监控**：binlog 到 ES 的延迟 < 5 秒（P99），超时告警

---

## 5. 5 大反模式

### 5.1 用 DB LIKE 做搜索

```sql
-- ❌ 全表扫描，100 万数据查询 > 10 秒
WHERE title LIKE '%运动鞋%'
```

**修复**：迁移到 Elasticsearch，倒排索引查询 O(1)。

### 5.2 不配中文分词器

```json
// ❌ 默认 standard analyzer 会把"红色运动鞋"拆成单字
{"title": {"type": "text"}}

// ✅ 配置 IK 分词器
{"title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"}}
```

### 5.3 排序只用相关性

```
// ❌ 纯 BM25 排序 → 销量 0 的新品排第一
// ✅ 混合排序 = BM25 × 0.4 + 销量分 × 0.3 + 评分 × 0.2 + 新鲜度 × 0.1
```

### 5.4 忽略数据同步延迟

```
用户刚改了商品标题 → 立即搜索 → 还是旧标题 → "搜索有 bug！"
```

**修复**：
- 前端：编辑后提示"搜索索引更新需要约 5 秒"
- 后端：写后读（read-after-write）场景直接查 DB

### 5.5 没做 Query 缓存

```
"运动鞋" 这个 query 每秒被搜索 500 次，每次都打到 ES → 浪费
```

**修复**：
- 热门 query → Redis 缓存结果（TTL 30s）
- 冷门 query → 直接查 ES
- 数据变更 → 异步失效相关缓存

---

## 6. 面试话术（30 秒版）

> "商品搜索系统核心是 Elasticsearch 倒排索引 + IK 中文分词 + BM25 相关性排序。
>
> 架构分 3 层：MySQL 做主存储，Canal 监听 binlog 通过 MQ 同步到 ES，搜索请求走 ES 集群。
>
> 排序用多阶段管道：先用 BM25 + 筛选条件召回 1000 条候选，再用轻量模型粗排到 100 条，最后用 ML 精排出 20 条。业务信号（销量、评分、新鲜度）混合进排序公式。
>
> 性能优化：热门 query 结果缓存到 Redis（TTL 30s），分片按品类划分减少跨分片查询，搜索建议用 ES 的 completion suggester。
>
> 一致性保证：Canal + MQ 顺序消费 + ES version 防覆盖 + 定时全量对比补偿。"

---

## 7. 交叉引用

- 主模块：[`04.system-design`](../../README.md) — 系统设计知识体系
- 同级案例：[敏感词过滤](../sensitive-word-filter/README.md) — AC 自动机 + 高并发过滤系统设计
- 同级案例：[大文件上传](../file-upload/README.md) — 分片 + 断点续传 + 秒传 + 对象存储
- 缓存模式：[缓存设计模式](../cache-patterns/README.md) — Cache-Aside / Write-Behind
- 消息队列：[消息队列](../mq/README.md) — 数据同步的 MQ 选型
- 数据库：[分库分表](../database-optimization/db-sharding/README.md) — 数据规模扩大后的分片策略
- 算法基础：[字符串算法](../../../02.computer-basics/02-algorithms/string-algorithms/) — AC 自动机 / Trie 树

## 相关章节

- 面试题：[`13.split-hairs/04.system-design`](../../../13.split-hairs/04.system-design/README.md) — 系统设计面试题全集
- 深度阅读：[`04.system-design`](../../README.md) — 系统设计主模块

← [返回: 高性能设计](../README.md)
