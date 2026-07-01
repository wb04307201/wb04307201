<!--
module:
  parent: java
  slug: java/zero-copy
  type: article
  category: 主模块子文章
  summary: 零拷贝
-->

# 零拷贝

零拷贝（Zero-copy）是指在数据传输过程中，**避免数据在内核空间与用户空间之间的 CPU 拷贝**。传统的 IO 操作需要将数据从内核缓冲区复制到用户缓冲区，再由用户缓冲区复制到内核的 socket 缓冲区，中间涉及多次 CPU 参与的拷贝。零拷贝通过减少甚至消除这些 CPU 拷贝，显著提升 IO 传输效率。

---
## 引言：反直觉代码
零拷贝 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、前置知识

### 1. 内核空间与用户空间

操作系统将虚拟内存划分为两部分：

| 空间 | 说明 |
|------|------|
| **内核空间（Kernel-space）** | 操作系统内核独占，常驻内存，拥有硬件访问权限。用户程序不能直接读写 |
| **用户空间（User-space）** | 每个进程独享的虚拟内存，进程间完全隔离。进程结束时自动释放 |

用户态进程如需使用系统资源（文件、网络等），必须通过**系统调用**进入内核态，由内核代为操作。

### 2. DMA（直接内存访问）

DMA（Direct Memory Access）是主板上的独立硬件控制器，允许外设（磁盘、网卡等）与内存之间**直接传输数据**，无需 CPU 参与。CPU 只需在传输前后进行设置和确认，传输过程中可以执行其他任务。

DMA 传输的两种模式：
- **标准 DMA**：外设 → 内核缓冲区（或反向），每次传输一块连续数据
- **scatter/gather DMA（SG-DMA）**：支持将数据从多个非连续内存区域收集（gather）传输，或将数据分散（scatter）到多个区域

### 3. 上下文切换

进程在用户态和内核态之间切换时，需要保存和恢复 CPU 寄存器、栈等上下文信息，这个过程称为**上下文切换**。每次切换都有性能开销。

---

## 二、IO 拷贝机制

以「客户端从服务器下载文件」为例，服务端需要做两件事：从磁盘读取文件内容，再通过网络发送给客户端。

### 1. 传统 read/write 拷贝

使用 `read()` + `write()` 的传统方式，数据从磁盘到网卡的完整流程如下：

```
read() 阶段：
  ① CPU 上下文切换到内核态（第 1 次切换）
  ② DMA 将磁盘数据拷贝到内核缓冲区（第 1 次 DMA 拷贝）
  ③ CPU 将内核缓冲区数据拷贝到用户缓冲区（第 1 次 CPU 拷贝）
  ④ CPU 上下文切换回用户态（第 2 次切换）

write() 阶段：
  ⑤ CPU 上下文切换到内核态（第 3 次切换）
  ⑥ CPU 将用户缓冲区数据拷贝到 socket 缓冲区（第 2 次 CPU 拷贝）
  ⑦ DMA 将 socket 缓冲区数据发送到网卡（第 2 次 DMA 拷贝）
  ⑧ CPU 上下文切换回用户态（第 4 次切换）
```

**汇总**：2 次 DMA 拷贝 + 2 次 CPU 拷贝 + 4 次上下文切换 = 共 **4 次数据拷贝，4 次上下文切换**。

### 2. mmap 内存映射

`mmap`（Memory Mapped I/O）将用户缓冲区的虚拟地址映射到内核缓冲区的物理内存上，**省去了内核缓冲区到用户缓冲区的 CPU 拷贝**，用户空间可以直接访问内核缓冲区的数据。

```
mmap() 阶段：
  ① CPU 上下文切换到内核态（第 1 次切换）
  ② DMA 将磁盘数据拷贝到内核缓冲区（第 1 次 DMA 拷贝）
  ③ 建立用户缓冲区与内核缓冲区的内存映射（无数据拷贝）
  ④ CPU 上下文切换回用户态（第 2 次切换）

write() 阶段：
  ⑤ CPU 上下文切换到内核态（第 3 次切换）
  ⑥ CPU 将内核缓冲区数据拷贝到 socket 缓冲区（第 1 次 CPU 拷贝）
  ⑦ DMA 将 socket 缓冲区数据发送到网卡（第 2 次 DMA 拷贝）
  ⑧ CPU 上下文切换回用户态（第 4 次切换）
```

