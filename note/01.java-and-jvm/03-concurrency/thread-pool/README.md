<!--
module:
  parent: java
  slug: java/thread-pool
  type: article
  category: 主模块子文章
  summary: Java 线程池（ThreadPoolExecutor）学习笔记
  depth: ⭐⭐⭐
-->

# Java 线程池（ThreadPoolExecutor）学习笔记

> **定位**：Java 线程池（ThreadPoolExecutor）学习笔记 的核心原理、实现与最佳实践。

---
## 引言：变更说明

全面梳理线程池原理、参数调优、拒绝策略与生产实践。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 一、为什么需要线程池

### 1.1 线程的代价

线程不是免费资源，每一次创建和销毁都有明确成本：

| 成本项 | 说明 | 典型量级 |
|--------|------|----------|
| **创建时间** | JVM 需向 OS 申请线程结构体、分配栈空间 | 约 0.1~1ms |
| **内存占用** | 每条线程默认栈大小 1MB（-Xss） | ~1MB / thread |
| **上下文切换** | 保存/恢复寄存器、TLB 失效、缓存行失效 | 数千 CPU 周期 |
| **调度开销** | OS 调度器需要在多条线程间做时间片分配 | CPU 核心数倍增效应 |

### 1.2 无线程池的问题

```java
// 反模式：每次请求都创建新线程
public void handleRequest(Request req) {
    new Thread(() -> process(req)).start();
    // 问题：
    // 1. 创建/销毁开销大
    // 2. 无限创建 → OOM
    // 3. 无复用、无统一管理
    // 4. 无法控制并发度
}
```

**核心问题：**

- **资源耗尽**：无限制创建线程导致 OOM（OutOfMemoryError）
- **响应延迟**：大量线程竞争 CPU，上下文切换频繁
- **缺乏管控**：无法监控、无法限流、无法优雅关闭
- **生命周期不可控**：线程创建后无法复用

### 1.3 线程池的价值

```text
┌─────────────────────────────────────────────────┐
│                  线程池                          │
│  ┌───────────────────────────────────────────┐  │
│  │  核心线程 (Core Threads)                   │  │
│  │  ██████ ██████ ██████ ██████              │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  任务队列 (Work Queue)                     │  │
│  │  [Task1] → [Task2] → [Task3] → ...        │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  非核心线程 (Non-Core Threads)             │  │
│  │  ░░░░░░ ░░░░░░                             │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
         ▲                        ▲
         │ 提交任务               │ 回收空闲线程
         └────────────────────────┘
```

**线程池带来的好处：**

- **降低开销**：线程复用，避免重复创建/销毁
- **控制并发**：限制最大线程数，防止资源耗尽
- **统一管理**：统一的监控、统计、生命周期管理
- **功能增强**：支持定时、周期、延迟执行等高级功能

---

## 二、ThreadPoolExecutor 核心参数

`ThreadPoolExecutor` 是 Java 线程池的核心实现类，有 7 个核心参数。

### 2.1 完整构造函数

```java
public ThreadPoolExecutor(
    int corePoolSize,            // 核心线程数
    int maximumPoolSize,         // 最大线程数
    long keepAliveTime,          // 空闲线程存活时间
    TimeUnit unit,               // 时间单位
    BlockingQueue<Runnable> workQueue,  // 工作队列
    ThreadFactory threadFactory,         // 线程工厂
    RejectedExecutionHandler handler     // 拒绝策略
)
```

### 2.2 参数详解

| 参数 | 类型 | 说明 | 推荐配置 |
|------|------|------|----------|
| **corePoolSize** | `int` | 核心线程数（常驻线程，即使空闲也不销毁，除非设置了 allowCoreThreadTimeOut） | CPU 密集型：CPU 核数 + 1；IO 密集型：CPU 核数 × 2 |
| **maximumPoolSize** | `int` | 最大线程数（核心线程 + 非核心线程的上限） | 与 corePoolSize 相同（使用有界队列时）；或根据负载动态调整 |
| **keepAliveTime** | `long` | 非核心线程空闲多久后被回收 | 30s~60s，IO 密集型可适当延长 |
| **unit** | `TimeUnit` | keepAliveTime 的时间单位 | `TimeUnit.SECONDS` |
| **workQueue** | `BlockingQueue` | 任务等待队列，核心线程满后任务排入此处 | 根据场景选择（见第四节） |
| **threadFactory** | `ThreadFactory` | 创建线程的工厂，可自定义线程名、优先级、守护状态等 | 务必使用自定义工厂，方便问题排查 |
| **handler** | `RejectedExecutionHandler` | 队列满且达到最大线程数时的拒绝策略 | 根据业务容忍度选择（见第五节） |

### 2.3 线程工厂示例

```java
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.atomic.AtomicInteger;

public class NamedThreadFactory implements ThreadFactory {

    private final AtomicInteger threadNumber = new AtomicInteger(1);
    private final String namePrefix;
    private final boolean daemon;

    public NamedThreadFactory(String poolName, boolean daemon) {
        this.namePrefix = poolName + "-thread-";
        this.daemon = daemon;
    }

    @Override
    public Thread newThread(Runnable r) {
        Thread t = new Thread(r, namePrefix + threadNumber.getAndIncrement());
        t.setDaemon(daemon);
        if (t.getPriority() != Thread.NORM_PRIORITY) {
            t.setPriority(Thread.NORM_PRIORITY);
        }
        return t;
    }
}
```

---

## 三、线程池工作流程

### 3.1 任务提交流程图

```text
              提交任务 (execute/submit)
                      │
                      ▼
            ┌───────────────────┐
            │ 核心线程是否已满？  │
            └───────┬───────────┘
                    │
          ┌─────────┼─────────┐
          │ NO              YES
          ▼                 ▼
   创建核心线程     ┌─────────────────┐
   执行任务        │ 队列是否已满？    │
                   └───────┬─────────┘
                           │
                 ┌─────────┼─────────┐
                 │ NO              YES
                 ▼                 ▼
            任务入队列       ┌─────────────────┐
            等待调度         │ 线程数是否达到    │
                            │   最大值？        │
                            └───────┬─────────┘
                                    │
                          ┌─────────┼─────────┐
                          │ NO              YES
                          ▼                 ▼
                   创建非核心线程     ┌──────────────┐
                   执行队列中任务     │ 执行拒绝策略  │
                                    └──────────────┘
```

### 3.2 文字版流程说明

```text
Step 1: 核心线程未满
    → 创建核心线程执行任务
    → 结束

Step 2: 核心线程已满，队列未满
    → 任务放入队列等待
    → 核心线程空闲时从队列取任务执行
    → 结束

Step 3: 核心线程已满，队列已满，线程数未达最大
    → 创建非核心线程执行任务
    → 结束后非核心线程空闲超过 keepAliveTime 则被回收
    → 结束

Step 4: 核心线程已满，队列已满，线程数已达最大
    → 触发 RejectedExecutionHandler
    → 根据拒绝策略处理（丢弃/抛异常/调用者执行等）
    → 结束
```

### 3.3 关键设计细节

