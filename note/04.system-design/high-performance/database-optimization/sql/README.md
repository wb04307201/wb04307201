# 常见 SQL 优化手段总结

## 一、避免使用 SELECT *
### 原因分析
1. **资源消耗**：SELECT * 会消耗更多的 CPU 和内存资源，因为需要加载所有字段
2. **网络带宽**：无用字段增加网络带宽资源消耗，增加数据传输时间，尤其是大字段（如 varchar、blob、text）
3. **索引优化**：无法使用 MySQL 优化器的覆盖索引优化策略（覆盖索引是速度极快、效率极高的查询优化方式）
4. **维护性**：SELECT <字段列表> 可减少表结构变更带来的影响，提高代码可维护性

### 优化建议
```sql
-- 不推荐
SELECT * FROM users;

-- 推荐
SELECT id, username, email FROM users;
```

## 二、分页优化
### 深度分页问题
当查询偏移量过大时（如 LIMIT 1000000, 10），性能会急剧下降

#### 1. 范围查询（适用于ID连续）
```sql
-- 查询指定ID范围的数据
SELECT * FROM t_order 
WHERE id > 100000 AND id <= 100010 
ORDER BY id;

-- 通过记录上次查询结果的最后一条记录的ID进行下一页查询
SELECT * FROM t_order 
WHERE id > 100000 
LIMIT 10;
```

#### 2. 子查询优化
```sql
-- 通过子查询获取ID起始值
SELECT * FROM t_order 
WHERE id >= (SELECT id FROM t_order ORDER BY id LIMIT 1000000, 1) 
LIMIT 10;
```

#### 3. 延迟关联（推荐）
```sql
-- 使用INNER JOIN
SELECT t1.* FROM t_order t1
INNER JOIN (SELECT id FROM t_order ORDER BY id LIMIT 1000000, 10) t2
ON t1.id = t2.id;

-- 使用逗号连接
SELECT t1.* FROM t_order t1,
(SELECT id FROM t_order ORDER BY id LIMIT 1000000, 10) t2
WHERE t1.id = t2.id;
```

#### 4. 覆盖索引（最佳方案）
```sql
-- 建立覆盖索引
CREATE INDEX idx_code_type ON t_order(code, type);

-- 使用覆盖索引查询
SELECT id, code, type FROM t_order
ORDER BY code
LIMIT 1000000, 10;
```

### 覆盖索引优势
1. 避免回表操作，减少IO
2. 将随机IO变为顺序IO
3. 适用于范围查询和排序操作

## 三、尽量避免多表JOIN
### 优化原则
1. 超过三个表禁止JOIN
2. 需要JOIN的字段数据类型必须一致
3. 确保被关联字段有索引

### JOIN实现方式对比
| 实现方式 | 描述 | 性能 |
|---------|------|------|
| Simple Nested-Loop Join | 直接使用笛卡尔积实现JOIN | 最低 |
| Block Nested-Loop Join | 利用JOIN BUFFER优化 | 中等 |
| Index Nested-Loop Join | 使用索引的JOIN方式 | 最高 |

### 优化方案
#### 1. 单表查询+内存关联（推荐）
```java
// 伪代码示例
List<User> users = query("SELECT * FROM users WHERE age > 20");
List<Order> orders = query("SELECT * FROM orders WHERE user_id IN (?)", userIds);
// 在内存中关联users和orders
```

#### 2. 数据冗余设计
```sql
-- 在订单表中冗余用户名称
CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,
    user_name VARCHAR(50),  -- 冗余字段
    amount DECIMAL(10,2),
    -- 其他字段
);
```

## 四、避免使用外键与级联
### 原因
1. 对分库分表不友好
2. 增加数据库维护复杂度
3. 性能影响相对较小

### 替代方案
1. 在应用层实现数据完整性检查
2. 使用事务保证数据一致性

## 五、选择合适的字段类型
### 优化原则
1. 存储字节越小，性能越好
2. 选择最合适的数据类型而非最大的

### 具体优化方案
#### 1. IP地址存储
```sql
-- 存储为无符号整型
ALTER TABLE connections ADD COLUMN ip_num INT UNSIGNED;
UPDATE connections SET ip_num = INET_ATON('192.168.1.1');

-- 查询时转换回IP
SELECT INET_NTOA(ip_num) FROM connections;
```

#### 2. 日期类型选择
| 类型 | 存储空间 | 时区支持 | 范围 |
|------|---------|---------|------|
| DATETIME | 8字节 | 不支持 | 1000-01-01 00:00:00 到 9999-12-31 23:59:59 |
| TIMESTAMP | 4字节 | 支持 | 1970-01-01 00:00:01 UTC 到 2038-01-19 03:14:07 UTC |

#### 3. 主键选择
```sql
-- 自增ID作为主键（推荐）
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    -- 其他字段
);

-- 分库分表场景使用分布式ID
CREATE TABLE orders (
    order_no VARCHAR(32) PRIMARY KEY,  -- 如UUID或雪花ID
    -- 其他字段
);
```

