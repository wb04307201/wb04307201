# MySQL SQL 调优全流程指南

## 一、核心原理

SQL 调优的本质是**减少数据访问量**和**优化执行路径**，将数据库的资源消耗（CPU、IO、内存）降到最低。MySQL 查询的执行流程决定了优化的切入点：

### 1. 查询执行链路
```
客户端请求
    ↓
查询缓存（8.0 已移除）
    ↓
解析器（Parser）：语法分析 → AST
    ↓
预处理器（Preprocessor）：语义检查、表名/列名解析
    ↓
优化器（Optimizer）：生成执行计划（基于成本模型 CBO）
    ↓
执行器（Executor）：调用存储引擎接口
    ↓
存储引擎（InnoDB/MyISAM）：返回数据
    ↓
结果集返回客户端
```

### 2. 优化器的成本模型
MySQL 优化器基于**统计信息**估算不同执行计划的成本，选择最小的方案：
- **I/O 成本**：读取数据页和索引页的次数（主要因素）。
- **CPU 成本**：行记录的条件判断、排序、聚合等操作。
- **内存成本**：临时表、排序缓冲区的使用。

优化器的决策依据存储在 `information_schema.STATISTICS` 和 InnoDB 的内部统计表中，可通过 `ANALYZE TABLE` 更新。

### 3. 调优的核心原则
- **少取**：减少扫描行数（使用索引）、减少返回列数（避免 SELECT *）。
- **少算**：避免复杂计算（函数、表达式下推），利用覆盖索引。
- **少传**：减少网络传输（分页、分批）。
- **少锁**：缩小锁范围（精确索引），缩短事务时间。

---

## 二、代码示例

以下展示从问题定位到优化落地的完整流程：

```sql
-- ==================== 步骤1：定位慢查询 ====================
-- 开启慢查询日志
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;  -- 超过1秒的记录
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- 或使用 Performance Schema（无需重启）
UPDATE performance_schema.setup_consumers
SET ENABLED = 'YES'
WHERE NAME LIKE '%statements_digest%';

-- ==================== 步骤2：EXPLAIN 分析 ====================
-- 典型慢查询
SELECT u.username, o.order_no, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
  AND o.create_time > '2024-01-01'
ORDER BY o.create_time DESC
LIMIT 10;

-- 执行计划分析
EXPLAIN FORMAT=JSON
SELECT u.username, o.order_no, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
  AND o.create_time > '2024-01-01'
ORDER BY o.create_time DESC
LIMIT 10;

-- EXPLAIN 输出关键字段解读：
-- id: 1                    ← 连接顺序
-- select_type: SIMPLE      ← 简单查询
-- table: u                 ← 访问 users 表
-- type: ALL                ← ⚠️ 全表扫描！需要优化
-- possible_keys: idx_status← 可用索引
-- key: NULL                ← ⚠️ 实际未使用索引
-- rows: 100000             ← ⚠️ 扫描10万行
-- Extra: Using filesort    ← ⚠️ 文件排序，效率低

-- ==================== 步骤3：添加索引优化 ====================
-- 优化1：为 users 表的 status 列添加索引
CREATE INDEX idx_users_status ON users(status);

-- 优化2：为 orders 表添加联合索引（覆盖 WHERE + JOIN + ORDER BY）
CREATE INDEX idx_orders_user_time ON orders(user_id, create_time);

-- 验证优化效果
EXPLAIN SELECT ...;
-- 期望看到：
-- table: u, type: ref, key: idx_users_status, rows: 5000
-- table: o, type: ref, key: idx_orders_user_time, rows: 10

-- ==================== 步骤4：SQL 重写优化 ====================
-- 反模式1：子查询嵌套
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- 优化：改为 JOIN
SELECT DISTINCT u.*
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.amount > 1000;

-- 反模式2：函数导致索引失效
SELECT * FROM orders
WHERE YEAR(create_time) = 2024;  -- ⚠️ 对列使用函数

-- 优化：范围查询
SELECT * FROM orders
WHERE create_time >= '2024-01-01' AND create_time < '2025-01-01';

-- 反模式3：隐式类型转换
SELECT * FROM users WHERE phone = 13800138000;  -- ⚠️ 数字字面量

-- 优化：字符串匹配
SELECT * FROM users WHERE phone = '13800138000';

-- 反模式4：大分页性能差
SELECT * FROM orders ORDER BY id LIMIT 1000000, 10;  -- ⚠️ 扫描100万行

-- 优化：延迟关联（先通过索引筛选主键，再回表取完整数据）
SELECT o.*
FROM orders o
INNER JOIN (
    SELECT id FROM orders ORDER BY id LIMIT 1000000, 10
) tmp ON o.id = tmp.id;

-- ==================== 步骤5：参数调优 ====================
-- 核心内存参数（my.cnf 配置）
[mysqld]
# InnoDB 缓冲池（设为物理内存的 60%-80%）
innodb_buffer_pool_size = 8G

# 日志文件大小（影响写入性能）
innodb_log_file_size = 1G

# 刷新策略（性能 vs 可靠性权衡）
innodb_flush_log_at_trx_commit = 2  # 每秒刷日志
sync_binlog = 0                      # 异步刷 binlog

# 排序和临时表
sort_buffer_size = 4M                # 每个会话的排序缓冲区
tmp_table_size = 64M                 # 内存临时表上限
max_heap_table_size = 64M

# 连接管理
max_connections = 500
wait_timeout = 300                   # 空闲连接超时释放

-- ==================== 步骤6：监控与持续优化 ====================
-- 查看实时慢查询
SELECT * FROM performance_schema.events_statements_current
ORDER BY TIMER_WAIT DESC
LIMIT 10;

-- 查看历史统计
SELECT
    DIGEST_TEXT,
    COUNT_STAR AS exec_count,
    SUM_TIMER_WAIT / 1e12 AS total_latency_sec,
    AVG_TIMER_WAIT / 1e9 AS avg_latency_ms,
    SUM_ROWS_EXAMINED AS rows_examined
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;

-- 查看未使用的索引
SELECT * FROM sys.schema_unused_indexes;

-- 查看冗余索引
SELECT * FROM sys.schema_redundant_indexes;
```

