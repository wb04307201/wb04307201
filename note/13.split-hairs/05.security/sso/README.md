<!--
question:
  id: 05.security-sso
  topic: 05.security
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [05.security, SSO, OAuth2, OIDC, JWT, Spring Security, 单点登录]
-->

# 单点登录（SSO）· 6 大方案选型深挖

> 一句话定位：单点登录不是单一技术，是**设计目标**——6 大方案（Cookie 共享 / CAS / OAuth2 + OIDC / SAML 2.0 / JWT / 代理）的核心都是"**如何把首次登录态安全传递给其他子系统**"。完整深度见 [主模块 sso 专题](../../../04.system-design/05-security/sso/README.md)。

> **系列定位**：经典 Java 后端安全面试题（字节 / 阿里 / 美团 / 360 / 蚂蚁 出题率 80%+）。考察的不是"SSO 是什么"，而是 **6 方案场景化对比能力** + **OAuth2+OIDC 流程深度** + **Spring Security 实战** + **JWT 撤销机制**。

---

## 引子：CTO 上 SSO 项目的 3 个崩溃现场

```text
场景：2024 Q3 某互联网公司 CTO 阿明要给 5 套内部系统做 SSO——
- 系统 A / B / C：D 内部系统（OA / CRM / ERP / GitLab）
- 系统 E：移动 App
- 用户：3000 员工 + 100 万 C 端
- 候选：①Cookie 共享 ②CAS ③OAuth2+OIDC ④SAML ⑤JWT 自建 ⑥代理
```

**决策现场**：
1. **架构师候选人会问**：「现代互联网 SSO 选哪个？为什么不是 CAS？」
2. **CTO 候选人会问**：「OAuth2 和 OIDC 啥关系？怎么和 Spring Security 集成？」
3. **资深候选人会问**：「JWT 自建为什么不行？Token 怎么撤销？」

普通候选人会答"用 OAuth2"——踩中"**理由模糊、缺反模式、缺方案对比**" 3 大雷区。
高分候选人会答：**6 大方案对比（Cookie / CAS / OAuth2+OIDC / SAML / JWT / 代理）+ 选型公式 + 5 反模式 + 场景化实战**。

---

## 一、核心原理（必选）

### 1.1 SSO 的本质

**Single Sign-On（SSO）**：用户**一次登录**，能在**多个互信系统间**无缝访问，**无需重复登录**。

3 大本质问题：
```text
问题 1：身份（Authentication）—— 用户是谁？
问题 2：会话（Session）—— 用户登录状态怎么保持？
问题 3：信任传递（Trust）—— 怎么把 IdP 的信任"传"给其他 SP？
```

SSO 解决**跨多个应用的身份与会话共享**，授权可独立处理。

### 1.2 SSO 3 大角色

```text
Identity Provider (IdP) —— 验证身份 + 颁发票据（Keycloak / Okta / Spring Authorization Server）
Service Provider (SP) —— 业务系统（OA / CRM / ERP / 移动 App）
Principal —— 用户/设备
```

### 1.3 6 大方案对比

| # | 方案 | 票据 | 跨域 | 移动端 | 适用 | 复杂度 |
|---|------|------|------|--------|------|--------|
| 1 | **Cookie 共享** | Cookie | ❌ 仅同根域 | ⚠️ | 同公司同根域 | 低 |
| 2 | **CAS** | Service Ticket | ✅ | ❌ | 老牌企业内部 | 中 |
| 3 | **OAuth2** | Access Token | ✅ | ✅ | 现代互联网（授权） | 中 |
| 4 | **OpenID Connect** | ID Token + Access Token | ✅ | ✅ | **现代互联网 SSO（推荐 ✅）** | 中 |
| 5 | **SAML 2.0** | XML Assertion | ✅ | ❌ | 跨国/金融/政府 | 高 |
| 6 | **JWT 自建** | JWT | ✅ | ✅ | 微服务内部 | 低 |

### 1.4 OAuth2 vs OIDC 关键差异

| 维度 | OAuth2 | OIDC |
|------|-------|------|
| 目的 | 授权（"能干什么"） | **身份**（"你是谁"） |
| Token | Access Token | Access + **ID Token**（JWT 含用户身份） |
| 关键 scope | 任意 | **`openid`**（必需） |
| UserInfo 端点 | 必需 | 可选（已含 ID Token） |

**反直觉**：OIDC = OAuth2 + 身份层，**不是替代**。

### 1.5 JWT 自建的"难撤销"问题

