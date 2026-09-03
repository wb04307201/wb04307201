<!--
question:
  id: 03.database-pg-vacuum-troubleshooting
  topic: 03.database
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 排查案例
  tags: [03.database, PostgreSQL, KingbaseES, autovacuum, troubleshooting]
-->

# PostgreSQL/KingbaseES VACUUM 排查：删完数据，查询反而变慢的真相

> **一句话定位**：PG/KingbaseES 的 DELETE 是"逻辑删除"（xmax 标记），**不会释放磁盘空间**；变慢的根因是 dead tuples 堆积 + autovacuum 滞后 + 统计信息陈旧 + 索引膨胀的复合作用。

> **系列定位**：经典 PG/金仓面试题（中频，DBA / 后端高频）。考察的不是"VACUUM 怎么用"，而是 **dead tuple 是什么** + **autovacuum 触发阈值公式** + **VACUUM vs VACUUM FULL 差异** + **表膨胀量化方法** + **人大金仓与 PG 异同**。

---

## 引子：凌晨定时任务清掉 1500 万数据后，原本 100ms 的查询飙到 3s

```text
场景：金融业务系统（KingbaseES V8R6，基于 PostgreSQL 9.6 内核改造）
表：   orders_log，5000 万行，订单流水表
现象：凌晨 3 点定时任务 DELETE 清掉 3 个月前的数据（约 1500 万行）
       白班 9 点上线，原本 100ms 的列表查询接口 P99 飙到 2.8s
       CPU 不高、IO 不忙、连接没满
初步怀疑：索引缓存没清？autovacuum 没自动处理？
dba 介入：
  查 pg_stat_user_tables → n_dead_tup = 1750 万（35% 表大小）
  last_autovacuum = 3 周前（说明从未自动触发）
  手动 VACUUM ANALYZE 后查询回到 120ms
```

**真相**（反直觉三连）：

1. PG 的 DELETE 不是物理删除，而是把元组的 `xmax` 字段标记为删除事务 ID，行还在 heap page 里
2. autovacuum **默认要等死元组达到 20% 表大小才触发**（`autovacuum_vacuum_scale_factor`），不是"有死元组就清"
3. `VACUUM ANALYZE` **只把 dead tuple 标记为"空间可重用"**，磁盘占用不变；只有 `VACUUM FULL` 才会真正回收 OS 空间，但**会锁表**

旁白：用户的"autovacuum 会自动处理"方向对但不完整。**真正的根因是 autovacuum 滞后 + dead tuples 堆积 + 统计信息陈旧 + 索引膨胀的复合作用**——这才是面试想听的方法论。

---

## 一、核心原理（4 个 WHY 反直觉点）

### 1.1 什么是 dead tuple（死元组）？

PG 在 heap page（数据页）里直接保存**多版本元组**，每个元组头部携带 `xmin`（插入事务 ID）和 `xmax`（删除/更新事务 ID）：

```sql
-- 伪代码示意 PG heap tuple 结构
struct HeapTupleHeaderData {
    t_xmin:     TransactionId  -- 插入该元组的事务 ID
    t_xmax:     TransactionId  -- 删除/更新该元组的事务 ID（0 = 仍在）
    t_cmin:     CommandId      -- 同一事务内命令 ID
    t_cmax:     CommandId
    t_data:     HeapTupleFields -- 用户数据
};
```

```text
┌─────────────────────────────┐
│ Heap Page (8KB)             │
│ ┌───────────────────────┐   │
│ │ Tuple v1 (xmin=100)   │──→ 对 tx<100 不可见（已被 VACUUM 标记）
│ │ Tuple v2 (xmax=200)   │──→ 已删除标记（dead tuple！）
│ │ Tuple v3 (xmin=300)   │──→ 当前活跃版本
│ └───────────────────────┘   │
│                             │
│ Free Space Map (FSM)        │ ← 跟踪每个页可用空间
│ Visibility Map (VM)         │ ← 跟踪哪些页所有元组都对所有事务可见
└─────────────────────────────┘
```

