# Java 核心概念：类、抽象类、接口、枚举、注解、记录类和异常

## 1. 类 (Class)

类是Java的基本构建块，是创建对象的蓝图。

```java
public class Person {
    // 字段
    private String name;
    private int age;
    
    // 构造方法
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // 方法
    public void introduce() {
        System.out.println("Hello, my name is " + name + " and I'm " + age + " years old.");
    }
}
```

## 2. 抽象类 (Abstract Class)

抽象类是不能被实例化的类，用于定义公共行为和抽象行为。

```java
public abstract class Animal {
    // 抽象方法
    public abstract void makeSound();
    
    // 具体方法
    public void eat() {
        System.out.println("This animal eats food.");
    }
}

public class Dog extends Animal {
    @Override
    public void makeSound() {
        System.out.println("Bark!");
    }
}
```

## 3. 接口 (Interface)

接口定义了一组方法签名（Java 8后也可以有默认实现），用于实现多继承和多态。

```java
public interface Vehicle {
    // 抽象方法
    void start();
    void stop();
    
    // 默认方法 (Java 8+)
    default void honk() {
        System.out.println("Beep beep!");
    }
    
    // 静态方法 (Java 8+)
    static int getMaxSpeed() {
        return 120;
    }
}

public class Car implements Vehicle {
    @Override
    public void start() {
        System.out.println("Car started");
    }
    
    @Override
    public void stop() {
        System.out.println("Car stopped");
    }
}
```

## 4. 枚举 (Enum)

枚举用于定义一组固定的常量。

```java
public enum Day {
    MONDAY("Monday"), 
    TUESDAY("Tuesday"), 
    WEDNESDAY("Wednesday"),
    // ... 其他天数
    
    private final String displayName;
    
    Day(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
}

// 使用
Day today = Day.MONDAY;
System.out.println(today.getDisplayName());
```

## 5. 注解 (Annotation)

注解用于为代码提供元数据。

```java
// 定义注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface MyAnnotation {
    String value() default "default";
    int priority() default 0;
}

// 使用注解
public class MyClass {
    @MyAnnotation(value = "test", priority = 1)
    public void myMethod() {
        // 方法实现
    }
}
```

## 6. 记录类 (Record, Java 14+)

记录类是用于声明不可变数据的简洁方式。

```java
public record Point(int x, int y) {
    // 自动生成:
    // - 私有final字段
    // - 公共构造方法
    // - getter方法
    // - equals(), hashCode(), toString()
    
    // 可以添加额外方法
    public double distanceFromOrigin() {
        return Math.sqrt(x * x + y * y);
    }
}

// 使用
Point p = new Point(3, 4);
System.out.println(p.x()); // 3
System.out.println(p.distanceFromOrigin()); // 5.0
```

## 7. 异常 (Exception)

Java使用异常处理错误和异常情况。

```java
// 自定义异常
public class InsufficientFundsException extends Exception {
    public InsufficientFundsException(String message) {
        super(message);
    }
}

// 使用异常
public class BankAccount {
    private double balance;
    
    public void withdraw(double amount) throws InsufficientFundsException {
        if (amount > balance) {
            throw new InsufficientFundsException("Insufficient funds: " + balance);
        }
        balance -= amount;
    }
    
    public static void main(String[] args) {
        BankAccount account = new BankAccount();
        account.balance = 100;
        
        try {
            account.withdraw(150);
        } catch (InsufficientFundsException e) {
            System.err.println("Error: " + e.getMessage());
        } finally {
            System.out.println("Transaction completed");
        }
    }
}
```

## 总结对比

| 特性   | 类    | 抽象类  | 接口          | 枚举       | 注解             | 记录类        | 异常           |
|------|------|------|-------------|----------|----------------|------------|--------------|
| 实例化  | 可以   | 不可以  | 不可以         | 可以(常量)   | 不可以            | 不可以        | 可以           |
| 继承   | 单继承  | 单继承  | 多实现         | 隐式继承Enum | 隐式继承Annotation | 隐式继承Record | 可继承Throwable |
| 字段   | 可以   | 可以   | Java 9+可以   | 可以       | 可以             | 自动生成       | 可以           |
| 方法实现 | 可以   | 可以   | Java 8+默认方法 | 可以       | 可以             | 自动生成       | 可以           |
| 构造方法 | 可以   | 可以   | 不可以         | 私有构造方法   | 不可以            | 自动生成       | 可以           |
| 主要用途 | 对象创建 | 抽象概念 | 行为规范        | 固定常量     | 元数据            | 不可变数据      | 错误处理         |

这些Java核心概念共同构成了Java面向对象编程的基础，每个都有其特定的用途和优势。