<!--
module:
  parent: system-design
  slug: system-design/rate-limiting/seckill-without-redis
  type: article
  category: 主模块子文章
  summary: 不用 Redis/MQ 怎么写秒杀？5 大单机方案 + 库存=1 特殊处理 + 2 台服务器一致性 + 实战模板。
  depth: ⭐⭐⭐⭐
-->

# 不用 Redis / MQ，秒杀怎么写？（5 大单机方案对比）

> 一句话定位：面试官刁难场景 —— **500 人抢 1 瓶茅台 / 2 台服务器 / 不用 Redis / MQ**。主流方案都假设有分布式组件，**强制不用**就要走单机方案。本文给出 **5 大单机方案**对比 + **库存=1 特殊处理** + **2 台服务器一致性** + **实战模板**（事务边界 + 事务外转换重复请求）。

> **同模块兄弟**：
> - [限流原理（rate-limiting/README）](README.md) — 通用限流原理（4 算法 + 4 策略）
> - [乐观锁（optimistic-lock）](../../06-idempotency/optimistic-lock/README.md) — 库存扣减基础

---

## 一、问题边界（先问清再答）

很多人一上来就答"用 Redis 分布式锁"，但**面试官问"不用 Redis"**——必须先确认边界：

```text
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
    // 为什么 permits=1？库存只有 1 件；如果库存是 N，permits 设为 N
    // 为什么用 Semaphore 而非 AtomicInteger？—— Semaphore 天然支持阻塞/非阻塞获取，AtomicInteger 需要 CAS 重试
    private final Semaphore stockSemaphore = new Semaphore(1);
    private final Set<Long> winners = ConcurrentHashMap.newKeySet();

    public boolean trySeckill(Long userId) {
        if (winners.contains(userId)) {
            return false;
        }
        // 为什么用 tryAcquire() 而非 acquire()？—— 非阻塞，抢不到立即返回 false，避免线程阻塞导致吞吐量下降
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

### 方案 4：单节点条件原子更新（DB 行锁 + 唯一约束，**生产首选**）

**原理**：用数据库**唯一索引**保证幂等，用**条件原子更新**（`stock > 0`）防止超卖 —— **2 台服务器共享同一 DB** 自动解决一致性问题。

> **注意**：这里的防超卖是**条件原子更新**（`UPDATE ... WHERE stock > 0`），不是 `version` 乐观锁。ABA 风险通过"库存单调递减 + 后续唯一约束"组合解决（详见 §4）。

```sql
CREATE TABLE seckill_order (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    UNIQUE KEY uk_user_product (user_id, product_id)  -- 唯一约束：每个用户只能抢一次
);
```

```java
@Transactional(rollbackFor = Exception.class)
public boolean trySeckill(Long userId, Long productId) {
    // 1. 条件原子扣减库存（防超卖）
    int updated = productMapper.deductStock(productId);
    if (updated == 0) {
        return false;  // 库存不足
    }

    // 2. 插入订单（靠唯一约束防重复）—— 同一事务内，整体回滚
    orderMapper.insert(new Order(userId, productId));
    return true;
}
```

```sql
-- 条件原子更新 SQL（关键）
-- 为什么是 stock > 0 而不是 version=?？因为秒杀场景的 ABA 风险（库存被扣完又回滚）由后续唯一约束兜底，
-- 单纯靠 stock>0 即可防止超卖（扣成负数）；若需严格防 ABA，可改为乐观锁（见 06-idempotency/optimistic-lock）
UPDATE product SET stock = stock - 1
WHERE id = #{productId} AND stock > 0;
```

**优点**：
- ✅ **2 台服务器共享 DB → 自动解决一致性问题**
- ✅ **唯一约束**防止用户重复抢
- ✅ **条件原子更新**防止超卖（扣成负数）
- ✅ 简单可靠（生产可用）

**缺点**：
- ❌ 高并发下 DB 压力大（5000+ 写请求）
- ❌ 需要 DB（MySQL / PostgreSQL）

**适用**：**2 台服务器 + 单 DB = 生产首选**（500 人级别足够）。

---

### 方案 5：内存队列（LinkedBlockingQueue + 单消费者，**真正串行**）

**原理**：把请求真正入队（**不直接扣库存**），**唯一消费者线程**串行取出处理，**避免并发扣减把库存扣成负数**。这是方案 5 与方案 2 的关键区别 —— 方案 2 让 500 个线程同时 CAS 自旋扣库存，方案 5 让请求排队，单线程顺序扣。

```java
public class QueueSeckill {

