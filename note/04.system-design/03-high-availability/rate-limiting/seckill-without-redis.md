<!--
module:
  parent: system-design
  slug: system-design/rate-limiting/seckill-without-redis
  type: article
  category: 主模块子文章
  summary: 不用 Redis/MQ 怎么写秒杀？5 大单机方案 + 库存=1 特殊处理 + 2 台服务器一致性 + 实战模板。
-->

# 不用 Redis / MQ，秒杀怎么写？（5 大单机方案对比）

> 一句话定位：面试官刁难场景 —— **500 人抢 1 瓶茅台 / 2 台服务器 / 不用 Redis / MQ**。主流方案都假设有分布式组件，**强制不用**就要走单机方案。本文给出 **5 大单机方案**对比 + **库存=1 特殊处理** + **2 台服务器一致性** + **实战模板**。

> **同模块兄弟**：
> - [限流原理（rate-limiting/README）](README.md) — 通用限流原理（4 算法 + 4 策略）
> - [乐观锁（optimistic-lock）](../../06-idempotency/optimistic-lock/README.md) — 库存扣减基础

---

## 一、问题边界（先问清再答）

很多人一上来就答"用 Redis 分布式锁"，但**面试官问"不用 Redis"**——必须先确认边界：

```
500 人抢 1 瓶茅台
├─ 库存 = 1（最关键的边界）
├─ 人数 = 500（不是 500 万）
├─ 服务器 = 2 台（不是 100 台集群）
├─ 不用 Redis / MQ（强制限制）
└─ 一次性活动（不是常态化秒杀）

→ 轻量级单机方案足够
→ 不需要分布式组件
```

**反直觉点**：**业务规模决定方案** —— 500 人 / 2 台 / 库存=1 用单机方案完全够用，强行上 Redis 反而是过度设计。

---

## 二、5 大单机方案对比

### 方案 1：`synchronized` + JVM 内存标志（最简单）

**原理**：用 `synchronized` 保证原子性，用 JVM 内存 Map 标记已抢用户。

```java
public class SimpleSeckill {
    private int stock = 1;  // 库存 1 瓶
    private Set<Long> winners = new HashSet<>();  // 已抢用户

    public boolean trySeckill(Long userId) {
        synchronized (this) {
            if (stock <= 0) {
                return false;  // 已抢完
            }
            if (winners.contains(userId)) {
                return false;  // 重复抢
            }
            // 模拟下单业务
            stock--;
            winners.add(userId);
            return true;
        }
    }
}
```

**优点**：
- ✅ 代码最简单（10 行搞定）
- ✅ 0 依赖（纯 JDK）

**缺点**：
- ❌ **单 JVM 锁**，2 台服务器各自加锁 → 超卖风险
- ❌ 重启 JVM 内存丢失（库存状态需持久化）

**适用**：**demo / 单机测试**，**生产不能用**（双服务器会超卖）。

---

### 方案 2：`AtomicInteger`（CAS 无锁）

**原理**：用 CAS 操作保证原子性，无需加锁。

```java
public class AtomicSeckill {
    private final AtomicInteger stock = new AtomicInteger(1);  // 库存 1
    private final Set<Long> winners = ConcurrentHashMap.newKeySet();

    public boolean trySeckill(Long userId) {
        if (winners.contains(userId)) {
            return false;
        }
        // CAS 自旋
        while (true) {
            int current = stock.get();
            if (current <= 0) {
                return false;  // 已抢完
            }
            if (stock.compareAndSet(current, current - 1)) {
                winners.add(userId);
                return true;
            }
            // CAS 失败重试
        }
    }
}
```

**优点**：
- ✅ 比 synchronized 快（无阻塞）
- ✅ 0 依赖

**缺点**：
- ❌ **单 JVM 限制**，2 台服务器依然超卖
- ❌ CAS 自旋高并发下 CPU 空转

**适用**：单机高并发；**生产依然不够**（双服务器）。

---

### 方案 3：`Semaphore`（信号量限流 + 库存）

**原理**：Semaphore 初始许可 = 库存数，`acquire()` 获取许可就成功。

```java
public class SemaphoreSeckill {
    private final Semaphore stockSemaphore = new Semaphore(1);  // 库存 1
    private final Set<Long> winners = ConcurrentHashMap.newKeySet();

    public boolean trySeckill(Long userId) {
        if (winners.contains(userId)) {
            return false;
        }
        // 非阻塞获取许可
        if (!stockSemaphore.tryAcquire()) {
            return false;  // 已抢完
        }
        winners.add(userId);
        return true;
    }
}
```

**优点**：
- ✅ 限流 + 库存一体（API 清晰）
- ✅ 非阻塞（`tryAcquire`）