**汇总**：2 次 DMA 拷贝 + 1 次 CPU 拷贝 + 4 次上下文切换 = 共 **3 次数据拷贝，4 次上下文切换**。

相比传统方式，**减少了 1 次 CPU 拷贝**。

### 3. sendfile 系统调用

Linux 2.1 内核引入 `sendfile()` 系统调用，数据直接在内核空间内完成从文件到 socket 的传输，**无需经过用户空间**。

```
sendfile() 阶段：
  ① CPU 上下文切换到内核态（第 1 次切换）
  ② DMA 将磁盘数据拷贝到内核缓冲区（第 1 次 DMA 拷贝）
  ③ CPU 将内核缓冲区数据拷贝到 socket 缓冲区（第 1 次 CPU 拷贝）
  ④ DMA 将 socket 缓冲区数据发送到网卡（第 2 次 DMA 拷贝）
  ⑤ CPU 上下文切换回用户态（第 2 次切换）
```

**汇总**：2 次 DMA 拷贝 + 1 次 CPU 拷贝 + 2 次上下文切换 = 共 **3 次数据拷贝，2 次上下文切换**。

相比 mmap，**减少了 2 次上下文切换**，且无需建立内存映射。

### 4. sendfile + DMA scatter/gather

Linux 2.4 内核对 `sendfile()` 做了优化，引入 SG-DMA 技术。内核缓冲区不再需要将数据拷贝到 socket 缓冲区，而是将数据的**描述信息**（内存地址 + 长度）传递给网卡，由网卡通过 DMA 直接从内核缓冲区读取数据。

```
sendfile() with SG-DMA 阶段：
  ① CPU 上下文切换到内核态（第 1 次切换）
  ② DMA 将磁盘数据拷贝到内核缓冲区（第 1 次 DMA 拷贝）
  ③ CPU 将数据的描述信息（地址+长度）传递给 socket 缓冲区（无数据拷贝）
  ④ DMA 根据描述信息直接从内核缓冲区读取数据发送到网卡（第 2 次 DMA 拷贝）
  ⑤ CPU 上下文切换回用户态（第 2 次切换）
```

**汇总**：2 次 DMA 拷贝 + 0 次 CPU 拷贝 + 2 次上下文切换 = 共 **2 次数据拷贝，2 次上下文切换**。

这是操作系统层面**真正意义上的零拷贝**——全程无 CPU 参与数据拷贝。

> **前提**：需要网卡硬件支持 SG-DMA（Scatter/Gather DMA）。

### 5. splice

Linux 2.6.17 内核引入 `splice()` 系统调用。与 `sendfile()` 不同的是，`splice()` **不依赖硬件支持**。

它在内核缓冲区与 socket 缓冲区之间建立一个**管道（pipe）**，数据通过管道在内核空间内直接流动，无需 CPU 拷贝。

```
splice() 阶段：
  ① CPU 上下文切换到内核态（第 1 次切换）
  ② DMA 将磁盘数据拷贝到内核缓冲区（第 1 次 DMA 拷贝）
  ③ 在内核缓冲区与 socket 缓冲区之间建立管道（无数据拷贝）
  ④ DMA 将 socket 缓冲区数据发送到网卡（第 2 次 DMA 拷贝）
  ⑤ CPU 上下文切换回用户态（第 2 次切换）
```

**汇总**：2 次 DMA 拷贝 + 0 次 CPU 拷贝 + 2 次上下文切换 = 共 **2 次数据拷贝，2 次上下文切换**。

同样是真正的零拷贝，但不要求网卡硬件支持 SG-DMA。

---

## 三、IO 拷贝机制对比

| 拷贝机制 | 系统调用 | CPU 拷贝 | DMA 拷贝 | 上下文切换 | 特点 |
|----------|----------|----------|----------|------------|------|
| 传统方式 | read + write | 2 | 2 | 4 | 资源消耗大，效率最低 |
| mmap | mmap + write | 1 | 2 | 4 | 省去内核到用户的 CPU 拷贝，适合随机读写 |
| sendfile | sendfile | 1 | 2 | 2 | 数据不经过用户空间，上下文切换减半 |
| sendfile + SG-DMA | sendfile | 0 | 2 | 2 | 真正零拷贝，需要网卡硬件支持 |
| splice | splice | 0 | 2 | 2 | 真正零拷贝，不依赖硬件，编程稍复杂 |

