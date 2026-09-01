<!--
module:
  parent: ai
  slug: ai/reranker
  type: article
  category: 主模块子文章
  summary: Cross-Encoder Reranker 重排序
  depth: ⭐⭐⭐⭐⭐
-->

# Reranker（重排序模型）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：Reranker = **Cross-Encoder 深度理解 query-document 关系**，**比向量检索精确率高 15-30%**。BGE-reranker / Cohere Rerank 是 2024 SOTA。

---

## 🎯 Bi-Encoder vs Cross-Encoder

**Bi-Encoder（向量检索）**：
```text
Query ─┐
       ├─→ [各自 Embedding] → [余弦相似度]
Doc  ──┘
```
- 优点：可预计算 + 快速 ANN 检索
- 缺点：query 和 doc 独立编码，**没看到彼此**

**Cross-Encoder（Reranker）**：
```text
Query ─┐
       ├─→ [联合 BERT] → [相关性分数 0-1]
Doc  ──┘
```
- 优点：query 和 doc **联合编码**，精确度高
- 缺点：不能预计算，每次查询都要重算

**最佳实践**：Bi-Encoder 召回 Top-100 + Cross-Encoder Rerank Top-10

---

## 📐 核心原理与公式

### Cross-Encoder 推理过程

1. **拼接**：构造 `[CLS] query [SEP] doc [SEP]` 输入
2. **联合编码**：BERT/RoBERTa 编码整个输入
3. **分类头**：`[CLS]` 向量 → Linear → Sigmoid → 相关性分数 $s \in [0, 1]$

### 训练目标

Cross-Encoder 用二分类损失训练：

$$
\mathcal{L}_{CE} = -\frac{1}{N} \sum_{i=1}^{N} \left[ y_i \log \sigma(s_i) + (1-y_i) \log (1-\sigma(s_i)) \right]
$$

- $s_i$：Cross-Encoder 输出分数
- $y_i \in \{0, 1\}$：标签（1 相关，0 不相关）
- $\sigma$：Sigmoid 函数

### 训练数据构造（Pair-wise + Hard Negatives）

```python
# 1. 收集正样本对
positive_pairs = [(q, d_pos) for q, d_pos in zip(queries, gold_docs)]

# 2. Hard Negative Mining（用 Bi-Encoder 检索 Top-50，剔除正例后随机抽 5 个）
hard_negatives = []
for q, d_pos in positive_pairs:
    candidates = bi_encoder.search(q, k=50)
    negatives = [c for c in candidates if c.id != d_pos.id][:5]
    hard_negatives.extend([(q, n) for n in negatives])

# 3. 训练
all_pairs = positive_pairs + hard_negatives
labels = [1] * len(positive_pairs) + [0] * len(hard_negatives)
```

**Hard Negative Mining 关键**：随机负样本太容易（模型已区分），Hard Negatives 才是真正的提升点。

### Bi-Encoder vs Cross-Encoder 数学对比

| 维度 | Bi-Encoder | Cross-Encoder |
|------|-----------|---------------|
| **推理复杂度** | $O(N \cdot d)$ 预计算 + $O(\log N)$ ANN | $O(N \cdot L^2)$ 重算 |
| **精确度** | 中 | 高（+15-30%） |
| **适用规模** | 千万级 | 千级（Top-100 内） |
| **可更新性** | doc 改了重 Embed 即可 | 必须重算 |

---

## 📅 演进史时间线

```text
2018 ── BERT (Devlin) ──────────── Cross-Encoder 登场
       ├─ monoBERT (Nogueira) ──── 首个 BERT Reranker
       │
2019 ── monoT5 (Nogueira) ─────── T5 序列到分数
       │
2020 ── Sentence-BERT ────────── Bi-Encoder 简化推理（不是 Reranker）
       │
2021 ── ColBERT (Khattab) ─────── 多向量延迟交互
       │
2022 ── Cohere Rerank English v2 ── 商业 API 化
       │
2023 ── BGE-reranker-large (BAAI) ── 中文 SOTA 开源
       │
2024 ── BGE-reranker-v2-m3 ───── 多语言 Reranker
       ├─ Cohere Rerank v3 ──────── 多语种 + 长文档
       ├─ Jina Reranker (Jina AI) ── 8K context
       ├─ mxbai-rerank-large ────── Mixtral 衍生
       │
2025 ── Qwen3-Reranker ────────── LLM-as-Reranker 兴起
       └─ RankT5 (Google) ───────── Listwise 训练
```

