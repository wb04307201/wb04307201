<!--
module:
  parent: split-hairs
  slug: 05.security
  type: article
  category: 高频面试题
  summary: 安全设计高频面试题与难点深挖（认证 / 加密 / Web 安全 / 限流 / OWASP）
question:
  id: 05.security-05.security
  topic: 05.security
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [05.security, RBAC, ABAC, SSO, OAuth2, JWT, Spring-Security, XSS, CSRF, TLS, 限流, OWASP]
-->

# 安全咬文嚼字

> 安全设计高频面试题与难点深挖（**认证 / 加密 / Web 安全 / 限流 / OWASP**），对齐主模块 [`04.system-design/05-security`](../../04.system-design/05-security/)。**10** 篇真题覆盖**权限系统设计** + **单点登录 6 方案** + **JWT vs Session** + **OAuth2 四种模式** + **XSS/CSRF/CSP** + **HTTPS 握手优化** + **传输 vs 存储加密** + **CORS 预检优化** + **限流算法选型** + **OWASP Top 10** 10 大方向。

---

## 文章清单（共 10 题，2026-07-16 更新）

### 认证与授权

| 主题 | 核心问题 |
|------|---------|
| [设计统一权限控制系统](access-control-design/README.md) | RBAC + ABAC + 缓存 + 审计 + 多租户隔离 |
| [单点登录 SSO 6 大方案](sso/README.md) | Cookie 共享 / CAS / OAuth2+OIDC / SAML / JWT / 代理 |
| [JWT vs Session 认证怎么选](jwt-vs-session/README.md) | Stateless vs Stateful + 撤销 + CSRF 攻击面 |
| [OAuth2 四种授权模式](oauth2-flow/README.md) | Authorization Code / PKCE / Client Credentials / Implicit |

### Web 安全与加密

| 主题 | 核心问题 |
|------|---------|
| [XSS、CSRF、CSP 三件套怎么防](xss-csrf-csp/README.md) | 3 种攻击 + 纵深防御 6 层 + CSP 策略 |
| [HTTPS 握手性能优化](https-handshake/README.md) | TLS 1.2 vs 1.3 + 0-RTT + OCSP Stapling |
| [传输加密 vs 存储加密](encryption-at-rest-transit/README.md) | 信封加密 + KMS/HSM + 全链路策略 |
| [CORS 预检请求性能陷阱](cors-preflight/README.md) | Simple Request 条件 + Preflight 缓存 + 消除策略 |

### 限流与 OWASP

| 主题 | 核心问题 |
|------|---------|
| [令牌桶 vs 漏桶 vs 滑动窗口](rate-limiting-algorithms/README.md) | 4 大限流算法 + Redis 分布式 + 二级限流 |
| [OWASP Top 10 面试怎么答](owasp-top10/README.md) | 10 大风险速记 + 防御速查 + 安全左移 |

---

## 兄弟模块

- **主模块深度**：[`04.system-design/05-security`](../../04.system-design/05-security/) — 访问控制 / JWT / OAuth2 / 加密 / OWASP / SSO 全套专题
- **同栏目兄弟题**：[`04.system-design`](../../04.system-design/) — 系统设计其他高频题
- **写作规范**：[QUESTION-FORMAT-SPEC.md](../../13.split-hairs/QUESTION-FORMAT-SPEC.md)

← [返回: 咬文嚼字（高频面试题）](../../README.md)
