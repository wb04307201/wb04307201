<!--
module:
  parent: java
  slug: java/version/java-13
  type: article
  category: 主模块子文章
  summary: Java 13：5 个 JEP，含动态 CDS 归档、ZGC 释放未用内存、Text Blocks 预览
  depth: ⭐
-->

# Java 13

## 引言：变更说明

Java 13 是 5 个 JEP 的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

### 相关阅读

← [Java 12](../java-12/README.md) · [Java 14](../java-14/README.md) · [Java 全部版本](../README.md)

---

- **JEP 350**: 动态 CDS 归档
- **JEP 351**: ZGC：释放未使用的内存
- **JEP 353**: 重新实现传统 Socket API
- **JEP 354**: Switch 表达式（预览）
- **JEP 355**: 文本块（预览）

## JEP 350: 动态 CDS 归档

动态类数据共享（Class Data Sharing, CDS）归档允许在运行时动态生成 CDS 归档文件。CDS 功能可以将一些常用的类预加载到共享内存中，这样多个 Java 进程可以共享这些类，从而减少启动时间和内存占用。在 Java 13 之前，CDS 归档文件需要在应用程序启动前静态生成。而动态 CDS 归档特性使得在应用程序运行过程中也可以创建归档文件，提高了 CDS 的灵活性和实用性。

例如，开发者可以在应用程序启动后，通过特定的 API 触发动态 CDS 归档的创建，将当前加载的类归档起来，以便后续的启动可以共享这些类。

## JEP 351: ZGC：释放未使用的内存

Z Garbage Collector（ZGC）是 Java 11 引入的一种低延迟垃圾回收器。在 Java 13 中，ZGC 增加了释放未使用的内存的功能。这意味着 ZGC 可以将不再使用的堆内存归还给操作系统，从而减少应用程序的内存占用。

在之前的版本中，即使应用程序不再需要大量的堆内存，ZGC 也会保留这些内存，导致内存占用较高。而通过释放未使用的内存功能，ZGC 可以根据应用程序的实际需求动态调整内存使用，提高内存资源的利用率。

```java
// 以下代码示例展示了如何通过 JVM 参数启用 ZGC 并观察内存释放情况
// 启动 Java 应用程序时添加以下参数
// -XX:+UseZGC -Xms1G -Xmx4G
// 在应用程序运行过程中，当内存使用量减少时，ZGC 会自动将未使用的内存归还给操作系统
```

## JEP 353: 重新实现传统 Socket API

传统的 Java Socket API 是基于 Unix Network Programming, Volume 1: The Sockets Networking API（UNIX 网络编程，卷 1：套接字联网 API）实现的，已经存在了很长时间。然而，随着时间推移，该实现暴露出一些问题，例如代码复杂、难以维护和扩展等。

Java 13 重新实现了传统的 Socket API，将其从基于 Unix 的实现迁移到基于 Java NIO（New I/O）的实现。新的实现简化了代码结构，提高了可维护性和性能，并且更好地支持了现代网络协议和特性。

```java
// 传统 Socket API 示例
try (Socket socket = new Socket("example.com", 80);
     PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
     BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {
    out.println("GET / HTTP/1.1");
    out.println("Host: example.com");
    out.println();

    String responseLine;
    while ((responseLine = in.readLine()) != null) {
        System.out.println(responseLine);
    }
} catch (IOException e) {
    e.printStackTrace();
}

// 新的 Socket API 实现方式在底层有所变化，但对外提供的接口基本保持一致，开发者可以无缝迁移
```

## JEP 354: Switch 表达式（预览）

Switch 表达式是对传统 Switch 语句的扩展和改进。在 Java 13 中，Switch 表达式作为预览特性引入，它提供了更简洁、更灵活的语法来处理多分支情况。

传统的 Switch 语句需要使用 `break` 语句来避免穿透（fall - through），而 Switch 表达式则通过箭头语法（`->`）和表达式返回值来简化代码。Switch 表达式可以返回值，这使得它可以更方便地用在赋值语句或方法调用中。

```java
// 传统 Switch 语句示例
int day = 3;
String dayType;
switch (day) {
    case 1:
    case 2:
    case 3:
    case 4:
    case 5:
        dayType = "Weekday";
        break;
    case 6:
    case 7:
        dayType = "Weekend";
        break;
    default:
        dayType = "Invalid day";
}
System.out.println(dayType);

// Switch 表达式示例（预览特性，需要启用预览功能）
int day = 3;
String dayType = switch (day) {
    case 1, 2, 3, 4, 5 -> "Weekday";
    case 6, 7 -> "Weekend";
    default -> "Invalid day";
};
System.out.println(dayType);
```

## JEP 355: 文本块（预览）

文本块是 Java 13 中引入的另一个预览特性，旨在简化多行字符串的编写。在之前的 Java 版本中，编写多行字符串需要使用转义字符和字符串连接操作，代码可读性较差。

文本块使用三引号（`"""`）来定义多行字符串，使得代码更加简洁和易读。文本块会自动处理换行符和缩进，减少了手动处理的麻烦。

