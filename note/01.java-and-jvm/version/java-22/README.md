<!--
module:
  parent: java
  slug: java/version/java-22
  type: article
  category: 主模块子文章
  summary: Java 22：12 个 JEP，含外部函数与内存 API 正式版、未命名变量预览、G1 区域固定、字符串模板预览
  depth: ⭐⭐
-->

# Java 22

## 引言：变更说明

Java 22 是 12 个 JEP 的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

### 相关阅读

← [Java 21](../java-21/README.md) · [Java 23](../java-23/README.md)

---

- **JEP 423**: G1 的区域固定
- **JEP 447**: 在 `super(...)` 调用前的语句（预览）
- **JEP 454**: 外部函数与内存 API
- **JEP 456**: 无名变量与模式
- **JEP 457**: 类文件 API（预览）
- **JEP 458**: 启动多文件源代码程序
- **JEP 459**: 字符串模板（第二次预览）
- **JEP 460**: 向量 API（第七次孵化）
- **JEP 461**: 流收集器（预览）
- **JEP 462**: 结构化并发（第二次预览）
- **JEP 463**: 隐式声明类和实例主方法（第二次预览）
- **JEP 464**: 作用域值（第二次预览）

## JEP 423: G1 的区域固定

在垃圾回收过程中，G1（Garbage-First）垃圾收集器有时需要将对象从一个区域移动到另一个区域。然而，在某些情况下，我们希望特定区域中的对象保持原地不动，例如，当这些对象正被本地代码访问时。该特性引入了区域固定机制，允许在垃圾回收期间防止特定区域被回收或压缩，从而确保本地代码可以安全地访问这些区域中的对象，而无需担心对象被移动。

## JEP 447: 在 `super(...)` 调用前的语句（预览）

在 Java 中，构造函数的第一条语句通常是调用父类的构造函数（`super(...)`）。然而，在某些情况下，我们希望在调用父类构造函数之前执行一些操作，例如验证参数或初始化某些字段。该特性允许在调用 `super(...)` 之前包含语句，从而提供了更大的灵活性。这些语句在子类构造函数体执行之前、父类构造函数调用之后立即执行（从逻辑顺序角度，代码写在 `super` 调用前，但实际执行是在 `super` 调用之后、子类构造函数体之前 ），并且可以访问子类的字段（但此时子类对象还未完全初始化，需谨慎使用）。

```java
class Parent {
    Parent(int value) {
        System.out.println("Parent constructor with value: " + value);
    }
}

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

## JEP 454: 外部函数与内存 API

外部函数与内存 API 提供了一种更安全、更高效的方式来调用本地代码（例如 C/C++ 库）和操作本地内存。它引入了新的类和接口，允许 Java 代码声明与本地代码的交互方式，并提供了对本地内存的精细控制。这使得 Java 应用程序可以更好地与现有的本地库集成，同时减少了使用 JNI（Java Native Interface）带来的复杂性和安全风险。

```java
import java.lang.foreign.*;

public class NativeExample {
    public static void main(String[] args) {
        try (Arena arena = Arena.ofAuto()) {
            // 分配本地内存
            MemorySegment segment = arena.allocate(4);
            MemoryAccess.setIntAtIndex(segment, ValueLayout.JAVA_INT, 0, 42);

            // 读取本地内存
            int value = MemoryAccess.getIntAtIndex(segment, ValueLayout.JAVA_INT, 0);
            System.out.println("Value: " + value);
        }
    }
}
```

## JEP 456: 无名变量与模式

无名变量与模式允许在模式匹配中使用没有显式名称的变量。这在某些情况下可以使代码更加简洁，特别是当我们只关心模式匹配的结果而不关心变量的具体名称时。例如，在使用 `instanceof` 模式匹配时，如果我们不需要访问匹配的对象，可以使用无名变量来避免不必要的变量声明。

```java
Object obj = "Hello";
if (obj instanceof String _) { // 使用无名变量
    System.out.println("It's a string");
}
```

## JEP 457: 类文件 API（预览）

类文件 API 提供了一种编程方式来读取、生成和转换 Java 类文件。它允许开发者在运行时或编译时分析类文件的结构，提取类、方法、字段等信息，并且可以生成新的类文件或修改现有的类文件。这对于构建代码分析工具、字节码操作库和编译器插件等非常有用。

```java
import jdk.incubator.classfile.*;
import java.nio.file.*;

