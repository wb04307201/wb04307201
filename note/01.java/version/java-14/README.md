# Java 14

- JEP 361：表达式（正式特性）
- JEP 368：增强文本块（第二次预览）
- JEP 359：Records (预览) ：Java 14 新特性—新特性 Record 类型
- JEP 305：模式匹配的 instanceof（预览）：Java 14 新特性—模式匹配的 instanceof
- JEP 358：改进 NullPointerExceptions 提示信息：Java 14 新特性—改进 NullPointerExceptions 提示信息
- JEP 343：打包工具（孵化）
- JEP 345：NUMA-Aware 内存分配
- JEP 349：JFR Event Streaming
- JEP 364：macOS 上的 ZGC（实验性）
- JEP 365：Windows 上的 ZGC（实验性）
- JEP 366：弃用 ParallelScavenge + SerialOld GC 组合
- JEP 367：删除 Pack200 工具和 API
- JEP 363：删除 CMS 垃圾收集器
- JEP 370：外部存储器访问 API（孵化器版）

---

## JEP 361：Switch 表达式（正式特性）
Java 12 引入 Switch 表达式作为预览功能发布，Java 13 对其进行增强处理。在 Java 14 中，`switch`表达式已经是一个标准特性。`Switch`表达式主要功能包括：

1. **简化的语法**: `switch`表达式允许使用更简洁的箭头语法`->`，这样可以直接返回一个值，而不需要`break`语句。
2. **多值匹配**: 在一个`case`分支中，可以同时匹配多个值，使用逗号分隔。
3. **yield 关键字**: 当使用传统的`switch`块语法时，可以使用`yield`来返回一个值。

| Java 版本 | 更新类型  | JEP     | 更新内容                                      |
|---------|-------|---------|-------------------------------------------|
| Java 12 | 预览特性  | JEP 325 | 引入 Switch 表达式作为预览特性                       |
| Java 13 | 第二次预览 | JEP 354 | 加入 yield 语句来替代 break 语句，用于从 switch 表达式返回值 |
| Java 14 | 正式特性  | JEP 361 | 成为正式特性                                    |

