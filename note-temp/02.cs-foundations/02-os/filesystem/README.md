<!--
module:
  parent: computer-basics/06-operating-system
  slug: computer-basics/06-operating-system/filesystem
  type: article
  category: 主模块子文章
  summary: 文件系统层次（VFS/ext4/XFS）、inode 与 dentry、文件描述符、I/O 模型与 Linux page cache。
-->

# 文件系统与 I/O

> Linux 的"一切皆文件"哲学将设备、进程、网络等抽象为统一的文件描述符接口。理解文件系统层次和 I/O 模型是高性能服务开发的基础。

---

## 一、文件系统层次结构

```text
┌───────────────────────────────────────────┐
│            用户空间应用                      │
│      (Java / Nginx / MySQL / ...)        │
├───────────────────────────────────────────┤
│            系统调用接口                      │
│    open() / read() / write() / close()    │
├───────────────────────────────────────────┤
│         VFS (虚拟文件系统层)                │ ← 统一接口
│    inode / dentry / file / superblock     │
├──────────┬──────────┬─────────────────────┤
│  ext4    │   XFS    │  NTFS / FAT32 / ... │ ← 具体文件系统
├──────────┴──────────┴─────────────────────┤
│         块设备层 (Block Layer)             │ ← I/O 调度
├───────────────────────────────────────────┤
│         设备驱动 (SATA/NVMe/USB)           │
├───────────────────────────────────────────┤
│            物理磁盘 / SSD                  │
└───────────────────────────────────────────┘
```

### 1.1 主流文件系统对比

| 文件系统 | 最大文件大小 | 最大卷大小 | 特点 | 典型场景 |
|---------|------------|-----------|------|---------|
| **ext4** | 16 TB | 1 EB | Linux 默认、日志、延迟分配 | 通用 Linux |
| **XFS** | 8 EB | 8 EB | 高性能大文件、并行 I/O | 数据库/大文件存储 |
| **Btrfs** | 16 EB | 16 EB | 快照、压缩、校验 | NAS / 开发环境 |
| **NTFS** | 16 TB | 256 TB | Windows 默认、ACL | Windows 系统 |
| **ZFS** | 16 EB | 256 PB | 企业级、快照、RAID-Z | 企业存储 |

---

## 二、inode 与 dentry

### 2.1 inode (索引节点)

inode 存储文件的**元数据**（不含文件名）：

| inode 字段 | 说明 |
|-----------|------|
| `st_mode` | 文件类型 + 权限（rwxrwxrwx） |
| `st_uid` / `st_gid` | 所有者 / 所属组 |
| `st_size` | 文件大小（字节） |
| `st_atime` / `st_mtime` / `st_ctime` | 访问 / 修改 / 状态变更时间 |
| `st_nlink` | 硬链接数 |
| `i_blocks` | 占用的磁盘块列表（直接块 + 间接块） |
| `i_ino` | inode 编号（文件系统内唯一） |

```bash
# 查看文件 inode 信息
stat filename
# 输出:
#   File: filename
#   Size: 4096       Blocks: 8     IO Block: 4096   regular file
#   Inode: 1234567    Links: 1
#   Access: (0644/-rw-r--r--)  Uid: (1000/user)  Gid: (1000/user)

# 查看文件系统 inode 使用情况
df -i
# /dev/sda1   Inodes: 6553600  IUsed: 523456  IFree: 6030144  IUse%: 8%
```

### 2.2 dentry (目录项)

dentry 将**路径名**映射到 **inode**：

```text
路径解析: /home/user/document.txt

/ ──dentry──► inode(dir)
  │
  home ──dentry──► inode(dir)
    │
    user ──dentry──► inode(dir)
      │
      document.txt ──dentry──► inode(file)

dentry cache (dcache):
  内核缓存最近使用的 dentry → 加速路径解析
  /home/user/document.txt → inode 1234567 (缓存命中)
```

### 2.3 硬链接 vs 软链接

| 维度 | 硬链接 (Hard Link) | 软链接 (Symbolic Link) |
|------|-------------------|----------------------|
| **本质** | 同一 inode 的多个目录项 | 独立文件，内容是目标路径 |
| **inode** | 相同 | 不同 |
| **跨文件系统** | 不可以 | 可以 |
| **删除原文件** | 仍可通过硬链接访问 | 悬空链接（dangling） |
| **目录** | 不能硬链接目录 | 可以链接目录 |

