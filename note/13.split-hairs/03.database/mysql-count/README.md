<!--
question:
  id: 03.database-count
  topic: 03.database
  difficulty: 未标
  frequency: 中频
  scenario_type: 性能对比
  tags: [03.database, MySQL, count]
-->

# MySQL COUNT(*) vs COUNT(1) vs COUNT(字段) 深度解析

## 引子：性能差 10 倍，你选哪个？

```sql
-- 统计用户表的总行数（1000 万条数据）
SELECT COUNT(*) FROM users;     -- 0.5 秒
SELECT COUNT(1) FROM users;     -- 0.5 秒（和 COUNT(*) 一样）
SELECT COUNT(id) FROM users;    -- 0.5 秒
SELECT COUNT(name) FROM users;  -- 2 秒（如果有 NULL 值，结果不同！）
```

`COUNT(*)` 和 `COUNT(1)` 性能一样？`COUNT(字段)` 和 `COUNT(*)` 结果可能不同？

关键区别：
- `COUNT(*)` 和 `COUNT(1)` → **统计所有行**（包括 NULL）
- `COUNT(字段)` → **只统计该字段非 NULL 的行**

---

> 📚 **前置知识**：[MySQL](../../../03.database/05-mysql/README.md)

## 一、核心原理

在 MySQL 中，`COUNT()` 函数用于统计行数，但不同参数的执行机制和语义存在差异。理解这些差异对于编写高效 SQL 至关重要。

**三种写法的核心区别：**

| **写法** | **统计逻辑** | **NULL 处理** | **索引利用** | **SQL 标准** |
|---------|------------|--------------|------------|------------|
| `COUNT(*)` | 统计表中的所有行 | 包含 NULL 值 | 使用最小索引或全表扫描 | SQL-92 标准 |
| `COUNT(1)` | 统计结果集行数（常量表达式） | 包含 NULL 值 | 使用最小索引或全表扫描 | 非标准扩展 |
| `COUNT(字段)` | 统计指定字段非 NULL 的行数 | 排除 NULL 值 | 若字段有索引可能走索引覆盖 | SQL-92 标准 |

**MySQL 优化器行为：**

在 MySQL 的 InnoDB 存储引擎中，`COUNT(*)` 和 `COUNT(1)` 的处理逻辑几乎完全相同：

1. **优化器重写**：MySQL 优化器会将 `COUNT(1)` 内部重写为 `COUNT(*)`，两者在执行计划层面没有区别。
2. **索引选择**：对于无 WHERE 条件的 `COUNT(*)`，InnoDB 会选择最小的二级索引进行扫描（如果存在），因为二级索引树比聚簇索引树更小，扫描成本更低。
3. **无索引回退**：如果没有二级索引，则会扫描聚簇索引（主键索引）。

**COUNT(字段) 的特殊性：**

- **NULL 过滤**：`COUNT(column)` 只统计该列值不为 NULL 的行，这与 `COUNT(*)` 的语义不同。
- **索引覆盖**：如果字段上有二级索引，且查询只需要该字段，MySQL 可能直接遍历二级索引而不回表，实现索引覆盖扫描（Covering Index）。
- **NOT NULL 约束**：如果字段定义了 `NOT NULL` 约束，`COUNT(字段)` 与 `COUNT(*)` 的结果相同，优化器也可能将其优化为 `COUNT(*)`。

**MyISAM vs InnoDB 的差异：**

- **MyISAM**：在元数据中存储了表的行数，对于 `SELECT COUNT(*) FROM table`（无 WHERE 条件）可以直接返回，时间复杂度 O(1)。但 MyISAM 不支持事务，已逐渐被淘汰。
- **InnoDB**：由于 MVCC 的存在，不同事务看到的行数可能不同（未提交的插入/删除），因此必须实时扫描索引树，时间复杂度 O(n)。

## 二、代码示例

**基础测试表结构：**

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL,
    email VARCHAR(128),              -- 允许 NULL
    age INT,                         -- 允许 NULL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created (created_at)
);

-- 插入测试数据
INSERT INTO users (name, email, age) VALUES 
('Alice', 'alice@example.com', 25),
('Bob', NULL, 30),                   -- email 为 NULL
('Charlie', 'charlie@example.com', NULL),  -- age 为 NULL
('David', NULL, NULL);               -- email 和 age 都为 NULL
```

**对比查询结果：**

```sql
-- 1. COUNT(*) - 统计所有行（包括 NULL）
SELECT COUNT(*) FROM users;
-- 结果: 4

-- 2. COUNT(1) - 与 COUNT(*) 相同
SELECT COUNT(1) FROM users;
-- 结果: 4

-- 3. COUNT(字段) - 排除 NULL 值
SELECT COUNT(email) FROM users;
-- 结果: 2（只有 Alice 和 Charlie 的 email 不为 NULL）

