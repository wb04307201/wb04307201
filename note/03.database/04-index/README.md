# 索引

索引（Index）是数据库为了加快数据检索而维护的一种数据结构。合理使用索引是 SQL 优化中最核心的手段。

---

## 一、为什么需要索引

没有索引时，数据库需要**全表扫描**（逐行遍历）来查找数据。索引通过维护有序的数据结构，将查找时间从 O(N) 降低到 O(log N) 甚至 O(1)。

| 操作 | 无索引 | 有 B+ 树索引 |
|------|--------|-------------|
| 查找 | O(N) 全表扫描 | O(log N) 树查找 |
| 100 万行查找次数 | ~100 万次 | ~20 次 |

---

## 二、索引数据结构

### 1. B+ 树（MySQL InnoDB 默认）

B+ 树是 MySQL InnoDB 引擎使用的核心索引结构。

**特点**：
- **非叶子节点**只存储键值，不存储数据（最大化每个节点能存的键数，降低树高）
- **叶子节点**存储完整数据行，且通过双向链表相连（支持范围查询）
- 3~4 层的 B+ 树可以索引数千万行数据

```
              [30, 60]                    ← 非叶子节点（只存键）
             /    |    \
        [10,20]  [40,50]  [70,80,90]      ← 非叶子节点
        / | \    / | \    / | | \
       ↓   ↓   ↓   ↓   ↓   ↓   ↓   ↓
     [10]-[20]-[30]-[40]-[50]-[60]-[70]-[80]-[90]  ← 叶子节点（双向链表）
       ↕         ↕         ↕         ↕
     数据行     数据行     数据行     数据行
```

**树高与数据量**（假设每个节点 16KB，每行 1KB）：

| 树高 | 可索引行数 |
|------|-----------|
| 2 层 | ~16,000 行 |
| 3 层 | ~2,500 万行 |
| 4 层 | ~40 亿行 |

### 2. Hash 索引

| 特性 | B+ 树索引 | Hash 索引 |
|------|----------|----------|
| 等值查询 | O(log N) | O(1) |
| 范围查询 | ✅ 支持 | ❌ 不支持 |
| 排序 | ✅ 支持 | ❌ 不支持 |
| 最左前缀 | ✅ 支持 | ❌ 不支持 |
| 使用引擎 | InnoDB（默认） | Memory（默认） |

> InnoDB 的**自适应哈希索引**（Adaptive Hash Index）会在内部自动为热点数据创建 Hash 索引，无需手动干预。

### 3. 全文索引

MySQL 5.6+ InnoDB 支持全文索引，底层使用**倒排索引**。

```sql
-- 创建全文索引
ALTER TABLE articles ADD FULLTEXT INDEX ft_title (title, content);

-- 全文搜索
SELECT * FROM articles WHERE MATCH(title, content) AGAINST('MySQL 优化');
```

---

## 三、索引分类

### 1. 按存储方式

| 类型 | 说明 |
|------|------|
| **聚簇索引** | 叶子节点存储完整数据行，数据按主键顺序物理存储。**InnoDB 表本身就是主键索引** |
| **非聚簇索引（二级索引）** | 叶子节点存储主键值，需要**回表**查询完整数据 |

### 2. 按逻辑分类

| 类型 | 说明 | 示例 |
|------|------|------|
| **主键索引** | 唯一 + 非空，InnoDB 必选 | `PRIMARY KEY (id)` |
| **唯一索引** | 值唯一，允许 NULL | `UNIQUE INDEX idx_email (email)` |
| **普通索引** | 最基本的索引，无约束 | `INDEX idx_name (name)` |
| **联合索引** | 多个列组成的索引 | `INDEX idx_a_b_c (a, b, c)` |
| **前缀索引** | 取列值的前 N 个字符 | `INDEX idx_name (name(10))` |
| **全文索引** | 用于文本搜索 | `FULLTEXT INDEX ft_idx (content)` |

### 3. 聚簇索引 vs 非聚簇索引

| 特性 | 聚簇索引 | 非聚簇索引 |
|------|---------|-----------|
| 每表数量 | 1 个（主键） | 多个 |
| 叶子节点 | 存储完整数据行 | 存储主键值 |
| 数据顺序 | 数据按聚簇索引排序 | 与数据物理顺序无关 |
| 查询方式 | 直接获取数据 | 需要**回表** |

### 4. 回表与覆盖索引

**回表**：通过非聚簇索引查到主键后，再回到聚簇索引查找完整数据行。两次 B+ 树遍历。

```
非聚簇索引：name = '张三' → 找到主键 id = 5
聚簇索引：id = 5 → 找到完整数据行
```

