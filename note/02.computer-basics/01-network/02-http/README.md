<!--
module:
  parent: computer-basics
  slug: computer-basics/02-http
  type: article
  category: 主模块子文章
  summary: 一份按版本梳理的 HTTP 协议速查手册：从 1996 到 2026 的 30 年演进历程。
-->

# HTTP 协议演进：从 HTTP/1.0 到 HTTP/3 完整解析

> 一份按版本梳理的 HTTP 协议速查手册：从 1996 到 2026 的 30 年演进历程。

---
## 引言：架构困境

HTTP 协议演进：从 HTTP/1.0 到 HTTP/3 完整解析 的关键不是'选型'——是**选完之后怎么在 5 个 trade-off 里活下来**。

本篇用'决策困境'切入，比较几种主流路径并讲清取舍。

---

## 一、HTTP 协议族演进

| 版本 | 年份 | 核心改进 |
|------|------|---------|
| **HTTP/0.9** | 1991 | 只有 GET，HTML |
| **HTTP/1.0** | 1996 | 加入 POST / Header / 状态码 |
| **HTTP/1.1** | 1997 | 持久连接 / 管道 / chunked / 缓存 |
| **HTTP/2** | 2015 | 二进制分帧 / 多路复用 / HPACK 压缩 |
| **HTTP/3** | 2022 | QUIC（基于 UDP）+ 内置 TLS 1.3 |

---

## 二、HTTP/1.0 vs HTTP/1.1

### 2.1 HTTP/1.0 痛点

```text
请求 1：建立 TCP 连接 → 发送请求 → 接收响应 → 关闭连接
请求 2：再次建立 TCP 连接 → 发送请求 → 接收响应 → 关闭连接
请求 3：再次建立 TCP 连接 → 发送请求 → 接收响应 → 关闭连接
```

**问题**：每次请求都要新建 TCP 连接（3 次握手 + 慢启动），性能差。

### 2.2 HTTP/1.1 改进

#### Keep-Alive（持久连接）

```http
Connection: keep-alive
```

```text
一个 TCP 连接上发送多个请求（不立即关闭）
```

#### 管道化（Pipelining）

```text
请求 1 → 请求 2 → 请求 3 → 响应 1 → 响应 2 → 响应 3
   ↑ 客户端不等响应就发下一个请求
```

**问题**：响应必须按顺序返回（队头阻塞）。

#### 其他改进

- Host 头（支持虚拟主机）
- Chunked Transfer Encoding（流式传输）
- 缓存控制（Cache-Control / ETag）
- 断点续传（Range）
- Cookie / Session

---

## 三、HTTP/2 详解

### 3.1 三大核心改进

| 改进 | 说明 |
|------|------|
| **二进制分帧** | 二进制协议（不再是文本） |
| **多路复用** | 一个连接并发多个请求 / 响应（解决队头阻塞）|
| **HPACK 头部压缩** | 减少重复头部传输 |

### 3.2 HTTP/2 帧结构

```text
+-----------------------------------------------+
|                 Length (24)                    |
+---------------+---------------+---------------+
|   Type (8)    |   Flags (8)   |
+-+-------------+---------------+-------------------------------+
|R|                 Stream Identifier (31)                          |
+=+=============================================================+
|                   Frame Payload (0...)                      ...
+---------------------------------------------------------------+
```

每个请求 / 响应被拆成多个帧，多路复用。

### 3.3 多路复用示意

```text
HTTP/1.1：请求 1 → 响应 1 → 请求 2 → 响应 2 → 请求 3 → 响应 3
            ↑ 串行（队头阻塞）

HTTP/2：  请求 1 + 请求 2 + 请求 3 → 响应 1 + 响应 2 + 响应 3
            ↑ 并发（无队头阻塞）
```

### 3.4 服务端推送（Server Push）

服务端主动推送资源（HTML / CSS / JS），无需客户端请求。

```text
HTML 响应 → 服务端推送 CSS → 服务端推送 JS
```

---

## 四、HTTP/3 详解（基于 QUIC + UDP）

### 4.1 为什么需要 HTTP/3？

HTTP/2 解决了应用层队头阻塞，但 **TCP 层队头阻塞仍在**：

```text
TCP 是可靠传输协议：丢一个包会阻塞后续所有包
   ↓
即使 HTTP/2 多路复用，TCP 层仍要等丢失的包重传
   ↓
HTTP/3 用 QUIC（基于 UDP）解决：每个流独立，不互相阻塞
```

### 4.2 QUIC 核心特性

| 特性 | 说明 |
|------|------|
| **基于 UDP** | 不再被 TCP 队头阻塞 |
| **内置 TLS 1.3** | 0-RTT 握手（首次 1-RTT，再次 0-RTT）|
| **多路复用** | 每个流独立，丢包不影响其他流 |
| **连接迁移** | 切换 WiFi / 4G 不重连（用 Connection ID）|
| **前向纠错** | 部分丢包可恢复（无需重传）|

### 4.3 握手对比

