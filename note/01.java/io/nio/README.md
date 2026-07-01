# Java NIO 全面学习笔记

## 一、IO 与 NIO 对比：面向流 vs 面向缓冲区

Java NIO（New IO / Non-blocking IO）自 JDK 1.4 引入，是对传统 `java.io` 包的重大补充。两者的核心差异如下：

| 对比维度 | BIO (java.io) | NIO (java.nio) |
|---------|---------------|----------------|
| **面向** | 面向流（Stream-oriented） | 面向缓冲区（Buffer-oriented） |
| **阻塞** | 阻塞 IO | 支持非阻塞 IO |
| **线程模型** | 一个连接一个线程 | 一个线程管理多个连接 |
| **选择器** | 无 | 有 Selector 多路复用器 |
| **性能** | 连接数少时够用 | 高并发、短连接场景优势明显 |
| **API 位置** | `java.io.*` | `java.nio.*`, `java.nio.channels.*` |

### 面向流的缺陷

```
客户端 --[字节流]--> 程序（一次读一个字节/一批字节，无法回头）
```

- 流是单向的，数据只能从流中顺序读取，**无法回溯**
- 每次 `read()` / `write()` 都要直接与操作系统交互
- 无法在缓冲区中前后移动指针来重新处理数据

### 面向缓冲区的优势

```
客户端 <===> [Channel] <===> [Buffer] <===> 程序
                         可来回移动 position 指针
```

- 数据先读到 Buffer，程序从 Buffer 中按需取数据
- Buffer 的 `position` 可自由移动，支持反复读写
- 配合 Channel 实现更高效的数据传输

---
## 引言：反直觉代码
Java NIO 全面学习笔记 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 二、Buffer 体系

Buffer 是 NIO 的核心抽象，所有数据传输都经过 Buffer。

### 2.1 Buffer 继承层次

```
Buffer (抽象基类)
  |
  +-- ByteBuffer        (最常用，支持直接/非直接缓冲区)
  |     +-- MappedByteBuffer (内存映射文件)
  |
  +-- CharBuffer
  +-- ShortBuffer
  +-- IntBuffer
  +-- LongBuffer
  +-- FloatBuffer
  +-- DoubleBuffer
```

### 2.2 创建 Buffer 的方式

```java
// 分配非直接缓冲区（堆内存）
ByteBuffer heapBuffer = ByteBuffer.allocate(1024);

// 分配直接缓冲区（本地内存，零拷贝潜力）
ByteBuffer directBuffer = ByteBuffer.allocateDirect(1024);

// 包装已有数组
byte[] data = new byte[100];
ByteBuffer wrapped = ByteBuffer.wrap(data);
```

### 2.3 直接缓冲区 vs 非直接缓冲区

| 特性 | 非直接缓冲区 (Heap) | 直接缓冲区 (Direct) |
|-----|-------------------|-------------------|
| 内存位置 | JVM 堆内 | 操作系统本地内存（堆外） |
| 创建开销 | 小 | 大（需要系统调用） |
| GC 影响 | 受 GC 管理 | 不受 GC 管理，需手动清理 |
| IO 性能 | 需要额外拷贝 | 避免一次拷贝，适合大数据量 |
| 适用场景 | 小数据、频繁创建销毁 | 大数据、持久 Channel 传输 |
| 判断方法 | `!buffer.isDirect()` | `buffer.isDirect()` |

```java
ByteBuffer buf = ByteBuffer.allocateDirect(4096);
System.out.println("是否直接缓冲区: " + buf.isDirect());  // true
```

---

## 三、Buffer 核心概念

### 3.1 四个核心属性

```
 0                    position              limit              capacity
 |-----------------------|--------------------|--------------------|
 |    可读/可写区域       |   不可访问区域       |   越界区域          |
 |-----------------------|--------------------|--------------------|
```

| 属性 | 含义 | 约束 |
|-----|------|------|
| **capacity** | 容量，Buffer 能容纳的最大元素数 | 创建后不可变 |
| **position** | 当前位置指针，下一次读/写的索引 | `0 <= position <= limit` |
| **limit** | 界限，第一个不应读取/写入的索引 | `0 <= limit <= capacity` |
| **mark** | 标记位置，用于 `reset()` 恢复 | `0 <= mark <= position` |

