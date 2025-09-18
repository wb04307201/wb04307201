# 函数式接口

函数式接口（Functional Interface）是Java 8引入的核心概念之一，主要用于支持Lambda表达式和方法引用，是函数式编程在Java中的具体实现载体。

## 1. 定义与核心特征
- **定义**：仅包含**一个抽象方法**的接口。
- **关键特征**：
    - 只能有一个抽象方法（可包含多个默认方法或静态方法）。
    - 可使用`@FunctionalInterface`注解显式声明（编译器会验证是否符合函数式接口规范，若不符合则报错）。
    - Lambda表达式可直接实现该接口的唯一抽象方法。

## 2. 常见内置函数式接口
Java 8在`java.util.function`包中预定义了大量函数式接口，按功能分类如下：

| 接口名          | 抽象方法签名          | 用途示例                     |
|-----------------|-----------------------|------------------------------|
| `Function<T,R>`  | `R apply(T t)`        | 类型转换（如`String::length`）|
| `Consumer<T>`   | `void accept(T t)`    | 消费对象（如`System.out::println`） |
| `Supplier<T>`   | `T get()`             | 提供对象（如`Instant::now`）  |
| `Predicate<T>`  | `boolean test(T t)`   | 条件判断（如`list.filter(p)`）|
| `UnaryOperator<T>` | `T apply(T t)`      | 同类型操作（如`Math::abs`）   |
| `BinaryOperator<T>` | `T apply(T a, T b)` | 双目运算（如`Integer::sum`）  |

## 3. 特殊规则与注意事项
- **默认方法与静态方法**：函数式接口可包含多个默认方法或静态方法（如`Comparator`的`thenComparing`），不影响其函数式接口性质。
- **Object类方法**：若接口中的抽象方法覆盖了`Object`类的方法（如`equals`、`hashCode`），则不计入抽象方法计数。例如：
  ```java
  @FunctionalInterface
  interface MyInterface {
      void doSomething(); // 唯一抽象方法
      @Override boolean equals(Object obj); // 覆盖Object方法，不视为抽象方法
  }
  ```
- **Lambda与类型推断**：Lambda表达式的类型由目标函数式接口决定。例如：
  ```java
  Function<Integer, String> func = i -> "Number: " + i; // Lambda实现Function接口的apply方法
  ```

## 4. 实际应用场景
- **Stream API**：`map`、`filter`、`forEach`等方法均接受函数式接口参数。
  ```java
  List<String> list = Arrays.asList("a", "bb", "ccc");
  list.stream().map(String::length).forEach(System.out::println); // 输出1,2,3
  ```
- **线程与并发**：`Runnable`、`Callable`作为经典函数式接口，用于线程执行体。
- **事件监听**：GUI编程中，按钮点击事件可通过`ActionListener`（函数式接口）处理。

## 5. 自定义函数式接口示例
```java
@FunctionalInterface
interface Greeting {
    void sayHello(String name); // 唯一抽象方法

    default void farewell() { // 默认方法
        System.out.println("Goodbye!");
    }
}

public class Main {
    public static void main(String[] args) {
        // Lambda实现
        Greeting g = name -> System.out.println("Hello, " + name);
        g.sayHello("Alice"); // 输出：Hello, Alice
        g.farewell(); // 输出：Goodbye!
    }
}
```

## 6. 对比传统接口
- **单一职责**：函数式接口强调“单一功能”，而传统接口可包含多个抽象方法。
- **Lambda支持**：函数式接口可直接由Lambda表达式实现，传统接口需通过匿名内部类。

## **总结**
函数式接口是Java实现函数式编程的关键设计，通过Lambda表达式和方法引用简化了代码，提升了开发效率。其核心在于“单一抽象方法”的约束，结合内置接口和自定义接口，可灵活应用于各种场景，如数据处理、异步编程、事件驱动等。理解其定义、规则和典型用例，是掌握Java现代编程范式的基础。