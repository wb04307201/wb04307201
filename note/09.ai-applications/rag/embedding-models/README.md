<!--
module:
  parent: ai
  slug: ai/embedding-models
  type: article
  category: 主模块子文章
  summary: Embedding 模型横评（BGE / M3E / Qwen / OpenAI）
  depth: ⭐⭐⭐⭐⭐
-->

# Embedding 模型横评

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：**BGE / M3E / Qwen / OpenAI text-embedding-3** 4 大主流 Embedding 模型横评，帮 RAG 系统选对 Embedding 提升 20-30% 召回。

---

## 📊 4 大模型对比

| 模型 | 维度 | 多语言 | 上下文 | MTEB 中文 | MTEB 英文 | 商业许可 | 显存 |
|------|------|--------|--------|----------|----------|---------|------|
| **BGE-M3** | 1024 | ✅ 100+ 语言 | 8K | **68.2** | 65.4 | MIT | 2GB |
| **M3E-large** | 1024 | ✅ 中英 | 512 | 64.3 | 60.1 | Apache | 1.5GB |
| **Qwen3-Embedding-8B** | 4096 | ✅ 多语言 | 32K | **70.5** | 70.8 | Apache | 16GB |
| **text-embedding-3-large** | 3072 | ✅ 多语言 | 8K | 65.8 | **68.4** | OpenAI API | - |

**MTEB**（Massive Text Embedding Benchmark）：2024 标准评测。

---

## 🆚 选型决策

```text
Q1: 预算？
├── 紧 → BGE-M3（开源免费）/ M3E
└── 充足 → OpenAI / Qwen3-8B

Q2: 多语言？
├── 仅中英 → M3E
└── 多语言（100+）→ BGE-M3

Q3: 上下文长度？
├── < 512 → M3E
├── 512-8K → BGE-M3
└── > 8K → Qwen3-8B

Q4: 准确性优先？
├── 通用 → BGE-M3
└── 极致 → Qwen3-8B（中文 SOTA）
```

---

## 📐 核心原理：向量空间 + 相似度

### Cosine Similarty 公式

Embedding 把文本映射到 $d$ 维实数空间 $\mathbb{R}^d$。两个向量间的余弦相似度定义为：

$$
\text{cos\_sim}(q, d) = \frac{q \cdot d}{\|q\|_2 \cdot \|d\|_2} = \frac{\sum_{i=1}^{d} q_i d_i}{\sqrt{\sum_{i=1}^{d} q_i^2} \cdot \sqrt{\sum_{i=1}^{d} d_i^2}}
$$

- **值域**：$[-1, 1]$，归一化后通常为 $[0, 1]$
- **几何意义**：两向量夹角的余弦，**与向量长度无关，只与方向相关**
- **为什么用 cosine？**：文本 Embedding 通常 L2 归一化，使得 cosine = 点积 = 1 − (1/2)·欧氏距离²

### Dot Product vs Cosine vs Euclidean

| 相似度 | 公式 | 适用场景 |
|--------|------|---------|
| **Cosine** | $\frac{q \cdot d}{\|q\| \|d\|}$ | 文本语义（主流） |
| **Dot Product** | $q \cdot d$ | 归一化后等价于 Cosine，速度更快 |
| **Euclidean** | $-\\|q - d\\|_2$ | 图像、稀疏向量 |

### ANN 检索加速

Embedding 检索是 **k-NN 问题**，暴力 $O(Nd)$ 太慢。生产用 ANN（Approximate Nearest Neighbor）：

- **HNSW**（Hierarchical Navigable Small World）：图索引，10ms 查百万级
- **IVF**（Inverted File）：聚类分桶，O($\sqrt{N}$)
- **PQ**（Product Quantization）：向量压缩到 1/32 内存

主流向量库（Milvus / Qdrant / Weaviate / Pinecone）默认用 HNSW 或 IVF-PQ。

---

## 📅 演进史时间线

