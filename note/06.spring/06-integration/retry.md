# Spring Retry 自动重试

> 最后更新: 2026-06-14

Spring Retry 是 Spring 框架中用于实现方法自动重试的组件，通过声明式编程模型简化瞬时故障处理（如网络超时、数据库连接失败等），提升系统容错能力。其核心机制基于 AOP 拦截器，结合灵活的策略配置实现可定制的重试行为。

## 一、核心工作原理
1. **AOP 拦截机制**
    - 通过 `@EnableRetry` 启用 AOP 代理，扫描带有 `@Retryable` 注解的方法。
    - 当方法抛出指定异常时，AOP 拦截器捕获异常并触发重试逻辑。

2. **重试决策流程**
    - **异常匹配**：检查抛出的异常是否在 `@Retryable.value` 或 `include` 列表中，且不在 `exclude` 列表中。
    - **策略判断**：根据 `RetryPolicy`（如最大尝试次数、超时时间）和 `BackOffPolicy`（如固定延迟、指数退避）决定是否重试。
    - **等待执行**：按策略等待指定时间后再次调用目标方法。
    - **恢复处理**：若所有重试失败，执行 `@Recover` 注解标记的恢复方法。

## 二、关键组件与配置
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

## 三、高级功能
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

## 四、应用场景与最佳实践
1. **典型场景**
    - 调用第三方 API 或微服务时的网络波动。
    - 数据库连接池耗尽或死锁。
    - 消息队列消费失败（如 RabbitMQ 重试队列）。

2. **最佳实践**
    - **精准异常过滤**：排除 `IllegalArgumentException` 等非瞬时异常。
    - **合理退避策略**：避免指数退避导致请求堆积，可结合随机抖动。
    - **熔断机制**：与 Spring Cloud Circuit Breaker 集成，防止“重试风暴”。
    - **日志与监控**：记录重试事件，便于问题排查。

## 五、示例代码
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

## 七、Reactive 与 WebClient 重试

`@Retryable` 基于 AOP 代理，**不适用于 `Mono` / `Flux` 内部订阅链**——返回 `Mono` 后方法立即结束，异常在订阅时才抛出，AOP 拦截器已经退出。响应式场景需要用 **Resilience4j** 或 Reactor 内建的 `retryWhen`。

### 1. Resilience4j Retry 装饰 WebClient

```java
Retry retry = Retry.of("webClient", RetryConfig.custom()
        .maxAttempts(3)
        .intervalFunction(IntervalFunction.ofExponentialRandomBackoff(
                Duration.ofMillis(500),  // initialInterval
                2.0,                      // multiplier
                0.5,                      // randomizationFactor (50% 抖动)
                Duration.ofSeconds(10)))  // maxInterval
        .retryOnException(e -> e instanceof WebClientRequestException)
        .build());

WebClient client = WebClient.builder()
        .baseUrl("https://api.example.com")
        .build();

// decorateSupplier / decorateFunction / decorateCheckedSupplier
Supplier<Mono<ResponseEntity<String>>> supplier = () -> client.get()
        .uri("/users/{id}", 1)
        .retrieve()
        .toEntity(String.class);
Supplier<Mono<ResponseEntity<String>>> decorated = Retry.decorateSupplier(retry, supplier);

Mono<ResponseEntity<String>> result = Mono.fromSupplier(decorated);
```

`IntervalFunction.ofExponentialRandomBackoff(initialInterval, multiplier, randomizationFactor, maxInterval)` 是 Resilience4j 推荐的**指数 + 随机抖动**配置，避免雷鸣群效应。

### 2. @Retryable 与 @CircuitBreaker 组合

Spring Cloud Circuit Breaker（Resilience4j 实现）支持把重试和熔断分层叠加：

```java
@Service
public class OrderClient {

    @CircuitBreaker(name = "orderService", fallbackMethod = "fallback")
    @Retryable(retryFor = WebClientRequestException.class, maxAttempts = 3,
               backoff = @Backoff(delay = 500, multiplier = 2, random = true))
    public Mono<OrderDTO> getOrder(Long id) {
        return webClient.get().uri("/orders/{id}", id).retrieve().bodyToMono(OrderDTO.class);
    }

    // 注意：fallback 方法签名需与原方法一致（同步 + 返回包装类型）
    private Mono<OrderDTO> fallback(Long id, Throwable t) {
        return Mono.error(new BusinessException("订单服务暂不可用", t));
    }
}
```

**执行顺序**（由外到内）：`@CircuitBreaker` → `@Retryable` → 原方法。即"熔断打开时不再重试，重试用尽后再判定熔断"。

### 3. ExponentialRandomBackOffPolicy 调优

Spring Retry 内置的 `ExponentialRandomBackOffPolicy` 等价于 Resilience4j 的 `ofExponentialRandomBackoff`，关键参数：

```java
ExponentialRandomBackOffPolicy policy = new ExponentialRandomBackOffPolicy();
policy.setInitialInterval(500L);       // 初始延迟
policy.setMultiplier(2.0);             // 每次乘以 multiplier
policy.setMaxInterval(10_000L);        // 上限
// jitter 由 ExponentialRandomBackOffPolicy 内部按 50% 随机化，无需手动设
```

`@Backoff` 注解等价方式：

```java
@Retryable(
    retryFor = {SQLException.class},
    maxAttempts = 5,
    backoff = @Backoff(
        delay = 500,         // initialInterval
        multiplier = 2.0,    // 每次翻倍
        maxDelay = 10_000,   // 上限
        random = true        // 启用 50% 随机抖动
    )
)
public void call() { ... }
```

**调优经验**：
- **多实例共享下游**：必加 `random = true`，避免整点雪崩。
- **multiplier** 过大（>3）易导致单请求总等待时间过长（重试 N 次后总耗时 = initial × (multiplier^N - 1) / (multiplier - 1)）。
- **maxDelay** 建议 = 下游平均恢复时间 / 2。
- **总超时控制**用 `TimeoutRetryPolicy` 或外部 Hystrix-style 超时，单纯靠 `maxAttempts` 无法限制总耗时。

### 4. 选型对照

| 方案 | 同步方法 | Reactor / WebClient | 分布式一致性 |
|------|:-------:|:------------------:|:----------:|
| Spring Retry `@Retryable` | 首选 | 不可用（AOP 失效） | 单 JVM |
| Resilience4j `Retry.decorate*` | 可用 | 首选 | 多 JVM 共享配置中心 |
| Reactor `retryWhen` | 不可用 | 备选 | 单 JVM |
| Spring Batch retry (chunk) | chunk 级 | N/A | 多 JVM（分区） |

> 监控告警建议接入 07-observability 中的 [Micrometer](../07-observability/micrometer.md)。