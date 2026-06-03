# ConcurrentHashMap 深入

> 目标：彻底搞懂 ConcurrentHashMap 的底层实现，包括 JDK 7 分段锁、JDK 8 CAS + synchronized 机制、put/get 流程、size() 原理、扩容迁移机制，以及并发场景下的选型。

---

## 一、为什么需要 ConcurrentHashMap

```
单线程场景：HashMap 足矣（O(1) 查找，最快）

多线程场景下三个选择：
  1. Hashtable    → 全表锁（synchronized 修饰每个方法），性能极差
  2. Collections.synchronizedMap → 全表锁（包装 HashMap），同样性能差
  3. ConcurrentHashMap → 分段/分桶锁，多线程并行读写，性能最优
```

### 并发集合对比

| 维度 | HashMap | Hashtable | synchronizedMap | ConcurrentHashMap |
|------|---------|-----------|-----------------|-------------------|
| **线程安全** | 否 | 是 | 是 | 是 |
| **锁粒度** | 无锁 | 全表锁 | 全表锁 | 分段锁 / 桶级锁 |
| **允许 null** | key 和 value 都可 | 都不可 | 取决于内部 Map | 都不可 |
| **并发读** | 不安全 | 互斥 | 互斥 | 无锁（volatile） |
| **并发写** | 数据覆盖 | 串行 | 串行 | 并行 |
| **迭代器** | fail-fast | fail-fast | fail-fast | 弱一致性 |
| **性能** | 最高 | 最低 | 低 | 高（仅次于 HashMap） |

---

## 二、JDK 7 的 Segment 分段锁机制

### 整体架构

```
ConcurrentHashMap
├── Segment[0]  ── ReentrantLock ── HashEntry[] table ── [e0]→[e1]→null
├── Segment[1]  ── ReentrantLock ── HashEntry[] table ── [e0]→null
├── Segment[2]  ── ReentrantLock ── HashEntry[] table ── [e0]→[e1]→[e2]→null
├── ...
└── Segment[15] ── ReentrantLock ── HashEntry[] table ── [e0]→null

并发度 = Segment 数量 = 16（默认，构造时可指定 concurrencyLevel）
每个 Segment 是一把独立的 ReentrantLock + 一个独立的 HashEntry[] 数组
```

### 两次 Hash 定位

```java
// JDK 7 的 put 流程
V put(K key, int hash, V value, boolean onlyIfAbsent) {
    // 第一次 hash：用 hash 的高位定位到某个 Segment
    Segment<K,V> seg = segments[hash & (segments.length - 1)];

    // 第二次 hash：在 Segment 内部定位到具体的桶
    seg.put(key, hash, value, false);
        // lock() → ReentrantLock 加锁
        // index = hash & (table.length - 1)  → 定位桶
        // 链表头插法插入新节点
        // unlock()
}
```

### 读写策略

```
读操作（get）：
  1. 第一次 hash 定位 Segment
  2. 读取 Segment 的 table 引用（volatile）
  3. 第二次 hash 定位桶
  4. 遍历链表查找
  → 全程无锁，靠 volatile 保证可见性

写操作（put）：
  1. 第一次 hash 定位 Segment
  2. segment.lock() → 获取该 Segment 的锁
  3. 在 Segment 内部的 table 上做修改
  4. segment.unlock()
  → 最多 16 个线程可以同时写（各自锁定不同的 Segment）
```

### JDK 7 的局限性

```
1. 并发度固定：最多 16 个线程同时写（Segment 数量在构造时确定）
2. 内存浪费：16 个 Segment，每个有自己的 HashEntry[] 数组
3. 锁粒度粗：一个 Segment 包含多个桶，同 Segment 内的写仍然互斥
4. 扩容低效：单个 Segment 自己扩容，不涉及其他 Segment
5. 链表头插法：JDK 7 的 ConcurrentHashMap 内部虽然不会死循环
   （每个 Segment 是独立的，不会互相干扰扩容），但仍然是头插法
```

---

## 三、JDK 8 的 CAS + synchronized 机制

### 整体架构

```
ConcurrentHashMap
└── Node<K,V>[] table（一个大的 Node 数组，和 HashMap 结构相同）
    ├── table[0]  → null
    ├── table[1]  → [K1,V1] → [K2,V2] → null        ← 链表
    ├── table[2]  → null
    ├── table[3]  → TreeBin 根节点                    ← 链表长度 ≥ 8 时树化
    │                ↙      ↘
    │              [K3]    [K4]
    │             ↙  ↘    ↙  ↘
    │           [K5] [K6] [K7] [K8]
    ├── table[4]  → ForwardingNode → nextTable       ← 扩容迁移中的桶
    └── ...

并发度 = table.length（初始 16，扩容后 32、64...）
每个桶 = 一把锁（synchronized 锁住链表/树的头节点）
```

### 为什么从 ReentrantLock 换成 synchronized

