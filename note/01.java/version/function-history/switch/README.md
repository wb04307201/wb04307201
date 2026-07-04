<!--
module:
  parent: java
  slug: java/switch
  type: article
  category: 主模块子文章
  summary: Switch
-->

# Switch

## 引言：变更说明

Switch 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 功能描述

Switch 语句是 Java 的基础控制流语句。从 Java 14 起，Switch 表达式引入了箭头语法和表达式返回值能力；Java 21 进一步将模式匹配转正为标准特性，允许在 switch 中直接进行类型检查和解构。这些改进使 switch 从单纯的条件分支转变为强大的模式匹配工具。

## 基本用法（最新，Java 26+）

```java
// 1. 传统 switch 语句（Java 8 及之前）
String day = "MONDAY";
String result;
switch (day) {
    case "MONDAY":
    case "TUESDAY":
    case "WEDNESDAY":
    case "THURSDAY":
    case "FRIDAY":
        result = "Weekday";
        break;
    default:
        result = "Weekend";
        break;
}

// 2. Switch 表达式 - 箭头语法（Java 14+）
String result2 = switch (day) {
    case "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY" -> "Weekday";
    case "SATURDAY", "SUNDAY" -> "Weekend";
    default -> "Unknown";
};

// 3. Switch 表达式 - yield 返回值（Java 14+）
int numLetters = switch (day) {
    case "MONDAY", "FRIDAY", "SUNDAY" -> 6;
    case "TUESDAY" -> 7;
    case "THURSDAY", "SATURDAY" -> 8;
    case "WEDNESDAY" -> 9;
    default -> {
        System.out.println("Invalid day: " + day);
        yield -1;
    }
};

// 4. Switch 模式匹配 - 类型模式（Java 21+）
static String format(Object obj) {
    return switch (obj) {
        case Integer i -> String.format("int %d", i);
        case Long l    -> String.format("long %d", l);
        case Double d  -> String.format("double %f", d);
        case String s  -> String.format("String: %s", s);
        case null      -> "null";
        default        -> obj.toString();
    };
}

// 5. Switch 模式匹配 - guard 条件（Java 21+）
sealed interface Shape permits Rectangle, Circle, Triangle { }
record Rectangle(int w, int h) implements Shape { }
record Circle(int r) implements Shape { }
record Triangle(int base, int height) implements Shape { }

String describe(Shape s) {
    return switch (s) {
        case Rectangle(int w, int h) when w == h -> "Square " + w + "x" + h;
        case Rectangle(int w, int h)             -> "Rectangle " + w + "x" + h;
        case Circle(int r) when r > 10           -> "Large circle, radius " + r;
        case Circle(int r)                       -> "Circle, radius " + r;
        case Triangle                            -> "Triangle";
    };
}

// 6. 基本类型模式匹配（Java 25+ 预览）
static String formatPrimitive(Object obj) {
    return switch (obj) {
        case int i    -> String.format("int %d", i);
        case long l   -> String.format("long %d", l);
        case double d -> String.format("double %f", d);
        case boolean b -> String.format("boolean %b", b);
        case String s -> String.format("String: %s", s);
        default       -> obj.toString();
    };
}

// 7. 嵌套模式匹配
record Point(int x, int y) { }
record ColoredPoint(Point p, String color) { }

String describeNested(Object obj) {
    return switch (obj) {
        case ColoredPoint(Point(int x, int y), String color)
                when x > 0 && y > 0 -> "First quadrant, " + color;
        case ColoredPoint(Point(int x, int y), _) -> "Other quadrant, " + color;
        default -> "Unknown";
    };
}
```

## 变更历史表

| Java版本  | 新特性/增强内容                                      |
|---------|-----------------------------------------------|
| Java 26 | JEP 530: 基本类型模式匹配（第四次预览）- 为正式发布做准备        |
| Java 25 | JEP 507: 基本类型模式匹配（第三次预览）- 扩展 instanceof 和 switch 到基本类型 |
| Java 21 | JEP 441: Switch 模式匹配转正为标准特性                    |
| Java 20 | JEP 433: Switch 模式匹配第四次预览                         |
| Java 19 | JEP 427: Switch 模式匹配第三次预览                         |
| Java 18 | JEP 420: Switch 模式匹配第二次预览                         |
| Java 17 | JEP 406: Switch 模式匹配首次预览 - 允许在 switch 中使用类型模式  |
| Java 14 | JEP 361: Switch 表达式转正为标准特性 - 引入箭头语法和 yield      |
| Java 13 | JEP 354: Switch 表达式第二次预览 - 引入 yield 替代 break    |
| Java 12 | JEP 325: Switch 表达式首次预览 - 引入箭头语法                |
| Java 8  | 传统 switch 语句，支持 byte/short/char/int/枚举/String      |

