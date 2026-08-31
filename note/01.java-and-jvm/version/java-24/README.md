<!--
module:
  parent: java
  slug: java/version/java-24
  type: article
  category: 主模块子文章
  summary: Java 24：24 个 JEP，含分代式 Shenandoah 实验性、紧凑对象头实验性、结构化并发孵化
  depth: ⭐⭐
-->

# Java 24

## 引言：变更说明

Java 24 是 24 个 JEP 的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

### 相关阅读

← [Java 23](../java-23/README.md) · [Java 25](../java-25/README.md)

---

- **JEP 404**: 分代式 Shenandoah（实验性）
- **JEP 450**: 紧凑对象头（实验性）
- **JEP 472**: 准备限制 JNI 的使用
- **JEP 475**: G1 的后期屏障扩展
- **JEP 478**: 密钥派生函数 API（预览）
- **JEP 479**: 移除 Windows 32 位 x86 端口
- **JEP 483**: 提前类加载与链接
- **JEP 484**: 类文件 API
- **JEP 485**: 流收集器
- **JEP 486**: 永久禁用安全管理器
- **JEP 487**: 作用域值（第四次预览）
- **JEP 488**: 模式、instanceof 和 switch 中的基本类型（第二次预览）
- **JEP 489**: 向量 API（第九次孵化）
- **JEP 490**: ZGC：移除非分代模式
- **JEP 491**: 无需固定同步虚拟线程
- **JEP 492**: 灵活的构造函数体（第三次预览）
- **JEP 493**: 无 JMODs 链接运行时镜像
- **JEP 494**: 模块导入声明（第二次预览）
- **JEP 495**: 简单源文件和实例主方法（第四次预览）
- **JEP 496**: 量子抗性模块 - 基于格的密钥封装机制
- **JEP 497**: 量子抗性模块 - 基于格的数字签名算法
- **JEP 498**: 使用 sun.misc.Unsafe 中的内存访问方法时发出警告
- **JEP 499**: 结构化并发（第四次预览）
- **JEP 501**: 弃用 32 位 x86 端口以待移除

## JEP 450: 紧凑对象头（实验性）

紧凑对象头旨在优化对象的内存布局，减少对象头的大小。对象头通常包含对象的相关元数据，如标记字、类指针等。通过紧凑对象头技术，可以压缩这些元数据的存储空间，从而节省内存。这对于内存敏感的应用程序，如大规模数据处理和缓存系统，能够显著提高内存使用效率，减少内存碎片。

## JEP 404: 分代式 Shenandoah（实验性）

分代式 Shenandoah 是对 Shenandoah 垃圾回收器的改进，引入了分代收集的概念。它将堆内存划分为年轻代和老年代，针对不同代的特点采用不同的垃圾回收策略。年轻代采用复制算法，快速回收短生命周期对象；老年代采用 Shenandoah 原有的并发标记压缩算法，减少垃圾回收停顿时间，提高应用程序的响应速度。这一特性对于内存占用较大且对响应时间要求较高的应用场景非常有帮助。

## JEP 472: 准备限制 JNI 的使用

JNI（Java Native Interface）允许 Java 代码与本地代码（如 C/C++）进行交互，但这也带来了一些安全性和性能方面的问题。该特性准备对 JNI 的使用进行限制，以增强 Java 平台的安全性和稳定性。具体措施可能包括限制某些 JNI 函数的调用、增加安全检查等，确保 JNI 的使用不会对 Java 应用程序造成潜在风险。

## JEP 475: G1 的后期屏障扩展

G1（Garbage - First）垃圾回收器是一种面向服务端应用的垃圾回收器。该特性对 G1 的后期屏障进行了扩展，后期屏障是在垃圾回收过程中用于跟踪对象引用变化的一种机制。通过扩展后期屏障，G1 可以更准确地跟踪对象引用，优化垃圾回收的标记和清理过程，提高垃圾回收的效率和性能，减少垃圾回收对应用程序性能的影响。

## JEP 478: 密钥派生函数 API（预览）

密钥派生函数 API 提供了一种标准化的方式来从初始密钥和其他数据派生额外的密钥。在现代加密中，为了避免密钥重复使用带来的安全隐患，通常需要为不同的加密目的生成多个不同的密钥。该 API 允许开发者使用统一的接口调用不同的密钥派生算法，如 HKDF、PBKDF2 等，方便地实现密钥派生功能，提高加密应用的安全性和开发效率。

