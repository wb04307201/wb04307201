<!--
module:
  parent: java
  slug: java/jmm
  type: article
  category: 主模块子文章
  summary: JMM (Java Memory Model) 学习笔记
-->

# JMM (Java Memory Model) 学习笔记

## 一、什么是 JMM

Java Memory Model (JMM) 是 Java 虚拟机规范中定义的一组规则，用于**屏蔽各种硬件和操作系统的内存访问差异**，以实现让 Java 程序在各种平台下都能达到一致的并发效果。

JMM 的核心目标是：

- 定义多线程之间如何通过**主内存**进行通信
- 规定哪些共享变量是**线程共享**的，如何写入、读取
- 确定一个线程对共享变量的写入，**何时对另一个线程可见**
- 通过 **happens-before** 规则保证程序执行的有序性

```
┌─────────────────────────────────────────────────────┐
│                  Java Memory Model                   │
│                                                     │
│   ┌─────────┐   ┌──────────┐   ┌─────────┐         │
│   │ Thread1 │   │ Thread2  │   │ ThreadN │         │
│   │ 工作内存 │   │ 工作内存  │   │ 工作内存 │         │
│   └────┬────┘   └────┬─────┘   └────┬────┘         │
│        │              │              │              │
│        └──────────────┼──────────────┘              │
│                       ▼                             │
│               ┌──────────────┐                      │
│               │    主内存      │                      │
│               │  (共享变量)    │                      │
│               └──────────────┘                      │
└─────────────────────────────────────────────────────┘
```

> JMM 是一种**抽象概念**，并不真实存在。它描述的是一组规则或规范，与 CPU 缓存、寄存器有相似之处，但本质上是 JVM 层面的抽象模型。

---
## 引言：反直觉代码

JMM (Java Memory Model) 学习笔记 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 二、主内存 vs 工作内存

JMM 将内存划分为两个层次：

### 主内存 (Main Memory)

| 特征 | 说明 |
|------|------|
| 存储内容 | 所有实例变量、静态变量、数组元素 |
| 可见性 | 所有线程共享，所有线程都能访问 |
| 对应硬件 | 大致对应计算机的物理主存 (RAM) |
| 线程归属 | 不属于任何特定线程 |

### 工作内存 (Working Memory)

| 特征 | 说明 |
|------|------|
| 存储内容 | 该线程使用的变量的主内存副本 |
| 可见性 | 仅当前线程可见，其他线程无法直接访问 |
| 对应硬件 | 大致对应 CPU 缓存 (L1/L2/L3)、寄存器 |
| 线程归属 | 每个线程独占 |

```
┌──────────────────────────────────────────────────────┐
│                    主内存 (共享)                       │
│                                                      │
│   int a = 10;    int b = 20;    Object obj = ...     │
│                                                      │
│         │                      ▲                     │
│    read │                      │ store                │
│         ▼                      │                     │
│  ┌──────────────┐        ┌──────────────┐            │
│  │  Thread A    │        │  Thread B    │            │
│  │  工作内存     │        │  工作内存     │            │
│  │  a=10 (副本)  │        │  b=20 (副本)  │            │
│  └──────────────┘        └──────────────┘            │
└──────────────────────────────────────────────────────┘
```

**关键规则：**

- 线程对变量的所有操作（读取、赋值等）都必须在工作内存中进行
- 不能直接读写主内存中的变量
- 不同线程之间无法直接访问对方工作内存中的变量
- 线程间变量值的传递必须通过**主内存**来完成

---

## 三、八大原子操作

JMM 定义了 8 种原子操作，用于描述主内存与工作内存之间的交互协议。

### 操作总览

| 序号 | 操作名 | 所属内存 | 说明 |
|------|--------|----------|------|
| 1 | **lock** | 主内存 | 把变量标记为线程独占状态 |
| 2 | **unlock** | 主内存 | 释放变量独占状态，释放后其他线程可锁定 |
| 3 | **read** | 主内存 | 把变量值从主内存传输到工作内存 |
| 4 | **load** | 工作内存 | 把 read 的值放入工作内存的变量副本 |
| 5 | **use** | 工作内存 | 把变量值传递给执行引擎，遇到 use 指令时触发 |
| 6 | **assign** | 工作内存 | 把执行引擎的值放回工作内存变量，遇到 assign 时触发 |
| 7 | **store** | 工作内存 | 把工作内存变量传送到主内存 |
| 8 | **write** | 主内存 | 把 store 的值放入主内存变量中 |

