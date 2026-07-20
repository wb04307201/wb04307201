<!--
question:
  id: 11.ai-react-vs-plan-execute
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: Agent 架构选型
  tags: [11.ai, ReAct, Plan-and-Execute, Agent, DAG, Multi-Agent]
-->

# ReAct vs Plan-and-Execute · 4 模式选型深挖

> 一句话定位：Agent 架构选型不是"哪个最好"，而是 **4 模式 6 维对比 + 场景化选型**——ReAct 灵活但贵、Plan-and-Execute 平衡、DAG 稳定但工程重、Multi-Agent 强大但复杂。完整深度见 [主模块 agent-execution-patterns 专题](../../../11.ai/04-architecture/agent-execution-patterns/README.md)。

> **系列定位**：经典 AI Agent 架构面试题（Anthropic / OpenAI / LangChain / 字节 / 阿里 / 美团 高频）。考察的不是"哪个模式最强"，而是 **6 维场景化对比能力** + **Plan Repair 三机制** + **混合架构实战**。

---

## 引子：CTO 选型 ReAct 还是 Plan-and-Execute 的 3 个现场

```text
场景：2024 Q4 某 AI 公司 CTO 阿明要做"AI 投资助手"——
- 输入：用户提问"分析一下腾讯股票"
- 任务：调用 5 个数据源 + 1 个计算 + 1 个总结
- 候选：①ReAct  ②Plan-and-Execute  ③DAG  ④Multi-Agent
```

**决策现场**：
1. **架构师候选人会问**：「ReAct 是不是更灵活，能处理探索性场景？」
2. **资深候选人会问**：「5-20 步 + 强依赖的任务，到底 ReAct 还是 Plan-and-Execute？RePlan 怎么实现？」
3. **CTO 候选人会问**：「生产环境我们想合规审计 + 灵活处理未知异常，怎么混合 4 模式？」

普通候选人会答："ReAct 更灵活"——踩中"**理由模糊、缺反模式、缺混合**" 3 大雷区。
高分候选人会答：**6 维对比（灵活性 / 预测 / token / 延迟 / 复现 / 复杂度）+ RePlan 3 机制 + 80% DAG 混合**。

---

## 一、核心原理（必选）

### 1.1 4 模式速览

| 模式 | 全称 | 核心思想 | 代表 |
|------|------|---------|------|
| **ReAct** | Reasoning + Acting | 思考→行动→观察→循环 | BabyAGI / AutoGPT |
| **Plan-and-Execute** | Plan-then-Execute | 先规划再执行 + 失败 RePlan | LangChain P&E / Devin |
| **DAG Workflow** | Directed Acyclic Graph | 节点 + 边的确定性图 | LangGraph / Temporal |
| **Multi-Agent** | Multi-Agent System | 多个 Agent 协作 | CrewAI / AutoGen |

### 1.2 4 模式 6 维打分

| 维度 | ReAct | Plan-and-Execute | DAG | Multi-Agent |
|------|-------|------------------|-----|-------------|
| **灵活性** | 9 | 6 | 4 | 8 |
| **可预测性** | 3 | 7 | 10 | 3 |
| **Token 成本** | 3 | 7 | 9 | 3 |
| **延迟** | 3 | 6 | 9 | 2 |
| **可复现性** | 3 | 6 | 10 | 3 |
| **工程复杂度** | 8 | 5 | 4 | 2 |
| **平均** | 4.8 | **6.2** | **7.7** | 3.5 |

完整对比见 [03-six-dimensions-comparison](../../../11.ai/04-architecture/agent-execution-patterns/03-six-dimensions-comparison.md)。

### 1.3 ReAct 本质（Thought + Action + Observation）

```
Thought: 我需要先查询腾讯股票
Action:  getStockPrice(symbol="0700.HK")
Observation: 当前价 350 HKD

Thought: 我应该再查财报
Action:  getFinancialReport(symbol="0700.HK", year=2024)
Observation: 营收 6000 亿
...（循环 N 次）
```

**核心**：每步 LLM 决策 + 工具执行 + 状态更新。

### 1.4 Plan-and-Execute 本质（两步走）

```
Stage 1 Planner：一次生成 Plan = [Step1, Step2, Step3]
   ↓
Stage 2 Executor：逐步执行
   - 失败 → RePlan / Adaptive / Plan Repair
```

