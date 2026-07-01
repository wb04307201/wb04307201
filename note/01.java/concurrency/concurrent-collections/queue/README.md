<!--
module:
  parent: java
  slug: java/queue
  type: article
  category: 主模块子文章
  summary: 掌握 ConcurrentLinkedQueue 的无锁 CAS 算法和 BlockingQueue 体系的完整实现，理解各自底层原理与适用场景。
-->

# 并发队列

> 目标：掌握 ConcurrentLinkedQueue 的无锁 CAS 算法和 BlockingQueue 体系的完整实现，理解各自底层原理与适用场景。

---
## 引言：反直觉代码

并发队列 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、ConcurrentLinkedQueue / ConcurrentLinkedDeque（无锁队列）

### 1.1 无锁算法基础

```
ConcurrentLinkedQueue 使用 CAS（Compare-And-Swap）实现无锁队列，
不依赖任何锁（synchronized / ReentrantLock 都没有）。

核心思想：
  1. 每个节点 volatile 引用 next
  2. 入队：CAS 修改尾节点的 next 指向新节点
  3. 出队：CAS 修改头节点的 next 指向下一个节点
  4. CAS 失败 → 自旋重试（不阻塞）

  线程 A ──→ CAS 修改 tail.next ──→ 成功 ──→ 完成
  线程 B ──→ CAS 修改 tail.next ──→ 失败 ──→ 自旋重试 ──→ 成功
  线程 C ──→ CAS 修改 tail.next ──→ 失败 ──→ 自旋重试 ──→ 成功
```

### 1.2 ConcurrentLinkedQueue 结构

```
入队示意（Michael-Scott 无锁队列算法）：

  初始状态：
    head ──→ [dummy] ──→ null  ← tail

  线程 A 入队 "A"：
    1. 创建新节点 newNode("A")
    2. CAS: tail.next = newNode
    3. CAS: tail = newNode（可能延迟执行，即 tail 不一定总是最新）

    head ──→ [dummy] ──→ [A] ──→ null  ← tail

  线程 B 入队 "B"：
    head ──→ [dummy] ──→ [A] ──→ [B] ──→ null  ← tail

  出队 "A"：
    1. p = head.next（跳过 dummy）
    2. item = p.item
    3. CAS: head = p（原 head.next 成为新 dummy）

    head ──→ [A(dumped)] ──→ [B] ──→ null  ← tail
                    ↑ item=null（已出队标记）
```

### 1.3 核心源码分析

```java
public class ConcurrentLinkedQueue<E> extends AbstractQueue<E> {

    // head 和 tail 都是 volatile
    private transient volatile Node<E> head;
    private transient volatile Node<E> tail;

    static class Node<E> {
        volatile E item;
        volatile Node<E> next;

        boolean casItem(E cmp, E val) {
            return UNSAFE.compareAndSwapObject(this, itemOffset, cmp, val);
        }

        boolean casNext(Node<E> cmp, Node<E> val) {
            return UNSAFE.compareAndSwapObject(this, nextOffset, cmp, val);
        }
    }

    public boolean offer(E e) {
        Objects.requireNonNull(e);
        final Node<E> newNode = new Node<E>(e);

        for (Node<E> t = tail, p = t;;) {
            Node<E> q = p.next;
            if (q == null) {
                // p 是尾节点，CAS 插入
                if (p.casNext(null, newNode)) {
                    // 插入成功，tail 可能延迟更新
                    if (p != t)  // 如果 tail 已经落后，更新它
                        casTail(t, newNode);
                    return true;
                }
                // CAS 失败 → 其他线程先插入了，重试
            }
            else if (p == q) {
                // 遇到哨兵节点（已出队的节点 next 指向自己）
                // 说明 tail 已经落后了，重新从 tail 开始
                p = (t != (t = tail)) ? t : head;
            }
            else {
                // p 不是尾节点，tail 落后了，尝试更新 tail
                p = (p != t && t != (t = tail)) ? t : q;
            }
        }
    }

    public E poll() {
        restartFromHead:
        for (;;) {
            for (Node<E> h = head, p = h, q;;) {
                E item = p.item;

                if (item != null && p.casItem(item, null)) {
                    // CAS 成功，取出元素
                    if (p != h)  // head 落后了，更新
                        updateHead(h, ((q = p.next) != null) ? q : p);
                    return item;
                }
                else if ((q = p.next) == null) {
                    // 队列为空
                    updateHead(h, p);
                    return null;
                }
                else if (p == q) {
                    // 遇到哨兵节点
                    continue restartFromHead;
                }
                else {
                    // 继续往后找
                    p = q;
                }
            }
        }
    }
}
```

