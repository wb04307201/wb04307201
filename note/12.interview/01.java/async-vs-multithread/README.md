<!--
question:
  id: 01.java-async-vs-multithread
  topic: 01.java
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 概念辨析
  tags: [01.java, async, multithreading, concurrency]
-->

# 异步就是多线程吗？

> **一句话定位**：异步讲"是否阻塞"，多线程讲"几个执行单元" —— 二者可独立组合，是并发编程最常被混淆的一对概念。

## 引子：一个常见的误解

面试官："你了解异步编程吗？"
候选人："了解，就是用多线程嘛。"

**错！** 异步和多线程是两个不同维度的概念。很多人把这两个概念混为一谈，但它们分别回答的是两个完全不同的问题：

- 异步回答的是："调用后要不要等结果？"
- 多线程回答的是："用几个线程来执行？"

---

## 一、核心原理：两个维度的区别

### 1.1 异步（Asynchronous）—— 执行顺序维度

| 模式 | 调用后行为 | 是否阻塞当前线程 |
|------|-----------|----------------|
| **同步** | 等待结果返回，才能执行下一步 | 是 |
| **异步** | 立即返回，结果通过回调/通知获取 | 否 |

```java
// 同步：阻塞等待
String result = httpClient.get("https://api.example.com");  // 阻塞 3 秒
process(result);  // 3 秒后才能执行

// 异步：立即返回
CompletableFuture<String> future = httpClient.getAsync("https://api.example.com");
future.thenAccept(result -> process(result));  // 数据到达时自动执行
System.out.println("这行立即执行，不等待");
```

**本质**：异步关注的是**调用者是否阻塞**。异步调用不阻塞发起方，结果通过回调、Future、Promise 等机制在将来某个时间点获取。

### 1.2 多线程（Multithreading）—— 执行主体维度

| 模式 | 执行方式 | 线程数量 |
|------|---------|---------|
| **单线程** | 所有任务排队执行 | 1 个 |
| **多线程** | 多个任务并发执行 | N 个 |

```java
// 单线程：所有任务排队
Thread thread = new Thread(() -> {
    task1();  // 1 秒
    task2();  // 1 秒
    task3();  // 1 秒
});  // 总计 3 秒

// 多线程：并发执行
new Thread(() -> task1()).start();  // 线程 1
new Thread(() -> task2()).start();  // 线程 2
new Thread(() -> task3()).start();  // 线程 3
// 总计 ~1 秒（假设 CPU 核心足够）
```

**本质**：多线程关注的是**有多少个执行单元**在同时工作。

### 1.3 关键区别

| 维度 | 异步 | 多线程 |
|------|------|--------|
| **关注点** | 执行顺序（是否阻塞） | 执行主体（线程数量） |
| **核心问题** | "调用后要不要等？" | "用几个线程执行？" |
| **实现方式** | 回调 / Promise / Future / 事件循环 | 创建多个线程 |
| **典型场景** | I/O 操作（网络请求、文件读写） | CPU 密集任务（计算、图像处理） |
| **资源开销** | 低（单线程 + 事件循环） | 高（线程创建 + 上下文切换） |
| **适合任务** | I/O 密集型 | CPU 密集型 |

---

## 二、4 种组合模式

### 2.1 同步 + 单线程（最传统）

```java
// 所有任务排队执行，阻塞等待
BufferedReader reader = new BufferedReader(new FileReader("file.txt"));
String line = reader.readLine();  // 阻塞
process(line);
```

**特点**：最简单，但效率最低。I/O 操作时线程阻塞等待，无法做其他事情。

### 2.2 异步 + 单线程（Node.js 模型）

```javascript
// 单线程 + 事件循环 + 非阻塞 I/O
fs.readFile('file.txt', (err, data) => {
    console.log(data);  // 数据到达时执行
});
console.log("这行先执行");  // 不等待文件读取
```

**特点**：Node.js 就是这种模型。单线程通过事件循环 + 非阻塞 I/O 实现高并发，适合 I/O 密集型场景。

### 2.3 异步 + 多线程（Java CompletableFuture）

```java
// 异步任务在线程池执行
CompletableFuture.supplyAsync(() -> {
    return fetchData();  // 在线程池的某个线程执行
}).thenAccept(data -> {
    process(data);  // 可能在另一个线程执行
});
System.out.println("这行立即执行");
```

