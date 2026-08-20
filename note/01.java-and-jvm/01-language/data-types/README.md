<!--
module:
  parent: java
  slug: java/concepts/data-types
  type: article
  category: 主模块子文章
  summary: Java 基本数据类型：8 大类型、自动装箱、缓存池。
-->

# 基本数据类型

> **定位**：Java 基本数据类型：8 大类型、自动装箱、缓存池。 的核心原理、实现与最佳实践。

---

## Java 中的8种基本数据类型

```text
8 种基本数据类型
├─ 6 种数字类型
│  ├─ 4 种整数型 ： byte、short、int、long
│  └─ 2 种浮点型 ： float、double
├─ 1 种字符类型 ： char
└─ 1 种布尔型 ： boolean
```

8 种基本数据类型的默认值以及所占空间的大小：

| 基本类型    | 位数 | 字节 | 默认值      | 取值范围                                                       |
|---------|----|----|----------|------------------------------------------------------------|
| byte    | 8  | 1  | 0        | -128 ~ 127                                                 |
| short   | 16 | 2  | 0        | -32768(-2^15) ~ 32767(2^15 - 1)                            |
| int     | 32 | 4  | 0        | -2147483648 ~ 2147483647                                   |
| long    | 64 | 8  | 0L       | -9223372036854775808(-2^63) ~ 9223372036854775807(2^63 - 1) |
| char    | 16 | 2  | '\u0000' | '\u0000' ~ '￿'(2^16 - 1)                          |
| float   | 32 | 4  | 0.0f     | ±1.4E-45 ~ ±3.4028235E38                                   |
| double  | 64 | 8  | 0.0d     | ±4.9E-324 ~ ±1.7976931348623157E308                        |
| boolean | 1  | —  | false    | true、false                                                 |

> `boolean` 在 JVM 中没有明确规定占用空间大小，在`boolean`数组中使用`byte`数组编码（1字节），在`boolean`变量中使用`int`（4字节）。

## 基本类型和包装类型的区别

| 对比维度 | 基本类型 | 包装类型 |
|---------|---------|---------|
| **用途** | 局部变量、常量定义 | 方法参数、对象属性、泛型参数 |
| **存储方式** | 局部变量在栈中，成员变量在堆中 | 对象实例存在于堆中 |
| **占用空间** | 较小（1~8字节） | 较大（对象头+字段值） |
| **默认值** | 有默认值（如`int`为0） | 默认值为`null` |
| **比较方式** | `==`比较值 | `==`比较内存地址，`equals()`比较值 |

```java
// 基本类型 vs 包装类型的比较
int a = 100;
int b = 100;
System.out.println(a == b);  // true（比较值）

Integer x = 100;
Integer y = 100;
System.out.println(x == y);      // true（缓存范围内，同一对象）
System.out.println(x.equals(y)); // true（比较值）

Integer m = 200;
Integer n = 200;
System.out.println(m == n);      // false（超出缓存范围，不同对象）
System.out.println(m.equals(n)); // true（比较值）
```

## 包装类型的缓存机制

Java 基本数据类型的包装类大部分都实现了缓存机制来提升性能：

| 包装类 | 缓存范围 | 说明 |
|-------|---------|------|
| `Byte` | [-128, 127] | byte 本身范围就是 -128~127 |
| `Short` | [-128, 127] | 仅缓存此范围 |
| `Integer` | [-128, 127] | 可通过`-XX:AutoBoxCacheMax`调整上限 |
| `Long` | [-128, 127] | 仅缓存此范围 |
| `Character` | [0, 127] | ASCII 范围 |
| `Boolean` | `TRUE`/`FALSE` | 直接返回常量实例 |

> `Float`和`Double`**没有**缓存机制，因为浮点数的取值范围太大，无法有效缓存。

## 自动装箱与拆箱

- **装箱（Autoboxing）**：将基本类型自动转换为对应的包装类型
- **拆箱（Unboxing）**：将包装类型自动转换为对应的基本类型

```java
// 自动装箱 - 编译器实际调用 Integer.valueOf(int)
Integer a = 10;

// 自动拆箱 - 编译器实际调用 a.intValue()
int b = a;

// 陷阱：拆箱空指针
Integer c = null;
int d = c;  // NullPointerException!
```