```java
// 传统多行字符串编写方式
String html = "<html>\n" +
              "    <body>\n" +
              "        <p>Hello, world</p>\n" +
              "    </body>\n" +
              "</html>\n";
System.out.println(html);

// 文本块示例（预览特性，需要启用预览功能）
String html = """
              <html>
                  <body>
                      <p>Hello, world</p>
                  </body>
              </html>
              """;
System.out.println(html);
```

---

## 其他新特性（非 JEP）

Java 13 还包含多项非 JEP 的改进，以下列出对开发者最实用的特性：

### 核心库

#### Unicode 12.1 支持

`Character` 类支持 Unicode 12.1（137,928 个字符、150 种文字、61 个新表情符号）。

#### 新日本年号 Reiwa

新增代表令和时代的 `JapaneseEra` 实例。可通过 `JapaneseEra.of(3)` 或 `JapaneseEra.valueOf("Reiwa")` 获取。占位名 "NewEra" 已替换为官方名称。

#### FileSystems.newFileSystem(Path, Map) 方法

`FileSystems` 新增三个方法简化文件作为文件系统的使用：`newFileSystem(Path)`、`newFileSystem(Path, Map)`、`newFileSystem(Path, Map, ClassLoader)`。

#### ByteBuffer 批量 get/put 方法

`ByteBuffer` 和其他缓冲类型新增绝对批量 get/put 方法，传输连续字节序列而不影响缓冲区位置。

#### Windows Developer Mode 符号链接

在 Windows 上，`Files.createSymbolicLink` 现在可以在进程未提升但用户运行在"开发者模式"时创建符号链接。

#### CLDR v35.1 支持

语言环境数据升级到 CLDR v35.1，包括日本新年号令和的本地化显示名称。

#### Runtime trace 方法移除

`Runtime` 中过时的 `traceInstructions(boolean)` 和 `traceMethodCalls(boolean)` 方法移除。它们多个版本已无功能；JVMTI 提供替代。

#### Pre-JDK 1.4 SocketImpl 移除

移除了针对 Java SE 1.3 及更早版本编译的自定义 `SocketImpl` 实现支持。对 Java SE 1.4 或更新版本编译的实现无影响。

### 安全

#### CRL 可配置读取超时

新系统属性 `com.sun.security.crl.readtimeout` 设置 CRL 检索的最大读取超时（秒）。默认 15 秒；0 表示无限超时。

#### keytool -showinfo -tls 命令

新 `keytool -showinfo -tls` 命令显示 TLS 配置信息。

#### SASL 机制限制

新安全属性 `jdk.sasl.disabledMechanisms` 允许禁用 SASL 机制。

#### MS CNG 支持

SunMSCAPI 提供者现在支持读取 CNG 格式的私钥。RSA 和 EC 密钥（CNG 格式）可从 Windows 密钥库加载。

#### SunPKCS11 升级到 PKCS#11 v2.40

新增 AES/GCM/NoPadding 密码、使用 SHA-2 家族的 DSA 签名和 RSASSA-PSS 签名支持。

#### TLS 中的 X25519 和 X448

命名椭圆曲线组 x25519 和 x448 可用于 JSSE 密钥协商（TLS 1.0-1.3）。x25519 是最首选的默认值。

#### 无状态会话恢复

服务端 JSSE 可以使用加密会话票据无状态运行（TLS 1.2 的 RFC 5077，TLS 1.3 的 RFC 8446）。新系统属性：`jdk.tls.client.enableSessionTicketExtension` 和 `jdk.tls.server.enableSessionTicketExtension`。

#### 移除遗留 com.sun.net.ssl 包

内部兼容包移除；自 Java SE 1.4 起标准替代在 `javax.net.ssl` 中可用。

#### Kerberos 跨域转介 (RFC 6806)

Kerberos 客户端支持主体名规范化和跨域转介。默认启用，最多 5 跳转介。

#### 移除的根证书

移除多个过期根证书：T-Systems Deutsche Telekom Root CA 2、DocuSign、Comodo 等。

### HotSpot / JVM

#### -XX:SoftMaxHeapSize 标志

新可管理标志 `-XX:SoftMaxHeapSize=<bytes>`（目前仅 ZGC 有效）。GC 努力不使堆增长超过此大小，除非必须避免 OOM。可通过 `jcmd VM.set_flag` 或 HotSpot MXBean 在运行时调整。

#### ZGC 最大堆大小增加

ZGC 支持的最大堆大小从 4TB 增加到 16TB。

### 工具

#### javadoc 移除旧功能

移除：(1) HTML 4 文档生成（HTML 5 自 JDK 11 起默认），(2) 旧 javadoc API（`com.sun.javadoc`），(3) HTML 框架支持（由搜索功能替代），(4) `--no-module-directories` 选项。

### XML / JAXP

#### DOM 和 SAX 工厂方法支持命名空间

新增 `newDefaultNSInstance()`、`newNSInstance()`、`newNSInstance(String, ClassLoader)` 方法，默认实例化支持命名空间的 DOM 和 SAX 工厂。

### 兼容性变更

| 变更 | 详情 |
|------|------|
| `-XX:+AggressiveOpts` 错误 | JDK 11 弃用，JDK 12 忽略；现在导致 VM 初始化错误 |
| IANA 时区数据 2019b | JDK 13 包含 IANA 时区数据 2019b 版本 |

---

← [返回 Java 版本特性](../README.md)