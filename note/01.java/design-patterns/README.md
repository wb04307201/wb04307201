# Java 设计模式学习笔记

> GoF 23 种设计模式的 Java 实现与选型指南

---

## 目录

| 编号 | 模式 | 分类 | 核心意图 |
|------|------|------|----------|
| 一 | 单例模式 | 创建型 | 全局唯一实例 |
| 二 | 工厂模式 | 创建型 | 对象创建封装 |
| 三 | 代理模式 | 结构型 | 控制对象访问 |
| 四 | 观察者模式 | 行为型 | 一对多依赖通知 |
| 五 | 策略模式 | 行为型 | 算法可替换 |
| 六 | 模板方法模式 | 行为型 | 骨架固定，细节延迟 |
| 七 | 装饰器模式 | 结构型 | 动态增强职责 |
| 八 | 责任链模式 | 行为型 | 请求逐级传递 |
| 九 | 建造者模式 | 创建型 | 复杂对象分步构建 |
| 十 | 适配器模式 | 结构型 | 接口兼容转换 |

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

## 四、观察者模式 Observer

定义对象间的一对多依赖关系，当被观察者状态改变时，所有依赖者自动收到通知。

### 4.1 Java 内置 Observer / Observable

> 注意：Java 9 起 `java.util.Observer` / `Observable` 已标记为 `@Deprecated`，但理解原理仍然重要。

```java
import java.util.Observable;
import java.util.Observer;

/**
 * 被观察者
 */
public class WeatherData extends Observable {

    private float temperature;

    public void setTemperature(float temperature) {
        this.temperature = temperature;
        setChanged();       // 标记数据已改变
        notifyObservers(temperature);
    }
}

/**
 * 观察者
 */
public class PhoneDisplay implements Observer {

    @Override
    public void update(Observable o, Object arg) {
        System.out.println("手机收到温度更新: " + arg);
    }
}

// 使用
WeatherData data = new WeatherData();
data.addObserver(new PhoneDisplay());
data.setTemperature(36.5f);  // -> 手机收到温度更新: 36.5
```

### 4.2 事件监听器模式（Spring 风格）

```java
import java.util.*;
import java.util.concurrent.*;

/**
 * 事件基类
 */
public abstract class ApplicationEvent {
    private final long timestamp;
    protected ApplicationEvent() { this.timestamp = System.currentTimeMillis(); }
    public long getTimestamp() { return timestamp; }
}

/**
 * 具体事件
 */
public class OrderCreatedEvent extends ApplicationEvent {
    private final String orderId;
    public OrderCreatedEvent(String orderId) { this.orderId = orderId; }
    public String getOrderId() { return orderId; }
}

/**
 * 监听器接口
 */
@FunctionalInterface
public interface ApplicationListener<T extends ApplicationEvent> {
    void onEvent(T event);
}

/**
 * 事件发布器
 */
public class ApplicationEventPublisher {

    private final Map<Class<?>, List<ApplicationListener<?>>> listeners = new ConcurrentHashMap<>();

    public <T extends ApplicationEvent> void addListener(
            Class<T> eventType, ApplicationListener<T> listener) {
        listeners.computeIfAbsent(eventType, k -> new CopyOnWriteArrayList<>()).add(listener);
    }

    @SuppressWarnings("unchecked")
    public <T extends ApplicationEvent> void publish(T event) {
        List<ApplicationListener<?>> list = listeners.get(event.getClass());
        if (list != null) {
            for (ApplicationListener<?> l : list) {
                ((ApplicationListener<T>) l).onEvent(event);
            }
        }
    }
}

// 使用
ApplicationEventPublisher publisher = new ApplicationEventPublisher();
publisher.addListener(OrderCreatedEvent.class,
        e -> System.out.println("发送通知: 订单 " + e.getOrderId() + " 已创建"));
publisher.addListener(OrderCreatedEvent.class,
        e -> System.out.println("扣减库存: 订单 " + e.getOrderId()));

publisher.publish(new OrderCreatedEvent("ORD-001"));
```

### 4.3 Java 9+ PropertyChangeListener 方案

```java
import java.beans.*;

/**
 * 使用 PropertyChangeListener 实现观察者模式
 */
public class User {

    private final PropertyChangeSupport pcs = new PropertyChangeSupport(this);
    private String name;

    public void addPropertyChangeListener(PropertyChangeListener listener) {
        pcs.addPropertyChangeListener(listener);
    }

    public void setName(String name) {
        String old = this.name;
        this.name = name;
        pcs.firePropertyChange("name", old, name);
    }
}

// 使用
User user = new User();
user.addPropertyChangeListener(e ->
    System.out.println(e.getPropertyName() + ": " + e.getOldValue() + " -> " + e.getNewValue()));
user.setName("张三");
```