```text
硬链接:
  file_a.txt (dentry) ──► inode 1234 ──► 数据块
  file_b.txt (dentry) ──► inode 1234 ──► 同上（st_nlink = 2）

软链接:
  file_a.txt (dentry) ──► inode 1234 ──► 数据块
  link_b.txt (dentry) ──► inode 5678 ──► 内容: "file_a.txt"
```

---

## 三、文件描述符与"一切皆文件"

### 3.1 文件描述符 (File Descriptor)

```text
进程的文件描述符表:
┌─────┬──────────────────────────┐
│ FD  │ 指向                      │
├─────┼──────────────────────────┤
│  0  │ stdin  (标准输入)         │ ← 预打开
│  1  │ stdout (标准输出)         │ ← 预打开
│  2  │ stderr (标准错误)         │ ← 预打开
│  3  │ /var/log/app.log         │
│  4  │ TCP socket (port 8080)   │ ← 网络也是 FD
│  5  │ pipe (read end)          │ ← 管道也是 FD
│  6  │ /dev/epoll               │ ← epoll 实例也是 FD
│ ... │                          │
└─────┴──────────────────────────┘

限制:
  ulimit -n      # 查看当前限制（默认 1024）
  ulimit -n 65535  # 临时调高
```

### 3.2 "一切皆文件"的体现

| 类型 | 路径 / 接口 | 操作 |
|------|-----------|------|
| 普通文件 | `/path/to/file` | `read()` / `write()` |
| 目录 | `/path/to/dir` | `opendir()` / `readdir()` |
| 管道 | `pipe()` | `read()` / `write()` |
| Socket | `socket()` | `read()` / `write()` / `send()` / `recv()` |
| 设备文件 | `/dev/sda`, `/dev/null` | `read()` / `write()` / `ioctl()` |
| epoll 实例 | `epoll_create()` | `epoll_ctl()` / `epoll_wait()` |
| 定时器 | `timerfd_create()` | `read()` |
| 信号 | `signalfd()` | `read()` |
| inotify | `inotify_init()` | `read()` |

### 3.3 FD 泄漏问题

```bash
# 查看进程的 FD 使用情况
ls -la /proc/<PID>/fd/ | wc -l

# 常见泄漏原因：
# 1. 打开文件/Socket 后未 close()
# 2. 异常路径跳过 close()（Java 中用 try-with-resources）
# 3. 连接池未正确归还
```

```java
// 错误：异常时 FD 泄漏
InputStream in = new FileInputStream("data.bin");
byte[] buf = new byte[1024];
in.read(buf);  // 如果这里抛异常，in 不会被关闭
in.close();

// 正确：try-with-resources 自动关闭
try (InputStream in = new FileInputStream("data.bin")) {
    byte[] buf = new byte[1024];
    in.read(buf);
}  // 无论是否异常，都会自动 close()
```

---

## 四、I/O 模型

### 4.1 五种 I/O 模型对比

| 模型 | 阻塞 | 同步 | 原理 | 适用场景 |
|------|------|------|------|---------|
| **阻塞 I/O (BIO)** | 是 | 是 | `read()` 阻塞直到数据就绪 | 简单场景、低并发 |
| **非阻塞 I/O (NIO)** | 否 | 是 | `read()` 立即返回，需轮询 | 少量 FD |
| **I/O 多路复用** | 否 | 是 | `select/poll/epoll` 监控多个 FD | 高并发网络服务 |
| **信号驱动 I/O** | 否 | 是 | 内核发信号通知数据就绪 | 较少使用 |
| **异步 I/O (AIO)** | 否 | 否 | `io_uring` / `aio_read`，完成后回调 | 极致性能 |

### 4.2 阻塞 vs 非阻塞 vs 多路复用 示意

```text
阻塞 I/O (每个连接一个线程):
  Thread-1: read(fd1) ──阻塞──► 数据就绪 ──► 处理
  Thread-2: read(fd2) ──阻塞──► 数据就绪 ──► 处理
  Thread-3: read(fd3) ──阻塞──► 数据就绪 ──► 处理
  问题：1 万连接 = 1 万线程

非阻塞 I/O (轮询):
  Thread: read(fd1)→EAGAIN → read(fd2)→EAGAIN → read(fd3)→数据→处理
  问题：忙轮询浪费 CPU

I/O 多路复用 (epoll):
  Thread: epoll_wait() ──阻塞──► fd2 就绪 ──► 处理 fd2
                              ► fd5 就绪 ──► 处理 fd5
  优势：1 个线程监控数万 FD
```

