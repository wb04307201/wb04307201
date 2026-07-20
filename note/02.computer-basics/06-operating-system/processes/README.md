<!--
module:
  parent: computer-basics/06-operating-system
  slug: computer-basics/06-operating-system/processes
  type: article
  category: 主模块子文章
  summary: 进程、线程、协程的本质区别，进程状态机、进程间通信（IPC）与线程同步机制。
-->

# 进程与线程

> 进程是资源分配的最小单位，线程是 CPU 调度的最小单位。理解它们的区别与协作方式，是掌握并发编程的基础。

---

## 一、进程 vs 线程 vs 协程

| 维度 | 进程 (Process) | 线程 (Thread) | 协程 (Coroutine) |
|------|---------------|--------------|-----------------|
| **定义** | 运行中的程序实例 | 进程内的执行单元 | 用户态的轻量级线程 |
| **地址空间** | 独立虚拟地址空间 | 共享所属进程的地址空间 | 共享所属线程的地址空间 |
| **调度方** | 操作系统内核 | 操作系统内核 | 用户态运行时（语言/框架） |
| **切换开销** | 高（需切换页表 + TLB 刷新） | 中（共享页表，但需切换栈） | 低（仅切换寄存器 + 栈指针） |
| **通信方式** | IPC（管道/共享内存/Socket） | 共享内存（需同步） | 直接共享变量（单线程内） |
| **典型大小** | 数十 MB ~ 数 GB | 栈默认 1~8 MB | 栈可动态增长（KB 级） |
| **崩溃隔离** | 进程间互不影响 | 一个线程崩溃可能导致整个进程退出 | 一个协程崩溃不影响其他协程 |

```text
进程 A (PID=1234)
┌──────────────────────────────────────────────┐
│  虚拟地址空间（独立）                          │
│  ┌────────────┬────────────┬────────────┐    │
│  │  代码段     │  数据段     │  堆 (↑)    │    │
│  ├────────────┴────────────┼────────────┤    │
│  │     共享区域             │            │    │
│  │  ┌──────────┐ ┌────────┐│            │    │
│  │  │ 线程1 栈 │ │线程2 栈││            │    │
│  │  └──────────┘ └────────┘│            │    │
│  │       栈 (↓)            │            │    │
│  └─────────────────────────┴────────────┘    │
│  文件描述符表 / 信号处理器 / 环境变量          │
└──────────────────────────────────────────────┘
```

---

## 二、进程状态机

进程在其生命周期中经历以下状态转换：

```text
                  fork()
    [新建] ──────────────► [就绪]
     (New)                 (Ready)
                            │  ▲
                   调度器    │  │ 时间片用完 /
                   分配 CPU │  │ 更高优先级抢占
                            ▼  │
                          [运行]
                         (Running)
                            │  ▲
              I/O 请求 /    │  │ I/O 完成 /
              等待锁        │  │ 事件通知
                            ▼  │
                          [阻塞]          [终止]
                        (Blocked) ◄──── (Terminated)
                                          exit()
```

| 状态 | 含义 | 在 Linux 中的对应 |
|------|------|------------------|
| **新建 (New)** | 进程正在创建（`fork()` 执行中） | — |
| **就绪 (Ready)** | 已分配到除 CPU 外的所有资源，等待调度 | `TASK_RUNNING`（在 runqueue 中） |
| **运行 (Running)** | 正在 CPU 上执行 | `TASK_RUNNING`（在 CPU 上） |
| **阻塞 (Blocked)** | 等待某个事件（I/O、锁、信号） | `TASK_INTERRUPTIBLE` / `TASK_UNINTERRUPTIBLE` |
| **终止 (Terminated)** | 进程执行完毕，等待父进程 `wait()` 回收 | `TASK_ZOMBIE`（僵尸进程） |

> **僵尸进程**：子进程已 `exit()`，但父进程未调用 `wait()` 回收，仍占用 PID 和进程表项。
> **孤儿进程**：父进程先于子进程退出，子进程被 `init`（PID=1）收养。

---

## 三、进程间通信 (IPC)

### 3.1 五种经典 IPC 机制

| 机制 | 原理 | 优点 | 缺点 | 典型场景 |
|------|------|------|------|---------|
| **管道 (Pipe)** | 内核缓冲区，半双工 | 简单、无需命名 | 仅限亲缘进程 | `ls \| grep "log"` |
| **命名管道 (FIFO)** | 文件系统节点，半双工 | 无亲缘关系进程可用 | 仍为半双工 | 无亲缘进程间通信 |
| **消息队列** | 内核中的消息链表 | 消息有类型、可随机读取 | 消息大小受限 | 系统服务间通信 |
| **共享内存** | 多个进程映射同一物理内存 | 最快的 IPC（无拷贝） | 需自行同步 | 高频数据交换 |
| **信号量 (Semaphore)** | 内核计数器，用于同步 | 可跨进程同步 | 仅用于同步，不传数据 | 生产者-消费者 |
| **Socket** | 网络通信端点 | 可跨主机 | 开销较大 | 分布式系统通信 |

