<!--
question:
  id: 03.database-sharding-resize
  topic: 03.database
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构困境
  tags: [03.database, 分库分表, 扩容, resharding, 数据迁移, ShardingSphere]
-->

# 分表后数据膨胀如何调整分表策略

> 经典数据库面试题（分库分表、架构演进高频）。考察的不是"分表怎么分"，而是 **分完之后怎么扩** —— 在线 resharding 方案设计 + 数据一致性保障 + 业务无感切换。完整概念见 [分库分表](../../../04.system-design/04-high-performance/database-optimization/db-sharding/README.md)。

> **系列定位**：中高级后端面试题（架构师必考）。考察的是"从 4 库扩到 8 库"这种**真实生产场景**的工程能力，而不是纸上谈兵。

---

## 引子：凌晨的告警

```text
🚨 告警：order_3 表行数突破 5000 万，查询 P99 延迟从 20ms 飙升到 800ms
```

当初按 `user_id % 4` 分了 4 张表，每张表设计容量 2000 万行。

两年后数据翻倍，order_3 成了热点表。老板说："扩到 8 张表，不能停服，不能丢数据。"

面试官问："你怎么做？从方案设计到灰度切换，讲一遍。"

如果你只能回答"用 ShardingSphere 扩一下"——面试就结束了。

---

## 一、什么时候该扩容？

| 信号 | 阈值参考 | 说明 |
|------|---------|------|
| **单表行数** | > 2000 万行（MySQL InnoDB） | B+ Tree 层级增加，查询变慢 |
| **P99 延迟** | 持续 > 200ms | 索引效率下降，磁盘 I/O 瓶颈 |
| **磁盘空间** | > 80% | 扩容前预留空间 |
| **写入 TPS** | 接近单表极限 | 锁竞争加剧 |

**扩容前确认**：先排查是否是"假膨胀"—— 大量冷数据？→ 先做[冷热分离](../../../04.system-design/04-high-performance/database-optimization/cold-hot-data-separation/README.md)，可能不需要扩容。

## 二、5 种扩容方案对比

| 方案 | 原理 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|---------|
| **翻倍扩容** | 表数量翻倍（4→8→16），旧数据按新 hash 迁移 | 路由规则简单，扩容后可继续翻倍 | 每次翻倍数据量翻倍，迁移量大 | **主流方案**，大多数场景 |
| **一致性哈希** | 虚拟节点环，扩容只迁移 1/N 数据 | 迁移量小（只迁移受影响的数据） | 实现复杂，跨分片查询困难 | 缓存类 / NoSQL 场景 |
| **Range 分片** | 按范围分片（1-1000万→表1），新增表接新范围 | 零迁移，旧数据不动 | 数据倾斜（新表热、旧表冷） | 日志/流水类（只追加） |
| **双写过渡** | 新旧库同时写，逐步切读流量 | 安全，可随时回滚 | 双倍写入开销，一致性保障难 | 高可用要求的核心业务 |
| **逻辑扩容** | 不改物理分片，加读副本/缓存/ES | 零迁移风险 | 不解决单表大小问题 | 读多写少场景（临时方案） |

## 三、翻倍扩容详解（主流方案）

### 3.1 路由规则变化

```text
扩容前：4 张表
  order_0: user_id % 4 == 0
  order_1: user_id % 4 == 1
  order_2: user_id % 4 == 2
  order_3: user_id % 4 == 3

扩容后：8 张表
  order_0: user_id % 8 == 0
  order_1: user_id % 8 == 1
  order_2: user_id % 8 == 2
  order_3: user_id % 8 == 3
  order_4: user_id % 8 == 4
  order_5: user_id % 8 == 5
  order_6: user_id % 8 == 6
  order_7: user_id % 8 == 7
```

**关键发现**：`user_id % 4 == 0` 的数据在扩容后分到 `order_0` 或 `order_4`（因为 `x % 8 == 0` 和 `x % 8 == 4` 都满足 `x % 4 == 0`）。这意味着**每张旧表的数据恰好一半留原表、一半迁新表**。

### 3.2 迁移步骤（6 步）

```text
Step 1: 建表
  → 新建 order_4 ~ order_7（表结构与旧表完全一致）

Step 2: 全量迁移
  → 扫描旧表，按新路由规则写入新表
  → order_0 中 user_id % 8 == 4 的行 → 写入 order_4
  → order_1 中 user_id % 8 == 5 的行 → 写入 order_5
  → ...

Step 3: 增量追平
  → 全量迁移期间旧表仍有新写入
  → 用 Binlog（Canal / Flink CDC）追增量，写入新表

Step 4: 双写校验
  → 新旧库同时写入，对比数据一致性
  → 行数 + Checksum 逐表校验

Step 5: 灰度切读
  → 1% → 10% → 50% → 100% 逐步将读流量切到新路由
  → 观察 P99 / 错误率

Step 6: 切写 + 下线旧路由
  → 写流量切到新路由
  → 停止双写，观察 1 周
  → 确认无误后清理旧数据（不急，留 1 个月）
```

### 3.3 数据一致性保障

