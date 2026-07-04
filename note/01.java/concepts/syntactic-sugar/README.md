<!--
module:
  parent: java
  slug: java/concepts/syntactic-sugar
  type: article
  category: 主模块子文章
  summary: Java 语法糖：泛型擦除、自动装箱、foreach、Lambda、try-with-resources。
-->

# 语法糖

## 引言：基础概念

语法糖 是入门必学的基础概念。

本篇给出一句话定义 + 最小可运行示例 + 3 个常见误区，**5 分钟读完，10 分钟上手**。

---

语法糖（Syntactic Sugar）是编程语言为了方便开发者使用而设计的特殊语法，不影响语言的功能，但使代码更简洁、更易读。编译后会被转换为等价的基础语法形式。

## Java 中常见的语法糖

### 1. 泛型（Generics）

增强类型安全，减少类型转换：

```java
import java.util.List;
import java.util.ArrayList;

// 使用泛型前
List list = new ArrayList();
list.add("Hello");
String str = (String) list.get(0);  // 需要强制类型转换

// 使用泛型后
List<String> genericList = new ArrayList<>();
genericList.add("Hello");
String genericStr = genericList.get(0);  // 无需类型转换
```

### 2. 自动装箱与拆箱

基本类型和包装类型之间的自动转换：

```java
Integer boxedInt = 10;   // 自动装箱：Integer.valueOf(10)
int unboxedInt = boxedInt; // 自动拆箱：boxedInt.intValue()
```

### 3. 增强型 for 循环（foreach）

简化数组和集合的遍历：

```java
int[] numbers = {1, 2, 3, 4, 5};

// 传统 for 循环
for (int i = 0; i < numbers.length; i++) {
    System.out.println(numbers[i]);
}

// 增强型 for 循环
for (int number : numbers) {
    System.out.println(number);
}
```

### 4. 可变参数（Varargs）

允许方法接收不定数量的参数：

```java
public void printNumbers(int... numbers) {
    for (int number : numbers) {
        System.out.println(number);
    }
}

// 调用示例（需在方法体内使用）
// printNumbers(1, 2, 3, 4, 5);  // 可以传递任意数量参数
// printNumbers();                // 空参数也合法
```

### 5. 静态导入

直接导入静态成员，无需通过类名引用：

```java
import static java.lang.Math.*;
import static java.lang.System.out;

// 不使用静态导入时的写法（即使有 import static 也可用全限定名）
System.out.println(Math.sqrt(16));

// 使用静态导入
out.println(sqrt(16));
```

### 6. 注解（Annotations）

为代码添加元数据：

```java
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.lang.annotation.ElementType;

// 定义注解（单独文件 TestAnnotation.java）
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface TestAnnotation {
    String value() default "default value";
}
```

```java
// 使用注解（TestClass.java）
public class TestClass {
    @TestAnnotation(value = "test method")
    public void testMethod() { }
}
```

### 7. Lambda 表达式（Java 8+）

简洁地实现函数式接口：

```java
// 匿名内部类
Runnable runnable = new Runnable() {
    @Override
    public void run() {
        System.out.println("Running via anonymous class");
    }
};

// Lambda 表达式
Runnable lambda = () -> System.out.println("Running via lambda");
```

### 8. Stream API 与 Lambda 的协作（Java 8+）

> **注意**：Stream API 本身（Stream、filter、map、collect 等）是 Java 标准库提供的 API/类库，并非语法糖。与之配合使用的 Lambda 表达式常被称为语法糖，但其实现机制与匿名内部类有本质区别——它通过 `invokedynamic` 指令和 `LambdaMetafactory` 在运行时动态生成实现类，而非编译时脱糖为匿名类。此处将其列入是从「提供更简洁语法」的角度。

声明式数据处理：

```java
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

List<String> list = Arrays.asList("apple", "banana", "cherry");

// Stream API 是标准库 API，其中的 Lambda 表达式是语法糖
List<Integer> lengths = list.stream()
    .filter(s -> s.startsWith("a"))  // Lambda 是语法糖
    .map(String::length)
    .collect(Collectors.toList());
```

### 9. 方法引用（Java 8+）

Lambda 表达式的进一步简化：

```java
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

List<String> list = Arrays.asList("apple", "banana", "cherry");

// Lambda
List<String> uppercased = list.stream()
    .map(s -> s.toUpperCase())
    .collect(Collectors.toList());

// 方法引用
List<String> methodRefUppercased = list.stream()
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

### 10. 类型推断（Java 7+ / 10+）

菱形操作符`<>`允许省略泛型类型声明：

```java
// Java 7 之前
Map<String, List<String>> map = new HashMap<String, List<String>>();

