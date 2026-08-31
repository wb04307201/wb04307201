<!--
module:
  parent: java
  slug: java/version/java-15
  type: article
  category: 主模块子文章
  summary: Java 15：14 个 JEP，含密封类预览、EdDSA 签名、ZGC/Shenandoah 正式版、Text Blocks 正式版
  depth: ⭐⭐⭐
-->

# Java 15

## 引言：变更说明

Java 15 是 14 个 JEP 的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

### 相关阅读

← [Java 14](../java-14/README.md) · [Java 16](../java-16/README.md)

---

- **JEP 339**: Edwards-Curve 数字签名算法 (EdDSA)
- **JEP 360**: 密封类（预览）
- **JEP 371**: 隐藏类
- **JEP 372**: 移除 Nashorn JavaScript 引擎
- **JEP 373**: 重新实现遗留的 DatagramSocket API
- **JEP 374**: 禁用并弃用偏向锁
- **JEP 375**: 针对 instanceof 的模式匹配（第二次预览）
- **JEP 377**: ZGC：可扩展的低延迟垃圾收集器
- **JEP 378**: 文本块
- **JEP 379**: Shenandoah：低暂停时间垃圾收集器
- **JEP 381**: 移除 Solaris 和 SPARC 端口
- **JEP 383**: 外部内存访问 API（第二次孵化）
- **JEP 384**: 记录类（第二次预览）
- **JEP 385**: 弃用 RMI 激活以供移除

## JEP 339: Edwards-Curve 数字签名算法 (EdDSA)

EdDSA 是一种现代数字签名算法，基于椭圆曲线密码学。它提供了更高的安全性和性能，并且比传统的 ECDSA 算法更简单和更易于实现。Java 15 引入了对 EdDSA 的支持，使得开发者可以更方便地使用这种先进的签名算法来保护数据的安全。

```java
// 生成 EdDSA 密钥对
KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("Ed25519");
KeyPair keyPair = keyPairGenerator.generateKeyPair();

// 使用私钥进行签名
Signature signature = Signature.getInstance("Ed25519");
signature.initSign(keyPair.getPrivate());
byte[] dataToSign = "Hello, World!".getBytes();
signature.update(dataToSign);
byte[] signatureBytes = signature.sign();

// 使用公钥验证签名
signature.initVerify(keyPair.getPublic());
signature.update(dataToSign);
boolean isValid = signature.verify(signatureBytes);
System.out.println("Signature is valid: " + isValid);
```

## JEP 360: 密封类（预览）

密封类是一种新的类声明机制，它允许开发者限制类的继承层次结构。通过密封类，可以明确指定哪些类可以继承当前类，从而提供更好的封装性和安全性。密封类适用于需要严格控制子类行为的场景，例如实现特定的设计模式或框架。

```java
// 定义一个密封类
public sealed class Animal permits Dog, Cat {
    // 类体
}

// 密封类的子类
public final class Dog extends Animal {
    // 类体
}

public final class Cat extends Animal {
    // 类体
}
```

## JEP 371: 隐藏类

隐藏类是一种只能在运行时动态生成的类，它们不能被直接引用或发现。隐藏类适用于需要动态生成代码的场景，例如框架和库的实现。通过隐藏类，可以提高代码的灵活性和性能，同时减少对静态类结构的依赖。

```java
// 使用 Lookup 类创建隐藏类
Lookup lookup = MethodHandles.lookup();
Class<?> hiddenClass = lookup.defineHiddenClass(new byte[]{...}, true).lookupClass();

// 隐藏类不能被直接引用
// 只能通过反射或其他动态机制来使用
```

## JEP 372: 移除 Nashorn JavaScript 引擎

Nashorn 是 Java 8 引入的一个 JavaScript 引擎，用于在 Java 应用程序中执行 JavaScript 代码。随着 GraalVM JavaScript 引擎的成熟和普及，Nashorn 引擎的使用逐渐减少。Java 15 决定移除 Nashorn JavaScript 引擎，以减少 JDK 的维护负担和代码复杂度。

## JEP 373: 重新实现遗留的 DatagramSocket API

遗留的 DatagramSocket API 存在一些设计和实现上的问题，例如线程安全性、性能和可扩展性等方面的不足。Java 15 对 DatagramSocket API 进行了重新实现，解决了这些问题，提高了 UDP 网络编程的可靠性和性能。

```java
// 使用重新实现的 DatagramSocket API
try (DatagramSocket socket = new DatagramSocket()) {
    byte[] sendData = "Hello, World!".getBytes();
    InetAddress address = InetAddress.getByName("localhost");
    DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length, address, 9876);
    socket.send(sendPacket);

    byte[] receiveData = new byte[1024];
    DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length);
    socket.receive(receivePacket);
    String receivedString = new String(receivePacket.getData(), 0, receivePacket.getLength());
    System.out.println("Received: " + receivedString);
} catch (IOException e) {
    e.printStackTrace();
}
```

