<!--
question:
  id: 11.ai-production-agent-system-design
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计 + 端到端架构
  tags: [11.ai, Agent, 端到端, 系统设计, 架构选型, Harness, Loop, 可靠性]
-->

# 生产级 Agent 系统端到端搭建 —— 8 步流水线 + 8 大组件

← 返回 [11.ai 面试题](../README.md)

> 引子：面试官问"设计一个生产级 Agent 系统，你怎么从头到尾把架构搭起来？"—— 不是问单个组件，而是问**怎么把 8 大组件串成端到端流水线**。

## 一、核心陷阱（咬文嚼字）

| 陷阱 | 表面理解 | 真实原因 | 核心防护 |
|------|---------|---------|---------|
| **知道组件 ≠ 知道怎么串** | 背 8 篇文章就行 | 缺端到端流水线 + checklist | 8 步流水线 + 每步 checklist |
| **忽略 Harness 设计** | 直接写代码 | 无约束 → Agent 跑偏 | Step 3: Harness 4 大类型 |
| **缺 Verifier** | Agent 自己检查 | 错误累积到最终输出 | Step 4: 每步 Verifier |
| **忽略可靠性防线** | 只关注功能 | 生产环境必踩死循环 | Step 5: 4 层防线 |
| **缺评测体系** | 上线后再说 | 无法量化质量 | Step 7: 6 维评测 |

---

## 二、8 步流水线（端到端）

### Step 1: 需求分析（30 分钟）

**输入**：业务需求文档
**输出**：Agent 能力边界 + 约束清单

**Checklist**：
- [ ] 任务类型：探索性（ReAct） vs 确定性（DAG）？
- [ ] 合规要求：是否需要审计轨迹？
- [ ] 成本预算：单次任务 Token 上限？
- [ ] 失败容忍度：允许重试几次？

