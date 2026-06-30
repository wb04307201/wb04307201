# CompletableFuture 完整笔记

## 一、Future 的局限性

在 Java 8 引入 `CompletableFuture` 之前，异步编程主要依赖 `java.util.concurrent.Future` 接口。然而 `Future` 存在明显的局限性，使其在实际开发中不够灵活。

### 1.1 get() 方法是阻塞的

```java
ExecutorService executor = Executors.newFixedThreadPool(3);
Future<String> future = executor.submit(() -> {
    Thread.sleep(2000);
    return "Hello from async task";
});

// get() 会阻塞当前线程，直到异步任务完成
String result = future.get(); // 阻塞等待
System.out.println(result);
```

| 问题 | 说明 |
|------|------|
| 同步阻塞 | `get()` 会阻塞调用线程，违背异步编程初衷 |
| 超时处理繁琐 | 需要捕获 `TimeoutException` 并自行处理 |
| 轮询低效 | 使用 `isDone()` 轮询会浪费 CPU 资源 |

### 1.2 无法组合多个 Future

```java
// 传统 Future 无法优雅地实现以下场景：
// 任务 A 完成后执行任务 B，再将结果合并
Future<Integer> a = executor.submit(() -> 10);
Future<Integer> b = executor.submit(() -> 20);

// 只能手动阻塞获取结果再计算
int sum = a.get() + b.get(); // 繁琐且容易出错
```

### 1.3 缺少异常传播机制

- `Future.get()` 将执行异常包装为 `ExecutionException`，需要嵌套解包
- 无法在异步链中声明式地处理异常
- 没有回调机制来优雅处理成功/失败两种路径

### 1.4 无法手动完成

`Future` 的结果只能由提交的任务本身产生，外部无法主动设置结果或取消后续流程。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

CompletableFuture 完整笔记 本应该很简单，在 Java 8 引入 `CompletableFuture` 之前，异步编程主要依赖 `java.util.concurrent.Future` 接口。然而 `Future` 存在明显的局限性，使其在实际开发中不够灵活

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 二、CompletableFuture 基本用法

`CompletableFuture` 实现了 `Future` 和 `CompletionStage` 两个接口，既兼容传统 `Future` 的使用方式，又提供了强大的组合能力。

### 2.1 创建方式对比

| 方法 | 返回值 | 适用场景 |
|------|--------|----------|
| `CompletableFuture.completedFuture(value)` | `CompletableFuture<U>` | 创建一个已完成的 Future |
| `CompletableFuture.runAsync(Runnable)` | `CompletableFuture<Void>` | 异步执行无返回值的任务 |
| `CompletableFuture.runAsync(Runnable, Executor)` | `CompletableFuture<Void>` | 指定线程池执行无返回值任务 |
| `CompletableFuture.supplyAsync(Supplier<U>)` | `CompletableFuture<U>` | 异步执行有返回值的任务 |
| `CompletableFuture.supplyAsync(Supplier<U>, Executor)` | `CompletableFuture<U>` | 指定线程池执行有返回值任务 |

### 2.2 supplyAsync — 有返回值的异步任务

```java
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    // 模拟耗时操作
    try { Thread.sleep(1000); } catch (InterruptedException e) {}
    return "Hello CompletableFuture";
});

// 使用默认 ForkJoinPool.commonPool() 执行
System.out.println(future.get()); // Hello CompletableFuture
```

### 2.3 runAsync — 无返回值的异步任务

```java
CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
    System.out.println("Running async task in thread: "
        + Thread.currentThread().getName());
    // 无返回值，适合纯副作用操作
});

future.join(); // 等待完成（不抛出受检异常）
```

### 2.4 get() vs join()

| 方法 | 异常类型 | 适用场景 |
|------|----------|----------|
| `get()` | `InterruptedException`, `ExecutionException` | 需要处理受检异常的场景 |
| `join()` | `CompletionException` (非受检) | 流式编程、链式调用中更简洁 |

```java
// get() 需要 try-catch
try {
    String result = future.get();
} catch (InterruptedException | ExecutionException e) {
    e.printStackTrace();
}

// join() 更简洁，异常为 RuntimeException
String result = future.join();
```

---

## 三、链式调用

`CompletableFuture` 支持以链式方式编排多个异步阶段，每个阶段在前一阶段完成后自动执行。

### 3.1 核心方法一览

