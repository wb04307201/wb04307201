# Java 22

- **JEP 423**: G1 的区域固定
- **JEP 447**: 在 `super(...)` 调用前的语句（预览）
- **JEP 454**: 外部函数与内存 API
- **JEP 456**: 无名变量与模式
- **JEP 457**: 类文件 API（预览）
- **JEP 458**: 启动多文件源代码程序
- **JEP 459**: 字符串模板（第二次预览）
- **JEP 460**: 向量 API（第七次孵化）
- **JEP 461**: 流收集器（预览）
- **JEP 462**: 结构化并发（第二次预览）
- **JEP 463**: 隐式声明类和实例主方法（第二次预览）
- **JEP 464**: 作用域值（第二次预览）

## JEP 423: G1 的区域固定

在垃圾回收过程中，G1（Garbage-First）垃圾收集器有时需要将对象从一个区域移动到另一个区域。然而，在某些情况下，我们希望特定区域中的对象保持原地不动，例如，当这些对象正被本地代码访问时。该特性引入了区域固定机制，允许在垃圾回收期间防止特定区域被回收或压缩，从而确保本地代码可以安全地访问这些区域中的对象，而无需担心对象被移动。

## JEP 447: 在 `super(...)` 调用前的语句（预览）

在 Java 中，构造函数的第一条语句通常是调用父类的构造函数（`super(...)`）。然而，在某些情况下，我们希望在调用父类构造函数之前执行一些操作，例如验证参数或初始化某些字段。该特性允许在调用 `super(...)` 之前包含语句，从而提供了更大的灵活性。这些语句在子类构造函数体执行之前、父类构造函数调用之后立即执行（从逻辑顺序角度，代码写在 `super` 调用前，但实际执行是在 `super` 调用之后、子类构造函数体之前 ），并且可以访问子类的字段（但此时子类对象还未完全初始化，需谨慎使用）。

```java
class Parent {
    Parent(int value) {
        System.out.println("Parent constructor with value: " + value);
    }
}

class Child extends Parent {
    private final int x;

    Child(int x) {
        int validatedX = validateX(x); // 在 super 调用前的语句
        super(validatedX);
        this.x = x;
    }

    private int validateX(int x) {
        if (x < 0) {
            throw new IllegalArgumentException("x must be non-negative");
        }
        return x;
    }
}
```

## JEP 454: 外部函数与内存 API

外部函数与内存 API 提供了一种更安全、更高效的方式来调用本地代码（例如 C/C++ 库）和操作本地内存。它引入了新的类和接口，允许 Java 代码声明与本地代码的交互方式，并提供了对本地内存的精细控制。这使得 Java 应用程序可以更好地与现有的本地库集成，同时减少了使用 JNI（Java Native Interface）带来的复杂性和安全风险。

```java
import jdk.incubator.foreign.*;

public class NativeExample {
    public static void main(String[] args) {
        // 加载本地库
        MemorySegment lib = MemorySegment.loadNative("mylib");

        // 声明本地函数
        FunctionDescriptor funcDesc = FunctionDescriptor.ofVoid(
            MemoryLayout.ofValueBits(32, MemoryLayout.PathElement.groupElement().withName("x"), ByteOrder.nativeOrder())
        );
        MemoryAccess.setInt(lib.asSlice(0), 42);
        MethodHandle funcHandle = CLinker.getInstance().downcallHandle(
            lib.baseAddress(),
            funcDesc,
            FunctionDescriptor.ofVoid()
        );

        // 调用本地函数
        try {
            funcHandle.invokeExact();
        } catch (Throwable e) {
            e.printStackTrace();
        }
    }
}
```

## JEP 456: 无名变量与模式

无名变量与模式允许在模式匹配中使用没有显式名称的变量。这在某些情况下可以使代码更加简洁，特别是当我们只关心模式匹配的结果而不关心变量的具体名称时。例如，在使用 `instanceof` 模式匹配时，如果我们不需要访问匹配的对象，可以使用无名变量来避免不必要的变量声明。

```java
Object obj = "Hello";
if (obj instanceof String _) { // 使用无名变量
    System.out.println("It's a string");
}
```

## JEP 457: 类文件 API（预览）

类文件 API 提供了一种编程方式来读取、生成和转换 Java 类文件。它允许开发者在运行时或编译时分析类文件的结构，提取类、方法、字段等信息，并且可以生成新的类文件或修改现有的类文件。这对于构建代码分析工具、字节码操作库和编译器插件等非常有用。

```java
import jdk.incubator.classfile.*;

public class ClassFileExample {
    public static void main(String[] args) throws Exception {
        // 创建一个简单的类文件
        ClassFile classFile = new ClassFile("com.example.MyClass", "java.lang.Object");
        MethodInfo methodInfo = new MethodInfo("myMethod", "()V", ClassFile.ACC_PUBLIC);
        methodInfo.addInstruction(Instruction.opReturn());
        classFile.addMethod(methodInfo);

        // 将类文件写入磁盘
        try (var out = Files.newOutputStream(Path.of("MyClass.class"))) {
            classFile.writeTo(out);
        }
    }
}
```

## JEP 458: 启动多文件源代码程序

