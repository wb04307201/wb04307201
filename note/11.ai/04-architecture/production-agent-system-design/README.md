<!--
module:
  parent: ai
  slug: ai/production-agent-system-design
  type: article
  category: 主模块子文章
  summary: 生产级 Agent 系统端到端搭建指南 —— 8 步流水线串联 8 大组件
-->

# 生产级 Agent 系统端到端搭建指南

← 返回 [架构设计](../README.md)

> 一句话定位：**把 8 大组件串成 Step 1→8 流水线** —— 从需求分析到生产监控，每步都有对应组件文章深读。本文不新增知识，只做**编排 + 互链 + checklist**。

## 反向链

- [agent-architecture](../agent-architecture/README.md)
- [harness-engineering](../../03-engineering/harness-engineering/README.md)

← [返回: L4 架构设计](../README.md)

---

## 为什么需要端到端指南

现有 8 篇组件文章各自独立：

| # | 组件 | 文章 | 解决什么 |
|---|------|------|---------|
| 1 | 架构选型 | [agent-architecture](../agent-architecture/README.md) | DAG vs ReAct vs Plan-Execute |
| 2 | Harness 约束 | [harness-engineering](../../03-engineering/harness-engineering/README.md) | Prompt/工具/输出约束 |
| 3 | Loop 兜底 | [loop-engineering](../../03-engineering/loop-engineering/README.md) | 循环调用 + Verifier |
| 4 | 可靠性 | [agent-reliability](../../03-engineering/agent-reliability/README.md) | 4 层防线防跑偏 |
| 5 | Memory | [agent-memory](../agent-memory/README.md) | 短期/长期/工作记忆 |
| 6 | 评测 | [agent-evaluation](../../08-llmops/agent-evaluation/README.md) | 6 维评测体系 |
| 7 | 监控 | [production-stability](../../08-llmops/production-stability/README.md) | 4 维监控 + Trace |
| 8 | 执行模式 | [agent-execution-patterns](../agent-execution-patterns/README.md) | 4 模式 6 维对比 |

**问题**：知道每个组件 ≠ 知道怎么串起来。本文给**8 步流水线** + **每步 checklist**。

---

## 8 步流水线（端到端）

```text
Step 1: 需求分析 → Step 2: 架构选型 → Step 3: Harness 设计
   ↓
Step 4: Loop + Verifier → Step 5: 可靠性防线 → Step 6: Memory 设计
   ↓
Step 7: 评测体系 → Step 8: 监控上线
```

### Step 1: 需求分析（30 分钟）

**输入**：业务需求文档
**输出**：Agent 能力边界 + 约束清单

**Checklist**：
- [ ] 任务类型：探索性（ReAct） vs 确定性（DAG）？
- [ ] 合规要求：是否需要审计轨迹？
- [ ] 成本预算：单次任务 Token 上限？
- [ ] 失败容忍度：允许重试几次？

