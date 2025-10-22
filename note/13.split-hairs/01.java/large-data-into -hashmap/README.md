# 快速安全地往HashMap里插入大量条数据

## 1. 预设初始容量和负载因子

为了避免频繁的扩容操作，应在创建 `HashMap` 时预设合适的初始容量：

```java
// 假设预计插入 N 条数据
int expectedSize = 1000000;
float loadFactor = 0.75f; // 默认负载因子
int initialCapacity = (int) (expectedSize / loadFactor) + 1;

Map<K, V> map = new HashMap<>(initialCapacity, loadFactor);
```


这样可以避免在插入过程中触发多次 `resize()` 操作。

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


## 4. 内存管理注意事项

虽然题目说明内存无限，但仍需注意以下几点：

- 监控JVM堆内存使用情况，避免OutOfMemoryError
- 考虑使用SoftReference或WeakReference存储大数据值
- 对于非常大的数据集，可考虑使用数据库或分布式缓存替代纯内存方案

## 5. 推荐的最佳实践组合

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