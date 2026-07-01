<!--
module:
  parent: java
  slug: java/collection/linked-hash-set
  type: article
  category: 主模块子文章
  summary: LinkedHashSet 底层基于 LinkedHashMap 的有序 Set 实现。
-->

# LinkedHashSet 学习笔记

## 一、底层 LinkedHashMap 实现

`LinkedHashSet` 的底层完全依赖 `LinkedHashMap` 实现。从源码可以看出，它继承自 `HashSet`，但构造函数中传入的是 `LinkedHashMap` 实例：

```java
public class LinkedHashSet<E>
    extends HashSet<E>
    implements Set<E>, Cloneable, java.io.Serializable {

    // 调用父类 HashSet 的构造函数，传入 LinkedHashMap
    public LinkedHashSet(int initialCapacity, float loadFactor) {
        super(initialCapacity, loadFactor, true); // true 表示使用 LinkedHashMap
    }
}
```

`HashSet` 内部有一个 `HashMap` 类型的成员 `map`，所有元素都作为 `map` 的 key 存储，value 统一为一个静态常量 `PRESENT`：

```java
public class HashSet<E> extends AbstractSet<E>
    implements Set<E>, Cloneable, java.io.Serializable {

    private transient HashMap<E, Object> map;

    // 所有元素存储为 map 的 key，value 统一为该对象
    private static final Object PRESENT = new Object();

    // 构造函数（仅包访问权限）
    HashSet(int initialCapacity, float loadFactor, boolean dummy) {
        map = new LinkedHashMap<>(initialCapacity, loadFactor);
    }
}
```

这种设计模式称为 **适配器模式** —— `HashSet` 本身不存储数据，而是将数据存储操作委托给内部的 `HashMap`。

```java
// 添加元素 —— 实际上调用 map.put(key, PRESENT)
public boolean add(E e) {
    return map.put(e, PRESENT) == null;
}

// 判断是否存在 —— 实际上调用 map.containsKey(key)
public boolean contains(Object o) {
    return map.containsKey(o);
}

// 删除元素 —— 实际上调用 map.remove(key)
public boolean remove(Object o) {
    return map.remove(o) == PRESENT;
}
```

**核心结论：** `LinkedHashSet` 本质上是一个 `LinkedHashMap` 的 "key 视图"，value 全部为无意义的 `PRESENT` 占位符。

---
---

## 二、保持插入顺序的原理（双向链表）

`LinkedHashMap` 在 `HashMap` 的基础上，每个 `Entry` 额外维护了 `before` 和 `after` 两个引用，形成一条 **双向链表**：

```java
static class Entry<K,V> extends HashMap.Node<K,V> {
    Entry<K,V> before;   // 指向前一个节点
    Entry<K,V> after;    // 指向后一个节点

    Entry(int hash, K key, V value, Node<K,V> next) {
        super(hash, key, value, next);
    }
}
```

### 链表结构示意图

```
head → [Entry1] ↔ [Entry2] ↔ [Entry3] ↔ [Entry4] → tail
        (先插入)                            (后插入)
```

- `head` 指向最早插入的节点
- `tail` 指向最新插入的节点
- 遍历 `LinkedHashSet` 时，沿着双向链表从头到尾遍历，因此遍历顺序 == 插入顺序

### 插入新元素时链表的更新

```java
// LinkedHashMap 新增节点后，将其追加到链表尾部
void linkNodeLast(LinkedHashMap.Entry<K,V> p) {
    LinkedHashMap.Entry<K,V> last = tail;
    tail = p;          // 新节点成为 tail
    if (last == null)
        head = p;      // 如果是第一个节点，head 也指向它
    else {
        p.before = last;  // 新节点的 before 指向前 tail
        last.after = p;   // 前 tail 的 after 指向新节点
    }
}
```

### 访问顺序模式（可选）

`LinkedHashMap` 还支持 **访问顺序**（accessOrder），构造函数中可设置：

```java
// accessOrder = true：按访问顺序排列（最近访问的在尾部）
LinkedHashMap<String, Integer> map = new LinkedHashMap<>(16, 0.75f, true);
```

当 `accessOrder = true` 时，每次 `get()` 操作都会将对应节点移到链表尾部。这是实现 **LRU Cache** 的基础：

