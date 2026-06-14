# Spring Boot 3 中 spring.factories 机制移除

> 最后更新: 2026-06-14
> ⬅️ [返回 04 Spring Boot](README.md) | [自动配置原理](auto-configuration.md) | [自定义 Starter](custom-starter.md)

在 Spring Boot 3.0 中，自动配置的注册方式从 `META-INF/spring.factories` 切换到 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。这一变革旨在优化启动性能、简化配置管理，并适应 Jakarta EE 9+ 命名空间。

---

## 一、变革背景与核心原因

### 1. 性能痛点

- **全量扫描**：旧版 Spring Boot 启动时会扫描所有 JAR 包中的 `spring.factories` 文件，即使某些配置永远不会被激活，导致不必要的 I/O 开销。
- **解析效率低**：Properties 文件的解析和反射调用开销较大，尤其在微服务架构中，多个服务重复加载相同配置会放大性能问题。

### 2. 技术演进需求

- Spring Boot 3.0 基于 Spring Framework 6.0 构建，要求 Java 17+，并迁移到 Jakarta EE 9+ 规范。
- 旧机制难以满足新生态的性能和可维护性要求。

---

## 二、新机制：AutoConfiguration.imports

### 1. 文件格式

新文件位于 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`，每行一个自动配置类的全限定名，例如：

```plaintext
org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration
org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

### 2. 核心改进

- **静态分析**：通过 Gradle/Maven 插件在编译时生成 `AutoConfiguration.imports`，避免运行时扫描。
- **按需加载**：结合 `@AutoConfiguration` 注解和条件注解（如 `@ConditionalOnClass`），实现更精准的配置激活。
- **性能优化**：启动时间显著缩短，内存占用减少。

### 3. 注解调整

旧版使用 `@Configuration` + `@ConditionalOnClass` 等组合注解，新版推荐使用 `@AutoConfiguration`（元注解，内部包含 `@Configuration` 和排序逻辑）：

```java
@AutoConfiguration
@ConditionalOnClass(DataSource.class)
public class DataSourceAutoConfiguration { ... }
```

---

## 三、迁移策略与最佳实践

### 1. 迁移步骤

- **移除旧配置**：删除 `spring.factories` 文件中 `EnableAutoConfiguration` 相关配置。
- **创建新文件**：在 `META-INF/spring/` 目录下新建 `org.springframework.boot.autoconfigure.AutoConfiguration.imports` 文件，并逐行写入需要自动配置的类名。
- **更新注解**：确保自动配置类使用 `@AutoConfiguration` 替代 `@Configuration`。

### 2. 兼容性处理

对于需兼容 Spring Boot 2.x 的库，可同时保留 `spring.factories` 和 `AutoConfiguration.imports`。Spring Boot 3.x 会自动识别并优先使用新机制。

### 3. 条件注解优化

新版支持更灵活的条件组合——直接组合多个 `@ConditionalOn*` 注解即可（Spring 会按 **AND** 语义求值）：

```java
@AutoConfiguration
@ConditionalOnClass(DataSource.class)
@ConditionalOnProperty(name = "app.db.enabled", havingValue = "true", matchIfMissing = true)
public class DatabaseAutoConfiguration { ... }
```

