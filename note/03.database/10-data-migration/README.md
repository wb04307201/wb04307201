<!--
module:
  parent: database
  slug: database/data-migration
  type: index
  category: 主模块子文章
  summary: 数据迁移覆盖全量、增量、异构三大场景,核心工具包括 DataX（离线全量）、Canal/Maxwell（Binlog 增量）、Flink CDC（实时流式）。
-->

# 数据迁移与同步

> 数据迁移与同步是企业级数据库的核心工程能力,涵盖全量迁移、增量同步、异构同步三大场景;常用工具包括 DataX(离线全量)、Canal/Maxwell(基于 Binlog 增量)、Flink CDC(实时流式)。


---

## 📚 核心内容

| 主题 | 内容 | 关键点 |
|------|------|--------|
| 一、数据迁移场景 | 升级 / 机房迁移 / 异构 / 分库分表 / 数仓 / 双写 | 全量 + 增量最常用 |
| 二、DataX(阿里开源) | Reader / Framework / Writer 三层架构 | 单机多线程,30+ 数据源 |
| 三、Canal(阿里 Binlog) | 模拟 Slave + ZK 高可用 + Java 客户端 | MySQL → MQ/ES/Redis |
| 四、Maxwell(Zendesk) | JSON 输出 + 主备锁 + 全增量一体化 | 轻量,无 ZK 依赖 |
| 五、Flink CDC(实时流式) | 全增量一体化 + Exactly-Once + Schema 演进 | MySQL → Doris/ES/Kafka |
| 六、工具对比与选型 | DataX / Canal / Maxwell / Flink CDC / Debezium | 决策树按实时性 + 下游选型 |
| 七、迁移实战要点 | 全量前准备 + 增量同步 + 双写切换 + 校验 | 4 阶段渐进 + 行数/Checksum 对比 |

---

## 一、数据迁移场景

| 场景 | 典型需求 | 同步方式 |
|------|---------|---------|
| **数据库升级** | MySQL 5.7 → 8.0 | 全量 + 增量 |
| **机房迁移** | 自建机房 → 阿里云 | 全量 + 增量 |
| **异构同步** | MySQL → Elasticsearch | 全量 + 增量 |
| **分库分表** | 单库 → 16 库 64 表 | 全量 + 增量 |
| **数据仓库** | MySQL → Hive/ClickHouse | T+1 全量 |
| **双写过渡** | 旧库 → 新库(灰度) | 双向同步 |

### 同步模式

| 模式 | 特点 |
|------|------|
| **全量同步** | 一次性把源库全部数据写入目标,适合初始化 |
| **增量同步** | 只同步源库新产生的变更(Binlog/触发器/时间戳) |
| **全量 + 增量** | 先全量初始化,再持续增量,**生产环境最常用** |

---

## 二、DataX(阿里开源离线同步)

DataX 是阿里开源的**异构数据源离线同步工具**,支持 MySQL、Oracle、PostgreSQL、HDFS、Hive、Elasticsearch 等 30+ 数据源。

### 1. 核心架构

```text
┌────────────┐
│  Reader    │  ← 读取源数据
└─────┬──────┘
      │
┌─────▼──────┐
│  Framework │  ← 任务调度、限流、容错
└─────┬──────┘
      │
┌─────▼──────┐
│  Writer    │  ← 写入目标
└────────────┘
```

- **Framework** 负责切片、并发、限流、容错
- **Reader/Writer** 是数据源插件,实现 Reader/Writer API 即可扩展
- **单机多线程** 模型(非分布式),大任务需单机资源够

### 2. MySQL → MySQL 全量同步配置

```json
{
    "job": {
        "content": [{
            "reader": {
                "name": "mysqlreader",
                "parameter": {
                    "username": "root",
                    "password": "password",
                    "connection": [{
                        "jdbcUrl": ["jdbc:mysql://src-host:3306/mydb"],
                        "table": ["users", "orders"]
                    }],
                    "column": ["id", "name", "email", "created_at"],
                    "splitPk": "id"
                }
            },
            "writer": {
                "name": "mysqlwriter",
                "parameter": {
                    "username": "root",
                    "password": "password",
                    "jdbcUrl": "jdbc:mysql://dst-host:3306/mydb",
                    "table": ["users", "orders"],
                    "writeMode": "insert"
                }
            }
        }],
        "setting": {
            "speed": {
                "channel": 8,           // 并发通道数
                "byte": 1048576         // 限速 1MB/s
            }
        }
    }
}
```

