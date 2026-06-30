# 垃圾回收

## 引言：性能对比（[AUTO] 自动生成，待人工 review）

垃圾回收 的垃圾回收（Garbage Collection, GC）是 Java 虚拟机自动管理内存的核心机制。JDK 提供了多种垃圾收集器以适应不同场景：Serial（单线程）、Parallel（吞吐量优先）、G1（平衡吞吐量和延迟）、ZGC（亚毫秒

**但实际**：常被问起'为什么我的版本慢 10 倍'、'怎么排查'。本篇用'对比数字'切入，把'常见 vs 极端'两种场景拆给你看。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---


## 功能描述

垃圾回收（Garbage Collection, GC）是 Java 虚拟机自动管理内存的核心机制。JDK 提供了多种垃圾收集器以适应不同场景：Serial（单线程）、Parallel（吞吐量优先）、G1（平衡吞吐量和延迟）、ZGC（亚毫秒级延迟）、Shenandoah（低停顿）、Epsilon（无操作，用于测试）。从 Java 21 起，分代式 ZGC 成为现代应用的首选。

## 基本用法（JVM 配置，Java 26+）

```bash
# 1. 使用 G1 GC（Java 9+ 默认）
java -XX:+UseG1GC -Xmx4g -Xms4g MyApp

# 2. 使用 ZGC（推荐，Java 23+ 默认分代模式）
java -XX:+UseZGC -Xmx16g MyApp

# 3. 使用 Shenandoah GC
java -XX:+UseShenandoahGC -Xmx16g MyApp

# 4. 使用 Parallel GC（吞吐量优先场景）
java -XX:+UseParallelGC -Xmx4g MyApp

# 5. 使用 Epsilon GC（性能测试，不做 GC）
java -XX:+UseEpsilonGC -Xmx1g MyApp

# 6. GC 日志配置（Java 9+ 统一格式）
java -Xlog:gc*:file=gc.log:time,uptime,level,tags:filecount=5,filesize=10M MyApp

# 7. G1 目标停顿时间配置
java -XX:+UseG1GC -XX:MaxGCPauseMillis=200 MyApp

# 8. ZGC 详细日志
java -XX:+UseZGC -Xlog:gc*=debug MyApp
```

## 变更历史表

| Java版本  | 新特性/增强内容                                     |
|---------|----------------------------------------------|
| Java 26 | JEP 522: G1 GC 通过减少同步来提高吞吐量                     |
| Java 25 | JEP 519: 紧凑对象头 - 减少对象头大小从 12 字节到 8 字节        |
| Java 24 | JEP 490: ZGC 移除非分代模式，专注于分代收集               |
| Java 24 | JEP 404: 分代式 Shenandoah（实验性）                   |
| Java 23 | JEP 474: ZGC 分代模式成为默认                          |
| Java 21 | JEP 439: 分代式 ZGC                                 |
| Java 16 | JEP 387: 弹性元空间                                |
| Java 16 | JEP 376: ZGC 并发线程栈处理                          |
| Java 15 | JEP 377: ZGC 转正为生产就绪功能                       |
| Java 14 | JEP 363: 移除 CMS 垃圾收集器                         |
| Java 12 | JEP 189: Shenandoah 垃圾收集器（实验性）               |
| Java 12 | JEP 344/346: G1 可中止混合收集、及时返回未使用内存           |
| Java 11 | JEP 318: Epsilon 垃圾回收器（实验性）                  |
| Java 11 | JEP 333: ZGC（实验性）                              |
| Java 10 | JEP 307: G1 的并行全垃圾回收                          |
| Java 9  | JEP 248: G1 成为默认垃圾收集器                        |
| Java 9  | JEP 271: 统一 GC 日志格式                             |
| Java 8  | JEP 173: 移除很少使用的垃圾回收器组合                     |
| Java 7  | 引入 G1（Garbage-First）垃圾收集器（实验性）               |
| Java 6  | 引入 Parallel Old 收集器                             |
| Java 5  | 引入 CMS（Concurrent Mark Sweep）收集器            |
| Java 4  | 引入 Parallel Scavenge 收集器                         |
| Java 2  | 引入分代垃圾回收概念                                    |
| Java 1  | 引入 Serial 垃圾收集器                                |

## 功能详细介绍

### 1. Java 1 - Serial GC

