<!--
module:
  parent: java
  slug: java/version/concurrency
  type: article
  category: 主模块子文章
  summary: Java 并发演进：synchronized → Lock → CompletableFuture → Virtual Threads。
-->

# 并发

## 引言：变更说明

并发 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 功能描述

Java 并发编程从基础的 Thread/synchronized 演进到现代并发模型。Java 21 转正的虚拟线程（Virtual Threads）彻底改变了高并发场景的编程方式——可以用同步写法实现异步性能。配合结构化并发（Structured Concurrency）和作用域值（Scoped Values），Java 为高并发服务端应用提供了完整的现代并发编程栈。

## 基本用法（最新，Java 26+）

```java
// 1. 虚拟线程（Java 21+ 正式特性）- 替代线程池的首选方式
Thread vt = Thread.startVirtualThread(() -> {
    System.out.println("Running in virtual thread: " + Thread.currentThread());
});
vt.join();

// 2. ExecutorService 虚拟线程（Java 21+）
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<String>> futures = IntStream.range(0, 10_000)
        .mapToObj(i -> executor.submit(() -> {
            Thread.sleep(10); // 模拟 I/O 阻塞
            return "Task " + i;
        }))
        .toList();
    // 等待所有任务完成
    executor.close(); // 自动 join
}

// 3. 结构化并发（Java 25+ 预览）
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    StructuredTaskScope.Subtask<User> userTask = scope.fork(() -> findUser(userId));
    StructuredTaskScope.Subtask<Order> orderTask = scope.fork(() -> fetchOrder(orderId));
    scope.join();            // 等待所有子任务
    scope.throwIfFailed();   // 任一失败则抛出

    User user = userTask.resultNow();
    Order order = orderTask.resultNow();
    return new Response(user, order);
}

// 4. 作用域值（Java 25+ 转正）
// 定义作用域值
static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();

// 设置并使用
ScopedValue.where(CURRENT_USER, authenticatedUser)
    .run(() -> processRequest());  // 当前线程及其子线程可访问

void processRequest() {
    User user = CURRENT_USER.get();  // 安全获取，替代 ThreadLocal
}

// 5. CompletableFuture 异步编程（Java 8+）
CompletableFuture<String> result = CompletableFuture
    .supplyAsync(() -> fetchData())
    .thenApply(data -> transform(data))
    .thenAccept(System.out::println)
    .exceptionally(ex -> { log.error("Error", ex); return null; });

// 6. CompletableFuture 组合
CompletableFuture.allOf(
    CompletableFuture.supplyAsync(() -> serviceA.getData()),
    CompletableFuture.supplyAsync(() -> serviceB.getData())
).thenAccept(v -> System.out.println("All complete"));

// 7. 虚拟线程 + CompletableFuture（Java 21+）
// 虚拟线程自动作为 CompletableFuture 的异步执行载体
CompletableFuture.supplyAsync(() -> blockingIoCall())
    .thenApplyAsync(result -> anotherBlockingCall(result));

// 8. StampedLock 乐观读（Java 8+）
class Point {
    private double x, y;
    private final StampedLock sl = new StampedLock();

    void move(double dx, double dy) {
        long stamp = sl.writeLock();
        try { x += dx; y += dy; }
        finally { sl.unlockWrite(stamp); }
    }

    double distanceFromOrigin() {
        long stamp = sl.tryOptimisticRead();
        double currentX = x, currentY = y;
        if (!sl.validate(stamp)) {  // 乐观读失败，升级为悲观读锁
            stamp = sl.readLock();
            try { currentX = x; currentY = y; }
            finally { sl.unlockRead(stamp); }
        }
        return Math.sqrt(currentX * currentX + currentY * currentY);
    }
}
```

## 变更历史表

| Java版本  | 新特性/增强内容                                             |
|---------|------------------------------------------------------|
| Java 26 | JEP 525: 结构化并发（第六次预览）                                |
| Java 25 | JEP 505: 结构化并发（第五次预览）                                |
| Java 25 | JEP 506: 作用域值（转正）                                   |
| Java 24 | JEP 491: 虚拟线程在 synchronized 中阻塞时释放平台线程              |
| Java 24 | JEP 499: 结构化并发（第四次预览）                                |
| Java 23 | JEP 480: 结构化并发（第三次预览）                                |
| Java 23 | JEP 487: 作用域值（第四次预览）                                 |
| Java 22 | 作用域值（第二次预览）                                          |
| Java 22 | 结构化并发（第二次预览）                                         |
| Java 21 | JEP 444: 虚拟线程（正式特性）                                  |
| Java 21 | JEP 446: 作用域值（预览）                                    |
| Java 21 | JEP 453: 结构化并发（预览）                                   |
| Java 20 | JEP 429: 作用域值（第一次孵化）                                 |
| Java 20 | JEP 436: 虚拟线程（第二次预览）                                 |
| Java 20 | JEP 437: 结构化并发（第二次孵化）                                |
| Java 19 | JEP 425: 虚拟线程（第一次预览）                                 |
| Java 19 | JEP 428: 结构化并发（第一次孵化）                                |
| Java 10 | JEP 312: 线程局部握手                                      |
| Java 9  | 更多并发更新（CompletableFuture 增强等）                         |
| Java 8  | CompletableFuture、StampedLock、并行流                      |
| Java 7  | Fork/Join 框架（JSR 166）                                 |
| Java 6  | JVM 对 synchronized 的偏向锁、轻量级锁优化                       |
| Java 5  | JSR 166: java.util.concurrent 包（线程池、并发集合、同步工具）      |
| Java 2  | ThreadLocal 类                                      |
| Java 1  | Thread 类和 synchronized 关键字                          |

