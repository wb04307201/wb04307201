<!--
question:
  id: 10.big-data-iceberg-acid
  topic: 10.big-data
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [10.big-data, Iceberg, ACID, 数据湖, Snapshot, Manifest, MVCC]
-->

# Iceberg 如何实现数据湖的 ACID 事务？

> 一句话定位：Iceberg 用 Snapshot + Manifest + MVCC 三层架构，让数据湖首次具备了真正的 ACID 事务——这是它碾压传统 Hive 表的核心竞争力。

> **系列定位**：经典大数据面试题（数据湖架构高频）。考察的不是"Iceberg 支持事务"，而是 **Snapshot 隔离机制** + **Manifest 文件组织** + **MVCC 并发控制** + **Merge-on-Read vs Copy-on-Write 策略选型**。

---

## 引子：数据湖的"脏读"噩梦

```text
某金融公司的风控数据湖（基于 Hive）：
- ETL Job A：正在写入今日交易数据（已写入 80%）
- 分析师 Job B：同时读取同一张表 → 读到不完整数据 → 生成错误风控报告
- ETL Job C：与 Job A 并发写入同一分区 → 两个 Job 互相覆盖文件 → 数据丢失
```

传统 Hive 表基于文件系统，天然不支持 ACID。**读操作可能读到写了一半的数据**（脏读），**并发写入可能互相覆盖**（丢失更新）。

Iceberg 的出现，第一次在数据湖层面解决了这些问题——不依赖 HDFS 的文件锁，而是靠**元数据层的 MVCC**。

---

## 一、核心原理

### 1.1 TL;DR：Iceberg 三层架构

| 层级 | 组件 | 作用 | 类比 |
|------|------|------|------|
| **元数据层** | Metadata File | 记录当前 Snapshot 指针 + Schema + 分区规则 | Git 的 HEAD |
| **快照层** | Snapshot | 某一时刻的完整数据视图（不可变） | Git 的 commit |
| **数据层** | Manifest File → Data File | Manifest 索引数据文件列表 + 统计信息 | Git 的 tree + blob |

### 1.2 Snapshot 隔离

```text
写入流程：
1. Writer 写入数据文件（Data File）到存储（HDFS / S3）
2. Writer 生成新的 Manifest File（记录新增/删除的数据文件）
3. Writer 生成新的 Metadata File（更新 Snapshot 指针）
4. Writer 通过原子操作（CAS）将表的 current-snapshot 指向新 Snapshot

读取流程：
1. Reader 读取当前 Metadata File → 获取 Snapshot 指针
2. Snapshot → 关联的 Manifest List → 所有 Manifest File
3. Manifest File → 统计信息过滤 → 只读取需要的 Data File
```

**关键特性**：Snapshot 一旦创建就**不可变**。Reader 始终读取一个一致的 Snapshot 视图，Writer 创建新 Snapshot 不影响正在读取的 Reader。

### 1.3 MVCC 并发控制

```text
Writer A 和 Writer B 并发写入：

Writer A: 写入 Data Files → 生成 Manifest → CAS 更新 Metadata
Writer B: 写入 Data Files → 生成 Manifest → CAS 更新 Metadata（冲突！）

Iceberg 的解决方式：
1. 乐观并发控制：Writer B 在提交时发现 Metadata 已被 Writer A 修改
2. 冲突检测：检查 Writer B 修改的分区是否与 Writer A 重叠
3. 无冲突 → 合并两个 Snapshot 的 Manifest 列表，重新提交
4. 有冲突 → 抛异常，Writer B 需要重试
```

### 1.4 Manifest File 结构

```text
Manifest File（Avro 格式）：
├── Manifest Entry 1:
│   ├── status: ADDED / EXISTING / DELETED
│   ├── data_file:
│   │   ├── file_path: s3://bucket/data/part-00000.parquet
│   │   ├── record_count: 50000
│   │   ├── file_size: 128MB
│   │   ├── column_sizes: {id: 4KB, name: 8KB, amount: 4KB}
│   │   ├── value_counts: {id: 50000, name: 50000}
│   │   ├── null_value_counts: {name: 120}
│   │   ├── lower_bounds: {id: 1, amount: 0.01}
│   │   └── upper_bounds: {id: 50000, amount: 9999.99}
├── Manifest Entry 2: ...
└── Manifest Entry N: ...
```

**统计信息**是 Iceberg 高性能的关键——查询时先过滤 Manifest Entry 的 min/max 统计，跳过不需要的数据文件（**Data Skipping**）。

---

## 二、详解：Merge-on-Read vs Copy-on-Write

### 2.1 两种写入策略对比

| 维度 | Copy-on-Write (COW) | Merge-on-Read (MOR) |
|------|--------------------|--------------------|
| **UPDATE/DELETE 时** | 重写整个数据文件 | 写入 Delete File（标记删除） |
| **写入延迟** | 高（需要拷贝全文件） | 低（只写变更标记） |
| **读取延迟** | 低（直接读，无需合并） | 较高（读取时合并 Delete File） |
| **适用场景** | 读多写少（OLAP 报表） | 写多读少（实时 CDC / 频繁更新） |
| **文件膨胀** | 大文件多 | Delete File 累积需定期 compaction |

### 2.2 Time Travel 查询

