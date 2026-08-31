<!--
question:
  id: 01.java-integer-cache
  topic: 01.java
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [01.java, integer, cache]
-->

# Integer缓存

> **一句话定位**：-128~127 整数对象池 —— 自动装箱命中缓存复用，`==` 看似相等但范围外即踩坑，必须用 equals。

## 引子：一个让人困惑的现象

先来看一段简单的代码：

```java
Integer a = 100;
Integer b = 100;
System.out.println(a == b); // 你猜是 true 还是 false？
```

运行结果：`true` ✓ 这符合直觉，两个值相同的对象应该相等。

但再看这段：

```java
Integer a = 1000;
Integer b = 1000;
System.out.println(a == b); // 这次呢？
```

运行结果：`false` ！！！

同样的代码，只是数值从 100 变成了 1000，结果就完全不同了。这是为什么？

答案就藏在 Java 的 **Integer 缓存机制** 中。接下来让我们一起揭开这个谜团。

---

## 一、核心原理

> 📚 **前置知识**：[基本数据类型与包装类](../../../01.java-and-jvm/01-language/data-types/README.md)

1. **缓存范围**
    - 默认缓存 **-128 到 127** 之间的整数对象。该范围基于实际开发中高频使用的小整数场景设计。
    - 可通过JVM参数 `-XX:AutoBoxCacheMax=<size>` 调整上限（如设为200，则范围变为-128到200），但需谨慎以避免内存浪费。

2. **复用机制**
    - 当通过 `Integer.valueOf(int)` 或自动装箱（如 `Integer a = 100;`）创建对象时：
        - 若值在缓存范围内，直接返回缓存池中的对象（**同一内存地址**）。
        - 若值超出范围，则新建对象（不同内存地址）。

## 二、实现细节
1. **IntegerCache内部类**
    - `Integer` 类通过静态嵌套类 `IntegerCache` 管理缓存，其核心代码如下：
      ```java
      private static class IntegerCache {
          static final int low = -128;
          static final int high; // 默认127，可通过JVM参数调整
          static final Integer[] cache;
          static {
              high = 127; // 默认值
              String prop = VM.getSavedProperty("java.lang.Integer.IntegerCache.high");
              if (prop != null) {
                  int i = parseInt(prop);
                  high = Math.min(i, Integer.MAX_VALUE - (-low) - 1);
              }
              cache = new Integer[(high - low) + 1];
              for (int j = 0; j < cache.length; j++) {
                  cache[j] = new Integer(low + j);
              }
          }
      }
      ```

2. **valueOf方法逻辑**
    - `Integer.valueOf(int i)` 方法是缓存复用的入口：
      ```java
      public static Integer valueOf(int i) {
          if (i >= IntegerCache.low && i <= IntegerCache.high) {
              return IntegerCache.cache[i + (-IntegerCache.low)];
          }
          return new Integer(i);
      }
      ```

**为什么需要缓存？** 在Java早期版本中，每次装箱都会创建新对象，对于频繁使用小整数的程序（如循环计数器），会产生大量临时对象增加GC压力。引入缓存后，-128到127范围内的Integer对象可以复用，显著减少内存分配。

## 三、使用场景与示例
1. **自动装箱与缓存复用**
   ```java
   Integer a = 127;  // 缓存范围内
   Integer b = 127;
   System.out.println(a == b); // true（同一对象）

   Integer c = 128;  // 超出缓存范围
   Integer d = 128;
   System.out.println(c == d); // false（新建对象）
   ```

2. **显式调用valueOf**
   ```java
   Integer x = Integer.valueOf(100);  // 缓存复用
   Integer y = Integer.valueOf(100);
   System.out.println(x == y); // true
   ```

3. **new关键字绕过缓存**
   ```java
   Integer m = new Integer(100);  // 强制新建对象
   Integer n = new Integer(100);
   System.out.println(m == n); // false
   ```

**自动装箱的底层实现：** Java编译器会将自动装箱代码转换为`valueOf()`调用。例如 `Integer a = 100;` 会被编译为 `Integer a = Integer.valueOf(100);`，而非 `new Integer(100);`。这就是为什么自动装箱能利用缓存的原因。

## 四、注意事项
1. **对象比较陷阱**
    - **错误用法**：使用 `==` 比较 `Integer` 对象（仅当值在缓存范围内且未使用 `new` 时可能为 `true`）。
    - **正确做法**：始终使用 `equals()` 方法或拆箱后比较：
      ```java
      Integer num1 = 200;
      Integer num2 = 200;
      System.out.println(num1.equals(num2)); // true
      System.out.println(num1.intValue() == num2.intValue()); // true
      ```

2. **缓存范围调整风险**
    - 扩大缓存范围（如设为200）会占用更多内存，需权衡性能与内存消耗。
    - 最大缓存上限受 `Integer.MAX_VALUE - (-low) - 1` 限制（约2^31 - 129）。

3. **其他包装类的缓存**
    - `Byte`、`Short`、`Character`、`Long`、`Boolean` 也有类似缓存机制，但范围或实现细节可能不同（如 `Character` 缓存0-127）。
    - `Float` 和 `Double` 无缓存机制。

**各包装类缓存范围对比：**