### 操作流程示意

**从主内存读取变量到工作内存：**

```
  主内存变量 ──read──> 传输中 ──load──> 工作内存变量副本
```

**从工作内存写回主内存：**

```
  工作内存变量副本 ──store──> 传输中 ──write──> 主内存变量
```

### 操作约束规则

1. **不允许** read/load、store/write 单独出现，必须成对
2. **不允许** 线程丢弃最近的 assign 操作，工作内存数据必须同步回主内存
3. **不允许** 无 assign 的 load 操作，新变量必须从主内存同步
4. 变量只允许同一时刻被一个线程 lock，lock 可被同一线程多次，需对应次数 unlock
5. unlock 前必须把变量 store/write 回主内存
6. 变量未 lock 则不能 unlock，也不能 unlock 其他线程 lock 的变量
7. 变量 lock 后，工作内存中的变量副本清零，重新执行 load 操作
8. 变量 lock 只允许读操作，write 前必须先 unlock

### 代码示例

```java
/**
 * 演示主内存与工作内存的交互
 * 没有 synchronized/volatile 时，线程可能看不到最新值
 */
public class MemoryVisibilityDemo {

    // 共享变量，初始值在主内存中
    private static int counter = 0;

    public static void main(String[] args) throws InterruptedException {
        // Thread-1 的工作内存中持有 counter=0 的副本
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 10000; i++) {
                // use -> assign (在工作内存中修改)
                // store -> write (尝试写回主内存，但不保证立刻可见)
                counter++;
            }
        });

        // Thread-2 同样持有 counter=0 的副本
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 10000; i++) {
                counter++;
            }
        });

        t1.start();
        t2.start();
        t1.join();
        t2.join();

        // 由于缺少同步机制，结果可能小于 20000
        System.out.println("counter = " + counter);
    }
}
```

---

## 四、happens-before 规则

`happens-before` 是 JMM 中最核心的概念。它定义了两个操作之间的**偏序关系**：如果操作 A happens-before 操作 B，则 A 的执行结果对 B 可见。

> **本质**：happens-before 约束的是**可见性**和**有序性**，不是强制禁止重排序，而是确保重排序不会改变正确程序的结果（as-if-serial 语义）。

### 八大规则

| 序号 | 规则名称 | 说明 |
|------|----------|------|
| 1 | **程序顺序规则** | 一个线程内，按书写顺序，前面的操作 happens-before 后面的操作 |
| 2 | **锁规则** | 对一个锁的 unlock happens-before 后续对该锁的 lock |
| 3 | **volatile 规则** | 对 volatile 变量的写 happens-before 后续对该变量的读 |
| 4 | **传递规则** | A happens-before B 且 B happens-before C，则 A happens-before C |
| 5 | **线程 start 规则** | 线程 A 调用 threadB.start() happens-before 线程 B 中的任何操作 |
| 6 | **线程 join 规则** | 线程 A 的任何操作 happens-before threadA.join() 返回 |
| 7 | **线程中断规则** | 对线程 interrupt() 的调用 happens-before 被中断线程检测到中断事件 |
| 8 | **对象终结规则** | 对象的初始化完成 happens-before finalize() 方法的开始 |

### 规则详解

#### 1. 程序顺序规则 (Program Order Rule)

```java
// 在同一线程内
int a = 1;      // (1) happens-before (2)
int b = a + 1;  // (2) 能看到 (1) 的结果
```

#### 2. 锁规则 (Monitor Lock Rule)

```java
// 线程 A
synchronized (lock) {
    sharedVar = 100;   // (1)
}                      // (2) unlock

// 线程 B
synchronized (lock) {  // (3) lock — happens-before 关系
    int x = sharedVar; // (4) x == 100，能看到 (1) 的修改
}
// (2) unlock happens-before (3) lock，因此 (1) happens-before (4)
```

#### 3. volatile 规则

