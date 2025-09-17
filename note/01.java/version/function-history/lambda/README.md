# Lambda

| Java版本  | 新特性/增强内容                           |
|---------|------------------------------------|
| Java 8  | JEP 126: 首次引入 Lambda 表达式和函数式接口     |
| Java 8  | 引入 java.util.function 包，包含常用的函数式接口 |
| Java 8  | 方法引用和构造器引用支持                       |
| Java 9  | Stream API 增强，提供更多函数式操作            |
| Java 10 | 局部变量类型推断(var)可用于 Lambda 参数         |
| Java 11 | Lambda 参数的局部变量语法得到完善               |
| Java 16 | 外部函数和内存 API（孵化器）支持函数式风格            |
| Java 17 | 外部函数和内存 API（孵化器）继续增强               |
| Java 19 | 外部函数和内存 API（预览）进一步完善               |
| Java 22 | 引入流收集器（预览），扩展函数式数据处理能力             |
| Java 23 | 流收集器（第二次预览）继续完善                    |
| Java 24 | 流收集器（正式版）可用                        |

## 功能详细介绍

### 1. Java 8 - Lambda 表达式初始引入 (JEP 126)

Java 8 是 Lambda 表达式在 Java 语言中的一个重要里程碑，为 Java 增加了函数式编程的能力。

#### 核心概念：

1. **Lambda 表达式**：简洁地表示匿名函数的语法
2. **函数式接口**：只包含一个抽象方法的接口，可以被 Lambda 表达式实现
3. **@FunctionalInterface 注解**：用于标记函数式接口

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


#### 与函数式接口结合使用：

```java
// 使用内置函数式接口
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// Predicate - 过滤
names.stream().filter(name -> name.startsWith("A")).forEach(System.out::println);

// Function - 转换
names.stream().map(String::toUpperCase).forEach(System.out::println);

// Consumer - 消费
names.stream().forEach(name -> System.out.println("Hello " + name));

// Supplier - 提供
Supplier<List<String>> listSupplier = () -> new ArrayList<>();
```


### 2. Java 8 - 方法引用

方法引用是 Lambda 表达式的简化形式：

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
Function<Integer, List<String>> listWithCapacity = ArrayList::new;
```


### 3. Java 9 - Stream API 增强

Java 9 为 Stream API 添加了新的函数式操作：

```java
List<Integer> numbers = List.of(1, 3, 5, 6, 7, 9);

// takeWhile - 从流中依次获取满足条件的元素，直到不满足条件为止
numbers.stream().takeWhile(n -> n % 2 == 1).forEach(System.out::println); // 1, 3, 5

// dropWhile - 与 takeWhile 相反
numbers.stream().dropWhile(n -> n % 2 == 1).forEach(System.out::println); // 6, 7, 9

// ofNullable - 创建一个可以包含单个元素或为空的 Stream
Stream<String> stream1 = Stream.ofNullable("Java");
Stream<String> stream2 = Stream.ofNullable(null);
```


### 4. Java 10 - Lambda 参数类型推断

Java 10 允许在 Lambda 表达式参数中使用 var 关键字：

```java
// Java 10 之前
BinaryOperator<Integer> adder = (a, b) -> a + b;

// Java 10 及以后 - 使用 var
BinaryOperator<Integer> adder = (var a, var b) -> a + b;

// 结合注解使用
BinaryOperator<Integer> adderWithAnnotation = (@NotNull var a, @NotNull var b) -> a + b;
```


### 5. Java 11 - Lambda 参数语法完善

Java 11 继续完善 Lambda 参数的类型推断功能，使语法更加一致和灵活。

### 6. Java 16 - 外部函数和内存 API（孵化器）

Java 16 引入了外部函数和内存 API，支持函数式编程风格：

```java
// 外部链接器 API 示例（孵化器特性）
import jdk.incubator.foreign.*;

