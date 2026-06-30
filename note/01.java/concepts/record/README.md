# 记录类（Record）

## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

记录类（Record） 本应该很简单，Record 是 Java 14 引入的预览特性（Java 16 正式发布），用于声明**不可变数据载体**的简洁语法。编译器会自动生成构造方法、getter、`equals()`、`hashCode()`、`toString()`等方法

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---


Record 是 Java 14 引入的预览特性（Java 16 正式发布），用于声明**不可变数据载体**的简洁语法。编译器会自动生成构造方法、getter、`equals()`、`hashCode()`、`toString()`等方法。

## 基本用法

```java
// 传统写法需要几十行
public class Point {
    private final int x;
    private final int y;
    public Point(int x, int y) { this.x = x; this.y = y; }
    public int getX() { return x; }
    public int getY() { return y; }
    @Override public boolean equals(Object o) { /* ... */ }
    @Override public int hashCode() { /* ... */ }
    @Override public String toString() { /* ... */ }
}

// Record 一行搞定
public record Point(int x, int y) { }

// 使用
Point p = new Point(3, 4);
System.out.println(p.x());         // 3（注意：getter 不带 get 前缀）
System.out.println(p.y());         // 4
System.out.println(p);             // Point[x=3, y=4]
```

## Local Record（局部 Record）

Java 16+ 允许在方法内部声明局部 Record，适用于临时数据投影、中间结果封装等场景，避免为一次性用途创建顶层类。

```java
public List<UserProjection> getActiveUsers() {
    // 局部 Record —— 仅在方法内可见
    record UserProjection(String name, String email) { }

    return userRepository.findAll().stream()
        .filter(User::isActive)
        .map(u -> new UserProjection(u.getName(), u.getEmail()))
        .toList();
}

// 配合 Stream 做数据聚合也很方便
public Map<String, Double> averageScoreByClass() {
    record ClassScore(String className, double score) { }

    return scores.stream()
        .map(s -> new ClassScore(s.getClassName(), s.getScore()))
        .collect(Collectors.groupingBy(
            ClassScore::className,
            Collectors.averagingDouble(ClassScore::score)
        ));
}
```

## Record 自动生成的内容

编译器为`record`自动生成：

| 自动生成内容 | 说明 |
|------------|------|
| `private final` 字段 | 每个组件对应一个不可变字段 |
| 全参构造方法 | 参数顺序与组件声明顺序一致 |
| 访问方法（accessor） | `x()`、`y()`（**不是**`getX()`、`getY()`） |
| `equals()` | 基于所有组件值比较 |
| `hashCode()` | 基于所有组件值计算 |
| `toString()` | 格式：`RecordName[field1=value1, field2=value2]` |

## 重写访问方法（Accessor Override）

Record 自动生成的 accessor 直接返回字段值，但你可以重写它来添加**防御性拷贝**、**数据格式化**或**校验逻辑**：

```java
public record Event(String name, LocalDate date, List<String> attendees) {

    // 重写 accessor —— 返回防御性拷贝，防止外部修改内部不可变列表
    @Override
    public List<String> attendees() {
        return List.copyOf(attendees);
    }

    // 重写 accessor —— 数据格式化
    @Override
    public String name() {
        return name == null ? "" : name.strip();
    }

    // 重写 accessor —— 派生计算
    @Override
    public LocalDate date() {
        // 例如：将存储的 epoch day 还原为 LocalDate（仅作示意）
        return date != null ? date : LocalDate.now();
    }
}
```

> **注意**：重写 accessor 时要确保不破坏 Record 的"等价契约"——即 `equals()` 和 `hashCode()` 仍基于原始字段值计算，而非 accessor 返回值。因此重写 accessor 通常只做防御性拷贝或格式化，不要改变逻辑语义。

## Compact Constructor（紧凑构造方法）

可以在 record 中自定义构造方法进行校验或转换，使用紧凑构造方法（省略参数列表）：

```java
public record Person(String name, int age) {
    // 紧凑构造方法 - 省略参数列表，直接使用字段名
    public Person {
        // 参数校验
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name 不能为空");
        }
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("age 不合法: " + age);
        }
        // 数据规范化（不需要 return，直接赋值给参数）
        name = name.trim();
    }
}

// 使用
Person p = new Person("  张三  ", 25);
System.out.println(p.name());  // 张三（已被 trim）

// new Person("", 25);         // 抛出 IllegalArgumentException
// new Person("张三", -1);      // 抛出 IllegalArgumentException
```

