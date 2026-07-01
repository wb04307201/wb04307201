<!--
module:
  parent: java
  slug: java/structural-patterns
  type: article
  category: 主模块子文章
  summary: 结构型模式
-->

# 结构型模式

> 关注类和对象的组合方式，通过组合关系实现松耦合的灵活结构。

---
## 引言：架构困境

结构型模式 的关键不是'选型'——是**选完之后怎么在 5 个 trade-off 里活下来**。

本篇用'决策困境'切入，比较几种主流路径并讲清取舍。

---

## 三、代理模式 Proxy

为其他对象提供一种代理，控制对这个对象的访问。

### 3.1 静态代理

```java
/**
 * 真实主题接口
 */
public interface UserService {
    void save(String name);
}

public class UserServiceImpl implements UserService {
    @Override public void save(String name) {
        System.out.println("保存用户: " + name);
    }
}

/**
 * 静态代理类：编译期确定
 */
public class UserServiceProxy implements UserService {

    private final UserService target;

    public UserServiceProxy(UserService target) {
        this.target = target;
    }

    @Override
    public void save(String name) {
        System.out.println("[事务] 开启事务");
        target.save(name);
        System.out.println("[事务] 提交事务");
    }
}

// 使用
UserService proxy = new UserServiceProxy(new UserServiceImpl());
proxy.save("张三");
```

### 3.2 JDK 动态代理

```java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

/**
 * JDK 动态代理：基于接口，运行时生成代理类
 */
public class JdkProxyHandler implements InvocationHandler {

    private final Object target;

    public JdkProxyHandler(Object target) {
        this.target = target;
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        System.out.println("[前置增强] " + method.getName());
        Object result = method.invoke(target, args);
        System.out.println("[后置增强] " + method.getName());
        return result;
    }

    @SuppressWarnings("unchecked")
    public <T> T getProxy() {
        return (T) Proxy.newProxyInstance(
                target.getClass().getClassLoader(),
                target.getClass().getInterfaces(),
                this);
    }
}

// 使用
UserService target = new UserServiceImpl();
UserService proxy = new JdkProxyHandler(target).getProxy();
proxy.save("李四");
```

### 3.3 CGLIB 动态代理

```java
import net.sf.cglib.proxy.Enhancer;
import net.sf.cglib.proxy.MethodInterceptor;
import net.sf.cglib.proxy.MethodProxy;

/**
 * CGLIB 代理：基于继承（无需接口），运行时生成子类
 */
public class CglibProxyFactory {

    @SuppressWarnings("unchecked")
    public static <T> T createProxy(Class<T> targetClass) {
        Enhancer enhancer = new Enhancer();
        enhancer.setSuperclass(targetClass);
        enhancer.setCallback((MethodInterceptor) (obj, method, args, proxy) -> {
            System.out.println("[CGLIB 前置] " + method.getName());
            Object result = proxy.invokeSuper(obj, args);
            System.out.println("[CGLIB 后置] " + method.getName());
            return result;
        });
        return (T) enhancer.create();
    }
}

// 使用
UserServiceImpl proxy = CglibProxyFactory.createProxy(UserServiceImpl.class);
proxy.save("王五");
```

### 3.4 代理模式对比

| 代理方式 | 是否需要接口 | 性能 | 典型应用 |
|----------|:------------:|:----:|----------|
| 静态代理 | 需要 | 最高 | 少量且确定的代理逻辑 |
| JDK 动态代理 | **必须**需要接口 | 较高 | Spring AOP（有接口时） |
| CGLIB | 不需要 | 一般 | Spring AOP（无接口时） |

---

## 七、装饰器模式 Decorator

在不改变原对象的情况下，动态地给对象添加职责。

### 7.1 Java I/O 中的装饰器

```java
import java.io.*;

// 标准 Java I/O 就是典型的装饰器模式：
// FileInputStream         -> 节点流（Component 实现）
// BufferedInputStream     -> 缓冲装饰器
// DataInputStream         -> 数据类型装饰器
// GZIPInputStream         -> 压缩装饰器

InputStream is = new GZIPInputStream(           // 压缩解压
                    new DataInputStream(         // 读取基本类型
                        new BufferedInputStream(  // 缓冲
                            new FileInputStream("data.bin")  // 文件输入
                        )));
```

### 7.2 自定义装饰器

