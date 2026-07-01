# WebClient 响应式 HTTP 客户端

> ⬅️ [返回 WebFlux 总览](README.md) | [02 Web 层](../README.md)

**WebClient** 是 Spring 5 引入的**非阻塞响应式 HTTP 客户端**，是 `RestTemplate`（已维护模式）的现代替代品。本文覆盖 WebClient 的同步/异步/流式调用、错误处理、超时/重试/限流、与 OpenFeign 的对比与选型。

---

## 🎯 一句话定位

**WebClient = "在响应式栈里调 HTTP"**——`RestTemplate` 用线程等结果，WebClient 用事件循环等回调；返回值始终是 `Mono<T>` / `Flux<T>`，可与 Reactor 全家桶无缝组合。

---

## 一、依赖与基础配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

> **注意**：引入 `spring-boot-starter-webflux` 后，默认容器会从 Tomcat 切换为 Netty。如果同时想用 MVC，**不要**让两个 starter 同时存在。

### 注入 WebClient

```java
@Bean
public WebClient webClient() {
    return WebClient.builder()
            .baseUrl("https://api.example.com")
            .defaultHeader(HttpHeaders.USER_AGENT, "demo/1.0")
            .defaultCookie("session", "abc123")
            .codecs(c -> c.defaultCodecs().maxInMemorySize(2 * 1024 * 1024)) // 2MB
            .build();
}
```

---

## 二、三种调用形态

### 1. 同步获取（仅在测试/边界使用）

```java
User user = webClient.get()
        .uri("/users/{id}", 1L)
        .retrieve()
        .bodyToMono(User.class)
        .block(); // 业务链路上禁止使用
```

### 2. 异步编排（推荐）

```java
Mono<User> userMono = webClient.get()
        .uri("/users/{id}", id)
        .retrieve()
        .bodyToMono(User.class);

// 进一步组合
Mono<UserDetail> detail = userMono.flatMap(user ->
        webClient.get().uri("/orders/{uid}", user.getId())
                .retrieve()
                .bodyToFlux(Order.class)
                .collectList()
                .map(orders -> new UserDetail(user, orders))
);
```

### 3. 流式消费（SSE / NDJSON / 大响应）

```java
webClient.get()
        .uri("/events/stream")
        .accept(MediaType.TEXT_EVENT_STREAM)
        .retrieve()
        .bodyToFlux(Event.class)
        .doOnNext(evt -> sink.tryEmitNext(evt))
        .subscribe();
```

---

## 三、retrieve() 与 exchangeToMono() 对比

| 维度 | `retrieve()` | `exchangeToMono()` / `exchangeToFlux()` |
|------|--------------|----------------------------------------|
| **状态码处理** | 4xx/5xx 自动抛 `WebClientResponseException` | 完全由开发者决定 |
| **响应头/原始字节** | 不暴露 | 可读 `ClientResponse` |
| **适用场景** | 95% 业务调用 | 文件下载、自定义错误、跨服务转发 |

```java
// exchangeToFlux 示例：自定义状态码处理
Flux<ByteBuffer> body = webClient.get()
        .uri("/files/{id}", id)
        .exchangeToFlux(resp -> {
            if (resp.statusCode().is2xxSuccessful()) {
                return resp.bodyToFlux(ByteBuffer.class);
            }
            return resp.createException().flatMapMany(Mono::error);
        });
```

---

## 四、错误处理

```java
Mono<User> user = webClient.get()
        .uri("/users/{id}", id)
        .retrieve()
        .bodyToMono(User.class)
        .onErrorResume(WebClientResponseException.NotFound.class,
                e -> Mono.error(new BizException("USER_NOT_FOUND")))
        .onErrorResume(WebClientResponseException.class,
                e -> Mono.error(new BizException("UPSTREAM_ERROR", e)))
        .timeout(Duration.ofSeconds(3), Mono.error(new BizException("UPSTREAM_TIMEOUT")))
        .retryWhen(Retry.backoff(3, Duration.ofMillis(200)) // 指数退避重试 3 次
                .filter(t -> t instanceof WebClientResponseException.ServiceUnavailable));
```