```java
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    public LRUCache(int capacity) {
        super(capacity, 0.75f, true); // 开启访问顺序
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity; // 超出容量则淘汰最老的
    }
}
```

> 注意：`LinkedHashSet` 的构造函数没有暴露 `accessOrder` 参数，因此 `LinkedHashSet` **只能** 保持插入顺序，不支持访问顺序。

---

## 三、与 HashSet 的对比

| 对比维度 | HashSet | LinkedHashSet |
|---------|---------|---------------|
| **底层结构** | HashMap | LinkedHashMap（HashMap + 双向链表） |
| **顺序保证** | 无序，遍历顺序不保证 | 按插入顺序遍历 |
| **内存开销** | 较小（每个 Entry 只有 next 指针） | 较大（每个 Entry 多了 before、after 指针） |
| **增删改查时间复杂度** | O(1) | O(1) |
| **遍历时性能** | 取决于桶数组大小（可能遍历大量空桶） | 只遍历链表中的有效节点，与 size 成正比 |
| **是否允许 null** | 允许一个 null | 允许一个 null |
| **线程安全** | 否 | 否 |
| **适用场景** | 不关心顺序的去重场景 | 需要保持插入顺序的去重场景 |

### 代码对比

```java
Set<String> hashSet = new HashSet<>();
hashSet.add("C");
hashSet.add("A");
hashSet.add("B");
System.out.println(hashSet);
// 输出：[A, B, C]（顺序不确定，取决于哈希值和扩容）

Set<String> linkedHashSet = new LinkedHashSet<>();
linkedHashSet.add("C");
linkedHashSet.add("A");
linkedHashSet.add("B");
System.out.println(linkedHashSet);
// 输出：[C, A, B]（严格按插入顺序）
```

### 性能细节

在 **小容量** 场景下，`LinkedHashSet` 的遍历性能优于 `HashSet`，因为：

- `HashSet` 迭代器需要遍历整个桶数组（包括空桶）
- `LinkedHashSet` 直接沿链表遍历，跳过空桶

在 **大容量且负载因子较低** 时，两者遍历性能差距更明显。

---

## 四、与 TreeSet 的对比

| 对比维度 | LinkedHashSet | TreeSet |
|---------|---------------|---------|
| **底层结构** | LinkedHashMap（数组 + 链表 + 红黑树 + 双向链表） | TreeMap（红黑树） |
| **顺序类型** | 插入顺序 | 自然排序（Comparable）或定制排序（Comparator） |
| **增删查时间复杂度** | O(1) | O(log n) |
| **内存开销** | 中等（双向链表额外开销） | 较大（红黑树节点有 parent、left、right、color 字段） |
| **null 支持** | 允许一个 null | 不允许 null（排序需要比较） |
| **范围查询** | 不支持 | 支持（subSet、headSet、tailSet） |
| **适用场景** | 保持插入顺序的去重集合 | 需要排序的范围查询集合 |

### 代码对比

```java
Set<String> linkedSet = new LinkedHashSet<>();
linkedSet.add("Banana");
linkedSet.add("Apple");
linkedSet.add("Cherry");
System.out.println(linkedSet);
// 输出：[Banana, Apple, Cherry] —— 按插入顺序

Set<String> treeSet = new TreeSet<>();
treeSet.add("Banana");
treeSet.add("Apple");
treeSet.add("Cherry");
System.out.println(treeSet);
// 输出：[Apple, Banana, Cherry] —— 按字典序排序

// TreeSet 支持范围查询
System.out.println(treeSet.subSet("Apple", "Cherry"));
// 输出：[Apple, Banana]
```

---

## 五、适用场景

### 1. 需要去重且保持原始顺序

```java
// 场景：过滤重复元素但保留用户输入的原始顺序
List<String> input = Arrays.asList("A", "B", "A", "C", "B", "D");
List<String> deduplicated = new ArrayList<>(new LinkedHashSet<>(input));
System.out.println(deduplicated);
// 输出：[A, B, C, D]
```

### 2. 实现按插入顺序遍历的 Set

```java
// 场景：缓存中按插入顺序记录最近访问的 key
Set<String> recentKeys = new LinkedHashSet<>();
recentKeys.add("user:1");
recentKeys.add("user:2");
recentKeys.add("user:3");
// 遍历时总是按 user:1 → user:2 → user:3 的顺序
```

