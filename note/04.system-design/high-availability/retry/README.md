# 重试

在分布式系统中，**重试**是一种基础且关键的容错策略，通过自动重试失败的请求来提高系统可用性。然而，不合理的设计可能导致级联故障、资源耗尽或数据不一致等问题。以下从原理、适用场景、策略设计、风险控制及实践工具五个维度展开介绍：

## 一、重试的核心原理
重试的核心逻辑是：**当请求因临时性故障（如网络抖动、服务超时、资源竞争）失败时，自动以一定策略（如指数退避）重新发起请求，直到成功或达到最大重试次数**。其本质是通过时间换成功率，适用于可恢复的临时性故障。

## 二、适用场景与不适用场景
### ✅ 适合重试的场景
1. **网络临时性故障**：如TCP连接超时、DNS解析失败。
2. **服务瞬时过载**：如数据库连接池耗尽但快速恢复。
3. **幂等操作**：如GET请求、PUT请求（更新已存在资源）、DELETE请求、带有唯一ID的创建操作（如订单号）。
4. **第三方服务抖动**：如支付接口短暂不可用。

### ❌ 不适合重试的场景
1. **非幂等操作**：如POST请求（重复提交可能导致数据重复）、无唯一ID的创建操作。
2. **永久性故障**：如服务宕机、依赖的存储损坏。
3. **超时阈值内无法完成**：如耗时任务（如大数据分析）超时后重试无意义。
4. **已触发熔断**：当服务已被熔断时，重试会加剧系统负载。

## 三、重试策略设计要点
### 1. 退避算法（Backoff Strategy）
- **固定间隔重试**：简单但可能导致瞬时过载（如每次重试间隔1秒）。
- **指数退避（Exponential Backoff）**：
    - 首次失败后等待`baseDelay`（如100ms），后续每次失败等待时间翻倍（如100ms→200ms→400ms）。
    - 可结合随机抖动（Jitter）避免重试风暴（如`delay = baseDelay * 2^retryCount * (1 + random(0,1))`）。
- **扁平指数退避**：设置最大间隔上限（如最大等待5秒），避免长时间等待。

### 2. 终止条件
- **最大重试次数**：通常设置为3-5次（如HTTP客户端默认3次）。
- **总超时时间**：限制所有重试的总时长（如总耗时不超过2秒）。
- **上下文感知终止**：如结合熔断器状态，当服务处于Open状态时直接失败。

### 3. 异常分类处理
- **可重试异常**：如`SocketTimeoutException`、`ConnectException`。
- **不可重试异常**：如`IllegalArgumentException`、`NullPointerException`。
- **部分成功异常**：如批量操作中部分失败，需根据业务决定是否重试。

## 四、重试的风险与控制
### 1. 级联故障（Cascading Failure）
- **问题**：当大量请求因故障同时重试时，可能压垮下游服务（如数据库连接池耗尽）。
- **解决方案**：
    - 结合熔断器（如Hystrix/Resilience4j），当错误率过高时直接失败。
    - 限制并发重试数（如信号量控制）。
    - 使用队列缓冲重试请求（如Kafka延迟队列）。

### 2. 数据不一致
- **问题**：非幂等操作重试可能导致重复数据（如重复扣款）。
- **解决方案**：
    - 设计幂等接口（如通过唯一ID去重）。
    - 使用分布式事务（如TCC、Saga模式）。
    - 引入状态机管理操作状态（如“已提交”“已处理”）。

### 3. 性能开销
- **问题**：频繁重试会增加响应时间（RT）和资源消耗。
- **解决方案**：
    - 设置合理的超时时间（如HTTP请求超时1秒）。
    - 异步重试（如MQ重试队列）。
    - 监控重试率，优化系统瓶颈。

## 五、实践工具与代码示例
### 1. 开源工具
- **Spring Retry**：基于注解的轻量级重试框架。
  ```java
  @Retryable(value = {RetryableException.class}, 
             maxAttempts = 3, 
             backoff = @Backoff(delay = 1000, multiplier = 2))
  public String callExternalService() {
      // 调用可能失败的外部服务
  }
  ```
- **Resilience4j Retry**：功能丰富，支持配置化与熔断集成。
  ```java
  RetryConfig config = RetryConfig.custom()
      .maxAttempts(3)
      .waitDuration(Duration.ofMillis(1000))
      .retryExceptions(TimeoutException.class, NetworkException.class)
      .build();
  Retry retry = Retry.of("externalService", config);
  Supplier<String> decoratedSupplier = Retry.decorateSupplier(retry, () -> callService());
  String result = Try.ofSupplier(decoratedSupplier).get();
  ```
- **Feign Client**：HTTP客户端内置重试机制（需配置`feign.retryer`）。

### 2. 云服务原生支持
- **AWS SDK**：自动为S3、DynamoDB等服务实现指数退避重试。
- **Azure SDK**：提供`RetryPolicy`配置重试行为。
- **GCP Client Libraries**：支持`ExponentialBackOff`策略。

## 六、最佳实践总结
1. **幂等设计优先**：确保重试不会导致数据不一致。
2. **退避算法合理**：避免固定间隔重试，优先选择指数退避+随机抖动。
3. **终止条件明确**：结合最大次数与总超时时间。
4. **异常分类处理**：区分临时性故障与业务错误。
5. **监控与告警**：跟踪重试率、失败率，及时发现系统性问题。
6. **与熔断、限流协同**：重试是局部容错，需结合全局容错策略。