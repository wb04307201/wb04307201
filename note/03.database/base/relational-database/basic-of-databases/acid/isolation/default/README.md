# 常见数据库的默认隔离级别

| 数据库系统                                | 默认隔离级别                  | 说明                                                      |
|--------------------------------------|-------------------------|---------------------------------------------------------|
| **MySQL** (InnoDB)                   | `REPEATABLE READ`       | 保证可重复读，但可能遇到幻读（InnoDB 通过 MVCC + 间隙锁解决幻读问题）。             |
| **PostgreSQL**                       | `READ COMMITTED`        | 仅能读取已提交的数据，避免脏读，但可能遇到不可重复读和幻读。                          |
| **Oracle**                           | `READ COMMITTED`        | 与 PostgreSQL 相同，默认避免脏读，但不解决不可重复读和幻读。                    |
| **SQL Server**                       | `READ COMMITTED`        | 默认使用行锁避免脏读，但可能遇到不可重复读；可通过 `READ COMMITTED SNAPSHOT` 优化。 |
| **SQLite**                           | `SERIALIZABLE`          | 通过全局写锁实现，写操作时完全阻塞读操作，保证最高隔离性（但并发性能低）。                   |
| **MariaDB**                          | `REPEATABLE READ`       | 与 MySQL InnoDB 一致。                                      |
| **DB2**                              | `CURSOR STABILITY` (CS) | 类似 `READ COMMITTED`，但锁定当前游标行，避免脏读。                      |
| **H2 Database** (2.x)                | `READ_COMMITTED`        | 轻量级 Java 嵌入式数据库，默认避免脏读，但可能遇到不可重复读和幻读。                   |
| **人大金仓 (KingbaseES)** V8             | `READ COMMITTED`        | 深度兼容 PostgreSQL，行为与 PG 一致；国产化场景需注意锁优化策略。                |
| **高斯数据库 (GaussDB)** (openGauss 5.0+) | `READ COMMITTED`        | 兼容 PG 生态，但通过 **AI 优化器** 动态调整锁粒度，减少幻读概率。                 |


---

## ⚠️ 关键注意事项
1. **MySQL 的特殊性**：  
   虽然 InnoDB 默认是 `REPEATABLE READ`，但通过 **间隙锁（Gap Lock）** 在特定场景下解决了幻读问题，实际隔离强度接近 `SERIALIZABLE`（但并非完全等价）。

2. **隔离级别可配置**：  
   所有数据库均允许通过配置或命令覆盖默认值，例如：
   ```sql
   -- MySQL/PostgreSQL 修改会话级别
   SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
   
   -- SQL Server 启用快照隔离
   ALTER DATABASE [DB] SET READ_COMMITTED_SNAPSHOT ON;
   ```

3. **分布式数据库差异**：
    - **TiDB**：默认 `REPEATABLE READ`（实际是 `SNAPSHOT ISOLATION`，等价于 Oracle 的 `SERIALIZABLE`）。
    - **CockroachDB**：默认 `SNAPSHOT ISOLATION`（强于 `REPEATABLE READ`）。

---

## 🔍 如何查看当前隔离级别？
- **MySQL**:
  ```sql
  SELECT @@transaction_isolation;  -- MySQL 8.0+
  SELECT @@tx_isolation;           -- 旧版本
  ```
- **PostgreSQL**:
  ```sql
  SHOW default_transaction_isolation;
  ```
- **SQL Server**:
  ```sql
  DBCC USEROPTIONS;  -- 查看当前会话设置
  ```
- **H2**:
  ```sql
  SELECT SESSION_PROPERTY('transactionIsolation'); -- 返回 2（READ_COMMITTED）
  ```
  - 仅在 **服务器模式（Server Mode）** 支持完整事务隔离，嵌入式模式（In-Memory）默认简化锁机制。
  - 通过 `-Dh2.lockMode=1` 参数可强制启用 `SERIALIZABLE`（但性能下降显著）。
- **KingbaseES**:
  ```sql
  SHOW default_transaction_isolation; -- 与 PostgreSQL 完全兼容
  ```
  - 虽默认 `READ COMMITTED`，但 **V8R6+ 版本** 新增 `READ COMMITTED FOR SHARE` 模式（自动对读操作加共享锁），减少幻读。
  - 金融级场景推荐手动设置 `SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE;`。
- **GaussDB**:
  ```sql
  SHOW default_transaction_isolation; -- 查看当前级别
  SHOW enable_default_ustore;          -- 检查是否启用 Ustore 引擎（影响隔离实现）
  ```
  - **GaussDB(for openGauss)**：默认 `READ COMMITTED`（与 PG 一致），但通过 **多版本并发控制（MVCC）+ 行级锁优化**，在 RR 级别下实际可避免幻读。
  - **GaussDB 分布式版**：默认 `SNAPSHOT ISOLATION`（强于 `REPEATABLE READ`），需确认部署模式。

---

## 💡 建议
- **应用层适配**：  
  高并发场景优先使用 `READ COMMITTED`（如 PostgreSQL/Oracle 默认），避免锁竞争；  
  金融级强一致性场景需手动提升至 `SERIALIZABLE`（但性能显著下降）。
- **验证实际行为**：  
  默认隔离级别可能随版本变化（例如 MySQL 5.7 与 8.0 行为一致，但与早期版本不同），**务必查阅官方最新文档**。

> 🌐 **官方文档参考**：  
> [MySQL 8.0 事务隔离](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html) |  
> [PostgreSQL 16 隔离级别](https://www.postgresql.org/docs/16/transaction-iso.html) |  
> [SQL Server 2022 隔离级别](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver16) |  
> [H2 2.2 事务隔离](https://h2database.com/html/advanced.html#transaction_isolation) |  
> [人大金仓 V8R6 事务管理](https://help.kingbase.com.cn/doc-view-11121.html) |  
> [GaussDB openGauss 5.0 隔离级别](https://docs.gaussdb.com/public/5.0/zh/docs/2developer/2_3_2_15_2.html) |  
