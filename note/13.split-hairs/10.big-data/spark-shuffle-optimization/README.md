<!--
question:
  id: 10.big-data-spark-shuffle-optimization
  topic: 10.big-data
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 性能对比
  tags: [10.big-data, Spark, Shuffle, 数据倾斜, AQE, Broadcast Join]
-->

# Spark Shuffle 优化：数据倾斜怎么解？

> 一句话定位：Shuffle 是 Spark 性能瓶颈的万恶之源，数据倾斜让 99% 的 Task 在等 1% 的 Task——这是大数据面试的"必考题"。

> **系列定位**：经典大数据面试题（Spark 性能优化高频）。考察的不是"Shuffle 很慢"，而是 **Shuffle 机制理解** + **倾斜检测手段** + **多种解决方案的适用边界** + **AQE 自适应优化**。

---

## 引子：一个跑了 8 小时的 Job

```text
某电商平台的"每日销售报表"Spark Job：
- 总数据量：50 亿条，200 个 Partition
- 199 个 Task 在 5 分钟内完成
- 最后 1 个 Task 跑了 8 小时还没结束
- 原因：某个商家 ID 占了 30% 的数据（大促期间的超级大卖家）
```

这不是段子，这是真实生产场景。数据倾斜让 Spark 的并行计算退化为串行——**整个 Job 的速度取决于最慢的那个 Task**。

更隐蔽的是：倾斜不一定是数据问题，也可能是 **key 的 hash 分布不均匀**（大量 null / 空值 / 默认值）。

---

## 一、核心原理

### 1.1 TL;DR：Shuffle 两种机制对比

| 维度 | Hash Shuffle（已淘汰） | Sort Shuffle（默认） |
|------|----------------------|---------------------|
| **文件数** | M × R（M 个 map，R 个 reduce） | M 个（每个 map 一个合并文件） |
| **排序** | 不排序 | 按 partition id 排序后写入 |
| **内存** | 需要同时打开 R 个文件 | 顺序写入，内存友好 |
| **适用场景** | Spark < 1.2 | Spark >= 1.2（默认） |

### 1.2 Shuffle 的核心流程

```text
Map 端：
  数据 → 按 key 的 hash 分配到 R 个 bucket → 溢写磁盘 → merge 成一个文件
                                                    ↓
                                              + .index 索引文件

Reduce 端：
  读取属于自己 partition 的数据块 → 反序列化 → 聚合/排序 → 输出
```

**性能瓶颈**：磁盘 IO + 网络传输 + 序列化/反序列化 + 数据压缩

### 1.3 数据倾斜的本质

```text
正常分布：每个 partition ≈ 25M 条数据 → Task 耗时均匀
倾斜分布：partition-0 = 15 亿条，partition-1~199 ≈ 500 万条 → 1 个 Task 耗时 300 倍
```

---

## 二、详解：6 种解决方案

### 2.1 方案一：Broadcast Join（小表场景首选）

```scala
// 当小表 < 10MB（默认阈值 spark.sql.autoBroadcastJoinThreshold）
// Spark 自动将小表广播到每个 Executor，完全避免 Shuffle

val bigTable = spark.read.parquet("hdfs:///orders")    // 50 亿条
val smallTable = spark.read.parquet("hdfs:///users")   // 100 万条

// 自动触发 Broadcast Join（无需手动）
bigTable.join(smallTable, "user_id")

// 手动强制 Broadcast
import org.apache.spark.sql.functions.broadcast
bigTable.join(broadcast(smallTable), "user_id")

// 调大阈值（适合 100MB 以内的小表）
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 100 * 1024 * 1024)
```

### 2.2 方案二：加盐（Salting）— 打散热点 Key

```scala
// 原始：join on merchant_id，某个 merchant_id 占 30% 数据
val orders = spark.read.parquet("orders")
val merchants = spark.read.parquet("merchants")

// ❌ 直接 Join → 数据倾斜
orders.join(merchants, "merchant_id")

// ✅ 加盐：将热点 key 拆成 N 个子 key
import org.apache.spark.sql.functions._

val N = 100  // 盐的范围
// 大表：merchant_id → merchant_id + "_" + random(0, N)
val saltedOrders = orders.withColumn(
  "salted_key",
  concat(col("merchant_id"), lit("_"), (rand() * N).cast("int"))
)

// 小表：explode 成 N 份，merchant_id → merchant_id + "_" + 0..N
val explodedMerchants = merchants
  .withColumn("salt", explode((0 until N).toArray))
  .withColumn("salted_key", concat(col("merchant_id"), lit("_"), col("salt")))

saltedOrders.join(explodedMerchants, "salted_key")
```

### 2.3 方案三：AQE 自适应倾斜连接（Spark 3.0+）

```scala
// 开启 AQE（Adaptive Query Execution）
spark.conf.set("spark.sql.adaptive.enabled", true)
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", true)

// AQE 自动检测倾斜并拆分大 Task
// 参数：
//   skewPartitionFactor = 5  （某 partition 大小 > 中位数 × 5 视为倾斜）
//   skewPartitionThreshold = 256MB  （且 > 256MB）
spark.conf.set("spark.sql.adaptive.skewJoin.skewPartitionFactor", 5)
spark.conf.set("spark.sql.adaptive.skewJoin.skewPartitionThreshold", "256MB")

// 开启后无需手动加盐，AQE 自动将倾斜 partition 拆成多个子 Task
orders.join(merchants, "merchant_id")  // AQE 自动优化
```