**特点**：Java 最推荐的方式。异步编排 + 线程池执行，兼顾非阻塞和并发能力。

### 2.4 同步 + 多线程（线程池 + Future.get）

```java
ExecutorService executor = Executors.newFixedThreadPool(4);
Future<String> future = executor.submit(() -> {
    return fetchData();  // 在线程池执行
});
String result = future.get();  // ❌ 阻塞等待，退化为同步
System.out.println("get() 返回后才执行");
```

**特点**：虽然用了多线程，但调用者通过 `Future.get()` 阻塞等待，实际上退化成了同步调用。

---

## 三、常见误区

### 误区 1："异步 = 多线程"

- **反例**：Node.js 是单线程 + 异步（事件循环 + 非阻塞 I/O）
- **真相**：异步可以用单线程实现，不依赖多线程。JavaScript 的 `setTimeout`、`fetch` 都是异步但运行在单线程环境中

### 误区 2："多线程 = 异步"

- **反例**：线程池 + `Future.get()` 是多线程但同步阻塞
- **真相**：多线程只是提供了并发执行的能力，是否异步取决于调用方式

### 误区 3："异步一定比同步快"

- **真相**：异步适合 I/O 密集型（不阻塞线程），CPU 密集任务用多线程更合适
- **示例**：计算 100 万个数的和，异步不会比同步快（没有 I/O 等待，反而增加回调开销）

### 误区 4："单线程不能做异步"

- **反例**：Node.js、浏览器 JavaScript 都是单线程异步模型
- **真相**：异步的核心是非阻塞 + 事件循环，与线程数量无关

---

## 四、什么时候用什么？

```text
                    任务类型是什么？
                    /              \
              I/O 密集型         CPU 密集型
                 |                   |
            用异步优先          用多线程优先
                 |                   |
        ┌────────┴────────┐    ┌────┴────┐
        |                 |    |         |
    单线程异步      多线程异步     多线程同步  多线程异步
    (Node.js)    (CompletableFuture) (Future.get) (supplyAsync)
    适合超高并发  适合 Java 后端    简单但不推荐  适合并行计算
```

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 网络请求 / API 调用 | 异步（单/多线程均可） | I/O 等待不阻塞线程 |
| 数据库查询 | 异步 + 多线程（CompletableFuture） | 异步编排 + 线程池并发查询 |
| 文件读写 | 异步（单线程事件循环） | NIO 非阻塞 I/O |
| 数值计算 / 加密 / 压缩 | 多线程（同步或异步均可） | CPU 密集，需要多核心并行 |
| 图片处理 / 视频编码 | 多线程 | 纯 CPU 计算 |

---

## 五、面试话术（30 秒版）

> "异步和多线程是两个维度的概念。**异步**关注执行顺序——调用后要不要等结果，同步阻塞等待，异步立即返回通过回调获取；**多线程**关注执行主体——用单线程还是多个线程并发执行。
>
> 两者可以组合：Node.js 是**单线程 + 异步**（事件循环 + 非阻塞 I/O）；Java 的 `CompletableFuture` 是**异步 + 多线程**（异步任务在线程池执行）；线程池 + `Future.get()` 是**多线程但同步**（阻塞等待结果）。
>
> 常见误区是'异步等于多线程'——实际上异步可以用单线程实现（如 Node.js），多线程也可以同步阻塞（如 `Future.get()`）。选择取决于场景：I/O 密集用异步，CPU 密集用多线程。"

---

## 六、交叉引用

- [CompletableFuture 原理](../../../01.java-and-jvm/03-concurrency/completablefuture/README.md) — Java 异步编程实现
- [线程池原理](../../../01.java-and-jvm/03-concurrency/thread-pool/README.md) — 多线程并发执行
- [事件循环 Event Loop](../../09.front-end/event-loop/README.md) — 单线程异步模型（前端视角）
- [并发 vs 并行](../concurrency-vs-parallelism/README.md) — 并发与并行的概念辨析
- 主模块：[`01.java`](../../../01.java-and-jvm/) — Java 知识体系

## 相关章节

- 深度阅读：[`01.java-and-jvm`](../../../01.java-and-jvm/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · Java](../README.md)
