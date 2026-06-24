# Record可以使用泛型么？深度解析Java Record与泛型的结合

## 引子：Java 16 的新语法

```java
// 以前写一个不可变数据类，需要大量模板代码
public class User {
    private final String name;
    private final int age;
    
    public User(String name, int age) { this.name = name; this.age = age; }
    public String getName() { return name; }
    public int getAge() { return age; }
    // 还有 equals、hashCode、toString...
}

// Java 16+：一行搞定
public record User(String name, int age) {}

// 还能用泛型！
public record Result<T>(int code, String message, T data) {}
Result<User> result = new Result<>(200, "ok", new User("张三", 25));
```

Record 是什么？它和普通类有什么区别？能用泛型吗？

---

> 📚 **前置知识**：[Record](../../../01.java/concepts/record/README.md) | [泛型](../../../01.java/concepts/generics/README.md)

## 一、核心原理

Java 16引入的`record`专为不可变数据载体设计，天然支持泛型且语法简洁。

**Record特征：**

| **特性** | **说明** | **与普通类对比** |
|---------|---------|-----------------|
| **不可变性** | 字段隐式`final` | 普通类可变 |
| **构造函数** | 自动生成 | 需手动编写 |
| **访问器** | `fieldName()` | getter/setter |
| **equals/hashCode** | 自动生成 | 需手动/Lombok |
| **继承** | 隐式继承`java.lang.Record` | 可继承任意类 |
| **泛型** | ✅ 完全支持 | ✅ 同样支持 |

**核心价值：**类型安全DTO、代码简洁、模式匹配友好、函数式编程支持

**泛型擦除：**
```java
public record Box<T>(T value) {}
// 编译后T被擦除为Object
public final class Box extends java.lang.Record {
    private final Object value;
    public Box(Object v) { this.value = v; }
    public Object value() { return value; }
}
```

**Record vs 传统类：**
```java
// Record（1行）
public record Result<T>(boolean success, T data, String error) {}
// 等价传统类（约50行）：构造函数+getter+equals+hashCode+toString
```

## 二、代码示例

**1. 基础泛型Record**

```java
public record Container<T>(T value) {
    public static <T> Container<T> of(T v) { return new Container<>(v); }
    public <R> Container<R> map(Function<T,R> f) { return new Container<>(f.apply(value)); }
}
Container<String> sc = Container.of("hello");
Container<Integer> ic = sc.map(String::length);  // 5
```

**2. 多泛型参数**

```java
public record Entry<K,V>(K key, V value) {}
Entry<String,Integer> e = Entry.of("age", 30);
List<Entry<String,Integer>> entries = List.of(Entry.of("Alice",25), Entry.of("Bob",30));
Map<String,Integer> map = entries.stream().collect(Collectors.toMap(Entry::key, Entry::value));
```

**3. 带泛型约束**

```java
public record Range<T extends Comparable<T>>(T min, T max) {
    public Range { if (min.compareTo(max) > 0) throw new IllegalArgumentException("min > max"); }
    public boolean contains(T v) { return v.compareTo(min) >= 0 && v.compareTo(max) <= 0; }
}
Range<Integer> r = new Range<>(0, 100);
r.contains(50);  // true
```

**4. 嵌套泛型**

```java
public record ApiResponse<T>(int code, String msg, Optional<T> data) {
    public static <T> ApiResponse<T> success(T d) { return new ApiResponse<>(200, "OK", Optional.ofNullable(d)); }
    public static <T> ApiResponse<T> error(int c, String m) { return new ApiResponse<>(c, m, Optional.empty()); }
    public <R> ApiResponse<R> mapData(Function<T,R> f) { return new ApiResponse<>(code, msg, data.map(f)); }
}
public record PageResult<T>(List<T> items, long total, int page, int size) {}

// 组合
ApiResponse<PageResult<User>> resp = ApiResponse.success(new PageResult<>(users, 100, 1, 10));
```

**5. Sealed Interface + Record（ADT）**

```java
public sealed interface Result<T> permits Success, Failure { T getOrNull(); }
public record Success<T>(T value) implements Result<T> { public T getOrNull() { return value; } }
public record Failure<T>(Exception error) implements Result<T> { public T getOrNull() { return null; } }

// 模式匹配
String process(Result<T> r) {
    return switch (r) {
        case Success<T> s -> "Success: " + s.value();
        case Failure<T> f -> "Failure: " + f.error().getMessage();
    };
}
```

**6. Spring Boot应用**

