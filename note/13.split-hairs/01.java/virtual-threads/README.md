<!--
question:
  id: 01.java-virtual-threads
  topic: 01.java
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 新技术原理
  tags: [01.java, virtual-threads, Java-21, JEP-444, 并发, Project-Loom]
-->

# 虚拟线程 —— Java 21 最大变革：同步写法 + 异步性能

> 一句话定位：**Java 21 面试高频题**。考察的不是"虚拟线程怎么用"，而是 **carrier thread 调度原理** + **pinning 问题** + **ThreadLocal 替代方案** + **适用场景判断**。深度实战见 [主模块深度章节](../../../01.java/concurrency/virtual-threads/README.md)。

> **系列定位**：Java 并发高频题（社招必考）。配套兄弟题：[CompletableFuture](../completable-future/README.md)、[ThreadLocal](../threadlocal/)、[synchronized](../synchronized-lock-upgrade/)。

---

⭐⭐⭐⭐ 深度级别（高级工程师级）
📚 前置知识：线程池 / synchronized / ThreadLocal / CompletableFuture

---

## 引子：面试经典开场

面试官："Java 21 的虚拟线程了解吗？和传统线程有什么区别？"

大多数人答："轻量级线程，创建成本低。"

面试官追问：
1. "虚拟线程阻塞时底层发生了什么？carrier thread 是什么？"
2. "synchronized 块内做数据库查询会怎样？"
3. "ThreadLocal 在虚拟线程下有什么问题？"

大多数人卡在追问上。**这道题考察的不是"知道虚拟线程"，而是"理解底层调度机制 + 工程落地陷阱"。**

---

## 一、核心原理

### 1.1 虚拟线程 vs 平台线程

| 特性 | 平台线程 | 虚拟线程 |
|------|---------|---------|
| 映射关系 | 1:1（JVM 线程 = OS 线程） | M:N（多个 VT 共享少量 carrier） |
| 栈空间 | ~1MB（OS 分配） | ~几 KB（JVM 堆上分配） |
| 创建成本 | 微秒级 | 纳秒级 |
| 数量上限 | ~1000（内存限制） | 百万级 |
| 阻塞行为 | OS 线程被占用 | 自动 unmount，carrier 复用 |
| 调度方 | OS 内核 | JVM（ForkJoinPool） |

### 1.2 Mount / Unmount 机制

```
虚拟线程执行流程：
1. mount 到 carrier thread → 执行代码
2. 遇到 I/O 阻塞 → 自动 unmount（carrier 释放）
3. carrier 去执行其他虚拟线程
4. I/O 返回 → 重新 mount 到可用 carrier → 继续执行
```

**关键**：对开发者来说，代码看起来是同步阻塞的，但底层 carrier 从不浪费——这就是"同步写法 + 异步性能"的本质。

---

## 二、7 道精选面试题

### Q1：虚拟线程的 carrier thread 是什么？由谁管理？

**答**：Carrier thread 是 ForkJoinPool 中的平台线程，默认数量 = CPU 核心数。虚拟线程不直接跑在 CPU 上，而是 mount 到 carrier 上执行。

```java
// 虚拟线程调度器（内部实现，简化）
// new ForkJoinPool(
//     parallelism = Runtime.availableProcessors(),
//     factory = virtualThreadFactory,
//     asyncMode = true  // FIFO 队列，非 work-stealing
// )
```

可以通过 `-Djdk.virtualThreadScheduler.parallelism=N` 调整，但通常不需要。

### Q2：虚拟线程在 synchronized 块内阻塞会怎样？

**答**：**Pinning** —— 虚拟线程无法 unmount，会 pin 住 carrier thread，导致其他虚拟线程无法使用该 carrier。

```java
// ❌ Pinning
synchronized (lock) {
    db.query(sql);  // DB I/O 阻塞 → carrier 被 pin → 其他 VT 排队
}

// ✅ 用 ReentrantLock 替代
lock.lock();
try {
    db.query(sql);  // 阻塞时正常 unmount
} finally {
    lock.unlock();
}
```

**检测**：`-Djdk.tracePinnedThreads=short`

**Java 24 改进**（JEP 491）：synchronized 内阻塞也能 unmount，pinning 问题基本消失。

### Q3：ThreadLocal 在虚拟线程下有什么问题？怎么解决？

**答**：虚拟线程可能有百万级，每个持有 ThreadLocal 副本 → 内存爆炸。典型场景：每个线程一个 DB Connection。

**解决方案**：
- **Java 25+**：用 `ScopedValue` 替代（不可变、自动清理、虚拟线程友好）
- **Java 21-24**：减少 ThreadLocal 使用，改用连接池 + 参数传递

