<!--
module:
  parent: spring
  slug: spring/aop/pointcut-expression
  type: article
  category: 主模块子文章
  summary: Spring AOP 切点表达式语法速查：execution/within/this/target/args/@annotation/bean 7 大表达式 + ❌/✅ 常见反例对比。
  depth: ⭐⭐⭐
-->

# 切点表达式语法

> ⬅️ [返回 AOP 总览](README.md) | [通知顺序与最佳实践](advice-order-and-best-practices.md)

Spring AOP 使用 **AspectJ 风格的表达式**来定义切入点（Pointcut），通过组合各种元素来精确定位特定的连接点。

---

## 🎯 一句话定位

**切点表达式 = "在哪里切"**——`execution` 按方法签名切（最常用），`within` 按类/包切，`bean` 按 Bean 名称切，`@annotation` 按注解切。4 类可组合使用（`&&`/`||`/`!`）。

---

## 一、基本语法结构

### execution 表达式（最常用）

```text
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

```text
execution(public void com.pack.service.UserService.doSomething())
```

### 2. 使用通配符

```text
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

## 八、常见 ❌/✅ 反例对比（避坑指南）

> 切点表达式写错通常**不会抛异常**（Spring 默认懒解析），只会"切不到"或"切到不该切的"。下面是 7 大表达式最常见的反例与正例。

### 8.1 execution — 漏空格 / 错用通配符

```java
// ❌ 反例 1：* 与类型之间漏空格 → 解析失败，启动时报 PointcutExpression 语法错
@Pointcut("execution(*UserService.*(..))")
public void wrong() {}

// ✅ 正例：* 与 UserService 之间必须有空格
@Pointcut("execution(* UserService.*(..))")
public void correct() {}

// ❌ 反例 2：想匹配任意包任意方法，写成 *.*.* 只能匹配 3 层包
@Pointcut("execution(* *.*.*(..))")  // 只匹配 com.xx.Xx.method()
public void wrong() {}

// ✅ 正例：.. 匹配任意层包
@Pointcut("execution(* com..*.*(..))")
public void correct() {}

// ❌ 反例 3：参数列表漏 ..
@Pointcut("execution(* UserService.save())")  // 只匹配无参的 save()
public void wrong() {}

// ✅ 正例：用 (..) 匹配任意参数
@Pointcut("execution(* UserService.save(..))")
public void correct() {}
```

### 8.2 within — `..` 与 `*` 混用错误

```java
// ❌ 反例：想匹配 com.pack 及其子包，写成 com.pack.* → 只匹配一层子包
@Pointcut("within(com.pack.*)")  // 匹配 com.pack.service，但不匹配 com.pack.service.impl
public void wrong() {}

// ✅ 正例：用 ..* 匹配多层子包
@Pointcut("within(com.pack..*)")
public void correct() {}
```

### 8.3 this / target — 代理对象与目标对象混淆

```java
// ❌ 反例 1：this(UserService) 在 JDK 动态代理下永远不匹配
// 因为代理对象是 $Proxy0，不是 UserService 类型
@Pointcut("this(UserService)")  // JDK 代理 → 永远 false
public void wrongJDK() {}

// ✅ 正例：CGLIB 代理下 this(子类) 才能匹配；JDK 代理改用 target
@Pointcut("target(UserService)")  // 目标对象类型匹配，JDK/CGLIB 都生效
public void correct() {}

// ❌ 反例 2：把 this/target 当 Bean 名称用
@Pointcut("this(userService)")  // 编译期不会报错，但运行永远不命中
public void wrong() {}

// ✅ 正例：Bean 名称匹配必须用 bean 表达式
@Pointcut("bean(userService)")
public void correct() {}
```

### 8.4 args — 与 execution 参数的区别

```java
// ❌ 反例：args 是按**运行时参数类型**匹配，不是按方法签名
// 想拦截 save(User) 方法，但 args 是 JoinPoint 入参绑定
@Pointcut("execution(* UserService.save(User)) && args(user)")
public void confuse() {}

// ✅ 正例：execution 管方法签名，args 只做参数绑定
@Pointcut("execution(* UserService.save(..)) && args(user)")
public void correct(User user) {}

// ❌ 反例：args 用全限定名做精确匹配（实际可简写）
@Pointcut("args(com.pack.model.User)")
public void verbose() {}

// ✅ 正例：args 默认就是按运行时类型匹配，简单名即可
@Pointcut("args(user)")
public void correct(User user) {}
```

