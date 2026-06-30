# WeakHashMap 学习笔记

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

WeakHashMap 学习笔记 本应该很简单，---

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、弱引用原理与 GC 行为

### 1.1 Java 中的四种引用类型

Java 的 `java.lang.ref` 包提供了四种引用类型，按强度从高到低排列：

```
强引用 (StrongReference)   >  软引用 (SoftReference)  >  弱引用 (WeakReference)  >  虚引用 (PhantomReference)
永不回收                OOM前回收          GC即回收(可达时)        仅用于追踪回收通知
```

| 引用类型 | 回收时机 | 典型用途 |
|---------|---------|---------|
| `StrongReference` | 永远不会被 GC 回收（除非不可达） | 普通对象引用 |
| `SoftReference` | 内存不足 OOM 之前回收 | 高速缓存（LRU 的替代方案） |
| `WeakReference` | 只要 GC 扫描到就会回收 | `WeakHashMap`、临时映射 |
| `PhantomReference` | 对象被回收后进入 ReferenceQueue | 精确追踪对象生命周期 |

### 1.2 弱引用的回收规则

当 GC 进行可达性分析时：

```
GC Roots
  │
  ├── 强引用链 ────────────► 对象存活 (强可达)
  │
  └── 仅有弱引用链 ────────► 对象标记为可回收 (弱可达)
```

```java
// 弱引用创建与回收演示
WeakReference<Object> weakRef = new WeakReference<>(new Object());

// 此时 weakRef.get() 返回实际对象引用
System.out.println(weakRef.get()); // java.lang.Object@xxx

// 触发 GC（注意：System.gc() 只是建议，不保证立即执行）
System.gc();
Thread.sleep(100);

// GC 后弱引用指向的对象被回收
System.out.println(weakRef.get()); // null
```

**核心要点**：弱引用对象本身仍然"存在"，但它指向的目标对象会被 GC 回收，之后 `get()` 返回 `null`。

---

## 二、WeakHashMap 的底层实现

### 2.1 类声明与 Entry 结构

`WeakHashMap` 的 `Entry` 继承自 `WeakReference`，这是其核心设计：

```java
// java.util.WeakHashMap 内部类（简化版）
private static class Entry<K, V> extends WeakReference<Object> implements Map.Entry<K, V> {
    V value;
    final int hash;
    Entry<K, V> next;

    Entry(Object key, V value, ReferenceQueue<Object> queue,
          int hash, Entry<K, V> next) {
        // 将 key 包装为弱引用，传入 queue 用于通知
        super(key, queue);
        this.value = value;
        this.hash = hash;
        this.next = next;
    }
}
```

**关键设计**：
- `key` 被包装为 `WeakReference` —— key 的回收不受 `WeakHashMap` 本身影响
- `value` 是强引用 —— 只要 Entry 存在，value 就不会被回收
- 每个 Entry 注册到了 `ReferenceQueue` —— 当 key 被 GC 回收后，Entry 会被放入队列

### 2.2 数据结构布局

```
WeakHashMap 内部结构
══════════════════════════════════════════════════════

  table[] (Entry 数组)
    │
    ├── [0] null
    │
    ├── [1] ──► Entry(key=WeakRef("name"), value="Bob", hash=xxx)
    │              │
    │              │ WeakReference.get() ──► "name" (字符串对象)
    │              │
    │              └── 注册到 ReferenceQueue ◄── 所有 Entry 共享
    │
    ├── [2] null
    │
    └── [3] ──► Entry(key=WeakRef(obj), value=data, hash=xxx)
                    │
                    └── next ──► Entry(key=WeakRef(obj2), value=data2)
                                     │
                                     └── (链表，处理哈希冲突)

  ReferenceQueue
    │
    └── 当 key 被 GC 回收后，对应的 Entry 被排入此队列
        └── expungeStaleEntries() 从队列取出并删除
```

### 2.3 构造函数

