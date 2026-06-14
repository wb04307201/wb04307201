# Micrometer 指标监控

> 最后更新: 2026-06-14
> ⬅️ [返回 07 可观测性](README.md) | [Prometheus + Grafana](prometheus-grafana.md) | [Spring Boot Actuator](actuator.md)

**Micrometer** 是 Spring Boot 的**指标门面**（类似 SLF4J 之于日志）——提供统一的指标 API，**底层可对接** Prometheus、Datadog、InfluxDB 等 12+ 种监控系统。

---

## 🎯 一句话定位

**Micrometer = "指标的 SLF4J"**——统一指标采集 API（Counter/Gauge/Timer），**通过注册不同的 MeterRegistry 适配**不同的监控系统（Prometheus、CloudWatch、Datadog）。Spring Boot Actuator 默认集成。

---

## 一、什么是 Micrometer

> **Micrometer** 是一个**指标收集门面库**（facade），被 Spring Boot 2.x+ 选为默认指标库。

| 特性 | 说明 |
|------|------|
| **定位** | 指标的 SLF4J |
| **支持的监控系统** | Prometheus、Datadog、CloudWatch、InfluxDB、Ganglia 等 12+ 种 |
| **核心组件** | Meter + MeterRegistry |
| **集成** | Spring Boot Actuator 默认集成 |

---

## 二、4 大核心指标类型

| 类型 | 用途 | 示例 |
|------|------|------|
| **Counter（计数器）** | 单调递增的计数 | 订单总数、错误数 |
| **Gauge（仪表）** | 实时值（可增可减） | 当前在线用户、队列大小 |
| **Timer（计时器）** | 测量耗时 + 调用次数 | 方法执行时间、HTTP 请求延迟 |
| **DistributionSummary（分布摘要）** | 测量数据分布 | 请求大小、响应大小 |

### 1. Counter（计数器）

> 单调递增的计数，常用于**累计统计**。

```java
@Component
public class OrderService {

    private final Counter orderCounter;

    public OrderService(MeterRegistry registry) {
        this.orderCounter = Counter.builder("order.created")
            .description("订单创建总数")
            .tag("type", "online")
            .register(registry);
    }

    public void createOrder(Order order) {
        orderRepository.save(order);
        orderCounter.increment();  // 计数 +1
    }
}
```

### 2. Gauge（仪表）

> **实时**反映某个值（可增可减），如在线用户数、内存使用。

```java
@Component
public class UserService {

    private final AtomicInteger onlineUsers = new AtomicInteger(0);

    public UserService(MeterRegistry registry) {
        Gauge.builder("users.online", onlineUsers, AtomicInteger::get)
            .description("在线用户数")
            .register(registry);
    }

    public void login() {
        onlineUsers.incrementAndGet();
    }

    public void logout() {
        onlineUsers.decrementAndGet();
    }
}
```

### 3. Timer（计时器）

> 测量方法执行时间 + 调用次数，常用于**性能监控**。

```java
@Component
public class OrderService {

    private final Timer orderTimer;

    public OrderService(MeterRegistry registry) {
        this.orderTimer = Timer.builder("order.create")
            .description("订单创建耗时")
            .publishPercentiles(0.5, 0.95, 0.99)  // P50/P95/P99
            .register(registry);
    }

    public Order createOrder(Order order) {
        return orderTimer.record(() -> {
            // 业务逻辑
            return orderRepository.save(order);
        });
    }
}
```

### 4. DistributionSummary（分布摘要）

> 测量**数据分布**（非时间），如请求大小、响应大小。

```java
@Component
public class FileService {

    private final DistributionSummary fileSizeSummary;

    public FileService(MeterRegistry registry) {
        this.fileSizeSummary = DistributionSummary.builder("file.size")
            .baseUnit("bytes")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(registry);
    }

    public void uploadFile(MultipartFile file) {
        fileSizeSummary.record(file.getSize());
    }
}
```

### 5. LongTaskTimer（长任务计时器）

