<!--
module:
  parent: system-design
  slug: system-design/03-loki
  type: article
  category: 主模块子文章
  summary: 一份按场景梳理的 Loki 速查手册：从部署架构到 LogQL 查询的完整实战。
-->

# Loki · 云原生日志聚合系统实战

> 一份按场景梳理的 Loki 速查手册：从部署架构到 LogQL 查询的完整实战。

---
---

## 一、Loki 简介

Loki 是 Grafana Labs 出品的云原生日志聚合系统，灵感来自 Prometheus —— 像 Prometheus 处理指标一样处理日志。

### 1.1 核心特性

- **轻量级**：不建索引，只对标签建索引
- **水平扩展**：无状态 Distributor + 有状态 Ingester + Store
- **Grafana 原生**：与 Grafana 无缝集成
- **LogQL**：类似 PromQL 的日志查询语言
- **低成本**：比 ELK 节省 10x 存储成本

### 1.2 与 ELK 对比

| 维度 | ELK（Elasticsearch） | Loki |
|------|--------------------|------|
| **索引** | 全文索引（重）| 标签索引（轻）|
| **存储** | 大（10x Loki）| 小（压缩 + 对象存储）|
| **查询** | 全文搜索 | 标签 + grep |
| **运维** | 复杂（JVM 调优）| 简单 |
| **适合** | 全文检索 / 复杂查询 | 云原生 / 大规模日志 |

---

## 二、Loki 架构

```
┌──────────────────────────────────────────────────┐
│  应用 / Pod（输出 stdout/stderr 日志）              │
│       ↓                                             │
│  Promtail / Alloy（日志采集 Agent）               │
└────────────────────┬─────────────────────────────┘
                     │ Push（gzip + protobuf）
                     ↓
┌──────────────────────────────────────────────────┐
│  Loki Cluster                                       │
│  ┌────────────┐ ┌─────────┐ ┌──────────┐         │
│  │ Distributor│ │ Ingester │ │ Querier  │         │
│  │（路由/限流）│ │（写入）  │ │（查询）  │         │
│  └────────────┘ └────┬────┘ └────┬─────┘         │
│                      ↓              ↓             │
│              ┌─────────────────────────────┐     │
│              │ Object Storage (S3 / OSS / TSDB)│     │
│              └─────────────────────────────┘     │
└──────────────────────────────────────────────────┘
                     ↓ LogQL 查询
              ┌──────────────┐
              │   Grafana     │
              └──────────────┘
```

---

## 三、组件详解

### 3.1 Distributor（分发器）

- 接收来自 Agent 的日志流
- 验证 + 路由 + 限流
- 无状态（水平扩展）

### 3.2 Ingester（写入器）

- 接收 Distributor 的日志
- 写入 WAL（Write-Ahead Log）
- 定期 flush 到对象存储
- 内存缓存最近数据（热查询）

### 3.3 Querier（查询器）

- 处理 LogQL 查询
- 从 Ingester + 对象存储读取
- 返回结果

### 3.4 Query Frontend（查询前端）

- 大查询拆分
- 并行执行
- 结果缓存

### 3.5 Store（存储）

- 长期存储对象（S3 / OSS / GCS）
- 块存储（chunks）+ 索引（boltdb-shipper）

---

## 四、部署模式

### 4.1 Monolithic Mode（单体，小规模）

```yaml
# loki-config.yaml
auth_enabled: false
server:
  http_listen_port: 3100

common:
  instance_addr: 127.0.0.1
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
  - from: 2020-10-24
    store: tsdb
    object_store: filesystem
    schema: v13
    index:
      prefix: index_
      period: 24h
```

### 4.2 Microservices Mode（微服务，生产）

```bash
# 通过 Helm 安装
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki \
  --set loki.storage.type=s3 \
  --set loki.storage.s3.bucket=loki-data \
  --set loki.storage.s3.region=us-east-1
```

### 4.3 K8s Helm 完整部署

