<!--
module:
  parent: ai/agent-architecture/agent-execution-patterns
  slug: ai/agent-architecture/agent-execution-patterns/02-plan-and-execute
  type: topic
  category: Plan-and-Execute 深度
  summary: Plan-and-Execute 深度剖析 —— 规划方法论 + RePlan / Adaptive / Plan-Repair 3 大重规划机制 + LangChain 实现 + 5 个反模式
-->

# Plan-and-Execute 深度剖析 · 先规划再执行

> **一句话**：Plan-and-Execute = "先用一个 LLM 规划任务，再逐步执行"——比 ReAct 多了**规划层**，支持 Plan Repair 修复失败，比 ReAct 更可控、更适合复杂多步任务。

← [返回: Agent 4 大模式](../README.md)

---

## 1. Plan-and-Execute 的本质

```
┌──────────────────────────────────────────────────────────┐
│ Stage 1：Planner（规划）                                  │
│   输入：用户问题                                          │
│   LLM 输出：Plan = [Step1, Step2, Step3, ...]            │
│   例：                                                     │
│   - Step 1: 查询订单 20260628                             │
│   - Step 2: 判断订单状态                                  │
│   - Step 3: 返回订单信息 / 触发退款                       │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ Stage 2：Executor（执行）                                 │
│   循环：                                                  │
│     - 取出当前 Step                                       │
│     - 调 Agent 执行 Step                                  │
│     - 收集执行结果                                        │
│     - 决定下一步（或触发 RePlan）                         │
└──────────────────────────────────────────────────────────┘
```

**核心思想**：**Plan 一次生成 + Execute 多次尝试 + Failure 重规划**

---

## 2. 4 大对比优势（vs ReAct）

| 维度 | ReAct | Plan-and-Execute |
|------|-------|------------------|
| **决策次数** | 每步都让 LLM 决策 | 一次性规划，逐步执行 |
| **Token 成本** | 高（每步 Thought）| 中（规划 1 次 + 执行 N 次）|
| **可预测性** | 差（路径随机）| 好（Plan 固定）|
| **可调试性** | 差（路径复杂）| 好（Plan 可视化）|
| **失败恢复** | 难（重新决策）| 易（RePlan / Repair）|

**反直觉**：Plan-and-Execute 在 **Token 成本** 上**不总优于** ReAct——如果规划错了，每次 RePlan 都耗 token。

---

## 3. 规划方法论（Plan 的 5 大要素）

```python
@dataclass
class PlanStep:
    step_id: int             # 1, 2, 3, ...
    description: str         # "查询订单 20260628"
    tool: str                # "get_order"
    inputs: dict             # {"order_id": "20260628"}
    dependencies: list       # [0, 1] = 依赖 Step 1 和 Step 2
    expected_output: str     # "订单状态字符串"
    status: str              # "pending" | "running" | "success" | "failed"
```

### 3.1 规划生成 5 要素

| 要素 | 说明 | 示例 |
|------|------|------|
| **任务分解** | 把大目标拆成子任务 | "退款" → [查询订单, 检查是否符合退款条件, 触发退款, 通知用户] |
| **依赖图** | 子任务的执行顺序 | Step 4 必须等 Step 2 完成 |
| **工具选择** | 每步用哪个工具 | Step 2 用 check_refund_eligibility |
| **预期输出** | 执行完成的样子 | Step 2 输出 refund_eligibility |
| **失败兜底** | 失败时怎么办 | Step 2 失败 → 重试 3 次 / 升级人工 |

### 3.2 规划 Prompt 模板

```
请将以下任务拆解为可执行步骤：

任务：{user_query}

输出 JSON 数组，每个元素包含：
- step: 步骤编号 (1, 2, 3...)
- description: 这一步做什么
- tool: 用哪个工具（必须从给定工具中选择）
- inputs: 工具参数（结构化）
- dependencies: 依赖哪些步骤

输出示例：
[
  {"step": 1, "description": "...", "tool": "...", "inputs": {...}, "dependencies": []},
  {"step": 2, "description": "...", "tool": "...", "inputs": {...}, "dependencies": [1]}
]

工具清单：
{tool_specs}
```

