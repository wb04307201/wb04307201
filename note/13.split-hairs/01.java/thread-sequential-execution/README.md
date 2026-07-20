<!--
question:
  id: 01.java-thread-sequential-execution
  topic: 01.java
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 工程实现
  tags: [01.java, Thread, join, CountDownLatch, CompletableFuture, 顺序执行]
-->

# 三个线程 T1、T2、T3 怎么确保它们按顺序执行？

> 一句话定位：**Java 面试经典 Top 10**。考察的不是"会用 join"，而是**3 种语义**（串行 / 分支 / 汇合）+ **8 种方案对比** + **实战选型**。深度原理见 [主模块深度章节](../../../01.java/concurrency/thread-basics/sequential-execution.md)。

> **系列定位**：高频 Java 面试题（校招 / 社招均考）。考察工程化判断力 + 多线程协作能力。配套同栏目兄弟题：[ThreadPool 面试题](../thread-pool/README.md) / [ThreadLocal 面试题](../threadlocal/README.md)。

---

⭐⭐⭐ 深度级别（中级 Java 工程师级）
📚 前置知识：Thread.join() / CountDownLatch / CompletableFuture 基本用法

---

## 引子：面试官的"语义陷阱"

面试官："有 T1、T2、T3 三个线程，怎么确保它们按顺序执行？"

阿明答："用 `Thread.join()`，t1.start(); t1.join(); t2.start(); t2.join(); t3.start();"

面试官追问："**等等，你说的'按顺序'是哪种？T1 → T2 → T3 串行？还是 T1 → (T2, T3 并行)？还是 (T1, T2 并行) → T3？**"

阿明答："……串行吧。"

面试官："**不知道语义就答方案 = 答错**。先问清'什么算顺序'，再选方案 —— 这才是工程化思考。"

阿明愣住。

**这道题的陷阱**：考察的不是某个工具的 API，而是**多线程编排的工程判断力**。

---

## Q1：3 线程"按顺序执行"有几种语义？

**答**：**3 种**。先问清语义，再选方案。

```
面试官说"按顺序"——具体是哪种？

├─ 语义 1：串行（T1 完成 → T2 开始 → T3 开始）
│   └─ 最常见的理解 ——"3 线程串行执行"
│
├─ 语义 2：分支（T1 完成 → T2 和 T3 并行开始）
│   └─ 实际场景：T1 初始化 → T2 读数据 + T3 写数据并行
│
└─ 语义 3：汇合（T1 和 T2 并行 → 都完成后 T3 开始）
    └─ 实际场景：T1 读 Redis + T2 读 DB → 都完成后 T3 处理
```

**反直觉点**：很多人一上来就答"用 join"，但**没问清语义就答 = 答错**。**第一步永远是问"什么算顺序"**。

**面试话术**：
> "先确认是哪种语义。**串行**用 `Thread.join()` 或 `CompletableFuture.thenRun()`；**分支**用 `thenRunAsync` + `allOf`；**汇合**用 `CountDownLatch` 或 `allOf`。"

---

## Q2：`Thread.join()` 怎么实现顺序？原理是什么？

**答**：**调用方线程阻塞**，直到目标线程终止。

```java
t1.start();
t1.join();  // 主线程阻塞，直到 T1 终止

t2.start();
t2.join();  // 主线程阻塞，直到 T2 终止

t3.start();
t3.join();  // 主线程阻塞，直到 T3 终止
```

**原理**（基于 wait/notify）：
- `join()` 内部调用 `synchronized(锁对象)` + `wait(0)`，释放锁并阻塞当前线程
- 目标线程终止时，JVM 调用 `lock.notifyAll()` 唤醒所有等待者
- 调用方线程被唤醒后继续执行

**优点**：
- ✅ 一行代码搞定
- ✅ 不需要额外对象

**缺点**：
- ❌ 阻塞**调用方线程**（不是被 join 的线程）
- ❌ 不适合分支 / 汇合语义
- ❌ 串行化整个流程（不是并行）

**反直觉点**：**`join()` 是阻塞调用方**，不是阻塞目标线程。`t1.join()` 是**主线程**被阻塞，等 T1 终止。

