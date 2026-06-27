# Bean 与 IoC 注解

> 最后更新: 2026-06-14
> ⬅️ [返回注解速查](../README.md) | [Web 注解](web.md) | [配置注解](configuration.md)

本节介绍用于**将类注册为 Bean、注入依赖、设置作用域**的注解。

---

## 🎯 一句话定位

**Bean 注解 = "声明谁是 Bean" + "谁需要依赖"**——`@Component` 家族（@Service/@Repository/@Controller）声明 Bean，`@Autowired`/`@Resource`/`@Inject` 注入依赖，`@Scope` 设置作用域。

---

## 一、声明 Bean（4 种"语义化"注解 + 1 个通用）

### @Component

> 泛指组件，当组件不好归类时使用此注解。功能上等价于 `@Service`/`@Repository`/`@Controller`，**但语义最弱**。

```java
@Component
public class DeptService {
    //具体的方法
}
```

### @Service

> 修饰 `service` 层组件，声明一个对象，会将类实例化并注入到 Bean 容器里。

```java
@Service
public class DeptService {
    //具体的方法
}
```

### @Repository

> 修饰 `dao` 层组件，将数据访问层的类标识为 Spring Bean。Spring 还会**自动转换持久化异常**（这是它与 @Component 唯一的差异）。

```java
@Repository
public interface RoleRepository extends JpaRepository<Role, Long> {
    //具体的方法
}
```

### @Controller

> 修饰 `controller` 层组件，与 `@RequestMapping` 配合使用。详见 [Web 注解](web.md)。

### @Bean

> 用于**方法**上，告诉 Spring "这是某个类的实例，当我需要时给我"。**与 xml 中 `<bean>` 等价**。

```java
@Configuration
public class AppConfig {
    @Bean
    public Uploader initFileUploader() {
        return new FileUploader();
    }
}
```

### @Component vs @Bean

| 维度 | @Component | @Bean |
|------|-----------|-------|
| **作用对象** | 类 | 方法 |
| **注册方式** | 类路径扫描（@ComponentScan） | 显式调用（方法返回值） |
| **自定义能力** | 弱 | 强（可写任意 Java 代码构造对象） |
| **典型场景** | 自己写的类 | 第三方库的类 |

> 📌 当需要把第三方库中的类注册为 Bean 时，**只能用 @Bean**（因为无法给第三方类加 @Component）。

---

## 二、注入 Bean（3 种注解）

### @Autowired

> Spring 提供的注解，**默认按类型（byType）** 注入，要求依赖对象必须存在。`required = false` 可关闭强制验证。

```java
@Autowired
private DeptService deptService;
```

### @Resource

> JDK 提供的注解（JSR-250），**默认按名称（byName）** 注入。`name` 指定名称，`type` 指定类型。

```java
@Resource(name = "deptService")
private DeptService deptService;

@Resource(type = RoleRepository.class)
private DeptService deptService;
```

### @Inject

> JDK 提供的注解（JSR-330），与 `@Autowired` 类似，可出现在**构造方法、方法、属性**上。

```java
@Inject  // 构造方法
public MurmurMessage(Header header, Content content) {
    this.headr = header;
    this.content = content;
}

@Inject  // 方法
public void setContent(Content content) {
    this.content = content;
}

@Inject  // 属性
private MurmurMessage murmurMessage;
```

### @Autowired vs @Resource vs @Inject

| 维度 | @Autowired | @Resource | @Inject |
|------|-----------|-----------|---------|
| **来源** | Spring | JDK（JSR-250） | JDK（JSR-330） |
| **默认注入方式** | byType | byName | byType |
| **多实现类时** | 需配合 @Qualifier | 可用 name 属性 | 需配合 @Qualifier |
| **支持位置** | 构造方法、方法、字段、参数 | 主要字段和方法 | 构造方法、方法、字段 |
| **required = false** | ✅ | ❌ | ❌ |

---

## 三、解决多实现类歧义

### @Qualifier

> 当有多个同一类型的 Bean 时，`@Autowired` 按类型注入会失败，用 `@Qualifier` 显式指定名称。

```java
@Autowired
@Qualifier("deptService")
private DeptService deptService;
```

### 典型场景

```java
public interface MessageSender { ... }

@Component("smsSender")
public class SmsSender implements MessageSender { ... }

@Component("emailSender")
public class EmailSender implements MessageSender { ... }

// 注入时需要 @Qualifier 区分
@Autowired
@Qualifier("smsSender")
private MessageSender sender;
```

---

## 四、Bean 作用域

### @Scope

> 声明 Spring Bean 的作用域，共有 6 种。

```java
@RestController
@Scope("singleton")  // 默认
public class HelloController {
}

@Scope(value = ConfigurableBeanFactory.SCOPE_PROTOTYPE)
public class DeptService {
}
```

### 6 种作用域

| 作用域 | 说明 | 适用场景 |
|--------|------|----------|
| **singleton** | 唯一 Bean 实例（**默认**） | 无状态 Bean（Service、DAO、Controller） |
| **prototype** | 每次获取都创建新实例 | 有状态 Bean（需要保存每次调用的数据） |
| **request** | 每个 HTTP 请求一个 Bean | Web 层请求级数据 |
| **session** | 每个 HTTP Session 一个 Bean | 用户会话级数据 |
| **application** | 整个 Web 应用一个 Bean | 全局共享数据 |
| **websocket** | 每个 WebSocket 会话一个 Bean | 实时通信 |

