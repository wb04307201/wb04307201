# 字符串拼接优化：StringBuilder 重用

在Java中，字符串拼接的性能优化是高频需求，而`StringBuilder`的重用是核心策略之一。

## 1. 为什么需要重用StringBuilder？
- **避免频繁创建对象的开销**：每次`new StringBuilder()`都会分配内存并初始化字符数组，高频拼接场景下（如循环内）会触发多次GC，影响性能。
- **减少扩容次数**：`StringBuilder`默认初始容量为16，超过容量时需扩容（复制原数组到新数组），预分配容量或重用可减少扩容次数。
- **对比`String`直接拼接**：在Java 8+中，编译器虽会将`String`拼接优化为`StringBuilder`，但循环内仍会重复创建对象；而手动重用`StringBuilder`可完全避免此问题。

## 2. 重用StringBuilder的实践方法
### 方法1：循环内重用（局部变量）
```java
StringBuilder sb = new StringBuilder(1024); // 预分配容量
for (int i = 0; i < 1000; i++) {
    sb.append("data").append(i); // 连续append避免中间生成String
    if (sb.length() > 1000) {
        // 处理部分结果（如写入文件）
        sb.setLength(0); // 清空内容，保留容量
    }
}
String result = sb.toString();
```
- **优势**：局部变量安全，无并发风险；`setLength(0)`清空内容但保留内存，避免重复分配。
- **注意**：预分配容量需根据业务估算，避免过度分配。

### 方法2：线程局部变量（ThreadLocal）
```java
private static final ThreadLocal<StringBuilder> SB_TL = ThreadLocal.withInitial(() -> 
    new StringBuilder(2048)
);

public String buildString() {
    StringBuilder sb = SB_TL.get();
    sb.setLength(0); // 重置长度，清空内容
    sb.append("Hello").append(" World");
    return sb.toString();
}
```
- **适用场景**：多线程环境下，避免为每个线程重复创建对象。
- **注意**：需在不再使用时调用`remove()`防止内存泄漏；容量固定，不适合动态扩容需求。

### 方法3：对象池（Object Pool）
- **适用场景**：超高并发、对象创建成本极高的场景（如Android低内存环境）。
- **实现**：使用`ConcurrentLinkedQueue`或第三方库（如Apache Commons Pool）管理`StringBuilder`实例。
- **注意**：需权衡池化带来的复杂性与性能收益，多数场景下`ThreadLocal`已足够。

## 3. 关键注意事项
- **线程安全**：`StringBuilder`非线程安全，多线程场景下必须通过`ThreadLocal`或同步控制确保线程独占。
- **容量管理**：
    - 预分配容量：通过`StringBuilder(int capacity)`避免初始扩容。
    - 动态扩容：当内容超过当前容量时，`StringBuilder`会自动扩容（通常为原容量×2+2），但频繁扩容仍影响性能，建议预估最大长度。
- **清空方式对比**：
    - `setLength(0)`：高效，保留原数组，下次`append`直接覆盖。
    - `delete(0, length())`：会触发数组复制，性能略差。
    - `new StringBuilder()`：重新分配内存，性能最差。
- **避免“假重用”**：
  ```java
  // 错误示例：表面重用，实则每次调用都创建新对象
  public StringBuilder getBuilder() {
      return new StringBuilder(); // 应返回已存在的实例
  }
  ```

## 4. 性能对比数据（参考）
| 操作方式                     | 10万次拼接耗时（ms） | 内存分配（MB）      |
|--------------------------|--------------|---------------|
| `String`直接拼接             | 1200+        | 高（大量临时String） |
| 循环内`new StringBuilder()` | 800          | 中（多次创建对象）     |
| `ThreadLocal`重用          | 150          | 低（单对象复用）      |
| 预分配容量+`setLength(0)`     | 120          | 极低（内存复用）      |

## 5. 最佳实践总结
- **单线程高频拼接**：使用局部变量+`setLength(0)`清空。
- **多线程场景**：`ThreadLocal`缓存实例，配合`setLength(0)`重用。
- **超大字符串**：预估容量，避免扩容；考虑分块处理（如每1000条数据写入文件后清空）。
- **代码可读性**：在性能敏感的代码段添加注释，说明重用逻辑，避免后续维护困惑。

通过合理重用`StringBuilder`，可显著提升字符串操作的性能，尤其在大数据量、高并发的场景下效果尤为明显。关键在于根据具体场景选择合适的重用策略，并注意线程安全与内存管理。