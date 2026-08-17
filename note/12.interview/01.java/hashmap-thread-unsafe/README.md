<!--
question:
  id: 01.java-hashmap-thread-unsafe
  topic: 01.java
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 并发陷阱
  tags: [01.java, HashMap, concurrent, thread-safety]
-->

# HashMap 为什么线程不安全？

## 引子：一段看似正常的多线程代码

```java
Map<String, Integer> map = new HashMap<>();

for (int i = 0; i < 100; i++) {
    int index = i;
    new Thread(() -> {
        for (int j = 0; j < 100; j++) {
            map.put("key-" + index + "-" + j, j);
        }
    }).start();
}
```

**实际现象：**

| 问题 | 表现 |
|------|------|
| 数据丢失 | 预期 10,000 条，实际可能只有 8,000+ 条 |
| JDK 7 死循环 | `get()` 时 CPU 100%，线程永久挂起（链表成环） |
| size 不准 | `map.size()` 返回值偏小，计数丢失 |

---

## 一、核心原理：3 大不安全表现

### 1. 数据丢失（JDK 7/8 都有）

**现象**：两个线程同时 put 到同一个空桶，后执行的覆盖先执行的。

```java
// 线程 A：tab[i] = nodeA   // nodeA.next = null
// 线程 B：tab[i] = nodeB   // nodeB.next = null（覆盖了线程 A）
// 结果：nodeA 丢了
```

**原因**：put 操作是 **check-then-act** 非原子——先检查 `tab[i] == null`，再赋值 `tab[i] = new Node`，两步之间可能被其他线程抢占。

### 2. 死循环（JDK 7 头插法独有）

**现象**：并发扩容后调用 `get()`，CPU 飙升到 100%。

**原因**：JDK 7 用**头插法**迁移链表，并发下两个线程同时反转链表，导致 `e.next` 成环，后续 get 遍历时永远走不出循环。

### 3. size 不准

```java
// ++size 拆解为 3 步
int tmp = size;    // ① 读
tmp = tmp + 1;     // ② 算
size = tmp;        // ③ 写
```

两个线程同时读到 `size = 5`，各自写回 `6`——实际 put 了 2 次，size 只加了 1。`read-modify-write` 不是原子操作。

---

## 二、源码级分析

### 2.1 put 的 check-then-act 非原子

```java
// JDK 8 HashMap.putVal() 简化
final V putVal(K key, V value) {
    int i = (n - 1) & hash;
    if ((p = tab[i]) == null)           // ① check：桶为空
        tab[i] = newNode(hash, key, value, null);  // ② act：直接赋值
    else {
        // 桶不为空，遍历链表追加或覆盖
        for (int binCount = 0; ; ++binCount) {
            if (e.hash == hash && e.key.equals(key)) { e.value = value; break; }
            if ((e = e.next) == null) { pred.next = new Node(...); break; }
        }
    }
    ++size;  // ③ 非原子操作
}
```

线程 A 执行完 ① 判断桶空，还没执行 ② 时被线程 B 抢占。线程 B 也判断桶空（因为 A 还没写入），两个线程都执行 ②，后者覆盖前者——**数据丢失**。

### 2.2 ++size 非原子

```java
// 真实源码
if (++size > threshold) resize();

// 字节码拆解
GETFIELD HashMap.size    // 读取
ICONST_1
IADD                     // 加 1
PUTFIELD HashMap.size    // 写回
IF_ICMPEQ ...            // 比较阈值
```

两个线程同时读到 `size=5` → 各自计算 6 → 各自写回 6。实际 size=6，正确应该是 7。

### 2.3 JDK 7 头插法扩容——链表成环示意

```
初始： 桶 i → A → B → null

线程 1 反转后：桶 i → B → A → null
线程 2 反转中：e=B, next=A, 设 B.next=A 时，A.next 还指向 B...

成环： B ↔ A（互相指向），get 遍历时永远出不去
```

