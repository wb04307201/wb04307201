# 事务失效场景与解决方案

> ⬅️ [返回事务总览](README.md) | [传播行为与隔离级别](propagation-and-isolation.md)

**事务失效是 Spring 面试和实际开发的高频问题**。本文整理 7 大常见失效场景、原因、解决方案，帮你彻底解决"事务不生效"问题。

---

## 🎯 一句话定位

**事务失效的 7 大场景 = 1)非public 2)自调用 3)异常被吞 4)异常类型错 5)数据库不支持 6)事务管理器未配 7)多线程**。其中**自调用**和**异常被吞**最常见，**非public** 最容易被忽略。

---

## 一、7 大失效场景速查表

| 场景 | 原因 | 解决方案 |
|------|------|---------|
| **非 public 方法** | AOP 代理仅拦截 public 方法 | 将方法改为 public |
| **自调用问题** | 类内部方法调用不经过代理 | 注入自身代理或使用 `AopContext.currentProxy()` |
| **异常被捕获未抛出** | 事务默认仅回滚 `RuntimeException` | 捕获后重新抛出或调用 `setRollbackOnly()` |
| **错误异常类型** | 检查型异常（如 IOException）不触发回滚 | 通过 `rollbackFor` 指定回滚异常 |
| **数据库不支持事务** | 表引擎为 MyISAM 等非事务型 | 切换为 InnoDB 等事务型引擎 |
| **事务管理器未配置** | 缺少 `@EnableTransactionManagement` | 配置事务管理器并启用注解 |
| **多线程调用** | 事务绑定线程，跨线程事务失效 | 避免多线程操作事务，或使用线程同步 |

---

## 二、详细分析与修复

### 场景 1：非 public 方法（最容易被忽略）

> **AOP 代理仅拦截 public 方法**。`protected`、`private`、`package-private` 方法上的 @Transactional 不会生效。

```java
@Service
public class OrderService {

    // ❌ 失效：protected 方法，事务不会生效
    @Transactional
    protected void saveOrderProtected() {
        orderRepository.save(new Order());
    }

    // ❌ 失效：private 方法，事务不会生效
    @Transactional
    private void saveOrderPrivate() {
        orderRepository.save(new Order());
    }

    // ✅ 正确：public 方法
    @Transactional
    public void saveOrderPublic() {
        orderRepository.save(new Order());
    }
}
```

**原因**：Spring AOP 只能拦截 public 方法（因为 JDK 代理基于接口，CGLIB 代理不能 override 非 public 方法）。

**修复**：将方法改为 `public`。

---

### 场景 2：自调用问题（最常见）

> 类内部方法调用不经过代理，导致 @Transactional 失效。

```java
@Service
public class OrderService {

    public void createOrder() {
        // ❌ 失效：this 调用，不经过代理
        saveOrder();
    }

    @Transactional
    public void saveOrder() {
        orderRepository.save(new Order());
    }
}
```

**原因**：`this.saveOrder()` 是**对象内部直接调用**，**没有走 Spring 代理**，所以 @Transactional 不生效。

**修复方案**：

#### 方案 1：注入自身代理（**推荐**）

```java
@Service
public class OrderService {

    @Autowired
    private OrderService self;  // 注入自身代理

    public void createOrder() {
        // ✅ 通过代理调用，事务生效
        self.saveOrder();
    }

    @Transactional
    public void saveOrder() {
        orderRepository.save(new Order());
    }
}
```

#### 方案 2：AopContext.currentProxy()

```java
@EnableAspectJAutoProxy(exposeProxy = true)  // 必须开启 exposeProxy
public class AppConfig { }

@Service
public class OrderService {

    public void createOrder() {
        // ✅ 通过 AopContext 拿到代理对象
        ((OrderService) AopContext.currentProxy()).saveOrder();
    }

    @Transactional
    public void saveOrder() {
        orderRepository.save(new Order());
    }
}
```

#### 方案 3：拆分到不同的 Bean

```java
@Service
public class OrderService {
    @Autowired
    private OrderHelper orderHelper;

    public void createOrder() {
        orderHelper.saveOrder();  // ✅ 不同 Bean，走代理
    }
}

@Service
public class OrderHelper {
    @Transactional
    public void saveOrder() {
        orderRepository.save(new Order());
    }
}
```

---

### 场景 3：异常被捕获未抛出（最隐蔽）

> 异常在方法内被 catch 住但没有重新抛出，**事务无法感知异常**，不回滚。

```java
@Service
public class OrderService {

    @Transactional
    public void createOrder() {
        try {
            orderRepository.save(new Order());
        } catch (Exception e) {
            // ❌ 异常被吞，事务不会回滚
            log.error("save failed", e);
        }
    }
}
```

**修复方案**：

```java
@Service
public class OrderService {

    @Transactional
    public void createOrder() {
        try {
            orderRepository.save(new Order());
        } catch (Exception e) {
            log.error("save failed", e);
            throw e;  // ✅ 重新抛出，事务回滚
        }
    }
}
```

或手动标记回滚：

```java
@Transactional
public void createOrder() {
    try {
        orderRepository.save(new Order());
    } catch (Exception e) {
        log.error("save failed", e);
        // 手动标记回滚
        TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
    }
}
```

---

### 场景 4：错误异常类型（最容易理解错）

> **事务默认仅回滚 `RuntimeException` 和 `Error`**，**不回滚检查型异常（Exception）**。

