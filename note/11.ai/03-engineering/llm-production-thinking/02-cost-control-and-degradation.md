<!--
module:
  parent: ai/llm-production-thinking
  slug: ai/llm-production-thinking/02-cost-control-and-degradation
  type: topic
  category: 成本控制
  summary: 5 层路由降级策略 + 硬成本上限 + 单请求 quota + 实时成本监控 + 反模式
-->

# 成本上限与自动降级 · 5 层路由

> **一句话**：LLM 成本像电费——**没硬上限一定爆**。用「5 层路由」（cheap 模型 → small 模型 → big 模型 → SaaS → 人工）+ 单请求 quota + 实时告警，三道防线保成本可控。

← [返回: 大模型思维工程](../README.md)

---

## 1. 为什么必须有硬成本上限？

**真实事故**：
- 2024 Q1，某 SaaS 公司大模型 Agent 上线后被刷，全天上 $12,000（预期 $300）
- 根因：循环 bug 让 Agent 无限调 API，token 累计无上限
- 修复：单请求 + 单用户 + 单租户 3 道 quota + 自动熔断

**成本爆炸 5 大常见原因**：
1. 循环调用（Agent 死循环）
2. Prompt 暴涨（误把 100k 文档塞进 prompt）
3. 多路并发（每个 query 调 5 个模型）
4. 用户滥用（被机器人刷）
5. 上游涨价（GPT-4o 涨价 30%）

---

## 2. 5 层路由降级策略

```
请求进来 ↓
   ↓
[Layer 1] 规则+缓存（5ms）—— 命中走 cached_answer
   ↓ 未命中
[Layer 2] Cheap 小模型（200ms，$0.0001/次）—— 处理 70% 简单请求
   ↓ 复杂 / 超阈值
[Layer 3] Big 模型（1s，$0.01/次）—— 处理 25% 中等请求
   ↓ 仍失败 / 超时
[Layer 4] SaaS API（3s，$0.05/次）—— 处理 4% 兜底
   ↓ 仍失败
[Layer 5] Human Handoff —— 1% 转人工
```

### 2.1 Layer 1：缓存 + 规则（90% ROI）

```python
def layer1(query):
    # 缓存（Redis 语义）
    cached = semantic_cache.get(query, threshold=0.95)
    if cached:
        return cached
    
    # 规则高频意图
    rule_result = rule_engine.match(query)
    if rule_result and rule_result.confidence > 0.9:
        return rule_result.answer
    
    return None  # 继续下一层
```

**成本**：$0
**延迟**：5-10ms

### 2.2 Layer 2：Cheap 小模型

```python
def layer2(query, complexity_classifier):
    if complexity_classifier(query) == "simple":
        # 用 7B-INT4 / Claude 3.5 Haiku
        return small_llm.invoke(query, timeout=2)
    return None
```

**成本**：$0.0001/次
**延迟**：200-500ms
**准确率**：85%（简单任务足够）

### 2.3 Layer 3：Big 模型

```python
def layer3(query):
    if complexity_classifier(query) in ["medium", "hard"]:
        return big_llm.invoke(query, timeout=10)
    return None
```

**成本**：$0.01-0.05/次
**延迟**：1-5s
**准确率**：95%+

### 2.4 Layer 4：SaaS 兜底（多供应商）

```python
def layer4(query):
    providers = [
        ("openai", lambda: openai.chat(query)),
        ("anthropic", lambda: anthropic.chat(query)),
    ]
    for name, fn in providers:
        try:
            return fn()
        except (RateLimit, Timeout, Error):
            continue
    return None
```

**成本**：$0.05-0.5/次
**延迟**：3-10s
**优点**：供应商故障不影响

### 2.5 Layer 5：人工介入

```python
def layer5(query):
    return {
        "status": "human_handoff",
        "queue": "ai-fallback",
        "sla": "5 分钟内人工接入",
        "user_msg": "您的问题较为复杂，正在转接人工客服...",
    }
```

**适用**：金融 / 医疗 / 法律高风险

---

## 3. 硬成本上限（3 道 quota）

### 3.1 单请求 quota

