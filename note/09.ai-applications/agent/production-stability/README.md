<!--module:
  parent: ai-applications/agent
  slug: ai-applications/agent/production-stability
  type: index
  category: AI 应用子 MOC
  summary: LLM 生产稳定性——思维范式 / 成本控制 / 一致性 / 熔断 / 在线监控 / 选型决策树。
-->

# Agent 生产稳定性（Production Stability）

> **定位**：LLM/Agent 在生产环境的稳定性专题——从思维范式到成本控制、失败处理、熔断降级、在线监控与选型决策树。

## 文章清单

| # | 主题 | 路径 | 摘要 |
|---|------|------|------|
| 1 | 思维范式 | [01-thinking-paradigm.md](./01-thinking-paradigm.md) | ReAct / CoT / Plan-Execute 等思维范式与生产稳定性关系 |
| 2 | 成本控制与降级 | [02-cost-control-and-degradation.md](./02-cost-control-and-degradation.md) | Token 预算、降级策略、缓存复用与限流 |
| 3 | 一致性与失败处理 | [03-consistency-and-failure-handling.md](./03-consistency-and-failure-handling.md) | 重试、对账、补偿、回滚与失败分类 |
| 4 | 超时与熔断 | [04-timeout-and-circuit-breaker.md](./04-timeout-and-circuit-breaker.md) | 超时分级、熔断器、隔离舱与故障域 |
| 5 | 在线监控 | [05-online-monitoring.md](./05-online-monitoring.md) | 黄金指标、链路追踪、日志聚合与告警分级 |
| 6 | 选型决策树 | [06-decision-tree.md](./06-decision-tree.md) | 6 大策略选型决策树 |

---

← [返回 Agent](../README.md)
