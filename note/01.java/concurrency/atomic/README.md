<!--
module:
  parent: java
  slug: java/atomic
  type: article
  category: 主模块子文章
  summary: Java 并发包 `java.util.concurrent.atomic` 中的原子类，基于 CAS 实现无锁并发，是高性能并发编程的核心工具。
-->

# 原子类学习笔记

> Java 并发包 `java.util.concurrent.atomic` 中的原子类，基于 CAS 实现无锁并发，是高性能并发编程的核心工具。

---
---

## 一、CAS 原理（Compare-And-Swap）

### 1.1 什么是 CAS

CAS（Compare-And-Swap / Compare-And-Set）是一种无锁的原子操作算法。它在更新变量时，会先比较当前值是否等于预期值，如果相等则更新为新值，否则不执行任何操作。

```
┌─────────────────────────────────────────────────┐
│                  CAS 操作逻辑                      │
├─────────────────────────────────────────────────┤
│                                                 │
│   当前内存值 V                                    │
│       ↓                                         │
│   ┌──────────────┐                              │
│   │  V == A ?     │                              │
│   └──┬────────┬──┘                              │
│      │ 是     │ 否                               │
│      ↓       ↓                                  │
│   V = B    返回 false                            │
│   返回 true   (重试)                              │
│                                                 │
│   A = 预期值（Expected Value）                    │
│   B = 新值（New Value）                           │
│   V = 内存中的当前值（Current Value）               │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 1.2 CAS 的硬件基础

CAS 操作最终依赖 CPU 的原子指令实现：

| CPU 架构 | 底层指令 | 说明 |
|---------|---------|------|
| x86 | `CMPXCHG` + `LOCK` 前缀 | 锁定总线或缓存行，保证多核下的原子性 |
| ARM | `LDREX` + `STREX` | 独占加载/存储，基于 LL/SC 模型 |

### 1.3 Java 中的 CAS 实现

Java 通过 `sun.misc.Unsafe` 类提供 CAS 操作，原子类封装了对 Unsafe 的调用：

```java
// AtomicInteger 中的核心方法
public final boolean compareAndSet(int expect, int update) {
    return unsafe.compareAndSwapInt(this, valueOffset, expect, update);
}
```

### 1.4 CAS 伪代码

```java
public final int getAndIncrement() {
    int current;
    int next;
    do {
        current = this.value;           // 读取当前值
        next = current + 1;             // 计算新值
    } while (!compareAndSet(current, next)); // CAS 失败则重试
    return current;
}
```

### 1.5 CAS 的优点

- **无锁**：不会造成线程阻塞，避免死锁问题
- **低开销**：失败时自旋重试，避免上下文切换
- **高吞吐**：低竞争场景下性能优于 `synchronized`

---

## 二、ABA 问题及解决

### 2.1 什么是 ABA 问题

ABA 问题是 CAS 机制的一个经典缺陷：

```
┌─────────────────────────────────────────────────────────┐
│                    ABA 问题演示                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  线程1                          线程2                    │
│  ─────                          ─────                    │
│  读取值 A = 10                                             │
│  ─────────────────────────────→                        │
│                                修改 A = 100               │
│                                修改 A = 10 (改回来了!)     │
│  ←─────────────────────────────                        │
│  CAS(10, 20) → 成功！但值已被修改过                      │
│                                                         │
│  问题：CAS 只比较值，不关心值是否被"动过"                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 ABA 问题的危害

| 场景 | 危害 |
|------|------|
| 无锁栈 | 栈节点被复用后导致内存访问错误 |
| 无锁链表 | 节点被回收后重新分配，造成 dangling pointer |
| 业务状态 | 值相同但中间状态已变化，业务逻辑出错 |

### 2.3 解决方案：AtomicStampedReference

`AtomicStampedReference` 通过引入**版本号（stamp）**来解决 ABA 问题。每次更新时版本号递增，CAS 时同时比较值和版本号。

