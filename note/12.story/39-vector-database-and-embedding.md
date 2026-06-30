<!--
story:
  number: 39
  type: 续集
  position: 续集十五
  title: 味道仓库
  audience: AI 工程师 / 架构师
-->

# 39 · 味道仓库

> 从阿明的"向量库慢 / 召回差 / 成本高"，看向量数据库与 Embedding —— **6 大主流向量库对比 + Embedding 模型选型 + 性能调优 + 成本控制**

> **系列定位**：本篇是「阿明餐厅」系列的**续集十五**。在[续集十二 · 36a 成本结构](./36a-ai-token-cost-structure.md)2.2-2.3 节，我们讲了 Embedding 成本与向量库成本。在[续集十四 · 38 · RAG 专题](./38-rag-retrieval-augmented-generation.md)第一章，我们讲了向量检索是 RAG 的核心环节。本篇是**向量数据库与 Embedding 实战专题** —— 从选型到部署，从性能到成本，从单库到分布式，完整讲透向量技术栈。

---

## 引言：阿明的向量库"又慢又贵又召回差"

2026 年初，阿明的 RAG 系统上线后，老陈收到一堆投诉：

```text
投诉 1: 慢
  "搜索要等 3 秒，网页都卡了"
  → 向量库 QPS 上不去，单次检索 200ms+

投诉 2: 召回差
  "明明文档里有相关内容，AI 却说没找到"
  → Embedding 模型不适合 + 检索策略单一

投诉 3: 贵
  "向量库月账单 4 万，比 LLM 还贵"
  → Pinecone 商业版 + 维度太高 + 没优化

投诉 4: 数据丢失
  "昨天更新的文档，今天搜不到"
  → 索引同步机制有问题
```

老陈意识到：**向量库是 RAG 的"心脏"，但他之前把它当"附件"对待**。

本篇专门讲清楚向量数据库 + Embedding 的工程实践。

---

> **阿明的厨房笔记（开篇场景）**：传统数据库是按"菜名"找菜 —— 你必须说"红烧肉"才找得到"红烧肉"。但向量数据库是按"味道指纹"找菜 —— 你说"我要吃甜甜的、肉肉的、有点酱香的"，它能从 1000 道菜里找出味道最接近的 5 道。本章阿明要把这个"味道仓库"建起来 —— 装修、设计、取货、调温度，全套流程。

## 第一章：向量数据库基础 —— 食材仓库不认名字认味道，按"像不像"找货

### 1.1 什么是向量数据库？

```text
传统数据库：
  - 结构化数据（数字、字符串）
  - 精确匹配（=, LIKE）
  - B-Tree / Hash 索引

向量数据库：
  - 高维向量（768-3072 维）
  - 相似度匹配（cosine / L2 / dot product）
  - HNSW / IVF / PQ 索引
```

### 1.2 核心概念

```text
向量（Vector）：高维浮点数数组
  例：[0.1, 0.3, -0.5, 0.2, ..., 0.8]（1024 维）

相似度（Similarity）：
  - Cosine 相似度：cos(θ)，范围 [-1, 1]，越接近 1 越相似
  - L2 距离（欧氏距离）：√(Σ(xi-yi)²)，越小越相似
  - Dot product（点积）：Σ(xi×yi)，越大越相似

ANN（Approximate Nearest Neighbor）：近似最近邻
  - 不保证 100% 准确，但速度快 10-100 倍
  - 召回率（Recall）：99%+ 通常可接受
```

### 1.3 主流索引算法

| 算法 | 原理 | 速度 | 召回率 | 适用 |
|------|------|------|--------|------|
| **HNSW** | Hierarchical Navigable Small World 图 | 快 | 高（>95%） | 通用首选 |
| **IVF** | Inverted File，聚类分桶 | 中 | 中 | 大数据集 |
| **PQ** | Product Quantization，向量压缩 | 内存省 | 中（牺牲精度） | 超大规模 |
| **Flat** | 暴力搜索（精确） | 慢 | 100% | 小数据集 / 评测 |

**HNSW 是 2026 年事实标准** —— 速度快 + 召回率高 + 实现成熟。

### 1.4 向量数据库的核心操作

