# Java 网络编程学习笔记

## 一、Socket 编程基础

### 1.1 什么是 Socket

Socket 是操作系统提供的进程间通信机制，是 TCP/IP 网络通信的端点抽象。Java 中通过 `java.net` 包提供 Socket 编程支持。

```
  ┌─────────────┐         TCP/IP 网络         ┌─────────────┐
  │   Client    │  ────────────────────────▶  │   Server    │
  │   Socket    │  ◀────────────────────────  │  ServerSocket│
  │  (IP:Port)  │         双向数据流           │  (IP:Port)  │
  └─────────────┘                            └─────────────┘
```

### 1.2 ServerSocket 服务端示例

```java
import java.io.*;
import java.net.*;

public class SimpleServer {
    public static void main(String[] args) throws IOException {
        // 创建 ServerSocket，绑定端口 8080
        try (ServerSocket serverSocket = new ServerSocket(8080)) {
            System.out.println("Server started on port 8080");

            // accept() 是阻塞调用，等待客户端连接
            Socket clientSocket = serverSocket.accept();
            System.out.println("Client connected: " + clientSocket.getRemoteSocketAddress());

            // 获取输入输出流
            BufferedReader in = new BufferedReader(
                new InputStreamReader(clientSocket.getInputStream()));
            PrintWriter out = new PrintWriter(
                clientSocket.getOutputStream(), true);

            // 读取客户端数据
            String line;
            while ((line = in.readLine()) != null) {
                System.out.println("Received: " + line);
                out.println("Echo: " + line);
            }
        }
    }
}
```

### 1.3 Socket 客户端示例

```java
import java.io.*;
import java.net.*;

public class SimpleClient {
    public static void main(String[] args) throws IOException {
        // 连接服务器
        try (Socket socket = new Socket("localhost", 8080)) {
            PrintWriter out = new PrintWriter(
                socket.getOutputStream(), true);
            BufferedReader in = new BufferedReader(
                new InputStreamReader(socket.getInputStream()));

            // 发送数据
            out.println("Hello, Server!");

            // 接收响应
            String response = in.readLine();
            System.out.println("Server response: " + response);
        }
    }
}
```

### 1.4 常用配置选项

| 方法 | 说明 | 默认值 |
|------|------|--------|
| `setSoTimeout(int ms)` | 读取超时时间 | 0 (永不超时) |
| `setTcpNoDelay(boolean on)` | 禁用 Nagle 算法 | false |
| `setReuseAddress(boolean on)` | 地址复用 | false |
| `setKeepAlive(boolean on)` | 心跳保活 | false |
| `setReceiveBufferSize(int size)` | 接收缓冲区大小 | 取决于 OS |
| `setSendBufferSize(int size)` | 发送缓冲区大小 | 取决于 OS |
| `setSoLinger(boolean on, int sec)` | 关闭时等待发送完成 | 禁用 |

---

## 二、多线程服务器模型（BIO）

### 2.1 BIO 模型特点

BIO（Blocking I/O）是 Java 最传统的 I/O 模型：

- 每个连接独占一个线程
- 线程在 read/write 操作时阻塞
- 模型简单，编程直观
- 线程数 = 连接数，高并发下资源消耗大

### 2.2 线程池版多线程服务器

```java
import java.io.*;
import java.net.*;
import java.util.concurrent.*;

public class BioThreadPoolServer {
    private static final int PORT = 8080;
    private static final int THREAD_POOL_SIZE = 50;

    public static void main(String[] args) throws IOException {
        ExecutorService executor = Executors.newFixedThreadPool(THREAD_POOL_SIZE);
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("BIO Server started on port " + PORT);

            while (!Thread.currentThread().isInterrupted()) {
                // accept 阻塞等待连接
                Socket clientSocket = serverSocket.accept();
                System.out.println("New connection: " + clientSocket.getRemoteSocketAddress());
                // 提交给线程池处理
                executor.submit(() -> handleClient(clientSocket));
            }
        }
    }

    private static void handleClient(Socket socket) {
        try (BufferedReader in = new BufferedReader(
                new InputStreamReader(socket.getInputStream()));
             PrintWriter out = new PrintWriter(
                socket.getOutputStream(), true)) {

            String line;
            while ((line = in.readLine()) != null) {
                if ("bye".equalsIgnoreCase(line)) break;
                out.println("Echo: " + line);
            }
        } catch (IOException e) {
            System.err.println("Client error: " + e.getMessage());
        } finally {
            try { socket.close(); } catch (IOException ignored) {}
        }
    }
}
```

