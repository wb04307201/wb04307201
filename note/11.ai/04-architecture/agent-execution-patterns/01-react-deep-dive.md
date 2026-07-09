<!--
module:
  parent: ai/agent-architecture/agent-execution-patterns
  slug: ai/agent-architecture/agent-execution-patterns/01-react-deep-dive
  type: topic
  category: ReAct 深度
  summary: ReAct（Reasoning + Acting）深度剖析 —— Thought/Action/Observation 三元组 + LangChain 实现 + Token 失控模式 + 5 个反模式
-->

# ReAct 深度剖析 · 思考 → 行动 → 观察 → 循环

> **一句话**：ReAct = 让 LLM 思考"下一步该做什么"，执行后看结果再决定——是**最经典的 Agent 循环模式**，但 Token 消耗不可控 + 路径不可复现是 2 大硬伤。

← [返回: Agent 4 大模式](../README.md)

---

## 1. ReAct 的本质（Thought + Action + Observation 三元组）

```
┌─────────────────────────────────────────────────────────────┐
│  Thought: 我需要先查询订单                                   │
│  Action:  getOrder(order_id="20260628")                    │
│  Observation: 订单状态：已支付                               │
│                                                              │
│  Thought: 订单已支付，我应该给用户返回结果                   │
│  Action:  ReturnMessage("订单 XXX 已支付，金额 XXX 元")    │
│  Observation: 完成                                           │
└─────────────────────────────────────────────────────────────┘
                       ↓
                  循环直到任务完成
```

**核心三要素**：
- **Thought（思考）**：模型推理"我下一步要做什么"
- **Action（行动）**：调用工具 / API / 计算
- **Observation（观察）**：工具执行结果反馈

每次循环 = **1 次 LLM 调用** + **1 次工具执行** + **1 步状态更新**。

---

## 2. LangChain ReAct 实现

### 2.1 基础代码

```python
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.tools import tool

@tool
def get_order(order_id: str) -> str:
    """查询订单状态"""
    return f"订单 {order_id} 已支付"

@tool
def request_refund(order_id: str) -> str:
    """申请退款"""
    return f"退款 {order_id} 已处理"

tools = [get_order, request_refund]
agent = initialize_agent(
    tools, llm, agent=AgentType.REACT_DOCSTORE, verbose=True
)

agent.run("帮用户查询订单 20260628 并判断是否已支付")
```

### 2.2 ReAct Prompt 模板（LangChain 内置）

```
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:
```

### 2.3 输出解析

LangChain 用正则解析：

```python
import re

action_match = re.match(
    r"Action: (.*?)\nAction Input: (.*)",
    text,
    re.DOTALL
)
```

---

## 3. ReAct 的 4 大优势

| 优势 | 说明 |
|------|------|
| **灵活** | LLM 自己决定下一步，应对未知场景 |
| **直观** | Thought-Action-Observation 三元组符合人类推理 |
| **可解释** | 每次 Thought 都是自然语言，可审计 |
| **实现简单** | LangChain / AutoGPT 框架开箱即用 |

---

## 4. ReAct 的 5 大硬伤

### 4.1 硬伤 1：Token 消耗不可控

```
单次循环：
  Thought: 200 tokens
  Action: 20 tokens
  Observation: 100 tokens

循环 10 次 = 3200 tokens（仅输入）
循环 50 次 = 16,000 tokens

vs DAG 同等任务 = 2000 tokens（每个节点 200 tokens × 10）
```

**反直觉**：ReAct 单次循环成本可控，但任务越复杂，循环次数指数级增长。

### 4.2 硬伤 2：执行路径不可复现

```
同一问题：
  "帮用户退款"
   - ReAct 第 1 次：Thought1 → Action1 → Observation1 → Thought2 → Action2
   - ReAct 第 2 次：Thought1 → Action2 → Observation2 → Thought3 → Action1

两次路径不同，调试困难。
```

**根因**：temperature > 0 + 概率性决策 = 不可复现。

### 4.3 硬伤 3：Context 越长越混乱

```
循环 30 次：
  Thought×30 + Action×30 + Observation×30
  = 60-90 段历史消息
  = 8000-15000 tokens context
  = 模型开始"忘掉早期信息"
  = 容易做出错误决策
```

### 4.4 硬伤 4："迷路"问题

经典失败模式：
```
Thought: 我应该先查询订单
Action: getOrder(order_id="ABC")
Observation: 找不到订单 ABC
Thought: 嗯，那我再试试另一个 ID
Action: getOrder(order_id="XYZ")
Observation: 还是找不到
Thought: 那我应该用 search_order 先搜索
Action: searchOrder("ABC")
...
无限循环直到 max_iterations 触发
```