### 2.4 方案四：两阶段聚合（Partial Aggregation）

```scala
// 场景：group by 聚合倾斜
// ❌ 直接聚合
orders.groupBy("merchant_id").agg(sum("amount"))

// ✅ 两阶段：先加盐局部聚合，再去盐全局聚合
val salted = orders
  .withColumn("salt", (rand() * 100).cast("int"))
  .groupBy("merchant_id", "salt")
  .agg(sum("amount").as("partial_sum"))

val result = salted
  .groupBy("merchant_id")
  .agg(sum("partial_sum").as("total_amount"))
```

### 2.5 方案五：过滤异常 Key

```scala
// 如果 null / 空值 / 特殊值 占比过高，先过滤再处理
val filtered = orders.filter(col("merchant_id").isNotNull && col("merchant_id") =!= "")
val nullOrders = orders.filter(col("merchant_id").isNull || col("merchant_id") === "")

// 正常数据走 Join
val joined = filtered.join(merchants, "merchant_id")

// null 数据单独处理（通常直接丢弃或填充默认值）
val result = joined.union(nullOrders.withColumn("merchant_name", lit("UNKNOWN")))
```

### 2.6 方案六：Map-Side Join（桶表优化）

```sql
-- Hive / Spark SQL：如果两张表已按相同方式分桶，可走 Bucket Map Join
CREATE TABLE orders_bucketed CLUSTERED BY (merchant_id) INTO 64 BUCKETS AS ...;
CREATE TABLE merchants_bucketed CLUSTERED BY (merchant_id) INTO 64 BUCKETS AS ...;

SET spark.sql.autoBroadcastJoinThreshold = -1;  -- 禁用 Broadcast
SET spark.sql.join.preferSortMergeJoin = false;

-- Spark 自动检测桶表并走 Bucket Map Join，无 Shuffle
SELECT * FROM orders_bucketed o JOIN merchants_bucketed m ON o.merchant_id = m.id;
```

---

## 三、常见陷阱

### 陷阱 1：AQE 不是银弹
- **真相**：AQE 只能优化 **Sort Merge Join** 中的倾斜，对 Broadcast Join 和 Shuffle Hash Join 无效。且 AQE 在运行时收集统计信息有额外开销，对短查询（< 10 秒）反而可能变慢。

### 陷阱 2：加盐后数据膨胀
- **真相**：小表 explode 成 N 份意味着网络传输量翻 N 倍。N 的选择需要权衡：太小倾斜没解决，太大小表膨胀严重。经验值 50-200。

### 陷阱 3：Broadcast Join 的 OOM 风险
- **真相**：Broadcast 阈值设太大（如 1GB），Driver 需要在内存中持有完整的小表副本并序列化广播。Executor 数量 × 表大小 = 实际内存占用。超过 Driver 内存就会 OOM。

### 陷阱 4：忽略 Shuffle 的序列化开销
- **真相**：Spark 默认用 Java 序列化，性能差。切换到 Kryo 序列化通常能提速 2-10 倍：`spark.serializer = org.apache.spark.serializer.KryoSerializer`。

---

## 四、最佳实践

```text
数据倾斜解决方案选择决策树：
├── 小表 Join 大表？（< 100MB）
│   └── → Broadcast Join（零 Shuffle，最优解）
├── Spark 3.0+？
│   └── → 开启 AQE（自动优化，无需改代码）
├── 聚合操作倾斜？
│   └── → 两阶段聚合（加盐局部聚合 + 去盐全局聚合）
├── 大表 Join 大表？
│   ├── → 加盐（Salting）
│   └── → 或预先分桶（Bucket Map Join）
└── null / 空值导致的倾斜？
    └── → 过滤异常 Key 后单独处理
```

---

## 五、面试话术（90 秒版本）

> "Spark Shuffle 数据倾斜的本质是 **key 的 hash 分布不均匀**，导致个别 Task 处理的数据量远超其他 Task，整个 Job 退化为串行。"
>
> "解决方案按场景分 6 种：**小表场景**优先 Broadcast Join 完全避免 Shuffle；**Spark 3.0+** 开启 AQE 自适应倾斜连接，自动检测并拆分倾斜 partition；**聚合场景**用两阶段聚合——先加盐做局部聚合再去盐做全局聚合；**大表 Join** 用加盐打散热点 key 或预先分桶走 Bucket Map Join；**null 值倾斜**直接过滤后单独处理。"
>
> "生产中我最常用的是 AQE + Broadcast Join 组合。AQE 一行配置就能解决大部分倾斜问题，Broadcast Join 在小表场景下零 Shuffle 是最优解。加盐方案作为兜底，适合 AQE 覆盖不到的场景。"

---

## 六、交叉引用

- **同栏目**：[`Hive 分区 vs 分桶`](../hive-partition-vs-bucket/README.md) — 分桶是 Map-Side Join 的基础
- **同栏目**：[`Flink Checkpoint vs Savepoint`](../flink-checkpoint-vs-savepoint/README.md) — 流处理的容错对比
- **主模块**：[`03.database`](../../../03.database/README.md) — 数据库层面的查询优化

---

> 📅 2026-07-16 · 咬文嚼字 · 大数据 · Spark 性能 · ⭐⭐⭐⭐⭐

← [返回: 咬文嚼字 · 大数据](../README.md)
