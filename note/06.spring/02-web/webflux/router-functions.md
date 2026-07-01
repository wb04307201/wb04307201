# Router Functions 函数式端点

> ⬅️ [返回 WebFlux 总览](README.md) | [02 Web 层](../README.md)

**Router Functions** 是 WebFlux 提供的**函数式、类型安全**的端点声明方式，用 `RouterFunction<ServerResponse>` 与 `HandlerFunction<ServerResponse>` 替代 `@RestController` 注解。核心价值：**可组合、可测试、便于做轻量网关/路由层**。

---

## 🎯 一句话定位

**Router Functions = "用 DSL 拼装路由表"**——把"什么 URL 走什么处理函数"以类型安全的方式表达，可被 `and`/`andRoute`/`andOther` 自由组合，非常适合做 BFF 聚合层或边缘网关。

---

## 一、Hello World

```java
// 1) Handler：纯函数，输入请求，返回 ServerResponse
HandlerFunction<ServerResponse> hello = request ->
        ServerResponse.ok().bodyValue("Hello, " + request.pathVariable("name"));

// 2) Router：URL 模板 → Handler
RouterFunction<ServerResponse> route = RouterFunctions.route()
        .GET("/hello/{name}", hello)
        .build();

// 3) 注册到 WebFlux 配置
@Bean
public RouterFunction<ServerResponse> routes(UserHandler userHandler) {
    return RouterFunctions.route()
            .GET("/users",            userHandler::list)
            .GET("/users/{id}",       userHandler::get)
            .POST("/users",           userHandler::create)
            .PUT("/users/{id}",       userHandler::update)
            .DELETE("/users/{id}",    userHandler::delete)
            .build();
}
```

> Handler 推荐拆成独立 Bean（如 `UserHandler`），方法签名保持 `ServerRequest → Mono<ServerResponse>`。

---

## 二、HandlerFunction 写法

```java
@Component
public class UserHandler {
    private final UserRepository repo;

    public UserHandler(UserRepository repo) { this.repo = repo; }

    public Mono<ServerResponse> list(ServerRequest req) {
        return ServerResponse.ok().body(repo.findAll(), User.class);
    }

    public Mono<ServerResponse> get(ServerRequest req) {
        Long id = Long.valueOf(req.pathVariable("id"));
        return repo.findById(id)
                .flatMap(u -> ServerResponse.ok().bodyValue(u))
                .switchIfEmpty(ServerResponse.notFound().build());
    }

    public Mono<ServerResponse> create(ServerRequest req) {
        return req.bodyToMono(User.class)
                .flatMap(repo::save)
                .flatMap(u -> ServerResponse.created(URI.create("/users/" + u.getId())).bodyValue(u));
    }
}
```

| ServerResponse 工厂 | 用途 |
|--------------------|------|
| `ok().bodyValue(x)` | 200 + JSON |
| `created(uri)` | 201 + Location 头 |
| `noContent()` | 204 |
| `badRequest().bodyValue(err)` | 400 + 错误体 |
| `notFound().build()` | 404 |
| `status(HttpStatus.UNAUTHORIZED).build()` | 自定义状态码 |

---

## 三、路由组合 DSL

```java
RouterFunction<ServerResponse> apiRoutes() {
    return route(GET("/api/v1/users"),       userHandler::list)
            .andRoute(GET("/api/v1/users/{id}"), userHandler::get)
            .andRoute(POST("/api/v1/users"),      userHandler::create)
            .and(otherRoute()); // 多个 RouterFunction 组合
}

RouterFunction<ServerResponse> actuatorRoutes() {
    return route(GET("/health"),  r -> ok().bodyValue("UP"))
            .andRoute(GET("/ready"), r -> ok().bodyValue("READY"));
}

@Bean
public RouterFunction<ServerResponse> composedRoutes() {
    return apiRoutes().and(actuatorRoutes());
}
```

### 谓词：method + path + header

```java
RouterFunction<ServerResponse> versioned = route()
        .GET(accept(MediaType.APPLICATION_JSON).and(path("/v2/*")),
             r -> ServerResponse.ok().bodyValue("v2"))
        .build();
```

可组合的谓词：`method`、`path`、`accept`、`contentType`、`header`、`queryParam`、`before`/`after`/`onError` 过滤器。

---

## 四、过滤器：before / after / filter

```java
RouterFunction<ServerResponse> withFilter = route()
        .GET("/api/users", userHandler::list)
        .before(req -> {
            long t0 = System.currentTimeMillis();
            req.attributes().put("t0", t0);
            return req;
        })
        .after((req, resp) -> {
            long t0 = (long) req.attributes().get("t0");
            log.info("cost={}ms", System.currentTimeMillis() - t0);
            return resp;
        })
        .build();

// 或 HandlerFilterFunction：可短路
HandlerFilterFunction<ServerResponse, ServerResponse> auth = (req, next) -> {
    String token = req.headers().firstHeader("Authorization");
    if (token == null) return ServerResponse.status(401).build();
    return next.handle(req);
};
```

---

## 五、与 @RestController 对比

| 维度 | 注解式（`@RestController`） | Router Functions |
|------|---------------------------|------------------|
| **声明方式** | 注解 + 方法签名 | 函数引用 + DSL |
| **路由可见性** | 分散在类/方法上 | 集中在一处 `RouterFunction` |
| **类型安全** | 编译期只校验方法签名 | URL 模板编译期校验 |
| **可组合性** | 低（用 `@RequestMapping` 拼接） | 高（`and` / `andRoute`） |
| **测试** | `MockMvc` / `WebTestClient` | 直接 `routerFunction(...).exchange(req)` |
| **AOP / 拦截器** | `@Around` / `WebFilter` | `HandlerFilterFunction` / `WebFilter` |
| **适合场景** | 业务 Controller（多方法、多动作） | 简单聚合层、BFF、轻网关、Actuator 自定义 |
| **学习成本** | 低 | 中 |

> **实战分工**：业务 CRUD 用 `@RestController`；跨服务聚合 / 网关层 / 边缘路由用 `RouterFunction`。

---

## 六、测试优势

```java
@Test
void listUsers() {
    WebTestClient.bindToRouterFunction(routes(userHandler))
            .build()
            .get().uri("/users")
            .exchange()
            .expectStatus().isOk()
            .expectBodyList(User.class).hasSize(3);
}
```

不需要起容器、不需要 `@WebMvcTest`/`@WebFluxTest`，**纯函数组合**直接测。

详见 [WebFlux 测试](testing.md)。

---

## 七、常见问题

1. **路由冲突**：先注册者优先生效；建议用 `@Order` 或集中一处装配。
2. **和注解式混用**：可以共存（`RouterFunctionMapping` + `RequestMappingHandlerMapping`），但风格不一致会增加维护成本。
3. **Handler 注入**：Handler 仍可以是 `@Component`，由 Spring 注入依赖。
4. **路径变量解析**：`req.pathVariable("id")` 强类型；缺值会抛 `IllegalArgumentException`，需在 `before` 阶段预校验。

---

## 相关章节

- ⬅️ [WebFlux 总览](README.md)
- [SSE 实时推送](sse.md) — RouterFunction + SSE 实战
- [WebFlux 测试](testing.md) — `WebTestClient.bindToRouterFunction`
- [MVC 总览](../mvc/README.md) — 注解式 MVC 对照
