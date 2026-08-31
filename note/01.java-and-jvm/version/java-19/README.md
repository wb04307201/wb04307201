<!--
module:
  parent: java
  slug: java/version/java-19
  type: article
  category: 主模块子文章
  summary: Java 19：7 个 JEP，含 Record 模式预览、Foreign Function 预览、虚拟线程预览
  depth: ⭐⭐
-->

# Java 19

## 引言：变更说明

Java 19 是 7 个 JEP 的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

### 相关阅读

← [Java 18](../java-18/README.md) · [Java 20](../java-20/README.md)

---

- **JEP 405**: Record 模式（预览）
- **JEP 422**: Linux/RISC-V 移植
- **JEP 424**: 外部函数与内存 API（预览）
- **JEP 425**: 虚拟线程（预览）
- **JEP 426**: 向量 API（第四次孵化）
- **JEP 427**: switch 表达式模式匹配（第三次预览）
- **JEP 428**: 结构化并发（孵化）

## JEP 405: Record 模式（预览）

Record 模式扩展了 Java 的模式匹配能力，使其能够与 Record 类（一种不可变数据类）一起使用。通过 Record 模式，开发者可以更简洁地解构 Record 对象，提取其各个组件的值。这有助于简化代码，尤其是在处理复杂数据结构时。

```java
record Point(int x, int y) {}

// 使用 Record 模式解构 Point 对象
Point p = new Point(10, 20);
if (p instanceof Point(int x, int y)) {
    System.out.println("x: " + x + ", y: " + y);
}
```

## JEP 422: Linux/RISC-V 移植

该特性将 Java 移植到 Linux/RISC-V 平台，使得 Java 程序能够在基于 RISC-V 架构的 Linux 系统上运行。RISC-V 是一种开源的指令集架构，具有简洁、模块化和可扩展性等特点。通过支持 Linux/RISC-V 平台，Java 能够覆盖更广泛的硬件设备，满足不同场景下的应用需求。

## JEP 424: 外部函数与内存 API（预览）

外部函数与内存 API 提供了一种更安全、更高效的方式来调用本地代码（如 C/C++ 编写的函数）和操作本地内存。它引入了新的类和接口，允许开发者以类型安全的方式访问本地库函数和内存区域，避免了传统 JNI（Java Native Interface）的一些复杂性和潜在的安全问题。

```java
// 示例代码：调用本地库函数
import java.lang.foreign.*;
import java.lang.invoke.*;

try (Arena arena = Arena.ofAuto()) {
    // 分配本地内存
    MemorySegment segment = arena.allocate(100);
    
    // 查找本地库函数
    Linker linker = Linker.nativeLinker();
    SymbolLookup stdlib = linker.defaultLookup();
    MemorySegment funcAddr = stdlib.find("add").get();
    
    // 创建方法句柄
    FunctionDescriptor addDesc = FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT, ValueLayout.JAVA_INT);
    MethodHandle addHandle = linker.downcallHandle(funcAddr, addDesc);
    
    // 调用函数
    int result = (int) addHandle.invoke(10, 20);
    System.out.println("Result: " + result);
}
```

## JEP 425: 虚拟线程（预览）

虚拟线程是一种轻量级的线程实现，旨在简化高并发编程。与传统的操作系统线程（也称为平台线程）相比，虚拟线程由 JVM 管理，具有更低的创建和销毁成本，以及更高的并发性。虚拟线程适用于 I/O 密集型和高并发场景，能够显著提高程序的吞吐量和响应速度。

```java
// 创建并启动虚拟线程
Runnable task = () -> {
    System.out.println("Hello from virtual thread!");
};
Thread virtualThread = Thread.startVirtualThread(task);
virtualThread.join();
```

## JEP 426: 向量 API（第四次孵化）

向量 API 提供了一种高效的方式来执行向量计算，适用于科学计算、机器学习等领域。它允许开发者使用硬件加速的向量指令来执行计算，从而提高性能。该特性通过引入一组新的类和接口，使得向量计算更加简洁和易用。

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

## JEP 427: switch 表达式模式匹配（第三次预览）

