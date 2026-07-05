<!--
module:
  parent: java
  slug: java/thread-basics
  type: article
  category: 主模块子文章
  summary: Java 线程基础
-->

# Java 线程基础

---

## 一、创建线程的 4 种方式

Java 中创建线程主要有以下 4 种方式：

### 1.1 继承 Thread 类

通过继承 `java.lang.Thread` 类并重写 `run()` 方法来创建线程。

```java
public class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println(Thread.currentThread().getName() + " 正在执行");
    }

    public static void main(String[] args) {
        MyThread thread = new MyThread();
        thread.setName("MyThread-1");
        thread.start(); // 调用 start() 而非 run()
    }
}
```

**特点：**
- 简单直观，适合简单场景
- 由于 Java 单继承限制，继承了 Thread 就不能再继承其他类
- `start()` 方法会启动新线程并调用 `run()`，直接调用 `run()` 只是在当前线程执行普通方法

### 1.2 实现 Runnable 接口

实现 `java.lang.Runnable` 接口，将任务与线程本身解耦。

```java
public class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println(Thread.currentThread().getName() + " 正在执行");
    }

    public static void main(String[] args) {
        Thread thread = new Thread(new MyRunnable(), "Runnable-Thread");
        thread.start();
    }
}
```

**Lambda 简化写法：**

```java
Thread thread = new Thread(() -> {
    System.out.println(Thread.currentThread().getName() + " Lambda 方式创建");
}, "Lambda-Thread");
thread.start();
```

**特点：**
- 避免了单继承限制，可以实现其他接口或继承其他类
- 任务（Runnable）与执行者（Thread）分离，更符合面向对象设计
- 无法返回执行结果，也无法抛出受检异常

### 1.3 实现 Callable 接口

实现 `java.util.concurrent.Callable<V>` 接口，支持返回值和异常抛出。

```java
import java.util.concurrent.Callable;
import java.util.concurrent.FutureTask;

public class MyCallable implements Callable<Integer> {
    @Override
    public Integer call() throws Exception {
        int sum = 0;
        for (int i = 1; i <= 100; i++) {
            sum += i;
        }
        return sum;
    }

    public static void main(String[] args) throws Exception {
        Callable<Integer> callable = new MyCallable();
        FutureTask<Integer> futureTask = new FutureTask<>(callable);
        Thread thread = new Thread(futureTask, "Callable-Thread");
        thread.start();

        // get() 会阻塞直到任务完成
        Integer result = futureTask.get();
        System.out.println("计算结果: " + result); // 5050
    }
}
```

**特点：**
- 有返回值，泛型指定返回类型
- 可以抛出受检异常
- 需要配合 `FutureTask` 使用，`FutureTask` 同时实现了 `Runnable` 和 `Future`

### 1.4 线程池

通过 `java.util.concurrent.ExecutorService` 统一管理线程，避免频繁创建和销毁线程。

```java
import java.util.concurrent.*;

public class ThreadPoolDemo {
    public static void main(String[] args) throws Exception {
        // 固定大小线程池
        ExecutorService executor = Executors.newFixedThreadPool(3);

        // 提交 Runnable 任务
        executor.submit(() -> System.out.println("任务 1 执行"));

        // 提交 Callable 任务，获取返回值
        Future<Integer> future = executor.submit(() -> {
            Thread.sleep(1000);
            return 42;
        });

        System.out.println("返回值: " + future.get());

        // 优雅关闭线程池
        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);
    }
}
```

**线程池类型对比：**

| 线程池类型 | 创建方法 | 特点 | 适用场景 |
|---|---|---|---|
| 固定大小线程池 | `newFixedThreadPool(n)` | 核心/最大线程数固定 | 负载较重的服务器 |
| 缓存线程池 | `newCachedThreadPool()` | 线程数无上限，空闲 60s 回收 | 大量短期异步任务 |
| 单线程池 | `newSingleThreadExecutor()` | 只有一个工作线程 | 保证顺序执行 |
| 定时线程池 | `newScheduledThreadPool(n)` | 支持定时/周期执行 | 定时任务 |

