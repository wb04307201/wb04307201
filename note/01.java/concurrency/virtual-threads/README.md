<!--
module:
  parent: java/concurrency
  slug: java/concurrency/virtual-threads
  type: deep-dive
  category: 虚拟线程
  summary: Java 21 虚拟线程深度解析 —— carrier thread / mount-unmount / pinning / ThreadLocal 替代 / 结构化并发 / 框架集成
-->

# 虚拟线程（Virtual Threads）—— Java 并发编程最大变革

> **一句话定位**：虚拟线程是 JVM 管理的轻量级线程，每个仅 ~几 KB 栈空间（平台线程 ~1MB），可以用**同步写法获得异步性能**，彻底改变了 Java 高并发编程模型。JEP 444 在 Java 21 正式转正。

📚 **前置知识**：[synchronized](../synchronized/README.md) · [ThreadLocal](../threadlocal/README.md) · [CompletableFuture](../completablefuture/README.md)

---

## 一、核心原理

### 1.1 平台线程 vs 虚拟线程

```
平台线程（Platform Thread）
┌──────────────────────────────────┐
│  1:1 映射到 OS 线程               │
│  每个 ~1MB 栈空间                 │
│  创建/销毁成本高（微秒级）         │
│  数量受限（通常 < 1000）           │
│  阻塞时 OS 线程被占用              │
└──────────────────────────────────┘

虚拟线程（Virtual Thread）
┌──────────────────────────────────┐
│  M:N 模型，JVM 调度              │
│  每个 ~几 KB 栈空间（堆上分配）    │
│  创建/销毁成本极低（纳秒级）       │
│  可创建数百万                     │
│  阻塞时自动 unmount，carrier 复用  │
└──────────────────────────────────┘
```

### 1.2 Carrier Thread 与 Mount/Unmount

虚拟线程不直接跑在 CPU 上，而是**挂载**（mount）到 carrier thread（平台线程）上执行：

```
                    ┌─ Virtual Thread 1 ─┐
                    │ (状态: running)     │
                    └────────┬───────────┘
                             │ mount
┌────────────────────────────▼────────────────────────────┐
│              ForkJoinPool（carrier threads）              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │ Carrier-1  │  │ Carrier-2  │  │ Carrier-3  │        │
│  │ (平台线程) │  │ (平台线程) │  │ (平台线程) │        │
│  │ VT-1 mount │  │ VT-5 mount │  │ VT-9 mount │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└─────────────────────────────────────────────────────────┘

                    ┌─ Virtual Thread 2 ─┐
                    │ (状态: unmounted)   │ ← 阻塞中，不占 carrier
                    │ 等待 I/O 返回       │
                    └────────────────────┘
```

**Mount**：虚拟线程被分配到一个 carrier thread 上执行。

**Unmount**：虚拟线程遇到阻塞操作（I/O / `Thread.sleep` / `Lock.lock`）时，JVM 自动将其从 carrier 上卸载，carrier 可以去执行其他虚拟线程。I/O 返回后重新 mount。

```java
// 这段代码看起来是同步阻塞的，但实际不浪费 carrier
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> {
        // 1. mount 到 carrier
        var response = httpClient.send(request, BodyHandlers.ofString());  // 阻塞
        // 2. 阻塞时自动 unmount，carrier 去执行其他 VT
        // 3. I/O 返回后重新 mount
        return response.body();
    });
}
```

### 1.3 调度器：ForkJoinPool

虚拟线程的 carrier threads 由 **ForkJoinPool** 管理（非 `commonPool`），默认线程数 = CPU 核心数：

```java
// 内部实现（简化）
// 虚拟线程调度器 = 新 ForkJoinPool，非 daemon，parallelism = Runtime.availableProcessors()
```

可以通过 JVM 参数调整：

```bash
# 调整 carrier 线程数（通常不需要改）
-Djdk.virtualThreadScheduler.parallelism=8

# 调整最大 carrier 线程数（防止 pinning 导致饥饿）
-Djdk.virtualThreadScheduler.maxPoolSize=256
```

---

## 二、基本用法

### 2.1 创建虚拟线程

```java
// 方式 1：Thread.startVirtualThread（最简单）
Thread vt = Thread.startVirtualThread(() -> {
    System.out.println("Hello from: " + Thread.currentThread());
    // 输出: Hello from: VirtualThread[#21]/runnable@ForkJoinPool-1-worker-1
});
vt.join();

// 方式 2：Thread.ofVirtual()（可配置名称）
Thread vt2 = Thread.ofVirtual()
    .name("my-vt-", 0)  // 名称前缀 + 序号
    .start(() -> doWork());

// 方式 3：ExecutorService（最推荐，生产环境首选）
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 100_000).forEach(i ->
        executor.submit(() -> {
            Thread.sleep(Duration.ofSeconds(1));  // 不占 carrier
            return "task-" + i;
        })
    );
}  // close() 自动等待所有任务完成
```

