<!--
module:
  parent: tools
  slug: tools/kubernetes
  type: article
  category: 主模块子文章
  summary: Kubernetes
-->

# Kubernetes · 云原生编排平台

> 一份从入门到实战的 K8s 完整速查手册：从"容器化部署"到"云原生架构"。

---
## 引言：架构困境
Kubernetes · 云原生编排平台 的关键不是'选型'——是**选完之后怎么在 5 个 trade-off 里活下来**。

本篇用'决策困境'切入，比较几种主流路径并讲清取舍。

---

## 一、一句话定位

**Kubernetes（K8s）**：Google 开源的容器编排平台，用于自动化部署、扩展、运维容器化应用，是云原生时代的"操作系统"。

---

## 二、K8s 的核心价值

```
传统部署：物理机/虚拟机 + 手动运维 + 脚本部署
        ↓
容器部署：Docker + 半自动 + 资源浪费
        ↓
K8s 编排：自动调度 + 自愈 + 弹性扩缩 + 滚动更新 + 服务发现
```

| 价值 | 说明 |
|------|------|
| **自动调度** | 根据资源/亲和性，自动分配 Pod 到合适 Node |
| **自愈** | 容器崩溃自动重启、Node 宕机自动迁移 |
| **弹性扩缩** | 根据 CPU/内存/自定义指标自动扩缩容 |
| **滚动更新** | 灰度发布 + 回滚，零停机部署 |
| **服务发现** | 自动 DNS + 负载均衡，无需手动配置 |
| **配置管理** | ConfigMap / Secret 统一管理配置 |
| **存储编排** | 自动挂载 PV / PVC |

---

## 三、核心架构（控制平面 + 工作节点）

```
┌────────────────────────────────────────────────┐
│  控制平面（Control Plane）                        │
│  ┌──────────┐ ┌──────┐ ┌────────┐ ┌─────────┐  │
│  │ API Server│ │etcd  │ │Scheduler│ │Controller│  │
│  └──────────┘ └──────┘ └────────┘ └─────────┘  │
└────────────────────────────────────────────────┘
                       ↓
┌────────────────────────────────────────────────┐
│  工作节点（Worker Node）                          │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ kubelet       │  │ kube-proxy    │            │
│  │ 容器运行时     │  │ 网络代理      │            │
│  └──────────────┘  └──────────────┘            │
│       ↓ Pod（容器组）                             │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│  │ Pod1 │ │ Pod2 │ │ Pod3 │ │ Pod4 │          │
│  └──────┘ └──────┘ └──────┘ └──────┘          │
└────────────────────────────────────────────────┘
```

---

## 四、核心概念（8 大对象）

| 对象 | 作用 | 典型场景 |
|------|------|---------|
| **Pod** | 最小调度单元（1+ 容器）| 应用实例 |
| **Deployment** | Pod 副本集 + 滚动更新 | 无状态应用 |
| **StatefulSet** | 有状态副本集 | 数据库 / MQ |
| **DaemonSet** | 每 Node 一个 Pod | 节点监控 / 日志收集 |
| **Service** | Pod 负载均衡 + 服务发现 | 微服务 |
| **Ingress** | 7 层路由（HTTP/HTTPS）| 域名访问 |
| **ConfigMap** | 配置中心（非敏感）| 应用参数 |
| **Secret** | 配置中心（敏感 / 加密）| 密码 / 证书 |
| **Job / CronJob** | 一次性 / 定时任务 | 数据处理 / 定时脚本 |

---

## 五、与传统架构对比

| 维度 | 传统部署（VM） | K8s 部署 |
|------|--------------|----------|
| 启动时间 | 分钟级 | 秒级 |
| 资源利用率 | 10-30% | 60-80% |
| 弹性扩缩 | 小时级（采购）| 秒级（自动）|
| 部署效率 | 周级 | 分钟级 |
| 故障恢复 | 人工（小时）| 自动（秒）|

---

## 六、主流发行版

| 发行版 | 提供方 | 适用场景 |
|--------|--------|---------|
| **Kubernetes（上游）** | CNCF | 自己运维 |
| **EKS** | AWS | AWS 用户 |
| **AKS** | Azure | Azure 用户 |
| **GKE** | Google Cloud | GCP 用户 |
| **ACK** | 阿里云 | 阿里云用户 |
| **TKE** | 腾讯云 | 腾讯云用户 |
| **OpenShift** | Red Hat | 企业级 |
| **Rancher** | SUSE | 多云管理 |

---

## 七、学习路径（4 阶段）

```
阶段 1（1 周）：Docker 基础 + K8s 核心概念（Pod/Deployment/Service）
阶段 2（2 周）：YAML 实战 + kubectl 命令 + 本地 minikube 部署
阶段 3（1 个月）：Ingress / ConfigMap / PersistentVolume / Helm
阶段 4（3 个月）：Operator / Helm Chart 开发 / 多集群管理 / GitOps
```

---

## 八、子目录速查

| 文章 | 内容 |
|------|------|
| [01-architecture](01-architecture/README.md) | K8s 整体架构（控制平面 + 工作节点 + 核心组件）|
| [02-pod-and-workload](02-pod-and-workload/README.md) | Pod + Deployment + StatefulSet + DaemonSet |
| [03-service-and-ingress](03-service-and-ingress/README.md) | Service + Ingress + 服务发现 |
| [04-configmap-and-secret](04-configmap-and-secret/README.md) | ConfigMap + Secret + 配置管理 |
| [05-storage-and-pv](05-storage-and-pv/README.md) | PV / PVC / StorageClass / 存储 |
| [06-network-and-service-mesh](06-network-and-service-mesh/README.md) | 网络模型 + Service Mesh |
| [07-helm](07-helm/README.md) | Helm Chart 包管理 |
| [08-operator-and-gitops](08-operator-and-gitops/README.md) | Operator + GitOps + ArgoCD |

---

← [返回工具链总览](../README.md) · 📅 2026-06-28