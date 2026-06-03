# Java 并发集合全面指南

> 目标：系统梳理 `java.util.concurrent` 包下的所有并发集合，理解各自底层原理、适用场景及选型策略。ConcurrentHashMap 已有专题，本章仅做简要引用。

---

## 一、ConcurrentHashMap（简要引用）

ConcurrentHashMap 是并发集合中最重要的成员，已有完整专题文档，详见 `collection/ConcurrentHashMap/README.md`。

```
核心要点速览：
  JDK 7：Segment 分段锁（ReentrantLock），并发度固定 16
  JDK 8：CAS + synchronized 桶级锁，读完全无锁（volatile）
  扩容：多线程协助 transfer，ForwardingNode 标记已迁移桶
  计数：baseCount + CounterCell[] 分段计数（类似 LongAdder）
  迭代：弱一致性，不抛 ConcurrentModificationException
```

### 快速对比表

| 集合 | 底层结构 | 线程安全方式 | 读性能 | 写性能 | 有序性 |
|------|----------|-------------|--------|--------|--------|
| ConcurrentHashMap | 数组+链表+红黑树 | CAS + synchronized | 无锁 | 桶级锁 | 无序 |
| CopyOnWriteArrayList | 数组 | 写时复制（ReentrantLock） | 无锁 | 全量复制 | 有序（插入序） |
| ConcurrentLinkedQueue | 链表 | CAS（无锁算法） | 无锁 | 无锁 | 有序（FIFO） |
| ArrayBlockingQueue | 数组 | ReentrantLock | 条件等待 | 条件等待 | 有序（FIFO） |
| ConcurrentSkipListMap | 跳表 | CAS + volatile | 无锁 | CAS | 有序（key 排序） |

---

## 二、CopyOnWriteArrayList（写时复制列表）

### 2.1 写时复制原理

```
核心思想：写入时不直接修改原数组，而是创建一份副本，
在副本上完成修改后，将引用指向新数组。

写时复制（Copy-On-Write, COW）流程：

  读操作 ──────────────────────────→ 直接读取原数组（无锁、无阻塞）
                                          │
  写操作 add(e) ──→ lock()  ──→ 复制原数组 ──→ 新数组末尾追加 ──→ setArray(新数组) ──→ unlock()
                                 │
                            原数组不变
                            (读线程继续使用)

  读线程 A：  [─── 读原数组 ───]
  读线程 B：        [─── 读原数组 ───]
  写线程 C：               [lock → 复制 → 修改 → 切换引用 → unlock]

  读线程永远不会阻塞，写线程之间互斥
```

### 2.2 核心源码分析

```java
public class CopyOnWriteArrayList<E> implements List<E> {

    // 核心：volatile 数组引用
    private transient volatile Object[] array;

    final Object[] getArray() {
        return array;
    }

    final void setArray(Object[] a) {
        array = a;   // volatile 写，保证所有线程立即可见
    }

    // add 操作
    public boolean add(E e) {
        final ReentrantLock lock = this.lock;
        lock.lock();                    // 写线程互斥
        try {
            Object[] elements = getArray();
            int len = elements.length;
            Object[] newElements = Arrays.copyOf(elements, len + 1);  // 全量复制
            newElements[len] = e;                                    // 在副本上修改
            setArray(newElements);                                   // 切换引用
            return true;
        } finally {
            lock.unlock();
        }
    }

    // get 操作（完全无锁）
    public E get(int index) {
        return get(getArray(), index);   // 直接读取 volatile 数组
    }

    // 迭代器：基于快照，不会抛 ConcurrentModificationException
    public Iterator<E> iterator() {
        return new COWIterator<E>(getArray(), 0);
    }

    static final class COWIterator<E> implements ListIterator<E> {
        private Object[] snapshot;   // 迭代器创建时的数组快照
        private int cursor;

        // next() 直接读快照，不受后续修改影响
        public E next() {
            return (E) snapshot[cursor++];
        }
    }
}
```

### 2.3 内存开销分析

```
每次写操作的内存开销：

  原数组大小 = N
  新数组大小 = N + 1
  临时内存 = N + (N + 1) = 2N + 1  （新旧数组同时存在）

  示例：
    列表有 10000 个元素，每次 add 都要复制 10000 个引用
    写入 100 次 → 复制 100 × 10000 = 1,000,000 次引用操作

  GC 压力：
    旧数组成为垃圾 → 频繁 GC
    列表越大，复制和 GC 开销越大
```

### 2.4 适用场景

