# Kotlin 高级特性

## 一、扩展函数与扩展属性

扩展函数为现有类添加方法，无需继承或工具类。

```java
// Java — 工具类
public class StringUtils {
    public static String lastChar(String s) {
        return s.substring(s.length() - 1);
    }
}
StringUtils.lastChar("hello");
```

```kotlin
// Kotlin — 扩展函数
fun String.lastChar(): Char = this[length - 1]
"hello".lastChar()    // 'o'，调用像原生方法
```

> **重要**：扩展函数是**静态解析**的，不支持多态。调用哪个扩展取决于声明类型而非运行时类型。不能覆盖成员方法。

扩展属性只能定义 getter/setter（无 backing field）：

```kotlin
val String.firstChar: Char get() = this[0]
```

## 二、委托（Delegation）

### 类级别委托

`by` 关键字自动将接口实现委托给指定对象，替代 Java 的手动委托模式。

```java
// Java — 手动委托
class PrinterService implements Printer {
    private final Printer delegate;
    PrinterService(Printer delegate) { this.delegate = delegate; }
    @Override public void print(String msg) { delegate.print(msg); }
}
```

```kotlin
// Kotlin — 一行
class PrinterService(private val delegate: Printer) : Printer by delegate
```

### 属性委托

```kotlin
// by lazy — 首次访问时计算，之后缓存（默认线程安全）
val database by lazy { Database.connect() }

// Delegates.observable — 属性变更监听
var name: String by Delegates.observable("<unset>") { prop, old, new ->
    println("$prop: $old -> $new")
}

// Delegates.vetoable — 可阻止赋值
var age: Int by Delegates.vetoable(0) { _, old, new ->
    new >= old    // 只允许增长
}

// 从 Map 读取属性
class User(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
}
```

自定义委托需实现 `getValue` / `setValue` 操作符。

## 三、操作符重载

Kotlin 允许自定义类型支持运算符，通过约定方法名映射。

```kotlin
data class Point(val x: Int, val y: Int) {
    operator fun plus(other: Point) = Point(x + other.x, y + other.y)
    operator fun unaryMinus() = Point(-x, -y)
    operator fun contains(p: Point) = x == p.x && y == p.y
    operator fun invoke() = "($x, $y)"     // 让对象可"调用"
    operator fun get(index: Int) = when (index) { 0 -> x; 1 -> y; else -> throw IndexOutOfBoundsException() }
}

val p1 = Point(1, 2)
val p2 = Point(3, 4)
p1 + p2        // Point(4, 6) — plus
-p1            // Point(-1, -2) — unaryMinus
p2 in p1       // false — contains
p1()           // "(1, 2)" — invoke
p1[0]          // 1 — get
```

常见约定：`+`(plus)、`-`(minus)、`*`(times)、`/`(div)、`%`(rem)、`==`(equals)、`<`(compareTo)、`[]`(get/set)、`in`(contains)、`..`(rangeTo)。

## 四、内联函数 `inline`

`inline` 函数在编译期展开调用处，消除 Lambda 的运行时开销（对象分配 + 虚方法调用）。

```kotlin
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.nanoTime()
    val result = block()
    return result to (System.nanoTime() - start)
}

val (result, time) = measureTime { expensiveComputation() }
// 编译后等价于直接内嵌 block 代码，无 Lambda 对象分配
```

- `noinline`：指定某个 Lambda 参数不内联（如需要存储或传递）
- `crossinline`：禁止 Lambda 中的非局部 `return`

> **规则**：内联函数的 `inline` 参数只能在函数体内直接调用，不能存储或传递给非内联函数。

## 五、值类 `value class`

值类（Kotlin 1.5+，原名 inline class）提供类型安全但零运行时开销的包装。

```kotlin
@JvmInline
value class UserId(val id: String)
@JvmInline
value class Password(private val s: String) {
    fun isValid() = s.length >= 8
}

fun login(id: UserId, password: Password) { /* ... */ }
login(UserId("u123"), Password("secure"))
// 编译后等价于 login("u123", "secure")，无对象分配
```

> **限制**：只能有一个 `val` 属性（不能是 `var`），不能有 `init` 块中的副作用（Kotlin 1.5+ 放宽）。在 JVM 上需要 `@JvmInline` 注解。

## 六、DSL 构建

Kotlin 的类型安全 DSL 能力来自带接收者的 Lambda（Lambda with Receiver）。

```kotlin
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class HTML {
    fun body(init: Body.() -> Unit) = Body().apply(init)
}

@HtmlDsl
class Body {
    private val paragraphs = mutableListOf<String>()
    fun p(text: String) { paragraphs += "<p>$text</p>" }
    fun render() = paragraphs.joinToString("\n")
}

fun html(init: HTML.() -> Unit) = HTML().apply(init)

// 使用
val doc = html {
    body {
        p("Hello, DSL!")
        p("Type-safe and concise.")
    }
}
```

- 带接收者的 Lambda 中可用 `this` 引用上下文对象
- `@DslMarker` 防止 DSL 嵌套中的作用域泄漏（不能在 `body` 内调用 `html` 的方法）
