<!--
module:
  parent: big-data
  slug: big-data/flink-vs-spark-streaming
  type: article
  category: 主模块子文章
  summary: Flink vs Spark Streaming——实时计算引擎深度对比
-->

# Flink vs Spark Streaming：实时计算引擎深度对比

> 一份按场景梳理的实时计算引擎速查手册：从架构原理到生产选型的完整对比。

---

## 模块导航
| 引擎 | 模型 | 延迟 | 吞吐 | 适用 |
|------|------|------|------|------|
| **Apache Flink** | 流优先（native streaming）| 毫秒级 | 高 | 实时风控 / 实时推荐 |
| **Spark Streaming** | 微批（micro-batch）| 秒级 | 极高 | 准实时报表 / 离线 + 实时统一 |
| **Kafka Streams** | 流优先（库）| 毫秒级 | 中 | 简单流处理（Java） |

### 1.1 学习路径

- 新人：从 Flink DataStream API 入手，掌握 Source → Transform → Sink
- 进阶：Flink SQL + Window + Watermark 处理乱序
- 实战：Kafka → Flink → Iceberg / Doris 实时数仓链路

---

## 知识脉络
```text
┌──────────────────────────────────────┐
│  Flink Cluster                        │
│  ┌────────────┐  ┌────────────┐     │
│  │ JobManager │  │ TaskManager│     │
│  │ 调度 + 检查点│  │ 任务执行     │     │
│  └────────────┘  └────────────┘     │
│         ↓                              │
│    Checkpoint（持久化状态）              │
└──────────────────────────────────────┘

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

---

## 速查要点
- **Flink**：流优先 + 事件时间 + Exactly-Once + RocksDB 状态后端
- **Spark Streaming**：早期 DStream 为微批（默认 batch interval 1 秒），新版 Structured Streaming 触发器可配置（默认 `micro-batch`，可切到 `continuous`）
- **Kafka Streams**：流优先库（轻量，无独立集群）

---

## 10 维度深度对比
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

## 生产选型决策
```text
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

## 生产实战
### 6.1 Flink Checkpoint 配置

```yaml
state:
  backend: rocksdb
  checkpoint:
    interval: 60s
    timeout: 300s
    min-pause-between: 30s
    storage: hdfs://namenode:9000/flink/checkpoints
```

### 6.2 Watermark（处理乱序）

```java
WatermarkStrategy
  .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
  .withTimestampAssigner((event, ts) -> event.getTimestamp());
```

### 6.3 Spark Structured Streaming

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

---

## 典型案例
**Flink 实时风控**：

```text
订单 → Kafka → Flink（CEP 引擎检测异常模式）→ 实时拦截
        ↓
   1. 检测 5 分钟内 5 笔订单 = 异常
   2. 自动冻结账户
   3. 通知风控人员
```

**Spark Streaming 实时数仓**：

```text
Kafka → Spark Structured Streaming → Delta Lake → BI
   延迟：30 秒（分钟级报表）
   吞吐：百万级/秒
```

---

## 最佳实践
| 实践 | 说明 |
|------|------|
| Flink 语言选型 | Java / Scala（性能最佳） |
| Spark 语言选型 | Python / SQL（易用性优先） |
| 状态后端 | RocksDB（TB 级状态首选） |
| Checkpoint 间隔 | 60-300 秒（不要太频繁） |
| 监控 | Flink UI / Spark UI + Prometheus Metrics |
| 灾备 | Savepoint（HDFS / S3） |

---

## 常见面试题
| 题目 | 核心考点 |
|------|---------|
| Flink 与 Spark Streaming 本质区别？ | 流式 vs 微批；延迟与吞吐 trade-off |
| Flink Exactly-Once 如何保证？ | Checkpoint + 两阶段提交 + WAL |
| Spark Structured Streaming vs DStream？ | 基于 Spark SQL vs RDD API |
| 何时选 Kafka Streams？ | 简单 Java 应用 + 无独立集群 |
| Flink Checkpoint 为什么用 RocksDB？ | TB 级状态 + 增量 checkpoint |

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 流式处理一定比微批快 | ✅ 高吞吐场景 Spark 微批可能更高效；延迟 vs 吞吐需权衡 |
| ❌ Flink 全面优于 Spark Streaming | ✅ 已有 Spark 集群 + 准实时需求 → Spark Streaming 更务实 |
| ❌ Exactly-Once 没有性能代价 | ✅ Checkpoint 间隔过短会显著降低吞吐量（60-300s 为宜） |
| ❌ RocksDB 状态后端总是最优 | ✅ 小状态（GB 级）Heap 后端延迟更低；RocksDB 优势在 TB 级 |
| ❌ 批流一体 = 同一套代码零改动 | ✅ API 统一但调优策略不同（批处理无需 Watermark / Checkpoint） |

---

## ⚙️ 参数配置速查表

### Flink 核心参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `state.backend` | rocksdb | 状态后端（TB 级状态首选） |
| `state.checkpoint.interval` | 60s-300s | Checkpoint 间隔（不要太频繁） |
| `state.checkpoint.timeout` | 300s | Checkpoint 超时时间 |
| `state.checkpoint.min-pause` | 30s | 两次 Checkpoint 最小间隔 |
| `execution.parallelism` | CPU 核心数 | 并行度（建议 = TaskManager 槽位数） |
| `taskmanager.memory.managed.size` | 4-16 GB | 托管内存（RocksDB 缓存） |
| `restart-strategy` | fixed-delay | 重启策略（生产推荐 fixed-delay） |
| `restart-strategy.fixed-delay.attempts` | 3 | 最大重启次数 |
| `watermark.idle-timeout` | 60s | 空闲数据源超时（避免 Watermark 停滞） |

### Spark Streaming 核心参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `spark.streaming.batchDuration` | 1s-10s | 微批间隔（影响延迟下限） |
| `spark.sql.streaming.trigger` | ProcessingTime(1s) | 触发器（continuous 可达毫秒级） |
| `spark.sql.streaming.checkpointLocation` | HDFS/S3 路径 | Checkpoint 位置（容错必需） |
| `spark.streaming.backpressure.enabled` | true | 背压机制（自动调节摄入速率） |
| `spark.sql.shuffle.partitions` | 200 | Shuffle 分区数（影响并行度） |
| `spark.executor.memory` | 4-16 GB | Executor 内存 |

---

## 与其他模块的关系
- **上游**：[03-realtime-compute](../)（实时计算总览）
- **下游**：被 [04 数据湖](../../04-data-lake/) / [05 OLAP](../../05-olap/) 消费
- **横向**：[02 Hadoop 生态](../../02-hadoop-ecosystem/) 离线批处理互补

---

## 📊 本节统计

| 维度 | 数字 |
|------|------|
| 引擎对比数 | 2（Flink / Spark Streaming）+ Kafka Streams 提及 |
| 10 维度对比项 | 10 |
| 选型决策问题 | 5（延迟 / 状态 / 团队 / 集群 / 数仓类型）|
| 实战配置案例 | 3（Checkpoint / Watermark / Structured Streaming） |
| 最佳实践条数 | 6 |
| 常见面试题数 | 5 |
| frontmatter 覆盖率 | 1 / 1 = 100% |
| 文末回链覆盖 | 1 / 1 = 100% |

---

← [返回实时计算总览](../) · ← [返回大数据总览](../../README.md)