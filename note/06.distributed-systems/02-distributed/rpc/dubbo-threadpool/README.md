<!--
module:
  parent: system-design
  slug: system-design/rpc/dubbo-threadpool
  type: article
  category: 主模块子文章
  summary: Dubbo 通过 SPI 机制提供 4 种可插拔线程池（Fixed / Cached / Limited / Eager），Eager 模式兼顾突发流量与资源受控
  depth: ⭐⭐⭐
-->

# Dubbo 线程池模型

> **一句话定位**：Dubbo 通过 SPI（`@SPI` 注解）实现 4 种可插拔线程池；**Eager 模式是生产推荐**，兼顾突发流量快速响应与资源受控。

> ⬅️ [返回 RPC 总览](../README.md) | [Apache Dubbo 总览](../apache-dubbo/README.md)

---

## 一、4 种内置线程池

Dubbo 的 `ThreadPool` 接口通过 `@SPI` 暴露 4 种实现：

| 实现类 | 对应 JDK 类型 | 队列 | 特点 | 适用场景 |
|--------|---------------|------|------|----------|
| `FixedThreadPool` | `newFixedThreadPool` | `LinkedBlockingQueue`（无界） | 固定大小 | **生产慎用**（无界队列 OOM） |
| `CachedThreadPool` | `newCachedThreadPool` | `SynchronousQueue` | 弹性扩缩 + 60s 回收 | 短任务、突发流量 |
| `LimitedThreadPool` | 自定义 | `LinkedBlockingQueue`（可指定容量） | 固定大小 + 有界队列 | **生产推荐** |
| `EagerThreadPool` | 自定义 | 自定义 `TaskQueue` | **优先入队，队列满才创建线程** | **生产推荐**（默认） |

## 二、配置方式

```yaml
# application.yml
dubbo:
  protocol:
    name: dubbo
    port: 20880
    threadpool: eager   # fixed | cached | limited | eager
    threads: 200
    iothreads: 8        # IO 线程（Netty boss + worker）
    queues: 0           # 队列容量（0 表示使用 SynchronousQueue / 自定义 eager 队列）
```

或代码配置：

```java
ProtocolConfig protocol = new ProtocolConfig();
protocol.setThreadpool("eager");
protocol.setThreads(200);
```

## 三、Eager 模式核心原理

Eager 模式的关键在重写 `TaskQueue.offer()`：返回 `false` 时，JDK `ThreadPoolExecutor` 会跳过「入队」直接 `addWorker` 创建新线程。

```java
public class EagerThreadPoolExecutor extends ThreadPoolExecutor {

    public EagerThreadPoolExecutor(int corePoolSize, int maximumPoolSize, ...) {
        super(corePoolSize, maximumPoolSize, ..., new TaskQueue<>());
    }

    @Override
    public void execute(Runnable command) {
        // ... 省略：先尝试 addWorker，失败再走父类逻辑
    }
}

public class TaskQueue<R extends Runnable> extends LinkedBlockingQueue<R> {
    private EagerThreadPoolExecutor executor;

    @Override
    public boolean offer(Runnable r) {
        if (executor.getPoolSize() < executor.getMaximumPoolSize()) {
            return false;   // 故意返回 false → 触发 addWorker 创建新线程
        }
        return super.offer(r);  // 真的满 → 走队列
    }
}
```

**Eager 模式的价值**：

| 场景 | Fixed 模式 | Eager 模式 |
|------|-----------|-----------|
| 突发流量 + 队列未满 | 任务在队列等待 → 响应延迟 | 立即创建新线程 → 快速响应 |
| 持续高负载 | 队列堆积 → OOM | 线程达 maxPoolSize → 走拒绝策略 |
| 资源占用 | 固定线程数 | 弹性伸缩 |

## 四、推荐选型

| 业务特征 | 推荐线程池 |
|---------|-----------|
| RPC Provider 高 QPS、突发流量 | **EagerThreadPool**（默认） |
| 后台批处理、限流场景 | LimitedThreadPool |
| 短任务、瞬时突发 | CachedThreadPool（注意 maxThreads） |
| 固定负载的内部服务 | FixedThreadPool（生产慎用无界队列） |

---

> **核心要点**：Dubbo 线程池不是「JDK 线程池的简单套壳」，而是把 JDK 的「核心线程 → 队列 → 非核心线程」三级模型通过 SPI 改造为可插拔架构；Eager 模式是 Dubbo 对 JDK 默认行为的反思——**「队列不应该是任务等待的唯一场所」**。

---

## 反向链

- [Java 线程池（01.java-and-jvm）](../../../01.java-and-jvm/03-concurrency/thread-pool/README.md) — JDK ThreadPoolExecutor 七大参数与 Eager 重写 offer 的原理
- [Apache Dubbo 总览](../apache-dubbo/README.md) — Dubbo 整体架构与服务治理
