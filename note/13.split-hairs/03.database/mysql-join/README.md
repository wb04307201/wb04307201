# MySQL JOIN 算法深度剖析

## 引子：同一个 JOIN，为什么快了 100 倍？

```sql
-- 两个大表 JOIN
SELECT * FROM orders o 
JOIN users u ON o.user_id = u.id;

-- 执行计划 1：NLJ（Nested Loop Join）无索引
-- orders 100 万行 × users 逐行扫描 → O(N×M) → 跑 10 分钟！

-- 执行计划 2：users.id 有索引
-- orders 100 万行 × 每次索引查找 → O(N×logM) → 3 秒！
```

同一个 JOIN，性能差 **200 倍**。差别就在于：

1. **驱动表选对了没**（小表驱动大表）
2. **被驱动表的 JOIN 字段有索引没**
3. **内存够不够装 Join Buffer**

MySQL 的 JOIN 算法有 3 种：NLJ、BNL、Hash Join。优化器会根据数据量和索引情况自动选择。

---

> 📚 **前置知识**：[MySQL](../../03.database/05-mysql/README.md) | [索引](../../03.database/04-index/README.md)

## 一、核心原理

JOIN 的本质是**两张表的笛卡尔积再过滤**。优化器需要决定哪张表作为**驱动表（外层表）**，哪张表作为**被驱动表（内层表）**。驱动表的每一行都要去被驱动表中匹配，因此驱动表的选择直接决定了外层循环的次数。优化器通常选择**结果集较小**的表作为驱动表，以减少外层迭代次数。

**优化器如何估算成本？** 优化器会统计每个表的行数、索引基数（Cardinality）、数据分布等信息，计算不同执行计划的IO成本和CPU成本，最终选择成本最低的方案。可以通过 `EXPLAIN FORMAT=JSON` 查看详细成本估算。

## 二、NLJ（Nested-Loop Join）

NLJ 是最基础的 JOIN 算法，采用**两层嵌套循环**：对驱动表的每一行，逐行扫描被驱动表进行匹配。当被驱动表的 JOIN 字段上有索引时，NLJ 会退化为 **Index Nested-Loop Join**：驱动表每取一行，就去被驱动表的索引中执行一次 `ref` 或 `eq_ref` 查找，时间复杂度从 O(N*M) 降至 O(N*logM)。这是最理想的 JOIN 场景。

```sql
-- EXPLAIN 输出中，若被驱动表的 type 为 ref/eq_ref，说明走了 NLJ + 索引
EXPLAIN SELECT * FROM dept d JOIN emp e ON d.id = e.dept_id;
-- emp 表的 type = ref，key = idx_dept_id → Index NLJ
```

**Index NLJ 的执行流程：**
1. 从驱动表取出第一行数据
2. 提取JOIN字段的值，到被驱动表的索引中查找
3. 如果找到匹配，再通过主键回表获取完整行数据（如果没有覆盖索引）
4. 重复步骤1-3直到驱动表遍历完毕

**性能瓶颈：** Index NLJ的主要开销在于**随机IO**。如果驱动表有N行，被驱动表需要执行N次索引查找，每次都可能涉及磁盘随机读取。MySQL 5.6引入的MRR（Multi-Range Read）优化可以将部分随机IO转为顺序IO，提升性能。

## 三、BNL（Block Nested-Loop Join）

当被驱动表的 JOIN 字段**没有索引**时，朴素 NLJ 会退化为全表扫描，复杂度 O(N*M)。BNL 对此做了批量优化：将驱动表的多行数据放入 `join_buffer`（内存块），然后一次性扫描被驱动表，将被驱动表的每一行与 join_buffer 中的所有行进行比较。这样被驱动表只需扫描一次，而非每行驱动表数据都扫一遍。`join_buffer_size` 默认 256KB，一次 JOIN 操作分配一个 buffer；buffer 越大，能容纳的驱动表行数越多，被驱动表扫描次数越少。

```sql
-- 查看当前 join_buffer_size
SHOW VARIABLES LIKE 'join_buffer_size';  -- 默认 262144 (256KB)

-- 调优：针对大表 JOIN 临时增大
SET SESSION join_buffer_size = 4194304;  -- 4MB
```

**BNL 的内存计算：** 假设每行驱动表数据占用100字节，256KB的buffer可以容纳约2500行。如果驱动表有10万行，则需要扫描被驱动表 100000/2500 = 40次。将buffer扩大到4MB后，扫描次数降至 100000/(4000000/100) ≈ 2.5次。

**BNL 的适用场景：**
- 被驱动表无法加索引（如频繁写入的表）
- 驱动表结果集较小，但JOIN字段没有合适索引
- 临时表或派生表的JOIN（无法创建索引）

## 四、Hash Join（MySQL 8.0.18+）

MySQL 8.0.18 引入了 Hash Join，专门处理**无索引的大表等值 JOIN**。算法分两阶段：**Build 阶段**扫描小表，以 JOIN 键为 Key 构建 Hash Table；**Probe 阶段**扫描大表，用同样的 Hash 函数计算大表每行的 Hash 值，去 Hash Table 中查找匹配。Hash Join 的时间复杂度接近 O(N+M)，远优于 BNL 的 O(N*M)。优化器会自动选择 Hash Join 替代 BNL，无需任何 hint。