```java
// 线程池内部用 ctl 这个 AtomicInteger 同时存储两个概念：
//   高 3 位 → runState（线程池运行状态）
//   低 29 位 → workerCount（活跃线程数）
//
// 五种运行状态：
//   RUNNING    : 接收新任务，处理队列任务
//   SHUTDOWN   : 不接收新任务，但继续处理队列任务
//   STOP       : 不接收新任务，不处理队列任务，中断正在执行的
//   TIDYING    : 所有任务已终止，workerCount 为 0，准备执行 terminated()
//   TERMINATED : terminated() 已完成

private final AtomicInteger ctl = new AtomicInteger(ctlOf(RUNNING, 0));
private static final int COUNT_BITS = Integer.SIZE - 3;  // 29
private static final int CAPACITY   = (1 << COUNT_BITS) - 1;

// runState 存储在高 3 位
private static final int RUNNING    = -1 << COUNT_BITS;
private static final int SHUTDOWN   =  0 << COUNT_BITS;
private static final int STOP       =  1 << COUNT_BITS;
private static final int TIDYING    =  2 << COUNT_BITS;
private static final int TERMINATED =  3 << COUNT_BITS;
```

### 3.4 execute() vs submit()

| 方法 | 返回值 | 异常处理 | 适用场景 |
|------|--------|----------|----------|
| `execute(Runnable)` | `void` | 异常直接抛出到调用线程 | 无需返回结果，不关心执行状态 |
| `submit(Runnable/Callable)` | `Future<?>` | 异常在 `Future.get()` 时包装为 `ExecutionException` | 需要返回值或需要检查执行状态 |

```java
// execute — 无返回值，异常直接抛出
executor.execute(() -> {
    // 此处的异常会传播到线程池的 UncaughtExceptionHandler
    throw new RuntimeException("unhandled");
});

// submit — 有 Future，异常延迟到 get()
Future<?> future = executor.submit(() -> {
    throw new RuntimeException("wrapped");
});
try {
    future.get();  // 抛出 ExecutionException
} catch (ExecutionException e) {
    Throwable cause = e.getCause();  // 原始异常
}
```

---

## 四、7 种内置阻塞队列

线程池的 `workQueue` 参数决定了任务的排队策略。Java 提供了 7 种内置的 `BlockingQueue` 实现。

### 4.1 队列总览

| 队列 | 数据结构 | 有界/无界 | 排序 | 典型用途 |
|------|----------|-----------|------|----------|
| **ArrayBlockingQueue** | 数组 | 有界 | FIFO | 最常用，控制并发 |
| **LinkedBlockingQueue** | 链表 | 可选（默认 Integer.MAX_VALUE） | FIFO | 吞吐量高，但默认无界 |
| **SynchronousQueue** | 无存储 | 有界（容量 0） | — | 直接传递，不排队 |
| **PriorityBlockingQueue** | 二叉堆 | 无界 | 优先级 | 按优先级调度 |
| **DelayQueue** | 二叉堆 + Delayed | 无界 | 延迟时间 | 定时/延迟任务 |
| **LinkedTransferQueue** | 链表 | 无界 | FIFO | 生产者直接传递给消费者 |
| **LinkedBlockingDeque** | 双向链表 | 可选 | 双端 FIFO | 工作窃取模式 |

### 4.2 ArrayBlockingQueue（推荐）

```java
// 有界数组队列，构造时必须指定容量
BlockingQueue<Runnable> queue = new ArrayBlockingQueue<>(100);

// 特点：
// 1. 固定容量，内存连续，缓存友好
// 2. 单锁（put 和 take 共用一把锁），并发度较低
// 3. 支持公平/非公平模式
BlockingQueue<Runnable> fairQueue = new ArrayBlockingQueue<>(100, true);
```

**适用场景：** 明确知道系统最大并发量的场景，防止 OOM。

### 4.3 LinkedBlockingQueue

```java
// 有界/无界链表队列
BlockingQueue<Runnable> unbounded = new LinkedBlockingQueue<>();       // 默认 Integer.MAX_VALUE
BlockingQueue<Runnable> bounded   = new LinkedBlockingQueue<>(100);    // 推荐：指定容量

// 特点：
// 1. 两把锁（putLock + takeLock），吞吐量高于 ArrayBlockingQueue
// 2. 节点分配带来 GC 压力
// 3. ⚠️ 默认无界！不指定容量 = 潜在 OOM
```

### 4.4 SynchronousQueue

```java
// 零容量队列，每个插入必须等待对应的取出
BlockingQueue<Runnable> syncQueue = new SynchronousQueue<>();

// 特点：
// 1. 不存储任何元素，相当于"手递手"传递
// 2. maximumPoolSize 必须足够大（或无界），否则容易触发拒绝
// 3. Executors.newCachedThreadPool() 使用的就是它

// 适用场景：
// 任务需要立即执行，不能排队等待
// 配合无界 maximumPoolSize 实现快速响应
```

### 4.5 PriorityBlockingQueue

```java
// 按优先级出队的无界队列
BlockingQueue<Runnable> pq = new PriorityBlockingQueue<>(
    11,  // 初始容量
    Comparator.comparingInt(r -> ((PriorityTask) r).getPriority())
);

// 特点：
// 1. 元素必须实现 Comparable 或提供 Comparator
// 2. ⚠️ 无界！高优先级任务持续入队 → 低优先级任务可能饿死
// 3. 所有元素按优先级排序，优先级高的先出队
```

### 4.6 DelayQueue

```java
// 延迟队列，元素必须实现 Delayed 接口
public class DelayedTask implements Delayed {
    private final long delayUntil;
    private final Runnable task;

    public DelayedTask(Runnable task, long delay, TimeUnit unit) {
        this.task = task;
        this.delayUntil = System.currentTimeMillis() + unit.toMillis(delay);
    }

    @Override
    public long getDelay(TimeUnit unit) {
        return unit.convert(delayUntil - System.currentTimeMillis(), TimeUnit.MILLISECONDS);
    }

    @Override
    public int compareTo(Delayed o) {
        return Long.compare(this.delayUntil, ((DelayedTask) o).delayUntil);
    }
}

// 特点：
// 1. 元素到期才能被 take() 取出
// 2. ⚠️ 无界！
// 3. Executors.newScheduledThreadPool() 底层使用 DelayedWorkQueue（基于 DelayQueue 优化）
```

### 4.7 LinkedTransferQueue

```java
// 支持直接传递的无界队列
LinkedTransferQueue<Runnable> transferQueue = new LinkedTransferQueue<>();

// 核心方法：
// transfer(E e)   — 阻塞直到有消费者取走元素
// tryTransfer(E)  — 没有等待的消费者则立即返回 false
// tryTransfer(E, timeout, unit) — 超时时间内等待消费者

// 特点：
// 1. 生产者可以直接"递"给消费者，跳过队列
// 2. 有等待消费者时效率极高
// 3. 无消费者时退化为普通无界队列
```

### 4.8 LinkedBlockingDeque

```java
// 双向链表队列，支持两端插入和取出
LinkedBlockingDeque<Runnable> deque = new LinkedBlockingDeque<>(100);

// 核心方法：
// addFirst / addLast
// takeFirst / takeLast
// putFirst / putLast

// 特点：
// 1. 支持工作窃取（Work-Stealing）模式
// 2. 每个线程有自己的 deque，空闲时可以"偷"其他线程的任务
// 3. Executors.newWorkStealingPool() 使用 ForkJoinPool（内部类似机制）
```

---

## 五、4 种拒绝策略

当队列已满且线程数达到 `maximumPoolSize` 时，线程池会调用 `RejectedExecutionHandler`。

### 5.1 策略对比

| 策略 | 行为 | 是否丢任务 | 是否阻塞 | 适用场景 |
|------|------|:----------:|:--------:|----------|
| **AbortPolicy**（默认） | 抛出 `RejectedExecutionException` | 否 | 否 | 需要明确感知拒绝，快速失败 |
| **CallerRunsPolicy** | 调用者线程自己执行该任务 | 否 | 是（间接限流） | 不允许丢任务，自带背压 |
| **DiscardPolicy** | 静默丢弃，不做任何处理 | 是 | 否 | 可容忍丢任务（如日志收集） |
| **DiscardOldestPolicy** | 丢弃队列中最老的任务，再重试入队 | 是 | 否 | 新任务优先，旧任务可丢弃 |

