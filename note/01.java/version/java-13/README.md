# Java 13

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