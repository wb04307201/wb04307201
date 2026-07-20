<!--
question:
  id: 01.java-concurrency-vs-parallelism
  topic: 01.java
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 概念辨析
  tags: [01.java, concurrency, parallelism, Rob-Pike, async, multithreading]
-->

# 并发 vs 并行 —— Rob Pike 经典定义 + 6 大误区 + 90 秒话术

> 一句话定位：**Concurrency 是结构（同一时间段处理多任务），Parallelism 是执行（同一时刻真跑多个）**——Rob Pike 名言。完整深度 + Java 实战见 [主模块 · Java 并发编程专题导航 第 1.3 节](../../../01.java/concurrency/README.md)。

> **系列定位**：Java 高频基础题（校招 70%+ 出题率 / 社招 50%）。考察的不是"听上去差不多"，而是 **Rob Pike 经典定义 + 6 大常见误区 + 多语言对照 + CPU-bound vs IO-bound 选型**。

---

⭐⭐⭐ 深度级别（应届/校招必会 / 社招基础）
📚 前置知识：线程基础 / async 异步编程 / CPU 与核数概念

---

## 引子：3 个崩溃现场

```text
场景：2025 春招 Java 后端一面——

面试官：「并发和并行的区别？」

候选人 A：「并发是同时处理多个，并行也是同时处理多个。」
            → 0 分，零区分

候选人 B：「并发是多线程，并行是多核。」
            → 60 分，遗漏结构 vs 执行的本质

候选人 C：「Concurrency 是 dealing with many things at once，
           Parallelism 是 doing many things at once。」
           + 补 Rob Pike 3 张图 + 6 大误区 + Java 实战
            → 高分
```

**三个层次**：

1. 校招：「并发 vs 并行？」
2. 社招：「Goroutine 是并发还是并行？取决于什么？」
3. 架构师：「一个 IO 密集 + CPU 密集混合系统，怎么选并发模型？」

普通候选人会答"同时处理多个"——踩中"**定义模糊、混淆结构 vs 执行、不会多模型选型**" 3 大雷区。
高分候选人会答：**Rob Pike 经典 + 3 张图 + 6 大误区 + CPU-bound vs IO-bound 选型矩阵**。

---

## 一、核心原理（必选）

### 1.1 Rob Pike 一句话定义（终极金句）

```text
Concurrency is about dealing with many things at once.
Parallelism is about doing many things at once.
                  —— Rob Pike, "Concurrency is not Parallelism"

并发是「结构」(deal with)：同一时间段处理多个任务的能力
并行是「执行」(do)：同一时刻多个任务真在跑的事实
```

### 1.2 3 张经典图速查（高频考点）

#### 图 1：咖啡店比喻

```
[Concurrent] 1 个咖啡师轮流做 5 杯      [Parallel] 5 个咖啡师各做 1 杯
  ┌─────────────────┐                      ┌──────────┐
  │ T1 ████ ████ ████│ T2:T3               │ T1 ████ │
  │ T2 ████ ████ ████│                       ├──────────┤
  │ T3 ████ ████ ████│                       │ T2 ████ │
  │ T4 ████ ████ ████│                       ├──────────┤
  │ T5 ████ ████ ████│                       │ T3 ████ │
  └─────────────────┘                      └──────────┘
  单核 × 5 任务                               多核 × 1 任务/核
  → 同一时间段，看起来同时                    → 同一时刻，真同时
```

#### 图 2：时序图（核心）

```text
并发（单核 / 时分复用）：
  Thread-A: |██░░░░░░░░|██░░░░░░░░|██░░░░░░░░|
  Thread-B: ░░|██░░░░░░|██░░░░░░|██░░░░░░|
            ──────────────────────────────→
            交替切换；同一时刻只有 1 个在跑

并行（多核 / 真同时）：
  Core-1:   |████████████████████████████|
  Core-2:   |████████████████████████████|
            ──────────────────────────────→
            真正同时
```

#### 图 3：CPU 视角

```text
[1 核 CPU]
  └─ 只能并发：调度器切换线程，CPU 利用率高，但同一时刻只跑 1 个
  └─ 你创建 100 个线程 = 100 个轮流等

[4 核 CPU]
  └─ 可并行：4 个线程真同时跑（理论 4 倍）
  └─ 但 100 个线程仍要时分复用，仍是「并发 + 部分并行」混合
```

### 1.4 4 维度对比表（核心考点）