**关键范式转变**：
1. **Pointwise**（2018）：单 (q, d) 评分
2. **Pairwise**（2020）：(q, d1) vs (q, d2) 比较
3. **Listwise**（2024）：一次评所有候选（如 RankT5）

---

## 📊 主流 Reranker 对比

| 模型 | 参数量 | 速度 | MTEB Reranking | 显存 |
|------|--------|------|---------------|------|
| **BGE-reranker-v2-m3** | 568M | 中 | 65.4 | 2GB |
| **Cohere Rerank-3** | - | 快 | 67.1 | API |
| **Jina Reranker** | 278M | 中 | 64.3 | 1GB |
| **mxbai-rerank-large** | 1.5B | 慢 | 66.5 | 6GB |

**BGE-reranker-v2-m3** 是中文 SOTA + 开源首选。

---

## 🛠️ 1. BGE-reranker

```python
from FlagEmbedding import FlagReranker

reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)

# 输入：query + 文档列表
scores = reranker.compute_score([
    ("query", "doc 1"),
    ("query", "doc 2"),
    ("query", "doc 3"),
])
# [0.92, 0.45, 0.78]
```

**输出**：每个 (query, doc) 对的相关性分数 0-1。

### BGE-reranker-v2-m3 详解

- **Backbone**：XLM-RoBERTa-large
- **参数量**：568M
- **多语言**：100+ 语种
- **输入长度**：512 token（query + doc 拼接）
- **MTEB Reranking**：65.4（2024 年 6 月）

---

## 🛠️ 2. Cohere Rerank 3（云端）

```python
import cohere
co = cohere.Client('api_key')

results = co.rerank(
    query="query",
    documents=["doc 1", "doc 2", "doc 3"],
    top_n=3,
    model="rerank-english-v3.0",
)
# 返回 Top-3 文档 + 分数
```

**优点**：质量高  
**缺点**：$2/1K queries

### Cohere Rerank 3 关键特性

- **多语种**：r3.0 支持英/日/中/法/德/西/葡/韩
- **长文档**：8K context
- **Listwise 训练**：比 v2.0 提升 ~15%
- **延迟**：~200ms（100 docs）

---

## 🛠️ 3. vLLM + 自研 Cross-Encoder

```python
from vllm import LLM, SamplingParams

llm = LLM(model="your-reranker-model")
sampling = SamplingParams(max_tokens=1)

prompts = [
    f"Query: {q}\nDoc: {d}\nRelevance (0-1):"
    for q, d in pairs
]
scores = llm.generate(prompts, sampling)
```

### vLLM 加速优势

- **PagedAttention**：KV Cache 分页，GPU 利用率 90%+
- **Continuous Batching**：动态批大小，吞吐 24× 提升
- **Speculative Decoding**：小模型草稿，大模型验证
- 适用：自研 Reranker、LLM-as-Reranker

---

## 🛠️ 4. Jina Reranker（长上下文 8K）

```python
# pip install jina
import requests

url = "https://api.jina.ai/v1/rerank"
headers = {
    "Authorization": f"Bearer {JINA_API_KEY}",
    "Content-Type": "application/json",
}
data = {
    "model": "jina-reranker-v2-base-multilingual",
    "query": "query text",
    "documents": ["doc 1", "doc 2", "doc 3"],
    "top_n": 3,
}

response = requests.post(url, headers=headers, json=data)
results = response.json()["results"]
```

**Jina Reranker 优势**：
- **8K context**（vs BGE 512）
- **多语种**：100+ 语种
- **开源**：jina-reranker-v2-base-multilingual（278M）

---

## 📐 RAG 中典型应用

```python
from langchain.vectorstores import Milvus
from FlagEmbedding import BGEM3FlagModel, FlagReranker

# Step 1: 向量检索 Top-100
vector_results = vector_store.similarity_search(query, k=100)

# Step 2: Reranker 重排
pairs = [(query, doc.page_content) for doc in vector_results]
rerank_scores = reranker.compute_score(pairs)

# Step 3: 取 Top-10
top_10 = sorted(zip(vector_results, rerank_scores), 
                 key=lambda x: -x[1])[:10]

# Step 4: 喂给 LLM
context = "\n".join([doc.page_content for doc, _ in top_10])
answer = llm.generate(f"Context: {context}\nQ: {query}\nA:")
```

### 二阶段 vs 三阶段流水线

```text
两阶段（推荐）：
Bi-Encoder Top-100 → Cross-Encoder Top-10 → LLM

三阶段（极致）：
Bi-Encoder Top-500 → Cross-Encoder Top-50 → LLM Rerank Top-10
                    ↑ 大规模召回              ↑ 轻量 LLM 重排
```

