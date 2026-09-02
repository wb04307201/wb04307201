<!--
module:
  parent: system-design
  slug: system-design/distributed-lock
  type: article
  category: 主模块子文章
  summary: 分布式锁 4 种主流方案（Redis/ZK/Etcd/DB）的实现原理 + 生产实践 + 选型决策树，Redisson 是 Java 主流方案，附 5 个生产踩坑案例。
  depth: ⭐⭐⭐⭐⭐
-->

# 分布式锁

---

> **一句话定位**：分布式锁用 Redis/ZooKeeper/Etcd/数据库 4 类方案在多节点间实现互斥，需权衡性能/一致性/容错。**Redisson 是 Java 生态事实标准**（看门狗续期 + 可重入 + 多算法一站式）。

分布式锁是分布式系统中用于协调多个节点对共享资源访问的一种机制，确保在多进程或多服务环境下，同一时间只有一个节点能访问临界资源，避免并发问题（数据不一致、超卖、重复扣款）。

## 一、为什么需要分布式锁？

| 场景 | 单机锁失效原因 | 后果 |
|------|--------------|------|
| **电商库存扣减** | 3 个 Tomcat 实例各自进程内 synchronized | **超卖**（卖出 > 库存数）|
| **分布式任务调度** | 多节点 cron 重复触发 | 重复扣款 / 重复发短信 |
| **缓存重建** | 多个节点同时查 DB 回写 | 雪崩 / DB 被打挂 |
| **消息消费** | 多个 consumer 抢同一消息 | **重复消费** |

**核心矛盾**：单机锁（Java `synchronized` / `ReentrantLock` / 文件锁）只能保护单进程内的临界区，**多进程/多机场景下完全失效**。

## 二、4 大核心特性（合格锁的 6 项必备）

| 特性 | 说明 | 实现难度 |
|------|------|:---:|
| **互斥性** | 同一时间只有一个客户端持有锁 | 必做 |
| **不死锁** | 客户端宕机后锁能自动释放 | 必做 |
| **可重入性** | 同一线程多次获取同一锁不阻塞 | 建议 |
| **容错性** | 部分节点故障不影响锁服务 | 必做 |
| **非阻塞获取** | `tryLock()` 可立即返回失败 | 建议 |
| **公平性** | 先到先得，避免饥饿 | 可选 |

## 三、4 种主流方案对比

| 方案 | 性能 | 一致性 | 复杂度 | 适用场景 | 推荐度 |
|------|:---:|:---:|:---:|------|:---:|
| **Redis (Redisson)** | ⭐⭐⭐⭐⭐ | 中（AP） | 低 | 高并发 + 性能敏感 | ⭐⭐⭐⭐⭐ |
| **ZooKeeper** | ⭐⭐⭐ | 强（CP） | 高 | 强一致 + 中等并发 | ⭐⭐⭐ |
| **Etcd** | ⭐⭐⭐ | 强（CP） | 中 | K8s 原生生态 | ⭐⭐⭐⭐ |
| **数据库 (MySQL)** | ⭐ | 强 | 低 | 临时方案 / 已有 DB | ⭐⭐ |

### 1. Redis（首选，AP 思想）

**核心命令**：
```bash
SET lock_key client_id NX PX 30000
# NX = 仅不存在时设置（加锁）
# PX 30000 = 30 秒过期（防死锁）
```

**释放锁（Lua 原子脚本）**：
```lua
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
else
    return 0
end
-- 必须用 Lua：GET + DEL 之间不能被其他客户端打断
```

**生产痛点 → 解决方案**：

| 痛点 | 现象 | Redisson 解决方案 |
|------|------|------------------|
| **锁过期提前** | 业务 30s 没跑完，锁已过期被其他客户端抢 | **看门狗（WatchDog）**：每 1/3 过期时间自动续期 |
| **误删别人锁** | A 业务慢导致锁过期，B 抢锁，A 完成后 DEL 删了 B 的锁 | **clientId 校验**（Lua 脚本比对）|
| **单点 Redis 故障** | Redis 宕机导致锁丢失 | **Redlock**：5 个独立 Redis 节点过半同意 |

