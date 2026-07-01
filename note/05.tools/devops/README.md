<!--
module:
  parent: tools
  slug: tools/devops
  type: article
  category: 主模块子文章
  summary: DevOps · CI/CD 工具链与实践
-->

# DevOps · CI/CD 工具链与实践

> 一份按工具链梳理的 DevOps 速查手册：从代码提交到生产部署的完整自动化路径。

---
---

## 一、CI/CD 是什么？

```
CI（Continuous Integration，持续集成）
  └─ 开发者频繁合并代码 → 自动化构建 + 测试

CD（Continuous Delivery / Deployment，持续交付/部署）
  └─ 自动化部署到测试/生产环境
```

**DevOps = CI + CD + 监控 + 协作 + 文化**

---

## 二、CI/CD 工具全景图

```
代码托管 → 触发构建 → 编译/测试 → 打包镜像 → 部署 → 监控
   │         │            │           │         │        │
 GitHub     Jenkins     Maven/      Docker   K8s/    Prometheus
 GitLab     GitLab CI   Gradle     Buildah   Helm    Grafana
 Gitee     GitHub      npm/pip              ArgoCD   Loki
 Bitbucket Actions    go build
           ArgoCD
           CircleCI
           Travis CI
```

---

## 三、3 大主流 CI 工具对比

| 工具 | 特点 | 适用 | 成本 |
|------|------|------|------|
| **Jenkins** | 老牌 / 插件最多 / 自托管 | 大型 / 复杂流水线 | 自建 |
| **GitLab CI** | GitLab 内置 / 一体化 | GitLab 用户 | 免费 + 付费版 |
| **GitHub Actions** | GitHub 内置 / 市场丰富 | GitHub 用户 | 免费额度 + 付费 |

### 3.1 Jenkins

```groovy
// Jenkinsfile
pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'mvn clean package'
      }
    }
    stage('Test') {
      steps {
        sh 'mvn test'
      }
    }
    stage('Deploy') {
      when {
        branch 'main'
      }
      steps {
        sh 'kubectl apply -f k8s/'
      }
    }
  }
}
```

### 3.2 GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - mvn clean package
  artifacts:
    paths:
      - target/*.jar

test:
  stage: test
  script:
    - mvn test

deploy:
  stage: deploy
  script:
    - kubectl apply -f k8s/
  only:
    - main
```

### 3.3 GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI Pipeline
on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build
        run: mvn clean package
      - name: Test
        run: mvn test
      - name: Build Docker Image
        run: docker build -t myapp:${{ github.sha }} .
      - name: Push to Registry
        run: docker push myapp:${{ github.sha }}
```

---

## 四、CD 工具对比

| 工具 | 特点 | 适用 |
|------|------|------|
| **ArgoCD** | K8s 原生 GitOps / UI 强大 | 生产标准 |
| **Flux** | CNCF 毕业 / 标准化 | 云原生标准 |
| **Spinnaker** | Netflix 出品 / 多云 | 大型企业 |
| **Jenkins X** | Jenkins 集成 | 传统团队 |
| **Tekton** | K8s 原生 / 标准化 | 云原生 |

详见 [08-operator-and-gitops](../kubernetes/08-operator-and-gitops/README.md)

---

## 五、子目录速查

| 文章 | 内容 |
|------|------|
| [01-jenkins](01-jenkins/README.md) | Jenkins 实战（Pipeline / 插件 / 分布式）|
| [02-gitlab-ci](02-gitlab-ci/README.md) | GitLab CI 一体化实战 |
| [03-github-actions](03-github-actions/README.md) | GitHub Actions 工作流实战 |
| [04-pipeline-patterns](04-pipeline-patterns/README.md) | 流水线设计模式（分支策略 / 多环境）|
| [05-deploy-strategies](05-deploy-strategies/README.md) | 部署策略（蓝绿 / 金丝雀 / 灰度）|
| [06-cicd-vs-gitops](06-cicd-vs-gitops/README.md) | CI/CD vs GitOps 区别与协同 |

---

## 六、CI/CD 流水线典型阶段

```
① 代码扫描（SAST）
   └─ SonarQube / Snyk / GitHub Code Scanning
② 依赖检查
   └─ npm audit / OWASP Dependency-Check
③ 编译构建
   └─ Maven / Gradle / npm / go build
④ 单元测试
   └─ JUnit / Jest / pytest
⑤ 集成测试
   └─ TestContainers / Postman / Selenium
⑥ 性能测试
   └─ JMeter / Locust / k6
⑦ 镜像打包
   └─ Docker / Buildah / Kaniko
⑧ 镜像扫描
   └─ Trivy / Clair / Anchore
⑨ 部署到环境
   └─ dev / staging / prod
⑩ 冒烟测试 + 回滚预案
```

---

## 七、关键指标（DevOps 4 大指标）

DORA 4 大指标（来自 Google DORA 报告）：

| 指标 | Elite 团队 | Low 团队 |
|------|----------|---------|
| **部署频率** | 按需（每天多次）| 每月-每 6 月 |
| **变更前置时间** | < 1 天 | > 1 月 |
| **变更失败率** | 0-15% | > 46% |
| **MTTR** | < 1 小时 | > 1 周 |

**目标**：所有团队向 Elite 靠拢，AI 时代更要高频率、低失败率。

---

## 八、最佳实践

1. **流水线即代码**：Jenkinsfile / .gitlab-ci.yml / .github/workflows/ 都进 Git
2. **缓存加速**：依赖缓存（Maven / npm）减少构建时间 50%
3. **并行执行**：单元测试 / 集成测试 / 性能测试并行
4. **环境一致**：dev / staging / prod 镜像一致（同一 Docker 镜像）
5. **失败快速回滚**：每次部署必须配回滚脚本
6. **密钥管理**：用 Vault / K8s Secret / 云厂商 KMS

---

← [返回工具链总览](../README.md) · 📅 2026-06-28