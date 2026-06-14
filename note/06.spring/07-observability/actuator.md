# Spring Boot Actuator 监控

> 最后更新: 2026-06-14
> ⬅️ [返回 07 可观测性](README.md) | [Micrometer](micrometer.md) | [Prometheus + Grafana](prometheus-grafana.md) | [健康检查三探针](health-probes.md) | [日志聚合](log-aggregation.md)

**Spring Boot Actuator** 是 Spring Boot 生态系统中的核心**生产就绪**模块，通过暴露 HTTP 端点和 JMX MBean 提供应用程序运行时状态的实时监控能力。其核心价值在于无需修改业务代码即可实现健康检查、性能指标采集、配置审计等功能，尤其适用于生产环境下的微服务监控场景。

---

## 🎯 一句话定位

**Actuator = "生产就绪工具箱"**——通过 `/actuator/**` 端点把应用的**健康状态、指标、配置、日志、线程**等运行时信息暴露给运维系统（Kubernetes、Prometheus、运维平台）。**指标采集**由 [Micrometer](micrometer.md) 完成，**指标存储/可视化**由 [Prometheus + Grafana](prometheus-grafana.md) 完成，本文档**只讲 Actuator 自身**。

---

## 一、依赖与启用

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<!-- 指标需配合 Micrometer 集成（Prometheus 格式输出） -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

**典型应用场景**：
- **Kubernetes 健康探测**：`/actuator/health` 端点 + [三探针（liveness/readiness/startup）](health-probes.md)
- **动态日志调整**：`/actuator/loggers` 实时修改日志级别
- **JVM 诊断**：`/actuator/heapdump` 生成堆转储文件分析内存泄漏
- **指标暴露**：`/actuator/prometheus` 提供 Prometheus 格式指标

---

## 二、端点暴露配置

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus  # 生产环境最小暴露面
        # include: *                              # 开发环境暴露全部
        base-path: /actuator                       # 自定义访问路径
        base-path: /manage                         # 也可改路径
  endpoint:
    health:
      show-details: always                        # always | when_authorized | never
      probes:
        enabled: true                             # 启用 K8s 探针（liveness/readiness）
      group:
        custom:                                    # 自定义健康分组
          include: db,redis,kafka
  endpoints:
    enabled-by-default: false                     # 默认关闭所有端点，按需开启
    health:
      enabled: true
    prometheus:
      enabled: true
```

---

## 三、核心端点速查

| 端点 | 路径 | 功能 | 敏感性 |
|:-----|:-----|:-----|:-------|
| `health` | `/actuator/health` | 聚合健康状态（DB、MQ、磁盘等） | 🟢 中（细节含依赖信息） |
| `info` | `/actuator/info` | 应用元信息（版本、构建时间、Git commit） | 🟢 低 |
| `metrics` | `/actuator/metrics` | 指标列表 + 详情 | 🟡 中 |
| `prometheus` | `/actuator/prometheus` | Prometheus 格式指标 | 🟡 中 |
| `loggers` | `/actuator/loggers` | 查看 / 动态修改日志级别 | 🔴 高（**写操作**） |
| `env` | `/actuator/env` | 生效的环境变量 + 配置属性 | 🔴 高（含密钥） |
| `configprops` | `/actuator/configprops` | 所有 `@ConfigurationProperties` | 🔴 高 |
| `beans` | `/actuator/beans` | Spring 容器中所有 Bean 依赖图 | 🟡 中 |
| `mappings` | `/actuator/mappings` | 所有 URL 映射 | 🟡 中 |
| `threaddump` | `/actuator/threaddump` | 线程栈快照 | 🟡 中 |
| `heapdump` | `/actuator/heapdump` | JVM 堆转储（下载 .hprof） | 🔴 高（含敏感数据） |
| `scheduledtasks` | `/actuator/scheduledtasks` | 所有 `@Scheduled` 任务 | 🟢 低 |
| `caches` | `/actuator/caches` | 缓存信息 | 🟢 低 |
| `conditions` | `/actuator/conditions` | 自动配置生效条件 | 🟢 低 |

> 📌 **生产最小暴露面**：`health,info,metrics,prometheus`——其余端点都按需开放。

---

## 四、自定义端点开发

通过代码暴露的HTTP或JMX接口，用于返回结构化数据或执行管理操作。

```java
@Component
@Endpoint(id = "customEndpoint")  // 端点路径：/actuator/customEndpoint
public class CustomEndpoint {

    @ReadOperation  // GET 请求
    public Map<String, String> customInfo() {
        return Map.of(
            "version", "1.0.0",
            "author", "DevTeam"
        );
    }

