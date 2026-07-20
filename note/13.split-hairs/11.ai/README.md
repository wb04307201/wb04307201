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

> AI 高频面试题与新概念深挖，对齐主模块 [`11.ai`](../../11.ai/)。**40 题**（find 校对 2026-07-19）= 一题一文（幻觉 / 思维 / 生产力悖论 / 代码流失 / ROI / Agent Memory / Agent 性能量化 / Token 经济学 / LLM Benchmark / RAG 权限隔离）+ 主模块配套精炼版（Prompt / Context / Harness / Loop / Transformer / Token / RAG / Function Calling / Agent DAG）。

> ⚠️ **定位说明**：本目录所有文章都是**面试深挖版**（陷阱 + 反直觉 + 30 秒话术，50-80 行）。完整概念文档见主模块对应位置（README 末尾"深度阅读"区有链接）。

---

## 🎯 读者角色速查（按身份挑题）

> **40 题**按难度与场景覆盖 6 类读者角色（find 校对 2026-07-19），按身份挑题效率最高。

| 读者角色 | 推荐题号 | 推荐阅读顺序 | 关键场景 |
|---------|---------|------------|---------|
| **Java 后端转 AI 应用** | 6-10, 17, 22-23, 35 | Transformer → Token → Prompt → Context → Function Calling → RAG | 大模型应用整合到现有业务 |
| **AI 算法工程师** | 1-2, 17, 26, 35 | Transformer → LLM Benchmark → Token 经济学 → RAG → LLM-as-Judge | 模型选型 / 评测 / 优化 |
| **前端 / 全栈** | 6, 9-10, 17, 32 | Prompt → Context → Function Calling → RAG → Agent Memory | AI 能力嵌入前端 / 全栈产品 |
| **架构师 / CTO** | 4-5, 8, 24, 28, 33-34 | AI 编程悖论 → AI 代码流失率 → Agent A/B Test → Multi-Agent → Agent Memory | AI 转型战略 / 技术选型 |
| **产品 / PM / 业务** | 3-5, 8, 24 | AI 思维 → AI 编程悖论 → Agent 性能量化 → Multi-Agent | AI 产品价值评估 / ROI 度量 |
| **面试高频精刷（校招）** | 1-2, 6-7, 9-10, 17, 32 | AI 思维 → Transformer → Prompt → Context → Function Calling → RAG → Agent Memory | 校招面试核心 8 题 |

---

## 文章清单（共 **40 题**，find 校对 2026-07-19）

### 🎯 真正的面试题（一题一文）

| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [AI 思维：抛硬币](ai-thinking/) | ⭐⭐ | 100 次正面后第 101 次概率？数学 vs AI 思维差异 |
| [LLM 幻觉问题](hallucination/) | ⭐⭐⭐⭐ | 幻觉成因 / 分类 / 检测与缓解方案 / 高风险 Fallback |
| [AI 编程生产力悖论](ai-coding-productivity-paradox/) | ⭐⭐⭐⭐ | Waydev/GitClear/Faros/Jellyfish 4 大研究 + DORA 框架 |
| [AI 代码流失率](ai-code-churn/) | ⭐⭐⭐⭐ | 采纳率 80% vs 留存率 30% 的真相 + 6 大改进策略 |
| [AI 编程 ROI 度量](ai-coding-roi/) | ⭐⭐⭐⭐ | DORA 4 指标 + SPACE 5 维度 + 改进策略 |
| **🆕 [AI 后端代码审核验收](ai-code-review/)** | ⭐⭐⭐⭐ | 6 层审核体系（契约/业务/安全/性能/可测/幻觉）+ 分级门禁 + "绿色测试"陷阱 |
| [Agent Memory 分类](agent-memory-classification/) | ⭐⭐⭐⭐ | 时间×认知×工程三维分类法 + 5 大框架 + 30/60/90 秒话术 |
| [如何量化 Agent 性能](agent-performance-evaluation/) | ⭐⭐⭐⭐⭐ | 6 大指标维度（任务完成率/步骤效率/工具使用/成本/满意度/稳定性）+ 5 种评估方法 |
| [RAG 权限隔离设计](rag-permission-isolation/) | ⭐⭐⭐⭐⭐ | 4 种隔离方案 + pre/post-filtering + ACL 同步 + 多租户 |
| [AI 编程 Token 经济学](ai-coding-token-economics/) | ⭐⭐⭐⭐ | 9.6 万 Token 中位数 + 杠杆率 + Token 悖论 + 企业案例 |
| [LLM Benchmark 深度剖析](llm-benchmark/) | ⭐⭐⭐⭐ | MMLU/HumanEval/Arena ELO + 数据污染 + 5 大问题 |
| **🆕 [Agent Evaluation 评测系统](agent-performance-evaluation/)** | ⭐⭐⭐⭐⭐ | 阿里一面原题 · 6 大评测维度 + 5 种方法 + 4 阶段 Pipeline + 7 反模式 | [agent-evaluation](../../11.ai/08-llmops/agent-evaluation/README.md) |

