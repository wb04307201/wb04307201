# Java 17

- **JEP 306**: 恢复始终严格的浮点语义
- **JEP 356**: 增强的伪随机数生成器
- **JEP 382**: 新的 macOS 渲染管线
- **JEP 391**: macOS/AArch64 移植
- **JEP 398**: 弃用 Applet API 以待移除
- **JEP 403**: 强力封装 JDK 内部元素
- **JEP 406**: switch 表达式中的模式匹配（预览）
- **JEP 407**: 移除 RMI 激活
- **JEP 409**: 密封类
- **JEP 410**: 移除实验性的 AOT 和 JIT 编译器
- **JEP 411**: 弃用安全管理器以待移除
- **JEP 412**: 外部函数和内存 API（孵化器）
- **JEP 414**: 向量 API（第二次孵化）
- **JEP 415**: 上下文特定反序列化过滤器

## JEP 306: 恢复始终严格的浮点语义

该特性恢复了 Java 中始终严格的浮点语义。在早期版本的 Java 中，为了优化性能，在某些情况下对浮点运算采用了非严格语义。然而，这种做法可能导致不同平台和不同 JVM 实现上的计算结果不一致，给一些对浮点精度要求严格的场景（如科学计算、金融计算等）带来了问题。

恢复始终严格的浮点语义后，Java 将遵循 IEEE 754 标准，确保浮点运算在不同环境下都能产生一致且精确的结果。这有助于提高 Java 在对浮点精度敏感领域的应用可靠性。

例如，在之前的非严格语义下，以下代码在不同 JVM 实现上可能得到不同结果：
```java
double a = 1.0;
double b = 0.1;
double c = 0.2;
double result = a - b - c;
System.out.println(result); 
```
恢复严格语义后，结果将更加一致和可预测。

## JEP 356: 增强的伪随机数生成器

此特性增强了 Java 中的伪随机数生成器（PRNG）。原有的 `java.util.Random` 类在随机数生成的质量和性能上存在一定局限性。新的特性引入了更强大、更灵活的伪随机数生成器接口和实现。

它提供了多种不同类型的随机数生成算法，开发者可以根据具体需求选择合适的生成器。例如，对于需要高安全性随机数的场景，可以使用加密强度的随机数生成器；对于对性能要求较高且对随机数质量要求相对宽松的场景，可以选择快速的随机数生成器。

```java
// 使用新的随机数生成器
import java.util.random.RandomGenerator;
import java.util.random.RandomGeneratorFactory;

RandomGenerator generator = RandomGeneratorFactory.of("L64X128MixRandom").create();
int randomNumber = generator.nextInt();
System.out.println(randomNumber);
```

## JEP 382: 新的 macOS 渲染管线

该特性为 macOS 平台引入了新的渲染管线。随着 macOS 系统的不断更新和图形技术的发展，原有的渲染管线在某些方面可能无法充分发挥系统的性能优势。新的渲染管线针对 macOS 的硬件和图形架构进行了优化，能够提供更好的图形渲染性能和视觉效果。

它支持更高效的图形绘制、更流畅的动画效果以及更好的硬件加速。对于在 macOS 平台上运行的 Java 图形应用程序（如游戏、图形编辑工具等），新的渲染管线将显著提升用户体验。

## JEP 391: macOS/AArch64 移植

此特性实现了 Java 在 macOS/AArch64 架构上的移植。随着苹果公司逐步将其产品从 Intel x86 架构转向自研的 AArch64 架构（如 Apple Silicon 芯片），为了确保 Java 能够在新的苹果设备上顺利运行，需要进行相应的移植工作。

通过该特性，Java 开发者可以在基于 AArch64 架构的 macOS 设备上开发和运行 Java 应用程序，无需担心架构兼容性问题。这有助于扩大 Java 在苹果生态系统中的应用范围。

## JEP 398: 弃用 Applet API 以待移除