```java
// volatile 变量
volatile boolean flag = false;
int data = 0;

// 线程 A — 写入
data = 42;        // (1)
flag = true;      // (2) volatile 写

// 线程 B — 读取
while (!flag) {   // (3) volatile 读
    Thread.yield();
}
System.out.println(data);  // (4) data == 42
// (2) volatile 写 happens-before (3) volatile 读
// (1) happens-before (2)，(3) happens-before (4)
// 传递性：(1) happens-before (4)，所以 data 一定是 42
```

#### 4. 传递规则 (Transitivity)

```
A ──happens-before──> B ──happens-before──> C
═══════════════════════════════════════════════
        A happens-before C (传递性)
```

#### 5. 线程 start 规则

```java
int localVar = 100;
Thread t = new Thread(() -> {
    // 这里一定能看到 localVar = 100 以及 t.start() 之前的所有操作
    System.out.println(localVar);  // 输出 100
});
localVar = 200;    // happens-before t.start()
t.start();         // start() happens-before 线程内的所有操作
```

#### 6. 线程 join 规则

```java
Thread t = new Thread(() -> {
    sharedValue = 999;   // 线程内操作
});
t.start();
t.join();                // join() 返回时，能看到线程内所有操作
System.out.println(sharedValue);  // 一定是 999
```

---

## 五、内存屏障 (Memory Barrier)

内存屏障（Memory Barrier / Memory Fence）是 CPU 或编译器提供的一种**同步原语**，用于控制指令的重排序和内存可见性。

### 四种基本屏障

| 屏障类型 | 名称 | 作用 |
|----------|------|------|
| **LoadLoad** | Load-Load Barrier | 确保 Load1 的数据装载先于 Load2 及后续的装载指令 |
| **StoreStore** | Store-Store Barrier | 确保 Store1 的数据对处理器可见先于 Store2 及后续存储 |
| **LoadStore** | Load-Store Barrier | 确保 Load1 的数据装载先于 Store2 及后续存储刷新 |
| **StoreLoad** | Store-Load Barrier | 确保 Store1 的数据对处理器可见先于 Load2 及后续装载 |

### 屏障语义示意

```
LoadLoad 屏障:
    Load1
    ── [LoadLoad] ──
    Load2
  (Load2 必须在 Load1 完成之后执行)

StoreStore 屏障:
    Store1
    ── [StoreStore] ──
    Store2
  (Store1 必须先于 Store2 刷新到主存)

LoadStore 屏障:
    Load1
    ── [LoadStore] ──
    Store2
  (Store2 必须在 Load1 之后执行)

StoreLoad 屏障:
    Store1
    ── [StoreLoad] ──
    Load2
  (Load2 必须在 Store1 刷新后执行，开销最大)
```

### 各类 CPU 对屏障的支持

| CPU 架构 | LoadLoad | StoreStore | LoadStore | StoreLoad | 备注 |
|----------|----------|------------|-----------|-----------|------|
| x86 | 不需要 | mfence | mfence | mfence | 强内存模型，只禁止 Store-Load 重排序 |
| ARM | 需要 | 需要 | 需要 | 需要 | 弱内存模型，需要大量屏障指令 |
| PowerPC | 需要 | 需要 | 需要 | 需要 | 弱内存模型 |

> **StoreLoad 屏障是四种中开销最大的**，因为在很多架构上需要刷新写缓冲区（Store Buffer）并等待其完成。

---

## 六、volatile 的内存屏障语义

`volatile` 是 JMM 提供的一种**轻量级同步机制**，它通过内存屏障来保证：

1. **可见性**：写操作的结果对其他线程立即可见
2. **有序性**：禁止指令重排序优化

### volatile 写操作的屏障策略

```
在每个 volatile 写操作之前插入 StoreStore 屏障
在每个 volatile 写操作之后插入 StoreLoad 屏障
```

```
volatile 写:
    普通 Store1
    ── [StoreStore] ──
    volatile Store
    ── [StoreLoad] ──
    后续任意操作
```

### volatile 读操作的屏障策略

```
在每个 volatile 读操作之后插入 LoadLoad 屏障
在每个 volatile 读操作之后插入 LoadStore 屏障
```

