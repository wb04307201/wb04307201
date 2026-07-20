<!--
module:
  parent: java
  slug: java/version
  type: article
  category: 主模块子文章
  summary: 追踪 Java 语言与平台的演进脉络，从功能变更历史到各版本新特性，全面掌握 Java 的发展轨迹。
-->

# Java 版本特性

> 追踪 Java 语言与平台的演进脉络，从功能变更历史到各版本新特性，全面掌握 Java 的发展轨迹。

---
## 引言：变更说明

Java 版本特性 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 目录导航

### 功能变更历史

按语言特性维度纵向梳理 Java 的演进，适合理解某个特性是如何一步步发展而来的。

#### 语言特性

| 序号 | 主题 | 说明 |
|------|------|------|
| 1 | [Lambda](lambda/) | 函数式编程：从匿名内部类到 Lambda 表达式（Java 8） |
| 2 | [Switch](switch/) | 从 switch 语句到 switch 表达式，支持模式匹配（Java 12 预览） |
| 3 | [instanceof](instanceof/) | 模式匹配：类型检查 + 变量绑定一步完成（Java 14 预览） |
| 4 | [Text Blocks](text-blocks/) | 多行文本块，简化字符串拼接（Java 13 预览） |
| 5 | [Record](record/) | 不可变数据载体类，自动生成 equals/hashCode/toString（Java 14 预览） |
| 6 | [Sealed Classes](sealed-classes/) | 密封类：显式声明允许继承的子类（Java 15 预览） |

#### 集合与流

| 序号 | 主题 | 说明 |
|------|------|------|
| 7 | [Stream API](stream-api/) | 声明式数据处理管道：filter/map/reduce（Java 8） |
| 8 | [Optional](optional/) | 优雅处理可能为空的值，减少 NullPointerException（Java 8） |

#### 并发模型

| 序号 | 主题 | 说明 |
|------|------|------|
| 9 | [并发](concurrency/) | 锁机制、线程池、虚拟线程等并发特性演进（Java 5+） |
|  | &emsp;└ [CHMRLock](https://gitee.com/wb04307201/CHMRLock) | 基于 ConcurrentHashMap + ReentrantLock 的锁实现（开源项目） |

#### JVM & 内存

| 序号 | 主题 | 说明 |
|------|------|------|
| 10 | [垃圾回收](gc/) | GC 算法演进：Serial → Parallel → CMS → G1 → ZGC → Shenandoah |
| 11 | [VarHandle](var-handle/) | 替代 Unsafe 的底层变量访问与原子操作 API（Java 9） |
| 12 | [Foreign Function & Memory API](ffi-api/) | 替代 JNI 的外部函数调用与堆外内存管理（Java 19 预览） |

#### 平台工具

| 序号 | 主题 | 说明 |
|------|------|------|
| 13 | [HTTP Client](http-client/) | 支持 HTTP/1.1、HTTP/2、WebSocket 的现代客户端（Java 9 预览） |
| 14 | [类文件 API](class-file-api/) | 标准化的 `.class` 文件解析、转换与生成（Java 22 预览） |
| 15 | [Vector API](vector-api/) | SIMD 向量化计算，利用硬件加速数值运算（Java 16 孵化） |

### 各版本特性

按版本号横向整理每个版本的 JEP 列表与核心变化。

| 版本 | LTS | 亮点 |
|------|-----|------|
| [Java 8](java-8/) | ✅ | Lambda、Stream API、新日期时间 API |
| [Java 9](java-9/) | | 模块系统（JPMS）、JShell、Reactive Streams |
| [Java 10](java-10/) | | 局部变量类型推断（`var`） |
| [Java 11](java-11/) | ✅ | HTTP Client 正式版、单文件运行 |
| [Java 12](java-12/) | | Switch 表达式预览、G1 ZGC |
| [Java 13](java-13/) | | Text Blocks 预览 |
| [Java 14](java-14/) | | Record 预览、instanceof 模式匹配预览 |
| [Java 15](java-15/) | | Sealed Classes 预览、Text Blocks 正式版 |
| [Java 16](java-16/) | | Record 正式版、新 JIT 编译器 |
| [Java 17](java-17/) | ✅ | Sealed Classes 正式版、强封装 JDK 内部 API |
| [Java 18](java-18/) | | UTF-8 默认编码、简单 Web 服务器 |
| [Java 19](java-19/) | | 虚拟线程预览、结构化并发 |
| [Java 20](java-20/) | | Scoped Values 预览、Record Patterns |
| [Java 21](java-21/) | ✅ | 虚拟线程正式版、Sequenced Collections |
| [Java 22](java-22/) | | 字符串模板预览、未命名变量 `_` |
| [Java 23](java-23/) | | 结构化并发预览、隐式声明的类 |
| [Java 24](java-24/) | | Stream Gatherers、类文件 API 正式版 |
| [Java 25](java-25/) | ✅ | 紧凑对象头、灵活方法体、主内存模型 |
| [Java 26](java-26/) | | 持续演进中 |

---

## 知识图谱

```text
版本特性 (version)
├── 功能变更历史
│   ├── 语言特性: Lambda / Switch / instanceof / Text Blocks / Record / Sealed Classes
│   ├── 集合与流: Stream API / Optional
│   ├── 并发模型: 锁机制 / 线程池 / 虚拟线程 / 结构化并发
│   ├── JVM & 内存: GC 演进 / VarHandle / FFM API
│   └── 平台工具: HTTP Client / 类文件 API / Vector API
│
└── 各版本特性 (java-8 ~ java-26)
    └── 每版本 JEP 列表与核心变化总结
```

---

## 📊 本节统计

| 统计维度 | 数值 | 口径 |
|----------|------|------|
| 分类主题数 | 2 | 功能变更历史（15 个特性专题，5 大分类）/ 各版本特性（Java 8 ~ 26 共 19 个版本子目录） |
| 子 README 数 | 35 | 功能变更历史（16 个 leaf）+ 各版本（java-8 ~ java-26 共 19 个 leaf） |
| 含 frontmatter 的 README | 36 / 36 | 100% 覆盖（2026-07-16） |

> **统计时间戳**：2026-07-01

---

← [返回 01.java 主模块](../README.md)
