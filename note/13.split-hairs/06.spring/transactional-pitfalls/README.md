# @Transactional 失效的 8 种场景

## 引子：一个线上 Bug

```java
@Service
public class OrderService {
    
    public void createOrder(Order order) {
        // 内部调用 saveOrder
        saveOrder(order);
    }
    
    @Transactional
    public void saveOrder(Order order) {
        orderMapper.insert(order);
        // 假设这里抛异常...
    }
}
```

你以为 `saveOrder` 加了 `@Transactional`，异常时会自动回滚？

**不会！** 事务根本没生效。

为什么？因为内部调用 `this.saveOrder()` 绕过了代理对象。`@Transactional` 是基于 AOP 实现的——**只有代理对象的调用才走事务拦截器**。

类似的坑还有 7 种——

---

> 📚 **前置知识**：[AOP](../../06.spring/01-core/aop/README.md) | [事务](../../06.spring/03-data/transaction/README.md) | [事务失效](../../06.spring/03-data/transaction/failure-cases.md)

## 一、核心原理

`@Transactional` 是基于 **AOP 代理**实现的。Spring 在编译/运行时为目标类生成代理对象，代理对象在方法调用前后开启/提交/回滚事务。

**关键洞见**：只有**通过代理对象调用**，事务才会生效。如果调用绕过了代理（比如同类内部方法调用），事务就失效。

---

## 二、8 种失效场景

### 1. 同类内部方法调用（最高频）

```java
@Service
public class OrderService {
    
    public void createOrder(Order order) {
        // ❌ 内部调用，绕过了代理，事务失效
        saveOrder(order);  
    }
    
    @Transactional
    public void saveOrder(Order order) {
        orderMapper.insert(order);
    }
}
```

**原因**：`createOrder()` 调用 `saveOrder()` 时，走的是 `this.saveOrder()`，而不是代理对象的 `saveOrder()`。

**修复方案**：

```java
// 方案 A：拆分到两个 Service
@Service
public class OrderService {
    @Autowired
    private OrderRepository orderRepository;
    
    public void createOrder(Order order) {
        orderRepository.saveOrder(order);  // 通过代理调用
    }
}

@Service
public class OrderRepository {
    @Transactional
    public void saveOrder(Order order) {
        orderMapper.insert(order);
    }
}

// 方案 B：自我注入（Spring 4.3+）
@Service
public class OrderService {
    @Autowired
    private OrderService self;  // 注入自己
    
    public void createOrder(Order order) {
        self.saveOrder(order);  // 通过代理调用
    }
    
    @Transactional
    public void saveOrder(Order order) {
        orderMapper.insert(order);
    }
}

// 方案 C：从 ApplicationContext 获取代理
@Autowired
private ApplicationContext context;

public void createOrder(Order order) {
    OrderService proxy = context.getBean(OrderService.class);
    proxy.saveOrder(order);
}
```

---

### 2. 方法不是 public

```java
@Service
public class OrderService {
    
    @Transactional
    protected void saveOrder(Order order) {  // ❌ protected，事务失效
        orderMapper.insert(order);
    }
    
    @Transactional
    private void saveOrder2(Order order) {  // ❌ private，事务失效
        orderMapper.insert(order);
    }
}
```

**原因**：Spring AOP 默认使用 JDK 动态代理（要求接口方法）或 CGLIB（要求子类重写）。`protected` / `private` 方法无法被代理。

**修复**：方法必须是 `public`。

---

### 3. 异常被 catch 吞掉

```java
@Service
public class OrderService {
    
    @Transactional
    public void createOrder(Order order) {
        try {
            orderMapper.insert(order);
            paymentService.pay(order);  // 抛异常
        } catch (Exception e) {
            log.error("error", e);
            // ❌ 异常被吞，Spring 不知道要回滚
        }
    }
}
```

**原因**：Spring 事务管理器只在方法抛出异常时回滚。异常被 catch 后，Spring 认为执行成功，提交事务。

**修复**：

```java
@Transactional
public void createOrder(Order order) {
    try {
        orderMapper.insert(order);
        paymentService.pay(order);
    } catch (Exception e) {
        log.error("error", e);
        throw e;  // ✅ 重新抛出，让 Spring 感知
        // 或 throw new RuntimeException(e);
    }
}
```

---

### 4. 抛出的异常类型不匹配

```java
@Service
public class OrderService {
    
    @Transactional
    public void createOrder(Order order) throws IOException {
        orderMapper.insert(order);
        throw new IOException("网络错误");  // ❌ 默认只回滚 RuntimeException 和 Error
    }
}
```

