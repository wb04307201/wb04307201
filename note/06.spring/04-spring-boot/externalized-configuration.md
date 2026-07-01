# Spring Boot 外部化配置

> ⬅️ [返回 04 Spring Boot](README.md) | [启动流程](startup-flow.md) | [自动配置原理](auto-configuration.md)

外部化配置（Externalized Configuration）是 Spring Boot 12 项生产级特性之首——把"配置"从代码中抽离，放到 JAR 之外的 `application.yml` / `application.properties` / 环境变量 / 命令行参数中，让同一份代码能在不同环境（dev / test / staging / prod）下无缝切换。

---

## 🎯 一句话定位

**外部化配置 = "一份代码，多套配置"**——通过 `application.yml` + `@Value` / `@ConfigurationProperties` / `@Profile` / `Environment` 4 大入口，让 Spring Boot 应用在不重新打包的情况下适配任何环境。

---

## 一、`application.yml` 加载顺序与优先级

Spring Boot 按以下**从高到低**的优先级加载配置（后加载的覆盖先加载的）：

| 优先级 | 来源 | 备注 |
|:------:|------|------|
| 1 | 命令行参数（`--server.port=9090`） | 最高优先级，适合临时覆盖 |
| 2 | `SPRING_APPLICATION_JSON` 内的 JSON | 环境变量形式 |
| 3 | ServletContext 初始化参数 | Web 环境特有 |
| 4 | JNDI 属性 | `java:comp/env` |
| 5 | JVM 系统属性（`-Dserver.port=9090`） | |
| 6 | OS 环境变量 | 容器化部署常用 |
| 7 | `application-{profile}.yml`（profile-specific） | 配合 `spring.profiles.active` |
| 8 | `application.yml`（默认） | 项目内的主配置 |
| 9 | `@PropertySource` 注解 | 自定义 properties 文件 |
| 10 | 默认属性（`SpringApplication.setDefaultProperties`） | 最低 |

> 📌 **profile-specific 文件覆盖默认文件**：当 `spring.profiles.active=prod` 时，`application-prod.yml` 的同名属性会覆盖 `application.yml` 的值。

---

## 二、`@Value` 基础用法 + SpEL

最轻量的配置注入方式，直接绑定单个属性值：

```java
@Component
public class AppConfig {

    // 基本类型
    @Value("${app.name}")
    private String appName;

    // 带默认值
    @Value("${app.timeout:3000}")
    private int timeout;

    // SpEL 表达式（以 # 开头）
    @Value("#{T(System).currentTimeMillis()}")
    private long startTime;

    // 列表（逗号分隔）
    @Value("${app.allowed-origins:http://localhost,http://example.com}")
    private List<String> allowedOrigins;
}
```

**优点**：简单直观。**缺点**：不支持嵌套属性、松散绑定、JSR-303 校验；多个属性散落在不同类里难以管理。

---

## 三、`@ConfigurationProperties` + `@ConfigurationPropertiesScan`

将一组**结构化配置**绑定到一个 POJO，是 `@Value` 的结构化替代方案。

### 1. 定义 Properties 类

```yaml
# application.yml
app:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: secret
    pool:
      max-size: 20
      min-idle: 5
  features:
    cache: true
    tracing: false
```

```java
@Data
@Component
@ConfigurationProperties(prefix = "app")
@Validated  // 启用 JSR-303 校验
public class AppProperties {

    @NotBlank
    private String name = "default-app";

    @Valid  // 嵌套校验
    private DataSource datasource;

    @NotNull
    private Map<String, Boolean> features = new HashMap<>();

    @Data
    public static class DataSource {
        @NotBlank private String url;
        private String username;
        private String password;

        @Valid
        private Pool pool;
    }

    @Data
    public static class Pool {
        @Min(1) @Max(100) private int maxSize = 10;
        @Min(0) private int minIdle = 0;
    }
}
```

### 2. 三种启用方式

```java
// 方式 1：在 Properties 类上加 @Component（最简单）
@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties { ... }

// 方式 2：在 @Configuration 类上 @EnableConfigurationProperties
@Configuration
@EnableConfigurationProperties(AppProperties.class)
public class AppConfig { ... }

// 方式 3（推荐 3.x）：@ConfigurationPropertiesScan 扫描整个包
@SpringBootApplication
@ConfigurationPropertiesScan("com.example.config")
public class MyApp { ... }
```

### 3. 嵌套绑定与松散绑定

- **嵌套绑定**：`app.datasource.pool.max-size` 自动绑定到 `appProperties.getDatasource().getPool().setMaxSize(20)`。
- **松散绑定**：`app.user-name`、`app.userName`、`app.user_name`、`APP_USERNAME` 等价（推荐 kebab-case）。

### 4. JSR-303 校验

启用 `@Validated` 后，启动时会自动校验配置：

```java
@Validated
@ConfigurationProperties(prefix = "app")
public class AppProperties {

    @NotBlank
    @Size(min = 3, max = 20)
    private String name;

    @Min(1024) @Max(65535)
    private int port;
}
```

启动若失败：

```
***************************
APPLICATION FAILED TO START
***************************
Description:
Binding to target com.example.AppProperties failed:

    Reason: must be greater than or equal to 1024
```

---

## 四、`@PropertySource` 加载自定义 properties 文件

默认只加载 `application.yml` / `application.properties`。如需加载**自定义文件**：

```java
@Configuration
@PropertySource("classpath:custom.properties")  // 加载 src/main/resources/custom.properties
@PropertySource(value = "file:${app.config.dir}/external.properties",
                ignoreResourceNotFound = true)   // 外部配置文件可缺失
public class ExternalConfig { ... }
```

