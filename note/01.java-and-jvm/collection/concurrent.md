<!--
module:
  parent: java
  slug: java/collection/concurrent
  type: article
  category: 主模块子文章
  summary: Java 并发集合原理与选型，覆盖 ConcurrentHashMap、CopyOnWriteArrayList、阻塞队列及常见并发陷阱。
-->

# 并发集合

> 目标：搞懂 ConcurrentHashMap 的实现原理，以及 Java 并发场景下各种集合类的选型。
>
> **系列导航**：[collection 系列索引](README.md) · [ArrayList](ArrayList/README.md) · [HashMap](hashmap.md) · [LinkedList](LinkedList/README.md) · [ConcurrentHashMap 专题](ConcurrentHashMap/README.md)

---

## 一、ConcurrentHashMap：JDK 7 vs JDK 8

### JDK 7：Segment 分段锁

```text
ConcurrentHashMap
├── Segment[0]  ← 每个 Segment 继承自 ReentrantLock
│   └── HashEntry[] table（独立的小 HashMap）
├── Segment[1]
│   └── HashEntry[] table
├── ...
└── Segment[15]  ← 默认 16 个 Segment
    └── HashEntry[] table

并发度 = Segment 数量 = 16（最多 16 个线程同时写）
读操作：无锁（volatile 保证可见性）
写操作：锁定目标 Segment，其他 Segment 不受影响
```

### JDK 8：CAS + synchronized

```text
ConcurrentHashMap
└── Node[] table（一个大的数组，和 HashMap 结构类似）
    ├── table[0] → null
    ├── table[1] → [K1,V1] → [K2,V2]  ← 链表
    ├── table[2] → 红黑树根节点        ← 链表长度 ≥ 8 时转换
    └── ...

并发度 = table.length（数组有多大，就有多少把"锁"）
读操作：无锁（volatile）
写操作：CAS 插入空桶 / synchronized 锁住链表或红黑树的头节点
```

### get() 为什么可以无锁

```java
// ConcurrentHashMap.get() 不加锁，靠 volatile 保证正确性
public V get(Object key) {
    Node<K,V>[] tab = table;          // volatile 读 table 引用
    Node<K,V> e = tabAt(tab, i);      // volatile 读桶头节点
    while (e != null) {
        if (e.hash == hash && e.key.equals(key))
            return e.val;              // volatile 读 val
        e = e.next;                    // volatile 读 next
    }
}
```

**Node 的三个关键字段都是 volatile**：
```java
static class Node<K,V> {
    final int hash;
    final K key;
    volatile V val;        // volatile ← 写操作修改后立即可见
    volatile Node<K,V> next; // volatile ← 链表结构变化立即可见
}
```

**加上 table 引用本身也是 volatile**，所以 get() 不需要加锁就能读到最新数据。这是 ConcurrentHashMap 读性能极高的核心原因。

> **例外**：如果 get() 遍历过程中遇到 `ForwardingNode`（扩容期间的占位节点），会转发到新 table 查找，这个过程也是无锁的。

### 为什么从分段锁改成 CAS + synchronized

| | JDK 7 分段锁 | JDK 8 CAS + synchronized |
|---|---|---|
| **并发度** | 固定 16（Segment 数量） | table.length（初始 16，随扩容增大） |
| **锁粒度** | 一个 Segment（包含多个桶） | 一个桶（链表/树的头节点） |
| **内存开销** | 16 个 Segment + 各自的 HashEntry[] | 一个 Node[] table |
| **JVM 优化** | ReentrantLock 有额外开销 | synchronized 在 JDK 6 后有偏向锁、轻量级锁优化 |

> **核心改进**：锁的粒度从"一个 Segment（多个桶）"细化到"一个桶"，并发度大幅提升。

---

## 二、ConcurrentHashMap 的 put() 流程

```java
map.put(key, value);
```

