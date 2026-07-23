<!--
module:
  parent: tools
  slug: tools/github-actions
  type: article
  category: 主模块子文章
  summary: GitHub Actions 云原生 CI/CD——从最小工作流到 Matrix 构建 / OIDC 凭证 / 自托管 Runner 的完整实战。
-->

# GitHub Actions · 云原生 CI/CD 实战

> 一份按场景梳理的 GitHub Actions 速查手册：从基础工作流到企业级 DevOps 的完整实战。

---
---

## 一、GitHub Actions 简介

GitHub Actions 是 GitHub 内置的 CI/CD 工具，与 GitHub 代码托管无缝集成。

### 1.1 核心特性

- **零配置**：GitHub 仓库自带 CI/CD 能力
- **市场丰富**：GitHub Marketplace 有 16000+ 预制 Action
- **免费额度**：公开仓库无限，私有仓库每月 2000 分钟
- **Runner 可自托管**：GitHub-hosted Runner 或自托管 Runner
- **Matrix 构建**：天然支持多平台/多版本并行构建

### 1.2 适用场景

- ✅ GitHub 用户
- ✅ 开源项目
- ✅ 中小团队
- ✅ Matrix 多平台测试
- ❌ 不在 GitHub 上的代码（推荐 GitLab CI / Jenkins）

---

## 二、核心概念

| 概念 | 说明 |
|------|------|
| **Workflow** | 一个 `.github/workflows/*.yml` 文件定义一个工作流 |
| **Job** | 工作流中的一个任务（一组 Steps） |
| **Step** | 任务中的一个具体步骤（运行命令或调用 Action） |
| **Action** | 可复用的步骤（GitHub Marketplace 或自建） |
| **Runner** | 实际执行工作流的运行环境 |
| **Event** | 触发工作流的事件（push / PR / schedule） |

---

## 三、最小工作流

### 3.1 文件位置

```text
.github/workflows/ci.yml
```

### 3.2 Hello World

```yaml
name: CI

on: [push, pull_request]

jobs:
  hello:
    runs-on: ubuntu-latest
    steps:
      - name: Say Hello
        run: echo "Hello GitHub Actions!"
```

---

## 四、完整 CI/CD 工作流示例

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  DOCKER_REGISTRY: ghcr.io
  APP_NAME: myapp

jobs:
  # 1. 测试
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Code coverage
        run: npm run coverage

  # 2. 代码质量
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm run lint

  # 3. 构建并推送镜像
  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.DOCKER_REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.DOCKER_REGISTRY }}/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=sha,prefix=git-

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  # 4. 部署到 staging
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - uses: actions/checkout@v4

      - name: Setup kubectl
        uses: azure/setup-kubectl@v4

      - name: Deploy to staging
        run: |
          echo "${{ secrets.KUBE_CONFIG_STAGING }}" | base64 -d > /tmp/kubeconfig
          KUBECONFIG=/tmp/kubeconfig kubectl apply -f k8s/
          KUBECONFIG=/tmp/kubeconfig kubectl rollout status deployment/myapp -n staging

  # 5. 部署到生产（手动确认）
  deploy-prod:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://www.example.com
    steps:
      - name: Deploy to production
        run: |
          echo "${{ secrets.KUBE_CONFIG_PROD }}" | base64 -d > /tmp/kubeconfig
          KUBECONFIG=/tmp/kubeconfig kubectl apply -f k8s/
          KUBECONFIG=/tmp/kubeconfig kubectl rollout status deployment/myapp -n production
