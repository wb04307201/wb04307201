<!--
question:
  id: 01.java-final-finally-finalize
  topic: 01.java
  difficulty: 未标
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [01.java, final, finally]
-->

# final / finally / finalize 深度剖析

## 引子：三胞胎兄弟，你能分清吗？

Java 里有三个名字长得像三胞胎的关键字：

| 关键字 | 你可能以为 | 实际上是 |
|--------|-----------|---------|
| `final` | "最终的"？ | 修饰符：让类/方法/变量**不可改变** |
| `finally` | "最后"？ | 异常处理：`try-catch` 后**必定执行**的代码块 |
| `finalize` | "终结"？ | 已废弃的 GC 钩子方法，**千万别用** |

名字只差一两个字母，但职责天差地别。面试中经常把它们混在一起考，你能分清楚吗？

---

## 一、final

> 📚 **前置知识**：[Java 语法基础](../../../01.java/concepts/syntax/README.md)

`final` 是 Java 中最常用的修饰符之一，核心语义是"不可改变"，根据修饰对象不同有三种表现。

### 1.1 修饰类：不可继承

被 `final` 修饰的类不能有子类，编译器会直接阻止继承行为。

```java
public final class String { }  // String 不可被继承
public final class Integer { } // Integer 不可被继承
// public class MyString extends String { } // 编译错误
```

**设计意图**：保证类的不可变性和安全性。像 `String`、`Integer` 这样的核心类，如果允许继承，子类可能破坏其不可变契约，导致哈希表、安全校验等依赖不可变性的机制失效。

### 1.2 修饰方法：不可重写 + 编译期绑定

`final` 方法可以被子类继承和调用，但不能被重写（override）。

```java
class Parent {
    public final void greet() {
        System.out.println("Hello");
    }
}
class Child extends Parent {
    // @Override public void greet() { } // 编译错误
}
```

**关键点**：`final` 方法在编译期就确定了调用目标（静态绑定），不会走虚方法表（vtable）查找，因此无法实现多态。这也是为什么 `private` 方法隐式等价于 `final`——私有方法本身就不能被重写。

**历史背景**：早期 JVM 中，`final` 方法可能被内联优化以提升性能。现代 JIT 编译器足够智能，能自行判断是否内联，因此出于性能考虑使用 `final` 的意义已不大。

### 1.3 修饰变量：不可重新赋值

这是 `final` 最核心的用法，但需要区分基本类型和引用类型。

```java
// 基本类型：值不可变
final int x = 10;
// x = 20; // 编译错误

// 引用类型：引用不可变，但对象内容可变
final List<String> list = new ArrayList<>();
list.add("hello");   // 合法：修改对象内部状态
// list = new LinkedList<>(); // 编译错误：不能重新赋值引用
```

**常见误区**：很多人认为 `final` 能让对象"不可变"，这是错误的。`final` 只保证引用本身不指向其他对象，不保证对象内部状态不变。真正的不可变对象需要类自身设计保证（如 `String` 内部 `char[]` 也是 `final` 且不提供修改方法）。

### 1.4 空白 final（Blank Final）

`final` 变量可以不立即初始化，但必须在使用前完成赋值，且只能赋值一次。

```java
class Example {
    private final int value;          // 空白 final

    {
        value = 42;                   // 实例代码块中初始化
    }

    private static final int STATIC_VALUE;

    static {
        STATIC_VALUE = 100;           // 静态代码块中初始化
    }
}
```

**初始化时机三选一**：
- 声明时直接赋值
- 实例代码块或构造器中赋值（实例变量）
- 静态代码块中赋值（静态变量）

构造器中赋值时要特别注意：如果有多个构造器，每个路径都必须给 `final` 变量赋值。

---

## 二、finally

`finally` 是 `try-catch-finally` 异常处理结构的一部分，核心保证是：**无论是否发生异常，finally 块都会执行**（除非 JVM 退出或线程被杀死）。

### 2.1 执行顺序

```java
public static int test() {
    try {
        System.out.println("try");
        return 1;
    } catch (Exception e) {
        System.out.println("catch");
        return 2;
    } finally {
        System.out.println("finally");  // 在 return 之前执行
    }
}
// 输出：try → finally → 返回 1
```

**关键规则**：`finally` 在 `return` 语句之后、实际返回值传递给调用者之前执行。如果 `finally` 中没有 `return`，则原来的返回值保持不变。

### 2.2 finally 中的 return 覆盖问题

```java
public static int dangerousReturn() {
    try {
        return 1;
    } finally {
        return 2;  // ⚠️ 覆盖了 try 中的返回值
    }
}
// 返回值是 2，不是 1
```

**陷阱分析**：当 `finally` 中包含 `return` 时，它会无条件覆盖 `try` 或 `catch` 中的返回值。这会导致：
1. 原始返回值丢失，调用方拿到意外结果
2. 如果 `try` 中抛出了异常但 `finally` 中有 `return`，异常会被吞掉

```java
public static int swallowException() {
    try {
        throw new RuntimeException("oops");
    } finally {
        return 1;  // ⚠️ 异常被吞掉，正常返回 1
    }
}
```

**最佳实践**：**永远不要在 `finally` 中使用 `return`**。IDE（如 IntelliJ IDEA）会将此标记为警告。

---

## 三、finalize

`Object.finalize()` 方法设计初衷是让对象在被垃圾回收前执行清理工作，类似析构函数。但它在 Java 9 中被标记为 `@Deprecated`，Java 18+ 中已移除。

### 3.1 为什么废弃？