### 1.5 3 大重规划机制

| 机制 | 描述 | 适用 |
|------|------|------|
| **RePlan** | 完全重规划 | 失败严重 |
| **Adaptive** | 部分调整 | 中等失败 |
| **Plan Repair** | 精准修复 | 轻量失败 |

工业实践：失败 ≤ 2 用 Plan Repair；3-5 用 Adaptive；> 5 触发 RePlan + 人工。

### 1.6 ReAct 5 大硬伤

1. **Token 消耗不可控**（每步 Thought）
2. **执行路径不可复现**（temperature > 0）
3. **Context 越长越混乱**（8000 token 后模型忘掉早期）
4. **迷路循环**（max_iterations 上限缺失）
5. **合规审计困难**（金融 / 医疗）

---

## 二、面试话术（90 秒版本 / 7 道）

> ⚠️ **模板不是背答案**——面试现场结合题目微调。

### 题目 A：ReAct 和 Plan-and-Execute 各自特点？什么时候选哪个？

**高分答案**（4 层递进，60-90 秒）：

```
1. 场景区分（15 秒）：
   "ReAct 用于'探索'（路径未知），Plan-and-Execute 用于'复杂多步 + 强依赖'。
   两者不是替代，是不同场景的工具。"

2. ReAct 特点（20 秒）：
   "ReAct = Thought + Action + Observation 三元组，
   LLM 自己决定下一步，最灵活但 Token 不可控、路径不可复现。
   适合：开放问答、客服对话、adhoc 数据分析。"

3. Plan-and-Execute 特点（25 秒）：
   "Plan-and-Execute = 一次规划 + 逐步执行 + 失败 RePlan。
   比 ReAct 多一个规划层，可控性更高但开发重。
   适合：5-20 步复杂任务、步骤间强依赖、需要修复失败。"

4. 选型决策（20 秒）：
   "判断公式：
   - 步骤数 ≤ 5 + 路径未知 → ReAct
   - 步骤数 5-20 + 路径大致清楚 → Plan-and-Execute
   - 业务流固定 → DAG
   - 多角色协作 → Multi-Agent

   工业实操：80% 是 DAG 主 + ReAct 子节点 + Plan Repair 修复。"
```

### 题目 B：Plan-and-Execute 失败怎么办？怎么 RePlan？

**高分答案**（60 秒）：

```
"Plan-and-Execute 失败有 3 大修复机制（按粒度）：

1. Plan Repair（推荐）：
   - LLM 推理错误根因
   - 精准修改 Step inputs / tool
   - 适用：参数错、临时错误

2. Adaptive Plan：
   - 部分 Plan 可用，跳过失败 + 插入兜底
   - 适用：失败中等（3-5 次）

3. RePlan（重规划）：
   - 丢弃剩余 Plan，重新规划
   - 适用：失败严重（> 5 次）

工业升级路径：
- 失败 ≤ 2：Plan Repair
- 失败 3-5：升级 Adaptive
- 失败 > 5：RePlan + 人工兜底

反模式：失败就盲目 RePlan（token 浪费）
正解：先 Repair，失败升级再 Adaptive，最后 RePlan。"
```

### 题目 C：ReAct 的 Token 失控问题怎么解决？

**高分答案**（45 秒）：

```
"ReAct Token 失控的 5 大解决方案：

1. 设置 max_iterations 上限（10-30）
2. 阶段性 Summary（每 5 轮压缩 context）
3. 工具约束（限制 ≤ 10 个工具，避免决策爆炸）
4. temperature=0（确定性，避免随机路径）
5. 兜底切换（ReAct 失败 → Plan-and-Execute）

实测：
- ReAct 同等任务 = 8500 tokens
- Plan-and-Execute 同等任务 = 4500 tokens（降 47%）
- DAG 同等任务 = 2800 tokens（降 67%）

反模式：
- max_iterations = 0（Agent 无限循环）
- 不做 Summary（context 爆炸）
- 默认 temperature=0.7（生产环境）"
```

### 题目 D：ReAct 和 DAG 怎么选？

**高分答案**（40 秒）：

