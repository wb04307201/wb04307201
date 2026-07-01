# 事务与并发控制

> 事务是数据库操作的最小逻辑单元,保证一组操作要么全部成功要么全部失败;并发控制解决多个事务同时执行时的数据一致性问题,核心机制是 ACID + 锁 + MVCC。

> 最后更新: 2026-06-09

## 目录

- [一、ACID 特性](#一acid-特性)
- [二、并发问题](#二并发问题)
- [三、事务隔离级别](#三事务隔离级别)
- [四、锁机制](#四锁机制)
- [五、MVCC(多版本并发控制)](#五mvcc多版本并发控制)
- [六、锁兼容矩阵](#六锁兼容矩阵)

---
## 引言：反直觉代码

事务与并发控制 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、ACID 特性

| 特性 | 英文 | 说明 | 实现机制 |
|------|------|------|---------|
| **原子性** | Atomicity | 事务中的操作要么全做，要么全不做 | Undo Log（回滚日志） |
| **一致性** | Consistency | 事务前后数据库处于合法状态 | 约束检查 + 原子性 + 隔离性共同保障 |
| **隔离性** | Isolation | 并发事务互不干扰 | 锁机制 + MVCC |
| **持久性** | Durability | 事务提交后数据永久保存 | Redo Log（重做日志）+ WAL |

### 原子性详解

事务失败时，通过 Undo Log 恢复到事务开始前的状态。

```
事务开始 → 操作A（记录Undo Log）→ 操作B（记录Undo Log）→ 操作B失败 → 通过Undo Log回滚操作A → 事务回滚完成
```

### 持久性详解

事务提交时，通过 **WAL（Write-Ahead Logging）** 机制：先写 Redo Log 到磁盘，再确认事务提交。即使数据库崩溃，也能通过 Redo Log 恢复。

```
事务提交 → 写 Redo Log → fsync 刷盘 → 返回提交成功
            ↓（崩溃恢复）
         重放 Redo Log → 数据恢复
```

---

## 二、并发问题

多个事务同时操作时，如果隔离不当，会出现以下问题：

| 问题 | 说明 | 示例 |
|------|------|------|
| **脏读** | 读到其他事务**未提交**的数据 | A 改余额为 200（未提交），B 读到 200，A 回滚后余额恢复为 100 |
| **不可重复读** | 同一事务内多次读取结果不同 | A 读余额为 100，B 改为 200 并提交，A 再读变成 200 |
| **幻读** | 同一事务内多次查询返回不同行数 | A 查"年龄>30"有 10 条，B 插入一条 35 岁的并提交，A 再查变成 11 条 |

### 不可重复读 vs 幻读

| 区别 | 不可重复读 | 幻读 |
|------|-----------|------|
| 侧重点 | **数据值**被修改 | **数据行数**发生变化 |
| 触发操作 | 其他事务 UPDATE | 其他事务 INSERT / DELETE |

---

## 三、事务隔离级别

SQL 标准定义了四种隔离级别，从低到高：

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|---------|:----:|:---------:|:----:|:----:|
| **读未提交** READ UNCOMMITTED | ❌ 会发生 | ❌ 会发生 | ❌ 会发生 | 最高 |
| **读已提交** READ COMMITTED | ✅ 解决 | ❌ 会发生 | ❌ 会发生 | 较高 |
| **可重复读** REPEATABLE READ | ✅ 解决 | ✅ 解决 | ❌ 会发生* | 一般 |
| **串行化** SERIALIZABLE | ✅ 解决 | ✅ 解决 | ✅ 解决 | 最低 |

> *MySQL InnoDB 的可重复读通过 **Next-Key Lock**（MVCC + 间隙锁）在很大程度上避免了幻读。

### 各数据库默认隔离级别

| 数据库 | 默认隔离级别 | 说明 |
|--------|------------|------|
| MySQL (InnoDB) | REPEATABLE READ | 通过 MVCC + 间隙锁解决幻读 |
| PostgreSQL | READ COMMITTED | 仅避免脏读 |
| Oracle | READ COMMITTED | 仅避免脏读 |
| SQL Server | READ COMMITTED | 支持 READ_COMMITTED_SNAPSHOT 优化 |
| SQLite | SERIALIZABLE | 全局写锁，并发性能低 |

### 查看与修改隔离级别

```sql
-- MySQL 查看
SELECT @@transaction_isolation;

-- MySQL 修改会话级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- PostgreSQL 查看
SHOW default_transaction_isolation;
```

---

## 四、锁机制

### 1. 按锁粒度分类

| 粒度 | 说明 | 适用场景 |
|------|------|---------|
| **表级锁** | 锁定整张表 | 批量操作、读多写少 |
| **行级锁** | 锁定单行或多行 | 高并发读写 |
| **页级锁** | 锁定数据页（介于表级和行级之间） | 特定场景（如 BDB 引擎） |

### 2. 按锁类型分类

| 锁类型 | 说明 |
|--------|------|
| **共享锁（S 锁/读锁）** | 允许多事务读，禁止写。`SELECT ... LOCK IN SHARE MODE` |
| **排他锁（X 锁/写锁）** | 独占资源，禁止其他读写。`SELECT ... FOR UPDATE` |
| **意向锁（IS/IX）** | 表级锁，表明事务"意向"在行/页上加锁 |
| **更新锁（U 锁）** | 准备更新但未提交，防止死锁（SQL Server） |

### 3. InnoDB 行锁算法

| 锁 | 说明 | 示例 |
|----|------|------|
| **Record Lock** | 锁定单行记录 | 锁定 `id = 1` 这一行 |
| **Gap Lock** | 锁定记录间的间隙，防止幻读 | 锁定 (1, 5) 之间的间隙 |
| **Next-Key Lock** | Record Lock + Gap Lock，默认算法 | 锁定 (1, 5] |
| **Insert Intention Lock** | 特殊间隙锁，提高 INSERT 并发 | 插入操作等待间隙锁释放 |

### 4. 乐观锁与悲观锁

| 特性 | 悲观锁 | 乐观锁 |
|------|--------|--------|
| 假设 | 冲突频繁 | 冲突较少 |
| 实现 | 数据库行锁/表锁（`FOR UPDATE`） | 版本号 / 时间戳（应用层） |
| 适用场景 | 写多读少 | 读多写少 |
| 缺点 | 并发度低，可能死锁 | 冲突时需重试 |

**乐观锁实现示例**：

```sql
-- 方案1：版本号
UPDATE accounts SET balance = 200, version = version + 1
WHERE id = 1 AND version = 3;
-- 如果 affected rows = 0，说明版本冲突，需重试

-- 方案2：CAS 比较
UPDATE accounts SET balance = 200
WHERE id = 1 AND balance = 100;
```

### 5. 死锁

**产生条件**：互斥 + 占有并等待 + 不可剥夺 + 环路等待。

**解决方案**：

| 方案 | 说明 |
|------|------|
| 顺序封锁 | 所有事务按相同顺序获取锁 |
| 超时回滚 | InnoDB 默认 50 秒超时，自动回滚 |
| 等待图法 | 检测事务等待环路，回滚代价最小的事务 |

```sql
-- 查看当前死锁信息（MySQL）
SHOW ENGINE INNODB STATUS;
```

---

## 五、MVCC（多版本并发控制）

MVCC（Multiversion Concurrency Control）通过维护数据的历史版本，实现**读写不阻塞**的高并发访问。

### 1. 核心思想

- **版本化数据**：每次修改不覆盖原数据，而是创建新版本，旧版本通过回滚指针链接
- **非阻塞读**：读操作（快照读）通过版本链找到可见版本，无需加锁
- **当前读加锁**：`SELECT ... FOR UPDATE` 等当前读操作仍需加锁

### 2. InnoDB 实现

#### 隐藏列

| 列 | 说明 |
|----|------|
| `DB_TRX_ID` | 最后修改该行的事务 ID |
| `DB_ROLL_PTR` | 回滚指针，指向 Undo Log 中的旧版本 |
| `DB_ROW_ID` | 无主键时的隐含自增行 ID |

#### 版本链

```
当前行（trx_id=100）
    ↓ roll_ptr
旧版本（trx_id=80）
    ↓ roll_ptr
更旧版本（trx_id=50）
    ↓ roll_ptr
...
```

#### Read View（读视图）

事务进行快照读时生成 Read View，包含：

| 字段 | 说明 |
|------|------|
| `m_ids` | 生成 Read View 时所有活跃事务 ID 列表 |
| `min_trx_id` | `m_ids` 中最小值 |
| `max_trx_id` | 生成 Read View 时系统即将分配的最大事务 ID |
| `creator_trx_id` | 创建该 Read View 的事务 ID |

**可见性判断规则**：

| 条件 | 结论 |
|------|------|
| `trx_id < min_trx_id` | 可见（事务已提交） |
| `trx_id >= max_trx_id` | 不可见（事务在 Read View 之后才开始） |
| `trx_id` 在 `m_ids` 中 | 不可见（事务还未提交） |
| `trx_id` 不在 `m_ids` 中 | 可见（事务已提交） |
| 以上都不满足 | 沿版本链继续查找 |

### 3. RC 与 RR 的区别

| 隔离级别 | Read View 生成时机 |
|---------|-------------------|
| **READ COMMITTED** | 每次快照读都重新生成 Read View |
| **REPEATABLE READ** | 事务第一次快照读时生成，整个事务期间复用 |

这解释了为什么 RR 能避免不可重复读——整个事务期间看到的都是同一个快照。

### 4. MVCC 的优缺点

| 优点 | 缺点 |
|------|------|
| 读写不阻塞，高并发 | 需要维护多版本数据，占用额外存储 |
| 避免脏读、不可重复读 | 需要定期清理旧版本（purge） |
| 支持时间点一致性读 | 实现复杂度高 |

---

## 六、锁兼容矩阵

| | S（共享） | X（排他） | IS（意向共享） | IX（意向排他） |
|---|:---:|:---:|:---:|:---:|
| **S** | ✅ | ❌ | ✅ | ❌ |
| **X** | ❌ | ❌ | ❌ | ❌ |
| **IS** | ✅ | ❌ | ✅ | ✅ |
| **IX** | ❌ | ❌ | ✅ | ✅ |

> ✅ = 兼容(可以同时持有),❌ = 冲突(需要等待)

---

## 七、死锁实战与排查

### 1. 经典死锁场景:账户转账

```sql
-- 事务 A
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- 锁 id=1
UPDATE accounts SET balance = balance + 100 WHERE id = 2;  -- 等待 id=2 的锁

-- 事务 B(同时)
BEGIN;
UPDATE accounts SET balance = balance - 50 WHERE id = 2;   -- 锁 id=2
UPDATE accounts SET balance = balance + 50 WHERE id = 1;   -- 等待 id=1 的锁

-- → 死锁!InnoDB 检测到后回滚代价小的事务
```

### 2. 查看最近一次死锁日志

```sql
SHOW ENGINE INNODB STATUS;
```

输出关键片段(简化):

```
LATEST DETECTED DEADLOCK
------------------------
2026-06-09 14:23:45 0x7f8b8c000700
*** (1) TRANSACTION:
TRANSACTION 12345, ACTIVE 0.1 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1136, 2 row lock(s)
MySQL thread id 1, query id 10 ... updating
UPDATE accounts SET balance = balance + 100 WHERE id = 2

*** (2) TRANSACTION:
TRANSACTION 12346, ACTIVE 0.1 sec starting index read
UPDATE accounts SET balance = balance + 100 WHERE id = 1

*** WE ROLL BACK TRANSACTION (1)
```

### 3. 死锁预防

| 策略 | 说明 |
|------|------|
| **统一加锁顺序** | 多表操作按固定顺序(如按 id 升序) |
| **单事务行数限制** | `LIMIT 1000`,避免大事务 |
| **降低隔离级别** | RC 比 RR 减少间隙锁 |
| **乐观锁替代** | 版本号控制,适合冲突少的场景 |
| **加锁超时** | `innodb_lock_wait_timeout = 5` 默认 50s |

### 4. 业务层处理死锁

```java
@Transactional
public void transfer() {
    try {
        // 业务逻辑
    } catch (CannotAcquireLockException e) {
        // 死锁,InnoDB 已自动回滚,业务重试
        retry();
    }
}
```

---

## 八、Spring 事务传播行为

`@Transactional` 提供 7 种传播行为,控制事务边界与嵌套:

| 传播行为 | 说明 | 适用场景 |
|---------|------|---------|
| **REQUIRED**(默认) | 沿用当前事务,无则新建 | 90% 业务场景 |
| **REQUIRES_NEW** | 无论是否有事务,都开新事务 | 日志记录、审计独立保存 |
| **NESTED** | 嵌套子事务(SAVEPOINT) | 部分回滚 |
| **SUPPORTS** | 有事务则加入,无则非事务执行 | 查询方法 |
| **NOT_SUPPORTED** | 挂起当前事务,以非事务执行 | 不需要事务的调用 |
| **MANDATORY** | 必须在事务中,否则抛异常 | 强制要求 |
| **NEVER** | 必须在非事务中,否则抛异常 | 反向强制 |

### 经典场景:日志独立保存

```java
@Service
public class OrderService {
    @Autowired LogService logService;
    
    @Transactional  // 主事务
    public void createOrder() {
        // 订单创建
        logService.saveLog();  // 独立事务,不受主事务回滚影响
    }
}

@Service
public class LogService {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveLog() {
        // 即使主事务回滚,日志也保留
    }
}
```

---

## 九、Savepoint(保存点)

部分回滚能力,在事务内部设置"还原点"。

```sql
BEGIN;

INSERT INTO users (name) VALUES ('Alice');
SAVEPOINT sp1;

INSERT INTO users (name) VALUES ('Bob');
SAVEPOINT sp2;

INSERT INTO users (name) VALUES ('Charlie');

-- 回滚到 sp2(撤销 Charlie,但保留 Alice 和 Bob)
ROLLBACK TO SAVEPOINT sp2;

-- 提交 Alice 和 Bob
COMMIT;
```

**适用场景**:
- 批量处理,部分失败时只回滚失败部分
- 复杂业务的多步处理
- 测试与回滚模拟

---

## 十、隔离级别选型建议

| 业务场景 | 推荐隔离级别 | 原因 |
|---------|-----------|------|
| **金融交易、支付** | SERIALIZABLE 或 RR + 乐观锁 | 强一致,绝对避免幻读 |
| **电商订单** | RR(InnoDB 默认) | 平衡一致性与并发 |
| **社交、内容平台** | RC | 高并发,可接受少量不可重复读 |
| **统计报表** | RC + 物化视图 | 读多写少,无需最强隔离 |
| **批量后台任务** | RC + 短事务 | 避免长事务阻塞 |

> **生产实践**:**80% 业务使用默认 RR 即可**,只在金融、库存等强一致场景显式升到 SERIALIZABLE。

---

## 相关章节

- [数据库基础知识](../01-fundamentals/README.md) — 完整性约束
- [SQL](../02-sql/README.md) — 合理使用事务的 8 条建议
- [索引](../04-index/README.md) — 索引与行锁的关系
- [MySQL](../05-mysql/README.md) — InnoDB 内部机制

## 参考资料

- [MySQL 8.0 InnoDB Locking and Transaction Model](https://dev.mysql.com/doc/refman/8.0/en/innodb-locking-transaction-model.html)
- [MySQL InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.0/en/innodb-multi-versioning.html)
- [A Critique of ANSI SQL Isolation Levels - Microsoft Research](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-95-51.pdf)
- [Java Concurrency in Practice - Chapter 9. 事务相关章节](https://jcip.net/)
