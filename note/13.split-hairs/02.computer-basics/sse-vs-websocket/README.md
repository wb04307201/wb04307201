<!--
question:
  id: 02.computer-basics-sse-vs-websocket
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构困境
  tags: [02.computer-basics, SSE, WebSocket, AI, streaming]
-->

# SSE vs WebSocket —— AI 对话为什么选 SSE？

## 引子：面试官的追问

```text
候选人：SSE 是单向的，WebSocket 是双向的。
面试官：那 ChatGPT、Claude、通义千问的 AI 对话，为什么全用 SSE 不用 WebSocket？
候选人：……
```

候选人答对了"单向 vs 双向"，但这只是表面。**面试官真正想考的是系统设计思维**——你有没有想过 AI 对话的通信特征是什么，为什么 SSE 恰好是最优解？

> 一句话定位：**SSE 是 AI 对话的"完美协议"——因为 LLM 对话天然是"一问多答"的单向流。**

---

## 一、核心原理

### 5 维对比表

| 维度 | SSE (Server-Sent Events) | WebSocket |
|------|--------------------------|-----------|
| **通信方向** | 单向：服务器 → 客户端 | 双向：服务器 ↔ 客户端 |
| **协议基础** | 标准 HTTP/1.1（`Content-Type: text/event-stream`） | 独立协议（`ws://` / `wss://`），通过 HTTP Upgrade 握手 |
| **重连机制** | ✅ 内置自动重连（`Last-Event-ID` + `retry`） | ❌ 需自行实现 |
| **代理/CDN 友好** | ✅ 纯 HTTP，所有代理/CDN/防火墙都支持 | ⚠️ 需要代理支持 `Upgrade` 头，很多企业代理不支持 |
| **实现复杂度** | 低（服务端就是一个长连接 HTTP 响应） | 高（需要协议升级、帧解析、心跳保活） |

### SSE 数据格式

```text
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"text": "你"}

data: {"text": "好"}

data: {"text": "，"}

data: {"text": "我是"}

data: {"text": "AI"}

data: [DONE]
```

每个 `data:` 行就是一个事件，浏览器 `EventSource` API 自动解析。

### WebSocket 数据格式

```text
Client → Server:  HTTP GET + Upgrade: websocket
Server → Client:  101 Switching Protocols
（之后双向二进制/文本帧通信）
```

---

## 二、AI 对话为什么选 SSE？（4 大理由）

### 理由 1：通信模式完美匹配

```text
AI 对话的通信特征：
用户发送一条消息（短请求，标准 HTTP POST）
  ↓
服务器流式返回几十~几百个 token（长响应，SSE stream）
  ↓
用户再发一条消息（又一个 HTTP POST）
```

**本质是"一问多答"的单向流** —— 用户不需要在 AI 回答的过程中发送数据。SSE 的单向特性恰好匹配，WebSocket 的双向能力是浪费。

### 理由 2：基础设施友好

| 场景 | SSE | WebSocket |
|------|-----|-----------|
| Nginx 反向代理 | ✅ 天然支持 | ⚠️ 需配置 `proxy_http_version 1.1` + `Upgrade` |
| CDN（CloudFlare） | ✅ HTTP 响应直接缓存 | ⚠️ 部分 CDN 不支持 WebSocket |
| 企业防火墙 | ✅ 走 443 端口 HTTP | ❌ 经常被拦截 |
| 负载均衡器 | ✅ 标准 HTTP 路由 | ⚠️ 需要 sticky session |
| HTTP/2 多路复用 | ✅ 天然支持 | ❌ WebSocket 是独立连接 |

AI 服务面向全球用户，**基础设施兼容性是生命线**。

### 理由 3：断线重连零成本

SSE 内置重连机制：

```javascript
// 浏览器 EventSource 自动处理：
// 1. 连接断开 → 自动重连
// 2. 带上 Last-Event-ID 告诉服务器"我上次收到了第 N 条"
// 3. 服务器从断点继续发送
```

WebSocket 要实现同等效果，需要自行编码心跳检测 + 重连逻辑 + 消息序号管理。

### 理由 4：服务端实现极简

```java
// Spring WebFlux 实现 AI 对话 SSE —— 只需 5 行核心代码
@GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> chatStream(@RequestParam String message) {
    return llmService.streamChat(message)  // LLM 返回 Flux<String>
        .map(token -> "data: " + token + "\n\n");
}
```

WebSocket 需要：协议升级处理 + 连接管理器 + 心跳线程 + 消息编解码器 + 连接池管理。

---

## 三、什么时候该用 WebSocket？（面试装逼区）

选 SSE 不代表 WebSocket 没用。以下场景**必须上 WebSocket**：

### 3.1 AI 场景：SSE + HTTP POST 才是主流（纠偏）

> ⚠️ **重要纠偏**：很多文章说"AI 需要 Function Calling / 多轮 Agent 就该上 WebSocket"——这是**理论化的早期架构思维**。在 2024-2026 实际工程落地中，**SSE + HTTP POST 组合已经覆盖了几乎所有 AI 交互场景**。

| 场景 | 理论说法（不准确） | 实际工程方案（主流） |
|------|------------------|-------------------|
| **用户中途打断 AI 生成** | "需要 WebSocket 双向" | ✅ **SSE + HTTP POST**：SSE 流式推送，停止用 `POST /api/abort` |
| **Function Calling（工具调用）** | "需要 WebSocket 双向传工具结果" | ✅ **SSE + HTTP POST**：SSE 推送工具调用事件，客户端执行后 `POST /api/tool-result` 返回结果 |
| **多轮 Agent** | "需要 WebSocket 持续双向" | ✅ **SSE + HTTP POST**：每轮 Agent 思考用 SSE 推送，用户操作/工具结果用 HTTP POST |
| **MCP（Model Context Protocol）** | — | ✅ **就是 SSE + HTTP POST**：MCP 标准协议本身就用 SSE 做 server→client 流式传输 |

