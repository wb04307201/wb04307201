## 一、底层双向链表结构

`LinkedList<E>` 的底层是一个**带头结点的双向链表**（实际上没有虚拟头结点，first 和 last 直接指向真实节点）。

```
┌───────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ first ├────>│ Node<E>          │<--->│ Node<E>          │<--->│ Node<E>          │<──┐
└───────┘     │ item | next | prev│     │ item | next | prev│     │ item | next | prev│   │
              └──────────────────┘     └──────────────────┘     └──────────────────┘   │
                                                                                       │
┌───────┐                                                                             │
│ last  ├─────────────────────────────────────────────────────────────────────────────┘
└───────┘
```

### 1.1 Node 内部类源码

```java
private static class Node<E> {
    E item;          // 数据域
    Node<E> next;    // 后继指针
    Node<E> prev;    // 前驱指针

    Node(Node<E> prev, E element, Node<E> next) {
        this.item = element;
        this.next = next;
        this.prev = prev;
    }
}
```

### 1.2 核心成员变量

```java
transient int size = 0;        // 链表长度
transient Node<E> first;       // 头节点引用
transient Node<E> last;        // 尾节点引用
transient int modCount = 0;    // 结构性修改次数 (用于 fail-fast)
```

> **关键点**：`size` 是显式维护的，因此 `size()` 是 **O(1)** 操作。

---
## 引言：反直觉代码
本文 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 二、构造方法

| 构造方法 | 说明 | 时间复杂度 |
|---------|------|-----------|
| `LinkedList()` | 创建空链表 | O(1) |
| `LinkedList(Collection<? extends E> c)` | 将集合元素依次添加到链表尾部 | O(n) |

```java
// 空构造
LinkedList<String> list = new LinkedList<>();   // first = last = null, size = 0

// 带集合构造
LinkedList<String> list = new LinkedList<>(Arrays.asList("A", "B", "C"));
// 内部调用 addAll(c)，逐个 linkLast
```

---

## 三、添加操作详解

### 3.1 add(E e) — 尾插

```java
public boolean add(E e) {
    linkLast(e);
    return true;
}

void linkLast(E e) {
    final Node<E> l = last;
    final Node<E> newNode = new Node<>(l, e, null);
    last = newNode;
    if (l == null)          // 链表为空
        first = newNode;
    else
        l.next = newNode;   // 旧尾节点的 next 指向新节点
    size++;
    modCount++;
}
```

```
添加前:  [A] <--> [B]         last -> [B]
添加后:  [A] <--> [B] <--> [C]  last -> [C]
```

### 3.2 addFirst(E e) — 头插

```java
public void addFirst(E e) {
    linkFirst(e);
}

private void linkFirst(E e) {
    final Node<E> f = first;
    final Node<E> newNode = new Node<>(null, e, f);
    first = newNode;
    if (f == null)
        last = newNode;
    else
        f.prev = newNode;
    size++;
    modCount++;
}
```

### 3.3 addLast(E e) — 等价于 add

```java
public void addLast(E e) {
    linkLast(e);   // 与 add 完全一致
}
```

### 3.4 add(int index, E element) — 指定位置插入

```java
public void add(int index, E element) {
    checkPositionIndex(index);
    if (index == size)
        linkLast(element);
    else
        linkBefore(element, node(index));
}
```

> **性能陷阱**：`add(index, e)` 需要先遍历到 index 位置，时间复杂度为 **O(n)**，并非 O(1)。

---

## 四、get / peek / poll 的区别

| 方法 | 所属接口 | 空列表行为 | 返回值 | 是否删除 |
|------|---------|-----------|--------|---------|
| `getFirst()` | Deque | 抛 `NoSuchElementException` | E | 否 |
| `peekFirst()` / `peek()` | Deque/Queue | 返回 `null` | E | 否 |
| `get(int index)` | List | 抛 `IndexOutOfBoundsException` | E | 否 |
| `removeFirst()` | Deque | 抛 `NoSuchElementException` | E | 是 |
| `pollFirst()` / `poll()` | Deque/Queue | 返回 `null` | E | 是 |
| `pop()` | Deque | 抛 `NoSuchElementException` | E | 是 |

```java
LinkedList<String> list = new LinkedList<>();

// 空列表对比
list.getFirst();    // NoSuchElementException
list.peekFirst();   // null
list.peek();        // null (peek 等价于 peekFirst)

list.add("A");
list.add("B");

// get vs peek vs poll
list.get(0);        // "A" (按索引，O(n))
list.peekFirst();   // "A" (看头节点，O(1)，不移除)
list.pollFirst();   // "A" (看头节点，O(1)，移除)
// 此时 list: [B]
```

