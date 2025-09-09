# WeakHashMap

**WeakHashMap 是 Java 中一种基于弱引用键的特殊 Map 实现，其核心特性是当键不再被外部强引用时，垃圾回收器（GC）可自动回收该键，并同步移除对应的键值对，从而有效防止内存泄漏。** 以下是其关键特性、实现原理、典型应用场景及注意事项的详细分析：

## 一、核心特性
1. **弱引用键（Weak Reference Keys）**
    - WeakHashMap 的键被包装在 `WeakReference` 中，当外部代码不再持有该键的强引用时，GC 会在下次运行时将其标记为可回收对象。
    - **示例**：若将对象 `obj` 作为键存入 WeakHashMap 后，将外部引用 `obj = null`，则 GC 可能回收 `obj`，并触发 WeakHashMap 自动移除该键值对。

2. **自动清理机制**
    - WeakHashMap 内部维护一个 `ReferenceQueue`，用于检测被 GC 回收的键。在调用 `get()`、`put()`、`size()` 等方法时，会主动清理队列中的失效条目。
    - **关键点**：清理时机依赖 GC 执行和后续的 WeakHashMap 操作，因此无法保证即时性。

3. **支持 `null` 键和 `null` 值**
    - 与 HashMap 类似，WeakHashMap 允许键和值为 `null`，但需注意多线程环境下的同步问题。

4. **遍历顺序不确定**
    - 由于弱引用的存在，遍历过程中键可能被 GC 回收，导致遍历结果不稳定。

## 二、实现原理
1. **Entry 结构**
    - WeakHashMap 的 `Entry` 类继承自 `WeakReference<K>`，并额外存储值（`V value`）和哈希值（`final int hash`）：
      ```java
      private static class Entry<K,V> extends WeakReference<K> implements Map.Entry<K,V> {
          V value;
          final int hash;
          Entry<K,V> next; // 用于处理哈希冲突的链表
      }
      ```

2. **GC 通知机制**
    - 通过 `ReferenceQueue<K>` 监听被回收的键。当键被 GC 回收时，对应的 `Entry` 会被放入队列，后续操作中清理这些失效条目。

3. **清理逻辑**
    - 在 `expungeStaleEntries()` 方法中，遍历队列并移除失效的 `Entry`：
      ```java
      private void expungeStaleEntries() {
          for (Object x; (x = queue.poll()) != null; ) {
              synchronized (queue) {
                  Entry<K,V> e = (Entry<K,V>) x;
                  int i = indexFor(e.hash, table.length);
                  // 从哈希桶中移除 e
              }
          }
      }
      ```

## 三、典型应用场景
1. **内存敏感的缓存**
    - **场景**：缓存耗时计算的结果（如元数据、配置对象），当缓存对象不再被外部使用时，自动释放内存。
    - **示例**：
      ```java
      WeakHashMap<ExpensiveObject, Metadata> cache = new WeakHashMap<>();
      Metadata meta = cache.get(obj);
      if (meta == null) {
          meta = computeMetadata(obj); // 耗时计算
          cache.put(obj, meta);
      }
      ```

2. **事件监听器管理**
    - **场景**：防止监听器因被 Map 强引用而无法被 GC 回收，避免内存泄漏。
    - **示例**：
      ```java
      WeakHashMap<EventListener, EventConfig> listeners = new WeakHashMap<>();
      listeners.put(listener, config); // 当 listener 不再被使用时，自动移除
      ```

3. **对象元数据存储**
    - **场景**：为对象附加元数据（如 AOP、序列化信息），当对象被回收时，元数据自动清理。
    - **示例**：
      ```java
      WeakHashMap<Object, MyMetadata> metadataMap = new WeakHashMap<>();
      metadataMap.put(obj, new MyMetadata()); // 当 obj 被回收时，元数据同步移除
      ```

## 四、注意事项
1. **非线程安全**
    - WeakHashMap 不是线程安全的，多线程环境下需通过 `Collections.synchronizedMap()` 包装或使用 `ConcurrentHashMap` 结合弱引用。

2. **清理时机不可控**
    - 依赖 GC 执行和后续的 WeakHashMap 操作，无法保证键值对立即被移除。若需强制清理，可调用 `System.gc()`（不推荐生产环境使用）。

3. **不适合存储关键数据**
    - 由于键可能被意外回收，WeakHashMap 不适用于需要持久存储的场景（如数据库连接池）。

4. **性能开销**
    - 弱引用和 `ReferenceQueue` 的维护会带来额外开销，需权衡内存占用与性能。

## 五、WeakHashMap vs HashMap
| **特性**     | **WeakHashMap** | **HashMap**   |
|------------|-----------------|---------------|
| **键引用类型**  | 弱引用（可被 GC 回收）   | 强引用（阻止 GC 回收） |
| **内存泄漏风险** | 低（自动清理）         | 高（需手动清理）      |
| **线程安全**   | 非线程安全           | 非线程安全         |
| **适用场景**   | 缓存、元数据存储、监听器管理  | 通用键值存储        |

## 六、总结
WeakHashMap 通过弱引用键和自动清理机制，为内存敏感的场景提供了高效的解决方案。其核心优势在于**自动释放不再使用的资源**，但需注意线程安全、清理时机和性能开销。在缓存、监听器管理等场景中，WeakHashMap 能显著降低内存泄漏风险，是 Java 集合框架中一个极具实用价值的工具。