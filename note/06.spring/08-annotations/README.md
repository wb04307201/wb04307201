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
| **Web 层** | `@RequestMapping` / `@RestController` / `@GetMapping` / `@PathVariable` / `@RequestParam` / `@RequestBody` / `@ResponseBody` | ⭐待拆分 (P2) |
| **Bean 与 IoC** | `@Component` / `@Service` / `@Repository` / `@Controller` / `@Autowired` / `@Resource` / `@Inject` / `@Qualifier` / `@Scope` | ⭐待拆分 (P2) |
| **配置** | `@Configuration` / `@Bean` / `@Value` / `@ConfigurationProperties` / `@PropertySource` / `@ImportResource` | ⭐待拆分 (P2) |
| **AOP** | `@Aspect` / `@Pointcut` / `@Before` / `@After` / `@AfterReturning` / `@AfterThrowing` / `@Around` / `@Order` | ⭐待拆分 (P2) |
| **异常处理** | `@ControllerAdvice` / `@ExceptionHandler` / `@ResponseStatus` | ⭐待拆分 (P2) |
| **测试** | `@RunWith` / `@SpringBootTest` / `@ActiveProfiles` / `@MockBean` | ⭐待拆分 (P2) |
| **条件装配** | `@Conditional` / `@ConditionalOnClass` / `@ConditionalOnMissingBean` / `@ConditionalOnProperty` | ⭐待拆分 (P2) |
| **启动** | `@SpringBootApplication` / `@EnableAutoConfiguration` / `@ComponentScan` / `@EnableScheduling` / `@EnableAsync` | ⭐待拆分 (P2) |

> 📦 **完整注解清单**（含详细说明）见 [legacy-full-reference.md](legacy-full-reference.md)（P2 阶段会按场景拆分）

---

## ⚡ 速查表

| 我想... | 用什么注解 | 章节 |
|:--------|:----------|:----:|
| 暴露 REST 接口 | `@RestController` + `@GetMapping`/`@PostMapping` | [Web 层](legacy-full-reference.md#springmvc相关注解) |
| 注入依赖 | `@Autowired` / `@Resource` / `@Inject` | [Bean](legacy-full-reference.md#bean相关注解) |
| 读取配置 | `@Value` / `@ConfigurationProperties` | [配置](legacy-full-reference.md#配置相关注解) |
| 写事务方法 | `@Transactional` | [事务](../03-data/transaction/README.md) |
| 缓存方法结果 | `@Cacheable` | [缓存](../03-data/cache/README.md) |
| 自动重试 | `@Retryable` + `@Recover` | [重试](../06-integration/retry.md) |
| 全局异常处理 | `@ControllerAdvice` + `@ExceptionHandler` | [异常](legacy-full-reference.md#异常处理相关注解) |
| 启动后执行 | `@PostConstruct` / `ApplicationRunner` | [启动](../04-spring-boot/application-bootstrap.md) |
| 写切面 | `@Aspect` + `@Before`/`@Around` | [AOP](../01-core/aop/README.md) |
| Bean 作用域 | `@Scope("singleton")` / `"prototype"` | [Bean](legacy-full-reference.md#bean相关注解) |
| 启用异步 | `@EnableAsync` + `@Async` | [启动](../04-spring-boot/application-bootstrap.md) |
| 启用定时任务 | `@EnableScheduling` + `@Scheduled` | 待补充 |

---

## 🤔 思考

1. **@Component vs @Service vs @Repository vs @Controller？** 业务语义不同（通用/服务/数据访问/控制层），但功能上等价，Spring 会以同样的方式扫描。
2. **@Autowired vs @Resource？** @Autowired 按类型（Spring），@Resource 按名称（JDK）。
3. **@Configuration vs @Bean？** @Configuration 标记类，@Bean 标记方法（方法返回值注册为 Bean）。
4. **@RestController vs @Controller？** @RestController = @Controller + @ResponseBody（所有方法默认返回 JSON）。

---

## 相关章节

- ⬅️ [返回 Spring 顶层](../README.md)
- [legacy-full-reference.md](legacy-full-reference.md) — 完整注解清单（P2 会按场景拆分为 7 个文件）
- [01 核心容器](../01-core/README.md) — Bean 相关注解
- [02 Web 层](../02-web/README.md) — MVC/WebFlux 相关注解
- [03 数据层](../03-data/README.md) — 事务/缓存相关注解
- [06 集成组件](../06-integration/README.md) — Validation/Retry/StateMachine 相关注解

---

> 🔍 需要完整注解说明？查看 [legacy-full-reference.md](legacy-full-reference.md)（P2 阶段会按场景拆分）
