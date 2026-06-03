# I/O

`I/O`（Input/Output）即输入和输出。数据从外部源（文件、网络、数据库等）读入内存的过程称为输入，从内存写出到外部目的地的过程称为输出。数据传输的过程类似于水流，因此称为 I/O 流。

---

## 一、I/O 流概述

### 1. 流的分类

Java I/O 流可以从三个维度进行分类：

| 分类维度 | 类型 | 说明 |
|----------|------|------|
| 数据流向 | 输入流 / 输出流 | 数据读入内存 / 从内存写出 |
| 数据单位 | 字节流 / 字符流 | 以字节（8 bit）为单位 / 以字符为单位 |
| 功能角色 | 节点流 / 处理流 | 直接连接数据源 / 在已有流上包装增强功能 |

### 2. 四大抽象基类

Java I/O 流的 40 多个类都派生自以下 4 个抽象基类：

| 基类 | 类型 | 说明 |
|------|------|------|
| `InputStream` | 字节输入流 | 所有字节输入流的父类 |
| `OutputStream` | 字节输出流 | 所有字节输出流的父类 |
| `Reader` | 字符输入流 | 所有字符输入流的父类 |
| `Writer` | 字符输出流 | 所有字符输出流的父类 |

### 3. 装饰器模式

Java I/O 体系大量使用**装饰器模式**（Decorator Pattern）。节点流负责直接连接数据源，处理流在节点流外层包装，提供缓冲、编码转换、数据格式化等增强功能。

```
// 典型装饰器嵌套结构：
// FileInputStream（节点流）→ BufferedInputStream（缓冲处理流）→ DataInputStream（数据格式处理流）
DataInputStream dis = new DataInputStream(
    new BufferedInputStream(
        new FileInputStream("data.bin")
    )
);
```

---

## 二、字节流

字节流以字节（byte，8 bit）为单位读写数据，适合处理二进制文件（图片、音频、视频等）。

### 1. InputStream（字节输入流）

`java.io.InputStream` 是所有字节输入流的抽象父类。

#### 常用方法

| 方法 | 说明 |
|------|------|
| `read()` | 读取下一个字节，返回 0~255，到达末尾返回 -1 |
| `read(byte[] b)` | 读取若干字节到数组 b，返回实际读取的字节数，等价于 `read(b, 0, b.length)` |
| `read(byte[] b, int off, int len)` | 从 off 位置开始，最多读取 len 个字节到数组 b |
| `skip(long n)` | 跳过 n 个字节，返回实际跳过的字节数 |
| `available()` | 返回不阻塞可读取的估计字节数 |
| `close()` | 关闭流并释放系统资源 |

#### Java 9+ 新增方法

| 方法 | 说明 |
|------|------|
| `readAllBytes()` | 读取所有字节，返回 `byte[]` |
| `readNBytes(byte[] b, int off, int len)` | 阻塞直到读取 len 个字节或到达末尾 |
| `transferTo(OutputStream out)` | 将全部字节传输到指定输出流，返回传输的字节数 |

#### 常用实现类

| 实现类 | 说明 |
|--------|------|
| `FileInputStream` | 从文件读取字节数据 |
| `ByteArrayInputStream` | 从内存中的字节数组读取 |
| `PipedInputStream` | 管道输入流，用于线程间通信（配合 `PipedOutputStream`） |
| `BufferedInputStream` | 带缓冲区的字节输入流，减少 IO 次数 |
| `DataInputStream` | 支持读取 Java 基本数据类型（int、double 等） |

### 2. OutputStream（字节输出流）

`java.io.OutputStream` 是所有字节输出流的抽象父类。

#### 常用方法

| 方法 | 说明 |
|------|------|
| `write(int b)` | 写入一个字节的低 8 位 |
| `write(byte[] b)` | 将数组 b 全部写入，等价于 `write(b, 0, b.length)` |
| `write(byte[] b, int off, int len)` | 从 off 位置开始写入 len 个字节 |
| `flush()` | 将缓冲区中的数据强制写出 |
| `close()` | 关闭流并释放系统资源 |

#### 常用实现类

| 实现类 | 说明 |
|--------|------|
| `FileOutputStream` | 将字节数据写入文件 |
| `ByteArrayOutputStream` | 将数据写入内存中的字节数组 |
| `PipedOutputStream` | 管道输出流，用于线程间通信（配合 `PipedInputStream`） |
| `BufferedOutputStream` | 带缓冲区的字节输出流 |
| `DataOutputStream` | 支持写入 Java 基本数据类型 |