| 维度 | 并发 (Concurrency) | 并行 (Parallelism) |
|------|------------------|-------------------|
| **核心问题** | 多个任务如何**交替**推进 | 多个任务如何**同时**执行 |
| **硬件要求** | 单核即可 | 必须多核 |
| **关注点** | 任务**调度**（deal with） | 任务**执行**（do） |
| **典型场景** | Node.js 单线程事件循环 | 多核 CPU 上的 goroutine |
| **Java 实战** | CompletableFuture 异步编排 | parallelStream / ForkJoinPool |
| **提速原理** | 提高 CPU 利用率（IO 等待时切别的） | 真减少总执行时间（分核跑） |
| **可以独立吗** | ✅ 单核也能并发 | ❌ 没多核就无法并行 |

---

## 二、6 大常见误区（必背）

| # | 误区 | 真相 |
|---|------|------|
| 1 | ❌ **"多线程 = 并行"** | 错！多线程在单核上只是并发，OS 时间片切换 |
| 2 | ❌ **"并发 = 性能更好"** | 错！CPU 密集型反而需要并行才能榨干多核 |
| 3 | ❌ **"异步 = 并发"** | 对！异步是并发的一种实现方式（Node.js / Goroutine / coroutine） |
| 4 | ❌ **"并行一定比串行快"** | 错！Amdahl 定律：并行加速比 = 1/(1-p + p/n)，有上限 |
| 5 | ❌ **"go func() 就是并行"** | 错！GOMAXPROCS=1 时只是并发（Go runtime 层面调度） |
| 6 | ❌ **"硬件 SIMD 也是并行"** | 是，但与应用层线程并行不同（一条指令多个数据） |

---

## 三、CPU-bound vs IO-bound 选型矩阵

| 任务类型 | 推荐模型 | 选型理由 |
|---------|---------|---------|
| **IO 密集**（网络请求、磁盘读写） | **并发**（多线程 / async）| CPU 等 IO 时可切别的任务，单核并发就够了 |
| **CPU 密集**（计算 / 加密 / 压缩）| **并行**（ForkJoinPool / 多进程）| 多核真同时跑才能榨干硬件 |
| **IO + CPU 混合** | **分层**（异步 IO + ForkJoinPool 并行计算）| 各层用最适合的模型 |
| **高并发低延迟**（10 万 QPS）| **异步 + 单线程 reactor**（Netty / Node.js）| 避免线程切换开销 |
| **CPU 极高吞吐**（离线批处理）| **并行 + ForkJoin**（parallelStream）| 榨干多核 |

### 实战案例

```java
// === IO 密集：用并发（CompletableFuture）===
CompletableFuture<String> userFuture  = CompletableFuture.supplyAsync(() -> fetchUser());
CompletableFuture<String> orderFuture = CompletableFuture.supplyAsync(() -> fetchOrders());
// 两个 IO 并发跑，节省总时间（CPU 在等 IO）

// === CPU 密集：用并行（parallelStream）===
List<Integer> result = hugeList.parallelStream()
    .map(this::heavyCompute)
    .collect(toList());
// 多核真同时算，加速比 ≈ 核数（受 Amdahl 限制）
```

---

## 四、5 大语言 / 模型的并发 vs 并行模式

| 语言 / 模型 | 并发实现 | 并行实现 | 默认行为 |
|------------|---------|---------|---------|
| **Java** | Thread / Executor / CompletableFuture | parallelStream / ForkJoinPool | 多线程（OS 调度）|
| **Go** | goroutine + channel | GOMAXPROCS 决定并行度 | GOMAXPROCS = NumCPU（自动并行）|
| **Erlang/Elixir** | process（轻量）| 多调度器 | 跨核自动并行 |
| **Node.js** | async/await 事件循环 | worker_threads / cluster | 单线程事件循环（默认）|
| **Rust** | tokio async | rayon（data-parallel）| 默认单线程 + async |
| **Python** | asyncio | multiprocessing | GIL 限制，单线程并发 |

---

## 五、面试话术（90 秒版本）

### 题目：并发和并行的区别？

**高分答案（4 层递进，60-90 秒）**：

