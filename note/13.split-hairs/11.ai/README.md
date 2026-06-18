# AI 咬文嚼字

> AI 高频面试题与新概念深挖，对齐主模块 [`11.ai`](../../11.ai/)

---

## 文章清单

| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [AI 思维：抛硬币](ai-thinking/) | ⭐⭐ | 100 次正面后第 101 次概率？数学 vs AI 思维差异 |

---

## 待补充的高频面试题

### LLM 基础（必考）
- **Transformer 架构核心**（Self-Attention + Positional Encoding + FFN）
- **Attention 机制详解**（QKV 矩阵运算）
- **Token 是什么**（BPE / SentencePiece / 计费原理）
- **Temperature / Top-p / Top-k 采样策略**
- **上下文窗口（Context Window）限制**

### Prompt Engineering（高频）
- **Few-shot / Zero-shot / Chain-of-Thought**
- **Prompt 注入攻击与防御**
- **System Prompt 设计最佳实践**
- **结构化输出**（JSON mode / Function Calling）

### RAG（检索增强生成）
- **RAG 架构设计**（Embedding + Vector DB + Retrieval + Generation）
- **Chunking 策略**（固定大小 / 语义分割 / 递归分割）
- **向量数据库选型**（Pinecone / Weaviate / Milvus / pgvector）
- **RAG vs Fine-tuning 选型**

### AI 应用工程
- **Hallucination（幻觉）问题**（原因 + 缓解方案）
- **Function Calling / Tool Use 原理**
- **AI Agent 架构**（ReAct / Plan-and-Execute）
- **流式响应（Streaming）实现**（SSE / ReadableStream）
- **AI 应用评估体系**（Eval / RAGAS）

### AI 产品与趋势
- **LLM 选型对比**（GPT-4 / Claude / Gemini / Llama）
- **本地部署 vs API 调用**
- **AI 安全与对齐**（RLHF / Constitutional AI）

---

## 学习路径

1. **入门**（3 天）：AI 思维 + Token 概念 + 基础 Prompt
2. **进阶**（2 周）：Transformer + RAG + Function Calling
3. **冲刺面试**：重点看"RAG 架构"、"幻觉问题"、"Agent 设计"（待补）

## 交叉引用

- 主模块：[`note/11.ai`](../../11.ai/) — AI 知识体系
- 相关章节：[`12.front-end`](../12.front-end/)（前端集成 AI）
