<!--
module:
  parent: database
  slug: database/index
  type: index
  category: 主模块子文章
  summary: 索引通过 B+ 树等数据结构将查找从 O(N) 降至 O(log N)，覆盖聚簇/非聚簇、最左前缀、覆盖索引、ICP、MRR 等核心概念。
-->

# 索引

> 索引(Index)是数据库为了加快数据检索而维护的辅助数据结构,MySQL InnoDB 默认采用 B+ 树;合理使用索引是 SQL 优化中最核心的手段。


---

## 📚 核心内容

| 主题 | 内容 | 关键点 |
|------|------|--------|
| 一、为什么需要索引 | O(N) → O(log N) | 100 万行查找从 100 万次降到 ~20 次 |
| 二、索引数据结构 | B+ 树 / Hash / 全文索引 | InnoDB 默认 B+ 树 |
| 三、索引分类 | 聚簇 / 非聚簇 / 主键 / 唯一 / 普通 / 联合 / 前缀 / 全文 | InnoDB 主键索引就是聚簇索引 |
| 四、最左前缀原则 | 联合索引 (a,b,c) 命中规则 | (a) / (a,b) / (a,b,c) |
| 五、索引失效场景 | 9 种典型场景 | 函数 / 运算 / 类型转换 / LIKE 左模糊 |
| 六、索引设计原则 | 何时加 / 不加 / 数量上限 | 单表 ≤ 5~6 个索引 |
| 七、索引维护 | SHOW INDEX / CREATE / DROP / 重建 | `OPTIMIZE TABLE` |
| 八、EXPLAIN 中的索引 | possible_keys / key / key_len / rows / Extra | `Using index` = 覆盖索引 |
| 九、索引下推(ICP) | WHERE 下推存储引擎层 | MySQL 5.6+,减少回表 80% |
| 十、MRR(Multi-Range Read) | 随机回表 → 顺序 I/O | 机械硬盘收益 5-10 倍 |
| 十一、Index Merge | 多个单列索引合并 | Intersection / Union / Sort-Union |
| 十二、Cardinality 与索引选择性 | 索引列唯一值数量 | 选择性 > 0.1 才有价值 |
| 十三、Online DDL | INPLACE / INSTANT | pt-osc / gh-ost |

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

```text
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

```text
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
| `Extra` | `Using index` = 覆盖索引 ✅,`Using index condition` = 索引下推 ✅ |

---

## 九、索引下推(ICP)完整原理

**索引下推**(Index Condition Pushdown,ICP)是 MySQL 5.6+ 的重要优化,**将 WHERE 条件下推至存储引擎层执行**,减少不必要的回表。

### 1. 优化前(无 ICP)

联合索引 `(name, age)`,SQL: `SELECT * FROM users WHERE name LIKE '张%' AND age > 25`

```text
存储引擎:  找到所有 name LIKE '张%' 的索引项
Server 层: 从聚簇索引回表读取完整行 → 在 Server 层过滤 age > 25
```

**问题**:回表 1000 次,其中 800 次最终因 age 不满足被丢弃。

### 2. 优化后(ICP 启用)

```text
存储引擎:  找到 name LIKE '张%' 的索引项 → 在存储引擎层用 age > 25 过滤
          → 只回表 200 个真正满足的索引项
Server 层: 读 200 行,无需再次过滤 age
```

**收益**:回表次数从 1000 → 200,**减少 80% 随机 I/O**。

### 3. 启用与验证

```sql
-- 默认开启
SET optimizer_switch = 'index_condition_pushdown=on';

-- EXPLAIN 中 Extra 显示 Using index condition 即表示 ICP 生效
EXPLAIN SELECT * FROM users WHERE name LIKE '张%' AND age > 25;
```

### 4. 适用条件

- 只能用于**二级索引**(聚簇索引本身就是全行)
- WHERE 条件是索引列的**非前缀部分**
- 范围扫描(`range`)和 ref 扫描都支持

---

## 十、MRR(Multi-Range Read)

MRR(MySQL 5.6+)是辅助回表的优化:**将随机回表转为顺序 I/O**。

### 1. 优化前

```sql
SELECT * FROM users WHERE age BETWEEN 20 AND 30;
-- 二级索引(age)找到 1000 个主键 → 1000 次随机回表
```

### 2. 优化后

```text
步骤 1: 二级索引找到 1000 个主键
步骤 2: 在内存中对主键排序 → [id=1, id=5, id=12, id=33, ...]
步骤 3: 按主键顺序回表 → 顺序 I/O
```

**收益**:机械硬盘场景下随机 I/O 性能可提升 5-10 倍。**SSD 场景收益较小**。

### 3. 配置

```sql
SET optimizer_switch = 'mrr=on';
SET optimizer_switch = 'mrr_cost_based=on';  -- 由优化器决定
```

---

## 十一、Index Merge(索引合并)

MySQL 5.0+ 支持对**多个单列索引**的结果做合并。

### 1. 三种合并方式