| 方法 | 接收参数 | 返回值 | 是否异步 |
|------|----------|--------|----------|
| `thenApply` | `T` | `U` | 否（同线程） |
| `thenApplyAsync` | `T` | `U` | 是 |
| `thenAccept` | `T` | `void` | 否 |
| `thenAcceptAsync` | `T` | `void` | 是 |
| `thenRun` | 无 | `void` | 否 |
| `thenRunAsync` | 无 | `void` | 是 |

### 3.2 thenApply — 转换结果

```java
CompletableFuture<Integer> future = CompletableFuture
    .supplyAsync(() -> 10)
    .thenApply(x -> x * 2)       // 10 -> 20
    .thenApply(x -> x + 5);      // 20 -> 25

System.out.println(future.join()); // 25
```

### 3.3 thenAccept — 消费结果

```java
CompletableFuture<Void> future = CompletableFuture
    .supplyAsync(() -> "Hello")
    .thenApply(String::toUpperCase)
    .thenAccept(System.out::println); // HELLO

future.join();
```

### 3.4 thenRun — 忽略结果执行后续动作

```java
CompletableFuture<Void> future = CompletableFuture
    .supplyAsync(() -> fetchData())
    .thenRun(() -> System.out.println("Task completed, result ignored"));
```

### 3.5 thenCompose — 扁平化嵌套 Future

当异步操作的结果本身也是一个 `CompletableFuture` 时，使用 `thenCompose` 避免嵌套。

```java
// thenCompose 将嵌套的 CompletableFuture<CompletableFuture<U>> 展平为 CompletableFuture<U>
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> "user-123")
    .thenCompose(userId -> getUserById(userId)); // getUserById 返回 CompletableFuture<User>

// 对比：使用 thenApply 会产生嵌套
// CompletableFuture<CompletableFuture<User>> nested = supplyAsync(...).thenApply(this::getUserById);
```

---

## 四、组合多个 CompletableFuture

### 4.1 thenCombine — 并行执行后合并

两个独立的 `CompletableFuture` 都完成后，将结果合并。

```java
CompletableFuture<String> nameFuture = CompletableFuture.supplyAsync(() -> "Alice");
CompletableFuture<Integer> ageFuture = CompletableFuture.supplyAsync(() -> 30);

CompletableFuture<String> combined = nameFuture
    .thenCombine(ageFuture, (name, age) -> name + " is " + age + " years old");

System.out.println(combined.join()); // Alice is 30 years old
```

### 4.2 thenAcceptBoth / runAfterBoth

```java
// thenAcceptBoth: 两个都完成后消费结果
future1.thenAcceptBoth(future2, (r1, r2) ->
    System.out.println(r1 + ", " + r2));

// runAfterBoth: 两个都完成后执行无参数操作
future1.runAfterBoth(future2, () ->
    System.out.println("Both tasks finished"));
```

### 4.3 applyToEither / acceptEither — 任一完成即执行

```java
CompletableFuture<String> fast = CompletableFuture.supplyAsync(() -> {
    Thread.sleep(500);
    return "Fast result";
});

CompletableFuture<String> slow = CompletableFuture.supplyAsync(() -> {
    Thread.sleep(2000);
    return "Slow result";
});

// 哪个先完成就用哪个的结果
String result = fast.applyToEither(slow, r -> r).join();
System.out.println(result); // Fast result
```

### 4.4 thenCombine vs thenCompose 对比

| 方法 | 执行关系 | 结果关系 | 典型场景 |
|------|----------|----------|----------|
| `thenCombine` | 两个 Future **并行** 执行 | 合并两个结果 | 同时查询用户信息和订单信息后拼接 |
| `thenCompose` | 两个 Future **串行** 执行 | 展平嵌套 Future | 先查用户 ID，再用 ID 查用户详情 |
| `thenApply` | 单 Future 串行 | 转换结果类型 | 将字符串转为大写 |

---

## 五、多任务编排

### 5.1 allOf — 等待所有任务完成

```java
CompletableFuture<String> f1 = CompletableFuture.supplyAsync(() -> "A");
CompletableFuture<String> f2 = CompletableFuture.supplyAsync(() -> "B");
CompletableFuture<String> f3 = CompletableFuture.supplyAsync(() -> "C");

// allOf 返回 CompletableFuture<Void>
CompletableFuture<Void> all = CompletableFuture.allOf(f1, f2, f3);

// 等待所有任务完成后收集结果
all.thenRun(() -> {
    List<String> results = Stream.of(f1, f2, f3)
        .map(CompletableFuture::join)
        .toList();
    System.out.println(results); // [A, B, C]
}).join();
```

### 5.2 anyOf — 任一任务完成即可

