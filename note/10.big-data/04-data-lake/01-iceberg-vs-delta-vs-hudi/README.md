# Iceberg vs Delta Lake vs Apache Hudi：数据湖三剑客深度对比

> 一份按场景梳理的数据湖格式速查手册：从架构原理到生产选型的完整对比。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

Iceberg vs Delta Lake vs Apache Hudi：数据湖三剑客深度对比 本应该很简单，一份按场景梳理的数据湖格式速查手册：从架构原理到生产选型的完整对比

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、数据湖三剑客概览

| 格式 | 出生 | 主导方 | 核心理念 |
|------|------|--------|---------|
| **Apache Iceberg** | 2017 | Netflix → Apache | 隐藏分区 + ACID + 多引擎 |
| **Delta Lake** | 2019 | Databricks | Spark 生态 + ACID + 时间旅行 |
| **Apache Hudi** | 2017 | Uber → Apache | 增量更新 + 记录级 CDC |

---

## 二、为什么需要"数据湖三件套"？

传统 Hive 格式（Parquet / ORC）的痛点：
- ❌ 不支持 ACID（并发写会冲突）
- ❌ 不支持 schema 演进（改字段名很难）
- ❌ 不支持时间旅行（看不到历史版本）
- ❌ 不支持高效更新（必须重写整个分区）

**Iceberg / Delta / Hudi 解决了这些问题**，让数据湖具备数仓能力（Lakehouse）。

---

## 三、Apache Iceberg 详解

### 3.1 核心特性

- **隐藏分区**：用户写 `WHERE date >= '2025-01-01'`，Iceberg 自动转换
- **多引擎支持**：Spark / Flink / Trino / Hive / Dremio
- **ACID 事务**：基于快照隔离
- **Schema 演进**：增删改字段、字段重命名
- **时间旅行**：查任意历史快照

### 3.2 架构

```
Iceberg Table
├── Metadata（manifest list）
│   ├── Manifest 1（数据文件列表）
│   ├── Manifest 2
│   └── Snapshot 列表
└── Data Files（Parquet / ORC / Avro）
```

### 3.3 典型场景

- 跨引擎数据湖（Spark + Flink + Trino）
- 云原生数据湖（S3 + Iceberg）
- 实时数据仓库（Flink + Iceberg + Doris）

---

## 四、Delta Lake 详解

### 4.1 核心特性

- **ACID 事务**：基于 Optimistic Concurrency Control
- **时间旅行**：`SELECT * FROM table VERSION AS OF 10`
- **Schema 演进**：自动 schema 合并
- **CDF（Change Data Feed）**：捕获所有变更
- **深度集成 Spark**：Spark 生态首选

### 4.2 架构

```
Delta Table = Parquet Files + Delta Log
├── _delta_log/
│   ├── 00000000000000000000.json
│   ├── 00000000000000000001.json
│   └── ...
└── data files（Parquet）
```

### 4.3 典型场景

- Databricks 用户
- Spark 生态数仓
- ML 特征工程（Delta + MLflow）

---

## 五、Apache Hudi 详解

### 5.1 核心特性

- **记录级 CDC**：高效的增删改（upsert / delete）
- **Copy-on-Write（COW）**：写时复制
- **Merge-on-Read（MOR）**：读时合并
- **增量查询**：Hudi 独有的增量拉取

### 5.2 架构

```
Hudi Table
├── Timeline（时间轴）
├── File Groups（数据文件组）
├── File Slices（文件切片）
└── Index（索引）
```

### 5.3 典型场景

- **CDC 数据入湖**：MySQL Binlog → Hudi（记录级 upsert）
- **流批一体**：Kafka → Flink → Hudi（Hudi 主键合并）
- **Uber 起源**：Uber 出行数据用 Hudi 处理

---

## 六、12 维度深度对比

| 维度 | Iceberg | Delta Lake | Hudi |
|------|---------|-----------|------|
| **出生** | Netflix 2017 | Databricks 2019 | Uber 2017 |
| **社区** | Apache 顶级（CNCF）| Databricks 主控 + 开源 | Apache 顶级 |
| **多引擎** | ✅ Spark/Flink/Trino | ⚠️ Spark 为主 | ✅ Spark/Flink |
| **ACID** | ✅ | ✅ | ✅ |
| **Schema 演进** | ✅ 强 | ✅ 强 | ✅ 中 |
| **隐藏分区** | ✅ 首创 | ❌ 无 | ❌ 无 |
| **时间旅行** | ✅ | ✅ | ✅ |
| **CDC 友好** | ⚠️ 中 | ⚠️ 中 | ✅ 强（Copy-on-Write / Merge-on-Read） |
| **流式摄入** | ✅ Flink 集成 | ✅ Structured Streaming | ✅ Flink 集成 |
| **云原生** | ✅ S3/OSS/GCS | ✅ S3/ADLS/GCS | ✅ S3/OSS/GCS |
| **生态成熟度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **学习曲线** | 中 | 低（Spark 用户）| 中 |

---

## 七、生产选型决策

```
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

## 八、生产实战对比

### 8.1 Iceberg + Flink + Doris 实时数仓

```
Kafka → Flink（CDC）→ Iceberg（湖仓）→ Doris（查询）
   延迟：分钟级
   优势：流批一体、Schema 演进
```

### 8.2 Delta + Spark 离线数仓

```
S3 → Delta Lake → Spark SQL → BI
   优势：Spark 生态完整
   限制：跨引擎支持弱
```

### 8.3 Hudi + Flink CDC 入湖

```
MySQL Binlog → Flink CDC → Hudi（COW）
   优势：记录级 upsert，性能最佳
```

---

## 九、主流厂商选型

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

## 十、最佳实践

1. **优先 Iceberg**：跨引擎最灵活、云原生标准
2. **Hudi 适合 CDC 场景**：MySQL → 数据湖
3. **Delta 适合 Spark 团队**：生态最完整
4. **避免重复选型**：一旦选定，全公司统一（不要 A 团队 Iceberg，B 团队 Delta）
5. **小文件合并**：每天 / 每周定期 compaction
6. **监控**：元数据文件大小、snapshot 数量、文件数

---

← [返回 10.big-data 主目录](../../README.md) · 📅 2026-06-28