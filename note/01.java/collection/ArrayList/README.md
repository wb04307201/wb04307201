<!--
module:
  parent: java
  slug: java/collection/arraylist
  type: article
  category: 主模块子文章
  summary: ArrayList 动态数组实现：扩容机制、fail-fast、序列化陷阱。
-->

# ArrayList 源码剖析与最佳实践

## 一、底层 Object[] 数组结构

ArrayList 的核心是一个动态数组, 通过 `transient Object[] elementData` 字段存储元素。

```
┌─────────────────────────────────────────────┐
│                 ArrayList                    │
├─────────────────────────────────────────────┤
│  transient Object[] elementData              │
│  int size                                    │
│  static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA │
├─────────────────────────────────────────────┤
│   elementData[0] ──► "A"                     │
│   elementData[1] ──► "B"                     │
│   elementData[2] ──► "C"                     │
│   elementData[3] ──► null (未使用)            │
│   elementData[4] ──► null (未使用)            │
│                  capacity = 5                 │
│                  size = 3                     │
└─────────────────────────────────────────────┘
```

**关键字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `elementData` | `transient Object[]` | 实际存储元素的数组, transient 表示不参与默认序列化 |
| `size` | `int` | 逻辑大小(元素个数), 非数组容量 |
| `DEFAULT_CAPACITY` | `static final int = 10` | 无参构造的默认初始容量 |
| `DEFAULTCAPACITY_EMPTY_ELEMENTDATA` | `static final Object[]` | 无参构造共享的空数组标记 |
| `EMPTY_ELEMENTDATA` | `static final Object[]` | 容量为 0 时共享的空数组标记 |
| `MAX_ARRAY_SIZE` | `static final int = Integer.MAX_VALUE - 8` | 数组最大尺寸, 防止 OOM |

**序列化机制:** `elementData` 被 `transient` 修饰, ArrayList 自定义了 `writeObject` / `readObject`, 只序列化实际元素 (`size` 个), 不序列化空槽位, 节省空间。

---
---

## 二、构造方法

### 2.1 无参构造

```java
public ArrayList() {
    this.elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
}
```

不会立即分配 10 个元素的数组, 而是指向一个**共享的空数组**。真正的第一次 `add()` 时才会扩容到 `DEFAULT_CAPACITY = 10`。这是懒加载策略, 避免构造后未使用造成的内存浪费。

```
构造后:    elementData ──► []  (共享空数组, size=0)
首次add(): elementData ──► [null, null, null, null, null, null, null, null, null, null]  (扩容到10)
```

### 2.2 指定初始容量

```java
public ArrayList(int initialCapacity) {
    if (initialCapacity > 0) {
        this.elementData = new Object[initialCapacity];
    } else if (initialCapacity == 0) {
        this.elementData = EMPTY_ELEMENTDATA;  // 共享空数组
    } else {
        throw new IllegalArgumentException("Illegal Capacity: " + initialCapacity);
    }
}
```

直接分配指定大小的数组。若传入 0, 同样指向共享空数组 `EMPTY_ELEMENTDATA`。

### 2.3 集合构造

```java
public ArrayList(Collection<? extends E> c) {
    Object[] a = c.toArray();
    if ((size = a.length) != 0) {
        if (c.getClass() == ArrayList.class) {
            elementData = Arrays.copyOf(a, size, Object[].class);
        } else {
            elementData = Arrays.copyOf(a, size, Object[].class);
        }
        // 防御性拷贝: c.toArray() 可能返回非 Object[] 类型
        if (elementData.getClass() != Object[].class)
            elementData = Arrays.copyOf(elementData, size, Object[].class);
    } else {
        elementData = EMPTY_ELEMENTDATA;
    }
}
```

直接将集合元素拷贝到数组, 容量等于集合大小, 不存在扩容过程。包含类型防御, 防止 `c.toArray()` 返回非 `Object[]` (如 `List<String>` 的 `toArray` 可能返回 `String[]`)。

---

## 三、add() 流程与扩容机制

### 3.1 add(E e) 流程