**Redisson 一行代码**：
```java
RLock lock = redisson.getLock("order:lock");
try {
    // 默认 30s 自动过期，看门狗自动续期
    lock.lock();
    doBusiness();  // 业务执行时间可以 > 30s
} finally {
    lock.unlock();  // 只解锁自己 clientId 的锁
}
```

### 2. ZooKeeper（CP 思想，强一致）

**实现原理**：临时顺序节点 + Watcher
1. 客户端在 `/lock_node` 下创建**临时顺序节点**（如 `lock_000003`）
2. 获取 `/lock_node` 下所有子节点，判断自己是否最小
3. 若最小 → 获得锁；若不是 → 监听前一个节点（`lock_000002`）
4. 当前一个节点删除（临时节点会话断开自动删除）→ Watcher 通知 → 重新判断

**优点**：
- 天然强一致（ZAB 协议）
- 临时节点自动删除，**不会死锁**
- Watcher 机制高效

**缺点**：
- 写性能较低（每次加锁 = 写节点）
- ZK 集群维护成本高
- Session 过期会导致锁误释放

### 3. Etcd（K8s 生态首选）

**实现原理**：Lease + Revision
```bash
# 加锁
etcdctl put /lock/key client_id --lease=30s
# etcd 保证全局唯一的 Revision（递增）
# client_id 校验防止误删
```

**适用**：Kubernetes 生态应用、配置中心、服务发现。

### 4. 数据库（兜底方案）

```sql
-- 加锁（唯一索引）
INSERT INTO distributed_lock (lock_key, client_id, expire_at)
VALUES ('order_lock', UUID(), NOW() + INTERVAL 30 SECOND);
-- 成功 → 获得锁；失败（主键冲突）→ 锁被占
```

**致命缺点**：每次加锁 = 1 次 DB 写，**性能极差**（100-1000 倍于 Redis），仅适用于：
- 已有 DB 不引入新组件
- 极低并发（如 1 分钟一次的任务调度）

## 四、Redlock 算法（Redis 集群方案）

**问题**：单 Redis 节点宕机 → 锁丢失

**方案**（Antirez 提出的多 Redis 共识）：
```
1. 客户端记录当前时间 T1
2. 依次向 N 个独立 Redis 节点申请锁（每个节点 SET NX PX）
3. 记录申请完所有节点的时间 T2
4. 当且仅当 满足以下全部条件 → 获得锁：
   a) 获得锁的节点数 ≥ N/2 + 1（过半）
   b) T2 - T1 < 锁过期时间
5. 锁的有效期 = 过期时间 - (T2 - T1)
```

**争议**：Martin Kleppmann《How to do distributed locking》指出 Redlock **不安全**（依赖时钟同步，GC 停顿可能误判）。**实战结论**：99% 场景用单 Redis + Redisson 即可，不建议上 Redlock。

## 五、生产踩坑案例（5 大常见事故）

### 案例 1：锁过期提前导致重复扣款

```
T0: 客户端 A 加锁成功（过期 30s）
T20: 业务没跑完（GC 停顿 15s）
T30: 锁过期
T31: 客户端 B 加锁成功（同一资源）
T50: A 业务跑完，扣款两次！
```

**修复**：Redisson 看门狗（默认 30s 过期，每 10s 自动续期）

### 案例 2：误删别人的锁

```lua
-- 错误：A 锁过期被 B 抢，A 完成后 DEL 删了 B 的锁
if redis.call('GET', KEYS[1]) == ARGV[1] then DEL  -- 没有 ARGV[1] 比对
```

**修复**：Lua 脚本必须比对 client_id

### 案例 3：Redis 集群脑裂

主从切换瞬间，主节点锁未同步到从节点 → 双客户端都"获得锁"

