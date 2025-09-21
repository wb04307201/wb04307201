# Switch

| Java版本  | 新特性/增强内容                                                   |
|---------|------------------------------------------------------------|
| Java 8  | 传统 switch 语句，支持 byte、short、char、int 及其包装类型，枚举类型和 String 类型 |
| Java 14 | JEP 361: Switch 表达式（标准特性）- 引入箭头语法和表达式形式                    |
| Java 17 | JEP 406: Switch 模式匹配（预览）- 允许在 switch 中使用类型模式匹配             |
| Java 21 | Switch 模式匹配（预览）- 继续完善模式匹配功能                                |
| Java 25 | JEP 507: 基本类型模式匹配（第三预览版）- 扩展模式匹配到基本类型                      |

## 功能详细介绍

### 1. Java 8 及之前版本 - 传统 Switch 语句

在 Java 8 及之前的版本中，switch 语句只支持有限的数据类型：
- 基本整数类型：byte、short、char、int
- 对应的包装类型：Byte、Short、Character、Integer
- 枚举类型
- String 类型（从 Java 7 开始支持）

传统 switch 语句存在一些限制和不足：
1. 需要使用 break 语句防止穿透（fall-through）
2. 不能作为表达式返回值
3. 不支持复杂的模式匹配

```java
// 传统 switch 语句示例
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
    case "SATURDAY":
    case "SUNDAY":
        result = "Weekend";
        break;
    default:
        result = "Unknown";
        break;
}
```


### 2. Java 14 - Switch 表达式 (JEP 361)

Java 14 将 switch 表达式从预览特性转为标准特性，引入了重大改进：

1. **箭头语法**：使用 `->` 替代传统的 `:`，自动避免穿透问题
2. **表达式形式**：switch 可以作为表达式返回值
3. **代码块支持**：可以使用 `{}` 包含多个语句，并使用 `yield` 返回值

```java
// 使用箭头语法的 switch 表达式
String day = "MONDAY";
String result = switch (day) {
    case "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY" -> "Weekday";
    case "SATURDAY", "SUNDAY" -> "Weekend";
    default -> "Unknown";
};

// 使用代码块的 switch 表达式
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
```


### 3. Java 17 - Switch 模式匹配 (JEP 406)

Java 17 引入了 switch 模式匹配的预览版本，这是一个重要的增强功能：

1. **类型模式匹配**：可以在 switch 中直接进行类型检查和转换
2. **instanceof 模式匹配**：结合 instanceof 操作符使用模式变量

```java
// Switch 模式匹配示例
static String format(Object obj) {
    return switch (obj) {
        case Integer i -> String.format("int %d", i);
        case Long l -> String.format("long %d", l);
        case Double d -> String.format("double %f", d);
        case String s -> String.format("String %s", s);
        default -> obj.toString();
    };
}
```


### 4. Java 21 - Switch 模式匹配增强

Java 21 继续完善 switch 模式匹配功能，提供了更强大的模式匹配能力：

1. **改进的类型检查**：更精确的类型推断和检查
2. **增强的模式语法**：支持更复杂的模式组合

### 5. Java 25 - 基本类型模式匹配 (JEP 507)

Java 25 进一步扩展了模式匹配的能力，支持基本类型：

1. **基本类型支持**：允许在 instanceof 和 switch 中直接使用基本类型
2. **更自然的语法**：简化了基本类型的模式匹配代码

```java
// Java 25 中的基本类型模式匹配示例
static void test(Object obj) {
    // 在 instanceof 中使用基本类型模式
    if (obj instanceof int i) {
        System.out.println("It's an int: " + i);
    }
    
    // 在 switch 中使用基本类型模式
    switch (obj) {
        case Integer i -> System.out.println("Integer: " + i);
        case int i -> System.out.println("int: " + i);  // 基本类型模式
        case String s -> System.out.println("String: " + s);
        default -> System.out.println("Other: " + obj);
    }
}
```


## 总结

Switch 语句从 Java 8 到 Java 25 经历了显著的演进：

1. **Java 14** 的 switch 表达式是第一个重大改进，引入了更简洁的语法和表达式能力
2. **Java 17** 开始的模式匹配预览是第二个重要里程碑，允许类型检查和转换直接在 switch 中进行
3. **Java 21-25** 持续完善模式匹配功能，特别是扩展到基本类型支持

这些改进使 switch 语句变得更加强大、简洁和安全，减少了传统 switch 语句中常见的错误（如忘记 break 语句），同时提供了更强大的模式匹配能力，使代码更加清晰和易读。