| 合并方式 | 触发条件 | 示例 |
|---------|---------|------|
| **Intersection** | 多个 AND 条件,各用不同索引 | `WHERE a=1 AND b=2`(a、b 各有索引) |
| **Union** | 多个 OR 条件,各用不同索引 | `WHERE a=1 OR b=2` |
| **Sort-Union** | OR 条件,某列范围扫描 | `WHERE a>10 OR b=2` |

### 2. 实战判断

```sql
EXPLAIN SELECT * FROM users WHERE first_name = '张' OR last_name = '三';
-- Extra: Using union(idx_first_name, idx_last_name); Using where
```

### 3. 何时使用 vs 联合索引

| 场景 | 推荐 |
|------|------|
| 2 个独立条件偶尔查询 | Index Merge 足够 |
| 高频组合查询 | 改用联合索引 `(first_name, last_name)` |

> **注意**:Index Merge 在某些场景下比联合索引**慢**(临时结果集合并开销),可通过 `IGNORE INDEX` 强制改用单索引验证。

---

## 十二、Cardinality 与索引选择性

**Cardinality**(基数)是优化器评估索引价值的关键指标,表示索引列的**唯一值数量**。

### 1. 查看 Cardinality

```sql
SHOW INDEX FROM users;
-- 关注 Cardinality 列
-- 越大越有区分度,索引越有价值
```

MySQL 通过采样估算(非精确),可通过 `ANALYZE TABLE` 刷新统计。

### 2. 索引选择性公式

```text
选择性 = Cardinality / 表行数
```

| 字段 | 例子 | 选择性 | 是否适合索引 |
|------|------|--------|------------|
| 用户 ID | unique | 1.0 | ✅ 极优 |
| 邮箱 | 几乎唯一 | ~1.0 | ✅ 优 |
| 性别 | 男/女 | 0.0001 | ❌ 差 |
| 状态(0/1) | 2 种值 | 0.0001 | ❌ 差 |
| 创建时间(年) | 5 年 | 0.5 | ⚠️ 一般 |

### 3. 何时不建索引(补充设计原则)

- **低选择性字段**(状态、类型、性别)— 索引扫描行数仍接近全表
- **频繁更新** — 每次 UPDATE 维护 B+ 树
- **表数据量小**(< 几百行) — 全表扫描更快
- **重复数据多** — 如订单的 `is_deleted` 字段

---

## 十三、Online DDL

MySQL 5.6+ 支持在线修改表结构,**不锁表或只短暂锁元数据**。

### 1. 关键参数 `ALGORITHM` 与 `LOCK`

```sql
-- 添加索引不锁表
ALTER TABLE users ADD INDEX idx_email (email), ALGORITHM=INPLACE, LOCK=NONE;

-- 三种 ALGORITHM
-- COPY: 旧方式,锁表,完整重建
-- INPLACE: 不复制表数据,只重建索引(部分 DDL 支持)
-- INSTANT: 仅修改元数据(MySQL 8.0+,最快)

-- 三种 LOCK
-- NONE: 允许读写
-- SHARED: 允许读,阻塞写
-- EXCLUSIVE: 锁表
```

### 2. INSTANT DDL(MySQL 8.0+)

支持的操作:
- 添加列(默认值/无默认值)
- 修改默认值
- 重命名列/表

**性能**:毫秒级完成,只修改数据字典,**不触碰表数据**。

### 3. 大表 ALTER 实战方案

```bash
# 方案 1: pt-online-schema-change (Percona)
# 1. 创建影子表 2. 触发器同步 3. 切换

# 方案 2: gh-ost (GitHub 开源)
# 基于 binlog 同步,无需触发器
```

---

## 🔗 相关章节

- [数据库基础知识](../01-fundamentals/README.md) — 索引概览与三大索引类型
- [SQL](../02-sql/README.md) — 慢查询分析中的索引优化
- [事务与并发控制](../03-transaction/README.md) — 行锁与索引的关系
- [MySQL](../05-mysql/README.md) — InnoDB Buffer Pool 与磁盘 I/O

---

## 📊 本节统计

- **leaf README 数**：1（本文即为分类 leaf，单 README 长文聚合 13 主题）
- **本节主题数**：13（必要性、数据结构、分类、最左前缀、失效场景、设计原则、维护、EXPLAIN、ICP、MRR、Index Merge、Cardinality、Online DDL）
- **frontmatter 状态**：✅ 已对齐 CONTRIBUTING §12 标准（summary ≤ 80 字 / type=index）
- **统计口径**：本目录无嵌套子目录，所有内容聚合在本 README

---

## 📖 参考资料

- [MySQL 8.0 InnoDB and the ACID Model](https://dev.mysql.com/doc/refman/8.0/en/mysql-acid.html)
- [MySQL InnoDB Index Physical Structure](https://dev.mysql.com/doc/refman/8.0/en/innodb-physical-structure.html)
- [B+ Tree Visualization](https://www.cs.usfca.edu/~galles/visualization/BPlusTree.html)
- [Use The Index, Luke! - A Guide to Database Performance for Developers](https://use-the-index-luke.com/)

---

← [返回 03.database 主模块](../README.md)