# 一、[Java](01.java/README.md)

> 从语言基础到 JVM 原理、并发编程、版本演进，系统性构建 Java 知识体系。

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [核心概念](01.java/concepts/) | 基本语法、面向对象、类型系统、反射、序列化、SPI 等 |
| 2 | [集合框架](01.java/collection/) | ArrayList、LinkedList、HashMap、ConcurrentHashMap 等源码剖析 |
| 3 | [I/O](01.java/io/) | I/O 流分类、NIO、零拷贝 |
| 4 | [JVM](01.java/jvm/) | 类加载、内存模型、GC、JVM 参数与调优 |
| 5 | [并发编程](01.java/concurrency/) | 线程基础、synchronized、volatile、JMM、JUC、ThreadLocal、CompletableFuture |
| 6 | [设计模式](01.java/design-patterns/) | GoF 23 种设计模式的 Java 实现与选型指南 |
| 7 | [构建工具](01.java/build-tools/) | Maven vs Gradle 对比与实战 |
| 8 | [Java Agent](01.java/java-agent/) | 字节码增强、Instrumentation API、预加载与 Attach 模式 |
| 9 | [JDBC](01.java/jdbc/) | JDBC 架构、核心接口、连接池与最佳实践 |
| 10 | [Kotlin](01.java/kotlin/) | Kotlin 语法、与 Java 对比、协程基础 |
| 11 | [日志](01.java/logging/) | 日志级别、Logback、Log4j2、SLF4J 门面 |
| 12 | [模块系统](01.java/modules/) | JPMS（Java 9+）、模块化迁移指南 |
| 13 | [网络编程](01.java/network/) | Socket、TCP/UDP、HTTP 客户端 |
| 14 | [测试](01.java/testing/) | JUnit 5、Mockito、JaCoCo、测试最佳实践 |
| 15 | [版本特性](01.java/version/) | Java 8 ~ 26 各版本新特性 & 功能演进历史（GC/Lambda/Stream/并发/FFM 等） |

# 二、[计算机基础](02.computer-basics/README.md)

> 系统性整理计算机科学基础知识，涵盖网络、算法、Linux、系统运维、知识产权等核心领域。

## 目录导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [01-网络](02.computer-basics/01-network/README.md) | OSI/TCP/IP 模型、协议族、HTTP 演进、WCAG |
| 2 | [02-算法](02.computer-basics/02-algorithms/README.md) | 算法概述、时间/空间复杂度、取舍策略 |
| 3 | [03-Linux](02.computer-basics/03-linux/README.md) | 常用命令、curl 详解 |
| 4 | [04-运维](02.computer-basics/04-operations/README.md) | 服务器性能指标、云服务模式 |
| 5 | [05-知识产权](02.computer-basics/05-ipr/README.md) | 专利 vs 软件著作权 |

# 三、[数据库](03.database/README.md)

> 从关系型数据库基础出发，依次深入 SQL、事务、索引、MySQL 内部机制，再扩展到缓存、Redis、NoSQL、连接池、数据迁移、监控与云数据库。

## 知识体系

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [数据库基础知识](03.database/01-fundamentals/README.md) | 核心概念、ER 图、范式、设计步骤 |
| 2 | [SQL](03.database/02-sql/README.md) | SQL 语法、执行顺序、慢查询分析与优化 |
| 3 | [事务与并发控制](03.database/03-transaction/README.md) | ACID、隔离级别、锁机制、MVCC |
| 4 | [索引](03.database/04-index/README.md) | B+ 树、聚簇/非聚簇索引、覆盖索引、最左前缀、索引失效 |
| 5 | [MySQL](03.database/05-mysql/README.md) | 架构、存储引擎、InnoDB 内部机制、主从复制、日志系统 |
| 6 | [缓存](03.database/06-cache/README.md) | 缓存分类、穿透/击穿/雪崩、缓存与数据库一致性 |
| 7 | [Redis](03.database/07-redis/README.md) | 数据类型、持久化、集群高可用、内存管理 |
| 8 | [NoSQL 数据库](03.database/08-nosql/README.md) | NoSQL 分类、SQL vs NoSQL 对比、选型指南 |
| 9 | [数据库连接池](03.database/09-connection-pool/README.md) | HikariCP、Druid、参数配置、监控 |
| 10 | [数据迁移与同步](03.database/10-data-migration/README.md) | DataX 全量同步、Canal/Maxwell Binlog 订阅、Flink CDC |
| 11 | [数据库监控告警](03.database/11-monitoring/README.md) | Prometheus + Grafana + AlertManager、慢查询分析 |
| 12 | [云数据库](03.database/12-cloud-database/README.md) | AWS RDS/Aurora、阿里云 PolarDB、TiDB Cloud、自建 vs 云 |