### 1.4 ConcurrentLinkedDeque

```
ConcurrentLinkedDeque 是双端队列版本，支持从两端入队和出队。

操作对比：

  操作              | ConcurrentLinkedQueue | ConcurrentLinkedDeque
  ─────────────────|───────────────────────|───────────────────────
  入队（尾部）       | offer(e)              | addLast(e) / offerLast(e)
  出队（头部）       | poll()                | pollFirst()
  入队（头部）       | 不支持                 | addFirst(e) / offerFirst(e)
  出队（尾部）       | 不支持                 | pollLast()
  底层算法           | Michael-Scott         | 改进版无锁双端队列

  性能特点相同：
    - 无锁 CAS
    - 无界
    - 不允许 null
    - O(1) 入队/出队（摊销）
```

### 1.5 性能特征

```
ConcurrentLinkedQueue vs BlockingQueue（如 LinkedBlockingQueue）：

  ┌────────────────────────┬─────────────────────┬──────────────────────┐
  │ 特性                    │ ConcurrentLinkedQ    │ LinkedBlockingQueue  │
  ├────────────────────────┼─────────────────────┼──────────────────────┤
  │ 线程安全机制             │ CAS（无锁）          │ ReentrantLock        │
  │ 阻塞                    │ 不阻塞               │ 可阻塞               │
  │ size()                  │ O(n) 遍历计数         │ O(1) 维护计数         │
  │ isEmpty()               │ 不保证准确            │ 准确                 │
  │ 高吞吐（无竞争）         │ 极快                 │ 较快                 │
  │ 高吞吐（高竞争）         │ CAS 自旋消耗 CPU      │ 线程阻塞，CPU 友好    │
  │ 适用场景                 │ 短暂入队/出队         │ 生产者-消费者        │
  └────────────────────────┴─────────────────────┴──────────────────────┘

  关键区别：
    ConcurrentLinkedQueue：入队后立即返回，不等待消费者
    BlockingQueue：队列为空时 take() 会阻塞等待
```

---

## 二、BlockingQueue 体系

```
BlockingQueue 接口定义了支持阻塞操作的队列，
核心特征：队列空时 take 阻塞，队列满时 put 阻塞。

BlockingQueue 继承体系：

  Queue<E>
    └── BlockingQueue<E>
          ├── ArrayBlockingQueue         ← 有界数组 + 单锁
          ├── LinkedBlockingQueue        ← 可选有界链表 + 双锁
          ├── PriorityBlockingQueue      ← 无界堆 + 单锁
          ├── DelayQueue                 ← 延迟队列（基于 P.B.Q）
          ├── SynchronousQueue           ← 零容量（直接传递）
          └── LinkedTransferQueue        ← 链表 + 等待匹配

  双端阻塞队列：
  Deque<E>
    └── BlockingDeque<E>
          └── LinkedBlockingDeque        ← 双向阻塞队列
```

### 2.1 ArrayBlockingQueue（有界数组阻塞队列）

```
结构：

  ArrayBlockingQueue（容量固定，单 ReentrantLock）

  ┌───┬───┬───┬───┬───┬───┬───┬───┐
  │ 3 │ 5 │ 8 │   │   │   │   │   │  ← 固定大小数组（循环使用）
  └───┴───┴───┴───┴───┴───┴───┴───┘
    ↑           ↑
   takeIndex   putIndex

  单 ReentrantLock + 两个 Condition：
    lock
    ├── notEmpty  ← put/add 后 signal（通知 take 可以消费了）
    └── notFull   ← take/poll 后 signal（通知 put 可以生产了）
```