**深读**：[agent-architecture §七 何时选 DAG vs ReAct](../../../11.ai/04-architecture/agent-architecture/README.md#七何时选-dag-vs-react)

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

**深读**：[agent-execution-patterns §四 6 维完整打分](../../../11.ai/04-architecture/agent-execution-patterns/README.md)

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

**深读**：[harness-engineering §三 4 大 Harness 类型](../../../11.ai/03-engineering/harness-engineering/README.md)

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

**深读**：[loop-engineering §三 3 大核心组件](../../../11.ai/03-engineering/loop-engineering/README.md)

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

**深读**：[agent-reliability §三 4 层工程防线](../../../11.ai/03-engineering/agent-reliability/README.md)

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

**深读**：[agent-memory §二 4 类 Memory](../../../11.ai/04-architecture/agent-memory/README.md)

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

**深读**：[agent-evaluation §二 6 维评测体系](../../../11.ai/08-llmops/agent-evaluation/README.md)

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

**深读**：[production-stability §二 4 维监控](../../../11.ai/08-llmops/production-stability/README.md)

---

## 三、端到端 Checklist（一页纸）

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

## 四、面试话术（90 秒版本）

### 题目：设计一个生产级 Agent 系统，你怎么从头到尾把架构搭起来？

**高分答案（4 层递进，60-90 秒）**：

```text
1. 一句话定位（10 秒）：
   "不是问单个组件，而是问怎么把 8 大组件串成端到端流水线。
    8 步：需求→架构→Harness→Loop→可靠性→Memory→评测→监控。"

2. 8 步流水线速览（40 秒）：
   "8 步流水线：
   Step 1 需求分析：任务类型（探索 vs 确定）+ 合规 + 成本
   Step 2 架构选型：DAG / ReAct / Plan-Execute 决策树
   Step 3 Harness 设计：4 大约束（Prompt/工具/输出/流程）
   Step 4 Loop + Verifier：每步检查 + 反馈重试
   Step 5 可靠性防线：4 层（L1-L4）
   Step 6 Memory 设计：4 类（短期/工作/长期/外部）
   Step 7 评测体系：6 维（任务 40%/步骤 20%/工具 10%/成本 10%/满意 15%/稳定 5%）
   Step 8 监控上线：4 维（性能/质量/成本/稳定）"

3. 关键决策点（20 秒）：
   "3 个关键决策：
   ① 架构选型：任务明确 → DAG；探索性 → ReAct
   ② Harness 设计：4 大约束缺一不可
   ③ 可靠性防线：L1-L4 全加，生产环境零容忍"

4. 真实案例（20 秒）：
   "电商客服 Agent：
   确定性任务 + 合规要求 → DAG Workflow
   Harness：'只查询订单，不修改数据库'
   可靠性：L1-L4 全加（金融场景）
   评测：任务完成 40% + 满意 15%（客服重满意）
   监控：P99 < 3s / 成功率 > 98%"
```

---

## 五、面试反问（让候选人反客为主）

```text
Q1：贵司 Agent 系统端到端搭建需要多久？
    → 答 8 小时（1 个工作日）= 高分
Q2：贵司 8 步流水线中哪步最耗时？
    → 答 Step 3 Harness 设计（2 小时）= 高分
Q3：贵司 Agent 系统的评测体系是 6 维吗？权重怎么分？
    → 答任务完成 40% + 满意 15% = 高分
Q4：贵司 Agent 监控的告警阈值是多少？
    → 答 P99 < 5s / 成功率 > 95% = 高分
Q5：贵司 Agent 系统的可靠性防线是几层？
    → 答 L1-L4 全加 = 高分
```

---

## 🔗 系列导航表（13.split-hairs · 11.ai 兄弟）

| 章节 | 核心考点 | 频率 |
|------|---------|------|
| [agent-dag-vs-react](../agent-dag-vs-react/README.md) | Agent DAG vs ReAct | ⭐⭐⭐⭐ |
| [agent-memory-classification](../agent-memory-classification/README.md) | Agent 记忆 4 类 | ⭐⭐⭐⭐ |
| [agent-performance-evaluation](../agent-performance-evaluation/README.md) | Agent 评估指标 | ⭐⭐⭐⭐ |
| [agent-reliability](../agent-reliability/README.md) | 4 层防线防跑偏 | ⭐⭐⭐⭐ |
| [claude-code-agentic-search](../claude-code-agentic-search/README.md) | Claude Code 搜索模式 | ⭐⭐⭐⭐ |
| [context-engineering](../context-engineering-interview/README.md) | Context Engineering | ⭐⭐⭐⭐⭐ |
| [function-calling](../function-calling/README.md) | Function Calling / Tool Use | ⭐⭐⭐⭐⭐ |
| [harness-engineering](../harness-engineering/README.md) | Harness 兜底工程 | ⭐⭐⭐⭐ |
| [loop-engineering](../loop-engineering/README.md) | Loop 兜底（死循环防护） | ⭐⭐⭐⭐ |
| [long-context-agent-strategy](../long-context-agent-strategy/README.md) | 长上下文策略 | ⭐⭐⭐⭐ |
| [multi-agent-system-design](../multi-agent-system-design/README.md) | Multi-Agent 5 组件 + 死循环 4 兜底 | ⭐⭐⭐⭐⭐ |
| [multi-turn-tool-reasoning](../multi-turn-tool-reasoning/README.md) | 多轮工具推理 | ⭐⭐⭐⭐⭐ |
| [react-vs-plan-execute](../react-vs-plan-execute/README.md) | ReAct vs Plan-Execute | ⭐⭐⭐⭐⭐ |
| [temperature-zero-myth](../temperature-zero-myth/README.md) | Temperature=0 仍变化 | ⭐⭐⭐⭐ |
| **production-agent-system-design**（本篇）| 端到端 8 步流水线 + 8 大组件 | ⭐⭐⭐⭐⭐ |

## 🔗 深度版（主模块）

- [11.ai · production-agent-system-design](../../../11.ai/04-architecture/production-agent-system-design/README.md) —— 8 步流水线详细 checklist + 真实案例（电商客服 Agent）

---

> 📅 2026-07-29 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 8 步流水线 + 8 大组件 + 90 秒话术 + 14 兄弟导航

← [返回: 11.ai 面试题](../README.md)
