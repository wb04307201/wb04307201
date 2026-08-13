<!--
question:
  id: 01.java-interface-vs-abstract
  topic: 01.java
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 概念辨析
  tags: [01.java, OOP, interface, abstract]
-->

# 接口 vs 抽象类：到底怎么选？

> ⬅️ [返回 Java 咬文嚼字](../README.md)

## 引子：面试官："这两个不是一样吗？"

```java
// 选项 A：抽象类
public abstract class Animal {
    private String name;
    public abstract void makeSound();
    public void breathe() {
        System.out.println(name + " is breathing");
    }
}

// 选项 B：接口
public interface Animal {
    void makeSound();
    default void breathe() {
        System.out.println("breathing");
    }
}
```

面试官问："Java 8 之后接口有 default 方法，接口和抽象类不是一样了吗？你平时怎么选？"

---

## 一、核心对比

| 维度 | 接口（interface） | 抽象类（abstract class） |
|------|-------------------|-------------------------|
| **设计目的** | 行为契约（能做什么） | 代码复用（是什么） |
| **构造器** | 无 | 有（子类必须调用 `super()`） |
| **成员变量** | 只能 `public static final` | 任意修饰符的实例变量 |
| **方法** | JDK 8+ 有 `default` / `static`，JDK 9+ 有 `private` | 任意（抽象 / 具体 / 静态 / 私有） |
| **继承关系** | 多实现（`implements A, B, C`） | 单继承（`extends` 只能一个） |
| **访问修饰符** | 方法默认 `public` | 任意（`private` / `protected` / `public`） |
| **实例化** | 不能 | 不能（但含构造器） |

---

## 二、设计哲学

### 接口 = "能做什么"（Can-Do）

接口描述的是**能力**或**契约**，与类的本质身份无关。

```java
// 这些是行为契约，不是"是什么"
public interface Flyable {
    void fly();
}

public interface Serializable { }   // 标记接口：可序列化能力
public interface Comparable<T> {    // 可比较能力
    int compareTo(T other);
}
```

一个 `Bird` 类可以同时是 `Animal`（is-a）+ `Flyable`（can-do）+ `Serializable`（can-do），这体现了接口的**正交性**。

### 抽象类 = "是什么"（Is-A）

抽象类描述的是**本质身份**，建立的是 is-a 继承层次。

```java
// 这些是身份层次，不是"能做什么"
public abstract class Animal {
    protected String name;
    public abstract void makeSound();
    public void breathe() {
        System.out.println(name + " is breathing");
    }
}

public class Dog extends Animal {   // Dog IS-A Animal
    @Override
    public void makeSound() {
        System.out.println("Woof!");
    }
}
```

**判断口诀**：如果去掉抽象方法后，剩余代码仍有意义（共享状态 / 构造逻辑 / 具体方法）→ 用抽象类；如果只剩方法签名列表 → 用接口。

---

## 三、JDK 8+ 的变化

| 版本 | 变化 | 说明 |
|------|------|------|
| JDK 8 | `default` 方法 | 接口可以有具体实现，向后兼容（如 `Collection.forEach`） |
| JDK 8 | `static` 方法 | 接口可以有静态工具方法（如 `Comparator.comparing`） |
| JDK 9 | `private` 方法 | 接口内部可复用代码，避免 default 方法暴露实现细节 |

**关键认知**：default 方法 ≠ 抽象类可以取代接口。default 的初衷是**向后兼容**（给已有接口加方法而不破坏实现类），不是让接口变成"轻量抽象类"。

---

## 四、选择原则

| 场景 | 推荐 | 原因 |
|------|------|------|
| 定义 API 契约 | 接口 | 解耦 + 实现无关 |
| 需要共享实例变量 | 抽象类 | 接口不能有非 final 字段 |
| 需要共享构造逻辑 | 抽象类 | 接口无构造器 |
| 需要多继承行为 | 接口 | 类只能 extends 一个，但 implements 多个 |
| 框架设计 | 接口 + 抽象基类组合 | Spring 风格：`List` 接口 + `AbstractList` 基类 |

**框架最佳实践**：对外暴露接口（用户编程面向接口），对内提供抽象基类（减少实现成本）。

```java
// 用户面向接口编程
List<String> list = new ArrayList<>();

// 框架提供抽象基类降低实现成本
public abstract class AbstractList<E> implements List<E> {
    // 共享实现：size(), isEmpty(), iterator() 等
}
```

---

## 五、面试话术（30 秒版）

> 「**接口是行为契约，抽象类是身份继承。** 接口回答'能做什么'（如 Flyable），抽象类回答'是什么'（如 Animal）。JDK 8 的 default 方法是为了向后兼容，不是让接口变成抽象类。选型时：**优先接口**（解耦 + 多实现），需要共享状态 / 构造逻辑时用抽象类，框架设计中两者组合用（接口 + 抽象基类）。」

---

## 六、交叉引用

- [多态](../polymorphism/) — 4 大核心 Java 多态面试深挖（vtable / default 冲突 / 重写）
- [Object 类](../object/) — 为什么需要 Integer / Double 包装类？
- [OOP 基础](../../../01.java-and-jvm/01-language/oop/README.md) — 面向对象四大核心概念

## 相关章节

- 深度阅读：[`01.java/核心概念`](01.java/README.md) — Java 知识体系导航

← [返回: 咬文嚼字 · interface-vs-abstract](../README.md)
