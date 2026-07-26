<!--
module:
  parent: ai/04-architecture/agent-execution-patterns
  slug: ai/agent-execution-patterns/planning-acting-monitoring
  type: article
  category: Agent 执行模式
  summary: Agent 三阶段闭环：Planning（规划）→ Acting（执行）→ Monitoring（监控）的 6 大反模式 + 实战案例 + 工具链选型
-->

# Agent 三阶段闭环：Planning → Acting → Monitoring

← [返回: Agent 执行模式](../README.md)

> **一句话定位**：现代 Agent 不是"一次调用就完事"——而是 **Planning（规划任务）→ Acting（执行动作）→ Monitoring（监控反馈）** 的闭环。任何一阶段缺失都会导致 Agent 失控。

---

## 0. 面试高频拷问

```text
Q：Agent 如何实现 Planning、Acting、Monitoring 三阶段闭环？
Q：为什么只让 Agent "思考 + 行动" 不够？
Q：Monitoring 阶段具体监控什么？
```

**回答框架（3 层递进）**：

1. **三阶段定义**：Planning（任务分解 + 依赖图）→ Acting（工具调用 + 状态流转）→ Monitoring（指标采集 + 异常检测 + 反馈修正）
2. **为什么缺一不可**：缺 Planning → Agent 乱执行；缺 Acting → Agent 空想；缺 Monitoring → Agent 失控
3. **工具链选型**：Planning 用 LangGraph / Temporal；Acting 用 Function Calling；Monitoring 用 Langfuse / Helicone

---

## 1. 三阶段定义

### 1.1 Planning（规划阶段）

**核心任务**：把用户的高层目标分解为可执行的子任务 + 依赖关系。

```text
用户目标："帮我分析 Q3 销售数据并生成报告"

Planning 输出：
├─ 子任务 1：从数据库拉取 Q3 销售数据（依赖：无）
├─ 子任务 2：数据清洗 + 异常值检测（依赖：子任务 1）
├─ 子任务 3：生成可视化图表（依赖：子任务 2）
├─ 子任务 4：撰写分析报告（依赖：子任务 2 + 3）
└─ 子任务 5：发送报告给管理层（依赖：子任务 4）
```

**关键设计**：
- **任务分解策略**：LLM 根据用户意图 + 历史案例分解
- **依赖图构建**：DAG（有向无环图）表示子任务依赖
- **失败回退**：某个子任务失败时，是重试还是跳过？

### 1.2 Acting（执行阶段）

**核心任务**：按 Planning 输出的依赖图，依次执行子任务。

```python
# 伪代码：按依赖图执行
for task in topo_sort(dag):
    if task.dependencies_satisfied():
        result = execute_tool(task.tool_name, task.params)
        task.mark_completed(result)
    else:
        task.mark_failed("Dependencies not met")
```

**关键设计**：
- **工具调用**：Function Calling / Tool Use 机制
- **状态流转**：任务状态（pending → running → completed/failed）
- **错误恢复**：失败任务的重试策略（指数退避 / 降级方案）

### 1.3 Monitoring（监控阶段）

**核心任务**：采集 Agent 运行指标 + 检测异常 + 反馈修正。

```text
监控 4 维度：
├─ 1. 任务完成率：成功完成的子任务数 / 总子任务数
├─ 2. 执行延迟：每个子任务的 P50 / P95 / P99 延迟
├─ 3. 工具调用成本：每次工具调用的 Token 消耗 + API 费用
└─ 4. 错误率：工具调用失败率 / 任务失败率

异常检测：
├─ 阈值告警：错误率 > 10% → 告警
├─ 趋势告警：延迟持续上升 → 告警
└─ 根因定位：Trace 追踪失败任务的具体步骤

反馈修正：
├─ 自动修复：检测到异常 → 自动重试 / 降级
├─ 人工介入：严重异常 → 通知人工处理
└─ 策略调整：根据监控数据调整 Planning 策略
```

---

## 2. 6 大反模式

### ❌ 反模式 1：只有 Acting，没有 Planning

**症状**：Agent 收到任务就"想到什么做什么"，没有任务分解

**问题**：
- 复杂任务容易遗漏步骤
- 子任务依赖关系混乱
- 无法并行执行，效率低

**修复**：引入 Planning 阶段，用 LLM 分解任务 + 构建 DAG

---

### ❌ 反模式 2：只有 Planning + Acting，没有 Monitoring

**症状**：Agent 执行完就结束，不知道执行得好不好

**问题**：
- 错误任务无法被发现
- 性能瓶颈无法定位
- 无法持续优化

**修复**：引入 Monitoring 阶段，采集 4 维指标 + 异常检测 + 反馈修正

---

### ❌ 反模式 3：Planning 阶段过度规划

**症状**：Planning 阶段花 10 分钟分解 100 个子任务，实际只需要 3 个

