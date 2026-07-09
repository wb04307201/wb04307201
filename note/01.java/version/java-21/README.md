<!--
module:
  parent: java
  slug: java/java-21
  type: article
  category: 主模块子文章
  summary: Java 21 LTS 全景：15 个 JEP 深度解读 + JDK 17→21 迁移指南
-->

# Java 21

> Java 21 是 2023 年 9 月发布的 LTS 版本，15 个 JEP 覆盖虚拟线程、模式匹配、序列化集合等核心特性。

## 引言：变更说明

Java 21 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

- **JEP 430**: 字符串模板（预览）
- **JEP 431**: 有序集合
- **JEP 439**: 分代式 ZGC
- **JEP 440**: 记录模式
- **JEP 441**: switch 表达式中的模式匹配
- **JEP 442**: 外部函数与内存 API（第三次预览）
- **JEP 443**: 未命名模式和变量（预览）
- **JEP 444**: 虚拟线程
- **JEP 445**: 未命名类和实例主方法（预览）
- **JEP 446**: 作用域值（预览）
- **JEP 448**: 向量 API（第六次孵化）
- **JEP 449**: 弃用待移除的 Windows 32 位 x86 端口
- **JEP 451**: 准备禁止动态加载代理
- **JEP 452**: 密钥封装机制 API
- **JEP 453**: 结构化并发（预览）

## JEP 430: 字符串模板（预览）

字符串模板是一种新的字符串处理机制，它允许开发者在字符串中嵌入表达式，从而更方便地构建复杂的字符串。Java 使用 `STR` 字符串模板处理器，通过在字符串前加上 `STR.` 前缀，并在其中使用 `\{}` 来嵌入表达式。

**为什么重要**：字符串模板不只是语法糖——它通过模板处理器（`STR`/`FMT`/`RAW`）在编译期/运行期对嵌入表达式做校验和转换，从根本上杜绝 SQL 注入等拼接漏洞。

**Before（JDK 17：字符串拼接易出错且不安全）**：

```java
String name = "Alice";
int age = 25;

// 方式 1：+ 拼接 —— 可读性差，容易漏空格
String msg1 = "Hello, my name is " + name + " and I'm " + age + " years old.";

// 方式 2：String.format —— 类型不安全，%s/%d 容易写错
String msg2 = String.format("Hello, my name is %s and I'm %d years old.", name, age);

// 方式 3：SQL 拼接 —— 存在注入风险！
String sql = "SELECT * FROM users WHERE name = '" + name + "'"; // ⚠️ SQL 注入
```

**After（JDK 21：字符串模板）**：

```java
String name = "Alice";
int age = 25;

// STR 处理器：直接嵌入表达式，编译期类型检查
String msg = STR."Hello, my name is \{name} and I'm \{age} years old.";

// 支持嵌入任意表达式，不限于变量
String info = STR."2 + 3 = \{2 + 3}, upper name = \{name.toUpperCase()}";

// FMT 处理器：带格式化（类似 printf）
String formatted = FMT."Price: %8.2f\{price}";

// RAW 处理器：获取原始模板，可做安全校验
// 自定义处理器可实现 SQL 参数化，彻底杜绝注入
StringTemplate st = RAW."SELECT * FROM users WHERE name = \{name}";
// 自定义处理器解析 st，自动转为 PreparedStatement
```

> ⚠️ **注意**：字符串模板在 JDK 21 中仍是预览特性，需在编译和运行时加 `--enable-preview`。JDK 23 中已被移除并重新设计（JEP 465），后续版本请关注新 API。

## JEP 431: 有序集合

有序集合是一种新的集合类型，它维护了元素的插入顺序。Java 21 引入了 `SequencedCollection`、`SequencedSet` 和 `SequencedMap` 接口，为具有明确相遇顺序的集合提供了统一的 API。与现有的集合类型（如 `HashSet` 不保证顺序，`LinkedHashSet` 保证插入顺序但缺乏获取首尾元素的方法）不同，有序集合接口提供了 `getFirst()`、`getLast()`、`addFirst()`、`addLast()` 等方法。

