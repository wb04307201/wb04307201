<!--
question:
  id: 03.database-deep-pagination
  topic: 03.database
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [03.database, deep, pagination]
-->

# 深分页：LIMIT 10000000, 10 为什么慢

> 一个看似简单但 90% 候选人答不全的问题。考察点不是 LIMIT 怎么写，而是 **OFFSET 的工作机制** 和 **覆盖索引的精确条件**。

## 引子：后台订单分页，第 1000 页打开空白 30 秒

```text
运营小王：老板让我看 2024 年第一笔历史订单。
→ 后台翻到第 1000 页（LIMIT 10 OFFSET 10000000）
→ 转圈 30 秒才出来，每页都慢
→ 用户投诉：后台不能用
```

**真相**：OFFSET 不是"跳过"，是**扫到 N 后丢弃**。
`LIMIT 10 OFFSET 10000000` 实际要扫 **10000010 行**。

3 个姿势：

1. **主键范围分页**（推荐）：`WHERE id > ? LIMIT 10`，O(log N) 走索引
2. **延迟关联**：先查 id（覆盖索引），再 IN 查详情
3. **业务层限制**：禁止跳到太深的页（前端只展示前 100 页）

## 一、核心结论（TL;DR）

| 分页方式 | 性能 | 适用场景 |
|---------|------|---------|
| `LIMIT 10 OFFSET 10000000` | ❌ 极慢（扫 1000 万 + 丢弃） | 几乎不用 |
| `WHERE id > ? LIMIT 10` | ✅ 极快（走主键索引） | 连续分页、API |
| 延迟关联（覆盖索引） | ⚠️ 中等 | 复杂条件 |
| ES `search_after` | ✅ 极快 | 搜索场景 |

> 一句话：**OFFSET 是「我先扫 N 行再丢掉」，不是「我从第 N 行开始」——OFFSET 越大越慢。**

---

## 二、OFFSET 的工作原理

```sql
SELECT * FROM user ORDER BY id LIMIT 10 OFFSET 10000000;
```

MySQL 实际执行过程：

```text
1. 按 id 排序找到第 10000010 行（扫了 10000010 行）
2. 取后 10 行返回
3. 丢掉了前 10000000 行（被读取但没返回）
```

**OFFSET 不跳过扫描**，而是「扫描后丢弃」。所以 OFFSET 10000000 的代价 = 扫 1000 万 + 丢 1000 万。

---

## 三、深分页为什么会慢（4 个原因）

1. **需要扫描 OFFSET+N 行**：OFFSET 10000000, 10 要扫 10000010 行
2. **需要排序**：ORDER BY 可能触发 filesort
3. **需要回表**：如果只查部分字段，覆盖索引会失效
4. **排序缓冲区溢出**：超过 sort_buffer_size 走磁盘临时文件

---

## 四、三种正确分页姿势

### 姿势 1：主键范围分页（推荐）

```sql
-- 第 1 页：取前 10 条
SELECT * FROM user ORDER BY id LIMIT 10;
-- 拿到最后一条 id = 100

-- 第 2 页：基于上一页最后一条
SELECT * FROM user WHERE id > 100 ORDER BY id LIMIT 10;
-- 拿到最后一条 id = 200

-- 第 3 页
SELECT * FROM user WHERE id > 200 ORDER BY id LIMIT 10;
```

**优点**：O(log N) 走主键索引，O(10) 返回
**缺点**：不能跳页，只能连续翻

### 姿势 2：覆盖索引 + 延迟关联

```sql
-- 第一步：只查 id（走覆盖索引，不回表）
SELECT id FROM user ORDER BY id LIMIT 10 OFFSET 10000000;

-- 第二步：根据 id 精准定位查详情
SELECT * FROM user WHERE id IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
```

**原理**：第一步只查 id（覆盖索引，不回表），第二步按 id 精准定位

### 姿势 3：业务侧限制深分页

```javascript
// 业务层不允许跳到第 1000 页（前端只展示前 N 页）
// 搜索引擎（ES）支持深分页（基于倒排索引）
```

---

## 五、面试陷阱

### 陷阱 1：以为 OFFSET 会"跳过"扫描

- **真相**：OFFSET 是"扫到 N 后丢弃"，不是"跳过 N 行"

### 陷阱 2：用子查询包装深分页能优化

```sql
-- ❌ 这样写反而更慢（外层无法用内层的索引）
SELECT * FROM user WHERE id IN (
  SELECT id FROM user LIMIT 10 OFFSET 10000000
);
```

- **正确**：先查 id，再 IN 查询详情（延迟关联）

### 陷阱 3：搜索引擎能完美解决深分页

- **真相**：ES 的 `from + size` 也有限制（默认 10000），超过要走 `search_after`

---

## 六、面试话术（90 秒版本）

> OFFSET 不是"跳过"，是"扫到 N 后丢弃"。`LIMIT 10 OFFSET 10000000` 实际要扫 1000 万行，代价是 O(10000010)。
>
> 正确的姿势是：
>
> 1. **主键范围分页**：`WHERE id > ? LIMIT 10`，O(log N) 走索引，O(10) 返回（推荐）
> 2. **延迟关联**：先查 id（覆盖索引），再 IN 查详情
> 3. **业务层限制**：不允许跳到太深的页
>
> 如果是搜索场景，用 ES 的 `search_after`（基于排序字段的游标），不用 `from + size`。

---

## 七、相关章节

- 同栏目：[`select-all-big-table`](../mysql-select-all-big-table/README.md) — SELECT * 内存陷阱
- 同栏目：[`batch-operation`](../mysql-batch-operation/README.md) — 批量插入
- 同栏目：[`tuning`](../mysql-tuning/README.md) — SQL 调优全流程
- 同栏目：[`index-failure`](../mysql-index-failure/README.md) — 索引失效的 10 种场景
- 主模块：[`03.database/02-sql`](../../../03.database/02-sql/README.md) — SQL 优化原则

---

> 📅 2026-06-28 · 咬文嚼字 · MySQL · ⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回数据库咬文嚼字](../README.md)