// 使用菱形操作符（Java 7+）
Map<String, List<String>> diamondMap = new HashMap<>();
```

Java 10+ 引入了局部变量类型推断（`var`），编译器可从右侧表达式推断变量类型：

```java
// Java 10+ 的局部变量类型推断
var list = new ArrayList<String>();  // 编译器推断为 ArrayList<String>
var map2 = new HashMap<String, Integer>();  // 编译器推断为 HashMap<String, Integer>
```

### 11. try-with-resources（Java 7+）

自动关闭实现了 `AutoCloseable` 接口的资源，编译后脱糖为嵌套的 `try-finally` 块：

```java
// try-with-resources 写法（资源自动关闭，代码简洁）
try (BufferedReader br = new BufferedReader(new FileReader("test.txt"))) {
    return br.readLine();
}
```

> 完整说明（传统写法对比、多资源声明、Java 9+ effectively final 改进等）参见 [exception/README.md](../../../README.md#try-with-resourcesjava-7)。

### 12. Switch 表达式（Java 14+）

> **注意**：Switch 表达式既是语法简化，也引入了新的语言语义（如作为表达式可返回值、强制穷举性检查、`yield` 关键字），是语法糖与语言特性的结合。

```java
// 传统 switch
// 注意：传统 switch 如果忘记 break，会产生 fall-through，继续执行下一个 case
String dayType;
switch (day) {
    case "MONDAY":
    case "TUESDAY":
    case "WEDNESDAY":
    case "THURSDAY":
    case "FRIDAY":
        dayType = "Weekday";
        break;  // 必须加 break，否则会 fall-through 到下一个 case
    case "SATURDAY":
    case "SUNDAY":
        dayType = "Weekend";
        break;
    default:
        throw new IllegalStateException("Unexpected: " + day);
}

// Switch 表达式
String dayTypeExpr = switch (day) {
    case "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY" -> "Weekday";
    case "SATURDAY", "SUNDAY" -> "Weekend";
    default -> throw new IllegalStateException("Unexpected: " + day);
};

// 使用 yield 的多行块
String result = switch (day) {
    case "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY" -> {
        // 多行逻辑
        yield "Weekday";  // yield 返回值
    }
    case "SATURDAY", "SUNDAY" -> {
        yield "Weekend";
    }
    default -> {
        throw new IllegalStateException("Unexpected: " + day);
    }
};
```

### 13. Record（Java 14 预览，Java 16 正式发布）

不可变数据的简洁声明：

```java
// 传统方式（等价写法，需要大量样板代码）
public class TraditionalPoint {
    private final int x;
    private final int y;
    public TraditionalPoint(int x, int y) { this.x = x; this.y = y; }
    public int getX() { return x; }
    public int getY() { return y; }
    // 还需实现 equals(), hashCode(), toString() ...
}

// Record（编译器自动生成规范构造器、访问器方法（x()、y()，非 getX()/getY()）、equals、hashCode、toString）
public record Point(int x, int y) { }
```

### 14. 文本块（Text Blocks，Java 15+）

使用`"""`三引号定义多行字符串字面量，无需手动拼接换行符和转义引号：

```java
String json = """
    {
      "name": "张三",
      "age": 25
    }
    """;
```

> 完整说明（基本规则、前导空白处理、与 `String` 方法的配合等）参见 [string/README.md](../../../README.md#文本块text-blocks)。

### 15. Pattern Matching（Java 16+/21+）

```java
// instanceof Pattern Matching（Java 16+）
if (obj instanceof String s) {
    System.out.println(s.length());  // 直接使用，无需强制转换
}

// Switch Pattern Matching（Java 21+）
String describe(Object obj) {
    return switch (obj) {
        case Integer i -> "Integer: " + i;
        case String s -> "String: " + s;
        case null -> "null";
        default -> "Other: " + obj;
    };
}
```

### 16. Sealed Classes（密封类，Java 17+）

> **注意**：密封类严格来说不是语法糖，而是语言级别的类型系统特性（在字节码中携带 `PermittedSubclasses` 属性，影响 JVM 运行时行为）。此处列入是为了全面介绍现代 Java 的重要语法特性。

限制哪些类可以继承：

```java
public sealed class Shape
    permits Circle, Rectangle, Triangle { }

public final class Circle extends Shape { }       // final - 不能再继承
public sealed class Rectangle extends Shape        // sealed - 继续限制
    permits Square { }
public non-sealed class Triangle extends Shape { } // non-sealed - 开放继承
```

---

← [返回 Java 核心概念](../README.md)