### 2.2 虚拟线程 vs 线程池

```java
// ❌ 旧方式：线程池，线程数受限
ExecutorService pool = Executors.newFixedThreadPool(200);
// 200 线程 × ~1MB = ~200MB 内存
// 10 万任务排队等 200 个线程

// ✅ 新方式：虚拟线程，每个任务一个线程
ExecutorService vtExecutor = Executors.newVirtualThreadPerTaskExecutor();
// 10 万虚拟线程 × ~几KB = ~几百MB 内存
// 10 万任务同时执行，无需排队
```

---

## 三、Pinning 问题与解决

### 3.1 什么是 Pinning

虚拟线程在 `synchronized` 块或 native 方法中阻塞时，**无法 unmount**，会 pin 住 carrier thread：

```java
// ❌ Pinning：synchronized 内部阻塞 I/O
synchronized (lock) {
    httpClient.send(request, BodyHandlers.ofString());  // 阻塞时 pin 住 carrier！
}
// 后果：carrier 被占用，其他虚拟线程无法使用这个 carrier
```

### 3.2 检测 Pinning

```bash
# 启动时加 JVM 参数，检测 pinning 事件
-Djdk.tracePinnedThreads=short  # 打印 pinning 堆栈（简短）
-Djdk.tracePinnedThreads=full   # 打印完整堆栈
```

### 3.3 解决方案：用 ReentrantLock 替代 synchronized

```java
// ❌ Pinning（synchronized）
synchronized (this) {
    jdbcTemplate.queryForObject(sql, String.class);  // DB I/O pin 住 carrier
}

// ✅ 不 Pinning（ReentrantLock）
private final ReentrantLock lock = new ReentrantLock();

lock.lock();
try {
    jdbcTemplate.queryForObject(sql, String.class);  // 阻塞时正常 unmount
} finally {
    lock.unlock();
}
```

**Java 24 改进**（JEP 491）：虚拟线程在 `synchronized` 中阻塞时也能释放 carrier thread，解决了这个痛点。如果你使用 Java 24+，pinning 问题基本消失。

---

## 四、ThreadLocal 与 ScopedValue

### 4.1 虚拟线程下 ThreadLocal 的问题

虚拟线程可能有**数百万**个，每个都持有 ThreadLocal 副本会导致巨大的内存开销：

```java
// ❌ 虚拟线程 + ThreadLocal = 内存爆炸
private static final ThreadLocal<Connection> DB_CONN =
    ThreadLocal.withInitial(() -> createConnection());

// 100 万虚拟线程 × 每个持有一个 Connection = 100 万连接！
```

### 4.2 ScopedValue（Java 25+ 转正）

`ScopedValue` 是 ThreadLocal 的现代替代，专为虚拟线程设计：

```java
// ✅ ScopedValue：不可变、轻量、虚拟线程友好
private static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();

// 设置作用域值（不可变，线程安全）
ScopedValue.where(CURRENT_USER, authenticatedUser)
    .run(() -> {
        processRequest();  // 当前线程及子线程可访问
    });

void processRequest() {
    User user = CURRENT_USER.get();  // 高效获取
    // 无需 remove()，作用域结束自动清理
}
```

**对比表**：

| 特性 | ThreadLocal | ScopedValue |
|------|-------------|-------------|
| 可变性 | 可变（`set()`） | **不可变**（创建后不能改） |
| 清理 | 需手动 `remove()` | 自动（作用域结束） |
| 虚拟线程 | 百万级 VT 内存开销大 | 轻量，无内存问题 |
| 继承 | `InheritableThreadLocal` | 自动传递给子 VT |
| 状态 | Java 1 正式 | Java 25 转正 |

---

## 五、结构化并发

### 5.1 问题：子任务的生命周期管理

```java
// ❌ CompletableFuture：子任务失败时不会自动取消其他任务
CompletableFuture<User> userFuture = supplyAsync(() -> findUser(id));
CompletableFuture<Order> orderFuture = supplyAsync(() -> fetchOrder(id));
// userFuture 失败 → orderFuture 仍在执行 → 浪费资源
```

### 5.2 StructuredTaskScope

结构化并发将多个子任务视为一个工作单元，任一失败自动取消其他：

```java
// ✅ 结构化并发（Java 19+ 预览，预计 Java 25+ 转正）
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<User> userTask = scope.fork(() -> findUser(id));
    Subtask<Order> orderTask = scope.fork(() -> fetchOrder(id));

    scope.join();            // 等待所有子任务完成
    scope.throwIfFailed();   // 任一失败则抛出异常

    return new Response(userTask.resultNow(), orderTask.resultNow());
}
// try-with-resources 退出时，自动取消所有未完成的子任务
```

**ShutdownOnFailure vs ShutdownOnSuccess**：

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| `ShutdownOnFailure` | 任一子任务失败 → 取消其他 | 并行查询，全部需要 |
| `ShutdownOnSuccess` | 任一子任务成功 → 取消其他 | 竞速查询，取最快结果 |