### 5.2 策略源码示意

```java
// 1. AbortPolicy — 默认策略，直接抛异常
public static class AbortPolicy implements RejectedExecutionHandler {
    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        throw new RejectedExecutionException(
            "Task " + r.toString() + " rejected from " + e.toString());
    }
}

// 2. CallerRunsPolicy — 调用者自己跑
public static class CallerRunsPolicy implements RejectedExecutionHandler {
    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        if (!e.isShutdown()) {
            r.run();  // 注意：是同步调用 run()，不是提交
        }
    }
}

// 3. DiscardPolicy — 静默丢弃
public static class DiscardPolicy implements RejectedExecutionHandler {
    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        // do nothing
    }
}

// 4. DiscardOldestPolicy — 丢弃最老的
public static class DiscardOldestPolicy implements RejectedExecutionHandler {
    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        if (!e.isShutdown()) {
            e.getQueue().poll();   // 移除队列头（最老的任务）
            e.execute(r);          // 重新提交当前任务
        }
    }
}
```

### 5.3 自定义拒绝策略

```java
// 实际生产中最推荐的做法：自定义拒绝策略，结合监控/告警/降级
RejectedExecutionHandler customHandler = (r, executor) -> {
    // 1. 记录监控指标
    MetricsCollector.increment("threadpool.reject.count");

    // 2. 记录日志（包含线程池状态）
    log.error("Thread pool rejected! poolSize={}, queueSize={}, active={}, task={}",
        executor.getPoolSize(),
        executor.getQueue().size(),
        executor.getActiveCount(),
        r.toString());

    // 3. 降级策略：写入持久化存储 / 发送消息队列
    PersistenceQueue.offer(r);

    // 4. 如果连降级存储也满了，才抛异常
    if (!PersistenceQueue.canAccept()) {
        throw new RejectedExecutionException("Both pool and fallback queue are full");
    }
};
```

---

## 六、Executors 工厂方法及其问题

### 6.1 四种工厂方法

```java
// 1. 固定大小线程池
ExecutorService fixed = Executors.newFixedThreadPool(10);
// → corePoolSize = 10, maximumPoolSize = 10,
//   keepAliveTime = 0, workQueue = LinkedBlockingQueue (无界!)

// 2. 缓存线程池
ExecutorService cached = Executors.newCachedThreadPool();
// → corePoolSize = 0, maximumPoolSize = Integer.MAX_VALUE,
//   keepAliveTime = 60s, workQueue = SynchronousQueue

// 3. 单线程池
ExecutorService single = Executors.newSingleThreadExecutor();
// → corePoolSize = 1, maximumPoolSize = 1,
//   keepQueue = LinkedBlockingQueue (无界!)

// 4. 定时线程池
ScheduledExecutorService scheduled = Executors.newScheduledThreadPool(5);
// → corePoolSize = 5, maximumPoolSize = Integer.MAX_VALUE,
//   workQueue = DelayedWorkQueue (无界!)
```

### 6.2 工厂方法的问题（阿里巴巴 Java 开发手册明确禁止）

| 工厂方法 | 风险 | 可能后果 |
|----------|------|----------|
| `newFixedThreadPool` | 使用无界 `LinkedBlockingQueue` | 任务堆积 → OOM |
| `newSingleThreadExecutor` | 同上 | 同上 |
| `newCachedThreadPool` | `maximumPoolSize = Integer.MAX_VALUE` | 线程无限创建 → OOM / CPU 100% |
| `newScheduledThreadPool` | `maximumPoolSize = Integer.MAX_VALUE` + 无界延迟队列 | 同上 |

```text
┌────────────────────────────────────────────────────────────┐
│  Executors.newFixedThreadPool(10) 的隐藏风险                │
│                                                            │
│  线程池配置:                                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  core=10  max=10  queue=LinkedBlockingQueue(无界)    │  │
│  │                                                      │  │
│  │  任务源源不断地涌入...                                │  │
│  │  [Task]→[Task]→[Task]→[Task]→[Task]→[Task]→...→OOM  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  结论：看似安全的固定线程池，队列无界 = 定时炸弹            │
└────────────────────────────────────────────────────────────┘
```

### 6.3 正确写法

```java
// 永远不要使用 Executors 工厂方法，改为手动创建 ThreadPoolExecutor
ExecutorService executor = new ThreadPoolExecutor(
    10,                          // corePoolSize
    20,                          // maximumPoolSize
    60L,                         // keepAliveTime
    TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(100),   // 有界队列！
    new NamedThreadFactory("biz-pool", false),
    new ThreadPoolExecutor.CallerRunsPolicy()
);
```

---

## 七、线程池监控

### 7.1 核心监控指标

```java
ThreadPoolExecutor executor = ...;

// 运行时指标
int poolSize     = executor.getPoolSize();        // 当前线程数
int activeCount  = executor.getActiveCount();     // 正在执行任务的线程数
int queueSize    = executor.getQueue().size();    // 队列中等待的任务数
long completed   = executor.getCompletedTaskCount(); // 已完成任务总数
long taskCount   = executor.getTaskCount();       // 已接收任务总数
boolean shutdown = executor.isShutdown();         // 是否已关闭
boolean terminated = executor.isTerminated();     // 是否已终止
```

### 7.2 监控看板设计

```text
┌────────────────── 线程池监控面板 ──────────────────┐
│                                                    │
│  Pool: biz-order-pool                              │
│  ┌──────────────────────────────────────────────┐ │
│  │  当前线程数:  15 / 20     ████████░░░░░░ 75% │ │
│  │  活跃线程数:  12           ████████░░░░░░ 60% │ │
│  │  队列深度:    87 / 100    ██████████░░░ 87%   │ │
│  │  已完成任务:  1,234,567                      │ │
│  │  累计拒绝数:  3                               │ │
│  │  状态:        RUNNING                         │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  告警阈值:                                          │
│  ⚠ 队列深度 > 80% → WARNING                        │
│  🔴 队列深度 > 95% → CRITICAL                      │
│  🔴 拒绝策略触发 → CRITICAL                        │
└────────────────────────────────────────────────────┘
```

### 7.3 监控代码示例

```java
import java.util.concurrent.*;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class MonitoredThreadPoolExecutor extends ThreadPoolExecutor {

    private volatile long rejectCount = 0;

    public MonitoredThreadPoolExecutor(int corePoolSize, int maximumPoolSize,
            long keepAliveTime, TimeUnit unit,
            BlockingQueue<Runnable> workQueue,
            ThreadFactory threadFactory,
            RejectedExecutionHandler handler) {
        super(corePoolSize, maximumPoolSize, keepAliveTime, unit,
              workQueue, threadFactory, (r, executor) -> {
            rejectCount++;
            handler.rejectedExecution(r, (ThreadPoolExecutor) executor);
        });
    }

    /** 定时打印线程池状态 */
    public void logPoolStatus() {
        log.info("ThreadPool Status: [poolSize={}, active={}, queueSize={}, "
                + "completed={}, rejected={}, isShutdown={}]",
            getPoolSize(),
            getActiveCount(),
            getQueue().size(),
            getCompletedTaskCount(),
            rejectCount,
            isShutdown());
    }

    /** 获取利用率 */
    public double getUtilization() {
        return (double) getActiveCount() / getMaximumPoolSize();
    }
}
```

### 7.4 Prometheus 集成示例

