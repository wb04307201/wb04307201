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

# 五、工具
## Git
### [Git 命令清单](05.tools/git/command/README.md)
### [Gitea](05.tools/git/gitea/README.md)
## Docker
### [Docker 命令](05.tools/docker/command/README.md)
### [Docker 镜像](05.tools/docker/images/README.md)
### [Podman](05.tools/docker/podman/README.md)
## [Nginx](05.tools/nginx/README.md)
### [Pingora](05.tools/nginx/pingora/README.md)
## [Monorepo](05.tools/monorepo/README.md)
## [阿里微服务](05.tools/ali-microservices/README.md)
## Java
### [Hutool、Apache Commons、Guava工具库](05.tools/java/tool-library/README.md)
### [Lombok注解如何让Java开发效率飙升](05.tools/java/lombok/README.md)

# 六、[Spring](06.spring/README.md)

> 从 Spring 核心到 Spring Boot / Cloud / 集成组件 / 可观测性 / 注解速查，系统覆盖 Spring 全家桶。

## 章节导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [01 核心容器](06.spring/01-core/README.md) | IoC/AOP 原理、Bean 生命周期与循环依赖（三级缓存）、FactoryBean、依赖注入（构造器/Setter/字段）、@Configuration Lite/Full、外部化配置、Event 机制、模块依赖、手写 mini Spring |
| 2 | [02 Web 层](06.spring/02-web/README.md) | Spring MVC 流程、Filter/AOP 顺序、异常/视图/上传/CORS/i18n/异步、WebFlux 响应式（WebClient/R2DBC/Router Functions/测试）、SSE |
| 3 | [03 数据层](06.spring/03-data/README.md) | 声明式/编程式事务、多数据源/JTA、JPA 事务、传播/隔离/失效、Seata 分布式事务、Spring Cache 4 大模式 + 多级缓存 + 序列化 |
| 4 | [04 Spring Boot](06.spring/04-spring-boot/README.md) | 自动配置原理、自定义 Condition 扩展、Starter 机制、spring.factories 迁移、启动流程、启动后钩子、外部化配置、内嵌服务器切换、GraalVM Native Image |
| 5 | [05 Spring Cloud](06.spring/05-spring-cloud/README.md) | 服务注册/配置中心（含加密）/负载均衡 RPC/熔断/网关（JWT 鉴权）/链路追踪/Stream/Bus/Seata 集成/版本对应 |
| 6 | [06 集成组件](06.spring/06-integration/README.md) | Validation（分组/跨字段/自定义）、Retry（Reactive）、StateMachine（持久化/并行）、Batch（重试/重启） |
| 7 | [07 可观测性](06.spring/07-observability/README.md) | Actuator 端点、健康探针、Micrometer（OTLP/LongTaskTimer）、Prometheus+Pushgateway、Grafana Alerting、ELK/Loki |
| 8 | [08 注解速查](06.spring/08-annotations/README.md) | 事务/缓存/调度/校验/重试/AOP/Web/JPA/测试/配置/异常 等按场景分类的索引 |

