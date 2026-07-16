<!--
question:
  id: 10.big-data-flink-checkpoint-vs-savepoint
  topic: 10.big-data
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [10.big-data, Flink, Checkpoint, Savepoint, 容错, 状态管理]
-->

# Flink Checkpoint vs Savepoint 有什么区别？

> 一句话定位：Checkpoint 是 Flink 的"自动保险"，Savepoint 是"手动存档"——搞混两者是生产事故的高发区。

> **系列定位**：经典大数据面试题（Flink 容错机制高频）。考察的不是"两者都能恢复状态"，而是 **触发方式差异** + **格式兼容性** + **增量策略** + **Exactly-Once 语义保障**。

---

## 引子：一次误操作引发的生产事故

```text
凌晨 2 点，运维小王："Job 挂了，我用 savepoint 恢复一下。"
执行：flink run -s savepoint-xxx.jar
结果：任务恢复了，但从 3 小时前的状态开始，丢了 3 小时的数据。
```

小王不知道的是：**Flink 的 Checkpoint 每 5 分钟自动执行一次**，但 Savepoint 是他昨天下午手动触发的。他用了一个过期的 Savepoint 而非最新的 Checkpoint 恢复任务。

这个场景暴露了 3 个关键问题：
1. Checkpoint 和 Savepoint 的**生命周期**完全不同
2. 两者的**格式兼容性**在不同版本间有差异
3. **增量 Checkpoint** 对状态后端的选择有强依赖

---

## 一、核心原理

### 1.1 TL;DR 对比表

| 维度 | Checkpoint | Savepoint |
|------|-----------|-----------|
| **触发方式** | 自动（周期性） | 手动（CLI / REST API） |
| **生命周期** | Flink 自动管理（保留策略可配） | 用户手动管理（需显式删除） |
| **主要用途** | 故障恢复（自动） | 版本升级 / 集群迁移 / A/B 测试 |
| **格式** | 内部格式（可能随版本变化） | 标准化格式（跨版本兼容） |
| **增量支持** | 支持（RocksDB 状态后端） | 不支持（始终全量） |
| **并发执行** | 可与 Savepoint 并发 | 默认阻塞 Checkpoint |
| **触发延迟** | 极低（周期性 barrier） | 较高（需 flush 所有算子） |

### 1.2 Checkpoint 的 Barrier 机制

```text
Source → barrier → Operator A → barrier → Operator B → barrier → Sink
         ↑                    ↑                    ↑
    barrier 对齐（Exactly-Once 关键）
```

- Flink 在数据流中插入 **barrier**（屏障），将数据流分成一个个"快照单元"
- **Exactly-Once 语义**：通过 barrier 对齐（barrier alignment）确保每个数据只被处理一次
- **At-Least-Once**：跳过 barrier 对齐，延迟更低但可能重复处理

### 1.3 Savepoint 的完整快照

Savepoint 会触发一次**完整的一致性快照**：
1. 向 JobManager 发送触发请求
2. JobManager 向所有 Source 算子发送 barrier
3. barrier 流经整个 DAG，每个算子将状态写入持久化存储
4. 所有算子确认后，生成 Savepoint 元数据文件

---

## 二、代码示例

### 2.1 配置 Checkpoint

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// 每 30 秒触发一次 Checkpoint
env.enableCheckpointing(30_000);

// 精确一次语义（默认）
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);

// Checkpoint 超时 10 分钟
env.getCheckpointConfig().setCheckpointTimeout(600_000);

// 最小间隔：两次 Checkpoint 之间至少 5 秒
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(5_000);

// 最大并发 Checkpoint 数
env.getCheckpointConfig().setMaxConcurrentCheckpoints(1);

// 任务取消时保留 Checkpoint（默认删除）
env.getCheckpointConfig().setExternalizedCheckpointCleanup(
    ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);

// 状态后端（RocksDB 支持增量 Checkpoint）
env.setStateBackend(new EmbeddedRocksDBStateBackend(true));  // true = 增量
```

### 2.2 触发 Savepoint

```bash
# 触发 Savepoint
flink savepoint :jobId /path/to/savepoints/

# 触发 Savepoint 并取消任务（原子操作）
flink cancel -s /path/to/savepoints/ :jobId

# 从 Savepoint 恢复
flink run -s /path/to/savepoints/savepoint-xxxxx myapp.jar

# 从 Checkpoint 恢复（路径不同）
flink run -s /path/to/checkpoints/checkpoint-xxxxx myapp.jar
```

### 2.3 增量 vs 全量 Checkpoint

```java
// RocksDB 增量 Checkpoint —— 只写入自上次以来的变更 SST 文件
// 优点：写入量小、速度快
// 缺点：恢复时需要合并多个增量快照
EmbeddedRocksDBStateBackend rocksDB = new EmbeddedRocksDBStateBackend(true);
env.setStateBackend(rocksDB);