### 4.4 观察者 vs 发布订阅

| 维度 | 观察者模式 | 发布/订阅模式 |
|------|-----------|--------------|
| 耦合度 | 观察者与被观察者直接关联 | 通过事件总线/消息中间件解耦 |
| 通信方式 | 同步通知 | 通常异步 |
| 典型实现 | Observer/Observable | Spring Event、Kafka、RabbitMQ |

---

## 五、策略模式 Strategy

定义一组算法族，让它们可以互相替换，使算法独立于使用它的客户端。

### 5.1 接口 + 多实现

```java
/**
 * 策略接口
 */
public interface DiscountStrategy {
    double calculate(double originalPrice);
}

/**
 * 无折扣
 */
public class NoDiscount implements DiscountStrategy {
    @Override public double calculate(double price) { return price; }
}

/**
 * 满减
 */
public class FullReductionDiscount implements DiscountStrategy {
    private final double threshold;
    private final double reduction;

    public FullReductionDiscount(double threshold, double reduction) {
        this.threshold = threshold;
        this.reduction = reduction;
    }

    @Override
    public double calculate(double price) {
        return price >= threshold ? price - reduction : price;
    }
}

/**
 * 百分比折扣
 */
public class PercentDiscount implements DiscountStrategy {
    private final double percent;

    public PercentDiscount(double percent) {
        this.percent = percent;
    }

    @Override
    public double calculate(double price) {
        return price * (1 - percent / 100);
    }
}

/**
 * 上下文：持有策略引用
 */
public class PriceCalculator {

    private DiscountStrategy strategy;

    public void setStrategy(DiscountStrategy strategy) {
        this.strategy = strategy;
    }

    public double calculate(double price) {
        return strategy.calculate(price);
    }
}

// 使用
PriceCalculator calculator = new PriceCalculator();

calculator.setStrategy(new NoDiscount());
System.out.println("无折扣: " + calculator.calculate(200));     // 200.0

calculator.setStrategy(new PercentDiscount(20));
System.out.println("8折: " + calculator.calculate(200));        // 160.0

calculator.setStrategy(new FullReductionDiscount(100, 30));
System.out.println("满100减30: " + calculator.calculate(200));   // 170.0
```

### 5.2 结合枚举实现策略（消除 if-else）

```java
import java.util.function.DoubleUnaryOperator;

/**
 * 枚举策略：利用函数式接口 + 枚举消除条件分支
 */
public enum DiscountType {

    NONE(p -> p),
    VIP_80(p -> p * 0.8),
    VIP_90(p -> p * 0.9),
    FULL_REDUCTION_200_50(p -> p >= 200 ? p - 50 : p);

    private final DoubleUnaryOperator calculator;

    DiscountType(DoubleUnaryOperator calculator) {
        this.calculator = calculator;
    }

    public double calculate(double price) {
        return calculator.applyAsDouble(price);
    }
}

// 使用
System.out.println(DiscountType.VIP_80.calculate(500));  // 400.0
```

### 5.3 策略 vs 状态模式

| 维度 | 策略模式 | 状态模式 |
|------|---------|---------|
| 意图 | 算法可替换 | 状态驱动行为变化 |
| 谁来切换 | 客户端主动选择 | 对象内部根据条件自动切换 |
| 例子 | 不同支付方式 | 订单状态（待付款->已付款->已发货） |

---

## 六、模板方法模式 Template Method

在抽象类中定义算法骨架，将某些步骤延迟到子类实现。

### 6.1 抽象类定义骨架

```java
/**
 * 抽象模板：定义业务流程骨架
 */
public abstract class AbstractOrderProcessor {

    /**
     * 模板方法：final 防止子类重写整个流程
     */
    public final void process(String orderId) {
        validateOrder(orderId);
        deductInventory(orderId);
        createPayment(orderId);
        sendNotification(orderId);
        updateStatus(orderId);
    }

    // 公共步骤（父类实现）
    protected void validateOrder(String orderId) {
        System.out.println("校验订单: " + orderId);
    }

    protected void deductInventory(String orderId) {
        System.out.println("扣减库存: " + orderId);
    }

    protected void updateStatus(String orderId) {
        System.out.println("更新订单状态: " + orderId);
    }

    // 抽象步骤（子类必须实现）
    protected abstract void createPayment(String orderId);

    // 钩子方法（子类可选覆盖）
    protected void sendNotification(String orderId) {
        // 默认不发送通知
    }
}

/**
 * 实物订单实现
 */
public class PhysicalOrderProcessor extends AbstractOrderProcessor {

    @Override
    protected void createPayment(String orderId) {
        System.out.println("实物订单 - 创建微信支付: " + orderId);
    }

    @Override
    protected void sendNotification(String orderId) {
        System.out.println("发送短信通知: " + orderId);
    }
}

/**
 * 虚拟订单实现
 */
public class VirtualOrderProcessor extends AbstractOrderProcessor {

    @Override
    protected void createPayment(String orderId) {
        System.out.println("虚拟订单 - 创建支付宝: " + orderId);
    }

    // 不重写 sendNotification，使用默认空实现
}

// 使用
AbstractOrderProcessor processor = new PhysicalOrderProcessor();
processor.process("ORD-20240101");
```

