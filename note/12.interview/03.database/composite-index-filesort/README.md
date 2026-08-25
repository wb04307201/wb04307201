<!--
question:
  id: 03.database-composite-index-filesort
  topic: 03.database
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 索引优化
  tags: [03.database, 联合索引, filesort, EXPLAIN, 索引优化, ORDER BY]
-->

# 联合索引明明覆盖了 WHERE 和 ORDER BY，为什么 explain 还会显示 Using filesort？

> **一句话定位**：联合索引覆盖了 WHERE + ORDER BY 的列，但 EXPLAIN 仍显示 `Using filesort` —— 这是面试高频陷阱，根因通常是 **排序方向不一致 / 范围查询截断 / 隐式类型转换 / 字符集 collation / 索引列不连续** 五大原因之一。

> **同模块兄弟**：[mysql-index-failure](../mysql-index-failure/) 讲 10 种索引失效场景；本文专注 **联合索引 + filesort** 的排查。

---

## 引子：索引明明覆盖了，为什么还 filesort？

```text
场景：线上慢查询告警，SQL 如下——
  SELECT * FROM orders WHERE user_id = 100 ORDER BY create_time;
  已有联合索引 idx_uid_ctime(user_id, create_time)

EXPLAIN 结果：
  type: ref
  Extra: Using filesort  ← ⚠️ 明明索引覆盖了 WHERE + ORDER BY！

查询耗时：无 filesort 时 2ms，有 filesort 时 380ms（190 倍差距）
```

联合索引完全覆盖了 WHERE 和 ORDER BY 的列，按道理应该直接走索引有序扫描，为什么 EXPLAIN 还显示 `Using filesort`？这通常是 5 个原因之一：排序方向不一致、范围查询截断、隐式类型转换、字符集 collation 差异、索引列不连续。每一个都能让索引"看得见却用不上"。

---

## 🎯 面试高频拷问

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

## ⚠️ 原因 1：排序方向不一致（ASC vs DESC）

**场景**：

```sql
-- 联合索引 (a ASC, b ASC)
CREATE INDEX idx_a_b ON t(a, b);

-- 查询
SELECT * FROM t WHERE a = 1 ORDER BY b DESC;
```

**问题**：
- MySQL 8.0 前**不支持降序索引**，索引默认 ASC
- ORDER BY DESC 无法利用 ASC 索引 → filesort

**修复**：
- MySQL 8.0+：创建降序索引 `CREATE INDEX idx_a_b ON t(a ASC, b DESC);`
- MySQL 5.7：调整 ORDER BY 方向（改为 ASC）或接受 filesort

**EXPLAIN 验证**：

```text
Extra: Using filesort  ← ⚠️ 排序方向不匹配
```

---

## ⚠️ 原因 2：范围查询截断索引

**场景**：

```sql
-- 联合索引 (a, b, c)
CREATE INDEX idx_a_b_c ON t(a, b, c);

-- 查询
SELECT * FROM t WHERE a > 1 ORDER BY b;
```

**问题**：
- WHERE 用了范围查询 `a > 1`
- 联合索引在范围查询后**截断**：a 列后的 b、c 列无法用于索引扫描
- ORDER BY b 无法利用索引 → filesort

**修复**：
- 调整索引顺序：把范围查询列放最后 `(b, c, a)`
- 或接受 filesort（范围查询 + 排序 + 数据量大时不可避免）

**EXPLAIN 验证**：

```text
type: range  ← ⚠️ 范围查询
key: idx_a_b_c
Extra: Using filesort  ← ⚠️ b 列无法用于排序
```

**关键规则**：
> 联合索引中，**范围查询（>、<、BETWEEN、LIKE）后的列无法用于索引扫描**。

---

## ⚠️ 原因 3：隐式类型转换

**场景**：

```sql
-- a 列是 VARCHAR
CREATE INDEX idx_a_b ON t(a, b);

-- 查询（a 传了数字）
SELECT * FROM t WHERE a = 123 ORDER BY b;
```

**问题**：
- a 列是 VARCHAR，但 WHERE 传了 INT
- MySQL 隐式转换：`VARCHAR → INT`（相当于对 a 列用了函数）
- 索引失效 → filesort

**修复**：
- 类型匹配：`WHERE a = '123'`（字符串加引号）
- 或调整表结构（a 列改为 INT）

**EXPLAIN 验证**：