```
最适合的场景（读多写少，写操作极少）：

  1. 配置列表：启动时加载一次，运行时几乎不修改
     例：黑名单列表、允许的 IP 列表、功能开关列表

  2. 监听器列表：注册/注销监听器的频率远低于触发频率
     例：事件监听器集合、观察者模式中的订阅者列表

  3. 快照读取：需要保证遍历时数据不被修改
     例：遍历在线用户列表（遍历期间用户上下线不影响本次遍历）

不适合的场景：

  1. 频繁写入 → 全量复制性能差
  2. 大列表   → 内存和 GC 压力巨大
  3. 强一致性 → 读操作可能看不到最新的写
```

### 2.5 使用示例

```java
// 监听器模式的经典用法
public class EventBus {
    // 读远多于写：addListener/removeListener 很少，fireEvent 很频繁
    private final CopyOnWriteArrayList<Listener> listeners = new CopyOnWriteArrayList<>();

    public void addListener(Listener l) {
        listeners.add(l);
    }

    public void removeListener(Listener l) {
        listeners.remove(l);
    }

    public void fireEvent(Event e) {
        // 遍历时不会抛 ConcurrentModificationException
        // 遍历过程中注册/注销的监听器本次看不到（快照语义）
        for (Listener listener : listeners) {
            listener.onEvent(e);
        }
    }
}

// 配置列表
CopyOnWriteArrayList<String> blackList = new CopyOnWriteArrayList<>();
blackList.add("192.168.1.100");
blackList.add("10.0.0.50");

// 安全检查（迭代器快照语义）
for (String ip : blackList) {
    if (isSuspicious(ip)) {
        block(ip);
    }
}
```

---

## 三、CopyOnWriteArraySet

### 3.1 原理

```
CopyOnWriteArraySet 内部持有一个 CopyOnWriteArrayList，
通过 addIfAbsent() 去重实现 Set 语义。

结构：

  CopyOnWriteArraySet<E>
    └── CopyOnWriteArrayList<E> list
          └── Object[] array（volatile）

  add(e):
    1. lock()
    2. 遍历原数组，检查 e 是否已存在（equals 比较）
    3. 已存在 → 返回 false
    4. 不存在 → 复制数组 → 追加 → setArray → unlock → 返回 true
```

### 3.2 核心源码

```java
public class CopyOnWriteArraySet<E> extends AbstractSet<E> {
    private final CopyOnWriteArrayList<E> al;

    public CopyOnWriteArraySet() {
        al = new CopyOnWriteArrayList<E>();
    }

    public boolean add(E e) {
        return al.addIfAbsent(e);   // 去重插入
    }

    // addIfAbsent 的简化逻辑
    public boolean addIfAbsent(E e) {
        final ReentrantLock lock = this.lock;
        lock.lock();
        try {
            Object[] elements = getArray();
            // 线性查找，O(n)
            for (int i = 0; i < elements.length; i++) {
                if (eq(e, elements[i]))  // eq 处理 null
                    return false;        // 已存在
            }
            // 不存在，复制并添加
            Object[] newElements = Arrays.copyOf(elements, elements.length + 1);
            newElements[elements.length] = e;
            setArray(newElements);
            return true;
        } finally {
            lock.unlock();
        }
    }
}
```

### 3.3 性能特征与对比

| 操作 | CopyOnWriteArraySet | Collections.synchronizedSet | ConcurrentHashMap.newKeySet() |
|------|---------------------|----------------------------|-------------------------------|
| add | O(n) + 全量复制 | O(1) + 全表锁 | O(1) + 桶级锁 |
| contains | O(n) 线性查找 | O(1) + 全表锁 | O(1) + 无锁（volatile） |
| remove | O(n) + 全量复制 | O(1) + 全表锁 | O(1) + 桶级锁 |
| 遍历 | 无锁快照 | 需要手动 synchronized | 弱一致性迭代 |
| 适用场景 | 极小集合 + 读多写少 | 不推荐 | **高并发 Set 首选** |

```java
// 推荐使用 ConcurrentHashMap.newKeySet() 替代 CopyOnWriteArraySet
Set<String> concurrentSet = ConcurrentHashMap.newKeySet();
concurrentSet.add("A");
concurrentSet.add("B");

// 底层：ConcurrentHashMap<String, Boolean>
// add → map.put(key, Boolean.TRUE)
// contains → map.containsKey(key)
// remove → map.remove(key)
```

---

## 四、ConcurrentLinkedQueue / ConcurrentLinkedDeque（无锁队列）

### 4.1 无锁算法基础

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

### 4.2 ConcurrentLinkedQueue 结构

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

### 4.3 核心源码分析

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

