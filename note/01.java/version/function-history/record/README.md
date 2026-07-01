<!--
module:
  parent: java
  slug: java/version/record
  type: article
  category: 主模块子文章
  summary: Java 14+ Record：不可变数据载体类的语法糖。
-->

# Record

## 引言：变更说明

Record 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 功能描述

Record 是 Java 16 引入的一种新的类声明形式，专门用于创建不可变的数据载体。Record 自动为每个字段生成访问器方法、`equals()`、`hashCode()` 和 `toString()`，大幅减少了数据类的样板代码。从 Java 19 开始，Record 还支持模式匹配（Record Patterns），可在 `instanceof` 和 `switch` 中直接解构 Record 的字段。

## 基本用法（最新，Java 21+）

```java
// 1. 基本定义（自动生成构造器、访问器、equals、hashCode、toString）
public record Person(String name, int age) {
    // 自定义校验逻辑（紧凑构造器）
    public Person {
        if (age < 0) throw new IllegalArgumentException("age must be >= 0");
    }
}

Person p = new Person("Alice", 30);
System.out.println(p.name());  // "Alice"（访问器方法，不是 getName()）

// 2. Record 模式匹配 - instanceof (Java 21+)
Object obj = new Person("Bob", 25);
if (obj instanceof Person(String name, int age)) {
    System.out.println(name + " is " + age);
}

// 3. Record 模式匹配 - switch (Java 21+)
sealed interface Shape permits Rectangle, Circle { }
record Rectangle(int w, int h) implements Shape { }
record Circle(int r) implements Shape { }

double area(Shape s) {
    return switch (s) {
        case Rectangle(int w, int h) -> w * h;
        case Circle(int r)           -> Math.PI * r * r;
    };
}

// 4. 嵌套 Record 模式
record Address(String city, String street) { }
record Contact(String name, Address address) { }

void print(Contact c) {
    if (c instanceof Contact(String name, Address(String city, _))) {
        System.out.println(name + " lives in " + city);
    }
}

// 5. 增强 for 循环中的 Record 模式 (Java 21+)
List<Point> points = List.of(new Point(1, 2), new Point(3, 4));
for (Point(int x, int y) : points) {
    System.out.println(x + ", " + y);
}

// 6. Record 继承泛型 (Java 21+)
record Result<T>(T data, String error) { }
Result<String> ok = new Result<>("success", null);
```

## 变更历史表

| Java版本  | 新特性/增强内容                                      |
|---------|-----------------------------------------------|
| Java 21 | JEP 440: Record 模式转正为标准特性                     |
| Java 20 | JEP 432: Record 模式第二次预览，支持增强 for 循环            |
| Java 19 | JEP 405: Record 模式首次预览，引入解构和模式匹配               |
| Java 16 | Records 转正为标准特性 (JEP 395)                      |
| Java 15 | Records 第二次预览                                     |
| Java 14 | JEP 359: Records 首次预览，引入数据载体类                   |

## 功能详细介绍

### 1. Java 14 - Record 首次预览 (JEP 359)

Java 14 首次引入 Record 作为预览特性，这是一种新的类声明形式，专门用于不可变数据载体。

```java
// 传统方式 vs Record
public class Person {
    private final String name;
    private final int age;
    public Person(String name, int age) { this.name = name; this.age = age; }
    public String name() { return name; }
    public int age() { return age; }
    // equals, hashCode, toString...
}
// Record 一行搞定：
public record Person(String name, int age) { }
```

Record 的特点：简洁性、不可变性、自动生成方法、规范构造器。

### 2. Java 15 - Record 第二次预览

Java 15 继续完善 Record 功能，解决第一版中发现的问题，API 设计更加稳定。

### 3. Java 16 - Record 转正 (JEP 395)

Java 16 将 Record 从预览特性转为标准特性，不再需要启用预览功能。

### 4. Java 19 - Record 模式首次预览 (JEP 405)

Java 19 引入 Record 模式，允许在 `instanceof` 操作中直接解构 Record 的字段：

```java
record Point(int x, int y) { }
Point point = new Point(10, 20);
if (point instanceof Point(int x, int y)) {
    System.out.println("X: " + x + ", Y: " + y);
}
```

### 5. Java 20 - Record 模式第二次预览 (JEP 432)

改进包括：支持泛型 Record 模式类型推断、支持 Record 模式出现在增强 for 语句标题中。

### 6. Java 21 - Record 模式转正 (JEP 440)

Record 模式转正为标准特性，与 switch 表达式完美结合：

```java
record Rectangle(int w, int h) { }
record Circle(int r) { }

String description = switch (shape) {
    case Rectangle(int w, int h) -> "Rectangle: " + w + "x" + h;
    case Circle(int r)           -> "Circle: radius " + r;
    default                      -> "Unknown";
};
```

## Record 的核心优势

1. **减少样板代码**：自动生成构造器、访问器、equals、hashCode 和 toString
2. **不可变性**：所有字段都是 final 的，确保线程安全
3. **模式匹配支持**：与 Record 模式结合，提供强大的模式匹配能力

## Record 的限制

1. 不能继承其他类（隐式继承 `java.lang.Record`）
2. 不能在 Record 头部之外声明实例字段
3. 不能声明抽象方法或 native 方法

## 总结

Record 从 Java 14 预览到 Java 21 成熟，配合 Record 模式，Java 的模式匹配能力显著增强。
