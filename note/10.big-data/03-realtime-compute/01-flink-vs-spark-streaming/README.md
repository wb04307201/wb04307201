<!--
module:
  parent: big-data
  slug: big-data/flink-vs-spark-streaming
  type: article
  category: 主模块子文章
  summary: Flink vs Spark Streaming
-->

# Flink vs Spark Streaming：实时计算引擎深度对比

> 一份按场景梳理的实时计算引擎速查手册：从架构原理到生产选型的完整对比。

---
---

## 一、实时计算的两大流派

| 引擎 | 模型 | 延迟 | 吞吐 | 适用 |
|------|------|------|------|------|
| **Apache Flink** | 流优先（native streaming）| 毫秒级 | 高 | 实时风控 / 实时推荐 |
| **Spark Streaming** | 微批（micro-batch）| 秒级 | 极高 | 准实时报表 / 离线 + 实时统一 |
| **Kafka Streams** | 流优先（库）| 毫秒级 | 中 | 简单流处理（Java） |

---

## 二、Apache Flink 详解

### 2.1 核心特性

- **流优先**：每条数据都是 event（不是 micro-batch）
- **事件时间（Event Time）**：基于数据本身的时间（不是处理时间）
- **精确一次（Exactly-Once）**：通过 Checkpoint 保证
- **状态后端**：RocksDB / Heap，处理 TB 级状态

### 2.2 架构

```
┌──────────────────────────────────────┐
│  Flink Cluster                        │
│  ┌────────────┐  ┌────────────┐     │
│  │ JobManager │  │ TaskManager│     │
│  │ 调度 + 检查点│  │ 任务执行     │     │
│  └────────────┘  └────────────┘     │
│         ↓                              │
│    Checkpoint（持久化状态）              │
└──────────────────────────────────────┘
```

### 2.3 典型场景

- 实时风控（毫秒级响应）
- 实时推荐（行为 → 实时特征 → 推荐）
- 实时数仓（Kafka → Flink → Iceberg / Doris）

---

## 三、Spark Streaming 详解

### 3.1 核心特性

- **微批处理**：把流数据切成小批次（默认 1 秒）
- **结构化流（Structured Streaming）**：基于 Spark SQL
- **生态丰富**：与 Spark 批处理无缝整合
- **语言统一**：Scala / Python / Java / R

### 3.2 架构

```
┌──────────────────────────────────────┐
│  Spark Cluster                       │
│  ┌────────────┐  ┌────────────┐     │
│  │ Driver      │  │ Executor   │     │
│  │ 调度        │  │ 任务执行    │     │
│  └────────────┘  └────────────┘     │
│         ↓                              │
│  DStream / Structured Streaming       │
└──────────────────────────────────────┘
```

### 3.3 典型场景

- 准实时数据仓库（T+1 改为分钟级）
- 流批一体（Lambda 架构）
- ETL（Kafka → Spark → 数仓）

---

## 四、10 维度深度对比

| 维度 | Flink | Spark Streaming |
|------|-------|-----------------|
| **处理模型** | 流优先（native）| 微批（micro-batch）|
| **延迟** | 毫秒级（< 100ms）| 秒级（1-10s）|
| **吞吐** | 高（百万级/秒）| 极高（百万级/秒）|
| **状态管理** | 内置 RocksDB / Heap | 需 checkpoint 到外部存储 |
| **事件时间** | 强（Watermark） | 中（Structured Streaming） |
| **Exactly-Once** | ✅ 内置 | ✅ 仅 Structured Streaming |
| **批流一体** | ✅（流批统一 API）| ✅（天然支持） |
| **SQL 支持** | ✅ Flink SQL | ✅ Spark SQL |
| **机器学习** | ✅ Flink ML | ✅ MLlib（生态更强）|
| **运维成本** | 高 | 中 |

---

## 五、生产选型决策树

```
Q1: 延迟要求？
├── < 100ms → Flink
└── 1-10s → Spark Streaming 也可

Q2: 状态规模？
├── TB 级状态 → Flink（原生支持）
└── GB 级状态 → 都可

Q3: 团队技术栈？
├── Java 为主 → Flink / Kafka Streams
├── Python / Scala → Spark Streaming（PySpark）
└── 混合 → Flink SQL

Q4: 已有 Spark 集群？
├── 是 → Spark Streaming（避免新集群）
└── 否 → Flink（生产标准）

Q5: 实时数仓 / 准实时？
├── 准实时 → Spark Structured Streaming
└── 实时数仓 → Flink + Iceberg / Doris
```

---

## 六、Flink 生产实战

### 6.1 Checkpoint 配置

```yaml
state:
  backend: rocksdb
  checkpoint:
    interval: 60s                 # 每 60 秒 checkpoint
    timeout: 300s
    min-pause-between: 30s
    storage: hdfs://namenode:9000/flink/checkpoints
```

### 6.2 Watermark（处理乱序）

```java
// 允许 5 秒乱序
WatermarkStrategy
  .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
  .withTimestampAssigner((event, ts) -> event.getTimestamp());
```

### 6.3 Savepoint（手动备份）

```bash
# 触发 savepoint
flink savepoint <jobId> hdfs:///flink/savepoints

# 从 savepoint 恢复
flink run -s hdfs:///flink/savepoints/savepoint-xxx \
  my-job.jar
```

---

## 七、Spark Streaming 生产实战

### 7.1 Structured Streaming 示例

```python
stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "events") \
    .load()

result_df = stream_df \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .filter("data.action = 'purchase'") \
    .groupBy(window("data.timestamp", "5 minutes")) \
    .count()

result_df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/delta/checkpoints") \
    .start()
```

### 7.2 微批 vs 连续处理

```python
# 微批（默认）
.option("trigger", "10 seconds")

# 连续处理（实验性）
.option("trigger", "continuous")
.option("continuous-checkpoint-interval", "1 second")
```

---

## 八、典型案例

### 8.1 Flink：实时风控

```
订单 → Kafka → Flink（CEP 引擎检测异常模式）→ 实时拦截
        ↓
   1. 检测 5 分钟内 5 笔订单 = 异常
   2. 自动冻结账户
   3. 通知风控人员
```

### 8.2 Spark Streaming：实时数仓

```
Kafka → Spark Structured Streaming → Delta Lake → BI
   延迟：30 秒（分钟级报表）
   吞吐：百万级/秒
```

---

## 九、最佳实践

1. **Flink 选 Java / Scala**：性能最佳
2. **Spark 选 Python / SQL**：易用性优先
3. **状态后端选 RocksDB**：TB 级状态首选
4. **Checkpoint 间隔**：60-300 秒（不要太频繁）
5. **监控**：Flink UI / Spark UI + Prometheus Metrics
6. **灾备**：Savepoint（HDFS / S3）

---

← [返回 10.big-data 主目录](../../README.md) · 📅 2026-06-28