```java
// 创建带版本号的引用，初始值为 10，版本号为 0
AtomicStampedReference<Integer> stampedRef = new AtomicStampedReference<>(10, 0);

int[] stampHolder = new int[1];
Integer value = stampedRef.get(stampHolder);
int stamp = stampHolder[0];

// CAS 时同时校验值和版本号
boolean success = stampedRef.compareAndSet(
    value,      // 预期值
    20,         // 新值
    stamp,      // 预期版本号
    stamp + 1   // 新版本号
);
```

### 2.4 AtomicStampedReference vs AtomicReference

| 特性 | AtomicReference | AtomicStampedReference |
|------|-----------------|------------------------|
| 比较内容 | 仅比较值 | 同时比较值和版本号 |
| ABA 防护 | 无 | 有 |
| 性能 | 更高 | 略低（多一次版本号比较） |
| 内存开销 | 小 | 大（额外存储版本号） |
| 适用场景 | 值不会被改回原值的场景 | 需要严格 ABA 防护的场景 |

### 2.5 另一个方案：AtomicMarkableReference

`AtomicMarkableReference` 使用一个布尔标记代替版本号，适用于只需标记"是否被修改过"的场景：

```java
// 第二个参数是 boolean 标记，不是递增的版本号
AtomicMarkableReference<String> markableRef =
    new AtomicMarkableReference<>("data", false);

// 标记为已处理
markableRef.compareAndSet("data", "data", false, true);
```

---

## 三、基本原子类

### 3.1 AtomicInteger

最常用的原子整数类。

```java
AtomicInteger counter = new AtomicInteger(0);

// 核心方法
counter.get();                    // 获取当前值
counter.set(100);                 // 设置值
counter.incrementAndGet();        // ++i，返回新值
counter.getAndIncrement();        // i++，返回旧值
counter.decrementAndGet();        // --i
counter.getAndDecrement();        // i--
counter.addAndGet(5);             // i += 5，返回新值
counter.getAndAdd(5);             // 返回旧值
counter.compareAndSet(100, 200);  // CAS
counter.updateAndGet(x -> x * 2); // Lambda 更新
```

### 3.2 AtomicLong

与 AtomicInteger 类似，但操作的是 `long` 类型（64 位）。

```java
AtomicLong counter = new AtomicLong(0L);

// API 与 AtomicInteger 基本一致
counter.incrementAndGet();
counter.compareAndSet(100L, 200L);
counter.getAndUpdate(x -> x + 10);
```

> **注意**：在 Java 8 之前，高竞争下 `AtomicLong` 的性能不如 `AtomicInteger`，因为 64 位 CAS 在某些平台上需要两条指令。Java 8 之后推荐使用 `LongAdder`。

### 3.3 AtomicBoolean

原子布尔值类。

```java
AtomicBoolean flag = new AtomicBoolean(false);

// 典型用法：只执行一次
if (flag.compareAndSet(false, true)) {
    // 只有一个线程能进入
    System.out.println("首次执行初始化逻辑");
}
```

### 3.4 基本原子类方法对照表

| 方法 | AtomicInteger | AtomicLong | AtomicBoolean |
|------|:---:|:---:|:---:|
| `get()` | ✓ | ✓ | ✓ |
| `set()` | ✓ | ✓ | ✓ |
| `getAndSet()` | ✓ | ✓ | ✓ |
| `compareAndSet()` | ✓ | ✓ | ✓ |
| `incrementAndGet()` | ✓ | ✓ | × |
| `getAndIncrement()` | ✓ | ✓ | × |
| `decrementAndGet()` | ✓ | ✓ | × |
| `addAndGet()` | ✓ | ✓ | × |
| `updateAndGet()` | ✓ | ✓ | × |

---

## 四、数组原子类

### 4.1 AtomicIntegerArray

对整型数组的每个元素提供原子操作。