> **注意：** 《阿里巴巴 Java 开发手册》建议不要使用 `Executors` 创建线程池，应使用 `ThreadPoolExecutor` 手动创建，以便明确资源约束，避免 OOM。

```java
// 推荐的线程池创建方式
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    5,                  // 核心线程数
    10,                 // 最大线程数
    60,                 // 空闲线程存活时间
    TimeUnit.SECONDS,   // 时间单位
    new LinkedBlockingQueue<>(100), // 工作队列
    new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
);
```

## 二、Thread 生命周期

Java 线程共有 **6 种状态**，定义在 `Thread.State` 枚举中：

```
                  ┌──────────┐
                  │   NEW    │  新建状态，调用了 new 但尚未调用 start()
                  └────┬─────┘
                       │ start()
                       ▼
                  ┌──────────┐
         ┌───────▶│ RUNNABLE │  可运行状态（包含就绪和运行中）
         │        └────┬─────┘
         │             │ 获取锁/被唤醒/超时到期
         │             ▼
         │        ┌──────────┐
         │        │  BLOCKED  │  阻塞状态，等待监视器锁
         │        └────┬─────┘
         │             │ 获取到锁
         │             ▼
         │        ┌──────────┐◀───────┐
         │        │ WAITING  │        │ notify() / notifyAll()
         │        └────┬─────┘        │ interrupt()
         │             │              │
         │      ┌──────┼──────┐       │
         │      ▼      ▼      ▼       │
         │   wait()  join()  LockSupport.park()
         │
         │        ┌──────────────┐◀────┐
         │        │TIMED_WAITING │     │ 超时 / interrupt()
         │        └──────┬───────┘     │
         │               │             │
         │      ┌────────┼────────┐    │
         │      ▼        ▼        ▼    │
         │   sleep()  wait(timeout) join(timeout)
         │   LockSupport.parkNanos()   │
         │                             │
         ▼                             │
    ┌──────────┐                       │
    │TERMINATED│  终止状态，run() 执行完毕
    └──────────┘                       │
                                       │
         以上状态间可互相转换 ◀─────────┘
```

### 各状态说明

| 状态 | 说明 | 触发条件 |
|---|---|---|
| `NEW` | 新建 | 调用了 `new Thread()` 但还未调用 `start()` |
| `RUNNABLE` | 可运行 | 调用了 `start()`，可能在运行或等待 CPU 时间片 |
| `BLOCKED` | 阻塞 | 等待获取监视器锁进入 `synchronized` 块/方法 |
| `WAITING` | 无限期等待 | 调用 `Object.wait()`、`Thread.join()`、`LockSupport.park()` |
| `TIMED_WAITING` | 超时等待 | 调用带超时参数的 `sleep()`、`wait()`、`join()` 等 |
| `TERMINATED` | 终止 | `run()` 方法执行完毕或抛出未捕获异常 |

### 查看线程状态

```java
public class ThreadStateDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread thread = new Thread(() -> {
            try {
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });

        System.out.println("创建后: " + thread.getState()); // NEW
        thread.start();
        System.out.println("启动后: " + thread.getState()); // RUNNABLE 或 TIMED_WAITING
        Thread.sleep(100);
        System.out.println("休眠中: " + thread.getState()); // TIMED_WAITING
        thread.join();
        System.out.println("结束后: " + thread.getState()); // TERMINATED
    }
}
```

## 三、Thread 常用方法

| 方法 | 类型 | 说明 |
|---|---|---|
| `start()` | 实例方法 | 启动线程，使其进入 RUNNABLE 状态；每个线程只能调用一次 |
| `run()` | 实例方法 | 线程的执行体，直接调用只是在当前线程执行普通方法 |
| `sleep(long ms)` | **静态方法** | 让当前线程休眠指定毫秒，不释放锁，会抛出 `InterruptedException` |
| `yield()` | **静态方法** | 让当前线程让出 CPU 时间片，回到就绪状态，不保证一定会切换 |
| `join()` | 实例方法 | 等待目标线程终止，调用方线程被阻塞 |
| `join(long ms)` | 实例方法 | 等待目标线程终止，最多等待指定毫秒 |
| `interrupt()` | 实例方法 | 中断目标线程，设置中断标志位 |
| `isAlive()` | 实例方法 | 判断线程是否存活（已启动且未终止） |
| `currentThread()` | **静态方法** | 返回当前正在执行的线程引用 |
| `getId()` | 实例方法 | 返回线程唯一标识 ID |
| `getName()` / `setName()` | 实例方法 | 获取/设置线程名称 |

