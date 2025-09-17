# Java 11

- **JEP 181**: 基于嵌套的访问控制
- **JEP 309**: 动态类文件常量
- **JEP 315**: 改进 Aarch64 内联函数
- **JEP 318**: Epsilon：无操作垃圾收集器
- **JEP 320**: 移除 Java EE 和 CORBA 模块
- **JEP 321**: HTTP Client（标准化）
- **JEP 323**: Lambda 参数的局部变量语法
- **JEP 324**: 使用 Curve25519 和 Curve448 进行密钥协商
- **JEP 327**: Unicode 10
- **JEP 328**: 飞行记录器
- **JEP 329**: ChaCha20 和 Poly1305 加密算法
- **JEP 330**: 启动单文件源代码程序
- **JEP 331**: 低开销堆分析
- **JEP 332**: 传输层安全（TLS）1.3
- **JEP 333**: ZGC：可扩展的低延迟垃圾收集器（实验性）
- **JEP 335**: 弃用 Nashorn JavaScript 引擎
- **JEP 336**: 弃用 Pack200 工具和 API

## JEP 181: 基于嵌套的访问控制

基于嵌套的访问控制允许在嵌套类和宿主类之间更灵活地访问私有成员。在 Java 11 之前，嵌套类（内部类、局部类和匿名类）对宿主类的私有成员的访问是通过合成访问方法实现的，这可能会在字节码层面暴露一些不必要的细节。基于嵌套的访问控制通过在类文件结构中引入嵌套成员访问机制，使得这种访问更加安全和直接。

例如，在一个内部类中访问宿主类的私有字段时，不再需要通过合成访问方法，而是直接在类文件中表明这种嵌套关系，从而简化了访问控制模型，提高了代码的安全性和可维护性。

## JEP 309: 动态类文件常量

动态类文件常量允许在运行时动态生成类文件中的常量。在 Java 11 之前，类文件中的常量池是在编译时确定的，这限制了一些动态代码生成和优化的场景。通过动态类文件常量，开发者可以在运行时根据需要动态地创建和修改类文件中的常量，从而为更灵活的代码生成和优化提供了支持。

例如，在一些动态代理框架中，可以根据不同的请求动态生成不同的类文件常量，从而实现更高效的代理逻辑。

## JEP 315: 改进 Aarch64 内联函数

Aarch64 是 ARM 架构的 64 位版本，广泛应用于移动设备和服务器领域。该特性改进了 Java 虚拟机（JVM）在 Aarch64 架构上的内联函数实现，以提高性能。内联函数是一种编译器优化技术，它将函数调用替换为函数体本身，从而减少函数调用的开销。

通过改进 Aarch64 内联函数，JVM 可以更好地利用 Aarch64 架构的硬件特性，提高代码的执行效率，特别是在一些计算密集型的应用程序中。

## JEP 318: Epsilon：无操作垃圾收集器

Epsilon 是一种无操作垃圾收集器，它不执行实际的垃圾回收操作。该特性主要用于性能测试和内存压力测试等场景。在传统的垃圾收集器中，垃圾回收过程会引入一定的停顿时间和性能开销，这可能会影响性能测试的准确性。

使用 Epsilon 垃圾收集器，可以避免垃圾回收对性能测试的干扰，从而更准确地评估应用程序的性能。例如，在测试应用程序的内存使用情况时，可以使用 Epsilon 垃圾收集器来观察应用程序在没有垃圾回收的情况下的内存增长趋势。

## JEP 320: 移除 Java EE 和 CORBA 模块

随着云计算和微服务架构的兴起，Java EE 和 CORBA 技术逐渐被新的技术所取代。为了简化 JDK 的体积和维护成本，Java 11 决定移除 Java EE 和 CORBA 模块。这些模块包括 JavaBeans Activation Framework（JAF）、Java API for XML Processing（JAXP）、Java API for XML Web Services（JAX-WS）、Java Management Extensions（JMX）、Java Transaction API（JTA）和 Common Object Request Broker Architecture（CORBA）等。

移除这些模块后，JDK 将更加专注于核心的 Java 语言和平台功能，同时鼓励开发者使用其他更适合现代应用开发的技术和框架。

## JEP 321: HTTP Client（标准化）

Java 11 对 HTTP Client API 进行了标准化，使其成为 Java 标准库的一部分。在之前的版本中，HTTP Client API 是作为孵化器模块提供的，而 Java 11 将其正式纳入标准库，并提供了更稳定和完善的 API。