### 2.3 BIO 模型局限性

```
  线程数 vs 连接数
  ┌──────────────────────────────────────┐
  │  连接数   线程数    内存消耗    CPU 利用率  │
  │   100      100     ~100MB      低       │
  │   1000     1000    ~1GB        中       │
  │   10000    10000   ~10GB       高(切换)  │
  │   100000   不可行   OOM        崩溃     │
  └──────────────────────────────────────┘
```

每个线程默认占用 ~1MB 栈空间，10000 个连接就需要约 10GB 内存，这是 BIO 无法应对高并发的根本原因。

---

## 三、NIO 网络编程（Selector + Channel）

### 3.1 NIO 核心概念

Java NIO（Non-blocking I/O）在 Java 1.4 引入，位于 `java.nio` 包：

| 组件 | 说明 |
|------|------|
| **Channel** | 通道，双向数据传输，类似 Stream 但可非阻塞 |
| **Buffer** | 缓冲区，数据容器，通过 position/limit/capacity 管理 |
| **Selector** | 选择器，单线程监控多个 Channel 的 I/O 事件 |

### 3.2 Buffer 使用

```java
// 创建 Buffer
ByteBuffer buffer = ByteBuffer.allocate(1024);

// 写入数据
buffer.put((byte) 1);
buffer.put("Hello".getBytes());

// 切换到读模式（flip：limit = position, position = 0）
buffer.flip();

// 读取数据
while (buffer.hasRemaining()) {
    System.out.print((char) buffer.get());
}

// 重置以便再次写入
buffer.clear();
```

### 3.3 NIO 服务器完整示例

```java
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.Iterator;
import java.util.Set;

public class NioServer {
    private static final int PORT = 8080;
    private static final int BUFFER_SIZE = 1024;

    public static void main(String[] args) throws IOException {
        // 1. 打开 ServerSocketChannel
        ServerSocketChannel serverChannel = ServerSocketChannel.open();
        // 2. 设置为非阻塞模式
        serverChannel.configureBlocking(false);
        serverChannel.bind(new InetSocketAddress(PORT));
        System.out.println("NIO Server started on port " + PORT);

        // 3. 创建 Selector
        Selector selector = Selector.open();
        // 4. 注册 OP_ACCEPT 事件
        serverChannel.register(selector, SelectionKey.OP_ACCEPT);

        // 5. 事件循环
        while (true) {
            int readyChannels = selector.select(); // 阻塞等待事件
            if (readyChannels == 0) continue;

            Set<SelectionKey> selectedKeys = selector.selectedKeys();
            Iterator<SelectionKey> iterator = selectedKeys.iterator();

            while (iterator.hasNext()) {
                SelectionKey key = iterator.next();

                if (key.isAcceptable()) {
                    handleAccept(key, serverChannel, selector);
                } else if (key.isReadable()) {
                    handleRead(key);
                } else if (key.isWritable()) {
                    handleWrite(key);
                }

                // 必须手动移除已处理的 key
                iterator.remove();
            }
        }
    }

    private static void handleAccept(SelectionKey key,
            ServerSocketChannel serverChannel, Selector selector) throws IOException {
        SocketChannel clientChannel = serverChannel.accept();
        clientChannel.configureBlocking(false);
        // 注册读事件，附带一个 Buffer 用于读写数据
        clientChannel.register(selector, SelectionKey.OP_READ,
                ByteBuffer.allocate(BUFFER_SIZE));
        System.out.println("Client connected: " + clientChannel.getRemoteAddress());
    }

    private static void handleRead(SelectionKey key) throws IOException {
        SocketChannel channel = (SocketChannel) key.channel();
        ByteBuffer buffer = (ByteBuffer) key.attachment();
        buffer.clear();

        int bytesRead = channel.read(buffer);
        if (bytesRead == -1) {
            // 客户端关闭
            channel.close();
            key.cancel();
            return;
        }

        buffer.flip();
        String message = new String(buffer.array(), 0, buffer.remaining());
        System.out.println("Received: " + message);

        // 切换为写事件
        buffer.compact();
        key.interestOps(SelectionKey.OP_WRITE);
    }

    private static void handleWrite(SelectionKey key) throws IOException {
        SocketChannel channel = (SocketChannel) key.channel();
        ByteBuffer buffer = (ByteBuffer) key.attachment();
        buffer.flip();

        channel.write(buffer);
        // 写完后切回读事件
        key.interestOps(SelectionKey.OP_READ);
    }
}
```

