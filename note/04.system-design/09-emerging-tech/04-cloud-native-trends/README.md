# 云原生 2026 趋势：Serverless / AI 基础设施 / 平台工程

> 一份按技术趋势梳理的云原生速查手册：从 Serverless 到 AI 基础设施的演进全景。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

云原生 2026 趋势：Serverless / AI 基础设施 / 平台工程 本应该很简单，一份按技术趋势梳理的云原生速查手册：从 Serverless 到 AI 基础设施的演进全景

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、2026 云原生 4 大趋势

1. **Serverless 化**：K8s + Serverless 混合部署
2. **AI 基础设施**：GPU 池化 / LLM 推理服务化
3. **平台工程（Platform Engineering）**：内部开发者平台（IDP）
4. **可观测性 2.0**：eBPF + OpenTelemetry + AI 增强

---

## 二、Serverless 演进

### 2.1 Serverless 三大形态

| 形态 | 特点 | 典型 |
|------|------|------|
| **FaaS（函数即服务）** | 事件触发 / 自动扩缩 | AWS Lambda / Azure Functions |
| **BaaS（后端即服务）** | 托管数据库 / 消息队列 | DynamoDB / Firebase |
| **Serverless K8s** | 容器 + 自动扩缩 | Knative / KEDA / Vercel |

### 2.2 Knative 实战

```yaml
# Knative Service
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - image: myapp:1.0
        resources:
          limits:
            memory: 512Mi
      # 缩容到 0（无请求时）
      autoscaling:
        minScale: 0
        maxScale: 100
```

**效果**：无请求时缩容到 0 → 节省 100% 资源；有请求时秒级冷启动。

### 2.3 KEDA（事件驱动扩缩容）

```yaml
# 基于 Kafka 队列长度扩缩
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: kafka-scaler
spec:
  scaleTargetRef:
    name: my-app
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka:9092
      consumerGroup: my-group
      topic: my-topic
      lagThreshold: "10"   # 队列长度 > 10 就扩
```

---

## 三、AI 基础设施（2026 最热趋势）

### 3.1 GPU 池化

```
传统：1 个 Pod 绑 1 张 GPU（浪费）
现代：GPU 共享 / 切分（MIG / vGPU / time-slicing）
```

#### 方案 1：NVIDIA MIG（Multi-Instance GPU）

```bash
# 把 A100 切成 7 个 MIG 实例
nvidia-smi mig -cgi 0,0,0,0,0,9,1,7
```

#### 方案 2：vGPU（虚拟 GPU）

- **NVIDIA vGPU**（商业）
- **HAMi**（开源）—— 国产开源 GPU 池化

#### 方案 3：Time-Slicing

```yaml
# K8s GPU time-slicing
apiVersion: v1
kind: ConfigMap
metadata:
  name: nvidia-device-plugin
data:
  config.yaml: |
    sharing:
      timeSlicing:
        resources:
        - name: nvidia.com/gpu
          replicas: 4   # 1 张卡当 4 张用
```

### 3.2 LLM 推理服务化

#### vLLM（推荐）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        args:
        - --model=meta-llama/Llama-3-70B-Instruct
        - --tensor-parallel-size=4
        - --gpu-memory-utilization=0.95
        resources:
          limits:
            nvidia.com/gpu: 4
        ports:
        - containerPort: 8000
```

#### 推理路由（智能路由）

```yaml
# 按 query 复杂度路由到不同模型
- 简单问题 → Llama-3-8B（快 + 便宜）
- 复杂问题 → GPT-4 / Claude Opus（慢 + 贵）
```

详见 [`11.ai/07-llmops`](../../11.ai/07-llmops/02-llmops-stack/README.md)

### 3.3 国产 GPU 适配

| 国产 GPU | 厂商 | 适配框架 |
|---------|------|---------|
| 昇腾（Ascend）| 华为 | CANN / MindSpore |
| 寒武纪 | 寒武纪 | Cambricon SDK |
| 海光（DCU）| 海光 | ROCm 兼容 |
| 壁仞 | 壁仞 | 自研 BIREN |

---

## 四、平台工程（Platform Engineering）

### 4.1 什么是平台工程？

**内部开发者平台（IDP）**：让开发者自助完成"非业务工作"（部署 / 监控 / 密钥），专注业务代码。

```
传统：开发者要懂 K8s / Docker / CI / 监控
  ↓
