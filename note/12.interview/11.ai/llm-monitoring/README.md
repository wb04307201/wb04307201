<!--
question:
  id: 11.ai-llm-monitoring
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: AI Production Engineering
  tags: [11.ai, LLM, 监控, Trace, 漂移检测, 黄金集, Production]
-->

# 上线后怎么检测准确率与幻觉率 —— Trace + 4 维监控 + 漂移检测

> 一句话定位：只监控 HTTP 200 + latency 是不够的——质量掉到 70% 用户狂喷。完整深度见 [主模块 · 线上监控与定位](../../../../agent/production-stability/05-online-monitoring.md)。

> **系列定位**：AI 生产工程面试题（Anthropic / Google 高频）。考察的是**可观测性工程**：4 维指标 + Trace 链路 + 黄金集回归 + 漂移检测。

---

## 引子：上游静默升级，用户狂喷"AI 变笨了"

```text
场景：某 AI 公司上游 GPT-4o 静默升级——
- 准确率从 92% 掉到 70%，但 HTTP 200 率 100%
- latency 也正常，监控没告警
- 用户投诉不断，7 天才发现原因
- CTO：限你 3 天建立完整监控体系
```

普通候选人会答"监控 HTTP 200 + latency 就够了"——踩中"**监控盲区、缺 Trace、缺黄金集回归**" 3 大雷区。
高分候选人会答：**4 维指标 + Trace（5 分钟定位）+ 黄金集回归 + 漂移检测**。

---

## 一、核心原理

### 1.1 4 维监控体系

| 维度 | 指标 | 频率 |
|------|------|------|
| 延迟 | P50/P95/P99 latency | 实时 |
| 成本 | 单请求 / 日累计 | 实时 |
| 质量 | 准确率 / 幻觉率 | 5 分钟 batch |
| 一致性 | 重复问题答案漂移率 | 1 小时 |

### 1.2 5 分钟定位实战

```text
1. 看监控大盘（30s）
2. 查 Trace 抽样 5 个失败请求（1 分钟）
3. 比对黄金集（2 分钟）
4. 定位根因：RAG 召回错 / Prompt 漂移 / 模型升级 / 数据过期（5 分钟）
```

### 1.3 黄金集回归

- **规模**：50-200 题人工标注
- **频率**：每月回归 / 每次模型升级跑全量
- **阈值**：准确率跌破 85% 告警

### 1.4 漂移检测

- Embedding 分布（KS 检验）
- Prompt 模板响应漂移
- 召回率变化

---

## 二、面试话术（60 秒版本）

**题目：上线后怎么检测准确率 / 幻觉率？怎么快速定位问题？**

**高分答案**（60 秒）：

```text
"4 维监控体系 + Trace + 黄金集回归。

4 维指标：
- 延迟：P50/P95/P99 latency（实时）
- 成本：单请求 / 日累计（实时）
- 质量：准确率 / 幻觉率（5 分钟 batch）
- 一致性：重复问题答案漂移率（1 小时）

黄金集（50-200 题人工标注）：
- 每月回归
- 每次模型升级跑全量
- 准确率跌破 85% 告警

漂移检测：
- Embedding 分布（KS 检验）
- Prompt 模板响应
- 召回率变化

5 分钟定位实战：
1. 看监控大盘（30s）
2. 查 Trace 抽样 5 个失败请求（1 分钟）
3. 比对黄金集（2 分钟）
4. 定位根因：RAG 召回错 / Prompt 漂移 / 模型升级 / 数据过期（5 分钟）

工具：Langfuse / Helicone / Phoenix

反模式：
- 只监控 HTTP 200 + latency（缺质量 + 成本 + 一致性）
- 上线后没 Trace（定位 3 天 vs 5 分钟）
- 黄金集跑一次（每次升级都应回归）
- 漂移检测从未设置（事故等到才发现）"
```

---

## 三、常见陷阱

### 陷阱：监控盲区（只盯延迟）

- **错误**：监控 HTTP 200 + latency 就够了
- **真相**：质量掉到 70%，用户以为是 AI 进步
- **代价**：3 个月才发现，损失 50% 用户

---

## 四、相关章节

- [主模块 · 线上监控与定位](../../../../agent/production-stability/05-online-monitoring.md) —— 深度内容
- [主模块 · llm-production-thinking 总目录](../../../../09.ai-applications/agent/production-stability/README.md)
- [主模块 · 决策树](../../../../09.ai-applications/agent/production-stability/06-decision-tree.md)
- [12.story · 05-observability](../../../13.story/05-observability.md) —— 阿明餐厅的可观测性实战

---

> 📅 2026-07-26 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 4 维监控 + Trace · 含 60 秒话术 + 反模式

← [返回: 咬文嚼字 · 11.ai](../README.md)
