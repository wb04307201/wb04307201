# CompletableFuture 异步编排深度剖析

> 一句话：CompletableFuture 将 Future 与 CompletionStage 融合，提供声明式异步任务编排能力，让链式回调、组合聚合、异常兜底成为可能。

---

## 一、核心原理

CompletableFuture 同时实现 `Future<V>` 和 `CompletionStage<V>` 两个接口，兼具"获取结果"与"事件驱动回调"双重身份。

- **Future**：提供 `get()`、`isDone()` 等阻塞查询能力。
- **CompletionStage**：定义 40+ 个默认方法，支持 then/compose/combine/handle 等编排原语。

底层通过 **Unsafe CAS + Volatile** 维护完成状态与结果，当某个阶段完成时触发注册的依赖动作（Action/Function/Consumer），形成有向无环图（DAG）式的执行流。

```mermaid
flowchart LR
    A[supplyAsync] --> B[thenApply]
    B --> C[thenCompose]
    C --> D[thenCombine]
    D --> E[handle]
    E --> F[join/get]
```

**线程模型**：

- 未显式传入 Executor 时，默认使用 `ForkJoinPool.commonPool()`，其并行度为 CPU 核数 -1。
- 适合轻量 CPU 密集型任务；IO 密集型应传入自定义线程池，避免 commonPool 被占满导致全局退化。
- Java 21 引入虚拟线程后，可用 `Executors.newVirtualThreadPerTaskExecutor()` 作为 Executor，每个异步任务运行在独立虚拟线程上，彻底消除线程池调参烦恼。

---

## 二、方法分类

CompletableFuture 的方法可按语义分为以下几类，命名规则遵循 `<转换类型><同步/异步>` 模式：

| 类别 | 方法签名示例 | 语义 |
|------|-------------|------|
| **thenApply** | `thenApply(Function<T,U>)` | 对结果做映射，返回 `CompletableFuture<U>`，等价于 Stream.map |
| **thenCompose** | `thenCompose(Function<T,CompletionStage<U>>)` | 扁平化嵌套 Future，等价于 Stream.flatMap |
| **thenCombine** | `thenCombine(Other, BiFunction)` | 等待两个独立 CompletableFuture 都完成后合并结果 |
| **thenAccept** | `thenAccept(Consumer<T>)` | 消费结果，无返回值，返回 `CompletableFuture<Void>` |
| **thenRun** | `thenRun(Runnable)` | 不关心结果，仅在当前阶段完成后执行副作用 |
| **allOf** | `allOf(CompletableFuture<?>... cfs)` | 等待所有 CompletableFuture 完成，返回 `CompletableFuture<Void>` |
| **anyOf** | `anyOf(CompletableFuture<?>... cfs)` | 任一 CompletableFuture 完成即返回，返回 `CompletableFuture<Object>` |
| **whenComplete** | `whenComplete(BiConsumer<T,Throwable>)` | 正常或异常都会触发，无法转换结果类型 |
| **exceptionally** | `exceptionally(Function<Throwable,T>)` | 仅在异常时触发，提供降级值，类似 try-catch |
| **handle** | `handle(BiFunction<T,Throwable,U>)` | 正常或异常都会触发，且可转换结果类型，最灵活 |

### thenApply vs thenCompose vs thenApplyMany

- **thenApply**：输入 T，输出 U，包裹为 `CompletableFuture<U>`。适用于纯函数转换。
- **thenCompose**：输入 T，输出 `CompletionStage<U>`，用于串联两个异步操作，避免 `CompletableFuture<CompletableFuture<U>>` 嵌套。
- **thenApplyMany**（Java 9+）：批量扁平化多个 CompletionStage，处理 Fan-in 场景的 FlatMap 语义。

### thenCombine 双路合并

```java
CompletableFuture<String> cf1 = CompletableFuture.supplyAsync(() -> "Hello");
CompletableFuture<String> cf2 = CompletableFuture.supplyAsync(() -> "World");
cf1.thenCombine(cf2, (s1, s2) -> s1 + " " + s2)
   .thenAccept(System.out::println); // Hello World
```

### allOf vs anyOf

- **allOf**：常用于"等待 N 个微服务全部响应"场景，需手动提取各 Future 的结果（因为返回 Void）。
- **anyOf**：常用于"多路冗余调用，取最快返回"的容错策略。

---

## 三、异常处理

CompletableFuture 提供三种异常处理机制，选择依据是**是否需要转换类型**与**是否区分正常路径**。

| 方法 | 触发条件 | 能否转换类型 | 典型场景 |
|------|---------|------------|---------|
| **exceptionally** | 仅异常 | 否（返回同类型 T） | 提供降级默认值 |
| **handle** | 正常+异常 | 是（T→U） | 统一封装 Result<T> |
| **whenComplete** | 正常+异常 | 否 | 记录日志、清理资源 |

### exceptionally：降级兜底

```java
CompletableFuture.supplyAsync(() -> {
    if (Math.random() > 0.5) throw new RuntimeException("fail");
    return 42;
}).exceptionally(ex -> {
    log.error("fallback due to: {}", ex.getMessage());
    return -1; // 降级值
});
```

