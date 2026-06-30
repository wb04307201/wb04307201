<!--
question:
  id: 01.java-volatile
  topic: 01.java
  difficulty: 未标
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [01.java, volatile]
-->

# volatile 内存语义深度剖析

## 引子：一个诡异的死循环

```java
class Task {
    static boolean running = true;
    
    public static void main(String[] args) throws Exception {
        new Thread(() -> {
            while (running) {
                // do something
            }
            System.out.println("线程结束");
        }).start();
        
        Thread.sleep(1000);
        running = false;  // 主线程修改为 false
        System.out.println("已设置 running = false");
    }
}
```

预期：线程应该打印"线程结束"并退出。

实际：**线程永远不会结束！** 陷入死循环。

为什么？因为新线程一直在用**自己缓存里的旧值**，看不到主线程的修改。加上 `volatile` 就能解决——

---

## 一、核心原理

> 📚 **前置知识**：[volatile](../../../01.java/concurrency/volatile/README.md) | [JMM](../../../01.java/concurrency/jmm/README.md)

### 1.1 JMM 基础

Java 内存模型定义线程与主内存的关系：所有变量存于**主内存**（共享），每个线程拥有**工作内存**（私有副本）。线程对变量的操作必须在工作内存中进行，不能直接读写主内存。

```
┌──────────────────────────────┐
│       主内存（Main Memory）     │
│  var A │ var B │ var C       │
└──────────────────────────────┘
     ▲         ▲         ▲
     │ load    │ load    │ load
     ▼         ▼         ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│线程1副本 │ │线程2副本 │ │线程3副本 │
│  var A' │ │  var A' │ │  var B' │
└─────────┘ └─────────┘ └─────────┘
```

无 volatile 时，线程修改自己的副本后，其他线程可能永远看不到这个修改。

### 1.2 volatile 的两大语义

#### （1）可见性（Visibility）

线程修改 volatile 变量时，JVM 立即将值**刷新到主内存**；其他线程读取时，强制**从主内存重新加载**。底层通过 **MESI 缓存一致性协议** 或 **Lock# 前缀指令**实现：写 volatile 时，处理器使其他 CPU 缓存行失效。

#### （2）有序性（Ordering）

volatile 通过**内存屏障**禁止指令重排序。JMM 将内存屏障分为四类：

| 屏障类型 | 指令示例 | 作用 |
|----------|----------|------|
| LoadLoad | `Load1; LoadLoad; Load2` | 确保 Load1 先于 Load2 及后续读 |
| StoreStore | `Store1; StoreStore; Store2` | 确保 Store1 刷主内存先于 Store2 |
| LoadStore | `Load1; LoadStore; Store2` | 确保 Load1 先于 Store2 及后续写 |
| StoreLoad | `Store1; StoreLoad; Load2` | 确保 Store1 刷主内存先于 Load2 |

**volatile 读的屏障策略：** 插入 `LoadLoad + LoadStore` 屏障，保证后续读写不被重排到 volatile 读之前。

**volatile 写的屏障策略：** 插入 `StoreStore + StoreLoad` 屏障，保证之前的写已刷主内存，且后续读能读到最新值（StoreLoad 开销最大）。

### 1.3 happens-before 规则

关键规则：**volatile 写 happens-before volatile 读**，结合传递性形成链式关系。

```mermaid
graph LR
    A[线程1: 写入 volatile var = 1] -->|happens-before| B[线程2: 读取 volatile var]
    B -->|happens-before| C[线程2: 读取普通变量 x]
    A -->|传递性| C
    style A fill:#ff6b6b
    style B fill:#4ecdc4
    style C fill:#c7f464
```

线程1 写 volatile 后，线程2 读该变量，可安全读取线程1 在写 volatile 之前写入的普通变量。

---

## 二、代码示例

### 2.1 DCL 单例为什么必须 volatile

双重检查锁定（DCL）缺少 volatile 会导致**半初始化问题**：

```java
public class Singleton {
    private static Singleton instance; // ❌ 缺少 volatile

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton(); // ⚠️ 非原子操作！
                }
            }
        }
        return instance;
    }
}
```

`new Singleton()` 分三步：
```
1. allocate()              // 分配内存
2. ctorInstance(memory)    // 初始化对象
3. instance = memory       // 指向内存地址
```

无 volatile 时，步骤 2 和 3 可能重排为 1→3→2，导致其他线程看到未初始化的对象。

**正确写法：**

```java
public class Singleton {
    private static volatile Singleton instance; // ✅ 禁止重排

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton(); // 保证 1→2→3 顺序
                }
            }
        }
        return instance;
    }
}
```

volatile 保证：(1) 禁止指令重排，确保三步按序执行；(2) 保证可见性，初始化完成后其他线程立即看到。

### 2.2 volatile i++ 为什么不安全

```java
public class VolatileCounter {
    private volatile int count = 0;
    public void increment() { count++; } // ❌ 不安全！
}
```

`count++` 包含三步：
```
1. READ:   temp = count      // 从主内存读取
2. MODIFY: temp = temp + 1   // 工作内存计算
3. WRITE:  count = temp      // 写回主内存
```

