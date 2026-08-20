<!--module:
  parent: 09.ai-applications
  slug: 09.ai-applications/agent/intelligent-system-layers
  type: index-only
  category: Agent 子模块索引
  summary: 智能系统三层架构——规则 / 启发式 / LLM 三层职责划分与协作模式。
-->

# 智能系统分层（Intelligent System Layers）

> ⬅️ [返回 09.ai-applications Agent 目录](../README.md)

## 📍 一句话定位

**智能系统分层 = 规则层（Rule）+ 启发式层（Heuristic）+ LLM 智能层**——按"成本 × 灵活性 × 可解释性"三维把任务分配到合适的层，避免"全用 LLM"造成的成本失控与不可审计问题。

## 🗂️ 文章清单

| # | 主题 | 难度 | 路径 | 核心内容 |
|---|------|------|------|---------|
| 1 | 智能系统三层 | ⭐⭐⭐⭐ | [system-three-layers.md](./system-three-layers.md) | 感知/认知/决策三层解耦与跨层协同，含硬件（仿生传感器 / 边缘芯片）、模型（LSTM+Transformer 多模态融合）与算法（贝叶斯推理 / 数据-特征-决策三级融合）选型参考 |

> 📌 本目录当前聚焦"分层架构"的硬件/数据/算法三层视角；与"规则 vs 启发式 vs LLM"业务三层视角互补——前者偏工程实现，后者偏业务决策。

## 🔗 关联主题

- [../agent-architecture/](../agent-architecture/) — Agent 系统级架构（BPMN + AI 融合），是分层架构在企业流程中的落地形态
- [../agent-execution-patterns/](../agent-execution-patterns/) — 4 大执行模式（ReAct / Plan-and-Execute / DAG / Multi-Agent），分层架构的执行层实现
- [../production-stability/01-thinking-paradigm.md](../production-stability/01-thinking-paradigm.md) — 思维范式：Prompt vs if-else（决策矩阵），是"业务分层"侧的方法论
- [../agent-memory/](../agent-memory/) — Agent 4 层记忆（working/episodic/semantic/procedural），是"认知层"的具体实现
- [../../08.ai-foundations/llm-inference/](../../../08.ai-foundations/llm-inference/) — LLM 推理优化（KV Cache / Paged Attention），分层架构中"智能层"的性能底座

## 📚 学习路径

1. **先建业务分层观**：读 [../production-stability/01-thinking-paradigm.md](../production-stability/01-thinking-paradigm.md) 的决策矩阵，理解"何时用规则、何时用 LLM"
2. **再读 [system-three-layers.md](./system-three-layers.md)**：掌握感知/认知/决策三层物理-数据-算法实现，看多模态融合与边缘智能的实际工程方案
3. **纵向对照记忆层**：跳到 [../agent-memory/](../agent-memory/)，看 working/episodic/semantic/procedural 4 层记忆如何映射到认知层
4. **横向看执行模式**：读 [../agent-execution-patterns/](../agent-execution-patterns/)，ReAct/Plan-and-Execute 是分层架构在"决策层"的实现路径
5. **企业级落地**：回到 [../agent-architecture/](../agent-architecture/) 看 BPMN+AI 融合案例，理解分层在生产环境的合规与审计价值

## 🎯 为什么需要"三层"抽象？

智能系统的复杂度爆炸，让"单层 LLM 解决一切"成为反模式：

- **成本失控**：每个请求都调 LLM，百万 QPS 下账单爆炸
- **延迟不可控**：LLM 推理 1-5 秒 vs 规则判断 0.1ms，差距 1000 倍
- **不可解释**：黑盒推理无法满足金融/医疗的审计需求

→ 三层架构（规则层快速判断 → 启发式层兜底 → LLM 智能层处理模糊问题）是性能/成本/可解释性的平衡解。

## 🧭 三层职责矩阵

| 层 | 输入特征 | 响应时间 | 成本 | 可解释性 |
|----|---------|---------|------|---------|
| **规则层** | 结构化 / 规则可枚举 | < 1ms | 极低 | ⭐⭐⭐⭐⭐ |
| **启发式层** | 半结构化 / 概率决策 | 1-10ms | 低 | ⭐⭐⭐⭐ |
| **LLM 智能层** | 非结构化 / 自然语言 | 1-5s | 高 | ⭐⭐ |

## 📊 本节统计

> 本目录当前收录 1 篇子文章（系统三层），由 `find` 在 `2026-08-20` 校对。

---

← [返回 Agent 目录](../README.md)