| 包装类 | 缓存范围 | 可配置 |
|--------|---------|-------|
| Boolean | TRUE, FALSE | 否 |
| Byte | -128 ~ 127 | 否 |
| Short | -128 ~ 127 | 否 |
| Character | 0 ~ 127 | 否 |
| Integer | -128 ~ 127 | 是（上限） |
| Long | -128 ~ 127 | 否 |

## 五、常见陷阱

### 陷阱 1：缓存范围边界问题

**真相**：缓存范围是 -128 ~ 127，**边界值 -128 仍在缓存内**，但 -129 会新建对象。面试常考边界值判断。

```java
Integer a = -128;
Integer b = -128;
System.out.println(a == b); // true（边界内）

Integer c = -129;
Integer d = -129;
System.out.println(c == d); // false（超出下界）
```

### 陷阱 2：反射修改缓存导致的诡异行为

**真相**：反射可以篡改 IntegerCache 数组，导致 `42 + 1 = 1000` 这种反直觉结果。生产环境绝对禁止；且 **Java 9+ 的 JPMS 模块系统默认封禁对 `java.lang` 的深层反射**（需 `--add-opens`），面试应主动提及版本演进。

```java
// 危险操作：通过反射修改缓存值（Java 8 可行，Java 9+ 需 --add-opens java.base/java.lang=ALL-UNNAMED）
Integer[] cache = getIntegerCache();
cache[128 + 42] = new Integer(999); // 将42的缓存改为999

System.out.println(Integer.valueOf(42)); // 输出999！
System.out.println(42 + 1); // 输出1000！因为42被改为999
```

这种操作会导致程序行为完全不可预测，生产环境中绝对禁止。

### 陷阱 3：反序列化破坏缓存

**真相**：反序列化永远新建对象，**不走 valueOf() 缓存入口**。即使值在 -128~127 范围内，`==` 也返回 false。

```java
// 反序列化会创建新的Integer对象，不走缓存
ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("obj.ser"));
oos.writeObject(Integer.valueOf(100));
oos.close();

ObjectInputStream ois = new ObjectInputStream(new FileInputStream("obj.ser"));
Integer deserialized = (Integer) ois.readObject();
System.out.println(deserialized == Integer.valueOf(100)); // false
```

## 六、性能优化意义
- **减少内存分配**：高频使用的小整数对象复用缓存，避免重复创建。
- **降低GC压力**：缓存对象不会被垃圾回收，减少GC频率。
- **提升运算效率**：在循环、计数等场景中，缓存复用显著提高性能。

**性能测试示例：**

```java
// 使用缓存：约50ms
long start = System.currentTimeMillis();
for (int i = 0; i < 1_000_000; i++) {
    Integer a = i % 100; // 大部分在缓存范围内
}
System.out.println(System.currentTimeMillis() - start);

// 不使用缓存（new）：约200ms
start = System.currentTimeMillis();
for (int i = 0; i < 1_000_000; i++) {
    Integer a = new Integer(i % 100);
}
System.out.println(System.currentTimeMillis() - start);
```

**总结**：Integer缓存机制通过复用小整数对象优化性能，但需注意对象比较方式和缓存范围调整的风险。在开发中应优先使用 `equals()` 比较对象，并谨慎扩展缓存上限。

**面试要点：**
1. Integer缓存的范围和配置方式
2. 自动装箱的底层实现（valueOf vs new）
3. 各包装类的缓存范围对比
4. 缓存带来的性能提升原理
5. 常见的Integer比较陷阱

## 相关章节

- 深度阅读：[`01.java/核心概念`](../../../01.java-and-jvm/01-language/README.md) — 基本类型、自动装箱/拆箱
- 数据类型详解：[`01.java/基本数据类型与包装类`](../../../01.java-and-jvm/01-language/data-types/README.md) — 8 种基本类型 + 缓存机制源码
- 相关：[`13.split-hairs/new-string`](../new-string/README.md) — 字符串常量池（同类型考点）
- 数据库 INT 列映射：[`03.data-stack/01-database`](../../../03.data-stack/01-database/README.md) — INT/BIGINT 类型与 Java 包装类选型

## 💡 面试话术

**30 秒话术**：

> "Integer 默认缓存 -128~127，`valueOf()` 和自动装箱走缓存，`new` 不走。范围外必新建对象，`==` 比较会踩坑——**永远用 `equals()` 比较包装类**。"

**90 秒话术**：

> "Java 为高频小整数设计了 IntegerCache（-128~127，上限可用 `-XX:AutoBoxCacheMax` 调整）。自动装箱 `Integer a = 100` 编译为 `Integer.valueOf(100)`，走缓存返回同一对象；`new Integer(100)` 绕开缓存新建。面试三大陷阱：①缓存边界（-128 OK，-129 false）②反射篡改缓存（Java 9+ JPMS 已封禁，需 `--add-opens`）③反序列化不走 valueOf。其他包装类（Byte/Short/Long/Character）也缓存但范围不同，**Float/Double 无缓存**。实战建议：比较用 `equals()`，JVM 参数慎调上限，序列化用 `readResolve()` 兜底。"

> 📅 2026-09-01 · 咬文嚼字 · Integer 缓存 · ⭐⭐⭐⭐（中频面试 + 实战必会）

← [返回: 咬文嚼字 · integer-cache](../README.md)