```java
public boolean add(E e) {
    modCount++;                          // 结构性修改计数 +1
    add(e, elementData, size);           // 调用私有方法
    return true;
}

private void add(E e, Object[] elementData, int s) {
    if (s == elementData.length)         // 数组满了, 需要扩容
        elementData = grow(s + 1);
    elementData[s] = e;                  // 在尾部赋值
    size = s + 1;                        // 逻辑大小 +1
}
```

```
add(e) 执行流程:
┌──────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────────┐
│ modCount++│───►│ s == length? │──是─►│ grow(s+1) 扩容 │───►│ elementData[s]=e │
└──────────┘    └──────────────┘    └────────────────┘    │ size = s + 1     │
                       │否                                └──────────────┘
                       ▼
                ┌──────────────┐
                │elementData[s]=e│
                │size = s + 1    │
                └──────────────┘
```

### 3.2 add(int index, E element) 流程

```java
public void add(int index, E element) {
    rangeCheckForAdd(index);           // 检查 index 合法性 [0, size]
    modCount++;
    if (size == elementData.length)
        grow(size + 1);
    System.arraycopy(elementData, index, elementData, index + 1, size - index);
    elementData[index] = element;
    size++;
}
```

插入指定位置, 需要将 index 及之后的所有元素后移一位, 时间复杂度 `O(n - index)`。

### 3.3 grow() 扩容机制

```java
private Object[] grow(int minCapacity) {
    int oldCapacity = elementData.length;
    if (oldCapacity > 0 || elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
        int newCapacity = ArraysSupport.newLength(oldCapacity,
                minCapacity - oldCapacity,    /* minimum growth */
                oldCapacity >> 1              /* preferred growth: 1.5倍 */);
        return elementData = Arrays.copyOf(elementData, newCapacity);
    } else {
        return elementData = new Object[Math.max(DEFAULT_CAPACITY, minCapacity)];
    }
}
```

**扩容规则:**

| 场景 | 新容量计算 |
|------|------------|
| 首次 add (空数组) | `max(DEFAULT_CAPACITY, minCapacity)` = 10 |
| 后续扩容 | `oldCapacity + (oldCapacity >> 1)` ≈ **1.5 倍** |
| 1.5 倍仍不够 | 使用 `minCapacity` (最少需要的容量) |
| 超过 MAX_ARRAY_SIZE | 调用 `hugeCapacity(minCapacity)`, 可扩至 `Integer.MAX_VALUE` |

**容量增长序列:** 10 → 15 → 22 → 33 → 49 → 73 → 109 → 163 → ...

```
扩容过程 (Arrays.copyOf 底层调用 System.arraycopy):

旧数组: [A][B][C][D][E]          capacity=5, size=5
                        │
                        ▼  grow(6)  →  newCapacity = 5 + (5>>1) = 7
                        │
新数组: [A][B][C][D][E][ ][ ]       capacity=7, size=5
                              ↑
                    System.arraycopy
                    (旧→新, 拷贝 size 个元素)
```

### 3.4 ensureCapacity() 手动扩容

```java
public void ensureCapacity(int minCapacity) {
    if (minCapacity > elementData.length
        && !(elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA && minCapacity <= DEFAULT_CAPACITY)) {
        modCount++;
        grow(minCapacity);
    }
}
```

当预先知道元素数量时, 可手动指定容量, 避免多次自动扩容带来的数组拷贝开销。

---

## 四、get / set / remove 流程

### 4.1 get(int index)

```java
public E get(int index) {
    Objects.checkIndex(index, size);     // 检查 0 <= index < size
    return elementData(index);            // 返回 elementData[index]
}
```

直接通过数组下标访问, 时间复杂度 `O(1)`。

### 4.2 set(int index, E element)

```java
public E set(int index, E element) {
    Objects.checkIndex(index, size);
    E oldValue = elementData(index);
    elementData[index] = element;         // 覆盖原位置
    return oldValue;                      // 返回旧值
}
```

时间复杂度 `O(1)`, 不会改变数组大小。

### 4.3 remove(int index)

