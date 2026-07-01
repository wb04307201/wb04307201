# Java 并发编程专题导航

> 从底层原语到现代并发模型，全面掌握 Java 并发编程体系。

---
## 引言：学习路径

Java 并发编程专题导航 是一个学习专题，由 N 个子主题构成。

本篇是入口导航——先扫一眼目录定目标，再按路径顺序读，每个子主题都给出'为什么学 / 学到什么 / 怎么用'。

---

## 一、专题概述

Java 并发编程是 Java 平台的核心能力之一，涵盖了从线程创建、同步控制、内存模型到高级并发抽象的全套机制。理解并发编程是编写高性能、高可靠服务端程序的前提。

### 1.1 为什么需要并发编程

```
┌─────────────────────────────────────────────────────────┐
│                    并发编程解决的问题                      │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  性能提升    │  │  资源利用率  │  │  用户体验   │     │
│  │             │  │             │  │             │     │
│  │ 多核 CPU    │→ │ 充分调度     │→ │ 快速响应    │     │
│  │ 并行计算    │  │ 避免空闲     │  │ 不阻塞 UI   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  架构简化    │  │  业务模型   │  │  系统吞吐   │     │
│  │             │  │             │  │             │     │
│  │ 事件驱动    │→ │ 自然映射     │→ │ 并发处理    │     │
│  │ 异步编排    │  │ 真实世界     │  │ 提升 QPS    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

并发编程的核心目标：在保证**正确性**（数据一致、无竞态）的前提下，最大化**吞吐量**和**响应速度**。

### 1.2 并发 vs 并行

| 概念 | 定义 | 关注点 | 示例 |
|------|------|--------|------|
| **并发** (Concurrency) | 多个任务在同一时间段内**交替**执行 | 任务调度与资源复用 | 单核 CPU 上运行多个线程 |
| **并行** (Parallelism) | 多个任务在同一时刻**真正同时**执行 | 充分利用多核 | 多核 CPU 上每个核各跑一个线程 |

```java
// 并发示例：单核 CPU 上两个线程交替执行
// Thread-A: |██░░░░░░░░|██░░░░░░░░|██░░░░░░░░|
// Thread-B: ░░|██░░░░░░|██░░░░░░|██░░░░░░|
//            交替切换，同一时刻只有一个在运行

// 并行示例：双核 CPU 上两个线程同时执行
// Core-1:   |████████████████████████████|
// Core-2:   |████████████████████████████|
//            真正同时运行
```

---

## 二、Java 并发演进历程

Java 并发能力经历了从底层原语到高级抽象的完整演进：

| 阶段 | Java 版本 | 核心特性 | 编程模型 |
|------|-----------|---------|---------|
| 第一阶段 | Java 1-4 | `Thread`、`synchronized`、`volatile`、`wait/notify` | 手动管理线程，底层同步原语 |
| 第二阶段 | Java 5-7 | `java.util.concurrent`、线程池、`Fork/Join`、并发集合 | 库级抽象，结构化并发工具 |
| 第三阶段 | Java 8-16 | `CompletableFuture`、`StampedLock`、`VarHandle` | 异步编排，无锁编程 |
| 第四阶段 | Java 19-26 | 虚拟线程、结构化并发、作用域值 | 现代轻量并发模型 |

```java
// === 第一阶段：手动管理线程（Java 1）===
new Thread(() -> {
    synchronized (lock) {
        doWork();
    }
}).start();

// === 第二阶段：线程池（Java 5）===
ExecutorService pool = Executors.newFixedThreadPool(4);
pool.submit(() -> doWork());

// === 第三阶段：异步编排（Java 8）===
CompletableFuture.supplyAsync(() -> fetchData())
    .thenApply(data -> transform(data))
    .thenAccept(System.out::println);