---

## 三、常见陷阱

### 1. 索引越多越好？
**误区**：给所有 WHERE 条件的列都加上索引。
**真相**：
- 每个索引都需要维护（INSERT/UPDATE/DELETE 时更新 B+ 树），写操作开销增加。
- 优化器可能选择错误的索引，反而降低性能。
- 索引占用额外存储空间，影响缓冲池命中率。

**最佳实践**：
- 单表索引数量控制在 5 个以内。
- 优先为高选择性（Distinct Value / Total Value > 0.1）的列建索引。
- 定期清理未使用索引：`DROP INDEX unused_idx ON table`。

### 2. 联合索引的顺序无关？
**误区**：`(a, b, c)` 和 `(c, b, a)` 效果一样。
**真相**：联合索引遵循**最左前缀原则**，顺序至关重要：
- `(status, create_time)` 支持 `WHERE status='x' ORDER BY create_time`
- `(create_time, status)` 不支持上述查询（create_time 是前缀）

**最佳实践**：
- 等值条件列在前，范围/排序列在后。
- 高选择性列在前（区分度高的列能更快缩小范围）。

### 3. COUNT(*) vs COUNT(1) vs COUNT(column)？
| 写法 | 含义 | 性能 |
|------|------|------|
| `COUNT(*)` | 统计总行数（含 NULL） | ⭐⭐⭐ 最快（优化器特殊处理） |
| `COUNT(1)` | 统计总行数（含 NULL） | ⭐⭐⭐ 同上（等价优化） |
| `COUNT(column)` | 统计非 NULL 行数 | ⭐⭐ 需检查列值 |
| `COUNT(DISTINCT column)` | 统计去重行数 | ⭐ 最慢（需排序/哈希） |

**最佳实践**：统一使用 `COUNT(*)`，语义清晰且性能最优。

### 4. OR 条件一定能用索引？
```sql
-- ❌ 部分列无索引，导致全表扫描
SELECT * FROM users WHERE email = 'x@example.com' OR age = 25;
-- 若只有 email 有索引，age 无索引，优化器可能放弃索引改用全表扫描

-- ✅ 改写为 UNION
SELECT * FROM users WHERE email = 'x@example.com'
UNION ALL
SELECT * FROM users WHERE age = 25;
```

### 5. LIMIT 就能解决大分页？
```sql
-- ❌ 深分页依然很慢
SELECT * FROM orders ORDER BY id LIMIT 1000000, 10;
-- 即使有主键索引，也需要扫描 100 万行再丢弃前 999,990 行

-- ✅ 游标分页（基于上次查询的最大 ID）
SELECT * FROM orders WHERE id > 999990 ORDER BY id LIMIT 10;
-- 直接定位起始位置，只扫描 10 行
```

---

## 四、最佳实践