### 3.2 缓冲区状态转换图

```
┌──────────────────────────────────────────────────────┐
│                  新建/调用 clear()                     │
│  position = 0                                         │
│  limit = capacity                                     │
│         │                                            │
│         ▼                                            │
│   ┌─────────────┐     写入数据       ┌─────────────┐  │
│   │   写模式     │ ──────────────►   │   写后状态   │  │
│   │ (填充数据)   │                   │ position 前进│  │
│   └─────────────┘                   └──────┬──────┘  │
│                                            │ flip()  │
│                                            ▼         │
│   ┌─────────────┐  rewind()   ┌─────────────┐        │
│   │   倒带模式   │ ◄─────────  │   读模式     │        │
│   │ pos=0,limit │             │ pos=0,limit │        │
│   │ =capacity   │             │ =旧position │        │
│   └─────────────┘             └─────────────┘        │
└──────────────────────────────────────────────────────┘
```

### 3.3 核心方法详解

| 方法 | 说明 | position | limit |
|-----|------|----------|-------|
| `flip()` | 写模式 → 读模式 | 0 | 旧 position |
| `rewind()` | 重读，不修改 limit | 0 | 不变 |
| `clear()` | 清空（实际不清零）准备写 | 0 | capacity |
| `compact()` | 压缩：保留未读数据后准备写 | 未读字节数 | capacity |
| `mark()` | 标记当前 position | - | - |
| `reset()` | position 恢复到 mark | mark 的值 | - |
| `hasRemaining()` | 是否还有元素可读 | - | - |
| `remaining()` | 剩余可读元素数 | - | - |

### 3.4 flip() / rewind() / clear() / compact() 对比

```java
ByteBuffer buf = ByteBuffer.allocate(10);

// 1. 写入 4 个字节
buf.put((byte)'A');
buf.put((byte)'B');
buf.put((byte)'C');
buf.put((byte)'D');
// 此时: position=4, limit=10, capacity=10

// 2. flip() → 切换到读模式
buf.flip();
// 此时: position=0, limit=4 (只能读到 D)

// 3. 读 2 个字节
buf.get(); // A
buf.get(); // B
// 此时: position=2, limit=4

// 4. compact() → 压缩后准备写
buf.compact();
// 此时: position=2 (剩余的 C、D 移到开头), limit=10
// Buffer 内容: [C, D, ?, ?, ?, ?, ?, ?, ?, ?]

// 5. clear() → 完全清空准备写
buf.clear();
// 此时: position=0, limit=10 (数据还在但被覆盖)
```

### 3.5 视图缓冲区（View Buffer）

```java
// ByteBuffer 可以创建各种类型的视图
ByteBuffer byteBuf = ByteBuffer.allocate(16);  // 16 字节

IntBuffer intBuf = byteBuf.asIntBuffer();       // 4 个 int (16/4)
ShortBuffer shortBuf = byteBuf.asShortBuffer();  // 8 个 short (16/2)
CharBuffer charBuf = byteBuf.asCharBuffer();     // 8 个 char (16/2)

// 视图和原 Buffer 共享底层数据，修改视图 = 修改原 Buffer
intBuf.put(0, 0x12345678);
System.out.println(Integer.toHexString(byteBuf.getInt(0)));  // 12345678
```

---

## 四、Channel 体系

Channel 是对传统流的替代，支持双向读写和非阻塞操作。

### 4.1 Channel 继承层次

```
Channel (接口)
  |
  +-- ReadableByteChannel
  +-- WritableByteChannel
  |
  +-- ByteChannel (extends Readable + Writable)
  |     |
  |     +-- FileChannel          (文件通道)
  |     +-- SocketChannel        (TCP 客户端通道)
  |     +-- ServerSocketChannel  (TCP 服务端通道)
  |     +-- DatagramChannel      (UDP 通道)
  |
  +-- GatheringByteChannel       (散射写入)
  +-- ScatteringByteChannel      (聚集读取)
  |
  +-- NetworkChannel             (网络通道基类)
  |     +-- AsynchronousSocketChannel
  |     +-- AsynchronousServerSocketChannel
  |
  +-- FileChannel
  |     +-- AsynchronousFileChannel
```

