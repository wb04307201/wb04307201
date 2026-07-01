<!--
module:
  parent: database
  slug: database/mysql
  type: index
  category: 主模块子文章
  summary: MySQL 采用 Server + 存储引擎两层架构,InnoDB 是默认引擎，核心机制覆盖 Buffer Pool、Redo Log、Binlog、主从复制与备份恢复。
-->

# MySQL

> MySQL 是最流行的开源关系型数据库,采用 Server 层 + 存储引擎层两层架构,InnoDB 是默认且推荐的事务型引擎,核心机制包括 Buffer Pool、Redo Log、Binlog 与主从复制。

> 最后更新: 2026-07-01

---

## 📚 核心内容

| 主题 | 内容 | 关键点 |
|------|------|--------|
| 一、MySQL 架构 | Server 层 + 存储引擎层 | 连接器 / 分析器 / 优化器 / 执行器 |
| 二、存储引擎对比 | InnoDB / MyISAM / Memory / Archive | 默认 InnoDB,事务安全 |
| 三、InnoDB 内部机制 | Buffer Pool + Change Buffer + 日志系统 + Double Write | Buffer Pool 占可用内存 70-80% |
| 四、MySQL 主从复制 | 异步 / 半同步 / 全同步 + Binlog 3 格式 | 推荐 ROW 格式 |
| 五、MySQL 高可用方案 | MHA / Orchestrator / MGR / Galera | MGR 是 MySQL 5.7+ 原生方案 |
| 六、MySQL 关键参数 | Buffer Pool / Redo Log / Binlog 刷盘 | 双 1 配置最安全 |
| 七、EXPLAIN 详解 | 12 种 type + FORMAT=JSON | 至少 range,严禁 ALL |
| 八、MySQL 8.0 新特性 | 窗口函数 / CTE / 原子 DDL / 隐藏索引 | 8.0+ 完整现代 SQL 支持 |
| 九、备份与恢复 | mysqldump / XtraBackup / PITR | 每周全量 + 每天增量 + 实时 binlog |
| 十、分区表 | RANGE / LIST / HASH / KEY | 分区键必须是主键一部分 |
| 十一、慢查询分析工具 | pt-query-digest / Performance Schema / sys schema | sys.statement_analysis |

---

## 一、MySQL 架构

MySQL 采用**两层架构**，Server 层与存储引擎层分离。

### Server 层

| 组件 | 职责 |
|------|------|
| **连接器** | 建立连接、权限验证、线程管理（线程池） |
| **分析器** | 词法分析（识别关键字）+ 语法分析（检查语法） |
| **优化器** | 选择索引、决定 JOIN 顺序、生成执行计划 |
| **执行器** | 调用存储引擎接口执行 SQL |
| **查询缓存** | MySQL 8.0 前存在，因更新频繁效率低已移除 |

### 存储引擎层

负责数据的存储和提取，支持插件式切换。

```
客户端 → 连接器 → 分析器 → 优化器 → 执行器 → 存储引擎 → 磁盘
                              ↓
                         查询缓存（8.0 前）
```

---

## 二、存储引擎对比

| 特性 | InnoDB | MyISAM | Memory | Archive |
|------|--------|--------|--------|---------|
| **事务** | ✅ 支持 | ❌ | ❌ | ❌ |
| **锁粒度** | 行级锁 | 表级锁 | 表级锁 | 行级锁（仅 INSERT） |
| **外键** | ✅ 支持 | ❌ | ❌ | ❌ |
| **崩溃恢复** | ✅ 支持 | ❌ | ❌ | ❌ |
| **全文索引** | 5.6+ | ✅ | ❌ | ❌ |
| **MVCC** | ✅ | ❌ | ❌ | ❌ |
| **主要用途** | 通用、事务安全 | 读密集、静态数据 | 临时数据 | 归档日志 |

> **默认选择 InnoDB**，除非有非常特殊的理由。

```sql
-- 查看表引擎
SHOW CREATE TABLE users;

-- 修改引擎
ALTER TABLE users ENGINE = InnoDB;
```

---

## 三、InnoDB 内部机制

### 1. Buffer Pool（缓冲池）

Buffer Pool 是 InnoDB 的核心组件，位于内存中，缓存磁盘数据页。

```
读操作：磁盘 → 加载到 Buffer Pool → 返回数据（后续读直接命中内存）
写操作：修改 Buffer Pool 中的页 → 刷盘（异步）
```

| 参数 | 默认值 | 建议 |
|------|--------|------|
| `innodb_buffer_pool_size` | 128MB | 可用内存的 **70~80%** |
| `innodb_buffer_pool_instances` | 1（<1GB）/ 8（>1GB） | 多实例减少锁竞争 |

