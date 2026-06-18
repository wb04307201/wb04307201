# 幂等性设计 6 大方案深度剖析

> 一句话：同一操作无论执行多少次，最终系统状态与执行一次完全一致。

---

## 一、核心原理

**幂等性（Idempotency）** 源于数学 `f(f(x)) = f(x)`，在分布式系统中表示：**同一个请求被重复处理多次，其产生的副作用与只处理一次完全相同**。

### 为什么需要幂等？

| 场景 | 说明 |
|------|------|
| 网络重试 | RPC/HTTP 超时后客户端自动重试，服务端可能已处理但响应丢失 |
| MQ 重复投递 | At-Least-Once 语义下消费者可能收到重复消息 |
| 用户重复点击 | 前端防抖失效或用户快速连击提交按钮 |
| 定时任务重跑 | 故障转移时可能触发重复执行 |
| 支付回调 | 第三方平台因网络波动重复发送回调通知 |

**没有幂等保障**会导致：重复扣款、重复下单、数据重复插入、库存多扣等问题。

---

## 二、6 大方案

### 方案一：唯一索引（Unique Index）

利用数据库 UNIQUE 约束防止重复插入，最底层最可靠的幂等机制。

```sql
ALTER TABLE orders ADD UNIQUE INDEX uk_order_no (order_no);

-- INSERT + ON DUPLICATE KEY UPDATE（MySQL）
INSERT INTO orders (order_no, user_id, amount, status)
VALUES ('ORD20260618001', 1001, 99.00, 'CREATED')
ON DUPLICATE KEY UPDATE amount = VALUES(amount), status = VALUES(status);
```

**适用**：订单创建、用户注册、优惠券领取。**优点**：数据库层面强制保证。**缺点**：仅适用于插入场景；高并发下冲突影响性能。

---

### 方案二：Token 机制（令牌机制）

服务端生成一次性 Token，客户端提交时携带，服务端验证后立即销毁。

```java
// 1. 客户端先获取 Token
@GetMapping("/token")
public String generateToken() {
    String token = UUID.randomUUID().toString().replace("-", "");
    redisTemplate.opsForValue().set("idempotent:token:" + token, "1", 5, TimeUnit.MINUTES);
    return token;
}

// 2. 客户端提交时携带 Token
@PostMapping("/order")
public Result createOrder(@RequestHeader("X-Idempotent-Token") String token, @RequestBody OrderRequest req) {
    Boolean exists = redisTemplate.delete("idempotent:token:" + token);
    if (Boolean.FALSE.equals(exists)) {
        throw new BusinessException("重复提交或 Token 已过期");
    }
    orderService.create(req);
    return Result.success();
}
```

**适用**：表单提交、API 防重放。**优点**：精确识别重复请求。**缺点**：需客户端配合；Redis 故障需降级。

---

### 方案三：状态机（State Machine）

通过 CAS 方式更新状态，只有当前状态符合预期时才允许流转。

```java
@Update("UPDATE orders SET status = #{newStatus}, pay_time = NOW() " +
        "WHERE id = #{orderId} AND status = #{expectedStatus}")
int updateOrderStatus(@Param("orderId") Long orderId,
                      @Param("newStatus") String newStatus,
                      @Param("expectedStatus") String expectedStatus);

// 业务层调用
int affected = orderMapper.updateOrderStatus(orderId, "PAID", "CREATED");
if (affected == 0) {
    log.warn("订单{}状态不是CREATED，拒绝重复处理", orderId);
    return; // 幂等返回
}
```

**适用**：订单状态流转、审批流程。**优点**：天然支持幂等；状态可追溯。**缺点**：需设计完整状态机。

---

### 方案四：乐观锁（Version / CAS）

通过版本号实现 CAS 更新，检测并发冲突。

```sql
ALTER TABLE inventory ADD COLUMN version INT DEFAULT 0;

UPDATE inventory
SET stock = stock - 1, version = version + 1
WHERE product_id = 1001 AND stock > 0 AND version = #{expectedVersion};
```

```java
Inventory inv = inventoryMapper.selectById(productId);
int affected = inventoryMapper.deductStock(productId, inv.getVersion());
if (affected == 0) {
    throw new OptimisticLockException("库存版本冲突，请重试");
}
```

