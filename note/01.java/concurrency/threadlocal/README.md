<!--
module:
  parent: java
  slug: java/threadlocal
  type: article
  category: 主模块子文章
  summary: ThreadLocal 是 Java 中实现线程封闭性的重要工具，它为每个使用它的线程提供一个独立的变量副本，从而实现线程间的数据隔离。
-->

# ThreadLocal 原理与最佳实践

> ThreadLocal 是 Java 中实现线程封闭性的重要工具，它为每个使用它的线程提供一个独立的变量副本，从而实现线程间的数据隔离。

---
## 引言：反直觉代码

ThreadLocal 原理与最佳实践 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 目录

- [一、ThreadLocal 原理和适用场景](#一threadlocal-原理和适用场景)
- [二、ThreadLocalMap 结构](#二threadlocalmap-结构)
- [三、set/get/remove 流程](#三setgetremove-流程)
- [四、内存泄漏问题](#四内存泄漏问题)
- [五、为什么 key 用弱引用](#五为什么-key-用弱引用)
- [六、InheritableThreadLocal](#六inheritablethreadlocal)
- [七、TransmittableThreadLocal](#七transmittablethreadlocal)
- [八、最佳实践](#八最佳实践)

---

## 一、ThreadLocal 原理和适用场景

### 1.1 核心思想

ThreadLocal 的核心思想是**空间换时间**——通过为每个线程提供一份独立的变量副本，避免了多线程竞争时的同步开销。

```
传统共享变量方式:
  Thread1 ──┐
  Thread2 ──┼──► Shared Variable ──► 需要同步 (synchronized / Lock)
  Thread3 ──┘

ThreadLocal 方式:
  Thread1 ──► ThreadLocal.ThreadLocalMap ──► value1 (独立)
  Thread2 ──► ThreadLocal.ThreadLocalMap ──► value2 (独立)
  Thread3 ──► ThreadLocal.ThreadLocalMap ──► value3 (独立)
  ───────────────────────────────────────────── 无需同步
```

### 1.2 适用场景

| 场景 | 说明 | 典型例子 |
|------|------|----------|
| 线程上下文传递 | 在同一个线程内传递上下文数据 | 用户身份信息、请求 ID |
| 非线程安全对象的线程封闭 | 让每个线程拥有独立实例 | SimpleDateFormat、DateFormat |
| 数据库连接管理 | 每个线程绑定独立的数据库连接 | Hibernate Session、JDBC Connection |
| 事务管理 | 保证同一个线程内的多个操作使用同一个事务 | Spring 的事务传播机制 |
| 链路追踪 | 在调用链中传递 TraceId | MDC (Mapped Diagnostic Context) |

### 1.3 不适用场景

| 场景 | 原因 |
|------|------|
| 线程间通信 | ThreadLocal 是隔离而非共享，不能用于线程间数据传递 |
| 高频创建销毁线程 | 每个 ThreadLocal 实例都需要在 Thread 中维护 Entry，线程频繁创建会增加开销 |
| 大对象存储 | 会导致 ThreadLocalMap 中 value 长期存活，增加内存泄漏风险 |

---

## 二、ThreadLocalMap 结构

### 2.1 整体关系

```
┌─────────────────────────────────────────────────────────┐
│                        Thread                            │
│                                                         │
│  threadLocals: ThreadLocalMap                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │              ThreadLocalMap                        │  │
│  │                                                    │  │
│  │  table: Entry[] (数组，大小为 2 的幂)              │  │
│  │  ┌─────┬───────┬───────┬───────┬───────┐          │  │
│  │  │ [0] │ [1]   │ [2]   │ [3]   │ [4]   │ ...     │  │
│  │  │     │ Entry │       │ Entry │       │          │  │
│  │  └─────┴──┬────┴───────┴──┬────┴───────┘          │  │
│  │           │               │                        │  │
│  │  ┌────────▼──────┐ ┌──────▼────────┐              │  │
│  │  │    Entry      │ │    Entry      │              │  │
│  │  │  key: WeakRef │ │  key: WeakRef │              │  │
│  │  │  value: T     │ │  value: T     │              │  │
│  │  └───────────────┘ └───────────────┘              │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
        ▲
        │ (弱引用指向)
┌───────┴──────────┐
│ ThreadLocal<A>   │
│ ThreadLocal<B>   │
└──────────────────┘
```

### 2.2 核心结构详解

#### Entry 类

```java
// ThreadLocalMap 的静态内部类
static class Entry extends WeakReference<ThreadLocal<?>> {
    /** The value associated with this ThreadLocal. */
    Object value;

    Entry(ThreadLocal<?> k, Object v) {
        super(k);  // key 是弱引用
        value = v;  // value 是强引用
    }
}
```

**关键特征：**

| 属性 | 引用类型 | 说明 |
|------|----------|------|
| key (ThreadLocal) | 弱引用 (WeakReference) | 当没有强引用指向 ThreadLocal 实例时，可被 GC 回收 |
| value | 强引用 | 只要 Entry 存在，value 就不会被回收 |

#### ThreadLocalMap 字段

```java
static class ThreadLocalMap {
    /** 初始容量，必须是 2 的幂 */
    private static final int INITIAL_CAPACITY = 16;

    /** 哈希表，用数组实现 */
    private Entry[] table;

    /** 当前 Entry 数量 */
    private int size = 0;

    /** 扩容阈值，默认容量的 2/3 */
    private int threshold;
}
```

### 2.3 哈希冲突解决：开放定址法（线性探测）

与 HashMap 使用链地址法不同，ThreadLocalMap 使用**开放定址法**解决哈希冲突。

```
假设 hash(ThreadLocalA) % 16 = 2，hash(ThreadLocalB) % 16 = 2 (冲突)

索引:  0    1    2         3         4    5
      ┌────┬────┬─────────┬─────────┬────┬────┐
      │    │    │ Entry A │ Entry B │    │    │
      └────┴────┴─────────┴─────────┴────┴────┘
                            ▲
                     线性探测: 位置 2 被占用,
                     尝试 2+1=3, 位置 3 空闲, 放入 Entry B
```

**开放定址法的优势：**

- 不需要额外的链表节点，内存开销更小
- 缓存友好，连续数组访问
- ThreadLocal 通常数量不多，冲突概率较低

**开放定址法的劣势：**

- 删除操作需要特殊处理（不能简单置 null，否则后面的元素无法查找）
- 连续冲突会导致性能退化

---

## 三、set/get/remove 流程

### 3.1 set 方法流程

```java
public void set(T value) {
    Thread t = Thread.currentThread();
    ThreadLocalMap map = getMap(t);
    if (map != null)
        map.set(this, value);
    else
        createMap(t, value);
}
```

```
set 流程图:
                    ┌──────────────────┐
                    │ 获取当前线程 t    │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ 获取 t.threadLocals│
                    └────────┬─────────┘
                             ▼
                    ┌── threadLocals == null? ──┐
                    │ Yes              No       │
                    ▼                  ▼        │
           ┌─────────────┐    ┌──────────────┐  │
           │ createMap() │    │ map.set()    │  │
           │ 创建新Map   │    │ 计算哈希索引  │  │
           │ 放入初始值  │    │ 查找或插入   │  │
           └─────────────┘    └──────┬───────┘  │
                                     ▼          │
                            ┌──────────────────┐│
                            │ 是否找到已有 key? ││
                            └──┬───────────┬───┘│
                          Yes │           │ No  │
                              ▼           ▼     │
                    ┌─────────────┐ ┌──────────┐│
                    │ 替换 value  │ │ 新建Entry││
                    └─────────────┘ │ 插入     ││
                                    └────┬─────┘│
                                         ▼      │
                                    ┌───────────┐│
                                    │ size >=   ││
                                    │ threshold?││
                                    └──┬────┬───┘│
                                  Yes │    │ No  │
                                      ▼    ▼     │
                                ┌─────────┐ ┌────┐
                                │ rehash()│ │结束│
                                │ clean   │ └────┘
                                │ stale   │
                                │ entries │
                                └─────────┘
```

**set 关键步骤：**

1. 计算哈希索引：`i = key.threadLocalHashCode & (len - 1)`
2. 如果位置 i 为空，直接创建 Entry 放入
3. 如果位置 i 已有元素且 key 相同，替换 value
4. 如果位置 i 已有元素但 key 不同（哈希冲突），线性探测下一个位置
5. 探测过程中如果发现 `key == null`（过期的 Entry），进行**替换过期 Entry**操作
6. 插入完成后检查是否需要扩容

### 3.2 get 方法流程

```java
public T get() {
    Thread t = Thread.currentThread();
    ThreadLocalMap map = getMap(t);
    if (map != null) {
        ThreadLocalMap.Entry e = map.getEntry(this);
        if (e != null) {
            @SuppressWarnings("unchecked")
            T result = (T)e.value;
            return result;
        }
    }
    return setInitialValue();
}
```

```
get 流程图:
                    ┌──────────────────┐
                    │ 获取当前线程 t    │
                    └────────┬─────────┘
                             ▼
                    ┌── map != null? ───┐
                    │ Yes        No     │
                    ▼                    ▼
           ┌──────────────┐    ┌─────────────┐
           │ map.getEntry │    │ setInitial  │
           │ (线性探测查找)│    │ Value()     │
           └──────┬───────┘    └──────┬──────┘
                  ▼                   ▼
         ┌── entry != null? ──┐ ┌──────────┐
         │ Yes         No     │ │ 返回初始 │
         ▼                    ▼ │ 值       │
    ┌──────────┐ ┌────────────┐└──────────┘
    │ 返回     │ │ 返回 null  │
    │ entry.value│ │(实际走    │
    └──────────┘ │ getEntry  │
                 │ 中的逻辑) │
                 └───────────┘
```

**get 关键步骤：**

1. 通过哈希找到数组索引
2. 如果索引处 key 匹配，直接返回
3. 如果不匹配，线性探测直到找到匹配 key 或遇到 null 桶
4. 探测过程中如果发现过期 Entry，进行清理
5. 如果最终未找到，调用 `setInitialValue()` 初始化

### 3.3 remove 方法流程

```java
public void remove() {
    ThreadLocalMap m = getMap(Thread.currentThread());
    if (m != null)
        m.remove(this);
}
```

```
remove 流程图:
                    ┌──────────────────┐
                    │ 获取当前线程的    │
                    │ ThreadLocalMap   │
                    └────────┬─────────┘
                             ▼
                    ┌── map != null? ───┐
                    │                   │
                    ▼                   ▼
           ┌──────────────┐    ┌─────────┐
           │ map.remove   │    │ 结束    │
           │ (查找并删除) │    └─────────┘
           └──────┬───────┘
                  ▼
         ┌──────────────────┐
         │ 找到匹配的 Entry  │
         │ 调用 e.clear()    │
         │ 调用 expungeStale │
         │ Entry 清理并      │
         │ 重新哈希后续元素  │
         └──────────────────┘
```

**remove 关键步骤：**

1. 线性探测找到匹配的 Entry
2. 调用 `e.clear()` 清除弱引用
3. 调用 `expungeStaleEntry()` 清理过期 Entry
4. 由于使用开放定址法，删除后需要**重新哈希**后续被探测过来的元素

### 3.4 三方法对比

| 方法 | 触发时机 | 是否创建 Map | 是否触发扩容 | 是否清理过期 Entry |
|------|----------|-------------|-------------|-------------------|
| set | 主动调用 | 是（首次） | 是 | 是（探测过程中） |
| get | 主动调用 | 是（首次，返回初始值时） | 否 | 是（探测过程中） |
| remove | 主动调用 | 否 | 否 | 是（删除时） |

---

## 四、内存泄漏问题

### 4.1 泄漏根源

ThreadLocalMap 中 Entry 的 key 是弱引用，但 value 是强引用。当 ThreadLocal 实例失去外部强引用后：

```
正常情况 (有外部强引用):
  ┌──────────────┐
  │ ThreadLocal  │──强引用──► (存活)
  └──────┬───────┘
         │ (弱引用)
         ▼
  ┌──────────────┐
  │ Entry(key,v) │──强引用──► value (存活)
  └──────────────┘

ThreadLocal 被 GC 回收后:
  ┌──────────────┐
  │ ThreadLocal  │  (已被 GC 回收!)
  └──────────────┘
         × (弱引用断掉)
         ▼
  ┌──────────────┐
  │ Entry(key=   │──强引用──► value (存活!) ← 泄漏!
  │ null, value) │
  └──────────────┘
  ▲
  │ 只要线程还在运行，
  │ Thread 引用存在 → ThreadLocalMap 存在 →
  → table 数组存在 → value 被强引用 → 无法回收!
```

### 4.2 泄漏场景示例

```java
// 反例: ThreadLocal 用完不 remove
public class LeakExample {
    // 匿名内部类创建，方法执行后失去强引用
    private static final ThreadLocal<byte[]> LOCAL = new ThreadLocal<>();

    public void doWork() {
        LOCAL.set(new byte[1024 * 1024]); // 1MB
        // ... 业务逻辑 ...
        // 忘记调用 LOCAL.remove()!
    }
}
// 每次调用 doWork()，如果线程复用（如线程池），
// ThreadLocalMap 中的 value 会一直累积!
```

### 4.3 为什么在线程池场景下尤其严重

```
线程池场景下的累积效应:

时间线:
  t1: Thread-A 调用 method1() → 设置 value1 (1MB), 未 remove
  t2: Thread-A 调用 method2() → 设置 value2 (2MB), 未 remove
  t3: Thread-A 调用 method3() → 设置 value3 (1MB), 未 remove
  ...
  tn: Thread-A 已泄漏 N MB 内存

  线程不销毁 → ThreadLocalMap 不销毁 → value 不释放 → 内存持续增长
```

### 4.4 JDK 的防御机制

虽然 ThreadLocalMap 无法完全避免内存泄漏，但它在多个位置做了**探测性清理**：

| 方法 | 清理时机 | 清理方式 |
|------|----------|----------|
| set() | 线性探测时遇到 key==null | 替换该位置，清理连续过期 Entry |
| get() | 线性探测时遇到 key==null | 清理该位置及后续连续过期 Entry |
| remove() | 找到并删除目标 Entry 后 | 清理从该位置开始的连续过期 Entry |
| resize() | 扩容时 | 跳过 key==null 的 Entry（不复制到新表） |

**注意：** 这些防御机制是**探测性**的（只清理当前探测路径上的过期 Entry），不是**全量扫描**，所以不能完全替代手动 remove。

---

## 五、为什么 key 用弱引用

### 5.1 如果 key 用强引用

```
key 强引用的情况:
  ┌──────────────┐
  │ ThreadLocal  │──外部强引用 (可被代码置 null)
  └──────┬───────┘
         │ (强引用)
         ▼
  ┌──────────────┐
  │ Entry(key,   │──强引用──► value
  │ value)       │
  └──────────────┘

问题:
  即使外部代码 threadLocal = null;
  ThreadLocal 仍然被 Entry 强引用 → 永远不会被 GC 回收 →
  → 内存泄漏更严重 (key 和 value 都泄漏)
```

### 5.2 使用弱引用的好处

```
key 弱引用的情况:
  ┌──────────────┐
  │ ThreadLocal  │──外部强引用 (可被代码置 null)
  └──────┬───────┘
         │ (弱引用)
         ▼
  ┌──────────────┐
  │ Entry(key,   │──强引用──► value
  │ value)       │
  └──────────────┘

好处:
  当外部 threadLocal = null 后:
  → ThreadLocal 只剩弱引用 → 下次 GC 时被回收
  → Entry 的 key 变为 null
  → ThreadLocalMap 可以检测到过期 Entry (key==null)
  → 在后续的 get/set/remove 中清理 value
  → 虽然不能立即回收 value，但至少给了回收的机会
```

### 5.3 三种引用方式对比

| key 引用方式 | ThreadLocal 置 null 后 | value 能否被回收 | 内存泄漏程度 |
|-------------|----------------------|-----------------|-------------|
| 强引用 | 永远不会被回收 | 不能 | 严重 (key+value 都泄漏) |
| 弱引用 | GC 时回收 key | 不能立即回收，但可在后续操作中被清理 | 较轻 (仅 value 暂时泄漏) |
| 软引用 | GC 时可能回收 | 同弱引用 | 较轻 |

**结论：** 弱引用是在"及时回收"和"可用性"之间的最佳权衡。它允许在外部不再需要 ThreadLocal 时回收 key，同时保留 value 直到下次访问该 ThreadLocalMap 时被清理。

---

## 六、InheritableThreadLocal

### 6.1 问题背景

普通的 ThreadLocal 无法将值传递给子线程：

```java
ThreadLocal<String> tl = new ThreadLocal<>();
tl.set("parent-value");

new Thread(() -> {
    System.out.println(tl.get());  // null! 无法继承父线程的值
}).start();
```

### 6.2 InheritableThreadLocal 原理

```java
public class InheritableThreadLocal<T> extends ThreadLocal<T> {

    // 重写 getMap，使用 Thread 的 inheritableThreadLocals 字段
    ThreadLocalMap getMap(Thread t) {
        return t.inheritableThreadLocals;
    }

    // 重写 createMap
    void createMap(Thread t, T firstValue) {
        t.inheritableThreadLocals = new ThreadLocalMap(this, firstValue);
    }

    // 重写 childValue，子线程继承父线程的值时的处理逻辑
    protected T childValue(T parentValue) {
        return parentValue;  // 默认直接返回父线程的值（浅拷贝）
    }
}
```

### 6.3 值传递时机

```
InheritableThreadLocal 值传递时机:

  ┌──────────────────┐
  │ 父线程 Thread     │
  │ inheritableThreadLocals: {key1=v1, key2=v2} │
  └────────┬─────────┘
           │ new Thread() 创建时
           ▼
  ┌──────────────────┐
  │ Thread.init()    │
  │ 检测父线程的     │
  │ inheritableThreadLocals != null
  │ 调用             │
  │ ThreadLocal.createInheritedMap() │
  └────────┬─────────┘
           ▼
  ┌──────────────────┐
  │ 子线程 Thread     │
  │ inheritableThreadLocals: {key1=v1, key2=v2} │
  │ (拷贝父线程的 Entry) │
  └──────────────────┘

注意: 传递发生在子线程创建时，是一次性拷贝，
      之后父子线程的值各自独立!
```

### 6.4 线程池场景的局限性

```java
// InheritableThreadLocal 在线程池中会出问题:
InheritableThreadLocal<String> itl = new InheritableThreadLocal<>();
itl.set("request-1");

ExecutorService pool = Executors.newFixedThreadPool(2);

// 第一次提交 - 线程创建时拷贝了 "request-1"
pool.submit(() -> System.out.println(itl.get()));  // "request-1"

itl.set("request-2");

// 第二次提交 - 复用已创建的线程，value 还是 "request-1"!
pool.submit(() -> System.out.println(itl.get()));  // "request-1" (不是 "request-2")
```

**问题根源：** 值传递只在 `new Thread()` 时发生一次。线程池复用线程时不会重新传递父线程的最新值。

---

## 七、TransmittableThreadLocal

### 7.1 背景

`TransmittableThreadLocal`（TTL）是阿里巴巴开源的库，解决了 `InheritableThreadLocal` 在线程池场景下的值传递问题。

Maven 依赖：

```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>transmittable-thread-local</artifactId>
    <version>2.14.5</version>
</dependency>
```

### 7.2 核心原理

TTL 通过**装饰器模式**包装 Runnable/Callable/ThreadPoolExecutor，在任务执行时捕获父线程的上下文，并在任务执行前传递到子线程。

```
TTL 工作流程:

主线程 (调用 submit/execute):
  ┌─────────────────────────────────────┐
  │ 1. 捕获 (capture)                   │
  │    获取当前线程所有 TTL 的值快照     │
  │    ↓                                │
  │ 2. 包装 Runnable                    │
  │    将快照封装到新的 Runnable 中      │
  │    ↓                                │
  └─────────────────┬───────────────────┘
                    ▼
线程池工作线程 (执行任务):
  ┌─────────────────────────────────────┐
  │ 3. replay (回放)                    │
  │    将捕获的值设置到当前工作线程      │
  │    保存工作线程之前的旧值 (用于恢复) │
  │    ↓                                │
  │ 4. 执行实际任务                     │
  │    ↓                                │
  │ 5. restore (恢复)                   │
  │    恢复工作线程到执行前的状态        │
  └─────────────────────────────────────┘
```

### 7.3 使用方式

#### 方式一：手动包装 Runnable/Callable

```java
TransmittableThreadLocal<String> ttl = new TransmittableThreadLocal<>();
ttl.set("main-thread-value");

Runnable task = () -> System.out.println(ttl.get());

// 用 TtlRunnable 包装原始 task
Runnable wrappedTask = TtlRunnable.get(task);
executor.submit(wrappedTask);
```

#### 方式二：包装 ExecutorService

```java
// 一次性包装整个线程池
ExecutorService ttlExecutor = TtlExecutors.getTtlExecutorService(executor);

ttl.set("context-value");
ttlExecutor.submit(() -> System.out.println(ttl.get()));  // "context-value"
```

#### 方式三：Java Agent 方式（推荐）

通过 JVM 参数启动，自动拦截线程池的创建：

```bash
java -javaagent:transmittable-thread-local-2.14.5.jar \
     -jar your-application.jar
```

无需修改任何代码，自动对 JDK 线程池、ForkJoinPool、RxJava 等生效。

### 7.4 TTL vs InheritableThreadLocal vs ThreadLocal

| 特性 | ThreadLocal | InheritableThreadLocal | TransmittableThreadLocal |
|------|-------------|----------------------|-------------------------|
| 父子线程传递 | 不支持 | 支持 (仅 new Thread 时) | 支持 (线程池也支持) |
| 线程池支持 | 不支持 | 不支持 | 支持 |
| 实现方式 | Thread 内部字段 | Thread 内部字段 | 装饰器 + Agent |
| 值传递时机 | N/A | 线程创建时 | 任务提交时 (capture) |
| 线程隔离 | 完全隔离 | 完全隔离 | 任务级隔离 (replay/restore) |
| 额外依赖 | 无 | 无 | 需要 ttl jar 包 |
| 性能开销 | 最低 | 低 | 中 (capture/replay 开销) |
| 适用场景 | 单线程内传递 | 简单父子线程场景 | 分布式追踪、全链路上下文传递 |

---

## 八、最佳实践

### 8.1 基本原则：必须 remove

```java
// 正确用法模板
public class ContextHolder {
    private static final ThreadLocal<Context> CONTEXT = new ThreadLocal<>();

    public static void set(Context ctx) {
        CONTEXT.set(ctx);
    }

    public static Context get() {
        return CONTEXT.get();
    }

    public static void remove() {
        CONTEXT.remove();
    }
}

// 使用时务必在 finally 中 remove
public void handleRequest() {
    try {
        ContextHolder.set(new Context());
        // ... 业务逻辑 ...
    } finally {
        ContextHolder.remove();  // ← 必须!
    }
}
```

### 8.2 Filter/Interceptor 中的使用

```java
// Spring MVC Interceptor 示例
public class TraceIdInterceptor implements HandlerInterceptor {

    private static final ThreadLocal<String> TRACE_ID = new ThreadLocal<>();

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) {
        String traceId = request.getHeader("X-Trace-Id");
        TRACE_ID.set(traceId);
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
                                HttpServletResponse response,
                                Object handler,
                                Exception ex) {
        // 请求结束后清理，防止线程池复用导致污染
        TRACE_ID.remove();
    }
}
```

### 8.3 与线程池配合的注意事项

```java
// 反例: 在异步线程中使用 ThreadLocal 后未清理
ExecutorService pool = Executors.newFixedThreadPool(4);

pool.submit(() -> {
    ThreadLocal<String> local = new ThreadLocal<>();
    local.set("async-value");
    doWork();
    // 忘记 remove → 线程池复用后，下一个任务可能读到脏数据!
});

// 正例: 在异步任务中确保清理
pool.submit(() -> {
    try {
        ThreadLocal<String> local = new ThreadLocal<>();
        local.set("async-value");
        doWork();
    } finally {
        local.remove();
    }
});
```

### 8.4 static ThreadLocal vs 非 static

```java
// 推荐: static final ThreadLocal
// 好处: ThreadLocal 实例全局唯一，避免重复创建
public class ServiceA {
    private static final ThreadLocal<UserContext> USER_CTX = new ThreadLocal<>();
}

// 不推荐: 非 static ThreadLocal
public class ServiceB {
    // 每次创建 ServiceB 实例都会新建 ThreadLocal
    // 旧的 ThreadLocal 可能被 GC 回收后留下过期 Entry
    private ThreadLocal<UserContext> userCtx = new ThreadLocal<>();
}
```

### 8.5 ThreadLocal 与初始值

```java
// 方式一: 重写 initialValue (匿名内部类方式)
private static final ThreadLocal<SimpleDateFormat> SDF =
    new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        }
    };

// 方式二: ThreadLocal.withInitial (Java 8+, 推荐)
private static final ThreadLocal<SimpleDateFormat> SDF =
    ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd HH:mm:ss"));
```

### 8.6 内存泄漏检查清单

| 检查项 | 是否满足 |
|--------|----------|
| ThreadLocal 是否声明为 `static final`？ | 是 |
| 使用完毕后是否在 finally 块中调用了 `remove()`？ | 是 |
| 在线程池中使用时，是否有拦截器/过滤器统一清理？ | 是 |
| 是否避免了在 ThreadLocal 中存储大对象？ | 是 |
| 是否使用了 TransmittableThreadLocal 处理线程池上下文传递？ | 视需求 |

### 8.7 常见面试题速查

| 问题 | 要点 |
|------|------|
| ThreadLocal 底层结构是什么？ | ThreadLocalMap，以 ThreadLocal 为 key 的开放定址哈希表 |
| ThreadLocalMap 如何解决哈希冲突？ | 线性探测（开放定址法） |
| Entry 的 key 为什么用弱引用？ | 当外部不再引用 ThreadLocal 时，key 可被 GC 回收，避免 key 泄漏 |
| ThreadLocal 会导致内存泄漏吗？ | 会，value 是强引用，需要手动 remove |
| InheritableThreadLocal 的局限性？ | 只在 new Thread 时传递值，不支持线程池复用场景 |
| TransmittableThreadLocal 解决了什么问题？ | 线程池场景下的上下文传递，通过 capture/replay/restore 机制 |
| ThreadLocal 线程安全的原理？ | 数据隔离，每个线程独立的副本，不存在竞争 |
| ThreadLocal 的 hashCode 怎么生成的？ | 基于 AtomicLong 的 HASH_CODE 累加，保证每次递增 |

---

> **总结：** ThreadLocal 是 Java 并发编程中的重要工具，理解其底层结构和内存管理机制对于正确使用和排查问题至关重要。核心记住三点：**(1) 每个线程独立副本，(2) Entry 的 key 是弱引用、value 是强引用，(3) 用完必须 remove。**
