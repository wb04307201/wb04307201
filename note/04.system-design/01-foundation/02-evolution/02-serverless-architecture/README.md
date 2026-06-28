# Serverless 架构：FaaS / BaaS / Knative 全场景实战

> 一份按形态梳理的 Serverless 速查手册：从函数即服务到边缘计算的完整实战。

---

## 一、什么是 Serverless？

Serverless 不是"没有服务器"，而是**"开发者不需要管理服务器"** —— 云厂商负责资源分配、扩缩、运维。

### 1.1 核心特性

- ✅ **按需付费**：不用不花钱（按调用 / 按时长）
- ✅ **自动扩缩**：0 → 1000 并发（毫秒级）
- ✅ **免运维**：不用管服务器 / K8s / 操作系统
- ⚠️ **冷启动**：首次调用有 100-500ms 延迟
- ⚠️ **厂商绑定**：每个云厂商 API 不同

### 1.2 与传统架构对比

| 维度 | 传统 VM | 容器（K8s）| Serverless |
|------|--------|----------|-----------|
| 启动时间 | 分钟 | 秒 | **毫秒** |
| 扩缩容 | 人工 / 脚本 | 自动（30s）| 自动（毫秒）|
| 运维成本 | 高 | 中 | **零** |
| 计费 | 包月 | 包月 | **按调用** |
| 适合 | 长期运行 | 中长期 | 短任务 / 突发 |

---

## 二、Serverless 三大形态

### 形态 1：FaaS（Function as a Service）

```
事件触发 → 函数执行 → 计费
   ↓
例：图片上传 → 触发 resize 函数 → 保存缩略图
```

| 平台 | 特点 |
|------|------|
| **AWS Lambda** | 最早 / 生态最丰富 |
| **Azure Functions** | 微软生态 / VS Code 集成 |
| **Google Cloud Functions** | GCP 生态 |
| **阿里云函数计算 FC** | 国产 / 阿里云生态 |
| **腾讯云 SCF** | 国产 / 腾讯云生态 |

### 形态 2：BaaS（Backend as a Service）

```
后端服务完全托管：
  - 数据库（DynamoDB / Firebase）
  - 消息队列（SQS / Pub-Sub）
  - 存储（S3 / OSS）
  - 认证（Cognito / 阿里云 IDaaS）
```

### 形态 3：Serverless 容器（Knative / KEDA）

```
K8s 上的 Serverless：
  - 流量为 0 → Pod 缩容到 0
  - 流量来 → 1 秒内启动 Pod
  - 流量走 → 5 分钟后自动缩容
```

**优势**：兼容 K8s 生态 + 自动扩缩

---

## 三、AWS Lambda 实战

### 3.1 Hello World

```python
import json

def lambda_handler(event, context):
    name = event.get('name', 'World')
    return {
        'statusCode': 200,
        'body': json.dumps(f'Hello, {name}!')
    }
```

### 3.2 触发器（事件源）

| 触发器 | 场景 |
|--------|------|
| **API Gateway** | HTTP 请求 |
| **S3** | 文件上传 |
| **DynamoDB Streams** | 数据变更 |
| **SQS** | 消息队列 |
| **EventBridge** | 定时 / 跨服务事件 |
| **CloudWatch** | 告警触发 |

### 3.3 Lambda 限制

| 限制 | 值 |
|------|-----|
| 内存 | 128 MB - 10 GB |
| 超时 | 最长 15 分钟 |
| 并发 | 默认 1000（可申请提高）|
| 部署包 | 50 MB（zip）/ 250 MB（容器镜像）|

### 3.4 冷启动优化

```yaml
# 启用 Provisioned Concurrency（预置并发）
# Lambda 预热实例，零冷启动

# 或用 SnapStart（Java 专用）
# 初始化一次，后续调用复用内存
```

---

## 四、Knative 实战（K8s 上的 Serverless）

### 4.1 核心组件

```
┌──────────────────────────────────────┐
│  Knative Serving                        │
│  ┌─────────┐  ┌─────────┐             │
│  │ Service │  │Revision │             │
│  │ 服务配置  │  │版本快照  │             │
│  └─────────┘  └─────────┘             │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│  Knative Eventing                      │
│  ┌─────────┐  ┌─────────┐             │
│  │ Broker  │  │ Trigger │             │
│  │ 事件路由  │  │事件触发  │             │
│  └─────────┘  └─────────┘             │
└──────────────────────────────────────┘
```

### 4.2 Knative Service 部署

```bash
# 安装 Knative
kubectl apply -f https://github.com/knative/serving/releases/latest/download/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/latest/download/serving-core.yaml
```

