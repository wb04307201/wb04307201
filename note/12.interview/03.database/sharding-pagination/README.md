<!--
question:
  id: 03.database-sharding-pagination
  topic: 03.database
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构设计
  tags: [03.database, sharding, pagination, distributed]
-->

# 分库分表后怎么做分页查询？

> 分库分表后数据分散在多个物理库表，单库的 LIMIT/OFFSET 不再适用——这就是分库分表带来的分页难题。与[MySQL 深度分页](../mysql-deep-pagination/)的区别：本题聚焦**跨库多表**场景，不是单库 OFFSET 优化。

---

## 引子：一个真实的业务需求

```text
场景：电商平台订单查询
- 订单表按 user_id 分 16 库 × 64 表 = 1024 张表
- 用户查询"我的订单"：SELECT * FROM orders WHERE user_id = ? ORDER BY create_time DESC LIMIT 0, 20
- 运营后台查询"所有订单"：SELECT * FROM orders ORDER BY create_time DESC LIMIT 1000000, 20

问题：
- 用户查询：单库单表，没问题
- 运营查询：跨 1024 张表分页，怎么搞？
```

---

## 一、核心原理：为什么分库分表后分页变难？

### 1.1 单库分页 vs 分库分页

```text
单库分页：
  SELECT * FROM orders ORDER BY create_time DESC LIMIT 1000000, 20
  → MySQL 优化器处理，深度分页用"延迟关联"优化（见 MySQL 深度分页）

分库分页（16 库 × 64 表）：
  SELECT * FROM orders ORDER BY create_time DESC LIMIT 1000000, 20
  → 需要跨 1024 张表排序 + 分页
  → 每张表都要 LIMIT 1000000, 20？然后合并？
  → 内存爆炸 + 性能灾难
```

### 1.2 核心难点

| 难点 | 说明 |
|------|------|
| **全局排序** | 1024 张表的数据需要全局排序（按 create_time） |
| **偏移量计算** | LIMIT 1000000, 20 意味着跳过前 100 万条，每张表都要跳过？ |
| **内存消耗** | 每张表返回 100 万条 → 1024 × 100 万 = 10 亿条 → OOM |
| **数据倾斜** | 某些表数据多，某些表数据少，分页结果不均匀 |

### 1.3 数据倾斜放大效应

```text
假设有 3 个分片，按时间分布不均匀：
  shard_0: 2024-01 ~ 2024-03，共 500 万条
  shard_1: 2024-04 ~ 2024-06，共 300 万条
  shard_2: 2024-07 ~ 2024-09，共 200 万条

查询 LIMIT 1000000, 20：
  → shard_0 返回 1000020 条（因为它最多）
  → shard_1 返回 1000020 条
  → shard_2 返回 1000020 条
  → 应用层需要合并 3 × 1000020 = 3000060 条
  → 但真正只需要 20 条！浪费 99.99%
```

---

## 二、4 大解决方案

### 方案 1：禁止深度分页（最推荐）

**思路**：业务层面限制，不允许跨库深度分页。

```text
用户查询"我的订单"：
  → 按 user_id 路由到单库单表
  → 单表分页，没问题

运营后台查询：
  → 限制只能按时间范围查询（如"最近 7 天"）
  → 或者只允许翻页前 100 页（LIMIT 0, 2000）
  → 超过 100 页？提示"请使用高级搜索"
```

**实现示例**：
```java
public PageResult<Order> queryOrders(OrderQueryRequest req) {
    // 限制最大偏移量
    if (req.getOffset() > 2000) {
        throw new BusinessException("请使用时间范围或高级搜索");
    }
    // 单路由键查询
    String shardKey = RouteEngine.route(req.getUserId());
    return orderDao.query(shardKey, req);
}
```

**适用场景**：C 端用户查询（单路由键）、运营后台浅分页

**优点**：简单、性能可控

**缺点**：业务受限

