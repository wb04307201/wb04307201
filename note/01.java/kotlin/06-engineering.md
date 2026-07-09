<!--
module:
  parent: java
  slug: java/kotlin/engineering
  type: article
  category: 主模块子文章
  summary: Kotlin 工程实践——Java 互操作、构建工具、迁移策略与 KMP 配置。
-->

# Kotlin 工程实践

## 一、Java 互操作

Kotlin 与 Java 100% 互操作，但需注意空安全和命名约定。

### 常用互操作注解

| 注解 | 作用 |
|------|------|
| `@JvmStatic` | 将 `companion object` 成员编译为 Java 静态方法 |
| `@JvmField` | 将 Kotlin 属性暴露为 Java 字段（无 getter/setter） |
| `@JvmOverloads` | 为带默认参数的函数生成多个 Java 重载 |
| `@JvmName` | 改变 Kotlin 函数在 Java 中的可见名称 |
| `@file:JvmName("Utils")` | 改变 Kotlin 文件生成的 Java 类名 |

```kotlin
class Config {
    companion object {
        @JvmStatic
        fun getInstance() = Config()

        @JvmField
        val VERSION = "1.0.0"
    }
}

// Java 调用：Config.getInstance() 和 Config.VERSION
```

### 默认参数与 Java 重载

Kotlin 的默认参数在 Java 中不可见，需加 `@JvmOverloads` 生成重载。

```kotlin
@JvmOverloads
fun greet(name: String = "World", times: Int = 1) { ... }
// Java 可调用：greet()、greet("X")、greet("X", 3)
```

## 二、Kotlin Multiplatform (KMP)

KMP 允许在 JVM、JS、Native（iOS/macOS/Linux/Windows）间共享业务逻辑，不替代 UI 层。

### Expect / Actual 机制

在 common 模块声明平台相关行为，在各平台模块实现。

```kotlin
// commonMain — 声明
expect fun platformName(): String
expect class PlatformStorage {
    fun getString(key: String): String?
    fun setString(key: String, value: String)
}

// jvmMain — 实现
actual fun platformName() = "JVM: ${System.getProperty("os.name")}"
actual class PlatformStorage {
    private val map = mutableMapOf<String, String>()
    actual fun getString(key: String) = map[key]
    actual fun setString(key: String, value: String) { map[key] = value }
}

// iosMain — 实现
actual fun platformName() = "iOS: ${UIDevice.currentDevice.systemName}"
actual class PlatformStorage { /* 使用 NSUserDefaults 实现 */ }
```

> **定位**：KMP 共享的是**业务逻辑**（网络、数据模型、算法），不是 UI。UI 仍用原生方案或 Compose Multiplatform。

## 三、构建工具

### Gradle Kotlin DSL

```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm") version "2.0.0"
    application
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")
    testImplementation(kotlin("test"))
}

kotlin {
    jvmToolchain(17)
}
```

### KSP vs kapt

- **kapt**：通过 Java Annotation Processing 处理 Kotlin 注解，速度慢
- **KSP（Kotlin Symbol Processing）**：Kotlin 原生编译期 API，比 kapt 快 2-3 倍，推荐新项目使用

### K2 编译器（Kotlin 2.0+）

新前端重写，带来：更快的编译速度、更精确的类型推断、更好的 IDE 支持、多平台统一。

## 四、从 Java 迁移的策略

1. **同一项目共存**：Kotlin 和 Java 可在同一 Gradle/Maven 项目中编译，互相调用
2. **新建文件用 Kotlin**：新功能用 Kotlin 编写，旧代码保持 Java
3. **自动转换**：IntelliJ 的 `Code → Convert Java File to Kotlin` 可一键转换
4. **处理平台类型**：转换后检查所有从 Java 返回的可空类型，显式加 `?`
5. **逐步重构**：将工具类改为扩展函数，将回调改为协程，将 Builder 改为 `apply`

> **警告**：自动转换产生的代码通常不够地道（如仍用 `!!` 而非 `?`）。转换后需手动优化。

## 五、构建工具对比

Kotlin 项目可选三种构建工具，各有适用场景：

