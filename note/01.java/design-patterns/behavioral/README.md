<!--
module:
  parent: java
  slug: java/behavioral-patterns
  type: article
  category: 主模块子文章
  summary: 行为型模式
-->

# 行为型模式

> 关注对象之间的职责分配与通信方式，让对象间的交互更加灵活和可维护。

---
## 引言：架构困境

行为型模式 的关键不是'选型'——是**选完之后怎么在 5 个 trade-off 里活下来**。

本篇用'决策困境'切入，比较几种主流路径并讲清取舍。

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

## 相关章节

- [设计模式总览](../README.md)
- [创建型模式](../creation/README.md)
- [结构型模式](../structural/README.md)

← [返回: Java 知识体系 · behavioral](../README.md)