```python
# 1. 创建 collection（表）
collection = client.create_collection(
    name="documents",
    dimension=1024,  # 向量维度
    distance="cosine",  # 相似度度量
    index_type="hnsw",  # 索引类型
    hnsw_config={
        "M": 16,  # 每个节点的连接数
        "efConstruction": 200,  # 构建时的搜索宽度
    }
)

# 2. 插入向量
collection.insert(
    ids=["doc1", "doc2"],
    vectors=[
        [0.1, 0.2, ...],  # doc1 的 1024 维向量
        [0.3, 0.4, ...],  # doc2 的 1024 维向量
    ],
    payloads=[
        {"title": "红烧肉做法", "category": "menu"},
        {"title": "红烧肉热量", "category": "nutrition"},
    ]
)

# 3. 检索
results = collection.search(
    query_vector=[0.2, 0.3, ...],  # 查询向量
    top_k=5,  # 返回 top-5
    filter={"category": "menu"},  # 元数据过滤
)

# 4. 删除
collection.delete(ids=["doc1"])

# 5. 更新（= 删除 + 插入）
collection.upsert(ids=["doc2"], vectors=[...], payloads=[...])
```

---

> **阿明的厨房笔记（第二章场景）**：味道仓库建好了，第一步是选"货架"。阿明面对 6 种货架 —— 简易货架（Chroma）、连锁仓库（Pinecone）、智能立体库（Qdrant）、巨型中央仓库（Milvus）、厨房角落小柜（pgvector）、品牌授权库（Weaviate）。每种仓库成本、速度、扩展性都不同 —— 跟开餐厅选"中央厨房"还是"前置仓"是同一道决策题。

## 第二章：6 大主流向量数据库对比 —— 简易货架到智能立体库，六种仓库怎么盖

### 2.1 总览对比表

| 数据库 | 类型 | 强项 | 弱项 | 适合 |
|--------|------|------|------|------|
| **Pinecone** | SaaS | 易用 + 全托管 | 贵 + 数据出云 | 快速起步 |
| **Qdrant** | 开源 + 云 | 性能 + Rust 实现 | 社区略小 | 私有化首选 |
| **Milvus** | 开源 + 云 | 大规模 + 分布式 | 部署复杂 | 亿级向量 |
| **Weaviate** | 开源 + 云 | 模块化 + GraphRAG | 性能略弱 | 多模态 |
| **pgvector** | PostgreSQL 扩展 | 复用 PG 生态 | 性能弱（百万级以下） | 已有 PG |
| **Chroma** | 开源 | 极简 + 嵌入式 | 不适合生产 | 原型开发 |

### 2.2 Pinecone（商业 SaaS 首选）

```text
优势：
  - 全托管，零运维
  - 全球低延迟
  - 企业级 SLA
  - 与 LangChain / LlamaIndex 深度集成

劣势：
  - 贵（$0.096/GB/月 + $0.004/查询）
  - 数据出云（合规风险）
  - 黑盒（无法调优底层）

定价（2026）：
  - Serverless：$0.096/GB/月 + $0.004/查询
  - Enterprise：议价

适合：初创公司 / 不想运维 / 合规不严
```

### 2.3 Qdrant（开源 + 性能首选）

```text
优势：
  - Rust 实现，性能极强
  - 开源（Apache 2.0）+ 自部署
  - 丰富的过滤能力
  - 文档友好

劣势：
  - 社区比 Milvus 小
  - 云版本比 Pinecone 弱

部署：
  - Docker：docker run -p 6333:6333 qdrant/qdrant
  - Kubernetes：Helm Chart
  - 云：Qdrant Cloud

适合：私有化 / 性能要求高
```

### 2.4 Milvus（亿级向量首选）

```text
优势：
  - 分布式架构，支持 10 亿+ 向量
  - 多种索引（HNSW / IVF / PQ / GPU）
  - 与 Spark / Kafka 集成

劣势：
  - 部署复杂（依赖 etcd + MinIO + Pulsar）
  - 运维成本高

适合：超大规模（亿级以上）
```

### 2.5 pgvector（轻量首选）