有序集合适用于需要按照插入顺序处理元素的场景，例如缓存、队列等。通过使用有序集合，开发者可以更方便地管理元素的顺序，提高代码的可读性和可维护性。

**为什么重要**：Java 集合框架自 1998 年以来就缺少"有序"的统一抽象——`List`、`LinkedHashSet`、`LinkedHashMap` 各自维护顺序但 API 不统一。JEP 431 补上了这个 25 年的设计缺口。

**Before（JDK 17：获取首尾元素各写各的）**：

```java
// List —— 用 get(0) / get(size()-1)
List<String> list = new ArrayList<>(List.of("a", "b", "c"));
String first = list.get(0);              // "a"
String last  = list.get(list.size() - 1); // "c"

// LinkedHashSet —— 没有 getFirst/getLast，只能迭代
LinkedHashSet<String> set = new LinkedHashSet<>(List.of("a", "b", "c"));
String setFirst = set.iterator().next();  // "a"
String setLast  = set.stream().reduce((a, b) -> b).orElse(null); // 低效！

// Deque —— 有 getFirst/getLast，但它不是 Collection 统一体系的一部分
```

**After（JDK 21：统一 API）**：

```java
// 任何有序集合都用同一套 API
SequencedSet<String> set = new LinkedHashSet<>();
set.addFirst("a");
set.addLast("c");
set.addLast("b");

String first = set.getFirst();  // "a"
String last  = set.getLast();   // "b"
SequencedSet<String> reversed = set.reversed(); // ["b", "c", "a"] — 零拷贝反转视图

// SequencedMap 同样适用
SequencedMap<String, Integer> map = new LinkedHashMap<>();
map.putFirst("x", 1);
map.putLast("z", 3);
map.firstEntry();   // x=1
map.lastEntry();    // z=3
```

> 💡 **迁移提示**：如果你代码中有 `list.get(list.size() - 1)` 或 `set.iterator().next()` 获取末尾元素的写法，全部替换为 `getLast()` / `getFirst()`。

## JEP 439: 分代式 ZGC

分代式 ZGC 是一种改进的垃圾回收算法，它结合了分代收集和 ZGC 垃圾回收器的优点。分代收集将堆内存分为不同的代，例如年轻代和老年代，并针对不同代的特点采用不同的垃圾回收策略。ZGC 则是一种并发式垃圾回收器，旨在减少垃圾回收的停顿时间。

分代式 ZGC 通过将分代收集和 ZGC 结合，提高了垃圾回收的效率和性能。它可以更有效地回收年轻代中的短期对象，同时减少老年代垃圾回收的停顿时间，提高应用程序的响应速度。

## JEP 440: 记录模式

记录模式是一种新的模式匹配机制，它允许开发者在模式匹配中直接使用记录类的属性。记录类是一种不可变的数据载体类，它自动提供了属性的访问器方法和一些标准方法（如 `equals`、`hashCode` 和 `toString`）。

通过记录模式，开发者可以更方便地对记录类进行解构和匹配，提高代码的可读性和简洁性。

**为什么重要**：记录模式让 Java 拥有了真正的"解构"能力——嵌套 record 可以一层拆开，配合 switch 模式匹配，复杂数据结构的处理代码量可减少 50% 以上。

**Before（JDK 17：手动 getter 链）**：

```java
record Point(int x, int y) {}
record Line(Point start, Point end) {}

Line line = new Line(new Point(1, 2), new Point(3, 4));

// 手动逐层取值
int startX = line.start().x();
int endX   = line.end().x();
int length = Math.abs(endX - startX);
System.out.println("水平距离: " + length);
```

**After（JDK 21：嵌套记录模式一步解构）**：

```java
record Point(int x, int y) {}
record Line(Point start, Point end) {}

Line line = new Line(new Point(1, 2), new Point(3, 4));

// 嵌套解构：一步拆到最内层
if (line instanceof Line(Point(var sx, var sy), Point(var ex, var ey))) {
    int length = Math.abs(ex - sx);
    System.out.println("水平距离: " + length);
}

// 配合 switch 更强大：按数据结构分支
Object shape = line;
String desc = switch (shape) {
    case Point(var x, var y) when x == 0 && y == 0 -> "原点";
    case Point(var x, var y)                        -> "点(" + x + "," + y + ")";
    case Line(Point(var x1, _), Point(var x2, _))   -> "水平跨度: " + Math.abs(x2 - x1);
    default                                          -> "未知图形";
};
```