### 4.4 ConcurrentLinkedDeque

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

### 4.5 性能特征

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

## 五、BlockingQueue 体系

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

### 5.1 ArrayBlockingQueue（有界数组阻塞队列）

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

### 5.2 LinkedBlockingQueue（可选有界链表阻塞队列）

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

### 5.3 PriorityBlockingQueue（优先级阻塞队列）

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

### 5.4 DelayQueue（延迟队列）

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

### 5.5 SynchronousQueue（同步队列，零容量）

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

### 5.6 LinkedTransferQueue（传输队列）

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

### 5.7 BlockingQueue 方法对比

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

### 5.8 BlockingQueue 汇总对比

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

## 六、ConcurrentSkipListMap / ConcurrentSkipListSet（跳表）

### 6.1 跳表（Skip List）原理

```
跳表是一种可以替代红黑树的概率性数据结构，
通过多层链表实现 O(log n) 的查找、插入和删除。

ASCII 结构示意（4 层跳表）：

  Level 3 (最高层, 约 n/8 个节点):
  HEAD ──────────────────────→ [16] ──────────────────────→ null

  Level 2 (约 n/4 个节点):
  HEAD ────────→ [8] ────────→ [16] ────────→ [24] ────→ null

  Level 1 (约 n/2 个节点):
  HEAD ──→ [4] ──→ [8] ──→ [12] ──→ [16] ──→ [20] ──→ [24] → null

  Level 0 (基础层, 所有节点):
  HEAD → [1]→[2]→[3]→[4]→[5]→[6]→[7]→[8]→[9]→[10]→...→[24]→null

  查找 key=15 的过程（从最高层开始）：
    1. Level 3: HEAD → [16] → 16 > 15，不能前进，下降
    2. Level 2: [8] → [16] → 16 > 15，不能前进，下降
    3. Level 1: [12] → [16] → 16 > 15，不能前进，下降
    4. Level 0: [14] → [15] → 找到！

  查找路径：HEAD → 8 → 12 → 14 → 15
  比较次数 ≈ log₂(n)，而不是 O(n)
```

### 6.2 随机高度

```
每个新节点的高度是随机生成的（概率 1/2 增加一层）：

  新节点高度算法（简化）：
    level = 1
    while (random.nextBoolean() && level < MAX_LEVEL)
        level++
    return level

  概率分布：
    Level 1: 50%  的节点
    Level 2: 25%  的节点
    Level 3: 12.5% 的节点
    Level 4: 6.25% 的节点
    ...

  期望高度 ≈ log₂(n)
  查找期望时间复杂度 ≈ O(log n)
```

### 6.3 ConcurrentSkipListMap 结构

```
ConcurrentSkipListMap 的底层节点结构：

  多层索引 + 基础数据层，每层都是单向链表

  Node 结构：
    class Node<K,V> {
        final K key;
        volatile Object value;      // 值或标记删除
        volatile Node<K,V> next;    // 水平链接
    }

    class Index<K,V> {
        final Node<K,V> node;       // 指向的 Node
        final Index<K,V> down;      // 下一层 Index
        volatile Index<K,V> right;  // 水平链接
    }

  整体结构：
    HeadIndex (head)
      ↓ right → down → right → down → right → down
    [Index] → [Index] → [Index]
      ↓         ↓         ↓
    [Node] → [Node] → [Node] → [Node] → [Node]  ← 基础层（数据层）
```

### 6.4 无锁操作

```
ConcurrentSkipListMap 使用 CAS 实现无锁的插入和删除：

  插入流程：
    1. 从最高层开始，逐层找到插入位置（最右侧 < key 的节点）
    2. 在基础层（Level 0）CAS 插入新节点
    3. 如果新节点有高层索引，从下到上逐层 CAS 插入索引
    4. 如果最高层需要扩展，CAS 更新 Head

  删除流程：
    1. 标记删除（value 设为特殊标记 SELF_KEY）
    2. 从右到左 CAS 删除（跳过已标记节点）
    3. 惰性删除：物理删除可能延迟，不影响正确性

  并发安全：
    - 所有链接修改都用 CAS
    - 删除先标记后删除（两步操作）
    - 读操作看到已删除节点会自动跳过
```

### 6.5 核心特性

