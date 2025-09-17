# Java 14

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
int numLetters = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> 6;
    case TUESDAY                -> 7;
    case THURSDAY, SATURDAY     -> 8;
    case WEDNESDAY              -> 9;
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