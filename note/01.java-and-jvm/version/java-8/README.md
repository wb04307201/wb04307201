<!--
module:
  parent: java
  slug: java/version/java-8
  type: article
  category: 主模块子文章
  summary: Java 8 (LTS)：55 个 JEP，含 Lambda 表达式、Stream API、Optional、新日期时间 API、默认方法、类型注解、Nashorn JavaScript 引擎
-->

# Java 8

## 引言：变更说明

Java 8 是 55 个 JEP 的合集，于 2014 年 3 月发布，是 Java 历史上最重要的 LTS（长期支持）版本之一。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

### 相关阅读

→ [Java 9](../java-9/README.md) · [Java 全部版本](../README.md)

---

- **JEP 103**: 类型注解处理器
- **JEP 113**: 改进字节码状态处理
- **JEP 114**: TLS 服务器指示名称 (SNI)
- **JEP 115**: 认证加密的密码套件
- **JEP 119**: 支持反射的自动代理选择
- **JEP 121**: 更强的证书验证算法
- **JEP 123**: 配置和禁用加密协议版本
- **JEP 124**: 增强证书处理
- **JEP 126**: 增强 PKI 路径验证算法
- **JEP 127**: 改进本地化数据
- **JEP 129**: 增强安全值处理
- **JEP 130**: 默认随机数生成器的改进
- **JEP 131**: 在 64 位 Windows 上生成 PKCS11 密钥存储
- **JEP 133**: 支持 64 位 Windows 上的 Kerberos
- **JEP 140**: 限制反序列化
- **JEP 142**: 废弃辅助类
- **JEP 166**: 为 JDK 9 的模块化做准备
- **JEP 171**: 融合三个 FIPS 认证
- **JEP 185**: 限制外部内存访问
- **JEP 128**: Lambda 表达式 & 虚拟扩展方法
- **JEP 138**: 基于 Autoconf 的构建系统
- **JEP 160**: 针对 Method Handles 的 Lambda 形式的表征
- **JEP 161**: 简洁的配置文件
- **JEP 162**: 为模块化做准备
- **JEP 164**: 利用 CPU 指令来改善 AES 加密的性能
- **JEP 174**: Nashorn 引擎（允许在 Java 程序中嵌入 JS 代码）
- **JEP 176**: 自动检测识别 Caller-Sensitive 方法
- **JEP 179**: JDK API 变化和稳定性记录
- **JEP 101**: 目标类型推断
- **JEP 104**: Java 类型注解
- **JEP 105**: DocTree API
- **JEP 106**: 在 javax.tools 中添加 Javadoc
- **JEP 107**: 集合数据批量操作（Stream API 的基础）
- **JEP 109**: 增强的包含 Lambda 的核心库
- **JEP 112**: 改进了字符集的实现
- **JEP 117**: 移除 APT（Annotation-Processing Tool）
- **JEP 118**: 运行过程中可访问参数名
- **JEP 120**: 重复注解（@Repeatable）
- **JEP 122**: 移除 Permanent Generation（永久代），使用元空间（MetaSpace）
- **JEP 135**: Base64 编解码
- **JEP 136**: 提供更多的验证错误信息
- **JEP 139**: 增强了 javac，以改善构建速度
- **JEP 147**: 减少类元数据封装
- **JEP 148**: 支持创建小型虚拟机（3M 以下）
- **JEP 149**: 减少了核心库的内存占用
- **JEP 150**: 新的日期时间 API（java.time 包）
- **JEP 153**: 命令行启动 JavaFX 应用
- **JEP 155**: 改进对并发的支持
- **JEP 170**: JDBC 4.2
- **JEP 172**: DocLint 工具，用来检查 Javadoc 注释内容
- **JEP 173**: 移除一些很少使用的垃圾回收器组合
- **JEP 177**: java.text.DecimalFormat.format 优化
- **JEP 178**: 静态链接的 JNI 库
- **JEP 180**: 使用平衡树处理频繁的 HashMap 碰撞
- **JEP 184**: HTTP URL 访问权限