> ⚠️ **注意**：不存在 `@ConditionalOnAll` 这样的官方注解。若需要"组合条件 + 自定义逻辑"，应实现自定义 `Condition` 类（见 [auto-configuration.md 自定义 Condition 章节](auto-configuration.md#十一自定义-condition-类)）。

### 4. 性能测试与验证

使用 JMH 基准测试对比新旧机制的加载性能：

```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
public class AutoConfigurationBenchmark {
    @Benchmark
    public void loadWithSpringFactories() { /* 模拟旧机制加载 */ }
    @Benchmark
    public void loadWithAutoConfigurationImports() { /* 模拟新机制加载 */ }
}
```

---

## 四、典型案例分析

### 1. Web MVC 自动配置迁移

- **旧版（Spring Boot 2.7）**：

  ```java
  @Configuration
  @ConditionalOnWebApplication(type = Type.SERVLET)
  @ConditionalOnClass({Servlet.class, DispatcherServlet.class})
  public class WebMvcAutoConfiguration { ... }
  ```

- **新版（Spring Boot 3.x）**：

  ```java
  @AutoConfiguration(after = DispatcherServletAutoConfiguration.class)
  @ConditionalOnWebApplication(type = Type.SERVLET)
  @ConditionalOnClass({Servlet.class, DispatcherServlet.class, WebMvcConfigurer.class})
  public class WebMvcAutoConfiguration { ... }
  ```

- **包路径的真实情况**：Spring Boot 3 引入 Jakarta Servlet 5+ 命名空间后，自动配置类包路径发生调整：
  - `org.springframework.boot.autoconfigure.web.servlet.*`（Servlet 栈，Tomcat/Jetty）
  - `org.springframework.boot.autoconfigure.web.reactive.*`（Reactive 栈，Netty）
  
  这些路径**不是简单的"重命名"**，而是按技术栈拆分。**Spring Boot 3.x 中部分旧的混合包路径（如 `org.springframework.boot.autoconfigure.web.WebMvcAutoConfiguration`）仍然存在以保持向后兼容**，但新代码应使用更明确的 `web.servlet` / `web.reactive` 子包。

### 2. Jakarta EE 适配

- **旧版（Servlet API，2.x 时代）**：

  ```java
  // 历史 API：2.x 时代为 javax.*，3.x 已统一迁移到 jakarta.*
  // import javax.servlet.Filter;  // ⚠️ 已弃用，仅作历史对照
  public class JwtFilter extends OncePerRequestFilter { ... }
  ```

- **新版（Jakarta Servlet API）**：

  ```java
  import jakarta.servlet.Filter;
  public class JwtFilter extends OncePerRequestFilter { ... }
  ```

- **批量替换策略（务必谨慎）**：

  > ⚠️ **javax.\* 中 `javax.persistence.*` / `javax.transaction.*` / `javax.validation.*` 不替换为 jakarta.\***，因为这些包名在 Jakarta EE 9+ 没有直接对应物：
  > - `javax.persistence.*` — JPA 仍由 EclipseLink/Hibernate 维护 javax 命名空间的部分（部分版本开始迁移到 `jakarta.persistence.*`）。
  > - `javax.transaction.*` — Jakarta Transactions 拆分为 `jakarta.transaction.*`，但需注意 JTA API 的变化。
  > - `javax.validation.*` — Jakarta Validation 3.0 已迁移到 `jakarta.validation.*`，但 Bean Validation 注解需要单独处理。

  **推荐做法**：

  - 使用 OpenRewrite 官方配方 `org.openrewrite.java.migrate.JavaxToJakarta` 自动处理已知映射。
  - 对未覆盖的包做手工 per-package 评审（特别是 `javax.persistence` / `javax.transaction`）。

  ```bash
  # OpenRewrite Maven 插件示例（不要盲目 sed 全局替换）
  mvn org.openrewrite.maven:rewrite-maven-plugin:5.40.0:run \
      -Drewrite.recipeArtifactCoordinates=org.openrewrite.java:rewrite-migrate-java:2.13.0 \
      -Drewrite.activeRecipes=org.openrewrite.java.migrate.JavaxToJakarta
  ```

---

## 五、总结与展望

Spring Boot 3.0 迁移 `spring.factories` 自动配置声明是为了应对日益复杂的生态系统和用户对启动性能的更高要求。新机制通过静态分析、按需加载和条件注解优化，显著提升了启动速度和开发体验。尽管短期内会带来迁移成本，但从长远来看，这一改变将为 Spring Boot 生态的可持续发展奠定坚实基础。建议开发者采用分阶段渐进式迁移策略，结合 OpenRewrite 等自动化工具降低升级风险。

---

> 最后更新: 2026-06-14