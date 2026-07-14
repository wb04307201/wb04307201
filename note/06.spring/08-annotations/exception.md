# 异常处理注解

> ⬅️ [返回注解速查](../README.md) | [Web 注解](web.md) | [AOP 注解](aop.md)

本节介绍 Spring 异常处理的核心注解：`@ControllerAdvice` + `@ExceptionHandler` 组合实现**全局异常处理**。

---

## 🎯 一句话定位

**异常处理注解 = 全局捕获 + 统一响应**——`@ControllerAdvice` 声明全局异常处理类（拦截所有 `@Controller` 的异常），`@ExceptionHandler` 声明处理方法（按异常类型匹配）。

---

## @ControllerAdvice + @ExceptionHandler

> 通常组合使用，处理全局异常，避免每个 Controller 写 `try-catch`。

```java
@ControllerAdvice
@Configuration
@Slf4j
public class GlobalExceptionConfig {

    private static final Integer GLOBAL_ERROR_CODE = 500;

    @ExceptionHandler(value = Exception.class)
    @ResponseBody
    public void exceptionHandler(HttpServletRequest request, HttpServletResponse response, 
                                 Exception e) throws Exception {
        log.error("【统一异常处理器】", e);
        ResultMsg<Object> resultMsg = new ResultMsg<>();
        resultMsg.setCode(GLOBAL_ERROR_CODE);
        if (e instanceof CommonException) {
            CommonException ex = (CommonException) e;
            if (ex.getErrCode() != 0) {
                resultMsg.setCode(ex.getErrCode());
            }
            resultMsg.setMsg(ex.getErrMsg());
        } else {
            resultMsg.setMsg(CommonErrorMsg.SYSTEM_ERROR.getMessage());
        }
        WebUtil.buildPrintWriter(response, resultMsg);
    }
}
```

---

## 注解详解

### @ControllerAdvice

| 维度 | 说明 |
|------|------|
| **作用** | 声明一个全局控制器增强类 |
| **作用域** | 默认对所有 `@Controller`（含 `@RestController`）生效 |
| **可限制范围** | 通过 `basePackages`、`assignableTypes`、`annotations` 限制 |
| **典型场景** | 全局异常处理、全局数据绑定、全局预处理 |

### @ExceptionHandler

| 维度 | 说明 |
|------|------|
| **作用** | 声明处理特定异常类型的方法 |
| **匹配规则** | 按方法参数中的异常类型精确匹配 |
| **优先级** | 局部（@Controller 内的 @ExceptionHandler） > 全局（@ControllerAdvice） |
| **多异常处理** | 一个方法可声明多个异常类型：`@ExceptionHandler({A.class, B.class})` |

---

## 常见模式

### 1. 业务异常 → 返回业务码

```java
@ExceptionHandler(BusinessException.class)
@ResponseBody
public Result<Object> handleBusiness(BusinessException e) {
    return Result.fail(e.getCode(), e.getMessage());
}
```

### 2. 参数校验异常 → 提取字段错误

```java
@ExceptionHandler(MethodArgumentNotValidException.class)
@ResponseBody
public Result<Object> handleValidation(MethodArgumentNotValidException e) {
    Map<String, String> errors = new HashMap<>();
    e.getBindingResult().getFieldErrors().forEach(err -> 
        errors.put(err.getField(), err.getDefaultMessage()));
    return Result.fail(400, "参数校验失败").with("errors", errors);
}
```

### 3. 兜底异常 → 500 错误

```java
@ExceptionHandler(Exception.class)
@ResponseBody
public Result<Object> handleAny(Exception e) {
    log.error("系统异常", e);
    return Result.fail(500, "系统繁忙，请稍后再试");
}
```

---

## 进阶：RestControllerAdvice

> Spring 5+ 提供 `@RestControllerAdvice` = `@ControllerAdvice` + `@ResponseBody`，**所有方法的返回值默认序列化为 JSON**（无需每个方法加 @ResponseBody）。

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public Result<Object> handleBusiness(BusinessException e) {
        return Result.fail(e.getCode(), e.getMessage());
    }
    // 无需 @ResponseBody
}
```

> 📌 现代项目**推荐用 @RestControllerAdvice**。

---

## 异常处理优先级

```mermaid
graph TB
    Req[请求] --> Throw[抛出异常]
    Throw --> Local{Controller 内的<br/>@ExceptionHandler<br/>是否匹配?}
    Local -->|匹配| LocalHandler[局部处理]
    Local -->|不匹配| Global{@ControllerAdvice<br/>是否匹配?}
    Global -->|匹配| GlobalHandler[全局处理]
    Global -->|不匹配| Default[Spring 默认处理<br/>500 错误]

    classDef match fill:#e8f5e9,stroke:#388e3c
    classDef miss fill:#ffebee,stroke:#c62828
    class LocalHandler,GlobalHandler match
    class Default miss
```

---

## 🤔 思考

1. **为什么 @ExceptionHandler 方法参数列表对返回值影响很大？** 因为 Spring 根据参数类型匹配异常（如方法参数是 `BusinessException` 就只处理 `BusinessException`）。
2. **能不能完全替代 Filter 中的异常处理？** 不能。Filter 抛出的异常不经过 DispatcherServlet，所以 @ControllerAdvice 抓不到，需要 `HandlerExceptionResolver` 或在 Filter 中手动处理。
3. **为什么用 @RestControllerAdvice 而不是 @ControllerAdvice？** 现代项目都是 JSON 接口，前者更简洁。
4. **异常处理要不要打日志？** 必须！尤其是兜底异常，否则线上问题难以排查。

---

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [01 核心容器/异常处理](../01-core/exception-handling.md) — 完整的异常处理机制
- [Web 注解](web.md) — @Controller、@RestController
- [06 集成组件/Validation](../06-integration/validation/validation-annotations-and-usage.md) — 校验异常的处理
