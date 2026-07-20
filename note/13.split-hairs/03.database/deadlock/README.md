<!--
question:
  id: 03.database-deadlock
  topic: 03.database
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 线上排查
  tags: [03.database, 死锁, deadlock, InnoDB, MySQL, 排查, 间隙锁]
-->

# 数据库死锁 —— 产生原理 + 线上排查 + 5 大预防策略

> 一句话定位：**MySQL 面试高频题 + 线上必备排查技能**。考察的不是"死锁是什么"，而是 **InnoDB 等待图检测原理** + **间隙锁死锁场景** + **SHOW ENGINE INNODB STATUS 日志解读** + **performance_schema 实时监控**。完整事务体系见 [事务主模块](../../../03.database/03-transaction/README.md)。

> **系列定位**：高频数据库面试题。配套兄弟题：[MVCC](../mvcc/README.md)、[MySQL 索引](../mysql-index-failure/README.md)。

---

⭐⭐⭐⭐ 深度级别（高级工程师 / DBA）
📚 前置知识：事务隔离级别 / InnoDB 锁类型（行锁/间隙锁/临键锁）/ MVCC

---

## 引子：线上死锁现场

凌晨 2 点，告警群炸了：

```
ERROR 1213 (40001): Deadlock found when trying to get lock; try restarting transaction
```

订单服务大面积超时，每秒数十个死锁错误。

你打开数据库，执行 `SHOW ENGINE INNODB STATUS`——输出 300 行，关键信息在哪？怎么看？怎么定位根因？怎么预防？

**这道题考察的不是"死锁 = 互相等待"，而是"从日志到根因的完整排查链路 + 预防策略"。**

---

## 一、核心原理

### 1.1 死锁 4 个必要条件

| 条件 | 说明 | InnoDB 场景 |
|------|------|------------|
| **互斥** | 资源同一时刻只能被一个事务持有 | 行锁/间隙锁排他 |
| **占有并等待** | 持有锁的同时等待其他锁 | UPDATE A 行后 UPDATE B 行 |
| **不可剥夺** | 已持有的锁不能被强制夺走 | 事务提交/回滚前不释放锁 |
| **环路等待** | 事务间形成等待环 | A→B→C→A |

**InnoDB 的死锁检测**：维护一张**等待图**（wait-for graph），每个事务是一个节点，"事务 X 等待事务 Y 持有的锁"是一条边。当图中出现**环**时，检测到死锁。

```
等待图示例：
  TX-100 ──等待──→ TX-200 ──等待──→ TX-100
                        ↑              │
                        └──── 环 ──────┘
→ InnoDB 选择回滚代价最小的事务（undo log 量最少）
```

### 1.2 InnoDB 的两种死锁类型

| 类型 | 触发场景 | 常见原因 |
|------|---------|---------|
| **行锁死锁** | 两个事务以不同顺序 UPDATE 相同行 | 加锁顺序不一致 |
| **间隙锁死锁** | RR 隔离级别下，两个事务对相同范围加间隙锁后都尝试插入 | 间隙锁不互斥（都持有），但插入意向锁与间隙锁互斥 |

**间隙锁死锁（最容易被忽视）**：

```sql
-- RR 隔离级别，表中只有 id=1,5,10
-- 事务 A
SELECT * FROM orders WHERE id = 3 FOR UPDATE;  -- 加间隙锁 (1,5)
-- 事务 B
SELECT * FROM orders WHERE id = 4 FOR UPDATE;  -- 也加间隙锁 (1,5)，不冲突！

-- 事务 A 尝试插入 id=3
INSERT INTO orders (id, amount) VALUES (3, 100);
-- → 需要插入意向锁，与事务 B 的间隙锁冲突 → 等待

-- 事务 B 尝试插入 id=4
INSERT INTO orders (id, amount) VALUES (4, 200);
-- → 需要插入意向锁，与事务 A 的间隙锁冲突 → 等待
-- → 死锁！
```

**解决**：降低隔离级别到 RC（不加间隙锁），或业务层避免"先查后插"模式。

---

## 二、线上排查 5 步法

### Step 1：确认死锁发生

```sql
-- 查看最近一次死锁日志
SHOW ENGINE INNODB STATUS\G

-- 关注 *** (1) TRANSACTION 和 *** (2) TRANSACTION 两个事务
-- 关注 WE ROLL BACK TRANSACTION (N) 哪个被回滚
```

### Step 2：开启死锁日志持久化

```sql
-- 默认只保留最近一次死锁，生产环境建议开启持久化
SET GLOBAL innodb_print_all_deadlocks = ON;
-- 所有死锁信息写入 MySQL error log
```

