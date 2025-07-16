# 重试

**重试机制（Retry Mechanism）** 是系统在遇到**临时性故障**（如网络抖动、服务过载、资源竞争）时，通过**自动重新执行失败操作**来提高请求成功率的容错设计模式。它与超时机制、熔断器等配合，是构建高可用系统的关键技术之一。

## 重试机制的核心作用
1. **应对临时性故障**
    - 网络延迟、服务重启、数据库连接池耗尽等场景下，重试可增加操作成功概率。
    - *示例*：支付接口因网络波动首次调用失败，重试后成功扣款。

2. **提升系统可用性**
    - 通过隐藏底层故障（如依赖服务短暂不可用），保持上层业务连续性。
    - *示例*：微服务调用链中，下游服务短暂超时，重试后恢复响应。

3. **简化客户端逻辑**
    - 客户端无需处理所有异常，由框架或中间件自动完成重试。
    - *示例*：HTTP客户端内置重试逻辑，开发者只需关注业务代码。

4. **与超时/熔断互补**
    - 超时机制终止慢操作，重试机制处理快速失败，熔断机制防止故障扩散。

## 重试机制的典型应用场景

| **场景**       | **适用重试的错误类型**          | **不适用场景**       |
|--------------|------------------------|-----------------|
| **网络请求**     | 连接超时、DNS解析失败、502/503错误 | 401未授权、404资源不存在 |
| **数据库操作**    | 死锁、临时锁超时、连接中断          | 唯一键冲突、外键约束失败    |
| **消息队列**     | 生产者发送消息超时、消费者处理失败      | 消息体格式错误、队列已满    |
| **分布式锁**     | 获取锁时网络中断、锁释放后立即重试      | 锁已被其他线程持有且无超时机制 |
| **第三方API调用** | 接口限流（429）、服务降级（503）    | 业务逻辑错误（如参数无效）   |

## 重试机制的关键设计要素
### 1. 重试策略
- **固定间隔重试（Fixed Backoff）**
    - 每次重试间隔时间固定（如1秒后重试，共3次）。
    - *适用场景*：故障恢复时间可预测（如数据库重启）。
    - *风险*：可能引发瞬时过载（如所有请求同时重试）。

- **指数退避重试（Exponential Backoff）**
    - 每次重试间隔时间按指数增长（如1s→2s→4s）。
    - *适用场景*：网络拥塞、服务过载等不可预测故障。
    - *示例*：
      ```java
      // Java伪代码：指数退避重试
      int maxRetries = 5;
      long initialDelay = 1000; // 1秒
      for (int i = 0; i < maxRetries; i++) {
          try {
              return callService();
          } catch (Exception e) {
              if (i == maxRetries - 1) throw e;
              Thread.sleep(initialDelay * (long) Math.pow(2, i)); // 1s, 2s, 4s...
          }
      }
      ```

- **带抖动的指数退避（Jittered Backoff）**
    - 在指数退避基础上添加随机抖动（如±50%），避免集群重试同步化。
    - *示例*：AWS SDK默认使用`Full Jitter`策略：
      ```
      delay = min(cap, random(0, base * 2^retry_count))
      ```

### 2. 重试条件
- **仅重试可恢复错误**
    - 区分**临时性错误**（如超时、503）和**永久性错误**（如404、401）。
    - *实现方式*：通过错误码或异常类型过滤。

- **避免重复重试已失败操作**
    - 对**幂等操作**（如GET、PUT、DELETE）可安全重试；对**非幂等操作**（如POST）需谨慎。
    - *解决方案*：
        - 使用唯一请求ID去重（如数据库操作加事务ID）。
        - 依赖服务支持幂等接口（如支付接口提供`idempotency_key`）。

### 3. 重试上限
- **最大重试次数**
    - 避免无限重试导致资源耗尽（如线程阻塞、连接泄漏）。
    - *推荐值*：3-5次（根据业务容忍度调整）。

- **全局重试预算**
    - 在分布式系统中，限制单个请求或服务的总重试次数（如跨微服务调用链）。
    - *示例*：Spring Retry的`@Retryable`支持`maxAttempts`参数。

### 4. 重试通知与监控
- **记录重试事件**
    - 通过日志或Metrics监控重试频率、成功率、失败原因。
    - *关键指标*：重试率（`retries/total_requests`）、重试成功率。

- **告警阈值**
    - 当重试率超过阈值（如10%）时触发告警，提示潜在故障。

---