---

## Q3：`CountDownLatch` vs `Thread.join()` 怎么选？

**答**：根据场景选：

| 场景 | 推荐 | 理由 |
|------|------|------|
| 简单串行（demo）| `Thread.join()` | 代码最简单 |
| **串行 + 可扩展**（生产环境）| **`CountDownLatch`** | 多阶段串联 + 汇合都支持 |
| 复杂编排（分支 / 异步链）| `CompletableFuture` | 链式调用最优雅 |

**CountDownLatch 的优势**（对比 join）：

1. **可扩展**：N 个线程汇合、N 个串行阶段都能用
2. **非阻塞**：`countDown()` 不阻塞，调用方线程可以继续做别的事
3. **可重用语义**：虽然一次性，但可以用多个 latch 串联

**对比代码**：

```java
// 串行（join）：主线程被反复阻塞
t1.start(); t1.join();
t2.start(); t2.join();
t3.start(); t3.join();

// 串行（CountDownLatch）：T1 / T2 / T3 自己等待，不阻塞主线程
CountDownLatch latch = new CountDownLatch(3);
Runnable task = () -> { doWork(); latch.countDown(); };
new Thread(task).start();  // T1
new Thread(task).start();  // T2
new Thread(task).start();  // T3
latch.await();  // 主线程等 3 个都完成

// 汇合（CountDownLatch）：T1 + T2 并行 → T3
CountDownLatch latch = new CountDownLatch(2);
new Thread(() -> { doT1(); latch.countDown(); }).start();
new Thread(() -> { doT2(); latch.countDown(); }).start();
new Thread(() -> { latch.await(); doT3(); }).start();
```

**反直觉点**：**`CountDownLatch` 是"一次性"**——`countDown()` 到 0 后无法重置。需要重复使用用 `CyclicBarrier`。

---

## Q4：`CompletableFuture` 怎么实现顺序？链式调用最佳实践是什么？

**答**：用 `thenRun()` / `thenRunAsync()` 链式触发，**优雅处理 3 种语义**。

```java
// 串行：T1 → T2 → T3
CompletableFuture.runAsync(() -> doT1())
    .thenRunAsync(() -> doT2())
    .thenRunAsync(() -> doT3())
    .join();  // 主线程等所有完成

// 分支：T1 → (T2, T3 并行) → 主流程继续
CompletableFuture<Void> t2 = CompletableFuture.runAsync(() -> doT1())
    .thenRunAsync(() -> doT2());
CompletableFuture<Void> t3 = CompletableFuture.runAsync(() -> doT1())
    .thenRunAsync(() -> doT3());
CompletableFuture.allOf(t2, t3).join();

// 汇合：(T1, T2 并行) → T3
CompletableFuture<Void> t1 = CompletableFuture.runAsync(() -> doT1());
CompletableFuture<Void> t2 = CompletableFuture.runAsync(() -> doT2());
CompletableFuture.allOf(t1, t2)
    .thenRunAsync(() -> doT3())
    .join();
```

**`runAsync` vs `thenRunAsync` 的区别**：
- `runAsync`：提交任务到 ForkJoinPool.commonPool()（默认线程池）
- `thenRunAsync`：上一步完成后**异步**执行下一步（**不在**上一步的线程里）

**生产环境踩坑**：
- ❌ 不指定线程池 → 用 commonPool（IO 密集型任务可能阻塞）
- ✅ 推荐：传入自定义线程池 `CompletableFuture.runAsync(task, executor)`

**优势**：
- ✅ 链式调用一目了然
- ✅ 3 种语义都能自然表达
- ✅ Java 8+ 现代写法

---

## Q5：生产环境推荐哪种方案？怎么选？

**答**：**首选 `CompletableFuture` + 自定义线程池**，其次 `CountDownLatch`。

**完整选型决策树**：

```
你的场景是？
├─ 简单串行（demo / 一次性）
│   └─ Thread.join()（最简单）
├─ 复杂编排（分支 / 汇合 / 异步链）
│   └─ CompletableFuture + 自定义线程池（首选）
├─ 纯串行任务队列
│   └─ SingleThreadExecutor
└─ 多线程并行 → 共同继续
    └─ CyclicBarrier 或 CompletableFuture.allOf
```

