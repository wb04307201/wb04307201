<!--
module:
  parent: java
  slug: java/synchronized
  type: article
  category: 主模块子文章
  summary: synchronized 学习笔记
-->

## 一、synchronized 的三种用法

`synchronized` 是 Java 语言内置的互斥锁机制，由 JVM 在字节码层面通过 `monitorenter` / `monitorexit` 指令实现，保证同一时刻只有一个线程可以执行被保护的代码。

### 1.1 修饰实例方法

锁对象是**当前实例**（`this`）。同一对象的多线程调用该方法是互斥的，不同对象之间互不影响。

```java
public class Counter {
    private int count = 0;

    public synchronized void increment() {
        count++;
    }

    public synchronized int getCount() {
        return count;
    }
}
```

字节码特征：方法 `ACC_SYNCHRONIZED` 标志位被设置，JVM 识别后自动插入 `monitorenter` / `monitorexit`。

### 1.2 修饰静态方法

锁对象是**该类的 Class 对象**（`Counter.class`）。所有实例共享同一把锁。

```java
public class Counter {
    private static int total = 0;

    public static synchronized void incrementTotal() {
        total++;
    }
}
```

### 1.3 修饰代码块

锁对象是**括号中指定的引用**，最灵活的方式。

```java
public class Counter {
    private final Object lock = new Object();
    private int count = 0;

    public void increment() {
        synchronized (lock) {        // 指定锁对象
            count++;
        }
    }

    public void batchIncrement(int n) {
        synchronized (this) {         // 等价于修饰实例方法
            for (int i = 0; i < n; i++) {
                count++;
            }
        }
    }
}
```

字节码层面会显式生成 `monitorenter` / `monitorexit` 指令，即使发生异常也能保证锁释放。

---
---

## 二、锁升级完整过程

Java 6 引入锁升级机制，synchronized 从"重量级"变为"自适应"锁，性能大幅提升。

```
无锁 ──竞争出现──> 偏向锁 ──竞争加剧──> 轻量级锁 ──竞争持续──> 重量级锁
(Biasable)       (Biased)            (Lightweight)         (Heavyweight)
```

| 阶段 | 触发条件 | 实现方式 | 性能特征 |
|------|----------|----------|----------|
| 无锁 | 对象刚创建，无线程竞争 | Mark Word 记录哈希码等信息 | 最佳，无额外开销 |
| 偏向锁 | 只有一个线程访问 | Mark Word 记录线程 ID | 几乎无开销，仅 CAS 一次 |
| 轻量级锁 | 出现交替竞争（非同时） | CAS + 自旋 + Lock Record | 短时间自旋，不阻塞 |
| 重量级锁 | 自旋失败或竞争激烈 | OS Mutex（互斥量） | 线程阻塞/唤醒，开销最大 |

升级是**单向的**，不可逆。一旦升级为重量级锁，即使竞争消失也不会降级。

---

## 三、Mark Word 结构详解

Mark Word 是对象头的一部分，位于对象内存布局的最前端，占 64 位（64 位 JVM 开启指针压缩时）。它动态存储锁状态信息。

### 3.1 64 位 JVM 下 Mark Word 的五种布局

```
  ┌─────────────────────────────────────────────────────────────┐
  │                    64-bit Mark Word                         │
  ├──────────────────────────┬──────────┬───────┬───────────────┤
  │   状态位 (最后 2-3 位)    │  其余位   │       │               │
  └──────────────────────────┴──────────┴───────┴───────────────┘
```

| 锁状态 | 25bit | 31bit | 1bit | 2bit | 2bit | 1bit |
|--------|-------|-------|------|------|------|------|
| 无锁 | hashCode | 分代年龄 | 0 | 01 | 偏向锁=0 |
| 偏向锁 | 线程ID | Epoch | 分代年龄 | 1 | 01 | 偏向锁=1 |
| 轻量级锁 | 指向 Lock Record 的指针 | 00 |
| 重量级锁 | 指向 Monitor 的指针 | 10 |
| GC 标记 | (空) | 11 |

