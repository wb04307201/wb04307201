<!--
module:
  parent: ai
  slug: ai/rag-pipeline
  type: article
  category: 主模块子文章
  summary: RAG 完整 Pipeline 综述
-->

# RAG Pipeline（完整流水线综述）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：RAG Pipeline = **Query Rewrite → Hybrid Search → Rerank → Generation** 全链路。**2024 SOTA 5 阶段架构**，召回率 +30%、精确率 +25%。

---

## 📐 5 阶段 SOTA 架构

```
User Query
   ↓
[Stage 1] Query Rewrite       ← 多轮融合 / HyDE / Multi-Query
   ↓
[Stage 2] Hybrid Search       ← 向量 + BM25（RRF 融合）
   ↓
[Stage 3] Rerank              ← Cross-Encoder Top-100 → Top-10
   ↓
[Stage 4] Context Compression ← 压缩到 LLM 上下文窗口
   ↓
[Stage 5] Generation          ← LLM 生成 + 引用溯源
   ↓
Answer + 引用
```

---

## 🔍 各阶段深度

### Stage 1: Query Rewrite

详见 [Query Rewrite 章节](../query-rewrite/README.md)
- 多轮对话 → 上下文融合
- 口语化 → 关键词改写
- 模糊问题 → Multi-Query

### Stage 2: Hybrid Search

详见 [Hybrid Search 章节](../hybrid-search/README.md)
- 向量（语义） + BM25（关键词）
- RRF 融合
- 召回率 +15-25%

### Stage 3: Rerank

详见 [Reranker 章节](../reranker/README.md)
- Bi-Encoder 召回 Top-100
- Cross-Encoder 重排 Top-10
- 精确率 +15-30%

### Stage 4: Context Compression

```python
# LongLLMLingua / LLMLingua
from llmlingua import PromptCompressor

compressor = PromptCompressor("microsoft/llmlingua-2-bert-base-multilingual-cased")
compressed = compressor.compress_prompt(
    context, 
    target_token=2000,  # 压缩到 2K tokens
)
```

**目标**：把 10K context 压缩到 2K，保留 90% 关键信息

### Stage 5: Generation

```python
prompt = f"""基于以下参考资料回答问题，要求准确、简洁，并标注引用。

参考资料：
{context_with_citations}

问题：{query}

回答：
"""
```

**要求**：
- ✅ 准确（基于 context）
- ✅ 简洁
- ✅ 引用溯源（[1], [2]...）

---

## 📊 各阶段效果提升

| 阶段 | 召回率 | 精确率 | 延迟 |
|------|--------|--------|------|
| 原始 | 0.65 | 0.60 | 100ms |
| + Query Rewrite | 0.75 | 0.65 | 200ms |
| + Hybrid Search | 0.85 | 0.70 | 250ms |
| + Rerank | 0.85 | 0.85 | 350ms |
| + Compression | 0.83 | 0.85 | 400ms |
| + Generation | 0.83 | 0.88 | 1500ms |

---

## 🛠️ 完整实现

```python
from langchain.vectorstores import Milvus
from FlagEmbedding import BGEM3FlagModel, FlagReranker
from llmlingua import PromptCompressor
from openai import OpenAI

class SOTARAG:
    def __init__(self):
        self.vector_store = Milvus(...)
        self.bm25 = BM25Retriever(...)
        self.reranker = FlagReranker('BAAI/bge-reranker-v2-m3')
        self.compressor = PromptCompressor("...")
        self.llm = OpenAI()
    
    def query(self, user_query, history=None):
        # Stage 1: Query Rewrite
        rewritten = self._rewrite(user_query, history)
        multi_queries = self._multi_query(rewritten)
        
        # Stage 2: Hybrid Search
        vector_results = []
        for q in multi_queries:
            vector_results.extend(self.vector_store.similarity_search(q, k=20))
        
        bm25_results = []
        for q in multi_queries:
            bm25_results.extend(self.bm25.retrieve(q, k=20))
        
        # RRF 融合
        merged = self._rrf_merge(vector_results, bm25_results, top_k=50)
        
        # Stage 3: Rerank
        pairs = [(rewritten, doc.content) for doc in merged]
        scores = self.reranker.compute_score(pairs)
        reranked = sorted(zip(merged, scores), key=lambda x: -x[1])[:10]
        
        # Stage 4: Compression
        context = "\n".join([doc.content for doc, _ in reranked])
        compressed = self.compressor.compress_prompt(context, target_token=2000)
        
        # Stage 5: Generation
        prompt = f"参考资料：\n{compressed}\n问题：{user_query}\n回答："
        answer = self.llm.generate(prompt)
        
        return answer
```

---

## 🔗 兄弟章节

- **本专题**：[Query Rewrite](../query-rewrite/README.md) / [Hybrid Search](../hybrid-search/README.md) / [Reranker](../reranker/README.md) / [Chunking](../chunking-strategies/README.md) / [Embedding](../embedding-models/README.md)
- **L1**：[Lost in middle](../lost-in-middle/README.md)
- **咬文嚼字**：[RAG 面试](../../../13.split-hairs/11.ai/rag/README.md)
- **LLMOps**：[RAG 评估](../../../08-llmops/agent-evaluation/09-rag-evaluation/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ RAG = 向量检索 | ✅ 2024 SOTA 是 5 阶段 Pipeline |
| ❌ 阶段越多越好 | ✅ 每阶段都增加延迟，需权衡 |
| ❌ 召回率 100% 才好 | ✅ 95% 已足够，最终靠 LLM |
| ❌ RAG 替代 fine-tune | ✅ RAG 适合知识更新场景，FT 适合技能固化 |

← [返回 L2 技术栈](../README.md)