### singleton vs prototype 的线程安全

| 作用域 | 是否线程安全 | 原因 |
|--------|------------|------|
| **singleton** | 取决于是否有状态 | 单例被多线程共享，**有可变成员变量就有线程安全问题** |
| **prototype** | ✅ 安全 | 每次获取新实例，无共享 |

### 解决 singleton 线程安全问题

```java
@Service
@Scope("singleton")
public class UserService {
    // 方案 1：避免可变成员变量（推荐）
    // 方案 2：用 ThreadLocal 封装可变状态
    private ThreadLocal<User> currentUser = new ThreadLocal<>();
}
```

---

## 五、Bean 注入语义注解

> 本节介绍**控制 Bean 注入行为**的注解：延迟注入、多实现类优先选择、强制顺序、集合排序。

### @Lazy

> 延迟初始化 Bean。**默认 Spring 在容器启动时实例化所有 singleton Bean**，`@Lazy` 让其在**首次被注入/查找**时才创建。

```java
@Lazy
@Service
public class HeavyService { ... }

// 注入时延迟：@Autowired + @Lazy
@Autowired @Lazy
private HeavyService heavy;       // 此处注入的是代理，方法被调用时才真正创建
```

#### 解决循环依赖

> 配合 `@Autowired` 上的 `@Lazy` 可**打破构造器注入的循环依赖**。

```java
// ❌ 循环依赖：构造器注入时启动失败
public A(B b) { this.b = b; }
public B(A a) { this.a = a; }

// ✅ 用 @Lazy 注入
public A(@Lazy B b) { this.b = b; }      // B 的代理先注入，使用时才真正创建
public B(A a) { this.a = a; }
```

> ⚠️ `@Lazy` 是治标手段，**根本解法是重构依赖方向**。详见 [01-core/ioc/circular-dependency](../01-core/ioc/circular-dependency.md)。

### @Primary

> 当有**多个同类型 Bean** 时，`@Primary` 标记的 Bean **优先被注入**（无需 `@Qualifier`）。

```java
public interface MessageSender { ... }

@Service
@Primary                          // ← 默认优先
public class EmailSender implements MessageSender { ... }

@Service
public class SmsSender implements MessageSender { ... }

// 不写 @Qualifier，默认注入 EmailSender
@Autowired
private MessageSender sender;
```

### @DependsOn

> 强制 **Bean 初始化顺序**——指定的 Bean 会在当前 Bean 之前创建。

```java
@DataSourceConfig   // 数据源先初始化
public class DataSourceConfig { ... }

@Service
@DependsOn("dataSourceConfig")    // 确保 DataSourceConfig 先 ready
public class UserService { ... }
```

> 📌 适用场景：Bean A 初始化时需要 Bean B 的状态（如配置加载器先于业务服务）。

### @Order 与 @Priority

> 控制**集合 / 数组注入**时的 Bean 顺序，或**AOP 通知**的执行顺序。

| 注解 | 位置 | 用途 |
|:-----|:-----|:-----|
| `@Order(value)` | 类 / 方法 / 字段 | 通用排序（值越小越靠前） |
| `@Priority(value)` | 类 / 方法 | 与 JSR-250 标准（作用相近） |

```java
// 集合注入：按 @Order 排序
public interface Plugin { }

@Component @Order(1) class LogPlugin implements Plugin { ... }
@Component @Order(2) class AuthPlugin implements Plugin { ... }

@Autowired
private List<Plugin> plugins;     // [LogPlugin, AuthPlugin]

// AOP 通知顺序
@Aspect @Component
@Order(1)                         // 数字越小优先级越高
public class TxAspect { ... }

@Aspect @Component
@Order(2)
public class LogAspect { ... }
```

---

## 🤔 思考

1. **@Component 家族（@Service/@Repository/@Controller）为什么功能等价还要分？** 业务语义化 + 未来扩展点（@Repository 自动转换异常）。
2. **构造器注入还是字段注入？** Spring 官方推荐**构造器注入**（强制依赖、利于测试、支持 final）。👉 详见 [为什么不推荐 @Autowired 字段注入](../../13.split-hairs/06.spring/not-use-@autowired/README.md)。
3. **@Autowired 找不到 Bean 怎么办？** 检查包路径（是否在 @ComponentScan 范围）、@Service 是否漏写、依赖是否冲突。
4. **为什么 singleton Bean 要避免可变成员变量？** 多个线程共享同一实例，可变状态会引发数据竞争。
5. **@Primary vs @Qualifier？** @Primary 是"约定"（默认选谁），@Qualifier 是"显式指定"。多团队协作时优先用 `@Qualifier` 显式声明，避免隐式行为。

---

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [01 核心容器/IoC](../../README.md) — Bean 生命周期
- [01 核心容器/依赖注入](../01-core/ioc/dependency-injection.md) — 3 种注入方式详解
- [01 核心容器/循环依赖](../01-core/ioc/circular-dependency.md) — @Lazy 解决循环依赖
- [13 辨析/为什么不推荐 @Autowired 字段注入](../../13.split-hairs/06.spring/not-use-@autowired/README.md)
- [配置注解](configuration.md) — @Configuration + @Bean
- [Web 注解](web.md) — @Controller 用法