```java
public E remove(int index) {
    Objects.checkIndex(index, size);
    modCount++;
    E oldValue = elementData(index);
    int numMoved = size - index - 1;      // 需要前移的元素个数
    if (numMoved > 0)
        System.arraycopy(elementData, index + 1, elementData, index, numMoved);
    elementData[--size] = null;           // 最后一个位置置 null (帮助 GC)
    return oldValue;
}
```

```
remove(1) 过程 (删除 index=1 的 B):

删除前: [A][B][C][D][E]    size=5
                │
                ▼  System.arraycopy(从 index+1 拷贝到 index, 拷贝 numMoved=3 个)
                │
删除后: [A][C][D][E][null]  size=4
                           ↑ 置 null 帮助 GC
```

时间复杂度 `O(n - index)`, 删除尾部元素最快 `O(1)`, 删除头部最慢 `O(n)`。

### 4.4 remove(Object o)

```java
public boolean remove(Object o) {
    if (o == null) {
        for (int index = 0; index < size; index++)
            if (elementData[index] == null) {
                fastRemove(index);
                return true;
            }
    } else {
        for (int index = 0; index < size; index++)
            if (o.equals(elementData[index])) {
                fastRemove(index);
                return true;
            }
    }
    return false;
}
```

从头遍历查找, 找到后调用 `fastRemove` (与 `remove(index)` 类似但不做边界检查和返回值), 时间复杂度 `O(n)`。

---

## 五、迭代器 ArrayList$Itr

### 5.1 迭代器结构

```java
private class Itr implements Iterator<E> {
    int cursor;        // 下一个要返回的元素下标, 初始为 0
    int lastRet = -1;  // 上一次返回的元素下标, 初始为 -1
    int expectedModCount = modCount;  // 期望的 modCount, 用于检测并发修改

    public boolean hasNext() {
        return cursor != size;
    }

    public E next() {
        checkForComodification();      // 检查 modCount 是否变化
        int i = cursor;
        if (i >= size) throw new NoSuchElementException();
        cursor = i + 1;
        return elementData(lastRet = i);
    }

    public void remove() {
        if (lastRet < 0) throw new IllegalStateException();
        checkForComodification();
        ArrayList.this.remove(lastRet); // 调用外部类的 remove
        cursor = lastRet;               // cursor 回退
        lastRet = -1;
        expectedModCount = modCount;    // 同步 modCount
    }
}
```

### 5.2 fail-fast 机制

```java
final void checkForComodification() {
    if (modCount != expectedModCount)
        throw new ConcurrentModificationException();
}
```

```
并发修改检测:

迭代器创建时: expectedModCount = modCount = 5

线程A (迭代): 读取 elementData[0]
线程B (修改): list.add("X")  → modCount = 6
线程A (迭代): checkForComodification()
              → 5 != 6 → 抛出 ConcurrentModificationException!
```

**关键点:**

| 场景 | 是否安全 | 说明 |
|------|----------|------|
| 使用 `Iterator.remove()` | 安全 | 会同步 `expectedModCount = modCount` |
| 使用 `list.remove()` 遍历时 | 不安全 | 触发 CME |
| 单线程遍历中调用 `list.add()` | 不安全 | 同样触发 CME |
| `ArrayList$Itr` 与 `ListIterator` | 都支持 fail-fast | 检测机制相同 |

### 5.3 ListIterator

```java
private class ListItr extends Itr implements ListIterator<E> {
    public boolean hasPrevious() { return cursor != 0; }
    public E previous() { ... }           // 向前遍历
    public void add(E e) { ... }          // 在当前位置插入
    public void set(E e) { ... }          // 替换 lastRet 位置的元素
}
```

`ListItr` 继承 `Itr`, 额外支持双向遍历、`add()`、`set()` 操作。

---

## 六、subList 陷阱

### 6.1 subList 返回的是视图

```java
public List<E> subList(int fromIndex, int toIndex) {
    subListRangeCheck(fromIndex, toIndex, size);
    return new SubList(this, 0, fromIndex, toIndex);  // 内部类, 持有原 List 引用
}
```