---

## 五、作为 Deque 的用法

`LinkedList` 同时实现了 `List`、`Queue`、`Deque` 接口，一表多用。

### 5.1 栈操作 (Stack 语义)

```
push(e)  <==>  addFirst(e)
pop()    <==>  removeFirst()
peek()   <==>  peekFirst()
```

```java
Deque<String> stack = new LinkedList<>();

stack.push("A");       // [A]
stack.push("B");       // [B, A]
stack.push("C");       // [C, B, A]

stack.peek();          // "C" (栈顶，不移除)
stack.pop();           // "C" (出栈)  -> [B, A]
stack.pop();           // "B"        -> [A]
stack.pop();           // "A"        -> []
stack.pop();           // NoSuchElementException!
```

### 5.2 队列操作 (Queue 语义)

```
offer(e)   <==>  addLast(e)
poll()     <==>  removeFirst()
peek()     <==>  peekFirst()
```

```java
Queue<String> queue = new LinkedList<>();

queue.offer("A");      // [A]
queue.offer("B");      // [A, B]
queue.offer("C");      // [A, B, C]

queue.peek();          // "A" (队首，不移除)
queue.poll();          // "A" (出队)  -> [B, C]
queue.poll();          // "B"        -> [C]
```

### 5.3 方法对照表

| 栈操作 | 队列操作 | 底层方法 |
|-------|---------|---------|
| `push(e)` | `offer(e)` / `add(e)` | `addFirst` / `addLast` |
| `pop()` | `poll()` | `removeFirst()` |
| `peek()` | `peek()` | `peekFirst()` |

---

## 六、迭代器 — ListItr 双向遍历

`LinkedList` 的 `listIterator()` 返回 `ListItr`，支持**正向**和**反向**遍历。

```java
LinkedList<String> list = new LinkedList<>();
list.add("A");
list.add("B");
list.add("C");

// 正向遍历
ListIterator<String> it = list.listIterator();
while (it.hasNext()) {
    System.out.print(it.next() + " ");   // A B C
}

// 反向遍历 (光标已在末尾)
while (it.hasPrevious()) {
    System.out.print(it.previous() + " ");  // C B A
}
```

### 6.1 ListItr 核心原理

```java
private class ListItr implements ListIterator<E> {
    private Node<E> lastReturned = null;   // 上次返回的节点
    private Node<E> next;                   // next() 将返回的节点
    private int nextIndex;                  // next 的索引
    private int expectedModCount = modCount; // fail-fast 检查

    ListItr(int index) {
        if (index == size) {
            next = null;                     // 从尾部开始
        } else {
            next = node(index);              // O(n) 定位
        }
        nextIndex = index;
    }
}
```

### 6.2 遍历性能对比

| 遍历方式 | 时间复杂度 | 说明 |
|---------|-----------|------|
| `for (E e : list)` | O(n) | 内部用 ListItr，从头到尾 |
| `for (int i=0; i<size; i++) get(i)` | **O(n^2)** | 每次 get 都从头遍历！ |
| `listIterator(index)` | O(n) | 首次定位 O(n)，后续 O(1) |
| 反向 `hasPrevious/previous` | O(n) | 从后往前同样 O(1) 步进 |

> **严重警告**：永远不要用索引 `for` 循环遍历 `LinkedList`，这是 **O(n^2)** 操作！

```java
// BAD - O(n^2)
for (int i = 0; i < list.size(); i++) {
    list.get(i);  // 每次都要从 first/last 走到位置 i
}

// GOOD - O(n)
for (String s : list) { }           // 增强 for
for (Iterator<String> it = list.iterator(); it.hasNext(); ) { }
```

---

## 七、为什么 ArrayDeque 通常比 LinkedList 更好

| 对比维度 | LinkedList | ArrayDeque |
|---------|------------|------------|
| 底层结构 | 双向链表 | 循环数组 |
| 内存开销 | 每个节点额外 2 个引用 + 对象头 | 仅数组本身 |
| 缓存局部性 | **差**（节点分散在堆上） | **好**（连续内存） |
| addFirst/addLast | O(1) | O(1) 均摊 |
| 随机访问 | O(n) | O(1) |
| GC 压力 | 大量 Node 对象 | 单个数组 |
| 扩容 | 不需要 | 2 倍扩容 |
| 是否允许 null | **是** | **否** |

