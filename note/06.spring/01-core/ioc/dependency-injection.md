# 构造器注入

**构造器注入（Constructor Injection）** 是一种依赖注入（Dependency Injection, DI）的实现方式，通过类的**构造函数**将依赖对象（如服务、配置、资源等）传递给该类。它是面向对象设计中**依赖倒置原则**和**单一职责原则**的具体实践，也是现代框架（如Spring、Dagger、.NET Core等）中推荐的主要注入方式。

---

## 核心概念
1. **依赖注入的本质**  
   将一个类所需的依赖（其他类或服务）从外部传入，而非在类内部直接创建（如通过`new`关键字）。这降低了类之间的耦合度，提高了代码的可测试性和可维护性。

2. **构造器注入的特点**
    - **显式依赖**：通过构造函数参数明确声明类需要哪些依赖。
    - **不可变性**：依赖对象在构造函数中初始化后，通常不可更改（可通过`final`修饰符强制实现）。
    - **强制性**：如果依赖未提供，类将无法实例化，确保对象始终处于有效状态。

---

## 示例代码
### 1. 传统方式（高耦合）
```java
public class OrderService {
    private PaymentService paymentService = new PaymentService(); // 内部创建依赖

    public void processOrder() {
        paymentService.pay(); // 直接使用
    }
}
```
- **问题**：`OrderService`与`PaymentService`紧密耦合，难以替换或测试。

### 2. 构造器注入（解耦）
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

---

## 为什么推荐构造器注入？
1. **明确性**：构造函数参数直接展示了类的依赖关系，代码可读性高。
2. **不可变性**：依赖在对象创建时即确定，避免运行时修改导致的不可预测行为。
3. **线程安全**：构造完成后对象状态完整，无需额外同步。
4. **框架支持**：Spring等框架通过反射自动调用构造函数并注入依赖，简化开发。

---

## 与其他注入方式的对比
| 注入方式         | 优点               | 缺点                |
|--------------|------------------|-------------------|
| **构造器注入**    | 强制依赖、不可变、线程安全    | 参数过多时构造函数可能臃肿     |
| **Setter注入** | 灵活（可动态修改依赖）      | 依赖可能为`null`，需额外校验 |
| **字段注入**     | 代码简洁（直接通过注解注入字段） | 破坏封装性，难以测试（需反射）   |

---

## 实际应用场景
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

## 总结
构造器注入是依赖注入中最清晰、最安全的方式，尤其适合需要强制依赖或不可变对象的场景。它通过显式声明依赖关系，提升了代码的健壮性和可测试性，是现代软件开发中的最佳实践之一。