**8 方案对比表**（推荐度排序）：

| 方案 | 推荐度 | 理由 |
|------|------:|------|
| **CompletableFuture** | ⭐⭐⭐⭐⭐ | 现代写法、3 语义全覆盖 |
| **CountDownLatch** | ⭐⭐⭐⭐⭐ | 生产首选、可扩展 |
| Thread.join() | ⭐⭐⭐ | 简单但阻塞主线程 |
| SingleThreadExecutor | ⭐⭐⭐⭐ | 纯串行任务流 |
| Semaphore | ⭐⭐⭐ | 可重置 |
| CyclicBarrier | ⭐⭐ | 仅汇合场景 |
| wait/notify | ⭐ | 不推荐，易死锁 |
| Lock + Condition | ⭐ | 杀鸡用牛刀 |

**反模式**（不要做的事）：
- ❌ 用 `volatile` 共享标志位（忙等 / 内存可见性问题）
- ❌ 自旋等待 `while (!flag) Thread.sleep(10)`（CPU 空转）
- ❌ `Thread.sleep(1000)` 模拟等待（不可靠）
- ❌ 共享一个 lock + 标志位串行（锁粒度太大）

---

## 总结：面试答这题的 3 层结构

**30 秒简版**：
> "先确认是哪种语义 —— 串行 / 分支 / 汇合。**首选 `CompletableFuture`**，链式 `thenRunAsync` + `allOf` 一目了然；简单场景用 `Thread.join()`；生产环境用 `CountDownLatch`（可扩展）。**避免**用 `wait/notify` 写复杂状态机（容易死锁）。"

**60 秒扩展版**（面试官追问细节）：
> "具体来说，`Thread.join()` 阻塞调用方线程（不是被 join 的线程），适合简单串行；`CountDownLatch` 是计数器 = 0 后所有 `await()` 唤醒，适合 N 线程汇合；`CompletableFuture` 是链式回调，`thenRunAsync` 不在上一步的线程里跑（避免阻塞）。生产环境踩坑：**必须传自定义线程池**给 `runAsync`，否则用 commonPool 可能阻塞其他任务。"
>
> "反模式：用 `volatile` 标志位串行 —— 内存可见性 OK，但 busy-wait CPU 空转；用 `Thread.sleep` 模拟等待 —— 生产必崩。"

**踩分点提醒**：
- ✅ 提"3 种语义" → 显式说明串行 / 分支 / 汇合
- ✅ 提"先问清语义再选方案" → 显式工程化思考
- ✅ 提"避免 wait/notify" → 显式知道反模式
- ✅ 提"必须传线程池" → 显式知道 CompletableFuture 陷阱

---

## 相关章节

**主模块**：
- [三个线程按顺序执行深度章节](../../../01.java/concurrency/thread-basics/sequential-execution.md) — 8 方案对比 + 实战模板 + 选型决策树
- [Thread 基础（thread-basics/README）](../../../01.java/concurrency/thread-basics/README.md) — `Thread.join()` / 中断机制
- [JUC 工具类](../../../01.java/concurrency/utilities/README.md) — CountDownLatch / CyclicBarrier / Semaphore
- [CompletableFuture 深度章节](../../../01.java/concurrency/completablefuture/README.md) — 异步编排全貌

**同栏目（01.java 高频面试题）**：
- [ThreadPool 为什么用线程池？](../thread-pool/README.md) — 线程池原理
- [ThreadLocal 为什么会有内存泄漏？](../threadlocal/README.md) — 线程局部变量
- [AQS 是什么？](../aqs/README.md) — 锁底层原理

**主模块其他相关**：
- [JUC 锁](../../../01.java/concurrency/juc-locks/README.md) — ReentrantLock / Condition

---

> 📅 2026-07-06 · 咬文嚼字 · 01.java · ⭐⭐⭐

← [返回: 咬文嚼字 · thread-sequential-execution](../README.md)