```java
/**
 * 组件接口
 */
public interface Coffee {
    String getDescription();
    double cost();
}

/**
 * 具体组件
 */
public class SimpleCoffee implements Coffee {
    @Override public String getDescription() { return "纯咖啡"; }
    @Override public double cost() { return 10.0; }
}

/**
 * 装饰器基类
 */
public abstract class CoffeeDecorator implements Coffee {

    protected final Coffee delegate;

    protected CoffeeDecorator(Coffee delegate) {
        this.delegate = delegate;
    }

    @Override public String getDescription() { return delegate.getDescription(); }
    @Override public double cost() { return delegate.cost(); }
}

/**
 * 加牛奶装饰
 */
public class MilkDecorator extends CoffeeDecorator {

    public MilkDecorator(Coffee delegate) { super(delegate); }

    @Override public String getDescription() {
        return delegate.getDescription() + " + 牛奶";
    }

    @Override public double cost() {
        return delegate.cost() + 3.0;
    }
}

/**
 * 加糖装饰
 */
public class SugarDecorator extends CoffeeDecorator {

    public SugarDecorator(Coffee delegate) { super(delegate); }

    @Override public String getDescription() {
        return delegate.getDescription() + " + 糖";
    }

    @Override public double cost() {
        return delegate.cost() + 1.0;
    }
}

// 使用
Coffee coffee = new SimpleCoffee();
coffee = new MilkDecorator(coffee);
coffee = new SugarDecorator(coffee);

System.out.println(coffee.getDescription());  // 纯咖啡 + 牛奶 + 糖
System.out.println(coffee.cost());             // 14.0
```

### 7.3 装饰器 vs 代理 vs 适配器

| 维度 | 装饰器 | 代理 | 适配器 |
|------|-------|------|-------|
| 意图 | 增加功能 | 控制访问 | 接口转换 |
| 接口 | 与原对象相同 | 与原对象相同 | 与原对象不同 |
| 关系 | 可以层层嵌套 | 通常一对一 | 一对一 |

---

## 十、适配器模式 Adapter

将一个类的接口转换成客户期望的另一个接口。

### 10.1 类适配器（继承）

```java
/**
 * 目标接口（客户端期望的接口）
 */
public interface Target {
    void request();
}

/**
 * 被适配者（已存在的、不兼容的类）
 */
public class Adaptee {
    public void specificRequest() {
        System.out.println("Adaptee 的特殊方法");
    }
}

/**
 * 类适配器：通过继承适配
 */
public class ClassAdapter extends Adaptee implements Target {

    @Override
    public void request() {
        specificRequest();  // 调用父类方法
    }
}

// 使用
Target target = new ClassAdapter();
target.request();  // Adpatee 的特殊方法
```

### 10.2 对象适配器（组合）

```java
/**
 * 对象适配器：通过组合适配（更推荐，符合组合优于继承）
 */
public class ObjectAdapter implements Target {

    private final Adaptee adaptee;

    public ObjectAdapter(Adaptee adaptee) {
        this.adaptee = adaptee;
    }

    @Override
    public void request() {
        adaptee.specificRequest();
    }
}
```

### 10.3 接口适配器（默认实现）

```java
/**
 * 大接口：有 5 个方法
 */
public interface WindowListener {
    void onOpen();
    void onClose();
    void onFocus();
    void onBlur();
    void onResize();
}

/**
 * 默认适配器：让子类只需覆盖关心的方法
 */
public abstract class WindowAdapter implements WindowListener {
    @Override public void onOpen() {}
    @Override public void onClose() {}
    @Override public void onFocus() {}
    @Override public void onBlur() {}
    @Override public void onResize() {}
}

// 使用
WindowListener listener = new WindowAdapter() {
    @Override public void onClose() {
        System.out.println("窗口关闭");
    }
};
```

### 10.4 实际应用举例

| 场景 | 被适配 | 适配器 | 目标接口 |
|------|-------|-------|---------|
| `InputStreamReader` | `InputStream`（字节流） | 字符编码转换 | `Reader`（字符流） |
| Spring `HandlerAdapter` | 各种 `Handler` | 统一调度 | `HandlerAdapter.handle()` |
| JDK `Arrays.asList()` | 数组 | 包装为 List | `List` 接口 |

---

## 相关章节

- [设计模式总览](../README.md)
- [创建型模式](../creation/README.md)
- [行为型模式](../behavioral/README.md)
