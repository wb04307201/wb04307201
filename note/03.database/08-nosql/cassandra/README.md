<!--
module:
  parent: database/nosql
  slug: database/nosql/cassandra
  type: article
  category: 主模块子文章
  summary: Cassandra 列存储数据库：数据模型、Query-first Design、可调一致性级别
-->

# Cassandra 列存储数据库

> Apache Cassandra 是高度可扩展的分布式列存储数据库，源自 Facebook Inbox Search 论文，采用无中心节点（Ring 架构）设计，以最终一致性换取极高的写入吞吐和可用性。Apple、Netflix、Instagram 等大厂均有大规模部署。

---

## 📚 核心内容

| 主题 | 关键点 |
|------|--------|
| 核心概念 | Keyspace / Column Family / Partition Key / Clustering Key |
| 数据模型 | Query-first Design，基于查询反推表结构 |
| CQL 语法 | 类 SQL 但限制多，不支持 JOIN 和子查询 |
| 一致性级别 | ONE / QUORUM / ALL / LOCAL_QUORUM 可调 |
| 架构特点 | Ring 架构、Gossip 协议、无单点故障 |
| 适用场景 | 时序数据、物联网、消息系统、用户活动追踪 |

---

## 一、核心概念

| 概念 | 类比 SQL | 说明 |
|------|---------|------|
| **Keyspace** | Database | 命名空间，定义复制策略（SimpleStrategy / NetworkTopologyStrategy） |
| **Column Family (Table)** | Table | 列族，每行可有不同列（稀疏存储） |
| **Partition Key** | 主键（部分） | 决定数据分布到哪个节点（通过一致性哈希） |
| **Clustering Key** | - | 决定分区内数据排序，支持复合 |
| **Wide Row** | 多个独立行的合并 | 一个分区可包含数百万行（物理上连续存储） |
| **Tombstone** | - | 删除标记，Compaction 时真正清除 |

---

## 二、架构概览

Cassandra 采用 **Ring 架构**（无 Master 节点），所有节点对等：

```text
        ┌──────────┐
   ┌────┤  Node A  ├────┐
   │    └──────────┘    │
   │                    │
┌──┴────┐           ┌───┴───┐
│Node D │           │Node B │
└──┬────┘           └───┬───┘
   │                    │
   │    ┌──────────┐    │
   └────┤  Node C  ├────┘
        └──────────┘

数据按 Partition Key 哈希值分布到 Ring 上
每个节点负责一段 Token 范围
副本按 Replication Factor 顺时针复制
```

**关键机制**：
- **Gossip 协议**：节点间心跳通信，无中心协调
- **Hinted Handoff**：目标节点宕机时，写入方暂存 hint，节点恢复后重放
- **Read Repair**：读请求时检测副本不一致，自动修复
- **Compaction**：合并 SSTable，清理 Tombstone 和过期数据

---

## 三、数据模型与 Query-first Design

### 3.1 CQL 数据模型示例

```cql
-- Keyspace 定义（3 副本，按机房分布）
CREATE KEYSPACE user_db WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 2, 'dc2': 1
};

-- 用户活动表（按月分簇，避免单分区过大）
CREATE TABLE user_activity (
    user_id    UUID,        -- Partition Key
    year_month text,        -- Clustering Key（按月分簇）
    day        int,
    event      text,
    timestamp  timestamp,
    PRIMARY KEY ((user_id, year_month), day, timestamp)
) WITH CLUSTERING ORDER BY (day DESC, timestamp DESC);
```

### 3.2 查询模式

- ✅ `WHERE user_id = ? AND year_month = ?`（分区查询，**快**，单节点处理）
- ✅ `WHERE user_id = ? AND year_month = ? AND day > 15`（分区内范围，**快**）
- ❌ `WHERE year_month = ?`（全分区扫描，**Cassandra 禁止**，需 ALLOW FILTERING）
- ❌ `WHERE event = ?`（无索引，全表扫描）

> **Cassandra 设计原则**：**基于查询模式反推表结构**（Query-first Design），而非先建模后查询。同一份数据通常需要建多张表（反规范化），每张表对应一个查询模式。

### 3.3 反规范化示例