```text
优势：
  - PostgreSQL 扩展，无需独立部署
  - 与 PG 生态融合（事务、备份、权限）
  - 适合中小规模

劣势：
  - 性能弱（百万级以下）
  - 不支持高级索引（GPU / PQ）

适合：
  - 已有 PG
  - 数据量 < 100 万
  - 不想增加运维
```

### 2.6 Weaviate / Chroma（特殊场景）

```text
Weaviate：
  - 强项：模块化 + GraphRAG + 多模态
  - 适合：需要混合搜索（向量 + 关键词 + Graph）

Chroma：
  - 强项：极简、嵌入式
  - 适合：原型开发 / Jupyter
  - 不适合：生产环境
```

### 2.7 阿明的选型决策

```text
阿明的 4 阶段选型：

阶段 1（原型）：Chroma（0 成本，3 分钟跑通）
阶段 2（早期）：pgvector（复用 PG，0 增量运维）
阶段 3（中等规模）：Qdrant（性能 + 私有化）
阶段 4（亿级）：Milvus（分布式 + GPU 索引）
```

---

> **阿明的厨房笔记（第三章场景）**：货架选好了，下一步是给每份食材贴"味觉坐标"。同是"红烧肉"，老厨师的版本和徒弟的版本味道不一样 —— Embedding 模型就是那个"老厨师"，能把味道拆成 1024 个维度（甜度、肉感、酱香、油度、软烂度……）。坐标贴得越准，"找相似菜"就越快越准。本章阿明要在 6 个 Embedding 模型里选 —— 用国外老厨师（OpenAI）、国产大厨（Qwen）、本地小厨（BGE）？

## 第三章：Embedding 模型选型 —— 给每份食材贴"味觉坐标"，贴得准才找得快

### 3.1 主流 Embedding 模型对比

| 模型 | 维度 | 强项 | 弱项 | 价格 |
|------|------|------|------|------|
| **OpenAI text-embedding-3-large** | 3072 | 通用最强 | 贵 + 出云 | $0.13/M |
| **OpenAI text-embedding-3-small** | 1536 | 性价比 | 略弱 | $0.02/M |
| **BGE-large-zh-v1.5** | 1024 | 中文 + 开源 | 英文略弱 | 自建 |
| **BGE-large-en-v1.5** | 1024 | 英文 + 开源 | 中文弱 | 自建 |
| **M3E-large** | 1024 | 中文 + 多任务 | 略旧 | 自建 |
| **Cohere embed-multilingual-v3** | 1024 | 多语言 | 国内访问难 | $0.10/M |
| **Jina Embeddings v3** | 1024 | 多任务 + 长文本 | 较新 | $0.02/M |

### 3.2 选型决策树

```text
Q1: 主要语言？
├── 中文为主 → BGE-large-zh-v1.5（开源 + 私有化）
├── 英文为主 → OpenAI text-embedding-3-large 或 BGE-large-en-v1.5
└── 多语言 → Cohere embed-multilingual-v3

Q2: 数据敏感度？
├── 高（不能出云）→ BGE 系列（自建）
└── 低 → OpenAI / Cohere（API）

Q3: 预算？
├── 充足 → OpenAI text-embedding-3-large
├── 中等 → OpenAI text-embedding-3-small
└── 低 → BGE 系列（自建）

Q4: 文档长度？
├── < 512 token → 通用模型
└── > 512 token → Jina / BGE-M3（支持长文本）
```

### 3.3 阿明的选型结论

```text
阿明的混合策略：
  - 主力：BGE-large-zh-v1.5（自建，私有化）
  - 补充：OpenAI text-embedding-3-large（关键文档）
  - 长文本：BGE-M3（> 2K token 的文档）

实测：
  - BGE 召回率：82%
  - OpenAI 召回率：88%
  - BGE-M3（长文档）：召回率 91%
  - 混合使用：召回率 93%（最优）
```

### 3.4 Embedding 模型的微调

```python
# 用 LoRA 微调 Embedding 模型
from sentence_transformers import SentenceTransformer, losses

model = SentenceTransformer("BAAI/bge-large-zh-v1.5")

# 准备领域数据集
train_examples = [
    InputExample(texts=["红烧肉", "红焖肉"], label=0.95),  # 相似
    InputExample(texts=["红烧肉", "糖醋排骨"], label=0.7),  # 中等相关
    InputExample(texts=["红烧肉", "意大利面"], label=0.1),  # 不相关
]

# 微调
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)
model.fit(train_dataloader, epochs=3)

# 保存
model.save("bge-finetuned-restaurant")
```

