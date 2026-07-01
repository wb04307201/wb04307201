# Java 线程池（ThreadPoolExecutor）学习笔记

---
## 引言：变更说明

Java 线程池（ThreadPoolExecutor）学习笔记 是 N 个 JEP / 特性 / 章节的合集。

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

```
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

```
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

```
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

```
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

```
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

```
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

```
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
