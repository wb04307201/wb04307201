<!--
module:
  parent: null
  number: 06
  slug: spring
  topic: Spring 全家桶
  audience: Java 后端工程师
  category: 后端框架
  type: index
  summary: 从 IoC/AOP 到 Spring Boot/Cloud/Security/集成组件，Java 最主流框架完整知识体系
-->

# Spring 全家桶

> 一句话导览：从 IoC/AOP 核心容器到 Spring Boot/Cloud 微服务，再到事务/缓存/MyBatis 数据层、Spring Security 安全与可观测性——Java 后端最主流框架的完整知识地图。

---

## 🎯 一句话定位

**Spring 全家桶 = 核心容器（IoC/AOP）+ Web（MVC/WebFlux）+ 数据（事务/缓存/MyBatis）+ Boot（约定优于配置）+ Cloud（微服务治理）+ 集成（Validation/Retry/Batch）+ 可观测性（Actuator/Micrometer）+ Security（认证/授权/防护）+ 注解速查**——按"骨架 → 血肉 → 云原生 → 安全"层层递进。

---

## 📚 适用人群

- **Java 后端工程师**：掌握 Spring 是入行必备，本文档提供深度细节与踩坑点
- **Spring 学习者**：从 IoC/AOP 基础到 Cloud 微服务，3 段式学习路径覆盖完整知识体系
- **面试备战者**：配合 `13.split-hairs/06.spring` 的"咬文嚼字"专题，吃透高频考点

---

## 🗺️ 目录导航

> 数字基线：以"分类下 leaf MD 数（含所有子目录与子子目录）"为统计口径。
> 实际结构 = 31 个 README + 21 个 leaf README + 89 个非 README 子文章 = 141 个 .md 文件（2026-07-19 find 校对）。

| 序号 | 分类 | 核心内容 | Leaf 数 | 入口 |
|:----:|:----|:---------|:-------:|:----:|
| 01 | **核心容器** | IoC/AOP 原理、Bean 生命周期与循环依赖、FactoryBean、依赖注入（构造器/Setter/字段）、@Configuration Lite/Full、外部化配置、Event 机制、模块依赖、手写 mini Spring | **13** | [01-core/README.md](01-core/README.md) |
| 02 | **Web 层** | Spring MVC 流程、Filter/Interceptor/AOP 顺序、异常/视图/上传/CORS/i18n/异步、WebFlux 响应式（WebClient/R2DBC/Router Functions/测试）、SSE 实时推送 | **13** | [02-web/README.md](02-web/README.md) |
| 03 | **数据层** | 声明式/编程式事务、多数据源/JTA、JPA 事务、传播/隔离/失效、Spring Cache（4 大模式 + 多级缓存 + 序列化）、[**MyBatis 全栈 4 主题**](03-data/mybatis/README.md)（架构原理 / 扩展能力 / Spring 整合 / MyBatis-Plus） | **40** | [03-data/README.md](03-data/README.md) |
| 04 | **Spring Boot** | 自动配置原理、自定义 Condition 扩展、Starter 机制、spring.factories 迁移、启动流程、启动后钩子、外部化配置、内嵌服务器切换、GraalVM Native Image | **9** | [04-spring-boot/README.md](04-spring-boot/README.md) |
| 05 | **Spring Cloud** | 服务注册/配置中心（含加密）/负载均衡 RPC/熔断/网关（JWT 鉴权）/链路追踪/Stream/Bus/Seata 集成/版本对应 | **12** | [05-spring-cloud/README.md](05-spring-cloud/README.md) |
| 06 | **集成组件** | Validation（分组/跨字段/自定义）、Retry（Reactive）、StateMachine（持久化/并行）、Batch（重试/重启） | **6** | [06-integration/README.md](06-integration/README.md) |
| 07 | **可观测性** | Actuator 端点、健康探针、Micrometer（OTLP/LongTaskTimer）、Prometheus+Pushgateway、Grafana Alerting、ELK/Loki | **5** | [07-observability/README.md](07-observability/README.md) |
| 08 | **注解速查** | 事务/缓存/调度/校验/重试/AOP/Web/JPA/测试/配置/异常 等按场景分类的索引 | **12** | [08-annotations/README.md](08-annotations/README.md) |
| 09 | **Spring Security** | SecurityFilterChain 架构、认证（密码/JWT/OAuth2）、授权（@PreAuthorize/ACL）、OAuth2 四种授权模式、CORS/CSRF/Session/安全 Header | **6** | [09-security/README.md](09-security/README.md) |

**合计**：9 大分类 · **31 个 README · 21 个 leaf README · 89 个非 README 子文章**。

