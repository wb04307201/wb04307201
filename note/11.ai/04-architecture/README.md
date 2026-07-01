# AI 架构设计

## 引言：架构困境

AI 架构设计 的关键不是'选型'——是**选完之后怎么在 5 个 trade-off 里活下来**。

本篇用'决策困境'切入，比较几种主流路径并讲清取舍。

---

← 返回 [总览](../README.md)

> 从智能系统分层到技术趋势，系统级架构设计参考。

## 子目录

| 目录 | 内容 |
|------|------|
| [intelligent-system-layers](intelligent-system-layers/) | 智能系统三层架构 — 感知与数据层 / 认知与模型层 / 决策与执行层 · AI技术栈分层架构全景 |
| [agent-architecture](agent-architecture/) | **Agent 架构设计** — ReAct / DAG / Plan-and-Execute / Multi-Agent 4 大架构对比 + 选型决策树 + 真实案例 |
| [ontology-driven-agent](ontology-driven-agent/) | **本体驱动的智能体** — 让 AI 从"黑箱推理"走向"结构化认知"，融合符号主义与连接主义，构建可信可审计可演化的 AI 系统 |
| [2026-trends](2026-trends/) | 2026 AI技术矩阵 — 大模型 / 多模态 / 具身智能 三位一体趋势 |

## 学习路径

架构设计承上启下：先理解 [技术栈](../02-technology-stack/) 各层组件，再看 [工程实践](../03-engineering/) 如何落地，最后用本模块的全局视角做系统设计。

## 相关章节

- 上游：[L3 工程实践](../03-engineering/) → **L4 架构设计** → [L5 行业应用](../05-applications/)
- 关联：[04.system-design](../../04.system-design/) — 通用系统设计方法论（DDD、分布式、高可用）
- 关联：[07.workflow BPMN+AI 融合](../../07.workflow/README.md) — 工作流引擎与 AI Agent 集成
