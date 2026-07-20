<!--
module:
  parent: ai/agent-architecture/agent-context
  slug: ai/agent-architecture/agent-context/05-sub-agents-decomposition
  type: topic
  category: 子 Agent 拆分
  summary: Sub-Agents / Multi-Agent / Task Decomposition —— 用任务拆分降低单 Agent 上下文压力，AutoGen/LangGraph 实战
-->

# Sub-Agents 任务拆分 · Multi-Agent 架构降低单 Agent 上下文

> **一句话**：当单 Agent 上下文撑不住时，**拆任务给子 Agent**——主 Agent 看"摘要 + 子任务列表"，每个子 Agent 各自看自己的上下文，最后主 Agent 汇总。

← [返回: Agent 长上下文架构](../README.md)

---

## 1. 为什么需要 Sub-Agents？

```text
单 Agent 问题（复杂任务）：
- 任务有 5 个子任务（搜索 / 计算 / 写作 / 验证 / 格式化）
- 每个子任务产生 10k token 中间结果
- 总 prompt = 50k+ token（成本高、注意力衰减）

Sub-Agent 架构：
- 主 Agent：看"任务列表 + 状态"（2k token）
- 子 Agent 1：只看自己的 10k context
- ...
- 主 Agent：只看结果摘要
→ 总 context 降低 50%+
```

---

## 2. 4 种 Sub-Agent 模式

### 2.1 Hierarchical（层级）

```text
主 Agent（Orchestrator）
    ├── 子 Agent 1（搜索）
    ├── 子 Agent 2（计算）
    └── 子 Agent 3（写作）
```

**特点**：主 Agent 控制流程，子 Agent 独立工作
**适用**：业务流程清晰、任务可分解
**代表**：LangGraph、AutoGen

### 2.2 Collaborative（协作）

```text
多个 Agent 同级，互相 message
Agent A ↔ Agent B ↔ Agent C
```

**特点**：所有 Agent 平等，通过消息达成共识
**适用**：需要多视角讨论（如辩论 / 评审）
**代表**：CrewAI、ChatDev

### 2.3 Sequential（顺序）

```text
Agent 1 → Agent 2 → Agent 3 → ...
（前一步输出作为后一步输入）
```

**特点**：流水线，单向
**适用**：ETL / 数据处理类任务
**代表**：DSPy、LlamaIndex

### 2.4 Mesh（网状）

```text
Agent A ↔ B
Agent A ↔ C
Agent B ↔ C
Agent B ↔ D
```

**特点**：最灵活但最复杂
**适用**：复杂决策（如股市分析）
**代表**：AutoGen 高级用法、MetaGPT

---

## 3. 主流框架对比

| 框架 | 模式 | 特点 | 适用 |
|------|------|------|------|
| **LangGraph** | Hierarchical | StateGraph 显式状态 | 生产级最稳定 |
| **AutoGen** | Mesh | 多 Agent 对话 | 微软 / 研究 |
| **CrewAI** | Collaborative | 角色分工 | 业务流程 |
| **DSPy** | Sequential | 编程式 pipeline | 数据处理 |
| **ChatDev** | Collaborative | 软件开发团队 | 高度专业化 |
| **MetaGPT** | Mesh | SOP 标准化 | 复杂软件项目 |

---

## 4. 任务拆分策略

### 4.1 按"步骤"拆（最常用）

```text
任务：写一篇技术博客
  - 子任务 1：研究主题（搜索资料）
  - 子任务 2：列大纲（生成结构）
  - 子任务 3：写首稿（生成内容）
  - 子任务 4：审稿（质量检查）
  - 子任务 5：润色（生成最终）
```

### 4.2 按"角色"拆

```text
任务：完成产品设计
  - PM Agent：用户需求 / PRD
  - Designer Agent：UX / 视觉
  - Engineer Agent：技术方案
  - Reviewer Agent：综合评审
```

### 4.3 按"数据源"拆

```text
任务：跨库分析用户行为
  - Sub-Agent 1：读 MySQL
  - Sub-Agent 2：读 ClickHouse
  - Sub-Agent 3：读 S3 logs
  - 主 Agent：汇总分析
```

---

## 5. 通信协议（关键难点）

### 5.1 主-子通信

```python
# 主 Agent 调用子 Agent
response = subagent.invoke(
    task="搜索 X 产品的 2024 销量",
    context_limit=10_000
)

# 子 Agent 返回结构化结果
{
    "status": "success",
    "data": {"year": 2024, "sales": 12345},
    "summary": "X 产品 2024 销量为 12,345 件",
    "raw_tokens_used": 8500  # 子 Agent 内部用 token
}
```

### 5.2 中间结果管理

**反模式**：把所有子结果塞回主 Agent（上下文爆炸）

**最佳实践**：
- 子 Agent 返回**摘要**而非原始数据
- 主 Agent 只看摘要 + 状态
- 完整数据存外部（数据库 / 向量库）

---

## 6. 实战：LangGraph Hierarchical

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    query: str
    subtasks: list
    results: list
    final_answer: str

def planner(state):
    return {"subtasks": ["search", "compute", "summarize"]}

def search_agent(state):
    # 调用 search 子 Agent
    result = search.invoke(state["query"])
    return {"results": [result]}

def compute_agent(state):
    result = compute.invoke(...)
    return {"results": state["results"] + [result]}

def summarizer(state):
    summary = llm.invoke(f"汇总：{state['results']}")
    return {"final_answer": summary}

# 构建图
workflow = StateGraph(State)
workflow.add_node("planner", planner)
workflow.add_node("search", search_agent)
workflow.add_node("compute", compute_agent)
workflow.add_node("summarizer", summarizer)
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "search")
workflow.add_edge("search", "compute")
workflow.add_edge("compute", "summarizer")
workflow.add_edge("summarizer", END)
```

---

## 7. 反模式 · Multi-Agent 的 5 个错

### ⚠️ 反模式 1：拆太细

- 错：拆 20 个子 Agent，每个只做 1 步
- 对：拆 3-5 个，每个职责清晰

### ⚠️ 反模式 2：忽略通信成本

- 错：每个子 Agent 返回 10k token → 主 Agent 看 30k
- 对：子 Agent 返回结构化摘要（< 500 token）

### ⚠️ 反模式 3：循环调用无终止

- 错：Agent A ↔ Agent B 一直互答
- 对：加 max_turns + 终止条件

### ⚠️ 反模式 4：不区分 Hierarchical 和 Collaborative

- 错：业务流用 Collaborative（角色混乱）
- 对：业务流用 Hierarchical（流程清晰）

### ⚠️ 反模式 5：Sub-Agents 替代 RAG

- 错："我有 Multi-Agent 了，不用 RAG"
- 对：Multi-Agent 处理任务分工，知识检索仍用 RAG

---

## 8. 一句话总结

> **Sub-Agents = 把"上下文压力"切给子 Agent——主 Agent 只看摘要 + 状态。Hierarchical 模式 80% 场景够用，3-5 个子 Agent 是 sweet spot。**

---

← [返回: Agent 长上下文架构](../README.md) · 上一章：[04-sliding-window-attention](04-sliding-window-attention.md) · 下一章：[06-long-context-models](06-long-context-models.md)