### 3.1 MyBatis 全栈专项（4 主题 · 27 篇）

03 数据层下设重点项目 [MyBatis 全栈](03-data/mybatis/README.md)，按 4 主题组织：

| 主题 | 目录 | 核心问题 | 篇数 |
|:----:|:----|:---------|:----:|
| 一、架构与原理 | [01-architecture/](03-data/mybatis/01-architecture/) | MyBatis 框架的内部机制：初始化、执行、组件、SQL、缓存、类图 | 8 |
| 二、扩展能力 | [02-extension/](03-data/mybatis/02-extension/) | TypeHandler / Interceptor / DatabaseIdProvider / 存储过程 | 4 |
| 三、Spring 整合 | [03-spring-integration/](03-data/mybatis/03-spring-integration/) | SqlSessionFactory / Mapper 扫描 / 事务 / 多数据源 / 二级缓存 | 5 |
| 四、MyBatis-Plus | [04-mybatis-plus/](03-data/mybatis/04-mybatis-plus/) | CRUD / Wrapper / 分页 / 代码生成器 | 10 |

---

## 🧭 学习路径

### 第 1 段：基础（IoC/AOP → Boot 入门）

```
01-core/ioc/                  → IoC 容器、Bean 生命周期、循环依赖
01-core/aop/                  → AOP 切面编程与代理机制
02-web/mvc/                   → Spring MVC 请求处理
03-data/transaction/          → 声明式事务
04-spring-boot/auto-configuration → 自动配置原理
```

**目标**：掌握 Spring 核心机制，能独立搭建 Spring Boot 单体应用。

### 第 2 段：进阶（Boot 精通 → Cloud 微服务 → Security）

```
04-spring-boot/externalized-configuration → 外部化配置
04-spring-boot/embedded-server → 内嵌服务器切换
09-security/filter-chain/     → SecurityFilterChain 架构
09-security/authentication/   → 认证机制（密码/JWT/OAuth2）
09-security/authorization/    → 授权机制（@PreAuthorize/ACL）
05-spring-cloud/service-registry/ → 服务注册/发现（Nacos/Consul）
05-spring-cloud/config-center.md → 配置中心
05-spring-cloud/gateway.md → API 网关（含 JWT 鉴权）
05-spring-cloud/circuit-breaker.md → 熔断/限流（Resilience4j/Sentinel）
```

**目标**：能设计 Spring Cloud 微服务架构，掌握 Spring Security 认证授权，理解分布式核心问题。

### 第 3 段：整合（数据层深化 + 可观测性 + 安全深化 + 注解速查）

```
03-data/cache/multi-level.md → 多级缓存架构
03-data/transaction/distributed/ → 分布式事务（Seata AT/TCC/Saga）
03-data/mybatis/03-spring-integration/ → Spring × MyBatis 工程整合
06-integration/validation/ → 参数校验
06-integration/batch.md → 批处理
07-observability/ → Actuator + Micrometer + Prometheus
09-security/oauth2/ → OAuth2 与 JWT 深入（授权服务器/Token 刷新/SSO）
09-security/cors-csrf/ → CORS/CSRF/Session/安全 Header 完整防护
08-annotations/ → 注解速查（按场景分类索引）
```

**目标**：掌握企业级 Spring 应用的全部生产特性，配合监控/日志/追踪构建可观测系统。

---

## 📖 开源参考

> 本节保留项目早期"开源参考"段落，并补充更完整的相关开源项目清单。

### 缓存与性能

