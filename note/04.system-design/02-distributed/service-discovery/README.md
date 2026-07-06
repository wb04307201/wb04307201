<!--
module:
  parent: system-design
  slug: system-design/service-discovery
  type: article
  category: 主模块子文章
  summary: 服务注册与发现 本应该很简单，服务注册与发现是微服务架构的核心基础设施，负责管理服务实例的地址信息，使服务之间能够动态发现和通信
-->

# 服务注册与发现

---

> 服务注册与发现是微服务架构的核心基础设施，负责管理服务实例的地址信息，使服务之间能够动态发现和通信。
>
## 什么是服务发现

在微服务架构中，服务实例会动态地启动、停止、扩容、缩容，IP 和端口不再固定。**服务发现**就是解决"服务 A 如何找到服务 B 当前可用的实例地址"这一问题。

核心流程分为三步：

1. **注册(Register)**：服务启动时将自己的地址信息注册到注册中心
2. **发现(Discover)**：服务调用方从注册中心查询目标服务的可用实例列表
3. **健康检查(Health Check)**：注册中心定期检查服务实例是否存活，剔除不健康的实例

```
┌──────────┐   注册    ┌─────────────────┐   查询    ┌──────────┐
│ Service A│──────────>│  注册中心        │<──────────│ Service B│
│ (Provider)│          │ (Registry)      │          │(Consumer)│
└──────────┘          │                 │          └──────────┘
  Instance 1          │  - Eureka        │
  Instance 2          │  - Nacos         │
  Instance 3          │  - Consul        │
  Instance 4          │  - ZooKeeper     │
                      └─────────────────┘
```

## 两种发现模式

### 客户端发现模式 (Client-Side Discovery)

服务调用方自己从注册中心查询实例列表，并自行决定负载均衡策略。

```
Service B                          Service A
 (Consumer)       Registry         (Provider)
     │               │                │
     │── 查询列表 ──>│                │
     │<─ 返回实例列表 │                │
     │               │                │
     │── 直接调用 ──────────────────>│
     │                               │
```

- **代表实现**：Eureka + Ribbon
- **优点**：简单直接，无额外网络跳数，客户端可自主选择负载均衡策略
- **缺点**：客户端需要集成注册中心 SDK，与注册中心耦合

### 服务端发现模式 (Server-Side Discovery)

调用方不直接感知注册中心，而是通过一个负载均衡器（如 API 网关）转发请求。

```
Service B          Load Balancer        Service A
 (Consumer)        / API Gateway        (Provider)
     │                   │                │
     │─── 调用 ─────────>│                │
     │                   │── 查询 ──────>│<─── 注册
     │                   │              │
     │<── 响应 ──────────│<── 转发 ────│
```

- **代表实现**：Nginx + Consul、Kubernetes Service + CoreDNS
- **优点**：服务调用方对注册中心无感知，职责清晰
- **缺点**：多一跳网络开销，负载均衡器本身可能成为单点

## 主流注册中心对比

| 特性 | Eureka | Nacos | Consul | ZooKeeper |
|------|--------|-------|--------|-----------|
| 开发语言 | Java | Java | Go | Java |
| CAP 模型 | AP | CP/AP 可切换 | CP | CP |
| 健康检查 | 心跳 | HTTP/TCP/MySQL/等 | HTTP/TCP/TCP+Script/等 | 临时节点心跳 |
| 负载均衡 | 客户端(Ribbon) | 客户端/服务端 | 客户端/服务端 | 无(需自行实现) |
| 多数据中心 | 不支持 | 支持 | 支持 | 不支持 |
| 配置管理 | 不支持 | 支持 | 支持(KV) | 支持 |
| 一致性协议 | 无(复制) | Raft(Distro) | Raft | ZAB |
| 跨语言 SDK | Java | Java/Go/.NET/等 | Go/Java/Python/等 | Java/C/Python/等 |
| Spring Cloud 集成 | 原生 | 原生 | Spring Cloud Consul | Curator/Spring |

### 选型建议

- **Spring Cloud 生态、追求快速上手**：Nacos 或 Eureka（Eureka 已停更，推荐 Nacos）
- **多语言环境、需要 KV 存储**：Consul
- **已有 ZooKeeper 基础设施**：可直接复用
- **大规模、高性能要求**：Nacos（支持百万级服务实例）

## 健康检查机制

注册中心必须及时感知服务实例的健康状态，避免将流量转发到故障节点。