**关键反直觉点**：
- DELETE 只设置 `xmax`，**元组物理位置不动**，heap page 空间不释放
- UPDATE 在 PG 里 = **delete + insert**（产生新元组，旧元组变 dead tuple）
- 这与 MySQL InnoDB 的"原地更新 + undo log"机制完全不同

### 1.2 autovacuum 触发公式（重点）

```sql
-- autovacuum 触发阈值公式
触发阈值 = autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor × n_live_tup

-- 默认值（PG/金仓通用）
autovacuum_vacuum_threshold     = 50        -- 固定基数
autovacuum_vacuum_scale_factor  = 0.2       -- 表大小的 20%

-- 案例计算（5000 万行表）
触发阈值 = 50 + 0.2 × 5000万 = 1000万 dead tuples 才会自动触发！
```

**反直觉点**：5000 万行表，删 1500 万行（30%）才会触发 autovacuum；如果只删 500 万（10%），autovacuum **永远不会自动启动**——这就是为什么用户场景下 `last_autovacuum = 3 周前`。

### 1.3 VACUUM vs VACUUM FULL（最容易混淆的一对）

| 维度 | VACUUM | VACUUM FULL |
|------|--------|-------------|
| **锁级别** | `ShareUpdateExclusiveLock`（不阻塞读写） | `AccessExclusiveLock`（**全表锁，阻塞一切**） |
| **空间回收** | 只标记 FSM 可重用，**磁盘占用不变** | 重建表，把 dead tuple 空间归还 OS |
| **索引** | 不重建 | 重建索引 |
| **执行时长** | 与 dead tuple 数成正比（流式处理） | 与表大小成正比（5000 万行可能数小时） |
| **生产可用性** | 可以（建议低峰期） | **慎用**，大型表锁表期间业务不可用 |
| **替代方案** | pg_repack（在线重建） | pg_repack、pg_squeeze |

**反直觉点**：很多人以为 `VACUUM ANALYZE` 能回收磁盘空间，实际**完全不能**——它只把死元组占的空间标记为"下次插入时可重用"，`du` 命令看文件大小不变。

### 1.4 人大金仓 KingbaseES 的特化点

KingbaseES V8R6 基于 PostgreSQL 9.6 内核改造，autovacuum 机制**完全兼容**，但有以下差异：

```sql
-- 系统视图前缀（人大金仓习惯用 sys_ 前缀）
SELECT * FROM sys_stat_user_tables;  -- 人大金仓常用
SELECT * FROM pg_stat_user_tables;  -- 原生 PG（人大金仓也支持）

-- 部分参数名差异
-- PG:        autovacuum_vacuum_scale_factor
-- 人大金仓:   vacuum_scale_factor (在 kingbase.conf 中别名)
```

**反直觉点**：人大金仓默认**关闭 autovacuum**（生产部署经验），需要手动开启；很多金仓生产环境的 `autovacuum = off` 是历史遗留配置，排查时务必先确认。

---

## 二、排查方法论（5 步走）

### 步骤 1：定位死元组最多的表

```sql
-- 找出死元组占比最高的 Top 30 表
SELECT
    schemaname || '.' || relname AS table_name,
    n_live_tup,
    n_dead_tup,
    CASE WHEN n_live_tup > 0
         THEN round(100.0 * n_dead_tup / (n_live_tup + n_dead_tup), 2)
         ELSE 0 END AS dead_pct,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables  -- 人大金仓也可用 sys_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC
LIMIT 30;
```

**判断标准**：
- `dead_pct > 10%`：表膨胀已较严重，需要立即处理
- `last_autovacuum IS NULL` 或 `> 7 天前`：autovacuum 长期未工作（参数或长事务阻塞）

### 步骤 2：查长事务（阻塞 vacuum 回收）

```sql
-- 找出所有活跃事务（长事务会阻止 vacuum 清理 dead tuple）
SELECT
    pid,
    state,
    now() - xact_start AS xact_age,
    left(query, 180) AS query_snippet,
    client_addr
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start
LIMIT 20;

-- 如果某个事务 idle in transaction 且 xact_age > 1h，需要立即 kill
SELECT pg_terminate_backend(pid);
```