新的 HTTP Client API 支持 HTTP/2 协议，提供了更简洁的 API 设计和更好的性能。开发者可以使用它来发送 HTTP 请求、处理响应、管理连接等，例如：

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class HttpClientExample {
    public static void main(String[] args) throws Exception {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://example.com"))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        System.out.println(response.statusCode());
        System.out.println(response.body());
    }
}
```

## JEP 323: Lambda 参数的局部变量语法

该特性允许在 Lambda 表达式中使用 `var` 关键字来声明局部变量，从而使 Lambda 表达式的代码更加简洁和易读。在 Java 11 之前，Lambda 表达式中的参数类型必须显式声明，这可能会导致代码冗长。

例如，使用 `var` 关键字可以简化 Lambda 表达式中的参数声明：

```java
import java.util.Arrays;
import java.util.List;

public class LambdaVarExample {
    public static void main(String[] args) {
        List<String> list = Arrays.asList("apple", "banana", "orange");
        list.forEach((var fruit) -> System.out.println(fruit));
    }
}
```

## JEP 324: 使用 Curve25519 和 Curve448 进行密钥协商

Curve25519 和 Curve448 是两种高效的椭圆曲线密码算法，它们提供了更高的安全性和性能。该特性在 Java 的加密库中引入了对 Curve25519 和 Curve448 的支持，使得开发者可以使用这些先进的密码算法进行密钥协商和加密通信。

例如，使用 Curve25519 进行密钥协商：

```java
import javax.crypto.KeyAgreement;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.spec.ECGenParameterSpec;

