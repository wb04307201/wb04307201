<!--
module:
  parent: system-design
  slug: system-design/02-evolution
  type: article
  category: 主模块子文章
  summary: 一份按时间梳理的架构演进速查手册：从单体到云原生到 AI 原生的完整演进。
-->

# 架构演进史：30 年互联网架构的演进全景

> 一份按时间梳理的架构演进速查手册：从单体到云原生到 AI 原生的完整演进。

---
## 引言：架构演进史：30 年互联网架构的演进全景 的关键决策

本篇是「架构演进史：30 年互联网架构的演进全景」的核心章节，聚焦该主题在实际落地时**5 个 trade-off 的取舍与决策轴**：单机 vs 垂直扩展 vs 水平扩展、SOA vs 微服务、关系型 vs NoSQL、传统部署 vs 容器化、自建数据中心 vs 公有云。

本篇用'决策困境'切入，比较几种主流路径并讲清取舍。

---

## 一、30 年架构演进全景

```text
1990s        2000s           2010s              2020s
  │            │               │                 │
单层(L1)    L2/L3      SOA → 微服务      云原生 / Serverless
  │            │               │                 │
单机 PC      客户端-      服务拆分          K8s + 容器
             服务器      + ESB             + 服务网格
              │            │                 │
              │         LAMP/J2EE         Spring Cloud
              │            │                 │
              │         Dubbo/Spring      Service Mesh
              │         Cloud              (Istio)
              │            │                 │
              │         Docker             AI 原生
              │         (2013)             (LLM Agent)
              ↓            ↓                 ↓
```

---

## 二、阶段 1：单体架构（1990s）

### 2.1 特征

- 所有功能在一个应用（WAR / EAR）
- 一个数据库（MySQL / Oracle）
- 一台服务器（Tomcat / WebLogic）
- 部署 = 整个应用重启

### 2.2 痛点

- ❌ 任何改动都要重新部署整个应用
- ❌ 一个 bug 导致整个应用挂掉
- ❌ 团队规模受限（5-10 人协作极限）
- ❌ 技术栈单一（不能 Python + Java 混用）

---

## 三、阶段 2：分层架构（2000s 初）

### 3.1 经典 3 层架构

```text
┌────────────────┐
│   表现层         │  JSP / Struts / Spring MVC
├────────────────┤
│   业务逻辑层      │  Service / EJB
├────────────────┤
│   数据访问层      │  DAO / Hibernate / MyBatis
└────────────────┘
```

### 3.2 经典技术栈

| 时期 | 主流技术栈 |
|------|----------|
| 2000-2005 | JSP + Servlet + MySQL |
| 2005-2010 | Struts / Spring / Hibernate |
| 2010-2015 | Spring MVC + MyBatis + Dubbo |

### 3.3 痛点（仍然存在）

- ❌ 单体应用 + 单数据库
- ❌ 扩展只能"垂直扩展"（加机器配置）
- ❌ 团队规模受限

---

## 四、阶段 3：分布式架构（2010s）

### 4.1 SOA（面向服务架构）

```text
ESB（企业服务总线）作为服务间通信的"中介"
   ↓
每个服务通过 ESB 通信
   ↓
解决了"系统间集成"问题
```

**问题**：ESB 本身成了瓶颈 + 单点故障。

### 4.2 微服务（Microservices）

```text
不用 ESB，每个服务独立：
  - 独立部署
  - 独立数据库
  - 独立技术栈
  - 独立团队（10 人以下）
```

**代表作**：Netflix（2010s 全面微服务化）

### 4.3 微服务技术栈

| 类别 | 主流框架 |
|------|---------|
| **服务治理** | Spring Cloud / Dubbo / gRPC |
| **服务发现** | Eureka / Consul / Nacos |
| **配置中心** | Apollo / Nacos / Spring Cloud Config |
| **熔断限流** | Hystrix / Sentinel / Resilience4j |
| **API 网关** | Zuul / Spring Cloud Gateway / Kong |

### 4.4 微服务痛点

- ❌ 服务数量爆炸（几十 / 几百个）
- ❌ 分布式事务复杂
- ❌ 链路追踪困难
- ❌ 运维成本高（每个服务都要部署 / 监控）

---

## 五、阶段 4：云原生（2015-2020）

### 5.1 三大核心技术

```text
容器化（Docker）→ 编排（K8s）→ 服务网格（Istio）
   ↓                  ↓                ↓
统一打包          自动扩缩          通信治理
```

### 5.2 CNCF 云原生全景

| 层次 | 项目 |
|------|------|
| **容器** | containerd / Docker |
| **编排** | Kubernetes |
| **服务网格** | Istio / Linkerd / Cilium |
| **监控** | Prometheus / Grafana / Loki / Tempo |
| **存储** | Rook / TiKV / MinIO |
| **数据库** | Vitess / TiDB / CockroachDB |
| **CI/CD** | ArgoCD / Tekton / Flux |
| **运行时** | gVisor / Kata Containers |

