# Helm · K8s 应用包管理工具

> 一份按层次梳理的 Helm 速查手册：从 Chart 结构到 Helmfile 多环境管理的完整实战。

---
## 引言：反直觉代码

Helm · K8s 应用包管理工具 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、Helm 是什么？

Helm 是 K8s 的"应用包管理器"，相当于 Linux 的 `apt` / `yum` / K8s 的"应用商店"。

```
传统部署：写一堆 YAML 文件（Deployment + Service + ConfigMap + ...）
       ↓
Helm 部署：一个 Chart 包（含模板 + 默认值），一行命令安装
```

---

## 二、Helm 3 大核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| **Chart** | 应用包（模板 + 默认值）| 软件安装包 |
| **Release** | Chart 的一个部署实例 | 软件安装 |
| **Repository** | Chart 仓库（Helm Hub）| 软件商店 |

---

## 三、Chart 结构

```
mychart/
├── Chart.yaml              # Chart 元数据（名称/版本）
├── values.yaml             # 默认配置（可被覆盖）
├── templates/              # K8s 资源模板
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── _helpers.tpl        # 模板辅助函数
│   └── NOTES.txt           # 安装后提示
├── charts/                 # 依赖的子 Chart
├── .helmignore             # 忽略文件
└── README.md               # Chart 说明
```

### 3.1 Chart.yaml

```yaml
apiVersion: v2
name: my-nginx
description: Custom Nginx Chart
type: application
version: 1.0.0              # Chart 版本
appVersion: "1.21"          # 应用版本
maintainers:
- name: Alice
  email: alice@example.com
```

### 3.2 values.yaml（默认值）

```yaml
replicaCount: 3
image:
  repository: nginx
  tag: "1.21"
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 80
resources:
  limits:
    cpu: 500m
    memory: 256Mi
ingress:
  enabled: false
  className: nginx
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: Prefix
```

### 3.3 templates/deployment.yaml（模板）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-nginx.fullname" . }}
  labels:
    {{- include "my-nginx.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "my-nginx.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "my-nginx.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        ports:
        - containerPort: 80
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

---

## 四、Helm 常用命令

```bash
# Chart 管理
helm create mychart                    # 创建 Chart
helm lint mychart                      # 校验 Chart
helm package mychart                    # 打包 Chart（.tgz）
helm template mychart                   # 渲染模板（不部署）

# Release 管理
helm install my-release mychart        # 安装 Release
helm install my-release mychart --values custom-values.yaml  # 自定义值
helm list                               # 列出所有 Release
helm status my-release                 # 查看 Release 状态
helm get values my-release             # 查看实际生效的值
helm get manifest my-release           # 查看渲染后的 YAML

# 升级 / 回滚
helm upgrade my-release mychart        # 升级
helm rollback my-release 1             # 回滚到版本 1
helm history my-release                 # 查看历史版本

# 卸载
helm uninstall my-release
```

---

## 五、values 覆盖（多环境配置）

### 5.1 命令行覆盖

```bash
helm install my-release mychart \
  --set replicaCount=5 \
  --set image.tag=1.22
```

### 5.2 文件覆盖

```bash
helm install my-release mychart \
  -f values-prod.yaml
```

### 5.3 多环境架构

```
charts/
├── values-dev.yaml        # 开发环境
├── values-staging.yaml    # 测试环境
└── values-prod.yaml       # 生产环境
```

---

## 六、Chart 依赖管理

```yaml
# Chart.yaml 中声明依赖
dependencies:
- name: postgresql
  version: 12.1.0
  repository: https://charts.bitnami.com/bitnami
  condition: postgresql.enabled
```

```bash
helm dependency update    # 下载依赖
helm dependency build     # 打包到 charts/
```

---

## 七、Helm Hook（生命周期钩子）

在特定阶段执行作业（如数据库迁移）：

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "{{ include "mychart.fullname" . }}-migrate"
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "1"
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migrate
        image: migrate:latest
        command: ["python", "migrate.py"]
```

| Hook 类型 | 触发时机 |
|-----------|---------|
| `pre-install` | 安装前 |
| `post-install` | 安装后 |
| `pre-upgrade` | 升级前 |
| `post-upgrade` | 升级后 |
| `pre-delete` | 卸载前 |
| `post-delete` | 卸载后 |

---

## 八、Helmfile（多 Chart 多环境）

Helmfile 是 Helm 的"上层封装"，用一个 YAML 管理多个 Chart：

```yaml
# helmfile.yaml
environments:
  default:
    values:
    - environment: prod
  staging:
    values:
    - environment: staging

releases:
  - name: prometheus
    chart: prometheus-community/prometheus
    version: 25.0.0
    values:
      - server:
          retention: 30d

  - name: grafana
    chart: grafana/grafana
    version: 6.50.0
    needs:
      - prometheus        # 依赖
```

```bash
helmfile apply             # 部署所有 release
helmfile apply --environment staging
helmfile diff              # 查看变更
```

---

## 九、Helm 仓库

| 仓库 | URL |
|------|-----|
| **Artifact Hub**（官方）| https://artifacthub.io |
| **Bitnami** | https://charts.bitnami.com/bitnami |
| **Prometheus Community** | https://prometheus-community.github.io/helm-charts |
| **Kubernetes Dashboard** | https://kubernetes.github.io/dashboard |
| **阿里云 ACK** | 自带应用市场 |

---

## 十、最佳实践

1. **每个 Chart 一个应用**：不要在一个 Chart 里塞多个应用
2. **values.yaml 写好默认值**：用户不需要改也能跑
3. **README.md 必写**：列出可配置项 + 示例
4. **使用语义化版本**：Chart 版本（breaking changes）+ AppVersion（应用版本）
5. **CI/CD 集成**：用 Helmfile / ArgoCD 部署，而非手动
6. **Secret 用 Sealed Secrets / External Secrets**：不要明文

---

← [返回 K8s 总览](../README.md) · 📅 2026-06-28