# 跳表集合

> 目标：理解 ConcurrentSkipListMap 和 ConcurrentSkipListSet 的跳表数据结构、无锁操作实现及有序并发场景应用。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

跳表集合 本应该很简单，目标：理解 ConcurrentSkipListMap 和 ConcurrentSkipListSet 的跳表数据结构、无锁操作实现及有序并发场景应用

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、跳表（Skip List）原理

```
跳表是一种可以替代红黑树的概率性数据结构，
通过多层链表实现 O(log n) 的查找、插入和删除。

ASCII 结构示意（4 层跳表）：

  Level 3 (最高层, 约 n/8 个节点):
  HEAD ──────────────────────→ [16] ──────────────────────→ null

  Level 2 (约 n/4 个节点):
  HEAD ────────→ [8] ────────→ [16] ────────→ [24] ────→ null

  Level 1 (约 n/2 个节点):
  HEAD ──→ [4] ──→ [8] ──→ [12] ──→ [16] ──→ [20] ──→ [24] → null

  Level 0 (基础层, 所有节点):
  HEAD → [1]→[2]→[3]→[4]→[5]→[6]→[7]→[8]→[9]→[10]→...→[24]→null

  查找 key=15 的过程（从最高层开始）：
    1. Level 3: HEAD → [16] → 16 > 15，不能前进，下降
    2. Level 2: [8] → [16] → 16 > 15，不能前进，下降
    3. Level 1: [12] → [16] → 16 > 15，不能前进，下降
    4. Level 0: [14] → [15] → 找到！

  查找路径：HEAD → 8 → 12 → 14 → 15
  比较次数 ≈ log₂(n)，而不是 O(n)
```

## 二、随机高度

```
每个新节点的高度是随机生成的（概率 1/2 增加一层）：

  新节点高度算法（简化）：
    level = 1
    while (random.nextBoolean() && level < MAX_LEVEL)
        level++
    return level

  概率分布：
    Level 1: 50%  的节点
    Level 2: 25%  的节点
    Level 3: 12.5% 的节点
    Level 4: 6.25% 的节点
    ...

  期望高度 ≈ log₂(n)
  查找期望时间复杂度 ≈ O(log n)
```

## 三、ConcurrentSkipListMap 结构

```
ConcurrentSkipListMap 的底层节点结构：

  多层索引 + 基础数据层，每层都是单向链表

  Node 结构：
    class Node<K,V> {
        final K key;
        volatile Object value;      // 值或标记删除
        volatile Node<K,V> next;    // 水平链接
    }

    class Index<K,V> {
        final Node<K,V> node;       // 指向的 Node
        final Index<K,V> down;      // 下一层 Index
        volatile Index<K,V> right;  // 水平链接
    }

  整体结构：
    HeadIndex (head)
      ↓ right → down → right → down → right → down
    [Index] → [Index] → [Index]
      ↓         ↓         ↓
    [Node] → [Node] → [Node] → [Node] → [Node]  ← 基础层（数据层）
```

## 四、无锁操作

```
ConcurrentSkipListMap 使用 CAS 实现无锁的插入和删除：

  插入流程：
    1. 从最高层开始，逐层找到插入位置（最右侧 < key 的节点）
    2. 在基础层（Level 0）CAS 插入新节点
    3. 如果新节点有高层索引，从下到上逐层 CAS 插入索引
    4. 如果最高层需要扩展，CAS 更新 Head

  删除流程：
    1. 标记删除（value 设为特殊标记 SELF_KEY）
    2. 从右到左 CAS 删除（跳过已标记节点）
    3. 惰性删除：物理删除可能延迟，不影响正确性

  并发安全：
    - 所有链接修改都用 CAS
    - 删除先标记后删除（两步操作）
    - 读操作看到已删除节点会自动跳过
```

## 五、核心特性

```java
public class ConcurrentSkipListMap<K,V>
        extends AbstractMap<K,V>
        implements ConcurrentNavigableMap<K,V> {

    // 常用操作（全部线程安全）
    V put(K key, V value);
    V get(Object key);
    V remove(Object key);

    // 有序操作
    K firstKey();             // 最小 key
    K lastKey();              // 最大 key
    K ceilingKey(K key);      // ≥ key 的最小 key
    K floorKey(K key);        // ≤ key 的最大 key
    K higherKey(K key);       // > key 的最小 key
    K lowerKey(K key);        // < key 的最大 key

    // 子视图（全部是并发安全的）
    ConcurrentNavigableMap<K,V> subMap(K from, K to);
    ConcurrentNavigableMap<K,V> headMap(K to);
    ConcurrentNavigableMap<K,V> tailMap(K from);

    // 批量操作
    int size();               // 近似值（不精确，高并发时）
    boolean isEmpty();
    void clear();
}
```

```
性能特征：

  操作        | 平均      | 最差
  ───────────|──────────|──────────
  查找        | O(log n) | O(n)（极端退化）
  插入        | O(log n) | O(n)
  删除        | O(log n) | O(n)
  范围查询    | O(log n + k) | O(n + k)

  与 TreeMap 对比：

    维度         | ConcurrentSkipListMap | TreeMap
    ────────────|───────────────────────|──────────
    线程安全     | 是（CAS）              | 否
    底层结构     | 跳表                    | 红黑树
    有序性       | 是                      | 是
    空间开销     | 略高（多层索引）         | 低
    内存局部性   | 差（节点分散）           | 好
    并发性能     | 高（无锁）              | 需要外部同步
```

## 六、ConcurrentSkipListSet

```
ConcurrentSkipListSet 内部持有一个 ConcurrentSkipListMap。

public class ConcurrentSkipListSet<E> extends AbstractSet<E>
        implements NavigableSet<E> {

    private final ConcurrentNavigableMap<E,Object> m;
    private static final Object PRESENT = new Object();

    public ConcurrentSkipListSet() {
        m = new ConcurrentSkipListMap<E,Object>();
    }

    public boolean add(E e) {
        return m.putIfAbsent(e, PRESENT) == null;
    }

    public boolean remove(Object o) {
        return m.remove(o, PRESENT);
    }

    public boolean contains(Object o) {
        return m.containsKey(o);
    }
}

// 使用示例
ConcurrentSkipListSet<Integer> set = new ConcurrentSkipListSet<>();
set.add(5);
set.add(2);
set.add(8);
set.add(1);

// 有序遍历
for (int n : set) {
    System.out.println(n);  // 1, 2, 5, 8
}

// 范围查询
NavigableSet<Integer> sub = set.subSet(2, true, 6, true);  // [2, 5]
```

---

## 相关章节

- [父目录：并发集合总览](../README.md)
- [写时复制集合](../copy-on-write/README.md)
- [并发队列](../queue/README.md)
- [ConcurrentHashMap 专题](../../../../README.md)