**LRU 改进**：InnoDB 将 Buffer Pool 的 LRU 链表分为 **young 区**和 **old 区**，防止全表扫描冲刷热点数据。

### 2. Change Buffer（变更缓冲）

当修改非聚簇索引（二级索引）的数据页不在 Buffer Pool 中时，InnoDB 不立即读磁盘，而是将修改缓存在 Change Buffer 中，后续访问该页时再合并。

**适用场景**：非唯一二级索引的 INSERT/UPDATE/DELETE。

### 3. 日志系统

InnoDB 使用多种日志协同工作：

| 日志 | 位置 | 作用 | 保证的 ACID |
|------|------|------|------------|
| **Redo Log** | InnoDB 引擎层 | 物理日志，记录"某页某偏移的数据被改成了什么" | 持久性 (D) |
| **Undo Log** | InnoDB 引擎层 | 逻辑日志，记录"某行数据修改前的值" | 原子性 (A) |
| **Binlog** | Server 层 | 逻辑日志，记录所有修改操作（用于复制和恢复） | 数据恢复和主从复制 |

#### Redo Log 写入流程（WAL）

```
事务执行 → 修改 Buffer Pool → 写 Redo Log（prepare 状态）→ binlog 写入 → Redo Log 改为 commit 状态
```

这就是**两阶段提交**，保证 Redo Log 和 Binlog 的一致性。

#### Redo Log 结构

Redo Log 是**固定大小的环形文件**（如 2 个文件，各 1GB），循环写入。

```
[文件1] [文件2]
  ↓write_pos        ↓checkpoint
  |---已写---|---可写---|
```

| 参数 | 说明 |
|------|------|
| `innodb_log_file_size` | 单个 Redo Log 文件大小 |
| `innodb_log_files_in_group` | Redo Log 文件个数 |
| `innodb_flush_log_at_trx_commit` | 刷盘策略（见下表） |

| `innodb_flush_log_at_trx_commit` | 行为 | 性能 | 安全性 |
|:---:|------|:---:|:---:|
| **0** | 每秒刷盘 | 最高 | 崩溃丢失 1 秒数据 |
| **1** | 每次提交都 fsync 到磁盘 | 最低 | 不丢数据（推荐） |
| **2** | 每次提交写到 OS 缓存，每秒 fsync | 中等 | OS 崩溃可能丢失 |

### 4. Double Write Buffer（双写缓冲）

防止**部分页写入**（Partial Page Write）导致数据损坏。InnoDB 先将页写入 Double Write Buffer（2MB），再写入数据文件。如果写入过程中崩溃，可以从 Double Write Buffer 恢复完整页。

---

## 四、MySQL 主从复制

### 1. 复制原理

```
Master                          Slave
┌─────────┐                    ┌─────────┐
│ 写操作   │                    │ IO 线程  │ ← 拉取 binlog
│    ↓     │   binlog 传输      │    ↓     │
│ binlog  │ ──────────────→   │ relay log │
│    ↓     │                    │    ↓     │
│ 磁盘    │                    │ SQL 线程 │ → 重放 relay log
└─────────┘                    │    ↓     │
                               │ 磁盘    │
                               └─────────┘
```

**三个线程**：
- **Master**：Binlog Dump 线程，发送 binlog 事件
- **Slave IO 线程**：拉取 binlog 写入 relay log
- **Slave SQL 线程**：读取 relay log 并重放

### 2. 复制模式

| 模式 | 说明 | 延迟 |
|------|------|:---:|
| **异步复制** | Master 写完 binlog 立即返回，不等 Slave | 最低 |
| **半同步复制** | Master 等待至少一个 Slave 确认收到 | 中等 |
| **全同步复制** | 所有 Slave 都执行完毕才返回（Galera/MGR） | 最高 |

### 3. Binlog 格式

| 格式 | 说明 | 优缺点 |
|------|------|--------|
| **STATEMENT** | 记录原始 SQL | 数据量小，但某些函数（NOW()）会导致不一致 |
| **ROW** | 记录每行数据变化 | 数据一致性好，但数据量大 |
| **MIXED** | 自动选择 STATEMENT 或 ROW | 折中方案 |

> **推荐 ROW 格式**，保证主从数据一致性。

### 4. 读写分离

```
应用层 → 读写分离中间件（如 ShardingSphere、ProxySQL）
           ├── 写请求 → Master
           └── 读请求 → Slave1 / Slave2（负载均衡）
```

注意**主从延迟**问题：写入后立即读取可能读到旧数据。解决方案：
- 关键业务强制读主库
- 使用半同步复制减少延迟

---

## 五、MySQL 高可用方案

