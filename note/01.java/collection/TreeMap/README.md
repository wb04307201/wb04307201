# Java TreeMap 学习笔记

> `TreeMap` 是基于红黑树（Red-Black Tree）实现的有序 Map，保证键的排序和 O(log n) 的查询性能。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

Java TreeMap 学习笔记 本应该很简单，`TreeMap` 是基于红黑树（Red-Black Tree）实现的有序 Map，保证键的排序和 O(log n) 的查询性能

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、红黑树数据结构

### 1.1 什么是红黑树

红黑树是一种**自平衡二叉查找树**，通过节点颜色和旋转操作保持近似平衡，确保最坏情况下操作时间复杂度为 O(log n)。

### 1.2 五条核心性质

```
1. 每个节点要么是红色，要么是黑色
2. 根节点是黑色
3. 每个叶子节点（NIL/空节点）是黑色
4. 红色节点的子节点必须是黑色（不能有两个连续的红色节点）
5. 从任一节点到其每个叶子的所有路径都包含相同数量的黑色节点（黑高相同）
```

### 1.3 红黑树 vs 其他树结构

| 特性 | BST（二叉查找树） | AVL 树 | 红黑树 | B+ 树 |
|------|------------------|--------|--------|-------|
| 平衡性 | 不平衡 | 严格平衡 | 近似平衡 | 多路平衡 |
| 查询复杂度 | O(n) 最坏 | O(log n) | O(log n) | O(log n) |
| 插入/删除开销 | 无 | 大（多次旋转） | 中（最多3次旋转） | 中 |
| 适用场景 | 理论 | 读多写少 | 读写均衡（JDK 选择） | 数据库/文件系统 |
| 树高上限 | n | 1.44·log₂(n+2) | 2·log₂(n+1) | 较低 |

### 1.4 旋转操作

```
        左旋 (rotateLeft)                 右旋 (rotateRight)

          P                                   S
         / \                                 / \
        S   c       ----------->           a   P
       / \                                     / \
      a   b                                   b   c

    左旋: P.right = S.right; S.right = P
    右旋: P.left = S.left; S.left = P
```

### 1.5 TreeMap 中的 Entry 节点结构

```java
static final class Entry<K,V> implements Map.Entry<K,V> {
    K key;
    V value;
    Entry<K,V> left;      // 左子节点
    Entry<K,V> right;     // 右子节点
    Entry<K,V> parent;    // 父节点
    boolean color = BLACK; // 节点颜色，默认黑色

    Entry(K key, V value, Entry<K,V> parent) {
        this.key = key;
        this.value = value;
        this.parent = parent;
    }
}
```

---

## 二、put() 流程与红黑树插入修复

### 2.1 put() 整体流程

```
put(K key, V value)
    │
    ├── ① 树为空 → 创建根节点（黑色），直接返回
    │
    ├── ② 树非空 → 从根开始 BST 插入
    │       │
    │       ├── cmp < 0 → 走左子树
    │       ├── cmp > 0 → 走右子树
    │       └── cmp == 0 → 覆盖旧值，返回旧值
    │
    └── ③ 新节点插入（红色） → fixAfterInsertion() 修复红黑树性质
```

### 2.2 核心源码流程

```java
public V put(K key, V value) {
    Entry<K,V> t = root;
    if (t == null) {
        // 空树，创建根节点
        compare(key, key); // 类型检查
        root = new Entry<>(key, value, null);
        size = 1;
        modCount++;
        return null;
    }

    // BST 查找插入位置
    int cmp;
    Entry<K,V> parent;
    Comparator<? super K> cpr = comparator;
    if (cpr != null) {
        do {
            parent = t;
            cmp = cpr.compare(key, t.key);
            if (cmp < 0) t = t.left;
            else if (cmp > 0) t = t.right;
            else return t.setValue(value); // key 已存在，覆盖
        } while (t != null);
    } else {
        // 使用 Comparable
        Comparable<? super K> k = (Comparable<? super K>) key;
        do {
            parent = t;
            cmp = k.compareTo(t.key);
            if (cmp < 0) t = t.left;
            else if (cmp > 0) t = t.right;
            else return t.setValue(value);
        } while (t != null);
    }

    // 插入新节点（红色）
    Entry<K,V> e = new Entry<>(key, value, parent);
    if (cmp < 0) parent.left = e;
    else parent.right = e;

    fixAfterInsertion(e); // 修复红黑树
    size++;
    modCount++;
    return null;
}
```

