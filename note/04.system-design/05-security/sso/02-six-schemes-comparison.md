<!--
module:
  parent: 04.system-design/05-security/sso
  slug: system-design/05-security/sso/02-six-schemes-comparison
  type: topic
  category: 6 大方案详解
  summary: SSO 6 大实现方案详解 —— Cookie 共享 / CAS / OAuth2 / OIDC / SAML 2.0 / JWT 自建
-->

# SSO 6 大方案详解 · 主流协议对比

> **一句话**：6 大方案不是"哪个最好"——是"哪个适合你的场景"。**Cookie 共享**适合同公司，**CAS** 适合老企业内部，**OAuth2+OIDC** 适合现代互联网，**SAML 2.0** 适合跨国企业，**JWT 自建** 适合微服务。

← [返回: SSO 总目录](../README.md)

---

## 1. 方案 A：Cookie 共享（同根域）

### 1.1 核心思想

多个子域共享同一个根域的 Cookie。

```text
[www.example.com]   ← 设置 Cookie：domain=.example.com
[app.example.com]   ← 自动收到 Cookie
[admin.example.com] ← 自动收到 Cookie
```

### 1.2 实现

```nginx
# 登录系统设置 Cookie（Domain 设为根域）
Set-Cookie: session_id=xxx; Path=/; Domain=.example.com; HttpOnly; Secure; SameSite=Lax

# 三个子域都共享同一 Cookie
```

### 1.3 优点

- 实现最简单（10 行代码）
- 用户体验最好（无感知）
- 性能最好（无网络跳转）

### 1.4 缺点

| 缺陷 | 说明 |
|------|------|
| **仅同根域** | a.com 和 b.com 不能共享 |
| **不安全** | Cookie 明文携带 session_id，易被劫持 |
| **单点故障** | 认证中心挂了全部登不上 |
| **不易跨平台** | 移动 App / 小程序不友好 |

### 1.5 适用

- 同公司多产品（小公司起步方案）
- 不需要跨主域
- 内部系统

---

## 2. 方案 B：CAS（Central Authentication Service）

### 2.1 核心思想

中心化认证服务 + Service Ticket（票据）。

```text
[CAS Server] 中央认证服务
   ↓ 重定向 + 票据
[App-A]        ← 用户访问 App-A，发现未登录
   ↓ 重定向到 CAS
[CAS Server]    ← 验证票据有效 → App-A 创建本地会话
   ↓ 颁发新票据
[App-B]        ← 同样流程（无需重新登录）
```

### 2.2 CAS 协议流程

```text
1. 用户访问 App-A
2. App-A 重定向到 CAS /login?service=https://app-a.com/callback
3. 用户输入账号密码
4. CAS 验证后重定向回 App-A，附 service ticket（一次性）
   例如：https://app-a.com/callback?ticket=ST-abc123
5. App-A 拿 ticket 到 CAS /serviceValidate 验证
6. 验证通过 → App-A 创建本地会话
7. 用户访问 App-B：App-B 重定向到 CAS → CAS 已有会话 → 直接颁发 ticket → 完成
```

### 2.3 优点

- 跨域支持（多子域）
- 老牌成熟（2002 年起）
- 开源（Apereo CAS）

### 2.4 缺点

| 缺陷 | 说明 |
|------|------|
| **复杂** | Service Ticket 流程需严格实现 |
| **老旧** | XML / 旧协议，移动端支持差 |
| **不开箱即用** | 需自己搭 CAS Server |

### 2.5 适用

- 老企业内部（10+ 年项目）
- Java EE 体系
- 政府 / 国企

---

## 3. 方案 C：OAuth2

### 3.1 核心思想

**OAuth2 = 授权框架**（不是认证）—— 但配合 OIDC 后**完整支持 SSO**。

### 3.2 OAuth2 4 种模式（Grant Type）