```java
// 示例代码：使用 HKDF 算法派生密钥
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.security.spec.AlgorithmParameterSpec;
import java.security.spec.HKDFParameterSpec;
import java.security.KeyDerivationFunction;

public class KeyDerivationExample {
    public static void main(String[] args) throws Exception {
        // 初始密钥材料
        byte[] initialKeyMaterial = "initial_key_material".getBytes();
        // 盐值
        byte[] salt = "salt_value".getBytes();
        // 扩展信息
        byte[] info = "info_data".getBytes();

        // 创建 KDF 对象，使用 HKDF - SHA256 算法
        KeyDerivationFunction hkdf = KeyDerivationFunction.getInstance("HKDF - SHA256");

        // 创建 Extract 和 Expand 参数规范
        AlgorithmParameterSpec params =
                HKDFParameterSpec.ofExtract()
                        .addIKM(initialKeyMaterial)
                        .addSalt(salt)
                        .thenExpand(info, 32);

        // 派生一个 32 字节的 AES 密钥
        SecretKey key = hkdf.deriveKey(new SecretKeySpec(new byte[0], "AES"), params);

        System.out.println("Derived key length: " + key.getEncoded().length);
    }
}
```

## JEP 479: 移除 Windows 32 位 x86 端口

随着计算机硬件的发展，64 位架构已经成为主流。为了简化 JDK 的开发和维护，该特性决定移除对 Windows 32 位 x86 架构的支持。这意味着从 Java 24 开始，JDK 将不再提供适用于 Windows 32 位 x86 处理器的版本。这一变化将使 JDK 能够更专注于 64 位架构的优化和功能开发，提高性能和安全性，同时符合行业趋势，因为大多数现代 Windows 计算机都已经采用 64 位操作系统和处理器。

## JEP 483: 提前类加载与链接

提前类加载与链接允许在应用程序启动前对类进行加载和链接操作。传统的类加载和链接是在应用程序运行时动态进行的，这会增加应用程序的启动时间。通过提前进行这些操作，JVM 可以在启动前完成类的初始化准备工作，减少启动时的延迟，提高应用程序的启动速度。这对于需要快速启动的应用程序，如桌面应用和服务器应用，非常有帮助。

## JEP 484: 类文件 API

类文件 API 提供了一组用于操作 Java 类文件的接口和类。开发者可以使用该 API 读取、修改和生成 Java 类文件，实现动态代码生成、类文件分析等功能。这对于一些需要动态生成代码或对类文件进行定制化处理的框架和工具非常有用，例如 AOP（面向切面编程）框架、代码优化工具等。

```java
// 示例代码：使用类文件 API 读取类文件信息
import java.lang.classfile.*;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

public class ClassFileApiExample {
    public static void main(String[] args) throws IOException {
        byte[] classBytes = Files.readAllBytes(Paths.get("MyClass.class"));
        ClassFile classFile = ClassFile.parse(classBytes);

        System.out.println("Class name: " + classFile.getName());
        System.out.println("Super class name: " + classFile.getSuperName());

        for (FieldInfo field : classFile.getFields()) {
            System.out.println("Field: " + field.getName() + ", type: " + field.getDescriptor());
        }

        for (MethodInfo method : classFile.getMethods()) {
            System.out.println("Method: " + method.getName() + ", descriptor: " + method.getDescriptor());
        }
    }
}
```

## JEP 485: 流收集器

流收集器（Stream Gatherers）是 Java 流 API 的重大扩展，引入了 `Stream::gather(Gatherer)` 方法。与传统的 `collect()` 不同，`gather()` 支持多阶段处理、状态维护和中间输出，可以实现更复杂的流操作，如窗口化、去重、限流等。开发者可以通过 `Gatherer` 接口自定义收集逻辑，而 JDK 也提供了 `Gatherers` 工具类中的常用实现（如 `fold`、`mapConcurrent`、`windowFixed` 等）。

```java
import java.util.List;
import java.util.stream.Gatherers;

public class StreamGatherersExample {
    public static void main(String[] args) {
        List<Integer> numbers = List.of(1, 2, 3, 4, 5);

        // 使用 Gatherers.fold 实现累加
        Integer sum = numbers.stream()
            .gather(Gatherers.fold(() -> 0, (acc, n) -> acc + n))
            .toList()
            .getFirst();
        System.out.println("Sum: " + sum); // Sum: 15

        // 使用 windowFixed 实现滑动窗口
        List.of("a", "b", "c", "d", "e").stream()
            .gather(Gatherers.windowFixed(3))
            .forEach(System.out::println);
        // 输出: [a, b, c], [b, c, d], [c, d, e]
    }
}
```

## JEP 486: 永久禁用安全管理器

