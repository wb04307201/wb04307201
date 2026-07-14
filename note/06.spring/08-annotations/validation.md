# 校验注解

> ⬅️ [返回注解速查](../README.md) | [Web 注解](web.md)

本节是 `@Valid` / `@Validated` 与 JSR-303 常见约束注解的速查手册。**深读请前往 [06-integration/validation](../06-integration/validation/validation-annotations-and-usage.md)**。

---

## 🎯 一句话定位

**校验注解 = "检查参数是否合法"**——`@Valid`（JSR-303）触发标准 Bean Validation，`@Validated`（Spring）支持**分组校验**和**方法级别校验**。

---

## 一、@Valid vs @Validated

| 维度 | @Valid (JSR-303) | @Validated (Spring) |
|:-----|:-----------------|:---------------------|
| **来源** | `jakarta.validation` | `org.springframework.validation` |
| **分组校验** | ❌ 不支持 | ✅ 支持 `@Validated({Group.class})` |
| **方法级别校验** | ❌ 需 @Executable | ✅ 直接放方法参数 |
| **嵌套校验** | ✅ 字段上加 `@Valid` | ✅ 同 |
| **典型场景** | Controller 入参（基础场景） | 复杂场景（多分组、Service 层校验） |

```java
@RestController
public class UserController {

    @PostMapping("/users")
    public User create(@Valid @RequestBody UserDTO dto) { ... }   // @Valid：基础校验

    @PostMapping("/users/v2")
    public User createV2(@Validated({Create.class}) @RequestBody UserDTO dto) { ... }   // @Validated：分组校验
}
```

---

## 二、嵌套校验（级联 @Valid）

> 想递归校验对象内的对象，**必须**在字段上加 `@Valid`，否则内层不校验。

```java
public class OrderDTO {
    @NotNull
    private Long id;

    @Valid                       // ← 关键：触发嵌套校验
    @NotNull
    private AddressDTO address;  // AddressDTO 内部的 @NotBlank 等才会生效
}

public class AddressDTO {
    @NotBlank
    private String street;
}
```

> 📌 集合字段同样需要 `@Valid`：
> ```java
> @Valid
> private List<@Valid ItemDTO> items;
> ```

---

## 三、分组校验

> 同一个 DTO 在不同场景下校验规则不同（如 `Create` 必填、`Update` 不必填）。

```java
public class UserDTO {
    @NotNull(groups = Update.class)        // Update 分组必填
    private Long id;

    @NotBlank(groups = {Create.class, Update.class})   // 两组都必填
    private String username;

    @Email(groups = Create.class)           // 只在 Create 分组校验
    private String email;
}

public interface Create {}
public interface Update {}
```

```java
// Controller
@PostMapping("/users")
public User create(@Validated(Create.class) @RequestBody UserDTO dto) { ... }

@PutMapping("/users/{id}")
public User update(@PathVariable Long id, @Validated(Update.class) @RequestBody UserDTO dto) { ... }
```

> 💡 进阶：`@GroupSequence` 控制分组顺序（前一组的失败会跳过后续组）。详见 [validation 分组章节](../06-integration/validation/validation-annotations-and-usage.md)。

---

## 四、Service / 方法级别校验

> `@Validated` 放在类上可触发方法参数校验（需配合 AOP 异常处理 `ConstraintViolationException`）。

```java
@Service
@Validated
public class UserService {

    public void updateEmail(@NotNull Long userId, @Email String email) {
        // 方法参数校验，违反时抛 ConstraintViolationException
    }
}
```

---

## 五、JSR-303 常用约束注解速查

### 1. 通用

| 注解 | 作用 | 类型 |
|:-----|:-----|:-----|
| `@NotNull` | 不为 null | Object |
| `@NotEmpty` | 不为 null 且 size > 0 | String / Collection / Map / Array |
| `@NotBlank` | 不为 null 且 trim 后 length > 0 | String |
| `@Null` | 必须为 null | Object |
| `@AssertTrue` | 必须为 true | boolean |
| `@AssertFalse` | 必须为 false | boolean |

