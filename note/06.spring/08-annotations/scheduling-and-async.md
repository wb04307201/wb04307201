# 调度与异步注解

> 最后更新: 2026-06-14
> ⬅️ [返回注解速查](../README.md) | [事务注解](transaction.md)

本节是 `@Scheduled` / `@Async` / `@EnableScheduling` / `@EnableAsync` 的速查手册——定时任务、异步方法、线程池配置。**深读请前往 [04-spring-boot/startup-flow](../../04-spring-boot/startup-flow.md)**。

---

## 🎯 一句话定位

**调度注解 = "按时间表触发"**（`@Scheduled` + `@EnableScheduling`），**异步注解 = "把方法丢到线程池执行"**（`@Async` + `@EnableAsync`）。

---

## 一、@EnableScheduling / @EnableAsync

> 在启动类或配置类上启用功能。Spring Boot 不会自动启用这两个特性。

```java
@SpringBootApplication
@EnableScheduling   // 启用 @Scheduled
@EnableAsync        // 启用 @Async
public class App { }
```

---

## 二、@Scheduled 4 种时间表达式

> **必须**配合 `@EnableScheduling` 才会生效。

| 属性 | 类型 | 说明 | 示例 |
|:-----|:-----|:-----|:-----|
| `fixedRate` | long (ms) | 从**方法开始**算起的间隔（**前一次开始 → 下一次开始**） | `fixedRate = 5000` |
| `fixedDelay` | long (ms) | 从**方法结束**算起的间隔（**前一次结束 → 下一次开始**） | `fixedDelay = 5000` |
| `initialDelay` | long (ms) | 首次执行前的延迟 | `initialDelay = 10000` |
| `cron` | String | Cron 表达式（**6 字段**，含秒） | `cron = "0 0 2 * * ?"` |
| `zone` | String | 时区（默认 JVM 时区） | `zone = "Asia/Shanghai"` |

```java
@Component
public class ScheduledTasks {

    @Scheduled(fixedRate = 5000)                    // 每 5s 一次
    public void heartbeat() { ... }

    @Scheduled(fixedDelay = 5000, initialDelay = 10000)   // 10s 后开始，每次结束 +5s
    public void poll() { ... }

    @Scheduled(cron = "0 0 2 * * ?")               // 每天凌晨 2 点
    public void dailyJob() { ... }
}
```

### fixedRate vs fixedDelay

```
fixedRate  : |---任务---|---任务---|---任务---|    （从开始算）
fixedDelay: |---任务---| ⏳5s |---任务---| ⏳5s |---任务---|  （从结束算）
```

> 📌 任务执行时长 > 间隔时，`fixedRate` 会**立即连发**下一轮；`fixedDelay` 总能保证间隔。

---

## 三、Cron 表达式 6 字段速查

```
┌────── 秒 (0-59)
│ ┌──── 分钟 (0-59)
│ │ ┌── 小时 (0-23)
│ │ │ ┌─ 日 (1-31)
│ │ │ │ ┌─ 月 (1-12)
│ │ │ │ │ ┌─ 星期 (0-7, 0=7=周日)
│ │ │ │ │ │
* * * * * *
```

| 字段 | 范围 | 特殊字符 |
|:-----|:-----|:---------|
| 秒 | 0-59 | `*` `,` `-` `/` |
| 分 | 0-59 | 同上 |
| 时 | 0-23 | 同上 |
| 日 | 1-31 | `*` `,` `-` `/` `?` `L` `W` |
| 月 | 1-12（或 JAN-DEC） | `*` `,` `-` `/` |
| 周 | 0-7（0=7=周日） | `*` `,` `-` `/` `?` `L` `#` |

| 表达式 | 含义 |
|:-------|:-----|
| `0 0 2 * * ?` | 每天凌晨 2 点 |
| `0 0/30 9-17 * * ?` | 9-17 点每 30 分钟 |
| `0 0 12 * * MON-FRI` | 工作日中午 12 点 |
| `0 15 10 L * ?` | 每月最后一天 10:15 |
| `0 0 0 1 1 ?` | 每年 1 月 1 日 0 点 |

