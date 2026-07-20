<!--
question:
  id: 01.java-generics-erasure
  topic: 01.java
  difficulty: ⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [01.java, generics, erasure]
-->

# Java 泛型擦除深度剖析

## 引子：一个让你怀疑人生的编译错误

```java
List<String> stringList = new ArrayList<>();
List<Integer> intList = new ArrayList<>();

System.out.println(stringList.getClass() == intList.getClass()); 
// true ？？？ 它们的类型不一样啊！
```

更诡异的是：

```java
// 编译报错！
public class Test {
    public void process(List<String> list) {}
    public void process(List<Integer> list) {}  // 编译错误：方法签名冲突！
}
```

`List<String>` 和 `List<Integer>` 明明是不同的泛型类型，为什么 `getClass()` 相同？为什么不能重载？

答案就藏在 Java 泛型的本质——**类型擦除**。

---

## 一、核心原理

> 📚 **前置知识**：[泛型](../../../01.java/concepts/generics/README.md)

泛型的本质是**编译期概念**。Java 在 JDK 5 引入泛型时，为了保证与已有字节码的向后兼容，选择了**类型擦除（Type Erasure）**方案：编译器在编译阶段完成类型检查后，将所有类型参数 `T`、`E`、`K`、`V` 等替换为其上界（若未指定上界则替换为 `Object`），并在必要时插入强制类型转换指令。这意味着 JVM 在运行时根本不知道泛型的存在。

```java
// 源码
public class Box<T> {
    private T value;
    public void set(T value) { this.value = value; }
    public T get() { return value; }
}

// 编译后等价于（伪代码）
public class Box {
    private Object value;
    public void set(Object value) { this.value = value; }
    public Object get() { return (Object) value; }
}
```

使用 `javap -v Box.class` 查看字节码，可以看到签名中保留了泛型信息（`Signature: Ljava/lang/Object;`），但实际字段和方法描述符中的类型全部被擦除为 `Ljava/lang/Object;`。泛型信息仅存储在 `Signature` 属性中，供反射和编译器使用，JVM 执行时完全忽略。

---

## 二、擦除的后果

由于运行时不存在泛型类型信息，以下操作在编译期均被禁止：

### 2.1 不能 `new T()`

```java
public <T> T create() {
    // 编译错误：Cannot instantiate the type T
    // return new T();
    // 正确做法：传入 Class<T>
    return null; // 占位
}
```

### 2.2 不能 `instanceof List<String>`

```java
public void check(Object obj) {
    // 编译错误：Cannot perform instanceof check against parameterized type
    // if (obj instanceof List<String>) { }
    // 只能检查原始类型
    if (obj instanceof List) { }
}
```

### 2.3 不能创建泛型数组

```java
public <T> T[] toArray(int size) {
    // 编译错误：Cannot create a generic array of T
    // return new T[size];
    // 正确做法：通过 Array.newInstance 或传入 Class<T>
    @SuppressWarnings("unchecked")
    T[] arr = (T[]) new Object[size];
    return arr;
}
```

### 2.4 静态成员不能使用类型参数

```java
public class Holder<T> {
    // 编译错误：Cannot make a static reference to the non-static type T
    // private static T staticValue;
    // 原因：静态变量属于类而非实例，而 T 是实例级别的类型参数
}
```

---

## 三、桥方法（Bridge Method）

当子类覆盖父类的泛型方法时，如果子类将类型参数具体化，会导致方法签名不一致，破坏多态。编译器通过生成**桥方法**来解决这个问题。

```java
// 父类
class Parent<T> {
    public T getData() { return null; }
}

// 子类
class Child extends Parent<String> {
    @Override
    public String getData() { return "hello"; }
}
```

编译后，`Child` 类中实际存在两个 `getData` 方法：

```
// 桥方法（由编译器生成）
public Object getData() {
    return this.getData(); // 调用下方的具体方法
}

// 用户编写的方法
public String getData() {
    return "hello";
}
```