安全管理器是 Java 平台中用于实现安全策略的组件，它可以限制 Java 应用程序的权限，如文件访问、网络访问等。然而，随着 Java 安全模型的发展和其他安全机制的不断完善，安全管理器的使用逐渐减少。该特性决定永久禁用安全管理器，以简化 Java 平台的安全架构，减少安全管理的复杂性。禁用安全管理器后，Java 应用程序将不再依赖该组件进行安全控制，而是采用更现代的安全机制。

## JEP 487: 作用域值（第四次预览）

作用域值是一种在特定作用域内共享不可变数据的机制。它类似于线程局部变量，但更适用于虚拟线程和结构化并发等新的编程模型。作用域值允许在大型程序中的组件之间安全有效地共享数据，而无需求助于方法参数。这对于减少代码冗余和提高代码的可维护性非常有帮助。在第四次预览中，移除了 `ScopedValue.where()` 的一些旧方法。

```java
import java.lang.ScopedValue;

public class ScopedValuesExample {
    private static final ScopedValue<String> USER_NAME = ScopedValue.newInstance();

    public static void main(String[] args) {
        ScopedValue.where(USER_NAME, "Alice")
            .run(() -> {
                System.out.println("Hello, " + USER_NAME.get());
                nestedScope();
            });
    }

    private static void nestedScope() {
        ScopedValue.where(USER_NAME, "Bob")
            .run(() -> {
                System.out.println("Nested scope: " + USER_NAME.get());
            });
    }
}
```

## JEP 488: 模式、instanceof 和 switch 中的基本类型（第二次预览）

该特性扩展了模式匹配的功能，允许在 `instanceof` 操作符和 `switch` 表达式中使用基本类型。这使得代码更加简洁和易读，减少了不必要的类型转换。在第二次预览中，可能会根据用户反馈对语法和语义进行进一步的调整和完善，提高该特性的稳定性和可用性。

```java
public class PatternMatchingWithPrimitivesExample {
    public static void main(String[] args) {
        Object obj = 42;
        if (obj instanceof int i) {
            System.out.println("It's an int: " + i);
        }

        int value = 2;
        String result = switch (value) {
            case 1 -> "One";
            case 2 -> "Two";
            case 3 -> "Three";
            default -> "Unknown";
        };
        System.out.println(result);
    }
}
```

## JEP 489: 向量 API（第九次孵化）

向量 API 提供了一种高效的方式来进行向量计算，适用于科学计算、机器学习等领域。该特性通过引入一组新的类和接口，允许开发者使用硬件加速的向量指令来执行计算，从而提高性能。在第九次孵化中，可能会对向量 API 的功能、性能和兼容性进行进一步的优化和测试，为正式发布做准备。

```java
import jdk.incubator.vector.*;

VectorSpecies<Integer> SPECIES = IntVector.SPECIES_256;

IntVector vector1 = IntVector.fromArray(SPECIES, new int[]{1, 2, 3, 4}, 0);
IntVector vector2 = IntVector.fromArray(SPECIES, new int[]{5, 6, 7, 8}, 0);

IntVector result = vector1.add(vector2);

int[] output = new int[4];
result.intoArray(output, 0);

System.out.println(java.util.Arrays.toString(output)); // [6, 8, 10, 12]
```

## JEP 490: ZGC：移除非分代模式

ZGC（Z Garbage Collector）是一种高性能的垃圾回收器，它具有低延迟的特点。该特性移除了 ZGC 的非分代模式，使 ZGC 专注于分代收集策略。分代收集可以根据对象的生命周期将堆内存分为年轻代和老年代，并针对不同代采用不同的垃圾回收策略，从而提高垃圾回收的效率和性能。

## JEP 491: 无需固定同步虚拟线程

该特性优化了虚拟线程的同步机制，使得虚拟线程在执行同步操作时不需要固定绑定到特定的载体线程。这减少了虚拟线程在同步块中的阻塞对其他虚拟线程的影响，提高了高并发场景下的整体性能。

## JEP 492: 灵活的构造函数体（第三次预览）

灵活的构造函数体允许在调用父类构造函数（`super(...)`）之前执行一些语句。在第三次预览中，该特性进一步完善了语义和实现，使得构造函数编写更加灵活。这些语句在代码上写在 `super` 调用前，但实际执行是在父类构造函数调用之后、子类构造函数体之前。

```java
class Child extends Parent {
    private final int x;

    Child(int x) {
        int validatedX = validateX(x); // 在 super 调用前的语句
        super(validatedX);
        this.x = x;
    }

    private int validateX(int x) {
        if (x < 0) {
            throw new IllegalArgumentException("x must be non-negative");
        }
        return x;
    }
}
```

