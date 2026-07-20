<!--
module:
  parent: system-design
  slug: system-design/microservices
  type: article
  category: 主模块子文章
  summary: 微服务架构（Microservices Architecture）是一种将大型应用程序拆分为一组**小型、独立服务**的设计方法，每个服务围绕特定业务能力构建，...
-->

# 微服务架构（Microservices）

> 微服务架构（Microservices Architecture）是一种将大型应用程序拆分为一组**小型、独立服务**的设计方法，每个服务围绕特定业务能力构建，通过轻量级机制（如 HTTP/REST、gRPC、消息队列）通信，支持独立部署、扩展和更新。

---
## 引言：架构困境

微服务的核心张力不是"拆还是不拆"——而是**服务粒度、事务边界、团队拓扑三者如何同向对齐**。粒度太粗退化为分布式单体；太细则调用链复杂、数据一致性难保证。本篇从康威定律出发，把"按业务能力切分 vs 按数据所有权切分"、"同步 RPC vs 异步事件"等核心 trade-off 讲清楚。

---

## 🎯 一句话定位

**微服务不是"小就是好"——它是"业务复杂度倒逼架构升级"的产物**。它用**服务边界**承载**业务边界**，用**独立部署**承载**团队自治**，用**治理体系**承载**复杂协作**。本章聚焦"微服务**设计**"——拆分策略、通信模式、数据一致性、服务契约、演进路径——而**工程实现**详见 02-07 各章节（分布式、高可用、高性能、安全、部署）。

---

## 🆕 微服务设计 5 大主题

微服务设计不只是"拆应用"，它需要回答 5 个核心问题：

| 主题 | 核心问题 | 子章节 |
|------|---------|:------:|
| **🧩 怎么拆** | 如何划定服务边界？粒度如何？ | [服务拆分策略](service-decomposition/README.md) |
| **📞 怎么通信** | 同步 vs 异步？API 怎么设计？ | [服务间通信](service-communication/README.md) |
| **📜 怎么定契约** | 接口如何规范化、版本化、测试？ | [服务契约](service-contract/README.md) |
| **💾 怎么管数据** | 跨服务数据一致性？Saga/CQRS/Event Sourcing？ | [数据一致性](data-consistency/README.md) |
| **🔄 怎么演进** | 单体如何迁移？团队如何组织？ | [演进与组织](migration-and-organization/README.md) |

---

## 📐 微服务核心特征（速览）

| 特征 | 含义 | 价值 |
|------|------|------|
| **单一职责** | 每个服务聚焦一个业务能力 | 避免"巨石应用" |
| **独立部署** | 服务可单独发布，无需协调 | 持续交付、降低变更风险 |
| **去中心化** | 数据/技术栈/治理各自自治 | 选型灵活、不被锁定 |
| **轻量通信** | API + 消息队列，弱耦合 | 故障隔离、可独立扩展 |
| **弹性容错** | 熔断、限流、降级 | 单服务故障不拖垮整体 |
| **可观测性** | Metrics / Logging / Tracing | 分布式问题可调试 |

---

## 📚 章节导航

