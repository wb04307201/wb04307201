# Optional

| Java版本  | 新特性/增强内容                                                  |
|---------|-----------------------------------------------------------|
| Java 8  | JEP 107: 首次引入 `Optional` 类，用于优雅地处理 `NullPointerException` |
| Java 9  | Optional 增强，新增 `ifPresentOrElse()`、`or()` 和 `stream()` 方法 |
| Java 10 | Optional 增强，新增 `orElseThrow()` 方法                         |
| Java 11 | Optional 增强，新增 `isEmpty()` 方法                             |

## 功能详细介绍

### 1. Java 8 - Optional 类初始引入

Java 8 首次引入了 `Optional` 类，这是为了解决 Java 中最常见的运行时异常之一：`NullPointerException`。

#### 核心概念和设计目标：

1. **优雅处理空值**：Optional 提供了一种更优雅的方式来处理可能为空的值，避免直接使用 `null` 导致的空指针异常
2. **函数式编程支持**：Optional 与 Stream API 和 Lambda 表达式紧密结合，支持函数式编程风格
3. **明确的意图表达**：通过使用 Optional，方法签名可以明确表达返回值可能为空的意图

#### 主要方法：

```java
// 创建 Optional 实例
Optional<String> optional1 = Optional.empty();           // 创建空的 Optional
Optional<String> optional2 = Optional.of("Hello");       // 创建包含值的 Optional（不允许 null）
Optional<String> optional3 = Optional.ofNullable(null);  // 创建可能包含 null 的 Optional

// 检查值是否存在
if (optional2.isPresent()) {
    System.out.println(optional2.get());
}

// 提供默认值
String result = optional3.orElse("Default Value");
String result2 = optional3.orElseGet(() -> "Computed Default");

// 执行操作
optional2.ifPresent(System.out::println);

// 转换值
Optional<String> upperCase = optional2.map(String::toUpperCase);
```


### 2. Java 9 - Optional 增强

Java 9 为 Optional 类添加了几个重要的新方法，增强了其功能和灵活性：

#### 新增方法：

1. **`ifPresentOrElse()`**：如果值存在则执行给定操作，否则执行给定的空值操作
2. **`or()`**：如果值存在则返回当前 Optional，否则返回由提供者创建的 Optional
3. **`stream()`**：将 Optional 转换为 Stream

```java
// ifPresentOrElse 示例
Optional<String> optional = Optional.ofNullable(getString());
optional.ifPresentOrElse(
    System.out::println,           // 值存在时执行
    () -> System.out.println("No value present")  // 值不存在时执行
);

// or 示例
Optional<String> first = Optional.empty();
Optional<String> second = Optional.of("Second");
Optional<String> result = first.or(() -> second);  // 返回第二个 Optional

// stream 示例
Optional<String> opt = Optional.of("Hello");
List<String> list = opt.stream().collect(Collectors.toList());  // 转换为包含 0 或 1 个元素的流
```


### 3. Java 10 - Optional 增强

Java 10 为 Optional 类添加了一个便捷方法：

#### 新增方法：

1. **`orElseThrow()`**：如果值不存在，则抛出 NoSuchElementException

```java
// orElseThrow 示例
Optional<String> optional = Optional.empty();
try {
    String value = optional.orElseThrow();  // 抛出 NoSuchElementException
} catch (NoSuchElementException e) {
    System.out.println("No value present");
}

// 与 get() 方法的区别：orElseThrow() 有更明确的语义
String value = optional.orElseThrow(() -> new RuntimeException("Value not present"));
```


### 4. Java 11 - Optional 增强

Java 11 为 Optional 类添加了一个检查空值的方法：

#### 新增方法：

1. **`isEmpty()`**：判断 Optional 是否为空（与 `isPresent()` 相反）

```java
// isEmpty 示例
Optional<String> emptyOptional = Optional.empty();
Optional<String> presentOptional = Optional.of("Hello");

System.out.println(emptyOptional.isEmpty());     // true
System.out.println(presentOptional.isEmpty());   // false

// 与 isPresent() 的对比
System.out.println(!emptyOptional.isPresent());     // true
System.out.println(!presentOptional.isPresent());   // false
```


## Optional 的核心优势

1. **避免 NullPointerException**：通过显式处理可能为空的值，减少运行时异常
2. **提高代码可读性**：方法签名明确表达了返回值可能为空的意图
3. **函数式编程支持**：与 Stream API 和 Lambda 表达式无缝集成
4. **链式操作**：支持流畅的链式调用，使代码更加简洁
5. **强制处理空值**：编译器强制开发者考虑空值情况

## 使用示例

```java
// 传统方式处理空值
public String getUserName(User user) {
    if (user != null) {
        Profile profile = user.getProfile();
        if (profile != null) {
            return profile.getName();
        }
    }
    return "Unknown";
}

// 使用 Optional 的方式
public String getUserName(User user) {
    return Optional.ofNullable(user)
                   .map(User::getProfile)
                   .map(Profile::getName)
                   .orElse("Unknown");
}

// 复杂的 Optional 链式操作
public Optional<String> processUser(User user) {
    return Optional.ofNullable(user)
                   .filter(u -> u.isActive())
                   .map(User::getProfile)
                   .flatMap(profile -> Optional.ofNullable(profile.getEmail()))
                   .filter(email -> email.contains("@"))
                   .map(String::toLowerCase);
}
```


## 最佳实践

1. **不要将 Optional 用作方法参数**：Optional 主要用于返回值
2. **不要在集合中使用 Optional**：应直接使用空集合而不是包含 Optional 的集合
3. **合理使用 orElse 和 orElseGet**：对于计算成本高的默认值，使用 orElseGet
4. **避免直接调用 get()**：应优先使用其他安全的方法
5. **考虑性能影响**：Optional 会带来轻微的性能开销，在性能敏感的场景中需要权衡

## 总结

Optional 从 Java 8 引入以来，逐步得到了增强和完善。它为 Java 提供了一种优雅且类型安全的方式来处理可能为空的值，有效减少了 NullPointerException 的发生。随着每个版本的迭代，Optional 的功能越来越丰富，使用起来也越来越便捷。通过合理使用 Optional，开发者可以编写出更加健壮、可读性更高的代码。