### 3. 代码示例

```java
// 文件复制（使用 try-with-resources 自动关闭资源）
try (InputStream in = new FileInputStream("source.jpg");
     OutputStream out = new FileOutputStream("target.jpg")) {

    byte[] buffer = new byte[8192];
    int bytesRead;
    while ((bytesRead = in.read(buffer)) != -1) {
        out.write(buffer, 0, bytesRead);
    }
    out.flush();
}
// try-with-resources 自动调用 close()，无需手动关闭
```

> **推荐**：始终使用 `try-with-resources`（Java 7+）管理流资源，避免资源泄漏。

---

## 三、字符流

字符流以字符（char，16 bit）为单位读写数据，内部处理了字符编码转换，适合处理文本文件。

### 1. Reader（字符输入流）

`java.io.Reader` 是所有字符输入流的抽象父类。

#### 常用方法

| 方法 | 说明 |
|------|------|
| `read()` | 读取一个字符，返回 0~65535，到达末尾返回 -1 |
| `read(char[] cbuf)` | 读取若干字符到数组，返回实际读取的字符数 |
| `read(char[] cbuf, int off, int len)` | 从 off 位置开始，最多读取 len 个字符 |
| `skip(long n)` | 跳过 n 个字符 |
| `close()` | 关闭流并释放资源 |

### 2. Writer（字符输出流）

`java.io.Writer` 是所有字符输出流的抽象父类。

#### 常用方法

| 方法 | 说明 |
|------|------|
| `write(int c)` | 写入单个字符 |
| `write(char[] cbuf)` | 写入字符数组 |
| `write(char[] cbuf, int off, int len)` | 从 off 位置开始写入 len 个字符 |
| `write(String str)` | 写入字符串 |
| `write(String str, int off, int len)` | 写入字符串的一部分 |
| `append(CharSequence csq)` | 追加字符序列，返回 Writer 本身（可链式调用） |
| `append(char c)` | 追加单个字符 |
| `flush()` | 刷新缓冲区 |
| `close()` | 关闭流并释放资源 |

### 3. 转换流

转换流是字节流与字符流之间的桥梁，负责编码转换。

| 类 | 说明 |
|----|------|
| `InputStreamReader` | 字节输入流 → 字符输入流，解码时使用指定字符集 |
| `OutputStreamWriter` | 字符输出流 → 字节输出流，编码时使用指定字符集 |

其子类 `FileReader` 和 `FileWriter` 是简化封装，但**默认使用平台编码**，无法指定字符集。需要指定编码时应使用转换流：

```java
// 指定 UTF-8 编码读取文件
try (BufferedReader reader = new BufferedReader(
        new InputStreamReader(new FileInputStream("data.txt"), StandardCharsets.UTF_8))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}
```

### 4. 字符编码

| 编码 | 说明 |
|------|------|
| `ASCII` | 7 位，128 个字符，英文专用 |
| `ISO-8859-1` | 8 位，256 个字符，西欧语言 |
| `GBK` | 中文编码，兼容 ASCII，一个汉字 2 字节 |
| `UTF-8` | Unicode 变长编码，英文 1 字节，中文 3 字节（**推荐**） |
| `UTF-16` | Unicode 定长编码，每个字符 2 或 4 字节 |

> **乱码原因**：编码和解码使用的字符集不一致。例如用 GBK 编码的文本用 UTF-8 解码就会出现乱码。

### 5. 代码示例

```java
// 字符流复制文本文件（指定 UTF-8 编码）
try (BufferedReader reader = new BufferedReader(
            new InputStreamReader(new FileInputStream("input.txt"), StandardCharsets.UTF_8));
     BufferedWriter writer = new BufferedWriter(
            new OutputStreamWriter(new FileOutputStream("output.txt"), StandardCharsets.UTF_8))) {

    String line;
    while ((line = reader.readLine()) != null) {
        writer.write(line);
        writer.newLine(); // 写入平台相关的换行符
    }
}
```

---

## 四、缓冲流

缓冲流在底层流外包裹一层缓冲区（默认 8192 字节/字符），减少实际 IO 操作次数，显著提升读写性能。

### 1. 字节缓冲流

