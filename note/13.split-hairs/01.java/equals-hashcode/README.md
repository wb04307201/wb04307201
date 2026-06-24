# == / equals / hashCode 深度剖析

## 引子：一个让人抓狂的 Bug

```java
String a = new String("hello");
String b = new String("hello");

System.out.println(a == b);      // false ？？？
System.out.println(a.equals(b)); // true
```

内容明明一样，为什么 `==` 返回 false？

再看一个更坑的：

```java
class User {
    String name;
    User(String name) { this.name = name; }
}

User u1 = new User("张三");
User u2 = new User("张三");

Set<User> set = new HashSet<>();
set.add(u1);
set.add(u2);

System.out.println(set.size()); // 2 ？？？明明是同一个人！
```

为什么 HashSet 认为这是两个人？因为没重写 `hashCode`！

---

## 一、核心原理

> 📚 **前置知识**：[Object 类](../../../01.java/concepts/object/README.md) | [String](../../../01.java/concepts/string/README.md)

在 Java 中，对象比较存在三个维度的概念：`==` 运算符、`equals()` 方法以及 `hashCode()` 方法。理解三者的区别与联系，是避免集合类 Bug 的关键。

### 1.1 == 运算符：引用层面的比较

`==` 是 Java 的基本运算符，其行为取决于操作数的类型：

- **基本数据类型**（`int`, `double`, `boolean` 等）：直接比较栈内存中的值。
- **引用数据类型**（对象）：比较的是堆内存中的**引用地址**（即对象句柄），而非对象内容。

```java
String a = new String("hello");
String b = new String("hello");
System.out.println(a == b); // false，因为 a 和 b 指向堆中不同地址
```

### 1.2 equals() 方法：逻辑内容的比较

`equals()` 定义在 `java.lang.Object` 中，默认实现依然是 `==`（比较引用）。为了比较对象的"逻辑相等性"，子类必须重写该方法。

重写的 `equals()` 必须满足以下五大契约：

1. **自反性**（Reflexive）：`x.equals(x)` 必须返回 `true`。
2. **对称性**（Symmetric）：`x.equals(y)` 为 `true`，则 `y.equals(x)` 也必须为 `true`。
3. **传递性**（Transitive）：若 `x.equals(y)` 且 `y.equals(z)` 为 `true`，则 `x.equals(z)` 也为 `true`。
4. **一致性**（Consistent）：只要对象未被修改，多次调用结果应一致。
5. **非空性**（Non-nullity）：`x.equals(null)` 必须返回 `false`。

### 1.3 hashCode() 方法：哈希定位的索引

`hashCode()` 返回一个 `int` 值，称为哈希码。它的设计初衷是为了提高哈希容器（`HashMap`, `HashSet`, `Hashtable`）的查找效率。

---

## 二、hashCode 契约

`Object` 规范明确规定了 `hashCode` 与 `equals` 的绑定关系：

> **如果两个对象通过 `equals()` 判断为相等，那么它们的 `hashCode()` 必须相同。**

反之不成立：`hashCode` 相同的对象，`equals` 不一定为 `true`（这就是哈希碰撞）。

### 2.1 为什么必须遵守契约？

以 `HashMap` 为例，其 `put/get` 操作的流程如下：

1. 计算 Key 的 `hashCode`，经过扰动函数处理后确定桶（Bucket）索引。
2. 遍历该桶中的链表或红黑树，使用 `equals()` 精确匹配 Key。

如果重写了 `equals` 但未重写 `hashCode`：

- 两个逻辑相等的对象可能产生不同的 `hashCode`。
- `HashMap` 会将它们放入不同的桶中。
- `get()` 时无法找到已 `put` 的对象，导致数据丢失或重复插入。

```java
// 反例：只重写 equals，未重写 hashCode
class BadKey {
    String name;
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        BadKey badKey = (BadKey) o;
        return Objects.equals(name, badKey.name);
    }
    // 缺少 hashCode 重写！
}

Map<BadKey, Integer> map = new HashMap<>();
BadKey k1 = new BadKey(); k1.name = "wb";
BadKey k2 = new BadKey(); k2.name = "wb";
map.put(k1, 1);
System.out.println(map.get(k2)); // null！因为 k1 和 k2 的 hashCode 不同
```

---

## 三、代码示例与陷阱

### 3.1 String 的 == 陷阱：常量池 vs 堆

`String` 是 Java 中最特殊的引用类型，因为它拥有字符串常量池（String Constant Pool）。