> ⚠️ **反模式**：不要对非 record 类使用记录模式——记录模式依赖 record 的规范构造函数（canonical constructor），普通类不支持解构。

## JEP 441: switch 表达式中的模式匹配

该特性扩展了 `switch` 表达式的功能，允许在 `switch` 表达式中使用模式匹配。这使得代码更加简洁和易读，减少了不必要的类型转换和条件判断。

**为什么重要**：switch 模式匹配消除了 Java 中最常见的 `if-else instanceof` 反模式，让类型分发像函数式语言一样简洁且编译器可检查穷举性。

**Before（JDK 17：if-else instanceof 链）**：

```java
static String formatValue(Object obj) {
    if (obj instanceof String s) {
        return "字符串: " + s;
    } else if (obj instanceof Integer i) {
        return "整数: " + i;
    } else if (obj instanceof Long l) {
        return "长整数: " + l;
    } else if (obj == null) {
        return "空值";  // 容易漏判 null
    } else {
        return "未知类型";
    }
}
```

**After（JDK 21：switch 模式匹配 + null 安全）**：

```java
static String formatValue(Object obj) {
    return switch (obj) {
        case String s   -> "字符串: " + s;
        case Integer i  -> "整数: " + i;
        case Long l     -> "长整数: " + l;
        case null       -> "空值";       // null 安全，不会 NPE
        default         -> "未知类型";
    };
}
// 编译器会检查 sealed 接口的所有 permitted 子类型是否穷举
```

> 💡 **最佳实践**：对 `sealed` 类型使用 switch 模式匹配时，编译器可以验证穷举性，漏掉一个子类就会报编译错误——这在 Visitor 模式中极其有用。

## JEP 442: 外部函数与内存 API（第三次预览）

外部函数与内存 API 提供了一种更安全、更高效的方式来调用本地代码和访问本地内存。它允许 Java 代码与本地库进行交互，扩展了 Java 的功能和应用场景。

该特性通过引入新的类和接口，提供了对本地函数调用和内存访问的封装，减少了使用 JNI（Java Native Interface）的复杂性和风险。

```java
// 调用本地函数示例
import java.lang.foreign.*;
import java.lang.invoke.*;

public class ForeignFunctionExample {
    public static void main(String[] args) throws Throwable {
        try (Arena arena = Arena.ofAuto()) {
            Linker linker = Linker.nativeLinker();
            MemorySegment strlenAddr = linker.defaultLookup().find("strlen").get();
            FunctionDescriptor fd = FunctionDescriptor.of(ValueLayout.JAVA_LONG, ValueLayout.ADDRESS);
            MethodHandle strlen = linker.downcallHandle(strlenAddr, fd);
            MemorySegment str = arena.allocateUtf8String("Hello");
            long len = (long) strlen.invoke(str);
            System.out.println("Length: " + len);
        }
    }
}
```

## JEP 443: 未命名模式和变量（预览）

未命名模式和变量是一种简化模式匹配代码的机制。它允许开发者在模式匹配中使用未命名的模式和变量，从而减少代码的冗余。

例如，在使用 `instanceof` 进行模式匹配时，如果不需要使用匹配到的变量，可以使用未命名模式：

```java
Object obj = "Hello";
if (obj instanceof String _) {
    System.out.println("It's a string");
}
```

## JEP 444: 虚拟线程

虚拟线程是一种轻量级的线程实现，它旨在简化高并发编程。与传统的操作系统线程不同，虚拟线程由 JVM 管理，而不是由操作系统调度。这使得虚拟线程的创建和销毁成本非常低，可以支持大量的并发线程。

虚拟线程适用于高并发的网络服务器、异步编程等场景。通过使用虚拟线程，开发者可以更方便地编写高并发的代码，提高应用程序的性能和响应速度。