| 类 | 说明 |
|----|------|
| `BufferedInputStream` | 字节输入缓冲流，内部维护 byte[] 缓冲区 |
| `BufferedOutputStream` | 字节输出缓冲流，写入时先进入缓冲区，满或 flush 时才真正写出 |

### 2. 字符缓冲流

| 类 | 说明 |
|----|------|
| `BufferedReader` | 字符输入缓冲流，提供 `readLine()` 按行读取 |
| `BufferedWriter` | 字符输出缓冲流，提供 `newLine()` 写入换行符 |

```java
// BufferedReader 按行读取
try (BufferedReader br = new BufferedReader(new FileReader("log.txt"))) {
    String line;
    while ((line = br.readLine()) != null) {
        System.out.println(line);
    }
}
```

### 3. 性能说明

- **无缓冲**：每次 `read()`/`write()` 都触发一次系统调用，开销大
- **有缓冲**：批量读写，系统调用次数大幅减少
- 缓冲区默认大小 8192，可根据场景通过构造函数指定
- 大文件拷贝时，缓冲流性能提升可达 **10~100 倍**

---

## 五、其他常用流

### 1. 数据流（DataInputStream / DataOutputStream）

支持直接读写 Java 基本数据类型（int、long、double、boolean 等），写入的数据与平台无关（大端序）。

```java
// 写入
try (DataOutputStream dos = new DataOutputStream(new FileOutputStream("data.bin"))) {
    dos.writeInt(100);
    dos.writeDouble(3.14);
    dos.writeUTF("你好"); // 写入带长度前缀的 UTF-8 字符串
}

// 读取（必须按写入顺序读取）
try (DataInputStream dis = new DataInputStream(new FileInputStream("data.bin"))) {
    int i = dis.readInt();       // 100
    double d = dis.readDouble(); // 3.14
    String s = dis.readUTF();    // "你好"
}
```

### 2. 打印流（PrintStream / PrintWriter）

| 类 | 说明 |
|----|------|
| `PrintStream` | 字节打印流，`System.out` 和 `System.err` 都是 `PrintStream` 实例 |
| `PrintWriter` | 字符打印流，支持 `printf()`/`format()` 格式化输出 |

特点：
- **不会抛出 IOException**，异常被内部吞掉，通过 `checkError()` 检查
- 支持 `print()`、`println()`、`printf()`、`format()` 等便捷方法
- 可设置自动刷新（`autoFlush`），每次 `println` 后自动 `flush`

### 3. 管道流（PipedInputStream / PipedOutputStream）

用于**线程间通信**，一个线程写入管道，另一个线程从管道读取。

```java
PipedInputStream pis = new PipedInputStream();
PipedOutputStream pos = new PipedOutputStream(pis); // 连接管道

// 写入线程
new Thread(() -> {
    try (pos) {
        pos.write("Hello from thread!".getBytes());
    } catch (IOException e) {
        e.printStackTrace();
    }
}).start();

// 读取线程
try (pis) {
    byte[] buf = new byte[1024];
    int len = pis.read(buf);
    System.out.println(new String(buf, 0, len));
}
```

> **注意**：管道流必须在**不同线程**中使用，同一线程读写会导致死锁。

### 4. 序列流（SequenceInputStream）

将多个输入流按顺序串联为一个逻辑流，读完第一个流后自动切换到第二个。

```java
try (InputStream s1 = new FileInputStream("part1.txt");
     InputStream s2 = new FileInputStream("part2.txt");
     SequenceInputStream sis = new SequenceInputStream(s1, s2)) {

    byte[] buf = new byte[8192];
    int len;
    while ((len = sis.read(buf)) != -1) {
        System.out.write(buf, 0, len);
    }
}
```

### 5. 随机访问流（RandomAccessFile）

`RandomAccessFile` 支持在文件的**任意位置**进行读写，通过 `seek()` 方法移动文件指针。

#### 访问模式

| 模式 | 说明 |
|------|------|
| `r` | 只读 |
| `rw` | 读写 |
| `rws` | 读写 + 同步更新文件内容和元数据到磁盘 |
| `rwd` | 读写 + 同步更新文件内容到磁盘（不保证元数据） |

```java
try (RandomAccessFile raf = new RandomAccessFile("data.dat", "rw")) {
    raf.writeInt(42);       // 写入 4 字节整数
    raf.seek(0);            // 移动到文件开头
    int value = raf.readInt(); // 读回 42

    raf.seek(raf.length()); // 移动到文件末尾（追加）
    raf.writeUTF("append");
}
```

