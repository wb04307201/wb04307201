<!--
module:
  parent: ai/04-architecture
  slug: ai/agent-architecture/agent-execution-patterns
  type: deep-dive
  category: Agent 执行模式
  summary: AI Agent 4 大执行模式深度对比 —— ReAct / Plan-and-Execute / DAG / Multi-Agent 的 6 维对比 + 场景化选型 + Plan-and-Execute 重规划机制
-->

# Agent 4 大执行模式深度专题

> **一句话答案**：4 大模式**没有绝对优劣**——ReAct 用于"探索"、Plan-and-Execute 用于"复杂任务"、DAG 用于"确定性"、Multi-Agent 用于"复杂协作"。生产环境通常是 **混合（DAG + Loop + Plan Repair）**。

← [返回: L4 架构设计](../README.md) · 同级：[agent-context](../agent-context/README.md) · [agent-memory](../agent-memory/README.md)

---

## 0. 面试高频拷问

```
Q：在构建 AI Agent 系统时，ReAct 和 Plan-and-Execute 是两种主流的执行模式，
   各有其独特的特点和适用场景。如何选？
```

**回答框架（4 层递进）**：

1. **场景区分**：ReAct 用于"探索"（未知多）vs Plan-and-Execute 用于"清晰目标 + 多步依赖"
2. **6 维对比**：灵活 / 可预测 / Token / 延迟 / 复现 / 复杂度
3. **重规划机制**：Plan-and-Execute 的核心是"Plan Repair"能力
4. **何时反选**：什么场景下 ReAct 比 Plan-and-Execute 更优

完整 5-7 道精选面试题见 [13.split-hairs/11.ai/react-vs-plan-execute](../../../13.split-hairs/11.ai/react-vs-plan-execute/README.md)。

---

## 1. 4 大模式速览

| 模式 | 全称 | 核心思想 | 代表项目 | 适用 |
|------|------|---------|---------|------|
| **ReAct** | Reasoning + Acting | 思考→行动→观察→循环 | BabyAGI, AutoGPT, ReAct paper | 探索 / 未知场景 |
| **Plan-and-Execute** | Plan-then-Execute | 先规划再执行，失败重规划 | LangChain Plan-and-Execute, Devin | 复杂多步任务 |
| **DAG Workflow** | Directed Acyclic Graph | 节点 + 边的确定性图 | LangGraph, Temporal, Cursor Composer | 确定性流程 |
| **Multi-Agent** | Multi-Agent System | 多个 Agent 协作 | CrewAI, AutoGen, MetaGPT | 复杂协作任务 |

---

## 2. 6 维核心对比

| 维度 | ReAct | Plan-and-Execute | DAG | Multi-Agent |
|------|-------|------------------|-----|-------------|
| **灵活性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **可预测性** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Token 成本** | 高 | 中 | 低 | 高 |
| **延迟** | 高 | 中 | 低 | 高 |
| **可复现性** | 差 | 中 | 好 | 差 |
| **工程复杂度** | 低 | 中 | 高 | 高 |

**一句话总结**：ReAct 灵活但贵、Plan-and-Execute 平衡、DAG 稳定但缺灵活、Multi-Agent 强大但复杂。

---

## 3. 子章节导航

| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [ReAct 深度](01-react-deep-dive.md) | ReAct 怎么"循环"？何时不可控？Token 失控的场景？ |
| 02 | [Plan-and-Execute 深度](02-plan-and-execute-deep-dive.md) | Plan 怎么做？RePlan / Adaptive / Plan-Repair 怎么选？失败如何修复？ |
| 03 | [6 维对比](03-six-dimensions-comparison.md) | 4 模式在 6 维度上的完整对比 + 各模式典型代表 |
| 04 | [选型决策树](04-selection-decision-tree.md) | "我是 X 场景，应该选 Y 模式"的决策流程 + 反模式 |
| 05 | [DAG 深度](05-dag-deep-dive.md) | 节点设计 + 错误恢复 + Loop 节点 + 反模式 |
| 06 | [Multi-Agent 深度](06-multi-agent-deep-dive.md) | 通信协议 + 协调者模式 + 循环调用防护 + 反模式 |

---

## 4. 反直觉点

- ⚠️ **"ReAct 等于 Agent"是错觉** —— ReAct 是**模式**之一，不是唯一。70%+ 复杂 Agent 是 ReAct + 其他模式混合
- ⚠️ **"Plan-and-Execute 不灵活"是错觉** —— 现代 Plan-and-Execute 支持 **Plan Repair**（失败修复），并不死板
- ⚠️ **"DAG 不能处理未知"是错觉** —— DAG 配合 **Loop 节点** + **Plan Repair 节点**可处理动态场景
- ⚠️ **"Multi-Agent 比单 Agent 强"是营销话术** —— 通信成本 + 调试难度 + Token 消耗 = 80% 场景不如单 Agent

---

## 5. 一句话速查

```
"Agent 4 大模式选型：
- 探索 / 未知多 → ReAct
- 复杂多步 / 目标清晰 → Plan-and-Execute
- 确定性 / 高合规 → DAG
- 复杂协作 → Multi-Agent
关键：生产环境通常是 2-3 种模式混合（DAG 主流程 + ReAct 兜底 + Plan Repair 修复）。"
```

---

## 6. 速查 · 关联资源

- 🆕 **入口路由**：[分层路由架构](../routing-architecture/README.md) —— 简单问答 Fast Path + 复杂 Agent Path 的统一入口设计
- **餐厅叙事**：[12.story/02-system-architecture-evolution.md](../../../12.story/02-system-architecture-evolution.md) —— 阿明餐厅选型 ReAct vs Plan-and-Execute 实战
- **面试题**：[13.split-hairs/11.ai/react-vs-plan-execute](../../../13.split-hairs/11.ai/react-vs-plan-execute/README.md) —— 5-7 道精选题
- **同级**：[agent-architecture](../agent-architecture/README.md) —— 4 模式综述 + DAG 决策树
- **相关**：[agent-context/05-sub-agents](../agent-context/05-sub-agents-decomposition.md) —— Multi-Agent Sub-Agents 实战

---

← [返回: L4 架构设计](../README.md)