```java
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.binder.MeterBinder;

public class ThreadPoolMetrics implements MeterBinder {

    private final ThreadPoolExecutor executor;
    private final String poolName;

    public ThreadPoolMetrics(ThreadPoolExecutor executor, String poolName) {
        this.executor = executor;
        this.poolName = poolName;
    }

    @Override
    public void bindTo(MeterRegistry registry) {
        Gauge.builder("threadpool.size", executor, ThreadPoolExecutor::getPoolSize)
            .tag("pool", poolName)
            .register(registry);

        Gauge.builder("threadpool.active", executor, ThreadPoolExecutor::getActiveCount)
            .tag("pool", poolName)
            .register(registry);

        Gauge.builder("threadpool.queue.size", executor,
                e -> e.getQueue().size())
            .tag("pool", poolName)
            .register(registry);

        Gauge.builder("threadpool.queue.remaining", executor,
                e -> e.getQueue().remainingCapacity())
            .tag("pool", poolName)
            .register(registry);

        Gauge.builder("threadpool.completed", executor,
                ThreadPoolExecutor::getCompletedTaskCount)
            .tag("pool", poolName)
            .register(registry);
    }
}
```

---

## 八、最佳实践

### 8.1 线程数配置

| 任务类型 | 公式 | 示例（8 核） | 原因 |
|----------|------|-------------|------|
| **CPU 密集型** | `CPU 核数 + 1` | 9 | +1 防止页缺失时 CPU 空闲 |
| **IO 密集型** | `CPU 核数 × (1 + 等待时间/计算时间)` | 16~32 | IO 等待期间 CPU 可执行其他任务 |
| **混合型** | 拆分任务或取中间值 | 12~16 | 尽量拆分为纯 CPU + 纯 IO 两个线程池 |

```java
// 快速估算
int cpuCores = Runtime.getRuntime().availableProcessors();

// CPU 密集型
int cpuPoolSize = cpuCores + 1;

// IO 密集型（假设 IO 等待 / 计算 = 3）
int ioPoolSize = cpuCores * (1 + 3);  // = cpuCores * 4
```

### 8.2 队列选择决策树

```text
                任务是否需要立即执行？
                /                    \
              YES                    NO
               |                      |
        SynchronousQueue          是否需要控制并发量？
        (配较大 maxPoolSize)       /                  \
                                 YES                  NO
                                  |                    |
                          ArrayBlockingQueue     LinkedBlockingQueue
                          (指定有界容量)         (⚠️ 必须指定容量！)
```

### 8.3 线程池生命周期管理

```java
public class ThreadPoolLifecycle {

    private final ThreadPoolExecutor executor;

    // 1. 创建
    public ThreadPoolLifecycle() {
        executor = new ThreadPoolExecutor(
            5, 10, 60L, TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(100),
            new NamedThreadFactory("my-pool", false),
            new ThreadPoolExecutor.CallerRunsPolicy()
        );
    }

    // 2. 优雅关闭
    public void shutdown() {
        // 停止接收新任务
        executor.shutdown();
        try {
            // 等待现有任务完成（最多 60 秒）
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                // 超时仍未完成 → 强制中断
                List<Runnable> pending = executor.shutdownNow();
                log.warn("Force shutdown, {} tasks pending", pending.size());
                if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
                    log.error("Pool did not terminate");
                }
            }
        } catch (InterruptedException e) {
            // 重新中断，确保调用者知道被中断
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}
```

### 8.4 完整生产级配置示例

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.util.concurrent.*;

@Configuration
public class ThreadPoolConfig {

    @Bean("orderExecutor")
    public Executor orderExecutor() {
        return new ThreadPoolExecutor(
            10,                                      // 核心线程
            20,                                      // 最大线程
            60L,                                     // 空闲回收时间
            TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(500),            // 有界队列
            new NamedThreadFactory("order-pool", false),
            (r, executor) -> {
                // 自定义拒绝策略：记录日志 + 告警 + 降级
                log.error("Order task rejected! poolSize={}, queueSize={}, active={}",
                    executor.getPoolSize(),
                    executor.getQueue().size(),
                    executor.getActiveCount());
                // 发送告警
                AlertService.send("订单线程池已满，触发拒绝策略");
                // 降级：持久化到数据库，后续补偿
                CompensationQueue.offer(r);
            }
        );
    }

    @Bean("queryExecutor")
    public Executor queryExecutor() {
        // 查询类 IO 密集型任务
        int cores = Runtime.getRuntime().availableProcessors();
        return new ThreadPoolExecutor(
            cores * 2,                               // 核心线程数较多
            cores * 4,                               // 最大线程数
            30L,
            TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(1000),
            new NamedThreadFactory("query-pool", false),
            new ThreadPoolExecutor.CallerRunsPolicy()  // 不允许丢弃
        );
    }
}
```

### 8.5 常见陷阱与避坑指南

| 陷阱 | 后果 | 正确做法 |
|------|------|----------|
| 使用 `Executors.newFixedThreadPool` | 无界队列 OOM | 手动创建 + `ArrayBlockingQueue` |
| 使用 `Executors.newCachedThreadPool` | 线程无限创建 OOM | 手动创建 + 有限 `maximumPoolSize` |
| 队列使用 `LinkedBlockingQueue` 不指定容量 | 默认 `Integer.MAX_VALUE` OOM | 永远指定容量 |
| `maximumPoolSize` 在有界队列时与 `corePoolSize` 不同 | 非核心线程几乎不会被创建 | 有界队列场景下两者设为相同 |
| 线程池中的线程抛出未捕获异常 | 任务静默失败 | 使用 `submit()` + `Future.get()` 或在 `Runnable` 中捕获 |
| 没有自定义 ThreadFactory | 线程名默认 `pool-N-thread-M`，无法排查 | 始终使用自定义工厂 |
| `shutdown()` 后继续提交任务 | 抛出 `RejectedExecutionException` | 配合 `isShutdown()` 检查 |
| 使用 `DiscardPolicy` 但不记录日志 | 任务丢失无感知 | 自定义策略 + 监控 + 告警 |
| 父线程 ThreadLocal 未传递给子线程 | 子线程获取不到上下文（如 userId、traceId） | 使用 `TaskDecorator` / `InheritableThreadLocal` / TransmittableThreadLocal |
| Spring 中 `@Async` 使用默认线程池 | 默认队列容量 `Integer.MAX_VALUE` | 自定义 `TaskExecutor` Bean |

### 8.6 线程池检查清单

```text
[ ] 是否手动创建 ThreadPoolExecutor（不使用 Executors 工厂）
[ ] corePoolSize 和 maximumPoolSize 是否合理（基于 CPU/IO 类型）
[ ] 是否使用了有界队列（ArrayBlockingQueue 或指定容量的 LinkedBlockingQueue）
[ ] 是否自定义了 ThreadFactory（有意义的线程名前缀）
[ ] 是否配置了合适的拒绝策略（建议 CallerRunsPolicy 或自定义）
[ ] 是否实现了监控指标（poolSize、queueSize、rejectCount）
[ ] 是否配置了告警（队列深度 > 80%、拒绝策略触发）
[ ] 是否有优雅关闭逻辑（shutdown + awaitTermination）
[ ] 任务异常是否有处理（try-catch 或 Future.get）
[ ] ThreadLocal 上下文是否需要传递（traceId、userId）
```

---

> **总结**：线程池是 Java 并发编程的基石。核心要记住一句话——
> **"永远不要信任 Executors 工厂方法，永远手动创建 ThreadPoolExecutor，永远使用有界队列，永远自定义 ThreadFactory 和拒绝策略。"**

---

## 九、Worker 回收机制（OpenJDK 源码级）

### 9.1 Worker 的本质：既是 Runnable 又是 AQS

`ThreadPoolExecutor` 内部通过 `Worker` 类同时承担「任务执行载体」和「独占可中断锁」两个职责。

```java
// OpenJDK: src/java.base/java/util/concurrent/ThreadPoolExecutor.java
private final class Worker extends AbstractQueuedSynchronizer implements Runnable {
    final Thread thread;        // 真正执行的 OS 线程
    Runnable firstTask;         // 创建时领到的第一个任务（避免先入队再取出）