### sleep vs yield 对比

```java
// sleep: 阻塞指定时间，不释放锁
synchronized (lock) {
    try {
        Thread.sleep(1000); // 持有 lock 锁休眠
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
}

// yield: 提示调度器让出 CPU，不释放锁，立即重新竞争
synchronized (lock) {
    Thread.yield(); // 仍然持有 lock，可能再次获得 CPU
}
```

### join 示例

```java
public class JoinDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            for (int i = 1; i <= 5; i++) {
                System.out.println("t1: " + i);
                try { Thread.sleep(200); } catch (InterruptedException e) {}
            }
        });

        t1.start();
        // 主线程等待 t1 执行完毕再继续
        t1.join();
        System.out.println("主线程继续执行");
    }
}
```

### interrupt 机制

`interrupt()` **不会真正停止线程**，而是设置中断标志位。线程需要自行检查并响应中断：

```java
public class InterruptDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread worker = new Thread(() -> {
            // 方式一：检查中断标志
            while (!Thread.currentThread().isInterrupted()) {
                System.out.println("工作中...");
                try {
                    Thread.sleep(500); // sleep 期间被中断会抛异常并清除标志
                } catch (InterruptedException e) {
                    // 恢复中断标志（重要！）
                    Thread.currentThread().interrupt();
                    System.out.println("收到中断信号，准备退出");
                    break;
                }
            }
            System.out.println("线程退出");
        });

        worker.start();
        Thread.sleep(1500);
        worker.interrupt(); // 发送中断信号
        worker.join();
    }
}
```

> **关键点：** `sleep()`、`wait()`、`join()` 等阻塞方法在收到中断时会抛出 `InterruptedException` 并**清除中断标志**。捕获异常后应调用 `Thread.currentThread().interrupt()` 恢复标志，以便上层感知中断。

## 四、守护线程（Daemon Thread）

守护线程是为其他用户线程提供服务的后台线程，如垃圾回收线程、JIT 编译线程等。

### 设置方式

```java
public class DaemonDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread daemon = new Thread(() -> {
            while (true) {
                System.out.println("守护线程运行中...");
                try { Thread.sleep(500); } catch (InterruptedException e) {}
            }
        });

        // 必须在 start() 之前设置
        daemon.setDaemon(true);
        daemon.start();

        Thread.sleep(2000);
        System.out.println("主线程结束");
        // 主线程结束后，JVM 退出，守护线程也随之终止
    }
}
```

### 守护线程 vs 用户线程

| 对比项 | 用户线程（User Thread） | 守护线程（Daemon Thread） |
|---|---|---|
| 默认值 | `isDaemon() == false` | `isDaemon() == true` |
| JVM 退出条件 | 所有用户线程结束后 JVM 才退出 | 不影响 JVM 退出 |
| 典型场景 | 业务逻辑线程 | GC、JIT、心跳检测等 |
| `finally` 块 | 正常执行 | 可能不执行，JVM 可能直接退出 |

> **注意：**
> - `setDaemon(true)` 必须在 `start()` 之前调用，否则抛出 `IllegalThreadStateException`
> - 守护线程创建的子线程默认也是守护线程
> 不要将守护线程用于关键业务（如文件写入），因为 `finally` 块可能来不及执行

## 五、线程优先级

线程优先级范围是 **1 ~ 10**，默认值为 **5**（`Thread.NORM_PRIORITY`）。

```java
public static final int MIN_PRIORITY     = 1;   // 最低优先级
public static final int NORM_PRIORITY    = 5;   // 默认优先级
public static final int MAX_PRIORITY     = 10;  // 最高优先级
```

### 设置与获取