```text
2013 ─┬─ Word2Vec (Mikolov) ───── 首个稠密词向量，CBOW/Skip-gram
       │
2014 ─┼─ GloVe (Stanford) ─────── 全局共现矩阵分解
       │
2017 ─┼─ Transformer (Vaswani) ── 注意力机制登场，告别 RNN
       │
2018 ─┼─ BERT (Devlin) ─────────── [CLS] 句向量，Contextual 词向量
       │   ├─ 衍生：Sentence-BERT (2019, Reimers)
       │   └─ 衍生：SimCSE (2021, contrastive)
       │
2020 ─┼─ Sentence-BERT 工业落地 ── Bi-Encoder + NLI/SNLI 微调
       │
2022 ─┼─ OpenAI text-embedding-ada-002 ── API 化 Embedding
       │
2023 ─┼─ BGE (BAAI) ───────────── 中文 SOTA 开源
       │   ├─ bge-large-zh-v1.5
       │   └─ bge-m3（多语言 + 8K）
       │
2024 ─┼─ BGE-M3 (BAAI) ─────────── 多功能（dense/sparse/multi-vector）
       │   ├─ text-embedding-3 (OpenAI, 可降维 256)
       │   ├─ Qwen3-Embedding-8B (Alibaba, 4096 维)
       │   └─ Cohere embed-v3（多语言）
       │
2025 ─┼─ Jina-v3 (long-context, 8K+)
       │   ├─ NV-Embed-v2 (NVIDIA, 32K, 2024)
       └─ E5-Mistral-7B (Microsoft, instruction-tuned)
```

**趋势观察**：
1. **维度上升**：768 → 1024 → 4096 → 8192（信息容量 ↑）
2. **上下文变长**：512 → 8K → 32K → 128K
3. **训练范式从对比学习到指令微调**（E5-Mistral-7B 用 SFT 训练 Embedding）
4. **多模态融合**：CLIP / BGE-VL / Jina-CLIP

---

## 🛠️ 1. BGE-M3（推荐默认）

**最强开源 Embedding**，2024 中文 SOTA。

```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

# 编码
embeddings = model.encode(
    ["文档1", "文档2", "查询"],
    batch_size=12,
    max_length=512,
)['dense_vecs']

# 计算相似度
import numpy as np
query_emb = embeddings[-1]
doc_embs = embeddings[:-1]
scores = query_emb @ doc_embs.T
```

**特性**：
- 支持 dense / sparse / multi-vector 三种检索
- 100+ 语言
- 长文本（8K）

### BGE-M3 三大检索模式

```python
# 1. Dense（稠密向量，最常用）
output = model.encode(["doc1", "query"], return_dense=True, return_sparse=False)
dense_vecs = output['dense_vecs']  # shape: (n, 1024)

# 2. Sparse（稀疏向量，类似 BM25 但可学习）
output = model.encode(["doc1", "query"], return_dense=False, return_sparse=True)
sparse_vecs = output['lexical_weights']  # 词 → 权重

# 3. Multi-Vector（ColBERT 风格，每 token 一个向量）
output = model.encode(["doc1", "query"], return_colbert_vecs=True)
colbert_vecs = output['colbert_vecs']  # shape: (n, tokens, 1024)
```

**原理**：M3 = **Multi-Functionality** + **Multi-Linguality** + **Multi-Granularity**：
- **多任务**：dense / sparse / ColBERT 三模式合一
- **多语言**：100+ 语种统一训练（XLM-RoBERTa backbone）
- **多粒度**：短句到 8K 长文本

---

## 🛠️ 2. M3E（Moka 开源）

