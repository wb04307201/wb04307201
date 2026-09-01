<!--
module:
  parent: database/04-index
  slug: database/04-index/composite-index-filesort
  type: article
  category: 索引优化
  summary: 联合索引覆盖了 WHERE + ORDER BY 仍 filesort 的 5 大原因 + EXPLAIN 排查步骤 + 修复方案
  depth: ⭐⭐⭐
-->

# 联合索引 + Using filesort：5 大原因 + 排查指南

← [返回: 索引](../README.md)

> **一句话定位**：联合索引覆盖了 WHERE + ORDER BY 的列，但 EXPLAIN 仍显示 `Using filesort` —— 这是 MySQL 性能优化的经典陷阱。根因通常是 **排序方向不一致 / 范围查询截断 / 隐式类型转换 / 字符集 collation / 索引列不连续** 五大原因之一。

---

## 面试高频拷问
```text
Q：联合索引 (a, b, c)，查询 WHERE a = 1 ORDER BY b，为什么还会 Using filesort？
Q：怎么排查 EXPLAIN 中的 Using filesort？
Q：联合索引覆盖了 WHERE 和 ORDER BY，为什么还慢？
```

**回答框架（5 大原因 + 排查步骤）**：

1. **排序方向不一致**：索引是 ASC，但 ORDER BY 是 DESC（MySQL 8.0 前不支持降序索引）
2. **范围查询截断**：WHERE 用了范围查询（`a > 1`），导致索引在 a 列后截断，b 列无法用于排序
3. **隐式类型转换**：WHERE 条件类型与索引列类型不匹配（如字符串 vs 数字）
4. **字符集 collation**：不同字符集的排序规则导致索引无法用于排序
5. **索引列不连续**：ORDER BY 的列在索引中不连续（跳过了中间列）

---

## 背景知识
### 1.1 什么是 filesort？

**filesort** 是 MySQL 的一种排序方式，表示**无法利用索引完成排序**，需要额外的排序操作。

**两种排序方式**：
- **索引排序**（Using index）：利用索引的有序性，直接按索引顺序读取数据 → 快
- **filesort**：数据读取后，在内存或磁盘中额外排序 → 慢

**filesort 的类型**：
- **内存排序**：数据量小（`sort_buffer_size` 内）→ 快
- **磁盘排序**：数据量大，超出 `sort_buffer_size` → 慢（涉及磁盘 I/O）

### 1.2 联合索引的有序性

联合索引 `(a, b, c)` 的有序性：
- 先按 a 排序
- a 相同时，按 b 排序
- a、b 都相同时，按 c 排序

**关键规则**：
> 联合索引的有序性**从最左列开始**，且**遇到范围查询后截断**。

---

## 5 大原因详解
### 原因 1：排序方向不一致（ASC vs DESC）

**场景**：

```sql
-- 联合索引 (a ASC, b ASC)
CREATE INDEX idx_a_b ON t(a, b);

-- 查询
SELECT * FROM t WHERE a = 1 ORDER BY b DESC;
```

**根因**：
- MySQL 8.0 前**不支持降序索引**，索引默认 ASC
- ORDER BY DESC 无法利用 ASC 索引 → filesort

**EXPLAIN 输出**：

```text
+----+-------------+-------+------+---------------+---------+---------+-------+------+-----------------------------+
| id | select_type | table | type | possible_keys | key     | key_len | ref   | rows | Extra                       |
+----+-------------+-------+------+---------------+---------+---------+-------+------+-----------------------------+
|  1 | SIMPLE      | t     | ref  | idx_a_b       | idx_a_b | 5       | const |   10 | Using where; Using filesort |
+----+-------------+-------+------+---------------+---------+---------+-------+------+-----------------------------+
```

**修复**：
- MySQL 8.0+：创建降序索引 `CREATE INDEX idx_a_b ON t(a ASC, b DESC);`
- MySQL 5.7：调整 ORDER BY 方向（改为 ASC）或接受 filesort

**验证**：

```sql
-- MySQL 8.0+
CREATE INDEX idx_a_b_desc ON t(a ASC, b DESC);
EXPLAIN SELECT * FROM t WHERE a = 1 ORDER BY b DESC;
-- Extra: Using index condition lookup（无 filesort）
```

---

### 原因 2：范围查询截断索引

**场景**：

```sql
-- 联合索引 (a, b, c)
CREATE INDEX idx_a_b_c ON t(a, b, c);

-- 查询
SELECT * FROM t WHERE a > 1 ORDER BY b;
```

