# 配置注解

> 最后更新: 2026-06-09
> ⬅️ [返回注解速查](../README.md) | [Bean 注解](bean-and-ioc.md) | [JPA 注解](jpa.md)

本节介绍 Spring/Java 配置相关的注解：声明配置类、启用自动配置、组件扫描、条件装配、外部化配置、Profile 多环境。

---

## 🎯 一句话定位

**配置注解 = "声明这是配置类" + "从哪扫" + "按什么条件装配" + "从哪读配置"**——`@Configuration` 标记配置类，`@ComponentScan` 决定扫描路径，`@Conditional` 家族按需装配，`@Value`/`@ConfigurationProperties` 绑定外部化配置。

---

## 一、声明配置类

### @Configuration

> 声明一个 Java 形式的配置类，相当于以前在 xml 中配置 `<beans>`。

```java
@Configuration
public class AppConfig {
    @Bean
    public Uploader initOSSUploader() {
        return new OSSUploader();
    }
}
```

### @Configuration vs @Component

| 维度 | @Configuration | @Component |
|------|---------------|------------|
| **语义** | 配置类（含 Bean 定义） | 普通组件 |
| **proxyBeanMethods** | 默认 `true`（保证单例） | 默认 `true` |
| **CGLIB 增强** | 是 | 否 |

> 📌 `@Configuration` 内部包含 `@Component`，会被组件扫描识别。

---

## 二、自动配置（Spring Boot 核心）

### @EnableAutoConfiguration

> 帮助 SpringBoot 应用将所有符合条件的 `@Configuration` 加载到当前 SpringBoot 里，并创建 Bean 交给 IoC 容器管理。

```java
@Configuration
@EnableAutoConfiguration(exclude = { 
    org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class 
})
public class AppConfig {
    //具有业务方法
}
```

### @AutoConfiguration

> Spring Boot 2.7+ 引入的专用注解，用于**明确标识自动配置类**，替代旧版通过 `META-INF/spring.factories` 注册的方式。

#### 与 @Configuration 的区别

| 特性 | @AutoConfiguration | @Configuration |
|------|--------------------|-----------------| 
| **用途** | 专为自动配置设计 | 通用配置类 |
| **条件化支持** | 强制要求（通常与 @Conditional 结合） | 可选 |
| **代理模式** | 默认 `proxyBeanMethods = false`（优化性能） | 默认 `proxyBeanMethods = true` |
| **注册方式** | `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` | `@ComponentScan` 或 `@Import` |

### @SpringBootApplication

> 等价于 `@Configuration + @EnableAutoConfiguration + @ComponentScan` 三件套，用于全局启动类。

```java
@SpringBootApplication
public class PropertyApplication {
    public static void main(String[] args) {
        SpringApplication.run(PropertyApplication.class, args);
    }
}
```

---

## 三、组件扫描

### @ComponentScan

> 标注哪些路径下的类需要被 Spring 扫描，用于自动发现和装配 Bean 对象。**默认扫描当前包及子包**。

```java
@ComponentScan(basePackages = {"com.xxx.a", "com.xxx.b", "com.xxx.c"})
```

> 💡 把 `@SpringBootApplication` 放在根包下，可以自动扫描所有子包，无需显式声明。

---

## 四、条件装配（Spring 4+）

### @Conditional

> 从 Spring 4 开始，通过 `@Conditional` 注解实现**按条件装载 Bean**，是 Spring Boot 自动配置的基石。

### 常用条件注解

| 注解 | 触发条件 |
|------|---------|
| `@ConditionalOnBean` | 当某个特定的 Bean **存在**时，配置生效 |
| `@ConditionalOnMissingBean` | 当某个特定的 Bean **不存在**时，配置生效 |
| `@ConditionalOnClass` | 当 Classpath 里**存在**指定的类，配置生效 |
| `@ConditionalOnMissingClass` | 当 Classpath 里**不存在**指定的类，配置生效 |
| `@ConditionalOnExpression` | 当给定的 SpEL 表达式计算结果为 true，配置生效 |
| `@ConditionalOnProperty` | 当指定的配置属性匹配，配置生效 |

### 完整示例

