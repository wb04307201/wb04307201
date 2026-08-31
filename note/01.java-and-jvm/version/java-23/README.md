<!--
module:
  parent: java
  slug: java/version/java-23
  type: article
  category: 主模块子文章
  summary: Java 23：12 个 JEP，含基本类型模式匹配预览、Markdown 文档注释、可控流式 IO 孵化
  depth: ⭐
-->

# Java 23

## 引言：变更说明

Java 23 是 12 个 JEP 的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

### 相关阅读

← [Java 22](../java-22/README.md) · [Java 24](../java-24/README.md)

---

- **JEP 455**: 模式、instanceof 和 switch 中的基本类型（预览）
- **JEP 466**: 类文件 API（第二次预览）
- **JEP 467**: Markdown 文档注释
- **JEP 469**: 向量 API（第八次孵化）
- **JEP 471**: 弃用 sun.misc.Unsafe 中的内存访问方法以待移除
- **JEP 473**: Stream 收集器（第二次预览）
- **JEP 474**: ZGC：默认采用分代模式
- **JEP 476**: 模块导入声明（预览）
- **JEP 477**: 隐式声明类和实例主方法（第三次预览）
- **JEP 480**: 结构化并发（第三次预览）
- **JEP 481**: 作用域值（第三次预览）
- **JEP 482**: 灵活的构造函数体（第二次预览）

## JEP 455: 模式、instanceof 和 switch 中的基本类型（预览）

该特性扩展了模式匹配的功能，允许在 `instanceof` 操作符和 `switch` 表达式中使用基本类型。这能让代码更简洁易读，减少不必要的类型转换。例如，使用 `instanceof` 时，可直接对基本类型判断：
```java
Object obj = 42;
if (obj instanceof int i) {
    System.out.println("It's an int: " + i);
}
```
在 `switch` 表达式中，也可用基本类型匹配：
```java
int value = 2;
String result = switch (value) {
    case 1 -> "One";
    case 2 -> "Two";
    case 3 -> "Three";
    default -> "Unknown";
};
System.out.println(result);
```

## JEP 466: 类文件 API（第二次预览）

类文件 API 为开发者提供了直接操作 Java 类文件的编程接口。通过该 API，开发者能以编程方式读取、分析和修改类文件，无需依赖外部工具或库。这对于构建类文件分析工具、代码转换工具和动态代码生成器等非常有用。例如，开发者可利用该 API 读取类文件中的方法信息、字段信息等，并根据需求进行修改或生成新的类文件。

## JEP 467: Markdown 文档注释

此特性引入对 Markdown 格式文档注释的支持。Markdown 是一种轻量级标记语言，易于编写和阅读。在 Java 代码中使用 Markdown 格式的文档注释，可生成更美观、结构更清晰的文档。例如，开发者可使用 Markdown 语法编写类、方法、字段等的说明文档，IDE 或文档生成工具能将其渲染为格式良好的 HTML 或其他格式的文档，提高代码文档的可读性和可维护性。
```markdown
/**
 * # 用户服务
 *
 * 提供用户管理相关功能。
 *
 * ## 主要方法
 * - `getUser(id)` — 获取用户信息
 * - `createUser(user)` — 创建新用户
 */
public class UserService { ... }
```

## JEP 469: 向量 API（第八次孵化）

向量 API 提供高效向量计算方式，适用于科学计算、机器学习等领域。通过引入新类和接口，允许开发者用硬件加速的向量指令执行计算，提高性能。例如：
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

## JEP 473: Stream 收集器（第二次预览）

Stream 收集器特性为 Java Stream API 提供了更强大和灵活的收集操作。它允许开发者自定义收集器，将 Stream 中的元素按照特定规则收集到结果容器中。这为数据处理和聚合操作提供了更多可能性，例如实现复杂的分组、排序、转换等操作。通过使用 Stream 收集器，开发者能以更简洁和声明式的方式处理数据集合，提高代码的可读性和可维护性。

## JEP 471: 弃用 sun.misc.Unsafe 中的内存访问方法以待移除

`sun.misc.Unsafe` 类提供了对底层内存操作的直接访问，但这些方法存在安全风险且不便于维护。该特性旨在弃用其中的内存访问方法，为后续移除做准备。这有助于提高 Java 平台的安全性和稳定性，鼓励开发者使用更安全和标准的内存操作方式，如 `java.nio` 包中的类和方法。

