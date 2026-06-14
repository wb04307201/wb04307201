# 重试注解

> 最后更新: 2026-06-14
> ⬅️ [返回注解速查](../README.md) | [校验注解](validation.md)

本节是 Spring Retry `@Retryable` / `@Recover` / `@EnableRetry` 的速查手册。**深读请前往 [06-integration/retry](../../06-integration/retry.md)**。

---

## 🎯 一句话定位

**重试注解 = "调用失败就再试几次"**——`@Retryable` 标记重试方法，`@Recover` 提供兜底回调，`@EnableRetry` 启用功能。

---

## 一、@EnableRetry

```java
@SpringBootApplication
@EnableRetry   // 启用 @Retryable 代理
public class App { }
```

> 需引入 `spring-retry` 依赖：
> ```xml
> <dependency>
>     <groupId>org.springframework.retry</groupId>
>     <artifactId>spring-retry</artifactId>
> </dependency>
> <dependency>
>     <groupId>org.springframework.boot</groupId>
>     <artifactId>spring-boot-starter-aop</artifactId>  <!-- 代理所需 -->
> </dependency>
> ```

---

## 二、@Retryable 关键属性

| 属性 | 默认 | 说明 |
|:-----|:-----|:-----|
| `value` / `include` | `{}` | 触发重试的异常类型（**包含**） |
| `exclude` | `{}` | 排除的异常类型（即使发生也不重试） |
| `retryFor` | `{}` | 触发重试的异常类型（Spring Retry 2.0+ 替代 `value`） |
| `maxAttempts` | `3` | 最大尝试次数（**包括首次**） |
| `backoff` | `@Backoff()` | 退避策略（见下） |
| `label` | `""` | 重试分组标签 |
| `listeners` | `{}` | 监听器（`RetryListener`） |

```java
@Retryable(
    retryFor = { IOException.class, TimeoutException.class },
    maxAttempts = 4,
    backoff = @Backoff(delay = 1000, multiplier = 2)   // 1s, 2s, 4s ...
)
public String callRemote() { ... }
```

> ⚠️ `value` / `include` 与 `retryFor` 含义相同，**后者是 Spring Retry 2.0+ 推荐的现代写法**。

---

## 三、@Backoff 3 种退避策略

| 策略 | 写法 | 行为 |
|:-----|:-----|:-----|
| **固定间隔** | `@Backoff(delay = 1000)` | 每次重试间隔固定 1s |
| **指数退避** | `@Backoff(delay = 1000, multiplier = 2)` | 1s → 2s → 4s → 8s … |
| **随机退避** | `@Backoff(delay = 1000, multiplier = 2, random = true)` | 指数 + 随机抖动（避免雪崩） |
| **最大间隔** | `@Backoff(delay = 1000, maxDelay = 10000, multiplier = 2)` | 指数但封顶 10s |

```java
// 指数退避：1s, 2s, 4s, 8s
@Retryable(retryFor = Exception.class, backoff = @Backoff(delay = 1000, multiplier = 2))

// 随机退避：避免集群同一时刻重试打爆下游
@Retryable(retryFor = Exception.class, backoff = @Backoff(delay = 500, multiplier = 2, random = true))
```

---

## 四、@Recover 兜底方法

> 重试次数耗尽后**最后一次抛出**的异常会作为参数，调用 `@Recover` 标注的兜底方法。

### 签名规则

> 1. **返回类型** 与 `@Retryable` 方法**完全相同**
> 2. 方法**第一个参数** 是抛出的异常类型（Throwable 子类）
> 3. 后续参数 与 `@Retryable` 方法参数**完全一致**
> 4. **必须**与 `@Retryable` 方法在**同一个类**中

```java
@Service
public class RemoteService {

    @Retryable(
        retryFor = { IOException.class },
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000)
    )
    public String call(String url) throws IOException {
        return restTemplate.getForObject(url, String.class);
    }

    @Recover
    public String fallback(IOException e, String url) {       // 第一个参数是异常
        log.warn("调用 {} 失败，兜底返回", url, e);
        return "DEFAULT";                                    // 兜底逻辑
    }
}
```

### 多个 Recover 兜底

> 不同异常类型可对应不同的 Recover 方法。

```java
@Recover
public String recoverIO(IOException e, String url) { return "DEFAULT-IO"; }

@Recover
public String recoverTimeout(TimeoutException e, String url) { return "DEFAULT-TIMEOUT"; }
```

---

## 五、适用与失效场景

| 场景 | 表现 |
|:-----|:-----|
| ✅ 远程调用（HTTP / RPC） | 偶发网络抖动、瞬时故障 |
| ✅ 数据库死锁 | 短时间内重试可能成功 |
| ✅ 消息中间件发送 | Send retry |
| ❌ **同类 self-invocation** | 不生效（绕过代理） |
| ❌ **private / final 方法** | 不生效 |
| ❌ 业务校验失败（参数错误） | **不应该**重试——用 `retryFor` 限定异常 |
| ❌ 非幂等操作（扣款、写库） | 重试可能产生副作用——需配合幂等键 |

```java
// ❌ 错误：内部调用不生效
public void outer() {
    inner();   // 绕过代理
}
@Retryable public void inner() { ... }

// ✅ 正确：注入自己 / 拆 Bean
@Autowired @Lazy private RemoteService self;
public void outer() { self.inner(); }
```

---

## 六、典型使用模板

```java
@Service
public class PaymentService {

    @Retryable(
        retryFor = { RestClientException.class },
        maxAttempts = 3,
        backoff = @Backoff(delay = 2000, multiplier = 2, random = true)
    )
    public PaymentResult pay(OrderDTO order) {
        return paymentGateway.charge(order);
    }

    @Recover
    public PaymentResult recover(RestClientException e, OrderDTO order) {
        // 落库标记"待重试"，由定时任务对账
        pendingRepo.save(new PendingPayment(order, e.getMessage()));
        return PaymentResult.pending();
    }
}
```

---

## 🤔 思考

1. **什么时候用 retry？** 失败**临时性** + **可重入**（幂等）——例如 HTTP 503、DB 死锁。
2. **重试与熔断的关系？** 重试放外面（补刀），熔断放外面（自我保护，避免放大故障）。生产建议**重试 + 熔断 + 限流**三件套：Resilience4j。
3. **@Retryable 与 @Transactional 顺序？** 代理层面，**事务在外、重试在内**：外层事务包裹整个"重试循环"，失败会回滚所有尝试。建议把 `@Retryable` 放在**单独 Bean** 而非事务方法上。
4. **同步重试 vs 异步重试？** Spring Retry 默认同步阻塞；如需异步可结合 `@Async`（注意线程安全）。

---

## 深入阅读

- [06-integration/retry](../../06-integration/retry.md) — Spring Retry 完整指南
- [06-integration/batch](../../06-integration/batch.md) — 失败重试与跳过（批处理场景）

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [事务注解](transaction.md) — 重试与事务的边界关系