```java
Thread t1 = new Thread(() -> System.out.println("低优先级线程"));
t1.setPriority(Thread.MIN_PRIORITY);

Thread t2 = new Thread(() -> System.out.println("高优先级线程"));
t2.setPriority(Thread.MAX_PRIORITY);

System.out.println("t1 优先级: " + t1.getPriority()); // 1
System.out.println("t2 优先级: " + t2.getPriority()); // 10
```

### 优先级规则

```
优先级范围:
  1 (MIN) ◀──────────────────────────────▶ 10 (MAX)
  │         │                  │          │
 低       默认(5)              │         高
                              │
              优先级越高，获得 CPU 时间片的概率越大
              但不保证先执行，具体取决于操作系统调度器
```

| 特性 | 说明 |
|---|---|
| 继承性 | 子线程默认继承父线程的优先级 |
| 平台依赖 | 优先级映射依赖操作系统，不同平台效果可能不同 |
| 不可靠 | 高优先级不一定先执行，不能作为业务逻辑依赖 |
| 范围限制 | 设置超出 1~10 范围会抛出 `IllegalArgumentException` |

> **注意：** 线程优先级高度依赖操作系统调度策略，在不同 OS 上表现可能不一致。不应将程序正确性建立在优先级之上。

## 六、线程安全三要素

### 6.1 原子性（Atomicity）

一个操作或多个操作要么全部执行且不被中断，要么全部不执行。

```java
// ❌ 非原子操作：i++ 实际上是三步操作（读-改-写）
int i = 0;
i++; // 多线程同时执行可能丢失更新

// ✅ 使用 AtomicInteger 保证原子性
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet(); // 原子 +1

// ✅ 使用 synchronized 保证原子性
synchronized (lock) {
    i++;
}
```

### 6.2 可见性（Visibility）

一个线程对共享变量的修改，能够及时被其他线程看到。

```java
// ❌ 可能不可见：线程 A 修改 flag，线程 B 可能永远看不到
boolean flag = false;
// 线程 A: flag = true;
// 线程 B: while (!flag) { ... }  可能死循环

// ✅ 使用 volatile 保证可见性
volatile boolean flag = false;

// ✅ 使用 synchronized 也保证可见性（进入同步块时刷新工作内存）
synchronized (lock) {
    flag = true;
}
```

**Java 内存模型（JMM）中的可见性问题：**

```
┌──────────────────────────────────────────────┐
│                   主内存                      │
│              sharedVar = 0                    │
│         ↗️  copy            copy  ↖️           │
┌┴───────────┐                      ┌───────────┴┐
│  线程 A     │                      │  线程 B     │
│ 工作内存    │                      │ 工作内存    │
│ sharedVar=1 │                      │ sharedVar=0 │
│  (修改后)   │                      │  (旧值)    │
└────────────┘                      └────────────┘

问题：线程 A 修改了工作内存中的值，但没有立即刷新到主内存
     线程 B 从主内存读取的仍是旧值

解决：volatile 关键字强制每次读取主内存，写入时立即刷新
```

### 6.3 有序性（Ordering）

程序执行的顺序按照代码先后顺序执行。编译器和处理器可能会对指令进行**重排序**优化。

```java
// 可能发生重排序的场景
int x = 0;       // 语句 1
int y = 1;       // 语句 2
boolean flag = true; // 语句 3

// 编译器/CPU 可能重排为：1→3→2 或 3→1→2 等
// 只要单线程执行结果不变，重排序就是允许的

// ✅ volatile 禁止重排序（内存屏障）
volatile boolean flag = true;

// ✅ synchronized 也保证有序性
```

### happens-before 原则

JMM 定义了 happens-before 规则来保证有序性和可见性：

| 规则 | 说明 |
|---|---|
| 程序顺序规则 | 一个线程内，按代码顺序，前面的操作 happens-before 后面的操作 |
| 锁规则 | 对一个锁的解锁 happens-before 后续对这个锁的加锁 |
| volatile 规则 | 对 volatile 变量的写 happens-before 后续对这个变量的读 |
| 传递规则 | A happens-before B，B happens-before C，则 A happens-before C |
| 线程启动规则 | `Thread.start()` happens-before 该线程的任意操作 |
| 线程终止规则 | 线程的所有操作 happens-before `Thread.join()` 返回 |
| 中断规则 | 对 `interrupt()` 的调用 happens-before 被中断线程检测到中断 |

