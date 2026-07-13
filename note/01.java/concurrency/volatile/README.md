<!--
module:
  parent: java
  slug: java/volatile
  type: article
  category: 主模块子文章
  summary: volatile 关键字深度解析
-->

# volatile 关键字深度解析

## 一、volatile 的两大核心作用

### 1.1 保证可见性（Visibility）

当一个线程修改了 volatile 修饰的变量后，新值会**立即**刷新到主内存中。其他线程在读取该变量时，会强制从主内存重新加载，从而保证所有线程看到的都是最新值。

```java
public class VisibilityDemo {
    // 不用 volatile：线程可能永远看不到 flag 被修改
    private volatile boolean flag = false;

    public void writer() {
        flag = true; // 写入后立刻对其他线程可见
    }

    public void reader() {
        while (!flag) {
            // 如果没有 volatile，这里可能永远循环
        }
        System.out.println("flag 已被修改");
    }
}
```

> **对比场景**：没有 volatile 时，JIT 可能将 `flag` 缓存到寄存器中，导致 `reader()` 陷入死循环。

### 1.2 禁止指令重排序（Ordering）

编译器和处理器为了优化性能，会对指令进行重排序。volatile 通过**内存屏障**禁止特定类型的重排序，保证有序性。

```java
// 没有 volatile 时可能的执行顺序
int a = 1;      // 语句1
int b = 2;      // 语句2
volatile int v = 3; // 语句3
int c = 4;      // 语句4
int d = 5;      // 语句5

// 编译/处理器可能重排为：
int b = 2;      // 语句2 ↑ 可以排到 volatile 前
int a = 1;      // 语句1 ↑ 可以排到 volatile 前
volatile int v = 3; // 语句3 —— 内存屏障位置
int d = 5;      // 语句5 ↓ 可以排到 volatile 后
int c = 4;      // 语句4 ↓ 可以排到 volatile 后
```

**核心规则**：

| 屏障类型 | 限制 |
|----------|------|
| volatile 写之前 | 之前的读/写不能重排到写之后 |
| volatile 写之后 | 之后的读/写不能重排到写之前 |
| volatile 读之前 | 之前的读/写不能重排到读之后 |
| volatile 读之后 | 之后的读/写不能重排到读之前 |

简单记忆：volatile 写 = "上面不准下来"，volatile 读 = "下面不准上去"。

---
---

## 二、happens-before 规则

happens-before 是 JMM 中定义可见性的核心规则。如果操作 A happens-before 操作 B，那么 A 的结果对 B 可见。

### 2.1 八大规则

| 序号 | 规则 | 说明 |
|------|------|------|
| 1 | 程序次序规则 | 单线程中，书写在前的操作 happens-before 书写在后的操作 |
| 2 | 管程锁定规则 | 一个 unlock 操作 happens-before 后面对同一个 lock 的加锁操作 |
| 3 | **volatile 变量规则** | 对 volatile 变量的写操作 happens-before 后续对该变量的读操作 |
| 4 | 线程启动规则 | Thread.start() happens-before 该线程的每个动作 |
| 5 | 线程终止规则 | 线程的所有操作 happens-before Thread.join() 返回 |
| 6 | 线程中断规则 | Thread.interrupt() happens-before 被中断线程检测到中断 |
| 7 | 对象终结规则 | 对象的初始化 happens-before finalize() 调用 |
| 8 | 传递性 | A happens-before B，B happens-before C，则 A happens-before C |

### 2.2 volatile 的 happens-before 示例

```java
class HBExample {
    int a = 0;
    volatile boolean flag = false;

    // 线程 A 执行
    public void writer() {
        a = 42;          // 操作 1
        flag = true;     // 操作 2（volatile 写）
    }

    // 线程 B 执行
    public void reader() {
        if (flag) {      // 操作 3（volatile 读）
            System.out.println(a); // 操作 4 — 一定输出 42
        }
    }
}
```

**推导链**：
- 操作 1 happens-before 操作 2（程序次序规则）
- 操作 2 happens-before 操作 3（volatile 变量规则）
- 操作 3 happens-before 操作 4（程序次序规则）
- 由传递性：操作 1 happens-before 操作 4，所以 `a` 一定为 42

---

## 三、JMM 工作内存 vs 主内存

Java 内存模型（Java Memory Model）规定了所有变量都存储在**主内存**中，每个线程有自己的**工作内存**。

### 3.1 内存结构 ASCII 图