---

## 五、epoll vs select vs poll

### 5.1 三者对比

| 维度 | select | poll | epoll |
|------|--------|------|-------|
| **最大 FD 数** | 1024（FD_SETSIZE） | 无上限 | 无上限（受内存限制） |
| **数据结构** | 位图 (bitmap) | 链表 (pollfd[]) | 红黑树 + 就绪链表 |
| **触发方式** | 每次遍历所有 FD | 每次遍历所有 FD | 仅返回就绪 FD |
| **时间复杂度** | O(n) | O(n) | O(1) 添加/删除，O(k) 返回就绪 |
| **拷贝开销** | 每次用户→内核拷贝 fd_set | 每次拷贝 pollfd[] | `epoll_ctl` 增量更新 |
| **边缘/水平触发** | 仅水平触发 (LT) | 仅水平触发 (LT) | 支持 ET + LT |
| **适用场景** | 跨平台兼容 | 跨平台兼容 | Linux 高性能首选 |

### 5.2 epoll 工作流程

```text
1. 创建 epoll 实例
   int epfd = epoll_create(1024);  // 返回 epoll FD

2. 注册监听的 FD
   struct epoll_event ev;
   ev.events = EPOLLIN;           // 监听可读事件
   ev.data.fd = client_fd;
   epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &ev);

3. 等待事件
   struct epoll_event events[MAX_EVENTS];
   int n = epoll_wait(epfd, events, MAX_EVENTS, timeout);
   for (int i = 0; i < n; i++) {
       // 仅处理就绪的 FD（无需遍历所有 FD）
       handle(events[i].data.fd);
   }

内核实现:
   ┌─────────────────────────────┐
   │  红黑树 (监听集合)           │
   │  ┌──┬──┬──┬──┬──┐          │
   │  │fd3│fd7│fd12│fd20│fd35│  │  ← O(log n) 增删
   │  └──┴──┴──┴──┴──┘          │
   ├─────────────────────────────┤
   │  就绪链表 (双向链表)         │
   │  fd7 ──► fd20 ──► NULL     │  ← epoll_wait 仅返回这些
   └─────────────────────────────┘
```

### 5.3 ET (Edge Triggered) vs LT (Level Triggered)

| 维度 | 水平触发 (LT) | 边缘触发 (ET) |
|------|-------------|-------------|
| **通知条件** | FD 缓冲区中有数据就通知 | 状态变化时才通知（新数据到达） |
| **处理要求** | 可分多次读取 | 必须一次读完（或用循环读到 EAGAIN） |
| **效率** | 可能多次通知同一 FD | 每个事件仅通知一次 |
| **默认** | select/poll/epoll 默认 | epoll 需显式设置 `EPOLLET` |

> **Nginx / Redis / Netty** 在 Linux 上使用 epoll + ET 模式实现高性能事件循环。

---

## 六、Linux Page Cache

### 6.1 原理

```text
写操作:
  应用 ──write()──► Page Cache ──(异步刷盘)──► 磁盘
                   (脏页 dirty page)

读操作:
  应用 ──read()──► Page Cache ──(命中)──► 返回数据
                   (若未命中)──► 从磁盘加载到 Page Cache

┌────────────┐     ┌─────────────┐     ┌────────┐
│  应用程序   │────►│ Page Cache  │────►│  磁盘   │
│  (用户态)   │◄────│ (内核态)    │◄────│        │
└────────────┘     └─────────────┘     └────────┘

Page Cache 特点:
  - 利用空闲内存缓存文件数据
  - 写操作先写 cache（脏页），异步刷盘
  - 读操作优先从 cache 读取
  - 内存不足时回收 clean page（脏页需先刷盘）
```

### 6.2 查看 Page Cache 使用

```bash
# 查看内存分布
free -h
#              total   used   free   shared  buff/cache  available
# Mem:          16Gi   4.2Gi  2.1Gi   512Mi    9.7Gi      11Gi
#                                   ↑
#                              Page Cache 占用

# 手动清理 Page Cache（不推荐在生产环境执行）
sync  # 先刷脏页
echo 3 > /proc/sys/vm/drop_caches

# 脏页刷盘参数
cat /proc/sys/vm/dirty_ratio         # 脏页占总内存比例触发同步写（默认 20%）
cat /proc/sys/vm/dirty_background_ratio  # 触发后台刷盘（默认 10%）
```

---

