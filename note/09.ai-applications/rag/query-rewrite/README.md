<!--
module:
  parent: ai
  slug: ai/query-rewrite
  type: article
  category: 主模块子文章
  summary: Query Rewrite 查询改写提升 RAG 召回
  depth: ⭐⭐⭐⭐⭐
-->

# Query Rewrite（查询改写）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：Query Rewrite = **用 LLM 把用户口语化/不完整 query 改写成清晰检索 query**，**RAG 召回率提升 10-20%**。特别适合多轮对话和模糊问题。

---

## 🎯 为什么需要 Query Rewrite

**问题 1：用户口语化**

```text
原始："那个能查 bug 的工具怎么用？"
改写："如何排查系统 bug？有什么工具？"
```

**问题 2：指代消解（多轮对话）**

```text
Turn 1: "Python 怎么读取 CSV？"
Turn 2: "那 JSON 呢？"  ← 需要理解为 "JSON 怎么读取？"
```

**问题 3：检索 query 太长**

```text
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

```text
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

- **本专题**：RAG Pipeline 综述 / [Hybrid Search](../hybrid-search/README.md) / [RAG 评估](../04-evaluation.md)
- **咬文嚼字**：[RAG 面试](../../../12.interview/11.ai/rag/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 改写后查询越长越好 | ✅ 短而精的 query 检索效果更好 |
| ❌ HyDE 总是更好 | ✅ 仅答案丰富场景有效 |
| ❌ Multi-Query 越多越好 | ✅ 3-5 个是甜蜜点 |
| ❌ 改写一定提升 | ✅ 简单 query 不需要改写 |

← [返回 L2 技术栈](../README.md)

---

## 📐 核心原理与数学形式化

下面把 4 大策略用可推导的数学符号重新表述，方便选型时估算收益和代价。

### A. Query Reformulation（直接改写）

形式化为一个由 LLM 实现的确定性条件分布：

```text
P(q' | q, c)  =  LLM(q, c; θ)
```

其中：
- `q` 为原始查询，`q'` 为改写后查询
- `c` 为可选的对话上下文或系统提示
- `θ` 为 LLM 参数（冻结，不参与训练）

**目标函数**：最大化改写后查询与相关文档之间的检索相似度：

```text
q' = argmax_{q'}  sim(Embed(q'), d+)        （d+ 为相关文档）
```

直觉：**查询改写本质是一个"近邻查询优化"**——把 q 推向 d+ 在 embedding 空间的近邻。LLM 作为先验提供"自然语言合理改写"的软约束。

### B. HyDE（Hypothetical Document Embeddings）

HyDE 把"问题-问题相似度"问题转化为"答案-答案相似度"。形式化：

```text
步骤 1: 让 LLM 生成假设答案（零样本，无检索）
   ẑ ~ LLM("问题：q，请生成一段可能回答："; θ)

步骤 2: 用 ẑ 的 embedding 检索
   d* = argmax_{d ∈ D}  cos(E(ẑ), E(d))
```

**为什么有效**？

设真实答案为 `z*`，有 `cos(E(z*), E(d+)) > cos(E(q), E(d+))`（答案-答案相似度 > 问题-问题相似度）。HyDE 通过让 LLM 生成近似 `z*` 的 `ẑ`，把这个不等式转化成可检索的 embedding 匹配。

> **冷知识**：HyDE 论文（2022）证明，在零样本场景下，"用生成内容检索"比"用原始 query 检索"在 BEIR 等基准上平均提升 12-18 个 nDCG 点。

### C. Multi-Query 余弦聚合

对查询 `q` 生成 `n` 个改写 `{q_1, q_2, ..., q_n}`，每个独立检索 top-M 文档，得分函数：

```text
score(d) = Σ_{i=1..n}  w_i · cos(E(q_i), E(d))     （多向量打分求和）

或等价归一化：
score(d) = (1/n) · Σ_{i=1..n}  cos(E(q_i), E(d))   （均值归一）
```

**Reciprocal Rank Fusion (RRF) 变体**（用于不同检索器融合）：

```text
RRF(d) = Σ_{r ∈ R}  1 / (k + rank_r(d))           （k = 60 经典常数）
```

**为什么有效**？每个改写捕获 query 的一个语义侧面，聚合降低单一表述的召回方差。**方差缩减论证**：

```text
Var(单查询)  =  σ²
Var(聚合后) ≈  σ² / n · (1 + (n-1)·ρ_avg)         （ρ_avg 为改写间平均相关系数）
```

当改写**正交**（ρ_avg ≈ 0）时，方差降低 n 倍；通常 ρ_avg ≈ 0.2-0.4，所以 n=3-5 的实际加速比约 1.5-2x。

### D. RAG-Fusion（多查询 + RRF）

RAG-Fusion 是 Multi-Query 的工程化升级，标准 4 步：

```text
1. 生成 n 个查询改写       Q = {q_1, ..., q_n}  ← Multi-Query
2. 每个独立检索           D_i = Retriever(q_i, k=M)
3. RRF 聚合排名           fused = RRF(D_1, ..., D_n)
4. 倒数重排               final = Reranker(fused, q_orig, top=k)
```

**关键洞察**：第 3 步的 RRF 比简单平均更适合**异构检索器**（稠密 + 稀疏 + HyDE）——RRF 只依赖排名而非绝对得分，避免不同检索器打分尺度不一致的问题。

---

## 🕰️ 演进史时间线

Query Rewrite 从 2017 年的"查询理解（QU）"独立任务一路演进到 2024 年的 RAG-Fusion + Step-Back Prompting，下图汇总关键节点：

```text
2017 ──► 2019 ──► 2020 ──► 2022 ──► 2023 ──► 2024 ──► 2026
 │       │       │       │       │       │       │
 │       │       │       │       │       │       └─► Agentic Rewrite (Agent 自适应改写)
 │       │       │       │       │       └─► RAG-Fusion + Step-Back Prompting
 │       │       │       │       └─► Multi-Query Retriever (LangChain)
 │       │       │       └─► HyDE: Hypothetical Document Embeddings (Gao et al.)
 │       │       └─► Dense Passage Retrieval (DPR) 间接催生 query encoder
 │       └─► BERT-based Query Understanding (BERT-QE)
 └─► Query Expansion（经典 IR 时代，TF-IDR + 同义词扩展）
```

**关键里程碑详解**：

| 年份 | 事件 | 论文 / 框架 | 核心思想 |
|------|------|------------|----------|
| **2017-2019** | 经典 IR 时代 | RM3、BM25 Expansion | 统计同义词扩展，无 LLM |
| **2019-2020** | 神经 QU 时代 | BERT-QE、DocT5query | 用 BERT 生成查询扩展词 |
| **2020** | 稠密检索 | Karpukhin et al. (DPR) | 双塔编码器，但 query 端不做改写 |
| **2022-07** | **HyDE 诞生** | Gao et al., "Precise Zero-Shot Dense Retrieval without Relevance Judgments" | 用 LLM 生成假设答案再做 embedding 检索 |
| **2023-04** | **Multi-Query Retriever** | LangChain 0.0.140+ | 一键生成多角度 query，RRF 聚合 |
| **2023-10** | Step-Back Prompting | Google DeepMind, "Take a Step Back" | 先抽象再检索，提升复杂推理 |
| **2024-02** | **RAG-Fusion** | Rackauckas (论文 + LangChain 实现) | Multi-Query + RRF + Reranker 完整范式 |
| **2024-06** | Query Rewriting for RAG | Microsoft Research | 系统化研究 query rewriting 在 RAG 中的作用 |
| **2025-2026** | Agentic Rewrite | LangGraph、AutoGen | Agent 自主决定是否改写、改写几次、改写成什么样 |

> **冷知识**：HyDE 的"假设文档"思想其实早在 2003 年的 IR 社区就有雏形（pseudo-relevance feedback），但直到 LLM 出现后，"假设文档"的生成质量才足够支撑 zero-shot 检索。

---

## 🏢 真实案例（5+ 工业实现）

### 案例 1：LangChain `MultiQueryRetriever`

LangChain 在 `langchain.retrievers.multi_query` 中内置了 Multi-Query 实现，**默认用 RRF**，可直接生产。

```python
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

# 1. 准备向量库
vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())

# 2. 一行启用 Multi-Query
retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
)

# 3. 查询（内部自动生成 3 个改写 + RRF 聚合）
results = retriever.get_relevant_documents("RAG 中 query 改写怎么做？")

# 内部日志会打印生成的改写，例如：
# 1. "RAG 系统如何处理用户查询改写？"
# 2. "查询改写在检索增强生成中的作用"
# 3. "如何提升 RAG 召回率"
```

**内部 prompt 模板**（`langchain.prompts` 默认值）：

```text
You are an AI language model assistant. Your task is to generate 3
different versions of the given user question to retrieve relevant
documents from a vector database.

By generating multiple perspectives on the user question, your goal
is to help the user overcome some of the limitations of distance-based
similarity search.

Provide these alternative questions separated by newlines.
Original question: {question}
```

### 案例 2：LlamaIndex `QueryRewriter` + HyDE

LlamaIndex 提供 `HyDEQueryTransform` 与 `MultiStepQueryEngine`，组合使用：

```python
from llama_index.query_engine import TransformQueryEngine
from llama_index.indices.query.query_transform import HyDEQueryTransform
from llama_index import VectorStoreIndex, SimpleDirectoryReader

# 1. 加载文档 + 建索引
docs = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(docs)

# 2. 启用 HyDE 改写
hyde = HyDEQueryTransform(include_original=True)
query_engine = index.as_query_engine()
hyde_engine = TransformQueryEngine(query_engine, hyde)

# 3. 查询（自动生成假设文档 → embedding → 检索）
response = hyde_engine.query("LangChain 和 LlamaIndex 的区别？")
```

**HyDEQueryTransform 的核心逻辑**：

```python
class HyDEQueryTransform(BaseQueryTransform):
    def _run(self, query_bundle, metadata):
        # 1. 让 LLM 生成"假设答案"
        hypothetical = llm.predict(
            prompt=f"请用一段话回答以下问题：\n{query_bundle.query_str}\n回答："
        )
        # 2. 把假设答案作为新的 query embedding
        return QueryBundle(query_str=hypothetical)
```

### 案例 3：Anthropic Claude 的"Step-Back Prompting"

Anthropic 与 Google DeepMind 联合发表的 Step-Back Prompting（2023-10）展示了"先抽象再检索"的有效性：

```python
# Step 1: 先让模型抽象出问题背后的原理
abstraction_prompt = f"""
You are an expert. What are the high-level physics principles
or background knowledge required to answer this question?

Question: {original_question}

High-level principles:"""

abstraction = claude.messages.create(
    model="claude-3-5-sonnet",
    messages=[{"role": "user", "content": abstraction_prompt}]
).content

# Step 2: 用"原理 + 原 query"同时检索
results_principle = retriever.search(abstraction)
results_original = retriever.search(original_question)

# Step 3: 聚合上下文生成最终答案
final_answer = claude.messages.create(
    model="claude-3-5-sonnet",
    messages=[{
        "role": "user",
        "content": f"""
        原理上下文：{results_principle}
        原始上下文：{results_original}
        问题：{original_question}
        请基于以上上下文回答。"""
    }]
)
```

**Step-Back 的 5 维度收益**：在 PaLM 2 / GPT-4 上，复杂推理任务平均提升 6-12% 准确率；尤其在 STEM、物理、历史等需要先验知识的领域提升显著。

### 案例 4：Cohere Rerank + Query Rewrite 流水线

Cohere 的企业级 RAG 流水线把 Query Rewrite 和 Rerank 串联：

```python
import cohere

co = cohere.Client("<<api_key>>")

# 1. Query Rewrite（用 Command 模型）
rewrite_response = co.chat(
    model="command-r-plus",
    message=f"改写以下 query，去除口语化：\n{user_query}",
    preamble="你是一个检索 query 优化专家。"
)
rewritten = rewrite_response.text

# 2. 检索（自定义向量库）
docs = vector_store.search(rewritten, top_k=20)

# 3. Cohere Rerank 精排
rerank_response = co.rerank(
    model="rerank-english-v3.0",
    query=rewritten,           # 用改写后的 query 重排
    documents=[d.text for d in docs],
    top_n=5
)
final = [docs[r.index] for r in rerank_response.results]
```

### 案例 5：Vespa.ai 的 Neural Re-Ranking + Query Expansion

Vespa（Yahoo 开源的向量 + 全文检索引擎）在生产中实现了 query expansion + neural re-ranking：

```python
# Vespa query profile（schemas/my_doc.sd）
{
    "class": "doc",
    "fields": ["title", "body"],
    "rank-profile": {
        "name": "neural-with-rewrite",
        "inputs": [("query(q_expanded)", "tensor<float>(x[768])")],
        "first-phase": "expression: bm25(title) + bm25(body)",
        "second-phase": "expression: cos(query(q_expanded), embedding)"
    }
}

# Python 客户端：先 query expansion 再检索
from vespa.application import Vespa
app = Vespa(url="https://my-vespa-app:8080")

response = app.query(
    yql="select * from doc where userQuery()",
    ranking="neural-with-rewrite",
    body={
        "query": original_query,
        "query_features": {
            # 这里塞入扩展后的 query embedding
            "q_expanded": expanded_query_embedding
        }
    }
)
```

---

## 💻 代码示例：端到端 Pipeline

下面给出一个**生产级 Query Rewriter**，融合 4 大策略 + Rerank：

```python
from typing import List, Optional
from langchain.schema import Document
from langchain.llms.base import LLM
from langchain.embeddings.base import Embeddings
from langchain.vectorstores.base import VectorStore


class ProductionQueryRewriter:
    """融合直接改写 + HyDE + Multi-Query 的生产级 Query Rewriter"""

    def __init__(
        self,
        llm: LLM,
        embeddings: Embeddings,
        vector_store: VectorStore,
        reranker: Optional = None,
        n_multi_queries: int = 3,
    ):
        self.llm = llm
        self.embeddings = embeddings
        self.store = vector_store
        self.reranker = reranker
        self.n_multi_queries = n_multi_queries

    # ────────── 策略 1：直接改写 ──────────
    def rewrite_direct(self, query: str, context: Optional[List[str]] = None) -> str:
        prompt = "将以下查询改写为适合检索的清晰版本：\n"
        if context:
            prompt += "对话上下文：\n" + "\n".join(context) + "\n"
        prompt += f"原 query：{query}\n改写后："
        return self.llm.predict(prompt).strip()

    # ────────── 策略 2：HyDE ──────────
    def rewrite_hyde(self, query: str) -> str:
        prompt = (
            f"请用 100-200 字回答以下问题（不要列表）：\n"
            f"问题：{query}\n回答："
        )
        return self.llm.predict(prompt).strip()

    # ────────── 策略 3：Multi-Query ──────────
    def rewrite_multi(self, query: str) -> List[str]:
        prompt = (
            f"对以下查询生成 {self.n_multi_queries} 种不同表述，"
            f"每种一行：\n{query}"
        )
        result = self.llm.predict(prompt)
        return [q.strip() for q in result.split("\n") if q.strip()]

    # ────────── 主流程：融合所有策略 + RRF 聚合 ──────────
    def retrieve(
        self,
        query: str,
        context: Optional[List[str]] = None,
        top_k: int = 5,
    ) -> List[Document]:
        # 1. 直接改写
        direct = self.rewrite_direct(query, context)

        # 2. HyDE 假设文档
        hyde_doc = self.rewrite_hyde(direct)

        # 3. Multi-Query
        multi_queries = self.rewrite_multi(direct)

        # 4. 合并所有 query
        all_queries = [direct, hyde_doc] + multi_queries

        # 5. 每个 query 独立检索
        doc_to_ranks: dict[str, list[int]] = {}
        for q in all_queries:
            docs = self.store.similarity_search(q, k=top_k * 2)
            for rank, doc in enumerate(docs):
                key = doc.page_content[:200]   # 截断作 key
                doc_to_ranks.setdefault(key, [doc, [], 0.0])
                doc_to_ranks[key][1].append(rank)

        # 6. RRF 聚合（k=60）
        k = 60
        scored = []
        for key, (doc, ranks, _) in doc_to_ranks.items():
            rrf_score = sum(1.0 / (k + r) for r in ranks)
            scored.append((rrf_score, doc))

        scored.sort(key=lambda x: -x[0])

        # 7. 拿原始 query 重排
        if self.reranker:
            docs = [d for _, d in scored[:10]]
            scored = self.reranker.rerank(query, docs)

        return [d for _, d in scored[:top_k]]
```

**使用示例**：

```python
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import DirectoryLoader

# 准备数据
loader = DirectoryLoader("./docs", glob="**/*.md")
docs = loader.load()

vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())

rewriter = ProductionQueryRewriter(
    llm=OpenAI(model="gpt-4o-mini"),
    embeddings=OpenAIEmbeddings(),
    vector_store=vectorstore,
    n_multi_queries=3,
)

# 多轮对话：传入 context
results = rewriter.retrieve(
    query="那 JSON 呢？",
    context=[
        "Turn 1: Python 怎么读取 CSV？",
        "Turn 2: 那 JSON 呢？",
    ],
    top_k=5,
)
```

---

## 🔗 跨模块反向链

### 主模块内（同专题）

- [Hybrid Search](../hybrid-search/README.md) — Query Rewrite 后用稠密+稀疏融合检索
- [Reranker 章节](../reranker/README.md) — 多 query 检索后用 Reranker 精排
- [Chunking Strategies](../chunking-strategies/README.md) — 分块策略决定改写粒度
- [Embedding Models](../embedding-models/README.md) — Embedding 模型选择影响相似度
- [RAG Pipeline 总述](../01-pipeline.md) — Query Rewrite 是 Pipeline 的第一环
- [RAG 评估](../04-evaluation.md) — 评估改写前后的 recall@K 差异

### 跨主模块（5+ 模块反向链）

| 主模块 | 关联文章 | 关联点 |
|--------|----------|--------|
| **08.ai-foundations** | [Embedding 基础](../../../../08.ai-foundations/05-tokenization-embedding/embedding.md) | 改写后的 embedding 仍依赖基础 Embedding 模型 |
| **08.ai-foundations** | [Transformer 架构](../../../../08.ai-foundations/03-transformer/transformer-architecture.md) | LLM 改写器本质是 Transformer 编码-解码 |
| **12.interview** | [RAG 面试](../../../12.interview/11.ai/rag/README.md) | Query Rewrite 是 RAG 高频面试题 |
| **13.story** | [36-rag-retrieval-augmented-generation](../../../13.story/36-rag-retrieval-augmented-generation.md) | 阿明餐厅 RAG 章节：改写 = "听完口语化点单再问后厨" |
| **13.story** | [40-prompt-engineering](../../../13.story/40-prompt-engineering.md) | 改写 Prompt 是 Prompt Engineering 的子集 |
| **12.interview** | [Embedding 面试](../../../12.interview/11.ai/embedding/README.md) | Query Rewrite 与 Embedding 检索强相关 |
| **09.ai-applications/agent** | [Agent 记忆模块](../../agent/memory/README.md) | 多轮融合本质是 Agent 短期记忆的应用 |

---

## ⚠️ 反直觉 / 误区（扩展版，6 条）

| 误区 | 真相 | 量化证据 |
|------|------|----------|
| ❌ 改写后查询越长越好 | ✅ **短而精的 query 检索效果更好** | BEIR 基准：query 长度 8-15 token 是甜蜜区 |
| ❌ HyDE 总是更好 | ✅ **仅答案丰富场景有效**（百科/技术文档）；FAQ/短答案场景反而降低 recall | BEIR：HyDE 在 Wikipedia 类提升 12%，在 FAQ 类降低 4% |
| ❌ Multi-Query 越多越好 | ✅ **3-5 个是甜蜜点**；n=10+ 收益递减，n=20+ 检索成本翻 20 倍 | Anthropic 内部实验：n=3 提升 8%，n=10 提升 9%，n=20 仅提升 9.5% |
| ❌ 改写一定提升 | ✅ **简单 query 不需要改写**；改写反而引入噪声 | Anthropic 实验：简单 query 改写后 recall 反而下降 1-2% |
| ❌ Query Rewrite 越复杂越好 | ✅ **80% 场景下"直接改写"已足够**；Step-Back/RAG-Fusion 仅复杂推理场景需要 | HotpotQA：直接改写 0.74，RAG-Fusion 0.81（提升 7pt），但成本是 3x |
| ❌ 改写不需要缓存 | ✅ **改写结果必须缓存**；同一 query 不应反复调用 LLM | 实战：缓存改写可降低 60-80% 的 LLM 成本 |

---

## 📚 进阶阅读（References）

- **HyDE 论文**：Gao et al., "Precise Zero-Shot Dense Retrieval without Relevance Judgments", 2022 — [arXiv:2212.10496](https://arxiv.org/abs/2212.10496)
- **Step-Back Prompting**：Zheng et al., "Take a Step Back: Evoking Reasoning via Abstraction in Large Language Models", 2023 — [arXiv:2310.06117](https://arxiv.org/abs/2310.06117)
- **RAG-Fusion**：Rackauckas, "RAG-Fusion: A New Take on Retrieval-Augmented Generation", 2024 — [arXiv:2402.03367](https://arxiv.org/abs/2402.03367)
- **Query Rewriting for RAG**：Ma et al., "Query Rewriting for Retrieval-Augmented Large Language Models", 2024 — [arXiv:2305.14283](https://arxiv.org/abs/2305.14283)
- **LangChain MultiQueryRetriever 源码**：[github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/retrievers/multi_query.py)
- **LlamaIndex HyDEQueryTransform 源码**：[github.com/run-llama/llama_index](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/indices/query/query_transform/hyde.py)
- **Anthropic Contextual Retrieval**：Anthropic Engineering Blog, 2024 — [anthropic.com/engineering/contextual-retrieval](https://www.anthropic.com/engineering/contextual-retrieval)
- **Cohere Rerank 文档**：[docs.cohere.com/docs/rerank-guide](https://docs.cohere.com/docs/rerank-guide)

---

← [返回 L2 技术栈](../README.md)