| 章节 | 文件 | 核心问题 | 建议时长 |
|:----:|:-----|:---------|:--------:|
| **基础** | [本文档](#一核心特征速览) | 微服务是什么、为什么 | 15 min |
| **拆分** | [服务拆分策略](service-decomposition/README.md) | 怎么划定服务边界？粒度判断？ | 45 min |
| **通信** | [服务间通信](service-communication/README.md) | 同步 vs 异步？API 版本管理？ | 50 min |
| **契约** | [服务契约](service-contract/README.md) | OpenAPI/Protobuf/契约测试？ | 35 min |
| **数据** | [数据一致性](data-consistency/README.md) | Saga/CQRS/Event Sourcing 怎么选？ | 60 min |
| **演进** | [演进与组织](migration-and-organization/README.md) | 单体如何迁移？团队怎么组织？ | 45 min |
| **整合** | [微服务与 DDD](microservices-and-ddd/README.md) | 业务能力 → 限界上下文 → 服务 | 30 min |

### 推荐阅读顺序

```text
基础（本文档）
  ↓
微服务与 DDD（先建立业务视角）
  ↓
  ┌── 拆分策略（决定边界）
  │     ↓
  ├── 服务间通信（决定协作方式）
  │     ↓
  ├── 服务契约（决定接口规范）
  │     ↓
  └── 数据一致性（决定数据治理）
  ↓
演进与组织（落地实践：迁移 + 团队）
```

- **时间紧张**（30 分钟）：基础 + 拆分策略前 3 节 + 演进路径
- **架构师视角**：5 大主题全读 + 微服务与 DDD
- **后端工程师**：通信 + 契约 + 数据一致性

---

## ⚖️ 何时用 / 何时不用微服务

### ✅ 适合微服务的场景

| 信号 | 说明 |
|------|------|
| **业务复杂度高** | 多个独立业务域，变更频率差异大 |
| **团队规模 ≥ 50 人** | 单一代码库协调成本指数增长 |
| **独立扩展需求** | 部分功能流量大需独立扩缩容 |
| **快速迭代要求** | 每周/每日发布，单体无法支撑 |
| **多技术栈** | 不同业务适合不同语言/框架 |
| **容错要求高** | 关键服务故障不能拖垮整体 |

### ❌ 不适合微服务的场景

| 反模式信号 | 说明 |
|----------|------|
| **团队 < 10 人** | 微服务的运维/治理成本超过收益 |
| **业务早期/不确定** | 频繁重写边界，拆分沉没成本高 |
| **强事务一致性** | 跨服务事务多，分布式事务复杂度爆表 |
| **流量小且稳定** | 扩展需求弱，单体足够 |
| **组织文化不匹配** | 团队未按业务能力拆分，强行微服务 → 分布式单体 |

> 🎯 **黄金法则**：**微服务是"业务复杂度"和"团队规模"的函数**，不是技术的时尚追求。**先单体后微服务**（Monolith First）通常是更稳的路径。

---

## 🧭 微服务在系统设计中的位置

```text
战略层：TOGAF（企业架构） → 决定"做什么系统、由谁做、怎么治理"
        ↓
架构层：DDD（领域驱动设计）→ 决定"业务边界在哪、领域模型是什么"
        ↓
风格层：微服务架构         → 决定"如何用服务承载业务边界"
        ↓
工程层：分布式 / HA / HP / 安全 / 部署 → 决定"服务如何可靠运行"
```

> **微服务 = 业务边界 + 自治团队 + 独立部署 + 治理体系**。它是 DDD 限界上下文的**工程实现**，是 TOGAF 业务能力的**技术落地**。

---

## 🔗 与本目录其他主题的交叉引用

| 主题 | 在哪里 | 微服务设计中的角色 |
|------|-------|------------------|
| **DDD 限界上下文** | [../ddd/](../ddd/README.md) | 服务拆分的**业务依据** |
| **TOGAF 业务能力** | [../togaf/](../togaf/README.md) | 服务拆分的**组织依据** |
| **团队拓扑** | [../togaf/conway-and-team-topology.md](../togaf/conway-and-team-topology.md) | 服务团队的**组织模式** |
| **康威定律** | [../togaf/conway-and-team-topology.md](../togaf/conway-and-team-topology.md) | 组织 → 架构的**因果关系** |
| **分布式锁/ID** | [../../../02-distributed/](../../../02-distributed/) | 跨服务协调基础设施 |
| **分布式事务** | [../../../02-distributed/distributed-transaction/](../../../02-distributed/distributed-transaction/) | Saga / TCC 等模式基础 |
| **限流 / 熔断 / 重试** | [../../../03-high-availability/](../../../03-high-availability/) | 服务弹性工程实现 |
| **缓存 / 消息队列** | [../../../04-high-performance/](../../../04-high-performance/) | 通信模式 + 性能优化 |
| **API 安全** | [../../../05-security/](../../../05-security/) | 服务间认证、mTLS、JWT |
| **可观测性** | [../../../07-deployment/observability/](../../../07-deployment/observability/) | 分布式追踪、监控、日志 |

---

## 🛠️ 核心技术栈速查

| 类别 | 主流选择 |
|------|---------|
| **服务注册发现** | Eureka、Consul、Nacos、Kubernetes DNS |
| **API 网关** | Spring Cloud Gateway、Kong、APISIX、Envoy、Traefik |
| **配置中心** | Spring Cloud Config、Apollo、Nacos |
| **服务通信（同步）** | REST（OpenAPI）、gRPC（Protobuf）、GraphQL |
| **服务通信（异步）** | Kafka、RabbitMQ、RocketMQ、Pulsar |
| **服务网格** | Istio、Linkerd、Consul Connect |
| **可观测性** | Prometheus + Grafana、ELK、Loki、Jaeger、SkyWalking、OpenTelemetry |
| **容器化/编排** | Docker、Kubernetes、Helm |
| **CI/CD** | GitLab CI、GitHub Actions、Argo CD、Spinnaker |

---

## 🤔 全章思考

1. **你的项目真的需要微服务吗**：用"何时用/不用"清单自评，10 人以下团队先考虑单体。
2. **你的服务边界清晰吗**：尝试画出服务依赖图，强耦合的服务应该合并。
3. **你的数据一致性如何保障**：跨服务调用是同步还是异步？有没有 Saga 补偿？
4. **你的团队与微服务对齐了吗**：3-5 人/团队、独立部署、长期稳定——满足几个？

---

## 相关章节

- [微服务与 DDD](microservices-and-ddd/README.md) — 业务能力 → 限界上下文 → 服务
- [服务拆分策略](service-decomposition/README.md) — 怎么拆？
- [服务间通信](service-communication/README.md) — 怎么通信？
- [服务契约](service-contract/README.md) — 怎么定契约？
- [数据一致性](data-consistency/README.md) — 怎么管数据？
- [演进与组织](migration-and-organization/README.md) — 怎么演进？

## 章节索引

- [架构认知的演进](../architecture-evolution/README.md) — OOD → DDD → 微服务的认知升级
- [领域驱动设计 DDD](../ddd/README.md) — 微服务边界的业务依据
- [企业架构 TOGAF 10](../togaf/README.md) — 业务能力地图、康威定律
- [分布式系统](../../../02-distributed/README.md) — 跨服务协调基础
- [高可用设计](../../../03-high-availability/README.md) — 熔断/限流/重试
- [高性能设计](../../../04-high-performance/README.md) — 缓存/消息队列
- [安全设计](../../../05-security/README.md) — 服务间认证
- [部署与运维](../../../07-deployment/README.md) — 可观测性、容量规划

---

## 🆚 微服务 vs 单体（Monolith）核心优势对比

> **一句话答案**：微服务的核心优势不是"技术先进"，而是**用服务边界承载业务边界、用独立部署承载团队自治**——这 6 大优势都在回答"为什么必须拆"。

### 6 大核心优势逐个剖析

#### 优势 1：独立部署（Independent Deploy）

**单体痛点**：100 工程师共用 1 个代码库，部署 1 小时（重启整个应用），1 个 bug 让全站挂。

**微服务做法**：每个服务单独发布，无需协调其他服务。

| 维度 | 单体 | 微服务 |
|------|------|--------|
| 部署频率 | 每周 1-2 次 | 每天 10-100 次 |
| 部署时长 | 1 小时（含全量回归）| 5-10 分钟（服务级）|
| 回滚影响 | 全站回滚 | 单服务回滚 |
| 故障影响半径 | 全站 | 单服务（其他服务照常）|

**反直觉**：独立部署的关键不是"快"，是"减少协调成本"——单体即使 CI/CD 优化到 5 分钟，只要 100 人共用一个仓就永远卡在代码冲突上。

#### 优势 2：独立伸缩（Independent Scaling）

**单体痛点**：用户量 100 倍增长，只能整体扩容——但热点功能只占 10% 代码，整容浪费 90%。

**微服务做法**：热点服务（如订单）单独扩 10 倍，其他服务保持 1 实例。

```text
典型场景：
- 订单服务：100 实例（流量最大）
- 用户服务：10 实例
- 评论服务：5 实例
- 后台管理：1 实例（凌晨定时任务）
```

**反直觉**：微服务不一定省钱（运维成本高），**但单位 GPU 利用率显著提升**。字节 / 美团 / 阿里的"中台化"本质是服务粒度独立伸缩。

#### 优势 3：技术异构（Polyglot）

**单体痛点**：Java 应用，所有功能只能用 Java；想用 Go 写高并发服务？不行。

**微服务做法**：每个服务选最合适的语言/数据库。

- 订单服务：Java（业务复杂） + MySQL
- 推荐服务：Python（ML 模型） + ClickHouse
- 实时通讯：Go（高并发） + Redis Streams
- 前端 BFF：Node.js（前端友好）

**反直觉**：技术异构是**优点也是缺点**——优点是选型灵活，缺点是**团队要维护多语言栈**（招聘 / 工具链 / 监控都要补）。

#### 优势 4：故障隔离（Failure Isolation）

**单体痛点**：用户服务 bug 导致 CPU 飙到 100%，**全站挂掉**（订单、支付、评论都不可用）。

**微服务做法**：用户服务挂了，其他服务独立工作（或降级）。

**生产案例**：
- Amazon 2018：服务故障隔离让"购物车挂掉" vs "首页还能开"
- Netflix Hystrix：服务熔断 + 降级 + Fallback

**反直觉**：微服务**不能消除故障**，但能把故障**爆炸半径**（blast radius）从"全站"降到"单服务"。

#### 优势 5：团队自治（Team Autonomy）

**单体痛点**：100 工程师在同一个仓库，**康威定律失败**——任何改动都要跨团队 review，节奏慢到每月 1 次发布。

**微服务做法**：Amazon "Two-Pizza Team" 原则——每个团队（10-15 人）独立负责一个服务的全生命周期（开发 / 部署 / 监控）。

| 团队 | 服务 | 业务 |
|------|------|------|
| 订单团队 | order-service | 下单 / 退款 |
| 库存团队 | inventory-service | 库存同步 |
| 推荐团队 | recommender-service | 个性化推荐 |

**反直觉**：团队自治的**副作用**是协作成本——服务间 API 约定 / 数据 schema 变更 / 故障协同——这是**分布式系统的本质复杂度**，不能消除。

#### 优势 6：可演进性（Evolution Capability）

**单体痛点**：老系统没人敢动（改 1 行牵动 100 个调用方），越老越僵。

**微服务做法**：每个服务独立演进，老服务可逐步废弃。

**生产案例**：Uber 从单体到微服务后，每年淘汰 5-10 个服务（替换为更现代的实现）。

**反直觉**：可演进性的关键是**契约稳定**（API 不变）和**灰度发布**（新旧共存）。

---

### 何时该用微服务？（决策矩阵）

| 决策项 | 单体更优 | 微服务更优 |
|--------|---------|-----------|
| **团队规模** | ≤ 20 人 | ≥ 50 人 |
| **业务复杂度** | 单一业务线 | 多业务线 / 多领域 |
| **用户量** | < 100 万 DAU | ≥ 1000 万 DAU |
| **代码量** | < 50 万行 | > 100 万行 |
| **伸缩需求** | 整体扩容够用 | 热点功能需独立扩 |
| **故障容忍** | 故障一次全挂可接受 | 部分故障必须不影响核心 |
| **技术异构需求** | 单一技术栈 | 多语言协同 |

### 反模式 · 6 个常见错

#### ⚠️ 反模式 1：不分场景直接拆

- 错：业务简单 / 用户量小（< 100 万 DAU）也拆
- 对：**先单体，后微服务**（Martin Fowler "Monolith First"）

#### ⚠️ 反模式 2：拆分粒度过细（100+ 服务）

- 错：一个 Spring Boot 应用拆成 100 个服务
- 对：按业务能力拆（5-20 个），每个服务有完整业务语义

#### ⚠️ 反模式 3：缺少自动化基础设施

- 错：拆完手动部署 100 个服务
- 对：必须先建**CI/CD + 服务网格 + 监控告警 + 链路追踪**

#### ⚠️ 反模式 4：跨服务 JOIN / 事务

- 错：跨服务 select 多个数据库做 join
- 对：服务自治 + Saga / Event Sourcing（详见 [data-consistency](data-consistency/README.md)）

#### ⚠️ 反模式 5：忽视分布式事务的复杂度

- 错：以为拆完就好了
- 对：先评估团队对分布式问题（CAP / 最终一致性 / Saga）的驾驭能力

#### ⚠️ 反模式 6：盲信"stay on monolith"

- 错：所有项目都"stay on monolith"
- 对：参考 Jackson / Shopify 经验但**业务驱动**——淘宝 2008 拆、字节中台化都因为业务倒逼

---

### Java 后端特定视角（Spring Boot 单机 vs Spring Cloud 微服务）

| 维度 | Spring Boot 单机 | Spring Cloud 微服务 |
|------|------------------|---------------------|
| 启动 | 1 个 jar 命令 | 需要 Nacos/Eureka 注册中心 + Gateway 网关 + 配置中心 |
| 部署 | 单 JVM | K8s 多 Pod + 服务网格 |
| 配置 | application.yml | Nacos/Apollo 配置中心（动态推送）|
| 服务发现 | 写死 URL | @EnableDiscoveryClient + 负载均衡 |
| 调用 | @Autowired 直接注入 | OpenFeign / RestTemplate + 熔断（Sentinel/Hystrix）|
| 分布式追踪 | 无 | SkyWalking / Zipkin |
| 监控 | Spring Actuator | Prometheus + Grafana + 链路追踪 |

**面试话术**：Spring Boot 是"小而美"的微服务基础，但**真正的微服务架构需要 Spring Cloud Alibaba 全套**（Nacos + Sentinel + Seata + SkyWalking）。

---

### 12.story 联动 & 面试精选

- **12.story 联动**：[07-from-chef-to-ceo](../../../../12.story/07-from-chef-to-ceo.md) —— 阿明餐厅从单店到连锁的"微服务架构转型"
- **面试题**：[13.split-hairs/04.system-design/microservices-vs-monolith](../../../../13.split-hairs/04.system-design/microservices-vs-monolith/README.md) —— 5-7 道精选题

---

← [返回系统设计基础](../README.md)
