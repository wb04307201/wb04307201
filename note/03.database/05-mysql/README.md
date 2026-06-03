# MySQL

MySQL 是最流行的开源关系型数据库，由 MySQL AB 开发，现属 Oracle 公司。它是 LAMP/LNMP 架构的核心组件。

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

> **双 1 配置**（`innodb_flush_log_at_trx_commit=1` + `sync_binlog=1`）是保证数据不丢失的最安全配置，适用于金融级场景。
