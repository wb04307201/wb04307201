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