**根因**：
- WHERE 用了范围查询 `a > 1`
- 联合索引在范围查询后**截断**：a 列后的 b、c 列无法用于索引扫描
- ORDER BY b 无法利用索引 → filesort

**EXPLAIN 输出**：

```text
+----+-------------+-------+-------+---------------+-----------+---------+------+------+--------------------------------+
| id | select_type | table | type  | possible_keys | key       | key_len | ref  | rows | Extra                          |
+----+-------------+-------+-------+---------------+-----------+---------+------+------+--------------------------------+
|  1 | SIMPLE      | t     | range | idx_a_b_c     | idx_a_b_c | 15      | NULL |  100 | Using index condition; Using filesort |
+----+-------------+-------+-------+---------------+-----------+---------+------+------+--------------------------------+
```

**关键规则**：
> 联合索引中，**范围查询（>、<、BETWEEN、LIKE）后的列无法用于索引扫描**。

**修复方案**：

1. **调整索引顺序**：把范围查询列放最后

```sql
-- 原索引 (a, b, c) → 新索引 (b, c, a)
CREATE INDEX idx_b_c_a ON t(b, c, a);

-- 查询
SELECT * FROM t WHERE a > 1 ORDER BY b;
-- b 列可以用于排序（因为 b 是最左列，且没有范围查询截断）
```

2. **接受 filesort**：如果范围查询 + 排序 + 数据量大，filesort 可能不可避免

---

### 原因 3：隐式类型转换

**场景**：

```sql
-- a 列是 VARCHAR
CREATE INDEX idx_a_b ON t(a, b);

-- 查询（a 传了数字）
SELECT * FROM t WHERE a = 123 ORDER BY b;
```

**根因**：
- a 列是 VARCHAR，但 WHERE 传了 INT
- MySQL 隐式转换：`VARCHAR → INT`（相当于对 a 列用了函数）
- 索引失效 → filesort

**EXPLAIN 输出**：

```text
+----+-------------+-------+------+---------------+------+---------+------+------+-----------------------------+
| id | select_type | table | type | possible_keys | key  | key_len | ref  | rows | Extra                       |
+----+-------------+-------+------+---------------+------+---------+------+------+-----------------------------+
|  1 | SIMPLE      | t     | ALL  | NULL          | NULL | NULL    | NULL | 1000 | Using where; Using filesort |
+----+-------------+-------+------+---------------+------+---------+------+------+-----------------------------+
```

**修复**：
- 类型匹配：`WHERE a = '123'`（字符串加引号）
- 或调整表结构（a 列改为 INT）

---

### 原因 4：字符集 collation 不一致

**场景**：

```sql
-- 表字符集 utf8mb4
CREATE TABLE t (
  a VARCHAR(50) CHARACTER SET utf8mb4,
  b INT,
  INDEX idx_a_b(a, b)
) CHARACTER SET utf8mb4;

-- 查询时连接字符集 utf8
SET NAMES utf8;
SELECT * FROM t WHERE a = 'abc' ORDER BY b;
```

**根因**：
- 表字符集 utf8mb4，连接字符集 utf8
- 排序规则（collation）不一致 → 索引无法用于排序

**修复**：
- 统一字符集：`SET NAMES utf8mb4;`
- 或调整表字符集（`ALTER TABLE t CONVERT TO CHARACTER SET utf8mb4;`）

---

### 原因 5：ORDER BY 列在索引中不连续

**场景**：

```sql
-- 联合索引 (a, b, c)
CREATE INDEX idx_a_b_c ON t(a, b, c);

-- 查询（跳过 b 列）
SELECT * FROM t WHERE a = 1 ORDER BY c;
```

**根因**：
- ORDER BY c，但索引中 b 在 c 前面
- 跳过了 b 列 → c 列无法用于排序 → filesort

**EXPLAIN 输出**：

```text
+----+-------------+-------+------+---------------+-----------+---------+-------+------+-----------------------------+
| id | select_type | table | type | possible_keys | key       | key_len | ref   | rows | Extra                       |
+----+-------------+-------+------+---------------+-----------+---------+-------+------+-----------------------------+
|  1 | SIMPLE      | t     | ref  | idx_a_b_c     | idx_a_b_c | 5       | const |   10 | Using where; Using filesort |
+----+-------------+-------+------+---------------+-----------+---------+-------+------+-----------------------------+
```

**修复**：
- 调整索引顺序：`(a, c)` 或 `(a, b, c)` 且查询时包含 b
- 或接受 filesort

---

## 排查步骤（4 步）
### Step 1：看 EXPLAIN

