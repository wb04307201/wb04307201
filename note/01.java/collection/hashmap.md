# HashMap 深入

> 目标：彻底搞懂 HashMap 的底层实现，包括 put 流程、扩容机制、哈希函数设计、线程安全问题。

---

## 一、底层数据结构

### JDK 8 的 HashMap

```
HashMap = Node[] table（数组 + 链表 + 红黑树）

table[0]  → null
table[1]  → [K1,V1] → [K2,V2] → null          ← 链表（长度 < 8）
table[2]  → null
table[3]  → [K3,V3] → [K4,V4]                  ← 链表
table[4]  → null
table[5]  → [K5,V5]                            ← 单个节点
             ↙    ↘
          [K6]   [K7]                           ← 红黑树（链表长度 ≥ 8 且 table.length ≥ 64）
            ↙  ↘
         [K8]  [K9]
...
table[n-1] → null
```

**Node 结构**：
```java
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;      // key 的哈希值
    final K key;
    V value;
    Node<K,V> next;      // 指向链表下一个节点
}
```

### 为什么用红黑树

```
哈希冲突严重时，链表退化为 O(n) 查找。
红黑树保证 O(log n) 查找，是 JDK 8 的核心优化。

转换条件：
  链表 → 红黑树：链表长度 ≥ 8 且 table.length ≥ 64
  红黑树 → 链表：树节点数 ≤ 6（留 2 的缓冲，避免频繁转换）

为什么是 8 和 6？
  根据泊松分布，链表长度达到 8 的概率约 0.00000006，极低。
  设置不同的阈值（8 和 6）防止在边界处反复转换。
```

---

## 二、hash() 函数

```java
// JDK 8 的 hash 函数
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

**为什么高 16 位异或低 16 位**：

```
HashMap 用 (n-1) & hash 定位桶（n 是 table 长度，2 的幂）。
当 n 较小时（如 16），只有 hash 的低 4 位参与运算，高位信息被浪费。
高 16 位 ^ 低 16 位 → 让高位也参与定位，减少冲突。

示例（n = 16）：
  hash = 0x0000_0000_0000_0000_0110_0101_1010_0011
  (n-1)= 0x0000_0000_0000_0000_0000_0000_0000_1111
  
  不做扰动：只有最后 4 位 0011 有效 → 桶 3
  扰动后：高位信息混入低 4 位 → 分布更均匀
```

---

## 三、容量为什么必须是 2 的幂

```java
// 定位桶的公式
int index = hash & (n - 1);  // n 是 table.length
```

**n 是 2 的幂时**：
```
n     = 16 = 0b0001_0000
n - 1 = 15 = 0b0000_1111    ← 低位全是 1

hash & (n-1) 等价于 hash % n，但位运算比取模快得多。
```

**n 不是 2 的幂时**：
```
n     = 15 = 0b0000_1111
n - 1 = 14 = 0b0000_1110    ← 低位有 0

hash & 14 → 第 0 位永远是 0 → 奇数桶永远为空 → 一半桶被浪费
```

**如果传入的初始容量不是 2 的幂**：
```java
// HashMap 构造函数会自动调整为不小于 capacity 的最小 2 的幂
new HashMap<>(10);  // 实际容量 = 16
new HashMap<>(33);  // 实际容量 = 64
```

---

## 四、put() 完整流程

```java
map.put(key, value);
```

```
put(key, value)
  │
  ├─ 1. 计算 hash = hash(key.hashCode())
  │
  ├─ 2. 如果 table 为空 → 初始化（resize）
  │
  ├─ 3. 定位桶：index = hash & (n-1)
  │     │
  │     ├─ table[index] == null → 直接创建新 Node 放入
  │     │
  │     └─ table[index] != null → 有冲突
  │           │
  │           ├─ 4. 如果第一个节点的 key 相同 → 覆盖 value
  │           │
  │           ├─ 5. 如果是红黑树节点 → 调用红黑树插入
  │           │
  │           └─ 6. 如果是链表 → 遍历链表
  │                 │
  │                 ├─ 找到相同 key → 覆盖 value
  │                 │
  │                 └─ 遍历到末尾未找到 → 尾插法插入新节点
  │                       │
  │                       └─ 7. 判断是否需要树化
  │                             if (链表长度 ≥ 8)
  │                               if (table.length < 64) → resize()（优先扩容）
  │                               else → treeifyBin()（转为红黑树）
  │
  ├─ 8. size++，modCount++
  │
  └─ 9. 如果 size > threshold → resize()（扩容）
```

### JDK 7 vs JDK 8 的插入方式

```
JDK 7：头插法
  新节点插到链表头部 → 扩容时链表会反转 → 多线程下可能形成环 → 死循环

JDK 8：尾插法
  新节点插到链表尾部 → 扩容时保持原顺序 → 不会形成环
  但多线程下仍可能数据覆盖（一个 put 被另一个覆盖）