**何时需要微调？**

```text
需要：
  - 领域术语多（医疗、法律、金融）
  - 通用模型召回率 < 70%
  - 有标注数据（> 1000 对）

不需要：
  - 通用场景（电商、餐饮、客服）
  - 召回率已经 > 85%
```

---

> **阿明的厨房笔记（第四章场景）**：货架有了、坐标贴好了，但"找菜"还是慢 —— 阿明发现：仓库巷道太宽（ef 参数过大）、食材包装太大（维度太高）、出库太散（无批量化）、常用菜没放门口（无缓存）。本章阿明化身仓库管理员，调整 4 个核心开关 —— 让"找菜"从 3 秒降到 200ms。

## 第四章：向量检索的 4 大调优 —— 巷道宽度、包装规格、批量出库、常用位

### 4.1 调优 1：HNSW 参数

```python
# HNSW 关键参数
hnsw_config = {
    "M": 16,  # 每个节点的连接数（越大召回越高，但内存越多）
    "efConstruction": 200,  # 构建时的搜索宽度（越大索引质量越好，但构建慢）
    "ef": 50,  # 查询时的搜索宽度（越大召回越高，但查询慢）
}

# 调优建议：
# - 数据量 < 100 万：M=16, efConstruction=200, ef=50
# - 数据量 100 万 - 1000 万：M=32, efConstruction=400, ef=100
# - 数据量 > 1000 万：M=48, efConstruction=500, ef=200
```

### 4.2 调优 2：维度选择

```text
维度 vs 召回率 / 成本：
  - 384 维：快 + 便宜，召回率略低
  - 768 维：平衡
  - 1024 维：通用主流
  - 1536 维：高召回
  - 3072 维：最高召回，最贵

建议：
  - 通用场景：1024 维
  - 高精度场景：1536-3072 维
  - 预算紧 / 数据大：512-768 维
```

### 4.3 调优 3：批量检索

```python
# 优化前：100 个查询 = 100 次网络往返
for query in queries:
    results = collection.search(query, top_k=5)

# 优化后：100 个查询 = 1 次网络往返
results = collection.search_batch(
    query_vectors=[q.embedding for q in queries],
    top_k=5,
)
```

### 4.4 调优 4：缓存策略

```python
# 1. 查询 Embedding 缓存（命中率 30-50%）
embedding_cache = RedisCache(ttl=7*24*3600)

async def get_embedding(text):
    cache_key = hash(text)
    cached = await embedding_cache.get(cache_key)
    if cached:
        return cached
    embedding = await embedding_api.embed(text)
    await embedding_cache.set(cache_key, embedding)
    return embedding

# 2. 检索结果缓存（命中率 20-30%）
#    key: hash(query), value: 检索结果
#    适用：FAQ、重复问题

# 3. 向量缓存（HNSW 不适用，但可以缓存原始向量）
```

---

> **阿明的厨房笔记（第五章场景）**：一个月后阿明拿到账单 —— "向量库月账单 4 万，比 LLM 还贵！"老陈说："老板，你想想，每找一次菜，钱包就漏一点：存储费（仓库租金）、查询费（出库费）、Embedding费（厨师成本）、副本费（备份仓库）。仓库没装仪表盘，钱烧了都不知道。"本章阿明要给"味道仓库"装"财务监控" —— 让每一笔支出都可追溯。

## 第五章：向量数据库的成本与监控 —— 每找一次食材花多少钱，仓库仪表盘怎么看

### 5.1 成本结构（详见 [36a 第二章 2.3](./36a-ai-token-cost-structure.md#23-组件-3向量数据库成本占-5-10)）

```text
向量库成本 = 存储费 + 查询费 + 网络费

存储费：
  - 向量 × 维度 × 4 bytes / GB
  - 100 万条 1024 维向量 ≈ 4 GB

查询费：
  - 按 QPS 计价（自建无此项）
  - Pinecone：$0.004/查询

网络费：
  - 跨 AZ / 跨区域（自建需注意）
```

