<!--
question:
  id: 10.big-data-hive-partition-vs-bucket
  topic: 10.big-data
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [10.big-data, Hive, 分区, 分桶, Partition, Bucket, 查询优化]
-->

# Hive 分区 vs 分桶怎么选？

> 一句话定位：分区是"按目录切蛋糕"，分桶是"按 hash 分文件"——选错了查询慢 10 倍，选对了 Join 直接走 Map-Side。

> **系列定位**：经典大数据面试题（Hive 存储优化高频）。考察的不是"两者都能加速查询"，而是 **Partition Pruning 原理** + **Bucket Map Join 条件** + **动态分区陷阱** + **小文件治理**。

---

## 引子：一个 SQL 扫了 500TB 数据

```text
某日志分析平台：
- 日志表按天分区，3 年积累了 1100 个分区，每个分区 500GB
- 新来的分析师写了一条 SQL：SELECT * FROM logs WHERE user_id = 12345
- 没有加分区过滤条件，Hive 全表扫描 550TB 数据
- 集群资源被占满，其他 Job 全部排队
```

这不是极端案例。Hive 的**分区裁剪（Partition Pruning）**是查询优化的第一道防线——**漏写分区条件 = 全表扫描**。

但分区不是万能的。当需要按 `user_id` 做 Join 时，分区帮不上忙，这时候需要**分桶（Bucket）**。

---

## 一、核心原理

### 1.1 TL;DR 对比表

| 维度 | 分区（Partition） | 分桶（Bucket） |
|------|------------------|---------------|
| **物理结构** | 目录级别（`/dt=2026-01-01/`） | 文件级别（`bucket_0000`, `bucket_0001`） |
| **划分依据** | 业务字段（日期、地区） | hash(key) % N |
| **主要目的** | 减少扫描范围（Partition Pruning） | 加速 Join（Bucket Map Join）+ 采样 |
| **数量建议** | 几十到几千（按天/月/地区） | 2 的幂次（16 / 32 / 64 / 128） |
| **动态生成** | 支持（动态分区） | 不支持（建表时固定） |
| **查询加速** | WHERE 条件裁剪 | JOIN + TABLESAMPLE 采样 |
| **典型字段** | `dt`（日期）、`region`（地区） | `user_id`、`order_id` |

### 1.2 分区裁剪（Partition Pruning）

```sql
-- 表结构：3 级分区
CREATE TABLE logs (
    user_id BIGINT, action STRING, duration INT
) PARTITIONED BY (dt STRING, region STRING, env STRING)
STORED AS ORC;

-- 物理目录结构
-- /user/hive/warehouse/logs/dt=2026-07-16/region=cn/env=prod/
-- /user/hive/warehouse/logs/dt=2026-07-16/region=us/env=prod/

-- ✅ Partition Pruning：只扫描 dt=2026-07-16 且 region=cn 的目录
SELECT * FROM logs WHERE dt = '2026-07-16' AND region = 'cn';

-- ❌ 全表扫描：缺少分区过滤条件
SELECT * FROM logs WHERE user_id = 12345;  -- 扫描所有分区！
```

### 1.3 分桶与 Bucket Map Join

```sql
-- 建表：按 user_id 分 64 个桶
CREATE TABLE orders (
    order_id BIGINT, user_id BIGINT, amount DECIMAL(10,2)
) PARTITIONED BY (dt STRING)
CLUSTERED BY (user_id) INTO 64 BUCKETS
STORED AS ORC;

CREATE TABLE users (
    user_id BIGINT, name STRING, level STRING
) CLUSTERED BY (user_id) INTO 64 BUCKETS
STORED AS ORC;

-- Bucket Map Join：两表按相同字段、相同桶数分桶
-- Hive 自动将相同桶号的文件配对，Map 端直接 Join
SET hive.optimize.bucketmapjoin = true;
SELECT o.*, u.name FROM orders o JOIN users u ON o.user_id = u.user_id;
```

---

## 二、详解

### 2.1 动态分区

```sql
-- 开启动态分区
SET hive.exec.dynamic.partition = true;
SET hive.exec.dynamic.partition.mode = nonstrict;
-- 限制动态分区数量（防止 OOM）
SET hive.exec.max.dynamic.partitions = 5000;
SET hive.exec.max.dynamic.partitions.pernode = 1000;

-- 动态分区插入：分区值由数据决定
INSERT OVERWRITE TABLE logs PARTITION (dt, region)
SELECT user_id, action, duration, dt, region
FROM raw_logs WHERE dt >= '2026-07-01';
```

### 2.2 ORDER BY vs SORT BY vs DISTRIBUTE BY