// === 第四阶段：虚拟线程（Java 21）===
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> blockingIoCall()); // 同步写法，异步性能
}
```

---

## 三、专题导航

以下是 Java 并发编程的核心子专题，按知识依赖关系排列：

| 序号 | 专题 | 说明 | 链接 |
|:----:|------|------|------|
| 一 | Java 内存模型 (JMM) | happens-before 原则、内存屏障、指令重排序、可见性与有序性 | [jmm](./jmm/) |
| 二 | volatile 关键字 | volatile 语义、可见性保证、禁止重排序、适用场景与局限 | [volatile](./volatile/) |
| 三 | synchronized 关键字 | 内置锁原理、Monitor 对象、锁升级过程（偏向锁→轻量级锁→重量级锁） | [synchronized](./synchronized/) |
| 四 | ThreadLocal 线程局部变量 | 线程封闭技术、内存泄漏问题、InheritableThreadLocal、TransmittableThreadLocal | [threadlocal](./threadlocal/) |
| 五 | 原子类与 CAS 操作 | `AtomicInteger`、`LongAdder`、`AtomicReference`、Unsafe、CAS 原理与 ABA 问题 | [atomic](./atomic/) |
| 六 | CompletableFuture 异步编程 | 异步编排、组合、异常处理、虚拟线程集成、与线程池对比 | [completablefuture](./completablefuture/) |

---

## 四、专题详解

### 一、Java 内存模型 (JMM)

Java 内存模型（Java Memory Model）是并发编程的**理论基础**，定义了线程如何与主内存和工作内存交互。

**核心概念：**
- **主内存**：所有线程共享的变量存储区域
- **工作内存**：每个线程私有的变量副本区域
- **happens-before 原则**：判断数据是否存在竞争的核心规则

```
┌─────────────────────────────────────────────┐
│              Java 内存模型                    │
│                                             │
│              ┌─────────┐                    │
│              │ 主 内 存 │ ← 所有共享变量      │
│              │ (RAM)   │                    │
│              └────┬────┘                    │
│                   │ 读/写                    │
│          ┌────────┼────────┐                │
│          ▼        ▼        ▼                │
│     ┌────────┐┌────────┐┌────────┐         │
│     │线程 A   ││线程 B   ││线程 C   │         │
│     │工作内存││工作内存││工作内存│         │
│     │ 副本x  ││ 副本x  ││ 副本x  │         │
│     └────────┘└────────┘└────────┘         │
│                                             │
│  问题：线程 A 修改 x，线程 B 何时能看到？     │
│  答案：由 JMM 的 happens-before 规则保证      │
└─────────────────────────────────────────────┘
```

**happens-before 八大规则：**

| 规则 | 说明 |
|------|------|
| 程序顺序规则 | 单线程内，前面的操作 happens-before 后面的操作 |
| 锁规则 | 解锁 happens-before 后续加锁 |
| volatile 规则 | volatile 写 happens-before 后续 volatile 读 |
| 传递规则 | A happens-before B，B happens-before C，则 A happens-before C |
| 线程启动规则 | `Thread.start()` happens-before 该线程的任何操作 |
| 线程终止规则 | 线程的所有操作 happens-before `Thread.join()` 返回 |
| 线程中断规则 | `Thread.interrupt()` happens-before 被中断线程检测到中断 |
| 对象终结规则 | 对象构造完成 happens-before `finalize()` 方法调用 |

```java
// happens-before 示例
class Example {
    int a = 0;
    volatile boolean flag = false;

    // 线程 A 执行
    void writer() {
        a = 42;             // (1)
        flag = true;        // (2) -- volatile 写
    }

    // 线程 B 执行
    void reader() {
        if (flag) {         // (3) -- volatile 读
            System.out.println(a); // (4) 一定输出 42
        }
    }
}
// 推导：(1) -> (2) [程序顺序]
//       (2) -> (3) [volatile 规则]
//       (3) -> (4) [程序顺序]
// 传递性：(1) -> (4)，所以 (4) 一定能看到 a = 42
```

> 详细内容见：[jmm 专题](./jmm/)

---

### 二、volatile 关键字

`volatile` 是 Java 提供的最轻量级的同步机制，保证变量的**可见性**和**禁止指令重排序**。

**核心特性：**

| 特性 | 说明 | 对比 synchronized |
|------|------|-------------------|
| 可见性 | 一个线程修改 volatile 变量，其他线程立即可见 | synchronized 也保证可见性 |
| 禁止重排序 | 编译器和 CPU 不会对 volatile 操作重排序 | synchronized 也禁止重排序 |
| 原子性 | **不保证**复合操作的原子性（如 `count++`） | synchronized 保证原子性 |

```java
// volatile 正确用法：状态标志
class Worker {
    private volatile boolean running = true;

    public void stop() {
        running = false;  // 写 volatile，其他线程立即可见
    }