| 对比项 | JDK 7（ReentrantLock） | JDK 8（synchronized） |
|--------|------------------------|----------------------|
| **锁对象** | Segment 实例 | Node 节点（链表/树的头节点） |
| **锁粒度** | 一个 Segment（多个桶） | 一个桶 |
| **并发度** | 固定 16 | 随 table 长度变化（16→32→64→...） |
| **JVM 优化** | 需要手动 lock/unlock | 偏向锁 → 轻量级锁 → 重量级锁 |
| **内存开销** | 每个 Segment 有 ReentrantLock 对象 | 每个 Node 内置 mark word 做锁 |

```
JDK 6 之后 synchronized 有了重大优化：
  - 偏向锁：无竞争时几乎没有开销
  - 轻量级锁：低竞争时 CAS 自旋
  - 重量级锁：高竞争时阻塞
  → 在锁粒度细化到单个桶的情况下，synchronized 的性能优于 ReentrantLock
```

### 核心安全机制

```java
// Node 的字段设计（volatile 保证可见性）
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;            // 不可变
    final K key;               // 不可变
    volatile V val;            // volatile → 写操作对所有线程立即可见
    volatile Node<K,V> next;   // volatile → 链表变化立即可见
}

// 对 table 数组的 volatile 访问
static final <K,V> Node<K,V> tabAt(Node<K,V>[] tab, int i) {
    return (Node<K,V>) U.getObjectVolatile(tab, ((long)i << ASHIFT) + ABASE);
}

static final <K,V> boolean casTabAt(Node<K,V>[] tab, int i, Node<K,V> c, Node<K,V> v) {
    return U.compareAndSwapObject(tab, ((long)i << ASHIFT) + ABASE, c, v);
}

static final <K,V> void setTabAt(Node<K,V>[] tab, int i, Node<K,V> v) {
    U.putObjectVolatile(tab, ((long)i << ASHIFT) + ABASE, v);
}
```

```
tabAt()    → Unsafe.getObjectVolatile → volatile 读（确保读到最新值）
casTabAt() → Unsafe.compareAndSwapObject → CAS 原子写（无锁插入空桶）
setTabAt() → Unsafe.putObjectVolatile → volatile 写（确保修改立即可见）
```

---

## 四、核心数据结构

### Node 体系

```
Node 体系（类继承结构）：

Node<K,V>                   ← 基础节点（链表节点）
  ├── TreeNode<K,V>         ← 红黑树节点（继承 LinkedHashMap.Entry）
  ├── TreeBin<K,V>          ← 红黑树的容器（替代桶位置，内部持有 TreeNode）
  ├── ForwardingNode<K,V>   ← 扩容期间的占位节点（指向新 table）
  ├── ReservationNode<K,V>  ← 占位节点（computeIfAbsent 等原子操作使用）
  └── (普通 Node)           ← 最常见的链表节点
```

### 各节点类型详解

```java
// 1. 普通 Node（链表节点）
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;
    final K key;
    volatile V val;
    volatile Node<K,V> next;
}

// 2. TreeNode（红黑树节点）
static final class TreeNode<K,V> extends Node<K,V> {
    TreeNode<K,V> parent;    // 父节点
    TreeNode<K,V> left;      // 左子节点
    TreeNode<K,V> right;     // 右子节点
    TreeNode<K,V> prev;      // 删除时需要
    boolean red;             // 颜色
}

// 3. TreeBin（红黑树容器，放在桶的位置上）
static final class TreeBin<K,V> extends Node<K,V> {
    TreeNode<K,V> root;       // 红黑树的根
    volatile Thread waiter;   // 等待写锁的线程
    volatile int lockState;   // 锁状态（读写锁）
    // TreeBin 内部 TreeNode 使用读写锁，而非 synchronized
    // 读多写少时可以并发读
}

// 4. ForwardingNode（扩容占位节点）
static final class ForwardingNode<K,V> extends Node<K,V> {
    final Node<K,V>[] nextTable;  // 指向新 table

    // find() 方法会转发到新 table 查找
    Node<K,V> find(int h, Object k) {
        // loop: 去 nextTable 中查找
        // 如果 nextTable 的桶又是 ForwardingNode，继续转发
    }
}
```

### 内存布局示意

```
┌──────────────────────────────────────────────────────────┐
│                    ConcurrentHashMap                      │
├──────────────────────────────────────────────────────────┤
│  volatile Node[] table        ← 主数组                    │
│  volatile int sizeCtl         ← 控制字段（初始化/扩容）     │
│  volatile long baseCount      ← 基础计数                   │
│  volatile CounterCell[]       ← 分段计数                   │
│                                                             │
│  table 内部：                                               │
│                                                             │
│  table[0]  → null                                           │
│  table[1]  → Node("k1","v1") → Node("k2","v2") → null      │
│  table[2]  → TreeBin{root → TreeNode...}                    │
│  table[3]  → ForwardingNode → nextTable                     │
│  table[4]  → null                                           │
│  table[5]  → Node("k3","v3") → null                         │
│  ...                                                        │
└──────────────────────────────────────────────────────────┘
```

---

## 五、put() 完整流程

```java
map.put(key, value);
// key 或 value 为 null → 立即抛 NullPointerException
```

