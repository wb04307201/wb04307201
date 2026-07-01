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

| 序号 | 主题 | 说明 |
|------|------|------|
| 1 | [垃圾回收](function-history/gc/) | GC 算法演进：Serial → Parallel → CMS → G1 → ZGC → Shenandoah |
| 2 | [Lambda](function-history/lambda/) | 函数式编程的引入与演进 |
| 3 | [Stream API](function-history/stream-api/) | 声明式数据处理管道 |
| 4 | [Optional](function-history/optional/) | 空值安全处理 |
| 5 | [Switch](function-history/switch/) | 从语句到表达式，模式匹配 |
| 6 | [instanceof](function-history/instanceof/) | 模式匹配与类型解构 |
| 7 | [并发](function-history/concurrency/) | 锁机制、线程池、虚拟线程等并发特性演进 |
| 8 | [类文件 API](function-history/class-file-api/) | 标准化的类文件解析与生成 |
| 9 | [HTTP Client](function-history/http-client/) | 现代 HTTP 客户端 API |
| 10 | [Foreign Function & Memory API](function-history/ffi-api/) | 替代 JNI 的外部函数与内存访问 |
| 11 | [Vector API](function-history/vector-api/) | SIMD 向量化计算 |
| 12 | [Sealed Classes](function-history/sealed-classes/) | 密封类：限制继承层次 |
| 13 | [Text Blocks](function-history/text-blocks/) | 多行文本块 |
| 14 | [VarHandle](function-history/var-handle/) | 底层变量访问与原子操作 |
| 15 | [Record](function-history/record/) | 不可变数据载体类 |

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

```
版本特性 (version)
├── 功能变更历史 (function-history)
│   ├── 语言特性: Lambda / Switch / instanceof / Text Blocks / Record / Sealed Classes
│   ├── 集合与流: Stream API / Optional / Sequenced Collections
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
| 分类主题数 | 2 | 功能变更历史（15 个特性专题）/ 各版本特性（Java 8 ~ 26 共 19 个版本子目录） |
| 子 README 数 | 38 | 含 function-history（17）/ java-8 ~ java-26（19）/ java-26 README 等深层 leaf |
| 含 frontmatter 的 README | 39 / 39 | 100% 覆盖（2026-07-01） |

> **统计时间戳**：2026-07-01

---

← [返回 01.java 主模块](../README.md)
