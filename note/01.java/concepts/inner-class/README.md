# 内部类

Java 允许在一个类的内部定义另一个类，被嵌套的类称为**内部类**（Inner Class），包含它的类称为**外部类**（Outer Class）。

## 内部类的4种类型

### 1. 成员内部类

定义在外部类的成员位置，可以访问外部类的所有成员（包括私有成员）。

```java
public class Outer {
    private String outerField = "外部字段";
    private static String staticField = "静态字段";

    // 成员内部类
    public class Inner {
        public void display() {
            // 可以直接访问外部类的所有成员
            System.out.println(outerField);
            System.out.println(staticField);
            // 也可以显式引用外部类
            System.out.println(Outer.this.outerField);
        }
    }
}

// 使用示例
class Demo {
    public static void main(String[] args) {
        // 创建内部类实例 - 必须通过外部类实例
        Outer outer = new Outer();
        Outer.Inner inner = outer.new Inner();
        inner.display();
    }
}
```

**特点**：
- 持有外部类实例的隐式引用（`Outer.this`）
- 可以访问外部类的所有成员（`private`也可以）
- **不能**定义静态成员（Java 16+ 允许定义所有静态成员；此前仅允许 static final 常量）
- 编译后生成 `Outer$Inner.class` 文件

### 2. 静态内部类

> **术语说明**：严格来说，JLS（Java Language Specification）中"内部类"（Inner Class）仅指非静态嵌套类，`static` 嵌套类应称为**静态嵌套类**（Static Nested Class），不属于内部类。此处沿用中文社区习惯称为"静态内部类"。

用`static`修饰的嵌套类，不持有外部类的引用。

```java
public class Outer {
    private static String staticField = "静态字段";
    private String instanceField = "实例字段";

    // 静态内部类
    public static class StaticInner {
        public void display() {
            System.out.println(staticField);     // 可以访问静态成员
            // System.out.println(instanceField); // 编译错误！不能访问实例成员
        }
    }
}

// 创建静态内部类实例 - 不需要外部类实例（以下代码需放在方法体内才能编译）
// Outer.StaticInner inner = new Outer.StaticInner();
// inner.display();
```

**典型应用 - 静态内部类单例模式**：

```java
public class Singleton {
    private Singleton() { }

    // Singleton 类加载不会触发 Holder 初始化；
    // 只有首次调用 getInstance() 访问 Holder.INSTANCE 时，Holder 才会被初始化
    private static class Holder {
        private static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE;  // 首次调用时触发 Holder 类初始化
    }
}
```

### 3. 局部内部类

定义在方法内部的类，只能在该方法内使用。

```java
public class Outer {
    public void method() {
        final String local = "局部变量";

        // 局部内部类
        class LocalInner {
            public void display() {
                System.out.println(local);  // 可以访问方法的 final 或 effectively final 变量
            }
        }

        LocalInner inner = new LocalInner();
        inner.display();
    }
    // LocalInner 在方法外部不可见
}
```

**特点**：
- 只能访问方法中的`final`或`effectively final`变量（effectively final 指没有声明为`final`，但初始化后从未被重新赋值的变量）
- 不能使用访问修饰符（`public`/`private`/`protected`）
- 编译后生成 `Outer$1LocalInner.class` 文件

### 4. 匿名内部类

没有类名的内部类，通常用于创建实现接口或继承类的**一次性**对象。

```java
// 以下代码需放在方法体内才能编译
// 实现接口的匿名内部类
// Runnable runnable = new Runnable() {
//     @Override
//     public void run() {
//         System.out.println("Running in anonymous class");
//     }
// };
//
// // 继承类的匿名内部类
// Thread thread = new Thread() {
//     @Override
//     public void run() {
//         System.out.println("Thread running");
//     }
// };
//
// // Java 8+ 可以用 Lambda 表达式替代函数式接口的匿名内部类
// Runnable lambda = () -> System.out.println("Running via lambda");
```

## 四种内部类对比

| 对比维度 | 成员内部类 | 静态内部类 | 局部内部类 | 匿名内部类 |
|---------|----------|----------|----------|----------|
| **访问外部实例成员** | 可以 | 不可以 | 可以（同一方法内） | 取决于上下文（实例上下文中可以，静态上下文中不可以） |
| **访问外部静态成员** | 可以 | 可以 | 可以 | 可以 |
| **定义静态成员** | Java 16+ 可以，此前不可以 | 可以 | 不可以 | 不可以 |
| **使用访问修饰符** | 可以 | 可以 | 不可以 | 不可以 |
| **持有外部类引用** | 是 | 否 | 是 | 取决于上下文 |
| **编译后文件名** | `Outer$Inner` | `Outer$StaticInner` | `Outer$1LocalInner` | `Outer$1` |
| **典型场景** | 与外部类强关联 | 工具类、单例 | 方法内辅助逻辑 | 一次性实现 |

## 内部类与 Lambda 表达式

Java 8 引入的 Lambda 表达式可以替代**函数式接口**（只有一个抽象方法的接口）的匿名内部类：

```java
import java.util.Comparator;

// 匿名内部类
Comparator<String> comparator = new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return a.length() - b.length();
    }
};

// Lambda 表达式
Comparator<String> lambda = (a, b) -> a.length() - b.length();

// 方法引用（最简洁）
Comparator<String> methodRef = Comparator.comparingInt(String::length);
```

> **注意**：Lambda 表达式与匿名内部类不完全等价，主要区别：
> - Lambda 的`this`指向外部类实例，而匿名内部类的`this`指向自身
> - Lambda **只能用于函数式接口**（只有一个抽象方法的接口）
> - Lambda 只能捕获**有效 final**（effectively final）的局部变量
> - Lambda **不能声明实例字段或实例方法**，匿名内部类则可以

## 内部类的注意事项

1. **序列化问题**：内部类（尤其是非静态内部类）不建议实现`Serializable`，因为编译器生成的合成字段在不同编译器实现中可能不同
2. **内存泄漏**：非静态内部类持有外部类的引用，如果内部类生命周期比外部类长，可能导致外部类无法被回收
3. **优先使用静态内部类**：如果内部类不需要访问外部类的实例成员，应声明为`static`，避免不必要的引用持有
