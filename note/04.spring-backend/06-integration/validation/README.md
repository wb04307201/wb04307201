<!--
module:
  parent: spring
  slug: spring/validation
  type: article
  category: 主模块子文章
  summary: Spring Validation 校验框架
-->

# Spring Validation 校验框架

> 基于 JSR-303/380 规范，通过注解实现 Controller/Service 参数校验

---
---

## 导航

| 序号 | 主题 | 核心内容 |
|------|------|---------|
| 1 | [annotations-and-usage.md](validation-annotations-and-usage.md) | JSR-303/380 标准注解、Hibernate Validator、`@Valid` vs `@Validated` |
| 2 | [custom-validator.md](custom-validator.md) | 自定义约束注解 + Validator 实现类 + 错误消息 |
| 3 | [cross-field.md](cross-field.md) | 跨字段组合校验、容器元素校验（`@Valid` 级联）|

---

## 知识脉络

```mermaid
graph TB
    A[Spring Validation] --> B[JSR-303/380 规范]
    A --> C[Spring 集成]
    A --> D[高级校验]

    B --> B1[基础注解<br/>@NotNull @NotBlank @Size @Email]
    B --> B2[Hibernate Validator<br/>具体实现]

    C --> C1[@Valid JSR 标准]
    C --> C2[@Validated Spring 扩展<br/>支持分组校验]
    C --> C3[MethodArgumentNotValidException]

    D --> D1[自定义 Validator<br/>约束注解 + 实现类]
    D --> D2[跨字段校验<br/>多字段组合验证]
    D --> D3[级联校验<br/>@Valid 嵌套对象]
```

---

## 核心注解速查

| 注解 | 作用 | 适用类型 |
|------|------|---------|
| `@NotNull` | 不能为 null | 任意类型 |
| `@NotBlank` | 不能为 null 且 trim 后非空 | String |
| `@NotEmpty` | 不能为 null 且非空集合/字符串 | String / Collection / Map / Array |
| `@Size(min, max)` | 长度/大小范围 | String / Collection / Map / Array |
| `@Min` / `@Max` | 数值范围 | 数值类型 |
| `@Email` | 邮箱格式校验 | String |
| `@Pattern` | 正则表达式匹配 | String |

## 触发方式对比

| 触发方式 | 来源 | 分组支持 | 嵌套校验 |
|----------|------|---------|---------|
| `@Valid` | JSR-303 标准 | 不支持 | 支持（级联）|
| `@Validated` | Spring 扩展 | 支持（分组）| 需配合 `@Valid` |

## 最小可运行示例（❌/✅ 对比）

**反模式**：Controller / Service 方法参数上**漏加 `@Valid`**，注解完全不会生效！

```java
// ❌ 反例：注解写了，但参数前未加 @Valid —— 校验永远不触发
@PostMapping("/users")
public UserDTO create(@RequestBody UserDTO body) {  // 缺 @Valid
    return userService.save(body);
}

public class UserDTO {
    @NotBlank private String name;                  // 永远不会被检查！
    @Email    private String email;
}
```

```java
// ✅ 正例：参数前加 @Valid 触发方法参数校验；嵌套对象再加一层 @Valid 级联
@PostMapping("/users")
public UserDTO create(@RequestBody @Valid UserDTO body) {
    return userService.save(body);
}

public class UserDTO {
    @NotBlank
    private String name;

    @Email
    private String email;

    @Valid
    @NotNull
    private AddressDTO address;     // 嵌套对象级联校验
}
```

校验失败时 Spring 抛 `MethodArgumentNotValidException`，由 `@RestControllerAdvice` 统一捕获并返回 HTTP 400，详见 [`异常处理`](../../01-core/exception-handling.md)。

## 版本演进与触发原理（一句话定位）

- **JSR-303 → JSR-380**：Bean Validation 从"基础注解集合（`@NotNull`/`@Size`）"演进为"统一规范、明确参数类型约束、跨字段 `@AssertTrue`"；**`Hibernate Validator 6+`** 是当前主流实现。
- **Controller 触发链**：`@RequestBody` 反序列化完成 → `RequestResponseBodyMethodProcessor` 调用 `Validator` → 失败抛 `MethodArgumentNotValidException`。
- **方法级触发**：方法参数前加 `@Validated` + Spring AOP 由 **`MethodValidationPostProcessor`** 把 Bean 包装成代理，调用前拦截（注意：**自调用 `this.foo()` 不走代理**，需要通过容器注入引用或 `AopContext.currentProxy()`）。

---

## 相关章节

- 上游：[`06 集成组件`](../README.md) — Validation / Retry / StateMachine / Batch
- 关联：[`02 Web 层`](../../02-web/README.md) — Validation 大量用于 Controller 参数
- 关联：[`异常处理`](../../01-core/exception-handling.md) — 捕获 `MethodArgumentNotValidException` 返回 400
- 关联：[`08 注解速查`](../../08-annotations/README.md) — 相关注解索引
- 下钻：[注解与使用](validation-annotations-and-usage.md) · [自定义验证器](custom-validator.md) · [跨字段校验](cross-field.md)

---

> 建议路径：从 [注解与使用](validation-annotations-and-usage.md) 开始 → 掌握基础后学习 [自定义验证器](custom-validator.md) → 最后看 [跨字段校验](cross-field.md)

← [返回: Spring 全家桶 · validation](../README.md)