### 3.2 关键位说明

```
    无锁状态 (biased_lock = 0, lock = 01):
    ┌──────────────────────┬────────┬─┬──┬─┐
    │   unused (25 bits)   │ hash   │0 │01│0│  ← biased_lock=0, lock=01
    └──────────────────────┴────────┴─┴──┴─┘
             ↑                    ↑
         未使用区域            对象 hashCode

    偏向锁状态 (biased_lock = 1, lock = 01):
    ┌───────────┬───────┬────┬─┬──┬─┐
    │ ThreadID  │ Epoch │ age│1 │01│1│  ← biased_lock=1, lock=01
    └───────────┴───────┴────┴─┴──┴─┘
       ↑            ↑
    偏向线程      偏向时间戳

    轻量级锁状态 (lock = 00):
    ┌─────────────────────────────┬──┬─┐
    │  指向栈中 Lock Record 的指针 │00│ │
    └─────────────────────────────┴──┴─┘

    重量级锁状态 (lock = 10):
    ┌─────────────────────────────┬──┬─┐
    │  指向堆中 Monitor 的指针     │10│ │
    └─────────────────────────────┴──┴─┘
```

- **lock**（2 位）：00=轻量级，01=无锁/偏向，10=重量级，11=GC 标记
- **biased_lock**（1 位）：0=非偏向，1=偏向
- **分代年龄**（4 位）：对象在新生代存活的 GC 次数，最大 15
- **hashCode**（31 位）：`System.identityHashCode()` 的结果，调用后才写入

---

## 四、偏向锁的启用与取消

### 4.1 偏向锁原理

偏向锁的核心思想是"大多数情况下锁不存在竞争，且总是被同一线程获取"。

```
Thread-A 首次获取锁:
  1. CAS 将 Thread-A 的 ID 写入 Mark Word
  2. 获取成功，偏向 Thread-A

Thread-A 再次获取同一把锁:
  1. 检查 Mark Word 中的 Thread ID == 当前线程
  2. 匹配成功 → 直接获取，无需 CAS

Thread-B 尝试获取偏向锁:
  1. 检查发现偏向的不是自己
  2. 触发偏向撤销 (Revoke)
  3. 升级到轻量级锁或重量级锁
```

### 4.2 JVM 参数控制

| 参数 | 说明 | Java 8 | Java 15+ |
|------|------|--------|----------|
| `-XX:+UseBiasedLocking` | 启用偏向锁 | 默认开启 | **已移除** |
| `-XX:BiasedLockingStartupDelay=<N>` | 启动延迟（毫秒） | 默认 4000 | 已移除 |

```bash
# Java 8 中关闭偏向锁
java -XX:-UseBiasedLocking MyApp

# Java 8 中立即启用（跳过延迟）
java -XX:BiasedLockingStartupDelay=0 MyApp
```

### 4.3 Java 15 移除偏向锁 (JEP 374)

