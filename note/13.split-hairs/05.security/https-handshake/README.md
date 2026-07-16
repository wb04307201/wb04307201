<!--
question:
  id: 05.security-https-handshake
  topic: 05.security
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 性能对比
  tags: [05.security, TLS, HTTPS, 握手, 0-RTT, Session Resumption, OCSP]
-->

# HTTPS 握手过程有哪些性能优化点？—— TLS 1.2 vs 1.3 与连接复用

> 一句话定位：TLS 1.2 完整握手 **2-RTT**，TLS 1.3 降到 **1-RTT**，Session Resumption + 0-RTT 可到 **0-RTT**。完整 TLS 协议见 [主模块加密通信](../../../04.system-design/05-security/encryption/README.md)。

> **系列定位**：经典性能优化面试题（字节 / 美团高频）。考察 **握手 RTT 优化** + **连接复用** + **OCSP Stapling**。

---

## 引子：首页 TTFB 从 800ms 到 200ms 的优化之路

```text
性能对比（上海 → 美西，RTT ≈ 150ms）：
- HTTP 直连：TTFB 160ms（1 次 TCP 握手）
- HTTPS TLS 1.2 首次：TTFB 610ms（TCP + TLS 完整握手）
- HTTPS TLS 1.3 首次：TTFB 460ms（TCP + TLS 仅 1-RTT）
- TLS 1.3 + 0-RTT：TTFB 310ms（提前发送数据）
- 连接复用：TTFB 160ms（握手已完成）
```

**反直觉**：HTTPS 首次连接的握手开销是 **3-4 倍 RTT**；0-RTT 有**重放攻击风险**，并非所有接口都适合。

---

## 一、核心原理

| 模式 | RTT | 安全性 | 适用 |
|------|-----|--------|------|
| TLS 1.2 完整握手 | 2-RTT | 完整 | 首次连接 |
| TLS 1.2 Session Resumption | 1-RTT | 完整 | 重复连接 |
| TLS 1.3 完整握手 | 1-RTT | 完整 + 前向安全 | 首次连接 |
| TLS 1.3 + 0-RTT | 0-RTT | **有重放风险** | 幂等请求 |
| 连接复用（Keep-Alive） | 0-RTT | 完整 | 同域名多请求 |

**TLS 1.2 完整握手（2-RTT）**：ClientHello → ServerHello+Certificate+KeyExchange → ClientKeyExchange+Finished → ServerFinished → 开始传输。

**TLS 1.3 改进（1-RTT）**：ClientHello 直接携带 ECDHE key_share，砍掉一个 RTT；废弃 RSA 密钥交换，只保留 (EC)DHE 前向安全。

---

## 二、详解

**Session Resumption**：首次握手后缓存 Session ID / Ticket，后续 ClientHello 携带 → 命中则跳过密钥协商（1-RTT）。Session Ticket 无状态适合集群，但 Ticket Key 需定期轮换（泄露 = 历史会话可解密）。

**TLS 1.3 的 0-RTT**：客户端缓存上次 PSK，新连接 ClientHello 带 PSK + early_data 直接发应用数据。**重放攻击风险**：仅用于幂等 GET 请求，POST/转账必须等 1-RTT。

**OCSP Stapling**：普通流程浏览器需额外请求 CA 验证证书状态（+1 RTT）；Stapling 让服务端缓存 OCSP 响应，握手时附带 → 省 1 个 RTT。

---

## 三、常见陷阱

- **0-RTT 用于非幂等操作**：数据可被重放 → 仅 GET 查询启用，转账/删除等 1-RTT
- **Session Ticket Key 不轮换**：泄露后历史会话可解密 → 每 24 小时轮换
- **不启用 OCSP Stapling**：每次连接额外请求 CA → Nginx `ssl_stapling on`
- **连接池不复用 HTTPS 连接**：每次完整握手浪费 2-3 RTT → HTTP Keep-Alive + 连接池

---

## 四、最佳实践

```nginx
# Nginx HTTPS 性能优化
ssl_protocols TLSv1.2 TLSv1.3;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
ssl_session_tickets on;
ssl_stapling on;
ssl_stapling_verify on;
ssl_early_data on;          # TLS 1.3 0-RTT
keepalive_timeout 65;
```

```
客户端优化：HTTP/2 多路复用 + 连接池（OkHttp 默认 5 连接 / 5 分钟）+ TLS 1.3 优先

优化效果量化：
  TLS 1.3（vs 1.2）→ 省 1 RTT
  Session Resumption → 省 1 RTT
  0-RTT → 省 1 RTT
  OCSP Stapling → 省 1 RTT
  连接复用 → 省全部 RTT
```

---

## 五、面试话术（90 秒版本）

> "HTTPS 握手瓶颈在 RTT 开销。TLS 1.2 完整握手需 2-RTT，TLS 1.3 通过 ClientHello 直接携带 ECDHE 公钥降到 1-RTT。Session Resumption 让重复连接跳过密钥协商降到 1-RTT，有 Session ID（需共享存储）和 Ticket（无状态）两种方式。TLS 1.3 的 0-RTT 允许 ClientHello 中直接发数据，但有重放风险，仅适合幂等 GET。
>
> OCSP Stapling 让服务端缓存证书状态并在握手时附带，省掉浏览器向 CA 的额外请求。综合优化：TLS 1.3 + Session Resumption + OCSP Stapling + 连接复用，HTTPS 首次连接从 600ms 降到 200ms 以内。"

---

## 六、交叉引用

- [传输加密 vs 存储加密](../encryption-at-rest-transit/README.md) — TLS 在加密体系中的定位
- [CORS 预检请求优化](../cors-preflight/README.md) — 另一个 RTT 优化维度
- [主模块 04.system-design/05-security](../../../04.system-design/05-security/README.md) — 安全知识体系

---

← [返回: 咬文嚼字 · 安全](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 05.security · ⭐⭐⭐⭐⭐