### handle：统一收口

```java
.handle((result, ex) -> {
    if (ex != null) {
        return Result.fail(ex.getMessage());
    }
    return Result.success(result);
})
```

### whenComplete：旁路观察

```java
.whenComplete((result, ex) -> {
    // 不能修改 result，也不能吞掉 ex
    log.info("completed: result={}, error={}", result, ex);
})
```

**关键区别**：`exceptionally` 只拦截异常路径；`handle` 和 `whenComplete` 两条路径都走，但只有 `handle` 能改变返回类型。若需在 `whenComplete` 中重新抛出异常，需包裹为 CompletionException，否则会丢失原始堆栈。

---

## 四、实战示例

### 多接口并行调用 + 聚合结果

假设需要并行调用用户服务、订单服务、积分服务，三者全部返回后组装 VO：

```java
CompletableFuture<UserVO> userCf = CompletableFuture.supplyAsync(this::fetchUser, executor);
CompletableFuture<List<OrderVO>> orderCf = CompletableFuture.supplyAsync(this::fetchOrders, executor);
CompletableFuture<Integer> pointsCf = CompletableFuture.supplyAsync(this::fetchPoints, executor);

CompletableFuture<UserProfileVO> profileCf = userCf
    .thenCombine(orderCf, (user, orders) -> Tuple.of(user, orders))
    .thenCombine(pointsCf, (tuple, points) -> {
        UserVO user = tuple.getLeft();
        List<OrderVO> orders = tuple.getRight();
        return UserProfileVO.builder()
            .user(user)
            .orders(orders)
            .points(points)
            .build();
    });

UserProfileVO profile = profileCf.join(); // 阻塞等待最终结果
```

### 自定义线程池

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    16,                          // corePoolSize
    64,                          // maximumPoolSize
    60L, TimeUnit.SECONDS,       // keepAliveTime
    new LinkedBlockingQueue<>(1024),
    new ThreadFactoryBuilder().setNameFormat("async-cf-%d").build(),
    new ThreadPoolExecutor.CallerRunsPolicy()
);

CompletableFuture.supplyAsync(() -> doHeavyIO(), executor);
```

### 与虚拟线程配合（Java 21+）

```java
try (var vExecutor = Executors.newVirtualThreadPerTaskExecutor()) {
    CompletableFuture<String> cf = CompletableFuture.supplyAsync(() -> {
        // 每个任务运行在独立虚拟线程，无需担心线程池耗尽
        return httpClient.getString(url);
    }, vExecutor);
    String result = cf.join();
}
```

虚拟线程消除了 IO 密集型场景下调大线程池参数的经验主义，每个阻塞调用等价于一次 yield，操作系统层面几乎零开销。

---

## 五、常见陷阱

### 1. 默认用 ForkJoinPool.commonPool

未传 Executor 的 `supplyAsync` / `runAsync` 会使用 commonPool，其并行度 = CPU核数 - 1。若链中存在 IO 阻塞（如 HTTP 请求、DB 查询），会迅速占满线程，导致其他无关异步任务饥饿。**最佳实践：始终显式传入自定义 Executor**。

### 2. 异常被吞

若链路末端既没有 `join()` / `get()`，也没有 `exceptionally()` / `handle()`，异常会被静默丢弃。调试时应至少添加 `.whenComplete((r, ex) -> { if (ex != null) log.error(ex); })`。

### 3. 阻塞式 get vs 异步链

`get()` 是 Java 5 遗留 API，抛出受检异常且不可中断；`join()` 抛出非受检 CompletionException，更适合函数式风格。但二者都会阻塞当前线程，应尽量将后续逻辑放入 `thenApply` / `thenAccept` 异步链中，仅在边界处（如 Controller 返回前）才调用 `join()`。

### 4. thenCompose 与 thenApply 误用

```java
// 错误：产生嵌套 CompletableFuture<CompletableFuture<U>>
cf.thenApply(x -> asyncCall(x))

// 正确：扁平化
cf.thenCompose(x -> asyncCall(x))
```

### 5. 线程上下文丢失

异步回调运行在线程池线程中，ThreadLocal（如 MDC、SecurityContext）不会自动传递。需用 InheritableThreadLocal 或在提交任务前手动捕获上下文。

---

## 六、面试话术（30 秒版）

> CompletableFuture 实现了 Future 和 CompletionStage，支持声明式异步编排。核心方法分三类：thenApply 做映射、thenCompose 做扁平化串联、thenCombine 做双路合并；allOf 等待全部、anyOf 取最快。异常处理上，exceptionally 只兜底异常，handle 能统一收口并转换类型，whenComplete 只做旁路观察。关键注意两点：一是永远别用默认的 commonPool，要传自定义线程池或 Java 21 虚拟线程；二是异常若不 join 或 handle 会被静默吞掉，调试时务必加日志钩子。

---

## 七、交叉引用

- 主模块：[`01.java`](../../../01.java/) — Java 知识体系
- [CompletableFuture](../../../01.java/concurrency/completablefuture/README.md) — JUC CompletableFuture 详解
- [并发工具类](../../../01.java/concurrency/utilities/README.md) — JUC 包核心组件
