# 编程式事务（TransactionTemplate）

> 最后更新: 2026-06-14
> ⬅️ [返回事务总览](README.md) | [传播行为与隔离级别](propagation-and-isolation.md)

`@Transactional` 覆盖 90% 业务场景，但在**复杂回滚逻辑、批量处理、动态事务边界**等精细控制场景下，需要用 `TransactionTemplate` 编程式事务——在代码中显式控制事务的 begin / commit / rollback。

---

## 🎯 一句话定位

**编程式事务 = 手动控制事务边界**——通过 `TransactionTemplate` 的 `execute(...)` API 在 lambda 内执行业务，结合 `TransactionStatus` 主动控制回滚。**与 `@Transactional` 互补，不替代**。

---

## 一、为什么需要编程式事务

### `@Transactional` 的局限

| 场景 | `@Transactional` 痛点 | `TransactionTemplate` 方案 |
|------|---------------------|--------------------------|
| **动态回滚条件** | rollbackFor 是静态配置 | 在 lambda 内根据业务条件 `status.setRollbackOnly()` |
| **事务边界跨方法** | AOP 代理只能拦截 public 方法 | 显式包裹任意代码块 |
| **复杂返回值** | 方法返回值类型固定 | `execute` 返回任意泛型 `T` |
| **批量循环** | 整个循环一个大事务 | 可每个迭代独立事务 |
| **与外部资源混合** | 与消息队列 / RPC 协调困难 | 显式控制提交时机 |

### 适用 vs 不适用

| 维度 | 声明式 `@Transactional` | 编程式 `TransactionTemplate` |
|------|------------------------|------------------------------|
| **代码量** | 1 行注解 | 5-10 行模板代码 |
| **可读性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **灵活性** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **使用频率** | 90%+ | < 10% |
| **典型场景** | 标准 CRUD | 复杂批量、动态回滚 |

---

## 二、核心 API：`TransactionTemplate`

### 1. 配置 Bean

```java
@Configuration
public class TxConfig {

    @Bean
    public TransactionTemplate transactionTemplate(PlatformTransactionManager txManager) {
        return new TransactionTemplate(txManager);
    }

    // 也可指定属性
    @Bean("readOnlyTx")
    public TransactionTemplate readOnlyTx(PlatformTransactionManager txManager) {
        return new TransactionTemplate(txManager);
        // 默认走 @Transactional 全局属性，也可单独设置
        template.setReadOnly(true);
        template.setTimeout(30);
        return template;
    }
}
```

### 2. `execute(TransactionCallback<T>)` API

```java
@Service
public class OrderService {

    @Autowired
    private TransactionTemplate transactionTemplate;

    public Order createOrder(Order order) {
        // 编程式事务：lambda 内所有代码在事务中
        return transactionTemplate.execute(status -> {
            try {
                orderRepository.save(order);
                inventoryService.decrease(order.getSkuId(), order.getQty());
                return order;
            } catch (InsufficientStockException e) {
                // 主动标记回滚
                status.setRollbackOnly();
                throw e;  // 抛出触发实际回滚
            }
        });
    }
}
```

| 方法 | 说明 |
|------|------|
| `execute(TransactionCallback<T>)` | 执行业务，返回结果 `T`，自动管理 commit/rollback |
| `executeWithoutResult(Consumer<TransactionStatus>)` | 无返回值版本 |
| `TransactionStatus.setRollbackOnly()` | 主动标记回滚（事务仍提交，但提交时回滚） |
| `TransactionStatus.isNewTransaction()` | 是否新事务 |
| `TransactionStatus.hasSavepoint()` | 是否有保存点（NESTED） |

---

## 三、与 `@Transactional` 混用

> 混用完全合法——**编程式事务会复用外层声明式事务**（REQUIRED 传播行为），不会创建新事务（除非显式配置 `PROPAGATION_REQUIRES_NEW`）。