```bash
# Prometheus + Loki + Grafana 完整栈
helm install loki grafana/loki \
  --set monitoring.enabled=true

# Alloy（日志采集）+ Loki + Grafana
helm install alloy grafana/alloy \
  --set lokiAddress=loki:3100
```

---

## 五、日志采集（Promtail / Alloy）

### 5.1 Promtail（旧版，推荐 Alloy）

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: system
    static_configs:
      - targets: [localhost]
        labels:
          job: syslog
          __path__: /var/log/*.log
```

### 5.2 Grafana Alloy（新版，推荐）

```yaml
# alloy.river
local.file_match "pod_logs" {
  path_targets = [{"__path__" = "/var/log/pods/*/*/*.log"}]
}

loki.source.file "pod_logs" {
  targets    = local.file_match.pod_logs.targets
  forward_to = [loki.write.default.receiver]
}

loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

### 5.3 K8s 自动发现

Alloy 自动发现 K8s Pod 日志（带 pod / namespace / container 标签）：

```
{loki}/logs?query={namespace="production", container="myapp"}
```

---

## 六、LogQL 查询实战

### 6.1 基本查询

```logql
# 1. 所有日志
{job="myapp"}

# 2. 多标签组合
{job="myapp", level="error"}

# 3. 文本过滤（grep）
{job="myapp"} |= "error"

# 4. 不包含
{job="myapp"} != "debug"

# 5. 正则
{job="myapp"} |~ "error|fail"

# 6. 时间范围
{job="myapp"} |= "error" | json | duration > 1s
```

### 6.2 进阶查询（解析日志）

```logql
# 1. JSON 解析
{job="myapp"} | json | status_code >= 500

# 2. Logfmt 解析
{job="myapp"} | logfmt | level="error"

# 3. 模板提取字段
{job="myapp"} | json | user_id="12345"

# 4. 聚合（每秒错误数）
sum(rate({job="myapp"} |= "error" [5m]))

# 5. P99 延迟
quantile_over_time(0.99,
  {job="myapp"} | json | unwrap duration [5m]
) by (endpoint)
```

### 6.3 关联追踪

```logql
# 通过 trace_id 关联 Tempo
{job="myapp"} | json | trace_id="abc123"
→ Tempo UI 显示完整调用链
```

---

## 七、LogQL 高级技巧

### 7.1 结构化日志模板

```json
{
  "timestamp": "2026-06-28T10:00:00Z",
  "level": "ERROR",
  "service": "myapp",
  "trace_id": "abc123",
  "user_id": "12345",
  "endpoint": "/api/users",
  "duration_ms": 1234,
  "message": "Database timeout"
}
```

### 7.2 非结构化日志处理

```logql
# 用正则提取字段
{job="legacy"} | regexp `(?P<ip>\d+\.\d+\.\d+\.\d+)`

# 用 line_format 添加字段
{job="myapp"} | line_format "{{.status_code}} {{.message}}"
```

---

## 八、存储后端选择

| 存储 | 适用 |
|------|------|
| **S3 / OSS / GCS** | 云原生（首选）|
| **MinIO** | 自建对象存储 |
| **GCS / Azure Blob** | 多云 |
| **文件系统** | 本地开发 |

---

## 九、告警集成

```logql
# 在 Loki ruler 中配置
groups:
- name: myapp_alerts
  rules:
  - alert: HighErrorRate
    expr: |
      sum(rate({job="myapp"} |= "error" [5m])) > 10
    for: 5m
    labels:
      severity: critical
```

---

## 十、最佳实践

1. **标签设计**：使用低基数标签（job / level / method / status）
2. **避免高基数**：不要把 user_id / request_id 作为标签
3. **结构化日志**：JSON / Logfmt（比纯文本好解析）
4. **采样率**：低重要性日志可采样（trace / info）
5. **保留策略**：按存储成本设置（hot / cold / archive）
6. **告警分级**：critical / warning / info
7. **关联追踪**：trace_id 关联 Prometheus + Loki + Tempo
8. **采集 Agent**：K8s 场景用 Alloy（替代 Promtail）

---

← [返回可观测性专题](../README.md) · 📅 2026-06-28