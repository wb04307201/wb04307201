<!--module:
  parent: 09.ai-applications
  slug: 09.ai-applications/agent/architecture
  type: index-only
  category: Agent 子模块索引
  summary: Agent 系统级架构模式——传统工作流引擎（BPMN）与 AI 智能体的融合实践。
-->

# Agent 架构（Architecture）

> ⬅️ [返回 09.ai-applications Agent 目录](../README.md)

## 📍 一句话定位

**Agent 架构 = 在确定性骨架（BPMN / 状态机）中嵌入 AI 推理节点**——用工作流引擎管"流程编排 + 合规审计"，用 AI 管"灵活推理 + 概率决策"，是 2025-2026 年企业级 Agent 落地的生产范式。

## 🗂️ 文章清单

| # | 主题 | 难度 | 路径 | 核心内容 |
|---|------|------|------|---------|
| 1 | BPMN 与 AI 集成 | ⭐⭐⭐⭐ | [bpmn-ai-integration.md](./bpmn-ai-integration.md) | 4 大融合模式（LLM 包装为 Service Task / AI 节点嵌入 / 流程生成式编排 / 端到端 BPMN+AI 协同），含 Camunda 8.5+ `fromAi()` FEEL 表达式、Mermaid 流程图与企业级落地案例 |

> 📌 本目录当前聚焦"传统工作流引擎 × AI 智能体"融合主题；后续将扩展入口路由架构（routing-architecture）、Context Engineering 等子主题。

## 🔗 关联主题

- [../agent-execution-patterns/](../agent-execution-patterns/) — Agent 4 大执行模式（ReAct / Plan-and-Execute / DAG / Multi-Agent），架构落地的执行层选择
- [../agent-spec-tools/](../agent-spec-tools/) — Superpowers / Spec-Kit / OpenSpec 规范工具，架构落地的需求侧管理
- [../case-studies/](../case-studies/) — Salesforce Agentforce / Shopify AI Agent 等真实案例，看架构如何落到生产
- [../production-agent-system-design/](../production-agent-system-design/) — 高可用 Agent 架构 + 容量评估 + 容灾，是架构的工程化延伸
- [09.ai-applications/llm-inference](../../llm-inference/README.md) — LLM 推理层（KV Cache / Flash Attention），架构的性能底座

## 📚 学习路径

1. **先读 BPMN 基础**：理解 BPMN 流程引擎的核心概念（Service Task / User Task / FEEL 表达式），这是后续"AI 嵌入 BPMN"的骨架
2. **再读 [bpmn-ai-integration.md](./bpmn-ai-integration.md)**：掌握 4 大融合模式 + Camunda 8.5+ `fromAi()` 调用方式 + Mermaid 流程图示例
3. **横向对比执行模式**：跳到 [../agent-execution-patterns/](../agent-execution-patterns/)，看 ReAct / Plan-and-Execute / DAG 与 BPMN 范式的差异与互补
4. **学企业级案例**：读 [../case-studies/](../case-studies/) 中的 Salesforce Agentforce，理解架构在真实生产环境如何落地
5. **最后看高可用**：读 [../production-agent-system-design/](../production-agent-system-design/)，了解架构的容灾、容量评估、可用性保障

## 🎯 为什么需要"架构"层抽象？

单纯 LLM 调用（Prompt → Answer）解决不了企业级问题：

- **审计压力**：金融/医疗场景必须能追溯"哪一步决策由谁做出"
- **合规要求**：长流程必须支持 SLA 升级、超时降级、人工介入
- **确定性 vs 概率性张力**：业务流程需要确定性骨架，但 AI 输出本质是概率性的

→ BPMN 范式正好提供了**可视化流程 + 审计 trail + SLA 机制**，是 AI 落地的天然搭档。

## 🧭 与"纯 Agent"范式的边界

| 维度 | 纯 Agent（ReAct/DAG） | BPMN+AI 融合 |
|------|--------------------|-------------|
| 流程定义 | LLM 自主规划 | 工程师预定义 BPMN 流程图 |
| 合规审计 | 弱（黑盒推理） | 强（BPMN 实例全追溯） |
| 长流程管理 | 弱（context 累积漂移） | 强（BPMN 提供 SLA + 升级） |
| Token 成本 | 不可控（循环调用风险） | 可控（每步 Service Task 独立计费） |
| 适用场景 | 探索型任务 / R&D | 生产型企业流程 |

## 📊 本节统计

> 本目录当前收录 1 篇子文章（BPMN × AI 集成），由 `find` 在 `2026-08-20` 校对。

---

← [返回 Agent 目录](../README.md)