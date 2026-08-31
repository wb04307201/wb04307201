<!--
module:
  parent: java
  slug: java/version/java-12
  type: article
  category: 主模块子文章
  summary: Java 12：8 个 JEP，含 switch 表达式预览、G1 改进、微基准套件
  depth: ⭐
-->

# Java 12

## 引言：变更说明

Java 12 是 8 个 JEP 的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

### 相关阅读

← [Java 11](../java-11/README.md) · [Java 13](../java-13/README.md) · [Java 全部版本](../README.md)

---

- **JEP 189**: Shenandoah：低暂停时间垃圾收集器（实验性）
- **JEP 230**: 微基准测试套件
- **JEP 325**: Switch 表达式（预览）
- **JEP 334**: JVM 常量 API
- **JEP 340**: 仅保留一个 AArch64 端口
- **JEP 341**: 默认 CDS 存档
- **JEP 344**: G1 的可中止混合收集
- **JEP 346**: G1 及时返回未使用的已提交内存

## JEP 189: Shenandoah：低暂停时间垃圾收集器（实验性）

Shenandoah 是一种实验性的垃圾收集器，旨在减少垃圾收集过程中的暂停时间。与传统的垃圾收集器不同，Shenandoah 通过并发的方式执行大部分垃圾收集工作，包括对象移动和引用更新，从而减少应用程序的停顿时间。

该特性对于需要低延迟的应用程序非常有用，例如实时系统、金融交易系统等。通过使用 Shenandoah 垃圾收集器，开发者可以在不影响应用程序性能的情况下更有效地管理内存。

## JEP 230: 微基准测试套件

微基准测试套件提供了一组标准的基准测试，用于衡量 Java 代码的性能。它允许开发者对小段代码进行精确的性能测试，比较不同实现方式的性能差异。

通过微基准测试套件，开发者可以更好地了解代码的性能特征，优化关键代码路径，提高应用程序的整体性能。例如，开发者可以使用微基准测试来比较不同算法的执行时间，选择最优的实现方式。

```java
import org.openjdk.jmh.annotations.*;
import java.util.concurrent.TimeUnit;

@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@State(Scope.Thread)
public class MyBenchmark {

    @Benchmark
    public void testMethod() {
        // 测试的代码
    }
}
```

## JEP 325: Switch 表达式（预览）

Switch 表达式扩展了传统的 `switch` 语句，使其可以返回值，并且可以使用更简洁的语法。它支持箭头语法（`->`）来简化代码，并且可以在 `case` 分支中使用表达式和语句。

该特性使得 `switch` 语句更加灵活和强大，减少了代码的冗余，提高了代码的可读性。例如，开发者可以使用 `switch` 表达式来简化多分支的条件判断，并将结果赋值给变量。

```java
String dayType = switch (day) {
    case "Monday", "Tuesday", "Wednesday", "Thursday", "Friday" -> "Weekday";
    case "Saturday", "Sunday" -> "Weekend";
    default -> throw new IllegalArgumentException("Invalid day: " + day);
};
System.out.println(dayType);
```

## JEP 334: JVM 常量 API

JVM 常量 API 提供了一种标准化的方式来操作 JVM 常量，例如类、方法、字段等的引用。它引入了一组新的类和接口，允许开发者在运行时获取和操作这些常量，而无需使用反射等复杂的技术。

通过 JVM 常量 API，开发者可以更安全、更高效地访问 JVM 常量，提高代码的可维护性和性能。例如，开发者可以使用该 API 来动态加载类、调用方法等。

```java
import java.lang.constant.ClassDesc;
import java.lang.constant.MethodTypeDesc;

ClassDesc stringDesc = ClassDesc.of("java.lang.String");
MethodTypeDesc concatMethodType = MethodTypeDesc.methodType(
    ClassDesc.of("java.lang.String"),
    ClassDesc.of("java.lang.String")
);
```

## JEP 340: 仅保留一个 AArch64 端口

在 Java 12 之前，JDK 为 AArch64 架构提供了两个不同的端口，分别针对不同的硬件平台进行优化。为了简化 JDK 的开发和维护，该特性决定仅保留一个 AArch64 端口，统一对 AArch64 架构的支持。

这一变化将使 JDK 能够更专注于一个端口的优化和功能开发，提高性能和稳定性。同时，也减少了开发者的配置复杂性，因为只需要使用一个 JDK 版本即可支持所有 AArch64 平台。

## JEP 341: 默认 CDS 存档

CDS（Class Data Sharing）是一种用于减少 Java 应用程序启动时间和内存占用的技术。它允许将常用的类数据在多个 JVM 实例之间共享，从而避免了重复加载和初始化这些类的开销。

该特性引入了默认的 CDS 存档，即在 JDK 安装时自动生成一个包含常用类数据的存档文件。这样，开发者无需手动配置 CDS，即可享受 CDS 带来的性能提升。

## JEP 344: G1 的可中止混合收集

G1（Garbage-First）垃圾收集器是一种面向服务器的垃圾收集器，旨在平衡吞吐量和低延迟。该特性改进了 G1 垃圾收集器的混合收集过程，使其可以在收集过程中根据需要中止，以减少对应用程序的影响。

通过可中止混合收集，G1 垃圾收集器可以更灵活地应对内存压力和应用程序的需求，提高垃圾收集的效率和性能。例如，当应用程序需要更多的内存时，G1 可以中止混合收集，优先满足应用程序的内存需求。

