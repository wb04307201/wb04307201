<!--
module:
  parent: system-design
  slug: system-design/jwt-security
  type: article
  category: 主模块子文章
  summary: 为什么 `localStorage` 存储 JWT 是危险的？JWT（JSON Web Token）是现代 Web 应用最常用的无状态认证方案，但其存储方式直接...
-->

# JWT 存储安全

> 为什么 `localStorage` 存储 JWT 是危险的？JWT（JSON Web Token）是现代 Web 应用最常用的无状态认证方案，但其存储方式直接决定了系统的安全性。本文从 JWT 结构出发，详解常见攻击、安全存储与撤销策略。

## 目录

- [JWT 结构](#jwt-结构)
- [标准 Claims](#标准-claims)
- [验证流程](#验证流程)
- [常见攻击与防御](#常见攻击与防御)
- [存储方式对比](#存储方式对比)
- [Token 撤销](#token-撤销)
- [相关章节](#相关章节)
- [参考资料](#参考资料)

---
## 引言：生产 Bug

JWT 存储安全 的关键不是'防住'——是**出事后 5 分钟内能定位**。

本篇用真实生产场景切入：线上怎么炸、按官方文档写为什么也会错、怎么止血。

---

## JWT 结构

JWT 是一段**点分隔**的 Base64URL 字符串，结构为 `header.payload.signature`：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NSIsIm5hbWUiOiJBbGljZSIsImlhdCI6MTUxNjIzOTAyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
         ───── Header ─────   ─────────── Payload ───────────   ────── Signature ──────
```

### Header（头部）

声明**类型**与**签名算法**：

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload（载荷）

携带**业务数据（Claims）**，例如：

```json
{
  "sub": "1234567890",
  "name": "Alice",
  "iat": 1516239022,
  "exp": 1735689600
}
```

> 注意：Payload 仅仅是 Base64URL **编码**而非**加密**，任何人都可以解码查看内容，**不要在 Payload 中存放敏感信息**（如密码、身份证号）。

### Signature（签名）

签名用于验证消息在传输过程中**未被篡改**。生成方式：

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

---

## 标准 Claims

JWT 规范（RFC 7519）定义了一组**注册声明（Registered Claims）**：

| Claim | 名称 | 说明 | 示例 |
|-------|------|------|------|
| `iss` | Issuer | 签发者 | `https://auth.example.com` |
| `sub` | Subject | 主体（通常是用户 ID） | `user_10086` |
| `aud` | Audience | 接收方 | `mobile-app` |
| `exp` | Expiration Time | 过期时间（Unix 秒） | `1735689600` |
| `iat` | Issued At | 签发时间 | `1735686000` |
| `nbf` | Not Before | 在此时间前不可用 | `1735686000` |
| `jti` | JWT ID | 唯一标识，用于防重放 | `a1b2c3d4-...` |

> 服务端**必须验证 `exp`、`iss`、`aud`**，推荐同时校验 `nbf` 与 `iat`。

---

## 验证流程

典型的非对称签名（RS256）流程：

```
┌──────────┐                              ┌──────────┐
│  Issuer  │                              │ Verifier │
│  (AS)    │                              │  (API)   │
└────┬─────┘                              └────┬─────┘
     │                                         │
     │ 1. 用私钥 (private key) 签名 JWT        │
     │   header.payload.signature              │
     │ ──────▶ 发给客户端 ──────▶              │
     │                                         │
     │                                         │ 2. 客户端发起请求，
     │                                         │    携带 Authorization: Bearer <jwt>
     │                                         │
     │                                         │ 3. 服务端用公钥 (public key)
     │                                         │    验证签名 + 检查 exp/iss/aud
     │                                         │
```

### Java 验证示例

```java
import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.auth0.jwt.interfaces.JWTVerifier;

public class JwtVerifier {

    // 从配置中心或 JWKS 端点加载公钥
    private static final RSAPublicKey PUBLIC_KEY = loadPublicKey();

    public static DecodedJWT verify(String token) {
        Algorithm algorithm = Algorithm.RSA256(PUBLIC_KEY, null);
        JWTVerifier verifier = JWT.require(algorithm)
                .withIssuer("https://auth.example.com")    // 验证 iss
                .withAudience("mobile-app")                // 验证 aud
                .acceptLeeway(30)                          // 允许 ±30s 时钟偏差
                .build();
        return verifier.verify(token);                     // 自动验证 exp / nbf
    }
}
```

---

## 常见攻击与防御

### 1. `alg=none` 攻击

攻击者将 Header 改为 `{"alg":"none"}` 并清空签名，期望服务端"信任无签名 Token"。

**防御**：
- 服务端**白名单**允许的算法（如仅允许 `RS256`），硬编码而非读取 Token 的 `alg` 字段。
- 库层面：使用 `auth0/java-jwt` 等成熟库，不要手写解析。

### 2. HS256 / RS256 算法混淆

如果服务端先用公钥字符串当 HMAC secret 签发，攻击者用该公钥伪造 HS256 Token，可能骗过验证逻辑。

**防御**：
- 明确区分对称（HS*）与非对称（RS*/ES*）密钥，绝不混用。
- 验证时根据**预期算法**加载对应密钥。

### 3. 弱 Secret

`HS256` 依赖一个高熵的共享密钥。使用 `secret` / `123456` 这类弱 secret 会被字典攻击秒破。

**防御**：
- Secret 至少 256 bit（32 字节），使用 `openssl rand -base64 32` 生成。
- Secret 存放在 Vault / KMS，**绝不**硬编码到代码或 Git。

### 4. 不验证 `aud` / `iss` 导致跨服务 Token 重放

Token A 服务签发的 Token 被用来访问 B 服务。

**防御**：每个服务在验证时强制 `withAudience(...)` / `withIssuer(...)`。

### 5. 不绑定用户上下文

仅靠 `sub` 无法防 Token 转发（一人登录，复制 Token 给多人用）。

**防御**：将 `sub` 与 IP / 设备指纹 / 一次性 Challenge 结合。

---

## 存储方式对比

### 为什么 `localStorage` 存储 JWT 是危险的？

1. **XSS 攻击的直接靶心**
   - 任何成功注入的 XSS 脚本均可直接读取 `localStorage` 中的 Token，无需用户交互。
   - 现代前端框架（如 React/Vue）虽能防御部分 XSS，但第三方库漏洞或用户输入处理不当仍可能导致突破。

2. **CSRF 防御失效**
   - `localStorage` 无法自动随请求发送 Token，需手动添加 `Authorization` 头，导致传统 CSRF 防护机制（如同源策略、CSRF Token）失效。

3. **持久化存储风险**
   - Token 可能长期保留在浏览器中，即使用户登出，恶意脚本仍可复用。

### 存储方案对比

| 方案 | XSS 防御 | CSRF 防御 | 自动发送 | 续期难度 | 推荐度 |
|------|----------|-----------|----------|----------|--------|
| `localStorage` | ❌ 弱（脚本可读） | ❌ 需自行实现 | ❌ 需 JS 手动 | 易 | ❌ 不推荐 |
| `sessionStorage` | ❌ 弱（脚本可读） | ❌ 需自行实现 | ❌ 需 JS 手动 | 中 | ⚠ 临时方案 |
| 普通 Cookie（无 HttpOnly） | ❌ 弱 | ⚠ SameSite | ✅ 自动 | 易 | ❌ 不推荐 |
| **HttpOnly + Secure + SameSite Cookie** | ✅ 强（脚本不可读） | ✅ 强 | ✅ 自动 | 中 | ✅ **首选** |
| 内存（闭包变量） + Refresh Cookie | ✅ 强 | ✅ 强 | ❌ 需 JS | 中 | ✅ **SPA 推荐** |

### 推荐方案

#### 方案 1：HttpOnly Cookie + SameSite（首选）

```
Set-Cookie: accessToken=eyJhbGciOi...; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900
```

- 免疫 XSS 窃取（`HttpOnly` 禁止脚本访问）。
- `SameSite` 属性防御 CSRF（`Strict` 完全禁止跨站请求，`Lax` 允许部分安全导航）。
- 浏览器自动管理 Cookie 发送。

**适用场景**：传统 Web 应用、需要强安全性的管理后台。

#### 方案 2：Short-Lived JWT + Refresh Token（平衡方案）

- 存储短期有效的 Access Token（如 15 分钟）在内存（`sessionStorage` 或闭包变量）中。
- 长期有效的 Refresh Token 存储在 `HttpOnly` Cookie 中，用于静默续期。

**适用场景**：需要无感知续期的移动端 Web 应用或 SPA。

#### 方案 3：WebAuthn + Passkeys（未来趋势）

- 利用浏览器原生 API（如 `PublicKeyCredential`）实现无密码认证。
- 彻底消除密码和 Token 泄露风险。

**适用场景**：高安全性需求（如金融、医疗）或支持现代浏览器的应用。

### React + Axios 集成示例

```javascript
// 使用 Axios 拦截器自动添加 Cookie 中的 Token
axios.interceptors.request.use(config => {
  const token = document.cookie.replace(/(?:(?:^|.*;\s*)accessToken\s*\=\s*([^;]*).*$)|^.*$/, '$1');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 登出时清除 Cookie（需服务端配合设置过期时间）
function logout() {
  document.cookie = 'accessToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}
```

### 安全增强措施

- **CSP (Content Security Policy)**：限制脚本来源，降低 XSS 成功率。
- **Token 加密**：对存储在 Cookie 中的 Token 进行服务端加密（如 JWE）。
- **IP/设备指纹绑定**：服务端校验 Token 的使用环境是否异常。

---

## Token 撤销

JWT 一旦签发，在过期前**默认无法撤销**——这既是其优势（无状态、性能高），也是其劣势。常见应对策略：

### 1. 短 TTL + Refresh Token

- Access Token TTL 控制在 5–30 分钟。
- Refresh Token TTL 较长（如 7–30 天），用于静默续期。
- 泄露后最多损失"短窗口"内的访问权。

### 2. 黑名单（Blocklist）

- 维护一个 Redis 黑名单，登出 / 改密码时将 jti 写入。
- 每次请求检查 `jti` 是否在黑名单中（牺牲部分无状态性）。

```java
public boolean isRevoked(String jti) {
    return Boolean.TRUE.equals(
        redisTemplate.hasKey("jwt:revoked:" + jti));
}
```

### 3. Refresh Token Rotation

- 每次使用 Refresh Token 换取新的 Access Token 时，**同步作废旧 Refresh Token 并签发新 Refresh Token**。
- 若服务端检测到旧 Refresh Token 被复用，判定为 Token 失窃，吊销该用户所有会话。

### 4. 版本号 / 凭据版本（`tokenVersion`）

- 在用户表中维护 `token_version`，JWT 中携带 `tv` claim。
- 用户改密码 / 踢出时 `tv++`，旧 Token 自然失效。
- 验证时需调用一次用户服务查 `tv`，是有状态的。

### 选型建议

| 场景 | 推荐策略 |
|------|----------|
| 普通 Web / 移动 App | 短 TTL（15min）+ Refresh Token Rotation |
| 高安全（金融/支付） | 短 TTL + 黑名单 + 设备/IP 绑定 |
| 用户主动登出 | 短 TTL 自动失效 + 黑名单加速 |
| 改密 / 权限变更 | `token_version` / 黑名单 |

---

## 相关章节

- [OAuth2.0 与 OIDC](../oauth2-oidc/README.md) — Access Token 的签发与使用流程
- [API 安全](../api-security/README.md) — Token 传输、签名验证、防重放
- [权限模型 RBAC / ABAC](../access-control/02-role-and-attribute/README.md) — Token 中的角色 / 权限声明如何消费
- [Spring Cloud Gateway JWT 鉴权实现](../../../06.spring/05-spring-cloud/gateway.md) — 网关层 JWT 校验 Filter 的 Java 实现示例

---

## 参考资料

- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [RFC 8725 - JSON Web Token Best Current Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP JSON Web Token Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [auth0/java-jwt](https://github.com/auth0/java-jwt)

← [返回: 系统设计 · jwt-security](README.md)
