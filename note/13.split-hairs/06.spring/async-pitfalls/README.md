# @Async 失效的 4 种场景与解决方案

## 引子：加了 @Async，为什么还是同步执行？

```java
@Service
public class NotifyService {
    
    @Async  // 应该异步执行啊！
    public void sendNotification(String message) {
        System.out.println("发送通知：" + message);
        System.out.println("线程：" + Thread.currentThread().getName());
    }
}

// 调用
notifyService.sendNotification("hello");
System.out.println("主线程继续执行");  // 结果：打印的还是主线程！
```

`@Async` 应该让方法在另一个线程执行，但实际上它还在主线程跑。为什么？

和 `@Transactional` 一样——`@Async` 也是基于 AOP 代理实现的。内部调用、非 public 方法等场景都会让代理失效。

---

> 📚 **前置知识**：[AOP](../../../06.spring/01-core/aop/README.md)

## 一、核心原理

Spring 的 `@Async` 注解通过 AOP（面向切面编程）代理机制实现异步调用。当在方法上标注 `@Async` 时，Spring 容器会为该 Bean 创建一个代理对象，实际调用时由代理对象将方法提交到线程池执行。

### 启用机制

使用 `@EnableAsync` 注解开启异步支持，该注解会导入 `AsyncConfigurationSelector`，注册以下核心组件：

- **AnnotationAsyncExecutionInterceptor**：拦截器，负责捕获被 `@Async` 标注的方法调用
- **AsyncExecutionInterceptor**：核心拦截逻辑，将方法调用封装为 `Runnable` 或 `Callable`，提交给 `TaskExecutor` 执行
- **ProxyAsyncConfiguration**：创建异步代理配置

### 执行流程

```
调用方 → 代理对象(Proxy) → AsyncExecutionInterceptor → TaskExecutor.execute() → 目标方法
```

默认情况下，Spring 使用 `SimpleAsyncTaskExecutor`，该执行器每次调用都创建新线程，不会复用线程池。

---

## 二、4 种失效场景

| 序号 | 失效场景 | 根本原因 |
|------|----------|----------|
| 1 | 同类内部调用 | 绕过 AOP 代理，直接调用目标对象方法 |
| 2 | 返回类型非 Future/CompletableFuture | 无法感知异步执行结果和异常 |
| 3 | 未添加 @EnableAsync | 异步基础设施未初始化，注解被忽略 |
| 4 | 默认 SimpleAsyncTaskExecutor | 每次新建线程，无线程复用和资源限制 |

---

## 三、每种场景代码示例 + 解决方案

### 场景一：同类内部调用（最常见）

```java
@Service
public class OrderService {

    public void createOrder() {
        // 问题：this.sendNotification() 直接调用目标对象，绕过代理
        sendNotification();  // ❌ 同步执行，@Async 失效
    }

    @Async
    public void sendNotification() {
        log.info("发送通知: thread={}", Thread.currentThread().getName());
    }
}
```

**解决方案：注入自身或通过其他 Bean 调用**

```java
@Service
public class OrderService {

    @Autowired
    private OrderService self;  // 注入代理对象

    public void createOrder() {
        self.sendNotification();  // ✅ 通过代理调用，@Async 生效
    }

    @Async
    public void sendNotification() {
        log.info("发送通知: thread={}", Thread.currentThread().getName());
    }
}
```

或者抽取到独立的 Service：

```java
@Service
public class NotificationService {
    @Async
    public void sendNotification() {
        log.info("发送通知: thread={}", Thread.currentThread().getName());
    }
}

@Service
public class OrderService {
    @Autowired
    private NotificationService notificationService;

    public void createOrder() {
        notificationService.sendNotification();  // ✅ 跨 Bean 调用，@Async 生效
    }
}
```

### 场景二：返回 void 无法感知异常

```java
@Async
public void processOrder() {
    // 抛出异常时，调用方无法捕获
    throw new RuntimeException("处理失败");  // ❌ 异常被吞掉
}
```

**解决方案：返回 CompletableFuture 获取异步结果**

```java
@Async
public CompletableFuture<String> processOrder() {
    try {
        log.info("处理订单: thread={}", Thread.currentThread().getName());
        return CompletableFuture.completedFuture("success");
    } catch (Exception e) {
        return CompletableFuture.failedFuture(e);  // ✅ 异常可被捕获
    }
}

// 调用方
CompletableFuture<String> future = orderService.processOrder();
try {
    String result = future.get(5, TimeUnit.SECONDS);  // 阻塞等待结果
} catch (ExecutionException e) {
    log.error("异步任务异常", e.getCause());  // ✅ 获取原始异常
} catch (TimeoutException e) {
    log.error("异步任务超时", e);
}
```

### 场景三：缺少 @EnableAsync

```java
@Configuration
@ComponentScan("com.example")
// 忘记添加 @EnableAsync  // ❌ @Async 注解被忽略
public class AppConfig {
}
```

**解决方案：显式启用异步支持**

```java
@Configuration
@EnableAsync  // ✅ 开启异步支持
@ComponentScan("com.example")
public class AppConfig {
}
```

### 场景四：默认 SimpleAsyncTaskExecutor

```java
@Async
public void heavyTask() {
    // 默认使用 SimpleAsyncTaskExecutor，每次创建新线程  // ❌ 无线程复用
    log.info("执行耗时任务: thread={}", Thread.currentThread().getName());
}
```

