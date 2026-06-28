# Agent 架构：DAG Workflow vs ReAct 循环

> 复杂 Agent 为什么越来越多采用 DAG，而不是简单的 ReAct 循环？考察的是 **Agent 架构选型的工程思维**，不是"哪个更好"。

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

## 八、面试陷阱

### 陷阱 1：以为 ReAct 是"过时"架构

- **真相**：ReAct 仍然是探索性任务的首选，生产环境 ReAct + Harness 也常见

### 陷阱 2：以为 DAG 完全取代 ReAct

- **真相**：DAG 用于"确定性流程"，ReAct 用于"探索性任务"，二者是互补

### 陷阱 3：以为 Multi-Agent 比 DAG 更先进

- **真相**：Multi-Agent 通信开销大，多数场景 DAG + Loop 已足够

### 陷阱 4：以为所有 Agent 都需要"思考"

- **真相**：DAG 中很多节点是纯函数调用，根本不需要 LLM 思考

---

## 九、面试话术模板

> 复杂 Agent 越来越多采用 DAG Workflow，核心原因是生产环境的稳定性、成本、可观测性、合规需求。
>
> ReAct 循环适合"探索性任务"（开放式问题、不确定路径），但生产环境面临 Token 消耗大、调试困难、行为不可预测的问题。
>
> DAG Workflow 适合"确定性流程"（固定路径、明确节点），优势是可预测、易调试、易并行、Token 友好。
>
> 真实选择是 DAG + Loop 混合：主流程 DAG（确定性），错误恢复用 Loop（灵活性）。
>
> Cursor、Claude Code、Devin、ChatGPT Agent 都是 DAG 为主。AutoGPT 这种纯 ReAct 已经退出主流。

---

## 十、相关章节

- 同栏目：[`function-calling`](../function-calling/README.md) — Function Calling 原理
- 同栏目：[`context-engineering`](../context-engineering/README.md) — Context Engineering
- 同栏目：[`harness-engineering`](../harness-engineering/README.md) — Harness Engineering
- 同栏目：[`loop-engineering`](../loop-engineering/README.md) — Loop Engineering
- 主模块：[`11.ai/04-architecture`](../../../../11.ai/04-architecture/README.md) — AI 架构设计

---

> 📅 2026-06-28 · 咬文嚼字 · AI 新概念 · ⭐⭐⭐⭐（高频面试 + 实战必会）