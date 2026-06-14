# Spring Validation

> 最后更新: 2026-06-14

Spring Validation 是基于 Java Bean Validation API（JSR 303/380）的规范实现，由 Hibernate Validator 提供具体实现，Spring 框架通过封装使其更易用。

## 1. 核心概念与规范
- **Bean Validation API**：定义标准注解（如 `@NotNull`, `@Size`, `@Email`）和验证接口，实现“约束一次，处处验证”。Hibernate Validator 是其参考实现，支持扩展注解（如 `@NotBlank`）。
- **Spring 集成**：Spring MVC/WebFlux 默认支持，通过 `@Valid`（JSR 标准）或 `@Validated`（Spring 扩展，支持分组）触发验证。验证失败时抛出 `MethodArgumentNotValidException`（Controller）或 `BindException`（方法级），默认返回 HTTP 400 错误。

## 2. 常用注解与场景
- **基础约束**：
    - `@NotNull`：值不能为 `null`；
    - `@NotEmpty`：集合/字符串非空且长度＞0；
    - `@NotBlank`：字符串非空且去除首尾空格后长度＞0；
    - `@Size(min=, max=)`：集合/字符串长度范围；
    - `@Pattern(regex=)`：正则匹配；
    - `@Min(value=)`/`@Max(value=)`：数值范围；
    - `@Email`：邮箱格式验证。
- **嵌套验证**：在嵌套对象字段上使用 `@Valid`（如 `@Valid @NotNull User user`）。
- **分组验证**：通过 `groups` 属性指定验证场景（如 `@NotBlank(groups = UpdateGroup.class)`），结合 `@Validated(UpdateGroup.class)` 按需激活。

## 3. 使用方法
- **Controller 层**：
    - `@RequestBody` + `@Valid`：验证 POST/PUT 请求体（DTO 对象）；
    - `@RequestParam`/`@PathVariable` + `@Validated`：验证 GET 请求参数；
    - 捕获异常：通过 `@ExceptionHandler` 自定义错误响应（如返回 JSON 格式的错误详情）。
- **Service 层**：
    - 在 Service 类或方法上添加 `@Validated`，配合参数注解实现方法级验证（如 `@Size(min=1) String name`）。
- **手动验证**：注入 `Validator` 实例，调用 `validator.validate(object, groups)` 并处理 `Set<ConstraintViolation>` 结果。

## 4. 自定义验证器
- **步骤**：
    1. 创建注解（如 `@AgeRange`），定义 `message` 和 `groups` 属性；
    2. 实现 `ConstraintValidator<A, T>` 接口，重写 `isValid(value, context)` 方法编写逻辑；
    3. 注册到 Spring 容器（通过 `@Component` 或 XML 配置）。
- **示例**：验证用户年龄在 18-60 岁之间，注解与验证器代码需关联。

## 5. 配置与集成
- **Spring Boot**：
    - 依赖：`spring-boot-starter-validation`（自动引入 Hibernate Validator）；
    - 配置：`application.properties` 中可设置全局错误消息（如 `spring.messages.basename=messages`）。
- **全局错误处理**：通过 `@ControllerAdvice + @ExceptionHandler` 统一处理验证异常，返回结构化错误信息（如字段名、错误码、消息）。
- **Thymeleaf 集成**：在表单中使用 `th:errors` 展示验证错误。

## 6. 高级特性
- **级联验证**：集合/数组元素验证（如 `List<@Valid User>`）；
- **方法级验证**：通过 `MethodValidationPostProcessor` 启用 Service 方法参数验证；
- **多场景 DTO**：避免代码重复，可通过分组验证或动态 DTO 设计（如 `UserPostDTO`/`UserPatchDTO`）替代。

**总结**：Spring Validation 通过注解驱动的方式解耦验证逻辑与业务代码，支持灵活扩展（自定义注解、分组、多场景验证），是构建健壮后端接口的关键工具。结合 Spring Boot 的自动配置，可快速集成并实现标准化、可维护的参数验证体系。