---

## 六、序列化与反序列化

序列化是将 Java 对象转换为字节序列的过程，反序列化是将字节序列还原为对象的过程。Java I/O 通过 `ObjectOutputStream` 和 `ObjectInputStream` 提供支持。

关键要点：
- 对象必须实现 `Serializable` 接口（标记接口）
- `serialVersionUID` 用于版本控制，未显式声明时 JVM 自动计算
- `transient` 修饰的字段不参与序列化
- 存在安全风险，Java 9+ 推荐使用 `ObjectInputFilter` 进行过滤

> 详细内容请参考：[序列化与反序列化](../concepts/serialization-and-deserialization/README.md)

---

## 七、File 类与 NIO.2 文件操作

### 1. File 类

`java.io.File` 是 Java 早期（JDK 1.0）提供的文件和目录抽象，可表示文件或目录的路径，并提供基本的文件操作。

#### 常用方法

| 方法 | 说明 |
|------|------|
| `exists()` | 判断文件或目录是否存在 |
| `isFile()` / `isDirectory()` | 判断是文件还是目录 |
| `createNewFile()` | 创建新文件（不存在时返回 true） |
| `mkdir()` / `mkdirs()` | 创建目录（`mkdirs` 可创建多级） |
| `delete()` | 删除文件或空目录 |
| `list()` / `listFiles()` | 列出目录下的文件名 / File 对象 |
| `length()` | 返回文件长度（字节） |
| `renameTo(File dest)` | 重命名或移动文件 |
| `getAbsolutePath()` | 获取绝对路径 |

```java
File file = new File("logs/app.log");
if (!file.exists()) {
    file.getParentFile().mkdirs(); // 确保父目录存在
    file.createNewFile();
}
System.out.println("文件大小: " + file.length() + " bytes");
```

> **局限**：`File` 类方法返回 `boolean` 而非抛出异常，出错时难以定位原因；不支持符号链接、文件属性查询等。Java 7 引入 NIO.2 解决了这些问题。

### 2. NIO.2：Path 与 Files

Java 7（NIO.2）引入了 `Path` 接口和 `Files` 工具类，是现代 Java 文件操作的推荐方式。

#### Path 接口

`Path` 表示文件系统中的一个路径，是 `File` 的现代化替代。

```java
Path path = Paths.get("logs/app.log");           // JDK 7+
Path path2 = Path.of("logs/app.log");             // JDK 11+（推荐）

System.out.println("文件名: " + path.getFileName());
System.out.println("父目录: " + path.getParent());
System.out.println("是否绝对路径: " + path.isAbsolute());
```

#### Files 工具类

`Files` 提供了大量静态方法用于文件操作，替代 `File` 类的大部分功能：

| 方法 | 说明 |
|------|------|
| `Files.exists(path)` | 判断路径是否存在 |
| `Files.createDirectory(path)` | 创建目录 |
| `Files.createDirectories(path)` | 创建多级目录 |
| `Files.delete(path)` | 删除文件（失败抛异常） |
| `Files.copy(source, target, options)` | 复制文件 |
| `Files.move(source, target, options)` | 移动/重命名文件 |
| `Files.readAllBytes(path)` | 读取文件所有字节 |
| `Files.readAllLines(path, charset)` | 按行读取文件 |
| `Files.writeString(path, text)` | 写入字符串（JDK 11+） |
| `Files.lines(path)` | 返回 `Stream<String>`，适合大文件逐行处理 |
| `Files.walk(path)` | 递归遍历目录树，返回 `Stream<Path>` |
| `Files.size(path)` | 获取文件大小 |
| `Files.isRegularFile(path)` | 是否为普通文件 |
| `Files.isDirectory(path)` | 是否为目录 |

```java
// 读取文件所有行
List<String> lines = Files.readAllLines(Path.of("config.txt"), StandardCharsets.UTF_8);

// 大文件逐行处理（惰性流，不会一次加载全部到内存）
try (Stream<String> stream = Files.lines(Path.of("big.log"))) {
    stream.filter(line -> line.contains("ERROR"))
          .forEach(System.out::println);
}

// 递归查找所有 .java 文件
try (Stream<Path> paths = Files.walk(Path.of("src"))) {
    paths.filter(p -> p.toString().endsWith(".java"))
         .forEach(System.out::println);
}
```

---

## 八、NIO（New I/O）

