<!--
module:
  parent: front-end
  slug: front-end/network/websocket
  type: article
  category: 主模块子文章
  summary: WebSocket 浏览器-服务器双向通信协议，基于 HTTP Upgrade。5 大特性 + 4 种应用场景 + 4 大实现库（SockJS / ws / Socket.IO / Spring WebSocket）+ vs SSE 对比。
  depth: ⭐⭐⭐
-->

# WebSocket

> **一句话定位**：WebSocket 是浏览器-服务器**全双工**通信协议（基于 HTTP Upgrade 升级），实时聊天/推送/协同编辑首选。

---

## 一、为什么需要 WebSocket？

| HTTP 限制 | WebSocket 解决方案 |
|----------|-----------------|
| 请求-响应单向 | **全双工**：服务端可主动发消息 |
| 每次重新建连 | **长连接**：1 次握手复用 |
| 实时性差（轮询延迟）| **毫秒级延迟** |
| Header 重复传输 | **帧头小**（2-14 字节）|

## 二、协议核心

**握手阶段**：HTTP Upgrade 升级
```
GET /chat HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

**响应**：
```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

**数据传输阶段**：WebSocket Frames（文本/二进制）

## 三、5 大特性

| 特性 | 说明 |
|------|------|
| **全双工** | 双向通信 |
| **长连接** | 1 次握手永久 |
| **低开销** | 帧头 2-14 字节 |
| **跨域** | 支持 CORS |
| **子协议** | 可指定 STOMP/MQTT 等 |

## 四、4 种应用场景

| 场景 | 示例 |
|------|------|
| **实时聊天** | 微信 Web、Slack |
| **实时推送** | 股票报价、体育比分 |
| **协同编辑** | Google Docs、Notion |
| **在线游戏** | 多人对战、棋牌 |

## 五、4 大实现库

| 库 | 语言 | 特性 |
|----|------|------|
| **ws** | Node.js | 最流行，零依赖 |
| **Socket.IO** | Node.js | 封装 WebSocket + 降级（兼容老浏览器）|
| **SockJS** | 浏览器/Node | 降级方案（XHR 长轮询/EventSource）|
| **Spring WebSocket** | Java | Spring Boot 集成 STOMP |

## 六、WebSocket vs SSE

| 维度 | WebSocket | SSE（Server-Sent Events）|
|------|----------|------------------------|
| 方向 | **全双工** | 单向（服务端→客户端）|
| 协议 | 独立（基于 HTTP Upgrade）| HTTP |
| 浏览器兼容 | IE10+ | IE 不支持 |
| 自动重连 | ❌ 需手动实现 | ✅（EventSource 内置）|
| 适用 | 聊天、协同 | 推送、通知 |

**反直觉**：80% 的"实时通知"用 SSE 就够，不需要 WebSocket。

## 七、生产踩坑

| 坑 | 现象 | 修复 |
|----|------|------|
| **Nginx 代理断开** | 60 秒无消息连接断开 | `proxy_read_timeout 3600s;` |
| **心跳缺失** | 路由器/防火墙超时 | 30s ping/pong |
| **消息顺序错乱** | 多连接并发 | 单连接 + 序号 |
| **断线无感** | 用户不知已掉线 | 客户端自动重连 + 服务端心跳 |

## 八、面试 Q&A

**Q: WebSocket 和 HTTP 长轮询区别？**

A：
| 维度 | WebSocket | HTTP 长轮询 |
|------|----------|------------|
| 实时性 | 毫秒 | 秒（轮询间隔） |
| 服务器推送 | ✅ 原生 | 需 keep-alive |
| 资源占用 | 1 长连接 | 多次请求 |
| 复杂度 | 中 | 低 |

**Q: 何时不用 WebSocket？**

A：3 个场景：
1. **简单 GET/POST**：REST 足够
2. **公网 + 浏览器兼容性差**：用 SSE 或轮询
3. **服务器集群**：WebSocket 需 sticky session（除非用 Redis Pub/Sub）

## 九、相关章节

- [HTTP 协议详解](../http-protocol/README.md) — WebSocket 升级基础
- [SSE vs WebSocket 对比](../../../02.cs-foundations/03-network/protocols/sse-vs-websocket/README.md) — 选型
- [前端实时方案总览](../../README.md) — 实时方案对比

← [返回前端网络](../README.md)