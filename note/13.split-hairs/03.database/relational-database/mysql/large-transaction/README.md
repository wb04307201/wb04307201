<!--
question:
  id: 03.database-large-transaction
  topic: 03.database
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 生产 Bug
  tags: [03.database, large, transaction]
-->

# 大事务：长事务的危害 + 5 大优化策略

> 一个隐蔽但致命的性能陷阱。考察点不是"什么是事务"，而是 **大事务持有多少资源、怎么检测、怎么拆分**。

## 引子：主从延迟告警，从库落后主库 1 小时

```text
凌晨 2 点，老张收到报警：
- 从库主从延迟：3600 秒（落后 1 小时）
- 业务监控：用户看不到刚下的订单

排查：每天凌晨有个对账作业，把昨天全部订单包在一个事务里 select + insert。
大事务 → 主库 binlog 1 个条目巨大 → 从库重放极慢 → 主从延迟 1 小时。
```

**真相**：大事务是 MySQL 性能的"沉默杀手"。

5 大危害：

1. **持有锁过久**：行锁 / 间隙锁直到 commit 才释放，其他事务等
2. **Undo Log 暴涨**：影响所有事务的 Undo 读取
3. **binlog 暴涨**：从库重放延迟
4. **连接池耗尽**：高并发下其他请求排队
5. **MVCC 快照过期**：Undo Log 不能清理

**正解**：每 1000 行一个事务、异步化、事务里不做 HTTP 请求、设置超时 + 监控长事务。

## 一、核心结论（TL;DR）

| 事务规模 | 影响 |
|---------|------|
| 小事务（<1000 行） | ✅ 推荐 |
| 中事务（1k-1w 行） | ⚠️ 需要评估 |
| 大事务（>10w 行） | ❌ 必然引发问题 |

> 一句话：**大事务持有锁、Undo Log、binlog、连接池资源，是 MySQL 性能的"沉默杀手"。**

---

## 二、什么是大事务

- 单个事务操作超过 **10 万行**
- 单个事务执行时间超过 **5-10 秒**
- 单个事务持有锁的范围过大

---

## 三、大事务的 5 大危害

### 1. 持有锁时间过长 → 锁等待 / 死锁

- 大事务持有的行锁 / 间隙锁直到 commit/rollback 才释放
- 其他事务等不到锁 → 锁等待 → 性能下降 → 严重时死锁

### 2. Undo Log 暴涨 → 回滚段膨胀

- 每个变更都写 Undo Log
- 大事务产生海量 Undo Log
- 回滚段膨胀 → 影响所有事务的 Undo 读取

### 3. binlog 暴涨 → 主从延迟

- 主库大事务 → binlog 写入巨大条目
- 从库重放大事务 → 主从延迟

### 4. 连接池占用 → 连接耗尽

- 事务期间连接不能释放
- 高并发下大事务 → 连接池快速耗尽 → 其他请求排队

### 5. MVCC 快照过期 → 查询性能下降

- 长事务持有旧快照
- Undo Log 不能清理
- 影响 MVCC 查询性能

---

## 四、如何检测大事务

### 1. 查看运行中的事务

```sql
SELECT * FROM information_schema.innodb_trx
ORDER BY trx_started ASC;   -- 最早的事务排前面
```

关键字段：
- `trx_started`：事务开始时间
- `trx_rows_modified`：已修改行数
- `trx_state`：事务状态

### 2. 查看长事务

```sql
SELECT * FROM information_schema.innodb_trx
WHERE trx_started < NOW() - INTERVAL 10 SECOND
ORDER BY trx_started ASC;
```

### 3. MySQL 8.0+ sys.schema

```sql
SELECT * FROM sys.innodb_long_running_transactions;
```

---

## 五、5 大优化策略

### 1. 拆分大事务

```java
// ❌ 100 万行一个事务
conn.setAutoCommit(false);
for (...) { batch insert; }
conn.commit();

// ✅ 每 1000 行一个事务
int batchSize = 1000;
for (int i = 0; i < total; i += batchSize) {
    conn.setAutoCommit(false);
    for (int j = 0; j < batchSize; j++) {
        // batch insert
    }
    conn.commit();   // 小事务
}
```

### 2. 异步化处理

```java
// ✅ 不在请求线程里做大事务
@Async
public void batchProcess(List<User> users) {
    // 分批处理
}
```

### 3. 避免事务里做无关操作

```java
// ❌ 事务里做 HTTP 请求
@Transactional
public void process() {
    updateDb();
    httpCall();      // 慢！
    updateDb();
}

// ✅ 事务外做 HTTP
public void process() {
    updateDb();
    httpCall();
    updateDb();
}
```

### 4. 设置事务超时

```java
// Spring
@Transactional(timeout = 5)   // 5 秒超时
```

### 5. 监控 + 告警

```sql
-- 设置长事务阈值
SET GLOBAL innodb_long_query_time = 5;
```

---

## 六、面试陷阱

### 陷阱 1：以为大事务能"快进快出"

- **真相**：MySQL 事务提交涉及 fsync、binlog、Undo Log 清理，大事务 commit 本身就很慢

### 陷阱 2：以为 @Transactional 自动拆分

- **真相**：Spring @Transactional 只标记事务边界，不会自动拆分。需要在业务代码里手动分批

### 陷阱 3：事务隔离级别越高越安全

- **真相**：RR（可重复读）比 RC（读已提交）持有更多锁，RR 下大事务更危险

---

## 七、面试话术（90 秒版本）

> 大事务是指单事务操作超过 10 万行或执行超过 5-10 秒的事务。它的危害包括：
>
> 1. **持有锁过久**：行锁/间隙锁直到 commit 才释放，导致其他事务等待
> 2. **Undo Log 暴涨**：影响所有事务的 Undo 读取
> 3. **binlog 暴涨**：主从延迟
> 4. **连接池耗尽**：高并发下其他请求排队
> 5. **MVCC 快照过期**：Undo Log 不能清理，影响查询
>
> 优化策略：拆分大事务（每 1000 行一个事务）、异步化处理、事务里不做 HTTP 请求、设置事务超时、监控长事务告警。

---

## 八、相关章节

- 同栏目：[`select-all-big-table`](../select-all-big-table/README.md) — SELECT 内存陷阱
- 同栏目：[`deep-pagination`](../deep-pagination/README.md) — 深分页
- 同栏目：[`batch-operation`](../batch-operation/README.md) — 批量插入
- 同栏目：[`what-lock`](../what-lock/README.md) — 行锁 / 表锁 / 间隙锁
- 同栏目：[`isolation`](../isolation/README.md) — 事务隔离级别
- 主模块：[`03.database/03-transaction`](../../../../../03.database/03-transaction/README.md) — 事务与并发控制

---

> 📅 2026-06-28 · 咬文嚼字 · MySQL · ⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回: 咬文嚼字 · large-transaction](README.md)