随着 Web 技术的不断发展，基于浏览器插件的 Applet 技术已经逐渐被淘汰。现代浏览器对插件的支持越来越有限，而且 Applet 存在安全风险、性能问题以及跨平台兼容性等方面的不足。

该特性将 Applet API 标记为弃用，并计划在未来版本中移除。这意味着开发者应逐渐停止使用 Applet 技术，转而采用更现代、更安全的 Web 技术（如 HTML5、JavaScript 等）来实现类似的功能。

## JEP 403: 强力封装 JDK 内部元素

为了增强 JDK 的安全性和稳定性，该特性强力封装了 JDK 的内部元素。在之前的版本中，JDK 的一些内部类、方法和字段可以被外部代码访问，这可能导致安全漏洞和不可预测的行为。

强力封装后，JDK 的内部元素将受到更严格的访问控制，外部代码无法直接访问这些内部元素。这有助于防止恶意代码对 JDK 内部状态的篡改，提高 JDK 的安全性和可靠性。同时，也使得 JDK 的内部实现可以更自由地进行修改和优化，而不必担心对外部代码的影响。

## JEP 406: switch 表达式中的模式匹配（预览）

模式匹配是一种强大的编程特性，它允许根据对象的类型和结构进行更灵活的条件判断。该特性在 switch 表达式中引入了模式匹配功能，使得代码更加简洁和易读。

在传统的 switch 语句中，只能根据常量值进行匹配，而模式匹配可以匹配对象的类型、属性等。例如，可以使用模式匹配来处理不同类型的对象，并根据对象的属性执行不同的操作。

```java
// 使用 switch 表达式中的模式匹配
record Point(int x, int y) {}

Object obj = new Point(1, 2);
String result = switch (obj) {
    case Integer i -> "It's an integer: " + i;
    case String s -> "It's a string: " + s;
    case Point p -> "It's a point: (" + p.x() + ", " + p.y() + ")";
    default -> "Unknown type";
};
System.out.println(result);
```

## JEP 407: 移除 RMI 激活

远程方法调用（RMI）激活是 RMI 机制中的一个功能，它允许远程对象在需要时被激活（创建和初始化）。然而，随着分布式计算技术的发展，RMI 激活的使用越来越少，而且该功能存在一些安全风险和复杂性。

该特性移除了 RMI 激活功能，简化了 RMI 机制，提高了其安全性和可维护性。开发者可以使用其他更现代、更安全的分布式计算技术（如 RESTful API、gRPC 等）来替代 RMI 激活。

## JEP 409: 密封类

密封类是一种新的类声明机制，它允许类或接口的作者控制哪些其他类或接口可以扩展或实现它们。通过密封类，可以定义一个封闭的类层次结构，限制子类的数量和类型。

密封类适用于需要严格控制类继承关系的场景，例如定义一组相关的类，这些类具有特定的行为和关系，不希望被外部随意扩展。使用密封类可以提高代码的安全性和可维护性，避免因不恰当的子类扩展而导致的问题。

```java
// 定义一个密封类
sealed class Shape permits Circle, Rectangle {
    // 类体
}

final class Circle extends Shape {
    // 类体
}

final class Rectangle extends Shape {
    // 类体
}
```

## JEP 410: 移除实验性的 AOT 和 JIT 编译器

提前编译（AOT）和即时编译（JIT）是提高 Java 程序性能的重要技术。然而，之前引入的实验性 AOT 和 JIT 编译器存在一些问题和局限性，例如兼容性问题、性能不稳定等。

该特性移除了这些实验性的编译器，以便集中精力优化现有的 JIT 编译器（如 HotSpot 中的 C2 编译器）和探索更有效的编译技术。这有助于提高 Java 程序的性能和稳定性。

## JEP 411: 弃用安全管理器以待移除

安全管理器是 Java 中用于实施安全策略的机制，它可以控制代码对系统资源的访问。然而，随着 Java 安全模型的发展和现代安全需求的变化，安全管理器逐渐暴露出一些问题，例如性能开销大、配置复杂等。

