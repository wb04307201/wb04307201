<!--
module:
  parent: split-hairs
  slug: 11.ai
  type: article
  category: 高频面试题
  summary: AI 高频面试题与新概念深挖（6 篇纯面试题 + 9 篇主模块精炼版）
question:
  id: 11.ai-11.ai
  topic: 11.ai
  difficulty: ⭐⭐
  frequency: 高频
  scenario_type: 反直觉代码
  tags: [11.ai]
-->

# AI 咬文嚼字

> AI 高频面试题与新概念深挖，对齐主模块 [`11.ai`](../../11.ai/)。18 题 = 9 篇纯面试题（幻觉 / 思维 / 生产力悖论 / 代码流失 / ROI / Agent Memory / Agent 性能量化 / Token 经济学 / LLM Benchmark / RAG 权限隔离）+ 9 篇主模块配套精炼版（Prompt / Context / Harness / Loop / Transformer / Token / RAG / Function Calling / Agent DAG）。

> ⚠️ **定位说明**：本目录所有文章都是**面试深挖版**（陷阱 + 反直觉 + 30 秒话术，50-80 行）。完整概念文档见主模块对应位置（README 末尾"深度阅读"区有链接）。

---

## 文章清单（20 题 = 9 篇纯面试题 + 11 篇精炼版）

### 🎯 真正的面试题（一题一文）

| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [AI 思维：抛硬币](ai-thinking/) | ⭐⭐ | 100 次正面后第 101 次概率？数学 vs AI 思维差异 |
| [LLM 幻觉问题](hallucination/) | ⭐⭐⭐⭐ | 幻觉成因 / 分类 / 检测与缓解方案 / 高风险 Fallback |
| [AI 编程生产力悖论](ai-coding-productivity-paradox/) | ⭐⭐⭐⭐ | Waydev/GitClear/Faros/Jellyfish 4 大研究 + DORA 框架 |
| [AI 代码流失率](ai-code-churn/) | ⭐⭐⭐⭐ | 采纳率 80% vs 留存率 30% 的真相 + 6 大改进策略 |
| [AI 编程 ROI 度量](ai-coding-roi/) | ⭐⭐⭐⭐ | DORA 4 指标 + SPACE 5 维度 + 改进策略 |
| [Agent Memory 分类](agent-memory-classification/) | ⭐⭐⭐⭐ | 时间×认知×工程三维分类法 + 5 大框架 + 30/60/90 秒话术 |
| [如何量化 Agent 性能](agent-performance-evaluation/) | ⭐⭐⭐⭐⭐ | 6 大指标维度（任务完成率/步骤效率/工具使用/成本/满意度/稳定性）+ 5 种评估方法 |
| [RAG 权限隔离设计](rag-permission-isolation/) | ⭐⭐⭐⭐⭐ | 4 种隔离方案 + pre/post-filtering + ACL 同步 + 多租户 |
| [AI 编程 Token 经济学](ai-coding-token-economics/) | ⭐⭐⭐⭐ | 9.6 万 Token 中位数 + 杠杆率 + Token 悖论 + 企业案例 |
| [LLM Benchmark 深度剖析](llm-benchmark/) | ⭐⭐⭐⭐ | MMLU/HumanEval/Arena ELO + 数据污染 + 5 大问题 |
| **🆕 [Agent Evaluation 评测系统](agent-performance-evaluation/)** | ⭐⭐⭐⭐⭐ | 阿里一面原题 · 6 大评测维度 + 5 种方法 + 4 阶段 Pipeline + 7 反模式 | [05-agent-evaluation](../../11.ai/05-agent-evaluation/README.md) |

### 📚 概念精炼版（主模块配套面试深挖）