### 📚 概念精炼版（主模块配套面试深挖）

| 主题 | 难度 | 核心问题 | 主模块位置 |
|------|------|---------|----------|
| [Prompt Engineering](prompt-engineering/) | ⭐⭐⭐⭐ | 8 种核心技巧 + 陷阱 + 注入防御 | [02-technology-stack/prompt-engineering](../../11.ai/02-technology-stack/prompt-engineering/README.md) |
| 🆕 [Temperature=0 误区](temperature-zero-myth/) | ⭐⭐⭐⭐ | 5 大根因 + 3 大防御 + Provider 差异 + 90 秒面试话术 | [03-consistency-and-failure-handling](../../11.ai/03-engineering/llm-production-thinking/03-consistency-and-failure-handling.md) |
| [Context Engineering](context-engineering-interview/) | ⭐⭐⭐⭐ | 4 大原则 + Lost in Middle + 演进路径 | [02-technology-stack/context-engineering](../../11.ai/02-technology-stack/context-engineering/README.md) |
| [Harness Engineering](harness-engineering/) | ⭐⭐⭐⭐ | 4 大 Harness 类型 + OpenSpec + 4 原则 | [03-engineering/harness-engineering](../../11.ai/03-engineering/harness-engineering/README.md) |
| [Loop Engineering](loop-engineering/) | ⭐⭐⭐⭐ | 3 大组件 + 6 大陷阱（含 Fresh Context 架构）+ Ralph Wiggum Loop | [03-engineering/loop-engineering](../../11.ai/03-engineering/loop-engineering/README.md) |
| [Transformer 架构](transformer/) | ⭐⭐⭐⭐⭐ | Self-Attention / QKV / Positional Encoding / FFN | [01-fundamentals/transformer](../../11.ai/01-fundamentals/transformer/README.md) |
| [LLM 推理优化](llm-inference/) | ⭐⭐⭐⭐ | Continuous Batching / PagedAttention / KV Cache / 量化 | [02-technology-stack/llm-inference-optimization](../../11.ai/02-technology-stack/llm-inference-optimization/README.md) |
| [LLM 对齐方法](llm-alignment/) | ⭐⭐⭐⭐ | RLHF / DPO / Constitutional AI / 5 大对齐方法 | [03-engineering/llm-alignment](../../11.ai/03-engineering/llm-alignment/README.md) |
| [Token 原理](token/) | ⭐⭐⭐ | BPE / SentencePiece / Tokenizer / 计费模型 | [02-technology-stack/token-billing](../../11.ai/02-technology-stack/token-billing/README.md) |
| [RAG 检索增强生成](rag/) | ⭐⭐⭐⭐⭐ | Embedding + Vector DB + Retrieval + Generation | [08-llmops/01-rag-vs-finetuning](../../11.ai/08-llmops/01-rag-vs-finetuning/README.md) |
| [Function Calling / Tool Use](function-calling/) | ⭐⭐⭐⭐⭐ | 工具调用原理 / Schema / ReAct Agent 集成 | [02-technology-stack/function-calling](../../11.ai/02-technology-stack/function-calling/README.md) |
| 🆕 [Multi-turn Tool Reasoning](multi-turn-tool-reasoning/) | ⭐⭐⭐⭐⭐ | 5 大场景（1 turn 解决不了）+ 6 大编排模式 + 4 大防御 + 90 秒话术 | [Function Calling 深度 第 4 节](../../11.ai/02-technology-stack/function-calling/README.md) |
| 🆕 [Multi-Agent 系统设计 + 死循环防护](multi-agent-system-design/) | ⭐⭐⭐⭐⭐ | 5 大组件（角色+协调者+通信+状态+终止）+ 3 种通信模式 + 4 大防护机制 + 6 大反模式 + 90 秒话术 | [06-multi-agent-deep-dive](../../11.ai/04-architecture/agent-execution-patterns/06-multi-agent-deep-dive.md) |
| 🆕 [Incremental Embedding 增量向量化](incremental-embedding/) | ⭐⭐⭐⭐ | 5 大增量策略（消息队列/异步/hot-cold/版本/监控）+ 4 大模型升级方案（双写/重读/异步迁移/灰度）+ 4 大反模式 + 90 秒话术 | [vector-search-at-scale 第 5.1 节](../../11.ai/02-technology-stack/vector-search-at-scale/README.md) |
| 🆕 [多 Agent 共享记忆](multi-agent-shared-memory/) | ⭐⭐⭐⭐⭐ | 5 大内容维度（上下文/事实/任务/技能/Memory 4 层）+ 3 实现层（消息/状态/语义）+ 6 大共享模式 + 5 大反模式 + 90 秒话术 | [agent-memory 共享专章](../../11.ai/04-architecture/agent-memory/shared-memory.md) |
| 🆕 [RAG 超范围拒答](rag-out-of-domain-rejection/) | ⭐⭐⭐⭐⭐ | 6 大检测机制（分数/距离/OOD/NLI/Self-Consistency）+ 5 大拒答模式（Hard/Soft/Partial/Deflect/Escalate）+ 4 步阈值调优 + 5 反模式 + 90 秒话术 | [08-llmops/06 专章](../../11.ai/08-llmops/06-rag-out-of-domain-rejection/README.md) |
| 🆕 [Agent A/B Test 系统设计](agent-ab-testing/) | ⭐⭐⭐⭐⭐ | 5 大组件（流量/配置/指标/统计/决策）+ 4 流量分配（hash/sticky/分层/Holdout）+ 显著性检验（t-test/Bonferroni/Sequential）+ 5 反模式 + 90 秒话术 | [agent-evaluation/02 专章](../../11.ai/08-llmops/agent-evaluation/02-ab-testing-design/README.md) |
| [Agent DAG vs ReAct](agent-dag-vs-react/) | ⭐⭐⭐⭐⭐ | 复杂 Agent 为什么采用 DAG Workflow | [04-architecture/agent-architecture](../../11.ai/04-architecture/agent-architecture/README.md) |
| **🆕 [ReAct vs Plan-and-Execute](react-vs-plan-execute/)** | ⭐⭐⭐⭐⭐ | 4 模式 6 维打分 + RePlan 3 机制 + 80% 是混合架构 + 7 道 Q&A | [04-architecture/agent-execution-patterns](../../11.ai/04-architecture/agent-execution-patterns/README.md) |
| [10亿级向量检索](vector-search-algorithms/) | ⭐⭐⭐⭐⭐ | HNSW vs IVF vs DiskANN 4 维选型 + 内存/磁盘/QPS/Recall 权衡 | [02-technology-stack/vector-search-algorithms](../../11.ai/02-technology-stack/vector-search-algorithms/README.md) |
| [千亿级向量检索](vector-search-at-scale/) | ⭐⭐⭐⭐⭐ | 5 关键架构转变 + 业界真实案例 + 5 阶段时延/召回/成本三元权衡 | [02-technology-stack/vector-search-at-scale](../../11.ai/02-technology-stack/vector-search-at-scale/README.md) |
| [万亿级向量检索](vector-search-trillion/) | ⭐⭐⭐⭐⭐ | 万亿级多集群 + 联邦 + TPU + 极限压缩 | [02-technology-stack/vector-search-trillion](../../11.ai/02-technology-stack/vector-search-trillion/README.md) |
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
4. **AI 生产力度量**（2026 新增）：生产力悖论 + 代码流失率 + ROI 度量 + 后端代码审核验收
5. **冲刺面试**：重点看"RAG 架构"、"幻觉问题"、"Agent 设计"、"Context/Harness/Loop Engineering"、"DAG vs ReAct"、"AI 编程生产力悖论"

## 使用建议

- 概念文章先看主模块建立完整认知，再看本目录的精炼版掌握陷阱和话术
- 每篇文章末尾都有"深度阅读"区，链接回主模块完整内容
- 一篇文章 50-80 行，可在 10-15 分钟内复习完，适合面试前过一遍

## 相关章节

- 主模块：[`note/11.ai`](../../11.ai/) — AI 知识体系完整内容
- 相关章节：[`09.front-end`](../09.front-end/)（前端集成 AI）

← [返回咬文嚼字（高频面试题）](../README.md)