## JEP 474: ZGC：默认采用分代模式

ZGC 是一种高性能垃圾回收器，该特性使其默认采用分代模式。分代模式根据对象的生命周期将堆内存分为不同代，如年轻代和老年代，并针对不同代采用不同的垃圾回收策略。这能提高垃圾回收的效率和性能，减少垃圾回收的停顿时间，提升应用程序的响应速度，尤其适用于对性能要求较高的大规模应用程序。

## JEP 476: 模块导入声明（预览）

模块导入声明提供更简洁的导入模块中包的方式。允许开发者通过 `import module` 语法导入整个模块的所有包，减少代码冗余。例如：
```java
// 使用模块导入声明 - 导入 java.sql 模块的所有包
import module java.sql;

// 无需再逐个导入
// import java.sql.Connection;
// import java.sql.DriverManager;
// import java.sql.ResultSet;
// import java.sql.Statement;
// ...

public class MyClass {
    // 可以直接使用 java.sql 模块中的所有类
    Connection conn = DriverManager.getConnection("jdbc:...");
}
```

## JEP 477: 隐式声明类和实例主方法（第三次预览）

该特性进一步简化 Java 源代码结构，支持隐式声明类和实例主方法。未命名的类可省略类名，且提供更简单的实例主方法声明方式。例如：
```java
// 紧凑源文件示例
void main() {
    System.out.println("Hello, World!");
}
```

## JEP 480: 结构化并发（第三次预览）

结构化并发是多线程编程方法，旨在简化多线程代码管理和错误处理。它将不同线程中的多个任务视为单个工作单元，提高代码可读性、可维护性和可靠性。引入 `StructuredTaskScope` 类，允许开发者将任务拆分为多个并发子任务，在各自线程执行，子任务须在主任务继续前完成，使错误处理更简单，异常可在一处捕获处理。例如：
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

## JEP 481: 作用域值（第三次预览）

作用域值是在特定作用域内共享不可变数据的机制。类似线程局部变量，但更适用于虚拟线程和结构化并发等新编程模型。允许在大型程序组件间安全有效共享数据，无需借助方法参数，减少代码冗余，提高可维护性。例如：
```java
final static ScopedValue<String> USER_NAME = ScopedValue.newInstance();

// 设置作用域值
ScopedValue.where(USER_NAME, "Alice")
           .run(() -> {
               // 在这个作用域内可以访问 USER_NAME
               System.out.println("Hello, " + USER_NAME.get());
           });
```

## JEP 482: 灵活的构造函数体（第二次预览）

灵活的构造函数体允许在调用父类构造函数（`super(...)`）之前执行一些语句。在第二次预览中，该特性进一步完善了语义和实现，使得构造函数编写更加灵活。这些语句在代码上写在 `super` 调用前，但实际执行是在父类构造函数调用之后、子类构造函数体之前。

