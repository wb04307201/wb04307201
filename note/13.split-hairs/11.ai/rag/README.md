<!--
question:
  id: 11.ai-rag
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [11.ai, RAG, rag]
-->

# RAG 架构设计 — 检索增强生成面试深挖

> 一句话定位：RAG（Retrieval-Augmented Generation）让 LLM 基于私有/实时数据回答 —— 是 2026 年企业 LLM 应用的事实标准。完整概念见 [主模块 RAG vs Fine-tuning](../../../11.ai/07-llmops/01-rag-vs-finetuning/README.md)。

---

## 引子：客服 AI 一本正经地编造订单号

```text
用户（真实对话）："请帮我查订单 8848-1922 的物流"
客服 AI：
"已为您查到订单 8848-1922，由杭州仓库发出，预计明日 14:00 前送达。"
（实际上这个订单号根本不存在，用户是随便测的）
```

**真相**：LLM 没有事实性保障，它**只能基于训练数据里的概率续写**。
不知道就说"不知道"？做不到，它会**编造**——而且语气非常自信。

RAG 的回答：

1. 用户问问题 → 先去企业知识库（订单系统 / CRM）检索真实数据
2. 把"检索到的真实文档"塞进 Prompt
3. 让 LLM **基于真实文档**回答，不能编造

RAG 不是"让 LLM 变聪明"，而是"**给 LLM 装一个能查事实的工具**"。

## 一、核心流程（一图记全）

```
离线索引：文档 → Chunking → Embedding → 向量数据库
在线查询：问题 → Embedding → 检索 Top-K → 拼接 Prompt → LLM 生成
```

**RAG 解决什么问题**：
- LLM 不知道你的私有数据（企业文档、代码库）
- LLM 知识有截止日期
- LLM 可能"幻觉"（编造事实）
- LLM 上下文窗口有限（塞不下 1000 页文档）

---

## 二、面试陷阱

### 陷阱 1：以为 RAG = 向量检索
- **真相**：Advanced RAG 是**混合检索（向量 + BM25）+ Reranker 重排序 + 查询改写 + 多路召回**。纯向量检索效果差。

### 陷阱 2：以为 Chunk 越大越好
- **真相**：经验值 **500-1500 字符**，太小丢上下文，太大噪音多；重叠 10-20% 保持连续性。

### 陷阱 3：以为 Embedding 模型无所谓
- **真相**：**中文必须用 BGE-M3 或 Cohere embed-v3**，OpenAI 对中文支持弱；维度从 768 到 3072 都有。

### 陷阱 4：以为 RAG 能完全解决幻觉
- **真相**：RAG 只解决"有据可依"，但模型仍可能**曲解检索内容**或**添加原文没有的信息**（忠实性幻觉）。

### 陷阱 5：忽视引用溯源
- **真相**：每个事实陈述必须有引用 ID，否则用户无法验证 → 高风险场景（医疗/法律）必须强制引用。

---

## 三、4 层优化速记

| 层 | 优化项 |
|---|--------|
| **Chunking** | 递归分割、500-1500 字符、重叠 10-20% |
| **Embedding** | 中文用 BGE-M3、英文用 OpenAI text-embedding-3 |
| **检索** | 混合检索（向量 + BM25）+ Reranker |
| **生成** | 引用源标注、置信度过滤、"不知道就说不知道" Prompt |

---

## 四、5 大向量数据库速记

| 数据库 | 适用 |
|--------|------|
| **Pinecone** | 云托管、快速启动 |
| **Weaviate** | GraphQL、多模态 |
| **Milvus** | 大规模、高性能 |
| **Qdrant** | Rust 性能优秀 |
| **pgvector** | 已有 PG 的团队 |

---

## 五、反直觉点

- **"RAG 优先"是 2026 共识**：Fine-tuning 用于风格调整，**事实查询用 RAG** —— RAG 随时更新、低成本、可溯源。
- **BM25 不是"过时技术"**：关键词检索在精确匹配（型号、专有名词）上反而比向量检索强，混合检索是标配。
- **Reranker 是性价比之王**：Cross-Encoder 重排序显著提升 Top-K 质量，延迟代价可接受。

---

## 六、30 秒面试话术

> RAG 是检索增强生成，让 LLM 基于私有数据回答。
>
> 流程：离线索引（文档分块 → Embedding → 存入向量数据库）+ 在线查询（问题向量化 → 检索相关片段 → 拼接 Prompt → LLM 生成）。
>
> 关键技术：Chunking（递归分割，块大小 500-1500 字符，重叠 10-20%）；Embedding 模型（OpenAI text-embedding-3、BGE-M3 中文首选）；向量数据库（Pinecone / Weaviate / Milvus / pgvector）。
>
> 优化：检索（混合检索向量+BM25 + Reranker 重排序）+ 生成（引用源标注、置信度过滤、Prompt 工程）。
>
> RAG vs Fine-tuning：RAG 随时更新、低成本、适合事实查询；Fine-tuning 内化知识、高成本、适合风格调整。
>
> 2026 共识：**RAG 优先**，Fine-tuning 补充。

---

## 七、深度阅读

- 主模块：[RAG vs Fine-tuning](../../../11.ai/07-llmops/01-rag-vs-finetuning/README.md)
- 关联：[Function Calling](../function-calling/README.md) — RAG 本质是 retrieve 工具
- 关联：[Token 与计费](../token/README.md) — RAG 减少 Token 消耗
- 关联：[LLM 幻觉](../hallucination/README.md) — RAG 是抗幻觉主流方案

---

## 八、RAG 的边界：什么时候不适合用？

RAG 在**文档问答、低频更新场景**是最佳方案，但在 **AI Coding 大规模代码库场景下 RAG 容易失败**——Claude Code 等主流 AI Coding 工具主动放弃 RAG，改用 Agentic Search。

- 兄弟面试题（高频反直觉）：[为什么 Claude Code 放弃了 RAG](../claude-code-agentic-search/README.md)
- 深度原理：[Agentic Search vs RAG](../../../11.ai/07-llmops/agentic-search-vs-rag/README.md)
- 实践原文：[Claude Code 最佳实践](../../../11.ai/03-engineering/claude-code-practices/README.md)

---

> 📅 2026-06-30 · 咬文嚼字 · 企业 LLM 标配 · ⭐⭐⭐⭐⭐