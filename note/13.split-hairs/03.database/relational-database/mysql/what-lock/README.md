# MySQL 什么情况下会锁表？

## 一、核心原理

MySQL 的锁行为由**存储引擎**（InnoDB/MyISAM）、**事务隔离级别**、**索引使用情况**和**SQL 语句类型**共同决定。理解"锁表"需要先厘清锁的粒度层次：

### 1. 锁的粒度层级（从细到粗）
- **行级锁（Row Lock）**：锁定单行或多行，并发度最高。InnoDB 通过索引项加锁实现，仅在使用索引时生效。
- **间隙锁（Gap Lock）**：锁定两个索引值之间的"空隙"，防止其他事务插入满足条件的新行（解决幻读问题）。仅在 `REPEATABLE READ` 隔离级别下生效。
- **临键锁（Next-Key Lock）**：行锁 + 间隙锁的组合，锁定范围是 `(前一个索引值, 当前索引值]`。InnoDB 在范围查询时的默认行为。
- **页级锁（Page Lock）**：锁定数据页（通常 16 KB），并发度中等。BDB 存储引擎使用，现代 MySQL 极少使用。
- **表级锁（Table Lock）**：锁定整张表，并发度最低。MyISAM 引擎的唯一选择，InnoDB 在特定场景下也会退化到此级别。

### 2. InnoDB vs MyISAM 的锁模型差异
| 特性 | InnoDB | MyISAM |
|------|--------|--------|
| 锁粒度 | 行级/表级 | 仅表级 |
| 事务支持 | ✅ 完整 ACID | ❌ 不支持 |
| 外键支持 | ✅ | ❌ |
| 并发性能 | 高（行锁） | 低（表锁） |
| 适用场景 | OLTP 高频读写 | 只读或批量加载 |

### 3. 锁退化的根本原因
InnoDB 的行锁依赖于**索引**。当 SQL 语句无法使用索引时，InnoDB 无法定位具体要锁定的行，只能升级为全表扫描并锁定所有行——这本质上等同于表锁。此外，某些 DDL 操作（如 `ALTER TABLE`）需要获取元数据锁（MDL），也会阻塞全表访问。

---

## 二、代码示例

以下实验演示各种锁表场景及验证方法：

```sql
-- ==================== 准备测试表 ====================
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    email VARCHAR(100),
    age INT,
    INDEX idx_email (email)
) ENGINE=InnoDB;

INSERT INTO users (name, email, age) VALUES
('Alice', 'alice@example.com', 25),
('Bob', 'bob@example.com', 30),
('Charlie', 'charlie@example.com', 35);

-- ==================== 场景1：无索引导致锁表 ====================
-- Session A: 对无索引列执行 FOR UPDATE（触发全表扫描）
START TRANSACTION;
SELECT * FROM users WHERE age = 30 FOR UPDATE;  -- age 无索引

-- Session B: 尝试更新任意行（即使不是 age=30 的行）
UPDATE users SET name = 'New Alice' WHERE id = 1;  -- BLOCKED! 被锁住

-- 原因：Session A 的全表扫描导致所有行被加 X 锁

-- ==================== 场景2：有索引时精准行锁 ====================
-- Session A: 对索引列执行 FOR UPDATE
START TRANSACTION;
SELECT * FROM users WHERE email = 'bob@example.com' FOR UPDATE;  -- 使用 idx_email

-- Session B: 更新其他行（不受影响）
UPDATE users SET name = 'New Alice' WHERE id = 1;  -- SUCCESS! 未被锁住

-- Session C: 更新同一行（被阻塞）
UPDATE users SET name = 'New Bob' WHERE id = 2;  -- BLOCKED!

-- ==================== 场景3：显式表锁 ====================
-- Session A: 获取写锁
LOCK TABLES users WRITE;

-- Session B: 任何读取都被阻塞
SELECT * FROM users;  -- BLOCKED!

-- Session A: 释放锁
UNLOCK TABLES;

-- ==================== 场景4：DDL 操作隐式锁表 ====================
-- Session A: 添加索引（需要 MDL 锁）
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Session B: 任何 DML 都被阻塞
UPDATE users SET name = 'Test' WHERE id = 1;  -- BLOCKED!

-- ==================== 场景5：间隙锁演示 ====================
-- 前提：隔离级别为 REPEATABLE READ
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Session A: 范围查询
START TRANSACTION;
SELECT * FROM users WHERE id > 2 FOR UPDATE;  -- 锁定 id=2,3 和间隙 (2, +∞)

-- Session B: 尝试插入新行到锁定范围
INSERT INTO users (id, name, email, age) VALUES (4, 'David', 'david@example.com', 40);
-- BLOCKED! 间隙锁阻止插入

-- Session A: 提交后 Session B 才能执行
COMMIT;

-- ==================== 监控锁状态 ====================
-- 查看当前锁等待
SELECT * FROM performance_schema.data_locks;
SELECT * FROM performance_schema.data_lock_waits;

-- 查看 InnoDB 状态（包含锁信息）
SHOW ENGINE INNODB STATUS\G

-- 查看事务列表
SELECT * FROM information_schema.INNODB_TRX;
```