```
┌──────────────────────────────────────────────────────┐
│                      主 内 存                          │
│   (Main Memory: 堆、方法区 — 所有线程共享)               │
│                                                      │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│   │ var x=10 │  │ var y=20 │  │ var z=30 │           │
│   └──────────┘  └──────────┘  └──────────┘           │
│                                                      │
└──────┬──────────────┬──────────────┬─────────────────┘
       │  read/write  │  read/write  │  read/write
       ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐
│  线程 A 工作   ││  线程 B 工作  ││  线程 C 工作  │
│   内存        ││   内存       ││   内存       │
│              ││              ││              │
│  x_copy=10  ││  x_copy=10  ││  z_copy=30  │
│  y_copy=20  ││              ││              │
│              ││  y_copy=20  ││              │
└──────────────┘└──────────────┘└──────────────┘
```

### 3.2 内存交互八种操作

| 操作 | 说明 | 归属 |
|------|------|------|
| lock | 将主内存变量标识为线程独占 | 主内存 |
| unlock | 释放主内存变量的独占状态 | 主内存 |
| read | 将主内存变量值传输到工作内存 | 主内存→工作内存 |
| load | 将 read 的值放入工作内存副本 | 工作内存 |
| use | 将工作内存变量传给执行引擎 | 工作内存 |
| assign | 将执行引擎结果赋给工作内存变量 | 工作内存 |
| store | 将工作内存变量传输到主内存 | 工作内存→主内存 |
| write | 将 store 的值写入主内存变量 | 主内存 |

### 3.3 volatile 在 JMM 中的特殊行为

```
volatile 写流程:                     volatile 读流程:
工作内存 ──assign──> store ──>       ┌──> load <── read ── 主内存
                       write ───>    │     (强制刷新)
                       主内存         │
                      (立即刷新)     └──> use ──> 执行引擎
```

普通变量可能延迟刷新，而 volatile 变量**强制**每次写都立刻 store+write 到主内存，每次读都强制 load+read 从主内存。

---

## 四、volatile 不能保证原子性

### 4.1 i++ 问题详解

```java
public class AtomicityDemo {
    private volatile int counter = 0;

    public void increment() {
        counter++; // 看似一行代码，实际是三步操作
    }
}
```

`counter++` 的三步分解：

```
步骤 1: read    — 从主内存读取 counter 的值
步骤 2: assign  — 工作内存中 +1
步骤 3: write   — 写回主内存
```

### 4.2 并发丢失场景

```
线程 A                      主内存                      线程 B
─────────────────────────────────────────────────────────────────
read counter = 0 ──>
                                counter = 0
                                         <── read counter = 0
assign: 0+1 = 1 ──>
assign: 0+1 = 1 ──>
write counter = 1 ──>
                                counter = 1
                                         <── write counter = 1
                                counter = 1  ❌ 期望 2，实际 1
```

**两次 +1 只加了 1**，因为 read 操作在 assign 之前就已经完成了，两个线程读到的是同一个旧值。

### 4.3 解决方案

| 方案 | 代码示例 | 适用场景 |
|------|----------|----------|
| synchronized | `synchronized(this) { counter++; }` | 简单场景 |
| AtomicInteger | `new AtomicInteger().incrementAndGet()` | 高并发计数器 |
| LongAdder | `new LongAdder().increment()` | 超高并发、多核 |
| ReentrantLock | `lock.lock(); try { counter++; } finally { lock.unlock(); }` | 需灵活锁控制 |

---

## 五、volatile 的底层原理：内存屏障

### 5.1 四种内存屏障

JMM 通过插入**内存屏障**（Memory Barrier / Memory Fence）来实现 volatile 语义：

| 屏障类型 | 英文全称 | 作用 |
|----------|----------|------|
| **LoadLoad** | Load-Load Barrier | 确保 Load1 的数据加载先于 Load2 及后续所有 load |
| **StoreStore** | Store-Store Barrier | 确保 Store1 的数据写入先于 Store2 及后续所有 store |
| **LoadStore** | Load-Store Barrier | 确保 Load1 的数据加载先于 Store2 及后续所有 store |
| **StoreLoad** | Store-Load Barrier | 确保 Store1 的数据写入先于 Load2 及后续所有 load |

### 5.2 屏障插入策略

```
          volatile 写操作的屏障插入

  普通读/写           volatile 写           普通读/写
     ↓                    ↓                    ↓
  ┌──────┐          ┌──────────┐          ┌──────┐
  │      │ ──►      │  Store   │ ──►      │      │
  │      │          │  Store   │          │      │
  │      │          │  StoreLoad│          │      │
  └──────┘          └──────────┘          └──────┘
     │                    │                    │
     │      StoreStore    │      StoreLoad     │
     │◄───────────────────┤                    │
     │                    │◄───────────────────┤
     │                    │                    │
```

```
          volatile 读操作的屏障插入

  普通读/写           volatile 读           普通读/写
     ↓                    ↓                    ↓
  ┌──────┐          ┌──────────┐          ┌──────┐
  │      │ ──►      │   Load   │ ──►      │      │
  │      │          │  LoadLoad│          │      │
  │      │          │  LoadStore│         │      │
  └──────┘          └──────────┘          └──────┘
     │                    │                    │
     │                    │────► LoadLoad      │
     │                    │                    │
     │                    │────► LoadStore     │
     │                    │                    │
```

