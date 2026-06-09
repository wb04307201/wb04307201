# 幂等性 vs 分布式事务（TCC / Saga）

> 很多人会混淆"幂等"和"分布式事务"。它们**解决问题不同、互补使用**。本文厘清两者关系，并给出实战选型建议。

## 目录

- [核心区别](#核心区别)
- [什么时候用什么](#什么时候用什么)
- [三者如何协作](#三者如何协作)
- [实战案例：电商下单](#实战案例电商下单)
- [选型决策表](#选型决策表)
- [相关章节](#相关章节)
- [参考资料](#参考资料)

---

## 核心区别

| 维度 | 幂等性 | 分布式事务 |
|------|--------|------------|
| **核心问题** | 同一操作执行 N 次 vs 1 次效果相同 | 多个服务的数据**要么全成功，要么全回滚** |
| **作用范围** | 单一操作（写一行 / 一个 API） | 跨服务 / 跨数据源 |
| **典型场景** | 支付扣款、MQ 消费、HTTP 重试 | 订单创建 + 库存扣减 + 支付扣款 |
| **实现方式** | Idempotency-Key / 乐观锁 / 状态机 | TCC / Saga / 2PC / 本地消息表 |
| **CAP 取向** | AP（高可用、最终一致） | CP（强一致）或最终一致 |
| **回滚语义** | 无需回滚（重复执行无害） | 必须可回滚（Cancel / Compensate） |
| **性能** | 极低开销 | 中等到高（需协调） |
| **复杂度** | 低 | 高 |

### 一句话总结

> **幂等性**解决"重复执行无害"；
> **分布式事务**解决"多步操作要么全成功要么全失败"。

---

## 什么时候用什么

### 单独使用幂等性

✅ **适用**：

- 单一 API 入口（用户重复点击 / 客户端重试）
- MQ 消费（至少一次语义）
- 第三方回调（Webhook 多次投递）
- **单服务内的多次重复请求**

❌ **不适用**：

- 跨服务的数据一致性（需要分布式事务）

### 单独使用分布式事务

✅ **适用**：

- 多服务写操作需要原子性
- 强一致业务（资金清结算）
- **每一步本身不需要重试**（业务调用幂等）

❌ **不适用**：

- 性能极敏感场景（事务协调开销大）
- 跨外部系统（无法 TCC 模式）

### 组合使用（推荐）

> **幂等性是分布式事务的"安全网"**。

```
客户端                  服务A                  服务B
   │                      │                      │
   │  POST /order         │                      │
   │  Idempotency-Key: K1 │                      │
   │ ──────────────────▶ │                      │
   │                      │                      │
   │                      │  Try (B 幂等)         │
   │                      │ ──────────────────▶  │
   │                      │                      │
   │                      │  Confirm (B 幂等)     │
   │                      │ ──────────────────▶  │
   │                      │                      │
   │  200 OK              │                      │
   │ ◀──────────────────  │                      │
   │                      │                      │
   │  (重复)               │                      │
   │  POST /order         │                      │
   │  Idempotency-Key: K1 │                      │
   │ ──────────────────▶ │                      │
   │                      │                      │
   │                      │  (Key 命中,直接返回)  │
   │  200 OK (相同结果)    │                      │
   │ ◀──────────────────  │                      │
```

幂等性让分布式事务的 **Confirm / Cancel 阶段重试安全**；分布式事务让多服务**保持一致**。

---

## 三者如何协作

```
┌────────────────────────────────────────────────────┐
│              完整的可靠调用链                       │
├────────────────────────────────────────────────────┤
│                                                    │
│   ① 客户端携带 Idempotency-Key                    │
│                                                    │
│   ② 服务 A 入口幂等检查（DB UNIQUE 索引）          │
│                                                    │
│   ③ 服务 A 启动分布式事务（TCC / Saga）            │
│      ├─ Try 阶段（每个服务都是幂等的）             │
│      ├─ Confirm 阶段（每个服务都是幂等的）         │
│      └─ Cancel 阶段（每个服务都是幂等的）          │
│                                                    │
│   ④ 服务 A 完成，返回 200                          │
│                                                    │
│   ⑤ 客户端 / MQ 重试时：                           │
│      - 入口幂等命中 → 直接返回历史响应             │
│      - 事务内幂等 → 重复 Confirm 安全              │
│      - 消息幂等 → 重复消费跳过                     │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 实战案例：电商下单

### 业务流

```
用户下单
  │
  ├── 创建订单 (Order Service)
  ├── 扣减库存 (Inventory Service)
  ├── 扣减余额 / 创建支付单 (Pay Service)
  └── 发送通知 (Notify Service)
```

### 朴素版（无幂等无事务）的问题

```
A: 创建订单成功
B: 扣减库存失败 → 抛错给用户
但订单已创建, 库存未扣, 状态不一致
```

### 加分布式事务（TCC）

```java
// Order Service
@TCC(confirmMethod = "confirmCreate", cancelMethod = "cancelCreate")
public void createOrder(OrderDTO order) {
    // Try: 预创建订单(状态=PENDING)
    orderRepo.save(new Order(order, PENDING));
    // 调用其他服务的 Try
    inventoryTccService.tryDecrease(order);
    payTccService.tryDeduct(order);
}

public void confirmCreate(OrderDTO order) {
    // Confirm: 订单状态 → PAID
    order.setStatus(PAID);
    orderRepo.save(order);
}

public void cancelCreate(OrderDTO order) {
    // Cancel: 订单状态 → CANCELLED
    order.setStatus(CANCELLED);
    orderRepo.save(order);
}
```

### 加幂等性后

```java
@PostMapping("/orders")
public OrderResult createOrder(@RequestBody @Valid OrderRequest req,
                               @RequestHeader("Idempotency-Key") String key) {
    // ① 入口幂等：同一 Key 重复请求直接返回
    return idempotencyService.execute(key, "create-order:" + req.getUserId(),
        () -> {
            // ② 分布式事务
            return tccTemplate.execute(() -> {
                return orderTccService.createOrder(req);
            });
        });
}
```

**现在所有重试场景都安全**：

| 场景 | 之前 | 之后 |
|------|------|------|
| 客户端超时重试 | 重复下单 | 入口幂等返回原订单 |
| TCC Confirm 阶段重试 | 担心重复 confirm | Confirm 阶段业务幂等 |
| MQ 重复消费订单消息 | 重复创建 | 去重表 / 状态机拦截 |
| Cancel 阶段重试 | 担心重复 cancel | Cancel 阶段业务幂等 |

---

## 选型决策表

| 你的场景 | 推荐方案 |
|----------|----------|
| 单一接口，重复请求有害 | **幂等性**（Idempotency-Key） |
| MQ 消费者 | **去重表** + 业务幂等 |
| 状态流转 | **状态机** |
| 跨服务强一致（资金 / 库存） | **TCC / Saga** + 每步幂等 |
| 跨服务最终一致（可异步） | **本地消息表** / **事务消息** + 幂等消费 |
| 第三方回调 | **Idempotency-Key** + 状态机 |
| 高并发扣库存 | **乐观锁 / 分布式锁**（视竞争度） |

### 反模式

❌ **"我用了 TCC 就万事大忧"** —— 缺了幂等，TCC 重试阶段可能造成数据错误。

❌ **"我用了幂等就不需要事务"** —— 跨服务不一致时幂等性解决不了。

❌ **"幂等性 = 分布式事务"** —— 两者正交，可以同时使用。

❌ **"我用了 Saga 就不要幂等了"** —— Saga 子事务的补偿必须幂等，否则补偿失败会导致资金错乱。

---

## 关键设计原则

1. **每个服务都应假设自己会被重试**
2. **每个写操作都应保证幂等性**
3. **跨服务一致性另选分布式事务方案**
4. **优先用业务唯一键 + UNIQUE 约束做幂等**（不依赖 Redis / 外部状态）

---

## 相关章节

- [Idempotency-Key 唯一标识](../idempotency-key/README.md)
- [乐观锁 / Version](../optimistic-lock/README.md)
- [状态机](../state-machine/README.md)
- [去重表](../deduplication-table/README.md)
- [02 分布式 / 分布式事务](../../02-distributed/distributed-transaction/README.md)
- [02 分布式 / 共识算法](../../02-distributed/consensus-algorithms/README.md)

## 参考资料

- [Chris Richardson - Microservices Patterns: Saga](https://microservices.io/patterns/data/saga.html)
- [Seata - TCC 模式](https://seata.io/zh-cn/docs/dev/mode/tcc.html)
- [Microsoft - Idempotency patterns](https://learn.microsoft.com/azure/architecture/microservices/design/idempotency)
- [BASE: An Acid Alternative](https://queue.acm.org/detail.cfm?id=1394128)
