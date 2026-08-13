<!--
module:
  parent: tools
  slug: tools/gitlab-ci
  type: article
  category: 主模块子文章
  summary: GitLab CI
-->

# GitLab CI · 一体化 DevOps 平台实战

> 一份按场景梳理的 GitLab CI 速查手册：从基础流水线到企业级 DevOps 链路的完整实战。

---
---

## 一、GitLab CI 简介

GitLab CI 是 GitLab 内置的 CI/CD 工具，与代码托管一体化，开箱即用。

### 1.1 核心特性

- **一体化**：代码托管 + CI/CD + Issue + Wiki 在一个平台
- **Pipeline as Code**：`.gitlab-ci.yml` 描述流水线
- **Runner 可扩展**：GitLab Runner 支持 Docker / K8s / Shell
- **内置制品库**：Container Registry / Maven / NPM
- **免费额度**：每月 400 分钟（社区版）

---

## 二、核心架构

```text
┌─────────────────────────────────────────┐
│  GitLab Server（代码托管 + CI 调度）          │
└────────────┬────────────────────────────┘
             │ 任务分发
             ↓
┌────────────┼────────────┐
↓            ↓            ↓
┌──────┐   ┌──────┐   ┌──────┐
│Runner│   │Runner│   │Runner│  ← K8s Pod / Docker / VM
└──────┘   └──────┘   └──────┘
```

---

## 三、`.gitlab-ci.yml` 基础

### 3.1 文件位置

```text
项目根目录/.gitlab-ci.yml
```

### 3.2 最小流水线

```yaml
stages:
  - build
  - test
  - deploy

build-job:
  stage: build
  script:
    - echo "Compiling..."
    - mvn clean package

test-job:
  stage: test
  script:
    - mvn test

deploy-job:
  stage: deploy
  script:
    - echo "Deploying..."
  environment: production
  only:
    - main
```

### 3.3 核心概念

| 概念 | 说明 |
|------|------|
| **Stages** | 阶段（如 build / test / deploy）|
| **Jobs** | 阶段内的具体任务 |
| **before_script / after_script** | 任务前后执行 |
| **variables** | 变量（CI_COMMIT_REF_NAME 等预定义）|
| **artifacts** | 工件（构建产物）|
| **cache** | 缓存（依赖、构建工具）|
| **environment** | 环境（dev / staging / prod）|
| **only / except** | 分支控制 |

---

## 四、完整流水线示例

```yaml
stages:
  - prepare
  - build
  - test
  - code-quality
  - package
  - deploy

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"
  DOCKER_REGISTRY: registry.gitlab.com
  APP_NAME: myapp

# 全局缓存
cache:
  key: ${CI_JOB_NAME}
  paths:
    - .m2/repository
    - node_modules/

# 1. 准备阶段
prepare-job:
  stage: prepare
  image: alpine:3.18
  script:
    - apk add --no-cache git
    - echo "Preparation done"

# 2. 构建
build-job:
  stage: build
  image: maven:3.9-openjdk-17
  script:
    - mvn clean package -DskipTests
  artifacts:
    paths:
      - target/*.jar
    expire_in: 1 day

# 3. 测试（并行）
unit-test:
  stage: test
  image: maven:3.9-openjdk-17
  script:
    - mvn test
  artifacts:
    when: always
    paths:
      - target/surefire-reports/

integration-test:
  stage: test
  image: maven:3.9-openjdk-17
  script:
    - mvn verify -Pintegration
  artifacts:
    when: always
    paths:
      - target/failsafe-reports/

# 4. 代码质量
code-quality:
  stage: code-quality
  image: maven:3.9-openjdk-17
  script:
    - mvn sonar:sonar
  allow_failure: true

# 5. 打包镜像
package-job:
  stage: package
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHORT_SHA .
    - docker push $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHORT_SHA
  only:
    - main

# 6. 部署
deploy-staging:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl apply -f k8s/ -n staging
    - kubectl rollout status deployment/myapp -n staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

deploy-prod:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl apply -f k8s/ -n production
    - kubectl rollout status deployment/myapp -n production
  environment:
    name: production
    url: https://www.example.com
  when: manual                    # 手动确认
  only:
    - main
```

