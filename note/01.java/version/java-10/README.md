# Java 10

- **JEP 286**: 局部变量类型推断
- **JEP 296**: 整合 JDK 代码库到单一存储库
- **JEP 304**: 垃圾回收器接口
- **JEP 307**: G1 的并行全垃圾回收
- **JEP 310**: 应用程序类数据共享
- **JEP 312**: 线程局部握手
- **JEP 313**: 移除本地头生成工具（javah）
- **JEP 314**: 额外的 Unicode 语言标签扩展
- **JEP 316**: 替代内存设备上的堆分配
- **JEP 317**: 基于 Java 的 JIT 编译器（实验性）
- **JEP 319**: 根证书
- **JEP 322**: 基于时间的版本发布
- **Stream API 增强**


## JEP 286: 局部变量类型推断

局部变量类型推断是 Java 10 引入的一个重要特性，它允许开发者在声明局部变量时省略显式的类型声明，而是使用 `var` 关键字来让编译器自动推断变量的类型。这一特性旨在减少代码冗余，提高代码的可读性和编写效率。

```java
// 传统方式声明变量
String message = "Hello, World!";
List<String> list = new ArrayList<>();

// 使用局部变量类型推断
var message = "Hello, World!";
var list = new ArrayList<String>();
```

## JEP 296: 整合 JDK 代码库到单一存储库

在 Java 10 之前，JDK 的代码库分散在多个 Mercural 存储库中，这给代码管理和协作带来了一定的复杂性。JEP 296 旨在将所有 JDK 的代码库整合到一个单一的存储库中，以简化开发流程，提高协作效率。

整合后的单一存储库结构更清晰，便于开发者浏览和修改代码，同时也减少了因多个存储库之间同步问题而导致的潜在错误。

## JEP 304: 垃圾回收器接口

JEP 304 引入了一个统一的垃圾回收器接口，旨在使不同的垃圾回收器实现能够更容易地集成到 JVM 中，并提高垃圾回收器的可维护性和可扩展性。

通过定义一个标准的垃圾回收器接口，JVM 可以更灵活地切换不同的垃圾回收算法，而无需对 JVM 的核心代码进行大量修改。这对于研究和开发新的垃圾回收算法非常有帮助，同时也为 JVM 的未来发展提供了更好的基础。

```java
// 示例代码展示如何通过接口与垃圾回收器交互（概念性示例，非实际代码）
interface GarbageCollector {
    void collect();
    void setOptions(Map<String, String> options);
}

class G1GarbageCollector implements GarbageCollector {
    @Override
    public void collect() {
        // 执行 G1 垃圾回收
    }

    @Override
    public void setOptions(Map<String, String> options) {
        // 设置 G1 垃圾回收器的选项
    }
}
```

## JEP 307: G1 的并行全垃圾回收

G1（Garbage-First）垃圾回收器是 Java 9 中默认的垃圾回收器，它在处理大型堆内存时表现出色。然而，在全垃圾回收（Full GC）阶段，G1 仍然是串行执行的，这可能会导致较长的停顿时间。

JEP 307 引入了 G1 的并行全垃圾回收功能，通过利用多核处理器的优势，并行执行全垃圾回收任务，从而减少了停顿时间，提高了应用程序的响应速度。

## JEP 310: 应用程序类数据共享

类数据共享（Class Data Sharing，CDS）是 Java 早期版本中引入的一项功能，它允许将一些常用的类加载到共享内存中，以便在不同的 JVM 实例之间共享，从而减少启动时间和内存占用。

JEP 310 扩展了 CDS 的功能，引入了应用程序类数据共享（Application Class-Data Sharing，AppCDS），允许开发者将自定义的应用程序类添加到共享存档中，进一步提高了应用程序的启动性能和内存使用效率。

```java
// 创建应用程序类数据共享存档的步骤（命令行示例）
// 1. 运行应用程序并记录类列表
java -Xshare:off -XX:+UseAppCDS -XX:DumpLoadedClassList=app_classlist.txt -cp your_app.jar YourApp

// 2. 创建共享存档
java -Xshare:dump -XX:+UseAppCDS -XX:SharedClassListFile=app_classlist.txt -XX:SharedArchiveFile=app_cds.jsa -cp your_app.jar

// 3. 使用共享存档运行应用程序
java -Xshare:on -XX:+UseAppCDS -XX:SharedArchiveFile=app_cds.jsa -cp your_app.jar YourApp
```

## JEP 312: 线程局部握手

在 Java 之前的版本中，JVM 在执行某些操作（如垃圾回收、安全点等）时，需要暂停所有线程以确保操作的正确性。这可能会导致应用程序的停顿时间增加，影响性能。

JEP 312 引入了线程局部握手（Thread-Local Handshakes）机制，它允许 JVM 在不暂停所有线程的情况下，与单个线程进行交互。这使得 JVM 可以更细粒度地控制线程的执行，减少了不必要的停顿时间，提高了应用程序的响应速度。

## JEP 313: 移除本地头生成工具（javah）

在 Java 开发中，当需要调用本地代码（如 C/C++ 编写的库）时，需要使用 `javah` 工具生成本地头文件，以便本地代码能够与 Java 代码进行交互。