**反直觉点**：很多 DBA 只盯着 `autovacuum` 参数，却忘了**长事务**会阻止 autovacuum 回收它能看见的 dead tuple——autovacuum 必须跳过任何"还可能被该事务看到"的旧版本。

### 步骤 3：量化表膨胀（用 pgstattuple 扩展）

```sql
-- 安装扩展（人大金仓默认可能未装）
CREATE EXTENSION IF NOT EXISTS pgstattuple;

-- 看表的物理膨胀情况
SELECT
    table_len / 1024 / 1024 AS table_size_mb,
    tuple_count AS live_tuples,
    dead_tuple_count,
    round(100.0 * dead_tuple_percent, 2) AS dead_pct,
    round(100.0 * free_percent, 2) AS free_space_pct,
    free_space / 1024 / 1024 AS free_space_mb
FROM pgstattuple('orders_log');

-- 典型输出：
--  table_size_mb | dead_tuple_count | dead_pct | free_space_pct
-- ---------------+------------------+----------+----------------
--           4500 |        17500000  |    35.00 |          12.50
--                                          ↑ 表膨胀 35%
--                                              ↑ 还有 12.5% 碎片空间
```

**量化标准**：
- `dead_pct > 20%`：**严重膨胀**，必须 VACUUM FULL 或 pg_repack
- `dead_pct 10-20%`：建议手动 VACUUM ANALYZE
- `dead_pct < 10%`：正常范围，让 autovacuum 自动处理

### 步骤 4：检查 autovacuum 实时状态

```sql
-- 看 autovacuum worker 是否在运行
SELECT
    pid,
    datname,
    relid::regclass AS table_name,
    phase,
    heap_blks_total,
    heap_blks_scanned,
    heap_blks_vacuumed,
    round(100.0 * heap_blks_scanned / NULLIF(heap_blks_total, 0), 2) AS scan_pct,
    round(100.0 * heap_blks_vacuumed / NULLIF(heap_blks_total, 0), 2) AS vacuum_pct,
    index_vacuum_count,
    max_dead_tuples,
    num_dead_tuples
FROM pg_stat_progress_vacuum;

-- 看 autovacuum worker 的历史执行情况
SELECT
    relid::regclass AS table_name,
    total_time,
    count(*) AS vacuum_count,
    max(dead_tuples) AS max_dead_tuples
FROM pg_stat_user_tables
WHERE last_autovacuum IS NOT NULL
GROUP BY relname
ORDER BY total_time DESC;
```

### 步骤 5：检查参数配置

```sql
-- 关键参数
SHOW autovacuum;                                -- 应为 on
SHOW autovacuum_vacuum_scale_factor;            -- 默认 0.2（建议大表调到 0.05）
SHOW autovacuum_vacuum_threshold;               -- 默认 50
SHOW autovacuum_naptime;                        -- 默认 60s（autovacuum 唤醒间隔）
SHOW autovacuum_max_workers;                    -- 默认 3（并发 worker 数）
SHOW autovacuum_work_mem;                       -- 每个 worker 内存（默认 -1 用 maintenance_work_mem）
SHOW maintenance_work_mem;                      -- 维护操作总内存

-- 大表建议配置（单表 > 1 亿行）
ALTER TABLE orders_log SET (
    autovacuum_vacuum_scale_factor = 0.02,      -- 2% 触发（更激进）
    autovacuum_vacuum_threshold = 1000,
    autovacuum_analyze_scale_factor = 0.01      -- 1% 触发 analyze
);
```

---

## 三、根因深挖（5 个反直觉点）

### 3.1 ❌ "DELETE 后空间会立即释放"

**✅ 真相**：DELETE 只是把元组的 `xmax` 标记为删除事务 ID，**heap page 中的物理位置不变**。

```sql
-- 验证：DELETE 前后表大小
SELECT pg_size_pretty(pg_total_relation_size('orders_log')) AS size_before;
DELETE FROM orders_log WHERE create_time < now() - interval '3 months';
SELECT pg_size_pretty(pg_total_relation_size('orders_log')) AS size_after;
-- 两个值完全一样！磁盘不释放
```