```java
CompletableFuture<String> fast = CompletableFuture.supplyAsync(() -> {
    sleep(1000);
    return "First";
});

CompletableFuture<String> medium = CompletableFuture.supplyAsync(() -> {
    sleep(2000);
    return "Second";
});

CompletableFuture<String> slow = CompletableFuture.supplyAsync(() -> {
    sleep(3000);
    return "Third";
});

// 返回 CompletableFuture<Object>，需要手动转型
Object result = CompletableFuture.anyOf(fast, medium, slow).join();
System.out.println(result); // First
```

### 5.3 allOf vs anyOf 对比

| 方法 | 返回类型 | 语义 | 典型场景 |
|------|----------|------|----------|
| `allOf` | `CompletableFuture<Void>` | 所有任务完成才继续 | 批量数据汇总、多数据源聚合 |
| `anyOf` | `CompletableFuture<Object>` | 任一任务完成即继续 | 多镜像源获取、超时兜底 |

> **注意**：`allOf` 返回 `Void` 类型，不直接携带结果。需要通过 `join()` 各个原始 Future 来获取结果。

---

## 六、异常处理

`CompletableFuture` 提供了三种异常处理方式，覆盖不同的使用场景。

### 6.1 exceptionally — 降级处理

当上游阶段抛出异常时，提供一个替代值。

```java
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> {
        if (true) throw new RuntimeException("Service unavailable");
        return "OK";
    })
    .exceptionally(ex -> "Fallback: " + ex.getMessage());

System.out.println(future.join());
// Fallback: java.lang.RuntimeException: Service unavailable
```

### 6.2 handle — 同时处理成功和异常

无论上游是否发生异常，`handle` 都会被调用。

```java
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> {
        int x = 1 / 0; // 触发异常
        return "Result";
    })
    .handle((result, ex) -> {
        if (ex != null) {
            return "Error occurred: " + ex.getCause().getMessage();
        }
        return "Success: " + result;
    });

System.out.println(future.join());
// Error occurred: / by zero
```

### 6.3 whenComplete — 记录结果但不改变返回值

```java
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> "Hello")
    .whenComplete((result, ex) -> {
        if (ex != null) {
            System.err.println("Error: " + ex.getMessage());
        } else {
            System.out.println("Result: " + result);
        }
    });

// whenComplete 不改变原始结果，仅作为副作用观察
System.out.println(future.join()); // Hello
```

### 6.4 异常处理方式对比

| 方法 | 参数 | 是否消费异常 | 返回值 | 典型用途 |
|------|------|:-----------:|--------|----------|
| `exceptionally` | `Throwable` | 是 | 降级值 | 提供默认值/兜底逻辑 |
| `handle` | `result, Throwable` | 是 | 新值或降级值 | 统一处理成功和失败 |
| `whenComplete` | `result, Throwable` | 否 | 原结果 | 日志记录、资源清理 |

### 6.5 异步版本

每个方法都有对应的 `Async` 版本，可指定在独立线程中执行：

```java
// 在自定义线程池中处理异常
future.exceptionallyAsync(ex -> "Fallback", customExecutor);
future.handleAsync((r, ex) -> r != null ? r : "N/A", customExecutor);
future.whenCompleteAsync((r, ex) -> log(r, ex), customExecutor);
```

---

## 七、自定义线程池

默认情况下，不带 `Executor` 参数的 `Async` 方法使用 `ForkJoinPool.commonPool()`。在生产环境中，建议显式指定线程池以实现资源隔离和精确控制。

### 7.1 为什么需要自定义线程池

| 原因 | 说明 |
|------|------|
| 资源隔离 | 不同业务使用不同线程池，避免互相影响 |
| 控制并发度 | 根据业务特性调整核心线程数和最大线程数 |
| 拒绝策略 | 自定义队列满时的处理策略 |
| 线程命名 | 便于日志追踪和问题排查 |

### 7.2 示例代码

```java
// 创建自定义线程池
ExecutorService customExecutor = new ThreadPoolExecutor(
    5,                                  // corePoolSize
    10,                                 // maximumPoolSize
    60L, TimeUnit.SECONDS,              // keepAliveTime
    new LinkedBlockingQueue<>(100),     // workQueue
    new ThreadFactory() {
        private final AtomicInteger counter = new AtomicInteger(0);
        @Override
        public Thread newThread(Runnable r) {
            Thread t = new Thread(r, "cf-pool-" + counter.incrementAndGet());
            t.setDaemon(false);
            return t;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy()  // 拒绝策略
);

// 使用自定义线程池
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> fetchDataFromRemote(), customExecutor)
    .thenApplyAsync(data -> processData(data), customExecutor)
    .thenAcceptAsync(result -> saveToDatabase(result), customExecutor);

// 注意：应用关闭时需要正确关闭线程池
// customExecutor.shutdown();
```

