# 使用自定义注解进行验证

> 最后更新: 2026-06-14

在Spring Validation中，自定义注解可实现业务特定的验证逻辑（如复杂规则校验）。

## 一、创建自定义注解

### 1. 创建自定义注解
定义注解元数据，指定验证规则和错误消息模板：
```java
import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import java.lang.annotation.*;

@Target({ElementType.FIELD, ElementType.PARAMETER}) // 作用于字段/方法参数
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = AgeRangeValidator.class) // 绑定验证器
public @interface AgeRange {
    String message() default "年龄必须在{min}至{max}岁之间";
    int min() default 18;
    int max() default 60;
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

### 2. 实现验证逻辑
编写`ConstraintValidator`接口的实现类，编写具体校验逻辑：
```java
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

public class AgeRangeValidator implements ConstraintValidator<AgeRange, Integer> {
    private int min;
    private int max;

    @Override
    public void initialize(AgeRange constraintAnnotation) {
        this.min = constraintAnnotation.min();
        this.max = constraintAnnotation.max();
    }

    @Override
    public boolean isValid(Integer value, ConstraintValidatorContext context) {
        if (value == null) return true; // 交由@NotNull处理空值
        return value >= min && value <= max;
    }
}
```

### 3. 在DTO/Entity中应用注解
在需要验证的字段上添加自定义注解：
```java
public class UserDTO {
    @AgeRange(min = 18, max = 60, message = "用户年龄不合法")
    private Integer age;
    
    // Getter/Setter
}
```

### 4. 控制器中使用验证
在Controller方法参数前添加`@Valid`触发验证：
```java
@PostMapping("/users")
public ResponseEntity<?> createUser(@Valid @RequestBody UserDTO userDTO) {
    // 验证通过后的业务逻辑
    return ResponseEntity.ok().build();
}
```

### 5. 自定义错误消息（可选）
在`src/main/resources/messages.properties`中定义国际化消息：
```properties
AgeRange.userDTO.age=年龄必须介于{min}至{max}岁之间
```
通过`application.properties`配置启用：
```properties
spring.messages.basename=messages
```

### 6. 高级扩展：动态参数验证
若需动态参数（如数据库查询结果），可在验证器中注入服务：
```java
@Component
public class DynamicAgeValidator implements ConstraintValidator<AgeRange, Integer> {
    @Autowired
    private AgeService ageService; // 注入业务服务

    @Override
    public boolean isValid(Integer value, ConstraintValidatorContext context) {
        return ageService.isValidAge(value); // 调用服务方法
    }
}
```

### 7. 验证流程解析
- **请求提交**：客户端提交包含`age`字段的JSON数据；
- **自动验证**：Spring MVC调用`Validator`实例执行`isValid()`方法；
- **错误处理**：验证失败时抛出`MethodArgumentNotValidException`，被`@ControllerAdvice`捕获并返回400错误；
- **响应示例**：
```json
{
  "errors": [
    {
      "field": "age",
      "message": "年龄必须在18至60岁之间"
    }
  ]
}
```

通过自定义注解，可将业务规则封装为可复用的验证组件，提升代码可维护性。结合Spring Validation的自动配置，可快速构建健壮的参数验证体系。

## 二、关键注意事项
- **空值处理**：自定义验证器不应处理`null`值，交由`@NotNull`单独验证；
- **线程安全**：验证器默认无状态，若需状态管理需自行保证线程安全；
- **分组验证**：通过`groups`属性指定场景，配合`@Validated(groups=Group.class)`使用；
- **性能优化**：复杂验证逻辑建议异步执行或缓存结果。

## 三、国际化与多语言

国际化（i18n）让验证消息根据请求 `Locale` 自动切换。Bean Validation 通过 `MessageInterpolator` 把 `{min}`、`{max}` 等占位符与资源束（ResourceBundle）合并；Spring 的 `LocalValidatorFactoryBean` 把 `MessageSource` 桥接到 Validator，Spring Boot 通过 `spring.messages.basename` 自动扫描。

### 多语言资源束

按 Hibernate Validator 约定，默认查找 `ValidationMessages` 主名：

```
src/main/resources/
├── ValidationMessages.properties              # 默认（兜底）
├── ValidationMessages_zh_CN.properties         # 简体中文
└── ValidationMessages_en.properties            # 英文
```

```properties
# ValidationMessages_zh_CN.properties
AgeRange.userDTO.age=年龄必须介于 {min} 至 {max} 岁之间
NotBlank.userDTO.username=用户名不能为空

# ValidationMessages_en.properties
AgeRange.userDTO.age=Age must be between {min} and {max}
NotBlank.userDTO.username=Username is required
```

**命名规则**：`{注解全类名}.{校验对象}.{字段}`，Hibernate Validator 按此匹配。比 `message="..."` 硬编码更友好，可由翻译团队维护。

### LocalValidatorFactoryBean 配置

```java
@Bean
public LocalValidatorFactoryBean validator(MessageSource messageSource) {
    LocalValidatorFactoryBean bean = new LocalValidatorFactoryBean();
    // 把 Spring 的 MessageSource 接入 Validator，优先使用 i18n 资源
    bean.setValidationMessageSource(messageSource);
    return bean;
}
```

> 若不显式注册 `LocalValidatorFactoryBean`，Spring Boot 自动配置的版本会自动注入 `MessageSource`，所以 `spring.messages.basename` 配置即可生效。

### MessageInterpolator SPI 自定义插值

当默认占位符语法（`{...}`、`${...}`）不满足需求时，可实现 `MessageInterpolator` SPI：

```java
public class CustomMessageInterpolator implements MessageInterpolator {
    private final MessageInterpolator delegate;

    public CustomMessageInterpolator(MessageInterpolator delegate) {
        this.delegate = delegate;
    }

    @Override
    public String interpolate(String messageTemplate, Context context) {
        // 例：把 {now} 替换为当前时间
        return delegate.interpolate(messageTemplate, context)
                       .replace("{now}", LocalDateTime.now().toString());
    }

    @Override
    public String interpolate(String messageTemplate, Context context, Locale locale) {
        return interpolate(messageTemplate, context);
    }
}

@Bean
public LocalValidatorFactoryBean validator() {
    LocalValidatorFactoryBean bean = new LocalValidatorFactoryBean();
    bean.setMessageInterpolator(new CustomMessageInterpolator(
            HibernateValidator.buildMessageInterpolator(new ResourceBundleMessageSource())));
    return bean;
}
```

### Spring Boot 默认扫描

Spring Boot 约定优于配置：在 `application.yml` 配置基名即可，无需显式 `@Bean`：

```yaml
spring:
  messages:
    basename: messages/i18n/messages   # 支持多基名，逗号分隔
    encoding: UTF-8
    fallback-to-system-locale: false  # 未匹配 Locale 时回退到 messages.properties
```

启动后所有 `@NotBlank(message="用户名不能为空")` 注解都会按 `Locale` 自动查表；Controller 无需手动传 `Locale`，由 `LocaleResolver` 决定（详见 02-web 的 i18n 配置）。

> **注意**：Bean Validation 默认查找 `ValidationMessages` 主名，Spring 接管后才会去 `messages` 基名下找。混用时可在 `Validator` 中同时指定 `setValidationMessageSource(...)`。