```text
put(key, value)
  │
  ├─ 1. 计算 hash
  │     key 或 value 为 null → 抛 NullPointerException
  │     （HashMap 允许 null → 详见 [HashMap](hashmap.md)，ConcurrentHashMap 不允许）
  │
  ├─ 2. 如果 table 为空 → initTable()（CAS 设置 sizeCtl）
  │
  ├─ 3. 定位桶：index = (n-1) & hash
  │     │
  │     ├─ table[index] == null
  │     │   → CAS 插入新节点（无锁）
  │     │   → 成功则 size++，判断是否扩容
  │     │   → 失败则重试（有其他线程在操作）
  │     │
  │     └─ table[index] != null
  │         → synchronized 锁住头节点
  │         │
  │         ├─ 如果是链表 → 遍历，找到则覆盖，找不到则尾插
  │         │
  │         ├─ 如果是红黑树 → putTreeVal()
  │         │
  │         └─ 链表长度 ≥ 8 → treeifyBin()（树化）
  │
  └─ 4. size++，判断是否需要扩容
        addCount(1L, resizeThreshold)
```

### 为什么不允许 null 键/值

```text
HashMap 允许 null 键（hash 固定为 0，放在 table[0]）
HashMap 允许 null 值

ConcurrentHashMap 不允许 null，原因：
  在并发环境下，无法区分"key 不存在"和"key 存在但 value 为 null"。

  例如：
    map.get(key) 返回 null
    → key 不存在？还是 key 存在但 value = null？

  HashMap 单线程下可以用 containsKey() 区分，
  但 ConcurrentHashMap 在 containsKey() 和 get() 之间可能被其他线程修改。
```

---

## 三、size() 怎么在并发下保证准确

```text
JDK 7：先不加锁尝试 3 次，如果 modCount 变化则加锁统计
JDK 8：baseCount + CounterCell[]（类似 LongAdder 的分段计数）
```

### JDK 8 的计数机制

```java
// OpenJDK 8 ConcurrentHashMap 的核心计数字段
private transient volatile long baseCount;
private transient volatile CounterCell[] counterCells;

// size() 先汇总计数，再把结果截断到 int 范围
public int size() {
    long n = sumCount();
    return ((n < 0L) ? 0 :
            (n > (long) Integer.MAX_VALUE) ? Integer.MAX_VALUE :
            (int) n);
}

final long sumCount() {
    CounterCell[] as = counterCells;
    long sum = baseCount;
    if (as != null) {
        for (CounterCell a : as) {
            if (a != null)
                sum += a.value;
        }
    }
    return sum;
}
```

```text
addCount(1L, resizeThreshold)：
  1. 先 CAS 更新 baseCount
  2. 如果 CAS 失败（有竞争）→ 使用 CounterCell[] 分段计数
  3. 如果 CounterCell 也竞争失败 → 扩容 CounterCell 数组
```

**准确性边界要看源码语义**：`size()` 的确调用 `sumCount()` 汇总 `baseCount + Σ CounterCell.value`，不是抽样估算；但汇总过程没有锁住所有写线程。读取不同 cell 之间仍可发生 `put/remove`，所以并发更新期间返回值是一个**瞬时观测值**，不承诺对应某个全局线性化时刻。它适合监控和容量观察，不适合用作“先判断再执行”的并发控制条件。

`mappingCount()` 使用同一份 `sumCount()`，只是不把结果截断为 `Integer.MAX_VALUE`，并不因此获得更强的一致性保证。

**为什么不用 AtomicInteger**：

```text
AtomicInteger 在高并发下 CAS 竞争激烈。
CounterCell[] 把计数分散到多个槽位，减少竞争。
这和 LongAdder 的思路一样：空间换时间。
```

---

## 四、多线程协助扩容

> **说明**：HashMap 的扩容叫 `resize()`，是一个线程独立完成的。ConcurrentHashMap 的扩容分为两步：`resize`（创建新 table 并分配迁移任务）和 `transfer`（多线程迁移数据）。

这是 ConcurrentHashMap 最复杂的部分。当 table 需要扩容时，多个线程可以同时参与迁移。

```text
扩容过程：
  1. 第一个触发扩容的线程：
     - 创建新 table（容量翻倍）
     - 设置 transferIndex = oldTable.length
     - 设置 sizeCtl 为负数（表示正在扩容）

  2. 其他线程检测到 sizeCtl < 0：
     - 加入扩容，领取一段迁移任务
     - 每个线程从 transferIndex 往前领取 stride 个桶

  3. 每个线程独立迁移自己领取的桶：
     - 把旧 table 的节点移到新 table
     - 迁移完的桶放一个 ForwardingNode（占位节点）

  4. 所有桶迁移完毕 → 替换 table 引用
```

