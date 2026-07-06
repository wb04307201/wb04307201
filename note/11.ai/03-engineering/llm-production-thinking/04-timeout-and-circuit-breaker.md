<!--
module:
  parent: ai/llm-production-thinking
  slug: ai/llm-production-thinking/04-timeout-and-circuit-breaker
  type: topic
  category: 超时熔断
  summary: 双 timeout + Circuit Breaker + Fallback 模型 + Hystrix 模式应用到 LLM 场景
-->

# 超时熔断 · 双 timeout + Circuit Breaker

> **一句话**：LLM 不可用时不能让整个系统崩——**双 timeout（5s 软限 + 30s 硬限）+ Circuit Breaker + Fallback 模型**三道防线，保系统可用性。

← [返回: 大模型思维工程](../README.md)

---

## 1. 为什么 LLM 必须有熔断？

**真实事故**：
- 2024 Q2 某 AI 公司接入某大模型 API，对方短暂故障（30 分钟）
- 失败模式：每个请求都卡 60 秒然后超时
- 用户体验：APP 完全卡死
- 损失：DAU 跌 40%，3 天恢复

**根因**：没有超时熔断，LLM 故障时整个调用链阻塞

---

## 2. 双 Timeout 设计

### 2.1 软超时（5s）+ 硬超时（30s）

```python
async def invoke_with_dual_timeout(prompt, soft=5, hard=30):
    try:
        # 硬超时兜底
        return await asyncio.wait_for(
            _invoke_with_progress_check(prompt, soft),
            timeout=hard
        )
    except asyncio.TimeoutError:
        # 硬超时触发
        log(f"hard timeout: {prompt[:50]}")
        return fallback_response()
```

### 2.2 软超时：渐进反馈

```python
async def _invoke_with_progress_check(prompt, soft_timeout):
    """软超时：开始收到 partial 响应就继续等"""
    start = time.time()
    # 触发软超时 → 发 partial 响应给前端（流式）
    while time.time() - start < soft_timeout:
        partial = await stream.next()
        if partial:
            send_to_user(partial)
            return partial
    return None  # 软超时未达成 → 走硬超时
```

**效果**：用户看到"AI 正在思考..."，然后 partial 响应，避免完全空白

### 2.3 硬超时：兜底 fallback

```python
FALLBACK_RESPONSES = {
    "timeout": "抱歉，AI 响应超时。请稍后重试或转人工客服。",
    "rate_limit": "系统繁忙，请 30 秒后重试。",
    "service_unavailable": "服务维护中，请稍后重试。",
}

def fallback_response(error_type="timeout"):
    return FALLBACK_RESPONSES[error_type]
```

---

## 3. Circuit Breaker（熔断器）

### 3.1 状态机

```
Closed ──── 错误率 > 阈值 ────→ Open
   ↑                              │
   │                              │ 30 秒冷却
   ↓                              ↓
Half-Open ──── 探测成功 ────→ Closed
   └────── 探测失败 ────→ Open
```

### 3.2 Netflix Hystrix 模式应用到 LLM

```python
class LLMCircuitBreaker:
    def __init__(self, model):
        self.model = model
        self.failure_count = 0
        self.success_count = 0
        self.state = "closed"  # closed / open / half-open
        self.failure_threshold = 5
        self.cooldown_seconds = 30
    
    async def invoke(self, prompt):
        if self.state == "open":
            if time.time() - self.opened_at < self.cooldown_seconds:
                raise CircuitOpenError("circuit is open")
            else:
                self.state = "half-open"
        
        try:
            result = await invoke_with_dual_timeout(prompt)
            self.on_success()
            return result
        except (Timeout, ServiceUnavailable) as e:
            self.on_failure()
            raise
    
    def on_success(self):
        self.success_count += 1
        if self.state == "half-open":
            self.state = "closed"
            self.failure_count = 0
    
    def on_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            self.opened_at = time.time()
```

### 3.3 Fallback 模型切换

```python
class FallbackChain:
    def __init__(self):
        self.primary = "gpt-4o"
        self.secondary = "claude-3.5-sonnet"
        self.tertiary = "llama-3-70b-local"
        self.final = "static_faq"
    
    async def invoke(self, prompt):
        for model in [self.primary, self.secondary, self.tertiary, self.final]:
            try:
                result = await invoke_with_timeout(model, prompt, soft=5, hard=30)
                log(f"success: {model}")
                return result
            except (Timeout, CircuitOpen) as e:
                log(f"{model} failed: {e}")
                continue
        return self.static_fallback(prompt)
```

---

## 4. 三层防御

```
[Layer 1] 客户端：loading state + cancel button（5s 用户能看到的）
   ↓
[Layer 2] Edge timeout：CDN/网关层 5s 截断
   ↓
[Layer 3] 服务端双 timeout：5s 软限（partial）+ 30s 硬限
   ↓
[Layer 4] Circuit Breaker：错误率超阈值熔断 30s
   ↓
[Layer 5] Fallback 模型：切换到 secondary/tertiary
   ↓
[Layer 6] 静态兜底：返回"请稍后重试"+ 转人工
```

---

## 5. 超时熔断 vs 重试：协同

```
请求触发：
  ↓
[Circuit] Open? → Yes → 直接 Fallback（不重试）
  ↓ No
[Invoke] → [Timeout?]
  ↓ No      ↓ Yes
  ↓     [Retry 可?]
  ↓         ↓ No → Fallback
  ↓         ↓ Yes
[Return]  [Backoff Retry]
            ↓
        [Retry 多次仍失败?]
            ↓ Yes → Open Circuit
```

**反直觉**：Circuit Open 时不重试——重试会加重负担，加速雪崩。

---

## 6. 监控指标

| 指标 | 公式 | 阈值 |
|------|------|------|
| **P50/P99 响应时间** | percentile(latency) | P99 < 10s |
| **超时率** | timeout_count / total | < 1% |
| **熔断次数** | circuit_open_count | 0 (正常) |
| **降级率** | fallback_count / total | < 5% |
| **Soft timeout rate** | partial_response_count / total | < 10% |

---

## 7. 反模式 · 5 个常见错

### ⚠️ 反模式 1：只设一个 timeout

- 错：timeout=30s 一刀切
- 对：双 timeout（5s 软 + 30s 硬）

### ⚠️ 反模式 2：超时后重试 5 次

- 错：timeout × 5 = 150s 用户空白
- 对：timeout 后**立即降级**（不重试）

### ⚠️ 反模式 3：没有熔断

- 错：错误率 80% 仍继续调用，把上游打死
- 对：错误率 > 50% 熔断 30 秒

### ⚠️ 反模式 4：没有 fallback 模型

- 错：唯一供应商挂了 → 100% 失败
- 对：至少 2 个供应商 + SaaS 兜底

### ⚠️ 反模式 5：熔断后立即恢复

- 错：熔断 1 秒又尝试
- 对：熔断 30 秒冷却 + 探针测试

---

## 8. 一句话总结

> **LLM 超时熔断 = 双 timeout（5s 软限 partial + 30s 硬限 fallback）+ Circuit Breaker（熔断 + 探针）+ Fallback 模型链。事故复盘的根因 80% 都是"没熔断"。**

---

← [返回: 大模型思维工程](../README.md) · 上一章：[03-consistency](03-consistency-and-failure-handling.md) · 下一章：[05-monitoring](05-online-monitoring.md)
