# Stream API

| Java版本 | 新特性/增强内容 |
|---------|---------------|
| Java 8 | JEP 107: 首次引入 Stream API (`java.util.stream`)，提供对元素流进行函数式操作的能力 |
| Java 9 | Stream API 增强，添加了 `takeWhile()`、`dropWhile()`、`ofNullable()` 和重载的 `iterate()` 方法 |
| Java 10 | Stream API 增强，新增收集到不可变集合的收集器 |
| Java 16 | Stream API 增强，新增 `toList()` 方法和 `mapMulti()` 方法 |
| Java 22 | JEP 461: 流收集器（预览）- 引入 `Stream::gather(Gatherer)` 方法 |
| Java 23 | JEP 473: 流收集器（第二次预览）- 继续完善流收集器功能 |
| Java 24 | JEP 485: 流收集器（正式版）- `Stream::gather(Gatherer)` 方法正式可用 |

## 功能详细介绍

### 1. Java 8 - Stream API 初始引入 (JEP 107)

Java 8 引入的 Stream API 是对集合处理方式的一次重大革新。它提供了一种声明式的、函数式的方式来处理数据集合。

核心概念：
- **中间操作**：如 `filter`、`map`、`sorted` 等，返回新的 Stream，支持链式调用
- **终端操作**：如 `collect`、`forEach`、`reduce` 等，触发实际计算并产生结果
- **惰性求值**：中间操作不会立即执行，只有在终端操作调用时才开始计算
- **并行处理**：通过 `parallelStream()` 轻松实现并行计算

```java
List<String> names = Arrays.asList("abc", "java", "python", "David", "Anna", "Edward");
List<String> result = names.stream()
    .filter(name -> name.startsWith("A"))
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```


### 2. Java 9 - Stream API 增强

Java 9 为 Stream API 添加了几个重要方法：

- `takeWhile()`: 从流中依次获取满足条件的元素，直到遇到不满足条件的元素为止
- `dropWhile()`: 与 `takeWhile()` 相反，跳过满足条件的元素，从第一个不满足条件的元素开始获取
- `ofNullable()`: 创建一个可以包含单个元素或为空的 Stream
- `iterate()` 的重载版本：添加了谓词参数来控制迭代的终止条件

```java
// takeWhile 示例
List<Integer> numbers = List.of(1, 3, 5, 6, 7, 9);
numbers.stream().takeWhile(n -> n % 2 == 1).forEach(System.out::println); // 输出: 1, 3, 5

// ofNullable 示例
Stream<String> stream = Stream.ofNullable(getString()); // getString() 可能返回 null
```


### 3. Java 10 - 不可变集合收集器

Java 10 增加了将流收集到不可变集合的功能：

- `Collectors.toUnmodifiableList()`
- `Collectors.toUnmodifiableSet()`
- `Collectors.toUnmodifiableMap()`

这些收集器创建的集合是不可变的，有助于提高线程安全性并减少意外修改的风险。

```java
List<String> immutableList = Stream.of("a", "b", "c")
    .collect(Collectors.toUnmodifiableList());
// immutableList.add("d"); // 抛出 UnsupportedOperationException
```


### 4. Java 16 - 更多 Stream 增强

Java 16 引入了以下增强功能：

- `toList()` 方法：直接创建不可变列表的便捷方法
- `mapMulti()`: 用于将一个元素转换为多个元素的更高效替代方案

```java
List<String> result = Stream.of("a", "b", "c")
    .toList(); // 创建不可变列表

// mapMulti 示例：将每个元素转换为自身和大写形式
Stream<String> stream = Stream.of("a", "b", "c");
stream.mapMulti((str, consumer) -> {
    consumer.accept(str);
    consumer.accept(str.toUpperCase());
}).forEach(System.out::println); // 输出: a, A, b, B, c, C
```


### 5. Java 22-24 - 流收集器 (Stream Gatherers)

这是 Stream API 最重要的增强之一，通过 `Stream::gather(Gatherer)` 方法实现：

- 允许开发者定义自定义的中间操作
- 支持更复杂的数据转换和状态管理
- 可以实现滑动窗口、自定义去重等复杂操作

```java
// 基于字符串长度的去重示例
var result = Stream.of("foo", "bar", "baz", "quux")
    .gather(Gatherer.ofSequential(
        HashSet::new, // 初始化状态为 HashSet
        (set, str, downstream) -> {
            if (set.add(str.length())) {
                return downstream.push(str);
            }
            return true; // 继续处理流
        }
    ))
    .toList(); // 结果: [foo, quux]
```


## 总结

Stream API 从 Java 8 引入以来，持续得到增强和改进。最初的核心功能提供了函数式处理集合的能力，随后的版本不断增加新的操作方法和收集器，使 API 更加完善和强大。最新的流收集器功能（Java 22-24）代表了 Stream API 的一个重要里程碑，允许开发者创建自定义的中间操作，极大地扩展了 Stream API 的应用范围和灵活性。

这些增强功能使开发者能够以更简洁、更可读的方式处理数据集合，同时充分利用现代多核处理器的优势进行并行计算。