# Java 16

- **JEP 338**: Vector API（孵化器）
- **JEP 347**: 启用 C++14 语言特性
- **JEP 357**: 从 Mercurial 迁移到 Git
- **JEP 369**: 迁移到 GitHub
- **JEP 376**: ZGC：并发线程栈处理
- **JEP 380**: Unix 域套接字通道
- **JEP 386**: Alpine Linux 移植
- **JEP 387**: 弹性元空间
- **JEP 388**: Windows/AArch64 移植
- **JEP 389**: 外部链接器 API（孵化器）
- **JEP 390**: 针对基于值的类的警告
- **JEP 392**: 打包工具
- **JEP 393**: 外部内存访问 API（第三次孵化）
- **JEP 394**: instanceof 的模式匹配
- **JEP 395**: 记录类
- **JEP 396**: 默认情况下强封装 JDK 内部元素
- **JEP 397**: 密封类（第二次预览）
- **Stream API 增强**

## JEP 338: Vector API（孵化器）
Vector API 旨在提供一种在 Java 中执行向量计算的机制，这些计算可以在支持向量指令的硬件上高效运行。通过使用该 API，开发者能够编写出可移植且性能优化的代码，用于处理数值计算密集型任务，如科学计算、机器学习等。例如，在处理大规模数组的数学运算时，Vector API 可以利用硬件的向量指令集（如 SSE、AVX 等）并行处理多个数据元素，从而显著提高计算速度。

```java
import jdk.incubator.vector.*;

public class VectorExample {
    public static void main(String[] args) {
        int[] array = {1, 2, 3, 4, 5, 6, 7, 8};
        int[] result = new int[array.length];

        // 获取默认的整数向量种类
        VectorSpecies<Integer> species = IntVector.SPECIES_256;

        int i = 0;
        for (; i <= array.length - species.length(); i += species.length()) {
            // 从数组加载向量
            IntVector va = IntVector.fromArray(species, array, i);
            // 对向量进行乘法运算（这里乘以 2）
            IntVector vb = va.mul(2);
            // 将结果存储回数组
            vb.intoArray(result, i);
        }

        // 处理剩余元素
        for (; i < array.length; i++) {
            result[i] = array[i] * 2;
        }

        // 输出结果
        for (int num : result) {
            System.out.print(num + " ");
        }
    }
}
```

## JEP 347: 启用 C++14 语言特性
此特性允许 JDK 的本地代码（主要是用 C++ 编写的部分）使用 C++14 标准引入的语言特性。C++14 在 C++11 的基础上进一步增强，提供了更多便利的功能和改进，如泛型 lambda 表达式、变量模板、返回类型推导等。启用 C++14 语言特性可以使 JDK 的本地代码编写更加简洁、高效，提高代码的可读性和可维护性，同时也能利用现代 C++ 的优势来优化性能。例如，使用泛型 lambda 表达式可以简化代码中回调函数的编写，使代码更加紧凑。

## JEP 357: 从 Mercurial 迁移到 Git
Mercurial 和 Git 都是流行的版本控制系统，但 Git 在全球开发者社区中更为广泛使用，具有更丰富的生态系统和工具支持。将 JDK 的代码库从 Mercurial 迁移到 Git，使得更多的开发者能够更方便地参与到 JDK 的开发中来。Git 的分布式架构和强大的分支管理功能，使得开发者可以更轻松地进行代码的克隆、分支创建、提交和合并等操作。此外，迁移到 Git 也有助于与现有的基于 Git 的开发工具和平台（如 GitHub）更好地集成，提高开发效率。

## JEP 369: 迁移到 GitHub
GitHub 是一个基于 Git 的代码托管平台，提供了丰富的协作功能，如问题跟踪、拉取请求、代码审查等。将 JDK 的代码库迁移到 GitHub 上，使得全球的 Java 开发者能够更加方便地访问 JDK 的源代码、报告问题、提交贡献代码。这促进了 Java 社区的开放性和协作性，加速了 JDK 的开发和改进。开发者可以通过 GitHub 的界面轻松地浏览代码、提出改进建议、参与讨论，并且可以通过拉取请求的方式将自己的代码贡献提交给 JDK 开发团队进行审查和合并。

## JEP 376: ZGC：并发线程栈处理
ZGC（Z Garbage Collector）是 Java 中的一种低延迟垃圾回收器。该特性增强了 ZGC 的功能，使其能够并发地处理线程栈。在传统的垃圾回收过程中，线程栈的处理通常需要暂停应用程序线程，这可能会导致应用程序的停顿，影响性能。而 ZGC 的并发线程栈处理技术允许垃圾回收器在应用程序线程继续运行的同时，对线程栈进行扫描和更新引用，从而减少了垃圾回收对应用程序的停顿时间，提高了应用程序的响应能力和吞吐量。这对于需要低延迟的应用程序，如实时交易系统、在线游戏等非常重要。