### 5.3 云原生的 4 大优势

- ✅ **弹性**：自动扩缩（秒级）
- ✅ **可观测**：metrics / logs / traces 标准化
- ✅ **声明式**：K8s YAML = 基础设施即代码
- ✅ **可移植**：任何云 / 任何环境

---

## 六、阶段 5：Serverless + 边缘（2020s）

### 6.1 Serverless 演进

| 时代 | 形态 | 启动时间 |
|------|------|---------|
| **传统** | VM | 分钟 |
| **容器** | Docker | 秒 |
| **K8s** | Pod | 秒 |
| **Serverless** | 函数 | **毫秒** |

### 6.2 4 大 Serverless 形态

| 形态 | 平台 | 特点 |
|------|------|------|
| **FaaS** | AWS Lambda / Azure Functions | 事件触发 |
| **BaaS** | DynamoDB / Firebase | 托管后端 |
| **Serverless K8s** | Knative / KEDA | K8s + 自动扩缩 |
| **边缘计算** | Cloudflare Workers / Fastly | 边缘节点 |

---

## 七、阶段 6：AI 原生（2024-2026）

### 7.1 4 大 AI 原生架构

| 架构 | 描述 |
|------|------|
| **AI Agent** | LLM + 工具 + 记忆 + 规划 |
| **RAG 系统** | LLM + 向量数据库 + 文档 |
| **Fine-tuning** | LLM + 行业数据 |
| **Multi-Modal** | LLM + 图像 / 视频 / 音频 |

### 7.2 AI 原生 vs 传统应用

| 维度 | 传统应用 | AI 原生 |
|------|---------|---------|
| **逻辑** | 代码（确定性）| LLM（概率性）|
| **输入** | 结构化 | 自然语言 / 多模态 |
| **输出** | JSON / 文本 | 自然语言 / 工具调用 |
| **成本** | CPU / 内存 | Token（按调用）|
| **测试** | 单元 / 集成 | 黄金集 + LLM-as-Judge |
| **部署** | Docker 镜像 | LLM API + 提示词 |

详见 [`11.ai/08-llmops`](../../../11.ai/08-llmops/README.md)

---

## 八、30 年架构演进时间线

| 年份 | 阶段 | 关键事件 |
|------|------|---------|
| 1990s | 单体 | LAMP / 客户端-服务器 |
| 2000-2005 | LAMP 成熟 | Struts / Spring / Hibernate |
| 2005-2010 | SOA 兴起 | ESB / WebLogic |
| 2010-2015 | 微服务爆发 | Spring Cloud / Dubbo / Netflix OSS |
| 2013 | Docker | 容器时代开启 |
| 2014 | K8s 发布 | 编排时代开启 |
| 2015 | CNCF 成立 | 云原生标准化 |
| 2017 | Istio 1.0 | Service Mesh 主流 |
| 2018 | K8s 1.10 | 生产可用 |
| 2020 | 疫情加速数字化 | 云原生全面落地 |
| 2021 | 微服务成熟 | Dapr / OpenTelemetry 兴起 |
| 2023 | ChatGPT 引爆 | AI 原生应用元年 |
| 2024 | AI Agent 崛起 | MCP / A2A 协议 |
| 2025 | LLM 推理优化 | vLLM / Sidecarless Mesh |
| 2026 | GPU 池化 | 平台工程成熟 |

---

## 九、架构演进的 4 大驱动力

1. **业务规模**：用户从 100 → 100万 → 1亿 → 10亿
2. **团队规模**：从 5 人 → 50 人 → 500 人 → 5000 人
3. **技术演进**：硬件 / 网络 / 框架的进步
4. **用户期望**：从功能 → 性能 → 体验 → 智能

---

## 十、给架构师的 4 大启示

1. **没有银弹**：每个阶段都有适合的场景（不要追新）
2. **演进式架构**：不要"一次性重写"（绞杀者模式）
3. **关注本质**：可扩展性 / 可维护性 / 可观测性是永恒主题
4. **业务驱动**：技术服务于业务（不是炫技）

---

## 专题导航

- [单体到微服务](01-monolith-to-microservices/README.md) — 单体拆分策略、迁移步骤与常见陷阱
- [Serverless 架构](02-serverless-architecture/README.md) — FaaS / BaaS / Knative 全场景实践

---

← [返回基础篇](../README.md) · 📅 2026-06-28

---

## 深度扩展

🆕 **微服务 vs 单体核心优势对比**：[system-design-basics/microservices/ 专题](../system-design-basics/microservices/README.md) —— 6 大核心优势（独立部署 / 独立伸缩 / 技术异构 / 故障隔离 / 团队自治 / 可演进）+ 6 大反模式 + Java Spring Cloud 7 维对比 + 何时该拆 7 维决策。面试精选 7 道 Q&A 见 [13.split-hairs/04.system-design/microservices-vs-monolith](../../../13.split-hairs/04.system-design/microservices-vs-monolith/README.md)。