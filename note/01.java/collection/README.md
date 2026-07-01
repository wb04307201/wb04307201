<!--
module:
  parent: java
  slug: java/collection
  type: article
  category: 主模块子文章
  summary: Java 集合框架全貌与各集合类的底层原理、选型指南。
-->

# Java 集合框架

> 目标：读完这篇，理解 Java 集合体系的全貌，能在实际场景中快速选出合适的集合类。

---
---

## 一、集合框架继承体系

```
Collection（接口）
├── List（有序、可重复）
│   ├── ArrayList          ← 动态数组，随机访问 O(1)
│   ├── LinkedList         ← 双向链表，头尾操作 O(1)
│   ├── Vector             ← ArrayList 的线程安全版（已过时）
│   └── CopyOnWriteArrayList ← 写时复制，读多写少场景
│
├── Set（无序、不可重复）
│   ├── HashSet            ← 基于 HashMap，O(1) 查找
│   ├── LinkedHashSet      ← 基于 LinkedHashMap，保持插入顺序
│   └── TreeSet            ← 红黑树，有序，O(log n)
│
└── Queue（队列）
    ├── PriorityQueue      ← 二叉堆，优先级队列
    ├── ArrayDeque         ← 动态数组双端队列（推荐替代 Stack）
    ├── LinkedList         ← 也实现了 Deque
    └── BlockingQueue      ← 阻塞队列（并发专用）
        ├── ArrayBlockingQueue
        ├── LinkedBlockingQueue
        ├── SynchronousQueue
        ├── DelayQueue
        └── PriorityBlockingQueue

Map（接口，键值对）
├── HashMap                ← 数组+链表+红黑树，O(1) 平均
├── LinkedHashMap          ← HashMap + 双向链表，保持插入/访问顺序
├── TreeMap                ← 红黑树，有序，O(log n)
├── WeakHashMap            ← 弱引用键，GC 自动回收
├── ConcurrentHashMap      ← JDK 7 分段锁 / JDK 8 CAS+synchronized，线程安全
├── ConcurrentSkipListMap  ← 跳表，有序 + 线程安全
└── Hashtable              ← 全表锁（已过时）
```

> **设计要点**：上图中 `HashSet` / `LinkedHashSet` / `TreeSet` 的底层实现均依赖 `Map` — `HashSet` 内部就是一个 `HashMap`，元素存在 key 上，value 统一用一个 `Object` 占位。理解 `HashMap` 就理解了 `HashSet`。例外：`EnumSet` 用位向量实现，`CopyOnWriteArraySet` 用 `CopyOnWriteArrayList` 实现，均不依赖 Map。

---

## 二、List / Set / Queue / Map 的核心区别

| 接口 | 特点 | 典型实现 | 线程安全实现 |
|------|------|----------|-------------|
| **List** | 有序、可重复、支持索引访问 | ArrayList、LinkedList | CopyOnWriteArrayList |
| **Set** | 无序、不可重复 | HashSet、TreeSet | ConcurrentHashMap.newKeySet() |
| **Queue** | 先进先出（FIFO） | ArrayDeque、PriorityQueue | ArrayBlockingQueue |
| **Map** | 键值对、键不可重复 | HashMap、TreeMap | ConcurrentHashMap |

---

## 三、选型决策树

```
你需要什么？
│
├── 键值对存储（Map）
│   ├── 不需要有序 → HashMap（默认选择）
│   ├── 需要保持插入顺序 → LinkedHashMap
│   ├── 需要按键排序 → TreeMap
│   ├── 需要线程安全 → ConcurrentHashMap
│   └── 需要有序 + 线程安全 → ConcurrentSkipListMap
│
├── 有序列表（List）
│   ├── 随机访问多（get/set）→ ArrayList（默认选择）
│   ├── 头尾插入删除多 → ArrayDeque（比 LinkedList 更快）
│   ├── 需要线程安全 + 读多写少 → CopyOnWriteArrayList
│   └── 需要线程安全 + 写多 → Collections.synchronizedList()
│
├── 去重集合（Set）
│   ├── 不需要有序 → HashSet（默认选择）
│   ├── 需要保持插入顺序 → LinkedHashSet
│   └── 需要排序 → TreeSet
│
└── 队列/栈（Queue/Deque）
    ├── 普通队列/栈 → ArrayDeque（推荐替代 Stack）
    ├── 优先级队列 → PriorityQueue
    ├── 阻塞队列（生产者-消费者）→ [详见并发集合文档](concurrent.md)
    └── 延迟队列 → DelayQueue
```