```
volatile 读:
    volatile Load
    ── [LoadLoad] ──
    后续 Load
    ── [LoadStore] ──
    后续 Store
```

### volatile 屏障总结表

| 操作 | 屏障插入位置 | 屏障类型 |
|------|------------|----------|
| volatile 写 | 写操作之前 | StoreStore |
| volatile 写 | 写操作之后 | StoreLoad |
| volatile 读 | 读操作之后 | LoadLoad |
| volatile 读 | 读操作之后 | LoadStore |

### 代码示例

```java
public class VolatileBarrierDemo {

    // 普通变量
    int a = 0;
    String s = "";

    // volatile 变量
    volatile boolean flag = false;

    // 线程 A 执行 writer()
    public void writer() {
        a = 1;              // 普通写
        s = "hello";        // 普通写
        // --- [StoreStore 屏障] ---
        flag = true;        // volatile 写
        // --- [StoreLoad 屏障] ---
    }

    // 线程 B 执行 reader()
    public void reader() {
        if (flag) {         // volatile 读
            // --- [LoadLoad 屏障] ---
            // --- [LoadStore 屏障] ---
            // 这里一定能看到 a=1 和 s="hello"
            System.out.println(a);  // 输出 1
            System.out.println(s);  // 输出 hello
        }
    }
}
```

### 为什么 volatile 不保证原子性

```java
// volatile 不能保证复合操作的原子性
public class VolatileNotAtomic {
    // volatile 只保证可见性和有序性，不保证 i++ 的原子性
    private volatile int i = 0;

    public void increment() {
        i++;  // 这是三个操作: read -> add -> write
              // volatile 无法让这三个步骤原子执行
    }
}

// 正确做法：使用 AtomicInteger
import java.util.concurrent.atomic.AtomicInteger;

public class AtomicCounter {
    private AtomicInteger i = new AtomicInteger(0);

    public void increment() {
        i.incrementAndGet();  // CAS 保证原子性
    }
}
```

---

## 七、final 域的内存屏障

JSR-133 规范对 `final` 域的语义进行了增强。对于 `final` 域，编译器和处理器需要遵守以下约束：

### 规则

| 序号 | 规则 | 说明 |
|------|------|------|
| 1 | 写 final 域重排序规则 | 构造函数中对 final 域的写不能被重排序到构造函数之外 |
| 2 | 读 final 域重排序规则 | 初次读一个对象的 final 域与初次读该对象引用不能重排序 |

### 内存屏障插入

| 操作 | 屏障插入 | 说明 |
|------|----------|------|
| final 域写后 | 在构造函数返回前插入 **StoreStore** 屏障 | 确保 final 域的写操作对其他线程可见 |
| final 域读前 | 在读 final 域之前插入 **LoadLoad** 屏障 | 确保读到的对象已被正确初始化 |

### 示例

```java
public class FinalExample {
    final int x;            // final 域
    int y;                  // 普通域
    static FinalExample obj;

    public FinalExample(int x, int y) {
        this.x = x;         // final 域写 — 不能被重排序到构造方法外
        this.y = y;         // 普通域写 — 可能被重排序
    }

    // 线程 A 调用
    public static void writer() {
        obj = new FinalExample(100, 200);
    }

    // 线程 B 调用
    public static void reader() {
        FinalExample local = obj;
        if (local != null) {
            int a = local.x;  // final 域读 — 一定能看到 100
            int b = local.y;  // 普通域读 — 不一定是 200（可能被重排序）
        }
    }
}
```

```
线程 A:  new FinalExample(100, 200)
          │
          ├── this.x = 100;     (final 域写)
          ├── this.y = 200;     (普通域写，可能被重排序)
          ├── [StoreStore 屏障]  (JSR-133 要求)
          └── obj = ...         (引用赋值)

线程 B:  local = obj;
          │
          ├── [LoadLoad 屏障]   (读 final 域前)
          ├── a = local.x;     (final 域读 — 一定是 100)
          └── b = local.y;     (普通域读 — 可能是默认值 0)
```

---

## 八、JSR-133 规范简述

### 什么是 JSR-133