### 4.2 FileChannel

```java
// 获取 FileChannel（只能通过流获取）
try (FileInputStream fis = new FileInputStream("input.txt");
     FileOutputStream fos = new FileOutputStream("output.txt")) {

    FileChannel inChannel = fis.getChannel();
    FileChannel outChannel = fos.getChannel();

    // 方式1: 通过 Buffer 传输
    ByteBuffer buffer = ByteBuffer.allocate(1024);
    while (inChannel.read(buffer) > 0) {
        buffer.flip();
        outChannel.write(buffer);
        buffer.clear();
    }

    // 方式2: transferTo（零拷贝，直接在内核空间传输）
    // inChannel.transferTo(0, inChannel.size(), outChannel);

    // 方式3: transferFrom
    // outChannel.transferFrom(inChannel, 0, inChannel.size());
}
```

### 4.3 散射读取与聚集写入

```java
// 散射读取 (Scattering Read): 一个 Channel → 多个 Buffer
ByteBuffer header = ByteBuffer.allocate(4);
ByteBuffer body = ByteBuffer.allocate(1024);
ByteBuffer[] buffers = {header, body};

channel.read(buffers);  // 先填满 header，再填 body

// 聚集写入 (Gathering Write): 多个 Buffer → 一个 Channel
header.flip();
body.flip();
channel.write(buffers);  // 按顺序写入
```

---

## 五、Selector 多路复用器

Selector 允许单线程管理多个 Channel，是 NIO 高并发的核心。

### 5.1 工作原理

```
                    ┌─────────────────────────────┐
                    │         Selector            │
                    │                             │
  Thread ─────────► │  register()                 │
                    │  select()  ◄── 阻塞/超时     │
                    │  selectedKeys() ──► 处理事件  │
                    └──────┬──┬──┬────────────────┘
                           │  │  │
              ┌────────────┘  │  └────────────┐
              ▼               ▼               ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │Channel 1 │  │Channel 2 │  │Channel N │
        └──────────┘  └──────────┘  └──────────┘
```

### 5.2 SelectionKey 的四种事件

| 常量 | 值 | 含义 | 触发时机 |
|-----|----|------|---------|
| `SelectionKey.OP_CONNECT` | 8 | 连接就绪 | 客户端 TCP 连接建立完成 |
| `SelectionKey.OP_ACCEPT` | 16 | 接收就绪 | 服务端收到新连接请求 |
| `SelectionKey.OP_READ` | 1 | 读就绪 | Channel 有数据可读 |
| `SelectionKey.OP_WRITE` | 4 | 写就绪 | Channel 可以写入数据 |

### 5.3 Channel 注册到 Selector

```java
Selector selector = Selector.open();

// 只有非阻塞模式的 Channel 才能注册到 Selector
ServerSocketChannel serverChannel = ServerSocketChannel.open();
serverChannel.bind(new InetSocketAddress(8080));
serverChannel.configureBlocking(false);

// 注册 OP_ACCEPT 事件，返回 SelectionKey
SelectionKey acceptKey = serverChannel.register(
    selector,
    SelectionKey.OP_ACCEPT,
    null  // 可附加一个对象
);
```

### 5.4 select() 方法

| 方法 | 说明 |
|-----|------|
| `select()` | 阻塞直到至少一个 Channel 就绪 |
| `select(timeout)` | 阻塞最多 timeout 毫秒 |
| `selectNow()` | 非阻塞，立即返回就绪数量 |
| `wakeup()` | 唤醒正在阻塞的 select() |

---

## 六、NIO 服务器完整示例