**覆盖索引**：查询的列都在索引中，无需回表。EXPLAIN 显示 `Using index`。

```sql
-- 创建联合索引
CREATE INDEX idx_name_age ON users (name, age);

-- 覆盖索引查询（无需回表）
SELECT name, age FROM users WHERE name = '张三';
-- EXPLAIN Extra: Using index ✅
```

> **优化核心**：尽量让查询成为覆盖索引，避免回表。

---

## 四、最左前缀原则

联合索引 `(a, b, c)` 遵循**最左前缀原则**：查询条件必须从索引最左列开始，连续匹配。

| 查询条件 | 是否走索引 | 使用的索引部分 |
|---------|:---------:|:------------:|
| `WHERE a = 1` | ✅ | (a) |
| `WHERE a = 1 AND b = 2` | ✅ | (a, b) |
| `WHERE a = 1 AND b = 2 AND c = 3` | ✅ | (a, b, c) |
| `WHERE b = 2` | ❌ | 无法使用 |
| `WHERE c = 3` | ❌ | 无法使用 |
| `WHERE a = 1 AND c = 3` | ⚠️ | 只用到 (a)，c 走索引下推(ICP) |
| `WHERE a = 1 ORDER BY b` | ✅ | (a) 等值 + (b) 排序 |
| `WHERE a > 1 AND b = 2` | ⚠️ | 用到 (a)，范围查询后索引中断 |

> **MySQL 5.6+ 索引下推（ICP）**：对于联合索引中无法用于查找的列，可以在存储引擎层进行过滤，减少回表次数。

---

## 五、索引失效场景

即使建了索引，以下情况可能导致索引无法使用：

| 场景 | 示例 | 解决方式 |
|------|------|---------|
| 对索引列使用函数 | `WHERE YEAR(create_time) = 2023` | 改为范围查询 `WHERE create_time >= '2023-01-01'` |
| 对索引列做运算 | `WHERE price * 2 > 100` | 改为 `WHERE price > 50` |
| 隐式类型转换 | 字符串列用数字查询 `WHERE phone = 13800138000` | 加引号 `WHERE phone = '13800138000'` |
| LIKE 左模糊 | `WHERE name LIKE '%张'` | 右模糊 `LIKE '张%'` 可走索引 |
| OR 条件中有非索引列 | `WHERE indexed_col = 1 OR non_indexed = 2` | 两个列都建索引 |
| NOT IN / NOT EXISTS | 某些场景优化器放弃索引 | 用 JOIN 或改写 SQL |
| 违反最左前缀 | 联合索引 (a,b,c) 查询 `WHERE b=?` | 调整查询或索引顺序 |
| 字符集不一致 | JOIN 两表的关联列字符集不同 | 统一字符集 |
| 数据量太小 | 优化器认为全表扫描更快 | 正常现象 |

---

## 六、索引设计原则

### 何时加索引

- WHERE 条件频繁使用的列
- JOIN 关联的列
- ORDER BY、GROUP BY 的列
- 高区分度的列（如用户 ID、邮箱）

### 何时不加索引

- 表数据量很小（几百行）
- 频繁更新的列（索引维护成本高）
- 区分度极低的列（如性别、状态字段）
- 已有联合索引覆盖的列

### 索引数量

- 单表索引一般不超过 **5~6 个**
- 每个索引会增加写入时的维护成本
- 联合索引优先于多个单列索引

---

## 七、索引维护

```sql
-- 查看表的索引
SHOW INDEX FROM users;

-- 创建索引
CREATE INDEX idx_email ON users (email);
CREATE UNIQUE INDEX idx_phone ON users (phone);
ALTER TABLE users ADD INDEX idx_name_age (name, age);

-- 删除索引
DROP INDEX idx_email ON users;

-- 重建索引（碎片整理）
ALTER TABLE users ENGINE = InnoDB;  -- MySQL
OPTIMIZE TABLE users;                -- MySQL
REINDEX INDEX idx_email;             -- PostgreSQL
```

---

## 八、EXPLAIN 中的索引信息

```sql
EXPLAIN SELECT * FROM users WHERE name = '张三' AND age > 25;
```

| 字段 | 关注点 |
|------|--------|
| `possible_keys` | 可能用到的索引 |
| `key` | 实际使用的索引（NULL = 全表扫描） |
| `key_len` | 实际使用的索引长度（字节），可判断联合索引用了几列 |
| `type` | 访问类型，`ref`/`range` 说明索引生效 |
| `rows` | 预估扫描行数 |
| `Extra` | `Using index` = 覆盖索引 ✅，`Using index condition` = 索引下推 ✅ |