Java 最初内置的垃圾收集器，单线程执行，采用标记-整理算法。适用于小型应用和客户端场景。

### 2. Java 2 - 分代 GC 概念

引入分代垃圾回收概念，将堆分为年轻代和老年代，针对对象生命周期特征采用不同策略。

### 3. Java 4 - Parallel Scavenge

多线程并行处理新生代垃圾回收，专注于最大化吞吐量。

### 4. Java 5 - CMS 收集器

Concurrent Mark Sweep 收集器，以最短停顿时间为目标，大部分工作与应用程序线程并发执行。

### 5. Java 6 - Parallel Old

Parallel Scavenge 的老年代版本，使用并行标记-整理算法，形成完整的并行收集器组合。

### 6. Java 7 - G1 收集器（实验性）

将堆划分为多个 Region，优先回收垃圾最多的区域，提供可预测的停顿时间模型。

### 7. Java 9 - G1 成为默认 (JEP 248)

G1 取代 Parallel GC 成为默认收集器，同时统一 GC 日志格式（JEP 271），使用 `-Xlog:gc*` 替代旧的 `-XX:+PrintGCDetails`。

### 8. Java 11 - ZGC 和 Epsilon

- **ZGC（JEP 333）**：新一代低延迟收集器，目标停顿时间 < 10ms，支持 TB 级堆
- **Epsilon（JEP 318）**：无操作收集器，分配内存但不回收，用于性能基准测试

### 9. Java 12 - Shenandoah（实验性）

Red Hat 开发的低延迟收集器，使用 Brooks Pointers 实现并发压缩，停顿时间与堆大小无关。

### 10. Java 14 - 移除 CMS

CMS 收集器正式移除，推荐使用 G1 或 ZGC 替代。

### 11. Java 15 - ZGC 转正

ZGC 从实验性转为生产就绪。

### 12. Java 21 - 分代式 ZGC (JEP 439)

引入分代式 ZGC，结合分代回收和 ZGC 的并发标记优势，显著提升吞吐量。

### 13. Java 23 - ZGC 分代模式成为默认 (JEP 474)

`-XX:+UseZGC` 自动启用分代收集，不再需要额外的 `-XX:+ZGenerational` 参数。

### 14. Java 24 - ZGC 移除非分代模式

非分代 ZGC 完全移除，ZGC 只保留分代模式。同时引入分代式 Shenandoah 作为实验性功能。

### 15. Java 25 - 紧凑对象头 (JEP 519)

通过减少对象头大小（从 12 字节到 8 字节），节省约 22% 堆使用，降低 GC 频率约 15%。

### 16. Java 26 - G1 GC 减少同步 (JEP 522)

通过减少 G1 写屏障中的同步操作和内部锁的使用，提高了 G1 垃圾回收器的吞吐量。优化了 G1 写屏障指令的数量，减少了并发标记过程中的锁竞争，使多线程环境下应用程序性能得到提升。

## 垃圾收集器对比

| 收集器       | 停顿时间     | 吞吐量  | 适用场景                 |
|-----------|----------|------|----------------------|
| Serial    | 高        | 中    | 小型应用、客户端             |
| Parallel  | 中        | 高    | 批处理、数据管道             |
| G1        | 可配置（中等） | 中高  | 通用服务端应用（默认）          |
| ZGC       | < 1ms   | 中    | 低延迟服务端、大堆（TB 级）     |
| Shenandoah| < 10ms  | 中    | 低延迟、超大堆              |
| Epsilon   | N/A     | 最高* | 性能测试、极短生命周期应用        |

## 最佳实践

1. **默认选择**：Java 21+ 应用优先使用 ZGC（`-XX:+UseZGC`），大堆应用收益明显
2. **兼容性**：需要 JDK 兼容性的场景使用 G1
3. **GC 日志**：始终启用 GC 日志便于问题排查
4. **避免过度调优**：大多数场景下默认配置已经足够，仅在性能瓶颈时才深入调优

## 总结

Java GC 从单线程 Serial 演进到多收集器并存，再到 ZGC 实现亚毫秒级停顿。Java 24+ 时代，ZGC 分代模式已成为生产环境的首选，紧凑对象头（Java 25）进一步优化了内存效率，G1 GC 的同步优化（Java 26）提升了默认 GC 的吞吐量。
