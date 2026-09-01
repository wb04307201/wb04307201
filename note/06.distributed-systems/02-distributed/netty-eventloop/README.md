<!--
module:
  parent: system-design
  slug: system-design/netty-eventloop
  type: article
  category: 主模块子文章
  summary: Netty 的线程模型核心是 EventLoop（单线程串行执行 ChannelHandler），业务长任务需切换至 UnorderedThreadPoolExecutor
  depth: ⭐⭐⭐
-->

# Netty EventLoop 与线程模型

> **一句话定位**：Netty 的 `EventLoop` 是**单线程串行执行 `ChannelHandler`** 的事件循环；业务长任务必须切到 `UnorderedThreadPoolExecutor`，否则会阻塞 IO。

> ⬅️ [返回 06 Distributed 总览](../../README.md)

---

## 一、Reactor 线程模型

Netty 基于 Reactor 模式，三种典型线程模型：

| 模型 | Boss | Worker | 适用 |
|------|------|--------|------|
| **单 Reactor 单线程** | 1 个 EventLoop 同时处理 accept + IO + 业务 | — | Demo |
| **单 Reactor 多线程** | 1 个 EventLoop 处理 accept | N 个 EventLoop 处理 IO；业务在独立线程池 | 中等并发 |
| **主从 Reactor 多线程**（**Netty 默认**） | Boss EventLoopGroup 处理 accept | Worker EventLoopGroup 处理 IO | 高并发 |

## 二、EventLoop 核心特性

```java
// Netty 服务端启动
EventLoopGroup bossGroup = new NioEventLoopGroup(1);
EventLoopGroup workerGroup = new NioEventLoopGroup();

ServerBootstrap b = new ServerBootstrap();
b.group(bossGroup, workerGroup)
 .channel(NioServerSocketChannel.class)
 .childHandler(new ChannelInitializer<SocketChannel>() {
     @Override
     protected void initChannel(SocketChannel ch) {
         ch.pipeline().addLast(new MyHandler());
     }
 });
```

**EventLoop 的关键约束**：

1. **一个 Channel 整个生命周期绑定同一个 EventLoop**（线程本地存储实现）
2. **一个 EventLoop 可绑定多个 Channel**（单线程多 Channel，IO 多路复用）
3. **ChannelHandler 在绑定 EventLoop 中按顺序串行执行**（无锁化设计）

## 三、EventLoop ≠ 业务线程池

```java
// ❌ 错误：在 EventLoop 中跑长任务
public class BadHandler extends ChannelInboundHandlerAdapter {
    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        // 这段代码在 EventLoop 线程执行！
        // 如果这里执行耗时 DB 查询，整个 EventLoop 就被阻塞
        // → 该 EventLoop 上所有 Channel 的 IO 都卡住
        Thread.sleep(5000);   // 灾难
    }
}

// ✅ 正确：使用 EventExecutorGroup 切换线程
public class GoodHandler extends ChannelInboundHandlerAdapter {
    private static final EventExecutorGroup businessPool =
        new DefaultEventExecutorGroup(16);   // 业务线程池

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        // 业务逻辑在 businessPool 中执行
        businessPool.submit(() -> {
            Object result = doBusiness(msg);
            // 写回时再切回 Channel 对应的 EventLoop
            ctx.channel().eventLoop().execute(() -> ctx.writeAndFlush(result));
        });
    }
}
```

## 四、UnorderedThreadPoolExecutor

Netty 提供的业务线程池 `UnorderedThreadPoolExecutor`：

```java
EventExecutorGroup businessGroup = new UnorderedThreadPoolExecutor(
    16, 32, 60L, TimeUnit.SECONDS,
    new MpscLinkedQueue<Runnable>(),   // MPSC 队列（多生产者单消费者，吞吐量高于 LinkedBlockingQueue）
    new DefaultThreadFactory("biz")
);
```

| 维度 | JDK ThreadPoolExecutor | Netty UnorderedThreadPoolExecutor |
|------|----------------------|-----------------------------------|
| 队列 | `LinkedBlockingQueue` | **`MpscLinkedQueue`**（更高的并发入队性能） |
| 拒绝日志 | 无 | 警告日志 |
| EventExecutor 集成 | 无 | 继承 `EventExecutorGroup`，Future 可监听 |
| 任务有序性 | FIFO 严格有序 | Unordered 名字明示不保证顺序 |

> Netty EventLoop **不是** `UnorderedThreadPoolExecutor`——EventLoop 是单线程串行；`UnorderedThreadPoolExecutor` 是 Netty 给业务代码用的并行线程池。

---

> **核心要点**：Netty 线程模型的核心是「**EventLoop 单线程串行 + ChannelHandler 无锁化**」；业务长任务必须主动切到 `UnorderedThreadPoolExecutor`，再通过 `ctx.channel().eventLoop().execute(...)` 把写回动作切回 IO 线程——这种「切线程不切顺序」的设计是 Netty 高性能的关键。

---

## 反向链

- [Java 线程池（01.java-and-jvm）](../../../01.java-and-jvm/03-concurrency/thread-pool/README.md) — JDK ThreadPoolExecutor 与 Netty UnorderedThreadPoolExecutor 的差异
