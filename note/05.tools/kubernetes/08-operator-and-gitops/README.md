<!--
module:
  parent: tools
  slug: tools/k8s-operator-gitops
  type: article
  category: 主模块子文章
  summary: K8s Operator 与 GitOps
-->

# K8s Operator 与 GitOps：云原生的终极自动化

> 一份按层次梳理的 K8s 高级运维速查手册：从自定义资源到声明式部署的完整实战。

---
---

## 一、Operator 模式：让 K8s 懂你的应用

### 1.1 为什么需要 Operator？

K8s 原生支持 Deployment / StatefulSet 等通用工作负载，但**有状态应用**（DB / MQ / 集群）的运维复杂：

- 数据库主从切换
- RabbitMQ 集群扩缩
- 证书轮换
- 备份恢复

**Operator = CRD + Controller**，用 K8s 原生方式管理"特定应用"。

### 1.2 Operator 架构

```
┌────────────────────────────────────────────────┐
│  用户：kubectl apply -f my-db.yaml               │
└────────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────────┐
│  CRD（Custom Resource Definition）               │
│  ┌─────────────────────────────────┐            │
│  │  apiVersion: myapp.example.com/v1 │            │
│  │  kind: MyDatabase                  │            │
│  │  spec:                             │            │
│  │    version: "8.0"                  │            │
│  │    replicas: 3                     │            │
│  └─────────────────────────────────┘            │
└────────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────────┐
│  Controller（Operator 核心）                      │
│  - watch MyDatabase CRD 变化                     │
│  - 调谐实际状态到期望状态                          │
│  - 创建/更新/删除 Pod / Service / PVC              │
│  - 处理应用特定逻辑（主从切换 / 备份）             │
└────────────────────────────────────────────────┘
```

---

## 二、CRD（Custom Resource Definition）

### 2.1 什么是 CRD？

CRD 是 K8s 的"插件机制"，让你定义新的资源类型。

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: mydatabases.myapp.example.com
spec:
  group: myapp.example.com
  scope: Namespaced
  names:
    plural: mydatabases
    singular: mydatabase
    kind: MyDatabase
    shortNames:
    - mdb
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              version:
                type: string
              replicas:
                type: integer
                minimum: 1
                maximum: 10
```

### 2.2 自定义资源使用

```yaml
apiVersion: myapp.example.com/v1
kind: MyDatabase
metadata:
  name: my-db-prod
spec:
  version: "8.0"
  replicas: 3
  storage: 100Gi
