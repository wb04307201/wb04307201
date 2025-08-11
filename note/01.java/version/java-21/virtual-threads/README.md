# Java 虚拟线程

Java 虚拟线程（Virtual Threads）是 JDK 19 引入（JDK 21 正式发布）的轻量级线程实现，由 JVM 管理而非操作系统内核，旨在解决传统线程在高并发场景下的资源限制问题，显著提升 I/O 密集型应用的性能与开发效率。

## 核心特性
1. **轻量级**
    - **内存占用低**：每个虚拟线程仅需约 1KB 栈空间（传统线程需 1MB 以上），可轻松创建百万级线程。
    - **用户态调度**：由 JVM 的协作式调度器管理，上下文切换在用户态完成，无需操作系统介入，开销极低。

2. **阻塞不浪费资源**
    - 遇到 I/O 操作（如网络请求、数据库查询）时，虚拟线程会自动挂起并释放载体线程（平台线程），让其他虚拟线程继续执行，避免资源闲置。

3. **兼容传统 API**
    - 完全兼容 `Thread`、`Runnable`、`ExecutorService` 等现有并发编程接口，无需学习新框架即可上手。

4. **结构化并发（JDK 21+）**
    - 支持 `StructuredTaskScope`，可安全管理多个并发任务，子任务出错时自动取消其他未完成任务。

## 与传统线程的对比
| **特性**               | **虚拟线程**                     | **传统线程（平台线程）**         |
|------------------------|----------------------------------|----------------------------------|
| **管理方**             | JVM                              | 操作系统内核                     |
| **内存占用**           | 约 1KB                           | 1MB 以上                         |
| **并发数量**           | 百万级                           | 几千级（受系统资源限制）         |
| **上下文切换开销**     | 用户态完成，极低                 | 需内核介入，较高                 |
| **阻塞行为**           | 自动挂起并释放载体线程           | 阻塞时仍占用资源                 |
| **编程模型**           | 同步风格，异步性能               | 需手动管理线程池，复杂度高       |

## 适用场景
1. **高并发 Web 服务**
    - 处理数万并发请求（如聊天室、游戏服务器、微服务网关），虚拟线程可避免线程资源耗尽问题。

2. **I/O 密集型任务**
    - 网络爬虫、批量数据库查询、文件读写等场景，虚拟线程通过“挂起-恢复”机制高效利用资源。

3. **微服务架构**
    - 服务间频繁调用（如 REST API、RPC），虚拟线程减少线程阻塞带来的性能损耗。

4. **异步编程替代方案**
    - 无需编写复杂的异步回调代码（如 CompletableFuture），保持同步编程风格的同时获得高性能。

## 代码示例
### 1. 直接创建虚拟线程
```java
Thread.startVirtualThread(() -> {
    System.out.println("运行在虚拟线程: " + Thread.currentThread());
});
```

### 2. 使用 ExecutorService 批量创建
```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> {
        executor.submit(() -> {
            System.out.println("任务 " + i + " 执行中");
            Thread.sleep(10); // 模拟 I/O 操作
            return "结果 " + i;
        });
    });
}
```

### 3. 结构化并发（JDK 21+）
```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    StructuredTaskScope.Subtask<String> task1 = scope.fork(() -> fetchData("A"));
    StructuredTaskScope.Subtask<String> task2 = scope.fork(() -> fetchData("B"));
    scope.join(); // 等待所有子任务完成
    System.out.println(task1.get() + task2.get());
} catch (Exception e) {
    e.printStackTrace();
}
```

## 性能对比
- **测试场景**：处理 100 万个任务，每个任务模拟 10ms I/O 延迟。
- **传统线程池（200 线程）**：
    - 耗时：约 30,000ms
    - 内存峰值：1.2GB
- **虚拟线程**：
    - 耗时：约 5,000ms
    - 内存峰值：200MB

## 注意事项
1. **不适合 CPU 密集型任务**
    - 虚拟线程的优势在于处理 I/O 阻塞，若任务持续占用 CPU，传统线程可能更高效。

2. **阻塞操作需支持挂起**
    - 虚拟线程依赖底层 API（如 `java.net`、`java.io` 包）的协程化实现，部分旧库可能不支持。

3. **调试差异**
    - 虚拟线程堆栈较深，调试时需区分载体线程和虚拟线程。

4. **ThreadLocal 行为变化**
    - 虚拟线程的 `ThreadLocal` 行为与传统线程不同，建议使用 `InheritableThreadLocal` 或 `ScopedValue`（JDK 21+）。