```java
// 核心字段
public class ArrayBlockingQueue<E> extends AbstractQueue<E>
        implements BlockingQueue<E>, java.io.Serializable {

    final Object[] items;           // 固定大小数组
    int takeIndex;                  // 下次 take 的位置
    int putIndex;                   // 下次 put 的位置
    int count;                      // 当前元素数量
    final ReentrantLock lock;       // 一把锁（读写共享）
    private final Condition notEmpty;
    private final Condition notFull;

    // put（队列满时阻塞）
    public void put(E e) throws InterruptedException {
        Objects.requireNonNull(e);
        final ReentrantLock lock = this.lock;
        lock.lockInterruptibly();
        try {
            while (count == items.length)
                notFull.await();     // 队列满，等待
            enqueue(e);              // 入队
        } finally {
            lock.unlock();
        }
    }

    // take（队列空时阻塞）
    public E take() throws InterruptedException {
        final ReentrantLock lock = this.lock;
        lock.lockInterruptibly();
        try {
            while (count == 0)
                notEmpty.await();    // 队列空，等待
            return dequeue();        // 出队
        } finally {
            lock.unlock();
        }
    }
}
```

```
特点：
  1. 有界：构造时必须指定容量，满了就不能再放
  2. 单锁：读写共用一把锁，put 和 take 不能并行
  3. 公平性：构造函数可指定 fair=true（FIFO 获取锁）
  4. 内存紧凑：基于数组，没有额外节点对象
  5. 适合场景：有明确容量限制的生产者-消费者
```

### 2.2 LinkedBlockingQueue（可选有界链表阻塞队列）

```
结构：

  LinkedBlockingQueue（可选容量上限，默认 Integer.MAX_VALUE，双锁）

  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
  │ 3   │───→│ 5   │───→│ 8   │───→│ 12  │───→ null
  └─────┘    └─────┘    └─────┘    └─────┘
     ↑  putLock                    ↑  takeLock
                                   各自独立，读写可并行
```

```java
// 双锁设计（生产者和消费者可以并行操作）
public class LinkedBlockingQueue<E> extends AbstractQueue<E>
        implements BlockingQueue<E> {

    final int capacity;              // 容量（默认 Integer.MAX_VALUE）
    final AtomicInteger count = new AtomicInteger();  // 元素计数
    transient Node<E> head;
    transient Node<E> last;          // 队尾

    private final ReentrantLock takeLock = new ReentrantLock();
    private final Condition notEmpty = takeLock.newCondition();

    private final ReentrantLock putLock = new ReentrantLock();
    private final Condition notFull = putLock.newCondition();

    // put 操作（用 putLock）
    public void put(E e) throws InterruptedException {
        if (e == null) throw new NullPointerException();
        int c = -1;
        Node<E> node = new Node<E>(e);
        final ReentrantLock putLock = this.putLock;
        final AtomicInteger count = this.count;
        putLock.lockInterruptibly();
        try {
            while (count.get() == capacity)
                notFull.await();      // 满了，等待
            enqueue(node);
            c = count.getAndIncrement();  // 原子 +1
            if (c + 1 < capacity)
                notFull.signal();     // 还有空间，唤醒其他生产者
        } finally {
            putLock.unlock();
        }
        if (c == 0)
            signalNotEmpty();       // 从无到有，通知消费者
    }

    // take 操作（用 takeLock）
    public E take() throws InterruptedException {
        E x;
        int c = -1;
        final AtomicInteger count = this.count;
        final ReentrantLock takeLock = this.takeLock;
        takeLock.lockInterruptibly();
        try {
            while (count.get() == 0)
                notEmpty.await();     // 空了，等待
            x = dequeue();
            c = count.getAndDecrement();  // 原子 -1
            if (c > 1)
                notEmpty.signal();    // 还有元素，唤醒其他消费者
        } finally {
            takeLock.unlock();
        }
        if (c == capacity)
            signalNotFull();          // 从满到不满，通知生产者
    }
}
```