```java
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.Iterator;
import java.util.Set;
import java.nio.charset.StandardCharsets;

/**
 * NIO 非阻塞 TCP 服务器
 * 单线程处理多个客户端连接
 */
public class NioServer {

    private static final int PORT = 8080;
    private static final int BUFFER_SIZE = 1024;

    public static void main(String[] args) throws IOException {
        // 1. 打开 Selector
        Selector selector = Selector.open();

        // 2. 打开 ServerSocketChannel 并绑定端口
        ServerSocketChannel serverChannel = ServerSocketChannel.open();
        serverChannel.bind(new InetSocketAddress(PORT));

        // 3. 设置为非阻塞模式
        serverChannel.configureBlocking(false);

        // 4. 注册 OP_ACCEPT 事件
        serverChannel.register(selector, SelectionKey.OP_ACCEPT);
        System.out.println("NIO Server started on port " + PORT);

        // 5. 事件循环
        while (true) {
            // 阻塞等待就绪事件
            int readyChannels = selector.select();
            if (readyChannels == 0) continue;

            // 获取就绪的 SelectionKey 集合
            Set<SelectionKey> selectedKeys = selector.selectedKeys();
            Iterator<SelectionKey> iterator = selectedKeys.iterator();

            while (iterator.hasNext()) {
                SelectionKey key = iterator.next();

                // 处理完毕后必须从集合中移除
                iterator.remove();

                try {
                    if (key.isAcceptable()) {
                        handleAccept(key, selector);
                    } else if (key.isReadable()) {
                        handleRead(key);
                    } else if (key.isWritable()) {
                        handleWrite(key);
                    }
                } catch (IOException e) {
                    // 客户端异常断开
                    key.channel().close();
                    key.cancel();
                    System.out.println("Client disconnected: " + e.getMessage());
                }
            }
        }
    }

    /**
     * 处理新连接
     */
    private static void handleAccept(SelectionKey key, Selector selector)
            throws IOException {
        ServerSocketChannel serverChannel = (ServerSocketChannel) key.channel();
        SocketChannel clientChannel = serverChannel.accept();

        if (clientChannel != null) {
            clientChannel.configureBlocking(false);
            // 附加一个 ByteBuffer 用于读写
            clientChannel.register(selector, SelectionKey.OP_READ,
                    ByteBuffer.allocate(BUFFER_SIZE));
            System.out.println("New client connected: "
                    + clientChannel.getRemoteAddress());
        }
    }

    /**
     * 处理读事件
     */
    private static void handleRead(SelectionKey key) throws IOException {
        SocketChannel clientChannel = (SocketChannel) key.channel();
        ByteBuffer buffer = (ByteBuffer) key.attachment();

        int bytesRead = clientChannel.read(buffer);
        if (bytesRead > 0) {
            buffer.flip();
            String message = StandardCharsets.UTF_8
                    .decode(buffer).toString().trim();
            System.out.println("Received from "
                    + clientChannel.getRemoteAddress() + ": " + message);

            // 切换为写模式，准备回写响应
            buffer.clear();
            String response = "Echo: " + message + "\n";
            buffer.put(response.getBytes(StandardCharsets.UTF_8));
            buffer.flip();

            clientChannel.register(key.selector(),
                    SelectionKey.OP_WRITE, buffer);
        } else if (bytesRead == -1) {
            // 客户端关闭
            clientChannel.close();
            key.cancel();
            System.out.println("Client closed connection");
        }
    }

    /**
     * 处理写事件
     */
    private static void handleWrite(SelectionKey key) throws IOException {
        SocketChannel clientChannel = (SocketChannel) key.channel();
        ByteBuffer buffer = (ByteBuffer) key.attachment();

        clientChannel.write(buffer);

        if (!buffer.hasRemaining()) {
            // 写完，切换回读模式
            buffer.clear();
            clientChannel.register(key.selector(),
                    SelectionKey.OP_READ, buffer);
        }
    }
}
```

---

## 七、Path 和 Files API (Java 7 NIO.2)

### 7.1 Path 接口

`java.nio.file.Path` 替代了 `java.io.File`，表示文件系统中的路径。

