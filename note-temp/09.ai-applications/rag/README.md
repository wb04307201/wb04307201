# RAG（Retrieval-Augmented Generation）

> **定位**：MOC——RAG 主题索引，覆盖流水线 / 范式演进 / 选型 / 评估 / 生产治理 / 前沿。
> **继承规范**：[../SPEC.md](../SPEC.md)

## 原子笔记清单

| # | 主题 | 路径 | 摘要 |
|---|------|------|------|
| 1 | RAG Pipeline | [01-pipeline.md](./01-pipeline.md) | 5 阶段 SOTA 架构：Query Rewrite → Hybrid Search → Rerank → 上下文压缩 → 生成 |
| 2 | 范式演进四阶段 | [02-paradigm-evolution.md](./02-paradigm-evolution.md) | Naive → Advanced → Modular → Agentic，含选型决策树 |
| 3 | RAG vs Fine-tuning | [03-rag-vs-finetuning.md](./03-rag-vs-finetuning.md) | Prompt / RAG / 微调三大定制策略对比与选型 |
| 4 | 评估 | [04-evaluation.md](./04-evaluation.md) | 检索 × 生成 × 系统 三维度 + RAGAS / TruLens / DeepEval |
| 5 | 超范围拒答 | [05-out-of-domain-rejection.md](./05-out-of-domain-rejection.md) | 6 大检测机制 + 5 大拒答模式 + 4 步阈值调优 + 监控 |
| 6 | Agentic RAG | [06-agentic-rag.md](./06-agentic-rag.md) | Agentic Search 取代 RAG 索引（AI Coding 场景） |

## 阅读路径

```text
先建立全景            01-pipeline（机制）+ 02-paradigm-evolution（代际）
    ↓
再决定要不要用 RAG    03-rag-vs-finetuning（选型）
    ↓
落地后度量与治理      04-evaluation（量化）+ 05-out-of-domain-rejection（拒答）
    ↓
看边界与前沿          06-agentic-rag（何时不该用 RAG）
```

> 💡 **正交提醒**：01 讲的是单次 RAG 的**执行环节**（机制），02 讲的是 RAG 的**范式代际**（成熟度），两者不是一回事，详见 02 的「关键澄清」章节。

## 关联主题

- [../prompts/](../prompts/) — Prompt 工程
- [../eval/](../eval/) — 评估方法
- [../agent/](../agent/) — Agent 框架
- [../../08.ai-foundations/03-transformer/](../../08.ai-foundations/03-transformer/) — Transformer 基础
- [../../08.ai-foundations/05-tokenization-embedding/](../../08.ai-foundations/05-tokenization-embedding/) — Embedding 基础

## 尚未迁移的 RAG 子环节

以下检索链路子章节仍在 `note/11.ai/02-technology-stack/`，待后续任务迁入本 MOC：

[Query Rewrite](../../../note/11.ai/02-technology-stack/query-rewrite/README.md) · [Hybrid Search](../../../note/11.ai/02-technology-stack/hybrid-search/README.md) · [Reranker](../../../note/11.ai/02-technology-stack/reranker/README.md) · [Chunking](../../../note/11.ai/02-technology-stack/chunking-strategies/README.md) · [Embedding Models](../../../note/11.ai/02-technology-stack/embedding-models/README.md) · [Lost in Middle](../../../note/11.ai/02-technology-stack/lost-in-middle/README.md) · [知识入库流水线](../../../note/11.ai/02-technology-stack/knowledge-ingestion-pipeline/README.md) · [长文档处理](../../../note/11.ai/02-technology-stack/long-document-processing/README.md)

---

← [返回 09.ai-applications](../README.md)
