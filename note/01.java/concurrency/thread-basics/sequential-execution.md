<!--
module:
  parent: java
  slug: java/concurrency/thread-basics/sequential-execution
  type: article
  category: 主模块子文章
  summary: T1/T2/T3 按顺序执行的 3 种语义 + Top 3 推荐方案 + 8 方案优劣对比 + 实战模板。
-->

# 三个线程 T1、T2、T3 怎么确保按顺序执行？8 方案对比

> 一句话定位：经典 Java 面试 Top 10 题。本文给出**3 种语义**（串行 / 分支 / 汇合）+ **Top 3 推荐方案**（join / CountDownLatch / CompletableFuture）+ **8 种方案优劣对比** + **实战模板**。

> **同模块兄弟**：
> - [Thread 基础（thread-basics/README）](README.md) — 讲原理（`join()` / `wait()` / 守护线程）
> - [JUC 工具类](../utilities/README.md) — CountDownLatch / CyclicBarrier / Semaphore 详解

---

## 一、问题本质：3 种语义（最容易答错的第一步）

很多人一上来就答"用 join"，但**没问清"什么算顺序"**就答 = 答错。

```text
面试官问："3 线程按顺序执行"——具体是哪种"顺序"？

├─ 语义 1：串行（T1 完成 → T2 开始 → T3 开始）
│   └─ 最常见的理解 ——"3 线程串行执行"
│
├─ 语义 2：分支（T1 完成 → T2 和 T3 并行开始）
│   └─ 实际场景：T1 初始化 → T2 读数据 + T3 写数据并行
│
└─ 语义 3：汇合（T1 和 T2 并行 → 都完成后 T3 开始）
    └─ 实际场景：T1 读 Redis + T2 读 DB → 都完成后 T3 处理
```

**反直觉点**：**先问清楚是哪种"顺序"，再选方案** —— 不同语义对应不同实现。

---

## 二、Top 3 推荐方案（实战排序）

### 2.1 方案 1：`Thread.join()` —— 最简单（O(1) 代码）

**原理**：调用 `t1.join()` 后，**当前线程阻塞**，直到 t1 终止。

```java
public class JoinDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            System.out.println("T1 开始");
            sleep(1000);
            System.out.println("T1 完成");
        }, "T1");

        Thread t2 = new Thread(() -> {
            System.out.println("T2 开始");
            sleep(500);
            System.out.println("T2 完成");
        }, "T2");

        Thread t3 = new Thread(() -> {
            System.out.println("T3 开始");
            System.out.println("T3 完成");
        }, "T3");

        long start = System.currentTimeMillis();

        t1.start();
        t1.join();  // 主线程等 T1

        t2.start();
        t2.join();  // 主线程等 T2

        t3.start();
        t3.join();  // 主线程等 T3

        // 输出顺序：T1 开始 → T1 完成 → T2 开始 → T2 完成 → T3 开始 → T3 完成
        // 总耗时：~1500ms（1000 + 500）
    }
}
```

**优点**：
- ✅ 代码最简单（一行 `join()`）
- ✅ 不需要额外对象

**缺点**：
- ❌ 阻塞**调用方线程**（main 线程被串行占用）
- ❌ 不适合"分支 / 汇合"语义

**适用**：简单串行、demo 代码。

---

### 2.2 方案 2：`CountDownLatch` —— 最通用（可扩展）

**原理**：计数器 = N，**每个被等待线程完成后调用 `countDown()`**，等待方调用 `await()` 阻塞直到计数器 = 0。

```java
public class CountDownLatchDemo {
    public static void main(String[] args) throws InterruptedException {
        // 串行版本（语义 1）：用 3 个 latch 串联
        CountDownLatch latch1 = new CountDownLatch(1);  // 等 T1
        CountDownLatch latch2 = new CountDownLatch(1);  // 等 T2
        CountDownLatch latch3 = new CountDownLatch(1);  // 等 T3

        new Thread(() -> {
            try {
                System.out.println("T1 开始");
                Thread.sleep(1000);
                System.out.println("T1 完成");
                latch1.countDown();  // T1 完成信号
                latch2.await();      // T1 等 T2 完成
                System.out.println("T1 在 T2 之后继续");
                latch3.await();      // T1 等 T3 完成
                System.out.println("T1 在 T3 之后继续");
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "T1").start();

        new Thread(() -> {
            try {
                latch1.await();      // T2 等 T1
                System.out.println("T2 开始");
                Thread.sleep(500);
                System.out.println("T2 完成");
                latch2.countDown();
                latch3.await();      // T2 等 T3
                System.out.println("T2 在 T3 之后继续");
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "T2").start();

        new Thread(() -> {
            try {
                latch2.await();      // T3 等 T2
                System.out.println("T3 开始");
                System.out.println("T3 完成");
                latch3.countDown();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "T3").start();
    }
}
```

**汇合版本（语义 3）**：