**缺点**：
- ❌ **单 JVM 限制**，2 台服务器依然超卖
- ❌ 默认非公平（可能饥饿）

**适用**：单机 + 限流；**生产依然不够**。

---

### 方案 4：单节点乐观锁（DB 行锁 + 唯一约束）

**原理**：用数据库**唯一索引**保证幂等，用**乐观锁**防止超卖，**2 台服务器共享同一 DB** 自动解决一致性问题。

```sql
CREATE TABLE seckill_order (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    UNIQUE KEY uk_user_product (user_id, product_id)  -- 唯一约束：每个用户只能抢一次
);
```

```java
@Transactional
public boolean trySeckill(Long userId, Long productId) {
    // 1. 乐观锁扣减库存
    int updated = productMapper.deductStock(productId);
    if (updated == 0) {
        return false;  // 库存不足
    }

    // 2. 插入订单（靠唯一约束防重复）
    try {
        orderMapper.insert(new Order(userId, productId));
        return true;
    } catch (DuplicateKeyException e) {
        // 触发唯一约束 → 用户重复抢
        // 回滚库存
        productMapper.addStock(productId, 1);
        return false;
    }
}
```

```sql
-- 乐观锁 SQL（关键）
UPDATE product SET stock = stock - 1, version = version + 1
WHERE id = #{productId} AND stock > 0 AND version = #{version};
```

**优点**：
- ✅ **2 台服务器共享 DB → 自动解决一致性问题**
- ✅ **唯一约束**防止用户重复抢
- ✅ **乐观锁**防止超卖
- ✅ 简单可靠（生产可用）

**缺点**：
- ❌ 高并发下 DB 压力大（5000+ 写请求）
- ❌ 需要 DB（MySQL / PostgreSQL）

**适用**：**2 台服务器 + 单 DB = 生产首选**（500 人级别足够）。

---

### 方案 5：内存队列（Disruptor / LinkedBlockingQueue）

**原理**：把请求入队，**单消费者**异步处理，保证**串行扣减**。

```java
public class QueueSeckill {
    private final BlockingQueue<SeckillRequest> queue = new LinkedBlockingQueue<>(1000);
    private final AtomicInteger stock = new AtomicInteger(1);
    private final Set<Long> winners = ConcurrentHashMap.newKeySet();

    public QueueSeckill() {
        // 单消费者线程
        new Thread(this::consume).start();
    }

    public boolean trySeckill(Long userId) {
        SeckillRequest req = new SeckillRequest(userId);
        // 异步提交，结果通过 Future 返回
        Future<Boolean> future = executor.submit(() -> {
            try {
                return process(req);
            } catch (Exception e) {
                return false;
            }
        });
        try {
            return future.get(100, TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            return false;  // 超时未抢到
        }
    }

    private boolean process(SeckillRequest req) {
        if (winners.contains(req.userId)) {
            return false;
        }
        if (stock.get() <= 0) {
            return false;
        }
        stock.decrementAndGet();
        winners.add(req.userId);
        return true;
    }
}
```

**优点**：
- ✅ **单消费者线程**保证原子性（无需锁）
- ✅ **背压机制**（队列满则拒绝）
- ✅ Disruptor 性能极高（百万 TPS）

**缺点**：
- ❌ **单 JVM 限制**，2 台服务器依然超卖
- ❌ 队列满会丢失请求（需监控）

**适用**：单机 + 高吞吐；**2 台服务器需要 MQ 或共享队列**（违背限制）。

---

## 三、5 方案对比表

| 方案 | 代码量 | 性能 | 2 台服务器 | 库存=1 防超卖 | 防重复抢 | 推荐度 |
|------|------:|-----:|:----------:|:-------------:|:--------:|------:|
| **synchronized** | ⭐ | ⭐⭐ | ❌ 超卖 | ⚠️ 单 JVM | ⚠️ 内存 | ⭐ |
| **AtomicInteger** | ⭐⭐ | ⭐⭐⭐ | ❌ 超卖 | ⚠️ 单 JVM | ⚠️ 内存 | ⭐⭐ |
| **Semaphore** | ⭐⭐ | ⭐⭐⭐ | ❌ 超卖 | ⚠️ 单 JVM | ⚠️ 内存 | ⭐⭐ |
| **乐观锁 + 唯一约束** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ **生产可用** | ✅ DB 唯一 | ✅ 唯一索引 | ⭐⭐⭐⭐⭐ |
| **内存队列** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ 超卖 | ⚠️ 单 JVM | ⚠️ 内存 | ⭐⭐⭐ |

