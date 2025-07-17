# Java 18

- JEP 400：默认UTF-8编码
- JEP 408：简易Web服务器
- JEP 413：支持在 Java API 文档中加入代码片段
- JEP 416：用方法句柄重新实现核心反射
- JEP 417：向量 API（第三孵化器）
- JEP 418：互联网地址解析 SPI
- JEP 419：外部函数和内存 API（第三孵化器）
- JEP 420：模式匹配 Switch 表达式（预览）
- JEP 421：弃用 Finalization 功能

---

## JEP 400：默认UTF-8编码
在Java 18之前，Java的标准字符集（Charset）是根据操作系统的区域设置决定的。这意味着在不同的操作系统和区域设置下，Java程序的行为可能会不同，特别是在处理文本数据时。这种不一致性导致了许多问题，尤其是在跨平台部署和国际化应用程序时。而且 UTF-8 支持几乎所有语言的字符。所以 Java 18 将UTF-8设为Java平台的默认字符集，解决了跨平台的一致性问题。从此以后，Java 在处理文本数据时的行为在各种平台上就更加一致，减少了与字符编码相关的错误和混淆。

## JEP 408：简易Web服务器
Java 18 引入该特性的主要目的为开发者提供一个轻量级、简单易用的 HTTP 服务器，用于原型制作、测试和开发环境。

Java 18 提供了一个命令：`jwebserver`。利用这个命令，我们可以启动一个简单的 、最小化的静态 Web 服务器，但是它不支持 CGI 和 Servlet，所以最好的使用场景是用来测试、教育以及演示等需求。

## JEP 413：支持在 Java API 文档中加入代码片段
在 Javadoc 工具中引入了`@snippet`标签，允许文档作者在 API 文档中嵌入源代码片段。

在之前的 Java 文档中，代码示例通常是文本形式，容易过时且难以验证正确性。通过这个特性，我们可以确保示例代码的准确性和时效性。

而且，我们还可以设置高亮、链接到 API 文档的其他部分、甚至是自定义的 CSS 样式，使文档更加生动和易于阅读。

## JEP 416：用方法句柄重新实现核心反射
反射是 Java 中非常重要的一个功能，使用场景很多。在 Java 18 之前，Java 的反射 API 使用了许多原生方法来实现其功能，这些原生方法与 JVM 的内部结构紧密相关，导致维护和更新反射 API 变得复杂。

Java 18 重构 Java 核心反射 API，以使用方法句柄代替 Java 语言的反射机制中的原生方法，使得反射机制的实现更加简洁，易于理解和维护。同时由于方法句柄是在 Java 语言层面实现的，它们可以利用 JVM 的现有优化（如内联和 JIT 编译），从而提高反射操作的性能。下面是官方给出了新老实现的反射性能基准测试结果：
- Java 18 之前：  
```shell
Benchmark                                     Mode  Cnt   Score  Error  Units
ReflectionSpeedBenchmark.constructorConst     avgt   10  68.049 ± 0.872  ns/op
ReflectionSpeedBenchmark.constructorPoly      avgt   10  94.132 ± 1.805  ns/op
ReflectionSpeedBenchmark.constructorVar       avgt   10  64.543 ± 0.799  ns/op
ReflectionSpeedBenchmark.instanceFieldConst   avgt   10  35.361 ± 0.492  ns/op
ReflectionSpeedBenchmark.instanceFieldPoly    avgt   10  67.089 ± 3.288  ns/op
ReflectionSpeedBenchmark.instanceFieldVar     avgt   10  35.745 ± 0.554  ns/op
ReflectionSpeedBenchmark.instanceMethodConst  avgt   10  77.925 ± 2.026  ns/op
ReflectionSpeedBenchmark.instanceMethodPoly   avgt   10  96.094 ± 2.269  ns/op
ReflectionSpeedBenchmark.instanceMethodVar    avgt   10  80.002 ± 4.267  ns/op
ReflectionSpeedBenchmark.staticFieldConst     avgt   10  33.442 ± 2.659  ns/op
ReflectionSpeedBenchmark.staticFieldPoly      avgt   10  51.918 ± 1.522  ns/op
ReflectionSpeedBenchmark.staticFieldVar       avgt   10  33.967 ± 0.451  ns/op
ReflectionSpeedBenchmark.staticMethodConst    avgt   10  75.380 ± 1.660  ns/op
ReflectionSpeedBenchmark.staticMethodPoly     avgt   10  93.553 ± 1.037  ns/op
ReflectionSpeedBenchmark.staticMethodVar      avgt   10  76.728 ± 1.614  ns/op
```

- Java 18 的新实现：  
```shell
Benchmark                                     Mode  Cnt    Score   Error  Units
ReflectionSpeedBenchmark.constructorConst     avgt   10   32.392 ± 0.473  ns/op
ReflectionSpeedBenchmark.constructorPoly      avgt   10  113.947 ± 1.205  ns/op
ReflectionSpeedBenchmark.constructorVar       avgt   10   76.885 ± 1.128  ns/op
ReflectionSpeedBenchmark.instanceFieldConst   avgt   10   18.569 ± 0.161  ns/op
ReflectionSpeedBenchmark.instanceFieldPoly    avgt   10   98.671 ± 2.015  ns/op
ReflectionSpeedBenchmark.instanceFieldVar     avgt   10   54.193 ± 3.510  ns/op
ReflectionSpeedBenchmark.instanceMethodConst  avgt   10   33.421 ± 0.406  ns/op
ReflectionSpeedBenchmark.instanceMethodPoly   avgt   10  109.129 ± 1.959  ns/op
ReflectionSpeedBenchmark.instanceMethodVar    avgt   10   90.420 ± 2.187  ns/op
ReflectionSpeedBenchmark.staticFieldConst     avgt   10   19.080 ± 0.179  ns/op
ReflectionSpeedBenchmark.staticFieldPoly      avgt   10   92.130 ± 2.729  ns/op
ReflectionSpeedBenchmark.staticFieldVar       avgt   10   53.899 ± 1.051  ns/op
ReflectionSpeedBenchmark.staticMethodConst    avgt   10   35.907 ± 0.456  ns/op
ReflectionSpeedBenchmark.staticMethodPoly     avgt   10  102.895 ± 1.604  ns/op
ReflectionSpeedBenchmark.staticMethodVar      avgt   10   82.123 ± 0.629  ns/op
```