JWT 颁发后在过期前都有效——**IdP 缺位**让撤销困难。需配合：
- **Redis 黑名单**（撤销后写入，TTL = 剩余有效期）
- **Refresh Token Rotate**（每次刷新换新 Token）
- **短 Access Token 有效期**（如 1h）

---

## 二、面试话术（90 秒版本 / 7 问）

> ⚠️ **模板不是背答案**——面试现场结合题目微调。

### 题目 A：什么是单点登录（SSO）？以及实现流程？

**高分答案**（4 层递进，60-90 秒）：

```text
1. 一句话定义（10 秒）：
   "SSO 是'用户一次登录，多系统访问'的设计目标——
   不是单一技术，是多个协议（CAS / OAuth2 / SAML）的设计思想。"

2. 3 大角色 + 核心流程（30 秒）：
   "3 大角色：
   - Principal：用户
   - Identity Provider (IdP)：验证身份 + 颁发票据
   - Service Provider (SP)：业务系统
   通用流程：
   ① 用户访问 SP-A
   ② SP-A 发现未登录，重定向到 IdP（含回调地址）
   ③ 用户在 IdP 登录
   ④ IdP 颁发票据，重定向回 SP-A
   ⑤ SP-A 验证票据 → 创建本地会话
   ⑥ 用户访问 SP-B（同样流程，但 IdP 已有会话，无需重新登录）"

3. 6 大方案选型（30 秒）：
   "6 大方案：
   - 同公司同根域 → Cookie 共享（最简）
   - 老企业内部 → CAS
   - 现代互联网 → OAuth2 + OIDC（推荐 ✅，80% 场景）
   - 跨国/合规 → SAML 2.0
   - 微服务内部 → JWT 自建 + Redis 黑名单
   - 代理模式 → 统一网关鉴权
   现代互联网首选 OAuth2 + OIDC（Spring Authorization Server / Keycloak）"

4. 反模式 + 反问（10 秒）：
   "5 反模式：SSO=OAuth2（缺 OIDC）/ JWT 永不过期 / 跨主域用 Cookie / IdP 单点 / 没登出。
   反问：贵司是同公司同根域，还是跨域多端？这是首要判断。"
```

### 题目 B：OAuth2 和 OIDC 什么关系？

**高分答案**（45 秒）：

```text
"OIDC = OAuth2 + 身份层。

OAuth2 解决授权（我能调你的 API）；
OIDC 在 OAuth2 基础上加 ID Token（含用户身份 JWT）。
所以纯 OAuth2 不能直接做 SSO——用户身份还要调 UserInfo 端点。

OIDC 必选 scope：openid。
完整 SSO 流程：
① 用户点击'用 Google 登录'
② 重定向到 Google OP（OpenID Provider）
③ scope=openid+profile+email
④ 登录成功后 OP 返回 access_token + id_token（含 sub/name/email）
⑤ 业务系统验证 id_token 签名，提取用户信息 → SSO 成功

反直觉：SSO 的关键是 id_token（身份），不是 access_token（授权）。"
```

### 题目 C：JWT 自建 vs OAuth2 + OIDC 怎么选？

**高分答案**（50 秒）：

```text
"选 JWT 自建的场景：
- 内部微服务 API 调用（性能优先）
- 已有用户系统，不想引入 IdP
- 简单业务，团队小

选 OAuth2 + OIDC 的场景：
- 互联网产品（跨平台 / 跨域 / 第三方登录）
- 企业多系统统一身份
- 需要集中失效（员工离职立即禁用）
- 需要第三方授权（'用微信登录'）

JWT 自建的 2 大致命问题：
1. 一旦颁发难撤销（需自建黑名单）
2. 没有集中失效点（员工离职需逐系统禁用）

实战：
- 微服务内部 API：JWT 自建
- 对外 SSO：OAuth2 + OIDC
- 不要混用（避免双套系统维护）"
```

### 题目 D：Spring Security 怎么集成 OAuth2 + OIDC？

**高分答案**（45 秒）：

```text
"Spring Security 集成 OAuth2 + OIDC 需 2 个组件：

1. IdP（Spring Authorization Server）：
   - @EnableAuthorizationServer
   - RegisteredClient + JWKSource（RS256 密钥对）
   - UserDetailsService 用户认证
   - 配置 scope（必须含 openid）
   - /oauth2/authorize, /token, /.well-known/...

2. 业务系统（Resource Server）：
   - spring-boot-starter-oauth2-resource-server
   - 配置 issuer-uri（自动发现 JWKS）
   - SecurityFilterChain 配 OAuth2 ResourceServer
   - @PreAuthorize("hasAuthority('SCOPE_admin')")

关键配置：
- 强制 HTTPS（OAuth2 必须）
- PKCE 启用（防 code 拦截）
- Access Token 短（1h）+ Refresh Token Rotate
- IdP 集群 + 数据库主从（高可用）"
```

