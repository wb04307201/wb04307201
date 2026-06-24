# String / StringBuilder / StringBuffer 深度对比

## 引子：一个经典的性能陷阱

```java
// 看起来没问题的代码
String result = "";
for (int i = 0; i < 100_000; i++) {
    result += "a";  // 每次拼接都创建新 String 对象！
}
// 耗时：~30 秒，创建了 100_000 个临时 String 对象

// 换一种写法
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 100_000; i++) {
    sb.append("a");  // 只操作一个可变数组
}
// 耗时：~5 毫秒
```

同样的循环，性能差了 **6000 倍**！原因就藏在 String 的**不可变性**设计里。

String、StringBuilder、StringBuffer——三个名字相近的类，底层设计截然不同。

---

## 一、核心原理

> 📚 **前置知识**：[String](../../../01.java/concepts/string/README.md)

Java 中的字符串处理涉及三个核心类，其设计哲学截然不同：

| 特性 | String | StringBuilder | StringBuffer |
|------|--------|---------------|--------------|
| 可变性 | **不可变** | 可变 | 可变 |
| 线程安全 | 天然安全 | 不安全 | **安全** |
| 底层存储 | `final char[]` (JDK8) / `final byte[]` (JDK9+) | `char[]` / `byte[]` | `char[]` / `byte[]` |
| 性能 | 修改时创建新对象 | 最快 | 较慢（同步开销） |

**关键设计差异：**

- **String**：一旦创建，内容不可更改。任何"修改"操作（如 `concat`、`replace`）都会返回新的 String 对象。
- **StringBuilder**：继承自 `AbstractStringBuilder`，内部维护一个可变的字符数组，所有方法无同步修饰。
- **StringBuffer**：同样继承自 `AbstractStringBuilder`，但在关键方法（`append`、`insert`、`delete` 等）上添加了 `synchronized` 关键字。

---

## 二、String 不可变性

### 2.1 为什么设计为不可变？

1. **安全性**：String 常用于类加载器、网络连接、文件路径等敏感场景。若可变，可能被恶意篡改。
2. **线程安全**：不可变对象天然线程安全，无需额外同步。
3. **哈希缓存**：String 的 `hashCode()` 被频繁使用（如 HashMap 的 key）。不可变性使得 hash 值可以缓存，提升性能。
4. **字符串常量池**：不可变是实现常量池共享的前提。

### 2.2 底层存储演进

```java
// JDK 8 及之前
public final class String {
    private final char value[];  // final 修饰，不可变
}

// JDK 9+ 引入 Compact Strings
public final class String {
    private final byte[] value;  // 改用 byte[] 节省内存
    private final byte coder;    // 标识编码：LATIN1(0) 或 UTF16(1)
}
```

JDK 9+ 的 Compact Strings 优化：对于纯 ASCII 字符串，每个字符仅占 1 字节（而非原来的 2 字节），内存占用减少约 50%。

### 2.3 字符串常量池与 intern()

**字符串常量池**位于堆内存中，用于存储字面量创建的 String 对象。

```java
String s1 = "hello";           // 从常量池获取
String s2 = new String("hello"); // 在堆上新建对象
System.out.println(s1 == s2);   // false（引用不同）
System.out.println(s1.equals(s2)); // true（内容相同）
```

**intern() 方法**：手动将 String 对象加入常量池。

```java
String s3 = new String("hello").intern();
System.out.println(s1 == s3); // true（s3 指向常量池中的 "hello"）
```

**intern() 原理：**
- JDK 6：常量池位于永久代（PermGen），`intern()` 会在永久代创建对象。
- JDK 7+：常量池移至堆内存，`intern()` 仅在堆中记录引用，避免 PermGen 溢出风险。

**适用场景**：大量重复字符串去重（如解析 XML/JSON 时的字段名）。

---

## 三、StringBuilder vs StringBuffer

### 3.1 synchronized 的性能开销

StringBuffer 的所有公开方法都带有 `synchronized` 修饰：

```java
// StringBuffer.java
@Override
public synchronized StringBuffer append(String str) {
    super.append(str);
    return this;
}

// StringBuilder.java
@Override
public StringBuilder append(String str) {
    super.append(str);
    return this;
}
```

**性能对比**：在单线程环境下，StringBuilder 比 StringBuffer 快 **10x~15x**。原因是 `synchronized` 会触发锁竞争、内存屏障等开销。

### 3.2 扩容机制

两者共用 `AbstractStringBuilder` 的扩容逻辑：

```java
private void ensureCapacityInternal(int minimumCapacity) {
    if (minimumCapacity - value.length > 0) {
        int newCapacity = ArraysSupport.newLength(value.length,
                minimumCapacity - value.length, /* minimum growth */
                2,                                /* preferred growth */
                Integer.MAX_VALUE - 8);          /* maximum limit */
        value = Arrays.copyOf(value, newCapacity);
    }
}
```

