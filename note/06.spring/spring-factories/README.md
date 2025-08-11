# spring.factories

在 Spring Boot 3.0 中，`spring.factories` 文件被彻底移除，取而代之的是新的 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 机制。这一变革旨在优化启动性能、简化配置管理，并适应现代 Java 生态的需求。以下是关键变化与迁移策略的详细分析：

### **一、变革背景与核心原因**
1. **性能痛点**
    - **全量扫描**：旧版 Spring Boot 启动时会扫描所有 JAR 包中的 `spring.factories` 文件，即使某些配置永远不会被激活，导致不必要的 I/O 开销。
    - **解析效率低**：Properties 文件的解析和反射调用开销较大，尤其在微服务架构中，多个服务重复加载相同配置会放大性能问题。
    - **依赖冲突**：不同版本的依赖可能定义相同的自动配置类，导致冲突难以解决。

2. **开发体验问题**
    - **调试困难**：大量自动配置类在启动时被加载，增加了调试复杂度。
    - **扩展不灵活**：第三方库开发者需遵循严格的命名约定，扩展机制不够直观。

3. **技术演进需求**
    - Spring Boot 3.0 基于 Spring Framework 6.0 构建，要求 Java 17+，并迁移到 Jakarta EE 9+ 规范。旧机制难以满足新生态的性能和可维护性要求。

### **二、新机制：AutoConfiguration.imports**
1. **文件格式**
    - 新文件位于 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`，每行一个自动配置类的全限定名，例如：
      ```plaintext
      org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration
      org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
      ```

2. **核心改进**
    - **静态分析**：通过 Gradle/Maven 插件在编译时生成 `AutoConfiguration.imports`，避免运行时扫描。
    - **按需加载**：结合 `@AutoConfiguration` 注解和条件注解（如 `@ConditionalOnClass`），实现更精准的配置激活。
    - **性能优化**：启动时间显著缩短，内存占用减少。官方数据显示，某些场景下启动速度提升 25%。

3. **注解调整**
    - 旧版使用 `@Configuration` + `@ConditionalOnClass` 等组合注解，新版推荐使用 `@AutoConfiguration`（元注解，内部包含 `@Configuration` 和排序逻辑），例如：
      ```java
      @AutoConfiguration
      @ConditionalOnClass(DataSource.class)
      public class DataSourceAutoConfiguration { ... }
      ```

### **三、迁移策略与最佳实践**
1. **迁移步骤**
    - **移除旧配置**：删除 `spring.factories` 文件中 `EnableAutoConfiguration` 相关配置。
    - **创建新文件**：在 `META-INF/spring/` 目录下新建 `org.springframework.boot.autoconfigure.AutoConfiguration.imports` 文件，并逐行写入需要自动配置的类名。
    - **更新注解**：确保自动配置类使用 `@AutoConfiguration` 替代 `@Configuration`（若需保留旧版兼容性，可同时使用两者）。

2. **兼容性处理**
    - 对于需兼容 Spring Boot 2.x 的库，可同时保留 `spring.factories` 和 `AutoConfiguration.imports`。Spring Boot 3.x 会自动识别并优先使用新机制。

3. **条件注解优化**
    - 新版支持更灵活的条件组合逻辑，例如使用 `@ConditionalOnAll` 替代多个 `@ConditionalOnClass` 组合：
      ```java
      @Configuration
      @ConditionalOnAll({
          @ConditionalOnClass(DataSource.class),
          @ConditionalOnProperty("app.db.enabled")
      })
      public class DatabaseAutoConfiguration { ... }
      ```

4. **性能测试与验证**
    - 使用 JMH 基准测试对比新旧机制的加载性能，例如：
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

### **四、典型案例分析**
1. **Web MVC 自动配置迁移**
    - **旧版（Spring Boot 2.7）**：
      ```java
      @Configuration
      @ConditionalOnWebApplication(type = Type.SERVLET)
      @ConditionalOnClass({Servlet.class, DispatcherServlet.class})
      public class WebMvcAutoConfiguration { ... }
      ```
    - **新版（Spring Boot 3.1）**：
      ```java
      @AutoConfiguration(after = DispatcherServletAutoConfiguration.class)
      @ConditionalOnWebApplication(type = Type.SERVLET)
      @ConditionalOnClass({Servlet.class, DispatcherServlet.class, WebMvcConfigurer.class})
      public class WebMvcAutoConfiguration { ... }
      ```
    - **关键变化**：包名升级（`org.springframework.boot.autoconfigure.web.servlet` → `org.springframework.boot.autoconfigure.web`），注解优化（`@AutoConfigureOrder` → `@AutoConfiguration` 元注解），功能调整（移除 JSP 支持，新增 `HiddenHttpMethodFilter` 条件配置）。

2. **Jakarta EE 适配**
    - **旧版（Servlet API）**：
      ```java
      import javax.servlet.Filter;
      public class JwtFilter extends OncePerRequestFilter { ... }
      ```
    - **新版（Jakarta Servlet API）**：
      ```java
      import jakarta.servlet.Filter;
      public class JwtFilter extends OncePerRequestFilter { ... }
      ```
    - **批量替换策略**：
      ```bash
      find . -name "*.java" -exec sed -i 's/javax.servlet/jakarta.servlet/g' {} \;
      ```

### **五、总结与展望**
Spring Boot 3.0 移除 `spring.factories` 是为了应对日益复杂的生态系统和用户对启动性能的更高要求。新机制通过静态分析、按需加载和条件注解优化，显著提升了启动速度和开发体验。尽管短期内会带来迁移成本，但从长远来看，这一改变将为 Spring Boot 生态的可持续发展奠定坚实基础。建议开发者采用分阶段渐进式迁移策略，结合自动化工具（如 OpenRewrite）降低升级风险，并充分利用官方文档和社区资源解决典型问题。