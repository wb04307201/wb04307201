<!--
module:
  parent: 03-network
  slug: 02.cs-foundations/03-network/tcp-handshake-teardown
  type: article
  category: 主模块子文章
  summary: TCP 三次握手 + 四次挥手 完整机制 —— 字段含义 + 状态机 + TIME_WAIT/2MSL + 反模式（SYN Flood / 半连接攻击）
  depth: ⭐⭐⭐⭐⭐
-->

# TCP 三次握手 + 四次挥手 · 完整机制

> **一句话定位**：TCP 连接建立 = **3 次握手（SYN → SYN-ACK → ACK）**；连接断开 = **4 次挥手（FIN → ACK → FIN → ACK）** + 主动方等待 **2MSL（TIME_WAIT）**。

← [返回: 计算机网络](../README.md) · TCP/IP 基础：[01-tcp-ip](../01-tcp-ip/README.md)

---

## 一、三次握手（建立连接）

### 1.1 流程图

```text
客户端                              服务端
  │                                  │
  │  1. SYN (seq=x)                  │
  │  ─────────────────────────────→  │  CLOSED → LISTEN → SYN_RECEIVED
  │                                  │
  │  2. SYN-ACK (seq=y, ack=x+1)     │
  │  ←─────────────────────────────  │
  │                                  │
  │  3. ACK (seq=x+1, ack=y+1)       │
  │  ─────────────────────────────→  │  ESTABLISHED
  │                                  │
  │         双向数据通道就绪           │
```

### 1.2 关键字段

| 字段 | 作用 |
|------|------|
| **SYN (synchronize)** | 同步序列号，请求建立连接 |
| **seq (sequence number)** | 本端数据起始序号（防乱序） |
| **ACK (acknowledge)** | 确认号，期待下一字节序号 |
| **SYN-ACK** | 同步 + 确认的合并标志（握手优化） |

### 1.3 为什么是 3 次（不是 2 次）？

**核心原因：双向通道确认**

```text
2 次握手的问题：
  客户端发 SYN → 服务端回 ACK
  → 但服务端不知道自己的 ACK 是否到达客户端
  → 若 ACK 丢失，客户端不会重试，服务端白白建立连接

3 次握手的优雅之处：
  第 3 次 ACK 让客户端确认"服务端收到了我的 SYN"
  同时让服务端确认"客户端收到了我的 ACK"
  → 双向通道可靠建立
```

---

## 二、四次挥手（断开连接）

### 2.1 流程图

```text
主动方（A）                          被动方（B）
  │                                  │
  │  1. FIN (seq=u)                  │
  │  ─────────────────────────────→  │  ESTABLISHED → CLOSE_WAIT
  │                                  │
  │  2. ACK (seq=v, ack=u+1)         │
  │  ←─────────────────────────────  │  （B 可能还有数据要发）
  │                                  │
  │  3. FIN (seq=w, ack=u+1)         │
  │  ←─────────────────────────────  │  CLOSE_WAIT → LAST_ACK
  │                                  │
  │  4. ACK (seq=u+1, ack=w+1)       │
  │  ─────────────────────────────→  │  CLOSED
  │                                  │
  │  A: TIME_WAIT (等待 2MSL)         │
  │     → CLOSED                     │
```

### 2.2 为什么是 4 次（不是 3 次）？

TCP 是**全双工**通信，需要双向独立关闭：

```text
场景：A 想关，B 还想发数据
  - 第 1 次 FIN：A 说"我不再发数据给你"
  - 第 2 次 ACK：B 说"收到，但请等下，我还有数据要发"
  - 第 3 次 FIN：B 发完数据后说"我也没数据了"
  - 第 4 次 ACK：A 确认"OK，连接关闭"

不能合并成 3 次：
  若 FIN + ACK 合并，B 发完数据才能 FIN，期间 A 等不到确认
```

---

## 三、TIME_WAIT 与 2MSL

### 3.1 2MSL 是什么？

**MSL (Maximum Segment Lifetime)** = 一个 TCP 段在网络中最长存活时间（Linux 默认 60s，Windows 默认 4min）。**2MSL = 2 × MSL**（Linux 默认 120s）。

### 3.2 为什么需要 TIME_WAIT？

