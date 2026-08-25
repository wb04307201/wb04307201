<!--
module:
  number: 09
  slug: ai-applications
  topic: AI Applications（RAG / Agent / Prompt / LLM 推理 / Fine-tuning / Eval）
  audience: AI 应用工程师 / 后端转 AI / 创业团队 / 求职面试者
  category: 主模块
  summary: AI 应用层——RAG、Agent 框架、Prompt 工程、LLM 推理优化、Fine-tuning、Eval 六大主题。
-->

# 09. AI Applications

> **定位**：AI 应用层——RAG、Agent、Prompt、LLM 推理工程、Fine-tuning、Eval。
> **继承规范**：[SPEC.md](./SPEC.md)

## MOC 索引

| # | 主题 | 用途 |
|---|------|------|
| 1 | [rag/](./rag/) | RAG 全景（检索 / rerank / 生成 / 评估 / 生产） |
| 2 | [agent/](./agent/) | Agent 框架（ReAct / Plan-Execute / Multi-Agent） |
| 3 | [prompts/](./prompts/) | Prompt 工程 |
| 4 | [llm-inference/](./llm-inference/) | LLM 推理优化（KV Cache / Flash Attention / Paged） |
| 5 | [fine-tuning/](./fine-tuning/) | 微调方法（SFT / RLHF / DPO） |
| 6 | [eval/](./eval/) | 评估方法 |

## 阅读路径（按场景）

- **从零搭一个 RAG 问答**：[rag/](./rag/) 全景 → [llm-inference/](./llm-inference/) 降本提速 → [eval/](./eval/) 验证效果
- **做生产级 Agent**：[agent/](./agent/) 框架与可靠性 → [prompts/](./prompts/) Prompt 工程 → [eval/](./eval/) 回归评测
- **面试冲刺**：先看各主题 README 的"面试高频题"速查，再按需深入（配套 [12.interview/11.ai](../12.interview/11.ai/) 陷阱版）
- **降本专题**：[agent/agent-context/](./agent/agent-context/) 上下文工程 + [llm-inference/](./llm-inference/) 推理优化

← [返回 note 总目录](../README.md)