```
put(key, value)
  │
  ├─ 1. 计算 spread(hash) = (h ^ (h >>> 16)) & HASH_BITS
  │     HASH_BITS = 0x7fffffff（保证 hash 始终为正数）
  │
  ├─ 2. 如果 table 为空 → initTable() 初始化
  │     CAS 设置 sizeCtl，保证只有一个线程执行初始化
  │
  ├─ 3. 定位桶：i = (n - 1) & hash
  │     │
  │     ├─ 桶为空（tabAt(tab, i) == null）
  │     │   → CAS 插入新节点
  │     │   → 成功：put 完成，addCount(1, binCount)
  │     │   → 失败：有竞争，重试（回到步骤 3）
  │     │
  │     ├─ 桶是 ForwardingNode（hash = MOVED = -1）
  │     │   → helpTransfer()：协助扩容
  │     │   → 完成后重试 put
  │     │
  │     └─ 桶有数据（链表或红黑树）
  │         → synchronized (f) 锁住头节点
  │         │
  │         ├─ 如果是链表（hash ≥ 0）
  │         │   → 遍历链表
  │         │   → 找到相同 key → 覆盖 value
  │         │   → 未找到 → 尾插法插入新节点
  │         │   → 链表长度 ≥ 8 → treeifyBin() 尝试树化
  │         │
  │         └─ 如果是红黑树（f 是 TreeBin）
  │             → putTreeVal() 插入树中
  │
  └─ 4. addCount(1L, binCount) → 增加计数，判断是否扩容
```

### 关键代码

```java
final V putVal(K key, V value, boolean onlyIfAbsent) {
    if (key == null || value == null) throw new NullPointerException();
    int hash = spread(key.hashCode());
    int binCount = 0;
    for (Node<K,V>[] tab = table;;) {
        Node<K,V> f; int n, i, fh;
        if (tab == null || (n = tab.length) == 0)
            tab = initTable();                            // 懒初始化
        else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
            if (casTabAt(tab, i, null, new Node<K,V>(hash, key, value, null)))
                break;                                    // CAS 成功，直接插入
        }
        else if ((fh = f.hash) == MOVED)
            tab = helpTransfer(tab, f);                   // 协助扩容
        else {
            V oldVal = null;
            synchronized (f) {                            // 锁住头节点
                if (tabAt(tab, i) == f) {
                    if (fh >= 0) {                        // 链表
                        binCount = 1;
                        for (Node<K,V> e = f;; ++binCount) {
                            K ek;
                            if (e.hash == hash && ((ek = e.key) == key || ek.equals(key))) {
                                oldVal = e.val;           // 覆盖旧值
                                if (!onlyIfAbsent) e.val = value;
                                break;
                            }
                            Node<K,V> pred = e;
                            if ((e = e.next) == null) {   // 尾插法
                                pred.next = new Node<K,V>(hash, key, value, null);
                                break;
                            }
                        }
                    }
                    else if (f instanceof TreeBin) {      // 红黑树
                        Node<K,V> p;
                        binCount = 2;
                        if ((p = ((TreeBin<K,V>)f).putTreeVal(hash, key, value)) != null) {
                            oldVal = p.val;
                            if (!onlyIfAbsent) p.val = value;
                        }
                    }
                }
            }
            if (binCount != 0) {
                if (binCount >= TREEIFY_THRESHOLD)
                    treeifyBin(tab, i);                   // 链表转红黑树
                if (oldVal != null)
                    return oldVal;
                break;
            }
        }
    }
    addCount(1L, binCount);                               // 计数 + 检查扩容
    return null;
}
```

---

## 六、get() 流程（无锁读取）

```java
public V get(Object key) {
    if (key == null) throw new NullPointerException();
    int hash = spread(key.hashCode());
    for (Node<K,V>[] tab = table;;) {
        Node<K,V> f; int n, i, fh; V val;
        if (tab == null || (n = tab.length) == 0 ||
            (f = tabAt(tab, i = (n - 1) & hash)) == null)
            return null;                                  // 桶为空

        if ((fh = f.hash) == MOVED)                       // 扩容期间
            tab = helpTransfer(tab, f);                   // 去新 table 找
        else {
            val = f.val;
            if (f.hash == hash && f.key.equals(key))
                return val;                               // 头节点命中
            if (fh < 0)                                   // 红黑树
                return ((TreeBin<K,V>)f).getTreeNode(hash, key);
            // 链表遍历
            for (Node<K,V> e = f.next; e != null; e = e.next) {
                if (e.hash == hash && e.key.equals(key))
                    return e.val;
            }
            return null;
        }
    }
}
```

```
get() 的核心特点：
  1. 全程不加锁
  2. volatile 读保证看到最新值
  3. 遇到 ForwardingNode 时去新 table 找（扩容期间也不影响读）
  4. 弱一致性：get() 可能看不到其他线程刚刚 put 的值（volatile 可见性延迟），
     但最终一定会看到
```

### 为什么 get() 不需要加锁

