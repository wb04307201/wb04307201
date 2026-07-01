# 测试注解

> ⬅️ [返回注解速查](../README.md) | [AOP 注解](aop.md)

本节介绍 Spring Test 模块的常用注解：声明测试环境、加载 Spring 上下文、激活 Profile。

---

## 🎯 一句话定位

**测试注解 = "用哪个 Spring 环境测" + "加载哪些 Bean"**——`@SpringBootTest` 启动完整 Spring 上下文，`@ActiveProfiles` 激活指定 Profile，`@MockBean` 替换真实 Bean。

---

## @SpringBootApplication 测试家族

### @ExtendWith（JUnit 5，替代 @RunWith）

> JUnit 5 的注解，声明测试扩展。Spring 测试需要用 `SpringExtension`（Spring 提供的扩展）。
>
> 📌 JUnit 4 的 `@RunWith(SpringRunner.class)` 已被替代，**Spring Boot 3.x 推荐 JUnit 5**。

```java
@ExtendWith(SpringExtension.class)
@SpringBootTest
public class TestJunit {
    // 测试方法
}
```

### @SpringBootTest

> 启动完整的 Spring Boot 应用上下文进行测试（**比 @Test 慢很多**，因为要启动容器）。

```java
@ActiveProfiles("dev")
@ExtendWith(SpringExtension.class)
@SpringBootTest
public class TestJunit {

    @Test
    public void executeTask() {
        // 测试...
    }
}
```

### @ActiveProfiles

> 一般作用于测试类上，声明生效的 Spring 配置文件，如指定 `application-dev.properties`。

```java
@ActiveProfiles("dev")
@SpringBootTest
public class TestJunit { ... }
```

---

## 4 种测试粒度

| 注解 | 加载范围 | 速度 | 适用场景 |
|------|---------|------|----------|
| **@SpringBootTest** | 完整 ApplicationContext | 慢（秒级） | 集成测试、Controller 集成 |
| **@WebMvcTest** | 仅 Web 层（Controller、Filter 等） | 中 | Controller 单元测试 |
| **@DataJpaTest** | 仅 JPA 组件 | 中 | Repository 单元测试 |
| **（无注解）** | 无 Spring 容器 | 快（毫秒级） | 纯 Java 单元测试 |

---

## 常见模式

### 1. 完整集成测试

```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testGetUser() throws Exception {
        mockMvc.perform(get("/users/1"))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("Alice"));
    }
}
```

### 2. 替换依赖（@MockBean）

```java
@SpringBootTest
class OrderServiceTest {

    @MockBean
    private PaymentService paymentService;  // 替换为 Mock

    @Autowired
    private OrderService orderService;

    @Test
    void testCreateOrder() {
        when(paymentService.pay(any())).thenReturn(true);
        // 测试
    }
}
```

### 3. 多环境测试

```java
@ActiveProfiles("test")
@SpringBootTest
@TestPropertySource(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb",
    "logging.level.root=DEBUG"
})
class TestWithCustomProps { ... }
```

---

## 切片测试与高级注解

> 本节介绍**测试范围裁剪**、**Mock 替换**和**Web/MVC 测试**相关注解。

### @TestConfiguration（测试专用配置）

> 在测试中**临时注册 Bean**，不影响主应用配置。类级别 `@Configuration` 同理。

```java
@SpringBootTest
class UserServiceTest {

    @TestConfiguration
    static class TestConfig {
        @Bean
        public MailService mockMailService() {
            return new MockMailService();       // 测试专用实现
        }
    }
}
```

### 切片测试家族（Spring Boot Test Slicing）

> 只加载**特定层**的 Bean，启动更快。

| 注解 | 加载范围 | 速度 | 典型场景 |
|:-----|:---------|:-----|:---------|
| `@SpringBootTest` | 完整 ApplicationContext | 慢（秒级） | 集成测试 |
| `@WebMvcTest(ControllerXxx.class)` | 仅 MVC（Controller + Filter + ControllerAdvice） | 快（百毫秒） | Controller 单元测试 |
| `@WebFluxTest` | 仅 WebFlux | 快 | WebFlux 单元测试 |
| `@DataJpaTest` | JPA + Repository + H2 in-memory DB | 中 | Repository 测试 |
| `@JdbcTest` | JDBC 基础设施 | 中 | JdbcTemplate 测试 |
| `@DataMongoTest` | MongoDB | 中 | MongoDB Repository |
| `@JsonTest` | Jackson 序列化 | 极快 | JSON 序列化验证 |
| `@RestClientTest` | RestTemplate / WebClient | 快 | HTTP 客户端测试 |
| `@DataRedisTest` | Redis | 中 | Redis 集成测试 |

