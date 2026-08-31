<!--
question:
  id: 11.ai-planning-acting-monitoring
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: Agent 架构
  tags: [11.ai, Agent, Planning, Acting, Monitoring, 三阶段闭环]
-->

# Planning/Acting/Monitoring 三阶段闭环面试题

> **一句话定位**：现代 Agent 不是"一次调用就完事"——而是 **Planning（规划）→ Acting（执行）→ Monitoring（监控）** 的闭环。任何一阶段缺失都会导致 Agent 失控。

> **同模块兄弟**：[ReAct vs Plan-and-Execute](../react-vs-plan-execute/) 讲执行模式选型；本文讲**三阶段闭环**的完整实现。

---

## 引子：Agent 执行 50 次工具调用后熔断

```text
凌晨 2 点告警：电商客服 Agent 死循环。
用户问"查订单"→ Agent 调用 search_orders → 返回空 → 换关键词重试
→ 再返回空 → 再换关键词 → 连续 50 次调用触发 Token 熔断（50K）。
```

典型的 Planning + Acting 架构缺陷：没有 Planning 阶段的任务分解（不知道最多试几次），Acting 阶段没有错误恢复（指数退避 / 降级方案），Monitoring 阶段只看了 P99 延迟没看工具调用成本。三阶段闭环缺一不可，6 大反模式中任何一条命中都会让 Agent 在生产环境失控。

---

## 🎯 面试高频拷问

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

## ⚠️ 陷阱 1：只有 Acting，没有 Planning

**症状**：Agent 收到任务就"想到什么做什么"，没有任务分解

**真相**：
- 复杂任务容易遗漏步骤
- 子任务依赖关系混乱
- 无法并行执行，效率低

**修复**：引入 Planning 阶段，用 LLM 分解任务 + 构建 DAG

---

## ⚠️ 陷阱 2：只有 Planning + Acting，没有 Monitoring

**症状**：Agent 执行完就结束，不知道执行得好不好

**真相**：
- 错误任务无法被发现
- 性能瓶颈无法定位
- 无法持续优化

**修复**：引入 Monitoring 阶段，采集 4 维指标 + 异常检测 + 反馈修正

---

## ⚠️ 陷阱 3：Monitoring 只看延迟

**症状**：只监控 P99 延迟，不监控任务完成率 / 错误率 / 成本

**真相**：
- 延迟正常但错误率高 → 用户不满意
- 成本低但任务完成率低 → 资源浪费
- 无法全面评估 Agent 质量

**修复**：监控 4 维度（任务完成率 + 执行延迟 + 工具成本 + 错误率）

---

## ⚠️ 陷阱 4：Planning 过度规划

**症状**：Planning 阶段花 10 分钟分解 100 个子任务，实际只需要 3 个

**真相**：
- Planning 成本过高（Token 消耗 + 延迟）
- 过度规划导致灵活性下降
- 用户等待时间过长

**修复**：
- Planning 阶段设置超时（如 30 秒）
- 子任务数量上限（如 10 个）
- 简单任务跳过 Planning，直接 Acting

---

## ⚠️ 陷阱 5：Acting 不做错误恢复

**症状**：工具调用失败就直接抛异常，整个任务中断

**真相**：
- 一次失败导致整个任务失败
- 用户体验差
- Token 浪费

**修复**：
- 重试策略：指数退避（1s → 2s → 4s）
- 降级方案：主工具失败 → 备用工具
- 部分失败容忍：某个子任务失败，其他子任务继续执行

---

## ⚠️ 陷阱 6：Monitoring 不做反馈修正

**症状**：采集了指标但不用于优化

**真相**：
- 同样的错误反复出现
- 性能瓶颈无法解决
- Agent 质量停滞不前

**修复**：
- 自动修复：检测到异常 → 自动重试 / 降级
- 策略调整：根据监控数据调整 Planning 策略
- 定期回顾：每周分析监控数据，优化 Agent 逻辑

---

## 💡 90 秒面试话术

> "Agent 三阶段闭环是 **Planning → Acting → Monitoring** 的完整循环：
>
> **Planning 阶段**：把用户的高层目标分解为可执行的子任务 + 依赖图。工具选型：LangGraph（状态图 + 条件分支）或 Temporal（工作流引擎 + 持久化）。关键设计：任务分解策略、依赖图构建、失败回退机制。
>
> **Acting 阶段**：按 Planning 输出的依赖图，依次执行子任务。工具选型：Function Calling（工具调用 + Schema 约束）或 MCP（标准化工具接口）。关键设计：工具调用机制、状态流转、错误恢复（指数退避 + 降级方案）。
>
> **Monitoring 阶段**：采集 Agent 运行指标 + 检测异常 + 反馈修正。监控 4 维度：任务完成率、执行延迟、工具调用成本、错误率。工具选型：Langfuse（Trace + 评估）或 Helicone（日志 + 指标 + 告警）。关键设计：阈值告警、趋势告警、根因定位、自动修复。
>
> **6 大反模式**：
> 1. 只有 Acting，没有 Planning → Agent 乱执行
> 2. 只有 Planning + Acting，没有 Monitoring → Agent 失控
> 3. Planning 过度规划 → 成本高、灵活性差
> 4. Acting 不做错误恢复 → 一次失败整个任务失败
> 5. Monitoring 只看延迟 → 无法全面评估质量
> 6. Monitoring 不做反馈修正 → 同样错误反复出现
>
> **一句话总结**：任何一阶段缺失都会导致 Agent 失控。"

---

## 📚 深度阅读

- [主模块深度文章](../../../09.ai-applications/agent/agent-execution-patterns/planning-acting-monitoring/README.md) — 三阶段定义 + 6 反模式 + 工具链选型 + 实战案例
- [ReAct vs Plan-and-Execute](../react-vs-plan-execute/) — 执行模式选型

---

> 📅 2026-09-01 · 咬文嚼字 · Agent 闭环 · ⭐⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回: AI 咬文嚼字](../README.md)
