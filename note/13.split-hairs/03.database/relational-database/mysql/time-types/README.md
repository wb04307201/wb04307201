# MySQL 时间类型选型指南

## 一、核心原理

MySQL 提供了多种时间数据类型，每种类型在存储格式、范围、时区处理和性能上存在显著差异。正确选择时间类型是数据库设计的基础，直接影响数据一致性、存储效率和跨时区兼容性。

**五大时间类型对比：**

| **类型** | **存储格式** | **存储范围** | **存储空间** | **时区处理** | **自动更新** | **适用场景** |
|---------|------------|------------|------------|------------|------------|------------|
| **DATE** | `YYYY-MM-DD` | `1000-01-01`到`9999-12-31` | 3字节 | 无时区信息 | 不支持 | 仅需日期的场景（如生日、节假日） |
| **TIME** | `HH:MM:SS` | `-838:59:59`到`838:59:59` | 3字节 | 无时区信息 | 不支持 | 具体时间点或时长（如会议开始时间） |
| **DATETIME** | `YYYY-MM-DD HH:MM:SS` | `1000-01-01 00:00:00`到`9999-12-31 23:59:59` | 8字节 | 固定存储，无时区转换 | 需手动设置或触发器 | 历史记录、未来日期（如订单创建时间） |
| **TIMESTAMP** | `YYYY-MM-DD HH:MM:SS` | `1970-01-01 00:00:01` UTC到`2038-01-19 03:14:07` UTC | 4字节 | 自动转换为UTC存储，检索时按会话时区转换 | 支持`DEFAULT CURRENT_TIMESTAMP`和`ON UPDATE CURRENT_TIMESTAMP` | 需时区同步的场景（如日志、跨时区应用） |
| **YEAR** | `YYYY` | `1901`到`2155` | 1字节 | 无时区信息 | 不支持 | 仅需年份的场景（如出生年份、年度统计） |

**关键差异解析：**

- **时区处理机制**：TIMESTAMP 在写入时将本地时间转换为 UTC 存储，读取时再根据会话时区转换回本地时间；DATETIME 则原样存储，不做任何时区转换。这意味着当服务器时区改变时，TIMESTAMP 显示的值会变化，而 DATETIME 保持不变。
- **2038年问题**：TIMESTAMP 使用 4 字节有符号整数存储 Unix 时间戳，最大值对应 2038-01-19 03:14:07 UTC，超出此范围会溢出。DATETIME 使用 8 字节，支持到 9999 年，不存在此问题。
- **存储效率**：TIMESTAMP 占用 4 字节，是 DATETIME 的一半，在大规模数据表中可显著节省存储空间。但 MySQL 8.0 引入了 fractional seconds 支持后，两者都可能额外占用 0-3 字节存储小数秒精度。

## 二、代码示例

**建表语句示例：**

```sql
-- 用户表：结合使用 DATETIME 和 TIMESTAMP
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(64) NOT NULL,
    birthday DATE NOT NULL,                    -- 生日：只需日期
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间：自动记录，支持时区
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- 更新时间：自动更新
    last_login DATETIME,                       -- 最后登录：固定时间点，不随时区变化
    birth_year YEAR                            -- 出生年份：仅年份
);

-- 订单表：使用 DATETIME 避免 2038 问题
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    order_time DATETIME NOT NULL,              -- 订单时间：长期历史数据
    expected_delivery DATETIME,                -- 预计送达：未来日期可能超过 2038
    status VARCHAR(20)
);

-- 日志表：使用 TIMESTAMP 节省空间
CREATE TABLE operation_logs (
    log_id BIGINT PRIMARY KEY,
    action VARCHAR(100),
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 日志时间：近期数据，无需担心 2038
);
```

**时区转换操作：**

```sql
-- 查看当前时区设置
SELECT @@global.time_zone, @@session.time_zone;

-- 设置会话时区
SET time_zone = '+08:00';          -- 北京时间
SET time_zone = 'Asia/Shanghai';   -- 使用时区名称

-- 时区转换函数
SELECT CONVERT_TZ('2024-01-01 12:00:00', '+00:00', '+08:00') AS beijing_time;
-- 输出: 2024-01-01 20:00:00

-- 跨时区查询示例
SELECT 
    created_at AS utc_time,
    CONVERT_TZ(created_at, '+00:00', '+08:00') AS beijing_time,
    CONVERT_TZ(created_at, '+00:00', '+09:00') AS tokyo_time
FROM operation_logs;
```

**Java 层面对接：**

```java
// JDBC 连接字符串中指定时区
String url = "jdbc:mysql://localhost:3306/mydb?serverTimezone=Asia/Shanghai&useLegacyDatetimeCode=false";

// Java 8+ LocalDateTime 与 MySQL DATETIME 映射
@Entity
public class Order {
    @Id
    private Long orderId;
    
    @Column(name = "order_time")
    private LocalDateTime orderTime;  // 对应 DATETIME
    
    @Column(name = "created_at")
    private Instant createdAt;        // 对应 TIMESTAMP
}
```

## 三、常见陷阱

**陷阱1：2038年溢出问题**