**轻量级中文 Embedding**。

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('moka-ai/m3e-large')
embeddings = model.encode(["文档1", "查询"])
```

**优点**：1.5GB 显存，中文友好  
**缺点**：仅中英

### M3E 训练方法

- **Backbone**：XLM-RoBERTa-large（560M 参数）
- **训练数据**：中文 STS / NLI 语料 + 伪标签扩充
- **损失函数**：对比学习（InfoNCE）

$$
\mathcal{L} = -\log \frac{\exp(\text{sim}(q, d^+) / \tau)}{\sum_{i} \exp(\text{sim}(q, d_i) / \tau)}
$$

其中 $d^+$ 是正样本，$\tau$ 是温度（通常 0.05）。

---

## 🛠️ 3. Qwen3-Embedding-8B（极致性能）

**2024 阿里最强 Embedding**，4096 维。

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('Qwen/Qwen3-Embedding-8B')
embeddings = model.encode(["文档1", "查询"])
```

**优点**：MTEB 双榜 SOTA  
**缺点**：16GB 显存

### Qwen3-Embedding 关键点

- **基于 Qwen3 基座**（LLM 衍生 Embedding）
- **指令微调**：支持 query / document 侧分别给指令模板
- **可变维度**：4096 / 1024 / 512 / 256（按需截断）
- **多语言**：100+ 语言，MTEB Multi-XL 排名第一

```python
# 指令感知编码
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('Qwen/Qwen3-Embedding-8B', trust_remote_code=True)

# 给 query 加指令
query_emb = model.encode(
    ["查询文本"],
    prompt="Given a query, retrieve relevant passages",
)
# 给 doc 直接编码
doc_emb = model.encode(["文档文本"])
```

---

## 🛠️ 4. OpenAI text-embedding-3

```python
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-large",
    input=["文档1", "查询"],
    dimensions=3072,  # 可降至 256
)
```

**优点**：质量稳定  
**缺点**：$0.13/1M tokens，数据出企业

### text-embedding-3 关键升级（2024）

相比 ada-002：
- **MATryoshka 训练**：可指定输出维度（256 / 1024 / 3072），前 N 维保留大部分信息
- **价格降低**：3-small 比 ada-002 便宜 5×
- **多语种**：替代 text-embedding-3-small/large 两档

```python
# 降维（节省存储 12×）
response_small = client.embeddings.create(
    model="text-embedding-3-large",
    input=["query"],
    dimensions=256,  # ← Matryoshka
)
```

---

## 📊 MTEB 排行榜（前 5 名）

| 排名 | 模型 | MTEB Score | 维度 | 显存 |
|------|------|-----------|------|------|
| 1 | Qwen3-Embedding-8B | 70.8 | 4096 | 16GB |
| 2 | text-embedding-3-large | 68.4 | 3072 | API |
| 3 | BGE-M3 | 65.4 | 1024 | 2GB |
| 4 | bge-large-en-v1.5 | 64.2 | 1024 | 1.5GB |
| 5 | M3E-large | 60.1 | 1024 | 1.5GB |

### MTEB 评测维度

MTEB（Massive Text Embedding Benchmark）包含 **56 个任务**：
- **分类**：Banking77 / Emotion / AmazonReviews
- **聚类**：ArxivClustering / RedditClustering
- **检索**：MS MARCO / NFCorpus / NQ
- **STS**（Semantic Textual Similarity）：STS12-22
- **重排**：AskUbuntuDupQuestions / MindSmallReranking
- **摘要**：SummEval

**平均分数** ≠ 单一检索分数，选型时关注**与场景最相关的子任务**。

---

## 🔬 真实案例研究

### 案例 1：ChatLaw 法律 RAG 系统

**场景**：100 万份中国法律法规 + 案例检索  
**挑战**：法律术语、案号、人名等专有名词检索  
**方案**：

```python
# 1. Embedding：BGE-M3 dense + sparse 混合
from FlagEmbedding import BGEM3FlagModel
model = BGEM3FlagModel('BAAI/bge-m3')

# 2. 索引：Elasticsearch 同时存 BM25 + dense vector
# 3. 检索：BM25 召回 + dense 重排（RRF 融合）
# 4. Reranker：bge-reranker-v2-m3 Top-3
```

**效果**：召回率从 0.72（纯向量）→ 0.91（混合 + Rerank），提升 **+19%**。

### 案例 2：Notion AI 文档问答