**适用**：库存扣减、账户余额更新。**优点**：无锁设计性能好。**缺点**：高并发下失败率高；存在 ABA 问题风险。

---

### 方案五：分布式锁（Distributed Lock）

使用 Redis SETNX 实现互斥锁，确保同一时刻只有一个请求在处理。

```java
public void processWithLock(String bizKey, Runnable task) {
    String lockKey = "lock:idempotent:" + bizKey;
    String requestId = UUID.randomUUID().toString();
    
    Boolean acquired = redisTemplate.opsForValue()
            .setIfAbsent(lockKey, requestId, 10, TimeUnit.SECONDS);
    
    if (Boolean.TRUE.equals(acquired)) {
        try {
            if (isAlreadyProcessed(bizKey)) return; // 双重检查
            task.run();
            markAsProcessed(bizKey);
        } finally {
            String script = "if redis.call('get', KEYS[1]) == ARGV[1] then " +
                           "return redis.call('del', KEYS[1]) else return 0 end";
            redisTemplate.execute(new DefaultRedisScript<>(script, Long.class),
                    Collections.singletonList(lockKey), requestId);
        }
    } else {
        throw new BusinessException("请求处理中，请勿重复提交");
    }
}
```

**适用**：秒杀活动、热点数据更新。**优点**：彻底避免并发冲突。**缺点**：依赖外部存储；性能开销大；需处理锁超时边界。

---

### 方案六：数据库约束（幂等记录表）

建立独立的幂等记录表，通过唯一约束 + 事务保证幂等。

```sql
CREATE TABLE idempotent_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    biz_type VARCHAR(32) NOT NULL COMMENT '业务类型: order/pay/refund',
    biz_id VARCHAR(64) NOT NULL COMMENT '业务唯一标识',
    request_hash CHAR(64) COMMENT '请求内容哈希',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_biz (biz_type, biz_id)
);
```

```java
@Transactional
public void executeWithIdempotentRecord(String bizType, String bizId, Runnable task) {
    IdempotentRecord record = new IdempotentRecord();
    record.setBizType(bizType);
    record.setBizId(bizId);
    
    int inserted = idempotentRecordMapper.insertIgnore(record);
    if (inserted == 0) {
        log.info("请求{}:{}已存在，跳过执行", bizType, bizId);
        return;
    }
    task.run(); // 与幂等记录在同一事务中
}
```

**适用**：跨服务幂等、MQ 消费幂等、支付回调。**优点**：业务解耦；可追溯历史。**缺点**：需额外建表；需定期清理数据。

---

## 三、方案对比表格

| 维度 | 唯一索引 | Token 机制 | 状态机 | 乐观锁 | 分布式锁 | 数据库约束 |
|------|---------|-----------|--------|--------|---------|-----------|
| **实现复杂度** | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **可靠性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **是否需要客户端配合** | 否 | 是 | 否 | 否 | 否 | 否 |
| **典型应用场景** | 订单创建 | 表单提交 | 状态流转 | 库存扣减 | 秒杀/热点 | MQ消费/回调 |

---

## 四、实战场景

### 场景一：支付回调幂等

```java
@PostMapping("/pay/callback/wechat")
public String wechatCallback(@RequestBody WxPayNotify notify) {
    String outTradeNo = notify.getOutTradeNo();
    
    // 先查状态，已处理则直接返回成功
    PaymentRecord record = paymentMapper.selectByOutTradeNo(outTradeNo);
    if (record != null && "PAID".equals(record.getStatus())) {
        return "<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>";
    }
    
    // 分布式锁 + 双重检查
    String lockKey = "lock:pay:callback:" + outTradeNo;
    return redisLock.execute(lockKey, () -> {
        record = paymentMapper.selectByOutTradeNo(outTradeNo);
        if (record != null && "PAID".equals(record.getStatus())) {
            return "<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>";
        }
        paymentService.handleSuccess(notify);
        return "<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>";
    });
}
```

**要点**：先查状态快速返回；分布式锁防并发；签名验证必须在业务处理前。

---

### 场景二：MQ 消费幂等