```
ArrayBlockingQueue vs LinkedBlockingQueue：

  维度              | ArrayBlockingQueue       | LinkedBlockingQueue
  ─────────────────|──────────────────────────|──────────────────────────
  数据结构           | 数组                      | 链表
  容量               | 固定（必须指定）            | 可选（默认无界）
  锁                 | 单锁（读写互斥）            | 双锁（读写可并行）
  内存分配           | 预分配，紧凑                | 按需分配节点对象
  吞吐量             | 中等                      | 更高（双锁并行）
  GC 压力            | 低                        | 高（频繁创建/回收 Node）
  推荐场景           | 有明确容量限制             | 高吞吐 + 可接受无界
```

### 2.3 PriorityBlockingQueue（优先级阻塞队列）

```
结构：

  PriorityBlockingQueue（无界，基于二叉堆数组，单锁）

  内部数组（二叉堆）：
  ┌────┬────┬────┬────┬────┬────┬────┐
  │  1 │  3 │  2 │  7 │  5 │  4 │  6 │  ← 堆：array[0] 始终是最小值
  └────┴────┴────┴────┴────┴────┴────┘

  出队顺序（自然序 / Comparator）：
  take() → 1 → 2 → 3 → 4 → 5 → 6 → 7（不是 FIFO！）

  特点：
    1. 无界（自动扩容数组）
    2. 单 ReentrantLock
    3. 元素必须实现 Comparable 或提供 Comparator
    4. 不允许 null
    5. 相同优先级的元素出队顺序不确定
```

```java
public class PriorityBlockingQueue<E> extends AbstractQueue<E>
        implements BlockingQueue<E> {

    private transient Object[] queue;   // 二叉堆数组
    private transient int size;
    private transient ReentrantLock lock;
    private transient Condition notEmpty;

    // take 总是取出堆顶（最小）元素
    public E take() throws InterruptedException {
        final ReentrantLock lock = this.lock;
        lock.lockInterruptibly();
        try {
            while (size == 0)
                notEmpty.await();
            return dequeue();           // 取出堆顶，重新调整堆
        } finally {
            lock.unlock();
        }
    }
}

// 示例
PriorityBlockingQueue<Task> queue = new PriorityBlockingQueue<>();
queue.add(new Task(3, "普通任务"));
queue.add(new Task(1, "紧急任务"));
queue.add(new Task(2, "重要任务"));

queue.take();  // → "紧急任务"（优先级 1 最小，最先出队）
queue.take();  // → "重要任务"
queue.take();  // → "普通任务"
```

### 2.4 DelayQueue（延迟队列）

```
结构：

  DelayQueue（基于 PriorityBlockingQueue，元素实现 Delayed 接口）

  Delayed 接口：
    interface Delayed extends Comparable<Delayed> {
        long getDelay(TimeUnit unit);   // 返回剩余延迟时间
    }

  内部：
    DelayQueue
      └── PriorityBlockingQueue<Delayed>
            └── 按 getDelay() 排序（延迟最短的在堆顶）

  工作流程：
    1. 元素按延迟时间排序（最短延迟在堆顶）
    2. take() 时检查堆顶元素的 getDelay()
    3. 如果延迟未到 → 等待（线程阻塞）
    4. 延迟到期 → 取出元素

  时间线示意：

    t=0    t=5    t=10   t=15   t=20   t=25
    │      │      │      │      │      │
    ├─A(delay=10)──→ 可取出
           ├─B(delay=5)──→ 可取出
                 ├─C(delay=15)──→ 可取出

    出队顺序：B(5s) → A(10s) → C(15s)
```

