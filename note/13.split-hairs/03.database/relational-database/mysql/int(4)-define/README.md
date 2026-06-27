# MySQL 中 `INT(4)` 的真正含义

## 引子：一个经典的误解

```sql
CREATE TABLE test (
    a INT(4),    -- 你以为只能存 0-9999？
    b INT(11),   -- 你以为能存更大的数？
    c INT(20)    -- 你以为范围更广？
);

-- 真相：a、b、c 的存储空间和数值范围完全一样！
-- 都是 4 字节，都是 -21 亿 ~ 21 亿
```

`INT(4)` 的括号里的数字**不代表数值范围，不代表存储大小**。它只代表一个已经被废弃的概念——**显示宽度**。

这道题是 MySQL 面试最高频的"陷阱题"。

---

> 📚 **前置知识**：[MySQL](../../../../../03.database/05-mysql/README.md)

## 一、核心原理

`INT(4)` 是 MySQL 中最容易被误解的数据类型定义之一。其核心要点可概括为：**括号中的数字与存储空间和数值范围完全无关，仅影响显示格式（且需配合 ZEROFILL 才生效）**。

### 1. INT 类型的固定特性
- **存储空间**：所有 INT 类型（无论 `INT(4)`、`INT(11)` 还是 `INT(20)`）始终占用 **4 字节（32 位）**。
- **数值范围**：
  - 有符号（SIGNED）：**-2,147,483,648 到 2,147,483,647**（约 ±21 亿）
  - 无符号（UNSIGNED）：**0 到 4,294,967,295**（约 ±42 亿）
- **括号数字的本质**：`INT(4)` 中的 `4` 是**显示宽度（Display Width）**元数据，不是长度限制，也不是精度声明。

### 2. 显示宽度的历史渊源
在 MySQL 早期版本（3.x/4.x），客户端工具功能简陋，数据库需要在服务端层面提供格式化能力。显示宽度就是为此设计的元数据：
- 当列定义了 `ZEROFILL` 属性时，查询结果会自动用前导零填充到指定宽度。
- 例如 `INT(4) ZEROFILL` 存储值 `5`，查询返回 `"0005"`；存储值 `12345`，返回 `"12345"`（超过宽度不截断）。

### 3. MySQL 8.0.17 的重大变更
从 MySQL 8.0.17 开始，**显示宽度已被废弃**：
- 创建表时指定的 `INT(4)` 会被自动转换为 `INT`，括号数字被忽略。
- `ZEROFILL` 属性仍然保留，但推荐使用 `LPAD()` 等 SQL 函数在应用层实现格式化。
- 这一变更体现了 MySQL 的设计哲学回归：**数据存储与展示分离**，数据库只负责存储，格式化交给前端或应用层。

---

## 二、代码示例

以下实验清晰展示 `INT(4)` 的真实行为：

```sql
-- ==================== 实验1：ZEROFILL 的填充效果 ====================
CREATE TABLE int_test (
    id INT PRIMARY KEY AUTO_INCREMENT,
    col_normal INT(4),           -- 普通 INT，括号无效
    col_zerofill INT(4) ZEROFILL -- 带 ZEROFILL，括号生效
);

INSERT INTO int_test (col_normal, col_zerofill) VALUES
(5, 5),
(123, 123),
(12345, 12345);  -- 超过4位，不截断

SELECT * FROM int_test;
-- 结果：
-- id | col_normal | col_zerofill
-- 1  | 5          | 0005        ← 填充到4位
-- 2  | 123        | 0123        ← 填充到4位
-- 3  | 12345      | 12345       ← 超过4位，原样显示

-- ==================== 实验2：数值范围不受括号影响 ====================
CREATE TABLE int_range_test (
    col_a INT(1),   -- 括号写1
    col_b INT(11),  -- 括号写11
    col_c INT(20)   -- 括号写20
);

-- 以下插入全部成功，证明括号不限制范围
INSERT INTO int_range_test VALUES
(2147483647, 2147483647, 2147483647);  -- 最大值
INSERT INTO int_range_test VALUES
(-2147483648, -2147483648, -2147483648); -- 最小值

-- 以下插入失败，超出 INT 范围
INSERT INTO int_range_test VALUES
(2147483648, 2147483648, 2147483648);  -- ERROR: Out of range

-- ==================== 实验3：MySQL 8.0.17+ 的废弃行为 ====================
-- 在 MySQL 8.0.17+ 执行
CREATE TABLE new_int_test (
    col INT(4)  -- 括号被忽略
);

SHOW CREATE TABLE new_int_test;
-- 结果：col INT  ← 括号数字消失

-- ==================== 实验4：应用层替代 ZEROFILL ====================
-- 推荐方式：用 LPAD 在查询时格式化
SELECT LPAD(col_normal, 4, '0') AS formatted
FROM int_test;
-- 结果：0005, 0123, 12345
```

**存储验证**：
```sql
-- 验证所有 INT 变体都占用 4 字节
SELECT
    COLUMN_NAME,
    COLUMN_TYPE,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,  -- NULL（整数无字符长度）
    NUMERIC_PRECISION,         -- 10（十进制位数）
    NUMERIC_SCALE              -- 0（小数位数）
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'int_test';
```

---

## 三、常见陷阱