### 方案 2：全局视野法（二次查询法）

**思路**：先从所有表中查出足够的数据做全局排序，拿到排序边界后精准定位。

```sql
-- Step 1：从每张表查出前 N 条的排序字段（id + create_time）
SELECT id, create_time FROM orders_0000 ORDER BY create_time DESC LIMIT 0, 20
SELECT id, create_time FROM orders_0001 ORDER BY create_time DESC LIMIT 0, 20
...
SELECT id, create_time FROM orders_1023 ORDER BY create_time DESC LIMIT 0, 20

-- Step 2：在应用层合并 + 排序，取第 1000000-1000020 条的 (create_time, id)
-- 假设得到：(2024-01-15 10:30:22, 12345678)

-- Step 3：根据排序字段定位到具体表，查完整数据
SELECT * FROM orders_xxxx
WHERE create_time <= '2024-01-15 10:30:22' AND id < 12345678
ORDER BY create_time DESC LIMIT 0, 20
```

**更精确的做法（游标分页）**：
```text
第 1 页：每张表 LIMIT 20 → 应用层合并排序 → 返回 20 条 + 最后一条的 (time, id)
第 2 页：每张表 WHERE (create_time, id) < (last_time, last_id) ORDER BY ... LIMIT 20
        → 应用层合并排序 → 返回 20 条
```

**适用场景**：数据量可控（每张表前 N 条能覆盖分页需求）

**优点**：可以支持分页，不需要额外存储

**缺点**：
- 第一次查询需要扫描所有表（1024 次 SQL）
- 只能支持浅分页（页码大了每张表返回的数据量也线性增长）
- 数据量大时内存消耗高
- 实现复杂

### 方案 3：搜索引擎法（ES）

**思路**：将数据同步到 Elasticsearch，用 ES 做分页查询。

```text
MySQL（分库分表） → Canal/Flink → Elasticsearch
                                      ↓
                              运营后台查询（分页）
```

**查询示例**：
```json
GET /orders/_search
{
  "query": {
    "range": {
      "create_time": {
        "lte": "2024-01-15T10:30:22"
      }
    }
  },
  "sort": [
    {"create_time": "desc"},
    {"id": "desc"}
  ],
  "from": 1000000,
  "size": 20
}
```

**深度分页用 `search_after`（推荐）**：
```json
GET /orders/_search
{
  "query": { "match_all": {} },
  "sort": [
    {"create_time": "desc"},
    {"id": "desc"}
  ],
  "search_after": [1705290622000, 12345678],
  "size": 20
}
```

**适用场景**：运营后台、复杂查询、深度分页

**优点**：
- ES 原生支持深度分页（scroll / search_after）
- 支持复杂条件查询
- 性能好，倒排索引天然适合多条件过滤

**缺点**：
- 需要维护 ES 集群
- 数据同步延迟（最终一致性）
- 成本高（存储 + 计算资源）

### 方案 4：冗余汇总法（空间换时间）

**思路**：在分库前，维护一张"全局排序表"（单库单表），记录所有数据的全局排序信息。

```sql
-- 全局排序表（单库单表）
CREATE TABLE orders_global_index (
  id BIGINT PRIMARY KEY,
  order_id BIGINT,
  user_id BIGINT,
  create_time DATETIME,
  shard_key VARCHAR(64),  -- 路由到哪个库表
  INDEX idx_create_time (create_time)
);

-- 插入订单时，同时写入全局索引表
INSERT INTO orders_xxxx (id, user_id, ...) VALUES (...);
INSERT INTO orders_global_index (id, order_id, user_id, create_time, shard_key)
VALUES (...);

-- 分页查询：先在全局索引表中分页
SELECT og.order_id, og.shard_key
FROM orders_global_index og
ORDER BY og.create_time DESC
LIMIT 1000000, 20;

-- 根据 shard_key 路由到具体库表查完整数据
SELECT * FROM orders_xxxx WHERE id IN (...);
```

