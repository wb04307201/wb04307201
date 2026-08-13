# SPEC for note-temp/04.spring-backend/

> **Inherits from**: [../SPEC.md](../SPEC.md)
> **Mode**: append + override
> **Updated**: 2026-08-13

---

## 模块定位

Spring 生态 + 后端框架（Spring Boot / Spring Cloud / 微服务框架）。

## 从 L0 继承

- G1-G6 通用评分维度
- 11 类基础扫描规则
- 命名约定 + commit 格式 + 互链规则

## 本模块规则

### 评估维度（追加 G 维度后）

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| A1 | 源码级深度 | 有源码片段 + WHY 注释 | 有代码只解释 WHAT | 无代码 |
| A2 | 版本演进对比 | 有 Boot 2.x vs 3.x 对比 | 提及差异未展开 | 无版本 |
| A3 | ❌/✅ 反例对比 | 有正反例（自动配置陷阱） | 只有正确用法 | 无对比 |
| A4 | 参数调优表 | 有 actual config + 调优建议 | 有表无建议 | 无参数 |
| A5 | 场景压测数据 | 有启动时间/内存/QPS 实测 | 有数字无场景 | 无数据 |

### 写作要求

- 所有 Spring 示例注明 Boot/Spring Framework/Cloud 版本与关键依赖。
- 自动配置、事务、连接池、序列化和异步边界须展示生效条件与常见陷阱。
- 配置示例使用可复制的 YAML/Java 片段，并解释为什么选择该值。
- 至少给出一个生产场景的启动时间、内存、吞吐或故障恢复观测结果。

### 子目录约定

- `01-core/`：IoC、AOP、事件、资源、事务与核心扩展点。
- `02-boot/`：自动配置、配置管理、打包、测试和 Actuator。
- `02-web/`：Web MVC/WebFlux、HTTP、参数校验与异常处理。
- `03-cloud/`：服务治理、配置中心、服务发现与云端集成。
- `04-data/`：Spring Data、数据访问、缓存与消息抽象。
- `06-integration/`：消息、批处理、远程调用与外部系统集成。
- `07-observability/`：指标、日志、链路追踪和健康检查。
- `08-annotations/`、`09-security/`：常用注解、认证授权与安全实践。