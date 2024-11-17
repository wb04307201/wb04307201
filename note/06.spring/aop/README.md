# Spring AOP

Spring AOP（面向切面编程）是一种强大的范式，用于模块化应用程序中的横切关注点。切入点（Pointcut）是一组一个或多个连接点（Join
Point）的集合，在这些连接点上应该应用通知（Advice）。连接点是程序执行过程中的一个点，比如方法执行、对象实例化或字段访问。切入点定义了通知执行的时机和位置。

## 切入点表达式语法

Spring AOP 使用 AspectJ 风格的表达式来定义切入点。这种语法涉及组合各种元素以精确定位特定的连接点。

例如，使用execution()来指定方法执行的连接点。其基本语法遵循如下的模式：

`execution(modifiers? return_type method_name(param_type1, param_type2, …))`

示例：

`execution(public void com.pack.service.UserService.doSomething())`

使用通配符匹配多个元素，类似于正则表达式。例如，* 可匹配任意字符序列，..可匹配任意数量的参数，如下示例：

`execution(* com.pack.service.*.*(..))`

使用within()可以指定某一类型或包中的连接点，如下示例：

`within(com.pack.service.*)`

该表达式匹配"com.pack.service"包中的所有方法。

### 匹配特定方法

最典型的点切表达式用于根据方法的签名匹配方法。

| Pointcut 表达式                                       | 说明                                            |
|----------------------------------------------------|-----------------------------------------------|
| execution(* com.pack.UserService.*(..))            | 匹配指定包和类中的所有方法                                 |
| execution(*UserService.*(..))                      | 匹配同一包和指定类中的所有方法                               |
| execution(public *UserService.*(..))               | 匹配UserService中的所有公共方法                         |
| execution(public UserUserService.*(..))            | 匹配UserService中所有返回类型为 User 对象的公共方法            |
| execution(public UserUserService.*(User, ..))      | 匹配UserService中所有返回类型为 User 且第一个参数为 User 的公共方法 |
| execution(public UserUserService.*(User, Integer)) | 匹配UserService中所有返回类型为 User 且带有指定参数的公共方法       |

### with表达式

可以使用 within() 函数拦截类或包中所有方法的执行，如下表格：

| Pointcut 表达式                 | 说明                               |
|------------------------------|----------------------------------|
| within(com.pack.*)           | 匹配包 "com.pack.*"中所有类的所有方法        |
| within(com.pack..*)          | 匹配包"com.pack"中所有类的所有方法，以及所有子包中的类 |
| within(com.pack.UserService) | 匹配指定包中指定类的所有方法                   |
| within(UserService)          | 匹配当前包中指定类的所有方法                   |
| within(IUserService+)        | 匹配指定接口所有实现中的所有方法法                |

### bean表达式

可以使用bean()函数来匹配所有符合指定模式的类中的所有方法。

| Pointcut 表达式             | 说明                                 |
|--------------------------|------------------------------------|
| bean(*Service)           | 匹配 bean 中名称以 "Service"结尾的所有方法      |
| bean(userService)        | 匹配指定 Bean 中名称为 "userService "的所有方法 |
| bean(com.pack.service.*) | 匹配特定包中所有bean的所有方法                  |
| bean(@PackAnnotation *)  | 将所有 Bean 中的所有方法与特定注解相匹配            |

### 组合切点表达式

在 AspectJ 中，点切分表达式可以与运算符 &&（和）、||（或）和 ！(通过一个简单的例子来理解。下面的示例匹配名称以 Service 或 DAO
结尾的 Bean 中的所有方法。

`bean(*Service) || bean(*DAO)`

## @Aspect顺序

假设有这样一个场景。有两个切面分别是LoggingAspect和SecurityAspect，它们都拦截服务包内的方法调用。为了确保在进行安全检查之前生成全面的日志，LoggingAspect应该在SecurityAspect之前执行。

类似地，在应用中还可能有CacheAspect和SecurityAspect。缓存切面（CachingAspect）应该先执行，以便在重复进行安全检查之前，可能从缓存中检索结果。

在这些情况下，明确强制执行切面的顺序是必要的。

### 使用@Order注解

定义切面执行顺序的一种直接方法是利用`@Order`注解。顺序值较低的方面优先执行。

- 相对于其他具有相同顺序值的对象，具有相同顺序值的切面将以任意顺序排序。
- 任何没有提供自己的排序值的切面都会被隐式地分配一个 Ordered.LOWEST_PRECEDENCE 值，从而在所有排序切面都执行完毕后再执行。

示例：

```java

@Aspect
@Order(1)
@Component
public class MyAspect1 {
    // 第一个执行
}

@Aspect
@Order(2)
@Component
public class MyAspect2 {
    // 最后执行
}
```

以上通过`@Order`指定了切面的顺序，值越小越先执行。

### 实现Ordered接口

切面排序的另一种方法是实现`Ordered`接口。这样可以对分配给切面的顺序值进行更多控制，如下示例：

```java

@Aspect
@Component
public class MyAspect1 implements Ordered {
    @Override
    public int getOrder() {
        // 在这里你可以根据一些逻辑判断进行返回值    
        return 1;
    }
    // 第一个执行
}

@Aspect
@Component
public class MyAspect2 implements Ordered {
    @Override
    public int getOrder() {
        return 2;
    }
    // 最后执行
}
```

通过这种实现`Ordered`接口的方式使得顺序可以更加的灵活。

### 完整示例

如下，创建了 LoggingAspect 和 SecurityAspect 两个切面。目标是在 SecurityAspect 之前执行 LoggingAspect。

```java

@Aspect
@Order(1)
@Component
public class LoggingAspect {
    private static final Logger logger = LoggerFactory.getLogger(LoggingAspect.class);

    @Before("execution(* com.pack.service.*.*(..))")
    public void logBefore() {
        logger.info("LoggingAspect: Logging before method execution");
        // Logging logic  
    }
}
```

在这里，@Order(1) 注解表示应首先执行日志记录。

下面，@Order(2) 注解表示安全方面应在第二位执行。

```java

@Aspect
@Order(2)
@Component
public class SecurityAspect {
    private static final Logger logger = LoggerFactory.getLogger(SecurityAspect.class);

    @Before("execution(* com.pack.service.*.*(..))")
    public void checkSecurity() {
        logger.info("SecurityAspect: Performing security check before method execution");
        // Security check logic  
    }
}
```

最终输出结果如下
```
INFO  LoggingAspect: Logging before method execution
INFO  SecurityAspect: Performing security check before method execution
```
通过调整@Order的数值来控制切面的执行顺序。