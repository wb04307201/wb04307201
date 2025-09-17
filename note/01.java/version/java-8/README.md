----------------------------------------------------------------------
# Java 8

- **JEP 126**: Lambda 表达式 & 虚拟扩展方法
- **JEP 138**: 基于 Autoconf 的构建系统
- **JEP 160**: 针对 Method Handles 的 Lambda 形式的表征
- **JEP 161**: 简洁的配置文件
- **JEP 162**: 为模块化做准备
- **JEP 164**: 利用 CPU 指令来改善 AES 加密的性能
- **JEP 174**: Nashorn 引擎（允许在 Java 程序中嵌入 JS 代码）
- **JEP 176**: 自动检测识别 Caller-Sensitive 方法
- **JEP 179**: JDK API 变化和稳定性记录
- **JEP 101**: 目标类型推断
- **JEP 104**: Java 类型注解
- **JEP 105**: DocTree API
- **JEP 106**: 在 javax.tools 中添加 Javadoc
- **JEP 107**: 集合数据批量操作（Stream API 的基础）
- **JEP 109**: 增强的包含 Lambda 的核心库
- **JEP 112**: 改进了字符集的实现
- **JEP 117**: 移除 APT（Annotation-Processing Tool）
- **JEP 118**: 运行过程中可访问参数名
- **JEP 120**: 重复注解（@Repeatable）
- **JEP 122**: 移除 Permanent Generation（永久代），使用元空间（MetaSpace）
- **JEP 135**: Base64 编解码
- **JEP 136**: 提供更多的验证错误信息
- **JEP 139**: 增强了 javac，以改善构建速度
- **JEP 147**: 减少类元数据封装
- **JEP 148**: 支持创建小型虚拟机（3M 以下）
- **JEP 149**: 减少了核心库的内存占用
- **JEP 150**: 新的日期时间 API（java.time 包）
- **JEP 153**: 命令行启动 JavaFX 应用
- **JEP 155**: 改进对并发的支持
- **JEP 170**: JDBC 4.2
- **JEP 172**: DocLint 工具，用来检查 Javadoc 注释内容
- **JEP 173**: 移除一些很少使用的垃圾回收器组合
- **JEP 177**: java.text.DecimalFormat.format 优化
- **JEP 178**: 静态链接的 JNI 库
- **JEP 180**: 使用平衡树处理频繁的 HashMap 碰撞
- **JEP 184**: HTTP URL 访问权限

## JEP 126: Lambda 表达式 & 虚拟扩展方法

Lambda 表达式是 Java 8 中最重要的特性之一，它允许开发者以更简洁的方式编写匿名函数。Lambda 表达式的主要用途是简化函数式接口（只有一个抽象方法的接口）的实现。

虚拟扩展方法（也称为默认方法）允许接口包含具体的方法实现，这样可以在不破坏现有实现的情况下向接口添加新功能。

```java
// Lambda 表达式示例
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
names.forEach(name -> System.out.println(name));

// 虚拟扩展方法示例
interface Greeting {
    void greet();
    default void greetInEnglish() {
        System.out.println("Hello");
    }
}

class EnglishGreeting implements Greeting {
    @Override
    public void greet() {
        greetInEnglish();
    }
}
```

## JEP 138: 基于 Autoconf 的构建系统

Autoconf 是一个用于生成自动化配置脚本的工具，广泛应用于开源软件的构建过程。该特性引入了基于 Autoconf 的构建系统，使得 JDK 的构建过程更加灵活和可移植。

通过使用 Autoconf，开发者可以在不同的平台上生成适合的配置脚本，简化了 JDK 的跨平台构建过程。

## JEP 160: 针对 Method Handles 的 Lambda 形式的表征

Method Handles 是 Java 中用于动态操作方法的一种机制。该特性改进了 Method Handles 的实现，使其能够更好地支持 Lambda 表达式。

通过这种改进，Lambda 表达式可以更高效地转换为 Method Handles，提高了函数式编程的性能。

## JEP 161: 简洁的配置文件

该特性引入了一种更简洁的配置文件格式，用于配置 JDK 的各种参数。这种格式减少了配置文件的冗余信息，使得配置更加直观和易于管理。

## JEP 162: 为模块化做准备

模块化是 Java 9 中引入的一个重要特性，该特性在 Java 8 中为模块化做了准备工作。它引入了一些基础结构和工具，以便后续能够顺利实现模块化系统。

## JEP 164: 利用 CPU 指令来改善 AES 加密的性能

