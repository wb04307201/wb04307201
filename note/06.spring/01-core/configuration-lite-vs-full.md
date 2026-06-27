# @Configuration 进阶：Lite Mode vs Full Mode 与 @Import 系列

> 最后更新: 2026-06-14
> ⬅️ [返回 01 核心容器](README.md) | [IoC 总览](ioc/README.md) | [FactoryBean](ioc/FactoryBean.md)

`@Configuration` 不只是"配置类标记"——它默认开启了 **CGLIB 增强（Full Mode）**，让 `@Bean` 方法间调用返回的是**容器内单例**，而不是 `new` 出来的新对象。`@Component` 标注的类即便有 `@Bean` 方法，也走的是 **Lite Mode**，没有 CGLIB 增强。配合 `@Import` / `@ImportSelector` / `@ImportBeanDefinitionRegistrar` 三个机制，可实现**模块化配置装配**。

---

## 🎯 一句话定位

**Full Mode = `@Configuration` + CGLIB 增强（保证 `@Bean` 方法调用是单例）**  
**Lite Mode = `@Component` / `@Import` / 静态 `@Bean` 方法（每次调用都新建）**  
**`@Import` 系列 = 把"模块 / 条件"动态接入容器的标准入口**

---

## 一、Full Mode vs Lite Mode

### 1.1 核心差异

| 维度 | Full Mode | Lite Mode |
|------|-----------|-----------|
| **触发条件** | 类标注 `@Configuration` | 类标注 `@Component` / `@Import` / `@Configuration(proxyBeanMethods = false)` |
| **是否有 CGLIB 代理** | ✅ 有 | ❌ 无 |
| **`@Bean` 方法互调结果** | 返回**容器内单例** | 返回**新对象**（普通 Java 调用） |
| **启动开销** | 略高（CGLIB 织入） | 低 |
| **使用场景** | 默认、推荐 | 配置类无内部方法调用、追求启动速度 |

### 1.2 Full Mode 示例

```java
@Configuration                          // ← Full Mode
public class AppConfig {

    @Bean
    public DataSource dataSource() {
        return new HikariDataSource();
    }

    @Bean
    public JdbcTemplate jdbcTemplate() {
        // 调用 dataSource() 时，**返回的是容器内单例**（CGLIB 拦截）
        return new JdbcTemplate(dataSource());
    }
}
```

效果：`ctx.getBean(DataSource.class)` 多次返回的是**同一个实例**。

### 1.3 Lite Mode 示例

```java
@Component                              // ← Lite Mode
public class AppConfig {

    @Bean
    public DataSource dataSource() {
        return new HikariDataSource();
    }

    @Bean
    public JdbcTemplate jdbcTemplate() {
        // 普通 Java 调用：dataSource() 直接执行方法体 → **new 一个新 DataSource**
        return new JdbcTemplate(dataSource());
    }
}
```

效果：每个 `@Bean` 方法都被**独立调用一次**，互不影响（但每次 `dataSource()` 调用都会 `new HikariDataSource()`，浪费资源）。

### 1.4 显式声明 Lite Mode

```java
@Configuration(proxyBeanMethods = false)  // ← 显式 Lite Mode
public class FastConfig {
    @Bean
    public DataSource dataSource() { ... }
}
```

> 📌 Spring Boot 2.2+ 的自动配置类（`@SpringBootApplication`）默认就是 `proxyBeanMethods = false`（Lite Mode），因为自动配置类之间基本不互相调用 `@Bean` 方法，省去 CGLIB 启动开销。

---

## 二、源码视角：Full Mode 的实现

Full Mode 下，Spring 用 **CGLIB** 在 `AppConfig` 字节码层面织入：

```java
// 伪代码：ConfigurationClassEnhancer 织入的拦截逻辑
public DataSource dataSource() {
    if (container.containsBean("dataSource")) {
        return (DataSource) container.getBean("dataSource");  // 命中容器
    }
    return super.dataSource();  // 第一次调用 → 真正执行方法体
}
```

这就是 `@Configuration` 类中 `@Bean` 方法能保证**单例 + 容器内复用**的原因。

---

## 三、@Import 系列

`@Import` 是 Spring 提供给配置类的"**模块化导入**"机制，可把其他配置类 / 普通的类动态纳入容器。

### 3.1 三种形式

| 注解 | 作用 | 典型场景 |
|------|------|----------|
| `@Import(XxxConfig.class)` | 导入**普通类 / 配置类** | 模块化拆分 `@Configuration` |
| `@Import(MySelector.class)` | 通过 `ImportSelector` **动态返回类名数组** | 条件装配（Spirng Boot 自动配置） |
| `@Import(MyRegistrar.class)` | 通过 `ImportBeanDefinitionRegistrar` **手动注册 BeanDefinition** | MyBatis `@MapperScan`、Dubbo `@Enable*` |

---

### 3.2 `@Import(普通类 / @Configuration 类)`

```java
@Configuration
@Import(OtherConfig.class)  // 把 OtherConfig 纳入容器
public class AppConfig { ... }
```

被 `@Import` 的类：

- 若为 `@Configuration`：走 Full Mode 处理。
- 若为普通类：被注册为 Bean（等同于 `@Component`，但**只在被 `@Import` 时才注册**）。

