<!--
module:
  parent: system-design
  slug: system-design/01-prometheus
  type: article
  category: 主模块子文章
  summary: 一份按场景梳理的 Prometheus 速查手册：从数据模型到生产告警的完整实战。
-->

# Prometheus · 云原生监控体系实战

> 一份按场景梳理的 Prometheus 速查手册：从数据模型到生产告警的完整实战。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

Prometheus · 云原生监控体系实战 本应该很简单，一份按场景梳理的 Prometheus 速查手册：从数据模型到生产告警的完整实战

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、Prometheus 简介

Prometheus 是 CNCF 毕业的开源监控系统，专为云原生和容器化场景设计。

### 1.1 核心特性

- **多维度数据模型**：时间序列用 metric name + labels 标识
- **PromQL 查询语言**：灵活的查询和聚合
- **Pull 模式**：主动拉取（而不是 Agent push）
- **服务发现**：自动发现 K8s / Consul / Eureka 中的 targets
- **告警管理**：Alertmanager 分组 / 抑制 / 静默
- **时序数据库**：本地 TSDB（高效压缩）

### 1.2 适用场景

- ✅ K8s 集群监控
- ✅ 微服务 / 中间件监控
- ✅ 业务指标监控（自定义 metrics）
- ❌ 大数据 APM（用 SkyWalking / Jaeger）
- ❌ 日志聚合（用 Loki / ELK）

---

## 二、核心架构

```
┌──────────────────────────────────────────────────┐
│  应用 / 中间件（暴露 /metrics 端点）                  │
│  Node Exporter / JVM / MySQL Exporter             │
└────────────────────┬─────────────────────────────┘
                     │ HTTP Pull（每 15 秒）
                     ↓
┌──────────────────────────────────────────────────┐
│  Prometheus Server                                 │
│  ┌────────┐ ┌──────┐ ┌──────────┐ ┌──────────┐  │
│  │Retrieval│ │TSDB │ │ PromQL  │ │ HTTP API │  │
│  └────────┘ └──────┘ └──────────┘ └──────────┘  │
│         ↓                                            │
│    Alert Rules → Alertmanager                       │
└────────────────────┬─────────────────────────────┘
                     │ Web UI / Grafana
                     ↓
              ┌──────────────┐
              │   Grafana     │
              │  (可视化)      │
              └──────────────┘
```

---

## 三、数据模型（Metric + Labels）

### 3.1 Metric 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **Counter**（计数器）| 只能递增 | http_requests_total |
| **Gauge**（仪表盘）| 可增可减 | node_memory_usage_bytes |
| **Histogram**（直方图）| 分布统计 + 分位数 | http_request_duration_seconds |
| **Summary**（摘要）| 类似 Histogram，客户端算分位数 | rpc_duration_seconds |

### 3.2 示例

```promql
# 一段时间内 HTTP 请求总数
http_requests_total{method="POST", handler="/api/users", status="200"}

# 内存使用量（可增可减）
node_memory_Active_bytes{instance="web-1", job="node"}

# 请求延迟分布（自动分桶）
http_request_duration_seconds_bucket{le="0.005"}
http_request_duration_seconds_bucket{le="0.01"}
http_request_duration_seconds_bucket{le="0.05"}
```

### 3.3 Labels 维度

Labels 是 K-V 对，用于切片：
```
http_requests_total{method="POST", handler="/api", status="200"}  1000
http_requests_total{method="POST", handler="/api", status="500"}  5
http_requests_total{method="GET", handler="/api", status="200"}   5000
```

**避免高基数 labels**（如 user_id / email / phone）：会让 TSDB 爆掉。

---

## 四、PromQL 查询实战

### 4.1 基础查询

```promql
# 1. 简单查询
up                                          # 1 = 在线，0 = 离线
node_cpu_seconds_total                       # CPU 时间

# 2. 时间范围
node_cpu_seconds_total[5m]                  # 最近 5 分钟
node_cpu_seconds_total[1h]                  # 最近 1 小时

# 3. 速率（rate）
rate(node_cpu_seconds_total[5m])            # CPU 使用率（每秒）
rate(http_requests_total[1m])               # HTTP QPS

# 4. 聚合
sum(rate(http_requests_total[5m]))          # 总 QPS
sum by (status)(rate(http_requests_total[5m]))  # 按状态分组
```

### 4.2 进阶查询

```promql
# 1. Histogram 计算 P99
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))

# 2. 错误率
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

# 3. 预测
predict_linear(node_filesystem_avail_bytes[6h], 4 * 3600) < 0

# 4. 内存使用率
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes
```