| 异常类型 | 触发条件 |
|----------|----------|
| `WebClientResponseException` | 4xx/5xx 默认（`retrieve()` 抛） |
| `WebClientRequestException` | 连接失败、超时、SSL 错误 |
| `ExchangeFunction` 自定义 | 业务侧显式抛 |

---

## 五、超时、重试、限流

### 1. 超时（响应式栈推荐 `timeout` 而非全局 `connectTimeout`）

```java
.webClient(...)
        .clientConnector(new ReactorClientHttpConnector(
                HttpClient.create()
                        .responseTimeout(Duration.ofSeconds(5))
                        .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 3000)))
```

### 2. 重试

```java
.retryWhen(Retry.fixedDelay(3, Duration.ofSeconds(1))
        .filter(t -> t instanceof WebClientRequestException))
```

### 3. 限流（Resilience4j 集成）

```java
User result = rateLimiter.executeSupplier(() ->
        webClient.get().uri("/users/{id}", id).retrieve().bodyToMono(User.class).block()
);
```

或者通过 `WebClientCustomizer` + `Resilience4jWebClient` 装饰器为每个请求加熔断/限流。

---

## 六、Spring Cloud OpenFeign 的响应式模式

`@FeignClient` 默认走 `Client` 抽象（HttpURLConnection），要变响应式需：

```java
@Bean
public ReactiveFeignCustomizer reactiveCustomizer() {
    return builder -> builder.client(new ReactorClientHttpConnector(HttpClient.create()));
}

@FeignClient(name = "user-svc", configuration = UserClientConfig.class)
public interface UserClient {
    @GetMapping("/users/{id}")
    Mono<User> findById(@PathVariable Long id);
}
```

> 集成复杂、默认仍是 `CompletableFuture` 行为；**WebFlux 体系下首选 WebClient**。

---

## 七、WebClient vs OpenFeign vs RestTemplate

| 维度 | WebClient | OpenFeign | RestTemplate |
|------|-----------|-----------|--------------|
| **响应式** | 原生 Mono/Flux | 通过适配 | 不支持 |
| **同步调用** | 需 `.block()` | 原生 | 原生 |
| **声明式客户端** | ❌（手写 builder） | ✅（注解 + 接口） | ❌ |
| **服务发现集成** | 需结合 LoadBalancer ExchangeFilterFunction | ✅（@FeignClient + name） | 需手动拼 URL |
| **可观测性** | WebClient Observation (Boot 3+) | Micrometer 内置 | 弱 |
| **维护状态** | 推荐 | 推荐（Spring Cloud） | 维护模式 |
| **典型场景** | WebFlux 应用内 | 跨服务调用（MVC） | 老项目维护 |

> **选型建议**：
> - WebFlux 应用 → **WebClient**（全栈同语言）
> - MVC + 大量服务间调用 → **OpenFeign**（声明式 + 服务发现）
> - 简单单次调用 → WebClient 或 RestTemplate 均可

---

## 八、常见问题

1. **响应式栈里调用 OpenFeign**：要小心线程模型，Feign 默认阻塞，要么切 `boundedElastic`，要么用响应式 Feign。
2. **大文件下载**：使用 `exchangeToFlux` + `DataBuffer`，避免一次性 `bodyToByteArray()` 吃满内存。
3. **Cookies / 鉴权传递**：使用 `ExchangeFilterFunction` 拦截修改 `ClientRequest`。
4. **日志**：开启 `org.springframework.web.reactive.function.client` 的 DEBUG 级别，或挂 `ExchangeFilterFunction` 打印请求/响应。

---

## 相关章节

- ⬅️ [WebFlux 总览](README.md)
- [SSE 实时推送](sse.md) — WebClient + Sinks 实战
- [R2DBC 响应式数据库](r2dbc.md) — 端到端响应式
- [06 集成组件/Retry](../../06-integration/retry.md) — Resilience4j 重试