```java
public WeakHashMap() {
    this(DEFAULT_INITIAL_CAPACITY, 0.75f);
}

public WeakHashMap(int initialCapacity, float loadFactor) {
    if (initialCapacity < 0)
        throw new IllegalArgumentException("Illegal Initial Capacity");
    if (loadFactor <= 0 || Float.isNaN(loadFactor))
        throw new IllegalArgumentException("Illegal Load Factor");
    this.loadFactor = loadFactor;
    threshold = initialCapacity;
    table = newTable(initialCapacity);
}
```

构造逻辑与 `HashMap` 一致，唯一的区别是内部使用的 `ReferenceQueue`：

```java
private final ReferenceQueue<Object> queue = new ReferenceQueue<>();
```

---

## 三、expungeStaleEntries() 清理机制

### 3.1 清理原理

这是 `WeakHashMap` 最核心的机制。当 key 被 GC 回收后，对应的 `WeakReference` 会被加入 `ReferenceQueue`。`expungeStaleEntries()` 方法负责从队列中取出这些"过期"的 Entry 并将其从 Map 中移除。

```java
private void expungeStaleEntries() {
    // 循环从队列中取出所有已过期的 Entry
    for (Object x; (x = queue.poll()) != null; ) {
        // 同步块保证线程安全（虽然 WeakHashMap 本身不是线程安全的）
        synchronized (queue) {
            @SuppressWarnings("unchecked")
                Entry<K,V> e = (Entry<K,V>) x;

            // 计算该 Entry 在 table 中的索引
            int i = indexFor(e.hash, table.length);

            // 从链表中摘除该 Entry
            Entry<K,V> prev = table[i];
            Entry<K,V> p = prev;
            while (p != null) {
                Entry<K,V> next = p.next;
                if (p == e) {
                    // 找到目标 Entry，从链表中移除
                    if (prev == e)
                        table[i] = next;   // 头节点直接替换
                    else
                        prev.next = next;   // 中间节点跳过

                    // 帮助 GC：断开引用
                    e.next = null;
                    e.value = null;
                    size--;
                    break;
                }
                prev = p;
                p = next;
            }
        }
    }
}
```

### 3.2 调用时机

`expungeStaleEntries()` **不是**由独立线程或定时器调用的，而是**惰性触发**的 —— 在几乎所有读写操作之前都会调用：

```
put() ──────────────────────► expungeStaleEntries() → 写入新 Entry
get() ──────────────────────► expungeStaleEntries() → 返回 value
remove() ───────────────────► expungeStaleEntries() → 删除指定 Entry
containsKey() ──────────────► expungeStaleEntries() → 检查是否存在
size() ─────────────────────► expungeStaleEntries() → 返回 size
isEmpty() ──────────────────► expungeStaleEntries() → 判空
keySet() / values() / entrySet() ──► expungeStaleEntries() → 返回视图
```

**惰性清理的优势**：不需要额外的 GC 线程，不会浪费 CPU 资源。

**惰性清理的劣势**：如果 Map 长时间不被访问，过期 Entry 会滞留，占用内存。

### 3.3 清理过程时序图

```
时间线
═════════════════════════════════════════════════════════════

T1:  map.put(key, value)
     └── Entry 存入 table，key 被包装为 WeakReference

T2:  外部将 key = null（失去强引用）
     └── 此时 key 变为弱可达状态

T3:  GC 运行
     └── 发现 key 仅被 WeakReference 引用，回收 key 对象
     └── 将 WeakReference (即 Entry) 排入 ReferenceQueue

T4:  map.get(anotherKey)   ← 触发了 expungeStaleEntries()
     └── 从 queue.poll() 拿到过期 Entry
     └── 从 table 链表中摘除 Entry
     └── size--
     └── 继续执行 get 逻辑
```

---

## 四、与 HashMap 的对比

### 4.1 核心差异对比表

