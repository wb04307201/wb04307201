# 数据库监控告警

> 数据库监控告警是生产环境稳定性的基石,核心目标是实时掌握 QPS、延迟、连接、复制延迟等关键指标,结合 Prometheus + Grafana + AlertManager 实现可视化与告警闭环。

> 最后更新: 2026-06-09

## 目录

- [一、监控体系架构](#一监控体系架构)
- [二、核心监控指标(Golden Signals)](#二核心监控指标golden-signals)
- [三、MySQL 监控](#三mysql-监控)
- [四、Redis 监控](#四redis-监控)
- [五、Prometheus + Grafana 实战](#五prometheus--grafana-实战)
- [六、告警规则设计](#六告警规则设计)
- [七、慢查询与日志分析](#七慢查询与日志分析)
- [八、生产事故案例](#八生产事故案例)

---

## 一、监控体系架构

### 1. 数据采集层次

```
┌────────────────────────────────────────────────┐
│                  业务层                         │
│  应用 QPS / 慢 SQL / 业务异常 / 错误率          │
└──────────────────┬─────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────┐
│                数据库层                         │
│  连接数 / QPS / 延迟 / 锁等待 / 复制延迟 / 缓存命中率 │
└──────────────────┬─────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────┐
│                 主机层                          │
│  CPU / 内存 / 磁盘 IO / 网络 / 系统负载         │
└──────────────────┬─────────────────────────────┘
                   ↓
                采集器(Exporter / Agent)
                   ↓
        ┌──────────┴──────────┐
        ↓                     ↓
   时间序列数据库         日志聚合
   (Prometheus)         (ELK / Loki)
        ↓                     ↓
   可视化(Grafana)        检索分析
        ↓
   告警(AlertManager)
        ↓
   通知(邮件 / 钉钉 / 飞书 / Slack)
```

### 2. 工具栈选型

| 层次 | 主流方案 |
|------|---------|
| **采集** | node_exporter、mysqld_exporter、redis_exporter、mongodb_exporter |
| **存储** | Prometheus(时序)、InfluxDB、Thanos(长期) |
| **可视化** | Grafana |
| **告警** | AlertManager、Grafana Alerts |
| **日志** | ELK(Elasticsearch + Logstash + Kibana)、Loki + Promtail |
| **APM** | SkyWalking、Pinpoint、Elastic APM |

---

## 二、核心监控指标(Golden Signals)

Google SRE 提出的 **4 大黄金指标**适用于所有服务,数据库同样适用:

| 指标 | 含义 | 数据库对应 |
|------|------|-----------|
| **Latency** | 响应时间 | SQL P50/P95/P99 延迟 |
| **Traffic** | 流量 | QPS、TPS、连接数 |
| **Errors** | 错误率 | SQL 错误数、超时数 |
| **Saturation** | 饱和度 | CPU、内存、磁盘 IO 使用率 |

### 数据库特有的 USE 方法(Brendan Gregg)

- **U**tilization:资源使用率(CPU、内存、磁盘、网络)
- **S**aturation:资源饱和度(队列长度、等待数)
- **E**rrors:错误事件(SQL 错误、连接失败、复制中断)

---

## 三、MySQL 监控

### 1. QPS / TPS

```sql
-- 总查询数
SHOW GLOBAL STATUS LIKE 'Questions';

-- 增删改执行数
SHOW GLOBAL STATUS LIKE 'Com_insert';
SHOW GLOBAL STATUS LIKE 'Com_update';
SHOW GLOBAL STATUS LIKE 'Com_delete';

-- 实时 QPS(两次采样差值)
SHOW GLOBAL STATUS LIKE 'Queries';
```

### 2. 关键性能指标(Performance Schema)

```sql
-- Top 10 慢 SQL
SELECT digest_text, count_star,
       sum_timer_wait/1e9 AS total_ms,
       avg_timer_wait/1e6 AS avg_ms
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC LIMIT 10;

-- 索引使用情况
SELECT * FROM sys.schema_index_statistics;

-- 表 I/O 热点
SELECT * FROM sys.io_global_by_file_by_latency;

-- 锁等待
SELECT * FROM sys.innodb_lock_waits;
```

### 3. 关键 SHOW STATUS 指标

| 指标 | 含义 | 告警阈值 |
|------|------|---------|
| `Threads_connected` | 当前连接数 | 接近 `max_connections` |
| `Threads_running` | 活跃线程数 | > 50 需关注 |
| `Slow_queries` | 慢查询累计 | 持续增长 |
| `Innodb_rows_read` | 读行数 | 性能基线对比 |
| `Innodb_buffer_pool_wait_free` | 缓冲池等待 | > 0 表示磁盘 I/O 瓶颈 |
| `Innodb_log_waits` | 日志等待 | > 0 表示 checkpoint 慢 |

### 4. 复制状态(主从架构)

```sql
SHOW SLAVE STATUS\G

-- 关键字段:
-- Seconds_Behind_Master: 复制延迟(秒)
-- Slave_IO_Running: IO 线程
-- Slave_SQL_Running: SQL 线程
-- Last_Error: 错误信息
```

> **MGR / Group Replication**:`SELECT * FROM performance_schema.replication_group_member_stats;`

### 5. mysqld_exporter 安装

```bash
# 1. 创建监控账号
CREATE USER 'exporter'@'%' IDENTIFIED BY 'P@ssw0rd' WITH MAX_USER_CONNECTIONS 3;
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'%';

# 2. 启动 exporter
mysqld_exporter \
  --mysqld.address=127.0.0.1:3306 \
  --mysqld.username=exporter \
  --mysqld.password=P@ssw0rd \
  --web.listen-address=:9104

# 3. Prometheus 抓取配置
# prometheus.yml
scrape_configs:
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql-exporter:9104']
```

### 6. MySQL Grafana 仪表盘

官方推荐仪表盘 ID:**7362**(Percona MySQL Overview,目前最主流)、**1516**(MySQL by Cloudflare)

关键面板:
- MySQL Uptime
- MySQL Connections (Threads_connected / max_connections)
- MySQL Queries per Second
- MySQL Slow Queries
- MySQL InnoDB Buffer Pool
- MySQL InnoDB I/O
- MySQL Replication Lag

---

## 四、Redis 监控

### 1. INFO 关键 sections

```bash
redis-cli INFO Memory
redis-cli INFO Stats
redis-cli INFO Replication
redis-cli INFO Keyspace
```

### 2. 关键指标

| 指标 | 含义 | 告警阈值 |
|------|------|---------|
| `used_memory` | 已用内存 | 接近 `maxmemory` |
| `used_memory_rss` | RSS 内存(实际占 OS) | - |
| `mem_fragmentation_ratio` | 内存碎片率 | > 1.5 或 < 1.0 |
| `connected_clients` | 客户端连接数 | > 5000 |
| `blocked_clients` | 阻塞客户端 | > 0 持续 5s |
| `instantaneous_ops_per_sec` | 实时 QPS | 基线对比 |
| `keyspace_hits` | 命中次数 | - |
| `keyspace_misses` | 未命中次数 | - |
| `latest_fork_usec` | 最近 fork 耗时 | > 1000ms |
| `rejected_connections` | 拒绝连接数 | > 0 |

### 3. 命中率计算

```promql
redis_keyspace_hit_rate = 
    rate(redis_keyspace_hits_total[5m]) / 
    (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))
```

> **健康基线**:命中率应 > 0.9,否则缓存设计有问题。

### 4. 慢查询

```bash
CONFIG SET slowlog-log-slower-than 10000  # 10ms
SLOWLOG GET 10
SLOWLOG LEN
```

### 5. 大 Key 检测

```bash
# Redis 4.0+
redis-cli --bigkeys

# 内存分析(详细)
redis-cli MEMORY USAGE mykey
```

### 6. redis_exporter 安装

```bash
redis_exporter \
  -redis.addr=redis://127.0.0.1:6379 \
  -web.listen-address=:9121
```

Grafana 仪表盘:**11835**(Redis 官方)

### 7. 集群监控

Cluster 模式下,额外关注:
- 每个 Master 节点的 `master_link_status`(集群总线)
- 槽位迁移状态(`cluster_slots_assigned` / `cluster_slots_ok`)
- 节点间 Gossip 延迟

---

## 五、Prometheus + Grafana 实战

### 1. Prometheus 完整配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

scrape_configs:
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql-exporter:9104']
        labels: { instance: 'mysql-master' }

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
        labels: { instance: 'redis-cluster' }

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 2. AlertManager 配置

```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'instance']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'ops-team'

receivers:
  - name: 'ops-team'
    webhook_configs:
      - url: 'https://oapi.dingtalk.com/robot/send?access_token=XXX'
        send_resolved: true
```

### 3. 告警分组与抑制

```yaml
routes:
  - match:
      severity: critical
    receiver: 'oncall'
  
  - match_re:
      alertname: '.*'
    group_by: [alertname, instance, severity]

inhibit_rules:
  # MySQL 宕机时,抑制 MySQL 的子告警
  - source_match:
      alertname: 'MySQLDown'
    target_match_re:
      alertname: 'MySQL.*'
    equal: ['instance']
```

---

## 六、告警规则设计

### 1. MySQL 告警规则(Prometheus 格式)

```yaml
# rules/mysql.yml
groups:
  - name: mysql_alerts
    rules:
      - alert: MySQLDown
        expr: mysql_up == 0
        for: 1m
        labels: { severity: critical }
        annotations:
          summary: "MySQL 实例 {{ $labels.instance }} 不可用"
          description: "已 1 分钟无法连接"

      - alert: MySQLHighConnections
        expr: >
          mysql_global_status_threads_connected /
          mysql_global_variables_max_connections > 0.8
        for: 5m
        labels: { severity: warning }
        annotations:
          summary: "MySQL 连接数使用率 > 80%"

      - alert: MySQLReplicationLag
        expr: mysql_slave_status_seconds_behind_master > 60
        for: 2m
        labels: { severity: warning }
        annotations:
          summary: "主从延迟 {{ $value }}s"

      - alert: MySQLSlowQueries
        expr: >
          rate(mysql_global_status_slow_queries[5m]) > 5
        for: 5m
        labels: { severity: warning }
        annotations:
          summary: "慢查询速率 {{ $value }} QPS"
```

### 2. Redis 告警规则

```yaml
groups:
  - name: redis_alerts
    rules:
      - alert: RedisDown
        expr: redis_up == 0
        for: 1m
        labels: { severity: critical }

      - alert: RedisMemoryHigh
        expr: >
          redis_memory_used_bytes / redis_memory_max_bytes > 0.8
        for: 5m
        labels: { severity: warning }
        annotations:
          summary: "Redis 内存使用率 > 80%"

      - alert: RedisHitRateLow
        expr: >
          rate(redis_keyspace_hits_total[5m]) /
          (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))
          < 0.9
        for: 10m
        labels: { severity: warning }
        annotations:
          summary: "Redis 命中率 < 90%"

      - alert: RedisRejectedConnections
        expr: redis_rejected_connections_total > 0
        for: 1m
        labels: { severity: critical }
```

### 3. 告警分级策略

| 级别 | 触发条件 | 通知方式 | 响应时间 |
|------|---------|---------|---------|
| **Critical** | 服务宕机、数据丢失风险 | 电话 + 短信 + 钉钉 @所有人 | 5 分钟 |
| **Warning** | 接近阈值、性能下降 | 钉钉群消息 | 30 分钟 |
| **Info** | 异常波动、需关注 | 邮件 / 钉钉普通消息 | 工作时间 |

---

## 七、慢查询与日志分析

### 1. MySQL 慢查询日志

```ini
# my.cnf
slow_query_log = 1
slow_query_log_file = /var/lib/mysql/slow.log
long_query_time = 2
log_slow_extra = FILE       # MySQL 8.0.14+
log_queries_not_using_indexes = 1
```

### 2. pt-query-digest 报告

```bash
pt-query-digest /var/lib/mysql/slow.log > daily_report.txt
```

报告内容:
- 总体统计(总查询、唯一查询、95%/99% 响应时间)
- Top 10 慢查询详情
- 各查询的扫描行数 / 返回行数

### 3. ELK 收集数据库日志

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    paths:
      - /var/lib/mysql/slow.log
      - /var/lib/mysql/error.log
    fields: { log_type: mysql }
    multiline.pattern: '^\d{4}-\d{2}-\d{2}'
    multiline.negate: true
    multiline.match: after

output.logstash:
  hosts: ["logstash:5044"]
```

Logstash 解析后入 Elasticsearch,Kibana 可视化检索。

---

## 八、生产事故案例

### 案例 1:慢 SQL 导致连接池打满

**现象**:应用 502,慢查询日志暴涨,数据库 QPS 暴增。

**排查**:
```sql
SHOW PROCESSLIST;  -- 发现大量"waiting for table metadata lock"
SELECT * FROM sys.processlist WHERE command = 'Query' AND time > 10;
```

**根因**:某条新上线的 SQL 全表扫描(`SELECT * FROM huge_table WHERE unindexed_col = 'x'`),单条执行 30s,占用连接池所有连接。

**修复**:
1. 紧急 kill 慢 SQL:`KILL <id>;`
2. 添加索引
3. 增加告警:慢查询速率 > 5/s 立即告警

### 案例 2:Redis 大 Key 导致集群故障

**现象**:Redis Cluster 单节点内存打满,触发流控,业务超时。

**排查**:
```bash
redis-cli --bigkeys  # 发现某 Hash 字段 5000万
INFO MEMORY          # mem_fragmentation_ratio = 1.8
```

**根因**:用户行为日志 Hash 持续追加,单 key 体积达 5GB,删除时阻塞主线程 5s+。

**修复**:
1. 立即 `DEBUG SLEEP 0` + `DEL` 拆分为小批量
2. 调整 `hash-max-ziplist-entries` 阈值
3. 上线大 Key 监控:对 1MB+ 的 key 报警

### 案例 3:主从延迟导致读旧数据

**现象**:用户支付成功后立即查询订单,显示"未支付"。

**排查**:
```sql
SHOW SLAVE STATUS;  -- Seconds_Behind_Master: 300s
```

**根因**:从库回放 SQL 慢(单条大事务 UPDATE 1 亿行)。

**修复**:
1. **短期**:关键业务强制读主库
2. **中期**:拆分大事务为小批次
3. **长期**:半同步复制 + 从库多线程回放(MySQL 5.7+ `slave_parallel_workers`)

---

## 相关章节

- [MySQL](../05-mysql/README.md) — 主从复制、参数调优
- [Redis](../07-redis/README.md) — 持久化、集群
- [数据库连接池](../09-connection-pool/README.md) — 连接池监控指标
- [数据迁移与同步](../10-data-migration/README.md) — Canal/Maxwell 监控
- [系统设计 · 可观测性](../../04.system-design/07-deployment/observability/README.md) — 系统全局监控

## 参考资料

- [Prometheus 官方文档](https://prometheus.io/docs/)
- [Grafana 官方仪表盘库](https://grafana.com/grafana/dashboards/)
- [Percona Monitoring Plugins](https://docs.percona.com/percona-monitoring-plugins/)
- [Google SRE Book - Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [mysqld_exporter GitHub](https://github.com/prometheus/mysqld_exporter)
- [redis_exporter GitHub](https://github.com/oliver006/redis_exporter)
- [USE 方法 - Brendan Gregg](http://www.brendangregg.com/usemethod.html)