```sql
-- 查询历史 Snapshot（时间旅行）
SELECT * FROM orders FOR TIMESTAMP AS OF '2026-07-15 10:00:00';

-- 查询指定 Snapshot ID
SELECT * FROM orders FOR VERSION AS OF 1234567890;

-- 查看 Snapshot 历史
SELECT snapshot_id, committed_at, operation, summary
FROM orders.snapshots
ORDER BY committed_at DESC LIMIT 10;

-- 回滚到指定 Snapshot（数据不丢失，只是切换指针）
CALL system.rollback_to_snapshot('orders', 1234567890);
```

### 2.3 Schema Evolution 与 Partition Evolution

```sql
-- Schema 演进：加列、改类型、重命名列（不影响历史数据）
ALTER TABLE orders ADD COLUMN discount DECIMAL(5,2);
ALTER TABLE orders RENAME COLUMN amount TO total_amount;

-- 分区演进：改分区规则（不影响历史分区，新数据按新规则分区）
ALTER TABLE orders REPLACE PARTITION FIELD dt WITH days(ts);
-- 历史数据仍按 dt 分区，新写入数据按 days(ts) 分区
-- Iceberg 查询时自动处理两种分区规则
```

---

## 三、常见陷阱

### 陷阱 1：MOR 模式下 Delete File 堆积
- **真相**：Merge-on-Read 每次 UPDATE/DELETE 都产生 Delete File，但不会立即合并。长时间不 compaction 会导致 Delete File 累积成百上千个，**读取时需要逐个合并**，性能急剧下降。必须配置定期 compaction 任务。

### 陷阱 2：Time Travel 不等于数据不删
- **真相**：Iceberg 的 Snapshot 只是元数据指针。底层数据文件可能被 **expire_snapshots** 清理。`CALL system.expire_snapshots('orders', 7)` 会删除 7 天前的 Snapshot **及其独有数据文件**。Time Travel 能回溯的范围受限于保留策略。

### 陷阱 3：并发写入的冲突检测是分区级别
- **真相**：Iceberg 的冲突检测粒度是**分区**，不是行。Writer A 和 Writer B 同时修改同一个分区内的不同行，仍然会冲突。Writer B 需要重试整个提交。高并发场景下需要合理设计分区规则以减少冲突。

### 陷阱 4：小文件问题
- **真相**：流式写入（如 Flink 写 Iceberg）每次 Checkpoint 产生一个 Data File，频率高时产生大量小文件（几 MB 甚至几百 KB）。必须用 `rewriteDataFiles` 做 compaction 合并小文件，否则查询性能严重下降。

---

## 四、最佳实践

```text
Iceberg 使用决策树：
├── 写入模式
│   ├── 读多写少（日报/月报） → Copy-on-Write
│   └── 写多读少（CDC / 实时更新） → Merge-on-Read + 定期 compaction
├── 存储后端
│   ├── 云环境 → S3/ADLS + DynamoDB 做 Catalog
│   └── 本地 → HDFS + Hive Metastore 做 Catalog
├── 维护任务（必须定期执行）
│   ├── rewriteDataFiles：合并小文件（每天）
│   ├── expireSnapshots：清理过期 Snapshot（每周）
│   ├── removeOrphanFiles：清理孤立文件（每月）
│   └── rewriteManifests：合并 Manifest 文件（按需）
└── 分区策略
    ├── 时间分区：days(ts) 或 hours(ts)（按查询粒度）
    └── 组合分区：days(ts) + bucket(16, user_id)（高基数列分桶）
```

---

## 五、面试话术（90 秒版本）

> "Iceberg 实现 ACID 的核心是 **Snapshot 隔离 + MVCC 并发控制**。每次写入不修改现有数据文件，而是创建新的 Snapshot——包含新的 Manifest List 和 Metadata File。Reader 始终读取一个一致的 Snapshot 视图，Writer 通过 CAS 原子操作更新 Snapshot 指针，冲突时用乐观并发控制检测分区级别的冲突并重试。"
>
> "写入策略有 **Copy-on-Write** 和 **Merge-on-Read** 两种：COW 写入时重写整个数据文件，读取快但写入慢，适合读多写少；MOR 写入时只标记删除，读取时合并，适合写多读少但必须配合定期 compaction。"
>
> "Iceberg 的杀手级特性是 **Time Travel**（查询历史 Snapshot）和 **Schema/Partition Evolution**（修改 Schema 或分区规则不影响历史数据）。生产中必须定期执行 rewriteDataFiles、expireSnapshots、removeOrphanFiles 三个维护任务，否则小文件和 Delete File 堆积会严重影响性能。"

---

## 六、交叉引用

- **同栏目**：[`Hive 分区 vs 分桶`](../hive-partition-vs-bucket/README.md) — 传统分区与 Iceberg 演进分区的对比
- **同栏目**：[`Kafka Exactly-Once`](../kafka-exactly-once/README.md) — 流式写入 Iceberg 的事务保障
- **同栏目**：[`Flink Checkpoint vs Savepoint`](../flink-checkpoint-vs-savepoint/README.md) — Flink 写 Iceberg 时的 Checkpoint 联动
- **主模块**：[`03.database`](../../../03.database/README.md) — 传统数据库 ACID 事务基础

---

> 📅 2026-07-16 · 咬文嚼字 · 大数据 · 数据湖 · ⭐⭐⭐⭐⭐

← [返回: 咬文嚼字 · 大数据](../README.md)