| 维度 | Gradle Kotlin DSL (`.kts`) | Gradle Groovy DSL (`.gradle`) | Maven (`pom.xml`) |
|------|---------------------------|-------------------------------|-------------------|
| 类型安全 | ✅ 编译期检查，配置错误即时发现 | ❌ 运行时才暴露 | ❌ XML 无类型检查 |
| IDE 支持 | ✅ 自动补全 + 跳转定义 | ⚠️ 基本补全，偶有失效 | ✅ 成熟稳定 |
| 学习曲线 | ⚠️ 需熟悉 Kotlin 语法 + Gradle API | ✅ Groovy 语法宽松 | ⚠️ XML 冗长但约定明确 |
| 构建速度 | ⚠️ 首次编译慢，增量编译快 | ✅ 配置阶段略快 | ✅ 稳定但多模块慢 |
| Kotlin 生态 | ✅ JetBrains 官方推荐 | ⚠️ 社区逐步迁移 | ❌ Kotlin 插件支持有限 |
| 多平台(KMP) | ✅ 原生支持 `kotlin { ... }` DSL | ⚠️ 语法兼容但不推荐 | ❌ 不支持 |

**推荐策略**：
- **新项目**：Gradle Kotlin DSL — 类型安全 + 官方文档全部使用 `.kts`
- **已有 Maven 项目**：不必为 Kotlin 迁移构建工具，Maven + kotlin-maven-plugin 足够
- **已有 Gradle Groovy**：可渐进迁移到 Kotlin DSL，或保持 Groovy（功能无差异）

## 六、KMP (Kotlin Multiplatform) 实战配置

以下是一个典型的 KMP 项目 `build.gradle.kts`，覆盖 JVM、JS、iOS 三个目标平台：

```kotlin
// build.gradle.kts
plugins {
    kotlin("multiplatform") version "2.0.0"
    kotlin("plugin.serialization") version "2.0.0"
}

kotlin {
    // 声明目标平台
    jvm()
    js(IR) {
        browser()
        nodejs()
    }
    iosX64()
    iosArm64()
    iosSimulatorArm64()

    // 配置各 sourceSet 的依赖
    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")
                implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.3")
                implementation("io.ktor:ktor-client-core:2.3.9")
            }
        }
        val commonTest by getting {
            dependencies {
                implementation(kotlin("test"))
            }
        }
        val jvmMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-okhttp:2.3.9")
            }
        }
        val jsMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-js:2.3.9")
            }
        }
        // iOS 共享 sourceSet（2.0+ 推荐 default hierarchy）
        val iosMain by creating {
            dependsOn(commonMain)
            dependencies {
                implementation("io.ktor:ktor-client-darwin:2.3.9")
            }
        }
        val iosX64Main by getting { dependsOn(iosMain) }
        val iosArm64Main by getting { dependsOn(iosMain) }
        val iosSimulatorArm64Main by getting { dependsOn(iosMain) }
    }
}
```

> **提示**：Kotlin 2.0+ 的 **Default Hierarchy Template** 会自动创建 `iosMain` 等中间 sourceSet，通常无需手动 `creating`。使用 `kotlin { applyDefaultHierarchyTemplate() }` 即可简化配置。

## 七、Java → Kotlin 迁移策略

### 渐进式迁移五步法

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 配置双语言编译 | Gradle 中同时启用 `java` + `kotlin` 插件，Java 和 Kotlin 文件共存 |
| 2 | 新功能用 Kotlin | 新模块、新类用 Kotlin 编写，旧代码暂不动 |
| 3 | 逐文件转换 | IntelliJ `Code → Convert Java File to Kotlin File` 转换工具类和数据类 |
| 4 | 处理平台类型 | 检查所有从 Java 方法返回的平台类型（`String!`），显式标注 `?` 或 `!!` |
| 5 | Kotlin 化重构 | 工具类 → 扩展函数，回调 → 协程，Builder → `apply`/`buildUpon` |

### 迁移三大陷阱

**陷阱 1：平台类型的空安全盲区**

Java 方法的返回类型在 Kotlin 中是"平台类型"（`String!`），编译器不做空安全检查：