```java
@WebMvcTest(UserController.class)        // 只加载 UserController，不加载 Service / Repo
class UserControllerTest {

    @Autowired private MockMvc mockMvc;
    @MockBean  private UserService userService;     // 替换依赖

    @Test
    void getUser() throws Exception {
        when(userService.findById(1L)).thenReturn(new User(1L, "Alice"));

        mockMvc.perform(get("/users/1"))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("Alice"));
    }
}
```

### @AutoConfigureMockMvc / @AutoConfigureWebTestClient

> 在 `@SpringBootTest` 中**追加** Web 测试能力（默认不自动配置）。

```java
@SpringBootTest
@AutoConfigureMockMvc           // 注入 MockMvc（不启动真实端口）
class WebTest {
    @Autowired private MockMvc mockMvc;
}

@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient     // 注入 WebTestClient（真实 HTTP）
class WebClientTest {
    @Autowired private WebTestClient webClient;
}
```

| 注解 | 客户端 | 是否真实端口 |
|:-----|:-------|:-------------|
| `@AutoConfigureMockMvc` | `MockMvc` | 否（直接调 Servlet） |
| `@AutoConfigureWebTestClient` | `WebTestClient` | **是**（真实 HTTP） |

### @MockBean vs @Mock vs @SpyBean

| 维度 | @MockBean | @Mock | @SpyBean |
|:-----|:----------|:------|:---------|
| **来源** | Spring Boot Test | Mockito | Spring Boot Test |
| **加入容器** | ✅ 替换容器中的 Bean | ❌ 仅本地对象 | ✅ 替换容器中的 Bean |
| **行为** | **全部 Mock**（无真实逻辑） | **全部 Mock** | **部分 Mock**（真实逻辑 + 桩特定方法） |
| **被 @Autowired 注入** | ✅ | ❌ | ✅ |
| **典型场景** | 替换慢依赖、第三方服务 | 单元测试中临时创建 | 只想改某几个方法、保留其他逻辑 |

```java
// @MockBean：完全 Mock
@MockBean
private PaymentService paymentService;
when(paymentService.pay(any())).thenReturn(true);

// @SpyBean：保留真实行为，可选择性 stub
@SpyBean
private OrderService orderService;
doReturn(mockResult).when(orderService).complexMethod(any());   // 仅这一方法 Mock
```

> ⚠️ Spring Boot 3.4+ 推荐改用 Spring Framework 6.2 引入的 `@MockitoBean` / `@MockitoSpyBean`（与 Mockito 5 集成更紧密）。

---

## 🤔 思考

1. **@SpringBootTest 启动慢怎么办？** 用 @WebMvcTest/@DataJpaTest 缩小范围，或用 `@MockBean` 替代真实依赖。
2. **为什么需要 @ExtendWith？** JUnit 5 通过扩展机制集成 Spring 上下文（`@ExtendWith(SpringExtension.class)`），JUnit 4 用 `@RunWith(SpringRunner.class)`，**Spring Boot 3.x 默认 JUnit 5**。
3. **测试要连真实数据库吗？** 推荐用 H2 in-memory 或 Testcontainers（Docker），避免污染生产数据。
4. **@MockBean 和 @Mock 区别？** `@MockBean` 替换 Spring 容器中的 Bean；`@Mock` 仅创建 Mock 对象（不放入容器）。
5. **@WebMvcTest vs @SpringBootTest + @AutoConfigureMockMvc？** 前者**只加载** Web 层（轻量、推荐），后者**加载全部** Bean 再追加 MockMvc（重）。优先切片。

---

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [配置注解](configuration.md) — @Configuration、@SpringBootApplication
- [AOP 注解](aop.md) — AOP 切面也常被测试