### 2.3 插入修复 fixAfterInsertion()

新插入的节点是**红色**的，可能违反性质4（连续红色），需要修复。

```
情况1：叔叔节点是红色
       → 父节点和叔叔变黑，祖父变红
       → 将祖父作为新的 x，继续向上检查

情况2：叔叔节点是黑色，x 是右孩子（LL 型镜像）
       → 先对父节点左旋，转为情况3

情况3：叔叔节点是黑色，x 是左孩子（LL 型）
       → 祖父右旋，父变黑，祖父变红
       → 修复完成
```

### 2.4 ASCII 图解插入修复

```
情况1 - 叔叔为红（变色，向上继续）:

           G(黑)                    G(红) ← x 指向这里
          /     \                  /     \
       P(红)    U(红)    →      P(黑)   U(黑)
      /                        /
    X(红)                    X(红)


情况3 - LL 型（右旋+变色）:

           G(黑)              P(黑)
          /     \            /     \
       P(红)    d    →     X(红)   G(红)
      /     \                      /     \
    X(红)   c                    c       d
```

### 2.5 最佳实践

```java
// 实践1：避免在 TreeMap 中使用 null key（与 HashMap 不同）
TreeMap<String, Integer> map = new TreeMap<>();
map.put(null, 1); // 编译通过，但运行时会抛 NullPointerException

// 实践2：自定义 Comparator 时保证与 equals 一致
TreeMap<Person, String> map = new TreeMap<>((a, b) ->
    Integer.compare(a.getId(), b.getId())
);
// 如果 compareTo/compare 返回 0，但 equals 返回 false，会导致行为异常

// 实践3：批量插入用 putAll() 优于逐个 put()
// TreeMap 无法像 HashMap 那样批量优化，但 putAll 语义更清晰
```

---

## 三、get() 流程

### 3.1 get() 源码分析

```java
public V get(Object key) {
    Entry<K,V> p = getEntry(key);
    return (p == null ? null : p.value);
}

final Entry<K,V> getEntry(Object key) {
    // 从根节点开始，按 BST 规则查找
    Entry<K,V> p = root;
    while (p != null) {
        int cmp = compare(key, p.key);
        if (cmp < 0)
            p = p.left;       // 往左找
        else if (cmp > 0)
            p = p.right;      // 往右找
        else
            return p;         // 找到
    }
    return null;
}
```

### 3.2 查找过程示意

```
查找 key = 50

           40
          /  \
        20    60
             /  \
           50    80
            \
             55

    40 → cmp > 0 → 右走 → 60 → cmp < 0 → 左走 → 50 → 找到
    比较次数 = 3 次，树高 = 3
```

### 3.3 containsKey() 与 containsValue()

| 方法 | 时间复杂度 | 原理 |
|------|-----------|------|
| `containsKey(key)` | O(log n) | 基于红黑树查找 |
| `containsValue(value)` | O(n) | 遍历整棵树的所有节点 |

```java
// containsKey - 高效
boolean has = map.containsKey("key"); // O(log n)

// containsValue - 低效，不推荐使用
boolean hasValue = map.containsValue("value"); // O(n)
```

### 3.4 最佳实践

```java
// 实践1：优先使用 containsKey() + get() 或直接 get() 判断 null
// 直接 get() 一次查找即可（如果 value 不可能为 null）
Integer val = map.get(key);
if (val != null) { ... }

// 实践2：如果 value 可能为 null，用 getOrDefault()
Integer val = map.getOrDefault(key, -1);

// 实践3：避免用 containsValue()，O(n) 性能差
// 如需反向查找，维护一个额外的 Map<V, K>
```

---

## 四、导航方法