### 2. 数值

| 注解 | 作用 | 类型 |
|:-----|:-----|:-----|
| `@Min(value)` | 大于等于 value | BigDecimal / BigInteger / 整型 / String |
| `@Max(value)` | 小于等于 value | 同上 |
| `@DecimalMin(value)` | 同 Min，支持小数字面量 | BigDecimal 等 |
| `@DecimalMax(value)` | 同 Max | 同上 |
| `@Positive` | 正数 | 数值 |
| `@PositiveOrZero` | 正数或 0 | 数值 |
| `@Negative` | 负数 | 数值 |
| `@NegativeOrZero` | 负数或 0 | 数值 |
| `@Digits(integer, fraction)` | 整数位 / 小数位 | 数值 |

### 3. 字符串 / 格式

| 注解 | 作用 |
|:-----|:-----|
| `@Size(min, max)` | 长度范围（String/Collection/Map/Array） |
| `@Pattern(regexp)` | 必须匹配正则 |
| `@Email` | 合法邮箱 |
| `@Length(min, max)` | （Hibernate Validator）字符长度 |
| `@URL` | 合法 URL |

### 4. 时间

| 注解 | 作用 |
|:-----|:-----|
| `@Past` | 必须是过去时间 |
| `@PastOrPresent` | 过去或现在 |
| `@Future` | 必须是未来时间 |
| `@FutureOrPresent` | 未来或现在 |

### 5. 集合 / Map

| 注解 | 作用 |
|:-----|:-----|
| `@Size(min, max)` | 元素数量 |
| `@NotEmpty` | 不为空 |

> 💡 Hibernate Validator 还提供 `@Range` / `@Length` / `@URL` / `@CodePointLength` / `@UniqueElements` 等扩展。

---

## 六、典型使用模板

```java
public class CreateUserRequest {

    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度 3-20")
    private String username;

    @NotBlank
    @Email(message = "邮箱格式不合法")
    private String email;

    @NotBlank
    @Pattern(regexp = "^(?=.*[A-Za-z])(?=.*\\d).{8,}$", message = "密码需 8 位以上且含字母数字")
    private String password;

    @Min(value = 0, message = "年龄不能小于 0")
    @Max(value = 150, message = "年龄不能大于 150")
    private Integer age;

    @Valid                                   // 嵌套校验
    private List<@Valid AddressDTO> addresses;
}
```

```java
@RestController
@RequestMapping("/users")
public class UserController {

    @PostMapping
    public Result create(@Valid @RequestBody CreateUserRequest req) {
        // 校验失败时，Spring 抛 MethodArgumentNotValidException
        // 配合 @ControllerAdvice 统一处理 → 见 [exception.md](exception.md)
    }
}
```

---

## 🤔 思考

1. **@Valid 加在哪里？** 加在方法参数前（@RequestBody 之前），触发该对象的字段约束。
2. **校验失败抛什么异常？** Controller 入口抛 `MethodArgumentNotValidException`；方法级抛 `ConstraintViolationException`——需各自在 `@ExceptionHandler` 中处理。
3. **分组校验与 nullable 字段？** `Update` 分组时 `id` 必填但其他字段可选；DTO 可用 `@Null(groups = Create.class)` 显式拒绝某些字段。
4. **业务校验放哪？** 简单格式（邮箱、手机号）放 JSR-303；业务规则（"该邮箱已注册"）放 Service 层抛业务异常。

---

## 深入阅读

- [06-integration/validation/validation-annotations-and-usage](../06-integration/validation/validation-annotations-and-usage.md) — 校验完整指南（含自定义注解）
- [06-integration/validation/custom-validator](../06-integration/validation/custom-validator.md) — 自定义校验器
- [06-integration/validation/cross-field](../06-integration/validation/cross-field.md) — 跨字段校验

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [Web 注解](web.md) — @RequestBody + @Valid
- [异常处理](exception.md) — @ControllerAdvice 统一处理校验异常
