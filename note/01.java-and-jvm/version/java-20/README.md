<!--
module:
  parent: java
  slug: java/version/java-20
  type: article
  category: 主模块子文章
  summary: Java 20：7 个 JEP，含作用域值孵化、记录模式预览、虚拟线程预览
-->

# Java 20

## 引言：变更说明

Java 20 是 7 个 JEP 的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

### 相关阅读

← [Java 19](../java-19/README.md) · [Java 21](../java-21/README.md)

---

- **JEP 429**: 作用域值（孵化器）
- **JEP 432**: 记录模式（第二次预览）
- **JEP 433**: switch 表达式中的模式匹配（第四次预览）
- **JEP 434**: 外部函数与内存 API（第二次预览）
- **JEP 436**: 虚拟线程（第二次预览）
- **JEP 437**: 结构化并发（第二次孵化器）
- **JEP 438**: 向量 API（第五次孵化器）

## JEP 429: 作用域值（孵化器）

作用域值是一种在特定作用域内共享不可变数据的机制。它为在大型程序组件之间安全有效地共享数据提供了一种新方式，无需借助方法参数传递。与线程局部变量不同，作用域值更适用于虚拟线程和结构化并发等新的编程模型，有助于减少代码冗余，提高代码可维护性。

```java
final static ScopedValue<String> USER_NAME = ScopedValue.newInstance();

// 设置作用域值
ScopedValue.where(USER_NAME, "Alice")
           .run(() -> {
               // 在这个作用域内可以访问 USER_NAME
               System.out.println("Hello, " + USER_NAME.get());
           });
```

## JEP 432: 记录模式（第二次预览）

记录模式扩展了模式匹配的功能，允许在模式匹配中直接解构记录类的属性。这使得代码更加简洁和易读，减少了不必要的属性访问代码。例如，可以更方便地从记录对象中提取特定属性进行处理。

```java
record Point(int x, int y) {}

Point point = new Point(10, 20);

// 使用记录模式解构
if (point instanceof Point(int x, int y)) {
    System.out.println("X: " + x + ", Y: " + y);
}
```

## JEP 433: switch 表达式中的模式匹配（第四次预览）

该特性进一步增强了 `switch` 表达式的功能，允许在 `switch` 中使用更丰富的模式匹配。除了支持类型模式外，还可以使用记录模式等，使得代码更加简洁和灵活，能够处理更复杂的条件逻辑。

```java
record Rectangle(int width, int height) {}
record Circle(int radius) {}

Object shape = new Rectangle(10, 20);

String description = switch (shape) {
    case Rectangle(int w, int h) -> "Rectangle with width " + w + " and height " + h;
    case Circle(int r) -> "Circle with radius " + r;
    default -> "Unknown shape";
};

System.out.println(description);
```

## JEP 434: 外部函数与内存 API（第二次预览）

外部函数与内存 API 提供了一种更安全、更高效的方式来调用本地代码和操作本地内存。它允许 Java 程序直接访问外部函数库，并与本地数据结构进行交互，而无需依赖 JNI（Java Native Interface），从而提高了性能和安全性。

```java
// 使用外部函数与内存 API 调用 C 标准库
import java.lang.foreign.*;
import java.lang.invoke.*;

public class ForeignFunctionExample {
    public static void main(String[] args) throws Throwable {
        try (Arena arena = Arena.ofAuto()) {
            // 在本地内存中创建字符串
            MemorySegment str = arena.allocateUtf8String("Hello");
            // 查找 strlen 函数
            Linker linker = Linker.nativeLinker();
            SymbolLookup lookup = linker.defaultLookup();
            MemorySegment strlenAddr = lookup.find("strlen").get();
            // 创建方法句柄并调用
            FunctionDescriptor fd = FunctionDescriptor.of(ValueLayout.JAVA_LONG, ValueLayout.ADDRESS);
            MethodHandle strlen = linker.downcallHandle(strlenAddr, fd);
            long len = (long) strlen.invoke(str);
            System.out.println("Length: " + len);
        }
    }
}
```

## JEP 436: 虚拟线程（第二次预览）

虚拟线程是一种轻量级的线程实现，旨在简化高并发编程。与传统的操作系统线程不同，虚拟线程由 JVM 管理，创建和切换的成本更低，可以轻松创建大量虚拟线程来处理并发任务，提高了程序的吞吐量和响应能力。

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 1000).forEach(i -> {
        executor.submit(() -> {
            System.out.println("Task " + i + " running on " + Thread.currentThread());
            return i;
        });
    });
}
```

## JEP 437: 结构化并发（第二次孵化器）

结构化并发是一种多线程编程方法，它将不同线程中运行的多个任务视为单个工作单元。通过引入 `StructuredTaskScope` 类，开发者可以将任务拆分为多个并发子任务，并在它们自己的线程中执行。子任务必须在主任务继续之前完成，这使得错误处理更加简单，因为异常可以在一个地方捕获和处理，提高了代码的可读性、可维护性和可靠性。

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

## JEP 438: 向量 API（第五次孵化器）

向量 API 提供了一种高效的方式来进行向量计算，适用于科学计算、机器学习等领域。该特性通过引入一组新的类和接口，允许开发者使用硬件加速的向量指令来执行计算，从而提高性能。开发者可以利用向量的并行计算能力，对大量数据进行快速处理。

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
System.out.println(java.util.Arrays.toString(output)); // [6, 8, 10, 12]
```

