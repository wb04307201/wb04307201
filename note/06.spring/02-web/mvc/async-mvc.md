# 异步 MVC：Callable / DeferredResult / SSE

> 最后更新: 2026-06-14
> ⬅️ [返回 MVC 总览](README.md) | [02 Web 层](../README.md)

Spring MVC 同步模型下，每个请求占用一个 Servlet 线程（默认 Tomcat 200）。**异步 MVC** 通过 `Callable` / `DeferredResult` / `SseEmitter` 把"等待下游完成"的时间释放回线程池，**显著提升并发吞吐**。本文覆盖 5 种核心 API、与 WebFlux 的边界、`spring.mvc.async` 配置。

---

## 🎯 一句话定位

**异步 MVC = "释放工作线程，等下游就绪再回写响应"**——Servlet 容器线程先归还，Controller 返回异步句柄；下游完成后用该句柄写回。**本质是把"等"从 Servlet 线程挪到业务线程**，让少量 Servlet 线程服务更多请求。

---

## 一、5 种异步 API 速览

| API | 用途 | 线程模型 |
|-----|------|----------|
| `Callable<T>` | 简单异步执行 | Spring 用 `TaskExecutor` 执行 |
| `DeferredResult<T>` | 跨组件（线程/消息）传递结果 | 完全自定义 |
| `WebAsyncTask<T>` | `Callable` 的加强版，可配超时/Executor | 同 Callable |
| `ResponseBodyEmitter` | 多次写响应（chunked） | 自定义 |
| `SseEmitter` | `ResponseBodyEmitter` 的 SSE 特化 | 自定义 |

---

## 二、Callable（最简单）

```java
@GetMapping("/users/{id}")
public Callable<User> getById(@PathVariable Long id) {
    return () -> userService.findByIdBlocking(id);  // 工作线程内执行
}
```

- Spring 用默认 `TaskExecutor`（或自定义 `WebMvcConfigurer.configureAsyncSupport`）执行 `Callable`。
- Servlet 线程立即释放；Callable 执行完成后，Spring 重新申请一个 Servlet 线程回写响应。

> **适用场景**：单次简单异步、临时把慢调用挪出 Servlet 线程。

---

## 三、DeferredResult（跨组件协作）

```java
@GetMapping("/orders/{id}")
public DeferredResult<Order> getOrder(@PathVariable String id) {
    DeferredResult<Order> dr = new DeferredResult<>(5_000L, "timeout");  // 5s 超时
    orderService.findAsync(id)
            .subscribe(
                    dr::setResult,      // 成功
                    dr::setErrorResult  // 失败
            );
    return dr;
}
```

- `DeferredResult` 可在**多个组件/线程**间传递（订单服务订阅消息、MQ 消费者回调等）。
- 超时 / 完成 / 异常三种终止路径都必须显式处理（`setResult` / `setErrorResult`）。

> **适用场景**：上游 Controller 等待下游异步事件（消息回调、跨服务推送）。

---

## 四、ResponseBodyEmitter（多次写响应）

```java
@GetMapping("/stream")
public ResponseBodyEmitter stream() {
    ResponseBodyEmitter emitter = new ResponseBodyEmitter(0L); // 0 = 不超时
    executor.submit(() -> {
        try {
            for (int i = 0; i < 10; i++) {
                emitter.send("data-" + i);
                emitter.send("\n");
                Thread.sleep(500);
            }
            emitter.complete();
        } catch (Exception e) {
            emitter.completeWithError(e);
        }
    });
    return emitter;
}
```

- 多次 `send()` → 客户端实时收到 chunked 响应。
- 底层 HTTP 响应 Content-Type 仍是 `application/octet-stream`（或自定义）。

> **适用场景**：大文件分段下载、自定义流式协议。

---

## 五、SseEmitter（SSE 实时推送）

> SSE 的 MVC 实现——如果不需要全栈响应式，**SseEmitter 是最轻量的方案**。