```
"ReAct vs DAG 决策：
1. 任务流程是否明确？
   - 完全明确 → DAG
   - 部分明确 → Plan-and-Execute
   - 完全未知 → ReAct

2. 是否需要审计？
   - 需要 → DAG（路径可追溯）
   - 不需要 → 可选项

3. Token 成本敏感？
   - 是 → DAG（每个节点 1 次 LLM）
   - 否 → 可选

工业实操：80% 业务用 DAG，ReAct 仅用于探索性子任务。

反模式：
- 业务流用 ReAct（路径不稳）
- 完全探索用 DAG（流程卡死）"
```

### 题目 E：Multi-Agent 一定比单 Agent 强吗？

**高分答案**（40 秒）：

```
"Multi-Agent 不一定比单 Agent 强。Multi-Agent 平均分 3.5（4 模式最低）。

3 大问题：
1. 通信开销（Agent 间消息占 LLM 调用 > 50%）
2. 循环调用（A→B→A 无终止）
3. 调试困难（多 Agent 状态）

80% 场景单 Agent 足够。多 Agent 适用：
- 复杂业务需多角色（PM + Designer + Engineer）
- 任务需辩论 / 评审（多视角）

反模式：
- 简单任务用 Multi-Agent
- 没 max_turns 终止条件
- 没 Trace 调试工具"
```

### 题目 F：生产环境应该选哪个？4 模式混合吗？

**高分答案**（45 秒）：

```
"生产环境 80% 是混合架构，不是单一模式：

工业标准：DAG + Plan-and-Execute + ReAct 兜底
- DAG：主流程（确定性部分）
- Plan-and-Execute：复杂多步子任务
- ReAct：未知异常子节点
- Plan Repair：失败修复节点

案例：
- LangGraph → DAG + 局部 ReAct 节点
- Devin → Plan-and-Execute + DAG
- Claude Code → DAG 主流程 + Loop 兜底
- Cursor Composer → 纯 DAG

关键：每种模式用于它最擅长的场景，而不是挑一个'最好'。"
```

### 题目 G：Multi-Agent 通信开销怎么优化？

**高分答案**（40 秒）：

```
"Multi-Agent 通信开销是最大性能瓶颈。3 大优化：

1. 摘要传递：
   - Agent A → B 不传完整 prompt，只传摘要
   - 节省 60-80% token

2. 异步通信：
   - 不阻塞主 Agent
   - Background Agent + Callback

3. 协调者模式：
   - 中央 Coordinator 调度
   - 子 Agent 无横向通信

反模式：
- Agent 横向互发消息（每轮 LLM 推理）
- 没 max_turns 终止（A→B 一直发）
- 完整 prompt 传递（冗余）

工业方案：CrewAI 已自动摘要传递。"
```

---

## 三、常见陷阱（必选，7 个核心反模式）

### 陷阱 1：业务流强用 ReAct

- **错误**：退款流程让 Agent 自己探索 5 步
- **真相**：业务流路径固定，DAG 更适合
- **代价**：Token 失控 + 路径不稳

### 陷阱 2：一次性规划 50 步

- **错误**：让 LLM 一次输出 50 步 Plan
- **真相**：超 20 步规划质量断崖
- **代价**：规划失败率高，多次 RePlan

### 陷阱 3：ReAct 不设 max_iterations

- **错误**：让 Agent 无限循环
- **真相**：必须上限（10-30 次）
- **代价**：Token 爆炸 + 响应延迟

### 陷阱 4：盲目相信 Multi-Agent

- **错误**："Agent 越多越强"
- **真相**：80% 场景单 Agent 足够
- **代价**：通信开销 + 调试困难

### 陷阱 5：默认温度 0.7

- **错误**：所有 Agent 默认 temperature=0.7
- **真相**：执行型 0 / 探索型 0.7
- **代价**：执行型路径不可复现

### 陷阱 6：Plan Repair 不分析错误根因

- **错误**：失败就盲目 RePlan
- **真相**：先推理错误根因
- **代价**：RePlan 频繁，token 浪费

### 陷阱 7：4 模式只用一个

- **错误**：只用 ReAct 或只用 DAG
- **真相**：混合架构（DAG + Plan Repair + ReAct 兜底）
- **代价**：单模式各有硬伤

---

## 四、最佳实践（4 模式工业方案）

### 方案 A：客服对话（ReAct 主导）

```
- 模式：ReAct + 温度=0
- 工具：≤ 10 个高频
- 优化：max_iterations=15 + Summary
- 监控：P95 延迟 + 准确率
```