public class ClassFileExample {
    public static void main(String[] args) throws Exception {
        // 读取已有的类文件
        byte[] bytes = Files.readAllBytes(Path.of("MyClass.class"));
        ClassModel classModel = ClassFile.of().parse(bytes);

        System.out.println("Class name: " + classModel.thisClass().get().asInternalName());
        System.out.println("Super class: " + classModel.superclass().get().asInternalName());

        for (MethodModel method : classModel.methods()) {
            System.out.println("Method: " + method.methodName().stringValue());
        }
    }
}
```

## JEP 458: 启动多文件源代码程序

通常情况下，Java 程序需要先编译成类文件，然后再运行。然而，对于一些简单的脚本或小型程序，这种编译过程可能会显得繁琐。该特性允许直接运行包含多个 Java 源代码文件的程序，而无需事先编译。Java 解释器会自动编译并运行这些源代码文件，使得开发和测试小型程序更加方便快捷。

假设我们有两个 Java 源代码文件 `Main.java` 和 `Helper.java`：

`Main.java`:
```java
public class Main {
    public static void main(String[] args) {
        Helper helper = new Helper();
        helper.sayHello();
    }
}
```

`Helper.java`:
```java
public class Helper {
    public void sayHello() {
        System.out.println("Hello from Helper!");
    }
}
```

我们可以直接使用以下命令运行程序：
```bash
java Main.java Helper.java
```

## JEP 459: 字符串模板（第二次预览）

字符串模板提供了一种更灵活、更易读的方式来构建字符串。它允许在字符串中嵌入表达式，这些表达式将在运行时进行求值，并将结果插入到字符串中。与传统的字符串拼接方式相比，字符串模板更加简洁明了，减少了代码的冗余和错误的可能性。

```java
String name = "Alice";
int age = 30;
String message = STR."Hello, \{name}! You are \{age} years old."; // 使用字符串模板
System.out.println(message);
```

## JEP 460: 向量 API（第七次孵化）

向量 API 提供了一种高效的方式来进行向量计算，适用于科学计算、机器学习等领域。该特性通过引入一组新的类和接口，允许开发者使用硬件加速的向量指令来执行计算，从而提高性能。与之前的孵化版本相比，该版本可能进一步优化了 API 的设计和性能，提供了更多的向量操作和功能。

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

## JEP 461: 流收集器（预览）

流收集器（Stream Gatherers）是 Java 流 API 的一个扩展，引入了 `Stream::gather(Gatherer)` 方法。它提供了一种更灵活、更强大的方式来处理流中的元素。与传统的流操作不同，`gather()` 支持多阶段处理、状态维护和中间输出，可以实现更复杂的流操作，如窗口化、去重、限流等。开发者可以通过 `Gatherer` 接口自定义收集逻辑。

```java
import java.util.List;
import java.util.stream.Gatherer;
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

## JEP 462: 结构化并发（第二次预览）

结构化并发是一种多线程编程方法，旨在简化多线程代码的管理和错误处理。它将不同线程中运行的多个任务视为单个工作单元，从而提高了代码的可读性、可维护性和可靠性。与第一次预览版本相比，该版本可能进一步完善了 API 的设计和功能，解决了之前版本中发现的问题。

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

## JEP 463: 隐式声明类和实例主方法（第二次预览）

该特性进一步简化了 Java 源代码的结构，允许开发者编写更简洁的代码。它支持隐式声明类，即未命名的类可以省略类名，并且提供了更简单的实例主方法声明方式。与第一次预览版本相比，该版本可能根据用户反馈进行了改进和优化，提高了特性的易用性和稳定性。

```java
// 隐式声明类和实例主方法示例
void main() {
    System.out.println("Hello, World!");
}
```

## JEP 464: 作用域值（第二次预览）

作用域值是一种在特定作用域内共享不可变数据的机制。它类似于线程局部变量，但更适用于虚拟线程和结构化并发等新的编程模型。与第一次预览版本相比，该版本可能进一步完善了作用域值的实现，提高了其性能和可靠性，并且可能增加了更多的使用场景和功能。

作用域值允许在大型程序中的组件之间安全有效地共享数据，而无需求助于方法参数。这对于减少代码冗余和提高代码的可维护性非常有帮助。

```java
final static ScopedValue<String> USER_NAME = ScopedValue.newInstance();

// 设置作用域值
ScopedValue.where(USER_NAME, "Alice")
           .run(() -> {
               // 在这个作用域内可以访问 USER_NAME
               System.out.println("Hello, " + USER_NAME.get());
           });
```

---

## 其他新特性（非 JEP）

Java 22 还包含大量非 JEP 的改进，以下列出对开发者最实用的特性：

### 核心库

#### Unicode 15.1 支持

`Character` 类升级到 Unicode 15.1，新增 627 个字符（总计 149,813）和一个新 `UnicodeBlock`（GB 18030 的 CJK 表意文字）。