## 重试机制的常见实现方式
### 1. 编程语言级实现
- **同步重试**（适合简单场景）
  ```python
  # Python示例：固定间隔重试
  import time
  from requests.exceptions import RequestException

  def call_with_retry(max_retries=3, delay=1):
      for i in range(max_retries):
          try:
              return requests.get("https://example.com")
          except RequestException as e:
              if i == max_retries - 1:
                  raise
              time.sleep(delay)
  ```

- **异步重试**（适合高并发场景）
  ```javascript
  // Node.js示例：使用async-retry库
  const retry = require('async-retry');

  async function fetchWithRetry() {
      await retry(
          async (bail) => {
              const res = await fetch("https://example.com");
              if (!res.ok) {
                  throw new Error(`HTTP error: ${res.status}`);
              }
              return res.json();
          },
          { retries: 3, minTimeout: 1000 }
      );
  }
  ```

### 2. 框架/中间件集成
- **Spring Retry**（Java）
  ```java
  @Retryable(value = {RemoteAccessException.class}, maxAttempts = 3, backoff = @Backoff(delay = 1000))
  public String callExternalService() {
      // 调用可能失败的远程服务
  }
  ```

- **Resilience4j**（Java）
  ```java
  RetryConfig config = RetryConfig.custom()
      .maxAttempts(3)
      .waitDuration(Duration.ofSeconds(1))
      .build();

  Retry retry = Retry.of("serviceA", config);

  Supplier<String> decoratedSupplier = Retry
      .decorateSupplier(retry, () -> callExternalService());
  ```

- **gRPC**（内置重试策略）
  ```yaml
  # gRPC客户端配置（YAML）
  retryPolicy:
    maxAttempts: 3
    initialBackoff: 0.1s
    maxBackoff: 1s
    backoffMultiplier: 2
    retryableStatusCodes: [UNAVAILABLE, DEADLINE_EXCEEDED]
  ```

### 3. 服务网格/API网关
- **Envoy Proxy**（通过Retry Policy）
  ```yaml
  # Envoy路由配置
  retries:
    retry_on: connect-failure,refused-stream,unavailable,cancelled,retriable-status-codes
    num_retries: 3
    per_try_timeout: 0.25s
  ```

- **Kong Gateway**（插件支持）
  ```lua
  -- Kong插件配置（Lua）
  local retries_plugin = {
      name = "retries",
      config = {
          attempts = 3,
          status_codes = { 502, 503, 504 }
      }
  }
  ```

## 重试机制的常见问题与解决方案

| **问题**                | **原因**            | **解决方案**                |
|-----------------------|-------------------|-------------------------|
| **重试风暴（Retry Storm）** | 大量请求同时重试，加剧系统负载   | 使用指数退避+抖动，限制并发重试数       |
| **非幂等操作重复执行**         | 如重复扣款、重复创建订单      | 依赖服务实现幂等接口，或客户端生成唯一ID去重 |
| **重试超时未释放资源**         | 重试期间未关闭连接、未回滚事务   | 确保重试逻辑在`finally`块中释放资源  |
| **分布式环境下重试不一致**       | 各节点重试策略不同导致行为差异   | 统一重试配置（如通过服务网格下发策略）     |
| **误重试永久性错误**          | 未正确过滤错误类型（如重试404） | 明确重试条件（如仅重试5xx错误）       |

## 重试机制的最佳实践
1. **区分错误类型**：仅对临时性错误重试，避免重试业务逻辑错误。
2. **限制重试范围**：在分布式系统中，避免跨服务链的重试放大故障（如A→B→C均重试3次，总请求数膨胀至27次）。
3. **结合熔断机制**：当重试失败率超过阈值时，触发熔断停止重试（如Hystrix/Resilience4j）。
4. **监控重试效果**：通过Metrics分析重试成功率，优化重试策略参数。
5. **用户透明化**：对终端用户隐藏重试逻辑，仅返回最终结果或友好错误提示。

---

## **总结**
重试机制是提升系统容错能力的关键手段，但其设计需谨慎平衡**成功率**与**系统稳定性**。核心原则包括：
- **精准重试**：仅针对可恢复错误，避免滥用。
- **渐进退避**：通过指数退避+抖动分散重试压力。
- **有限重试**：设置合理的重试次数上限。
- **幂等保障**：确保非幂等操作的安全执行。

结合超时、熔断、限流等机制，重试可构建出**弹性架构**，使系统在故障面前保持优雅降级而非崩溃。