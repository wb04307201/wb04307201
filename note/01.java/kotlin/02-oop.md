# Kotlin 面向对象

## 一、类与构造器

### 主构造器 + `init` 块

Kotlin 的主构造器直接定义在类签名中，属性声明即字段。

```java
// Java
public class Person {
    private final String name;
    private int age;
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

```kotlin
// Kotlin
class Person(val name: String, var age: Int)  // 一行搞定
```

主构造器不能包含代码，初始化逻辑放在 `init` 块：

```kotlin
class Person(val name: String, var age: Int) {
    init {
        require(age >= 0) { "Age must be non-negative" }
    }
}
```

### 次构造器

次构造器必须委托主构造器：

```kotlin
class Person(val name: String) {
    var age: Int = 0
    constructor(name: String, age: Int) : this(name) {
        this.age = age
    }
}
```

## 二、数据类 `data class`

自动生成 `equals()`、`hashCode()`、`toString()`、`copy()` 和解构方法 `componentN()`。

```java
// Java 16+
public record Person(String name, int age) {}
```

```kotlin
// Kotlin
data class Person(val name: String, val age: Int)

val p1 = Person("Alice", 30)
val p2 = p1.copy(age = 31)   // 复制并修改部分属性
val (name, age) = p1         // 解构声明
```

## 三、密封类 `sealed class`

限制继承层次，编译期已知所有子类型，配合 `when` 可做穷举检查。

```kotlin
sealed class Result<out T>
data class Success<T>(val data: T) : Result<T>()
data class Error(val exception: Throwable) : Result<Nothing>()

fun handle(result: Result<String>) = when (result) {
    is Success -> println(result.data)
    is Error -> println(result.exception.message)
    // 无需 else — 编译器已穷举
}
```

> **对比**：Java 17+ 也有 `sealed class`，但 Kotlin 的密封类从 1.0 就已存在，且与 `when` 表达式深度集成。

## 四、`object` 与 Companion Object

### 单例 `object`

Kotlin 原生支持单例，替代 Java 的手动实现（双重检查、枚举单例等）。

```java
// Java — 双重检查锁
public class Config {
    private static volatile Config instance;
    private Config() {}
    public static Config getInstance() {
        if (instance == null) {
            synchronized (Config.class) {
                if (instance == null) instance = new Config();
            }
        }
        return instance;
    }
}
```

```kotlin
// Kotlin — 一行
object Config {
    val url = "jdbc:mysql://localhost:3306/db"
    fun connect() { /* ... */ }
}
// 调用：Config.connect()
```

### Companion Object — 替代 `static`

Kotlin 没有 `static` 关键字，用 `companion object` 实现类级别的成员。

```kotlin
class MathUtils {
    companion object {
        const val PI = 3.14159
        fun max(a: Int, b: Int) = if (a > b) a else b
    }
}
// 调用：MathUtils.max(1, 2)，MathUtils.PI
```

> **提示**：Java 调用时需用 `MathUtils.Companion.max()`，加 `@JvmStatic` 后可直接 `MathUtils.max()` 调用。

## 五、可见性修饰符

| 修饰符 | Java | Kotlin |
|--------|------|--------|
| `public` | 所有可见 | 所有可见（默认） |
| `protected` | 子类 + 同包 | 仅子类 |
| `private` | 仅同类 | 同类 + 同文件（顶层声明时） |
| `internal` | 无 | **同模块内可见** |

`internal` 是 Kotlin 独有的模块级可见性，在 Gradle 中一个模块即一个 module。

## 六、嵌套类 vs 内部类

Kotlin 嵌套类**默认静态**（无外部类引用），与 Java 相反。用 `inner` 关键字才有外部类引用。

```kotlin
class Outer {
    private val x = 1
    class Nested { fun f() {} }             // 静态嵌套，不能访问 x
    inner class Inner { fun f() { x } }     // 内部类，持有外部引用
}
```

## 七、泛型

### 声明处型变

Kotlin 在类声明处指定型变，避免 Java 使用处的通配符。

```java
// Java — 使用处通配符
List<? extends Number> nums = new ArrayList<Integer>();
```

```kotlin
// Kotlin — 声明处型变
interface Producer<out T> { fun produce(): T }
val p: Producer<Number> = object : Producer<Int> { override fun produce() = 1 }
```

- `out T`（协变）：T 只能出现在返回位置，类比 Java `? extends T`
- `in T`（逆变）：T 只能出现在参数位置，类比 Java `? super T`
- 无修饰：不变，T 可出现在任意位置

### 使用处型变 & 星投影

```kotlin
val list: MutableList<out Any> = mutableListOf<String>()  // 只读
val anyList: List<*> = listOf(1, "a", true)               // 星投影，等价 List<out Any?>
```

### `reified` 类型参数

配合 `inline` 函数，泛型类型在运行时可用（Java 做不到）。

```kotlin
inline fun <reified T : Any> Gson.fromJson(json: String): T =
    fromJson(json, T::class.java)

val user: User = gson.fromJson(json)   // 无需传入 Class 参数
```
