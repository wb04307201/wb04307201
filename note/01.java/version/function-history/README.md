<!--
module:
  parent: java
  slug: java/function-history
  type: article
  category: 主模块子文章
  summary: 功能版本变更历史
-->

# 功能版本变更历史

> 按语言特性维度纵向梳理 Java 各核心功能的演进历程，理解每个特性"为什么来"以及"怎么变"。

---
## 引言：变更说明

功能版本变更历史 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 目录导航

### 语言特性

| 主题 | 说明 | 引入版本 |
|------|------|----------|
| [Lambda](lambda/) | 函数式编程：从匿名内部类到 Lambda 表达式 | Java 8 |
| [Switch](switch/) | 从 switch 语句到 switch 表达式，支持模式匹配 | Java 12 预览 |
| [instanceof](instanceof/) | 模式匹配：类型检查 + 变量绑定一步完成 | Java 14 预览 |
| [Text Blocks](text-blocks/) | 多行文本块，简化字符串拼接 | Java 13 预览 |
| [Record](record/) | 不可变数据载体类，自动生成 equals/hashCode/toString | Java 14 预览 |
| [Sealed Classes](sealed-classes/) | 密封类：显式声明允许继承的子类 | Java 15 预览 |

### 集合与流

| 主题 | 说明 | 引入版本 |
|------|------|----------|
| [Stream API](stream-api/) | 声明式数据处理管道：filter/map/reduce | Java 8 |
| [Optional](optional/) | 优雅处理可能为空的值，减少 NullPointerException | Java 8 |

### 并发模型

| 主题 | 说明 | 引入版本 |
|------|------|----------|
| [并发](concurrency/) | Java 并发特性的演进全景 | Java 5+ |
| &emsp;├ [定义](concurrency/define/) | 并发编程基础定义 | |
| &emsp;│&emsp;├ [Java 锁机制](concurrency/define/java-locks/) | synchronized / ReentrantLock / StampedLock 等 | |
| &emsp;│&emsp;└ [线程池](concurrency/define/thread-pool/) | ExecutorService / ThreadPoolExecutor | |
| &emsp;└ [CHMRLock](https://gitee.com/wb04307201/CHMRLock) | 基于 ConcurrentHashMap + ReentrantLock 的锁实现（开源项目） | |

### JVM & 内存

| 主题 | 说明 | 引入版本 |
|------|------|----------|
| [垃圾回收](gc/) | GC 算法演进：Serial → Parallel → CMS → G1 → ZGC → Shenandoah | Java 1.0+ |
| [VarHandle](var-handle/) | 替代 Unsafe 的底层变量访问与原子操作 API | Java 9 |
| [Foreign Function & Memory API](ffi-api/) | 替代 JNI 的外部函数调用与堆外内存管理 | Java 19 预览 |

### 平台工具

| 主题 | 说明 | 引入版本 |
|------|------|----------|
| [HTTP Client](http-client/) | 支持 HTTP/1.1、HTTP/2、WebSocket 的现代客户端 | Java 9 预览 |
| [类文件 API](class-file-api/) | 标准化的 `.class` 文件解析、转换与生成 | Java 22 预览 |
| [Vector API](vector-api/) | SIMD 向量化计算，利用硬件加速数值运算 | Java 16 孵化 |

---

## 演进时间线

```
Java 8  (2014) ── Lambda / Stream / Optional
    │
Java 9  (2017) ── 模块系统 / VarHandle / HTTP Client 预览
    │
Java 11 (2018) ── HTTP Client 正式版
    │
Java 12 (2019) ── Switch 表达式预览
    │
Java 13 (2019) ── Text Blocks 预览
    │
Java 14 (2020) ── Record / instanceof 模式匹配 预览
    │
Java 15 (2020) ── Sealed Classes 预览 / Text Blocks 正式版
    │
Java 16 (2021) ── Record 正式版 / Vector API 孵化
    │
Java 17 (2021) ── Sealed Classes 正式版
    │
Java 19 (2022) ── FFM API 预览
    │
Java 21 (2023) ── 虚拟线程正式版
    │
Java 22 (2024) ── 类文件 API 预览
    │
Java 24 (2025) ── 类文件 API 正式版
    │
Java 25 (2025) ── 紧凑对象头 / 灵活方法体
```
