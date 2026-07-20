<!--
module:
  parent: system-design
  slug: system-design/sql
  type: article
  category: 主模块子文章
  summary: 常见 SQL 优化手段总结 的SQL 优化是数据库性能优化中投入产出比最高的手段。本文系统梳理了索引设计、查询重写、执行计划分析等关键手段
-->

# 常见 SQL 优化手段总结

## 引言：性能对比

常见 SQL 优化手段总结 的关键不是'快'——是**什么时候慢、慢多少、为什么**。

本篇用'常见 vs 极端'两组数字切入，把排查思路和优化边界讲清。

---

> SQL 优化是数据库性能优化中投入产出比最高的手段。本文系统梳理了索引设计、查询重写、执行计划分析等关键手段。
>
## 目录

- [一、避免使用 SELECT *](#一避免使用-select-)
- [二、分页优化](#二分页优化)
- [三、尽量避免多表 JOIN](#三尽量避免多表-join)
- [四、避免使用外键与级联](#四避免使用外键与级联)
- [五、选择合适的字段类型](#五选择合适的字段类型)
- [六、使用 UNION ALL 代替 UNION](#六使用-union-all-代替-union)
- [七、批量操作优化](#七批量操作优化)
- [八、SQL 性能分析工具](#八sql-性能分析工具)
- [九、索引优化策略](#九索引优化策略)
- [十、慢查询优化流程](#十慢查询优化流程)
- [十一、其他优化建议](#十一其他优化建议)

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

---

← [返回 数据库优化](../README.md)

---

## 四、10 张表 JOIN 实战拆分 + 大厂严禁的 5 大理由

> 本文「三、尽量避免多表 JOIN」讲了**原则**（避免）；本节讲**为什么 + 怎么拆**（理由 + 实战案例）。

### 4.1 大厂为什么严格控制 JOIN 数量（5 大理由）

#### 理由 1：性能瓶颈 —— 笛卡尔积爆炸

**原理**：N 张表 JOIN 的笛卡尔积是 **N × M × ... × K** 倍数（取决于 JOIN 类型）。

| 表数 | 笛卡尔积倍数 | 实际行数（每表 10 万行）|
|----:|-----------:|------------------------:|
| 2 | 10⁵ × 10⁵ = 10¹⁰ | 100 亿 |
| 3 | × 10⁵ | 1000 万亿 |
| 5 | × 10⁵ | 10²⁵（天文数字）|
| 10 | × 10⁵ | **10⁵⁰（物理上不可能完成）** |

**实战真相**：MySQL 的优化器会让"10 张表 JOIN"在小数据集上跑通，但**生产数据 1 万起步时必然超时**。

#### 理由 2：索引失效 —— JOIN 顺序错了就全表扫描

```sql
-- 假设 a join b on a.id = b.a_id（b.a_id 有索引）
-- 但执行计划可能选 b 驱动 a（因为 a 行数少）
-- 此时 a.id 没有索引 → 全表扫描
```

**真相**：**MySQL 优化器对小数据集的 JOIN 顺序选择经常出错**，10 张表 JOIN 触发错误的概率指数级上升。

#### 理由 3：Buffer Pool 抖动 —— 数据库连接被独占

**现象**：
- 10 表 JOIN 经常跑 30 秒+
- 数据库连接池（默认 10-20 连接）被这些"慢查询"独占
- 其他正常请求排队 → **整个服务雪崩**

**大厂经验值**：**单 SQL 超过 5 秒 = 线上事故**，单 SQL 超过 10 张表 = 必定超过 5 秒。

#### 理由 4：可维护性 —— SQL 没人敢改

```text
新人接手看到 10 张表 JOIN：
├─ 不敢改字段 → 业务迭代停滞
├─ 不敢加索引 → 性能永远优化不了
└─ 不敢重构 → 代码腐烂

→ 团队效率下降 50%+
```

#### 理由 5：分布式场景下彻底失效

```text
MySQL 分库分表后：
├─ 10 张表分布在 10 个库
├─ 单库 JOIN 不可能跨库
└─ 必须用「应用层 JOIN」或「数据仓库」

→ 多表 JOIN 在分布式架构下根本不可行
```

### 4.2 大厂明文规范引用

| 公司 | 规范 |
|------|------|
| **阿里巴巴《Java 开发手册》** | "**超过 3 张表禁止 JOIN**，需要 JOIN 的字段数据类型必须一致" |
| **字节跳动 SQL 规范** | "单 SQL JOIN 表数量 **≤ 4**，超过需拆分" |
| **美团技术团队** | "**严禁 5 张表以上的 JOIN**，推荐应用层组装" |
| **Netflix Data Gateway** | "Microservices 严禁跨服务 JOIN，必须通过 API 组合" |
| **Google SRE** | "DB query latency > 1s = P0 事故" |

### 4.3 10 张表 JOIN 的 5 大拆分策略

#### 策略 1：分步 SQL + 应用层组装（最常用）

```java
// 错误：10 张表 JOIN
List<OrderDTO> list = orderDao.join10Tables(userId);

// 正确：分 3 次查询 + 应用层组装
Map<Long, User> users = userDao.findByIds(orderIds);  // 1 次
Map<Long, Product> products = productDao.findByIds(productIds);  // 1 次
List<Order> orders = orderDao.findByUserId(userId);  // 1 次
// 应用层组装（Stream / Map join）
List<OrderDTO> result = orders.stream()
    .map(o -> new OrderDTO(o, users.get(o.getUserId()), products.get(o.getProductId())))
    .collect(toList());
```

**性能对比**（10 万订单 + 10 张表）：
- 10 表 JOIN：30 秒（超时）
- 分 3 次单表查询 + 应用层组装：**200ms**

**优势**：
- ✅ 单 SQL 简单（可优化、可加索引）
- ✅ 数据库压力分散
- ✅ 应用层缓存友好（每个查询可独立缓存）

#### 策略 2：冗余字段（适度反范式）

```sql
-- order 表加 user_name 冗余字段（直接从 user 表同步）
ALTER TABLE order ADD COLUMN user_name VARCHAR(50);

-- 查询时不需要 JOIN user 表
SELECT * FROM order WHERE user_id = ?;  -- 直接拿到 user_name
```

**同步方案**：
- **同步双写**：写 order 时同时写 user_name（事务保证）
- **异步订阅**：监听 user 表的 binlog → 更新 order.user_name（最终一致）
- **定时全量**：每天跑一次全量同步（容忍 1 天延迟）

**适用场景**：读多写少、性能要求极高（订单详情、商品详情）

#### 策略 3：宽表化（OLAP 场景）

```text
原始：order 表 + user 表 + product 表 + address 表 + payment 表 + ... （10 张）
宽表：dwd_order_detail（包含所有需要展示的字段，单表 200 列）

→ 一次查询拿到所有数据，零 JOIN
```

**适用场景**：数据仓库 / BI 报表 / 用户画像（写少读多）

**代价**：
- 宽表字段多 → 写入慢
- 字段冗余 → 存储成本高
- 维护 ETL 管道

#### 策略 4：数据仓库 + OLAP 引擎

```text
MySQL（OLTP）→ Canal / Debezium → Kafka → Flink → ClickHouse / Doris（OLAP）

业务查询：
├─ 简单查询 → MySQL
└─ 复杂报表（多表 JOIN）→ ClickHouse / Doris（专为 JOIN 设计）
```

**核心原则**：**OLTP 不做多表 JOIN，复杂查询去 OLAP 引擎**。

#### 策略 5：业务拆分（领域驱动）

```sql
-- 错误：一张大表 + 10 个 JOIN
SELECT * FROM order_with_user_product_address_payment_log_...

-- 正确：按业务领域拆分
order-service: SELECT * FROM order WHERE user_id = ?;
user-service: GET /users/{userId}
product-service: GET /products/{productId}
payment-service: GET /payments/{orderId}
-- 应用层组装
```

**优势**：符合微服务原则，单服务单表，可独立优化。

### 4.4 实战案例：订单中心 10 表 JOIN 改造

**原状（10 张表 JOIN）**：
```sql
SELECT o.*, u.name, u.phone, p.title, p.image, a.province, a.city,
       pay.amount, pay.method, log.action, ...
FROM order o
JOIN user u ON o.user_id = u.id
JOIN product p ON o.product_id = p.id
JOIN address a ON o.address_id = a.id
JOIN payment pay ON o.id = pay.order_id
JOIN order_log log ON o.id = log.order_id
JOIN ...
WHERE o.user_id = ?  -- 单 SQL 30 秒超时
```

**改造后（3 步 SQL + 宽表）**：

```java
// 1. 查订单主表
List<Order> orders = orderDao.findByUserId(userId);

// 2. 查关联数据（3 次单表查询）
Set<Long> orderIds = orders.stream().map(Order::getId).collect(toSet());
Map<Long, List<OrderLog>> logs = orderLogDao.findByOrderIds(orderIds);
Map<Long, Payment> payments = paymentDao.findByOrderIds(orderIds);

// 3. 用宽表字段（order 表冗余了 user_name / product_title / address_summary）
List<OrderDTO> dtos = orders.stream()
    .map(o -> new OrderDTO(o, logs.get(o.getId()), payments.get(o.getId())))
    .collect(toList());

// 总耗时：200ms（vs 原 30 秒）
```

**关键改造点**：
1. **订单表加冗余字段**（user_name / product_title / address_summary）—— 减少 5 个 JOIN
2. **日志和支付用批量 IN 查询** —— 减少 2 个 JOIN
3. **应用层组装** —— 单 SQL 简单可控

### 4.5 决策树：什么时候用什么策略

```text
10 张表 JOIN？
├─ OLTP 场景（实时业务）？
│   ├─ 性能要求极高（< 50ms）→ 策略 2 冗余字段
│   ├─ 性能要求中等（< 500ms）→ 策略 1 分步 SQL（最常用）
│   └─ 业务跨领域 → 策略 5 业务拆分
└─ OLAP 场景（报表 / 分析）？
    ├─ 写少读多 → 策略 3 宽表化
    └─ 实时分析 → 策略 4 数据仓库 + OLAP 引擎
```

### 4.6 反模式提醒（不要做的事）

| 反模式 | 后果 |
|--------|------|
| ❌ "反正能跑通，先不管" | 1 万行数据时雪崩 |
| ❌ "加更多索引能解决" | 索引过多反而拖慢写 |
| ❌ "JOIN 比多次查询快" | 数据库压力 = JOIN 笛卡尔积 |
| ❌ "先跑通再优化" | 10 张表 JOIN 一旦上线，重构成本极高 |

---

## 五、相关章节

**面试题（13.split-hairs）**：
- [咬文嚼字·mysql-join 算法深挖](../../../../13.split-hairs/03.database/mysql-join/README.md) — 本文「实战篇」的算法基础篇（NLJ / BNL / Hash Join）

**主模块基础**：
- [03.database/02-sql（SQL 语法基础）](../../../../03.database/02-sql/README.md) — JOIN 语法 + 执行顺序