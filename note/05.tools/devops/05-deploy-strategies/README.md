<!--
module:
  parent: tools
  slug: tools/deploy-strategies
  type: article
  category: 主模块子文章
  summary: 部署策略：蓝绿/金丝雀/灰度发布
-->

# 部署策略：蓝绿 / 金丝雀 / 灰度发布实战

> 一份按场景梳理的部署策略速查手册：从滚动更新到金丝雀的 5 大策略完整对比。

---
## 引言：反直觉代码

部署策略：蓝绿 / 金丝雀 / 灰度发布实战 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、为什么需要部署策略？

每次部署都是"上线风险"：
- ❌ 直接全量发布 → 100% 用户受影响（如果有问题）
- ❌ 出问题再回滚 → 平均回滚时间 30 分钟 + 用户体验受损

**好部署策略的目标**：
- ✅ 部署期间用户无感知（零停机）
- ✅ 出问题快速回滚（< 1 分钟）
- ✅ 灰度验证（5% → 50% → 100%）

---

## 二、5 大部署策略对比

| 策略 | 零停机 | 快速回滚 | 灰度能力 | 资源消耗 | 复杂度 |
|------|--------|---------|---------|---------|--------|
| **Recreate**（停机部署）| ❌ | ✅ | ❌ | 低 | 低 |
| **Rolling Update**（滚动）| ✅ | 中 | ❌ | 低 | 中 |
| **Blue-Green**（蓝绿）| ✅ | ✅ 秒级 | ❌ | 2 倍 | 中 |
| **Canary**（金丝雀）| ✅ | ✅ | ✅ | 中 | 高 |
| **A/B Testing**（A/B 测试）| ✅ | ✅ | ✅✅ | 中 | 高 |

---

## 三、Recreate（停机部署）

```
v1 ─────┐
        ↓ 停机
v2 ─────┘
```

- **流程**：停 v1 → 启动 v2
- **优点**：最简单
- **缺点**：有停机时间，不可用
- **场景**：开发环境、内部工具、不重要的服务

---

## 四、Rolling Update（滚动更新）— K8s 默认

```
v1 [v1] [v1] [v1]
   ↓
v2 [v2] [v1] [v1]
   ↓
   [v2] [v2] [v1]
   ↓
   [v2] [v2] [v2]
```

- **流程**：逐个替换 Pod（默认 25% 并行）
- **优点**：零停机、资源不增
- **缺点**：回滚慢、新旧版本共存可能冲突
- **场景**：无状态服务、API 服务

### K8s 配置

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1                  # 最多超出 1 个 Pod
      maxUnavailable: 0            # 不可用为 0
```

---

## 五、Blue-Green（蓝绿部署）

```
        Load Balancer
             │
   ┌─────────┴─────────┐
   ↓                   ↓
[Blue v1]           [Green v2]   ← v2 部署但不接流量
   ↓
[Blue v1 only]   ← 流量切换
   ↓
                   [Green v2 only]  ← 切流量到 Green
   ↓
              [Green v2 only]   ← v1 缩容
```

- **流程**：部署 v2 到 Green 环境 → 验证 → 切流量 → 缩容 v1
- **优点**：零停机、回滚秒级（切回 Blue）
- **缺点**：资源 2 倍（两套环境同时运行）
- **场景**：关键业务、大版本发布

### K8s 实现（用 Service selector）

```yaml
# v1 service
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
    version: v1                  # 指向 v1 Pod
  ports:
  - port: 80

# 切换时：修改 selector
# selector:
#   version: v2                  # 切到 v2 Pod
```

---

## 六、Canary（金丝雀发布）

```
v1: [v1] [v1] [v1] [v1]  ← 90% 流量
v2: [v2]                   ← 10% 流量（金丝雀）

↓ 验证通过，逐步放量
v1: [v1] [v1] [v1]        ← 75%
v2: [v2] [v2]            ← 25%

↓ 继续放量
v1: [v1] [v1]            ← 50%
v2: [v2] [v2]            ← 50%

