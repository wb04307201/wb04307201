# 测试注解

> 最后更新: 2026-06-09
> ⬅️ [返回注解速查](../README.md) | [AOP 注解](aop.md)

本节介绍 Spring Test 模块的常用注解：声明测试环境、加载 Spring 上下文、激活 Profile。

---

## 🎯 一句话定位

**测试注解 = "用哪个 Spring 环境测" + "加载哪些 Bean"**——`@SpringBootTest` 启动完整 Spring 上下文，`@ActiveProfiles` 激活指定 Profile，`@MockBean` 替换真实 Bean。

---

## @SpringBootApplication 测试家族

### @RunWith

> JUnit 4 的注解，声明测试运行器。Spring 测试需要用 `SpringRunner`（Spring 提供的运行器）。

```java
@RunWith(SpringRunner.class)
@SpringBootTest
public class TestJunit {
    // 测试方法
}
```

### @SpringBootTest

> 启动完整的 Spring Boot 应用上下文进行测试（**比 @Test 慢很多**，因为要启动容器）。

```java
@ActiveProfiles("dev")
@RunWith(SpringRunner.class)
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

## 🤔 思考

1. **@SpringBootTest 启动慢怎么办？** 用 @WebMvcTest/@DataJpaTest 缩小范围，或用 `@MockBean` 替代真实依赖。
2. **为什么需要 @RunWith？** JUnit 4 要求显式声明运行器；JUnit 5 用 `@ExtendWith(SpringExtension.class)` 替代。
3. **测试要连真实数据库吗？** 推荐用 H2 in-memory 或 Testcontainers（Docker），避免污染生产数据。
4. **@MockBean 和 @Mock 区别？** `@MockBean` 替换 Spring 容器中的 Bean；`@Mock` 仅创建 Mock 对象（不放入容器）。

---

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [配置注解](configuration.md) — @Configuration、@SpringBootApplication
- [AOP 注解](aop.md) — AOP 切面也常被测试