> 测量**正在执行**中的任务耗时——`Timer` 测量**已完成**任务的耗时，`LongTaskTimer` 测量**正在执行**的任务（如批处理、异步任务、长连接）。

**与 Timer 的核心区别**：

| 维度 | Timer | LongTaskTimer |
|:-----|:------|:--------------|
| 测量对象 | **已完成**任务的耗时 | **正在执行**任务的耗时 |
| 数据点 | 每次 `record()` 增加一个 | 任务**运行期间**持续贡献 |
| 适用 | HTTP 请求、方法调用 | 批处理、异步任务、MQ 消费者、长轮询 |
| 输出指标 | 计数 + 总耗时 + 分布 | **active count（活跃数）** + **duration（总时长）** + **max（最长任务）** |

**API 用法**：

```java
@Component
public class BatchImportService {

    private final LongTaskTimer importTimer;

    public BatchImportService(MeterRegistry registry) {
        this.importTimer = LongTaskTimer.builder("batch.import.duration")
            .description("批处理导入任务耗时")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(registry);
    }

    public void importBatch(List<Order> orders) {
        // 启动采样（必须持有 Sample 引用，调用 stop 才结束）
        LongTaskTimer.Sample sample = importTimer.start();
        try {
            for (Order order : orders) {
                processOne(order);
            }
        } finally {
            sample.stop();
        }
    }
}
```

**输出指标**（Prometheus 格式）：

```
batch_import_duration_active_count    3    # 当前正在执行的任务数
batch_import_duration_duration_sum     12.5 # 所有活跃任务已运行的总秒数
batch_import_duration_max              8.1  # 当前活跃任务中最长的已运行时间
```

**适用场景**：
- **批处理任务**——每条记录的导入耗时
- **异步消息消费**——Kafka/RabbitMQ 消费者单条消息处理时间
- **长连接**——WebSocket 连接的存活时长
- **定时任务**——`@Scheduled` 任务的执行时长

**自动注册（ExecutorService 监控）**：

```java
@Bean
public ExecutorService batchExecutor(MeterRegistry registry) {
    return ExecutorServiceMetrics.monitor(
        registry,
        Executors.newFixedThreadPool(4),
        "batch.executor"
    );
}
```

**结合 `@Timed` 注解**：Micrometer AOP 模块**不支持** `LongTaskTimer`（因为 `@Timed` 假设方法会返回），需手动调用 `start()` / `sample.stop()`。

---

## 三、Tag（标签）—— 维度化指标

> **Tag = 指标的维度**。通过 Tag 可以在 Prometheus/Grafana 中**按维度筛选**。

```java
Counter.builder("order.created")
    .tag("type", "online")              // 订单类型
    .tag("channel", "mobile")           // 下单渠道
    .tag("user_level", "vip")           // 用户等级
    .register(registry);
```

**Tag 的常见维度**：
- 业务维度：订单类型、支付方式
- 技术维度：HTTP 方法、URL 模板
- 环境维度：region、env

> ⚠️ **不要用用户 ID 当 Tag**（基数爆炸，Prometheus 会挂）。

---

## 四、3 种使用方式

### 1. 注入 MeterRegistry

```java
@Service
public class OrderService {
    private final MeterRegistry registry;

    public OrderService(MeterRegistry registry) {
        this.registry = registry;
    }

    public void createOrder() {
        registry.counter("order.created").increment();
    }
}
```

### 2. @Timed 注解

```java
@Timed(value = "order.create", description = "订单创建耗时")
public Order createOrder(Order order) {
    return orderRepository.save(order);
}
```

### 3. 函数式编程

```java
Timer.Sample sample = Timer.start(registry);
try {
    // 业务逻辑
} finally {
    sample.stop(registry.timer("order.create"));
}
```

---

## 五、Spring Boot 自动注册的指标

> Spring Boot Actuator **自动注册大量指标**，无需写代码。

