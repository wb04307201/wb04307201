# Record

| Java版本  | 新特性/增强内容                                      |
|---------|-----------------------------------------------|
| Java 14 | JEP 359: Records（第一次预览）- 引入 Record 作为预览特性     |
| Java 15 | Records（第二次预览）- 继续完善 Record 功能                |
| Java 16 | Records（正式特性）- Record 转正为标准特性                 |
| Java 19 | JEP 405: Record 模式（第一次预览）- 引入 Record 模式作为预览特性 |
| Java 20 | JEP 432: Record 模式（第二次预览）- 继续完善 Record 模式功能   |
| Java 21 | JEP 440: Record 模式（正式特性）- Record 模式转正为标准特性    |

## 功能详细介绍

### 1. Java 14 - Record 初始引入 (JEP 359)

Java 14 首次引入了 Record 作为预览特性，这是 Java 语言的一个重要里程碑。

#### 核心概念：

Record 是一种新的类声明形式，专门用于创建不可变的数据载体类。它提供了一种简洁的语法来声明只包含数据的类。

#### 基本语法：

```java
// 传统方式定义数据类
public class Person {
    private final String name;
    private final int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String name() { return name; }
    public int age() { return age; }
    
    @Override
    public boolean equals(Object obj) { /* 实现 */ }
    @Override
    public int hashCode() { /* 实现 */ }
    @Override
    public String toString() { /* 实现 */ }
}

// 使用 Record 简化定义
public record Person(String name, int age) { }
```


#### Record 的特点：

1. **简洁性**：大大减少了定义数据类时所需的样板代码
2. **不可变性**：所有字段都是 final 的，实例一旦创建就不能修改
3. **自动生成方法**：自动为每个字段生成 getter 方法、equals()、hashCode() 和 toString() 方法
4. **构造器**：自动生成规范构造器（canonical constructor）

#### 使用示例：

```java
// 定义 Record
record Point(int x, int y) { }

// 使用 Record
Point p1 = new Point(10, 20);
Point p2 = new Point(10, 20);

// 自动生成的方法
System.out.println(p1.x());        // 10
System.out.println(p1.y());        // 20
System.out.println(p1.toString()); // Point[x=10, y=20]
System.out.println(p1.equals(p2)); // true
```


### 2. Java 15 - Record 继续完善

Java 15 继续完善 Record 功能，解决第一版中发现的问题。

### 3. Java 16 - Record 转正为正式特性

Java 16 将 Record 从预览特性转正为标准特性，标志着该功能的成熟。

#### 主要改进：

1. **正式支持**：不再需要启用预览功能即可使用
2. **稳定性**：API 设计更加稳定，减少了重大变更的可能性
3. **工具支持**：IDE 和其他开发工具对 Record 提供了更好的支持

### 4. Java 19 - Record 模式初始引入 (JEP 405)

Java 19 引入了 Record 模式作为预览特性，扩展了 Record 的功能。

#### 核心概念：

Record 模式允许在 instanceof 操作中使用 Record，并直接解构和匹配 Record 中的字段。

#### 基本用法：

```java
record Point(int x, int y) { }

Point point = new Point(10, 20);

// 使用 Record 模式解构
if (point instanceof Point(int x, int y)) {
    System.out.println("X: " + x + ", Y: " + y);
}
```


#### 主要优势：

1. **模式匹配**：可以在 instanceof 操作中直接进行类型检查和解构
2. **代码简洁性**：减少了类型转换和字段访问的样板代码
3. **类型安全**：编译时检查确保模式匹配的正确性

### 5. Java 20 - Record 模式继续完善 (JEP 432)

Java 20 继续完善 Record 模式功能。

#### 改进内容：

1. **泛型支持**：添加对通用 Record 模式类型参数推断的支持
2. **增强 for 循环**：支持 Record 模式出现在增强 for 语句的标题中
3. **命名模式移除**：删除对命名 Record 模式的支持

### 6. Java 21 - Record 模式转正为正式特性 (JEP 440)

Java 21 将 Record 模式从预览特性转正为标准特性。

#### 与 switch 表达式的结合：

```java
record Rectangle(int width, int height) { }
record Circle(int radius) { }

Object shape = new Rectangle(10, 20);

String description = switch (shape) {
    case Rectangle(int w, int h) -> "Rectangle with width " + w + " and height " + h;
    case Circle(int r) -> "Circle with radius " + r;
    default -> "Unknown shape";
};

System.out.println(description);
```


## Record 的核心优势

1. **减少样板代码**：自动生成构造器、getter、equals、hashCode 和 toString 方法
2. **不可变性**：所有字段都是 final 的，确保线程安全
3. **数据透明性**：字段可以直接访问，提供良好的数据透明性
4. **模式匹配支持**：与 Record 模式结合使用，提供强大的模式匹配能力

## Record 的限制

1. **不能继承其他类**：Record 隐式继承 java.lang.Record，不能再继承其他类
2. **不能声明实例字段**：除了在 Record 头部声明的字段外，不能声明其他实例字段
3. **不能声明抽象方法**：Record 不能声明抽象方法
4. **不能声明 native 方法**：Record 不能声明 native 方法

## 最佳实践

1. **适用于数据载体**：Record 非常适合用作 DTO（数据传输对象）、值对象等
2. **与模式匹配结合**：在需要类型检查和数据提取的场景中使用 Record 模式
3. **避免复杂逻辑**：Record 主要用于数据载体，避免在其中实现复杂的业务逻辑
4. **合理使用自定义构造器**：在需要验证参数或进行其他处理时，可以定义自定义构造器

## 适用场景

1. **数据传输对象（DTO）**：在网络传输或不同层之间传递数据
2. **值对象**：表示不可变的值概念
3. **配置对象**：存储不可变的配置信息
4. **查询结果**：存储数据库查询或其他操作的结果
5. **函数返回值**：当需要返回多个值时使用 Record

## 总结

Record 从 Java 14 的预览特性发展到 Java 21 的成熟特性，为 Java 开发者提供了一种简洁、安全的方式来创建数据载体类。结合 Record 模式，Java 的模式匹配能力得到了显著增强，使得代码更加简洁和易读。Record 的引入体现了 Java 语言对现代编程需求的响应，特别是在函数式编程和数据处理方面的需求。通过减少样板代码和提供内置的不可变性，Record 使得 Java 开发更加高效和安全。