```java
import java.nio.file.*;

// 创建 Path
Path path1 = Paths.get("/home/user/docs/file.txt");
Path path2 = Path.of("/home", "user", "docs", "file.txt");  // Java 11+
Path path3 = FileSystems.getDefault().getPath("/tmp/test");

// Path 常用方法
System.out.println(path1.getFileName());       // file.txt
System.out.println(path1.getParent());         // /home/user/docs
System.out.println(path1.getNameCount());      // 3
System.out.println(path1.getName(1));          // user
System.out.println(path1.getRoot());           // /
System.out.println(path1.isAbsolute());        // true
System.out.println(path1.toAbsolutePath());    // 转为绝对路径
```

### 7.2 Files 工具类

```java
import java.nio.file.*;
import java.nio.file.attribute.*;
import java.io.*;
import java.util.*;
import java.util.stream.*;

public class FilesApiDemo {

    public static void main(String[] args) throws IOException {
        Path file = Path.of("demo.txt");
        Path dir = Path.of("demo-dir");

        // ===== 文件操作 =====

        // 创建文件
        Files.createFile(file);
        Files.createDirectories(dir);
        Files.createDirectories(Path.of("a/b/c"));  // 递归创建

        // 写入文件（覆盖）
        Files.writeString(file, "Hello NIO.2\n", StandardOpenOption.CREATE);

        // 追加写入
        Files.writeString(file, "Appended line\n", StandardOpenOption.APPEND);

        // 读取文件
        String content = Files.readString(file);
        System.out.println(content);

        // 按行读取
        List<String> lines = Files.readAllLines(file);

        // 流式读取大文件（内存友好）
        try (Stream<String> stream = Files.lines(file)) {
            stream.filter(line -> line.contains("NIO"))
                  .forEach(System.out::println);
        }

        // 读写字节
        byte[] bytes = Files.readAllBytes(file);
        Files.write(file, "new content".getBytes());

        // 复制 / 移动 / 删除
        Files.copy(file, Path.of("backup.txt"), StandardCopyOption.REPLACE_EXISTING);
        Files.move(Path.of("backup.txt"), Path.of("moved.txt"),
                StandardCopyOption.ATOMIC_MOVE);
        Files.deleteIfExists(Path.of("moved.txt"));

        // ===== 文件信息 =====

        System.out.println("Exists: " + Files.exists(file));
        System.out.println("Is regular file: " + Files.isRegularFile(file));
        System.out.println("Size: " + Files.size(file) + " bytes");
        System.out.println("Is readable: " + Files.isReadable(file));
        System.out.println("Is writable: " + Files.isWritable(file));
        System.out.println("Is hidden: " + Files.isHidden(file));
        System.out.println("Last modified: "
                + Files.getLastModifiedTime(file));

        // ===== 目录遍历 =====

        // 列出目录内容（非递归）
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(dir)) {
            for (Path entry : stream) {
                System.out.println(entry.getFileName());
            }
        }

        // 递归遍历文件树
        try (Stream<Path> walk = Files.walk(Path.of("."))) {
            walk.filter(Files::isRegularFile)
                .forEach(System.out::println);
        }

        // 查找匹配文件
        try (Stream<Path> find = Files.find(Path.of("."), 3,
                (path, attrs) -> path.toString().endsWith(".java"))) {
            find.forEach(System.out::println);
        }

        // ===== 文件属性 =====

        // 基本属性
        BasicFileAttributes attrs = Files.readAttributes(file,
                BasicFileAttributes.class);
        System.out.println("Creation time: " + attrs.creationTime());
        System.out.println("Is directory: " + attrs.isDirectory());
        System.out.println("Size: " + attrs.size());

        // Posix 权限（仅 Unix/Linux）
        if (FileSystems.getDefault()
                .supportedFileAttributeViews().contains("posix")) {
            Set<PosixFilePermission> perms = Files.getPosixFilePermissions(file);
            System.out.println(PosixFilePermissions.toString(perms));
            Files.setPosixFilePermissions(file,
                    PosixFilePermissions.fromString("rw-r--r--"));
        }
    }
}
```

### 7.3 WatchService 文件监听

