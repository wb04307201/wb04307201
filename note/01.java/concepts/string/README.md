<!--
module:
  parent: java
  slug: java/string
  type: article
  category: 主模块子文章
  summary: String
-->

# String

## 引言：基础概念

String 是入门必学的基础概念。

本篇给出一句话定义 + 最小可运行示例 + 3 个常见误区，**5 分钟读完，10 分钟上手**。

---

## `String`的不可变性

`String`是不可变类，一旦创建就不能修改：

- 保存字符串的数组被`final`修饰且为私有
- `String`类本身被`final`修饰，不能被继承
- `String`类没有提供任何修改内部字符数组的方法

```java
String s = "Hello";
s.concat(" World");      // 创建新对象，原 s 不变
System.out.println(s);   // 仍然是 "Hello"

s = s.concat(" World");  // s 引用指向新对象 "Hello World"
```

## `String`、`StringBuffer`、`StringBuilder`的区别

### 对比总结

| 类型 | 可变性 | 线程安全 | 性能 |
|------|--------|---------|------|
| `String` | 不可变 | 天然线程安全 | 每次操作创建新对象，最慢 |
| `StringBuffer` | 可变 | 线程安全（`synchronized`） | 中等 |
| `StringBuilder` | 可变 | 非线程安全 | 最快（通常比`StringBuffer`快，具体比例因场景而异） |

### 使用场景总结

- **操作少量数据**：使用`String`
- **单线程操作大量字符串**：使用`StringBuilder`
- **多线程操作大量字符串**：使用`StringBuffer`

```java
// 性能对比
// 1. String - 每次拼接创建新对象
String s = "";
for (int i = 0; i < 10000; i++) {
    s += i;  // 极慢！每次创建新 String 对象
}

// 2. StringBuilder - 在原有对象上修改
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);  // 快！
}

// 3. StringBuffer - 同 StringBuilder，但加锁
StringBuffer sbuf = new StringBuffer();
for (int i = 0; i < 10000; i++) {
    sbuf.append(i);  // 线程安全，稍慢
}
```

### Java 9 将`String`底层实现由`char[]`改为`byte[]`

Java 9 引入了**Compact Strings**优化：

- 新`String`支持两种编码：Latin-1（ISO-8859-1）和 UTF-16
- 如果字符串中的所有字符都在 Latin-1 范围内（0~255），则使用`byte[]`存储（每字符1字节）
- 如果包含超出 Latin-1 范围的字符（如中文），则使用 UTF-16 编码的`byte[]`存储（每字符2字节）
- Latin-1 编码下`byte`比`char`节省一半内存

## 字符串常量池

字符串常量池是 JVM 为了提升性能和减少内存消耗而专门开辟的一块区域，主要目的是**避免字符串的重复创建**。

```java
String s1 = "abc";         // 从常量池获取（或创建后放入常量池）
String s2 = "abc";         // 从常量池获取，与 s1 是同一个对象
String s3 = new String("abc"); // 在堆中创建新对象

System.out.println(s1 == s2);  // true（同一常量池对象）
System.out.println(s1 == s3);  // false（不同对象）

String s4 = s3.intern();   // 返回常量池中的引用
System.out.println(s1 == s4);  // true
```

### `new String("abc")`创建了几个对象？

会创建 **1 或 2 个**字符串对象：

1. 如果字符串常量池中**不存在**"abc"：创建 2 个对象（一个放入常量池，一个由`new`在堆中创建）
2. 如果字符串常量池中**已存在**"abc"：只创建 1 个新对象（`new`出来的，常量池中已有）

## 字符串比较

### `equals()` vs `==`

- `==` 比较的是**引用**（是否指向同一个对象）
- `equals()` 比较的是**内容**（字符序列是否相同），`String` 重写了 `Object.equals()` 方法

```java
String s1 = "abc";
String s2 = new String("abc");

System.out.println(s1 == s2);        // false（不同对象）
System.out.println(s1.equals(s2));   // true（内容相同）
```

> **最佳实践**：比较字符串内容时始终使用 `equals()`，避免使用 `==`。

### `equalsIgnoreCase()`

忽略大小写比较字符串内容：

```java
"Hello".equalsIgnoreCase("hello");  // true
"Hello".equalsIgnoreCase("HELLO");  // true
```