### 5.3 各平台的具体实现

| 平台 | StoreLoad 实现 | 其他屏障 |
|------|----------------|----------|
| x86 | `lock` 前缀指令（如 `lock addl $0, (%rsp)`） | x86 自身不允许 StoreLoad 重排，其他屏障为空 |
| ARM | `dmb`（Data Memory Barrier） | ARM 弱内存模型，所有屏障都有实际指令 |
| PowerPC | `sync` / `lwsync` | 弱内存模型，需要显式屏障 |

```assembly
; x86 下 volatile 写的典型实现
mov    [rax], 1        ; 写入值
lock addl $0, (%rsp)   ; StoreLoad 屏障，强制刷出写缓冲
```

`lock` 前缀指令的效果：
1. 将当前处理器缓存行的数据**立即写回主内存**
2. 使其他处理器中对应缓存行**失效**（通过 MESI 协议）
3. 相当于一个**全局内存屏障**

---

## 六、volatile 与 synchronized 对比

### 6.1 全面对比表

| 对比维度 | volatile | synchronized |
|----------|----------|--------------|
| **本质** | 变量修饰符 | 代码块/方法修饰符 |
| **可见性** | 保证 | 保证（unlock 前刷新到主内存） |
| **原子性** | 不保证 | 保证（互斥排他） |
| **有序性** | 禁止重排 | 串行化执行，天然有序 |
| **阻塞** | 不会阻塞线程 | 获取不到锁时阻塞 |
| **性能** | 轻量（无上下文切换） | 较重（涉及锁竞争、上下文切换） |
| **适用场景** | 状态标志、DCL 单例 | 复合操作、临界区保护 |
| **底层实现** | 内存屏障 | Monitor 对象 + CAS/阻塞队列 |

### 6.2 选择指南

```
                   是否只有单一变量读写？
                    /                   \
                  是                     否
                  /                       \
         是否需要原子操作？            用 synchronized
          /            \                或 Lock
       是               否
       /                 \
  AtomicInteger    volatile
  LongAdder
```

### 6.3 代码对比

```java
// volatile：仅适合单一状态标志
volatile boolean running = true;
while (running) { /* ... */ }

// synchronized：适合复合操作
private int balance = 0;
public synchronized void transfer(int amount) {
    if (balance >= amount) {
        balance -= amount;
    }
}
// 这里必须用 synchronized，因为判断和修改是复合操作
```

---

## 七、DCL（双重检查锁定）单例中的 volatile

### 7.1 为什么需要 volatile

```java
// ❌ 错误写法 — 没有 volatile
public class Singleton {
    private static Singleton instance; // 缺少 volatile！

    public static Singleton getInstance() {
        if (instance == null) {                  // 第一次检查（无锁）
            synchronized (Singleton.class) {
                if (instance == null) {          // 第二次检查（有锁）
                    instance = new Singleton();  // 问题所在！
                }
            }
        }
        return instance;
    }
}
```

**问题分析**：`new Singleton()` 并非原子操作，包含三步：

```
1. 分配内存空间
2. 调用构造方法初始化对象
3. 将引用指向分配的内存
```

没有 volatile 时，步骤 2 和 3 可能被重排序：

```
正常顺序:                        重排序后:
1. 分配内存                      1. 分配内存
2. 初始化对象                    3. 引用指向内存 (instance != null)
3. 引用指向内存 ← instance != null  2. 初始化对象 ← 还没执行！

线程 B 看到 instance != null，直接返回了未初始化完成的对象！
```

### 7.2 正确写法

```java
// ✅ 正确写法 — 加上 volatile
public class Singleton {
    private static volatile Singleton instance;

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

加上 volatile 后，写操作前后都插入了内存屏障，禁止了步骤 2、3 的重排序，保证对象完全初始化后才对其他线程可见。

### 7.3 其他单例实现方式

```java
// 方式一：静态内部类（推荐）— 利用类加载机制保证线程安全
public class Singleton {
    private Singleton() {}

    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}

// 方式二：枚举（最安全，防反射和序列化攻击）
public enum Singleton {
    INSTANCE;
}

// 方式三：饿汉式（简单但浪费资源）
public class Singleton {
    private static final Singleton INSTANCE = new Singleton();
    public static Singleton getInstance() { return INSTANCE; }
}
```

---

## 八、MESI 缓存一致性协议

### 8.1 多核 CPU 缓存架构

```
┌─────────────────────────────────────────────────────────┐
│                        主 内 存                           │
│                   (Main Memory / DRAM)                    │
└────────┬──────────────┬──────────────┬──────────────────┘
         │              │              │
    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
    │  CPU 0  │    │  CPU 1  │    │  CPU 2  │
    │ L1 Cache│    │ L1 Cache│    │ L1 Cache│
    │ L2 Cache│    │ L2 Cache│    │ L2 Cache│
    └─────────┘    └─────────┘    └─────────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
              ┌─────────┴─────────┐
              │  总线 / 互连网络    │
              │ (Bus / Interconnect)│
              └───────────────────┘