随着 Java 的发展，`javah` 工具的功能已经逐渐被集成到 `javac` 编译器中。JEP 313 决定移除 `javah` 工具，以简化开发流程，减少开发者需要掌握的工具数量。从 Java 10 开始，开发者可以直接使用 `javac` 命令生成本地头文件。

## JEP 314: 额外的 Unicode 语言标签扩展

Unicode 语言标签用于标识自然语言的变体，例如地区、脚本、书写方向等。JEP 314 引入了额外的 Unicode 语言标签扩展，以支持更多的语言变体和文化习惯。

这些扩展的语言标签可以帮助开发者更准确地处理国际化文本，例如在格式化日期、时间、数字等时，根据不同的语言标签选择合适的显示方式。

```java
import java.text.NumberFormat;
import java.util.Locale;

public class UnicodeLanguageTagExample {
    public static void main(String[] args) {
        // 使用扩展的 Unicode 语言标签
        Locale locale = Locale.forLanguageTag("en-US-u-ca-buddhist");
        NumberFormat numberFormat = NumberFormat.getInstance(locale);

        double number = 12345.67;
        System.out.println(numberFormat.format(number));
    }
}
```

## JEP 316: 替代内存设备上的堆分配

随着计算机硬件的发展，除了传统的 DRAM 内存，还出现了一些替代内存设备，如非易失性内存（NVM）。这些替代内存设备具有不同的特性和性能优势，例如持久性、低延迟等。

JEP 316 允许 JVM 在替代内存设备上进行堆分配，以充分利用这些设备的优势。通过在替代内存设备上分配堆内存，开发者可以实现数据的持久化存储，减少数据在应用程序重启时的加载时间，同时也可以提高内存的访问速度。

## JEP 317: 基于 Java 的 JIT 编译器（实验性）

即时编译器（Just-In-Time Compiler，JIT）是 Java 虚拟机的重要组成部分，它负责将 Java 字节码编译成本地机器码，以提高程序的执行效率。在 Java 10 之前，JVM 主要使用基于 C++ 编写的 JIT 编译器，如 C1 和 C2。

JEP 317 引入了一个基于 Java 的 JIT 编译器（Graal），作为实验性功能。Graal 编译器具有更好的可扩展性和可维护性，它允许开发者使用 Java 语言来编写和优化编译器代码。此外，Graal 编译器还支持多种编程语言的前端，为 JVM 的多语言支持提供了更好的基础。

## JEP 319: 根证书

在 Java 应用程序中，当需要建立安全连接（如 HTTPS）时，需要使用根证书来验证服务器的身份。在 Java 10 之前，JDK 中不包含任何根证书，开发者需要手动配置或依赖操作系统提供的根证书。

JEP 319 在 JDK 中包含了一个默认的根证书集合，这使得 Java 应用程序能够更方便地建立安全连接，而无需开发者进行额外的配置。这一特性提高了 Java 应用程序的安全性和易用性。

## JEP 322: 基于时间的版本发布

在 Java 10 之前，Java 的版本发布周期不固定，这给开发者和企业带来了一定的不确定性。JEP 322 引入了基于时间的版本发布模型，规定每六个月发布一个 Java 版本，以提供更可预测的发布周期。

基于时间的版本发布模型使得开发者能够更及时地获取 Java 的新特性和改进，同时也为企业提供了更好的规划和管理 Java 环境的基础。每个版本都有一个明确的发布日期和版本号，例如 Java 10、Java 11 等，方便开发者识别和引用。

## Stream API 增强
### 1. `Collectors` API 的增强：不可变集合支持
- **核心改进**：Java 10在`Collectors`类中新增了`toUnmodifiableList()`、`toUnmodifiableSet()`和`toUnmodifiableMap()`方法，允许在流操作中直接生成不可变集合。
- **代码示例**：
  ```java
  List<String> immutableList = Stream.of("a", "b", "c")
                                    .collect(Collectors.toUnmodifiableList());
  // immutableList.add("d"); // 抛出UnsupportedOperationException
  ```
- **优势**：
    - **线程安全**：不可变集合天然避免并发修改问题。
    - **性能优化**：减少防御性拷贝的开销（如方法参数传递时无需创建副本）。
    - **代码清晰**：显式声明集合不可变性，提升可读性。

### **2. 局部变量类型推断（`var`）的间接支持**
- **关联性**：虽然`var`是Java 10的语言特性，但它简化了Stream API的链式调用代码：
  ```java
  var result = Stream.of(1, 2, 3)
                    .filter(x -> x % 2 == 0)
                    .map(x -> x * 2)
                    .collect(Collectors.toList());
  ```
- **影响**：
    - 减少冗余类型声明，使流操作更聚焦于逻辑本身。
    - 与Stream API的函数式风格形成协同效应，提升代码简洁性。

### **3. 性能与内部优化的持续改进**
- **底层优化**：Java 10延续了Java 9对Stream的改进（如`takeWhile`/`dropWhile`方法），进一步优化了中间操作的执行效率。
- **并行流支持**：通过`parallel()`方法生成的并行流仍能利用多核CPU，但需注意：
    - **适用场景**：大数据集（如GB级以上）或计算密集型任务（如复杂转换）。
    - **开销权衡**：小数据集可能因线程调度开销导致性能下降。