#### UTF-32 字符集常量

`StandardCharsets` 新增三个常量：`UTF_32`、`UTF_32BE`、`UTF_32LE`，补充现有的 8 位和 16 位等效项。

#### ListFormat 本地化列表格式

新类 `java.text.ListFormat` 处理本地化列表模式。例如 ["Foo", "Bar", "Baz"] 格式化为 "Foo, Bar, and Baz"（美式英语）或 "Foo, Bar et Baz"（法语）。支持三种连接类型：`STANDARD`、`OR` 和 `UNIT`。

```java
List<String> items = List.of("Foo", "Bar", "Baz");
String formatted = ListFormat.getInstance(Locale.US, ListFormat.Type.STANDARD, ListFormat.Width.WIDE).format(items);
// "Foo, Bar, and Baz"
```

#### RandomGenerator.equiDoubles() 方法

新增 `equiDoubles()` 方法保证均匀分布，比现有 `doubles()`/`nextDouble()` 更密集。返回 `DoubleStream`。

#### BasicFileAttributes.creationTime() Linux 上返回出生时间

在 Linux（内核 4.11+，glibc 2.28+）上，`BasicFileAttributes.creationTime()` 现在通过 `struct statx` 的 `stx_btime` 返回文件出生时间。之前返回最后修改时间。

#### java.io.File 丢弃 Windows 长路径前缀