```java
int[] arr = {1, 2, 3, 4, 5};
AtomicIntegerArray atomicArray = new AtomicIntegerArray(arr);

atomicArray.get(0);                    // 获取索引 0 的值
atomicArray.set(0, 100);               // 设置索引 0 的值
atomicArray.getAndSet(0, 200);         // 设置并返回旧值
atomicArray.getAndIncrement(1);        // arr[1]++
atomicArray.incrementAndGet(1);        // ++arr[1]
atomicArray.compareAndSet(2, 3, 99);   // CAS: arr[2]==3 则设为 99
atomicArray.addAndGet(3, 10);          // arr[3] += 10
```

> **注意**：数组原子类在构造时会对传入数组做**防御性拷贝**，后续对原始数组的修改不会影响原子数组。

### 4.2 AtomicLongArray

与 `AtomicIntegerArray` 类似，但元素类型为 `long`。

```java
long[] data = {100L, 200L, 300L};
AtomicLongArray longArray = new AtomicLongArray(data);

longArray.getAndIncrement(0);
longArray.addAndGet(1, 50L);
```

### 4.3 AtomicReferenceArray

对对象引用数组提供原子操作。

```java
String[] names = {"Alice", "Bob", "Charlie"};
AtomicReferenceArray<String> refArray = new AtomicReferenceArray<>(names);

refArray.set(0, "David");
String old = refArray.getAndSet(1, "Eve");
refArray.compareAndSet(2, "Charlie", "Frank");
```

### 4.4 数组原子类对比

| 类 | 元素类型 | 内存布局 | 典型场景 |
|----|---------|---------|---------|
| AtomicIntegerArray | int | 连续 int 数组 | 计数器数组、统计 |
| AtomicLongArray | long | 连续 long 数组 | 高精度统计 |
| AtomicReferenceArray | 引用(T) | 引用数组 | 对象池、无锁数据结构 |

---

## 五、字段更新器

### 5.1 AtomicIntegerFieldUpdater

当不能修改已有类的源码，但需要对其中某个 `volatile` 字段做原子更新时使用。

```java
public class User {
    // 必须是 volatile，且不能是 static
    public volatile int score;
}

// 创建更新器（类、字段名）
AtomicIntegerFieldUpdater<User> updater =
    AtomicIntegerFieldUpdater.newUpdater(User.class, "score");

User user = new User();
updater.incrementAndGet(user);   // score++
updater.compareAndSet(user, 0, 100);
```

### 5.2 注意事项

```java
// 字段更新器的严格约束：
//
// 1. 字段必须用 volatile 修饰
// 2. 字段不能是 static（静态字段）
// 3. 字段必须是基本类型（int / long / boolean）或引用类型
// 4. 字段必须在指定的类或父类中
// 5. 字段名必须完全匹配（字符串，无编译期检查）
```

### 5.3 三种字段更新器

| 更新器 | 目标类型 | 适用字段 |
|--------|---------|---------|
| AtomicIntegerFieldUpdater | int | `volatile int` 字段 |
| AtomicLongFieldUpdater | long | `volatile long` 字段 |
| AtomicReferenceFieldUpdater<T,V> | 引用 | `volatile V` 字段 |

### 5.4 性能对比

```
直接使用 volatile 字段          : ████████████████████ (最快)
AtomicInteger                   : ████████████████
AtomicIntegerFieldUpdater       : ████████████ (最慢，反射开销)

原因：字段更新器底层通过反射获取字段的偏移量，
      且每次操作都需要将目标对象作为参数传递，
      比直接使用原子类有额外的方法调用开销。
```

---

## 六、累加器（Java 8+）

### 6.1 LongAdder

`LongAdder` 是 Java 8 引入的高性能累加器，采用**分段累加**（Cell Striping）策略。

```java
LongAdder adder = new LongAdder();

adder.increment();              // 等价于 add(1)
adder.add(10L);                 // 增加指定值
long total = adder.sum();       // 获取总和
adder.reset();                  // 重置为 0
```

