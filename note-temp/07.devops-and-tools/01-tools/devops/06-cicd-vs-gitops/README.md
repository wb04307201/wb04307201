<!--
module:
  parent: tools
  slug: tools/cicd-vs-gitops
  type: article
  category: 主模块子文章
  summary: CI/CD vs GitOps
-->

# CI/CD vs GitOps：理念差异与协同模式

> 一份按理念梳理的 DevOps 范式速查手册：从 CI/CD 到 GitOps 的演进路径与最佳组合。

---
---

## 一、CI/CD vs GitOps 核心区别

| 维度 | CI/CD | GitOps |
|------|-------|--------|
| 真相源 | CI 服务器 + 镜像仓库 | **Git 仓库** |
| 触发器 | 代码 push | Git 变更 |
| 部署执行 | CI Pipeline | GitOps Operator（ArgoCD / Flux） |
| 状态对齐 | 手动 / 脚本 | **自动同步** |
| 漂移检测 | ❌ 无 | ✅ 自动检测 + 修复 |
| 回滚 | 重新部署旧版本 | **Git revert** |
| 审计 | CI 日志 | **Git history** |

**核心理念区别**：
- **CI/CD**：构建 + 测试 + 部署（push 模式）
- **GitOps**：以 Git 为真相源（pull 模式）

---

## 二、CI/CD 模式详解

### 2.1 典型流程

```text
代码 push → CI 触发 → 构建 → 测试 → 部署（CI 推送到 K8s）
```

### 2.2 优点

- ✅ 流程清晰，从代码到部署全自动化
- ✅ 适合"主动部署"（代码更新时部署）
- ✅ 与 GitLab / GitHub 原生集成

### 2.3 缺点

- ❌ 部署后集群状态可能漂移（手动改动、扩容）
- ❌ 回滚需重新跑 Pipeline
- ❌ 集群配置分散（CI + K8s 两边都要管）
- ❌ 多集群管理复杂（每集群都要配凭证）

---

## 三、GitOps 模式详解

### 3.1 典型流程

```text
Git 变更 → GitOps Operator 检测 → 同步到 K8s（pull 模式）
                ↓
         自动检测 + 修复漂移
```

### 3.2 4 大原则

1. **声明式**：所有配置用 YAML 描述
2. **版本化**：Git 是唯一真相源
3. **自动拉取**：Agent 从 Git 拉取配置
4. **自动同步**：持续调谐集群状态

### 3.3 优点

- ✅ Git 是真相源（审计 / 回滚天然）
- ✅ 自动检测漂移（集群 vs Git 不一致自动修复）
- ✅ 一键回滚（Git revert）
- ✅ 多集群管理（一份 Git 管 100 集群）
- ✅ 与 PR 流程集成（Code Review）

### 3.4 缺点

- ❌ 启动较复杂（需要 GitOps Operator）
- ❌ 紧急修复需走 Git（不能直接 kubectl apply）

---

## 四、两种模式对比

### 4.1 工作流对比

```text
CI/CD 工作流：
开发者 → Git push → CI 构建 → 部署脚本 → K8s

GitOps 工作流：
开发者 → Git PR → PR 合并 → GitOps Operator → K8s
```

### 4.2 触发机制对比

| 触发 | CI/CD | GitOps |
|------|-------|--------|
| 代码 push | ✅ 自动 | ❌ 需 Git 合并 |
| 紧急修复 | ✅ Pipeline 触发 | ⚠️ 需 Git 提交 |
| 配置变更 | ⚠️ 需 Pipeline | ✅ GitOps 自动 |
| 集群漂移 | ❌ 不处理 | ✅ 自动修复 |

---

## 五、协同模式（推荐）

实际生产中，**CI/CD + GitOps 协同使用**：

```text
┌──────────────┐                              ┌──────────────┐
│   CI/CD       │   构建镜像 + 更新 YAML        │   GitOps      │
│  (Jenkins/    │ ────────────────────────→  │  (ArgoCD/     │
│  GitLab CI/   │   把 image tag 写入 Git       │   Flux)       │
│  GitHub Act)  │                              │              │
└──────────────┘                              └──────┬───────┘
                                                       │
                                                       ↓ 同步
                                                  ┌──────────┐
                                                  │ K8s 集群  │
                                                  └──────────┘
```