```java
// T1 和 T2 并行，都完成后 T3 开始
CountDownLatch latch = new CountDownLatch(2);  // 等 2 个线程

new Thread(() -> {
    doWork("T1");
    latch.countDown();
}).start();

new Thread(() -> {
    doWork("T2");
    latch.countDown();
}).start();

new Thread(() -> {
    latch.await();  // T3 等 T1 + T2 都完成
    doWork("T3");
}).start();
```

**优点**：
- ✅ **可扩展**：N 个线程汇合、N 个串行阶段都能用
- ✅ **非阻塞**：调用 `countDown()` 不阻塞

**缺点**：
- ❌ **不可重置**（一次性）—— 多次串行需要多个 latch
- ❌ 代码比 join 复杂

**适用**：**生产环境首选**，可读性 + 扩展性最好。

---

### 2.3 方案 3：`CompletableFuture.thenRun()` —— 现代写法

**原理**：链式调用，**上一步完成后自动触发下一步**。

```java
public class CompletableFutureDemo {
    public static void main(String[] args) {
        CompletableFuture<Void> t1 = CompletableFuture.runAsync(() -> {
            System.out.println("T1 开始");
            sleep(1000);
            System.out.println("T1 完成");
        });

        CompletableFuture<Void> t2 = t1.thenRunAsync(() -> {
            System.out.println("T2 开始");
            sleep(500);
            System.out.println("T2 完成");
        });

        CompletableFuture<Void> t3 = t2.thenRunAsync(() -> {
            System.out.println("T3 开始");
            System.out.println("T3 完成");
        });

        t3.join();  // 主线程等所有完成
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
```

**分支版本（语义 2）**：

```java
// T1 → (T2, T3 并行) → 都完成后主流程继续
CompletableFuture<Void> t1 = CompletableFuture.runAsync(() -> {
    System.out.println("T1 开始");
    sleep(1000);
    System.out.println("T1 完成");
});

CompletableFuture<Void> t2 = t1.thenRunAsync(() -> {
    System.out.println("T2 开始");
    sleep(500);
    System.out.println("T2 完成");
});

CompletableFuture<Void> t3 = t1.thenRunAsync(() -> {
    System.out.println("T3 开始");
    sleep(800);
    System.out.println("T3 完成");
});

CompletableFuture.allOf(t2, t3).join();  // 主流程等 T2 + T3 都完成
```

**优点**：
- ✅ **链式调用最优雅**（thenRun 一目了然）
- ✅ **3 种语义都能自然表达**

**缺点**：
- ❌ 需要 Java 8+
- ❌ 调试相对困难（链式调用）

**适用**：**新项目首选**，代码最优雅。

---

## 三、其他 5 种方案对比（备选）

### 3.1 `Semaphore`（信号量）

**原理**：用 `acquire()` / `release()` 控制许可。

```java
Semaphore s1 = new Semaphore(0);  // 初始 0 个许可
Semaphore s2 = new Semaphore(0);

t1.start();
t1.join(); s1.release();  // T1 完成后释放 s1

new Thread(() -> { s1.acquire(); /* T2 工作 */; s2.release(); }).start();
// ... T3 用 s2.acquire()
```

**适用**：和 CountDownLatch 类似，但**可重置**（release 后 acquire 又可阻塞）。

### 3.2 `CyclicBarrier`（循环屏障）

**原理**：N 个线程都到达屏障后才继续。

```java
CyclicBarrier barrier = new CyclicBarrier(3);  // 3 个线程都到才继续
for (int i = 0; i < 3; i++) {
    new Thread(() -> {
        doWork();
        barrier.await();  // 等所有线程到屏障
        doNext();
    }).start();
}
```

**适用**：**汇合语义**（多线程并行 → 共同继续），但**不适合串行**。

### 3.3 `wait()` / `notify()`（synchronized + 共享标志）

**原理**：每个线程用 `synchronized` + `wait()` 阻塞，用 `notify()` 唤醒。

```java
class SequentialRunner {
    private int order = 1;
    public synchronized void run1() throws InterruptedException {
        while (order != 1) wait();
        System.out.println("T1");
        order = 2;
        notifyAll();
    }
    // run2() / run3() 类似
}
```

**适用**：**不推荐**（代码复杂、易出错，CountDownLatch 是更好的替代）。

### 3.4 `Lock` + `Condition`（ReentrantLock）

**原理**：类似 wait/notify，但用 Lock + Condition。

```java
ReentrantLock lock = new ReentrantLock();
Condition c1 = lock.newCondition();
// ... 用 c1.await() / c1.signal()
```

**适用**：需要**多个等待队列**的复杂场景；普通顺序执行**杀鸡用牛刀**。

### 3.5 单线程池（`newSingleThreadExecutor`）

**原理**：所有任务提交到**单线程池**，**自动串行执行**。