## JEP 374: 禁用并弃用偏向锁

偏向锁是一种在单线程环境下提高锁性能的机制。然而，随着多核处理器的普及和并发编程的广泛应用，偏向锁的优势逐渐减弱，并且在某些情况下可能会导致性能下降。Java 15 决定禁用并弃用偏向锁，以简化锁的实现和提高并发性能。

## JEP 375: 针对 instanceof 的模式匹配（第二次预览）

模式匹配是一种强大的编程特性，它允许开发者根据对象的类型和结构进行更灵活的条件判断。Java 15 继续完善针对 instanceof 的模式匹配功能，提供了第二次预览版本。通过模式匹配，可以简化代码，提高可读性和可维护性。

```java
Object obj = "Hello";
if (obj instanceof String s) {
    System.out.println("The length of the string is: " + s.length());
}
```

## JEP 377: ZGC：可扩展的低延迟垃圾收集器

ZGC 是一种新型的垃圾收集器，旨在实现可扩展的低延迟垃圾收集。它适用于大内存堆和高并发应用程序，能够在不影响应用程序性能的情况下进行高效的垃圾回收。Java 15 对 ZGC 进行了进一步的优化和改进，提高了其稳定性和性能。

```java
// 启动 JVM 时指定使用 ZGC
// java -XX:+UseZGC -Xmx4g MyApplication
```

## JEP 378: 文本块

