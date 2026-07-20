<!--
question:
  id: 01.java-replace-synchronized-with-atomic
  topic: 01.java
  difficulty: ⭐⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [01.java, replace, synchronized]
-->

# 并发编程优化：Atomic类替代synchronized深度解析

## 引子：同一个计数器，性能差 10 倍

```java
// 方式 1：synchronized
public class SyncCounter {
    private long count = 0;
    public synchronized void increment() { count++; }
}

// 方式 2：Atomic
public class AtomicCounter {
    private AtomicLong count = new AtomicLong(0);
    public void increment() { count.incrementAndGet(); }
}

// 10 个线程各执行 100 万次
// synchronized: ~800ms
// Atomic:       ~80ms  ← 快了 10 倍！
```

为什么 Atomic 比 synchronized 快这么多？

核心区别：**synchronized 让其他线程"睡觉"（阻塞），Atomic 让其他线程"重试"（CAS 自旋）**。

---

> 📚 **前置知识**：[Atomic](../../../01.java/concurrency/atomic/README.md) | [synchronized](../../../01.java/concurrency/synchronized/README.md)

## 一、核心原理

`synchronized`和`java.util.concurrent.atomic`提供两种不同的线程安全机制。理解底层原理、适用场景和性能特征是编写高效并发代码的关键。

**本质对比：**

| **维度** | **synchronized** | **Atomic类** |
|---------|-----------------|--------------|
| **锁类型** | 悲观锁（阻塞） | 乐观锁（CAS自旋） |
| **实现机制** | Monitor+队列 | Unsafe.compareAndSwapInt/Long/Object |
| **线程状态** | BLOCKED→WAITING | RUNNABLE（自旋不挂起） |
| **上下文切换** | 用户态↔内核态（昂贵） | 纯用户态 |
| **粒度** | 代码块/方法 | 单个变量 |
| **复合操作** | 天然支持 | 需额外处理 |
| **低竞争性能** | 中等 | 高（无阻塞） |
| **高竞争性能** | 较好 | 差（CPU空转） |

**CAS（Compare-And-Swap）原理：**
```text
三要素：V(内存值)、A(预期值)、B(新值)
if (V == A) { V = B; return true; } else { return false; }
// 映射到CPU的CMPXCHG指令，硬件保证原子性
```

**锁升级机制（Java 1.6+）：**
```text
无锁 → 偏向锁 → 轻量级锁 → 重量级锁

1. 偏向锁：单线程访问时Mark Word记录线程ID，后续进入无需CAS
2. 轻量级锁：多线程交替访问，通过CAS将Mark Word替换为Lock Record指针
3. 重量级锁：真正竞争时，依赖OS Mutex Lock，未获取线程BLOCKED

JDK8默认：偏向锁延迟4秒启动
```

**volatile与Atomic的关系：**
```java
public class AtomicInteger {
    private volatile int value;  // volatile保证可见性
    public final boolean compareAndSet(int expect, int update) {
        return unsafe.compareAndSwapInt(this, valueOffset, expect, update);  // CAS保证原子性
    }
}
// volatile单独使用：volatile int count; count++; ❌ 不是原子操作（read-modify-write三步）
```

## 二、代码示例

**1. 计数器对比**

```java
// synchronized
static class SyncCounter {
    private int count = 0;
    public synchronized void increment() { count++; }
    public synchronized int get() { return count; }
}

// AtomicInteger
static class AtomicCounter {
    private AtomicInteger count = new AtomicInteger(0);
    public void increment() { count.incrementAndGet(); }
    public int get() { return count.get(); }
}

// 性能测试（8线程，1000万次递增）
// synchronized: 50 ns/op; AtomicInteger: 20 ns/op → Atomic快2.5倍
```

**2. ABA问题及解决**

```java
// ABA问题演示
AtomicInteger balance = new AtomicInteger(100);
// T1: 读100，准备CAS为50；T2: 100→50→100；T1: CAS成功但状态已变

// 解决1：AtomicStampedReference（带版本号）
AtomicStampedReference<Integer> ref = new AtomicStampedReference<>(100, 1);
int[] stamp = new int[1];
Integer expected = ref.get(stamp);
ref.compareAndSet(expected, 50, stamp[0], stamp[0]+1);  // 同时匹配值和版本

// 解决2：AtomicMarkableReference（带标记位）
AtomicMarkableReference<String> state = new AtomicMarkableReference<>("ACTIVE", false);
state.compareAndSet(expected, expected, false, true);  // 标记为删除
```

**3. 无锁数据结构：栈**

```java
public class LockFreeStack<T> {
    private static class Node<T> { final T item; Node<T> next; Node(T i) { this.item = i; } }
    private final AtomicReference<Node<T>> top = new AtomicReference<>();
    
    public void push(T item) {
        Node<T> newHead = new Node<>(item);
        do { newHead.next = top.get(); } while (!top.compareAndSet(newHead.next, newHead));
    }
    
    public T pop() {
        Node<T> oldHead;
        do { oldHead = top.get(); if (oldHead == null) return null; } 
        while (!top.compareAndSet(oldHead, oldHead.next));
        return oldHead.item;
    }
}
```

**4. LongAdder：高竞争终极方案**

```java
// LongAdder原理：内部维护Cell数组，每个线程操作不同Cell，求和时累加
LongAdder adder = new LongAdder();
adder.increment();  // 高并发下比AtomicLong快2-3倍

// 测试（16线程，1亿次递增）
// AtomicLong: 5234ms; LongAdder: 1876ms → 快2.79倍
```

**5. 状态标志**

