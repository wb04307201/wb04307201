<!--
module:
  parent: java
  slug: java/copy-on-write
  type: article
  category: 主模块子文章
  summary: 深入理解 CopyOnWriteArrayList 和 CopyOnWriteArraySet 的写时复制原理、源码分析、性能特征及适用场景。
-->

# 写时复制集合

> 目标：深入理解 CopyOnWriteArrayList 和 CopyOnWriteArraySet 的写时复制原理、源码分析、性能特征及适用场景。

---
## 引言：反直觉代码

写时复制集合 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、CopyOnWriteArrayList（写时复制列表）

### 1.1 写时复制原理

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

### 1.2 核心源码分析

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

### 1.3 内存开销分析

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

### 1.4 适用场景

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

### 1.5 使用示例

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

## 二、CopyOnWriteArraySet

### 2.1 原理

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

### 2.2 核心源码

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

### 2.3 性能特征与对比

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

## 相关章节

- [父目录：并发集合总览](../README.md)
- [ConcurrentHashMap 专题](../../../../README.md)
- [并发队列](../queue/README.md)
- [跳表集合](../skip-list/README.md)