### 7.3 线程池选择建议

| 任务类型 | 推荐配置 |
|----------|----------|
| CPU 密集型 | 核心线程数 = CPU 核心数 + 1 |
| IO 密集型 | 核心线程数 = CPU 核心数 * 2 |
| 混合型 | 拆分为 CPU 和 IO 两个线程池 |
| 短时高并发 | 较大的 maximumPoolSize + SynchronousQueue |

### 7.4 常见陷阱

```java
// 错误：使用 newCachedThreadPool，线程数可能无限增长
ExecutorService unbounded = Executors.newCachedThreadPool();

// 错误：使用 newFixedThreadPool，队列无界可能 OOM
ExecutorService unboundedQueue = Executors.newFixedThreadPool(10);

// 正确：手动创建 ThreadPoolExecutor，明确队列大小和拒绝策略
ExecutorService safe = new ThreadPoolExecutor(
    5, 20, 60L, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(500),
    new ThreadPoolExecutor.AbortPolicy()
);
```

---

## 八、与 RxJava / Stream 的对比

### 8.1 CompletableFuture vs RxJava

| 维度 | CompletableFuture | RxJava |
|------|-------------------|--------|
| **定位** | 单次异步操作 | 响应式流（0、1 或多个数据项） |
| **数据量** | 单个结果 | 事件流（Observable/Flowable） |
| **背压** | 不支持 | Flowable 支持背压 |
| **操作符** | 有限的组合方法 | 丰富的操作符（map、filter、zip、buffer 等） |
| **学习曲线** | 较低，JDK 内置 | 较高，需要理解响应式概念 |
| **适用场景** | 简单的异步编排、微服务间调用 | 复杂事件处理、实时数据流、UI 事件流 |

```java
// RxJava 示例：可以处理多个事件
Observable.just(1, 2, 3, 4, 5)
    .filter(x -> x % 2 == 0)
    .map(x -> x * 10)
    .subscribe(System.out::println);
// 输出: 20, 40, 60

// CompletableFuture 只能处理单个值
CompletableFuture.supplyAsync(() -> 42)
    .thenApply(x -> x * 10)
    .thenAccept(System.out::println);
// 输出: 420
```

### 8.2 CompletableFuture vs Stream API

| 维度 | CompletableFuture | Stream API |
|------|-------------------|------------|
| **执行模型** | 异步、非阻塞 | 同步（默认）、惰性求值 |
| **并行** | 天然异步，由线程池驱动 | `parallelStream()` 使用 ForkJoinPool |
| **组合性** | 时间维度上的编排 | 数据维度上的流水线 |
| **异常处理** | exceptionally / handle | try-catch 或自定义包装 |
| **适用场景** | 跨服务调用、异步 IO | 集合数据的转换与聚合 |

```java
// Stream：对集合数据进行流水线处理
List<String> names = users.stream()
    .filter(u -> u.isActive())
    .map(User::getName)
    .sorted()
    .toList();

// CompletableFuture：对异步操作进行时间维度编排
CompletableFuture<User> userFuture = CompletableFuture.supplyAsync(this::fetchUser);
CompletableFuture<Order> orderFuture = CompletableFuture.supplyAsync(this::fetchOrders);

CompletableFuture<String> summary = userFuture
    .thenCombine(orderFuture, this::formatSummary);
```

### 8.3 三者选择决策树

```
是否处理数据集合？
  |-- 是 --> 使用 Stream API
  |-- 否 --> 是否产生连续事件流？
                |-- 是 --> 使用 RxJava / Reactor
                |-- 否 --> 使用 CompletableFuture
```

### 8.4 混合使用示例

在实际项目中，三者经常混合使用：

```java
CompletableFuture<List<User>> usersFuture =
    CompletableFuture.supplyAsync(() -> userRepository.findAll());

usersFuture
    .thenApply(users -> users.stream()
        .filter(User::isActive)
        .map(User::getEmail)
        .toList())
    .thenAccept(emails -> emails.forEach(this::sendNotification))
    .exceptionally(ex -> {
        log.error("Notification failed", ex);
        return null;
    });
```

> **总结**：`CompletableFuture` 是 JDK 内置的异步编排工具，适合单次异步结果的组合。它与 Stream（数据处理）和 RxJava（事件流）互补而非替代关系。在现代 Java 开发中，三者配合使用可以覆盖绝大多数并发编程场景。