通常情况下，Java 程序需要先编译成类文件，然后再运行。然而，对于一些简单的脚本或小型程序，这种编译过程可能会显得繁琐。该特性允许直接运行包含多个 Java 源代码文件的程序，而无需事先编译。Java 解释器会自动编译并运行这些源代码文件，使得开发和测试小型程序更加方便快捷。

假设我们有两个 Java 源代码文件 `Main.java` 和 `Helper.java`：

`Main.java`:
```java
public class Main {
    public static void main(String[] args) {
        Helper helper = new Helper();
        helper.sayHello();
    }
}
```

`Helper.java`:
```java
public class Helper {
    public void sayHello() {
        System.out.println("Hello from Helper!");
    }
}
```

我们可以直接使用以下命令运行程序：
```bash
java Main.java Helper.java
```

## JEP 459: 字符串模板（第二次预览）

字符串模板提供了一种更灵活、更易读的方式来构建字符串。它允许在字符串中嵌入表达式，这些表达式将在运行时进行求值，并将结果插入到字符串中。与传统的字符串拼接方式相比，字符串模板更加简洁明了，减少了代码的冗余和错误的可能性。

```java
String name = "Alice";
int age = 30;
String message = STR."Hello, \{name}! You are \{age} years old."; // 使用字符串模板
System.out.println(message);
```

## JEP 460: 向量 API（第七次孵化）

向量 API 提供了一种高效的方式来进行向量计算，适用于科学计算、机器学习等领域。该特性通过引入一组新的类和接口，允许开发者使用硬件加速的向量指令来执行计算，从而提高性能。与之前的孵化版本相比，该版本可能进一步优化了 API 的设计和性能，提供了更多的向量操作和功能。

```java
// 创建两个向量
IntVector vector1 = IntVector.fromArray(VectorSpecies.ofDefault(int.class), new int[]{1, 2, 3, 4}, 0);
IntVector vector2 = IntVector.fromArray(VectorSpecies.ofDefault(int.class), new int[]{5, 6, 7, 8}, 0);

// 执行向量加法
IntVector result = vector1.add(vector2);

// 将结果存储到数组中
int[] output = new int[4];
result.intoArray(output, 0);

// 输出结果
System.out.println(Arrays.toString(output)); // [6, 8, 10, 12]
```

## JEP 461: 流收集器（预览）

流收集器是 Java 流 API 的一个扩展，它提供了一种更灵活、更强大的方式来收集流中的元素。传统的流收集器（如 `Collectors.toList()`、`Collectors.toSet()` 等）提供了一些基本的收集功能，但有时可能无法满足复杂的需求。该特性引入了新的收集器接口和实现，允许开发者自定义收集逻辑，实现更复杂的收集操作，例如分组、聚合、转换等。

```java
import java.util.*;
import java.util.stream.*;
import java.util.function.*;

public class StreamGatherersExample {
    public static void main(String[] args) {
        List<String> words = Arrays.asList("apple", "banana", "cherry", "date", "elderberry");

        // 使用自定义收集器将单词按长度分组，并统计每组的单词数量
        Map<Integer, Long> wordCountByLength = words.stream()
           .collect(Collectors.groupingBy(
                String::length,
                Collectors.counting()
            ));

        System.out.println(wordCountByLength);
    }
}
```

## JEP 462: 结构化并发（第二次预览）

结构化并发是一种多线程编程方法，旨在简化多线程代码的管理和错误处理。它将不同线程中运行的多个任务视为单个工作单元，从而提高了代码的可读性、可维护性和可靠性。与第一次预览版本相比，该版本可能进一步完善了 API 的设计和功能，解决了之前版本中发现的问题。

该特性引入了 `StructuredTaskScope` 类，允许开发者将任务拆分为多个并发子任务，并在它们自己的线程中执行。子任务必须在主任务继续之前完成，这使得错误处理更加简单，因为异常可以在一个地方捕获和处理。

```java
try (var scope = new StructuredTaskScope<Object>()) {
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

## JEP 463: 隐式声明类和实例主方法（第二次预览）

该特性进一步简化了 Java 源代码的结构，允许开发者编写更简洁的代码。它支持隐式声明类，即未命名的类可以省略类名，并且提供了更简单的实例主方法声明方式。与第一次预览版本相比，该版本可能根据用户反馈进行了改进和优化，提高了特性的易用性和稳定性。

```java
// 隐式声明类和实例主方法示例
void main() {
    System.out.println("Hello, World!");
}
```

## JEP 464: 作用域值（第二次预览）

作用域值是一种在特定作用域内共享不可变数据的机制。它类似于线程局部变量，但更适用于虚拟线程和结构化并发等新的编程模型。与第一次预览版本相比，该版本可能进一步完善了作用域值的实现，提高了其性能和可靠性，并且可能增加了更多的使用场景和功能。

作用域值允许在大型程序中的组件之间安全有效地共享数据，而无需求助于方法参数。这对于减少代码冗余和提高代码的可维护性非常有帮助。

```java
final static ScopedValue<String> USER_NAME = new ScopedValue<>();

// 设置作用域值
ScopedValue.where(USER_NAME, "Alice")
           .run(() -> {
               // 在这个作用域内可以访问 USER_NAME
               System.out.println("Hello, " + USER_NAME.get());
           });
```