```java
public record ServiceResult<T>(boolean success, T data, String errorCode) {
    public static <T> ServiceResult<T> ok(T d) { return new ServiceResult<>(true, d, null); }
    public static <T> ServiceResult<T> fail(String c) { return new ServiceResult<>(false, null, c); }
}
public record UserDTO(Long id, String username, String email) {}

@Service
public class UserService {
    public ServiceResult<UserDTO> getUser(Long id) {
        try {
            User u = userRepository.findById(id).orElseThrow();
            return ServiceResult.ok(new UserDTO(u.getId(), u.getUsername(), u.getEmail()));
        } catch (NotFoundException e) { return ServiceResult.fail("USER_NOT_FOUND"); }
    }
}

@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping("/{id}")
    public ResponseEntity<ServiceResult<UserDTO>> get(@PathVariable Long id) {
        ServiceResult<UserDTO> r = userService.getUser(id);
        return ResponseEntity.status(r.success() ? HttpStatus.OK : HttpStatus.NOT_FOUND).body(r);
    }
}
```

## 三、常见陷阱

**陷阱1：误以为Record字段可变**
```java
// ❌ 编译错误：record字段是final
a.value = "world";  // Cannot assign to final variable
// ✅ 创建新实例
updated = new MutableAttempt<>("world");
// 集合防御性拷贝
public record Safe(List<String> items) { public Safe(List<String> i) { this.items = List.copyOf(i); } }
```

**陷阱2：泛型数组创建错误**
```java
// ❌ Cannot create generic array of T
// private T[] arr = new T[10];
// ✅ 用List代替
public record Better<T>(List<T> items) {}
```

**陷阱3：重写equals破坏契约**
```java
// ❌ 只比较部分字段，但hashCode基于全部 → 不一致
public record Point(int x, int y) {
    @Override public boolean equals(Object o) { return o instanceof Point p && x == p.x; }
    // hashCode仍基于x和y！
}
// ✅ 如必须自定义，同时重写hashCode
@Override public int hashCode() { return Objects.hash(x, y); }
```

**陷阱4：忽略泛型擦除**
```java
// ❌ 运行时无法区分泛型类型（都被擦除为Object）
// ✅ 传递Class对象
public record TypedPair<T,U>(T first, Class<T> firstType) {
    public boolean isFirstOfType(Class<?> c) { return firstType.isAssignableFrom(c); }
}
```

**陷阱5：Mock问题**
```java
// ❌ 某些Mockito版本无法mock record（final类）
// ✅ 使用真实record实例（推荐，因为record本就是数据载体）
UserDTO real = new UserDTO(1L, "test", "test@example.com");
when(service.getUser(1L)).thenReturn(ServiceResult.ok(real));
```

## 四、最佳实践

**1. 选型决策**
```
需要创建类？
├── 需要可变状态？→ 普通class
├── 需要继承其他类？→ 普通class
├── 数据载体（DTO/VO）？→ ✅ record
└── 需要泛型？→ ✅ Record完全支持
```

**2. 防御性拷贝**
```java
public record Order(String id, List<OrderItem> items, Map<String,String> meta) {
    public Order { items = List.copyOf(items); meta = Map.copyOf(meta); }  // 不可变副本
}
```

**3. Builder模式**
```java
public record CreateUserRequest(String username, String email, int age) {
    public static class Builder {
        private String username, email; private int age;
        public Builder username(String u) { username=u; return this; }
        public Builder email(String e) { email=e; return this; }
        public Builder age(int a) { age=a; return this; }
        public CreateUserRequest build() { return new CreateUserRequest(username, email, age); }
    }
}
CreateUserRequest req = new CreateUserRequest.Builder().username("alice").email("alice@example.com").age(25).build();
```

**4. Jackson序列化**
```java
// Jackson 2.12+原生支持record
public record Product(Long id, String name, BigDecimal price) implements Serializable {}
ObjectMapper mapper = new ObjectMapper();
Product p = new Product(1L, "iPhone", new BigDecimal("999"));
String json = mapper.writeValueAsString(p);  // {"id":1,"name":"iPhone","price":999}
```

## 五、面试话术

**面试官：Java Record可以使用泛型吗？**

回答要点：
1. **可以**，语法与普通泛型类一致
2. **示例**：`public record Result<T>(boolean success, T data, String error) {}`
3. **价值**：极简语法实现类型安全不可变DTO
4. **泛型擦除**：和普通类一样，运行时类型信息被擦除
5. **应用场景**：API响应封装、函数式Monad、领域事件

**面试官：Record和普通类的区别？**

回答要点：
- **不可变性**：Record字段隐式final
- **自动生成**：构造函数、equals、hashCode、toString
- **继承限制**：只能继承java.lang.Record
- **语义**：基于值的语义，适合数据载体

**面试官：Record泛型方法怎么定义？**

```java
public record Container<T>(T value) {
    public <R> Container<R> map(Function<T,R> f) { return new Container<>(f.apply(value)); }
}
// 类级<T>和方法级<R>独立
```

## 六、交叉引用

- **相关主题**：[Java泛型擦除](../generics-erasure/README.md) - 泛型擦除、PECS原则
- **实战应用**：[Java Record概念](../../../01.java/concepts/record/README.md)
- **序列化**：[JSON处理](../../../06.spring/02-web/README.md)
