# Java 26

- **JEP 500**: 准备使 final 真正表示最终
- **JEP 504**: 移除 Applet API
- **JEP 516**: 支持任何 GC 的 AOT 对象缓存
- **JEP 517**: HTTP Client API 支持 HTTP/3
- **JEP 522**: G1 GC 通过减少同步来提高吞吐量
- **JEP 524**: PEM 编码的加密对象（第二次预览）
- **JEP 525**: 结构化并发（第六次预览）
- **JEP 526**: 惰性常量（第二次预览）
- **JEP 529**: 向量 API（第十一次孵化）
- **JEP 530**: 模式、instanceof 和 switch 中的基本类型（第四次预览）

## JEP 500: 准备使 final 真正表示最终

该特性限制了深度反射操作，默认情况下通过反射修改 final 字段会在运行时产生警告。在 Java 中，final 关键字表示字段一旦赋值就不能再被修改，但通过反射机制（如 `Field.set()`）可以绕过这一限制。该特性旨在加强 final 的语义，使 final 字段真正表示"不可变"，提高代码的安全性和可预测性。

这一变化为未来版本中彻底禁止通过反射修改 final 字段做准备，有助于 JIT 编译器进行更激进的优化。

## JEP 504: 移除 Applet API

Applet API 早在 Java 9 中就被标记为弃用，Java 26 正式将其从 JDK 中移除。随着现代浏览器逐步放弃对 NPAPI 插件的支持，Java Applet 已经失去了运行环境。移除该 API 可以减少 JDK 的维护负担，并消除不再需要的安全考量。

## JEP 516: 支持任何 GC 的 AOT 对象缓存

该特性将 AOT（Ahead-of-Time）对象缓存功能扩展到支持所有垃圾回收器。此前，AOT 对象缓存仅能与特定的 GC 配合使用。通过这一改进，开发者可以使用 `-XX:AOTCache` 参数配合任意 GC（如 G1、ZGC、Shenandoah 等）来缓存 AOT 编译后的对象，从而加快应用程序的启动速度。

```bash
# 生成 AOT 缓存
java -XX:AOTCache=cache.aot -cp myapp.jar MyMainClass

# 使用 AOT 缓存运行应用
java -XX:AOTCache=cache.aot -cp myapp.jar MyMainClass
```

## JEP 517: HTTP Client API 支持 HTTP/3

该特性在 Java 的 HTTP Client API 中引入了对 HTTP/3 协议的支持。HTTP/3 基于 QUIC 传输协议，相比 HTTP/2 具有更好的弱网络环境表现和更低的连接建立延迟。

```java
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_3)
    .build();

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://example.com"))
    .build();

HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
System.out.println(response.statusCode());
```

## JEP 522: G1 GC 通过减少同步来提高吞吐量

该特性通过减少 G1 写屏障中的同步操作和内部锁的使用，提高了 G1 垃圾回收器的吞吐量。具体来说，它优化了 G1 写屏障指令的数量，减少了并发标记过程中的锁竞争，使应用程序在多线程环境下的性能得到提升。

这对于使用 G1 作为默认 GC 的服务端应用程序来说是一个重要的性能改进。

## JEP 524: PEM 编码的加密对象（第二次预览）

PEM（Privacy Enhanced Mail）是一种广泛使用的编码格式，用于表示加密对象（如密钥、证书等）。该特性提供了对 PEM 编码的加密对象的读取和写入支持，使 Java 能够更方便地与现有的加密基础设施进行集成。

在第二次预览中，可能对 API 进行了进一步的完善和优化。

## JEP 525: 结构化并发（第六次预览）

结构化并发是一种多线程编程方法，旨在简化多线程代码的管理和错误处理。它将不同线程中运行的多个任务视为单个工作单元，从而提高了代码的可读性、可维护性和可靠性。

该特性引入了 `StructuredTaskScope` 类，允许开发者将任务拆分为多个并发子任务，并在它们自己的线程中执行。

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
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

## JEP 526: 惰性常量（第二次预览）

惰性常量是一种新的常量求值机制，允许在首次使用时才计算常量的值，而不是在类加载时立即计算。这可以减少启动时间和内存占用，特别适用于那些很少使用或计算成本较高的常量。

在第二次预览中，该特性可能进一步完善了其语义和实现。

## JEP 529: 向量 API（第十一次孵化）

向量 API 提供了一种高效的方式来进行向量计算，适用于科学计算、机器学习等领域。该特性通过引入一组新的类和接口，允许开发者使用硬件加速的向量指令来执行计算，从而提高性能。

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

## JEP 530: 模式、instanceof 和 switch 中的基本类型（第四次预览）

该特性扩展了模式匹配的功能，允许在 `instanceof` 操作符和 `switch` 表达式中使用基本类型。这使得代码更加简洁和易读，减少了不必要的类型转换。

```java
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
```

在第四次预览中，该特性可能进一步调整了语法和语义，为正式发布做准备。