### 3.4 NIO 四种事件类型

| 事件常量 | 值 | 说明 |
|----------|-----|------|
| `OP_ACCEPT` | 16 | 客户端连接请求（仅 ServerSocketChannel） |
| `OP_CONNECT` | 8 | 连接建立完成（仅 SocketChannel） |
| `OP_READ` | 1 | 通道可读 |
| `OP_WRITE` | 4 | 通道可写 |

---

## 四、AIO 异步 I/O（NIO.2）

### 4.1 AIO 概述

AIO（Asynchronous I/O）在 Java 7 以 NIO.2 引入，位于 `java.nio.channels` 包：

- 真正的异步 I/O，调用后立即返回，完成后通过回调/ Future 通知
- 依赖操作系统支持（Linux 下依赖 libaio，Windows 下使用 IOCP）
- Linux 上 AIO 支持有限，实际生产中较少使用

### 4.2 AIO 服务器示例（Future 方式）

```java
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.concurrent.Future;

public class AioServer {
    private static final int PORT = 8080;
    private static final int BUFFER_SIZE = 1024;

    public static void main(String[] args) throws Exception {
        // 创建异步通道组
        AsynchronousChannelGroup group = AsynchronousChannelGroup
                .withFixedThreadPool(10, Executors.defaultThreadFactory());

        // 创建异步服务器通道
        AsynchronousServerSocketChannel serverChannel =
                AsynchronousServerSocketChannel.open(group)
                    .bind(new InetSocketAddress(PORT));

        System.out.println("AIO Server started on port " + PORT);

        while (true) {
            // accept 立即返回 Future
            Future<AsynchronousSocketChannel> future = serverChannel.accept();
            AsynchronousSocketChannel clientChannel = future.get(); // 阻塞等待

            System.out.println("Client connected: " + clientChannel.getRemoteAddress());

            ByteBuffer buffer = ByteBuffer.allocate(BUFFER_SIZE);
            Future<Integer> readFuture = clientChannel.read(buffer);
            int bytesRead = readFuture.get();

            buffer.flip();
            String message = new String(buffer.array(), 0, bytesRead);
            System.out.println("Received: " + message);
        }
    }
}
```

### 4.3 AIO 服务器示例（CompletionHandler 回调方式）

```java
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.*;

public class AioCallbackServer {
    private static final int PORT = 8080;
    private static final int BUFFER_SIZE = 1024;

    public static void main(String[] args) throws IOException {
        AsynchronousServerSocketChannel serverChannel =
                AsynchronousServerSocketChannel.open()
                    .bind(new InetSocketAddress(PORT));

        System.out.println("AIO Callback Server started on port " + PORT);
        acceptConnection(serverChannel);

        // 主线程阻塞
        Thread.currentThread().join();
    }

    private static void acceptConnection(AsynchronousServerSocketChannel server) {
        server.accept(null, new CompletionHandler<
                AsynchronousSocketChannel, Object>() {
            @Override
            public void completed(AsynchronousSocketChannel client, Object att) {
                // 继续接受下一个连接
                acceptConnection(server);
                // 处理当前连接
                handleClient(client);
            }

            @Override
            public void failed(Throwable exc, Object att) {
                System.err.println("Accept failed: " + exc.getMessage());
            }
        });
    }

    private static void handleClient(AsynchronousSocketChannel client) {
        ByteBuffer buffer = ByteBuffer.allocate(BUFFER_SIZE);
        client.read(buffer, buffer, new CompletionHandler<
                Integer, ByteBuffer>() {
            @Override
            public void completed(Integer bytesRead, ByteBuffer buf) {
                if (bytesRead == -1) {
                    try { client.close(); } catch (IOException ignored) {}
                    return;
                }
                buf.flip();
                String msg = new String(buf.array(), 0, bytesRead);
                System.out.println("Received: " + msg);
            }

            @Override
            public void failed(Throwable exc, ByteBuffer att) {
                System.err.println("Read failed: " + exc.getMessage());
            }
        });
    }
}
```