### 题目 E：Token 怎么撤销？JWT 自建的最大问题？

**高分答案**（50 秒）：

```text
"JWT 自建默认无撤销机制——这是最大问题。

正确撤销方案：
1. Redis 黑名单
   - 撤销时写入 Redis（key = token_hash, value = "revoked", TTL = 剩余有效期）
   - 每次验签后查 Redis（命中则拒绝）
2. Refresh Token Rotate
   - 每次刷新换新 Refresh Token，旧 Token 立即失效
   - 检测到 Refresh Token 重用则全部 Token 撤销
3. 短 Access Token + 长 Refresh Token
   - Access Token 1h + Refresh 7d
   - 时间到了自动失效

OAuth2 + OIDC 天然支持撤销：
- Token Introspection 端点
- revoke 端点（RFC 7009）
- IdP 集中失效

反模式：JWT 颁发后想撤销 → 没法撤销，只能'等过期'。"
```

### 题目 F：怎么实现单点登出？

**高分答案**（40 秒）：

```text
"单点登出（Single Logout）有 3 大方案：

1. CAS（成熟）：
   - 重定向到 CAS /logout
   - CAS 通过回调清各 SP Session
   - 用户点一次退出，所有系统退出

2. OIDC backchannel logout：
   - IdP 推送登出到 SP（HTTP POST 含 logout_token）
   - SP 清本地 Session + Cookie
   - 用户主动登出，IdP 通知所有 SP

3. JWT 自建（困难）：
   - 用户点登出 → Redis 写黑名单
   - 但其他系统不知道 → 需 Redis Pub/Sub 广播
   - 或短 TTL 强制过期（不实时）

反模式：只实现登录不实现登出——员工离职后仍能访问所有系统。"
```

### 题目 G：CSRF / XSS / Cookie 在 SSO 中的角色？

**高分答案**（35 秒）：

```text
"SSO 需注意 3 大 Web 攻击：

1. CSRF（Cross-Site Request Forgery）：
   - OAuth2 攻击：截获 Authorization Code
   - 防护：State 参数（CSRF token）、PKCE

2. XSS（Cross-Site Scripting）：
   - Token 注入攻击
   - 防护：HttpOnly Cookie、CSP 头部、Token 不放 localStorage

3. Cookie SameSite：
   - OAuth2 必须设置 SameSite=Lax 或 None（+ Secure）
   - 防跨站 Cookie 发送

反模式：localStorage 存 Token（XSS 一击必中）"
```

---

## 三、常见陷阱（必选，5 个核心反模式）

### 陷阱 1：SSO = OAuth2（缺 OIDC）

- **错误**："我们要 SSO，用 OAuth2"
- **真相**：纯 OAuth2 仅"授权"，缺身份层
- **代价**：每个 SP 都要调 UserInfo 端点 → 设计复杂，体验差

### 陷阱 2：JWT 永不过期

- **错误**：Access Token 设 30 天有效
- **真相**：泄露后 30 天都能用
- **代价**：员工离职后还能访问 30 天

### 陷阱 3：同根域 Cookie 跨主域

- **错误**：用 Cookie 共享做跨主域 SSO
- **真相**：Cookie 不能跨主域（浏览器同源策略）
- **代价**：所有跨主域系统都登不上

### 陷阱 4：IdP 单点未高可用

- **错误**：IdP 部署单实例
- **真相**：IdP 挂了 = 所有 SP 都不能登录
- **代价**：1 小时故障 = 整个公司断网

### 陷阱 5：没有单点登出

- **错误**：只实现登录，不实现登出
- **真相**：员工离职后，所有系统都能访问
- **代价**：安全审计失败 / 离职员工能偷数据

---

## 四、最佳实践（4 大工业方案）

### 方案 A：互联网产品（OAuth2 + Spring Authorization Server）

```text
- 方案：OAuth2 + OIDC + Spring Authorization Server
- 配置：PKCE 启用 + RS256 + 短 Access Token
- 用户：1 亿
- 架构：IdP 集群 + 数据库主从 + Redis 缓存

实施：
1. Spring Authorization Server 部署 IdP
2. 各业务系统接 OAuth2 Resource Server
3. JWT 验签 + @PreAuthorize
4. OIDC backchannel logout
```