---

## 六、适用场景与反模式

### 6.1 什么时候用虚拟线程

```
任务类型？
├─ I/O 密集型（HTTP / DB / 文件）→ ✅ 虚拟线程（最佳场景）
├─ 高并发请求处理 → ✅ 虚拟线程（每请求一线程）
├─ CPU 密集型（计算 / 加密）→ ❌ 保持平台线程池
├─ 需要 synchronized 且 Java < 24 → ⚠️ 改用 ReentrantLock
└─ 大量使用 ThreadLocal → ⚠️ 迁移到 ScopedValue 后再用
```

### 6.2 5 大反模式

**1. 池化虚拟线程**

```java
// ❌ 虚拟线程不应该池化（创建成本低，无需复用）
ExecutorService pool = Executors.newFixedThreadPool(100,
    Thread.ofVirtual().factory());

// ✅ 每个任务创建一个新虚拟线程
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
```

**2. 用虚拟线程做 CPU 密集计算**

```java
// ❌ CPU 密集型：虚拟线程没有性能优势，反而调度开销更大
executor.submit(() -> computeHash(data));  // 纯计算

// ✅ CPU 密集型用平台线程池
ExecutorService cpuPool = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
cpuPool.submit(() -> computeHash(data));
```

**3. 忽略 Pinning（Java < 24）**

```java
// ❌ synchronized 内做 I/O，pin 住 carrier
synchronized (this) {
    db.query(sql);
}

// ✅ 用 ReentrantLock（Java 21-23）或直接升级 Java 24+
```

**4. 虚拟线程 + 大量 ThreadLocal**

```java
// ❌ 百万虚拟线程 × ThreadLocal = 内存爆炸
// ✅ 迁移到 ScopedValue（Java 25+）或减少 ThreadLocal 使用
```

**5. 给虚拟线程设置优先级**

```java
// ❌ 虚拟线程不支持线程优先级（setPriority 无效）
Thread.ofVirtual().start(() -> {
    Thread.currentThread().setPriority(Thread.MAX_PRIORITY);  // 无效！
});
```

---

## 七、框架集成

### 7.1 Spring Boot 3.2+

```yaml
# application.yml
spring:
  threads:
    virtual:
      enabled: true  # Tomcat 和 @Async 自动使用虚拟线程
```

### 7.2 注意事项

| 框架/库 | 虚拟线程兼容性 | 说明 |
|---------|--------------|------|
| **Tomcat 10.1+** | ✅ | Spring Boot 3.2 开启后自动使用 |
| **JDBC 驱动** | ⚠️ 部分 | MySQL Connector/J 8.2+ 已兼容；旧驱动可能 pinning |
| **Redis (Lettuce)** | ✅ | 基于 Netty，非阻塞 |
| **Kafka Client** | ⚠️ 部分 | 0.11+ 版本基本兼容 |
| **Hibernate** | ✅ | 6.x 版本已适配 |

---

## 八、面试话术（30 秒版）

> "虚拟线程是 Java 21 正式转正的轻量级线程，由 JVM 调度而非 OS 调度。每个虚拟线程只需几 KB 栈空间（平台线程 1MB），可以轻松创建百万级。
>
> 底层原理是 M:N 模型——虚拟线程 mount 到 carrier thread（ForkJoinPool 管理的平台线程）上执行，遇到 I/O 阻塞时自动 unmount，carrier 去执行其他虚拟线程。这让开发者可以用同步写法获得异步性能。
>
> 需要注意 pinning 问题：synchronized 块内的阻塞 I/O 会 pin 住 carrier（Java 24 已修复）。生产环境用 ReentrantLock 替代 synchronized。
>
> 虚拟线程是 I/O 密集型的最佳选择，不适合 CPU 密集计算。配合结构化并发（StructuredTaskScope）和 ScopedValue（替代 ThreadLocal），构成了 Java 现代并发编程三件套。"

---

## 九、交叉引用

- **前置知识**：[synchronized](../synchronized/README.md) — 锁升级 + pinning 的根因
- **前置知识**：[ThreadLocal](../threadlocal/README.md) — 虚拟线程下的内存问题 + ScopedValue 替代
- **异步编排**：[CompletableFuture](../completablefuture/README.md) — 虚拟线程集成 + 对比
- **版本演进**：[Java 21](../../version/java-21/README.md) — JEP 444 全景 + 迁移指南
- **并发演进**：[并发功能历史](../../version/function-history/concurrency/README.md) — JEP 425→444→491 完整演进链
- **面试题**：[13.split-hairs/virtual-threads](../../../13.split-hairs/01.java/virtual-threads/README.md) — 7 道精选 Q&A

## 相关章节

- 主模块：[`01.java`](../../README.md) — Java 知识体系
- 深度阅读：[`01.java/concurrency`](../README.md) — 并发编程专题导航

← [返回 Java 并发编程专题](../README.md)
