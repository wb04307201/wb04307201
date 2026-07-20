<!--
module:
  parent: spring
  slug: spring/ioc/dependency-injection
  type: article
  category: 主模块子文章
  summary: Spring 依赖注入 4 种方式：构造器、Setter、字段、@Bean/工厂方法。
-->

# 依赖注入

> ⬅️ [返回 IoC 总览](README.md) | [Bean 生命周期](bean-lifecycle.md) | [作用域与线程安全](scopes-and-thread-safety.md)

Spring 框架支持 **4 种依赖注入方式**：构造器注入、Setter 注入、字段注入、工厂方法注入（含静态工厂与实例工厂）。其中前 3 种是基于注解的常规用法，最后 1 种主要用于兼容老代码（已被 `@Bean` 取代）。

---

## 🎯 一句话定位

**依赖注入 = 把依赖从外部"塞"进来，而非内部 `new`**——Spring 提供了 4 种"塞法"，从最推荐的构造器注入，到兼容遗留代码的工厂方法注入。

---

## 一、构造器注入（推荐）

**构造器注入（Constructor Injection）** 是一种依赖注入（Dependency Injection, DI）的实现方式，通过类的**构造函数**将依赖对象（如服务、配置、资源等）传递给该类。它是面向对象设计中**依赖倒置原则**和**单一职责原则**的具体实践，也是现代框架（如Spring、Dagger、.NET Core等）中推荐的主要注入方式。

### 核心概念

1. **依赖注入的本质**  
   将一个类所需的依赖（其他类或服务）从外部传入，而非在类内部直接创建（如通过`new`关键字）。这降低了类之间的耦合度，提高了代码的可测试性和可维护性。

2. **构造器注入的特点**
    - **显式依赖**：通过构造函数参数明确声明类需要哪些依赖。
    - **不可变性**：依赖对象在构造函数中初始化后，通常不可更改（可通过`final`修饰符强制实现）。
    - **强制性**：如果依赖未提供，类将无法实例化，确保对象始终处于有效状态。

### 示例代码

**1. 传统方式（高耦合）**

```java
public class OrderService {
    private PaymentService paymentService = new PaymentService(); // 内部创建依赖

    public void processOrder() {
        paymentService.pay(); // 直接使用
    }
}
```

- **问题**：`OrderService`与`PaymentService`紧密耦合，难以替换或测试。

**2. 构造器注入（解耦）**

```java
public class OrderService {
    private final PaymentService paymentService; // 依赖通过构造器传入

    // 构造函数注入
    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    public void processOrder() {
        paymentService.pay();
    }
}
```

- **优势**：
    - `PaymentService`由外部传入，可灵活替换为模拟对象（Mock）进行单元测试。
    - 通过`final`确保依赖不可变，避免空指针异常。

### 为什么推荐构造器注入？

1. **明确性**：构造函数参数直接展示了类的依赖关系，代码可读性高。
2. **不可变性**：依赖在对象创建时即确定，避免运行时修改导致的不可预测行为。
3. **线程安全**：构造完成后对象状态完整，无需额外同步。
4. **框架支持**：Spring等框架通过反射自动调用构造函数并注入依赖，简化开发（Spring 4.3+ 单构造器可省略 `@Autowired`）。

---

## 二、Setter 注入

> 通过 `setter` 方法注入依赖，**可选依赖**或**需要动态修改**时使用。

```java
public class ReportService {
    private Printer printer;

    @Autowired(required = false) // 可选依赖
    public void setPrinter(Printer printer) {
        this.printer = printer;
    }
}
```

**特点**：
- 灵活，可重新调用 setter 切换依赖
- 无法表达必填、字段不能加 `final`

---

## 三、字段注入（Field Injection）

> 直接在字段上加 `@Autowired`，**代码最简洁但不推荐**。

```java
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository; // 字段注入
}
```