| 主题 | 难度 | 核心问题 | 主模块位置 |
|------|------|---------|----------|
| [Prompt Engineering](prompt-engineering/) | ⭐⭐⭐⭐ | 8 种核心技巧 + 陷阱 + 注入防御 | [02-technology-stack/prompt-engineering](../../11.ai/02-technology-stack/prompt-engineering/README.md) |
| [Context Engineering](context-engineering/) | ⭐⭐⭐⭐ | 4 大原则 + Lost in Middle + 演进路径 | [02-technology-stack/context-engineering](../../11.ai/02-technology-stack/context-engineering/README.md) |
| [Harness Engineering](harness-engineering/) | ⭐⭐⭐⭐ | 4 大 Harness 类型 + OpenSpec + 4 原则 | [03-engineering/harness-engineering](../../11.ai/03-engineering/harness-engineering/README.md) |
| [Loop Engineering](loop-engineering/) | ⭐⭐⭐⭐ | 3 大组件 + 6 大陷阱（含 Fresh Context 架构）+ Ralph Wiggum Loop | [03-engineering/loop-engineering](../../11.ai/03-engineering/loop-engineering/README.md) |
| [Transformer 架构](transformer/) | ⭐⭐⭐⭐⭐ | Self-Attention / QKV / Positional Encoding / FFN | [01-fundamentals/transformer](../../11.ai/01-fundamentals/transformer/README.md) |
| [Token 原理](token/) | ⭐⭐⭐ | BPE / SentencePiece / Tokenizer / 计费模型 | [02-technology-stack/token-billing](../../11.ai/02-technology-stack/token-billing/README.md) |
| [RAG 检索增强生成](rag/) | ⭐⭐⭐⭐⭐ | Embedding + Vector DB + Retrieval + Generation | [07-llmops/01-rag-vs-finetuning](../../11.ai/07-llmops/01-rag-vs-finetuning/README.md) |
| [Function Calling / Tool Use](function-calling/) | ⭐⭐⭐⭐⭐ | 工具调用原理 / Schema / ReAct Agent 集成 | [02-technology-stack/function-calling](../../11.ai/02-technology-stack/function-calling/README.md) |
| [Agent DAG vs ReAct](agent-dag-vs-react/) | ⭐⭐⭐⭐⭐ | 复杂 Agent 为什么采用 DAG Workflow | [04-architecture/agent-architecture](../../11.ai/04-architecture/agent-architecture/README.md) |
| **🆕 [ReAct vs Plan-and-Execute](react-vs-plan-execute/)** | ⭐⭐⭐⭐⭐ | 4 模式 6 维打分 + RePlan 3 机制 + 80% 是混合架构 + 7 道 Q&A | [04-architecture/agent-execution-patterns](../../11.ai/04-architecture/agent-execution-patterns/README.md) |
| [Skill 设计方法论](skill-design/) | ⭐⭐⭐⭐ | 决策树（写 Skill vs CLAUDE.md / Hook / MCP）+ 6 字段 frontmatter + YAML 模板 | [03-engineering/claude-code-practices/skill-design](../../11.ai/03-engineering/claude-code-practices/skill-design.md) |
| [Skill 命中率](skill-hit-rate/) | ⭐⭐⭐⭐ | 数量爆炸后 4 层模型（描述 / 路由 / 加载 / 评估）+ 5 大反模式 + 65% → 92% 实战 | [03-engineering/claude-code-practices/skill-hit-rate](../../11.ai/03-engineering/claude-code-practices/skill-hit-rate.md) |
| **🆕 [工业部署推理引擎选型](inference-engine-selection/)** | ⭐⭐⭐⭐⭐ | vLLM vs Ollama 5 大理由 + PagedAttention + 连续批处理 + 4 引擎对比 + 7 道 Q&A | [03-engineering/ai-platforms/vllm-vs-ollama](../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/README.md) |
| **🆕 [Agent 长上下文策略](long-context-agent-strategy/)** | ⭐⭐⭐⭐⭐ | 6 大策略组合（Chunking / RAG / Memory / Sliding Window / Sub-Agents / Long-Context）+ Lost in Middle + 7 道 Q&A | [04-architecture/agent-context](../../11.ai/04-architecture/agent-context/README.md) |
| **🆕 [大模型思维工程 5 问](production-thinking-5q/)** | ⭐⭐⭐⭐⭐ | 5 大灵魂拷问（Prompt vs if-else / 成本降级 / 一致性 / 超时熔断 / 监控定位）+ 5 层路由 + 双 timeout + 6 道 Q&A | [03-engineering/llm-production-thinking](../../11.ai/03-engineering/llm-production-thinking/README.md) |

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