SELECT COUNT(age) FROM users;
-- 结果: 2（只有 Alice 和 Bob 的 age 不为 NULL）

-- 4. COUNT(主键) - 等价于 COUNT(*)
SELECT COUNT(id) FROM users;
-- 结果: 4
```

**EXPLAIN 分析执行计划：**

```sql
-- COUNT(*) 的执行计划
EXPLAIN SELECT COUNT(*) FROM users;
-- type: index, key: idx_email（选择最小的二级索引）
-- Extra: Using index

-- COUNT(1) 的执行计划（与 COUNT(*) 相同）
EXPLAIN SELECT COUNT(1) FROM users;
-- type: index, key: idx_email
-- Extra: Using index

-- COUNT(email) 的执行计划
EXPLAIN SELECT COUNT(email) FROM users;
-- type: index, key: idx_email（直接使用 email 索引）
-- Extra: Using index

-- 带 WHERE 条件的 COUNT
EXPLAIN SELECT COUNT(*) FROM users WHERE age > 20;
-- type: range, key: idx_age（如果 age 有索引）
-- Extra: Using where; Using index
```

**大表性能测试：**

```sql
-- 生成 100 万测试数据
DELIMITER $$
CREATE PROCEDURE insert_test_data(IN num INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    WHILE i <= num DO
        INSERT INTO users (name, email, age) 
        VALUES (CONCAT('user_', i), 
                IF(RAND() > 0.3, CONCAT('user_', i, '@example.com'), NULL),
                IF(RAND() > 0.2, FLOOR(RAND() * 50 + 18), NULL));
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

CALL insert_test_data(1000000);

-- 性能对比（100 万数据）
SELECT BENCHMARK(10, (SELECT COUNT(*) FROM users));      -- 约 0.5s
SELECT BENCHMARK(10, (SELECT COUNT(1) FROM users));      -- 约 0.5s（相同）
SELECT BENCHMARK(10, (SELECT COUNT(email) FROM users));  -- 约 0.6s（略慢，需检查 NULL）
```

## 三、常见陷阱

**陷阱1：误以为 COUNT(1) 比 COUNT(*) 快**

```sql
-- 错误认知：COUNT(1) 只计算常量，所以更快
SELECT COUNT(1) FROM users;  -- 并不比 COUNT(*) 快

-- 真相：MySQL 优化器将两者视为相同
-- 可通过 EXPLAIN 验证，两者的执行计划完全一致
```

**陷阱2：COUNT(字段) 忽略了 NULL 值**

```sql
-- 业务需求：统计有邮箱的用户数
SELECT COUNT(email) FROM users;
-- 注意：这会遗漏 email 为 NULL 的用户

-- 正确做法：明确业务语义
-- 如果想知道总用户数（无论是否有邮箱）
SELECT COUNT(*) FROM users;

-- 如果想知道有邮箱的用户数
SELECT COUNT(email) FROM users;

-- 如果想同时知道两者
SELECT 
    COUNT(*) AS total_users,
    COUNT(email) AS users_with_email,
    COUNT(*) - COUNT(email) AS users_without_email
FROM users;
```

**陷阱3：在大表上频繁执行 COUNT(*)**

```sql
-- 问题：每次 COUNT(*) 都需要扫描索引树，1000 万数据可能需要几秒
SELECT COUNT(*) FROM huge_table;  -- 耗时 3-5 秒

-- 解决方案1：使用近似值
SHOW TABLE STATUS LIKE 'huge_table';
-- Rows 字段给出近似值，基于统计信息

-- 解决方案2：维护计数器表
CREATE TABLE table_counters (
    table_name VARCHAR(64) PRIMARY KEY,
    row_count BIGINT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 通过触发器或应用层维护计数
INSERT INTO table_counters (table_name, row_count) 
VALUES ('huge_table', (SELECT COUNT(*) FROM huge_table))
ON DUPLICATE KEY UPDATE row_count = VALUES(row_count);
```

**陷阱4：COUNT(DISTINCT 字段) 的性能问题**

```sql
-- COUNT(DISTINCT) 需要排序或哈希去重，性能较差
SELECT COUNT(DISTINCT email) FROM users;  -- 100 万数据可能需要数秒

-- 优化方案：使用子查询或临时表
SELECT COUNT(*) FROM (
    SELECT DISTINCT email FROM users
) AS tmp;

-- 或者使用位图（Bitmap）等高级技术（MySQL 8.0+）
```

**陷阱5：忽略锁竞争**

```sql
-- 在高并发场景下，COUNT(*) 可能与写操作产生锁竞争
-- InnoDB 的 MVCC 允许非阻塞读，但某些情况下仍可能等待锁

-- 解决方案：使用快照读（一致性读）
START TRANSACTION WITH CONSISTENT SNAPSHOT;
SELECT COUNT(*) FROM users;
COMMIT;
```

## 四、最佳实践

**1. 默认使用 COUNT(*)**

```sql
-- 推荐：符合 SQL 标准，语义清晰，性能最优
SELECT COUNT(*) FROM users WHERE status = 'active';

-- 不推荐：COUNT(1) 虽然性能相同，但语义不如 COUNT(*) 清晰
SELECT COUNT(1) FROM users WHERE status = 'active';
```

**2. 需要排除 NULL 时使用 COUNT(字段)**

```sql
-- 统计有效数据量
SELECT 
    COUNT(*) AS total_rows,
    COUNT(email) AS valid_emails,
    COUNT(phone) AS valid_phones
FROM users;
```

**3. 利用索引优化 COUNT 查询**

```sql
-- 确保常用查询条件有合适的索引
CREATE INDEX idx_status ON users (status);

-- 复合索引覆盖常见查询
CREATE INDEX idx_status_created ON users (status, created_at);

-- 查询时会自动利用索引
SELECT COUNT(*) FROM users WHERE status = 'active' AND created_at > '2024-01-01';
```

**4. 分页场景避免 OFFSET + COUNT(*)**

```sql
-- 传统分页：需要两次查询（COUNT + SELECT）
SELECT COUNT(*) FROM users WHERE status = 'active';  -- 获取总数
SELECT * FROM users WHERE status = 'active' LIMIT 10 OFFSET 1000;  -- 获取数据

-- 游标分页：无需 COUNT，性能更好
SELECT * FROM users WHERE status = 'active' AND id > last_seen_id ORDER BY id LIMIT 10;

-- 前端展示"下一页"按钮而非总页数时，只需查询 LIMIT+1 条判断是否有更多
```

**5. 缓存 COUNT 结果**

```java
// 对于变化不频繁的表，可以缓存 COUNT 结果
@Cacheable(value = "userCount", ttl = 300)  // 缓存 5 分钟
public long getUserCount() {
    return userRepository.count();
}

// 或使用 Redis 缓存
String cacheKey = "count:users:active";
Long count = redisTemplate.opsForValue().get(cacheKey);
if (count == null) {
    count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM users WHERE status=?", Long.class, "active");
    redisTemplate.opsForValue().set(cacheKey, count, 5, TimeUnit.MINUTES);
}
```

**6. 使用 Approximate Count 算法**

```sql
-- HyperLogLog（Redis）：极小空间实现基数估算
PFADD users:hll user1 user2 user3
PFCOUNT users:hll  -- 近似去重计数，误差约 0.81%

-- MySQL 8.0+ 使用系统视图获取近似行数
SELECT TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'mydb' AND TABLE_NAME = 'users';
```

## 五、面试话术

**面试官：COUNT(*)、COUNT(1)、COUNT(字段) 有什么区别？**

回答要点：
1. **语义差异**：`COUNT(*)` 和 `COUNT(1)` 统计所有行（含 NULL），`COUNT(字段)` 只统计非 NULL 行
2. **性能比较**：在 MySQL 中，`COUNT(*)` 和 `COUNT(1)` 性能完全相同（优化器视为等价）
3. **索引利用**：三者都可能利用二级索引，`COUNT(字段)` 若字段有索引可实现覆盖扫描
4. **推荐使用**：优先使用 `COUNT(*)`，符合 SQL 标准；需要排除 NULL 时用 `COUNT(字段)`

**面试官：为什么 InnoDB 的 COUNT(*) 比 MyISAM 慢？**

回答要点：
- **MyISAM**：在元数据中存储行数，无 WHERE 条件时直接返回，O(1) 复杂度
- **InnoDB**：因 MVCC 机制，不同事务看到的行数不同，需实时扫描索引树，O(n) 复杂度
- **优化思路**：缓存计数、维护计数器表、使用近似值

**面试官：如何优化大表的 COUNT 查询？**

回答要点：
1. **索引优化**：确保查询条件有合适的二级索引，InnoDB 会选最小索引扫描
2. **缓存策略**：Redis 缓存 COUNT 结果，设置合理 TTL
3. **计数器表**：通过触发器或应用层维护实时计数
4. **近似查询**：接受统计信息的近似值（`SHOW TABLE STATUS`）
5. **架构调整**：读写分离、分库分表、使用 OLAP 引擎（ClickHouse）做分析

## 六、交叉引用

- **相关主题**：[MySQL索引优化](../../../03.database/04-index/README.md) - 理解二级索引与覆盖索引
- **延伸学习**：[MySQL事务隔离](../../../03.database/03-transaction/README.md) - MVCC机制对COUNT的影响
- **性能调优**：[MySQL慢查询分析](../tuning/README.md) - EXPLAIN执行计划解读

## 相关章节

- 深度阅读：[`03.database`](../../../03.database/README.md) — 主模块详细内容

← [返回数据库咬文嚼字](../README.md)