```bash
python datax.py job/mysql2mysql.json
```

### 3. 性能调优

| 参数 | 含义 | 推荐值 |
|------|------|--------|
| `channel` | 并发数 | CPU 核数 × 2 |
| `batchSize` | 每批写入记录数 | 1024~4096 |
| `speed.byte` | 字节限速 | 100MB/s+ |
| `speed.record` | 记录数限速 | 10000/s |

> **实战**:5 亿行 MySQL 表迁移约 2-4 小时(channel=16,batchSize=2048)。

### 4. 局限

- ❌ **无分布式**:单节点瓶颈
- ❌ **断点续传弱**:失败需重跑
- ❌ **不支持实时**:只支持离线/全量

---

## 三、Canal(阿里 Binlog 订阅)

Canal 模拟 MySQL Slave 接收 Binlog,**实时**解析并投递到下游(MQ、Redis、ES 等)。

### 1. 核心原理

```text
MySQL Master ── binlog ──→ Canal Server ──→ Canal Client ──→ 下游系统
         (row format)        (伪装 Slave)      (解析/订阅)
```

1. Canal Server 模拟 MySQL Slave,向 Master 发送 `dump` 协议
2. Master 推送 Binlog Event
3. Canal 解析 Event(insert/update/delete) → 转换为业务消息
4. Canal Client 订阅 Canal Server 投递的变更

### 2. 部署架构

```text
┌──────────────────────────────────────┐
│           Canal Server                │
│  ┌──────────┐  ┌──────────┐  ┌─────┐│
│  │ Instance1│  │ Instance2│  │ ... ││
│  │ 监听 DB1 │  │ 监听 DB2 │  │     ││
│  └────┬─────┘  └────┬─────┘  └─────┘│
└───────┼─────────────┼───────────────┘
        │             │
   ZK 集群(高可用与配置)
        │             │
   ┌────▼─────────────▼─────┐
   │      Canal Client       │  → MQ / Kafka / RocketMQ
   └─────────────────────────┘   → 业务消费(MQ → ES/Redis)
```

### 3. Canal 配置

```properties
# canal.properties
canal.id = 1
canal.ip = 192.168.1.10
canal.port = 11111
canal.zkServers = zk1:2181,zk2:2181,zk3:2181

# instance.properties
canal.instance.mysql.slaveId = 1234
canal.instance.master.address = 192.168.1.5:3306
canal.instance.dbUsername = canal
canal.instance.dbPassword = canal
canal.instance.defaultDatabaseName = mydb
canal.instance.filter.regex = mydb\\..*
canal.instance.tsdb.enable = true
```

### 4. Java 客户端示例

```java
CanalConnector connector = CanalConnectors.newClusterConnector(
    "zk1:2181,zk2:2181,zk3:2181",
    "example",
    "canal",
    "canal"
);
connector.connect();
connector.subscribe(".*\\..*");
connector.rollback();

while (running) {
    Message message = connector.getWithoutAck(100);
    long batchId = message.getId();
    if (batchId != -1) {
        for (CanalEntry.Entry entry : message.getEntries()) {
            if (entry.getEntryType() == EntryType.ROWDATA) {
                RowChange rowChange = CanalEntry.RowChange.parseFrom(entry.getStoreValue());
                for (RowData rowData : rowChange.getRowDatasList()) {
                    // 业务处理:同步到 ES / Redis / 缓存失效
                }
            }
        }
        connector.ack(batchId);
    }
}
```

### 5. 适用场景

- MySQL → Elasticsearch 同步(搜索)
- MySQL → Redis 同步(缓存预热)
- MySQL → Kafka 同步(下游数据分发)
- 异地多活数据同步

### 6. 关键注意事项

- ✅ MySQL 必须开启 **Binlog 且为 ROW 格式**
- ✅ Canal 用户需有 **REPLICATION SLAVE** 权限
- ✅ 监控 Canal 消费位点(避免延迟累积)
- ⚠️ Binlog 延迟时 Canal 会延迟同步,需告警

---

## 四、Maxwell(Zendesk 开源)

Maxwell 是另一款 MySQL Binlog 订阅工具,比 Canal 更轻量,直接输出 **JSON 到 Kafka**。

### 1. 与 Canal 对比

