# 切点表达式语法

> ⬅️ [返回 AOP 总览](README.md) | [通知顺序与最佳实践](advice-order-and-best-practices.md)

Spring AOP 使用 **AspectJ 风格的表达式**来定义切入点（Pointcut），通过组合各种元素来精确定位特定的连接点。

---

## 🎯 一句话定位

**切点表达式 = "在哪里切"**——`execution` 按方法签名切（最常用），`within` 按类/包切，`bean` 按 Bean 名称切，`@annotation` 按注解切。4 类可组合使用（`&&`/`||`/`!`）。

---

## 一、基本语法结构

### execution 表达式（最常用）

```
execution(modifiers? return_type method_name(param_type1, param_type2, …))
```

| 元素 | 含义 | 是否必填 |
|------|------|---------|
| `modifiers` | 修饰符（public/protected/private） | 否 |
| `return_type` | 返回类型（可用 `*` 通配） | 是 |
| `method_name` | 方法名（可用 `*` 通配） | 是 |
| `param_type` | 参数类型列表 | 是 |

### 关键通配符

| 通配符 | 含义 |
|--------|------|
| `*` | 匹配任意**单层**字符序列（不含 `.`） |
| `..` | 匹配任意**多层**字符序列（含 `.`），也匹配任意数量参数 |

---

## 二、execution 表达式

### 1. 精确匹配

```
execution(public void com.pack.service.UserService.doSomething())
```

### 2. 使用通配符

```
execution(* com.pack.service.*.*(..))
```

含义：**匹配 com.pack.service 包下任何类的任何方法**（任意返回类型、任意方法名、任意参数）。

### 3. execution 表达式速查

| Pointcut 表达式 | 说明 |
|-----------------|------|
| `execution(* com.pack.UserService.*(..))` | 匹配指定包和类中的**所有方法** |
| `execution(*UserService.*(..))` | 匹配**同一包**和指定类中的所有方法 |
| `execution(public *UserService.*(..))` | 匹配 `UserService` 中的所有**公共**方法 |
| `execution(public User UserService.*(..))` | 匹配 `UserService` 中所有返回类型为 `User` 的公共方法 |
| `execution(public User UserService.*(User, ..))` | 匹配**第一个参数为 User**、返回类型为 User 的公共方法 |
| `execution(public User UserService.*(User, Integer))` | 匹配**两个指定参数**、返回类型为 User 的公共方法 |

---

## 三、within 表达式（按类/包匹配）

> `within` 比 `execution` 更简洁——**只关心类/包，不关心方法签名**。

| Pointcut 表达式 | 说明 |
|-----------------|------|
| `within(com.pack.*)` | 匹配包 `com.pack.*` 中**所有类的所有方法** |
| `within(com.pack..*)` | 匹配 `com.pack` 及其**所有子包**中的类的方法 |
| `within(com.pack.UserService)` | 匹配**指定类**的所有方法 |
| `within(UserService)` | 匹配**当前包**中 `UserService` 类的所有方法 |
| `within(IUserService+)` | 匹配指定接口**所有实现类**的所有方法（`+` 表示子类） |

> 💡 `execution` vs `within`：`execution` 按方法签名（方法名+参数），`within` 按类/包。`within` 性能更好（不需要解析方法签名）。

---

## 四、bean 表达式（按 Bean 名称匹配）

> Spring 特有的表达式，**按 Spring 容器中的 Bean 名称匹配**。

| Pointcut 表达式 | 说明 |
|-----------------|------|
| `bean(*Service)` | 匹配 bean 名称**以 Service 结尾**的所有方法 |
| `bean(userService)` | 匹配 bean 名称**为 userService** 的所有方法 |
| `bean(com.pack.service.*)` | 匹配**特定包**中所有 bean 的所有方法 |
| `bean(@PackAnnotation *)` | 匹配带有**特定注解**的 Bean 的所有方法 |

### bean 与 @annotation 联合

```java
// 匹配所有标了 @Service 注解的 Bean
@Around("bean(@org.springframework.stereotype.Service *)")
public Object around(ProceedingJoinPoint pjp) throws Throwable {
    // ...
}
```

---

## 五、组合切点表达式

