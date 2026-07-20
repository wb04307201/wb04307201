<!--
module:
  parent: computer-basics
  slug: computer-basics/network/protocols/sse-vs-websocket
  type: article
  category: 主模块子文章
  summary: SSE vs WebSocket 协议深度对比——连接建立、数据帧、重连机制与 AI 时代的选型。
-->

# SSE vs WebSocket —— 协议深度对比

← 返回 [网络协议](../README.md)

> SSE 和 WebSocket 都是实时通信技术，但底层协议、连接模型、重连机制截然不同。本文从协议层面深度对比两者。

---
---

## 一、核心结论（TL;DR）

| 维度 | SSE | WebSocket |
|------|-----|-----------|
| **协议** | HTTP/1.1 长连接（`Transfer-Encoding: chunked`） | 独立协议（RFC 6455），通过 HTTP Upgrade 握手 |
| **连接建立** | 普通 HTTP 请求，`Accept: text/event-stream` | HTTP GET + `Upgrade: websocket` → 101 Switching Protocols |
| **数据帧** | 文本格式（`data:` / `event:` / `id:` / `retry:`） | 二进制帧（2-14 字节帧头 + payload） |
| **重连** | 浏览器内置（`Last-Event-ID` 自动续传） | 无内置，需自行实现 |
| **HTTP/2 兼容** | ✅ 天然支持（多路复用） | ⚠️ 每个 WebSocket 独占一个 TCP 连接 |

---

## 二、连接建立过程对比

### SSE：标准 HTTP 请求

```text
Client → Server:
GET /api/events HTTP/1.1
Host: example.com
Accept: text/event-stream
Cache-Control: no-cache

Server → Client:
HTTP/1.1 200 OK
Content-Type: text/event-stream
Transfer-Encoding: chunked
Cache-Control: no-cache
Connection: keep-alive

data: first message

data: second message
...（连接保持，持续推送）
```

**关键**：SSE 就是一个**永远不结束的 HTTP 响应**。服务器用 `Transfer-Encoding: chunked` 持续发送数据块。

### WebSocket：协议升级

```text
Client → Server:
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

Server → Client:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=

（之后切换为 WebSocket 二进制帧协议）
```

**关键**：WebSocket 先用 HTTP 握手，然后**协议升级**为独立的二进制帧协议。升级后不再是 HTTP。

---

## 三、数据帧格式对比

### SSE 帧格式（纯文本）

```text
event: message        ← 事件类型（可选）
id: 42                ← 事件 ID（可选，用于重连）
retry: 3000           ← 重连间隔毫秒（可选）
data: {"text":"你好"} ← 数据（必填，可多行）
                      ← 空行 = 帧结束
```

**特点**：
- 纯文本，人可读
- 每帧以 `\n\n` 结束
- `data:` 可以出现多次（拼接为一条消息）
- 只能发文本（二进制需 Base64 编码）

### WebSocket 帧格式（二进制）

```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+---+-+-+-------------+-------------------------------+
|F|R|R|R| opcode|M|P| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|Y|             |   (if payload len==126/127)   |
| |1|2|3|       |K|L|             |                               |
+-+-+-+-+-+-+-+-+---+-+-+-------------+ - - - - - - - - - - - - - -+
|     Masking-key (0 or 4 bytes)      |      Payload Data         |
+-------------------------------------+ - - - - - - - - - - - - - +
```

**特点**：
- 二进制帧，人不可读
- 帧头 2-14 字节（FIN + opcode + mask + length）
- 支持 4 种帧类型：文本（0x1）、二进制（0x2）、关闭（0x8）、Ping/Pong（0x9/0xA）
- 客户端发送必须 mask，服务器发送不 mask

---

## 四、重连机制对比

### SSE：内置自动重连

```text
连接断开
  ↓
浏览器等待 retry 毫秒（默认 ~3 秒）
  ↓
自动重连，请求头带上：
  Last-Event-ID: 42
  ↓
服务器收到 Last-Event-ID，从 ID=43 开始发送
  ↓
客户端无缝恢复
```

**代码层面零成本**——浏览器 EventSource API 自动处理所有重连逻辑。

### WebSocket：需自行实现

```text
连接断开
  ↓
应用层检测到 ws.onclose 事件
  ↓
自行编写重连逻辑：
  - 指数退避（1s → 2s → 4s → 8s...）
  - 最大重试次数
  - 心跳检测（Ping/Pong 帧）
  ↓
重新建立 WebSocket 连接（完整握手）
  ↓
自行恢复消息状态（需应用层序号机制）
```

---

## 五、代理 / 负载均衡 / CDN 影响

| 基础设施 | SSE 表现 | WebSocket 表现 |
|---------|---------|--------------|
| **Nginx 反向代理** | ✅ 默认支持 HTTP 长连接 | ⚠️ 需配置 `proxy_http_version 1.1` + `proxy_set_header Upgrade` + `proxy_read_timeout` |
| **AWS ALB** | ✅ 需设 idle timeout > SSE 间隔 | ⚠️ 需要配置 WebSocket 支持 |
| **CloudFlare CDN** | ✅ HTTP 响应正常缓存 | ⚠️ 需要开启 WebSocket 支持（Enterprise） |
| **企业防火墙** | ✅ 走 443 HTTPS | ❌ 很多防火墙拦截 Upgrade 请求 |
| **HTTP/2 多路复用** | ✅ 多个 SSE 流共享一个 TCP 连接 | ❌ 每个 WebSocket 独占一个 TCP 连接 |