## JEP 128: Lambda 表达式 & 虚拟扩展方法

Lambda 表达式是 Java 8 中最重要的特性之一，它允许开发者以更简洁的方式编写匿名函数。Lambda 表达式的主要用途是简化函数式接口（只有一个抽象方法的接口）的实现。

虚拟扩展方法（也称为默认方法）允许接口包含具体的方法实现，这样可以在不破坏现有实现的情况下向接口添加新功能。

```java
// Lambda 表达式示例
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
names.forEach(name -> System.out.println(name));

// 虚拟扩展方法示例
interface Greeting {
    void greet();
    default void greetInEnglish() {
        System.out.println("Hello");
    }
}

class EnglishGreeting implements Greeting {
    @Override
    public void greet() {
        greetInEnglish();
    }
}
```

## JEP 138: 基于 Autoconf 的构建系统

Autoconf 是一个用于生成自动化配置脚本的工具，广泛应用于开源软件的构建过程。该特性引入了基于 Autoconf 的构建系统，使得 JDK 的构建过程更加灵活和可移植。

通过使用 Autoconf，开发者可以在不同的平台上生成适合的配置脚本，简化了 JDK 的跨平台构建过程。

## JEP 160: 针对 Method Handles 的 Lambda 形式的表征

Method Handles 是 Java 中用于动态操作方法的一种机制。该特性改进了 Method Handles 的实现，使其能够更好地支持 Lambda 表达式。

通过这种改进，Lambda 表达式可以更高效地转换为 Method Handles，提高了函数式编程的性能。

## JEP 161: 简洁的配置文件

该特性引入了一种更简洁的配置文件格式，用于配置 JDK 的各种参数。这种格式减少了配置文件的冗余信息，使得配置更加直观和易于管理。

## JEP 162: 为模块化做准备

模块化是 Java 9 中引入的一个重要特性，该特性在 Java 8 中为模块化做了准备工作。它引入了一些基础结构和工具，以便后续能够顺利实现模块化系统。

## JEP 164: 利用 CPU 指令来改善 AES 加密的性能

该特性通过利用现代 CPU 提供的特定指令集（如 AES-NI），显著提高了 AES 加密和解密的性能。这对于需要高性能加密的应用程序非常有益。

## JEP 166: 为 JDK 9 的模块化做准备

在 JDK 8 中进行模块化系统（Jigsaw）的前期准备工作，包括代码库重构、依赖关系清理和构建系统适配，为 Java 9 正式引入模块化系统铺路。

## JEP 174: Nashorn 引擎（允许在 Java 程序中嵌入 JS 代码）

Nashorn 是一个基于 Java 的 JavaScript 引擎，它允许开发者在 Java 应用程序中执行 JavaScript 代码。这使得 Java 和 JavaScript 之间的交互更加容易，适用于需要混合编程的场景。

```java
ScriptEngine engine = new ScriptEngineManager().getEngineByName("nashorn");
try {
    engine.eval("print('Hello, World!')");
} catch (ScriptException e) {
    e.printStackTrace();
}
```

## JEP 176: 自动检测识别 Caller-Sensitive 方法

Caller-Sensitive 方法是指其行为依赖于调用者的方法。该特性引入了一种机制，能够自动检测和识别这些方法，从而在安全管理和反射操作中提供更准确的信息。

## JEP 179: JDK API 变化和稳定性记录

该特性旨在记录 JDK API 的变化和稳定性信息，帮助开发者更好地理解和使用 JDK API。通过提供详细的变更日志和稳定性评级，开发者可以更容易地跟踪 API 的演进。

## JEP 101: 目标类型推断

目标类型推断允许编译器根据上下文自动推断出 Lambda 表达式或方法引用的目标类型。这使得代码更加简洁，减少了显式类型声明的需要。

```java
// 目标类型推断示例
List<String> list = Arrays.asList("a", "b", "c");
String joined = list.stream().reduce("", (a, b) -> a + b);
```

## JEP 103: 类型注解处理器