---

## 五、BIO / NIO / AIO 三种模型对比

### 5.1 同步与异步、阻塞与非阻塞

理解 I/O 模型的关键在于两个维度：

```
  同步 vs 异步
  ┌────────────────────────────────────────────────────┐
  │  同步 (Synchronous) : 调用者主动参与 I/O 操作      │
  │     - 阻塞式：调用线程挂起等待（BIO）              │
  │     - 非阻塞式：立即返回，轮询状态（NIO）          │
  │                                                    │
  │  异步 (Asynchronous) : 操作系统完成 I/O 后通知调用者│
  │     - 回调或 Future 获取结果（AIO）                │
  └────────────────────────────────────────────────────┘

  生活比喻：烧开水
  ┌────────────────────────────────────────────────────┐
  │  BIO   : 盯着水壶，水开了才离开（阻塞等待）          │
  │  NIO   : 每隔几秒去看一下水壶（非阻塞轮询）          │
  │  AIO   : 水壶响了自动通知你（异步回调）              │
  └────────────────────────────────────────────────────┘
```

### 5.2 详细对比表

| 维度 | BIO | NIO | AIO |
|------|-----|-----|-----|
| 全称 | Blocking I/O | Non-blocking I/O | Asynchronous I/O |
| 引入版本 | JDK 1.0 | JDK 1.4 | JDK 7 |
| 包名 | `java.net` | `java.nio` | `java.nio.channels` |
| 核心组件 | Socket/ServerSocket | Channel/Buffer/Selector | AsynchronousChannel |
| 通信方式 | 流（Stream） | 缓冲区（Buffer） | 缓冲区（Buffer） |
| 阻塞方式 | 阻塞 | 非阻塞 | 异步 |
| 线程模型 | 一连接一线程 | 多路复用单/少线程 | 回调/未来 |
| 适用场景 | 连接数少且固定 | 高并发、短连接 | 高并发、长连接、文件 I/O |
| 编程难度 | 低 | 中 | 高 |
| Linux 支持 | 良好 | epoll 完善 | 有限（依赖 libaio） |
| 代表框架 | Tomcat (BIO模式) | Netty, Tomcat (NIO) | 较少使用 |
| 吞吐量 | 低 | 高 | 高 |
| 延迟 | 低（无轮询开销） | 略高（多路复用） | 低（回调触发） |

### 5.3 选择建议

| 场景 | 推荐模型 | 理由 |
|------|----------|------|
| 内部工具，< 100 并发 | BIO | 简单可靠，够用 |
| Web 服务器，高并发 | NIO | 生态成熟，性能优秀 |
| 网关/代理 | NIO | 连接数巨大，需多路复用 |
| 文件异步读写 | AIO | OS 原生异步支持 |
| 企业级应用 | NIO（通过 Netty） | 生态最完善 |

---

## 六、Reactor 模型

### 6.1 什么是 Reactor 模型

Reactor 是一种事件驱动的网络编程设计模式，核心思想是将 I/O 事件的分发与处理解耦。Doug Lea 在《Scalable IO in Java》中详细阐述了这一模型。

### 6.2 单线程 Reactor

```
  ┌─────────────────────────────────────────┐
  │          Single Thread Reactor          │
  │                                         │
  │  ┌──────────┐     ┌──────────────┐      │
  │  │ Acceptor │───▶ │  Selector    │      │
  │  └──────────┘     │  (Event Loop)│      │
  │                   └──────┬───────┘      │
  │                          │              │
  │                   ┌──────▼───────┐      │
  │                   │   Handler    │      │
  │                   │  (Read/Decode│      │
  │                   │   Compute/   │      │
  │                   │   Encode/Send)│      │
  │                   └──────────────┘      │
  └─────────────────────────────────────────┘

  特点：单线程完成 accept → read → decode → compute → encode → send
  优点：简单，无线程切换开销
  缺点：无法利用多核，Handler 阻塞影响整体
  适用：单机少量连接，简单协议
```