### 方案 B：跨域企业（OIDC + Keycloak）

```text
- 方案：OIDC + Keycloak
- 用户：50 万员工
- 架构：Keycloak 集群 + LDAP 后端用户

Keycloak 优势：
- 完整产品（UI / 管理后台）
- 支持 SAML / LDAP / 第三方 OAuth
- 多语言生态
```

### 方案 C：金融跨国（SAML 2.0）

```text
- 方案：SAML 2.0 + Shibboleth IdP
- 合规：金融监管 / 国际标准
- 协议：XML 签名 + 单点登出

实施：
- SP 配 Shibboleth SP 模块
- IdP 选 Shibboleth IdP 或商业（如 Okta）
```

### 方案 D：微服务内部（JWT + Redis 黑名单）

```text
- 方案：JWT 自签 + Redis 黑名单 + Refresh Rotate
- 用户：内部 API 调用
- 架构：Redis Cluster + 短 TTL

实施：
- 颁发 JWT（RS256）+ Refresh Token（独立 secret）
- 验签 + 黑名单查询
- 登出写黑名单
- Refresh Rotate 检测 token 重用
```

### 选型决策表

| 场景 | 方案 |
|------|------|
| 同公司同根域 | Cookie 共享 |
| 互联网产品 | OAuth2 + OIDC + Spring Authorization Server |
| 跨域企业 | OIDC + Keycloak |
| 跨国合规 | SAML 2.0 |
| 老系统 Java EE | CAS |
| 微服务内部 | JWT + Redis 黑名单 |

---

## 五、相关章节（强制）

### 主模块深度专题

- [sso 总目录](../../../04.system-design/05-security/sso/README.md)
- [01-sso-concept](../../../04.system-design/05-security/sso/01-sso-concept.md) —— SSO 原理 + 3 大角色 + 6 反模式
- [02-six-schemes-comparison](../../../04.system-design/05-security/sso/02-six-schemes-comparison.md) —— Cookie/CAS/OAuth2/OIDC/SAML/JWT 详解
- [03-spring-security-implementation](../../../04.system-design/05-security/sso/03-spring-security-implementation.md) —— Spring Authorization Server 实战
- [04-jwt-implementation](../../../04.system-design/05-security/sso/04-jwt-implementation.md) —— JWT + Redis 黑名单实战
- [05-selection-decision-tree](../../../04.system-design/05-security/sso/05-selection-decision-tree.md) —— 5 分钟决策树

### 主模块兄弟

- [04.system-design/05-security/oauth2-oidc](../../../04.system-design/05-security/oauth2-oidc/README.md) —— OAuth2/OIDC 完整（500 行）
- [04.system-design/05-security/jwt-security](../../../04.system-design/05-security/jwt-security/README.md) —— JWT 完整（325 行）
- [04.system-design/05-security/access-control](../../../04.system-design/05-security/access-control/README.md) —— RBAC/ABAC

### split-hairs 兄弟

- 🆕 [设计统一权限控制系统](../access-control-design/README.md) — RBAC+ABAC 混合 + 数据模型 + 缓存 + 审计 + 多租户 + 7 道面试题

### Java 后端（Spring）

- [06.spring/05-spring-cloud/gateway](../../../06.spring/05-spring-cloud/gateway.md) —— Spring Cloud Gateway OAuth2 集成
- [06.spring/05-spring-cloud/README](../../../06.spring/05-spring-cloud/README.md) —— Spring Cloud 全套

---

## 六、面试反问（让候选人反客为主）

```text
Q1：贵司跨主域吗（同根域 vs 跨主域）？
    → 同根域 Cookie 共享，跨主域 OAuth2+OIDC
Q2：贵司产品是 Web 还是含 App？
    → Web 单方案；多端 OAuth2+OIDC
Q3：贵司用户量级？
    → < 100 万：CAS；> 100 万：OAuth2
Q4：贵司对延迟 P99 SLO 是多少？
    → < 100ms：JWT 自建（无 IdP 网络跳转）；< 500ms 可接受 OAuth2
Q5：贵司是否需 IdP 集中失效？
    → 是 → OAuth2+OIDC（推荐）；否 → JWT 自建
```

---

> 📅 2026-07-06 · 咬文嚼字 · 05.security · ⭐⭐⭐⭐⭐ · 7 道精选 Q&A · 含 90 秒话术模板 + 5 大反模式 + 4 工业方案

← [返回: 咬文嚼字 · sso](../README.md)