    /** 请求真正进入队列（核心：LinkedBlockingQueue.put 是阻塞入队）*/
    private final BlockingQueue<SeckillRequest> queue = new LinkedBlockingQueue<>(1000);

    /** 库存与中奖名单 —— 只被唯一消费者线程访问，无需加锁 */
    private final AtomicInteger stock = new AtomicInteger(1);
    private final Set<Long> winners = ConcurrentHashMap.newKeySet();

    /** 唯一消费者线程（单线程串行处理）*/
    private final Thread consumer;

    public QueueSeckill() {
        this.consumer = new Thread(this::consumeLoop, "seckill-consumer");
        this.consumer.setDaemon(true);
        this.consumer.start();
    }

    /**
     * 生产者：把请求真正塞进队列，O(1)。
     * 注意：这里不做任何业务判断（不查 winners、不扣库存），
     * 全部交给消费者串行处理，避免并发扣库存扣成负数。
     */
    public boolean trySeckill(Long userId, long timeoutMs) {
        SeckillRequest req = new SeckillRequest(userId);
        boolean offered = queue.offer(req);  // 非阻塞入队
        if (!offered) {
            return false;  // 队列满 → 拒绝（背压）
        }
        // 等消费者处理结果（这里用 CountDownLatch 简化）
        try {
            return req.getResult(timeoutMs, TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            return false;  // 超时未抢到（消费者太慢或队列堆积）
        }
    }

    /**
     * 唯一消费者线程：take() 阻塞取请求，串行处理。
     * 由于只有这一个线程访问 stock 和 winners，无需任何锁/CAS。
     */
    private void consumeLoop() {
        while (true) {
            try {
                SeckillRequest req = queue.take();  // 阻塞取，队列空则等待
                process(req);                       // 串行执行
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                // 单条请求处理失败不影响整体（已在 process 内标记 result）
            }
        }
    }

    /** 串行处理（单线程执行 → 无并发问题）*/
    private void process(SeckillRequest req) {
        try {
            if (winners.contains(req.userId)) {
                req.markResult(false);  // 重复抢
                return;
            }
            if (stock.get() <= 0) {
                req.markResult(false);  // 已抢完
                return;
            }
            stock.decrementAndGet();   // 串行环境下 get-then-set 是安全的
            winners.add(req.userId);
            req.markResult(true);
        } catch (Exception e) {
            req.markResult(false);
        }
    }

    /** 请求载体（用户ID + 结果回执）*/
    private static class SeckillRequest {
        final Long userId;
        private final CountDownLatch latch = new CountDownLatch(1);
        private volatile boolean result = false;

        SeckillRequest(Long userId) {
            this.userId = userId;
        }

        void markResult(boolean r) {
            this.result = r;
            this.latch.countDown();
        }

        boolean getResult(long timeout, TimeUnit unit) throws TimeoutException {
            if (!latch.await(timeout, unit)) {
                throw new TimeoutException();
            }
            return result;
        }
    }
}
```

**为什么这次不会扣成负数？**
```text
方案 2（AtomicInteger 自旋）：500 个线程同时 CAS 扣 stock
├─ T1 读到 stock=1 → CAS stock=0 成功
├─ T2 读到 stock=0 → CAS 失败，返回 false ✅
└─ 安全但 CAS 自旋有 CPU 空转

方案 5（本节，单消费者）：500 个请求排队进 BlockingQueue
├─ 唯一消费者线程串行 take() → process()
├─ 第 1 个请求：stock=1 → 扣成 stock=0，winners 加入 user1，返回 true
├─ 第 2~500 个请求：stock=0 → 直接返回 false
└─ 永远不会出现"两个线程同时看到 stock=1 都去扣"的情况 → 库存绝对不会扣成负数
```

**优点**：
- ✅ **真正串行处理**（请求真正入队 + 唯一消费者）→ 库存不会扣成负数
- ✅ **背压机制**（队列满则拒绝）
- ✅ 无 CAS 自旋（消费者串行处理）

**缺点**：
- ❌ **单 JVM 限制**，2 台服务器依然超卖（每台 JVM 各一个独立队列）
- ❌ 队列满会丢失请求（需监控 + 报警）
- ❌ 消费者单线程是吞吐瓶颈（高并发下需用 Disruptor 多生产者单消费者提升）

**适用**：单机 + 高吞吐 + 库存不允许超扣；**2 台服务器需要 MQ 或共享队列**（违背限制）。

---

## 三、5 方案对比表

| 方案 | 代码量 | 性能 | 2 台服务器 | 库存=1 防超卖 | 防重复抢 | 推荐度 |
|------|------:|-----:|:----------:|:-------------:|:--------:|------:|
| **synchronized** | ⭐ | ⭐⭐ | ❌ 超卖 | ⚠️ 单 JVM | ⚠️ 内存 | ⭐ |
| **AtomicInteger** | ⭐⭐ | ⭐⭐⭐ | ❌ 超卖 | ⚠️ 单 JVM | ⚠️ 内存 | ⭐⭐ |
| **Semaphore** | ⭐⭐ | ⭐⭐⭐ | ❌ 超卖 | ⚠️ 单 JVM | ⚠️ 内存 | ⭐⭐ |
| **条件原子更新 + 唯一约束** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ **生产可用** | ✅ DB 唯一 | ✅ 唯一索引 | ⭐⭐⭐⭐⭐ |
| **内存队列（单消费者）** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ 超卖 | ✅ **串行保证** | ⚠️ 内存 | ⭐⭐⭐ |

**关键洞察**：**只有方案 4（条件原子更新 + 唯一约束）能解决 2 台服务器一致性问题** —— 其他 4 个都是单 JVM 方案。

---

## 四、库存=1 的特殊处理（防超卖 / ABA / 重复扣减）

### 4.1 防超卖：条件原子更新 SQL

```sql
-- 关键：WHERE stock > 0 —— 防止扣成负数
UPDATE product
SET stock = stock - 1
WHERE id = ? AND stock > 0;
-- 影响行数 = 1 成功；= 0 失败（库存不足）
```

**反直觉点**：**光靠 `UPDATE product SET stock = stock - 1` 不够** —— 必须带 `stock > 0` 条件，否则可能扣成负数（MySQL 默认 0 也允许扣，扣成 -1 / -2 都不报错）。

### 4.2 关于 ABA 问题：秒杀场景的边界澄清

```text
标准 ABA 场景（version 乐观锁）：
T1: A 读 stock=1, version=1
T2: B 抢到 → stock=0, version=2
T3: 退货 → stock=1（ABA：A 看到的和现在一样）
T4: A 用 version=1 提交 → 失败（version 不匹配）✅

秒杀场景的实际情况：
- 库存只减不增（不会"退货补库存"）
- 即使真的"扣减又回滚"，库存依然是单调递减
- 唯一约束兜底：重复 user+product 的订单会被 MySQL 拒绝
```

**结论**：**秒杀场景下 `WHERE stock > 0` 的条件原子更新足够**，ABA 风险通过业务特性（库存只减不增）+ 后续唯一约束组合消除。**不需要在 deductStock 中校验 version 字段**。

> 如果你的业务是**通用库存系统**（需要"扣减 / 回滚 / 退货补库存"等完整生命周期），请改用 [乐观锁](../../06-idempotency/optimistic-lock/README.md) 的 `version` 方案。

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

**插入冲突 → DuplicateKeyException → 整个事务回滚**（库存扣减也撤销）。

**反直觉点**：**靠代码判重（`if (exists)` + `insert`）有 TOCTOU 问题**，**靠唯一索引 100% 防重**。

---

## 五、2 台服务器的一致性（共享 DB 方案）

### 5.1 主从读写分离

```text
写流量：服务器 A + 服务器 B → 写主 DB
读流量：服务器 A + 服务器 B → 读从 DB（最终一致）

秒杀场景：
├─ 库存扣减必须读主（避免主从延迟导致超卖）
└─ 订单查询可以读从（容忍 1 秒延迟）
```

### 5.2 同步方案（避免主从延迟）

```text
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

```text
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
-- 商品表
CREATE TABLE product (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    stock INT NOT NULL DEFAULT 0
);

-- 订单表（带唯一约束）
CREATE TABLE seckill_order (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    order_no VARCHAR(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_product (user_id, product_id),
    UNIQUE KEY uk_order_no (order_no)
);

-- 初始化库存
INSERT INTO product (id, name, stock) VALUES (1, '茅台', 1);
```

### 6.2 SeckillService（核心：事务边界 + 事务外转换重复请求）

> **关键设计**：**库存扣减 + 订单插入必须在同一事务内**，事务提交后才能对外宣称"秒杀成功"。**DuplicateKeyException 必须在事务外捕获** —— 事务内捕获会导致手工补库存（虚增风险）。

```java
@Service
public class SeckillService {

    @Autowired
    private ProductMapper productMapper;

    @Autowired
    private OrderMapper orderMapper;

    /**
     * 入口：事务外捕获重复请求异常，返回"已存在订单ID"
     */
    public SeckillResult trySeckill(Long userId, Long productId) {
        try {
            return doSeckillInTx(userId, productId);  // 内部事务
        } catch (DuplicateKeyException e) {
            // 事务外捕获：唯一约束触发 → 该用户已抢过
            // 不补库存！让数据库事务自己回滚（已经回滚了）
            Order existing = orderMapper.findByUserAndProduct(userId, productId);
            return SeckillResult.duplicate(existing != null ? existing.getId() : null);
        }
    }

    /**
     * 内部事务：库存扣减 + 订单插入 在同一事务内
     */
    @Transactional(rollbackFor = Exception.class)
    public SeckillResult doSeckillInTx(Long userId, Long productId) {
        // 1. 条件原子扣减库存（防超卖）
        int rows = productMapper.deductStock(productId);
        if (rows == 0) {
            return SeckillResult.outOfStock();  // 库存不足
        }

        // 2. 插入订单（靠唯一约束防重复抢）
        //    重复插入会抛 DuplicateKeyException → 整个事务回滚 → 库存扣减撤销
        Order order = new Order();
        order.setUserId(userId);
        order.setProductId(productId);
        order.setOrderNo(generateOrderNo());
        orderMapper.insert(order);
        return SeckillResult.success(order.getId());
    }
}

@Mapper
public interface ProductMapper {
    // 条件原子更新（防超卖）：不是 version 乐观锁，单纯 stock > 0 条件即可
    @Update("UPDATE product SET stock = stock - 1 " +
            "WHERE id = #{productId} AND stock > 0")
    int deductStock(Long productId);
}

@Mapper
public interface OrderMapper {
    @Insert("INSERT INTO seckill_order(user_id, product_id, order_no) " +
            "VALUES(#{userId}, #{productId}, #{orderNo})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    void insert(Order order);

    @Select("SELECT * FROM seckill_order WHERE user_id = #{userId} " +
            "AND product_id = #{productId} LIMIT 1")
    Order findByUserAndProduct(@Param("userId") Long userId,
                                @Param("productId") Long productId);
}
```

### 6.3 A3 反例 vs 正例：DuplicateKeyException 的处理位置

**❌ 反例：事务内 catch DuplicateKeyException → 手工补库存（库存虚增风险）**

```java
@Transactional(rollbackFor = Exception.class)
public boolean trySeckill_WRONG(Long userId, Long productId) {
    int rows = productMapper.deductStock(productId);
    if (rows == 0) return false;

    try {
        orderMapper.insert(new Order(userId, productId));
        return true;
    } catch (DuplicateKeyException e) {
        // ❌ 错点 1：事务内捕获异常 → 框架不知道发生了异常
        // ❌ 错点 2：手工补库存 → 与原本已扣减的库存抵消，看似 OK
        // ❌ 错点 3：如果 addStock 失败（DB 抖动），库存永久虚减
        productMapper.addStock(productId, 1);
        return false;
    }
}
```

**为什么错？**

```text
风险链路：
1. 用户 A 抢到 → deductStock 扣 1 → stock=0
2. 用户 A 重复抢 → insert 抛 DuplicateKeyException
3. catch 住 → addStock 加 1 → stock=1（看似恢复）
4. 但如果第 3 步 addStock 失败（DB 抖动 / 网络超时） → stock 永远停在 0
5. 即使第 3 步成功，addStock 也是脏写 —— 在事务回滚的语义里，"补回去"是手动补偿而不是原子回滚

更隐蔽的并发问题：
- 假设用户 A 抢到（stock 1→0）
- 用户 A 重复抢 → catch → addStock 1（stock 0→1）
- 此时用户 B 刚好挤进来 → 看到 stock=1 → 抢到（stock 1→0）
- 用户 A 的 addStock（库存虚增）已被用户 B 消费 → 最终用户 A 和 B 都"成功" → 超卖
```

**✅ 正例：让 MySQL 整体回滚 + 事务外根据主键查询已存在订单**

```java
// 事务外：捕获 DuplicateKeyException → 查已存在订单 → 返回该订单ID
public SeckillResult trySeckill_RIGHT(Long userId, Long productId) {
    try {
        return doSeckillInTx(userId, productId);  // 内部 @Transactional
    } catch (DuplicateKeyException e) {
        // ✅ 正确 1：让数据库事务整体回滚（库存扣减自动撤销）
        // ✅ 正确 2：事务外根据唯一键查询已存在订单 → 返回同一订单ID
        // ✅ 正确 3：幂等语义 —— 用户重复抢，返回同一个订单，不扣第二次库存
        Order existing = orderMapper.findByUserAndProduct(userId, productId);
        return SeckillResult.duplicate(existing != null ? existing.getId() : null);
    }
}
```

**为什么对？**

```text
正确链路：
1. 用户 A 抢到 → deductStock 扣 1（stock=0）→ insert order → 事务提交 ✅
2. 用户 A 重复抢 → deductStock 扣 1（stock=0，WHERE stock>0 失败，rows=0）
   等等 —— 如果 stock>0 失败，应该早就 return false 了
3. 真实并发场景：用户 A 和 B 同时抢（都在 stock=1 时进来）
   ├─ A 先抢到 → deductStock(stock=0) → insert 成功 → 事务提交
   └─ B 后到 → deductStock(stock=0, rows=0) → 直接返回 outOfStock
4. 真正的 DuplicateKeyException 触发场景：A 已经成功一次，再次重试
   ├─ A 第二次进 → deductStock(stock=0, rows=0) → 直接返回 outOfStock
   └─ 不应该走到 insert 才对！

那 DuplicateKeyException 什么时候触发？
- 答：竞争窗口极小 —— A 已经过 deductStock（stock=0）→ insert 还没提交 → B 抢到时间片也过 deductStock（rows=0）→ return
- 实际触发 DuplicateKeyException 的典型场景：A 用客户端重试（deductStock 还没提交时重试又来一次）→ 两次都过 deductStock（都看到 stock=1）→ 一个 insert 成功，一个 insert 失败
- 此时事务回滚（库存扣减撤销）→ 事务外捕获 → 返回已存在订单 ✅
```

### 6.4 Controller 层（加限流防雪崩）

```java
@RestController
public class SeckillController {
    @Autowired
    private SeckillService seckillService;

    // 为什么 500？按 QPS 峰值 × 平均响应时间（秒）估算；如 1000 QPS × 0.5s = 500 并发许可
    // 为什么 Semaphore 而非 Guava RateLimiter？—— Semaphore 控制并发数，RateLimiter 控制速率，秒杀场景并发控制更关键
    private final Semaphore rateLimiter = new Semaphore(500);

    @PostMapping("/seckill/{productId}")
    public Result seckill(@PathVariable Long productId, HttpSession session) {
        Long userId = (Long) session.getAttribute("userId");

        // 1. 限流（防瞬时 500 请求打爆 DB）
        if (!rateLimiter.tryAcquire()) {
            return Result.fail("系统繁忙，请稍后重试");
        }

        try {
            // 2. 秒杀（事务外捕获重复请求）
            SeckillResult result = seckillService.trySeckill(userId, productId);
            switch (result.getStatus()) {
                case SUCCESS:      return Result.ok(result.getOrderId());
                case DUPLICATE:    return Result.ok(result.getOrderId());  // 幂等返回同一订单
                case OUT_OF_STOCK: return Result.fail("已抢完");
                default:           return Result.fail("系统异常");
            }
        } finally {
            rateLimiter.release();
        }
    }
}
```

### 6.5 性能估算

```text
500 人 / 2 台服务器 / 库存=1：
- 每台服务器 ~250 请求
- DB 写 1 次成功 + 499 次失败
- 总耗时：~500ms（条件原子更新 + 唯一索引）

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
| ❌ `UPDATE product SET stock = stock - 1` 不带 `WHERE stock > 0` | 超卖（扣成负数） |
| ❌ 事务内 catch DuplicateKeyException 后手工 addStock | 库存虚增 + 超卖（详见 §6.3） |
| ❌ 用 version 乐观锁处理秒杀 | 过度设计 —— 秒杀库存只减不增，stock>0 已足够 |
| ❌ 用代码判重（if exists + insert）| TOCTOU 漏洞 |
| ❌ 把库存扣减和下单放 2 个事务 | 一致性问题 |
| ❌ 方案 5 让消费者多线程并发扣库存 | 库存扣成负数（必须唯一消费者串行） |

---

## 九、可复用 Checklist（秒杀方案自查）

- [ ] 确认问题边界：人数 / 服务器数 / 库存数 / 限制条件
- [ ] 库存=1 → 必须条件原子更新 + 唯一约束
- [ ] 2 台服务器 → 共享 DB 自动解决一致性
- [ ] 500 人级别 → 单机方案够用，**不要过度设计**
- [ ] `WHERE stock > 0` 必备（防扣成负数）
- [ ] 唯一索引必备（防重复抢）
- [ ] **事务边界**：库存扣减 + 订单插入 同一事务
- [ ] **异常处理**：DuplicateKeyException 在事务外捕获 → 查询已存在订单返回
- [ ] 限流防雪崩（Semaphore 即可）
- [ ] Controller 层 try-finally 释放许可
- [ ] 监控：库存剩余 / QPS / 超卖告警

---

## 十、相关章节

**同模块原理**：
- [限流原理（rate-limiting/README）](README.md) — 4 大算法 + 4 大策略
- [乐观锁（optimistic-lock）](../../06-idempotency/optimistic-lock/README.md) — 通用库存系统的 version 方案
- [幂等性（idempotency）](../../06-idempotency/README.md) — 防重复原理

**面试题**：
- [秒杀刁难题面试 5 题](../../../12.interview/04.system-design/seckill-without-redis/README.md) — 5 题配套面试

**餐厅叙事（13.story）**：
- [04 · peak-traffic-defense（餐厅流量防御）](../../../13.story/04-peak-traffic-defense.md) — 餐厅流量 = 茅台秒杀的隐喻版；本节"限流 + 单机扣库存"的 5 大方案正是阿明餐厅遇到的高峰防御故事原型。

**其他相关**：
- 限流算法（rate-limiting）面试题 — 互补章节
- [MySQL 行锁原理](../../../01.java-and-jvm/03-concurrency/juc-locks/README.md) — 乐观锁底层实现

---

← [返回 限流原理](README.md)
