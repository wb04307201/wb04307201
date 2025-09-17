# Java 21

- **JEP 430**: 字符串模板（预览）
- **JEP 431**: 有序集合
- **JEP 439**: 分代式 ZGC
- **JEP 440**: 记录模式
- **JEP 441**: switch 表达式中的模式匹配
- **JEP 442**: 外部函数与内存 API（第三次预览）
- **JEP 443**: 未命名模式和变量（预览）
- **JEP 444**: 虚拟线程
- **JEP 445**: 未命名类和实例主方法（预览）
- **JEP 446**: 作用域值（预览）
- **JEP 448**: 向量 API（第六次孵化）
- **JEP 449**: 弃用待移除的 Windows 32 位 x86 端口
- **JEP 451**: 准备禁止动态加载代理
- **JEP 452**: 密钥封装机制 API
- **JEP 453**: 结构化并发（预览）

## JEP 430: 字符串模板（预览）

字符串模板是一种新的字符串处理机制，它允许开发者在字符串中嵌入表达式，从而更方便地构建复杂的字符串。字符串模板通过使用反引号（`）来定义模板字符串，并在其中使用 `${}` 来嵌入表达式。

```java
String name = "Alice";
int age = 25;
String message = `Hello, my name is ${name} and I'm ${age} years old.`;
System.out.println(message);
```

这一特性使得字符串拼接更加简洁和易读，减少了使用 `+` 操作符进行字符串拼接的繁琐过程。

## JEP 431: 有序集合

有序集合是一种新的集合类型，它维护了元素的插入顺序。与现有的集合类型（如 `HashSet` 不保证顺序，`LinkedHashSet` 保证插入顺序但功能有限）不同，有序集合提供了更丰富的操作和更好的性能。

有序集合适用于需要按照插入顺序处理元素的场景，例如缓存、队列等。通过使用有序集合，开发者可以更方便地管理元素的顺序，提高代码的可读性和可维护性。

```java
OrderedSet<String> orderedSet = OrderedSet.of("apple", "banana", "cherry");
orderedSet.forEach(System.out::println); // 输出顺序为 apple, banana, cherry
```

## JEP 439: 分代式 ZGC

分代式 ZGC 是一种改进的垃圾回收算法，它结合了分代收集和 ZGC 垃圾回收器的优点。分代收集将堆内存分为不同的代，例如年轻代和老年代，并针对不同代的特点采用不同的垃圾回收策略。ZGC 则是一种并发式垃圾回收器，旨在减少垃圾回收的停顿时间。

分代式 ZGC 通过将分代收集和 ZGC 结合，提高了垃圾回收的效率和性能。它可以更有效地回收年轻代中的短期对象，同时减少老年代垃圾回收的停顿时间，提高应用程序的响应速度。

## JEP 440: 记录模式

记录模式是一种新的模式匹配机制，它允许开发者在模式匹配中直接使用记录类的属性。记录类是一种不可变的数据载体类，它自动提供了属性的访问器方法和一些标准方法（如 `equals`、`hashCode` 和 `toString`）。

通过记录模式，开发者可以更方便地对记录类进行解构和匹配，提高代码的可读性和简洁性。

```java
record Point(int x, int y) {}

Point point = new Point(10, 20);
if (point instanceof Point(int x, int y)) {
    System.out.println("x: " + x + ", y: " + y);
}
```

## JEP 441: switch 表达式中的模式匹配

该特性扩展了 `switch` 表达式的功能，允许在 `switch` 表达式中使用模式匹配。这使得代码更加简洁和易读，减少了不必要的类型转换和条件判断。

```java
Object obj = "Hello";
String result = switch (obj) {
    case String s -> "It's a string: " + s;
    case Integer i -> "It's an integer: " + i;
    default -> "Unknown type";
};
System.out.println(result);
```

## JEP 442: 外部函数与内存 API（第三次预览）

外部函数与内存 API 提供了一种更安全、更高效的方式来调用本地代码和访问本地内存。它允许 Java 代码与本地库进行交互，扩展了 Java 的功能和应用场景。

该特性通过引入新的类和接口，提供了对本地函数调用和内存访问的封装，减少了使用 JNI（Java Native Interface）的复杂性和风险。

```java
// 调用本地函数示例
try (var lib = LibraryLoader.load("mylibrary")) {
    FunctionDescriptor fd = FunctionDescriptor.of(C_INT, C_INT, C_INT);
    MethodHandle add = lib.lookup("add", fd);
    int result = (int) add.invokeExact(10, 20);
    System.out.println("Result: " + result);
}
```

## JEP 443: 未命名模式和变量（预览）

未命名模式和变量是一种简化模式匹配代码的机制。它允许开发者在模式匹配中使用未命名的模式和变量，从而减少代码的冗余。

例如，在使用 `instanceof` 进行模式匹配时，如果不需要使用匹配到的变量，可以使用未命名模式：

```java
Object obj = "Hello";
if (obj instanceof String(_)) {
    System.out.println("It's a string");
}
```

## JEP 444: 虚拟线程

虚拟线程是一种轻量级的线程实现，它旨在简化高并发编程。与传统的操作系统线程不同，虚拟线程由 JVM 管理，而不是由操作系统调度。这使得虚拟线程的创建和销毁成本非常低，可以支持大量的并发线程。

虚拟线程适用于高并发的网络服务器、异步编程等场景。通过使用虚拟线程，开发者可以更方便地编写高并发的代码，提高应用程序的性能和响应速度。

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> System.out.println("Hello from virtual thread"));
}
```