### 3. SQL 查询结果去重

```java
// 场景：从数据库读取数据后去重，同时保持结果集原有顺序
Set<Record> uniqueRecords = new LinkedHashSet<>();
for (Record r : resultSet) {
    uniqueRecords.add(r);
}
```

### 4. 需要确定性顺序的单元测试

```java
// 场景：测试中需要可预测的遍历顺序
@Test
void testSetOrder() {
    Set<String> set = new LinkedHashSet<>();
    set.add("first");
    set.add("second");
    set.add("third");

    Iterator<String> it = set.iterator();
    assertEquals("first", it.next());
    assertEquals("second", it.next());
    assertEquals("third", it.next());
}
```

### 5. 配置解析时保留用户定义的顺序

```java
// 场景：解析 YAML/JSON 配置文件时，保持配置的声明顺序
Set<String> pluginOrder = new LinkedHashSet<>();
pluginOrder.add("logging");
pluginOrder.add("auth");
pluginOrder.add("cors");
// 按此顺序初始化插件链
```

---

## 六、面试高频问题

### Q1：LinkedHashSet 的底层数据结构是什么？

**答：** `LinkedHashSet` 内部使用 `LinkedHashMap` 存储数据，元素作为 key，value 统一为 `PRESENT`。`LinkedHashMap` 继承自 `HashMap`，在 `HashMap` 数组 + 链表 + 红黑树的基础上，通过 `Entry` 节点中的 `before` 和 `after` 指针维护了一条双向链表，保证遍历顺序等于插入顺序。

### Q2：LinkedHashSet 和 HashSet 的区别是什么？

**答：** 主要区别在于 **顺序保证** 和 **内存开销**。`HashSet` 不保证遍历顺序，内存开销较小；`LinkedHashSet` 按插入顺序遍历，但每个 Entry 多了两个引用指针，内存开销略大。两者的增删查时间复杂度都是 O(1)。

### Q3：LinkedHashSet 允许 null 吗？

**答：** 允许，但只能有一个 null 元素，因为 Set 要求元素唯一。null 的 hashCode 为 0，存储在数组索引 0 的位置。

### Q4：LinkedHashSet 是线程安全的吗？

**答：** 不是。在多线程环境下并发修改会导致数据不一致。如果需要线程安全的有序 Set，可以使用 `Collections.synchronizedSet(new LinkedHashSet<>())` 或者使用 `CopyOnWriteArraySet`（适合读多写少的场景）。

### Q5：LinkedHashSet 的遍历性能为什么通常优于 HashSet？

**答：** 因为 `LinkedHashSet` 沿双向链表遍历，只访问有效节点，时间复杂度严格为 O(n)。而 `HashSet` 的迭代器需要遍历整个桶数组，当容量大但元素少时（负载因子低），会遍历大量空桶，效率较低。

### Q6：为什么 LinkedHashSet 不支持访问顺序模式？

**答：** 因为 `LinkedHashSet` 继承自 `HashSet`，其构造函数通过 `super(initialCapacity, loadFactor, true)` 调用包访问权限的构造函数，该构造函数固定创建 `LinkedHashMap` 时 `accessOrder = false`。`LinkedHashSet` 没有暴露 `accessOrder` 参数的构造函数。

### Q7：LinkedHashSet 在什么情况下会退化？

**答：** 当多个元素的 `hashCode()` 相同（哈希冲突严重）时，`LinkedHashMap` 的桶中链表长度超过 8 且数组容量超过 64 时会树化为红黑树。此时增删查时间复杂度从 O(1) 退化到 O(log n)。但由于双向链表仍然维护着插入顺序，**遍历顺序不受影响**。

### Q8：LinkedHashSet 的初始容量和负载因子如何设置？

**答：** 默认初始容量为 16，默认负载因子为 0.75。如果能预估元素数量，建议设置 `initialCapacity = 预期元素数量 / 0.75 + 1`，避免扩容带来的性能损耗和链表重建开销：

```java
// 预计存储 1000 个元素
Set<String> set = new LinkedHashSet<>((int) (1000 / 0.75f) + 1);
```
