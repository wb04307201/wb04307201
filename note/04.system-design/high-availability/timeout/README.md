# 超时

在分布式系统中，**超时**是一种基础且关键的容错策略，用于限制请求的等待时间，防止因依赖服务不可用或响应缓慢导致资源耗尽或级联故障。以下是超时策略的详细介绍，涵盖原理、类型、配置要点、风险控制及实践工具：

## 一、超时的核心原理
超时的本质是**为请求设置一个最大等待时间阈值**。当请求在指定时间内未完成时，系统主动终止请求并返回失败（或降级响应），避免线程、连接、内存等资源被无限期占用。其核心目标包括：
- **防止资源泄漏**：如HTTP连接、数据库连接池耗尽。
- **避免级联故障**：防止下游服务的慢响应导致上游服务堆积请求。
- **提升用户体验**：快速失败比无限等待更友好（如返回“服务繁忙，请稍后重试”）。

## 二、超时的类型与场景
### 1. 连接超时（Connection Timeout）
- **定义**：建立网络连接的最大等待时间（如TCP握手、HTTP连接）。
- **适用场景**：
    - 依赖的第三方服务网络延迟高（如跨机房调用）。
    - 防止因DNS解析失败或网络分区导致连接阻塞。
- **示例**：HTTP客户端设置`connectTimeout=3s`。

### 2. 读取超时（Read Timeout）
- **定义**：等待响应数据的最大时间（从连接建立成功到收到第一个字节或完整响应）。
- **适用场景**：
    - 依赖服务处理时间过长（如复杂查询、大数据计算）。
    - 防止因下游服务逻辑死循环或资源竞争导致响应延迟。
- **示例**：数据库查询设置`socketTimeout=5s`。

### 3. 写入超时（Write Timeout）
- **定义**：发送请求数据的最大时间（如上传大文件、批量写入）。
- **适用场景**：
    - 避免因网络拥塞或服务端处理能力不足导致写入阻塞。
- **示例**：Kafka生产者设置`request.timeout.ms=10s`。

### 4. 全局事务超时
- **定义**：分布式事务（如TCC、Saga）的总执行时间限制。
- **适用场景**：
    - 防止长事务占用锁或资源（如订单支付超时自动回滚）。
- **示例**：Seata事务管理器设置`txTimeout=30s`。

## 三、超时配置的关键要点
### 1. 动态调整策略
- **静态超时**：固定值（如所有请求超时5秒），简单但缺乏灵活性。
- **动态超时**：根据历史响应时间分布动态计算（如P99延迟+缓冲时间）。
    - **实现方式**：
        - 滑动窗口统计：记录最近N次请求的延迟，取P99或P95值。
        - 外部配置中心：通过Apollo、Nacos等动态修改超时参数。
        - 自适应算法：如根据系统负载（CPU、内存）动态调整超时时间。

### 2. 分级超时
- **按服务重要性分级**：
    - 核心服务（如支付）设置较短超时（如2秒）。
    - 非核心服务（如日志上报）设置较长超时（如10秒）。
- **按操作类型分级**：
    - 查询操作：超时较短（如1秒）。
    - 写入操作：超时较长（如3秒）。
- **示例配置**：
  ```yaml
  services:
    payment:
      connectTimeout: 1s
      readTimeout: 2s
    logging:
      connectTimeout: 5s
      readTimeout: 10s
  ```

### 3. 超时与重试的协同
- **关系**：超时是重试的前提（只有超时失败才会触发重试）。
- **配置建议**：
    - 超时时间应小于重试的总间隔（如首次超时1秒，重试间隔2秒）。
    - 避免超时过长导致重试无效（如超时10秒+重试3次=总耗时30秒）。
- **示例逻辑**：
  ```java
  for (int i = 0; i < maxRetries; i++) {
      try {
          return callServiceWithTimeout(timeoutMs);
      } catch (TimeoutException e) {
          if (i == maxRetries - 1) throw e;
          Thread.sleep(backoffDelay);
      }
  }
  ```

## 四、超时的风险与控制
### 1. 误触发风险
- **问题**：超时设置过短可能导致正常请求被错误终止（如依赖服务临时负载高但可恢复）。
- **解决方案**：
    - 结合熔断器：当错误率过高时动态延长超时时间。
    - 使用降级策略：超时后返回缓存数据或默认值。
    - 监控超时率：通过Prometheus+Grafana跟踪超时请求比例。

### 2. 级联故障
- **问题**：下游服务超时可能导致上游服务线程堆积（如Tomcat线程池耗尽）。
- **解决方案**：
    - 异步化调用：使用Future、CompletableFuture或Reactor模式。
    - 限流：结合Sentinel或Resilience4j限制并发请求数。
    - 快速失败：超时后立即释放资源，不等待重试结果。

### 3. 数据不一致
- **问题**：超时后无法确定请求是否生效（如数据库更新超时，但实际已成功）。
- **解决方案**：
    - 幂等设计：通过唯一ID确保重复请求无副作用。
    - 补偿机制：超时后查询状态或发起反向操作（如支付超时后查询订单状态）。
    - 分布式事务：使用TCC或Saga模式保证最终一致性。

## 五、实践工具与代码示例
### 1. HTTP客户端超时配置
- **OkHttp**：
  ```java
  OkHttpClient client = new OkHttpClient.Builder()
      .connectTimeout(3, TimeUnit.SECONDS)
      .readTimeout(5, TimeUnit.SECONDS)
      .writeTimeout(5, TimeUnit.SECONDS)
      .build();
  ```
- **Feign**：
  ```yaml
  feign:
    client:
      config:
        default:
          connectTimeout: 3000
          readTimeout: 5000
  ```

### 2. RPC框架超时配置
- **gRPC**：
  ```java
  ManagedChannel channel = ManagedChannelBuilder.forAddress("localhost", 8080)
      .usePlaintext()
      .enableRetry()
      .maxRetryAttempts(3)
      .defaultLoadBalancingPolicy("round_robin")
      .build();
  // 调用时设置超时
  Stub stub = ServiceGrpc.newStub(channel);
  stub.withDeadlineAfter(5, TimeUnit.SECONDS).callMethod(request, observer);
  ```
- **Dubbo**：
  ```xml
  <dubbo:reference id="userService" interface="com.example.UserService" timeout="3000" />
  ```

### 3. 数据库超时配置
- **MySQL JDBC**：
  ```properties
  spring.datasource.hikari.connection-timeout=30000
  spring.datasource.hikari.socket-timeout=60000
  ```
- **MongoDB**：
  ```java
  MongoClientSettings settings = MongoClientSettings.builder()
      .applyToConnectionPoolSettings(builder -> 
          builder.maxWaitTime(120, TimeUnit.SECONDS))
      .applyToSocketSettings(builder -> 
          builder.connectTimeout(10, TimeUnit.SECONDS))
      .build();
  ```

## 六、最佳实践总结
1. **分级超时**：根据服务重要性和操作类型设置差异化超时。
2. **动态调整**：结合P99延迟和系统负载动态计算超时值。
3. **协同策略**：超时需与重试、熔断、限流协同使用。
4. **幂等保障**：超时后需处理可能的重复请求。
5. **监控告警**：实时跟踪超时率，及时发现系统性问题。
6. **异步优先**：对长耗时操作优先使用异步调用，避免同步阻塞。