| 方案 | 说明 | 适用场景 |
|------|------|---------|
| **主从 + 手动切换** | 主库故障后手动提升从库 | 简单场景 |
| **MHA** | 自动检测主库故障并切换 | 中等规模 |
| **Orchestrator** | 拓扑管理 + 自动故障转移 | 大规模集群 |
| **MGR（Group Replication）** | MySQL 原生多主/单主复制 | MySQL 5.7+ |
| **Galera Cluster** | 多主同步复制（Percona/MariaDB） | 强一致性需求 |

---

## 六、MySQL 关键参数

| 参数 | 说明 | 建议值 |
|------|------|--------|
| `innodb_buffer_pool_size` | InnoDB 缓冲池大小 | 可用内存 70~80% |
| `innodb_flush_log_at_trx_commit` | Redo Log 刷盘策略 | 1（最安全） |
| `sync_binlog` | Binlog 刷盘频率 | 1（每次事务刷盘） |
| `innodb_log_file_size` | Redo Log 文件大小 | 256MB~1GB |
| `max_connections` | 最大连接数 | 根据业务调整 |
| `innodb_io_capacity` | 磁盘 IOPS | SSD: 2000+ |

> **双 1 配置**(`innodb_flush_log_at_trx_commit=1` + `sync_binlog=1`)是保证数据不丢失的最安全配置,适用于金融级场景。

---

## 七、EXPLAIN 详解

### 1. EXPLAIN 12 种 type 值(从优到劣)

| type | 含义 | 性能 |
|------|------|------|
| `system` | 表只有一行(系统表) | ⭐⭐⭐⭐⭐ |
| `const` | 主键/唯一索引等值查询,只匹配 1 行 | ⭐⭐⭐⭐⭐ |
| `eq_ref` | JOIN 中,主键/唯一索引关联,每行 1 次匹配 | ⭐⭐⭐⭐ |
| `ref` | 非唯一索引等值查询 | ⭐⭐⭐ |
| `range` | 索引范围扫描(`>`, `<`, `BETWEEN`, `IN`) | ⭐⭐⭐ |
| `index` | 全索引扫描(扫完整个索引树) | ⭐⭐ |
| `ALL` | **全表扫描**(最差) | ⭐ |

> **优化目标**:**至少达到 `range` 级别**,严禁出现 `ALL`(全表扫描)。

### 2. EXPLAIN FORMAT=JSON

```sql
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE email = 'a@b.com';
```

JSON 格式提供:
- 实际成本估算(`query_block.cost_info.query_cost`)
- 是否使用临时表(`temporary_table`)
- 排序方式(`sort_using_filesort`)

### 3. EXPLAIN 关键字段速查

| 字段 | 关注点 |
|------|--------|
| `type` | 至少 `range`,严禁 `ALL` |
| `key` | 实际使用的索引(NULL = 全表扫描) |
| `key_len` | 索引使用长度(可判断联合索引用了几列) |
| `rows` | 预估扫描行数 |
| `Extra` | `Using filesort`/`Using temporary` 需优化 |

---

## 八、MySQL 8.0 新特性

| 特性 | 说明 | 价值 |
|------|------|------|
| **窗口函数** | ROW_NUMBER/RANK/LAG/LEAD 等 | 复杂分析查询 |
| **CTE (WITH)** | 公用表表达式,替代嵌套子查询 | 可读性 + 性能 |
| **原子 DDL** | DDL 操作要么全成要么全败 | 元数据一致性 |
| **降序索引** | 真正支持 DESC 索引 | 排序性能 |
| **JSON 增强** | `JSON_TABLE`、`->>` 运算符 | 半结构化数据 |
| **隐藏索引** | 索引软删除,验证后再物理删除 | 安全调优 |
| **Resource Group** | 将线程绑定到特定 CPU | 高并发控制 |
| **EXPLAIN ANALYZE** | 真实执行统计 | 性能调优 |

---

## 九、备份与恢复

### 1. 逻辑备份(mysqldump)

```bash
# 备份整个库
mysqldump -u root -p mydb > mydb.sql

# 备份单表
mysqldump -u root -p mydb users > users.sql

# 备份时加一致性快照(--single-transaction)
mysqldump --single-transaction -u root -p mydb > mydb.sql

# 恢复
mysql -u root -p mydb < mydb.sql
```

**优点**:跨版本、跨平台、可读。
**缺点**:大库慢(数小时)。

### 2. 物理备份(Percona XtraBackup)

```bash
# 全量备份
xtrabackup --backup --target-dir=/backup/full

# 恢复
xtrabackup --prepare --target-dir=/backup/full
xtrabackup --copy-back --target-dir=/backup/full
```

**优点**:热备份、速度快(GB/s)、支持增量。
**缺点**:仅限 InnoDB,跨平台差。

### 3. 基于时间点恢复(PITR)

```bash
# 1. 恢复全量备份
xtrabackup --prepare --target-dir=/backup/full

# 2. 应用 binlog 到指定时间点
mysqlbinlog --stop-datetime="2026-06-09 14:00:00" \
    /var/lib/mysql/binlog.000001 | mysql -u root -p
```

