<!--
module:
  parent: 04.spring-backend
  slug: 04.spring-backend/02-boot/async-task-executor
  type: article
  category: 主模块子文章
  summary: Spring Boot @Async 异步任务底层即 ThreadPoolExecutor，本文梳理 AsyncConfigurer、TaskExecutorBuilder、ThreadPoolTaskExecutor 配置及与 JDK ThreadPoolExecutor 的关系
  depth: ⭐⭐⭐
-->

# Spring Boot @Async 异步任务与 TaskExecutor

> **一句话定位**：Spring Boot `@Async` 底层即 `ThreadPoolTaskExecutor`（封装自 JDK `ThreadPoolExecutor`）；本文梳理 Async 配置、线程池选型与 ThreadLocal 上下文传递。

> ⬅️ [返回 04 Spring Boot](../README.md)

---

## 一、为什么需要异步任务

在 Web 请求链路中，部分操作（发短信、写审计日志、调外部 API）不阻塞主线程即可完成。Spring 提供 `@Async` 注解 + `TaskExecutor` 抽象，让方法在独立线程池中执行，主线程立即返回。

```java
@Async("orderExecutor")
public void sendSms(Order order) {
    // 在 orderExecutor 线程池中执行
    smsClient.send(order.getPhone(), order.getContent());
}
```

## 二、Spring TaskExecutor 体系

| 抽象/实现 | 角色 |
|----------|------|
| `Executor` (JDK) | 最顶层接口，`execute(Runnable)` |
| `ExecutorService` (JDK) | 加 `submit()` / `shutdown()` / `Future` |
| `TaskExecutor` (Spring) | 标记接口，继承 `Executor`，无新增方法 |
| `AsyncTaskExecutor` (Spring) | 增加 `submit(Callable)` / `CompletableFuture` 提交 |
| `ThreadPoolTaskExecutor` (Spring) | **Spring 推荐的实现**，封装 JDK `ThreadPoolExecutor` |
| `SimpleAsyncTaskExecutor` (Spring) | 每次提交都 new Thread，**不池化**（生产禁用） |

## 三、ThreadPoolTaskExecutor 配置

```java
@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean("orderExecutor")
    public ThreadPoolTaskExecutor orderExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(200);
        executor.setKeepAliveSeconds(60);
        executor.setThreadNamePrefix("order-async-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(60);
        executor.initialize();
        return executor;
    }
}
```

## 四、TaskDecorator：ThreadLocal 上下文传递

Spring 提供了 `TaskDecorator` 钩子，可在任务提交时捕获父线程上下文，运行时恢复到子线程：

```java
executor.setTaskDecorator(runnable -> {
    Map<String, String> context = MDC.getCopyOfContextMap();   // 捕获 traceId
    RequestAttributes attrs = RequestContextHolder.getRequestAttributes();
    return () -> {
        try {
            if (context != null) MDC.setContextMap(context);
            if (attrs != null) RequestContextHolder.setRequestAttributes(attrs);
            runnable.run();
        } finally {
            MDC.clear();
            RequestContextHolder.resetRequestAttributes();
        }
    };
});
```

## 五、常见陷阱

| 陷阱 | 后果 | 正确做法 |
|------|------|---------|
| `@Async` 注解在同类内部调用 | 绕过 Spring 代理 → 同步执行 | 拆分到独立 Bean，或注入自身代理 |
| 默认使用 `SimpleAsyncTaskExecutor` | 每次 new Thread → OOM 风险 | 显式配置 `ThreadPoolTaskExecutor` |
| 队列容量默认 `Integer.MAX_VALUE` | 任务堆积 → OOM | `setQueueCapacity(200)` 显式指定 |
| 异步方法返回 `void` 抛异常 | 异常静默丢失 | 返回 `CompletableFuture<T>` + `.exceptionally(...)` |
| `ThreadLocal`（traceId）未传递 | 子线程日志无 traceId | 配置 `TaskDecorator` 或用 `TransmittableThreadLocal` |

---

> **核心要点**：Spring `@Async` 不是银弹，它只是把 JDK `ThreadPoolExecutor` 封装得更好用；底层原理仍受 7 大参数、4 种拒绝策略、3 种队列行为约束。**生产中必须显式配置线程池**，绝不能依赖默认行为。

---

## 反向链

- [Java 线程池（01.java-and-jvm）](../../../01.java-and-jvm/03-concurrency/thread-pool/README.md) — 底层 `ThreadPoolExecutor` 七大参数与拒绝策略
