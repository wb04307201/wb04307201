<!--
module:
  parent: java
  slug: java/version/java-14
  type: article
  category: 主模块子文章
  summary: Java 14：16 个 JEP，含 Records 预览、instanceof 模式匹配预览、switch 表达式正式版、Helpful NPE
-->

# Java 14

## 引言：变更说明

Java 14 是 16 个 JEP 的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

### 相关阅读

← [Java 13](../java-13/README.md) · [Java 15](../java-15/README.md)

---

- **JEP 305**: 针对 `instanceof` 的模式匹配（预览）
- **JEP 343**: 打包工具（孵化器）
- **JEP 345**: G1 的 NUMA 感知内存分配
- **JEP 349**: JFR 事件流
- **JEP 352**: 非易失性映射字节缓冲区
- **JEP 358**: 有用的 `NullPointerException`
- **JEP 359**: 记录类（预览）
- **JEP 361**: Switch 表达式（标准）
- **JEP 362**: 弃用 Solaris 和 SPARC 端口
- **JEP 363**: 移除 Concurrent Mark Sweep（CMS）垃圾收集器
- **JEP 364**: macOS 上的 ZGC
- **JEP 365**: Windows 上的 ZGC
- **JEP 366**: 弃用 ParallelScavenge + SerialOld GC 组合
- **JEP 367**: 移除 Pack200 工具和 API
- **JEP 368**: 文本块（第二次预览）
- **JEP 370**: 外部内存访问 API（孵化器）

## JEP 305: 针对 `instanceof` 的模式匹配（预览）

该特性引入了模式匹配的概念到 `instanceof` 操作符中，使得类型检查和类型转换可以一步完成，减少了代码的冗余和提高了可读性。

```java
Object obj = "Hello";
if (obj instanceof String s) {
    System.out.println(s.length()); // 可以直接使用转换后的变量 s
}
```

## JEP 343: 打包工具（孵化器）

打包工具（`jpackage`）是一个用于将 Java 应用程序打包成特定平台（如 Windows、macOS 和 Linux）上的原生安装包或可执行文件的工具。它简化了应用程序的分发过程，使得用户可以像安装原生应用程序一样安装 Java 应用程序。

```bash
# 示例命令，将应用程序打包成 macOS 的 dmg 文件
jpackage --name MyApp --input lib --main-jar myapp.jar --type dmg
```

## JEP 345: G1 的 NUMA 感知内存分配

NUMA（Non-Uniform Memory Access）是一种多处理器架构，其中内存访问时间取决于内存相对于处理器的位置。该特性使 G1 垃圾收集器能够感知 NUMA 架构，并优化内存分配策略，以提高应用程序在 NUMA 系统上的性能。

## JEP 349: JFR 事件流

JFR（Java Flight Recorder）事件流允许开发者以流式的方式访问 JFR 记录的事件数据，而无需等待记录完成或处理整个记录文件。这对于实时监控和分析应用程序的性能非常有用。

## JEP 352: 非易失性映射字节缓冲区

该特性引入了一种新的字节缓冲区类型，即非易失性映射字节缓冲区（Non-Volatile Mapped Byte Buffers），它允许 Java 应用程序直接访问非易失性存储设备（如 SSD）上的数据，而无需通过文件系统 API。这对于需要高性能持久化存储的应用程序非常有用。

## JEP 358: 有用的 `NullPointerException`

该特性改进了 `NullPointerException` 的错误信息，提供了更详细的变量信息，帮助开发者更快地定位和解决空指针异常问题。

```java
String str = null;
str.length(); // 抛出 NullPointerException，并显示类似 "Cannot invoke "String.length()" because "str" is null" 的错误信息
```

## JEP 359: 记录类（预览）

记录类是一种简洁的数据载体类，它自动提供了 `equals`、`hashCode`、`toString` 等方法，以及紧凑的构造器和访问器方法。记录类使得创建不可变的数据对象变得更加简单和直观。

```java
record Point(int x, int y) {}

Point p = new Point(1, 2);
System.out.println(p); // 输出: Point[x=1, y=2]
```

## JEP 361: Switch 表达式（标准）

Switch 表达式扩展了传统的 `switch` 语句，使其可以作为一个表达式返回一个值。它还引入了新的 `->` 语法来简化 `case` 标签，并支持多标签和表达式组合。

```java
String day = "MONDAY";
int numLetters = switch (day) {
    case "MONDAY", "FRIDAY", "SUNDAY"    -> 6;
    case "TUESDAY"                       -> 7;
    case "THURSDAY", "SATURDAY"          -> 8;
    case "WEDNESDAY"                     -> 9;
    default                              -> -1;
};
```