### 4.5 硬伤 5：合规审计困难

金融 / 医疗 / 法律场景要求 Agent 行为可审计：

```
ReAct 路径："随便走"
DAG 路径："固定节点 + 边，可完整审计"
```

---

## 5. ReAct 适用场景 vs 不适用场景

### 5.1 适用 ✅

| 场景 | 原因 |
|------|------|
| 探索 / 研究类任务 | 路径未知 |
| 创意 / 写作类 | 多尝试找最佳 |
| 客服对话（开放问答）| 每个用户问题不同 |
| 数据分析（adhoc query）| 查询路径不固定 |
| 简单工具组合（≤ 5 个）| 单层循环可处理 |

### 5.2 不适用 ❌

| 场景 | 原因 | 推荐 |
|------|------|------|
| 业务流程（步骤固定）| ReAct 路径不稳定 | DAG |
| 多步强依赖任务 | 需先规划 | Plan-and-Execute |
| 高合规场景 | 不可审计 | DAG |
| 超过 50 个工具 | 决策困难 | DAG 或 Multi-Agent |
| Token 成本敏感 | 消耗不可控 | DAG |

---

## 6. ReAct 优化方向（5 个实战技巧）

### 6.1 设置 max_iterations

```python
agent = initialize_agent(
    tools, llm, 
    agent=AgentType.REACT_DOCSTORE,
    max_iterations=10,  # 强制上限
    early_stopping_method="force"  # 达到 max 返回当前最佳
)
```

### 6.2 阶段性 Summary

```python
# 每 5 轮压缩一次历史
if iter % 5 == 0:
    summary = llm.invoke(f"压缩最近 5 轮：{history[-10:]}")
    history = [summary] + history[-2:]  # 保留最新 2 轮
```

### 6.3 工具约束

```python
# 减少工具到 ≤ 10 个
filtered_tools = filter_relevant_tools(query_embedding, tools, top_k=10)
```

### 6.4 设置 temperature = 0（确定性）

```python
llm = OpenAI(temperature=0)  # 避免随机性
```

### 6.5 用 Plan-and-Execute 兜底

```python
# 当 ReAct 不适用时自动切换
if task_complexity > threshold:
    return plan_and_execute_agent(prompt)
else:
    return react_agent(prompt)
```

---

## 7. 反模式 · 5 个常见错

### ⚠️ 反模式 1：业务流强用 ReAct

- 错：退款流程用 ReAct 循环
- 对：退款流程是步骤固定的，用 DAG

### ⚠️ 反模式 2：max_iterations = 0 或不设

- 错：让 Agent 无限循环
- 对：必须 max_iterations 上限（10-30）

### ⚠️ 反模式 3：不做 Summary

- 错：context 无限增长直到 OOM
- 对：阶段性 summary + window

### ⚠️ 反模式 4：忽略温度

- 错：默认 temperature=0.7（生产）
- 对：ReAct 应 temperature=0（可预测）

### ⚠️ 反模式 5：盲目用 temperature=0

- 错：所有 ReAct 都 temperature=0
- 对：探索任务 temperature=0.7 + 投票；执行任务 temperature=0

---

## 8. 一句话总结

> **ReAct 是最经典的 Agent 循环模式——Thought/Action/Observation 三元组 + LLM 自己决策 = 灵活但 Token 不可控。生产场景需配合 max_iterations + Summary + 兜底模式（Plan-and-Execute 或 DAG）。**

---

## 系列导航

| # | 章节 | 核心问题 |
|---|------|---------|
| **01** | **ReAct 深度（本文）** | Thought/Action/Observation 循环 + Token 失控 |
| 02 | [Plan-and-Execute 深度](02-plan-and-execute-deep-dive.md) | 规划 + RePlan + Plan Repair |
| 03 | [6 维对比](03-six-dimensions-comparison.md) | 4 模式完整打分 |
| 04 | [选型决策树](04-selection-decision-tree.md) | 场景化选型 + checklist |
| 05 | [DAG 深度](05-dag-deep-dive.md) | 节点设计 + 错误恢复 + Loop 节点 |
| 06 | [Multi-Agent 深度](06-multi-agent-deep-dive.md) | 通信协议 + 协调者 + 循环防护 |

---

← [返回: Agent 4 大模式](../README.md) · 下一章：[02-plan-and-execute](02-plan-and-execute-deep-dive.md)
