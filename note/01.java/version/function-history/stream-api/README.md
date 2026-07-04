<!--
module:
  parent: java
  slug: java/version/stream-api
  type: article
  category: 主模块子文章
  summary: Java 8 Stream API：函数式集合操作、并行流与性能陷阱。
-->

# Stream API

## 引言：变更说明

Stream API 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 功能描述

Stream API 提供了一种声明式、函数式的方式来处理数据集合。支持链式中间操作（filter、map、sorted 等）和终端操作（collect、forEach、reduce 等），具有惰性求值和并行处理能力。从 Java 22 起新增 `Stream::gather(Gatherer)` 方法，允许自定义中间操作。

## 基本用法（最新，Java 24+）

```java
List<String> names = List.of("Alice", "Bob", "Charlie", "David");

// 1. 基础链式操作
List<String> result = names.stream()
    .filter(name -> name.length() > 3)
    .map(String::toUpperCase)
    .sorted()
    .toList();  // Java 16+，返回不可变 List

// 2. takeWhile / dropWhile (Java 9+)
List.of(1, 3, 5, 6, 7, 9).stream().takeWhile(n -> n % 2 == 1);  // [1, 3, 5]
List.of(1, 3, 5, 6, 7, 9).stream().dropWhile(n -> n % 2 == 1);  // [6, 7, 9]

// 3. mapMulti (Java 16+)
Stream.of("a", "b").mapMulti((s, consumer) -> {
    consumer.accept(s);
    consumer.accept(s.toUpperCase());
}).toList();  // ["a", "A", "b", "B"]

// 4. Stream::gather 自定义中间操作 (Java 24+)
Stream.of("foo", "bar", "baz", "quux")
    .gather(Gatherers.windowFixed(3))
    .toList();  // [["foo","bar","baz"], ["bar","baz","quux"]]

// 5. 不可变集合收集器 (Java 10+)
Stream.of("a", "b").collect(Collectors.toUnmodifiableList());

// 6. 并行流
names.parallelStream().filter(name -> name.startsWith("A")).toList();
```

## 变更历史表

| Java版本  | 新特性/增强内容                                                                         |
|---------|----------------------------------------------------------------------------------|
| Java 24 | JEP 485: Stream::gather(Gatherer) 正式可用                                       |
| Java 23 | JEP 473: Stream::gather(Gatherer) 第二次预览                                     |
| Java 22 | JEP 461: Stream::gather(Gatherer) 首次预览，引入自定义中间操作                     |
| Java 16 | 新增 toList() 方法和 mapMulti() 方法                                              |
| Java 10 | 新增 Collectors.toUnmodifiableList/Set/Map                                       |
| Java 9  | 新增 takeWhile()、dropWhile()、ofNullable() 和带谓词的 iterate()                   |
| Java 8  | JEP 107: 首次引入 Stream API                                                     |

## 功能详细介绍

### 1. Java 8 - Stream API 初始引入 (JEP 107)

Java 8 引入的 Stream API 是对集合处理方式的一次重大革新。

核心概念：
- **中间操作**：如 `filter`、`map`、`sorted` 等，返回新的 Stream，支持链式调用
- **终端操作**：如 `collect`、`forEach`、`reduce` 等，触发实际计算并产生结果
- **惰性求值**：中间操作不会立即执行，只有在终端操作调用时才开始计算
- **并行处理**：通过 `parallelStream()` 轻松实现并行计算

```java
List<String> names = Arrays.asList("abc", "java", "python", "David", "Anna");
List<String> result = names.stream()
    .filter(name -> name.startsWith("A"))
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

自定义 Collector：
```java
Collector<T, ?, String> joining(CharSequence delimiter) {
    return Collector.of(
        () -> new StringJoiner(delimiter),
        (joiner, element) -> joiner.add(element.toString()),
        (joiner1, joiner2) -> joiner1.merge(joiner2),
        StringJoiner::toString
    );
}
```

### 2. Java 9 - Stream API 增强

Java 9 为 Stream API 添加了几个重要方法：

- `takeWhile()`: 从流中依次获取满足条件的元素，直到遇到不满足条件的元素为止
- `dropWhile()`: 与 `takeWhile()` 相反，跳过满足条件的元素
- `ofNullable()`: 创建一个可以包含单个元素或为空的 Stream
- `iterate()` 的重载版本：添加了谓词参数来控制迭代的终止条件

```java
List<Integer> numbers = List.of(1, 3, 5, 6, 7, 9);
numbers.stream().takeWhile(n -> n % 2 == 1).forEach(System.out::println); // 1, 3, 5
numbers.stream().dropWhile(n -> n % 2 == 1).forEach(System.out::println); // 6, 7, 9

// iterate 带终止条件
Stream.iterate(0, i -> i < 10, i -> i + 1).forEach(System.out::println);
```

### 3. Java 10 - 不可变集合收集器

Java 10 增加了将流收集到不可变集合的功能：

```java
List<String> immutableList = Stream.of("a", "b", "c")
    .collect(Collectors.toUnmodifiableList());
// immutableList.add("d"); // 抛出 UnsupportedOperationException
```

### 4. Java 16 - toList() 和 mapMulti()

Java 16 引入了两项增强：

- `toList()`: 直接创建不可变列表的便捷方法
- `mapMulti()`: 将一个元素转换为多个元素的更高效替代方案（替代 `flatMap` 的部分场景）

```java
List<String> result = Stream.of("a", "b", "c").toList(); // 不可变列表

// mapMulti 示例
Stream.of("a", "b").mapMulti((str, consumer) -> {
    consumer.accept(str);
    consumer.accept(str.toUpperCase());
}).forEach(System.out::println); // a, A, b, B
```

### 5. Java 22-24 - Stream Gatherers (JEP 461/473/485)

这是 Stream API 最重要的增强之一，引入了 `Stream::gather(Gatherer)` 方法：

- Java 22: 首次预览，允许定义自定义中间操作
- Java 23: 第二次预览，API 微调
- Java 24: 正式转正

```java
// 基于字符串长度的去重示例
var result = Stream.of("foo", "bar", "baz", "quux")
    .gather(Gatherers.windowFixed(3))
    .toList(); // [["foo","bar","baz"], ["bar","baz","quux"]]

// 自定义 Gatherer
Gatherer<String, ?, String> deduplicate = Gatherer.of(
    () -> new HashSet<Integer>(),
    (state, element, downstream) -> {
        if (state.add(element.length())) {
            return downstream.push(element);
        }
        return true;
    }
);

Stream.of("foo", "bar", "baz", "quux")
    .gather(deduplicate)
    .toList(); // ["foo", "quux"]
```

## 总结

Stream API 从 Java 8 引入以来持续增强，最新的 Stream Gatherers 功能（Java 22-24）代表了重要里程碑，允许创建自定义中间操作，极大扩展了 API 的灵活性。

---

← [返回 功能版本变更历史](../README.md)
