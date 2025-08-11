# 函数式接口

**函数式接口**是Java 8引入的关键特性，旨在通过简化代码结构、提升可读性，为函数式编程提供基础支持。

## 1. 定义与规范
- **核心定义**：函数式接口（Functional Interface）是**仅包含一个抽象方法**的接口（允许覆盖`Object`类的公共方法，如`toString()`）。
- **注解约束**：使用`@FunctionalInterface`注解标记接口，编译器会强制检查接口是否符合规范（非强制但推荐）。
- **示例**：
  ```java
  @FunctionalInterface
  interface Calculator {
      int calculate(int a, int b); // 唯一抽象方法
  }
  ```

## 2. 与Lambda表达式的协同
- **Lambda表达式的基础**：函数式接口是Lambda表达式的类型依据，Lambda表达式本质上是函数式接口的实例。
- **语法简化**：Lambda表达式通过箭头符号`->`将参数与方法体分离，替代传统匿名内部类，显著减少代码冗余。
  ```java
  // 传统匿名内部类实现
  Runnable runnable = new Runnable() {
      @Override
      public void run() {
          System.out.println("Hello from anonymous class");
      }
  };

  // Lambda表达式实现
  Runnable lambdaRunnable = () -> System.out.println("Hello from lambda");
  ```

## 3. 内置函数式接口：`java.util.function`包
Java 8在`java.util.function`包中提供了丰富的内置函数式接口，覆盖常见操作场景：

| **接口**         | **功能**                          | **示例**                                                                 |
|------------------|-----------------------------------|--------------------------------------------------------------------------|
| `Predicate<T>`   | 接收参数并返回布尔值（条件判断）  | `Predicate<String> isLong = s -> s.length() > 5;`                        |
| `Consumer<T>`    | 接收参数并执行操作（无返回值）    | `Consumer<String> printer = s -> System.out.println(s);`                |
| `Function<T,R>`  | 接收参数并返回结果（转换操作）    | `Function<String, Integer> parser = s -> Integer.parseInt(s);`          |
| `Supplier<T>`    | 无参数，返回结果（延迟计算）      | `Supplier<Double> randomSupplier = () -> Math.random();`                 |
| `UnaryOperator<T>`| 接收一个参数并返回同类型结果      | `UnaryOperator<Integer> square = x -> x * x;`                             |

## 4. 函数式接口的实际应用
### 场景1：集合操作（Stream API）
函数式接口与Stream API结合，实现声明式数据处理：
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
List<String> filteredNames = names.stream()
    .filter(name -> name.length() > 3) // Predicate过滤
    .map(String::toUpperCase)         // Function转换
    .collect(Collectors.toList());
```

### 场景2：线程与回调
简化线程创建和回调逻辑：
```java
// 线程启动
new Thread(() -> System.out.println("Running in a thread")).start();

// 回调函数
void executeCallback(Runnable callback) {
    callback.run();
}
executeCallback(() -> System.out.println("Callback executed"));
```

### 场景3：方法引用与构造器引用
进一步简化Lambda表达式，提升代码可读性：
```java
// 静态方法引用
Function<String, Integer> parser = Integer::parseInt;

// 实例方法引用
Consumer<String> printer = System.out::println;

// 构造器引用
Supplier<List<String>> listSupplier = ArrayList::new;
```

## 5. 特性优势总结
- **代码简洁性**：Lambda表达式替代匿名内部类，减少样板代码。
- **可读性提升**：声明式编程风格使逻辑更清晰。
- **类型安全**：编译器通过函数式接口强制类型检查。
- **并行处理支持**：与Stream API结合，轻松实现并行流操作。

## 6. 注意事项
- **接口唯一性**：确保函数式接口仅包含一个抽象方法（覆盖`Object`方法不计入）。
- **默认方法兼容性**：接口可包含默认方法（`default`修饰），但不影响函数式接口定义。
- **向后兼容性**：Java 8之前的常见接口（如`Runnable`、`Comparator`）已自动符合函数式接口规范。