```java
@Service
public class OrderService {

    @Transactional  // ❌ IOException 是检查型异常，不触发回滚
    public void importOrders() throws IOException {
        orderRepository.save(new Order());
        Files.readAllBytes(Paths.get("/tmp/x"));  // 抛 IOException
    }
}
```

**修复方案**：

```java
@Service
public class OrderService {

    // ✅ 显式指定回滚异常
    @Transactional(rollbackFor = Exception.class)
    public void importOrders() throws IOException {
        orderRepository.save(new Order());
        Files.readAllBytes(Paths.get("/tmp/x"));
    }
}
```

**4 种异常回滚配置**：

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `rollbackFor` | `RuntimeException.class`, `Error.class` | 指定**触发回滚**的异常 |
| `noRollbackFor` | 空 | 指定**不回滚**的异常 |
| `rollbackForClassName` | 同 rollbackFor | 字符串形式 |
| `noRollbackForClassName` | 同 noRollbackFor | 字符串形式 |

> 📌 最佳实践：**统一用 `@Transactional(rollbackFor = Exception.class)`**。

---

### 场景 5：数据库不支持事务

> 表引擎为 MyISAM 等**非事务型**引擎时，事务不生效。

```sql
-- 查看表引擎
SHOW TABLE STATUS WHERE Name = 'orders';

-- 修改为 InnoDB（事务型）
ALTER TABLE orders ENGINE = InnoDB;
```

**常见事务型引擎**：
- MySQL：**InnoDB**（支持）
- MySQL：**MyISAM**（**不支持**）
- PostgreSQL：默认支持
- Oracle：默认支持

---

### 场景 6：事务管理器未配置

> 缺少 `@EnableTransactionManagement` 或未配置 `PlatformTransactionManager`。

```java
@Configuration
@EnableTransactionManagement  // ✅ 启用事务管理
public class AppConfig {

    @Bean
    public PlatformTransactionManager transactionManager(DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

> 📌 **Spring Boot 项目**：spring-boot-starter-data-jpa 或 jdbc 自动配置了事务管理器，**无需手动配置**。

---

### 场景 7：多线程调用

> **事务绑定到当前线程**。子线程中获取不到父线程的事务，**子线程的事务独立**。

```java
@Service
public class OrderService {

    @Transactional
    public void createOrder() {
        orderRepository.save(new Order());

        // ❌ 子线程中无法获取父线程的事务
        new Thread(() -> {
            logRepository.save(new Log("订单创建"));  // 没有事务
        }).start();
    }
}
```

**修复方案**：

```java
@Service
public class OrderService {

    @Autowired
    private LogService logService;

    @Transactional
    public void createOrder() {
        orderRepository.save(new Order());

        // ✅ 同步调用（同一线程）
        logService.logOperation("订单创建");
    }
}

@Service
public class LogService {

    // 独立事务，确保日志一定入库
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logOperation(String message) {
        logRepository.save(new Log(message));
    }
}
```

---

## 三、事务失效排查清单

> 遇到事务不生效时，按这个清单逐项检查：

```
✅ 1. 方法是 public 吗？
✅ 2. 是否是自调用？（this.xxx()）
✅ 3. 异常被 catch 了吗？有没有重新抛出？
✅ 4. 异常类型对吗？需要 rollbackFor 配置？
✅ 5. 数据库引擎支持事务吗？（InnoDB 才支持）
✅ 6. 事务管理器配置了吗？（Spring Boot 自动）
✅ 7. 类是否被 Spring 管理？（@Service/@Component）
✅ 8. 方法是否被外部调用？（代理对象调用）
```

### 调试技巧

```java
// 1. 在方法第一行打印日志，确认是否被代理调用
public void createOrder() {
    System.out.println("OrderService: " + this.getClass().getName());
    // 如果输出是 OrderService（不是 OrderService$$EnhancerByCGLIB），说明没走代理
    saveOrder();
}

// 2. 在 @Transactional 方法中抛 RuntimeException，测试是否回滚
@Transactional
public void testRollback() {
    jdbcTemplate.execute("INSERT INTO orders (name) VALUES ('test')");
    throw new RuntimeException("test");
    // 如果回滚成功，说明事务生效
}
```

---

## 四、最佳实践

1. **优先声明式事务**：减少代码侵入，提升可维护性。
2. **合理选择传播行为和隔离级别**：根据业务需求（性能、一致性）权衡。
3. **避免自调用**：通过代理对象调用事务方法（注入 self）。
4. **明确回滚异常**：统一用 `rollbackFor = Exception.class`。
5. **数据库兼容性**：确认数据库支持指定隔离级别和事务特性。
6. **异常处理**：捕获后必须**重新抛出**或**手动标记回滚**。
7. **多线程场景**：用 `REQUIRES_NEW` 实现独立事务。

---

## 🤔 思考

1. **为什么 AOP 不能拦截 private 方法？** JDK 代理基于接口；CGLIB 代理不能 override private 方法。
2. **自调用为什么会失效？** `this.method()` 不经过 Spring 生成的代理对象。
3. **为什么检查型异常默认不回滚？** Spring 早期设计者的判断——检查型异常是"可预期的"，应由业务代码处理。
4. **多线程事务能传播吗？** 不能，事务绑定 ThreadLocal。

---

## 相关章节

- ⬅️ [返回事务总览](README.md)
- [传播行为与隔离级别](propagation-and-isolation.md) — 7 种传播 + 4 种隔离
- [03 数据层/分布式事务](distributed/theory-and-patterns.md) — Seata、2PC、3PC、Saga
- [01 核心容器/AOP 通知顺序](../../01-core/aop/advice-order-and-best-practices.md) — 自调用问题详解