```text
核心目的：保证最后一个 ACK 能到达对端
  - A 发送第 4 次 ACK 后进入 TIME_WAIT
  - 若 ACK 丢失，B 会重传 FIN（第 3 步）
  - A 在 TIME_WAIT 期间收到重传 FIN → 重发 ACK
  - 2MSL 后确认 B 已收到 ACK → 彻底关闭

副作用：
  - TIME_WAIT 状态占用连接端口
  - 高并发短连接场景（如 HTTP）会出现大量 TIME_WAIT
  - 解决方案：SO_REUSEADDR、调整 tcp_tw_reuse（Linux 4.12+）
```

### 3.3 Linux 调优参数

```bash
# /etc/sysctl.conf
net.ipv4.tcp_tw_reuse = 1            # 允许 TIME_WAIT 状态的 socket 用于新连接
net.ipv4.tcp_tw_recycle = 0          # ⚠️ 已废弃，不要开启（NAT 环境会丢包）
net.ipv4.tcp_fin_timeout = 30        # FIN_WAIT_2 超时时间（默认 60s）
net.ipv4.tcp_max_tw_buckets = 65536  # TIME_WAIT 数量上限（超过则直接销毁）
```

---

## 四、5 大反模式

### 4.1 半连接攻击（SYN Flood）

```text
攻击者只发 SYN，永远不回 ACK
  → 服务端 SYN_RECEIVED 队列耗尽
  → 拒绝服务（DoS）

防御：
  - SYN Cookie（不分配资源，仅靠 seq 计算）
  - 缩短 SYN timeout
  - 增加半连接队列（net.ipv4.tcp_max_syn_backlog）
```

### 4.2 大并发短连接的 TIME_WAIT 堆积

```text
现象：高 QPS HTTP 服务 TIME_WAIT 数 = 端口数 × 10000
原因：每次 HTTP 短连接都是 4 次挥手 + TIME_WAIT 120s
解决：
  - HTTP 长连接（Keep-Alive）
  - 连接池复用（HttpClient Pool）
  - SO_REUSEADDR 允许端口重用
```

### 4.3 不当使用 CLOSE_WAIT 状态

```text
现象：大量 CLOSE_WAIT 状态连接堆积
原因：应用层未调用 close() 或异常时未释放
排查：jstack 看线程是否卡在 socket.close()
预防：try-with-resources 自动释放
```

### 4.4 错误理解 2MSL 等待目的

```text
❌ "2MSL 是为了让对端收到 ACK" — 不准确
✅ "2MSL 保证 ACK 丢失时对端能重传 FIN，且 ACK 在网络中的所有副本都消失"

副作用：保证旧连接的延迟报文不会影响新连接（同端口五元组复用）
```

### 4.5 误用 FIN_WAIT_2 调优

```text
FIN_WAIT_2 = A 发完 FIN 并收到 ACK，等待 B 发 FIN
  - 若 B 异常未发 FIN，A 永远停在 FIN_WAIT_2
  - tcp_fin_timeout 控制最长等待（默认 60s）
  - 不要盲目调大，可能掩盖 B 端 bug
```

---

## 五、面试话术（30 秒版）

> "TCP 三次握手建立连接：客户端 SYN → 服务端 SYN-ACK → 客户端 ACK。核心是双向确认——客户端确认服务端收到了自己的 SYN，服务端确认客户端收到了自己的 ACK。
>
> 四次挥手断开连接：主动方 FIN → 被动方 ACK → 被动方 FIN → 主动方 ACK。**比建立多一次**，因为 TCP 是全双工，需要双向独立关闭。
>
> 主动方最后进入 TIME_WAIT 等待 2MSL（默认 120s）：① 保证 ACK 丢失时对端能重传 FIN ② 保证网络中的旧报文消失，不影响新连接。
>
> 高并发场景（HTTP 短连接）会堆积大量 TIME_WAIT，解决方案是 Keep-Alive + SO_REUSEADDR + 连接池复用。
>
> 常见攻击：SYN Flood 利用半连接队列耗尽，防御用 SYN Cookie + 缩短 timeout。"

---

## 关联章节

- **TCP/IP 基础**：[`01-tcp-ip`](../01-tcp-ip/README.md) — 4 层模型 + TCP/UDP 对比
- **HTTP 协议**：[`02-http`](../02-http/README.md) — 基于 TCP 的应用层协议
- **HTTPS/TLS**：[`04-https-tls`](../04-https-tls/README.md) — TLS 1.3 1-RTT 握手对比 TCP 3 次握手

← [返回: 计算机网络](../README.md)