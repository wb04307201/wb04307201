# Optional 类

> `Optional`是`Java 8`引入的一个容器类，它位于`java.util`包下。`Optional`类是一个可以为null的容器对象，用于解决空指针异常（`NullPointerException`）的问题。通过明确地使用`Optional`，程序可以更加清晰地表达一个值可能存在也可能不存在的情况，从而提高代码的健壮性和可读性。  

## 主要特点和用途

> - **避免空指针异常**：`Optional`提供了一种更优雅的方式来处理可能为`null`的值，从而避免了在程序中频繁地进行空值检查。明确的存在性表示：`Optional`可以清晰地表示一个值是否存在，这比传统的`null`检查方式更加直观。
> - **链式调用**：`Optional`提供了丰富的API，支持链式调用，从而使得代码更加简洁和易于维护。

## `Optional`常用方法

### 创建`Optional`实例

> `Optional`类提供了几种创建实例的方法：
> - **`Optional.empty()`**：创建一个空的`Optional`实例，不包含任何值。
> - **`Optional.of(T value)`**：创建一个包含指定值的`Optional`实例。如果`value`为`null`，则抛出`NullPointerException`。
> - **`Optional.ofNullable(T value)`**：创建一个可能包含`null`值的`Optional`实例。如果`value`为`null`，则返回一个空的`Optional`实例。

### 常用方法

> - **`isPresent()`**：检查Optional实例中是否包含值。如果包含值，则返回`true`；否则返回`false`。
> - **`get()`**：如果`Optional`实例包含值，则返回该值；否则抛出`NoSuchElementException`。
> - **`orElse(T other)`**：如果`Optional`实例包含值，则返回该值；否则返回指定的默认值`other`。
> - **`orElseGet(Supplier<? extends T> other)`**：如果`Optional`实例包含值，则返回该值；否则调用`other`提供的`Supplier`函数生成一个默认值。
> - **`orElseThrow(Supplier<? extends X> exceptionSupplier)`**：如果`Optional`实例包含值，则返回该值；否则抛出由`exceptionSupplier`提供的异常。
> - **`ifPresent(Consumer<? super T> consumer)`**：如果`Optional`实例包含值，则使用`consumer`对其执行操作。
> - **`map(Function<? super T, ? extends U> mapper)`**：如果`Optional`实例包含值，则将其映射到另一个值上，并返回包含新值的`Optional`实例；否则返回一个空的`Optional`实例。
> - **`flatMap(Function<? super T, Optional<U>> mapper)`**：与`map`类似，但映射函数返回的是`Optional`类型，并且会自动扁平化。

```java
import java.util.Optional;

public class OptionalExample {
    public static void main(String[] args) {
        // 创建一个包含值的Optional
        Optional<String> optionalString = Optional.of("Hello, Optional!");
    
        // 使用isPresent()检查值是否存在
        if (optionalString.isPresent()) {
            System.out.println(optionalString.get()); // 输出: Hello, Optional! 
        }
    
        // 使用orElse()提供默认值
        String value = optionalString.orElse("Default Value");
        System.out.println(value); // 输出: Hello, Optional!
        
        // 使用map()进行转换
        Optional<Integer> optionalLength = optionalString.map(String::length);
        if (optionalLength.isPresent()) {
            System.out.println("Length: " + optionalLength.get()); // 输出: Length: 15
        }
    
        // 创建一个空的Optional
        Optional<String> emptyOptional = Optional.ofNullable(null);
    
        // 使用orElseGet()
        String emptyValue = emptyOptional.orElseGet(() -> "Value is not present");
        System.out.println(emptyValue); // 输出: Value is not present
        
        // 使用ifPresent()
        emptyOptional.ifPresent(System.out::println); // 不会打印任何东西
    }
}
```