**关键**：HTTP/2 下 SSE 特别高效 —— 多个 SSE 流可以在同一个 TCP 连接上多路复用，而 WebSocket 无法利用 HTTP/2。

---

## 六、选型决策树

```text
你的场景是什么？
│
├─ 纯文本流式输出（ChatGPT 式问答/通知/行情）
│   └─ SSE ✅
│       理由：简单、重连内置、代理友好、HTTP/2 多路复用
│
├─ AI 需要工具调用（Function Calling）/ 多轮 Agent
│   └─ SSE + HTTP POST ✅（不是 WebSocket！）
│       理由：MCP 协议就是这个模式，SSE 推送工具事件 + POST 返回结果
│
├─ 双向实时通信（聊天/协作编辑/游戏）
│   └─ WebSocket ✅
│       理由：双向、低延迟、二进制帧
│
├─ 音视频流
│   └─ WebRTC ✅
│       理由：P2P + 低延迟媒体传输
│
└─ 低频通知（每分钟几次）
    └─ 长轮询 / 短轮询
        理由：最简单，无需长连接
```

### 大厂真实选型原则

| 场景 | 选型 | 理由 |
|------|------|------|
| AI 对话（含 Function Calling / Agent / MCP） | **SSE + HTTP POST** | ChatGPT/Claude/MCP 都是这个模式，覆盖几乎所有 AI 交互 |
| 纯文本流式输出（通知/行情/日志） | **SSE** | 简单、轻量、够用 |
| 社交聊天室 / 协作编辑 / 在线游戏 | **WebSocket** | 真正的高频双向通信 |
| 涉及音视频流 | **WebRTC** | P2P + 低延迟媒体传输 |

---

## 七、AI 对话场景深度分析

### 通信模型

```text
用户输入 "什么是 HashMap"
         │
         ▼
    POST /api/chat    ← 标准 HTTP 请求（用户 → 服务器）
    {"message": "什么是 HashMap"}
         │
         ▼
    200 OK             ← SSE 响应开始（服务器 → 用户）
    Content-Type: text/event-stream
         │
    data: {"token": "HashMap"}
    data: {"token": " 是"}
    data: {"token": " Java"}
    data: {"token": " 中的"}
    ...
    data: [DONE]       ← 流结束
         │
用户点击"停止生成"
         │
         ▼
    POST /api/abort   ← 另一个 HTTP 请求（不是 SSE 通道）
    {"session_id": "xxx"}
```

**核心洞察**：AI 对话看似"双向"，实际是**多个"一问一答"的串联**。每个"问"是独立 HTTP 请求，每个"答"是独立 SSE 流。不需要 WebSocket 的持续双向通道。

### 为什么不选 WebSocket？

| 考量 | SSE 优势 | WebSocket 劣势 |
|------|---------|--------------|
| **连接数** | 一次对话一个 HTTP 响应，用完释放 | 需要维护长连接，10 万并发 = 10 万长连接 |
| **服务端资源** | 无状态 HTTP，可水平扩展 | 有状态连接，需要 sticky session |
| **CDN 分发** | 响应可经 CDN 边缘缓存 | WebSocket 绕过 CDN，直连源站 |
| **故障恢复** | 断线自动重连 + Last-Event-ID | 需自行实现全套重连机制 |
| **监控/调试** | 标准 HTTP 日志，curl 即可测试 | 需要专门的 WebSocket 调试工具 |

### 纠偏：AI 场景真的需要 WebSocket 吗？

> ⚠️ 很多文章说"Function Calling / 多轮 Agent 需要 WebSocket"——这是**理论化的早期架构思维**。2024-2026 实际工程落地中，**SSE + HTTP POST 已经覆盖了几乎所有 AI 交互场景**。

| AI 场景 | 理论说法（不准确） | 实际工程方案 |
|---------|------------------|------------|
| **Function Calling** | "需要 WebSocket 双向传工具结果" | ✅ SSE 推送工具调用事件 + HTTP POST 返回执行结果 |
| **用户中途打断** | "需要 WebSocket 双向" | ✅ SSE 流式推送 + `POST /api/abort` |
| **多轮 Agent** | "需要 WebSocket 持续双向" | ✅ 每轮 Agent 用 SSE 推送，用户操作/工具结果用 HTTP POST |
| **MCP 协议** | — | ✅ 标准就是 SSE + HTTP POST |

**核心模式**："SSE 负责 server→client 流式推送，HTTP POST 负责 client→server 指令回传"。这个组合足以覆盖 ChatGPT、Claude、通义千问等所有主流 AI 产品。

> **真正需要 WebSocket 的 AI 场景**目前极少——只有毫秒级高频双向通信或实时音视频+AI 混合等极端场景。

---

## 八、相关章节

- 面试版：[SSE vs WebSocket 面试题](../../../../13.split-hairs/02.computer-basics/sse-vs-websocket/README.md) — 面试话术 + 陷阱 + 90 秒答案
- HTTP 基础：[HTTP 协议](../../02-http/README.md) — HTTP/1.1 长连接与 chunked 传输
- 前端推送：[网页端消息推送](../../../../13.split-hairs/09.front-end/message/README.md) — 轮询/SSE/WebSocket/WebTransport 全景
- Spring 实现：[WebFlux SSE](../../../../06.spring/02-web/webflux/sse.md) — Spring 服务端 SSE 实现

---

> 📅 2026-07-09 · 网络协议 · SSE vs WebSocket · 深度对比

← [返回: 网络协议](../README.md)