```sql
-- ORDER BY：全局排序，1 个 Reducer（数据量大时极慢）
SELECT * FROM orders ORDER BY amount DESC;  -- 单 Reducer

-- SORT BY：每个 Reducer 内排序（不保证全局有序）
SET mapreduce.job.reduces = 10;
SELECT * FROM orders SORT BY amount DESC;  -- 10 个 Reducer 各自排序

-- DISTRIBUTE BY + SORT BY：先按 key 分发到同一 Reducer，再排序
SELECT * FROM orders DISTRIBUTE BY user_id SORT BY amount DESC;
-- 同一 user_id 的数据在同一个 Reducer 中，按 amount 排序

-- CLUSTERED BY = DISTRIBUTE BY + SORT BY（相同字段时简写）
-- 建表时的 CLUSTERED BY (user_id) INTO 64 BUCKETS
-- 等价于 DISTRIBUTE BY user_id SORT BY user_id
```

### 2.3 小文件问题

```sql
-- 问题：动态分区 + 多 Reducer = 大量小文件
-- 500 个分区 × 100 个 Reducer = 最多 50000 个文件

-- 解决方案 1：合并小文件
SET hive.merge.mapfiles = true;
SET hive.merge.mapredfiles = true;
SET hive.merge.size.per.task = 256000000;  -- 256MB
SET hive.merge.smallfiles.avgsize = 128000000;  -- 128MB

-- 解决方案 2：减少 Reducer 数量
SET mapreduce.job.reduces = 10;  -- 而非让 Hive 自动决定

-- 解决方案 3：CombineHiveInputFormat
SET hive.input.format = org.apache.hadoop.hive.ql.io.CombineHiveInputFormat;
```

---

## 三、常见陷阱

### 陷阱 1：分区列选择不当
- **真相**：分区列的基数（cardinality）决定分区数量。用 `user_id` 做分区会产生百万个目录，NameNode 元数据爆炸。经验值：**分区数 < 5000**，基数高的列用分桶。

### 陷阱 2：分桶后数据不均匀
- **真相**：hash(user_id) % 64 理论上均匀，但如果 user_id 有大量 null 值或固定前缀，某些桶会特别大。需要先清洗数据再分桶。

### 陷阱 3：Bucket Map Join 的严格条件
- **真相**：两表必须用**相同字段**分桶，且桶数**相同或成倍数关系**。桶数不同（如 64 vs 32）时 Hive 不会走 Bucket Map Join，退化为普通 Reduce Join。

### 陷阱 4：动态分区 OOM
- **真相**：动态分区在 Reduce 端需要为每个分区维护一个文件写入器。分区数 × Reducer 数过多时，Reducer 内存溢出。必须设置 `hive.exec.max.dynamic.partitions.pernode` 限制。

---

## 四、最佳实践

```text
分区 vs 分桶选择决策树：
├── 查询总是按时间 / 地区过滤？
│   └── → 分区（Partition Pruning 直接跳过无关目录）
├── 需要按 user_id 做 Join？
│   └── → 分桶（Bucket Map Join 避免 Shuffle）
├── 既要分区又要分桶？
│   └── → 分区 + 分桶组合（先分区再在分区内分桶）
├── 需要随机采样？
│   └── → 分桶 + TABLESAMPLE BUCKET 1 OUT OF 64
└── 数据量 < 100GB？
    └── → 不分区不分桶（ORC/Parquet 自带列裁剪 + predicate pushdown）
```

---

## 五、面试话术（90 秒版本）

> "Hive 分区和分桶是两种不同层级的数据组织方式。**分区是目录级别**的，按业务字段（日期、地区）将数据放到不同子目录，核心收益是 **Partition Pruning**——WHERE 条件能直接跳过无关目录，大幅减少扫描量。**分桶是文件级别**的，按 hash(key) % N 将数据分到固定数量的文件中，核心收益是 **Bucket Map Join**——两表按相同字段、相同桶数分桶时，Map 端直接配对同桶号文件做 Join，完全避免 Shuffle。"
>
> "选型原则：基数低的列（日期、地区）做分区，基数高的列（user_id）做分桶。分区数控制在 5000 以内避免 NameNode 压力，桶数选 2 的幂次。两者可以组合使用——先按日期分区，再在分区内按 user_id 分桶。"
>
> "最常见的坑是漏写分区条件导致全表扫描、Bucket Map Join 条件不匹配退化为 Reduce Join、动态分区产生大量小文件。"

---

## 六、交叉引用

- **同栏目**：[`Spark Shuffle 优化`](../spark-shuffle-optimization/README.md) — Shuffle 优化与分桶的关系
- **同栏目**：[`Iceberg ACID`](../iceberg-acid/README.md) — 数据湖对分区/分桶的演进
- **主模块**：[`03.database`](../../../03.database/README.md) — 数据库索引与分区基础

---

> 📅 2026-07-16 · 咬文嚼字 · 大数据 · Hive 存储 · ⭐⭐⭐⭐

← [返回: 咬文嚼字 · 大数据](../README.md)
