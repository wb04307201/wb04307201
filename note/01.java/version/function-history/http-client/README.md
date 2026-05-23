# HTTP Client

## 功能描述

HTTP Client 是 Java 11 转正的标准化 HTTP 客户端 API，支持 HTTP/1.1 和 HTTP/2，提供同步和异步请求方式。替代了老旧的 `HttpURLConnection`，支持现代 Web 协议（WebSocket、响应式流），是 Java 生态中最常用的网络编程工具。

## 基本用法（最新，Java 26+）

```java
import java.net.http.*;
import java.net.URI;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;

// 1. 创建 HttpClient（可复用，线程安全）
// Java 26+ 支持 HTTP/3（基于 QUIC 协议），也可选择 HTTP_2 或 HTTP_1_1
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_3)
    .connectTimeout(Duration.ofSeconds(10))
    .followRedirects(HttpClient.Redirect.NORMAL)
    .build();

// 2. 同步 GET 请求
HttpResponse<String> response = client.send(
    HttpRequest.newBuilder()
        .uri(URI.create("https://api.example.com/data"))
        .header("Accept", "application/json")
        .GET()
        .build(),
    HttpResponse.BodyHandlers.ofString()
);
System.out.println(response.statusCode() + ": " + response.body());

// 3. 异步 GET 请求
CompletableFuture<HttpResponse<String>> future = client.sendAsync(
    HttpRequest.newBuilder()
        .uri(URI.create("https://api.example.com/data"))
        .GET()
        .build(),
    HttpResponse.BodyHandlers.ofString()
);
future.thenAccept(r -> System.out.println(r.body()));

// 4. POST JSON 请求
HttpRequest postRequest = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString("{\"name\":\"Alice\"}"))
    .build();
HttpResponse<String> postResponse = client.send(postRequest,
    HttpResponse.BodyHandlers.ofString());

// 5. 文件上传/下载
// 上传文件
HttpRequest uploadRequest = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/upload"))
    .POST(HttpRequest.BodyPublishers.ofFile(Path.of("data.json")))
    .build();

// 下载文件到磁盘
HttpResponse<Path> downloadResponse = client.send(
    HttpRequest.newBuilder()
        .uri(URI.create("https://example.com/file.zip"))
        .GET()
        .build(),
    HttpResponse.BodyHandlers.ofFile(Path.of("download.zip"))
);

// 6. 流式响应处理
HttpResponse<Stream<String>> streamResponse = client.send(
    HttpRequest.newBuilder()
        .uri(URI.create("https://api.example.com/lines"))
        .GET()
        .build(),
    HttpResponse.BodyHandlers.ofLines()
);
streamResponse.body().forEach(System.out::println);

// 7. 并发请求（批量）
List<CompletableFuture<HttpResponse<String>>> futures = List.of(
    "https://api.example.com/a",
    "https://api.example.com/b",
    "https://api.example.com/c"
).stream()
    .map(url -> HttpRequest.newBuilder(URI.create(url)).GET().build())
    .map(req -> client.sendAsync(req, HttpResponse.BodyHandlers.ofString()))
    .toList();
CompletableFuture.allOf(futures.toArray(CompletableFuture[]::new)).join();

// 8. 虚拟线程中使用 HTTP Client（Java 21+）
// HTTP Client 原生支持虚拟线程，在虚拟线程中调用 send() 会自动挂起
Thread.startVirtualThread(() -> {
    HttpResponse<String> r = client.send(request, HttpResponse.BodyHandlers.ofString());
    System.out.println(r.body());
});
```

## 变更历史表

| Java版本  | 新特性/增强内容                                             |
|---------|------------------------------------------------------|
| Java 26 | JEP 517: HTTP Client 支持 HTTP/3 协议                          |
| Java 21 | HttpClient 在虚拟线程中阻塞调用时自动挂起（配合 JEP 444）            |
| Java 11 | JEP 321: HTTP Client 转正为标准特性（java.net.http 包）      |
| Java 10 | JEP 321: HTTP Client 第二次孵化                              |
| Java 9  | JEP 110: HTTP Client 首次孵化（jdk.incubator.httpclient 包） |
| Java 1  | HttpURLConnection（传统 HTTP 客户端，功能有限且 API 老旧）        |

## 功能详细介绍

### 1. Java 1-8 - HttpURLConnection 时代

`HttpURLConnection` 是 Java 唯一的内置 HTTP 客户端，但存在诸多问题：
- API 设计老旧，不支持现代 HTTP 特性
- 仅支持 HTTP/1.1
- 连接池管理不完善
- 不支持异步请求
- 错误处理不一致

### 2. Java 9 - HTTP Client 首次孵化 (JEP 110)

全新的 `java.net.http` 模块引入：
- 支持 HTTP/2 和 WebSocket
- 提供同步和异步两种请求方式
- 内置连接池管理
- 流式请求和响应支持

包名：`jdk.incubator.httpclient`

### 3. Java 10 - 第二次孵化 (JEP 321)

API 微调，改进 WebSocket 支持和错误处理。

### 4. Java 11 - HTTP Client 转正 (JEP 321)

从孵化模块转为标准特性，包名变为 `java.net.http`，包含三个核心类：
- `HttpClient`：客户端实例，线程安全，可复用
- `HttpRequest`：不可变的请求对象
- `HttpResponse`：响应结果

### 5. Java 21+ - 虚拟线程集成

HTTP Client 的阻塞式 `send()` 方法在虚拟线程中调用时，I/O 操作会自动挂起并释放载体线程，使虚拟线程可以高效地处理大量并发 HTTP 请求。

### 6. Java 26 - HTTP/3 支持 (JEP 517)

HTTP Client 新增对 HTTP/3 协议的支持，基于 QUIC 传输协议，相比 HTTP/2 具有更好的弱网络环境表现和更低的连接建立延迟：

```java
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_3)
    .build();
```

## HttpClient vs 第三方库

| 特性          | HttpClient        | OkHttp              | Apache HttpClient |
|-------------|-------------------|---------------------|-------------------|
| 内置          | 是（JDK 11+）        | 否（需引入依赖）            | 否（需引入依赖）           |
| HTTP/2 支持   | 原生支持              | 支持                   | 支持                |
| 异步支持        | CompletableFuture | Callback/Coroutine   | Future            |
| WebSocket   | 支持                | 支持                   | 不支持               |
| 虚拟线程集成      | 原生支持（Java 21+）    | 兼容                   | 兼容                |

## 总结

HTTP Client 从 Java 9 孵化到 Java 11 转正，提供了现代化的 HTTP/1.1、HTTP/2 和 HTTP/3 客户端能力，完全替代了老旧的 `HttpURLConnection`。Java 21 的虚拟线程集成使其在高并发 HTTP 场景中表现优异，Java 26 的 HTTP/3 支持进一步提升了弱网络环境下的性能。
