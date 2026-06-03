# 重写 `note/01.java/io` 笔记计划

## Context

当前 `note/01.java/io/` 下有两个笔记文件：`README.md`（I/O 主文件）和 `zero-copy/README.md`（零拷贝）。
现有内容存在大量遗漏（缺少 File 类、NIO 核心组件、装饰器模式、字符编码、数据流、管道流、try-with-resources 等），且过度依赖图片（用户要求全部移除）。需要按照项目已有风格（中文序号 H2、阿拉伯数字 H3、表格+代码示例+最佳实践）重写两个文件。

---

## 修改文件

| 文件 | 操作 |
|------|------|
| `note/01.java/io/README.md` | 完全重写 |
| `note/01.java/io/zero-copy/README.md` | 完全重写 |
| `note/01.java/io/img*.png`（7 个） | 删除 |
| `note/01.java/io/zero-copy/img*.png`（5 个） | 删除 |

> 注：`note/README.md` 主索引中 IO 的条目（3. I/O、3.1 零拷贝）无需变更，结构不变。

---

## 一、`note/01.java/io/README.md` 重写结构

### 现有问题
- 字节流/字符流部分只有 API 罗列，缺少代码示例和实际用法
- 缺少：File 类、字符编码、转换流详解、数据流、管道流、ByteArray 流、SequenceInputStream、装饰器模式、try-with-resources、NIO 核心组件（Buffer/Channel/Selector）、NIO.2 Files/Path API
- BIO/NIO/AIO 部分全靠图片撑，图片删除后几乎为空
- 缓冲流、打印流、随机访问流内容过于简略

### 重写后大纲

```
# I/O

引言段落（定义 + I/O 流本质）

---

## 一、I/O 流概述
- 流的分类体系（方向 + 数据单位 + 功能 → 分类表格）
- 四大抽象基类（InputStream/OutputStream/Reader/Writer）
- 装饰器模式（IO 体系的核心设计模式，说明为什么要层层包装）

## 二、字节流
### 1. InputStream（字节输入流）
- 常用方法表格（保留现有 + Java 9+ 新方法）
- 常用实现类：FileInputStream、ByteArrayInputStream、PipedInputStream
### 2. OutputStream（字节输出流）
- 常用方法表格
- 常用实现类：FileOutputStream、ByteArrayOutputStream、PipedOutputStream
### 3. 代码示例
- try-with-resources 文件复制示例

## 三、字符流
### 1. Reader（字符输入流）
- 常用方法表格
- FileReader 的使用
### 2. Writer（字符输出流）
- 常用方法表格
- FileWriter 的使用
### 3. 转换流
- InputStreamReader / OutputStreamWriter
- 字符编码问题（Charset、常见编码、乱码原因）
### 4. 代码示例

## 四、缓冲流
### 1. 字节缓冲流（BufferedInputStream / BufferedOutputStream）
- 原理（内部缓冲区减少 IO 次数）
- 默认缓冲区大小 8192
### 2. 字符缓冲流（BufferedReader / BufferedWriter）
- readLine() 方法
- newLine() 方法
### 3. 代码示例 + 性能说明

## 五、其他常用流
### 1. 数据流（DataInputStream / DataOutputStream）
- 读写基本数据类型
### 2. 打印流（PrintStream / PrintWriter）
- System.out 的本质
- printf / format
### 3. 管道流（PipedInputStream / PipedOutputStream）
- 线程间通信
### 4. 序列流（SequenceInputStream）
- 合并多个输入流
### 5. 随机访问流（RandomAccessFile）
- 读写模式表格
- seek() 方法

## 六、序列化与反序列化（简要说明 + 链接引用）
- 简述 ObjectInputStream / ObjectOutputStream 用途
- 提及 serialVersionUID 和 transient 关键字
- 详细内容由 concepts/serialization-and-deserialization/README.md 承载，此处仅做链接引用，不展开

## 七、File 类与 NIO.2 文件操作
### 1. File 类
- 常用方法表格
### 2. NIO.2：Path 与 Files
- Path 接口
- Files 工具类常用方法
- 代码示例（遍历目录、读写文件、复制文件）

## 八、NIO（New I/O）
### 1. NIO 概述（面向块、非阻塞）
### 2. 三大核心组件
- Buffer（缓冲区）：position / limit / capacity / flip / clear
- Channel（通道）：FileChannel / SocketChannel / ServerSocketChannel
- Selector（多路复用器）：一个线程管理多个 Channel
### 3. NIO vs BIO 对比表

## 九、IO 模型
### 1. 前置概念（用户态/内核态、系统调用、DMA、阻塞的含义）
### 2. BIO（同步阻塞 I/O）
- 文字描述 + 流程说明
### 3. NIO（同步非阻塞 I/O + IO 多路复用）
- 同步非阻塞的轮询问题
- IO 多路复用：select / poll / epoll 对比
- Java Selector 的角色
### 4. AIO（异步非阻塞 I/O）
- 回调机制
- Netty 弃用 AIO 的原因
### 5. 三种模型对比表

## 十、最佳实践
1. 始终使用 try-with-resources
2. 用缓冲流包装原始流
3. 大文件用 NIO FileChannel + MappedByteBuffer
4. 文本操作优先用字符流
5. 注意字符编码一致性
6. 高并发场景使用 NIO + Selector
```

