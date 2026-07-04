<!--
module:
  parent: java
  slug: java/concepts/method
  type: article
  category: 主模块子文章
  summary: Java 方法：重载/重写、可变参数、参数传递、Lambda 简写。
-->

# 方法

## 引言：基础概念

方法 是入门必学的基础概念。

本篇给出一句话定义 + 最小可运行示例 + 3 个常见误区，**5 分钟读完，10 分钟上手**。

---

## 方法的返回值

- 方法的返回值是方法体中的代码执行后产生的结果
- 作用是接收结果使得它可以用于其他操作
- 没有返回值的方法使用`void`声明

## 方法的4种类型

按照方法的返回值和参数类型将方法分为4种：

1. **无参数无返回值**
2. **有参数无返回值**
3. **有返回值无参数**
4. **有返回值有参数**

```java
// 1. 无参无返回值
public void sayHello() {
    System.out.println("Hello!");
}

// 2. 有参无返回值
public void greet(String name) {
    System.out.println("Hello, " + name + "!");
}

// 3. 有返回值无参数
public String getName() {
    return "John";
}

// 4. 有返回值有参数
public int add(int a, int b) {
    return a + b;
}
```

## 静态方法 vs 实例方法

### 静态方法不能调用非静态成员

静态方法属于类，在类加载时就已分配内存，可以通过类名直接访问。而非静态成员属于实例对象，只有在对象实例化之后才存在。

在类的非静态成员不存在的时候静态方法就已经存在了，此时调用在内存中还不存在的非静态成员属于非法操作。

| 对比维度 | 静态方法 | 实例方法 |
|---------|---------|---------|
| **调用方式** | 可通过类名直接调用，无需创建对象 | 必须通过对象实例调用 |
| **访问限制** | 只能访问静态成员（静态变量和静态方法） | 可以访问所有成员（静态+非静态） |
| **`this`关键字** | 不能使用`this` | 可以使用`this`指向当前对象 |
| **绑定方式** | 静态绑定，通过类名直接关联 | 动态绑定，通过对象引用在运行时查找（虚方法表） |

```java
public class Example {
    private int instanceVar = 10;
    private static int staticVar = 20;

    // 静态方法
    public static void staticMethod() {
        System.out.println(staticVar);    // 合法
        // System.out.println(instanceVar); // 编译错误！不能访问非静态成员
    }

    // 实例方法
    public void instanceMethod() {
        System.out.println(staticVar);    // 合法
        System.out.println(instanceVar);  // 合法
    }
}
```

## 重载（Overload）和重写（Override）

| 对比维度 | 重载（Overload） | 重写（Override） |
|---------|---------------|----------------|
| **发生范围** | 同一个类内 | 父子类之间 |
| **参数列表** | 必须不同 | 必须相同 |
| **返回类型** | 可以不同 | 子类返回值类型必须是父类返回类型的相同类型或子类型（协变返回） |
| **异常** | 可以不同 | 子类声明的**受检异常**必须是父类异常的相同类型或子类型（`RuntimeException` 不受此限制） |
| **访问修饰符** | 可以不同 | 不能做更严格的限制（可降低限制） |
| **发生阶段** | 编译期（静态绑定） | 运行期（动态绑定） |

```java
// 重载示例：同一个类中方法名相同，参数列表不同
public class Calculator {
    public int add(int a, int b) { return a + b; }
    public double add(double a, double b) { return a + b; }
    public int add(int a, int b, int c) { return a + b + c; }
}
```

```java
// 重写示例：子类重新定义父类的方法
public class Animal {
    public String sound() { return "..."; }
}

public class Dog extends Animal {
    @Override
    public String sound() { return "Bark!"; }
}
```

## 可变长参数（Varargs）

可变长参数允许在调用方法时传入不定数量的参数，在方法内部以数组形式处理。

```java
public class VarargsDemo {
    public static void printAll(String... args) {
        for (String arg : args) {
            System.out.println(arg);
        }
    }

    public static void main(String[] args) {
        printAll("a", "b", "c");
        printAll("x");
        printAll();  // 空参数也合法
    }
}
```

### 可变长参数的使用规则

1. 一个方法中最多只能有**一个**可变长参数
2. 可变长参数必须是方法的**最后一个**参数
3. 可变长参数可以像数组一样使用`length`属性

