<!--
module:
  parent: front-end
  slug: front-end/sessions
  type: article
  category: 主模块子文章
  summary: Cookies vs LocalStorage 会话管理
-->

# Cookies vs LocalStorage 用于会话管理：你需要知道的一切

---

**原文链接**：[https://supertokens.com/blog/cookies-vs-localstorage-for-sessions-everything-you-need-to-know](https://supertokens.com/blog/cookies-vs-localstorage-for-sessions-everything-you-need-to-know)

> 📌 **本文与 [`13.split-hairs/09.front-end/storage/`](../../../13.split-hairs/09.front-end/storage/README.md/) 的关系**
>
> - 本文档是**原文完整翻译稿**(SuperTokens, 2023),系统讲述 Cookies / LocalStorage / SessionStorage / IndexedDB 四种浏览器存储在会话管理中的取舍,是一篇**通识性的工程实践**。
> - `13.split-hairs/09.front-end/storage/` 是**「咬文嚼字」小专题**,聚焦面试 / 辨析场景,常以「**X 和 Y 区别?**」表格对照形式出现。
> - **阅读建议**:工程落地看本文,面试 / 快速对比看 split-hairs。如发现 split-hairs 里有更精简的结论,可以反向回流到本文校对。

## 引言
在 Web 开发中，我们有多种方式来存储数据。其中，Cookies 和 LocalStorage API 是最常用的两种。本文将深入探讨它们分别是什么、各自的用途，以及如何在身份验证和会话管理（Session Management）中正确使用它们。

## 浏览器中存储数据的多种方式
在深入了解 Cookies 和 LocalStorage 之前，我们先来看看现代浏览器中可用的数据存储方式：

| 存储方式 | 类型 | 描述 | 存储限制 | 持久性 |
| --- | --- | --- | --- | --- |
| **Cookies** | 标准 | 浏览器存储的小块数据，会随每次 HTTP 请求发送回服务器。主要用于会话管理、身份验证和追踪用户行为。 | 每个 Cookie 约 4KB | 可设置过期时间；可以是基于会话的或持久的。 |
| **Local Storage** | 标准 | 浏览器中的键值对存储，即使关闭浏览器数据也会保留。适合存储需要跨会话持久化的小量数据。 | 每个域名约 5-10MB | 持久化，直到被显式删除。 |
| **Session Storage** | 标准 | 类似于 Local Storage，但数据仅在页面会话期间有效。关闭页面或标签页后数据会被清除。 | 每个域名约 5-10MB | 基于会话。 |
| **IndexedDB** | 标准 | 用于存储大量结构化数据（包括文件和 blob）的低级 API。支持事务、搜索和索引。 | 取决于浏览器实现，通常为数 GB | 持久化，直到被显式删除。 |

*注：WebSQL 已被弃用，而 File System Access API 是相对较新的标准。通常建议使用广泛支持的标准（如 Cookies, Local Storage, Session Storage 和 IndexedDB）。*

## 什么是 Cookies？
Cookies 的历史非常悠久（诞生于 1994 年，1995 年被广泛接受）。简单来说，Cookies 是 Web 服务器在用户浏览网站时创建，并由浏览器放置在用户设备上的小块数据。

在 Web 早期，每个 Cookie 4096 字节（约 4KB）的容量已经相当不错了。但随着 Web 应用变得越来越复杂，4KB 的限制显得捉襟见肘。开发者要么限制自己的存储需求，要么拼凑多个 Cookie（依然受限），或者干脆把存储的难题交给服务器。为了解决这些限制，LocalStorage 应运而生。

## 什么是 LocalStorage？
LocalStorage（严格来说是 Web Storage 规范中的 `localStorage` 部分）作为 HTML5 规范的一部分被引入，旨在解决 Cookies 的一些限制（最明显的就是存储容量）。

与每次 HTTP 请求都会携带的 Cookies 不同，LocalStorage 允许 Web 应用在浏览器中存储更多的数据。它的核心优势在于**存储容量**——不再局限于几千字节，而是允许每个域名存储约 5 到 10 MB 的数据。

这使得 LocalStorage 非常适合存储那些**不需要在每次请求时发送给服务器**的持久化数据，例如用户偏好设置、UI 状态等。

## Cookies 与 LocalStorage 的核心差异

| 特性 | Cookies | Local Storage |
| --- | --- | --- |
| **存储容量** | 每个 Cookie 约 4KB | 每个域名约 5-10MB |
| **过期时间** | 可设置过期时间；支持会话级或持久化 | 持久化，直到被显式删除 |
| **数据传输** | 随每次 HTTP 请求发送到服务器 | 不随 HTTP 请求发送，仅限客户端 |
| **可访问性** | 客户端和服务器端均可访问 | 仅限客户端访问 |
| **安全性** | 易受 XSS 攻击；可标记为 `HttpOnly` 和 `Secure` 以降低风险 | 易受 XSS 攻击；不适合存储敏感数据 |
| **API** | `document.cookie`（手动处理）；通过 HTTP 头设置/获取 | `localStorage.setItem()` 和 `localStorage.getItem()` |
| **作用域** | 可通过 domain 和 path 属性跨子域名和协议访问 | 限定在特定的域名和协议（源）内 |

### API 使用示例
**Cookies API** 相对古老且不够友好：
```javascript
// 设置 Cookie
document.cookie = "username=JohnDoe; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/";

// 获取 Cookie
let allCookies = document.cookie;
// 需要手动解析字符串来获取特定值...
```
*(幸运的是，现在有很多优秀的库如 `js-cookie` 可以简化这一过程。)*

**LocalStorage API** 则现代且简洁得多：
```javascript
// 设置数据
localStorage.setItem("username", "JohnDoe");

// 获取数据
let username = localStorage.getItem("username"); 
```
*注意：LocalStorage 只能存储字符串。如果要存储对象或数组，需要使用 `JSON.stringify()` 和 `JSON.parse()` 进行序列化和反序列化。*

## 会话存储场景下的对比（核心重点）

在身份验证和会话管理（Session Storage）这一特定场景下，Cookies 和 LocalStorage 的表现有着天壤之别。

### 何时使用 Cookies 存储会话数据？
在大多数情况下，**Cookies 是存储会话数据的推荐选择**，尤其是在安全性至关重要的场景中。

1. **安全的身份验证**：如果你要管理用户身份验证，应该使用 Cookies 存储会话 Token。`HttpOnly` 标志可以确保页面上的 JavaScript 无法访问该 Cookie，从而大幅降低 XSS（跨站脚本）攻击的风险。`Secure` 标志则保证 Cookie 仅通过 HTTPS 发送，防止在不安全的连接中暴露。
2. **服务端会话管理**：由于 Cookies 会自动随每次请求发送到服务器，它们是传统服务端会话管理的理想选择。
3. **跨子域名共享**：如果你的应用跨越多个子域名（例如 `shop.yoursite.com` 和 `auth.yoursite.com`），Cookies 允许通过设置 `Domain` 属性在这些子域名之间无缝共享会话 Token。
4. **防范 XSS 和 CSRF**：通过结合使用 `HttpOnly`、`Secure` 和 `SameSite` 标志，Cookies 可以最大程度地缩小攻击面，有效缓解 XSS 和 CSRF（跨站请求伪造）攻击。

**结论**：任何与身份验证（Auth）相关的数据，都应该放在 Cookie 中。

### 何时使用 LocalStorage 存储会话数据？
LocalStorage 也可以用于会话存储，但**这种方式通常安全性较低**。只有在 XSS 风险极小或会话数据不敏感的情况下才应考虑使用。

1. **单页应用（SPAs）**：如果你正在构建一个纯客户端应用，需要会话 Token 在页面刷新后保留，但不需要随每次 HTTP 请求发送，LocalStorage 可能是一个更直接的方案。但必须高度警惕 XSS 风险。
2. **短生命周期的非敏感会话**：适用于单次用户交互或同一会话后即丢弃的 Token。
3. **本地缓存**：用于存储提升用户体验的非敏感数据（如购物车数据、UI 状态），避免重复从服务器获取。
4. **离线使用**：对于离线优先的应用，LocalStorage 可以在用户断网时临时保存会话 Token，直到重新连接。

**结论**：任何对客户端很重要的设置或状态都可以放在 LocalStorage 中。虽然你可以把会话数据存在 LocalStorage 中，但**通常情况下应尽量避免这样做**。

## 总结

* **Cookies** 凭借其缓解 XSS 和 CSRF 攻击的能力（通过 `HttpOnly`、`Secure` 和 `SameSite` 等标志），是**安全会话管理和身份验证的首选**。
* **LocalStorage** 最适合用于 SPA 中的**客户端状态管理和非敏感会话数据**。但由于其面临的安全风险，**强烈不建议**使用 LocalStorage 来存储身份验证 Token。

---

## 🔗 配套章节

- 🆕 [JWT 安全深度](../../../../04.system-design/05-security/jwt-security/README.md) —— 「为什么 localStorage 存 JWT 是危险的」+ 6 大方案对比表 + HttpOnly Cookie 首选 + 双 Token（内存 + Refresh Cookie）实战代码
- 🆕 [前端存储方式（咬文嚼字）](../../../../../13.split-hairs/09.front-end/storage/README.md) —— 4 种存储对比 + 场景化推荐（用户认证与会话管理 → Cookie + HttpOnly）

---

← [返回 前端安全](../README.md)