| 模式 | 流程 | 适用 |
|------|------|------|
| **授权码模式（Authorization Code）** | 第三方跳转登录 | Web SSO（最常用）|
| **密码模式（Password）** | 用户名密码直接换 Token | 内部应用（不推荐公网）|
| **客户端模式（Client Credentials）** | 服务对服务认证 | 微服务之间 |
| **隐式模式（Implicit）** | 直接返回 Token（前端 SPA）| 已弃用，推荐 PKCE |

### 3.3 OAuth2 授权码模式流程

```text
┌─────────┐                ┌─────────┐                  ┌─────────┐
│  浏览器  │                │ App-A   │                  │ Auth    │
│         │                │         │                  │ Server  │
└────┬────┘                └────┬────┘                  └────┬────┘
     │  1.访问 App-A          │                              │
     ├───────────────────────→                              │
     │                        │ 2.重定向到 Auth Server      │
     │   ?response_type=code                                │
     │   &client_id=app-a                                  │
     │   &redirect_uri=https://app-a/callback              │
     ├─────────────────────────────────────────────────────→│
     │                        │                              │
     │   3.登录 + 授权   │                              │
     │◀────────────────────────────────────────────────────┤
     │   4.返回授权码                                   │
     │   https://app-a/callback?code=ABC123               │
     ├───────────────────────→                              │
     │                        │ 5.用 code 换 Token         │
     │                        │ POST /token                 │
     │                        │   code=ABC123              │
     │                        │   client_id + secret        │
     │                        ├────────────────────────────→│
     │                        │                              │
     │                        │   6.返回 access_token      │
     │                        │   + refresh_token          │
     │                        │   + id_token (OIDC)        │
     │                        │←────────────────────────────┤
     │                        │                              │
     │   7.App-A 设置 cookie     │                              │
     │◀────────────────────────┤                              │
     │                          │                              │
```

### 3.4 优点

- 跨域 / 跨平台（移动 / Web / 小程序通用）
- 短 Access Token + 长 Refresh Token（可撤销）
- 用户授权粒度可控（scope）
- 现代事实标准

### 3.5 缺点

- **不包含用户身份**（需配合 OIDC）
- 配置复杂（多种 grant type）
- 需 HTTPS

### 3.6 适用

- 跨平台应用（Web + iOS + Android）
- 互联网产品
- 需要第三方授权（"用微信登录"）

---

## 4. 方案 D：OpenID Connect（OIDC）

### 4.1 核心思想

**OAuth2 + 身份层** = OIDC。补充 ID Token（JWT 格式），让 OAuth2 也能传递身份。

### 4.2 关键差异

| 维度 | OAuth2 | OIDC |
|------|-------|------|
| **目的** | 授权 | 身份认证 |
| **Token** | Access Token | Access Token + **ID Token**（含用户身份） |
| **颁发** | Auth Server | Auth Server（OpenID Provider）|
| **用户信息** | 需调 UserInfo 端点 | 直接从 ID Token Claims 读 |

### 4.3 OIDC 流程（基于授权码）

```text
1. App-A 重定向用户到 OpenID Provider (OP)：
   ?scope=openid+profile+email   ← 关键是 openid scope
2. 用户在 OP 登录 + 授权
3. OP 重定向回 App-A 回调：
   ?code=abc123  &  id_token=eyJ... （ID Token）
4. App-A 用 code 换 access_token + id_token
5. App-A 验证 ID Token 签名，提取用户身份
```

### 4.4 优点

- 完整 SSO 解决方案
- JWT 格式 ID Token 携带用户信息
- 主流 Identity Provider 支持（Keycloak / Okta / Auth0 / Authing）

### 4.5 适用

- **现代互联网 SSO 首选** ⭐
- 跨平台应用
- 需要统一身份 + 第三方授权

---

## 5. 方案 E：SAML 2.0

### 5.1 核心思想

基于 XML 断言的 SAML 协议，由 IdP 签名后 SP 验证。

### 5.2 SAML SSO 流程