---

### 3.3 `@Import(ImportSelector.class)`

`ImportSelector` 根据条件**动态选择**要导入的类名。Spring Boot 自动配置的"开/关"就靠它。

```java
public class MyImportSelector implements ImportSelector {
    @Override
    public String[] selectImports(AnnotationMetadata importingClassMetadata) {
        // 可根据注解属性、环境变量等动态决定
        if (someCondition()) {
            return new String[] { "com.example.FooConfig" };
        }
        return new String[] {};
    }
}
```

```java
@Configuration
@Import(MyImportSelector.class)
public class AppConfig { ... }
```

#### 进阶：`DeferredImportSelector`

```java
public class MyDeferredImportSelector implements DeferredImportSelector {
    @Override
    public String[] selectImports(AnnotationMetadata metadata) {
        return new String[] { "com.example.FooConfig" };
    }
}
```

- 与 `ImportSelector` 的区别：**延迟到所有配置类解析完成后**再导入。
- Spring Boot 的 `AutoConfigurationImportSelector`（即所有 `spring.factories` / `AutoConfiguration.imports` 中的类）都基于它实现。

---

### 3.4 `@Import(ImportBeanDefinitionRegistrar.class)`

`ImportBeanDefinitionRegistrar` 提供**手动注册 BeanDefinition** 的入口，最灵活。

```java
public class MyBeanDefinitionRegistrar implements ImportBeanDefinitionRegistrar {
    @Override
    public void registerBeanDefinitions(AnnotationMetadata metadata, BeanDefinitionRegistry registry) {
        // 手动注册 BeanDefinition
        RootBeanDefinition def = new RootBeanDefinition(MyService.class);
        registry.registerBeanDefinition("myService", def);
    }
}
```

```java
@Configuration
@Import(MyBeanDefinitionRegistrar.class)
public class AppConfig { ... }
```

#### 真实案例：MyBatis `@MapperScan`

```java
@MapperScan("com.example.mapper")  // 内部通过 @Import 引入 MapperScannerRegistrar
@SpringBootApplication
public class App { ... }
```

`MapperScannerRegistrar` 实现 `ImportBeanDefinitionRegistrar`：

- 扫描 `basePackages` 下的所有接口；
- 为每个接口生成 `MapperFactoryBean` 的 `BeanDefinition`；
- 注册到容器。

---

## 四、三机制对比

| 维度 | `@Import(类)` | `@ImportSelector` | `@ImportBeanDefinitionRegistrar` |
|------|-------------|-------------------|----------------------------------|
| **导入对象** | 写死的类 | 动态返回类名数组 | 手动注册 BeanDefinition |
| **灵活度** | 低 | 中（条件选择） | 高（完全控制） |
| **典型用户** | 模块化拆分 | 自动配置、条件装配 | 第三方框架集成 |
| **执行时机** | 解析配置类时 | 解析配置类时 | 解析配置类时 |
| **可否注册非 BeanDefinition** | ❌ | ❌ | ❌（只能注册 BeanDefinition） |

---

## 五、最佳实践

1. **默认用 Full Mode**（`@Configuration`），安全可靠。
2. **Spring Boot 自动配置类** 用 Lite Mode（`proxyBeanMethods = false`），省启动开销。
3. **业务模块拆分** 用 `@Import` 引入子配置类，避免"巨型 `@Configuration`"。
4. **条件装配** 用 `@Import` + `ImportSelector`（或 `DeferredImportSelector`）。
5. **需要自定义 BeanDefinition** 时用 `ImportBeanDefinitionRegistrar`。

---

## 六、ASCII 流程：Full Mode vs Lite Mode

```
@Configuration 类（Full Mode）
└── 容器启动时 CGLIB 增强，生成子类
    ├── @Bean 方法被调用时，先查容器
    │     ├── 容器已有 → 返回容器内单例
    │     └── 容器没有 → 执行方法体，注册到容器
    └── 方法间调用 → 走 CGLIB 拦截 → 单例复用

@Component 类 / @Configuration(proxyBeanMethods=false)（Lite Mode）
└── 无 CGLIB 增强
    ├── @Bean 方法被调用 → 总是执行方法体
    └── 方法间调用 → 普通 Java 调用 → 每次 new 新对象
```

---

## 🤔 思考

1. **`@Configuration` 必须配合 CGLIB 吗？** Spring 用 CGLIB 是默认实现，`proxyBeanMethods = false` 可关闭。
2. **`@Import` 的类没有 `@Component` 也会被注册？** 会——`@Import` 本身就具备"被导入即注册"的能力。
3. **`DeferredImportSelector` 为什么是延迟的？** 为了让所有用户配置类先解析完，再让"自动配置"对它们做条件匹配（`@Conditional` 评估）。

---

## 相关章节

- ⬅️ [返回 01 核心容器](README.md)
- [IoC 总览](ioc/README.md)
- [FactoryBean](ioc/FactoryBean.md) — 复杂对象的工厂化创建
- [依赖注入](ioc/dependency-injection.md) — `@Bean` 方法返回值的注入
- [08 注解速查](../../README.md) — `@Configuration` / `@Import` 注解细节
