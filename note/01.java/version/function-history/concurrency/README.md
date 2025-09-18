# 并发

| Java版本  | 新特性/增强内容                                             |
|---------|------------------------------------------------------|
| Java 1  | 基础线程支持，引入 Thread 类和 synchronized 关键字                 |
| Java 2  | 引入 ThreadLocal 类，支持线程局部变量                            |
| Java 5  | JEP 47: java.util.concurrent 包，引入线程池、并发集合、同步工具等      |
| Java 6  | JVM 层面对 synchronized 的优化，引入偏向锁、轻量级锁等                 |
| Java 7  | JEP 10: Fork/Join 框架，引入 Phaser、TransferQueue 等并发工具   |
| Java 8  | JEP 155: 改进对并发的支持，引入 CompletableFuture 和 StampedLock |
| Java 8  | Stream API 引入并行流支持                                   |
| Java 9  | JEP 266: 更多并发更新                                      |
| Java 10 | JEP 312: 线程局部握手                                      |
| Java 14 | JEP 372: 删除 Nashorn JavaScript 引擎（包含相关并发组件）          |
| Java 16 | JEP 376: ZGC 并行线程栈处理                                 |
| Java 19 | JEP 425: 虚拟线程（第一次预览）                                 |
| Java 19 | JEP 428: 结构化并发（第一次孵化）                                |
| Java 20 | JEP 429: 作用域值（第一次孵化）                                 |
| Java 20 | JEP 436: 虚拟线程（第二次预览）                                 |
| Java 20 | JEP 437: 结构化并发（第二次孵化）                                |
| Java 21 | JEP 444: 虚拟线程（正式特性）                                  |
| Java 21 | JEP 446: 作用域值（预览）                                    |
| Java 21 | JEP 453: 结构化并发（预览）                                   |
| Java 22 | 作用域值（第二次预览）                                          |
| Java 22 | 结构化并发（第二次预览）                                         |
| Java 23 | JEP 480: 结构化并发（第三次预览）                                |
| Java 23 | JEP 487: 作用域值（第三次预览）                                 |
| Java 24 | JEP 487: 作用域值（第四次预览）                                 |
| Java 24 | JEP 491: 虚拟线程的同步而不固定平台线程                             |
| Java 24 | JEP 499: 结构化并发（第四次预览）                                |
| Java 25 | JEP 505: 结构化并发（第五次预览）                                |
| Java 25 | JEP 506: 作用域值（最终版）                                   |

## 功能详细介绍

### 1. Java 1 - 基础并发支持

Java 1.0 奠定了 Java 并发编程的基础：

1. **Thread 类**：提供了基本的线程创建和管理功能
```java
// 基本线程创建示例
class MyThread extends Thread {
    public void run() {
        System.out.println("Hello from thread!");
    }
}

// 使用线程
MyThread thread = new MyThread();
thread.start();
```


2. **synchronized 关键字**：提供了基本的对象锁机制
```java
// synchronized 方法
public synchronized void doSomething() {
    // 线程安全的代码块
}

// synchronized 代码块
public void doSomething() {
    synchronized(this) {
        // 线程安全的代码块
    }
}
```


### 2. Java 2 - ThreadLocal 支持

Java 2 引入了 `ThreadLocal` 类，支持线程局部变量：

1. **ThreadLocal**：为每个线程提供独立的变量副本
```java
// ThreadLocal 示例
public class ThreadLocalExample {
    private static final ThreadLocal<Integer> threadLocalValue = new ThreadLocal<Integer>() {
        @Override
        protected Integer initialValue() {
            return 0;
        }
    };
    
    public void increment() {
        threadLocalValue.set(threadLocalValue.get() + 1);
    }
    
    public int getValue() {
        return threadLocalValue.get();
    }
}
```


### 3. Java 5 - 并发编程里程碑 (JEP 47)

Java 5 是并发编程的一个重要里程碑，引入了 `java.util.concurrent` 包：

#### java.util.concurrent 包的主要组件：

1. **Executor 框架**：提供了线程池管理功能
```java
// ExecutorService 示例
ExecutorService executor = Executors.newFixedThreadPool(10);
executor.submit(() -> {
    System.out.println("Task executed in thread pool");
});
executor.shutdown();
```


2. **并发集合**：线程安全的集合实现
```java
// ConcurrentHashMap 示例
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("key", 1);
Integer value = map.get("key");

// BlockingQueue 示例
BlockingQueue<String> queue = new LinkedBlockingQueue<>();
queue.put("item");  // 阻塞式添加
String item = queue.take();  // 阻塞式获取
```