```text
key: NULL  ← ⚠️ 索引未使用
Extra: Using filesort
```

---

## ⚠️ 原因 4：字符集 collation 不一致

**场景**：

```sql
-- 表字符集 utf8mb4
-- 查询时连接字符集 utf8
SELECT * FROM t WHERE a = 'abc' ORDER BY b;
```

**问题**：
- 表字符集 utf8mb4，连接字符集 utf8
- 排序规则（collation）不一致 → 索引无法用于排序

**修复**：
- 统一字符集：`SET NAMES utf8mb4;`
- 或调整表字符集（`ALTER TABLE t CONVERT TO CHARACTER SET utf8mb4;`）

**EXPLAIN 验证**：

```text
Extra: Using filesort  ← ⚠️ collation 不匹配
```

---

## ⚠️ 原因 5：ORDER BY 列在索引中不连续

**场景**：

```sql
-- 联合索引 (a, b, c)
CREATE INDEX idx_a_b_c ON t(a, b, c);

-- 查询（跳过 b 列）
SELECT * FROM t WHERE a = 1 ORDER BY c;
```

**问题**：
- ORDER BY c，但索引中 b 在 c 前面
- 跳过了 b 列 → c 列无法用于排序 → filesort

**修复**：
- 调整索引顺序：`(a, c)` 或 `(a, b, c)` 且查询时包含 b
- 或接受 filesort

**EXPLAIN 验证**：

```text
key: idx_a_b_c
Extra: Using filesort  ← ⚠️ c 列无法用于排序（跳过了 b）
```

---

## 🔍 排查步骤（4 步）

**第一步：看 EXPLAIN**

```sql
EXPLAIN SELECT * FROM t WHERE a = 1 ORDER BY b;
```

重点关注：
- `type`：是否 ALL（全表扫描）或 range（范围查询）
- `key`：是否用了预期索引
- `Extra`：是否有 `Using filesort`

**第二步：检查索引定义**

```sql
SHOW INDEX FROM t;
```

关注：
- 索引列顺序
- 排序方向（ASC / DESC，MySQL 8.0+）
- 字符集

**第三步：对照 5 大原因逐一排查**

| 原因 | 排查方法 |
|------|---------|
| 排序方向不一致 | 检查索引 ASC/DESC vs ORDER BY ASC/DESC |
| 范围查询截断 | 检查 WHERE 是否用了 >、<、BETWEEN、LIKE |
| 隐式类型转换 | 检查 WHERE 条件类型 vs 索引列类型 |
| 字符集 collation | 检查表字符集 vs 连接字符集 |
| 索引列不连续 | 检查 ORDER BY 列在索引中是否连续 |

**第四步：修复 + 验证**

- 修复后重新 EXPLAIN，确认 `Extra` 无 `Using filesort`
- 或用 `EXPLAIN FORMAT=JSON` 查看详细计划

---

## 💡 30 秒面试话术

> "联合索引覆盖了 WHERE + ORDER BY 但仍 filesort，通常是 5 大原因之一：
>
> **第一**：排序方向不一致。索引是 ASC，但 ORDER BY 是 DESC。MySQL 8.0 前不支持降序索引，8.0+ 可以创建 DESC 索引。
>
> **第二**：范围查询截断。WHERE 用了范围查询（如 a > 1），联合索引在 a 列后截断，b 列无法用于排序。修复：调整索引顺序，把范围查询列放最后。
>
> **第三**：隐式类型转换。WHERE 条件类型与索引列类型不匹配（如字符串传了数字），相当于对索引列用了函数 → 索引失效。
>
> **第四**：字符集 collation 不一致。表字符集和连接字符集不同，排序规则不匹配 → 索引无法用于排序。
>
> **第五**：ORDER BY 列在索引中不连续。跳过了中间列（如索引是 a,b,c，但 ORDER BY c），c 列无法用于排序。
>
> **排查步骤**：EXPLAIN 看 Extra → SHOW INDEX 检查索引定义 → 逐一对照 5 大原因 → 修复后重新 EXPLAIN 验证。"

---

## 📚 深度阅读

- [主模块深度文章](../../../03.data-stack/01-database/04-index/composite-index-filesort/README.md) — 5 大原因详解 + EXPLAIN 排查 + 修复方案
- [mysql-index-failure](../mysql-index-failure/) — 10 种索引失效场景

---

← [返回: Database 咬文嚼字](../README.md)