```kotlin
// ❌ Java 方法可能返回 null，但 Kotlin 当作非空使用
val user: String = javaService.findUser(id) // 编译通过，运行时 NPE！

// ✅ 显式标注可空类型，强制安全处理
val user: String? = javaService.findUser(id)
val name = user ?: "unknown"
```

**陷阱 2：扩展函数与成员函数同名冲突**

Kotlin 中成员函数优先级高于扩展函数，迁移时可能意外覆盖行为：

```kotlin
// Java 工具类
// StringUtils.isEmpty(str) → 迁移为扩展函数

fun String.isEmpty(): Boolean = this.length == 0  // ❌ 与 kotlin.String 内置冲突

// ✅ 使用不同名称或限定作用域
fun String.isBlank(): Boolean = this.trim().isEmpty()
```

**陷阱 3：SAM 转换差异**

Java 的 SAM（Single Abstract Method）接口在 Kotlin 中可用 Lambda，但行为有细微差异：

```java
// Java
executor.submit(() -> doWork());  // 每次创建新实例
```

```kotlin
// ❌ 误以为 Kotlin Lambda 和 Java Lambda 完全等价
executor.submit(Runnable { doWork() })  // ✅ 正确：显式 SAM 构造

// 注意：Kotlin 函数类型不能直接传给 Java 的 SAM 接口
// 需要用 Runnable { ... } 或 object : Runnable { ... } 包装
```

## 八、常见陷阱

### 陷阱 1：`!!` 强制非空断言滥用

```kotlin
// ❌ 强制非空 → 运行时 NullPointerException
val name: String = user!!.name!!

// ✅ 安全调用 + Elvis 提供默认值
val name: String = user?.name ?: "unknown"

// ✅ 确定非空时用 require 提前断言，使失败点更明确
requireNotNull(user) { "user must not be null" }
val name = user.name
```

### 陷阱 2：混淆 `List` 与 `Array`

```kotlin
// ❌ 误用 Array（主要用于 Java 互操作和 varargs）
val items: Array<String> = arrayOf("a", "b")
items[0] = "c"  // 可变，绕过了不可变集合的保护

// ✅ 日常开发使用 List / MutableList
val items: List<String> = listOf("a", "b")          // 不可变
val mutable: MutableList<String> = mutableListOf("a", "b")  // 明确可变
```

### 陷阱 3：`data class` 的 `equals()` 只比较主构造函数属性

```kotlin
// ❌ age 不在主构造函数中，不参与 equals 比较
data class User(val name: String) {
    var age: Int = 0
}
val u1 = User("Tom").apply { age = 20 }
val u2 = User("Tom").apply { age = 30 }
println(u1 == u2)  // true！age 被忽略

// ✅ 将影响相等性判断的字段放入主构造函数
data class User(val name: String, val age: Int)
```

### 陷阱 4：扩展函数的静态分派

```kotlin
open class Base
class Derived : Base()

fun Base.greet() = "Hello from Base"
fun Derived.greet() = "Hello from Derived"

val obj: Base = Derived()
// ❌ 期望调用 Derived 版本，实际调用 Base 版本
println(obj.greet())  // "Hello from Base" — 扩展函数基于声明类型分派

// ✅ 如需多态行为，使用成员函数而非扩展函数
open class Base { open fun greet() = "Hello from Base" }
class Derived : Base() { override fun greet() = "Hello from Derived" }
```

> **总结**：扩展函数是**静态解析**的（编译时根据变量声明类型决定），成员函数是**动态分派**的（运行时根据实际类型决定）。这是 Kotlin 新手最常踩的坑之一。

---

## 相关章节

- ⬅️ [返回 Kotlin 目录](README.md)
- [01 基础语法](01-basics.md) — 空安全、类型系统、控制流基础
- [02 面向对象](02-oop.md) — data class、sealed class、泛型
- [03 函数式](03-functional.md) — 集合操作、作用域函数、Sequence
- [04 高级特性](04-advanced.md) — 扩展函数、委托、内联、值类
- [05 协程与异步](05-coroutines.md) — 协程、Flow、Channel、结构化并发

← [返回: Kotlin](README.md)