类型注解处理器（Type Annotation Processor）为 Java 类型系统提供了注解支持，允许在类型使用的地方（如泛型参数、类型转换等）添加注解，而不仅仅是在声明处。这是 JEP 104（Java 类型注解）的基础设施。

## JEP 104: Java 类型注解

Java 类型注解允许开发者在类型使用的地方添加注解，而不仅仅是在声明的地方。这提供了更细粒度的元数据控制，有助于改进代码的可读性和可维护性。

```java
// Java 类型注解示例
public class Example {
    public static void main(@NonNull String[] args) {
        // ...
    }
}
```

## JEP 105: DocTree API

DocTree API 提供了一种访问和操作 Javadoc 注释树结构的机制。这使得开发者可以编写工具来分析和处理 Javadoc 注释，例如生成文档或进行代码检查。

## JEP 106: 在 javax.tools 中添加 Javadoc

该特性在 `javax.tools` 包中添加了对 Javadoc 的支持，使得开发者可以通过编程方式生成 Javadoc 文档。这对于自动化构建和文档生成非常有用。

## JEP 107: 集合数据批量操作（Stream API 的基础）

该特性引入了集合数据的批量操作机制，为 Stream API 的实现奠定了基础。Stream API 提供了一种函数式的方式来处理集合数据，支持过滤、映射、归约等操作。

```java
// Stream API 示例
List<String> filtered = names.stream()
                           .filter(name -> name.startsWith("A"))
                           .collect(Collectors.toList());
```

## JEP 109: 增强的包含 Lambda 的核心库

该特性对 Java 核心库进行了增强，使其更好地支持 Lambda 表达式。许多核心库方法现在接受函数式接口作为参数，从而可以利用 Lambda 表达式简化代码。

## JEP 112: 改进了字符集的实现

该特性改进了 Java 中字符集的实现，提高了字符编码和解码的性能和准确性。这对于处理多语言文本的应用程序非常重要。

## JEP 113: 改进字节码状态处理

改进 HotSpot 客户端编译器（C1）的字节码状态处理机制，优化了字节码到 IR（中间表示）的转换过程，提高了编译效率和生成代码的质量。

## JEP 114: TLS 服务器指示名称 (SNI)

JSSE（Java Secure Socket Extension）新增对 TLS 扩展服务器名称指示（Server Name Indication，SNI）的支持。SNI 允许客户端在 TLS 握手时指定要连接的主机名，使服务器能够在同一 IP 地址上提供多个不同域名的证书。

```java
// SNI 示例
SSLSocket socket = (SSLSocket) sslSocketFactory.createSocket();
socket.addHandshakeCompletedListener(event -> {
    System.out.println("TLS handshake completed");
});
// SNI 参数通过 SSLParameters 配置
SSLParameters params = new SSLParameters();
params.setServerNames(List.of(new SNIHostName("example.com")));
socket.setSSLParameters(params);
```

## JEP 115: 认证加密的密码套件

支持认证加密（AE，Authenticated Encryption）密码套件，如 AES/GCM（Galois/Counter Mode）。AE 同时提供数据机密性和完整性保护，比传统的加密+MAC 组合更安全高效。

## JEP 117: 移除 APT（Annotation-Processing Tool）

APT 是一个较早的注解处理工具，该特性决定将其从 JDK 中移除，因为现在有更先进的注解处理机制（如 `javax.annotation.processing`）可用。

## JEP 118: 运行过程中可访问参数名

该特性允许在运行时通过反射机制访问方法的参数名。这对于调试和日志记录非常有用，因为可以显示实际的参数名而不是 `arg0`、`arg1` 等占位符。

```java
// 访问参数名示例
Method method = Example.class.getMethod("exampleMethod", String.class);
Parameter[] parameters = method.getParameters();
for (Parameter parameter : parameters) {
    System.out.println(parameter.getName());
}
```

## JEP 119: 支持反射的自动代理选择

