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
| HTTP 缓存机制 | 📝 速查 | 详见 [12.interview/09.front-end/http-cache](../../../../note/12.interview/09.front-end/http-cache/) |
| HTTPS 握手 | 📝 速查 | 详见 [12.interview/09.front-end/https-handshake](../../../../note/12.interview/09.front-end/https-handshake/) |
| CORS 跨域 | 📝 速查 | 详见 [07-security/cors](../../07-security/cors/) |

### 学习路径

- **入门**：HTTP 方法语义（GET / POST / PUT / DELETE）→ 缓存机制
- **进阶**：HTTPS 握手 → 跨域（CORS 预检）
- **实战**：浏览器 DevTools Network 面板分析请求

---

## 与其他模块的关系

- **上游**：[`02.computer-basics/01-network`](../../../../note/02.cs-foundations/01-network/) — HTTP 协议族（TCP/IP / DNS / TLS）
- **横向**：[`07-security`](../../07-security/) — CORS / CSRF / CSP 安全相关
- **下游**：[`05-architecture/bff`](../../05-architecture/bff/) — BFF 层网络优化

---

## 📊 本节统计

- **子 README 数**：1
- **数据快照**：2026-08

---

← [返回前端工程总览](../README.md)