该特性扩展了 switch 表达式的功能，使其支持模式匹配。通过模式匹配，switch 表达式可以更简洁地处理不同类型的对象，并根据对象的特征执行不同的操作。这使得代码更加易读和维护，减少了不必要的类型转换和条件判断。

```java
Object obj = "Hello";
String result = switch (obj) {
    case String s -> "It's a string: " + s;
    case Integer i -> "It's an integer: " + i;
    default -> "Unknown type";
};
System.out.println(result);
```

## JEP 428: 结构化并发（孵化）

结构化并发是一种多线程编程方法，旨在简化多线程代码的管理和错误处理。它将不同线程中运行的多个任务视为单个工作单元，从而提高了代码的可读性、可维护性和可靠性。该特性引入了 `StructuredTaskScope` 类，允许开发者将任务拆分为多个并发子任务，并在它们自己的线程中执行。子任务必须在主任务继续之前完成，这使得错误处理更加简单，因为异常可以在一个地方捕获和处理。

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

---

## 其他新特性（非 JEP）

Java 19 还包含多项非 JEP 的改进，以下列出对开发者最实用的特性：

### 核心库

#### Unicode 14.0 支持

新增 838 个字符（总计 144,697）、5 种新文字（总计 159）、37 个新表情符号。

#### stdout/stderr 编码系统属性

新增 `stdout.encoding` 和 `stderr.encoding` 系统属性，指定标准输出和错误流使用的编码。平台不提供控制台流时默认为 `native.encoding`。可通过 `-D` 覆盖以强制使用 UTF-8。

#### user.home 回退到 $HOME

在 Linux 和 macOS 上，如果 `user.home` 为空或单字符，回退到 `$HOME` 环境变量。在容器/systemd 环境中很有用。

#### HashMap/HashSet 预分配工厂方法

新增静态工厂方法：`HashMap.newHashMap(int)`、`LinkedHashMap.newLinkedHashMap(int)`、`WeakHashMap.newWeakHashMap(int)`、`HashSet.newHashSet(int)`、`LinkedHashSet.newLinkedHashSet(int)`。容纳预期映射数而无需调整大小。优先于 int 参数构造函数。

#### Double.toString/Float.toString 改进

更严格的规范合规性。某些返回的字符串现在更短。例如 `Double.toString(2e23)` 现在返回 `"2.0E23"`。

#### Windows ADS 控制系统属性

新 `jdk.io.File.enableADS` 系统属性启用/禁用 `java.io.File` 中的 NTFS 备用数据流支持。

#### Files.copy 跨文件系统复制 POSIX 属性

`Files.copy(Path,Path)` 现在在不同文件系统提供者之间复制时复制 POSIX 文件访问权限。

#### FileChannel.transferFrom Linux 4.5+ 性能提升

Linux 内核 4.5+ 上 `FileChannel.transferFrom()` 性能显著提升。可能返回少于请求的字节数（"短传输"），规范允许。

#### InetAddress 拒绝模糊 IPv4 字面量

严格只接受 IPv4 字面量的十进制四元组表示法。抛出 `UnknownHostException` 处理无效字面量。

#### \b 默认只匹配 ASCII

`\b` 元字符现在默认只匹配 ASCII 单词字符（与 `\w` 一致）。使用 `UNICODE_CHARACTER_CLASS` 标志进行 Unicode 匹配。

#### DateTimeFormatter.ofLocalizedPattern

新方法 `DateTimeFormatter.ofLocalizedPattern(String)` 用于灵活的本地化日期/时间格式化。例如 `ofLocalizedPattern("yMMM")` 产生 "Feb 2022"（美国）或 "2022年2月"（日语）。

#### Locale.of() 工厂方法

新的 `Locale.of()` 工厂方法替代弃用的构造函数。工厂方法有效地重用现有 `Locale` 实例。

#### JNDI 更严格的 URL 解析

LDAP、DNS 和 RMI JNDI 提供者中的 URL 解析更严格。由 `com.sun.jndi.{ldap,dns,rmi}URLParsing` 系统属性控制，值为 `"legacy"`、`"compat"`（默认）或 `"strict"`。

### 安全

#### TLS/DTLS 签名方案 API