**关键洞察**：**只有方案 4（乐观锁 + 唯一约束）能解决 2 台服务器一致性问题** —— 其他 4 个都是单 JVM 方案。

---

## 四、库存=1 的特殊处理（防超卖 / ABA / 重复扣减）

### 4.1 防超卖：乐观锁 SQL

```sql
-- 关键：stock > 0 条件 + version 字段
UPDATE product
SET stock = stock - 1, version = version + 1
WHERE id = ? AND stock > 0 AND version = ?;
-- 影响行数 = 1 成功；= 0 失败（库存不足或 version 不对）
```

**反直觉点**：**光靠 `UPDATE product SET stock = stock - 1` 不够** —— 必须带 `stock > 0` 条件，否则可能扣成负数。

### 4.2 防 ABA：用 version 字段

```
时间线：
T1: A 读 stock=1, version=1
T2: B 抢到 → stock=0, version=2
T3: A 用 version=1 提交 → 影响 0 行（A 失败）✅
```

**没有 version** 的情况：
```
T1: A 读 stock=1
T2: B 抢到 → stock=0
T3: 退货 → stock=1（ABA 问题：A 看到的和现在一样）
T4: A 用 stock=1 提交 → 成功扣减 ❌（A 应该失败）
```

**结论**：**乐观锁必须带 version 字段**（或在 UPDATE 中带原始 stock 值）。

### 4.3 防重复抢：唯一索引

```sql
-- 关键：UNIQUE KEY (user_id, product_id)
CREATE TABLE seckill_order (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    UNIQUE KEY uk_user_product (user_id, product_id)
);
```

**插入冲突 → DuplicateKeyException → 回滚库存**。

**反直觉点**：**靠代码判重（`if (exists)` + `insert`）有 TOCTOU 问题**，**靠唯一索引 100% 防重**。

---

## 五、2 台服务器的一致性（共享 DB 方案）

### 5.1 主从读写分离

```
写流量：服务器 A + 服务器 B → 写主 DB
读流量：服务器 A + 服务器 B → 读从 DB（最终一致）

秒杀场景：
├─ 库存扣减必须读主（避免主从延迟导致超卖）
└─ 订单查询可以读从（容忍 1 秒延迟）
```

### 5.2 同步方案（避免主从延迟）

```
方案 1：强制读主
  ├─ 所有请求走主 DB（牺牲读扩展性）
  └─ 简单可靠

方案 2：缓存 + 异步同步
  ├─ 库存数据先写 Redis（如果有）
  └─ 异步同步到 DB（最终一致）

方案 3：定时同步检查
  ├─ 每秒检查主从延迟
  └─ 延迟 > 1 秒告警
```

**轻量级秒杀推荐**：**强制读主**（500 人级别，DB 压力不大，简单可靠）。

### 5.3 双写方案（避免单 DB 单点）

```
主 DB ← 同步 ← 从 DB
├─ 主 DB 写：服务器 A 写主，服务器 B 写主
├─ 主 DB 故障 → 从 DB 升级为主
└─ 异步同步：mysql-binlog / Debezium

500 人秒杀：单主从足够（不需要双主）
```

---

## 六、实战模板（500 人 / 2 台服务器 / 库存=1）

### 6.1 数据库准备

```sql
-- 商品表（带 version）
CREATE TABLE product (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    stock INT NOT NULL DEFAULT 0,
    version INT NOT NULL DEFAULT 0
);

-- 订单表（带唯一约束）
CREATE TABLE seckill_order (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_product (user_id, product_id)
);

-- 初始化库存
INSERT INTO product (id, name, stock) VALUES (1, '茅台', 1);
```

### 6.2 Java 代码（生产级）

```java
@Service
public class SeckillService {
    @Autowired
    private ProductMapper productMapper;

    @Autowired
    private OrderMapper orderMapper;

    @Transactional(rollbackFor = Exception.class)
    public boolean trySeckill(Long userId, Long productId) {
        // 1. 乐观锁扣减库存（防超卖）
        int rows = productMapper.deductStock(productId);
        if (rows == 0) {
            return false;  // 库存不足
        }

        // 2. 插入订单（靠唯一约束防重复抢）
        try {
            Order order = new Order();
            order.setUserId(userId);
            order.setProductId(productId);
            orderMapper.insert(order);
            return true;
        } catch (DuplicateKeyException e) {
            // 用户重复抢 → 回滚库存
            productMapper.addStock(productId, 1);
            return false;
        }
    }
}

@Mapper
public interface ProductMapper {
    @Update("UPDATE product SET stock = stock - 1, version = version + 1 " +
            "WHERE id = #{productId} AND stock > 0")
    int deductStock(Long productId);

    @Update("UPDATE product SET stock = stock + #{delta}, version = version + 1 " +
            "WHERE id = #{productId}")
    int addStock(@Param("productId") Long productId, @Param("delta") int delta);
}
```

