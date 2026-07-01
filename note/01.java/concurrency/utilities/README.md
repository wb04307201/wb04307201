<!--
module:
  parent: java
  slug: java/concurrency-utilities
  type: article
  category: 主模块子文章
  summary: Java 并发工具类
-->

# Java 并发工具类 (java.util.concurrent)

> `java.util.concurrent` 包提供了一组高级并发构建块，用于简化多线程程序的开发。
> 本文档系统介绍 `CountDownLatch`、`CyclicBarrier`、`Semaphore`、`Phaser`、`Exchanger` 五大同步工具。

---
## 引言：反直觉代码

Java 并发工具类 (java.util.concurrent) 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 目录

- [一、CountDownLatch（倒计时门闩）](#一countdownlatch倒计时门闩)
- [二、CyclicBarrier（循环屏障）](#二cyclicbarrier循环屏障)
- [三、Semaphore（信号量）](#三semaphore信号量)
- [四、Phaser（阶段器）](#四phaser阶段器)
- [五、Exchanger（交换器）](#五exchanger交换器)
- [六、各工具对比与使用场景](#六各工具对比与使用场景)

---

## 一、CountDownLatch（倒计时门闩）

### 1.1 核心概念

`CountDownLatch` 是一个同步辅助类，允许一个或多个线程等待其他线程完成一组操作。

- 初始化时指定一个计数值（count）
- 每次调用 `countDown()` 方法使计数减一
- `await()` 方法阻塞直到计数归零
- **计数不可重置**，归零后无法复用（一次性工具）

### 1.2 核心 API

| 方法 | 说明 |
|------|------|
| `CountDownLatch(int count)` | 构造器，指定初始计数 |
| `void await()` | 阻塞等待计数归零 |
| `boolean await(long timeout, TimeUnit unit)` | 超时等待，超时返回 false |
| `void countDown()` | 计数减一 |
| `long getCount()` | 获取当前计数值 |

### 1.3 工作原理

```
主线程                         工作线程1    工作线程2    工作线程3
  |                               |            |            |
  |-- new CountDownLatch(3)       |            |            |
  |                               |            |            |
  |-- await() ────────┐           |            |            |
  |                   |           | countDown()|            |
  |        阻塞等待    |           |            |            |
  |                   |           |            | countDown()|
  |                   |           |            |            |
  |                   |           |            |            | countDown()
  |                   |◀──────────┴────────────┴────────────┘
  |   count=0, 唤醒继续               (最后一次countDown)
  |
  |-- 继续执行后续逻辑
```

### 1.4 代码示例

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class CountDownLatchDemo {

    /**
     * 场景: 主线程等待多个工作线程完成任务后再继续执行
     * 典型应用: 服务启动时等待所有子模块初始化完成
     */
    public static void main(String[] args) throws InterruptedException {
        int workerCount = 3;
        CountDownLatch latch = new CountDownLatch(workerCount);

        ExecutorService executor = Executors.newFixedThreadPool(workerCount);

        for (int i = 1; i <= workerCount; i++) {
            final int workerId = i;
            executor.submit(() -> {
                try {
                    System.out.println("Worker-" + workerId + " 开始工作...");
                    Thread.sleep((long) (Math.random() * 2000));
                    System.out.println("Worker-" + workerId + " 完成工作");
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    latch.countDown(); // 无论成功或失败都要释放
                }
            });
        }

        // 主线程等待所有工作线程完成，最多等待 5 秒
        boolean finished = latch.await(5, TimeUnit.SECONDS);
        if (finished) {
            System.out.println("所有工作线程已完成，主线程继续执行");
        } else {
            System.out.println("超时！仍有 " + latch.getCount() + " 个线程未完成");
        }

        executor.shutdown();
    }
}
```

### 1.5 典型使用场景

- **服务启动**: 主线程等待所有子系统（数据库连接池、缓存服务、消息队列等）初始化完成
- **并行计算**: 将大任务拆分为多个子任务并行执行，等待所有子任务结果汇总
- **性能测试**: 多个线程同时到达起跑线后开始压力测试（配合第二个 latch）
- **批量加载**: 等待多个数据源加载完毕后才能对外提供服务

### 1.6 最佳实践

1. **始终在 finally 块中调用 `countDown()`**，确保即使发生异常计数也能正确递减
2. **设置合理的超时时间**，避免因某个线程永远不 `countDown()` 导致主线程永久阻塞
3. **使用 `getCount()` 检查剩余未完成任务数**，便于调试和监控
4. **不可复用的特性意味着每次使用都需要创建新实例**，若需循环使用应考虑 `CyclicBarrier`
5. 注意 `countDown()` 调用次数超过初始 count 值不会产生异常，但多出的调用无效

---

## 二、CyclicBarrier（循环屏障）

### 2.1 核心概念

`CyclicBarrier` 是一个同步辅助类，允许一组线程互相等待，直到所有线程都到达某个公共屏障点（barrier point）后再一起继续执行。

- 与 `CountDownLatch` 的关键区别：**可循环使用**
- 屏障释放后自动重置，可被下一批线程复用
- 支持在所有线程到达屏障后执行一个"屏障动作"（Runnable）

### 2.2 核心 API

| 方法 | 说明 |
|------|------|
| `CyclicBarrier(int parties)` | 构造器，指定参与屏障的线程数 |
| `CyclicBarrier(int parties, Runnable barrierAction)` | 构造器，带屏障完成后执行的动作 |
| `int await()` | 等待其他线程到达屏障 |
| `int await(long timeout, TimeUnit unit)` | 超时等待 |
| `int getNumberWaiting()` | 获取当前已到达屏障的线程数 |
| `int getParties()` | 获取屏障所需的线程总数 |
| `void reset()` | 重置屏障，等待中的线程抛出 `BrokenBarrierException` |
| `boolean isBroken()` | 检查屏障是否已损坏 |

### 2.3 工作原理

```
线程 A ───▶ await() ──┐
                       │
线程 B ───▶ await() ──┼──▶ [屏障点] ──▶ 执行 barrierAction ──▶ 全部释放 ──▶ 屏障自动重置
                       │
线程 C ───▶ await() ──┘

重置后: 可以被下一批线程再次使用
```

### 2.4 代码示例

```java
import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class CyclicBarrierDemo {

    /**
     * 场景: 多线程分阶段计算，每个阶段完成后才能进入下一个阶段
     * 典型应用: 并行迭代算法、多轮 MapReduce
     */
    public static void main(String[] args) {
        int workerCount = 3;

        // 屏障动作: 所有线程到达后执行
        Runnable barrierAction = () ->
            System.out.println(">>> 所有线程已到达屏障，开始下一阶段计算");

        CyclicBarrier barrier = new CyclicBarrier(workerCount, barrierAction);

        ExecutorService executor = Executors.newFixedThreadPool(workerCount);

        for (int i = 1; i <= workerCount; i++) {
            final int workerId = i;
            executor.submit(() -> {
                try {
                    // 第一阶段
                    System.out.println("Worker-" + workerId + " 执行第一阶段");
                    Thread.sleep((long) (Math.random() * 1000));
                    System.out.println("Worker-" + workerId + " 第一阶段完成，等待其他线程");

                    // 等待所有线程完成第一阶段
                    barrier.await();
                    System.out.println("Worker-" + workerId + " 进入第二阶段");

                    // 第二阶段
                    Thread.sleep((long) (Math.random() * 1000));
                    System.out.println("Worker-" + workerId + " 第二阶段完成");

                    // 再次使用同一个屏障（循环特性）
                    barrier.await();
                    System.out.println("Worker-" + workerId + " 全部完成");

                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } catch (BrokenBarrierException e) {
                    System.err.println("屏障被破坏: " + e.getMessage());
                }
            });
        }

        executor.shutdown();
    }
}
```

### 2.5 CountDownLatch vs CyclicBarrier

| 对比维度 | CountDownLatch | CyclicBarrier |
|----------|----------------|---------------|
| 计数方式 | 递减（countDown） | 递增（到达线程计数） |
| 可复用性 | 不可复用，一次性 | 可循环使用 |
| 等待模式 | 一个（或多个）线程等待其他线程 | 所有线程互相等待 |
| 屏障动作 | 无 | 支持 barrierAction |
| 损坏恢复 | 无损坏概念 | 支持 `reset()` 和 `isBroken()` |
| 典型场景 | 主线程等待多个子任务完成 | 多线程多阶段协作计算 |

### 2.6 最佳实践

1. **注意 `BrokenBarrierException` 的处理**：当屏障被 `reset()` 或某个等待线程被中断时，所有等待线程都会收到此异常
2. **屏障动作中避免耗时操作或阻塞调用**，屏障动作执行期间所有线程都在等待
3. **使用 `isBroken()` 检查屏障状态**，在异常恢复逻辑中判断是否需要重建屏障
4. **确保参与屏障的线程数与 parties 一致**，否则永远无法达到屏障
5. **超时场景下需考虑对其他线程的影响**：一个线程超时退出可能导致屏障被破坏

---

## 三、Semaphore（信号量）

### 3.1 核心概念

`Semaphore` 维护了一组虚拟许可证（permits），线程通过获取许可证来控制对共享资源的并发访问数量。

- 构造时指定许可证数量
- `acquire()` 获取许可证，无可用许可时阻塞
- `release()` 释放许可证
- 支持**公平模式**和**非公平模式**
- 许可证数量可在运行时动态调整

### 3.2 核心 API

| 方法 | 说明 |
|------|------|
| `Semaphore(int permits)` | 构造器，非公平模式 |
| `Semaphore(int permits, boolean fair)` | 构造器，指定公平性 |
| `void acquire()` | 获取一个许可证，可中断 |
| `void acquire(int permits)` | 获取多个许可证 |
| `void acquireUninterruptibly()` | 获取许可证，不可中断 |
| `boolean tryAcquire()` | 尝试获取，不阻塞 |
| `boolean tryAcquire(long timeout, TimeUnit unit)` | 超时尝试获取 |
| `void release()` | 释放一个许可证 |
| `void release(int permits)` | 释放多个许可证 |
| `int availablePermits()` | 获取当前可用许可证数 |
| `void reducePermits(int reduction)` | 减少许可证数 |
| `int drainPermits()` | 获取并清空所有可用许可证 |

### 3.3 工作原理

```
                   Semaphore(permits=3)
                    ┌──────────────┐
                    │  可用许可: 3  │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
      线程A              线程B              线程C
   acquire()          acquire()          acquire()
    成功               成功               成功
   许可: 2            许可: 1            许可: 0

      线程D              线程E
   acquire()          acquire()
    阻塞               阻塞
   (等待许可)          (等待许可)

         ┌─────────────────┐
         ▼                 ▼
      线程A              线程B
     release()          release()
   许可: 1 → 2        许可: 2 → 3
         │                 │
         ▼                 ▼
      线程D              线程E
    被唤醒              被唤醒
   acquire() 成功      acquire() 成功
```

### 3.4 代码示例

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;

public class SemaphoreDemo {

    /**
     * 场景: 数据库连接池管理，限制同时访问数据库的线程数
     */
    public static void main(String[] args) {
        // 最多允许 3 个线程同时访问数据库
        int maxConcurrentConnections = 3;
        Semaphore semaphore = new Semaphore(maxConcurrentConnections, true); // 公平模式

        ExecutorService executor = Executors.newFixedThreadPool(10);

        for (int i = 1; i <= 10; i++) {
            final int taskId = i;
            executor.submit(() -> {
                try {
                    System.out.println("Task-" + taskId + " 请求数据库连接...");
                    semaphore.acquire();
                    System.out.println("Task-" + taskId + " 获得数据库连接 (剩余许可: "
                            + semaphore.availablePermits() + ")");

                    // 模拟数据库操作
                    Thread.sleep(2000);
                    System.out.println("Task-" + taskId + " 数据库操作完成");

                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    semaphore.release();
                    System.out.println("Task-" + taskId + " 释放数据库连接");
                }
            });
        }

        executor.shutdown();
    }

    /**
     * 流量控制示例: 限制每秒请求数
     */
    public static void rateLimitDemo() throws InterruptedException {
        Semaphore semaphore = new Semaphore(100); // 令牌桶: 最多100个令牌

        // 定时补充令牌的线程
        Thread tokenRefiller = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    int current = semaphore.availablePermits();
                    int toAdd = Math.min(10, 100 - current);
                    if (toAdd > 0) {
                        semaphore.release(toAdd);
                    }
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }, "TokenRefiller");
        tokenRefiller.setDaemon(true);
        tokenRefiller.start();
    }
}
```

### 3.5 公平模式 vs 非公平模式

| 模式 | 行为 | 吞吐量 | 适用场景 |
|------|------|--------|----------|
| 公平模式 (fair=true) | 按 FIFO 顺序分配许可证 | 较低 | 需要保证线程不被饿死的场景 |
| 非公平模式 (fair=false) | 允许插队，新来的线程可能先获得许可 | 较高 | 大多数场景的默认选择 |

### 3.6 最佳实践

1. **始终在 finally 块中调用 `release()`**，避免许可证泄漏导致其他线程永久阻塞
2. **合理选择公平模式**：默认非公平模式性能更好，但有线程饥饿风险
3. **`acquire()` 和 `release()` 的次数必须匹配**，否则会导致许可证数量异常
4. **使用 `tryAcquire(timeout, unit)` 替代 `acquire()` 来避免无限等待**
5. 信号量可以用作**二值信号量**（permits=1），此时行为类似互斥锁（ReentrantLock），但信号量不绑定特定线程，可在不同线程中 acquire 和 release
6. **注意动态调整许可证数量的线程安全性**：`reducePermits()` 和 `drainPermits()` 会影响正在等待的线程

---

## 四、Phaser（阶段器）

### 4.1 核心概念

`Phaser` 是 Java 7 引入的可复用同步屏障，结合了 `CountDownLatch` 和 `CyclicBarrier` 的功能，并提供了更灵活的阶段管理能力。

- 支持**动态注册和注销**参与者
- 支持**多阶段**（phase）推进
- 每个阶段可自定义到达行为（`onAdvance()`）
- 支持**层次化** Phaser 树，减少竞争

### 4.2 核心 API

| 方法 | 说明 |
|------|------|
| `Phaser()` | 构造器，初始 0 个参与者 |
| `Phaser(int parties)` | 构造器，指定初始参与者数 |
| `Phaser(Phaser parent)` | 构造器，指定父 Phaser（层次化） |
| `int register()` | 动态注册一个新参与者 |
| `int bulkRegister(int parties)` | 批量注册多个参与者 |
| `int arrive()` | 到达但不等待 |
| `int arriveAndAwaitAdvance()` | 到达并等待其他参与者（类似 barrier.await()） |
| `int arriveAndDeregister()` | 到达并注销自己 |
| `int getPhase()` | 获取当前阶段号 |
| `int getRegisteredParties()` | 获取已注册的参与者数 |
| `int getArrivedParties()` | 获取已到达当前阶段的参与者数 |
| `boolean isTerminated()` | 检查是否已终止 |
| `void forceTermination()` | 强制终止 Phaser |

### 4.3 工作原理

```
                Phase 0           Phase 1           Phase 2
              ┌────────┐        ┌────────┐        ┌────────┐
              │ Phaser │        │ Phaser │        │ Phaser │
              │  parties=3      │  parties=3      │  parties=2
              └───┬────┘        └───┬────┘        └───┬────┘
                  │                 │                 │
    线程A ──────▶ ├──▶ arrive ◀──▶ │──▶ arrive ◀──▶ │──▶ arriveAndDeregister
                  │                 │                 │   (线程A退出, parties=2)
    线程B ──────▶ ├──▶ arrive ◀──▶ │──▶ arrive ◀──▶ │──▶ arrive
                  │                 │                 │
    线程C ──────▶ ├──▶ arrive ◀──▶ │──▶ arrive ◀──▶ │──▶ arrive
                  │                 │                 │
    线程D ──▶ register (Phase 0 中途加入)
                  │
    所有线程到达 ─▶ [屏障释放] ──▶ 自动进入下一 Phase
```

### 4.4 代码示例

```java
import java.util.concurrent.Phaser;

public class PhaserDemo {

    /**
     * 场景: 多阶段流水线处理，每个阶段完成后才能进入下一阶段
     * 参与者数量可在运行过程中动态变化
     */
    public static void main(String[] args) {
        Phaser phaser = new Phaser(1); // 主线程也算一个参与者
        System.out.println("初始阶段: " + phaser.getPhase());

        // 动态注册 3 个工作线程
        for (int i = 1; i <= 3; i++) {
            final int workerId = i;
            phaser.register(); // 注册新参与者

            new Thread(() -> {
                try {
                    // 阶段 1: 数据准备
                    System.out.println("Worker-" + workerId + " 准备数据...");
                    Thread.sleep(500);
                    phaser.arriveAndAwaitAdvance();

                    // 阶段 2: 数据处理
                    System.out.println("Worker-" + workerId + " 处理数据 (Phase "
                            + phaser.getPhase() + ")...");
                    Thread.sleep(500);
                    phaser.arriveAndAwaitAdvance();

                    // 阶段 3: 结果汇总（Worker-3 完成后退出）
                    System.out.println("Worker-" + workerId + " 汇总结果 (Phase "
                            + phaser.getPhase() + ")...");
                    Thread.sleep(500);

                    if (workerId == 3) {
                        phaser.arriveAndDeregister(); // Worker-3 退出
                        System.out.println("Worker-3 已完成并退出");
                    } else {
                        phaser.arriveAndAwaitAdvance();
                    }

                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Worker-" + i).start();
        }

        // 主线程等待所有阶段完成
        // arriveAndAwaitAdvance 的次数 = 注册的新参与者数量 + 1 (主线程自己)
        int phases = 3;
        for (int i = 0; i < phases; i++) {
            phaser.arriveAndAwaitAdvance();
        }

        // 注销主线程
        phaser.arriveAndDeregister();
        System.out.println("所有阶段已完成，当前阶段: " + phaser.getPhase());
    }
}
```

### 4.5 Phaser vs CountDownLatch vs CyclicBarrier

| 对比维度 | CountDownLatch | CyclicBarrier | Phaser |
|----------|----------------|---------------|--------|
| 可复用 | 否 | 是 | 是 |
| 动态参与者 | 否 | 否 | **是** |
| 多阶段支持 | 否 | 手动重置 | **内置支持** |
| 层次化 | 否 | 否 | **是** |
| 到达不等待 | 不支持 | 不支持 | **支持** (`arrive()`) |
| 动态注销 | 不支持 | 不支持 | **支持** (`arriveAndDeregister()`) |
| 终止机制 | 无 | `reset()` | `forceTermination()` |
| Java 版本 | 5+ | 5+ | **7+** |
| 复杂度 | 低 | 中 | 高 |

### 4.6 最佳实践

1. **优先使用更简单的工具**：如果只需要一次性等待，用 `CountDownLatch`；如果需要循环屏障，用 `CyclicBarrier`；只有动态参与者或多阶段场景才用 `Phaser`
2. **利用层次化 Phaser 减少竞争**：当参与者数量很大时，使用父子 Phaser 树结构减少 CAS 竞争
3. **注意 `arrive()` 和 `arriveAndAwaitAdvance()` 的区别**：前者只计数不阻塞，后者计数并等待
4. **合理使用 `arriveAndDeregister()`**：线程完成自己的部分后应及时注销，避免阻塞后续阶段
5. **重写 `onAdvance()` 自定义阶段转换行为**，返回 `true` 表示终止 Phaser

---

## 五、Exchanger（交换器）

### 5.1 核心概念

`Exchanger` 用于两个线程在某个同步点交换数据。两个线程同时到达交换点后，互相传递各自的数据对象。

- **仅适用于两个线程**之间的数据交换
- 两个线程调用 `exchange()` 后，各自获得对方传入的对象
- 如果只有一个线程到达，则会阻塞等待配对线程
- Java 9 起新增了 `exchange(V item, long timeout, TimeUnit unit)` 超时方法

### 5.2 核心 API

| 方法 | 说明 |
|------|------|
| `Exchanger()` | 构造器 |
| `V exchange(V x)` | 交换数据，阻塞直到另一个线程到达 |
| `V exchange(V x, long timeout, TimeUnit unit)` | 带超时的交换（Java 9+） |

### 5.3 工作原理

```
线程 A (生产者)                  Exchanger                 线程 B (消费者)
      │                              │                          │
      │   bufferA = 填充数据          │                          │
      │   exchange(bufferA) ────────▶ │ ◀───── exchange(bufferB)  │
      │                              │                          │
      │     ◀── 获得 bufferB ─────── │ ──▶ 获得 bufferA ───────▶ │
      │   (空的缓冲区)                │                    (填充数据的缓冲区)
      │                              │                          │
      │   处理 bufferB (空的)         │               处理 bufferA (填充的)
      │   重新填充...                 │               消费数据...
```

### 5.4 代码示例

```java
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Exchanger;

public class ExchangerDemo {

    /**
     * 场景: 生产者-消费者模式中的缓冲区交换
     * 生产者填充缓冲区，消费者消费后返回空缓冲区，实现零拷贝式数据传递
     */
    public static void main(String[] args) {
        Exchanger<List<String>> exchanger = new Exchanger<>();

        // 生产者线程
        Thread producer = new Thread(() -> {
            List<String> buffer = new ArrayList<>();

            for (int i = 0; i < 5; i++) {
                // 填充缓冲区
                buffer.add("Data-" + i);
                buffer.add("Data-" + (i * 10));

                try {
                    System.out.println("[生产者] 发送: " + buffer);
                    // 交换: 发送填充的缓冲区，获取空缓冲区
                    buffer = exchanger.exchange(buffer);
                    System.out.println("[生产者] 收到空缓冲区，大小: " + buffer.size());
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }

            System.out.println("[生产者] 生产完成");
        }, "Producer");

        // 消费者线程
        Thread consumer = new Thread(() -> {
            List<String> buffer = new ArrayList<>();

            for (int i = 0; i < 5; i++) {
                try {
                    // 交换: 发送空缓冲区，获取填充的缓冲区
                    buffer = exchanger.exchange(buffer);
                    System.out.println("[消费者] 收到: " + buffer);

                    // 消费数据
                    buffer.forEach(data ->
                        System.out.println("  [消费者] 处理: " + data));
                    buffer.clear(); // 清空作为空缓冲区

                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }

            System.out.println("[消费者] 消费完成");
        }, "Consumer");

        producer.start();
        consumer.start();

        try {
            producer.join();
            consumer.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("交换完成");
    }
}
```

### 5.5 最佳实践

1. **Exchanger 专为两个线程设计**，不适合多于两个线程的场景
2. **注意超时处理**（Java 9+）：使用带超时的 `exchange()` 避免无限等待，超时后检查配对线程是否还存活
3. **典型应用是"乒乓缓冲区"模式**：两个线程交替使用两个缓冲区，一个填充一个消费
4. **交换的对象引用**：交换的是对象引用，不是深拷贝，确保两个线程不会同时修改同一个对象
5. **如果一个线程可能提前结束**，考虑使用中断机制通知另一个线程退出等待
6. **注意 Java 9 前后 API 差异**：Java 9 之前只有无参超时版本

---

## 六、各工具对比与使用场景

### 6.1 功能对比总览

| 特性 | CountDownLatch | CyclicBarrier | Semaphore | Phaser | Exchanger |
|------|:---:|:---:|:---:|:---:|:---:|
| **核心用途** | 等待计数归零 | 线程集合点 | 限制并发数 | 多阶段同步 | 两线程交换 |
| **可复用** | 否 | 是 | 是 | 是 | 是 |
| **参与者数量** | 不固定 | 固定 | 不固定 | 动态可变 | **严格为 2** |
| **阻塞方向** | 单向等待 | 互相等待 | 竞争许可 | 互相等待 | 配对等待 |
| **阶段管理** | 无 | 无 | 无 | **多阶段** | 无 |
| **超时支持** | 是 | 是 | 是 | 是 | Java 9+ 支持 |
| **引入版本** | Java 5 | Java 5 | Java 5 | Java 7 | Java 5 |

### 6.2 场景决策图

```
你的并发需求是什么?
│
├── "我需要一个/多个线程等待其他线程完成"
│   └── 等待完成后需要再次等待吗?
│       ├── 不需要 → CountDownLatch
│       └── 需要   → CyclicBarrier 或 Phaser
│
├── "我需要限制同时访问某资源的线程数量"
│   └── Semaphore
│
├── "我需要多线程分阶段协作，每个阶段完成后再进入下一阶段"
│   └── 参与线程数会变化吗?
│       ├── 不变 → CyclicBarrier
│       └── 变化 → Phaser
│
└── "我需要两个线程互相交换数据"
    └── Exchanger
```

### 6.3 使用场景速查表

| 场景 | 推荐工具 | 原因 |
|------|----------|------|
| 服务启动，等待所有组件初始化 | CountDownLatch | 一次性等待，语义最清晰 |
| 并行任务拆分后等待汇总结果 | CountDownLatch | 主线程等待多个子线程完成 |
| 多线程压力测试同时启动 | CountDownLatch × 2 | 第一个控制起跑线，第二个统计结果 |
| 多轮迭代算法（如并行排序） | CyclicBarrier | 每轮完成后自动进入下一轮 |
| MapReduce 风格的多阶段计算 | CyclicBarrier / Phaser | 屏障动作适合做阶段间协调 |
| 数据库连接池限流 | Semaphore | 精确控制并发连接数 |
| API 接口限流（令牌桶） | Semaphore | 许可证即令牌，tryAcquire 即消费 |
| 线程安全的资源池 | Semaphore | 许可证数量=池大小 |
| 动态增减参与者的多阶段计算 | Phaser | 唯一支持动态注册/注销的工具 |
| 父子任务分层同步 | Phaser | 层次化 Phaser 树减少竞争 |
| 生产者-消费者零拷贝缓冲交换 | Exchanger | 两个线程完美配对交换缓冲区 |
| 基因序列比对（双线程交替处理） | Exchanger | 两个线程交替传递数据块 |

### 6.4 组合使用模式

实际项目中，这些工具经常组合使用：

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Semaphore;

/**
 * 组合模式示例: 限流 + 起跑线同步 + 多阶段计算
 *
 * 场景: 模拟 10 个用户同时进行 3 轮操作，每轮操作受数据库连接数限制
 */
public class CombinedPatternDemo {

    public static void main(String[] args) throws Exception {
        int userCount = 10;
        int dbConnections = 3;   // 最多 3 个并发数据库操作
        int rounds = 3;          // 3 轮操作

        Semaphore dbSemaphore = new Semaphore(dbConnections); // 限流
        CountDownLatch startLatch = new CountDownLatch(1);     // 起跑线
        CountDownLatch doneLatch = new CountDownLatch(userCount); // 完成计数
        CyclicBarrier roundBarrier = new CyclicBarrier(userCount,
                () -> System.out.println(">>> 第 " +
                        ((CyclicBarrier) Thread.currentThread()
                                .getThreadLocalRandom().nextInt()) + " 轮开始"));

        for (int i = 1; i <= userCount; i++) {
            final int userId = i;
            new Thread(() -> {
                try {
                    // 1. 在起跑线等待，模拟所有用户同时开始
                    startLatch.await();

                    for (int round = 1; round <= rounds; round++) {
                        // 2. 获取数据库连接（限流）
                        dbSemaphore.acquire();
                        try {
                            System.out.println("User-" + userId +
                                    " 第" + round + "轮: 操作数据库");
                            Thread.sleep(100);
                        } finally {
                            dbSemaphore.release();
                        }

                        // 3. 每轮结束后等待所有用户
                        if (round < rounds) {
                            roundBarrier.await();
                        }
                    }

                } catch (Exception e) {
                    Thread.currentThread().interrupt();
                } finally {
                    doneLatch.countDown();
                }
            }, "User-" + i).start();
        }

        // 发令枪: 所有线程同时开始
        startLatch.countDown();

        // 等待所有用户完成
        doneLatch.await();
        System.out.println("所有用户操作完成");
    }
}
```

### 6.5 性能考量

| 工具 | 底层机制 | 竞争开销 | 适用规模 |
|------|----------|----------|----------|
| CountDownLatch | AQS (CAS + park/unpark) | 低 | 任意 |
| CyclicBarrier | ReentrantLock + Condition | 中 | 中小规模 (< 100) |
| Semaphore | AQS (CAS + park/unpark) | 低-中 | 任意（公平模式开销稍大） |
| Phaser | 无锁 CAS + 树形优化 | 低（层次化时） | 大规模 (> 100) 建议层次化 |
| Exchanger | 槽位交换 (slot-based) | 低 | 严格为 2 |

### 6.6 最佳实践总结

1. **选择最简单的工具**：不要为了"高级"而使用复杂工具，能满足需求的最简单工具就是最好的选择
2. **始终处理中断**：所有阻塞方法都可能抛出 `InterruptedException`，正确设置中断标志
3. **设置超时避免死锁**：生产环境中几乎所有阻塞调用都应该有超时机制
4. **在 finally 块中释放资源**：`countDown()`、`release()` 等释放操作必须在 finally 中执行
5. **监控和日志**：记录等待时间、超时次数、剩余计数等指标，便于生产问题排查
6. **考虑使用 CompletableFuture 替代**：对于简单的异步等待场景，Java 8 的 `CompletableFuture` 可能更简洁
7. **注意线程池大小**：使用这些同步工具时，确保线程池有足够线程，否则可能导致死锁
8. **避免在持有锁的情况下调用阻塞方法**：防止嵌套锁导致的死锁问题

---

> **相关文档**:
> - [Java 线程与锁基础](../../../README.md)
> - [Java 并发集合](../../../README.md)
> - [Java 线程池](../../../README.md)
> - [Java 原子操作与 AQS](../../../README.md)