## 七、与 Java NIO 的关系

### 7.1 Java NIO 核心组件与 OS 映射

| Java NIO 组件 | OS 底层对应 | 说明 |
|--------------|-----------|------|
| `Channel` | 文件描述符 (FD) | `SocketChannel` / `FileChannel` |
| `Buffer` | 用户态内存缓冲区 | `ByteBuffer`（堆内/堆外） |
| `Selector` | `epoll` (Linux) / `kqueue` (macOS) | I/O 多路复用 |
| `SelectionKey` | epoll 中的 `epoll_event` | 就绪事件 |

### 7.2 Selector 工作流程

```java
// 1. 创建 Selector（底层调用 epoll_create）
Selector selector = Selector.open();

// 2. 注册 Channel（底层调用 epoll_ctl ADD）
ServerSocketChannel server = ServerSocketChannel.open();
server.configureBlocking(false);
server.bind(new InetSocketAddress(8080));
server.register(selector, SelectionKey.OP_ACCEPT);

// 3. 事件循环（底层调用 epoll_wait）
while (true) {
    int readyCount = selector.select();  // 阻塞直到有事件就绪
    if (readyCount > 0) {
        Set<SelectionKey> keys = selector.selectedKeys();
        Iterator<SelectionKey> iter = keys.iterator();
        while (iter.hasNext()) {
            SelectionKey key = iter.next();
            if (key.isAcceptable()) {
                // 处理新连接
                SocketChannel client = server.accept();
                client.configureBlocking(false);
                client.register(selector, SelectionKey.OP_READ);
            } else if (key.isReadable()) {
                // 处理读事件
                SocketChannel ch = (SocketChannel) key.channel();
                ByteBuffer buf = ByteBuffer.allocate(1024);
                ch.read(buf);
            }
            iter.remove();
        }
    }
}
```

### 7.3 Netty 的 EventLoop 模型

```text
Netty EventLoop (1 个线程):
┌─────────────────────────────────────┐
│  EventLoop                          │
│  ┌─────────────────────────────┐   │
│  │  Selector (epoll)           │   │
│  │  ┌───┬───┬───┬───┬───┐     │   │
│  │  │ch1│ch2│ch3│ch4│ch5│     │   │  ← 1 个线程管理多个 Channel
│  │  └───┴───┴───┴───┴───┘     │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  任务队列                     │   │
│  │  [task1] [task2] [task3]    │   │  ← 非 I/O 任务也在此线程执行
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘

默认配置: EventLoopGroup 线程数 = CPU 核心数 × 2
每个 EventLoop 管理 ~数千 Channel
```

---

## 八、常见面试题

| 问题 | 核心要点 |
|------|---------|
| inode 和文件名的关系？ | inode 存元数据不含文件名；文件名存在目录的 dentry 中 |
| 硬链接和软链接的区别？ | 硬链接共享 inode，软链接是独立文件（内容为路径） |
| 文件描述符是什么？ | 进程级整数索引，指向内核的文件对象（open file description） |
| epoll 比 select 好在哪？ | O(1) 事件通知（只返回就绪 FD）、无 1024 限制、支持 ET |
| Page Cache 的作用？ | 缓存文件数据到内存，减少磁盘 I/O（读缓存 + 写缓冲） |
| BIO/NIO/AIO 区别？ | 阻塞同步 / 非阻塞同步（多路复用）/ 非阻塞异步 |

---

## 九、相关章节

- 返回：[`06-operating-system`](../README.md) — 操作系统概述
- 深度阅读：[`01.java/io`](../../../01.java/io/) — Java I/O 体系（BIO/NIO 详解）
- 深度阅读：[`01.java/concurrency`](../../../01.java/concurrency/) — 并发编程（Netty 事件循环模型）
- 关联：[`04.system-design/04-high-performance`](../../../04.system-design/04-high-performance/) — 高性能设计（I/O 模型选型）
- 关联：[`03.database`](../../../03.database/) — 数据库（存储引擎与文件系统的关系）

---

## 📊 本节统计

| 统计维度 | 数值 | 口径 |
|----------|------|------|
| 核心主题数 | 7 | 文件系统层次 · inode/dentry · FD · I/O 模型 · epoll · Page Cache · Java NIO |
| 代码示例数 | 5 | stat 命令 · try-with-resources · epoll C 代码 · Java Selector · Netty 模型 |

> **统计时间戳**：2026-07-16

---

← [返回: 操作系统概述](../README.md)
