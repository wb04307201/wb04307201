# 使用自定义注解进行验证

在Spring Validation中，自定义注解可实现业务特定的验证逻辑（如复杂规则校验）。

### **1. 创建自定义注解**
定义注解元数据，指定验证规则和错误消息模板：
```java
import javax.validation.Constraint;
import javax.validation.Payload;
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

### **2. 实现验证逻辑**
编写`ConstraintValidator`接口的实现类，编写具体校验逻辑：
```java
import javax.validation.ConstraintValidator;
import javax.validation.ConstraintValidatorContext;

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

### **3. 在DTO/Entity中应用注解**
在需要验证的字段上添加自定义注解：
```java
public class UserDTO {
    @AgeRange(min = 18, max = 60, message = "用户年龄不合法")
    private Integer age;
    
    // Getter/Setter
}
```

### **4. 控制器中使用验证**
在Controller方法参数前添加`@Valid`触发验证：
```java
@PostMapping("/users")
public ResponseEntity<?> createUser(@Valid @RequestBody UserDTO userDTO) {
    // 验证通过后的业务逻辑
    return ResponseEntity.ok().build();
}
```

### **5. 自定义错误消息（可选）**
在`src/main/resources/messages.properties`中定义国际化消息：
```properties
AgeRange.userDTO.age=年龄必须介于{min}至{max}岁之间
```
通过`application.properties`配置启用：
```properties
spring.messages.basename=messages
```

### **6. 高级扩展：动态参数验证**
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

### **验证流程解析**
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

### **关键注意事项**
- **空值处理**：自定义验证器不应处理`null`值，交由`@NotNull`单独验证；
- **线程安全**：验证器默认无状态，若需状态管理需自行保证线程安全；
- **分组验证**：通过`groups`属性指定场景，配合`@Validated(groups=Group.class)`使用；
- **性能优化**：复杂验证逻辑建议异步执行或缓存结果。

通过自定义注解，可将业务规则封装为可复用的验证组件，提升代码可维护性。结合Spring Validation的自动配置，可快速构建健壮的参数验证体系。