```yaml
# Knative Service 配置
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
      # 缩容到 0
      autoscaling:
        minScale: 0
        maxScale: 100
        target: 70   # CPU 目标 70%
```

### 4.3 KEDA 事件驱动扩缩

```yaml
# KEDA 基于 Kafka 队列扩缩容
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: kafka-consumer
spec:
  scaleTargetRef:
    name: my-consumer
  pollingInterval: 10
  cooldownPeriod: 30
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka:9092
      consumerGroup: my-group
      topic: orders
      lagThreshold: "100"
```

---

## 五、Cloudflare Workers（边缘 Serverless）

### 5.1 核心优势

- **冷启动 < 5ms**（V8 isolate）
- **99% 请求 < 50ms**
- 全球 200+ 边缘节点
- 免费额度：10 万次/天

### 5.2 Hello World

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  return new Response('Hello from edge!', {
    headers: { 'content-type': 'text/plain' }
  });
});
```

### 5.3 适用场景

- API 路由 / 反向代理
- A/B 测试（边缘）
- 地理限制
- Bot 防护
- 简单图像处理

---

## 六、4 大生产最佳实践

### 6.1 函数设计原则

| 原则 | 说明 |
|------|------|
| **单一职责** | 一个函数 = 一个功能 |
| **无状态** | 不在函数内保存状态（用外部存储）|
| **幂等性** | 多次调用结果相同（防重试）|
| **快速启动** | 减少依赖（缩短冷启动）|

### 6.2 冷启动优化

```yaml
# 1. 减小部署包
- 只包含必要依赖
- 使用 Lambda Layers 共享依赖

# 2. 预置并发
- 启用 Provisioned Concurrency
- 适用于"启动慢"的运行时（Java / .NET）

# 3. 优化初始化
- 减少启动时网络调用
- 预热 SDK 客户端
```

### 6.3 监控与调试

```yaml
# 关键指标
- 调用次数 / 错误率 / 延迟
- 并发数 / 限流触发次数
- 冷启动次数 / 冷启动延迟
- 内存使用 / 超时次数

# 工具
- CloudWatch（AWS）
- Azure Application Insights
- 阿里云日志服务 / 监控
```

### 6.4 成本优化

```
Serverless 成本陷阱：
  - 调用次数多 → 费用高
  - 长时间运行 → 费用高
  - 跨服务调用多 → 费用爆炸

优化策略：
  - 合并小调用（批处理）
  - 设置超时（避免僵尸函数）
  - 用 Provisioned Concurrency 选按需 vs 预置
```

---

## 七、Serverless 适用与不适用

### 7.1 适用场景 ✅

| 场景 | 原因 |
|------|------|
| **API 后端** | 按调用计费 / 自动扩缩 |
| **数据处理** | 事件触发 / 短任务 |
| **Webhook** | 异步处理 |
| **图像处理** | 按需处理 |
| **定时任务** | cron 替代 |
| **聊天机器人** | 突发流量 |

### 7.2 不适用场景 ❌

| 场景 | 原因 |
|------|------|
| **长任务（> 15 分钟）** | Lambda 超时限制 |
| **大内存（> 10 GB）** | Lambda 内存限制 |
| **低延迟要求（< 10ms）** | 冷启动延迟 |
| **强 GPU 需求** | Lambda 不支持 GPU |
| **稳定高负载** | K8s 更便宜 |

---

## 八、Serverless 架构模式

### 模式 1：API Backend

```
用户 → API Gateway → Lambda → DynamoDB
```

### 模式 2：事件流处理

```
S3 上传 → Lambda 触发 → Rekognition（图像识别）→ DynamoDB
```

### 模式 3：定时任务

```
EventBridge（cron）→ Lambda → 清理数据
```

### 模式 4：Chatbot

```
用户 → API Gateway → Lambda → 调用 LLM API → 返回
```

### 模式 5：WebSocket

```
WebSocket 连接 → Lambda（长连接）→ 实时通信
```

---

## 九、最佳实践

1. **冷启动预算**：P95 冷启动 < 500ms
2. **幂等性必备**：防重试导致重复执行
3. **观测三件套**：指标 / 日志 / 链路追踪
4. **函数粒度**：不要过大（< 200 行）
5. **依赖管理**：用 Lambda Layers 共享依赖
6. **超时设置**：必设（避免僵尸函数）
7. **VPC 优化**：VPC 内 Lambda 冷启动慢（考虑不放 VPC）
8. **Serverless 不适合所有场景**：长任务 / 大内存用 K8s

---

← [返回架构演进史](../README.md) · 📅 2026-06-28