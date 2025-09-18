# 线程池

在Java和Spring生态中，线程池是并发编程的核心工具，用于管理线程资源、提升系统性能。

## 一、Java原生线程池（基于`java.util.concurrent`）

### 1. 四大核心线程池（通过`Executors`工厂方法创建）
| 线程池类型                         | 特性                                    | 适用场景             | 潜在风险        |
|-------------------------------|---------------------------------------|------------------|-------------|
| **`newFixedThreadPool`**      | 固定大小线程池，使用无界队列（`LinkedBlockingQueue`） | 长期任务、负载均衡（如日志处理） | 无界队列可能导致OOM |
| **`newCachedThreadPool`**     | 线程数无上限，使用`SynchronousQueue`           | 短时间大量任务（如HTTP请求） | 线程数爆炸导致资源耗尽 |
| **`newSingleThreadExecutor`** | 单线程，任务顺序执行（FIFO）                      | 顺序任务（如单线程文件写入）   | 性能瓶颈（单线程）   |
| **`newScheduledThreadPool`**  | 支持定时/周期性任务，使用`DelayedWorkQueue`       | 定时任务（如数据备份）      | 任务堆积时队列无界   |

### 2. 高级线程池（直接使用`ThreadPoolExecutor`）
- **核心参数**：
    - `corePoolSize`：核心线程数（CPU密集型任务=CPU核数，IO密集型任务=CPU核数×2）。
    - `maximumPoolSize`：最大线程数（短期高并发=略大于核心数，长期高并发=动态调整）。
    - `workQueue`：任务队列（高并发推荐`SynchronousQueue`，普通任务推荐`ArrayBlockingQueue`）。
    - `rejectedExecutionHandler`：拒绝策略（推荐`CallerRunsPolicy`避免任务丢失）。
- **示例配置**：
  ```java
  ThreadPoolExecutor executor = new ThreadPoolExecutor(
      4, // corePoolSize
      16, // maximumPoolSize
      60, TimeUnit.SECONDS, // keepAliveTime
      new LinkedBlockingQueue<>(1000), // workQueue
      new CallerRunsPolicy() // rejectedExecutionHandler
  );
  ```

### 3. Fork/Join线程池（`ForkJoinPool`）
- **特性**：基于“分治+工作窃取”算法，适合大规模并行计算。
- **适用场景**：大数据处理、复杂计算（如矩阵运算）。
- **示例**：
  ```java
  ForkJoinPool pool = new ForkJoinPool(Runtime.getRuntime().availableProcessors());
  pool.invoke(new RecursiveTask<Integer>() { /* 任务实现 */ });
  ```

## 二、Spring线程池（基于`TaskExecutor`封装）

### 1. Spring原生线程池
- **`SimpleAsyncTaskExecutor`**：
    - **特性**：每次任务创建新线程，默认无资源限制。
    - **适用场景**：简单异步任务（不推荐生产环境使用）。
- **`ThreadPoolTaskExecutor`**：
    - **特性**：对`ThreadPoolExecutor`的封装，支持Spring配置。
    - **核心参数**：
        - `corePoolSize`：核心线程数。
        - `maxPoolSize`：最大线程数。
        - `queueCapacity`：队列容量。
        - `threadNamePrefix`：线程名前缀（便于调试）。
    - **配置示例**：
      ```java
      @Configuration
      @EnableAsync
      public class ThreadPoolConfig {
          @Bean("taskExecutor")
          public ThreadPoolTaskExecutor executor() {
              ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
              executor.setCorePoolSize(5);
              executor.setMaxPoolSize(10);
              executor.setQueueCapacity(25);
              executor.setThreadNamePrefix("MyExecutor-");
              executor.initialize();
              return executor;
          }
      }
      ```

### 2. Spring异步任务支持
- **`@Async`注解**：
    - **用法**：在方法上标注`@Async`，指定线程池名称（如`@Async("taskExecutor")`）。
    - **示例**：
      ```java
      @Service
      public class AsyncService {
          @Async("taskExecutor")
          public void executeTask(int i) {
              System.out.println(Thread.currentThread().getName() + " 执行任务: " + i);
          }
      }
      ```

### 3. Spring定时任务线程池
- **`ThreadPoolTaskScheduler`**：
    - **特性**：支持定时和周期性任务。
    - **配置示例**：
      ```java
      @Configuration
      public class SchedulerConfig {
          @Bean
          public ThreadPoolTaskScheduler taskScheduler() {
              ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
              scheduler.setPoolSize(5);
              scheduler.setThreadNamePrefix("Scheduler-");
              scheduler.initialize();
              return scheduler;
          }
      }
      ```

## 三、线程池选择与最佳实践

### 1. 场景化推荐
| 场景           | 推荐线程池                                     | 配置建议                        |
|--------------|-------------------------------------------|-----------------------------|
| **CPU密集型任务** | `ThreadPoolExecutor`                      | `corePoolSize=CPU核数+1`，无界队列 |
| **IO密集型任务**  | `ThreadPoolExecutor`                      | `corePoolSize=CPU核数×2`，有界队列 |
| **高并发突发请求**  | `ThreadPoolExecutor` + `SynchronousQueue` | 快速拒绝新任务（避免雪崩）               |
| **定时任务**     | `ScheduledThreadPoolExecutor`             | 固定线程数（如4）                   |
| **顺序任务**     | `SingleThreadExecutor`                    | 无队列或小队列                     |

### 2. 避免的陷阱
- **无界队列**：可能导致OOM（如`LinkedBlockingQueue`默认`Integer.MAX_VALUE`）。
- **线程数爆炸**：`CachedThreadPool`在极端情况下会创建过多线程。
- **任务丢失**：未正确配置拒绝策略（推荐`CallerRunsPolicy`）。

### 3. 监控与调优
- **监控指标**：
    - `getPoolSize()`：当前线程数。
    - `getActiveCount()`：活跃线程数。
    - `getQueue().size()`：队列任务数。
- **工具推荐**：
    - **Prometheus + Grafana**：实时监控线程池状态。
    - **JMX**：通过JConsole或VisualVM查看线程池运行数据。