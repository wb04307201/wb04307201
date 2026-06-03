# Kotlin 基础

## 一、变量声明

Kotlin 区分只读与可变变量，Java 通过 `final` 实现只读。

```kotlin
val name = "Kotlin"    // 只读，等价于 Java 的 final String name
var count = 0          // 可变，等价于 Java 的 int count
val inferred = 42      // 类型推断为 Int，无需显式声明
val explicit: Int = 42 // 显式类型
```

> **提示**：`val` 是引用不可变，不是深不可变。`val list = mutableListOf(1,2)` 仍可修改元素。

## 二、字符串模板

```java
// Java
String msg = "Hello, " + name + "! You are " + age + " years old.";
```

```kotlin
// Kotlin
val msg = "Hello, $name! You are $age years old."
val calc = "Result: ${2 + 3}"   // 支持表达式
```

## 三、空安全（Null Safety）

Kotlin 最具差异化的特性。Java 的 `null` 可导致运行时 NPE，Kotlin 在编译期拦截。

```java
// Java — 编译通过，运行时报 NPE
String str = null;
System.out.println(str.length());
```

```kotlin
// Kotlin — 编译期拦截
val str: String = null   // ❌ 编译错误：Null can not be a value of a non-null type String
```

### 可空类型与操作符

```kotlin
val name: String? = null

name?.length          // 安全调用：null 时返回 null
name?.length ?: 0     // Elvis 操作符：null 时提供默认值
name!!.length         // 非空断言：null 时抛 NPE（尽量避免）
name as? String       // 安全转换：失败返回 null 而非抛异常
```

### 平台类型

从 Java 代码返回的类型在 Kotlin 中视为**平台类型**（`String!`），可空性不确定。Kotlin 编译器不会强制检查，由开发者决定是否加 `?`。

> **最佳实践**：自己的 Kotlin 代码尽量用非空类型，只在真正需要 null 时才加 `?`。调用 Java 库时，对可能为 null 的返回值显式标注 `?`。

## 四、控制流

### `when` 表达式

Kotlin 的 `when` 替代 Java 的 `switch`，是表达式（有返回值），支持任意类型和复杂条件。

```java
// Java
String result;
switch (day) {
    case MONDAY:
    case FRIDAY:
        result = "busy";
        break;
    default:
        result = "normal";
}
```

```kotlin
// Kotlin
val result = when (day) {
    Day.MONDAY, Day.FRIDAY -> "busy"
    Day.SATURDAY, Day.SUNDAY -> "weekend"
    else -> "normal"    // 必须覆盖所有情况
}
```

`when` 还可不带参数，替代 `if-else if` 链：

```kotlin
val desc = when {
    x in 1..10 -> "small"
    x > 100 -> "large"
    else -> "medium"
}
```

### 区间与 `in`

```kotlin
for (i in 1..10) print(i)        // 1 到 10（闭区间）
for (i in 1 until 10) print(i)   // 1 到 9（左闭右开）
for (i in 10 downTo 1 step 2) print(i)  // 10, 8, 6, 4, 2

if (x in 1..100) println("in range")     // 范围检查
if (x !in 0..100) println("out of range")
```

### 标签跳转

Kotlin 支持带标签的 `return`/`break`/`continue`，替代 Java 的带标签 break。

```kotlin
loop@ for (i in 1..100) {
    for (j in 1..100) {
        if (condition) break@loop
    }
}
```

## 五、异常处理

### 无 Checked Exception

Kotlin 不区分 checked / unchecked 异常，所有异常都是运行时异常。设计理由：函数式组合时 checked exception 是障碍。

```java
// Java — 必须声明或捕获
public void read() throws IOException {
    Files.readAllLines(path);
}
```

```kotlin
// Kotlin — 无需声明
fun read() {
    Files.readAllLines(path)   // 不强制捕获，也不需 throws 声明
}
```

### `try` 作为表达式

```kotlin
val number = try {
    input.toInt()
} catch (e: NumberFormatException) {
    0    // 默认值
}
```

### `Nothing` 类型

`Nothing` 表示"永不返回"，用于 `throw` 表达式或无限循环。

```kotlin
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}
```