```sql
EXPLAIN SELECT * FROM t WHERE a = 1 ORDER BY b;
```

重点关注：
- `type`：是否 ALL（全表扫描）或 range（范围查询）
- `key`：是否用了预期索引
- `Extra`：是否有 `Using filesort`

### Step 2：检查索引定义

```sql
SHOW INDEX FROM t;
```

关注：
- 索引列顺序
- 排序方向（ASC / DESC，MySQL 8.0+）
- 字符集

### Step 3：对照 5 大原因逐一排查

| 原因 | 排查方法 |
|------|---------|
| 排序方向不一致 | 检查索引 ASC/DESC vs ORDER BY ASC/DESC |
| 范围查询截断 | 检查 WHERE 是否用了 >、<、BETWEEN、LIKE |
| 隐式类型转换 | 检查 WHERE 条件类型 vs 索引列类型 |
| 字符集 collation | 检查表字符集 vs 连接字符集 |
| 索引列不连续 | 检查 ORDER BY 列在索引中是否连续 |

### Step 4：修复 + 验证

- 修复后重新 EXPLAIN，确认 `Extra` 无 `Using filesort`
- 或用 `EXPLAIN FORMAT=JSON` 查看详细计划

```sql
EXPLAIN FORMAT=JSON SELECT * FROM t WHERE a = 1 ORDER BY b;
```

---

## 实战案例
### 案例 1：电商订单查询

**场景**：

```sql
-- 订单表
CREATE TABLE orders (
  order_id BIGINT PRIMARY KEY,
  user_id INT,
  create_time DATETIME,
  status TINYINT,
  INDEX idx_user_status_time(user_id, status, create_time)
);

-- 查询：某用户的所有"已完成"订单，按时间倒序
SELECT * FROM orders
WHERE user_id = 123 AND status = 2
ORDER BY create_time DESC;
```

**问题**：EXPLAIN 显示 `Using filesort`

**排查**：
- 索引：`(user_id, status, create_time)` — ASC
- ORDER BY：`create_time DESC`
- 根因：排序方向不一致（原因 1）

**修复**：

```sql
-- MySQL 8.0+
CREATE INDEX idx_user_status_time_desc
ON orders(user_id ASC, status ASC, create_time DESC);

EXPLAIN SELECT * FROM orders
WHERE user_id = 123 AND status = 2
ORDER BY create_time DESC;
-- Extra: Using index condition（无 filesort）
```

### 案例 2：日志查询

**场景**：

```sql
-- 日志表
CREATE TABLE logs (
  id BIGINT PRIMARY KEY,
  level VARCHAR(10),
  create_time DATETIME,
  message TEXT,
  INDEX idx_level_time(level, create_time)
);

-- 查询：最近 7 天的 ERROR 日志，按时间排序
SELECT * FROM logs
WHERE level = 'ERROR' AND create_time > DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY create_time;
```

**问题**：EXPLAIN 显示 `Using filesort`

**排查**：
- WHERE：`create_time > ...` — 范围查询
- 索引：`(level, create_time)` — create_time 在范围查询后
- 根因：范围查询截断（原因 2）

**修复**：

```sql
-- 调整索引顺序
CREATE INDEX idx_time_level ON logs(create_time, level);

-- 查询
SELECT * FROM logs
WHERE level = 'ERROR' AND create_time > DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY create_time;
-- create_time 是最左列，可以用于排序
```

---

## 一句话速查
```text
"联合索引 + filesort 5 大原因：
1. 排序方向不一致（ASC vs DESC）
2. 范围查询截断（>、<、BETWEEN、LIKE 后的列无法用于排序）
3. 隐式类型转换（WHERE 类型 vs 索引列类型不匹配）
4. 字符集 collation 不一致（表字符集 vs 连接字符集）
5. 索引列不连续（跳过了中间列）
排查：EXPLAIN 看 Extra → SHOW INDEX 检查索引 → 逐一对照 5 大原因 → 修复后验证。"
```

---

## 交叉引用
- **同模块兄弟**：
  - [mysql-index-failure 面试题](../../../../../note/12.interview/03.database/mysql-index-failure/) — 10 种索引失效场景
  - [mysql-tuning 面试题](../../../../../note/12.interview/03.database/mysql-tuning/) — SQL 调优

- **相关章节**：
  - [索引主模块](../README.md) — 索引原理 + B+ 树
  - [MySQL 主模块](../../05-mysql/README.md) — MySQL 架构 + 事务

---

← [返回: 索引](../README.md) · [返回: Database](../../README.md)
