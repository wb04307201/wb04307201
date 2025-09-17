# instanceof

| Java版本  | 新特性/增强内容                                |
|---------|-----------------------------------------|
| Java 8  | 传统 instanceof 操作符，仅支持类型检查               |
| Java 14 | JEP 305: instanceof 模式匹配（预览）- 引入模式变量    |
| Java 15 | JEP 375: instanceof 模式匹配（第二次预览）- 继续完善功能 |
| Java 16 | JEP 394: instanceof 模式匹配（正式特性）- 转正为标准特性 |
| Java 21 | 基本类型模式匹配（预览）- 扩展到基本类型                   |
| Java 23 | JEP 455: 基本类型模式匹配（预览）- 继续完善基本类型支持       |
| Java 25 | JEP 507: 基本类型模式匹配（第三次预览）- 进一步完善功能       |

## 功能详细介绍

### 1. Java 8 及之前版本 - 传统 instanceof 操作符

在 Java 8 及之前的版本中，instanceof 操作符仅用于类型检查，如果需要使用转换后的对象，必须进行显式的类型转换：

```java
Object obj = "Hello World";
if (obj instanceof String) {
    String str = (String) obj;  // 需要显式类型转换
    System.out.println(str.toUpperCase());
}
```


传统 instanceof 存在以下问题：
1. 需要显式类型转换，增加了代码冗余
2. 容易出现 ClassCastException（虽然在 instanceof 检查后不太可能）
3. 代码不够简洁

### 2. Java 14 - instanceof 模式匹配 (JEP 305 预览)

Java 14 引入了 instanceof 模式匹配的预览版本，这是 instanceof 操作符的第一个重大改进：

1. **模式变量**：在 instanceof 检查成功后，自动创建一个模式变量
2. **作用域限制**：模式变量仅在 if 语句的 true 分支中可用

```java
Object obj = "Hello World";
// 传统方式
if (obj instanceof String) {
    String str = (String) obj;
    System.out.println(str.toUpperCase());
}

// Java 14 模式匹配方式
if (obj instanceof String str) {  // 自动创建模式变量 str
    System.out.println(str.toUpperCase());  // 直接使用 str，无需显式转换
}
```


### 3. Java 15 - instanceof 模式匹配 (JEP 375 第二次预览)

Java 15 继续完善 instanceof 模式匹配功能：

1. **改进的作用域规则**：模式变量的作用域更加精确
2. **与其他逻辑操作符的结合**：更好地支持 && 和 || 操作符

```java
Object obj = "Hello World";
// 模式变量可以在 && 的右侧使用
if (obj instanceof String str && str.length() > 5) {
    System.out.println(str.toUpperCase());
}

// 在 || 操作符中的使用（注意作用域）
if (obj instanceof String str || obj instanceof Integer i) {
    // 这里不能直接使用 str 或 i，因为编译器无法确定哪个条件为真
}
```


### 4. Java 16 - instanceof 模式匹配 (JEP 394 正式特性)

Java 16 将 instanceof 模式匹配从预览特性转为标准特性：

1. **正式支持**：不再是预览特性，可以安全地在生产环境中使用
2. **更完善的作用域规则**：模式变量的作用域更加清晰和一致

```java
public class InstanceofPatternMatching {
    public static void main(String[] args) {
        Object obj = "Hello World";
        
        // 基本用法
        if (obj instanceof String str) {
            System.out.println(str.toUpperCase());
        }
        
        // 与逻辑操作符结合
        if (obj instanceof String str && str.length() > 5) {
            System.out.println("Long string: " + str);
        }
        
        // 在复合条件中使用
        Object anotherObj = 42;
        if (!(anotherObj instanceof String str)) {
            System.out.println("Not a string");
        }
    }
}
```


### 5. Java 21-25 - 基本类型模式匹配

从 Java 21 开始，instanceof 模式匹配功能进一步扩展到基本类型：

1. **基本类型支持**：允许在 instanceof 中直接使用基本类型
2. **统一的模式匹配语法**：基本类型和引用类型的模式匹配语法保持一致

```java
// Java 21+ 中的基本类型模式匹配示例
static void processObject(Object obj) {
    // 传统方式处理基本类型包装类
    if (obj instanceof Integer) {
        Integer i = (Integer) obj;
        System.out.println("Integer value: " + i);
    }
    
    // 使用基本类型模式匹配（Java 21+）
    if (obj instanceof int i) {  // 直接匹配 int 基本类型
        System.out.println("int value: " + i);
    }
    
    // 也可以匹配包装类型
    if (obj instanceof Integer integer) {
        System.out.println("Integer value: " + integer);
    }
}
```


### 6. Java 23 - 基本类型模式匹配增强 (JEP 455)

Java 23 继续完善基本类型模式匹配：

1. **扩展支持**：支持更多的基本类型模式匹配
2. **与 switch 表达式的结合**：更好地与 switch 模式匹配配合使用

```java
// Java 23 中的增强示例
static String formatValue(Object obj) {
    return switch (obj) {
        case Integer i -> String.format("int %d", i);
        case int i -> String.format("int primitive %d", i);  // 基本类型模式
        case Double d -> String.format("double %f", d);
        case double d -> String.format("double primitive %f", d);  // 基本类型模式
        case String s -> String.format("String %s", s);
        default -> obj.toString();
    };
}
```


### 7. Java 25 - 基本类型模式匹配 (JEP 507 第三次预览)

Java 25 进一步完善基本类型模式匹配功能：

1. **更完整的支持**：对所有基本类型提供一致的模式匹配支持
2. **更好的类型推断**：改进了编译器的类型推断能力

```java
// Java 25 中的完整示例
static void demonstratePrimitivePatterns(Object obj) {
    // 所有基本类型的模式匹配
    if (obj instanceof boolean b) {
        System.out.println("Boolean: " + b);
    } else if (obj instanceof byte b) {
        System.out.println("Byte: " + b);
    } else if (obj instanceof short s) {
        System.out.println("Short: " + s);
    } else if (obj instanceof int i) {
        System.out.println("Int: " + i);
    } else if (obj instanceof long l) {
        System.out.println("Long: " + l);
    } else if (obj instanceof float f) {
        System.out.println("Float: " + f);
    } else if (obj instanceof double d) {
        System.out.println("Double: " + d);
    } else if (obj instanceof char c) {
        System.out.println("Char: " + c);
    } else if (obj instanceof String s) {
        System.out.println("String: " + s);
    }
}
```


## 总结

instanceof 操作符从 Java 8 到 Java 25 经历了显著的演进：

1. **Java 14-16** 的模式匹配是第一个重大改进，引入了模式变量，消除了显式类型转换的需要
2. **Java 21-25** 扩展了模式匹配到基本类型，使 instanceof 更加强大和统一

这些改进使 instanceof 操作符变得更加强大、简洁和安全，减少了传统 instanceof 使用中的样板代码，同时提供了更强大的模式匹配能力，使代码更加清晰和易读。基本类型模式匹配的引入进一步完善了 Java 的模式匹配体系，为开发者提供了更加一致和强大的类型检查与转换能力。