```

---

## 五、resize() 扩容

```java
// 扩容条件：size > threshold
// threshold = capacity * loadFactor
// 默认 loadFactor = 0.75
// 默认 capacity = 16 → threshold = 12
// 当第 13 个元素插入时触发扩容
```

### 扩容过程

```
旧 table（容量 16）                    新 table（容量 32）
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │13 │14 │15 │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │13 │14 │15 │16 │17 │18 │19 │20 │21 │22 │23 │24 │25 │26 │27 │28 │29 │30 │31 │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

扩容时每个节点的去向判断（核心优化）：
  if ((hash & oldCap) == 0)
    → 留在原位置（index 不变）
  else
    → 去 index + oldCap 的位置

示例：hash = 17, oldCap = 16
  17 & 16 = 16 ≠ 0 → 去 17 + 16 = 33？不对
  实际：新 index = hash & (newCap-1) = 17 & 31 = 17
  旧 index = 17 & 15 = 1
  17 - 1 = 16 = oldCap → 去 1 + 16 = 17 ✅
```

### 扩容时链表拆分（JDK 8 优化）

```
旧桶 index = 3，链表：[A:hash=3] → [B:hash=19] → [C:hash=35] → null
oldCap = 16, newCap = 32

拆分规则：hash & oldCap 是否为 0
  A: 3  & 16 = 0  → 留在 newTable[3]
  B: 19 & 16 = 16 → 去 newTable[3+16] = newTable[19]
  C: 35 & 16 = 0  → 留在 newTable[3]

结果：
  newTable[3]  → [A] → [C] → null    （保持原顺序）
  newTable[19] → [B] → null

不需要 rehash！不需要重新计算 index！
只需看 hash 的第 log2(oldCap) 位是 0 还是 1。
```

---

## 六、关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_INITIAL_CAPACITY` | 16 | 初始容量 |
| `MAXIMUM_CAPACITY` | 2^30 | 最大容量 |
| `DEFAULT_LOAD_FACTOR` | 0.75 | 负载因子（空间与时间的权衡） |
| `TREEIFY_THRESHOLD` | 8 | 链表转红黑树的阈值 |
| `UNTREEIFY_THRESHOLD` | 6 | 红黑树退化为链表的阈值 |
| `MIN_TREEIFY_CAPACITY` | 64 | 树化的最小 table 长度（小于此值优先扩容） |

### loadFactor 怎么选

```
默认 0.75 是时间和空间的最佳平衡点。

调高（如 0.9）：
  + 节省空间（扩容更晚）
  - 冲突增多，查找变慢

调低（如 0.5）：
  + 冲突减少，查找更快
  - 浪费空间（很多空桶）
  - 扩容更频繁

除非极端场景（内存紧张或性能极致），不要改默认值。
```

---

## 七、线程安全问题

HashMap **不是线程安全的**。多线程下有两个经典问题：

### 问题 1：JDK 7 的死循环（头插法 + 扩容时链表反转）

```
线程 A 和线程 B 同时触发扩容，对同一个桶做 head-insert：

原始链表：[A] → [B] → null

线程 A 执行到一半被挂起：
  新链表头指向 A，A.next 还未设置

线程 B 完成扩容：
  新链表：[B] → [A] → null（反转了）

线程 A 恢复执行：
  设置 A.next = B → [A] → [B] → [A] → ... 形成环

后续 get() 遍历这个桶 → 死循环，CPU 100%
```

### 问题 2：JDK 8 的数据覆盖（尾插法解决了死循环，但有新问题）

```
线程 A 和线程 B 同时 put，hash 相同，定位到同一个空桶：

线程 A：判断 table[index] == null，准备插入
线程 B：判断 table[index] == null，准备插入
线程 B：先执行，table[index] = NodeB
线程 A：后执行，table[index] = NodeA  ← NodeB 被覆盖！

结果：线程 B 的数据丢失。
```

### 解决方案

| 方案 | 适用场景 |
|------|----------|
| **ConcurrentHashMap** | 多线程读写，推荐首选 |
| `Collections.synchronizedMap(new HashMap<>())` | 简单包装，全表锁，性能差 |
| `Hashtable` | 已过时，不推荐 |
| 外部加锁 | 需要复合操作时（如 check-then-act） |

---

## 八、LinkedHashMap

LinkedHashMap 继承自 HashMap，在哈希表的基础上增加了一条**双向链表**，用于维护插入顺序或访问顺序。

### 底层结构

```
HashMap 部分（和 HashMap 完全一样）：
table[0] → [K1,V1] → null
table[1] → [K2,V2] → [K3,V3] → null
...

双向链表（额外维护）：
head ⇄ [K1,V1] ⇄ [K2,V2] ⇄ [K3,V3] ⇄ tail
         ↑ before/after 指针串联所有节点
```

### 两种模式

