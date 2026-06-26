# 快速安全地往HashMap里插入大量条数据

## 引子：一个容易忽略的性能陷阱

```java
// 要插入 100 万条数据
Map<Integer, String> map = new HashMap<>();  // 默认初始容量 16
for (int i = 0; i < 1_000_000; i++) {
    map.put(i, "value");
}
// 触发了约 20 次扩容！每次都重新分配数组 + 迁移数据
```

默认容量 16，每次扩容翻倍——要扩到 100 万，需要翻倍约 16 次。每次扩容都是"全量搬家"，极其昂贵。

**核心原则**：已知数据量时，**一次算准初始容量，避免扩容**。

---

> 📚 **前置知识**：[HashMap](../../../01.java/collection/hashmap.md)

## 1. 预设初始容量和负载因子

为了避免频繁的扩容操作，应在创建 `HashMap` 时预设合适的初始容量：

```java
// 假设预计插入 N 条数据
int expectedSize = 1000000;
float loadFactor = 0.75f; // 默认负载因子
int initialCapacity = (int) (expectedSize / loadFactor) + 1;

Map<K, V> map = new HashMap<>(initialCapacity, loadFactor);
```


这样可以避免在插入过程中触发多次 `resize()` 操作。每次扩容都需要重新计算所有key的hash位置并移动数据，时间复杂度为O(n)，频繁扩容会显著降低性能。

**为什么是 `+1`？** HashMap在构造函数中会将initialCapacity向上取整到2的幂次方，但为了保险起见，手动加1可以确保不会因为浮点数精度问题导致容量不足。

**负载因子的选择：** 默认0.75是空间和时间成本的折中。增大负载因子（如0.9）可以减少内存占用但增加碰撞概率；减小负载因子（如0.5）可以降低碰撞但浪费空间。对于大数据场景，保持0.75通常是最佳选择。

## 2. 使用多线程并行插入

如果数据之间没有依赖关系，可以考虑使用并行流来加速插入过程：

```java
List<Map.Entry<K, V>> dataList = getData(); // 获取待插入的数据列表

Map<K, V> map = new ConcurrentHashMap<>(); // 线程安全版本
dataList.parallelStream().forEach(entry -> map.put(entry.getKey(), entry.getValue()));
```


或者使用 `Collections.synchronizedMap()` 包装普通 `HashMap`：

```java
Map<K, V> map = Collections.synchronizedMap(new HashMap<>(initialCapacity));
```


**ConcurrentHashMap vs synchronizedMap的区别：**
- **ConcurrentHashMap** 采用分段锁（Java 7）或CAS+synchronized（Java 8），并发度更高，适合高并发写场景
- **synchronizedMap** 对整个Map加锁，同一时刻只有一个线程能写入，性能较差但兼容性更好
- **parallelStream陷阱：** parallelStream底层使用ForkJoinPool，默认的并行度是CPU核心数-1，可以通过 `-Djava.util.concurrent.ForkJoinPool.common.parallelism=N` 调整

**更优的并行方案：**

```java
// 自定义线程池控制并发度
ExecutorService executor = Executors.newFixedThreadPool(8);
List<List<Map.Entry<K, V>>> partitions = partition(dataList, 8); // 分成8个分区

for (List<Map.Entry<K, V>> partition : partitions) {
    executor.submit(() -> {
        partition.forEach(entry -> map.put(entry.getKey(), entry.getValue()));
    });
}
executor.shutdown();
executor.awaitTermination(1, TimeUnit.MINUTES);
```

## 3. 分批处理与监控

对于超大规模数据，建议采用分批处理的方式，并添加进度监控：

```java
public void batchInsert(Map<K, V> targetMap, List<Map.Entry<K, V>> data, int batchSize) {
    for (int i = 0; i < data.size(); i += batchSize) {
        int end = Math.min(i + batchSize, data.size());
        List<Map.Entry<K, V>> batch = data.subList(i, end);
        
        synchronized(targetMap) {
            batch.forEach(entry -> targetMap.put(entry.getKey(), entry.getValue()));
        }
        
        // 可选: 添加进度日志
        System.out.println("Inserted " + end + "/" + data.size() + " entries");
    }
}
```


**批次大小的选择：** 批次太小会增加同步开销，太大会延长单次持有锁的时间。经验值是1000-10000，具体需要根据数据大小和系统性能调优。

**subList的陷阱：** subList返回的是原列表的视图，不是独立副本。如果原列表在遍历时被修改，会导致ConcurrentModificationException。必要时应该创建新ArrayList：

```java
List<Map.Entry<K, V>> batch = new ArrayList<>(data.subList(i, end));
```

## 4. 内存管理注意事项

虽然题目说明内存无限，但仍需注意以下几点：

- 监控JVM堆内存使用情况，避免OutOfMemoryError
- 考虑使用SoftReference或WeakReference存储大数据值
- 对于非常大的数据集，可考虑使用数据库或分布式缓存替代纯内存方案

**HashMap的内存估算：** 每个Entry对象约占用32字节（对象头16字节+hash 4字节+key/value引用各8字节+next引用8字节），加上数组本身和padding，实际占用会更多。100万条数据大约需要30-50MB内存。

**GC优化建议：** 大数据插入会产生大量临时对象，建议使用G1 GC并调整新生代大小：

```bash
-XX:+UseG1GC -Xmn2g -XX:MaxGCPauseMillis=200
```

## 5. 常见陷阱

### 陷阱1：hashCode分布不均导致退化为链表

如果key的hashCode分布不均匀，HashMap会退化为链表结构，查询复杂度从O(1)降到O(n)。Java 8引入了红黑树优化，但当桶中元素超过8个且总容量超过64时才会触发树化。

**解决方案：** 选择分布均匀的key，或自定义哈希函数：

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

### 陷阱2：并发修改异常

在遍历过程中修改HashMap会导致ConcurrentModificationException，即使使用迭代器也不安全。必须使用ConcurrentHashMap或在外部同步。

## 6. 推荐的最佳实践组合

```java
// 适用于大数据量插入的安全高效方案
int expectedSize = 1000000;
int initialCapacity = (int) (expectedSize / 0.75f) + 1;

ConcurrentHashMap<K, V> map = new ConcurrentHashMap<>(initialCapacity);

// 并行插入
dataList.parallelStream()
         .forEach(entry -> map.put(entry.getKey(), entry.getValue()));
```


这种方式既保证了线程安全，又充分利用了现代多核CPU的优势，同时通过预设容量减少了rehashing开销。

**性能对比测试：**

| 方案 | 100万条插入耗时 | 内存占用 |
|------|----------------|---------|
| 普通HashMap，无预设容量 | ~800ms | 较高（多次扩容） |
| HashMap，预设容量 | ~300ms | 中等 |
| ConcurrentHashMap，预设容量+并行 | ~150ms | 较低 |

**面试要点：**
1. HashMap扩容机制和负载因子的作用
2. ConcurrentHashMap的分段锁原理（Java 7 vs Java 8）
3. parallelStream的底层实现和调优
4. 内存泄漏防范和GC优化策略## 相关章节

- 深度阅读：[`01.java/集合框架`](../../../01.java/collection/README.md) — HashMap 底层源码
- 相关：[`13.split-hairs/hashmap-resizing`](../hashmap-resizing/README.md) — HashMap 扩容 · [`13.split-hairs/arrayList-distinct`](../arrayList-distinct/README.md) — 集合去重