### Step 3：查看实时锁等待

```sql
-- MySQL 8.0+ 使用 performance_schema（替代已弃用的 information_schema 锁表）
SELECT
    r.trx_id AS waiting_trx_id,
    r.trx_mysql_thread_id AS waiting_thread,
    r.trx_query AS waiting_query,
    b.trx_id AS blocking_trx_id,
    b.trx_mysql_thread_id AS blocking_thread,
    b.trx_query AS blocking_query
FROM performance_schema.data_lock_waits w
JOIN performance_schema.data_locks r ON w.REQUESTING_ENGINE_LOCK_ID = r.ENGINE_LOCK_ID
JOIN performance_schema.data_locks b ON w.BLOCKING_ENGINE_LOCK_ID = b.ENGINE_LOCK_ID;
```

### Step 4：定位根因 SQL

```sql
-- 查看被阻塞的事务
SELECT * FROM information_schema.INNODB_TRX
WHERE trx_state = 'LOCK WAIT';

-- 查看当前活跃事务（按运行时间排序）
SELECT trx_id, trx_state, trx_started, trx_rows_locked, trx_rows_modified, trx_query
FROM information_schema.INNODB_TRX
ORDER BY trx_started;
```

### Step 5：杀阻塞会话（紧急止血）

```sql
-- 找到阻塞源的线程 ID
-- 从 Step 3 的结果中找到 blocking_thread

-- 杀掉阻塞会话（会回滚该事务）
KILL <blocking_thread_id>;
```

**注意**：KILL 是紧急手段，正常应通过优化 SQL 和加锁顺序预防。

---

## 三、7 道精选面试题

### Q1：死锁日志怎么看？SHOW ENGINE INNODB STATUS 的关键字段？

**答**：关注 4 个区块——

```
LATEST DETECTED DEADLOCK
  *** (1) TRANSACTION:       ← 事务 1 的 SQL + 持有的锁 + 等待的锁
  *** (2) TRANSACTION:       ← 事务 2 的 SQL + 持有的锁 + 等待的锁
  *** WE ROLL BACK TRANSACTION (N)  ← InnoDB 选择回滚哪个
```

**关键字段**：
- `LOCK WAIT X lock struct(s)` — 该事务持有 X 个锁
- `locks rec_but_not_gap` — 行锁（非间隙锁）
- `locks gap before rec` — 间隙锁
- `undo log entries N` — 回滚代价（InnoDB 选 undo 少的回滚）

### Q2：行锁死锁和间隙锁死锁有什么区别？怎么区分？

**答**：

| 特征 | 行锁死锁 | 间隙锁死锁 |
|------|---------|-----------|
| 隔离级别 | 任何级别 | **仅 RR**（RC 不加间隙锁） |
| 日志特征 | `locks rec_but_not_gap` | `locks gap before rec` |
| 常见场景 | UPDATE 不同行顺序不同 | SELECT FOR UPDATE + INSERT |
| 解决 | 统一加锁顺序 | 降为 RC / 避免先查后插 |

### Q3：InnoDB 怎么检测死锁？检测频率？

**答**：InnoDB 维护**等待图**（wait-for graph），每次事务请求锁时检查是否形成环。检测到环后，**选择 undo log 量最少的事务回滚**（代价最小）。

**检测频率**：每次加锁时实时检测（不是定时扫描）。

**超时兜底**：如果等待图检测未触发（极端边界情况），`innodb_lock_wait_timeout`（默认 50 秒）兜底超时回滚。

### Q4：为什么降低隔离级别到 RC 可以减少死锁？

**答**：RC 级别不加**间隙锁**（gap lock），只加行锁。行锁的冲突范围远小于间隙锁，死锁概率大幅降低。

**代价**：RC 级别可能出现**幻读**（同一事务内两次 SELECT 结果不同），但对大多数业务可接受。

### Q5：索引对死锁有什么影响？

**答**：**影响巨大**——InnoDB 的行锁是加在**索引记录**上，不是加在行上。

```sql
-- 没有索引
UPDATE orders SET status = 1 WHERE user_id = 100;
-- → 全表扫描，锁住所有行 → 极易死锁

-- 有 user_id 索引
UPDATE orders SET status = 1 WHERE user_id = 100;
-- → 只锁 user_id=100 的行 → 死锁概率低
```

**原则**：UPDATE/DELETE 的 WHERE 条件必须走索引，否则退化为表锁。

### Q6：`innodb_deadlock_detect = OFF` 是什么意思？什么时候用？

**答**：关闭 InnoDB 的死锁检测。高并发场景下（1000+ 并发），等待图的环检测本身成为性能瓶颈（O(n²) 复杂度）。关闭后依赖 `innodb_lock_wait_timeout` 超时回滚。