## JEP 346: G1 及时返回未使用的已提交内存

该特性改进了 G1 垃圾收集器的内存管理机制，使其能够及时返回未使用的已提交内存给操作系统。在传统的垃圾收集器中，已提交的内存通常会在 JVM 运行期间一直保留，即使部分内存不再使用。

通过及时返回未使用的已提交内存，G1 垃圾收集器可以减少 JVM 的内存占用，提高系统的资源利用率。这对于内存敏感的应用程序和云计算环境非常重要，可以节省成本并提高性能。

---

## 其他新特性（非 JEP）

Java 12 还包含多项非 JEP 的改进，以下列出对开发者最实用的特性：

### 核心库

#### Unicode 11 支持

新增 684 个字符（含 66 个表情符号）、11 个新文字区块和 7 种新文字。

#### POSIX_SPAWN 进程启动选项

`jdk.lang.Process.launchMechanism` 属性现可设为 `POSIX_SPAWN`，缓解 Linux 上生成子进程的罕见病态情况。默认值（`VFORK`）不变。

#### 紧凑数字格式化

`NumberFormat` 新增 `getCompactNumberInstance()` 方法，以简短、人类可读的形式格式化数字（如 1000 → "1K"，1000000 → "1M"）。

```java
NumberFormat fmt = NumberFormat.getCompactNumberInstance(Locale.US, NumberFormat.Style.SHORT);
System.out.println(fmt.format(1_000_000)); // "1M"
```

#### Properties.loadFromXML 规范合规

XML 解析器现在拒绝不合规的 XML 文档，抛出 `InvalidPropertiesFormatException`。

#### 日本新年号支持

支持 2019 年 5 月开始的日本新年号方块字符 U+32FF。`JapaneseEra.of()`、`valueOf()` 和 `values()` 已澄清适应未来日本年号添加的方式。

#### finalize 方法移除

`FileInputStream`/`FileOutputStream` 和 `ZipFile`/`Inflater`/`Deflater` 的 `finalize` 方法（JDK 9 已弃用）现已移除。

### 安全

#### TLS ChaCha20-Poly1305 密码套件

新增密码套件（默认启用）：
- TLS 1.3: `TLS_CHACHA20_POLY1305_SHA256`
- TLS 1.2: `TLS_ECDHE_ECDSA/RSA/DHE_RSA_WITH_CHACHA20_POLY1305_SHA256`

#### 禁用 TLS 匿名和 NULL 密码套件

匿名和 NULL 密码套件已添加到 `jdk.tls.disabledAlgorithms` 并默认禁用。

#### 禁用所有 DES TLS 密码套件

所有基于 DES 的 TLS 密码套件通过 `jdk.tls.disabledAlgorithms` 中的 "DES" 标识默认停用。

#### 移除 TLS v1 和 v1.1 必需支持

`SSLContext` API 不再要求所有 SE 实现必须支持 TLSv1 和 TLSv1.1。

#### java.security.manager 新选项

`java.security.manager` 系统属性新增 "disallow" 令牌选项，阻止 `System.setSecurityManager` 使用，提升不使用安全管理器的应用性能。

#### keytool -groupname 选项

`keytool -genkeypair` 新增 `-groupname` 选项指定命名曲线（如 `secp384r1`），优先于 `-keysize`。

#### JFR 安全事件

新增 4 个 JFR 事件：`jdk.SecurityPropertyModification`、`jdk.TLSHandshake`、`jdk.X509Validation`、`jdk.X509Certificate`。默认禁用。

#### X25519/X448 私钥编码格式修正

私钥编码修正为使用 RFC 8410 标准格式。不向后兼容；需替换不兼容的存储密钥。

### HotSpot / JVM

#### ZGC 并发类卸载

ZGC 现在支持并发类卸载，释放未使用类的数据结构，降低应用占用。对 GC 停顿时间零影响。

#### G1 标记周期释放内存

G1 现在可以在任何并发标记周期内将 Java 堆内存归还操作系统。可通过设置 `-Xms` 等于 `-Xmx` 禁用。

#### 老年代分配到替代内存设备

G1 和 Parallel GC 的实验性功能，通过 `-XX:AllocateOldGenAt=<path>` 将老年代分配到 NV-DIMM。

#### `-XX:+ExtensiveErrorReports` 标志

新标志用于 `hs_err<pid>.log` 中更详细的崩溃报告。产品构建中默认禁用。

### 工具

#### jdeps 传递依赖分析

`--print-module-deps`、`--list-deps` 和 `--list-reduce-deps` 现在执行传递模块依赖分析。`--no-recursive` 用于非传递分析。

#### javac 移除 Java 6 支持

已移除对 `-source`、`-target` 和 `--release` 值 `6`/`1.6` 的支持。

### 客户端库

#### 文件规范化缓存默认禁用

文件规范化缓存（存在长期正确性问题）现默认禁用。可通过 `sun.io.useCanonCaches` 系统属性重新启用。

#### Swing GTK 3.20+ 兼容性

Swing GTK Look and Feel 在 GTK+ 3.20+ 上无法渲染部分 UI 组件。可使用 `-Djdk.gtk.version=2.2` 请求 GTK2+ 渲染。

---

← [返回 Java 版本特性](../README.md)