### 扩容期间 put 遇到 ForwardingNode 怎么办

```text
put() 定位到某个桶 → 发现是 ForwardingNode（该桶已迁移）
  → 调用 helpTransfer() 协助扩容（帮忙迁移其他桶）
  → 扩容完成后重试 put()
```

这意味着：扩容期间，新来的 put 线程不会等待，而是主动帮忙搬运数据，加速扩容完成。

### ForwardingNode 的作用

```java
// 如果一个桶已经被迁移到新 table，旧 table 的这个位置放一个 ForwardingNode
static final class ForwardingNode<K,V> extends Node<K,V> {
    final Node<K,V>[] nextTable;  // 指向新 table

    // 访问 ForwardingNode 时，自动转发到新 table
    Node<K,V> find(int h, Object k) {
        return nextTable 中查找;
    }
}
```

> **效果**：扩容期间，读操作遇到 ForwardingNode 会自动去新 table 找，不会阻塞也不会读到过期数据。

---

## 五、ConcurrentHashMap 常用原子操作

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// putIfAbsent：key 不存在时才插入（原子）
map.putIfAbsent("A", 1);

// computeIfAbsent：key 不存在时计算并插入（原子）
map.computeIfAbsent("B", k -> expensiveComputation(k));

// compute：无论 key 是否存在都计算新值（原子）
map.compute("A", (k, v) -> v == null ? 1 : v + 1);  // 计数器

// merge：合并值（原子）
map.merge("A", 1, Integer::sum);  // 如果存在则加 1，不存在则设为 1

// replace：key 存在时才替换（原子）
map.replace("A", 1, 2);  // 仅当 A 的当前值是 1 时才替换为 2
```

**为什么要用原子操作**：
```java
// 错误：非原子的 check-then-act
if (!map.containsKey("A")) {
    map.put("A", 1);  // 两步之间可能被其他线程插入
}

// 正确：原子操作
map.putIfAbsent("A", 1);
```

---

## 六、CopyOnWriteArrayList

写时复制的线程安全 List，适合**读多写少**的场景。

### 原理

```text
读操作：无锁，直接读内部数组
写操作：加锁，复制整个数组，修改副本，替换引用

        ┌─────────────────────┐
读线程 → │ [A, B, C, D, E]    │ ← 当前数组（只读）
        └─────────────────────┘

写线程（add "F"）：
  1. 加锁（ReentrantLock）
  2. 复制数组 → [A, B, C, D, E, F]
  3. 替换引用：volatile array = newArray
  4. 释放锁

读线程继续读旧数组，不受影响。
新读线程看到新数组。
```

### 写锁演进：JDK 8 vs JDK 11+

写时复制策略没有改变，变化的是**写操作的互斥实现**。JDK 8 使用 `ReentrantLock`；JDK 11 将锁字段改为普通 `Object`，写方法使用 JVM 内置的 `synchronized`。这里没有用 CAS 完成整次写入：复制数组与发布新数组必须作为一个互斥临界区，否则两个写线程可能基于同一旧数组复制，造成更新丢失。

```java
// OpenJDK 8：显式 ReentrantLock
final transient ReentrantLock lock = new ReentrantLock();

public boolean add(E e) {
    final ReentrantLock lock = this.lock;
    lock.lock();
    try {
        Object[] elements = getArray();
        int len = elements.length;
        Object[] newElements = Arrays.copyOf(elements, len + 1);
        newElements[len] = e;
        setArray(newElements);       // volatile 发布新数组
        return true;
    } finally {
        lock.unlock();
    }
}
```

```java
// OpenJDK 11+：普通锁对象 + synchronized
final transient Object lock = new Object();