```java
public class ConcurrentSkipListMap<K,V>
        extends AbstractMap<K,V>
        implements ConcurrentNavigableMap<K,V> {

    // 常用操作（全部线程安全）
    V put(K key, V value);
    V get(Object key);
    V remove(Object key);

    // 有序操作
    K firstKey();             // 最小 key
    K lastKey();              // 最大 key
    K ceilingKey(K key);      // ≥ key 的最小 key
    K floorKey(K key);        // ≤ key 的最大 key
    K higherKey(K key);       // > key 的最小 key
    K lowerKey(K key);        // < key 的最大 key

    // 子视图（全部是并发安全的）
    ConcurrentNavigableMap<K,V> subMap(K from, K to);
    ConcurrentNavigableMap<K,V> headMap(K to);
    ConcurrentNavigableMap<K,V> tailMap(K from);

    // 批量操作
    int size();               // 近似值（不精确，高并发时）
    boolean isEmpty();
    void clear();
}
```

```
性能特征：

  操作        | 平均      | 最差
  ───────────|──────────|──────────
  查找        | O(log n) | O(n)（极端退化）
  插入        | O(log n) | O(n)
  删除        | O(log n) | O(n)
  范围查询    | O(log n + k) | O(n + k)

  与 TreeMap 对比：

    维度         | ConcurrentSkipListMap | TreeMap
    ────────────|───────────────────────|──────────
    线程安全     | 是（CAS）              | 否
    底层结构     | 跳表                    | 红黑树
    有序性       | 是                      | 是
    空间开销     | 略高（多层索引）         | 低
    内存局部性   | 差（节点分散）           | 好
    并发性能     | 高（无锁）              | 需要外部同步
```

### 6.6 ConcurrentSkipListSet

```
ConcurrentSkipListSet 内部持有一个 ConcurrentSkipListMap。

public class ConcurrentSkipListSet<E> extends AbstractSet<E>
        implements NavigableSet<E> {

    private final ConcurrentNavigableMap<E,Object> m;
    private static final Object PRESENT = new Object();

    public ConcurrentSkipListSet() {
        m = new ConcurrentSkipListMap<E,Object>();
    }

    public boolean add(E e) {
        return m.putIfAbsent(e, PRESENT) == null;
    }

    public boolean remove(Object o) {
        return m.remove(o, PRESENT);
    }

    public boolean contains(Object o) {
        return m.containsKey(o);
    }
}

// 使用示例
ConcurrentSkipListSet<Integer> set = new ConcurrentSkipListSet<>();
set.add(5);
set.add(2);
set.add(8);
set.add(1);

// 有序遍历
for (int n : set) {
    System.out.println(n);  // 1, 2, 5, 8
}

// 范围查询
NavigableSet<Integer> sub = set.subSet(2, true, 6, true);  // [2, 5]
```

---

## 七、并发集合选型指南

### 7.1 按数据结构维度选型

```
需要 Map 时：
  ┌─────────────────────────────────────────────────┐
  │ 需要有序？                                       │
  │   ├─ 是 → ConcurrentSkipListMap                 │
  │   └─ 否 → 需要 key 可以为 null？                 │
  │             ├─ 是 → Collections.synchronizedMap  │
  │             └─ 否 → ConcurrentHashMap（首选）    │
  └─────────────────────────────────────────────────┘

需要 List 时：
  ┌─────────────────────────────────────────────────┐
  │ 写操作频繁吗？                                    │
  │   ├─ 是 → 不用并发 List（改用 Queue/Deque）      │
  │   └─ 否 → 读远多于写？                           │
  │             ├─ 是 → CopyOnWriteArrayList         │
  │             └─ 否 → Collections.synchronizedList │
  └─────────────────────────────────────────────────┘

需要 Queue 时：
  ┌─────────────────────────────────────────────────┐
  │ 需要阻塞等待？                                    │
  │   ├─ 是 → 需要容量限制？                          │
  │   │         ├─ 固定容量 → ArrayBlockingQueue      │
  │   │         ├─ 可选容量 → LinkedBlockingQueue     │
  │   │         ├─ 优先级   → PriorityBlockingQueue   │
  │   │         ├─ 延迟执行 → DelayQueue              │
  │   │         ├─ 零容量   → SynchronousQueue        │
  │   │         └─ 直接传递 → LinkedTransferQueue     │
  │   └─ 否 → 需要双端操作？                           │
  │             ├─ 是 → ConcurrentLinkedDeque          │
  │             └─ 否 → ConcurrentLinkedQueue          │
  └─────────────────────────────────────────────────┘

需要 Set 时：
  ┌─────────────────────────────────────────────────┐
  │ 需要有序？                                       │
  │   ├─ 是 → ConcurrentSkipListSet                  │
  │   └─ 否 → ConcurrentHashMap.newKeySet()（首选）  │
  │             读极多写极少 → CopyOnWriteArraySet     │
  └─────────────────────────────────────────────────┘
```

