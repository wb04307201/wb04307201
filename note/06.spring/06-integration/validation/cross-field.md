# 跨字段校验（Cross-Field Validation）

单个字段上的 `@NotBlank`、`@Size` 等注解只能看到自身值，业务中"开始日期必须早于结束日期"、"两次输入密码必须一致"等规则需要**跨字段**或**类级别**校验。本节介绍四种主流方案。

## 一、@ScriptAssert（Hibernate Validator）

`@ScriptAssert` 在类级别用一个脚本引擎（JSR-223，如 JavaScript、Groovy、Kotlin）写出跨字段表达式：

```java
@ScriptAssert(lang = "javascript",
              script = "_.startDate.isBefore(_.endDate)",
              message = "开始日期必须早于结束日期")
public class DateRangeDTO {
    private LocalDate startDate;
    private LocalDate endDate;
}
```

- `_.fieldName` 引用同对象字段。
- 失败时抛 `ConstraintViolation` 指向类本身（`propertyPath` 为空）。
- **优点**：零代码、声明式。**缺点**：脚本无 IDE 支持、调试困难、性能略低（每次校验启动脚本引擎），复杂规则不推荐。

## 二、自定义 ConstraintValidator（**类级别，推荐**）

JSR-303 设计的限制：字段级 `ConstraintValidator` **拿不到 root bean**（Bean Validation 规范按字段粒度调度，验证器方法只接收单个字段值），所以"字段级跨字段校验"本质上是伪命题。**推荐用类级别注解**，验证器直接持有整个对象引用：

```java
@Constraint(validatedBy = DateRangeValidator.class)
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface ValidDateRange {
    String message() default "开始日期必须早于结束日期";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

@Component
public class DateRangeValidator
        implements ConstraintValidator<ValidDateRange, DateRangeDTO> {

    @Override
    public boolean isValid(DateRangeDTO dto, ConstraintValidatorContext ctx) {
        if (dto == null) return true;
        if (dto.getStartDate() == null || dto.getEndDate() == null) return true;
        boolean ok = dto.getStartDate().isBefore(dto.getEndDate());
        if (!ok) {
            ctx.disableDefaultConstraintViolation();
            ctx.buildConstraintViolationWithTemplate(ctx.getDefaultConstraintMessageTemplate())
               .addPropertyNode("endDate")    // 把错误定位到具体字段
               .addConstraintViolation();
        }
        return ok;
    }
}

@ValidDateRange
public class DateRangeDTO {
    private LocalDate startDate;
    private LocalDate endDate;
}
```

`addPropertyNode("endDate")` 让前端能精确定位错误字段。

## 三、@Valid 传播到 List / Set 元素

Bean Validation 2.0 起支持容器元素校验：

```java
public class OrderDTO {
    @NotEmpty
    @Valid                                   // 触发对 List 中每个元素的校验
    private List<@Valid OrderItemDTO> items; // 字段 + 元素类型双重 @Valid
}

public class OrderItemDTO {
    @NotBlank
    private String sku;

    @Min(1)
    private Integer quantity;
}
```

`List<@Valid OrderItemDTO>` 会在校验 `OrderDTO` 时递归校验每个 `OrderItemDTO`。集合自身校验用 `@NotEmpty`、元素校验用 `@Valid`，两者独立。

支持 `List`、`Set`、`Map<K, V>`（V 上可加 `@Valid`）、数组等。

## 四、@AssertTrue / @AssertFalse 自定义逻辑

Bean Validation 提供了两个轻量级注解，要求方法返回 `boolean`：

```java
public class SignupDTO {
    @NotBlank
    private String password;

    @NotBlank
    private String confirmPassword;

    @AssertTrue(message = "两次密码必须一致")
    public boolean isPasswordMatched() {
        return Objects.equals(password, confirmPassword);
    }
}
```

- 方法名遵循 JavaBean 规范（`isXxx` / `getXxx`）。
- 无注解时仍会被 `@Valid` 触发校验。
- 适合单 DTO 内 1-2 条简单规则；规则多时升级为 `ConstraintValidator`。

## 五、选型对照

| 方案 | 适用场景 | 复杂度 | 推荐度 |
|------|---------|:-----:|:-----:|
| `@ScriptAssert` | 一行表达式、临时规则 | 低 | 谨慎 |
| 类级 `@Constraint` + 自定义 `ConstraintValidator` | 多字段组合、复杂业务规则 | 中 | 推荐 |
| `@Valid` 容器元素 | 集合/嵌套对象递归 | 低 | 推荐 |
| `@AssertTrue` 方法 | 简单布尔规则、即时验证 | 低 | 推荐 |

> 多场景分组请结合 [validation-annotations-and-usage.md 第 7 节](validation-annotations-and-usage.md#7-分组校验与-groupsequence)。
