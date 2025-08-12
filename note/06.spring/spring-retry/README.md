# Spring Retry 自动重试

Spring Retry 是 Spring 框架中用于实现方法自动重试的组件，通过声明式编程模型简化瞬时故障处理（如网络超时、数据库连接失败等），提升系统容错能力。其核心机制基于 AOP 拦截器，结合灵活的策略配置实现可定制的重试行为。

## 核心工作原理
1. **AOP 拦截机制**
    - 通过 `@EnableRetry` 启用 AOP 代理，扫描带有 `@Retryable` 注解的方法。
    - 当方法抛出指定异常时，AOP 拦截器捕获异常并触发重试逻辑。

2. **重试决策流程**
    - **异常匹配**：检查抛出的异常是否在 `@Retryable.value` 或 `include` 列表中，且不在 `exclude` 列表中。
    - **策略判断**：根据 `RetryPolicy`（如最大尝试次数、超时时间）和 `BackOffPolicy`（如固定延迟、指数退避）决定是否重试。
    - **等待执行**：按策略等待指定时间后再次调用目标方法。
    - **恢复处理**：若所有重试失败，执行 `@Recover` 注解标记的恢复方法。

## 关键组件与配置
### 1. 核心注解
- **`@EnableRetry`**  
  启用 Spring Retry 功能，通常添加在启动类或配置类上。

- **`@Retryable`**  
  定义重试规则：
  ```java
  @Retryable(
      value = {SQLException.class},      // 触发重试的异常类型
      maxAttempts = 3,                  // 最大尝试次数（含首次调用）
      backoff = @Backoff(delay = 1000) // 固定延迟1秒后重试
  )
  public void callExternalService() { ... }
  ```

- **`@Recover`**  
  定义重试失败后的恢复逻辑，方法签名需与 `@Retryable` 方法兼容：
  ```java
  @Recover
  public void recover(SQLException e) {
      log.error("所有重试失败，执行降级处理", e);
  }
  ```

### 2. 重试策略（RetryPolicy）
- **SimpleRetryPolicy**：基于尝试次数的简单策略。
  ```java
  SimpleRetryPolicy policy = new SimpleRetryPolicy();
  policy.setMaxAttempts(5); // 设置最大重试次数
  ```

- **TimeoutRetryPolicy**：基于总超时时间的策略。
  ```java
  TimeoutRetryPolicy policy = new TimeoutRetryPolicy();
  policy.setTimeout(5000L); // 设置超时时间为5秒
  ```

- **ExceptionClassifierRetryPolicy**：根据异常类型动态决策。
  ```java
  Map<Class<? extends Throwable>, Boolean> retryableExceptions = new HashMap<>();
  retryableExceptions.put(IllegalArgumentException.class, true);  // 重试
  retryableExceptions.put(NullPointerException.class, false);       // 不重试
  ExceptionClassifierRetryPolicy policy = new ExceptionClassifierRetryPolicy();
  policy.setPolicyMap(retryableExceptions);
  ```

### 3. 退避策略（BackOffPolicy）
- **FixedBackOffPolicy**：固定间隔重试。
  ```java
  FixedBackOffPolicy policy = new FixedBackOffPolicy();
  policy.setBackOffPeriod(2000L); // 每次重试间隔2秒
  ```

- **ExponentialBackOffPolicy**：指数退避，避免雪崩。
  ```java
  ExponentialBackOffPolicy policy = new ExponentialBackOffPolicy();
  policy.setInitialInterval(1000L);  // 初始延迟1秒
  policy.setMultiplier(2.0);         // 每次延迟时间翻倍
  policy.setMaxInterval(10000L);     // 最大延迟10秒
  ```

- **UniformRandomBackOffPolicy**：随机间隔重试。
  ```java
  UniformRandomBackOffPolicy policy = new UniformRandomBackOffPolicy();
  policy.setMinBackOffPeriod(1000L);  // 最小延迟1秒
  policy.setMaxBackOffPeriod(3000L);  // 最大延迟3秒
  ```

## 高级功能
1. **监听器（RetryListener）**  
   监听重试生命周期事件（开始、错误、关闭），实现自定义逻辑：
   ```java
   @Component
   public class CustomRetryListener implements RetryListener {
       @Override
       public <T, E extends Throwable> boolean open(RetryContext context, RetryCallback<T, E> callback) {
           log.info("重试开始，当前次数: {}", context.getRetryCount());
           return true; // 继续重试
       }
       // 其他方法省略...
   }
   ```

2. **编程式配置（RetryTemplate）**  
   通过 Java 代码手动创建重试模板：
   ```java
   @Bean
   public RetryTemplate retryTemplate() {
       RetryTemplate template = new RetryTemplate();
       template.setRetryPolicy(new SimpleRetryPolicy(3));
       template.setBackOffPolicy(new ExponentialBackOffPolicy());
       return template;
   }
   ```

3. **表达式支持**  
   使用 SpEL 动态配置参数：
   ```java
   @Retryable(
       maxAttemptsExpression = "#{${retry.maxAttempts:3}}", // 从配置文件读取
       backoff = @Backoff(delayExpression = "#{T(java.lang.Math).random() * 1000}") // 随机延迟
   )
   public void dynamicRetryMethod() { ... }
   ```

## 应用场景与最佳实践
1. **典型场景**
    - 调用第三方 API 或微服务时的网络波动。
    - 数据库连接池耗尽或死锁。
    - 消息队列消费失败（如 RabbitMQ 重试队列）。

2. **最佳实践**
    - **精准异常过滤**：排除 `IllegalArgumentException` 等非瞬时异常。
    - **合理退避策略**：避免指数退避导致请求堆积，可结合随机抖动。
    - **熔断机制**：与 Spring Cloud Circuit Breaker 集成，防止“重试风暴”。
    - **日志与监控**：记录重试事件，便于问题排查。

## 示例代码
```java
@SpringBootApplication
@EnableRetry
public class RetryDemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(RetryDemoApplication.class, args);
    }
}

@Service
public class OrderService {
    @Retryable(
        value = {SQLException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2),
        listeners = {"customRetryListener"} // 引用自定义监听器
    )
    public void placeOrder(Order order) throws SQLException {
        // 模拟数据库操作失败
        if (order.getAmount() > 1000) {
            throw new SQLException("Database connection failed");
        }
        log.info("订单创建成功: {}", order.getId());
    }

    @Recover
    public void recover(SQLException e, Order order) {
        log.error("订单创建失败，执行降级处理: {}", order.getId(), e);
    }
}
```

## 六、总结
Spring Retry 通过声明式注解和灵活的策略配置，为分布式系统提供了强大的容错能力。其核心优势在于：
- **解耦重试逻辑**：业务代码与重试策略分离。
- **策略可定制**：支持多种重试和退避策略。
- **生态集成**：与 Spring Boot、AOP、监控系统无缝协作。

合理使用 Spring Retry 可显著提升系统稳定性，但需避免滥用导致性能问题。