```java
@Configuration
public class ConditionalConfig {

    @ConditionalOnBean(AppConfig.class)
    @Bean
    public A createA() {
        return new A();
    }

    @ConditionalOnMissingBean(AppConfig.class)
    @Bean
    public B createB() {
        return new B();
    }

    @ConditionalOnClass(KafkaTemplate.class)
    @Bean
    public C createC() {
        return new C();
    }

    @ConditionalOnMissingClass(KafkaTemplate.class)
    @Bean
    public D createD() {
        return new D();
    }

    @ConditionalOnExpression("${enableConfig:false}")
    @Bean
    public E createE() {
        return new E();
    }

    @ConditionalOnProperty(prefix = "filter", name = "loginFilter", havingValue = "true")
    @Bean
    public F createF() {
        return new F();
    }
}
```

> 📌 `@ConditionalOnMissingBean` 是 Spring Boot 自动配置的核心：用户没自定义就用默认的。

---

## 五、外部化配置

### @Value

> 在任意 Spring 管理的 Bean 中通过这个注解获取任何来源配置的属性值。

```properties
# application.properties
config.name=zhangsan
```

```java
@RestController
public class HelloController {
    @Value("${config.name}")
    private String config;

    @GetMapping("config")
    public String config() {
        return JSON.toJSONString(config);
    }
}
```

### @ConfigurationProperties

> **`@Value` 在每个类中获取属性配置值的做法不推荐**。企业项目通常一次性读取一个 Java 配置类，多次复用。

```properties
# application.properties
config.name=demo_1
config.value=demo_value_1
```

```java
@Component
@ConfigurationProperties(prefix = "config")
public class Config {
    private String name;
    private String value;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getValue() { return value; }
    public void setValue(String value) { this.value = value; }
}

// 注入使用
@Autowired
private Config config;
```

### @Value vs @ConfigurationProperties

| 维度 | @Value | @ConfigurationProperties |
|------|--------|--------------------------|
| **注入方式** | 单个字段 | 整个类（多个属性） |
| **类型安全** | 弱（需手动转换） | 强（自动绑定） |
| **松散绑定** | ❌ 严格匹配 | ✅ 支持 `person.firstName` → `firstName`/`first-name`/`first_name` |
| **SpEL** | ✅ 支持 | ❌ |
| **校验** | ❌ | ✅ 支持 JSR-303 校验 |
| **适用场景** | 简单配置、动态表达式 | 结构化配置 |

> 📌 经验法则：**简单值用 @Value，结构化配置用 @ConfigurationProperties**。

---

## 六、自定义配置文件

### @PropertySource

> 读取自定义的配置文件（如 `test.properties`、`business.properties`）。

```java
@SpringBootApplication
@PropertySource(value = {"test.properties", "bussiness.properties"})
public class PropertyApplication {
    public static void main(String[] args) {
        SpringApplication.run(PropertyApplication.class, args);
    }
}
```

### @ImportResource

> 加载 xml 配置文件（兼容老项目）。

```java
@ImportResource(locations = "classpath:aaa.xml")
@SpringBootApplication
public class PropertyApplication {
    public static void main(String[] args) {
        SpringApplication.run(PropertyApplication.class, args);
    }
}
```

---

## 🤔 思考

1. **@SpringBootApplication 为什么是三件套？** 它把"我是配置类 + 启用自动配置 + 扫描当前包"封装为一行，简化启动类。
2. **@ConditionalOnMissingBean 的妙用？** Spring Boot 的"约定优于配置"：用户没配就用默认的，用户配了就用用户的。
3. **什么时候用 @PropertySource vs application.yml？** `@PropertySource` 适合老项目迁移或第三方配置；新项目推荐用 `application.yml`（Spring Boot 自动加载）。
4. **@ConfigurationProperties + @Validated？** 可以校验配置合法性（邮箱格式、长度等），避免运行时才发现配置错误。

---

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [04 Spring Boot/自定义 Starter](../../04-spring-boot/custom-starter.md) — @ConfigurationProperties 实战
- [04 Spring Boot/自动配置原理](../../04-spring-boot/README.md) — @EnableAutoConfiguration 工作机制
- [Bean 注解](bean-and-ioc.md) — @Bean、@Component
- [Web 注解](web.md) — @Controller、@RestController