### 6.3 Controller 层（加限流防雪崩）

```java
@RestController
public class SeckillController {
    @Autowired
    private SeckillService seckillService;

    // Semaphore 限流（单机 500 容量足够）
    private final Semaphore rateLimiter = new Semaphore(500);

    @PostMapping("/seckill/{productId}")
    public Result seckill(@PathVariable Long productId, HttpSession session) {
        Long userId = (Long) session.getAttribute("userId");

        // 1. 限流（防瞬时 500 请求打爆 DB）
        if (!rateLimiter.tryAcquire()) {
            return Result.fail("系统繁忙，请稍后重试");
        }

        try {
            // 2. 秒杀
            boolean success = seckillService.trySeckill(userId, productId);
            return success ? Result.ok() : Result.fail("已抢完或重复抢");
        } finally {
            rateLimiter.release();
        }
    }
}
```

### 6.4 性能估算

```
500 人 / 2 台服务器 / 库存=1：
- 每台服务器 ~250 请求
- DB 写 1 次成功 + 499 次失败
- 总耗时：~500ms（乐观锁 + 唯一索引）

远超用户感知（用户可接受 1-3 秒） ✅
```

---

## 七、局限性 + 何时升级到 Redis

**单机方案局限**：

| 场景 | 单机方案 | 升级到 Redis |
|------|---------|-------------|
| < 1000 人 / 单库存 | ✅ 足够 | ❌ 过度设计 |
| < 5000 人 / 单库存 | ⚠️ DB 压力大 | ✅ Redis 分布式锁 |
| 10000+ 人 / 单库存 | ❌ 必崩 | ✅ Redis + MQ 削峰 |
| 常态化秒杀 | ❌ DB 是瓶颈 | ✅ Redis 库存预扣 + MQ 异步下单 |

**升级信号**：
- ❌ DB QPS > 1000 → 升级 Redis 缓存
- ❌ 库存频繁冲突 → 升级 Redis 分布式锁
- ❌ 用户感知延迟 > 1 秒 → 升级 MQ 削峰

**结论**：**业务规模决定方案**，500 人 / 单库存的单机方案完全够用。**不要为了用 Redis 而用 Redis**。

---

## 八、反模式（不要做的事）

| 反模式 | 后果 |
|--------|------|
| ❌ 强行上 Redis | 运维成本 +10，单机方案本来够用 |
| ❌ `UPDATE product SET stock = stock - 1` 不带 `WHERE stock > 0` | 超卖 |
| ❌ 不用 version 字段 | ABA 问题 |
| ❌ 用代码判重（if exists + insert）| TOCTOU 漏洞 |
| ❌ 把库存扣减和下单放 2 个事务 | 一致性问题 |

---

## 九、可复用 Checklist（秒杀方案自查）

- [ ] 确认问题边界：人数 / 服务器数 / 库存数 / 限制条件
- [ ] 库存=1 → 必须乐观锁 + 唯一约束
- [ ] 2 台服务器 → 共享 DB 自动解决一致性
- [ ] 500 人级别 → 单机方案够用，**不要过度设计**
- [ ] `WHERE stock > 0` 必备
- [ ] `version` 字段必备（防 ABA）
- [ ] 唯一索引必备（防重复抢）
- [ ] 限流防雪崩（Semaphore 即可）
- [ ] Controller 层 try-finally 释放许可
- [ ] 监控：库存剩余 / QPS / 超卖告警

---

## 十、相关章节

**同模块原理**：
- [限流原理（rate-limiting/README）](README.md) — 4 大算法 + 4 大策略
- [乐观锁（optimistic-lock）](../../06-idempotency/optimistic-lock/README.md) — 库存扣减基础
- [幂等性（idempotency）](../../06-idempotency/README.md) — 防重复原理

**面试题**：
- [秒杀刁难题面试 5 题](../../../13.split-hairs/04.system-design/seckill-without-redis/README.md) — 5 题配套面试

**餐厅叙事（12.story）**：
- [04 · peak-traffic-defense（餐厅流量防御）](../../../12.story/04-peak-traffic-defense.md) — 餐厅流量 = 茅台秒杀的隐喻版

**其他相关**：
- [限流算法（rate-limiting）面试题](../../../13.split-hairs/04.system-design/rate-limiting/README.md) — 互补章节
- [MySQL 行锁原理](../../../01.java/concurrency/juc-locks/README.md) — 乐观锁底层实现

---

← [返回 限流原理](../README.md)