## 功能详细介绍

### 1. Java 1-4 - 基础并发

Java 1 提供 `Thread` 类和 `synchronized` 关键字。Java 2 引入 `ThreadLocal` 提供线程局部变量。

### 2. Java 5 - 并发编程里程碑 (JSR 166)

引入 `java.util.concurrent` 包：
- **Executor 框架**：`ExecutorService`、`ThreadPoolExecutor`
- **并发集合**：`ConcurrentHashMap`、`BlockingQueue`、`CopyOnWriteArrayList`
- **同步工具**：`ReentrantLock`、`CountDownLatch`、`Semaphore`、`CyclicBarrier`
- **Future/Callable**：异步结果获取

### 3. Java 7 - Fork/Join 框架

引入分治任务的并行执行框架：

```java
class FibonacciTask extends RecursiveTask<Integer> {
    private final int n;
    FibonacciTask(int n) { this.n = n; }
    @Override
    protected Integer compute() {
        if (n <= 1) return n;
        FibonacciTask f1 = new FibonacciTask(n - 1);
        f1.fork();
        return new FibonacciTask(n - 2).compute() + f1.join();
    }
}
```

### 4. Java 8 - CompletableFuture 和 StampedLock

**CompletableFuture** 提供了更强大的异步编程能力，支持链式调用和组合：

```java
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> "Hello")
    .thenApply(s -> s + " World")
    .thenAccept(System.out::println);
```

**StampedLock** 提供比 ReadWriteLock 更高效的读写锁，支持乐观读。

### 5. Java 19-21 - 虚拟线程（JEP 425/436/444）

虚拟线程是轻量级线程实现，每个仅需约 1KB 栈空间，可以轻松创建数百万个：

```java
// 替代线程池的用法
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i ->
        executor.submit(() -> { /* I/O 操作 */ })
    );
}
```

性能对比（100 万任务，10ms I/O 延迟）：
| 方案 | 耗时 | 内存 |
|-----|------|------|
| 线程池（200 线程） | ~30s | ~1.2GB |
| 虚拟线程 | ~5s | ~200MB |

### 6. Java 19-25 - 结构化并发（孵化 → 预览）

将多线程任务视为单个工作单元，子任务出错时自动取消其他任务：

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var user = scope.fork(() -> findUser());
    var order = scope.fork(() -> fetchOrder());
    scope.join().throwIfFailed();
    return new Response(user.resultNow(), order.resultNow());
}
```

### 7. Java 20-25 - 作用域值（孵化 → 预览 → 转正）

替代 `ThreadLocal`，在虚拟线程环境中高效共享不可变数据：

```java
static final ScopedValue<User> USER = ScopedValue.newInstance();
ScopedValue.where(USER, currentUser).run(() -> processRequest());
```

### 8. Java 24 - 虚拟线程 synchronized 优化

虚拟线程在 `synchronized` 中阻塞时通常能释放载体线程，解决了早期虚拟线程与 `synchronized` 的兼容问题。

## 现代并发模型核心优势

| 特性 | 替代方案 | 优势 |
|------|---------|------|
| 虚拟线程 | 线程池/异步回调 | 同步写法 + 异步性能 |
| 结构化并发 | CompletableFuture | 自动错误传播和任务取消 |
| 作用域值 | ThreadLocal | 轻量、虚拟线程友好 |

## 适用场景

1. **高并发 Web 服务**：处理数万并发请求
2. **I/O 密集型任务**：网络爬虫、批量数据库查询
3. **微服务调用**：并发调用多个下游服务
4. **传统线程池替代**：所有使用线程池的场景

## 总结

Java 并发从 `synchronized` + `Thread` 演进到虚拟线程 + 结构化并发 + 作用域值的现代模型。Java 21+ 的虚拟线程是最大变革——用同步写法获得异步性能，无需再编写复杂的异步回调代码。结构化并发持续迭代预览（Java 26 第六次预览），为正式发布做准备。