### 6.3 多线程 Reactor

```
  ┌─────────────────────────────────────────────────┐
  │           Multi-Thread Reactor                   │
  │                                                  │
  │  ┌──────────┐     ┌──────────────┐              │
  │  │ Acceptor │───▶ │  Selector    │              │
  │  └──────────┘     │  (Event Loop)│              │
  │                   └──────┬───────┘              │
  │                          │                      │
  │                   ┌──────▼───────┐              │
  │                   │   Handler    │              │
  │                   │   (Read/     │              │
  │                   │    Decode)   │              │
  │                   └──────┬───────┘              │
  │                          │ dispatch             │
  │                   ┌──────▼──────────────────┐   │
  │                   │     Worker Thread Pool  │   │
  │                   │  ┌────┐ ┌────┐ ┌────┐  │   │
  │                   │  │ T1 │ │ T2 │ │ T3 │  │   │
  │                   │  │    │ │    │ │    │  │   │
  │                   │  └────┘ └────┘ └────┘  │   │
  │                   │   (Compute/Encode/Send) │   │
  │                   └─────────────────────────┘   │
  └─────────────────────────────────────────────────┘

  特点：Selector 线程负责 I/O 事件，业务处理交给线程池
  优点：I/O 不阻塞业务计算，可充分利用多核
  缺点：Acceptor 仍为单点
  适用：大多数业务服务器
```

### 6.4 主从多线程 Reactor（Master-Slave）

```
  ┌───────────────────────────────────────────────────────────┐
  │              Master-Slave Multi-Thread Reactor            │
  │                                                           │
  │  ┌─────────────────┐    ┌─────────────────────┐          │
  │  │  MainReactor    │    │    SubReactors       │          │
  │  │  (Acceptor)     │    │  ┌───────────────┐  │          │
  │  │                 │    │  │ SubReactor-1  │  │          │
  │  │  ┌──────────┐   │    │  │ (Selector +   │  │          │
  │  │  │Selector   │───┼───▶│  │  Handler)     │  │          │
  │  │  │(accept)   │   │    │  └───────┬───────┘  │          │
  │  │  └──────────┘   │    │          │          │          │
  │  └─────────────────┘    │  ┌───────▼───────┐  │          │
  │                         │  │ SubReactor-2  │  │          │
  │    监听连接事件          │  │ (Selector +   │  │          │
  │    分发给 SubReactor     │  │  Handler)     │  │          │
  │                         │  └───────┬───────┘  │          │
  │                         │          │          │          │
  │                         │  ┌───────▼───────┐  │          │
  │                         │  │ SubReactor-N  │  │          │
  │                         │  │ (Selector +   │  │          │
  │                         │  │  Handler)     │  │          │
  │                         │  └───────┬───────┘  │          │
  │                         └──────────┬──────────┘          │
  │                                    │ dispatch             │
  │                         ┌──────────▼──────────────────┐  │
  │                         │     Worker Thread Pool      │  │
  │                         │  (Business Logic Processing)│  │
  │                         └─────────────────────────────┘  │
  └───────────────────────────────────────────────────────────┘

  特点：MainReactor 只管 accept，SubReactor 负责 I/O 读写，
        Worker 线程池处理业务逻辑
  优点：accept 与 I/O 分离，连接处理能力线性扩展
  缺点：架构复杂，调试困难
  适用：高并发网关、IM 服务器、RPC 框架
```

### 6.5 Reactor 模型对比总结

| 维度 | 单线程 | 多线程 | 主从多线程 |
|------|--------|--------|------------|
| Reactor 数量 | 1 | 1 | 1 + N |
| Accept 处理 | 同线程 | 同线程 | 独立 MainReactor |
| I/O 处理 | 同线程 | 同线程 | 多个 SubReactor |
| 业务处理 | 同线程 | 线程池 | 线程池 |
| 多核利用 | 否 | 部分 | 是 |
| 连接上限 | 低 | 中 | 高 |
| 复杂度 | 低 | 中 | 高 |
| 典型使用 | 简单工具 | Tomcat NIO | Netty 默认模式 |

---

## 七、Java 11+ HttpClient（java.net.http）

### 7.1 概述

Java 11 引入了全新的 `java.net.http.HttpClient` API，替代老旧的 `HttpURLConnection`：