> **一句话原则**：不知道选什么就选 `HashMap` / `ArrayList` / `ArrayDeque`，等遇到具体需求再换。

---

## 四、ArrayList vs LinkedList

这是最常考也最容易选错的两个类。

### 底层结构

```
ArrayList：Object[] 动态数组
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ A │ B │ C │ D │   │   │   │   │  ← 容量 8，size 4
└───┴───┴───┴───┴───┴───┴───┴───┘

LinkedList：双向链表
null ← [prev|A|next] ⇄ [prev|B|next] ⇄ [prev|C|next] → null
```

### 性能对比

| 操作 | ArrayList | LinkedList |
|------|-----------|------------|
| 随机访问 `get(i)` | **O(1)** ✅ | O(n) ❌ |
| 尾部插入 `add(e)` | O(1) 均摊 | O(1) |
| 头部插入 `add(0, e)` | O(n) | **O(1)** ✅ |
| 中间插入 `add(i, e)` | O(n) | O(n)（需要遍历到 i） |
| 尾部删除 | O(1) | O(1) |
| 头部删除 | O(n) | **O(1)** ✅ |
| 内存开销 | 尾部预留空间 | 每个节点额外 2 个指针（16~24 字节） |

### 实际选择建议

```
99% 的场景选 ArrayList，原因：
1. CPU 缓存友好：数组内存连续，局部性好
2. 随机访问 O(1)：绝大多数业务都需要按索引访问
3. 尾部插入 O(1) 均摊：扩容频率低（每次 1.5 倍）

LinkedList 只在以下场景有优势：
1. 频繁在头部插入/删除（如实现队列，但 ArrayDeque 更好）
2. 需要在迭代过程中高效地插入/删除元素（iterator.remove() 是 O(1)）
```

> **实测数据**：在 10000 个元素的列表中随机访问，ArrayList 约 0.01ms，LinkedList 约 3ms — 差 300 倍。CPU 缓存命中率是关键因素。

### ArrayList 扩容机制

```java
// ArrayList 默认容量 10，扩容为原来的 1.5 倍
ArrayList<String> list = new ArrayList<>();  // 初始容量 10
list.add("A");  // size=1
// ... 加到第 11 个元素时触发扩容
// 新容量 = 10 + 10/2 = 15
// 再满时 → 15 + 15/2 = 22
```

**优化**：如果已知元素数量，构造时指定容量避免扩容：
```java
ArrayList<String> list = new ArrayList<>(1000);  // 预分配 1000
```

---

### Arrays.asList() 陷阱

```java
// Arrays.asList() 返回的是 java.util.Arrays$ArrayList（固定大小），不是 java.util.ArrayList
List<String> list = Arrays.asList("A", "B", "C");
list.add("D");    // 抛 UnsupportedOperationException！
list.remove(0);   // 同样抛异常！

// 修改会影响原数组（共享同一块内存）
String[] arr = {"A", "B", "C"};
List<String> list2 = Arrays.asList(arr);
list2.set(0, "X");
System.out.println(arr[0]);  // "X" — 原数组也被改了！

// 正确做法：包装一层
List<String> mutableList = new ArrayList<>(Arrays.asList("A", "B", "C"));
mutableList.add("D");  // OK
```

---

## 五、Comparable vs Comparator

两种方式实现排序，适用于不同场景：

| | Comparable | Comparator |
|---|---|---|
| **包** | `java.lang` | `java.util` |
| **方法** | `compareTo(T o)` | `compare(T o1, T o2)` |
| **修改位置** | 类内部实现（自然排序） | 类外部定义（定制排序） |
| **是否需要改类** | 是 | 否 |
| **优先级** | 低 | 高（Comparator 覆盖 Comparable） |

