<!--
question:
  id: 03.database-batch-operation
  topic: 03.database
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 生产 Bug
  tags: [03.database, batch, operation]
-->

# 批量插入：JDBC batch vs rewriteBatchedStatements 性能对比

> 同样是"插入 100 万行"，写法不同性能差 100 倍。考察点不是"怎么用 batch"，而是 **MySQL JDBC 的 `rewriteBatchedStatements` 参数如何把 batch 编译成 multi-value INSERT**。

## 引子：30 分钟同步 100 万订单，跑了一晚上没完

```text
业务方催上线：数据迁移，要求 30 分钟内把 100 万订单灌进新库。
同事小王写：
  for (Order o : orders) {
    ps.setString(1, o.getNo());
    ps.executeUpdate();
  }
结果：跑了一晚上，进度 40 万 / 100 万。
老板：明天 deadline，今晚要搞完！
```

**真相**：100 万次 INSERT = 100 万次 RTT（网络往返）。
- 单条 INSERT：~600 秒
- JDBC batch 默认：~30 秒（仍然是 N 个独立 INSERT）
- **JDBC batch + `rewriteBatchedStatements=true`**：~3 秒（驱动自动合成 multi-value INSERT）
- LOAD DATA INFILE：~1 秒

**不开启 `rewriteBatchedStatements` = 用 batch 等于没用**，性能差距 100 倍。

## 一、核心结论（TL;DR）

| 方式 | 100 万行耗时（参考） | 网络往返次数 |
|------|-------------------|-------------|
| 单条 INSERT | ~600 秒 | 100 万次 |
| JDBC batch（默认） | ~30 秒 | 100 万次 |
| JDBC batch + `rewriteBatchedStatements=true` | ~3 秒 | ~10 万次 |
| LOAD DATA INFILE | ~1 秒 | 1 次 |

> 一句话：**JDBC batch 默认是"批量发送 N 个独立 INSERT"，需要 `rewriteBatchedStatements=true` 才能合并成 multi-value INSERT，性能才能真正起飞。**

---

## 二、单条 INSERT 为什么慢

```java
// ❌ 反例：100 万次网络往返
for (User user : users) {
    PreparedStatement ps = conn.prepareStatement("INSERT INTO user VALUES (?, ?)");
    ps.setString(1, user.getName());
    ps.setInt(2, user.getAge());
    ps.executeUpdate();
    ps.close();
}
```

每次 INSERT 都要：
1. 客户端 → 服务端：发送 SQL + 参数
2. 服务端解析、写入 InnoDB
3. 服务端 → 客户端：返回 affected rows

**100 万次 INSERT = 100 万次 RTT**，慢是必然的。

---

## 三、JDBC batch 的两个层级

### Level 1：默认 JDBC batch（伪批量）

```java
PreparedStatement ps = conn.prepareStatement("INSERT INTO user VALUES (?, ?)");
for (User user : users) {
    ps.setString(1, user.getName());
    ps.setInt(2, user.getAge());
    ps.addBatch();   // 加入批次
}
int[] results = ps.executeBatch();   // 一次性发送
```

**默认行为**：把 N 个 INSERT 打包成一个网络包发送，但**仍然是 N 个独立的 INSERT 语句**。

服务端需要：
- 解析 N 次 SQL
- 执行 N 次 INSERT
- 生成 N 个 Undo Log

**性能提升有限**：~10-20 倍

### Level 2：rewriteBatchedStatements=true（真批量）

```java
String url = "jdbc:mysql://host:3306/db?rewriteBatchedStatements=true";

PreparedStatement ps = conn.prepareStatement("INSERT INTO user VALUES (?, ?)");
for (User user : users) {
    ps.setString(1, user.getName());
    ps.setInt(2, user.getAge());
    ps.addBatch();
}
ps.executeBatch();
```

**驱动行为**：把 N 个 INSERT 自动重写成一个 multi-value INSERT：

```sql
INSERT INTO user VALUES (?, ?), (?, ?), (?, ?), ..., (?, ?)   -- 一次性 N 条
```

