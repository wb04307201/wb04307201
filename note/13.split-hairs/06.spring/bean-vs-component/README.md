# @Bean vs @Component 深度对比

> 一句话：@Component 是类级别注解，通过包扫描自动注册；@Bean 是方法级别注解，在配置类中手动定义，适合第三方库和精细控制场景。

---

## 一、核心原理

| 维度 | @Component | @Bean |
|------|-----------|-------|
| 注解位置 | 类级别 | 方法级别（必须在 @Configuration 或@Component 类中） |
| 注册方式 | 包扫描自动发现并注册 | 方法返回值作为 Bean 手动注册 |
| 适用对象 | 自己编写的类 | 任何类，尤其是第三方库的类 |
| 控制粒度 | 粗粒度 | 细粒度（可控制名称、作用域、初始化逻辑等） |
| CGLIB 代理 | 不需要 | Full 模式下需要 CGLIB 代理保证单例 |

**本质区别**：@Component 是声明式自动注册，@Bean 是编程式手动注册。

---

## 二、@Component 详解

### 2.1 @Component 及其派生注解

```java
@Service          // 服务层业务逻辑
@Repository       // 数据访问层，额外提供异常转换功能
@Controller       // Web 控制器层，配合 MVC 框架使用
```

这三个注解内部都元标注了 @Component，行为完全一致，只是语义不同便于分层识别。

### 2.2 包扫描机制 @ComponentScan

Spring Boot 启动时会自动扫描主类所在包及其子包：

```java
@SpringBootApplication  // 内部包含 @ComponentScan
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

也可自定义扫描范围：

```java
@Configuration
@ComponentScan(basePackages = {"com.example.service", "com.example.repository"})
public class ScanConfig {}
```

**扫描流程**：确定扫描路径 → 遍历 .class 文件 → 检查 @Component 及派生注解 → 生成 BeanDefinition 注册到容器 → Bean 名称默认为类名首字母小写。

### 2.3 适用场景

- **适用**：项目内部自己编写的类、不需要复杂初始化逻辑的组件
- **不适用**：第三方库的类、需要条件化创建 Bean、需要通过方法参数注入依赖的场景

---

## 三、@Bean 详解

### 3.1 基本用法

@Bean 必须用在被 @Configuration 或 @Component 标注的类中的方法上：

```java
@Configuration
public class DataSourceConfig {
    @Bean
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:mysql://localhost:3306/test");
        ds.setUsername("root");
        ds.setPassword("123456");
        return ds;
    }
}
```

方法返回值会被注册为 Spring Bean，默认 Bean 名称为方法名。

### 3.2 适合 @Bean 的场景

**场景一：第三方库类**

```java
@Bean
public RestTemplate restTemplate() {
    return new RestTemplateBuilder().setConnectTimeout(Duration.ofSeconds(5)).build();
}
```

**场景二：需要复杂初始化逻辑**

```java
@Bean
public ThreadPoolExecutor threadPoolExecutor() {
    return new ThreadPoolExecutor(corePoolSize, maxPoolSize, keepAliveTime, TimeUnit.SECONDS,
        new LinkedBlockingQueue<>(100),
        new ThreadFactoryBuilder().setNameFormat("worker-%d").build(),
        new CallerRunsPolicy());
}
```

**场景三：需要根据条件创建不同实现**

```java
@Bean
@ConditionalOnProperty(name = "cache.type", havingValue = "redis")
public CacheManager redisCacheManager() {
    return new RedisCacheManager(redisConnectionFactory);
}
```

### 3.3 方法参数自动注入

@Bean 方法的参数会自动从容器中查找并注入：

```java
@Configuration
public class AppConfig {
    @Bean
    public ServiceA serviceA() { return new ServiceA(); }

    @Bean
    public ServiceB serviceB(ServiceA serviceA) {  // 自动注入
        return new ServiceB(serviceA);
    }
}
```

这种写法清晰展示了 Bean 之间的依赖关系，比字段注入更易于测试和理解。

---

## 四、@Configuration 的 CGLIB 代理

### 4.1 Full 模式与 Lite 模式

| 模式 | proxyBeanMethods | 行为 | 性能 |
|------|-----------------|------|------|
| Full 模式 | true（默认） | Spring 对配置类生成 CGLIB 子类代理 | 较慢 |
| Lite 模式 | false | 不生成代理，直接调用原始方法 | 较快 |

### 4.2 Full 模式的魔法

在 Full 模式下，多次调用同一个 @Bean 方法会返回同一个实例：

```java
@Configuration(proxyBeanMethods = true)
public class FullConfig {
    @Bean
    public ServiceA serviceA() { return new ServiceA(); }

    @Bean
    public ServiceB serviceB() { return new ServiceB(serviceA()); }  // 返回缓存实例

    @Bean
    public ServiceC serviceC() { return new ServiceC(serviceA()); }  // 返回缓存实例
}
```

Spring 通过 CGLIB 代理拦截方法调用：第一次执行方法体创建实例并注册，后续调用直接从缓存返回。

### 4.3 Lite 模式的行为

Lite 模式下没有代理拦截，每次调用都创建新对象：

```java
@Configuration(proxyBeanMethods = false)
public class LiteConfig {
    @Bean
    public ServiceA serviceA() { return new ServiceA(); }

