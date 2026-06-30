# Kotlin

Kotlin 是由 JetBrains 设计的静态类型现代编程语言，运行于 JVM 之上。2016 年发布 v1.0，2017 年被 Google 宣布为 Android 开发首选语言，2019 年成为 JVM 默认语言。相比 Java，Kotlin 以空安全、协程、扩展函数、简洁语法等特性显著提升了开发效率与代码安全性。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

Kotlin 本应该很简单，Kotlin 是由 JetBrains 设计的静态类型现代编程语言，运行于 JVM 之上。2016 年发布 v1.0，2017 年被 Google 宣布为 Android 开发首选语言，2019 年成为 JVM 默认语言。相比 Java，K

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 文件导航

| 文件 | 内容 | 核心对比点 |
|------|------|-----------|
| [01-basics.md](01-basics.md) | 基础语法、类型系统、空安全、控制流、异常 | `val/var` vs `final`，空安全 vs NPE，`when` vs `switch` |
| [02-oop.md](02-oop.md) | 类与对象、泛型、继承、可见性 | `data class` vs `record`，`sealed` vs `sealed`，`out/in` vs `? extends/super` |
| [03-functional.md](03-functional.md) | 函数、集合、函数式、作用域函数 | 默认参数 vs 重载，`Sequence` vs `Stream`，作用域函数 vs 无 |
| [04-advanced.md](04-advanced.md) | 扩展、委托、操作符、内联、值类、DSL | 扩展函数 vs 工具类，`by lazy` vs 手动延迟，值类 vs 包装类 |
| [05-coroutines.md](05-coroutines.md) | 协程、Flow、Channel、结构化并发 | 协程 vs 线程，`Flow` vs Reactive Streams，`Channel` vs `BlockingQueue` |
| [06-engineering.md](06-engineering.md) | 互操作、KMP、构建工具、迁移策略 | `@JvmStatic` 互操作，`expect/actual`，Gradle KTS vs Groovy |

---

## Kotlin vs Java 核心差异总览

| 维度 | Java | Kotlin |
|------|------|--------|
| 空安全 | 运行时检查（NPE） | 编译期保证（`?` 类型系统） |
| 变量 | `final` / 可变 | `val` / `var`（类型推断） |
| 字符串 | `+` 拼接 / `String.format` | 模板 `"Hello, $name!"` |
| 数据载体 | `record`（Java 16+） | `data class`（自动生成 `equals/hashCode/toString/copy`） |
| 继承控制 | 默认非 `final` | 默认 `final`，`open` 才可继承 |
| 密封类型 | `sealed`（Java 17+） | `sealed class/interface`（配合 `when` 穷举） |
| 静态成员 | `static` | `companion object` + `@JvmStatic` |
| 单例 | 手动实现（双重检查等） | `object` 原生支持 |
| 异步编程 | 线程 / `CompletableFuture` | 协程（`launch`/`async`） / `Flow` |
| 扩展能力 | 工具类 / 继承 | 扩展函数 / 扩展属性 |
| 函数式 | Stream API（链式调用冗长） | 集合函数 + Lambda（`map { it * 2 }`） |
| Checked Exception | 强制声明或捕获 | 无 |
| `switch` | 有限类型，语句 | `when` 表达式，支持任意类型和条件 |
| 泛型 | 类型擦除，通配符 `? extends/super` | 声明处型变 `out/in` + `reified` |
| 延迟初始化 | 手动检查 null | `lateinit` / `by lazy` |
| 构建工具 | Maven / Gradle Groovy DSL | Gradle Kotlin DSL（`.kts`） |
| 跨平台 | JVM only | KMP（JVM / JS / Native / Android / iOS） |

---

## 推荐学习路径

从 Java 迁移到 Kotlin 的建议顺序：

1. **基础语法**（[01-basics](01-basics.md)）：`val/var`、空安全、`when` — 1-2 天即可上手
2. **面向对象**（[02-oop](02-oop.md)）：`data class`、`sealed`、`object` — 熟悉 Kotlin 的 OOP 风格
3. **函数式**（[03-functional](03-functional.md)）：集合操作、作用域函数 — 大幅减少样板代码
4. **高级特性**（[04-advanced](04-advanced.md)）：扩展函数、委托、内联 — 提升表达力
5. **协程**（[05-coroutines](05-coroutines.md)）：异步编程范式转变 — 重点投入
6. **工程实践**（[06-engineering.md](06-engineering.md)）：互操作、KMP、构建 — 实际项目所需

> **提示**：Kotlin 与 Java 可 100% 互操作，建议在现有项目中逐步替换，而非一次性迁移。新建文件用 Kotlin，旧代码保持 Java，逐步迁移。
