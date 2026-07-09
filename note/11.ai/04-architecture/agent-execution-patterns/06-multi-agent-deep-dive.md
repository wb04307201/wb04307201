<!--
module:
  parent: ai/agent-architecture/agent-execution-patterns
  slug: ai/agent-architecture/agent-execution-patterns/06-multi-agent
  type: topic
  category: Multi-Agent 深度
  summary: Multi-Agent 深度剖析 —— 通信协议 + 协调者模式 + CrewAI/AutoGen 实现 + 循环调用防护 + 5 个反模式
-->

# Multi-Agent 深度剖析 · 多智能体协作

> **一句话**：Multi-Agent = 多个 Agent 各司其职、互相通信——理论上最强大，但**通信开销 + 调试复杂度 + Token 消耗**让 80% 的场景不如单 Agent。

← [返回: Agent 4 大模式](../README.md)

---

## 1. Multi-Agent 的本质

```
┌──────────────────────────────────────────────────────────┐
│ Multi-Agent = 多个 Agent + 通信协议 + 协调机制             │
│                                                          │
│  [研究员 Agent] ←→ [协调者] ←→ [编码 Agent]               │
│                       ↕                                   │
│                  [测试 Agent]                             │
│                                                          │
│  每个 Agent：独立的 LLM + 工具 + 记忆                      │
│  通信协议：消息传递 / 共享状态 / 黑板模式                   │
│  协调机制：轮流发言 / 投票 / 协调者调度                     │
└──────────────────────────────────────────────────────────┘
```

**核心特征**：
- **专业化**：每个 Agent 擅长一个领域（研究/编码/测试）
- **并行性**：多个 Agent 可以同时工作
- **通信成本**：Agent 之间传递消息需要额外 Token

---

## 2. 3 种通信模式

### 2.1 点对点（Peer-to-Peer）

```text
Agent A → Agent B（直接发消息）
Agent B → Agent C
Agent C → Agent A

优点：灵活
缺点：N 个 Agent → N² 条通信链路 → Token 爆炸
```

### 2.2 协调者（Orchestrator / Supervisor）

```text
[协调者 Agent]
  ├─ 分配任务 → [研究员 Agent]
  ├─ 分配任务 → [编码 Agent]
  ├─ 汇总结果 → [测试 Agent]
  └─ 最终输出

优点：通信链路 O(N)，可控
缺点：协调者是单点 + 瓶颈
```

### 2.3 黑板模式（Blackboard / Shared State）

```text
[共享状态空间]
  Agent A 写入 → 所有 Agent 可读
  Agent B 写入 → 所有 Agent 可读

优点：解耦，Agent 不直接通信
缺点：状态一致性难保证
```

**生产推荐**：**协调者模式**（最可控，通信成本最低）。

---

## 3. 协调者的 3 种调度策略

| 策略 | 原理 | 适用 |
|------|------|------|
| **顺序调度** | Agent A 完成 → Agent B → Agent C | 流水线任务 |
| **并行调度** | Agent A/B/C 同时执行 → 汇总 | 独立子任务 |
| **动态调度** | 协调者根据中间结果决定下一步调谁 | 复杂任务 |

```text
动态调度示例：
  协调者："用户要一个电商网站"
    → 先调 [研究员]：调研竞品
    → 根据调研结果，调 [架构师]：设计方案
    → 根据方案，调 [编码 Agent]：实现
    → 如果测试失败，再调 [编码 Agent]：修复
```

---

## 4. 循环调用防护

Multi-Agent 最大的风险：**A 调 B → B 调 A → 无限循环**。

### 4 种防护机制

| 机制 | 实现 | 说明 |
|------|------|------|
| **max_turns** | 限制总对话轮数（如 10 轮） | 最常用，兜底机制 |
| **max_depth** | 限制调用深度（如 3 层） | 防止嵌套调用 |
| **协调者裁决** | 协调者判断"够了"→ 终止 | 智能终止 |
| **Token 预算** | 总 Token 超过阈值 → 强制终止 | 成本控制 |

```text
防护示例：
  max_turns = 10
  max_depth = 3
  token_budget = 50,000

  第 1 轮：协调者 → 研究员（depth=1）
  第 2 轮：研究员 → 协调者（depth=1）
  第 3 轮：协调者 → 编码（depth=2）
  第 4 轮：编码 → 协调者（depth=2）
  ...
  第 10 轮：达到 max_turns → 强制终止，输出当前最佳结果
```

---

## 5. 典型实现框架

| 框架 | 特点 | 适用 |
|------|------|------|
| **CrewAI** | 角色化 Agent + 任务分配 + 协作流程 | 快速原型 |
| **AutoGen**（微软） | 对话式 Multi-Agent + 代码执行 | 研究 + 编码协作 |
| **MetaGPT** | SOP 驱动 + 角色分工 | 软件开发模拟 |
| **ChatDev** | 虚拟软件公司（CEO/CTO/程序员/测试） | 端到端开发 |
| **LangGraph** | 通用图框架，可实现 Multi-Agent | 自定义流程 |

