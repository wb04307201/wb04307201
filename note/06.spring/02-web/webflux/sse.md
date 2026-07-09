# WebFlux 响应式 + SSE 实时推送

> ⬅️ [返回 02 Web 层](../README.md) | [WebFlux 总览](README.md)

WebFlux + SSE（Server-Sent Events）是 Spring 实现**高并发实时推送**的典型方案：在**在线聊天、实时通知、股票行情、IoT 数据上报**等场景下，响应式非阻塞 I/O 配合 SSE 单向流可实现单机 **10 万+** 长连接。本文先给出 WebFlux 速览，再讲 SSE 的核心实现与性能优化。

---

## 一、WebFlux 速览

> 仅给出与本篇强相关的概念铺垫，完整综述见 [WebFlux 总览](README.md)。

### 1. Reactor 三大核心

| 类型 | 形态 | 典型用途 |
|------|------|---------|
| `Mono<T>` | 0..1 个元素 | 单值查询、增删改 |
| `Flux<T>` | 0..N 个元素 | 流式查询、推送、订阅 |
| `Sinks` | 手动 emit 的"广播源" | 跨组件发布数据 |

### 2. 线程模型要点

- 默认运行在 **Netty 的 EventLoop**（少量线程）上，**非阻塞**。
- 一旦方法体内出现**阻塞调用**（JDBC、sleep、长时间计算），必须切换到 `Schedulers.boundedElastic()` 之类的工作线程池。
- 编排链路上**不要在订阅前阻塞**——`block()` 会把异步优势打回原形。

### 3. 背压（Backpressure）

- 响应式流天然支持**消费者驱动的流量控制**：消费者可声明 `request(n)` 告诉上游"我这次只处理 n 条"。
- SSE 场景下若消息频率远高于客户端处理速度，可使用 `onBackpressureBuffer()`、`onBackpressureDrop()` 或 `onBackpressureLatest()` 显式选择策略。

---

## 二、核心实现方案

### 1. 基于 WebFlux + Sinks 的响应式架构

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

### 2. Controller 接口设计

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

### 3. 前端集成

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

---

## 三、性能优化策略

### 1. 高并发处理

- **线程池调优**：配置专用线程池处理 SSE 连接（如 `ForkJoinPool.commonPool()` 或自定义线程池）。
- **背压控制**：WebFlux 默认支持背压，避免消费者过载。可通过 `onBackpressureBuffer()` 自定义策略。

### 2. 连接管理

- **超时设置**：通过 `spring.mvc.async.request-timeout` 调整连接超时（默认 30 秒）。
- **断连重试**：前端 `EventSource` 自动重连，后端可通过 `Last-Event-ID` 头补发丢失消息。

### 3. 数据序列化

- 使用 **JSON**（如 `Jackson`）或 **Protobuf** 减少传输体积，提升吞吐量。

### 4. 集群扩展

- **Redis 发布/订阅**：多实例间共享 Sink 数据流，实现水平扩展。
- **消息中间件**：集成 Kafka/RabbitMQ 解耦生产者与消费者。

---

## 四、与传统 SSE 的对比

| 特性 | 响应式 SSE（WebFlux） | 传统 SSE（Servlet） |
|------|----------------------|---------------------|
| **并发模型** | 非阻塞 I/O | 阻塞 I/O（每连接一线程） |
| **吞吐量** | 10万+（单机） | 数千（依赖线程池配置） |
| **资源消耗** | 低（事件循环） | 高（线程栈开销） |
| **适用场景** | 高并发实时推送 | 低并发或简单需求 |

---

## 五、实战案例：实时消息系统

1. **后端实现**：
   - 使用 `Sinks.Many` 广播消息，所有订阅者实时接收。
   - 通过 `@GetMapping("/stream")` 暴露 SSE 端点。
2. **前端展示**：
   - 动态更新消息列表，支持断连重连。
3. **压测结果**：
   - 单机 10 万连接时，CPU 占用率 < 60%，延迟 < 100ms。

---

## 六、常见问题与解决

1. **连接泄漏**：
   - 确保调用 `emitter.complete()` 或 `emitter.completeWithError()` 关闭连接。
2. **消息丢失**：
   - 前端通过 `Last-Event-ID` 请求补发，后端记录已发送消息 ID。
3. **序列化异常**：
   - 检查 `@JsonSerialize` 注解或自定义 `ObjectMapper` 配置。
4. **线程池被占满**：
   - 业务方法内若调用阻塞 IO（如 JDBC），使用 `subscribeOn(Schedulers.boundedElastic())` 切到工作线程。

---

## 相关章节

- 🆕 面试视角：[SSE vs WebSocket —— AI 对话为什么选 SSE](../../../13.split-hairs/02.computer-basics/sse-vs-websocket/README.md) — 协议对比 + 系统设计选型
- 🆕 协议深度：[SSE vs WebSocket 协议对比](../../../02.computer-basics/01-network/protocols/sse-vs-websocket/README.md) — 连接建立 + 帧格式 + 重连机制
- ⬅️ [返回 02 Web 层](../README.md)
- [WebFlux 总览](README.md) — Mono/Flux/背压/线程模型/选型决策
- [WebClient 调用](webclient.md) — 响应式 HTTP 客户端
- [R2DBC 响应式数据库](r2dbc.md) — 响应式持久层
- [WebFlux 测试](testing.md) — WebTestClient 与 @WebFluxTest
- [01 核心容器/异常处理](../../01-core/exception-handling.md) — 通用异常机制
