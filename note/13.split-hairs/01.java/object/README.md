<!--
question:
  id: 01.java-object
  topic: 01.java
  difficulty: 未标
  frequency: 中频
  scenario_type: 性能对比
  tags: [01.java, object]
-->

# Java 为什么将基础数据类型封装为对象

## 引子：既然有 int，为什么还要 Integer？

```java
// 基本类型就够了啊？
int a = 10;
int b = 20;
System.out.println(a + b);  // 30 ✓

// 但你试试这样：
List<int> list = new ArrayList<>();  // ❌ 编译报错！

// 只能用包装类
List<Integer> list = new ArrayList<>();  // ✓
list.add(10);  // 自动装箱：int → Integer
```

Java 设计者明明知道 `int` 比 `Integer` 快得多，为什么还要搞出 `Integer`、`Double` 这些包装类？

答案在于——**面向对象的世界里，一切皆对象**。

---

> 📚 **前置知识**：[基本数据类型](../../../01.java/concepts/data-types/README.md)

Java 将基础数据类型（如 `int`、`double` 等）封装为对象（如 `Integer`、`Double` 等）主要是为了解决基础类型在面向对象编程中的局限性，同时满足更复杂的编程需求。

---

### 1. **统一数据类型处理**
- **问题**：基础类型是值类型，不是对象，无法直接作为泛型参数、集合元素（如 `List<int>` 不合法）或反射机制中的操作对象。
- **解决**：封装为对象后，可以统一处理所有数据类型。例如：
  ```java
  List<Integer> numbers = Arrays.asList(1, 2, 3); // 基础类型无法直接作为泛型参数
  ```

---

### 2. **支持面向对象特性**
- **方法调用**：对象可以调用方法，而基础类型不能。例如：
  ```java
  Integer num = 42;
  String str = num.toString(); // 调用对象方法
  // int primitive = 42.toString(); // 编译错误
  ```
- **继承与多态**：封装类可以继承 `Object` 或实现接口（如 `Comparable<Integer>`），支持多态和动态绑定。

---

### 3. **提供额外功能**
- **工具方法**：封装类提供了大量实用方法（如类型转换、字符串解析、常量定义等）：
  ```java
  Integer.parseInt(“123”);      // 字符串转整数
  Integer.MAX_VALUE;            // 获取最大值常量
  Integer.compare(3, 5);        // 比较两个整数
  ```
- **自动装箱/拆箱**：Java 5+ 支持自动转换，简化代码：
  ```java
  Integer obj = 100; // 自动装箱（int → Integer）
  int primitive = obj; // 自动拆箱（Integer → int）
  ```

**自动装箱的陷阱：** 自动装箱虽然方便，但可能产生意外的性能问题。例如在循环中使用 `Integer` 而非 `int` 会导致大量对象创建：

```java
// 糟糕的性能：每次循环创建一个新Integer对象
Integer sum = 0;
for (int i = 0; i < 1000000; i++) {
    sum += i; // 自动装箱 + 拆箱，产生大量临时对象
}

// 更好的做法：使用基础类型
long sum = 0;
for (int i = 0; i < 1000000; i++) {
    sum += i;
}
```

---

### 4. **支持 `null` 值**
- **问题**：基础类型有默认值（如 `int` 默认为 `0`），无法表示”无值”状态。
- **解决**：对象可以赋值为 `null`，表示缺失或未初始化：
  ```java
  Integer nullableInt = null; // 合法
  // int primitive = null;    // 编译错误
  ```

**数据库映射场景：** 在ORM框架中，`null` 值非常重要。例如数据库字段允许NULL时，必须使用封装类而非基础类型：

```java
@Entity
public class User {
    @Column(nullable = true)
    private Integer age; // 可以为null，表示未知
    // 如果使用 int age，则无法区分0和null
}
```

---

### 5. **集合框架的需求**
- Java 集合（如 `List`、`Map`）只能存储对象，封装类是唯一选择：
  ```java
  Map<String, Integer> ageMap = new HashMap<>();
  ageMap.put(“Alice”, 25); // 键值对中的值必须是对象
  ```

---

### 6. **反射机制的支持**
- 反射需要操作对象类型（`Class` 对象），基础类型需通过封装类获取：
  ```java
  Class<?> intClass = int.class;    // 基础类型的 Class 对象
  Class<?> integerClass = Integer.class; // 封装类的 Class 对象
  ```

---

### 7. **泛型与类型擦除的兼容性**
- 泛型在运行时会被擦除为 `Object` 或基础类型的封装类（如 `List<Integer>` 擦除后为 `List<Object>` 的子类）。基础类型无法直接参与泛型类型擦除。

---

### 8. **常见陷阱**

#### 陷阱1：NullPointerException

```java
Integer num = getNullableInteger(); // 可能返回null
int value = num; // 如果num为null，抛出NullPointerException
```

**解决方案：** 在使用前始终检查null，或使用Optional包装。

#### 陷阱2：对象比较误用

```java
Integer a = 1000;
Integer b = 1000;
System.out.println(a == b); // false！超出缓存范围，是不同对象
System.out.println(a.equals(b)); // true，正确比较方式
```

#### 陷阱3：内存泄漏

```java
// WeakHashMap中使用Integer作为key可能导致意外行为
Map<Integer, String> cache = new WeakHashMap<>();
cache.put(new Integer(1), “value”); // 可能被GC回收
```

---

### 9. **历史与兼容性**
- Java 设计初期未引入泛型和集合框架，封装类为后续扩展提供了基础。即使现代 Java 引入了值类型提案（如 Project Valhalla），封装类仍会长期存在以保持兼容性。

---

### 10. 性能权衡
- **开销**：封装类有对象头（16字节）、内存分配和垃圾回收的开销，基础类型更高效（int仅4字节）。
- **优化**：JVM 通过自动装箱缓存（如 `Integer.valueOf(-128~127)`）和逃逸分析减少性能损耗。

**内存对比示例：**

```java
// 100万个int：约4MB
int[] primitives = new int[1_000_000];

// 100万个Integer：约24MB（对象头16字节 + int值4字节 + 引用8字节 + padding）
Integer[] objects = new Integer[1_000_000];
```

---

### 总结
封装基础类型是 Java 在**纯面向对象设计**与**性能**之间的妥协，它解决了基础类型在泛型、集合、反射等场景中的局限性，同时通过自动装箱/拆箱和 JVM 优化降低了使用成本。现代 Java（如记录类、模式匹配）进一步减少了对封装类的依赖，但它们仍是核心语言特性之一。

**面试要点：**
1. 为什么需要封装类（泛型、集合、null支持）
2. 自动装箱/拆箱的原理和性能陷阱
3. Integer缓存机制（-128到127）
4. 基础类型vs封装类的内存占用差异
5. ORM场景中为什么必须使用封装类## 相关章节

- 深度阅读：[`01.java/核心概念`](../../../01.java/concepts/README.md) — 包装类、泛型、类型系统
- 相关：[`13.split-hairs/integer-cache`](../integer-cache/README.md) — Integer 缓存（同类考点）
