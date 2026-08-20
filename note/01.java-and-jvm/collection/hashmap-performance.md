<!--
module:
  parent: java
  slug: java/collection/hashmap-performance
  type: article
  category: 主模块子文章
  summary: HashMap 大数据量插入的性能陷阱 + 初始容量预设 + 并行方案（split-hairs 迁出）
-->

# HashMap 大数据量插入（split-hairs 视角）

> **定位**：HashMap 大数据量插入的性能陷阱 + 初始容量预设 + 并行方案 的核心原理、实现与最佳实践。
>
> 本节由 `12.interview/01.java/large-data-into-hashmap/` 迁出，专注**性能陷阱与并发方案**。HashMap 基础原理见 [hashmap.md](./hashmap.md)。

## 一个容易忽略的性能陷阱

```java
// 要插入 100 万条数据
Map<Integer, String> map = new HashMap<>();  // 默认初始容量 16
for (int i = 0; i < 1_000_000; i++) {
    map.put(i, "value");
}
// 触发了约 20 次扩容！每次都重新分配数组 + 迁移数据
```

**核心原则**：已知数据量时，**一次算准初始容量，避免扩容**。每次扩容都是"全量搬家"，时间复杂度 O(n)，N 次扩容累计代价巨大。

---

## 一、预设初始容量和负载因子（最有效）

```java
int expectedSize = 1_000_000;
float loadFactor = 0.75f;
int initialCapacity = (int) (expectedSize / loadFactor) + 1;  // 公式：N / loadFactor + 1

Map<K, V> map = new HashMap<>(initialCapacity, loadFactor);
```

**为什么 `+1`？** HashMap 构造函数内部会将 `initialCapacity` 向上取整到 2 的幂，但加 1 是为了**防浮点精度误差导致容量不足触发最后一次扩容**——这是一个常被忽视的细节。

**负载因子选择：**

| 场景 | 负载因子 | 理由 |
|------|---------|------|
| 一般场景 | 0.75（默认） | 空间 / 时间成本折中 |
| 内存紧张 / 命中率高优先 | 0.5~0.6 | 减少哈希冲突 |
| 内存充足 / 接受少量冲突 | 0.9 | 节省空间 |

---

## 二、多线程并行插入

```java
// 用 ConcurrentHashMap 并行安全插入
ConcurrentHashMap<K, V> map = new ConcurrentHashMap<>(initialCapacity);
dataList.parallelStream()
         .forEach(entry -> map.put(entry.getKey(), entry.getValue()));
```

**ConcurrentHashMap vs synchronizedMap 区别：**

| 维度 | ConcurrentHashMap | Collections.synchronizedMap |
|------|-------------------|----------------------------|
| 并发度 | JDK7 分段锁 / JDK8 CAS+synchronized（桶级） | 全表锁（一次只能 1 个写） |
| 性能 | 高 | 低 |
| 适用 | 高并发写 | 兼容老代码、简单场景 |

**parallelStream 陷阱：**
- 默认并行度 = CPU 核数 - 1，通过 `-Djava.util.concurrent.ForkJoinPool.common.parallelism=N` 调整
- 共享可变状态未充分同步 → 数据丢失 / 死循环 / 阻塞 IO 风险

---

## 三、推荐最佳实践组合

```java
// 适用于大数据量插入的安全高效方案
int expectedSize = 1_000_000;
int initialCapacity = (int) (expectedSize / 0.75f) + 1;

ConcurrentHashMap<K, V> map = new ConcurrentHashMap<>(initialCapacity);

dataList.parallelStream()
         .forEach(entry -> map.put(entry.getKey(), entry.getValue()));
```

这种组合**同时解决 3 个问题**：预设容量避免扩容 + ConcurrentHashMap 保证线程安全 + parallelStream 利用多核。

---

## 性能对比（实测参考）

| 方案 | 100 万条插入耗时 | 备注 |
|------|----------------|------|
| 普通 HashMap，无预设容量 | ~800ms | 约 20 次扩容开销 |
| HashMap，预设容量 | ~300ms | 减少扩容但单线程 |
| ConcurrentHashMap + 预设容量 + 并行 | ~150ms | 综合最优 |

> 实测数据会因 JVM 版本、CPU 核数、key 类型而异，此处为相对数量级参考。

---

## 30 秒面试话术

> "HashMap 大数据插入的关键是**预设初始容量 = expectedSize / 0.75 + 1**，避免扩容开销。多线程场景用 `ConcurrentHashMap` 配 `parallelStream` 或自定义线程池分片插入。注意 parallelStream 默认用 `ForkJoinPool.commonPool()`，避免在里面做阻塞 IO，否则可能拖垮整个应用的并行任务。"

## 反直觉陷阱

```java
// 陷阱 1：预设容量算错导致最后一次扩容
int initialCapacity = (int) (expectedSize / 0.75f);  // ❌ 少 + 1 可能撞临界值

// 陷阱 2：parallelStream 里做阻塞 IO
dataList.parallelStream().forEach(e -> {
    httpClient.send(...);   // ❌ 拖死 ForkJoinPool.commonPool()
});

// 陷阱 3：subList 的视图陷阱
List<Entry<K, V>> batch = data.subList(i, end);  // ❌ 原 List 修改时抛 CME
// ✅ 正确：new ArrayList<>(data.subList(i, end));
```

## 面试反问（高频追问）

- **Q：为什么用 `(int)(N/0.75) + 1` 而不是 `N * 1.34`？** A：`+1` 是保险，防止浮点精度问题导致扩容阈值刚好踩在 `capacity * loadFactor` 时触发最后一次扩容。
- **Q：ConcurrentHashMap 的并发度上限是多少？** A：JDK 7 是 Segment 数（默认 16），JDK 8 是 `Node` 数组大小（理论无上限，受内存约束）。
- **Q：parallelStream 适合什么场景？** A：**纯 CPU 密集 + 数据无共享**的场景。涉及 IO、共享状态、阻塞操作必须用专用线程池。

---

## 相关章节

- [HashMap 源码剖析](./hashmap.md) — 数组 + 链表 + 红黑树、扩容机制
- [集合框架总览](./README.md)
- [split-hairs/hashmap-resizing 扩容原理](../../12.interview/01.java/hashmap-resizing/README.md)

← [返回 集合框架](./README.md)