    Worker(Runnable firstTask) {
        this.firstTask = firstTask;
        // 在构造里就 setState(1)，表示「启动时即占用」
        setState(-1); // inhibit interrupts until runWorker
        this.thread = getThreadFactory().newThread(this);
    }

    public void run() {
        runWorker(this);   // 转入 Worker 主循环
    }

    // tryAcquire/tryRelease 仅 0↔1，用来实现「独占当前线程」
    protected boolean tryAcquire(int unused) {
        if (compareAndSetState(0, 1)) {
            setExclusiveOwnerThread(Thread.currentThread());
            return true;
        }
        return false;
    }
}
```

**关键设计点**：

- Worker 既是 Runnable（被新 Thread 持有后跑 `runWorker`），又是 AQS（`state` 字段：-1=初始，0=空闲，1=正在跑任务）
- 为什么不直接用 Thread + Runnable？因为需要「中断前检查 Worker 是否正在跑任务」—— `tryLock()` 成功才真正中断（见 `interruptIdleWorkers`）

### 9.2 getTask()：Worker 主循环的取任务方法

这是 worker 回收机制的**核心入口**。源码（OpenJDK 21+）：

```java
private Runnable getTask() {
    boolean timed = false;   // 本轮循环是否需要限时等待

    for (;;) {
        int c = ctl.get();
        int rs = runStateOf(c);     // 线程池运行状态

        // 状态检测：SHUTDOWN + 队列空 → 退出；STOP → 必退出
        if (rs >= SHUTDOWN && (rs >= STOP || workQueue.isEmpty())) {
            decrementWorkerCount();
            return null;
        }

        int wc = workerCountOf(c);

        // 是否启用超时回收：
        //   allowCoreThreadTimeOut=true → 核心线程也限时回收
        //   wc > corePoolSize           → 非核心线程限时回收
        boolean allowCoreTimeout = allowCoreThreadTimeOut;
        boolean timed = allowCoreTimeout || wc > corePoolSize;

        // 二次校验：超过 maxPoolSize 或（限时回收且队列空）→ 退出
        if ((wc > maximumPoolSize) || (timed && workQueue.isEmpty())) {
            if (compareAndDecrementWorkerCount(c)) return null;
            continue;
        }

        try {
            Runnable r = timed
                ? workQueue.poll(keepAliveTime, unit)   // 非核心：限时等待
                : workQueue.take();                     // 核心：永久阻塞

            if (r != null) return r;
            // r == null 表示 poll 超时（仅限时）→ 进入下次循环 → 触发回收
        } catch (InterruptedException retry) {
            // 中断被忽略，重试
        }
    }
}
```

**源码中两条关键路径**：

| 场景 | 调用 | 行为 |
|------|------|------|
| 核心线程 + 队列空 | `workQueue.take()` | 永久阻塞，直到新任务入队 |
| 非核心线程 + 队列空 | `workQueue.poll(keepAliveTime, unit)` | 阻塞 keepAliveTime 后返回 null → 触发回收 |

### 9.3 触发回收的三种情况

当 `getTask()` 返回 `null` 时，外层 `runWorker()` 会退出循环，进而调用 `processWorkerExit()`：

```text
getTask() 返回 null 的三种情况
│
├─ 1. 线程池状态 ≥ STOP                 → 必须退出
├─ 2. wc > maximumPoolSize（动态缩容） → 退出多余 worker
└─ 3. timed && workQueue.isEmpty()      → 非核心线程空闲超时
```

### 9.4 processWorkerExit：剔除 + 补偿新建

```java
private void processWorkerExit(Worker w, boolean completedAbruptly) {
    if (completedAbruptly)  // 异常退出 → 补偿 workerCount
        decrementWorkerCount();

    ReentrantLock mainLock = this.mainLock;
    mainLock.lock();
    try {
        completedTaskCount += w.completedTasks;
        workers.remove(w);
    } finally {
        mainLock.unlock();
    }

    tryTerminate();        // 尝试触发 TERMINATED 状态

    // 关键补偿逻辑：
    int c = ctl.get();
    if (runStateLessThan(c, STOP)) {
        if (!completedAbruptly) {
            // 队列非空时，至少保留一个 worker 兜底消费
            int min = allowCoreThreadTimeOut ? 0 : corePoolSize;
            if (min == 0 && !workQueue.isEmpty())
                min = 1;
            if (workerCountOf(c) >= min)
                return;    // 已有足够 worker → 不补偿
        }
        addWorker(null, false);   // 补偿新建一个 worker
    }
}
```

**核心补偿规则**：如果线程池没在 STOP 状态，且当前 worker 数少于 `corePoolSize`（或队列非空），会自动 `addWorker(null, false)` 补偿一个 worker。

> 这就是为什么「即使你把 `corePoolSize` 设成 0，任务来时线程池也会至少启动 1 个 worker 去消费队列」——这就是 `addWorker(null, false)` 的补偿机制在起作用。

---

## 十、拒绝策略矩阵全景

### 10.1 4 个内置策略对比矩阵

| 策略 | 行为 | 是否丢任务 | 是否阻塞调用方 | 是否抛异常 | 适用场景 | 源码位置（OpenJDK 21） |
|------|------|:----------:|:--------------:|:----------:|----------|------------------------|
| **AbortPolicy**（默认） | 抛出 `RejectedExecutionException` | 否 | 否 | 是 | 需要明确感知拒绝、快速失败 | `ThreadPoolExecutor.java:2397` |
| **CallerRunsPolicy** | 调用者线程同步执行 `r.run()` | 否 | 是（间接限流） | 否 | 不允许丢任务，需要天然背压 | `ThreadPoolExecutor.java:2423` |
| **DiscardPolicy** | 静默丢弃，连日志都没有 | 是 | 否 | 否 | 可容忍丢任务（日志收集、非关键统计） | `ThreadPoolExecutor.java:2450` |
| **DiscardOldestPolicy** | `queue.poll()` 丢队首 → `execute(r)` 重试 | 是（丢老的） | 否 | 否 | 新任务优先级更高（如实时行情） | `ThreadPoolExecutor.java:2432` |

### 10.2 源码逐字对照

```java
// === AbortPolicy ===
public static class AbortPolicy implements RejectedExecutionHandler {
    public AbortPolicy() { }
    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        throw new RejectedExecutionException(
            "Task " + r.toString() + " rejected from " + e.toString());
    }
}

// === CallerRunsPolicy ===
public static class CallerRunsPolicy implements RejectedExecutionHandler {
    public CallerRunsPolicy() { }
    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        if (!e.isShutdown()) {
            r.run();    // 注意：是 run() 不是 start()；同步阻塞调用线程
        }
    }
}

// === DiscardPolicy ===
public static class DiscardPolicy implements RejectedExecutionHandler {
    public DiscardPolicy() { }
    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        // do nothing —— 比 AbortPolicy 还要安静！
    }
}

