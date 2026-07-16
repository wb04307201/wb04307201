<!--
question:
  id: tools-nginx-reverse-proxy
  topic: tools
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [tools, Nginx, 反向代理, 负载均衡, upstream, 健康检查]
-->

# Nginx 反向代理的负载均衡策略有哪些？

> 一句话定位：Nginx 的 upstream 模块提供 4 种负载均衡策略 —— 选错策略会导致流量不均、会话丢失、甚至雪崩。

> **系列定位**：经典工具链面试题（部署与运维高频）。考察的不是"proxy_pass 怎么写"，而是 **策略选型能力** + **健康检查机制** + **生产调优经验**。

---

## 引子：一次"诡异"的流量不均

```text
你有 4 台后端服务器，Nginx 做负载均衡。
上线后发现：server-A 的 CPU 80%，server-B/C/D 只有 10%。
排查半天发现 —— 大部分请求来自同一个办公网的 NAT IP，
而你用的是 ip_hash 策略，同一个 IP 永远打到同一台机器。
```

ip_hash 解决了会话粘滞问题，却引入了流量倾斜。**4 种策略各有什么坑？怎么在会话保持和负载均衡之间取得平衡？**

---

## 一、核心原理

反向代理为服务端服务（客户端不知道后端有多台机器），与正向代理（VPN / Squid，为客户端服务）正好相反。Nginx 通过 `upstream` 模块实现负载均衡：

```nginx
upstream backend {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
    server 10.0.0.3:8080;
    server 10.0.0.4:8080;
}
server {
    location / { proxy_pass http://backend; }
}
```

### 1.3 TL;DR 四种策略对比表

| 策略 | 原理 | 适用场景 | 缺点 |
|------|------|---------|------|
| **Round-Robin**（默认） | 轮流分配 | 无状态服务 | 不考虑服务器负载 |
| **Weighted** | 按权重分配 | 服务器配置不同 | 需手动调权重 |
| **ip_hash** | 按客户端 IP 哈希 | 需要会话粘滞 | NAT 后多用户共享 IP 导致倾斜 |
| **least_conn** | 最少连接数 | 长连接 / 请求耗时差异大 | 短请求场景效果不明显 |

---

## 二、详解：配置示例与选型建议

**Round-Robin（默认）**：按顺序轮流，适合所有服务器配置相同、请求耗时相近的场景。

**Weighted**：按 `weight` 比例分配，适合服务器配置不同（8 核 vs 4 核）。`backup` 参数可做冷备：

```nginx
upstream backend {
    server 10.0.0.1:8080 weight=3;
    server 10.0.0.2:8080 weight=1;
    server 10.0.0.3:8080 weight=1 backup;
}
```

**ip_hash**：同一 IP 始终打到同一台服务器，解决 session 不一致问题。但在 NAT / CDN 环境下大量用户共享出口 IP，导致严重倾斜。

**least_conn**：把请求发给当前连接数最少的服务器，适合 WebSocket / 长轮询 / 文件上传等长连接场景。

**Sticky Session**：Nginx Plus 支持 `sticky cookie`，开源版可用 `hash $cookie_JSESSIONID` 实现基于 cookie 的一致性路由 —— 但**更推荐 Redis 集中 session**。

---

## 三、常见陷阱

### 陷阱 1：健康检查配置不当，流量打到宕机节点

- **现象**：用户间歇性报 502
- **真相**：Nginx 开源版只有**被动健康检查**（`max_fails=3 fail_timeout=30s`），3 次失败后才摘除。需要主动检查可用第三方模块 `nginx_upstream_check_module`

### 陷阱 2：ip_hash + NAT = 流量倾斜

- **现象**：一台服务器 CPU 打满，其他闲置
- **真相**：公司出口 NAT / CDN 回源 IP 共享，ip_hash 把大量用户绑到同一台。改用 `hash $cookie_JSESSIONID` 或 Redis 集中 session

### 陷阱 3：proxy_buffer 没调优导致大响应卡死

- **现象**：Nginx 内存暴涨，响应变慢
- **真相**：默认 `proxy_buffer_size 4k`，大 API 响应（如 JSON 列表）超出缓冲区。需根据业务调整 `proxy_buffer_size` 和 `proxy_buffers`

### 陷阱 4：upstream keepalive 未开启

- **现象**：后端服务器大量 TIME_WAIT 连接
- **真相**：Nginx 默认每次请求新建 TCP 连接。加 `keepalive 32;` 复用连接，减少握手开销

---

## 四、最佳实践

1. **默认用 Round-Robin**，服务器配置不同时用 Weighted
2. **会话保持优先用 Redis 集中 session**，而非 ip_hash（避免 NAT 问题）
3. **必须配置健康检查**：`max_fails=3 fail_timeout=30s`，有条件用主动检查
4. **开启 upstream keepalive**：`keepalive 32;` 减少 TCP 握手
5. **proxy 超时设合理值**：`proxy_connect_timeout 5s; proxy_read_timeout 30s;`（别用默认 60s）

---

## 五、面试话术（90 秒版本）

> "Nginx upstream 提供 4 种负载均衡策略：Round-Robin（默认轮流）、Weighted（按权重）、ip_hash（按 IP 粘滞）、least_conn（最少连接）。
>
> 选型核心看两点：服务是否无状态、请求是否长连接。无状态服务用 Round-Robin 或 Weighted；需要会话保持时，**优先用 Redis 集中 session 而非 ip_hash**（因为 NAT 环境会流量倾斜）；长连接场景用 least_conn。
>
> 生产调优要注意：被动健康检查（max_fails + fail_timeout）防止打到宕机节点、upstream keepalive 减少 TCP 握手、proxy_buffer 根据业务调整避免大响应卡死。"

---

## 六、交叉引用

- 同栏目：[Docker 多阶段构建](../docker-multi-stage/README.md) — 容器化部署
- 同栏目：[K8s Pod 生命周期](../k8s-pod-lifecycle/README.md) — 容器编排（K8s Service 自带负载均衡）
- 同栏目：[Git Rebase vs Merge](../git-rebase-vs-merge/README.md) — 版本管理
- 系统设计：[限流算法](../../04.system-design/rate-limiting/README.md) — Nginx 限流配合
- 系统设计：[熔断降级](../../04.system-design/circuit-breaker/README.md) — 后端保护机制

---

← [返回: 咬文嚼字 · 工具](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 工具 · ⭐⭐⭐⭐（高频面试 + 生产运维必会）
