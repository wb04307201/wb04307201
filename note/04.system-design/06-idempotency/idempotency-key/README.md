<!--
module:
  parent: system-design
  slug: system-design/idempotency-key
  type: article
  category: 主模块子文章
  summary: Idempotency-Key 是**最通用**的幂等性方案：客户端为每个请求生成一个唯一 Key，服务端用这个 Key 去重。即使客户端重试 10 次，服务端...
-->

# Idempotency-Key 唯一标识

> Idempotency-Key 是**最通用**的幂等性方案：客户端为每个请求生成一个唯一 Key，服务端用这个 Key 去重。即使客户端重试 10 次，服务端也只处理一次。

## 目录

- [原理](#原理)
- [适用场景](#适用场景)
- [代码实现（Java + Redis）](#代码实现java--redis)
- [数据库唯一索引（双保险）](#数据库唯一索引双保险)
- [HTTP 协议约定](#http-协议约定)
- [注意事项](#注意事项)
- [选型建议](#选型建议)
- [相关章节](#相关章节)
- [参考资料](#参考资料)

---
---

## 原理

```
Client                              Server
  │                                    │
  │  POST /payments                    │
  │  Idempotency-Key: pay-20250609-001 │
  │ ─────────────────────────────────▶ │
  │                                    │
  │                  ┌──────────────────┤
  │                  │ 1. 查 Redis       │
  │                  │    KEY: pay-001?  │
  │                  │    → 命中？直接返回│
  │                  └──────────────────┤
  │                                    │
  │                  ┌──────────────────┤
  │                  │ 2. SETNX 锁定     │
  │                  │    状态:PROCESSING│
  │                  │    TTL: 60s       │
  │                  └──────────────────┤
  │                                    │
  │                  ┌──────────────────┤
  │                  │ 3. 执行业务       │
  │                  │    扣款 + 写 DB   │
  │                  └──────────────────┤
  │                                    │
  │                  ┌──────────────────┤
  │                  │ 4. 缓存结果       │
  │                  │    状态:SUCCESS   │
  │                  │    TTL: 24h       │
  │                  └──────────────────┤
  │                                    │
  │  200 OK { paymentId: "P001" }      │
  │ ◀───────────────────────────────── │
  │                                    │
  │  (客户端超时，重试)                  │
  │  POST /payments                    │
  │  Idempotency-Key: pay-20250609-001 │
  │ ─────────────────────────────────▶ │
  │                                    │
  │                  1. 查 Redis 命中   │
  │                  2. 直接返回缓存结果 │
  │                                    │
  │  200 OK { paymentId: "P001" }      │
  │ ◀───────────────────────────────── │
```

### 状态机

```
                  ┌─────────────┐
                  │   (新 Key)   │
                  └──────┬──────┘
                         │ 首次请求
                         ▼
                  ┌─────────────┐
       重复请求  ◀│ PROCESSING  │  业务执行中
        (返回 409) └──────┬──────┘
                         │ 业务完成
                         ▼
                  ┌─────────────┐
                  │   SUCCESS   │  重复请求直接返回结果
                  └─────────────┘
```

---

## 适用场景

- **写 API**（POST 创建订单、支付、注册）
- 任何**客户端可生成唯一标识**的场景
- **移动端弱网**重试
- 任何**第三方回调**（支付回调、Webhook）

**不适用**：

- 查询（GET）—— HTTP 本身幂等
- 客户端无法携带 Key 的旧系统

---

## 代码实现（Java + Redis）

```java
@Service
public class IdempotencyService {

    @Autowired
    private StringRedisTemplate redis;

    @Autowired
    private PaymentRepository paymentRepo;

    private static final Duration LOCK_TTL = Duration.ofSeconds(60);
    private static final Duration RESULT_TTL = Duration.ofHours(24);

    /**
     * 处理幂等请求
     * @param key    客户端提供的 Idempotency-Key
     * @param bizKey 业务键（如 userId+orderId，用于防不同业务复用同 key）
     * @param action 业务逻辑
     */
    public <T> T execute(String key, String bizKey,
                         Supplier<T> action) {
        String cacheKey = "idem:" + bizKey + ":" + key;

        // 1. 查缓存：已 SUCCESS 直接返回
        String cached = redis.opsForValue().get(cacheKey + ":result");
        if (cached != null) {
            return deserialize(cached);
        }

        // 2. SETNX 抢锁（带 fingerprint 防误用）
        String fingerprint = hash(bizKey);
        Boolean acquired = redis.opsForValue()
                .setIfAbsent(cacheKey + ":lock", fingerprint, LOCK_TTL);
        if (!Boolean.TRUE.equals(acquired)) {
            // 已被其他请求占用
            throw new IdempotencyInProgressException("请求正在处理中");
        }

        try {
            // 3. 执行业务
            T result = action.get();

            // 4. 缓存结果
            redis.opsForValue().set(
                cacheKey + ":result",
                serialize(result),
                RESULT_TTL
            );
            return result;
        } catch (RuntimeException e) {
            // 业务失败：释放锁，让重试有机会再试
            redis.delete(cacheKey + ":lock");
            throw e;
        }
    }
}
```

### 关键设计点

1. **PROCESSING 状态 + 短 TTL**：
   - 防止客户端疯狂重试打爆业务
   - 短 TTL（如 60s）后即便业务挂掉，锁也会释放
2. **RESULT 状态 + 长 TTL**：
   - 让重复请求直接走缓存
   - TTL 至少覆盖业务对账窗口
3. **fingerprint 校验**：
   - 防止 A 用户的 key 被 B 误用
   - 校验 `(bizKey + path) hash` 一致才返回缓存

---

## 数据库唯一索引（双保险）

Redis 可能在以下场景失效：

- Redis 不可用 → fail-open
- TTL 过期 → 旧记录消失

**数据库唯一约束**是最后一道防线：

```sql
CREATE TABLE payment_records (
    id                   BIGINT PRIMARY KEY,
    payment_request_id   VARCHAR(64)  NOT NULL,
    order_id             VARCHAR(32)  NOT NULL,
    operation_type       VARCHAR(16)  NOT NULL DEFAULT 'PAY',
    amount               DECIMAL(10,2),
    status               ENUM('PENDING','SUCCESS','FAILED') NOT NULL DEFAULT 'PENDING',
    created_at           TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_payment_request (payment_request_id),
    INDEX idx_order (order_id)
);
```

```java
@Transactional
public PaymentResult createPayment(String paymentRequestId, PayRequest req) {
    // 1. 先查
    Optional<Payment> existing = paymentRepo.findByPaymentRequestId(paymentRequestId);
    if (existing.isPresent()) {
        return PaymentResult.from(existing.get());   // 直接返回已有结果
    }

    // 2. 插入（依赖 UNIQUE 约束兜底）
    try {
        Payment p = new Payment();
        p.setPaymentRequestId(paymentRequestId);
        p.setOrderId(req.getOrderId());
        p.setAmount(req.getAmount());
        p.setStatus(PaymentStatus.PENDING);
        paymentRepo.insert(p);

        // 3. 调外部支付通道
        ChannelResult res = channel.charge(req);

        // 4. 更新状态
        p.setStatus(res.isSuccess() ? SUCCESS : FAILED);
        paymentRepo.update(p);
        return PaymentResult.from(p);
    } catch (DuplicateKeyException e) {
        // 并发场景下另一个请求先插入成功
        return paymentRepo.findByPaymentRequestId(paymentRequestId)
                .map(PaymentResult::from)
                .orElseThrow();
    }
}
```

---

## HTTP 协议约定

参考 Stripe 和 IETF 草案：

```http
POST /v1/payments HTTP/1.1
Host: api.example.com
Idempotency-Key: pay-20250609-abc123
Content-Type: application/json

{ "amount": 1000, "currency": "CNY" }
```

服务端响应：

| 场景 | HTTP Code | 含义 |
|------|-----------|------|
| 首次处理中 | 200/201 | 正常响应 |
| 重复请求（命中缓存） | 200/201 | 返回**相同**的响应体（与首次一致） |
| 重复请求（处理中） | 409 Conflict | 提示"请求正在处理" |
| Key 与上次不同业务不匹配 | 422 | Idempotency-Key 冲突 |
| Key 缺失 | 400 | 要求必须传 Key |

---

## 注意事项

1. **Key 命名规范**：
   - 客户端生成 UUID / 业务前缀 + 时间戳
   - 避免使用订单号等业务字段（防碰撞）
   - 推荐 `pay-{userId}-{timestamp}-{rand}` 格式

2. **结果一致性**：
   - 重复请求必须返回**字节级相同**的响应
   - 不要在响应里加 "requestTime" 等动态字段
   - 重要：响应 Header 也应一致（如 `Idempotency-Replayed: true` 可选）

3. **请求体变化**：
   - 同 Key + 不同 body → 应返回 422（防止客户端 bug 静默使用旧结果）
   - 实现：用 SHA256(body) 作为 fingerprint

4. **过期时间**：
   - 至少保留 24h（覆盖常见对账窗口）
   - Stripe 保留 24h

5. **不要用于所有接口**：
   - 真正的只读查询不需要
   - 真正幂等的操作（如 PUT 替换资源）也不需要

---

## 选型建议

| 场景 | 推荐 |
|------|------|
| 支付 / 转账 / 充值 | ✅ 必选 |
| 创建订单 / 提交表单 | ✅ 推荐 |
| 第三方回调（Webhook） | ✅ 推荐 |
| 状态修改类 | ✅ 推荐 |
| 删除操作 | ⚠ 可选（DELETE 本身幂等，但若涉及多步操作仍需） |
| 批量操作 | ✅ 每条记录单独 Key |

---

## 相关章节

- [乐观锁 / Version](../optimistic-lock/README.md) — 并发更新场景
- [状态机](../state-machine/README.md) — 订单状态流转
- [去重表](../deduplication-table/README.md) — MQ 消费场景
- [与分布式事务的关系](../vs-distributed-transaction/README.md) — 何时用幂等 vs TCC / Saga
- [02 分布式 / 分布式锁](../../02-distributed/distributed-lock/README.md) — SETNX 分布式锁原理

## 参考资料

- [Stripe API - Idempotent Requests](https://stripe.com/docs/api/idempotent_requests)
- [IETF Draft - The Idempotency-Key HTTP Header Field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
- [Brandur Leach - Idempotency Keys](https://brandur.org/idempotency-keys)
- [PayPal API - Idempotency](https://developer.paypal.com/api/rest/reference/idempotency/)