```java
import java.nio.file.*;

public class FileWatcher {
    public static void main(String[] args) throws Exception {
        Path dir = Path.of(".");
        WatchService watchService = FileSystems.getDefault()
                .newWatchService();

        // 注册监听事件
        dir.register(watchService,
                StandardWatchEventKinds.ENTRY_CREATE,
                StandardWatchEventKinds.ENTRY_MODIFY,
                StandardWatchEventKinds.ENTRY_DELETE);

        System.out.println("Watching directory: " + dir.toAbsolutePath());

        while (true) {
            WatchKey key = watchService.take();  // 阻塞等待事件

            for (WatchEvent<?> event : key.pollEvents()) {
                WatchEvent.Kind<?> kind = event.kind();
                Path fileName = (Path) event.context();

                System.out.printf("Event: %s on file: %s%n",
                        kind.name(), fileName);
            }

            key.reset();  // 重新激活 key
        }
    }
}
```

---

## 八、异步文件通道 AsynchronousFileChannel

Java 7 引入的异步 IO（AIO），支持 Future 和 CompletionHandler 两种编程模型。

### 8.1 Future 模式

```java
import java.nio.*;
import java.nio.channels.*;
import java.nio.file.*;
import java.util.concurrent.*;

public class AsyncFileFutureDemo {

    public static void main(String[] args) throws Exception {
        Path path = Path.of("async-test.txt");
        Files.writeString(path, "Initial content for async demo.\n");

        // 打开异步文件通道
        AsynchronousFileChannel channel = AsynchronousFileChannel.open(
                path,
                StandardOpenOption.READ,
                StandardOpenOption.WRITE
        );

        // ===== 异步写入 =====
        ByteBuffer writeBuffer = ByteBuffer.allocate(1024);
        writeBuffer.put("Async write via Future!\n".getBytes());
        writeBuffer.flip();

        Future<Integer> writeResult = channel.write(writeBuffer, 0);

        // 可以做一些其他事情...
        while (!writeResult.isDone()) {
            System.out.println("Writing...");
            Thread.sleep(100);
        }
        System.out.println("Bytes written: " + writeResult.get());

        // ===== 异步读取 =====
        ByteBuffer readBuffer = ByteBuffer.allocate(1024);
        Future<Integer> readResult = channel.read(readBuffer, 0);

        // 等待读取完成
        int bytesRead = readResult.get();
        readBuffer.flip();
        String content = new String(readBuffer.array(), 0, bytesRead);
        System.out.println("Read content: " + content);

        channel.close();
    }
}
```

### 8.2 CompletionHandler 模式

```java
import java.nio.*;
import java.nio.channels.*;
import java.nio.file.*;

public class AsyncFileHandlerDemo {

    public static void main(String[] args) throws Exception {
        Path path = Path.of("async-handler.txt");
        Files.writeString(path, "Hello from CompletionHandler!\n");

        AsynchronousFileChannel channel = AsynchronousFileChannel.open(
                path, StandardOpenOption.READ);

        ByteBuffer buffer = ByteBuffer.allocate(1024);

        // 异步读取，完成后回调
        channel.read(buffer, 0, null, new CompletionHandler<Integer, Void>() {
            @Override
            public void completed(Integer result, Void attachment) {
                buffer.flip();
                String content = new String(buffer.array(), 0, result);
                System.out.println("Async read completed: " + content);
                try { channel.close(); } catch (Exception e) { e.printStackTrace(); }
            }

            @Override
            public void failed(Throwable exc, Void attachment) {
                System.err.println("Async read failed: " + exc.getMessage());
            }
        });

        // 等待回调执行
        Thread.sleep(1000);
    }
}
```

---

## 九、Pipe 线程间 NIO 通信

Pipe 创建了两个 Channel 之间的单向数据通道，用于线程间通信。

### 9.1 Pipe 结构

```
  线程 A                        线程 B
    │                             │
    ▼                             │
 Source Channel                   │
    │                             │
    ▼                             │
  ┌──────────────────┐            │
  │      Pipe        │            │
  │   (环形缓冲区)    │            │
  └──────────────────┘            │
    │                             │
    ▼                             ▼
              Sink Channel  (写入端)
```

实际上：
- **SinkChannel**：写入端，写入数据到 Pipe
- **SourceChannel**：读取端，从 Pipe 读取数据