3. **同步工具类**：
```java
// CountDownLatch 示例
CountDownLatch latch = new CountDownLatch(3);
// 在其他线程中调用 latch.countDown()
latch.await();  // 等待计数器归零

// Semaphore 示例
Semaphore semaphore = new Semaphore(2);  // 允许2个线程同时访问
semaphore.acquire();  // 获取许可
// 执行受保护的代码
semaphore.release();  // 释放许可

// ReentrantLock 示例
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    // 线程安全的代码块
} finally {
    lock.unlock();
}
```


4. **Future 和 Callable**：
```java
// Callable 和 Future 示例
Callable<String> task = () -> {
    Thread.sleep(1000);
    return "Task result";
};

ExecutorService executor = Executors.newSingleThreadExecutor();
Future<String> future = executor.submit(task);
String result = future.get();  // 阻塞直到任务完成
```


### 4. Java 6 - JVM 同步优化

Java 6 主要对 JVM 层面的同步机制进行了优化：

1. **偏向锁**：减少了同一线程多次获取同一锁的开销
2. **轻量级锁**：优化了无竞争情况下的锁获取
3. **自适应自旋锁**：根据前一次在同一锁上的自旋时间及拥有者状态来决定自旋时间

### 5. Java 7 - 并发功能增强 (JEP 10)

Java 7 继续增强了并发编程功能：

#### Fork/Join 框架：

1. **ForkJoinPool**：专门用于执行 ForkJoinTask 的线程池
2. **RecursiveTask 和 RecursiveAction**：支持分治算法的任务抽象

```java
// Fork/Join 示例
class FibonacciTask extends RecursiveTask<Integer> {
    private final int n;
    
    FibonacciTask(int n) {
        this.n = n;
    }
    
    @Override
    protected Integer compute() {
        if (n <= 1) {
            return n;
        }
        FibonacciTask f1 = new FibonacciTask(n - 1);
        f1.fork();
        FibonacciTask f2 = new FibonacciTask(n - 2);
        return f2.compute() + f1.join();
    }
}

// 使用 Fork/Join 框架
ForkJoinPool pool = new ForkJoinPool();
FibonacciTask task = new FibonacciTask(10);
int result = pool.invoke(task);
```


#### 其他并发工具：

1. **Phaser**：更灵活的同步屏障
```java
// Phaser 示例
Phaser phaser = new Phaser(3);  // 3个参与者
phaser.arriveAndAwaitAdvance();  // 到达并等待其他线程
```


2. **ThreadLocalRandom**：为并发环境提供高效的随机数生成器
```java
// ThreadLocalRandom 示例
int randomValue = ThreadLocalRandom.current().nextInt(100);
```


### 6. Java 8 - 并发基础增强

Java 8 在并发编程方面进行了多项重要改进，为后续版本的发展奠定了基础。

#### JEP 155: 改进对并发的支持

引入了新的并发工具和机制：

1. **CompletableFuture**：提供了更强大的异步编程能力
```java
// CompletableFuture 示例
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> "Hello")
                                                  .thenApply(s -> s + " World");
future.thenAccept(System.out::println);
```



2. **StampedLock**：提供了比 ReadWriteLock 更高效的读写锁实现
```java
StampedLock lock = new StampedLock();
long stamp = lock.readLock();
try {
    // 读操作
} finally {
    lock.unlockRead(stamp);
}
```



#### Stream API 并行流支持

引入了并行流处理能力：
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
int sum = numbers.parallelStream()
                 .mapToInt(Integer::intValue)
                 .sum();
```



### 7. Java 9 - 并发功能增强

#### JEP 266: 更多并发更新

增加了更多的并发工具和API，如 CompletableFuture 的增强等。

### 8. Java 10 - 线程优化

#### JEP 312: 线程局部握手

引入了线程局部握手（Thread-Local Handshakes）机制，它允许 JVM 在不暂停所有线程的情况下，与单个线程进行交互。这使得 JVM 可以更细粒度地控制线程的执行，减少了不必要的停顿时间，提高了应用程序的响应速度。

### 9. Java 19 - 现代并发编程模型引入

Java 19 是并发编程的一个重要里程碑，引入了虚拟线程、结构化并发等现代并发编程模型。

#### JEP 425: 虚拟线程（第一次预览）

虚拟线程是一种轻量级的线程实现，旨在简化高并发编程：
```java
// 创建并启动虚拟线程
Runnable task = () -> {
    System.out.println("Hello from virtual thread!");
};
Thread virtualThread = Thread.startVirtualThread(task);
virtualThread.join();
```



#### JEP 428: 结构化并发（第一次孵化）

结构化并发是一种多线程编程方法，旨在简化多线程代码的管理和错误处理：
```java
try (var scope = new StructuredTaskScope<Object>()) {
    Future<Integer> future1 = scope.fork(() -> doTask1());
    Future<String> future2 = scope.fork(() -> doTask2());
    scope.join();
    scope.throwIfFailed();

    Integer result1 = future1.resultNow();
    String result2 = future2.resultNow();
    // 处理结果
} catch (Exception e) {
    // 处理异常
}
```



### 10. Java 20 - 并发功能继续完善

#### JEP 429: 作用域值（第一次孵化）

作用域值是一种在线程内和线程间共享不可变数据的机制：
```java
final static ScopedValue<String> USER_NAME = new ScopedValue<>();