**解决方案：自定义 ThreadPoolTaskExecutor**

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(4);           // 核心线程数
        executor.setMaxPoolSize(8);            // 最大线程数
        executor.setQueueCapacity(100);        // 队列容量
        executor.setThreadNamePrefix("async-"); // 线程名前缀
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();                 // ⚠️ 必须调用
        return executor;
    }

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return (ex, method, params) -> {
            log.error("异步方法 {} 发生异常: {}", method.getName(), ex.getMessage(), ex);
        };
    }
}
```

---

## 四、最佳实践

### 1. 始终使用自定义线程池

避免使用默认的 `SimpleAsyncTaskExecutor`，根据业务场景合理配置线程池参数：

```java
ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
executor.setCorePoolSize(Runtime.getRuntime().availableProcessors());
executor.setMaxPoolSize(Runtime.getRuntime().availableProcessors() * 2);
executor.setQueueCapacity(200);
executor.setKeepAliveSeconds(60);
executor.setThreadNamePrefix("business-async-");
executor.setWaitForTasksToCompleteOnShutdown(true);  // 优雅关闭
executor.setAwaitTerminationSeconds(30);
executor.initialize();
```

### 2. 正确处理异步异常

对于返回 `void` 的 `@Async` 方法，配置全局异常处理器：

```java
@Bean
public AsyncUncaughtExceptionHandler asyncUncaughtExceptionHandler() {
    return (ex, method, params) -> {
        log.error("异步任务 [{}] 执行失败, 参数: {}", 
                  method.getName(), Arrays.toString(params), ex);
        // 可选：发送告警、记录监控指标等
    };
}
```

对于返回 `CompletableFuture` 的方法，在调用方通过 `exceptionally()` 或 `handle()` 处理：

```java
orderService.processOrder()
    .thenAccept(result -> log.info("处理成功: {}", result))
    .exceptionally(ex -> {
        log.error("处理失败", ex);
        return null;
    });
```

### 3. 合理使用 Future 返回值

优先使用 `CompletableFuture` 而非裸 `Future`，支持链式调用和组合操作：

```java
@Async
public CompletableFuture<User> getUserById(Long id) {
    User user = userRepository.findById(id);
    return CompletableFuture.completedFuture(user);
}

@Async
public CompletableFuture<Order> getOrderById(Long id) {
    Order order = orderRepository.findById(id);
    return CompletableFuture.completedFuture(order);
}

// 并行执行多个异步任务
getUserById(1L).thenCombine(getOrderById(1L), (user, order) -> {
    // 两个任务都完成后执行
    return buildUserOrderView(user, order);
});
```

---

## 五、常见陷阱

### 陷阱一：SimpleAsyncTaskExecutor 不复用线程

默认执行器每次调用都创建新线程，高并发下会导致：

- 线程数量无限增长，耗尽系统资源
- 频繁线程创建/销毁带来性能开销
- 无法控制并发度，可能压垮下游服务

**验证方式**：观察日志中的线程名，若每次不同则说明未复用。

### 陷阱二：@Async + @Transactional 的事务传播问题

```java
@Transactional
public void createOrder() {
    saveOrder();              // 在主线程事务中
    sendNotification();       // @Async 在新线程中执行
}

@Async
@Transactional               // ❌ 新线程中的独立事务，不继承主事务
public void sendNotification() {
    updateNotificationStatus();  // 此事务与 createOrder 的事务无关
}
```

**问题分析**：

- `@Async` 方法在新的线程中执行，Spring 的事务上下文基于 `ThreadLocal`，新线程无法访问主线程的事务
- 即使添加 `@Transactional`，也是独立的新事务，与调用方事务无关联
- 若主事务回滚，异步方法已提交的更改不会回滚，导致数据不一致

**解决方案**：

- 避免在 `@Async` 方法中使用 `@Transactional`，或将异步逻辑设计为最终一致性补偿
- 如需保证一致性，使用消息队列+本地事务表方案

### 陷阱三：循环依赖导致代理失效

当存在循环依赖时，Spring 可能注入的是原始对象而非代理对象，导致 `@Async` 失效。

**解决方案**：使用 `@Lazy` 打破循环依赖，或重构代码消除循环依赖。

---

## 六、面试话术（30 秒版）

> "@Async 基于 Spring AOP 代理实现。最常见的失效场景是同类内部调用，因为 this 调用绕过了代理对象，直接执行目标方法。解决方案是注入自身或通过其他 Bean 调用。另外要注意返回 void 时异常会被吞掉，建议返回 CompletableFuture 获取异步结果。还要记得加 @EnableAsync 开启异步支持，并配置自定义线程池避免 SimpleAsyncTaskExecutor 每次新建线程的问题。"

**追问要点**：

- Q: 为什么同类调用会失效？A: Spring AOP 基于代理，内部调用绕过代理
- Q: 如何获取异步执行的异常？A: 返回 CompletableFuture，通过 get() 或 exceptionally() 捕获
- Q: @Async 和 @Transactional 能一起用吗？A: 可以，但事务是独立的，不共享事务上下文

---

## 七、交叉引用

- 主模块：[`06.spring`](../../../06.spring/) — Spring 知识体系
- [事务传播](../../../06.spring/03-data/transaction/propagation-and-isolation.md) — @Transactional 事务传播机制
- [线程池核心原理](../../../01.java/concurrency/thread-basics/README.md) — 线程池调优实战

## 相关章节

- 深度阅读：[`06.spring`](../../06.spring/README.md) — 主模块详细内容