### 4.1 导航方法一览

TreeMap 独有的**导航方法**是其核心优势，HashMap 完全不具备这些能力。

| 方法 | 说明 | 返回 |
|------|------|------|
| `firstKey()` | 最小的 key | K |
| `lastKey()` | 最大的 key | K |
| `lowerKey(K)` | 严格小于 key 的最大 key | K |
| `floorKey(K)` | 小于等于 key 的最大 key | K |
| `ceilingKey(K)` | 大于等于 key 的最小 key | K |
| `higherKey(K)` | 严格大于 key 的最大 key | K |
| `pollFirstEntry()` | 删除并返回最小键值对 | Map.Entry |
| `pollLastEntry()` | 删除并返回最大键值对 | Map.Entry |

### 4.2 图解导航方法

```
树上 key 分布:  10 --- 20 --- 30 --- 50 --- 70 --- 80

查找 target = 40:

lowerKey(40)    → 30  （严格小于 40 的最大值）
floorKey(40)    → 30  （<= 40 的最大值，40 不存在等同 lower）
ceilingKey(40)  → 50  （>= 40 的最小值）
higherKey(40)   → 50  （严格大于 40 的最小值）

查找 target = 50（key 存在）:

lowerKey(50)    → 30
floorKey(50)    → 50  ← 等于自身
ceilingKey(50)  → 50  ← 等于自身
higherKey(50)   → 70
```

### 4.3 导航方法源码原理

```java
// 以 ceilingKey 为例：找 >= key 的最小节点
public K ceilingKey(K key) {
    return keyOrNull(getCeilingEntry(key));
}

final Entry<K,V> getCeilingEntry(K key) {
    Entry<K,V> p = root;
    while (p != null) {
        int cmp = compare(key, p.key);
        if (cmp > 0) {
            // key 比当前节点大，往右子树找
            p = p.right;
        } else if (cmp < 0) {
            // key 比当前节点小，当前节点可能是候选，但左子树可能更接近
            Entry<K,V> parent = p.parent;
            Entry<K,V> ch = p;
            while (parent != null && ch == parent.left) {
                // 一直沿左链向上回溯
                ch = parent;
                parent = parent.parent;
            }
            return parent;
        } else {
            return p; // 精确匹配
        }
    }
    return null;
}
```

### 4.4 最佳实践

```java
TreeMap<Integer, String> scores = new TreeMap<>();
scores.put(60, "及格");
scores.put(80, "良好");
scores.put(90, "优秀");

// 场景1：分数段匹配
int myScore = 75;
String grade = scores.floorEntry(myScore).getValue(); // "及格"

// 场景2：查找下一个可用资源
Integer nextAvailable = scores.higherKey(currentId);

// 场景3：排行榜
String topPlayer = scores.lastEntry().getValue();
String bottomPlayer = scores.firstEntry().getValue();
```

---

## 五、subMap / headMap / tailMap 范围查询

### 5.1 范围查询方法

| 方法 | 返回 | 说明 |
|------|------|------|
| `subMap(fromKey, toKey)` | SortedMap | fromKey <= key < toKey |
| `headMap(toKey)` | SortedMap | key < toKey |
| `tailMap(fromKey)` | SortedMap | key >= fromKey |

**注意**：返回的 `SortedMap` 是**视图（view）**，不是拷贝。对视图的修改会反映到原 Map。

### 5.2 带边界参数的重载（Java 6+）

```java
// 支持指定边界开闭
subMap(K fromKey, boolean fromInclusive,
       K toKey,   boolean toInclusive)

headMap(K toKey, boolean inclusive)

tailMap(K fromKey, boolean inclusive)
```

### 5.3 示例与 ASCII 图解

```
树上 key 分布:  10 --- 20 --- 30 --- 40 --- 50 --- 60 --- 70 --- 80

subMap(25, 65)         → [30, 40, 50, 60]     (25 <= key < 65)
subMap(25,true,65,true)→ [30, 40, 50, 60]     (25 <= key <= 65, 结果相同因为 25/65 不存在)
headMap(40)            → [10, 20, 30]         (key < 40)
tailMap(60)            → [60, 70, 80]         (key >= 60)
```