| 检查方式 | 原理 | 适用场景 |
|---------|------|---------|
| **心跳检测** | 服务定期向注册中心发送心跳 | Eureka、ZooKeeper |
| **HTTP 检查** | 注册中心定期调用 `/health` 端点 | Consul、Nacos |
| **TCP 检查** | 注册中心尝试建立 TCP 连接 | Consul、Nacos |
| **脚本检查** | 执行自定义脚本判断健康状态 | Consul |
| **MySQL 检查** | 检测数据库连接是否正常 | Nacos |

### 健康检查时序图

```
注册中心                              服务实例
   │                                    │
   │──── HTTP GET /health ────────────>│
   │<──── 200 OK ─────────────────────│   健康
   │                                    │
   │──── HTTP GET /health ────────────>│
   │──── 超时/连接失败 ───────────────>│   不健康
   │  (连续 N 次失败后剔除)              │
   │                                    │
   │── 广播剔除事件 ────────────────>│  通知消费者
```

## 优雅上下线

### 优雅上线 (Graceful Startup)

服务启动后不能立即接收流量，需要等依赖服务就绪、预热完成后再注册：

1. **延迟注册**：启动完成后延迟 N 秒再向注册中心注册，等待 JVM 预热、连接池初始化
2. **健康检查通过后再注册**：先不注册，等自身健康检查通过后主动注册
3. **分批发布**：灰度发布，每次只上线少量实例

### 优雅下线 (Graceful Shutdown)

服务停止时不能立刻终止，需要处理完已有请求再关闭：

1. **注销注册**：先向注册中心注销自己，不再接收新请求
2. **等待已有请求完成**：等待 N 秒让正在处理的请求完成
3. **关闭资源**：关闭连接池、线程池等

```
服务下线流程:

  注销注册 ──> 等待处理中请求 ──> 关闭连接池 ──> 关闭进程
     │              │                │            │
     ▼              ▼                ▼            ▼
  不再接收       等待 30s~60s      清理资源      进程退出
  新请求
```

### Spring Boot 优雅下线示例

```yaml
# application.yml
server:
  shutdown: graceful  # 启用优雅关闭
spring:
  lifecycle:
    timeout-per-shutdown-phase: 60s  # 最大等待时间
```

```java
// Nacos 优雅下线
@Bean
public NacosServiceRegistry nacosServiceRegistry() {
    // 注册 Spring 关闭事件监听
    context.addApplicationListener(event -> {
        if (event instanceof ContextClosedEvent) {
            // 1. 先从注册中心注销
            nacosRegistration.deregister();
            // 2. 等待已有请求完成
            Thread.sleep(30000);
        }
    });
}
```

## 服务发现常见模式

### 1. 服务注册表模式 (Service Registry Pattern)

集中式注册中心维护所有服务实例的信息，是最常见的模式。

### 2. 自愈模式 (Self-Healing Pattern)

服务实例定期续约（Renew），注册中心超时未收到续约则自动注销。配合健康检查实现故障自动转移。

### 3. 多级发现模式 (Hierarchical Discovery)

在大规模系统中，注册中心分层部署：

```
                    ┌──────────────┐
                    │ 全局注册中心   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ 机房 A    │ │ 机房 B    │ │ 机房 C    │
        │ 注册中心   │ │ 注册中心   │ │ 注册中心   │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │             │             │
           实例列表       实例列表       实例列表
```

### 4. 服务网格模式 (Service Mesh Pattern)

将服务发现下沉到 Sidecar 代理（如 Istio/Envoy），服务本身不感知注册中心。

```
Service A          Sidecar A     Sidecar B         Service B
  业务代码          (Envoy)       (Envoy)           业务代码
     │               │             │                  │
     │── 调用 ──────>│── 服务发现 ──>│── 路由 ─────────>│
     │               │  & 负载均衡   │                  │
     │<─ 响应 ───────│<─ 转发 ──────│<─ 响应 ──────────│
```

## 参考链接

- [Spring Cloud Netflix Eureka](https://github.com/Netflix/eureka)
- [Alibaba Nacos](https://nacos.io/)
- [HashiCorp Consul](https://www.consul.io/)
- [Apache ZooKeeper](https://zookeeper.apache.org/)

## 相关章节

- [API 网关](../api-gateway/README.md) — 与服务端发现模式结合实现统一入口
- [RPC](../rpc/README.md) — 内部服务调用的实现方式
- [分布式锁](../distributed-lock/README.md) — 基于 Etcd/ZooKeeper 的实现
- [分布式 ID](../distributed-id/README.md) — 实例 ID 与请求唯一标识

← [返回: 系统设计 · service-discovery](README.md)