public boolean add(E e) {
    synchronized (lock) {
        Object[] es = getArray();
        int len = es.length;
        es = Arrays.copyOf(es, len + 1);
        es[len] = e;
        setArray(es);                // volatile 发布新数组
        return true;
    }
}
```

| 对比项 | JDK 8 | JDK 11+ |
|---|---|---|
| 锁字段 | `ReentrantLock` | `Object` |
| 写入临界区 | `lock()/unlock()` + `finally` | `synchronized (lock)` |
| 公平锁/可中断锁能力 | 实现中未开放给调用方 | 不提供 |
| 核心语义 | 锁内复制并发布 | 锁内复制并发布 |

> **演进原因**：该内部锁只需要不可重入控制之外的基本互斥，不使用 `Condition`、公平性、可中断获取等 `ReentrantLock` 扩展能力；改用 `synchronized` 可简化代码，并直接受益于 JVM 对内置锁的持续优化。不要据此推导“所有场景 synchronized 都一定更快”，性能仍需按目标 JDK 和负载用 JMH 验证。

### 读操作与快照迭代器

```java
public E get(int index) {
    return elementAt(getArray(), index);  // volatile 读数组引用，无锁
}

// 迭代器创建时捕获当时的数组引用
public Iterator<E> iterator() {
    return new COWIterator<E>(getArray(), 0);
}
```

普通 `get()` 每次读取当前数组；迭代器则固定遍历创建时捕获的不可变数组快照。因此后续写入不会抛 `ConcurrentModificationException`，也一定不会出现在这个既有迭代器里。它常被笼统归入 fail-safe/弱一致遍历，但语义上要与 `ConcurrentHashMap` 区分：前者是**固定快照**，后者的弱一致迭代可能观察到部分并发更新。

### 优缺点

| 优点 | 缺点 |
|------|------|
| 读操作无锁，极快 | 写操作复制整个数组，内存和时间开销大 |
| 迭代器不会抛 `ConcurrentModificationException` | 迭代器看不到写操作的修改（弱一致性） |
| 适合读多写少 | 不适合写多或大数组 |

### 适用场景

```text
✅ 适合：
  - 事件监听器列表（注册少，触发多）
  - 配置列表（修改少，读取多）
  - 黑名单/白名单（更新频率低）

❌ 不适合：
  - 频繁增删的场景（每次写都复制整个数组）
  - 大数组（复制开销大）
  - 需要实时看到修改的场景（迭代器弱一致性）
```

---

## 七、阻塞队列选型

阻塞队列是生产者-消费者模型的核心。`BlockingQueue` 接口定义了阻塞的 `put()` 和 `take()` 方法。

### 选型决策

```text
你需要什么？
│
├── 有界队列（防止 OOM）
│   └── ArrayBlockingQueue
│       - 数组实现，创建时必须指定容量
│       - 单锁（put 和 take 互斥）
│       - 公平/非公平锁可选
│
├── 无界队列（或大容量）
│   └── LinkedBlockingQueue
│       - 链表实现，默认容量 Integer.MAX_VALUE（几乎无界）
│       - 双锁（putLock + takeLock，生产消费不互斥）
│       - 吞吐更高
│
├── 同步传递（不存储元素）
│   └── SynchronousQueue
│       - 每个 put 必须等一个 take，反之亦然
│       - 线程池 Executors.newCachedThreadPool() 用的就是这个
│       - 适合直接传递任务
│
├── 优先级队列
│   └── PriorityBlockingQueue
│       - 二叉堆实现，无界
│       - 出队顺序按优先级
│
└── 延迟队列
    └── DelayQueue
        - 元素到期后才能出队
        - 用于定时任务、延迟重试
```

### ArrayBlockingQueue vs LinkedBlockingQueue

| | ArrayBlockingQueue | LinkedBlockingQueue |
|---|---|---|
| **底层** | 数组 | 链表 |
| **有界/无界** | 有界（必须指定容量） | 可选（默认 Integer.MAX_VALUE） |
| **锁** | 单锁（put/take 互斥） | 双锁（put/take 不互斥） |
| **吞吐** | 较低（锁竞争） | 较高（锁分离） |
| **内存** | 预分配（创建时占用） | 按需分配（每个节点额外开销） |
| **GC 压力** | 低（数组复用） | 高（频繁创建/回收节点） |

```java
// 典型用法：生产者-消费者
BlockingQueue<String> queue = new ArrayBlockingQueue<>(100);