```
Thread A ──► SinkChannel ──► [Pipe Buffer] ──► SourceChannel ──► Thread B
```

### 9.2 使用示例

```java
import java.nio.*;
import java.nio.channels.*;
import java.nio.charset.*;

public class PipeDemo {

    public static void main(String[] args) throws Exception {
        // 1. 打开 Pipe
        Pipe pipe = Pipe.open();

        // 2. 生产者线程：写入数据到 SinkChannel
        Thread producer = new Thread(() -> {
            try {
                Pipe.SinkChannel sink = pipe.sink();
                String message = "Hello from Producer Thread!\n";
                ByteBuffer buffer = ByteBuffer.wrap(
                        message.getBytes(StandardCharsets.UTF_8));

                while (buffer.hasRemaining()) {
                    sink.write(buffer);
                }
                sink.close();
                System.out.println("[Producer] Message sent");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }, "Producer");

        // 3. 消费者线程：从 SourceChannel 读取数据
        Thread consumer = new Thread(() -> {
            try {
                Pipe.SourceChannel source = pipe.source();
                ByteBuffer buffer = ByteBuffer.allocate(1024);

                int bytesRead = source.read(buffer);
                buffer.flip();
                String received = StandardCharsets.UTF_8
                        .decode(buffer).toString();
                System.out.println("[Consumer] Received: " + received);
                source.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }, "Consumer");

        consumer.start();
        Thread.sleep(500);  // 确保消费者先启动
        producer.start();

        producer.join();
        consumer.join();
    }
}
```

### 9.3 Pipe 注意事项

| 注意点 | 说明 |
|-------|------|
| 单向通信 | 一个 Pipe 只能单向传输，双向需要两个 Pipe |
| 阻塞模式 | Pipe 的 Channel 默认是阻塞的，不支持 Selector |
| 缓冲区大小 | 由操作系统决定，通常几 KB |
| 关闭顺序 | 写入端关闭后，读取端读完剩余数据后返回 -1 |

---

## 十、IO / NIO / AIO 对比

| 对比维度 | BIO (IO) | NIO | AIO (NIO.2) |
|---------|----------|-----|-------------|
| **全称** | Blocking IO | Non-blocking IO | Asynchronous IO |
| **引入版本** | JDK 1.0 | JDK 1.4 | JDK 7 |
| **模型** | 同步阻塞 | 同步非阻塞 | 异步非阻塞 |
| **API 包** | `java.io.*` | `java.nio.*`<br>`java.nio.channels.*` | `java.nio.channels.*`<br>(Asynchronous*) |
| **数据读写** | Stream 顺序读写 | Buffer + Channel | AsynchronousChannel + Callback |
| **线程模型** | 一连接一线程 | 一 Selector 一线程（Reactor） | 操作系统回调（Proactor） |
| **阻塞点** | read/write 都阻塞 | select 阻塞，I/O 不阻塞 | 完全不阻塞，回调通知 |
| **编程模型** | 最简单 | 较复杂（状态机） | 中等（Future/Callback） |
| **操作系统** | 通用 | Linux: epoll<br>Windows: IOCP | Linux: epoll (模拟)<br>Windows: IOCP (原生) |
| **适用场景** | 连接数少、长连接 | 连接数多、短连接、高并发 | 文件异步读写、Windows 平台 |
| **典型框架** | 简单 Socket 程序 | Netty, Mina, Tomcat (NIO模式) | 较少直接使用 |

### 三种 IO 模型形象比喻

```
BIO (同步阻塞):
  你去餐厅点餐 → 坐在柜台前等 → 服务员做好后给你 → 才能离开
  (期间什么都干不了)

NIO (同步非阻塞):
  你去餐厅点餐 → 拿到一个号码牌 → 坐在休息区刷手机
  → 隔一会儿去柜台看一下好了没 → 好了就取餐
  (select = 去柜台看好了没)

AIO (异步非阻塞):
  你去餐厅点餐 → 坐在休息区 → 服务员做好后叫你的名字送到座位
  (完全不用操心，回调通知)
```