```java
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

---

## 其他新特性（非 JEP）

Java 23 还包含大量非 JEP 的改进，以下列出对开发者最实用的特性：

### 核心库

#### Console 显式 Locale 方法

`java.io.Console` 新增 4 个接受 `java.util.Locale` 的方法：`format(Locale, ...)`、`printf(Locale, ...)`、`readLine(Locale, ...)`、`readPassword(Locale, ...)`。

```java
Console console = System.console();
console.printf(Locale.FRANCE, "Prix: %, .2f €\n", 1234.56);
```

#### JFR 序列化误声明事件

新增 `jdk.SerializationMisdeclaration` JFR 事件，在序列化相关字段/方法声明不当时触发（如 `writeObject()` 声明为 `public` 而非 `private`）。

#### WatchService 最大事件数

新系统属性 `jdk.nio.file.WatchService.maxEventsPerPoll` 设置发出 OVERFLOW 事件前的最大待处理 WatchService 事件数。

#### Instant.until(Instant)

新增 `Instant.until(Instant)` 方法获取到指定 `Instant` 的 `Duration`。比 `Duration.between()` 更方便。

```java
Instant start = Instant.now();
// ...
Duration elapsed = start.until(Instant.now());
```

#### HttpServer 缓冲响应头

`HttpServer` 不再在分块模式或存在响应体时立即发送响应头，而是缓冲并与响应体一起发送，改善性能。

#### DecimalFormat 转义修复

`MessageFormat.toPattern()` 现在正确转义嵌套格式子模式中的单引号。

### 安全

#### java.security.debug 增强

`java.security.debug` 系统属性现接受 `+timestamp` 和 `+thread` 后缀，添加时间戳、线程 ID、线程名和调用者信息。

```bash
-Djava.security.debug=all+timestamp+thread
```

#### KeychainStore-ROOT 密钥库

Apple "KeychainStore" 现支持两种密钥库类型：`KeychainStore`（用户当前钥匙串）和 `KeychainStore-ROOT`（系统根证书钥匙串）。

#### Kerberos 大小写敏感查找

新安全属性 `jdk.security.krb5.name.caseSensitive` 控制 keytab 和凭证缓存中主体名查找的大小写敏感性。默认 `false`。

#### SunPKCS11 遗留机制检查增强

SunPKCS11 遗留机制检查现在具有服务类型粒度。新配置属性 `allowLegacy`（默认 `false`）。

#### CipherInputStream 缓冲区增大

`CipherInputStream` 内部缓冲区从 512 字节增加到 8192 字节，提升性能。

#### PKCS12 自定义迭代次数

新系统属性 `keystore.pkcs12.certPbagIterationCount`（默认 50,000）和 `keystore.pkcs12.keyPbagIterationCount`（默认 100,000）。

#### Certainly 根证书

新增两个根证书：`certainlyrootr1` 和 `certainlyroote1`。

### 工具

#### javac 注解处理默认禁用

javac 中的注解处理现在仅在显式配置或显式请求时运行。使用 `-proc:full` 保留旧行为。

#### javac -Xlint:dangling-doc-comments

新增 lint 子选项检测错误放置或意外的文档注释。

#### javadoc 结构化导航改进

生成的 API 文档增强导航：当前页面目录侧边栏、页面头部面包屑导航、TOC 文本过滤、折叠/展开按钮。

#### javadoc JavaScript 模块支持

`javadoc --add-script` 现支持 JavaScript 模块（按文件扩展名或内容自动检测）。

#### javap -verify

新增 `javap -verify` 选项打印额外的类验证信息。

### XML / JAXP

#### 严格 JAXP 配置模板

新模板文件 `$JAVA_HOME/conf/jaxp-strict.properties.template`，用于使用更严格的 XML 处理设置测试应用。

### HotSpot

#### Parallel GC 新 Full GC 算法

Parallel GC 现在使用与 Serial GC 和 G1 GC 相同的 Full GC 算法。新算法对有问题的负载表现显著更好，并消除 1.5% 堆外内存开销。

#### GetObjectMonitorUsage 不再支持虚拟线程

JVM TI `GetObjectMonitorUsage` 重新规范：不再在监视器由虚拟线程拥有时返回监视器信息。

#### -Xnoagent 移除

`-Xnoagent` java 启动器选项（之前弃用待移除）现已移除。使用它将导致错误。

### 国际化

#### Unicode 16.0

支持 Unicode 16.0 标准。

#### CLDR v46

语言环境数据更新到 Unicode CLDR v46 版本。

### 移除特性

| 移除项 | 详情 |
|--------|------|
| `Thread.suspend()`/`resume()` | 自 JDK 1.2 弃用，Java 19/20 退化为 UnsupportedOperationException，现完全移除 |
| `ThreadGroup.stop()` | 自 JDK 1.2 弃用，Java 20 退化，现完全移除 |
| VarHandle 对齐访问模式 | `byteArrayViewVarHandle` 不再支持原子访问模式 |
| `jdk.random` 模块 | RandomGenerator 算法实现移至 `java.base` |
| 遗留 JRE/COMPAT 语言环境数据 | CLDR 语言环境数据现在是唯一选项 |
| JMX Subject 委托 | `JMXConnector.getMBeanServerConnection(Subject)` 抛 UnsupportedOperationException |
| JMX 管理 Applet (m-let) | `MLet`、`MLetContent`、`PrivateMLet`、`MLetMBean` 移除 |

### 弃用特性

| 弃用项 | 详情 |
|--------|------|
| `java.beans.beancontext` 包 | 整包弃用待移除 |
| `PreserveAllAnnotations` VM 选项 | 弃用，将被废弃并移除 |
| `DontYieldALot` 标志 | 弃用 |
| `UseEmptySlotsInSupers` | 弃用，JDK 24 废弃 |
| `UseNotificationThread` | 弃用 |

---

← [返回 Java 版本特性](../README.md)