**为什么重要**：虚拟线程彻底改变了 Java 并发编程模型——用同步写法获得异步性能，无需再依赖 Reactive 框架（如 RxJava、WebFlux）即可支撑百万级并发连接。

**Before（JDK 17：平台线程池，线程数受限）**：

```java
// 平台线程：每个线程约 1MB 栈空间，1000 线程 ≈ 1GB 内存
ExecutorService executor = Executors.newFixedThreadPool(200);
List<Future<String>> futures = new ArrayList<>();
for (int i = 0; i < 10_000; i++) {
    futures.add(executor.submit(() -> {
        // 阻塞 I/O 时线程被占用却无法做其他工作
        return callRemoteService();
    }));
}
// 10000 个任务排队等 200 个线程 → 大量时间浪费在排队上
```

**After（JDK 21：虚拟线程，每个任务一个线程）**：

```java
// 虚拟线程：每个仅 ~几KB，百万级也不是问题
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> {
        executor.submit(() -> {
            // 阻塞 I/O 时虚拟线程自动 unmount，carrier 线程去执行其他任务
            return callRemoteService();
        });
    });
}
// 10000 个任务同时执行，写法依然是同步阻塞风格，无需 CompletableFuture
```

> ⚠️ **反模式**：不要对虚拟线程使用 `synchronized` 块做 I/O 操作——它会 pin 住 carrier 线程。应改用 `ReentrantLock`。

## JEP 445: 未命名类和实例主方法（预览）

该特性进一步简化了 Java 源代码的结构，允许开发者编写更简洁的代码。它支持未命名类，即类可以没有显式的名称，并且提供了更简单的实例主方法声明方式。

```java
// 未命名类和实例主方法示例
void main() {
    System.out.println("Hello, World!");
}
```

## JEP 446: 作用域值（预览）

作用域值是一种在特定作用域内共享不可变数据的机制。它类似于线程局部变量，但更适用于虚拟线程和结构化并发等新的编程模型。

作用域值允许在大型程序中的组件之间安全有效地共享数据，而无需求助于方法参数。这对于减少代码冗余和提高代码的可维护性非常有帮助。

```java
final static ScopedValue<String> USER_NAME = ScopedValue.newInstance();

// 设置作用域值
ScopedValue.where(USER_NAME, "Alice")
           .run(() -> {
               // 在这个作用域内可以访问 USER_NAME
               System.out.println("Hello, " + USER_NAME.get());
           });
```

## JEP 448: 向量 API（第六次孵化）

向量 API 提供了一种高效的方式来进行向量计算，适用于科学计算、机器学习等领域。该特性通过引入一组新的类和接口，允许开发者使用硬件加速的向量指令来执行计算，从而提高性能。

```java
import jdk.incubator.vector.*;

// 创建向量种类（指定使用 256 位 SIMD 寄存器）
VectorSpecies<Integer> SPECIES = IntVector.SPECIES_256;

// 创建两个向量
IntVector vector1 = IntVector.fromArray(SPECIES, new int[]{1, 2, 3, 4}, 0);
IntVector vector2 = IntVector.fromArray(SPECIES, new int[]{5, 6, 7, 8}, 0);

// 执行向量加法
IntVector result = vector1.add(vector2);

// 将结果存储到数组中
int[] output = new int[4];
result.intoArray(output, 0);

// 输出结果
System.out.println(java.util.Arrays.toString(output)); // [6, 8, 10, 12]
```

## JEP 449: 弃用待移除的 Windows 32 位 x86 端口

随着计算机硬件的发展，64 位架构已经成为主流。为了简化 JDK 的开发和维护，该特性决定弃用并最终移除对 Windows 32 位 x86 架构的支持。这意味着未来的 JDK 版本将不再提供适用于 Windows 32 位 x86 处理器的版本。

这一变化将使 JDK 能够更专注于 64 位架构的优化和功能开发，提高性能和安全性。同时，也符合行业趋势，因为大多数现代计算机都已经采用 64 位操作系统和处理器。

