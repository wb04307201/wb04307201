<!--
module:
  parent: ai/llm-production-thinking
  slug: ai/llm-production-thinking/06-decision-tree
  type: topic
  category: 5 大问题决策树
  summary: 5 大问题场景化决策树 + 反模式 + checklist + 一句话总结
-->

# 决策树 · 5 大问题场景化选型

> **一句话**：5 大问题没有"最强方案"——只有「**场景 × 风险 × 成本**」3 维约束下的最优组合。给一张「5 分钟决策树」+「实施 checklist」。

← [返回: 大模型思维工程](../README.md)

---

## 1. 5 分钟决策树（按问题逐个走）

### Q1 决策树：何时用 LLM？

```text
输入是结构化数据？
├─ 是 → if-else（不要用 LLM）
└─ 否（自然语言） ↓
规则可枚举（< 50 条）？
├─ 是 → if-else + 漏斗到 LLM 兜底
└─ 否 ↓
错误容许 5%+？
├─ 否 → 必须 if-else（医疗/金融）
└─ 是 ↓
ROI ≥ 10x 规则？
├─ 是 → 用 LLM
└─ 否 → 用规则
```

### Q2 决策树：成本降级

```text
请求 QPS > 100？
├─ 是 → 强制缓存 + cheap 模型优先
└─ 否 ↓
任务简单？
├─ 是 → Layer 2 cheap 模型
└─ 否 ↓
任务关键？
├─ 是 → Layer 3 big 模型 + Judge
└─ 否 → Layer 2 cheap 模型
```

### Q3 决策树：连续不一致

```text
答案是离散（分类 / 短答）？
├─ 是 → Self-Consistency 投票
└─ 否（开放） ↓
Judge 模型选哪？
├─ 通用 → GPT-4
├─ 业务 → 业务 judge
└─ 预算紧 → 开源 70B
Judge 失败？
├─ 是 → Fallback 模型 / 默认选择
└─ 否 → 用 Judge 结果
```

### Q4 决策树：超时熔断

```text
错误率超 50%？
├─ 是 → 立即熔断 30s
└─ 否 ↓
P99 延迟 > 10s 持续 5 分钟？
├─ 是 → 熔断 + 降级
└─ 否 ↓
供应商故障？
├─ 是 → 切换 Fallback 供应商
└─ 否 → 继续观察
```

### Q5 决策树：线上监控

```text
已经上线多久？
├─ < 30 天 → 重点：黄金集 + Trace
├─ 30-180 天 → 加：漂移检测 + 成本监控
└─ > 180 天 → 重点：漂移检测 + 自动回滚

事故频率？
├─ < 1 次/月 → 健康
├─ 1-4 次/月 → 重点优化
└─ > 4 次/月 → 重新设计架构
```

---

## 2. 5 大问题配置矩阵

| 场景 | 思维范式 | 成本策略 | 一致性策略 | 熔断策略 | 监控策略 |
|------|---------|---------|-----------|---------|---------|
| 客服 Agent | 规则优先 | Layer 2 cheap | Self-Consistency | 双 timeout | Trace + 黄金集 |
| 代码助手 | LLM 主 + 规则校验 | Layer 3 big | Judge + Self-Reflection | 双 timeout + 熔断 | Trace + 漂移 |
| 内容生成 | LLM 全程 | Layer 3 + Judge | Judge 投票 | 双 timeout | 质量回归 |
| 金融分析 | 规则优先 + LLM 兜底 | Layer 3 + 人审 | 多供应商投票 | 强熔断 + 转人工 | 强监控 + 审计 |
| 文档问答 | LLM 主 + 缓存 | Layer 2 + RAG | Self-Consistency | 双 timeout | Trace + 黄金集 |

---

## 3. 实施 Checklist（部署前必过）

### 3.1 设计阶段

- [ ] 思维范式决策（哪些用规则，哪些用 LLM）
- [ ] 5 层路由配置（cheap → big → SaaS → human）
- [ ] 3 道 quota（单请求 / 单用户 / 单租户）
- [ ] Self-Consistency 投票 + Judge 模型
- [ ] 双 timeout（5s 软限 + 30s 硬限）
- [ ] Fallback 供应商列表（≥ 2 个）

### 3.2 上线前

- [ ] 黄金集 ≥ 50 题（覆盖核心场景）
- [ ] 跑黄金集准确率 ≥ 85%
- [ ] 监控大盘配置（4 维指标）
- [ ] Trace 平台接入（Langfuse / Helicone）
- [ ] 漂移检测 baseline 设定
- [ ] 告警阈值设定（P99 / 成本 / 准确率）

### 3.3 上线后

- [ ] **每天**：监控大盘巡检
- [ ] **每周**：黄金集回归
- [ ] **每月**：漂移检测 + 报告
- [ ] **每升级**：跑全量黄金集 + 重新评估
- [ ] **事故复盘**：定位时间 < 5 分钟

---

## 4. 反模式速查（5 大问题的"最常错"）

| 问题 | 反模式 | 修复 |
|------|--------|------|
| Q1 | 所有逻辑用 LLM | 4 信号决策 |
| Q2 | 没有硬上限 | 3 道 quota 强制 |
| Q3 | raw 重试 | Self-Consistency + Judge |
| Q4 | 只一个 timeout | 双 timeout + Circuit Breaker |
| Q5 | 只监控延迟 | 4 维监控 + Trace |

---

## 5. 一句话总结（决策树精简版）

```text
Q1：思维范式 → 4 信号决策（能用规则就别用 LLM）
Q2：成本降级 → 5 层路由 + 3 道 quota（必须硬限）
Q3：一致性 → Self-Consistency + Judge + 重试预算
Q4：超时熔断 → 双 timeout + Circuit Breaker + Fallback
Q5：监控定位 → Trace + 黄金集 + 漂移（每月回归 + 实时告警）
```

---

## 6. 一句话总结

> **LLM 生产工程 = 5 个问题协同处理——任何一项薄弱都会成为事故温床。先决策、再实施、后监控，3 阶段严格遵守。**

---

← [返回: 大模型思维工程](../README.md) · 上一章：[05-monitoring](05-online-monitoring.md) · 专题结束
