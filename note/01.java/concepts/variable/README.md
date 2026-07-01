<!--
module:
  parent: java
  slug: java/variable
  type: article
  category: 主模块子文章
  summary: 变量
-->

# 变量

## 引言：基础概念

变量 是入门必学的基础概念。

本篇给出一句话定义 + 最小可运行示例 + 3 个常见误区，**5 分钟读完，10 分钟上手**。

---

## 成员变量与局部变量的区别

| 对比维度 | 成员变量 | 局部变量 |
|---------|---------|---------|
| **所属** | 属于类（或实例） | 属于方法或代码块 |
| **修饰符** | 可用`public`/`private`/`static`/`final`等 | 不能用访问修饰符和`static`，可用`final` |
| **存储位置** | `static`成员变量在方法区（JDK 8+ 在 HotSpot 中实际存储于元空间/堆中）；非`static`在堆中 | 栈内存中 |
| **生命周期** | 实例变量随对象创建而存在，随对象销毁而消亡；静态变量随类加载而存在，随类卸载而消亡 | 随方法调用而创建，随方法结束而消亡 |
| **默认值** | 有默认值（如`int`为0，引用为`null`） | 无默认值，必须显式初始化 |

```java
public class Example {
    private int memberVar = 10;       // 成员变量 - 属于实例
    private static int staticVar = 5; // 成员变量 - 属于类（静态变量）

    public void method() {
        int localVar = 20;            // 局部变量 - 属于方法
        // int uninitVar;             // 编译错误：局部变量未赋值，使用前必须初始化
    }
}
```

## 静态变量（`static`变量）

静态变量是被`static`关键字修饰的成员变量：

- 被类的所有实例**共享**，无论创建多少个对象，都共享同一份静态变量
- 在**类加载**时初始化，早于对象创建
- 可以通过**类名**直接访问，无需创建对象实例
- 目的是**节省内存**

```java
public class Counter {
    private static int count = 0;  // 所有实例共享

    public Counter() {
        count++;
    }

    public static int getCount() {
        return count;
    }
}

// 使用（同一文件中，只能有一个 public 顶层类，因此 Main 使用包私有访问级别）
class Main {
    public static void main(String[] args) {
        new Counter();
        new Counter();
        System.out.println(Counter.getCount());  // 2
    }
}
```

> **注意**：在多线程环境下，静态变量需要同步访问（使用`synchronized`或`AtomicInteger`等），否则可能出现竞态条件。

## 字符型常量和字符串常量的区别

| 对比维度 | 字符常量 | 字符串常量 |
|---------|---------|----------|
| **形式** | 单引号`'a'` | 双引号`"abc"` |
| **本质** | 相当于一个整型值（Unicode 码点） | `String` 对象引用，指向字符串常量池中的字符串对象 |
| **占用空间** | 2字节（`char`） | 若干个字节（取决于长度） |
| **运算** | 可以参与表达式运算 | 不能直接参与数值运算 |

```java
char ch = 'A';
int ascii = ch;           // 65（隐式转换为 int）
String str = "Hello";     // 字符串常量，存储在字符串常量池中
```

## `final`关键字与变量

`final`可以修饰变量，表示该变量一旦被赋值后就不能再修改：

```java
import java.util.List;
import java.util.ArrayList;

public class FinalDemo {
    public void demo() {
        // final 基本类型变量 - 值不可变
        final int MAX_SIZE = 100;
        // MAX_SIZE = 200;  // 编译错误

        // final 引用类型变量 - 引用不可变，但对象内容可变
        final List<String> list = new ArrayList<>();
        list.add("item");         // 合法 - 修改的是对象内容
        // list = new ArrayList<>();  // 编译错误 - 不能改变引用
    }
}
```

### `final`、`finally`、`finalize`的区别