---

## 其他新特性（非 JEP）

Java 20 还包含多项非 JEP 的改进，以下列出对开发者最实用的特性：

### 核心库

#### Unicode 15.0 支持

`java.lang.Character` 升级到 Unicode 15.0，新增 4,489 个字符（总计 149,186）、2 种新文字、20 个新表情符号和 4,193 个 CJK 汉字。

#### Thread.suspend/resume 改为抛异常

`Thread.suspend()` 和 `Thread.resume()` 现在抛出 `UnsupportedOperationException`。这些方法自 JDK 1.2 起就因死锁倾向被弃用。

#### Thread.stop 改为抛异常

`Thread.stop()` 现在抛出 `UnsupportedOperationException`。通过抛出 `ThreadDeath` 停止线程本质上是不安全的。

#### URL 构造函数弃用

URL 构造函数已弃用。请使用 `java.net.URI` 解析/构造 URL。新增 `URL::of(URI, URLStreamHandler)` 方法。

#### HTTP Client 改进

- 默认 Keep Alive 时间从 1200 秒减少到 30 秒
- HTTP 响应输入流在线程中断时抛出 `IOException`
- HTTP/2 空闲连接超时：新增 `jdk.httpclient.keepalivetimeout.h2` 属性

```java
// URL 构造函数替代方案
URL url = URL.of(URI.create("https://example.com"), null);
```

#### macOS 不再规范化文件路径为 Unicode 格式 D

macOS 上的文件名不再规范化为 Apple 的 Unicode Normalization Format D 变体。可通过 `jdk.nio.path.useNormalizationFormD=true` 重新启用。

#### BreakIterator 字形支持

`BreakIterator` 字符边界分析现在符合 Unicode 标准附件 #29 的扩展字形簇。

#### CLDR v42 支持

语言环境数据升级到 Unicode CLDR v42。主要变更：NBSP/NNBSP 前缀到 AM/PM 时间格式、中国每周第一天修正。

### 安全

#### TLS 密钥交换命名组

新增 API `SSLParameters.getNamedGroups()` 和 `SSLParameters.setNamedGroups()` 自定义 TLS/DTLS 连接的密钥交换命名组。

#### 禁用 TLS_ECDH 密码套件

TLS_ECDH 密码套件默认禁用（添加到 `jdk.tls.disabledAlgorithms` 中的 "ECDH"），不保持前向保密。

#### Poly1305/ChaCha20 硬件加速

- x86_64 AVX512 平台上的 Poly1305 MAC 算法优化
- x86_64（AVX/AVX2/AVX512）和 aarch64（Advanced SIMD）上的 ChaCha20 密码优化

#### JNDI LDAP 对象反序列化默认禁用

`com.sun.jndi.ldap.object.trustSerialData` 默认改为 `false`。透明反序列化现在需要显式启用。

#### JFR 安全事件

新增 `jdk.InitialSecurityProperty`（默认启用）和 `jdk.SecurityProviderService`（默认禁用）JFR 事件。

#### DTLS 恢复使用 HelloVerifyRequest

SunJSSE DTLS 实现现在默认对所有握手（新建和恢复）交换 cookie。

### HotSpot / JVM

#### G1 垃圾回收改进

- 新增 "G1 Concurrent GC" `GarbageCollectorMXBean`，报告 Remark 和 Cleanup GC 暂停
- 改进 G1 并发细化线程控制，通常分配更少线程
- G1 预防性 GC 默认禁用

#### 遗留并行类加载工作区弃用

HotSpot 中自 JDK 6 以来的非并行类加载器遗留工作区现在弃用并默认禁用。受影响加载器可能看到 `LinkageError`。可通过 `-XX:+EnableWaitForParallelLoad` 临时重新启用。

### 工具

#### javac 复合赋值有损转换警告

新增 `-Xlint:lossy-conversions` 选项警告复合赋值中可能有损的类型转换。

#### javac 移除 Java 7 支持

已移除对 `-source`、`-target` 和 `--release` 值 `7`/`1.7` 的支持。

#### jmod --compress 选项

`jmod` 工具现接受 `--compress=zip-[0-9]` 指定 JMOD 存档压缩级别。

### 管理

#### JMX 连接使用 ObjectInputFilter

默认 JMX 代理现在在 RMI 连接上设置 `ObjectInputFilter` 以限制反序列化类型。

#### JMX 管理 Applet 弃用

JMX 管理 Applet（m-let）功能弃用待移除。`MLet`、`MLetContent`、`PrivateMLet`、`MLetMBean` 受影响。

#### JDI setValue 禁止修改 final 字段

规范更新要求 `setValue()` 目标字段为非 final（静态和实例）。

---

← [返回 Java 版本特性](../README.md)