### 3.2 ❌ "autovacuum 会立即触发清理"

**✅ 真相**：默认要等死元组达到 **20% 表大小**才触发。

```sql
-- 反例：5000 万行表，删 500 万行（10%），autovacuum 永远不启动
DELETE FROM orders_log WHERE create_time < now() - interval '6 months';
-- 期望：autovacuum 自动清理
-- 实际：触发阈值 = 50 + 0.2 × 5000万 = 1000万，500万 < 1000万，不触发

-- 解决：调小 scale_factor 或手动 VACUUM
ALTER TABLE orders_log SET (autovacuum_vacuum_scale_factor = 0.02);
-- 现在 100万 dead tuple 就会触发 autovacuum
```

### 3.3 ❌ "VACUUM ANALYZE 能回收空间"

**✅ 真相**：只标记空间可重用，**磁盘占用完全不变**。

```text
┌────────────────────────────────────────────────┐
│  VACUUM 做了什么？                              │
├────────────────────────────────────────────────┤
│  1. 扫描 heap page                             │
│  2. 找到对所有事务都不可见的 dead tuple         │
│  3. 把这些空间标记到 FSM（Free Space Map）      │
│  4. 后续 INSERT 可以复用这些空间                │
│                                                │
│  ❌ 不会做：                                   │
│  - 不会把空间还给操作系统                       │
│  - 不会压缩 heap page                          │
│  - 不会缩小表文件                               │
└────────────────────────────────────────────────┘
```

**验证**：
```sql
VACUUM ANALYZE orders_log;
SELECT pg_size_pretty(pg_total_relation_size('orders_log'));
-- 大小完全不变！只是 FSM 标记这些页"有空闲空间可用"
```

### 3.4 ❌ "VACUUM FULL 总是能用"

**✅ 真相**：会加 `AccessExclusiveLock`，**阻塞该表所有读写**。

```sql
-- 反例：5000 万行表上跑 VACUUM FULL
BEGIN;
LOCK TABLE orders_log IN ACCESS EXCLUSIVE MODE;  -- VACUUM FULL 等价于此锁
-- 此时所有 SELECT/INSERT/UPDATE/DELETE 全部阻塞
-- 业务会立即感知到连接超时
```

**生产推荐替代方案**：
```bash
# pg_repack：在线重建表，不锁表（推荐）
pg_repack -t orders_log -h localhost -p 54321 -U dbadmin

# pg_squeeze：另一个在线重建工具
pg_squeeze -f squeeze.conf -t orders_log
```

### 3.5 ❌ "表膨胀就完了，索引没事"

**✅ 真相**：索引也膨胀（index bloat），index scan 需扫更多 dead pointers。

```sql
-- 检查索引膨胀
SELECT
    schemaname || '.' || indexname AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan AS scan_count,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;

-- 用 pgstattuple 检查索引膨胀
SELECT * FROM pgstatindex('orders_log_idx_user_id');
-- avg_leaf_density < 70 表示索引碎片化严重
```

**反直觉点**：用户场景中 `last_analyze = 3 周前`，意味着**优化器用的是 3 周前的统计信息**，新插入的数据分布完全没纳入估算——这是查询慢的次要根因（即使 VACUUM 了，统计信息也可能过期）。

---

## 四、解决（含代码块 + 配置 diff + 前后对比）

### 4.1 立即止血（不锁表）

```sql
-- 手动 VACUUM（不锁表，仅标记空间可重用）
VACUUM (ANALYZE, VERBOSE) orders_log;

-- VERBOSE 输出示例：
-- INFO: vacuuming "public.orders_log"
-- INFO: scanned index "orders_log_pkey" to remove 17500000 row versions
-- DETAIL: CPU 12.50s/15.20s sec elapsed, 8.5M rows/sec
-- INFO: "orders_log": removed 17500000 row versions in 18523 pages
-- INFO: index "orders_log_pkey" now contains 35000000 row versions in 89234 pages
-- DETAIL: CPU 5.20s/8.10s sec elapsed
```

**效果**：
- 立即更新统计信息（ANALYZE 部分）
- 标记 dead tuple 空间可重用
- 不锁表，业务可继续读写

