<!--
module:
  parent: ai
  slug: ai/hybrid-search
  type: article
  category: 主模块子文章
  summary: 向量 + BM25 混合检索
-->

# Hybrid Search（混合检索）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：Hybrid Search = **向量检索（语义）+ BM25（关键词）融合**，**召回率比单一方案高 15-25%**。RAG 生产环境标配。

---

## 🎯 为什么需要混合

**向量检索弱项**：
- ❌ 专有名词（人名、产品名）召回差
- ❌ 罕见词（专业术语）召回差
- ❌ 完全相同字面无相似语义时（如"Apple"公司 vs 苹果）

**BM25 弱项**：
- ❌ 同义词（"汽车" / "车" / "vehicle"）召回差
- ❌ 语义相关但用词不同时召回差

**混合 = 互补**：

```
向量得分：semantic_similarity(query, doc)
BM25 得分：keyword_match(query, doc)
最终得分：α * 向量得分 + (1 - α) * BM25 得分
```

---

## 📐 主流融合算法

### 1. 加权融合（Weighted Sum）

```python
final_score = α * vector_score + (1 - α) * bm25_score
# α = 0.5-0.7（向量权重略高）
```

**优点**：简单  
**缺点**：分数尺度差异需归一化

### 2. Reciprocal Rank Fusion（RRF）

```python
def rrf(vector_results, bm25_results, k=60):
    scores = {}
    for rank, doc_id in enumerate(vector_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    for rank, doc_id in enumerate(bm25_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])
```

**优点**：不需归一化  
**缺点**：k 值需调

### 3. Cross-Encoder Re-ranking

见 [Reranker 章节](../reranker/README.md)

---

## 🛠️ Elasticsearch + 向量混合

```python
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

es = Elasticsearch()
model = SentenceTransformer('BAAI/bge-m3')

# 1. 索引
docs = [
    {"id": 1, "content": "...", "vector": model.encode("...")},
]
for doc in docs:
    es.index(index="my_index", body=doc)

# 2. 查询
query = "..."
query_vec = model.encode(query)

response = es.search(
    index="my_index",
    body={
        "query": {
            "bool": {
                "should": [
                    {"match": {"content": query}},  # BM25
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                                "params": {"query_vector": query_vec.tolist()}
                            }
                        }
                    }
                ]
            }
        }
    }
)
```

---

## 📊 混合 vs 单一对比

| 方案 | 召回率 | 精确率 | 速度 |
|------|--------|--------|------|
| 仅向量 | 0.78 | 0.72 | 50ms |
| 仅 BM25 | 0.72 | 0.75 | 5ms |
| **混合 (RRF)** | **0.88** | **0.80** | 55ms |
| **混合 + Rerank** | **0.92** | **0.88** | 200ms |

**结论**：混合 + Rerank 是 SOTA。

---

## 🔗 兄弟章节

- **本专题**：[Embedding 模型](../embedding-models/README.md) / [Chunking](../chunking-strategies/README.md) / [Reranker](../reranker/README.md) / [RAG 评估](../../../06-agent-evaluation/09-rag-evaluation/README.md)
- **L1**：[Lost in middle](../lost-in-middle/README.md)
- **咬文嚼字**：[RAG 面试](../../../../../13.split-hairs/11.ai/rag/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 向量检索已足够 | ✅ 专有名词场景仍弱 |
| ❌ 混合一定更好 | ✅ 需调权重 + 选融合算法 |
| ❌ BM25 已过时 | ✅ 与向量互补，仍是基础 |
| ❌ 混合一定慢 | ✅ RRF 仅 5-10ms 额外开销 |

← [返回 L2 技术栈](../README.md)