<!--
module:
  parent: split-hairs
  slug: split-hairs/big-data
  type: index
  category: 高频面试题
  summary: 大数据面试题 — Flink / Spark / Hive / Iceberg / Doris / Kafka
-->

# 大数据咬文嚼字

> 大数据高频面试题与深度剖析，覆盖 Flink / Spark / Hive / Iceberg / Doris / Kafka 六大核心组件。6 篇分实时计算 / 批处理 / 数据仓库 / 数据湖 / OLAP / 消息队列 6 组，覆盖 80% 大数据面试高频题。

---

## 文章清单（共 6 篇）

### 实时计算与流处理
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Flink Checkpoint vs Savepoint](flink-checkpoint-vs-savepoint/) | ⭐⭐⭐⭐ | 自动 vs 手动、格式兼容性、增量检查点、Exactly-Once 语义 |

### 批处理与 Shuffle
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Spark Shuffle 优化](spark-shuffle-optimization/) | ⭐⭐⭐⭐⭐ | 数据倾斜检测、加盐、AQE 自适应、Broadcast Join 阈值 |

### 数据仓库
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Hive 分区 vs 分桶](hive-partition-vs-bucket/) | ⭐⭐⭐⭐ | Partition Pruning、Bucket Map Join、动态分区、小文件问题 |

### 数据湖
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Iceberg ACID 事务](iceberg-acid/) | ⭐⭐⭐⭐⭐ | Snapshot 隔离、Manifest 文件、MVCC、Merge-on-Read vs Copy-on-Write |

### OLAP 引擎
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Doris vs ClickHouse](doris-vs-clickhouse/) | ⭐⭐⭐⭐ | 架构对比、Join 性能、实时导入、生态选型 |

### 消息队列
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Kafka Exactly-Once](kafka-exactly-once/) | ⭐⭐⭐⭐⭐ | 幂等 Producer、事务 API、Consumer Offset、Kafka Streams |

---

## 学习路径

1. **入门**（1 周）：Hive 分区 vs 分桶 + Doris vs ClickHouse 选型 + Flink Checkpoint vs Savepoint
2. **进阶**（2 周）：Spark Shuffle 优化 + Kafka Exactly-Once + Iceberg ACID
3. **冲刺面试**（1 周）：全部 6 篇的面试话术 + 交叉引用串联

## 相关章节

- 主模块：大数据相关知识分散在 [`03.database`](../../03.database/)（数据库）、[`04.system-design`](../../04.system-design/)（分布式系统）
- 相关面试题：[`03.database`](../03.database/)（MVCC / 事务隔离）/ [`04.system-design`](../04.system-design/)（分布式一致性）

← [返回咬文嚼字（高频面试题）](../README.md)
