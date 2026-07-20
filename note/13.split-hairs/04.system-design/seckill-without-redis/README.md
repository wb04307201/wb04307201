<!--
question:
  id: 04.system-design-seckill-without-redis
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐
  frequency: 中高
  scenario_type: 工程权衡 / 刁难题
  tags: [04.system-design, 秒杀, 高并发, 单机方案, 乐观锁, 刁难面试]
-->

# 500 人抢 1 瓶茅台，2 台服务器，不用 Redis / MQ，秒杀怎么写？

> 一句话定位：**大厂面试经典刁难题**。考察架构师的**应变能力** —— 当主流方案（Redis 分布式锁 / MQ 削峰）被禁用时，怎么用**最朴素的单机工具**解决问题。深度实战见 [主模块深度章节](../../../04.system-design/03-high-availability/rate-limiting/seckill-without-redis.md)。

> **系列定位**：高频刁难题（校招 / 社招都考）。考察"被限制时的工程判断力"。配套兄弟题：[限流原理面试题](../rate-limiting/README.md)。

---

⭐⭐⭐⭐ 深度级别（高级架构师级）
📚 前置知识：乐观锁 / 唯一约束 / Semaphore / DB 行锁 / 分布式一致性基础

---

## 引子：面试官的"刁难陷阱"

面试官："500 人抢 1 瓶茅台，2 台服务器，**不用 Redis / MQ**，秒杀怎么写？"

阿明答："用 Redis 分布式锁..."

面试官："**不用 Redis**，重答。"

阿明答："用 MQ 削峰..."

面试官："**也不用 MQ**，再答。"

阿明答："那... 用 synchronized？"

面试官："**2 台服务器**，单 JVM synchronized 没用。"

阿明愣住。

**这道题的陷阱**：**考察的不是"用什么分布式组件"，而是"组件被禁用时的应变能力"**。很多人卡在"主流方案被禁用"上，没意识到**业务规模决定方案** —— 500 人级别用单机方案完全够用。

---

## Q1：不用 Redis / MQ，秒杀怎么写？（先问清边界）

**答**：**先问清问题边界** —— 500 人 / 2 台服务器 / 库存=1 是"轻量级秒杀"，**单机方案完全够用**，强行上 Redis 是过度设计。

```text
问题边界：
├─ 人数 = 500（不是 500 万）
├─ 服务器 = 2 台（共享 DB）
├─ 库存 = 1（最关键的边界）
├─ 一次性活动（不是常态化秒杀）
└─ 不用 Redis / MQ（强制限制）

→ 轻量级单机方案足够
→ 不需要分布式组件
```

**反直觉点**：**业务规模决定方案**。很多人觉得"秒杀必须用 Redis" —— 但 500 人级别的秒杀用单机方案完全够用，**0 依赖、0 运维成本**。

**核心方案**：**乐观锁 + 唯一约束**（唯一能解决 2 台服务器一致性的单机方案）

```sql
-- 1. 乐观锁扣减库存（防超卖）
UPDATE product SET stock = stock - 1, version = version + 1
WHERE id = ? AND stock > 0;  -- 影响 0 行 = 失败

-- 2. 唯一约束防重复抢
CREATE TABLE seckill_order (
    user_id BIGINT, product_id BIGINT,
    UNIQUE KEY uk_user_product (user_id, product_id)
);
-- DuplicateKeyException → 用户重复抢
```

**2 台服务器共享同一 DB → 自动解决一致性问题**（DB 行锁 + 唯一约束保证）。

---

## Q2：5 大单机方案的优劣对比？怎么选？

**答**：根据场景选：

| 方案 | 代码量 | 性能 | 2 台服务器 | 防超卖 | 推荐度 |
|------|------:|-----:|:----------:|:------:|------:|
| **synchronized** | ⭐ | ⭐⭐ | ❌ 超卖 | ❌ | ⭐ |
| **AtomicInteger** | ⭐⭐ | ⭐⭐⭐ | ❌ 超卖 | ❌ | ⭐⭐ |
| **Semaphore** | ⭐⭐ | ⭐⭐⭐ | ❌ 超卖 | ❌ | ⭐⭐ |
| **乐观锁 + 唯一约束** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ **生产可用** | ✅ | ⭐⭐⭐⭐⭐ |
| **内存队列** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ 超卖 | ❌ | ⭐⭐⭐ |

