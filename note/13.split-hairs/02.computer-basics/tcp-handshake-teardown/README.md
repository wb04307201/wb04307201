<!--
question:
  id: 02.computer-basics-tcp-handshake-teardown
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 反直觉代码
  tags: [02.computer-basics, TCP, 三次握手, 四次挥手, TIME_WAIT, CLOSE_WAIT]
-->

# TCP 三次握手与四次挥手深度剖析

> 一句话定位：三次握手建连接、四次挥手断连接 —— 搞不清状态机和 seq/ack，面试必翻车，生产必踩坑。完整概念见 [TCP/IP 协议族](../../../02.computer-basics/01-network/01-tcp-ip/README.md)。

> **系列定位**：经典计算机网络面试题（后端 / 前端 / 通用高频）。考察的不是"SYN-ACK-SYN"背诵，而是 **状态机转换** + **seq/ack 计算** + **TIME_WAIT / CLOSE_WAIT 生产问题** + **安全攻防**。

---

## 引子：面试官的追问链

```text
面试官：TCP 三次握手的过程是什么？
你：SYN → SYN+ACK → ACK。
面试官：为什么是三次？两次不行吗？
你：……两次不能确认客户端的接收能力。
面试官：那四次挥手呢？为什么握手三次、挥手四次？
你：……
面试官：TIME_WAIT 状态持续多久？为什么需要它？
你：……
面试官：线上服务大量 CLOSE_WAIT 怎么排查？
你：……
```

能背流程只是起点。面试官要的是：**每个 why 都能答上来，每个生产问题都能排查**。

---

## 一、三次握手（连接建立）

### 1.1 流程图 + 状态机

```text
客户端（CLOSED）                              服务端（LISTEN）
    │                                            │
    │  ① SYN, seq=x                              │
    │  ─────────────────────────────────────────→ │
    │  状态: SYN-SENT                             │ 状态: SYN-RCVD
    │                                            │
    │  ② SYN+ACK, seq=y, ack=x+1                 │
    │  ←───────────────────────────────────────── │
    │                                            │
    │  ③ ACK, seq=x+1, ack=y+1                   │
    │  ─────────────────────────────────────────→ │
    │  状态: ESTABLISHED                          │ 状态: ESTABLISHED
    │                                            │
    └──────── 连接建立，开始传输数据 ────────────┘
```

### 1.2 seq 和 ack 的计算规则

| 报文 | seq | ack | 含义 |
|------|-----|-----|------|
| ① SYN | x（随机 ISN） | 无 | "我的初始序号是 x" |
| ② SYN+ACK | y（随机 ISN） | x+1 | "收到你的 x，我期望下一个是 x+1；我的初始序号是 y" |
| ③ ACK | x+1 | y+1 | "收到你的 y，我期望下一个是 y+1" |

**关键**：SYN 和 FIN 各消耗一个序列号（即使不携带数据），所以 ack = 对方 seq + 1。

### 1.3 为什么是三次，不是两次？

**两次握手的致命问题**：历史连接（stale connection）导致资源浪费。

```text
场景：客户端发了一个 SYN（seq=100），网络延迟，超时后重发 SYN（seq=200）

两次握手：
  1. 服务端收到 seq=100 的旧 SYN → 回复 SYN+ACK → 认为连接已建立 → 分配资源
  2. 但客户端知道这是过期的 → 不会响应
  3. 服务端白白浪费了资源（连接泄漏）

三次握手：
  1. 服务端收到 seq=100 的旧 SYN → 回复 SYN+ACK
  2. 客户端知道这是过期的 → 不发 ACK（或发 RST）
  3. 服务端没收到第三次 ACK → 不建立连接 → 不浪费资源
```

**本质**：三次握手是**最小次数**能同时确认双方的发送和接收能力。

| 次数 | 能确认什么 | 不能确认什么 |
|------|-----------|-------------|
| 1 次（SYN） | 客户端能发 | 服务端是否收到、是否能发 |
| 2 次（SYN + SYN+ACK） | 客户端能发、服务端能收能发 | 客户端是否能收 |
| **3 次** | **双方都能发能收** ✅ | — |

## 二、四次挥手（连接断开）

### 2.1 流程图 + 状态机