- [Caffeine](https://github.com/ben-manes/caffeine) —— Java 高性能本地缓存（多级缓存的 L1 选择，参见 [03-data/cache/multi-level.md](03-data/cache/multi-level.md)）
- [Redis](https://github.com/redis/redis) —— 分布式缓存事实标准（多级缓存的 L2 选择）
- [JetCache](https://github.com/alibaba/jetcache) —— 阿里开源多级缓存框架（Spring Cache 整合）

### 安全与认证

- [Spring Security](https://github.com/spring-projects/spring-security) —— Spring 生态安全框架（[09-security](09-security/README.md) 研究对象）
- [Spring Authorization Server](https://github.com/spring-projects/spring-authorization-server) —— OAuth2 授权服务器实现
- [jjwt](https://github.com/jwtk/jjwt) —— Java JWT 库（JWT 生成/验证/解析）

### 微服务治理

- [Nacos](https://github.com/alibaba/nacos) —— 注册中心 + 配置中心（Spring Cloud Alibaba 推荐）
- [Sentinel](https://github.com/alibaba/Sentinel) —— 流量治理（熔断/限流/热点）
- [Seata](https://github.com/seata/seata) —— 分布式事务（AT/TCC/Saga/XA 4 种模式）
- [Spring Cloud Gateway](https://github.com/spring-cloud/spring-cloud-gateway) —— 响应式 API 网关

### 数据访问

- [MyBatis](https://github.com/mybatis/mybatis-3) —— 半自动 ORM（[MyBatis 全栈](03-data/mybatis/README.md) 专题研究对象）
- [MyBatis-Plus](https://github.com/baomidou/mybatis-plus) —— MyBatis 增强工具集（CRUD/Wrapper/代码生成器）
- [HikariCP](https://github.com/brettwooldridge/HikariCP) —— Spring Boot 默认连接池

### 可观测性

- [Micrometer](https://github.com/micrometer-metrics/micrometer) —— 指标门面库（类似 SLF4J 之于日志）
- [Prometheus](https://github.com/prometheus/prometheus) —— 指标采集与告警
- [Grafana](https://github.com/grafana/grafana) —— 指标可视化与 Dashboard
- [Jaeger](https://github.com/jaegertracing/jaeger) —— 分布式链路追踪（[05-spring-cloud/distributed-tracing.md](05-spring-cloud/distributed-tracing.md) 配合 Micrometer Tracing）

### 工具与教学

- [Mini Spring（microrest）](01-core/minispring/microrest/README.md) —— 200 行手写实现 IoC + MVC 的教学项目（项目内）

---

## 🔗 相关章节

- ⬆️ [返回笔记目录](../README.md)
- ↔️ [01.java](../01.java/README.md) —— Java 语言基础（Spring 的语言载体）
- ↔️ [04.system-design](../04.system-design/README.md) —— 系统设计（Spring Cloud 的理论基础）
- ↔️ [13.split-hairs/06.spring](../13.split-hairs/06.spring/README.md) —— Spring 咬文嚼字（高频面试考点）

---

## 🏆 最佳实践速览

| 领域 | 实践要点 |
|------|---------|
| **依赖注入** | 优先构造器注入，避免 `@Autowired` 字段注入；配合 `@RequiredArgsConstructor` 简化 |
| **事务管理** | `@Transactional` 标注在 Service 层；注意同类调用失效、异常类型匹配、传播行为选择 |
| **缓存** | 多级缓存（Caffeine L1 + Redis L2）；`@Cacheable` + 自定义 KeyGenerator；防穿透用空值缓存 |
| **配置管理** | `@ConfigurationProperties` 替代 `@Value`；多环境 Profile 隔离；敏感配置加密 |
| **异常处理** | `@RestControllerAdvice` 全局统一；业务异常继承 `RuntimeException`；错误码规范化 |
| **安全** | `SecurityFilterChain` Bean 方式配置（废弃 `WebSecurityConfigurerAdapter`）；JWT 无状态认证；方法级 `@PreAuthorize`；REST API 禁用 CSRF |
| **可观测性** | Actuator + Micrometer 指标暴露；分布式追踪（Micrometer Tracing → OTLP）；结构化日志 |

---

## 🎯 高频面试题（咬文嚼字）

针对面试中反复深挖的细节问题，见 [13.split-hairs/06.spring](../13.split-hairs/06.spring/)：

| 主题 | 难度 | 核心问题 |
|------|:----:|:---------|
| [@Transactional 失效 8 种场景](../13.split-hairs/06.spring/transactional-pitfalls/) | ⭐⭐⭐⭐⭐ | 同类调用 / 异常类型 / 多线程 / 传播行为 |
| [Bean 生命周期详解](../13.split-hairs/06.spring/bean-lifecycle/) | ⭐⭐⭐⭐ | 实例化 → 注入 → 初始化 → 销毁 12 步 |
| [为什么不推荐 @Autowired](../13.split-hairs/06.spring/not-use-@autowired/) | ⭐⭐⭐ | 字段注入 vs 构造器注入 |

---

## 📖 外部参考

- [Spring 官方文档](https://spring.io/docs)
- [Spring Boot 参考指南](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [Spring Cloud 参考指南](https://spring.io/projects/spring-cloud)
- [Spring Security 参考指南](https://docs.spring.io/spring-security/reference/)
- [Spring Authorization Server](https://docs.spring.io/spring-authorization-server/docs/current/reference/html/)
- [Spring 全家桶中文文档](https://springdoc.cn/)

---

> 🚀 从 [01 核心容器](01-core/README.md) 开始你的 Spring 全家桶之旅

---

← [返回笔记目录](../README.md)