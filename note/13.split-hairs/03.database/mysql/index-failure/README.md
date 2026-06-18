# MySQL 索引失效的 10 种场景

> 一句话：**建了索引却没用上？这 10 种情况会让索引"白建"**

---

## 一、核心原理

MySQL 索引基于 **B+ Tree**。查询优化器（Optimizer）会评估"走索引"vs"全表扫描"的成本，选择代价更小的方案。**当走索引成本高于全表扫描时，优化器放弃索引**。

---

## 二、10 种失效场景

### 1. LIKE 以通配符开头

```sql
-- ❌ 索引失效（左通配）
SELECT * FROM users WHERE name LIKE '%张';

-- ✅ 索引有效（右通配）
SELECT * FROM users WHERE name LIKE '张%';
```

**原因**：B+ Tree 从左到右匹配，`%` 开头无法确定起始位置。

---

### 2. 对索引列使用函数或运算

```sql
-- ❌ 索引失效
SELECT * FROM users WHERE YEAR(create_time) = 2024;
SELECT * FROM users WHERE age + 1 = 30;

-- ✅ 索引有效
SELECT * FROM users WHERE create_time >= '2024-01-01' AND create_time < '2025-01-01';
SELECT * FROM users WHERE age = 29;
```

**原则**：保持索引列"干净"，把运算放到等号右边。

---

### 3. 隐式类型转换

```sql
-- phone 是 VARCHAR，但传入数字
-- ❌ 索引失效（MySQL 隐式转换为数字比较）
SELECT * FROM users WHERE phone = 13800138000;

-- ✅ 索引有效（字符串类型匹配）
SELECT * FROM users WHERE phone = '13800138000';
```

**检查**：`EXPLAIN` 看到 `type: ALL` 就是全表扫描。

---

### 4. OR 条件中有非索引列

```sql
-- name 有索引，age 没索引
-- ❌ 索引失效（OR 要求两边都有索引）
SELECT * FROM users WHERE name = '张三' OR age = 25;

-- ✅ 方案 1：给 age 也加索引
-- ✅ 方案 2：用 UNION 改写
SELECT * FROM users WHERE name = '张三'
UNION
SELECT * FROM users WHERE age = 25;
```

---

### 5. 联合索引不满足最左前缀

```sql
-- 联合索引 (a, b, c)
-- ✅ 索引有效
WHERE a = 1
WHERE a = 1 AND b = 2
WHERE a = 1 AND b = 2 AND c = 3

-- ❌ 索引失效（跳过 a）
WHERE b = 2
WHERE c = 3
WHERE b = 2 AND c = 3

-- ⚠️ MySQL 8.0+ 优化器可能自动调整（Index Skip Scan）
```

**最左前缀原则**：联合索引必须从最左列开始连续使用。

---

### 6. 索引列参与比较（!= 或 <>）

```sql
-- ❌ 大部分情况索引失效
SELECT * FROM users WHERE status != 0;

-- 但如果非 0 数据占比极小，优化器可能仍选索引
```

---

### 7. IS NULL / IS NOT NULL

```sql
-- ⚠️ 视数据分布而定
SELECT * FROM users WHERE deleted_at IS NULL;      -- 可能失效
SELECT * FROM users WHERE deleted_at IS NOT NULL;  -- 可能失效
```

**原因**：如果 NULL 值占比很大，全表扫描更快。

---

### 8. 排序字段与索引顺序不一致

```sql
-- 索引 (a, b)
-- ✅ 索引有效（顺序一致）
WHERE a = 1 ORDER BY b

-- ❌ 索引失效（排序字段不在索引中）
WHERE a = 1 ORDER BY c
```

---

### 9. SELECT * 导致覆盖索引失效

```sql
-- 索引 (name)，但 SELECT * 需要回表读所有列
-- ❌ 可能放弃索引（回表成本高）
SELECT * FROM users WHERE name = '张三';

-- ✅ 覆盖索引（只读索引列）
SELECT name FROM users WHERE name = '张三';
```

---

### 10. 数据量太小

```sql
-- 表只有 10 行数据
-- ❌ 优化器直接选全表扫描（索引成本 > 全表扫描）
```

**经验值**：表数据 < 几千行，索引优势不明显。

---

## 三、排查工具

### EXPLAIN 关键字段

```sql
EXPLAIN SELECT * FROM users WHERE name = '张三';
```

| 字段 | 含义 | 健康值 |
|------|------|--------|
| `type` | 访问类型 | `ref` / `range` / `const` 好；`ALL` 差 |
| `key` | 实际使用的索引 | 非 NULL |
| `rows` | 扫描行数 | 越少越好 |
| `Extra` | 额外信息 | `Using index`（覆盖索引）好；`Using filesort` 差 |

### 常见 type 优劣

```
system > const > eq_ref > ref > range > index > ALL
（最好）                                    （最差）
```

---

## 四、面试话术（30 秒版）

> "索引失效主要有 10 种情况：
> 
> 1. LIKE 左通配（`%abc`）
> 2. 对索引列用函数或运算
> 3. 隐式类型转换
> 4. OR 条件中有非索引列
> 5. 联合索引不满足最左前缀
> 6. != 或 <> 比较
> 7. IS NULL / IS NOT NULL（视数据分布）
> 8. 排序字段与索引不一致
> 9. SELECT * 导致覆盖索引失效
> 10. 数据量太小，优化器放弃索引
> 
> 排查用 `EXPLAIN`，看 `type` 是否为 `ALL`、`key` 是否为 NULL。"

---

## 五、交叉引用

- 主模块：[`03.database`](../../../03.database/) — 数据库知识体系
- [索引优化](../../../../03.database/04-index/README.md) — 索引数据结构与优化实战
- [MVCC 原理](../../mvcc/README.md) — MVCC 实现原理
- [B+ Tree](../../bplus-tree/README.md) — B+ Tree 详解