// === DiscardOldestPolicy ===
public static class DiscardOldestPolicy implements RejectedExecutionHandler {
    public DiscardOldestPolicy() { }
    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        if (!e.isShutdown()) {
            e.getQueue().poll();      // 丢老的
            e.execute(r);             // 重试提交（可能再次失败）
        }
    }
}
```

### 10.3 何时需要自定义

自定义 `RejectedExecutionHandler` 的三大典型场景：

1. **监控埋点**：调用方 `Metrics.counter("executor_rejected_total").increment()` 上报 Prometheus
2. **告警触发**：通过 IM / PagerDuty 通知 oncall
3. **降级持久化**：写入磁盘队列 / Kafka / DB，后续异步补偿（例：订单线程池拒绝时写入 Redis Stream）

> 生产环境**几乎都是自定义策略**。4 个内置策略只有 CallerRunsPolicy 在 RPC 之外的纯内部任务中可以勉强直接使用，其他都需要包装。

---

## 十一、监控告警体系

### 11.1 关键监控指标

| 指标 | API | 类型 | 说明 |
|------|-----|------|------|
| `pool_size` | `getPoolSize()` | Gauge | 当前 worker 数 |
| `active_count` | `getActiveCount()` | Gauge | 正在执行任务的 worker 数 |
| `queue_size` | `getQueue().size()` | Gauge | 队列中待执行任务数 |
| `queue_remaining` | `getQueue().remainingCapacity()` | Gauge | 队列剩余容量（无界队列返回 `Integer.MAX_VALUE`） |
| `completed_task_count` | `getCompletedTaskCount()` | Counter | 累计完成任务数 |
| `largest_pool_size` | `getLargestPoolSize()` | Gauge | 历史最大线程数（监控瞬时扩容） |
| `task_count` | `getTaskCount()` | Counter | 已接收任务总数（含拒绝） |
| `rejected_count` | 自定义 | Counter | 累计拒绝任务数（需自定义策略时统计） |

### 11.2 Micrometer + Prometheus 集成

```java
import io.micrometer.core.instrument.Metrics;
import io.micrometer.core.instrument.binder.jvm.ExecutorServiceMetrics;
import java.util.concurrent.ThreadPoolExecutor;

// 一行接入 Micrometer：自动生成全套指标
ExecutorService monitored = ExecutorServiceMetrics.monitor(
    Metrics.globalRegistry,
    executor,
    "order-executor"     // 指标名前缀
);
```

Micrometer 自动导出的指标名（Prometheus 风格）：

| Prometheus 指标 | 含义 |
|----------------|------|
| `executor_pool_size_threads` | 当前线程数 |
| `executor_pool_core_threads` | 核心线程数 |
| `executor_pool_max_threads` | 最大线程数 |
| `executor_queue_size` | 队列深度 |
| `executor_rejected_total` | 累计拒绝数 |
| `executor_seconds_count` | 任务执行总次数（Histogram） |
| `executor_seconds_sum` | 任务执行总耗时 |
| `executor_seconds_max` | 单任务最长耗时 |
| `executor_idle_seconds_count` | 空闲时长 |

### 11.3 告警阈值设计

| 阈值 | 严重度 | 触发条件 | 处置建议 |
|------|--------|----------|----------|
| 队列使用率 > 80% | WARNING | 持续 5 分钟 | 排查上游 QPS 是否异常 |
| 队列使用率 > 95% | CRITICAL | 持续 1 分钟 | 立即扩容 / 限流 |
| 拒绝策略触发 | CRITICAL | 任意一次 | 立即介入（已对业务产生影响） |
| 活跃线程数 > 90% × maxPoolSize | WARNING | 持续 5 分钟 | 准备扩容 |
| 单任务最长耗时 > 30s | WARNING | 任意一次 | 排查慢任务 |
| `completedTaskCount` 不增长 | CRITICAL | 持续 1 分钟 | 线程池已死锁或卡死 |

### 11.4 Grafana 看板（PromQL 片段）

```promql
# 队列使用率
executor_queue_size / (executor_queue_size + executor_queue_remaining)

# 拒绝率（按 5 分钟聚合）
rate(executor_rejected_total[5m])

# 任务平均耗时
rate(executor_seconds_sum[5m]) / rate(executor_seconds_count[5m])

# 线程池利用率
executor_pool_size_threads / executor_pool_max_threads

# P99 任务耗时（假设已配置 Histogram percentile）
histogram_quantile(0.99, rate(executor_seconds_bucket[5m]))
```

---

## 十二、主流框架线程池实战

### 12.1 Tomcat 线程池

Tomcat 自定义了一个 `TaskQueue`（继承 `LinkedBlockingQueue`），通过「强制触发新建 worker」绕过 JDK 的「核心线程满 → 入队」默认行为。

```text
JDK 默认行为：
    core 满 → 入队 → 队列满 → 才会创建非核心线程

Tomcat 改造后：
    core 满 → 入队 → 队列满 → 创建非核心线程（保留 JDK 行为）
    但 Tomcat 又加了 force()：
        public boolean force(Runnable o) {
            // 强制把任务入队，跳过队列容量检查
            // 用于「如果当前 thread 数 < maxThreads，就先入队、不创建新线程」
        }
```

关键参数（`server.xml` / `application.yml`）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `server.tomcat.threads.max` | 200 | 最大线程数（= maximumPoolSize） |
| `server.tomcat.threads.min-spare` | 25 | 核心线程数（= corePoolSize） |
| `server.tomcat.accept-count` | 100 | 等待队列容量（= workQueue 容量） |
| `server.tomcat.max-connections` | 8192 | 最大连接数 |
| `server.tomcat.connection-timeout` | 20000 | 连接超时（ms） |

源码路径：`org.apache.tomcat.util.threads.ThreadPoolExecutor`

### 12.2 Dubbo 线程池

Dubbo 通过 SPI 机制（`@SPI` 注解）实现可插拔线程池，4 种内置实现：

| 实现类 | 对应 JDK 类型 | 特点 |
|--------|--------------|------|
| `FixedThreadPool` | `newFixedThreadPool` 等价 | 固定大小 + 无界队列（生产慎用） |
| `CachedThreadPool` | `newCachedThreadPool` 等价 | 弹性扩缩 + SynchronousQueue |
| `LimitedThreadPool` | 自定义 | 固定大小 + 有界队列（**推荐生产用**） |
| `EagerThreadPool` | 自定义 | **优先入队，队列满才创建线程**（兼顾吞吐+资源） |

**Eager 模式核心源码**（`EagerThreadPoolExecutor`）：

```java
// 自定义 TaskQueue：先尝试入队，入队失败才创建线程
public class EagerThreadPoolExecutor extends ThreadPoolExecutor {
    // 重写 offer：返回 false 表示「入队失败，需要创建新线程」
    public boolean offer(Runnable r) {
        if (executor.getPoolSize() < executor.getMaximumPoolSize()) {
            return false;    // 故意返回 false → 触发 addWorker 创建新线程
        }
        return super.offer(r);
    }
}
```

**Eager 模式的价值**：兼顾「突发流量时快速响应」（避免任务在队列里等）和「资源受控」（不会无限扩线程）。Dubbo 的默认线程池正是 eager。

### 12.3 Netty 线程池

Netty 的业务线程池是 `io.netty.util.concurrent.UnorderedThreadPoolExecutor`：

```java
// Netty 业务线程池 - 继承自 JDK ThreadPoolExecutor
public class UnorderedThreadPoolExecutor extends ThreadPoolExecutor {

    // 关键差异 1: 使用 MPSC 队列（多生产者单消费者），吞吐量高于 LinkedBlockingQueue
    private final MpscLinkedQueue<Runnable> taskQueueMPSC;

