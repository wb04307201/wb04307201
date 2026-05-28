# 术语表

> 「阿明餐厅」系列涉及的 60+ 核心技术术语速查。按主题分类，每条包含：术语名称、一句话解释、出处文章。

← [返回系列导读](./index.md)

---

## 架构 & 存储

| 术语 | 解释 | 出处 |
|------|------|------|
| **Cache Aside** | 先更新数据库，再删除缓存。适合读多写少的缓存更新策略 | [前传](./02-system-architecture-evolution.md) |
| **Write Through** | 写入时同时更新缓存和数据库，保证强一致性 | [前传](./02-system-architecture-evolution.md) |
| **最终一致性 (Eventual Consistency)** | 数据在极短时间窗口内可能不一致，但最终会达成一致 | [前传](./02-system-architecture-evolution.md) |
| **读写分离** | 主库负责写操作，从库负责读操作，通过同步机制保持一致 | [前传](./02-system-architecture-evolution.md) |
| **垂直拆分** | 按业务线将系统拆分为独立的子系统，各自独立运营 | [前传](./02-system-architecture-evolution.md) |
| **水平分片 (Sharding)** | 按区域或时间将同一张表的数据拆分到多个库/表中 | [前传](./02-system-architecture-evolution.md) |
| **Saga** | 分布式事务方案：每步操作都有补偿操作，失败时逆向回滚 | [前传](./02-system-architecture-evolution.md) |
| **TCC (Try-Confirm-Cancel)** | 分布式事务方案：预留资源 → 确认 → 取消，业务侵入性强 | [前传](./02-system-architecture-evolution.md) |
| **多活容灾** | 多个数据中心同时对外提供服务，单点故障不影响整体 | [前传](./02-system-architecture-evolution.md) |
| **云原生 (Cloud Native)** | 容器化 + K8s 编排 + 服务网格 + DevOps 的架构范式 | [前传](./02-system-architecture-evolution.md) |

---

## 流量治理

| 术语 | 解释 | 出处 |
|------|------|------|
| **令牌桶 (Token Bucket)** | 限流算法：匀速生成令牌，请求拿到令牌才能处理，允许一定突发 | [正传 1](./04-peak-traffic-defense.md) |
| **漏桶 (Leaky Bucket)** | 限流算法：请求先进桶，匀速流出，实现绝对匀速 | [正传 1](./04-peak-traffic-defense.md) |
| **熔断器 (Circuit Breaker)** | 当错误率超阈值时自动切断调用，防止慢服务拖垮整个系统 | [正传 1](./04-peak-traffic-defense.md) |
| **降级 (Degradation)** | 资源不足时，主动放弃部分功能，保住核心业务 | [正传 1](./04-peak-traffic-defense.md) |
| **削峰填谷** | 用消息队列将瞬间流量高峰拉平成稳定的处理能力 | [正传 1](./04-peak-traffic-defense.md) |
| **弹性伸缩 (Auto Scaling)** | 根据监控指标动态增减资源实例，应对流量波动 | [正传 1](./04-peak-traffic-defense.md) |
| **全链路压测** | 模拟真实流量对整个系统链路进行压力测试，提前发现瓶颈 | [正传 1](./04-peak-traffic-defense.md) |

---

## 可观测性

| 术语 | 解释 | 出处 |
|------|------|------|
| **结构化日志 (Structured Logging)** | 用 JSON 等结构化格式记录日志，便于检索和分析 | [正传 2](./05-observability.md) |
| **P99 延迟** | 99% 的请求在该时间内完成，衡量系统尾部延迟的关键指标 | [正传 2](./05-observability.md) |
| **分布式追踪 (Distributed Tracing)** | 通过 Trace ID 串联一次请求在多个服务间的完整调用链 | [正传 2](./05-observability.md) |
| **SLI (Service Level Indicator)** | 服务级别指标：衡量服务行为的可量化度量 | [正传 2](./05-observability.md) |
| **SLO (Service Level Objective)** | 服务级别目标：基于 SLI 设定的目标区间（如可用性 ≥ 99.9%） | [正传 2](./05-observability.md) |
| **错误预算 (Error Budget)** | SLO 允许的不可用时间余额（如 99.9% = 全年 8.76 小时） | [正传 2](./05-observability.md) |

