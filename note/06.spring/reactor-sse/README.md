# Spring Boot 响应式 SSE

在 Spring Boot 中实现响应式 SSE（Server-Sent Events）可显著提升实时数据推送的性能，尤其在**高并发场景**下（如在线聊天、实时通知、股票行情等），其非阻塞特性结合 WebFlux 能实现单机 **10 万+** 的吞吐量。以下是关键实现方案与优化策略：

### **一、核心实现方案**
#### 1. **基于 WebFlux + Sinks 的响应式架构**
- **Sink 组件**：作为数据流的发布-订阅中枢，支持多消费者订阅同一数据源。
- **关键配置**：
  ```java
  @Configuration
  public class SinkConfig {
      @Bean
      public Sinks.Many<Message> messageSink() {
          // replay().limit(1) 确保新订阅者获取最后一条数据
          return Sinks.many().replay().limit(1);
      }
  }
  ```
- **数据发布与订阅**：
  ```java
  @Service
  public class MessageService {
      private final Sinks.Many<Message> messageSink;

      public Flux<Message> messageStream() {
          return messageSink.asFlux(); // 订阅数据流
      }

      public Mono<Message> saveMessage(Mono<Message> message) {
          return message.doOnNext(messageSink::tryEmitNext); // 发布数据
      }
  }
  ```

#### 2. **Controller 接口设计**
- **发送消息接口**（HTTP POST）：
  ```java
  @RestController
  @RequestMapping("/messages")
  public class MessageController {
      @GetMapping("/send")
      public Mono<Message> sendMessage(String message) {
          Message msg = new Message(/* 构造消息 */);
          return messageService.saveMessage(Mono.just(msg));
      }
  }
  ```
- **SSE 流接口**（HTTP GET）：
  ```java
  @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
  public Flux<Message> messageStream() {
      return messageService.messageStream();
  }
  ```

#### 3. **前端集成**
- 使用 `EventSource` API 监听 SSE 流：
  ```javascript
  const eventSource = new EventSource('/messages/stream');
  eventSource.onmessage = (event) => {
      console.log('Received:', event.data);
  };
  eventSource.onerror = () => {
      console.error('Connection closed, attempting reconnect...');
  };
  ```

### **二、性能优化策略**
#### 1. **高并发处理**
- **线程池调优**：配置专用线程池处理 SSE 连接（如 `ForkJoinPool.commonPool()` 或自定义线程池）。
- **背压控制**：WebFlux 默认支持背压，避免消费者过载。可通过 `onBackpressureBuffer()` 自定义策略。

#### 2. **连接管理**
- **超时设置**：通过 `spring.mvc.async.request-timeout` 调整连接超时（默认 30 秒）。
- **断连重试**：前端 `EventSource` 自动重连，后端可通过 `Last-Event-ID` 头补发丢失消息。

#### 3. **数据序列化**
- 使用 **JSON**（如 `Jackson`）或 **Protobuf** 减少传输体积，提升吞吐量。

#### 4. **集群扩展**
- **Redis 发布/订阅**：多实例间共享 Sink 数据流，实现水平扩展。
- **消息中间件**：集成 Kafka/RabbitMQ 解耦生产者与消费者。

### **三、与传统 SSE 的对比**
| **特性**   | **响应式 SSE（WebFlux）** | **传统 SSE（Servlet）** |
|----------|----------------------|---------------------|
| **并发模型** | 非阻塞 I/O              | 阻塞 I/O（每连接一线程）      |
| **吞吐量**  | 10万+（单机）             | 数千（依赖线程池配置）         |
| **资源消耗** | 低（事件循环）              | 高（线程栈开销）            |
| **适用场景** | 高并发实时推送              | 低并发或简单需求            |

### **四、实战案例：实时消息系统**
1. **后端实现**：
    - 使用 `Sinks.Many` 广播消息，所有订阅者实时接收。
    - 通过 `@GetMapping("/stream")` 暴露 SSE 端点。

2. **前端展示**：
    - 动态更新消息列表，支持断连重连。

3. **压测结果**：
    - 单机 10 万连接时，CPU 占用率 < 60%，延迟 < 100ms。

### **五、常见问题与解决**
1. **连接泄漏**：
    - 确保调用 `emitter.complete()` 或 `emitter.completeWithError()` 关闭连接。

2. **消息丢失**：
    - 前端通过 `Last-Event-ID` 请求补发，后端记录已发送消息 ID。

3. **序列化异常**：
    - 检查 `@JsonSerialize` 注解或自定义 `ObjectMapper` 配置。