```java
// 自定义延迟元素
class DelayedTask implements Delayed {
    private final long deadline;
    private final String name;

    public DelayedTask(String name, long delay, TimeUnit unit) {
        this.name = name;
        this.deadline = System.currentTimeMillis() + unit.toMillis(delay);
    }

    @Override
    public long getDelay(TimeUnit unit) {
        long remaining = deadline - System.currentTimeMillis();
        return unit.convert(remaining, TimeUnit.MILLISECONDS);
    }

    @Override
    public int compareTo(Delayed other) {
        return Long.compare(this.getDelay(TimeUnit.MILLISECONDS),
                            other.getDelay(TimeUnit.MILLISECONDS));
    }

    @Override
    public String toString() {
        return name + " (deadline=" + deadline + ")";
    }
}

// 使用
DelayQueue<DelayedTask> delayQueue = new DelayQueue<>();
delayQueue.add(new DelayedTask("任务A", 10, TimeUnit.SECONDS));
delayQueue.add(new DelayedTask("任务B", 5, TimeUnit.SECONDS));
delayQueue.add(new DelayedTask("任务C", 15, TimeUnit.SECONDS));

// take 会阻塞直到延迟到期
// 先取出 B（5s），再 A（10s），最后 C（15s）
```

```
典型场景：
  1. 缓存过期：放入时设 TTL，到期自动取出并清理
  2. 定时任务：延迟执行的任务放入队列，到期后触发
  3. 订单超时：下单后放入延迟队列，超时未支付自动取消
  4. 会话管理：用户会话到期自动失效
```

### 2.5 SynchronousQueue（同步队列，零容量）

```
核心特征：不存储元素，每个 put 必须等待一个 take，反之亦然。

  SynchronousQueue
    容量 = 0
    没有内部数据结构（不存储任何元素）

  put(e) ──→ 阻塞，等待某个线程调用 take()
  take() ──→ 阻塞，等待某个线程调用 put(e)

  线程 A（生产者）：         线程 B（消费者）：
    sq.put("data")  ───────→ sq.take()
         │                       │
         ├──── 直接传递 ──────────┤
         │     (不经过队列)       │
         ↓                       ↓
      返回成功               拿到 "data"
```

```java
public class SynchronousQueue<E> extends AbstractQueue<E>
        implements BlockingQueue<E> {

    // 两种模式
    // 1. 非公平（默认）：TransferStack（LIFO 栈）
    //    后等待的线程先匹配
    // 2. 公平：TransferQueue（FIFO 队列）
    //    先等待的线程先匹配

    // 构造函数
    public SynchronousQueue() {
        this(false);  // 默认非公平
    }

    public SynchronousQueue(boolean fair) {
        // fair=true  → TransferQueue（FIFO）
        // fair=false → TransferStack（LIFO）
    }
}

// 示例
SynchronousQueue<String> sq = new SynchronousQueue<>();

// 线程 A
new Thread(() -> {
    try {
        sq.put("Hello");  // 阻塞，直到有消费者
        System.out.println("已交付");
    } catch (InterruptedException e) {}
}).start();

// 线程 B
new Thread(() -> {
    try {
        String msg = sq.take();  // 阻塞，直到有生产者
        System.out.println("收到: " + msg);
    } catch (InterruptedException e) {}
}).start();
```

```
适用场景：
  1. 线程池：Executors.newCachedThreadPool() 使用 SynchronousQueue
     → 每个任务直接交给空闲线程，没有空闲就创建新线程
     → 不需要队列等待，任务必须立即被消费

  2. 直接传递：生产者和消费者直接交接数据，不经过中间缓冲
  3.  rendezvous（ rendez-vous 会合点）：两个线程在某个点同步

  不适合：
    - 需要缓冲的场景（容量为零）
    - 生产者和消费者速率不一致的场景
```

### 2.6 LinkedTransferQueue（传输队列）