### 5.4 NavigableMap 增强

```java
// 降序视图（非常有用的特性）
NavigableMap<Integer, String> desc = map.descendingMap();

// 降序后范围查询
desc.subMap(60, true, 30, false); // 等同于 subMap(30,false,60,true) 但降序输出
```

### 5.5 视图特性

```java
TreeMap<Integer, String> map = new TreeMap<>();
map.put(10, "A");
map.put(20, "B");
map.put(30, "C");
map.put(40, "D");

// subMap 是视图
SortedMap<Integer, String> sub = map.subMap(15, 35);
// sub = {20=B, 30=C}

sub.put(25, "X"); // 视图修改会反映到原 map
// map 变为 {10=A, 20=B, 25=X, 30=C, 40=D}

sub.put(50, "Y"); // 抛 IllegalArgumentException！
// 原因：50 不在视图范围 [15, 35) 内
```

### 5.6 最佳实践

```java
// 实践1：时间范围查询（日志场景）
TreeMap<Long, LogEntry> logs = new TreeMap<>();
long startTime = System.currentTimeMillis() - 3600_000L; // 1小时前
long endTime = System.currentTimeMillis();
SortedMap<Long, LogEntry> lastHour = logs.subMap(startTime, endTime);

// 实践2：如果需要不可变快照，应显式拷贝
SortedMap<K, V> snapshot = new TreeMap<>(map.subMap(from, to));

// 实践3：迭代范围查询，高效（只遍历范围内部）
for (Map.Entry<Integer, String> e : map.subMap(20, 60).entrySet()) {
    // 只遍历范围内的节点
}
```

---

## 六、与 HashMap 的性能对比

### 6.1 性能对比总览

| 操作 | HashMap | TreeMap | 说明 |
|------|---------|---------|------|
| `put()` | O(1) 平均 | O(log n) | HashMap 哈希定位，TreeMap 树查找 |
| `get()` | O(1) 平均 | O(log n) | 同上 |
| `remove()` | O(1) 平均 | O(log n) | 同上 |
| `containsKey()` | O(1) 平均 | O(log n) | 同上 |
| `containsValue()` | O(n) | O(n) | 都需要遍历 |
| `firstKey()` | 不支持 | O(log n) | TreeMap 独有 |
| `range query` | 不支持 | O(log n + k) | k 为范围内元素个数 |
| 遍历有序性 | 无序 | 有序（升序） | TreeMap 核心优势 |
| 内存开销 | 中等 | 较大 | 每个 Entry 多存储 parent/color |
| null key | 支持 | 不支持 | 比较时会 NPE |

### 6.2 时间复杂度可视化

```
操作耗时对比 (n = 元素数量)

HashMap  ┃━━━━━━━━  O(1) 常数时间
         ┃
TreeMap  ┃━━━━━━━━━━━━━━━━  O(log n) 对数时间
         ┃
List     ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  O(n) 线性时间

         0        10       100      1000    → n
```

### 6.3 实际性能基准（参考）

| 场景 | HashMap | TreeMap | 建议 |
|------|---------|---------|------|
| 100 万元素 put | ~50ms | ~300ms | 不需要有序选 HashMap |
| 100 万元素 get | ~1ms | ~5ms | 差距不大 |
| 遍历（无序） | 快 | 中等 | HashMap 遍历更快 |
| 范围查询 | 无法高效实现 | 优秀 | 必须选 TreeMap |
| 排行榜 Top-K | 需要额外排序 | O(k) 直接取 | 选 TreeMap |

### 6.4 选型决策树

```
需要 Key 有序吗？
    ├── 不需要 → HashMap
    └── 需要
        ├── 只需要插入顺序有序 → LinkedHashMap
        └── 需要按 Key 排序/范围查询 → TreeMap

Key 需要 null 吗？
    ├── 是 → HashMap
    └── 否 → 看是否需要有序

内存敏感？
    ├── 是 → HashMap
    └── 否 → 按需求选择
```