### 6.2 钩子方法控制流程

```java
public abstract class AbstractReportGenerator {

    public final void generate() {
        collectData();
        if (needFilter()) {           // 钩子方法控制是否过滤
            filterData();
        }
        formatReport();
        outputReport();
    }

    protected abstract void collectData();
    protected abstract void formatReport();
    protected abstract void outputReport();

    // 钩子方法：默认返回 false
    protected boolean needFilter() { return false; }
    protected void filterData() {}
}

public class FilteredReportGenerator extends AbstractReportGenerator {

    @Override protected void collectData() { System.out.println("收集数据"); }
    @Override protected void formatReport() { System.out.println("格式化报表"); }
    @Override protected void outputReport() { System.out.println("输出报表"); }
    @Override protected boolean needFilter() { return true; }  // 启用过滤
    @Override protected void filterData() { System.out.println("过滤脏数据"); }
}
```

### 6.3 模板方法 vs 策略模式

| 维度 | 模板方法 | 策略模式 |
|------|---------|---------|
| 实现方式 | 继承（抽象类） | 组合（接口 + 实现类） |
| 代码复用 | 骨架方法在父类复用 | 策略类各自独立 |
| 推荐场景 | 流程固定，部分步骤可变 | 算法完全可替换 |

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

## 八、责任链模式 Chain of Responsibility

使多个对象都有机会处理请求，从而避免请求发送者与接收者耦合。

### 8.1 Servlet Filter 实现

```java
import javax.servlet.*;
import java.io.IOException;

/**
 * 编码过滤器
 */
public class EncodingFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {
        request.setCharacterEncoding("UTF-8");
        response.setCharacterEncoding("UTF-8");
        System.out.println("EncodingFilter: 执行前");
        chain.doFilter(request, response);  // 放行
        System.out.println("EncodingFilter: 执行后");
    }
}

/**
 * 认证过滤器
 */
public class AuthFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {
        String token = request.getParameter("token");
        if (token == null || token.isEmpty()) {
            throw new SecurityException("未认证");
        }
        System.out.println("AuthFilter: 执行前");
        chain.doFilter(request, response);
        System.out.println("AuthFilter: 执行后");
    }
}
```

> Servlet 容器按 `<filter-mapping>` 顺序串联 FilterChain。

### 8.2 Spring Interceptor 实现

```java
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.ModelAndView;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

/**
 * 日志拦截器
 */
public class LogInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) throws Exception {
        System.out.println("请求开始: " + request.getRequestURI());
        return true;  // true = 继续执行，false = 拦截
    }

    @Override
    public void postHandle(HttpServletRequest request,
                           HttpServletResponse response,
                           Object handler,
                           ModelAndView modelAndView) throws Exception {
        System.out.println("Controller 执行完成");
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
                                HttpServletResponse response,
                                Object handler,
                                Exception ex) throws Exception {
        System.out.println("请求结束");
    }
}

// 注册
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new LogInterceptor())
                .addPathPatterns("/**")
                .excludePathPatterns("/health");
    }
}
```

### 8.3 自定义责任链

```java
/**
 * 处理抽象类
 */
public abstract class ApprovalHandler {

    protected ApprovalHandler next;

    public void setNext(ApprovalHandler next) {
        this.next = next;
    }

    public abstract void handleRequest(double amount);
}

/**
 * 组长：审批 <= 5000
 */
public class TeamLeaderHandler extends ApprovalHandler {
    @Override
    public void handleRequest(double amount) {
        if (amount <= 5000) {
            System.out.println("组长审批通过: " + amount);
        } else {
            if (next != null) next.handleRequest(amount);
            else System.out.println("无人可审批: " + amount);
        }
    }
}

/**
 * 部门经理：审批 <= 20000
 */
public class ManagerHandler extends ApprovalHandler {
    @Override
    public void handleRequest(double amount) {
        if (amount <= 20000) {
            System.out.println("经理审批通过: " + amount);
        } else {
            if (next != null) next.handleRequest(amount);
            else System.out.println("无人可审批: " + amount);
        }
    }
}

/**
 * CEO：审批任意金额
 */
public class CEOHandler extends ApprovalHandler {
    @Override
    public void handleRequest(double amount) {
        System.out.println("CEO审批通过: " + amount);
    }
}

// 使用
ApprovalHandler teamLeader = new TeamLeaderHandler();
ApprovalHandler manager = new ManagerHandler();
ApprovalHandler ceo = new CEOHandler();

teamLeader.setNext(manager);
manager.setNext(ceo);

teamLeader.handleRequest(3000);   // 组长审批通过
teamLeader.handleRequest(15000);  // 经理审批通过
teamLeader.handleRequest(50000);  // CEO审批通过
```

