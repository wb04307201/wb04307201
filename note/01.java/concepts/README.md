# Java 核心概念

本目录涵盖 Java 语言的核心概念和基础知识，从基本语法到高级特性。

## 目录

### 语言基础

| 主题 | 说明 |
|------|------|
| [基本语法](syntax/) | 注释、关键字、运算符、流程控制 |
| [基本数据类型](data-types/) | 8种基本类型、包装类、自动装箱拆箱、精度问题 |
| [变量](variable/) | 成员变量、局部变量、静态变量、final关键字 |
| [方法](method/) | 方法类型、重载与重写、静态方法、可变参数、参数传递 |

### 面向对象

| 主题 | 说明 |
|------|------|
| [面向对象基础](oop/) | 三大特征（封装/继承/多态）、深浅拷贝、接口与抽象类、hashCode |
| [Object 类](object/) | 所有类的根类、equals/hashCode/toString、Objects工具类 |
| [内部类](inner-class/) | 成员内部类、静态内部类、局部内部类、匿名内部类 |

### 类型系统

| 主题 | 说明 |
|------|------|
| [枚举](enum/) | 枚举常量、带属性/方法的枚举、EnumSet/EnumMap、枚举单例 |
| [泛型](generics/) | 类型擦除、通配符、PECS原则、多重边界 |
| [注解](annotation/) | 元注解、自定义注解、运行时注解处理 |
| [记录类 Record](record/) | 不可变数据载体、Compact Constructor、与Lombok对比 |

### 核心机制

| 主题 | 说明 |
|------|------|
| [String](string/) | 不可变性、String/StringBuffer/StringBuilder、字符串常量池 |
| [异常](exception/) | 异常层次、Checked/Unchecked、try-with-resources、最佳实践 |
| [反射](reflection/) | Class对象、动态操作类、字段和方法访问、应用场景 |
| [序列化和反序列化](serialization-and-deserialization/) | Serializable、序列化框架对比（Jackson/Protobuf/Kryo等） |
| [SPI](spi/) | Service Provider Interface、ServiceLoader、插件化扩展 |
| [语法糖](syntactic-sugar/) | Lambda、Stream、Switch表达式、文本块、Pattern Matching |

## 核心概念速查

### 类 (Class)

类是 Java 的基本构建块，是创建对象的蓝图。

```java
public class Person {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public void introduce() {
        System.out.println("我叫" + name + "，今年" + age + "岁。");
    }
}
```

### 抽象类 (Abstract Class)

不能被实例化的类，用于定义公共行为和抽象行为。

```java
public abstract class Animal {
    public abstract void makeSound();  // 抽象方法
    public void eat() { System.out.println("eating..."); }  // 具体方法
}
```

### 接口 (Interface)

定义方法签名的契约，Java 8+ 支持默认方法和静态方法。

```java
public interface Vehicle {
    void start();
    void stop();
    default void honk() { System.out.println("Beep!"); }
}
```

### 异常 (Exception)

Java 使用异常处理错误和异常情况。try-with-resources 需要 Java 7+，`var` 需要 Java 10+。

```java
// MyResource 必须实现 AutoCloseable 接口才能在 try-with-resources 中使用
class MyResource implements AutoCloseable {
    @Override
    public void close() throws Exception {
        System.out.println("资源已关闭");
    }
}

try (MyResource resource = new MyResource()) {
    // 使用资源
} catch (Exception e) {
    // 处理异常
}
```

## 概念关系总览

```text
Java 核心概念
│
├── 类型系统
│   ├── 基本数据类型 → 包装类（自动装箱拆箱）
│   ├── 引用类型 → 类 / 接口 / 枚举 / 注解 / Record
│   └── 泛型（编译期类型安全）
│
├── 面向对象
│   ├── 封装 → 访问控制（public/private/protected）
│   ├── 继承 → extends / implements
│   └── 多态 → 方法重写 + 向上转型
│
├── 核心机制
│   ├── 异常处理 → try-catch-finally / try-with-resources
│   ├── 反射 → 运行时类型信息
│   ├── 序列化 → 对象 ↔ 字节流
│   └── SPI → 插件化扩展
│
└── 语法糖
    ├── Lambda → 函数式编程
    ├── Stream → 声明式数据处理
    ├── Switch 表达式 → 增强分支逻辑
    ├── 文本块 → 多行字符串字面量
    └── Pattern Matching → 类型安全的模式匹配
```
