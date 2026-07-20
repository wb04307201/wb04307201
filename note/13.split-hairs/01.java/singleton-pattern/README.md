<!--
question:
  id: 01.java-singleton-pattern
  topic: 01.java
  difficulty: ⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [01.java, singleton, pattern]
-->

# 单例模式

## 引子：为什么全局只需要一个？

```java
// 数据库连接池，全系统只需要一个
DatabasePool pool1 = new DatabasePool();
DatabasePool pool2 = new DatabasePool();  // ❌ 两个连接池？资源浪费！

// 配置管理器
ConfigManager config1 = new ConfigManager();
ConfigManager config2 = new ConfigManager();  // ❌ 读两次配置？不一致风险！
```

有些东西，全局只需要一份：数据库连接池、配置中心、Spring 的 BeanFactory……

如何保证**一个类只能创建一个实例**？这就是单例模式。但写法远不止一种——

---

> 📚 **前置知识**：[设计模式](../../../01.java/design-patterns/README.md)

## 一、饿汉式（静态常量）
```java
public class Singleton {
    private static final Singleton instance = new Singleton();
    private Singleton() {}
    public static Singleton getInstance() {
        return instance;
    }
}
```
- **特点**：类加载即初始化，线程安全，非懒加载（适合频繁使用场景）

## 二、懒汉式（线程不安全）
```java
public class Singleton {
    private static Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```
- **问题**：多线程下可能创建多个实例（不推荐）

## 三、懒汉式（同步方法）
```java
public synchronized static Singleton getInstance() {
    if (instance == null) {
        instance = new Singleton();
    }
    return instance;
}
```
- **缺点**：每次获取实例都需同步，性能差

## 四、双重检查锁（DCL）
```java
public class Singleton {
    private static volatile Singleton instance; // volatile保证可见性和有序性
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) { // 第一次检查
            synchronized (Singleton.class) {
                if (instance == null) { // 第二次检查
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```
- **关键点**：`volatile`禁止指令重排序，避免返回未初始化的对象
- **适用场景**：JDK1.5+的懒加载+高并发场景

## 五、静态内部类（推荐）
```java
public class Singleton {
    private Singleton() {}
    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }
    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}
```
- **原理**：类加载时初始化内部类，JVM保证线程安全
- **优点**：懒加载、线程安全、代码简洁

## 六、枚举单例（最佳实践）
```java
public enum Singleton {
    INSTANCE;
    public void doSomething() {
        System.out.println("业务方法");
    }
}
```
- **优势**：
    - 天然防止反射攻击（构造器私有）
    - 序列化安全（无需额外readResolve）
    - 线程安全（由JVM保证）
- **使用**：`Singleton.INSTANCE.doSomething();`

## 七、使用容器（如Spring）
```java
// 实际开发中更推荐通过IOC容器管理单例
@Controller
public class UserController {
    // Spring自动保证单例
}
```

### 对比总结
| 实现方式    | 线程安全 | 懒加载 | 防反射攻击 | 防序列化 | 推荐指数  |
|---------|------|-----|-------|------|-------|
| 饿汉式     | ✅    | ❌   | ❌     | ❌    | ★★☆   |
| 懒汉式（同步） | ✅    | ✅   | ❌     | ❌    | ★☆☆   |
| 双重检查锁   | ✅    | ✅   | 需处理   | 需处理  | ★★★   |
| 静态内部类   | ✅    | ✅   | ❌     | 需处理  | ★★★★  |
| 枚举单例    | ✅    | ❌   | ✅     | ✅    | ★★★★★ |

**最佳实践建议**：
- 优先使用**枚举单例**（Java5+推荐）
- 需要懒加载时使用**静态内部类**
- 避免直接使用反射破坏单例（可通过抛出异常阻止）
- 序列化场景需重写`readResolve()`方法

> 注：在Spring等框架中，通常通过容器管理bean的单例状态，无需手动实现单例模式。## 相关章节

- 深度阅读：[`01.java/设计模式`](../../../01.java/design-patterns/README.md) — GoF 23 种设计模式
- 相关：[`06.spring/01-core`](../../../06.spring/01-core/README.md) — Spring 单例 Bean（容器管理单例）

← [返回: 咬文嚼字 · singleton-pattern](../README.md)