**修复**：业务层加版本号 / 时间戳校验（不要只信 Redis）

### 案例 4：续期线程挂掉

Redisson 看门狗在客户端进程内，**进程 OOM 后锁过期**

**修复**：业务超时保护 + 服务端监控 + 设置 `lockWatchdogTimeout` 上限

### 案例 5：事务回滚 + 锁提前释放

```java
@Transactional
public void pay() {
    lock.lock();
    try {
        reduceStock();  // 抛异常
    } finally {
        lock.unlock();  // 提前释放，其他线程进来
        // 事务回滚（但锁已经释放）
    }
}
```

**修复**：锁释放必须在**事务提交后**（`TransactionSynchronizationManager.registerSynchronization`）

## 六、选型决策树

```
Q1: 性能要求？
  ├─ 高（万 QPS+）→ Redis + Redisson ✅
  └─ 中低（百 QPS）→ Q2

Q2: 强一致要求？
  ├─ 是 → ZK / Etcd
  └─ 否 → Redis

Q3: 已有组件？
  ├─ 已有 Redis → 直接 Redis
  ├─ 已有 MySQL → DB 锁（临时方案）
  └─ 都没有 → 引入 Redis（最简单）

Q4: K8s 生态？
  └─ 是 → Etcd（k8s-control-plane 已用）

Q5: 可接受短暂脑裂？
  ├─ 是 → Redis
  └─ 否 → ZK
```

## 七、5 个常见误区

| 误区 | 真相 |
|------|------|
| `SETNX` + 过期时间 = 安全锁 | ❌ 必须配 Lua 释放脚本，否则会误删 |
| 单 Redis = 高可用 | ❌ Redis 宕机锁丢失，业务需容错 |
| Redlock = 分布式锁银弹 | ❌ Martin Kleppmann 指出依赖时钟不安全 |
| 看门狗 = 万无一失 | ❌ GC 停顿 / 进程 OOM 仍可能丢锁 |
| ZK 临时节点 = 强一致 | ⚠️ Session 过期是常见坑 |

## 八、面试高频问题

**Q: Redis 分布式锁与 ZK 分布式锁的区别？**

**A**:

| 维度 | Redis | ZooKeeper |
|------|-------|-----------|
| 性能 | 高（10w+ QPS）| 中（万级 QPS）|
| 一致性 | AP（最终一致）| CP（强一致）|
| 实现 | SETNX + Lua | 临时顺序节点 |
| 容错 | 主从切换可能丢锁 | Session 过期可能误释放 |
| 推荐 | 高并发首选 | 强一致场景 |

**Q: Redisson 看门狗原理？**

A：
1. 加锁成功 → 启动 `scheduleExpirationRenewal` 定时任务
2. 每 `过期时间 / 3`（默认 10s）续期一次
3. 默认过期时间 30s（`lockWatchdogTimeout` 可配）
4. unlock / 业务完成 → 取消续期任务

## 九、相关章节

- [UUID](../distributed-id/uuid/README.md) — 锁的客户端标识（client_id）
- [分布式事务](../distributed-transaction/README.md) — 锁在事务协调中的作用
- [服务注册与发现](../service-discovery/README.md) — Etcd/ZK 同时支持锁与发现
- [分布式 ID 总览](../distributed-id/README.md) — 唯一标识生成方案
- [缓存一致性](../../04-high-performance/cache-patterns/README.md) — 锁+缓存双写策略

## 十、参考链接

- [Redisson 官方文档](https://redisson.org/docs/)
- [Redlock 算法原文（Antirez）](https://redis.io/docs/manual/patterns/distributed-locks/)
- [How to do distributed locking（Martin Kleppmann）](https://martinfowler.com/articles/patterns-of-distributed-systems/distributed-lock.html)
- [Apache Curator（ZooKeeper 客户端）](https://curator.apache.org/)

← [返回分布式系统](../README.md)