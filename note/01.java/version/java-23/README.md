# Java 23

- JEP 455:模式中的原始类型、instanceof和switch(预览)
- JEP 456:类文件API(第二次预览)
- JEP 467:Markdown文档注释
- JEP 469:向量API(第八次孵化)
- JEP 473:流收集器(第二次预览)
- JEP 471:弃用sun.misc.Unsafe中的内存访问方法
- JEP 474:ZGC:默认的分代模式
- JEP 476:模块导入声明(预览)
- JEP 477:未命名类和实例main方法(第三次预览)
- JEP 480:结构化并发(第三次预览)
- JEP 481:作用域值(第三次预览)
- JEP 482:灵活的构造函数体(第二次预览)

---

## JEP 455:模式中的原始类型、instanceof和switch(预览)

在 JEP 455 之前， `instanceof`只支持引用类型，`switch`表达式和语句的`case`标签只能使用整数字面量、枚举常量和字符串字面量。

JEP 455 的预览特性中，`instanceof`和`switch`全面支持所有原始类型，包括`byte`,`short`,`char`,`int`,`long`,`float`,`double`,`boolean`。
```java
// 传统写法
if (i >= -128 && i <= 127) {
    byte b = (byte)i;
    ... b ...
}

// 使用 instanceof 改进
if (i instanceof byte b) {
    ... b ...
}

long v = ...;
// 传统写法
if (v == 1L) {
    // ...
} else if (v == 2L) {
    // ...
} else if (v == 10_000_000_000L) {
    // ...
}

// 使用 long 类型的 case 标签
switch (v) {
    case 1L:
        // ...
        break;
    case 2L:
        // ...
        break;
    case 10_000_000_000L:
        // ...
        break;
    default:
        // ...
}
```

## JEP 456:类文件API(第二次预览)

类文件 API 在 Java 22 进行了第一次预览，由 JEP 457 提出。

类文件 API 的目标是提供一套标准化的 API，用于解析、生成和转换 Java 类文件，取代过去对第三方库（如 ASM）在类文件处理上的依赖。
```java
// 创建一个 ClassFile 对象，这是操作类文件的入口。
ClassFile cf = ClassFile.of();
// 解析字节数组为 ClassModel
ClassModel classModel = cf.parse(bytes);

// 构建新的类文件，移除以 "debug" 开头的所有方法
byte[] newBytes = cf.build(classModel.thisClass().asSymbol(),
        classBuilder -> {
            // 遍历所有类元素
            for (ClassElement ce : classModel) {
                // 判断是否为方法 且 方法名以 "debug" 开头
                if (!(ce instanceof MethodModel mm
                        && mm.methodName().stringValue().startsWith("debug"))) {
                    // 添加到新的类文件中
                    classBuilder.with(ce);
                }
            }
        });
```

## JEP 467:Markdown文档注释

在 JavaDoc 文档注释中可以使用 Markdown 语法，取代原本只能使用 HTML 和 JavaDoc 标签的方式。

Markdown 更简洁易读，减少了手动编写 HTML 的繁琐，同时保留了对 HTML 元素和 JavaDoc 标签的支持。这个增强旨在让 API 文档注释的编写和阅读变得更加轻松，同时不会影响现有注释的解释。Markdown 提供了对常见文档元素（如段落、列表、链接等）的简化表达方式，提升了文档注释的可维护性和开发者体验。

Markdown 文档注释  
![img.png](img.png)

## JEP 469:向量API(第八次孵化)

JEP 469：向量 API（第八次孵化）向量计算由对向量的一系列操作组成。向量 API 用来表达向量计算，该计算可以在运行时可靠地编译为支持的 CPU 架构上的最佳向量指令，从而实现优于等效标量计算的性能。

向量 API 的目标是为用户提供简洁易用且与平台无关的表达范围广泛的向量计算。

