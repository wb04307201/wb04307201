<!--
module:
  parent: ai
  slug: ai/query-rewrite
  type: article
  category: 主模块子文章
  summary: Query Rewrite 查询改写提升 RAG 召回
-->

# Query Rewrite（查询改写）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：Query Rewrite = **用 LLM 把用户口语化/不完整 query 改写成清晰检索 query**，**RAG 召回率提升 10-20%**。特别适合多轮对话和模糊问题。

---

## 🎯 为什么需要 Query Rewrite

**问题 1：用户口语化**

```
原始："那个能查 bug 的工具怎么用？"
改写："如何排查系统 bug？有什么工具？"
```

**问题 2：指代消解（多轮对话）**

```
Turn 1: "Python 怎么读取 CSV？"
Turn 2: "那 JSON 呢？"  ← 需要理解为 "JSON 怎么读取？"
```

**问题 3：检索 query 太长**

```
原始："我想知道关于 LLM 在生产环境部署的最佳实践，特别是 vLLM 和量化方面"
改写："LLM 生产部署 vLLM 量化"
```

---

## 📊 4 大改写策略

### 1. 直接改写

```python
rewrite_prompt = """将用户问题改写为适合检索的清晰 query。
保留核心意图，去除口语化。

原 query：{query}
改写后："""
rewritten = llm.generate(rewrite_prompt)
```

**适用**：单轮对话

### 2. 多轮融合（带上下文）

```python
rewrite_prompt = """根据对话历史，将当前问题改写为独立的检索 query。

历史：
  Turn 1: Python 怎么读取 CSV？
  Turn 2: 那 JSON 呢？

改写后：Python 怎么读取 JSON 文件？
"""
```

**适用**：多轮对话

### 3. HyDE（Hypothetical Document Embeddings）

```python
# 1. 让 LLM 生成"假设的答案"
hyde_doc = llm.generate(f"问题：{query}\n假设的答案：")

# 2. 用假设答案做 Embedding 检索
hyde_emb = embedding_model.encode(hyde_doc)
results = vector_store.similarity_search_by_vector(hyde_emb)
```

**核心洞察**：答案和答案相似度 > 问题和问题相似度

**适用**：问题简短、答案丰富的场景

### 4. Multi-Query（多角度查询）

```python
# 1. LLM 生成 3-5 个改写
queries = llm.generate(f"对问题生成 3 种不同表述：\n{query}")

# 2. 每个 query 独立检索
all_results = []
for q in queries:
    all_results.extend(vector_store.similarity_search(q, k=10))

# 3. 合并去重
final = deduplicate(all_results)
```

**适用**：模糊/口语化问题

---

## 📐 选型决策

```
Q1: 单轮 vs 多轮？
├── 单轮 → 直接改写
└── 多轮 → 多轮融合

Q2: 答案丰富度？
├── 答案丰富（如百科）→ HyDE
└── 答案简短（如 FAQ）→ 直接改写

Q3: 用户 query 模糊度？
├── 清晰 → 跳过改写
├── 中等 → 直接改写
└── 模糊 → Multi-Query
```

---

## 📊 提升效果

| 任务 | 原始 | 直接改写 | HyDE | Multi-Query |
|------|------|---------|------|------------|
| HotpotQA | 0.68 | 0.74 | 0.76 | 0.78 |
| 多轮对话 | 0.55 | 0.65 | 0.68 | 0.70 |
| 模糊问题 | 0.60 | 0.68 | 0.72 | 0.75 |

---

## 🛠️ 完整 Pipeline

```python
class QueryRewriter:
    def __init__(self, llm, embedding_model, vector_store):
        self.llm = llm
        self.embedding = embedding_model
        self.store = vector_store
    
    def rewrite(self, query, history=None):
        # 1. 改写
        if history:
            rewritten = self._rewrite_with_context(query, history)
        else:
            rewritten = self._rewrite_direct(query)
        
        # 2. HyDE 增强（可选）
        hyde_doc = self.llm.generate(f"问题：{rewritten}\n简短答案：")
        
        # 3. 多角度查询
        multi_queries = self.llm.generate(
            f"对问题生成 3 种不同检索表述：\n{rewritten}"
        ).split("\n")
        
        return rewritten, [hyde_doc] + multi_queries
    
    def retrieve(self, query, history=None, top_k=10):
        rewritten, queries = self.rewrite(query, history)
        
        # 多个 query 检索
        all_docs = []
        for q in queries:
            docs = self.store.similarity_search(q, k=top_k)
            all_docs.extend(docs)
        
        # Rerank + 去重
        unique = self._deduplicate(all_docs)
        return self._rerank(rewritten, unique)[:5]
```

---

## 🔗 兄弟章节

- **本专题**：[RAG Pipeline 综述](../rag-pipeline/README.md) / [Hybrid Search](../hybrid-search/README.md) / [RAG 评估](../../../08-llmops/agent-evaluation/09-rag-evaluation/README.md)
- **咬文嚼字**：[RAG 面试](../../../13.split-hairs/11.ai/rag/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 改写后查询越长越好 | ✅ 短而精的 query 检索效果更好 |
| ❌ HyDE 总是更好 | ✅ 仅答案丰富场景有效 |
| ❌ Multi-Query 越多越好 | ✅ 3-5 个是甜蜜点 |
| ❌ 改写一定提升 | ✅ 简单 query 不需要改写 |

← [返回 L2 技术栈](../README.md)