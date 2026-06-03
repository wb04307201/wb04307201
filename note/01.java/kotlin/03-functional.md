# Kotlin 函数式

## 一、函数特性

### 默认参数与命名参数

Kotlin 的默认参数替代 Java 的方法重载，命名参数提升可读性。

```java
// Java — 需要多个重载
public String buildUrl(String host) { return buildUrl(host, 8080); }
public String buildUrl(String host, int port) { return buildUrl(host, port, "/"); }
public String buildUrl(String host, int port, String path) { ... }
```

```kotlin
// Kotlin — 一个函数
fun buildUrl(host: String, port: Int = 8080, path: String = "/") =
    "http://$host:$port$path"

buildUrl("localhost")                           // 全部默认
buildUrl("localhost", path = "/api")            // 命名参数跳过 port
```

### 单表达式函数

```kotlin
fun max(a: Int, b: Int) = if (a > b) a else b
// 编译器推断返回类型为 Int
```

### 中缀函数 `infix`

```kotlin
infix fun Int.to(other: Int) = Pair(this, other)
val pair = 1 to 2    // 等价于 1.to(2)，读起来像自然语言
```

### 尾递归 `tailrec`

```kotlin
tailrec fun factorial(n: Int, acc: Long = 1): Long =
    if (n <= 1) acc else factorial(n - 1, acc * n)
// 编译器优化为循环，避免栈溢出
```

## 二、集合

### 只读 vs 可变接口

Kotlin 区分只读集合接口（`List`/`Set`/`Map`）和可变接口（`MutableList`/`MutableSet`/`MutableMap`）。

```kotlin
val list: List<Int> = listOf(1, 2, 3)         // 只读接口
val mutable: MutableList<Int> = mutableListOf(1, 2, 3)  // 可变
mutable.add(4)     // ✅
// list.add(4)     // ❌ 编译错误
```

> **对比**：Java 的 `Collections.unmodifiableList` 是运行时包装，Kotlin 的只读接口在编译期就阻止修改。

### 集合创建

```kotlin
listOf(1, 2, 3)          // 不可变 List
mutableListOf(1, 2, 3)   // 可变 List
setOf("a", "b")          // 不可变 Set
mapOf("key" to "value")  // 不可变 Map
```

## 三、高阶函数与集合操作

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

numbers.map { it * 2 }           // [2, 4, 6, 8, 10]
numbers.filter { it > 3 }        // [4, 5]
numbers.filter { it % 2 == 0 }.map { it * it }  // [4, 16]
numbers.fold(0) { acc, i -> acc + i }           // 15
numbers.reduce { acc, i -> acc * i }            // 120
```

Lambda 最后一个参数可移出括号（trailing lambda），`it` 是单参数 Lambda 的默认名。

## 四、`Sequence` 惰性求值

`Sequence` 对比 Java `Stream`：惰性求值，中间操作不产生新集合。

```java
// Java Stream — 每次 filter/map 都产生中间集合
list.stream().filter(x -> x > 3).map(x -> x * 2).findFirst()
```

```kotlin
// Kotlin Sequence — 惰性求值，元素逐个流过整条管道
val result = (1..1_000_000)
    .asSequence()
    .map { it * 2 }     // 不立即执行
    .filter { it > 10 } // 不立即执行
    .take(5)
    .toList()           // 触发计算
```

> **何时用**：链式操作超过 2 步且数据量大时，`Sequence` 比直接集合操作更高效。小数据量用直接集合操作（无额外开销）。

## 五、五个作用域函数

Kotlin 的作用域函数是减少临时变量的核心工具。

| 函数 | 上下文对象 | 返回值 | 典型场景 |
|------|-----------|--------|---------|
| `let` | `it` | Lambda 结果 | null 检查后的链式操作 |
| `run` | `this` | Lambda 结果 | 对象配置 + 计算结果 |
| `with` | `this` | Lambda 结果 | 在同一对象上调用多个方法 |
| `apply` | `this` | 对象本身 | 对象初始化 / 配置 |
| `also` | `it` | 对象本身 | 副作用（日志、验证） |

```kotlin
// let — null 安全链式操作
val len = str?.let { it.trim().length }

// apply — 对象初始化
val dataSource = DataSource().apply {
    url = "jdbc:mysql://localhost/db"
    user = "root"
    password = "secret"
}

// also — 副作用
val numbers = mutableListOf(1, 2, 3)
    .also { println("Before: $it") }
    .add(4)

// run — 配置 + 计算
val result = config.run {
    val url = "$host:$port/$path"
    connect(url)
}
```

> **选择口诀**：需要返回对象本身用 `apply`/`also`，需要返回计算结果用 `let`/`run`。用 `this` 引用上下文用 `run`/`with`/`apply`，用 `it` 用 `let`/`also`。