引入 `java.net.ProxySelector` 的默认实现，支持通过反射机制自动选择代理。当应用需要通过 HTTP/SOCKS 代理访问外部资源时，系统可以根据配置自动选择合适的代理服务器。

## JEP 120: 重复注解（@Repeatable）

重复注解允许在同一个元素上多次应用同一个注解。这在需要多次使用相同类型的元数据时非常有用，避免了创建多个包装注解的麻烦。

```java
// 重复注解示例
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@Repeatable(Roles.class)
public @interface Role {
    String value();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface Roles {
    Role[] value();
}

@Role("Admin")
@Role("User")
public class ExampleClass {
    // ...
}
```

## JEP 121: 更强的证书验证算法

改进 PKIX 证书路径验证算法，提供更严格的证书链验证。增强了 `java.security.cert` 包中的证书验证逻辑，包括对证书扩展项的更精确检查和对弱算法的拒绝。

## JEP 122: 移除 Permanent Generation（永久代），使用元空间（MetaSpace）

该特性移除了 JVM 中的永久代，改用元空间来存储类的元数据。元空间使用本地内存，而不是 JVM 堆内存，从而避免了永久代内存溢出的问题。

## JEP 123: 配置和禁用加密协议版本

新增系统属性 `jdk.tls.disabledAlgorithms`，允许管理员禁用特定的 SSL/TLS 协议版本（如 SSLv3、TLSv1.0 等）和加密算法。这对于应对已知安全漏洞（如 POODLE）至关重要。

## JEP 124: 增强证书处理

改进 X.509 证书处理逻辑，增强了对证书扩展项的解析和验证，提高了证书链构建的准确性和性能。

## JEP 126: 增强 PKI 路径验证算法

改进 PKI（公钥基础设施）路径验证算法的实现，优化了证书链验证的性能和正确性，支持更多的证书策略和约束检查。

## JEP 127: 改进本地化数据

改进 JDK 中的本地化数据处理，采用 Unicode CLDR（Common Locale Data Repository）数据作为默认的区域设置数据来源，提供更准确的国际化支持。可通过 `-Djava.locale.providers=CLDR` 启用。

## JEP 129: 增强安全值处理

增强 `java.security` 包中安全相关值的处理机制，改进了权限检查和安全策略的执行效率。

## JEP 130: 默认随机数生成器的改进

改进默认随机数生成器（DRBG）的实现，基于 NIST SP 800-90A 标准，提供更安全和可配置的随机数生成支持。

```java
// 使用 DRBG
SecureRandom random = SecureRandom.getInstance("DRBG");
byte[] bytes = new byte[32];
random.nextBytes(bytes);
```

## JEP 131: 在 64 位 Windows 上生成 PKCS11 密钥存储

SunPKCS11 提供者支持在 64 位 Windows 平台上生成和管理 PKCS#11 密钥存储，扩展了硬件安全模块（HSM）的 platform 支持。

## JEP 133: 支持 64 位 Windows 上的 Kerberos

将 Kerberos 安全协议的支持扩展到 64 位 Windows 平台，使企业级单点登录（SSO）可以在 64 位 Windows 环境中正常工作。

## JEP 135: Base64 编解码

该特性在 Java 核心库中添加了 Base64 编解码的支持，使得开发者可以方便地进行 Base64 编码和解码操作。

```java
// Base64 编解码示例
String originalInput = "test string";
String encodedString = Base64.getEncoder().encodeToString(originalInput.getBytes());
byte[] decodedBytes = Base64.getDecoder().decode(encodedString);
String decodedString = new String(decodedBytes);
```

## JEP 136: 提供更多的验证错误信息

该特性改进了 Java 编译器和运行时系统的错误报告机制，提供了更详细和准确的验证错误信息。这有助于开发者更快地定位和修复问题。

## JEP 139: 增强了 javac，以改善构建速度

该特性对 `javac` 编译器进行了优化，提高了编译速度。这对于大型项目的构建过程非常有益，减少了开发者的等待时间。

## JEP 140: 限制反序列化