在 Windows 上，从带长路径前缀（`\\?\` 或 `\\?\UNC`）的路径创建 `File` 现在会剥离前缀。与 `java.nio.file.Path` 行为对齐。

#### JLine 作为默认控制台提供者

- `System.console()` 现在返回具有增强编辑功能的 `Console`
- 即使标准流重定向或连接到虚拟终端，`System.console()` 现在也返回 `Console` 对象（之前返回 `null`）
- 新方法 `Console.isTerminal()` 测试是否连接到终端
- 系统属性 `-Djdk.console=java.base` 恢复遗留行为

#### TCP Keepalive 扩展套接字选项 Windows 支持

`ExtendedSocketOptions.TCP_KEEPIDLE` 和 `TCP_KEEPINTERVAL` 在 Windows 10 版本 1709+ 上受支持。`TCP_KEEPCOUNT` 在 Windows 10 版本 1703+ 上受支持。

#### ZIP64 额外字段验证改进

`ZipFile` 和 Zip FileSystem 提供者现在提供 ZIP64 额外字段的额外验证。可通过系统属性 `jdk.util.zip.disableZip64ExtraFieldValidation=true` 禁用。

#### newConstructorForSerialization 用方法句柄重新实现

`ReflectionFactory::newConstructorForSerialization` 用方法句柄重新实现。现在当声明类不是目标的超类时抛出 `UnsupportedOperationException`。

### HotSpot / JVM

#### G1: 快速回收疏散失败区域

G1 现在在下一次垃圾回收中回收疏散失败的区域。大幅减少回收几乎为空区域的时间，减少堆压力。

#### Parallel: 大对象数组的精确并行扫描

Parallel GC 工作器现在将工作限制在其 64kB 条带，只处理大对象数组的有趣部分。改善并行性，减少工作窃取。存在大对象数组时 GC 暂停与 G1 相当（某些情况下减少 4-5 倍）。

#### Serial: 稀疏脏卡片的更好 GC 吞吐量

改进对象起始查找和脏卡片搜索。使用大对象数组的基准测试中 Young-GC 暂停减少约 40%。

#### G1: 平衡代码根扫描阶段

G1 现在在区域内多个线程之间分配代码根扫描工作，消除编译代码中 Java 对象引用分布不均时的可扩展性瓶颈。

#### 两阶段分段堆转储

堆转储分为两个阶段：(1) 并发线程写入分段堆文件（应用暂停），(2) 合并到完整文件（应用恢复）。显著减少应用暂停时间。

#### -Xshare:dump 的 JIT 编译

现在可以在使用 `-Xshare:dump` 创建 CDS 归档时通过添加 `-Xmixed` 启用 JIT 编译。加速大类列表的归档创建。

#### hs_err 文件现在打印锁栈

线程本地锁栈部分添加到 `hs_err` 报告文件。仅在启用轻量级锁定模式（`-XX:LockingMode=2`）时打印。

#### NMT 峰值值在发布版本中可用

NMT 报告现在显示所有类别的峰值（JVM 生命周期内最高的已提交内存）。

#### 新 System.map 和 System.dump_map 诊断命令

新 `jcmd System.map` 和 `jcmd System.dump_map` 命令打印 JVM 进程的虚拟内存映射及 NMT 信息。

### 安全

#### -XshowSettings 新安全类别

`-XshowSettings` 启动器选项新增 `security` 类别。子类别：`all`、`properties`、`providers`、`tls`。

#### HSS/LMS: keytool 和 jarsigner 变更

`jarsigner` 和 `keytool` 现在支持分层签名系统/Leighton-Micali 签名（HSS/LMS）算法。

#### XML Security 更新到 Santuario 3.0.3

新增四个基于 SHA-3 的 RSA-MGF1 `SignatureMethod` 算法。

#### 新增根 CA 证书

新增多个根 CA 证书：Certigna Root CA、DigiCert CS ECC/RSA Root G5、emSign Root CA、Telia Root CA v2、ISRG Root X2（Let's Encrypt）。

#### 独立 TLS 服务器/客户端证书链长度属性

两个新系统属性：
- `jdk.tls.server.maxInboundCertificateChainLength`（默认 8）
- `jdk.tls.client.maxInboundCertificateChainLength`（默认 10）

#### KRB5 includedir 文件按字母数字顺序读取

`krb5.conf` `includedir` 目录中的文件现在按字母数字顺序读取（与 MIT krb5 1.17 一致）。

### 工具

#### javadoc @inheritDoc 标签变更

`@inheritDoc` 标签新增可选参数指定继承文档搜索的超类型。算法修改以更好地与 JLS 方法继承/覆盖规则对齐。

#### 弃用方法的 JFR 事件

新 JFR 事件 `jdk.DeprecatedInvocation` 检测弃用 JDK 方法的使用。必须通过命令行上的 `-XX:StartFlightRecording` 启用。

#### javac 受限方法 Lint 警告

新 `-Xlint:restricted` lint 选项在编译时警告调用受限 FFM API 方法。可用 `@SuppressWarnings("restricted")` 抑制。

#### --release N 模块版本变更

使用 `--release N` 时，系统模块描述符现在包含 `N` 作为模块版本（无论当前 JDK 版本如何都一致）。

#### -XshowSettings:locale 选项

`-XshowSettings` 不再默认打印语言环境信息。使用 `-XshowSettings:locale` 查看可用语言环境。

### 国际化

#### CLDR v44 支持

语言环境数据升级到 CLDR 44。主要变更：墨西哥和拉美国家时间格式从 24 小时制改为 12 小时制；澳大利亚和英国 `FULL` 日期格式在工作日后不再有逗号。

#### 通过 CLDR 数据获取格里高利时代名称

`java.time.format` API 现在从 CLDR 语言环境数据获取格里高利时代名称（之前使用遗留 COMPAT 数据）。ROOT 语言环境返回 "BCE"/"CE" 而不是 "BC"/"AD"。

### 移除

| 移除项 | 详情 |
|--------|------|
| `sun.misc.Unsafe.shouldBeInitialized`/`ensureClassInitialized` | 自 JDK 15 弃用，现移除。替代：`MethodHandles.Lookup.ensureInitialized(Class)` |
| `Thread.countStackFrames()` | 自 JDK 1.2 弃用，自 Java 9 弃用待移除，现移除。替代：`StackWalker` |
| 旧核心反射实现 | 旧核心反射实现移除。`-Djdk.reflect.useDirectMethodHandle=false` 现在是无操作 |
| `jdeps -profile`/`-P` 选项 | 自 JDK 21 弃用，现移除。紧凑配置文件自 Java 9 起已过时 |

### 弃用待移除

| 弃用项 | 详情 |
|--------|------|
| `sun.misc.Unsafe` 方法 | `park`、`unpark`、`getLoadAverage`、`loadFence`、`storeFence`、`fullFence` 弃用待移除 |
| `-Xnoagent` 选项 | 多个版本被忽略，现在生成弃用警告 |
| `jdk.crypto.ec` 模块 | SunEC JCE 提供者移至 `java.base` 模块。空模块存在用于过渡 |
| `-Xdebug`/`-debug` 选项 | 多个版本被忽略，现在生成弃用警告 |

### 已知问题

| 问题 | 详情 |
|------|------|
| Apple Silicon + macOS 14.4 意外终止 | 已修复：Apple macOS 14.4 Sonoma 最终版本导致 M1/M2/M3 上的 Java 意外终止 |
| `Files.readString` UTF-16 可能返回不正确字符串 | 解决方法：使用 `-XX:-CompactStrings` 禁用紧凑字符串 |
| ZGC 非默认 ObjectAlignmentInBytes 崩溃 | 已知问题 |
| JFR 增加启动时间 | 小应用使用 `-XX:StartFlightRecording` 时启动时间增加 |

---

← [返回 Java 版本特性](../README.md)