```java
@Service
public class OrderService {

    @Autowired private TransactionTemplate txTemplate;

    @Transactional  // 外层声明式事务
    public void batchCreate(List<Order> orders) {
        for (Order order : orders) {
            // ✅ 编程式事务加入外层事务（REQUIRED）
            // 任一元素失败 → 整个外层事务回滚
            txTemplate.execute(status -> {
                orderRepository.save(order);
                return null;
            });
        }
    }
}
```

### 独立事务场景（PROPAGATION_REQUIRES_NEW）

```java
@Bean
public TransactionTemplate newTxTemplate(PlatformTransactionManager txManager) {
    TransactionTemplate t = new TransactionTemplate(txManager);
    t.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRES_NEW);
    return t;
}

// 用法：日志记录场景 —— 不管主事务成功失败，日志都入库
@Service
public class OrderService {

    @Autowired @Qualifier("newTxTemplate")
    private TransactionTemplate newTxTemplate;

    @Transactional
    public void createOrder(Order order) {
        try {
            orderRepository.save(order);
        } finally {
            // 独立事务，主事务回滚不影响日志写入
            newTxTemplate.executeWithoutResult(s ->
                logRepository.save(new Log("order created"))
            );
        }
    }
}
```

---

## 四、嵌套调用与回滚控制

### 场景：批量处理，部分回滚

```java
public void batchProcess(List<Task> tasks) {
    for (Task task : tasks) {
        txTemplate.execute(status -> {
            try {
                processOne(task);
            } catch (BusinessException e) {
                // 单条失败：仅回滚当前事务
                status.setRollbackOnly();
                log.warn("task {} failed, skipped", task.getId());
            }
            return null;
        });
    }
}
```

### 场景：基于结果动态决定提交 / 回滚

```java
public boolean tryDeduct(Long userId, BigDecimal amount) {
    Boolean success = txTemplate.execute(status -> {
        User user = userRepository.findById(userId).orElseThrow();
        if (user.getBalance().compareTo(amount) < 0) {
            status.setRollbackOnly();  // 余额不足，主动回滚
            return false;
        }
        user.setBalance(user.getBalance().subtract(amount));
        userRepository.save(user);
        return true;
    });
    return Boolean.TRUE.equals(success);
}
```

---

## 五、异常处理

```java
txTemplate.execute(status -> {
    try {
        riskyOperation();
    } catch (CheckedException e) {
        // 业务异常 → 标记回滚
        status.setRollbackOnly();
        throw e;  // 必须重新抛出，否则不会真正回滚
    } catch (RuntimeException e) {
        // RuntimeException 自动触发回滚，无需显式处理
        throw e;
    }
    return null;
});
```

> 📌 **关键**：lambda 抛异常 → 自动回滚；`setRollbackOnly()` 仅是**标记**，必须**配合抛异常**才会真正回滚。

---

## 六、最佳实践

1. **优先声明式事务**：90% 场景一行注解比模板代码清晰。
2. **声明式与编程式可混用**：编程式加入外层事务（REQUIRED 默认）。
3. **`setRollbackOnly()` 必须配合 throw**：标记只是"建议"，不抛异常仍会提交。
4. **注意事务边界**：lambda 内**所有**代码都在事务中（避免长事务）。
5. **不要在事务中捕获异常却不抛出**：导致事务不触发回滚。
6. **`PROPAGATION_REQUIRES_NEW`** 用于审计日志、通知推送等独立场景。

---

## 🤔 思考

1. **`setRollbackOnly()` 不抛异常会怎样？** Spring 仍会调用 commit，但数据库收到的是 "rollback only" 标记 → 数据库执行回滚。**所以 throw 是给调用方看的**。
2. **lambda 抛异常 = 回滚 = 回滚的是哪个事务？** 当前事务（外层如有事务则外层回滚）。
3. **编程式事务能管理分布式事务吗？** 不能。分布式事务需 `@GlobalTransactional`（Seata）或 JTA。

---

## 相关章节

- ⬅️ [返回事务总览](README.md)
- [传播行为与隔离级别](propagation-and-isolation.md) — REQUIRED/REQUIRES_NEW 传播行为
- [事务失效场景](failure-cases.md) — 异常吞掉、自调用等陷阱