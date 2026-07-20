<!--
module:
  parent: tools
  slug: tools/k8s-service-ingress
  type: article
  category: 主模块子文章
  summary: K8s Service 与 Ingress
-->

# K8s Service 与 Ingress：服务发现 + 7 层路由

> 一份按层次梳理的 K8s 网络速查手册：从 ClusterIP 到 Ingress 的完整路径。

---
---

## 一、为什么需要 Service？

Pod 是短暂的（IP 变化），微服务之间需要"稳定地址 + 负载均衡"——这就是 Service。

```text
┌──────────────────────────────────────┐
│  Service: nginx-service (ClusterIP)    │  ← 稳定 IP（10.96.0.10）
│  selector: { app: nginx }              │
└──────────────────────────────────────┘
            ↓ Endpoints（自动维护）
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Pod: nginx-0│  │  Pod: nginx-1│  │  Pod: nginx-2│  ← IP 变化
│  IP: 10.1.0.5 │  │  IP: 10.1.0.6 │  │  IP: 10.1.0.7 │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## 二、4 种 Service 类型

| 类型 | 作用 | 典型场景 |
|------|------|---------|
| **ClusterIP（默认）** | 集群内部访问 | 微服务间调用 |
| **NodePort** | 通过 Node 端口暴露 | 开发测试 |
| **LoadBalancer** | 云厂商负载均衡器 | 生产环境 |
| **ExternalName** | DNS 别名 | 跨集群访问 |

### 2.1 ClusterIP（最常用）

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
  - port: 80           # Service 端口
    targetPort: 80      # Pod 端口
    protocol: TCP
```

访问：`curl nginx-service:80`（集群内）

### 2.2 NodePort

```yaml
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080     # 30000-32767 范围
```

访问：`curl <NodeIP>:30080`

### 2.3 LoadBalancer

```yaml
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
```

云厂商（AWS / 阿里云）会自动创建 SLB / ALB。

### 2.4 ExternalName

```yaml
spec:
  type: ExternalName
  externalName: my-db.example.com
```

用作跨集群 / 外部服务的 DNS 别名。

---

## 三、Endpoints 与服务发现

### 3.1 Endpoints 自动维护

Service 通过 Label Selector 自动维护 Endpoints（Pod IP 列表）：

```bash
kubectl get endpoints nginx-service
# NAME             ENDPOINTS
# nginx-service    10.1.0.5:80,10.1.0.6:80,10.1.0.7:80
```

### 3.2 服务发现 3 种方式

| 方式 | 实现 | 适用 |
|------|------|------|
| **环境变量** | Pod 启动时注入 SERVICE_HOST | 简单场景 |
| **DNS（推荐）** | CoreDNS 解析 Service 名 | 微服务主流 |
| **API 查询** | 调用 API Server | 自定义场景 |

```bash
# 验证 DNS 解析
kubectl exec -it nginx-0 -- nslookup nginx-service
```

---

## 四、负载均衡策略

| 策略 | 说明 | 默认 |
|------|------|------|
| **Round Robin（轮询）** | 轮流分配 | ✅ |
| **Session Affinity** | 同一客户端走同一 Pod | ❌ |

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

---

## 五、Headless Service

无 ClusterIP 的 Service，用于 Pod 间直接寻址（StatefulSet 必需）：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
spec:
  clusterIP: None               # 无 ClusterIP
  selector:
    app: mysql
  ports:
  - port: 3306
```

访问：直接通过 Pod 名（如 `mysql-0.mysql-headless`）

---

## 六、Ingress：7 层路由

Ingress 是 K8s 的"反向代理 + 负载均衡"（HTTP/HTTPS 层），对应 Nginx Ingress Controller / Traefik 等。

### 6.1 为什么需要 Ingress？

Service 是 4 层（TCP/UDP），但实际业务需要：
- 域名访问（`api.example.com`）
- HTTPS 证书
- 路径分流（`/api` → 后端，`/web` → 前端）
- 灰度发布（金丝雀）

### 6.2 Ingress 架构

```text
                       ┌─────────────────┐
                       │  Ingress Controller │  ← Nginx / Traefik
                       │  （7 层反向代理）   │
                       └────────┬────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ↓                 ↓                 ↓
        ┌──────────┐      ┌──────────┐      ┌──────────┐
        │ Service A│      │ Service B│      │ Service C│
        │ (前端)    │      │ (后端)    │      │ (管理端)  │
        └──────────┘      └──────────┘      └──────────┘
```

### 6.3 Ingress YAML

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls-secret
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

---

## 七、Ingress Controller 选型

| Controller | 特点 | 性能 | 配置难度 |
|-----------|------|------|---------|
| **Nginx Ingress（最流行）** | 成熟、社区大 | ⭐⭐⭐⭐ | 中 |
| **Traefik** | 自动 HTTPS / Dashboard | ⭐⭐⭐⭐ | 低 |
| **HAProxy** | 高性能 / 老牌 | ⭐⭐⭐⭐⭐ | 高 |
| **Contour** | Envoy 内核 / CRD 友好 | ⭐⭐⭐⭐⭐ | 中 |
| **APISIX** | 国产 / 高性能 / 插件丰富 | ⭐⭐⭐⭐⭐ | 中 |
| **Kong** | 插件生态丰富 | ⭐⭐⭐⭐ | 中 |

---

## 八、实战命令

```bash
# Service 操作
kubectl expose deployment nginx --port=80 --target-port=80
kubectl get svc
kubectl describe svc nginx-service

# Ingress 操作
kubectl get ingress
kubectl describe ingress app-ingress

# 调试网络
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# 在 debug 容器里 nslookup 服务名
```

---

← [返回 K8s 总览](../README.md) · 📅 2026-06-28