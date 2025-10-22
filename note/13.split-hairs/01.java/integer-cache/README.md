# Integer缓存

## 一、核心原理
1. **缓存范围**
    - 默认缓存 **-128 到 127** 之间的整数对象。该范围基于实际开发中高频使用的小整数场景设计。
    - 可通过JVM参数 `-XX:AutoBoxCacheMax=<size>` 调整上限（如设为200，则范围变为-128到200），但需谨慎以避免内存浪费。

2. **复用机制**
    - 当通过 `Integer.valueOf(int)` 或自动装箱（如 `Integer a = 100;`）创建对象时：
        - 若值在缓存范围内，直接返回缓存池中的对象（**同一内存地址**）。
        - 若值超出范围，则新建对象（不同内存地址）。

## 二、实现细节
1. **IntegerCache内部类**
    - `Integer` 类通过静态嵌套类 `IntegerCache` 管理缓存，其核心代码如下：
      ```java
      private static class IntegerCache {
          static final int low = -128;
          static final int high; // 默认127，可通过JVM参数调整
          static final Integer[] cache;
          static {
              high = 127; // 默认值
              String prop = VM.getSavedProperty("java.lang.Integer.IntegerCache.high");
              if (prop != null) {
                  int i = parseInt(prop);
                  high = Math.min(i, Integer.MAX_VALUE - (-low) - 1);
              }
              cache = new Integer[(high - low) + 1];
              for (int j = 0; j < cache.length; j++) {
                  cache[j] = new Integer(low + j);
              }
          }
      }
      ```

2. **valueOf方法逻辑**
    - `Integer.valueOf(int i)` 方法是缓存复用的入口：
      ```java
      public static Integer valueOf(int i) {
          if (i >= IntegerCache.low && i <= IntegerCache.high) {
              return IntegerCache.cache[i + (-IntegerCache.low)];
          }
          return new Integer(i);
      }
      ```

## 三、使用场景与示例
1. **自动装箱与缓存复用**
   ```java
   Integer a = 127;  // 缓存范围内
   Integer b = 127;
   System.out.println(a == b); // true（同一对象）

   Integer c = 128;  // 超出缓存范围
   Integer d = 128;
   System.out.println(c == d); // false（新建对象）
   ```

2. **显式调用valueOf**
   ```java
   Integer x = Integer.valueOf(100);  // 缓存复用
   Integer y = Integer.valueOf(100);
   System.out.println(x == y); // true
   ```

3. **new关键字绕过缓存**
   ```java
   Integer m = new Integer(100);  // 强制新建对象
   Integer n = new Integer(100);
   System.out.println(m == n); // false
   ```

## 四、注意事项
1. **对象比较陷阱**
    - **错误用法**：使用 `==` 比较 `Integer` 对象（仅当值在缓存范围内且未使用 `new` 时可能为 `true`）。
    - **正确做法**：始终使用 `equals()` 方法或拆箱后比较：
      ```java
      Integer num1 = 200;
      Integer num2 = 200;
      System.out.println(num1.equals(num2)); // true
      System.out.println(num1.intValue() == num2.intValue()); // true
      ```

2. **缓存范围调整风险**
    - 扩大缓存范围（如设为200）会占用更多内存，需权衡性能与内存消耗。
    - 最大缓存上限受 `Integer.MAX_VALUE - (-low) - 1` 限制（约2^31 - 129）。

3. **其他包装类的缓存**
    - `Byte`、`Short`、`Character`、`Long`、`Boolean` 也有类似缓存机制，但范围或实现细节可能不同（如 `Character` 缓存0-127）。
    - `Float` 和 `Double` 无缓存机制。

## 五、性能优化意义
- **减少内存分配**：高频使用的小整数对象复用缓存，避免重复创建。
- **降低GC压力**：缓存对象不会被垃圾回收，减少GC频率。
- **提升运算效率**：在循环、计数等场景中，缓存复用显著提高性能。

**总结**：Integer缓存机制通过复用小整数对象优化性能，但需注意对象比较方式和缓存范围调整的风险。在开发中应优先使用 `equals()` 比较对象，并谨慎扩展缓存上限。