### 7.2 按场景维度选型

| 场景 | 推荐集合 | 原因 |
|------|----------|------|
| 高并发缓存 | ConcurrentHashMap | O(1) 查找，桶级锁 |
| 监听器集合 | CopyOnWriteArrayList | 遍历无锁，修改极少 |
| 生产者-消费者（有界） | ArrayBlockingQueue | 固定容量，防止内存溢出 |
| 生产者-消费者（高吞吐） | LinkedBlockingQueue | 双锁并行，高吞吐 |
| 任务调度（优先级） | PriorityBlockingQueue | 按优先级出队 |
| 订单超时取消 | DelayQueue | 按到期时间出队 |
| CachedThreadPool | SynchronousQueue | 零延迟传递 |
| 有序并发 Map | ConcurrentSkipListMap | O(log n) + 有序 |
| 并发 Set | ConcurrentHashMap.newKeySet() | 底层 CHM，高性能 |
| 无锁高吞吐队列 | ConcurrentLinkedQueue | CAS 无锁，不阻塞 |
| 线程安全计数器 | LongAdder / AtomicLong | 不是集合，但常配合使用 |

### 7.3 性能对比速查

```
  ┌──────────────────────┬──────┬──────┬──────┬────────┬──────────┐
  │ 集合                  │ 查找  │ 插入  │ 删除  │ 遍历    │ 内存开销  │
  ├──────────────────────┼──────┼──────┼──────┼────────┼──────────┤
  │ ConcurrentHashMap    │ O(1) │ O(1) │ O(1) │ 弱一致  │ 中等      │
  │ CopyOnWriteArrayList │ O(n) │ O(n)*│ O(n)*│ 快照    │ 高（复制）│
  │ ConcurrentLinkedQ    │ N/A  │ O(1) │ O(1) │ 弱一致  │ 低        │
  │ ArrayBlockingQueue   │ N/A  │ O(1)†│ O(1)†│ N/A     │ 低        │
  │ LinkedBlockingQueue  │ N/A  │ O(1)†│ O(1)†│ N/A     │ 中        │
  │ PriorityBlockingQ    │ N/A  │ O(logn)│O(logn)│ N/A    │ 低        │
  │ ConcurrentSkipListMap│O(logn)│O(logn)│O(logn)│ 弱一致  │ 较高      │
  └──────────────────────┴──────┴──────┴──────┴────────┴──────────┘

  * = 写时复制，实际开销 = O(N) 复制 + O(1) 追加
  † = 阻塞操作，O(1) 指不考虑等待时间
  N/A = 队列不支持随机查找
```

### 7.4 常见陷阱

```
陷阱 1：用 CopyOnWriteArrayList 存储频繁修改的数据
  → 每次修改都全量复制，大列表会 OOM

陷阱 2：用 ConcurrentLinkedQueue.size() 做业务判断
  → size() 是 O(n) 遍历计数，高并发下结果不准确

陷阱 3：认为 ConcurrentHashMap 的复合操作是原子的
  → if (!map.containsKey(k)) map.put(k, v) 不是原子操作
  → 应该用 putIfAbsent 或 computeIfAbsent

陷阱 4：用 SynchronousQueue 做缓冲
  → 容量为零，生产者和消费者必须同时在场

陷阱 5：忽略 BlockingQueue 的容量限制
  → LinkedBlockingQueue 默认无界（Integer.MAX_VALUE）
  → 生产者快于消费者时会 OOM

陷阱 6：用 Collections.synchronizedList 做遍历时修改
  → 遍历时修改会抛 ConcurrentModificationException
  → 应该用迭代器的 remove 方法或 CopyOnWriteArrayList

陷阱 7：认为 ConcurrentSkipListMap 的 size() 精确
  → 高并发时 size() 返回近似值
  → 需要精确计数时自行维护 AtomicLong
```

### 7.5 最佳实践总结

```
1. 优先选择无锁/细粒度锁的集合（ConcurrentHashMap, ConcurrentLinkedQueue）
2. 写时复制集合只适用于写极少的场景（配置列表、监听器集合）
3. 生产者-消费者场景用 BlockingQueue，不要用手动 wait/notify
4. 需要有序时用 ConcurrentSkipListMap，不要用 ConcurrentHashMap + 外部排序
5. 原子操作优先用集合自带的方法（putIfAbsent, compute, merge）
6. 遍历时不要假设集合状态不变（弱一致性语义）
7. 容量限制很重要：无界队列在背压场景下会导致 OOM
8. 注意 null 处理：大多数并发集合不允许 null 元素
```
