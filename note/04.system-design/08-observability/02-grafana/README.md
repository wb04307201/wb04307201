# Grafana · 可视化与仪表盘实战

> 一份按场景梳理的 Grafana 速查手册：从基础仪表盘到企业级可视化平台的完整实战。

---

## 一、Grafana 简介

Grafana 是开源的可视化与监控平台，支持 30+ 数据源（Prometheus / Loki / Elasticsearch / InfluxDB 等），是企业级仪表盘的事实标准。

### 1.1 核心特性

- **多数据源**：Prometheus / Loki / Tempo / Elasticsearch / CloudWatch
- **丰富的可视化**：Graph / Gauge / Table / Heatmap / Geomap
- **告警集成**：Alertmanager / Slack / Webhook / 钉钉 / 飞书
- **权限管理**：组织 / 团队 / 用户 / 角色
- **模板变量**：交互式仪表盘（如下拉筛选）
- **告警 + 注解**：标注发布 / 事故时间点

---

## 二、Grafana 核心架构

```
┌─────────────────────────────────────────────────┐
│  Grafana Server                                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐     │
│  │ DataSource │ │ Dashboard  │ │ Alerting   │     │
│  │ Manager    │ │ Engine     │ │ Engine     │     │
│  └────────────┘ └────────────┘ └────────────┘     │
│         ↓              ↓              ↓            │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│   │Prometheus│  │Dashboard  │  │ Slack    │         │
│   │ / Loki   │  │ / Folder │  │ / Alert  │         │
│   └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────┘
```

---

## 三、安装与配置

### 3.1 Docker 安装

```bash
docker run -d \
  --name=grafana \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana:latest
```

### 3.2 K8s Helm 安装

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set persistence.enabled=true \
  --set adminPassword=myStrongPassword
```

---

## 四、添加数据源

### 4.1 Prometheus 数据源

```
Configuration → Data Sources → Add data source
- Type: Prometheus
- URL: http://prometheus:9090
- Access: Server (default)
```

### 4.2 Loki 数据源（日志）

```
- Type: Loki
- URL: http://loki:3100
```

### 4.3 Tempo 数据源（链路追踪）

```
- Type: Tempo
- URL: http://tempo:3100
```

### 4.4 多个数据源

一个 Dashboard 可以用多个数据源（如 Prometheus 指标 + Loki 日志 + Tempo 追踪）。

---

## 五、面板类型（10+ 种可视化）

| 面板 | 适用场景 |
|------|---------|
| **Time series** | 指标趋势（CPU / 内存 / QPS）|
| **Stat** | 当前数值（大字号数字）|
| **Gauge** | 阈值告警（如磁盘使用率 80%）|
| **Bar chart** | 分类对比 |
| **Pie chart** | 占比 |
| **Table** | 详细列表（Top N）|
| **Heatmap** | 分布（请求延迟分布）|
| **Heatmap (new)** | 更强大 |
| **Geomap** | 地理数据 |
| **Logs** | 日志（来自 Loki / ES）|
| **Trace** | 链路追踪（来自 Tempo / Jaeger）|
| **Text** | Markdown 文档 |

---

## 六、模板变量（交互式仪表盘）

```promql
# 变量定义（Variables）
- $job（多选下拉）：所有 job 标签
- $instance：所有 instance
- $interval：时间范围

# 面板中使用变量
rate(http_requests_total{job="$job", instance=~"$instance"}[$interval])
```

### 6.1 变量类型

| 类型 | 来源 | 示例 |
|------|------|------|
| **Query** | 数据源查询 | `label_values(http_requests_total, job)` |
| **Custom** | 手动输入 | `dev, staging, prod` |
| **Interval** | 时间间隔 | `1m, 5m, 1h` |
| **Datasource** | 数据源切换 | `Prometheus, Loki` |
| **Constant** | 常量 | `production` |

### 6.2 变量级联

```
$datacenter（北京 / 上海 / 广州）
  → $cluster（根据 $datacenter 过滤）
    → $instance（根据 $cluster 过滤）
```

---

## 七、典型 Dashboard 设计

### 7.1 4 大黄金 Dashboard

| Dashboard | 内容 |
|-----------|------|
| **系统总览** | CPU / 内存 / 磁盘 / 网络 全局 |
| **应用监控** | QPS / 延迟 / 错误率（USE / RED）|
| **K8s 集群** | Pod 数 / Node 数 / 资源利用率 |
| **业务监控** | DAU / 订单 / GMV / 转化率 |

### 7.2 USE 方法（系统性能）

- **U**tilization（利用率）：CPU % / 内存 %
- **S**aturation（饱和度）：队列长度
- **E**rrors（错误）：错误事件数

### 7.3 RED 方法（服务性能）

- **R**ate（速率）：每秒请求数
- **E**rrors（错误）：错误率
- **D**uration（延迟）：P50 / P99 延迟

---

## 八、Dashboard 模板（可导入）

### 8.1 官方 Dashboard

- Grafana 官方：[grafana.com/grafana/dashboards](https://grafana.com/grafana/dashboards)
- K8s 集群：Dashboard ID 315
- JVM 应用：Dashboard ID 4701
- Node Exporter：Dashboard ID 1860
- MySQL：Dashboard ID 7362

### 8.2 导入方式

```
Dashboard → Import → 输入 Dashboard ID → Load
```

---

## 九、Grafana 告警

### 9.1 配置告警（统一告警）

```
Alerting → Alert rules → New alert rule
- Query: sum(rate(http_requests_total{status="500"}[5m]))
- Condition: IS ABOVE 10
- Evaluate every: 1m
- For: 5m
```

### 9.2 通知渠道

| 渠道 | 适用 |
|------|------|
| **Slack / 钉钉 / 飞书** | 团队即时通知 |
| **Email** | 传统邮件 |
| **PagerDuty / OpsGenie** | 值班告警 |
| **Webhook** | 自定义集成 |
| **Telegram / Discord** | 开发者社区 |

---

## 十、权限与组织

### 10.1 多租户架构

```
Organization（组织）
├── Team A（团队）
│   ├── Folder 1（文件夹）
│   │   ├── Dashboard 1
│   │   └── Dashboard 2
│   └── Folder 2
└── Team B
```

### 10.2 角色权限

| 角色 | 权限 |
|------|------|
| **Admin** | 全部权限 |
| **Editor** | 编辑 Dashboard / 数据源 |
| **Viewer** | 只读 |

---

## 十一、最佳实践

1. **统一 Dashboard 规范**：所有 Dashboard 加标签 / 描述
2. **变量命名一致**：`$job` / `$instance` / `$interval`
3. **告警分级**：critical / warning / info
4. **使用 Annotations**：标注发布 / 事故时间点
5. **模板化**：常用 Dashboard 做成模板导出
6. **告警抑制**：重复告警合并，避免告警风暴
7. **权限最小化**：团队只看自己负责的 Dashboard
8. **SLO 仪表盘**：把"用户感知"指标（SLO）放最显眼位置

---

← [返回可观测性专题](../README.md) · 📅 2026-06-28