| 维度 | HashMap | WeakHashMap |
|-----|---------|-------------|
| key 引用类型 | 强引用 | 弱引用（`WeakReference`） |
| key 被回收后 | key 不会被回收 | key 可被 GC 回收，Entry 自动清理 |
| 生命周期管理 | 手动 remove | 自动清理（惰性触发） |
| 线程安全 | 否 | 否 |
| 允许 null key | 是 | 是（null key 不会被自动清理） |
| 适用场景 | 常规键值对存储 | 缓存、元数据附加、监听器注册表 |
| 内部 Entry | 普通对象 | 继承 `WeakReference` |
| 额外开销 | 无 | `ReferenceQueue` 维护 + 惰性清理开销 |

### 4.2 行为差异演示

```java
// HashMap: 强引用，key 不会被回收
HashMap<String, String> hashMap = new HashMap<>();
String key = "test";
hashMap.put(key, "value");
key = null; // 只是局部变量不再引用，但 HashMap 内部仍持有强引用
System.gc();
System.out.println(hashMap.containsKey("test")); // true —— key 仍然存在

// WeakHashMap: 弱引用，key 可被回收
WeakHashMap<String, String> weakMap = new WeakHashMap<>();
String key2 = "test";
weakMap.put(key2, "value");
key2 = null; // 外部失去强引用
System.gc();
Thread.sleep(100);
System.out.println(weakMap.containsKey("test")); // false —— Entry 已被清理
```

### 4.3 关于 null key 的特殊处理

```java
// null key 不会被包装为 WeakReference
// 因为 WeakReference 的构造函数不允许 null 作为 referent
public V put(K key, V value) {
    Object k = maskNull(key);  // key == null 时替换为静态 Object NULL_KEY
    ...
}

private static final Object NULL_KEY = new Object();

static Object maskNull(Object key) {
    return (key == null) ? NULL_KEY : key;
}

static Object unmaskNull(Object key) {
    return (key == NULL_KEY) ? null : key;
}
```

`null` key 使用一个内部静态对象 `NULL_KEY` 代替，因此 **null key 不会被 GC 回收**。

### 4.4 性能对比

```
操作               HashMap           WeakHashMap
─────────────────────────────────────────────────
put()              O(1)              O(1) + expungeStaleEntries() 开销
get()              O(1)              O(1) + expungeStaleEntries() 开销
remove()           O(1)              O(1) + expungeStaleEntries() 开销
size()             O(1)              O(n) + expungeStaleEntries() 清理
内存占用           较小              较大（每个 Entry 额外持有一个 WeakReference 对象）
GC 压力            无                有（ReferenceQueue 处理 + 额外对象创建）
```

---

## 五、典型应用场景

### 5.1 场景一：本地缓存

当缓存的 key 是大对象或外部不再需要时，自动释放内存：

```java
public class ImageCache {
    // 使用 WeakHashMap 作为缓存，当外部不再持有图片引用时自动回收
    private final Map<String, BufferedImage> cache = new WeakHashMap<>();

    public BufferedImage getImage(String path, Supplier<BufferedImage> loader) {
        // 注意：这里 value 是强引用，所以如果仅用 WeakHashMap，
        // value 不会被回收 —— 需要配合 WeakReference 包裹 value
        return cache.computeIfAbsent(path, k -> loader.get());
    }
}
```

**注意**：`WeakHashMap` 只弱引用 key，value 是强引用。如果需要 value 也能被回收，应使用：

```java
// 正确姿势：key 和 value 都可回收
Map<String, WeakReference<BufferedImage>> cache = new WeakHashMap<>();

public BufferedImage getImage(String path, Supplier<BufferedImage> loader) {
    WeakReference<BufferedImage> ref = cache.get(path);
    if (ref != null) {
        BufferedImage img = ref.get();
        if (img != null) return img; // 缓存命中
    }
    // 缓存未命中或已被回收，重新加载
    BufferedImage img = loader.get();
    cache.put(path, new WeakReference<>(img));
    return img;
}
```