```
Node 的三个字段设计：
  - hash: final（不可变）
  - key:  final（不可变）
  - val:  volatile（修改立即可见）
  - next: volatile（链表结构变化立即可见）

加上 table 本身是 volatile 引用，所以：
  - get 读到的是最新的 table 引用
  - get 遍历链表时，每个节点的 val 和 next 都是最新的
  - 不会出现读到"半截"链表的情况

唯一的弱一致性场景：
  put 刚修改了 val，get 可能在极短时间内读到旧值（CPU 缓存延迟）
  但这通常只有几纳秒，对绝大多数场景无影响。
```

---

## 七、initTable() 初始化

```java
private final Node<K,V>[] initTable() {
    Node<K,V>[] tab; int sc;
    while ((tab = table) == null || tab.length == 0) {
        // sizeCtl < 0 表示有其他线程在初始化
        if ((sc = sizeCtl) < 0)
            Thread.yield();              // 让出 CPU，等待初始化完成
        // CAS 尝试将 sizeCtl 设为 -1（抢到初始化权）
        else if (U.compareAndSwapInt(this, SIZECTL, sc, -1)) {
            try {
                if ((tab = table) == null || tab.length == 0) {
                    int n = (sc > 0) ? sc : DEFAULT_CAPACITY;
                    @SuppressWarnings("unchecked")
                    Node<K,V>[] nt = (Node<K,V>[])new Node<?,?>[n];
                    table = tab = nt;
                    sc = n - (n >>> 2);  // sizeCtl = 0.75 * n（扩容阈值）
                }
            } finally {
                sizeCtl = sc;
            }
            break;
        }
    }
    return tab;
}
```

```
初始化策略：
  1. 检查 sizeCtl：如果 < 0，说明有其他线程在初始化 → Thread.yield() 等待
  2. CAS 竞争：将 sizeCtl 设为 -1，CAS 成功则获得初始化权
  3. 创建 table：默认容量 16，sizeCtl 设为 12（0.75 * 16）
  4. CAS 失败：回到循环开头，检测到 table 不为空则退出
  → 保证多线程下只有一个线程执行初始化
```

---

## 八、扩容机制（transfer）

### 整体流程

```
扩容触发：addCount(1L, binCount) → size >= threshold

步骤：
  1. 第一个线程检测到需要扩容：
     → sizeCtl 设置为 (n << 1) 的负数标记（表示正在扩容）
     → 创建新 table（容量翻倍）
     → 设置 transferIndex = oldTable.length

  2. 多线程参与 transfer()：
     → 每个线程从 transferIndex 领取一段迁移任务（stride 个桶）
     → transferIndex 是全局的，CAS 递减，保证任务不重复
     → 每个线程独立迁移自己领取的桶

  3. 迁移单个桶：
     → 遍历旧桶的链表/树
     → 根据 (hash & oldCap) == 0 决定去向
         留原位置 或 去 原位置 + oldCap
     → 拆分成两个链表（lo 和 hi）
     → 把 lo 放到新 table[i]，hi 放到新 table[i + oldCap]
     → 旧 table 的该桶位置放 ForwardingNode

  4. 全部迁移完成：
     → table = nextTable
     → sizeCtl = 新容量的 0.75 倍
```

### 迁移示意

```
旧 table（容量 16）                              新 table（容量 32）
┌───┬───┬───┬───┬───┬───┬───┬───┐               ┌───┬───┬───┬───┬───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │               │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │
├───┼───┼───┼───┼───┼───┼───┼───┤               ├───┼───┼───┼───┼───┼───┼───┼───┤
│ 8 │ 9 │10 │11 │12 │13 │14 │15 │               │ 8 │ 9 │10 │11 │12 │13 │14 │15 │
└───┴───┴───┴───┴───┴───┴───┴───┘               ├───┼───┼───┼───┼───┼───┼───┼───┤
                                                │16 │17 │18 │19 │20 │21 │22 │23 │
旧桶 index=3，链表：                             ├───┼───┼───┼───┼───┼───┼───┼───┤
  [A:hash=3] → [B:hash=19] → [C:hash=35]        │24 │25 │26 │27 │28 │29 │30 │31 │
                                                └───┴───┴───┴───┴───┴───┴───┴───┘
判断规则：(hash & oldCap) == 0
  A: 3 & 16 = 0  → 留 newTable[3]               迁移结果：
  B: 19 & 16 = 16 → 去 newTable[19]                newTable[3]  → [A] → [C] → null
  C: 35 & 16 = 0  → 留 newTable[3]                newTable[19] → [B] → null

旧 table[3] → ForwardingNode（指向新 table）
```

### 多线程协助扩容

```java
// 扩容期间 put 遇到 ForwardingNode
if ((fh = f.hash) == MOVED)
    tab = helpTransfer(tab, f);  // 主动帮忙搬运数据

// helpTransfer 内部
final Node<K,V>[] helpTransfer(Node<K,V>[] tab, Node<K,V> f) {
    // 检测到扩容正在进行（sizeCtl < 0）
    // 加入 transfer 线程池，领取迁移任务
    // 搬运完自己的任务后返回新 table
}
```