**适用**：极高并发 + 短事务 + 死锁概率低的场景（如阿里双十一热点更新优化）。

**风险**：死锁不会被立即检测，事务会等到超时才回滚（默认 50 秒），可能导致大面积超时。

### Q7：业务层怎么处理死锁？

**答**：3 层防御——

```java
// 1. Spring 自动重试（推荐）
@Transactional
public void transfer() { /* 业务逻辑 */ }
// Spring 的 @Retryable 或自定义重试拦截器

// 2. 手动重试
for (int retry = 0; retry < 3; retry++) {
    try {
        doTransfer();
        break;
    } catch (CannotAcquireLockException e) {
        if (retry == 2) throw e;  // 最后一次仍失败则抛出
        Thread.sleep(50 * (retry + 1));  // 退避重试
    }
}

// 3. 异步重试（MQ）
// 死锁失败 → 发送重试消息到 MQ → 消费者延迟重试
```

---

## 四、5 大预防策略

| 策略 | 说明 | 效果 |
|------|------|------|
| **1. 统一加锁顺序** | 多行操作按 id 升序排列后依次 UPDATE | 消除环路 |
| **2. 缩短事务** | 减少事务持有锁的时间，批量 UPDATE 改为分批小事务 | 减少锁冲突窗口 |
| **3. 降低隔离级别** | RR → RC，消除间隙锁 | 消除间隙锁死锁 |
| **4. 合理索引** | UPDATE/DELETE 的 WHERE 条件走索引 | 避免全表锁 |
| **5. 乐观锁替代** | 版本号 CAS 更新替代 SELECT FOR UPDATE | 无锁竞争 |

---

## 五、常见陷阱

**陷阱 1：WHERE 条件不走索引**

```sql
-- ❌ 全表扫描 → 锁住所有行
UPDATE orders SET status = 1 WHERE create_time > '2026-01-01';

-- ✅ 加索引后只锁匹配行
ALTER TABLE orders ADD INDEX idx_create_time (create_time);
UPDATE orders SET status = 1 WHERE create_time > '2026-01-01';
```

**陷阱 2：大事务中混合多个操作**

```java
// ❌ 一个事务中查 3 张表再依次更新
@Transactional
public void process() {
    User u = userRepo.findById(id);    // 锁 user 表
    Order o = orderRepo.findById(id);  // 锁 order 表
    Account a = accountRepo.findById(id); // 锁 account 表
    // 其他事务如果以不同顺序访问 → 死锁
}

// ✅ 拆分为小事务 / 统一访问顺序
```

**陷阱 3：SELECT FOR UPDATE 后 INSERT**

```sql
-- ❌ RR 级别下间隙锁死锁的经典模式
SELECT * FROM orders WHERE id = 3 FOR UPDATE;  -- 间隙锁 (1,5)
INSERT INTO orders (id) VALUES (3);             -- 插入意向锁冲突
```

---

## 六、面试话术（30 秒版）

> "数据库死锁的 4 个必要条件是互斥、占有并等待、不可剥夺、环路等待。InnoDB 通过维护等待图实时检测死锁，发现环后回滚 undo log 最少的事务。
>
> 线上排查 5 步：SHOW ENGINE INNODB STATUS 看死锁日志 → 开启 innodb_print_all_deadlocks 持久化 → performance_schema.data_lock_waits 查实时锁等待 → INNODB_TRX 定位根因 SQL → KILL 阻塞会话紧急止血。
>
> 最常见的两种死锁：行锁死锁（UPDATE 不同行顺序不一致）和间隙锁死锁（RR 级别下 SELECT FOR UPDATE + INSERT）。间隙锁死锁可以通过降低隔离级别到 RC 来消除。
>
> 预防 5 策：统一加锁顺序 + 缩短事务 + 降低隔离级别 + 确保 WHERE 走索引 + 乐观锁替代。"

---

## 七、交叉引用

- **事务体系**：[事务](../../../03.database/03-transaction/README.md) — ACID / 隔离级别 / 锁机制 / MVCC / 死锁实战
- **相关面试题**：[MVCC](../mvcc/README.md) — 读写不阻塞的原理
- **相关面试题**：[MySQL 索引](../mysql-index-failure/README.md) — 索引对锁范围的影响
- **监控**：[数据库监控](../../../03.database/11-monitoring/README.md) — 锁等待监控
- **主模块**：[`03.database`](../../../03.database/) — 数据库知识体系

## 相关章节

- 深度阅读：[`03.database`](../../03.database/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · deadlock](../README.md)