| 指标 | 说明 |
|------|------|
| `jvm.memory.used` | JVM 内存使用 |
| `jvm.gc.pause` | GC 暂停时间 |
| `http.server.requests` | HTTP 请求（自带 method/uri/status 标签） |
| `hikaricp.connections.active` | HikariCP 数据库连接池 |
| `system.cpu.usage` | 系统 CPU 使用率 |
| `process.cpu.usage` | 进程 CPU 使用率 |
| `logback.events` | 日志事件计数 |

### HTTP 请求指标（自动）

```yaml
# application.yml
management:
  metrics:
    tags:
      application: ${spring.application.name}
    distribution:
      percentiles-histogram:
        http.server.requests: true
      percentiles:
        http.server.requests: 0.5,0.95,0.99
```

---

## 六、4 种 MeterRegistry

> **同一个 Micrometer API，可对接 4+ 种监控系统**。

```xml
<!-- Prometheus -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>

<!-- Datadog -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-datadog</artifactId>
</dependency>

<!-- InfluxDB -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-influx</artifactId>
</dependency>
```

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: prometheus    # 暴露 /actuator/prometheus
  prometheus:
    metrics:
      export:
        enabled: true
```

访问 `http://localhost:8080/actuator/prometheus` 即可看到 Prometheus 格式的指标。

---

## 七、3 个生产实践

### 1. 业务关键指标

```java
@Service
public class OrderService {
    private final Counter successCounter;
    private final Counter failCounter;
    private final Timer timer;

    public OrderService(MeterRegistry registry) {
        this.successCounter = Counter.builder("order.create").tag("result", "success").register(registry);
        this.failCounter = Counter.builder("order.create").tag("result", "fail").register(registry);
        this.timer = Timer.builder("order.create.duration").register(registry);
    }

    public Order createOrder(OrderDTO dto) {
        return timer.record(() -> {
            try {
                Order order = orderRepository.save(new Order(dto));
                successCounter.increment();
                return order;
            } catch (Exception e) {
                failCounter.increment();
                throw e;
            }
        });
    }
}
```

### 2. 自定义 HealthIndicator

`HealthIndicator` 是 Spring Boot Actuator 的健康检查核心接口。每个 `HealthIndicator` Bean 都会作为 `/actuator/health` 的**子组件**贡献自己的健康状态。

#### 2.1 HealthIndicator 接口（基础版）

```java
@Component
public class OrderServiceHealthIndicator implements HealthIndicator {
    @Override
    public Health health() {
        try {
            long count = orderRepository.count();
            if (count > 0) {
                return Health.up().withDetail("count", count).build();
            }
            return Health.down().withDetail("reason", "no orders").build();
        } catch (Exception e) {
            // 异常未捕获 → 500 错误。建议改用 AbstractHealthIndicator
            throw new RuntimeException(e);
        }
    }
}
```

#### 2.2 AbstractHealthIndicator 抽象类（带 try/catch 包装）

**生产推荐**——自动捕获异常，转换为 `Health.down()`：

```java
@Component
public class DatabaseHealthIndicator extends AbstractHealthIndicator {

    @Autowired
    private DataSource dataSource;

    @Override
    protected void doHealthCheck(Health.Builder builder) {
        try (Connection conn = dataSource.getConnection()) {
            if (conn.isValid(3)) {
                builder.up().withDetail("database", "reachable");
            } else {
                builder.down().withDetail("database", "unreachable");
            }
        } catch (SQLException e) {
            // 自动转为 down(status=DOWN) + 异常信息
            builder.down(e);
        }
    }
}
```

#### 2.3 HealthContributor 组合接口（Spring Boot 2.2+）

`HealthContributor` 是 `HealthIndicator` 的父接口，允许**嵌套层级**。实现 `CompositeHealthContributor` 可表达"组件 → 子组件"的两级健康结构：