```java
// 插入顺序（默认）：遍历顺序 = 插入顺序
LinkedHashMap<String, Integer> map = new LinkedHashMap<>();
map.put("C", 3); map.put("A", 1); map.put("B", 2);
map.forEach((k, v) -> System.out.print(k + " "));  // C A B

// 访问顺序（accessOrder = true）：遍历顺序 = 最近访问顺序
LinkedHashMap<String, Integer> lru = new LinkedHashMap<>(16, 0.75f, true);
lru.put("C", 3); lru.put("A", 1); lru.put("B", 2);
lru.get("C");  // 访问 C，C 移到末尾
lru.forEach((k, v) -> System.out.print(k + " "));  // A B C
```

### 实现 LRU 缓存

```java
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    public LRUCache(int capacity) {
        super(capacity, 0.75f, true);  // accessOrder = true
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;  // 超过容量时自动移除最久未访问的元素
    }
}

LRUCache<String, Integer> cache = new LRUCache<>(3);
cache.put("A", 1);
cache.put("B", 2);
cache.put("C", 3);
cache.get("A");        // 访问 A，A 变为最近
cache.put("D", 4);     // 容量超限，移除最久未访问的 B
// cache = {C=3, A=1, D=4}
```

---

## 九、HashSet 原理

HashSet 的底层就是一个 HashMap，元素存在 key 上，value 统一用一个 `PRESENT` 对象占位。

```java
// HashSet 源码（简化）
public class HashSet<E> extends AbstractSet<E> {
    private transient HashMap<E, Object> map;
    private static final Object PRESENT = new Object();  // 所有 key 共享的 value

    public boolean add(E e) {
        return map.put(e, PRESENT) == null;  // put 返回 null 表示新插入
    }

    public boolean contains(Object o) {
        return map.containsKey(o);
    }

    public boolean remove(Object o) {
        return map.remove(o) == PRESENT;
    }
}
```

> **结论**：理解 HashMap 就理解了 HashSet。HashSet 的所有行为（哈希冲突、扩容、红黑树转换）都委托给内部的 HashMap。

---

## 十、JDK 8 新增方法

JDK 8 为 Map 接口新增了一批实用方法，在日常开发中使用频率极高：

```java
Map<String, Integer> map = new HashMap<>();

// getOrDefault：key 不存在时返回默认值（替代 null 检查）
int count = map.getOrDefault("A", 0);

// forEach：遍历（替代 for + entrySet）
map.forEach((k, v) -> System.out.println(k + "=" + v));

// putIfAbsent：key 不存在时才插入
map.putIfAbsent("A", 1);

// computeIfAbsent：key 不存在时计算并插入（常用于缓存和多值 Map）
map.computeIfAbsent("B", k -> expensiveComputation(k));

// 多值 Map 的经典写法
Map<String, List<String>> multiMap = new HashMap<>();
multiMap.computeIfAbsent("fruits", k -> new ArrayList<>()).add("apple");

// computeIfPresent：key 存在时重新计算值
map.computeIfPresent("A", (k, v) -> v + 1);

// compute：无论是否存在都计算（统一处理插入和更新）
map.compute("A", (k, v) -> v == null ? 1 : v + 1);

// merge：合并值（常用于计数器）
map.merge("A", 1, Integer::sum);  // 不存在则设为 1，存在则加 1

// replaceAll：替换所有值
map.replaceAll((k, v) -> v * 2);
```

> **与 ConcurrentHashMap 的关系**：这些方法在 `ConcurrentHashMap` 中是**原子**的（整个 compute/merge 操作在锁内完成），而在 `HashMap` 中不是原子的。→ 详见 [并发集合](concurrent.md) 第五节

---

## 十一、面试高频问题速查

| 问题 | 答案要点 |
|------|----------|
| HashMap 的底层实现 | JDK 8：数组 + 链表 + 红黑树 |
| put() 的流程 | hash → 定位桶 → 空桶直接插 → 冲突则链表/红黑树 → size > threshold 则扩容 |
| 为什么容量是 2 的幂 | `hash & (n-1)` 等价取模且更快；避免奇数桶浪费 |
| hash() 为什么扰动 | 让高位参与定位，减少冲突 |
| 链表什么时候转红黑树 | 长度 ≥ 8 且 table.length ≥ 64（否则优先扩容） |
| 扩容时怎么处理链表 | `hash & oldCap` 判断去向，不需要 rehash |
| JDK 7 和 8 的区别 | 头插法 → 尾插法（解决死循环）；新增红黑树优化 |
| HashMap 线程安全吗 | 不安全。JDK 7 死循环，JDK 8 数据覆盖 |
| HashMap 和 Hashtable | Hashtable 全表锁、不支持 null、已过时 |
| HashMap 和 TreeMap | HashMap O(1) 无序，TreeMap O(log n) 有序 |
| HashMap 和 ConcurrentHashMap | ConcurrentHashMap JDK 7 分段锁 / JDK 8 CAS+synchronized，线程安全 → [详见](concurrent.md) |
| 为什么 HashMap 允许 null 键 | 特殊处理：null 键的 hash 固定为 0，放在 table[0] |
| 可变对象能作 key 吗 | 技术上可以，但如果 put 后修改了 key 的 hashCode 字段，get() 会找不到（hash 变了，去了不同的桶） |
