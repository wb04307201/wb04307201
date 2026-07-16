<!--
question:
  id: 05.security-jwt-vs-session
  topic: 05.security
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [05.security, JWT, Session, Cookie, Token, 认证]
-->

# JWT vs Session 认证怎么选？—— Stateless 与 Stateful 的工程权衡

> 一句话定位：JWT 和 Session 不是"哪个更好"，而是**无状态 vs 有状态**的架构选型。完整认证理论见 [主模块 JWT 安全](../../../04.system-design/05-security/jwt-security/README.md)。

> **系列定位**：经典后端安全面试题（字节 / 阿里 / 美团高频）。考察 **Stateless vs Stateful 的架构影响** + **Token 撤销方案** + **CSRF 攻击面差异**。

---

## 引子：一次选型失误导致的全站故障

```text
某电商团队从 Session 迁移到 JWT，以为"去掉 Redis 就能提升性能"——
上线当天：用户登出后仍能下单（JWT 无法撤销）
第二周：Payload 塞了角色 + 菜单权限，Cookie 超 4KB 被截断
第三周：想强制下线某用户，发现只能"等 Token 自然过期"
```

---

## 一、核心原理

| 维度 | Session | JWT |
|------|---------|-----|
| 状态 | **有状态**（服务端存储） | **无状态**（客户端自包含） |
| 大小 | Session ID ~32 字节 | Payload 可膨胀 1-4 KB |
| 撤销 | 直接删除 Session | 需黑名单 / 短过期 + 刷新 |
| 横向扩展 | 需共享 Session Store | 天然无状态 |
| CSRF 攻击面 | Cookie 自动携带 → 高 | Authorization Header → 低 |

**Session 流程**：登录 → 服务端创建 Session 存 Redis → 返回 Set-Cookie → 后续请求带 Cookie 查 Redis。

**JWT 流程**：登录 → 服务端签发 JWT（HS256/RS256）→ 客户端存 Token → 后续请求 Authorization: Bearer 验签。

---

## 二、代码示例

```java
// Session 认证（Spring Boot）
@PostMapping("/login")
public String login(@RequestBody LoginRequest req, HttpSession session) {
    User user = authService.authenticate(req.getUsername(), req.getPassword());
    session.setAttribute("userId", user.getId());
    return "OK"; // 框架自动 Set-Cookie: JSESSIONID
}

// JWT 认证（Spring Boot）
@PostMapping("/login")
public TokenResponse login(@RequestBody LoginRequest req) {
    User user = authService.authenticate(req.getUsername(), req.getPassword());
    String token = Jwts.builder()
        .setSubject(String.valueOf(user.getId()))
        .setExpiration(new Date(System.currentTimeMillis() + 3600_000))
        .signWith(secretKey, SignatureAlgorithm.HS256).compact();
    return new TokenResponse(token);
}
```

---

## 三、常见陷阱

- **JWT Payload 过大**：菜单树塞进 JWT → Cookie 4KB 限制截断 → 只放 userId + roles
- **JWT 无法撤销**：登出后 Token 仍有效 → 需 Redis 黑名单（key = jti，TTL = 剩余有效期）
- **Session 不考虑横向扩展**：内存 Session + 加机器 → 请求漂移到新节点 → 用户"被登出"
- **JWT Secret 硬编码**：源码泄露 = 所有人可伪造 Token → 用环境变量或 Vault

---

## 四、最佳实践

```
选型决策树：
  需要服务端强制控制（踢人 / 单设备登录）？ → Session + Redis
  微服务间调用 / 移动端？ → JWT（短过期 + Refresh Token Rotate）
  传统 Web 应用？ → Session（简单可靠）

JWT 安全加固：Access Token 15-60 分钟 + Refresh Token 7 天 + Rotate + RS256
Session 安全加固：HttpOnly + Secure + SameSite=Lax + 登录成功后 regenerate ID
```

---

## 五、面试话术（90 秒版本）

> "JWT 和 Session 的核心区别是 Stateless vs Stateful。Session 在服务端存储状态，能随时撤销和强制下线，但需要 Redis 共享做横向扩展。JWT 自包含，天然支持扩展，但一旦签发无法主动撤销。
>
> 选型看场景：需要强控制选 Session + Redis；微服务和移动端选 JWT + 短过期 + Refresh Rotate。常见坑有 3 个：JWT Payload 超 4KB、无撤销机制致被盗 Token 持续有效、Session 没做 Redis 共享致扩容后掉登录态。两者都要防 CSRF——Session 用 SameSite + CSRF Token，JWT 用 Authorization Header 传递。"

---

## 六、交叉引用

- [单点登录 6 大方案](../sso/README.md) — JWT 在 SSO 中的定位
- [统一权限控制系统](../access-control-design/README.md) — RBAC + ABAC 与认证的关系
- [XSS、CSRF、CSP 三件套](../xss-csrf-csp/README.md) — Cookie 安全详解
- [主模块 JWT 安全](../../../04.system-design/05-security/jwt-security/README.md) — JWT 签发与验证全流程

---

← [返回: 咬文嚼字 · 安全](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 05.security · ⭐⭐⭐⭐