**深读**：[agent-architecture §七 何时选 DAG vs ReAct](../agent-architecture/README.md#七何时选-dag-vs-react)

---

### Step 2: 架构选型（1 小时）

**输入**：Step 1 需求清单
**输出**：架构决策（DAG / ReAct / Plan-Execute / Multi-Agent）

**决策树**：

```text
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

**深读**：[agent-execution-patterns §四 6 维完整打分](../agent-execution-patterns/README.md)

---

### Step 3: Harness 设计（2 小时）

**输入**：Step 2 架构决策
**输出**：系统 Prompt + 工具描述 + 输出格式约束

**4 大 Harness 类型**：

| 类型 | 作用 | 示例 |
|------|------|------|
| Prompt 约束 | 任务边界 + 禁止动作 | "只写 Java 代码，不修改数据库" |
| 工具约束 | 何时用 / 何时不用 | "search 返回空时停止，不要换词重试" |
| 输出约束 | 格式 + Schema | "必须返回 JSON，包含 code + explanation" |
| 流程约束 | 节点顺序 + 分支条件 | "intent_classify → query_order → format_response" |

**深读**：[harness-engineering §三 4 大 Harness 类型](../../03-engineering/harness-engineering/README.md)

---

### Step 4: Loop + Verifier 设计（1 小时）

**输入**：Step 3 Harness 设计
**输出**：循环调用逻辑 + Verifier 检查点

**3 大核心组件**：

| 组件 | 作用 | 示例 |
|------|------|------|
| 任务定义 | 清晰 + 可验证 | "实现 LRU Cache，get/put O(1)" |
| Verifier | 每步检查 | 语法检查 + 语义检查 + 业务规则 |
| 反馈机制 | 失败 → 重试 | "测试失败，错误信息：..." |

**Verifier 类型**：
- 语法检查：代码编译 / JSON 解析
- 语义检查：逻辑一致性 / 业务规则
- 空结果检测：搜索返回空 → 换策略

**深读**：[loop-engineering §三 3 大核心组件](../../03-engineering/loop-engineering/README.md)

---

### Step 5: 可靠性防线（1 小时）

**输入**：Step 4 Loop 设计
**输出**：4 层防线配置

**4 层防线**：

| 层 | 防线 | 配置 |
|----|------|------|
| L1 | Prompt 约束 | 任务边界 + 禁止动作 |
| L2 | Verifier 检测 | 每步检查 + 空结果检测 |
| L3 | 状态回滚 | 连续失败 3 次 → 回滚到成功快照 |
| L4 | 成本熔断 | Token 上限 50K + 80% 告警 |

**深读**：[agent-reliability §三 4 层工程防线](../../03-engineering/agent-reliability/README.md)

---

### Step 6: Memory 设计（30 分钟）

**输入**：Step 5 可靠性防线
**输出**：Memory 类型 + 存储方案

**4 类 Memory**：

| 类型 | 作用 | 存储 |
|------|------|------|
| 短期记忆 | 当前任务上下文 | Context Window |
| 工作记忆 | 中间结果 | KV Store / DB |
| 长期记忆 | 历史经验 | Vector Store |
| 外部记忆 | 知识库 | RAG / 数据库 |

**深读**：[agent-memory §二 4 类 Memory](../agent-memory/README.md)

---

### Step 7: 评测体系（2 小时）

**输入**：Step 6 Memory 设计
**输出**：评测指标 + 基准数据集

**6 维评测**：

| 维度 | 权重 | 指标 |
|------|------|------|
| 任务完成 | 40% | 成功率 / 步骤正确率 |
| 步骤效率 | 20% | 平均步骤数 / Token 消耗 |
| 工具使用 | 10% | 工具调用准确率 |
| 成本控制 | 10% | 单次任务成本 |
| 用户满意 | 15% | 评分 / NPS |
| 稳定性 | 5% | 一致性 / 漂移率 |

**深读**：[agent-evaluation §二 6 维评测体系](../../08-llmops/agent-evaluation/README.md)

---

### Step 8: 监控上线（1 小时）

**输入**：Step 7 评测体系
**输出**：监控指标 + 告警规则

**4 维监控**：

| 维度 | 指标 | 告警阈值 |
|------|------|---------|
| 性能 | 延迟 / Token 消耗 | P99 > 5s / Token > 50K |
| 质量 | 成功率 / 一致性 | 成功率 < 95% / 一致性 < 0.95 |
| 成本 | 单次任务成本 | > $0.10 |
| 稳定性 | 漂移率 / 错误率 | 漂移 > 0.05 / 错误 > 5% |

**深读**：[production-stability §二 4 维监控](../../08-llmops/production-stability/README.md)

---

## 端到端 Checklist（一页纸）

```text
□ Step 1: 需求分析（30 分钟）
  □ 任务类型：探索性 vs 确定性
  □ 合规要求：审计轨迹
  □ 成本预算：Token 上限
  □ 失败容忍度：重试次数

□ Step 2: 架构选型（1 小时）
  □ 决策树：DAG / ReAct / Plan-Execute / Multi-Agent
  □ 输出：架构决策文档

□ Step 3: Harness 设计（2 小时）
  □ Prompt 约束：任务边界 + 禁止动作
  □ 工具约束：何时用 / 何时不用
  □ 输出约束：格式 + Schema
  □ 流程约束：节点顺序 + 分支条件

□ Step 4: Loop + Verifier 设计（1 小时）
  □ 任务定义：清晰 + 可验证
  □ Verifier：语法 + 语义 + 空结果
  □ 反馈机制：失败 → 重试

□ Step 5: 可靠性防线（1 小时）
  □ L1 Prompt 约束
  □ L2 Verifier 检测
  □ L3 状态回滚
  □ L4 成本熔断

□ Step 6: Memory 设计（30 分钟）
  □ 短期记忆：Context Window
  □ 工作记忆：KV Store / DB
  □ 长期记忆：Vector Store
  □ 外部记忆：RAG / 数据库

□ Step 7: 评测体系（2 小时）
  □ 6 维评测：任务 / 步骤 / 工具 / 成本 / 满意 / 稳定
  □ 基准数据集：Ground Truth Sets

□ Step 8: 监控上线（1 小时）
  □ 4 维监控：性能 / 质量 / 成本 / 稳定
  □ 告警规则：阈值配置
```

**总耗时**：~8 小时（1 个工作日）

---

## 真实案例：电商客服 Agent

| Step | 决策 | 理由 |
|------|------|------|
| 1 需求 | 确定性任务 + 合规要求 | 订单查询 / 退款流程固定 |
| 2 架构 | DAG Workflow | 流程固定 + 审计需求 |
| 3 Harness | Prompt 约束 + 工具约束 | "只查询订单，不修改数据库" |
| 4 Loop | Verifier 检查订单状态 | 语法 + 业务规则 |
| 5 可靠性 | L1-L4 全加 | 金融场景，零容忍 |
| 6 Memory | 短期 + 工作记忆 | 当前会话 + 订单历史 |
| 7 评测 | 任务完成 40% + 满意 15% | 客服场景重满意 |
| 8 监控 | 4 维全监控 | P99 < 3s / 成功率 > 98% |

---

## 相关章节

### 8 大组件（按流水线顺序）

1. [agent-architecture](../agent-architecture/README.md) — DAG vs ReAct vs Plan-Execute
2. [harness-engineering](../../03-engineering/harness-engineering/README.md) — 4 大 Harness 类型
3. [loop-engineering](../../03-engineering/loop-engineering/README.md) — 循环调用 + Verifier
4. [agent-reliability](../../03-engineering/agent-reliability/README.md) — 4 层防线
5. [agent-memory](../agent-memory/README.md) — 4 类 Memory
6. [agent-evaluation](../../08-llmops/agent-evaluation/README.md) — 6 维评测
7. [production-stability](../../08-llmops/production-stability/README.md) — 4 维监控
8. [agent-execution-patterns](../agent-execution-patterns/README.md) — 4 模式 6 维对比

### 面试题

- [agent-dag-vs-react](../../../13.split-hairs/11.ai/agent-dag-vs-react/README.md) — 架构选型陷阱
- [agent-reliability](../../../13.split-hairs/11.ai/agent-reliability/README.md) — 4 层防线速查
- [production-agent-system-design](../../../13.split-hairs/11.ai/production-agent-system-design/README.md) — 端到端综合设计题

---

← [返回: L4 架构设计](../README.md)
