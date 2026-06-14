# 如何创建自己的 Starter 模块

> 最后更新: 2026-06-14
> ⬅️ [返回 04 Spring Boot](README.md) | [自动配置原理](auto-configuration.md) | [spring.factories 迁移](spring-factories-migration.md)

在 Spring Boot 的世界里，**Starter** 是一组预定义的依赖项集合与自动配置机制的完美结合，它通过"约定优于配置"的原则，将复杂的功能模块封装为简单的依赖入口，让开发者能够像搭积木一样快速构建应用。

---

## 一、Starter 的本质：依赖管理与自动配置的融合

### 1. 依赖聚合

Starter 将实现特定功能所需的所有依赖（如库、框架、工具类）打包成一个整体。例如：

- `spring-boot-starter-web` 整合了 Spring MVC、Tomcat、Jackson 等，开发者无需手动添加这些依赖。
- `spring-boot-starter-data-jpa` 封装了 Hibernate、Spring Data JPA 等，简化数据库访问配置。

### 2. 自动配置

Starter 通过自动配置注册文件声明自动配置类（`@Configuration`），Spring Boot 在启动时会根据条件注解（如 `@ConditionalOnClass`、`@ConditionalOnMissingBean`）动态加载这些配置。例如：

- 当类路径中存在 `Servlet` 类时，自动配置嵌入式 Tomcat。
- 当未定义 `DataSource` Bean 时，根据配置文件创建内存数据库（如 H2）。

### 3. 开箱即用的魔法

开发者仅需引入 Starter 依赖并配置少量属性（如 `server.port=8080`），即可直接使用功能，无需编写冗余的 XML 或 Java 配置代码。

> 📌 **自动配置注册方式的版本差异**：
> - **Spring Boot 2.x**：使用 `META-INF/spring.factories`（`key=value` 格式）。
> - **Spring Boot 3.x**：推荐 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`（每行一个类全限定名）；保留 `spring.factories` 用于 Listener / EnvironmentPostProcessor 等其他 SPI 扩展。

---

## 二、自定义 Starter：从 0 到 1 的完整流程

以封装一个 Redis 操作 Starter 为例，步骤如下。

### 1. 创建 Maven 项目

#### Spring Boot 2.x（`spring.factories` 方式）

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.0</version>
</parent>

<dependencies>
    <!-- 基础依赖 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
    </dependency>
    <!-- Redis 客户端 -->
    <dependency>
        <groupId>redis.clients</groupId>
        <artifactId>jedis</artifactId>
        <version>4.3.1</version>
    </dependency>
    <!-- 配置处理器（可选） -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-configuration-processor</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

**2.x 自动配置入口（`src/main/resources/META-INF/spring.factories`）**：

```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
com.example.starter.RedisAutoConfiguration
```

#### Spring Boot 3.x（`AutoConfiguration.imports` 方式）

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
</parent>
<!-- 其余依赖与 2.x 相同 -->
```

**3.x 自动配置入口（`src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`）**：

```plaintext
com.example.starter.RedisAutoConfiguration
```

> 同时把类上的 `@Configuration` 改为 `@AutoConfiguration`（更轻量且支持 `@AutoConfigureBefore/After` 排序）。

### 2. 定义配置属性类

```java
@ConfigurationProperties(prefix = "demo.redis")
@Data
public class RedisProperties {
    private String host = "localhost";
    private int port = 6379;
    private int timeout = 2000;
    private String password;
    // 其他属性...
}
```

通过 `@ConfigurationProperties` 绑定 `application.yml` 中的配置：

```yaml
demo:
  redis:
    host: 192.168.1.100
    port: 6379
    timeout: 3000
```

### 3. 实现自动配置类

```java
@AutoConfiguration  // 3.x；2.x 用 @Configuration
@EnableConfigurationProperties(RedisProperties.class)
@ConditionalOnClass(Jedis.class) // 当类路径存在 Jedis 时生效
public class RedisAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean // 当不存在 JedisPool 实例时创建
    public JedisPool jedisPool(RedisProperties properties) {
        JedisPoolConfig poolConfig = new JedisPoolConfig();
        // ... 配置 pool
        return new JedisPool(poolConfig,
                             properties.getHost(),
                             properties.getPort(),
                             properties.getTimeout(),
                             properties.getPassword());
    }
}
```

### 4. 打包与使用

- 执行 `mvn clean install` 将 Starter 安装到本地仓库。
- 在其他项目中引入依赖：

  ```xml
  <dependency>
      <groupId>com.example</groupId>
      <artifactId>spring-boot-starter-demo-redis</artifactId>
      <version>1.0.0</version>
  </dependency>
  ```

- 直接注入 `JedisPool` 使用：

  ```java
  @Autowired
  private JedisPool jedisPool;
  ```

---

## 三、Starter 的设计哲学与最佳实践

### 1. 模块化

每个 Starter 应聚焦单一功能（如数据库、缓存、消息队列），避免"大而全"的依赖。

### 2. 可扩展性

- 通过 `@Conditional` 注解实现灵活配置（如根据环境切换数据源）。
- 提供默认配置，同时允许通过 `application.yml` 覆盖。

### 3. 文档化

在 `README.md` 中明确说明依赖关系、配置项和示例代码，降低使用者学习成本。

### 4. 测试覆盖

编写集成测试验证 Starter 在不同场景下的行为（如配置缺失、依赖冲突）。

### 5. 跨版本兼容

如果你的 Starter 同时支持 2.x 和 3.x，可以**同时保留** `spring.factories` 和 `AutoConfiguration.imports`：

- 2.x 用户读取 `spring.factories`。
- 3.x 用户优先读取 `AutoConfiguration.imports`。

注意保持 `@Configuration`（2.x 兼容）而非 `@AutoConfiguration`，或使用条件注解分别处理。

---

## 四、Starter 的扩展能力：解锁 Spring Boot 生态

自定义 Starter 不仅是技术实践，更是构建企业级中间件的基础。例如：

- **阿里云 OSS Starter**：封装文件上传、下载逻辑，开发者仅需配置 AccessKey 即可使用。
- **Sentinel Starter**：集成流量控制、熔断降级功能，简化微服务治理。

通过 Starter，Spring Boot 真正实现了"**约定优于配置**"和"**开箱即用**"的核心理念，让开发者从重复劳动中解放，专注于业务创新。

---

> 最后更新: 2026-06-14