**核心模式**："SSE 负责服务器→客户端的流式推送，HTTP POST 负责客户端→服务器的指令/数据回传"。这个组合已经足够处理 ChatGPT、Claude、通义千问等所有主流 AI 产品的交互需求。

> **什么时候 AI 场景真的需要 WebSocket？** 目前几乎没有。只有极特殊场景（如毫秒级高频双向通信、实时音视频+AI 混合）才可能需要。面试时如果被追问，说出"SSE + HTTP POST 是实际主流"比说"AI 需要 WebSocket"更能体现工程思维。

### 3.2 传统场景

| 场景 | 为什么 SSE 不行 | WebSocket 优势 |
|------|---------------|--------------|
| **在线聊天**（微信/Slack） | 双方都要实时发消息 | 双向通信 |
| **多人协作编辑**（Google Docs） | 多人同时修改 + 实时同步 | 双向 + 低延迟 |
| **在线游戏** | 高频双向操作 | 双向 + 二进制帧 |
| **股票交易** | 下单 + 实时行情 | 双向 + 超低延迟 |

### 3.3 大厂真实选型原则

| 场景 | 选型 | 理由 |
|------|------|------|
| AI 对话（含 Function Calling / Agent） | **SSE + HTTP POST** | ChatGPT/Claude/MCP 都是这个模式，覆盖几乎所有 AI 交互 |
| 纯文本流式输出（通知/行情/日志） | **SSE** | 简单、轻量、够用 |
| 社交聊天室 / 协作编辑 / 在线游戏 | **WebSocket** | 真正的高频双向通信 |
| 涉及音视频流 | **WebRTC** | P2P + 低延迟媒体传输 |

> **判断标准**：AI 场景 → SSE + HTTP POST（不需要 WebSocket）；真正的高频双向通信（聊天/协作/游戏）→ WebSocket；音视频 → WebRTC。

---

## 四、常见陷阱

### 陷阱 1：以为 SSE 只能发文本
- **真相**：SSE 的 `data:` 字段可以发任何文本内容（JSON / Base64 编码的二进制）。但确实不适合大量二进制数据。

### 陷阱 2：以为 SSE 连接数无限制
- **真相**：HTTP/1.1 下浏览器对同一域名最多 **6 个并行连接**（SSE 占一个）。解决方案：用 HTTP/2（多路复用）或不同子域名。

### 陷阱 3：以为 WebSocket 性能一定更好
- **真相**：WebSocket 虽然延迟更低，但连接建立成本更高（HTTP Upgrade + 帧协议），且每条消息有 2-14 字节的帧头开销。对于"一问多答"模式，SSE 的纯 HTTP 响应反而更高效。

### 陷阱 4：不知道 AI 对话可以"假双向"
- **真相**：ChatGPT 的"停止生成"功能不是通过 SSE 实现的（SSE 是单向的），而是通过**另一个 HTTP 请求**（POST /api/abort）通知服务器停止生成。这是"SSE + HTTP 请求"的组合模式。

---

## 五、面试话术（90 秒版）

> SSE 和 WebSocket 的核心区别是单向 vs 双向。AI 对话选择 SSE 有四个原因：
>
> 第一，**通信模式匹配**。AI 对话是典型的"一问多答"——用户发一条消息（HTTP POST），服务器流式返回几十个 token（SSE stream）。用户不需要在 AI 回答的过程中发送数据，双向能力是浪费。
>
> 第二，**基础设施友好**。SSE 就是标准 HTTP 响应，所有代理、CDN、防火墙、负载均衡器都天然支持。WebSocket 需要 Upgrade 握手，很多企业代理和 CDN 不支持或需要额外配置。AI 服务面向全球用户，这个兼容性是生命线。
>
> 第三，**断线重连零成本**。SSE 内置 Last-Event-ID 自动重连机制，WebSocket 需要自己实现心跳+重连+消息序号。
>
> 第四，**服务端极简**。Spring WebFlux 里 5 行代码就能实现 SSE 流式响应，WebSocket 需要连接管理、心跳、帧协议等一堆组件。
>
> 有人会问"那 Function Calling、多轮 Agent 这些复杂场景呢？"——实际上 2024-2026 的工程实践中，这些场景也用 SSE + HTTP POST 组合。MCP 协议本身就是这个模式：SSE 做 server→client 流式推送，HTTP POST 做 client→server 的指令回传。ChatGPT、Claude 的工具调用也是这个套路。真正需要 WebSocket 的是社交聊天、协作编辑、在线游戏这些高频双向场景。大厂选型原则：AI 场景 → SSE + HTTP POST，高频双向 → WebSocket，音视频 → WebRTC。

---

## 六、相关章节

- 协议深度：[SSE vs WebSocket 协议深度对比](../../../02.computer-basics/01-network/protocols/sse-vs-websocket/README.md)
- 前端推送：[网页端消息推送方式](../../09.front-end/message/README.md) — 轮询/SSE/WebSocket/WebTransport 全景对比
- Spring 实现：[WebFlux SSE 实时推送](../../../06.spring/02-web/webflux/sse.md) — Spring 服务端 SSE 实现
- 网络基础：[HTTP 协议](../../../02.computer-basics/01-network/02-http/README.md) — HTTP/1.1 长连接基础

---

> 📅 2026-07-09 · 咬文嚼字 · 网络协议 · ⭐⭐⭐⭐

← [返回: 咬文嚼字 · 02.computer-basics](../README.md)
