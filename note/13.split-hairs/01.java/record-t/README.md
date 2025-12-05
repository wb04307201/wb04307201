# Record可以使用泛型么？

从 Java 14 引入 `record`（预览特性），到 Java 16 正式发布，record 作为一种特殊形式的类（主要用于不可变数据载体），完全支持泛型。

## 泛型 record 的基本语法

```java
public record Box<T>(T value) {}
```

在这个例子中，`Box` 是一个泛型 record，它持有一个类型为 `T` 的字段 `value`。

## 使用示例

```java
Box<String> stringBox = new Box<>("Hello");
Box<Integer> intBox = new Box<>(42);

System.out.println(stringBox.value()); // 输出: Hello
System.out.println(intBox.value());    // 输出: 42
```

## 支持多个泛型参数

```java
public record Pair<K, V>(K key, V value) {}
```

使用：

```java
Pair<String, Integer> pair = new Pair<>("Age", 30);
System.out.println(pair.key() + ": " + pair.value()); // Age: 30
```

### ⚠️ 注意事项

1. **泛型擦除**：和普通泛型类一样，record 的泛型在运行时也会被擦除（type erasure）。
2. **不能继承**：record 隐式继承自 `java.lang.Record`，因此不能显式继承其他类（包括泛型类），但可以实现接口。
3. **不能抽象**：record 不能是抽象的，所以不能定义抽象泛型方法（但可以使用泛型字段和泛型方法）。

## 泛型方法（在 record 内部）

record 也可以包含泛型方法（虽然不常见）：

```java
public record Container<T>(T item) {
    public <R> R map(Function<T, R> mapper) {
        return mapper.apply(item);
    }
}
```

使用：

```java
Container<String> container = new Container<>("world");
String upper = container.map(String::toUpperCase);
System.out.println(upper); // WORLD
```

---

## 总结

✅ **Java record 支持泛型**，语法简洁，使用方式与普通泛型类一致，非常适合用于封装通用的数据结构（如 `Result<T>`, `Pair<K,V>` 等）。

> 兼容性：Java 16+（record 正式发布版本），泛型 record 在 Java 14+ 的预览版本中就已支持。