**核心原理**：

```
┌──────────────────────────────────────────────────────────┐
│                  LongAdder 内部结构                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   +------------+      +----+----+----+----+               │
│   |   base     |─────→|cell|cell|cell|cell| ...           │
│   |  (long)    |      +----+----+----+----+               │
│   +------------+        ↑                                 │
│                         │                                 │
│         低竞争时直接更新 base                               │
│         高竞争时分散到不同的 cell 上累加                     │
│         sum() = base + Σ(cell[i].value)                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 6.2 LongAccumulator

`LongAccumulator` 是 `LongAdder` 的泛化版本，允许自定义累加函数。

```java
// 自定义累加器：取最大值 (相当于 max 操作)
LongAccumulator maxAccumulator = new LongAccumulator(
    (a, b) -> Math.max(a, b),  // 累加函数
    Long.MIN_VALUE              // 初始值
);

maxAccumulator.accumulate(10);
maxAccumulator.accumulate(50);
maxAccumulator.accumulate(30);
System.out.println(maxAccumulator.get());  // 50
```

### 6.3 DoubleAdder

`LongAdder` 的 `double` 版本，用法完全一致。

```java
DoubleAdder adder = new DoubleAdder();

adder.add(3.14);
adder.add(2.71);
double total = adder.sum();   // 5.85
adder.reset();
```

### 6.4 DoubleAccumulator

`LongAccumulator` 的 `double` 版本。

```java
DoubleAccumulator acc = new DoubleAccumulator(
    (a, b) -> a + b,
    0.0
);

acc.accumulate(1.5);
acc.accumulate(2.5);
System.out.println(acc.get());  // 4.0
```

### 6.5 累加器家族总结

| 类 | 数据类型 | 操作 | 初始值 | 说明 |
|----|---------|------|--------|------|
| LongAdder | long | 加法 | 0 | 最常用的高性能累加器 |
| LongAccumulator | long | 自定义 | 指定 | 支持任意二元运算 |
| DoubleAdder | double | 加法 | 0.0 | double 版 LongAdder |
| DoubleAccumulator | double | 自定义 | 指定 | double 版 LongAccumulator |

---

## 七、LongAdder vs AtomicLong 性能对比

### 7.1 核心差异

```
┌────────────────────────────────────────────────────────────┐
│              AtomicLong vs LongAdder 架构对比               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  AtomicLong:                                               │
│  ┌────────────────────────┐                                │
│  │    单个 volatile long   │ ← 所有线程竞争同一个 CAS 位置    │
│  │    (value = 0)         │   高竞争 → 大量 CAS 失败重试     │
│  └────────────────────────┘                                │
│                                                            │
│  LongAdder:                                                │
│  ┌──────────────┐  ┌───┐ ┌───┐ ┌───┐ ┌───┐               │
│  │ base = 0     │  │ C1│ │ C2│ │ C3│ │ C4│               │
│  └──────────────┘  └───┘ └───┘ └───┘ └───┘               │
│     ↑                │     │     │     │                  │
│  低竞争时用    线程根据 hash 分散到不同 cell                   │
│  base 直接加   每个 cell 独立累加，无竞争                      │
│  sum() = base + C1 + C2 + C3 + C4                           │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 7.2 性能测试对比

在 16 线程并发累加 1000 万次的环境下的典型结果：

| 指标 | AtomicLong | LongAdder | 说明 |
|------|-----------|-----------|------|
| 吞吐量 | ~50K ops/s | ~200K ops/s | LongAdder 约 4 倍 |
| CAS 失败率 | 高（大量竞争） | 极低（分散到 cell） | LongAdder 优势明显 |
| CPU 利用率 | 高（自旋重试） | 低（减少竞争） | LongAdder 更节能 |
| `sum()` 开销 | O(1) | O(N)（遍历 cell 数组） | AtomicLong 更快 |
| 内存占用 | 小（单个 long） | 大（Cell 数组 + 填充） | 以空间换时间 |

