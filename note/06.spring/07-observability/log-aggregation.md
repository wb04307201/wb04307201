# 日志聚合（ELK / Loki / Fluentd）

> ⬅️ [返回 07 可观测性](README.md) | [Actuator](actuator.md) | [Micrometer](micrometer.md)

**日志聚合** = 把分散在各 Pod/容器的 stdout/stderr 集中采集、索引、检索、可视化。Spring Boot 默认通过 Logback 输出，**生产环境必须**配合集中式日志平台（ELK 或 Loki），否则排查问题如同大海捞针。

---

## 🎯 一句话定位

**Spring Boot 输出 JSON 结构化日志 → 采集层（Fluentd / Filebeat） → 存储层（Elasticsearch / Loki） → 展示层（Kibana / Grafana）**——并在日志中**自动注入 traceId/spanId**，实现"看到一条错误日志 → 直接跳到调用链"。

---

## 一、两条主流路线对比

| 方案 | 组件 | 索引方式 | 适用场景 | 资源消耗 |
|:-----|:-----|:---------|:--------|:--------|
| **ELK 经典** | Elasticsearch + Logstash/Fluentd + Kibana | **全文索引** | 需要复杂全文搜索、聚合分析 | 高（ES 重） |
| **Loki 轻量** | Loki + Promtail/Fluentd + Grafana | **仅索引元数据**（不索引内容） | K8s 云原生、成本敏感、已有 Grafana | 低（Loki 轻） |

> 📌 **Grafana 已统一**——Grafana 同时支持 ES 与 Loki 作为数据源，仪表盘与告警可复用。

---

## 二、Spring Boot 结构化 JSON 日志

生产环境**强烈建议**输出 JSON 格式，便于采集层直接转发，避免 Logstash 的 `grok` 解析。

### 1. 添加 Logback JSON Encoder 依赖

```xml
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>7.4</version>
</dependency>
```

### 2. 配置 `logback-spring.xml`

```xml
<configuration>
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>spanId</includeMdcKeyName>
            <customFields>{"app":"order-service","env":"prod"}</customFields>
            <fieldNames>
                <timestamp>@timestamp</timestamp>
                <message>msg</message>
                <logger>logger</logger>
                <thread>thread</thread>
            </fieldNames>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="STDOUT"/>
    </root>
</configuration>
```

### 3. 输出示例

```json
{
  "@timestamp": "2026-06-14T10:23:45.123+08:00",
  "level": "ERROR",
  "logger": "com.example.OrderService",
  "thread": "http-nio-8080-exec-3",
  "msg": "订单创建失败",
  "traceId": "7a3b4c5d6e7f8a9b",
  "spanId": "1a2b3c4d5e6f7a8b",
  "app": "order-service",
  "env": "prod"
}
```

---

## 三、MDC 链路追踪 ID 透传

**MDC（Mapped Diagnostic Context）** = Logback/SLF4J 提供的**线程局部上下文**，可在日志输出时自动附加 key-value 字段。**与 Micrometer Tracing 集成**后，traceId/spanId 会自动写入 MDC。

### 1. 与 Micrometer Tracing 自动集成

只要引入 `micrometer-tracing-bridge-brave` 或 `micrometer-tracing-bridge-otel`，并配置日志 pattern 包含 `%X{traceId}` / `%X{spanId}`，链路 ID 即自动注入。

### 2. 业务代码手动写入

```java
import org.slf4j.MDC;

MDC.put("userId", "12345");
MDC.put("orderNo", "ORD202606140001");
try {
    log.info("开始处理订单");
    // 业务逻辑
} finally {
    MDC.remove("userId");
    MDC.remove("orderNo");
}
```

### 3. Logback 文本格式（非 JSON 时的回退方案）

```xml
<pattern>
  %d{yyyy-MM-dd HH:mm:ss.SSS} %-5level [%thread] [traceId=%X{traceId:-}, spanId=%X{spanId:-}] %logger{36} - %msg%n
</pattern>
```

输出：`2026-06-14 10:23:45.123 ERROR [http-nio-8080-exec-3] [traceId=7a3b4c5d, spanId=1a2b3c4d] c.e.OrderService - 订单创建失败`

---

## 四、ELK 方案落地

### 1. Filebeat 收集（推荐，比 Logstash 轻）

```yaml
# filebeat.yml
filebeat.inputs:
  - type: container
    paths:
      - /var/log/containers/order-service-*.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "order-service-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"
```

### 2. docker-compose 启动

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.3
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports: ["9200:9200"]

  kibana:
    image: docker.elastic.co/kibana/kibana:8.15.3
    ports: ["5601:5601"]
    depends_on: [elasticsearch]

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.15.3
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on: [elasticsearch]
```

### 3. Kibana 查询：按 traceId 拉日志

```
app: "order-service" AND traceId: "7a3b4c5d6e7f8a9b"
```

---

## 五、Loki 轻量方案落地

### 1. Promtail 收集

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    static_configs:
      - targets: [localhost]
        labels:
          job: containerlogs
          __path__: /var/log/containers/order-service-*.log
    pipelineStages:
      - docker: {}
      - match:
          selector: '{job="containerlogs"}'
          stages:
            - json:
                expressions:
                  level: level
                  traceId: traceId
            - labels:
                level:
                traceId:
```

### 2. docker-compose

```yaml
services:
  loki:
    image: grafana/loki:3.3.0
    ports: ["3100:3100"]

  promtail:
    image: grafana/promtail:3.3.0
    volumes:
      - ./promtail-config.yaml:/etc/promtail/config.yaml
      - /var/log/containers:/var/log/containers:ro
    depends_on: [loki]

  grafana:
    image: grafana/grafana
    ports: ["3000:3000"]
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 3. Grafana 中按 traceId 查询

```logql
{app="order-service"} |= "7a3b4c5d6e7f8a9b"
```

---

## 六、与 Micrometer Tracing 协同

```
HTTP 请求 →  Micrometer Tracing 创建 traceId/spanId
            ↓
            自动写入 MDC（traceId, spanId）
            ↓
            Logback 输出（JSON 字段或文本 pattern）
            ↓
            Filebeat / Promtail 收集
            ↓
            ES / Loki 存储
            ↓
            Kibana / Grafana 检索 → 跳转 Jaeger 查看完整调用链
```

> 📌 **日志 + 追踪统一体验**：在 Kibana/Grafana 中用 `traceId` 检索出该请求的**所有日志**，再点击跳转到 Jaeger/Tempo 看**完整调用链**——这是云原生可观测性的"杀手锏"。

---

## 七、4 大生产实践

1. **必须输出 JSON**——别用人类可读格式，机器解析成本太高。
2. **traceId/spanId 必入 MDC**——否则日志和链路无法关联。
3. **采样率合理**——生产 100% 采样日志成本高，可 10%~100% 采样链路 + 100% 采样 ERROR。
4. **日志级别动态调整**——通过 `/actuator/loggers` 临时提级排查，无需重启。

---

## 相关章节

- ⬅️ [返回 07 可观测性](README.md)
- [Actuator](actuator.md) — `/actuator/loggers` 动态日志级别
- [Micrometer](micrometer.md) — Micrometer Tracing 桥接
- [分布式追踪](../05-spring-cloud/distributed-tracing.md) — traceId 透传与采样策略