桥方法的签名与父类擦除后的签名一致（返回 `Object`），内部委托给子类的具体实现。通过反射可以观察到：

```java
Method[] methods = Child.class.getDeclaredMethods();
for (Method m : methods) {
    System.out.println(m.getName() + ": " + m.getReturnType());
    System.out.println("  isBridge: " + m.isBridge());
}
// 输出：
// getData: class java.lang.String  isBridge: false
// getData: class java.lang.Object  isBridge: true
```

桥方法是编译器维持协变返回类型和多态性的关键机制，对开发者透明。

---

## 四、通配符 PECS

### 4.1 `? extends T`（Producer Extends）

`? extends T` 表示上界通配符，适用于**只读场景**（生产者）。你可以从中读取元素（保证是 T 或其子类），但不能写入（除了 `null`），因为编译器不知道具体类型。

```java
List<? extends Number> list = new ArrayList<Integer>();
Number n = list.get(0);  // OK：读取到的一定是 Number 子类
// list.add(1);           // 编译错误：无法确定具体类型
list.add(null);           // OK：null 是所有引用类型的子类型
```

### 4.2 `? super T`（Consumer Super）

`? super T` 表示下界通配符，适用于**只写场景**（消费者）。你可以向其中写入 T 或其子类元素，但读取时只能得到 `Object`，因为编译器不知道上界。

```java
List<? super Integer> list = new ArrayList<Number>();
list.add(1);              // OK：Integer 是 Number 的子类
// list.add("hello");     // 编译错误：String 不是 Integer 的超类
Object obj = list.get(0); // OK：只能保证是 Object
// Integer n = list.get(0); // 编译错误：无法保证是 Integer
```

### 4.3 PECS 原则

**Producer Extends, Consumer Super**：如果一个参数化类型代表生产者（只向外提供数据），使用 `extends`；如果代表消费者（只接收外部数据），使用 `super`。

---

## 五、常见陷阱

### 5.1 `List<Object>` 不能赋值给 `List<String>`

```java
List<String> strings = new ArrayList<>();
// List<Object> objects = strings; // 编译错误
// 如果允许，就可以 objects.add(1)，导致 strings 中混入非 String 类型
```

泛型是**不变的（Invariant）**，即使 `String` 是 `Object` 的子类，`List<String>` 也不是 `List<Object>` 的子类。这是为了保障类型安全。

### 5.2 反射获取泛型类型

虽然运行时泛型被擦除，但通过 `getGenericSuperclass()` 和 `ParameterizedType` 可以在某些场景下恢复泛型信息：

```java
abstract class GenericDao<T> {
    private Class<T> entityClass;

    @SuppressWarnings("unchecked")
    public GenericDao() {
        Type type = getClass().getGenericSuperclass();
        if (type instanceof ParameterizedType) {
            Type actualType = ((ParameterizedType) type).getActualTypeArguments()[0];
            this.entityClass = (Class<T>) actualType;
        }
    }

    public Class<T> getEntityClass() {
        return entityClass;
    }
}

class UserDao extends GenericDao<User> {}
// new UserDao().getEntityClass() → User.class
```

这种技巧广泛用于 DAO 框架和序列化库中，但前提是泛型信息在类定义时被具体化（即子类继承时指定了具体类型）。

---

## 六、面试话术（30 秒版）

"Java 泛型采用类型擦除实现，编译后所有类型参数都被替换为上界或 Object，JVM 运行时不感知泛型。这导致不能 new T()、不能用 instanceof 检查泛型类型、不能创建泛型数组。当子类覆盖父类泛型方法时，编译器会生成桥方法维持多态性。PECS 原则指导我们：生产者用 extends 保证只读，消费者用 super 保证只写。虽然泛型被擦除，但通过反射的 ParameterizedType 可以在子类继承具体化类型时恢复泛型信息。"

---

## 七、交叉引用

- 主模块：[`01.java`](../../../01.java/) — Java 知识体系

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · generics-erasure](../README.md)