## JEP 380: Unix 域套接字通道
Unix 域套接字是一种在 Unix 和类 Unix 系统上用于同一主机上进程间通信的机制。与传统的网络套接字相比，Unix 域套接字具有更高的性能和更低的开销，因为它们不需要经过网络协议栈的处理。该特性在 Java 中引入了对 Unix 域套接字通道的支持，使得 Java 应用程序能够更高效地在同一主机上的不同进程之间进行通信。例如，在一个复杂的服务器应用程序中，不同的组件可以以独立的进程运行，并通过 Unix 域套接字通道进行快速的数据交换，提高系统的整体性能和可扩展性。

```java
import java.io.IOException;
import java.net.StandardProtocolFamily;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.file.*;
import java.nio.file.attribute.*;
import java.util.concurrent.*;

public class UnixDomainSocketExample {
    public static void main(String[] args) throws Exception {
        Path socketPath = Paths.get("/tmp/test.sock");
        // 清理可能存在的旧套接字文件
        Files.deleteIfExists(socketPath);

        // 创建服务器端套接字通道
        try (ServerSocketChannel serverChannel = ServerSocketChannel.open();
             AsynchronousFileChannel fileChannel = AsynchronousFileChannel.open(socketPath,
                     StandardOpenOption.CREATE, StandardOpenOption.READ, StandardOpenOption.WRITE)) {
            serverChannel.bind(new java.net.UnixDomainSocketAddress(socketPath));
            serverChannel.configureBlocking(false);

            // 创建客户端套接字通道
            try (SocketChannel clientChannel = SocketChannel.open(StandardProtocolFamily.UNIX)) {
                clientChannel.connect(new java.net.UnixDomainSocketAddress(socketPath));

                // 服务器端接受连接
                Selector selector = Selector.open();
                serverChannel.register(selector, SelectionKey.OP_ACCEPT);

                while (true) {
                    selector.select();
                    for (SelectionKey key : selector.selectedKeys()) {
                        if (key.isAcceptable()) {
                            SocketChannel acceptedChannel = serverChannel.accept();
                            acceptedChannel.configureBlocking(false);
                            acceptedChannel.register(selector, SelectionKey.OP_READ);
                        } else if (key.isReadable()) {
                            SocketChannel channel = (SocketChannel) key.channel();
                            ByteBuffer buffer = ByteBuffer.allocate(1024);
                            int bytesRead = channel.read(buffer);
                            if (bytesRead == -1) {
                                channel.close();
                            } else {
                                buffer.flip();
                                System.out.println("Server received: " + new String(buffer.array(), 0, bytesRead));
                                // 简单回显
                                channel.write(buffer);
                            }
                        }
                    }
                    selector.selectedKeys().clear();
                }
            }
        }
    }
}
```

## JEP 386: Alpine Linux 移植
Alpine Linux 是一种轻量级的 Linux 发行版，以其小巧的体积、安全性和资源效率而受到广泛关注。将 JDK 移植到 Alpine Linux 上，使得 Java 应用程序能够在这种轻量级的 Linux 环境中运行。这对于容器化部署和云计算环境非常有利，因为 Alpine Linux 的小体积可以减少容器的镜像大小，提高资源利用率，加快容器的启动速度。开发者可以将 Java 应用程序打包到基于 Alpine Linux 的容器中，实现更高效的部署和运行。

## JEP 387: 弹性元空间
元空间是 Java 虚拟机（JVM）中用于存储类元数据的区域。在传统的实现中，元空间的大小通常是固定的或者有一些不太灵活的调整机制。弹性元空间特性引入了一种更智能的元空间管理机制，它能够根据应用程序的运行时需求动态地调整元空间的大小。当应用程序加载的类增多，需要更多的元数据存储空间时，弹性元空间可以自动扩展；而当一些类被卸载，不再需要存储其元数据时，元空间又可以自动收缩。这种动态调整机制有助于优化内存使用，避免内存浪费，同时确保应用程序在处理大量类时不会因为元空间不足而出现问题。

## JEP 388: Windows/AArch64 移植
AArch64 是 ARM 架构的 64 位版本，在移动设备、嵌入式系统和一些服务器领域得到了广泛应用。将 JDK 移植到 Windows/AArch64 平台，使得 Java 应用程序能够在基于 ARM 架构的 Windows 设备上运行。这扩大了 Java 的应用范围，使得开发者可以利用 ARM 架构的优势，如低功耗、高性能等，来开发和部署 Java 应用程序。例如，在一些移动设备或低功耗服务器上运行 Java 服务，可以提供更好的能效比。