## JEP 417：向量 API（第三孵化器）
向量 API 是在 Java 16 中作为孵化器引入的，Java 17 经历第二次孵化，Java 18 再一次孵化。

向量 API 的目的是提供一个表达式丰富、编译时性能可预测的平台，用于编写复杂的向量计算，以充分利用现代处理器的 SIMD（单指令多数据）指令。Java 18 对向量 API 进行了进一步的改进和增强，以更好地利用硬件功能，提高 Java 在数值计算和机器学习等领域的性能。

| Java 版本 | 更新类型  | JEP     | 更新内容                                     |
|---------|-------|---------|------------------------------------------|
| Java 16 | 第一次孵化 | JEP 338 | 提供了一个平台无关的方式来表达向量计算，能够充分利用现代处理器上的向量硬件指令。 |
| Java 17 | 第二次孵化 | JEP 414 | 对 API 进行了改进，增加了性能优化和新的功能。                |
| Java 18 | 第三次孵化 | JEP 417 | 进一步增强 API，改进了性能和易用性。                     |

## JEP 418：互联网地址解析 SPI
Java 的网络地址解析机制长期以来一直是固定的，依赖于操作系统的解析机制。这限制了 Java 应用在处理网络地址时的灵活性和可扩展性。

Java 18 引入该特性的主要目标是引入一个新的服务提供接口（SPI），用于自定义网络地址解析。其主要内容：
- **服务提供接口 (SPI)**：允许开发者实现自定义的`InetAddressResolver`，用于替代默认的网络地址解析机制。
- **灵活配置**：应用程序可以通过配置文件或运行时参数指定使用哪个`InetAddressResolver`实现。
- **改进的 DNS 支持**: 提供了对现代 DNS 记录类型的支持，例如 DNSSEC。

## JEP 419：外部函数和内存 API（第三孵化器）
外部函数和内存 API 是在 Java 17 中作为孵化器引入的，其主要目的是改善 Java 与本地代码（如 C 或 C++）的互操作性。

传统上，Java 与本地代码的互操作需要使用 Java Native Interface (JNI)，这不仅复杂、性能有限，而且 JNI 的使用往往容易出错且不安全。

外部函数和内存 API 提供了一套更简洁的 API，用于调用本地函数和处理本地内存，降低了复杂性，而且还设计了更多的安全保护措施，降低了内存泄露和应用崩溃的风险。

主要是通过两个组件实现的：
- **Foreign Function Interface (FFI)**: 允许 Java 代码直接调用非 Java 代码，特别是用 C/C++ 编写的代码。这可以通过定义一种类型安全的方式来实现，同时避免了 Java 本地接口（JNI）的复杂性和开销。
- **Foreign Memory Access API**：提供了一种安全的方法来访问不受 JVM 管理的内存。这对于需要操作系统级别内存操作或者直接与外部设备交互的应用程序非常重要。

| Java 版本	 | 更新类型	  | JEP	    | 更新内容                   |
|----------|--------|---------|------------------------|
| Java 14  | 孵化器	   | JEP 370 | 引入了外部内存访问 API          |
| Java 15  | 第二次孵化	 | JEP 383 | 优化外部内存访问 API           |
| Java 16  | 孵化器	   | JEP 389 | 引入了外部链接器 API           |
| Java 16  | 第三次孵化	 | JEP 393 | 继续优化                   |
| Java 17  | 孵化器	   | JEP 412 | 引入了外部函数和内存 API         |
| Java 18  | 第二次孵化	 | JEP 419 | 在此版本中，API再次进行了一些改进和扩展。 |

## JEP 420： 模式匹配 Switch 表达式（预览）
在 Java 18 之前，处理多种类型通常需要使用多个`if-else`语句和类型检查。为了减少冗余的类型检查和类型转换代码，同时让代码更加直观，易于理解和维护。

于是 Java引入模式匹配的 Switch 表达式，通过扩展`switch`语句，使其能够支持类型模式，从而可以直接处理不同类型的数据。该特性首次在 Java 17 中作为预览特性引入，Java 18 作为第二次预览再次引入。

| Java 版本	 | 更新类型	  | JEP	    | 更新内容                     |
|----------|--------|---------|--------------------------|
| Java 17	 | 第一次预览	 | JEP 406 | 引入模式匹配的 Swith 表达式作为预览特性。 |
| Java 18	 | 第二次预览	 | JEP 420 | 对其做了改进和细微调整。             |

## JEP 421：弃用 Finalization 功能
Finalization 是 Java 早期版本引入的功能，用于在对象被垃圾收集器销毁之前执行清理操作。然而，这个机制存在诸多问题，比如性能不佳、行为不可预测、容易导致内存泄漏等。

Java 18 将该功能标记为废弃。这就意味着`finalize()`将不再被调用，从而消除了 Finalization 带来的所有问题。Java 18 推荐使用 Cleaner 和 PhantomReference 作为 Finalization 的替代方案。