> 在 AspectJ 中，切点表达式可以与运算符组合使用：

| 运算符 | 含义 |
|--------|------|
| `&&` | 和（同时满足） |
| `\|\|` | 或（满足任一） |
| `!` | 非（取反） |

### 示例

```java
// 匹配名称以 Service 或 DAO 结尾的 Bean 中的所有方法
@Pointcut("bean(*Service) || bean(*DAO)")
public void serviceOrDAO() {}

// 匹配 com.pack.service 包下的所有方法，但排除 UserService
@Pointcut("within(com.pack.service..*) && !execution(* com.pack.service.UserService.*(..))")
public void serviceExcludeUser() {}
```

### 完整组合示例

```java
@Aspect
@Component
public class ServiceLogAspect {

    // 切点：service 包下所有 public 方法，参数包含 User
    @Pointcut("execution(public * com.pack.service..*.*(com.pack.model.User, ..))")
    public void userRelatedMethods() {}

    // 切点：所有 @Cacheable 注解的方法
    @Pointcut("@annotation(org.springframework.cache.annotation.Cacheable)")
    public void cacheableMethods() {}

    // 组合：service 包 + 有 @Cacheable 注解
    @Pointcut("userRelatedMethods() && cacheableMethods()")
    public void combinedPointcut() {}

    @Before("combinedPointcut()")
    public void log() {
        System.out.println("Service method with @Cacheable called");
    }
}
```

---

## 六、@annotation 表达式（按方法注解匹配）

> 这是**最实用**的切点——按自定义注解切。

```java
// 1. 自定义注解
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface AuditLog {
    String module();
}

// 2. 切点：所有标了 @AuditLog 的方法
@Pointcut("@annotation(com.pack.annotation.AuditLog)")
public void auditLogMethods() {}

@Around("auditLogMethods() && @annotation(auditLog)")
public Object around(ProceedingJoinPoint pjp, AuditLog auditLog) throws Throwable {
    log.info("Audit module: {}", auditLog.module());
    return pjp.proceed();
}

// 3. 使用
@AuditLog(module = "ORDER")
public Order createOrder(OrderDTO dto) {
    // ...
}
```

---

## 七、切点表达式对比

| 表达式 | 维度 | 性能 | 典型场景 |
|--------|------|------|----------|
| `execution` | 方法签名 | 较慢（需解析方法签名） | 精确控制方法粒度 |
| `within` | 类/包 | 快 | 拦截整个包/类 |
| `bean` | Bean 名称 | 快 | 按 Spring Bean 名称拦截 |
| `@annotation` | 方法注解 | 中 | 拦截自定义注解方法（**最推荐**） |
| `args` | 参数类型 | 中 | 按参数类型拦截 |
| `@within` | 类注解 | 中 | 拦截带特定注解的类 |
| `this` / `target` | 代理对象/目标对象 | 慢 | 复杂 AOP 场景 |

---

## 八、性能优化建议

> ⚠️ 切入点表达式会**影响应用性能**（每次方法调用都要匹配切点）。

1. **优先用 `within` 而非 `execution`**：`within` 是包/类级别匹配，比 `execution` 快。
2. **避免太宽泛的匹配**：不要写 `execution(* *..*(..))`，会匹配所有方法。
3. **优先按注解切**：`@annotation` 性能好且语义清晰。
4. **缓存切点匹配结果**：Spring 内部已对切点解析做了缓存，无需额外处理。

---

## 🤔 思考

1. **execution 和 within 怎么选？** 拦截整个包/类用 `within`，精确方法粒度用 `execution`。
2. **@annotation 比 execution 快吗？** 性能相当，但 `@annotation` 语义更清晰。
3. **bean 表达式能匹配接口吗？** 不能，`bean` 按 Bean 实例名称匹配，接口本身不是 Bean。
4. **& 和 && 等价吗？** XML 中必须用 `and`/`or`/`not`（XML 不支持 `&&`/`||`/`!`）。

---

## 相关章节

- ⬅️ [返回 AOP 总览](README.md)
- [通知顺序与最佳实践](advice-order-and-best-practices.md)
- [08 注解/AOP 注解](../../08-annotations/aop.md)