```java
// Comparable：类内部定义自然排序
public class Person implements Comparable<Person> {
    private int age;
    @Override
    public int compareTo(Person other) {
        return Integer.compare(this.age, other.age);  // 升序
    }
}

// Comparator：类外部定义定制排序（推荐）
Comparator<Person> byAgeDesc = (p1, p2) -> Integer.compare(p2.age, p1.age);
Comparator<Person> byName = Comparator.comparing(Person::getName);
Comparator<Person> byAgeThenName = Comparator.comparingInt(Person::getAge)
                                              .thenComparing(Person::getName);

// 使用
Collections.sort(persons, byAgeDesc);
TreeMap<Person, String> map = new TreeMap<>(byAgeThenName);
```

> **最佳实践**：优先用 `Comparator`（不修改类、可组合、支持多字段排序）。JDK 8 的 `Comparator.comparing()` 链式调用非常优雅。

---

## 六、迭代器：fail-fast vs fail-safe

### fail-fast（快速失败）

`ArrayList`、`HashMap`、`HashSet` 等**非并发集合**的迭代器都是 fail-fast。

```java
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));
Iterator<String> it = list.iterator();
list.add("D");           // 修改了集合
it.next();               // 抛出 ConcurrentModificationException
```

**原理**：集合维护一个 `modCount` 计数器，每次修改（add/remove/clear）+1。迭代器创建时记录 `expectedModCount = modCount`，每次 `next()` 检查是否相等。不等 → 抛异常。

### fail-safe（安全失败）

`CopyOnWriteArrayList`、`ConcurrentHashMap` 等**并发集合**的迭代器是 fail-safe（弱一致性）。

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
map.put("B", 2);
Iterator<String> it = map.keySet().iterator();
map.put("C", 3);         // 修改了集合
it.next();               // 不抛异常，但可能看不到 "C"
```

**原理**：迭代器基于集合的快照或当前状态，不抛异常，但**不保证能看到修改**。

| | fail-fast | fail-safe（弱一致性） |
|---|---|---|
| **典型集合** | ArrayList、HashMap、HashSet | CopyOnWriteArrayList、ConcurrentHashMap |
| **遍历时修改** | 抛 `ConcurrentModificationException` | 不抛异常 |
| **能看到修改** | 不能（直接报错） | 不一定（弱一致性） |
| **性能开销** | 低（只检查计数器） | CopyOnWriteArrayList 写时复制数组；ConcurrentHashMap 弱一致遍历无快照开销 |

---

## 七、hashCode() 和 equals() 契约

这是 `HashMap` / `HashSet` 正确工作的基础。

### 规则

```
1. equals() 相等的两个对象，hashCode() 必须相等
2. hashCode() 相等的两个对象，equals() 不一定相等（哈希冲突）
3. 重写 equals() 必须同时重写 hashCode()
```

### 违反规则的后果

```java
class Person {
    String name;
    // 只重写了 equals，没重写 hashCode
    @Override
    public boolean equals(Object o) {
        return o instanceof Person && name.equals(((Person) o).name);
    }
    // hashCode() 用的是 Object 的默认实现（JDK 8+ 默认用 xor-shift 随机数生成器）
}

Person p1 = new Person("Alice");
Person p2 = new Person("Alice");
p1.equals(p2);  // true

HashSet<Person> set = new HashSet<>();
set.add(p1);
set.contains(p2);  // false！因为 hashCode 不同，去了不同的桶
```

### 正确写法

```java
class Person {
    String name;
    int age;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Person)) return false;
        Person p = (Person) o;
        return age == p.age && Objects.equals(name, p.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, age);  // JDK 7+ 推荐
    }
}
```

> **IDE 自动生成**：IntelliJ IDEA 中 `Alt+Insert` → `equals() and hashCode()`，选 `Objects.hash()` 模板。

---

## 八、TreeMap 简述

TreeMap 基于红黑树实现，提供按键排序的能力。详细源码分析不在此展开，核心要点：

| 特性 | TreeMap | HashMap |
|------|---------|---------|
| 底层结构 | 红黑树 | 哈希表 + 链表/红黑树 |
| 时间复杂度 | O(log n) 稳定 | O(1) 平均，O(n) 最坏 |
| 有序性 | 按键排序 | 无序 |
| null 键 | 不允许 | 允许 1 个 |
| 线程安全 | 否 | 否 |

**适用场景**：
- 需要按 key 排序（如字典、排行榜）
- 需要范围查询（`subMap(from, to)`、`floorKey(k)`、`ceilingKey(k)`）
- 需要获取最大/最小 key（`firstKey()`、`lastKey()`）

```java
TreeMap<Integer, String> scores = new TreeMap<>();
scores.put(85, "Alice");
scores.put(92, "Bob");
scores.put(78, "Charlie");