---

## 安全架构

| 术语 | 解释 | 出处 |
|------|------|------|
| **OAuth 2.0** | 第三方授权协议：给第三方有限权限的令牌，而非暴露密码 | [正传 3](./06-security-architecture.md) |
| **MFA (Multi-Factor Authentication)** | 多因素认证：密码 + 短信/指纹/硬件密钥，提高安全性 | [正传 3](./06-security-architecture.md) |
| **SSO (Single Sign-On)** | 单点登录：一次登录，访问所有关联系统 | [正传 3](./06-security-architecture.md) |
| **RBAC (Role-Based Access Control)** | 基于角色的权限控制：权限绑定在角色上，而非个人 | [正传 3](./06-security-architecture.md) |
| **ABAC (Attribute-Based Access Control)** | 基于属性的权限控制：根据用户/资源/环境属性动态计算权限 | [正传 3](./06-security-architecture.md) |
| **零信任 (Zero Trust)** | 永远不信任，始终验证。无论内网外网，每次访问都需认证 | [正传 3](./06-security-architecture.md) |
| **mTLS (Mutual TLS)** | 双向 TLS：服务端和客户端互相验证证书，用于服务间认证 | [正传 3](./06-security-architecture.md) |
| **KMS (Key Management Service)** | 密钥管理服务：管理加密密钥的生成、轮换、访问控制 | [正传 3](./06-security-architecture.md) |
| **数据脱敏 (Data Masking)** | 在不影响业务的前提下隐藏敏感信息（掩码/哈希/令牌化） | [正传 3](./06-security-architecture.md) |

---

## 测试策略

| 术语 | 解释 | 出处 |
|------|------|------|
| **测试金字塔 (Test Pyramid)** | 单元测试 70% + 集成测试 20% + E2E 测试 10% 的理想结构 | [正传 4](./08-qa-testing-strategy.md) |
| **TDD (Test-Driven Development)** | 测试驱动开发：Red（写失败测试）→ Green（最小实现）→ Refactor | [正传 4](./08-qa-testing-strategy.md) |
| **FIRST 原则** | 单元测试五原则：Fast / Isolated / Repeatable / Self-validating / Timely | [正传 4](./08-qa-testing-strategy.md) |
| **契约测试 (Contract Test)** | 消费方定义期望，提供方验证实现，保证接口兼容性 | [正传 4](./08-qa-testing-strategy.md) |
| **测试左移 (Shift Left)** | 把测试提前到需求/设计阶段，尽早发现问题 | [正传 4](./08-qa-testing-strategy.md) |
| **测试右移 (Shift Right)** | 在生产环境中持续测试（混沌工程、A/B 测试、监控） | [正传 4](./08-qa-testing-strategy.md) |

---

## CI/CD & DevOps

| 术语 | 解释 | 出处 |
|------|------|------|
| **CI (Continuous Integration)** | 持续集成：频繁合并代码到主分支，自动运行测试 | [正传 5](./09-cicd-devops.md) |
| **CD (Continuous Delivery)** | 持续交付：将部署过程自动化，随时可一键部署到生产 | [正传 5](./09-cicd-devops.md) |
| **灰度发布 (Gray Release)** | 新功能先对少数用户开放，验证无问题后再全量开放 | [正传 5](./09-cicd-devops.md) |
| **蓝绿部署 (Blue-Green)** | 新老版本同时运行，通过路由切换流量，实现秒级回滚 | [正传 5](./09-cicd-devops.md) |
| **金丝雀发布 (Canary)** | 新版本先对少量真实用户开放，用监控数据判断是否全量 | [正传 5](./09-cicd-devops.md) |
| **GitOps** | 基础设施配置存储在 Git 中，通过 Git 提交触发自动化部署 | [正传 5](./09-cicd-devops.md) |
| **Feature Toggle** | 特性开关：通过配置控制功能是否对用户可见，无需重新部署 | [正传 5](./09-cicd-devops.md) |