| 特性 | Canal | Maxwell |
|------|-------|---------|
| 输出 | 自定义协议,需编码 | **JSON,开箱即用** |
| HA | ZK 集群 | 内置主备(Redis 锁) |
| 部署 | 较重(JVM + ZK) | 轻量(单 JAR) |
| 客户端 | 多语言(Java 为主) | 任何语言(消费 JSON) |
| 数据过滤 | 弱(订阅粒度) | 内置 SQL 过滤 |
| Bootstrap | 无 | **支持全量 + 增量一体化** |

### 2. 配置示例

```properties
# config.properties
producer=kafka
kafka.bootstrap.servers=localhost:9092
kafka_topic=cdc

# MySQL 连接
host=127.0.0.1
user=maxwell
password=maxwell

# 过滤表
filter=include: db1.users, db1.orders

# 启动位置
bootstrapper=async
```

```bash
maxwell --config=config.properties --daemon
```

### 3. 输出 JSON 格式

```json
{
    "database": "mydb",
    "table": "users",
    "type": "insert",
    "ts": 1623238812,
    "xid": 12345,
    "data": {
        "id": 1001,
        "name": "张三",
        "email": "a@b.com"
    }
}
```

### 4. 适用场景

- 快速搭建 CDC 管道(无 ZK 依赖)
- 异构同步(Spark/Flink/ES 直接消费 JSON)
- 全量初始化 + 增量同步一体化

---

## 五、Flink CDC(实时流式同步)

Flink CDC 基于 **Flink 流处理引擎**提供**全增量一体化同步**,支持 MySQL、PostgreSQL、Oracle、MongoDB 等。

### 1. 核心优势

- **全增量一体化**:无需先全量再切换增量
- **Exactly-Once 语义**:基于 Flink 状态 + 2PC
- **支持 Schema 演进**:DDL 同步(部分)
- **强大的下游生态**:Kafka、Pulsar、JDBC、Iceberg、Hudi 等

### 2. MySQL → Doris 同步(SQL 一行配置)

```sql
-- Flink SQL
CREATE TABLE source_users (
    id INT PRIMARY KEY,
    name STRING,
    email STRING
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = '127.0.0.1',
    'port' = '3306',
    'username' = 'flink',
    'password' = 'flink',
    'database-name' = 'mydb',
    'table-name' = 'users'
);

CREATE TABLE sink_users (
    id INT PRIMARY KEY,
    name STRING,
    email STRING
) WITH (
    'connector' = 'doris',
    'fenodes' = '127.0.0.1:8030',
    'table.identifier' = 'mydb.users',
    'sink.enable-2pc' = 'true'
);

INSERT INTO sink_users SELECT * FROM source_users;
```

### 3. 全量阶段

Flink CDC 启动时:
1. 锁定 Binlog 位点(`SHOW MASTER STATUS`)
2. 执行全量快照(`SELECT *` 配合一致性读)
3. 从锁定位点开始订阅增量 Binlog
4. 全量 + 增量**无缝衔接**

### 4. 适用场景

- 数据仓库实时入仓(MySQL → Doris/StarRocks/Hudi)
- 异构实时同步(MySQL → Elasticsearch)
- 多源汇聚(多 MySQL → 统一 Kafka 主题)
- 数据库镜像(MySQL → MySQL 容灾)

### 5. 版本与依赖

| 组件 | 版本要求 |
|------|---------|
| Flink | 1.13+(推荐 1.17+) |
| MySQL | 5.7+ / 8.0+(开启 Binlog ROW 模式) |
| JDK | 8 / 11 |

---

## 六、工具对比与选型

| 工具 | 类型 | 实时性 | 异构 | 分布式 | 适用场景 |
|------|------|--------|------|--------|---------|
| **DataX** | 离线全量 | ❌ 离线 | ✅ | ❌ 单机 | T+1 仓库、一次性迁移 |
| **Canal** | Binlog 订阅 | ✅ 秒级 | ✅ | ✅ ZK 集群 | MySQL → MQ/ES/Redis |
| **Maxwell** | Binlog 订阅 | ✅ 秒级 | ✅ | ⚠️ 主备 | 轻量 CDC 管道 |
| **Flink CDC** | 流式 CDC | ✅ 实时 | ✅ | ✅ Flink 集群 | 大规模实时数据集成 |
| **DTS(阿里云)** | 商业 | ✅ | ✅ | ✅ | 云上托管,免运维 |
| **DMS(华为云)** | 商业 | ✅ | ✅ | ✅ | 华为云用户 |
| **Debezium** | Binlog 订阅 | ✅ | ✅ | ✅ Kafka | Kafka 生态首选 |