### 1. 误认为 `INT(4)` 只能存 4 位数
这是最普遍的误解。很多开发者看到 `INT(4)` 以为最大只能存 `9999`，实际可以存到 `2147483647`。若业务确实需要限制范围（如年份、月份），应使用 `CHECK` 约束：
```sql
CREATE TABLE year_table (
    year INT CHECK (year BETWEEN 1900 AND 2100)
);
```

### 2. 误认为 `INT(4)` 比 `INT(11)` 节省空间
所有 INT 类型都占 4 字节，括号数字不影响存储。若想节省空间，应选择更小的数据类型：
- `TINYINT`：1 字节，范围 -128~127（或 0~255 UNSIGNED）
- `SMALLINT`：2 字节，范围 -32768~32767
- `MEDIUMINT`：3 字节，范围 -8388608~8388607
- `INT`：4 字节
- `BIGINT`：8 字节

### 3. ZEROFILL 隐式添加 UNSIGNED
在 MySQL 中，给列添加 `ZEROFILL` 属性会**自动将其设为 UNSIGNED**：
```sql
CREATE TABLE test (
    col INT(4) ZEROFILL
);
INSERT INTO test VALUES (-5);  -- ERROR: 负数不允许
```
这是因为填充前导零的概念对负数没有意义。

### 4. 忽视迁移兼容性
若项目需要从 MySQL 迁移到其他数据库（如 PostgreSQL、SQLite），`INT(n)` 语法可能不被支持。PostgreSQL 只有 `INTEGER`，没有宽度参数。提前避免使用显示宽度可以降低迁移成本。

### 5. ORM 框架的误导
某些 ORM 框架（如 Hibernate）在自动生成 DDL 时会输出 `INT(11)`，这只是框架的默认行为，不代表有特殊含义。可以通过自定义方言（Dialect）覆盖这种行为。

---

## 四、最佳实践

### 1. 根据数值范围选择数据类型
| 场景 | 推荐类型 | 理由 |
|------|----------|------|
| 年龄、月份、状态码 | `TINYINT` / `SMALLINT` | 范围足够，节省空间 |
| 用户 ID、订单 ID | `INT` | 覆盖绝大多数场景（±21 亿） |
| 全局唯一 ID、雪花算法 | `BIGINT` | 防止溢出 |
| 布尔值 | `TINYINT(1)` 或 `BOOLEAN` | 语义清晰 |
| 自增主键 | `INT UNSIGNED AUTO_INCREMENT` | 范围翻倍（0~42 亿） |

### 2. 避免使用 ZEROFILL
除非有遗留系统兼容需求，否则不建议在新项目中使用 `ZEROFILL`。原因：
- MySQL 8.0.17+ 已废弃该特性
- 格式化应在应用层或前端完成，符合关注点分离原则
- `ZEROFILL` 隐式添加 `UNSIGNED`，可能导致意外的负数拒绝

**替代方案**：
```java
// Java 应用层格式化
String formatted = String.format("%04d", value);  // 5 → "0005"

// SQL 层格式化（如需）
SELECT LPAD(column_name, 4, '0') FROM table;
```

### 3. 显式声明 SIGNED/UNSIGNED
对于边界敏感的业务（如库存、余额），显式声明符号性以避免歧义：
```sql
CREATE TABLE inventory (
    quantity INT UNSIGNED NOT NULL DEFAULT 0  -- 库存不能为负
);
```

### 4. 使用 CHECK 约束保证数据完整性
MySQL 8.0.16+ 支持 `CHECK` 约束，可在数据库层面强制业务规则：
```sql
CREATE TABLE user_profile (
    age INT CHECK (age >= 0 AND age <= 150),
    score INT CHECK (score >= 0 AND score <= 100)
);
```

### 5. 监控整数溢出风险
对于接近 INT 上限的场景（如用户数超 20 亿的社交平台），应提前规划迁移方案：
```sql
-- 在线修改为大类型（MySQL 8.0+ 支持 Online DDL）
ALTER TABLE users MODIFY id BIGINT UNSIGNED AUTO_INCREMENT;
```

---

## 五、面试话术

**面试官**："MySQL 中 `INT(4)` 的含义是什么？"

**参考回答**：
> "`INT(4)` 中的 `4` 是显示宽度，不是存储长度或数值范围限制。所有 INT 类型都固定占用 4 字节，有符号范围是 ±21 亿左右。
>
> 显示宽度只有在配合 `ZEROFILL` 属性时才生效，作用是查询时用前导零填充到指定位数。比如 `INT(4) ZEROFILL` 存 5 会显示为 0005。但这个特性在 MySQL 8.0.17 已经被废弃了，官方建议格式化工作在应用层完成。
>
> 在实际开发中，我不会通过括号数字来控制数据范围，而是根据业务需求选择合适的数据类型——小范围用 TINYINT 或 SMALLINT，大范围用 INT 或 BIGINT。如果需要限制取值范围，会用 CHECK 约束。
>
> 另外需要注意的是，ZEROFILL 会隐式将列设为 UNSIGNED，负数无法存入。在设计表结构时，我会显式声明 SIGNED 或 UNSIGNED，让意图更清晰。"

**加分项**：提及 MySQL 8.0.17 的版本变更，或讨论 Online DDL 修改整数类型的注意事项。

---

## 六、交叉引用

- MySQL 整数类型全览见 [MySQL核心](../../../../../03.database/05-mysql/README.md)

## 相关章节

- 深度阅读：[`03.database`](../../../../03.database/README.md) — 主模块详细内容
