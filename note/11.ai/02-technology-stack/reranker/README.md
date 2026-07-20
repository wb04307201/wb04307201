<!--
module:
  parent: ai
  slug: ai/reranker
  type: article
  category: 主模块子文章
  summary: Cross-Encoder Reranker 重排序
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

---

## 📊 提升效果

| 任务 | 仅向量 | 向量 + Rerank | 提升 |
|------|--------|--------------|------|
| HotpotQA | 0.68 | 0.82 | +14% |
| Natural Questions | 0.72 | 0.85 | +13% |
| 中文 RAG | 0.65 | 0.80 | +15% |
| Code Search | 0.55 | 0.75 | +20% |

---

## 🔗 兄弟章节

- **本专题**：[Hybrid Search](../hybrid-search/README.md) / [Embedding 模型](../embedding-models/README.md) / [RAG 评估](../../08-llmops/agent-evaluation/09-rag-evaluation/README.md)
- **咬文嚼字**：[RAG 面试](../../../13.split-hairs/11.ai/rag/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ Reranker 一定大幅提升 | ✅ 中等场景 +5-10% |
| ❌ Reranker 替代向量检索 | ✅ 是补充，需向量先召回 |
| ❌ Reranker 越贵越好 | ✅ BGE-reranker 已足够 80% 场景 |
| ❌ Reranker 越多越好 | ✅ Top-100 → Top-10 即可 |

← [返回 L2 技术栈](../README.md)