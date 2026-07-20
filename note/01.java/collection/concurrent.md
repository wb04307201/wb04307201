# 并发集合

> 目标：搞懂 ConcurrentHashMap 的实现原理，以及 Java 并发场景下各种集合类的选型。

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
```java
// 核心字段
private transient volatile long baseCount;           // 基础计数
private transient volatile CounterCell[] counterCells; // 分段计数数组
```text

```text
// 计数逻辑（伪代码）
addCount(1L, resizeThreshold):
  1. 先 CAS 更新 baseCount
  2. 如果 CAS 失败（有竞争）→ 使用 CounterCell[] 分段计数
  3. 如果 CounterCell 也竞争失败 → 扩容 CounterCell 数组

// size() = baseCount + sum(counterCells)
// mappingCount() 返回 long，size() 返回 int（可能溢出）
```text
```

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

### 源码关键（JDK 8 实现，JDK 11+ 改用 synchronized + CAS）

```java
// JDK 8 写操作（以 add 为例）
public boolean add(E e) {
    final ReentrantLock lock = this.lock;
    lock.lock();
    try {
        Object[] elements = getArray();       // 获取当前数组
        Object[] newElements = Arrays.copyOf(elements, len + 1);  // 复制
        newElements[len] = e;                  // 修改副本
        setArray(newElements);                 // volatile 写，替换引用
        return true;
    } finally {
        lock.unlock();
    }
}

// 读操作
public E get(int index) {
    return get(getArray(), index);  // 直接读，无锁
}
```

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

## 十一、常见误区

### 1. size() 的值可能迅速过期

```java
// size() 返回的是调用瞬间的精确快照（baseCount + Σ CounterCell），不是近似计算
// 但在高并发下，返回后这个值可能已经被其他线程修改了
// 元素可能超过 int 范围时用 mappingCount()（返回 long，避免溢出）
long count = map.mappingCount();
```

### 2. 迭代器是弱一致性的

```java
// 遍历时其他线程修改不会抛 ConcurrentModificationException
// 但可能看到也可能看不到修改
for (String key : map.keySet()) {
    // key 可能在遍历时被其他线程删除或修改
}
```

### 3. 复合操作不是原子的

```java
// 错误：check-then-act 不是原子的
if (map.containsKey("A")) {
    map.put("A", map.get("A") + 1);  // 两步之间可能被其他线程修改
}

// 正确：用原子方法
map.compute("A", (k, v) -> v == null ? 1 : v + 1);
// 或
map.merge("A", 1, Integer::sum);
```

### 4. 不要用 Collections.synchronizedMap 包 ConcurrentHashMap

```java
// 错误：无意义的包装，反而降低性能
Map<String, Integer> badMap = Collections.synchronizedMap(new ConcurrentHashMap<>());

// 正确：ConcurrentHashMap 本身已经线程安全，直接用即可
Map<String, Integer> goodMap = new ConcurrentHashMap<>();
```