```
扩容期间 put 的行为：
  遇到 ForwardingNode → 不等待，不阻塞
  → 主动帮忙搬运数据（helpTransfer）
  → 搬运完成后重试 put

扩容期间 get 的行为：
  遇到 ForwardingNode → 去新 table 查找
  → 不会读到过期数据

核心思想：扩容不是"停下来等"，而是"大家一起帮忙搬"。
```

---

## 九、size() 方法的实现原理

### JDK 7 vs JDK 8

```
JDK 7：
  - 每个 Segment 维护自己的 count
  - size() = Σ Segment[i].count
  - 先不加锁累加 3 次，如果 modCount 没变就认为准确
  - 否则加所有 Segment 的锁再统计

JDK 8：
  - baseCount + CounterCell[] 分段计数（类似 LongAdder）
  - 无竞争时直接 CAS 更新 baseCount
  - 有竞争时分散到 CounterCell[] 的各个槽位
  - size() = baseCount + Σ CounterCell[i].value
```

### JDK 8 的 CounterCell 计数机制

```java
// 核心字段
private transient volatile long baseCount;
private transient volatile CounterCell[] counterCells;

// CounterCell 结构
@sun.misc.Contended  // 缓存行填充，防止伪共享
static final class CounterCell {
    volatile long value;
    CounterCell(long x) { value = x; }
}
```

```
CounterCell[] 的设计思路（LongAdder 同款）：

        baseCount
           ↑
           │ CAS（无竞争时）
           │
    ┌──────┴──────┐
    │             │
  CAS 成功      CAS 失败（有竞争）
                   │
                   ↓
         ┌─────┬─────┬─────┬─────┐
         │ CC0 │ CC1 │ CC2 │ CC3 │  ← CounterCell[]
         │ +1  │ +1  │ +1  │ +1  │
         └─────┴─────┴─────┴─────┘
           ↑     ↑     ↑     ↑
         线程A  线程B  线程C  线程D（各自更新不同的槽位）

size() = baseCount + CC0.value + CC1.value + CC2.value + CC3.value
```

### addCount 方法

```java
// 简化版的 addCount（每次 put 后调用）
private final void addCount(long x, int check) {
    CounterCell[] as; long b, s;
    // 先尝试 CAS 更新 baseCount
    if ((as = counterCells) != null ||
        !U.compareAndSwapLong(this, BASECOUNT, b = baseCount, s = b + x)) {
        // CAS 失败 → 有竞争 → 使用 CounterCell 分段计数
        CounterCell a; long v; int m;
        boolean uncontended = true;
        // 用 ThreadLocalRandom 分散到不同槽位
        int h = ThreadLocalRandom.getProbe();
        // CAS 更新对应槽位
        // 如果槽位也竞争失败 → fullAddCount（扩容数组或重试）
    }
    // check > 0 时判断是否需要扩容
    if (check >= 0) {
        Node<K,V>[] tab, nt; int n, sc;
        while (s >= (long)(sc = sizeCtl) && (tab = table) != null
                && (n = tab.length) < MAXIMUM_CAPACITY) {
            // 触发扩容
            transfer(tab, nt);
        }
    }
}
```

### 为什么不用 AtomicInteger

```
AtomicInteger 在高并发下的问题：
  所有线程 CAS 同一个变量 → 大量 CAS 失败 → 自旋重试 → CPU 浪费

CounterCell[] 的优势：
  把计数分散到多个槽位 → 不同线程操作不同的槽位 → CAS 冲突大幅减少
  → 空间换时间（和 LongAdder 一样的思路）

@Contended 注解：
  让 CounterCell 独占一个缓存行，避免伪共享（False Sharing）
  → CPU 缓存行通常 64 字节，@Contended 填充到 > 64 字节
```

### size() 和 mappingCount() 的区别

```java
public int size() {
    long n = sumCount();
    return ((n < 0L) ? 0 : (n > (long)Integer.MAX_VALUE) ? Integer.MAX_VALUE : (int)n);
}

public long mappingCount() {
    long n = sumCount();
    return (n < 0L) ? 0L : n;  // 返回 long，不会溢出
}
```

```
sumCount() 的计算：
  long sum = baseCount;
  if ((as = counterCells) != null) {
      for (CounterCell a : as)
          if (a != null) sum += a.value;
  }
  return sum;

区别：
  size()       → 返回 int，元素超过 Integer.MAX_VALUE 时截断
  mappingCount() → 返回 long，适合超大规模 Map
  → 两者计算逻辑完全相同，只是返回类型不同
```

---

## 十、与 Hashtable 和 synchronizedMap 的深度对比

### 三者的锁机制

```
Hashtable：
  每个 public 方法都加了 synchronized → 全表锁
  put() 时整个 Hashtable 被锁定，其他线程全部阻塞

  public synchronized V put(K key, V value) {
      // 整个方法被 synchronized 保护
  }

Collections.synchronizedMap：
  内部持有一个 mutex 对象（可以是外部传入的任意锁，默认是 this）
  每个方法都 synchronized(mutex)

  private static class SynchronizedMap<K,V> implements Map<K,V> {
      final Object mutex;
      public V put(K key, V value) {
          synchronized (mutex) {
              return m.put(key, value);
          }
      }
  }

ConcurrentHashMap：
  桶级锁（synchronized 锁住单个桶的头节点）
  空桶插入用 CAS（完全无锁）
  读操作完全无锁（volatile 保证可见性）
```