### 选型决策树

```text
是否需要实时同步?
├─ 否 → DataX(全量) 或 sqoop
└─ 是 → 下游是什么?
       ├─ Kafka / MQ → Canal / Maxwell / Debezium
       ├─ ES / 数据仓库 → Flink CDC
       └─ 同构 MySQL → 阿里云 DTS(免运维)
```

---

## 七、迁移实战要点

### 1. 全量迁移前准备

| 步骤 | 内容 |
|------|------|
| ① **数据校验** | 源库与目标库表结构一致性、行数差异、checksum 校验 |
| ② **回滚方案** | 保留源库可写,目标库先只读,出问题秒切回 |
| ③ **限速保护** | DataX 设置 `speed.byte` 限速,避免打满源库 |
| ④ **业务方沟通** | 选择业务低峰期(凌晨 2-5 点) |
| ⑤ **数据脱敏** | 含敏感字段(身份证、手机号)的提前脱敏 |

### 2. 增量同步阶段

1. 全量完成后,**记录源库 Binlog 位点**
2. Canal/Maxwell 从该位点开始订阅
3. 实时同步增量到目标库
4. **监控延迟**:目标库落后 Binlog 位点的时间应 < 1s

### 3. 切换双写与回滚

```text
阶段 1: 老库写,新库只读
       ↓ 验证 1-2 天
阶段 2: 老库 + 新库双写(增量同步核对)
       ↓ 验证 1-2 天
阶段 3: 新库为主,老库只读
       ↓ 验证 1-2 天
阶段 4: 停用老库
```

### 4. 数据一致性校验

```sql
-- 行数对比
SELECT COUNT(*) FROM source_db.users;
SELECT COUNT(*) FROM target_db.users;

-- Checksum 对比
CHECKSUM TABLE source_db.users;
CHECKSUM TABLE target_db.users;

-- 抽样业务字段(MySQL 用 RAND() 抽样,PostgreSQL 用 TABLESAMPLE)
-- MySQL:
SELECT id, MD5(CONCAT(name, email)) AS hash
FROM source_db.users WHERE RAND() < 0.001;  -- 约 0.1% 抽样
-- PostgreSQL:
SELECT id, MD5(CONCAT(name, email)) AS hash
FROM source_db.users TABLESAMPLE BERNOULLI(0.1);  -- 0.1% 抽样
```

### 5. 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 主键冲突 | 增量与全量重复 | 全量期间源库只读 |
| Binlog 延迟 | Canal 处理慢 | 加大 Canal 实例 + 优化下游 |
| 字段类型不兼容 | 异构库差异 | 显式转换(DATE → TIMESTAMP) |
| 大表迁移超时 | 切分不合理 | 按 ID 范围分批 |
| 切换后丢数据 | 增量未追平 | 延迟 < 5s 后再切换 |

---

## 🔗 相关章节

- [MySQL](../05-mysql/README.md) — Binlog 格式、主从复制
- [事务与并发控制](../03-transaction/README.md) — 一致性与并发同步
- [缓存](../06-cache/README.md) — 缓存预热与 Canal 协同
- [系统设计 · 分布式事务](../../04.system-design/02-distributed/distributed-transaction/README.md) — 数据一致性理论

---

## 📊 本节统计

- **leaf README 数**：1（本文即为分类 leaf，单 README 长文聚合 7 主题）
- **本节主题数**：7（迁移场景、DataX、Canal、Maxwell、Flink CDC、工具选型、实战要点）
- **frontmatter 状态**：✅ 已对齐 CONTRIBUTING §12 标准（summary ≤ 80 字 / type=index）
- **统计口径**：本目录无嵌套子目录，所有内容聚合在本 README

---

## 📖 参考资料

- [DataX GitHub](https://github.com/alibaba/DataX)
- [Canal GitHub](https://github.com/alibaba/canal)
- [Maxwell GitHub](https://github.com/zendesk/maxwell)
- [Flink CDC 官方文档](https://ververica.github.io/flink-cdc-connectors/)
- [Debezium 官方文档](https://debezium.io/documentation/)
- [阿里云数据传输服务 DTS](https://www.aliyun.com/product/dts)

---

**相关面试题**：[`分表扩容策略`](../../13.split-hairs/03.database/sharding-resize/README.md) — 翻倍扩容 + 双写过渡 + 灰度切换

← [返回 03.database 主模块](../README.md)