| 关键字 | 说明 |
|-------|------|
| `final` | 修饰符。修饰类表示不可继承，修饰方法表示不可重写，修饰变量表示不可修改 |
| `finally` | 异常处理关键字。`try-catch-finally`中保证代码一定会被执行（除`System.exit()`或JVM崩溃外） |
| `finalize` | `Object`类的方法。垃圾回收前可能调用的清理方法。Java 9 起已标记为 `@Deprecated`，Java 18（JEP 421）起标记为"for removal"，但截至目前版本（Java 26）尚未正式移除。不推荐使用，应改用 `Cleaner` 或 `AutoCloseable` |

### Effectively Final 变量

Java 8 起，lambda 表达式和匿名内部类可以引用**effectively final**的局部变量——即未显式声明 `final`，但实际只赋值一次的变量。

```java
public class EffectivelyFinalDemo {
    public static void main(String[] args) {
        String greeting = "Hello";  // 未声明 final，但只赋值一次 → effectively final
        // greeting = "Hi";         // 若取消此行注释，greeting 不再是 effectively final

        Runnable task = () -> System.out.println(greeting);  // 合法
        task.run();  // Hello
    }
}
```

> **注意**：如果变量在声明后被重新赋值，则不再是 effectively final，此时在 lambda 或匿名内部类中引用它会导致编译错误。

## `static final` 常量（编译期常量）

当 `static` 和 `final` 同时修饰一个变量时，该变量成为**编译期常量**（constant variable），具有以下特殊语义：

- **编译期内联替换**：编译器在编译时直接将常量值替换到所有引用处，运行时不再访问该变量
- **命名规范**：全大写，单词间用下划线分隔（如 `MAX_SIZE`、`DEFAULT_TIMEOUT`）
- **与 `final` 实例变量的区别**：`final` 实例变量在每次创建对象时初始化，可以每个实例拥有不同的值；`static final` 常量在类加载时初始化，所有实例共享同一个值

```java
public class Constants {
    // 编译期常量 - 值在编译时确定并内联替换
    public static final int MAX_SIZE = 100;
    public static final String APP_NAME = "MyApp";
    public static final double PI = 3.141592653589793;

    // final 实例变量 - 每个对象可以有不同的值
    private final int id;

    public Constants(int id) {
        this.id = id;  // 在构造器中赋值，之后不可修改
    }
}

// 使用
class App {
    public static void main(String[] args) {
        System.out.println(Constants.MAX_SIZE);   // 100
        System.out.println(Constants.APP_NAME);   // MyApp
    }
}
```

## `var` 局部变量类型推断（Java 10+）

Java 10 引入了 `var` 受限标识符（restricted identifier），允许编译器根据初始化表达式自动推断局部变量的类型，减少冗余的类型声明：

```java
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class VarDemo {
    public static void main(String[] args) {
        // 基本用法 - 编译器自动推断类型
        var name = "Alice";                // 推断为 String
        var age = 25;                      // 推断为 int
        var pi = 3.14;                     // 推断为 double
        var list = new ArrayList<String>(); // 推断为 ArrayList<String>
        var map = new HashMap<String, Integer>(); // 推断为 HashMap<String, Integer>

        // 与 final 结合 - 不可变引用 + 类型推断
        final var MAX_RETRY = 3;           // 推断为 int，且不可修改

        // for 循环中使用
        var items = List.of("a", "b", "c");
        for (var item : items) {           // item 推断为 String
            System.out.println(item);
        }
    }
}
```

**适用场景**：当右侧类型已经很明显时，使用 `var` 可以减少冗余，提高可读性。

```java
// 使用 var 前
BufferedReader reader = new BufferedReader(new FileReader("data.txt"));
// 使用 var 后 - 类型信息已在右侧体现
var reader = new BufferedReader(new FileReader("data.txt"));
```

**限制**：

- **仅用于局部变量**：不能用于成员变量、方法参数、方法返回值
- **必须初始化**：`var x;` 是非法的，编译器无法推断类型
- **不能推断为 `null`**：`var x = null;` 是非法的，`null` 不携带类型信息
- **不能用于数组字面量**：`var arr = {1, 2, 3};` 是非法的，需改为 `var arr = new int[]{1, 2, 3};`
