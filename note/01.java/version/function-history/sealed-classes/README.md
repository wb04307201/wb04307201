# Sealed Classes

## 引言：变更说明

Sealed Classes 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 功能描述

Sealed Classes（密封类）允许类或接口限制哪些其他类可以继承或实现它。通过显式声明允许的子类，密封类提供了更细粒度的继承控制，使代码更加安全和可维护。与模式匹配结合使用时，编译器可以验证 switch 表达式的穷举性，无需 default 分支。

## 基本用法（最新，Java 21+）

```java
// 1. 密封类 - 使用 permits 明确指定子类
public sealed class Shape permits Circle, Rectangle, Triangle { }

// 子类必须是 final、sealed 或 non-sealed
public final class Circle extends Shape { }             // 不可再继承
public sealed class Rectangle extends Shape              // 可继续限制
    permits FilledRectangle, EmptyRectangle { }
public non-sealed class Triangle extends Shape { }       // 开放继承

// 2. 密封接口
public sealed interface Expr permits Constant, Add, Mul { }
public final record Constant(int value) implements Expr { }
public final record Add(Expr left, Expr right) implements Expr { }
public final record Mul(Expr left, Expr right) implements Expr { }

// 3. 密封类 + Switch 模式匹配（穷举检查，无需 default）
int eval(Expr e) {
    return switch (e) {
        case Constant(int v) -> v;
        case Add(Expr l, Expr r) -> eval(l) + eval(r);
        case Mul(Expr l, Expr r) -> eval(l) * eval(r);
    }; // 编译器知道只有三种情况，无需 default
}

// 4. 同一文件中的密封类（省略 permits）
// 当所有子类都在同一文件中声明时，可以省略 permits 子句
sealed class Status { }           // permits Success, Error 可省略
final class Success extends Status { }
final class Error extends Status { String message; }

// 5. 密封类在 instanceof 中的使用
void process(Shape s) {
    if (s instanceof Circle c) {
        System.out.println("Circle");
    } else if (s instanceof Rectangle r) {
        System.out.println("Rectangle");
    }
    // 编译器可以推断所有情况（配合 sealed 限制）
}
```

## 变更历史表

| Java版本  | 新特性/增强内容                                            |
|---------|-----------------------------------------------------|
| Java 21 | 密封类与 Record 模式匹配、Switch 模式匹配完全集成                   |
| Java 17 | JEP 409: 密封类转正为标准特性                                |
| Java 16 | JEP 397: 密封类第二次预览 - 改进 permits 语法                  |
| Java 15 | JEP 360: 密封类首次预览 - 引入 sealed、permits、non-sealed 关键字 |

## 功能详细介绍

### 1. Java 15 - 密封类首次预览 (JEP 360)

首次引入三个关键字：
- `sealed`：声明此类只允许特定子类继承
- `permits`：指定允许的子类列表
- `non-sealed`：子类选择开放继承（密封链中的出口）

```java
public abstract sealed class Vehicle
    permits Car, Truck, Motorcycle { }
```

### 2. Java 16 - 第二次预览 (JEP 397)

改进 `permits` 子句的语法限制，当子类在同一源文件中声明时允许省略 `permits`。

### 3. Java 17 - 密封类转正 (JEP 409)

密封类成为标准特性。三个核心约束：
1. 密封类和其允许的子类必须在同一模块中（如果在命名模块中）
2. 每个允许的子类必须直接扩展密封类
3. 每个允许的子类必须选择其继承性质：`final`、`sealed` 或 `non-sealed`

### 4. Java 21 - 与模式匹配完全集成

密封类与 Record 模式和 Switch 模式匹配深度集成，形成完整的代数数据类型（ADT）支持：

```java
sealed interface Json permits JsonString, JsonNumber, JsonObject, JsonArray, JsonBoolean, JsonNull { }
// 配合 switch 实现类型安全的数据处理
String render(Json j) {
    return switch (j) {
        case JsonString(String s) -> "\"" + s + "\"";
        case JsonNumber(Number n) -> n.toString();
        case JsonObject(Map<String, Json> m) -> "{...}";
        case JsonArray(List<Json> l) -> "[...]";
        case JsonBoolean(boolean b) -> Boolean.toString(b);
        case JsonNull -> "null";
    };
}
```

## 密封类 vs 传统继承控制

| 方式            | 控制粒度  | 编译器支持 | 适用场景           |
|---------------|-------|------|----------------|
| `final` 类    | 完全禁止  | 是    | 不可变类、工具类        |
| 包私有构造函数       | 模块级   | 否    | 限制同包继承          |
| `sealed` 类   | 精确控制  | 是    | 领域模型、AST、状态机    |
| 默认（无限制）       | 无     | 否    | 需要开放继承的场景       |

## 适用场景

1. **领域建模**：有限的状态集合（如订单状态、用户角色）
2. **AST/表达式树**：编译器、解析器的抽象语法树
3. **JSON/XML 解析**：有限的 JSON 类型
4. **结果类型**：`Result<T>` 只能是 `Success<T>` 或 `Failure`

## 总结

密封类从 Java 15 预览到 Java 17 转正，为 Java 提供了精确的继承控制能力。与模式匹配结合后，形成完整的代数数据类型支持，使代码更加安全和可维护。