```python
@quota(max_input_tokens=4000, max_output_tokens=2000, max_total_cost=0.05)
def invoke_llm(prompt):
    return llm.invoke(prompt)
```

**触发**：token 超额 → 自动 truncate；总成本 > 上限 → 抛 QuotaExceededError

### 3.2 单用户/单租户 quota

```python
# 每日配额（按用户）
user_quota = UserQuota(
    daily_cost_limit=10.0,    # $10/day
    monthly_cost_limit=200,   # $200/month
    per_request_timeout=30,
)

# 触发限流后降级
def invoke_with_user_quota(user_id, prompt):
    if user_quota.exceeded(user_id):
        return layer4_saas(prompt)  # 降级到 SaaS（更便宜）
    if user_quota.near_limit(user_id, threshold=0.8):
        # 80% 阈值告警
        log_warning("user near cost limit", user_id)
    return big_llm.invoke(prompt)
```

### 3.3 单租户全局 quota

```python
# 租户级每日配额（防刷）
tenant_quota = TenantQuota(
    daily_cost_limit=1000.0,    # $1000/day per tenant
    concurrent_limit=100,        # 同时最大 100 请求
    burst_rate_limit=10,         # 每秒最多 10 个
)
```

---

## 4. 实时成本监控 + 告警

### 4.1 必监控指标

| 指标 | 公式 | 阈值 |
|------|------|------|
| **P50 单请求成本** | median(request_cost) | ≤ $0.005 |
| **P99 单请求成本** | max(request_cost) | ≤ $0.05 |
| **日累计成本** | sum(today_cost) | ≤ quota × 0.8 |
| **成本率** | cost / revenue | ≤ 5% |
| **缓存命中率** | cache_hit / total_requests | ≥ 30% |
| **降级触发率** | degradation_trigger / total | ≤ 5% |

### 4.2 Prometheus + Grafana 部署

```yaml
# llm_cost_dashboard
panels:
  - metric: llm_request_cost_bucket
    viz: histogram
    thresholds: [0.001, 0.005, 0.01, 0.05]
  - metric: llm_daily_cost_total
    viz: timeseries
    alert: > 800  # 80% quota 时告警
  - metric: llm_cache_hit_ratio
    viz: gauge
    target: 0.3
  - metric: llm_degradation_ratio
    viz: gauge
    threshold: 0.05
```

### 4.3 自动熔断

```python
class CostCircuitBreaker:
    def __init__(self, daily_limit):
        self.daily_limit = daily_limit
        self.current = 0
    
    def should_break(self, request_cost):
        if self.current + request_cost > self.daily_limit * 0.95:
            return True  # 95% 阈值熔断
        return False
```

---

## 5. 反模式 · 5 个常见错

### ⚠️ 反模式 1：没有硬上限

- 错："看监控再说"——监控是事后
- 对：3 道 quota（请求 + 用户 + 租户）强制硬限

### ⚠️ 反模式 2：滥用 big 模型

- 错：所有请求都用 GPT-4
- 对：5 层路由，70% 用 small 模型

### ⚠️ 反模式 3：忽视缓存

- 错：每次都重调 LLM
- 对：语义缓存（阈值 0.95）+ 规则缓存

### ⚠️ 反模式 4：没有降级路径

- 错：LLM 失败 → 500 错误
- 对：Layer 4 SaaS + Layer 5 人工兜底

### ⚠️ 反模式 5：忽视间接成本

- 错：只算 token 费，忽视：
  - GPU 排队延迟（用户流失）
  - 重试放大（一次失败重试 3 次 = 3x 成本）
  - 风险成本（幻觉导致客诉赔偿）
- 对：算 TCO（总拥有成本）= 直接 + 间接

---

## 6. 一句话总结

> **LLM 成本 = 5 层路由（cache → cheap → big → SaaS → human）+ 3 道 quota（请求 + 用户 + 租户）+ 实时监控告警。忽视任何一项，一定爆。**

---

← [返回: 大模型思维工程](../README.md) · 上一章：[01-thinking-paradigm](01-thinking-paradigm.md) · 下一章：[03-consistency](03-consistency-and-failure-handling.md)