```

```bash
kubectl get mydatabases
# NAME          VERSION   REPLICAS   STATUS
# my-db-prod    8.0       3          Running
```

---

## 三、Operator 开发（Kubebuilder / Operator SDK）

### 3.1 Operator SDK 框架

```
my-operator/
├── api/
│   └── v1/
│       └── mydatabase_types.go    # CRD 定义
├── controllers/
│   └── mydatabase_controller.go   # 调谐逻辑
├── config/
│   ├── default/                   # 部署 YAML
│   └── rbac/                     # 权限
├── main.go                        # 入口
└── Makefile
```

### 3.2 简化 Controller 代码

```go
func (r *MyDatabaseReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. 获取 CR
    var mydb myappv1.MyDatabase
    if err := r.Get(ctx, req.NamespacedName, &mydb); err != nil {
        return ctrl.Result{}, err
    }

    // 2. 调谐：让实际状态 == 期望状态
    if mydb.Spec.Replicas == 3 {
        // 创建 3 个 StatefulSet Pod
        // 配置主从复制
        // 设置健康检查
    }

    // 3. 周期调谐（30 秒后再来检查）
    return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
}
```

---

## 四、主流 Operator 生态

| 应用 | Operator |
|------|----------|
| **MySQL** | mysql-operator / presslabs |
| **PostgreSQL** | postgres-operator / Crunchy |
| **MongoDB** | mongodb-operator |
| **Kafka** | strimzi-kafka-operator |
| **RabbitMQ** | rabbitmq-operator |
| **Redis** | redis-operator |
| **ElasticSearch** | elastic-cloud-operator |
| **Prometheus** | prometheus-operator |
| **Cert Manager** | cert-manager（TLS 自动签发）|

---

## 五、Operator Hub

K8s 社区维护的 Operator 仓库：

| Hub | URL |
|-----|-----|
| **OperatorHub.io**（Red Hat）| https://operatorhub.io |
| **Artifact Hub** | https://artifacthub.io |
| **Kubernetes SIG** | https://github.com/kubernetes-sigs |

---

## 六、GitOps：用 Git 管理所有配置

### 6.1 GitOps 核心原则

1. **声明式**：所有配置用 YAML 描述（Git 中）
2. **版本化**：Git 是唯一真相源
3. **自动同步**：集群状态自动与 Git 同步
4. **可审计**：所有变更通过 PR 审核

### 6.2 GitOps vs 传统 CI/CD

| 维度 | 传统 CI/CD | GitOps |
|------|-----------|--------|
| 真相源 | CI 服务器 | Git |
| 部署触发 | CI 完成后 | Git 变更 |
| 回滚 | 重新部署 | Git revert |
| 审计 | CI 日志 | Git history |
| 漂移检测 | 无 | 自动检测 |

### 6.3 GitOps 工具对比

| 工具 | 特点 | 适用 |
|------|------|------|
| **ArgoCD** | K8s 原生 / UI 强大 / 多集群 | 最流行 |
| **Flux** | CNCF 毕业 / GitOps 工具集 | 云原生标准 |
| **Jenkins X** | 集成 Jenkins | 传统团队 |
| **Spinnaker** | Netflix 开源 / 多云 | 大型 |

---

## 七、ArgoCD 实战

### 7.1 安装 ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 7.2 Application 定义

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/my-app-config.git
    targetRevision: main
    path: overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
  syncPolicy:
    automated:
      prune: true                 # 自动清理
      selfHeal: true              # 自动修复漂移
    syncOptions:
    - CreateNamespace=true
```

### 7.3 核心特性

| 特性 | 说明 |
|------|------|
| **自动同步** | Git 变更自动部署到 K8s |
| **漂移修复** | K8s 状态偏离 Git 自动修复 |
| **PR 预览** | PR 创建临时环境预览 |
| **多集群** | 一个 ArgoCD 管多个 K8s 集群 |
| **回滚** | 一键回滚到任意 Git 历史版本 |

---

## 八、ApplicationSets（多环境部署）

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-app-multienv
spec:
  generators:
  - list:
      elements:
      - cluster: dev
        url: https://dev-k8s.example.com
      - cluster: staging
        url: https://staging-k8s.example.com
      - cluster: prod
        url: https://prod-k8s.example.com
  template:
    metadata:
      name: 'my-app-{{cluster}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/myorg/my-app-config.git
        targetRevision: main
        path: overlays/{{cluster}}
      destination:
        server: '{{url}}'
        namespace: my-app
```

---

## 九、Flux vs ArgoCD 对比

| 维度 | ArgoCD | Flux |
|------|--------|------|
| UI | ✅ 强大 Web UI | ❌ CLI 为主 |
| GitOps 工具集 | ❌ 单一工具 | ✅ GitOps Toolkit（多组件） |
| 多集群管理 | ✅ ApplicationSets | ✅ Flux Federation |
| 学习曲线 | 中 | 较陡 |
| 生态 | 最大 | CNCF 标准 |

**推荐**：
- 需要 UI / 可视化 → **ArgoCD**
- 云原生 / 标准化 → **Flux**

---

## 十、最佳实践

1. **GitOps 优先于 kubectl apply**：所有变更走 Git
2. **PR 审核 + 自动测试**：不允许直推 main
3. **多环境分层**：dev → staging → prod（渐进部署）
4. **Operator 不是越多越好**：只对"真正复杂的有状态应用"用
5. **GitOps + Helm 配合**：Helm 模板 + ArgoCD 自动同步
6. **回滚预案**：每次升级前确认 Git 历史可回滚

---

← [返回 K8s 总览](../README.md) · 📅 2026-06-28