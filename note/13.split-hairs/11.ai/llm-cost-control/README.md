<!--
question:
  id: 11.ai-llm-cost-control
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: AI Production Engineering
  tags: [11.ai, LLM, 成本控制, 降级, 路由, Production]
-->

# 模型调用的成本上限是多少 —— 5 层路由 + 3 道 Quota

> 一句话定位：LLM 成本必须硬上限 + 自动降级，循环 bug 会 1 小时烧 $1000。完整深度见 [主模块 · 成本控制与降级](../../../11.ai/03-engineering/llm-production-thinking/02-cost-control-and-degradation.md)。

> **系列定位**：AI 生产工程面试题（字节 / 阿里 / 美团高频）。考察的是**成本上限设计 + 5 层降级路由**能力。

---

## 引子：上线 1 周，成本从 $300/天 飙到 $12,000/天

```text
场景：某 AI 客服上线——
- Agent 循环 bug 无限调 API，token 无上限
- 没 quota 限制，1 小时烧 $4200
- 监控是事后发现，已经损失 $10,000+
```

普通候选人会答"先上线看监控再说"——踩中"**缺硬上限、缺降级、缺协同**" 3 大雷区。
高分候选人会答：**3 道 quota（防爆）+ 5 层路由（降级）+ Prometheus 告警熔断**。

---

## 一、核心原理

### 1.1 3 道 Quota（防爆）

```text
单请求：4000 输入 / 2000 输出 / $0.05
单用户：$10/天 / $200/月
单租户：$1000/天 / 并发 100
```

### 1.2 5 层路由（降级）

```text
Layer 1：缓存 + 规则（5ms）—— 80% 请求，$0
   ↓ 未命中
Layer 2：Cheap 小模型（200ms，$0.0001）—— 15%
   ↓ 复杂
Layer 3：Big 模型（1s，$0.01）—— 4%
   ↓ 仍失败
Layer 4：SaaS API fallback（3s，$0.05）—— 1%
   ↓ 仍失败
Layer 5：人工兜底 —— 0.X%
```

---

## 二、面试话术（60 秒版本）

**题目：模型调用的成本上限是多少？超了如何自动降级？**

**高分答案**（60 秒）：

```text
"LLM 成本必须硬上限 + 自动降级，3 道 quota + 5 层路由：

3 道 quota（防爆）：
- 单请求：4000 输入 / 2000 输出 / $0.05
- 单用户：$10/天 / $200/月
- 单租户：$1000/天 / 并发 100

5 层路由（降级）：
- Layer 1 缓存 + 规则：$0, 5ms
- Layer 2 Cheap 小模型：$0.0001, 200ms（80%）
- Layer 3 Big 模型：$0.01, 1s（4%）
- Layer 4 SaaS API fallback：$0.05, 3s（1%）
- Layer 5 人工兜底

实时监控 + Prometheus 告警：95% 阈值时熔断，
P99 单请求 $0.05 触发降级。"

反问：贵司是 B2C 高 QPS 还是 B2B 低 QPS？
前者必须 Layer 2 主导，后者 Layer 3 足够。"
```

---

## 三、常见陷阱

### 陷阱：成本爆炸（无硬上限）

- **错误**：所有调用不加 quota，"看监控再说"
- **真相**：监控是事后，循环 bug 会 1 小时烧 $1000
- **代价**：上线即事故，日烧 $4200+

---

## 四、相关章节

- [主模块 · 成本控制与降级](../../../11.ai/03-engineering/llm-production-thinking/02-cost-control-and-degradation.md) —— 深度内容
- [主模块 · llm-production-thinking 总目录](../../../11.ai/03-engineering/llm-production-thinking/README.md)
- [主模块 · 决策树](../../../11.ai/03-engineering/llm-production-thinking/06-decision-tree.md)
- [11.ai · vLLM vs Ollama](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/README.md) —— 推理引擎选型（成本相关）

---

> 📅 2026-07-26 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 成本控制 · 含 60 秒话术 + 反模式

← [返回: 咬文嚼字 · 11.ai](../README.md)