### 6.5 最佳实践

```java
// 场景1：纯 KV 存储，不需要有序
Map<String, Integer> fast = new HashMap<>();

// 场景2：需要保持插入顺序
Map<String, Integer> insertOrdered = new LinkedHashMap<>();

// 场景3：需要排序 + 范围查询
NavigableMap<Integer, String> sorted = new TreeMap<>();

// 场景4：高频查询 + 偶尔排序
// 用 HashMap 为主，需要排序时用 TreeMap 临时包装
Map<Integer, String> primary = new HashMap<>();
NavigableMap<Integer, String> forSort = new TreeMap<>(primary); // 一次性拷贝
```

---

## 七、Comparator vs Comparable 排序

### 7.1 两种排序方式对比

| 维度 | Comparable | Comparator |
|------|-----------|------------|
| 定义位置 | 在实体类内部实现 | 外部独立类或 Lambda |
| 接口方法 | `compareTo(T o)` | `compare(T o1, T o2)` |
| 控制权 | 类自身控制排序逻辑 | 调用方控制排序逻辑 |
| 灵活性 | 低（每个类只能有一个自然顺序） | 高（可以有多个比较器） |
| TreeMap 使用 | `new TreeMap<>()` 自然排序 | `new TreeMap<>(comparator)` |

### 7.2 Comparable 自然排序

```java
// 实体类实现 Comparable
public class Student implements Comparable<Student> {
    private int id;
    private String name;
    private int score;

    // compareTo 定义"自然顺序"
    @Override
    public int compareTo(Student other) {
        return Integer.compare(this.id, other.id);
    }
}

// TreeMap 使用自然排序
TreeMap<Student, String> map = new TreeMap<>();
map.put(new Student(3, "张三"), "A");
map.put(new Student(1, "李四"), "B");
map.put(new Student(2, "王五"), "C");

// 遍历时按 id 排序: 李四(1) → 王五(2) → 张三(3)
```

### 7.3 Comparator 定制排序

```java
// 方式1：Lambda 表达式
TreeMap<String, Integer> map = new TreeMap<>(
    (a, b) -> b.length() - a.length() // 按字符串长度降序
);

// 方式2：Comparator.comparing()
TreeMap<Student, String> map = new TreeMap<>(
    Comparator.comparingInt(Student::getScore).reversed() // 分数降序
);

// 方式3：多级排序
TreeMap<Student, String> map = new TreeMap<>(
    Comparator.comparingInt(Student::getScore)
              .reversed()
              .thenComparing(Student::getName)
);
```

### 7.4 TreeMap 如何选择排序方式

```java
// 1. 无参构造 → 要求 Key 实现 Comparable
TreeMap<K, V> map1 = new TreeMap<>();

// 2. 有参构造 → 使用指定的 Comparator
TreeMap<K, V> map2 = new TreeMap<>(myComparator);

// 3. 拷贝构造 → 继承原 Map 的排序方式
TreeMap<K, V> map3 = new TreeMap<>(existingSortedMap);

// 4. SortedMap 构造 → 继承原 SortedMap 的排序方式
TreeMap<K, V> map4 = new TreeMap<>(existingNavigableMap);
```

### 7.5 Comparator 链式编程

```java
// Java 8+ 推荐写法
Comparator<Person> comparator = Comparator
    .comparing(Person::getLastName)           // 第一级：姓氏升序
    .thenComparing(Person::getFirstName)      // 第二级：名字升序
    .thenComparingInt(Person::getAge)         // 第三级：年龄升序
    .reversed();                              // 整体反转

TreeMap<Person, String> map = new TreeMap<>(comparator);
```

### 7.6 compareTo 与 equals 一致性

```java
// 一致：compareTo 返回 0 时 equals 也返回 true
public int compareTo(Student other) {
    return Integer.compare(this.id, other.id);
}

// 不一致：可能导致 TreeMap 行为异常
// 如果 compareTo 只比较 name，但 equals 比较 name+id
// 两个不同 id 但同名的学生，TreeMap 会认为是"相同 key"

// JDK 文档明确建议：
// 强烈建议 compareTo 与 equals 保持一致
// "(compareTo(x)==0) == (x.equals(y))"
```

