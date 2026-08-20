<!--
module:
  parent: java
  slug: java/creational-patterns/singleton
  type: article
  category: 主模块子文章
  summary: 单例模式 5 种实现对比 + 反射/序列化破坏 + 选型指南（split-hairs 迁出）
-->

# 单例模式（split-hairs 视角）

> **定位**：单例模式 5 种实现对比 + 反射/序列化破坏 + 选型指南 的核心原理、实现与最佳实践。
>
> 本节由 `12.interview/01.java/singleton-pattern/` 迁出，按"面试优先级"重新组织：5 种实现 → 8 种破坏方式 → 选型推荐。完整原理与基础实现见 [creation/README.md](./README.md#一单例模式-singleton)。

## 引言：为什么单例如此重要？

```java
// 数据库连接池，全系统只需要一个
DatabasePool pool1 = new DatabasePool();
DatabasePool pool2 = new DatabasePool();  // ❌ 两个连接池？资源浪费 + 不一致！

// Spring BeanFactory 本质上就是单例
```

保证一个类**全局只有一个实例**，并提供统一访问点。Java 5+ 提供了 5 种主流写法，每种都有性能/线程安全/防破坏的取舍。

---

## 5 种主流实现对比速查

| 实现方式 | 线程安全 | 懒加载 | 防反射攻击 | 防序列化破坏 | 推荐指数 |
|---------|:------:|:-----:|:--------:|:----------:|:-------:|
| 饿汉式 | ✅ | ❌ | ❌ | ❌ | ★★☆ |
| 懒汉式（同步方法） | ✅ | ✅ | ❌ | ❌ | ★☆☆ |
| 双重检查锁（DCL） | ✅ | ✅ | 需处理 | 需处理 | ★★★ |
| 静态内部类 | ✅ | ✅ | ❌ | 需处理 | ★★★★ |
| 枚举单例 | ✅ | ❌ | ✅ | ✅ | ★★★★★ |

### 1. 饿汉式（静态常量）— 最简单

```java
public class Singleton {
    private static final Singleton INSTANCE = new Singleton();
    private Singleton() {}
    public static Singleton getInstance() { return INSTANCE; }
}
```

- ✅ 类加载即初始化，线程安全，代码最简
- ❌ 非懒加载，可能浪费内存（如果实例很重）

### 2. 懒汉式（线程不安全）— 反面教材

```java
public class Singleton {
    private static Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();  // ❌ 多线程下可能创建多个实例
        }
        return instance;
    }
}
```

### 3. 懒汉式（同步方法）— 性能杀手

```java
public static synchronized Singleton getInstance() {
    if (instance == null) instance = new Singleton();
    return instance;
}
```

- ✅ 线程安全 + 懒加载
- ❌ **每次调用都同步**，并发性能差

### 4. 双重检查锁（DCL）— 高并发首选

```java
public class Singleton {
    private static volatile Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {                       // 第一次检查（无锁）
            synchronized (Singleton.class) {
                if (instance == null) {                // 第二次检查（有锁）
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

- 关键点：`volatile` 必须加，否则 JMM 下可能**返回未初始化的半成品对象**（`new` 操作分 3 步：分配内存 → 初始化 → 赋值引用，无 volatile 可能被重排序）
- 适用：JDK 1.5+ 懒加载 + 高并发场景

### 5. 静态内部类（Holder）— 推荐写法之一

```java
public class Singleton {
    private Singleton() {}
    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }
    public static Singleton getInstance() { return Holder.INSTANCE; }
}
```

- 原理：JVM 保证类加载时初始化 `Holder`，线程安全天然达成
- 优点：懒加载 + 线程安全 + 代码简洁，无需 `volatile`

### 6. 枚举单例（Effective Java 强烈推荐）

```java
public enum Singleton {
    INSTANCE;
    public void doSomething() { System.out.println("业务方法"); }
}

// 使用
Singleton.INSTANCE.doSomething();
```

- ✅ **天然防反射攻击**（构造器由 JVM 反射禁止调用）
- ✅ **天然防序列化破坏**（JVM 特殊处理枚举的序列化）
- ✅ 线程安全由 JVM 保证
- ❌ 无法懒加载；语义上不如类直观

---

## 反射/序列化如何破坏单例？

### 反射破坏（攻击 4 种实现）

```java
// 通过反射调用私有构造器，绕过单例检查
Constructor<Singleton> c = Singleton.class.getDeclaredConstructor();
c.setAccessible(true);
Singleton s1 = Singleton.getInstance();
Singleton s2 = c.newInstance();   // ❌ 创建了新实例！
```

**防御**：在构造器中抛 `RuntimeException`（但仍有被反射二次攻击的风险）。

### 序列化破坏

```java
// 序列化 + 反序列化会创建新对象
ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("singleton"));
oos.writeObject(Singleton.INSTANCE);
ObjectInputStream ois = new ObjectInputStream(new FileInputStream("singleton"));
Singleton s = (Singleton) ois.readObject();   // ❌ 新实例！
```

**防御**：实现 `readResolve()` 方法返回 `INSTANCE`：

```java
private Object readResolve() { return INSTANCE; }
```

**枚举单例免疫**：JVM 内部对枚举的序列化和反射都有特殊处理。

---

## 30 秒面试话术

> "Java 单例有 5 种写法：饿汉式（线程安全但浪费）、懒汉式（性能差）、DCL（高并发首选，注意 `volatile` 防半初始化）、静态内部类（推荐写法之一）、枚举（Effective Java 最佳实践，天然防反射和序列化）。**实际项目优先用枚举**，需要懒加载用静态内部类，Spring 项目直接交给 IOC 容器管理。"

## 最佳实践选型

| 场景 | 推荐实现 |
|------|---------|
| Java 5+ 通用场景 | **枚举单例**（Effective Java Item 3 推荐） |
| 需要懒加载 | 静态内部类 |
| 高并发 + 性能关键 | DCL + `volatile` |
| Spring 项目 | 直接用容器（`@Component` 默认 singleton） |
| 配置文件 / Logger / Spring Bean | 全部交由容器管理，**无需手写单例** |

---

## 相关章节

- [创建型模式总览](./README.md) — 单例 / 工厂 / 建造者
- [设计模式主文档](../README.md) — GoF 23 种模式选型
- [`06.spring/01-core` 容器单例](../../../04.spring-backend/01-core/README.md) — Spring Bean 默认 scope=singleton

← [返回 创建型模式](./README.md)
