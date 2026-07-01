<!--
module:
  parent: java
  slug: java/generics
  type: article
  category: 主模块子文章
  summary: 泛型
-->

# 泛型

## 引言：基础概念

泛型 是入门必学的基础概念。

本篇给出一句话定义 + 最小可运行示例 + 3 个常见误区，**5 分钟读完，10 分钟上手**。

---

Java 泛型（Generics）是 JDK 5 引入的特性，通过类型参数增强代码的可读性、类型安全性和复用性。

## 泛型的使用方式

### 泛型类

```java
public class Box<T> {
    private T value;

    public Box(T value) { this.value = value; }
    public T getValue() { return value; }
    public void setValue(T value) { this.value = value; }
}

// 使用
// <> 钻石运算符（Java 7+），JDK 5/6 需写为 new Box<String>("Hello")
Box<String> stringBox = new Box<>("Hello");
Box<Integer> intBox = new Box<>(42);
```

### 泛型接口

```java
import java.util.List;

public interface Repository<T, ID> {
    T findById(ID id);
    void save(T entity);
    List<T> findAll();
}

public class UserRepository implements Repository<User, Long> {
    @Override
    public User findById(Long id) { /* ... */ }
    // ...
}
```

### 泛型方法

```java
public class Util {
    // 泛型方法 - 类型参数声明在方法返回类型之前
    public static <T> void printArray(T[] array) {
        for (T item : array) {
            System.out.print(item + " ");
        }
        System.out.println();
    }

    // 带返回值的泛型方法
    public static <T extends Comparable<T>> T max(T a, T b) {
        return a.compareTo(b) >= 0 ? a : b;
    }
}

// 使用 - 编译器自动推断类型
Util.printArray(new String[]{"a", "b", "c"});
Util.printArray(new Integer[]{1, 2, 3});
```

## 类型擦除

Java 泛型是通过**类型擦除**（Type Erasure）实现的，即泛型信息只在编译期存在，编译后会被擦除。

### 擦除规则

1. **无界类型参数**（`<T>`）：擦除后替换为`Object`
2. **有界类型参数**（`<T extends Comparable>`）：擦除后替换为第一个边界类型

```java
// 编译前
public class Box<T> {
    private T value;
}

// 编译后（擦除后）- T 被替换为 Object
public class Box {
    private Object value;
}

// 编译前
public class NumberBox<T extends Number> {
    private T value;
}

// 编译后 - T 被替换为 Number
public class NumberBox {
    private Number value;
}
```

### 类型擦除带来的限制

```java
// 1. 不能使用基本类型作为类型参数
// Box<int> intBox = new Box<>();     // 编译错误！
Box<Integer> intBox = new Box<>();    // 必须用包装类

// 2. 不能创建泛型类型的实例
// T obj = new T();                   // 编译错误！

// 3. 不能创建泛型数组
// T[] array = new T[10];             // 编译错误！

// 4. 不能对泛型类型使用 instanceof
// if (obj instanceof Box<String>)    // 编译错误！
Object obj = new Box<>();
if (obj instanceof Box)               // 只能检查原生类型（Raw Type）
```

## 类型通配符

### 无界通配符 `<?>`

表示未知类型，通常用于只读取不写入的场景。

```java
// 可以接受任何类型的 Box
public void printBox(Box<?> box) {
    Object value = box.getValue();  // 只能作为 Object 使用
    System.out.println(value);
}
```

### 上界通配符 `<? extends T>`

表示类型是 T 或 T 的子类，用于**读取**场景（生产者）。

```java
// 接受 Number 或其子类（Integer、Double 等）的 Box
public double sum(Box<? extends Number> box1, Box<? extends Number> box2) {
    Number n1 = box1.getValue();  // 安全：一定是 Number 或其子类
    Number n2 = box2.getValue();
    return n1.doubleValue() + n2.doubleValue();
}
```

### 下界通配符 `<? super T>`

表示类型是 T 或 T 的父类，用于**写入**场景（消费者）。

```java
// 接受 Integer 或其父类（Number、Object）的 Box
public void addInteger(Box<? super Integer> box) {
    box.setValue(42);  // 安全：一定可以放入 Integer
}
```

## PECS 原则

**PECS**（Producer Extends, Consumer Super）是选择通配符的核心原则：

