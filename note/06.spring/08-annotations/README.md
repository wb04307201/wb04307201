# 08 注解速查

> 最后更新: 2026-06-09
> ⬅️ [返回 Spring 顶层](../README.md)

---

## 🎯 一句话定位

**Spring 注解 = 按场景分类的速查手册**——本节是所有 Spring 注解的"分类索引"，需要时按"我在做什么"快速查找。

---

## 📚 分类索引

| 场景 | 核心注解 | 详解 |
|:-----|:---------|:----:|
| **Web 层** | `@RequestMapping` / `@RestController` / `@GetMapping` / `@PathVariable` / `@RequestParam` / `@RequestBody` / `@ResponseBody` | [web.md](web.md) |
| **Bean 与 IoC** | `@Component` / `@Service` / `@Repository` / `@Controller` / `@Autowired` / `@Resource` / `@Inject` / `@Qualifier` / `@Scope` | [bean-and-ioc.md](bean-and-ioc.md) |
| **配置** | `@Configuration` / `@Bean` / `@Value` / `@ConfigurationProperties` / `@PropertySource` / `@ImportResource` | [configuration.md](configuration.md) |
| **AOP** | `@Aspect` / `@Pointcut` / `@Before` / `@After` / `@AfterReturning` / `@AfterThrowing` / `@Around` / `@Order` | [aop.md](aop.md) |
| **异常处理** | `@ControllerAdvice` / `@ExceptionHandler` / `@ResponseStatus` | [exception.md](exception.md) |
| **测试** | `@RunWith` / `@SpringBootTest` / `@ActiveProfiles` / `@MockBean` | [test.md](test.md) |
| **条件装配** | `@Conditional` / `@ConditionalOnClass` / `@ConditionalOnMissingBean` / `@ConditionalOnProperty` | [configuration.md](configuration.md#四条件装配-spring-4) |
| **启动** | `@SpringBootApplication` / `@EnableAutoConfiguration` / `@ComponentScan` / `@EnableScheduling` / `@EnableAsync` | [configuration.md](configuration.md#二自动配置-spring-boot-核心) |
| **JPA** | `@Entity` / `@Table` / `@Id` / `@Column` / `@OneToOne` / `@OneToMany` / `@ManyToOne` | [jpa.md](jpa.md) |
| **事务** | `@Transactional` / `@EnableTransactionManagement` | [事务](../03-data/transaction/README.md) |
| **缓存** | `@Cacheable` / `@CachePut` / `@CacheEvict` / `@EnableCaching` | [缓存](../03-data/cache/README.md) |
| **校验** | `@Valid` / `@Validated` / `@NotNull` / `@Min` / `@Max` | [Validation](../06-integration/validation/annotations-and-usage.md) |
| **重试** | `@Retryable` / `@Recover` / `@EnableRetry` | [Retry](../06-integration/retry.md) |

---

## ⚡ 速查表

| 我想... | 用什么注解 | 章节 |
|:--------|:----------|:----:|
| 暴露 REST 接口 | `@RestController` + `@GetMapping`/`@PostMapping` | [Web 层](web.md) |
| 注入依赖 | `@Autowired` / `@Resource` / `@Inject` | [Bean](bean-and-ioc.md) |
| 读取配置 | `@Value` / `@ConfigurationProperties` | [配置](configuration.md) |
| 写事务方法 | `@Transactional` | [事务](../03-data/transaction/README.md) |
| 缓存方法结果 | `@Cacheable` | [缓存](../03-data/cache/README.md) |
| 自动重试 | `@Retryable` + `@Recover` | [重试](../06-integration/retry.md) |
| 全局异常处理 | `@ControllerAdvice` + `@ExceptionHandler` | [异常](exception.md) |
| 启动后执行 | `@PostConstruct` / `ApplicationRunner` | [启动](../04-spring-boot/application-bootstrap.md) |
| 写切面 | `@Aspect` + `@Before`/`@Around` | [AOP](aop.md) |
| Bean 作用域 | `@Scope("singleton")` / `"prototype"` | [Bean](bean-and-ioc.md) |
| 启用异步 | `@EnableAsync` + `@Async` | [启动](../04-spring-boot/application-bootstrap.md) |
| 启用定时任务 | `@EnableScheduling` + `@Scheduled` | [启动](../04-spring-boot/application-bootstrap.md) |
| 写 JPA 实体 | `@Entity` + `@Id` + `@Column` | [JPA](jpa.md) |
| 写测试类 | `@SpringBootTest` + `@MockBean` | [测试](test.md) |
| 条件装配 | `@ConditionalOnClass` / `@ConditionalOnProperty` | [配置](configuration.md#四条件装配-spring-4) |
| 启动 Spring Boot | `@SpringBootApplication` | [配置](configuration.md#二自动配置-spring-boot-核心) |
| 校验请求参数 | `@Valid` + `@NotNull` + `@Min`/`@Max` | [Validation](../06-integration/validation/annotations-and-usage.md) |

---

## 🤝 注解之间的协作关系

```mermaid
graph LR
    Boot[启动类<br/>@SpringBootApplication] --> Scan[@ComponentScan<br/>扫描 Bean]
    Boot --> Auto[启用自动配置<br/>@EnableAutoConfiguration]
    Boot --> Config[声明配置类<br/>@Configuration]

    Scan --> Comp[@Component<br/>@Service @Repository @Controller]
    Auto --> Cond[@Conditional 家族]
    Cond --> BeanDef[@Bean 定义]

    Comp --> DI[@Autowired @Resource]
    DI --> AOP[@Aspect @Around]
    AOP --> Tx[@Transactional]

    Comp --> Web[@RestController @RequestMapping]
    Web --> Validate[@Valid]
    Web --> ExHandle[@ControllerAdvice<br/>@ExceptionHandler]

    Comp --> Cache[@Cacheable]
    Comp --> Retry[@Retryable]
```

---

## 🤔 思考

1. **@Component vs @Service vs @Repository vs @Controller？** 业务语义不同（通用/服务/数据访问/控制层），但功能上等价，Spring 会以同样的方式扫描。
2. **@Autowired vs @Resource？** @Autowired 按类型（Spring），@Resource 按名称（JDK）。
3. **@Configuration vs @Bean？** @Configuration 标记类，@Bean 标记方法（方法返回值注册为 Bean）。
4. **@RestController vs @Controller？** @RestController = @Controller + @ResponseBody（所有方法默认返回 JSON）。
5. **什么时候用 @Aspect 不用 @Bean？** 自己的切面类用 @Aspect + @Component（自动扫描）；第三方库的切面用 @Configuration + @Bean 显式注册。

---

## 📂 文件清单

| 文件 | 内容 | 状态 |
|:-----|:-----|:----:|
| [web.md](web.md) | Spring MVC 注解（@RestController、@RequestMapping、参数绑定） | ✅ |
| [bean-and-ioc.md](bean-and-ioc.md) | Bean 声明/注入/作用域（@Component 家族、@Autowired、@Scope） | ✅ |
| [configuration.md](configuration.md) | 配置/条件装配/外部化配置（@Configuration、@Conditional、@Value） | ✅ |
| [aop.md](aop.md) | AOP 注解（@Aspect、@Pointcut、5 种通知） | ✅ |
| [exception.md](exception.md) | 异常处理（@ControllerAdvice、@ExceptionHandler） | ✅ |
| [test.md](test.md) | 测试注解（@SpringBootTest、@MockBean、@ActiveProfiles） | ✅ |
| [jpa.md](jpa.md) | JPA 注解（@Entity、@Table、@Id、关联关系） | ✅ |

---

## 相关章节

- ⬅️ [返回 Spring 顶层](../README.md)
- [01 核心容器](../01-core/README.md) — Bean 相关注解
- [02 Web 层](../02-web/README.md) — MVC/WebFlux 相关注解
- [03 数据层](../03-data/README.md) — 事务/缓存相关注解
- [06 集成组件](../06-integration/README.md) — Validation/Retry/StateMachine 相关注解
