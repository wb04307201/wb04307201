<!--
module:
  parent: system-design
  slug: system-design/state-machine
  type: article
  category: 主模块子文章
  summary: 状态机（State Machine）将业务抽象为"有限状态 + 合法转移"，**让"重复执行非法操作"自然失败**。最典型的应用是订单状态流转。
-->

# 状态机

> 状态机（State Machine）将业务抽象为"有限状态 + 合法转移"，**让"重复执行非法操作"自然失败**。最典型的应用是订单状态流转。

## 目录

- [原理](#原理)
- [适用场景](#适用场景)
- [代码实现](#代码实现)
- [进阶：Spring State Machine](#进阶spring-state-machine)
- [注意事项](#注意事项)
- [选型建议](#选型建议)
- [相关章节](#相关章节)
- [参考资料](#参考资料)

---
## 引言：反直觉代码

状态机 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 原理

### 经典订单状态机

```
                    ┌──────────┐
       创建订单     │ CREATED  │
       ─────────▶  └────┬─────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        ┌──────────┐         ┌──────────┐
        │   PAID   │         │CANCELLED │   超时 / 用户取消
        └────┬─────┘         └──────────┘
             │
   ┌─────────┴─────────┐
   │                   │
   ▼                   ▼
┌──────────┐      ┌──────────┐
│ SHIPPED  │      │ REFUNDED │   申请退款
└────┬─────┘      └──────────┘
     │
     ▼
┌──────────┐
│COMPLETED │
└──────────┘
```

幂等性体现：

- 已 PAID 的订单再次调用 `pay()` → 状态不允许，抛错
- 已 CANCELLED 的订单调用 `pay()` → 状态不允许
- 已 SHIPPED 的订单调用 `cancel()` → 状态不允许

> 关键：状态转移函数是**幂等**的——同一操作在已终止状态下调用，结果都是"非法转移"。

---

## 适用场景

- **订单 / 工单 / 审批流程**（状态多、转移复杂）
- **支付流程**（PENDING → SUCCESS / FAILED）
- **优惠券核销**（UNUSED → USED → EXPIRED）
- **任务 / Bug 跟踪**（TODO → DOING → DONE）
- **任何业务对象生命周期明确**的场景

**不适用**：

- 状态极简（≤ 2 个）的场景
- 状态转移无规律、靠人工配置的场景

---

## 代码实现

### 1. 枚举 + 转移矩阵（推荐）

```java
public enum OrderStatus {
    CREATED, PAID, SHIPPED, COMPLETED, CANCELLED, REFUNDED;

    /** 合法转移矩阵 */
    private static final Map<OrderStatus, Set<OrderStatus>> TRANSITIONS = Map.of(
        CREATED,   Set.of(PAID, CANCELLED),
        PAID,      Set.of(SHIPPED, REFUNDED),
        SHIPPED,   Set.of(COMPLETED, REFUNDED),
        COMPLETED, Set.of(REFUNDED),
        CANCELLED, Set.of(),
        REFUNDED,  Set.of()
    );

    /**
     * 是否允许转移到新状态
     * 重复调用同一操作: 新状态 == 旧状态 时返回 false
     */
    public boolean canTransitionTo(OrderStatus next) {
        return TRANSITIONS.getOrDefault(this, Set.of()).contains(next);
    }

    /**
     * 严格判断（包含同状态调用）
     */
    public boolean isSameState(OrderStatus other) {
        return this == other;
    }
}
```

```java
@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepo;

    @Transactional
    public void payOrder(Long orderId, String paymentRequestId) {
        Order order = orderRepo.findById(orderId)
                .orElseThrow(() -> new NotFoundException("订单不存在"));

        // 1. 状态校验
        if (!order.getStatus().canTransitionTo(OrderStatus.PAID)) {
            if (order.getStatus() == OrderStatus.PAID) {
                // 重复支付：返回当前结果（幂等友好）
                log.info("订单 {} 已支付, 重复请求 paymentRequestId={}",
                        orderId, paymentRequestId);
                return;
            }
            throw new IllegalStateException(
                "订单当前状态 " + order.getStatus() + " 不允许支付");
        }

        // 2. 执行支付
        paymentService.charge(order, paymentRequestId);

        // 3. 状态转移
        order.setStatus(OrderStatus.PAID);
        orderRepo.save(order);
    }
}
```

### 2. 数据库约束兜底

即使应用层有 bug 重复执行，数据库也应有约束：

```sql
CREATE TABLE orders (
    id              BIGINT PRIMARY KEY,
    status          VARCHAR(16) NOT NULL,
    status_version  INT NOT NULL DEFAULT 0,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 状态机：CREATED → PAID
UPDATE orders
SET status = 'PAID',
    status_version = status_version + 1
WHERE id = ? AND status = 'CREATED';

-- 检查影响行数
-- = 1: 成功
-- = 0: 状态已变更（被别的请求抢先 / 重复支付），按幂等处理
```

### 3. 完整流程

```
┌─────────┐         ┌──────────┐         ┌──────────┐
│ 客户端   │         │  Order    │         │   DB     │
│         │         │  Service  │         │          │
└────┬────┘         └────┬─────┘         └────┬─────┘
     │  pay(orderId)     │                    │
     │ ────────────────▶ │                    │
     │                   │  SELECT status     │
     │                   │ ──────────────────▶│
     │                   │ ◀── 'CREATED' ────│
     │                   │                    │
     │                   │ 校验: CREATED→PAID │
     │                   │ ✓ 合法             │
     │                   │                    │
     │                   │  UPDATE            │
     │                   │  WHERE status=     │
     │                   │       'CREATED'    │
     │                   │ ──────────────────▶│
     │                   │ ◀── affected=1 ────│
     │                   │                    │
     │  重复支付          │                    │
     │  pay(orderId)     │                    │
     │ ────────────────▶ │                    │
     │                   │  SELECT status     │
     │                   │ ──────────────────▶│
     │                   │ ◀── 'PAID' ────────│
     │                   │                    │
     │                   │ 校验: PAID→PAID    │
     │                   │ ✗ 非法             │
     │                   │                    │
     │ ◀── 200 OK ──────│                    │
     │   (幂等返回)       │                    │
```

---

## 进阶：Spring State Machine

对于超复杂流程（如电商大促的多阶段订单），可用 [Spring Statemachine](https://spring.io/projects/spring-statemachine)：

```java
@Configuration
@EnableStateMachine
public class OrderStateMachineConfig
        extends StateMachineConfigurerAdapter<OrderStatus, OrderEvent> {

    @Override
    public void configure(StateMachineStateConfigurer<OrderStatus, OrderEvent> states)
            throws Exception {
        states.withStates()
            .initial(CREATED)
            .states(EnumSet.allOf(OrderStatus.class))
            .end(COMPLETED)
            .end(CANCELLED)
            .end(REFUNDED);
    }

    @Override
    public void configure(StateMachineTransitionConfigurer<OrderStatus, OrderEvent> t)
            throws Exception {
        t.withExternal()
            .source(CREATED).target(PAID).event(PAY)
            .and().withExternal()
            .source(PAID).target(SHIPPED).event(SHIP)
            .and().withExternal()
            .source(SHIPPED).target(COMPLETED).event(CONFIRM_RECEIVE)
            .and().withExternal()
            .source(CREATED).target(CANCELLED).event(CANCEL)
            .and().withExternal()
            .source(PAID).target(REFUNDED).event(REFUND);
    }
}
```

---

## 注意事项

### 1. 状态转移表必须穷尽

任何状态组合都应明确"允许 / 拒绝 / 重复幂等"三选一，不要留白。

### 2. 同状态调用的处理

```java
if (order.getStatus() == OrderStatus.PAID) {
    // 决策A: 视为幂等成功（推荐用于支付/通知）
    return;
    // 决策B: 抛错
    // throw new IllegalStateException("订单已支付");
}
```

- **支付回调**：决策 A（让支付平台收到成功）
- **人工操作**：决策 B（提示已操作过）

### 3. 终态不可逆

`COMPLETED` / `CANCELLED` / `REFUNDED` 应**没有出边**，确保不会再被修改。

### 4. 状态机 ≠ 业务流程

- 状态机只管"对象当前能做什么"
- 业务流程（如"先支付后发货"）是状态机的转移条件

### 5. 持久化

- 状态应持久化到 DB（不是内存）
- 高频状态变更可考虑追加 `status_history` 表做审计

---

## 选型建议

| 场景 | 推荐 |
|------|------|
| 订单 / 支付 / 退款 | ✅ 状态机 |
| 简单布尔状态（已读 / 未读） | ❌ 普通字段即可 |
| 状态 ≥ 5 个且有复杂转移 | ✅✅ 状态机 + 转移矩阵 |
| 状态多且需要可视化配置 | Spring Statemachine / 流程引擎（Camunda） |
| 跨服务状态同步 | ⚠ 配合 Saga / 事件溯源 |

---

## 相关章节

- [Idempotency-Key 唯一标识](../idempotency-key/README.md) — 入口层幂等
- [乐观锁 / Version](../optimistic-lock/README.md) — 数值类状态变更
- [去重表](../deduplication-table/README.md) — MQ 消费场景
- [与分布式事务的关系](../vs-distributed-transaction/README.md) — 跨服务状态同步

## 参考资料

- [Martin Fowler - State Pattern](https://martinfowler.com/eaaCatalog/state.html)
- [Spring Statemachine](https://spring.io/projects/spring-statemachine)
- [Workflow Patterns](http://www.workflowpatterns.com/)
- [Coloring Book: Finite State Machines for Designers](https://github.com/isu-quartet/colloquium)
