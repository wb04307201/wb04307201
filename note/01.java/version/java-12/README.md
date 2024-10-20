# Java 12

- JEP 189：Shenandoah 垃圾收集器（预览特性）
- JEP 325：Switch 表达式（预览特性）：Java 12 新特性—Switch 表达式
- JEP 334：JVM 常量 API
- JEP 230：微基准测试套件（JMH）的支持
- 新增 String API：Java 12 新特性—新增 String API
- 新增 Files API：Java 12 新特性—新增 Files API
- 新增 NumberFormat API：Java 12 新特性—新增 NumberFormat API
- 新增 Collectors API：Java 12 新特性—新增 Collectors API
- JEP 340：移除多余ARM64实现
- JEP 341：默认CDS归档
- JEP 344：G1的可中断 mixed GC

## JEP 189：Shenandoah 垃圾收集器（预览特性）
Shenandoah 垃圾收集器，一个专门用来处理大堆（Heap）和低延迟垃圾收集器，目前是一个实验性质的垃圾收集器。

对于需要处理大量数据的应用，如高吞吐和大内存的应用，传统垃圾收集器在回收内存时可能导致明显的停顿。为了解决这个问题，尤其是在大内存需求的应用场景中，引入 Shenandoah 垃圾收集器。

Shenandoah 使用了一种用于并发压缩堆时维护对象引用的技术（Brooks Pointers：布鲁克斯指针）。这种技术允许收集器在压缩堆时并行地移动对象，而不必暂停应用线程，这就允许Shenandoah 能够在应用线程运行的同时进行垃圾回收，从而减少停顿。

Shenandoah 有如下几大好处：
- **显著减少停顿时间**：Shenandoah 可以在应用运行时并行地进行垃圾回收，显著减少了停顿时间，这对于需要高响应性的应用来说至关重要。
- **适用于大内存应用**：对于拥有大量内存的应用程序，Shenandoah 提供了更平滑的性能表现，减少了因垃圾收集引起的性能波动。

## JEP 325：Switch 表达式（预览特性）
传统的`switch`语句在语法上比较繁琐，容易出错，特别是在忘记写`break`语句的情况下，为了解决这一问题 Java 引`Switch`表达式作为一项预览特性，该项特性提升了`switch`语句的灵活性和简洁性。它带来了如下几大变化：
- **新语法**  
传统的`switch`语句要求每个`case`后面跟随一段代码块。而新的`switch`表达式允许使用更简洁的箭头语法`->`，直接将一个值与特定的`case`关联起来。
- **表达式形式**  
在新的`switch`表达式中，可以直接返回一个值，而不是像以前那样仅作为一个控制流语句。这使得`switch`可以更加灵活地应用在各种场景中。

## JEP 334：JVM 常量 API
Java 虚拟机不仅支持 Java 语言，还支持许多动态语言（如 Kotlin、Scala、Groovy），这些语言在运行时经常需要与 JVM 的底层常量池交互。提供一个标准的 API 可以让这些操作更加容易和一致。

Java 12 引入特性：JVM 常量 API，它提供了一套 API，用于表示在类文件中作为常量池项出现的各种类型的常量。这些 API 使得开发人员可以以编程方式描述和操纵那些通常由 Java 虚拟机在低级别处理的常量。这个 API 主要包含在`java.lang.constant`包中，其中包括`Constable`和`ConstantDesc`等接口，以及多个实现这些接口的类，如`ClassDesc`、`MethodTypeDesc`等。

## JEP 230：微基准测试套件（JMH）的支持
在 Java 应用程序的开发过程中，精确地测量代码的性能至关重要，尤其是在优化瓶颈或进行微调时，但是Java 虚拟机的复杂性使得准确地进行微基准测试变得困难（比如 JIT 编译、垃圾收集等）。

于是 Java 官方提供了一套用于微基准测试的框架：JMH。JMH是专门设计用来准确地测量和基准 Java 代码的性能，它提供了一种准确测量 Java 代码性能的方法，特别是对于那些微小和精细的性能变化。

