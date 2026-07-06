<!--
module:
  parent: system-design
  slug: system-design/observability
  type: article
  category: 主模块子文章
  summary: 可观测性（Observability）是现代分布式系统运维的核心能力。它让我们能够通过系统的外部输出来推断其内部状态，从而快速定位和解决问题。
-->

# 可观测性：Metrics + Logs + Traces

> 可观测性（Observability）是现代分布式系统运维的核心能力。它让我们能够通过系统的外部输出来推断其内部状态，从而快速定位和解决问题。

## 目录

- [可观测性 vs 监控](#可观测性-vs-监控)
- [三大支柱](#三大支柱)
  - [Metrics — 指标](#metrics--指标)
  - [Logs — 日志](#logs--日志)
  - [Traces — 链路追踪](#traces--链路追踪)
- [三大支柱的关联](#三大支柱的关联)
- [可观测性成熟度模型](#可观测性成熟度模型)
- [工具选型参考](#工具选型参考)

---
---

## 可观测性 vs 监控

### 核心区别

| 维度 | 监控（Monitoring） | 可观测性（Observability） |
|------|-------------------|--------------------------|
| **本质** | 已知问题的检测 | 未知问题的探索 |
| **方式** | 预设告警规则，被动响应 | 主动探索系统状态 |
| **问题** | "系统是否在正常范围内运行？" | "系统为什么出现了异常？" |
| **能力** | 告诉你"出了问题" | 帮助你"找到问题根源" |
| **方法** | 阈值告警 + Dashboard | 高基数数据 + 灵活查询 |

### 通俗比喻

> **监控** 是汽车的仪表盘：告诉你油量不足、水温过高。
> **可观测性** 是汽车维修站的诊断仪：不仅告诉你灯亮了，还能告诉你哪个传感器出了问题、为什么出问题。

### 两者的关系

可观测性不是替代监控，而是**包含**监控。监控是可观测性的子集：

```
┌─────────────────────────────────┐
│        可观测性                  │
│  ┌───────────────────────────┐  │
│  │       监控                 │  │
│  │  (告警 + Dashboard + 阈值) │  │
│  └───────────────────────────┘  │
│                                  │
│  + 灵活查询                      │
│  + 高基数数据分析                 │
│  + 问题根因定位                   │
│  + 未知问题探索                   │
└─────────────────────────────────┘
```

---

## 三大支柱

```
         ┌─────────────────┐
         │   可观测性       │
         │  Observability   │
         └────────┬────────┘
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
   ┌───────┐ ┌────────┐ ┌────────┐
   │Metrics│ │  Logs  │ │ Traces │
   │ 指标  │ │  日志   │ │ 链路   │
   └───────┘ └────────┘ └────────┘
   定量测量    离散事件    请求路径
   时间序列    文本记录    调用拓扑
```

### Metrics — 指标

**定义**: 指标是可度量的数值数据，通常以时间序列的形式存储，反映系统在某一时间点的状态。

#### 关键特征

- **聚合的**：通常是计数、求和、平均值等聚合结果
- **低存储成本**：相比日志和链路，存储开销最小
- **适合告警**：天然支持阈值判断和趋势分析
- **低基数**：标签（label）组合有限

#### RED 方法（面向请求的服务）

| 指标 | 英文 | 说明 | 示例 |
|------|------|------|------|
| Rate | 请求速率 | 每秒请求数 | `http_requests_total` |
| Errors | 错误率 | 失败请求占比 | `http_requests_errors_total` |
| Duration | 响应时长 | 请求耗时分布 | `http_request_duration_seconds` |

#### USE 方法（面向资源的服务）

| 指标 | 英文 | 说明 | 示例 |
|------|------|------|------|
| Utilization | 利用率 | 资源使用百分比 | `node_cpu_usage_ratio` |
| Saturation | 饱和度 | 排队等待程度 | `node_disk_io_time_ratio` |
| Errors | 错误数 | 资源错误计数 | `node_disk_errors_total` |

#### 关键指标一览

| 层级 | 关键指标 |
|------|----------|
| 应用层 | QPS、RT（P50/P95/P99）、错误率、活跃用户数、线程池使用率 |
| JVM 层 | GC 次数/耗时、堆内存使用、类加载数、线程数 |
| 数据库 | 连接数、慢查询数、QPS、锁等待时间、Buffer Pool 命中率 |
| 中间件 | 消息堆积量、消费延迟、Topic 分区数 |
| 系统层 | CPU、内存、磁盘 I/O、网络带宽、文件描述符 |

#### Prometheus + Grafana 示例

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'spring-boot-app'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['app-server:8080']
```

```java
// Spring Boot + Micrometer
@RestController
public class OrderController {

    private final Counter orderCounter;
    private final Timer orderTimer;

    public OrderController(MeterRegistry registry) {
        this.orderCounter = registry.counter("orders.created.total");
        this.orderTimer = registry.timer("orders.create.duration");
    }

    @PostMapping("/orders")
    public Order createOrder(@RequestBody OrderRequest req) {
        return orderTimer.record(() -> {
            Order order = orderService.create(req);
            orderCounter.increment();
            return order;
        });
    }
}
```

---

### Logs — 日志

**定义**: 日志是系统在运行过程中产生的离散事件记录，包含时间戳、级别、消息和上下文信息。

#### 日志级别

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| `TRACE` | 最详细 | 开发调试，记录每一步操作细节 |
| `DEBUG` | 调试信息 | 排查问题时的详细上下文 |
| `INFO` | 关键事件 | 应用启动/关闭、重要业务操作 |
| `WARN` | 警告 | 可恢复的异常、不推荐的操作 |
| `ERROR` | 错误 | 需要关注的异常，但系统仍可运行 |
| `FATAL` | 致命错误 | 系统无法继续运行 |

#### 结构化日志

结构化日志将日志以 JSON 等机器可读格式输出，便于索引和分析：

```json
{
  "timestamp": "2025-06-04T10:30:00.123Z",
  "level": "INFO",
  "logger": "com.example.OrderService",
  "thread": "http-nio-8080-exec-1",
  "traceId": "abc123def456",
  "spanId": "span-001",
  "userId": "user-789",
  "message": "Order created successfully",
  "orderId": "ORD-20250604-001",
  "amount": 299.00,
  "duration_ms": 45
}
```

#### 日志收集方案

| 方案 | 组件 | 特点 |
|------|------|------|
| ELK | Elasticsearch + Logstash + Kibana | 功能强大，资源消耗大 |
| EFK | Elasticsearch + Fluentd + Kibana | Fluentd 更轻量 |
| Loki | Grafana Loki + Promtail | 轻量级，与 Prometheus 生态集成 |
| 云方案 | AWS CloudWatch / 阿里云 SLS | 免运维，成本较高 |

#### Logback 配置示例（Spring Boot）

```xml
<!-- logback-spring.xml -->
<configuration>
    <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <customFields>{"app":"order-service","env":"prod"}</customFields>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="JSON"/>
    </root>
</configuration>
```

---

### Traces — 链路追踪

**定义**: 链路追踪记录一个请求在整个分布式系统中的完整调用路径，展示服务之间的依赖关系和每个环节的耗时。

#### 核心概念

| 概念 | 说明 |
|------|------|
| Trace | 一个完整的请求链路，由多个 Span 组成 |
| Span | 链路中的一个操作单元（如一次 RPC 调用、一次 DB 查询） |
| TraceID | 全局唯一的链路标识，贯穿整个调用链 |
| SpanID | 当前操作的唯一标识 |
| Parent SpanID | 父操作的 SpanID，构成调用树 |

#### Trace 数据结构

```
Trace: abc123def456
├── Span: span-001 [API Gateway]          0ms ─── 500ms
│   ├── Span: span-002 [Order Service]    5ms ─── 200ms
│   │   ├── Span: span-004 [DB Query]    10ms ─── 50ms
│   │   └── Span: span-005 [Cache Hit]   15ms ─── 20ms
│   └── Span: span-003 [Inventory Svc]  30ms ─── 350ms
│       └── Span: span-006 [RPC Call]    40ms ─── 300ms
└── Span: span-007 [Async Processing]   505ms ─── 800ms
```

#### OpenTelemetry

OpenTelemetry（OTel）是 CNCF 下的可观测性标准，提供统一的 API 和 SDK：

```java
// OpenTelemetry 手动埋点示例
@RestController
public class OrderController {

    private final Tracer tracer = GlobalOpenTelemetry.getTracer("order-service");

    @PostMapping("/orders")
    public Order createOrder(@RequestBody OrderRequest req) {
        // 创建一个 Span
        Span span = tracer.spanBuilder("createOrder")
                .setAttribute("order.amount", req.getAmount())
                .setAttribute("order.items.count", req.getItems().size())
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            // 业务逻辑 - 子 Span 会自动关联
            return orderService.create(req);
        } catch (Exception e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

#### 主流方案对比

| 方案 | 特点 | 适用场景 |
|------|------|----------|
| Jaeger | CNCF 毕业，功能完善，支持多种存储后端 | 通用分布式系统追踪 |
| Zipkin | Twitter 开源，轻量级，社区成熟 | 中小型系统 |
| SkyWalking | 国产，APM 全功能，自动探针 | Java 生态深度监控 |
| OpenTelemetry | 标准规范，多语言支持 | 新项目首选 |

---

## 三大支柱的关联

三大支柱不是孤立的，它们通过 **TraceID** 串联在一起：

```
                    TraceID: abc123def456
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
         ┌─────────┐ ┌─────────┐ ┌─────────┐
         │ Metrics  │ │  Logs   │ │ Traces  │
         │         │ │         │ │         │
         │ QPS: 100│ │[INFO]   │ │ span-001│
         │ RT: 45ms│ │ traceId │ │ span-002│
         │ Err: 0.1│ │ abc123  │ │ span-003│
         └─────────┘ └─────────┘ └─────────┘
              ▲           ▲           ▲
              └───────────┼───────────┘
                          │
                  同一个请求的
                  三种视角

典型排查流程:
  1. Metrics 告警 → "P99 延迟从 100ms 飙升到 2000ms"
  2. 用 TraceID 搜索 → 找到耗时异常的 Trace
  3. 查看 Trace → "Inventory Service 的 DB 查询耗时 1800ms"
  4. 用 TraceID 查 Logs → 看到具体的 SQL 和异常信息
  5. 根因定位 → "慢查询: 缺少索引"
```

### TraceID 透传

在微服务架构中，TraceID 需要在服务之间传递：

```
HTTP Header:
  X-Trace-Id: abc123def456
  X-Span-Id: span-002
  X-Parent-Span-Id: span-001

MDC (SLF4J):
  MDC.put("traceId", "abc123def456");
  log.info("Processing order"); // 日志自动包含 traceId
```

---

## 可观测性成熟度模型

| 级别 | 阶段 | 特征 | 能力 |
|------|------|------|------|
| L1 | 混沌期 | 无监控，出了问题才知道 | 用户反馈 → 被动修复 |
| L2 | 基础监控 | 有基础指标和日志，但分散 | Dashboard + 基础告警 |
| L3 | 集中化 | 日志和指标集中收集 | 统一 Dashboard + 关联查询 |
| L4 | 全链路 | 三大支柱完整集成 | 通过 TraceID 串联排查 |
| L5 | 智能化 | AIOps，自动根因分析 | 异常自动检测 + 自愈 |

### 各阶段关键指标

| 维度 | L1 | L2 | L3 | L4 | L5 |
|------|----|----|----|----|----|
| MTTR | 数小时~数天 | 数小时 | 数十分钟 | 数分钟 | 秒级 |
| 告警覆盖 | 无 | 基础资源 | 应用指标 | SLO 驱动 | 智能异常检测 |
| 日志 | 本地文件 | 集中收集 | 结构化 + 索引 | 与 Trace 关联 | AI 辅助分析 |
| 链路 | 无 | 无 | 关键路径 | 全量采集 | 自动拓扑发现 |

---

## SLO / SLI / Error Budget

SRE 体系下，可观测性的最终目标不是"看见指标"，而是驱动**服务质量可量化、可管理**的工程决策。SLO / SLI / Error Budget 是这一体系的核心概念。

### SLI（Service Level Indicator）— 服务等级指标

**定义**：SLI 是对服务质量某一方面的**量化测量**，是 SLO 计算的基础。

**常见 SLI 类型**

| 维度 | SLI 示例 | 测量方式 |
|------|----------|----------|
| 可用性 | 成功请求数 / 总请求数 | 统计 5xx、4xx、网络错误等失败请求占比 |
| 延迟 | P50 / P95 / P99 / P99.9 响应时间 | 直方图（Histogram）+ 分位数计算 |
| 吞吐量 | 每秒请求数（QPS/TPS） | 计数器（Counter） |
| 正确性 | 业务结果正确率 | 业务断言或回放测试 |
| 持久性 | 数据写入成功率 | 存储系统写入结果统计 |
| 端到端 | 关键业务路径成功率 | 真实用户监控（RUM）/ 合成监控 |

**示例**

```
SLI_availability = 1 - (错误请求数 / 总请求数)
SLI_latency_p99  = histogram_quantile(0.99, http_request_duration_seconds)
```

### SLO（Service Level Objective）— 服务等级目标

**定义**：SLO 是 SLI 的**目标值**或目标范围，是团队对用户的服务承诺。

**示例**

```
SLO：核心订单 API 可用性 ≥ 99.95%（月度）
SLO：搜索 API P99 延迟 < 200ms（滚动 28 天）
SLO：支付链路端到端成功率 ≥ 99.99%（季度）
```

**SLO 设计原则**

- **可衡量**：必须能用 SLI 量化
- **可达到**：基于现状+改进空间，不能拍脑袋定 100%
- **有约束**：与可用性成本直接相关，越高越贵
- **可沟通**：业务、研发、运维共同认可

### Error Budget — 错误预算

**定义**：Error Budget 是 **(1 - SLO) × 时间窗口** 内允许的"错误额度"。SLO 是承诺，Error Budget 是这个承诺之外允许犯错的预算。

**计算公式**

```
Error Budget = (1 - SLO) × 总请求数
            = (1 - SLO) × 时间窗口内的总请求量
```

**示例**

```
SLO = 99.9% 可用性
时间窗口 = 30 天
总请求数 = 1 亿次

Error Budget = (1 - 0.999) × 1 亿 = 10 万次失败请求
```

**时间维度的预算**

| SLO | 月度停机预算 | 季度停机预算 | 年度停机预算 |
|-----|--------------|--------------|--------------|
| 99% | 7.2 小时 | 21.6 小时 | 86.4 小时 |
| 99.9% | 43 分钟 | 2.16 小时 | 8.64 小时 |
| 99.95% | 21.6 分钟 | 64.8 分钟 | 4.32 小时 |
| 99.99% | 4.3 分钟 | 13 分钟 | 52.6 分钟 |

### SLO 驱动的发布决策

Error Budget 不仅是衡量指标，更是**约束开发节奏的工程工具**：

```
┌──────────────────────────────────────────┐
│         Error Budget 周期                 │
│                                          │
│   ┌────────────────────────────────┐     │
│   │ ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░ │     │
│   │ 已消耗           剩余预算       │     │
│   └────────────────────────────────┘     │
│                                          │
│   剩余预算 > 50%  →  正常发布节奏         │
│   剩余预算 20~50% →  谨慎发布、加大评审    │
│   剩余预算 < 20%  →  冻结非必要发布        │
│   预算耗尽        →  全面停止发布，转入    │
│                      可靠性改进专项        │
└──────────────────────────────────────────┘
```

**核心思想**：当 Error Budget 耗尽时，团队应当停止新功能发布，专注于**提升可靠性、偿还技术债**。这避免了"为了发版而牺牲稳定性"的反模式。

### SLO 与告警的区别

| 维度 | 传统告警 | SLO 告警 |
|------|----------|----------|
| 触发条件 | 单一指标阈值 | 错误预算燃烧速率 |
| 严重程度 | 静态分级 | 动态分级（基于预算剩余） |
| 决策依据 | 单一指标 | 多窗口、多燃烧率 |
| 行动指引 | 排查问题 | 排查问题 + 评估是否暂停发布 |

**多窗口、多燃烧率（Multi-Window, Multi-Burn-Rate）告警示例**

```
快窗口（1 小时）告警：过去 1 小时消耗月度预算的 2%
  → 提示：短期可能严重故障
慢窗口（6 小时）告警：过去 6 小时消耗月度预算的 5%
  → 提示：潜在的性能退化
两者同时告警 → 严重事故，需立即响应
```

---

## 工具选型参考

| 用途 | 开源方案 | 商业方案 |
|------|----------|----------|
| Metrics | Prometheus, VictoriaMetrics | Datadog, New Relic |
| Dashboards | Grafana | Grafana Cloud |
| Logs | ELK, Loki | Splunk, Datadog Logs |
| Traces | Jaeger, Zipkin, SkyWalking | Datadog APM, New Relic |
| 全栈 | OpenTelemetry + Grafana Stack | Datadog, Dynatrace |
| APM | SkyWalking, Pinpoint | AppDynamics, New Relic |

### 链路追踪方案选型：SkyWalking vs Jaeger vs Zipkin

三者都是主流的分布式链路追踪方案，但定位与能力有显著差异：

| 维度 | Jaeger | Zipkin | SkyWalking |
|------|--------|--------|------------|
| 出身 | Uber（→ CNCF 毕业） | Twitter | 国产（Apache 顶级） |
| 语言支持 | 多语言（Go/Java/Node/Python） | 多语言 | 多语言（Java 最强） |
| 探针方式 | 需手动/部分自动 | 需手动/部分自动 | 字节码增强（Java 自动） |
| Metrics/Logs | 需结合 Prometheus/Loki | 需结合外部方案 | 内置 Metrics + Logs + Traces |
| 拓扑分析 | 基础依赖图 | 简单 | 强（服务/实例/Endpoint 三层） |
| 告警 | 不支持 | 不支持 | 内置告警规则 |
| 存储后端 | ES/Cassandra/Kafka | ES/MySQL/Cassandra | ES/H2/MySQL/TiDB |
| 适用场景 | 通用分布式追踪、Go/Polyglot | 简单轻量、已有 ES 栈 | Java 生态深度监控、一体化 APM |

**选型建议**

- **Java 单语言 + 需要一体化 APM**（Metrics+Logs+Traces+告警）：选 **SkyWalking**，探针零侵入
- **多语言 + 已有 Prometheus/Grafana 栈**：选 **Jaeger**，与 CNCF 生态融合度高
- **资源受限 + 简单轻量**：选 **Zipkin**，部署最简单
- **新项目、多语言、面向未来**：基于 **OpenTelemetry** 规范，对接任意后端（Jaeger/Tempo/SkyWalking）

### 推荐方案（Java 生态）

```
Spring Boot + Micrometer + OpenTelemetry
        │
        ├── Metrics → Prometheus + Grafana
        ├── Logs    → Logback (JSON) → Loki / ELK
        └── Traces  → OpenTelemetry SDK → Jaeger / Tempo
```

## 参考资料

- [Google SRE Book - Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Google SRE Book - Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [OpenTelemetry](https://opentelemetry.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Loki](https://grafana.com/oss/loki/)
- [Jaeger](https://www.jaegertracing.io/)

## 相关章节

- [熔断降级](../../03-high-availability/circuit-break/README.md) — 触发熔断时通常依赖告警（状态变化、错误率）
- [限流](../../03-high-availability/rate-limiting/README.md) — 限流触发的告警与"接近阈值"告警
- [超时控制](../../03-high-availability/timeout/README.md) — 超时率、慢调用比例等关键监控指标
- [缓存设计模式](../../04-high-performance/cache-patterns/README.md) — 缓存命中率、击穿/雪崩的监控指标
- [部署与发布策略](../deploy/README.md) — 发布过程中的可观测性（错误率、延迟、流量回滚观测）
- [Spring Boot Actuator / Micrometer / Prometheus 集成](../../../06.spring/07-observability/README.md) — Spring 工程可观测性落地方案

← [返回: 系统设计 · observability](README.md)