### CrewAI 示例

```python
from crewai import Agent, Task, Crew

# 定义 Agent（角色化）
researcher = Agent(
    role="技术研究员",
    goal="调研给定技术的优缺点和最佳实践",
    backstory="你是一位资深技术研究员，擅长对比分析",
    tools=[search_tool, web_scraper]
)

coder = Agent(
    role="高级开发者",
    goal="根据研究结果编写高质量代码",
    backstory="你是一位全栈工程师，注重代码质量",
    tools=[code_executor, file_writer]
)

reviewer = Agent(
    role="代码审查员",
    goal="审查代码质量，发现问题并给出修改建议",
    backstory="你是一位严格的 code reviewer"
)

# 定义任务
research_task = Task(
    description="调研 React vs Vue 在大型项目中的表现",
    agent=researcher,
    expected_output="一份包含对比表格的研究报告"
)

code_task = Task(
    description="根据研究结论，用推荐的框架搭建项目骨架",
    agent=coder,
    expected_output="可运行的项目代码"
)

review_task = Task(
    description="审查代码，检查是否符合最佳实践",
    agent=reviewer,
    expected_output="审查报告 + 修改建议"
)

# 组建团队
crew = Crew(
    agents=[researcher, coder, reviewer],
    tasks=[research_task, code_task, review_task],
    process="sequential"  # 顺序执行
)

result = crew.kickoff()
```

---

## 6. Multi-Agent vs 单 Agent

| 维度 | Multi-Agent | 单 Agent |
|------|------------|---------|
| **能力上限** | 更高（专业化分工） | 受限于单个 LLM |
| **Token 成本** | 3-10x（通信开销） | 1x |
| **调试难度** | 极高（多 Agent 状态追踪） | 中等 |
| **延迟** | 高（串行通信 + 多次 LLM 调用） | 中 |
| **可控性** | 低（Agent 间交互不可预测） | 高 |
| **适用比例** | ~20% 场景 | ~80% 场景 |

**关键判断**：

| 信号 | 选择 |
|------|------|
| 单 Agent 无法完成（如需要同时搜索 + 编码 + 测试） | Multi-Agent |
| 任务可以分解为独立子任务 | Multi-Agent（并行） |
| 需要不同"专家视角"（如开发 + 安全审计） | Multi-Agent |
| 其他所有情况 | 单 Agent |

---

## 7. 5 个反模式

### ⚠️ 反模式 1：Agent 越多越好

- 错："5 个 Agent 一定比 1 个强"
- 对：80% 场景单 Agent 足够。Multi-Agent 的通信成本 + 调试难度往往得不偿失

### ⚠️ 反模式 2：没有协调者

- 错：让 Agent 之间自由对话（Peer-to-Peer）
- 对：必须有协调者控制对话方向和终止条件

### ⚠️ 反模式 3：Agent 之间传递完整上下文

- 错：每个 Agent 把完整对话历史传给下一个
- 对：传递摘要 + 关键信息（减少 Token 消耗）

### ⚠️ 反模式 4：用 Multi-Agent 做简单任务

- 错：让"研究员 + 编码 + 测试"3 个 Agent 去改一个按钮颜色
- 对：简单任务用单 Agent 或直接手写

### ⚠️ 反模式 5：忽略 Agent 身份混乱

- 错：Agent A 开始扮演 Agent B 的角色（LLM 的角色扮演倾向）
- 对：严格的 system prompt + 工具隔离 + 协调者监控

---

## 8. 一句话总结

> **Multi-Agent 是"最后的手段"**：只有当单 Agent 确实无法胜任时才使用。生产环境中，优先用 DAG 编排单 Agent，而不是 Multi-Agent 协作。如果必须用 Multi-Agent，选协调者模式 + max_turns 兜底。

---

## 系列导航

| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [ReAct 深度](01-react-deep-dive.md) | Thought/Action/Observation 循环 + Token 失控 |
| 02 | [Plan-and-Execute 深度](02-plan-and-execute-deep-dive.md) | 规划 + RePlan + Plan Repair |
| 03 | [6 维对比](03-six-dimensions-comparison.md) | 4 模式完整打分 |
| 04 | [选型决策树](04-selection-decision-tree.md) | 场景化选型 + checklist |
| 05 | [DAG 深度](05-dag-deep-dive.md) | 节点设计 + 错误恢复 + Loop 节点 |
| **06** | **Multi-Agent 深度（本文）** | 通信协议 + 协调者 + 循环防护 |

---

← [返回: Agent 4 大模式](../README.md) · 上一章：[05-dag](05-dag-deep-dive.md)
