<!--
module:
  parent: java
  slug: java/concurrency-basics
  type: article
  category: 主模块子文章
  summary: 并发编程基础概念
-->

# 并发编程基础概念

## 引言：变更说明

并发编程基础概念 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

Java 并发编程是 Java 平台的核心能力之一，涵盖了从线程创建、同步控制到高级并发模型的全套机制。理解并发编程的基础概念，是编写高性能、高可靠服务端程序的前提。

## 一、什么是并发编程

并发（Concurrency）是指多个任务在同一时间段内**交替或同时**执行。与并行（Parallelism，强调同一时刻多个任务真正同时运行）不同，并发更侧重于任务调度和资源复用。在 Java 中，并发编程主要解决以下问题：

| 问题维度 | 具体表现 |
|---------|---------|
| 正确性 | 多线程对共享资源的读写导致数据不一致 |
| 活性 | 死锁、饥饿、活锁导致任务无法推进 |
| 性能 | 线程创建/切换开销、锁竞争导致吞吐量下降 |
| 复杂性 | 异步回调嵌套、错误传播困难、调试困难 |

```java
// 并发问题的经典示例：非线程安全的计数器
class UnsafeCounter {
    private int count = 0;

    public void increment() {
        count++; // 非原子操作：读-改-写三个步骤
    }

    public int get() {
        return count;
    }
}
// 两个线程同时调用 increment()，最终 count 可能小于预期值
```

## 二、Java 并发编程发展历程

Java 并发能力经历了从底层原语到高级抽象的完整演进，大致可分为四个阶段：

| 阶段 | 版本 | 核心特性 | 编程模型 |
|------|------|---------|---------|
| 第一阶段 | Java 1-4 | `Thread`、`synchronized`、`volatile`、`wait/notify` | 手动管理线程，底层同步原语 |
| 第二阶段 | Java 5-7 | `java.util.concurrent` 包、线程池、`Fork/Join` | 库级抽象，结构化并发工具 |
| 第三阶段 | Java 8-16 | `CompletableFuture`、`StampedLock`、`VarHandle` | 异步编排，无锁编程 |
| 第四阶段 | Java 19-26 | 虚拟线程、结构化并发、作用域值 | 现代轻量并发模型 |

```java
// 第一阶段：Java 1 手动管理线程
new Thread(() -> {
    System.out.println("Hello from " + Thread.currentThread().getName());
}).start();

// 第二阶段：Java 5 线程池（推荐方式）
ExecutorService pool = Executors.newFixedThreadPool(4);
pool.submit(() -> doWork());

// 第三阶段：Java 8 CompletableFuture 异步编排
CompletableFuture.supplyAsync(() -> fetchData())
    .thenCombine(CompletableFuture.supplyAsync(() -> fetchMeta()),
        (data, meta) -> combine(data, meta));

// 第四阶段：Java 21 虚拟线程（推荐方式）
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> blockingIoCall());
}
```

## 三、并发编程核心知识体系

Java 并发编程涵盖以下核心领域：

### 1. 线程基础

- **线程创建**：继承 `Thread` 类、实现 `Runnable` / `Callable` 接口
- **线程状态**：NEW、RUNNABLE、BLOCKED、WAITING、TIMED_WAITING、TERMINATED
- **线程协作**：`wait()/notify()/notifyAll()`、`join()`、`Thread.yield()`

```java
// 线程状态转换示例
Thread t = new Thread(() -> {
    synchronized (lock) {
        lock.wait(); // RUNNABLE → WAITING
    }
});
t.start();        // NEW → RUNNABLE
t.join();         // 等待 TERMINATED
```

### 2. 锁与同步机制

- **内置锁**：`synchronized` 关键字（偏向锁 → 轻量级锁 → 重量级锁的锁升级过程）
- **显式锁**：`ReentrantLock`、`ReentrantReadWriteLock`、`StampedLock`
- **原子变量**：`AtomicInteger`、`LongAdder`、`AtomicReference`
- **CAS 操作**：Compare-And-Swap 无锁并发基础

### 3. 线程池与执行器

- **ThreadPoolExecutor** 七大参数及工作流程
- **ForkJoinPool** 工作窃取算法
- **虚拟线程**（Java 21+）：轻量级线程，替代传统线程池

### 4. 并发工具类

- **CountDownLatch**：等待多个操作完成
- **CyclicBarrier**：多线程 barrier 同步点
- **Semaphore**：信号量控制并发访问数
- **Phaser**：灵活的分阶段同步
- **Exchanger**：线程间数据交换

### 5. 并发集合

- **ConcurrentHashMap**：分段锁 / CAS + synchronized
- **CopyOnWriteArrayList**：写时复制的线程安全 List
- **BlockingQueue**：生产者-消费者模式的核心数据结构
- **ConcurrentLinkedQueue**：无锁并发队列

### 6. 可见性与有序性

- **volatile 关键字**：保证可见性和禁止指令重排序
- **happens-before 原则**：JMM（Java 内存模型）的核心规则
- **指令重排序**：编译器和处理器的优化行为

```java
// volatile 保证可见性
class VolatileExample {
    private volatile boolean flag = false;

    // 线程 A
    public void writer() {
        flag = true; // 写 volatile 变量
    }

    // 线程 B
    public void reader() {
        if (flag) { // 读 volatile 变量，一定能看到 true
            // ...
        }
    }
}
```

## 四、常见并发问题

| 问题类型 | 描述 | 解决方案 |
|---------|------|---------|
| 竞态条件 | 多个线程对共享变量的执行顺序不确定 | 加锁、原子操作 |
| 死锁 | 多个线程互相等待对方持有的锁 | 锁排序、超时获取、死锁检测 |
| 饥饿 | 某些线程长期得不到 CPU 时间片 | 公平锁、调整优先级 |
| 活锁 | 线程不断重试但始终无法推进 | 引入随机退避 |
| 内存可见性 | 一个线程的修改对其他线程不可见 | `volatile`、`synchronized`、`final` |

## 五、专题导航

以下是并发编程基础概念的子专题，涵盖锁机制和线程池的深入内容：

| 专题 | 说明 | 链接 |
|------|------|------|
| Java 锁机制 | `synchronized` 原理、锁升级、`ReentrantLock`、`StampedLock`、CAS、AQS 等 | [java-locks](./java-locks/README.md) |
| 线程池 | `ThreadPoolExecutor` 参数详解、工作队列、拒绝策略、ForkJoinPool、虚拟线程等 | [thread-pool](./thread-pool/README.md) |

## 六、最佳实践原则

1. **优先使用并发库**：`java.util.concurrent` 提供的工具类，而不是手动管理线程
2. **最小化共享状态**：不可变对象 > 线程封闭 > 同步访问
3. **锁的范围尽量小**：缩小临界区，减少锁持有时间
4. **避免在锁内执行耗时操作**：如 I/O、网络调用
5. **使用虚拟线程处理 I/O 密集型任务**（Java 21+）
6. **始终为线程池设置合理的参数**：根据 CPU 密集型或 I/O 密集型选择核心线程数
7. **正确处理中断**：响应 `InterruptedException`，不吞掉中断信号

---

← [返回 功能版本变更历史](../README.md)