```java
String s1 = "hello";           // 从常量池获取
String s2 = "hello";           // 同样指向常量池中的同一对象
System.out.println(s1 == s2);  // true

String s3 = new String("hello"); // 在堆中创建新对象
System.out.println(s1 == s3);    // false

String s4 = s3.intern();         // 手动入池，返回池中的引用
System.out.println(s1 == s4);    // true
```

**陷阱提示**：在生产环境中，永远不要使用 `==` 比较字符串内容，应始终使用 `equals()`。

### 3.2 Integer 缓存的 == 陷阱

Java 对 `-128` 到 `127` 之间的 `Integer` 做了缓存（`IntegerCache`）。

```java
Integer a = 100;
Integer b = 100;
System.out.println(a == b); // true，命中缓存

Integer c = 200;
Integer d = 200;
System.out.println(c == d); // false，超出缓存范围，创建了新对象
```

**最佳实践**：包装类型之间的比较，一律使用 `Objects.equals()` 或 `intValue()`。

### 3.3 HashMap 中的 hashCode 扰动函数

`HashMap` 并非直接使用 `hashCode()` 的值，而是进行了一次扰动处理：

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

**设计意图**：将高 16 位与低 16 位进行异或，使高位信息也能参与寻址。因为 HashMap 的容量通常是 2 的幂，`(n - 1) & hash` 实际上只使用了 hash 的低位。如果不做扰动，当 hashCode 的低位分布不均匀时，碰撞概率会急剧上升。

---

## 四、最佳实践

### 4.1 使用 Objects 工具类

手动编写 `equals` 和 `hashCode` 容易遗漏 `null` 检查，推荐使用 JDK 7 引入的工具类：

```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;
    User user = (User) o;
    return id == user.id && Objects.equals(name, user.name);
}

@Override
public int hashCode() {
    return Objects.hash(id, name);
}
```

### 4.2 利用 Lombok 简化代码

在实体类上添加注解，由编译器自动生成符合契约的代码：

```java
@Data
@EqualsAndHashCode
public class User {
    private Long id;
    private String name;
}
```

**注意**：如果类中有敏感字段（如密码）或不参与业务唯一性的字段（如创建时间），应在注解中排除：
`@EqualsAndHashCode(exclude = {"password", "createTime"})`

### 4.3 IDEA 一键生成

快捷键 `Alt + Insert` → `equals() and hashCode()`，选择模板即可。IDEA 生成的代码已经过充分优化，能处理绝大多数场景。

---

## 五、常见陷阱

### 5.1 hashCode 碰撞与性能退化

虽然 `hashCode` 相同不代表 `equals` 相同，但如果大量对象的 `hashCode` 都集中在同一个值，会导致 `HashMap` 退化为链表（JDK 8 之前）或频繁触发红黑树转换（JDK 8+）。

**错误示范**：
```java
@Override
public int hashCode() {
    return 1; // 所有对象进入同一个桶，HashMap 退化为 O(n)
}
```

### 5.2 可变字段参与 hashCode

如果将可变字段（如 `List` 或未加 `final` 的业务状态）加入 `hashCode` 计算，当对象被放入 `HashSet` 后修改了该字段，会导致 `hashCode` 改变，从而永远无法从集合中删除该对象。

**建议**：尽量使用不可变字段（如 `id`、`uuid`）作为 `hashCode` 的计算依据。

### 5.3 继承体系下的对称性破坏

当子类增加新的比较字段时，`instanceof` 的使用会导致对称性失效。
- 父类 `equals` 使用 `instanceof` 判断子类，认为两者相等。
- 子类 `equals` 使用 `getClass()` 判断，认为两者不等。

**解决方案**：在 `equals` 中使用 `getClass()` 而非 `instanceof`，或者遵循《Effective Java》中关于继承与 `equals` 的复合模式建议。

---

## 六、面试话术（30 秒版）

"`==` 比较的是引用地址，而 `equals` 用于比较对象的逻辑内容。`hashCode` 是为了配合 `HashMap` 等哈希容器提高效率的。

Java 规定：如果两个对象 `equals` 相等，它们的 `hashCode` 必须相同。否则在 `HashMap` 中会出现 put 进去却 get 不到的情况。

在实际开发中，我通常使用 `Objects.equals` 处理 null 安全，或者直接用 Lombok 的 `@Data` 注解自动生成符合契约的代码。另外要注意，String 和 Integer 包装类在使用 `==` 时有常量池和缓存的陷阱，比较包装类型一定要用 `equals`。"

---

## 七、交叉引用

- 主模块：[`01.java`](../../../01.java/) — Java 知识体系
- [HashMap](../../../01.java/collection/hashmap.md) — HashMap 底层原理详解
- [String](../../../01.java/concepts/string/README.md) — 字符串常量池与 intern 机制