### 7.3 选型建议

```
选择 AtomicLong 的场景：
  ✓ 需要强一致性的精确值
  ✓ 低竞争、少线程场景
  ✓ 频繁读取（sum 操作），少写入
  ✓ 内存敏感的场景

选择 LongAdder 的场景：
  ✓ 高并发、多线程累加（如统计 QPS、总耗时）
  ✓ 写入远多于读取
  ✓ 对"实时精确值"不敏感
  ✓ 追求极致吞吐量
```

### 7.4 基准测试代码

```java
@BenchmarkMode(Mode.Throughput)
@Fork(1)
@Warmup(iterations = 3)
@Measurement(iterations = 5)
public class AtomicBenchmark {

    private AtomicLong atomicLong = new AtomicLong(0);
    private LongAdder longAdder = new LongAdder();

    @Benchmark
    public void testAtomicLong() {
        atomicLong.incrementAndGet();
    }

    @Benchmark
    public void testLongAdder() {
        longAdder.increment();
    }
}
```

---

## 八、Unsafe 类简述

### 8.1 什么是 Unsafe

`sun.misc.Unsafe` 是 Java 提供的一个**非标准、非安全**的工具类，提供了直接内存操作、CAS、线程调度等底层能力。`java.util.concurrent` 中的原子类几乎全部基于 Unsafe 实现。

```
┌─────────────────────────────────────────────────────────┐
│              Unsafe 能力图谱                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐    │
│  │ CAS 操作     │  │ 内存操作     │  │ 线程调度      │    │
│  │             │  │             │  │              │    │
│  │ compareAnd  │  │ allocate    │  │ park /       │    │
│  │ SwapInt     │  │ memory      │  │ unpark       │    │
│  │ compareAnd  │  │ freeMemory  │  │              │    │
│  │ SwapLong    │  │ copyMemory  │  │ monitorEnter │    │
│  │ compareAnd  │  │ getAddress  │  │ monitorExit  │    │
│  │ SwapObject  │  │ putAddress  │  │              │    │
│  └─────────────┘  └─────────────┘  └──────────────┘    │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐    │
│  │ 字段偏移量   │  │ 数组操作     │  │ 类操作       │    │
│  │             │  │             │  │              │    │
│  │ objectField │  │ arrayBase   │  │ staticField  │    │
│  │ Offset      │  │ Offset      │  │ Offset       │    │
│  │ objectField │  │ arrayIndex  │  │ ensureClass  │    │
│  │ Size        │  │ Scale       │  │ Initialized  │    │
│  └─────────────┘  └─────────────┘  └──────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 8.2 获取 Unsafe 实例

由于 Unsafe 是受保护的，不能直接通过构造函数获取：

```java
// 通过反射获取 Unsafe 实例
public static Unsafe getUnsafe() throws Exception {
    Field field = Unsafe.class.getDeclaredField("theUnsafe");
    field.setAccessible(true);
    return (Unsafe) field.get(null);
}
```

### 8.3 Unsafe 核心 API 示例

```java
Unsafe unsafe = getUnsafe();

// --- CAS 操作 ---
// 对对象 obj 的偏移量为 offset 的 int 字段做 CAS
boolean ok = unsafe.compareAndSwapInt(obj, offset, expectedValue, newValue);

// --- 内存操作 ---
// 分配堆外内存
long address = unsafe.allocateMemory(1024);

// 直接写入内存
unsafe.putLong(address, 12345L);

// 读取内存
long value = unsafe.getLong(address);

// 释放内存
unsafe.freeMemory(address);

// --- 字段偏移量 ---
// 获取字段在对象内存布局中的偏移量（用于 CAS 定位字段）
Field valueField = AtomicInteger.class.getDeclaredField("value");
long valueOffset = unsafe.objectFieldOffset(valueField);