```text
1. 用户访问 SP（业务系统）
2. SP 生成 SAML AuthnRequest（XML）
3. 浏览器重定向到 IdP（携带 SAMLRequest）
4. 用户在 IdP 登录
5. IdP 生成 SAML 断言（XML + 签名）
6. 浏览器 POST SAMLResponse 到 SP 的 ACS 端点
7. SP 验证 XML 签名 → 创建本地会话
```

### 5.3 优点

- 老牌企业级（金融 / 政府 / 跨国）
- XML 签名非对称加密（强安全）
- 完整标准（含 SingleLogout）

### 5.4 缺点

| 缺陷 | 说明 |
|------|------|
| XML 笨重 | 移动端支持差 |
| 配置复杂 | 元数据交换、签名验证 |
| 不适合现代 Web | 推荐 OAuth2/OIDC |

### 5.5 适用

- 跨国企业（SAP / Oracle）
- 金融 / 政府 / 医疗
- 已有 SAML 基础设施

---

## 6. 方案 F：JWT 自建

### 6.1 核心思想

颁发 JWT（自签含 Claims），子系统验签即可。

```java
// 颁发 JWT
String jwt = Jwts.builder()
    .setSubject("user-123")
    .claim("role", "admin")
    .setExpiration(new Date(System.currentTimeMillis() + 3600000))
    .signWith(SignatureAlgorithm.HS256, secret)
    .compact();
```

### 6.2 优点

- 无状态（无需查询 IdP）
- 高性能（本地验签）
- 跨语言支持（所有语言都有 JWT 库）

### 6.3 缺点

| 缺陷 | 说明 |
|------|------|
| **难撤销** | 一旦颁发，到期前都有效（除非用黑名单）|
| **IdP 缺位** | 没有集中失效点 |
| **Secret 管理** | 共享密钥分发难 |

### 6.4 适用

- 微服务内部 API 调用
- BFF 与下游服务
- 已配合 IdP + 黑名单

---

## 7. 6 大方案对比表

| 维度 | Cookie | CAS | OAuth2 | OIDC ⭐ | SAML | JWT |
|------|--------|-----|--------|---------|------|------|
| 跨域 | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 移动端 | ⚠️ | ❌ | ✅ | ✅ | ❌ | ✅ |
| 单点登出 | ❌ | ✅ | ⚠️ | ✅ | ✅ | ❌ |
| Token 自验签 | N/A | ❌ | ❌ | ✅ | ❌ | ✅ |
| 标准成熟度 | ⚠️ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| 复杂度 | 低 | 中 | 中高 | 中 | 高 | 低 |
| 适用时代 | 2010 之前 | 2005-2015 | 2015+ | 2015+ | 2005+ | 2015+ |
| 主流框架 | 无 | Apereo CAS | Spring Authorization Server | Keycloak | Shibboleth | 无标准 |

---

## 8. 选型决策

```text
场景：我要做 SSO，怎么选？

Q1：跨主域吗？
├─ 否 → Cookie 共享（同公司）
└─ 是 ↓

Q2：现代互联网产品（Web + App）？
├─ 是 → OAuth2 + OIDC（推荐 ✅）
└─ 否 ↓

Q3：跨国 / 合规 / 金融？
├─ 是 → SAML 2.0
└─ 否 ↓

Q4：10 年以上老系统（Java EE）？
├─ 是 → CAS
└─ 否 ↓

Q5：内部微服务（API 调用）？
├─ 是 → JWT 自建 + Redis 黑名单
└─ 否 ↓

默认推荐：OAuth2 + OIDC + Keycloak（80% 场景）
```

---

## 9. 一句话总结

> **6 大方案选型公式：现代互联网选 OAuth2+OIDC；跨国企业选 SAML；Java EE 老系统选 CAS；微服务内部选 JWT；同公司同根域选 Cookie。**

---

← [返回: SSO 总目录](../README.md) · 上一章：[01-sso-concept](01-sso-concept.md) · 下一章：[03-spring-security-implementation](03-spring-security-implementation.md)