---

## 三、常见陷阱

### 1. 误认为 `UPDATE` 一定只锁影响的行
```sql
-- 危险操作：age 无索引，实际锁住全表
UPDATE users SET name = 'New' WHERE age = 30;
```
即使 `WHERE` 条件只匹配一行，若过滤列无索引，InnoDB 会全表扫描并锁定所有行。**解决方案**：确保 `WHERE`/`JOIN` 中的列都有合适的索引。

### 2. 忽视隐式类型转换导致的索引失效
```sql
-- 假设 phone 是 VARCHAR 类型且有索引
SELECT * FROM users WHERE phone = 13800138000 FOR UPDATE;  -- 数字字面量

-- 结果：隐式类型转换导致索引失效，退化为全表锁
-- 正确写法
SELECT * FROM users WHERE phone = '13800138000' FOR UPDATE;  -- 字符串字面量
```

### 3. 大事务长时间持锁
```java
// 反模式：事务中包含远程调用
@Transactional
public void processOrder(Long orderId) {
    Order order = orderDao.findById(orderId);     // 锁定订单行
    httpClient.post("http://payment-service", ...); // HTTP 调用耗时 5 秒
    order.setStatus("PAID");
    orderDao.update(order);                        // 锁持有长达 5 秒+
}
```
**解决方案**：将远程调用移出事务边界，或使用异步事件驱动架构。

### 4. 死锁的产生与规避
```sql
-- Session A:                -- Session B:
START TRANSACTION;           START TRANSACTION;
UPDATE users SET name='A' WHERE id=1;  UPDATE users SET name='B' WHERE id=2;
UPDATE users SET name='A' WHERE id=2;  UPDATE users SET name='B' WHERE id=1;
-- 结果：双方互相等待对方持有的锁 → 死锁

-- InnoDB 自动检测死锁并回滚其中一个事务
-- ERROR 1213 (40001): Deadlock found when trying to get lock
```
**预防措施**：
- 统一加锁顺序（如始终按 id 从小到大更新）
- 设置合理的 `innodb_lock_wait_timeout`（默认 50 秒）
- 使用乐观锁（版本号机制）替代悲观锁

### 5. 主从复制中的锁问题
主库上的 `FOR UPDATE` 不会复制到从库，但若主库因锁等待超时回滚，从库可能已经执行了部分语句，导致主从不一致。**解决方案**：关键业务使用 `pt-heartbeat` 监控主从延迟。

---

## 四、最佳实践

### 1. 索引设计原则
- **等值查询优先**：为 `WHERE` 中的列建立精确匹配索引。
- **联合索引遵循最左前缀**：`(a, b, c)` 支持 `WHERE a=? AND b=?`，但不支持 `WHERE b=? AND c=?`。
- **覆盖索引避免回表**：索引包含查询所需的所有字段，减少二次查找。
- **定期分析索引使用率**：
  ```sql
  SELECT * FROM sys.schema_unused_indexes;  -- 未使用的索引
  SELECT * FROM sys.schema_redundant_indexes; -- 冗余索引
  ```