```

每个 CPU 有自己的缓存，同一个变量可能被多个 CPU 缓存，如果不做协调就会出现数据不一致。

### 8.2 MESI 四种状态

| 状态 | 英文全称 | 含义 | 可否修改 | 其他核是否有副本 |
|------|----------|------|----------|-----------------|
| **M** | Modified（已修改） | 缓存行数据已被修改，与主内存不一致 | 可以 | 无（独占） |
| **E** | Exclusive（独占） | 缓存行数据与主内存一致，仅本核缓存 | 可以 | 无（独占） |
| **S** | Shared（共享） | 缓存行数据与主内存一致，多个核都有缓存 | 不可 | 有 |
| **I** | Invalid（无效） | 缓存行数据无效，不能使用 | 不可 | 不确定 |

### 8.3 状态转换

```
                    本地写
          ┌─────────────────────┐
          │                     │
          ▼                     │
        ┌───┐    远程读     ┌───┐
        │ E │────────────►│ S │
        └───┘◄────────────└───┘
          │      失效响应     │
          │                   │
          ▼                   ▼
        ┌───┐              ┌───┐
        │ M │              │ I │
        └───┘              └───┘
          │                   ▲
          │ 刷新到内存          │
          └───────────────────┘
             其他核写(发送Invalid)
```

**完整状态转换表**：

| 当前状态 | 事件 | 新状态 | 说明 |
|----------|------|--------|------|
| I | 本地读（缓存未命中） | E/M | 从内存加载，若其他核无副本则为 E |
| I | 本地读（缓存命中） | S | 从内存加载，其他核有副本 |
| E | 本地写 | M | 直接修改，无需通知 |
| S | 本地写 | M | 先发送 Invalid 使其他核失效，再修改 |
| M | 本地读/写 | M | 直接操作 |
| 任何 | 收到其他核的读 | S/I | 若为 M 则先写回内存 |
| 任何 | 收到其他核的 Invalid | I | 标记为无效 |

### 8.4 MESI 与 volatile 的关系

volatile 写对应的 `lock` 前缀指令会：
1. 强制将当前核的缓存行写回主内存
2. 通过 MESI 协议发送 Invalid 消息使其他核的对应缓存行失效
3. 其他核下次读取时被迫从主内存重新加载

这就是 volatile 实现**可见性**的硬件基础。

```
volatile 写 → lock 指令 → 刷回主内存 + 发送 Invalid
                                            │
                    ┌───────────────────────┤
                    ▼                       ▼
              CPU 1 Cache Line          CPU 2 Cache Line
              State: M → I              State: S → I
              (失效)                    (失效)
                    │                       │
                    ▼                       ▼
              下次读取时从主内存重新加载 ← 保证可见性
```

---

## 九、总结与最佳实践

### 9.1 volatile 使用 checklist

- [ ] 仅用于单一变量读写，不用于复合操作
- [ ] 状态标志、中断信号等场景优先考虑
- [ ] DCL 单例的 instance 必须加 volatile
- [ ] 不替代 synchronized 用于需要原子性的场景
- [ ] 理解 happens-before 规则，正确推导可见性

### 9.2 常见误区

| 误区 | 正确认知 |
|------|----------|
| volatile 能保证线程安全 | 仅保证可见性和有序性，不保证原子性 |
| volatile 比 synchronized 快就一定更好 | 适用场景不同，不能简单替换 |
| volatile 变量不需要加锁 | 如果涉及复合操作，仍需加锁 |
| volatile 适合计数器 | 计数器应该用 AtomicInteger |

### 9.3 一句话总结

> **volatile 是轻量级的同步机制，保证可见性和有序性，但不保证原子性。底层通过内存屏障和 MESI 协议实现，是理解 Java 并发编程的基石。**

---

## 🔗 配套章节

- 🆕 [volatile 内存语义（咬文嚼字 · 13.split-hairs）](../../../../13.split-hairs/01.java/volatile/README.md) —— 面试速查版：引子「诡异死循环」+ JMM 基础 + 内存语义深度 + 经典反模式 + 90 秒话术
- [synchronized 内存语义与锁升级](../synchronized/README.md) —— 同章节的「锁」维度
- [JMM 与 happens-before 规则](../jmm/README.md) —— volatile 与 JMM 规则的对应
- [CAS 与原子类](../atomic/README.md) —— volatile 不足时的补救方案（AtomicInteger）

---

← [返回 Java 并发编程专题导航](../README.md)