## JEP 445: 未命名类和实例主方法（预览）

该特性进一步简化了 Java 源代码的结构，允许开发者编写更简洁的代码。它支持未命名类，即类可以没有显式的名称，并且提供了更简单的实例主方法声明方式。

```java
// 未命名类和实例主方法示例
void main() {
    System.out.println("Hello, World!");
}
```

## JEP 446: 作用域值（预览）

作用域值是一种在特定作用域内共享不可变数据的机制。它类似于线程局部变量，但更适用于虚拟线程和结构化并发等新的编程模型。

作用域值允许在大型程序中的组件之间安全有效地共享数据，而无需求助于方法参数。这对于减少代码冗余和提高代码的可维护性非常有帮助。

```java
final static ScopedValue<String> USER_NAME = new ScopedValue<>();

// 设置作用域值
ScopedValue.where(USER_NAME, "Alice")
           .run(() -> {
               // 在这个作用域内可以访问 USER_NAME
               System.out.println("Hello, " + USER_NAME.get());
           });
```

## JEP 448: 向量 API（第六次孵化）

向量 API 提供了一种高效的方式来进行向量计算，适用于科学计算、机器学习等领域。该特性通过引入一组新的类和接口，允许开发者使用硬件加速的向量指令来执行计算，从而提高性能。

```java
// 创建两个向量
IntVector vector1 = IntVector.fromArray(VectorSpecies.ofDefault(int.class), new int[]{1, 2, 3, 4}, 0);
IntVector vector2 = IntVector.fromArray(VectorSpecies.ofDefault(int.class), new int[]{5, 6, 7, 8}, 0);

// 执行向量加法
IntVector result = vector1.add(vector2);

// 将结果存储到数组中
int[] output = new int[4];
result.intoArray(output, 0);

// 输出结果
System.out.println(Arrays.toString(output)); // [6, 8, 10, 12]
```

## JEP 449: 弃用待移除的 Windows 32 位 x86 端口

随着计算机硬件的发展，64 位架构已经成为主流。为了简化 JDK 的开发和维护，该特性决定弃用并最终移除对 Windows 32 位 x86 架构的支持。这意味着未来的 JDK 版本将不再提供适用于 Windows 32 位 x86 处理器的版本。

这一变化将使 JDK 能够更专注于 64 位架构的优化和功能开发，提高性能和安全性。同时，也符合行业趋势，因为大多数现代计算机都已经采用 64 位操作系统和处理器。

## JEP 451: 准备禁止动态加载代理

动态加载代理是一种在运行时动态生成代理类的技术，它常用于 AOP（面向切面编程）等场景。然而，动态加载代理也存在一些安全风险和性能问题。

该特性准备禁止动态加载代理，以提高 Java 应用程序的安全性和性能。通过禁止动态加载代理，可以减少潜在的安全漏洞，并优化 JVM 的性能。

## JEP 452: 密钥封装机制 API

密钥封装机制 API 提供了一种标准化的方式来封装和解封密钥。密钥封装是一种加密技术，它允许将一个密钥（称为封装密钥）用于加密另一个密钥（称为被封装密钥），从而实现对被封装密钥的安全存储和传输。

```java
// 创建一个 KEM 对象，使用 ECIES 算法
KEM kem = KEM.getInstance("ECIES");

// 生成封装密钥和被封装密钥
KeyPair encapsulationKeyPair = kem.generateKeyPair();
byte[] encapsulatedKey = kem.encapsulate(encapsulationKeyPair.getPublic());
SecretKey unwrappedKey = kem.decapsulate(encapsulatedKey, encapsulationKeyPair.getPrivate());
```

## JEP 453: 结构化并发（预览）

结构化并发是一种多线程编程方法，旨在简化多线程代码的管理和错误处理。它将不同线程中运行的多个任务视为单个工作单元，从而提高了代码的可读性、可维护性和可靠性。

该特性引入了 `StructuredTaskScope` 类，允许开发者将任务拆分为多个并发子任务，并在它们自己的线程中执行。子任务必须在主任务继续之前完成，这使得错误处理更加简单，因为异常可以在一个地方捕获和处理。

```java
try (var scope = new StructuredTaskScope<Object>()) {
    Future<Integer> future1 = scope.fork(() -> doTask1());
    Future<String> future2 = scope.fork(() -> doTask2());
    scope.join();
    scope.throwIfFailed();

    Integer result1 = future1.resultNow();
    String result2 = future2.resultNow();
    // 处理结果
} catch (Exception e) {
    // 处理异常
}
```