---

## 📊 提升效果

| 任务 | 仅向量 | 向量 + Rerank | 提升 |
|------|--------|--------------|------|
| HotpotQA | 0.68 | 0.82 | +14% |
| Natural Questions | 0.72 | 0.85 | +13% |
| 中文 RAG | 0.65 | 0.80 | +15% |
| Code Search | 0.55 | 0.75 | +20% |
| BEIR (avg) | 0.61 | 0.78 | +17% |
| TREC-COVID | 0.71 | 0.91 | +20% |

---

## 🔬 真实案例研究

### 案例 1：阿里巴巴电商搜索

**场景**：淘宝商品搜索（10 亿商品）  
**方案**：

```python
# 阶段 1：Bi-Encoder Top-1000（向量库召回）
vector_results = dasheng.search(query, k=1000)

# 阶段 2：Cross-Encoder Rerank Top-50
reranked = bge_reranker(query, vector_results, top_k=50)

# 阶段 3：业务层（CTR 模型）Top-10
final = ctr_model(reranked)[:10]
```

**效果**：
- 仅向量：CTR = 4.2%
- 向量 + Reranker：CTR = 5.6%（+33%）
- **关键**：Reranker 抓"用户真实意图"（如"夏季透气运动鞋" → 语义匹配）

### 案例 2：Elasticsearch RAG + Rerank

**场景**：企业内部知识库问答  
**方案**：

```python
# ES 8.13+ 原生 RRF + Reranker
response = es.search(
    index="knowledge_base",
    body={
        "query": {"match": {"content": query}},
        "knn": {
            "field": "embedding",
            "query_vector": query_emb,
            "k": 100,
            "num_candidates": 500,
        },
        "rank": {"rrf": {"window_size": 100, "k": 60}},
    }
)

# 外部 Reranker（bge-reranker）
top_100 = [hit["_source"] for hit in response["hits"]["hits"]]
reranked = bge_reranker(query, top_100, top_k=10)
```

**效果**：召回率 0.72 → 0.88（+16%）

### 案例 3：Notion AI 文档问答

**场景**：千万级 Notion 工作区  
**方案**：
- 召回：OpenAI text-embedding-3-large + BM25（混合 RRF）
- Rerank：**Cohere Rerank-3**（云端 API）
- 最终：取 Top-10 喂给 GPT-4

**关键决策**：用云端 API（Notion 数据已托管 SaaS，无隐私顾虑），质量优先。

---

## 🛠️ 进阶：LLM-as-Reranker

用大模型自身当 Reranker，免训练：

```python
# GPT-4 / Claude 作 Reranker
def llm_rerank(query, docs, llm):
    prompt = f"""Rate the relevance of each doc to the query on 0-5 scale.

Query: {query}

Docs:
{chr(10).join(f'{i+1}. {doc}' for i, doc in enumerate(docs))}

Output format: JSON list of scores in order."""
    
    response = llm.generate(prompt)
    scores = json.loads(response)
    return sorted(zip(docs, scores), key=lambda x: -x[1])
```

**优点**：零训练  
**缺点**：慢（每次 ~1s）、贵（$0.03/1K docs）、不稳定

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ Reranker 一定大幅提升 | ✅ 中等场景 +5-10%；极简单场景可能反向（过拟合） |
| ❌ Reranker 替代向量检索 | ✅ 是补充，需向量先召回；Reranker 算 Top-100 内还行 |
| ❌ Reranker 越贵越好 | ✅ BGE-reranker-v2-m3 已足够 80% 场景；Cohere 仅在长文/多语种占优 |
| ❌ Reranker 越多越好 | ✅ Top-100 → Top-10 即可；Top-1000 算力浪费 |
| ❌ Reranker = Cross-Encoder | ✅ Cross-Encoder 是主流，但还有 LLM-as-Reranker / Listwise 等 |
| ❌ BGE-reranker 比 Cohere 差 | ✅ 中文 BGE 更优；英文 Cohere v3 更优；多语种持平 |
| ❌ Reranker 不能用 vLLM 加速 | ✅ vLLM 自定义 prompt + logprob 可作 Reranker（实验性） |
| ❌ Reranker 训练无需数据 | ✅ 需 (q, d+, d-) 三元组 + Hard Negative Mining |
| ❌ Reranker 分数可直接比较 | ✅ 不同 Reranker 分数尺度不同（如 BGE 0-1，Cohere -1~1），不可跨模型对比 |

---