这是对数组元素的简单标量计算：
```java
void scalarComputation(float[] a, float[] b, float[] c) {
   for (int i = 0; i < a.length; i++) {
        c[i] = (a[i] * a[i] + b[i] * b[i]) * -1.0f;
   }
}
```
这是使用 Vector API 进行的等效向量计算：
```java
static final VectorSpecies<Float> SPECIES = FloatVector.SPECIES_PREFERRED;

void vectorComputation(float[] a, float[] b, float[] c) {
    int i = 0;
    int upperBound = SPECIES.loopBound(a.length);
    for (; i < upperBound; i += SPECIES.length()) {
        // FloatVector va, vb, vc;
        var va = FloatVector.fromArray(SPECIES, a, i);
        var vb = FloatVector.fromArray(SPECIES, b, i);
        var vc = va.mul(va)
                   .add(vb.mul(vb))
                   .neg();
        vc.intoArray(c, i);
    }
    for (; i < a.length; i++) {
        c[i] = (a[i] * a[i] + b[i] * b[i]) * -1.0f;
    }
}
```

## JEP 473:流收集器(第二次预览)

流收集器在 Java 22 进行了第一次预览，由 JEP 461 提出。

这个改进使得 Stream API 可以支持自定义中间操作。
```java
source.gather(a).gather(b).gather(c).collect(...)
```

## JEP 471:弃用sun.misc.Unsafe中的内存访问方法

JEP 471 提议弃用`sun.misc.Unsafe`中的内存访问方法，这些方法将来的版本中会被移除。

这些不安全的方法已有安全高效的替代方案：
- `java.lang.invoke.VarHandle`：JDK 9 (JEP 193) 中引入，提供了一种安全有效地操作堆内存的方法，包括对象的字段、类的静态字段以及数组元素。
- `java.lang.foreign.MemorySegment`：JDK 22 (JEP 454) 中引入，提供了一种安全有效地访问堆外内存的方法，有时会与`VarHandle`协同工作。

这两个类是 Foreign Function & Memory API 的核心组件，分别用于管理和操作堆外内存。

Foreign Function & Memory API 在 Java 22 中正式转正，成为标准特性。
```java
import jdk.incubator.foreign.*;
import java.lang.invoke.VarHandle;

// 管理堆外整数数组的类
class OffHeapIntBuffer {

// 用于访问整数元素的VarHandle
    private static final VarHandle ELEM_VH = ValueLayout.JAVA_INT.arrayElementVarHandle();

// 内存管理器
    private final Arena arena;

// 堆外内存段
    private final MemorySegment buffer;

// 构造函数，分配指定数量的整数空间
    public OffHeapIntBuffer(long size) {
        this.arena  = Arena.ofShared();
        this.buffer = arena.allocate(ValueLayout.JAVA_INT, size);
    }

// 释放内存
    public void deallocate() {
        arena.close();
    }

// 以volatile方式设置指定索引的值
    public void setVolatile(long index, int value) {
        ELEM_VH.setVolatile(buffer, 0L, index, value);
    }

// 初始化指定范围的元素为0
    public void initialize(long start, long n) {
        buffer.asSlice(ValueLayout.JAVA_INT.byteSize() * start,
                       ValueLayout.JAVA_INT.byteSize() * n)
              .fill((byte) 0);
    }

// 将指定范围的元素复制到新数组
    public int[] copyToNewArray(long start, int n) {
        return buffer.asSlice(ValueLayout.JAVA_INT.byteSize() * start,
                              ValueLayout.JAVA_INT.byteSize() * n)
                     .toArray(ValueLayout.JAVA_INT);
    }
}
```

## JEP 474:ZGC:默认的分代模式

Z 垃圾回收器 (ZGC) 的默认模式切换为分代模式，并弃用非分代模式，计划在未来版本中移除。这是因为分代 ZGC 是大多数场景下的更优选择。

## JEP 476:模块导入声明(预览)

模块导入声明允许在 Java 代码中简洁地导入整个模块的所有导出包，而无需逐个声明包的导入。这一特性简化了模块化库的重用，特别是在使用多个模块时，避免了大量的包导入声明，使得开发者可以更方便地访问第三方库和 Java 基本类。

