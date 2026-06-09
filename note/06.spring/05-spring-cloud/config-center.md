# 配置中心（Config Center）

> 最后更新: 2026-06-09
> ⬅️ [返回 05 Spring Cloud](README.md) | [服务注册](service-registry/) | [分布式追踪](distributed-tracing.md)

配置中心是微服务架构的"**配置大脑**"——集中管理所有服务的配置，**配置变更实时推送**，告别改配置要重启 N 个服务的痛苦。

---

## 🎯 一句话定位

**配置中心 = "微服务的 application.yml 集中仓"**——所有服务的配置统一存储在配置中心（Git、Nacos、Apollo），**应用启动时拉取配置**，**配置变更时实时推送**。最常用方案：**Nacos Config**（国内主流） / **Spring Cloud Config + Git**（传统方案）。

---

## 一、为什么需要配置中心

### 单体应用

```yaml
# application.yml
spring.datasource.url=jdbc:mysql://localhost:3306/db
```

✅ 简单，配置文件在工程里，改完重启。

### 微服务（50 个服务 × 5 个环境 = 250 个配置文件）

| 痛点 | 配置中心解决方案 |
|------|----------------|
| 配置文件散落各处 | **集中管理** |
| 改配置要重启 50 个服务 | **实时推送** |
| 多环境配置难管理 | **环境隔离**（dev/test/prod） |
| 配置变更无审计 | **版本管理** + 变更记录 |
| 敏感配置明文存储 | **加密存储** |

---

## 二、3 大主流方案对比

| 方案 | 维护方 | 配置存储 | 实时推送 | 适用场景 |
|------|--------|---------|---------|---------|
| **Nacos Config** | 阿里 | 内置 DB / MySQL | ✅ 长轮询 | **国内主流**、一站式（注册+配置） |
| **Apollo** | 携程 | MySQL | ✅ 长轮询 + 推送 | **大厂首选**、功能完善 |
| **Spring Cloud Config** | Spring | **Git** | ❌ 需配合 Bus | 传统方案、版本管理依赖 Git |

> 📌 2025 年新项目**首选 Nacos Config**（一站式，部署简单）。

---

## 三、Nacos Config 实战（**推荐**）

### 1. 添加依赖

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
</dependency>
```

### 2. bootstrap.yml 配置

```yaml
spring:
  application:
    name: order-service
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        file-extension: yaml
        namespace: dev
        group: DEFAULT_GROUP
        refresh-enabled: true
```

### 3. Nacos 控制台添加配置

Data ID: `order-service.yaml`
Group: `DEFAULT_GROUP`
配置内容：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/order
    username: root
    password: 123456
custom:
  feature: enabled
```

### 4. 代码使用

```java
@RestController
@RefreshScope  // 配置变更时刷新 Bean
public class ConfigController {

    @Value("${custom.feature}")
    private String feature;

    @GetMapping("/feature")
    public String getFeature() {
        return feature;
    }
}
```

### 5. 多环境隔离

```
Nacos Namespace（命名空间）= 环境
- dev（开发）
- test（测试）
- prod（生产）
```

每个 Namespace 下的 Data ID 必须唯一。

---

## 四、Apollo 实战

### 1. 添加依赖

```xml
<dependency>
    <groupId>com.ctrip.framework.apollo</groupId>
    <artifactId>apollo-client</artifactId>
</dependency>
```

### 2. application.yml

```yaml
app:
  id: order-service
apollo:
  meta: http://apollo-config:8080
  bootstrap:
    enabled: true
    namespaces: application,mysql.yml
```

### 3. 启用 Apollo

```java
@SpringBootApplication
@EnableApolloConfig  // 启用 Apollo
public class OrderServiceApplication { ... }
```

### 4. 代码使用

```java
@RestController
public class ConfigController {

    @Value("${custom.feature:default}")
    private String feature;

    // 或
    @ApolloConfig
    private Config config;

    @GetMapping("/feature")
    public String getFeature() {
        return config.getProperty("custom.feature", "default");
    }
}
```

---

## 五、Spring Cloud Config 实战

### 1. Config Server 端

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-config-server</artifactId>
</dependency>
```

```yaml
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/myorg/config-repo
          default-label: main
          search-paths: '{application}'
```

```java
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication { ... }
```

### 2. Config Client 端

```yaml
spring:
  cloud:
    config:
      uri: http://localhost:8888
      name: order-service
      profile: dev
```

> ⚠️ **Spring Cloud Config 默认不支持实时推送**——需要配合 **Spring Cloud Bus（Kafka/RabbitMQ）** 才能实现配置变更实时推送。

---

## 六、3 大方案对比表

| 维度 | Nacos Config | Apollo | Spring Cloud Config |
|------|--------------|--------|---------------------|
| **配置存储** | 内置 DB / MySQL | MySQL | Git |
| **实时推送** | ✅ 长轮询（1s） | ✅ 长轮询 + 推送 | ❌ 需 Bus |
| **多环境** | Namespace | Cluster | Profile |
| **灰度发布** | ✅ | ✅ | ❌ |
| **权限管理** | ✅ | ✅ 完善 | ❌ 依赖 Git |
| **审计日志** | ✅ | ✅ 完善 | Git 提交历史 |
| **部署难度** | ⭐ 简单 | ⭐⭐ 中 | ⭐⭐ 中 |
| **运维成本** | 低 | 中（需自建 Portal） | 中（需自建 Bus） |
| **国内使用** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

---

## 七、4 个核心概念（以 Nacos 为例）

### Data ID

> 一个配置文件，**通常等于 `application.name + file-extension`**。

例：`order-service.yaml`

### Group

> 配置分组，**默认 `DEFAULT_GROUP`**。用于将多个 Data ID 归类。

### Namespace

> **命名空间 = 环境隔离**。每个 Namespace 独立。

### 配置推送

```
Nacos Server ← → Nacos Client（长轮询，1s 间隔）
              ↓
        推送变更
              ↓
        @RefreshScope Bean 重建
```

---

## 八、生产最佳实践

### 1. 命名规范

```
Data ID: {应用名}-{环境}.{扩展名}
例：order-service-dev.yaml
```

### 2. 敏感配置加密

```yaml
spring:
  datasource:
    password: ENC(xxxxxxxxxxx)  # 加密存储
```

### 3. 配置变更通知

> 配置变更通过 Spring Cloud Bus 推送到所有服务实例。

### 4. 灰度发布

> 先发布到部分实例，验证后再全量。

### 5. 配置回滚

> 通过版本管理（一键回滚到历史版本）。

---

## 🤔 思考

1. **Nacos 和 Apollo 怎么选？** Nacos 一站式（注册+配置），简单易用；Apollo 配置中心功能更完善（权限/审计）。
2. **配置中心挂了怎么办？** 本地缓存（Spring Cloud Config 有本地副本）；Nacos Client 缓存快照。
3. **配置推送有延迟吗？** Nacos 1s（长轮询），Apollo 准实时（HTTP 长轮询 + 推送）。
4. **配置中心和配置文件的优先级？** 远程配置 > 本地 application.yml。

---

## 相关章节

- ⬅️ [返回 05 Spring Cloud](README.md)
- [服务注册](service-registry/) — 服务注册中心
- [负载均衡](load-balancer.md) — 从配置中心读取负载均衡策略
- [04 Spring Boot/外部化配置](../04-spring-boot/externalized-config-and-profiles.md) — 本地配置加载顺序