// --- 线程挂起 / 唤醒 ---
unsafe.park(false, 0L);      // 挂起当前线程
unsafe.unpark(thread);       // 唤醒指定线程
```

### 8.4 Unsafe 在 AtomicInteger 中的使用

```java
public class AtomicInteger extends Number {

    // 通过 Unsafe 获取 value 字段的内存偏移量
    private static final Unsafe unsafe = Unsafe.getUnsafe();
    private static final long valueOffset;

    static {
        try {
            valueOffset = unsafe.objectFieldOffset(
                AtomicInteger.class.getDeclaredField("value")
            );
        } catch (NoSuchFieldException e) {
            throw new Error(e);
        }
    }

    // value 用 volatile 修饰，保证可见性
    private volatile int value;

    public final int getAndIncrement() {
        // 在偏移量 valueOffset 处做原子 +1 操作
        return unsafe.getAndAddInt(this, valueOffset, 1);
    }
}
```

### 8.5 Java 9+ 的 VarHandle

Java 9 引入了 `VarHandle` 作为 Unsafe 的安全替代方案：

```java
// Java 9+ 使用 VarHandle 代替 Unsafe
class MyCounter {
    private volatile int value;

    // 通过 MethodHandles 获取 VarHandle
    private static final VarHandle VALUE;

    static {
        try {
            VALUE = MethodHandles.lookup()
                .findVarHandle(MyCounter.class, "value", int.class);
        } catch (Exception e) {
            throw new Error(e);
        }
    }

    public void increment() {
        VALUE.getAndAdd(this, 1);
    }
}
```

### 8.6 Unsafe 使用风险

| 风险 | 说明 |
|------|------|
| 非公开 API | `Unsafe` 不属于标准 API，未来版本可能移除 |
| 内存安全 | 直接操作内存可能导致越界、内存泄漏 |
| 模块限制 | Java 9+ 的模块系统默认禁止访问 `sun.misc` 包 |
| JVM 安全 | 绕过 JVM 安全检查可能导致虚拟机崩溃 |
| 调试困难 | 直接内存操作产生的 bug 难以定位和复现 |

> **建议**：业务代码中应尽量避免直接使用 Unsafe。优先使用 `java.util.concurrent.atomic` 包中的高级封装。Unsafe 仅适用于框架和基础设施的开发。

---

## 附录：原子类速查表

| 类别 | 类名 | 数据类型 | 核心用途 |
|------|------|---------|---------|
| 基本类型 | AtomicInteger | int | 原子整数操作 |
| 基本类型 | AtomicLong | long | 原子长整数操作 |
| 基本类型 | AtomicBoolean | boolean | 原子布尔操作 |
| 基本类型 | AtomicReference\<V\> | 引用 | 原子引用操作 |
| 数组类型 | AtomicIntegerArray | int[] | 原子整型数组 |
| 数组类型 | AtomicLongArray | long[] | 原子长整型数组 |
| 数组类型 | AtomicReferenceArray\<E\> | E[] | 原子引用数组 |
| 字段更新器 | AtomicIntegerFieldUpdater | int 字段 | 原子更新已有类的字段 |
| 字段更新器 | AtomicLongFieldUpdater | long 字段 | 同上 |
| 字段更新器 | AtomicReferenceFieldUpdater | 引用字段 | 同上 |
| ABA 解决 | AtomicStampedReference | 引用 + 版本号 | 带版本号的原子引用 |
| ABA 解决 | AtomicMarkableReference | 引用 + 标记 | 带布尔标记的原子引用 |
| 累加器 | LongAdder | long | 高并发累加（推荐） |
| 累加器 | LongAccumulator | long | 自定义累加函数 |
| 累加器 | DoubleAdder | double | 高并发 double 累加 |
| 累加器 | DoubleAccumulator | double | 自定义 double 累加 |

---

← [返回 Java 并发编程专题导航](../README.md)