文本块是一种多行字符串字面量的表示方式，它使得编写包含多行文本的代码更加简洁和易读。文本块使用三个双引号（"""）作为起始和结束标记，可以自动处理换行符和缩进，减少了字符串拼接和转义字符的使用。

```java
String html = """
    <html>
        <body>
            <p>Hello, World!</p>
        </body>
    </html>
    """;
System.out.println(html);
```

## JEP 379: Shenandoah：低暂停时间垃圾收集器

Shenandoah 是一种低暂停时间的垃圾收集器，它通过并发标记和并发压缩等机制，减少了垃圾回收对应用程序的停顿时间。Java 15 对 Shenandoah 垃圾收集器进行了进一步的优化和改进，提高了其性能和稳定性。

```java
// 启动 JVM 时指定使用 Shenandoah
// java -XX:+UseShenandoahGC -Xmx4g MyApplication
```

## JEP 381: 移除 Solaris 和 SPARC 端口

随着计算机硬件架构的发展，Solaris 和 SPARC 架构的使用逐渐减少。为了简化 JDK 的开发和维护，Java 15 决定移除对 Solaris 和 SPARC 端口的支持。这意味着从 Java 15 开始，JDK 将不再提供适用于 Solaris 操作系统和 SPARC 处理器的版本。

## JEP 383: 外部内存访问 API（第二次孵化）

外部内存访问 API 提供了一种高效的方式来访问 Java 堆之外的内存，例如本地内存和共享内存。这对于需要与本地代码或其他进程进行交互的应用程序非常有用，例如高性能计算、数据库连接和图形处理等领域。Java 15 对外部内存访问 API 进行了第二次孵化，进一步完善了其功能和性能。

```java
// 使用外部内存访问 API
MemorySegment segment = MemorySegment.allocateNative(1024);
MemoryAccess.setIntAtIndex(segment, 0, 42);
int value = MemoryAccess.getIntAtIndex(segment, 0);
System.out.println("Value: " + value);
```

## JEP 384: 记录类（第二次预览）

记录类是一种简洁的数据载体类，它自动提供了常见的方法，如构造函数、访问器方法、equals()、hashCode() 和 toString() 等。记录类适用于需要表示简单数据结构的场景，减少了样板代码的编写，提高了代码的可读性和可维护性。Java 15 对记录类进行了第二次预览，进一步完善了其功能和语法。

```java
// 定义一个记录类
public record Person(String name, int age) {
    // 记录类的类体可以为空，或者包含静态方法、静态初始化块等
}

// 使用记录类
Person person = new Person("Alice", 30);
System.out.println(person.name()); // 访问器方法
System.out.println(person.age());
System.out.println(person); // toString() 方法
```

## JEP 385: 弃用 RMI 激活以供移除

RMI（Remote Method Invocation）激活是一种用于在分布式系统中启动和管理远程对象的技术。然而，随着现代分布式架构的发展，RMI 激活的使用逐渐减少，并且存在一些安全性和性能方面的问题。Java 15 决定弃用 RMI 激活功能，为未来的移除做准备。

---

## 其他新特性（非 JEP）

Java 15 还包含多项非 JEP 的改进，以下列出对开发者最实用的特性：

### 核心库

#### CharSequence.isEmpty() 默认方法

`CharSequence` 新增默认 `isEmpty()` 方法，测试字符序列是否为空。可用作方法引用。

#### Unicode 13.0 支持

`Character` 支持 Unicode 13.0（5,930 个新字符，总计 143,859；4 种新文字；55 个新表情符号）。

#### 优化的空子串处理

`String.substring`、`stripLeading` 和 `stripTrailing` 不再冗余创建新的空 `String`。

#### Lookup::defineClass 链接类

`Lookup::defineClass` 现在在返回前实际链接类，符合规范说明。

#### 序列化过滤器处理改进

`ObjectInputStream.setObjectInputFilter` 现在必须在从流中读取任何对象之前调用。

#### TreeMap 方法专门化实现

`TreeMap` 现在覆盖 `putIfAbsent`、`computeIfAbsent`、`computeIfPresent`、`compute` 和 `merge` 以获得更好性能。

#### SO_INCOMING_NAPI_ID 套接字选项

新增 Linux 特定套接字选项 `SO_INCOMING_NAPI_ID`，添加到 `jdk.net.ExtendedSocketOptions`。允许查询底层设备队列的 NAPI ID。

#### HttpClient 不再覆盖 SSLContext 默认协议

当未显式提供 `SSLParameters` 时，`HttpClient` 在 TLS 握手期间使用 `SSLContext` 的默认协议集。

#### DecimalFormat 货币分组分隔符

`DecimalFormat`/`DecimalFormatSymbols` 现在可以处理货币值的分组分隔符。

#### localizedBy() 修复

`DateTimeFormatter.localizedBy(Locale)` 现在正确地尊重指定语言环境的默认值。

### 安全

#### jarsigner 撤销检查

`jarsigner` 新增 `-revCheck` 选项启用证书撤销检查。

#### 弱算法警告

`keytool` 和 `jarsigner` 使用弱加密算法时发出警告。本版本对 SHA-1 和 1024 位 RSA/DSA 密钥发出警告。

#### SunJCE SHA-3 Hmac 算法

SunJCE 现支持 `HmacSHA3-224`、`HmacSHA3-256`、`HmacSHA3-384` 和 `HmacSHA3-512`。

#### TLS 签名方案系统属性

新增 `jdk.tls.client.SignatureSchemes` 和 `jdk.tls.server.SignatureSchemes` 自定义 TLS 签名方案。

#### TLS 1.3 certificate_authorities 扩展

支持可选的 TLS 1.3 `certificate_authorities` 扩展。

#### SSLEngine 默认服务器角色

`SSLEngine` 现在默认为服务器模式（JDK 11+ 之前是客户端模式）。

#### Kerberos canonicalize 支持

`krb5.conf` 中的 `canonicalize` 标志现在受支持。

### HotSpot / JVM

#### 字段布局计算变更

更积极的优化以避免实例中未使用的间隙。可通过 `-XX:-UseEmptySlotsInSupers` 禁用。

####  Helpful NPE 消息默认启用

JEP 358 的有帮助的 `NullPointerException` 消息现在默认打印，显示 NPE 发生位置的代码片段。

#### 偏向锁禁用和弃用

偏向锁默认禁用。`UseBiasedLocking` 及相关标志弃用。

#### G1 堆区域大小改进的人体工程学

G1 堆区域大小计算更改为默认返回更大的区域。区域大小现在向上舍入到最近的 2 的幂。

#### jhsdb debugd 新选项

三个新选项：`--rmiport`、`--registryport`、`--hostname`。

### 工具

#### jcmd GC.heap_dump gz 选项

新整数选项 `gz` 启用堆转储的 gzip 压缩。值为压缩级别（1=最快到 9=最佳压缩）。

```bash
jcmd <pid> GC.heap_dump filename=/tmp/heap.hprof gz=1
```

#### jstatd -r 选项

`jstatd` 新增 `-r <port>` 选项指定 RMI 连接器端口。

#### jpackage macOS 公证支持

`jpackage` 现在可以在 macOS 上创建适用于公证的包。

### 国际化

#### CLDR v37 支持

语言环境数据升级到 Unicode CLDR v37。

### 移除

| 移除项 | 详情 |
|--------|------|
| Nashorn JavaScript 引擎 | Nashorn 脚本引擎、API 和 `jjs` 工具已移除 |
| RMI 静态存根编译器 (`rmic`) | 自 JDK 13 弃用待移除，现移除 |
| Solaris 特定 SO_FLOW_SLA 套接字选项 | 随 Solaris 端口移除 |

---

← [返回 Java 版本特性](../README.md)