## 功能详细介绍

### 1. Java 8 及之前 - 传统 Switch 语句

传统 switch 语句支持 byte、short、char、int 及其包装类型，Java 7 开始支持 String 类型。主要限制：需要 break 防止穿透、不能作为表达式返回值、不支持类型模式匹配。

### 2. Java 12 - Switch 表达式首次预览 (JEP 325)

首次引入箭头语法 `case L ->`，自动避免穿透问题：

```java
String result = switch (day) {
    case "MONDAY", "FRIDAY", "SUNDAY" -> 6;
    case "TUESDAY" -> 7;
    default -> -1;
};
```

### 3. Java 13 - Switch 表达式第二次预览 (JEP 354)

引入 `yield` 关键字在代码块中返回值，替代容易混淆的 `break value`：

```java
int result = switch (day) {
    case "MONDAY" -> {
        System.out.println("Start of week");
        yield 1;
    }
    default -> 0;
};
```

### 4. Java 14 - Switch 表达式转正 (JEP 361)

Switch 表达式从预览转为标准特性，不再需要 `--enable-preview` 标志。

### 5. Java 17 - Switch 模式匹配首次预览 (JEP 406)

允许在 switch 中使用类型模式，直接在 case 中进行类型检查和变量绑定：

```java
static String format(Object obj) {
    return switch (obj) {
        case Integer i -> String.format("int %d", i);
        case String s  -> String.format("String: %s", s);
        default        -> obj.toString();
    };
}
```

### 6. Java 18-20 - Switch 模式匹配迭代预览 (JEP 420/427/433)

持续完善：支持密封类穷举检查（无需 default）、guard 条件（when 子句）、null 值处理改进、嵌套模式匹配等。

### 7. Java 21 - Switch 模式匹配转正 (JEP 441)

Switch 模式匹配转正为标准特性。配合密封类和 Record 模式，可实现强大的代数数据类型处理：

```java
sealed interface Expr permits ConstantExpr, PlusExpr, TimesExpr, NegExpr { }
record ConstantExpr(int value) implements Expr { }
record PlusExpr(Expr left, Expr right) implements Expr { }
record TimesExpr(Expr left, Expr right) implements Expr { }
record NegExpr(Expr operand) implements Expr { }

int eval(Expr e) {
    return switch (e) {
        case ConstantExpr(int v) -> v;
        case PlusExpr(Expr l, Expr r) -> eval(l) + eval(r);
        case TimesExpr(Expr l, Expr r) -> eval(l) * eval(r);
        case NegExpr(Expr o) -> -eval(o);
    }; // 密封接口保证穷举，无需 default
}
```

### 8. Java 25 - 基本类型模式匹配第三次预览 (JEP 507)

扩展 instanceof 和 switch 到所有基本类型（int、long、double、boolean 等），使类型处理更加统一：

```java
switch (obj) {
    case int i    -> System.out.println("int: " + i);
    case long l   -> System.out.println("long: " + l);
    case double d -> System.out.println("double: " + d);
    case boolean b -> System.out.println("boolean: " + b);
    case String s -> System.out.println("String: " + s);
    default       -> System.out.println("other: " + obj);
}
```

### 9. Java 26 - 基本类型模式匹配第四次预览 (JEP 530)

进一步调整语法和语义，为正式发布做准备。

## 总结

Switch 从传统条件分支语句演进为强大的模式匹配工具：Java 12-14 引入表达式语法消除穿透问题，Java 17-21 引入类型模式匹配实现类型安全的分支处理，Java 25-26 扩展到基本类型模式。配合密封类和 Record，switch 成为处理代数数据类型的核心机制。

---

← [返回 功能版本变更历史](../README.md)
