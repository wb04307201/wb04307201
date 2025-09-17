# Java 24

- **JEP 404**: 分代式 Shenandoah（实验性）
- **JEP 450**: 紧凑对象头（实验性）
- **JEP 472**: 准备限制 JNI 的使用
- **JEP 475**: G1 的后期屏障扩展
- **JEP 478**: 密钥派生函数 API（预览）
- **JEP 479**: 移除 Windows 32 位 x86 端口
- **JEP 483**: 提前类加载与链接
- **JEP 484**: 类文件 API
- **JEP 485**: 流收集器
- **JEP 486**: 永久禁用安全管理器
- **JEP 487**: 作用域值（第四次预览）
- **JEP 488**: 模式、instanceof 和 switch 中的基本类型（第二次预览）
- **JEP 489**: 向量 API（第九次孵化）
- **JEP 490**: ZGC：移除非分代模式
- **JEP 491**: 无需固定同步虚拟线程
- **JEP 492**: 灵活的构造函数体（第三次预览）
- **JEP 493**: 无 JMODs 链接运行时镜像
- **JEP 494**: 模块导入声明（第二次预览）
- **JEP 495**: 简单源文件和实例主方法（第四次预览）
- **JEP 496**: 量子抗性模块 - 基于格的密钥封装机制
- **JEP 497**: 量子抗性模块 - 基于格的数字签名算法
- **JEP 498**: 使用 sun.misc.Unsafe 中的内存访问方法时发出警告
- **JEP 499**: 结构化并发（第四次预览）
- **JEP 501**: 弃用 32 位 x86 端口以待移除

## JEP 404: 分代式 Shenandoah（实验性）

分代式 Shenandoah 是对 Shenandoah 垃圾回收器的改进，引入了分代收集的概念。它将堆内存划分为年轻代和老年代，针对不同代的特点采用不同的垃圾回收策略。年轻代采用复制算法，快速回收短生命周期对象；老年代采用 Shenandoah 原有的并发标记压缩算法，减少垃圾回收停顿时间，提高应用程序的响应速度。这一特性对于内存占用较大且对响应时间要求较高的应用场景非常有帮助。

## JEP 450: 紧凑对象头（实验性）

紧凑对象头旨在优化对象的内存布局，减少对象头的大小。对象头通常包含对象的相关元数据，如标记字、类指针等。通过紧凑对象头技术，可以压缩这些元数据的存储空间，从而节省内存。这对于内存敏感的应用程序，如大规模数据处理和缓存系统，能够显著提高内存使用效率，减少内存碎片。

## JEP 472: 准备限制 JNI 的使用

JNI（Java Native Interface）允许 Java 代码与本地代码（如 C/C++）进行交互，但这也带来了一些安全性和性能方面的问题。该特性准备对 JNI 的使用进行限制，以增强 Java 平台的安全性和稳定性。具体措施可能包括限制某些 JNI 函数的调用、增加安全检查等，确保 JNI 的使用不会对 Java 应用程序造成潜在风险。

## JEP 475: G1 的后期屏障扩展

G1（Garbage - First）垃圾回收器是一种面向服务端应用的垃圾回收器。该特性对 G1 的后期屏障进行了扩展，后期屏障是在垃圾回收过程中用于跟踪对象引用变化的一种机制。通过扩展后期屏障，G1 可以更准确地跟踪对象引用，优化垃圾回收的标记和清理过程，提高垃圾回收的效率和性能，减少垃圾回收对应用程序性能的影响。

## JEP 478: 密钥派生函数 API（预览）

密钥派生函数 API 提供了一种标准化的方式来从初始密钥和其他数据派生额外的密钥。在现代加密中，为了避免密钥重复使用带来的安全隐患，通常需要为不同的加密目的生成多个不同的密钥。该 API 允许开发者使用统一的接口调用不同的密钥派生算法，如 HKDF、PBKDF2 等，方便地实现密钥派生功能，提高加密应用的安全性和开发效率。

```java
// 示例代码：使用 HKDF 算法派生密钥
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.security.spec.AlgorithmParameterSpec;
import java.security.spec.HKDFParameterSpec;
import java.security.KeyDerivationFunction;

public class KeyDerivationExample {
    public static void main(String[] args) throws Exception {
        // 初始密钥材料
        byte[] initialKeyMaterial = "initial_key_material".getBytes();
        // 盐值
        byte[] salt = "salt_value".getBytes();
        // 扩展信息
        byte[] info = "info_data".getBytes();

        // 创建 KDF 对象，使用 HKDF - SHA256 算法
        KeyDerivationFunction hkdf = KeyDerivationFunction.getInstance("HKDF - SHA256");

        // 创建 Extract 和 Expand 参数规范
        AlgorithmParameterSpec params =
                HKDFParameterSpec.ofExtract()
                        .addIKM(initialKeyMaterial)
                        .addSalt(salt)
                        .thenExpand(info, 32);

        // 派生一个 32 字节的 AES 密钥
        SecretKey key = hkdf.deriveKey(new SecretKeySpec(new byte[0], "AES"), params);

        System.out.println("Derived key length: " + key.getEncoded().length);
    }
}
```

## JEP 479: 移除 Windows 32 位 x86 端口

随着计算机硬件的发展，64 位架构已经成为主流。为了简化 JDK 的开发和维护，该特性决定移除对 Windows 32 位 x86 架构的支持。这意味着从 Java 24 开始，JDK 将不再提供适用于 Windows 32 位 x86 处理器的版本。这一变化将使 JDK 能够更专注于 64 位架构的优化和功能开发，提高性能和安全性，同时符合行业趋势，因为大多数现代 Windows 计算机都已经采用 64 位操作系统和处理器。

## JEP 483: 提前类加载与链接