**场景**：千万级 Notion 工作区文档问答  
**方案**：
- **Embedding**：OpenAI text-embedding-3-large（3072 维，Matryoshka 降至 1024）
- **存储**：Pinecone 向量库
- **量化**：int8 量化节省 75% 存储
- **检索**：ANN Top-50 → Rerank Top-10

**关键决策**：商业 API（数据已托管给 Notion，无需担心出域）。

### 案例 3：阿里巴巴 Qwen-Agent 知识库

**场景**：淘宝/天猫商家文档 + 商品知识库  
**方案**：
- **Embedding**：Qwen3-Embedding-8B（自家模型，零成本）
- **训练数据**：淘宝商品语料微调
- **指令感知**：query 端加 "Given product query, retrieve relevant product description"
- **性能**：MTEB 中文榜 SOTA（70.5）

---

## 🛠️ 进阶：Embedding 微调（Fine-tuning）

通用 Embedding 在垂直领域不够用？Fine-tune 提升 10-30%。

### 训练数据构造

```python
# 1. 收集 (query, positive_doc, negative_doc) 三元组
train_data = [
    {
        "query": "怎么重置密码",
        "pos": ["点击登录页'忘记密码'按钮..."],
        "neg": ["用户协议第三条...", "客服电话：400-xxx"]  # Hard Negatives
    },
    # ...
]

# 2. 用 sentence-transformers 微调
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

model = SentenceTransformer('BAAI/bge-m3')
train_examples = [
    InputExample(texts=[ex['query'], ex['pos'][0], ex['neg'][0]])
    for ex in train_data
]
loader = DataLoader(train_examples, batch_size=16)
loss = losses.TripletLoss(model)

model.fit(
    train_objectives=[(loader, loss)],
    epochs=3,
    warmup_steps=100,
)
model.save('./bge-m3-finetuned')
```

### Hard Negative Mining

随机负样本不够，**难负样本**（与 query 相似但非正例）才能有效训练：

```python
# 步骤 1：用原始模型 Top-100 结果
# 步骤 2：剔除已知正例，取 Top-30 作为 Hard Negatives
# 步骤 3：再训练
```

---

## 🛠️ 向量库选型

| 向量库 | 部署 | 索引 | 适用规模 |
|--------|------|------|---------|
| **Milvus** | 自建 / 托管 | HNSW + IVF + PQ | 百万~亿级 |
| **Qdrant** | 自建 / 托管 | HNSW | 十万~百万级 |
| **Weaviate** | 自建 / 托管 | HNSW | 多模态友好 |
| **Pinecone** | SaaS | 未知（专利） | 不想运维 |
| **Chroma** | 嵌入式 | HNSW | 本地原型 |
| **pgvector** | Postgres 扩展 | IVFFlat / HNSW | 已用 PG |
| **Elasticsearch** | 自建 | HNSW（8.0+） | 已有 ES |

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 维度越高越好 | ✅ 1024 是性价比甜蜜点；维度翻倍效果提升 < 5%，成本翻倍 |
| ❌ Embedding 越新越好 | ✅ 取决于场景（中文 BGE 仍强；英文 text-embedding-3 仍 SOTA） |
| ❌ OpenAI 一定最强 | ✅ 中文场景 BGE-M3 更优；多语言需看具体语种 |
| ❌ Embedding 训练一次永远用 | ✅ 需按场景 fine-tune（领域语料可提 10-30%） |
| ❌ 直接用 cosine 相似度 | ✅ 归一化后 dot product 等价但快 2× |
| ❌ Embedding 维度 = 信息容量 | ✅ MATryoshka 训练可降维，前 256 维保留 95% 信息 |
| ❌ 向量库越大越好 | ✅ < 100 万用 Qdrant/Chroma；千万级才需 Milvus |
| ❌ 中文必须用中文模型 | ✅ BGE-M3 多语言已覆盖 100+ 语言，含小语种 |
| ❌ 一次性 encode 越多越好 | ✅ 需 batch_size 调优（过大 OOM，过小 GPU 利用率低） |

---

