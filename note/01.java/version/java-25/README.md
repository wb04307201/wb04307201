# Java 25

- **JEP 470**: PEM 编码的加密对象（预览）
- **JEP 502**: 稳定值（预览）
- **JEP 503**: 移除 32 位 x86 端口
- **JEP 505**: 结构化并发（第五次预览）
- **JEP 506**: 作用域值
- **JEP 507**: 模式、instanceof 和 switch 中的基本类型（第三次预览）
- **JEP 508**: 向量 API（第十次孵化）
- **JEP 509**: JFR CPU 时间分析（实验性）
- **JEP 510**: 密钥派生函数 API
- **JEP 511**: 模块导入声明
- **JEP 512**: 紧凑源文件和实例主方法
- **JEP 513**: 灵活的构造函数体
- **JEP 514**: 提前命令行优化
- **JEP 515**: 提前方法分析
- **JEP 518**: JFR 协作采样
- **JEP 519**: 紧凑对象头
- **JEP 520**: JFR 方法计时与追踪
- **JEP 521**: 分代式 Shenandoah

## JEP 470: PEM 编码的加密对象（预览）

PEM（Privacy Enhanced Mail）是一种广泛使用的编码格式，用于表示加密对象，如密钥、证书等。该特性引入了对 PEM 编码的加密对象的支持，使得 Java 能够更方便地处理这些常见的加密数据格式。

通过该特性，开发者可以轻松地读取和写入 PEM 编码的加密对象，例如：

```java
// 读取 PEM 编码的私钥
String pemPrivateKey = "-----BEGIN PRIVATE KEY-----\n...";
PrivateKey privateKey = PemReader.readPrivateKey(pemPrivateKey);

// 写入 PEM 编码的证书
X509Certificate certificate = ...;
String pemCertificate = PemWriter.writeCertificate(certificate);
```

这一特性对于与现有的加密基础设施和工具进行集成非常有用，简化了加密对象的处理流程。

## JEP 502: 稳定值（预览）

稳定值是一种新的编程概念，旨在提供一种不可变且线程安全的数据共享机制。与传统的线程局部变量不同，稳定值可以在多个线程之间共享，而无需担心并发访问的问题。

稳定值适用于需要在多个线程之间共享常量或配置数据的场景，例如应用程序的配置参数、全局常量等。通过使用稳定值，可以避免使用锁或其他同步机制，提高程序的性能和可维护性。

```java
// 定义一个稳定值
StableValue<String> configValue = StableValue.of("default_value");

// 在多个线程中访问稳定值
Runnable task = () -> {
    String value = configValue.get();
    System.out.println("Thread " + Thread.currentThread().getName() + ": " + value);
};

new Thread(task).start();
new Thread(task).start();
```

## JEP 503: 移除 32 位 x86 端口

随着计算机硬件的发展，64 位架构已经成为主流。为了简化 JDK 的开发和维护，该特性决定移除对 32 位 x86 架构的支持。这意味着从 Java 25 开始，JDK 将不再提供适用于 32 位 x86 处理器的版本。

这一变化将使 JDK 能够更专注于 64 位架构的优化和功能开发，提高性能和安全性。同时，也符合行业趋势，因为大多数现代计算机都已经采用 64 位操作系统和处理器。

## JEP 505: 结构化并发（第五次预览）

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

## JEP 506: 作用域值

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

## JEP 507: 模式、instanceof 和 switch 中的基本类型（第三次预览）

该特性扩展了模式匹配的功能，允许在 `instanceof` 操作符和 `switch` 表达式中使用基本类型。这使得代码更加简洁和易读，减少了不必要的类型转换。

例如，在使用 `instanceof` 时，可以直接对基本类型进行判断：

```java
Object obj = 42;
if (obj instanceof int i) {
    System.out.println("It's an int: " + i);
}
```

在 `switch` 表达式中，也可以使用基本类型进行匹配：

```java
int value = 2;
String result = switch (value) {
    case 1 -> "One";
    case 2 -> "Two";
    case 3 -> "Three";
    default -> "Unknown";
};
System.out.println(result);
```

## JEP 508: 向量 API（第十次孵化）

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

## JEP 509: JFR CPU 时间分析（实验性）

JFR（Java Flight Recorder）是一种用于记录和分析 Java 应用程序性能的工具。该特性引入了 CPU 时间分析功能，允许开发者深入了解应用程序的 CPU 使用情况，识别性能瓶颈。