Java 12 为JDK源代码添加了一套微基准测试（大约100个），简化了现有微基准测试的运行和新基准测试的创建过程。 它基于Java Microbenchmark Harness（JMH）并支持JMH更新。

该特性可以让我们轻松地运行当前的微基准测试并为JDK源代码添加新的微基准测试。 可以基于Java Microbenchmark Harness（JMH）轻松测试JDK性能。 它将支持JMH更新，并在套件中包含一组（约100个）基准测试。

## 新增 String API
Java 12 对`String`进一步增强，引入 3 个方法：
- **indent()**：根据给定的数量调整每一行的缩进。
- **transform()**：将字符串转换为 R 形式的结果。
- **describeConstable()**：该方法用于支持新的常量 API，它返回一个`Optional`，描述字符串的常量描述。

## 新增 Files API
Java 12 对 Files 类进一步增强，新增一个 API：
- **mismatch()**：用于比较两个文件的内容。它返回两个文件内容第一次不匹配的位置的索引。

## 新增 NumberFormat API
为了更好地处理数字格式化，Java 12 引入了紧凑型数字格式化的功能，它允许 NumberFormat 以更紧凑、更易于阅读的方式格式化数字。例如，将 "1,000" 格式化为 "1K"，或将 "1,000,000" 格式化为 "1M"。这种格式在显示大量数据时特别有用，可以帮助用户更快地理解数字的规模。
```java
NumberFormat fmt = NumberFormat.getCompactNumberInstance(Locale.US, NumberFormat.Style.SHORT);
String result = fmt.format(1000);
System.out.println(result);
```

## 新增 Collectors API
引入`teeing()`，该方法是一个非常强大的收集器（Collector）。它接受两个收集器和一个二元运算符，可以并行地将数据发送到两个不同的收集器，并在最后将这两个收集器的结果合并。
```java
Collectors.teeing(Collector<? super T,A,R1> downstream1, Collector<? super T,A,R2> downstream2, BiFunction<? super R1,? super R2,R> merger)
```

## JEP 340：移除多余ARM64实现
在 Java 12 之前，Java 有两个 AArch64 端口：一个用于 OpenJDK，另一个用于 Oracle JDK。这造成了维护上的重复和效率问题。

Java 12 合并两个 AArch64 端口，同时统一他们的代码库，这就意味着未来所有的 AArch64 特定代码将在同一个代码库中维护，从而简化了开发和维护工作。

## JEP 341：默认CDS归档
类数据共享（Class Data Sharing, CDS）是 Java 为加速应用启动时间和减少内存占用而引入的技术。它允许将类元数据存储在共享存档中，这样不同的 Java 进程可以共享这些数据，而不是每个进程都单独加载。但是在 Java 12 之前，创建 CDS 存档需要手动执行，这对于某些用户来说可能是个技术障碍。

Java 12 引入默认 CSD 归档，它的核心在 JDK 构建过程中生成默认的 CDS 存档。这就表明用户无需手动创建 CDS 存档，就可以直接享受类数据共享带来的性能优势。

默认 CSD 归档有如下几个好处：
- **提高启动速度**：由于默认的 CDS 存档，Java 应用的启动时间可以显著减少。
- **减少内存占用**：共享类元数据减少了内存占用，特别是在多个 Java 应用同时运行时更加明显。
- **用户友好**：无需用户额外操作，使得所有用户都能轻松受益于 CDS 技术。

## EP 344：G1的可中断 mixed GC
Java 12 之前，G1 垃圾收集器在执行混合收集（即同时回收年轻代和老年代）时，有时会导致较长的停顿时间，这对那些低延迟的应用来说是一个不可接受的问题。

Java 12 引入了一种机制，允许 G1 垃圾收集器在执行混合收集时，在超过预设的停顿时间阈值时提前中断收集过程。

同时G1 垃圾收集器可以根据之前的收集数据和当前的停顿时间目标，动态地调整其行为。这意味着 G1 收集器将基于实时性能反馈来优化其垃圾收集过程。