## JEP 389: 外部链接器 API（孵化器）
外部链接器 API 提供了一种在 Java 中与本地代码（如 C/C++ 编写的库）进行交互的机制。通过该 API，开发者可以在 Java 代码中直接调用本地函数，而无需使用传统的 Java Native Interface（JNI）。这简化了与本地代码的集成过程，减少了开发复杂度，并且提高了性能。例如，开发者可以使用外部链接器 API 来调用操作系统提供的底层 API，或者调用第三方的高性能 C/C++ 库，从而在 Java 应用程序中充分利用本地代码的优势。

```java
import jdk.incubator.foreign.*;
import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodType;

public class ForeignLinkerExample {
    public static void main(String[] args) throws Throwable {
        // 加载本地库
        LibraryLookup<CLinker> lib = LibraryLookup.ofDefault();
        // 获取本地函数符号
        SymbolLookup.Named printf = SymbolLookup.loaderLookup().lookup("printf").get();
        // 创建方法句柄
        MethodType type = MethodType.methodType(int.class, MemoryAddress.class, MemoryAddress.class);
        MethodHandle mh = CLinker.getInstance().downcallHandle(
                printf,
                type,
                FunctionDescriptor.of(CLinker.C_INT,
                        CLinker.C_POINTER,
                        CLinker.C_POINTER));

        // 准备参数
        try (ResourceScope scope = ResourceScope.newConfinedScope()) {
            MemorySegment format = MemorySegment.ofArray(new byte[]{(byte) 'H', (byte) 'e', (byte) 'l', (byte) 'l', (byte) 'o', (byte) '\0'}, scope);
            MemorySegment result = (MemorySegment) mh.invokeExact(
                    CLinker.toCString("Hello, %s\n", scope).address(),
                    format.address());
        }
    }
}
```

## JEP 390: 针对基于值的类的警告
基于值的类是指那些行为类似于值（如不可变、没有身份标识等）的类，例如 `Integer`、`String` 等。该特性引入了一种机制，当开发者以不恰当的方式使用基于值的类时，编译器会发出警告。例如，当对基于值的类进行不必要的同步操作时，编译器会提示这种操作可能是无效的，因为基于值的类的实例通常是不可变的，不需要同步。这些警告有助于开发者编写更正确、更高效的代码，避免一些常见的错误和性能问题。

## JEP 392: 打包工具
打包工具提供了一种简单的方式将 Java 应用程序及其依赖项打包成一个可分发的格式，如特定平台的安装包（如 Windows 的.msi 文件、macOS 的.pkg 文件等）或跨平台的容器镜像。这使得开发者能够更方便地将 Java 应用程序交付给最终用户，简化了应用程序的安装和部署过程。打包工具可以自动处理依赖关系，确保应用程序在目标环境中能够正确运行，并且可以根据不同的平台和需求进行定制化的打包配置。

## JEP 393: 外部内存访问 API（第三次孵化）
外部内存访问 API 允许 Java 应用程序直接访问堆外内存（即不由 JVM 管理的内存）。这在处理大规模数据或与本地代码交互时非常有用，例如在进行高性能的 I/O 操作、与硬件设备通信或处理大型数据集时。通过该 API，开发者可以更高效地在 Java 代码和本地内存之间传输数据，减少数据复制的开销，提高应用程序的性能。例如，在处理网络数据包或大型文件时，可以直接将数据读取到堆外内存，然后在 Java 代码中进行处理，避免了将数据从堆外复制到堆内的过程。

```java
import jdk.incubator.foreign.*;
import java.nio.ByteBuffer;

public class ForeignMemoryAccessExample {
    public static void main(String[] args) {
        try (ResourceScope scope = ResourceScope.newConfinedScope()) {
            // 分配堆外内存
            MemorySegment segment = MemorySegment.allocateNative(1024, scope);

            // 将数据写入堆外内存
            byte[] data = "Hello, Foreign Memory!".getBytes();
            segment.copyFrom(MemorySegment.ofArray(data));

            // 从堆外内存读取数据
            byte[] buffer = new byte[data.length];
            segment.copyTo(0, MemorySegment.ofArray(buffer));

            System.out.println(new String(buffer));
        }
    }
}
```

## JEP 394: instanceof 的模式匹配
该特性扩展了 `instanceof` 操作符的功能，允许在判断对象类型的同时，将对象转换为指定的类型并提取其成员。这使得代码更加简洁和易读，减少了不必要的类型转换代码。例如，在使用 `instanceof` 判断对象是否为某个类的实例后，可以直接在同一个表达式中访问该对象的成员，而无需先进行显式的类型转换。这在处理复杂对象结构或进行多态操作时非常有用，能够提高代码的可维护性和可读性。