    // 关键差异 2: execute() 时如检测到 OOM / 拒绝，打印警告日志
    public void execute(Runnable command) {
        // ...
        try {
            super.execute(command);
        } catch (RejectedExecutionException e) {
            // Netty 的特色：拒绝时打印警告日志（便于排查）
            logger.warn("Rejected task from {}", this, e);
            throw e;
        }
    }
}
```

关键差异：

| 维度 | JDK ThreadPoolExecutor | Netty UnorderedThreadPoolExecutor |
|------|----------------------|-----------------------------------|
| 队列 | `LinkedBlockingQueue` | **`MpscLinkedQueue`**（更高的并发入队性能） |
| 拒绝日志 | 无 | 警告日志 |
| EventExecutor 集成 | 无 | 继承 `EventExecutorGroup`，Future 可监听 |
| 任务有序性 | FIFO 严格有序 | Unordered 名字明示不保证顺序 |

> Netty EventLoop **不是** `UnorderedThreadPoolExecutor`——EventLoop 是单线程串行；`UnorderedThreadPoolExecutor` 是 Netty 给业务代码用的并行线程池（不在 EventLoop 跑长任务时使用）。

---

## 十三、美团动态线程池案例

### 13.1 背景

美团 2018 年开源的「线程池参数动态化」方案，已在生产环境大规模落地。核心问题：

- 业务高峰时线程池参数（corePoolSize / maximumPoolSize / queueSize）无法实时调整
- 修改需要重启应用，QPS 一过峰值又得改回来

### 13.2 解决方案

美团封装了 `DynamicThreadPoolExecutor`，继承自 JDK `ThreadPoolExecutor`：

```java
public class DynamicThreadPoolExecutor extends ThreadPoolExecutor {

    // Nacos 配置中心监听
    @NacosConfigListener(dataId = "thread-pool-config")
    public void onConfigChanged(ThreadPoolConfig newConfig) {
        // 反射动态修改父类 private final 字段
        ReflectUtils.setField(corePoolSizeField, this, newConfig.getCoreSize());
        ReflectUtils.setField(maximumPoolSizeField, this, newConfig.getMaxSize());
        // ...
    }

    // 改造拒绝策略：触发告警 + 落库
    public void rejectedExecution(Runnable r) {
        // ... 同 §五 自定义拒绝策略
    }
}
```

### 13.3 关键能力

| 能力 | 说明 |
|------|------|
| 参数运行时修改 | 通过反射绕过 `final` 限制，修改 `corePoolSize` 等 |
| 配置中心下发 | Nacos / Apollo 监听数据变更事件 |
| 实时监控 | JMX / Prometheus 暴露指标 |
| 告警联动 | 拒绝 / 队列满自动通知 oncall |

### 13.4 引用文章

- **标题**：美团技术团队「Java 线程池实现原理及其在美团业务中的实践」
- **作者**：美团技术团队
- **发表年份**：2018 年
- **文章地址**：tech.meituan.com/2020/04/02/java-pooling-pratice.html
- **核心论点**：线程池参数应当支持运行时动态调整，而不是停机 + 重启

---

## 十四、参数调优公式

### 14.1 经典公式（Brian Goetz《Java Concurrency in Practice》）

```text
Nthreads = Ncpu × Ucpu × (1 + W/C)

其中：
  Ncpu   = CPU 核数（Runtime.getRuntime().availableProcessors()）
  Ucpu   = 目标 CPU 利用率（0~1，建议 0.5~0.8）
  W      = 等待时间（wait time，如 IO / 网络等待）
  C      = 计算时间（compute time）
  W/C    = 「等待/计算」比
```

### 14.2 简化经验值

| 任务类型 | 经验公式 | 8 核示例 | 原因 |
|----------|----------|----------|------|
| **CPU 密集型** | `Ncpu + 1` | 9 | +1 防止页缺失时 CPU 空闲 |
| **IO 密集型（DB/网络）** | `2 × Ncpu` | 16 | IO 等待期间 CPU 可执行其他任务 |
| **IO 密集型（远程 RPC）** | `3 × Ncpu ~ 4 × Ncpu` | 24~32 | 远程调用等待更久 |

### 14.3 自适应公式（更精细）

```java
// 假设线程 A：50% 时间在 IO 等待，50% 时间计算
// → 1 个线程占用 CPU 50%，那么 Ncpu × 2 是合理的

double ioRatio = 0.5;          // IO 占比 50%
double cpuPerThread = 1.0 - ioRatio;  // 每个线程占 CPU 50%
int Nthreads = (int) (Ncpu / cpuPerThread);  // = Ncpu × 2
```

### 14.4 压测调优流程

```text
1. 初始配置：CPU 密集=Ncpu+1，IO 密集=2×Ncpu
   ↓
2. 压测：观察 CPU 利用率、线程池利用率、队列使用率
   ↓
3. 调优矩阵：
   CPU 高 + 线程池利用率低 → 加线程数
   CPU 低 + 线程池利用率高 → 任务可能阻塞 IO，看 W/C
   队列使用率高             → 加线程或扩队列容量（避免 OOM）
   ↓
4. 生产灰度 → 全量 → 持续监控
```

---

## 十五、JDK 演进史

| 年份 | 里程碑 | 关键贡献 |
|------|--------|----------|
| 2004 | Doug Lea 出版《Java Concurrency in Practice》 | 业界线程池模式的标准定义（Brian Goetz 等合著） |
| 2006 | JDK 5（Java 5.0） | 引入 `java.util.concurrent` + `ThreadPoolExecutor` |
| 2011 | JDK 7 | 引入 `ForkJoinPool`（Doug Lea 设计，工作窃取） |
| 2014 | JDK 8 | 引入 `CompletableFuture`（组合式异步） |
| 2018 | 美团开源 DynamicThreadPoolExecutor | 线程池参数动态化（生产落地） |
| 2020 | JDK 14 | Virtual Threads（Loom 项目）Preview |
| 2023 | JDK 21 | Virtual Threads GA（**JEP 444**） |

> Virtual Threads ≠ 替代线程池：Virtual Threads 适合 IO 密集型任务；CPU 密集型仍应使用 `ForkJoinPool.commonPool()` 或自定义线程池。

---

## 十六、反直觉误区清单

### 16.1 ❌「corePoolSize 越小越好」

**真相**：corePoolSize 过小 → 突发流量时频繁触发 worker 创建（new Thread 开销 ~0.1~1ms），反而拉低 QPS。

**正解**：根据历史 QPS 峰值设置 corePoolSize，宁可多 1~2 个常驻 worker。

### 16.2 ❌「无界队列不会拒绝」

**真相**：无界队列（`new LinkedBlockingQueue()`）永远不会触发拒绝策略，但任务持续堆积 → **OOM**。这是「没拒绝 = 安全」最常见的误解。

**正解**：永远指定队列容量。

### 16.3 ❌「CallerRunsPolicy 一定安全」

**真相**：CallerRunsPolicy 让提交线程同步执行任务。如果提交线程是 RPC 线程（如 Netty IO 线程），会**阻塞 RPC 响应** → 整个 RPC 链路雪崩。

**正解**：RPC 入口应使用自定义拒绝策略（埋点 + 持久化），而非 CallerRunsPolicy。

### 16.4 ❌「workQueue 用 LinkedBlockingQueue 即可」

**真相**：`new LinkedBlockingQueue()` 默认容量 `Integer.MAX_VALUE`，与无界等价。

**正解**：`new LinkedBlockingQueue(100)` 或 `new ArrayBlockingQueue(100)`。

### 16.5 ❌「线程池监控只看 poolSize」

**真相**：poolSize 满说明已经触发非核心线程创建（很可能已经积压）。真正能提前预警 OOM 的指标是 **队列使用率**。

**正解**：核心告警指标是 `queueSize / queueCapacity`，阈值 80%。

### 16.6 ❌「Virtual Threads 替代线程池」

**真相**：Virtual Threads 在 IO 密集型场景下吞吐量提升 10x+；但 CPU 密集型任务（计算、序列化）仍应使用 `ForkJoinPool.commonPool()`。

**正解**：IO 密集用 `Executors.newVirtualThreadPerTaskExecutor()`；CPU 密集继续用线程池。

### 16.7 ❌「shutdownNow() 立即停止」

**真相**：`shutdownNow()` 只「向所有 worker 发送中断信号」，不保证任务立即停止。`awaitTermination()` 才是「等真正终止」。

**正解**：`shutdownNow() + awaitTermination(超时)` 组合使用。

### 16.8 ❌「线程池中的异常会自动处理」

**真相**：`execute(Runnable)` 抛出的未捕获异常会传播到线程的 `UncaughtExceptionHandler`；`submit(Runnable)` 抛出的异常会被包装到 `Future`，**不主动调用 `future.get()` 就永远看不到**。

**正解**：要么用 `execute()` + 自定义 `Thread.UncaughtExceptionHandler`，要么用 `submit()` + `future.get()` 检查异常。

---

## 十七、高级代码示例

### 17.1 自定义 RejectedExecutionHandler（埋点 + 告警 + 持久化）

```java
public class MetricAndAlertRejectHandler implements RejectedExecutionHandler {