> 开源参考: [基于 ConcurrentHashMap 的高性能缓存实现](https://gitee.com/wb04307201/CHMCache) — 基于 LRU 策略，支持自动过期、大小限制、后台清理。

# 四、[系统设计](04.system-design/README.md)

> 系统设计知识体系图谱，从基础理论（软件工程 / DDD / TOGAF）到工程实践（分布式 / 高可用 / 高性能 / 安全 / 幂等 / 部署）的完整学习路径。

## 篇章导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [01 基础](04.system-design/01-foundation/README.md) | 软件工程、OOD/DDD/TOGAF/ArchiMate/IT4IT、技术债 |
| 2 | [02 分布式](04.system-design/02-distributed/README.md) | CAP、共识算法、分布式事务、RPC |
| 3 | [03 高可用](04.system-design/03-high-availability/README.md) | 限流、熔断、重试、降级、冗余、混沌 |
| 4 | [04 高性能](04.system-design/04-high-performance/README.md) | 负载均衡、CDN、缓存、数据库优化、消息队列、连接池、序列化、Java 优化 |
| 5 | [05 安全](04.system-design/05-security/README.md) | JWT、OAuth2、API 安全、OWASP、加密、密钥管理 |
| 5a | [访问控制](04.system-design/05-security/access-control/README.md) | 6 大权限模型（DAC/MAC/RBAC/ABAC/ReBAC/混合）与选型决策 |
| 6 | [06 幂等设计](04.system-design/06-idempotency/README.md) | 幂等键、乐观锁、状态机、去重表、与分布式事务的关系 |
| 7 | [07 部署与运维](04.system-design/07-deployment/README.md) | 部署架构、可观测性、容量规划 |

> 开源参考：
> - [Flexible Lock · 灵锁](https://gitee.com/wb04307201/flexible-lock) — 基于 Spring Boot 的统一锁接口，支持 Redis 单点/集群/哨兵、Zookeeper、本地锁
> - [Rate Limiter · 限流器](https://gitee.com/wb04307201/rate-limiter) — 配套限流组件

# 五、[工具链](05.tools/README.md)

> 工欲善其事，必先利其器。覆盖版本控制（Git）、容器化（Docker/Podman）、反向代理（Nginx/Pingora）、Monorepo、Java 工具库与阿里微服务生态。

## 模块导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [01 Git](05.tools/git/command/README.md) | 命令清单、[Gitea](05.tools/git/gitea/README.md) 自建代码托管 |
| 2 | [02 Docker](05.tools/docker/command/README.md) | 命令速查、[Compose](05.tools/docker/docker-compose/README.md)、[镜像](05.tools/docker/images/README.md)、[Podman](05.tools/docker/podman/README.md) |
| 3 | [03 Nginx](05.tools/nginx/README.md) | 反向代理/负载均衡、[Pingora](05.tools/nginx/pingora/README.md) 新一代代理 |
| 4 | [04 Monorepo](05.tools/monorepo/README.md) | 单仓多项目管理、演进路径、工具选型 |
| 5 | [05 Java 工具库](05.tools/java/tool-library/README.md) | Hutool / Guava / Commons、[Lombok](05.tools/java/lombok/README.md) 注解提效 |
| 6 | [06 阿里微服务](05.tools/ali-microservices/README.md) | Nacos 服务发现与配置管理、阿里云原生微服务生态 |

# 六、[Spring](06.spring/README.md)

> 从 Spring 核心到 Spring Boot / Cloud / 集成组件 / 可观测性 / 注解速查，系统覆盖 Spring 全家桶。

## 章节导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [01 核心容器](06.spring/01-core/README.md) | IoC/AOP 原理、Bean 生命周期与循环依赖（三级缓存）、FactoryBean、依赖注入（构造器/Setter/字段）、@Configuration Lite/Full、外部化配置、Event 机制、模块依赖、手写 mini Spring |
| 2 | [02 Web 层](06.spring/02-web/README.md) | Spring MVC 流程、Filter/AOP 顺序、异常/视图/上传/CORS/i18n/异步、WebFlux 响应式（WebClient/R2DBC/Router Functions/测试）、SSE |
| 3 | [03 数据层](06.spring/03-data/README.md) | 声明式/编程式事务、多数据源/JTA、JPA 事务、传播/隔离/失效、Seata 分布式事务、Spring Cache 4 大模式 + 多级缓存 + 序列化、[**MyBatis 全栈**](06.spring/03-data/mybatis/README.md)（架构原理 / 扩展能力 / Spring 整合 / MyBatis-Plus 4 主题） |
| 4 | [04 Spring Boot](06.spring/04-spring-boot/README.md) | 自动配置原理、自定义 Condition 扩展、Starter 机制、spring.factories 迁移、启动流程、启动后钩子、外部化配置、内嵌服务器切换、GraalVM Native Image |
| 5 | [05 Spring Cloud](06.spring/05-spring-cloud/README.md) | 服务注册/配置中心（含加密）/负载均衡 RPC/熔断/网关（JWT 鉴权）/链路追踪/Stream/Bus/Seata 集成/版本对应 |
| 6 | [06 集成组件](06.spring/06-integration/README.md) | Validation（分组/跨字段/自定义）、Retry（Reactive）、StateMachine（持久化/并行）、Batch（重试/重启） |
| 7 | [07 可观测性](06.spring/07-observability/README.md) | Actuator 端点、健康探针、Micrometer（OTLP/LongTaskTimer）、Prometheus+Pushgateway、Grafana Alerting、ELK/Loki |
| 8 | [08 注解速查](06.spring/08-annotations/README.md) | 事务/缓存/调度/校验/重试/AOP/Web/JPA/测试/配置/异常 等按场景分类的索引 |

> 开源参考：
> - [Multi-Level Cache Spring Boot Starter](https://gitee.com/wb04307201/multi-level-cache-spring-boot-starter) — 通过 `CacheManager` 接口扩展多级缓存注解
> - [Method Trace Log](https://gitee.com/wb04307201/methodTraceLog) — 基于 Spring AOP + Micrometer 的方法调用追踪工具

# 七、[工作流](07.workflow/README.md)

> 工作流 = **BPMN 流程骨架（确定性、可审计）** + **事件驱动协作神经（异步、弹性）**。覆盖工作流概念定义、BPMN 流程引擎（Camunda 7/8/Zeebe）、微服务编排（编舞 vs 编排）、事件驱动编排（EventMesh / Serverless Workflow），并衔接 [11.ai BPMN+AI 融合](11.ai/04-architecture/bpmn-ai-integration.md) 4 模式（Camunda 8.5+ AI Agent Sub-process + Zeebe AI Worker）。

## 章节导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [工作流定义](07.workflow/define/README.md) | 业务/技术视角、BPMN 2.0 三要素（FlowObject / ConnectingObject / Artifact）、请假审批实例 + 3 企业案例 |
| 2 | [流程引擎](07.workflow/process-engine/README.md) | 4 阶段工作原理、5 里程碑、3 大引擎对比（Camunda/Flowable/Activiti）、5 维度选型决策树 + 2025-2026 趋势 |
| 2a | [Camunda 7 实战](07.workflow/process-engine/camunda/camunda-7/README.md) | SpringBoot 集成 + Swagger + bpmn-js + 5 任务节点对比 + 银行 50 万件/年案例 |
| 2b | [Camunda 8 / 云原生](07.workflow/process-engine/camunda/camunda-8/README.md) | Zeebe 内核 + 10K+/秒 + 8.5+ AI Agent Sub-process + fromAi() FEEL + 8.7/8.8 路线 |
| 2c | [Zeebe 引擎](07.workflow/process-engine/camunda/camunda-8/zeebe/README.md) | Client/Gateway/Broker/Exporter 4 大组件 + gRPC 实战 + K8s 部署 + 跨境电商 10K+/秒案例 |
| 3 | [工作流引擎与微服务编排](07.workflow/workflow-and-microservice-orchestration/README.md) | 编舞 vs 编排 + Zeebe/Conductor/Cadence 对比 + Netflix/Uber 案例 + Temporal 1.x 进展 |
| 4 | [事件驱动与 Serverless Workflow](07.workflow/apache-eventmesh/README.md) | 事件驱动作为「神经系统」+ CNCF Serverless Workflow 0.8/0.9/1.0 + EventMesh + 12306 1500 万张票/天案例 |

> 开源参考：暂无（流程引擎以商业产品 Camunda/Flowable/Activiti 为主，事件驱动生态以 Apache EventMesh / CNCF Serverless Workflow 为主）

# 八、[业务应用系统](08.application-systems/README.md)

> 一份按业务价值链梳理的业务系统速查手册，覆盖 21 个常见业务系统（MES · ERP · SCM · WMS · APS · SCADA · PLM · PDM · QMS · CRM · EAM · SRM · OMS · SCRM · OA · MOM · TMS · LIMS · CMS · BI · PMS），帮助业务/产品/需求人员快速建立完整的业务系统认知地图，并具备日常速查能力。

## 章节导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [业务价值链全景图](08.application-systems/README.md#-业务价值链全景图) | 研发创新 → 生产制造 → 供应链 → 销售服务 → 运营管理 → 专项支持 |
| 2 | [01 研发创新](08.application-systems/README.md#01-研发创新) | PLM · PDM · CMS |
| 3 | [02 生产制造](08.application-systems/README.md#02-生产制造) | MES · MOM · APS · SCADA |
| 4 | [03 供应链](08.application-systems/README.md#03-供应链) | SCM · SRM · WMS · TMS |
| 5 | [04 销售服务](08.application-systems/README.md#04-销售服务) | CRM · SCRM · OMS |
| 6 | [05 运营管理](08.application-systems/README.md#05-运营管理) | ERP · BI · EAM · OA · QMS |
| 7 | [06 专项支持](08.application-systems/README.md#06-专项支持) | LIMS · PMS |
| 8 | [系统集成模式](08.application-systems/README.md#-系统集成模式) | 跨系统集成架构与模式 |
| 9 | [系统速查表 + 学习路线](08.application-systems/README.md#-系统速查表) | 21 业务系统速查 + 入门/进阶/精通三段式学习路径 |

# 九、[前端工程](09.front-end/README.md)

> 现代前端工程的知识地图——从浏览器原理到 AI 协同开发，对齐 `04.system-design` / `06.spring` / `11.ai` 的 9 模块分层结构。

## 模块导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [01 基础](09.front-end/01-foundation/README.md) | 浏览器原理、HTML 语义化、CSS 工程化、Web 标准 |
| 2 | [02 语言](09.front-end/02-language/README.md) | JavaScript 核心机制、ES2024-2026 新特性、TypeScript 5 工程实践、Node/Deno/Bun 运行时 |
| 3 | [03 框架](09.front-end/03-frameworks/README.md) | 2026 框架格局、React/Vue/Svelte/元框架/选型 |
| 4 | [04 工程化](09.front-end/04-engineering/README.md) | 构建工具（Vite/Webpack/Turbopack）、包管理、Monorepo、测试、Lint |
| 5 | [05 架构](09.front-end/05-architecture/README.md) | 渲染模式（CSR/SSR/SSG/RSC）、状态、路由、微前端、Web Components、BFF |
| 6 | [06 性能](09.front-end/06-performance/README.md) | Core Web Vitals（LCP/INP/CLS）、Lighthouse、运行时性能与监控 |
| 7 | [07 安全](09.front-end/07-security/README.md) | XSS / CSRF / CSP / SRI / CORS / Sessions / 依赖供应链 |
| 8 | [08 跨端](09.front-end/08-cross-platform/README.md) | 移动（RN/Flutter）、桌面（Electron/Tauri）、小程序（微信/Taro）、PWA |
| 9 | [09 前端与 AI](09.front-end/09-frontend-and-ai/README.md) | AI SDK、AI Native UI、AI IDE（Cursor/Claude Code）、Vibe Coding、MCP 协议 |

> 开源参考：暂无（当前 9 模块中仅 03 框架、05 架构、07 安全有存量内容，其余模块为占位骨架，深度子文档待后续按需补充）

# 十、[大数据](10.big-data/README.md)

> 从数仓架构到 OLAP、数据湖、治理——大数据技术栈的完整地图。8 大主题涵盖离线/实时数仓、Hadoop 生态、实时计算、数据湖、OLAP、任务调度、数据治理与异构同步。

## 模块导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [01 数仓架构](10.big-data/01-data-warehouse/README.md) | Lambda / Kappa / 湖仓一体 / 批流融合 |
| 2 | [02 Hadoop 生态](10.big-data/02-hadoop-ecosystem/README.md) | HDFS / YARN / MapReduce / Hive / Presto / Trino |
| 3 | [03 实时计算](10.big-data/03-realtime-compute/README.md) | Flink / Spark Streaming / Storm |
| 4 | [04 数据湖](10.big-data/04-data-lake/README.md) | Apache Iceberg / Hudi / Delta Lake / 存算分离 |
| 5 | [05 OLAP](10.big-data/05-olap/README.md) | Apache Doris / StarRocks / ClickHouse / Trino |
| 6 | [06 调度](10.big-data/06-scheduling/README.md) | Apache Airflow / DolphinScheduler / Azkaban |
| 7 | [07 数据治理](10.big-data/07-data-governance/README.md) | Apache Atlas / DataHub / 数据血缘 / 数据质量 |
| 8 | [08 同步工具](10.big-data/08-sync-tools/README.md) | DataX / Apache SeaTunnel / Sqoop / Flume |

# 十一、[AI 知识体系](11.ai/README.md)
## 目录导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [L1 基础概念](11.ai/01-fundamentals/README.md) | 大语言模型基础、神经网络层次、嵌入 vs 向量化、稠密模型 vs MoE |
| 2 | [L2 技术栈](11.ai/02-technology-stack/README.md) | 61 核心概念全景、多模态、Prompt 工程、显存估算 |
| 3 | [L3 工程实践](11.ai/03-engineering/README.md) | 深度学习框架、应用开发框架、计算平台、本地部署、AI 平台对比 |
| 4 | [L4 架构设计](11.ai/04-architecture/README.md) | 智能系统分层架构、2026 技术趋势 |
| 5 | [L5 行业应用](11.ai/05-applications/README.md) | 汽车行业落地、具身智能 |
| 6 | [L6 前沿研究](11.ai/06-research/README.md) | 沉思模型（Rumination）等前沿探索 |
| 7 | [教学课程](11.ai/training/README.md) | Spring AI Agent 实战 16 课 |

# 十二、[「阿明餐厅」技术系列](12.story/README.md)

> 以餐厅经营为叙事主线，用 **43 篇** 故事讲透从架构演进到 AI 转型的技术全景。前传 + 续集一 + 正传 14 + 终章 + 番外 6 + 续集 2-17（AI 时代 16 篇）+ 番外 7-8 —— 一篇一个核心主题，篇篇独立又互相串联。
>
> **2026 v2 更新**：评测（34）、协议（35）、Token 经济学（36）三篇已拆分为 a/b 双篇（结构性优化）；新增可观测性、RAG、向量库、AI 合规、AI 私有化、Prompt 工程、多模态 7 个专题。

## 系列导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [系列导览](12.story/README.md) | 43 篇全景图 + 4 条主路径 + 13 类角色推荐 + 概念交叉索引 |
| 2 | [前传 · 架构演进](12.story/02-system-architecture-evolution.md) | 架构"长"出来（单机→云原生）+ IT 成熟度 L1-L7 评估 |
| 3 | [续集一 · AI Agent 架构](12.story/01-ai-agent-architecture.md) | 7 大模块：感知/记忆/规划/工具/协同/反馈/安全（衔接 [11.ai AI 知识体系](11.ai/README.md)）|
| 4 | [正传 1-14 · 核心工程（14 篇）](12.story/04-peak-traffic-defense.md) | 流量/可观测/安全/QA/CI-CD/API/数据/前端/故障/性能/异步/分布式/多端/数据库迁移 |
| 5 | [终章 · 从厨师到 CEO](12.story/07-from-chef-to-ceo.md) | 5 人→500 人：康威/团队拓扑/SECI/ADR/Docs-as-Code/IDP/工程师文化 |
| 6 | [番外 1-6 · 专题拓展（6 篇）](12.story/03-refactoring-guide-for-pm.md) | 重构/FinOps/SaaS/搜索推荐/低代码/国际化 |
| 7 | [续集 2-12 · AI 时代上半场（11 篇）](12.story/11-ai-learning-paradox.md) | 学习/组织/创业/自进化/信任/认知债/Harness/致命三件套 + [34a/34b 评测](12.story/34a-ai-evaluation-fundamentals.md) + [35a/35b 协议](12.story/35a-mcp-protocol.md) + [36a/36b Token](12.story/36a-ai-token-cost-structure.md) |
| 8 | [续集 13-17 · AI 时代下半场（5 篇）](12.story/37-ai-observability.md) | [37 可观测性](12.story/37-ai-observability.md) / [38 RAG](12.story/38-rag-retrieval-augmented-generation.md) / [39 向量库](12.story/39-vector-database-and-embedding.md) / [40 合规](12.story/40-ai-compliance-and-regulation.md) / [41 私有化](12.story/41-ai-private-deployment.md) |
| 9 | [番外 7-8 · 工程化专题（2 篇）](12.story/42-prompt-engineering.md) | [42 Prompt 工程](12.story/42-prompt-engineering.md) + [43 多模态](12.story/43-multimodal-ai.md) |
| 10 | [辅助资料 · 速查 + 术语](12.story/cheatsheet.md) | [一页纸速查](12.story/cheatsheet.md)（43 篇心法 + AI 选型 + Agent 工具链）；[术语表](12.story/glossary.md)（250+ 词条 / 40 主题）|

> 开源参考：12.story 章节本身为本仓库原创叙事，引用开源项目包括 Camunda 7/8、Apache EventMesh、CNCF Serverless Workflow、Dify/Coze/LangGraph、n8n、MCP/A2A、Qwen-VL、GPT-4o、Claude 3.5、LangSmith、vLLM、Qdrant、Milvus、Pinecone 等（详见各文末「延伸阅读」）。

# 十三、[咬文嚼字（高频面试题）](13.split-hairs/README.md)

> 主模块的"刺刀版" —— 专治面试中那些"好像懂但说不清"的高频 / 高难度问题。
> 每篇 50-300 行，聚焦单一问题，从原理到陷阱到最佳实践、面试话术一次讲透。
> 6 大分类共 **115 篇** 深度文章 + 121 篇 frontmatter 元数据（详见 [QUESTION-FORMAT-SPEC](./13.split-hairs/QUESTION-FORMAT-SPEC.md)），覆盖 Java / 数据库 / 系统设计 / Spring / AI / 前端。
> 写作规范：[QUESTION-FORMAT-SPEC.md](./13.split-hairs/QUESTION-FORMAT-SPEC.md) | 自动化校验：[scripts/validate.py](./13.split-hairs/scripts/validate.py)

## 分类导航

| 序号 | 主题 | 文章数 | 入口 |
|------|------|--------|------|
| 1 | Java 基础陷阱 | 32 | [01.java](13.split-hairs/01.java/README.md) |
| 2 | 数据库细节 | 22 | [03.database](13.split-hairs/03.database/README.md) |
| 3 | 系统设计难点 | 13 | [04.system-design](13.split-hairs/04.system-design/README.md) |
| 4 | Spring 面试高频 | 13 | [06.spring](13.split-hairs/06.spring/README.md) |
| 5 | AI 新概念 | 14 | [11.ai](13.split-hairs/11.ai/README.md) |
| 6 | 前端细节 | 25 | [09.front-end](13.split-hairs/09.front-end/README.md) |

---

## 01.java（31 篇）—— Java 基础陷阱

### 集合与数据结构

| 主题 | 核心问题 |
|------|---------|
| [ArrayList 去重](13.split-hairs/01.java/arrayList-distinct/README.md) | LinkedHashSet vs Stream |
| [HashSet 替代 LinkedList 查找](13.split-hairs/01.java/replace-linkedlist-with-hashset/README.md) | 什么时候该换数据结构？ |
| [HashMap 扩容](13.split-hairs/01.java/hashmap-resizing/README.md) | 1GB 的 HashMap 扩容会发生什么？ |
| [快速插入大量数据到 HashMap](13.split-hairs/01.java/large-data-into-hashmap/README.md) | 初始化容量 + 负载因子的权衡 |
| [快速给 Map 排序](13.split-hairs/01.java/sort-map/README.md) | TreeMap vs LinkedHashMap 选型 |

### 并发与线程

| 主题 | 核心问题 |
|------|---------|
| [ConcurrentHashMap 原理](13.split-hairs/01.java/concurrent-hashmap/README.md) | JDK 7 vs 8 实现差异 |
| [ThreadLocal 原理](13.split-hairs/01.java/threadlocal/README.md) | ThreadLocal 原理与内存泄漏 |
| [synchronized 锁升级](13.split-hairs/01.java/synchronized-lock-upgrade/README.md) | 偏向锁 → 轻量级 → 重量级 |
| [volatile 内存语义](13.split-hairs/01.java/volatile/README.md) | 可见性、有序性、原子性 |
| [AQS 框架原理](13.split-hairs/01.java/aqs/README.md) | AbstractQueuedSynchronizer 实现机制 |
| [线程池 7 大参数](13.split-hairs/01.java/thread-pool/README.md) | ThreadPoolExecutor 核心参数详解 |
| [Atomic 替代 synchronized](13.split-hairs/01.java/replace-synchronized-with-atomic/README.md) | CAS 无锁编程 |
| [CompletableFuture 编排](13.split-hairs/01.java/completable-future/README.md) | 异步任务编排 |

### JVM 与类加载

| 主题 | 核心问题 |
|------|---------|
| [JVM 内存区域](13.split-hairs/01.java/jvm-memory/README.md) | JVM 内存模型 + 对象创建流程 |
| [GC 算法与收集器](13.split-hairs/01.java/gc-algorithms/README.md) | GC 算法 + 垃圾收集器对比 |
| [类加载机制](13.split-hairs/01.java/class-loading/README.md) | 双亲委派模型 + 自定义类加载器 |
| [CPU 飙升排查](13.split-hairs/01.java/cpu-spike-troubleshooting/README.md) | 线上 CPU 100% 排查全流程 |
| [JVM 内存配置踩坑](13.split-hairs/01.java/jvm-memory-pitfall/README.md) | -Xmx 超过系统可用内存导致启动失败 |

### 语言基础

| 主题 | 核心问题 |
|------|---------|
| [== / equals / hashCode](13.split-hairs/01.java/equals-hashcode/README.md) | 相等性判断契约与陷阱 |
| [泛型擦除与 PECS](13.split-hairs/01.java/generics-erasure/README.md) | 类型擦除 + Producer Extends Consumer Super |
| [反射原理与性能](13.split-hairs/01.java/reflection/README.md) | Reflection API 使用与性能开销 |
| [String/Builder/Buffer](13.split-hairs/01.java/string-builder-buffer/README.md) | 字符串拼接选型指南 |
| [StringBuilder 重用](13.split-hairs/01.java/reuse-of-stringbuilder/README.md) | 循环中字符串拼接优化 |
| [final/finally/finalize](13.split-hairs/01.java/final-finally-finalize/README.md) | 三个关键字的区别与用法 |
| [SPI 机制](13.split-hairs/01.java/spi/README.md) | Service Provider Interface 扩展机制 |

### 对象与类型

| 主题 | 核心问题 |
|------|---------|
| [创建对象](13.split-hairs/01.java/create-object/README.md) | Java 创建对象的 5 种方式 |
| [基础类型封装为对象](13.split-hairs/01.java/object/README.md) | 为什么需要 Integer / Double 包装类？ |
| [Integer 缓存](13.split-hairs/01.java/integer-cache/README.md) | -128 到 127 的复用机制与陷阱 |
| [new String("123")](13.split-hairs/01.java/new-string/README.md) | 字符串常量池 vs 堆 |
| [Record 与泛型](13.split-hairs/01.java/record-t/README.md) | Java 14+ Record 可以用泛型吗？ |

### 设计模式与技巧

| 主题 | 核心问题 |
|------|---------|
| [单例模式](13.split-hairs/01.java/singleton-pattern/README.md) | 5 种实现方式 + 反射 / 序列化破坏 |
| [switch 前用 if 优化](13.split-hairs/01.java/if-before-switch/README.md) | 热点状态的快速路径优化 |

### 综合

| 主题 | 核心问题 |
|------|---------|
| [高频面试题合集](13.split-hairs/01.java/questions/README.md) | Java 综合高频问题速查 |

## 03.database（18 篇）—— 数据库细节

### MySQL 基础

| 主题 | 核心问题 |
|------|---------|
| [事务隔离机制](13.split-hairs/03.database/relational-database/mysql/isolation/README.md) | RU / RC / RR / Serializable |
| [INT(4) 的定义](13.split-hairs/03.database/relational-database/mysql/int(4)-define/README.md) | 显示宽度 vs 存储范围 |
| [快速加索引](13.split-hairs/03.database/relational-database/mysql/quickly-add-index/README.md) | 大表在线加索引 |
| [时间类型对比](13.split-hairs/03.database/relational-database/mysql/time-types/README.md) | DATETIME / TIMESTAMP / DATE |
| [COUNT(*) vs COUNT(1) vs COUNT(字段)](13.split-hairs/03.database/relational-database/mysql/count/README.md) | 性能差异与最佳实践 |
| [SQL 调优](13.split-hairs/03.database/relational-database/mysql/tuning/README.md) | Explain + 索引优化 |
| [加什么锁](13.split-hairs/03.database/relational-database/mysql/what-lock/README.md) | 行锁 / 表锁 / 间隙锁 |
| [索引失效的 10 种场景](13.split-hairs/03.database/mysql/index-failure/README.md) | LIKE 左通配 / 函数 / OR / 最左前缀 |

### MySQL 深入

| 主题 | 核心问题 |
|------|---------|
| [MVCC 实现原理](13.split-hairs/03.database/mvcc/README.md) | Read View + Undo Log |
| [B+ Tree 为什么适合数据库索引](13.split-hairs/03.database/bplus-tree/README.md) | vs B-Tree / Hash |
| [MySQL 主从复制延迟](13.split-hairs/03.database/replication-lag/README.md) | 延迟原因与解决方案 |
| [MySQL JOIN 算法](13.split-hairs/03.database/mysql-join/README.md) | NLJ / BNL / Hash Join |

### Redis 基础

| 主题 | 核心问题 |
|------|---------|
| [Redis 搜索](13.split-hairs/03.database/nosql/key-value/redis/search/README.md) | 全文搜索实现 |
| [缓存穿透 / 击穿 / 雪崩](13.split-hairs/03.database/redis/cache-penetration-breakdown-avalanche/README.md) | 面试必考三件套 |

### Redis 深入

| 主题 | 核心问题 |
|------|---------|
| [Redis 持久化](13.split-hairs/03.database/redis-persistence/README.md) | RDB / AOF / 混合持久化 |
| [Redis 内存淘汰策略](13.split-hairs/03.database/redis-eviction/README.md) | 8 种淘汰策略详解 |
| [Redis 集群](13.split-hairs/03.database/redis-cluster/README.md) | Sentinel vs Cluster |
| [Redis 大 Key 问题](13.split-hairs/03.database/redis-big-key/README.md) | 发现与治理方案 |

## 04.system-design（10 篇）—— 系统设计难点

### 高性能

| 主题 | 核心问题 |
|------|---------|
| [MQ 消息积压](13.split-hairs/04.system-design/high-performance/mq/mq-backlog/README.md) | 紧急止血 + 长期优化 |
| [为什么还要 RocketMQ](13.split-hairs/04.system-design/high-performance/mq/still-need-rocketmq/README.md) | Kafka vs RocketMQ vs RabbitMQ |
| [缓存与数据库一致性](13.split-hairs/04.system-design/high-performance/cache-consistency/README.md) | 延迟双删 vs Canal Binlog |
| [分布式锁](13.split-hairs/04.system-design/high-performance/distributed-lock/README.md) | Redis vs ZooKeeper |
| [限流算法](13.split-hairs/04.system-design/high-performance/rate-limiting/README.md) | 计数器 / 滑动窗口 / 漏桶 / 令牌桶 |

### 分布式

| 主题 | 核心问题 |
|------|---------|
| [分布式 ID](13.split-hairs/04.system-design/distributed/distributed-id/README.md) | UUID / DB / 雪花算法 / Leaf |
| [分布式事务](13.split-hairs/04.system-design/distributed/distributed-transaction/README.md) | 2PC / TCC / Saga / 本地消息表 |
| [CAP 定理实际应用](13.split-hairs/04.system-design/cap-theorem/README.md) | CP vs AP 选型决策 |

### 高并发

| 主题 | 核心问题 |
|------|---------|
| [幂等性设计 6 大方案](13.split-hairs/04.system-design/idempotency/README.md) | Token / 状态机 / 唯一索引 / 去重表 |
| [熔断降级实战](13.split-hairs/04.system-design/circuit-breaker/README.md) | Sentinel / Resilience4j 落地 |

## 06.spring（13 篇）—— Spring 面试高频

### 基础

| 主题 | 核心问题 |
|------|---------|
| [不推荐 @Autowired](13.split-hairs/06.spring/not-use-@autowired/README.md) | 字段注入 vs 构造器注入 |
| [PO / VO / DTO / BO / DAO / POJO](13.split-hairs/06.spring/clarify-various-o/README.md) | 数据对象辨析 |

### IoC 与 Bean

| 主题 | 核心问题 |
|------|---------|
| [Bean 生命周期](13.split-hairs/06.spring/bean-lifecycle/README.md) | 实例化 → 注入 → 初始化 → 销毁 12 步 |
| [@Bean vs @Component](13.split-hairs/06.spring/bean-vs-component/README.md) | 两种 Bean 注册方式的区别 |
| [Spring Boot 自动配置原理](13.split-hairs/06.spring/auto-configuration/README.md) | @EnableAutoConfiguration + 条件注解 |
| [循环依赖三级缓存](13.split-hairs/06.spring/circular-dependency/README.md) | DefaultSingletonBeanRegistry |

### AOP 与事务

| 主题 | 核心问题 |
|------|---------|
| [@Transactional 失效 8 种场景](13.split-hairs/06.spring/transactional-pitfalls/README.md) | 同类调用 / 异常类型 / 多线程 / 传播行为 |
| [@Transactional 传播行为](13.split-hairs/06.spring/transactional-propagation/README.md) | 7 种 propagation 详解 |
| [JDK 动态代理 vs CGLIB](13.split-hairs/06.spring/jdk-proxy-vs-cglib/README.md) | 两种代理机制的原理与选择 |
| [AOP 实现原理](13.split-hairs/06.spring/aop-principle/README.md) | 切面、通知、连接点、切入点 |
| [@Async 失效 4 种场景](13.split-hairs/06.spring/async-pitfalls/README.md) | 同类调用 / 非 @Bean / 线程池缺失 |

### Spring MVC

| 主题 | 核心问题 |
|------|---------|
| [Spring MVC 请求流程](13.split-hairs/06.spring/spring-mvc-flow/README.md) | DispatcherServlet 9 步流程 |

## 11.ai（7 篇）—— AI 新概念

| 主题 | 核心问题 |
|------|---------|
| [AI 思维：抛硬币](13.split-hairs/11.ai/ai-thinking/README.md) | 数学 vs AI 思维差异 |
| [Transformer 架构核心](13.split-hairs/11.ai/transformer/README.md) | Self-Attention + QKV + Multi-Head |
| [Token 与计费原理](13.split-hairs/11.ai/token/README.md) | BPE / WordPiece / 上下文窗口 / 计费 |
| [RAG 架构设计](13.split-hairs/11.ai/rag/README.md) | Chunking / Embedding / 向量数据库 |
| [Prompt Engineering 技巧](13.split-hairs/11.ai/prompt-engineering/README.md) | 8 种核心技术 + 注入防御 |
| [LLM 幻觉问题](13.split-hairs/11.ai/hallucination/README.md) | 幻觉成因 / 分类 / 检测与缓解 |
| [Function Calling / Tool Use](13.split-hairs/11.ai/function-calling/README.md) | 工具调用原理 / Schema 定义 / ReAct Agent |

## 09.front-end（19 篇）—— 前端细节

### HTTP / 网络

| 主题 | 核心问题 |
|------|---------|
| [GET vs POST](13.split-hairs/09.front-end/get-and-post/README.md) | 7 大差异 + 幂等性 |
| [HTTP 缓存机制](13.split-hairs/09.front-end/http-cache/README.md) | 强缓存 Cache-Control / 协商缓存 ETag |
| [CORS 跨域详解](13.split-hairs/09.front-end/cors/README.md) | 简单请求 / 预检请求 / 常见头部 |
| [HTTPS 握手过程](13.split-hairs/09.front-end/https-handshake/README.md) | TLS 1.2 vs 1.3 / 证书验证 |

### 浏览器机制

| 主题 | 核心问题 |
|------|---------|
| [消息机制](13.split-hairs/09.front-end/message/README.md) | 推送消息的方式 |
| [存储方案](13.split-hairs/09.front-end/storage/README.md) | Cookie / LocalStorage / IndexedDB |
| [事件循环 Event Loop](13.split-hairs/09.front-end/event-loop/README.md) | 宏任务 / 微任务 / async-await |
| [从 URL 输入到页面展示](13.split-hairs/09.front-end/from-url-to-page/README.md) | 网络 + 解析 + 渲染全链路 |

### JavaScript 核心

| 主题 | 核心问题 |
|------|---------|
| [闭包 Closure](13.split-hairs/09.front-end/closure/README.md) | 私有变量 / 内存泄漏 / React Hooks 陷阱 |
| [原型链与继承](13.split-hairs/09.front-end/prototype-chain/README.md) | __proto__ vs prototype / 继承方案 |
| [this 绑定规则](13.split-hairs/09.front-end/this-binding/README.md) | 默认 / 隐式 / 显式 / new / 箭头函数 |
| [防抖 + 节流手写](13.split-hairs/09.front-end/debounce-throttle/README.md) | debounce / throttle 实现与应用场景 |
| [Promise 手写实现](13.split-hairs/09.front-end/promise-handwriting/README.md) | Promise.all / race / allSettled |
| [深拷贝实现](13.split-hairs/09.front-end/deep-copy/README.md) | 递归 / 循环引用 / 特殊类型处理 |

### CSS

| 主题 | 核心问题 |
|------|---------|
| [BFC 块级格式化上下文](13.split-hairs/09.front-end/bfc/README.md) | 触发条件 / 应用场景 / 边距折叠 |

### 框架

| 主题 | 核心问题 |
|------|---------|
| [Virtual DOM + Diff 算法](13.split-hairs/09.front-end/virtual-dom-diff/README.md) | O(n) 复杂度 + Key 的作用 |
| [React Hooks 原理](13.split-hairs/09.front-end/react-hooks/README.md) | 闭包 + Hooks 链表 + 闭包陷阱 |
| [Vue 响应式原理](13.split-hairs/09.front-end/vue-reactivity/README.md) | Object.defineProperty vs Proxy |

### 安全

| 主题 | 核心问题 |
|------|---------|
| [XSS / CSRF 攻击防御](13.split-hairs/09.front-end/xss-csrf/README.md) | 反射型 / 存储型 / Token / SameSite Cookie |

---

# 十四、[项目管理与成本控制](14.project-management/README.md)

> **从老板 / PM / 技术总监的另一面** —— 不是技术细节，而是"花 50 万做 App 值不值？花 50 万买 AI 工具一年回本不？"这类决策实战。
>
> ⚠️ **2026-06-30 新建主模块**：原 `13.split-hairs/04.system-design/project-management/` 中 2 篇已迁回本主模块（`app-quote-breakdown` / `outsourcing-pitfalls`），`mobile-tech-stack` 计划迁至主模块 `09.front-end/08-cross-platform/`。

| 主题 | 核心问题 | 难度 |
|------|---------|------|
| [5 万 vs 50 万 App 报价差在哪](14.project-management/app-quote-breakdown/README.md) | 12 大成本维度拆解 + 决策矩阵 | ⭐⭐⭐ |
| [App 技术栈选型：原生 vs 跨端](09.front-end/08-cross-platform/mobile-tech-stack/README.md) | 原生 vs Flutter vs RN vs H5 vs 小程序 | ⭐⭐⭐ |
| [外包项目避坑指南](14.project-management/outsourcing-pitfalls/README.md) | 5 大隐性成本 + 合同 8 条必看 | ⭐⭐⭐ |

## 适用人群

- 👔 **老板 / 创业者**：评估外包报价、控制项目成本
- 📋 **PM / 项目经理**：管理需求变更、识别风险、推进交付
- 🧑‍💼 **技术总监 / 架构师**：技术选型 ROI 计算、组织能力建设

## 学习路径

1. **快速入门**（30 分钟）：看 `app-quote-breakdown`，5 分钟理解报价差异
2. **技术决策**（30 分钟）：看 mobile-tech-stack，评估技术栈对成本的影响
3. **合同避坑**（1 小时）：看 `outsourcing-pitfalls` → 当 checklist 用