## 六、使用UNION ALL代替UNION
### 区别对比
| 特性 | UNION | UNION ALL |
|------|-------|----------|
| 去重 | 是 | 否 |
| 排序 | 是 | 否 |
| 性能 | 较低 | 较高 |

### 使用建议
```sql
-- 需要去重时使用UNION
SELECT product_id FROM orders_2022
UNION
SELECT product_id FROM orders_2023;

-- 不需要去重时使用UNION ALL（推荐）
SELECT product_id FROM orders_2022
UNION ALL
SELECT product_id FROM orders_2023;
```

## 七、批量操作优化
### 优化方案
#### 1. 批量INSERT
```sql
-- 单条插入
INSERT INTO users(name, age) VALUES('张三', 20);
INSERT INTO users(name, age) VALUES('李四', 25);

-- 批量插入（推荐）
INSERT INTO users(name, age) VALUES 
('张三', 20),
('李四', 25),
('王五', 30);
```

#### 2. 批量UPDATE
```sql
-- 使用CASE WHEN批量更新
UPDATE products
SET price = CASE 
    WHEN id = 1 THEN 100
    WHEN id = 2 THEN 200
    ELSE price
END
WHERE id IN (1, 2);
```

## 八、SQL性能分析工具
### 1. SHOW PROFILE
```sql
-- 开启profiling
SET profiling = 1;

-- 执行SQL
SELECT * FROM large_table WHERE condition = value;

-- 查看性能分析
SHOW PROFILES;
SHOW PROFILE FOR QUERY 1;
```

### 2. EXPLAIN分析
```sql
EXPLAIN SELECT * FROM orders 
WHERE user_id = 100 
ORDER BY create_time DESC 
LIMIT 10;
```

### EXPLAIN关键字段说明
| 字段 | 含义 |
|------|------|
| id | 查询标识符 |
| select_type | 查询类型 |
| table | 访问的表 |
| type | 访问类型（ALL, index, range, ref, eq_ref, const, system） |
| possible_keys | 可能使用的索引 |
| key | 实际使用的索引 |
| key_len | 使用的索引长度 |
| rows | 预估需要检查的行数 |
| Extra | 额外信息（Using where, Using index等） |

## 九、索引优化策略
### 1. 索引创建原则
- 选择区分度高的列（如用户名>性别）
- 频繁作为查询条件的列
- 频繁需要排序或分组的列
- 经常用于表连接的列

### 2. 联合索引设计
```sql
-- 单列索引
CREATE INDEX idx_name ON users(name);
CREATE INDEX idx_age ON users(age);

-- 联合索引（推荐）
CREATE INDEX idx_name_age ON users(name, age);
```

### 3. 前缀索引优化
```sql
-- 为长字符串创建前缀索引
CREATE INDEX idx_email_prefix ON users(email(10));  -- 只索引前10个字符
```

### 4. 避免索引失效
#### 常见索引失效场景
1. 隐式类型转换
```sql
-- user_id是varchar类型，但传入数字
SELECT * FROM users WHERE user_id = 123;  -- 索引失效
```

2. 函数操作
```sql
-- 对索引列使用函数
SELECT * FROM orders WHERE DATE(create_time) = '2023-01-01';
```

3. LIKE以通配符开头
```sql
-- 以%开头的LIKE查询
SELECT * FROM products WHERE name LIKE '%手机';
```

4. OR条件使用不当
```sql
-- OR条件中有一个列没有索引
SELECT * FROM users WHERE name = '张三' OR age = 20;
```

### 5. 索引维护
```sql
-- 查看未使用的索引（MySQL 5.7+）
SELECT * FROM sys.schema_unused_indexes;

-- 删除无用索引
DROP INDEX idx_unused ON users;
```

## 十、慢查询优化流程
1. 开启慢查询日志
```sql
-- 配置文件设置
slow_query_log = 1
slow_query_log_file = /var/log/mysql/mysql-slow.log
long_query_time = 2  -- 超过2秒的查询记录
log_queries_not_using_indexes = 1  -- 记录未使用索引的查询
```

2. 分析慢查询日志
```bash
# 使用mysqldumpslow工具分析
mysqldumpslow -s t /var/log/mysql/mysql-slow.log  # 按时间排序
mysqldumpslow -s c /var/log/mysql/mysql-slow.log  # 按出现次数排序
```

3. 优化慢查询
- 添加合适的索引
- 重写SQL语句
- 考虑读写分离
- 对于复杂查询，考虑拆分为多个简单查询

## 十一、其他优化建议
1. **合理使用事务**：避免长事务，事务中操作的数据量不宜过大
2. **数据库参数调优**：根据服务器配置调整缓冲池大小等参数
3. **定期维护表**：
   ```sql
   ANALYZE TABLE orders;  -- 更新统计信息
   OPTIMIZE TABLE orders;  -- 整理表碎片（仅MyISAM和InnoDB）
   ```
4. **使用连接池**：避免频繁创建和销毁数据库连接
5. **读写分离**：将读操作分流到从库

通过综合应用这些优化手段，可以显著提高SQL查询性能，提升数据库整体运行效率。在实际优化过程中，应根据具体业务场景和性能测试结果选择最适合的优化方案。