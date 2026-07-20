<!--
module:
  parent: ai/agent-architecture/agent-execution-patterns
  slug: ai/agent-architecture/agent-execution-patterns/04-decision-tree
  type: topic
  category: 选型决策
  summary: 4 模式场景化决策树 + 反模式 + checklist
-->

# 选型决策树 · 4 模式场景化

> **一句话**：4 模式没有"最强"——只有「**场景 × 灵活性 × 成本**」3 维约束下的最优组合。给一张「5 分钟决策树」+「实施 checklist」。

← [返回: Agent 4 大模式](../README.md)

---

## 1. 5 分钟决策树

```text
Q1：任务流程是否明确？
├─ 完全明确（业务流） → DAG
└─ 部分明确 ↓

Q2：步骤数 ≤ 5？
├─ 是 + 路径未知   → ReAct
├─ 是 + 路径大致清楚 → 单 Agent + DAG
└─ 否（5+） ↓

Q3：步骤数 5-20？
├─ 是 + 强依赖（步骤间） → Plan-and-Execute
└─ 否（> 20） ↓

Q4：任务复杂需多角色协作？
├─ 是 → Multi-Agent
└─ 否 ↓

Q5：是否需要合规审计？
├─ 是 → DAG（强制）
└─ 否 ↓

Q6：是否需要灵活性 > 稳定性？
├─ 是 → ReAct（+ max_iterations）
└─ 否 → DAG（主流程）+ ReAct（兜底节点）
```

---

## 2. 场景化配置矩阵

| 场景 | 第一选择 | 第二选择 | 理由 |
|------|---------|---------|------|
| 客服对话 | ReAct + 温度=0 | Plan-and-Execute | 灵活但可控 |
| 代码助手 | DAG + Loop | Plan-and-Execute | 确定性流程 |
| 研究任务 | Plan-and-Execute | Multi-Agent | 多步强依赖 |
| 退款流程 | DAG | Plan-and-Execute | 业务流固定 |
| 数据分析 | DAG | Plan-and-Execute | 查询路径固定 |
| 创意写作 | ReAct + 温度=0.7 | Multi-Agent | 多探索 |
| 复杂业务流 | Plan-and-Execute + DAG | Multi-Agent | 规划 + 执行 |
| 高合规场景 | DAG（强制）| Plan-and-Execute | 可审计 |

---

## 3. 实施 Checklist

### 3.1 设计阶段

- [ ] **判断模式**：根据决策树选 1-2 个主模式
- [ ] **Plan 大小**：≤ 20 步（> 20 需分层）
- [ ] **失败策略**：Plan Repair / Adaptive / RePlan 三选一
- [ ] **Token 上限**：单次任务 ≤ 5 层路由（见 llm-production-thinking）
- [ ] **可观测性**：每步 Trace（关联 11.ai/03-engineering/llm-production-thinking）

### 3.2 工程阶段

- [ ] **重试机制**：max_iterations 上限
- [ ] **Context 管理**：Summary / Window（ReAct 必做）
- [ ] **温度控制**：执行型 0 / 探索型 0.7
- [ ] **Checkpoint**：每 3 步持久化
- [ ] **人工兜底**：连续失败 5 次触发人工

### 3.3 运维阶段

- [ ] **Trace 链路**：每步耗时 + token
- [ ] **黄金集回归**：每月 1 次
- [ ] **漂移检测**：Embedding / Prompt
- [ ] **告警**：P95 > 阈值 / 失败率 > 5%

---

## 4. 反模式速查（5 个最常见错）

| 反模式 | 场景 | 修复 |
|--------|------|------|
| **业务流用 ReAct** | 退款 / 订单 / 售后 | 改 DAG |
| **Plan 50 步** | 复杂任务一次规划 | 分层规划 |
| **Multi-Agent 简化任务** | "Agent 越多越强" | 单 Agent 先 |
| **默认 DAG** | 探索任务也用 DAG | 探索 ReAct |
| **只用一种模式** | 不组合 | DAG 主 + 副（ReAct/Plan Repair）|

---

## 5. 反向决策 · 5 个错误信号

| 错误信号 | 含义 |
|---------|------|
| ReAct 循环超过 30 次未收敛 | 任务不该用 ReAct |
| Plan Repair 频繁触发（> 5 次/任务） | 任务不适合 Plan-and-Execute |
| Multi-Agent 通信占 LLM 调用 > 50% | 任务不需 Multi-Agent |
| DAG 节点失败无恢复 | 错误处理缺失 |
| 模式混用导致调试困难 | 缺少 Trace 工具 |

---

## 6. 决策树精简版（一屏速查）

```text
┌──────────────────────────────────────────────┐
│  Step 1：业务流 vs 探索                      │
│    业务流 → DAG                              │
│    探索   → ReAct                            │
│                                              │
│  Step 2：步骤数                              │
│    ≤ 5    → 单 Agent / DAG                   │
│    5-20   → Plan-and-Execute                 │
│    > 20   → Multi-Agent / 分层 Plan          │
│                                              │
│  Step 3：合规与可审计                         │
│    高合规 → DAG 强制                         │
│                                              │
│  Step 4：实施 checklist（见 3.1-3.3）         │
└──────────────────────────────────────────────┘
```

---

## 7. 实操迁移路径

### 7.1 从 ReAct 迁移到 Plan-and-Execute

适用：ReAct 循环频繁 (≥ 10 次) + 任务相似

```text
Step 1: 收集最近 100 个 ReAct 路径
Step 2: 提取高频路径作为 Plan 模板
Step 3: 用 Planner 一次性生成 Plan
Step 4: 用 Executor 逐步执行
Step 5: 失败触发 Plan Repair
```

### 7.2 从 Plan-and-Execute 迁移到 DAG

适用：Plan 趋于稳定 + 失败率 < 1%

```text
Step 1: 收集最近 1000 个 Plan
Step 2: 提取公共 Plan 为 DAG 节点
Step 3: 用 LangGraph 实现
Step 4: 加 Error Handler 节点
Step 5: 保留 Plan Repair 节点（处理未知异常）
```

---

## 8. 一句话总结

> **4 模式选型不是"最强"——是"最契合"。5 分钟走完决策树 + 严格按 checklist 实施，比纠结技术先进性重要 10 倍。生产环境 80% 是 DAG + Plan-and-Execute + 局部 ReAct 兜底。**

---

← [返回: Agent 4 大模式](../README.md) · 上一章：[03-six-dimensions-comparison](03-six-dimensions-comparison.md) · 专题结束