### 5.2 监控指标

```text
1. 性能指标
  - QPS（每秒查询数）
  - P50 / P99 延迟
  - 索引大小

2. 质量指标
  - Recall@K（实测召回率）
  - MRR（平均倒数排名）
  - 用户反馈（搜索满意度）

3. 成本指标
  - 月存储费
  - 月查询费
  - 单次查询成本

4. 可用性
  - uptime
  - 错误率
  - 索引同步延迟
```

### 5.3 监控工具

```python
# Prometheus + Grafana 监控 Qdrant
from prometheus_client import Counter, Histogram

vector_search_latency = Histogram(
    "vector_search_latency_seconds",
    "向量检索延迟"
)

vector_search_count = Counter(
    "vector_search_total",
    "向量检索总数"
)

# 在检索时埋点
@vector_search_latency.time()
async def search_with_metrics(query):
    vector_search_count.inc()
    return await qdrant.search(query)
```

---

> **阿明的厨房笔记（第六章场景）**：阿明的餐厅连锁开到 80 家，每家店都有自己的"味道仓库"。现在问题来了 —— A 店的"川菜仓库"和 B 店的"川菜仓库"能合并吗？顾客问"辣的菜"能不能同时返回所有店的菜？仓库租金涨了怎么办（压缩存储）？本章阿明要从"单店仓库"升级到"连锁仓库网络"。

## 第六章：向量数据库的高级话题 —— 跨库调拨、多维查找、压缩存储

### 6.1 分布式向量库

```text
适用：> 1 亿向量

方案：
  - Milvus 分布式（推荐）
  - Pinecone Enterprise
  - 自建分片（按业务 / 时间）

挑战：
  - 数据一致性
  - 跨分片检索
  - 索引重建
```

### 6.2 混合检索（Hybrid Search）

```text
向量检索 + 关键词检索 = Hybrid Search

实现：
  1. 向量检索 top-100
  2. BM25 检索 top-100
  3. 加权融合（0.7 * 向量 + 0.3 * 关键词）
  4. ReRank 取 top-10

工具：Qdrant + Elasticsearch + Cohere Rerank

详见 [38 第二章 2.1](./38-rag-retrieval-augmented-generation.md#21-模式-1hybrid-search混合检索)
```

### 6.3 元数据过滤

```python
# 向量检索 + 元数据过滤
results = collection.search(
    query_vector=embedding,
    top_k=5,
    filter={
        "category": "menu",  # 类别
        "date": {"$gte": "2026-01-01"},  # 时间
        "source": {"$in": ["internal", "wiki"]},  # 来源
        "permission": {"$contains": user_role},  # 权限
    }
)
```

**为什么需要元数据过滤？**

```text
1. 权限控制：不同用户看不同文档
2. 时效性：只用最近 30 天的文档
3. 来源筛选：只检索可信来源
4. 业务分类：只检索特定类别
```

### 6.4 向量压缩

```text
PQ（Product Quantization）：
  - 1024 维 → 64 字节
  - 压缩比 16x
  - 召回率损失 5-10%

适用场景：
  - 超大规模（> 1 亿向量）
  - 内存受限
  - 召回率要求略宽松

工具：Faiss / ScaNN
```

---

> **阿明的厨房笔记（第七章场景）**：仓库上了，但阿明发现个问题 —— 顾客抱怨"找菜慢"，老陈说"仓库跑得好好的"，到底谁说的对？仓库也需要"仪表盘"：每天出库多少次（QPS）、平均出库时间（P99 延迟）、仓库多少菜（向量数）、哪些菜最常被找（Top Query）、哪些菜根本没人找（冷数据）。本章阿明要给"味道仓库"装上"老陈牌监控大屏"。

## 第七章：向量数据库的可观测性 —— 仓库也要装监控，找货快不快一查便知

### 7.1 与 37 · AI Observability 打通

```text
向量检索 trace 数据：
  - 查询向量（不存原文本，存 hash）
  - top-K 文档 ID + 分数
  - 检索延迟
  - 元数据过滤条件
  - 索引类型 / 参数

工具集成：
  - LangSmith + Qdrant
  - Arize Phoenix + Milvus
  - OpenLLMetry + 任何向量库

详见 [37 · AI 可观测性](./37-ai-observability.md)
```