## JEP 451: 准备禁止动态加载代理

动态加载代理是一种在运行时动态生成代理类的技术，它常用于 AOP（面向切面编程）等场景。然而，动态加载代理也存在一些安全风险和性能问题。

该特性准备禁止动态加载代理，以提高 Java 应用程序的安全性和性能。通过禁止动态加载代理，可以减少潜在的安全漏洞，并优化 JVM 的性能。

## JEP 452: 密钥封装机制 API

密钥封装机制 API 提供了一种标准化的方式来封装和解封密钥。密钥封装是一种加密技术，它允许将一个密钥（称为封装密钥）用于加密另一个密钥（称为被封装密钥），从而实现对被封装密钥的安全存储和传输。

```java
// 创建一个 KEM 对象，使用 ECIES 算法
KEM kem = KEM.getInstance("ECIES");

// 生成封装密钥和被封装密钥
KeyPair encapsulationKeyPair = kem.generateKeyPair();
byte[] encapsulatedKey = kem.encapsulate(encapsulationKeyPair.getPublic());
SecretKey unwrappedKey = kem.decapsulate(encapsulatedKey, encapsulationKeyPair.getPrivate());
```

## JEP 453: 结构化并发（预览）

结构化并发是一种多线程编程方法，旨在简化多线程代码的管理和错误处理。它将不同线程中运行的多个任务视为单个工作单元，从而提高了代码的可读性、可维护性和可靠性。

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

## JDK 17 → 21 迁移对比表

| 维度 | JDK 17 | JDK 21 | 迁移建议 |
|------|--------|--------|----------|
| **并发模型** | 平台线程池（`newFixedThreadPool`） | 虚拟线程（`newVirtualThreadPerTaskExecutor`） | I/O 密集型服务直接切换，CPU 密集型保持平台线程 |
| **类型分发** | `if-else instanceof` 链 | `switch` 模式匹配 | 全量替换，sealed 类可获编译期穷举检查 |
| **集合首尾操作** | `list.get(0)` / `list.get(size()-1)` / 迭代器 | `getFirst()` / `getLast()` / `reversed()` | 机械替换，无风险 |
| **数据解构** | 手动 getter 链 `obj.field().sub()` | 记录模式 `Point(var x, var y)` | record 类优先使用，非 record 类不受影响 |
| **字符串构建** | `+` 拼接 / `String.format` | 字符串模板 `STR."..."`（预览） | 暂观望，JDK 23 已重新设计，等稳定版 |
| **GC 选择** | G1（默认）/ ZGC | G1（默认）/ 分代 ZGC | 低延迟场景加 `-XX:+UseZGC -XX:+ZGenerational` |
| **本地调用** | JNI（复杂且不安全） | 外部函数与内存 API（第三次预览） | 新项目可尝试，老项目 JNI 暂不动 |
| **并发编排** | `CompletableFuture` / 手写线程管理 | 结构化并发（预览） | 适合新模块，老代码暂不迁移 |
| **平台支持** | Windows x86 32-bit 仍可用 | Windows x86 32-bit 已弃用 | 确认部署环境无 32 位依赖 |

### 迁移优先级建议

```
┌─────────────────────────────────────────────────┐
│  立即迁移（LTS → LTS 本身就是理由）              │
│  ├── 虚拟线程 —— I/O 密集型服务性能飞跃          │
│  ├── switch 模式匹配 —— 代码量减少 + 编译期安全   │
│  └── 有序集合 API —— 零风险机械替换               │
├─────────────────────────────────────────────────┤
│  推荐采用                                        │
│  ├── 记录模式 —— record 类的项目直接受益          │
│  └── 分代 ZGC —— 延迟敏感型应用                  │
├─────────────────────────────────────────────────┤
│  观望（预览特性，API 可能变）                     │
│  ├── 字符串模板 —— JDK 23 已重新设计              │
│  ├── 结构化并发 —— 等正式化                       │
│  └── 外部函数 API —— 等正式化                     │
└─────────────────────────────────────────────────┘
```

---

← [返回: Java 版本演进](../README.md)