JSR-133 (Java Specification Request #133) 全称为 **"JSR-133: Java Memory Model and Thread Specification Revision"**，是对 Java 1.5 中 Java 内存模型和线程规范的重大修订。

在 Java 1.4 及之前，JMM 存在严重缺陷：

- volatile 不能防止指令重排序
- final 域可以被其他线程看到未初始化的值
- 线程同步语义不够明确
- 很多代码在理论上正确但实际上不可靠

### JSR-133 的主要改进

| 改进项 | Java 1.4 (旧 JMM) | Java 1.5+ (JSR-133) |
|--------|-------------------|---------------------|
| volatile 语义 | 仅保证可见性 | 保证可见性 + 禁止重排序 |
| final 语义 | 可能看到半初始化对象 | 构造函数返回前确保 final 域初始化完成 |
| happens-before | 无明确定义 | 明确定义 8 条 happens-before 规则 |
| synchronized | 语义模糊 | 语义增强，与 happens-before 对齐 |
| 原子类 | 无 | 新增 `java.util.concurrent.atomic` 包 |
| 锁和条件变量 | 无 | 新增 `java.util.concurrent.locks` 包 |

### happens-before 形式化定义

JSR-133 引入了 happens-before 作为 JMM 的核心约束关系：

```
hb(a, b)  当且仅当  操作 a 对内存的影响对操作 b 可见
```

核心特性：

```
1. 自反性: hb(a, a)          总是成立
2. 传递性: hb(a, b) ∧ hb(b, c) → hb(a, c)
3. 偏序性: 不构成 happens-before 的操作对之间，允许重排序
```

### 与 as-if-serial 的关系

```
┌──────────────────────────────────────────────┐
│                 as-if-serial                   │
│                                              │
│  单线程视角：无论怎么重排序，执行结果          │
│  必须和按代码顺序执行的结果一致              │
│                                              │
│  JMM 保证：                                  │
│  - 线程内：程序顺序规则保证 as-if-serial       │
│  - 线程间：happens-before 保证可见性           │
│  - 无 hb 关系的操作：可自由重排序              │
└──────────────────────────────────────────────┘
```

### JMM 在现代 Java 中的体现

```java
// JSR-133 后，以下构造都是线程安全的：

// 1. Double-Checked Locking (DCL) — volatile 修复后安全
public class Singleton {
    private static volatile Singleton instance;

    public static Singleton getInstance() {
        if (instance == null) {                      // 第一次检查
            synchronized (Singleton.class) {
                if (instance == null) {              // 第二次检查
                    instance = new Singleton();      // volatile 保证可见性和有序性
                }
            }
        }
        return instance;
    }
}

// 2. 安全发布 (Safe Publication) 模式
public class SafePublication {
    private volatile Holder holder;

    public void initialize() {
        holder = new Holder(42);   // volatile 写保证安全发布
    }

    public int getValue() {
        return holder == null ? 0 : holder.value;  // volatile 读
    }
}

// 3. CountDownLatch 使用 happens-before 规则
import java.util.concurrent.CountDownLatch;

public class CountDownLatchDemo {
    public static void main(String[] args) throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(3);

        for (int i = 0; i < 3; i++) {
            new Thread(() -> {
                // 线程内操作 happens-before latch.countDown()
                doWork();
                latch.countDown();   // volatile 写（AQS 内部）
            }).start();
        }

        // latch.await() happens-before await() 返回后的所有操作
        latch.await();
        System.out.println("All tasks completed");
    }
}
```

### 总结

```
┌─────────────────────────────────────────────────┐
│              JSR-133 核心要点                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. 引入 happens-before 作为可见性保证           │
│  2. 增强 volatile 语义: 可见性 + 有序性          │
│  3. 增强 final 语义: 构造函数安全发布            │
│  4. 提供原子操作和高级并发工具                    │
│  5. 屏蔽硬件差异，保证跨平台一致性                 │
│                                                 │
│  核心口诀:                                        │
│  - 单线程看 as-if-serial                          │
│  - 多线程看 happens-before                        │
│  - 共享变量加锁或使用 volatile                     │
│  - 无 hb 关系 = 可能看到陈旧数据                   │
│                                                 │
└─────────────────────────────────────────────────┘
```