```
LinkedList 内存布局 (每个 Node 都是独立对象):

Heap:  [Node@1a2b][Node@3c4d][Node@5e6f] ... (分散)
        ↓       ↓       ↓
       [A]     [B]     [C]

ArrayDeque 内存布局 (连续数组):

Heap:  [ null, A, B, C, null, null, null, null ]
        ↑head      ↑tail
        (循环使用)
```

### 7.1 定量分析

假设存储 100 万个 `String` 引用：

- **LinkedList**：100 万个 Node 对象 × (24 字节对象头 + 8 字节 item + 8 字节 next + 8 字节 prev) ≈ **48 MB** 额外开销
- **ArrayDeque**：仅一个 `Object[]` 数组 + 少量字段 ≈ **8 MB** 额外开销

### 7.2 官方文档原话

> *"This class is likely to be faster than `Stack` when used as a stack, and faster than `LinkedList` when used as a queue."* — `ArrayDeque` Javadoc

---

## 八、面试高频问题

### Q1：LinkedList 是线程安全的吗？

**不是**。多线程并发修改会破坏链表结构，导致 `ConcurrentModificationException` 或更严重的死循环/数据丢失。

```java
// 线程安全替代方案
List<String> safe = Collections.synchronizedList(new LinkedList<>());
// 或使用 ConcurrentLinkedDeque (无锁 CAS)
Deque<String> concurrent = new ConcurrentLinkedDeque<>();
```

### Q2：LinkedList 的 get(int) 为什么慢？

```java
Node<E> node(int index) {
    // 性能优化：判断靠近 head 还是 tail
    if (index < (size >> 1)) {
        Node<E> x = first;
        for (int i = 0; i < index; i++)
            x = x.next;
        return x;
    } else {
        Node<E> x = last;
        for (int i = size - 1; i > index; i--)
            x = x.prev;
        return x;
    }
}
```

> **优化点**：从靠近的一端开始遍历，最坏情况仍是 O(n/2)。

### Q3：ArrayList vs LinkedList 如何选择？

| 场景 | 推荐 | 原因 |
|------|------|------|
| 频繁随机访问 | ArrayList | O(1) vs O(n) |
| 频繁头尾插入/删除 | ArrayDeque | 缓存友好 |
| 频繁中间插入/删除 | 视情况 | 两者都需要 O(n)，LinkedList 省移动但多遍历 |
| 内存敏感 | ArrayList | 紧凑存储 |
| 需要 null 元素的 Deque | LinkedList | ArrayDeque 不允许 null |
| 实现 LRU 缓存 | LinkedList | 配合 HashMap 用 remove + addLast |

### Q4：LinkedList 的 fail-fast 机制如何工作？

```java
// 迭代器检查
final void checkForComodification() {
    if (modCount != expectedModCount)
        throw new ConcurrentModificationException();
}
```

在 `next()`、`previous()`、`remove()`、`add()` 等方法入口处都会检查 `modCount`。

### Q5：LinkedList 可以用来做 LRU Cache 吗？

可以，但通常用 `LinkedHashMap` 更优雅：

```java
// 方案一：LinkedList + HashMap
class LRUCache<K, V> {
    private final int capacity;
    private final Map<K, V> map = new HashMap<>();
    private final LinkedList<K> order = new LinkedList<>();

    public V get(K key) {
        if (!map.containsKey(key)) return null;
        order.remove(key);          // O(n) 瓶颈！
        order.addLast(key);
        return map.get(key);
    }

    public void put(K key, V value) {
        if (map.size() >= capacity) {
            K evict = order.removeFirst();
            map.remove(evict);
        }
        order.addLast(key);
        map.put(key, value);    // 注意: 此处简化了 key 已存在的更新逻辑
    }
}

// 方案二：LinkedHashMap (推荐，O(1))
Map<K, V> lru = new LinkedHashMap<>(capacity, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }
};
```

### Q6：LinkedList 序列化时为什么要特殊处理？

```java
// LinkedList 的 Node 没有实现 Serializable
// 所以 writeObject/readObject 需要手动序列化 item 数据

private void writeObject(java.io.ObjectOutputStream s) throws IOException {
    s.defaultWriteObject();
    s.writeInt(size);
    for (Node<E> x = first; x != null; x = x.next)
        s.writeObject(x.item);   // 只序列化数据，不序列化节点结构
}
```

这样做的目的是避免序列化整个链表结构（包含 next/prev 引用），节省空间并避免循环引用问题。