## JEP 362: 弃用 Solaris 和 SPARC 端口

随着计算机硬件的发展，Solaris 操作系统和 SPARC 架构的使用已经逐渐减少。为了简化 JDK 的开发和维护，该特性决定弃用对 Solaris 和 SPARC 端口的支持。

## JEP 363: 移除 Concurrent Mark Sweep（CMS）垃圾收集器

CMS 垃圾收集器是一种较老的垃圾收集算法，它在某些场景下可能会导致较长的停顿时间。随着 G1 和 ZGC 等更先进的垃圾收集器的出现，CMS 垃圾收集器已经逐渐被淘汰。该特性正式从 JDK 中移除了 CMS 垃圾收集器。

## JEP 364: macOS 上的 ZGC

ZGC 是一种可扩展的低延迟垃圾收集器，它旨在满足大规模应用程序对垃圾收集性能的需求。该特性将 ZGC 引入到 macOS 平台上，使得 macOS 上的 Java 应用程序也可以享受到 ZGC 带来的性能提升。

## JEP 365: Windows 上的 ZGC

与 JEP 364 类似，该特性将 ZGC 引入到 Windows 平台上，使得 Windows 上的 Java 应用程序也可以使用 ZGC 作为垃圾收集器。

## JEP 366: 弃用 ParallelScavenge + SerialOld GC 组合

ParallelScavenge + SerialOld GC 组合是一种较老的垃圾收集策略，它在某些场景下可能不是最优的选择。随着更先进的垃圾收集器的出现，该特性决定弃用这种组合。

## JEP 367: 移除 Pack200 工具和 API

Pack200 是一种用于压缩 JAR 文件的工具和技术，它可以减少 JAR 文件的大小，从而加快应用程序的下载和启动速度。然而，随着网络带宽的增加和应用程序分发方式的改变，Pack200 的使用已经逐渐减少。该特性正式从 JDK 中移除了 Pack200 工具和 API。

## JEP 368: 文本块（第二次预览）

文本块是一种多行字符串字面量的表示方式，它简化了在 Java 代码中嵌入多行文本（如 HTML、SQL、JSON 等）的过程。该特性是文本块的第二次预览，进一步改进了文本块的语法和功能。

```java
String html = """
              <html>
                  <body>
                      <p>Hello, world</p>
                  </body>
              </html>
              """;
```

## JEP 370: 外部内存访问 API（孵化器）

外部内存访问 API 提供了一种统一的方式来访问和管理堆外内存（如本地内存、直接缓冲区等）。它简化了与本地代码交互的过程，并提高了内存访问的性能和安全性。该特性是外部内存访问 API 的孵化器版本，旨在收集反馈并进一步改进 API 的设计。

---

## 其他新特性（非 JEP）

Java 14 还包含多项非 JEP 的改进，以下列出对开发者最实用的特性：

### 核心库

#### 会计货币格式支持

通过 `"u-cf-account"` Unicode 语言环境扩展调用 `NumberFormat.getCurrencyInstance(Locale)` 可获取会计样式的货币格式实例。例如在 `Locale.US` 中格式化为 `"($3.27)"` 而不是 `"-$3.27"`。

#### CompactNumberFormat 复数支持

`CompactNumberFormat` 现在可以处理复数形式。例如 2,000,000 在德语中格式化为 `"2 Millionen"`（LONG 样式），而 1,000,000 格式化为 `"1 Million"`。

#### 线程中断状态始终可用

`Thread` 的中断状态现在始终可用。如果在启动之前或终止之后中断线程，`t.isInterrupted()` 将返回 true。

#### Thread.suspend/resume 弃用待移除

以下方法终弃：`Thread.suspend()`、`Thread.resume()`、`ThreadGroup.suspend()`、`ThreadGroup.resume()`、`ThreadGroup.allowThreadSuspension(boolean)`。

#### 序列化过滤器处理改进

`jdk.serialFilter` 系统属性只能在命令行设置。如果未在命令行设置，可通过 `java.io.ObjectInputFilter.Config.setSerialFilter` 设置。通过 `System.setProperty` 设置无效。

#### Zip 文件系统抛出 NoSuchFileException

当 `FileSystems.newFileSystem` 被调用且指定的 Zip/JAR 文件不存在且 `create` 不为 `true` 时，Zip 文件系统现在抛出 `NoSuchFileException`。

#### Runtime.exec 和 ProcessBuilder 参数限制

收紧了对 `Runtime.exec` 和 `ProcessBuilder` 创建的进程参数引号的约束。可能影响使用安全管理器部署的 Windows 应用程序。

#### DatagramSocket.send 抛出 IllegalArgumentException

