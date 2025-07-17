# Lambda
Lambda 表达式是 Java 8 引入的一项重要特性，它允许以简洁的语法表示匿名函数，主要用于简化函数式接口的实例化过程，提升代码的可读性和可维护性。**

## Lambda 表达式的基本语法

Lambda 表达式由参数列表、箭头符号（`->`）和主体组成，其基本语法格式如下：

```java
(parameters) -> expression
// 或
(parameters) -> { statements; }
```

- **参数列表（parameters）**：Lambda 表达式的参数列表，可以省略类型声明（编译器可自动推断）。若只有一个参数且类型可推断，可省略小括号。
- **箭头符号（`->`）**：分隔参数列表和主体部分。
- **主体（expression 或 statements）**：Lambda 表达式的逻辑代码，可以是单个表达式或代码块。若为单个表达式，其值自动作为返回值；若为代码块，需使用 `return` 语句显式返回。

## Lambda 表达式的核心应用场景

### 1. 函数式接口的实现

Lambda 表达式主要用于实现**函数式接口**（即仅包含一个抽象方法的接口）。通过 `@FunctionalInterface` 注解标记的接口可明确标识为函数式接口。

**示例：实现 `Runnable` 接口**
```java
Runnable r = () -> System.out.println("Hello, Lambda!");
new Thread(r).start(); // 输出：Hello, Lambda!
```

### 2. 与 Stream API 结合

Lambda 表达式与 `Stream API` 结合可实现高效的数据处理，如过滤、映射、排序等操作。

**示例：过滤并打印以 "C" 开头的名字**
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");
names.stream()
     .filter(name -> name.startsWith("C")) // Lambda 表达式过滤
     .map(name -> name.toUpperCase())      // Lambda 表达式转换
     .forEach(System.out::println);         // 方法引用打印
```

### 3. 事件处理

Lambda 表达式可简化事件处理器接口（如 `ActionListener`）的实现，避免匿名内部类的冗长代码。

**示例：按钮点击事件处理**
```java
JButton button = new JButton("Click Me");
button.addActionListener(event -> System.out.println("Button clicked!"));
```

### 4. 自定义排序逻辑

Lambda 表达式可与 `Comparator` 接口结合，实现灵活的排序规则。

**示例：按字符串长度降序排序**
```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");
names.sort((name1, name2) -> name2.length() - name1.length());
System.out.println(names); // 输出：[Charlie, Alice, David, Bob]
```

### 5. 并发编程

Lambda 表达式可简化并发任务的编写，如与 `CompletableFuture`、`ExecutorService` 等工具结合使用。

**示例：异步任务执行**
```java
CompletableFuture.supplyAsync(() -> "Hello, Async!")
                .thenAccept(System.out::println); // 输出：Hello, Async!
```

## Lambda 表达式的优势

1. **简洁性**：  
   Lambda 表达式用更少的代码实现相同功能，减少样板代码（如匿名内部类的冗长语法）。

2. **可读性**：  
   逻辑更直观，尤其是与 Stream API 结合时，代码更贴近自然语言描述。

3. **灵活性**：  
   支持函数式编程范式，可轻松实现行为参数化（将行为作为参数传递）。

4. **并行支持**：  
   与 Stream API 的并行流结合，可充分利用多核处理器提升性能。

## 、Lambda 表达式的限制

1. **变量作用域**：  
   Lambda 表达式可访问外部作用域的变量，但该变量必须是 `final` 或**事实上不可变**（即赋值后不再修改）。

2. **接口限制**：  
   仅适用于函数式接口（单个抽象方法），无法直接实现多抽象方法的接口。

3. **调试复杂性**：  
   匿名函数的特性可能增加调试难度（如堆栈跟踪信息不直观）。

## 方法引用：Lambda 表达式的简化形式

当 Lambda 表达式仅调用一个现有方法时，可使用**方法引用**进一步简化代码。方法引用有四种形式：

1. **静态方法引用**：`ClassName::staticMethodName`  
   **示例**：
   ```java
   Function<String, Integer> parseInt = Integer::parseInt;
   int number = parseInt.apply("123"); // 输出：123
   ```

2. **实例方法引用**：`instance::methodName`  
   **示例**：
   ```java
   List<String> list = Arrays.asList("a", "b", "c");
   list.forEach(System.out::println); // 输出：a, b, c
   ```

3. **构造方法引用**：`ClassName::new`  
   **示例**：
   ```java
   Supplier<List<String>> listSupplier = ArrayList::new;
   List<String> list = listSupplier.get();
   ```

4. **任意类型实例方法引用**：`ClassName::methodName`  
   **示例**：
   ```java
   BiFunction<String, String, Integer> stringCompare = String::compareTo;
   int result = stringCompare.apply("abc", "abd"); // 输出：-1
   ```