// HashMapStateBackend —— 始终全量
// 优点：恢复速度快（直接加载）
// 缺点：状态大时 Checkpoint 耗时长
HashMapStateBackend hashMap = new HashMapStateBackend();
env.setStateBackend(hashMap);
```

---

## 三、常见陷阱

### 陷阱 1：用过期 Savepoint 恢复丢失数据
- **真相**：Savepoint 是手动触发的，不会自动更新。生产环境应优先用 Checkpoint 恢复，Savepoint 仅在版本升级 / 集群迁移时使用。

### 陷阱 2：Checkpoint 间隔设太短导致反压
- **真相**：Checkpoint 本身有开销（barrier 注入 + 状态持久化）。间隔太短（< 10 秒）在大状态场景下会导致 Checkpoint 来不及完成就被下一次触发，形成"Checkpoint 风暴"。建议根据状态大小设置为 30s-5min。

### 陷阱 3：忽略 barrier 对齐的性能影响
- **真相**：Exactly-Once 需要 barrier 对齐——先到达的 barrier 所在 channel 会被**阻塞**直到所有 channel 的 barrier 都到达。数据倾斜时，对齐等待时间可能极长，导致吞吐骤降。At-Least-Once 跳过对齐但允许重复。

### 陷阱 4：Savepoint 跨版本不兼容
- **真相**：Flink 官方承诺 Savepoint **跨小版本兼容**（1.14 → 1.15），但**跨大版本不保证**（1.x → 2.x）。升级前应阅读 Release Notes 的兼容性说明。

---

## 四、最佳实践

### 4.1 生产环境配置清单

```text
Checkpoint 策略
├── 间隔：30s - 5min（按状态大小调整）
├── 模式：EXACTLY_ONCE（金融/订单场景）或 AT_LEAST_ONCE（日志/指标场景）
├── 超时：10min（避免僵尸 Checkpoint）
├── 保留策略：RETAIN_ON_CANCELLATION（方便调试）
├── 状态后端：RocksDB + 增量（状态 > 1GB 时必选）
└── 存储：HDFS / S3（不要用本地磁盘）
```

### 4.2 版本升级流程

```bash
# 1. 触发 Savepoint 并优雅停止
flink cancel -s hdfs:///savepoints/upgrade-v2/ :jobId

# 2. 部署新版本 JAR
# 3. 从 Savepoint 恢复
flink run -s hdfs:///savepoints/upgrade-v2/savepoint-xxxxx myapp-v2.jar
```

### 4.3 监控告警

| 指标 | 告警阈值 | 含义 |
|------|---------|------|
| `lastCheckpointDuration` | > 60s | Checkpoint 耗时过长 |
| `lastCheckpointSize` | > 10GB | 状态膨胀 |
| `lastCheckpointExternalPath` | 为空 | Checkpoint 未持久化 |
| `failedCheckpoints` | > 3 次/小时 | Checkpoint 持续失败 |

---

## 五、面试话术（90 秒版本）

> "Flink 的 Checkpoint 和 Savepoint 都是基于 Chandy-Lamport 算法的一致性快照，核心区别在于**生命周期**和**使用场景**。"
>
> "Checkpoint 是**自动触发**的周期性快照，由 Flink 内部管理生命周期，主要用于**故障自动恢复**。它通过 barrier 对齐实现 Exactly-Once 语义，支持增量模式（RocksDB 状态后端），只写入变更的 SST 文件。"
>
> "Savepoint 是**手动触发**的完整快照，生命周期由用户管理。主要用于**版本升级、集群迁移、A/B 测试**等需要人工干预的场景。Savepoint 使用标准化格式，跨小版本兼容，但始终是**全量快照**。"
>
> "生产中常见的坑是：用过期 Savepoint 恢复丢数据、Checkpoint 间隔太短导致反压、Exactly-Once 的 barrier 对齐在数据倾斜时性能骤降。建议 Checkpoint 间隔 30s-5min，状态大时用 RocksDB 增量，版本升级时用 Savepoint。"

---

## 六、交叉引用

- **同栏目**：[`Kafka Exactly-Once`](../kafka-exactly-once/README.md) — 端到端 Exactly-Once 需要 Flink + Kafka 联动
- **同栏目**：[`Spark Shuffle 优化`](../spark-shuffle-optimization/README.md) — 批处理场景的容错对比
- **主模块**：[`03.database`](../../../03.database/README.md) — 数据库事务与 ACID 基础

---

> 📅 2026-07-16 · 咬文嚼字 · 大数据 · Flink 容错 · ⭐⭐⭐⭐

← [返回: 咬文嚼字 · 大数据](../README.md)
