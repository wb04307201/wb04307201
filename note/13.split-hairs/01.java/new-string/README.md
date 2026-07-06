<!--
question:
  id: 01.java-new-string
  topic: 01.java
  difficulty: 未标
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [01.java, new, string]
-->

# `new String("123")` 创建几个对象？

## 引子：一道经典面试题

面试官：**`String s = new String("123");` 创建了几个对象？**

你可能脱口而出：**1 个！**

错！答案可能是 **1 个**，也可能是 **2 个**，取决于执行时的上下文环境。

这道题看似简单，实则暗藏玄机，考察的是对**字符串常量池**、**堆内存布局**和 **JVM 优化机制**的深度理解。

---

## 一、核心原理

> 📚 **前置知识**：[String](../../../01.java/concepts/string/README.md) | [JVM 内存](../../../01.java/jvm/README.md)

`String str = new String("123");` 是 Java 面试中的经典题目，考察对**字符串常量池（String Pool）**、**堆内存布局**和**JVM 优化机制**的理解。答案取决于执行时的上下文环境：

### 场景分解

**情况 1：常量池中不存在 `"123"`（首次执行）**
- **步骤 1**：JVM 处理字面量 `"123"`，在字符串常量池中创建一个 String 对象（若池中已存在则跳过此步）。
- **步骤 2**：`new` 关键字在堆中创建一个新的 String 对象，其内部的 `byte[] value` 数组引用指向常量池中 `"123"` 的字符数据（Java 9+ 之前是共享 `char[]`，之后是独立 `byte[]`）。
- **结果**：共创建 **2 个对象**（常量池 1 个 + 堆中 1 个）。

**情况 2：常量池中已存在 `"123"`（重复执行）**
- **步骤 1**：字面量 `"123"` 已在常量池中，无需新建。
- **步骤 2**：`new` 关键字仍在堆中创建新的 String 对象。
- **结果**：仅创建 **1 个对象**（堆中 1 个）。

### JVM 内存布局关键点
- **字符串常量池的位置**：Java 6 及以前位于方法区（永久代），Java 7 移至堆内，Java 8 以后永久代被元空间取代，字符串常量池完全驻留在堆中。因此，"常量池中的对象"也属于堆内存对象。
- **`new String()` 的强制新建**：与直接赋值 `String s = "123"` 不同（直接从常量池返回引用），`new String("123")` 无论内容是否相同，都会在堆中创建新对象，地址必然不同。
- **Java 9+ 的 Compact Strings**：从 Java 9 开始，String 内部从 `char[]` 改为 `byte[]` + `coder`，`new String()` 创建的对象拥有独立的 `byte[]` 副本，不再与常量池共享数组。

---

## 二、代码示例

以下代码验证对象创建数量和引用关系：

```java
public class StringPoolTest {
    public static void main(String[] args) {
        // ==================== 实验1：基本对比 ====================
        String s1 = "123";              // 常量池中查找或创建
        String s2 = new String("123");  // 堆中新建
        String s3 = new String("123");  // 堆中再新建

        System.out.println(s1 == s2);   // false（s1在常量池，s2在堆）
        System.out.println(s2 == s3);   // false（两个不同的堆对象）
        System.out.println(s1.equals(s2)); // true（内容相同）

        // ==================== 实验2：intern() 的作用 ====================
        String s4 = new String("456").intern(); // 手动将堆中对象放入常量池
        String s5 = "456";                       // 直接从常量池获取

        System.out.println(s4 == s5);   // true（都指向常量池）

        // ==================== 实验3：Java 9+ 的 byte[] 独立性 ====================
        // 通过反射验证 new String() 创建独立的 value 数组
        String s6 = "789";
        String s7 = new String("789");

        try {
            java.lang.reflect.Field valueField = String.class.getDeclaredField("value");
            valueField.setAccessible(true);

            byte[] value6 = (byte[]) valueField.get(s6);
            byte[] value7 = (byte[]) valueField.get(s7);

            System.out.println(value6 == value7); // false（Java 9+ 独立数组）
        } catch (Exception e) {
            e.printStackTrace();
        }

        // ==================== 实验4：性能对比 ====================
        long start = System.nanoTime();
        for (int i = 0; i < 1_000_000; i++) {
            String s = new String("test"); // 每次创建新对象
        }
        long end = System.nanoTime();
        System.out.println("new String: " + (end - start) / 1_000_000 + " ms");

        start = System.nanoTime();
        for (int i = 0; i < 1_000_000; i++) {
            String s = "test"; // 复用常量池
        }
        end = System.nanoTime();
        System.out.println("literal: " + (end - start) / 1_000_000 + " ms");
    }
}
```

**典型输出**（Java 11 环境）：
```
false
false
true
true
false
new String: 45 ms
literal: 2 ms
```

---

## 三、常见陷阱