```text
HTTP/1.1：TCP 握手（1 RTT） + TLS 握手（2 RTT） = 3 RTT
HTTP/2  ：TCP 握手（1 RTT） + TLS 握手（1 RTT） = 2 RTT（TLS 1.3）
HTTP/3  ：QUIC 握手（首次 1 RTT / 再次 0 RTT）
```

**效果**：网页首屏加载时间减少 20-30%。

---

## 五、HTTP 状态码速查

### 5.1 1xx（信息性）

- `100 Continue`：继续

### 5.2 2xx（成功）

- `200 OK`：成功
- `201 Created`：创建成功
- `204 No Content`：成功无返回

### 5.3 3xx（重定向）

- `301 Moved Permanently`：永久重定向
- `302 Found`：临时重定向
- `304 Not Modified`：缓存命中

### 5.4 4xx（客户端错误）

- `400 Bad Request`：请求错误
- `401 Unauthorized`：未认证
- `403 Forbidden`：无权限
- `404 Not Found`：资源不存在
- `405 Method Not Allowed`：方法不允许
- `429 Too Many Requests`：限流

### 5.5 5xx（服务端错误）

- `500 Internal Server Error`：服务器内部错误
- `502 Bad Gateway`：网关错误（Nginx 上游错误）
- `503 Service Unavailable`：服务不可用（过载 / 维护）
- `504 Gateway Timeout`：网关超时

---

## 六、HTTP 方法

| 方法 | 幂等 | 用途 |
|------|------|------|
| **GET** | ✅ | 获取资源 |
| **POST** | ❌ | 创建资源 |
| **PUT** | ✅ | 完整更新资源 |
| **PATCH** | ❌ | 部分更新资源 |
| **DELETE** | ✅ | 删除资源 |
| **HEAD** | ✅ | 获取元信息（无 body）|
| **OPTIONS** | ✅ | 跨域预检 |

**幂等性**：多次请求效果相同（GET / PUT / DELETE），可安全重试。

---

## 七、HTTP 头部字段速查

### 7.1 通用头部

| 字段 | 作用 |
|------|------|
| `Cache-Control` | 缓存控制 |
| `Connection` | 连接管理（keep-alive / close）|
| `Date` | 时间戳 |
| `Transfer-Encoding` | 传输编码（chunked）|

### 7.2 请求头部

| 字段 | 作用 |
|------|------|
| `Host` | 虚拟主机 |
| `User-Agent` | 客户端标识 |
| `Accept` | 可接受的响应类型 |
| `Authorization` | 认证信息（Bearer Token）|
| `Cookie` | 会话 Cookie |
| `Referer` | 来源页面 |

### 7.3 响应头部

| 字段 | 作用 |
|------|------|
| `Content-Type` | 响应类型（application/json）|
| `Content-Length` | 响应长度 |
| `Set-Cookie` | 设置 Cookie |
| `Location` | 重定向目标 |
| `ETag` | 缓存标识 |
| `Cache-Control` | 缓存策略 |

---

## 八、HTTP 缓存机制

### 8.1 强缓存（不发送请求）

```http
Cache-Control: max-age=31536000
# 1 年内不请求服务端
```

### 8.2 协商缓存（发送请求但 body 可能是 304）

```http
If-None-Match: "abc123"   # 客户端缓存版本
# 服务端对比 → 一致返回 304（不传 body）
# 不一致返回 200 + 新 body
```

### 8.3 缓存策略组合

```http
# 静态资源（永久缓存）
Cache-Control: public, max-age=31536000, immutable

# 动态资源（每次验证）
Cache-Control: no-cache, must-revalidate
ETag: "version-abc"

# 私密内容
Cache-Control: private, no-store
```

---

## 九、HTTP/2 服务器推送实战

### 9.1 Nginx 配置

```nginx
server {
  listen 443 ssl http2;

  location / {
    root /var/www/html;

    # 推送关键资源
    http2_push_preload on;

    # 资源提示（替代推送）
    add_header Link "</css/main.css>; rel=preload; as=style";
    add_header Link "</js/main.js>; rel=preload; as=script";
  }
}
```

### 9.2 资源提示（Resource Hints）

```html
<!-- preload：关键资源提前加载 -->
<link rel="preload" href="/css/main.css" as="style">
<link rel="preload" href="/js/main.js" as="script">

<!-- prefetch：下一个页面资源 -->
<link rel="prefetch" href="/next-page.html">

<!-- preconnect：提前建立连接 -->
<link rel="preconnect" href="https://cdn.example.com">
```

---

## 十、最佳实践

1. **生产用 HTTP/2**：性能提升 30%+（零配置，浏览器自动协商）
2. **关键资源 preload**：用 `<link rel="preload">`
3. **静态资源长期缓存**：`max-age=31536000, immutable`
4. **动态资源 ETag**：协商缓存
5. **CDN 启用 HTTP/3**：握手快，抗丢包
6. **避免无谓 Cookie**：减少请求头大小
7. **启用 Gzip / Brotli**：压缩响应

---

← [返回计算机网络](../README.md) · 📅 2026-06-28