| 问题 | 说明 |
|------|------|
| **不保证执行时机** | GC 何时触发不确定，`finalize` 可能很久后才执行，甚至 JVM 退出时都不执行 |
| **性能极差** | 带 `finalize` 的对象需要经过两次 GC 才能被回收（第一次执行 finalize，第二次才真正回收），严重拖慢 GC |
| **可能导致对象复活** | 在 `finalize` 中将 `this` 引用赋值给其他变量，可以让对象"起死回生"，造成内存泄漏 |
| **异常被静默吞掉** | `finalize` 中抛出的未捕获异常会被忽略，难以调试 |
| **没有执行保证** | 即使调用了 `System.gc()`，也不保证 `finalize` 一定会被执行 |

### 3.2 替代方案

#### 方案一：try-with-resources（推荐用于资源关闭）

```java
// 传统方式（容易遗漏）
BufferedReader br = null;
try {
    br = new BufferedReader(new FileReader("test.txt"));
    // 读取文件
} catch (IOException e) {
    e.printStackTrace();
} finally {
    if (br != null) {
        try { br.close(); } catch (IOException e) { e.printStackTrace(); }
    }
}

// 现代方式（Java 7+）
try (BufferedReader br = new BufferedReader(new FileReader("test.txt"))) {
    // 读取文件，自动关闭
}
```

#### 方案二：Cleaner（Java 9+，用于原生资源清理）

```java
import java.lang.ref.Cleaner;

public class NativeResource implements AutoCloseable {
    private static final Cleaner CLEANER = Cleaner.create();
    private final Cleaner.Cleanable cleanable;
    private boolean closed = false;

    public NativeResource() {
        this.cleanable = CLEANER.register(this, () -> {
            // 清理原生资源（如 JNI 分配的内存）
            System.out.println("Cleaning up native resource");
        });
    }

    @Override
    public void close() {
        if (!closed) {
            cleanable.clean();  // 显式清理
            closed = true;
        }
    }
}
```

**Cleaner 的核心优势**：
- 清理逻辑与对象生命周期解耦
- 通过 `AutoCloseable` 提供确定性清理
- `Cleaner` 作为最后防线，防止忘记调用 `close()` 时的资源泄漏

---

## 四、代码示例 + 陷阱

### 陷阱 1：finally 中 return 覆盖

```java
public static int trap1() {
    try {
        return 100;
    } finally {
        return 200;  // 实际返回 200
    }
}
```

### 陷阱 2：final 变量未在构造器中初始化

```java
class BadExample {
    private final int value;  // 编译错误：blank final 未初始化

    public BadExample() {
        // 忘记给 value 赋值
    }
}
```

### 陷阱 3：误以为 final 引用指向的对象不可变

```java
final StringBuilder sb = new StringBuilder("hello");
sb.append(" world");  // 合法！对象内容可以修改
System.out.println(sb);  // "hello world"
```

### 陷阱 4：finally 中抛出异常覆盖原有异常

```java
public static void trap4() throws Exception {
    try {
        throw new IOException("original");
    } finally {
        throw new SQLException("covers original");  // 原始异常丢失
    }
}
```

---

## 五、最佳实践

### 5.1 用 try-with-resources 替代 finally 关闭资源

```java
// ✅ 推荐
try (Connection conn = dataSource.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql)) {
    // 执行业务逻辑
}
// 自动按相反顺序关闭资源

// ❌ 避免
Connection conn = null;
try {
    conn = dataSource.getConnection();
} finally {
    if (conn != null) {
        try { conn.close(); } catch (SQLException e) { /* log */ }
    }
}
```

### 5.2 用 Cleaner 处理原生资源

对于涉及 JNI、直接内存等非堆资源的场景，使用 `Cleaner` 作为安全网：

```java
public class DirectMemoryBuffer implements AutoCloseable {
    private static final Cleaner CLEANER = Cleaner.create();
    private final Cleaner.Cleanable cleanable;
    private long address;  // 原生内存地址

    public DirectMemoryBuffer(long size) {
        this.address = allocateNativeMemory(size);
        this.cleanable = CLEANER.register(this, () -> {
            freeNativeMemory(address);
        });
    }

    @Override
    public void close() {
        cleanable.clean();
        address = 0;  // 防止重复释放
    }

    private static native long allocateNativeMemory(long size);
    private static native void freeNativeMemory(long address);
}
```

### 5.3 final 变量的使用建议

- 所有不会被重新赋值的字段都应加上 `final`，提升代码可读性
- 不可变类（如 DTO、Value Object）的所有字段都应是 `private final`
- 方法参数加 `final` 可防止意外修改，但团队风格一致更重要

---

## 六、面试话术（30 秒版）

> "`final`、`finally`、`finalize` 三个关键字名字相似但用途完全不同。
>
> `final` 是修饰符，修饰类表示不可继承（如 String），修饰方法表示不可重写且编译期绑定，修饰变量表示不可重新赋值——注意引用类型只是引用不可变，对象内容仍可修改。
>
> `finally` 是异常处理的一部分，保证无论是否异常都会执行，常用于资源清理。但要特别注意，**永远不要在 finally 中写 return**，否则会覆盖 try 中的返回值，甚至吞掉异常。
>
> `finalize` 是 Object 类的方法，原本是垃圾回收前的清理钩子，但因为执行时机不确定、性能差、可能导致对象复活等问题，在 Java 9 被废弃。现在关闭资源应该用 **try-with-resources**，原生资源清理由 **Cleaner** 负责。
>
> 总结一句话：`final` 管不可变，`finally` 管清理，`finalize` 已经淘汰。"

---

## 七、交叉引用

- 主模块：[`01.java`](../../../01.java/) — Java 知识体系
- [JVM 调优](../../../01.java/jvm/tuning.md) — GC 算法与内存管理

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · final-finally-finalize](README.md)
