<!--
module:
  parent: big-data
  slug: big-data/iceberg-vs-delta-vs-hudi
  type: article
  category: 主模块子文章
  summary: Iceberg vs Delta Lake vs Hudi——数据湖三剑客深度对比
-->

# Iceberg vs Delta Lake vs Apache Hudi：数据湖三剑客深度对比

> 一份按场景梳理的数据湖格式速查手册：从架构原理到生产选型的完整对比。

---

## 1. 模块导航

| 格式 | 出生 | 主导方 | 核心理念 |
|------|------|--------|---------|
| **Apache Iceberg** | 2017 | Netflix → Apache | 隐藏分区 + ACID + 多引擎 |
| **Delta Lake** | 2019 | Databricks | Spark 生态 + ACID + 时间旅行 |
| **Apache Hudi** | 2017 | Uber → Apache | 增量更新 + 记录级 CDC |

### 1.1 学习路径

- 新人：从 Iceberg 入手，理解隐藏分区 + 多引擎支持
- 进阶：Hudi COW / MOR 表类型与索引选择
- 实战：S3 + Iceberg + Spark + Trino 端到端数据湖

---

## 2. 为什么需要数据湖三件套？

传统 Hive 格式（Parquet / ORC）的痛点：

- 不支持 ACID（并发写会冲突）
- 不支持 schema 演进（改字段名很难）
- 不支持时间旅行（看不到历史版本）
- 不支持高效更新（必须重写整个分区）

**Iceberg / Delta / Hudi 解决了这些问题**，让数据湖具备数仓能力（Lakehouse）。

---

## 3. Apache Iceberg 详解

### 3.1 核心特性

- **隐藏分区**：用户写 `WHERE date >= '2025-01-01'`，Iceberg 自动转换
- **多引擎支持**：Spark / Flink / Trino / Hive / Dremio
- **ACID 事务**：基于快照隔离
- **Schema 演进**：增删改字段、字段重命名
- **时间旅行**：查任意历史快照

### 3.2 架构

```text
Iceberg Table
├── Metadata（manifest list）
│   ├── Manifest 1（数据文件列表）
│   ├── Manifest 2
│   └── Snapshot 列表
└── Data Files（Parquet / ORC / Avro）
```

---

## 4. Delta Lake 详解

### 4.1 核心特性

- **ACID 事务**：基于 Optimistic Concurrency Control
- **时间旅行**：`SELECT * FROM table VERSION AS OF 10`
- **Schema 演进**：自动 schema 合并
- **CDF（Change Data Feed）**：捕获所有变更
- **深度集成 Spark**：Spark 生态首选

### 4.2 架构

```text
Delta Table = Parquet Files + Delta Log
├── _delta_log/
│   ├── 00000000000000000000.json
│   ├── 00000000000000000001.json
│   └── ...
└── data files（Parquet）
```

---

## 5. Apache Hudi 详解

### 5.1 核心特性

- **记录级 CDC**：高效的增删改（upsert / delete）
- **Copy-on-Write（COW）**：写时复制
- **Merge-on-Read（MOR）**：读时合并
- **增量查询**：Hudi 独有的增量拉取

### 5.2 架构

```text
Hudi Table
├── Timeline（时间轴）
├── File Groups（数据文件组）
├── File Slices（文件切片）
└── Index（索引）
```

---

## 6. 12 维度深度对比

| 维度 | Iceberg | Delta Lake | Hudi |
|------|---------|-----------|------|
| **出生** | Netflix 2017 | Databricks 2019 | Uber 2017 |
| **社区** | Apache 软件基金会顶级项目 | Databricks 主控 + 开源 | Apache 软件基金会顶级项目 |
| **多引擎** | ✅ Spark/Flink/Trino | ⚠️ Spark 为主 | ✅ Spark/Flink |
| **ACID** | ✅ | ✅ | ✅ |
| **Schema 演进** | ✅ 强 | ✅ 强 | ✅ 中 |
| **隐藏分区** | ✅ 首创 | ❌ 无 | ❌ 无 |
| **时间旅行** | ✅ | ✅ | ✅ |
| **CDC 友好** | ⚠️ 中 | ⚠️ 中 | ✅ 强（COW / MOR） |
| **流式摄入** | ✅ Flink 集成 | ✅ Structured Streaming | ✅ Flink 集成 |
| **云原生** | ✅ S3/OSS/GCS | ✅ S3/ADLS/GCS | ✅ S3/OSS/GCS |
| **生态成熟度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **学习曲线** | 中 | 低（Spark 用户）| 中 |