## JEP 493: 无 JMODs 链接运行时镜像

该特性允许 `jlink` 工具在不使用 JMOD 文件的情况下创建运行时镜像。它支持使用 JAR 文件作为输入源，简化了运行时镜像的构建过程，使开发者可以更灵活地定制 Java 运行时环境。

## JEP 494: 模块导入声明（第二次预览）

模块导入声明提供了一种更简洁的方式来导入模块中的包。在第二次预览中，该特性可能进一步完善了语法和实现。它允许开发者在一个地方声明需要导入的模块和包，减少了代码的冗余。

## JEP 495: 简单源文件和实例主方法（第四次预览）

该特性进一步简化了 Java 源代码的结构，允许开发者编写更简洁的代码。它支持简单源文件格式，即未命名的类可以省略类名，并且提供了更简单的实例主方法声明方式。在第四次预览中，该特性已经非常接近正式发布。

```java
// 简单源文件示例
void main() {
    System.out.println("Hello, World!");
}
```

## JEP 496: 量子抗性模块 - 基于格的密钥封装机制

该特性引入了基于格的密码学算法来实现密钥封装机制（KEM），以应对未来量子计算机可能带来的安全威胁。这是 Java 在量子安全密码学领域的重要一步，为未来的安全通信提供了基础。

## JEP 497: 量子抗性模块 - 基于格的数字签名算法

与 JEP 496 配套，该特性引入了基于格的数字签名算法（DSA），同样是为了应对量子计算带来的安全挑战。这些算法共同构成了 Java 的量子抗性加密能力。

## JEP 498: 使用 sun.misc.Unsafe 中的内存访问方法时发出警告

该特性在使用 `sun.misc.Unsafe` 类中的内存访问方法时发出警告，为后续移除这些方法做准备。这鼓励开发者迁移到更安全、更标准的内存操作方式（如外部函数与内存 API）。

## JEP 499: 结构化并发（第四次预览）

