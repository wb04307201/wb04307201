<!--
question:
  id: 05.security-oauth2-flow
  topic: 05.security
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [05.security, OAuth2, Authorization Code, Implicit, Client Credentials, PKCE]
-->

# OAuth2 四种授权模式分别适用什么场景？—— Grant Type 选型与 PKCE 加固

> 一句话定位：OAuth2 的 4 种 Grant Type 本质是**"谁来证明身份、在哪里证明"**的不同组合。完整 OAuth2 协议见 [主模块 OAuth2/OIDC](../../../04.system-design/05-security/oauth2-oidc/README.md)。

> **系列定位**：经典安全面试题（大厂高频）。考察 **4 种模式场景化对比** + **PKCE 为什么取代 Implicit** + **Authorization Code 拦截攻击**。

---

## 引子：一个 App 接微信登录引发的安全审计

```text
某创业团队给移动 App 接入"微信登录"，架构师选了 Implicit Flow（觉得简单）——
安全审计发现：Token 出现在 URL Fragment 里，被浏览器历史记录 + Referrer 泄露
微信官方已推荐 Authorization Code + PKCE，Implicit 标记为"不推荐"
```

**反直觉**：OAuth 2.1 草案已废弃 Implicit；PKCE 本来给移动端设计，现在 SPA 也必须用。

---

## 一、核心原理

| 模式 | 适用场景 | 安全等级 | 当前状态 |
|------|---------|---------|---------|
| **Authorization Code** | 传统 Web App（有后端） | ⭐⭐⭐⭐⭐ | 推荐 |
| **Authorization Code + PKCE** | SPA / 移动端 | ⭐⭐⭐⭐⭐ | **首选** |
| **Client Credentials** | 服务间调用（无用户） | ⭐⭐⭐⭐ | 推荐 |
| **Implicit** | ~~SPA~~ | ⭐⭐ | **已废弃** |

**Authorization Code 流程**：用户重定向到授权页 → 登录授权 → 回调带 code → 后端用 code + client_secret 换 Token。**关键**：Token 交换在后端完成，前端永远接触不到 Token。

**PKCE 防什么**：Authorization Code 拦截攻击——恶意 App 截获 code 后换取 Token。PKCE 让客户端生成 code_verifier，授权请求带其 SHA256 哈希，Token 交换时带原始 verifier 验证。

**Client Credentials**：无用户参与，client_id + client_secret 直接换 Token，适合微服务间调用。

**Implicit 为什么废弃**：Token 在 URL Fragment → 历史记录泄露；无 Refresh Token；无法验证客户端身份。

---

## 二、详解

### 2.1 PKCE 流程

```text
① Client 生成 code_verifier（随机 43-128 字符）
② 计算 code_challenge = BASE64URL(SHA256(code_verifier))
③ 授权请求带 code_challenge
④ Token 交换带 code_verifier
⑤ Auth Server 验证 SHA256(verifier) == challenge → 即使 code 被截获也无法利用
```

### 2.2 安全加固清单

- 强制 HTTPS（OAuth2 在 HTTP 下完全不安全）
- Authorization Code 一次性使用（10 分钟过期）
- State 参数防 CSRF：`state = HMAC(session_id, secret)`
- Refresh Token Rotate + 重用检测（重用则撤销整条链）
- Scope 最小化：只申请业务需要的权限

---

## 三、常见陷阱

- **SPA 用 Implicit Flow**：OAuth 2.1 已废弃 → 改用 Authorization Code + PKCE
- **不校验 State 参数**：CSRF 攻击者把自己的 Code 注入受害者浏览器
- **微服务间用 Authorization Code**：无用户参与时应选 Client Credentials
- **Refresh Token 不设过期且不 Rotate**：被盗后可无限续命

---

## 四、最佳实践

```text
选型决策树：
  有用户参与？
  ├─ 否 → Client Credentials（服务间调用）
  └─ 是 → 客户端能安全存储 Secret？
       ├─ 是（Web 后端） → Authorization Code
       └─ 否（SPA / 移动端） → Authorization Code + PKCE
```

---

## 五、面试话术（90 秒版本）

> "OAuth2 有 4 种 Grant Type。Authorization Code 适合有后端的 Web App，Token 交换在后端完成。Code + PKCE 是升级版，用 code_verifier 防 Code 拦截攻击，是 SPA 和移动端首选。Client Credentials 用于服务间调用，无用户参与。Implicit 已被 OAuth 2.1 废弃，因 Token 暴露在 URL Fragment 且无法刷新。
>
> PKCE 的核心：客户端生成随机 verifier，授权请求发其 SHA256 哈希，Token 交换时发原始 verifier 验证。即使 Code 被截获，没有 verifier 也换不到 Token。安全要点：强制 HTTPS、State 防 CSRF、Refresh Token Rotate、Scope 最小化。"

---

## 六、交叉引用

- [单点登录 6 大方案](../sso/README.md) — OAuth2 在 SSO 中的角色
- [JWT vs Session](../jwt-vs-session/README.md) — Token 存储与传递
- [XSS、CSRF、CSP 三件套](../xss-csrf-csp/README.md) — State 参数与 CSRF 防护
- [主模块 OAuth2/OIDC](../../../04.system-design/05-security/oauth2-oidc/README.md) — 协议深度 + Spring 实现

---

← [返回: 咬文嚼字 · 安全](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 05.security · ⭐⭐⭐⭐⭐