// 设置作用域值
ScopedValue.where(USER_NAME, "Alice")
           .run(() -> {
               // 在这个作用域内可以访问 USER_NAME
               System.out.println("Hello, " + USER_NAME.get());
           });
```



#### JEP 436: 虚拟线程（第二次预览）

继续优化虚拟线程功能。

#### JEP 437: 结构化并发（第二次孵化）

继续完善结构化并发功能。

### 11. Java 21 - 现代并发编程模型转正

Java 21 将多个现代并发编程特性从预览或孵化状态转正为标准特性。

#### JEP 444: 虚拟线程（正式特性）

虚拟线程成为标准特性，提供更简洁的 API：
```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> {
        executor.submit(() -> {
            System.out.println("任务 " + i + " 执行中");
            Thread.sleep(10); // 模拟 I/O 操作
            return "结果 " + i;
        });
    });
}
```



#### JEP 446: 作用域值（预览）

作用域值进入预览阶段。

#### JEP 453: 结构化并发（预览）

结构化并发进入预览阶段。

### 12. Java 22 - 并发功能持续完善

继续完善作用域值和结构化并发功能。

### 13. Java 23 - 并发功能进一步优化

#### JEP 480: 结构化并发（第三次预览）

继续完善结构化并发功能。

#### JEP 487: 作用域值（第三次预览）

继续完善作用域值功能。

### 14. Java 24 - 并发功能进一步增强

#### JEP 487: 作用域值（第四次预览）

继续完善作用域值功能。

#### JEP 491: 虚拟线程的同步而不固定平台线程

优化了虚拟线程与 synchronized 的工作机制，虚拟线程在 synchronized 方法和代码块中阻塞时，通常能够释放其占用的操作系统线程（平台线程）。

#### JEP 499: 结构化并发（第四次预览）

继续完善结构化并发功能。

### 15. Java 25 - 并发功能成熟化

#### JEP 505: 结构化并发（第五次预览）

继续完善结构化并发功能。

#### JEP 506: 作用域值（最终版）

作用域值成为标准特性，提供线程间安全共享不可变数据的轻量方案：
```java
// 定义作用域值
private static final ScopedValue<User> CONTEXT = ScopedValue.newInstance();

// 使用作用域值
void handleRequest(Request req) {
    User user = authenticate(req);
    ScopedValue.where(CONTEXT, user)
              .run(() -> processRequest(req));
}

// 在子任务中获取值
void processRequest(Request req) {
    User user = CONTEXT.get();  // 安全获取作用域值
    // 处理请求...
}
```



## 现代并发编程模型核心优势

### 虚拟线程
1. **高并发性**：可以轻松创建数百万个虚拟线程
2. **资源效率**：每个虚拟线程仅需约 1KB 栈空间
3. **简化编程**：保持同步编程风格的同时获得异步性能
4. **自动挂起**：遇到 I/O 操作时自动挂起并释放载体线程

### 结构化并发
1. **简化错误处理**：子任务出错时自动取消其他未完成任务
2. **提高可读性**：将多个并发任务视为单个工作单元
3. **增强可靠性**：确保任务的原子性和一致性

### 作用域值
1. **替代 ThreadLocal**：比 ThreadLocal 更适合虚拟线程环境
2. **线程安全**：提供线程间安全共享不可变数据的轻量方案
3. **性能优化**：专为虚拟线程优化，减少内存占用

## 适用场景

1. **高并发 Web 服务**：处理数万并发请求
2. **I/O 密集型任务**：网络爬虫、批量数据库查询、文件读写
3. **微服务架构**：服务间频繁调用
4. **异步编程替代**：无需编写复杂的异步回调代码

## 性能对比

- **测试场景**：处理 100 万个任务，每个任务模拟 10ms I/O 延迟
- **传统线程池（200 线程）**：
    - 耗时：约 30,000ms
    - 内存峰值：1.2GB
- **虚拟线程**：
    - 耗时：约 5,000ms
    - 内存峰值：200MB

## 总结

从 Java 1 到 Java 25，Java 并发编程经历了从基础支持到现代并发模型的演进。Java 1 奠定了基础，Java 5 引入了 java.util.concurrent 包，Java 7 增加了 Fork/Join 框架，Java 8 引入了 CompletableFuture 和 StampedLock 等工具，Java 19 开始引入虚拟线程、结构化并发等现代并发编程模型，到 Java 25 这些特性逐渐成熟并成为标准。这些改进显著提升了 Java 在高并发场景下的性能和开发效率，为现代应用程序提供了更强大的并发处理能力。