<!--
module:
  parent: big-data
  slug: big-data/clickhouse-vs-doris-vs-starrocks
  type: article
  category: 主模块子文章
  summary: ClickHouse vs Doris vs StarRocks——实时 OLAP 三剑客深度对比
-->

# ClickHouse vs Apache Doris vs StarRocks：实时 OLAP 三剑客深度对比

> 一份按场景梳理的 OLAP 引擎速查手册：从架构原理到生产选型的完整对比。

---

## 1. 模块导航

| 引擎 | 出生 | 主导方 | 核心理念 |
|------|------|--------|---------|
| **ClickHouse** | 2016 | Yandex（俄罗斯）| 列存 + 向量化 + 单表极致性能 |
| **Apache Doris** | 2017 | 百度 → Apache | 兼容 MySQL 协议 + 实时数仓 |
| **StarRocks** | 2020 | Apache Doris 分支 → 鼎石科技 | MySQL 兼容 + CBO 优化器 + 多表 JOIN |

### 1.1 学习路径

- 新人：从 Doris 入手（MySQL 协议兼容，学习曲线最低）
- 进阶：ClickHouse MergeTree 家族引擎
- 实战：Kafka → Doris Stream Load 实时大屏链路

---

## 2. ClickHouse 详解

### 2.1 核心特性

- **列式存储 + 向量化执行**：极致单表查询性能
- **压缩算法**：每列自适应压缩（LZ4 / ZSTD）
- **MergeTree 引擎**：数据按主键排序、后台合并
- **分布式**：分片（shard）+ 副本（replica）
- **生态丰富**：JDBC / ODBC / HTTP / CLI

### 2.2 典型场景

- 日志分析（用户行为 / 业务日志）
- 实时大宽表查询（单表数十亿行）
- 监控指标存储（Prometheus 后端）

---

## 3. Apache Doris 详解

### 3.1 核心特性

- **MySQL 协议兼容**：直接用 MySQL 客户端连接
- **FE / BE 架构**：Frontend（查询优化）+ Backend（存储计算）
- **多种存储模型**：聚合模型 / 明细模型 / 更新模型
- **实时数仓**：Kafka → Doris（秒级延迟）

### 3.2 典型场景

- 实时报表（MySQL 协议 + 高并发）
- 用户行为分析（PB 级）
- 替代 MySQL + Elasticsearch 的 OLAP 场景

---

## 4. StarRocks 详解

### 4.1 核心特性

- **CBO 优化器**：基于代价的多表 JOIN 优化（行业领先）
- **向量化执行 + CBO**：性能优于 Doris
- **实时数仓**：Kafka → StarRocks（秒级）
- **兼容 MySQL 协议**：生态友好
- **多表物化视图**：复杂查询加速

### 4.2 典型场景

- 复杂多表 JOIN（电商订单 + 用户 + 商品）
- 实时数据仓库（替代 ClickHouse + Druid）
- 高并发实时查询（QPS 量级以官方 benchmark 与实际硬件为准）

---

## 5. 12 维度深度对比

| 维度 | ClickHouse | Apache Doris | StarRocks |
|------|-----------|--------------|-----------|
| **协议兼容** | HTTP / TCP | MySQL ✅ | MySQL ✅ |
| **单表查询** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **多表 JOIN** | ⭐⭐⭐（弱）| ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **实时摄入** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **并发查询** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **运维复杂度** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **生态成熟度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **云原生** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **国产化支持** | 俄罗斯（受国际影响）| 国产开源（百度）| 国产开源（鼎石）|
| **多表物化视图** | ⚠️ 弱 | ✅ 支持 | ✅ 强 |
| **运维工具** | 自带 / 第三方 | 自带 | 自带（更完善）|
| **学习曲线** | 中 | 低（MySQL 友好）| 低 |

---

## 6. 生产选型决策

```text
Q1: 主要场景？
├── 单表大宽表分析 → ClickHouse（极致性能）
├── 多表 JOIN + 高并发 → StarRocks（首选）
├── 实时报表 + MySQL 兼容 → Doris（平衡）
└── 复杂分析 + 灵活查询 → StarRocks / Doris

Q2: 团队背景？
├── MySQL DBA 多 → Doris / StarRocks
├── 数据团队为主 → ClickHouse
└── 全栈 → StarRocks（综合最强）

Q3: 数据规模？
├── TB 级 → 都可
├── PB 级 → ClickHouse / StarRocks
└── 100+ PB → ClickHouse（分片成熟）

Q4: 国产化要求？
├── 强 → Doris / StarRocks（国内主导）
└── 无要求 → ClickHouse / Doris / StarRocks 都行
```

---