新增 `jdk.serialFilter` 系统属性和 JVM 级过滤器机制，允许应用配置反序列化过滤规则，防止恶意对象的反序列化攻击（反序列化漏洞防护）。

```bash
# 配置反序列化过滤器
java -Djdk.serialFilter="!com.dangerous.**;maxdepth=5;maxarray=100" MyApp
```

## JEP 142: 废弃辅助类

将 `java.util.Date` 和 `java.util.Calendar` 等辅助类标记为废弃（实际为推荐迁移到新 API），引导开发者使用 `java.time` 包中的现代日期时间 API。

## JEP 147: 减少类元数据封装

该特性通过减少类元数据的封装开销，提高了 JVM 的性能。类元数据是描述类结构和行为的信息，减少其封装可以加快类的加载和链接过程。

## JEP 148: 支持创建小型虚拟机（3M 以下）

该特性优化了 JVM 的内存使用，使得可以创建内存占用更小的虚拟机实例（3M 以下）。这对于嵌入式系统和资源受限的环境非常有用。

## JEP 149: 减少了核心库的内存占用

该特性通过优化核心库的实现，减少了其内存占用。这对于提高应用程序的整体性能和资源利用率非常重要。

## JEP 150: 新的日期时间 API（java.time 包）

新的日期时间 API 引入了 `java.time` 包，提供了一种更现代、更易用的日期和时间处理机制。它解决了旧日期时间 API 中的许多问题，如线程安全性、易用性等。

```java
// 新的日期时间 API 示例
LocalDate today = LocalDate.now();
LocalDateTime now = LocalDateTime.now();
ZonedDateTime zonedNow = ZonedDateTime.now();
```

## JEP 153: 命令行启动 JavaFX 应用

该特性允许通过命令行直接启动 JavaFX 应用程序，简化了 JavaFX 应用的部署和运行过程。

```bash
java --module-path /path/to/javafx-sdk/lib --add-modules javafx.controls,javafx.fxml -jar MyApp.jar
```

## JEP 155: 改进对并发的支持

该特性对 Java 的并发支持进行了改进，引入了新的并发工具和机制，如 `CompletableFuture` 和 `StampedLock`，提高了多线程编程的效率和可靠性。

```java
// CompletableFuture 示例
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> "Hello")
                                                  .thenApply(s -> s + " World");
future.thenAccept(System.out::println);
```

## JEP 170: JDBC 4.2

JDBC 4.2 是 Java 数据库连接 API 的一个更新版本，引入了一些新特性和改进，如支持新的 SQL 类型、改进的连接池管理等。

## JEP 171: 融合三个 FIPS 认证

整合三个 FIPS（Federal Information Processing Standards）认证的实现，统一了安全提供者的 FIPS 合规处理逻辑，简化了安全配置和合规性检查。

## JEP 172: DocLint 工具，用来检查 Javadoc 注释内容

DocLint 是一个用于检查 Javadoc 注释内容的工具，它可以帮助开发者确保 Javadoc 注释的准确性和一致性。通过 DocLint，可以检测出注释中的语法错误、格式问题等。

## JEP 173: 移除一些很少使用的垃圾回收器组合

该特性移除了一些很少使用的垃圾回收器组合，简化了 JVM 的垃圾回收配置选项。这有助于减少开发者的配置负担，提高垃圾回收的效率。

## JEP 177: java.text.DecimalFormat.format 优化

该特性对 `java.text.DecimalFormat.format` 方法进行了优化，提高了数字格式化的性能。这对于需要频繁进行数字格式化的应用程序非常有益。

## JEP 178: 静态链接的 JNI 库

该特性支持静态链接 JNI（Java Native Interface）库，使得 JNI 库可以在应用程序启动时一次性加载，而不是在每次调用时动态加载。这提高了 JNI 调用的性能。

## JEP 180: 使用平衡树处理频繁的 HashMap 碰撞

该特性改进了 `HashMap` 的实现，当发生频繁的碰撞时，使用平衡树而不是链表来存储元素。这提高了 `HashMap` 在高碰撞情况下的性能。