> 频繁拆装箱会严重影响系统性能，应该尽量避免不必要的拆装箱操作，特别是在循环中。

## 浮点数运算精度丢失

浮点数精度丢失与计算机以二进制存储浮点数的机制有关。计算机在表示一个数字时宽度是有限的，无限循环的小数存储在计算机时只能被截断，所以会导致小数精度损失。

```java
System.out.println(0.1 + 0.2);  // 0.30000000000000004（不是0.3！）
System.out.println(1.0 - 0.8);  // 0.19999999999999996（不是0.2！）
```

**解决方案**：使用`BigDecimal`

```java
// import java.math.BigDecimal;
BigDecimal a = new BigDecimal("0.1");
BigDecimal b = new BigDecimal("0.2");
System.out.println(a.add(b));  // 0.3

// 注意：必须使用 String 构造方法，不能使用 double 构造方法
// 错误：new BigDecimal(0.1) 仍然会有精度问题

// 推荐写法：BigDecimal.valueOf(double)
BigDecimal c = BigDecimal.valueOf(0.1);
BigDecimal d = BigDecimal.valueOf(0.2);
System.out.println(c.add(d));  // 0.3
// valueOf(double) 相比 new BigDecimal(double) 的优势在于内部先调用 Double.toString(double)，
// 能将 double 转为最简洁的十进制字符串表示，避免直接使用 double 构造带来的精度问题。
// 注意：valueOf(double) 内部先调用 Double.toString(double) 再构造，因此不会有精度问题。
```

## 类型转换（Casting）

Java 中基本数据类型之间的转换分为两种：**隐式扩展转换**（自动、安全）和**显式窄化转换**（强制、可能溢出）。

### 隐式扩展转换（Widening）

小范围类型赋值给大范围类型时，Java 自动完成转换，无需任何语法标记，且不会丢失数据。

```text
自动类型提升链：
byte → short → int → long → float → double
char → int
```

```java
int a = 100;
long b = a;      // int → long，自动提升，安全
double c = a;    // int → double，自动提升，安全
double d = 3.14f; // float → double，自动提升，安全
```

### 显式窄化转换（Narrowing / Casting）

大范围类型赋值给小范围类型时，必须使用强制转换运算符 `(type)`，编译器不会自动完成，且存在溢出和精度丢失风险。

```java
long x = 100000L;
int y = (int) x;   // long → int，需强制转换

double pi = 3.14;
int n = (int) pi;  // double → int，小数部分被截断，n = 3

float f = 3.14f;
byte bt = (byte) f; // float → byte，截断且可能溢出
```

### 溢出风险

强制窄化转换不会抛出异常，而是在超出目标类型范围时静默截断高位字节，导致结果与预期不符，属于隐蔽 bug。

```java
int max = Integer.MAX_VALUE;   // 2147483647
long overflow = max + 1L;      // 正确：2147483648（long 范围）
int danger = (int) overflow;   // 危险！结果：-2147483648（溢出为负数）

// 安全做法：转换前做范围检查，或使用 Math.toIntExact()
int safe = Math.toIntExact(overflow); // 抛出 ArithmeticException，而非静默溢出
```

### 算术运算中的自动类型提升

Java 在进行 `byte`、`short`、`char` 的算术运算时，会自动将它们提升为 `int` 再计算，因此运算结果是 `int` 类型，不能再直接赋回给 `byte`/`short`/`char`。

```java
byte a = 1;
byte b = 2;
// byte c = a + b;   // 编译错误！a + b 的结果是 int
byte c = (byte) (a + b);  // 需要强制转换

// 特例：使用 += 复合赋值运算符时，编译器会自动插入强制转换
byte d = 10;
d += 5;  // 等价于 d = (byte)(d + 5)，编译通过
```

> **最佳实践**：尽量使用 `int` 作为整数运算的默认类型，避免频繁窄化转换；涉及金额计算时使用 `BigDecimal`（见上文）；必须窄化转换时用 `Math.toIntExact()` 等方法检测溢出。

