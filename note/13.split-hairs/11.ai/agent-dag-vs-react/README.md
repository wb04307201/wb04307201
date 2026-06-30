<!--
question:
  id: 11.ai-agent-dag-vs-react
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 架构困境
  tags: [11.ai, Agent, agent]
-->

# Agent 架构选型 — DAG vs ReAct 面试深挖

> 一句话定位：复杂 Agent 为什么越来越多采用 DAG？核心是生产环境的稳定性、成本、可观测性、合规需求。完整概念见 [主模块 Agent 架构](../../../11.ai/04-architecture/agent-architecture/README.md)。

---

## 引子：让 AI 自己跑业务，3 个订单后开始"迷路了"

```text
你的 AI 客服 Agent：

用户 1："退款？"
Agent（ReAct 模式）：思考 → 调 refund API → 完成
用户 2："查订单？"
Agent：思考 → 调 query API → 完成
用户 3："把这三个订单合并发到一个地址？"
Agent：思考 → 调 query 1 → 调 query 2 → 调 query 3 → ... 想怎么合并 → ...
失败：context 太长忘了前面的结果
```

**真相**：复杂业务流程（多步骤、强依赖）让 Agent **自己规划**会崩。

两种范式对比：

- **DAG（静态流程图）**：人画好流程，Agent 按图跑。**确定性高、可调试**
- **ReAct（边想边做）**：Agent 自己决定下一步。**灵活但不可控**

实战：**复杂业务用 DAG + ReAct 混合**——固定分支用 DAG，模糊决策用 ReAct。

## 一、4 大架构速记

| 架构 | 模式 | 适用 |
|------|------|------|
| **ReAct** | 思考 → 行动 → 观察 → 循环 | 探索性任务 |
| **DAG** | 有向无环图，节点 + 边 | 确定性流程 |
| **Plan-and-Execute** | 先规划再执行 | 复杂任务 |
| **Multi-Agent** | 多 Agent 协作 | 复杂业务 |

> 一句话：**ReAct 用于"探索"，DAG 用于"执行"；生产环境 DAG + Loop 混合**。

---

## 二、面试陷阱

### 陷阱 1：以为 ReAct 是"过时"架构
- **真相**：ReAct 仍是**探索性任务**首选（开放式问题、不确定路径），生产环境 ReAct + Harness 也常见。

### 陷阱 2：以为 DAG 完全取代 ReAct
- **真相**：DAG 用于"确定性流程"，ReAct 用于"探索性任务"，**二者是互补**，不是替代。

### 陷阱 3：以为 Multi-Agent 比 DAG 更先进
- **真相**：Multi-Agent **通信开销大**，多数场景 DAG + Loop 已足够；Multi-Agent 只在"职责明确分工"时才有优势。

### 陷阱 4：以为所有 Agent 节点都需要"思考"
- **真相**：DAG 中很多节点是**纯函数调用**（参数提取、格式转换、DB 查询），根本不需要 LLM 思考，可显著降低成本。

### 陷阱 5：忽视 DAG 的"灵活性不足"
- **真相**：未定义流程用 DAG 会很僵硬；需配合 **Context Engineering + Harness Engineering** 提供动态决策能力。

---

## 三、为何复杂 Agent 选 DAG？

1. **稳定性**：生产 99.9% 可用，DAG 行为可预测
2. **成本控制**：DAG 每节点调一次 LLM，ReAct 每次循环都调
3. **调试可观测**：DAG 路径可 Trace，ReAct 路径难复现
4. **合规**：金融/医疗要求可审计，DAG 满足
5. **LLM 能力提升**：2026 LLM 足够强，DAG 灵活性不足被 Context/Harness 弥补

---

## 四、真实案例速记

| 产品 | 架构 | 理由 |
|------|------|------|
| **Cursor** | DAG（Composer） | 代码生成是确定性流程 |
| **Claude Code** | DAG + Loop | 主流程 DAG + 错误重试 Loop |
| **Devin** | Plan-and-Execute + DAG | 先规划再执行 |
| **AutoGPT** | ReAct | 探索性研究 |

---

## 五、选型决策树

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

**推荐**：生产环境用 **DAG + Loop 混合**（确定性节点用 DAG，探索性节点用 Loop）。

---

## 六、反直觉点

- **ReAct 循环不是越深越好**：循环 3-5 轮未完成就要触发 Harness 兜底，否则 Token 爆炸。
- **DAG 不是"硬编码"**：现代 DAG 框架（LangGraph）支持**条件分支、动态子图**，灵活性比传统工作流强。

---

## 七、30 秒面试话术

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

## 八、深度阅读

- 主模块：[Agent 架构](../../../11.ai/04-architecture/agent-architecture/README.md)
- 关联：[Function Calling](../function-calling/README.md) — Agent 的"手"
- 关联：[Loop Engineering](../loop-engineering/README.md) — DAG 的兜底机制
- 关联：[Harness Engineering](../harness-engineering/README.md) — DAG 是 Harness 的强约束

---

> 📅 2026-06-30 · 咬文嚼字 · 高频面试 + 实战必会 · ⭐⭐⭐⭐⭐