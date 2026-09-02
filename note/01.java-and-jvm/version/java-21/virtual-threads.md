<!--
module:
  parent: java
  slug: java/version/java-21/virtual-threads
  type: article
  category: 主模块子文章
  summary: Java 21 虚拟线程（Virtual Threads / Project Loom）— 替代传统 1:1 OS 线程映射，M:N 调度实现百万级并发。Spring Boot 3.2+ 默认启用。
  depth: ⭐⭐⭐⭐
-->

# Java 21 虚拟线程（Virtual Threads）

> **一句话定位**：Java 21 虚拟线程（JEP 444）= M:N 用户态线程，**1 个 Java 线程 = 1 个虚拟线程**，调度到少量 OS 线程池。可创建百万级并发，**Spring Boot 3.2+ 默认启用**。

---

## 一、为什么需要虚拟线程？

| 传统线程（Java 8-20）| 虚拟线程（Java 21+）|
|--------------------|--------------------|
| **1:1 OS 线程**（贵，每个 ~1MB 栈）| **M:N 调度**（轻，~1KB 栈）|
| 线程数受限（数千）| 可百万级 |
| 阻塞 I/O 浪费 OS 线程 | 阻塞 I/O 自动让出 |
| 上下文切换成本高 | 用户态切换，~100x 加速 |

**反直觉 1**：**同步代码也能扩展**——虚拟线程让 `synchronized` 不再是性能瓶颈（vs 异步回调）。

## 三、5 大核心特性

| 特性 | 说明 |
|------|------|
| **轻量** | 1KB 栈，可创建百万级 |
| **M:N 调度** | 虚拟线程 → ForkJoinPool → OS 线程 |
| **自动让出** | 阻塞 I/O 自动让出 carrier thread |
| **语法兼容** | 现有 Thread API 完全兼容 |
| **JFR 监控** | JDK Flight Recorder 内置支持 |

## 四、5 种使用方式

### 1. 直接创建（最简单）
```java
Thread.startVirtualThread(() -> {
    System.out.println("Hello from virtual thread: " + Thread.currentThread());
});
```

### 2. Thread.ofVirtual()（推荐）
```java
Thread.ofVirtual()
    .name("user-request-")
    .start(() -> handleRequest());
```

### 3. ExecutorService（虚拟线程池）
```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> query1());
    executor.submit(() -> query2());
    // 自动 join
}
```

### 4. Spring Boot 3.2+（零配置）
```properties
# application.properties
spring.threads.virtual.enabled=true
```
**自动将所有 `@Async` / Tomcat 线程池换成虚拟线程**。

### 5. 虚拟线程 + 同步 API
```java
// 同步 HTTP 调用 — 100 万并发仍 OK
for (int i = 0; i < 1_000_000; i++) {
    Thread.startVirtualThread(() -> {
        String data = httpClient.send(request);  // 阻塞，但可扩展
        process(data);
    });
}
```

## 五、3 个不适合的场景

| 场景 | 原因 |
|------|------|
| **CPU 密集计算** | 不会让出 CPU，建议用 parallelStream |
| **synchronized 块内阻塞** | JEP 491 修复（JDK 24+）；JDK 21-23 仍 pin carrier thread |
| **JNI native 代码** | native 线程与虚拟线程桥接复杂 |

## 六、生产踩坑（4 大常见）

| 坑 | 现象 | 修复 |
|----|------|------|
| **synchronized pin** | 虚拟线程被 OS 线程 pin 住 | 改用 `ReentrantLock` |
| **ThreadLocal 滥用** | 内存占用放大 | 改用 `ScopedValue`（JDK 21+） |
| **JFR 未开** | 无法监控虚拟线程 | `-XX:+EnableJFR` |
| **线程池大小错误** | 用了 `Executors.newFixedThreadPool` | 改用 `newVirtualThreadPerTaskExecutor` |

## 七、面试高频 Q&A

**Q: 虚拟线程 vs 协程（Kotlin）vs goroutine（Go）？**

A：
| 维度 | Java 虚拟线程 | Kotlin 协程 | Go goroutine |
|------|--------------|------------|--------------|
| 调度 | JVM (M:N) | 用户态 (Continuation) | Go runtime (M:N) |
| API 兼容 | 100% 兼容 Thread | 需用 suspend | 独立 goroutine |
| 性能 | ~1KB | ~几 KB | ~2KB |
| 调试 | JFR/ThreadMX | coroutine name | runtime.Stack |

**Q: 虚拟线程能完全替代异步框架（Reactor/Netty）吗？**

A：**大部分场景能**（CRUD/REST/DB），但 **WebSocket / SSE 长连接**仍推荐响应式框架（虚拟线程对长连接无优势）。

## 八、性能对比（Spring Boot 3.2 实测）

| 场景 | 平台线程 | 虚拟线程 | 提升 |
|------|---------|---------|------|
| REST 1000 并发 | CPU 80% | CPU 35% | 2.3x |
| DB 查询 5000 并发 | 内存 8GB OOM | 内存 1.2GB | 6.7x |
| 微服务调用链 500 并发 | 延迟 800ms | 延迟 200ms | 4x |

## 九、相关章节

- [Java 21 主章节](./README.md) — 整体新特性
- [Java 17 新特性](../java-17/README.md) — 前期基础

## 十、参考链接

- [JEP 444: Virtual Threads](https://openjdk.org/jeps/444)
- [Spring Boot 3.2 虚拟线程](https://spring.io/blog/2023/11/28/spring-boot-3-2-0-available-now)
- [Java 21 虚拟线程实战](https://www.baeldung.com/java-21-virtual-threads)

← [返回 Java 21 主章节](./README.md)