```

---

## 五、核心 Action 速查

| Action | 用途 |
|--------|------|
| `actions/checkout@v4` | 拉取代码 |
| `actions/setup-node@v4` | 配置 Node.js |
| `actions/setup-python@v5` | 配置 Python |
| `actions/setup-java@v4` | 配置 Java |
| `actions/setup-go@v5` | 配置 Go |
| `actions/cache@v4` | 缓存依赖 |
| `actions/upload-artifact@v4` | 上传工件 |
| `actions/download-artifact@v4` | 下载工件 |
| `docker/login-action@v3` | Docker 登录 |
| `docker/build-push-action@v5` | Docker 构建推送 |
| `azure/setup-kubectl@v4` | 配置 kubectl |

---

## 六、Matrix 多平台构建

```yaml
test:
  runs-on: ${{ matrix.os }}
  strategy:
    matrix:
      os: [ubuntu-latest, macos-latest, windows-latest]
      node: [18, 20, 22]
    fail-fast: false              # 不让单个失败中断其他
    max-parallel: 3

  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node }}
    - run: npm test
```

效果：3 OS × 3 Node 版本 = 9 个并行任务。

---

## 七、Secrets 与环境管理

### 7.1 Secrets（密钥）

```text
Settings → Secrets and variables → Actions → New repository secret
- DOCKER_PASSWORD
- KUBE_CONFIG_PROD
- DATABASE_URL
```

```yaml
steps:
  - run: echo "${{ secrets.DOCKER_PASSWORD }}" | docker login ...
```

### 7.2 Environment（环境）

```text
Settings → Environments → New environment
- staging: 需要 reviewer（可选）
- production: 需要 2 个 reviewer
```

```yaml
deploy-prod:
  environment:
    name: production
    url: https://www.example.com
```

---

## 八、自托管 Runner

### 8.1 为什么需要自托管？

- 免费 Runner 配置固定（2 核 7G）
- 需要特殊环境（GPU / 大内存 / 内网访问）
- 数据合规（不能上传 GitHub）

### 8.2 添加 Runner

> **前置条件**：
> - GitHub org/repo admin 权限
> - Runner 机器需能访问 github.com（443 端口）
> - 建议配置：2C4G+（自托管 Runner）
> - 已安装 git / Docker（按需）

```bash
# 在你的服务器上
mkdir actions-runner && cd actions-runner

# 下载
curl -o actions-runner-linux-x64-2.319.1.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.319.1/actions-runner-linux-x64-2.319.1.tar.gz

tar xzf ./actions-runner-linux-x64-2.319.1.tar.gz

# 配置
./config.sh --url https://github.com/myorg/myrepo --token XXXXXX

# 运行（作为服务）
sudo ./svc.sh install
sudo ./svc.sh start
```

工作流中指定：

```yaml
jobs:
  build:
    runs-on: self-hosted           # 使用自托管 Runner
    # 或：runs-on: [self-hosted, gpu]   # 带标签
```

---

## 九、GitHub Actions vs Jenkins vs GitLab CI

| 维度 | GitHub Actions | Jenkins | GitLab CI |
|------|---------------|---------|-----------|
| 集成度 | GitHub 一体化 | 独立 | GitLab 一体化 |
| 学习曲线 | 低 | 中 | 中 |
| 插件市场 | 16000+ Actions | 1800+ | GitLab 内置 |
| 自托管 Runner | ✅ | ✅（Agent） | ✅（Runner） |
| 免费额度 | 公开无限 / 私有 2000 分钟/月 | 全免费（自建） | 400 分钟/月 |
| 适合 | GitHub / 中小 | 大企业 / 复杂 | GitLab / 中型 |

---

## 十、最佳实践

1. **Workflow as Code**：所有 `.yml` 进 Git，禁用手动触发
2. **缓存**：用 `actions/cache` 减少构建时间 50%+
3. **并行**：独立 Job 用 matrix 并行执行
4. **环境隔离**：dev / staging / prod 用独立 Environment
5. **Secrets 保护**：用 Masked Secrets + Environment Protection
6. **OIDC 代替长期凭证**：AWS / Azure 集成推荐 OIDC
7. **自托管 Runner**：大内存 / GPU / 内网访问场景

---

← [返回 DevOps 总览](../README.md) · 📅 2026-06-28