---

## 7. 生产选型决策

```text
Q1: 主要引擎是？
├── Spark 为主 + Databricks → Delta Lake
├── Flink 为主 / 跨引擎 → Iceberg
└── CDC 为主（MySQL → 数据湖）→ Hudi

Q2: 团队背景？
├── 已有 Spark → Delta / Iceberg
├── 已有 Flink → Iceberg / Hudi
└── 多团队 → Iceberg（最中立）

Q3: 业务场景？
├── 准实时数仓（小时级）→ 都可
├── 实时数仓（分钟级）→ Iceberg + Flink
└── CDC 入湖 → Hudi（最强）

Q4: 云厂商绑定？
├── AWS + Databricks → Delta
├── 阿里云 / OSS → Iceberg
└── 多云 → Iceberg
```

---

## 8. 生产实战对比

**Iceberg + Flink + Doris 实时数仓**：

```text
Kafka → Flink（CDC）→ Iceberg（湖仓）→ Doris（查询）
   延迟：分钟级
   优势：流批一体、Schema 演进
```

**Delta + Spark 离线数仓**：

```text
S3 → Delta Lake → Spark SQL → BI
   优势：Spark 生态完整
   限制：跨引擎支持弱
```

**Hudi + Flink CDC 入湖**：

```text
MySQL Binlog → Flink CDC → Hudi（COW）
   优势：记录级 upsert，性能最佳
```

---

## 9. 主流厂商选型

| 厂商 | 推荐 |
|------|------|
| **Netflix** | Iceberg（自家出品）|
| **Uber** | Hudi（自家出品）|
| **Databricks** | Delta Lake（自家出品）|
| **阿里云** | Iceberg + Paimon（湖仓一体）|
| **腾讯云** | Iceberg |
| **AWS** | Delta Lake / Iceberg（S3） |
| **Azure** | Delta Lake（ADLS）|
| **Snowflake** | Iceberg 集成 |

---

## 10. 最佳实践

| 实践 | 说明 |
|------|------|
| 优先 Iceberg | 跨引擎最灵活、云原生标准 |
| Hudi 适合 CDC | MySQL → 数据湖 |
| Delta 适合 Spark | 团队生态最完整 |
| 避免重复选型 | 一旦选定全公司统一（不要 A 团队 Iceberg、B 团队 Delta） |
| 小文件合并 | 每天/每周定期 compaction |
| 监控 | 元数据文件大小 / snapshot 数量 / 文件数 |

---

## 11. 常见面试题

| 题目 | 核心考点 |
|------|---------|
| 三种数据湖格式核心差异？ | 多引擎 / CDC / Spark 生态 |
| Iceberg 隐藏分区原理？ | partition transform 不依赖目录名 |
| COW vs MOR 区别？ | 写时合并 vs 读时合并；性能特征 |
| Delta Lake 为何强绑定 Spark？ | 深度集成 + 事务日志 + Databricks 生态 |
| Hudi 为何适合 CDC？ | 记录级 upsert + 索引 |
| 何时不用 Iceberg？ | 已有 Databricks 全栈 + 团队仅用 Spark |

---

## 12. 与其他模块的关系

- **上游**：[04-data-lake](../)（数据湖总览）
- **下游**：被 [05 OLAP](../../05-olap/) / [03 实时计算](../../03-realtime-compute/) 消费
- **横向**：[01 数仓架构](../../01-data-warehouse/) 湖仓一体范式

---

## 📊 本节统计

| 维度 | 数字 |
|------|------|
| 数据湖格式数 | 3（Iceberg / Delta / Hudi）|
| 12 维度对比项 | 12 |
| 选型决策问题 | 4（引擎 / 团队 / 场景 / 云厂商） |
| 厂商选型表 | 8（Netflix / Uber / Databricks / 阿里 / 腾讯 / AWS / Azure / Snowflake）|
| 实战案例数 | 3（Iceberg + Flink + Doris / Delta + Spark / Hudi + Flink CDC）|
| 最佳实践条数 | 6 |
| 常见面试题数 | 6 |
| frontmatter 覆盖率 | 1 / 1 = 100% |
| 文末回链覆盖 | 1 / 1 = 100% |

---

← [返回数据湖总览](../) · ← [返回大数据总览](../../README.md)