- 支持 HTTP/1.1 和 HTTP/2
- 支持同步和异步请求
- 支持 WebSocket
- API 设计现代，链式调用

### 7.2 基本使用

```java
import java.net.URI;
import java.net.http.*;
import java.time.Duration;

public class HttpClientDemo {
    public static void main(String[] args) throws Exception {
        // 创建 HttpClient（线程安全，建议复用）
        HttpClient client = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_2)
                .connectTimeout(Duration.ofSeconds(10))
                .followRedirects(HttpClient.Redirect.NORMAL)
                .build();

        // 构建请求
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.example.com/data"))
                .header("Content-Type", "application/json")
                .timeout(Duration.ofSeconds(5))
                .GET()
                .build();

        // 同步发送
        HttpResponse<String> response = client.send(request,
                HttpResponse.BodyHandlers.ofString());

        System.out.println("Status: " + response.statusCode());
        System.out.println("Body: " + response.body());
    }
}
```

### 7.3 异步请求

```java
// 异步发送，返回 CompletableFuture
CompletableFuture<HttpResponse<String>> future = client.sendAsync(request,
        HttpResponse.BodyHandlers.ofString());

future.thenAccept(response -> {
    System.out.println("Status: " + response.statusCode());
    System.out.println("Body: " + response.body());
}).exceptionally(e -> {
    System.err.println("Request failed: " + e.getMessage());
    return null;
});
```

### 7.4 POST 请求示例

```java
// JSON POST
HttpRequest postRequest = HttpRequest.newBuilder()
        .uri(URI.create("https://api.example.com/users"))
        .header("Content-Type", "application/json")
        .POST(HttpRequest.BodyPublishers.ofString(
                "{\"name\":\"test\",\"age\":25}"))
        .build();

HttpResponse<String> response = client.send(postRequest,
        HttpResponse.BodyHandlers.ofString());
```

### 7.5 文件上传/下载

```java
// 下载文件到磁盘
HttpRequest downloadReq = HttpRequest.newBuilder()
        .uri(URI.create("https://example.com/file.zip"))
        .build();

HttpResponse<Path> downloadResp = client.send(downloadReq,
        HttpResponse.BodyHandlers.ofFile(
                Path.of("downloaded_file.zip")));

// 上传文件
HttpRequest uploadReq = HttpRequest.newBuilder()
        .uri(URI.create("https://example.com/upload"))
        .POST(HttpRequest.BodyPublishers.ofFile(
                Path.of("upload_file.zip")))
        .build();
```

### 7.6 常用配置选项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `version()` | HTTP 协议版本 | `HTTP_1_1` / `HTTP_2` |
| `connectTimeout()` | 连接超时 | `Duration.ofSeconds(10)` |
| `followRedirects()` | 重定向策略 | `NORMAL` / `ALWAYS` / `NEVER` |
| `proxy()` | 代理设置 | `ProxySelector.of(...)` |
| `executor()` | 异步任务线程池 | `Executors.newFixedThreadPool(...)` |
| `sslContext()` | SSL/TLS 配置 | `SSLContext.getDefault()` |

---

## 八、Netty 简介

### 8.1 为什么需要 Netty

虽然 Java NIO 提供了多路复用能力，但原生 NIO 编程存在诸多痛点：

| 痛点 | 说明 |
|------|------|
| **API 复杂** | Selector/Channel/Buffer 组合使用繁琐 |
| **Bug 多** | JDK NIO 的 epoll bug（空轮询导致 CPU 100%） |
| **拆包/粘包** | TCP 流式传输需自行处理消息边界 |
| **编解码** | 需要手动实现协议的 encode/decode |
| **断线重连** | 需要自行实现连接管理 |
| **性能调优** | 缓冲区管理、内存池等需深入理解 |
| **SSL/TLS** | 集成复杂 |

### 8.2 Netty 核心概念