### 8.5 @annotation — 注解参数绑定遗漏

```java
// ❌ 反例：@annotation 想拿注解属性，但忘了加 binding 参数
@Pointcut("@annotation(AuditLog)")
@Around("auditLog()")
public Object wrong(ProceedingJoinPoint pjp) {
    // 无法拿到 module 属性
    return pjp.proceed();
}

// ✅ 正例：表达式与方法参数同名绑定
@Pointcut("@annotation(auditLog)")
@Around("auditLog() && @annotation(auditLog)")
public Object correct(ProceedingJoinPoint pjp, AuditLog auditLog) throws Throwable {
    log.info("module: {}", auditLog.module());  // 可访问
    return pjp.proceed();
}

// ❌ 反例：@annotation 用 @ 符号 + 简写
@Pointcut("@annotation(@AuditLog)")  // 语法错
public void wrong() {}

// ✅ 正例：@annotation 内部不加 @
@Pointcut("@annotation(com.pack.AuditLog)")
public void correct() {}
```

### 8.6 bean — 名称匹配 vs 类型匹配

```java
// ❌ 反例 1：bean() 内写类名（启动不报错，但永远不命中）
@Pointcut("bean(UserService)")
public void wrong() {}

// ✅ 正例：bean 按 Bean 名称（默认是类名首字母小写，或 @Service("xxx") 指定）
@Pointcut("bean(userService)")
public void correct() {}

// ❌ 反例 2：通配符用了 ..
@Pointcut("bean(*..Service)")  // 语法错，bean 只支持 *
public void wrong() {}

// ✅ 正例：bean 表达式只支持 * 通配
@Pointcut("bean(*Service)")
public void correct() {}
```

### 8.7 组合运算符（XML vs Annotation 写法）

```java
// ❌ 反例：在 @Pointcut 注解里写 and / or
@Pointcut("execution(* UserService.*(..)) and within(com.pack..*)")
public void wrong() {}

// ✅ 正例：注解里用 && || !
@Pointcut("execution(* UserService.*(..)) && within(com.pack..*)")
public void correct() {}

// ⚠️ 注意：XML 配置里反过来必须用 and / or / not（XML 实体要求）
// <aop:config>
//   <aop:pointcut id="pc"
//     expression="execution(* UserService.*(..)) and within(com.pack..*)"/>
// </aop:config>
```

### 8.8 自调用失效（与切点表达式的隐性坑）

```java
// ❌ 反例：切点表达式写得再准，自调用就绕过代理
@Service
public class OrderService {
    @Transactional
    public void createOrder() {
        saveOrder();  // ❌ 直接 this 调用 → 事务失效
    }

    @Transactional
    public void saveOrder() {
        // ...
    }
}

// ✅ 正例：通过代理对象调用
@Service
public class OrderService {
    @Autowired
    private OrderService self;  // ✅ 注入自身代理

    @Transactional
    public void createOrder() {
        self.saveOrder();  // ✅ 走代理 → 事务生效
    }

    @Transactional
    public void saveOrder() {
        // ...
    }
}
```

---

## 九、性能优化建议

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
5. **为什么 this(UserService) 在 JDK 代理下失效？** JDK 动态代理生成的类实现 UserService 但不是 UserService 子类，`this()` 是运行时 instanceof 检查，对 `$Proxy0` 返回 false。要匹配目标对象用 `target()`。

---

## 相关章节

- ⬅️ [返回 AOP 总览](README.md)
- [通知顺序与最佳实践](advice-order-and-best-practices.md) — 多切面顺序 + `@Order` + 自调用失效
- [08 注解/AOP 注解](../../08-annotations/aop.md) — `@Aspect` / `@Pointcut` 注解全解
- [03 数据层/事务失效](../../04-data/transaction/failure-cases.md) — 自调用绕过代理导致 `@Transactional` 失效
- [01.java/并发总览](../../../01.java-and-jvm/03-concurrency/README.md) — AOP 代理与并发原语都涉及"对象语义 vs 运行时语义"的区分

← [返回: aop](../README.md) | [返回: 01-core](../../README.md) | [返回: 04.spring-backend](../../../README.md)