```java
// ScopedValue 用法
static final ScopedValue<User> USER = ScopedValue.newInstance();
ScopedValue.where(USER, currentUser).run(() -> processRequest());
```

### Q4：虚拟线程适合什么场景？不适合什么场景？

**答**：

| 场景 | 是否适合 | 原因 |
|------|---------|------|
| HTTP 请求处理 | ✅ | I/O 密集，阻塞时 carrier 复用 |
| 数据库批量查询 | ✅ | 大量阻塞 I/O |
| 微服务并发调用 | ✅ | 同步写法 + 异步性能 |
| 文件读写 | ✅ | I/O 密集 |
| CPU 密集计算 | ❌ | 无阻塞，虚拟线程调度是额外开销 |
| 加密/哈希 | ❌ | 纯计算，用平台线程池 |

### Q5：虚拟线程应该池化吗？

**答**：**不应该**。虚拟线程创建成本极低（纳秒级 + 几 KB），不需要复用。

```java
// ❌ 池化虚拟线程（无意义）
Executors.newFixedThreadPool(100, Thread.ofVirtual().factory());

// ✅ 每任务一线程
Executors.newVirtualThreadPerTaskExecutor();
```

### Q6：CompletableFuture vs 虚拟线程，怎么选？

**答**：

| 维度 | CompletableFuture | 虚拟线程 |
|------|-------------------|---------|
| 编程风格 | 异步回调链 | 同步写法 |
| 可读性 | 中等 | 高 |
| 异常处理 | `.exceptionally()` | 标准 try-catch |
| 适用场景 | 非阻塞 I/O + 流式处理 | 阻塞 I/O + 高并发 |

**最佳组合**：CompletableFuture 的异步任务运行在虚拟线程 Executor 上。

### Q7：生产环境使用虚拟线程需要注意什么？

**答**：4 个检查项——

1. **synchronized → ReentrantLock**（Java < 24 时必须）
2. **ThreadLocal 审计**：确认没有大量 ThreadLocal（迁移到 ScopedValue 或参数传递）
3. **JDBC 驱动兼容**：MySQL Connector/J 8.2+ 已兼容，旧版本可能 pinning
4. **监控**：JFR（Java Flight Recorder）已原生支持虚拟线程事件

---

## 三、常见陷阱

**陷阱 1：给虚拟线程设优先级**

```java
// ❌ 虚拟线程不支持优先级（setPriority 被忽略）
Thread.ofVirtual().start(() -> {
    Thread.currentThread().setPriority(Thread.MAX_PRIORITY);  // 无效
});
```

**陷阱 2：用虚拟线程做 CPU 密集计算**

```java
// ❌ CPU 密集型：虚拟线程没有优势
executor.submit(() -> computeSHA256(data));

// ✅ CPU 密集型用固定线程池
Executors.newFixedThreadPool(availableProcessors());
```

**陷阱 3：忘记关闭 ExecutorService**

```java
// ❌ 虚拟线程 ExecutorService 不关闭 → 程序不退出
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
executor.submit(() -> longRunningTask());
// 没有 close() → 虚拟线程不会自动等待完成

// ✅ 用 try-with-resources
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> longRunningTask());
}  // 自动 close() → 等待所有任务完成
```

---

## 四、面试话术（30 秒版）

> "虚拟线程是 Java 21 正式转正的轻量级线程，由 JVM 的 ForkJoinPool 调度，每个只需几 KB 栈空间。
>
> 核心机制是 M:N 模型：虚拟线程 mount 到 carrier thread 上执行，遇到 I/O 阻塞时自动 unmount，carrier 去执行其他虚拟线程。这让开发者用同步阻塞写法就能获得异步性能。
>
> 生产环境注意 4 点：synchronized 替换为 ReentrantLock（防 pinning，Java 24 已修复）、ThreadLocal 迁移到 ScopedValue、JDBC 驱动兼容性、ExecutorService 用 try-with-resources 确保关闭。
>
> 虚拟线程最适合 I/O 密集型场景（HTTP / DB / 微服务调用），不适合 CPU 密集型计算。"

---

## 五、交叉引用

- **深度实战**：[虚拟线程深度解析](../../../01.java/concurrency/virtual-threads/README.md) — carrier thread + pinning + 结构化并发 + 框架集成
- **相关面试题**：[CompletableFuture](../completable-future/README.md) — 异步编排 + 虚拟线程集成
- **相关面试题**：[synchronized 锁升级](../synchronized-lock-upgrade/) — pinning 的根因
- **相关面试题**：[ThreadLocal 原理](../threadlocal/) — 虚拟线程下的内存问题
- **主模块**：[`01.java/concurrency`](../../../01.java/concurrency/README.md) — 并发编程专题导航

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · virtual-threads](README.md)
