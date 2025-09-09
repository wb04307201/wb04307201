# ConcurrentHashMap

**ConcurrentHashMap 是 Java 中专为高并发场景设计的线程安全哈希表实现，位于 `java.util.concurrent` 包，它通过分段锁（或 CAS+synchronized）机制允许多线程并发读写，显著提升了并发性能，同时避免了传统同步容器（如 Hashtable）因全局锁导致的性能瓶颈。**

## 核心特性
1. **线程安全**
    - 继承自 `ConcurrentMap` 接口，所有原子操作（如 `putIfAbsent`、`remove`、`replace`）均保证线程安全。
    - 内部采用分段锁（Segment）或 CAS（Compare-And-Swap）+ synchronized 机制，将数据划分为多个段（默认16段），每个段独立加锁，减少线程竞争。

2. **高并发性能**
    - **读操作**：完全并发，无需加锁（基于 `volatile` 变量和 happens-before 原则保证可见性）。
    - **写操作**：仅锁定目标段，其他段可同时被其他线程访问。
    - **扩容机制**：支持动态扩容，扩容时分段处理，避免全局阻塞。

3. **数据结构**
    - 数组 + 链表 + 红黑树：链表解决哈希冲突，当链表长度超过阈值（默认8）时转换为红黑树，提升查找效率（O(log n)）。

## 与 Hashtable/HashMap 的对比
| **特性**               | **ConcurrentHashMap**               | **Hashtable**                     | **HashMap**                     |
|------------------------|-------------------------------------|-----------------------------------|---------------------------------|
| **线程安全**           | 是（分段锁/CAS+synchronized）        | 是（全局锁 `synchronized`）       | 否（非线程安全）                |
| **并发性能**           | 高（分段锁减少竞争）                 | 低（全局锁导致串行化）           | 高（单线程优化）                |
| **读操作加锁**         | 否（基于 `volatile`）               | 是（全局锁）                     | 否                              |
| **写操作加锁**         | 是（仅目标段）                      | 是（全局锁）                     | 否（需外部同步）                |
| **扩容机制**           | 分段动态扩容                        | 全局阻塞扩容                     | 触发扩容时可能死循环（多线程）  |

## 适用场景
1. **高并发读写**
    - 适合读多写少的场景（如缓存、计数器、会话管理），读操作完全并发，写操作分段加锁。

2. **替代 Hashtable/SynchronizedMap**
    - 在需要线程安全但追求高性能的场景下，优先选择 `ConcurrentHashMap` 而非 `Hashtable` 或 `Collections.synchronizedMap(new HashMap<>())`。

3. **避免死锁与性能瓶颈**
    - 传统同步容器（如 Hashtable）因全局锁导致线程阻塞，而 `ConcurrentHashMap` 通过分段锁或 CAS 机制减少竞争，提升吞吐量。

## 代码示例
```java
import java.util.concurrent.ConcurrentHashMap;

public class ConcurrentHashMapDemo {
    public static void main(String[] args) {
        // 创建 ConcurrentHashMap
        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

        // 并发写入（不同线程可操作不同段）
        map.put("A", 1);
        map.put("B", 2);

        // 并发读取（无需加锁）
        Integer valueA = map.get("A");
        System.out.println("Value of A: " + valueA);

        // 原子操作
        map.putIfAbsent("C", 3); // 仅当键不存在时插入
        map.computeIfAbsent("D", k -> 4); // 键不存在时计算并插入

        // 遍历（弱一致性迭代器，不抛出 ConcurrentModificationException）
        map.forEach((k, v) -> System.out.println(k + ": " + v));
    }
}
```

## 注意事项
1. **size() 的近似性**
    - `size()` 方法返回近似值（因并发修改可能导致计数偏差），需精确值时使用 `mappingCount()`（返回 `long` 类型）。

2. **迭代器弱一致性**
    - 迭代器遍历时若其他线程修改映射，不会抛出 `ConcurrentModificationException`，但可能反映或不反映修改。

3. **避免复合操作**
    - 复合操作（如“检查再操作”）需额外同步，或使用 `ConcurrentMap` 的原子方法（如 `compute`、`merge`）。