## 🔗 兄弟章节

- **本专题**：[Hybrid Search](../hybrid-search/README.md) / [Embedding 模型](../embedding-models/README.md) / [RAG 评估](../04-evaluation.md)
- **咬文嚼字**：[RAG 面试](../../../12.interview/11.ai/rag/README.md)
- **L1 数学基础**：[Cross-Encoder 训练](../../../08.ai-foundations/03-transformer/attention-mechanism.md) — BERT 微调原理
- **进阶**：LLM-as-Judge — Reranker 的另一种实现
- **工业实践**：Cohere Rerank 实战 — 商业 API 集成
- **面试题**：[reranker-面试](../../../12.interview/11.ai/vector-search-at-scale/README.md) — 5 道高频追问
- **故事化**：[13.story 阿明餐厅 RAG 篇](../../../13.story/) — Reranker 类比"老厨师品鉴打分"

---

## 📐 深度：Pairwise vs Listwise 训练

### Pointwise（默认 BGE / Cohere）

每个 (q, d) 对独立打分，二分类：

$$
\mathcal{L}_{pointwise} = -\frac{1}{N} \sum_{i} \left[ y_i \log \sigma(s_i) + (1-y_i) \log (1-\sigma(s_i)) \right]
$$

### Pairwise（RankNet / LambdaRank）

两个 (q, d1, d2) 一起训练，d1 应比 d2 分数高：

$$
\mathcal{L}_{pairwise} = \sum_{(d^+, d^-)} \max(0, \text{margin} - (s^+ - s^-))
$$

### Listwise（ListNet / ListMLE）

整个候选列表一起训练，目标函数：

$$
\mathcal{L}_{listwise} = -\sum_{d \in D} P^*(d | q) \log P(d | q)
$$

其中 $P^*$ 是真实排序概率，$P$ 是模型预测概率。

**对比**：

| 方法 | 优点 | 缺点 | 代表 |
|------|------|------|------|
| **Pointwise** | 简单稳定 | 忽略相对关系 | BGE-reranker |
| **Pairwise** | 学习相对顺序 | 忽略全局 | RankNet |
| **Listwise** | 全局最优 | 训练复杂 | RankT5, Cohere v3 |

---

## 🛠️ 实战：RankT5 / Listwise 训练

### RankT5 原理（Google 2023）

用 T5 生成排序后的文档列表：

```python
# 输入
input_text = f"Query: {q}\nDocs: {docs}\nRerank by relevance."

# 输出（按相关性降序的 doc 编号列表）
target_text = "3 1 4 2 5"  # doc 3 最相关，doc 5 最不相关

# 训练（监督微调）
loss = cross_entropy(model(input_text), target_text)
```

**优点**：一次评所有候选（不像 pointwise 一个个算）  
**缺点**：推理时仍需 beam search 生成列表

---

## 🔬 真实案例研究（续）

### 案例 4：Hugging Face Chat Reranker

**场景**：Hugging Chat 内部 RAG 系统  
**配置**：
- 召回：bge-large-en-v1.5（ANN Top-50）
- Reranker：**bge-reranker-large**（开源）
- LLM：Mistral-7B
- **效果**：NDCG@10 0.71 → 0.83（+12%）

### 案例 5：百度文心 ERNIE Rerank

**场景**：百度搜索问答  
**方案**：
- 召回：ERNIE Embedding
- Reranker：自研 ERNIE-Rerank
- 关键优化：**Pairwise 训练 + 蒸馏**（用 GPT-4 生成 pair 标签）

### 案例 6：Stack Overflow 代码搜索

**场景**：代码片段搜索  
**挑战**：变量名、函数名专有名词  
**方案**：
- BM25 + CodeBERT Bi-Encoder（混合 RRF）
- Reranker：**CodeBERT Cross-Encoder**
- 微调数据：100K Stack Overflow QA pairs

**效果**：
- 仅 BM25：MRR = 0.55
- BM25 + Dense：MRR = 0.68
- BM25 + Dense + Rerank：**MRR = 0.81**（+47%）

---

## 🛠️ 进阶：自训练 Reranker

### 完整训练 Pipeline

