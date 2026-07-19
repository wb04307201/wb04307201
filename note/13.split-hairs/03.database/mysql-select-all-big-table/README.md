<!--
question:
  id: 03.database-select-all-big-table
  topic: 03.database
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 生产 Bug
  tags: [03.database, select, all]
-->

# SELECT * 查 2000 万行数据，会炸内存吗

> 一个看似无聊、但 90% 候选人答不全的「基础」问题。真正考察的不是 SQL 本身，而是 **MySQL JDBC 驱动的默认行为 + JVM 堆内存模型**。

## 引子：跑批导出 2000 万行，JVM OOM 崩溃

```text
小王写了个跑批：
  while (rs.next()) {
    processRow(rs);   // 一行一行处理
  }
跑了一晚上：java.lang.OutOfMemoryError: Java heap space
2000 万行 / 1000 万级内存 / 服务挂掉
```

**真相**：你以为 `while(rs.next())` 是一行一行处理，
**驱动早就把全部行加载到堆内存了** —— 你看到的"游标"只是在内存里挪指针。

MySQL JDBC 默认配置：

| 配置 | 默认 | 后果 |
|------|------|------|
| `useCursorFetch` | `false` | 走一次性 fetch all |
| `fetchSize` | `0` | "由驱动决定" → 实际全量缓存 |
| `resultSetType` | `TYPE_FORWARD_ONLY` | 内部 `RowDataStatic`（全量缓存）|

**真实开销**：单行 500B 的表，2000 万行 ≈ **50-100 GB JVM 堆**（含对象膨胀 5-10x）→ 必 OOM。

4 种解法：

1. **JDBC 流式**：`setFetchSize(Integer.MIN_VALUE)`（MySQL 专属魔法值）
2. **服务端游标**：URL 加 `useCursorFetch=true&defaultFetchSize=1000`
3. **深分页**：`WHERE id > ? LIMIT n`（不要 OFFSET）
4. **专用工具**：`mysqldump` / `SELECT INTO OUTFILE`

## 一、核心结论（TL;DR）

| 问题 | 答案 |
|------|------|
| 会不会炸内存？ | **会，必炸** |
| 为什么？ | MySQL JDBC 默认走「一次性 fetch all」，驱动先把 2000 万行全部塞进 JVM 堆 |
| 加 `setFetchSize(100)` 能解决吗？ | **不能**，非游标模式下 `fetchSize` 只是个「一次缓冲多大」的提示 |
| 真正的解法？ | `setFetchSize(Integer.MIN_VALUE)` 走 MySQL 专用流式；或 URL 加 `useCursorFetch=true`；或 LIMIT 分页 |

> 一句话：**你以为 `while(rs.next())` 是一行一行处理，其实驱动早就把全部行加载到堆内存了，「游标」只是在内存里挪指针。**

---

## 二、默认机制：数据是怎么「炸」进内存的

### 1. 完整数据流

```
MySQL Server
    │
    │  ① 服务端执行 SELECT *，把 2000 万行结果集在内存里序列化
    │
    │  ② 通过 socket 一次性（或按 net_buffer_length 分包）推给客户端
    │     ※ 受 max_allowed_packet（默认 64 MB）单包限制
    │       但驱动会多次拉取，最终拼成完整结果集
    ▼
JDBC 驱动（mysql-connector-j）
    │
    │  ③ 收到全部数据后，解码为 RowData 行结构
    │
    │  ④ 缓存在 JVM 堆内存（默认 useCursorFetch=false + fetchSize=0）
    │
    │  ⑤ 暴露给 ResultSet 对象
    ▼
ResultSet（你看到的「游标」）
    │
    │  ⑥ while(rs.next()) —— 只是在内存里往后挪指针
    │     ❗ 数据早已在内存中
    ▼
业务代码
```

### 2. 三个致命默认配置

| 配置项 | 默认值 | 后果 |
|--------|--------|------|
| `useCursorFetch` | `false` | 走「一次性 fetch all」路径 |
| `fetchSize` | `0` | 表示「由驱动决定」，驱动选 Integer.MIN_VALUE 的非流式行为 |
| `resultSetType` | `TYPE_FORWARD_ONLY` | 驱动内部用 `RowDataStatic`（全量缓存）而非 `RowDataDynamic` |

---

## 三、内存占用估算

### 1. 公式

```
JVM 堆占用 ≈ 单行宽 × 行数 × 对象膨胀系数（5 ~ 10）
```

### 2. 不同行宽下的真实开销

| 单行宽 | 原始数据 2000 万行 | Java 堆占用（×5~10） | 8 GB 堆？ |
|--------|------------------|--------------------|---------|
| 100 B  | 2 GB             | **10 ~ 20 GB**     | ❌ OOM  |
| 500 B  | 10 GB            | **50 ~ 100 GB**    | ❌ OOM  |
| 1 KB   | 20 GB            | **100 ~ 200 GB**   | ❌ OOM  |
| 10 KB  | 200 GB           | **物理内存上限**    | ❌ 直接挂  |

### 3. 对象膨胀来源

每个字段在 Java 侧的实际占用远大于磁盘存储：

- **对象头**：16 B / 对象
- **数组头**：16 B + 长度字段
- **引用**：4 ~ 8 B / 字段
- **`String`**：内部 `byte[]` + `hash` 字段
- **`BigDecimal`**：内部 `int[]` + `scale`
- **字符集解码**：UTF-8 → UTF-16，Latin 字符膨胀 2 倍
- **RowData 行包装对象**

