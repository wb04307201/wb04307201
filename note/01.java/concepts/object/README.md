<!--
module:
  parent: java
  slug: java/concepts/object
  type: article
  category: 主模块子文章
  summary: Java Object 类：equals/hashCode/toString/wait/notify 等 11 个方法。
-->

# Object 类

## 引言：基础概念

Object 类 是入门必学的基础概念。

本篇给出一句话定义 + 最小可运行示例 + 3 个常见误区，**5 分钟读完，10 分钟上手**。

---

Java 中的 `Object` 类是所有 Java 类的根类（超类），即所有未显式声明父类的类都默认隐式继承自 `Object`。它定义了所有对象共有的基本行为。

## 核心方法与作用

### 1. `equals(Object obj)`

```java
public boolean equals(Object obj)
```

- **默认行为**：比较两个对象的内存地址是否相同（即是否为同一对象），等价于 `==`。
- **重写场景**：当需要基于对象内容而非内存地址判断相等性时，需重写此方法。

假设 `Person` 类定义如下：

```java
public class Person {
    private String name;
    private int age;
    // ... 构造方法、getter/setter 省略
}
```

> **重写实现与契约**：完整的 `Person.equals()` 和 `Person.hashCode()` 重写实现、Java 16+ 模式匹配写法，以及 `equals()` 必须满足的五条契约（自反性、对称性、传递性、一致性、非空性），参见 [oop/README.md](../../../README.md#hashcode-与哈希表)。

### 2. `hashCode()`

```java
public native int hashCode()
```

- **默认行为**：返回对象的哈希码（由 JVM 决定，通常与内存地址相关）。
- **重写规则**：若重写 `equals()`，**必须同步重写 `hashCode()`**，确保相等的对象哈希值相同。违反此规则会导致对象在 `HashMap`、`HashSet` 等基于哈希的集合中行为异常。

> 完整的 `hashCode()` 重写实现与最佳实践参见 [oop/README.md](../../../README.md#hashcode-与哈希表)。

### 3. `toString()`

```java
public String toString()
```

- **默认行为**：返回 `类名@十六进制哈希码`（如 `Person@1a2b3c`）。
- **重写场景**：为对象提供有意义的字符串表示，方便调试和日志输出。

```java
@Override
public String toString() {
    return "Person{name='" + name + "', age=" + age + "}";
}
```

### 4. `clone()`

```java
protected native Object clone() throws CloneNotSupportedException
```

- 实现对象的**浅拷贝**。需先实现 `Cloneable` 接口（标记接口），并重写方法为 `public`。
- **深拷贝**需手动处理对象内部的可变引用类型字段。

深拷贝的前提：引用类型字段所在的类也必须实现 `Cloneable` 接口并提供 `public clone()` 方法。例如 `Address` 类：

```java
class Address implements Cloneable {
    String city;

    @Override
    public Address clone() throws CloneNotSupportedException {
        return (Address) super.clone();
    }
}
```

```java
// 前提：Person 类需实现 Cloneable 接口 —— public class Person implements Cloneable
@Override
public Person clone() throws CloneNotSupportedException {
    Person cloned = (Person) super.clone();
    if (this.address != null) {
        cloned.address = this.address.clone(); // 深拷贝引用类型字段
    }
    return cloned;
}
```

### 5. `getClass()`

```java
public final native Class<?> getClass()
```

- 返回对象的运行时类（`Class` 实例），被 `final` 修饰，不允许子类重写。
- 可用于反射操作（如获取类名、方法、字段等）。

### 6. 线程通信方法

| 方法 | 说明 |
|------|------|
| `wait()` | 使当前线程等待，直到被唤醒或超时。**释放锁** |
| `wait(long timeout)` | 等待指定毫秒数。**释放锁** |
| `wait(long timeout, int nanos)` | 等待指定时间（毫秒+纳秒）。**释放锁** |
| `notify()` | 唤醒在此对象监视器上等待的**一个**线程 |
| `notifyAll()` | 唤醒在此对象监视器上等待的**所有**线程 |

> **注意**：所有 `wait()/notify()/notifyAll()` 方法都必须在 `synchronized` 同步块/方法中调用，否则会抛出 `IllegalMonitorStateException`。

### 7. `finalize()`

```java
protected void finalize() throws Throwable
```

- **已过时（Java 9+ 标记为 `@Deprecated`）**：垃圾回收前可能调用的清理方法。Java 18 起标记为 `@Deprecated(forRemoval=true)`（JEP 421），JEP 501 提案计划在未来版本默认禁用终结器（Finalization）并最终彻底移除。
- **问题**：执行时机不确定、影响 GC 性能、可能导致对象重生（object resurrection）。
- **替代方案**：使用 `try-with-resources`、`java.lang.ref.Cleaner`（Java 9+）或显式的 `close()` 方法。

## `Objects` 工具类（`java.util.Objects`）

Java 7 引入的 `Objects` 工具类提供了一系列静态方法，用于对对象进行空安全的操作，是对 `Object` 类方法的有力补充。

### `Objects.equals(Object a, Object b)`

空安全的 `equals` 比较，避免空指针异常：

```java
// 不安全写法 - 如果 obj 为 null 会抛 NPE
obj.equals(other);

// 安全写法
Objects.equals(obj, other);  // 两者都为 null 返回 true，一个为 null 返回 false
```

**源码逻辑**：
```java
public static boolean equals(Object a, Object b) {
    return (a == b) || (a != null && a.equals(b));
}
```

### `Objects.requireNonNull(T obj)`

对参数进行非空校验，为 `null` 时抛出 `NullPointerException`：

```java
public class User {
    private String name;

    public User(String name) {
        // 如果 name 为 null，立即抛出 NPE，附带自定义信息
        this.name = Objects.requireNonNull(name, "name 不能为 null");
    }
}
```

**变体**：
```java
Objects.requireNonNull(obj);                          // 默认 NPE
Objects.requireNonNull(obj, "message");               // 自定义错误信息
Objects.requireNonNull(obj, () -> "lazy message");    // 延迟构造错误信息（Java 8+）
```

### `Objects.hashCode(Object o)` 和 `Objects.hash(Object... values)`

```java
// 单个对象的哈希值（null 安全，null 返回 0）
int hash = Objects.hashCode(obj);

// 多个字段组合哈希值（常用于重写 hashCode()）
// 注意：参与 hash 的字段应与 equals() 中使用的字段保持一致
@Override
public int hashCode() {
    return Objects.hash(name, age);
}
```

### `Objects.toString(Object o)` 和 `Objects.toString(Object o, String nullDefault)`

```java
Objects.toString(obj);              // null 返回 "null"
Objects.toString(obj, "未知");       // null 返回 "未知"
```

### `Objects.compare(T a, T b, Comparator<? super T> c)`

空安全的比较器：

```java
// 如果两个对象都为 null（a == b），返回 0；否则委托给传入的 Comparator 进行比较
// 注意：Comparator 需自行处理 null，否则会抛出 NullPointerException
int result = Objects.compare(obj1, obj2, comparator);
```

### `Objects.isNull(Object obj)` 和 `Objects.nonNull(Object obj)`

```java
Objects.isNull(obj);     // 等价于 obj == null
Objects.nonNull(obj);    // 等价于 obj != null
```

> 这两个方法主要用于 Stream API 中的方法引用：`list.stream().filter(Objects::nonNull)`

## 关键特性

- **多态基石**：所有对象均可向上转型为 `Object`，支持泛型、集合（如 `List<Object>`）等通用操作。
- **默认行为一致性**：未重写的 Object 方法保持默认行为（如 `equals` 的地址比较），为所有对象提供一致的基础语义。

## 最佳实践

- **重写原则**：重写 `equals()` 时必须同时重写 `hashCode()`；使用 IDE 自动生成或 `Objects.hash()` 来避免出错。
- **避免滥用 `clone()`**：优先使用拷贝构造函数或序列化方案实现对象复制。
- **线程安全**：`wait()/notify()` 需谨慎使用，优先选择 `java.util.concurrent` 中的高级同步工具（如 `CountDownLatch`、`Semaphore`、`BlockingQueue`）。
- **空值处理**：优先使用 `Objects` 工具类进行空安全操作，而不是手动判空。
- **Java 8+ 替代方案**：考虑使用 `Optional` 来显式表达可能为空的值，避免 `null` 的隐式传递。
- **多态核心**：[polymorphism](../polymorphism/README.md) — 多态深度专题：方法签名决定多态分派（Object 类 11 个方法是多态基础案例）

---

← [返回 Java 核心概念](../README.md)