    public void run() {
        while (running) {  // 读 volatile，一定能看到最新值
            doWork();
        }
    }
}

// volatile 错误用法：复合操作不保证原子性
class BadCounter {
    private volatile int count = 0;

    public void increment() {
        count++; // 问题：读-改-写三步，volatile 只保证单步可见性
                 // 两个线程同时调用，可能丢失计数
    }
}
```

> 详细内容见：[volatile 专题](./volatile/)

---

### 三、synchronized 关键字

`synchronized` 是 Java 最基础的同步机制，基于 JVM 内部的 Monitor 对象实现。

**锁升级过程（重点）：**

```
无锁 → 偏向锁 → 轻量级锁（自旋） → 重量级锁（阻塞）

┌──────────────────────────────────────────────────────────┐
│                    synchronized 锁升级                    │
│                                                          │
│  阶段 1: 无锁                                             │
│  ┌─────────────────────────────┐                         │
│  │ Mark Word: 无锁状态标识      │                         │
│  └─────────────────────────────┘                         │
│                                                          │
│  阶段 2: 偏向锁（仅一个线程访问时）                         │
│  ┌─────────────────────────────┐                         │
│  │ Mark Word: 偏向线程ID +  Epoch│  ← 无锁竞争，无开销      │
│  └─────────────────────────────┘                         │
│                                                          │
│  阶段 3: 轻量级锁（少量竞争，自旋等待）                      │
│  ┌─────────────────────────────┐                         │
│  │ Mark Word: 指向 Lock Record  │  ← CAS 竞争，自旋        │
│  └─────────────────────────────┘                         │
│                                                          │
│  阶段 4: 重量级锁（竞争激烈，阻塞等待）                      │
│  ┌─────────────────────────────┐                         │
│  │ Mark Word: 指向 Monitor      │  ← OS 互斥锁，阻塞       │
│  └─────────────────────────────┘                         │
└──────────────────────────────────────────────────────────┘
```

```java
// 基本用法
class Counter {
    private int count = 0;

    // 同步实例方法 → 锁 this
    public synchronized void increment() {
        count++;
    }

    // 同步静态方法 → 锁 Counter.class
    public static synchronized void staticIncrement() {
        // ...
    }

    // 同步代码块 → 锁指定对象
    public void add() {
        synchronized (this) {
            count++;
        }
    }
}
```

> 详细内容见：[synchronized 专题](./synchronized/)

---

### 四、ThreadLocal 线程局部变量

`ThreadLocal` 提供线程局部变量，实现**线程封闭**，每个线程拥有独立的变量副本，无需加锁即可保证线程安全。

**数据结构：**

```
ThreadLocal 原理图

  Thread-1                    Thread-2
  ┌──────────────┐           ┌──────────────┐
  │ threadLocals │           │ threadLocals │
  │ (Entry[])    │           │ (Entry[])    │
  ├──────────────┤           ├──────────────┤
  │ TL-A → Val1  │           │ TL-A → Val2  │  ← 同一个 ThreadLocal，不同值
  │ TL-B → Val3  │           │ TL-B → Val4  │
  └──────────────┘           └──────────────┘
       ▲                          ▲
       └──────────┬───────────────┘
                  │
          ┌───────────────┐
          │ ThreadLocal<A>│  ← 弱引用 key
          │ ThreadLocal<B>│
          └───────────────┘
```

**内存泄漏问题：**

```java
// ThreadLocal 的 key 是弱引用，value 是强引用
// 如果 ThreadLocal 对象被 GC 回收，Entry 的 key 变为 null
// 但 value 仍然强引用，导致内存泄漏
// 解决方案：使用完毕后务必调用 remove()

public class ThreadLocalDemo {
    private static final ThreadLocal<UserContext> USER_CONTEXT =
        ThreadLocal.withInitial(UserContext::new);