public class ForeignLinkerExample {
    public static void main(String[] args) throws Throwable {
        // 使用函数式风格调用本地函数
        LibraryLookup lib = LibraryLookup.ofDefault();
        SymbolLookup printfSymbol = SymbolLookup.loaderLookup().lookup("printf").get();
        
        MethodType type = MethodType.methodType(int.class, MemoryAddress.class, MemoryAddress.class);
        MethodHandle mh = CLinker.getInstance().downcallHandle(
                printfSymbol,
                type,
                FunctionDescriptor.of(CLinker.C_INT, CLinker.C_POINTER, CLinker.C_POINTER));
    }
}
```


### 7. Java 17-19 - 外部函数和内存 API 持续增强

外部函数和内存 API 在 Java 17-19 中持续改进，提供了更丰富的函数式编程支持：

```java
// Java 19 中的外部函数和内存 API（预览）
import java.lang.foreign.*;
import java.lang.invoke.MethodHandle;

public class FFMExample {
    public static void main(String[] args) throws Throwable {
        // 使用函数式风格进行内存操作
        try (var arena = Arena.ofConfined()) {
            MemorySegment segment = arena.allocate(100);
            // 函数式操作内存
        }
    }
}
```


### 8. Java 22-24 - 流收集器（Gatherer）

Java 22 开始引入流收集器功能，扩展了函数式数据处理能力：

```java
// Java 22+ 流收集器示例（预览特性）
import java.util.stream.Gatherer;

var result = Stream.of("foo", "bar", "baz", "quux")
    .gather(Gatherer.ofSequential(
        HashSet::new, // 初始化状态
        (set, str, downstream) -> {
            if (set.add(str.length())) {
                return downstream.push(str);
            }
            return true;
        }
    ))
    .toList(); // [foo, quux]
```


## Lambda 表达式的核心优势

1. **代码简洁性**：Lambda 表达式使代码更加简洁易读，替代冗长的匿名内部类
2. **函数式编程支持**：支持函数作为一等公民，提高代码抽象能力
3. **类型推断**：编译器可以自动推断参数类型，减少样板代码
4. **与 Stream API 结合**：与 Stream API 完美结合，轻松实现数据处理流水线
5. **并行处理**：与并行流结合，轻松实现并行处理
6. **性能优化**：JVM 可以对 Lambda 表达式进行优化

## 常用 Lambda 表达式示例

```java
// 基本用法
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");

// 过滤
List<String> filtered = names.stream()
    .filter(name -> name.length() > 3)
    .collect(Collectors.toList());

// 映射
List<Integer> lengths = names.stream()
    .map(String::length)
    .collect(Collectors.toList());

// 排序
List<String> sorted = names.stream()
    .sorted((s1, s2) -> s1.compareToIgnoreCase(s2))
    .collect(Collectors.toList());

// 归约
int totalLength = names.stream()
    .mapToInt(String::length)
    .sum();

// 分组
Map<Integer, List<String>> groupedByLength = names.stream()
    .collect(Collectors.groupingBy(String::length));
```


## 最佳实践

1. **优先使用方法引用**：能使用方法引用时优先使用，代码更简洁
2. **合理使用 var**：在 Java 10+ 中合理使用 var 简化 Lambda 参数声明
3. **避免副作用**：Lambda 表达式应尽量避免副作用，保持纯函数特性
4. **合理使用并行流**：在数据量大且计算复杂时使用并行流
5. **组合使用**：合理组合各种函数式接口，构建复杂的处理逻辑
6. **注意捕获变量**：Lambda 表达式只能捕获 effectively final 的变量

## 总结

从 Java 8 引入 Lambda 表达式以来，函数式编程在 Java 生态系统中不断发展和完善。Java 8 奠定了函数式编程的基础，后续版本通过 Stream API 增强、局部变量类型推断、外部函数和内存 API 等特性，持续丰富函数式编程的能力。这些特性使 Java 开发者能够编写更加简洁、可读和可维护的代码，同时充分利用现代多核处理器的优势进行并行计算。Lambda 表达式已成为现代 Java 开发中不可或缺的重要特性。