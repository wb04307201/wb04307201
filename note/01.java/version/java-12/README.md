# Java 12

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