## JEP 184: HTTP URL 访问权限

该特性增强了 Java 对 HTTP URL 的访问权限控制，使得开发者可以更细粒度地控制对 HTTP 资源的访问。这对于安全敏感的应用程序非常重要。

## JEP 185: 限制外部内存访问

限制对堆外内存（off-heap memory）的访问，增强安全性。通过安全检查机制防止不受信任的代码直接操作本地内存，减少内存安全风险。

---

## 其他新特性（非 JEP）

Java 8 还包含大量非 JEP 的改进，以下列出对开发者最实用的特性：

### 语言特性

#### Method References（方法引用）

方法引用提供了一种更简洁的方式来引用已命名的方法，是 Lambda 表达式的语法糖。

```java
// 方法引用示例
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
names.forEach(System.out::println);  // 方法引用

// 等价于 Lambda
names.forEach(name -> System.out.println(name));

// 静态方法引用
List<Integer> nums = Arrays.asList(3, 1, 4, 1, 5);
nums.sort(Integer::compareTo);
```

#### Improved Type Inference（改进的类型推断）

编译器类型推断能力增强，减少了显式类型声明的需要。

### 集合与流

#### Stream API（`java.util.stream`）

Stream API 提供了函数式风格的集合元素操作，支持顺序和并行的 map-reduce 变换。

```java
// Stream API 示例
List<String> filtered = names.stream()
    .filter(name -> name.startsWith("A"))
    .map(String::toUpperCase)
    .sorted()
    .collect(Collectors.toList());

// 并行流
long count = names.parallelStream()
    .filter(name -> name.length() > 3)
    .count();
```

#### Parallel Array Sorting（并行数组排序）

`Arrays.parallelSort()` 方法使用 Fork/Join 框架进行并行排序。

```java
int[] data = {5, 3, 8, 1, 9, 2};
Arrays.parallelSort(data);
```

#### HashMap Performance Improvement（HashMap 性能改进）

HashMap 在处理频繁碰撞时使用平衡树替代链表，提高了最坏情况下的性能（O(log n) vs O(n)）。

### 核心 API

#### Base64 Encoding/Decoding（Base64 编解码）

`java.util.Base64` 提供了标准的 Base64 编解码支持。

```java
String encoded = Base64.getEncoder().encodeToString("Hello".getBytes());
byte[] decoded = Base64.getDecoder().decode(encoded);
```

#### Unsigned Arithmetic Support（无符号算术支持）

`Integer` 和 `Long` 新增无符号算术操作方法。

```java
int unsigned = Integer.parseUnsignedInt("4294967295");  // 2^32 - 1
String hex = Integer.toUnsignedString(0xFFFFFFFF);       // "4294967295"
```

#### New Date-Time Package（新日期时间包）

`java.time` 包提供了现代的日期时间处理 API，解决了旧 API 的线程安全和设计问题。

```java
LocalDate today = LocalDate.now();
LocalDateTime now = LocalDateTime.now();
ZonedDateTime zoned = ZonedDateTime.now(ZoneId.of("Asia/Shanghai"));
Duration duration = Duration.between(startTime, endTime);
Period period = Period.between(startDate, endDate);
```

### 并发

#### StampedLock（ stamped 锁）

`java.util.concurrent.locks.StampedLock` 提供了三种模式的锁：写锁、读锁和乐观读。

```java
StampedLock lock = new StampedLock();

// 乐观读
long stamp = lock.tryOptimisticRead();
// ... 读取数据 ...
if (!lock.validate(stamp)) {
    stamp = lock.readLock();  // 升级为悲观读锁
    try { /* 重新读取 */ } finally { lock.unlockRead(stamp); }
}

// 写锁
long ws = lock.writeLock();
try { /* 修改数据 */ } finally { lock.unlockWrite(ws); }
```

#### ConcurrentHashMap Aggregate Operations（ConcurrentHashMap 聚合操作）