```java
@Component
public class OrderMessageConsumer {
    @RabbitListener(queues = "order.created")
    public void consume(OrderCreatedEvent event, Channel channel, Message message) {
        String messageId = message.getMessageProperties().getMessageId();
        try {
            transactionTemplate.execute(status -> {
                if (messageLogMapper.existsByMessageId(messageId)) return null;
                messageLogMapper.insert(new MessageLog(messageId, "order.created"));
                orderService.processOrderCreated(event);
                return null;
            });
            channel.basicAck(message.getMessageProperties().getDeliveryTag(), false);
        } catch (Exception e) {
            channel.basicNack(message.getMessageProperties().getDeliveryTag(), false, true);
        }
    }
}
```

**要点**：消息ID作为幂等键；幂等记录与业务操作同事务；失败时 NACK 触发重试。

---

### 场景三：接口重试幂等

```java
@PostMapping("/register")
public Result register(@Valid @RequestBody UserRegisterRequest req,
                      @RequestHeader(value = "X-Request-Id", required = false) String requestId) {
    if (StringUtils.isBlank(requestId)) {
        throw new IllegalArgumentException("缺少 X-Request-Id 请求头");
    }
    
    String key = "idempotent:request:" + requestId;
    Boolean isFirst = redisTemplate.opsForValue().setIfAbsent(key, "1", 24, TimeUnit.HOURS);
    
    if (Boolean.FALSE.equals(isFirst)) {
        Object cachedResult = redisTemplate.opsForValue().get("idempotent:result:" + requestId);
        if (cachedResult != null) {
            return (Result) JsonUtils.fromJson((String) cachedResult, Result.class);
        }
        return Result.error("请求正在处理中");
    }
    
    try {
        Result result = userService.register(req);
        redisTemplate.opsForValue().set("idempotent:result:" + requestId,
                JsonUtils.toJson(result), 24, TimeUnit.HOURS);
        return result;
    } catch (Exception e) {
        redisTemplate.delete(key); // 异常时删除 Token，允许重试
        throw e;
    }
}
```

**要点**：客户端生成全局唯一 Request-Id；服务端缓存首次响应；异常时清理幂等标记。

---

## 五、常见陷阱

### 陷阱一：Token 过期时间设置不当

过短导致正常重试被拒绝；过长导致 Redis 内存膨胀。**最佳实践**：API 接口 5-10 分钟，异步任务 24 小时。

### 陷阱二：乐观锁 ABA 问题

线程 B 将 version 从 1→2→1，线程 A 误判未修改。**解决**：使用数据库自增 version；或用时间戳替代版本号。

### 陷阱三：分布式锁超时导致重复执行

锁持有者执行时间超过超时时间，锁被释放。**解决**：设置合理超时时间（大于 P99 执行时长）；实现 Watchdog 自动续期；业务层增加二次幂等校验。

### 陷阱四：唯一索引高并发性能下降

大量重复请求导致频繁抛出 Duplicate Key 异常。**解决**：前置 Redis 预检；使用 `INSERT IGNORE` 避免异常；限流保护。

### 陷阱五：混合方案中的顺序错误

**正确顺序**：1. 快速路径：查询幂等记录/状态，已处理则直接返回；2. 慢速路径：获取锁 → 双重检查 → 执行业务 → 释放锁。

---

## 六、面试话术（30 秒版）

> "幂等性是指同一操作执行多次与执行一次的效果完全相同。在分布式系统中，由于网络重试、MQ 重复投递、用户重复点击等原因，必须保证接口幂等。
>
> 常见的 6 大方案包括：**唯一索引**利用数据库约束防止重复插入，可靠性最高；**Token 机制**通过一次性令牌精确识别重复请求；**状态机**通过 CAS 更新状态，天然支持幂等；**乐观锁**用版本号检测并发冲突，适合读多写少；**分布式锁**实现强互斥，适用于秒杀等热点场景；**数据库约束**通过独立幂等记录表实现跨服务幂等。
>
> 实际项目中我会组合使用，比如支付回调采用'状态机 + 分布式锁'，MQ 消费采用'幂等记录表 + 事务'，这样既保证可靠性又兼顾性能。"

---

## 七、交叉引用

- 主模块：[`04.system-design`](../../../04.system-design/) — 系统设计知识体系
- [分布式锁](../../../04.system-design/02-distributed/distributed-lock/README.md) — 分布式锁实现详解
