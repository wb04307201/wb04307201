# 熔断

断（Circuit Breaker）是一种分布式系统中的容错机制，用于防止系统因依赖服务故障而引发连锁反应，导致整个系统崩溃。它通过在服务调用链中插入一个“熔断器”，在检测到异常时主动切断调用，避免资源耗尽或雪崩效应。以下是详细解释：

> 类似电路中的保险丝：当电流过大（服务过载或故障）时，保险丝熔断以保护电路，避免火灾。故障修复后，保险丝可恢复连接。


## 熔断器的工作状态
熔断器通常有三种状态，通过**状态机**管理：

| 状态       | 触发条件                          | 行为                                                                 |
|------------|-----------------------------------|----------------------------------------------------------------------|
| **Closed** （闭合） | 初始状态，服务调用正常            | 正常转发请求，同时统计失败率（如连续失败次数、错误率阈值）。           |
| **Open**   （断开） | 失败率超过阈值（如50%错误率）    | 直接拒绝请求，返回降级响应（如默认值、缓存数据、错误提示）。           |
| **Half-Open**（半开） | 断开一段时间后（如5秒）           | 尝试放行部分请求（如10%），若成功则恢复Closed状态，否则重回Open状态。  |


### 熔断器的关键参数
- **失败阈值**：触发熔断的错误率（如连续3次失败或50%请求失败）。
- **熔断时长**：Open状态持续的时间（如5秒），之后进入Half-Open状态。
- **恢复条件**：Half-Open状态下成功请求的比例（如80%成功则恢复）。
- **超时时间**：请求的最大等待时间，避免长时间阻塞。


### **熔断的实现方式**
#### **1. 客户端熔断（推荐）**
- **适用场景**：微服务架构中，服务调用方自行实现熔断。
- **工具示例**：
    - **Hystrix**（Netflix开源，已停更）：通过`@HystrixCommand`注解定义熔断逻辑。
    - **Resilience4j**（Java生态）：提供更轻量的熔断、限流、重试组合方案。
    - **Sentinel**（阿里开源）：支持流量控制、熔断降级、系统自适应保护。
    - **Spring Cloud Circuit Breaker**：统一抽象层，支持多种实现（Resilience4j、Sentinel等）。

**代码示例（Resilience4j）**：
```java
// 配置熔断器
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50) // 失败率阈值50%
    .waitDurationInOpenState(Duration.ofSeconds(5)) // Open状态持续5秒
    .build();

CircuitBreaker circuitBreaker = CircuitBreaker.of("myService", config);

// 使用熔断器包装请求
Supplier<String> decoratedSupplier = CircuitBreaker
    .decorateSupplier(circuitBreaker, () -> callRemoteService());

try {
    String result = decoratedSupplier.get();
} catch (Exception e) {
    // 熔断触发时，快速失败并返回降级逻辑
    String fallback = "Fallback response";
    log.error("Service unavailable, using fallback: {}", fallback);
}
```

#### **2. 服务端熔断**
- **适用场景**：服务提供方主动保护自身，避免被调用方拖垮。
- **实现方式**：
    - **线程池隔离**：为每个依赖服务分配独立线程池，超时后直接拒绝新请求。
    - **信号量隔离**：通过计数器限制并发请求数（适用于轻量级操作）。
    - **API网关熔断**：在网关层（如Kong、Spring Cloud Gateway）配置熔断规则。

## 现成的解决⽅案
Spring Cloud 官⽅⽬前推荐的熔断器组件如下：Hystrix、Resilience4J、Alibaba Sentinel

| 特性              | Alibaba Sentinel            | Hystrix         | Resilience4j        |
|-----------------|-----------------------------|-----------------|---------------------|
| 隔离策略            | 信号量隔离（并发控制）                 | 线程池隔离/信号量隔离     | 信号量隔离               |
| 熔断降级策略          | 基于慢调用比例、异常比例、异常数            | 基于异常比例          | 基于异常比例、响应时间         |
| 实时统计实现          | 滑动窗口（LeapArray）             | 滑动窗口（基于 RxJava） | Ring Bit Buffer     |
| 动态规则配置          | 支持多种数据源                     | 支持多种数据源         | 有限支持                |
| 扩展性             | 多个扩展点                       | 插件的形式           | 接口的形式               |
| 基于注解的支持         | 支持                          | 支持              | 支持                  |
| 限流              | 基于 QPS，支持基于调用关系的限流          | 有限的支持           | Rate Limiter        |
| 流量整形            | 支持预热模式与匀速排队控制效果             | 不支持             | 简单的 Rate Limiter 模式 |
| 系统自适应保护         | 支持                          | 不支持             | 不支持                 |
| 多语言支持           | Java/Go/C++                 | Java            | Java                |
| Service Mesh 支持 | 支持 Envoy/Istio              | 不支持             | 不支持                 |
| 控制台             | 提供开箱即用的控制台，可配置规则、实时监控、机器发现等 | 简单的监控查看         | 不提供控制台，可对接其它监控系统    |

### 1. Alibaba Sentinel与Spring Cloud Alibaba集成良好
### 2. Hystrix、Resilience4J与Spring Cloud集成良好
### 3. Hystrix已停止维护的，仅作兼容支持