ConcurrentHashMap 新增 stream 和 Lambda 批量操作方法。

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.forEach(10, (k, v) -> System.out.println(k + "=" + v));
map.search(10, (k, v) -> v > 100 ? k : null);
```

#### ForkJoinPool Common Pool（共享线程池）

新增公共 ForkJoinPool 实例，用于并行流和 CompletableFuture。

### 安全

#### TLS 1.2 Enabled by Default（默认启用 TLS 1.2）

客户端默认启用 TLS 1.2 协议。

#### AEAD Algorithms（AEAD 算法）

支持 AES/GCM/NoPadding 加密套件。

```java
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
GCMParameterSpec spec = new GCMParameterSpec(128, iv);
cipher.init(Cipher.ENCRYPT_MODE, secretKey, spec);
```

#### SHA-224 Message Digests（SHA-224 摘要）

支持 SHA-224 消息摘要算法。

#### PKIXRevocationChecker（证书吊销检查器）

新增 `java.security.cert.PKIXRevocationChecker` 类，用于配置 X.509 证书吊销检查。

### JavaFX

#### Modena Theme（新默认主题）

JavaFX 默认视觉主题从 Caspian 更换为 Modena。

#### SwingNode（嵌入 Swing 内容）

`SwingNode` 允许在 JavaFX 应用中嵌入 Swing 组件。

```java
SwingNode swingNode = new SwingNode();
SwingUtilities.invokeLater(() -> {
    swingNode.setContent(new JButton("Swing Button"));
});
```

#### New UI Controls（新 UI 控件）

新增 `DatePicker` 和 `TreeTableView` 控件。

#### 3D Graphics（3D 图形）

支持 `Shape3D`（Box、Cylinder、Sphere、MeshView）、`SubScene`、材质、灯光等 3D 图形功能。

#### Hi-DPI Display Support（高分屏支持）

JavaFX 支持高分辨率显示器。

### 工具

#### jjs 命令行工具

`jjs` 命令行工具用于调用 Nashorn JavaScript 引擎。

```bash
echo 'print("Hello from Nashorn!")' | jjs
jjs script.js
```

#### jdeps 依赖分析工具

`jdeps` 用于分析类文件的依赖关系。

```bash
jdeps myapp.jar  # 显示依赖关系
jdeps -verbose:package myapp.jar  # 按包级别显示
```

#### javac -parameters（参数名保留）

`-parameters` 选项在编译时保留方法参数名，供反射 API 使用。

```bash
javac -parameters MyClass.java
```

#### javac -h（生成原生头文件）

`-h` 选项自动生成 JNI 头文件，取代了 `javah` 工具。

### Javadoc

#### DocTree API

DocTree API 允许将 Javadoc 注释作为抽象语法树遍历。

#### -Xdoclint（文档检查）

`-Xdoclint` 默认启用，检查无效 HTML 和可访问性问题。

### 国际化

#### Unicode 6.2.0 Support

支持 Unicode 6.2.0 标准。

#### Unicode CLDR Data

采用 Unicode CLDR 数据，可通过 `java.locale.providers` 系统属性配置。

### IO 与 NIO

#### EventPortSelectorProvider

Solaris 上基于事件端口机制的新 `SelectorProvider`。

#### String Encoding/Decoding Performance

`String(byte[], *)` 构造器和 `getBytes()` 方法的编解码性能提升。

### HotSpot VM

#### AES Hardware Intrinsics（AES 硬件加速）

Intel Westmere 2010+ 处理器支持 AES-NI 指令加速。

```bash
java -XX:+UseAES -XX:+UseAESIntrinsics MyApp
```

#### PermGen Removal（永久代移除）

类的元数据迁移到本地内存（Metaspace），避免 Permanent Generation 内存溢出。

### JDBC

#### JDBC-ODBC Bridge Removed

移除了 JDBC-ODBC 桥接器。

#### JDBC 4.2

引入 JDBC 4.2 新特性。

---

← [返回 Java 版本特性](../README.md)
<!-- TODO: 拆分候选 (712 行 / 57 个 H2，超 500+8 阈值） -->