public class Curve25519Example {
    public static void main(String[] args) throws Exception {
        // 生成 Curve25519 密钥对
        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("XDH");
        keyPairGenerator.initialize(new ECGenParameterSpec("X25519"));
        KeyPair keyPair1 = keyPairGenerator.generateKeyPair();
        KeyPair keyPair2 = keyPairGenerator.generateKeyPair();

        PrivateKey privateKey1 = keyPair1.getPrivate();
        PublicKey publicKey2 = keyPair2.getPublic();

        // 密钥协商
        KeyAgreement keyAgreement1 = KeyAgreement.getInstance("XDH");
        keyAgreement1.init(privateKey1);
        keyAgreement1.doPhase(publicKey2, true);

        byte[] sharedSecret1 = keyAgreement1.generateSecret();
        System.out.println("Shared secret 1: " + bytesToHex(sharedSecret1));
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
```

## JEP 327: Unicode 10

Unicode 10 是 Unicode 标准的第十个版本，它引入了新的字符、表情符号和符号。Java 11 支持 Unicode 10 标准，使得开发者可以在 Java 应用程序中使用最新的 Unicode 字符。

例如，可以使用 Unicode 10 中的新表情符号：

```java
public class Unicode10Example {
    public static void main(String[] args) {
        String faceWithSymbolsOnMouth = "\uD83E\uDD2C"; // 🤬
        System.out.println("Face with symbols on mouth: " + faceWithSymbolsOnMouth);
    }
}
```

## JEP 328: 飞行记录器

Java 飞行记录器（JFR）是一种用于记录和分析 Java 应用程序性能的工具。Java 11 对 JFR 进行了改进，使其更加易于使用和集成。JFR 可以记录应用程序的运行时信息，如方法调用、线程活动、内存使用等，帮助开发者诊断性能问题和优化应用程序。

例如，可以使用 JFR 记录应用程序的运行时信息，并使用 Java Mission Control（JMC）工具进行分析：

```java
import jdk.jfr.*;
import jdk.jfr.consumer.*;

public class JFRExample {
    @Label("Hello World")
    @Description("A simple JFR event")
    static class HelloWorld extends Event {
        @Label("Message")
        String message;
    }

    public static void main(String[] args) throws Exception {
        // 创建 JFR 录制
        Recording recording = new Recording();
        recording.start();

        // 触发 JFR 事件
        HelloWorld event = new HelloWorld();
        event.message = "Hello, World!";
        event.commit();

        // 停止录制
        recording.stop();

        // 保存录制文件
        recording.dump(Paths.get("jfr_example.jfr"));

        // 分析录制文件（可以使用 JMC 工具）
        // 这里简单打印录制文件信息
        System.out.println("Recording saved to jfr_example.jfr");
    }
}
```

## JEP 329: ChaCha20 和 Poly1305 加密算法

ChaCha20 是一种流密码算法，Poly1305 是一种消息认证码算法。Java 11 在加密库中引入了对 ChaCha20 和 Poly1305 的支持，提供了更高效的加密和认证功能。这些算法在移动设备和低功耗设备上具有较好的性能表现。

例如，使用 ChaCha20-Poly1305 进行加密和解密：

```java
import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.util.Base64;

public class ChaCha20Poly1305Example {
    public static void main(String[] args) throws Exception {
        // 生成密钥
        KeyGenerator keyGenerator = KeyGenerator.getInstance("ChaCha20-Poly1305");
        SecretKey secretKey = keyGenerator.generateKey();

        // 生成初始化向量（IV）
        byte[] iv = new byte[12];
        new SecureRandom().nextBytes(iv);

        // 加密
        Cipher cipher = Cipher.getInstance("ChaCha20-Poly1305");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, new IvParameterSpec(iv));
        byte[] plaintext = "Hello, World!".getBytes();
        byte[] ciphertext = cipher.doFinal(plaintext);

        System.out.println("Ciphertext: " + Base64.getEncoder().encodeToString(ciphertext));

        // 解密
        cipher.init(Cipher.DECRYPT_MODE, secretKey, new IvParameterSpec(iv));
        byte[] decryptedText = cipher.doFinal(ciphertext);
        System.out.println("Decrypted text: " + new String(decryptedText));
    }
}
```

## JEP 330: 启动单文件源代码程序

Java 11 允许直接运行单个 Java 源代码文件，而无需先编译成类文件。这简化了小型 Java 程序的开发和测试过程，提高了开发效率。例如，有一个名为 `HelloWorld.java` 的文件，内容如下：

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

在 Java 11 中，可以直接使用以下命令运行该文件：

```bash
java HelloWorld.java
```

## JEP 331: 低开销堆分析

低开销堆分析允许开发者在不显著影响应用程序性能的情况下分析堆内存的使用情况。该特性通过与垃圾收集器集成，提供了实时的堆内存信息，帮助开发者诊断内存泄漏和优化内存使用。

例如，可以使用低开销堆分析工具来获取堆内存的统计信息，如对象数量、内存占用等，从而找出内存泄漏的源头。

## JEP 332: 传输层安全（TLS）1.3

TLS 1.3 是传输层安全协议的最新版本，它提供了更高的安全性和性能。Java 11 支持 TLS 1.3 协议，使得 Java 应用程序可以使用更安全的加密通信。TLS 1.3 简化了握手过程，减少了通信延迟，同时提供了更强的加密算法支持。

例如，在配置 Java 的 SSL 上下文时，可以启用 TLS 1.3 协议：

```java
import javax.net.ssl.*;
import java.security.*;

public class TLS13Example {
    public static void main(String[] args) throws Exception {
        // 创建 SSL 上下文
        SSLContext sslContext = SSLContext.getInstance("TLS");

        // 初始化 SSL 上下文（这里省略密钥和证书的配置）
        // 实际应用中需要配置合适的密钥和证书
        sslContext.init(null, null, null);

        // 获取 SSL 套接字工厂
        SSLSocketFactory sslSocketFactory = sslContext.getSocketFactory();

        // 创建 SSL 套接字并连接到服务器（这里只是示例，实际需要指定服务器地址和端口）
        // SSLSocket socket = (SSLSocket) sslSocketFactory.createSocket("example.com", 443);

        // 配置 SSL 套接字使用 TLS 1.3 协议
        // socket.setEnabledProtocols(new String[]{"TLSv1.3"});

        System.out.println("TLS 1.3 support is available");
    }
}
```

## JEP 333: ZGC：可扩展的低延迟垃圾收集器（实验性）

ZGC 是一种可扩展的低延迟垃圾收集器，旨在满足大规模应用程序对低延迟垃圾收集的需求。它采用了并发标记、并发整理和负载均衡等技术，能够在多核处理器上实现高效的垃圾收集，同时将垃圾收集的停顿时间控制在毫秒级别。

由于 ZGC 在 Java 11 中是实验性特性，需要在启动 JVM 时使用特定的参数来启用，例如：

```bash
java -XX:+UnlockExperimentalVMOptions -XX:+UseZGC YourApplication