```java
// 全量迁移伪代码
for each row in old_table:
    new_shard = row.user_id % NEW_SHARD_COUNT
    if new_shard != old_shard:
        insert into new_table(new_shard) values (row)
        // 幂等：INSERT IGNORE / ON DUPLICATE KEY UPDATE

// 增量追平（Binlog 监听）
canal.subscribe("old_db.old_table")
for each binlogEvent:
    new_shard = event.user_id % NEW_SHARD_COUNT
    if new_shard != old_shard:
        applyToNewTable(event)
```

## 四、双写方案详解（高可用场景）

```text
阶段 1: 只写旧库（现状）
  WRITE → old_db

阶段 2: 双写（过渡期）
  WRITE → old_db + new_db（异步复制 / 业务层双写）
  READ  ← old_db（读流量不变）

阶段 3: 切读
  WRITE → old_db + new_db
  READ  ← new_db（灰度 1% → 100%）

阶段 4: 切写
  WRITE → new_db（主）+ old_db（兜底，可回滚）
  READ  ← new_db

阶段 5: 单写新库
  WRITE → new_db
  READ  ← new_db
  old_db 只保留 1 个月（回滚保险）
```

**关键风险**：双写期间如果一边成功一边失败 → 数据不一致。
**解法**：
- 业务层双写：先写旧库，异步写新库，失败重试 + 告警
- Binlog 复制：Canal/Maxwell 监听旧库 Binlog，写入新库（最终一致）
- 定时校验脚本：每小时对比新旧库行数 + Checksum

## 五、常见陷阱

### 陷阱 1：扩容不需要迁移数据

- **真相**：除非用 Range 分片（只追加），否则 hash 取模方案扩容一定需要迁移数据
- 一致性哈希迁移量最小（1/N），但不是零

### 陷阱 2：直接改路由规则就行

- **真相**：改了 `user_id % 4` 为 `user_id % 8` 后，不迁移数据的话，一半查询会查到空结果
- 必须**先迁移数据，再切路由**

### 陷阱 3：全量迁移可以一步到位

- **真相**：全量迁移期间旧库仍在写入 → 必须全量 + 增量追平两步走
- 漏掉增量追平 = 迁移期间的新数据丢失

### 陷阱 4：扩容后性能线性提升

- **真相**：翻倍扩容只解决了单表大小问题，跨分片查询、分布式事务等开销不变
- 如果瓶颈是"跨分片 JOIN"，扩容不解决问题

### 陷阱 5：ShardingSphere 一键搞定

- **真相**：ShardingSphere-Scaling 提供了迁移工具，但路由规则设计、灰度策略、回滚方案仍需人工设计
- 工具解决"怎么搬"，架构师解决"搬之前和搬之后的事"

## 六、最佳实践

1. **先冷热分离，再考虑扩容** — 如果 60% 是冷数据，归档后可能不需要扩容
2. **分表数量选 2 的幂** — 4/8/16/32，翻倍扩容时路由规则变化最友好
3. **全量迁移用限速** — 别打满数据库 I/O，控制在 30% 带宽以内
4. **灰度切流用百分比** — 1% → 10% → 50% → 100%，每步观察 30 分钟
5. **保留回滚能力** — 旧库至少保留 1 个月，切回路由即可恢复
6. **监控先行** — 迁移前配好全链路监控（P99 / TPS / 错误率 / 行数对比）

## 七、面试话术（90 秒版本）

> "分表后数据膨胀的扩容，核心是**在线 resharding**，关键挑战是迁移期间不影响业务。
>
> **主流方案是翻倍扩容**：从 4 表扩到 8 表，路由规则从 `user_id % 4` 变为 `user_id % 8`。每张旧表的数据恰好一半留在原表、一半迁到新表。
>
> **迁移分 6 步**：建表 → 全量迁移 → Binlog 增量追平 → 双写校验 → 灰度切读（1%→100%）→ 切写 + 下线旧路由。
>
> **数据一致性靠三段式**：全量迁移 + Binlog 增量追平 + 定时 Checksum 校验。
>
> **高可用场景用双写过渡**：新旧库同时写 → 切读 → 切写 → 单写新库，全程可回滚。
>
> **扩容前先做冷热分离**，归档冷数据后可能根本不需要扩容。分表数量选 2 的幂（4/8/16），方便后续继续翻倍。"

## 八、相关章节

- 主模块：[`分库分表`](../../../04.system-design/04-high-performance/database-optimization/db-sharding/README.md) — 分库分表全景（垂直/水平/分片算法/分片键选择）
- 同模块：[`数据迁移与同步`](../../../03.database/10-data-migration/README.md) — DataX / Canal / Flink CDC 迁移工具链
- 同栏目：[`大事务的危害与拆分`](../mysql-large-transaction/README.md) — 迁移过程中的事务控制
- 同栏目：[`MySQL 主从复制延迟`](../replication-lag/README.md) — 增量同步延迟问题
- 相关：[`分布式 ID 生成方案`](../../04.system-design/distributed-id/README.md) — 分表后的全局唯一 ID

---

> 📅 2026-07-07 · 咬文嚼字 · 分表扩容策略 · ⭐⭐⭐⭐⭐（高频面试 + 架构师必备）

← [返回数据库咬文嚼字](../README.md)