### 性能对比

```
假设 16 个线程同时写一个 Map：

Hashtable / synchronizedMap：
  线程 A:  [synchronized 整个方法 ──────]  ← 10ms
  线程 B:  [等待 10ms][synchronized ──────]  ← 10ms
  ...
  总时间 ≈ 16 × 10ms = 160ms

ConcurrentHashMap（16 个桶，线程分散到不同桶）：
  线程 A: [CAS 或 synchronized 桶1 ──]  ← 1ms
  线程 B: [CAS 或 synchronized 桶2 ──]  ← 1ms
  线程 C: [CAS 或 synchronized 桶3 ──]  ← 1ms
  ...
  总时间 ≈ 1ms（完全并行）

→ 写入性能差距可达 100 倍以上
```

### 对比表格

| 维度 | Hashtable | synchronizedMap | ConcurrentHashMap |
|------|-----------|-----------------|-------------------|
| **锁机制** | 方法级 synchronized | 对象级 synchronized(mutex) | 桶级 synchronized + CAS |
| **并发度** | 1（串行） | 1（串行） | table.length（并行） |
| **读性能** | 需要获取锁 | 需要获取锁 | 无锁（volatile 读） |
| **null 支持** | 不允许 | 取决于内部 Map | 不允许 |
| **迭代器** | fail-fast | fail-fast | 弱一致性 |
| **内存开销** | 低 | 低 | 略高（CounterCell 等） |
| **是否推荐** | 已过时 | 仅在简单场景 | **推荐** |

### 为什么 ConcurrentHashMap 不允许 null

```java
// HashMap 中：
map.get(key) 返回 null
  → 可能是 key 不存在
  → 可能是 key 存在但 value = null
  → 需要 containsKey() 区分（单线程安全）

// ConcurrentHashMap 中：
map.get(key) 返回 null
  → key 不存在 还是 value = null？
  → containsKey() 和 get() 之间可能被其他线程修改
  → 无法可靠区分

所以 ConcurrentHashMap 直接不允许 null，
get() 返回 null 一定表示 key 不存在。
```

---

## 十一、JDK 8+ 原子操作方法

ConcurrentHashMap 在 JDK 8 中新增了一批原子操作方法，这些方法在并发场景下非常关键。

### computeIfAbsent

```java
// 语法
V computeIfAbsent(K key, Function<? super K, ? extends V> mappingFunction)

// 典型场景：缓存 + 懒加载
ConcurrentHashMap<String, List<String>> cache = new ConcurrentHashMap<>();

// 如果 key 不存在，计算 value 并插入（整个过程原子）
cache.computeIfAbsent("users", k -> loadFromDB(k));

// 多值 Map 的经典写法
cache.computeIfAbsent("fruits", k -> new ArrayList<>()).add("apple");

// 与 putIfAbsent 的区别：
map.putIfAbsent("A", 1);           // 只接受常量值
map.computeIfAbsent("A", k -> 1);  // 可以接受计算函数（懒执行）
```

```
computeIfAbsent 的原子性保证：
  1. 检查 key 是否存在
  2. 如果不存在，调用 mappingFunction 计算 value
  3. 插入新节点
  → 整个过程在 synchronized 块内完成
  → 其他线程不会看到"半截"状态
  → mappingFunction 不会被其他线程的 put 干扰
```

### compute

```java
// 语法
V compute(K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)

// 计数器的安全写法
map.compute("counter", (k, v) -> v == null ? 1 : v + 1);

// 更新用户信息
map.compute(userId, (k, oldProfile) -> {
    if (oldProfile == null) return newProfile;
    return oldProfile.merge(newProfile);
});
```

```
compute 的执行时机：
  key 不存在：remappingFunction(key, null)
  key 存在：  remappingFunction(key, oldValue)
  → 如果函数返回 null → 删除该 key
  → 整个计算过程在 synchronized 内完成
```

### merge

```java
// 语法
V merge(K key, V value, BiFunction<? super V, ? super V, ? extends V> remappingFunction)

// 最简单的计数器（一行搞定）
map.merge("counter", 1, Integer::sum);

// 合并两个 Set
map.merge("tags", Set.of("java"), (old, newVal) -> {
    Set<String> merged = new HashSet<>(old);
    merged.addAll(newVal);
    return merged;
});
```

```
merge 的执行逻辑：
  key 不存在  → 插入 value
  key 存在    → remappingFunction(oldValue, value) → 更新 value
  → 如果函数返回 null → 删除该 key
```

### 所有原子方法汇总

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// JDK 8 新增的原子方法
map.putIfAbsent("A", 1);                  // 不存在时插入
map.computeIfAbsent("B", k -> 1);         // 不存在时计算并插入
map.computeIfPresent("C", (k, v) -> v+1); // 存在时计算
map.compute("D", (k, v) -> v==null?1:v+1);// 统一计算（插入或更新）
map.merge("E", 1, Integer::sum);          // 合并值（常用于计数器）
map.replace("F", 1, 2);                   // CAS 替换（旧值匹配才替换）
map.replace("F", 2);                      // 存在时替换