此特性对初学者和原型开发尤为有用，因为它无需开发者将自己的代码模块化，同时保留了对传统导入方式的兼容性，提升了开发效率和代码可读性。
```java
// 导入整个 java.base 模块，开发者可以直接访问 List、Map、Stream 等类，而无需每次手动导入相关包
import module java.base;

public class Example {
    public static void main(String[] args) {
        String[] fruits = { "apple", "berry", "citrus" };
        Map<String, String> fruitMap = Stream.of(fruits)
            .collect(Collectors.toMap(
                s -> s.toUpperCase().substring(0, 1),
                Function.identity()));

System.out.println(fruitMap);
    }
}
```

## JEP 477:未命名类和实例main方法(第三次预览)

这个特性主要简化了`main`方法的的声明。对于 Java 初学者来说，这个`main`方法的声明引入了太多的 Java 语法概念，不利于初学者快速上手。

没有使用该特性之前定义一个`main`方法：
```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```
使用该新特性之后定义一个`main`方法：
```java
class HelloWorld {
    void main() {
        System.out.println("Hello, World!");
    }
}
```
进一步简化（未命名的类允许我们省略类名）
```java
void main() {
   System.out.println("Hello, World!");
}
```

## JEP 480:结构化并发(第三次预览)

Java 19 引入了结构化并发，一种多线程编程方法，目的是为了通过结构化并发 API 来简化多线程编程，并不是为了取代`java.util.concurrent`，目前处于孵化器阶段。

结构化并发将不同线程中运行的多个任务视为单个工作单元，从而简化错误处理、提高可靠性并增强可观察性。也就是说，结构化并发保留了单线程代码的可读性、可维护性和可观察性。

结构化并发的基本 API 是`StructuredTaskScope`。`StructuredTaskScope`支持将任务拆分为多个并发子任务，在它们自己的线程中执行，并且子任务必须在主任务继续之前完成。

`StructuredTaskScope`的基本用法如下：
```java
try (var scope = new StructuredTaskScope<Object>()) {
    // 使用fork方法派生线程来执行子任务
    Future<Integer> future1 = scope.fork(task1);
    Future<String> future2 = scope.fork(task2);
    // 等待线程完成
    scope.join();
    // 结果的处理可能包括处理或重新抛出异常
    ... process results/exceptions ...
} // close
```
结构化并发非常适合虚拟线程，虚拟线程是 JDK 实现的轻量级线程。许多虚拟线程共享同一个操作系统线程，从而允许非常多的虚拟线程。

## JEP 481:作用域值(第三次预览)

作用域值（Scoped Values）可以在线程内和线程间共享不可变的数据，优于线程局部变量，尤其是在使用大量虚拟线程时。
```java
final static ScopedValue<...> V = new ScopedValue<>();

// In some method
ScopedValue.where(V, <value>)
           .run(() -> { ... V.get() ... call methods ... });

// In a method called directly or indirectly from the lambda expression
... V.get() ...
```
作用域值允许在大型程序中的组件之间安全有效地共享数据，而无需求助于方法参数。

## JEP 482:灵活的构造函数体(第二次预览)

在 JEP 482 之前，Java 要求在构造函数中，`super(...)`或`this(...)`调用必须作为第一条语句出现。这意味着我们无法在调用父类构造函数之前在子类构造函数中直接初始化字段。

灵活的构造函数体解决了这一问题，它允许在构造函数体内，在调用`super(..)`或`this(..)`之前编写语句，这些语句可以初始化字段，但不能引用正在构造的实例。这样可以防止在父类构造函数中调用子类方法时，子类的字段未被正确初始化，增强了类构造的可靠性。

这一特性解决了之前 Java 语法限制了构造函数代码组织的问题，让开发者能够更自由、更自然地表达构造函数的行为，例如在构造函数中直接进行参数验证、准备和共享，而无需依赖辅助方法或构造函数，提高了代码的可读性和可维护性。
```java
class Person {
    private final String name;
    private int age;

public Person(String name, int age) {
        if (age < 0) {
            throw new IllegalArgumentException("Age cannot be negative.");
        }
        this.name = name; // 在调用父类构造函数之前初始化字段
        this.age = age;
        // ... 其他初始化代码
    }
}

class Employee extends Person {
    private final int employeeId;

public Employee(String name, int age, int employeeId) {
        this.employeeId = employeeId; // 在调用父类构造函数之前初始化字段
        super(name, age); // 调用父类构造函数
        // ... 其他初始化代码
    }
}
```