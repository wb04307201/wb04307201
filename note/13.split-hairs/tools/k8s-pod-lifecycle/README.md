<!--
question:
  id: tools-k8s-pod-lifecycle
  topic: tools
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 生产Bug
  tags: [tools, Kubernetes, Pod, 生命周期, Probe, Init Container, PreStop]
-->

# K8s Pod 生命周期中有哪些容易忽略的状态？

> 一句话定位：Pod 不只是"Running 或 CrashLoopBackOff" —— Init Container、三种 Probe、PreStop Hook 共同决定了流量何时进入、何时离开你的容器。

> **系列定位**：经典容器编排面试题（K8s 高频 + 生产事故高发区）。考察的不是"kubectl get pods 看状态"，而是 **生命周期各阶段的触发条件** + **Probe 配置陷阱** + **优雅停机机制**。

---

## 引子：凌晨 2 点的 502 错误

```text
生产环境 K8s 集群，用户投诉凌晨 2 点大量 502 错误。
kubectl get pods 显示所有 Pod 都是 Running 状态。
排查发现：应用启动了但数据库连接池还没初始化完，
readiness probe 只检查了 HTTP /health 返回 200 ——
应用一启动就返回 200，但实际还没准备好接请求。
流量在应用"半就绪"时就被灌进来了。
```

Pod 是 Running ≠ 应用已就绪。**三种 Probe 的区别、Init Container 的执行时机、优雅停机时 PreStop 的作用 —— 这些"隐藏状态"才是真正的面试考点。**

---

## 一、核心原理

### 1.1 Pod 生命周期的 5 个阶段

| 阶段 | 含义 | 常见原因 |
|------|------|---------|
| **Pending** | 已创建但未调度 / 拉镜像中 | 资源不足、镜像拉取慢 |
| **Running** | 至少一个容器在运行 | 正常（但不代表"就绪"） |
| **Succeeded** | 所有容器正常退出 | Job / 批处理任务完成 |
| **Failed** | 至少一个容器异常退出 | OOM / 非零退出码 |
| **Unknown** | 无法获取状态 | 节点失联 / 网络分区 |

### 1.2 TL;DR 三种 Probe 对比表

| Probe | 作用 | 失败后果 | 典型配置 |
|-------|------|---------|---------|
| **Startup** | 检测容器是否已启动 | 在 Startup 通过前，其他 Probe 不执行 | 慢启动应用（JVM 预热） |
| **Readiness** | 检测应用是否准备好接流量 | 从 Service Endpoint 中摘除 | `/ready` 检查依赖 |
| **Liveness** | 检测应用是否存活 | 重启容器 | `/health` 检查核心功能 |

---

## 二、详解：容易忽略的生命周期事件

### 2.1 Init Containers

Init Container 在主容器之前**按顺序**执行，每个必须成功后才执行下一个。常见用途：等待依赖服务就绪、数据库迁移、配置文件生成。例如：

```yaml
initContainers:
  - name: wait-for-db
    image: busybox
    command: ['sh', '-c', 'until nc -z mysql 3306; do sleep 1; done']
```

### 2.2 Startup Probe：解决慢启动问题

配置 `startupProbe` 时设 `failureThreshold: 30` + `periodSeconds: 2`，给应用 60 秒启动窗口。**在 Startup Probe 通过之前，Readiness 和 Liveness 都不会执行。** 没有它，JVM 应用启动慢（10-30 秒），Liveness 在启动期间就检查失败 → 反复重启 → `CrashLoopBackOff`。

### 2.3 Readiness vs Liveness 的关键区别

- **Readiness 失败**：从 Service Endpoint 摘除，不接流量（容器**不重启**）
- **Liveness 失败**：重启容器（可能导致数据丢失）

**关键原则**：Readiness 检查**依赖项**（数据库、Redis），Liveness 只检查**自身存活**（线程是否卡死）。端点必须分开。

### 2.4 PreStop Hook：优雅停机的关键