### 2. 事务最小化原则
```java
// ✅ 推荐：事务范围最小化
@Transactional
public void updateStatus(Long id, String status) {
    Order order = orderDao.findById(id);
    order.setStatus(status);
    orderDao.update(order);  // 事务仅包含必要的 DB 操作
}

// ❌ 不推荐：事务过大
@Transactional
public void processOrder(OrderRequest req) {
    validateRequest(req);       // 校验逻辑无需事务
    calculatePrice(req);        // 计算逻辑无需事务
    Order order = convert(req);
    orderDao.insert(order);     // 只有这一步需要事务
    sendNotification(order);    // 通知逻辑无需事务
}
```

### 3. 选择合适的隔离级别
| 隔离级别 | 锁行为 | 适用场景 |
|----------|--------|----------|
| READ COMMITTED | 仅锁定修改的行，无间隙锁 | 高并发 OLTP，允许幻读 |
| REPEATABLE READ | 行锁 + 间隙锁，防止幻读 | 默认选择，数据一致性要求高 |
| SERIALIZABLE | 所有读都加共享锁 | 极端一致性场景（极少用） |

```sql
-- 根据业务需求调整隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

### 4. 使用乐观锁替代悲观锁
```sql
-- 表结构增加版本字段
ALTER TABLE users ADD COLUMN version INT DEFAULT 0;

-- 应用层实现 CAS 更新
UPDATE users SET name='New', version=version+1
WHERE id=1 AND version=0;  -- 若 affected_rows=0，说明已被其他事务修改
```

### 5. 监控与告警
```sql
-- 配置慢查询日志捕获锁等待
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;

-- 使用 Performance Schema 分析锁
SELECT
    blocking_pid,
    blocked_pid,
    sql_text
FROM performance_schema.data_lock_waits w
JOIN performance_schema.threads t ON w.blocking_thread_id = t.thread_id;
```

---

## 五、面试话术

**面试官**："MySQL 什么情况下会锁表？"

**参考回答**：
> "锁表通常发生在以下几种场景：
>
> 第一，**无索引的全表扫描**。当 UPDATE、DELETE 或 SELECT FOR UPDATE 的 WHERE 条件没有用到索引时，InnoDB 无法定位具体要锁定的行，只能对全表所有行加锁，这本质上等同于锁表。比如 `UPDATE users SET name='x' WHERE age=30`，如果 age 列没有索引，就会锁住整张表。
>
> 第二，**显式的 LOCK TABLES 语句**。无论是 InnoDB 还是 MyISAM，执行 `LOCK TABLES users WRITE` 都会锁定整张表，其他会话的读写都会被阻塞。
>
> 第三，**DDL 操作**。像 ALTER TABLE、DROP INDEX 这类语句需要获取元数据锁（MDL），在 DDL 执行期间，整个表的 DML 操作都会被阻塞。这也是为什么大表的 DDL 要在业务低峰期执行。
>
> 第四，**间隙锁的范围过大**。在 REPEATABLE READ 隔离级别下，范围查询的 FOR UPDATE 会锁定整个区间。比如 `SELECT * FROM users WHERE id > 100 FOR UPDATE`，如果表中最大 id 是 200，那么 (100, +∞) 这个区间内的所有插入都会被阻止。
>
> 在实际开发中，我主要通过三个手段避免意外锁表：一是确保 WHERE 条件中的列都有索引；二是控制事务范围，尽早提交；三是使用 READ COMMITTED 隔离级别消除间隙锁，除非业务强依赖可重复读语义。"

**加分项**：提及 Next-Key Lock 的数学定义 `(prev_key, current_key]`，或讨论 Online DDL 的 ALGORITHM 参数（INPLACE vs COPY）。

---

## 六、交叉引用

- InnoDB 锁机制详解见 [事务与锁](../transaction/locks.md)
- 索引设计与优化见 [索引原理](../index/b-tree.md)
- 事务隔离级别见 [ACID 与 MVCC](../transaction/isolation-levels.md)
- 死锁排查指南见 [故障诊断](../troubleshooting/deadlock.md)
- Online DDL 最佳实践见 [表结构变更](../ddl/online-alter.md)
