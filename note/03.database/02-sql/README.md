# SQL

> SQL(Structured Query Language)是用于管理关系型数据库的标准语言,本文涵盖 SQL 分类、核心语法、执行顺序与慢查询分析与优化。

> 最后更新: 2026-06-09

## 目录

- [一、SQL 分类](#一sql-分类)
- [二、核心语法](#二核心语法)
- [三、SQL 执行顺序](#三sql-执行顺序)
- [四、慢查询分析与优化](#四慢查询分析与优化)
- [五、SQL 最佳实践](#五sql-最佳实践)

---

## 一、SQL 分类

| 分类 | 全称 | 关键字 | 说明 |
|------|------|--------|------|
| **DDL** | Data Definition Language | `CREATE`、`ALTER`、`DROP`、`TRUNCATE` | 定义和修改数据库对象（表、索引、视图） |
| **DML** | Data Manipulation Language | `INSERT`、`UPDATE`、`DELETE` | 操作表中的数据 |
| **DQL** | Data Query Language | `SELECT` | 查询数据 |
| **DCL** | Data Control Language | `GRANT`、`REVOKE` | 控制权限 |
| **TCL** | Transaction Control Language | `BEGIN`、`COMMIT`、`ROLLBACK` | 事务控制 |

---

## 二、核心语法

### 1. SELECT（查询）

```sql
SELECT column1, column2, ...          -- 选择列
FROM table_name                        -- 数据来源
[WHERE condition]                      -- 行过滤条件
[GROUP BY column_name]                 -- 分组
[HAVING condition]                     -- 分组后过滤
[ORDER BY column_name [ASC|DESC]]      -- 排序
[LIMIT number OFFSET offset];          -- 分页
```

**常用函数**：

| 函数 | 说明 | 示例 |
|------|------|------|
| `COUNT(*)` | 统计行数 | `SELECT COUNT(*) FROM users` |
| `SUM(col)` | 求和 | `SELECT SUM(amount) FROM orders` |
| `AVG(col)` | 平均值 | `SELECT AVG(salary) FROM employees` |
| `MAX/MIN(col)` | 最大/最小值 | `SELECT MAX(price) FROM products` |
| `DISTINCT` | 去重 | `SELECT DISTINCT city FROM users` |

### 2. INSERT（插入）

```sql
-- 单行插入
INSERT INTO users (name, email) VALUES ('张三', 'zhangsan@example.com');

-- 多行插入
INSERT INTO users (name, email) VALUES
    ('李四', 'lisi@example.com'),
    ('王五', 'wangwu@example.com');

-- 从查询结果插入
INSERT INTO users_backup SELECT * FROM users;
```

### 3. UPDATE（更新）

```sql
UPDATE users
SET name = '张三丰', email = 'zhangsanfeng@example.com'
WHERE id = 1;
```

> **务必加 WHERE 条件**，否则会更新整张表的所有行。

### 4. DELETE（删除）

```sql
DELETE FROM users WHERE id = 1;

-- 删除所有数据（不推荐，用 TRUNCATE 代替）
-- DELETE FROM users;
```

### 5. JOIN（连接查询）

| 类型 | 说明 |
|------|------|
| `INNER JOIN` | 只返回两表匹配的行 |
| `LEFT JOIN` | 返回左表所有行 + 右表匹配行（不匹配则为 NULL） |
| `RIGHT JOIN` | 返回右表所有行 + 左表匹配行 |
| `FULL JOIN` | 返回两表所有行（MySQL 不直接支持，用 UNION 模拟） |
| `CROSS JOIN` | 笛卡尔积，返回所有组合 |

```sql
-- 查询用户及其订单
SELECT u.name, o.order_no, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

### 6. 子查询

```sql
-- WHERE 子查询
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- EXISTS 子查询（通常比 IN 更高效）
SELECT * FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

---

## 三、SQL 执行顺序

SQL 的**书写顺序**和**实际执行顺序**不同，理解执行顺序对优化查询至关重要。

### 书写顺序 vs 执行顺序

```
书写顺序：SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT
执行顺序：FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

| 执行步骤 | 说明 |
|---------|------|
| 1. `FROM` / `JOIN` | 确定数据来源表，执行表连接 |
| 2. `WHERE` | 对行进行过滤（**不能使用聚合函数**） |
| 3. `GROUP BY` | 按列分组 |
| 4. `HAVING` | 对分组结果过滤（**可以使用聚合函数**） |
| 5. `SELECT` | 选择列、计算表达式、生成别名 |
| 6. `DISTINCT` | 去重 |
| 7. `ORDER BY` | 排序（可以使用 SELECT 中的别名） |
| 8. `LIMIT` / `OFFSET` | 分页 |

### 示例

```sql
SELECT department, COUNT(*) AS cnt
FROM employees
WHERE salary > 5000
GROUP BY department
HAVING COUNT(*) > 5
ORDER BY cnt DESC
LIMIT 10;
```

**实际执行过程**：
1. `FROM employees` → 加载 employees 表
2. `WHERE salary > 5000` → 过滤薪资 > 5000 的行
3. `GROUP BY department` → 按部门分组
4. `HAVING COUNT(*) > 5` → 只保留人数 > 5 的部门
5. `SELECT department, COUNT(*) AS cnt` → 计算列
6. `ORDER BY cnt DESC` → 按人数降序
7. `LIMIT 10` → 取前 10 条

### 关键注意事项

- **WHERE 不能用聚合函数**（如 `SUM()`、`COUNT()`），因为聚合发生在 WHERE 之后
- **HAVING 可以用聚合函数**，因为它在 GROUP BY 之后执行
- **ORDER BY 可以用 SELECT 中的别名**，因为 SELECT 先于 ORDER BY 执行

---

## 四、慢查询分析与优化

### 1. 捕获慢查询

#### MySQL 慢查询日志

```sql
-- 查看当前配置
SHOW VARIABLES LIKE 'slow_query_log%';
SHOW VARIABLES LIKE 'long_query_time';

-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;  -- 阈值 2 秒
```

永久配置（`my.cnf`）：

```ini
[mysqld]
slow_query_log = 1
slow_query_log_file = /var/lib/mysql/slow.log
long_query_time = 2
```

#### PostgreSQL

```ini
# postgresql.conf
log_min_duration_statement = 2000  # 2000ms
```

### 2. 分析执行计划

使用 `EXPLAIN` 查看 SQL 的执行计划：

```sql
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
```

**MySQL EXPLAIN 关键字段**：

| 字段 | 说明 |
|------|------|
| **type** | 访问类型，从优到劣：`system` > `const` > `eq_ref` > `ref` > `range` > `index` > `ALL` |
| **key** | 实际使用的索引，NULL 表示未使用索引 |
| **rows** | 预估扫描行数，越小越好 |
| **Extra** | 关键额外信息（见下表） |

**Extra 常见值**：

| Extra | 含义 | 是否需优化 |
|-------|------|-----------|
| `Using index` | 覆盖索引，无需回表 | ✅ 好 |
| `Using where` | 存储引擎检索后由 Server 层过滤 | ⚠️ 一般 |
| `Using filesort` | 额外排序操作 | ❌ 需优化 |
| `Using temporary` | 使用临时表 | ❌ 需优化 |
| `Using index condition` | 索引下推（ICP） | ✅ 好 |

### 3. 常见慢查询原因与优化

#### 索引相关

| 原因 | 示例 | 优化方式 |
|------|------|---------|
| 缺少索引 | WHERE 字段无索引 | 添加索引 |
| 对索引列使用函数 | `WHERE YEAR(create_time) = 2023` | 改为 `WHERE create_time >= '2023-01-01'` |
| 对索引列做运算 | `WHERE price * 2 > 100` | 改为 `WHERE price > 50` |
| 违反最左前缀 | 联合索引 (a,b,c)，查询 `WHERE b=?` | 调整索引顺序或查询条件 |
| 隐式类型转换 | 字符串字段用数字查询 | 类型匹配 |

#### SQL 写法

| 优化点 | 差的写法 | 好的写法 |
|--------|---------|---------|
| 避免 `SELECT *` | `SELECT * FROM users` | `SELECT id, name FROM users`（配合覆盖索引） |
| 深分页 | `LIMIT 1000000, 20` | 游标分页：`WHERE id > last_id LIMIT 20` |
| 子查询改 JOIN | `WHERE id IN (SELECT ...)` | `JOIN` 或 `EXISTS` |
| 拆分大查询 | 一个复杂的多表 JOIN | 应用层拆分，多个简单查询 |

#### 索引优化实战

```sql
-- 问题 SQL
SELECT * FROM orders
WHERE user_id = 100 AND status = 'paid'
ORDER BY create_time DESC LIMIT 10;

-- EXPLAIN：type=ALL, key=NULL（全表扫描）

-- 优化：创建联合索引
ALTER TABLE orders ADD INDEX idx_user_status_time (user_id, status, create_time);

-- 再次 EXPLAIN：type=ref, key=idx_user_status_time, rows 大幅减少
```

> 联合索引顺序很重要：等值条件的列放前面，范围/排序的列放后面。

### 4. 优化验证

1. 再次 `EXPLAIN` 确认执行计划变优
2. 测试环境对比执行时间
3. 生产环境持续监控慢查询日志

---

## 五、SQL 最佳实践

1. **禁止 `SELECT *`**：只取需要的字段
2. **WHERE 条件加索引**：频繁用于 WHERE、JOIN、ORDER BY、GROUP BY 的字段
3. **避免在索引列上做函数运算**
4. **深分页用游标替代 OFFSET**
5. **用 EXISTS 替代大结果集的 IN 子查询**
6. **UPDATE/DELETE 务必加 WHERE**
7. **使用预编译语句（PreparedStatement）**：防止 SQL 注入，提升性能
8. **合理使用事务**：避免大事务长时间占用锁

---

## 相关章节

- [数据库基础知识](../01-fundamentals/README.md) — 核心概念、ER 图、范式
- [事务与并发控制](../03-transaction/README.md) — 合理使用事务的原则
- [索引](../04-index/README.md) — 索引是 SQL 优化核心
- [MySQL](../05-mysql/README.md) — MySQL EXPLAIN 深入解读

## 参考资料

- [MySQL 8.0 SQL Statement Syntax](https://dev.mysql.com/doc/refman/8.0/en/sql-statements.html)
- [PostgreSQL Documentation - SQL Commands](https://www.postgresql.org/docs/current/sql-commands.html)
- [Use The Index, Luke! - SQL Performance eBook](https://use-the-index-luke.com/)
- [SQL Window Functions Tutorial](https://www.postgresql.org/docs/current/tutorial-window.html)
