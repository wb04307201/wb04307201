# 微服务架构（Microservices）

> 微服务架构（Microservices Architecture）是一种将大型应用程序拆分为一组**小型、独立服务**的设计方法，每个服务围绕特定业务能力构建，通过轻量级机制（如 HTTP/REST、gRPC、消息队列）通信，支持独立部署、扩展和更新。

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

```
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

```
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