---

## API 设计

| 术语 | 解释 | 出处 |
|------|------|------|
| **RESTful** | 资源导向的 API 设计风格：URL 表示资源，HTTP 方法操作资源 | [正传 6](./10-api-design.md) |
| **GraphQL** | 客户端指定返回字段的查询语言，避免 Over/Under-fetching | [正传 6](./10-api-design.md) |
| **gRPC** | 基于 Protocol Buffers 的高性能 RPC 框架，适合微服务间通信 | [正传 6](./10-api-design.md) |
| **OpenAPI (Swagger)** | API 文档标准：用 YAML/JSON 描述 API，自动生成文档和客户端代码 | [正传 6](./10-api-design.md) |
| **幂等性 (Idempotency)** | 同一请求执行多次，结果和执行一次相同，防止重复提交 | [正传 6](./10-api-design.md) |
| **API 网关 (API Gateway)** | 统一入口：集中处理认证、限流、路由、协议转换等横切关注点 | [正传 6](./10-api-design.md) |

---

## AI Agent

| 术语 | 解释 | 出处 |
|------|------|------|
| **RAG (Retrieval-Augmented Generation)** | 检索增强生成：先从知识库检索相关信息，再交给 LLM 生成回答 | [续集](./01-ai-agent-architecture.md) |
| **ReAct** | 推理策略：思考-行动-观察循环，边做边查 | [续集](./01-ai-agent-architecture.md) |
| **ToT (Tree of Thought)** | 树状思维：探索多条推理路径，评估后择优 | [续集](./01-ai-agent-architecture.md) |
| **GoT (Graph of Thought)** | 图状思维：推理节点可合并/回溯，减少重复计算 | [续集](./01-ai-agent-architecture.md) |
| **Function Calling** | 智能体通过标准化接口（JSON Schema）调用外部工具 | [续集](./01-ai-agent-architecture.md) |
| **Multi-Agent** | 多智能体协同：多个 Agent 分工协作，类似团队组织设计 | [续集](./01-ai-agent-architecture.md) |
| **RLHF / DPO** | 基于人类反馈的强化学习 / 直接偏好优化，用反馈数据优化模型 | [续集](./01-ai-agent-architecture.md) |
| **Prompt 注入** | 通过构造恶意输入绕过智能体安全规则的 attack 手法 | [续集](./01-ai-agent-architecture.md) |

---

## 团队管理 & 重构

| 术语 | 解释 | 出处 |
|------|------|------|
| **康威定律 (Conway's Law)** | 系统架构反映组织沟通结构。组织怎么拆，系统就怎么拆 | [终章](./07-from-chef-to-ceo.md) |
| **技术雷达 (Technology Radar)** | ThoughtWorks 提出的技术选型工具：评估/试验/采用/暂缓四象限 | [终章](./07-from-chef-to-ceo.md) |
| **IDP (Internal Developer Platform)** | 内部开发者平台：将通用能力（CI/CD、监控、部署）沉淀为共享基础设施 | [终章](./07-from-chef-to-ceo.md) |
| **技术债 (Technical Debt)** | 为赶进度而做的技术妥协，像借债一样需要"还本付息" | [番外](./03-refactoring-guide-for-pm.md) |
| **绞杀者模式 (Strangler Fig Pattern)** | 渐进式重构策略：新功能用新系统实现，逐步替换旧系统 | [番外](./03-refactoring-guide-for-pm.md) |
| **分支抽象 (Branch by Abstraction)** | 通过抽象层隔离新旧实现，在不影响线上的前提下逐步迁移 | [番外](./03-refactoring-guide-for-pm.md) |

---

← [返回系列导读](./index.md)