---

## 五、服务发现（自动发现 Targets）

### 5.1 K8s 服务发现

```yaml
# prometheus.yml
scrape_configs:
- job_name: 'kubernetes-pods'
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
    action: keep
    regex: true
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
    action: replace
    target_label: __metrics_path__
    regex: (.+)
```

### 5.2 文件服务发现

```yaml
scrape_configs:
- job_name: 'node'
  file_sd_configs:
  - files:
    - 'targets/nodes/*.json'
```

---

## 六、Exporter 生态

| Exporter | 用途 |
|---------|------|
| **node_exporter** | 主机指标（CPU / 内存 / 磁盘）|
| **cAdvisor** | 容器指标 |
| **kube-state-metrics** | K8s 对象指标 |
| **jmx_exporter** | JVM 应用 |
| **mysqld_exporter** | MySQL |
| **redis_exporter** | Redis |
| **nginx-prometheus-exporter** | Nginx |
| **rabbitmq_exporter** | RabbitMQ |
| **blackbox_exporter** | 黑盒监控（HTTP / TCP / ICMP）|
| **kafka_exporter** | Kafka |

---

## 七、应用埋点（自定义 Metrics）

### 7.1 Java（Micrometer）

```java
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;

Counter ordersCounter = Counter.builder("orders_total")
    .description("Total orders")
    .tag("status", "success")
    .register(meterRegistry);

ordersCounter.increment();
```

### 7.2 Python（prometheus_client）

```python
from prometheus_client import Counter, start_http_server

orders_counter = Counter('orders_total', 'Total orders', ['status'])

orders_counter.labels(status='success').inc()

start_http_server(8000)  # 暴露 /metrics
```

### 7.3 Go（prometheus/client_golang）

```go
import "github.com/prometheus/client_golang/prometheus"

var ordersCounter = prometheus.NewCounterVec(
    prometheus.CounterOpts{Name: "orders_total"},
    []string{"status"},
)

func init() {
    prometheus.MustRegister(ordersCounter)
}

func main() {
    ordersCounter.WithLabelValues("success").Inc()
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":8080", nil)
}
```

---

## 八、告警规则（Alertmanager）

### 8.1 告警规则示例（prometheus.yml）

```yaml
groups:
- name: example
  rules:
  - alert: HighErrorRate
    expr: |
      sum(rate(http_requests_total{status=~"5.."}[5m]))
      /
      sum(rate(http_requests_total[5m]))
      > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }} for service {{ $labels.service }}"

  - alert: PodDown
    expr: kube_pod_status_phase{phase="Running"} == 0
    for: 5m
    labels:
      severity: warning

  - alert: DiskSpaceLow
    expr: |
      (node_filesystem_avail_bytes{mountpoint="/"} * 100)
      / node_filesystem_size_bytes{mountpoint="/"} < 10
    for: 10m
    labels:
      severity: warning
```

### 8.2 Alertmanager 路由

```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'cluster']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-critical'
  routes:
  - match:
      severity: critical
    receiver: 'pagerduty'
  - match:
      severity: warning
    receiver: 'slack-warning'

receivers:
- name: 'slack-critical'
  slack_configs:
  - api_url: https://hooks.slack.com/xxx
  channel: '#alerts-critical'
```

---

## 九、Prometheus 高可用与扩展

### 9.1 单实例 Prometheus（适合中小规模）

```
1 Prometheus + 1 Alertmanager + 1 Grafana
```

### 9.2 HA（双实例 + Thanos）

```
2 Prometheus（联邦 / HA 模式）
  ↓
Thanos（长期存储 + 全局查询）
  ↓
对象存储（S3 / OSS / GCS）
```

### 9.3 Mimir / Cortex（生产级）

- **Mimir**（Grafana Labs）：水平扩展 PB 级
- **Cortex**（CNCF）：多租户

---

## 十、最佳实践

1. **Metric 命名规范**：`{namespace}_{subsystem}_{name}_{unit}`（如 `http_requests_total`）
2. **避免高基数 labels**：不要把 user_id / email 作为 label
3. **合理设置 scrape_interval**：通常 15-30 秒
4. **使用 recording rules**：把复杂查询预计算
5. **保留策略**：根据存储成本设置（15d / 30d / 90d）
6. **告警分级**：critical / warning / info
7. **告警去重 + 分组**：Alertmanager 自动处理
8. **不要把 Prometheus 当日志系统**：用 Loki / ELK

---

← [返回可观测性专题](../README.md) · 📅 2026-06-28