**性能飞跃**：~100-200 倍

### Level 3：executeLargeBatch（MySQL 8.0+）

```java
PreparedStatement ps = conn.prepareStatement("INSERT INTO user VALUES (?, ?)");

for (User user : users) {
    ps.setString(1, user.getName());
    ps.setInt(2, user.getAge());
    ps.addBatch();
}
ps.executeLargeBatch();   // MySQL 8.0+ 推荐
```

MySQL 8.0 驱动对 executeBatch 做了优化，效果等价于 rewriteBatchedStatements。

---

## 四、最佳实践

### 1. 必须开启 rewriteBatchedStatements

```java
String url = "jdbc:mysql://host:3306/db?rewriteBatchedStatements=true&useServerPrepStmts=false";
```

### 2. 合理设置 batchSize

```java
// 推荐：每批 1000-5000 条
int batchSize = 1000;
for (int i = 0; i < users.size(); i++) {
    ps.setString(1, users.get(i).getName());
    ps.setInt(2, users.get(i).getAge());
    ps.addBatch();
    if ((i + 1) % batchSize == 0) {
        ps.executeBatch();
        conn.commit();
    }
}
ps.executeBatch();   // 处理剩余
conn.commit();
```

### 3. 大批量用 LOAD DATA INFILE

```bash
# 把数据写成 CSV
# 直接导入（不走 SQL 解析）
mysql -h host -u user -p -e "LOAD DATA INFILE '/tmp/users.csv' INTO TABLE user FIELDS TERMINATED BY ','"
```

### 4. 关闭自动提交

```java
conn.setAutoCommit(false);   // 批量提交
// ...batch insert...
conn.commit();
```

---

## 五、面试陷阱

### 陷阱 1：以为 addBatch 就是"批量"

- **真相**：默认 addBatch 只是把 SQL 打包发送，**不是合并成 multi-value INSERT**

### 陷阱 2：batchSize 越大越好

- **真相**：batchSize 过大导致单次执行时间过长、内存占用增加；推荐 1000-5000

### 陷阱 3：用事务包裹整个批量

```java
// ❌ 100 万行一个事务 = 大事务
conn.setAutoCommit(false);
for (...) { ps.addBatch(); }
ps.executeBatch();
conn.commit();   // 大事务
```

- **问题**：大事务持有锁、Undo Log 大、binlog 大
- **正确**：每 1000 行一个事务（详见 [`large-transaction`](../large-transaction/README.md)）

---

## 六、面试话术（90 秒版本）

> 单条 INSERT 慢是因为每次都要走"客户端发送 → 服务端解析 → 服务端写入 → 返回"的完整流程，100 万行就是 100 万次 RTT。
>
> JDBC batch 默认是把 N 个 INSERT 打包发送，但**还是 N 个独立的 INSERT**，服务端仍然要解析 N 次。
>
> 真正起飞的是 `rewriteBatchedStatements=true`，驱动会把 N 个 INSERT 自动重写成一个 multi-value INSERT（`INSERT INTO t VALUES (...), (...), (...)`），减少 90% 的 RTT 和解析开销。
>
> 更大的批量用 LOAD DATA INFILE，直接把文件读进 InnoDB，不走 SQL 解析。
>
> 注意大事务问题：每 1000-5000 行一个事务，避免持有锁过久。

---

## 七、相关章节

- 同栏目：[`select-all-big-table`](../select-all-big-table/README.md) — SELECT 内存陷阱
- 同栏目：[`deep-pagination`](../deep-pagination/README.md) — 深分页
- 同栏目：[`large-transaction`](../large-transaction/README.md) — 大事务
- 同栏目：[`tuning`](../tuning/README.md) — SQL 调优全流程
- 同栏目：[`what-lock`](../what-lock/README.md) — 行锁 / 表锁 / 间隙锁
- 主模块：[`01.java/jdbc`](../../../../../01.java/jdbc/README.md) — JDBC 核心接口

---

> 📅 2026-06-28 · 咬文嚼字 · MySQL · ⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回: 咬文嚼字 · batch-operation](README.md)
