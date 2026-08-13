# 自定义 Condition 类（高级）

> ⬅️ [返回 04 Spring Boot](README.md) | [自动配置原理](auto-configuration.md) | [自定义 Starter](custom-starter.md)

当内置的 11 个 `@ConditionalOn*` 注解无法表达你的业务规则（例如"配置文件存在且版本号 ≥ 1.5"），可以**自己实现 `Condition` 接口**，再用通用的 `@Conditional(MyCondition.class)` 引用。

---

## 🎯 一句话定位

**自定义 `Condition` = `@ConditionalOn*` 11 个内置注解之外的"逃生口"**——用纯 Java 写一个布尔判定器，组合 classpath / Bean / 配置属性等多源条件，形成可复用的业务规则。

---

## 十一、自定义 `Condition` 类

当内置的 11 个 `@ConditionalOn*` 注解无法表达你的业务规则（例如"配置文件存在且版本号 ≥ 1.5"），可以**自己实现 `Condition` 接口**，再用通用的 `@Conditional(MyCondition.class)` 引用。

### 1. 核心接口

```java
public interface Condition {
    boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata);
}
```

- `ConditionContext` — 拿到 `BeanFactory`、`Environment`、`ResourceLoader`、`ClassLoader`，可判断 classpath 资源 / Bean / 配置属性。
- `AnnotatedTypeMetadata` — 可读取自定义注解的元数据（`@Conditional(MyCondition.class)` 上声明的属性）。

### 2. 实战案例：仅当 `app.feature.flag = on` 且 classpath 存在某个类时生效

```java
// (1) 自定义 Condition 实现
public class FeatureFlagAndClassCondition implements Condition {

    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        // 2a. 判断 classpath 类
        boolean classPresent;
        try {
            Class.forName("com.example.optional.Dependency", false,
                          context.getClassLoader());
            classPresent = true;
        } catch (ClassNotFoundException e) {
            classPresent = false;
        }

        // 2b. 判断配置属性
        Environment env = context.getEnvironment();
        boolean flagOn = "on".equalsIgnoreCase(env.getProperty("app.feature.flag"));

        return classPresent && flagOn;
    }
}

// (2) 在自动配置类上使用
@AutoConfiguration
@Conditional(FeatureFlagAndClassCondition.class)
public class FeatureAutoConfiguration {

    @Bean
    public FeatureService featureService(FeatureProperties props) {
        return new FeatureService(props);
    }
}
```

### 3. 进阶：自定义注解 + 元数据读取

将业务参数提升为注解属性（而非硬编码在 Condition 内），让 Condition 更通用：

```java
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Conditional(OnPropertyAndClassCondition.class)
public @interface ConditionalOnPropertyAndClass {
    String value();              // 配置项 key
    String havingValue();        // 期望值
    String className();          // 必须存在的类名
}

public class OnPropertyAndClassCondition implements Condition {
    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        Map<String, Object> attrs = metadata.getAnnotationAttributes(
            ConditionalOnPropertyAndClass.class.getName());

        String propKey   = (String) attrs.get("value");
        String propValue = (String) attrs.get("havingValue");
        String className = (String) attrs.get("className");

        boolean propOk = propValue.equalsIgnoreCase(
            context.getEnvironment().getProperty(propKey));

        boolean classOk;
        try {
            Class.forName(className, false, context.getClassLoader());
            classOk = true;
        } catch (ClassNotFoundException e) {
            classOk = false;
        }

        return propOk && classOk;
    }
}

// 使用：
@AutoConfiguration
@ConditionalOnPropertyAndClass(value = "app.feature.flag",
                               havingValue = "on",
                               className = "com.example.optional.Dependency")
public class FeatureAutoConfiguration { ... }
```

### 4. 选型建议

| 场景 | 推荐 |
|------|------|
| 已有 `@ConditionalOn*` 能覆盖 | 优先用现成注解（性能更好、IDE 友好） |
| 业务规则需要"组合判定 + 复杂逻辑" | 自定义 `Condition` 类 |
| 同一条规则要在多处复用 | 自定义注解 + 元数据读取模式 |

> 📌 **调试技巧**：自定义 Condition 失败时，开启 `debug=true`，启动日志会在 **Negative matches** 部分精确指出哪个 `@Conditional` 没匹配。


## 相关章节

- ⬅️ [返回 04 Spring Boot](README.md)
- [自动配置原理](auto-configuration.md) — 内置 11 个 `@ConditionalOn*` 注解的工作机制
- [自定义 Starter](custom-starter.md) — 自动配置类 + 条件注解封装为可复用 Starter

---