    @WriteOperation  // POST 请求（写操作，需授权）
    public String updateConfig(@Selector String key, String value) {
        // 实现配置更新逻辑
        return "Configuration updated: " + key + " = " + value;
    }
}
```

**注解层级**：

| 注解 | 适用 |
|:-----|:-----|
| `@Endpoint` | 同时暴露 Web + JMX |
| `@WebEndpoint` | 仅暴露 Web |
| `@JmxEndpoint` | 仅暴露 JMX |
| `@RestControllerEndpoint` | Web 端点 + 返回 `@ResponseBody` |
| `@ServletEndpoint` | 实现为 Servlet（如 `/heapdump`） |

**操作注解**：`@ReadOperation`（GET）、`@WriteOperation`（POST）、`@DeleteOperation`（DELETE）。

---

## 五、安全加固

### 1. 基于 Spring Security 保护

```java
@Configuration
public class ActuatorSecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/actuator/health", "/actuator/health/**").permitAll()  // 健康检查公开
            .requestMatchers("/actuator/prometheus").permitAll()                    // Prometheus 抓取
            .requestMatchers("/actuator/**").hasRole("ADMIN")                       // 其他需管理员
            .anyRequest().authenticated()
        ).httpBasic(Customizer.withDefaults());
        return http.build();
    }
}
```

### 2. 敏感端点脱敏

```yaml
management:
  endpoint:
    env:
      enabled: true
      show-values: WHEN_AUTHORIZED    # 仅认证用户可见敏感值（默认 NEVER）
    configprops:
      show-values: WHEN_AUTHORIZED
    heapdump:
      enabled: false                  # 生产建议直接关闭
  endpoints:
    web:
      exposure:
        exclude: env,heapdump,configprops  # 排除最危险端点
```

### 3. 端口隔离（高级）

将 Actuator 放在**独立端口**（避免与业务流量共享）：

```yaml
management:
  server:
    port: 9090                        # Actuator 独立端口
    address: 127.0.0.1                # 仅本机访问（配 Nginx 代理）
```

### 4. Actuator 暴露面清单（生产）

| 类别 | 端点 | 建议 |
|:-----|:-----|:-----|
| ✅ 公开 | `health`, `info`, `prometheus` | 内部网络/Prometheus 抓取 |
| ⚠️ 鉴权 | `metrics`, `loggers`, `mappings`, `beans` | 仅管理员 |
| ❌ 关闭 | `env`, `heapdump`, `configprops`, `threaddump` | 默认关闭，按需开启 |

---

## 六、自定义 HealthIndicator

`HealthIndicator` 是 Actuator 健康检查的核心接口。完整详解（`HealthIndicator` / `AbstractHealthIndicator` / `CompositeHealthContributor` / K8s 探针映射）见 [micrometer.md § 自定义 HealthIndicator](micrometer.md#二自定义-healthindicator) 与 [health-probes.md](health-probes.md)。

**最小示例**：

```java
@Component
public class OrderServiceHealthIndicator implements HealthIndicator {
    @Override
    public Health health() {
        if (orderRepository.count() > 0) {
            return Health.up().withDetail("count", orderRepository.count()).build();
        }
        return Health.down().withDetail("reason", "no orders").build();
    }
}
```

访问 `/actuator/health/orderService`：

```json
{
  "status": "UP",
  "details": { "count": 1234 }
}
```

---

## 七、动态日志级别

> 排查问题时**无需重启**即可调整日志级别——`/actuator/loggers` 是生产排障利器。

```bash
# 查看指定 logger 当前级别
curl http://localhost:8080/actuator/loggers/com.example.service

# 动态调整级别
curl -X POST http://localhost:8080/actuator/loggers/com.example.service \
  -H "Content-Type: application/json" \
  -d '{"configuredLevel":"DEBUG"}'
```

---

## 八、与 Micrometer / Prometheus 的协作

```
┌─────────────────────────────────────────────────────────────┐
│  Spring Boot 应用                                            │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────────┐    │
│  │ Actuator  │──>│  Micrometer  │──>│ /actuator/       │    │
│  │  端点暴露  │   │ 指标门面      │   │   prometheus     │    │
│  └──────────┘   └──────────────┘   └────────┬─────────┘    │
└──────────────────────────────────────────────┼──────────────┘
                                               │  scrape (pull)
                                  ┌────────────▼─────────┐
                                  │  Prometheus + Grafana │
                                  └──────────────────────┘
```

- **Actuator** = 端点暴露 + 健康检查 + 配置审计
- **Micrometer** = 指标采集门面（见 [micrometer.md](micrometer.md)）
- **Prometheus + Grafana** = 指标存储 + 可视化 + 告警（见 [prometheus-grafana.md](prometheus-grafana.md)）
- **K8s 探针** = 存活/就绪/启动三探针（见 [health-probes.md](health-probes.md)）
- **日志聚合** = Logback JSON + ELK/Loki（见 [log-aggregation.md](log-aggregation.md)）

---

## 九、4 大生产实践

1. **生产最小暴露面**——只暴露 `health,info,metrics,prometheus`，其他按需开启。
2. **敏感端点必须鉴权**——`env,heapdump,configprops,loggers` 一律 ADMIN 角色。
3. **健康检查分层**——Liveness 只看 JVM 状态，Readiness 才看依赖。
4. **heapdump 默认关闭**——内存快照含敏感数据，必要时通过 JMX 或 jcmd 离线采集。

---

## 🤔 思考

1. **Actuator 与 Micrometer 关系？** Actuator 负责**暴露端点**，Micrometer 负责**指标采集**——两者通过 `MeterRegistry` 解耦。
2. **生产应该暴露哪些端点？** 最小集：`health,info,metrics,prometheus`。
3. **health 端点如何保护？** `permitAll`（K8s/Prometheus 抓取），其他端点 ADMIN 鉴权。
4. **动态日志级别怎么用？** 排查时 POST `/actuator/loggers/<package>` 临时提级，问题定位后回滚。

---

## 相关章节

- ⬅️ [返回 07 可观测性](README.md)
- [Micrometer](micrometer.md) — 指标采集门面
- [Prometheus + Grafana](prometheus-grafana.md) — 指标存储与可视化
- [健康检查三探针](health-probes.md) — K8s liveness/readiness/startup
- [日志聚合](log-aggregation.md) — ELK / Loki / Fluentd
- [分布式追踪](../05-spring-cloud/distributed-tracing.md) — Tracing 深度