    public void process() {
        try {
            UserContext ctx = USER_CONTEXT.get();
            ctx.setUserId(123);
            doBusiness();
        } finally {
            USER_CONTEXT.remove(); // 必须清理，防止内存泄漏！
        }
    }
}
```

> 详细内容见：[threadlocal 专题](./threadlocal/)

---

### 五、原子类与 CAS 操作

原子类基于 **CAS**（Compare-And-Swap）无锁算法实现线程安全的单变量操作，性能优于加锁方案。

**CAS 原理：**

```
┌───────────────────────────────────────────────────────┐
│                    CAS 操作原理                        │
│                                                       │
│  CAS(预期值, 新值)  →  成功/失败                       │
│                                                       │
│  伪代码：                                              │
│  boolean CAS(int* addr, int expected, int newValue) { │
│      if (*addr == expected) {                          │
│          *addr = newValue;                             │
│          return true;                                  │
│      }                                                 │
│      return false;                                     │
│  }                                                     │
│                                                       │
│  CPU 指令支持：x86 的 CMPXCHG / ARM 的 LDREX/STREX     │
└───────────────────────────────────────────────────────┘
```

**原子类家族：**

| 类别 | 类名 | 说明 |
|------|------|------|
| 基本类型 | `AtomicInteger`、`AtomicLong`、`AtomicBoolean` | 单变量原子操作 |
| 数组类型 | `AtomicIntegerArray`、`AtomicLongArray`、`AtomicReferenceArray` | 数组元素的原子操作 |
| 引用类型 | `AtomicReference`、`AtomicStampedReference`（解决 ABA） | 对象引用的原子操作 |
| 字段更新器 | `AtomicIntegerFieldUpdater`、`AtomicLongFieldUpdater` | 指定类的 volatile 字段 |
| 累加器 | `LongAdder`、`DoubleAdder`（高并发更优） | 分段累加，减少 CAS 竞争 |

```java
// AtomicInteger 用法
AtomicInteger counter = new AtomicInteger(0);

counter.incrementAndGet();   // 原子自增，返回新值
counter.getAndIncrement();   // 原子自增，返回旧值
counter.compareAndSet(5, 10);// CAS: 期望值为 5，更新为 10

// LongAdder（高并发场景推荐）
LongAdder longAdder = new LongAdder();
longAdder.increment();       // 分段累加
long sum = longAdder.sum();  // 获取总和
```

> 详细内容见：[atomic 专题](./atomic/)

---

### 六、CompletableFuture 异步编程

`CompletableFuture`（Java 8 引入）提供了强大的异步编排能力，支持链式调用、组合、异常处理，是回调地狱的终结者。

**核心能力：**

```java
// 1. 创建异步任务
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    return fetchDataFromRemote();
});

// 2. 链式变换
future
    .thenApply(data -> parse(data))          // 转换结果
    .thenAccept(result -> System.out.println(result)) // 消费结果
    .exceptionally(ex -> {                   // 异常处理
        log.error("Failed", ex);
        return "fallback";
    });

// 3. 组合多个异步任务
CompletableFuture<String> f1 = CompletableFuture.supplyAsync(() -> callA());
CompletableFuture<String> f2 = CompletableFuture.supplyAsync(() -> callB());

// 等待两个都完成
CompletableFuture.allOf(f1, f2).join();
String result = f1.join() + f2.join();

// 任一完成即可
CompletableFuture.anyOf(f1, f2).join();

// 4. 超时控制
String result = future.orTimeout(5, TimeUnit.SECONDS).join();

// 5. 虚拟线程集成（Java 21+）
// 默认使用 ForkJoinPool.commonPool()
// 可指定使用虚拟线程的执行器
CompletableFuture.supplyAsync(() -> blockingIoCall(),
    Executors.newVirtualThreadPerTaskExecutor());