scores.subMap(80, 95);     // {85=Alice, 92=Bob}
scores.floorKey(90);       // 85（≤ 90 的最大 key）
scores.lastKey();          // 92
```

> **线程安全替代**：`ConcurrentSkipListMap`（基于跳表，有序 + 线程安全，O(log n)）。→ 详见 [并发集合](concurrent.md)

---

## 九、WeakHashMap 简述

WeakHashMap 的键使用弱引用，当键不再被外部强引用持有时，GC 会自动回收该键值对。

| 特性 | WeakHashMap | HashMap |
|------|-------------|---------|
| 键的引用类型 | 弱引用 | 强引用 |
| GC 行为 | 键无强引用时自动回收键值对 | 键值对永远不被回收 |
| 线程安全 | 否 | 否 |

**适用场景**：
- 缓存（键对象被回收时缓存自动失效）
- 为对象附加元数据（对象被回收时元数据自动清理）

```java
WeakHashMap<Object, Metadata> cache = new WeakHashMap<>();
Object key = new Object();
cache.put(key, computeMetadata());  // 存入缓存

key = null;  // 不再有强引用
System.gc(); // 下次 GC 时，cache 中该条目会被自动移除
```

> **注意**：不要用 `String` 字面量作 WeakHashMap 的键 — 字符串常量池持有强引用，永远不会被 GC。

---

## 十、不可变集合（JDK 9+）

JDK 9 引入了工厂方法创建不可变集合，比 `Collections.unmodifiableList()` 更简洁安全。

```java
// List
List<String> list = List.of("A", "B", "C");           // 不可变 List
List<String> list2 = List.of();                        // 空 List

// Set
Set<Integer> set = Set.of(1, 2, 3);                    // 不可变 Set

// Map
Map<String, Integer> map = Map.of("A", 1, "B", 2);    // 不可变 Map
Map<String, Integer> map2 = Map.ofEntries(              // 超过 10 个元素
    Map.entry("A", 1), Map.entry("B", 2)
);

// 从已有集合创建不可变副本
List<String> copy = List.copyOf(existingList);
```

**特点**：
- 不可添加、删除、修改元素
- 不允许 `null` 元素
- 不保证迭代顺序与创建顺序一致（除 `List` 外）
- 内存效率更高（内部优化了存储结构）

> **对比 `Collections.unmodifiableList()`**：`unmodifiableList` 是对原集合的包装，原集合被修改时包装视图也会变。`List.of()` 创建的是真正独立的不可变副本。

---

## 总结

```
集合选型核心原则：

1. Map 选 HashMap（无序）/ TreeMap（有序）/ ConcurrentHashMap（并发）
2. List 选 ArrayList（通用）/ CopyOnWriteArrayList（并发读多写少）
3. Set 选 HashSet（无序）/ TreeSet（有序）
4. Queue 选 ArrayDeque（普通）/ PriorityQueue（优先级）/ ArrayBlockingQueue（并发）

5. 不知道选什么 → 先用 HashMap / ArrayList，遇到具体需求再换
6. 并发场景 → 永远选 java.util.concurrent 包下的实现，不要手动加锁
```

---

## 📊 本节统计

| 统计维度 | 数值 | 口径 |
|----------|------|------|
| 分类主题数 | 4 | List / Set / Queue / Map |
| 子 README 数 | 6 | `collection/` 下 leaf README（ArrayList / LinkedList / ConcurrentHashMap / LinkedHashSet / TreeMap / WeakHashMap） |
| 含 frontmatter 的 README | 7 / 7 | 100% 覆盖（2026-07-01） |

> **统计时间戳**：2026-07-01

---

← [返回 01.java 主模块](../README.md)