---

## 二、`note/01.java/io/zero-copy/README.md` 重写结构

### 现有问题
- 内容质量不错但缺少：Netty 零拷贝、DirectByteBuffer、应用场景对比、mmap 的限制与内存泄漏、性能数据
- 代码示例中 `instance code` 重复出现
- 内核空间/用户空间解释段落放在 sendfile+DMA 后面，位置不合理

### 重写后大纲

```
# 零拷贝

概念定义 + 为什么需要零拷贝

---

## 一、前置知识
### 1. 内核空间与用户空间
### 2. DMA（直接内存访问）
### 3. 上下文切换（用户态/内核态）

## 二、IO 拷贝机制
### 1. 传统 read/write 拷贝
- 4 次拷贝、4 次切换、流程说明
### 2. mmap 内存映射
- 3 次拷贝、4 次切换
### 3. sendfile 系统调用
- 3 次拷贝、2 次切换
### 4. sendfile + DMA scatter/gather
- 2 次 DMA、0 次 CPU 拷贝、2 次切换（真正的零拷贝）
### 5. splice
- 2 次 DMA、0 次 CPU 拷贝、2 次切换（无需硬件支持）

## 三、IO 拷贝机制对比（表格，保留并优化现有表格）

## 四、Java 零拷贝实现
### 1. NIO MappedByteBuffer（mmap）
- 代码示例
- 适用场景（大文件随机读写）
- 限制与注意事项（内存泄漏、 unmapping 问题、地址空间限制）
### 2. FileChannel.transferTo（sendfile）
- 代码示例
- 适用场景（文件传输，如 Kafka）
### 3. DirectByteBuffer
- 直接内存 vs 堆内存
- GC 影响

## 五、Netty 中的零拷贝（概念 + 核心类介绍）
- CompositeByteBuf：合并多个 ByteBuf 而不复制内存
- FileRegion：封装 FileChannel.transferTo，实现文件传输零拷贝
- wrap() 方法：零拷贝包装，避免数据复制
- 不深入源码，侧重概念理解和用途说明

## 六、应用场景
- Kafka：sendfile 实现高速日志传输
- RocketMQ：mmap 实现消息存储
- Netty：网络传输优化
- 选择指南：什么时候用 mmap，什么时候用 sendfile

## 七、总结
```

---

## 执行步骤

1. 重写 `note/01.java/io/README.md`（完全替换内容）
2. 重写 `note/01.java/io/zero-copy/README.md`（完全替换内容）
3. 删除所有图片文件（12 个 .png）

## 验证方式

- 检查两个 README.md 无图片引用
- 检查 H2 使用中文序号、H3 使用阿拉伯数字
- 检查代码示例语法正确
- 检查 `note/README.md` 主索引链接仍然有效