Java 7 引入的 NIO（New I/O，也称 Non-blocking I/O）是对传统 I/O 的重大升级，核心变化是**面向块**和**非阻塞**。

### 1. NIO 与 BIO 对比

| 特性 | BIO（传统 IO） | NIO（新 IO） |
|------|----------------|--------------|
| 数据单位 | 面向流（Stream） | 面向块（Block/Buffer） |
| 阻塞行为 | 阻塞 | 非阻塞 |
| 线程模型 | 一个连接一个线程 | 一个线程管理多个连接（Selector） |
| 适用场景 | 连接数少、短连接 | 连接数多、长连接（聊天、推送） |

### 2. 三大核心组件

#### Buffer（缓冲区）

Buffer 是 NIO 中数据的容器，本质是一个数组，通过 `position`、`limit`、`capacity` 三个属性管理数据读写：

| 属性 | 说明 |
|------|------|
| `capacity` | 缓冲区总容量，创建后不可变 |
| `position` | 当前读写位置 |
| `limit` | 可读/可写的上界 |

常用操作：

| 方法 | 说明 |
|------|------|
| `allocate(capacity)` | 分配指定容量的缓冲区 |
| `put(data)` | 写入数据 |
| `flip()` | 切换为读模式（`limit = position`，`position = 0`） |
| `get()` | 读取数据 |
| `clear()` | 清空缓冲区，准备重新写入 |
| `compact()` | 清空已读数据，保留未读数据 |

```java
ByteBuffer buffer = ByteBuffer.allocate(1024);

// 写入
buffer.put("Hello NIO".getBytes());

// 切换为读模式
buffer.flip();

// 读取
byte[] data = new byte[buffer.remaining()]; // remaining = limit - position
buffer.get(data);
System.out.println(new String(data)); // Hello NIO
```

常用 Buffer 类型：`ByteBuffer`、`CharBuffer`、`IntBuffer`、`LongBuffer`、`FloatBuffer`、`DoubleBuffer`、`ShortBuffer`。

#### Channel（通道）

Channel 是 NIO 中的数据通道，替代了传统 IO 的流（Stream）。Channel 是**双向**的（可读可写），而 Stream 是单向的。

| Channel 类型 | 说明 |
|--------------|------|
| `FileChannel` | 文件读写 |
| `SocketChannel` | TCP 客户端 |
| `ServerSocketChannel` | TCP 服务端 |
| `DatagramChannel` | UDP 通信 |

```java
// FileChannel 读写文件
try (FileChannel channel = FileChannel.open(Path.of("data.txt"),
        StandardOpenOption.READ, StandardOpenOption.WRITE, StandardOpenOption.CREATE)) {

    ByteBuffer buffer = ByteBuffer.wrap("Hello Channel".getBytes());
    channel.write(buffer);

    buffer.flip();
    channel.read(buffer, 0);
}
```

#### Selector（多路复用器）

Selector 是 NIO 的核心，允许**一个线程管理多个 Channel**。通过 `select()` 方法轮询已注册的 Channel，返回就绪的 Channel 集合。

```java
Selector selector = Selector.open();

// 注册 Channel 到 Selector，监听可读事件
serverChannel.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select(); // 阻塞直到有 Channel 就绪
    Set<SelectionKey> keys = selector.selectedKeys();
    Iterator<SelectionKey> it = keys.iterator();

    while (it.hasNext()) {
        SelectionKey key = it.next();
        it.remove();

        if (key.isAcceptable()) {
            // 处理新连接
        } else if (key.isReadable()) {
            // 处理读数据
        }
    }
}
```

---

## 九、IO 模型

### 1. 前置概念

| 概念 | 说明 |
|------|------|
| **用户态 / 内核态** | 用户程序运行在用户态，操作系统核心运行在内核态。用户态不能直接访问硬件和受保护内存 |
| **系统调用** | 用户态请求内核态服务的唯一方式（如 read、write、open） |
| **DMA** | Direct Memory Access，独立的硬件控制器，允许外设与内存直接传输数据，无需 CPU 参与 |
| **阻塞** | 线程发起 IO 请求后，在数据就绪前一直挂起等待 |

### 2. BIO（同步阻塞 I/O）

BIO 是最传统的 IO 模型。应用程序发起 IO 请求后，线程被阻塞，直到数据准备好并被拷贝到用户空间才返回。

**特点**：
- 每个连接需要一个独立线程处理
- 线程在等待数据时处于阻塞状态，浪费系统资源
- 适合连接数较少且固定的场景