```
  Netty 架构分层
  ┌────────────────────────────────────────────┐
  │              Application Layer             │
  │         (Handler / Business Logic)          │
  ├────────────────────────────────────────────┤
  │           Pipeline / ChannelHandler         │
  │    (Inbound: 解码、业务处理)                │
  │    (Outbound: 编码、发送)                   │
  ├────────────────────────────────────────────┤
  │              EventLoopGroup                │
  │    (BossGroup: accept 连接)                 │
  │    (WorkerGroup: 读写 I/O)                  │
  ├────────────────────────────────────────────┤
  │              Channel                       │
  │    (NioSocketChannel / NioServerSocketChannel) │
  ├────────────────────────────────────────────┤
  │              Transport                     │
  │    (NIO / OIO / Local / Embedded)          │
  └────────────────────────────────────────────┘
```

### 8.3 Netty 服务器示例

```java
import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.*;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.handler.codec.string.StringDecoder;
import io.netty.handler.codec.string.StringEncoder;

public class NettyServer {
    public static void main(String[] args) throws InterruptedException {
        // BossGroup 处理 accept 连接
        EventLoopGroup bossGroup = new NioEventLoopGroup(1);
        // WorkerGroup 处理 I/O 读写
        EventLoopGroup workerGroup = new NioEventLoopGroup();

        try {
            ServerBootstrap bootstrap = new ServerBootstrap();
            bootstrap.group(bossGroup, workerGroup)
                    .channel(NioServerSocketChannel.class)
                    .childHandler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel ch) {
                            ChannelPipeline pipeline = ch.pipeline();
                            // 添加编解码器
                            pipeline.addLast(new StringDecoder());
                            pipeline.addLast(new StringEncoder());
                            // 添加业务处理器
                            pipeline.addLast(new SimpleChannelInboundHandler<String>() {
                                @Override
                                protected void channelRead0(
                                        ChannelHandlerContext ctx, String msg) {
                                    System.out.println("Received: " + msg);
                                    ctx.writeAndFlush("Echo: " + msg);
                                }
                            });
                        }
                    })
                    .option(ChannelOption.SO_BACKLOG, 128)
                    .childOption(ChannelOption.SO_KEEPALIVE, true);

            ChannelFuture future = bootstrap.bind(8080).sync();
            System.out.println("Netty Server started on port 8080");
            future.channel().closeFuture().sync();
        } finally {
            bossGroup.shutdownGracefully();
            workerGroup.shutdownGracefully();
        }
    }
}
```

### 8.4 Netty 核心组件

| 组件 | 说明 |
|------|------|
| `EventLoopGroup` | 事件循环组，包含多个 EventLoop |
| `EventLoop` | 事件循环，一个线程处理多个 Channel 的 I/O |
| `Channel` | 网络连接抽象（客户端/服务端） |
| `ChannelHandler` | 处理 I/O 事件的处理器 |
| `ChannelPipeline` | Handler 链，Inbound/Outbound 双向传播 |
| `ChannelFuture` | 异步操作结果的容器 |
| `ByteBuf` | 比 NIO Buffer 更强大的缓冲区 |
| `Bootstrap` / `ServerBootstrap` | 启动引导类 |

### 8.5 Netty vs 原生 NIO 对比

| 特性 | 原生 NIO | Netty |
|------|----------|-------|
| 代码量 | 多（需手动管理） | 少（链式配置） |
| 拆包/粘包 | 手动实现 | 内置多种解码器 |
| 内存管理 | 手动 | 池化 ByteBuf，引用计数 |
| 异常处理 | 分散 | 统一 ChannelHandler |
| SSL/TLS | 复杂 | `SslHandler` 一行添加 |
| 协议支持 | 仅 TCP/UDP | HTTP, WebSocket, Redis, Redisson 等 |
| 社区生态 | 仅 JDK 文档 | 广泛使用，文档丰富 |

---

## 九、网络编程最佳实践

### 9.1 连接管理

```java
// 1. 设置合理的超时时间，避免永久阻塞
socket.setSoTimeout(30_000); // 30 秒读超时

// 2. 使用 try-with-resources 确保资源释放
try (Socket socket = new Socket(host, port)) {
    // 使用 socket
} // 自动关闭

// 3. 优雅关闭：先关输入，再关输出，最后关 Socket
socket.shutdownInput();
socket.shutdownOutput();
socket.close();
```

### 9.2 线程池配置