### 3.2 管道示例（C 语言）

```c
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main() {
    int pipefd[2];
    pipe(pipefd);  // 创建管道: pipefd[0]=读端, pipefd[1]=写端

    pid_t pid = fork();
    if (pid == 0) {
        // 子进程：写入管道
        close(pipefd[0]);  // 关闭读端
        write(pipefd[1], "hello from child", 16);
        close(pipefd[1]);
    } else {
        // 父进程：读取管道
        close(pipefd[1]);  // 关闭写端
        char buf[64];
        read(pipefd[0], buf, sizeof(buf));
        printf("Parent received: %s\n", buf);
        close(pipefd[0]);
    }
    return 0;
}
```

### 3.3 共享内存示意

```text
进程 A                    进程 B
┌──────────┐            ┌──────────┐
│ 虚拟地址  │            │ 虚拟地址  │
│ 0x7f0000 │            │ 0x8f0000 │
└────┬─────┘            └────┬─────┘
     │                       │
     │   shmget() + shmat()  │
     ▼                       ▼
┌─────────────────────────────────┐
│        共享内存段 (物理内存)       │
│   [  data buffer: 1024 bytes ]  │
└─────────────────────────────────┘

注意：两个进程的虚拟地址不同，但映射到同一物理内存
```

---

## 四、线程同步机制

### 4.1 四种同步原语对比

| 原语 | 作用 | 粒度 | 适用场景 |
|------|------|------|---------|
| **互斥锁 (Mutex)** | 保证同一时刻只有一个线程访问共享资源 | 临界区 | 简单互斥 |
| **读写锁 (RWLock)** | 允许多个读线程同时访问，写时独占 | 读多写少 | 缓存、配置读取 |
| **条件变量 (CondVar)** | 线程等待某个条件成立时被唤醒 | 条件等待 | 生产者-消费者 |
| **信号量 (Semaphore)** | 控制同时访问某资源的线程数量 | 计数 | 连接池、限流 |

### 4.2 互斥锁 vs 读写锁

```text
互斥锁 (Mutex):
  线程 A ──lock──► [临界区] ──unlock──►
  线程 B ──等待 ──────────────────► lock ──► [临界区] ──► unlock
  （即使 A 在读，B 也要等）

读写锁 (RWLock):
  读者 A ──rdlock──► [读数据] ──rdunlock──►
  读者 B ──rdlock──► [读数据] ──rdunlock──►   ← 可同时读
  写者 C ──等待 ──────────────────────────► wrlock ──► [写数据] ──► wrunlock
  （写时独占，读时共享）
```

### 4.3 生产者-消费者模型（条件变量）

```c
#include <pthread.h>

#define BUFFER_SIZE 10
int buffer[BUFFER_SIZE];
int count = 0;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t not_full = PTHREAD_COND_INITIALIZER;
pthread_cond_t not_empty = PTHREAD_COND_INITIALIZER;

void* producer(void* arg) {
    for (int i = 0; i < 100; i++) {
        pthread_mutex_lock(&mutex);
        while (count == BUFFER_SIZE)           // 缓冲区满，等待
            pthread_cond_wait(&not_full, &mutex);
        buffer[count++] = i;                   // 放入数据
        pthread_cond_signal(&not_empty);       // 通知消费者
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

void* consumer(void* arg) {
    for (int i = 0; i < 100; i++) {
        pthread_mutex_lock(&mutex);
        while (count == 0)                     // 缓冲区空，等待
            pthread_cond_wait(&not_empty, &mutex);
        int val = buffer[--count];             // 取出数据
        pthread_cond_signal(&not_full);        // 通知生产者
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}
```

> **关键细节**：`pthread_cond_wait()` 必须配合 `while` 循环（而非 `if`），防止**虚假唤醒 (spurious wakeup)**。

---

## 五、用户态线程 vs 内核态线程

