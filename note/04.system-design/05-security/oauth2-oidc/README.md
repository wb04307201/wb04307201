<!--
module:
  parent: system-design
  slug: system-design/oauth2-oidc
  type: article
  category: 主模块子文章
  summary: OAuth2.0 是现代互联网最流行的授权框架，OIDC 则在其之上构建了身份认证层。
-->

# OAuth2.0 与 OpenID Connect (OIDC)

> OAuth2.0 是现代互联网最流行的授权框架，OIDC 则在其之上构建了身份认证层。

## 目录

- [OAuth2.0 核心概念](#oauth20-核心概念)
- [四种授权模式](#四种授权模式)
- [OpenID Connect (OIDC)](#openid-connect-oidc)
- [OAuth2.0 vs OIDC 对比](#oauth20-vs-oidc-对比)
- [最佳实践与常见陷阱](#最佳实践与常见陷阱)
- [相关章节](#相关章节)
- [参考资料](#参考资料)

---
---

## OAuth2.0 核心概念

OAuth2.0（Open Authorization 2.0）是一个**授权**框架，允许第三方应用以有限的权限访问用户在另一个服务上的资源，而无需暴露用户的凭证。

### 四大角色

| 角色 | 英文 | 说明 | 示例 |
|------|------|------|------|
| 资源所有者 | Resource Owner | 拥有资源实体的实体，通常是**用户** | 你（GitHub 用户） |
| 客户端 | Client | 代表资源所有者发起请求的应用 | 第三方 App、SPA |
| 授权服务器 | Authorization Server (AS) | 验证用户身份并颁发 Access Token | GitHub OAuth 服务器 |
| 资源服务器 | Resource Server (RS) | 持有受保护资源，验证 Token 后返回数据 | GitHub API |

### 核心流程概览

```text
┌─────────┐     ①请求授权     ┌──────────┐
│         │ ─────────────────▶ │          │
│  Client │                    │    AS    │
│         │ ◀───────────────── │          │
└────┬────┘     ②返回Token     └────┬─────┘
     │                              │
     │ ③携带Token请求资源            │
     ▼                              ▼
┌─────────┐     ④验证Token       ┌──────────┐
│         │ ────────────────────▶ │          │
│  Client │                       │    RS    │
│         │ ◀──────────────────── │          │
└─────────┘     ⑤返回资源         └──────────┘
```

> **关于 Resource Owner Password Credentials（Password Grant）**：RFC 6749 最初定义的 4 种授权模式中包含"密码模式"，但因其要求用户将密码直接交给客户端，安全风险高，已被 RFC 8252（OAuth 2.0 for Native Apps）和 OAuth 2.1 草案**废弃**，新项目**不应再使用**。

---

## 四种授权模式

本文按推荐度从高到低排列：

1. 授权码模式（Authorization Code）
2. 授权码 + PKCE（推荐用于 SPA / 移动端）
3. 客户端凭证模式（Client Credentials）
4. 隐式模式（Implicit，已废弃，仅作了解）

### 1. 授权码模式（Authorization Code）— 最安全、最推荐

**适用场景**: 服务端 Web 应用（有后端服务器能安全保管 Client Secret）

这是 OAuth2.0 中最安全、最推荐的模式。核心思想是：**先拿授权码，再用授权码换 Token**，避免 Token 直接暴露在浏览器中。

#### 流程图

```text
浏览器                客户端后端              授权服务器(AS)
  │                     │                      │
  │  ① 重定向到授权页面   │                      │
  │ ─────────────────────────────────────────▶│
  │                     │                      │
  │  ② 用户登录并授权     │                      │
  │ ◀─────────────────────────────────────────│
  │                     │                      │
  │  ③ 回调,携带 code    │                      │
  │ ──────────────────▶ │                      │
  │                     │                      │
  │                     │  ④ POST /token       │
  │                     │  (code+client_secret)│
  │                     │ ──────────────────▶ │
  │                     │                      │
  │                     │  ⑤ 返回 access_token │
  │                     │ ◀────────────────── │
  │                     │                      │
  │  ⑥ 返回 token/session│                      │
  │ ◀────────────────── │
```

#### 步骤详解

1. **用户点击登录** → 客户端生成 `state`（防 CSRF），重定向到授权服务器
   ```text
   GET https://as.example.com/authorize?
     response_type=code
     &client_id=s6BhdRkqt3
     &redirect_uri=https://client.example.com/callback
     &scope=read%20write
     &state=xyz123
   ```

2. **用户登录并授权** → 授权服务器验证用户身份，展示授权页面

3. **授权回调** → 授权服务器重定向回客户端，URL 中携带 `code` 和 `state`
   ```text
   GET https://client.example.com/callback?
     code=SplxlOBeZQQYbYS6WxSbIA
     &state=xyz123
   ```

4. **后端换取 Token** → 客户端后端用 `code` + `client_secret` 向 Token 端点换取 Token
   ```http
   POST /oauth/token HTTP/1.1
   Host: as.example.com
   Content-Type: application/x-www-form-urlencoded
   Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW

   grant_type=authorization_code
   &code=SplxlOBeZQQYbYS6WxSbIA
   &redirect_uri=https://client.example.com/callback
   ```

5. **返回 Token**
   ```json
   {
     "access_token": "2YotnFZFEjr1zCsicMWpAA",
     "token_type": "Bearer",
     "expires_in": 3600,
     "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
     "scope": "read write"
   }
   ```

6. **客户端建立会话** → 将 Token 存入 Session 或设置 HttpOnly Cookie

#### 关键安全点

- `state` 参数防止 CSRF 攻击
- Token 通过后端服务器间通信获取，不经过浏览器
- 使用 `client_secret` 验证客户端身份

---

### 2. Authorization Code + PKCE — 移动端 / SPA 推荐

**适用场景**: 单页应用（SPA）、移动应用、桌面应用

PKCE（Proof Key for Code Exchange，读作 "pixy"）是 OAuth2.0 的扩展，通过在授权请求时生成一个密钥对，确保只有发起请求的客户端才能换取 Token，防止授权码拦截攻击。

#### PKCE 核心参数

| 参数 | 说明 |
|------|------|
| `code_verifier` | 客户端生成的随机字符串（43-128 字符） |
| `code_challenge` | `code_verifier` 的哈希值，发送给授权服务器 |
| `code_challenge_method` | 哈希算法：`S256`（推荐）或 `plain` |

计算公式：`code_challenge = BASE64URL(SHA256(code_verifier))`

#### 流程图

```text
浏览器/APP              客户端逻辑               授权服务器(AS)
  │                       │                        │
  │  生成 code_verifier   │                        │
  │  计算 code_challenge  │                        │
  │                       │                        │
  │  ① 请求授权(含         │                        │
  │     code_challenge)   │                        │
  │ ───────────────────────────────────────────▶ │
  │                       │                        │
  │  ② 用户登录并授权      │                        │
  │                       │                        │
  │  ③ 回调,返回 code     │                        │
  │ ────────────────────▶ │                        │
  │                       │                        │
  │                       │  ④ POST /token         │
  │                       │  (code+code_verifier)  │
  │                       │ ────────────────────▶ │
  │                       │                        │
  │                       │  ⑤ 验证 verifier,      │
  │                       │     返回 access_token  │
  │                       │ ◀──────────────────── │
  │                       │                        │
  │  ⑥ 登录成功           │                        │
  │ ◀─────────────────── │
```

#### 代码示例

**Step 1: 生成 code_verifier 和 code_challenge**

```java
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;

public class PkceUtil {
    // 生成 43-128 字符的随机 code_verifier
    public static String generateCodeVerifier() {
        SecureRandom random = new SecureRandom();
        byte[] bytes = new byte[32];
        random.nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    // 根据 code_verifier 计算 code_challenge (S256)
    public static String generateCodeChallenge(String codeVerifier) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(codeVerifier.getBytes());
        return Base64.getUrlEncoder().withoutPadding().encodeToString(hash);
    }
}
```

**Step 2: 发起授权请求**

```text
GET https://as.example.com/authorize?
  response_type=code
  &client_id=s6BhdRkqt3
  &redirect_uri=myapp://callback
  &scope=openid%20profile
  &state=xyz123
  &code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
  &code_challenge_method=S256
```

**Step 3: 用 code_verifier 换取 Token**

```http
POST /oauth/token HTTP/1.1
Host: as.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=SplxlOBeZQQYbYS6WxSbIA
&redirect_uri=myapp://callback
&client_id=s6BhdRkqt3
&code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

授权服务器会用 `code_verifier` 计算 SHA256 并与之前收到的 `code_challenge` 比对，匹配才返回 Token。

---

### 3. 客户端凭证模式（Client Credentials）— 机器对机器

**适用场景**: 服务端对服务端、后台任务、微服务之间调用

此模式不涉及用户，是客户端以自己的身份获取访问令牌。

#### 流程图

```text
客户端                     授权服务器(AS)
  │                           │
  │  ① POST /token            │
  │  (client_id+client_secret)│
  │ ────────────────────────▶│
  │                           │
  │  ② 返回 access_token      │
  │ ◀────────────────────────│
  │
  │  ③ 携带 Token 访问资源服务器
  │ ───────────────────────▶ RS
```

#### 请求示例

```http
POST /oauth/token HTTP/1.1
Host: as.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW

grant_type=client_credentials
&scope=read:metrics
```

#### 响应

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read:metrics"
}
```

#### 使用场景举例

| 场景 | 说明 |
|------|------|
| 微服务间调用 | 服务 A 调用服务 B 的 API |
| 后台定时任务 | 定时任务访问资源服务器拉取数据 |
| CI/CD 流水线 | 部署脚本调用云资源 API |
| 第三方数据同步 | 系统间数据对接 |

---

### 4. 隐式模式（Implicit）— 不推荐、已废弃

**适用场景**: 已废弃，不再推荐使用

> RFC 6749 中定义的隐式模式因安全风险已被 RFC 8252 和 OAuth 2.1 废弃。

#### 为什么不推荐

1. **Access Token 直接在 URL 中返回**，会出现在浏览器历史、服务器日志、Referer 头中
2. **无法刷新 Token**，没有 `refresh_token`
3. **无法证明客户端身份**，没有 `client_secret`
4. **容易被恶意脚本窃取**

#### 旧流程图（仅作了解）

```text
浏览器                          授权服务器(AS)
  │                                │
  │  ① 请求授权 (response_type=token)│
  │ ──────────────────────────────▶│
  │                                │
  │  ② 用户登录并授权                │
  │                                │
  │  ③ 回调,直接在 URL fragment 中  │
  │     返回 access_token           │
  │ ◀──────────────────────────────│
  │
  │  #access_token=xxxxx&token_type=Bearer
```

**替代方案**: 使用 **Authorization Code + PKCE**（见上方第 2 种模式）

---

## OpenID Connect (OIDC)

OIDC 是基于 OAuth2.0 构建的**身份认证**协议。OAuth2.0 解决的是**授权**（能不能访问资源），OIDC 解决的是**认证**（你是谁）。

### 核心概念

| 概念 | 说明 |
|------|------|
| ID Token | JWT 格式，包含用户身份信息，由授权服务器签名 |
| UserInfo Endpoint | 获取用户详细信息的 API 端点 |
| `openid` Scope | 请求 OIDC 功能时必须携带此 scope |
| Standard Claims | 标准用户信息字段：sub, name, email, picture 等 |

### OIDC 流程（基于授权码模式）

```text
浏览器                客户端后端              AS/OIDC Provider
  │                     │                      │
  │  ① 请求授权           │                      │
  │  (scope=openid)      │                      │
  │ ─────────────────────────────────────────▶│
  │                     │                      │
  │  ② 用户登录授权       │                      │
  │  ③ 回调 + code      │                      │
  │ ──────────────────▶ │                      │
  │                     │  ④ 换 Token          │
  │                     │ ──────────────────▶ │
  │                     │  ⑤ access_token      │
  │                     │     + id_token       │
  │                     │ ◀────────────────── │
  │                     │                      │
  │                     │  ⑥ 可选: 调用        │
  │                     │     UserInfo Endpoint│
  │                     │ ──────────────────▶ │
  │                     │  ⑦ 用户详细信息       │
  │                     │ ◀────────────────── │
  │                     │                      │
  │  ⑧ 验证 ID Token    │                      │
  │     建立会话        │                      │
  │ ◀────────────────── │
```

### ID Token 结构

ID Token 是一个签名的 JWT，包含用户身份信息：

```json
{
  "iss": "https://accounts.google.com",
  "sub": "110169484474386276334",
  "aud": "your-client-id",
  "exp": 1678901234,
  "iat": 1678897634,
  "nonce": "n-0S6_WzA2Mj",
  "name": "张三",
  "email": "zhangsan@example.com",
  "email_verified": true,
  "picture": "https://example.com/avatar.jpg"
}
```

**关键字段说明**:

| 字段 | 说明 |
|------|------|
| `iss` | Issuer，签发者（必须验证） |
| `sub` | Subject，用户唯一标识（在同一 Issuer 下稳定不变） |
| `aud` | Audience，接收方（必须匹配客户端 ID） |
| `exp` | Expiration，过期时间 |
| `nonce` | 防重放攻击，必须与请求时发送的一致 |

### 验证 ID Token 的步骤

1. 验证签名（使用 Issuer 的公钥）
2. 验证 `iss` 是否为预期的签发者
3. 验证 `aud` 是否包含当前客户端 ID
4. 验证 `exp` 是否未过期
5. 验证 `nonce` 是否与请求时一致（如使用了 nonce）

---

## OAuth2.0 vs OIDC 对比

| 维度 | OAuth2.0 | OIDC |
|------|----------|------|
| **核心目的** | 授权（Access Resource） | 认证（Authentication） |
| **回答问题** | "能不能访问资源？" | "你是谁？" |
| **核心产物** | Access Token | ID Token + Access Token |
| **Token 格式** | 不透明字符串或 JWT | 必须是 JWT |
| **Scope** | 自定义资源范围 | 必须包含 `openid` |
| **用户信息** | 需要调用资源服务器 API | 通过 ID Token 和 UserInfo Endpoint 获取 |
| **标准化程度** | 框架，具体实现灵活 | 标准化程度更高，Claim 有规范 |
| **典型场景** | 第三方应用访问用户数据 | 单点登录（SSO）、联合身份 |
| **关系** | 基础协议 | 构建在 OAuth2.0 之上 |

---

## 最佳实践与常见陷阱

### 最佳实践

1. **永远使用 Authorization Code + PKCE**，即使是 SPA 和移动应用
2. **绝对不要在前端存储 Access Token**，使用 HttpOnly Cookie 或 BFF（Backend for Frontend）模式
3. **始终验证 `state` 参数**，防止 CSRF 攻击
4. **始终验证 ID Token 的签名和声明**，包括 `iss`、`aud`、`exp`、`nonce`
5. **使用最短合理的 Token 过期时间**，配合 Refresh Token 续期
6. **Access Token 和 Refresh Token 分开存储**，Refresh Token 需要更严格的保护
7. **PKCE 始终使用 `S256` 算法**，不要使用 `plain`
8. **使用 HTTPS**，所有 OAuth2.0/OIDC 通信必须加密

### 常见陷阱

| 陷阱 | 风险 | 解决方案 |
|------|------|----------|
| localStorage 存 Token | XSS 攻击可窃取 Token | 使用 HttpOnly Cookie 或 BFF 模式 |
| 不验证 state | CSRF 攻击 | 生成随机 state，回调时校验 |
| Implicit 模式 | Token 泄露 | 改用 Authorization Code + PKCE |
| Password Grant | 用户密码泄露给客户端 | 改用 Auth Code + PKCE |
| 不验证 ID Token 签名 | 伪造身份 | 用公钥验证 JWT 签名 |
| 超长 Token 过期时间 | Token 被盗后长期有效 | Access Token 短时效 + Refresh Token |
| 使用 plain 的 PKCE | 授权码拦截攻击 | 始终使用 S256 |
| redirect_uri 不校验 | 开放重定向漏洞 | 精确匹配预注册的 redirect_uri |

### Java 生态推荐实现

| 框架 | 说明 |
|------|------|
| Spring Authorization Server | Spring 官方授权服务器实现（推荐用于新项目） |
| Spring Security OAuth2 Resource Server | 作为资源服务器验证 Access Token（推荐） |
| Keycloak | 开源身份认证与访问管理服务器 |
| Pac4j | 多协议安全引擎（OAuth、SAML、CAS 等） |

> **重要更新**：`spring-security-oauth2`（已废弃）已被 **Spring Authorization Server** 替代；新项目请使用 **Spring Authorization Server** 或 **Keycloak**。原 `spring-security-oauth2` 项目自 2020 年起进入维护模式，不再添加新功能。

---

## 相关章节

- [JWT 存储安全](../jwt-security/README.md) — Access Token / ID Token 的存储与撤销
- [API 安全](../api-security/README.md) — Bearer Token 传输、签名验证、防重放
- [权限模型 RBAC / ABAC](../access-control/02-role-and-attribute/README.md) — Token 中携带的 scope / role 如何消费

## 参考资料

- [RFC 6749 - The OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [RFC 6750 - The OAuth 2.0 Authorization Framework: Bearer Token Usage](https://tools.ietf.org/html/rfc6750)
- [RFC 7636 - Proof Key for Code Exchange (PKCE)](https://tools.ietf.org/html/rfc7636)
- [RFC 8252 - OAuth 2.0 for Native Apps](https://tools.ietf.org/html/rfc8252)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [OAuth 2.1 Draft](https://oauth.net/2.1/)

---

## 🆕 深度扩展：单点登录（SSO）6 大方案专题

本章节重点讲 OAuth2/OIDC 协议本身，**SSO 作为设计目标**的 6 大实现方案对比（含 CAS / Cookie / OAuth2+OIDC / SAML 2.0 / JWT / 代理）已沉淀到独立专题：

- **SSO 主模块深度**：[../sso/README.md](../sso/README.md) —— 6 文件 / 1520 行深度（含 Spring Security 实战 + JWT 自签 + 选型决策树）
- **面试题（5.security 新增）**：[13.split-hairs/05.security/sso](../../../13.split-hairs/05.security/sso/README.md) —— 7 道精选 Q&A + 90 秒话术 + 5 反模式

← [返回 安全篇](../README.md)