## JEP 368：增强文本块（第二次预览）
为了能够更好地处理多行字符串的情况，Java 13 引入文本块来简化多行字符串字面量的编写和管理。Java 14 对其进一步增强，新加入了两个转义符，分别是：`\`和`\s`：
- **\ (行尾转义符)**: 这个转义符用于去除行尾换行符，使得代码中的文本块和实际字符串之间可以有更好的对齐，同时不在字符串的内容中包含不必要的换行符。
- **\s (空格转义序列)**: 这个转义符用于在需要的地方显式添加尾随空格，这在某些格式化文本中是必要的。

| Java 版本 | 更新类型  | JEP     | 更新内容                    |
|---------|-------|---------|-------------------------|
| Java 13 | 预览特性  | JEP 354 | 引入文本块作为预览特性，支持多行字符串字面量。 |
| Java 14 | 第二次预览 | JEP 368 | 改进文本块，包括空行和转义序列的处理。     |

## JEP 359：Records (预览)
Java 14 引入一种新的类型： "Record"（记录）。它是 Java 14 的预览特性，旨在提供一种简洁的方式来声明只包含数据的类，通常被用于作为数据载体。它主要针对那些只需要携带数据且不需要复杂的业务逻辑的简单类。

Records 允许我们以一种极其简洁的方式定义一个类，我们只需要指定其数据内容。对于每个 Record，Java 都会自动地为其成员变量生成`equals()`,`hashCode()`,`toString()`方法，以及所有字段的访问器方法（getter）

**为什么没有 setter 方法呢？**

因为 Record 的实例是不可变的，它所有的字段都是`final`，这就意味着一旦构造了一个 Record 实例，其状态就不能更改了。

Records 具备如下几个优势：
- **简洁性**: 减少了定义数据类时所需的样板代码。
- **可读性**: 记录的结构一目了然，增强了代码的清晰性和易读性。
- **安全性**: 由于其不可变性，Records 可以提高代码的安全性和可预测性。
- **适用于数据载体**: 非常适合用作传递数据的简单载体，例如 DTO（数据传输对象）。

## JEP 305：模式匹配的 instanceof（预览）
Java 14 引入了模式匹配的`instanceof`操作，目的是增强`instanceof`操作符，使其更加强大和灵活，同时减少样板代码。

在Java 14 之前，`instanceof`主要用来检查对象的类型，然后根据类型对目标对象进行类型转换，之后进行不同的处理、实现不同的逻辑，如下：
```java
if (obj instanceof String) {
    String s = (String) obj;
    // 业务逻辑
}
```

在 Java 14 中，使用模式匹配的 instanceof，这可以被简化为：
```java
if (obj instanceof String s) {
    // 直接使用 s
}
```
如果`obj`是`String`类型的实例，`s`就会被自动声明并初始化为`obj`强制转换后的值。这样就避免了单独的类型转换步骤，并使得代码更加简洁易读。

## JEP 358：改进 NullPointerExceptions 提示信息
在 Java 14 之前，当程序中出现空指针异常时，Java 通常只提供很少的信息，比如异常发生的行号。这使得开发者很难确定是哪个特定的变量或方法调用导致了异常。

所以 Java 14 引入该特性，目的改善`NullPointerException`的提示信息，使其更加详细和有助于调试。

该特性是可选的，使用`XX:+ShowCodeDetailsInExceptionMessages`，启用该特性，启用后，当发生空指针 异常是会提示更多的信息，指出具体是哪个变量或表达式为`null`导致了异常。

## JEP 343：打包工具（孵化）
在 Java 14 之前，Java 应用通常依赖于 JAR 文件来分发和运行，或者需要第三方工具来创建本地应用程序包，Java 14 引入一个新的打包工具，基于`javapackager`的`jpackage`，用于打包 Java 应用程序为特定平台的本地安装包。

该特性提供一个官方的、简单易用的打包工具，使 Java 应用可以更容易地分发和安装在各种平台上，包括 Windows、macOS 和 Linux。同时该工具能够创建包含 Java 运行时环境（JRE）的自包含应用程序包。这意味着用户不需要在其设备上预先安装 Java 运行时环境。

## JEP 345：NUMA-Aware 内存分配
Java 14 引入该特性的目的是优化 G1 垃圾收集器在 NUMA（Non-Uniform Memory Access）架构下的性能。

在 NUMA 架构的系统中，处理器访问自己本地节点（Local Node）的内存比访问其他节点（Remote Node）的内存速度更快。但是在 Java 14 之前，JVM 的垃圾收集器并不是 NUMA 敏感的，这意味着它在分配和管理内存时并没有考虑 NUMA 架构的特点，可能导致性能不佳。

该项特性为 G1 垃圾收集器增加了 NUMA 敏感的内存分配策略，通过优化内存分配，减少跨节点的内存访问，使G1 能够根据运行时的 NUMA 拓扑动态调整其内存分配策略，而提高了在 NUMA 系统上运行的 Java 应用程序的性能。

这个特性在支持的平台上默认启用。对于不支持或不需要的情况，需要使用-XX:+UseNUMA 来启用或禁用 NUMA-Aware 的行为。

该特性特别适用于大型、多处理器的服务器，因为这些服务器通常采用 NUMA 架构。

下面是关于 NUMA 的简单介绍：
- NUMA（Non-Uniform Memory Access）是一种计算机内存设计，用于多处理器系统，特别是在大型服务器、多核处理器和大量内存配置中常见。它的主要特点是内存访问时间取决于内存位置相对于处理器的位置。
- 在 NUMA 架构中，内存被划分为多个区域，每个区域与特定的处理器或处理器组相关联。
  - **本地内存访问**：当处理器访问其关联的内存区域（即本地内存）时，速度较快。
  - **远程内存访问**：当处理器访问非关联的内存区域（即远程内存）时，速度较慢。

## JEP 349：JFR Event Streaming
JFR 是一种用于收集运行中 Java 应用程序的诊断和性能分析数据的工具。它主要用于事后分析，即在一段时间内收集数据，然后进行分析。

Java 14 增强了该功能，使得可以持续地、实时地处理（流式地）JFR 数据，无论是在进程内还是进程外。下面是 JFR 事件流的关键特性：
- **实时事件流**：能够实时流式传输 JFR 事件，使应用程序能够实时响应事件。
- **进程内 API**：该特性包括一个进程内 API，用于在同一 Java 进程中消费事件，使得将实时事件监控集成到 Java 应用程序中变得更加容易。
- **进程外流式处理**：它还支持进程外流式处理，允许外部工具连接到 Java 进程并消费 JFR 事件。
- **筛选和定制**：开发者可以筛选他们想要流式传输的事件，并配置事件的详细程度。
- **低性能开销**：JFR 事件流设计时考虑了性能，确保即使在持续收集和处理事件时，对应用程序的性能影响也最小。

## JEP 364：macOS 上的 ZGC（实验性）
该特性将 ZGC 的支持扩展到 macOS，这使得 macOS 上的 Java 开发者和用户也能够利用 ZGC 的高性能特性。

## JEP 365：Windows 上的 ZGC（实验性）
该特性将 ZGC 的支持扩展到 Windows，这使得 Windows 上的 Java 开发者和用户也能够利用 ZGC 的高性能特性。

## JEP 366：弃用 ParallelScavenge + SerialOld GC 组合
随着 JVM 的发展，垃圾收集器技术也在不断进步。新的垃圾收集器（如 G1、ZGC 和 Shenandoah）为性能和效率提供了更好的解决方案。而 ParallelScavenge + SerialOld 这个组合，在年轻代中使用并行算法，而在老年代中使用串行算法，这种组合方式已经不具备优势了，由于这个组合很少使用，但是却要花费巨大工作量来进行维护，得不偿失，所以 Java 14 弃用该组合。

## JEP 367：删除 Pack200 工具和 API
Pack200 是一种专门为 Java 类文件设计的压缩技术，最初在 Java 5 中引入。它可以显著减小 JAR 文件的大小，因此被广泛用于优化网络传输 Java 应用程序和库。

随着时间的推移和技术的发展，网络速度的提高和存储成本的降低减少了对极端压缩技术的需求。同时，新的打包技术（如`jlink`和`jmod`）的出现，以及 Java 模块系统的引入，使得 Pack200 的应用场景变得有限。

Java 14 宣布正式移除 Pack200 工具和 API。

## JEP 363： 删除 CMS 垃圾收集器
CMS（Concurrent Mark Sweep）垃圾收集器是一个以最小化应用程序停顿时间为目标的收集器，最初设计用于老年代的垃圾收集。

随着新一代垃圾收集器（如 G1、ZGC 和 Shenandoah）的出现和成熟，CMS 的技术相对过时，并且维护成本逐渐增高。此外，新的收集器在性能和功能上均优于 CMS。

Java 14 正式移除了 CMS 垃圾收集器及其相关代码。

## JEP 370：外部存储器访问 API（孵化器版）
EP 370为Java程序提供了一种安全、高效的方式来访问Java堆之外的外部内存。这一API的引入，旨在满足Java程序对外部内存访问的多样化需求，并克服现有API（如`java.nio.ByteBuffer`和`sun.misc.Unsafe`）的限制。

外部存储器访问API主要包含以下三个类：
- **MemorySegment**：表示一个外部内存段，可以对其进行读写操作。
- **MemoryAddress**：表示一个内存地址，用于定位外部内存中的特定位置。
- **MemoryLayout**：描述外部内存的布局，包括其数据类型和结构。

与现有的`java.nio.ByteBuffer`相比，外部存储器访问API具有以下优势：
- **更大的内存容量**：`ByteBuffer`使用基于`in`t的索引方案，因此其容量不能超过2GB。而外部存储器访问API则不受此限制，可以操作更大的内存区域。
- **更明确的内存管理**：与`ByteBuffer`的内存管理依赖于垃圾回收器不同，外部存储器访问API要求开发者在源代码中明确指定内存释放操作，从而提高了内存管理的确定性和可控性。