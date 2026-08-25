<!--
module:
  parent: 05.frontend
  slug: 05.frontend/03-network
  type: index
  category: 主模块子 MOC
  summary: 前端网络协议与请求机制（HTTP/HTTPS / WebSocket / 跨域 / 缓存）
-->

# 03 网络

> 前端视角的网络协议层——从 HTTP 方法、缓存机制到跨域、安全握手，是浏览器与服务器交互的协议基础。

---

## 主题导航

| 主题 | 状态 | 说明 |
|------|------|------|
| [HTTP 协议 · GET vs POST](http-protocol/get-vs-post.md) | ✓ 已有 | 9 大差异 + 幂等性 + 语义本质 |
| HTTP 缓存机制 | 📝 速查 | 详见 [12.interview/09.front-end/http-cache](../../12.interview/09.front-end/http-cache/) |
| HTTPS 握手 | 📝 速查 | 详见 [12.interview/09.front-end/https-handshake](../../12.interview/09.front-end/https-handshake/) |
| CORS 跨域 | 📝 速查 | 详见 [07-security/cors](../07-security/cors/) |

**速读概述（免跳转）**：

- **HTTP 缓存**：两级策略——强缓存（`Cache-Control: max-age`，不发请求）+ 协商缓存（`ETag` / `Last-Modified`，304 省 body）。典型配置：HTML 走 `no-cache`（每次协商），带 hash 的 JS/CSS 走 `max-age=31536000, immutable`
- **HTTPS 握手**：TLS 1.2 = 2-RTT（RSA/ECDHE + 证书校验）；TLS 1.3 = 1-RTT + 0-RTT 恢复。前端可见收益：HSTS 防降级、证书错误页排查（域名/有效期/链不全三类）
- **CORS**：浏览器同源策略放行机制。简单请求直接带 `Origin`；非简单（自定义头 / `PUT` / `application/json`）先发 `OPTIONS` 预检。凭证请求需 `Access-Control-Allow-Credentials` + 服务端精确回显 `Origin`（不能 `*`）

### 学习路径

- **入门**：HTTP 方法语义（GET / POST / PUT / DELETE）→ 缓存机制
- **进阶**：HTTPS 握手 → 跨域（CORS 预检）
- **实战**：浏览器 DevTools Network 面板分析请求
- **性能**：Resource Timing API（`performance.getEntriesByType('resource')` 拿每个请求的分阶段耗时）→ Navigation Timing（导航全链路）→ DevTools Network 的 Waterfall 定位慢请求（DNS / TCP / TTFB / Content Download 分段）

## 核心概念速查：HTTP 方法对比

| 方法 | 语义 | 幂等 | 安全 | Body |
|------|------|------|------|------|
| GET | 读取 | ✓ | ✓ | 规范不推荐（参数走 query） |
| POST | 创建/提交 | ✗ | ✗ | ✓ |
| PUT | 整体替换 | ✓ | ✗ | ✓ |
| PATCH | 局部更新 | ✗（实现相关） | ✗ | ✓ |
| DELETE | 删除 | ✓ | ✗ | 可选 |

> 面试考点：幂等 = 多次执行结果一致（网络重试安全的前提）；安全 = 无副作用。浏览器重试只会自动重发安全方法。

## 浏览器环境差异提示

- **Service Worker 拦截**：SW 可拦截同源请求返回缓存/合成响应，Network 面板显示 `(ServiceWorker)` 来源——排查"接口改了没生效"先看 SW 缓存策略
- **SSR 场景**：服务端 `fetch` 不会自动携带浏览器 Cookie（无 Cookie 概念），需手动透传 `Cookie` 头；且服务端无 `window`，涉及浏览器 API 的拦截器要分支处理
- **缓存三处位置**：Memory Cache（页面生命周期）→ Disk Cache（跨页面）→ Service Worker Cache（显式控制），DevTools 的 `from cache` 需结合 Size 列判断来源

---

## 与其他模块的关系

- **上游**：[`02.cs-foundations/03-network`](../../02.cs-foundations/03-network/README.md) — HTTP 协议族（TCP/IP / DNS / TLS）
- **横向**：[`07-security`](../07-security/README.md) — CORS / CSRF / CSP 安全相关
- **下游**：[`05-architecture/bff`](../05-architecture/bff/README.md) — BFF 层网络优化

---

## 📊 本节统计

- **子 README 数**：1
- **数据快照**：2026-08

---

← [返回前端工程总览](../README.md)