### 4.2 根治方案（在线重建表）

```bash
# 用 pg_repack 在线重建（无锁）
pg_repack -t orders_log -h 192.168.1.100 -p 54321 -U dbadmin -d mydb

# 原理：
# 1. 创建影子表 orders_log_tmp
# 2. 在后台把 live tuple 复制到影子表
# 3. 同步增量（通过 trigger 捕获后续变更）
# 4. 原子切换（短时间拿 AccessExclusiveLock，几秒）
# 5. 删除原表，影子表改名
```

### 4.3 调优 autovacuum 配置（事前预防）

```sql
-- kingbase.conf / postgresql.conf
# 全局参数（重启生效）
autovacuum = on
autovacuum_max_workers = 6                   -- 默认 3，并发清理
autovacuum_naptime = 30s                     -- 默认 60s，更频繁唤醒
maintenance_work_mem = 2GB                   -- 默认 64MB，大表 vacuum 更高效
default_statistics_target = 500              -- 采样精度（默认 100）

# 单表参数（在线生效，推荐）
ALTER TABLE orders_log SET (
    autovacuum_enabled = true,
    autovacuum_vacuum_scale_factor = 0.02,   -- 2% 触发（原 20%）
    autovacuum_vacuum_threshold = 1000,
    autovacuum_analyze_scale_factor = 0.01,  -- 1% 触发 analyze
    autovacuum_vacuum_cost_delay = 10        -- 降低对业务 IO 影响
);
```

### 4.4 前后对比

| 维度 | 优化前 | 优化后 |
|------|--------|--------|
| **n_dead_tup** | 1750 万（35%） | 0（每次事务后立即清理） |
| **last_autovacuum** | 3 周前 | 30 秒前（持续运行） |
| **表大小** | 4.5 GB | 2.8 GB（pg_repack 后） |
| **索引大小** | 1.8 GB | 1.1 GB |
| **查询耗时 P99** | 2800 ms | 120 ms（提升 23 倍） |
| **CPU** | 65%（seq scan 消耗） | 18%（index scan） |
| **IO 等待** | 高（buffer hit 40%） | 低（buffer hit 92%） |

---

## 五、验证（制品层 / 环境层 / 应用层）

### 5.1 制品层（SQL 自验）

```sql
-- 验证 1：dead tuple 应清零
SELECT n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
WHERE relname = 'orders_log';
-- 期望：n_dead_tup < 1000，last_autovacuum 在 1 分钟内

-- 验证 2：表膨胀应恢复
SELECT * FROM pgstattuple('orders_log');
-- 期望：dead_tuple_percent < 5%

-- 验证 3：统计信息应最新
SELECT last_analyze, last_autoanalyze
FROM pg_stat_user_tables
WHERE relname = 'orders_log';
-- 期望：两个时间戳都在 5 分钟内

-- 验证 4：autovacuum 频率应提升
SELECT count(*), max(last_autovacuum)
FROM pg_stat_user_tables
WHERE last_autovacuum > now() - interval '1 hour';
-- 期望：count > 5（说明 autovacuum 频繁工作）
```

### 5.2 环境层（监控告警）

```sql
-- 加监控：dead tuple 超过 100 万告警
CREATE OR REPLACE FUNCTION check_table_bloat() RETURNS TABLE (
    table_name text,
    dead_tuples bigint,
    dead_pct numeric
) AS $$
    SELECT
        schemaname || '.' || relname,
        n_dead_tup,
        round(100.0 * n_dead_tup / NULLIF(n_live_tup, 0), 2)
    FROM pg_stat_user_tables
    WHERE n_dead_tup > 1000000
    ORDER BY n_dead_tup DESC;
$$ LANGUAGE SQL;

-- 加监控：长事务超过 30 分钟告警
SELECT pid, xact_start, left(query, 100)
FROM pg_stat_activity
WHERE xact_start < now() - interval '30 minutes';
```

### 5.3 应用层（业务验证）

