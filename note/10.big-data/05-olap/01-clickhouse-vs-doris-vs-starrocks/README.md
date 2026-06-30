# ClickHouse vs Apache Doris vs StarRocks：实时 OLAP 三剑客深度对比

> 一份按场景梳理的 OLAP 引擎速查手册：从架构原理到生产选型的完整对比。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

ClickHouse vs Apache Doris vs StarRocks：实时 OLAP 三剑客深度对比 本应该很简单，一份按场景梳理的 OLAP 引擎速查手册：从架构原理到生产选型的完整对比

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、OLAP 三剑客概览

| 引擎 | 出生 | 主导方 | 核心理念 |
|------|------|--------|---------|
| **ClickHouse** | 2016 | Yandex（俄罗斯）| 列存 + 向量化 + 单表极致性能 |
| **Apache Doris** | 2017 | 百度 → Apache | 兼容 MySQL 协议 + 实时数仓 |
| **StarRocks** | 2020 | Apache Doris 分支 → 鼎石科技 | MySQL 兼容 + CBO 优化器 + 多表 JOIN |

---

## 二、ClickHouse 详解

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

## 三、Apache Doris 详解

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

## 四、StarRocks 详解

### 4.1 核心特性

- **CBO 优化器**：基于代价的多表 JOIN 优化（行业领先）
- **向量化执行 + CBO**：性能优于 Doris
- **实时数仓**：Kafka → StarRocks（秒级）
- **兼容 MySQL 协议**：生态友好
- **多表物化视图**：复杂查询加速

### 4.2 典型场景

- 复杂多表 JOIN（电商订单 + 用户 + 商品）
- 实时数据仓库（替代 ClickHouse + Druid）
- 高并发实时查询（每分钟 10 万+ QPS）

---

## 五、12 维度深度对比

| 维度 | ClickHouse | Apache Doris | StarRocks |
|------|-----------|--------------|-----------|
| **协议兼容** | HTTP / TCP | MySQL ✅ | MySQL ✅ |
| **单表查询** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **多表 JOIN** | ⭐⭐⭐（弱）| ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **实时摄入** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **并发查询** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **运维复杂度** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **生态成熟度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **云原生** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **国产化支持** | 俄罗斯（受国际影响）| 国产开源（百度）| 国产开源（鼎石）|
| **多表物化视图** | ⚠️ 弱 | ✅ 支持 | ✅ 强 |
| **运维工具** | 自带 / 第三方 | 自带 | 自带（更完善）|
| **学习曲线** | 中 | 低（MySQL 友好）| 低 |

---

## 六、生产选型决策

```
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

## 七、典型场景对比

| 场景 | 推荐 | 理由 |
|------|------|------|
| **用户行为日志分析**（单表）| ClickHouse | 单表性能极致 |
| **电商订单 + 用户 + 商品 JOIN** | StarRocks | CBO 多表 JOIN 强 |
| **实时报表（MySQL 兼容）**| Doris | 协议兼容、生态成熟 |
| **指标监控（Prometheus 替代）**| ClickHouse | 写入快、压缩率高 |
| **PB 级实时数据仓库** | StarRocks / Doris | 实时摄入 + 高并发 |
| **多维分析（ad-hoc）**| StarRocks | CBO 优化器最优 |

---

## 八、生产实战

### 8.1 ClickHouse 集群部署

```bash
# 1 个 clickhouse-server，多个分片
# 配置文件 /etc/clickhouse-server/config.xml
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
-- 创建表
CREATE TABLE orders (
  order_id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  order_time DATETIME
)
UNIQUE KEY(order_id)
DISTRIBUTED BY HASH(order_id) BUCKETS 32
PROPERTIES (
  "replication_num" = "3"
);

-- Kafka → Doris Stream Load
INSERT INTO orders
SELECT * FROM kafka_source
WHERE order_time > '2026-01-01';
```

### 8.3 StarRocks 多表物化视图

```sql
-- 创建异步物化视图
CREATE MATERIALIZED VIEW order_summary_mv
DISTRIBUTED BY HASH(order_id)
REFRESH ASYNC EVERY (INTERVAL 1 HOUR)
AS SELECT
  o.order_id,
  u.user_name,
  p.product_name,
  o.amount,
  o.order_time
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN products p ON o.product_id = p.product_id;
```

---

## 九、迁移路径

### 从 MySQL → OLAP

```
MySQL → DataX / Flink CDC → Kafka → Doris/StarRocks → BI
   异步复制（不影响线上 MySQL）
```

### 从 Hive → 实时 OLAP

```
Hive → Spark → Iceberg → Doris/StarRocks
   或
Hive → Presto/Trino（过渡）
```

---

## 十、最佳实践

1. **ClickHouse 适合单表**：多表 JOIN 性能一般
2. **Doris 适合实时报表**：MySQL 协议兼容、运维简单
3. **StarRocks 适合复杂 JOIN**：CBO 优化器最强
4. **数据规模 PB 级**：首选 ClickHouse（分片成熟）
5. **国产化 + MySQL 生态**：首选 Doris
6. **多团队混合引擎**：考虑统一（不要三套都用）

---

← [返回 10.big-data 主目录](../../README.md) · 📅 2026-06-28