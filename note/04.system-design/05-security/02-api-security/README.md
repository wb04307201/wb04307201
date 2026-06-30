<!--
module:
  parent: system-design
  slug: system-design/02-api-security
  type: article
  category: 主模块子文章
  summary: 一份按层次梳理的 API 安全速查手册：从认证到限流的 7 层防护完整实战。
-->

# API 安全：认证 / 授权 / 限流 完整实战

> 一份按层次梳理的 API 安全速查手册：从认证到限流的 7 层防护完整实战。

---
## 引言：生产 Bug（[AUTO] 自动生成，待人工 review）

API 安全：认证 / 授权 / 限流 完整实战 的一份按层次梳理的 API 安全速查手册：从认证到限流的 7 层防护完整实战

**但实际**：常被攻击或出 Bug 后背锅。本篇用'生产场景'切入：
线上怎么炸、有没有上线过的坑、为什么按官方文档写也会错。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、API 安全的 7 层防护

```
┌─────────────────────────────────────┐
│  1. 传输层：HTTPS / TLS 1.2+          │
├─────────────────────────────────────┤
│  2. 认证层：你是谁？OAuth2 / JWT      │
├─────────────────────────────────────┤
│  3. 授权层：你能做什么？RBAC / ABAC  │
├─────────────────────────────────────┤
│  4. 审计层：日志 + 监控              │
├─────────────────────────────────────┤
│  5. 输入层：参数验证 / 防注入        │
├─────────────────────────────────────┤
│  6. 限流层：防刷 / 防 DDoS            │
├─────────────────────────────────────┤
│  7. 响应层：错误处理 / 防泄漏        │
└─────────────────────────────────────┘
```

---

## 二、认证（Authentication）：你是谁？

### 2.1 4 大认证方式对比

| 方式 | 适用 | 优点 | 缺点 |
|------|------|------|------|
| **Session + Cookie** | 传统 Web | 简单 | 不适合移动端 / 跨域 |
| **JWT（Token）** | 现代 API / 移动端 | 无状态 / 跨域 | Token 撤销难 |
| **OAuth2 / OIDC** | 第三方授权（微信登录） | 标准协议 | 流程复杂 |
| **API Key** | 服务间调用 | 简单 | 安全性低 |

### 2.2 JWT 结构

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkphbmUgRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

```
Header:  {"alg":"HS256","typ":"JWT"}
Payload: {"sub":"1234567890","name":"Jane","iat":1516239022}
Signature: HMACSHA256(base64(header) + "." + base64(payload), secret)
```

### 2.3 JWT 最佳实践

```java
// 1. 不要在 JWT 里存敏感信息（payload 只 base64 编码，不加密）
// 2. 使用强密钥（HS256 至少 32 字节）
// 3. 设置合理的过期时间（access 15min，refresh 7d）
// 4. 使用 refresh token 机制
// 5. 重要操作要二次验证
```

---

## 三、授权（Authorization）：你能做什么？

### 3.1 RBAC vs ABAC

| 模型 | 描述 | 适用 |
|------|------|------|
| **RBAC**（基于角色）| 权限绑定到角色 | 中小系统 |
| **ABAC**（基于属性）| 权限根据属性动态计算 | 复杂系统 |
| **PBAC**（基于策略）| 用 DSL（如 OPA）描述策略 | 云原生 |

### 3.2 RBAC 实现

```sql
-- 5 张表
users（用户）
roles（角色）
permissions（权限）
user_roles（用户-角色）
role_permissions（角色-权限）
```

```java
// 检查用户是否有权限
if (user.hasRole("ADMIN") && user.hasPermission("user:delete")) {
  // 允许删除
}
```

### 3.3 ABAC 示例

```java
// 不仅看角色，还看属性
if (user.getDepartment().equals(document.getOwnerDepartment())
    && document.getStatus().equals("DRAFT")
    && time.isBusinessHour()) {
  // 允许编辑
}
```

---

## 四、限流（Rate Limiting）：防刷 + 防 DDoS

### 4.1 4 大限流算法

| 算法 | 原理 | 适用 |
|------|------|------|
| **固定窗口** | 每分钟重置计数 | 简单场景 |
| **滑动窗口** | 滑动时间窗 | 推荐 |
| **令牌桶** | 匀速生成令牌 | 突发流量 |
| **漏桶** | 匀速漏出 | 严格限速 |

### 4.2 Redis + Lua 限流（生产推荐）

```lua
-- sliding_window.lua
local key = KEYS[1]
local window = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
local current = redis.call('INCR', key)
if current == 1 then
  redis.call('EXPIRE', key, window)
end
if current > limit then
  return 0
end
return 1
```

```java
// Java 调用
public boolean allowRequest(String userId) {
  String key = "rate:" + userId;
  Long result = redisTemplate.execute(luaScript,
      Collections.singletonList(key),
      "60", "100");  // 60 秒最多 100 次
  return result == 1;
}
```

### 4.3 网关层限流（Sentinel / Spring Cloud Gateway）

```yaml
# Spring Cloud Gateway 限流
spring:
  cloud:
    gateway:
      routes:
      - id: api_route
        uri: lb://my-service
        filters:
        - name: RequestRateLimiter
          args:
            redis-rate-limiter.replenishRate: 100
            redis-rate-limiter.burstCapacity: 200
```

---