volatile 只保证第1步读最新、第3步写后可见，但**三步之间无原子性**。竞态演示：

```
时间线  线程A                  线程B
───────────────────────────────────────
t1     READ count → 0
t2                          READ count → 0  （旧值）
t3     MODIFY 0+1 → 1
t4                          MODIFY 0+1 → 1
t5     WRITE count = 1
t6                          WRITE count = 1  （丢失一次递增）
```

**正确做法：** 使用 `AtomicInteger`（CAS）或 `synchronized`。

```java
// ✅ 方案1：AtomicInteger
private AtomicInteger count = new AtomicInteger(0);
public void increment() { count.incrementAndGet(); }

// ✅ 方案2：synchronized
private int count = 0;
public synchronized void increment() { count++; }
```

---

## 三、常见陷阱

### 3.1 volatile 不保证原子性

volatile 只保证可见性和有序性，**不保证**复合操作（如 `i++`、check-then-act）的原子性。

```java
// ❌ 错误：volatile 不能保证计数器线程安全
private volatile int counter = 0;
for (int i = 0; i < 10000; i++) {
    new Thread(() -> counter++).start();
}
// 最终 counter 大概率 < 10000
```

### 3.2 volatile vs synchronized

| 对比维度 | volatile | synchronized |
|----------|----------|--------------|
| 可见性 | ✅ | ✅ |
| 有序性 | ✅（内存屏障） | ✅（串行化） |
| 原子性 | ❌ | ✅（互斥锁） |
| 阻塞 | ❌ | ✅ |
| 性能 | 轻量级（CPU 级） | 重量级（OS 级） |
| 适用场景 | 状态标志、DCL 单例 | 复合操作、临界区 |

**本质区别：** volatile 是字段级同步（硬件屏障），synchronized 是代码块/方法级同步（Monitor 锁）。

### 3.3 多变量不变量无法用 volatile 保护

```java
// ❌ 错误：volatile 无法保证 x,y 的关联一致性
private volatile int x = 0, y = 0;
public void set(int newX, int newY) { x = newX; y = newY; }
public boolean check() { return x == y; } // 可能读到中间状态
```

---

## 四、最佳实践

### 4.1 使用条件（需同时满足）

1. 单一变量读写（不涉及多变量关联）
2. 写操作不依赖当前值（或仅单线程写）
3. 不需要与其他操作组成原子复合操作

**典型场景：**

```java
// ✅ 场景1：状态标志位
private volatile boolean running = true;
public void stop() { running = false; }
public void run() { while (running) { doWork(); } }

// ✅ 场景2：DCL 单例
private static volatile Singleton instance;

// ✅ 场景3：独立观察结果
private volatile String lastResponse;
```

### 4.2 DCL 正确写法

```java
public class DoubleCheckedLocking {
    private static volatile DoubleCheckedLocking instance;
    private DoubleCheckedLocking() {}

    public static DoubleCheckedLocking getInstance() {
        if (instance == null) {              // 第一次检查：无锁快速路径
            synchronized (DoubleCheckedLocking.class) {
                if (instance == null) {      // 第二次检查：防重复创建
                    instance = new DoubleCheckedLocking();
                }
            }
        }
        return instance;
    }
}
```

要点：volatile 不可省略，两次检查都不可省略，锁必须是 Class 对象。

### 4.3 状态标志位模式

```java
public class Worker implements Runnable {
    private volatile boolean stopped = false;

    @Override
    public void run() {
        while (!stopped) { processTask(); }
        cleanup();
    }

    public void shutdown() { stopped = true; }
}
```

相比 `Thread.interrupt()`，这种方式更优雅、更可预测。

### 4.4 AtomicInteger 底层

```java
public class AtomicInteger {
    private volatile int value; // volatile 保证可见性

    public final int incrementAndGet() {
        for (;;) {
            int current = get();
            int next = current + 1;
            if (compareAndSet(current, next)) return next;
        }
    }
}
```

结合 volatile（可见性）+ CAS（原子性）实现无锁并发。

---

## 五、面试话术（30 秒版）

> "volatile 保证**可见性**和**有序性**，但**不保证原子性**。
>
> **可见性**：修改后立即刷主内存，其他线程读时强制重载，底层通过 MESI 协议或 Lock 指令实现。
>
> **有序性**：通过内存屏障禁止重排。volatile 读插 LoadLoad+LoadStore，写插 StoreStore+StoreLoad。
>
> 典型场景：**状态标志位**（volatile boolean 控制线程退出）和 **DCL 单例**（防止 new 的重排导致半初始化）。
>
> 注意：`i++` 这种 read-modify-write 需用 `AtomicInteger` 或 `synchronized`。"

---

## 六、交叉引用

- 主模块：[`01.java`](../../../01.java/) — Java 知识体系
- [synchronized](../../../01.java/concurrency/synchronized/README.md) — synchronized 内存语义与锁升级
- [并发工具类](../../../01.java/concurrency/utilities/README.md) — java.util.concurrent 包详解
- [JMM](../../../01.java/concurrency/jmm/README.md) — Java 内存模型与 happens-before 规则
- [CAS 与原子类](../../../01.java/concurrency/atomic/README.md) — AtomicInteger 与 CAS 乐观锁

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容