// 生产者
queue.put("task");  // 队列满时阻塞

// 消费者
String task = queue.take();  // 队列空时阻塞

// 非阻塞版本
queue.offer("task");    // 队列满时返回 false
queue.poll();           // 队列空时返回 null
```

> **线程池中的选择**：
> - `FixedThreadPool` / `SingleThreadPool` → `LinkedBlockingQueue`（无界，任务堆积）
> - `CachedThreadPool` → `SynchronousQueue`（直接传递，不堆积）
> - 自定义线程池建议用 `ArrayBlockingQueue`（有界，防止 OOM）

---

## 八、非阻塞并发队列：ConcurrentLinkedQueue

不是所有并发队列都需要阻塞。`ConcurrentLinkedQueue` 是基于 CAS 实现的**非阻塞**线程安全队列，适合高吞吐、不需要等待的场景。

| | ConcurrentLinkedQueue | ArrayBlockingQueue |
|---|---|---|
| **阻塞** | 不阻塞（空时 poll 返回 null） | 空时 take() 阻塞 |
| **锁机制** | 无锁（CAS） | ReentrantLock |
| **吞吐** | 高 | 中 |
| **适用场景** | 消息缓冲、事件队列 | 生产者-消费者 |

```java
ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<>();
queue.offer("task1");      // 入队（永远成功）
String task = queue.poll(); // 出队（空时返回 null，不阻塞）
```

> **还有** `ConcurrentLinkedDeque`（双端版本），支持头尾两端操作。

---

## 九、ConcurrentSkipListMap

跳表实现的有序 + 线程安全 Map，是 TreeMap 的并发替代。

### 跳表结构

```text
Level 3:  1 ──────────────────────── 9
Level 2:  1 ──── 3 ──────────────── 9
Level 1:  1 ── 3 ── 5 ── 7 ────── 9
Level 0:  1 ── 3 ── 5 ── 7 ── 8 ── 9  ← 最底层包含所有元素
```

- 查找从最高层开始，向右走直到找到大于目标的节点，然后下降一层
- 时间复杂度 O(log n)，与红黑树相同
- 并发友好：插入/删除只影响局部，不需要全局重平衡

### 与 TreeMap 对比

| | TreeMap | ConcurrentSkipListMap |
|---|---|---|
| 底层 | 红黑树 | 跳表 |
| 有序 | 是 | 是 |
| 线程安全 | 否 | 是 |
| 时间复杂度 | O(log n) | O(log n) |
| null 键 | 不允许 | 不允许 |

```java
ConcurrentSkipListMap<String, Integer> map = new ConcurrentSkipListMap<>();
map.put("banana", 2);
map.put("apple", 1);
map.put("cherry", 3);

map.firstKey();                  // "apple"
map.subMap("apple", "cherry");   // {apple=1, banana=2}
```

---

## 十、并发集合速查表

| 场景 | 推荐集合 | 不推荐 |
|------|----------|--------|
| 多线程 Map | **ConcurrentHashMap** | Hashtable、Collections.synchronizedMap |
| 多线程有序 Map | **ConcurrentSkipListMap** | Collections.synchronizedSortedMap |
| 多线程 List（读多写少） | **CopyOnWriteArrayList** | Vector |
| 多线程 List（写多） | **Collections.synchronizedList** | CopyOnWriteArrayList |
| 多线程 Set | **ConcurrentHashMap.newKeySet()** | Collections.synchronizedSet |
| 生产者-消费者（有界） | **ArrayBlockingQueue** | — |
| 生产者-消费者（高吞吐） | **LinkedBlockingQueue** | — |
| 线程池任务传递 | **SynchronousQueue** | — |
| 延迟任务 | **DelayQueue** | Timer |
| 优先级任务 | **PriorityBlockingQueue** | — |

---

## 十一、实战陷阱

### 1. 把 size() 当作并发控制条件

```java
// ❌ 错误：size() 与后续 put 是两个独立操作，且并发汇总不提供全局快照
if (map.size() < limit) {
    map.put(key, value);             // 多个线程都可能通过检查，最终突破 limit
}