通过 JFR CPU 时间分析，开发者可以获取有关方法执行时间、线程 CPU 使用率等详细信息，从而优化应用程序的性能。

## JEP 510: 密钥派生函数 API

密钥派生函数 API 提供了一种标准化的方式来从初始密钥和其他数据派生额外的密钥。这在现代加密中非常重要，因为它允许为不同的加密目的生成多个不同的密钥，避免密钥重复使用带来的安全隐患。

```java
// 创建一个 KDF 对象，使用 HKDF-SHA256 算法
KDF hkdf = KDF.getInstance("HKDF-SHA256");

// 创建 Extract 和 Expand 参数规范
AlgorithmParameterSpec params =
    HKDFParameterSpec.ofExtract()
                     .addIKM(initialKeyMaterial) // 设置初始密钥材料
                     .addSalt(salt)             // 设置盐值
                     .thenExpand(info, 32);     // 设置扩展信息和目标长度

// 派生一个 32 字节的 AES 密钥
SecretKey key = hkdf.deriveKey("AES", params);
```

## JEP 511: 模块导入声明

模块导入声明提供了一种更简洁的方式来导入模块中的包。它允许开发者在一个地方声明需要导入的模块和包，减少了代码的冗余。

```java
// 使用模块导入声明
import com.example.module.*;
import static com.example.module.ClassName.*;

public class MyClass {
    // 类体
}
```

## JEP 512: 紧凑源文件和实例主方法

该特性进一步简化了 Java 源代码的结构，允许开发者编写更简洁的代码。它支持紧凑源文件格式，即未命名的类可以省略类名，并且提供了更简单的实例主方法声明方式。

```java
// 紧凑源文件示例
void main() {
    System.out.println("Hello, World!");
}
```

## JEP 513: 灵活的构造函数体

灵活的构造函数体允许开发者在构造函数中使用更灵活的代码结构。它支持在构造函数中使用 `yield` 语句来返回值，使得构造函数的编写更加简洁和易读。

```java
class MyClass {
    private final int value;

    MyClass(int initialValue) {
        value = switch (initialValue) {
            case 0 -> 0;
            case 1 -> 1;
            default -> yield initialValue * 2;
        };
    }
}
```

## JEP 514: 提前命令行优化

提前命令行优化是一种在应用程序启动前对命令行参数进行优化的技术。它可以减少应用程序启动时的开销，提高启动速度。

通过提前命令行优化，JVM 可以在启动前分析命令行参数，并进行一些预处理和优化，例如类加载、链接等，从而减少启动时的延迟。

## JEP 515: 提前方法分析

提前方法分析是一种在编译时对方法进行分析和优化的技术。它可以在方法被调用之前对其进行静态分析，识别潜在的性能问题和优化机会。

通过提前方法分析，编译器可以生成更高效的代码，提高应用程序的性能。例如，它可以识别出可以内联的方法，减少方法调用的开销。

## JEP 518: JFR 协作采样

JFR 协作采样是一种改进的 JFR 采样机制，它允许不同的线程协作进行采样，减少了采样的开销和对应用程序性能的影响。

通过 JFR 协作采样，开发者可以更准确地获取应用程序的性能数据，而不会因为采样过程本身对性能产生显著影响。

## JEP 519: 紧凑对象头

紧凑对象头是一种优化对象内存布局的技术，它可以减少对象头的大小，从而节省内存空间。这对于内存敏感的应用程序非常重要，例如大规模的数据处理和缓存系统。

通过紧凑对象头，JVM 可以更高效地管理内存，减少内存碎片，提高内存使用效率。

## JEP 520: JFR 方法计时与追踪

JFR 方法计时与追踪功能允许开发者记录方法的执行时间和调用栈信息，帮助识别性能瓶颈和调试应用程序。

通过 JFR 方法计时与追踪，开发者可以获取有关方法执行的详细信息，例如方法的调用次数、平均执行时间、最大执行时间等，从而优化应用程序的性能。

## JEP 521: 分代式 Shenandoah

分代式 Shenandoah 是一种改进的垃圾回收算法，它结合了分代收集和 Shenandoah 垃圾回收器的优点，提高了垃圾回收的效率和性能。

分代式 Shenandoah 将堆内存分为不同的代，例如年轻代和老年代，并针对不同代的特点采用不同的垃圾回收策略。这样可以更有效地回收垃圾，减少垃圾回收的停顿时间，提高应用程序的响应速度。。