```
subList 视图结构:

原列表: [0:A][1:B][2:C][3:D][4:E][5:F]   size=6

subList(1, 4) 返回视图:
┌─────────────────────────────┐
│         SubList              │
│  root = 原ArrayList          │
│  offset = 1                  │
│  size = 3                    │
├─────────────────────────────┤
│  get(0) → root.elementData[1] = B │
│  get(1) → root.elementData[2] = C │
│  get(2) → root.elementData[3] = D │
└─────────────────────────────┘

注意: 不是新列表! 修改 SubList 会影响原列表!
```

### 6.2 常见陷阱

```java
List<Integer> list = new ArrayList<>(Arrays.asList(0, 1, 2, 3, 4));
List<Integer> sub = list.subList(1, 4);   // [1, 2, 3]

// 陷阱 1: 修改 subList 会影响原列表
sub.set(0, 99);
// list  → [0, 99, 2, 3, 4]
// sub   → [99, 2, 3]

// 陷阱 2: 修改原列表后, subList 操作抛 CME
list.add(100);
sub.get(0);   // ConcurrentModificationException! (modCount 变化)

// 陷阱 3: ClassCastException
ArrayList<Integer> sub2 = (ArrayList<Integer>) list.subList(0, 3);
// ClassCastException! SubList 不是 ArrayList 的子类
```

### 6.3 正确获取独立子列表

```java
// 方式 1: 新 ArrayList 包装 (推荐)
List<Integer> independent = new ArrayList<>(list.subList(1, 4));

// 方式 2: Java 10+
List<Integer> independent = List.copyOf(list.subList(1, 4));

// 方式 3: 使用 Stream
List<Integer> independent = list.stream().skip(1).limit(3).collect(Collectors.toList());
```

---

## 七、ArrayList 与 Vector 对比

### 7.1 核心差异

| 对比项 | ArrayList | Vector |
|--------|-----------|--------|
| 包 | `java.util` (JDK 1.2) | `java.util` (JDK 1.0) |
| 线程安全 | **否** | **是** (方法级 synchronized) |
| 扩容策略 | **1.5 倍** | **2 倍** (或指定增量) |
| 性能 | 高 (无锁开销) | 低 (每个方法都同步) |
| 构造参数 | 仅 initialCapacity | initialCapacity + capacityIncrement |
| 枚举接口 | 无 | 提供 `elements()` 返回 Enumeration |
| 迭代器 fail-fast | 是 | 是 (但 VectorIterator 额外检查) |
| 历史定位 | 推荐使用 | 遗留类, 不推荐新代码使用 |

### 7.2 Vector 扩容源码

```java
// Vector 的 grow 方法
private Object[] grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = ArraysSupport.newLength(oldCapacity,
            minCapacity - oldCapacity,
            capacityIncrement > 0 ? capacityIncrement : oldCapacity);  // 2倍!
    return elementData = Arrays.copyOf(elementData, newCapacity);
}
```

### 7.3 线程安全的替代方案

```java
// 替代方案 1: Collections.synchronizedList (包装)
List<String> syncList = Collections.synchronizedList(new ArrayList<>());

// 替代方案 2: CopyOnWriteArrayList (读多写少)
List<String> cowList = new CopyOnWriteArrayList<>();

// 替代方案 3: 手动同步 (推荐粒度更细)
synchronized (list) {
    list.add("item");
}
```

**Vector 的同步缺陷:** 即使复合操作也不安全。

```java
// 反模式: Vector 的 "线程安全" 是假象
if (!vector.contains(element)) {     // 操作1: 检查
    vector.add(element);             // 操作2: 添加
}
// 两个操作之间可能被其他线程插入相同元素! 必须整体加锁:
synchronized (vector) {
    if (!vector.contains(element)) {
        vector.add(element);
    }
}
```

---

## 八、ArrayList 与 LinkedList 详细对比

### 8.1 数据结构对比