### `compareTo()`

`String` 实现了 `Comparable<String>` 接口，`compareTo()` 按字典序比较，返回负数、零或正数：

```java
"apple".compareTo("banana");   // 负数（'a' < 'b'）
"apple".compareTo("apple");    // 0（相等）
"banana".compareTo("apple");   // 正数（'b' > 'a'）
```

> 如果需要忽略大小写的字典序比较，使用 `compareToIgnoreCase()`。

## 字符串常用方法

| 方法 | 说明 |
|------|------|
| `length()` | 返回字符串长度 |
| `charAt(int index)` | 返回指定位置的字符 |
| `substring(int begin, int end)` | 截取子串 |
| `indexOf(String str)` | 返回首次出现的索引，不存在返回 -1 |
| `contains(CharSequence s)` | 是否包含指定子串 |
| `startsWith(String prefix)` | 是否以指定前缀开头 |
| `endsWith(String suffix)` | 是否以指定后缀结尾 |
| `equals(Object o)` / `equalsIgnoreCase(String s)` | 内容比较（忽略大小写） |
| `compareTo(String s)` / `compareToIgnoreCase(String s)` | 字典序比较 |
| `trim()` / `strip()` | 去除首尾空白（`strip()`是Java 11+，支持Unicode空白） |
| `split(String regex)` | 按正则分割为数组 |
| `replace(CharSequence old, CharSequence new)` | 替换子串（字面量替换） |
| `replaceAll(String regex, String replacement)` | 按正则表达式替换所有匹配项 |
| `replaceFirst(String regex, String replacement)` | 按正则表达式替换首个匹配项 |
| `toLowerCase()` / `toUpperCase()` | 大小写转换 |
| `isEmpty()` / `isBlank()` | 是否为空/空白（`isBlank()`是Java 11+） |
| `String.format(String format, Object... args)` | 按格式化模板生成字符串（支持 `%s`、`%d`、`%f` 等占位符） |
| `String.join(CharSequence delimiter, CharSequence... elements)` | 用分隔符拼接多个字符串（Java 8+） |

### `String.format()` 示例

```java
String name = "Alice";
int age = 30;
String msg = String.format("Name: %s, Age: %d", name, age);
// "Name: Alice, Age: 30"
```

### `String.join()` 示例

```java
String result = String.join(", ", "apple", "banana", "cherry");
// "apple, banana, cherry"

List<String> list = List.of("a", "b", "c");
String joined = String.join("-", list);
// "a-b-c"
```

## 字符串拼接的底层实现

Java 编译器会将`+`号拼接优化为`StringBuilder`：

```java
// 编译器优化后等价于
String s = "a" + "b" + "c";
// 编译时常量拼接，直接优化为 "abc"

String a = "a";
String b = "b";
String c = a + b;
// 编译为：new StringBuilder().append(a).append(b).toString()
```

> **注意**：在循环中使用`+`拼接字符串仍然会每次创建新的`StringBuilder`，应在循环外创建一个`StringBuilder`并在循环内使用`append()`。

```java
// 反例：循环中使用 + 拼接（每次循环创建新的 StringBuilder）
String s = "";
for (int i = 0; i < 10000; i++) {
    s += i;  // 等价于 s = new StringBuilder().append(s).append(i).toString()
}

// 正例：循环外创建 StringBuilder，循环内 append
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);
}
String result = sb.toString();
```

## 文本块（Text Blocks）

Java 15 引入了**文本块**（Text Blocks），使用`"""`三引号语法来定义多行字符串，无需手动拼接换行符和转义引号。文本块在处理 JSON、SQL、HTML 模板等多行文本时非常实用。

传统写法：

```java
String json = "{\n" +
              "    \"name\": \"Alice\",\n" +
              "    \"age\": 30\n" +
              "}";
```

文本块写法（Java 15+），与上面的传统写法等价：

```java
String json = """
        {
            "name": "Alice",
            "age": 30
        }
        """;
```

文本块的基本规则：

- 以`"""`开头，以`"""`结尾，开头`"""`后必须换行
- 编译器会自动去除公共前导空白（以最左侧非空行为基准）
- 文本块内的双引号无需转义
- 可以使用`String`的所有方法（如`stripIndent()`、`formatted()`等）

---

← [返回 Java 核心概念](../README.md)