↓ 全部切换
v2: [v2] [v2] [v2] [v2]  ← 100%
```

- **流程**：v2 部署 5% 流量 → 验证 → 25% → 50% → 100%
- **优点**：风险最小、可随时回滚
- **缺点**：配置复杂、需要智能流量切分
- **场景**：高频发布、A/B 测试、新功能验证

### K8s + Istio 实现

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts:
  - my-app
  http:
  - match:
    - headers:
        x-user-group:
          exact: "beta-users"      # 给特定用户开 beta
    route:
    - destination:
        host: my-app-v2
      weight: 100
  - route:
    - destination:
        host: my-app-v1
      weight: 90
    - destination:
        host: my-app-v2
      weight: 10
```

详见：[08-operator-and-gitops](../kubernetes/08-operator-and-gitops/README.md) 的 Istio VirtualService 示例。

### 简易 K8s 实现（用 2 个 Deployment）

```yaml
# v1 Deployment + Service（90% 流量）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-v1
spec:
  replicas: 9                      # 9 个 v1 Pod
  selector:
    matchLabels:
      app: my-app
      version: v1
  template:
    metadata:
      labels:
        app: my-app
        version: v1
    spec:
      containers:
      - name: app
        image: my-app:v1
---
# v2 Deployment + Service（10% 流量，金丝雀）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-v2
spec:
  replicas: 1                      # 1 个 v2 Pod
  selector:
    matchLabels:
      app: my-app
      version: v2
  template:
    metadata:
      labels:
        app: my-app
        version: v2
    spec:
      containers:
      - name: app
        image: my-app:v2
---
# 顶层 Service：负载均衡 v1 + v2 Pod
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app                    # 同时选 v1 + v2
  ports:
  - port: 80
```

---

## 七、A/B Testing（A/B 测试）

```
对照组 v1: 50% 流量
实验组 v2: 50% 流量
   ↓ 收集数据（转化率、跳出率）
根据统计显著性决定胜负
```

| Canary | A/B Testing |
|--------|------------|
| 验证部署稳定性 | 验证功能价值 |
| 短期（分钟-小时） | 长期（天-周） |
| 关注错误率 / 性能 | 关注业务指标（转化） |
| 流量不均（5%-100%） | 流量均分（50/50） |

---

## 八、Feature Flag（功能开关）

与部署策略配合使用，让"代码已部署但功能未启用"成为可能。

### 8.1 主流工具

| 工具 | 类型 |
|------|------|
| **LaunchDarkly** | SaaS（付费）|
| **Unleash** | 开源 |
| **Flagsmith** | 开源 + SaaS |
| **自研（数据库表）** | 简单场景 |

### 8.2 实现示例（Unleash）

```javascript
// 代码中
if (unleash.isEnabled('new-feature', context)) {
  // 新功能
} else {
  // 老功能
}

// 不用部署，通过控制台开关
// new-feature: enabled 5% → 25% → 100%
```

**优势**：紧急回滚只需关开关（5 秒），不用重新部署。

---

## 九、5 大策略选型决策

```
Q1: 能否容忍 1 分钟停机？
├── 是 → Recreate
└── 否 ↓

Q2: 是否需要灰度发布？
├── 否 → Blue-Green（秒级回滚）
└── 是 ↓

Q3: 是否需要按用户/区域分流？
├── 否 → Canary（按比例）
└── 是 ↓

Q4: 是否要做 A/B 测试（业务验证）？
├── 否 → Canary + Feature Flag
└── 是 → A/B Testing + Feature Flag

Q5: 资源是否充足？
├── 否 → Rolling Update
└── 是 → 任意策略
```

---

## 十、最佳实践

1. **无状态服务**：默认用 K8s Rolling Update（最简单）
2. **关键业务**：Blue-Green + 自动回滚脚本
3. **高频发布**：Canary + Feature Flag（Netflix 模式）
4. **A/B 验证**：用 LaunchDarkly / Unleash
5. **数据库迁移**：单独策略（Flyway / Liquibase），与代码解耦
6. **回滚演练**：每月做一次回滚演练（确保真能用）
7. **监控告警**：部署后 5 分钟内必须无错误率飙升

---

← [返回 DevOps 总览](../README.md) · 📅 2026-06-28