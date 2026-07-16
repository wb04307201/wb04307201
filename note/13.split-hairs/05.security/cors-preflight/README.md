<!--
question:
  id: 05.security-cors-preflight
  topic: 05.security
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 性能对比
  tags: [05.security, CORS, Preflight, OPTIONS, Access-Control, 跨域]
-->

# CORS 预检请求的性能陷阱怎么解？—— Simple Request 与 Preflight 的 RTT 优化

> 一句话定位：跨域"非简单请求"会触发 **OPTIONS 预检请求**，额外增加一个 RTT——通过构造 Simple Request 或缓存 Preflight 可消除。完整 Web 安全见 [主模块 Web 安全](../../../04.system-design/05-security/web-security/README.md)。

> **系列定位**：前端 + 后端交叉面试题（中高频）。考察 **Simple Request 触发条件** + **Preflight 缓存策略** + **如何避免不必要的预检**。

---

## 引子：API 响应时间从 100ms 变成 300ms 的隐形杀手

```text
性能对比（前端 http://app.example.com → 后端 http://api.example.com）：
- 同域请求：100ms（1 次请求）
- 跨域 Simple Request：110ms（1 次请求 + CORS 头校验）
- 跨域 + Preflight：310ms（OPTIONS 200ms + 实际请求 100ms）
- 跨域 + Preflight + 未缓存：每次都是 310ms！
```

**反直觉**：CORS 不是服务端"拦截"，而是**浏览器端的安全策略**；加了自定义 Header（如 `X-Auth-Token`）或 `Content-Type: application/json` 都会触发 Preflight。

---

## 一、核心原理

| 维度 | Simple Request | Preflighted Request |
|------|---------------|-------------------|
| HTTP 方法 | 仅 GET / HEAD / POST | PUT / DELETE / PATCH 等 |
| Content-Type | text/plain / form-data / urlencoded | application/json 等 |
| 自定义 Header | 不允许 | 允许（但触发 Preflight） |
| 额外请求 | **无** | 1 次 OPTIONS |

**Simple Request 3 条件**（同时满足）：① GET/HEAD/POST ② Content-Type 为 text/plain / form-data / urlencoded ③ 无自定义 Header（注意 Authorization 头也触发 Preflight）。违反任一条件 → Preflight。

**Preflight 流程**：浏览器先发 OPTIONS 请求（带 Origin + Request-Method + Request-Headers）→ 服务端返回 Allow-Origin/Methods/Headers + Max-Age → 通过后发实际请求。

---

## 二、代码示例

```java
// Spring Boot CORS 配置
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://app.example.com")
            .allowedMethods("GET", "POST", "PUT", "DELETE")
            .allowedHeaders("X-Auth-Token", "Content-Type")
            .maxAge(86400); // Preflight 缓存 24 小时
    }
}
```

```javascript
// ❌ 触发 Preflight（application/json）
fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });

// ✅ 避免 Preflight（text/plain，服务端解析 JSON）
fetch(url, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify(data) });
```

---

## 三、常见陷阱

- **`Authorization` 头触发 Preflight**：即使 GET 也会触发 → Token 改用 Cookie（SameSite=Lax）
- **`maxAge` 设太小**：默认 5 秒，每次多一次 OPTIONS → 设 86400（Chrome 最大 2 小时）
- **`allowedOrigins("*")` 搭配 `allowCredentials`**：规范禁止 → 明确列出 Origin
- **Preflight 缓存不生效**：URL 或 Header 变化导致缓存失效 → 减少 URL 参数变化

---

## 四、最佳实践

```
消除 Preflight 的 3 种策略：
① 构造 Simple Request：GET/POST + text/plain + 无自定义 Header
② 最大化 Preflight 缓存：Access-Control-Max-Age: 86400
③ 同域部署：前后端同域或反向代理统一域名

性能影响：
  同域 → 0 额外延迟
  跨域 Simple → ~0ms
  跨域 Preflight（未缓存） → +1 RTT
  跨域 Preflight（已缓存） → 0ms

监控目标：OPTIONS 请求占总请求 < 5%
```

---

## 五、面试话术（90 秒版本）

> "CORS 预检是浏览器对跨域非简单请求自动发送的 OPTIONS 请求，每次额外消耗一个 RTT。Simple Request 不触发预检，条件是 GET/HEAD/POST + 标准 Content-Type + 无自定义 Header。
>
> 消除预检的 3 种策略：第一，构造 Simple Request，用 text/plain 替代 application/json；第二，设置 Access-Control-Max-Age 缓存预检结果，Chrome 最大支持 2 小时；第三，前后端同域部署。
>
> 常见坑：Authorization 头会触发预检即使 GET 也如此；allowedOrigins 不能用通配符搭配 credentials；预检缓存按 URL + Method + Header 组合独立存储，URL 参数变化会失效。"

---

## 六、交叉引用

- [HTTPS 握手性能优化](../https-handshake/README.md) — 另一个 RTT 优化维度
- [XSS、CSRF、CSP 三件套](../xss-csrf-csp/README.md) — CORS 与 CSRF 的关系
- [令牌桶 vs 漏桶](../rate-limiting-algorithms/README.md) — API 网关性能优化
- [主模块 04.system-design/05-security](../../../04.system-design/05-security/README.md) — 安全知识体系

---

← [返回: 咬文嚼字 · 安全](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 05.security · ⭐⭐⭐⭐