**问题**：
- 破坏封装性，依赖对外部不可见
- 难以单元测试（无法通过构造器注入 Mock）
- 无法加 `final`

---

## 四、工厂方法注入（Factory Method Injection）

> 兼容遗留代码的方式，**已被 `@Bean` 取代**，新项目不推荐使用。

### 1. 静态工厂方法注入

调用**静态方法**返回对象，容器通过 `factory-method` 指定。

```xml
<bean id="clientService" class="com.example.ClientService"
      factory-method="createInstance">
    <constructor-arg value="arg1"/>
</bean>
```

```java
public class ClientService {
    private final String arg;

    private ClientService(String arg) {
        this.arg = arg;
    }

    // 静态工厂方法
    public static ClientService createInstance(String arg) {
        return new ClientService(arg);
    }
}
```

### 2. 实例工厂方法注入

先有一个工厂 Bean，再调用它的**实例方法**返回目标对象。

```xml
<!-- 1. 定义工厂 Bean -->
<bean id="serviceFactory" class="com.example.DefaultServiceFactory"/>

<!-- 2. 通过工厂的实例方法创建目标 Bean -->
<bean id="clientService" factory-bean="serviceFactory" factory-method="createClientServiceInstance">
    <constructor-arg value="arg1"/>
</bean>
```

```java
public class DefaultServiceFactory {
    public ClientService createClientServiceInstance(String arg) {
        return new ClientService(arg);
    }
}
```

### 工厂方法 vs @Bean

| 维度 | 工厂方法（XML） | @Bean |
|------|---------------|-------|
| **配置形式** | XML | Java 注解 |
| **类型安全** | 弱（字符串） | 强（编译期校验） |
| **可读性** | 差 | 好 |
| **现状** | 已被淘汰 | 主流方式 |

> 📌 新项目**用 `@Bean` 替代工厂方法注入**。

---

## 五、4 种注入方式对比

| 注入方式 | 优点 | 缺点 | 推荐度 |
|---------|------|------|:------:|
| **构造器注入** | 强制依赖、不可变、线程安全、支持 final | 构造方法可能过长 | ⭐⭐⭐⭐⭐ |
| **Setter 注入** | 灵活、可选依赖、可动态修改 | 无法表达必填、不能 final | ⭐⭐⭐ |
| **字段注入** | 代码简洁 | 破坏封装性、难测试、不能 final | ⭐ |
| **工厂方法注入** | 兼容老代码 | 配置冗长、已被 `@Bean` 取代 | ⭐ |

> 📌 Spring 官方**推荐构造器注入**（强制依赖、支持不可变对象）。

---

## 六、实际应用场景

- **Spring框架**：通过`@Autowired`注解标记构造函数（甚至可省略注解，Spring 4.3+自动识别）。
  ```java
  @Service
  public class OrderService {
      private final PaymentService paymentService;

      // Spring会自动注入依赖
      public OrderService(PaymentService paymentService) {
          this.paymentService = paymentService;
      }
  }
  ```
- **单元测试**：使用Mock对象替换真实依赖。
  ```java
  @Test
  public void testProcessOrder() {
      PaymentService mockPayment = Mockito.mock(PaymentService.class);
      OrderService orderService = new OrderService(mockPayment);
      orderService.processOrder();
      Mockito.verify(mockPayment).pay(); // 验证交互
  }
  ```

---

## 七、总结

构造器注入是依赖注入中最清晰、最安全的方式，尤其适合需要强制依赖或不可变对象的场景。它通过显式声明依赖关系，提升了代码的健壮性和可测试性，是现代软件开发中的最佳实践之一。工厂方法注入主要存在于遗留 XML 配置中，新项目应优先使用 `@Bean`。

---

## 相关章节

- ⬅️ [返回 IoC 总览](README.md)
- [Bean 生命周期](bean-lifecycle.md)
- [作用域与线程安全](scopes-and-thread-safety.md)
- [循环依赖与三级缓存](circular-dependency.md)
