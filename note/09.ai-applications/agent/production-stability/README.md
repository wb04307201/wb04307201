<!--module:
  parent: 09.ai-applications
  slug: 09.ai-applications/agent/production-stability
  type: index-only
  category: Agent 子模块索引
  summary: LLM 生产稳定性——思维范式 / 成本控制 / 一致性 / 熔断 / 在线监控 / 选型决策树。
  depth: ⭐⭐⭐⭐⭐
-->

# Agent 生产稳定性（Production Stability）

> ⬅️ [返回 09.ai-applications Agent 目录](../README.md)

## 📍 一句话定位

**Agent 生产稳定性 = LLM/Agent 在生产环境的"6 道防线"**——从思维范式（Prompt vs if-else）→ 成本控制（5 层路由 + quota）→ 一致性（Self-Consistency 投票）→ 熔断降级（双 timeout + Circuit Breaker）→ 在线监控（Trace + 黄金集）→ 决策树选型，覆盖 75% 上线 30 天内遇到的准确率下降 / 幻觉率飙升等真实事故。

## 🗂️ 文章清单

| # | 主题 | 难度 | 路径 | 核心内容 |
|---|------|------|------|---------|
| 1 | 思维范式 | ⭐⭐⭐ | [01-thinking-paradigm.md](./01-thinking-paradigm.md) | Prompt vs if-else 决策矩阵——"能用规则就别用 LLM"，含 ROI 公式 + 8 大场景特征对照 |
| 2 | 成本控制与降级 | ⭐⭐⭐ | [02-cost-control-and-degradation.md](./02-cost-control-and-degradation.md) | 5 层路由降级（cheap→small→big→SaaS→人工）+ 硬成本上限 + 单请求 quota + 实时监控 + 反模式 |
| 3 | 一致性与失败处理 | ⭐⭐⭐⭐ | [03-consistency-and-failure-handling.md](./03-consistency-and-failure-handling.md) | Self-Consistency 投票 + Judge 模型 + 重试预算 + 多结果聚合 + 失败模式（3 次重试都错的处理） |
| 4 | 超时与熔断 | ⭐⭐⭐ | [04-timeout-and-circuit-breaker.md](./04-timeout-and-circuit-breaker.md) | 双 timeout（5s 软限 + 30s 硬限）+ Circuit Breaker + Fallback 模型 + Hystrix 模式应用 |
| 5 | 在线监控 | ⭐⭐⭐⭐ | [05-online-monitoring.md](./05-online-monitoring.md) | Trace（链路追踪）+ 黄金集回归 + 漂移检测——5 分钟定位问题（vs 数天排查）+ 5 大常见事故 |
| 6 | 选型决策树 | ⭐⭐⭐ | [06-decision-tree.md](./06-decision-tree.md) | 5 大问题场景化决策树 + 反模式 + checklist + "5 分钟选型"速查 |

## 🔗 关联主题

- [../agent-reliability/](../agent-reliability/) — Agent 可靠性（4 大机制 + 失败恢复 + 监控），是生产稳定性的系统级实现
- [../loop-engineering/](../loop-engineering/) — Loop 工程（自动修复 + Verifier），与重试预算、超时控制直接耦合
- [../production-agent/](../production-agent/) — 生产级 Agent 工程实践，与本目录的"思维范式 + 决策树"形成方法论+实战对照
- [../production-agent-system-design/](../production-agent-system-design/) — 生产级 Agent 系统设计（高可用架构 + 容量评估 + 容灾），从系统视角看稳定性
- [09.ai-applications/llm-inference](../../llm-inference/README.md) — LLM 推理优化（KV Cache / Paged Attention），是降低单请求延迟/成本的技术底座

## 📚 学习路径

1. **先建思维范式**：读 [01-thinking-paradigm.md](./01-thinking-paradigm.md)，建立"Prompt vs if-else"决策矩阵，避免"上来就用 LLM"的反模式
2. **再学成本控制**：读 [02-cost-control-and-degradation.md](./02-cost-control-and-degradation.md)，5 层路由 + quota 三道防线（血泪教训：循环 bug 一晚上烧 $12,000）
3. **学一致性策略**：读 [03-consistency-and-failure-handling.md](./03-consistency-and-failure-handling.md)，理解"重试 3 次都错"是 LLM 概率性本质，必须靠 Self-Consistency 投票
4. **熔断与超时**：读 [04-timeout-and-circuit-breaker.md](./04-timeout-and-circuit-breaker.md)，双 timeout + Circuit Breaker + Fallback 三道防线（30 分钟 LLM 故障导致 DAU 跌 40% 的真实案例）
5. **在线监控**：读 [05-online-monitoring.md](./05-online-monitoring.md)，Trace + 黄金集回归 + 漂移检测，5 分钟定位问题的工程方案
6. **速查决策树**：最后读 [06-decision-tree.md](./06-decision-tree.md)，把前 5 章的方法论压成 5 分钟决策树

## 🎯 为什么生产稳定性是 Agent 的生死线？

LLM 上线后 30 天内，**75% 的产品会遇到"准确率下降 / 幻觉率飙升"**——但排查需要数天（Helicone 2024 报告）。5 大常见事故：

1. 上游模型升级（OpenAI / Anthropic 静默更新权重）
2. Prompt 改动未回归（同事改了一个变量）
3. 用户分布漂移（新场景出现）
4. 数据漂移（外部知识库过期）
5. 第三方依赖（Embedding 模型变化影响 RAG）

→ 生产稳定性 6 章是按"思维 → 成本 → 一致性 → 熔断 → 监控 → 决策树"顺序展开的完整防御体系。

## 🧭 6 章知识拓扑

```text
thinking-paradigm（思维：何时用 LLM）
       ↓
cost-control（成本：5 层路由 + quota）
       ↓
consistency-failure（一致性：Self-Consistency + Judge）
       ↓
timeout-circuit-breaker（熔断：双 timeout + Circuit Breaker）
       ↓
online-monitoring（监控：Trace + 黄金集 + 漂移）
       ↓
decision-tree（决策：5 分钟选型速查）
```

## 📊 本节统计

> 本目录当前收录 6 篇子文章（thinking-paradigm / cost-control / consistency / timeout / monitoring / decision-tree），由 `find` 在 `2026-08-20` 校对。

---

← [返回 Agent 目录](../README.md)