```java
ExecutorService exec = Executors.newSingleThreadExecutor();
exec.submit(() -> { /* T1 */ });
exec.submit(() -> { /* T2 */ });
exec.submit(() -> { /* T3 */ });
exec.shutdown();
```

**适用**：**纯串行任务队列**（不关心线程名 / 不需要 join 中间结果）。

---

## 四、8 方案对比表

| 方案 | 代码量 | 性能 | 可扩展性 | 易理解性 | 串行 | 分支 | 汇合 | 推荐度 |
|------|------:|-----:|---------:|---------:|:----:|:----:|:----:|------:|
| `Thread.join()` | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ✅ | ❌ | ❌ | ⭐⭐⭐ |
| `CountDownLatch` | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ❌ | ✅ | ⭐⭐⭐⭐⭐ |
| `CompletableFuture` | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| `Semaphore` | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ | ✅ | ✅ | ⭐⭐⭐ |
| `CyclicBarrier` | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ❌ | ❌ | ✅ | ⭐⭐ |
| `wait()/notify()` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ✅ | ⚠️ | ⚠️ | ⭐ |
| `Lock + Condition` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ✅ | ⚠️ | ⚠️ | ⭐ |
| `SingleThreadExecutor` | ⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ✅ | ❌ | ❌ | ⭐⭐⭐⭐ |

**选型决策树**：

```text
你的场景是？
├─ 简单串行（demo / 一次性）
│   ├─ 不需要扩展 → Thread.join()（最简单）
│   └─ 要扩展到 N 线程 → CountDownLatch
├─ 复杂编排（分支 / 汇合 / 异步链）
│   └─ CompletableFuture（现代写法，首选）
├─ 纯串行任务队列
│   └─ SingleThreadExecutor（任务流式提交）
└─ 多线程并行 → 共同继续
    └─ CyclicBarrier 或 CompletableFuture.allOf
```

---

## 五、实战模板：3 种典型场景

### 5.1 串行：T1 → T2 → T3

```java
// 推荐：CompletableFuture
CompletableFuture.runAsync(() -> doT1())
    .thenRunAsync(() -> doT2())
    .thenRunAsync(() -> doT3())
    .join();
```

### 5.2 分支：T1 → (T2, T3 并行)

```java
CompletableFuture<Void> t1 = CompletableFuture.runAsync(() -> doT1());
CompletableFuture<Void> t2 = t1.thenRunAsync(() -> doT2());
CompletableFuture<Void> t3 = t1.thenRunAsync(() -> doT3());
CompletableFuture.allOf(t2, t3).join();
```

### 5.3 汇合：(T1, T2 并行) → T3

```java
CompletableFuture<Void> t1 = CompletableFuture.runAsync(() -> doT1());
CompletableFuture<Void> t2 = CompletableFuture.runAsync(() -> doT2());
CompletableFuture.allOf(t1, t2)
    .thenRunAsync(() -> doT3())
    .join();
```

---

## 六、反模式（不要做的事）

| 反模式 | 后果 |
|--------|------|
| ❌ 用 volatile 共享标志位 | 忙等 / 内存可见性问题 |
| ❌ 自旋等待（while loop sleep） | CPU 空转，性能差 |
| ❌ `Thread.sleep(1000)` 模拟等待 | 不可靠，生产必崩 |
| ❌ 共享一个 lock + 标志位串行 | 锁粒度太大，性能差 |
| ❌ 用 wait/notify 写复杂状态机 | 容易死锁，**CountDownLatch 是更好选择** |

---

## 七、可复用 Checklist（选型自查）

- [ ] 先确认是"串行 / 分支 / 汇合"哪种语义
- [ ] 简单串行 → `Thread.join()`
- [ ] 复杂编排 → `CompletableFuture`
- [ ] 汇合 N 线程 → `CountDownLatch` 或 `CompletableFuture.allOf`
- [ ] 多线程并行 → 共同继续 → `CyclicBarrier`
- [ ] **不推荐**用 wait/notify 写串行（CountDownLatch 更安全）
- [ ] 异常处理：必须 `try-catch InterruptedException` + 恢复中断标志

---

## 八、相关章节

**同模块基础**：
- [Thread 基础（thread-basics/README）](README.md) — `Thread.join()` / `wait()` / 中断机制
- [JUC 工具类](../utilities/README.md) — CountDownLatch / CyclicBarrier / Semaphore 详解
- [JUC 锁](../juc-locks/README.md) — ReentrantLock / Condition
- [CompletableFuture](../completablefuture/README.md) — 异步编排全貌

**面试题（13.split-hairs）**：
- [三个线程按顺序执行面试 5 题](../../../13.split-hairs/01.java/thread-sequential-execution/README.md) — 本文实战模板的面试题版

**相关主题**：
- [线程池](../../../13.split-hairs/01.java/thread-pool/README.md) — 多线程管理
- [ThreadLocal](../../../13.split-hairs/01.java/threadlocal/README.md) — 线程局部变量

---

← [返回 Thread 基础](README.md)