该特性通过利用现代 CPU 提供的特定指令集（如 AES-NI），显著提高了 AES 加密和解密的性能。这对于需要高性能加密的应用程序非常有益。

## JEP 174: Nashorn 引擎（允许在 Java 程序中嵌入 JS 代码）

Nashorn 是一个基于 Java 的 JavaScript 引擎，它允许开发者在 Java 应用程序中执行 JavaScript 代码。这使得 Java 和 JavaScript 之间的交互更加容易，适用于需要混合编程的场景。

```java
ScriptEngine engine = new ScriptEngineManager().getEngineByName("nashorn");
try {
    engine.eval("print('Hello, World!')");
} catch (ScriptException e) {
    e.printStackTrace();
}
```

## JEP 176: 自动检测识别 Caller-Sensitive 方法

Caller-Sensitive 方法是指其行为依赖于调用者的方法。该特性引入了一种机制，能够自动检测和识别这些方法，从而在安全管理和反射操作中提供更准确的信息。

## JEP 179: JDK API 变化和稳定性记录

该特性旨在记录 JDK API 的变化和稳定性信息，帮助开发者更好地理解和使用 JDK API。通过提供详细的变更日志和稳定性评级，开发者可以更容易地跟踪 API 的演进。

## JEP 101: 目标类型推断

目标类型推断允许编译器根据上下文自动推断出 Lambda 表达式或方法引用的目标类型。这使得代码更加简洁，减少了显式类型声明的需要。

```java
// 目标类型推断示例
List<String> list = Arrays.asList("a", "b", "c");
String joined = list.stream().reduce("", (a, b) -> a + b);
```

## JEP 104: Java 类型注解

Java 类型注解允许开发者在类型使用的地方添加注解，而不仅仅是在声明的地方。这提供了更细粒度的元数据控制，有助于改进代码的可读性和可维护性。

```java
// Java 类型注解示例
public class Example {
    public static void main(@NonNull String[] args) {
        // ...
    }
}
```

## JEP 105: DocTree API

DocTree API 提供了一种访问和操作 Javadoc 注释树结构的机制。这使得开发者可以编写工具来分析和处理 Javadoc 注释，例如生成文档或进行代码检查。

## JEP 106: 在 javax.tools 中添加 Javadoc

该特性在 `javax.tools` 包中添加了对 Javadoc 的支持，使得开发者可以通过编程方式生成 Javadoc 文档。这对于自动化构建和文档生成非常有用。

## JEP 107: 集合数据批量操作（Stream API 的基础）

该特性引入了集合数据的批量操作机制，为 Stream API 的实现奠定了基础。Stream API 提供了一种函数式的方式来处理集合数据，支持过滤、映射、归约等操作。

```java
// Stream API 示例
List<String> filtered = names.stream()
                           .filter(name -> name.startsWith("A"))
                           .collect(Collectors.toList());
```

## JEP 109: 增强的包含 Lambda 的核心库

该特性对 Java 核心库进行了增强，使其更好地支持 Lambda 表达式。许多核心库方法现在接受函数式接口作为参数，从而可以利用 Lambda 表达式简化代码。

## JEP 112: 改进了字符集的实现

该特性改进了 Java 中字符集的实现，提高了字符编码和解码的性能和准确性。这对于处理多语言文本的应用程序非常重要。

## JEP 117: 移除 APT（Annotation-Processing Tool）

APT 是一个较早的注解处理工具，该特性决定将其从 JDK 中移除，因为现在有更先进的注解处理机制（如 `javax.annotation.processing`）可用。

## JEP 118: 运行过程中可访问参数名

该特性允许在运行时通过反射机制访问方法的参数名。这对于调试和日志记录非常有用，因为可以显示实际的参数名而不是 `arg0`、`arg1` 等占位符。

```java
// 访问参数名示例
Method method = Example.class.getMethod("exampleMethod", String.class);
Parameter[] parameters = method.getParameters();
for (Parameter parameter : parameters) {
    System.out.println(parameter.getName());
}
```

## JEP 120: 重复注解（@Repeatable）

重复注解允许在同一个元素上多次应用同一个注解。这在需要多次使用相同类型的元数据时非常有用，避免了创建多个包装注解的麻烦。

```java
// 重复注解示例
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@Repeatable(Roles.class)
public @interface Role {
    String value();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface Roles {
    Role[] value();
}

@Role("Admin")
@Role("User")
public class ExampleClass {
    // ...
}
```

## JEP 122: 移除 Permanent Generation（永久代），使用元空间（MetaSpace）