```java
// 根据场景选择合适的线程池
// I/O 密集型：线程数 = CPU 核心数 * 2
ExecutorService ioPool = Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors() * 2);

// 使用自定义 ThreadFactory 便于排查问题
ThreadFactory threadFactory = new ThreadFactoryBuilder()
        .setNameFormat("network-worker-%d")
        .setUncaughtExceptionHandler((t, e) ->
            log.error("Thread {} error", t.getName(), e))
        .build();
```

### 9.3 拆包/粘包处理

TCP 是面向字节流的协议，不保证消息边界，常见解决方案：

| 方案 | 说明 | 适用场景 |
|------|------|----------|
| **固定长度** | 每个消息固定 N 字节 | 定长协议 |
| **分隔符** | 用特殊字符分隔（如 `\n`） | 文本协议 |
| **长度字段** | 消息头包含长度字段 | 二进制协议 |
| **消息结束标记** | 特定结束标记 | 自定义协议 |

```java
// 使用长度字段：[4字节长度][N字节数据]
public class LengthFrameDecoder {
    public static byte[] decode(ByteBuffer buffer) {
        if (buffer.remaining() < 4) return null;

        int length = buffer.getInt(); // 读取消息长度
        if (buffer.remaining() < length) return null;

        byte[] data = new byte[length];
        buffer.get(data);
        return data;
    }
}
```

### 9.4 零拷贝技术

```java
// 1. FileChannel.transferTo() - 直接在内核空间传输
FileChannel fileChannel = FileChannel.open(
        Paths.get("largefile.dat"), StandardOpenOption.READ);
SocketChannel socketChannel = SocketChannel.open(
        new InetSocketAddress("host", 8080));
// 数据不经过用户空间，直接由 DMA 发送到网卡
fileChannel.transferTo(0, fileChannel.size(), socketChannel);

// 2. DirectBuffer - 堆外内存，避免 JNI 拷贝
ByteBuffer directBuffer = ByteBuffer.allocateDirect(1024 * 1024);

// 3. Netty 的 CompositeByteBuf - 逻辑拼接，避免内存拷贝
CompositeByteBuf composite = Unpooled.compositeBuffer();
composite.addComponents(true, buf1, buf2, buf3);
```

### 9.5 性能调优清单

| 调优项 | 建议值 | 说明 |
|--------|--------|------|
| `SO_BACKLOG` | 1024+ | 连接等待队列大小 |
| `SO_REUSEADDR` | true | 允许地址复用 |
| `TCP_NODELAY` | true | 禁用 Nagle 算法，减少延迟 |
| `SO_RCVBUF` | 按需调整 | 接收缓冲区，高吞吐可增大 |
| `SO_SNDBUF` | 按需调整 | 发送缓冲区 |
| `SO_KEEPALIVE` | true | TCP 保活 |
| `reuseAddress` | true | 快速重启服务 |
| 连接池 | 必选 | 复用连接，减少握手开销 |
| 批处理写入 | 推荐 | `writeAndFlush` 合并多次写 |

### 9.6 安全注意事项

1. **输入校验**：所有来自网络的输入都视为不可信
2. **速率限制**：防止单个客户端占用过多资源
3. **SSL/TLS**：敏感数据必须加密传输
4. **连接数限制**：对单 IP 设置最大连接数，防止 DoS
5. **超时设置**：防止慢连接占用资源
6. **日志脱敏**：不在日志中记录敏感信息

### 9.7 常见问题排查

| 问题 | 可能原因 | 排查方法 |
|------|----------|----------|
| `Connection refused` | 服务未启动或端口错误 | `netstat -tlnp` 检查端口 |
| `Connection timeout` | 网络不通或防火墙 | `telnet host port` 测试连通性 |
| `Connection reset` | 对端异常关闭 | 检查服务端日志 |
| CPU 100% | NIO 空轮询 bug | 检查 JDK 版本，升级或打补丁 |
| 内存泄漏 | 连接未关闭 / 缓冲区未释放 | `netstat` 检查连接数，Heap Dump 分析 |
| 消息不完整 | 拆包/粘包处理不当 | 添加协议边界处理 |

---

> **总结**：Java 网络编程从 BIO 到 NIO 再到 AIO，经历了从阻塞到非阻塞再到异步的演进。实际生产中，推荐使用 NIO 配合 Netty 框架，既保证了高性能，又降低了开发复杂度。对于 HTTP 客户端场景，Java 11+ 的 `HttpClient` 是首选方案。
