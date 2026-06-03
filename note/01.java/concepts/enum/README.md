# 枚举（Enum）

枚举用于定义一组固定的常量，每个常量都是枚举类型的一个实例。Java 枚举在 Java 5 引入，本质上是继承 `java.lang.Enum` 的类（默认 `final`，但当枚举常量包含各自的类体实现时，编译器会生成非 `final` 的抽象类，每个常量对应一个匿名子类）。

## 基本用法

```java
public enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}

// 使用
Day today = Day.MONDAY;
System.out.println(today);           // MONDAY
System.out.println(today.ordinal()); // 0（序号）
System.out.println(today.name());    // "MONDAY"
```

## 带属性的枚举

枚举常量可以携带自定义属性：

```java
public enum Season {
    SPRING("春天", 1),
    SUMMER("夏天", 2),
    AUTUMN("秋天", 3),
    WINTER("冬天", 4);

    private final String chineseName;
    private final int order;

    Season(String chineseName, int order) {
        this.chineseName = chineseName;
        this.order = order;
    }

    public String getChineseName() { return chineseName; }
    public int getOrder() { return order; }
}

System.out.println(Season.SPRING.getChineseName()); // 春天
```

## 带方法的枚举

枚举可以定义方法，甚至每个常量可以有不同的方法实现：

```java
public enum Operation {
    ADD("+") {
        @Override
        public double apply(double a, double b) { return a + b; }
    },
    SUBTRACT("-") {
        @Override
        public double apply(double a, double b) { return a - b; }
    },
    MULTIPLY("*") {
        @Override
        public double apply(double a, double b) { return a * b; }
    },
    DIVIDE("/") {
        @Override
        public double apply(double a, double b) {
            if (b == 0) throw new ArithmeticException("除数不能为零");
            return a / b;
        }
    };

    private final String symbol;

    Operation(String symbol) { this.symbol = symbol; }

    public String getSymbol() { return symbol; }

    // 抽象方法 - 每个常量必须实现
    public abstract double apply(double a, double b);
}

System.out.println(Operation.ADD.apply(3, 4));     // 7.0
System.out.println(Operation.MULTIPLY.apply(3, 4)); // 12.0
```

## 枚举与 switch

枚举天然支持`switch`语句：

```java
Day day = Day.MONDAY;
switch (day) {
    case MONDAY:
    case TUESDAY:
    case WEDNESDAY:
    case THURSDAY:
    case FRIDAY:
        System.out.println("工作日");
        break;
    case SATURDAY:
    case SUNDAY:
        System.out.println("周末");
        break;
}

// Java 14+ Switch 表达式
String type = switch (day) {
    case MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY -> "工作日";
    case SATURDAY, SUNDAY -> "周末";
};
```

## 枚举的常用方法

| 方法 | 说明 |
|------|------|
| `name()` | 返回枚举常量的名称 |
| `ordinal()` | 返回枚举常量的序号（从 0 开始） |
| `values()` | 返回所有枚举常量的数组 |
| `valueOf(String name)` | 根据名称返回枚举常量（名称不匹配时抛出 IllegalArgumentException，参数为 null 时抛出 NullPointerException） |
| `compareTo(E other)` | 比较两个枚举常量的序号 |
| `toString()` | 返回枚举常量的名称（可重写） |

```java
// 遍历所有枚举常量
for (Day day : Day.values()) {
    System.out.println(day.ordinal() + ": " + day.name());
}

// 根据名称获取
Day day = Day.valueOf("MONDAY");
```

## `EnumSet` 和 `EnumMap`

### EnumSet

专门为枚举设计的 `Set` 实现，内部使用位向量存储，性能极高（需要 `import java.util.EnumSet;`）：

```java
// 创建包含指定元素的 EnumSet
EnumSet<Day> workDays = EnumSet.of(Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY,
                                     Day.THURSDAY, Day.FRIDAY);

// 创建包含所有元素的 EnumSet
EnumSet<Day> allDays = EnumSet.allOf(Day.class);

// 创建空的 EnumSet
EnumSet<Day> noDays = EnumSet.noneOf(Day.class);

// 创建范围 EnumSet
EnumSet<Day> range = EnumSet.range(Day.MONDAY, Day.FRIDAY);

// 创建补集
EnumSet<Day> weekend = EnumSet.complementOf(workDays);
```

### EnumMap

专门为枚举设计的 `Map` 实现，内部使用数组存储，性能优于 `HashMap`（需要 `import java.util.EnumMap;`）：

```java
EnumMap<Day, String> schedule = new EnumMap<>(Day.class);
schedule.put(Day.MONDAY, "开会");
schedule.put(Day.FRIDAY, "代码评审");
schedule.put(Day.SUNDAY, "休息");
```

## 枚举单例模式

枚举实现单例是《Effective Java》推荐的方式：

```java
public enum Singleton {
    INSTANCE;

    private final String config;

    Singleton() {
        // 初始化逻辑
        config = "default";
    }

    public String getConfig() { return config; }
}

// 使用
System.out.println(Singleton.INSTANCE.getConfig());
```

**优势**：
- **实例创建线程安全**：JVM 保证枚举实例只被创建一次（注意：若实例包含可变状态，仍需额外同步措施）
- **防止反射攻击**：`Constructor.newInstance()` 对枚举类型做了特殊检查，会拒绝创建枚举实例并抛出异常
- **防止序列化破坏**：枚举天然支持序列化，不会通过反序列化创建新实例
- **代码简洁**：只需几行代码

## 枚举实现接口

枚举可以实现接口，每个常量可以提供各自的实现，从而支持多态调用：

```java
public interface Describable {
    String describe();
}

public enum Color implements Describable {
    RED {
        @Override
        public String describe() { return "红色"; }
    },
    GREEN {
        @Override
        public String describe() { return "绿色"; }
    },
    BLUE {
        @Override
        public String describe() { return "蓝色"; }
    }
}

// 多态调用
Describable c = Color.RED;
System.out.println(c.describe()); // 红色

for (Color color : Color.values()) {
    System.out.println(color.name() + ": " + color.describe());
}
```

## 枚举的特性总结

| 特性 | 说明 |
|------|------|
| **本质** | 继承 `java.lang.Enum` 的类（通常 `final`，含常量级别类体时非 `final`） |
| **构造方法** | 只能是 `private`（默认就是 `private`） |
| **继承** | 不能继承其他类（已隐式继承`Enum`），但可以实现接口 |
| **实例** | 枚举常量都是`public static final`的实例 |
| **比较** | 可以用`==`比较（因为每个常量只有一个实例） |
| **switch** | 天然支持`switch`语句 |
| **序列化** | 天然支持序列化 |
| **抽象方法** | 枚举可以声明抽象方法，每个枚举常量必须提供各自的实现 |

## 枚举 vs 常量类

```java
// 常量类方式 - 不推荐
public class Days {
    public static final int MONDAY = 0;
    public static final int TUESDAY = 1;
    // 问题：类型不安全，值可以随意传入
}

// 枚举方式 - 推荐
public enum Day {
    MONDAY, TUESDAY
    // 优势：类型安全、有命名空间、可以携带属性和方法
}
```
