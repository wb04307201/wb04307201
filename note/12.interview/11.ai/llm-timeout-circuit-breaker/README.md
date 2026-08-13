<!--
question:
  id: 11.ai-llm-timeout-circuit-breaker
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: AI Production Engineering
  tags: [11.ai, LLM, 超时, 熔断, Circuit Breaker, Fallback, Production]
-->

# 等不及模型思考 —— 双 Timeout + Circuit Breaker 熔断

> 一句话定位：单 timeout 一刀切让用户体验崩塌，必须双 timeout + 熔断器 + Fallback 链。完整深度见 [主模块 · 超时熔断](../../../../note/11.ai/08-llmops/production-stability/04-timeout-and-circuit-breaker.md)。

> **系列定位**：AI 生产工程面试题（字节 / 美团高频）。考察的是**可用性工程**：双 timeout + Circuit Breaker + Fallback 模型链的协同。

---

## 引子：供应商短暂故障 30 分钟，APP 完全卡死

```text
场景：某 AI 公司供应商 OpenAI 故障 30 分钟——
- 每个请求卡 60 秒（单 timeout 一刀切）
- 没有熔断，所有请求排队等超时
- APP 完全不可用，用户流失率暴涨
- CTO：限你 2 天加上熔断机制
```

普通候选人会答"超时后重试 5 次"——踩中"**单 timeout、超时重试、无熔断**" 3 大雷区。
高分候选人会答：**双 timeout（软限 + 硬限）+ Circuit Breaker + Fallback 模型链**。

---

## 一、核心原理

### 1.1 熔断 3 道防线

```text
[客户端] loading state（5s 用户能看到的）
   ↓
[Edge Timeout] CDN/网关层 5s 截断
   ↓
[服务端双 Timeout] 5s 软限 partial + 30s 硬限 fallback
   ↓
[Circuit Breaker] 错误率 > 50% 熔断 30s
   ↓
[Fallback 模型链] 切换 secondary/tertiary/SaaS
   ↓
[静态兜底] "请稍后重试" + 转人工
```

### 1.2 双 Timeout 策略

| Timeout 类型 | 时间 | 行为 |
|-------------|------|------|
| 软限 | 5s | 开始响应就 partial 推给前端（流式） |
| 硬限 | 30s | 兜底 fallback（直接返回"请稍后重试"） |

### 1.3 Circuit Breaker 状态机

```text
Closed（正常）→ 错误率 > 50% → Open（熔断 30s）
  ↓
Half-Open 探针：成功 50% → Closed（恢复）
```

---

## 二、面试话术（60 秒版本）

**题目：等不及模型思考，系统有没有超时熔断？**

**高分答案**（60 秒）：

```text
"必须有三层超时熔断：

1. 双 Timeout：
   - 软 5s：开始响应就 partial 推给前端（流式）
   - 硬 30s：兜底 fallback（直接返回"请稍后重试"）

2. Circuit Breaker（熔断器）：
   - 错误率 > 50% 熔断 30s
   - Half-Open 探针：成功 50% 后恢复
   - 避免雪崩

3. Fallback 模型链：
   - primary（GPT-4o）→ secondary（Claude）→ tertiary（开源）→ static FAQ
   - 多供应商 + SaaS 兜底

反模式：
- 只一个 timeout → 切
- 超时后重试 5 次 → 错（不要重试，fallback）
- 没有熔断 → 一旦故障全挂
- 只有 1 个供应商 → 必须多供应商"
```

---

## 三、常见陷阱

### 陷阱：单 timeout

- **错误**：timeout=30s 一刀切
- **真相**：长等待让用户体验崩塌
- **代价**：用户流失，APP 卡死

---

## 四、相关章节

- [主模块 · 超时熔断](../../../../note/11.ai/08-llmops/production-stability/04-timeout-and-circuit-breaker.md) —— 深度内容
- [主模块 · llm-production-thinking 总目录](../../../../note/11.ai/08-llmops/production-stability/README.md)
- [主模块 · 决策树](../../../../note/11.ai/08-llmops/production-stability/06-decision-tree.md)

---

> 📅 2026-07-26 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 超时熔断 · 含 60 秒话术 + 反模式

← [返回: 咬文嚼字 · 11.ai](../README.md)