Java 15 通过 [JEP 374](https://openjdk.org/jeps/374) 将偏向锁设为 **始终禁用**，原因如下：

1. **代码复杂度**：偏向锁实现增加了 JVM 约 13% 的锁相关代码
2. **维护成本高**：与虚拟线程、值类型等新特性难以兼容
3. **实际收益有限**：现代并发场景中偏向锁命中率不高
4. **替代方案更好**：JUC 锁和后续虚拟线程提供更灵活的同步方式

从 Java 15 开始，`-XX:+UseBiasedLocking` 变为**废弃参数**，Java 22+ 中彻底移除该参数。

---

## 五、轻量级锁的 CAS 自旋

### 5.1 Lock Record 结构

当锁升级为轻量级锁时，JVM 在当前线程的栈帧中创建一个 **Lock Record**（锁记录）：

```
  ┌─────────────────────────────────────────┐
  │          Thread Stack Frame             │
  │  ┌───────────────────────────────────┐  │
  │  │       Lock Record (锁记录)        │  │
  │  │  ┌─────────────────────────────┐  │  │
  │  │  │ Displaced Mark Word         │  │  │  ← 保存原始 Mark Word
  │  │  ├─────────────────────────────┤  │  │
  │  │  │ 指向 Object 的指针 (owner)  │  │  │
  │  │  └─────────────────────────────┘  │  │
  │  └───────────────────────────────────┘  │
  └─────────────────────────────────────────┘
           │
           ▼  CAS 操作
  ┌─────────────────────────────────────────┐
  │              Heap Object                │
  │  ┌───────────────────────────────────┐  │
  │  │  Mark Word (lock=00)              │  │
  │  │  ┌─────────────────────────────┐  │  │
  │  │  │ 指向 Lock Record 的指针      │  │  │
  │  │  └─────────────────────────────┘  │  │
  │  └───────────────────────────────────┘  │
  └─────────────────────────────────────────┘
```

### 5.2 加锁/解锁过程

**加锁步骤：**

1. 判断对象是否处于无锁状态（`lock == 01`）
2. 如果是，在当前线程栈中分配 Lock Record
3. 将对象 Mark Word 复制到 Lock Record 的 Displaced Mark Word 中
4. 用 CAS 将对象 Mark Word 更新为指向 Lock Record 的指针
5. CAS 成功 → 获取轻量级锁；CAS 失败 → 进入自旋或膨胀

**解锁步骤：**

1. 用 CAS 将 Lock Record 中的 Displaced Mark Word 写回对象头
2. CAS 成功 → 解锁完成
3. CAS 失败 → 说明有其他线程竞争，升级为重量级锁

### 5.3 自旋与自适应自旋

```java
// 伪代码：轻量级锁的 CAS 自旋过程
while (!CAS(markWord, oldMarkWord, newMarkWord)) {
    if (spinCount++ > threshold) {
        // 自旋次数超过阈值，膨胀为重量级锁
        inflateToHeavyweightLock();
        break;
    }
    // 短暂自旋，忙等待
    Thread.onSpinWait();  // Java 9+ PAUSE 指令
}
```

自旋次数阈值由 JVM 自适应调整（`-XX:PreBlockSpin` 等参数），避免长时间无意义的 CPU 空转。

---

## 六、重量级锁的 OS Mutex

### 6.1 ObjectMonitor 结构

当自旋失败，锁膨胀为重量级锁，底层使用 **ObjectMonitor**（C++ 实现，基于 OS Mutex）。

```
  ObjectMonitor (C++ HotSpot 实现)
  ┌─────────────────────────────────────────┐
  │  _owner          : 持有锁的线程指针      │
  │  _WaitSet        : wait() 的线程队列     │
  │  _EntryList      : 阻塞等待的线程队列     │
  │  _count          : 重入计数              │
  │  _recursions     : 重入次数               │
  │  _cxq            : 竞争队列 (CAS Queue)  │
  │  _succ           : 下一个被唤醒的线程     │
  └─────────────────────────────────────────┘
```

### 6.2 线程进入流程

```
  线程尝试获取重量级锁
         │
         ▼
  ┌──────────────┐
  │ 锁是否空闲？   │────是──> 获取锁，_owner = 当前线程
  └──────────────┘
         │ 否
         ▼
  进入 _cxq 队列 (CAS 入队)
         │
         ▼
  park() → 线程阻塞 (OS 级别)
         │
         ▼
  前一个线程释放锁 → unpark() 唤醒下一个
```

### 6.3 为什么重量级锁开销大

| 操作 | 轻量级锁 | 重量级锁 |
|------|----------|----------|
| 加锁 | CAS（用户态） | Mutex 系统调用（内核态） |
| 阻塞 | 无（自旋） | park → 线程切换 |
| 唤醒 | 无 | unpark → 上下文切换 |
| 开销 | ~纳秒级 | ~微秒级（1000 倍差距） |

---

## 七、锁消除与锁粗化（JIT 优化）

### 7.1 锁消除 (Lock Elimination)

JIT 编译器通过**逃逸分析**（Escape Analysis）发现某些锁对象不会逃逸到方法外部，从而完全消除锁操作。

```java
public String concat(String a, String b) {
    // StringBuffer 内部使用 synchronized
    // 但 sb 是局部变量，不会逃逸 → JIT 消除锁
    StringBuffer sb = new StringBuffer();
    sb.append(a).append(b);
    return sb.toString();
}
```

开启逃逸分析：`-XX:+DoEscapeAnalysis`（默认开启）

### 7.2 锁粗化 (Lock Coarsening)

当 JIT 发现对同一对象的加锁/解锁操作频繁出现在连续代码中，会将多次加锁合并为一次。

```java
// 优化前：循环内反复加锁/解锁
public void demo() {
    for (int i = 0; i < 1000; i++) {
        synchronized (this) {   // 每次循环都加锁
            doSomething(i);
        }
    }
}

// 锁粗化后（JIT 自动完成）：
public void demo() {
    synchronized (this) {       // 只加一次锁
        for (int i = 0; i < 1000; i++) {
            doSomething(i);
        }
    }
}
```

### 7.3 JIT 优化对比

| 优化 | 触发条件 | 优化效果 | JVM 参数 |
|------|----------|----------|----------|
| 锁消除 | 对象不逃逸 | 完全移除锁操作 | `-XX:+DoEscapeAnalysis` |
| 锁粗化 | 连续加锁/解锁 | 减少锁操作次数 | `-XX:+OptimizeStringConcat` |
| 锁膨胀 | 自旋超时 | 保证正确性 | `-XX:PreBlockSpin` |

---

## 八、synchronized vs ReentrantLock 对比

| 维度 | synchronized | ReentrantLock |
|------|-------------|---------------|
| **实现层面** | JVM 关键字，字节码指令 | JDK 类（`java.util.concurrent`） |
| **锁获取** | 隐式（语言层面） | 显式（`lock()` / `unlock()`） |
| **可中断** | 不支持 | 支持（`lockInterruptibly()`） |
| **超时获取** | 不支持 | 支持（`tryLock(timeout)`） |
| **公平性** | 非公平 | 可选（构造参数） |
| **条件变量** | 单一 wait/notify | 多个 `Condition` |
| **可重入** | 是 | 是 |
| **性能 (Java 6+)** | 接近 ReentrantLock | 与 synchronized 差距极小 |
| **锁状态查询** | 不支持 | `isLocked()`, `getHoldCount()` |
| **代码安全性** | 自动释放，不易死锁 | 需 `try-finally` 手动释放 |
| **适用场景** | 一般同步需求 | 需要高级特性（可中断、超时、公平、多条件） |

### 使用建议

```java
// 简单场景优先用 synchronized —— 安全、简洁
synchronized (list) {
    list.add(item);
}

// 需要超时/可中断/公平锁时用 ReentrantLock
ReentrantLock lock = new ReentrantLock(true);  // 公平锁
if (lock.tryLock(3, TimeUnit.SECONDS)) {
    try {
        // 业务逻辑
    } finally {
        lock.unlock();  // 必须在 finally 中释放
    }
}
```

### 总结

- **日常开发**：优先使用 `synchronized`，代码更简洁且不会忘记释放锁
- **特殊需求**：需要超时等待、可中断、公平锁、多条件变量时选择 `ReentrantLock`
- **性能**：Java 6 之后两者性能差距微乎其微，不再成为选型的主要考量
- **趋势**：Java 21 虚拟线程（Project Loom）中，`synchronized` 的阻塞成本进一步降低