**结论：实际占用通常是磁盘行宽的 5 ~ 10 倍，绝不是 1:1。**

---

## 四、正确的四种姿势

### 姿势 A：MySQL 专用流式（推荐）

```java
// 关键：Integer.MIN_VALUE 是 MySQL JDBC 的「魔法值」
stmt.setFetchSize(Integer.MIN_VALUE);

try (ResultSet rs = stmt.executeQuery("SELECT * FROM big_table")) {
    while (rs.next()) {
        // 驱动才真正一次拉一行，前一行处理完才拉下一行
        processOneRow(rs);
    }
}
```

### 姿势 B：服务端真游标

```java
// URL 开启服务端游标
String url = "jdbc:mysql://host:3306/db?useCursorFetch=true&defaultFetchSize=1000";

PreparedStatement stmt = conn.prepareStatement(sql);
stmt.setFetchSize(1000);   // 服务端每次推 1000 行

try (ResultSet rs = stmt.executeQuery()) {
    while (rs.next()) {
        processOneRow(rs);
    }
}
```

> ⚠️ **副作用**：服务端游标会持有事务锁直到 ResultSet 关闭，且占用服务端临时表空间。

### 姿势 C：深分页 / 游标分页

```sql
-- ❌ 反例：越往后越慢（OFFSET 10000000 仍要扫 1000 万行）
SELECT * FROM big_table LIMIT 10 OFFSET 10000000;

-- ✅ 正例：基于有序键的游标分页
SELECT * FROM big_table WHERE id > ? ORDER BY id LIMIT 1000;
```

### 姿势 D：专用导出工具（最稳）

```bash
# 内存友好，服务端直接流式输出
mysqldump -h host -u user -p db big_table > big_table.sql

# 或
mysql -h host -u user -p -e "SELECT * INTO OUTFILE '/tmp/big.csv' FROM big_table"
```

---

## 五、经典面试陷阱（候选人 90% 会踩）

### 陷阱 1：以为 `setFetchSize(100)` 就流式了

```java
// ❌ 这样写还是会炸
stmt.setFetchSize(100);  // 在非游标模式下，这个值被驱动「软忽略」
```

- **真相**：MySQL JDBC 在 `useCursorFetch=false` 时，`fetchSize` 只是「一次网络往返拉多少行」，**最终还是会拉完全部行到本地缓存**。
- **验证**：打开驱动日志 `logger=com.mysql.cj=DEBUG`，会看到 `fetchSize=100, fetching all rows`。

### 陷阱 2：以为 ResultSet 类型是 `SCROLL_SENSITIVE` 就能边读边释放

- **真相**：驱动内部数据结构分两种：

  | ResultSet 类型 | 内部数据结构 | 是否全量缓存 |
  |----------------|--------------|--------------|
  | `TYPE_FORWARD_ONLY` | `RowDataStatic` | ✅ 全量 |
  | `TYPE_SCROLL_SENSITIVE` | 仍是 `RowDataStatic` | ✅ 全量（仅支持双向滚动） |
  | `TYPE_SCROLL_INSENSITIVE` | 仍是 `RowDataStatic` | ✅ 全量 |

  → 不存在「边读边释放」的滚动模式。

### 陷阱 3：用 ORM（Hibernate / MyBatis）就以为自动流式了

- **真相**：MyBatis 默认把所有行封装成 `List<T>` 返回，内存压力更大（再加一层 POJO 膨胀）。
- **正确做法**：MyBatis 用 `Cursor<T>` + `@Options(fetchSize = Integer.MIN_VALUE)`：

  ```java
  @Options(fetchSize = Integer.MIN_VALUE)
  @ResultType(User.class)
  @Select("SELECT * FROM user")
  Cursor<User> streamAll();
  ```

---

## 六、面试话术模板（90 秒版本）

> **答**：一定会炸。MySQL JDBC 驱动默认 `useCursorFetch=false` + `fetchSize=0`，走的是一次性 fetch all 路径，2000 万行结果集会被全部加载到 JVM 堆内存里。即使我用 `while(rs.next())` 一行一行处理，驱动内部早就把所有行解码成 `RowDataStatic` 缓存了，「游标」只是个在内存里挪动的指针。
>
> 真正的解法分三个层级：
>
> 1. **JDBC 层**：`stmt.setFetchSize(Integer.MIN_VALUE)` 走 MySQL 专用流式，或者 URL 加 `useCursorFetch=true` 走服务端真游标；
> 2. **SQL 层**：永远不要在业务代码里裸 `SELECT *`，用基于有序键的游标分页（`WHERE id > ? LIMIT n`），不要用 `OFFSET`；
> 3. **架构层**：批量导出走 `mysqldump` / `SELECT INTO OUTFILE` / DataX 等专用工具，不要用 JDBC。

---

## 七、相关章节

- 主模块：[`03.database/02-sql`](../../../03.database/02-sql/README.md) — SQL 优化原则「少取/少传」
- 主模块：[`03.database/05-mysql`](../../../03.database/05-mysql/README.md) — MySQL 架构与 InnoDB
- 同栏目：[`tuning`](../mysql-tuning/README.md) — SQL 调优全流程
- 同栏目：[`count`](../mysql-count/README.md) — COUNT 性能差异
- 关联：[`01.java/jdbc`](../../../01.java/jdbc/README.md) — JDBC 核心接口与连接池

---

> 📅 2026-06-28 · 咬文嚼字 · MySQL · ⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回数据库咬文嚼字](../README.md)
