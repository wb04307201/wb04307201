<!--
question:
  id: 01.java-reuse-of-stringbuilder
  topic: 01.java
  difficulty: ⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [01.java, reuse, stringbuilder]
-->

# 字符串拼接优化：StringBuilder 重用深度解析

## 引子：你真的会用 StringBuilder 吗？

```java
// 大多数人的写法
public String buildSql(List<String> columns) {
    StringBuilder sb = new StringBuilder();
    sb.append("SELECT ");
    for (String col : columns) {
        sb.append(col).append(", ");
    }
    return sb.toString();
}

// 高并发场景下：每次调用都创建新的 StringBuilder
// 1000 QPS × 每次调用 = 1000 个临时对象/秒
```

StringBuilder 已经够快了，还能更快吗？

**能**——在高并发场景下，**重用 StringBuilder 实例**，避免频繁创建/销毁对象。

---

> 📚 **前置知识**：[String](../../../01.java/concepts/string/README.md)

## 一、核心原理

`String`不可变性导致每次拼接创建新对象，`StringBuilder`通过可变数组避免。高并发场景下**重用**实例才能最大化收益。

```java
// ❌ 低效：每次拼接创建新对象
String result = "";
for (int i = 0; i < 10000; i++) result += "item" + i;  // ~20000个临时对象

// ✅ 高效：只创建一个
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) sb.append("item").append(i);
String result = sb.toString();  // 1个StringBuilder + 1个String
```

**内部结构：**
```java
abstract class AbstractStringBuilder {
    byte[] value;   // 字符数组（JDK9+ compact）
    int count;      // 当前长度
    void expand(int min) { value = Arrays.copyOf(value, (value.length+1)*2); }  // ×2+2
}
```

**重用的价值：**

| **维度** | **新建** | **重用** |
|---------|---------|---------|
| 对象分配 | 每次新建 | 复用 |
| GC压力 | 大量垃圾 | 极少 |
| CPU | 重复初始化 | 仅清空计数 |

**编译器优化局限：**
```java
String s = "a" + "b";  // 编译器优化为new StringBuilder
for (int i=0; i<n; i++) result += items[i];  // 循环内仍重复创建
// 手动优化
StringBuilder sb = new StringBuilder();
for (int i=0; i<n; i++) sb.append(items[i]);
```

## 二、代码示例

**1. 基础重用**

```java
public String buildCsv(List<String[]> rows) {
    StringBuilder sb = new StringBuilder(100 * rows.size());
    for (String[] row : rows) {
        for (int i = 0; i < row.length; i++) {
            sb.append(row[i]); if (i < row.length-1) sb.append(',');
        }
        sb.append('\n');
        if (sb.length() > 8192) { flush(sb.toString()); sb.setLength(0); }  // 清空重用
    }
    return sb.toString();
}
```

**JMH测试：** 重用比每次新建快约7倍（890 vs 125 ops/s）。

**2. ThreadLocal重用**

```java
public class TLStringBuilder {
    private static final ThreadLocal<StringBuilder> TL = ThreadLocal.withInitial(() -> new StringBuilder(256));
    public static StringBuilder get() { StringBuilder sb = TL.get(); sb.setLength(0); return sb; }
    public static void cleanup() { TL.remove(); }  // 防止内存泄漏
}

// Spring Filter中使用
try {
    StringBuilder sb = TLStringBuilder.get();
    sb.append(request.getMethod()).append(' ').append(request.getRequestURI());
    log.info("Request: {}", sb);
} finally { TLStringBuilder.cleanup(); }
```

**3. 容量管理**

```java
// 预分配：expectedSize * 5/4 + 16
StringBuilder sb = new StringBuilder(expectedChars * 5 / 4 + 16);

// 动态调整：超过阈值重建
if (reuseCount > 100 && sb.capacity() > 65536) sb = new StringBuilder(256);
else sb.setLength(0);
```

**4. 替代方案**

```java
String.join(", ", names);                    // 已知集合
String.format("Name: %s", name);             // 模板化
"""{"name": "%s"}""".formatted(name);        // Text Blocks
names.stream().collect(Collectors.joining(", "));  // Stream
```

## 三、常见陷阱

