<!--module:
  parent: ai-applications
  slug: ai-applications/agent
  type: index
  category: AI 应用子 MOC
  summary: Agent 主题索引——架构 / 上下文 / 评测 / 执行模式 / 记忆 / 可靠性 / Spec 工具 / 案例 / 编程 Agent / 本体驱动 / 生产实践。
  depth: ⭐⭐⭐
-->

# Agent（智能体）

> **定位**：MOC——Agent 主题索引，覆盖架构 / 上下文 / 评测 / 执行模式 / 记忆 / 可靠性 / Spec 工具 / 案例 / 编程 Agent / 本体驱动 / 生产实践 / 系统设计。
> **继承规范**：[../SPEC.md](../SPEC.md)

## 主题清单

| # | 子主题 | 路径 | 摘要 |
|---|--------|------|------|
| 1 | Agent 架构 | [agent-architecture/](agent-architecture/README.md) | DAG vs ReAct vs Plan-and-Execute 三大范式对比 + 选型决策树 |
| 2 | Agent 长上下文 | [agent-context/](agent-context/README.md) | 6 大策略（Chunking/RAG/Memory/Sliding Window/Sub-Agents/Long-Context） |
| 3 | Agent 评测 | [agent-evaluation/](agent-evaluation/README.md) | 6 大评测维度 + 5 种方法 + 阿里一面实战 + 7 反模式 |
| 4 | Agent 4 大执行模式 | [agent-execution-patterns/](agent-execution-patterns/README.md) | ReAct / Plan-and-Execute / DAG / Multi-Agent 6 维对比 + Planning-Acting-Monitoring |
| 5 | Loop 工程 | [loop-engineering/](loop-engineering/README.md) | 循环执行机制——自动修复 / 验证器 / 循环命令 / IDE 案例 |
| 6 | Agent 记忆 | [agent-memory/](agent-memory/README.md) | 4 层记忆架构（working/episodic/semantic/procedural）+ Shared Memory |
| 7 | Agent 可靠性 | [agent-reliability/](agent-reliability/README.md) | 4 大可靠性机制 + 失败恢复 + 监控 |
| 8 | Agent Spec 工具 | [agent-spec-tools/](agent-spec-tools/README.md) | Superpowers / Spec-Kit / OpenSpec 三工具对比与组合 |
| 9 | 真实案例 | [case-studies/](case-studies/README.md) | Salesforce Agentforce / Shopify AI Agent 等 |
| 10 | 编程 Agent | [coding-agents/](coding-agents/README.md) | Claude Code / Codex / OpenCode / OMP 四大编程 Agent |
| 11 | 本体驱动 Agent | [ontology-driven-agent/](ontology-driven-agent/README.md) | 本体论驱动的 Agent 架构 |
| 12 | 生产级 Agent | [production-agent/](production-agent/README.md) | 生产环境 Agent 工程实践 |
| 13 | 生产稳定性 | [production-stability/](production-stability/README.md) | 思维范式 / 成本控制 / 熔断 / 监控 / 选型决策树 |
| 14 | 生产级 Agent 系统设计 | [production-agent-system-design/](production-agent-system-design/README.md) | 高可用 Agent 架构 + 容量评估 + 容灾 |
| 15 | AI 平台 | [ai-platforms/](ai-platforms/README.md) | Coze / Dify / LangGraph / Spring AI 平台选型对比 |

## 阅读路径

```text
先建全景            agent-architecture（架构综述）+ agent-memory（记忆）
    ↓
深入核心机制         agent-execution-patterns（4 模式）+ agent-context（长上下文）
    ↓
落地实践            production-agent（生产实践）+ agent-reliability（可靠性）
    ↓
量化与治理           agent-evaluation（评测）+ case-studies（真实案例）
    ↓
工具与协作           agent-spec-tools（规范工具）+ coding-agents（编程 Agent）
```

## 关联主题

- [../prompts/](../prompts/) — Prompt 工程
- [../rag/](../rag/) — RAG（含 04-evaluation 评估）
- [../llm-inference/](../llm-inference/) — LLM 推理（Agent 基础设施）
- [../../08.ai-foundations/](../../../note/08.ai-foundations/) — AI 基础（Transformer / LLM / Embedding）

## 与其他模块的缺口（已知）

> ⚠️ **`agent-evaluation/` 系列文章原为 01–09 连续编号；09-rag-evaluation 已被 Task 13 迁至 `../rag/04-evaluation.md`**。本目录系列现为 01–08，9 号断号，详见 [agent-evaluation/README.md](agent-evaluation/README.md)。

> ⚠️ **`agent-context/02-rag-in-agent.md`** 虽匹配 RAG 关键词，但属于 `agent-context/` 7 章系列，**有意保留**在 Agent 主题（而非 RAG MOC），详见 Task 13 报告 P2。

## 尚未迁移的 Agent 相关章节

以下 Agent 相关主题将在 Phase 1+ 迁入本 MOC（占位路径已映射）：

- ⚠️ Function Calling 工具调用 — `./agent-spec-tools/function-calling/`
- ⚠️ Context Engineering — `../prompts/context-engineering/`
- ⚠️ 入口路由架构 — `./architecture/routing-architecture/`
- ⚠️ 智能系统分层 — `./architecture/intelligent-system-layers/`

---

← [返回 09.ai-applications](../README.md)