| 维度 | 用户态线程 (M:1 / M:N) | 内核态线程 (1:1) |
|------|----------------------|-----------------|
| **创建/销毁** | 极快（用户态操作） | 较慢（需系统调用） |
| **调度** | 用户态运行时调度 | 内核调度器 |
| **阻塞 I/O** | 一个线程阻塞 → 整个进程阻塞（M:1） | 仅该线程阻塞 |
| **多核利用** | M:1 模型无法利用多核 | 天然支持多核 |
| **栈大小** | 可动态增长（KB 级） | 固定（通常 1~8 MB） |
| **典型实现** | Go goroutine、Kotlin coroutine | Linux pthread、Java Thread（传统） |

```text
M:1 模型 (多用户线程 → 1 内核线程)
  用户线程A ──┐
  用户线程B ──┼──► 内核线程 ──► CPU
  用户线程C ──┘
  缺点：无法多核并行，一个阻塞全部阻塞

M:N 模型 (多用户线程 → 多内核线程)
  用户线程A ──┐         ┌──► 内核线程1 ──► CPU Core 0
  用户线程B ──┼──调度──►├──► 内核线程2 ──► CPU Core 1
  用户线程C ──┘         └──► 内核线程3 ──► CPU Core 2
  Go goroutine 的 GMP 模型即为此类

1:1 模型 (1 用户线程 → 1 内核线程)
  Java Thread ──► 内核线程 ──► CPU
  简单直接，但线程创建/切换开销大
```

---

## 六、Java 中的线程映射

### 6.1 传统 Thread（1:1 模型）

```java
// 每个 Java Thread 对应一个操作系统内核线程
Thread t = new Thread(() -> {
    System.out.println("Running on: " + Thread.currentThread().getName());
});
t.start();  // JVM 调用 pthread_create() 创建内核线程
```

**问题**：每个线程占用 ~1MB 栈内存，大量线程时内存和上下文切换开销巨大。

### 6.2 Virtual Thread / Project Loom（M:N 模型，JDK 21+）

```java
// Virtual Thread：用户态轻量级线程，由 JVM 调度
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 100_000; i++) {
        executor.submit(() -> {
            // 阻塞 I/O 时自动让出载体线程（carrier thread）
            Thread.sleep(Duration.ofSeconds(1));
            return "done";
        });
    }
}
// 10 万个虚拟线程，底层仅需少量载体线程
```

### 6.3 Thread vs Virtual Thread 对比

| 维度 | Thread（平台线程） | Virtual Thread（虚拟线程） |
|------|-------------------|--------------------------|
| **底层模型** | 1:1（对应内核线程） | M:N（JVM 调度到载体线程） |
| **栈内存** | ~1 MB（固定） | KB 级（堆上分配，动态增长） |
| **创建数量** | 数百~数千 | 数十万~百万 |
| **阻塞行为** | 阻塞内核线程 | 自动 unmount，不阻塞载体线程 |
| **适用场景** | CPU 密集型计算 | I/O 密集型（网络/数据库调用） |
| **synchronized** | 正常 pin 到载体线程 | 会 pin 载体线程（推荐用 ReentrantLock） |

> **实践建议**：I/O 密集型应用（Web 服务、微服务）优先使用 Virtual Thread；CPU 密集型计算保持传统 Thread + 线程池。

---

## 七、常见面试题

| 问题 | 核心要点 |
|------|---------|
| 进程和线程的区别？ | 资源分配 vs CPU 调度单位；地址空间独立 vs 共享 |
| 为什么线程切换比进程切换快？ | 线程共享页表，无需切换地址空间 / 刷新 TLB |
| 什么是僵尸进程？如何避免？ | 子进程退出但父进程未 `wait()`；用 `signal(SIGCHLD, SIG_IGN)` 或显式 `wait()` |
| 互斥锁和信号量的区别？ | 互斥锁是二值信号量的特例；信号量可计数（控制并发数） |
| 协程比线程好在哪？ | 用户态调度（无内核开销）、栈更小（KB 级）、可创建更多实例 |

---

## 八、相关章节

- 返回：[`06-operating-system`](../README.md) — 操作系统概述
- 深度阅读：[`01.java/concurrency`](../../../01.java/concurrency/) — Java 并发编程（线程池/锁/Fork-Join）
- 深度阅读：[`01.java/jvm`](../../../01.java/jvm/) — JVM 内存模型（栈/堆与 OS 内存的关系）

---

## 📊 本节统计

| 统计维度 | 数值 | 口径 |
|----------|------|------|
| 核心主题数 | 6 | 进程/线程/协程对比 · 进程状态机 · IPC · 线程同步 · 用户态/内核态线程 · Java 映射 |
| 代码示例数 | 4 | C 管道示例 · 生产者消费者 · Java Thread · Virtual Thread |

> **统计时间戳**：2026-07-16

---

← [返回: 操作系统概述](../README.md)
