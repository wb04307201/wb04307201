# K8s Pod 与工作负载：Deployment / StatefulSet / DaemonSet

> 一份按工作负载类型梳理的速查手册：从 Pod 基础到 4 种工作负载的实战用法。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

K8s Pod 与工作负载：Deployment / StatefulSet / DaemonSet 本应该很简单，一份按工作负载类型梳理的速查手册：从 Pod 基础到 4 种工作负载的实战用法

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、Pod：K8s 最小调度单元

### 1.1 什么是 Pod？

Pod 是 K8s 中"最小的可部署计算单元"，可以包含 1 个或多个容器。

```
┌─────────────────── Pod ───────────────────┐
│                                          │
│   ┌─────────────┐   ┌─────────────┐    │
│   │  App 容器    │   │ Sidecar 容器 │    │
│   │ （主业务）    │   │ （日志/代理）│    │
│   └─────────────┘   └─────────────┘    │
│         ↕ 共享网络/存储                   │
│   ┌───────────────────────────────┐    │
│   │     Pause 容器（基础设施）         │    │
│   └───────────────────────────────┘    │
│                                          │
└──────────────────────────────────────────┘
```

### 1.2 Pod 核心特性

| 特性 | 说明 |
|------|------|
| **共享网络** | Pod 内所有容器共享 IP + 端口 |
| **共享存储** | Pod 内 Volume 共享 |
| **生命周期** | 短暂的，可能被重建 |
| **同进同退** | Pod 内所有容器同生命周期 |

### 1.3 Pod YAML 示例

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi
  - name: log-sidecar
    image: busybox
    command: ['sh', '-c', 'tail -f /var/log/nginx/access.log']
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/nginx
  volumes:
  - name: log-volume
    emptyDir: {}
```

---

## 二、4 大工作负载对比

| 工作负载 | 适用场景 | 关键特性 |
|---------|---------|---------|
| **Deployment** | 无状态应用（Web/API/微服务）| 副本集 + 滚动更新 |
| **StatefulSet** | 有状态应用（DB/MQ/集群）| 稳定网络 ID + 持久存储 |
| **DaemonSet** | 节点级服务（日志/监控/网络）| 每 Node 一个 Pod |
| **Job / CronJob** | 一次性 / 定时任务 | 任务完成 / 定时触发 |

---

## 三、Deployment：无状态应用

### 3.1 适用场景

- Web 服务（Spring Boot / Node.js / Python）
- API 网关
- 微服务
- 前端 SSR

### 3.2 Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3                      # 3 个副本
  selector:
    matchLabels:
      app: nginx
  strategy:
    type: RollingUpdate             # 滚动更新策略
    rollingUpdate:
      maxSurge: 1                  # 最多超出 1 个 Pod
      maxUnavailable: 0            # 不可用为 0（零停机）
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
```

### 3.3 滚动更新 vs 蓝绿 vs 金丝雀

| 策略 | 优点 | 缺点 |
|------|------|------|
| **RollingUpdate（默认）** | 零停机、平滑 | 回滚慢 |
| **Recreate** | 简单 | 停机 |
| **Blue-Green（蓝绿）** | 一键回滚 | 资源 2 倍 |
| **Canary（金丝雀）** | 渐进放量 | 配置复杂 |

---

## 四、StatefulSet：有状态应用

### 4.1 适用场景

- 数据库（MySQL / PostgreSQL / MongoDB）
- 消息队列（Kafka / RabbitMQ）
- 集群软件（ZooKeeper / etcd）
- 分布式存储

### 4.2 StatefulSet 关键特性

- **稳定网络 ID**：pod-0、pod-1、pod-2（而非 deployment 的随机 hash）
- **持久存储**：每个 Pod 独立的 PV
- **有序部署**：pod-0 先启动，pod-0 ready 后 pod-1 才启动
- **有序删除**：pod-N 先删除，倒序删除

### 4.3 StatefulSet YAML 示例

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: ssd
      resources:
        requests:
          storage: 100Gi
```

---

## 五、DaemonSet：节点级服务

### 5.1 适用场景

- 日志收集（Fluentd / Filebeat）
- 节点监控（Node Exporter）
- 网络插件（Calico / Cilium）
- 存储插件（GlusterFS / Ceph）

### 5.2 DaemonSet YAML

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true              # 使用主机网络
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
          hostPort: 9100              # 暴露到主机
```

---

## 六、Job 与 CronJob

### 6.1 Job（一次性任务）

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-import
spec:
  completions: 1                   # 完成 1 次
  parallelism: 1                  # 并行度 1
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: importer
        image: importer:latest
        command: ["python", "import.py"]
```

### 6.2 CronJob（定时任务）

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-report
spec:
  schedule: "0 2 * * *"            # 每天凌晨 2 点
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: report
            image: report:latest
            command: ["python", "report.py"]
```

---

## 七、实战命令速查

```bash
# Deployment 操作
kubectl create deployment nginx --image=nginx:1.21
kubectl scale deployment/nginx --replicas=5
kubectl rollout status deployment/nginx
kubectl rollout undo deployment/nginx        # 回滚

# Pod 排查
kubectl get pods -o wide
kubectl describe pod <pod-name>
kubectl logs <pod-name> -f --previous

# 进入 Pod
kubectl exec -it <pod-name> -- /bin/bash

# StatefulSet 特殊操作
kubectl exec mysql-0 -- mysql -uroot
```

---

← [返回 K8s 总览](../README.md) · 📅 2026-06-28