**适用场景**：写少读多、对实时性要求不高

**优点**：查询性能好（单表分页，可用延迟关联优化）

**缺点**：
- 写入成本翻倍（两次 INSERT，或走 Binlog 异步同步）
- 数据一致性维护复杂
- 全局索引表可能成为瓶颈（本身也会变大）
- 如果全局索引表也大了，需要再做一轮分片 → 问题递归

---

## 三、方案对比 + 生产推荐

| 方案 | 适用场景 | 性能 | 复杂度 | 推荐度 |
|------|---------|------|--------|--------|
| **禁止深度分页** | C 端用户查询 | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| **全局视野法** | 数据量可控 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **搜索引擎法** | 运营后台、复杂查询 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **冗余汇总法** | 写少读多 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

**生产推荐**：
1. **C 端用户查询**：禁止深度分页（方案 1）+ 单路由键分页
2. **运营后台查询**：搜索引擎法（方案 3，ES）
3. **数据量小（< 100 万）**：全局视野法（方案 2）
4. **写少读多 + 实时性要求低**：冗余汇总法（方案 4）

**核心原则**：能不分页就不分页，必须分页就用 ES。

---

## 四、常见陷阱

### 陷阱 1：每张表 LIMIT offset, size 然后合并

```text
错误做法：
  每张表执行 LIMIT 1000000, 20 → 1024 × 20 = 20480 条
  在应用层合并排序 → 取前 20 条

问题：
  假设 shard_0 有 200 万条最新数据，shard_1 只有 10 条
  → shard_1 的 10 条可能全部排在前 20
  → 但其他表 LIMIT 20 只返回了各自的前 20，全局前 20 可能被漏掉
  → 结果不正确！
```

### 陷阱 2：用 OFFSET 跨库分页

```text
错误做法：
  在中间件层（如 ShardingSphere）直接执行 LIMIT offset, size
  → 中间件会向每个分片发送相同的 SQL
  → 每个分片都扫描 offset + size 条数据
  → 网络 + 内存双重爆炸
```

### 陷阱 3：全局索引表无限增长

```text
全局索引表本身也会变大 → 超过单表容量 → 也需要分片
→ 分片后又回到原问题：跨库分页怎么做？
→ 递归问题，无解
→ 所以全局索引表只能作为过渡方案，或者配合冷热分离使用
```

---

## 五、面试话术（30 秒版）

> "分库分表后分页查询有 4 种方案：**禁止深度分页**——业务层面限制，C 端用户按路由键查询单表分页，运营后台限制翻页页数；**全局视野法**——先从每张表查前 N 条的排序字段，应用层合并排序后定位到具体表，适合数据量可控场景；**搜索引擎法**——数据同步到 ES，用 ES 的 search_after 做分页查询，适合运营后台和复杂查询；**冗余汇总法**——维护全局索引表，单表分页后路由到具体库表。
>
> 生产推荐：C 端用户查询用方案 1（禁止深度分页），运营后台用方案 3（ES），数据量小用方案 2（全局视野）。核心思想是'能不分页就不分页，必须分页就用 ES'。"

---

## 六、交叉引用

- [分库分表分布式事务](../sharding-distributed-tx/README.md) — 分库分表后跨库事务处理
- [分库分表扩容](../sharding-resize/README.md) — 分库分表扩容方案
- [MySQL 深度分页](../mysql-deep-pagination/README.md) — 单库深度分页优化（延迟关联）
- 主模块：[`03.database`](../../../03.data-stack/01-database/README.md) — 数据库知识体系

## 相关章节

- 深度阅读：[`03.database`](../../../03.data-stack/01-database/README.md) — 数据库咬文嚼字全景（MySQL / Redis / 分库分表）

> 📅 2026-09-01 · 咬文嚼字 · 分库分表 · ⭐⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回: 咬文嚼字 · sharding-pagination](../README.md)
