<!--
module:
  parent: system-design
  slug: system-design/tomcat-threadpool
  type: article
  category: 主模块子文章
  summary: Tomcat 自定义 TaskQueue（继承 LinkedBlockingQueue）通过 force() 强制入队逻辑绕过 JDK 默认的「核心线程满 → 入队」行为
  depth: ⭐⭐⭐
-->

# Tomcat 线程池调优（TaskQueue）

> **一句话定位**：Tomcat 自定义 `TaskQueue`（继承 `LinkedBlockingQueue`），通过 `force()` 强制入队逻辑绕过 JDK 的「核心线程满 → 入队」默认行为，让线程数更快涨到 maxThreads。

> ⬅️ [返回 06 Distributed 总览](../../README.md)

---

## 一、Tomcat 线程模型

```text
┌─────────────────────────────────────────────────────────┐
│  Acceptor (1~2 线程)                                    │
│      │                                                  │
│      ▼                                                  │
│  Poller (NIO Selector, 默认 2 线程)                      │
│      │                                                  │
│      ▼                                                  │
│  Executor (ThreadPoolExecutor，默认 200 线程)           │
│      │                                                  │
│      ▼                                                  │
│  CoyoteAdapter → Servlet → 用户代码                       │
└─────────────────────────────────────────────────────────┘
```

| 组件 | 线程数 | 角色 |
|------|--------|------|
| **Acceptor** | 1~2 | 接收 TCP 连接，accept() |
| **Poller** | `selectorCount`（默认 2） | NIO Selector 检测可读事件 |
| **Executor** | `maxThreads`（默认 200） | 处理 HTTP 请求（运行用户代码） |

## 二、Tomcat TaskQueue 的「黑科技」

Tomcat 默认行为（`server.xml` / `application.yml`）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `server.tomcat.threads.max` | 200 | 最大线程数（= `maximumPoolSize`） |
| `server.tomcat.threads.min-spare` | 25 | 核心线程数（= `corePoolSize`） |
| `server.tomcat.accept-count` | 100 | 等待队列容量（= `workQueue` 容量） |
| `server.tomcat.max-connections` | 8192 | 最大连接数 |
| `server.tomcat.connection-timeout` | 20000 | 连接超时（ms） |

**JDK 默认 vs Tomcat 改造**：

```text
JDK 默认：
  core 满 → 入队 → 队列满 → 创建非核心线程

Tomcat TaskQueue.offer() 重写后：
  if (当前线程数 < maxThreads) return false;  // 强制返回 false → 触发 addWorker
  return super.offer(r);                        // 真的超过 maxThreads 才入队
```

```java
// Tomcat 源码：org.apache.tomcat.util.threads.TaskQueue
public class TaskQueue extends LinkedBlockingQueue<Runnable> {
    private transient volatile ThreadPoolExecutor parent;

    @Override
    public boolean offer(Runnable o) {
        // 关键：如果线程数还没到 maxThreads，故意返回 false
        if (parent == null) return super.offer(o);
        if (parent.getPoolSize() < parent.getMaximumPoolSize()) {
            return false;   // 触发 JDK 创建新线程
        }
        return super.offer(o);
    }

    public boolean force(Runnable o) {
        // force() 永远入队成功（用于关闭前的兜底）
        if (parent == null || parent.isShutdown()) throw new RejectedExecutionException(...);
        return super.offer(o);
    }
}
```

## 三、调优建议

| 场景 | 配置 |
|------|------|
| **CPU 密集型 API**（计算、序列化） | `max-threads = CPU 核数 + 1` |
| **IO 密集型 API**（DB 查询、远程调用） | `max-threads = CPU 核数 × 4 ~ 8` |
| **高并发 + 长任务** | 降低 `max-threads`，配合异步化 / 消息队列 |
| **线程数达到 max 后** | 任务进入 `accept-count` 队列；队列满 → 拒绝连接（返回 503） |

```yaml
# application.yml
server:
  tomcat:
    threads:
      max: 400              # 最大线程数
      min-spare: 50         # 核心线程数
    accept-count: 200       # 等待队列容量
    max-connections: 10000  # 最大连接数
    connection-timeout: 30000
```

## 四、监控指标

通过 JMX 或 Micrometer 暴露：

```java
Gauge.builder("tomcat.threads.busy", () -> ManagementFactory.getPlatformMBeanServer()
    .getAttribute(new ObjectName("Tomcat:type=ThreadPool,name=\"http-nio-8080\""), "currentThreadsBusy"))
    .register(registry);
```

| 指标 | 含义 | 告警阈值 |
|------|------|----------|
| `currentThreadsBusy` | 正在执行请求的线程数 | > 80% × maxThreads 持续 5min |
| `currentThreadCount` | 当前线程数 | > maxThreads 持续 1min |
| `backlog` | accept-count 队列长度 | > 50% × accept-count |

---

> **核心要点**：Tomcat 线程池是「**对 JDK ThreadPoolExecutor 的实战级改造**」——通过 `TaskQueue.offer()` 返回 false 让线程数优先涨到 maxThreads，再走队列兜底。这种设计更适合 Web 容器场景：**响应速度 > 队列堆积**，但代价是 maxThreads 配错会导致线程数爆炸。

---

## 反向链

- [Java 线程池（01.java-and-jvm）](../../../01.java-and-jvm/03-concurrency/thread-pool/README.md) — JDK ThreadPoolExecutor 默认行为与 Tomcat TaskQueue 重写 offer 的原理