### 7.2 检索质量监控

```python
# 在线检索质量监控
async def monitor_retrieval_quality(query, results):
    # 1. 统计 top-1 分数
    top_score = results[0].score

    # 2. 分数过低告警（可能检索失败）
    if top_score < 0.5:
        await alert_low_retrieval_score(query, top_score)

    # 3. 分数分布监控
    score_distribution = [r.score for r in results]
    await metrics.record_score_distribution(score_distribution)

    # 4. 抽样人工 review
    if random.random() < 0.01:  # 1% 抽样
        asyncio.create_task(human_review(query, results))
```

---

## 核心总结：向量数据库全景

| 维度 | 核心内容 | 工具 / 方法 |
|------|----------|------------|
| **基础** | 向量 / 相似度 / ANN | 见第一章 |
| **6 大向量库** | Pinecone / Qdrant / Milvus / Weaviate / pgvector / Chroma | 见第二章 |
| **Embedding 选型** | OpenAI / BGE / M3E / Cohere / Jina | 见第三章 |
| **4 大调优** | HNSW 参数 / 维度 / 批量 / 缓存 | 见第四章 |
| **成本监控** | 存储费 + 查询费 + 网络费 | 见第五章 |
| **高级话题** | 分布式 / Hybrid / 元数据 / 压缩 | 见第六章 |
| **可观测性** | 与 37 AI Observability 打通 | 见第七章 |

### 一句心法

**向量数据库是 RAG 的"心脏"，不是"附件"**：选型决定性能，调优决定召回率，监控决定稳定性，成本决定可持续性。

---

## 延伸阅读

- [RAG 检索增强生成 38](./38-rag-retrieval-augmented-generation.md) —— 续集十四，向量检索是 RAG 的核心环节
- [AI 成本结构 36a](./36a-ai-token-cost-structure.md) / [36b 成本优化](./36b-ai-token-cost-optimization.md) —— 续集十二，向量库与 Embedding 成本详解
- [AI 可观测性 37](./37-ai-observability.md) —— 续集十三，向量检索的 trace 与监控
- [AI 评测工程 34a/34b](./34a-ai-evaluation-fundamentals.md) / [34b](./34b-ai-evaluation-pipeline.md) —— 续集十，向量检索的 Recall / MRR 评测

---

## 跨章节衔接

- 11.ai/02-technology-stack/README.md —— AI 技术栈 —— 向量数据库在 AI 技术栈中的位置
- 11.ai/03-engineering/ai-platforms/README.md —— AI 平台 —— 主流平台的向量库集成

---

## 结语

阿明花了 2 个月重新设计向量库选型与调优，效果立竿见影：

```text
优化前：
  - 单次检索：300ms（太慢）
  - 召回率：75%（太差）
  - 月成本：4 万（太贵）

优化后：
  - 单次检索：50ms（6x 提速）
  - 召回率：92%（+17%）
  - 月成本：1.2 万（-70%）

关键动作：
  1. pgvector → Qdrant（性能 6x）
  2. 维度 1536 → 1024（成本 -33%）
  3. 加 Hybrid Search（召回 +12%）
  4. 加 ReRank（Faithfulness +8%）
  5. 加 HNSW 调优（性能 +20%）
```

下次当你选向量库时，不妨问自己：

- 我的数据量级？**百万 / 千万 / 亿级**
- 我的性能要求？**P99 < 100ms**
- 我的合规要求？**能出云吗**
- 我的预算？**存储费 + 查询费**
- 我的 Embedding 模型？**中文 / 英文 / 多语言**
- 我的检索策略？**纯向量 / Hybrid / Graph**
- 我有元数据过滤吗？**权限 / 时效 / 来源**
- 我有**缓存策略**吗？**Embedding 缓存 + 结果缓存**

> 好的向量数据库设计，不是"选个 Pinecone 就完事"，而是"选型 + 调优 + 监控 + 成本"的完整工程。这是 RAG 系统**事实性**的基石。

← [返回系列导读](./index.md)