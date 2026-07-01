<!--
module:
  parent: database
  slug: database/sql
  type: article
  category: 主模块子文章
  summary: SQL
-->

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
## 引言：反直觉代码

SQL 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

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
8. **合理使用事务**:避免大事务长时间占用锁

---

## 六、CTE(公用表表达式)

CTE(Common Table Expressions)从 MySQL 8.0 开始支持,用于将复杂查询拆分为命名临时结果集,大幅提升可读性。

### 1. 基本语法

```sql
WITH cte_name AS (
    SELECT ... FROM ...
)
SELECT * FROM cte_name;
```

### 2. 实战:多层嵌套查询改写

**改写前**(嵌套子查询,可读性差):

```sql
SELECT name FROM employees
WHERE dept_id IN (
    SELECT id FROM departments
    WHERE location_id IN (
        SELECT id FROM locations WHERE country = 'CN'
    )
);
```

**改写后**(CTE 链式,清晰):

```sql
WITH cn_locations AS (
    SELECT id FROM locations WHERE country = 'CN'
),
cn_depts AS (
    SELECT id FROM departments WHERE location_id IN (SELECT id FROM cn_locations)
)
SELECT name FROM employees WHERE dept_id IN (SELECT id FROM cn_depts);
```

### 3. 递归 CTE(组织树、层级数据)

```sql
-- 查询员工及其所有上级
WITH RECURSIVE org_tree AS (
    -- 锚点:起始行(顶级员工)
    SELECT id, name, manager_id, 1 AS level
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    -- 递归:下级
    SELECT e.id, e.name, e.manager_id, t.level + 1
    FROM employees e
    JOIN org_tree t ON e.manager_id = t.id
)
SELECT * FROM org_tree ORDER BY level;
```

---

## 七、窗口函数(Window Functions)

窗口函数从 MySQL 8.0 起支持,实现"分组但不聚合"的复杂分析,优于子查询方案。

### 1. 常用窗口函数

| 函数 | 用途 | 示例 |
|------|------|------|
| `ROW_NUMBER()` | 行号(1, 2, 3 不重复) | 每组前 N 名 |
| `RANK()` | 排名(1, 1, 3 跳号) | 成绩排名 |
| `DENSE_RANK()` | 排名(1, 1, 2 不跳号) | 同分连续排名 |
| `LAG(col, n)` | 往前第 n 行的值 | 与上一行对比 |
| `LEAD(col, n)` | 往后第 n 行的值 | 与下一行对比 |
| `SUM/AVG() OVER()` | 累计求和/平均 | 累计销售额 |

### 2. 经典案例

#### Top N 每组

```sql
-- 每个部门工资最高的 3 名员工
SELECT * FROM (
    SELECT
        dept_id, name, salary,
        ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn
    FROM employees
) t
WHERE rn <= 3;
```

#### 同比/环比

```sql
-- 销售额与上月对比
SELECT
    month, amount,
    LAG(amount, 1) OVER (ORDER BY month) AS last_month,
    amount - LAG(amount, 1) OVER (ORDER BY month) AS diff
FROM monthly_sales;
```

#### 累计求和

```sql
SELECT
    order_date, amount,
    SUM(amount) OVER (ORDER BY order_date) AS cumulative
FROM orders;
```

---

## 八、JOIN 算法详解

数据库执行 JOIN 时,有 3 种核心算法:

| 算法 | 原理 | 适用场景 |
|------|------|---------|
| **Nested Loop Join (NLJ)** | 双层循环,外表逐行驱动内表索引查找 | 内表有索引、结果集小 |
| **Hash Join** | 构建 Hash 表,探测匹配 | **MySQL 8.0.18+ 支持**,等值 JOIN、大表 |
| **Sort Merge Join** | 两表排序后双指针合并 | 范围 JOIN、已排序数据 |

```sql
-- EXPLAIN 中 Extra 字段提示算法
EXPLAIN SELECT * FROM orders o JOIN users u ON o.user_id = u.id;
-- Using join buffer (hash join)  → MySQL 8.0.18+
-- Using where; Using index       → NLJ
```

---

## 九、EXPLAIN ANALYZE(MySQL 8.0.18+)

`EXPLAIN ANALYZE` 在 EXPLAIN 基础上**实际执行 SQL**,返回真实耗时与行数。

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE age > 20 ORDER BY create_time DESC LIMIT 10;
```

输出示例:

```
-> Limit: 10 row(s)  (actual time=15.2..15.2 rows=10 loops=1)
    -> Sort: create_time DESC  (actual time=15.2..15.2 rows=10 loops=1)
        -> Index lookup on users using idx_age (age>20)  (cost=1200..1500 rows=5000)
            (actual time=0.5..12.3 rows=5000 loops=1)
```

> **关键指标**:`actual time` 真实耗时,`rows` 真实行数,`loops` 循环次数。三者结合可发现"预估 vs 实际"的统计信息偏差。

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