> 💡 在线工具：[cron.qqe2.com](https://cron.qqe2.com/)

---

## 四、@Async 关键属性

> **必须**配合 `@EnableAsync` 才会生效。方法会**在调用方的线程**（默认 `SimpleAsyncTaskExecutor`）之外异步执行。

| 属性 | 默认 | 说明 |
|:-----|:-----|:-----|
| `value` | — | 指定 `Executor` Bean 名称 |

```java
@Service
public class NotifyService {

    @Async
    public CompletableFuture<String> sendAsync(String user) {
        // 异步执行
        return CompletableFuture.completedFuture("OK");
    }

    @Async("taskExecutor")     // 指定线程池
    public void send(String user) { ... }
}
```

### 适用与失效

| 场景 | 表现 |
|:-----|:-----|
| ✅ 异步调用方 / Controller 注入 Service | 生效（走代理） |
| ❌ **同类 self-invocation** | 失效（绕过代理） |
| ❌ **private / final 方法** | 失效（无法生成代理） |
| ❌ 静态方法 | 失效（无对象代理） |

```java
// ❌ 失效
@Service
public class NotifyService {
    public void sendAll() {
        send("a");     // 内部调用，不走代理
    }
    @Async public void send(String user) { ... }
}

// ✅ 正确：拆 Bean 或注入自己
@Service
public class NotifyService {
    @Lazy @Autowired private NotifyService self;

    public void sendAll() {
        self.send("a");     // 走代理
    }
    @Async public void send(String user) { ... }
}
```

### 返回类型

| 返回类型 | 行为 |
|:---------|:-----|
| `void` | 异步执行，调用方立即返回 |
| `CompletableFuture<T>` | 拿到异步结果（`future.get()` 阻塞 / `thenAccept()` 回调） |
| `Future<T>` | 拿结果 |
| 普通类型 | **总是返回 `null`**（返回值被吞掉） |

---

## 五、自定义 TaskExecutor / 线程池

> Spring Boot 默认提供 `ThreadPoolTaskExecutor` Bean（来自 `TaskExecutionAutoConfiguration`）。

```java
@Configuration
public class AsyncConfig {

    @Bean("taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor exec = new ThreadPoolTaskExecutor();
        exec.setCorePoolSize(8);
        exec.setMaxPoolSize(32);
        exec.setQueueCapacity(200);
        exec.setKeepAliveSeconds(60);
        exec.setThreadNamePrefix("async-");
        exec.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        exec.initialize();
        return exec;
    }
}
```

```yaml
# Spring Boot 也支持配置文件方式（推荐）
spring:
  task:
    execution:
      pool:
        core-size: 8
        max-size: 32
        queue-capacity: 200
        keep-alive: 60s
      thread-name-prefix: async-
```

### 调度器线程池

```java
@Configuration
public class SchedulingConfig implements SchedulingConfigurer {
    @Override
    public void configureTasks(ScheduledTaskRegistrar taskRegistrar) {
        taskRegistrar.setScheduler(pooledScheduler());
    }

    @Bean(destroyMethod = "shutdown")
    public ExecutorService pooledScheduler() {
        return Executors.newScheduledThreadPool(4);
    }
}
```

---

## 🤔 思考

1. **为什么 @Async 必须 public？** Spring 通过代理调用，private 方法不会被代理拦截。
2. **@Async 抛异常会怎样？** 默认会丢失（无返回值时）。建议返回 `CompletableFuture` 并用 `.exceptionally()` 处理。
3. **@Scheduled 单线程还是多线程？** 默认单线程——多个 `@Scheduled` 任务**串行执行**，长任务会阻塞其他任务。建议配置 `TaskScheduler` 池。
4. **@Async 与 @Transactional 共存？** `@Async` 跑在独立线程，**不继承调用方事务**！需要事务请在 `@Async` 方法自身加 `@Transactional`。
5. **分布式定时任务？** 多实例部署时 `@Scheduled` 会**重复触发**。生产请用 XXL-Job / ElasticJob / ShedLock 等分布式调度方案。

---

## 深入阅读

- [04-spring-boot/startup-flow](../../04-spring-boot/startup-flow.md) — 启动与后台任务线程池
- [04-spring-boot/externalized-configuration](../../04-spring-boot/externalized-configuration.md) — 线程池配置 externalization

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [事务注解](transaction.md) — @Async 与 @Transactional 的线程边界
- [配置注解](configuration.md) — @EnableScheduling / @EnableAsync
