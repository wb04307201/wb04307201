<!--
question:
  id: 05.security-xss-csrf-csp
  topic: 05.security
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 生产Bug
  tags: [05.security, XSS, CSRF, CSP, 安全头, SameSite, HttpOnly]
-->

# XSS、CSRF、CSP 三件套怎么防？—— Web 安全三道防线

> 一句话定位：XSS 是"注入恶意脚本"，CSRF 是"伪造用户请求"，CSP 是"浏览器端的脚本白名单"——三者构成**纵深防御**。完整 Web 安全见 [主模块 Web 安全](../../../04.system-design/05-security/web-security/README.md)。

> **系列定位**：经典前端 + 后端安全面试题。考察 **3 种攻击的区分** + **多层防御组合** + **CSP 策略实战配置**。

---

## 引子：一个评论区引发的连环安全事故

```text
🚨 生产事故链：
1. 用户在评论区输入 <script>fetch('/api/transfer',{method:'POST'})</script>
2. 后端未转义直接存库 → 其他用户浏览时脚本执行（存储型 XSS）
3. 脚本以受害者身份发起转账 → 后端只校验了 Cookie（CSRF 成功）
4. 管理员后台没设 CSP 头 → 攻击者加载外部脚本窃取管理员 Cookie
```

**反直觉**：HttpOnly Cookie 能防 XSS 窃取 Cookie，但**防不了 CSRF**（浏览器仍自动携带）。

---

## 一、核心原理

| 维度 | XSS | CSRF | CSP（防御） |
|------|-----|------|------------|
| 攻击目标 | 用户浏览器 | 服务端 API | N/A（防御手段） |
| 攻击本质 | 注入恶意脚本 | 伪造用户请求 | 限制脚本来源 |
| 核心防御 | 输出转义 + CSP | CSRF Token + SameSite | HTTP 响应头 |

**XSS 三种类型**：反射型（URL 参数反射到页面）、存储型（存库，所有访问者中招，最危险）、DOM 型（前端 JS 直接操作 DOM 注入，不经过服务端）。

**CSRF 原理**：受害者已登录 bank.com → 访问 evil.com → evil.com 包含 `<img src="https://bank.com/transfer?to=attacker">` → 浏览器自动带 Cookie → 服务端认为合法请求。

**CSP 示例**：`Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.example.com;` → 违反策略的脚本即使注入也不执行。

---

## 二、代码示例

```java
// XSS 防御：输出转义（Spring）
@GetMapping("/comment")
public String showComment(@RequestParam String text) {
    return "<div>" + HtmlUtils.htmlEscape(text) + "</div>";
    // < → &lt;  > → &gt;  " → &quot;
}

// CSRF 防御：Spring Security 自动启用 CSRF Token
// 表单：<input type="hidden" th:name="${_csrf.parameterName}" th:value="${_csrf.token}"/>

// CSP 配置（Spring Security）
http.headers(h -> h.contentSecurityPolicy(csp -> csp
    .policyDirectives("default-src 'self'; script-src 'self' https://cdn.example.com; report-uri /csp-report")
));
```

---

## 三、常见陷阱

- **以为 HttpOnly 能防 CSRF**：HttpOnly 阻止 JS 读 Cookie，但浏览器仍自动携带 → 必须靠 Token 或 SameSite
- **CSP 用了 `unsafe-eval` + `unsafe-inline`**：等于放弃 CSP → 改用 `nonce` 或 `hash`
- **只防 POST 不防 GET**：`<img src="/api/delete?id=1">` 用 GET 也能变更状态 → GET 不应有副作用
- **SameSite=None 不设 Secure**：Chrome 80+ 要求 SameSite=None 必须搭配 Secure

---

## 四、最佳实践

```text
纵深防御 6 层：
① 输入验证 — 白名单校验（拒绝 <script> 等）
② 输出转义 — HTML 实体编码（OWASP Java Encoder）
③ CSP 头 — 限制脚本来源 + 报告违规
④ Cookie 属性 — HttpOnly + Secure + SameSite
⑤ CSRF Token — 状态变更请求必须携带
⑥ SameSite — Strict（银行）/ Lax（大多数应用）/ None+Secure（第三方嵌入）

CSP 渐进上线：先 Report-Only 观察 → 分析违规报告 → 切 Enforcement
```

---

## 五、面试话术（90 秒版本）

> "XSS、CSRF、CSP 是 Web 安全三道防线。XSS 分反射型、存储型和 DOM 型，防御靠输出转义加 CSP 限制脚本来源。CSRF 利用用户已登录的 Cookie 伪造请求，防御靠 CSRF Token 和 SameSite Cookie。CSP 通过 HTTP 头声明允许加载资源的来源，违反策略的脚本即使注入也不执行。
>
> 三者经常联合攻击：XSS 可能被用来发起 CSRF，HttpOnly 防 XSS 窃取但防不了 CSRF，所以必须多层防御——输入验证、输出转义、CSP、Cookie 属性、CSRF Token 缺一不可。CSP 推荐先用 Report-Only 模式观察再切 Enforcement。"

---

## 六、交叉引用

- [单点登录 6 大方案](../sso/README.md) — OAuth2 中的 State 参数防 CSRF
- [JWT vs Session](../jwt-vs-session/README.md) — Cookie 安全属性配置
- [OWASP Top 10](../owasp-top10/README.md) — XSS 和注入在 OWASP 中的排名
- [主模块 04.system-design/05-security](../../../04.system-design/05-security/README.md) — 安全知识体系

---

← [返回: 咬文嚼字 · 安全](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 05.security · ⭐⭐⭐⭐