**问题**：
- Planning 成本过高（Token 消耗 + 延迟）
- 过度规划导致灵活性下降
- 用户等待时间过长

**修复**：
- Planning 阶段设置超时（如 30 秒）
- 子任务数量上限（如 10 个）
- 简单任务跳过 Planning，直接 Acting

---

### ❌ 反模式 4：Acting 阶段不做错误恢复

**症状**：工具调用失败就直接抛异常，整个任务中断

**问题**：
- 一次失败导致整个任务失败
- 用户体验差
- Token 浪费

**修复**：
- 重试策略：指数退避（1s → 2s → 4s）
- 降级方案：主工具失败 → 备用工具
- 部分失败容忍：某个子任务失败，其他子任务继续执行

---

### ❌ 反模式 5：Monitoring 阶段只看延迟

**症状**：只监控 P99 延迟，不监控任务完成率 / 错误率 / 成本

**问题**：
- 延迟正常但错误率高 → 用户不满意
- 成本低但任务完成率低 → 资源浪费
- 无法全面评估 Agent 质量

**修复**：监控 4 维度（任务完成率 + 执行延迟 + 工具成本 + 错误率）

---

### ❌ 反模式 6：Monitoring 阶段不做反馈修正

**症状**：采集了指标但不用于优化

**问题**：
- 同样的错误反复出现
- 性能瓶颈无法解决
- Agent 质量停滞不前

**修复**：
- 自动修复：检测到异常 → 自动重试 / 降级
- 策略调整：根据监控数据调整 Planning 策略（如：某类任务经常失败 → 调整分解策略）
- 定期回顾：每周分析监控数据，优化 Agent 逻辑

---

## 3. 工具链选型

| 阶段 | 推荐工具 | 核心能力 | 适用场景 |
|------|---------|---------|---------|
| **Planning** | LangGraph | 状态图 + 条件分支 + 循环 | 复杂多步任务 |
| **Planning** | Temporal | 工作流引擎 + 持久化 + 重试 | 长耗时任务 |
| **Acting** | Function Calling | 工具调用 + Schema 约束 | 所有场景 |
| **Acting** | MCP（Model Context Protocol） | 标准化工具接口 | 多工具协作 |
| **Monitoring** | Langfuse | Trace + 评估 + 黄金集 | 全链路追踪 |
| **Monitoring** | Helicone | 日志 + 指标 + 告警 | 轻量监控 |
| **Monitoring** | Phoenix（Arize） | LLM 可观测性 | 深度分析 |

---

## 4. 实战案例：客服 Agent

```text
用户问题："我的订单什么时候到？"

=== Planning 阶段 ===
子任务 1：从用户 ID 获取订单号（工具：get_user_orders）
子任务 2：查询订单物流状态（工具：query_logistics）
子任务 3：生成回复（工具：generate_response）

依赖图：
  子任务 1 → 子任务 2 → 子任务 3

=== Acting 阶段 ===
执行子任务 1：调用 get_user_orders(user_id="u_123")
  → 返回：订单号 = "order_456"

执行子任务 2：调用 query_logistics(order_id="order_456")
  → 返回：物流状态 = "已发货，预计明天到达"

执行子任务 3：调用 generate_response(context="已发货，预计明天到达")
  → 返回："您的订单已发货，预计明天到达。"

=== Monitoring 阶段 ===
采集指标：
  - 任务完成率：3/3 = 100%
  - 执行延迟：P99 = 2.3s
  - 工具调用成本：$0.003
  - 错误率：0%

异常检测：无异常

反馈修正：无需调整
```

---

## 5. 一句话速查

```text
"Agent 三阶段闭环：
- Planning：任务分解 + 依赖图（LangGraph / Temporal）
- Acting：工具调用 + 状态流转（Function Calling / MCP）
- Monitoring：指标采集 + 异常检测 + 反馈修正（Langfuse / Helicone）
关键：任何一阶段缺失都会导致 Agent 失控。"
```

---

## 6. 交叉引用

- **同系列兄弟**：
  - [ReAct 深度](../01-react-deep-dive.md) — ReAct 循环机制
  - [Plan-and-Execute 深度](../02-plan-and-execute-deep-dive.md) — Plan Repair 机制
  - [6 维对比](../03-six-dimensions-comparison.md) — 4 模式完整对比
  - [选型决策树](../04-selection-decision-tree.md) — 场景化选型

- **相关章节**：
  - [Agent Memory](../../agent-memory/README.md) — 记忆架构（Monitoring 阶段需要）
  - [Function Calling](../../../02-technology-stack/function-calling/README.md) — 工具调用原理（Acting 阶段基础）
  - [LLM 监控](../../../08-llmops/production-stability/05-online-monitoring.md) — 4 维监控体系

---

← [返回: Agent 执行模式](../README.md) · [返回: L4 架构设计](../../README.md)