```text
客户端（ESTABLISHED）                          服务端（ESTABLISHED）
    │                                            │
    │  ① FIN, seq=u                              │
    │  ─────────────────────────────────────────→ │
    │  状态: FIN-WAIT-1                           │ 状态: CLOSE-WAIT
    │                                            │ （服务端可能还有数据要发）
    │  ② ACK, seq=v, ack=u+1                     │
    │  ←───────────────────────────────────────── │
    │  状态: FIN-WAIT-2                           │
    │                                            │
    │         ... 服务端继续发送剩余数据 ...         │
    │                                            │
    │  ③ FIN, seq=w, ack=u+1                     │
    │  ←───────────────────────────────────────── │
    │                                            │ 状态: LAST-ACK
    │  ④ ACK, seq=u+1, ack=w+1                   │
    │  ─────────────────────────────────────────→ │
    │  状态: TIME-WAIT                            │ 状态: CLOSED
    │  （等待 2MSL）                               │
    │  状态: CLOSED                               │
    └──────── 连接关闭 ──────────────────────────┘
```

### 2.2 为什么挥手要四次，不是三次？

**TCP 是全双工的**，每个方向的关闭需要**独立确认**。

- 握手时 SYN+ACK 可以合并（双方同时发起连接），所以 3 次够
- 挥手时一方发 FIN 只表示"我不再发数据了"，但**还能收数据**（半关闭状态）
- 服务端收到 FIN 后可能还有数据要发，所以 ACK 和 FIN **不能合并**

```text
握手：SYN 和 ACK 可以打包在同一个报文中 → 3 次
挥手：ACK 和 FIN 通常不能合并（服务端可能还有数据没发完）→ 4 次
```

### 2.3 挥手也可能是三次

如果服务端在收到 FIN 时**恰好也没有数据要发**，可以把 ACK 和 FIN 合并发送：

```text
客户端                 服务端
  │  FIN  →              │
  │  ← FIN+ACK           │  （ACK 和 FIN 合并）
  │  ACK  →              │

三次完成！
```

## 三、TIME_WAIT：最被误解的状态

### 3.1 TIME_WAIT 在谁那边？

**主动关闭方**进入 TIME_WAIT。谁先调 `close()` 发 FIN，谁就进入 TIME_WAIT。

### 3.2 持续多久？

**2MSL**（Maximum Segment Lifetime，报文最大生存时间）。

- Linux 默认 MSL = 60 秒 → 2MSL = **120 秒**（有些系统为 60 秒）
- 可通过 `/proc/sys/net/ipv4/tcp_fin_timeout` 调整（注意：这个参数实际控制 FIN-WAIT-2 超时，不是 TIME_WAIT）

### 3.3 为什么需要 TIME_WAIT？

**两个核心原因**：

1. **确保最后一个 ACK 到达对方**
   ```text
   如果最后一个 ACK 丢了：
   - 服务端没收到 ACK → 重发 FIN
   - 客户端在 TIME_WAIT 状态 → 能收到重发的 FIN 并重新 ACK
   - 如果没有 TIME_WAIT → 客户端已 CLOSED → FIN 被丢弃 → 服务端卡住
   ```

2. **防止旧连接的数据包被新连接误收**
   ```text
   场景：
   - 旧连接 A→B（port 8080）关闭
   - 新连接 A→B（port 8080）立即建立
   - 如果旧连接的延迟数据包到达 → 被新连接误收 → 数据错乱

   2MSL 保证：旧连接的所有数据包在网络中自然消亡
   ```

### 3.4 TIME_WAIT 过多的危害与优化

| 问题 | 表现 | 优化方案 |
|------|------|---------|
| 端口耗尽 | `Cannot assign requested address` | `net.ipv4.tcp_tw_reuse = 1`（允许复用） |
| 内存占用 | 大量 TIME_WAIT 连接占用内核内存 | 连接池化（长连接复用）|
| 连接建立慢 | 端口不够用时新建连接失败 | 扩大端口范围 `ip_local_port_range` |

> **注意**：`tcp_tw_recycle` 在 Linux 4.12+ 已被移除（NAT 环境下有严重 bug），不要使用。

## 四、CLOSE_WAIT：生产最常见的坑

### 4.1 CLOSE_WAIT 在谁那边？

**被动关闭方**（收到 FIN 但还没调 `close()` 的一方）。

### 4.2 大量 CLOSE_WAIT 的根因

```text
CLOSE_WAIT 大量堆积 = 你的代码没有 close() 连接！

常见原因：
1. 异常路径没关闭连接（catch 块里忘了 close）
2. 连接池配置错误（没有归还连接到池中）
3. 代码 bug：处理完业务逻辑后没有调用 socket.close()
4. HTTP Client 没有正确关闭 response（如 Apache HttpClient）
```

### 4.3 排查方法

```bash
# 查看 CLOSE_WAIT 连接数
ss -tn state close-wait | wc -l

# 查看是哪个进程
ss -tn state close-wait -p

# 查看代码中的连接关闭逻辑
grep -rn "\.close()" src/ --include="*.java"
```