```sql
-- 错误：插入超出 TIMESTAMP 范围的值
INSERT INTO logs (log_time) VALUES ('2040-01-01 00:00:00');
-- 报错: Data truncation: Incorrect datetime value

-- 正确：长期数据使用 DATETIME
ALTER TABLE logs MODIFY COLUMN log_time DATETIME;
```

**陷阱2：时区配置不一致导致数据混乱**

```sql
-- 场景：服务器时区从 +08:00 改为 +00:00 后，TIMESTAMP 显示值变化
-- 插入时（时区 +08:00）
INSERT INTO users (username, created_at) VALUES ('Alice', '2024-01-01 12:00:00');
-- 实际存储 UTC: 2024-01-01 04:00:00

-- 查询时（时区改为 +00:00）
SELECT created_at FROM users WHERE username = 'Alice';
-- 返回: 2024-01-01 04:00:00（而非原始的 12:00:00）
```

**陷阱3：索引失效**

```sql
-- 错误：在时间列上使用函数，导致索引失效
SELECT * FROM orders WHERE YEAR(order_time) = 2024;  -- 全表扫描

-- 正确：使用范围查询，利用索引
SELECT * FROM orders 
WHERE order_time >= '2024-01-01' AND order_time < '2025-01-01';
```

**陷阱4：零日期处理**

```sql
-- MySQL 默认允许 '0000-00-00'，但这不是合法日期
-- 建议设置严格的 SQL 模式
SET sql_mode = 'NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- 插入零日期将报错
INSERT INTO users (birthday) VALUES ('0000-00-00');  -- Error
```

**陷阱5：DST（夏令时）导致的歧义**

```sql
-- 在实行夏令时的地区，某些时间点会出现两次
-- 例如美国东部时间 2024-11-03 01:30:00 可能出现两次
-- 建议使用 UTC 存储 TIMESTAMP，在应用层处理本地时间转换
```

## 四、最佳实践

**1. 选型决策树**

```
需要存储时间吗？
├── 仅需日期 → DATE（生日、节假日）
├── 仅需时间 → TIME（营业时间、课程表）
├── 仅需年份 → YEAR（成立年份、年度统计）
└── 需要完整时间
    ├── 需要时区自动转换 → TIMESTAMP（日志、用户活动记录）
    │   └── 数据范围是否超过 2038？
    │       ├── 是 → DATETIME
    │       └── 否 → TIMESTAMP
    └── 不需要时区转换 → DATETIME（合同签署、财务报表）
```

**2. 统一时区策略**

- 数据库全局时区设置为 UTC：`default_time_zone='+00:00'`
- 应用层根据用户所在地进行时区转换
- 前端展示时使用 JavaScript 的 `Intl.DateTimeFormat` 进行本地化

**3. 索引优化**

```sql
-- 为高频查询的时间字段建立索引
CREATE INDEX idx_order_time ON orders (order_time);

-- 复合索引：时间 + 状态
CREATE INDEX idx_status_time ON orders (status, order_time);

-- 覆盖索引：避免回表
CREATE INDEX idx_covering ON orders (order_time, status, amount);
```

**4. 分区表策略**

```sql
-- 按时间范围分区，提升查询性能
CREATE TABLE operation_logs (
    log_id BIGINT,
    action VARCHAR(100),
    log_time DATETIME
) PARTITION BY RANGE (YEAR(log_time)) (
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);
```

**5. 自动时间戳管理**

```sql
-- 利用 MySQL 自动特性，减少应用层代码
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 对于 DATETIME，可使用触发器实现类似功能
DELIMITER $$
CREATE TRIGGER before_update_users
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END$$
DELIMITER ;
```

## 五、面试话术

**面试官：DATETIME 和 TIMESTAMP 有什么区别？**

回答要点：
1. **存储空间**：TIMESTAMP 4 字节，DATETIME 8 字节
2. **时区处理**：TIMESTAMP 会自动进行 UTC 转换，DATETIME 原样存储
3. **时间范围**：TIMESTAMP 到 2038 年，DATETIME 到 9999 年
4. **自动更新**：TIMESTAMP 支持 `ON UPDATE CURRENT_TIMESTAMP`，DATETIME 需要触发器
5. **选型建议**：跨时区用 TIMESTAMP，长期历史数据用 DATETIME

**面试官：如何处理跨时区的时间存储？**

推荐方案：
- 数据库统一使用 UTC 时区存储 TIMESTAMP
- 后端接收请求时转换为 UTC 存入数据库
- 查询返回给前端时，由前端根据用户浏览器时区进行展示
- 避免在数据库中混用多个时区，保证数据一致性

**面试官：2038年问题如何解决？**

解决方案：
- 短期：评估业务数据范围，确认是否需要存储 2038 年之后的数据
- 中期：将可能超出的字段从 TIMESTAMP 改为 DATETIME
- 长期：新建表时直接使用 DATETIME，避免后续迁移成本
- 注意：修改现有字段类型会锁表，需在低峰期执行

## 六、交叉引用

- **相关主题**：[MySQL 事务隔离级别](../isolation/README.md) - 理解 MVCC 中的版本链与时间戳
- **性能优化**：[MySQL 索引优化](../../../../../03.database/04-index/README.md) - 时间字段的索引策略
- **JVM 关联**：[Java 日期时间API](../../../../../01.java/concepts/date-time/README.md) - Java 层面的时间处理