```python
from FlagEmbedding import FlagReranker, FlagModel
from torch.utils.data import DataLoader
import torch.nn as nn

# 1. 准备数据（query, positive, negative）
train_data = [
    {
        "query": "如何重置密码",
        "positives": ["点击登录页'忘记密码'按钮..."],
        "negatives": ["客服电话：400-xxx", "用户协议..."]
    },
    # ...
]

# 2. Hard Negative Mining（用 Bi-Encoder 检索）
bi_encoder = FlagModel('BAAI/bge-m3')
all_hard_negatives = []
for sample in train_data:
    # 检索 Top-100
    candidates = bi_encoder.encode(sample["positives"])
    query_emb = bi_encoder.encode([sample["query"]])
    scores = (query_emb @ candidates.T).flatten()
    
    # 取 Top-10 排除正例后随机选 5
    top_indices = scores.argsort()[-10:][::-1]
    hard_negs = [sample["positives"][i] for i in top_indices 
                  if i not in [sample["positives"].index(p) for p in sample["positives"]]][:5]
    all_hard_negatives.extend(hard_negs)

# 3. 训练数据构造
train_pairs = []
for sample, hard_negs in zip(train_data, all_hard_negatives):
    for pos in sample["positives"]:
        train_pairs.append({
            "query": sample["query"],
            "doc": pos,
            "label": 1
        })
    for neg in hard_negs:
        train_pairs.append({
            "query": sample["query"],
            "doc": neg,
            "label": 0
        })

# 4. 微调 Reranker
reranker = FlagReranker('BAAI/bge-reranker-v2-m3')
loader = DataLoader(train_pairs, batch_size=16)

optimizer = torch.optim.AdamW(reranker.model.parameters(), lr=2e-5)
for epoch in range(3):
    for batch in loader:
        scores = reranker.compute_score(
            list(zip(batch["query"], batch["doc"]))
        )
        loss = F.binary_cross_entropy(
            torch.tensor(scores),
            torch.tensor(batch["label"], dtype=torch.float)
        )
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

# 5. 保存
reranker.save("./bge-reranker-finetuned")
```

---

## 📊 Reranker 选型决策树

```text
Q1: 是否需要多语言？
├── 仅中文 → BGE-reranker-v2-m3（性价比最高）
├── 中英 → BGE-reranker-v2-m3 / Cohere v3
└── 多语种 → Cohere v3 / Jina Reranker

Q2: 数据隐私？
├── 不能出域 → BGE / Jina（开源）
└── 可出域 → Cohere（云端）

Q3: 上下文长度？
├── < 512 → BGE / mxbai（标准）
├── 512-8K → Jina Reranker（8K）
└── > 8K → LLM-as-Reranker

Q4: 成本？
├── 紧 → BGE / Jina（自托管）
└── 充足 → Cohere v3（$2/1K queries）

Q5: 极致精度？
├── 标准 → BGE-reranker-v2-m3
└── 极致 → mxbai-rerank-large + 蒸馏
```

---

## 🛠️ 性能优化：批量推理

```python
# FlagReranker 默认支持 batch
reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)

# ❌ 错误：逐条算（100 次 forward）
for query, doc in pairs:
    score = reranker.compute_score([(query, doc)])[0]

# ✅ 正确：批量推理
scores = reranker.compute_score(pairs, batch_size=64)
# 一次 forward 处理 64 对，速度提升 ~10×
```

### ONNX / vLLM 加速

```python
# ONNX 推理（CPU 友好）
from optimum.onnxruntime import ORTModelForSequenceClassification

model = ORTModelForSequenceClassification.from_pretrained(
    'BAAI/bge-reranker-v2-m3',
    export=True,
)
# CPU 上推理比 PyTorch 快 ~2×

# vLLM 加速（GPU，LLM-as-Reranker 场景）
from vllm import LLM, SamplingParams

llm = LLM(model="your-reranker-model")
# PagedAttention + Continuous Batching
```

---

## 📊 工业级指标参考

| 场景 | 召回→Rerank 提升 | Rerank 延迟 | 单 query 成本 |
|------|------------------|-------------|--------------|
| **通用 RAG（中文）** | +15% | 200ms (50 docs) | $0.001 |
| **电商搜索** | +33% CTR | 150ms (100 docs) | $0.005 |
| **法律检索** | +20% | 300ms (50 docs) | $0.002 |
| **代码搜索** | +20% MRR | 250ms (50 docs) | $0.003 |
| **学术论文** | +12% NDCG | 200ms (100 docs) | $0.002 |

---

## 🎓 进阶阅读

- **monoBERT**：Nogueira et al., 2019
- **Sentence-BERT**：Reimers & Gurevych, 2019
- **Cohere Rerank**：cohere.com/rerank
- **RankT5**：arXiv:2310.08324
- **BGE-reranker-v2**：huggingface.co/BAAI/bge-reranker-v2-m3

---

← [返回 L2 技术栈](../README.md)