```
ArrayList (动态数组):
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ A │ B │ C │ D │ E │   │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
  0   1   2   3   4   ← 连续内存, 随机访问 O(1)

LinkedList (双向链表):
 head                                                   tail
  │                                                      │
  ▼                                                      ▼
┌───┬───┬───┐   ┌───┬───┬───┐   ┌───┬───┬───┐   ┌───┬───┬───┐
│◄──│ A │──►│◄─►│◄──│ B │──►│◄─►│◄──│ C │──►│◄─►│◄──│ D │──►│
└───┴───┴───┘   └───┴───┴───┘   └───┴───┴───┘   └───┴───┴───┘
  Node            Node            Node            Node
  prev=null       prev=A          prev=B          prev=C
  next=B          next=C          next=D          next=null
  (每个节点额外 2 个引用开销)
```

### 8.2 时间复杂度对比

| 操作 | ArrayList | LinkedList | 说明 |
|------|-----------|------------|------|
| `get(i)` | **O(1)** | O(n) | 数组直接下标 vs 链表遍历 |
| `set(i, e)` | **O(1)** | O(n) | 同上 |
| `add(e)` 尾部 | **O(1)** 均摊 | O(1) | ArrayList 可能触发扩容 |
| `add(i, e)` 中间 | O(n-i) | O(n) | 都需要移动/遍历 |
| `remove(i)` 中间 | O(n-i) | O(n) | 同上 |
| `remove(e)` 按值 | O(n) | O(n) | 都需要遍历查找 |
| `contains(e)` | O(n) | O(n) | 都需要遍历 |
| 迭代 `Iterator.next()` | O(1) | O(1) | 都是顺序访问 |
| 内存占用 | **低** | 高 | 每个节点多 2 个引用 |

### 8.3 内存占用对比

```
存储 N 个元素:

ArrayList:
  Object[] 数组 = N 个引用 + (扩容冗余空间)
  假设容量 10, 实际 3 个元素: 10 × 4B(32位) = 40B (含7个空槽)

LinkedList:
  N × Node 对象
  每个 Node = 对象头(12B) + prev引用(4B) + next引用(4B) + item引用(4B) = 24B (对齐后)
  3 个元素: 3 × 24B = 72B (无冗余但固定开销大)
  + 3 个 item 引用 (已在 Node 内)
```

### 8.4 缓存局部性

```
CPU Cache 影响:

ArrayList: [A][B][C][D][E][F]
            ↑ 连续内存, 一次 cache line 加载可获取多个元素
            缓存命中率高

LinkedList: A ──► B ──► C ──► D
            ↑ 节点分散在堆中, 每次 next() 可能 cache miss
            缓存命中率低

实际性能: ArrayList 遍历通常比 LinkedList 快 3-5 倍
```

### 8.5 使用场景建议

| 场景 | 推荐 | 原因 |
|------|------|------|
| 频繁随机访问 | ArrayList | O(1) 下标访问 |
| 频繁尾部增删 | ArrayList | 均摊 O(1), 内存紧凑 |
| 频繁头部/中间插入删除 | LinkedList | 但需注意先定位到位置也是 O(n) |
| 实现队列/栈 | LinkedList / ArrayDeque | 提供 Deque 接口 |
| 大数据量存储 | ArrayList | 内存效率高, CPU 缓存友好 |
| 读多写少的并发场景 | CopyOnWriteArrayList | 写时复制 |
| 几乎全部场景 | **ArrayList** | 90% 情况下 ArrayList 是更好的选择 |

**重要结论:** 除非确实需要频繁在头部/中间插入删除且有 `ListIterator` 定位, 否则一律使用 `ArrayList`。LinkedList 的 O(1) 插入优势在 Java 中几乎无法发挥, 因为定位到插入位置本身就需要 O(n) 遍历。

---

## 九、面试高频问题

### Q1: ArrayList 的默认初始容量是多少? 什么时候真正分配?

**答:** 默认容量为 10, 但无参构造时并不会立即分配, 而是指向共享空数组 `DEFAULTCAPACITY_EMPTY_ELEMENTDATA`。**第一次调用 `add()` 时**才会扩容到 10。这是懒加载优化。

### Q2: ArrayList 的扩容倍数是多少? 底层如何实现?

**答:** 扩容为原来的 **1.5 倍** (`oldCapacity + oldCapacity >> 1`)。底层通过 `Arrays.copyOf()` 实现, `Arrays.copyOf()` 内部调用 `System.arraycopy()` (native 方法) 进行数组拷贝。

