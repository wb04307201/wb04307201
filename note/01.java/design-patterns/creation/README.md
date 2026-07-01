<!--
module:
  parent: java
  slug: java/creational-patterns
  type: article
  category: 主模块子文章
  summary: 创建型模式
-->

# 创建型模式

> 关注对象的创建过程，将实例化与使用分离，使系统更灵活、更易扩展。

---
## 引言：架构困境

创建型模式 的关键不是'选型'——是**选完之后怎么在 5 个 trade-off 里活下来**。

本篇用'决策困境'切入，比较几种主流路径并讲清取舍。

---

## 一、单例模式 Singleton

确保一个类只有一个实例，并提供全局访问点。

### 1.1 饿汉式（Eager Initialization）

```java
/**
 * 饿汉式：类加载时创建实例，线程安全
 */
public class EagerSingleton {

    private static final EagerSingleton INSTANCE = new EagerSingleton();

    private EagerSingleton() {
        // 私有构造，防止外部 new
    }

    public static EagerSingleton getInstance() {
        return INSTANCE;
    }
}
```

| 优点 | 缺点 |
|------|------|
| 类加载即创建，线程安全 | 可能造成资源浪费（未使用也创建） |
| 代码简洁 | 无法传递参数 |

### 1.2 懒汉式（Lazy Initialization）

```java
/**
 * 懒汉式：首次使用时创建，需同步保证线程安全
 */
public class LazySingleton {

    private static LazySingleton instance;

    private LazySingleton() {}

    public static synchronized LazySingleton getInstance() {
        if (instance == null) {
            instance = new LazySingleton();
        }
        return instance;
    }
}
```

| 优点 | 缺点 |
|------|------|
| 延迟加载 | synchronized 导致每次调用都加锁，性能差 |

### 1.3 双重检查锁 DCL（Double-Checked Locking）

```java
/**
 * DCL：只在首次创建时加锁，兼顾性能与延迟加载
 */
public class DclSingleton {

    // volatile 禁止指令重排序，防止其他线程拿到半成品
    private static volatile DclSingleton instance;

    private DclSingleton() {}

    public static DclSingleton getInstance() {
        if (instance == null) {                 // 第一次检查（无锁）
            synchronized (DclSingleton.class) {
                if (instance == null) {         // 第二次检查（有锁）
                    instance = new DclSingleton();
                }
            }
        }
        return instance;
    }
}
```

> `volatile` 关键字必不可少，否则在 JMM 下可能发生「半初始化」问题。

### 1.4 静态内部类（Static Inner Class / Initialization-on-Demand）

```java
/**
 * 静态内部类：利用类加载机制保证线程安全，推荐写法之一
 */
public class StaticInnerSingleton {

    private StaticInnerSingleton() {}

    // 外部类加载时不会加载内部类，首次调用 getInstance 才触发
    private static class Holder {
        static final StaticInnerSingleton INSTANCE = new StaticInnerSingleton();
    }

    public static StaticInnerSingleton getInstance() {
        return Holder.INSTANCE;
    }
}
```

| 优点 | 缺点 |
|------|------|
| 延迟加载 + 线程安全，无需 volatile | 反射/序列化可破坏（需额外防范） |

### 1.5 枚举单例（Enum Singleton）

```java
/**
 * 枚举单例：Effective Java 推荐写法
 */
public enum EnumSingleton {

    INSTANCE;

    public void doSomething() {
        System.out.println("业务逻辑");
    }
}

// 使用
EnumSingleton.INSTANCE.doSomething();
```

| 优点 | 缺点 |
|------|------|
| 天然线程安全、防反射、防序列化破坏 | 无法延迟加载；不直观 |

### 1.6 模式对比

| 实现方式 | 线程安全 | 延迟加载 | 性能 | 推荐度 |
|----------|:--------:|:--------:|:----:|:------:|
| 饿汉式 | 是 | 否 | 高 | 一般场景 |
| 懒汉式（synchronized） | 是 | 是 | 低 | 不推荐 |
| DCL（volatile） | 是 | 是 | 高 | 推荐 |
| 静态内部类 | 是 | 是 | 高 | 推荐 |
| 枚举 | 是 | 否 | 高 | 最推荐 |

---

## 二、工厂模式 Factory Pattern

将对象创建过程封装起来，客户端不直接使用 new。

### 2.1 简单工厂（Simple Factory）

```java
/**
 * 产品接口
 */
public interface Payment {
    void pay(double amount);
}

public class Alipay implements Payment {
    @Override public void pay(double amount) {
        System.out.println("支付宝支付: " + amount);
    }
}

public class WechatPay implements Payment {
    @Override public void pay(double amount) {
        System.out.println("微信支付: " + amount);
    }
}

/**
 * 简单工厂
 */
public class PaymentFactory {

    public static Payment create(String type) {
        return switch (type.toLowerCase()) {
            case "alipay"  -> new Alipay();
            case "wechat"  -> new WechatPay();
            default -> throw new IllegalArgumentException("未知支付类型: " + type);
        };
    }
}

// 使用
Payment payment = PaymentFactory.create("alipay");
payment.pay(100.0);
```