**扩容公式**：`newCapacity = oldCapacity * 2 + 2`

**最佳实践**：若能预估字符串长度，构造时指定初始容量，避免多次扩容和数组拷贝。

```java
// 避免
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i); // 触发多次扩容
}

// 推荐
StringBuilder sb = new StringBuilder(4000); // 预估容量
for (int i = 0; i < 1000; i++) {
    sb.append(i); // 几乎无扩容
}
```

---

## 四、+ 号编译期优化

### 4.1 常量折叠（Constant Folding）

编译器会对编译期可确定的字符串拼接进行优化：

```java
// 源码
String s = "a" + "b" + "c";

// 编译后等价于
String s = "abc"; // 直接合并为一个常量
```

这种优化称为**常量折叠**，发生在 javac 编译阶段，生成的字节码中只有一个 `"abc"` 常量。

### 4.2 运行时拼接

对于运行期才能确定的拼接，编译器会转换为 `StringBuilder`：

```java
// 源码
String s = "hello" + name + "world";

// 编译后等价于
String s = new StringBuilder().append("hello").append(name).append("world").toString();
```

### 4.3 循环中的陷阱

```java
// 糟糕写法：每次循环创建新的 StringBuilder
String result = "";
for (int i = 0; i < 10000; i++) {
    result += i; // 等价于 result = new StringBuilder(result).append(i).toString();
}

// 推荐写法：复用同一个 StringBuilder
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);
}
String result = sb.toString();
```

**性能差异**：在 10000 次循环中，`+=` 写法可能比 StringBuilder 慢 **100x 以上**，因为每次迭代都涉及对象创建、数组拷贝和垃圾回收。

---

## 五、常见陷阱

### 5.1 == vs equals

```java
String s1 = new String("hello");
String s2 = new String("hello");
System.out.println(s1 == s2);      // false（比较引用）
System.out.println(s1.equals(s2)); // true（比较内容）
```

**原则**：String 比较永远使用 `equals()`，`==` 仅用于判断是否为同一对象引用。

### 5.2 substring 的内存泄漏问题（JDK 6 vs 7）

**JDK 6 的实现**：
```java
// JDK 6 String.substring()
String(int offset, int count, char value[]) {
    this.value = value;      // 共享原始 char[]
    this.offset = offset;
    this.count = count;
}
```

JDK 6 的 `substring()` 共享原 String 的 `char[]`，仅记录偏移量和长度。这导致一个小问题：**截取一小段字符串会阻止整个大数组被 GC**。

```java
// JDK 6 内存泄漏示例
String huge = new String(new char[10_000_000]); // 10MB
String small = huge.substring(0, 10);            // 仅需要 10 个字符
// huge 被 GC 后，small 仍然持有整个 10MB 的 char[]！
```

**JDK 7u6+ 的修复**：
```java
// JDK 7+ String.substring()
public String substring(int beginIndex, int endIndex) {
    int subLen = endIndex - beginIndex;
    return new String(value, beginIndex, subLen); // 复制新数组
}
```

JDK 7+ 改为拷贝子数组，虽然增加了内存分配，但避免了内存泄漏。

### 5.3 StringBuilder 的 capacity 误区

```java
StringBuilder sb = new StringBuilder(10);
sb.append("hello world!"); // 长度 12，超过初始容量 10
System.out.println(sb.capacity()); // 输出 22（10 * 2 + 2）
```

**注意**：`capacity()` 不等于 `length()`。`capacity` 是当前数组总容量，`length` 是已使用的字符数。

---

## 六、面试话术（30 秒版）

> "String 是不可变的，底层在 JDK 8 是 `final char[]`，JDK 9+ 优化为 `final byte[]` + coder 标识。不可变带来的好处是线程安全、hash 可缓存、支持常量池共享。
>
> StringBuilder 和 StringBuffer 都是可变的，区别在于 StringBuffer 的方法加了 `synchronized`，线程安全但有性能开销，单线程下 StringBuilder 快 10 倍以上。
>
> 编译期会对 `'a' + 'b'` 做常量折叠优化成 `'ab'`，但运行期的拼接（如循环中用 `+=`）会被转成每次新建 StringBuilder，性能极差，应显式使用 StringBuilder 并预估初始容量。
>
> 另外，JDK 6 的 `substring()` 共享 char[] 会导致内存泄漏，JDK 7+ 已修复为拷贝子数组。"

---

## 七、交叉引用

- 主模块：[`01.java`](../../../01.java/) — Java 知识体系
- [String](../../../01.java/concepts/string/README.md) — 字符串常量池与 intern 机制
- [JVM 内存](../../../01.java/jvm/README.md) — JVM 内存模型与 GC