### 4.4 TIME_WAIT vs CLOSE_WAIT 对比

| 维度 | TIME_WAIT | CLOSE_WAIT |
|------|-----------|------------|
| **在哪方** | 主动关闭方 | 被动关闭方 |
| **含义** | 等待旧数据包消亡 | 等待应用层关闭连接 |
| **大量堆积说明** | 短连接太多（正常现象） | **代码 bug**（没 close） |
| **解决方式** | tcp_tw_reuse + 连接池 | **修代码**（确保 finally 里 close） |
| **是否是问题** | 通常是正常的 | **一定是问题** |

## 五、常见陷阱

### 陷阱 1：SYN Flood 攻击

- **原理**：攻击者发送大量 SYN 但不回 ACK → 服务端半连接队列满 → 正常用户无法建立连接
- **防御**：SYN Cookie（不在半连接队列分配资源，把状态编码到 seq 中）、调小 `tcp_max_syn_backlog`

### 陷阱 2：2 次握手"够了"

- **真相**：两次无法确认客户端的接收能力 → 历史连接浪费服务端资源（见 §1.3）

### 陷阱 3：TIME_WAIT 可以安全关闭

- **真相**：TIME_WAIT 是 TCP 协议正确性保障，强行关闭（`tcp_tw_recycle`）会导致 NAT 环境下连接异常

### 陷阱 4：CLOSE_WAIT 是网络问题

- **真相**：CLOSE_WAIT 永远是**代码问题**，不是网络问题。检查你的 `finally` 块有没有 `close()`

### 陷阱 5：挥手一定四次

- **真相**：如果被动方没有剩余数据，ACK+FIN 可以合并 → 三次挥手（见 §2.3）

## 六、最佳实践

1. **使用连接池**：HTTP Client / DB Connection Pool 复用长连接，减少 TIME_WAIT
2. **finally 必 close**：所有 socket / stream / connection 在 finally 中关闭，杜绝 CLOSE_WAIT 泄漏
3. **tcp_tw_reuse = 1**：允许 TIME_WAIT 状态的端口复用（安全，Linux 推荐）
4. **监控 CLOSE_WAIT**：`ss -tn state close-wait | wc -l` 加入告警，> 100 就排查
5. **SYN Cookie 开启**：`net.ipv4.tcp_syncookies = 1`（默认开启），防御 SYN Flood
6. **不要使用 tcp_tw_recycle**：Linux 4.12+ 已移除，NAT 环境下有严重问题

## 七、面试话术（90 秒版本）

> "TCP 三次握手和四次挥手是连接管理的核心机制。
>
> **三次握手**：客户端发 SYN → 服务端回 SYN+ACK → 客户端回 ACK。之所以需要三次而不是两次，是因为两次握手无法确认客户端的接收能力——如果客户端发了一个过期的 SYN，服务端会错误地建立连接并浪费资源。
>
> **四次挥手**：主动方发 FIN → 被动方回 ACK → 被动方发 FIN → 主动方回 ACK。之所以需要四次，是因为 TCP 是全双工的，被动方收到 FIN 后可能还有数据要发送，所以 ACK 和 FIN 不能合并。但如果被动方恰好没有数据，ACK+FIN 可以合并为三次。
>
> **TIME_WAIT** 在主动关闭方，持续 2MSL（约 60-120 秒），作用是确保最后一个 ACK 到达 + 防止旧连接数据包干扰新连接。大量 TIME_WAIT 是正常现象，可以用 tcp_tw_reuse 优化。
>
> **CLOSE_WAIT** 在被动关闭方，大量 CLOSE_WAIT 一定是代码 bug —— 没有正确 close() 连接。排查方法：`ss -tn state close-wait` + 检查代码 finally 块。"

## 八、相关章节

- 主模块：[`TCP/IP 协议族`](../../../02.computer-basics/01-network/01-tcp-ip/README.md) — TCP 完整知识体系（协议栈 + 可靠性机制 + 拥塞控制）
- 同模块：[`TCP 报文结构`](../../../02.computer-basics/01-network/protocols/tcp-packet/README.md) — TCP 头部字段 + 6 个控制标志位详解
- 同模块：[`TCP/IP 四层模型`](../../../02.computer-basics/01-network/tcp-ip-model/README.md) — 网络分层架构
- 相关面试题：[`HTTPS 握手`](../../09.front-end/https-handshake/README.md) — TLS 在 TCP 之上的握手过程

---

> 📅 2026-07-07 · 咬文嚼字 · TCP 三次握手四次挥手 · ⭐⭐⭐⭐（高频面试 + 生产排查必备）

← [返回计算机基础咬文嚼字](../README.md)