## 五、API Key 管理（服务间认证）

### 5.1 生成与存储

```java
// 生成强随机 API Key
String apiKey = Base64.getUrlEncoder().withoutPadding()
    .encodeToString(SecureRandom.getInstanceStrong().generateSeed(32));

// 存储：数据库只存 hash（不存明文）
String apiKeyHash = BCrypt.hashpw(apiKey, BCrypt.gensalt());
db.save(new ApiKey(apiKeyHash, ownerId, scope, expiresAt));
```

### 5.2 验证

```java
public boolean verifyApiKey(String apiKey) {
  // 用数据库 hash 验证（不直接查询）
  ApiKey record = db.findByHashPrefix(apiKey.substring(0, 8));
  if (record == null) return false;
  return BCrypt.checkpw(apiKey, record.getHash());
}
```

### 5.3 Key 轮转

- 每 90 天轮转一次
- 支持多 Key 并行（灰度切换）
- 立即吊销机制

---

## 六、HTTPS 配置（传输安全）

### 6.1 Nginx HTTPS 配置

```nginx
server {
  listen 443 ssl http2;
  server_name api.example.com;

  ssl_certificate     /etc/nginx/ssl/example.com.crt;
  ssl_certificate_key /etc/nginx/ssl/example.com.key;
  ssl_protocols       TLSv1.2 TLSv1.3;
  ssl_ciphers         HIGH:!aNULL:!MD5;

  # HSTS
  add_header Strict-Transport-Security "max-age=31536000" always;
  add_header X-Frame-Options "SAMEORIGIN" always;
}
```

### 6.2 证书自动续期（Let's Encrypt）

```bash
# 安装 certbot
apt-get install certbot python3-certbot-nginx

# 自动申请 + 续期
certbot --nginx -d api.example.com
```

---

## 七、API 输入验证

### 7.1 Jakarta Validation（Java）

```java
@PostMapping("/users")
public ResponseEntity<?> createUser(@Valid @RequestBody CreateUserRequest req) {
  // ...
}

@Data
public class CreateUserRequest {
  @NotBlank
  @Size(min = 3, max = 20)
  private String username;

  @Email
  @NotBlank
  private String email;

  @Min(0) @Max(150)
  private Integer age;

  @Pattern(regexp = "^[a-zA-Z0-9]+$")
  private String password;
}
```

### 7.2 防 SQLi / NoSQLi

```java
// ✅ 参数化（MyBatis）
@Select("SELECT * FROM users WHERE username = #{username}")
User findByUsername(@Param("username") String username);

// ❌ 字符串拼接（危险）
@Select("SELECT * FROM users WHERE username = '" + username + "'")
```

### 7.3 防 Mass Assignment（批量赋值）

```java
// ✅ 显式绑定字段
public class UpdateUserRequest {
  private String username;
  private String email;
  // 不暴露 role / isAdmin
}

// ❌ 直接绑定整个对象
public void updateUser(@RequestBody User user) {
  // 攻击者可传 {"role":"admin"} 越权
  userRepository.save(user);
}
```

---

## 八、错误处理（不泄漏信息）

### 8.1 反例（泄漏细节）

```json
{
  "error": "SQLException: column 'password' doesn't exist at line 1, query was SELECT * FROM users WHERE...",
  "stackTrace": "java.sql.SQLException: ...\n\tat com.example.UserService.find..."
}
```

### 8.2 正例（统一错误响应）

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "用户不存在",
    "requestId": "req-abc123"
  }
}
```

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

  @ExceptionHandler(UserNotFoundException.class)
  public ResponseEntity<?> handleNotFound(UserNotFoundException e) {
    return ResponseEntity.status(404).body(Map.of(
      "error", Map.of(
        "code", "USER_NOT_FOUND",
        "message", "用户不存在",
        "requestId", MDC.get("requestId")
      )
    ));
  }

  @ExceptionHandler(Exception.class)
  public ResponseEntity<?> handleGeneric(Exception e) {
    log.error("Unexpected error", e);
    return ResponseEntity.status(500).body(Map.of(
      "error", Map.of("code", "INTERNAL_ERROR", "message", "系统异常")
    ));
  }
}
```

---

## 九、API 安全检查清单

```
✅ HTTPS 全站（TLS 1.2+）
✅ 强认证（JWT / OAuth2 / MFA）
✅ 最小权限（RBAC / ABAC）
✅ 输入验证（白名单 + 大小限制）
✅ 防 SQLi / XSS / CSRF
✅ 限流（网关 + Redis 滑动窗口）
✅ 审计日志（所有 API 调用记录）
✅ 错误处理（不泄漏细节）
✅ 依赖扫描（SCA + SAST）
✅ 渗透测试（每年）
```

---

## 十、最佳实践

1. **HTTPS 全站**：禁用 HTTP，启用 HSTS
2. **JWT 短期 access + 长期 refresh**：access 15min，refresh 7d
3. **限流分层**：网关（粗）+ 服务（细）
4. **错误统一处理**：不泄漏堆栈 / SQL
5. **API Key 存 hash**：不存明文
6. **审计日志**：登录、权限变更、敏感操作必记
7. **依赖扫描**：CI 用 Snyk / Trivy
8. **定期渗透测试**：至少每年一次

---

← [返回系统设计总览](../../README.md) · 📅 2026-06-28