```
1. 一句话（10 秒）：
   "Concurrency 是结构——同一时间段处理多个任务；
    Parallelism 是执行——同一时刻多个任务真在跑。
    Rob Pike 名言。"

2. 3 张图速览（30 秒）：
   "3 张经典图：
   ① 咖啡店比喻：1 个咖啡师轮流做 5 杯 vs 5 个咖啡师各做 1 杯
   ② 时序图：并发是时分复用 (Thread-A|B 交替)，
             并行是真同时 (Core-1|Core-2 同时)
   ③ CPU 视角：单核只能并发；多核才能并行"

3. 6 大误区（30 秒）：
   "6 大误区：
   ① 多线程 ≠ 并行（单核只是并发）
   ② 并发 ≠ 性能更好（CPU 密集型反而要并行）
   ③ 异步是并发的一种实现
   ④ 并行加速受 Amdahl 定律限制（理论 < 1/(1-p)）
   ⑤ Goroutine 默认 GOMAXPROCS = NumCPU 时并行；=1 时只并发
   ⑥ 硬件 SIMD 也是并行（指令级并行）"

4. 选型视角（20 秒）：
   "实战选型：
   - IO 密集 → 并发（async / NIO）
   - CPU 密集 → 并行（ForkJoinPool / multiprocessing）
   - 反例：把 IO 密集用 ForkJoinPool = 浪费线程切换
   - 反例：把 CPU 密集用单线程 reactor = 浪费多核
   - 实战原则：先识别任务类型，再选并发模型"
```

---

## 六、面试反问（让候选人反客为主）

```
Q1：贵司的并发模型用哪个？（reactor / proactor / actor）
    → reactor（事件循环）+ worker pool = 大厂常见
Q2：贵司 CPU 密集任务怎么处理？
    → ForkJoinPool / parallelStream / 独立计算集群
Q3：贵司如何选 GOMAXPROCS？
    → 默认 NumCPU；容器内要看 cgroup 限制
Q4：贵司做压测时怎么发现并行瓶颈？
    → Thread dump + flame graph + 阿姆达尔定律分析
Q5：贵司用协程/虚拟线程替代线程池？
    → Java 21 虚拟线程 / Go goroutine / Kotlin coroutine
```

---

## 🔗 系列导航表（13.split-hairs · 01.java 兄弟）

| 章节 | 核心考点 | 频率 |
|------|---------|------|
| [aqs](../aqs/README.md) | AQS 同步器原理 | ⭐⭐⭐⭐⭐ |
| [arrayList-distinct](../arrayList-distinct/README.md) | ArrayList 去重陷阱 | ⭐⭐⭐ |
| [class-loading](../class-loading/README.md) | 类加载机制 | ⭐⭐⭐⭐⭐ |
| [completable-future](../completable-future/README.md) | CompletableFuture 实战 | ⭐⭐⭐⭐ |
| [concurrent-hashmap](../concurrent-hashmap/README.md) | ConcurrentHashMap 演进 | ⭐⭐⭐⭐⭐ |
| [cpu-spike-troubleshooting](../cpu-spike-troubleshooting/README.md) | CPU 飙高排查 | ⭐⭐⭐⭐ |
| [gc-algorithms](../gc-algorithms/README.md) | GC 算法 | ⭐⭐⭐⭐⭐ |
| [hashmap-resizing](../hashmap-resizing/README.md) | HashMap 扩容 | ⭐⭐⭐⭐ |
| [jvm-memory](../jvm-memory/README.md) | JVM 内存模型 | ⭐⭐⭐⭐⭐ |
| [synchronized-lock-upgrade](../synchronized-lock-upgrade/README.md) | synchronized 锁升级 | ⭐⭐⭐⭐⭐ |
| [thread-pool](../thread-pool/README.md) | 线程池 7 大参数 + 4 拒绝策略 | ⭐⭐⭐⭐⭐ |
| [threadlocal](../threadlocal/README.md) | ThreadLocal 原理与内存泄漏 | ⭐⭐⭐⭐⭐ |
| [virtual-threads](../virtual-threads/README.md) | 虚拟线程（Java 21） | ⭐⭐⭐⭐ |
| **concurrency-vs-parallelism**（本篇）| Rob Pike 定义 + 6 大误区 + 90 秒话术 | ⭐⭐⭐ |

## 🔗 深度版（主模块）

- [01.java · Java 并发编程专题导航 第 1.3 节深展](../../../01.java/concurrency/README.md#一三-并发与并行深度展开rob-pike-详解--java-实战) — Rob Pike 5 张图详解 + Go 比喻 + 6 大误区清单 + Java ForkJoinPool / CompletableFuture 实战

---

> 📅 2026-07-13 · 咬文嚼字 · 01.java · ⭐⭐⭐ · Rob Pike + 6 大误区 + 5 语言对照 + CPU/IO 选型矩阵 + 90 秒话术 + 14 兄弟导航

← [返回: 咬文嚼字 · 01.java](../README.md)