### 8.4 责任链对比

| 实现 | 优点 | 缺点 | 典型场景 |
|------|------|------|---------|
| Servlet Filter | 容器管理，配置灵活 | 耦合 Servlet API | Web 请求预处理 |
| Spring Interceptor | 与 Spring 生态集成 | 仅作用于 Spring MVC | 鉴权、日志、审计 |
| 自定义责任链 | 完全灵活 | 需手动组装链 | 审批流、规则引擎 |

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

## 十一、模式选型指南

### 11.1 创建型模式选型

| 需求 | 推荐模式 | 理由 |
|------|---------|------|
| 全局唯一实例 | 单例 | 限制实例个数 |
| 创建过程复杂，参数多 | 建造者 | 链式调用，可读性好 |
| 需要统一创建入口 | 简单工厂 | 集中管理 |
| 产品种类会不断扩展 | 工厂方法 | 符合开闭原则 |
| 创建一组相关产品 | 抽象工厂 | 产品族一致性 |
| 对象构造分步骤，不同顺序产生不同结果 | 建造者 | 步骤灵活 |

### 11.2 结构型模式选型

| 需求 | 推荐模式 | 理由 |
|------|---------|------|
| 动态添加职责 | 装饰器 | 灵活组合，替代继承 |
| 控制对象访问 | 代理 | 远程、延迟、安全等场景 |
| 接口不兼容 | 适配器 | 桥接新旧系统 |
| 简化复杂子系统接口 | 外观（Facade） | 对外提供统一入口 |
| 请求需要多个对象依次处理 | 责任链 | 解耦发送者与接收者 |
| 需要将抽象与实现分离 | 桥接 | 多维度独立变化 |

### 11.3 行为型模式选型

| 需求 | 推荐模式 | 理由 |
|------|---------|------|
| 算法需要动态切换 | 策略 | 消除 if-else/switch |
| 流程固定，部分步骤可变 | 模板方法 | 骨架复用 |
| 一对多依赖通知 | 观察者 | 事件驱动 |
| 对象状态改变时行为改变 | 状态 | 消除状态条件分支 |
| 解耦请求发送者与接收者 | 命令 | 支持撤销/重做 |
| 遍历聚合对象而不暴露内部结构 | 迭代器 | 统一遍历方式 |
| 多个对象协作完成请求，但职责不明确 | 中介者 | 集中管理交互逻辑 |

### 11.4 Spring 框架中的设计模式速查

| 模式 | Spring 中的应用 |
|------|----------------|
| 单例 | Bean 默认 scope=singleton |
| 工厂方法 | `BeanFactory`, `FactoryBean` |
| 代理 | AOP（JDK / CGLIB） |
| 观察者 | `ApplicationEvent` / `@EventListener` |
| 策略 | `Resource` 接口、`HandlerMapping` |
| 模板方法 | `JdbcTemplate`, `RestTemplate` |
| 装饰器 | `HttpSession` 包装、`ServletRequest` 包装 |
| 责任链 | `FilterChain`, `HandlerInterceptor` 链 |
| 适配器 | `HandlerAdapter` |
| 建造者 | `UriComponentsBuilder`, `ResponseEntity.BodyBuilder` |
| 代理 | Spring AOP 动态代理 |
| 观察者 | `ApplicationEventPublisher` |
| 策略 | `TaskScheduler` 不同实现 |

### 11.5 设计原则总结

| 原则 | 英文 | 说明 |
|------|------|------|
| 单一职责 | SRP | 一个类只做一件事 |
| 开闭原则 | OCP | 对扩展开放，对修改封闭 |
| 里氏替换 | LSP | 子类可替换父类而不影响程序 |
| 依赖倒置 | DIP | 依赖抽象，不依赖具体 |
| 接口隔离 | ISP | 接口尽量小而专 |
| 迪米特法则 | LoD | 只与直接朋友通信 |
| 组合优于继承 | Favor Composition | 降低耦合，增强灵活 |

> 设计模式是解决特定问题的经验总结，不是银弹。
> 在实际开发中，应先识别问题，再选择模式，而非生搬硬套。