### 代码风格对比：读取文件内容

```java
// ===== BIO 方式 =====
try (BufferedReader br = new BufferedReader(
        new FileReader("data.txt"))) {
    String line;
    while ((line = br.readLine()) != null) {
        System.out.println(line);
    }
}

// ===== NIO 方式 (Buffer + Channel) =====
try (FileChannel channel = FileChannel.open(
        Path.of("data.txt"), StandardOpenOption.READ)) {
    ByteBuffer buffer = ByteBuffer.allocate(1024);
    while (channel.read(buffer) > 0) {
        buffer.flip();
        System.out.print(StandardCharsets.UTF_8.decode(buffer));
        buffer.clear();
    }
}

// ===== NIO.2 方式 (Files API) =====
Files.lines(Path.of("data.txt"))
     .forEach(System.out::println);

// ===== AIO 方式 (AsynchronousFileChannel) =====
AsynchronousFileChannel channel = AsynchronousFileChannel.open(
        Path.of("data.txt"), StandardOpenOption.READ);
ByteBuffer buffer = ByteBuffer.allocate(1024);
channel.read(buffer, 0, null, new CompletionHandler<Integer, Void>() {
    @Override
    public void completed(Integer bytes, Void att) {
        buffer.flip();
        System.out.print(StandardCharsets.UTF_8.decode(buffer));
    }
    @Override
    public void failed(Throwable exc, Void att) {
        exc.printStackTrace();
    }
});
```

### 性能参考（高并发场景）

```
连接数 100     │ BIO ★★★  │ NIO ★★★★★ │ AIO ★★★★
连接数 1000    │ BIO ★    │ NIO ★★★★★ │ AIO ★★★★
连接数 10000   │ BIO ✗    │ NIO ★★★★★ │ AIO ★★★★
连接数 100000  │ BIO ✗    │ NIO ★★★★  │ AIO ★★★★★
                (受线程数限制) (优秀)     (最优但 Linux 实现非纯异步)
```

---

## 附录：NIO 常用 API 速查表

### ByteBuffer 快捷操作

| 方法 | 作用 |
|-----|------|
| `ByteBuffer.allocate(n)` | 分配堆缓冲区 |
| `ByteBuffer.allocateDirect(n)` | 分配直接缓冲区 |
| `ByteBuffer.wrap(byte[])` | 包装数组 |
| `put(byte)` | 写入一个字节 |
| `get()` | 读取一个字节 |
| `putInt(int)` | 写入 4 字节 int |
| `getInt()` | 读取 4 字节 int |
| `asCharBuffer()` | 创建 CharBuffer 视图 |
| `order(ByteOrder)` | 设置字节序（大端/小端） |

### Files 常用方法

| 方法 | 作用 |
|-----|------|
| `Files.createFile(path)` | 创建文件 |
| `Files.createDirectories(path)` | 递归创建目录 |
| `Files.exists(path)` | 判断是否存在 |
| `Files.readAllBytes(path)` | 读取全部字节 |
| `Files.readAllLines(path)` | 读取所有行 |
| `Files.readString(path)` | 读取为字符串 (Java 11+) |
| `Files.writeString(path, str)` | 写入字符串 (Java 11+) |
| `Files.copy(src, dst)` | 复制文件 |
| `Files.move(src, dst)` | 移动/重命名文件 |
| `Files.delete(path)` | 删除文件 |
| `Files.size(path)` | 获取文件大小 |
| `Files.walk(path)` | 递归遍历目录 (Stream) |
| `Files.list(path)` | 列出目录 (Stream) |
| `Files.lines(path)` | 逐行读取 (Stream) |

### Selector 常用方法

| 方法 | 作用 |
|-----|------|
| `Selector.open()` | 创建选择器 |
| `channel.register(sel, ops)` | 注册 Channel |
| `selector.select()` | 阻塞等待就绪事件 |
| `selector.selectNow()` | 非阻塞检查就绪事件 |
| `selector.selectedKeys()` | 获取就绪 Key 集合 |
| `selector.wakeup()` | 唤醒阻塞的 select |
| `key.cancel()` | 取消注册 |