---

## 4. 3 大重规划机制（核心！）

### 4.1 RePlan（重新规划）

```
原始 Plan: [Step1, Step2, Step3, Step4]
执行到 Step3 失败
↓
丢弃剩余 Steps，从 Step3 重新规划新 Plan
↓
新 Plan: [Step1, Step2-new, Step3, Step4-new]
```

**优点**：彻底重规划
**缺点**：耗 token（重新规划）+ 丢失之前上下文

### 4.2 Adaptive Plan（自适应规划）

```
原始 Plan: [Step1, Step2, Step3, Step4]
Step3 失败
↓
改 Plan：跳过 Step3，加 Step3.5（人工兜底）
↓
新 Plan: [Step1, Step2, Step3.5, Step4]
```

**优点**：保留部分 Plan，不全推倒
**缺点**：可能陷入局部最优

### 4.3 Plan Repair（计划修复）—— 推荐

```
原始 Plan: [Step1, Step2, Step3, Step4]
Step3 失败（具体错误：参数 X 不存在）
↓
LLM Reasoning：识别错误根源，生成修复建议
↓
修复 Step3 inputs（添加默认值）
↓
Plan: [Step1, Step2, Step3-fixed, Step4]
```

**优点**：精确修复 + token 少
**缺点**：LLM 需理解错误根因

### 4.4 三机制对比

| 机制 | 适用 | Token 成本 |
|------|------|-----------|
| RePlan | 失败严重 / Plan 完全不可行 | 高（全重）|
| Adaptive | 失败中等 / 部分 Plan 可用 | 中 |
| Plan Repair | 失败轻 / 具体错误 | 低（精准） |

**实际工业实践**：失败次数 ≤ 2 用 Plan Repair；3-5 次升级到 Adaptive；> 5 次触发 RePlan + 人工兜底。

---

## 5. LangChain / LangGraph 实现

### 5.1 LangChain 基础实现

```python
from langchain.experimental.plan_and_execute import (
    PlanAndExecute, 
    load_agent_executor, 
    load_chat_planner
)
from langchain.llms import OpenAI

# Step 1: 创建 Planner
planner = load_chat_planner(llm)

# Step 2: 创建 Executor
executor = load_agent_executor(llm, tools, verbose=True)

# Step 3: 组合
agent = PlanAndExecute(planner=planner, executor=executor)

# Step 4: 运行
result = agent.run("帮用户退款订单 20260628")
```

### 5.2 LangGraph 实战（推荐）

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List

class PlanExecuteState(TypedDict):
    input: str
    plan: List[dict]
    past_steps: List[tuple]
    response: str

def execute_step(state: PlanExecuteState):
    plan = state["plan"]
    task = plan[0]  # 取出第一个 step
    # 执行 step
    result = agent_executor.invoke({"input": task["description"], **task["inputs"]})
    return {
        "past_steps": state["past_steps"] + [(task, result["output"])],
        "plan": plan[1:],  # 移除已执行 step
    }

def plan_step(state: PlanExecuteState):
    # 根据历史重新规划
    new_plan = planner.invoke({
        "input": state["input"],
        "past_steps": state["past_steps"],
    })
    return {"plan": new_plan}

def should_replan(state):
    if state["response"]:
        return END
    if len(state["plan"]) > 0:
        return "executor"  # 继续执行
    if max_iterations_reached(state):
        return END
    return "planner"  # 触发重规划