## 7. 典型场景对比

| 场景 | 推荐 | 理由 |
|------|------|------|
| **用户行为日志分析**（单表）| ClickHouse | 单表性能极致 |
| **电商订单 + 用户 + 商品 JOIN** | StarRocks | CBO 多表 JOIN 强 |
| **实时报表（MySQL 兼容）**| Doris | 协议兼容、生态成熟 |
| **指标监控（Prometheus 替代）**| ClickHouse | 写入快、压缩率高 |
| **PB 级实时数据仓库** | StarRocks / Doris | 实时摄入 + 高并发 |
| **多维分析（ad-hoc）**| StarRocks | CBO 优化器最优 |

---

## 8. 生产实战

### 8.1 ClickHouse 集群部署

```xml
<remote_servers>
  <my_cluster>
    <shard>
      <internal_replication>true</internal_replication>
      <replica><host>ch1</host><port>9000</port></replica>
      <replica><host>ch2</host><port>9000</port></replica>
    </shard>
    <shard>
      <internal_replication>true</internal_replication>
      <replica><host>ch3</host><port>9000</port></replica>
    </shard>
  </my_cluster>
</remote_servers>
```

### 8.2 Doris 实时数据摄入

```sql
CREATE TABLE orders (
  order_id BIGINT, user_id BIGINT, amount DECIMAL(10,2), order_time DATETIME
)
UNIQUE KEY(order_id)
DISTRIBUTED BY HASH(order_id) BUCKETS 32
PROPERTIES ("replication_num" = "3");

INSERT INTO orders
SELECT * FROM kafka_source WHERE order_time > '2026-01-01';
```

### 8.3 StarRocks 多表物化视图

```sql
CREATE MATERIALIZED VIEW order_summary_mv
DISTRIBUTED BY HASH(order_id)
REFRESH ASYNC EVERY (INTERVAL 1 HOUR)
AS SELECT
  o.order_id, u.user_name, p.product_name, o.amount, o.order_time
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id;
```

---

## 9. 迁移路径

**MySQL → OLAP**：

```text
MySQL → DataX / Flink CDC → Kafka → Doris/StarRocks → BI
   异步复制（不影响线上 MySQL）
```

**Hive → 实时 OLAP**：

```text
Hive → Spark → Iceberg → Doris/StarRocks
   或
Hive → Presto/Trino（过渡）
```

---

## 10. 最佳实践

| 实践 | 说明 |
|------|------|
| ClickHouse 适合单表 | 多表 JOIN 性能一般 |
| Doris 适合实时报表 | MySQL 协议兼容、运维简单 |
| StarRocks 适合复杂 JOIN | CBO 优化器最强 |
| 数据规模 PB 级 | 首选 ClickHouse（分片成熟） |
| 国产化 + MySQL 生态 | 首选 Doris |
| 多团队混合引擎 | 考虑统一（不要三套都用） |

---

## 11. 常见面试题

| 题目 | 核心考点 |
|------|---------|
| OLAP 三剑客核心差异？ | 单表极致 / MySQL 兼容 / CBO 优化 |
| ClickHouse 为何不擅长 JOIN？ | 列存 + 单表极致优化 |
| Doris Unique Key 表 MOR 优势？ | 实时 upsert + 读时合并 |
| StarRocks CBO 比 Doris 强在哪？ | 基于成本的多表 JOIN 优化 |
| 物化视图 vs 实时聚合？ | 预计算 vs 流式聚合；查询延迟 vs 实时性 |
| 国产化 OLAP 选哪个？ | Doris / StarRocks（ClickHouse 受国际影响） |

---

## 12. 与其他模块的关系

- **上游**：[05-olap](../)（OLAP 总览）
- **下游**：被 [11 数据可视化](../../../11.ai/) / 报表工具消费
- **横向**：[04 数据湖](../../04-data-lake/)（数据湖 + OLAP 联合）

---

## 📊 本节统计

| 维度 | 数字 |
|------|------|
| OLAP 引擎数 | 3（ClickHouse / Doris / StarRocks） |
| 12 维度对比项 | 12 |
| 选型决策问题 | 4（场景 / 团队 / 规模 / 国产化） |
| 典型场景对比 | 6 |
| 实战案例数 | 3（ClickHouse 部署 / Doris 摄入 / StarRocks 物化视图）|
| 迁移路径数 | 2（MySQL / Hive）|
| 最佳实践条数 | 6 |
| 常见面试题数 | 6 |
| frontmatter 覆盖率 | 1 / 1 = 100% |
| 文末回链覆盖 | 1 / 1 = 100% |

---

← [返回 OLAP 总览](../) · ← [返回大数据总览](../../README.md)