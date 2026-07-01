<!--
module:
  parent: split-hairs
  slug: 11.ai
  type: article
  category: 高频面试题
  summary: AI 高频面试题与新概念深挖（5 篇纯面试题 + 9 篇主模块精炼版）
question:
  id: 11.ai-11.ai
  topic: 11.ai
  difficulty: ⭐⭐
  frequency: 高频
  scenario_type: 反直觉代码
  tags: [11.ai]
-->

# AI 咬文嚼字

> AI 高频面试题与新概念深挖，对齐主模块 [`11.ai`](../../11.ai/)。14 篇 = 5 篇纯面试题（幻觉 / 思维 / 生产力悖论 / 代码流失 / ROI）+ 9 篇主模块配套精炼版（Prompt / Context / Harness / Loop / Transformer / Token / RAG / Function Calling / Agent DAG）。

> ⚠️ **定位说明**：本目录所有文章都是**面试深挖版**（陷阱 + 反直觉 + 30 秒话术，50-80 行）。完整概念文档见主模块对应位置（README 末尾"深度阅读"区有链接）。

---

## 文章清单（14 题 = 5 篇纯面试题 + 9 篇精炼版）

### 🎯 真正的面试题（一题一文）

| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [AI 思维：抛硬币](ai-thinking/) | ⭐⭐ | 100 次正面后第 101 次概率？数学 vs AI 思维差异 |
| [LLM 幻觉问题](hallucination/) | ⭐⭐⭐⭐ | 幻觉成因 / 分类 / 检测与缓解方案 / 高风险 Fallback |
| [AI 编程生产力悖论](ai-coding-productivity-paradox/) | ⭐⭐⭐⭐ | Waydev/GitClear/Faros/Jellyfish 4 大研究 + DORA 框架 |
| [AI 代码流失率](ai-code-churn/) | ⭐⭐⭐⭐ | 采纳率 80% vs 留存率 30% 的真相 + 6 大改进策略 |
| [AI 编程 ROI 度量](ai-coding-roi/) | ⭐⭐⭐⭐ | DORA 4 指标 + SPACE 5 维度 + 改进策略 |

### 📚 概念精炼版（主模块配套面试深挖）

| 主题 | 难度 | 核心问题 | 主模块位置 |
|------|------|---------|----------|
| [Prompt Engineering](prompt-engineering/) | ⭐⭐⭐⭐ | 8 种核心技巧 + 陷阱 + 注入防御 | [02-technology-stack/prompt-engineering](../../11.ai/02-technology-stack/prompt-engineering/README.md) |
| [Context Engineering](context-engineering/) | ⭐⭐⭐⭐ | 4 大原则 + Lost in Middle + 演进路径 | [02-technology-stack/context-engineering](../../11.ai/02-technology-stack/context-engineering/README.md) |
| [Harness Engineering](harness-engineering/) | ⭐⭐⭐⭐ | 4 大 Harness 类型 + OpenSpec + 4 原则 | [03-engineering/harness-engineering](../../11.ai/03-engineering/harness-engineering/README.md) |
| [Loop Engineering](loop-engineering/) | ⭐⭐⭐⭐ | 3 大组件 + 4 大失败模式 + 5 大最佳实践 | [03-engineering/loop-engineering](../../11.ai/03-engineering/loop-engineering/README.md) |
| [Transformer 架构](transformer/) | ⭐⭐⭐⭐⭐ | Self-Attention / QKV / Positional Encoding / FFN | [01-fundamentals/transformer](../../11.ai/01-fundamentals/transformer/README.md) |
| [Token 原理](token/) | ⭐⭐⭐ | BPE / SentencePiece / Tokenizer / 计费模型 | [02-technology-stack/token-billing](../../11.ai/02-technology-stack/token-billing/README.md) |
| [RAG 检索增强生成](rag/) | ⭐⭐⭐⭐⭐ | Embedding + Vector DB + Retrieval + Generation | [07-llmops/01-rag-vs-finetuning](../../11.ai/07-llmops/01-rag-vs-finetuning/README.md) |
| [Function Calling / Tool Use](function-calling/) | ⭐⭐⭐⭐⭐ | 工具调用原理 / Schema / ReAct Agent 集成 | [02-technology-stack/function-calling](../../11.ai/02-technology-stack/function-calling/README.md) |
| [Agent DAG vs ReAct](agent-dag-vs-react/) | ⭐⭐⭐⭐⭐ | 复杂 Agent 为什么采用 DAG Workflow | [04-architecture/agent-architecture](../../11.ai/04-architecture/agent-architecture/README.md) |

---

## 学习路径

1. **入门**（3 天）：AI 思维 + Token 概念 + 基础 Prompt
2. **进阶**（2 周）：Transformer + RAG + Function Calling
3. **AI 工程 4 阶段演进**：Prompt → Context → Harness → Loop
4. **AI 生产力度量**（2026 新增）：生产力悖论 + 代码流失率 + ROI 度量
5. **冲刺面试**：重点看"RAG 架构"、"幻觉问题"、"Agent 设计"、"Context/Harness/Loop Engineering"、"DAG vs ReAct"、"AI 编程生产力悖论"

## 使用建议

- 概念文章先看主模块建立完整认知，再看本目录的精炼版掌握陷阱和话术
- 每篇文章末尾都有"深度阅读"区，链接回主模块完整内容
- 一篇文章 50-80 行，可在 10-15 分钟内复习完，适合面试前过一遍

## 相关章节

- 主模块：[`note/11.ai`](../../11.ai/) — AI 知识体系完整内容
- 相关章节：[`09.front-end`](../09.front-end/)（前端集成 AI）

← [返回咬文嚼字（高频面试题）](../README.md)