```sql
-- EXPLAIN 中 Extra 列显示 "Using join buffer (hash join)" 表示使用了 Hash Join
EXPLAIN FORMAT=TREE SELECT * FROM t1 JOIN t2 ON t1.col = t2.col;
-- Output: -> Inner hash join (t2.col = t1.col) (cost=...) 
--           -> Hash
--           -> Table scan on t1
--           -> Table scan on t2
```

**Hash Join 的优势：**
- **线性复杂度**：O(N+M) 对比 BNL 的 O(N*M)，大数据量下优势明显
- **无需索引**：适合临时表或无法加索引的场景
- **内存友好**：MySQL实现支持磁盘溢出，不会因内存不足而失败

**Hash Join 的限制：**
- 仅支持等值JOIN（=），不支持范围查询（>、<、BETWEEN）
- 非等值条件会在Hash Match后进行过滤
- 小表过大会导致Hash Table无法完全放入内存，触发磁盘溢出，性能下降

## 五、小表驱动大表

"小表驱动大表"的原则源于**减少外层循环次数**。驱动表的结果集行数决定了外层循环的迭代次数，因此优化器倾向于选择经过 WHERE 过滤后结果集更小的表作为驱动表。注意这里的"小"不是指表的物理大小，而是**参与 JOIN 的有效行数**。通过 `EXPLAIN` 可以观察优化器的选择：第一行显示的表即为驱动表。

```sql
-- EXPLAIN 输出第一行为驱动表
EXPLAIN SELECT * FROM small_table s JOIN large_table l ON s.id = l.small_id;
-- id | table       | type | ...
-- 1  | small_table | ALL  | ...    ← 驱动表（全表扫描）
-- 1  | large_table | ref  | ...    ← 被驱动表（索引查找）
```

**强制指定驱动表：** 可以使用 `STRAIGHT_JOIN` 强制MySQL按照书写顺序选择驱动表：

```sql
-- 强制 large_table 作为驱动表（不推荐，仅作演示）
SELECT * FROM large_table STRAIGHT_JOIN small_table ON large_table.id = small_table.large_id;
```

## 六、优化手段

| 手段 | 说明 |
|------|------|
| **给被驱动表 JOIN 字段加索引** | 将 BNL/Hash Join 转为 Index NLJ，复杂度从 O(N*M) 降至 O(N*logM) |
| **调整 join_buffer_size** | 无法加索引时，增大 buffer 可减少被驱动表扫描次数；每次 JOIN 分配一个 buffer，不宜过大以免内存溢出 |
| **确保 JOIN 字段类型一致** | 字段类型不同（如 int vs varchar）会导致索引失效，触发全表扫描 |
| **利用 MRR（Multi-Range Read）** | MySQL 5.6+ 引入，将随机 IO 转为顺序 IO，优化 Index NLJ 中回表查询的性能；通过 `mrr_cost_based` 参数控制 |
| **避免 SELECT *** | 覆盖索引可以避免回表，进一步减少 IO |
| **使用延迟关联（Deferred Join）** | 先通过覆盖索引获取主键，再回表查询完整数据，减少回表次数 |

```sql
-- 检查 MRR 是否开启
SHOW VARIABLES LIKE 'optimizer_switch';
-- mrr=on, mrr_cost_based=on 表示启用基于成本的 MRR 优化

-- 延迟关联示例：先通过索引获取id，再join原表
SELECT e.* FROM employee e
INNER JOIN (SELECT id FROM employee WHERE dept_id = 10 LIMIT 100) tmp
ON e.id = tmp.id;
```

## 七、常见陷阱

### 陷阱1：隐式类型转换导致索引失效

```sql
-- phone_number 是 VARCHAR 类型，以下写法会导致索引失效
SELECT * FROM users u JOIN orders o ON u.phone_number = o.user_phone;
-- 如果 o.user_phone 是 INT 类型，MySQL 会对 u.phone_number 做类型转换，索引失效
```

**解决方案：** 确保JOIN字段的数据类型完全一致，包括字符集和排序规则。

### 陷阱2：多表JOIN时索引设计不当

三表JOIN时，应该给中间表的两个JOIN字段都加索引。例如 A JOIN B JOIN C，B表应该在JOIN A的字段和JOIN C的字段上分别建立索引。

## 八、面试话术（30 秒版）

> "MySQL JOIN 有三种算法：NLJ、BNL 和 Hash Join。**NLJ** 是嵌套循环，被驱动表有索引时走 Index NLJ，每次通过索引查找匹配行，效率最高。**BNL** 用于无索引场景，把驱动表数据放入 join_buffer，一次扫描被驱动表时批量比较，减少被驱动表扫描次数。**Hash Join** 是 8.0.18 新增的，先扫描小表建 Hash Table，再扫描大表 Probe，复杂度 O(N+M)。优化原则是**小表驱动大表**，即让过滤后行数少的表做驱动表，减少外层循环次数；同时尽量给被驱动表的 JOIN 字段加索引，让 BNL 退化为 Index NLJ。可以用 EXPLAIN 的 type 字段判断：ref/eq_ref 表示走了索引，ALL 表示全表扫描。"

## 九、交叉引用

- 主模块：[`03.database`](../../../03.database/) — 数据库知识体系
- [索引优化](../../../03.database/04-index/README.md) — MySQL 索引数据结构与优化
- [MySQL 核心](../../../03.database/05-mysql/README.md) — EXPLAIN 执行计划与锁机制

## 相关章节

- 深度阅读：[`03.database`](../../03.database/README.md) — 主模块详细内容