```java
@Component
public class ExternalServiceHealthContributor implements CompositeHealthContributor {

    private final Map<String, HealthContributor> contributors = new LinkedHashMap<>();

    public ExternalServiceHealthContributor() {
        contributors.put("payment", new PaymentServiceHealthIndicator());
        contributors.put("inventory", new InventoryServiceHealthIndicator());
        contributors.put("sms", new SmsServiceHealthIndicator());
    }

    @Override
    public Iterable<NamedContributor<HealthContributor>> iterator() {
        return contributors.entrySet().stream()
            .map(e -> NamedContributor.of(e.getKey(), e.getValue()))
            .collect(Collectors.toList());
    }

    @Override
    public HealthContributor getContributor(String name) {
        return contributors.get(name);
    }
}
```

访问 `/actuator/health/externalService`：

```json
{
  "status": "UP",
  "components": {
    "payment": { "status": "UP", "details": { ... } },
    "inventory": { "status": "DOWN", "details": { "reason": "timeout" } },
    "sms": { "status": "UP" }
  }
}
```

#### 2.4 命名约定与 K8s 探针映射

Actuator 自动识别以下 Bean 名称作为**保留的探针 contributor**：

| Bean 名称 | 端点 | 用途 |
|:----------|:-----|:-----|
| `xxxLivenessStateHealthIndicator` | `/actuator/health/liveness` | 失败 → K8s 重启 Pod |
| `xxxReadinessStateHealthIndicator` | `/actuator/health/readiness` | 失败 → 摘流量 |
| `xxxStartupHealthIndicator` | `/actuator/health/startup` | 慢启动应用专用 |
| `xxxHealthIndicator` | `/actuator/health/xxx` | 自定义健康项 |

> ⚠️ **Liveness 不要做依赖检查**——DB 抖动会触发 K8s 重启所有 Pod 雪崩；DB 检查放 Readiness。
> 详见 [health-probes.md](health-probes.md)。

#### 2.5 整体状态聚合规则

`/actuator/health` 顶层状态由所有子项聚合：

| 策略 | 规则 |
|:-----|:-----|
| **默认** | 任一子项 `DOWN` → 整体 `DOWN` |
| **`management.endpoint.health.group.*.include`** | 自定义分组聚合（按需聚合 DB、Redis、MQ 等） |
| **`management.endpoint.health.status.order`** | 自定义状态顺序（如 `DOWN > OUT_OF_SERVICE > UP > UNKNOWN`） |
| **`management.endpoint.health.status.http-mapping`** | 状态码映射（如 `DOWN → 503`、`OUT_OF_SERVICE → 200`） |

### 3. 自定义 Metrics Filter

```java
@Bean
public MeterFilter meterFilter() {
    return new MeterFilter() {
        @Override
        public Meter.Id map(Meter.Id id) {
            // 重命名指标
            if (id.getName().startsWith("myapp.")) {
                return id.withName("app." + id.getName().substring(6));
            }
            return id;
        }
    };
}
```

---

## 八、OTLP 与 OpenTelemetry 导出

> Micrometer Tracing 默认走 **Brave / Zipkin** 桥接（`micrometer-tracing-bridge-brave`），但 **OpenTelemetry（OTel）** 已成为云原生**链路追踪的事实标准**。Spring Boot 3.x+ 通过 `micrometer-tracing-bridge-otel` 提供与 OpenTelemetry SDK 的桥接，再由 OTLP 协议导出到任意兼容后端。

### 1. 与 Zipkin / Brave 的关系

```
Micrometer Tracing (API facade)
    │
    ├── bridge-brave ──> Brave ──> Zipkin reporter
    │                       │
    │                       └──> Zipkin / Zipkin-compatible (Jaeger)
    │
    └── bridge-otel  ──> OpenTelemetry SDK ──> OTLP exporter
                                                │
                                                ├──> OTel Collector
                                                ├──> Jaeger (原生 OTLP)
                                                ├──> Tempo
                                                ├──> SigNoz
                                                └──> 任何 OTLP 兼容后端
```

> 📌 **演进方向**：Brave 维护模式（不再大版本迭代），OpenTelemetry 是**未来标准**。新项目建议直接选 `bridge-otel`。