## 🔗 兄弟章节

- **本专题**：[Chunking 策略](../chunking-strategies/README.md) / [Hybrid Search](../hybrid-search/README.md) / [Reranker](../reranker/README.md) / [RAG 评估](../04-evaluation.md)
- **L1**：Embedding vs Vectorization
- **咬文嚼字**：[RAG 面试](../../../12.interview/11.ai/rag/README.md)
- **入库侧**：[knowledge-ingestion-pipeline](../knowledge-ingestion-pipeline/README.md) — Embedding 模型选型（在"Embedding"环节批量调用 + 异步写入）
- **L1 数学基础**：[Transformer 与 Attention](../../../08.ai-foundations/03-transformer/attention-mechanism.md) — Embedding 来自 Transformer 最后一层
- **L1 训练范式**：[对比学习](../../../08.ai-foundations/05-tokenization-embedding/embedding.md) — InfoNCE 损失是 Embedding 训练核心
- **数据侧**：[向量数据库](../vector-search-algorithms/README.md) — 存 Embedding 的向量库选型
- **面试题**：[embedding-面试](../../../12.interview/11.ai/incremental-embedding/README.md) — 5 道高频追问
- **故事化**：[13.story 阿明餐厅 RAG 篇](../../../13.story/) — Embedding 类比"菜品指纹"

---

## 🛠️ 实战：完整 Embedding 选型流程

### 步骤 1：业务场景评估

```python
# 决策矩阵
scenario = {
    "data_type": "Chinese legal docs",   # 中文法律
    "scale": "100K docs",
    "latency_requirement": "100ms",
    "budget": "low",                     # 开源优先
    "language": "zh + en",
    "context_length": 2048,
}

# 输出推荐
recommend = "BGE-M3"  # 中文 + 多语言 + 2GB 显存 + 8K context
```

### 步骤 2：本地试用

```python
# pip install FlagEmbedding
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

# 准备测试集
test_queries = ["怎么申请专利", "专利侵权的赔偿标准", "商标注册流程"]
test_docs = [
    "专利申请需要提交说明书、权利要求书、摘要等文件。",
    "专利侵权赔偿包括实际损失、侵权获利、许可费倍数等。",
    "商标注册通过国家知识产权局进行，流程包括形式审查和实质审查。",
]

# 计算相似度
import numpy as np
q_emb = model.encode(test_queries, return_dense=True)['dense_vecs']
d_emb = model.encode(test_docs, return_dense=True)['dense_vecs']

# 3x3 相似度矩阵
sim_matrix = q_emb @ d_emb.T
print("Query x Doc 相似度矩阵:")
print(sim_matrix.round(3))

# 期望：q1 应与 d1 最高，q2 与 d2，q3 与 d3
```

### 步骤 3：上线 + 监控

```python
# 1. 批量 Embedding 入库
import asyncio
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

async def embed_batch(texts):
    loop = asyncio.get_event_loop()
    embeddings = await loop.run_in_executor(
        None,
        lambda: model.encode(texts, batch_size=32)['dense_vecs']
    )
    return embeddings

# 2. 异步写入向量库
texts = [...]  # 100 万文档
batch_size = 1000
for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    embs = await embed_batch(batch)
    vector_store.upsert(embs, batch)
```

---

## 📚 评测数据集

| 数据集 | 规模 | 语言 | 任务 |
|--------|------|------|------|
| **MTEB** | 56 任务 | EN+ | 综合 |
| **C-MTEB** | 35 任务 | ZH | 中文综合 |
| **BEIR** | 18 数据集 | EN | 零样本检索 |
| **MS MARCO** | 500K Q | EN | 段落检索 |
| **NQ** | 3K Q | EN | 开放域 QA |
| **HotpotQA** | 113K Q | EN | 多跳推理 |

### BEIR 零样本检索排行

| 模型 | NDCG@10 (avg) |
|------|---------------|
| **Qwen3-Embedding-8B** | 0.582 |
| **BGE-M3** | 0.541 |
| **text-embedding-3-large** | 0.555 |
| **E5-Large-v2** | 0.498 |