该特性将安全管理器标记为弃用，并计划在未来版本中移除。开发者应采用更现代、更灵活的安全机制（如 Java 模块系统的安全特性、容器化技术等）来保障应用程序的安全。

## JEP 412: 外部函数和内存 API（孵化器）

该特性引入了一个新的 API，允许 Java 代码更安全、更高效地与本地代码（如 C/C++ 编写的库）进行交互，以及直接访问本地内存。在之前的版本中，Java 与本地代码交互主要通过 Java Native Interface（JNI）实现，但 JNI 存在一些缺点，如性能较低、使用复杂等。

外部函数和内存 API 提供了一种更简洁、更安全的方式来调用本地函数和操作本地内存。它支持自动内存管理、类型安全检查等功能，减少了因与本地代码交互而导致的安全风险和内存泄漏问题。

```java
// 使用外部函数和内存 API 示例（假设已导入相关包）
MemorySegment segment = MemorySegment.allocateNative(100);
try (var scope = new ResourceScope()) {
    MemoryAddress address = segment.baseAddress();
    // 调用本地函数（这里只是示例，实际需要定义本地函数）
    // assume we have a native function that adds two numbers
    int result = NativeFunctions.add(address.toRawLongValueType(), 10, 20);
    System.out.println(result);
}
```

## JEP 414: 向量 API（第二次孵化）

向量 API 旨在提供一种高效的方式来处理向量计算。向量计算在科学计算、机器学习、图形处理等领域有着广泛的应用。通过利用硬件的向量指令集（如 SIMD 指令），向量 API 可以显著提高计算性能。

该特性是向量 API 的第二次孵化，在之前的基础上进行了进一步的优化和改进。它提供了一组丰富的类和接口，允许开发者以简洁的方式表达向量计算，同时充分利用硬件的并行计算能力。

```java
// 使用向量 API 进行向量加法示例（假设已导入相关包）
VectorSpecies<Float> SPECIES = FloatVector.SPECIES_256;
float[] a = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f};
float[] b = {9.0f, 10.0f, 11.0f, 12.0f, 13.0f, 14.0f, 15.0f, 16.0f};
float[] result = new float[8];

for (int i = 0; i < a.length; i += SPECIES.length()) {
    FloatVector va = FloatVector.fromArray(SPECIES, a, i);
    FloatVector vb = FloatVector.fromArray(SPECIES, b, i);
    FloatVector vr = va.add(vb);
    vr.intoArray(result, i);
}

System.out.println(Arrays.toString(result));
```

## JEP 415: 上下文特定反序列化过滤器

反序列化是将序列化的对象数据重新构建为对象的过程。然而，反序列化过程可能存在安全风险，例如恶意构造的序列化数据可能导致代码执行漏洞。

上下文特定反序列化过滤器允许开发者根据反序列化的上下文（如类加载器、线程等）动态地控制哪些类可以被反序列化。通过设置合适的过滤器，可以防止恶意类的加载和实例化，提高反序列化过程的安全性。

```java
// 使用上下文特定反序列化过滤器示例
import java.io.*;
import java.util.function.Predicate;

class MyFilter implements Predicate<Class<?>> {
    @Override
    public boolean test(Class<?> clazz) {
        // 只允许反序列化特定的类
        return clazz == String.class || clazz == Integer.class;
    }
}

public class DeserializationExample {
    public static void main(String[] args) throws Exception {
        String serializedData = "..."; // 序列化数据
        try (var in = new ByteArrayInputStream(serializedData.getBytes());
             var ois = new ObjectInputStream(in)) {
            // 设置反序列化过滤器
            ObjectInputFilter filter = new MyFilter();
            ois.setObjectInputFilter(filter);
            Object obj = ois.readObject();
            System.out.println(obj);
        }
    }
}
```