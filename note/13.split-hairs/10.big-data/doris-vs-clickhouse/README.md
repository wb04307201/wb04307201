<!--
question:
  id: 10.big-data-doris-vs-clickhouse
  topic: 10.big-data
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [10.big-data, Doris, ClickHouse, OLAP, 列存, 实时分析]
-->

# Doris vs ClickHouse 怎么选？

> 一句话定位：ClickHouse 是"单机暴力美学"的极致，Doris 是"分布式全能选手"——选错引擎意味着要么 Join 跑不动，要么运维扛不住。

> **系列定位**：经典大数据面试题（OLAP 选型高频）。考察的不是"两者都快"，而是 **架构差异的本质原因** + **Join 性能差距的根源** + **实时导入能力对比** + **生态与运维成本**。

---

## 引子：两个团队的选型之争

```text
公司要建统一 OLAP 平台，两个团队吵了起来：

团队 A（ClickHouse 派）：
"ClickHouse 单表查询比 Doris 快 3-10 倍，GitHub star 30K+，Yandex 生产验证！"

团队 B（Doris 派）：
"我们有 20 张大表的 Join 查询，ClickHouse 的 Join 是出了名的弱。
而且运维团队只有 3 个人，ClickHouse 集群扩缩容要手动 rebalance……"

CTO 的灵魂拷问："快是快在哪？弱是弱在哪？到底怎么选？"
```

这场争论在 2024-2026 年的大数据团队中反复上演。答案不是"A 比 B 好"，而是**搞清楚各自的架构基因**。

---

## 一、核心原理

### 1.1 TL;DR 架构对比

| 维度 | ClickHouse | Apache Doris |
|------|-----------|-------------|
| **架构** | 非对称（MergeTree 引擎） | MPP（FE + BE 对称架构） |
| **Join 能力** | 弱（Hash Join 内存受限） | 强（Runtime Filter + Colocate Join） |
| **单表查询** | 极快（向量化 + SIMD） | 快（向量化，略慢于 CH） |
| **实时导入** | 弱（异步 Merge，有延迟） | 强（Routine Load + Stream Load） |
| **扩缩容** | 手动（需 rebalance 数据） | 自动（数据自动均衡） |
| **事务** | 弱（无标准事务） | 支持（Exactly-Once 导入） |
| **生态** | 丰富（ClickHouse 公司全力推） | 增长中（百度开源 + 社区活跃） |
| **运维复杂度** | 高（配置项 500+） | 中（配置项 < 100） |

### 1.2 ClickHouse 为什么单表快

```text
ClickHouse 的 MergeTree 引擎有 3 个杀手级优化：

1. 向量化执行 + SIMD 指令
   - 一次处理 8192 行数据（一个 Column 块）
   - 利用 CPU 的 AVX2/AVX-512 指令集并行计算

2. 稀疏索引 + 数据排序
   - 主键不是唯一索引，而是稀疏索引（每 8192 行一个索引条目）
   - 数据按 ORDER BY 排序存储 → 范围查询极快

3. Merge 策略
   - 后台持续将小 part 合并为大 part
   - 读取时直接扫描已排序的大 part，无需合并
```

### 1.3 Doris 为什么 Join 强

```text
Doris 的 Join 优化有 3 层：

1. Colocate Join（同桶 Join）
   - 两表按相同方式分桶 → 相同桶号的数据在同一个 BE 节点
   - Join 在本地完成，零网络传输

2. Shuffle Join
   - 数据按 Join Key 重新分布到各 BE 节点
   - 分布式 Hash Join，适合大表 Join 大表

3. Runtime Filter
   - 在 Build 端生成 Bloom Filter / Min-Max Filter
   - 下发到 Probe 端，在扫描阶段就过滤掉 90%+ 不匹配的行
   - 大表 Join 小表场景下性能提升 5-10 倍
```

---

## 二、详解

### 2.1 数据模型对比

```sql
-- ClickHouse：MergeTree 系列引擎
CREATE TABLE events (
    event_date Date,
    user_id UInt64,
    event_type String,
    properties Map(String, String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_type, user_id, event_date)
TTL event_date + INTERVAL 90 DAY;  -- 90 天自动清理

-- Doris：Unique / Duplicate / Aggregate 模型
CREATE TABLE events (
    event_date DATE,
    user_id BIGINT,
    event_type VARCHAR(50),
    properties JSONB
) UNIQUE KEY(event_date, user_id, event_type)
DISTRIBUTED BY HASH(user_id) BUCKETS 16
PARTITION BY RANGE(event_date) (
    PARTITION p202607 VALUES LESS THAN ('2026-08-01')
)
PROPERTIES ("replication_num" = "3");
```

### 2.2 实时导入对比

