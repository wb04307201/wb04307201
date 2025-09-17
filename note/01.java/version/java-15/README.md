# Java 15

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