// ✅ 正确：容量是硬约束时，在同一把锁/信号量协议下完成判断与占位
if (permits.tryAcquire()) {
    V old = map.putIfAbsent(key, value);
    if (old != null) {
        permits.release();           // key 已存在，没有新增槽位
    }
}
```

源码中的 `size()` 汇总 `baseCount + Σ CounterCell.value`，所以它不是随机近似值；但遍历计数槽时写线程仍可更新不同槽位，结果不承诺是线性一致快照。`mappingCount()` 解决的是 `int` 上限问题，不解决一致性问题。

### 2. 混淆两类并发迭代器

```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
list.add("A");
Iterator<String> snapshot = list.iterator();
list.add("B");
// snapshot 只遍历创建时数组中的 "A"，一定看不到后来加入的 "B"

ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
Iterator<String> weak = map.keySet().iterator();
map.put("B", 2);
// weak 不抛 CME；可能看到也可能看不到并发加入的 "B"
```

两者都不会抛 `ConcurrentModificationException`，但保证不同：CopyOnWriteArrayList 是**确定的旧快照**；ConcurrentHashMap 是**弱一致遍历**，会反映迭代器创建时或创建后的部分状态，而且元素不会被重复返回。

### 3. 误以为线程安全集合让复合操作自动原子化

```java
// ❌ 错误：get 与 put 各自线程安全，组合后仍会丢更新
map.put("A", map.getOrDefault("A", 0) + 1);

// ✅ 正确：把读-改-写交给容器的原子方法
map.merge("A", 1, Integer::sum);
map.compute("B", (k, v) -> v == null ? 1 : v + 1);
```

`compute*` / `merge` 的回调在原子更新协议内执行，应保持短小，避免阻塞 I/O、递归更新同一个 key 或执行不可控的用户代码。

### 4. 给 ConcurrentHashMap 再套 synchronizedMap

```java
// ❌ 无意义的全表包装，增加锁竞争
Map<String, Integer> badMap =
        Collections.synchronizedMap(new ConcurrentHashMap<>());

// ✅ 直接使用容器提供的并发与原子 API
ConcurrentHashMap<String, Integer> goodMap = new ConcurrentHashMap<>();
```

### 5. 忽视负载模型，凭“线程安全”三个字选集合

| 负载 | 推荐 | 原因与代价 |
|---|---|---|
| List 读远多于写、规模可控 | `CopyOnWriteArrayList` | 读无锁、快照迭代；每次写 O(n) 复制并产生旧数组垃圾 |
| List 写频繁或数组很大 | 锁保护的 `ArrayList`，或重审数据结构 | 避免每次写全量复制；遍历时必须遵守同一锁协议 |
| Map 高并发读写 | `ConcurrentHashMap` | 读基本无锁、桶级写协调；批量快照需另行同步 |
| 有界生产者-消费者 | `ArrayBlockingQueue` | 固定容量提供背压，数组复用、GC 压力较低 |
| 非阻塞事件缓冲 | `ConcurrentLinkedQueue` | CAS 高吞吐，但没有容量背压，消费者需处理空轮询 |

性能不能只比较单次 `get()`：CopyOnWriteArrayList 的一次写会分配并复制 `n + 1` 长度数组，旧迭代器还会延长旧数组生命周期；写比例、集合规模、分配率和 GC 暂停必须一起衡量。应针对目标 JDK 用 JMH 模拟真实读写比例，而不是引用脱离环境的固定倍数。

---

## 十二、章节互链

- 先读 [ArrayList 源码剖析](ArrayList/README.md)，对比普通动态数组与 CopyOnWriteArrayList 的复制成本、fail-fast / 快照迭代语义。
- 结合 [HashMap 深入](hashmap.md)，理解 ConcurrentHashMap 为什么沿用“数组 + 链表 + 红黑树”又必须改造写入、扩容和计数协议。
- 对照 [LinkedList 源码剖析](LinkedList/README.md)，区分普通双向链表、`ConcurrentLinkedDeque` 与阻塞队列的场景边界。
- 完整专题入口见 [Java collection 系列索引](README.md)，ConcurrentHashMap 的独立展开见 [ConcurrentHashMap 专题](ConcurrentHashMap/README.md)。

---

← [返回: collection](../README.md) | [返回: 01.java](../../README.md)