### 2. 依赖与配置

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
    <!-- OTLP HTTP/gRPC 导出器（二选一） -->
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-otlp</artifactId>
</dependency>
<dependency>
    <!-- Micrometer 指标也走 OTel（可选） -->
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-instrument-observation</artifactId>
</dependency>
```

```yaml
# application.yml
management:
  tracing:
    sampling:
      probability: 1.0         # 100% 采样（生产可降至 0.1）
  otlp:
    tracing:
      endpoint: http://otel-collector:4318/v1/traces
      timeout: 10s
    metrics:
      endpoint: http://otel-collector:4318/v1/metrics
```

### 3. OpenTelemetry SDK 集成

Micrometer 桥接会自动配置 `OpenTelemetry` SDK（`SdkTracerProvider` + `SdkMeterProvider` + `Resource`），通常**无需手动写代码**。如需自定义：

```java
@Bean
public OpenTelemetry openTelemetry(Resource resource, SdkTracerProvider tracerProvider) {
    return OpenTelemetrySdk.builder()
        .setTracerProvider(tracerProvider)
        .setPropagators(ContextPropagators.create(W3CTraceContextPropagator.getInstance()))
        .buildAndRegisterGlobal();
}
```

### 4. OTLP 协议：gRPC vs HTTP

| 协议 | 端口（Collector 默认） | 适用 |
|:-----|:---------------------|:----|
| **OTLP/gRPC** | `4317` | 高吞吐、低延迟（推荐） |
| **OTLP/HTTP** | `4318` | 防火墙友好（可走 80/443） |

### 5. 实战：docker-compose 启动 OTel Collector + Jaeger

```yaml
# docker-compose.yml
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.110.0
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP

  jaeger:
    image: jaegertracing/all-in-one:1.60
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686"  # Jaeger UI
      - "14250:14250"  # gRPC
```

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

exporters:
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true
  debug: {}

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp/jaeger, debug]
    metrics:
      receivers: [otlp]
      exporters: [debug]
```

应用启动后访问 `http://localhost:16686` 即可看到 Jaeger 中的调用链——数据流为：Spring Boot → OTLP → Collector → Jaeger。

### 6. 与 Prometheus 并存

OTel **不会**替代 Prometheus（指标存储仍是 Prometheus 主导），推荐**混合架构**：

- **指标** → Micrometer → Prometheus（pull）→ Grafana
- **链路** → Micrometer Tracing → OTel → OTLP → Collector → Jaeger / Tempo
- **日志** → Logback JSON → Filebeat/Promtail → Loki / ES

---

## 九、Micrometer vs Dropwizard Metrics

| 维度 | Micrometer | Dropwizard Metrics |
|------|-----------|---------------------|
| **维护方** | Spring 团队 | 社区 |
| **生态** | Spring Boot 默认 | 老牌 |
| **后端支持** | 12+ 种 | 较少 |
| **维度（Tag）** | ✅ 一等公民 | ⚠️ 弱 |
| **推荐** | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## 十、5 大最佳实践

1. **用 @Timed 替代手写 Timer**（AOP 自动织入）
2. **业务关键路径都打点**（订单、支付、登录）
3. **Tag 维度不要太多**（基数爆炸）
4. **P95/P99 比平均值更有意义**（平均值掩盖问题）
5. **结合 Prometheus + Grafana**（可视化 + 告警）

---

## 🤔 思考

1. **Counter 和 Gauge 区别？** Counter 单调递增（如订单总数）；Gauge 可增可减（如在线用户）。
2. **Timer 记录什么？** 调用次数 + 总耗时 + 分布（P50/P95/P99）。
3. **Tag 怎么设计？** 有限枚举维度（type、channel、status），避免用户 ID。
4. **为什么 Micrometer 是 Spring Boot 默认？** Spring 团队出品，与 Spring 生态深度集成。

---

## 相关章节

- ⬅️ [返回 07 可观测性](README.md)
- [Prometheus + Grafana](prometheus-grafana.md) — 可视化 + 告警
- [Spring Boot Actuator](actuator.md) — 指标暴露端点
- [分布式追踪](../05-spring-cloud/distributed-tracing.md) — Tracing + Metrics 统一