---

## 四、Java 零拷贝实现

Java 通过 NIO 支持了 `mmap` 和 `sendfile` 两种零拷贝机制。

### 1. MappedByteBuffer（mmap）

`MappedByteBuffer` 是 `ByteBuffer` 的子类，通过内存映射将文件直接映射到内存中访问。底层调用操作系统的 `mmap` 系统调用。

```java
try (FileChannel readChannel = FileChannel.open(
            Paths.get("source.dat"), StandardOpenOption.READ);
     FileChannel writeChannel = FileChannel.open(
            Paths.get("target.dat"), StandardOpenOption.WRITE, StandardOpenOption.CREATE)) {

    // 将文件映射到内存（只读模式，映射 40MB）
    MappedByteBuffer mappedBuffer = readChannel.map(
            FileChannel.MapMode.READ_ONLY, 0, 1024L * 1024 * 40);

    // 写入目标文件
    writeChannel.write(mappedBuffer);
}
```

**适用场景**：大文件的随机读写（如数据库页文件、日志文件索引）。

**限制与注意事项**：

| 问题 | 说明 |
|------|------|
| 内存泄漏 | `MappedByteBuffer` 映射的内存由操作系统管理，JVM GC 不会自动回收，需等 `DirectByteBuffer` 关联的 Cleaner 触发 |
| 地址空间限制 | 32 位 JVM 上单个映射最大约 1.5~2 GB；64 位 JVM 无此限制 |
| 小文件效率低 | 映射建立的开销可能超过直接读取，适合大文件（通常 > 几 MB） |
| 无法主动解除映射 | Java 没有提供 `unmap()` 方法，只能通过反射调用 `sun.misc.Cleaner` 或等待 GC（Java 14+ 提供 `MappedByteBuffer.force()` 但不能解除映射） |

### 2. FileChannel.transferTo（sendfile）

`FileChannel.transferTo()` 底层调用操作系统的 `sendfile` 系统调用，实现文件到通道的高效传输。

```java
try (FileChannel src = FileChannel.open(
            Paths.get("source.dat"), StandardOpenOption.READ);
     FileChannel dest = FileChannel.open(
            Paths.get("target.dat"), StandardOpenOption.WRITE, StandardOpenOption.CREATE)) {

    // 零拷贝传输，底层使用 sendfile
    long transferred = src.transferTo(0, src.size(), dest);
    System.out.println("传输了 " + transferred + " 字节");
}
```

**适用场景**：文件到文件、文件到网络的顺序传输（如文件服务器、消息队列日志传输）。

> **注意**：`transferTo()` 不保证一定使用零拷贝，取决于操作系统是否支持 `sendfile`。Linux 2.1+ 支持，Windows 的 `TransmitFile` 也支持。

### 3. DirectByteBuffer

`DirectByteBuffer` 分配的内存位于 JVM 堆外（Off-Heap），直接由操作系统管理，JVM 通过 JNI 直接操作这块内存。

```java
// 分配 1MB 直接内存
ByteBuffer directBuffer = ByteBuffer.allocateDirect(1024 * 1024);

// 写入数据
directBuffer.put("Hello Direct Memory".getBytes());

// 切换为读模式
directBuffer.flip();
byte[] data = new byte[directBuffer.remaining()];
directBuffer.get(data);
System.out.println(new String(data));
```

**堆内存 vs 直接内存**：

| 特性 | HeapByteBuffer（堆内存） | DirectByteBuffer（直接内存） |
|------|--------------------------|------------------------------|
| 分配位置 | JVM 堆内 | JVM 堆外（操作系统内存） |
| GC 管理 | JVM GC 管理 | 不受 GC 直接管理，通过 Cleaner 回收 |
| IO 性能 | 需要额外拷贝到内核 | 直接与内核交互，减少一次拷贝 |
| 分配开销 | 低 | 高（涉及系统调用） |
| 适用场景 | 短生命周期、小数据 | 长生命周期、大数据、频繁 IO |

> **注意**：频繁创建和销毁 `DirectByteBuffer` 会给系统带来压力。Netty 等框架通过**内存池**（如 `PooledByteBufAllocator`）来复用直接内存。

---

## 五、Netty 中的零拷贝

