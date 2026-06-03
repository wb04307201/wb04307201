# JUC Locks 学习笔记 (AQS / ReentrantLock / ReentrantReadWriteLock / StampedLock / Condition)

---

## 目录

- [I. AQS（AbstractQueuedSynchronizer）原理](#i-aqsabstractqueuedsynchronizer原理)
- [II. ReentrantLock 实现原理](#ii-reentrantlock-实现原理)
- [III. ReentrantReadWriteLock 读写锁](#iii-reentrantreadwritelock-读写锁)
- [IV. StampedLock（Java 8）](#iv-stampedlockjava-8)
- [V. Condition（await/signal）对比 Object.wait/notify](#v-conditionawaitsignal-对比-objectwaitnotify)
- [VI. Lock vs synchronized 完整对比](#vi-lock-vs-synchronized-完整对比)
- [VII. 自旋锁与适应性自旋](#vii-自旋锁与适应性自旋)

---

## I. AQS（AbstractQueuedSynchronizer）原理

AQS（AbstractQueuedSynchronizer）是 JUC 包中所有锁和同步器的 **基础设施框架**。ReentrantLock、ReentrantReadWriteLock、CountDownLatch、Semaphore、FutureTask 等都基于 AQS 实现。

### 1.1 核心设计思想

AQS 的核心抽象为两个部分：

```
AQS = 同步状态（volatile int state） + CLH 等待队列
```

- **同步状态 state**：一个 volatile int 变量，子类通过 `tryAcquire` / `tryRelease` 等方法基于 CAS 修改 state，实现不同的同步语义。
  - ReentrantLock：state 表示重入次数（0 = 空闲，>0 = 已持有）
  - Semaphore：state 表示剩余许可数
  - CountDownLatch：state 表示倒数计数器
- **CLH 队列**：一个双向 FIFO 队列，存放等待获取锁的线程节点

### 1.2 AQS 队列结构（ASCII 示意图）

```
     +------+  prev  +-----+  prev  +-----+
head |      | <----- |     | <----- |     | tail
     | Node | -----> | Node | -----> | Node |
     +------+  next  +-----+  next  +-----+
       |                |               |
     (null)          thread          thread
                   waiting          waiting
```

每个 Node 节点的核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `thread` | Thread | 等待的线程 |
| `prev` | Node | 前驱节点 |
| `next` | Node | 后继节点 |
| `waitStatus` | int | 节点状态 |
| `nextWaiter` | Node | Condition 队列中的后继 |

### 1.3 waitStatus 状态值

```java
static final int CANCELLED =  1;   // 线程被取消或超时，节点应从队列移除
static final int SIGNAL    = -1;   // 后继节点需要被唤醒（最常见状态）
static final int CONDITION = -2;   // 节点在 Condition 队列中等待
static final int PROPAGATE = -3;   // 用于共享模式，表示 propagate release
// 0: 初始状态，新节点创建时默认为 0
```

状态转换图：

```
新节点(0) --> 被后继设为 SIGNAL(-1) --> 释放时唤醒
       \
        --> 取消 CANCELLED(1) --> 出队
```

### 1.4 AQS 核心模板方法

AQS 采用 **模板方法模式**，子类只需实现以 `try` 开头的 protected 方法：

| 方法 | 说明 | 模式 |
|------|------|------|
| `tryAcquire(int)` | 尝试获取独占资源 | 独占 |
| `tryRelease(int)` | 尝试释放独占资源 | 独占 |
| `tryAcquireShared(int)` | 尝试获取共享资源，<0 失败，=0 成功但无剩余，>0 成功且有余量 | 共享 |
| `tryReleaseShared(int)` | 尝试释放共享资源 | 共享 |
| `isHeldExclusively()` | 当前线程是否独占持有 | 独占 |

### 1.5 acquire 完整流程（独占模式）

```java
public final void acquire(int arg) {
    if (!tryAcquire(arg) &&
        acquireQueued(addWaiter(Node.EXCLUSIVE), arg))
        selfInterrupt();
}
```

流程图：

```
tryAcquire(state)
     │
     ├── 成功 → 直接返回，获取锁
     │
     └── 失败
          │
          ▼
     addWaiter(Node)  ──→ 封装为 Node，尾部入队
          │
          ▼
     acquireQueued(node)
          │
          ├── 前驱是 head？── 是 ──→ 再 tryAcquire → 成功则 setHead → 返回
          │                        │
          │                        └── 失败
          │
          └── 不是 head / 再抢失败
                    │
                    ▼
               shouldParkAfterFailedAcquire
                    │
                    ├── 前驱 SIGNAL → parkAndCheckInterrupt() → 挂起
                    │
                    └── 前驱 CANCELLED → 清理前驱，重新尝试
```

### 1.6 release 流程

```java
public final boolean release(int arg) {
    if (tryRelease(arg)) {
        Node h = head;
        if (h != null && h.waitStatus != 0)
            unparkSuccessor(h);  // 唤醒后继
        return true;
    }
    return false;
}
```

唤醒逻辑：从 head 开始向后找第一个 `waitStatus <= 0` 的有效节点，调用 `LockSupport.unpark()` 唤醒其线程。

---

## II. ReentrantLock 实现原理

### 2.1 基本结构

```
ReentrantLock
    │
    ├── Sync (extends AQS)   ← 抽象基类
    │       │
    │       ├── NonfairSync  ← 非公平锁
    │       │
    │       └── FairSync     ← 公平锁
```

### 2.2 state 的含义

ReentrantLock 中，AQS 的 `state` 表示 **锁重入次数**：

```
state == 0   → 锁空闲
state == 1   → 被某线程持有，重入 1 次
state == n   → 被某线程持有，重入 n 次
```

### 2.3 非公平锁 vs 公平锁

| 维度 | 非公平锁（NonfairSync） | 公平锁（FairSync） |
|------|------------------------|-------------------|
| 创建方式 | `new ReentrantLock()`（默认） | `new ReentrantLock(true)` |
| 获取锁策略 | 先 CAS 抢，抢不到再排队 | 直接检查队列，有排队者则排队 |
| 吞吐量 | **更高**（减少线程切换） | 较低 |
| 公平性 | 可能饥饿（后到线程先抢成功） | 严格按 FIFO 顺序 |
| 适用场景 | 大多数场景，追求吞吐量 | 需要严格顺序的场景 |

### 2.4 非公平锁 lock 源码分析

```java
// NonfairSync.lock()
final void lock() {
    // 第一步：直接 CAS 尝试抢锁（不管队列有没有人排队）
    if (compareAndSetState(0, 1))
        setExclusiveOwnerThread(Thread.currentThread());
    else
        // 第二步：抢不到，走 AQS 标准 acquire 流程
        acquire(1);
}

// NonfairSync.tryAcquire()
protected final boolean tryAcquire(int acquires) {
    return nonfairTryAcquire(acquires);
}

final boolean nonfairTryAcquire(int acquires) {
    final Thread current = Thread.currentThread();
    int c = getState();
    if (c == 0) {
        // state 为 0，说明锁空闲，再次 CAS 抢
        if (compareAndSetState(0, acquires)) {
            setExclusiveOwnerThread(current);
            return true;
        }
    }
    // 如果当前线程已经持有锁 → 重入，state++
    else if (current == getExclusiveOwnerThread()) {
        int nextc = c + acquires;
        if (nextc < 0) // 溢出保护
            throw new Error("Maximum lock count exceeded");
        setState(nextc);
        return true;
    }
    return false; // 获取失败
}
```

### 2.5 公平锁 lock 源码分析

```java
// FairSync.lock()
final void lock() {
    acquire(1);  // 直接走 AQS 流程，没有抢先 CAS
}

// FairSync.tryAcquire()
protected final boolean tryAcquire(int acquires) {
    final Thread current = Thread.currentThread();
    int c = getState();
    if (c == 0) {
        // 关键差异：hasQueuedPredecessors() 检查队列中是否有等待更久的线程
        if (!hasQueuedPredecessors() &&
            compareAndSetState(0, acquires)) {
            setExclusiveOwnerThread(current);
            return true;
        }
    }
    else if (current == getExclusiveOwnerThread()) {
        int nextc = c + acquires;
        if (nextc < 0)
            throw new Error("Maximum lock count exceeded");
        setState(nextc);
        return true;
    }
    return false;
}
```

`hasQueuedPredecessors()` 的核心逻辑：

```java
public final boolean hasQueuedPredecessors() {
    Node t = tail;
    Node h = head;
    Node s;
    // 判断 head.next 是否存在且不是当前线程
    return h != t &&
        ((s = h.next) == null || s.thread != Thread.currentThread());
}
```

### 2.6 ReentrantLock 完整示例

```java
import java.util.concurrent.locks.ReentrantLock;

public class ReentrantLockDemo {
    private final ReentrantLock lock = new ReentrantLock(); // 默认非公平
    private int counter = 0;

    public void increment() {
        lock.lock();  // 获取锁
        try {
            counter++;
        } finally {
            lock.unlock();  // 必须在 finally 中释放
        }
    }

    // 可中断锁示例
    public void incrementInterruptibly() throws InterruptedException {
        lock.lockInterruptibly();  // 等待时可被中断
        try {
            counter++;
        } finally {
            lock.unlock();
        }
    }

    // 尝试获取锁示例
    public boolean tryIncrement() {
        if (lock.tryLock()) {       // 非阻塞尝试
            try {
                counter++;
                return true;
            } finally {
                lock.unlock();
            }
        }
        return false;  // 获取失败，不阻塞
    }

    // 带超时的尝试
    public boolean tryIncrementWithTimeout() throws InterruptedException {
        if (lock.tryLock(500, TimeUnit.MILLISECONDS)) {
            try {
                counter++;
                return true;
            } finally {
                lock.unlock();
            }
        }
        return false;  // 超时未获取到
    }
}
```

---

## III. ReentrantReadWriteLock 读写锁

### 3.1 基本设计

读写锁将锁分为两类：

- **读锁（共享锁）**：多个线程可同时持有
- **写锁（独占锁）**：只能有一个线程持有

```
ReentrantReadWriteLock
    │
    ├── ReadLock   ← 共享模式（多个读者可同时持有）
    │
    └── WriteLock  ← 独占模式（同一时刻只有一个写者）
```

### 3.2 state 的拆分

```
      高 16 位                低 16 位
    ┌─────────────┬─────────────────────┐
    │  读锁计数    │    写锁重入次数      │
    │ (shared)    │   (exclusive)       │
    └─────────────┴─────────────────────┘
         ↑                 ↑
    读线程持有总数      写线程重入次数
```

```java
static final int SHARED_SHIFT   = 16;
static final int SHARED_UNIT    = (1 << SHARED_SHIFT); // 0x00010000
static final int MAX_COUNT      = (1 << SHARED_SHIFT) - 1; // 65535
static final int EXCLUSIVE_MASK = (1 << SHARED_SHIFT) - 1; // 0x0000FFFF

// 读计数：通过位运算
int readCount = state >>> SHARED_SHIFT;
// 写计数：
int writeCount = state & EXCLUSIVE_MASK;
```

### 3.3 锁兼容矩阵

|        | 读锁 | 写锁 |
|--------|------|------|
| **读锁** | 兼容 | 互斥 |
| **写锁** | 互斥 | 互斥 |

即：**读-读 不互斥，其他都互斥**。

### 3.4 锁降级

**锁降级**：持有写锁 → 获取读锁 → 释放写锁，最终只持有读锁。

```java
class CachedData {
    Object data;
    volatile boolean cacheValid;
    final ReentrantReadWriteLock rwl = new ReentrantReadWriteLock();

    void processCachedData() {
        // 1. 先获取读锁，读取数据
        rwl.readLock().lock();
        try {
            if (!cacheValid) {
                // 2. 数据失效 → 释放读锁，升级为写锁
                rwl.readLock().unlock();
                rwl.writeLock().lock();
                try {
                    // 双重检查
                    if (!cacheValid) {
                        data = loadData();
                        cacheValid = true;
                    }
                    // 3. 锁降级：在持有写锁时获取读锁
                    rwl.readLock().lock();
                } finally {
                    // 4. 释放写锁，此时仍持有读锁 → 降级完成
                    rwl.writeLock().unlock();
                }
            }
            // 使用数据（此时持有读锁）
            use(data);
        } finally {
            rwl.readLock().unlock();
        }
    }
}
```

> **注意**：ReentrantReadWriteLock **不支持锁升级**（读锁 → 写锁），会导致死锁。因为读锁是共享的，多个持有读锁的线程都想升级为写锁时会互相阻塞。

### 3.5 公平模式

```java
// 公平模式下，写锁优先于读锁获取
// 当写锁释放时，等待时间最长的线程（无论读写）优先获取
```

---

## IV. StampedLock（Java 8）

### 4.1 概述

`StampedLock` 是 Java 8 引入的读写锁改进版，相比 `ReentrantReadWriteLock`：

- **性能更高**（内部使用更精细的自旋和阻塞策略）
- **支持乐观读**（Optimistic Read）—— 无锁读取 + 版本校验
- **不支持重入**（这是与 RWLock 的重要区别）
- 返回 `long` 类型的 **stamp**（印章/戳）来管理锁状态

### 4.2 三种读模式

| 模式 | 方法 | 特点 |
|------|------|------|
| **乐观读** | `tryOptimisticRead()` | 不阻塞，返回 stamp，后续需用 `validate(stamp)` 验证 |
| **读锁** | `readLock()` | 阻塞式共享锁，需 `unlockRead(stamp)` 释放 |
| **写锁** | `writeLock()` | 阻塞式独占锁，需 `unlockWrite(stamp)` 释放 |

### 4.3 乐观读示例（StampedLock 最核心用法）

```java
class Point {
    private double x, y;
    private final StampedLock sl = new StampedLock();

    // 移动点（写操作）
    void move(double deltaX, double deltaY) {
        long stamp = sl.writeLock();  // 获取写锁
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            sl.unlockWrite(stamp);    // 释放写锁
        }
    }

    // 读取距离（乐观读）
    double distanceFromOrigin() {
        // 1. 尝试乐观读（不加锁，性能极高）
        long stamp = sl.tryOptimisticRead();
        double currentX = x, currentY = y;

        // 2. 验证 stamp 是否仍然有效
        if (!sl.validate(stamp)) {
            // 3. 验证失败 → 说明有写操作发生，升级为悲观读锁
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

    // 锁升级：读锁 → 写锁
    void moveIfAtOrigin(double newX, double newY) {
        long stamp = sl.readLock();
        try {
            while (x == 0.0 && y == 0.0) {
                // 尝试将读锁升级为写锁
                long ws = sl.tryConvertToWriteLock(stamp);
                if (ws != 0L) {
                    stamp = ws;
                    x = newX;
                    y = newY;
                    break;
                } else {
                    // 升级失败（有其他读者），先释放读锁再获取写锁
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

### 4.4 StampedLock vs ReentrantReadWriteLock

| 维度 | StampedLock | ReentrantReadWriteLock |
|------|-------------|----------------------|
| 乐观读 | 支持 | 不支持 |
| 重入 | **不支持** | 支持 |
| 性能 | 更高 | 较低 |
| 锁升级/降级 | 支持转换 | 仅支持降级 |
| 返回值 | long stamp | 无 |
| Condition 支持 | **不支持** | 支持 |
| 公平模式 | **不支持** | 支持 |

---

## V. Condition（await/signal）对比 Object.wait/notify

### 5.1 基本对比

| 维度 | Object.wait/notify | Condition.await/signal |
|------|--------------------|------------------------|
| 关联对象 | 每个 Object 都有 | 与 Lock 关联，一个 Lock 可创建多个 Condition |
| 前置条件 | 必须在 synchronized 块中 | 必须在 lock.lock() 之后 |
| 多等待队列 | 不支持（每个锁只有一个等待集） | **支持**（一个锁多个 Condition） |
| 中断响应 | `wait()` 不响应中断 | `await()` 响应中断，`awaitUninterruptibly()` 不响应 |
| 超时等待 | `wait(timeout)` | `await(time, unit)` / `awaitNanos()` |
| 灵活性 | 低 | 高 |

### 5.2 经典示例：生产者-消费者（ArrayBlockingQueue 内部实现原理）

```java
import java.util.concurrent.locks.*;

class BoundedBuffer<E> {
    final Lock lock = new ReentrantLock();
    final Condition notFull  = lock.newCondition();  // 不满条件
    final Condition notEmpty = lock.newCondition();  // 不空条件
    final Object[] items = new Object[100];
    int putIndex, takeIndex, count;

    public void put(E x) throws InterruptedException {
        lock.lock();
        try {
            while (count == items.length)
                notFull.await();  // 满了 → 在 notFull 队列等待
            items[putIndex] = x;
            putIndex = (putIndex + 1) % items.length;
            count++;
            notEmpty.signal();    // 唤醒一个在 notEmpty 队列等待的消费者
        } finally {
            lock.unlock();
        }
    }

    @SuppressWarnings("unchecked")
    public E take() throws InterruptedException {
        lock.lock();
        try {
            while (count == 0)
                notEmpty.await(); // 空了 → 在 notEmpty 队列等待
            E x = (E) items[takeIndex];
            takeIndex = (takeIndex + 1) % items.length;
            count--;
            notFull.signal();     // 唤醒一个在 notFull 队列等待的生产者
            return x;
        } finally {
            lock.unlock();
        }
    }
}
```

### 5.3 Condition 等待队列原理

Condition 内部维护了一个**单向等待队列**（与 AQS 主队列独立）：

```
firstWaiter → Node → Node → Node → lastWaiter
              ↓        ↓        ↓
            thread   thread   thread
```

- `await()` 流程：
  1. 将当前线程封装为 Node（waitStatus = CONDITION）加入 Condition 队列
  2. 完全释放锁（state 归零，恢复释放前的状态）
  3. `LockSupport.park()` 挂起
  4. 被 signal 唤醒后，从 Condition 队列 **转移到 AQS 主队列**
  5. 重新竞争锁

- `signal()` 流程：
  1. 将 Condition 队列的 firstWaiter 移到 AQS 主队列尾部
  2. 等待该节点被 AQS 的 unparkSuccessor 唤醒

> **关键区别**：`signal()` 不释放锁，被 signal 的线程要等调用 signal 的线程释放锁后才能继续竞争。这与 `notify()` 的行为一致。

---

## VI. Lock vs synchronized 完整对比

### 6.1 对比总览表

| 维度 | synchronized | Lock（ReentrantLock） |
|------|-------------|----------------------|
| **实现层面** | JVM 层面（monitorenter/monitorexit 字节码） | Java API 层面（AQS + CAS） |
| **语法** | 语言关键字 | 接口/类 |
| **锁释放** | 自动释放（代码块结束或异常时） | 手动释放（必须在 finally 中 unlock） |
| **可中断** | 不支持 | 支持（lockInterruptibly） |
| **超时获取** | 不支持 | 支持（tryLock(timeout)） |
| **公平性** | 非公平（JVM 实现，不可控） | 可选（公平/非公平） |
| **条件变量** | 不支持（只有一个 wait set） | 支持（可创建多个 Condition） |
| **锁状态查询** | 不支持 | 支持（isLocked、isHeldByCurrentThread 等） |
| **重入性** | 可重入 | 可重入 |
| **性能（早期JDK）** | 较差 | 较好 |
| **性能（JDK 6+）** | 优化后接近 Lock | 与 synchronized 差距缩小 |

### 6.2 synchronized 的底层原理

```
synchronized 的锁存储在对象头（Mark Word）中：

对象头 Mark Word（64位 JVM，压缩Oops）：
┌─────────────────────────────────────────────┐
│  hashcode(25) │ age(4) │ biased(1) │ lock(2)│  ← 无锁状态
│  thread(54)   │ epoch(2)│ age(4) │ biased(1)│  ← 偏向锁
│  ptr(62)      │ lock(2)                       │  ← 轻量级锁（栈中 LockRecord）
│  ptr(62)      │ lock(2)                       │  ← 重量级锁（指向 Monitor 对象）
└─────────────────────────────────────────────┘
```

锁升级过程（JDK 6 之后）：

```
无锁 → 偏向锁 → 轻量级锁（自旋）→ 重量级锁（阻塞）
  ↑        ↑          ↑              ↑
 对象创建  单个线程    竞争激烈        自旋超时/竞争激烈
         偏向模式    CAS 尝试         Monitor 阻塞
```

### 6.3 代码风格对比

```java
// synchronized 写法
public synchronized void syncMethod() {
    // 自动获取和释放
    doSomething();
}

// 等价 Lock 写法
private final Lock lock = new ReentrantLock();

public void lockMethod() {
    lock.lock();
    try {
        doSomething();
    } finally {
        lock.unlock();  // 必须手动释放，通常在 finally 中
    }
}
```

### 6.4 何时选择哪个

```
选择策略：
┌─────────────────────────────────────────────────┐
│  需要可中断 / 超时 / 公平 / 多 Condition？       │
│     │                                            │
│     ├── 是 → 用 ReentrantLock                    │
│     │                                            │
│     └── 否 → 优先用 synchronized（更简洁）       │
│              JDK 6+ 性能差距很小                  │
└─────────────────────────────────────────────────┘
```

---

## VII. 自旋锁与适应性自旋

### 7.1 什么是自旋锁

**自旋锁**：线程在获取锁失败时，不立即阻塞（不进入操作系统级别的阻塞），而是执行一个**忙循环**（spin loop）不断尝试获取锁。

```java
// 自旋锁伪代码
public class SpinLock {
    private final AtomicReference<Thread> owner = new AtomicReference<>();

    public void lock() {
        Thread current = Thread.currentThread();
        // 不断 CAS 尝试获取锁
        while (!owner.compareAndSet(null, current)) {
            // 自旋等待 —— 空转
        }
    }

    public void unlock() {
        owner.compareAndSet(Thread.currentThread(), null);
    }
}
```

### 7.2 自旋锁的优缺点

| 优点 | 缺点 |
|------|------|
| 避免线程上下文切换开销 | 占用 CPU 时间片（忙等消耗 CPU） |
| 适合短临界区（锁持有时间很短） | 长临界区会浪费大量 CPU |
| 在多核 CPU 上效果好 | 单核 CPU 上无效（持有者无法运行） |

### 7.3 JDK 中的自旋

JDK 中的自旋锁出现在多个层次：

#### 7.3.1 synchronized 的轻量级锁阶段

当锁升级为轻量级锁时，线程会在用户态自旋尝试 CAS 获取：

```
CAS 获取锁
    │
    ├── 成功 → 进入临界区
    │
    └── 失败
         │
         ├── 自旋（默认 10 次，-XX:PreBlockSpin 控制）
         │    │
         │    ├── 期间再次 CAS → 成功 → 进入临界区
         │    │
         │    └── 自旋结束仍未获取 → 膨胀为重量级锁
         │
         └── 重量级锁 → 线程阻塞（OS 级别）
```

#### 7.3.2 AQS 中的自旋

AQS 在 `acquireQueued()` 中也有自旋逻辑：

```java
final boolean acquireQueued(Node node, int arg) {
    boolean failed = true;
    try {
        boolean interrupted = false;
        for (;;) {  // ← 自旋循环
            final Node p = node.predecessor();
            // 如果前驱是 head，再试一次获取锁
            if (p == head && tryAcquire(arg)) {
                setHead(node);
                p.next = null;
                failed = false;
                return interrupted;
            }
            // shouldParkAfterFailedAcquire 决定是否挂起
            if (shouldParkAfterFailedAcquire(p, node))
                parkAndCheckInterrupt();  // ← 挂起（退出自旋）
        }
    } finally {
        if (failed) cancelAcquire(node);
    }
}
```

这里的关键点：**不会无限自旋**。当 `shouldParkAfterFailedAcquire` 返回 true 时，线程就会被 `park()` 挂起，从自旋转为阻塞。

### 7.4 适应性自旋（Adaptive Spinning）

JDK 6 引入了**适应性自旋**：自旋的次数不再固定，而是根据**前一次在同一个锁上的自旋时间**和**锁拥有者的状态**来动态决定。

```
适应性自旋策略：

┌─────────────────────────────────────────────────┐
│  上次自旋成功获取锁 → 这次多自旋一会儿           │
│  上次自旋失败 → 这次少自旋或不自旋，直接阻塞     │
│                                                  │
│  JVM 会学习每个锁的"自旋历史"                    │
└─────────────────────────────────────────────────┘
```

相关 JVM 参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-XX:+UseSpinning` | 开启自旋（JDK 6 默认开启） | 开启 |
| `-XX:PreBlockSpin` | 自旋次数（JDK 7 之后由 JVM 自适应控制） | 10 |
| `-XX:+UseBiasedLocking` | 开启偏向锁（JDK 15 默认关闭） | 关闭 |

### 7.5 自旋锁 vs 阻塞锁 性能对比场景

```
场景 A：临界区极短（纳秒到微秒级）
┌──────────────────────────────────────────┐
│  自旋锁 >> 阻塞锁                        │
│  原因：上下文切换（几微秒）> 锁持有时间   │
└──────────────────────────────────────────┘

场景 B：临界区较长（毫秒级或更久）
┌──────────────────────────────────────────┐
│  阻塞锁 >> 自旋锁                        │
│  原因：自旋浪费 CPU，阻塞让出 CPU 给其他  │
│        线程执行更有价值的工作             │
└──────────────────────────────────────────┘

场景 C：竞争激烈 + 锁持有时间不定
┌──────────────────────────────────────────┐
│  适应性自旋 + 阻塞 = 最佳选择            │
│  JDK 默认策略                            │
└──────────────────────────────────────────┘
```

### 7.6 实际建议

```
使用建议：
1. 大多数场景：直接使用 synchronized 或 ReentrantLock
   → JVM 内部已自适应处理自旋

2. 极端低延迟场景：考虑
   - 自旋锁（自己实现或使用第三方库）
   - Lock-Free 数据结构（AtomicReference、ConcurrentLinkedQueue）
   - Disruptor（Ring Buffer + 自旋等待策略）

3. 避免自己写 naive 的 while(true) 自旋
   → 使用 Thread.onSpinWait() (JDK 9+) 提示 CPU 优化
   → 或使用 LockSupport.parkNanos(1) 让出时间片
```

```java
// JDK 9+ 自旋提示
while (!casOperation()) {
    Thread.onSpinWait();  // 告诉 CPU：我在自旋，可以优化
}
```

---

> **总结**：AQS 是 JUC 锁的基石，通过 state + CLH 队列实现了统一的同步器框架。ReentrantLock 在其上实现了可重入独占锁，ReentrantReadWriteLock 拆分了读写场景，StampedLock 进一步提供了乐观读优化。选择锁时，优先考虑简单性（synchronized），在需要高级特性时再使用 Lock 体系。