**原因**：`@Transactional` 默认 `rollbackFor = {RuntimeException.class, Error.class}`，**不包括 checked exception（如 IOException）**。

**修复**：

```java
@Transactional(rollbackFor = Exception.class)  // ✅ 指定所有 Exception 都回滚
public void createOrder(Order order) throws IOException {
    // ...
}
```

> **最佳实践**：永远写 `@Transactional(rollbackFor = Exception.class)`，避免漏回滚。

---

### 5. 数据库引擎不支持事务

```java
@Transactional
public void saveData() {
    // 如果 MySQL 表引擎是 MyISAM，事务根本不会生效
    myisamMapper.insert(data);
}
```

**原因**：MyISAM 不支持事务，InnoDB 才支持。

**修复**：检查数据库表引擎：
```sql
SHOW TABLE STATUS WHERE Name = 'your_table';
-- 查看 Engine 列是否为 InnoDB
```

---

### 6. 未被 Spring 管理

```java
// ❌ 没有 @Service / @Component 注解，不是 Spring Bean
public class OrderService {
    
    @Transactional
    public void saveOrder(Order order) {
        orderMapper.insert(order);
    }
}
```

**原因**：只有 Spring 管理的 Bean 才能被 AOP 代理，普通 Java 对象加了 `@Transactional` 也无效。

**修复**：加上 `@Service` 或 `@Component`。

---

### 7. 多线程调用

```java
@Service
public class OrderService {
    
    @Transactional
    public void createOrders(List<Order> orders) {
        orders.parallelStream().forEach(order -> {
            orderMapper.insert(order);  // ❌ 并行流在新线程执行，不在原事务中
        });
    }
}
```

**原因**：事务是线程绑定的（ThreadLocal）。新线程中的操作不在原事务的上下文中。

**修复**：不要在事务方法中使用多线程。如果需要并发，拆分成多个独立事务。

---

### 8. 传播行为（Propagation）配置错误

```java
@Service
public class OrderService {
    
    @Transactional
    public void outer() {
        inner();  // inner 的事务传播行为影响外层
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void inner() {
        // 挂起外层事务，开启新事务
    }
}
```

**传播行为速查**：

| 传播行为 | 含义 | 典型场景 |
|---------|------|---------|
| `REQUIRED`（默认） | 有事务则加入，无则新建 | 常规业务 |
| `REQUIRES_NEW` | 总是新建事务，挂起外层 | 日志记录（必须独立） |
| `NESTED` | 嵌套事务（SAVEPOINT） | 部分回滚 |
| `SUPPORTS` | 有事务则加入，无则非事务运行 | 查询方法 |
| `NOT_SUPPORTED` | 总是非事务运行 | 完全不需要事务 |
| `MANDATORY` | 必须在事务中调用，否则抛异常 | 强制事务上下文 |
| `NEVER` | 不能在事务中调用，否则抛异常 | 严格非事务 |

---

## 三、检查清单

| 检查项 | 通过？ |
|--------|-------|
| 方法是 `public` 吗？ | ☐ |
| 类被 `@Service` / `@Component` 管理吗？ | ☐ |
| 异常被 catch 吞掉了吗？ | ☐ |
| 抛出的异常类型匹配 `rollbackFor` 吗？ | ☐ |
| 是同类内部调用吗？（最常见陷阱） | ☐ |
| 数据库表引擎是 InnoDB 吗？ | ☐ |
| 多线程环境下使用了吗？ | ☐ |
| `propagation` 配置正确吗？ | ☐ |

---

## 四、面试话术（30 秒版）

> "@Transactional 失效主要有 8 种场景：
> 
> 1. **方法不是 public**，代理无法拦截
> 2. **类没被 Spring 管理**，没有代理对象
> 3. **同类内部调用**，走 this 绕过代理（最常见）
> 4. **异常被 catch 吞掉**，Spring 不知道要回滚
> 5. **异常类型不匹配**，默认只回滚 RuntimeException
> 6. **数据库引擎不支持**，MyISAM 没事务
> 7. **多线程环境**，事务是线程绑定的
> 8. **传播行为配错**，比如 REQUIRES_NEW 挂起了外层事务
> 
> 实战中最常见的是第 3 种——同类内部调用。解决方案是拆分到两个 Service，或者自我注入。"

---

## 五、交叉引用

- 主模块：[`06.spring`](../../../06.spring/) — Spring 知识体系
- [AOP 原理](../../../06.spring/08-annotations/aop.md) — AOP 原理详解
- [@Autowired 推荐用法](../not-use-@autowired/README.md) — @Autowired 推荐用法

## 相关章节

- 深度阅读：[`06.spring`](../../06.spring/README.md) — 主模块详细内容