```cql
-- 按用户查活动
CREATE TABLE activity_by_user (
    user_id UUID, created_at timestamp, event text,
    PRIMARY KEY (user_id, created_at)
);

-- 按时间查所有用户活动（需配合 bucket 避免热分区）
CREATE TABLE activity_by_time (
    time_bucket text,  -- '2024-01' 格式，作为分区键
    user_id UUID, created_at timestamp, event text,
    PRIMARY KEY (time_bucket, created_at, user_id)
);
```

---

## 四、一致性级别（可调）

| Level | 含义 | 延迟 | 适用场景 |
|-------|------|------|---------|
| `ONE` | 1 个副本确认 | 最低 | 日志采集、计数器（允许丢失少量数据） |
| `QUORUM` | 多数副本确认（RF/2+1） | 中等 | 用户数据、业务核心 |
| `ALL` | 所有副本确认 | 最高 | 极少使用（任一节点宕机即失败） |
| `LOCAL_QUORUM` | 同机房多数确认 | 中（无跨机房延迟） | **多机房部署推荐** |
| `EACH_QUORUM` | 每个机房都多数确认 | 高 | 强一致跨机房 |
| `LOCAL_ONE` | 同机房 1 个节点 | 低 | 读多写少，允许短暂不一致 |

> **可调一致性是 Cassandra 的核心优势**：写用 `QUORUM` + 读用 `QUORUM` 可保证强一致（Read-Repair 兜底）；写用 `ONE` + 读用 `ONE` 追求极致性能。

**一致性公式**：若写级别为 `W`，读级别为 `R`，当 `W + R > RF`（副本数）时，保证读到最新数据。

---

## 五、常见反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| 超大分区（>100MB） | 单节点过载，Compaction 卡顿 | 引入时间 bucket 拆分分区 |
| 全表扫描（ALLOW FILTERING） | 扫所有节点，极慢 | 重新设计表结构匹配查询 |
| 频繁删除 | Tombstone 堆积，读性能下降 | 用 TTL 替代手动 DELETE |
| 用 Cassandra 做 JOIN | 不支持，需应用层处理 | 反规范化，宽表冗余 |
| 单节点部署 | 失去分布式优势 | 最少 3 节点，RF=3 |

---

## 六、时序数据模式

Cassandra 是时序数据的经典存储方案（IoT 传感器、监控指标、用户行为）：

```cql
CREATE TABLE sensor_data (
    sensor_id  UUID,
    bucket     text,       -- '2024-01-15' 日 bucket
    ts         timestamp,
    value      double,
    PRIMARY KEY ((sensor_id, bucket), ts)
) WITH CLUSTERING ORDER BY (ts DESC)
  AND default_time_to_live = 2592000;  -- 30 天自动过期
```

**设计要点**：
- **bucket 粒度**：按数据量选日/月/小时，保证单分区 ≤ 100MB
- **TTL 自动清理**：时序数据天然适合过期，避免手动 Compaction
- **写入路径**：数据先写 MemTable（内存），满后 flush 为 SSTable，全程顺序写，写入极快

---

## 七、与同类对比

| 维度 | Cassandra | HBase | MongoDB |
|------|-----------|-------|---------|
| 架构 | Ring（无 Master） | Master-Slave（HMaster + RegionServer） | Primary-Secondary（副本集） |
| 写入性能 | 极高（顺序写） | 极高（LSM Tree） | 高（WiredTiger） |
| 一致性 | 可调（ONE → QUORUM） | 强一致（基于 ZooKeeper） | 可调（w:1 → majority） |
| 查询能力 | CQL（类 SQL，无 JOIN） | Get/Scan（API 极简） | 丰富查询 + 聚合管道 |
| 运维复杂度 | 中（需关注 Compaction） | 高（依赖 Hadoop 生态） | 低（Atlas 托管） |
| 典型用户 | Apple（iCloud）、Netflix | 阿里、字节（日志平台） | 大量中小规模应用 |

---

## 🔗 相关章节

- [NoSQL 总览](../README.md) — NoSQL 类型对比与选型指南
- [HBase 架构](../README.md#八hbase-架构) — HBase 基于 HDFS，强一致列存储
- [系统设计 · 分布式存储](../../../04.system-design/02-distributed/) — 一致性哈希、Gossip 协议深入

---

← [返回 NoSQL 数据库](../README.md)