### 7.7 最佳实践

```java
// 实践1：优先在实体类中实现 Comparable（自然排序）
public class User implements Comparable<User> {
    @Override
    public int compareTo(User other) {
        return Long.compare(this.id, other.id);
    }
}

// 实践2：需要多种排序时使用 Comparator
TreeMap<User, String> byName = new TreeMap<>(
    Comparator.comparing(User::getName)
);

// 实践3：null 安全比较
TreeMap<String, Integer> map = new TreeMap<>(
    Comparator.nullsFirst(String::compareToIgnoreCase)
);

// 实践4：避免整数相减写法（可能溢出）
// 错误写法: return a.age - b.age;     // age 差值大时会溢出
// 正确写法: return Integer.compare(a.age, b.age);
```

---

## 八、面试高频问题

### 8.1 TreeMap 和 HashMap 的区别？

| 维度 | HashMap | TreeMap |
|------|---------|---------|
| 底层结构 | 数组 + 链表/红黑树 | 红黑树 |
| 有序性 | 无序 | 按键升序排列 |
| null key | 允许一个 | 不允许 |
| 时间复杂度 | O(1) 平均 | O(log n) |
| 适用场景 | 快速查找 | 有序遍历、范围查询 |

**回答要点**：从数据结构、有序性、性能、null 支持、适用场景五个维度回答。

### 8.2 TreeMap 的 key 为什么不能为 null？

```
因为在 put/get 时需要进行 key 的比较（compareTo 或 comparator.compare），
对 null 调用 compare 方法会抛出 NullPointerException。
而 HashMap 将 null key 特殊处理（存放在 index 0 的位置），不需要比较。
```

```java
// 如果确实需要 null key，可以通过自定义 Comparator 实现
TreeMap<String, Integer> map = new TreeMap<>(
    Comparator.nullsFirst(String::compareTo)
);
map.put(null, 0); // 现在可以了
```

### 8.3 TreeMap 是线程安全的吗？

```
不是。TreeMap 没有内置的线程安全机制。

线程安全的替代方案：
1. Collections.synchronizedSortedMap(new TreeMap<>())  // 粗粒度锁
2. ConcurrentHashMap + 外部排序                         // 高并发场景
3. 业务层自行加锁                                       // 细粒度控制

注意：ConcurrentHashMap 不保证遍历顺序，不能直接替代 TreeMap。
```

### 8.4 红黑树插入时新节点为什么是红色？

```
如果新节点是黑色：
  → 从根到该叶子路径上的黑色节点数 +1
  → 违反性质5（黑高相同）
  → 修复需要调整整条路径，代价大

如果新节点是红色：
  → 只可能违反性质4（连续红色）
  → 修复只涉及局部节点（最多3次旋转）
  → 代价小

所以选择红色，因为修复代价更小。
```

### 8.5 TreeMap 的迭代器顺序是什么？

```java
TreeMap<Integer, String> map = new TreeMap<>();
map.put(3, "C");
map.put(1, "A");
map.put(2, "B");

// 迭代顺序永远是 key 的升序: 1 → 2 → 3
for (Map.Entry<Integer, String> entry : map.entrySet()) {
    System.out.println(entry.getKey() + "=" + entry.getValue());
}

// 如果需要降序，使用 descendingMap()
for (Map.Entry<Integer, String> entry : map.descendingMap().entrySet()) {
    System.out.println(entry.getKey() + "=" + entry.getValue());
}
```

### 8.6 什么情况下 HashMap 中的链表会转红黑树？

```
这不是 TreeMap 的问题，而是 HashMap 的优化。

JDK 8+ 中，HashMap 的桶中链表长度 >= 8 且数组长度 >= 64 时，
链表会转为红黑树，将极端情况下的查找从 O(n) 提升到 O(log n)。

这是为了防止 Hash 冲突攻击导致的性能退化。

注意：HashMap 中的红黑树节点和 TreeMap 的红黑树节点是不同的实现类。
HashMap 使用 TreeNode，TreeMap 使用 Entry。
```