// 批量操作（JDK 8 新增，用于大数据量场景）
map.forEach(1, (k, v) -> process(k, v));  // 并行 forEach
map.search(1, (k, v) -> v > 100 ? v : null);  // 并行搜索
map.reduceValues(1, Integer::sum);        // 并行聚合
```

### 批量操作说明

```java
// 批量操作的共同参数：parallelismThreshold
// 当元素数量 ≥ 此值时，使用 ForkJoinPool 并行执行

// forEach（阈值 = 2，即元素 ≥ 2 时并行）
map.forEach(2, (k, v) -> System.out.println(k + "=" + v));

// 搜索（找到就停止，返回第一个非 null 结果）
String result = map.search(2, (k, v) -> v > 100 ? k : null);

// 归约（聚合计算）
int sum = map.reduceValuesToInt(2, Integer::intValue, 0, Integer::sum);

// 映射 + 归约
int count = map.reduceValues(2, v -> 1, Integer::sum);  // 统计数量
```

---

## 十二、TreeBin 的读写锁机制

```
红黑树节点用 TreeBin 包裹，TreeBin 内部使用轻量级读写锁：

锁状态（lockState 的位运算）：
  WRITER      = 1（有写线程持有锁）
  WAITER      = 2（有线程在等待写锁）
  READER      = 4（读线程计数，左移 2 位开始计数）

读操作：
  if ((lockState & (WRITER | WAITER)) == 0)
    → 无写竞争，直接读（无锁）
    → CAS 增加 READER 计数
  else
    → 有写操作，获取读锁（竞争）

写操作（插入/删除树节点）：
  CAS 将 lockState |= WRITER
  → 如果 CAS 失败 → 进入等待（WAITER）
  → 等待所有读线程释放读锁后执行写操作
  → 完成后释放写锁（lockState ^= WRITER）

优势：
  - 读多写少时，读线程几乎无锁
  - 写线程排他，保证树的正确性
  - 比 synchronized 更细粒度的控制
```

---

## 十三、最佳实践

### 1. 构造时指定容量

```java
// 错误：默认容量 16，插入大量元素时频繁扩容
ConcurrentHashMap<String, Object> bad = new ConcurrentHashMap<>();

// 正确：预估容量，减少扩容
int expectedSize = 1000;
ConcurrentHashMap<String, Object> good = new ConcurrentHashMap<>(expectedSize);

// 更精确：考虑负载因子 0.75
int expectedSize = 1000;
int capacity = (int) Math.ceil(expectedSize / 0.75) + 1;
ConcurrentHashMap<String, Object> precise = new ConcurrentHashMap<>(capacity);
```

### 2. 用原子方法替代 check-then-act

```java
// 错误：非原子的复合操作
if (!map.containsKey(key)) {
    map.put(key, value);           // 两步之间可能被其他线程插入
}

// 错误：非原子的读-改-写
Integer count = map.get(key);
if (count == null) count = 0;
map.put(key, count + 1);          // 三步之间可能被其他线程修改

// 正确：原子操作
map.putIfAbsent(key, value);
map.merge(key, 1, Integer::sum);
```

### 3. 用 computeIfAbsent 做懒加载缓存

```java
// 错误：非原子缓存（多线程下可能重复计算）
V cached = cache.get(key);
if (cached == null) {
    cached = expensiveComputation(key);  // 可能被多个线程同时执行
    cache.put(key, cached);
}

// 正确：原子缓存
V cached = cache.computeIfAbsent(key, k -> expensiveComputation(k));
// mappingFunction 只会被执行一次（即使多线程同时调用）
```

### 4. 不要用 Collections.synchronizedMap 包装 ConcurrentHashMap

```java
// 错误：无意义的包装，反而增加开销
Map<String, Integer> bad = Collections.synchronizedMap(new ConcurrentHashMap<>());

// 正确：直接用 ConcurrentHashMap
Map<String, Integer> good = new ConcurrentHashMap<>();
```

### 5. 遍历时的注意事项

```java
// 弱一致性：遍历过程中其他线程的修改可能看不到
// 但不会抛 ConcurrentModificationException

// 安全的遍历 + 修改
for (Iterator<Map.Entry<String, Integer>> it = map.entrySet().iterator();
     it.hasNext(); ) {
    Map.Entry<String, Integer> entry = it.next();
    if (entry.getValue() < 0) {
        it.remove();  // 用迭代器的 remove 方法
    }
}

// JDK 8 的并发 forEach（内部处理并发）
map.forEach((k, v) -> {
    // 这里的修改对其他线程的 forEach 可见性不确定
    // 但对后续的 get() 一定可见
});
```

### 6. 超大规模 Map 用 mappingCount()

```java
// 当 Map 元素可能超过 Integer.MAX_VALUE 时
long size = map.mappingCount();  // 返回 long