### 三要素总结

```
                ┌─────────────────────┐
                │    线程安全三要素     │
                ├─────────────────────┤
                │                     │
                │  🔒 原子性           │
                │  操作不可分割        │
                │  方案: CAS/synchronized│
                │                     │
                │  👁️ 可见性           │
                │  修改及时可见        │
                │  方案: volatile/    │
                │        synchronized │
                │                     │
                │  📋 有序性           │
                │  执行顺序可预期       │
                │  方案: volatile/    │
                │        synchronized │
                │                     │
                └─────────────────────┘
```

| 要素 | 问题描述 | 解决方案 | 典型场景 |
|---|---|---|---|
| 原子性 | 多个操作被中断导致不一致 | `synchronized`、`Lock`、`AtomicXxx` | `i++` 计数 |
| 可见性 | 线程间看不到彼此的修改 | `volatile`、`synchronized`、`final` | 状态标志位 |
| 有序性 | 指令重排导致逻辑错乱 | `volatile`、`synchronized`、`happens-before` | 双重检查锁定 |

## 七、Runnable vs Callable vs Thread 对比

| 对比维度 | Thread | Runnable | Callable<V> |
|---|---|---|---|
| 类型 | 类（继承） | 接口（实现） | 泛型接口（实现） |
| 返回值 | 无（void） | 无（void） | 有返回值（泛型 V） |
| 异常抛出 | 不能抛出受检异常 | 不能抛出受检异常 | **可以**抛出受检异常 |
| 方法名 | `run()` | `run()` | `call()` |
| 使用方式 | `new MyThread().start()` | `new Thread(runnable).start()` | 配合 `FutureTask` 使用 |
| 能否被线程池直接使用 | 可以 | 可以 | 需包装为 `FutureTask` |
| 单继承限制 | **有**（继承了 Thread 就不能继承其他类） | 无 | 无 |

### 代码对照

```java
// 1. Thread - 继承方式
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Thread 方式");
    }
}
new MyThread().start();

// 2. Runnable - 接口实现方式
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("Runnable 方式");
    }
}
new Thread(new MyRunnable()).start();

// 3. Callable - 带返回值的方式
class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        return "Callable 返回结果";
    }
}
FutureTask<String> task = new FutureTask<>(new MyCallable());
new Thread(task).start();
String result = task.get(); // 获取返回值
```

### 选择建议

```
是否需要返回值？
    ├─ 是 → 使用 Callable + FutureTask / 线程池.submit()
    └─ 否
        │
        ├─ 是否只需要定义任务逻辑？
        │   ├─ 是 → 使用 Runnable（推荐，灵活、可复用）
        │   └─ 否 → 使用 Thread（简单但不推荐，受单继承限制）
        │
        └─ 是否需要在线程内获取线程本身引用？
            ├─ 是 → Runnable 中用 Thread.currentThread()
            └─ 否 → 任何方式均可

推荐优先级：Callable ≈ Runnable > Thread
```

---

## 七、3 线程按顺序执行（实战篇姐妹）

本文 § 三.3 讲了 `Thread.join()` 的**原理**（阻塞调用方线程）；实战中"T1 → T2 → T3 按顺序执行"有 **3 种语义 + 8 种方案**对比，独立章节：

- [sequential-execution.md](sequential-execution.md) — 串行 / 分支 / 汇合 3 语义 + Top 3 推荐方案（join / CountDownLatch / CompletableFuture）+ 8 方案对比表 + 实战模板

**面试配套**：[13.split-hairs/01.java/thread-sequential-execution](../../../13.split-hairs/01.java/thread-sequential-execution/README.md) — 5 题面试题版（语义陷阱 / join 原理 / CountDownLatch 选型 / CompletableFuture 链式 / 生产推荐）

---

← [返回 Java 并发编程专题导航](../README.md)
