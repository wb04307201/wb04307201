<!--
module:
  parent: java
  slug: java/java-locks
  type: article
  category: 主模块子文章
  summary: Java 锁机制详解
-->

# Java 锁机制详解

> 全面梳理 synchronized、ReentrantLock、ReentrantReadWriteLock、StampedLock 的原理与实践

---
## 引言：变更说明

Java 锁机制详解 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 目录

- [一、synchronized 锁升级过程](#一synchronized-锁升级过程)
- [二、Mark Word 结构详解](#二mark-word-结构详解)
- [三、ReentrantLock 原理](#三reentrantlock-原理)
- [四、ReentrantReadWriteLock](#四reentrantreadwritelock)
- [五、StampedLock](#五stampedlock)
- [六、锁选择指南](#六锁选择指南)

---

## 一、synchronized 锁升级过程

### 1.1 锁的四种状态

Java 6 之后，synchronized 不再是单纯的重量级锁，而是引入了锁升级机制，根据竞争程度动态调整锁的粒度，大幅提升性能。

```text
无锁 (No Lock) → 偏向锁 (Biased Lock) → 轻量级锁 (Lightweight Lock) → 重量级锁 (Heavyweight Lock)
```

```text
┌─────────────────────────────────────────────────────────────────┐
│                    synchronized 锁升级流程                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐             │
│   │  无  锁   │ ───▶ │  偏向锁   │ ───▶ │ 轻量级锁  │             │
│   │  (New)   │      │ (Biased) │      │(Spin/CAS)│             │
│   └──────────┘      └──────────┘      └────┬─────┘             │
│                                            │                   │
│                                            ▼                   │
│                                     ┌──────────┐              │
│                                     │ 重量级锁  │              │
│                                     │(Monitor) │              │
│                                     └──────────┘              │
│                                                                 │
│  触发条件:                                                        │
│  偏向锁:  首个线程进入, Mark Word 记录线程 ID                       │
│  轻量级锁: 出现竞争, CAS 尝试获取锁                                 │
│  重量级锁: 自旋失败 / 竞争加剧, 线程阻塞挂起                         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 偏向锁 (Biased Locking)

**核心思想**: 如果锁总是被同一个线程获取, 则不需要任何同步操作。

- 首个线程获取锁时, 将 Mark Word 中的偏向线程 ID 设置为当前线程
- 后续该线程再次进入同步块时, 只需检查 Mark Word 中的线程 ID 是否匹配
- 无需 CAS, 无需自旋

```java
public class BiasedLockDemo {
    // 默认开启偏向锁 (JDK 15 之前)
    // JVM 参数: -XX:+UseBiasedLocking -XX:BiasedLockingStartupDelay=0
    private final Object lock = new Object();

    public void biasedMethod() {
        // 第一次进入: 设置偏向线程
        // 后续进入: 直接检查线程 ID, 无 CAS 开销
        synchronized (lock) {
            System.out.println("偏向锁生效, 线程: " + Thread.currentThread().getName());
        }
    }
}
```

**偏向锁撤销条件**:

- 另一个线程尝试获取该锁
- 调用 `wait()` / `notify()` 方法
- 偏向线程退出同步块后, 其他线程进入

### 1.3 轻量级锁 (Lightweight Locking)

**核心思想**: 通过 CAS + 自旋避免线程阻塞, 适用于锁持有时间短、竞争不激烈的场景。

```java
public class LightweightLockDemo {
    private int counter = 0;
    private final Object lock = new Object();

    public void increment() {
        // 多线程竞争时, 偏向锁升级为轻量级锁
        // 线程通过 CAS 尝试获取锁, 失败则自旋等待
        synchronized (lock) {
            counter++;
        }
    }
}
```

**自旋锁优化**:

| JDK 版本 | 自旋策略 |
|---------|---------|
| JDK 6 | 固定次数自旋 (默认 10 次) |
| JDK 7+ | 自适应自旋, 根据历史自旋成功率动态调整次数 |

### 1.4 重量级锁 (Heavyweight Locking)

当轻量级锁自旋失败或竞争激烈时, 升级为重量级锁, 线程阻塞挂起, 依赖操作系统 Mutex 实现。

```java
public class HeavyweightLockDemo {
    private final Object lock = new Object();

    public void heavyMethod() {
        // 竞争激烈的场景, 轻量级锁自旋多次失败后升级为重量级锁
        synchronized (lock) {
            // 耗时操作, 线程可能被阻塞
            doHeavyWork();
        }
    }

    private void doHeavyWork() {
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

### 1.5 最佳实践

1. **减少 synchronized 的粒度**: 只包裹必要的代码段, 不要包裹整个方法
2. **避免锁升级**: 如果确定存在竞争, 直接使用 ReentrantLock 或设置 JVM 参数关闭偏向锁
3. **注意 JDK 15+ 变化**: 偏向锁在 JDK 15 中被废弃 (Deprecated), JDK 18+ 已移除
4. **合理使用锁消除**: JIT 编译器可以消除不逃逸对象的锁, 确保私有变量不逃逸

---

## 二、Mark Word 结构详解

### 2.1 什么是 Mark Word

Mark Word 是对象头 (Object Header) 的一部分, 用于存储对象的运行时数据, 包括哈希码、GC 分代年龄、锁状态等。在 64 位 JVM 中, Mark Word 占 64 bit (8 字节)。

### 2.2 Mark Word 在不同锁状态下的结构

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    64-bit JVM Mark Word 结构                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  无锁状态:                                                               │
│  ┌──────────────────────┬─────┬──────┬───────────┬────┬─────────────────┐│
│  │ unused:25            │ age:4│ 1  │  01      │    │                 ││
│  ├──────────────────────┼─────┼──────┼───────────┼────┤                 ││
│  │ 对象哈希码 (54 bits)  │分代年龄│ 偏向锁 │ 锁标志位  │    │                 ││
│  └──────────────────────┴─────┴──────┴───────────┴────┴─────────────────┘│
│                                                                         │
│  偏向锁状态:                                                             │
│  ┌──────────────┬─────────────┬────────────┬──────┬─────────────────────┐│
│  │ Thread:54    │ Epoch:2     │ unused:1   │  age:4│  1  │  01          ││
│  ├──────────────┼─────────────┼────────────┼──────┼─────┼───────────────┤│
│  │ 偏向线程 ID   │ 偏向时间戳   │  未使用     │分代年龄│偏向锁│ 锁标志位      ││
│  └──────────────┴─────────────┴────────────┴──────┴─────┴───────────────┘│
│                                                                         │
│  轻量级锁状态:                                                           │
│  ┌──────────────────────────────────────────────┬───────┬────────────────┐│
│  │ ptr_to_lock_record:62                         │  00   │                ││
│  ├──────────────────────────────────────────────┼───────┤                ││
│  │ 指向栈中 Lock Record 的指针                     │ 锁标志位│                ││
│  └──────────────────────────────────────────────┴───────┴────────────────┘│
│                                                                         │
│  重量级锁状态:                                                           │
│  ┌──────────────────────────────────────────────┬───────┬────────────────┐│
│  │ ptr_to_monitor:62                             │  10   │                ││
│  ├──────────────────────────────────────────────┼───────┤                ││
│  │ 指向 Monitor 对象的指针                         │ 锁标志位│                ││
│  └──────────────────────────────────────────────┴───────┴────────────────┘│
│                                                                         │
│  GC 标记状态:                                                            │
│  ┌──────────────────────────────────────────────┬───────┬────────────────┐│
│  │ ptr_to_forwarding:62                          │  11   │                ││
│  ├──────────────────────────────────────────────┼───────┤                ││
│  │ 指向复制后新对象的指针                           │ 锁标志位│                ││
│  └──────────────────────────────────────────────┴───────┴────────────────┘│
│                                                                         │
│  锁标志位 (最后 2 bit):                                                   │
│  00 - 轻量级锁   01 - 无锁/偏向锁   10 - 重量级锁   11 - GC 标记           │
│  偏向锁标志: 倒数第 3 bit, 01 状态下该位为 1 表示偏向锁, 为 0 表示无锁       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Lock Record (栈帧中的锁记录)

轻量级锁加锁时, 会在当前线程的栈帧中创建一个 Lock Record:

```text
┌─────────────────────────────────────────────────┐
│              线程栈帧中的 Lock Record              │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  displaced_markword (保存的原始 Mark Word) │  │
│  ├───────────────────────────────────────────┤  │
│  │  obj_ref (指向被锁对象的引用)               │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  加锁过程:                                        │
│  1. 将对象 Mark Word 复制到 Lock Record          │
│  2. CAS 将对象 Mark Word 替换为 Lock Record 地址  │
│  3. CAS 成功 → 加锁成功; 失败 → 锁膨胀           │
│                                                 │
│  解锁过程:                                        │
│  1. CAS 将 Lock Record 中的 Mark Word 还原        │
│  2. CAS 成功 → 解锁成功; 失败 → 说明锁已膨胀      │
└─────────────────────────────────────────────────┘
```

### 2.4 ObjectMonitor (重量级锁核心)

```java
// ObjectMonitor 核心结构 (C++ 伪代码)
struct ObjectMonitor {
    int     _count;          // 锁重入次数
    int     _recursions;     // 递归次数 (重入锁)
    Thread* _owner;          // 当前持有锁的线程
    int     _waiters;        // 等待线程数量
    ObjectWaiter* _cxq;     // 入口队列 (Contention Queue)
    ObjectWaiter* _EntryList; // 就绪队列
    ObjectWaiter* _WaitSet;   // 等待队列 (调用 wait() 进入)
};
```

### 2.5 最佳实践

1. **理解对象头开销**: 每个对象都有 Mark Word 开销, 大量小对象场景考虑使用数组或紧凑布局
2. **hashCode 缓存**: `Object.hashCode()` 首次调用时计算并存入 Mark Word, 后续直接读取
3. **JOL 工具分析**: 使用 `jol-core` 查看对象实际布局, 验证锁状态

```xml
<!-- JOL (Java Object Layout) 依赖 -->
<dependency>
    <groupId>org.openjdk.jol</groupId>
    <artifactId>jol-core</artifactId>
    <version>0.16</version>
</dependency>
```

```java
import org.openjdk.jol.info.ClassLayout;

public class MarkWordAnalysis {
    public static void main(String[] args) {
        Object obj = new Object();
        // 打印对象布局, 包含 Mark Word 信息
        System.out.println(ClassLayout.parseInstance(obj).toPrintable());
    }
}
```

---

## 三、ReentrantLock 原理

### 3.1 核心架构

ReentrantLock 基于 AQS (AbstractQueuedSynchronizer) 实现, 使用 CAS + volatile + LockSupport 完成锁操作。

```text
┌─────────────────────────────────────────────────────────────────┐
│                    ReentrantLock 架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────┐              │
│  │              ReentrantLock                     │              │
│  │  ┌─────────────────┐  ┌─────────────────────┐ │              │
│  │  │   FairSync      │  │    NonfairSync      │ │              │
│  │  │  (公平锁实现)    │  │   (非公平锁实现)     │ │              │
│  │  └────────┬────────┘  └─────────┬───────────┘ │              │
│  │           │                      │             │              │
│  │           └──────────┬───────────┘             │              │
│  │                      ▼                         │              │
│  │         ┌─────────────────────────┐            │              │
│  │         │     AQS (Sync)          │            │              │
│  │         │  state (volatile int)   │            │              │
│  │         │  CLH 等待队列            │            │              │
│  │         └─────────────────────────┘            │              │
│  └───────────────────────────────────────────────┘              │
│                                                                 │
│  核心组件:                                                        │
│  - state: volatile int, 表示锁的状态 (0=无锁, >0=重入次数)        │
│  - CLH 队列: 双向链表, 存储等待获取锁的线程                        │
│  - CAS: 原子操作, 用于修改 state 和队列节点                        │
│  - LockSupport: 线程阻塞/唤醒 (park/unpark)                      │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 非公平锁加锁流程

```java
public class ReentrantLockNonfairDemo {
    private final ReentrantLock lock = new ReentrantLock(false); // 非公平锁

    public void doWork() {
        lock.lock();
        try {
            // 临界区
            doSomething();
        } finally {
            lock.unlock(); // 必须在 finally 中释放
        }
    }
}
```

**加锁流程**:

```text
lock() 调用
    │
    ▼
┌─────────────────┐     成功      ┌──────────────┐
│ CAS state 0→1   │ ──────────▶  │ 获取锁成功     │
│ (尝试快速获取)   │              └──────────────┘
└────────┬────────┘
         │ 失败 (已有线程持有)
         ▼
┌─────────────────┐     是当前线程  ┌──────────────┐
│ 检查是否是当前    │ ────────────▶ │ state++,      │
│ 线程持有的锁     │               │ 重入成功       │
└────────┬────────┘               └──────────────┘
         │ 不是当前线程
         ▼
┌─────────────────────────────────────────┐
│ 加入 CLH 等待队列                        │
│ → LockSupport.park() 阻塞线程            │
│ → 被唤醒后再次尝试获取锁                  │
└─────────────────────────────────────────┘
```

### 3.3 AQS CLH 队列结构

```text
┌─────────────────────────────────────────────────────────────────┐
│                    CLH 双向等待队列                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐                │
│  │  Head     │ ──▶ │ Node(T1)  │ ──▶ │ Node(T2)  │ ──▶ null     │
│  │ (dummy)   │ ◀── │          │ ◀── │          │ ◀──            │
│  └──────────┘     └──────────┘     └──────────┘                │
│                                                                 │
│  每个 Node 包含:                                                 │
│  ┌───────────────────────────────────────────────────┐         │
│  │  thread:  等待的线程引用                            │         │
│  │  prev:    前驱节点                                  │         │
│  │  next:    后继节点                                  │         │
│  │  waitStatus: 节点状态                               │         │
│  │             SIGNAL(-1): 后继线程需要被唤醒           │         │
│  │             CANCELLED(1):  线程已取消/超时/中断      │         │
│  │             CONDITION(-2): 在 Condition 队列中      │         │
│  │             PROPAGATE(-3): 共享模式下传播唤醒        │         │
│  │  nextWaiter: 条件队列中的下一个节点                  │         │
│  └───────────────────────────────────────────────────┘         │
│                                                                 │
│  队列操作 (全部使用 CAS 保证线程安全):                             │
│  - enq(): 将节点插入队尾                                         │
│  - acquire(): 尝试获取锁, 失败则入队                             │
│  - release(): 释放锁, 唤醒后继节点                               │
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 公平锁 vs 非公平锁

| 对比项 | 公平锁 (Fair) | 非公平锁 (Nonfair) |
|-------|-------------|-----------------|
| 获取顺序 | 严格按 FIFO | 允许插队 |
| 吞吐量 | 较低 | 较高 (减少线程唤醒开销) |
| 饥饿风险 | 无 | 低优先级线程可能饥饿 |
| 上下文切换 | 较多 | 较少 |
| 默认选择 | 否 | **是** (默认) |
| 适用场景 | 要求公平性的场景 | 大多数高并发场景 |

```java
// 公平锁
ReentrantLock fairLock = new ReentrantLock(true);

// 非公平锁 (默认)
ReentrantLock nonfairLock = new ReentrantLock(); // 等价于 new ReentrantLock(false)
```

### 3.5 可中断锁与超时锁

```java
public class InterruptibleLockDemo {
    private final ReentrantLock lock = new ReentrantLock();

    // 可中断获取锁
    public void interruptibleMethod() throws InterruptedException {
        lock.lockInterruptibly(); // 响应中断
        try {
            doSomething();
        } finally {
            lock.unlock();
        }
    }

    // 超时获取锁
    public void timeoutMethod() {
        try {
            if (lock.tryLock(3, TimeUnit.SECONDS)) {
                try {
                    doSomething();
                } finally {
                    lock.unlock();
                }
            } else {
                // 超时后的降级处理
                handleTimeout();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

### 3.6 Condition 条件变量

```java
public class ConditionDemo {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();
    private final Object[] items = new Object[100];
    private int count;

    public void put(Object item) throws InterruptedException {
        lock.lock();
        try {
            while (count == items.length) {
                notFull.await(); // 队列满, 等待
            }
            items[count++] = item;
            notEmpty.signal(); // 唤醒取数据的线程
        } finally {
            lock.unlock();
        }
    }

    public Object take() throws InterruptedException {
        lock.lock();
        try {
            while (count == 0) {
                notEmpty.await(); // 队列空, 等待
            }
            Object item = items[--count];
            notFull.signal(); // 唤醒存数据的线程
            return item;
        } finally {
            lock.unlock();
        }
    }
}
```

### 3.7 最佳实践

1. **lock/unlock 配对**: unlock 必须放在 finally 块中
2. **优先非公平锁**: 除非业务强依赖公平性, 默认使用非公平锁以获得更高吞吐量
3. **避免死锁**: 使用 `tryLock(timeout)` 替代无限等待的 `lock()`
4. **Condition 替代 wait/notify**: Condition 支持多个等待队列, 精确唤醒目标线程
5. **避免锁泄漏**: 确保每个 lock() 都有对应的 unlock(), 使用 try-with-resources 模式

---

## 四、ReentrantReadWriteLock

### 4.1 读写锁核心概念

读写锁将锁分为读锁 (共享锁) 和写锁 (独占锁), 允许多个线程同时读, 但写操作独占。

```text
┌─────────────────────────────────────────────────────────────────┐
│              ReentrantReadWriteLock 锁兼容矩阵                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│              │  当前读锁    │  当前写锁                           │
│  ────────────┼─────────────┼─────────────                        │
│  请求读锁    │   ✓ 允许     │   ✗ 阻塞                           │
│  请求写锁    │   ✗ 阻塞     │   ✗ 阻塞                           │
│                                                                 │
│  规则:                                                           │
│  - 读-读: 不互斥 (可并发)                                        │
│  - 读-写: 互斥                                                   │
│  - 写-写: 互斥                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 基本用法

```java
public class ReadWriteLockDemo {
    private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
    private final ReadLock readLock = rwLock.readLock();
    private final WriteLock writeLock = rwLock.writeLock();
    private Map<String, Object> cache = new HashMap<>();

    public Object get(String key) {
        readLock.lock();
        try {
            return cache.get(key);
        } finally {
            readLock.unlock();
        }
    }

    public void put(String key, Object value) {
        writeLock.lock();
        try {
            cache.put(key, value);
        } finally {
            writeLock.unlock();
        }
    }
}
```

### 4.3 锁降级 (Lock Downgrading)

写线程持有写锁时, 可以再获取读锁, 然后释放写锁, 实现锁降级。这保证了从写操作到读操作的平滑过渡, 中间不允许其他写线程插入。

```java
public class LockDowngradeDemo {
    private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
    private volatile boolean isUpdated = false;
    private Object data;

    public void processWithDowngrade() {
        rwLock.writeLock().lock();
        try {
            // 1. 执行写操作
            data = computeData();
            isUpdated = true;

            // 2. 获取读锁 (锁降级: 写锁 + 读锁同时持有)
            rwLock.readLock().lock();
        } finally {
            // 3. 释放写锁 (保留读锁)
            rwLock.writeLock().unlock();
        }

        // 4. 在读锁保护下执行后续读操作
        try {
            readAndProcess(data);
        } finally {
            // 5. 释放读锁
            rwLock.readLock().unlock();
        }
    }

    private Object computeData() {
        return "computed";
    }

    private void readAndProcess(Object d) {
        // 处理数据
    }
}
```

**注意**: 不支持锁升级! 读锁不能升级为写锁, 否则会导致死锁。

```java
// 错误示例: 锁升级会导致死锁
public void wrongUpgrade() {
    rwLock.readLock().lock();
    try {
        if (needsUpdate()) {
            // 死锁! 读锁未释放就尝试获取写锁
            rwLock.writeLock().lock(); // BLOCKED!
        }
    } finally {
        rwLock.readLock().unlock();
    }
}
```

### 4.4 公平性策略

| 策略 | 说明 |
|-----|------|
| 非公平 (默认) | 写锁插入优先级高于读锁, 写饥饿风险低 |
| 公平 | 严格按等待顺序获取, 读写交替 |

```java
// 公平模式: 适合读多写少, 需要保证读线程不被饿死的场景
ReentrantReadWriteLock fairRwLock = new ReentrantReadWriteLock(true);
```

### 4.5 最佳实践

1. **读多写少场景**: 读操作远多于写操作时使用, 如缓存系统
2. **锁降级模式**: 写后需要立即读取验证时使用锁降级
3. **避免长时间持写锁**: 写锁独占, 长时间持有可能导致大量读线程阻塞
4. **读锁不保证可见性**: 获取读锁时不一定能看到其他线程的写操作 (需要写锁先行)
5. **不支持锁升级**: 设计上不允许从读锁升级到写锁

---

## 五、StampedLock

### 5.1 为什么需要 StampedLock

ReentrantReadWriteLock 存在两个问题:

- **写饥饿**: 大量读操作时, 写线程可能长时间等待
- **读锁性能**: 读锁仍然需要 CAS 操作, 有性能开销

StampedLock (Java 8 引入) 引入了**乐观读锁 (Optimistic Read)**, 在读多写少且读操作不依赖强一致性的场景下, 性能显著提升。

### 5.2 三种锁模式

```text
┌─────────────────────────────────────────────────────────────────┐
│                 StampedLock 三种锁模式                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  模式            │ 说明                      │ 性能              │
│  ────────────────┼───────────────────────────┼────────────      │
│  写锁 (Write)    │ 独占锁, 同 ReentrantLock   │ 低 (独占)         │
│  悲观读锁 (Read)  │ 共享锁, 同 ReadWriteLock   │ 中 (需 CAS)       │
│  乐观读 (OptRead) │ 无锁读取, 事后校验版本号    │ 高 (无阻塞)       │
│                                                                 │
│  乐观读流程:                                                     │
│  1. 获取当前版本号 (stamp)                                       │
│  2. 读取数据 (无锁)                                              │
│  3. 校验版本号是否变化                                           │
│     - 未变化: 读取成功, 数据一致                                  │
│     - 已变化: 升级为悲观读锁, 重新读取                           │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 StampedLock 完整示例

```java
public class StampedLockDemo {
    private final StampedLock sl = new StampedLock();
    private double x, y; // 共享数据

    // 乐观读: 高性能, 适用于数据不一致可接受的场景
    public double distanceFromOrigin() {
        long stamp = sl.tryOptimisticRead(); // 获取乐观读锁, 返回版本号
        double currentX = x;
        double currentY = y;

        // 校验版本号: 如果期间没有写操作, 返回 true
        if (!sl.validate(stamp)) {
            // 版本号变化, 升级为悲观读锁
            stamp = sl.readLock();
            try {
                currentX = x;
                currentY = y;
            } finally {
                sl.unlockRead(stamp);
            }
        }
        return Math.sqrt(currentX * currentX + currentY * currentY);
    }

    // 写锁: 独占
    public void move(double deltaX, double deltaY) {
        long stamp = sl.writeLock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            sl.unlockWrite(stamp);
        }
    }

    // 悲观读锁: 保证强一致性
    public double getXY() {
        long stamp = sl.readLock();
        try {
            return x + y;
        } finally {
            sl.unlockRead(stamp);
        }
    }

    // 读锁升级为写锁 (尝试转换)
    public void moveIfAtOrigin(double newX, double newY) {
        long stamp = sl.readLock();
        try {
            while (x == 0.0 && y == 0.0) {
                // 尝试将读锁转换为写锁
                long ws = sl.tryConvertToWriteLock(stamp);
                if (ws != 0L) {
                    stamp = ws; // 转换成功
                    x = newX;
                    y = newY;
                    return;
                } else {
                    // 转换失败, 先释放读锁, 再获取写锁
                    sl.unlockRead(stamp);
                    stamp = sl.writeLock();
                }
            }
        } finally {
            sl.unlock(stamp);
        }
    }
}
```

### 5.4 性能对比

```text
┌─────────────────────────────────────────────────────────────────┐
│              不同锁在高并发读场景下的性能对比                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  吞吐量 (相对值, 越高越好):                                       │
│                                                                 │
│  StampedLock (乐观读)    ██████████████████████████████  100%    │
│  ReentrantReadWriteLock  ████████████████              ~55%     │
│  synchronized            ██████████                      ~35%    │
│  ReentrantLock           █████████                       ~30%    │
│                                                                 │
│  测试场景: 95% 读 + 5% 写, 16 线程并发                           │
│  数据来源: 典型基准测试, 实际结果因硬件/负载而异                    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.5 StampedLock 注意事项

| 特性 | 说明 |
|-----|------|
| 不可重入 | StampedLock 不支持重入, 同一线程重复获取会死锁 |
| 无锁语义 | 乐观读不阻塞写线程, 写也不阻塞乐观读 |
| 中断支持 | 不支持中断式获取锁, `lockInterruptibly()` 不可用 |
| Condition | 不支持 Condition 条件变量 |
| 版本号溢出 | stamp 是 long 类型, 极端情况下可能溢出 (极罕见) |

### 5.6 最佳实践

1. **读远大于写**: 乐观读在读操作占 90%+ 的场景下优势明显
2. **数据一致性要求不高**: 乐观读允许短暂的不一致, 适用于缓存、统计等场景
3. **避免在乐观读中做耗时操作**: 校验失败后需要重试, 耗时操作降低整体吞吐
4. **注意不可重入**: 如果方法调用链中需要多次获取同一锁, 不要使用 StampedLock
5. **不要依赖中断**: 不支持 `lockInterruptibly()`, 需要自行处理超时和中断

---

## 六、锁选择指南

### 6.1 锁对比总览

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Java 锁机制对比总览                                     │
├─────────────┬────────────┬──────────┬──────────┬──────────┬──────────────────┤
│   特性       │ synchronized│ Reentrant│ RWLock   │StampedLock│ 适用场景         │
│             │            │  Lock    │          │          │                  │
├─────────────┼────────────┼──────────┼──────────┼──────────┼──────────────────┤
│ 可重入       │     ✓      │    ✓     │    ✓     │    ✗     │                  │
│ 公平性       │    非公平   │  公平/   │ 公平/    │    ✗     │                  │
│             │            │  非公平   │ 非公平    │          │                  │
│ 条件变量     │  wait/    │ Condition│ Condition│    ✗     │                  │
│             │  notify    │          │          │          │                  │
│ 读写分离     │     ✗      │    ✗     │    ✓     │    ✓     │                  │
│ 乐观读       │     ✗      │    ✗     │    ✗     │    ✓     │                  │
│ 可中断       │     ✗      │    ✓     │    ✓     │    ✗     │                  │
│ 超时获取     │     ✗      │    ✓     │    ✓     │    ✗     │                  │
│ 锁降级       │     ✗      │    ✗     │    ✓     │    ✓     │                  │
│ 性能 (低竞争)│    好      │   好     │    中    │   最优    │                  │
│ 性能 (高竞争)│    中      │   好     │    好    │   好     │                  │
│ 性能 (读多写少)│  差      │   差     │    好    │   最优    │                  │
├─────────────┴────────────┴──────────┴──────────┴──────────┴──────────────────┤
│  JDK 版本: synchronized (1.0)  ReentrantLock (1.5)  RWLock (1.5)  Stamped(1.8) │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 决策树

```text
                        是否需要锁?
                            │
                    ┌───────┴───────┐
                    是              否 (使用无锁方案/原子类)
                    │
            是否读多写少?
               ╱       ╲
             是          否
             │           │
     是否需要强一致性?    是否需要以下特性:
        ╱         ╲      - 可中断/超时
       是          否     - 多 Condition
     │             │     - 公平性
  ReadWriteLock  StampedLock  需要 → ReentrantLock
  (悲观读锁)     (乐观读)      不需要 → synchronized
```

### 6.3 场景推荐

| 场景 | 推荐锁 | 理由 |
|-----|-------|------|
| 简单同步, 低竞争 | `synchronized` | 语法简洁, JIT 优化好, 无需手动释放 |
| 需要可中断/超时 | `ReentrantLock` | 支持 `lockInterruptibly()` / `tryLock()` |
| 多个等待条件 | `ReentrantLock` + `Condition` | 多条件队列, 精确唤醒 |
| 缓存系统 (读多写少) | `StampedLock` | 乐观读性能最优 |
| 配置中心 (读远多于写) | `ReentrantReadWriteLock` | 悲观读保证一致性 |
| 需要公平调度 | `ReentrantLock(true)` | 严格按 FIFO 顺序 |
| 计数器/状态标志 | `AtomicInteger` / `LongAdder` | 无锁 CAS, 性能最优 |
| 方法级别同步 | `synchronized` 方法 | 语法最简洁 |

### 6.4 无锁替代方案

很多场景下根本不需要锁:

```java
// 场景1: 简单计数器 - 使用 AtomicInteger 替代 synchronized
public class CounterWithAtomic {
    private final AtomicInteger count = new AtomicInteger(0);

    public void increment() {
        count.incrementAndGet(); // CAS 无锁操作
    }

    public int get() {
        return count.get(); // volatile 语义保证可见性
    }
}

// 场景2: 高并发计数器 - 使用 LongAdder 替代 AtomicInteger
public class HighConcurrentCounter {
    private final LongAdder counter = new LongAdder();

    public void increment() {
        counter.increment(); // 分段累加, 高并发下性能优于 AtomicInteger
    }

    public long sum() {
        return counter.sum();
    }
}

// 场景3: 引用安全发布 - 使用 volatile
public class SafePublication {
    private volatile Config config;

    public void init() {
        // volatile 保证 initConfig() 的结果对所有线程可见
        config = initConfig();
    }

    public Config getConfig() {
        return config; // 无需加锁
    }
}
```

### 6.5 最佳实践

1. **优先使用高层并发工具**: `ConcurrentHashMap`、`CopyOnWriteArrayList` 等已内部优化
2. **缩小同步范围**: 只同步必要的代码行, 不要在同步块中做 I/O 或网络调用
3. **避免嵌套锁**: 多层锁嵌套增加死锁风险, 使用单一锁或锁分段
4. **文档化锁的使用**: 在类注释中说明锁的使用策略和约束
5. **性能测试**: 不同锁方案在不同硬件上的表现差异很大, 务必做基准测试
6. **避免隐式锁**: 注意 `Collections.synchronizedMap()` 等方法返回的包装类内部使用锁
7. **死锁检测**: 生产环境使用 `jstack` 或 JMX 的 `ThreadMXBean.findDeadlockedThreads()` 检测

---

## 附录: 常用 JVM 锁相关参数

| 参数 | 说明 | 默认值 |
|-----|------|-------|
| `-XX:+UseBiasedLocking` | 开启偏向锁 (JDK 15 已废弃) | JDK 6-14: 开启 |
| `-XX:BiasedLockingStartupDelay=N` | 偏向锁启动延迟 (毫秒) | 4000 |
| `-XX:PreBlockSpin=N` | 自旋次数 (JDK 6, 已废弃) | 10 |
| `-XX:+UseSpinning` | 开启自旋锁 (JDK 6, 已废弃) | 开启 |
| `-XX:LockingMode=legacy` | 使用旧版锁实现 (JDK 18+, 移除偏向锁后恢复) | 无 |

---

*本文档基于 JDK 8-21 版本编写, 部分特性在不同 JDK 版本中可能存在差异, 请以实际运行环境为准。*

---

← [返回 并发编程基础概念](../README.md)