结构化并发是一种多线程编程方法，旨在简化多线程代码的管理和错误处理。在第四次预览中，该特性进一步完善了 API 的设计和功能。它引入了 `StructuredTaskScope` 类，允许开发者将任务拆分为多个并发子任务。

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<Integer> future1 = scope.fork(() -> doTask1());
    Future<String> future2 = scope.fork(() -> doTask2());
    scope.join();
    scope.throwIfFailed();

    Integer result1 = future1.resultNow();
    String result2 = future2.resultNow();
    // 处理结果
}
```

## JEP 501: 弃用 32 位 x86 端口以待移除

该特性将 32 位 x86 端口标记为弃用状态，为未来版本中的移除做准备。随着 64 位架构的普及，32 位 x86 端口的使用已经越来越少，移除它可以简化 JDK 的维护负担。

---

## 其他新特性（非 JEP）

Java 24 还包含大量非 JEP 的改进，以下列出对开发者最实用的特性：

### 核心库

#### Reader.of(CharSequence)

新静态工厂方法从 `CharSequence`（如 `String`、`StringBuilder`）获取 `Reader`。在某些情况下比 `StringReader` 更高效。

```java
Reader reader = Reader.of("Hello, World!");
Reader reader2 = Reader.of(stringBuilder);
```

#### Unicode 16.0 支持

升级到 Unicode 16.0，新增 5,185 个字符（总计 154,998）。7 种新文字：Garay、Gurung Khema、Kirat Rai、Ol Onal、Sunuwar、Todhri、Tulu-Tigalari。

#### Process.waitFor(Duration)

新增使用 `java.time.Duration` 的重载方法，替代原始超时值+单位，减少用户困惑。

```java
Process process = new ProcessBuilder("long-task").start();
process.waitFor(Duration.ofSeconds(30));
```

#### ProcessBuilder Windows 引号扩展

扩展参数字符串引号以包含所有 Unicode 空格分隔符字符（`Character.isSpaceChar`）。

#### HTTP 最大头部大小限制

`HttpURLConnection` 和 `HttpClient` 的默认最大响应头部大小为 384kB。可通过 `jdk.http.maxHeaderSize` 系统属性配置。

#### HttpClient 改进

- 中间响应限制：`jdk.httpclient.maxNonFinalResponses`（默认 8）
- HPack 动态表限制：`jdk.httpclient.maxLiteralWithIndexing`（默认 512）
- `Expect: 100-Continue` 行为对齐 RFC 9110
- 用户设置的 `Authorization`/`Proxy-Authorization` 头部不再被认证器覆盖

#### Socket.connect 行为变更

如果连接无法建立或超时，`Socket.connect()` 现在关闭 Socket。之前它使 Socket 保持"无用"状态。

#### VirtualThreadSchedulerMXBean

新增 JMX 监控/管理接口，用于虚拟线程调度器。支持监控目标并行度、使用线程数、排队虚拟线程数，以及动态更改目标并行度。

### 安全

#### java.security 文件包含

`java.security` 属性文件现支持 `include <path>` 指令包含其他属性文件。

#### SHA3 性能提升

SHA3-224/256/384/512 改进 6-27%。AVX-512 平台通过新内在实现额外提升 30-40%。

#### TLS 会话票据计数

新系统属性 `jdk.tls.server.newSessionTicketCount`（0-10，默认 1）设置每个会话发送的 TLSv1.3 恢复票据数量。

#### TLS 密码套件通配符禁用

`jdk.tls.disabledAlgorithms` 现支持 `*` 通配符（如 `TLS_RSA_*` 禁用所有以该前缀开头的密码套件）。

#### TLS_RSA 密码套件默认禁用

`TLS_RSA_*` 默认添加到 `jdk.tls.disabledAlgorithms`，缺乏前向保密。

#### Entrust 证书不信任

2024 年 11 月 11 日后由 Entrust/AffirmTrust 根证书签发的 TLS 服务器证书将被拒绝。

#### SunPKCS11 AES CTS 支持

新增 AES/CTS/NoPadding 变换支持。新 `cipherTextStealingVariant` 配置属性（CS1/CS2/CS3）。

### HotSpot / JVM

#### Unified Logging 多行解析

多行日志消息中的换行后输出特殊空装饰器 `[ ]` 加空格，用于无歧义解析。

#### LockingMode 标志弃用

`LockingMode` 标志、`LM_LEGACY`（1）和 `LM_MONITOR`（0）弃用。仅支持 `LM_LIGHTWEIGHT`（JDK 23 起默认）。

#### RedefineClasses 始终验证

在 `RedefineClasses` 期间，类字节码现在由类文件验证器验证，无论已弃用的 `-Xverify` 设置如何。

### 工具

#### jar --keep-old-files / -k

`jar xkf foo.jar` 或 `jar --extract --keep-old-files --file foo.jar` 防止提取时覆盖现有文件。

#### jar --dir / -C

`jar -xf foo.jar -C /tmp/bar/` 指定提取目标目录。

#### jcmd 虚拟线程诊断

新增两个 `jcmd` 命令：
- `Thread.vthread_scheduler` — 打印调度器信息
- `Thread.vthread_pollers` — 打印阻塞网络 I/O 的 I/O 轮询器

#### javadoc 外部规范摘要页

API 文档新增摘要页，列出 Java SE 和 JDK API 引用的外部规范。

#### jpackage WiX v4/v5 支持

`jpackage` 在 Windows 上支持 WiX v4 和 v5（除 v3 外）。自动选择最新安装版本。

#### javac 局部类静态上下文强制

在静态上下文中创建内部局部类实例的 `new` 表达式必须出现在同一静态上下文中。

#### jlink ALL-MODULE-PATH 需要 --module-path

`jlink --add-modules ALL-MODULE-PATH` 现在需要显式 `--module-path` 选项。

#### 移除和弃用的启动器选项

- **移除**: `-t`、`-tm`、`-Xfuture`、`-checksource`、`-cs`、`-noasyncgc`
- **弃用**: `-verbosegc`、`-noclassgc`、`-verify`、`-verifyremote`、`-ss`、`-ms`、`-mx`

### XML / JAXP

#### XML Catalog 扩展

JDK 内置 XML Catalog 现包含 W3C DTD/XSD：`xml:` 命名空间、XML Schema Part 1 & 2、XHTML 1.0 & 1.1。本地加载无需网络访问。

#### XSLT/XPath 扩展函数默认禁用

`jdk.xml.enableExtensionFunctions` 默认从 `true` 改为 `false`。

#### JAXP 限制调整

默认实体扩展限制减少到 2500。可通过 `jdk.xml.entityExpansionLimit` 配置。

### JNDI

#### JNDI 远程代码下载永久禁用

LDAP 和 RMI 提供者的远程代码下载永久禁用。`com.sun.jndi.rmi.object.trustURLCodebase` 和 `com.sun.jndi.ldap.object.trustURLCodebase` 系统属性移除。

### 客户端库

#### GTK 2 支持移除

`java.desktop` 模块移除 GTK 2 互操作。`jdk.gtk.version=2` 或 `2.2` 不再有效；始终加载 GTK 3。

---

← [返回 Java 版本特性](../README.md)