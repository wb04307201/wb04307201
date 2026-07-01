<!--
module:
  parent: spring
  slug: spring/annotations
  type: article
  category: 主模块子文章
  summary: Spring 注解速查：事务/缓存/调度/校验/重试/AOP/Web 等场景分类索引。
-->

# 08 注解速查

> 最后更新: 2026-06-14
> ⬅️ [返回 Spring 顶层](../README.md)

---
## 引言：反直觉代码

08 注解速查 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 🎯 一句话定位

**Spring 注解 = 按场景分类的速查手册**——本节是所有 Spring 注解的"分类索引"，需要时按"我在做什么"快速查找。

---

## 📚 分类索引

| 场景 | 核心注解 | 详解 |
|:-----|:---------|:----:|
| **Web 层** | `@RequestMapping` / `@RestController` / `@GetMapping` / `@PathVariable` / `@RequestParam` / `@RequestBody` / `@ResponseBody` | [web.md](web.md) |
| **Web 高级** | `@CrossOrigin` / `@RequestHeader` / `@CookieValue` / `@MatrixVariable` / `@ModelAttribute` / `@SessionAttribute` | [web.md#跨域与请求映射细节](web.md) |
| **Bean 与 IoC** | `@Component` / `@Service` / `@Repository` / `@Controller` / `@Autowired` / `@Resource` / `@Inject` / `@Qualifier` / `@Scope` | [bean-and-ioc.md](bean-and-ioc.md) |
| **Bean 注入语义** | `@Lazy` / `@Primary` / `@DependsOn` / `@Order` / `@Priority` | [bean-and-ioc.md#五bean-注入语义注解](bean-and-ioc.md) |
| **配置** | `@Configuration` / `@Bean` / `@Value` / `@ConfigurationProperties` / `@PropertySource` / `@ImportResource` | [configuration.md](configuration.md) |
| **多环境** | `@Profile` / `application-{profile}.yml` / `spring.profiles.active` | [configuration.md#七profile-与环境隔离](configuration.md) |
| **AOP** | `@Aspect` / `@Pointcut` / `@Before` / `@After` / `@AfterReturning` / `@AfterThrowing` / `@Around` / `@Order` | [aop.md](aop.md) |
| **异常处理** | `@ControllerAdvice` / `@ExceptionHandler` / `@ResponseStatus` | [exception.md](exception.md) |
| **测试** | `@ExtendWith` / `@SpringBootTest` / `@ActiveProfiles` / `@MockBean` | [test.md](test.md) |
| **切片测试** | `@TestConfiguration` / `@WebMvcTest` / `@DataJpaTest` / `@AutoConfigureMockMvc` / `@SpyBean` | [test.md#切片测试与高级注解](test.md) |
| **条件装配** | `@Conditional` / `@ConditionalOnClass` / `@ConditionalOnMissingBean` / `@ConditionalOnProperty` | [configuration.md#四条件装配-spring-4](configuration.md) |
| **启动** | `@SpringBootApplication` / `@EnableAutoConfiguration` / `@ComponentScan` / `@EnableScheduling` / `@EnableAsync` | [configuration.md#二自动配置-spring-boot-核心](configuration.md) |
| **JPA 基础** | `@Entity` / `@Table` / `@Id` / `@Column` / `@OneToOne` / `@OneToMany` / `@ManyToOne` | [jpa.md](jpa.md) |
| **JPA 高级** | `@MappedSuperclass` / `@Inheritance` / `@Embeddable` / `@Convert` / `@Version` / `@Lock` | [jpa.md#高级映射与查询注解](jpa.md) |
| **事务** | `@Transactional` / `@EnableTransactionManagement` | [transaction.md](transaction.md) |
| **缓存** | `@Cacheable` / `@CachePut` / `@CacheEvict` / `@Caching` / `@CacheConfig` / `@EnableCaching` | [cache.md](cache.md) |
| **调度与异步** | `@Scheduled` / `@Async` / `@EnableScheduling` / `@EnableAsync` | [scheduling-and-async.md](scheduling-and-async.md) |
| **校验** | `@Valid` / `@Validated` / `@NotNull` / `@NotBlank` / `@Email` / `@Size` / `@Pattern` | [validation.md](validation.md) |
| **重试** | `@Retryable` / `@Recover` / `@Backoff` / `@EnableRetry` | [retry.md](retry.md) |

---

## ⚡ 速查表

| 我想... | 用什么注解 | 章节 |
|:--------|:----------|:----:|
| 暴露 REST 接口 | `@RestController` + `@GetMapping`/`@PostMapping` | [Web 层](web.md) |
| 注入依赖 | `@Autowired` / `@Resource` / `@Inject` | [Bean](bean-and-ioc.md) |
| 读取配置 | `@Value` / `@ConfigurationProperties` | [配置](configuration.md) |
| 多环境切换 | `@Profile` + `application-{profile}.yml` | [Profile](configuration.md#七profile-与环境隔离) |
| 写事务方法 | `@Transactional` | [事务](transaction.md) |
| 缓存方法结果 | `@Cacheable` | [缓存](cache.md) |
| 自动重试 | `@Retryable` + `@Recover` | [重试](retry.md) |
| 全局异常处理 | `@ControllerAdvice` + `@ExceptionHandler` | [异常](exception.md) |
| 启动后执行 | `@PostConstruct` / `ApplicationRunner` | [启动](../04-spring-boot/application-bootstrap.md) |
| 写切面 | `@Aspect` + `@Before`/`@Around` | [AOP](aop.md) |
| Bean 作用域 | `@Scope("singleton")` / `"prototype"` | [Bean](bean-and-ioc.md) |
| 启用异步 | `@EnableAsync` + `@Async` | [异步](scheduling-and-async.md) |
| 启用定时任务 | `@EnableScheduling` + `@Scheduled` | [调度](scheduling-and-async.md) |
| 写 JPA 实体 | `@Entity` + `@Id` + `@Column` | [JPA](jpa.md) |
| 写 JPA 继承/嵌入 | `@MappedSuperclass` / `@Embedded` / `@Inheritance` | [JPA 高级](jpa.md#高级映射与查询注解) |
| 写测试类 | `@SpringBootTest` + `@MockBean` | [测试](test.md) |
| 切片测试 | `@WebMvcTest` / `@DataJpaTest` | [切片测试](test.md#切片测试与高级注解) |
| 条件装配 | `@ConditionalOnClass` / `@ConditionalOnProperty` | [配置](configuration.md#四条件装配-spring-4) |
| 启动 Spring Boot | `@SpringBootApplication` | [配置](configuration.md#二自动配置-spring-boot-核心) |
| 校验请求参数 | `@Valid` + `@NotNull` + `@Min`/`@Max` | [Validation](validation.md) |
| 跨域 | `@CrossOrigin` / `WebMvcConfigurer` | [Web](web.md#跨域与请求映射细节) |
| 多实现类优先选择 | `@Primary` | [Bean](bean-and-ioc.md#五bean-注入语义注解) |
| 乐观锁 | `@Version` | [JPA](jpa.md#高级映射与查询注解) |
| 悲观锁 | `@Lock` | [JPA](jpa.md#高级映射与查询注解) |

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
    Web --> Cors[@CrossOrigin]
    Web --> Validate[@Valid @Validated]
    Web --> ExHandle[@ControllerAdvice<br/>@ExceptionHandler]

    Comp --> Cache[@Cacheable @CachePut @CacheEvict]
    Comp --> Retry[@Retryable @Recover]
    Comp --> Sched[@Scheduled @Async]

    DI --> Primary[@Primary @Qualifier]
    DI --> Lazy[@Lazy @DependsOn @Order]
```

---

## 🤔 思考

1. **@Component vs @Service vs @Repository vs @Controller？** 业务语义不同（通用/服务/数据访问/控制层），但功能上等价，Spring 会以同样的方式扫描。
2. **@Autowired vs @Resource？** @Autowired 按类型（Spring），@Resource 按名称（JDK）。
3. **@Configuration vs @Bean？** @Configuration 标记类，@Bean 标记方法（方法返回值注册为 Bean）。
4. **@RestController vs @Controller？** @RestController = @Controller + @ResponseBody（所有方法默认返回 JSON）。
5. **什么时候用 @Aspect 不用 @Bean？** 自己的切面类用 @Aspect + @Component（自动扫描）；第三方库的切面用 @Configuration + @Bean 显式注册。
6. **@Cacheable、@Transactional、@Async 都有 self-invocation 问题？** 是的——三者都基于 AOP 代理，**内部 this.xxx() 调用绕过代理**。统一解法：拆 Bean 或注入自己（`@Lazy`）。

---

## 📂 文件清单

| 文件 | 内容 | 状态 |
|:-----|:-----|:----:|
| [web.md](web.md) | Spring MVC 注解（@RestController、@RequestMapping、@CrossOrigin、参数绑定） | ✅ |
| [bean-and-ioc.md](bean-and-ioc.md) | Bean 声明/注入/作用域/注入语义（@Lazy/@Primary/@Order） | ✅ |
| [configuration.md](configuration.md) | 配置/条件装配/外部化配置/Profile（@Configuration、@Conditional、@Profile） | ✅ |
| [aop.md](aop.md) | AOP 注解（@Aspect、@Pointcut、5 种通知） | ✅ |
| [exception.md](exception.md) | 异常处理（@ControllerAdvice、@ExceptionHandler） | ✅ |
| [test.md](test.md) | 测试注解（@SpringBootTest、@MockBean、切片测试） | ✅ |
| [jpa.md](jpa.md) | JPA 注解（@Entity、@Table、@Id、关联关系 + 高级映射/锁） | ✅ |
| [transaction.md](transaction.md) | 事务注解（@Transactional 7 传播 / 4 隔离 / 失效场景） | ✅ |
| [cache.md](cache.md) | 缓存注解（@Cacheable/@CachePut/@CacheEvict + SpEL） | ✅ |
| [scheduling-and-async.md](scheduling-and-async.md) | 调度与异步（@Scheduled cron / @Async / 线程池） | ✅ |
| [validation.md](validation.md) | 校验注解（@Valid/@Validated + JSR-303 约束） | ✅ |
| [retry.md](retry.md) | 重试注解（@Retryable/@Recover/@Backoff） | ✅ |

---

## 相关章节

- ⬅️ [返回 Spring 顶层](../README.md)
- [01 核心容器](../01-core/README.md) — Bean 相关注解
- [02 Web 层](../02-web/README.md) — MVC/WebFlux 相关注解
- [03 数据层](../03-data/README.md) — 事务/缓存相关注解
- [06 集成组件](../06-integration/README.md) — Validation/Retry/StateMachine 相关注解
- [13 辨析/为什么不推荐 @Autowired 字段注入](../../13.split-hairs/06.spring/not-use-@autowired/README.md) — 字段注入 vs 构造器注入
- [13 辨析/PO-VO-DTO-BO-DAO-POJO 语义辨析](../../13.split-hairs/06.spring/clarify-various-o/README.md) — 各层对象语义