> 开源参考：
> - [Multi-Level Cache Spring Boot Starter](https://gitee.com/wb04307201/multi-level-cache-spring-boot-starter) — 通过 `CacheManager` 接口扩展多级缓存注解
> - [Method Trace Log](https://gitee.com/wb04307201/methodTraceLog) — 基于 Spring AOP + Micrometer 的方法调用追踪工具

# 七、[工作流](07.workflow/README.md)

> 工作流 = **BPMN 流程骨架（确定性、可审计）** + **事件驱动协作神经（异步、弹性）**。从工作流概念定义到 BPMN 流程引擎（Camunda 7/8/Zeebe）、微服务编排（编舞 vs 编排）、事件驱动编排（EventMesh / Serverless Workflow）系统覆盖。

## 目录导航

| 序号 | 主题 | 核心内容 |
|:----:|:----|:---------|
| 1 | [工作流定义](07.workflow/define/README.md) | 业务/技术视角、BPMN 2.0 三要素（FlowObject / ConnectingObject / Artifact）、请假审批实例 |
| 2 | [流程引擎](07.workflow/process-engine/README.md) | 4 阶段工作原理、5 里程碑、3 大引擎对比（Camunda/Flowable/Activiti）、5 维度选型决策树 |
| 2a | [Camunda 7 实战](07.workflow/process-engine/camunda/camunda-7/README.md) | SpringBoot 集成 / Swagger / bpmn-js / 5 大任务节点类型 |
| 2b | [Camunda 8 / 云原生](07.workflow/process-engine/camunda/camunda-8/README.md) | Zeebe 内核、10K+ 实例/秒、8.5+ AI Agent Sub-process、fromAi() FEEL |
| 2c | [Zeebe 引擎](07.workflow/process-engine/camunda/camunda-8/zeebe/README.md) | Client/Gateway/Broker/Exporter 4 大组件 + Mermaid graph TB 架构图 |
| 3 | [工作流引擎与微服务编排](07.workflow/workflow-and-microservice-orchestration/README.md) | 编舞（choreography）vs 编排（orchestration）、Zeebe/Conductor/Cadence |
| 4 | [事件驱动与 Serverless Workflow](07.workflow/apache-eventmesh/README.md) | 事件驱动作为工作流的「神经系统」、CNCF Serverless Workflow DSL 标准、EventMesh 组件、电商订单落地 |

# 八、[Mybatis](08.mybatis/README.md)
## [MyBatis拦截器](08.mybatis/interceptor/README.md)
## [Mybatis-Plus](08.mybatis/mybatis-plus/README.md)
### [MyBatis-Plus Generator ：自动生成代码的利器](08.mybatis/mybatis-plus/generator/README.md)
### [条件构造器Wrapper](08.mybatis/mybatis-plus/Wrapper/README.md)
### [LambdaQueryWrapper 中的序列化函数式接口 SFunction](08.mybatis/mybatis-plus/Wrapper/lambdaQueryWrapper-function/README.md)

# 九、其他
## [常用系统](09.other/common-systems/README.md)
### [ERP](09.other/common-systems/erp/README.md)
### [PDM](09.other/common-systems/pdm/README.md)
## 无代码平台
### [宜搭介绍](09.other/nocode/yida/README.md)
### [简道云介绍](09.other/nocode/jiandaoyun/README.md)
### [零代码平台架构设计](09.other/nocode/design/README.md)
## [Hapoop](09.other/hadoop/README.md)

# 十、[大数据](10.big-data/README.md)
## [2024年的开源数据工程生态系统全景图](10.big-data/open-source/README.md)
## [离线数仓/实时数仓](10.big-data/offline-or-real-time-data-warehouse/README.md)

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

# 十二、前端
## [前端框架](12.font-end/frameworks/README.md)
## [CORS 跨域](12.font-end/cors/README.md)
## [微前端](12.font-end/micro-frontend/README.md)
## [Web Components](12.font-end/web-components/README.md)

# 十三、咬文嚼字
## 01.java/
### [高频面试题](13.split-hairs/01.java/questions/README.md)
### [创建对象](13.split-hairs/01.java/create-object/README.md)
### [单例模式](13.split-hairs/01.java/singleton-pattern/README.md)
### [Integer缓存](13.split-hairs/01.java/integer-cache/README.md)
### [`String str = new String("123")`会在堆中生成几个新对象](13.split-hairs/01.java/new-string/README.md)
### [Java 为什么将基础数据类型（如 int、double 等）封装为对象](13.split-hairs/01.java/object/README.md)
### [`switch`前使用`if`针对高频热点状态的优化](13.split-hairs/01.java/if-before-switch/README.md)
### [ArrayList去重](13.split-hairs/01.java/arrayList-distinct/README.md)
### [数据结构选择：HashSet 替代 LinkedList 查找](13.split-hairs/01.java/replace-linkedlist-with-hashset/README.md)
### [并发编程优化：Atomic 类替代 synchronized](13.split-hairs/01.java/replace-synchronized-with-atomic/README.md)
### [字符串拼接优化：StringBuilder 重用](13.split-hairs/01.java/reuse-of-stringbuilder/README.md)
### [快速给Map排序](13.split-hairs/01.java/sort-map/README.md)
### [1GB级别的`HashMap`的扩容](13.split-hairs/01.java/hashmap-resizing/README.md)
### [快速安全地往HashMap里插入大量条数据](13.split-hairs/01.java/large-data-into-hashmap/README.md)
## 03.数据库
### 关系型数据库
#### MySQL
##### [MySQL的事务隔离机制](13.split-hairs/03.database/relational-database/mysql/isolation/README.md)
##### [`INT(4)` 的定义](13.split-hairs/03.database/relational-database/mysql/int(4)-define/README.md)
##### [1亿条数据快速加索引的方法](13.split-hairs/03.database/relational-database/mysql/quickly-add-index/README.md)
##### [时间类型对比](13.split-hairs/03.database/relational-database/mysql/time-types/README.md)
##### [MySQL 中 COUNT(*)、COUNT(1)、COUNT(字段名) 的区别与性能比较](13.split-hairs/03.database/relational-database/mysql/count/README.md)
##### [MySQL慢查询调优](13.split-hairs/03.database/relational-database/mysql/tuning/README.md)
##### [在MySQL中，执行 `SELECT * FROM table WHERE id = ? FOR UPDATE` 语句时加什么锁？](13.split-hairs/03.database/relational-database/mysql/what-lock/README.md)
## NoSQL数据库
### Redis
#### [如何查找但不导致Redis阻塞](13.split-hairs/03.database/nosql/key-value/redis/search/README.md)
## 04.系统设计
### 高性能
#### 消息队列
###### [MQ消息积压](13.split-hairs/04.system-design/high-performance/mq/mq-backlog/README.md)
###### [有了kafka为什么还要有rocketmq？](13.split-hairs/04.system-design/high-performance/mq/still-need-rocketmq/README.md)
## 06.Spring
### [Spring里为什么不推荐使用@ Autowired](13.split-hairs/06.spring/not-use-@autowired/README.md)
### [分清PO、VO、DTO、BO、DAO、POJO](13.split-hairs/06.spring/clarify-various-o/README.md)
## 11.AI
### [AI思维-抛硬币](13.split-hairs/11.ai/ai-thinking/README.md)
## 12.前端
### [HTTP 请求中的 GET 和 POST](13.split-hairs/12.font-end/get-and-post/README.md)
### [网页端接受推送消息的方式](13.split-hairs/12.font-end/message/README.md)
### [前端存储方式](13.split-hairs/12.font-end/storage/README.md)

# 十四、[「阿明餐厅」技术系列](14.story/index.md)
> 以餐厅经营为叙事主线，用 30+ 篇故事讲透从架构演进到 AI 转型的技术全景。
## 系列导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [0. 系列导览](14.story/index.md) | 术语表（160+ 词）、一页纸速查 |
| 2 | [1. 前传 · 架构演进](14.story/02-system-architecture-evolution.md) | 架构是"长"出来的、IT 成熟度 L1-L7 评估 |
| 3 | [2. 正传 · 核心技术（15 篇）](14.story/04-peak-traffic-defense.md) | 流量治理、可观测性、安全、QA、CI/CD、API、数据、前端、故障、性能、MQ、分布式、实时、多端、数据库迁移 |
| 4 | [3. 番外 · 专题拓展（7 篇）](14.story/03-refactoring-guide-for-pm.md) | 重构、FinOps、SaaS 多租户、搜索推荐、知识工程、低代码、国际化 |
| 5 | [4. 续集 · AI Agent（6 篇）](14.story/01-ai-agent-architecture.md) | AI Agent 架构、AI 学习、组织转型、AI 原生创业、自进化组织、AI 幻觉治理 |
