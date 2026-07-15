<!--
module:
  parent: ai
  slug: ai/agent-architecture
  type: article
  category: 主模块子文章
  summary: Agent 架构：DAG vs ReAct vs Plan-and-Execute 三种范式对比。
-->

# Agent 架构：DAG vs ReAct vs Plan-and-Execute

← 返回 [架构设计](../README.md)

> 复杂 Agent 为什么越来越多采用 DAG？ReAct 循环与 DAG Workflow 是两大主流架构 —— 它们是互补关系（探索 vs 执行），而非替代关系。生产环境通常是 DAG + Loop 混合。

---
---

## 一、核心结论（TL;DR）

| 架构 | 模式 | 适用场景 |
|------|------|---------|
| **ReAct 循环** | 思考 → 行动 → 观察 → 循环 | 探索性任务 |
| **DAG Workflow** | 有向无环图，节点 + 边 | 确定性流程 |
| **Plan-and-Execute** | 先规划再执行 | 复杂任务 |
| **Multi-Agent** | 多个 Agent 协作 | 复杂业务 |

> 一句话：**ReAct 用于"探索"，DAG 用于"执行"；生产级 Agent 通常是 DAG + Loop 混合**。

---

## 二、ReAct 循环的本质

ReAct（Reasoning + Acting）是最经典的 Agent 循环模式：

```
Thought: 我需要先查询订单
Action: getOrder(order_id="20260628")
Observation: 订单状态：已支付

Thought: 订单已支付，我应该给用户返回结果
Action: 返回订单信息给用户
Observation: 完成
```

**代码示例**：

```python
while not task_completed:
    thought = llm.think(context)        # 思考下一步
    action = llm.choose_tool(thought)   # 选择工具
    observation = execute(action)       # 执行工具
    context.add(thought, action, observation)  # 更新上下文
```

**优点**：
- 灵活：Agent 自己决定下一步
- 适合开放性问题
- 实现简单

**缺点**：
- 不可预测：每次执行路径可能不同
- 调试困难：循环路径不固定
- 容易"迷路"：Context 越长越混乱
- Token 消耗大：每次都要重新"思考"

---

## 三、DAG Workflow 的本质

DAG（Directed Acyclic Graph）是把任务拆成节点，用有向无环图组织：

```
[用户输入]
    ↓
[意图识别] ─→ [订单查询] ─→ [结果格式化] ─→ [返回]
    ↓
[退款申请] ─→ [审核] ─→ [执行退款] ─→ [通知]
```

**代码示例（LangGraph）**：

```python
from langgraph.graph import StateGraph

workflow = StateGraph(State)

# 定义节点
workflow.add_node("intent_classify", classify_intent)
workflow.add_node("query_order", query_order)
workflow.add_node("request_refund", request_refund)
workflow.add_node("format_response", format_response)

# 定义边（流程）
workflow.add_edge("intent_classify", "query_order")
workflow.add_edge("intent_classify", "request_refund")
workflow.add_edge("query_order", "format_response")
workflow.add_edge("request_refund", "format_response")

workflow.set_entry_point("intent_classify")
```

**优点**：
- 可预测：每次执行路径固定
- 易调试：节点 + 边可视化
- 易优化：可以并行执行独立节点
- Token 友好：每个节点只处理自己的子任务

**缺点**：
- 不灵活：固定流程，无法应对未知情况
- 开发成本：需要预先设计节点和边
- 难以处理"未定义流程"

---

## 四、4 大主流 Agent 架构对比

| 架构 | 代表项目 | 优势 | 劣势 |
|------|---------|------|------|
| **ReAct** | BabyAGI, AutoGPT | 灵活、探索 | 不可预测、Token 消耗大 |
| **DAG** | LangGraph, Temporal | 稳定、高效 | 不灵活 |
| **Plan-and-Execute** | Plan-and-Execute Agent | 规划清晰 | 规划可能错误 |
| **Multi-Agent** | CrewAI, AutoGen | 协作能力强 | 通信开销大 |

---

## 五、为什么复杂 Agent 越来越多采用 DAG？

### 1. 稳定性需求

生产环境要求 99.9% 可用，DAG 流程固定、行为可预测。

### 2. 成本控制

ReAct 循环每次调用 LLM，Token 成本不可控；DAG 每个节点只调用一次。

### 3. 调试可观测性

DAG 的执行路径可以用 Trace 工具完整记录，ReAct 循环的路径难以复现。

### 4. 合规需求

金融、医疗等行业要求 Agent 行为可审计，DAG 满足需求。

### 5. 大模型能力提升

2026 年的 LLM 足够强，DAG 的"灵活性不足"问题被 Context Engineering 和 Harness Engineering 弥补。

---

## 六、真实案例

| 产品 | Agent 架构 | 选择理由 |
|------|-----------|---------|
| **Cursor** | DAG（Composer） | 代码生成是确定性流程 |
| **Claude Code** | DAG + Loop | 主流程 DAG + 错误重试 Loop |
| **Devin** | Plan-and-Execute + DAG | 先规划再执行 |
| **ChatGPT Agent** | DAG | 产品化需求 |
| **AutoGPT** | ReAct | 探索性研究 |

---

## 七、何时选 DAG vs ReAct？

```
Q1: 任务流程是否明确？
├── 是 → DAG Workflow
└── 否 → Q2

Q2: 是否需要探索未知信息？
├── 是 → ReAct Loop
└── 否 → DAG Workflow

Q3: 是否有合规/审计要求？
├── 是 → DAG Workflow
└── 否 → Q4

Q4: 是否需要灵活性 > 稳定性？
├── 是 → ReAct Loop
└── 否 → DAG Workflow
```

**推荐**：生产环境用 DAG + Loop 混合（确定性节点用 DAG，探索性节点用 Loop）。

---

## 八、面试陷阱速览

> 完整陷阱 + 反直觉 + 30 秒话术见 [13.split-hairs Agent 架构](../../../13.split-hairs/11.ai/agent-dag-vs-react/README.md)

---

## 相关章节

- 上游：[智能系统分层](../intelligent-system-layers/README.md) — Agent 在分层架构中的位置
- 关联：[Agent Memory 架构](../agent-memory/README.md) — Memory × Agent 执行架构（DAG/ReAct/Plan 的 Memory 特殊要求）
- 关联：[Loop Engineering](../../03-engineering/loop-engineering/README.md) — DAG 的兜底机制
- 关联：[Harness Engineering](../../03-engineering/harness-engineering/README.md) — DAG 是 Harness 的强约束
- 实战：[生产级 Agent](../../03-engineering/production-agent/README.md) — DAG 在生产环境的落地

← [返回: AI 知识体系 · agent-architecture](README.md)

---

## 深度扩展

🆕 **4 模式 6 维深度对比**：[agent-execution-patterns 专题](../agent-execution-patterns/README.md) —— ReAct Thought/Action/Observation 5 硬伤 + Plan-and-Execute 3 大重规划机制（RePlan / Adaptive / Plan Repair）+ 6 维完整打分 + 5 分钟决策树 + 7 道面试题。

🆕 **Agent 评测专题**：[agent-evaluation](../../08-llmops/agent-evaluation/README.md) —— Agent 评测 6 维（任务 40% / 步骤 20% / 工具 10% / 成本 10% / 满意 15% / 稳定 5%）+ 5 种方法 + 4 阶段 Pipeline 1511 行。面试精选 [13.split-hairs Agent 性能评估](../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)。