### 方案 B：投资分析（Plan-and-Execute 主导）

```
- 模式：Plan-and-Execute + DAG 子节点
- 规划：5-10 高层步骤
- 修复：Plan Repair 2 次 → Adaptive 1 次 → RePlan
- 监控：每步 Trace
```

### 方案 C：退款业务流（DAG 主导）

```
- 模式：DAG + 错误处理节点
- 节点：query_order → check_eligibility → process_refund → notify
- 错误：每个节点加 Error Handler
- 监控：节点耗时 + 成功率
```

### 方案 D：AI 软件团队（Multi-Agent）

```
- 模式：CrewAI + Hierarchical
- 角色：PM / Designer / Engineer / Reviewer
- 通信：摘要传递（不是完整 prompt）
- 终止：max_turns=10
```

### 选型决策表

| 场景 | 主模式 | 副模式 |
|------|--------|--------|
| 客服对话 | ReAct | Summary |
| 投资研究 | Plan-and-Execute | DAG 子节点 |
| 退款流 | DAG | Error Handler |
| 代码生成 | DAG + Loop | Plan Repair |
| 数据分析 | DAG | ReAct 子节点 |
| 创意写作 | ReAct + 0.7 温度 | 多版本投票 |
| AI 团队 | Multi-Agent | Hierarchical |

---

## 五、相关章节（强制）

### 主模块深度专题

- [agent-execution-patterns 总目录](../../../11.ai/04-architecture/agent-execution-patterns/README.md)
- [01-react-deep-dive](../../../11.ai/04-architecture/agent-execution-patterns/01-react-deep-dive.md) —— ReAct 深度 + 5 硬伤
- [02-plan-and-execute-deep-dive](../../../11.ai/04-architecture/agent-execution-patterns/02-plan-and-execute-deep-dive.md) —— 规划方法 + 3 大修复机制
- [03-six-dimensions-comparison](../../../11.ai/04-architecture/agent-execution-patterns/03-six-dimensions-comparison.md) —— 4 模式 6 维对比
- [04-selection-decision-tree](../../../11.ai/04-architecture/agent-execution-patterns/04-selection-decision-tree.md) —— 5 分钟决策树

### 同栏目（11.ai）姐妹篇

- [agent-dag-vs-react](../../11.ai/agent-dag-vs-react/README.md) —— DAG vs ReAct 已有深度
- [agent-architecture](../../../11.ai/04-architecture/agent-architecture/README.md) —— 4 模式综述
- [loop-engineering](../../11.ai/loop-engineering/README.md) —— Loop Engineering 失败模式
- [harness-engineering](../../11.ai/harness-engineering/README.md) —— Harness 是 DAG 的强约束

### 主模块兄弟

- [11.ai/04-architecture/agent-architecture](../../../11.ai/04-architecture/agent-architecture/README.md) —— Agent 架构总览
- [11.ai/04-architecture/agent-context/05-sub-agents-decomposition](../../../11.ai/04-architecture/agent-context/05-sub-agents-decomposition.md) —— Multi-Agent Sub-Agents 实战

### 实战姐妹（12.story）

- [12.story/02-system-architecture-evolution](../../../12.story/02-system-architecture-evolution.md) —— 阿明餐厅选型 ReAct vs Plan-and-Execute 实战
- [12.story/05-observability](../../../12.story/05-observability.md) —— AI 思维工程 5 问（监控）

---

## 六、面试反问（让候选人反客为主）

```
Q1：贵司 Agent 是业务流程（退款 / 订单）还是探索研究？
    → 业务流 DAG，探索 ReAct
Q2：贵司任务典型步骤数？
    → ≤ 5 用 ReAct/DAG，5-20 用 Plan-and-Execute，> 20 分层
Q3：贵司对延迟的 P95 SLO 是多少？
    → < 1s 强制 DAG，< 5s 可 ReAct/Plan，> 5s 都行
Q4：贵司是否多角色协作（PM + Designer + Engineer）？
    → 是：Multi-Agent；否：单 Agent + 模式组合
Q5：贵司对答案准确性的要求？
    → 高合规用 DAG，可接受灵活用 ReAct/Plan-and-Execute
```

---

> 📅 2026-07-06 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 7 道精选 Q&A · 含 90 秒话术模板

← [返回: 咬文嚼字 · react-vs-plan-execute](../README.md)