```

**CompletableFuture vs 虚拟线程对比：**

| 维度 | CompletableFuture | 虚拟线程（Java 21+） |
|------|-------------------|---------------------|
| 编程风格 | 异步回调链 | 同步写法 |
| 可读性 | 中等（链式调用） | 高（线性逻辑） |
| 异常处理 | `.exceptionally()` | 标准 try-catch |
| 适用场景 | 非阻塞 I/O、流式处理 | 阻塞 I/O、高并发 |
| 学习曲线 | 较陡 | 低 |

> 详细内容见：[completablefuture 专题](./completablefuture/)

---

## 五、并发编程知识体系全景

```
┌────────────────────────────────────────────────────────────────┐
│                    Java 并发编程知识体系                         │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  理论基础                                                  │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │ │
│  │  │  JMM 模型   │  │ volatile   │  │ happens-before 原则 │  │ │
│  │  │  主/工作内存│  │  可见性/有序│  │  八大规则           │  │ │
│  │  └────────────┘  └────────────┘  └────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                    │
│  ┌───────────────────────┼────────────────────────────────┐  │
│  │  同步机制                                                  │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────┐  │  │
│  │  │ synchronized   │  │ 显式锁(JUC)     │  │ 原子类    │  │  │
│  │  │ 锁升级/Monitor │  │ ReentrantLock  │  │ CAS/ABA  │  │  │
│  │  │ 偏向→轻量→重量 │  │ StampedLock    │  │ LongAdder│  │  │
│  │  └────────────────┘  └────────────────┘  └──────────┘  │  │
│  └───────────────────────┼────────────────────────────────┘  │
│                          │                                    │
│  ┌───────────────────────┼────────────────────────────────┐  │
│  │  线程管理                                                  │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────┐  │  │
│  │  │ ThreadLocal    │  │ 线程池          │  │ 虚拟线程  │  │  │
│  │  │ 线程封闭       │  │ ThreadPoolExec │  │ Java 21+ │  │  │
│  │  │ 内存泄漏防护   │  │ ForkJoinPool   │  │ 轻量调度  │  │  │
│  │  └────────────────┘  └────────────────┘  └──────────┘  │  │
│  └───────────────────────┼────────────────────────────────┘  │
│                          │                                    │
│  ┌───────────────────────┼────────────────────────────────┐  │
│  │  异步编排                                                  │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────┐  │  │
│  │  │ Future/Callable│  │ CompletableFuture│ │ 结构化并  │  │  │
│  │  │ Java 5-7       │  │ Java 8+        │  │ 发(预览) │  │  │
│  │  │ 阻塞等待       │  │ 链式组合       │  │ Java 25+ │  │  │
│  │  └────────────────┘  └────────────────┘  └──────────┘  │  │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## 六、常见并发问题速查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **竞态条件** | 多线程对共享变量的执行顺序不确定 | 加锁、原子操作、不可变对象 |
| **死锁** | 循环等待对方持有的锁 | 锁排序、`tryLock` 超时、死锁检测 |
| **饥饿** | 某些线程长期得不到 CPU 或锁 | 公平锁、调整优先级 |
| **活锁** | 线程不断重试但始终无法推进 | 引入随机退避 |
| **内存可见性** | 一个线程的修改对其他线程不可见 | `volatile`、`synchronized`、`final` |
| **指令重排序** | 编译器/CPU 优化导致执行顺序变化 | `volatile`、内存屏障 |
| **ThreadLocal 泄漏** | Entry 的 value 强引用未被清理 | `finally` 块中 `remove()` |
| **CAS ABA 问题** | 值被修改后恢复为原值，CAS 无法感知 | `AtomicStampedReference` |

---

## 七、最佳实践原则

1. **优先使用并发库**：`java.util.concurrent` 提供的工具类，而非手动管理线程
2. **最小化共享状态**：不可变对象 > 线程封闭（ThreadLocal） > 同步访问
3. **锁的范围尽量小**：缩小临界区，减少锁持有时间
4. **避免在锁内执行耗时操作**：如 I/O、网络调用
5. **I/O 密集型使用虚拟线程**（Java 21+），CPU 密集型使用固定线程池
6. **始终为线程池设置合理参数**：根据任务类型选择核心线程数
7. **正确处理中断**：响应 `InterruptedException`，不吞掉中断信号
8. **ThreadLocal 用完必清**：`finally` 块中调用 `remove()` 防止泄漏

---

## 八、专题目录结构

```
concurrency/
├── README.md              ← 本文件，专题导航
├── jmm/                   ← Java 内存模型
│   └── README.md
├── volatile/              ← volatile 关键字
│   └── README.md
├── synchronized/          ← synchronized 关键字与锁机制
│   └── README.md
├── threadlocal/           ← ThreadLocal 线程局部变量
│   └── README.md
├── atomic/                ← 原子类与 CAS 操作
│   └── README.md
└── completablefuture/     ← CompletableFuture 异步编程
    └── README.md
```

---

> **总结**：Java 并发编程从 `synchronized` + `Thread` 演进到虚拟线程 + 结构化并发的现代模型。
> 本专题覆盖了并发编程的基础知识体系——从 JMM 理论到 volatile/synchronized 同步原语，
> 从 ThreadLocal 线程封闭到 CAS 无锁编程，再到 CompletableFuture 异步编排。
> 掌握这些内容是进一步学习线程池、虚拟线程、结构化并发等高级主题的基础。