K8s 终止流程：发送 SIGTERM → 执行 PreStop → 等待 `terminationGracePeriodSeconds` → SIGKILL。

```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 10"]
```

**为什么需要 `sleep 10`**：Endpoint 摘除是异步的，流量可能还在涌入。PreStop sleep 给 kube-proxy 时间更新 iptables 规则，避免"已终止但仍收到请求"的 502。

---

## 三、常见陷阱

### 陷阱 1：Readiness 和 Liveness 用同一个端点

- **现象**：数据库抖动 → Readiness 失败 → 同时 Liveness 也失败 → 容器重启 → 级联故障
- **真相**：Readiness 检查外部依赖，Liveness 只检查自身。数据库不可用时应该**停止接流量**而不是**重启容器**

### 陷阱 2：没配 Startup Probe，慢启动应用 CrashLoopBackOff

- **现象**：Spring Boot 应用反复重启，`kubectl describe` 显示 Liveness 失败
- **真相**：JVM 预热 20 秒，Liveness 超时只有 5 秒。加 Startup Probe 给足启动时间

### 陷阱 3：terminationGracePeriodSeconds 太短

- **现象**：Pod 终止时进行中的请求全部 502
- **真相**：默认 30 秒。如果应用处理长请求（文件上传 / WebSocket），需要调大到 60-120 秒

### 陷阱 4：Init Container 卡死 + PreStop 缺失

- **Init Container 卡死**：Pod 状态 `Init:0/2` 不动，原因是等待的依赖没起来。`kubectl logs <pod> -c <init-container>` 查日志
- **PreStop 没配**：每次滚动更新丢请求（短暂 502），Endpoint 摘除和容器终止有时间差，加 `preStop: exec: sleep 5-10` 解决

---

## 四、最佳实践

1. **三种 Probe 各司其职**：Startup（启动）→ Readiness（依赖就绪）→ Liveness（自身存活），端点分开
2. **慢启动应用必配 Startup Probe**：JVM / Python ML 模型加载 / 数据库迁移后的应用
3. **PreStop sleep 5-10 秒**：给 Endpoint 摘除留缓冲时间，避免滚动更新丢请求
4. **Init Container 处理依赖等待**：比在主容器里写 `while true` 等待逻辑更干净
5. **terminationGracePeriodSeconds 按业务调**：短请求 30s（默认），长请求 60-120s

---

## 五、面试话术（90 秒版本）

> "K8s Pod 生命周期容易忽略的有三块：Init Container、三种 Probe、PreStop Hook。
>
> Init Container 在主容器之前按顺序执行，典型用途是等依赖就绪和数据库迁移。三种 Probe 分工不同：Startup Probe 解决慢启动问题（如 JVM 预热），在它通过前其他 Probe 不执行；Readiness Probe 检查依赖是否就绪，失败时从 Service 摘除但不重启；Liveness Probe 检查自身是否存活，失败时重启容器。
>
> 最常见的坑是 Readiness 和 Liveness 用同一个端点 —— 数据库抖动同时触发容器重启，导致级联故障。生产环境还要配 PreStop Hook sleep 5-10 秒，给 Endpoint 摘除留缓冲，避免滚动更新时的 502 错误。"

---

## 六、交叉引用

- 同栏目：[Docker 多阶段构建](../docker-multi-stage/README.md) — 容器化基础
- 同栏目：[Nginx 反向代理](../nginx-reverse-proxy/README.md) — 流量入口（与 K8s Ingress 互补）
- 系统设计：[熔断降级](../../04.system-design/circuit-breaker/README.md) — 后端保护（Probe 失败时的降级策略）
- 系统设计：[限流算法](../../04.system-design/rate-limiting/README.md) — K8s HPA 扩缩容配合

---

← [返回: 咬文嚼字 · 工具](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 工具 · ⭐⭐⭐⭐⭐（高频面试 + 生产事故高发区）