**关键洞察**：**只有方案 4（乐观锁 + 唯一约束）能解决 2 台服务器一致性问题** —— 其他 4 个都是单 JVM 方案，2 台服务器会超卖。

**反模式**：强行上 Redis
- 500 人秒杀用 Redis = 过度设计
- 运维成本 +10，性能反而下降（多一跳网络）
- **业务规模决定方案**，不要为了用 Redis 而用 Redis

---

## Q3：库存=1 怎么避免超卖？（3 大机制）

**答**：**乐观锁 + version + 唯一约束**，3 大机制组合。

### 机制 1：乐观锁防超卖

```sql
-- 关键：WHERE stock > 0 条件
UPDATE product SET stock = stock - 1, version = version + 1
WHERE id = #{productId} AND stock > 0 AND version = #{version};
-- 影响行数 = 1 成功；= 0 失败（库存不足或 version 不对）
```

**反模式**：`UPDATE product SET stock = stock - 1`（**不带 `WHERE stock > 0`**）→ 库存可能扣成负数 → **超卖**。

### 机制 2：version 字段防 ABA

```text
时间线（无 version）：
T1: A 读 stock=1
T2: B 抢到 → stock=0
T3: 退货 → stock=1（ABA 问题）
T4: A 用 stock=1 提交 → 成功扣减 ❌（A 应该失败）

时间线（有 version）：
T1: A 读 stock=1, version=1
T2: B 抢到 → stock=0, version=2
T3: A 用 version=1 提交 → 影响 0 行（A 失败）✅
```

**结论**：**乐观锁必须带 version 字段**。

### 机制 3：唯一索引防重复抢

```sql
CREATE TABLE seckill_order (
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    UNIQUE KEY uk_user_product (user_id, product_id)  -- 关键
);
```

**插入冲突 → DuplicateKeyException → 回滚库存**。

**反直觉点**：**靠代码判重（`if (exists)` + `insert`）有 TOCTOU 漏洞**（两次操作之间状态变了），**靠唯一索引 100% 防重**。

---

## Q4：2 台服务器数据怎么一致？共享 DB 方案

**答**：**2 台服务器共享同一 DB → 用 DB 行锁 + 唯一约束自动解决一致性**。

### 方案对比

| 方案 | 一致性保证 | 复杂度 | 适用 |
|------|-----------|------|------|
| **共享 DB + 乐观锁** | DB 行锁 + 唯一约束 | ⭐ | 500 人级别（推荐）|
| 主从读写分离 | 最终一致（主从延迟）| ⭐⭐⭐ | 读多写少（秒杀不适用）|
| 分布式锁 | 强一致 | ⭐⭐⭐⭐⭐ | 10000+ 写（过度设计）|

**轻量级秒杀推荐：共享 DB + 强制读主**（避免主从延迟导致超卖）。

```java
@Transactional
public boolean trySeckill(Long userId, Long productId) {
    // 1. 乐观锁扣减库存
    int rows = productMapper.deductStock(productId);
    if (rows == 0) return false;

    // 2. 插入订单（靠唯一约束防重复抢）
    try {
        orderMapper.insert(new Order(userId, productId));
        return true;
    } catch (DuplicateKeyException e) {
        // 重复抢 → 回滚库存
        productMapper.addStock(productId, 1);
        return false;
    }
}
```

**反直觉点**：**单 JVM 的 synchronized / Semaphore 在 2 台服务器下完全失效**（每台服务器各自加锁，2 台都能扣减 → 超卖）。**只有 DB 级别的锁能跨服务器**。

---

## Q5：面试被追问"为什么不用 Redis"怎么答？

**答**：**业务驱动 + 成本 / 运维 / 风险 3 维度**。

### 答法模板