### Q3: ArrayList 线程安全吗? 如何保证线程安全?

**答:** 不安全。保证线程安全的三种方式:
1. `Collections.synchronizedList(new ArrayList<>())` - 方法级同步
2. `CopyOnWriteArrayList` - 写时复制, 适合读多写少
3. 手动 `synchronized` 或 `ReentrantLock` 包裹

### Q4: ArrayList 遍历时删除元素的正确方式?

**答:** 使用 `Iterator.remove()`, 不能使用 `for-each` 或普通 for 循环中直接调用 `list.remove()`。

```java
// 正确方式
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    if ("target".equals(it.next())) {
        it.remove();   // 安全
    }
}

// 反模式
for (String s : list) {
    if ("target".equals(s)) {
        list.remove(s);   // ConcurrentModificationException!
    }
}
```

### Q5: subList 返回的是什么? 有什么坑?

**答:** 返回的是 `RandomAccessSubList` 视图, 不是新 ArrayList。对 subList 的修改会反映到原列表, 原列表的结构修改会导致 subList 抛出 CME。需要独立副本时应 `new ArrayList<>(list.subList(from, to))`。

### Q6: ArrayList 和 LinkedList 的区别? 什么时候用哪个?

**答:** 核心区别是底层数据结构 (数组 vs 双向链表)。ArrayList 支持 O(1) 随机访问, 内存紧凑, 缓存友好; LinkedList 插入删除理论 O(1) 但定位 O(n)。实际场景中 90% 以上情况应选择 ArrayList。

### Q7: ArrayList 的 elementData 为什么用 transient 修饰?

**答:** 为了自定义序列化。`elementData` 可能有大量空槽位 (容量 > 实际大小), 自定义 `writeObject` 只序列化 `size` 个有效元素, 节省序列化后的体积。反序列化时 `readObject` 重新分配适当大小的数组。

### Q8: ArrayList 的 fastRemove 和 remove 有什么区别?

**答:** `fastRemove` 是私有方法, 不做 index 边界检查, 不返回被删除的元素。主要在 `Iterator.remove()` 和 `removeIf()` 等内部方法中调用, 减少不必要的检查提升性能。

### Q9: ArrayList 最大容量是多少?

**答:** 理论最大容量是 `Integer.MAX_VALUE - 8` (`MAX_ARRAY_SIZE`)。超过此值时 `hugeCapacity()` 方法会尝试扩展到 `Integer.MAX_VALUE`, 但受限于 JVM 堆内存, 实际中几乎不可能达到。

### Q10: 为什么 ArrayList 的迭代器是 fail-fast 的?

**答:** 迭代器创建时保存 `expectedModCount = modCount`, 每次 `next()` / `remove()` 检查两者是否相等。不等说明其他线程 (或同线程其他代码) 做了结构性修改, 立即抛出 `ConcurrentModificationException`, 避免不确定的遍历行为。这是一种**快速失败的安全策略**, 不是真正的并发控制。

### Q11: `Arrays.asList()` 返回的 List 能 add 吗?

**答:** 不能。`Arrays.asList()` 返回的是 `Arrays` 的内部类 `ArrayList`, 不是 `java.util.ArrayList`, 底层是固定大小的数组包装, `add()` / `remove()` 会抛 `UnsupportedOperationException`。

```java
List<String> list = Arrays.asList("a", "b", "c");
list.add("d");   // UnsupportedOperationException!

// 正确做法
List<String> mutable = new ArrayList<>(Arrays.asList("a", "b", "c"));
mutable.add("d");   // OK
```

### Q12: ArrayList 的 trimToSize() 方法有什么用?

**答:** 将 `elementData` 的容量缩减为当前 `size`, 释放多余的内存。适用于添加完所有元素后, 确认不会再增长的场景。

```java
ArrayList<String> list = new ArrayList<>();   // capacity=10
for (int i = 0; i < 3; i++) list.add("x");    // size=3, capacity=10
list.trimToSize();                            // capacity=3, 节省 7 个引用空间
```