```
LinkedTransferQueue 是最强大的阻塞队列，
结合了 SynchronousQueue 的直接传递和传统队列的缓冲能力。

新增方法：

  transfer(e)   → 阻塞直到有消费者取走元素（类似 SynchronousQueue.put）
  tryTransfer(e) → 如果有消费者立即返回 true，否则返回 false（不阻塞）
  tryTransfer(e, timeout, unit) → 等待超时后返回

  ┌────────────┬──────────────┬──────────────┬───────────────┐
  │ 方法        │ 队列有消费者  │ 队列无消费者  │ 是否阻塞       │
  ├────────────┼──────────────┼──────────────┼───────────────┤
  │ put(e)     │ 直接传递      │ 排队等待      │ 是（永久）     │
  │ offer(e)   │ 直接传递      │ 入队立即返回  │ 否            │
  │ transfer(e)│ 直接传递      │ 排队等待      │ 是（永久）     │
  │ tryTransfer│ 直接传递      │ 返回 false   │ 否            │
  └────────────┴──────────────┴──────────────┴───────────────┘
```

```java
LinkedTransferQueue<String> ltq = new LinkedTransferQueue<>();

// transfer：必须等到消费者
new Thread(() -> {
    System.out.println("等待消费者...");
    ltq.transfer("data");  // 阻塞，直到有线程 take
    System.out.println("消费者已取走");
}).start();

Thread.sleep(1000);

// 消费者
new Thread(() -> {
    String msg = ltq.take();  // 从 transfer 直接获取
    System.out.println("收到: " + msg);
}).start();

// tryTransfer：不等消费者
boolean success = ltq.tryTransfer("quick");  // 无消费者 → false
// 元素不入队，直接丢弃
```

### 2.7 BlockingQueue 方法对比

```
BlockingQueue 提供四类方法，行为各不相同：

  ┌────────────┬──────────┬───────────┬─────────────┬─────────────────┐
  │ 操作        │ 抛出异常  │ 特殊值     │ 阻塞         │ 超时              │
  ├────────────┼──────────┼───────────┼─────────────┼─────────────────┤
  │ 插入        │ add(e)   │ offer(e)  │ put(e)      │ offer(e,t,u)    │
  │ 移除        │ remove() │ poll()    │ take()      │ poll(t,u)       │
  │ 检查        │ element()│ peek()    │ —           │ —               │
  └────────────┴──────────┴───────────┴─────────────┴─────────────────┘

  插入：
    add(e)      → 满时抛 IllegalStateException
    offer(e)    → 满时返回 false
    put(e)      → 满时阻塞等待
    offer(e,t,u)→ 满时等待超时，超时返回 false

  移除：
    remove()    → 空时抛 NoSuchElementException
    poll()      → 空时返回 null
    take()      → 空时阻塞等待
    poll(t,u)   → 空时等待超时，超时返回 null

  检查：
    element()   → 空时抛异常（不删除）
    peek()      → 空时返回 null（不删除）
```

### 2.8 BlockingQueue 汇总对比

| 队列 | 容量 | 数据结构 | 锁机制 | 排序 | 典型场景 |
|------|------|----------|--------|------|----------|
| ArrayBlockingQueue | 有界 | 数组 | 单锁 | FIFO | 固定缓冲的生产者-消费者 |
| LinkedBlockingQueue | 可选有界 | 链表 | 双锁 | FIFO | 高吞吐生产者-消费者 |
| PriorityBlockingQueue | 无界 | 二叉堆 | 单锁 | 优先级 | 任务调度、优先级处理 |
| DelayQueue | 无界 | 堆（Delayed） | 单锁 | 延迟时间 | 缓存过期、定时任务 |
| SynchronousQueue | 零 | 无 | CAS+锁 | 无 | CachedThreadPool |
| LinkedTransferQueue | 无界 | 链表 | CAS+锁 | FIFO | 直接传递+缓冲混合 |
| LinkedBlockingDeque | 可选有界 | 链表 | 双锁 | 双端FIFO | 工作窃取、双端消费 |

---

## 相关章节

- [父目录：并发集合总览](../README.md)
- [写时复制集合](../copy-on-write/README.md)
- [跳表集合](../skip-list/README.md)
- [ConcurrentHashMap 专题](../../../../README.md)