```java
// JDK 7 transfer() 核心代码（头插法）
void transfer(Entry[] newTable) {
    for (Entry<K,V> e : table) {
        while (null != e) {
            Entry<K,V> next = e.next;        // 线程 1 停在这里：next=A
            int i = indexFor(e.hash, newCap);
            e.next = newTable[i];            // 线程 2 已把 B 设为 newTable[i]
            newTable[i] = e;                 // A.next=B, B.next=A → 成环！
            e = next;
        }
    }
}
```

JDK 8 改用**尾插法**+高位迁移，不再反转链表，但**多线程并发 put 仍不安全**（数据丢失 + size 不准）。

---

## 三、4 大解决方案对比

| 方案 | 性能 | 线程安全级别 | 适用场景 | 备注 |
|------|------|-------------|---------|------|
| **ConcurrentHashMap** | ⭐⭐⭐⭐⭐ | 强安全 | 高并发读写 | **推荐**，CAS+synchronized 细粒度锁 |
| Collections.synchronizedMap | ⭐⭐⭐ | 强安全 | 低并发简单场景 | 全局 synchronized 大锁，读也阻塞 |
| Hashtable | ⭐ | 强安全 | 遗留系统 | 所有方法 synchronized，**已过时** |
| 外部加锁 | ⭐⭐⭐ | 取决于锁粒度 | 特殊业务逻辑 | `ReentrantLock` + HashMap，灵活但易出错 |

```java
// ✅ 推荐：ConcurrentHashMap
Map<String, Integer> safeMap = new ConcurrentHashMap<>();

// 可用但不推荐：synchronizedMap
Map<String, Integer> syncMap = Collections.synchronizedMap(new HashMap<>());

// ❌ 不要用了：Hashtable（所有方法 synchronized，性能极差）
Map<String, Integer> ht = new Hashtable<>();
```

---

## 四、ConcurrentHashMap 为什么线程安全？

### JDK 7：分段锁（Segment）

```text
ConcurrentHashMap
├── Segment[0] (ReentrantLock) → HashEntry[]
├── Segment[1] (ReentrantLock) → HashEntry[]
└── ... → Segment[15]
```

16 把锁保护 16 个段，同一段内串行，不同段可并行。最大并发度 = Segment 数量。

### JDK 8：CAS + synchronized 桶级锁

```text
put 流程：
1. 桶为空 → CAS 直接插入（无锁路径，最快）
2. 桶有元素 → synchronized 锁住头节点
3. 遇到 ForwardingNode → 协助迁移
4. size 统计 → baseCount + CounterCell 数组分散竞争
```

**核心差异**：JDK 7 一把锁保护一片桶，JDK 8 一把锁保护一个桶——理论并发度 = 桶数量。

---

## 五、面试话术（30 秒版）

> "HashMap 线程不安全有 3 个层面：**数据丢失**——put 是 check-then-act 非原子，多线程同时写到同一空桶会覆盖；**死循环**——JDK 7 头插法扩容反转链表，并发下指针成环导致 CPU 100%，JDK 8 改为尾插法修复了死循环但仍不安全；**size 不准**——++size 不是原子操作，read-modify-write 会丢失计数。
>
> 解决方案首推 **ConcurrentHashMap**：JDK 7 用分段锁（Segment），JDK 8 用 CAS + synchronized 细化到桶级，读操作无锁，写操作只锁头节点，size 用 CounterCell 分散竞争。Hashtable 和 synchronizedMap 都是全局大锁，性能差，不推荐。"

---

## 六、交叉引用

- [HashMap 扩容机制](../hashmap-resizing/) — 扩容原理 + Java 8 高位迁移算法
- [ConcurrentHashMap 原理](../concurrent-hashmap/) — JDK 7 分段锁 vs JDK 8 CAS+synchronized
- 主模块：[`HashMap 原理`](../../../01.java-and-jvm/collection/hashmap.md) — HashMap 核心数据结构

## 相关章节

- 深度阅读：[`01.java-and-jvm`](../../../01.java-and-jvm/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · hashmap-thread-unsafe](../README.md)