> "不用 Redis 是**业务规模决定的**，不是技术限制。具体来说：
>
> **第一**，500 人 / 2 台 / 库存=1 是**轻量级秒杀**，单机方案完全够用。500 个请求打 DB，500ms 内完成，DB 完全扛得住。
>
> **第二**，**强上 Redis 的成本**：
> - 运维成本：Redis 集群需要部署 / 监控 / 备份
> - 网络成本：多一跳网络（Redis → 应用 → DB），延迟增加
> - 复杂度：分布式锁要考虑脑裂 / 时钟漂移
> - **500 人级别不值得**
>
> **第三**，**单机的乐观锁方案已经够稳**：
> - DB 行锁保证跨服务器一致
> - 唯一约束保证不超卖
> - version 字段防 ABA
> - 实战验证过 10000+ 级别也能扛
>
> **第四**，**何时升级到 Redis**：
> - DB QPS > 1000 → 升级
> - 库存频繁冲突 → 升级
> - 用户感知延迟 > 1 秒 → 升级
> - **500 人级别完全不需要**"

### 踩分点

- ✅ 提"业务规模决定方案" → 显式工程判断
- ✅ 提"强上 Redis 的成本" → 显式权衡意识
- ✅ 提"乐观锁方案已经够稳" → 显式实战经验
- ✅ 提"何时升级" → 显式演进意识

---

## 总结：面试答这题的 3 层结构

**30 秒简版**：
> "500 人 / 2 台 / 库存=1 是轻量级秒杀，**业务规模决定方案**——单机乐观锁 + 唯一约束完全够用。具体：**乐观锁扣库存**（防超卖 + ABA）+ **唯一索引防重复抢** + **2 台服务器共享 DB 自动一致**。500 个请求 ~500ms 完成，DB 扛得住。**不用 Redis 是因为不值得**——运维成本 / 网络成本 / 复杂度都上升，500 人级别单机方案已稳。"

**60 秒扩展版**（如果面试官追问细节）：
> "具体来说，单机的 `synchronized` / `Semaphore` / `AtomicInteger` 都不行——**单 JVM 锁在 2 台服务器下失效**，每台服务器各自加锁 → 超卖。
>
> 只有**DB 级别的锁**能跨服务器：**乐观锁 `UPDATE ... WHERE stock > 0` + version 字段防 ABA + UNIQUE KEY 防重复抢**。这 3 个机制组合保证 2 台服务器下**零超卖**。
>
> 性能上：500 个请求，乐观锁 + 唯一约束大约 500ms，DB 压力 < 1000 QPS，完全在 MySQL 承受范围内。**强上 Redis 反而是过度设计**——Redis 集群运维成本 + 多一跳网络延迟，对 500 人级别是负优化。
>
> **何时升级**：DB QPS > 1000 / 库存频繁冲突 / 用户感知延迟 > 1 秒 → 升级到 Redis。500 人级别完全不需要。"

**踩分点提醒**：
- ✅ 提"业务规模决定方案" → 显式不教条
- ✅ 提"单 JVM 锁在 2 台服务器下失效" → 显式分布式常识
- ✅ 提"3 大机制"（乐观锁 + version + 唯一索引）→ 显式实战深度
- ✅ 提"500ms 完成 / DB 扛得住" → 显式性能估算
- ✅ 提"何时升级" → 显式演进意识

---

## 相关章节

**主模块**：
- [秒杀刁难题深度章节](../../../04.system-design/03-high-availability/rate-limiting/seckill-without-redis.md) — 5 方案对比 + 3 大机制 + 2 台服务器一致性 + 实战模板
- [限流原理（rate-limiting/README）](../../../04.system-design/03-high-availability/rate-limiting/README.md) — 4 算法 + 4 策略
- [乐观锁（optimistic-lock）](../../../04.system-design/06-idempotency/optimistic-lock/README.md) — 库存扣减基础
- [MySQL 行锁原理](../../../01.java/concurrency/juc-locks/README.md) — 乐观锁底层实现

**同栏目兄弟**：
- [限流算法面试题](../rate-limiting/README.md) — 通用限流原理面试
- [缓存一致性面试题](../cache-consistency/README.md) — 缓存场景

**餐厅叙事（12.story）**：
- [04 · peak-traffic-defense（餐厅流量防御）](../../../12.story/04-peak-traffic-defense.md) — 餐厅流量 = 茅台秒杀的隐喻版

---

> 📅 2026-07-06 · 咬文嚼字 · 04.system-design · ⭐⭐⭐⭐

← [返回系统设计咬文嚼字](../README.md)