### 4. 备份策略矩阵

| 备份类型 | 频率 | 保留 | RPO(数据丢失) | RTO(恢复时间) |
|---------|------|------|--------------|--------------|
| 全量 | 每周 | 4 周 | 数小时 | 数小时 |
| 增量 | 每天 | 7 天 | 数小时 | 较快 |
| Binlog | 实时 | 7 天 | 接近 0 | 中等 |

---

## 十、分区表

当单表数据量超过 5000 万行,考虑使用 MySQL **分区表**(应用层透明)。

### 1. 4 种分区方式

| 分区类型 | 适用 | 示例 |
|---------|------|------|
| **RANGE** | 按连续区间 | 按时间、按 ID 区间 |
| **LIST** | 按枚举值 | 按地区(华东/华南/华北) |
| **HASH** | 按哈希值均匀分布 | 按 user_id % 4 |
| **KEY** | 类似 HASH,MySQL 自管理 | 按主键哈希 |

### 2. RANGE 分区实战

```sql
CREATE TABLE orders (
    id BIGINT,
    created_at DATETIME,
    amount DECIMAL(10,2)
)
PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION pmax  VALUES LESS THAN MAXVALUE
);
```

### 3. 注意事项

- 分区键必须是**主键或唯一键**的一部分
- 单表最多 **8192 个分区**
- 性能提升主要在**范围查询**(配合 WHERE 分区键)
- **慎用**:JOIN 时分区键不对齐会导致全表扫描

---

## 十一、慢查询分析工具

### 1. pt-query-digest(Percona Toolkit)

业界最常用的 MySQL 慢查询分析工具,生成可读报告。

```bash
# 分析慢查询日志
pt-query-digest /var/lib/mysql/slow.log > digest_report.txt

# 直接分析正在运行的 MySQL
pt-query-digest --processlist h=localhost,u=root,p=password

# 过滤特定时间范围
pt-query-digest --since '2026-06-08' --until '2026-06-09' /var/lib/mysql/slow.log
```

报告输出关键信息:
- 总查询数、唯一查询数
- 各查询的**响应时间分布**(95% / 99%)
- 各查询的**扫描行数**与**返回行数**
- TOP 10 慢查询详情

### 2. Performance Schema

MySQL 内置的性能监控框架,8.0 起显著增强。

```sql
-- 启用
UPDATE performance_schema.setup_consumers
SET enabled = 'YES' WHERE name LIKE 'events_statements%';

-- 查询最耗时的 SQL
SELECT digest_text, count_star, sum_timer_wait/1e9 AS total_ms
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC LIMIT 10;
```

### 3. sys schema(MySQL 5.7+)

基于 Performance Schema 的可读视图,简化查询。

```sql
-- 查看最慢的 SQL(按平均耗时)
SELECT query, db, exec_count, avg_latency
FROM sys.statement_analysis
LIMIT 10;

-- 查看冗余索引
SELECT * FROM sys.schema_redundant_indexes;

-- 查看未使用的索引
SELECT * FROM sys.schema_unused_indexes;
```

---

## 🔗 相关章节

- [数据库基础知识](../01-fundamentals/README.md) — 数据库核心概念
- [SQL](../02-sql/README.md) — 慢查询分析与 EXPLAIN
- [事务与并发控制](../03-transaction/README.md) — InnoDB 事务实现
- [索引](../04-index/README.md) — InnoDB 索引底层结构
- [缓存](../06-cache/README.md) — MySQL 查询缓存(8.0 已移除)
- [数据库连接池](../09-connection-pool/README.md) — MySQL 连接池配置

---

## 📊 本节统计

- **leaf README 数**：1（本文即为分类 leaf，单 README 长文聚合 11 主题）
- **本节主题数**：11（架构、引擎对比、InnoDB 内部、主从复制、高可用、关键参数、EXPLAIN、8.0 新特性、备份恢复、分区表、慢查询工具）
- **frontmatter 状态**：✅ 已对齐 CONTRIBUTING §12 标准（summary ≤ 80 字 / type=index）
- **统计口径**：本目录无嵌套子目录，所有内容聚合在本 README；最后更新 2026-07-01

---

## 📖 参考资料

- [MySQL 8.0 Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)
- [MySQL InnoDB Architecture (官方图解)](https://dev.mysql.com/doc/refman/8.0/en/innodb-architecture.html)
- [High Performance MySQL](https://www.oreilly.com/library/view/high-performance-mysql/9780596101718/) — O'Reilly 经典
- [MySQL 8.0 新特性官方说明](https://dev.mysql.com/doc/refman/8.0/en/mysql-nutshell.html)

---

← [返回 03.database 主模块](../README.md)