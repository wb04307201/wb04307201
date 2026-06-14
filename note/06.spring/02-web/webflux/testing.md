# WebFlux 测试

> 最后更新: 2026-06-14
> ⬅️ [返回 WebFlux 总览](README.md) | [02 Web 层](../README.md)

WebFlux 应用有两类主流测试方式：**`WebTestClient`（全栈/集成）** + **`@WebFluxTest`（切片）**。`WebTestClient` 是不起容器的 HTTP 客户端模拟器，可以无缝对接 `RouterFunction`、注解式 Controller、`WebHandler` 任意一种。

---

## 🎯 一句话定位

**WebFlux 测试 = "用 WebTestClient 直接打路由器/Controller，不起 Tomcat/Netty"**——既保留真实 HTTP 语义（Header、Body、状态码），又具备单元测试的速度与隔离性。

---

## 一、依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
<!-- WebTestClient 自带于 spring-test（Spring Framework） -->
```

---

## 二、WebTestClient 三种绑定方式

### 1. 绑定到 RouterFunction（最快）

```java
@Test
void listUsers() {
    WebTestClient.bindToRouterFunction(routes(new UserHandler(repoMock)))
            .build()
            .get().uri("/users")
            .exchange()
            .expectStatus().isOk()
            .expectBodyList(User.class).hasSize(3);
}
```

### 2. 绑定到 ApplicationContext（推荐：与 Spring 集成）

```java
@SpringBootTest
class UserControllerIT {

    @Autowired
    private ApplicationContext ctx;

    private WebTestClient client;

    @BeforeEach
    void setUp() {
        client = WebTestClient.bindToApplicationContext(ctx).build();
    }

    @Test
    void get() {
        client.get().uri("/users/1")
              .exchange()
              .expectStatus().isOk()
              .expectBody()
              .jsonPath("$.name").isEqualTo("Alice");
    }
}
```

### 3. 绑定到真实 Controller（注解式）

```java
WebTestClient.bindToController(new UserController(repo))
        .build()
        .get().uri("/users")
        .exchange()
        .expectStatus().isOk();
```

---

## 三、@WebFluxTest 切片测试

```java
@WebFluxTest(UserController.class)  // 只加载该 Controller + WebFlux 基础设施
class UserControllerTest {

    @Autowired
    private WebTestClient client;

    @MockBean
    private UserRepository repo;

    @Test
    void getById() {
        when(repo.findById(1L)).thenReturn(Mono.just(new User(1L, "Alice")));

        client.get().uri("/users/1")
              .exchange()
              .expectStatus().isOk()
              .expectBody(User.class).isEqualTo(new User(1L, "Alice"));
    }

    @Test
    void notFound() {
        when(repo.findById(99L)).thenReturn(Mono.empty());

        client.get().uri("/users/99")
              .exchange()
              .expectStatus().isNotFound();
    }
}
```

> `@WebFluxTest` 默认**不加载** `Service` / `Repository` / `@Configuration`，需要 `@MockBean` 显式打桩。
> 字段注入 `WebTestClient` 由 Spring Boot 自动配置；也可以 `@Autowired ApplicationContext` 自己 build。

---

## 四、流式（SSE）端到端测试

```java
@Test
void sseStream() {
    Flux<Message> msgs = Flux.just(msg("a"), msg("b"), msg("c"));

    client.get().uri("/messages/stream")
          .accept(MediaType.TEXT_EVENT_STREAM)
          .exchange()
          .expectStatus().isOk()
          .returnResult(Message.class)
          .getResponseBody()
          .as(StepVerifier::create)
          .expectNext(msg("a"))
          .expectNext(msg("b"))
          .expectNext(msg("c"))
          .verifyComplete();
}
```

> 配合 Reactor `StepVerifier`，可对 `Flux<T>` 做严格按序断言。

---

## 五、JSON 断言技巧

```java
client.post().uri("/users")
      .contentType(MediaType.APPLICATION_JSON)
      .bodyValue(new UserReq("Alice", "a@x.com"))
      .exchange()
      .expectStatus().isCreated()
      .expectHeader().exists("Location")
      .expectBody()
      .jsonPath("$.id").isNumber()
      .jsonPath("$.name").isEqualTo("Alice");
```

也可以 `.expectBody(User.class).isEqualTo(expected)` 直接反序列化为对象比对（注意类型与字段严格匹配）。

---

## 六、测试常见问题

1. **如何模拟错误**：`when(repo.findById(1L)).thenReturn(Mono.error(new BizException("X")))`，再断言 `.expectStatus().is5xxServerError()`。
2. **如何验证拦截器**：`WebTestClient` 默认会执行注册的 `WebFilter` / `HandlerFilterFunction`，**断言副作用**（如 Logger、Metrics）即可。
3. **如何测 SSE 长连接超时**：用 `StepVerifier.create(...).thenAwait(Duration.ofSeconds(2))`，可验证连接保持时长。
4. **CORS 头测试**：用 `.header("Origin", "https://x.com").exchange()`，再断言响应 `Access-Control-Allow-Origin`。
5. **不引入 spring-boot-starter-test 怎么用**：仅需 `spring-test` + `reactor-test`，可独立引入。

---

## 相关章节

- ⬅️ [WebFlux 总览](README.md)
- [SSE 实时推送](sse.md) — SSE 端到端测试
- [Router Functions](router-functions.md) — 路由绑定测试
- [08 注解速查/测试](../../08-annotations/test.md) — @MockBean、@WebFluxTest 全注解