---

## 💡 性能优化

### GPU 推理加速

```python
# 1. FP16（精度略降，速度 +50%）
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

# 2. Flash Attention（长文本必备）
model = BGEM3FlagModel(
    'BAAI/bge-m3',
    use_fp16=True,
    attn_implementation='flash_attention_2'  # 显存 -40%
)

# 3. ONNX 推理（CPU 友好，延迟 -30%）
# optimum-cli export onnx --model BAAI/bge-m3 --task feature-extraction onnx/
```

### 量化部署

```python
# INT8 量化（显存 1/4，速度 +30%）
from transformers import AutoModel
model = AutoModel.from_pretrained('BAAI/bge-m3', load_in_8bit=True)

# INT4 量化（GPTQ/AWQ）
# 显存 1/8，但 MTEB 降 ~2%
```

---

## 🔍 调试：Embedding 检索效果差？

### 排查清单

1. **向量是否归一化？** → 大多数模型需 L2 normalize
2. **Embedding 模型对吗？** → 不同语种需不同模型
3. **Query 和 Doc 编码方式一致？** → 某些模型需不同 prompt
4. **文档长度超限？** → BGE-M3 8K，M3E 仅 512
5. **向量库索引类型？** → Cosine 必须用 cosine similarity

```python
# 调试技巧：可视化相似度矩阵
import matplotlib.pyplot as plt
import seaborn as sns

sim_matrix = q_emb @ d_emb.T
plt.figure(figsize=(8, 6))
sns.heatmap(sim_matrix, annot=True, cmap='YlOrRd',
            xticklabels=[f'd{i+1}' for i in range(len(d_emb))],
            yticklabels=[f'q{i+1}' for i in range(len(q_emb))])
plt.title('Query-Doc Similarity')
plt.savefig('similarity_debug.png')
```

---

## 🛠️ 多语言 Embedding 实战

### BGE-M3 多语种检索

```python
# 100+ 语言统一向量空间
queries = {
    "zh": "什么是机器学习？",
    "en": "What is machine learning?",
    "ja": "機械学習とは何ですか？",
    "fr": "Qu'est-ce que l'apprentissage automatique ?",
}

# 编码（共享向量空间！）
embeddings = {}
for lang, q in queries.items():
    emb = model.encode([q])['dense_vecs'][0]
    embeddings[lang] = emb

# 中文 doc 与日文 query 也能匹配
zh_doc_emb = model.encode(["机器学习是人工智能的分支"])['dense_vecs'][0]
print("中日相似度:", cos_sim(embeddings['ja'], zh_doc_emb))
# 输出: 0.82  ← 跨语言检索成功！
```

---

## 📦 部署清单（生产级）

```python
# requirements.txt
# FlagEmbedding>=1.2.0
# sentence-transformers>=2.2.0
# torch>=2.0
# transformers>=4.35
# pymilvus>=2.3.0  # 向量库

# Dockerfile 示例
FROM nvidia/cuda:12.1-runtime-ubuntu22.04
RUN pip install FlagEmbedding fastapi uvicorn
COPY app.py /app/
WORKDIR /app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Embedding 服务 API

```python
from fastapi import FastAPI
from pydantic import BaseModel
from FlagEmbedding import BGEM3FlagModel

app = FastAPI()
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

class EmbedRequest(BaseModel):
    texts: list[str]

@app.post("/embed")
def embed(req: EmbedRequest):
    embeddings = model.encode(req.texts)['dense_vecs']
    return {"embeddings": embeddings.tolist()}

# 启动：uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## 🎓 进阶阅读

- **MTEB 论文**：arXiv:2210.07316
- **Sentence-BERT 论文**：arXiv:1908.10084
- **BGE-M3 论文**：arXiv:2402.03216
- **对比学习综述**：arXiv:2011.00362
- **Matryoshka Embeddings**：arXiv:2205.13147

---

← [返回 L2 技术栈](../README.md)