### 1. 索引设计黄金法则
```sql
-- 法则1：覆盖索引（避免回表）
-- 查询只需要 id 和 name，建立联合索引包含这两列
CREATE INDEX idx_user_id_name ON users(id, name);
SELECT id, name FROM users WHERE id > 100;  -- Using index（覆盖索引）

-- 法则2：前缀索引（长字符串优化）
-- email 长度不均，取前 20 字符建立前缀索引
CREATE INDEX idx_email_prefix ON users(email(20));

-- 法则3：降序索引（MySQL 8.0+）
CREATE INDEX idx_create_time_desc ON orders(create_time DESC);
SELECT * FROM orders ORDER BY create_time DESC LIMIT 10;  -- 避免 filesort

-- 法则4：函数索引（MySQL 8.0+）
CREATE INDEX idx_year ON orders((YEAR(create_time)));
SELECT * FROM orders WHERE YEAR(create_time) = 2024;  -- 可使用索引
```

### 2. SQL 编写规范
```sql
-- ✅ 明确指定列名
SELECT username, email FROM users;

-- ❌ 避免 SELECT *
SELECT * FROM users;  -- 返回无用列，浪费 IO 和网络

-- ✅ 使用 EXISTS 替代 IN（子查询结果集大时）
SELECT * FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);

-- ✅ 批量插入代替逐条插入
INSERT INTO users (username, email) VALUES
('alice', 'alice@example.com'),
('bob', 'bob@example.com'),
('charlie', 'charlie@example.com');

-- ✅ 使用预处理语句（防止 SQL 注入 + 执行计划复用）
PREPARE stmt FROM 'SELECT * FROM users WHERE id = ?';
SET @id = 1;
EXECUTE stmt USING @id;
```

### 3. 分库分表策略
当单表数据量超过 **1000 万行**或**单表大小超过 10 GB**时，考虑水平拆分：
```sql
-- 按用户 ID 取模分表
CREATE TABLE orders_0 (...);
CREATE TABLE orders_1 (...);
CREATE TABLE orders_2 (...);

-- 路由规则：table_index = user_id % 3

-- 或使用中间件（ShardingSphere、MyCat）自动路由
```

### 4. 读写分离架构
```
主库（Master）：处理写操作和实时读
    ↓ 异步复制
从库1（Slave）：处理报表查询、离线分析
从库2（Slave）：处理备份、数据导出
```

### 5. 定期维护任务
```sql
-- 每周执行
ANALYZE TABLE users, orders;          -- 更新统计信息
OPTIMIZE TABLE users;                  -- 重建表，消除碎片

-- 每月执行
CHECK TABLE users EXTENDED;            -- 检查表完整性
SHOW TABLE STATUS LIKE 'users';        -- 查看数据量、索引大小
```

---

## 五、面试话术

**面试官**："请谈谈你的 SQL 调优经验。"

**参考回答**：
> "我的调优方法论可以概括为'**定位→分析→优化→验证**'四个步骤。
>
> **第一步是定位**，通过慢查询日志或 Performance Schema 找出耗时最长的 Top 10 SQL。我会关注两个指标：平均延迟和总延迟。有些 SQL 单次执行不快但调用频率极高，累计耗时可能超过真正的慢查询。
>
> **第二步是分析**，用 EXPLAIN 查看执行计划，重点关注 type（是否全表扫描）、key（是否用到预期索引）、rows（扫描行数）、Extra（是否有 Using filesort 或 Using temporary）。如果 type 是 ALL 或者 rows 远大于返回行数，说明有优化空间。
>
> **第三步是优化**，主要从三个层面入手：一是索引优化，比如添加缺失的索引、调整联合索引顺序、利用覆盖索引避免回表；二是 SQL 重写，比如把子查询改成 JOIN、避免对索引列使用函数、用 EXISTS 替代 IN；三是架构优化，比如读写分离、分库分表、引入缓存。
>
> **第四步是验证**，再次执行 EXPLAIN 确认执行计划改善，并通过基准测试对比优化前后的吞吐量和延迟。同时会观察生产环境的慢查询日志，确保没有回归。
>
> 举个实际案例：我们有一个订单查询接口响应时间超过 5 秒，通过 EXPLAIN 发现 orders 表的 create_time 列做了全表扫描。我添加了一个 `(user_id, create_time)` 的联合索引，同时把 SQL 中的 `YEAR(create_time)=2024` 改成了范围查询，最终响应时间降到 200 毫秒，提升了 25 倍。"

**加分项**：提及优化器追踪（`optimizer_trace`）、索引下推（ICP）、或讨论 MVCC 对查询性能的影响。

---

## 六、交叉引用

- InnoDB 索引结构见 [B+ 树原理](../../../bplus-tree/README.md)
- 事务隔离与锁见 [MVCC 机制](../../../mvcc/README.md)