```java
Object obj = "Hello";
if (obj instanceof String s) {
    System.out.println("The length of the string is: " + s.length());
}
```

## JEP 395: 记录类
记录类是一种简洁的方式来定义不可变的数据载体类。通过使用 `record` 关键字，开发者可以快速定义一个类，该类自动具有不可变性、自动生成的构造函数、访问器方法（getter）、`equals()`、`hashCode()` 和 `toString()` 方法等。记录类非常适合用于表示简单的数据结构，如配置对象、数据传输对象等。它减少了样板代码的编写，提高了代码的可读性和可维护性。例如，定义一个表示二维点的记录类：

```java
record Point(int x, int y) {}

public class RecordExample {
    public static void main(String[] args) {
        Point point = new Point(10, 20);
        System.out.println("Point: (" + point.x() + ", " + point.y() + ")");
        System.out.println("ToString: " + point);
    }
}
```

## JEP 396: 默认情况下强封装 JDK 内部元素
在早期的 Java 版本中，JDK 的一些内部 API 可以被外部代码访问，但这可能会导致代码的脆弱性和安全问题，因为这些内部 API 可能会在不通知开发者的情况下发生变化。该特性默认情况下强封装 JDK 内部元素，限制外部代码对 JDK 内部 API 的访问。这有助于提高 JDK 的安全性和稳定性，鼓励开发者使用标准的 Java API 来开发应用程序。如果确实需要访问某些内部 API，开发者可以通过特定的命令行选项来放宽封装限制，但这应该被视为一种临时解决方案，而不是推荐的做法。

## JEP 397: 密封类（第二次预览）
密封类是一种用于限制类或接口的继承层次的机制。通过使用 `sealed` 关键字声明一个类或接口，开发者可以明确指定哪些其他类或接口可以继承它。这有助于创建更可控的类层次结构，提高代码的安全性和可维护性。例如，在一个图形库中，可以使用密封类来定义不同类型的图形，并限制只有特定的子类可以继承基类，从而确保图形的行为符合预期。密封类在预览阶段，允许开发者在实际项目中进行试用和反馈，以便进一步完善该特性。

```java
sealed class Shape permits Circle, Rectangle {
    // 类的成员
}

final class Circle extends Shape {
    // 圆的实现
}

final class Rectangle extends Shape {
    // 矩形的实现
}

public class SealedClassExample {
    public static void main(String[] args) {
        Shape shape = new Circle();
        if (shape instanceof Circle c) {
            System.out.println("It's a circle with radius (if applicable)");
        } else if (shape instanceof Rectangle r) {
            System.out.println("It's a rectangle with length and width (if applicable)");
        }
    }
}
```

## Stream API 增强
### **1. `toList()`：简化流到列表的转换**
- 新增 `toList()` 方法，直接作为终端操作调用，代码更简洁：
  ```java
  List<String> result = Stream.of("a", "b", "c")
      .filter(s -> s.startsWith("a"))
      .toList(); // 返回不可变列表
  ```

- **关键特性**：
    - **不可变性**：返回的列表是 `Collections.unmodifiableList` 包装的，无法修改元素（增删改会抛出 `UnsupportedOperationException`）。
    - **性能优化**：内部通过数组直接构造列表，减少临时对象创建，性能优于 `Collectors.toList()`。
    - **与 `Collectors.toUnmodifiableList()` 对比**：  
      Java 10 引入的 `Collectors.toUnmodifiableList()` 也可生成不可变列表，但 `toList()` 更简洁，且性能更优。

- **适用场景**：  
  需要快速生成不可变列表的流操作，如过滤、映射后的结果收集。

### **2. `mapMulti()`：高效替代 `flatMap()` 的元素转换**
- `mapMulti()` 通过 `BiConsumer` 直接接收元素并推送零个或多个结果到下游，避免创建临时流：
  ```java
  List<String> result = Stream.of("a", "bb", "ccc")
      .mapMulti((s, consumer) -> consumer.accept(String.valueOf(s.length()))) // 直接推送结果
      .toList();
  ```

- **关键特性**：
    - **零开销**：无需创建内部流，减少内存分配和垃圾回收压力。
    - **灵活性**：可动态决定推送结果的数量（如过滤、复制元素）。
    - **与 `flatMap()` 对比**：  
      `flatMap()` 更声明式，适合明确映射逻辑；`mapMulti()` 更命令式，适合复杂或性能敏感场景。

- **适用场景**：  
  需要高效处理大量数据或动态生成结果的流操作，如日志解析、数据转换。