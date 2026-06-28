# CI/CD 流水线设计模式：分支策略与多环境管理

> 一份按层次梳理的流水线设计速查手册：从分支策略到多环境管理的最佳实践。

---

## 一、为什么需要"流水线设计模式"？

没有设计模式的 CI/CD 流水线：
- ❌ 团队 A 用 Git Flow，B 用 trunk-based，互相看不懂
- ❌ 测试环境每天在编译 100 个版本，浪费 50% 算力
- ❌ 部署到生产要 5 个人手动确认 2 小时
- ❌ 回滚要翻半天 git log

有设计模式的 CI/CD 流水线：
- ✅ 全团队统一分支策略
- ✅ 环境分层清晰（dev / staging / prod）
- ✅ 部署自动化，一键回滚
- ✅ 监控告警完善

---

## 二、3 大分支策略对比

### 2.1 Git Flow（重型）

```
master ────────────────────────────────────────────
        │                  ↑                ↑
        │                  │ Merge          │ Merge
        │                  │                │
release ────────  ←─────────────────────────────
        │          ↑
        │ Merge    │
        ↓          │
develop ───────────────────────────────────────
        │                ↑
        │ Merge          │ Feature branch
        ↓                │
feature/* ──────  ─────────────────────────────
```

| 阶段 | 操作 |
|------|------|
| 开发 | feature/* → develop |
| 测试 | develop → release |
| 发布 | release → master + tag |
| 修复 | hotfix → master + develop |

**适用**：版本化发布的产品（如 SDK / 移动 App）|
**缺点**：分支多、合并复杂、不适合持续部署

### 2.2 GitHub Flow（轻量）

```
main ────────────────────────────────────────────
  │        ↑        ↑        ↑
  │        │ Merge  │        │
  │        │        │        │
feature ──  ──────  ──────  ────────  ──────────
```

| 阶段 | 操作 |
|------|------|
| 开发 | feature → main（PR + Review） |
| 部署 | main → production |
| 回滚 | revert commit |

**适用**：SaaS / Web 应用（持续部署） |
**优点**：简单、PR 即 Review、CD 友好

### 2.3 Trunk-Based Development（极简）

```
main ────────────────────────────────────────────
  │        ↑        ↑        ↑
  │        │ Merge  │        │
  │        │        │        │
feature ──  ──────  ──────  ────────
       (短生命周期,<1天)
```

- 所有改动直接进 main（短生命周期 feature branch）
- 用 Feature Flag 控制发布
- 不做"分支管理"，做"代码管理"

**适用**：DevOps 成熟团队（Google / Facebook 模式）|
**优点**：最简单、最适合 CI/CD

### 2.4 选型对比

| 维度 | Git Flow | GitHub Flow | Trunk-Based |
|------|---------|-------------|-------------|
| 复杂度 | 高 | 中 | 低 |
| 发布频率 | 周/月级 | 日级 | 持续 |
| 团队规模 | 大团队 | 中小 | 任意 |
| 适合 | 移动 App / SDK | SaaS | 高成熟度团队 |

---

## 三、多环境管理

### 3.1 环境分层标准

```
┌──────────────────────────────────────────────┐
│  Production（生产）—— 真实用户                    │
│   └─ 部署频率：每天多次 / 周级                    │
│   └─ 准入门槛：人工审批 + 自动化测试 100%         │
└──────────────────────────────────────────────┘
                     ↑
┌──────────────────────────────────────────────┐
│  Staging（预生产）—— 真实数据镜像                  │
│   └─ 部署频率：每次 main commit                  │
│   └─ 准入门槛：自动化测试通过                    │
└──────────────────────────────────────────────┘
                     ↑
┌──────────────────────────────────────────────┐
│  Dev（开发）—— 开发者自测                        │
│   └─ 部署频率：每个 PR                          │
│   └─ 准入门槛：编译 + 单元测试通过                │
└──────────────────────────────────────────────┘
```

### 3.2 GitLab CI 多环境配置

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

# 通用作业模板
.build_template:
  stage: build
  script:
    - mvn clean package
  artifacts:
    paths:
      - target/*.jar

# Dev 环境（自动部署）
deploy-dev:
  stage: deploy
  script:
    - kubectl apply -f k8s/dev/
  environment:
    name: dev
    url: https://dev.example.com
  rules:
    - if: $CI_MERGE_REQUEST_ID   # PR 时部署

# Staging 环境（main 分支自动）
deploy-staging:
  stage: deploy
  script:
    - kubectl apply -f k8s/staging/
  environment:
    name: staging
    url: https://staging.example.com
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

# Prod 环境（手动确认 + tag）
deploy-prod:
  stage: deploy
  script:
    - kubectl apply -f k8s/prod/
  environment:
    name: production
    url: https://www.example.com
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
  when: manual                    # 手动确认
```

### 3.3 GitHub Actions 多环境配置

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: ${{ github.ref == 'refs/heads/main' && 'staging' || 'dev' }}
      url: ${{ github.ref == 'refs/heads/main' && 'https://staging.example.com' || 'https://dev.example.com' }}
    steps:
      - run: echo "Deploying..."
```

---

## 四、PR 流水线设计

### 4.1 PR 触发的流水线目标

```
每个 PR 必须验证：
  ① 编译通过
  ② 单元测试通过（覆盖率达标）
  ③ 代码扫描（SAST）无严重问题
  ④ 集成测试通过
  ⑤ Docker 镜像构建成功
  ⑥ Preview 环境部署成功（可选）
```

### 4.2 GitLab CI PR 流水线示例

```yaml
pr-pipeline:
  stage: test
  script:
    - mvn verify
    - sonar-scanner
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

preview-deploy:
  stage: deploy
  script:
    - kubectl apply -f preview/
    - echo "Preview: https://pr-$CI_MERGE_REQUEST_IID.example.com"
  environment:
    name: review/pr-$CI_MERGE_REQUEST_IID
    on_stop: cleanup-preview
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

---

## 五、Tag 发布流水线

### 5.1 语义化版本（SemVer）

```
v1.2.3
│ │ │
│ │ └─ Patch（补丁）：Bug 修复
│ └─── Minor（次版本）：新功能（向后兼容）
└───── Major（主版本）：破坏性变更
```

### 5.2 Tag 触发部署

```yaml
# GitLab CI
deploy-prod:
  stage: deploy
  script:
    - kubectl apply -f k8s/prod/
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
```

```yaml
# GitHub Actions
on:
  push:
    tags:
      - 'v*'
```

---

## 六、构建缓存与加速

### 6.1 GitLab CI 缓存

```yaml
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .m2/repository/             # Maven 依赖
    - node_modules/                # Node 依赖
    - .gradle/caches/             # Gradle 缓存
```

### 6.2 GitHub Actions 缓存

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'npm'                  # 自动缓存

- uses: actions/cache@v4
  with:
    path: ~/.gradle/caches
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}
```

**效果**：构建时间减少 50-70%。

---

## 七、并行执行策略

### 7.1 Pipeline 并行

```
传统串行：build → test → deploy（30 分钟）
现代并行：build + lint + security scan（5 分钟）→ test → deploy（15 分钟）
```

### 7.2 GitLab CI

```yaml
stages:
  - checks
  - build
  - test
  - deploy

# checks 阶段 3 个 job 并行
lint:
  stage: checks
  script: npm run lint

security:
  stage: checks
  script: npm audit

sast:
  stage: checks
  script: sonar-scanner
```

### 7.3 GitHub Actions Matrix

```yaml
jobs:
  test:
    strategy:
      matrix:
        node: [18, 20, 22]
        os: [ubuntu, macos, windows]
    runs-on: ${{ matrix.os }}-latest
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

---

## 八、流水线模板化（避免重复）

### 8.1 GitLab CI 模板

```yaml
# .gitlab-ci.yml
include:
  - local: 'ci/templates/.maven.yml'
  - local: 'ci/templates/.docker.yml'
  - local: 'ci/templates/.deploy.yml'
```

### 8.2 GitHub Actions 可复用工作流

```yaml
# .github/workflows/reusable-ci.yml
name: Reusable CI
on:
  workflow_call:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test

# 使用
# .github/workflows/ci.yml
name: Project CI
on: [push]
jobs:
  ci:
    uses: ./.github/workflows/reusable-ci.yml
```

---

## 九、流水线监控与告警

| 指标 | 监控工具 |
|------|---------|
| 流水线成功率 | GitLab / GitHub 内置 |
| 构建时长 | Prometheus + Grafana |
| 失败原因分类 | Sentry / ELK |
| 队列等待 | Runner 监控 |

---

## 十、最佳实践

1. **Pipeline as Code**：所有 .yml 进 Git，禁用 UI 配置
2. **统一分支策略**：全团队用同一套（推荐 GitHub Flow + Trunk-based）
3. **多环境分层**：dev / staging / prod 严格分层
4. **PR 流水线 + main 流水线**：分离 PR 验证和生产部署
5. **构建缓存**：依赖缓存减少 50% 构建时间
6. **并行执行**：独立 Job 并行，总时间减半
7. **模板化**：CI 模板 / Action 复用，减少维护成本
8. **监控告警**：流水线失败立即通知

---

← [返回 DevOps 总览](../README.md) · 📅 2026-06-28