```bash
# ClickHouse：Kafka Engine Table（异步消费，有延迟）
CREATE TABLE kafka_events (
    user_id UInt64, event_type String, ts DateTime
) ENGINE = Kafka()
SETTINGS kafka_broker_list = 'kafka:9092',
         kafka_topic_list = 'events',
         kafka_group_name = 'ch_group',
         kafka_format = 'JSONEachRow';

# 需要 Materialized View 将 Kafka 表数据导入 MergeTree 表
CREATE MATERIALIZED VIEW events_mv TO events AS
SELECT * FROM kafka_events;

# Doris：Routine Load（支持 Exactly-Once）
CREATE ROUTINE LOAD job_events ON events
COLUMNS TERMINATED BY ",",
COLUMNS(user_id, event_type, ts)
FROM KAFKA ("kafka_broker_list" = "kafka:9092",
            "kafka_topic" = "events",
            "property.group.id" = "doris_group");

# Doris：Stream Load（HTTP 接口，秒级延迟）
curl --location-trusted -u root: \
    -H "format: json" -H "strip_outer_array: true" \
    -T data.json http://fe:8030/api/db/events/_stream_load
```

### 2.3 扩缩容对比

```text
ClickHouse 扩容流程：
1. 添加新节点到集群配置
2. 修改 Distributed 表的集群配置
3. 手动执行 ALTER TABLE ... MOVE PARTITION 迁移数据
4. 或重建 Distributed 表 + 重新写入
5. 整个过程需要 DBA 介入，耗时小时级

Doris 扩容流程：
1. ALTER SYSTEM ADD BACKEND "new_host:9050";
2. 系统自动将 Tablet 从旧节点均衡到新节点
3. 后台自动完成，无需人工干预
4. 整个过程自动完成，耗时取决于数据量
```

---

## 三、常见陷阱

### 陷阱 1：ClickHouse 的 Join 不是不能用，而是要会用
- **真相**：ClickHouse 的 Hash Join 把 Build 表全量加载到内存，小表 Join 没问题。**大表 Join 大表**确实弱，但可以通过 Dictionary + 宽表预聚合规避。ClickHouse 的设计哲学是"尽量避免 Join"——用物化视图预计算。

### 陷阱 2：Doris 的 Unique 模型有性能代价
- **真相**：Unique 模型（主键去重）在写入时需要 Merge 操作，导入性能比 Duplicate 模型低 30-50%。如果数据本身不重复（如日志），应该用 Duplicate 模型而非 Unique。

### 陷阱 3：ClickHouse 的并发能力有限
- **真相**：ClickHouse 单查询极快，但并发能力有限（推荐 < 100 QPS）。每个查询占用大量 CPU 资源。高并发场景（BI 报表、用户自助查询）需要加缓存层。Doris 的 MPP 架构更适合高并发。

### 陷阱 4：忽略运维成本
- **真相**：ClickHouse 配置项 500+，集群管理复杂，社区版缺少企业级管控能力。3 人以下运维团队建议选 Doris——开箱即用，扩缩容自动，Web UI 完善。

---

## 四、最佳实践

```text
OLAP 引擎选型决策树：
├── 单表聚合查询为主 + 数据量大（> 100TB）？
│   └── → ClickHouse（单表性能无敌）
├── 多表 Join 查询为主？
│   └── → Doris（Colocate Join + Runtime Filter）
├── 高并发 BI 报表（> 500 QPS）？
│   └── → Doris（MPP + 缓存） 或 ClickHouse + 外部缓存
├── 运维团队 < 3 人？
│   └── → Doris（开箱即用，自动扩缩容）
├── 需要 Exactly-Once 实时导入？
│   └── → Doris（Routine Load 原生支持）
└── 已有 Kafka + Flink 生态？
    ├── → ClickHouse（Flink Connector 成熟）
    └── → Doris（Flink-Doris-Connector 官方维护）
```

---

## 五、面试话术（90 秒版本）

> "ClickHouse 和 Doris 的架构基因不同。ClickHouse 基于 **MergeTree 引擎**，通过向量化执行 + SIMD + 稀疏索引实现单表查询的极致性能，但 Join 是短板——Hash Join 把 Build 表全量放内存，大表 Join 大表容易 OOM。Doris 基于 **MPP 架构**（FE + BE），通过 Colocate Join（同桶本地 Join）和 Runtime Filter（Bloom Filter 下推）实现强 Join 能力。"
>
> "选型核心看 4 点：**查询模式**（单表聚合选 CH，多表 Join 选 Doris）、**并发需求**（高并发选 Doris）、**运维能力**（小团队选 Doris）、**实时性**（Exactly-Once 选 Doris Routine Load）。"
>
> "实际项目中，ClickHouse 更适合日志分析、指标聚合等单表场景；Doris 更适合 BI 报表、用户画像、多表关联分析等综合场景。2025 年以来 Doris 的向量化引擎（Nereids）已经大幅缩小了单表性能差距。"

---

## 六、交叉引用

- **同栏目**：[`Hive 分区 vs 分桶`](../hive-partition-vs-bucket/README.md) — 分区/分桶是 OLAP 引擎优化的基础
- **同栏目**：[`Iceberg ACID`](../iceberg-acid/README.md) — Doris 可直接查询 Iceberg 表（Lakehouse 模式）
- **同栏目**：[`Kafka Exactly-Once`](../kafka-exactly-once/README.md) — 实时导入的端到端一致性
- **主模块**：[`03.database`](../../../03.database/README.md) — 数据库引擎与查询优化基础

---

> 📅 2026-07-16 · 咬文嚼字 · 大数据 · OLAP 选型 · ⭐⭐⭐⭐

← [返回: 咬文嚼字 · 大数据](../README.md)