workflow = StateGraph(PlanExecuteState)
workflow.add_node("planner", plan_step)
workflow.add_node("executor", execute_step)
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "executor")
workflow.add_conditional_edges("executor", should_replan)
```

---

## 6. Plan-and-Execute 适用场景 vs 不适用场景

### 6.1 适用 ✅

| 场景 | 原因 |
|------|------|
| 复杂多步任务（5-20 步）| 一次性规划清晰 |
| 步骤间强依赖（A 依赖 B 结果）| Plan 显式声明 dependencies |
| 失败可恢复的任务 | Plan Repair 修复失败 |
| 业务流（部分可预测）| 规划兜底，RePlan 适配异常 |

### 6.2 不适用 ❌

| 场景 | 原因 | 推荐 |
|------|------|------|
| 步骤数 > 50 | Plan 太大，LLM 难以一次规划 | Multi-Agent |
| 路径完全未知 | 规划不出 | ReAct |
| 单步交互式 | 不需要规划 | 直接调工具 |
| 任务高度不确定 | RePlan 频繁，token 成本高 | ReAct |

---

## 7. Plan-and-Execute 优化方向

### 7.1 分层规划

```
Stage 1: Global Planner（粗粒度规划 5-10 高层步骤）
Stage 2: Sub-Planner（每个粗粒度步骤展开 3-5 细粒度步骤）
Stage 3: Executor（执行细粒度步骤）
```

**优点**：避免 50 步巨型 Plan，分层可控

### 7.2 Plan Checkpoint

```python
# 每 N 步做一次 checkpoint（持久化）
if (step_count + 1) % 3 == 0:
    save_checkpoint({
        "plan": state["plan"],
        "past_steps": state["past_steps"],
        "response": state["response"],
    })
```

### 7.3 Plan Caching

```python
# 相似任务复用 Plan
if query_similarity(new_query, past_query) > 0.9:
    return cached_plan(past_plan)
```

---

## 8. 反模式 · 5 个常见错

### ⚠️ 反模式 1：一次性规划 50 步

- 错：让 LLM 一次输出 50 步 Plan
- 对：分层规划 + 每个粗步骤展开 3-5 细步骤

### ⚠️ 反模式 2：失败不 RePlan

- 错：Step 失败后继续下一步（或放弃）
- 对：失败必须触发 RePlan / Repair / Adaptive

### ⚠️ 反模式 3：Plan Repair 不分析错误根因

- 错：失败就盲目重新规划
- 对：先推理错误根因，再决定 Repair / RePlan

### ⚠️ 反模式 4：规划用同一个 LLM

- 错：规划 + 执行都用 GPT-4
- 对：规划可用便宜模型（Qwen 32B），执行用 GPT-4

### ⚠️ 反模式 5：不持久化 Plan

- 错：失败重试从头开始
- 对：Checkpoint + Plan Caching

---

## 9. Plan-and-Execute vs ReAct 选型矩阵

| 任务特征 | ReAct | Plan-and-Execute |
|---------|-------|------------------|
| 步骤数 ≤ 5 + 路径未知 | ✅ | ⚠️ |
| 步骤数 5-20 + 路径大致清楚 | ⚠️ | ✅ |
| 步骤数 > 20 | ❌ | ⚠️（需分层）|
| 强依赖（步骤间） | ❌ | ✅ |
| 失败可恢复 | ⚠️ | ✅ |
| 完全探索 | ✅ | ❌ |

**实战模板**：**ReAct 探索 + Plan-and-Execute 兜底**（用 ReAct 跑前几步，发现路径后切换到 Plan-and-Execute）

---

## 10. 一句话总结

> **Plan-and-Execute = 一次性规划 + 逐步执行 + 失败 RePlan/Repair——比 ReAct 更可控，适合 5-20 步复杂任务。三大重规划机制（RePlan / Adaptive / Plan Repair）从粗到细，工业级方案是 Plan Repair + 分层规划。**

---

← [返回: Agent 4 大模式](../README.md) · 上一章：[01-react-deep-dive](01-react-deep-dive.md) · 下一章：[03-six-dimensions-comparison](03-six-dimensions-comparison.md)