## 7. 分组校验与 @GroupSequence

当同一个 DTO 在不同业务场景下需要执行不同的校验规则时（例如 `Create` 与 `Update` 场景），仅靠 `@Valid` 无法精细控制——`@Valid` 会校验所有标注的约束。`@Validated(groups = ...)`（Spring 扩展）允许只校验指定 group 下的约束，`@GroupSequence` 进一步强制约束的执行顺序并在前面 group 失败时短路。

### 7.1 定义 Group 接口

Group 是普通 Java 接口（Marker Interface），仅作为分组标识，无任何方法：

```java
public interface Create extends Default {}
public interface Update extends Default {}
```

### 7.2 在 DTO 字段上指定 group

```java
public class UserDTO {
    @Null(groups = Create.class, message = "新建时 id 必须为空")
    @NotNull(groups = Update.class, message = "更新时 id 不能为空")
    private Long id;

    @NotBlank(groups = {Create.class, Update.class})
    private String username;

    @Email(groups = Create.class)               // 仅创建时校验邮箱
    private String email;

    // 默认组（未指定 groups）等价于 groups = {Default.class}
    @NotNull
    private LocalDateTime createdAt;
}
```

### 7.3 在 Controller 按 group 激活

```java
@RestController
@RequestMapping("/users")
@Validated
public class UserController {

    @PostMapping
    public UserDTO create(@Validated(Create.class) @RequestBody UserDTO dto) {
        // 仅校验 Create 组的约束：username 必填、id 必须为 null、email 格式合法
        return userService.create(dto);
    }

    @PutMapping
    public UserDTO update(@Validated(Update.class) @RequestBody UserDTO dto) {
        // 仅校验 Update 组的约束：id 必填、username 必填
        return userService.update(dto);
    }
}
```

### 7.4 @GroupSequence 强制执行顺序

如果 Create 场景需要"先校验基础字段再校验业务规则"，或者希望"前面 group 失败时不再继续后续 group 校验"，可使用 `@GroupSequence`：

```java
@GroupSequence({Default.class, Create.class, BusinessRule.class})
public interface CreateSequence {}

public class OrderDTO {
    @NotNull                                   // 属 Default 组，先校验
    private Long id;

    @Future                                    // 属 Create 组，第二步校验
    private LocalDate deliveryDate;

    @ScriptAssert(lang = "javascript",
                  script = "...",
                  groups = BusinessRule.class) // 业务规则组，最后执行
    private OrderDTO self;
}
```

激活顺序校验：

```java
@PostMapping("/orders")
public OrderDTO create(@Validated(CreateSequence.class) @RequestBody OrderDTO dto) {
    // 严格按 Default → Create → BusinessRule 顺序执行
    // 任一前置 group 失败，后续 group 不再执行（短路）
    return orderService.create(dto);
}
```

### 7.5 默认 group 与 Default.class

- **未指定 `groups` 属性** 等价于 `groups = {Default.class}`，始终参与校验。
- `@Validated` 不传参时仅校验 `Default` 组的约束。
- 若一个 group 接口 `extends Default`（如 `Create extends Default`），则属于该 group 的字段也属于 `Default` 组——意味着声明 `groups = {Create.class}` 时，Default 组约束仍会执行。

### 7.6 实战案例：同一 DTO 多场景

RESTful 风格中 `POST /users` 与 `PUT /users/{id}` 共用 `UserDTO` 是常见模式：

| 字段 | Create | Update |
|------|:------:|:------:|
| id | 必须 null | 必须非 null |
| username | @NotBlank | @NotBlank |
| email | @Email + @NotBlank | 不校验 |
| password | @NotBlank, @Size(min=8) | 不校验 |

通过分组，两套规则合并到同一 DTO 上，避免维护 `UserCreateDTO` / `UserUpdateDTO` 重复代码。

> **跨字段校验**请参考 [cross-field.md](cross-field.md)。