Netty 中的「零拷贝」与操作系统层面的零拷贝含义略有不同。操作系统零拷贝侧重于减少内核空间与用户空间之间的数据拷贝，而 Netty 零拷贝侧重于**在用户空间内避免不必要的内存复制**。

### 1. CompositeByteBuf

`CompositeByteBuf` 将多个 `ByteBuf` 组合为一个逻辑 Buffer，**不实际拷贝数据**，只是维护引用列表。

```
// 传统方式：需要分配新数组并拷贝
byte[] result = new byte[buf1.length + buf2.length];
System.arraycopy(buf1, 0, result, 0, buf1.length);
System.arraycopy(buf2, 0, result, buf1.length, buf2.length);

// Netty 方式：零拷贝组合
CompositeByteBuf composite = Unpooled.compositeBuffer();
composite.addComponents(true, buf1, buf2); // 逻辑合并，无数据拷贝
```

**场景**：HTTP 消息由 header + body 组成，分别处理后需要合并发送，使用 `CompositeByteBuf` 避免了中间拷贝。

### 2. FileRegion

`FileRegion` 封装了 `FileChannel.transferTo()`，实现文件传输时的零拷贝。

```java
// 服务端发送文件给客户端（零拷贝）
public void channelRead(ChannelHandlerContext ctx, Object msg) {
    RandomAccessFile raf = new RandomAccessFile("large-file.dat", "r");
    FileRegion region = new DefaultFileRegion(
            raf.getChannel(), 0, raf.length());
    ctx.writeAndFlush(region); // 底层使用 sendfile 零拷贝传输
}
```

### 3. wrap() 方法

`Unpooled.wrappedBuffer()` 将已有的 byte 数组或 ByteBuffer 包装为 `ByteBuf`，**不拷贝数据**，包装后的 `ByteBuf` 与原数组共享内存。

```java
byte[] data = "Hello".getBytes();
ByteBuf buf = Unpooled.wrappedBuffer(data); // 零拷贝包装，共享内存
// 修改 data 会影响 buf 的内容
```

---

## 六、应用场景

### 1. Kafka —— sendfile 高速日志传输

Kafka 的 Producer 写入日志文件，Consumer 读取日志文件。Kafka 使用 `FileChannel.transferTo()`（底层 sendfile）将日志文件直接通过网络发送给 Consumer，数据不经过用户空间，极大提升了吞吐量。

### 2. RocketMQ —— mmap 消息存储

RocketMQ 使用 `MappedByteBuffer`（底层 mmap）映射消息存储文件（CommitLog），实现消息的高性能随机读写。对于小文件（如 ConsumeQueue），mmap 的随机访问优势尤为明显。

### 3. Netty —— 网络传输优化

Netty 通过 `FileRegion` 实现文件零拷贝传输，通过 `CompositeByteBuf` 避免消息组装时的内存拷贝，通过 `DirectByteBuffer` + 内存池减少堆与直接内存之间的拷贝。

### 4. 选择指南

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 大文件顺序传输（文件下载、日志传输） | `sendfile`（`transferTo`） | 数据不经过用户空间，吞吐最高 |
| 大文件随机读写（数据库、索引文件） | `mmap`（`MappedByteBuffer`） | 支持随机访问，无需 read/write 系统调用 |
| 小文件传输 | 传统 IO 或 NIO 普通 Buffer | 零拷贝建立映射的开销可能超过收益 |
| 用户空间内数据合并/组装 | Netty `CompositeByteBuf` | 避免中间缓冲区的内存拷贝 |
| 网络文件传输 | Netty `FileRegion` | 封装 sendfile，与 Netty Pipeline 无缝集成 |

---

## 七、总结

零拷贝的核心目标是**减少数据在内核空间与用户空间之间的 CPU 拷贝**，本质上是让数据尽可能直接到达目的地。

| 层级 | 零拷贝方式 | 代表技术 |
|------|-----------|----------|
| 操作系统层 | mmap、sendfile、splice | Linux 内核系统调用 |
| Java NIO 层 | `MappedByteBuffer`、`FileChannel.transferTo` | 封装 OS 零拷贝 API |
| 框架层 | `CompositeByteBuf`、`FileRegion`、内存池 | Netty 用户空间零拷贝 |

理解零拷贝机制对于分析高性能中间件（Kafka、RocketMQ、Netty）的底层原理至关重要，也是系统设计和性能调优中的高频考点。
