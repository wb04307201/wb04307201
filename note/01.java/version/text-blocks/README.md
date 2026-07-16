<!--
module:
  parent: java
  slug: java/version/text-blocks
  type: article
  category: 主模块子文章
  summary: Java 13/15 Text Blocks：多行字符串字面量。
-->

# Text Blocks

## 引言：变更说明

Text Blocks 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 功能描述

Text Blocks（文本块）是 Java 15 转正的多行字符串字面量语法，使用 `"""` 作为定界符。它消除了多行字符串中繁琐的 `+` 拼接和 `\n` 转义，使 SQL 查询、JSON、HTML、XML 等多行文本的编写更加直观和可维护。

## 基本用法（最新，Java 21+）

```java
// 1. 基本多行字符串
String html = """
    <html>
        <body>
            <p>Hello, World!</p>
        </body>
    </html>
    """;

// 2.  incidental 缩进（自动去除公共前缀空格）
// 编译器会自动检测最左侧非空白字符的位置，去除公共缩进
String json = """
    {
        "name": "Alice",
        "age": 30,
        "skills": ["Java", "Python"]
    }
    """;
// 实际内容从第一列开始，没有前导空格

// 3. 显式控制缩进（使用 \s 保留尾部空格）
String table = """
    Name  | Age | City\s\s
    ------|-----|--------
    Alice |  30 | Beijing
    Bob   |  25 | Shanghai
    """;

// 4. 嵌入式表达式（Java 21+ 模板表达式，预览中）
// String greeting = STR."Hello, \{name}!";  // 模板表达式是单独的特性

// 5. 无需转义的内容
String path = """
    C:\Users\wb04307201\Documents
    """;
// 注意：\U 和 \u 等特殊转义序列仍需注意，但大部分反斜杠不需要转义

// 6. 连接其他字符串
String query = """
    SELECT u.name, u.email
    FROM users u
    WHERE u.status = 'ACTIVE'
    ORDER BY u.created_at DESC
    """ + " LIMIT " + pageSize;

// 7. 空文本块
String empty = """
    """;  // 空字符串 ""

// 8. 尾部空格处理（默认会去除每行尾部空格）
String withSpaces = """
    line1   
    line2   
    """.indent(0);  // 使用 indent() 保留或控制缩进
```

## 变更历史表

| Java版本  | 新特性/增强内容                                           |
|---------|----------------------------------------------------|
| Java 21 | 模板表达式首次预览（与文本块配合使用，STR 内联模板）                |
| Java 15 | JEP 378: Text Blocks 转正为标准特性                      |
| Java 14 | JEP 368: Text Blocks 第二次预览 - 新增 \s 转义和文本块处理方法     |
| Java 13 | JEP 355: Text Blocks 首次预览 - 引入 """ 多行字符串语法          |

## 功能详细介绍

### 1. Java 13 - Text Blocks 首次预览 (JEP 355)

首次引入 `"""` 定界符的多行字符串语法：

```java
// 之前：繁琐的拼接
String sql = "SELECT id, name\n" +
             "FROM users\n" +
             "WHERE status = 'ACTIVE'";

// 现在：直观的文本块
String sql = """
    SELECT id, name
    FROM users
    WHERE status = 'ACTIVE'
    """;
```

特点：
- 自动处理换行符（使用 `\n`）
- 自动去除公共缩进（incidental whitespace）
- 双引号不需要转义

### 2. Java 14 - Text Blocks 第二次预览 (JEP 368)

新增功能：
- **`\s` 转义序列**：表示单个空格，阻止尾部空格被修剪
- **文本块处理方法**：`String` 类新增 `stripIndent()`、`translateEscapes()`、`formatted(Object... args)` 等方法

```java
String formatted = """
    Name: %s
    Age: %d
    """.formatted("Alice", 30);

// stripIndent - 手动去除公共缩进
// translateEscapes - 处理转义序列
```

### 3. Java 15 - Text Blocks 转正 (JEP 378)

Text Blocks 成为标准特性。与 Java 14 相比无功能变化，API 稳定。

### 4. Java 21 - 模板表达式预览（配合使用）

模板表达式（JEP 430）与文本块结合使用：

```java
String name = "Alice";
String greeting = STR."Hello, \{name}!";

String json = STR."""
    {
        "name": "\{name}",
        "timestamp": "\{System.currentTimeMillis()}"
    }
    """;
```

注意：模板表达式是独立的特性，文本块本身已是标准特性。

## Text Blocks vs 传统多行字符串

| 方面       | 传统方式                            | Text Blocks                     |
|----------|---------------------------------|---------------------------------|
| 可读性      | 差（需要 + 拼接和 \n）                    | 优（直接编写多行文本）                     |
| 引号转义     | 双引号需要 `\"`                       | 不需要                              |
| 缩进处理     | 手动控制                              | 自动去除公共缩进                        |
| 尾部空格     | 保留                                | 默认去除（可用 `\s` 保留）                |
| 格式化      | `String.format()`                | `.formatted()` 便捷方法             |

## 总结

Text Blocks 从 Java 13 预览到 Java 15 转正，彻底改变了 Java 中多行字符串的编写体验。它是开发者感知最强的语法改进之一，显著提升了 SQL、JSON、HTML 等文本的可读性。

---

← [返回 功能版本变更历史](../README.md)