### 紧凑构造方法 vs 规范构造方法

```java
// 紧凑构造方法（推荐）- 省略参数列表和赋值
public record Point(int x, int y) {
    public Point {
        if (x < 0) throw new IllegalArgumentException("x 不能为负");
    }
}

// 规范构造方法 - 完整参数列表，需要手动赋值
public record Point(int x, int y) {
    public Point(int x, int y) {
        if (x < 0) throw new IllegalArgumentException("x 不能为负");
        this.x = x;
        this.y = y;
    }
}
```

## 添加额外方法和静态成员

```java
public record Point(int x, int y) {
    // 静态常量
    public static final Point ORIGIN = new Point(0, 0);

    // 静态方法
    public static Point of(int x, int y) {
        return new Point(x, y);
    }

    // 实例方法
    public double distanceTo(Point other) {
        int dx = this.x - other.x;
        int dy = this.y - other.y;
        return Math.sqrt((long) dx * dx + (long) dy * dy);
    }

    public double distanceFromOrigin() {
        return distanceTo(ORIGIN);
    }
}

// 使用
Point p = Point.of(3, 4);
System.out.println(p.distanceFromOrigin());  // 5.0
```

## Record 的约束

| 约束 | 说明 |
|------|------|
| **不可变性** | 组件字段是`private final`的，不能添加非`final`的实例字段 |
| **不能继承** | 隐式继承`java.lang.Record`，不能继承其他类 |
| **不可被继承** | Record 类隐式为 final，不能被其他类继承 |
| **可以实现接口** | 可以实现一个或多个接口 |
| **可以定义静态字段** | 允许`static`字段和方法 |
| **不能定义实例字段** | 不能添加组件列表之外的实例字段 |

```java
// 实现接口
public record UserDTO(String name, String email) implements Serializable {
    private static final long serialVersionUID = 1L;
}
```

## Record 与 JPA/Hibernate

Record 的不可变性使其天然适合做**DTO**（数据传输对象），但不适合直接用作 JPA 实体（JPA 需要可变对象和默认构造方法）。

```java
// 适合做 DTO
public record UserDTO(Long id, String name, String email) {
    // 从 Entity 转换
    public static UserDTO from(User user) {
        return new UserDTO(user.getId(), user.getName(), user.getEmail());
    }
}

// 不适合做 Entity - JPA 需要无参构造和 setter
// public record UserEntity(Long id, String name) { }  // 不行！
```

## Record vs Lombok @Data / @Value

| 对比维度 | Record | Lombok @Data | Lombok @Value |
|---------|--------|-------------|--------------|
| **依赖** | JDK 原生，无需额外依赖 | 需要 Lombok 库 | 需要 Lombok 库 |
| **可变性** | 不可变 | 可变（生成setter） | 不可变 |
| **继承** | 不可被继承（隐式 final） | 可以继承（但 equals/hashCode 需注意 callSuper） | 不能继承（final类） |
| **getter 命名** | `name()` | `getName()` | `getName()` |
| **构造方法** | 只有全参构造 | @RequiredArgsConstructor（为 final/@NonNull 字段生成带参构造） | 只有全参构造 |
| **IDE 支持** | Java 16+ 完善支持 | 需要 Lombok 插件 | 需要 Lombok 插件 |
| **适用场景** | 简单不可变数据载体 | 传统 POJO、Entity | 不可变数据载体 |

## Record 配合 Pattern Matching（Java 16+）

```java
// instanceof Pattern Matching
Object obj = new Point(3, 4);
if (obj instanceof Point p) {
    System.out.println(p.x() + p.y());  // 直接使用
}

// Switch Pattern Matching（Java 21+）
String describe(Object obj) {
    return switch (obj) {
        case Point p -> "Point at (" + p.x() + ", " + p.y() + ")";
        case String s -> "String: " + s;
        case null -> "null";
        default -> "Unknown: " + obj;
    };
}
```

## Record 模式解构（Record Patterns）

Java 21+ 支持 Record 的模式匹配解构：

```java
record Point(int x, int y) { }
record Line(Point start, Point end) { }

// 嵌套解构
Line line = new Line(new Point(0, 0), new Point(3, 4));

if (line instanceof Line(Point(var x1, var y1), Point(var x2, var y2))) {
    double length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    System.out.println("Line length: " + length);  // 5.0
}
```