## 使用`BigInteger`处理超过`long`范围的数据

`BigInteger`内部使用`int[]`数组来存储任意大小的整型数据，支持所有基本算术运算。

```java
// import java.math.BigInteger;
BigInteger big = new BigInteger("123456789012345678901234567890");
BigInteger result = big.multiply(big);
System.out.println(result);
```

> `BigInteger`和`BigDecimal`运算效率相对较低，适用于对精度要求高于性能要求的场景（如金融计算）。

---


## 相关章节

- [Java 并发工具类 (java.util.concurrent)](../../03-concurrency/utilities/README.md)
- [ThreadLocal 原理与最佳实践](../../03-concurrency/threadlocal/README.md)
- [LinkedList 源码剖析与最佳实践](../../collection/LinkedList/README.md)

## 速记卡：split-hairs 视角 — 为什么需要包装类？

> 本节由 `12.interview/01.java/object/` 迁出，整合"为什么需要 Integer/Double 这类包装类"的 7 大设计动机（主模块已讲过基本类型 vs 包装类型对比，本节聚焦**why**）。

**7 大设计动机速记：**

| # | 动机 | 本质 |
|---|------|------|
| 1 | 泛型约束：`List<int>` 不合法 | 基本类型无法作为类型参数 |
| 2 | 集合元素：`Map<K, Integer>` | 集合框架只接受对象 |
| 3 | null 支持：`Integer age = null` | 基本类型有默认值 0，无法表达"未赋值" |
| 4 | OOP 特性：`Integer.parseInt()`、`MAX_VALUE` | 对象能调用方法、暴露常量、继承多态 |
| 5 | 反射机制：`Integer.class` vs `int.class` | 反射需要 `Class` 对象 |
| 6 | 泛型擦除兼容：`List<Integer>` 擦除为 `Object` | 基本类型无法参与擦除规则 |
| 7 | ORM 映射：`@Column(nullable=true) Integer age` | 区分"0"和"null"，数据库字段语义 |

**一句话总结**：「Java 设计者知道 `int` 比 `Integer` 快 5 倍，但为了**纯面向对象一致性**，宁可承担装箱开销——性能问题用 `Integer.valueOf()` 缓存 + 逃逸分析去优化。」

### 3 大反直觉陷阱

```java
// 陷阱 1：NullPointerException — 自动拆箱的隐形 NPE
Integer num = getNullableInteger();  // 可能返回 null
int value = num;                     // ❌ NPE！拆箱 null → int 失败

// 陷阱 2：== 比较超范围 Integer
Integer a = 1000, b = 1000;
System.out.println(a == b);          // ❌ false（超出 -128~127 缓存，不同对象）
System.out.println(a.equals(b));     // ✅ true

// 陷阱 3：WeakHashMap + Integer key → 缓存被 GC 静默回收
Map<Integer, String> cache = new WeakHashMap<>();
cache.put(new Integer(1), "value");  // ❌ Integer 是 final，JVM 可能缓存，也可能 GC 回收
```

### 30 秒面试话术

> "Java 用包装类解决 3 个核心问题：**泛型参数必须是对象**（`List<int>` 编译报错）、**支持 null 表达"无值"**（基本类型只能用默认值 0）、**集合框架只接受对象**。代价是装箱/拆箱开销，JVM 通过 `Integer.valueOf()` 缓存 [-128,127] 和逃逸分析做优化。"

### 面试反问（高频追问）

- **Q：`Integer a = 1000; Integer b = 1000; a == b` 为什么是 false？** A：超出 `Integer.IntegerCache.high`（默认 127）范围时，`valueOf()` 不会从缓存池拿，会 `new` 新对象，所以 `==` 比较的是不同对象地址。
- **Q：能不能扩大缓存范围？** A：可以，通过 JVM 参数 `-XX:AutoBoxCacheMax=1000`（仅 Integer 有效），但需谨慎，可能撑爆 metaspace/堆。
- **Q：包装类在 JPA 实体里必须用基本类型还是包装类？** A：**包装类**——JPA 需要用 `null` 表达"未赋值"状态，基本类型 0 无法与 null 区分。

---

← [返回 Java 核心概念](../README.md)