```java
@GetMapping(value = "/sse/orders", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public SseEmitter sse() {
    SseEmitter emitter = new SseEmitter(0L);
    executor.submit(() -> {
        try {
            for (int i = 0; i < 10; i++) {
                emitter.send(SseEmitter.event()
                        .id(String.valueOf(i))
                        .name("order")
                        .data(new OrderEvent(i, "evt-" + i)));
                Thread.sleep(1000);
            }
            emitter.complete();
        } catch (Exception e) {
            emitter.completeWithError(e);
        }
    });
    return emitter;
}
```

- 同样支持断连清理：`emitter.onCompletion(() -> log.info("done"))` / `onTimeout(...)`。
- 与 WebFlux + SSE 的对比：[SSE 实时推送（WebFlux）](../webflux/sse.md) 是**全响应式**方案；本篇是**MVC 同步栈**的 SSE 实现。

> **适用场景**：实时通知、进度推送、聊天；并发不需十万级时用 `SseEmitter`，否则上 WebFlux。

---

## 六、配置：spring.mvc.async

```yaml
spring:
  mvc:
    async:
      request-timeout: 30s       # 异步请求超时（默认 30s，0 = 关闭）
      task-execution:
        pool:
          core-size: 8
          max-size: 64
          queue-capacity: 200
          thread-name-prefix: mvc-async-
```

或者 Java Config：

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void configureAsyncSupport(AsyncSupportConfigurer configurer) {
        configurer.setDefaultTimeout(30_000L);
        configurer.setTaskExecutor(new ThreadPoolTaskExecutor() {{
            setCorePoolSize(8);
            setMaxPoolSize(64);
            setQueueCapacity(200);
            setThreadNamePrefix("mvc-async-");
            initialize();
        }});
    }
}
```

> **超时**：超时的 `DeferredResult` 会回调 `setErrorResult`；未设置则回 503。

---

## 七、异常处理

异步请求的异常处理与同步略有不同：

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler
    public ResponseEntity<ApiError> handleAsync(AsyncRequestTimeoutException e) {
        return ResponseEntity.status(503).body(new ApiError("ASYNC_TIMEOUT", "请求超时"));
    }
}
```

> 异步请求**不会**自动进 `@ExceptionHandler`——必须在回调内（`setErrorResult` / `onError`）显式传响应。

---

## 八、异步 MVC vs WebFlux

| 维度 | 异步 MVC | WebFlux |
|------|----------|---------|
| **编程模型** | 命令式 + 异步句柄 | 声明式 Mono/Flux |
| **底层** | Servlet 3.1 异步 | Netty / Servlet 3.1 |
| **线程模型** | 1 请求 = 1 Servlet 线程（短时间） | EventLoop 全复用 |
| **阻塞 IO 兼容** | ✅（用 TaskExecutor 隔离） | ❌（需切到 boundedElastic） |
| **背压** | ❌ | ✅ |
| **学习成本** | 低 | 中 |
| **典型并发量** | 千~万 | 万~十万+ |
| **何时选** | 现有 MVC 项目需提升并发 | 高并发 I/O / 长连接 / 流式 |

> **实战分工**：
> - 并发从 200 提升到 2000 → **异步 MVC** 即可；
> - 并发上 10 万 → **WebFlux**。

---

## 九、最佳实践

1. **Async MVC 不是银弹**：下游阻塞时间越长越好，但要监控 `TaskExecutor` 队列。
2. **必须显式 complete**：`emitter.complete()` / `setResult` 不调会导致 Servlet 线程泄漏。
3. **超时设上限**：永远不要 `0L`（不超时）除非业务真的需要——避免 DoS 风险。
4. **限流**：高频 SSE 端点用 Resilience4j 限流，防止连接风暴。
5. **统一异常**：用 `AsyncUncaughtExceptionHandler`（`@Async`）/ 在回调里 `setErrorResult`，避免 500 裸奔。

---

## 相关章节

- ⬅️ [返回 MVC 总览](README.md)
- [SSE 实时推送（WebFlux）](../webflux/sse.md) — 响应式 SSE 方案
- [异常处理](exception-resolver.md) — 异步异常
- [组件对比与场景](components-order.md) — 异步在执行链中的位置