```java
public class WorkerThread extends Thread {
    private final AtomicBoolean running = new AtomicBoolean(true);
    @Override public void run() { while (running.get()) doWork(); }
    public void stopGracefully() { running.set(false); }
}
// 使用
WorkerThread w = new WorkerThread(); w.start();
Thread.sleep(5000); w.stopGracefully(); w.join();
```

## 三、常见陷阱

**陷阱1：用Atomic实现复合操作**
```java
// ❌ check-then-act不是原子的
if (count.get() < 100) count.incrementAndGet();  // check和act之间可能被干扰
// ✅ 原子复合操作
count.updateAndGet(c -> c < 100 ? c + 1 : c);
// 或CAS循环
while (true) { int c = count.get(); if (c >= 100) break; if (count.compareAndSet(c, c+1)) break; }
```

**陷阱2：高竞争下CAS自旋导致CPU飙升**
```java
// ❌ 100线程竞争同一变量，99%的CAS失败，CPU空转
AtomicInteger shared = new AtomicInteger(0);
for (int i=0; i<100; i++) new Thread(() -> { for (int j=0; j<1_000_000; j++) shared.incrementAndGet(); }).start();

// ✅ LongAdder（分段累加）
LongAdder adder = new LongAdder();
// ✅ 或ThreadLocal+定期合并
ThreadLocal<Integer> local = ThreadLocal.withInitial(() -> 0);
local.set(local.get()+1);
if (local.get() % 1000 == 0) { global.addAndGet(local.get()); local.set(0); }
```

**陷阱3：忽略内存可见性**
```java
// ❌ 普通变量：一个线程修改，其他可能看不到
private boolean flag = false;
new Thread(() -> flag = true).start();
while (!flag) {}  // 可能无限循环！

// ✅ volatile或Atomic
private volatile boolean flag = false;
private AtomicBoolean flag = new AtomicBoolean(false);
```

**陷阱4：AtomicReference误用**
```java
// ❌ 修改对象内部字段后CAS，引用没变
AtomicReference<User> ref = new AtomicReference<>(new User("Alice", 25));
User u = ref.get(); u.setAge(26);
ref.compareAndSet(u, u);  // 总是false（同一引用）

// ✅ 创建新对象
ref.compareAndSet(u, new User(u.getName(), 26));
// 或用immutable对象
record User(String name, int age) {}
```

## 四、最佳实践

**1. 选型决策**
```text
并发控制需求？
├── 单变量原子操作
│   ├── 低/中竞争 → AtomicInteger/AtomicReference
│   └── 高竞争（累加）→ LongAdder
├── 多变量复合操作 → synchronized / ReentrantLock
├── 条件等待 → synchronized（wait/notify）或ReentrantLock（tryLock/超时）
└── 简单状态标志 → AtomicBoolean / volatile
```

**2. 优先高层抽象**
```java
// ❌ 手动线程安全
class ManualCache { private final Map<String,String> cache = new HashMap<>();
    public synchronized String get(String k) { return cache.get(k); }}

// ✅ ConcurrentHashMap
ConcurrentMap<String,String> cache = new ConcurrentHashMap<>();
cache.computeIfAbsent(key, k -> loadFromDB(k));
```

**3. 监控CAS失败率**
```java
public class ConcurrencyMetrics {
    private final LongAdder casSuccess = new LongAdder(), casFailure = new LongAdder();
    public boolean trackedCAS(AtomicInteger a, int exp, int upd) {
        boolean ok = a.compareAndSet(exp, upd);
        if (ok) casSuccess.increment(); else casFailure.increment();
        return ok;
    }
    public double successRate() { long t = casSuccess.sum()+casFailure.sum(); return t==0?1:(double)casSuccess.sum()/t; }
}
```

## 五、面试话术

**面试官：synchronized和Atomic类的区别？**

回答要点：
1. **机制**：synchronized是悲观锁（阻塞），Atomic是乐观锁（CAS自旋）
2. **粒度**：synchronized保护代码块/方法；Atomic仅单变量
3. **性能**：低竞争时Atomic更快（无上下文切换）；高竞争时synchronized可能更好
4. **功能**：synchronized支持复合操作和条件等待；Atomic仅保证单操作原子性
5. **选择**：单变量用Atomic；复合操作用synchronized/ReentrantLock；高竞争累加用LongAdder

**面试官：什么是ABA问题？如何解决？**

回答要点：
- **定义**：值从A→B→A，CAS误判为未变化
- **危害**：可能导致错误状态转换
- **解决**：AtomicStampedReference加版本号；AtomicMarkableReference加标记位
- **实际影响**：无锁数据结构中较常见，简单计数器影响不大

**面试官：LongAdder为什么比AtomicLong快？**

回答要点：
- **核心思想**：空间换时间，Cell数组分散竞争
- **工作原理**：每个线程根据哈希操作不同Cell，减少CAS冲突
- **求和**：sum()遍历所有Cell累加
- **权衡**：占用更多内存，sum()不是强一致

## 六、交叉引用

- **相关主题**：[HashMap扩容](../hashmap-resizing/README.md) - ConcurrentHashMap并发扩容
- **延伸学习**：[Java synchronized锁升级](../synchronized-lock-upgrade/README.md) - 偏向锁/轻量级锁/重量级锁
- **数据库关联**：[MySQL事务隔离](../../../03.database/03-transaction/README.md)
- **分布式扩展**：[分布式锁](../../../04.system-design/02-distributed/distributed-lock/README.md) - Redis/ZooKeeper

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · replace-synchronized-with-atomic](../README.md)