---

## 五、GitLab Runner 配置

### 5.1 安装 Runner

```bash
# Linux 安装
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt-get install gitlab-runner

# 注册 Runner
sudo gitlab-runner register
# 输入 GitLab URL、token、描述、标签、执行器（docker）
```

### 5.2 Docker Executor 配置

`/etc/gitlab-runner/config.toml`：

```toml
[[runners]]
  url = "https://gitlab.com/"
  token = "xxxxxx"
  executor = "docker"
  [runners.docker]
    image = "alpine:latest"
    privileged = true
    volumes = ["/cache", "/var/run/docker.sock:/var/run/docker.sock"]
```

### 5.3 K8s Executor 配置（生产推荐）

```yaml
# Helm 安装 GitLab Runner
helm repo add gitlab https://charts.gitlab.io
helm install gitlab-runner gitlab/gitlab-runner \
  --set gitlabUrl=https://gitlab.com/ \
  --set runnerRegistrationToken=xxxxxx \
  --set rbac.create=true
```

---

## 六、CI/CD 变量管理

### 6.1 预定义变量

| 变量 | 说明 |
|------|------|
| `CI_COMMIT_REF_NAME` | 分支名 |
| `CI_COMMIT_SHORT_SHA` | commit SHA 短码 |
| `CI_PIPELINE_ID` | 流水线 ID |
| `CI_PROJECT_DIR` | 项目目录 |
| `CI_JOB_STAGE` | 当前阶段 |

### 6.2 自定义变量

```yaml
# 方式 1：在 .gitlab-ci.yml 中定义
variables:
  DATABASE_URL: "postgresql://..."

# 方式 2：在 GitLab UI 设置（Settings → CI/CD → Variables）
# 优先级：命令行 > UI 变量 > 文件变量
```

### 6.3 受保护变量

```text
Settings → CI/CD → Variables → Add Variable
- Key: DATABASE_PASSWORD
- Value: ******
- Type: Variable
- Protected: ✅ （隐藏 value）
- Masked: ✅ （日志中隐藏）
```

---

## 七、CI 模板与组件复用

### 7.1 模板（Template）

```yaml
.template-build: &template-build
  stage: build
  image: maven:3.9-openjdk-17
  script:
    - mvn clean package

build-job:
  <<: *template-build              # YAML 锚点引用
```

### 7.2 包含（Include）

```yaml
# 主 .gitlab-ci.yml
include:
  - local: 'ci/build.yml'
  - local: 'ci/test.yml'
  - local: 'ci/deploy.yml'
```

### 7.3 触发器（Trigger）

```yaml
# 多项目触发
trigger-job:
  stage: deploy
  trigger:
    project: myorg/another-project
    branch: main
```

---

## 八、Docker-in-Docker（构建镜像）

```yaml
package-job:
  stage: package
  image: docker:24
  services:
    - name: docker:24-dind           # 启动 DinD 服务
      alias: docker
  variables:
    DOCKER_TLS_CERTDIR: ""
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHORT_SHA .
    - docker push $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHORT_SHA
```

> **新方案**：Kaniko / Buildah 不需 Docker daemon，更安全。

---

## 九、GitLab CI/CD 高级特性

| 特性 | 说明 |
|------|------|
| **Auto DevOps** | 自动检测语言 + 自动构建/测试/部署 |
| **Review Apps** | 每个 MR 自动部署一个临时环境 |
| **GitLab Pages** | 静态网站托管 |
| **Container Scanning** | 镜像安全扫描 |
| **License Compliance** | 依赖许可证检查 |
| **Performance Testing** | k6 集成 |

---

## 十、最佳实践

1. **Pipeline as Code**：所有 .gitlab-ci.yml 进 Git
2. **缓存优化**：依赖缓存减少 50% 构建时间
3. **并行执行**：独立 Job 并行跑
4. **Artifact 管理**：构建产物保留时间合理（不要无限期）
5. **环境隔离**：dev / staging / prod 独立变量
6. **失败通知**：Slack / 钉钉 / 飞书 集成
7. **安全**：Secret 用 Protected Variables

---

← [返回 DevOps 总览](../README.md) · 📅 2026-06-28