### 1. 误认为 `new String()` 只在堆中创建对象
很多开发者知道 `new` 在堆中创建对象，但忽视了字面量 `"123"` 本身也会触发常量池的创建。关键在于：**字面量的处理发生在编译期或类加载期，`new` 的执行发生在运行期**，两者是分开的。

### 2. 混淆 `==` 和 `equals()`
```java
String a = "hello";
String b = new String("hello");
System.out.println(a == b);      // false（比较引用地址）
System.out.println(a.equals(b)); // true（比较内容）
```
`==` 比较的是对象在堆中的内存地址，`equals()` 比较的是字符序列。对于 String，应始终使用 `equals()` 进行内容比较。

### 3. 忽视 `intern()` 的副作用
`intern()` 会将堆中对象的引用注册到常量池，若常量池已满（在 Java 6 及以前有大小限制），可能触发 `OutOfMemoryError`。在 Java 7+ 中，常量池动态扩容，但仍需注意内存占用。

### 4. 在循环中滥用 `new String()`
```java
// 反模式：每次迭代创建新对象
for (int i = 0; i < 10000; i++) {
    String s = new String("prefix_" + i); // 浪费内存
}

// 推荐：直接使用字面量或 StringBuilder
for (int i = 0; i < 10000; i++) {
    String s = ("prefix_" + i).intern(); // 或直接用字符串拼接
}
```

### 5. 误认为字符串拼接会产生多个对象
现代 JVM 会对字符串拼接进行优化：
```java
String s = "Hello" + " " + "World"; // 编译器优化为单个常量 "Hello World"
```
但若涉及变量，则无法完全优化：
```java
String prefix = "Hello";
String s = prefix + " World"; // 运行时创建新对象（通过 StringBuilder）
```

---

## 四、最佳实践

### 1. 优先使用字面量赋值
```java
// ✅ 推荐：直接从常量池获取，无额外开销
String s = "hello";

// ❌ 不推荐：强制创建冗余对象
String s = new String("hello");
```

### 2. 谨慎使用 `intern()`
`intern()` 适用于需要大量重复字符串的场景（如数据解析、符号表），但需注意：
- Java 6：常量池在永久代，大小有限（默认 1~4 MB），慎用 `intern()`。
- Java 7+：常量池在堆中，可自动扩容，但仍可能引发 GC 问题。
- 建议：仅在字符串重复率高的场景使用，并监控堆内存。

### 3. 使用 `StringBuilder` 进行动态拼接
```java
// ✅ 高效拼接
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append("item_").append(i).append(",");
}
String result = sb.toString();

// ❌ 低效：每次拼接创建新 String 对象
String result = "";
for (int i = 0; i < 1000; i++) {
    result += "item_" + i + ","; // O(n²) 复杂度
}
```

### 4. 利用 Compact Strings 特性
Java 9+ 的 Compact Strings 自动选择 `byte[]` 或 `char[]` 存储：
- 纯 ASCII 字符串：使用 `byte[]`，节省 50% 空间。
- 包含非 ASCII 字符：使用 `byte[]` + UTF-16 编码。
无需手动优化，JVM 自动处理。

### 5. 字符串比较的统一规范
```java
// ✅ 安全比较：防止 NPE
if ("expected".equals(actual)) { ... }

// ✅ 忽略大小写
if ("admin".equalsIgnoreCase(input)) { ... }

// ❌ 危险：可能抛出 NullPointerException
if (actual.equals("expected")) { ... }
```

---

## 五、面试话术

**面试官**："`String str = new String("123")` 创建几个对象？"

**参考回答**：
> "这取决于常量池中是否已经存在 `"123"`。
>
> 如果是首次执行，常量池中没有 `"123"`，那么会创建 2 个对象：一个是常量池中的 `"123"`，另一个是堆中通过 `new` 创建的 String 实例。如果常量池中已经有 `"123"`（比如之前执行过 `String s = "123"`），那么只会在堆中创建 1 个新对象。
>
> 这里的关键点是：字面量 `"123"` 会触发常量池的操作，而 `new` 关键字强制在堆中创建新对象，两者的地址一定不同。所以 `new String("123") == "123"` 永远返回 false。
>
> 另外需要注意的是，从 Java 9 开始，String 内部从 `char[]` 改成了 `byte[]`，`new String()` 创建的对象拥有独立的字节数组副本，不再与常量池共享底层数据。这也是为什么在实际开发中，我们应该优先使用字面量赋值，避免用 `new String()` 制造垃圾对象。"

**追问**："如何验证创建了几个对象？"
> "可以通过 `jstat -gcutil` 观察 GC 前后的对象数量变化，或者使用 JOL（Java Object Layout）工具分析对象布局。更简单的方式是通过代码验证：比较 `==` 的结果，如果两次 `new String("123")` 的地址不同，说明堆中创建了独立对象。"

---

## 六、交叉引用

- String 源码分析见 [Java 核心类库](../../../01.java/concepts/string/README.md)
- StringBuilder 性能分析见 [集合与工具类](../../../01.java/collection/README.md)

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · new-string](README.md)