该特性移除了 JVM 中的永久代，改用元空间来存储类的元数据。元空间使用本地内存，而不是 JVM 堆内存，从而避免了永久代内存溢出的问题。

## JEP 135: Base64 编解码

该特性在 Java 核心库中添加了 Base64 编解码的支持，使得开发者可以方便地进行 Base64 编码和解码操作。

```java
// Base64 编解码示例
String originalInput = "test string";
String encodedString = Base64.getEncoder().encodeToString(originalInput.getBytes());
byte[] decodedBytes = Base64.getDecoder().decode(encodedString);
String decodedString = new String(decodedBytes);
```

## JEP 136: 提供更多的验证错误信息

该特性改进了 Java 编译器和运行时系统的错误报告机制，提供了更详细和准确的验证错误信息。这有助于开发者更快地定位和修复问题。

## JEP 139: 增强了 javac，以改善构建速度

该特性对 `javac` 编译器进行了优化，提高了编译速度。这对于大型项目的构建过程非常有益，减少了开发者的等待时间。

## JEP 147: 减少类元数据封装

该特性通过减少类元数据的封装开销，提高了 JVM 的性能。类元数据是描述类结构和行为的信息，减少其封装可以加快类的加载和链接过程。

## JEP 148: 支持创建小型虚拟机（3M 以下）

该特性优化了 JVM 的内存使用，使得可以创建内存占用更小的虚拟机实例（3M 以下）。这对于嵌入式系统和资源受限的环境非常有用。

## JEP 149: 减少了核心库的内存占用

该特性通过优化核心库的实现，减少了其内存占用。这对于提高应用程序的整体性能和资源利用率非常重要。

## JEP 150: 新的日期时间 API（java.time 包）

新的日期时间 API 引入了 `java.time` 包，提供了一种更现代、更易用的日期和时间处理机制。它解决了旧日期时间 API 中的许多问题，如线程安全性、易用性等。

```java
// 新的日期时间 API 示例
LocalDate today = LocalDate.now();
LocalDateTime now = LocalDateTime.now();
ZonedDateTime zonedNow = ZonedDateTime.now();
```

## JEP 153: 命令行启动 JavaFX 应用

该特性允许通过命令行直接启动 JavaFX 应用程序，简化了 JavaFX 应用的部署和运行过程。

```
java --module-path /path/to/javafx-sdk/lib --add-modules javafx.controls,javafx.fxml -jar MyApp.jar
```

## JEP 155: 改进对并发的支持

该特性对 Java 的并发支持进行了改进，引入了新的并发工具和机制，如 `CompletableFuture` 和 `StampedLock`，提高了多线程编程的效率和可靠性。

```java
// CompletableFuture 示例
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> "Hello")
                                                  .thenApply(s -> s + " World");
future.thenAccept(System.out::println);
```

## JEP 170: JDBC 4.2

JDBC 4.2 是 Java 数据库连接 API 的一个更新版本，引入了一些新特性和改进，如支持新的 SQL 类型、改进的连接池管理等。

## JEP 172: DocLint 工具，用来检查 Javadoc 注释内容

DocLint 是一个用于检查 Javadoc 注释内容的工具，它可以帮助开发者确保 Javadoc 注释的准确性和一致性。通过 DocLint，可以检测出注释中的语法错误、格式问题等。

## JEP 173: 移除一些很少使用的垃圾回收器组合

该特性移除了一些很少使用的垃圾回收器组合，简化了 JVM 的垃圾回收配置选项。这有助于减少开发者的配置负担，提高垃圾回收的效率。

## JEP 177: java.text.DecimalFormat.format 优化

该特性对 `java.text.DecimalFormat.format` 方法进行了优化，提高了数字格式化的性能。这对于需要频繁进行数字格式化的应用程序非常有益。

## JEP 178: 静态链接的 JNI 库

该特性支持静态链接 JNI（Java Native Interface）库，使得 JNI 库可以在应用程序启动时一次性加载，而不是在每次调用时动态加载。这提高了 JNI 调用的性能。

## JEP 180: 使用平衡树处理频繁的 HashMap 碰撞

该特性改进了 `HashMap` 的实现，当发生频繁的碰撞时，使用平衡树而不是链表来存储元素。这提高了 `HashMap` 在高碰撞情况下的性能。

## JEP 184: HTTP URL 访问权限

该特性增强了 Java 对 HTTP URL 的访问权限控制，使得开发者可以更细粒度地控制对 HTTP 资源的访问。这对于安全敏感的应用程序非常重要。
----------------------------------------------------------------------