新增 `SSLParameters.getSignatureSchemes()` 和 `setSignatureSchemes()` API 自定义每个 TLS/DTLS 连接的签名方案。

#### Windows KeyStore 本地机器访问

SunMSCAPI 提供者扩展了 `Windows-MY-LOCALMACHINE` 和 `Windows-ROOT-LOCALMACHINE` 密钥库类型。

#### 更大的默认密钥大小

- RSA/RSASSA-PSS/DH: 2048 → 3072
- EC: 256 → 384
- AES: 128 → 256（如果策略限制则回退到 128）
- `jarsigner` 现在使用 SHA-384 而不是 SHA-256 作为默认摘要

#### 3DES TLS 密码套件从默认移除

7 个使用 3DES 的 TLS 密码套件从默认启用列表中移除。

#### RC2 和 ARCFOUR 添加到遗留算法

RC2 和 ARCFOUR (RC4) 添加到 `jdk.security.legacyAlgorithms` 属性。

#### macOS KeychainStore 信任设置

只有用户钥匙串中具有适当信任设置的证书才作为受信任证书公开。

#### RFC 6125 端点标识合规

SunJSSE 现在完全符合 RFC 6125。TLS 证书中的通配符域匹配仅允许通配符位于最左侧标签时。

### HotSpot / JVM

#### 自动 CDS 归档生成

新 `-XX:+AutoCreateSharedArchive` 标志自动创建或更新 CDS 归档。

```bash
java -XX:+AutoCreateSharedArchive -XX:SharedArchiveFile=app.jsa -cp app.jar App
```

#### Linux/AArch64 上的 PAC-RET 保护

ARMv8.3 指针认证代码扩展支持，防止 ROP 攻击。使用 `--enable-branch-protection` 构建。通过 `-XX:UseBranchProtection=standard` 或 `-XX:UseBranchProtection=pac-ret` 启用。

#### CPU 份额忽略用于活跃处理器计数

JVM 不再使用 Linux cgroups `cpu.shares` 计算线程池大小（不正确）。恢复容器中的完整 CPU 利用率。

#### 虚拟线程的 JVM TI 变更

JVM TI 更新以支持虚拟线程。新函数：`SuspendAllVirtualThreads`、`ResumeAllVirtualThreads`。新事件：`VirtualThreadStart`、`VirtualThreadEnd`。

### 工具

#### jstatd 不再需要 SecurityManager

`jstatd` 不再需要安全管理器和策略文件。内部使用 `ObjectInputFilter` 进行反序列化过滤。

#### JShell 高亮显示弃用元素

JShell 标记弃用元素并在控制台中高亮显示变量和关键字。

#### -Xss 向上舍入到页面大小

线程栈大小（`-Xss`）可能向上舍入到系统页面大小的倍数。

#### Indy String Concat 修复操作顺序

字符串连接现在从左到右计算每个参数并使用即时字符串转换，修复 JEP 280 错误。

#### JavaDoc 搜索增强

添加独立搜索页面。搜索语法增强以允许多个搜索词。

#### jpackage 每用户和系统范围配置

`jpackage` 应用现在在用户特定位置查找 `.cfg` 文件。

### 国际化

#### CLDR v41 支持

语言环境数据升级到 Unicode Consortium CLDR v41。

### 客户端库

#### Metal 是 macOS 上的默认 Java 2D 管道

Swing/Java2D 现在默认使用 Apple Metal API 渲染（自 JDK 17 起可用但不是默认）。更快的图形，更低的功耗。可通过 `-Dsun.java2d.metal=false` 或 `-Dsun.java2d.opengl=true` 禁用。

### 平台特定

#### 工具链升级到 Visual Studio 2022

Windows JDK 现在使用 MSVC 2022 工具链构建。

#### RPM 安装目录变更

RPM 安装路径从 `/usr/java/jdk-${VERSION}` 变更为 `/usr/lib/jvm/jdk-${FEATURE}-oracle-${ARCH}`。

#### macOS/Windows 每特性单安装目录

- macOS: `/Library/Java/JavaVirtualMachines/jdk-${FEATURE}.jdk`
- Windows: `%ProgramFiles%\Java\jdk-%FEATURE%`

---

← [返回 Java 版本特性](../README.md)