> ⚠️ `@PropertySource` 不支持 YAML——如需 YAML，请改用 `application-{profile}.yml` 或自定义 `PropertySourceLoader`。

---

## 五、`Environment` 抽象 + `MutablePropertySources` 链

`Environment` 是 Spring 配置的**统一门面**，所有属性源（properties source）都挂在它的 `MutablePropertySources` 链上：

```java
@Component
public class EnvPrinter implements ApplicationRunner {

    @Autowired
    private Environment env;

    @Override
    public void run(ApplicationArguments args) {
        // 1. 读取属性
        String port = env.getProperty("server.port");
        // 带默认值
        String region = env.getProperty("app.region", "cn-east-1");
        // 强类型
        Integer maxSize = env.getProperty("app.pool.max-size", Integer.class, 10);

        // 2. 检查 profile
        boolean isProd = env.acceptsProfiles(Profiles.of("prod"));
        boolean isDev  = env.acceptsProfiles(Profiles.of("dev", "test"));

        // 3. 查看所有属性源
        for (PropertySource<?> ps : env.getPropertySources()) {
            System.out.println(ps.getName() + " -> " + ps.getSource());
        }
    }
}
```

---

## 六、`@Profile` 多环境配置

`@Profile` 让 Bean / 配置类只在指定 profile 下生效。

### 1. 三种声明方式

```java
// (1) 类级别
@Profile("prod")
@Configuration
public class ProdConfig {
    @Bean
    public DataSource prodDataSource() { ... }
}

// (2) 方法级别
@Configuration
public class DataSourceConfig {

    @Bean
    @Profile("dev")
    public DataSource devDataSource() { return new H2DataSource(); }

    @Bean
    @Profile("prod")
    public DataSource prodDataSource() { return new MysqlDataSource(); }
}

// (3) 表达式
@Profile("!prod")        // 非 prod
@Profile("dev | test")   // dev 或 test
@Profile("prod & eu")    // prod 且 eu
```

### 2. 激活 profile

```bash
# 方式 1：application.yml
spring:
  profiles:
    active: dev

# 方式 2：命令行
java -jar app.jar --spring.profiles.active=prod

# 方式 3：环境变量
SPRING_PROFILES_ACTIVE=prod java -jar app.jar

# 方式 4：JVM 参数
java -Dspring.profiles.active=prod -jar app.jar
```

### 3. profile-specific 配置文件

```
src/main/resources/
├── application.yml              # 公共配置
├── application-dev.yml          # 开发环境
├── application-test.yml         # 测试环境
└── application-prod.yml         # 生产环境
```

激活 `prod` 时，`application-prod.yml` 覆盖 `application.yml`。

---

## 七、`@Value` vs `@ConfigurationProperties` 选型决策表

| 维度 | `@Value` | `@ConfigurationProperties` |
|------|----------|----------------------------|
| **绑定方式** | 单个属性 | 结构化（嵌套 / 集合 / Map） |
| **松散绑定** | 不支持 | 支持（kebab / camel / snake） |
| **SpEL** | 支持 | 不支持 |
| **JSR-303 校验** | 不支持 | 支持（`@Validated`） |
| **元数据提示** | 无 | 生成 `spring-configuration-metadata.json`，IDE 自动补全 |
| **多属性管理** | 散落各处 | 集中在一个 POJO |
| **性能** | 每次启动反射读取 | 启动时一次性绑定 |

**经验法则**：
- **1-3 个独立属性** → `@Value` 更轻量。
- **结构化配置**（数据源、Redis、线程池、第三方 SDK） → `@ConfigurationProperties` + `@ConfigurationPropertiesScan`。
- **需要校验** → `@ConfigurationProperties` + `@Validated`。

---

## 八、`spring.config.import` 外部配置导入

Spring Boot 2.4+ 引入 `spring.config.import`，可把远程 / 额外的配置合并进 Environment：

```yaml
# application.yml
spring:
  config:
    import:
      - classpath:extra-config.yml           # 额外 classpath 文件
      - file:./config/secrets.properties     # 文件系统（容器外挂配置常用）
      - optional:file:/run/secrets/app.yml  # optional: 前缀 = 文件可缺失
      - vault://secret/myapp/dev            # Spring Cloud Config / Vault
```

> 📌 `optional:` 前缀是 Spring Boot 2.4+ 的关键改进——文件缺失时**不报错**（特别适合 K8s Secret 挂载场景）。

---

## 🤔 思考

1. **为什么配置要外部化？** 让同一份构建产物（jar / image）在不同环境运行，避免"为每个环境重新打包"。
2. **`@Value` 和 `@ConfigurationProperties` 选哪个？** 看属性的**数量与结构**——少量独立属性用 `@Value`，结构化批量属性用 `@ConfigurationProperties`。
3. **为什么 profile 文件命名是 `application-{profile}.yml`？** Spring Boot 约定的查找规则，无需显式注册。
4. **K8s 下配置怎么管？** 用 `spring.config.import` + `optional:file:...` 挂载 ConfigMap / Secret，再叠加环境变量 `SPRING_PROFILES_ACTIVE`。
5. **`@PropertySource` 和 `spring.config.import` 区别？** 前者是注解级别、只支持 properties；后者是配置文件级别、支持 YAML + 远程。

---

## 相关章节

- ⬅️ [返回 04 Spring Boot](README.md)
- [启动流程](startup-flow.md) — Environment 在启动的哪个阶段被准备
- [自动配置原理](auto-configuration.md) — `@ConditionalOnProperty` 用的是同一个 Environment
- [08 注解/配置注解](../08-annotations/configuration.md) — `@Value` / `@ConfigurationProperties` / `@Profile` 详解
- [01 核心/外部化配置](../01-core/externalized-configuration.md) — Spring Core 层面的配置注入原理

---