**陷阱1：忘记清空**
```java
// ❌ 内容累积
StringBuilder sb = new StringBuilder();
for (int i=0; i<10; i++) { sb.append(i); process(sb.toString()); }  // "0","01","012"...
// ✅ setLength(0)
for (int i=0; i<10; i++) { sb.setLength(0); sb.append(i); process(sb.toString()); }
```

**陷阱2：delete vs setLength**
```java
// ❌ delete触发数组复制，O(n)
sb.delete(0, sb.length());
// ✅ setLength只改计数，O(1)
sb.setLength(0);
```

**陷阱3：线程安全**
```java
// ❌ StringBuilder非线程安全
private static StringBuilder shared = new StringBuilder();  // 多线程append会错乱
// ✅ ThreadLocal
private static ThreadLocal<StringBuilder> tl = ThreadLocal.withInitial(StringBuilder::new);
// ✅ 或StringBuffer（有同步开销）
StringBuffer safe = new StringBuffer();
```

**陷阱4：ThreadLocal泄漏**
```java
// ❌ 不清理导致内存泄漏（线程池环境）
@WebFilter("/*")
public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) {
    StringBuilder sb = tl.get(); /* 使用 */ chain.doFilter(req, res);
    // 忘记tl.remove() → 泄漏！
}
// ✅ finally中清理
try { /* 使用 */ } finally { tl.remove(); }
```

**陷阱5：忽略简洁方案**
```java
// ❌ 过度使用
StringBuilder sb = new StringBuilder();
for (int i=0; i<names.size(); i++) { if (i>0) sb.append(", "); sb.append(names.get(i)); }
// ✅
String.join(", ", names);
```

## 四、最佳实践

**1. 选型决策**
```
拼接需求？
├── 固定少量(≤5) → +运算符（编译器优化）
├── 循环内 → StringBuilder + setLength(0)
├── Web请求 → ThreadLocal重用
├── 集合连接 → String.join() / Collectors.joining()
├── 模板化 → String.format() / Text Blocks
└── 超大(>1MB) → 直接OutputStream
```

**2. 工具类封装**

```java
public final class SBUtils {
    private static final ThreadLocal<StringBuilder> TL = ThreadLocal.withInitial(() -> new StringBuilder(256));
    public static StringBuilder obtain() { StringBuilder sb = TL.get(); sb.setLength(0); return sb; }
    public static void release() { TL.remove(); }
    public static String join(CharSequence d, Iterable<?> e) {
        StringBuilder sb = obtain(); boolean f = true;
        for (Object x : e) { if (!f) sb.append(d); sb.append(x); f = false; }
        String r = sb.toString(); release(); return r;
    }
}
```

**3. 监控**
```java
@Component public class SBMetrics {
    private final LongAdder allocs = new LongAdder(), reuses = new LongAdder();
    public double rate() { long t = allocs.sum()+reuses.sum(); return t==0?0:(double)reuses.sum()/t; }
}
```

## 五、面试话术

**面试官：为什么StringBuilder比String拼接快？**

回答要点：
1. String每次拼接创建新对象，产生大量垃圾；StringBuilder用可变数组
2. 编译器虽优化简单拼接，但循环内仍重复创建
3. 10000次拼接：String约100ms，StringBuilder约1ms，差100倍

**面试官：如何重用StringBuilder？**

回答要点：
- 局部变量：循环外创建，`setLength(0)`清空
- ThreadLocal：Web应用每个请求复用，finally中remove
- `setLength(0)`比`delete(0,len)`快，只改计数不复制数组

**面试官：StringBuilder vs StringBuffer？**

回答要点：
- StringBuffer加synchronized线程安全；StringBuilder不加锁更快
- 单线程用StringBuilder；多线程共享用StringBuffer或ThreadLocal

## 六、交叉引用

- **底层原理**：[String/Builder/Buffer 深度对比](../string-builder-buffer/README.md) - 扩容机制 + 源码拆解 + JIT intrinsic
- **相关主题**：[new String对象创建](../new-string/README.md) - 字符串常量池
- **并发编程**：[ThreadLocal](../thread-pool/README.md) - 内存泄漏防范
- **性能调优**：[JVM调优](../../../01.java/jvm/tuning.md)
- **关联知识**：[HashMap扩容](../hashmap-resizing/README.md) - 预分配容量

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · reuse-of-stringbuilder](../README.md)