    @Bean
    public ServiceB serviceB() { return new ServiceB(serviceA()); }  // 创建新实例！
}
```

只有第一次调用时返回的对象会被注册为 Bean，后续调用创建的对象不会被注册。

### 4.4 Spring Boot 自动配置的 Lite 模式

Spring Boot 的自动配置类默认使用 Lite 模式：

```java
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass(DataSource.class)
public class DataSourceAutoConfiguration { ... }
```

**原因**：自动配置类数量众多，Full 模式的 CGLIB 代理开销显著；自动配置类内部通常不会互相调用 @Bean 方法。

如果需要跨 @Bean 方法调用保证单例，应该使用方法参数注入：

```java
@Configuration(proxyBeanMethods = false)
public class SafeConfig {
    @Bean
    public ServiceA serviceA() { return new ServiceA(); }

    @Bean
    public ServiceB serviceB(ServiceA serviceA) {  // 推荐：通过参数注入
        return new ServiceB(serviceA);  // 容器保证注入的是单例
    }
}
```

---

## 五、对比表格

| 维度 | @Component | @Bean |
|------|-----------|-------|
| **注解类型** | 类级别注解 | 方法级别注解 |
| **注册机制** | 包扫描自动发现 | 配置类方法手动定义 |
| **适用类** | 自己编写的类（可修改源码） | 任何类，尤其是第三方库 |
| **精细控制** | 有限（仅能指定名称和作用域） | 全面（名称、作用域、init/destroy、依赖等） |
| **CGLIB 代理** | 不需要 | Full 模式需要 |
| **条件化创建** | 需配合 @Conditional 系列注解 | 天然支持，配合 @Conditional 更灵活 |
| **测试友好度** | 一般（依赖扫描） | 好（可直接调用方法） |
| **IDE 支持** | 跳转方便（直接在类上） | 需跳转到配置类方法 |
| **可读性** | 简洁直观 | 集中管理，依赖关系清晰 |
| **典型场景** | Service、Repository、Controller | DataSource、RestTemplate、ThreadPoolExecutor |

---

## 六、常见陷阱

### 陷阱一：Full 模式下同一 @Bean 方法多次调用返回同一实例

```java
@Configuration(proxyBeanMethods = true)
public class TrapConfig {
    @Bean
    public ServiceA serviceA() {
        System.out.println("Creating ServiceA");
        return new ServiceA();
    }

    @Bean
    public ServiceB serviceB() {
        ServiceA a1 = serviceA();
        ServiceA a2 = serviceA();
        System.out.println(a1 == a2);  // true
        return new ServiceB(a1);
    }
}
```

**现象**：控制台只打印一次 "Creating ServiceA"。**解决**：如需多个实例，分别定义不同的 @Bean 方法，或使用原型作用域 `@Scope("prototype")`。

### 陷阱二：Lite 模式下误以为方法调用会返回单例

```java
@Configuration(proxyBeanMethods = false)
public class LiteTrapConfig {
    @Bean
    public ServiceA serviceA() { return new ServiceA(); }

    @Bean
    public ServiceB serviceB() {
        return new ServiceB(serviceA());  // 创建了未注册的孤儿对象！
    }
}
```

**现象**：ServiceB 持有的 ServiceA 不是容器中的那个 Bean。**解决**：始终通过方法参数注入依赖。

### 陷阱三：@Component 类中的 @Bean 方法也是 Lite 模式

```java
@Component  // 不是 @Configuration
public class ComponentWithBean {
    @Bean
    public ServiceA serviceA() { return new ServiceA(); }

    @Bean
    public ServiceB serviceB() {
        return new ServiceB(serviceA());  // Lite 模式，创建新实例
    }
}
```

@Component 类中的 @Bean 方法始终以 Lite 模式运行，即使显式指定 proxyBeanMethods=true 也无效。

---

## 七、面试话术（30 秒版）

> "@Component 和 @Bean 都是用来定义 Spring Bean 的。@Component 是类级别注解，通过包扫描自动注册，适合我们自己写的类；@Bean 是方法级别注解，在 @Configuration 配置类中手动定义，特别适合第三方库的类或者需要精细控制的场景。
>
> 另外要注意 @Configuration 有 Full 和 Lite 两种模式：Full 模式下 Spring 会用 CGLIB 代理配置类，多次调用同一个 @Bean 方法会返回同一个单例；Lite 模式不代理，每次调用都创建新对象。Spring Boot 自动配置类默认用 Lite 模式是为了性能。
>
> 最佳实践是：自己的代码优先用 @Component，第三方库或需要复杂初始化时用 @Bean，依赖注入优先通过方法参数而不是直接调用 @Bean 方法。"

---

## 八、交叉引用

- 主模块：[`06.spring`](../../../06.spring/) — Spring 知识体系
- [Spring AOP](../../../06.spring/08-annotations/aop.md) — CGLIB 代理机制深入
- [Bean 生命周期](../../../06.spring/01-core/ioc/bean-lifecycle.md) — Bean 从创建到销毁的全过程
- [自动配置原理](../../../06.spring/04-spring-boot/auto-configuration.md) — Spring Boot 如何发现并加载 Bean
- [@Conditional 条件注解](../../../06.spring/08-annotations/configuration.md) — 按需注册 Bean