### 2.2 工厂方法（Factory Method）

```java
/**
 * 工厂方法：每个具体产品对应一个具体工厂
 */
public interface PaymentFactory {
    Payment createPayment();
}

public class AlipayFactory implements PaymentFactory {
    @Override public Payment createPayment() { return new Alipay(); }
}

public class WechatPayFactory implements PaymentFactory {
    @Override public Payment createPayment() { return new WechatPay(); }
}

// 使用
PaymentFactory factory = new AlipayFactory();
Payment payment = factory.createPayment();
payment.pay(200.0);
```

### 2.3 抽象工厂（Abstract Factory）

```java
/**
 * 抽象工厂：创建一组相关/相互依赖的对象
 */
public interface UIComponentFactory {
    Button createButton();
    Dialog createDialog();
}

// Windows 系列
public class WindowsFactory implements UIComponentFactory {
    @Override public Button createButton() { return new WindowsButton(); }
    @Override public Dialog createDialog() { return new WindowsDialog(); }
}

// Mac 系列
public class MacFactory implements UIComponentFactory {
    @Override public Button createButton() { return new MacButton(); }
    @Override public Dialog createDialog() { return new MacDialog(); }
}

// 使用
UIComponentFactory factory = new WindowsFactory();
Button btn = factory.createButton();
Dialog dlg = factory.createDialog();
```

### 2.4 工厂模式对比

| 类型 | 扩展性 | 复杂度 | 适用场景 |
|------|:------:|:------:|----------|
| 简单工厂 | 差（违反开闭） | 低 | 产品种类少且稳定 |
| 工厂方法 | 好 | 中 | 每种产品独立扩展 |
| 抽象工厂 | 好 | 高 | 产品族（多个相关产品族） |

---

## 九、建造者模式 Builder

将复杂对象的构建与表示分离，同样的构建过程可以创建不同的表示。

### 9.1 经典 Builder 实现

```java
/**
 * 产品类
 */
public class Computer {

    private final String cpu;
    private final String ram;
    private final String disk;
    private final String gpu;
    private final String os;

    // 私有构造
    private Computer(Builder builder) {
        this.cpu  = builder.cpu;
        this.ram  = builder.ram;
        this.disk = builder.disk;
        this.gpu  = builder.gpu;
        this.os   = builder.os;
    }

    @Override
    public String toString() {
        return "Computer{cpu='%s', ram='%s', disk='%s', gpu='%s', os='%s'}"
                .formatted(cpu, ram, disk, gpu, os);
    }

    /**
     * 静态内部 Builder
     */
    public static class Builder {
        private String cpu;
        private String ram;
        private String disk;
        private String gpu;
        private String os;

        public Builder cpu(String cpu) { this.cpu = cpu; return this; }
        public Builder ram(String ram) { this.ram = ram; return this; }
        public Builder disk(String disk) { this.disk = disk; return this; }
        public Builder gpu(String gpu) { this.gpu = gpu; return this; }
        public Builder os(String os) { this.os = os; return this; }

        public Computer build() {
            // 可以在这里做最终校验
            if (cpu == null) throw new IllegalStateException("CPU 不能为空");
            return new Computer(this);
        }
    }
}

// 使用
Computer computer = new Computer.Builder()
        .cpu("Intel i9-14900K")
        .ram("64GB DDR5")
        .disk("2TB NVMe SSD")
        .gpu("RTX 4090")
        .os("Ubuntu 24.04 LTS")
        .build();

System.out.println(computer);
```

### 9.2 Lombok @Builder

```java
import lombok.Builder;

@Builder
public class User {
    private String username;
    private String email;
    private int age;
    private String role;
}

// 使用（Lombok 自动生成 Builder）
User user = User.builder()
        .username("admin")
        .email("admin@example.com")
        .age(30)
        .role("ADMIN")
        .build();
```

### 9.3 Builder vs 构造器 vs JavaBean

| 维度 | 重叠构造器 | JavaBean（setter） | Builder |
|------|-----------|-------------------|---------|
| 参数多时可读性 | 差 | 好 | 好 |
| 不可变性 | 可以做到 | 做不到 | 可以做到 |
| 一致性校验 | 分散 | 困难 | build() 统一校验 |
| 推荐度 | 参数少时用 | 不推荐 | 参数 >= 4 时推荐 |

---

## 相关章节

- [设计模式总览](../README.md)
- [结构型模式](../structural/README.md)
- [行为型模式](../behavioral/README.md)
