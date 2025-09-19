# Object类

Java中的`Object`类是所有Java类的根类（超类），即所有类（除直接继承其他类的类外）都默认继承自`Object`。它定义了所有对象共有的基本行为，

## 核心方法与作用
1. **`public boolean equals(Object obj)`**
    - **默认行为**：比较两个对象的内存地址是否相同（即是否为同一对象）。
    - **重写场景**：当需要基于对象内容而非内存地址判断相等性时（如自定义类的对象比较），需重写此方法。例如：
      ```java
      @Override
      public boolean equals(Object o) {
          if (this == o) return true;
          if (o == null || getClass() != o.getClass()) return false;
          // 比较对象属性值
      }
      ```

2. **`public int hashCode()`**
    - **默认行为**：返回对象的内存地址的哈希值（由JVM决定）。
    - **重写规则**：若重写`equals()`，必须同步重写`hashCode()`，确保**相等的对象哈希值相同**（否则会违反`HashMap`等集合的约定）。

3. **`public String toString()`**
    - **默认行为**：返回`类名@十六进制哈希码`（如`java.lang.Object@1a2b3c`）。
    - **重写场景**：为对象提供有意义的字符串表示（如调试信息），例如：
      ```java
      @Override
      public String toString() {
          return "Person{name='张三', age=20}";
      }
      ```

4. **`protected Object clone() throws CloneNotSupportedException`**
    - 实现对象的浅拷贝。需先实现`Cloneable`接口（标记接口），并重写方法为`public`。
    - **深拷贝**需手动处理对象内部的可变引用。

5. **`public final Class<?> getClass()`**
    - 返回对象的运行时类（`Class`实例），可用于反射操作（如获取类名、方法、字段等）。

6. **线程通信方法**
    - `public final void wait()`, `public final void notify()`, `public final void notifyAll()`
    - **注意**：需在`synchronized`同步块/方法中调用，用于线程间协作（如等待条件满足、唤醒等待线程）。

7. **`protected void finalize() throws Throwable`**
    - **已过时（Java 9+）**：垃圾回收前可能调用的清理方法。因执行时机不确定且影响性能，推荐使用`try-with-resources`或`Cleaner`替代。

## 关键特性
- **单例设计模式基础**：`Object`提供了线程安全的单例实现方式（如`private`构造器+静态工厂方法）。
- **多态基石**：所有对象均可向上转型为`Object`，支持泛型、集合（如`List<Object>`）等通用操作。
- **默认行为一致性**：未重写的方法保持默认实现（如`equals`的地址比较），避免意外行为。

## 最佳实践
- **重写原则**：
    - 重写`equals()`时，需满足自反性、对称性、传递性、一致性、非空性。
    - 重写`hashCode()`时，使用`Objects.hash(属性1, 属性2)`或手动组合属性哈希值。
- **避免滥用**：如非必要，避免重写`clone()`（优先用拷贝构造函数或序列化方案）。
- **线程安全**：`wait()/notify()`需谨慎使用，优先选择`java.util.concurrent`中的高级同步工具（如`CountDownLatch`、`BlockingQueue`）。

通过理解`Object`类的方法和特性，可以更高效地设计自定义类，并确保其与Java生态（如集合框架、多线程）兼容。