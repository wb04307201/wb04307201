<!--
module:
  parent: java
  slug: java/version/lambda
  type: article
  category: 主模块子文章
  summary: Java 8 Lambda 表达式：函数式接口、方法引用、流式编程基础。
-->

# Lambda

## 引言：变更说明

Lambda 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 功能描述

Lambda 表达式是 Java 8 引入的重要语言特性，它允许将函数作为参数传递给方法，使 Java 具备函数式编程的能力。Lambda 表达式配合函数式接口和 Stream API，彻底改变了 Java 的数据处理方式。

## 基本用法（Java 11+ 最新语法）

```java
// Lambda 表达式语法：(参数) -> { 方法体 }
// 单参数可省略括号，单表达式可省略大括号

// 1. 结合内置函数式接口使用
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
names.stream()
    .filter(name -> name.startsWith("A"))       // Predicate
    .map(String::toUpperCase)                    // Function + 方法引用
    .forEach(System.out::println);               // Consumer

// 2. var 参数 + 注解（Java 11+）
BinaryOperator<Integer> add = (@NonNull var a, @NonNull var b) -> a + b;

// 3. 方法引用（静态、实例、构造器）
Function<String, Integer> parseInt = Integer::parseInt;    // 静态方法引用
Function<String, Integer> length = String::length;         // 任意对象实例方法引用
Supplier<List<String>> newList = ArrayList::new;           // 构造器引用

// 4. 组合函数式接口
Function<Integer, Integer> f = x -> x * 2;
Function<Integer, Integer> g = x -> x + 1;
Function<Integer, Integer> h = f.andThen(g);  // h(x) = g(f(x)) = 2x + 1

// 5. 自定义函数式接口
@FunctionalInterface
interface StringProcessor {
    String process(String input);

    default StringProcessor andThen(StringProcessor after) {
        return (String s) -> after.process(this.process(s));
    }
}
```

## 变更历史表

| Java版本  | 新特性/增强内容                           |
|---------|------------------------------------|
| Java 8  | Lambda 表达式和函数式接口引入                   |
| Java 8  | java.util.function 包，包含常用函数式接口        |
| Java 8  | 方法引用和构造器引用支持                       |
| Java 9  | Stream API 新增 takeWhile/dropWhile/ofNullable |
| Java 11 | JEP 323: Lambda 参数的局部变量语法(var)          |

## 功能详细介绍

### 1. Java 8 - Lambda 表达式引入

Java 8 引入了 Lambda 表达式，为 Java 增加了函数式编程的能力。这是 Java 语言历史上最大的语法变化之一。

#### 核心概念：

1. **Lambda 表达式**：简洁地表示匿名函数的语法
2. **函数式接口**：只包含一个抽象方法的接口，可以被 Lambda 表达式实现
3. **@FunctionalInterface 注解**：用于标记函数式接口，编译器会验证接口是否满足函数式接口的要求
4. **方法引用**：Lambda 表达式的简化形式，通过 `::` 语法引用已有方法

#### Lambda 表达式语法：

```java
// 基本语法：(parameters) -> expression
// 或：(parameters) -> { statements; }

// 示例：
Comparator<String> comparator = (s1, s2) -> s1.compareToIgnoreCase(s2);

// 简化形式（单参数可省略括号）：
Function<String, Integer> length = s -> s.length();

// 多行表达式：
Function<Integer, Integer> square = x -> {
    int result = x * x;
    return result;
};
```

#### 方法引用：

```java
// 静态方法引用
Function<String, Integer> parseInt = Integer::parseInt;

// 实例方法引用（特定对象）
String str = "Hello";
Supplier<Integer> length = str::length;

// 实例方法引用（任意对象）
Function<String, Integer> stringLength = String::length;

// 构造器引用
Supplier<List<String>> listSupplier = ArrayList::new;
```

### 2. Java 9 - Stream API 增强

Java 9 为 Stream API 添加了新的函数式操作，进一步增强了 Lambda 表达式的数据处理能力。

```java
List<Integer> numbers = List.of(1, 3, 5, 6, 7, 9);

// takeWhile - 从流中依次获取满足条件的元素，直到不满足条件为止
numbers.stream().takeWhile(n -> n % 2 == 1).forEach(System.out::println); // 1, 3, 5

// dropWhile - 与 takeWhile 相反
numbers.stream().dropWhile(n -> n % 2 == 1).forEach(System.out::println); // 6, 7, 9

// ofNullable - 创建一个可以包含单个元素或为空的 Stream
Stream<String> stream1 = Stream.ofNullable("Java");
Stream<String> stream2 = Stream.ofNullable(null);

// iterate 增强（带终止条件）
Stream.iterate(0, i -> i < 10, i -> i + 1).forEach(System.out::println);
```

### 3. Java 11 - Lambda 参数的局部变量语法 (JEP 323)

Java 11 允许在 Lambda 表达式参数中使用 `var` 关键字，使得可以在 Lambda 参数上添加注解，同时保持类型推断。

```java
// Java 10 之前 - 无法在 Lambda 参数上使用注解
BinaryOperator<Integer> adder = (a, b) -> a + b;

// Java 11 - 使用 var
BinaryOperator<Integer> adder = (var a, var b) -> a + b;

// 结合注解使用（这是 var 在 Lambda 中的主要用途）
BinaryOperator<Integer> adderWithAnnotation = (@NotNull var a, @NotNull var b) -> a + b;

// 部分参数使用 var（要么全部使用，要么都不使用）
// 合法：
(var x, var y) -> x + y
// 不合法：
(var x, y) -> x + y  // 编译错误
```

## Lambda 表达式的核心优势

1. **代码简洁性**：Lambda 表达式使代码更加简洁易读，替代冗长的匿名内部类
2. **函数式编程支持**：支持函数作为一等公民，提高代码抽象能力
3. **类型推断**：编译器可以自动推断参数类型，减少样板代码
4. **与 Stream API 结合**：与 Stream API 完美结合，轻松实现数据处理流水线
5. **并行处理**：与并行流结合，轻松实现并行处理

## 最佳实践

1. **优先使用方法引用**：能使用方法引用时优先使用，代码更简洁
2. **合理使用 var**：在 Java 11+ 中，当需要在 Lambda 参数上添加注解时使用 var
3. **避免副作用**：Lambda 表达式应尽量避免副作用，保持纯函数特性
4. **合理使用并行流**：在数据量大且计算复杂时使用并行流
5. **组合使用**：合理组合各种函数式接口，构建复杂的处理逻辑
6. **注意捕获变量**：Lambda 表达式只能捕获 effectively final 的变量

## 总结

从 Java 8 引入 Lambda 表达式以来，该特性经历了持续的完善。Java 8 奠定了函数式编程的基础，Java 9 增强了 Stream API 的函数式操作，Java 11 允许在 Lambda 参数中使用 var 关键字以支持注解。这些改进使 Java 开发者能够编写更加简洁、可读和可维护的代码。

---

← [返回 功能版本变更历史](../README.md)