```bash
# 1. 接口响应时间
wrk -t4 -c100 -d30s http://api.example.com/orders/list
# 期望：P99 < 200ms

# 2. 慢查询日志
grep "duration: " /var/log/kingbase/slow.log | tail -20
# 期望：无 > 1s 的查询

# 3. EXPLAIN 对比
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders_log WHERE user_id = 12345 ORDER BY create_time DESC LIMIT 20;
-- 优化前：Index Scan, rows=50000, time=2500ms
-- 优化后：Index Scan, rows=20, time=15ms
```

---

## 六、面试话术（90 秒版本）

> **面试官**："生产环境删了张大表的数据后，查询反而变慢，你如何排查？"
>
> **参考回答**：
>
> "我会按 '**定位 → 量化 → 处置 → 预防**' 四步走。
>
> **第一步定位**：查 `pg_stat_user_tables`，重点看 `n_dead_tup` 和 `last_autovacuum` 两个字段。如果 dead tuple 占比超过 20%，说明 autovacuum 没及时清理。如果 `last_autovacuum` 是几天前，说明要么触发阈值没到，要么被长事务阻塞。
>
> **第二步量化**：用 `pgstattuple` 扩展看 `dead_tuple_percent`，超过 20% 就是严重膨胀；同时用 `pg_stat_progress_vacuum` 看 autovacuum worker 是否在跑、跑到哪一步了。
>
> **第三步处置**：根据严重程度分三档——轻中度膨胀（< 20%）手动 `VACUUM ANALYZE`，不锁表，立即止血；中重度（20-50%）用 `pg_repack` 在线重建表；重度（> 50%）考虑维护窗口 `VACUUM FULL`，但要提前评估锁表时长。
>
> **第四步预防**：调 `autovacuum_vacuum_scale_factor` 从 0.2 降到 0.02，让大表更激进地触发；加监控告警 dead tuple > 100 万；定期清理长事务。
>
> 举一个实际案例：我们 KingbaseES V8R6 的订单表 5000 万行，凌晨删 1500 万行后查询从 100ms 飙到 3s。查 `n_dead_tup` 是 1750 万、占比 35%，`last_autovacuum` 是 3 周前。手动 `VACUUM ANALYZE` 后查询回到 120ms，再用 `pg_repack` 把表从 4.5GB 压到 2.8GB，最后调小 scale_factor 到 0.02，后续自动维护就健康了。"

**加分项**：提及 `VACUUM FREEZE` / transaction ID 回卷问题（32 亿事务 ID 用完会强制停库）；或对比 PG 与 MySQL InnoDB 的 MVCC 差异（undo log vs heap tuple 多版本）。

---

## 七、相关章节

### 同栏目兄弟

- [MySQL SQL 调优全流程指南](../mysql-tuning/README.md) — EXPLAIN + 索引优化思路（PG 调优异曲同工，但工具链不同）
- [批量插入：JDBC batch vs rewriteBatchedStatements 性能对比](../mysql-batch-operation/README.md) — 大批量操作思路（PG 的 COPY 命令才是对应的批量插入方案）
- [MVCC 实现原理深度剖析](../mvcc/README.md) — MySQL InnoDB MVCC（PG MVCC 完全不同：heap tuple + xmax 标记 vs undo log）
- [B+ Tree 为什么适合数据库索引](../bplus-tree/README.md) — 索引扫描原理（PG 用 B-tree 而非 B+ Tree，叶子节点直接存 TID）

### 主模块深读

- [PostgreSQL 深度原理](../../../03.data-stack/01-database/13-postgresql/README.md) — MVCC / 索引 / 扩展 / 高可用（含 VACUUM 与膨胀大章节，含人大金仓特化）

### 关联主题

- [PostgreSQL 深度原理](../../../03.data-stack/01-database/13-postgresql/README.md) — MVCC / 索引 / 扩展 / 高可用，含 VACUUM 与膨胀大章节、含人大金仓特化（同主模块深读，避免重复链接）

---

> 📅 2026-09-03 · 咬文嚼字 · PostgreSQL / KingbaseES · ⭐⭐⭐⭐（中频面试 + DBA/后端实战必会）

← [返回: 数据库咬文嚼字](../../README.md)