### 5.2 场景二：附加元数据（不修改原对象）

```java
public class MetadataRegistry {
    // 将元数据附加到任意对象上，不修改原类
    // 当对象被 GC 回收时，元数据自动清除
    private final WeakHashMap<Object, Map<String, Object>> metadata = new WeakHashMap<>();

    // 为对象设置元数据
    public void setMeta(Object obj, String key, Object value) {
        metadata.computeIfAbsent(obj, k -> new HashMap<>()).put(key, value);
    }

    // 获取元数据
    public Object getMeta(Object obj, String key) {
        Map<String, Object> map = metadata.get(obj);
        return map == null ? null : map.get(key);
    }
}
```

**典型用法**：
- 为第三方库的对象附加标签
- ORM 框架中为实体对象附加持久化状态
- AOP 代理中存储拦截器信息

### 5.3 场景三：监听器注册表

```java
public class EventBus {
    // 监听器注册表 —— 当监听器对象被外部丢弃时自动注销
    private final WeakHashMap<Object, List<Consumer<Event>>> listeners = new WeakHashMap<>();

    public void register(Object listener, Consumer<Event> handler) {
        listeners.computeIfAbsent(listener, k -> new ArrayList<>()).add(handler);
    }

    public void fire(Event event) {
        // 遍历时自动清理已失效的监听器
        listeners.forEach((key, handlers) ->
            handlers.forEach(h -> h.accept(event)));
    }
}
```

### 5.4 场景四：ThreadLocal 的替代方案

```java
// 传统 ThreadLocal —— 需要手动 remove，否则容易内存泄漏
// ThreadLocal<String> threadLocal = new ThreadLocal<>();

// WeakHashMap 方案 —— key 是 Thread 对象，Thread 结束后自动清理
WeakHashMap<Thread, Object> threadData = new WeakHashMap<>();

void setThreadData(Object data) {
    threadData.put(Thread.currentThread(), data);
}

Object getThreadData() {
    return threadData.get(Thread.currentThread());
}
```

---

## 六、使用注意事项和陷阱

### 6.1 陷阱一：String 常量池导致 key 不被回收

```java
WeakHashMap<String, String> map = new WeakHashMap<>();

// 字符串字面量存放在常量池，是强可达的
map.put("hello", "world");
// 即使不再使用 "hello"，字符串常量池仍持有引用
// —— key 永远不会被 GC 回收！
System.gc();
System.out.println(map.size()); // 仍然是 1

// 正确做法：使用 new String() 创建非常量字符串
String key = new String("hello");
map.put(key, "world");
key = null; // 失去强引用
System.gc();
System.out.println(map.size()); // 0 —— Entry 被清理
```

**根本原因**：字符串常量池是 GC Root 的强引用链，所以字符串字面量永远不会被回收。

### 6.2 陷阱二：value 是强引用

```java
WeakHashMap<Object, BigObject> map = new WeakHashMap<>();
BigObject big = new BigObject();
map.put(new Object(), big);
// 当 key 被回收后，Entry 被清理，value 的强引用才被断开
// 但在清理之前，value 始终不会被 GC 回收
```

**解决方案**：value 也用 `WeakReference` 包裹（参见 5.1 节）。

### 6.3 陷阱三：不是线程安全的

```java
WeakHashMap<String, String> map = new WeakHashMap<>();

// 多线程并发读写会抛出 ConcurrentModificationException
// 或出现数据不一致

// 解决方案一：Collections.synchronizedMap
Map<String, String> syncMap = Collections.synchronizedMap(new WeakHashMap<>());

// 解决方案二：ConcurrentHashMap + WeakReference value（推荐）
// 注意：ConcurrentHashMap 不支持 key 为弱引用
ConcurrentHashMap<String, WeakReference<String>> concurrentCache = new ConcurrentHashMap<>();
```

### 6.4 陷阱四：null key 不会被清理