平台工程：内部平台封装复杂性，开发者点几个按钮即可
```

### 4.2 4 大 IDP 工具

| 工具 | 类型 |
|------|------|
| **Backstage**（Spotify 出品，CNCF）| 开发者门户 |
| **Humanitec** | 平台编排 |
| **Port** | IDP 平台 |
| **Kratix**（Syntasso）| 平台工程框架 |

### 4.3 Backstage 实战

```yaml
# software-catalog.yaml（开发者门户）
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: my-service
  description: 我的订单服务
spec:
  type: service
  lifecycle: production
  owner: team-a
  system: order-system
  providesApis:
  - my-service-api
  dependsOn:
  - component:default/postgres
```

**功能**：
- 服务目录（所有服务一览）
- 技术文档自动生成
- 服务健康度（oncall / owner）
- CI/CD 状态

### 4.4 IDP 黄金路径

```
开发者 → IDP 平台 → 选择模板 → 填表单 → 自动创建
   ↓
  Git 仓库 + K8s 部署 + 监控 + 域名 + 文档
   ↓
  5 分钟完成"开箱即用"的新服务
```

---

## 五、可观测性 2.0（eBPF + AI 增强）

详见 [`08-observability`](../08-observability/README.md) + [`01-ebpf`](../01-ebpf/README.md)

### 5.1 OpenTelemetry（OTel）一统江湖

```
传统：
  - Prometheus（指标）
  - Jaeger（链路追踪）
  - ELK（日志）
  各自为政，难以关联

OpenTelemetry（OTel）：
  - 统一 SDK（采集指标 / 链路 / 日志）
  - 统一数据格式（OTLP）
  - 统一后端（可发到任意厂商）
```

### 5.2 OTel + eBPF 自动埋点

```
传统：业务代码手动加 SDK
  ↓
eBPF 自动埋点：
  - HTTP/gRPC 调用自动追踪
  - 数据库查询自动捕获
  - 系统调用关联业务 Trace
```

### 5.3 AI 增强的可观测

- **异常检测**：AI 自动发现异常（如突增的 P99 延迟）
- **根因分析**：AI 定位故障源（"80% 是数据库慢查询"）
- **预测性告警**：AI 预测未来 1 小时会出问题

---

## 六、其他重要趋势

### 6.1 WebAssembly（WASM）进入云原生

- 边缘计算（Cloudflare Workers / Fastly）
- 插件系统（Envoy WASM Filter）
- 详情见 [`02-wasm`](../02-wasm/README.md)

### 6.2 FinOps 成熟

- 实时成本监控（Kubecost / OpenCost）
- 自动化成本优化（spot instance / 自动缩容）
- FinOps 团队组织化

### 6.3 供应链安全（SLSA / Sigstore）

| 工具 | 用途 |
|------|------|
| **SLSA** | 供应链安全等级（Google）|
| **Sigstore** | 镜像签名（Cosign）|
| **SBOM** | 软件物料清单（CycloneDX / SPDX）|
| **in-toto** | 供应链完整性验证 |

### 6.4 绿色云原生（GreenOps）

- 碳排放监控（KubeGreen）
- 能耗优化（CPU 动态调频）
- 区域选择（清洁能源）

---

## 七、未来 3 年（2026-2028）展望

| 年份 | 趋势 |
|------|------|
| **2026** | GPU 池化成熟 / LLM 推理服务化 / 平台工程普及 |
| **2027** | Sidecarless Service Mesh 主流 / AI 增强可观测 |
| **2028** | Serverless K8s 标准化 / WASM 大规模生产 |

---

## 八、最佳实践

1. **混合部署**：K8s 长期服务 + Serverless 短任务
2. **GPU 池化**：生产必备（节省 50%+ GPU 成本）
3. **IDP 建设**：100+ 工程师的公司必备
4. **OpenTelemetry**：2026 必采纳（不再选型）
5. **供应链安全**：SBOM + 镜像签名（金融 / 政府强制）
6. **FinOps 团队**：成本优化专职
7. **可观测优先**：上 Mesh / 微服务前先做监控
8. **AI 增强**：让 AI 帮运维（自动诊断 / 自动告警）

---

← [返回系统设计总览](../../README.md) · 📅 2026-06-28