    private final Counter rejectedCounter;
    private final AlertService alertService;
    private final PersistenceQueue persistenceQueue;

    public MetricAndAlertRejectHandler(MeterRegistry registry) {
        this.rejectedCounter = Counter.builder("executor_rejected_total")
            .description("Total rejected tasks")
            .register(registry);
        this.alertService = new AlertService();
        this.persistenceQueue = new DiskPersistenceQueue("/var/log/pool-rejected");
    }

    @Override
    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        // 1. 上报监控
        rejectedCounter.increment();

        // 2. 记录详细日志（含线程池状态 + 任务信息）
        LoggerFactory.getLogger(getClass()).error(
            "[Rejected] poolName={}, poolSize={}, active={}, queueSize={}, task={}",
            e.getThreadFactory().toString(),
            e.getPoolSize(), e.getActiveCount(), e.getQueue().size(), r);

        // 3. 告警
        alertService.notify("[CRITICAL] 线程池已满，请立即排查");

        // 4. 降级：持久化到磁盘队列，后续扫描重试
        try {
            persistenceQueue.offer(r);
        } catch (Exception ex) {
            // 持久化也失败 → 最后一道防线：抛异常
            throw new RejectedExecutionException("All fallback paths failed", ex);
        }
    }
}
```

### 17.2 反射动态修改 ThreadPoolExecutor 参数

```java
public class ThreadPoolConfigRefresher {

    private static final Field CORE_POOL_SIZE;
    private static final Field MAXIMUM_POOL_SIZE;

    static {
        try {
            CORE_POOL_SIZE = ThreadPoolExecutor.class.getDeclaredField("corePoolSize");
            MAXIMUM_POOL_SIZE = ThreadPoolExecutor.class.getDeclaredField("maximumPoolSize");
            CORE_POOL_SIZE.setAccessible(true);
            MAXIMUM_POOL_SIZE.setAccessible(true);
        } catch (NoSuchFieldException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    public static void resize(ThreadPoolExecutor executor, int newCore, int newMax) {
        // 注意：corePoolSize 不能大于 maximumPoolSize
        if (newCore > newMax) throw new IllegalArgumentException("core > max");

        try {
            // 先设置 max → 再设置 core（JDK 内部 check 顺序要求）
            MAXIMUM_POOL_SIZE.setInt(executor, newMax);
            CORE_POOL_SIZE.setInt(executor, newCore);

            // 收缩时：如果当前 worker 数 > 新的 core，触发多余的 worker 回收
            if (executor.getPoolSize() > newCore) {
                executor.setCorePoolSize(newCore);  // 触发 interruptIdleWorkers
            }
        } catch (IllegalAccessException e) {
            throw new RuntimeException("Failed to resize thread pool", e);
        }
    }
}
```

> ⚠️ **风险提示**：反射修改 JDK 私有字段属于「黑科技」，生产环境务必通过配置中心灰度发布，并保留 JDK 升级时的兼容性测试（字段名可能在不同 JDK 版本变动）。

### 17.3 Spring Boot @Async 自定义线程池

```java
@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean("taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(200);
        executor.setKeepAliveSeconds(60);
        executor.setThreadNamePrefix("async-task-");
        // TaskDecorator：用于传递 ThreadLocal（traceId、userId）
        executor.setTaskDecorator(runnable -> {
            Map<String, String> context = MDC.getCopyOfContextMap();
            return () -> {
                try {
                    if (context != null) MDC.setContextMap(context);
                    runnable.run();
                } finally {
                    MDC.clear();
                }
            };
        });
        // 自定义拒绝策略
        executor.setRejectedExecutionHandler(new MetricAndAlertRejectHandler(meterRegistry));
        executor.initialize();
        return executor;
    }
}
```

---

## 十八、跨模块反向链

线程池在 Java 后端生态中的位置：

```text
Java 并发（JVM 维度）
  └─ 线程池（本文）
        ├─→ 锁机制（ReentrantLock）
        ├─→ 内存模型（JMM）
        └─→ Future / CompletableFuture

Spring 后端（框架维度）
  └─ Spring Boot @Async / TaskExecutor
        └─→ 底层即 ThreadPoolExecutor

分布式 RPC
  └─ Dubbo 自定义 ThreadPool（fixed/cached/limited/eager）

高性能网络
  └─ Netty EventLoop / UnorderedThreadPoolExecutor

Web 容器
  └─ Tomcat TaskQueue（定制 ThreadPoolExecutor）
```

### 18.1 向上链（依赖/被依赖）

- [线程池高频面试题（12.interview）](../../../12.interview/01.java/thread-pool-高频面试题/README.md) — 面试必备精简版（高频问答）
- [JMM 内存模型（01.java-and-jvm）](../jmm-memory-model/README.md) — 线程池内存可见性保证（happens-before）
- [ReentrantLock 锁机制（01.java-and-jvm）](../lock-reentrantlock/README.md) — Worker 的 AQS 实现基础
- [Spring Boot @Async TaskExecutor（04.spring-backend）](../../../04.spring-backend/spring-boot/async-task-executor/README.md) — Spring 异步任务底层即 ThreadPoolExecutor
- [Dubbo 线程池模型（06.distributed-systems）](../../../06.distributed-systems/rpc/dubbo-threadpool/README.md) — Dubbo 4 种内置线程池（fixed/cached/limited/eager）
- [Netty EventLoop 与线程模型（06.distributed-systems）](../../../06.distributed-systems/network/netty-eventloop/README.md) — Netty 业务线程池 UnorderedThreadPoolExecutor
- [Tomcat 线程池调优（06.distributed-systems）](../../../06.distributed-systems/web-servers/tomcat-threadpool/README.md) — Tomcat TaskQueue 定制

### 18.2 向下链（本文被引用）

- `12.interview/01.java/thread-pool-高频面试题/` — 面试题简版反向链回本文
- `04.spring-backend/spring-boot/async-task-executor/` — Spring @Async 章节引用本文做底层原理说明

---

⭐⭐⭐⭐（高频面试 + 实战必会）

## 反向链

- [异步 vs 多线程](../../../12.interview/01.java/async-vs-multithread/README.md) — 概念辨析：异步 ≠ 多线程（线程池 + Future.get() 是多线程但同步）