```
客户端1 ──► 线程1（阻塞等待 → 读取 → 处理 → 响应）
客户端2 ──► 线程2（阻塞等待 → 读取 → 处理 → 响应）
客户端N ──► 线程N（阻塞等待 → 读取 → 处理 → 响应）
```

### 3. NIO（同步非阻塞 I/O + IO 多路复用）

#### 同步非阻塞

应用程序发起 IO 请求后，如果数据未就绪，系统调用**立即返回**（不阻塞），应用程序需要不断轮询检查数据是否就绪。

**问题**：频繁轮询消耗大量 CPU 资源。

#### IO 多路复用

通过一次系统调用同时监控多个 IO 事件，当某个连接的数据就绪时才通知应用程序，避免了无效轮询。

| 多路复用机制 | 说明 | 最大连接数 |
|-------------|------|-----------|
| `select` | 最早的多路复用，几乎所有 OS 都支持 | ~1024 |
| `poll` | select 的改进版，使用链表替代位图 | 无硬性限制 |
| `epoll` | Linux 2.6+ 引入，基于事件驱动，效率最高 | 无限制（受内存约束） |

**Java NIO 的 Selector** 底层使用的就是操作系统的多路复用机制（Linux 上是 epoll，macOS 上是 kqueue，Windows 上是 select）。

```
一个线程（Selector）──► 监控多个 Channel ──► 数据就绪时处理
         │
         ├── Channel 1（客户端1）
         ├── Channel 2（客户端2）
         └── Channel N（客户端N）
```

### 4. AIO（异步非阻塞 I/O）

AIO（也称 NIO2 异步模式）是 Java 7 引入的异步 IO 模型。应用程序发起 IO 请求后立即返回，操作系统在 IO 完成后通过**回调**通知应用程序。

**特点**：
- 完全异步，无需轮询
- 操作系统完成全部 IO 操作后通知应用
- 编程模型更复杂（基于回调 / `Future`）

```java
// AIO 异步读取文件
AsynchronousFileChannel channel = AsynchronousFileChannel.open(
    Path.of("data.txt"), StandardOpenOption.READ);

ByteBuffer buffer = ByteBuffer.allocate(1024);
Future<Integer> future = channel.read(buffer, 0);

// 可以做其他事情...
while (!future.isDone()) {
    System.out.println("doing other work...");
}

buffer.flip();
byte[] data = new byte[buffer.remaining()];
buffer.get(data);
System.out.println(new String(data));
```

> **Netty 弃用 AIO 的原因**：Netty 曾尝试使用 AIO，但在 Linux 上性能并未显著提升（Linux 的 AIO 实现不如 epoll 成熟），且编程复杂度大幅增加，最终选择基于 NIO + epoll 的方案。

### 5. 三种模型对比

| 特性 | BIO | NIO（多路复用） | AIO |
|------|-----|------------------|-----|
| IO 模型 | 同步阻塞 | 同步非阻塞 + 多路复用 | 异步非阻塞 |
| 编程复杂度 | 简单 | 中等 | 复杂 |
| 线程模型 | 一连接一线程 | 一线程多连接 | 回调/Future |
| 适用场景 | 连接数少、短连接 | 连接数多、长连接 | 重量级异步操作 |
| 典型框架 | Tomcat（早期） | Netty、Mina | 较少使用 |
| 数据就绪时 | 阻塞等待 | Selector 通知 | 回调通知 |

---

## 十、最佳实践

1. **始终使用 try-with-resources**（Java 7+）自动关闭流，防止资源泄漏
2. **用缓冲流包装原始流**，减少系统调用次数（`BufferedInputStream`、`BufferedReader`）
3. **大文件操作优先使用 NIO**（`FileChannel` + `MappedByteBuffer` 或 `transferTo`）
4. **文本操作使用字符流**（`Reader`/`Writer`），二进制操作使用字节流（`InputStream`/`OutputStream`）
5. **明确指定字符编码**，避免依赖平台默认编码导致乱码
6. **高并发网络通信使用 NIO + Selector**，避免 BIO 的线程资源浪费
7. **文件操作优先使用 NIO.2 的 `Files` / `Path`**，替代 `File` 类（API 更完善、异常更清晰）
8. **注意 `flush()` 与 `close()` 的关系**：`close()` 内部会调用 `flush()`，但不能只依赖 `flush()` 而忽略 `close()`