### 5.1 协同工作流

1. **CI/CD 阶段**：构建镜像 → 推送到镜像仓库 → 更新 Git 中的 YAML（image tag）
2. **GitOps 阶段**：检测到 Git 变更 → 同步到 K8s 集群

### 5.2 协同示例（GitLab CI + ArgoCD）

**GitLab CI** (`.gitlab-ci.yml`):

```yaml
build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

update-gitops:
  stage: deploy
  script:
    # 自动更新 GitOps 仓库的 image tag
    - git clone https://gitlab.com/myorg/gitops-repo.git
    - cd gitops-repo
    - |
      cat > my-app.yaml <<EOF
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: my-app
      spec:
        template:
          spec:
            containers:
            - name: app
              image: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
      EOF
    - git add my-app.yaml
    - git commit -m "Update my-app to $CI_COMMIT_SHORT_SHA"
    - git push origin main
```

**ArgoCD**（自动检测 Git 变更 → 部署）

```text
Application: my-app
Source: gitops-repo / my-app.yaml
Sync Policy: Automated + Prune + SelfHeal
```

---

## 六、典型组合方案

### 6.1 中小团队

```text
GitHub Actions + ArgoCD
- GitHub Actions: 构建镜像 + 更新 manifest
- ArgoCD: 自动部署 + 漂移修复
```

### 6.2 大型企业

```text
Jenkins + GitLab + ArgoCD
- Jenkins: 构建镜像（重型构建）
- GitLab: 镜像仓库 + 制品管理
- ArgoCD: 多集群部署 + 灰度
```

### 6.3 云原生标准

```text
GitHub Actions + Flux
- GitHub Actions: 构建 + 镜像推送
- Flux: GitOps 工具集（CNCF 毕业）
```

---

## 七、GitOps 工具对比

| 工具 | 特点 | 适用 |
|------|------|------|
| **ArgoCD** | UI 强大 / 多集群 | 大部分场景（推荐） |
| **Flux** | CNCF 毕业 / 标准化 | 云原生标准 |
| **Jenkins X** | Jenkins 集成 | 传统 Jenkins 用户 |
| **Spinnaker** | Netflix / 多云 | 大型企业 |

详见 [08-operator-and-gitops](../../kubernetes/08-operator-and-gitops/README.md)

---

## 八、迁移路径（从 CI/CD 到 GitOps）

### 阶段 1：双轨运行（1-3 个月）

```text
- 保留 CI/CD 部署流程
- 新增 GitOps 部署（小流量）
- 两者并存，逐步迁移
```

### 阶段 2：GitOps 主导（3-6 个月）

```text
- 新服务统一用 GitOps
- 旧服务保留 CI/CD（直到迁移完）
```

### 阶段 3：全面 GitOps（6+ 个月）

```text
- 所有服务用 GitOps
- CI 只负责构建 + 更新 Git
- 紧急修复走 GitOps PR（5 分钟）
```

---

## 九、5 大反模式

| 反模式 | 后果 |
|--------|------|
| **手动 kubectl apply** | 漂移、不可追溯 |
| **CI 直接部署，无 GitOps** | 配置分散、难以回滚 |
| **GitOps 但 CI 不更新 Git** | 配置不一致 |
| **绕过 GitOps 直接改集群** | 漂移违反 GitOps 原则 |
| **GitOps 缺少 PR 审核** | 错误配置直接进生产 |

---

## 十、最佳实践

1. **CI + GitOps 协同**：CI 构建镜像，GitOps 部署应用
2. **Git 是唯一真相源**：所有集群配置都在 Git
3. **PR 审核**：所有 GitOps 变更走 PR + Code Review
4. **自动漂移修复**：开启 ArgoCD SelfHeal
5. **多集群管理**：一个 ArgoCD 实例管多集群
6. **回滚演练**：每月演练 Git revert 回滚
7. **监控告警**：GitOps 失败立即通知

---

← [返回 DevOps 总览](../README.md) · 📅 2026-06-28