### 8.7 TreeMap 的时间复杂度能保证吗？

```
是的。红黑树的性质保证了：
- 树高 <= 2 * log₂(n+1)
- 因此 put/get/remove 最坏情况都是 O(log n)

不像 HashMap 在极端 Hash 冲突下可能退化到 O(n)，
TreeMap 在最坏情况下也有 O(log n) 的保证。
```

### 8.8 如何用 TreeMap 实现 LRU Cache？

```java
// TreeMap 本身不适合 LRU（按访问时间淘汰），但可以近似实现：

// 方式1：用 LinkedHashMap（推荐）
Map<K, V> lru = new LinkedHashMap<>(16, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > MAX_SIZE;
    }
};

// 方式2：TreeMap + 时间戳作为 key（按时序排序）
TreeMap<Long, CacheEntry> cache = new TreeMap<>();
// 淘汰时删除最早的
cache.pollFirstEntry();
```

### 8.9 TreeMap 内存占用为什么比 HashMap 大？

```
每个 Entry 节点需要存储：
- key 引用       (4~8 bytes)
- value 引用     (4~8 bytes)
- left 引用      (4~8 bytes)
- right 引用     (4~8 bytes)
- parent 引用    (4~8 bytes)
- color boolean   (1 byte + padding)
- 对象头          (12~16 bytes)

合计约 40~64 bytes/entry，加上红黑树的指针开销。

HashMap 的 Node：
- hash int        (4 bytes)
- key 引用        (4~8 bytes)
- value 引用      (4~8 bytes)
- next 引用       (4~8 bytes)
- 对象头           (12~16 bytes)

合计约 28~40 bytes/entry。

所以 TreeMap 内存开销大约比 HashMap 多 50%~60%。
```

### 8.10 TreeMap 的 subMap 修改会影响原 Map 吗？

```java
TreeMap<Integer, String> map = new TreeMap<>();
map.put(1, "A");
map.put(2, "B");
map.put(3, "C");
map.put(4, "D");

SortedMap<Integer, String> sub = map.subMap(2, 4); // [2, 4)

// 修改视图 → 影响原 Map
sub.put(2, "X");
// map 变为 {1=A, 2=X, 3=C, 4=D}

// 删除视图中的元素 → 影响原 Map
sub.remove(3);
// map 变为 {1=A, 2=X, 4=D}

// 原 Map 修改 → 如果在视图范围内，会影响视图
map.put(3, "Y");
// sub 变为 {2=X, 3=Y}

// 总结：subMap 返回的是实时视图（live view），不是快照
```

---

## 九、总结

### 9.1 核心知识体系

```
TreeMap
├── 数据结构：红黑树（自平衡 BST）
│   ├── 5 条性质：颜色、根黑、叶黑、无连续红、黑高一致
│   ├── 旋转操作：左旋、右旋
│   └── 变色操作：插入修复、删除修复
│
├── 核心操作
│   ├── put()：BST 插入 + 红黑树修复（变色 + 旋转）
│   ├── get()：BST 查找，O(log n)
│   └── remove()：BST 删除 + 红黑树修复（更复杂）
│
├── 导航方法（TreeMap 独有优势）
│   ├── lowerKey / floorKey / ceilingKey / higherKey
│   └── firstKey / lastKey / pollFirstEntry / pollLastEntry
│
├── 范围查询
│   ├── subMap / headMap / tailMap
│   └── 视图（非拷贝）、实时同步
│
└── 排序机制
    ├── Comparable：自然排序
    └── Comparator：定制排序（推荐，更灵活）
```

### 9.2 何时选择 TreeMap

```
选 TreeMap 当：
  ✓ 需要 key 有序遍历
  ✓ 需要范围查询（subMap）
  ✓ 需要导航方法（ceiling/floor）
  ✓ 需要排行榜/Top-K 场景

选 HashMap 当：
  ✓ 只需要快速查找
  ✓ 不需要有序性
  ✓ 内存敏感
  ✓ 需要 null key
```