如果套接字未连接且 `DatagramPacket` 不包含地址，`send` 方法现在抛出 `IllegalArgumentException`（而不是 `NullPointerException`）。

#### InetSocketAddress.toString 格式变更

IPv6 字面量现在按 RFC 2732 用方括号括起来。未解析的地址现在使用 `<unresolved>` 标记。

#### 容器内 OperatingSystemMXBean 方法返回容器特定数据

以下方法在容器中执行时现在返回容器特定信息：`getFreePhysicalMemorySize()`、`getTotalPhysicalMemorySize()`、`getFreeSwapSpaceSize()`、`getTotalSwapSpaceSize()`、`getSystemCpuLoad()`。

### 安全

#### 弱命名曲线默认禁用

47 条弱命名曲线通过新 `jdk.disabled.namedCurves` 安全属性默认禁用，可使用 `include` 关键字包含在 `disabledAlgorithms` 属性中。

#### 可信 TLS 服务器证书需要精确匹配

TLS 服务器证书必须与客户端上的可信证书精确匹配才能被信任。

#### 信任锚证书的新检查

信任锚必须包含 `cA=true` 的基本约束扩展，如果存在密钥用法扩展，则必须设置 `keyCertSign` 位。新系统属性 `jdk.security.allowNonCaAnchor` 恢复先前行为。

#### 移除 SSLv2Hello 和 SSLv3

SSLv2Hello 和 SSLv3 从默认启用的 TLS 协议中移除。

#### 无状态恢复默认启用

服务端 JSSE 现在默认以无状态模式运行（TLS 1.2 的 RFC 5077，TLS 1.3 的 RFC 8446）。加密会话票据发送给客户端用于会话恢复，改善性能和内存使用。

#### 移除过时的 NIST EC 曲线

sect283k1、sect283r1、sect409k1、sect409r1、sect571k1、sect571r1 和 secp256k1 从默认命名组中移除。

#### 弃用遗留椭圆曲线

47 条遗留命名椭圆曲线在 `SunEC` 提供者中弃用（brainpoolP*、secp*、sect*、X9.62 曲线）。

#### 弃用 OracleUcrypto JCE 提供者

`OracleUcrypto` JCE 提供者和 `jdk.crypto.ucrypto` 模块弃用待移除。

#### 新增根证书

新增 LuxTrust Global Root 2 和 4 个 Amazon Root CA 证书。

### HotSpot / JVM

#### NullPointerException 详细消息

新 JVM 选项 `-XX:+ShowCodeDetailsInExceptionMessages` 分析程序以确定哪个引用为 null，并在 `NullPointerException.getMessage()` 中提供详细信息，包括方法、文件名和行号。

```bash
# 启用详细 NPE 消息（默认启用）
java -XX:+ShowCodeDetailsInExceptionMessages MyApp
```

#### AOT 默认关闭

`UseAOT` 默认从 `enabled` 改为 `disabled`。`UseAOT`、`PrintAOT`、`AOTLibrary` 标志改为实验性。

#### Parallel GC 改进

Parallel GC 采用与其他收集器相同的任务管理机制来调度并行任务。可能导致显著的性能改进。

#### Shenandoah 自修复屏障

LRB 现在在同一代码路径上自修复转发引用，消除热访问的持续解析。

#### Shenandoah 并发类卸载

Shenandoah GC 现在支持完全并发类卸载，最小化 Final Mark 暂停期间的类卸载工作。

### 工具

#### 可发现的 javac 插件默认调用

`javac` 插件现在可以通过实现 `Plugin.isDefault()` 返回 `true` 来选择默认启动。

#### 注解对象 toString 一致

核心反射和 `javac` 注解处理中注解对象的 `toString` 输出现在遵循相同约定，允许输出在源代码中使用。

### XML / JAXP

#### SAX ContentHandler 新方法

`SAX ContentHandler` 新增 `declaration` 方法接收 XML 声明通知。应用可以准确接收声明的版本、编码和独立属性。

### 国际化

#### CLDR v36 支持

语言环境数据升级到 Unicode Consortium 的 CLDR v36。

### 移除

| 移除项 | 详情 |
|--------|------|
| `sun.nio.cs.map` 系统属性 | 移除。应用必须根据需求指定正确的字符集名称 |
| `netscape.javascript.JSObject.getWindow` 方法 | 移除。JDK 9 弃用，JDK 11 起始终返回 null |
| 弃用的 `java.security.acl` API | 移除 `Acl`、`AclEntry`、`AclNotFoundException`、`Group` 等类 |
| 默认 `keytool -keyalg` 值 | 必须显式指定 `-keyalg` 选项 |

---

← [返回 Java 版本特性](../README.md)