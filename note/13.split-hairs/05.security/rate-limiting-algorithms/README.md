<!--
question:
  id: 05.security-rate-limiting-algorithms
  topic: 05.security
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [05.security, 限流, 令牌桶, 漏桶, 滑动窗口, 固定窗口]
-->

# 令牌桶 vs 漏桶 vs 滑动窗口怎么选？—— 4 大限流算法对比

> 一句话定位：**令牌桶允许突发**，**漏桶强制平滑**，**滑动窗口精确计数**，**固定窗口最简单但有边界问题**。完整 API 安全见 [主模块 API 安全](../../../04.system-design/05-security/api-security/README.md)。

> **系列定位**：经典系统设计面试题（高频）。考察 **4 种算法适用场景** + **Redis 分布式实现** + **边界条件处理**。

---

## 引子：秒杀系统被刷爆的 3 种死法

```text
某电商秒杀，预期 1 万 QPS，实际涌入 50 万——
固定窗口：第 59 秒涌入 2 万 + 第 0 秒又涌入 2 万 → 瞬间 4 万击穿（边界突刺）
漏桶：强制 1 万 QPS 匀速 → 用户排队 50 秒 → 90% 超时放弃
令牌桶：允许突发 3 万（桶容量）→ 系统扛住 → 桶空后降为 1 万 QPS
```

**反直觉**：固定窗口两个窗口交界处可承受 **2 倍限流阈值**；漏桶看似公平但突发时**所有用户都慢**。

---

## 一、核心原理

| 算法 | 突发流量 | 复杂度 | 精度 | 适用场景 |
|------|---------|--------|------|---------|
| **固定窗口** | ❌ 边界 2 倍突刺 | 低 | 窗口级 | 简单场景 |
| **滑动窗口** | ⚠️ 窗口内突发 | 中 | 亚秒级 | API 限流（主流） |
| **漏桶** | ❌ 强制匀速 | 中 | 精确 | 消息队列 / 流量整形 |
| **令牌桶** | ✅ 允许突发 | 中 | 精确 | Web API / 秒杀（推荐） |

**固定窗口**：按时间窗口计数，到阈值拒绝。问题：窗口末尾 + 下一窗口开头 = 瞬间突刺。

**滑动窗口**：细分为多个子窗口（如 1 秒分 10 个 100ms），滑动计算总和。消除边界突刺。

**漏桶**：请求进入队列，以固定速率流出。满了就拒绝。无论进入多快，出口恒定。

**令牌桶**：以固定速率生成令牌，请求消耗令牌。桶满时令牌丢弃，桶空时请求被拒。**允许突发**（桶里积累的令牌可一次性消耗）。

---

## 二、代码示例

```java
// Guava RateLimiter（令牌桶）
RateLimiter limiter = RateLimiter.create(100.0); // 每秒 100 个令牌

// 阻塞等待
limiter.acquire();

// 非阻塞
if (limiter.tryAcquire()) {
    return processRequest();
}
throw new RateLimitException("请求被限流");
```

```lua
-- Redis 滑动窗口（Lua 保证原子性）
-- KEYS[1]=限流key, ARGV[1]=窗口ms, ARGV[2]=最大请求数
local key, window, limit = KEYS[1], tonumber(ARGV[1]), tonumber(ARGV[2])
local now = tonumber(redis.call('TIME')[1]) * 1000
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)
if count < limit then
    redis.call('ZADD', key, now, now .. math.random())
    redis.call('PEXPIRE', key, window)
    return 0  -- 允许
end
return 1  -- 拒绝
```

---

## 三、常见陷阱

- **固定窗口边界突刺**：两窗口交界处可承受 2 倍阈值 → 改用滑动窗口或令牌桶
- **分布式限流不考虑 Redis 延迟**：每次查 Redis RTT 5ms × 10 万 QPS → 本地预分配 + Redis 定期同步
- **漏桶用于用户请求**：强制匀速致所有用户排队 → 用户请求用令牌桶，消息队列用漏桶
- **限流 Key 粒度太粗**：全局限流 → 一个用户刷接口影响所有人 → 按 user_id / IP / API 分别限流

---

## 四、最佳实践

```text
选型决策树：
  需要精确控制速率？
  ├─ 是 → 允许突发？ → 是 → 令牌桶（Web API / 秒杀）
  │                    → 否 → 漏桶（消息队列）
  └─ 否 → 需要高精度？ → 是 → 滑动窗口（API 网关）
                        → 否 → 固定窗口（日志统计）

分布式限流架构：
  层 1：本地限流（Guava RateLimiter，单机保护）
  层 2：集群限流（Redis + Lua，全局 QPS 控制）

限流响应规范：429 Too Many Requests + Retry-After + X-RateLimit-*
```

---

## 五、面试话术（90 秒版本）

> "限流有 4 种经典算法。固定窗口按时间窗口计数，但有边界突刺——两窗口交界处可承受 2 倍阈值。滑动窗口细分为多个子窗口，消除边界问题，是 API 网关主流。漏桶强制请求以固定速率流出，适合消息队列流量整形。令牌桶以固定速率生成令牌，允许突发消耗积累令牌，是 Web API 和秒杀首选——Guava RateLimiter 就是令牌桶实现。
>
> 分布式限流用 Redis + Lua 保证原子性，大规模场景用二级限流：本地 Guava 预分配 + Redis 全局同步。限流维度要细：按 user_id、IP、API 分别限流。"

---

## 六、交叉引用

- [CORS 预检请求优化](../cors-preflight/README.md) — API 网关性能优化
- [HTTPS 握手性能优化](../https-handshake/README.md) — 连接层性能优化
- [OWASP Top 10](../owasp-top10/README.md) — API 安全与限流
- [统一权限控制系统](../access-control-design/README.md) — 权限维度的访问控制
- [主模块 04.system-design/05-security](../../../04.system-design/05-security/README.md) — 安全知识体系

---

← [返回: 咬文嚼字 · 安全](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 05.security · ⭐⭐⭐⭐