提前类加载与链接允许在应用程序启动前对类进行加载和链接操作。传统的类加载和链接是在应用程序运行时动态进行的，这会增加应用程序的启动时间。通过提前进行这些操作，JVM 可以在启动前完成类的初始化准备工作，减少启动时的延迟，提高应用程序的启动速度。这对于需要快速启动的应用程序，如桌面应用和服务器应用，非常有帮助。

## JEP 484: 类文件 API

类文件 API 提供了一组用于操作 Java 类文件的接口和类。开发者可以使用该 API 读取、修改和生成 Java 类文件，实现动态代码生成、类文件分析等功能。这对于一些需要动态生成代码或对类文件进行定制化处理的框架和工具非常有用，例如 AOP（面向切面编程）框架、代码优化工具等。

```java
// 示例代码：使用类文件 API 读取类文件信息
import jdk.incubator.classfile.*;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

public class ClassFileApiExample {
    public static void main(String[] args) throws IOException {
        byte[] classBytes = Files.readAllBytes(Paths.get("MyClass.class"));
        ClassFile classFile = ClassFile.parse(classBytes);

        System.out.println("Class name: " + classFile.getName());
        System.out.println("Super class name: " + classFile.getSuperName());

        for (FieldInfo field : classFile.getFields()) {
            System.out.println("Field: " + field.getName() + ", type: " + field.getDescriptor());
        }

        for (MethodInfo method : classFile.getMethods()) {
            System.out.println("Method: " + method.getName() + ", descriptor: " + method.getDescriptor());
        }
    }
}
```

## JEP 485: 流收集器

流收集器是 Java 流 API 的扩展，它提供了一种更方便的方式将流中的元素收集到特定的数据结构中。传统的流收集操作通常使用 `Collectors` 类提供的方法，但这些方法在某些场景下可能不够灵活。流收集器允许开发者自定义收集逻辑，将流元素收集到自定义的数据结构中，或者对收集过程进行更复杂的处理，提高了流操作的灵活性和功能性。

```java
import java.util.*;
import java.util.stream.*;

public class StreamGatherersExample {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

        // 使用自定义的流收集器将偶数收集到一个 Set 中，奇数收集到一个 List 中
        Map<Boolean, Object> result = numbers.stream().collect(
                Collectors.partitioningBy(
                        n -> n % 2 == 0,
                        Collectors.teeing(
                                Collectors.toSet(),
                                Collectors.toList(),
                                (set, list) -> new Object[]{set, list}
                        )
                )
        );

        Set<Integer> evenSet = (Set<Integer>) ((Object[]) result.get(true))[0];
        List<Integer> oddList = (List<Integer>) ((Object[]) result.get(false))[1];

        System.out.println("Even numbers: " + evenSet);
        System.out.println("Odd numbers: " + oddList);
    }
}
```

## JEP 486: 永久禁用安全管理器

安全管理器是 Java 平台中用于实现安全策略的组件，它可以限制 Java 应用程序的权限，如文件访问、网络访问等。然而，随着 Java 安全模型的发展和其他安全机制的不断完善，安全管理器的使用逐渐减少。该特性决定永久禁用安全管理器，以简化 Java 平台的安全架构，减少安全管理的复杂性。禁用安全管理器后，Java 应用程序将不再依赖该组件进行安全控制，而是采用更现代的安全机制。

## JEP 487: 作用域值（第四次预览）

作用域值是一种在特定作用域内共享不可变数据的机制。它类似于线程局部变量，但更适用于虚拟线程和结构化并发等新的编程模型。作用域值允许在大型程序中的组件之间安全有效地共享数据，而无需求助于方法参数。这对于减少代码冗余和提高代码的可维护性非常有帮助。在第四次预览中，可能会对作用域值的性能、易用性等方面进行进一步的优化和改进。

```java
import jdk.incubator.concurrent.ScopedValue;
import jdk.incubator.concurrent.ScopedValue.Where;

public class ScopedValuesExample {
    private static final ScopedValue<String> USER_NAME = ScopedValue.newInstance();

    public static void main(String[] args) {
        Where<String> where = ScopedValue.where(USER_NAME, "Alice");
        where.run(() -> {
            System.out.println("Hello, " + USER_NAME.get());
            nestedScope();
        });
    }

    private static void nestedScope() {
        Where<String> nestedWhere = ScopedValue.where(USER_NAME, "Bob");
        nestedWhere.run(() -> {
            System.out.println("Nested scope: " + USER_NAME.get());
        });
    }
}
```

## JEP 488: 模式、instanceof 和 switch 中的基本类型（第二次预览）

该特性扩展了模式匹配的功能，允许在 `instanceof` 操作符和 `switch` 表达式中使用基本类型。这使得代码更加简洁和易读，减少了不必要的类型转换。在第二次预览中，可能会根据用户反馈对语法和语义进行进一步的调整和完善，提高该特性的稳定性和可用性。

```java
public class PatternMatchingWithPrimitivesExample {
    public static void main(String[] args) {
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
    }
}
```

## JEP 489: 向量 API（第九次孵化）

向量 API 提供了一种高效的方式来进行向量计算，适用于科学计算、机器学习等领域。该特性通过引入一组新的类和接口，允许开发者使用硬件加速的向量指令来执行计算，从而提高性能。在第九次孵化中，可能会对向量 API 的功能、性能和兼容性进行进一步的优化和测试，为正式发布做准备。

```java
import jdk.incubator.vector.*;

public class VectorApiExample {
    public static void main(String[] args) {
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
    }
}
```

## JEP 490: ZGC：移除非分代模式

ZGC（Z Garbage Collector）是一种高性能的垃圾回收器，它具有低延迟的特点。该特性移除了 ZGC 的非分代模式，使 ZGC 专注于分代收集策略。分代收集可以根据对象