// 不要这样用：
int size = map.size();           // 超过 21 亿会截断
```

### 7. 选择合适的并发 Map

```
读多写少，元素少且小 → CopyOnWriteArrayList + 手动维护映射
读多写少，需要有序   → ConcurrentSkipListMap
读写混合，高并发     → ConcurrentHashMap（首选）
需要复杂并发操作     → ConcurrentHashMap + compute/merge 原子方法
分布式缓存           → Caffeine / Redis（不是本地 Map 能解决的）
```

---

## 十四、面试高频问题速查

### 基础问题

| 问题 | 答案要点 |
|------|----------|
| ConcurrentHashMap 是线程安全的吗？ | 是，保证并发场景下的数据一致性 |
| 允许 null 键/值吗？ | 不允许，抛出 NullPointerException |
| JDK 7 和 JDK 8 的区别？ | JDK 7：Segment 分段锁（ReentrantLock）；JDK 8：CAS + synchronized 桶级锁 |
| 读操作需要加锁吗？ | 不需要，靠 volatile 保证可见性 |
| 迭代器是 fail-fast 吗？ | 不是，是弱一致性（不抛异常，可能看不到最新修改） |

### 深入问题

| 问题 | 答案要点 |
|------|----------|
| 为什么 get() 可以不加锁？ | Node 的 val 和 next 都是 volatile；table 也是 volatile 引用；get 读到的始终是"完整"状态 |
| 为什么不允许 null？ | 并发环境下无法区分"key 不存在"和"value = null"，containsKey() 和 get() 之间可能被修改 |
| 写操作的锁粒度有多细？ | JDK 8 中锁粒度是一个桶（链表/树的头节点），不同桶的写完全并行 |
| 空桶插入需要加锁吗？ | 不需要，用 CAS 原子插入（无锁） |
| treeifyBin 时怎么保证安全？ | synchronized 锁住头节点，链表转 TreeBin 的过程是排他的 |
| 扩容期间 put/get 的行为？ | put 遇到 ForwardingNode 会协助扩容（helpTransfer）；get 遇到会去新 table 查找 |

### 核心原理问题

| 问题 | 答案要点 |
|------|----------|
| size() 怎么保证并发下的准确性？ | baseCount + CounterCell[] 分段计数，类似 LongAdder，CAS 无竞争 → 分段 CAS 有竞争 |
| 为什么用 CounterCell 不用 AtomicInteger？ | AtomicInteger 高并发下 CAS 竞争激烈；CounterCell 把计数分散到多个槽位减少冲突 |
| 多个线程如何协同扩容？ | 全局 transferIndex（CAS 递减），每个线程领取一段迁移任务（stride 个桶） |
| ForwardingNode 的作用？ | 标记已迁移的桶；读操作遇到它自动转发到新 table；写操作遇到它协助扩容 |
| sizeCtl 字段的含义？ | >0：初始化后的扩容阈值；=0：默认；=-1：正在初始化；< -1：正在扩容，高 16 位标识 |
| 红黑树的并发控制？ | TreeBin 内置轻量级读写锁（位运算），读多写少时读线程几乎无锁 |

### 对比问题

| 问题 | 答案要点 |
|------|----------|
| 和 Hashtable 的区别？ | Hashtable 全表锁、性能差、已过时；CHM 分段/分桶锁、高性能 |
| 和 synchronizedMap 的区别？ | synchronizedMap 全表锁（synchronized(mutex)）；CHM 桶级锁 + CAS |
| 和 ConcurrentSkipListMap 的区别？ | CHM 无序 O(1)，CSM 有序 O(log n)；CSM 基于跳表 |
| 为什么 JDK 8 从 Segment 改成 CAS+synchronized？ | 锁粒度更细（桶级）、JVM 对 synchronized 有优化、内存开销更小 |

### 场景题

| 问题 | 答案要点 |
|------|----------|
| 多线程下安全的计数器怎么写？ | map.merge(key, 1, Integer::sum) 或 map.compute(key, (k,v) -> v==null?1:v+1) |
| 多线程下安全的懒加载缓存？ | cache.computeIfAbsent(key, k -> expensiveComputation(k)) |
| 如何遍历 ConcurrentHashMap 并删除元素？ | 用迭代器的 remove() 方法，或用 map.remove(key) 在 forEach 中 |
| ConcurrentHashMap 适合做分布式缓存吗？ | 不适合，它是本地缓存；分布式缓存用 Redis/Caffeine |
| 如果需要一个线程安全的有序 Map？ | ConcurrentSkipListMap（跳表实现，O(log n)） |

### 陷阱题

| 问题 | 答案要点 |
|------|----------|
| size() 返回的值一定准确吗？ | 是精确快照（baseCount + Σ CounterCell），但返回后可能已被修改 |
| computeIfAbsent 的 mappingFunction 会执行几次？ | 只执行一次（在 synchronized 内），即使多线程同时调用 |
| ConcurrentHashMap 的 put 和 get 能保证原子性吗？ | 单个 put/get 是原子的，但 put+get 的复合操作不是（需要用 compute） |
| 可以用 ConcurrentHashMap 实现一个线程安全的 Set 吗？ | 可以：ConcurrentHashMap.newKeySet()，底层是 CHM + PRESENT 占位值 |