```java
WeakHashMap<String, String> map = new WeakHashMap<>();
map.put(null, "null-value");
// null key 内部替换为 NULL_KEY 静态对象
// NULL_KEY 永远不被 GC 回收 —— 这个 Entry 永远存在
System.gc();
System.out.println(map.size()); // 仍然是 1
```

### 6.5 陷阱五：迭代器期间的 GC 行为

```java
WeakHashMap<String, String> map = new WeakHashMap<>();
String key = new String("test");
map.put(key, "value");

Iterator<String> it = map.keySet().iterator();
key = null;    // 失去强引用
System.gc();    // 触发 GC

// 此时调用 iterator.next() 会触发 expungeStaleEntries()
// 导致 ConcurrentModificationException（因为迭代器创建后结构被修改）
it.next(); // 可能抛出异常
```

### 6.6 陷阱六：equals/hashCode 与弱引用的交互

```java
class MutableKey {
    private String name;

    MutableKey(String name) { this.name = name; }

    public void setName(String name) { this.name = name; }

    @Override
    public int hashCode() { return name.hashCode(); }

    @Override
    public boolean equals(Object o) {
        if (!(o instanceof MutableKey)) return false;
        return name.equals(((MutableKey) o).name);
    }
}

WeakHashMap<MutableKey, String> map = new WeakHashMap<>();
MutableKey key = new MutableKey("abc");
map.put(key, "value");

key.setName("xyz"); // 修改了 key 的 hashCode
map.get(key); // 找不到 —— 因为 hashCode 变了
```

**规则**：作为 `WeakHashMap` 的 key 的对象，在放入 Map 后不应修改其 `hashCode()` 和 `equals()` 依赖的字段。

---

## 七、与 ReferenceQueue 的关系

### 7.1 ReferenceQueue 的作用

`ReferenceQueue` 是 `java.lang.ref` 包中的核心组件，用于在引用对象被 GC 回收时通知注册者。

```
GC 发现对象仅被 WeakReference 引用
        │
        ▼
  回收目标对象
        │
        ▼
  将 WeakReference 本身排入 ReferenceQueue
        │
        ▼
  WeakHashMap 从 queue.poll() 取出过期引用
        │
        ▼
  从 table 中移除对应的 Entry
```

### 7.2 ReferenceQueue 的三种操作

```java
ReferenceQueue<Object> queue = new ReferenceQueue<>();
WeakReference<Object> ref = new WeakReference<>(new Object(), queue);

// 1. poll() —— 非阻塞，立即返回队列头部的引用，队列为空则返回 null
Reference<?> polled = queue.poll();

// 2. remove() —— 阻塞，直到有引用入队
Reference<?> removed = queue.remove();

// 3. remove(timeout) —— 阻塞指定时间，超时返回 null
Reference<?> removedWithTimeout = queue.remove(1000);
```

`WeakHashMap` 使用的是 `poll()` —— 非阻塞，只在访问 Map 时顺便清理。

### 7.3 完整的生命周期

```
┌─────────────────────────────────────────────────────────────┐
│                    WeakHashMap + ReferenceQueue 生命周期      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. put(key, value)                                         │
│     └── 创建 Entry(key, value, queue, hash, next)           │
│     └── Entry 继承 WeakReference，将 key 作为 referent       │
│     └── 注册到 ReferenceQueue                                │
│                                                             │
│  2. 外部失去 key 的强引用                                    │
│     └── key 变为弱可达                                       │
│                                                             │
│  3. GC 运行                                                  │
│     └── 回收 key 对象                                       │
│     └── 将 Entry (WeakReference) 排入 queue                  │
│                                                             │
│  4. 下次访问 Map (get/put/size/...)                          │
│     └── expungeStaleEntries() 被调用                         │
│     └── queue.poll() 取出过期 Entry                          │
│     └── 从 table 链表中摘除 Entry                             │
│     └── size--                                              │
│     └── value = null (帮助 GC 回收 value)                    │
│                                                             │
│  5. value 如果没有其他强引用，下次 GC 时被回收                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.4 ReferenceQueue 与 PhantomReference 的对比

```java
// WeakReference：referent 被回收后立即入队
WeakReference<Object> weakRef = new WeakReference<>(obj, queue);
// 可以在 get() 返回 null 之前知道对象即将被回收