```java
// 合法
public void method(String name, int... numbers) { }

// 非法 - 可变参数不在最后
// public void method(int... numbers, String name) { }

// 非法 - 多个可变参数
// public void method(String... names, int... numbers) { }
```

## 方法参数传递机制

Java 中只有**值传递**（pass-by-value），没有引用传递：

- **基本类型参数**：传递的是值的副本，修改参数不影响原始变量
- **引用类型参数**：传递的是引用地址的副本，可以通过引用修改对象内容，但不能让原始引用指向新对象

```java
public class PassByValueDemo {
    public static void modify(int num, int[] arr) {
        num = 100;      // 不影响原始变量
        arr[0] = 100;   // 会影响原始数组内容
        arr = new int[]{1, 2, 3}; // 不影响原始引用
    }

    public static void main(String[] args) {
        int x = 1;
        int[] a = {10, 20};
        modify(x, a);
        System.out.println(x);     // 1（未改变）
        System.out.println(a[0]);  // 100（被修改）
    }
}
```

## Java 方法的更多类型

除了类中的静态方法和实例方法，Java 还定义了以下几种方法类型：

### 抽象方法（Abstract Method）

抽象方法只有方法声明，没有方法体，必须在子类中被重写。它用于定义类的行为规范，强制子类实现。

```java
// 抽象类定义抽象方法
public abstract class Shape {
    // 抽象方法：没有方法体，由子类实现
    public abstract double area();

    // 普通实例方法
    public void printArea() {
        System.out.println("面积: " + area());
    }
}
```

```java
// 子类实现抽象方法
public class Circle extends Shape {
    private double radius;

    public Circle(double radius) {
        this.radius = radius;
    }

    @Override
    public double area() {
        return Math.PI * radius * radius;
    }
}
```

### 接口 default 方法（Java 8+）

Java 8 引入了 `default` 关键字，允许在接口中提供方法的默认实现。这使得接口可以在不破坏现有实现类的情况下添加新方法。

```java
// 接口中定义抽象方法和 default 方法
public interface Greeting {
    // 抽象方法（接口中的传统方法）
    String sayHello();

    // default 方法：提供默认实现，实现类可以选择重写
    default String sayGoodbye() {
        return "Goodbye!";
    }
}
```

```java
// 实现类只需实现抽象方法，可选择重写 default 方法
public class EnglishGreeting implements Greeting {
    @Override
    public String sayHello() {
        return "Hello!";
    }
    // sayGoodbye() 使用接口的默认实现
}
```

### 接口静态方法（Java 8+）

Java 8 同时允许在接口中定义静态方法，通过接口名直接调用，常用于提供工具方法。

```java
public interface MathUtil {
    // 接口静态方法
    static int max(int a, int b) {
        return a >= b ? a : b;
    }

    // 接口静态方法
    static int abs(int a) {
        return a >= 0 ? a : -a;
    }
}

// 调用：通过接口名直接调用
// int result = MathUtil.max(3, 5);
```

### 接口 private 方法（Java 9+）

Java 9 允许在接口中定义 `private` 方法，用于在多个 `default` 方法或静态方法之间复用代码，避免重复。

```java
public interface Logger {
    default void logInfo(String msg) {
        log("INFO", msg);
    }

    default void logError(String msg) {
        log("ERROR", msg);
    }

    // private 方法：仅在接口内部使用，实现类无法访问或重写
    private void log(String level, String msg) {
        System.out.println("[" + level + "] " + msg);
    }
}
```

### 各类方法对比

| 方法类型 | 所属 | 是否有方法体 | 调用方式 | 引入版本 |
|---------|------|------------|---------|---------|
| 实例方法 | 类 | 是 | 通过对象实例调用 | Java 1.0 |
| 静态方法 | 类 | 是 | 通过类名调用 | Java 1.0 |
| 抽象方法 | 抽象类 | 否 | 子类重写后通过对象调用 | Java 1.0 |
| 接口 default 方法 | 接口 | 是 | 通过实现类对象调用 | Java 8 |
| 接口静态方法 | 接口 | 是 | 通过接口名调用 | Java 8 |
| 接口 private 方法 | 接口 | 是 | 仅接口内部调用 | Java 9 |

---

← [返回 Java 核心概念](../README.md)