| 角色 | 通配符 | 说明 | 典型操作 |
|------|--------|------|---------|
| **生产者**（Producer） | `<? extends T>` | 从容器中**读取**数据 | `get()` |
| **消费者**（Consumer） | `<? super T>` | 向容器中**写入**数据 | `set()`/`add()` |
| 既是生产者又是消费者 | `<T>` | 不需要通配符 | `get()` + `set()` |

```java
// Collections.copy() 的经典签名
public static <T> void copy(List<? super T> dest, List<? extends T> src)
// src 是生产者（读取）→ extends
// dest 是消费者（写入）→ super
```

## 多重边界

类型参数可以有多个边界（一个类 + 多个接口）：

```java
import java.io.Serializable;

// T 必须同时是 Number 的子类且实现 Comparable 和 Serializable
public <T extends Number & Comparable<T> & Serializable> void method(T value) {
    // value 可以调用 Number 和 Comparable 的方法，同时可作为 Serializable 类型进行序列化
}
```

## 递归类型边界

类型参数引用自身作为边界，常见于构建器模式和链式调用：

```java
// 经典示例：Comparable 的自引用
public class Person implements Comparable<Person> {
    private int age;

    @Override
    public int compareTo(Person other) {
        return Integer.compare(this.age, other.age);
    }
}

// 构建器模式中的递归类型边界
public abstract class Builder<T extends Builder<T>> {
    protected String name;

    @SuppressWarnings("unchecked")
    public T setName(String name) {
        this.name = name;
        return (T) this;  // 返回子类类型
    }
}
```

> `@SuppressWarnings("unchecked")` 用于抑制泛型 unchecked 转换警告。因为 `(T) this` 的强制转换在运行时无法验证 `T` 的实际类型，编译器会产生 unchecked cast warning。

## 泛型与反射

虽然泛型在运行时被擦除（无法从对象实例获取泛型信息），但可以通过反射从类元数据（字段声明、方法签名、父类声明等）中获取泛型信息：

```java
import java.lang.reflect.Type;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Field;
import java.util.List;

// 定义示例类
class Parent<T> {}
class MyClass extends Parent<String> {
    private List<String> list;
}

// 获取类的泛型参数类型
Type superClass = MyClass.class.getGenericSuperclass();
if (superClass instanceof ParameterizedType) {
    Type[] typeArgs = ((ParameterizedType) superClass).getActualTypeArguments();
    // typeArgs[0] 就是泛型参数的实际类型
}

// 获取字段的泛型类型
Field field = MyClass.class.getDeclaredField("list");
Type fieldType = field.getGenericType();
if (fieldType instanceof ParameterizedType) {
    Type[] types = ((ParameterizedType) fieldType).getActualTypeArguments();
    // types[0] 是 List 的泛型参数类型（如 String 对应的 Type 对象）
}
```

## 泛型与可变参数

泛型与可变参数（varargs）结合使用时会产生**堆污染**（Heap Pollution）问题：

```java
// 编译器会产生 unchecked warning：Possible heap pollution from parameterized vararg type
public static <T> void addAll(List<T> list, List<T>... lists) {
    for (List<T> l : lists) {
        list.addAll(l);
    }
}

// JDK 8+ 推断 T=Object，编译通过；运行时 list.addAll(l) 仅复制 Object 引用，不会直接出错
// 但 varargs 数组的类型安全已被破坏，若数组引用泄漏则可能导致 ClassCastException
List<String> strList = new ArrayList<>();
List<Integer> intList = new ArrayList<>();
addAll(strList, intList);  // 编译通过（JDK 8+），运行时不会直接抛出异常

// 堆污染真正导致 ClassCastException 的场景：varargs 数组引用泄漏
static void heapPollution(List<String>... stringLists) {
    Object[] array = stringLists;        // 泛型数组赋值给 Object[]，数组引用泄漏
    List<Integer> tmpList = List.of(42);
    array[0] = tmpList;                  // 堆污染：List<Integer> 被存入本应只含 List<String> 的数组
    String s = stringLists[0].get(0);    // 运行时 ClassCastException!
}
```

Java 7 引入了 `@SafeVarargs` 注解，用于标注那些虽然使用了泛型可变参数但能保证类型安全的方法（通常是 `static`、`final` 或 `private` 方法）：

```java
@SafeVarargs
public static <T> List<T> of(T... elements) {
    List<T> list = new ArrayList<>();
    for (T element : elements) {
        list.add(element);
    }
    return list;
}
```

> **注意**：`@SafeVarargs` 只能用于不可被重写的方法（`static`、`final`、`private` 或构造方法），因为编译器需要确认方法的实现是类型安全的。