// PhantomReference：referent 被回收后入队，但 get() 永远返回 null
PhantomReference<Object> phantomRef = new PhantomReference<>(obj, queue);
// 用途：精确知道对象何时被 GC 回收，用于清理堆外内存等场景
```

---

## 八、最佳实践

### 8.1 缓存场景推荐方案

```java
// 方案一：简单场景，直接用 WeakHashMap
Map<KeyType, ValueType> cache = new WeakHashMap<>();

// 方案二：value 也可回收（推荐）
Map<KeyType, WeakReference<ValueType>> cache = new WeakHashMap<>();

// 方案三：高并发场景
ConcurrentHashMap<KeyType, WeakReference<ValueType>> concurrentCache = new ConcurrentHashMap<>();

// 方案四：Guava Cache / Caffeine（生产环境首选）
// 这些库提供了更完善的自动过期机制
Cache<KeyType, ValueType> guavaCache = CacheBuilder.newBuilder()
    .weakKeys()
    .weakValues()
    .build();
```

### 8.2 元数据附加推荐方案

```java
// 方式一：WeakHashMap（适合单线程或同步场景）
class MetaStore {
    private final WeakHashMap<Object, Map<String, String>> meta = new WeakHashMap<>();

    public synchronized void put(Object obj, String k, String v) {
        meta.computeIfAbsent(obj, x -> new HashMap<>()).put(k, v);
    }
}

// 方式二：IdentityHashMap + WeakHashMap（需要精确的 identity 比较）
// 因为 WeakHashMap 默认用 equals/hashCode，如果对象重写了这些方法可能会影响查找
```

### 8.3 避免使用的场景

| 场景 | 原因 | 替代方案 |
|-----|------|---------|
| 持久化存储 | key 可能被 GC 回收导致数据丢失 | `HashMap` / 数据库 |
| 需要精确 size() 的统计 | 惰性清理导致 size 可能不准确 | `HashMap` |
| 高并发读写 | 不是线程安全的 | `ConcurrentHashMap` + `WeakReference` value |
| 字符串常量作为 key | 常量池持有强引用，自动清理失效 | 用 `new String()` 包装 |
| 可变对象作为 key | hashCode 变化导致查找失败 | 使用不可变对象 |

### 8.4 生产环境排查技巧

```java
// 监控 WeakHashMap 中的过期 Entry 数量
public class MonitoredWeakHashMap<K, V> extends WeakHashMap<K, V> {
    private int lastSize = 0;

    @Override
    public V put(K key, V value) {
        V result = super.put(key, value);
        checkStaleEntries();
        return result;
    }

    private void checkStaleEntries() {
        if (lastSize != size()) {
            System.out.println("清理了 " + (lastSize - size()) + " 个过期 Entry");
            lastSize = size();
        }
    }
}
```

---

## 九、源码关键方法速查

```java
// WeakHashMap 核心方法列表（JDK 8）

private ReferenceQueue<Object> queue;   // 过期引用队列

private void expungeStaleEntries()      // 清理过期 Entry（惰性触发）

public V put(K key, V value)            // 存入键值对
public V get(Object key)                // 获取值
public V remove(Object key)             // 移除键值对
public boolean containsKey(Object key)  // 检查是否包含 key
public int size()                       // 返回键值对数量
public boolean isEmpty()                // 是否为空

public Set<K> keySet()                  // 返回 key 视图
public Collection<V> values()           // 返回 value 视图
public Set<Map.Entry<K,V>> entrySet()   // 返回 Entry 视图
```

---

*本笔记基于 JDK 8+ 的 `java.util.WeakHashMap` 源码编写*
