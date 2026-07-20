<!--
question:
  id: 01.java-try-catch-performance
  topic: 01.java
  difficulty: ⭐⭐⭐
  frequency: 中高频
  scenario_type: 反直觉性能
  tags: [01.java, try-catch, 异常性能, JVM, fillInStackTrace, OmitStackTraceInFastThrow]
-->

# try-catch 会影响性能吗？—— 正常路径零开销，异常抛出才贵

> 一句话定位：**Java 性能面试题经典**。考察的不是"try-catch 慢不慢"，而是**区分正常路径和异常路径的开销差异** + **fillInStackTrace 的根因** + **JIT 快速抛出优化** + **替代方案选型**。完整异常体系见 [异常主模块](../../../01.java/concepts/exception/README.md)。

> **系列定位**：中高频性能面试题。配套兄弟题：[Error vs Exception](../error-vs-exception/README.md)、[StringBuilder 重用](../reuse-of-stringbuilder/README.md)。

---

⭐⭐⭐ 深度级别（中高级）
📚 前置知识：JVM 栈帧 / 异常表 / JIT 编译

---

## 引子：一段反直觉的 benchmark

```java
// 测试 1：有 try-catch 的正常路径
long sum = 0;
for (int i = 0; i < 1_000_000; i++) {
    try {
        sum += i;
    } catch (Exception e) {
        // 不会进入
    }
}
// 耗时：~2ms

// 测试 2：没有 try-catch 的正常路径
long sum2 = 0;
for (int i = 0; i < 1_000_000; i++) {
    sum2 += i;
}
// 耗时：~2ms（几乎一样！）

// 测试 3：每次都抛异常
long sum3 = 0;
for (int i = 0; i < 1_000_000; i++) {
    try {
        throw new Exception();
    } catch (Exception e) {
        sum3 += i;
    }
}
// 耗时：~800ms（慢了 400 倍！）
```

**结论**：try-catch **正常路径几乎零开销**，但**异常抛出极其昂贵**。

---

## 一、核心原理

### 1.1 try-catch 的字节码实现：异常表

try-catch 在字节码层面**不是指令**，而是一张**异常表**（Exception Table）：

```
// 字节码（简化）
  0: iload_1           // 正常路径的指令
  1: iadd
  2: istore_2
  // ... 没有 catch 相关的指令！

Exception table:
  from    to  target type
     0     3     4   Class java/lang/Exception
```

**正常路径**：CPU 按顺序执行指令，异常表不参与执行 → **零开销**。

**异常路径**：JVM 在异常发生时查异常表，找到匹配的 handler → 跳转到 target 偏移量。

### 1.2 异常抛出的开销来源

抛出一个异常涉及 3 个昂贵操作：

| 步骤 | 操作 | 开销 |
|------|------|------|
| 1 | `new Exception()` | 对象分配（堆内存） |
| 2 | `fillInStackTrace()` | **遍历整个调用栈**，记录每一帧的类名/方法名/行号 → **最慢** |
| 3 | 栈展开（stack unwinding） | 从抛出点逐帧查找异常表匹配的 handler |

**fillInStackTrace 占总开销的 60-80%**——调用栈越深越慢。

```java
// 自定义异常可以跳过 fillInStackTrace
public class FastException extends RuntimeException {
    @Override
    public synchronized Throwable fillInStackTrace() {
        return this;  // 不收集堆栈，性能提升 10-50 倍
    }
}

// benchmark
throw new RuntimeException();  // ~800ns（含 fillInStackTrace）
throw new FastException();     // ~15ns（跳过 fillInStackTrace）
```

### 1.3 JIT 优化：OmitStackTraceInFastThrow

JVM 有一个关键优化：**同一个位置反复抛出同一个异常时，JIT 会省略堆栈收集**。

```java
// 循环中反复抛 NPE
for (int i = 0; i < 1_000_000; i++) {
    try {
        String s = null;
        s.length();  // 每次都抛 NPE
    } catch (NullPointerException e) {
        // 前几千次：完整堆栈（~800ns）
        // JIT 优化后：无堆栈的预分配实例（~10ns）
    }
}
```

**原理**：JVM 对 `NullPointerException`、`ArithmeticException`、`ArrayIndexOutOfBoundsException` 等内置异常预分配了**无堆栈的单例实例**。JIT 检测到同一位置反复抛出后，直接用预分配实例替代 `new`。

**关闭优化**（调试时需要完整堆栈）：
```bash
-XX:-OmitStackTraceInFastThrow
```

---

## 二、5 道精选面试题

### Q1：try-catch 放在循环内和循环外，性能有区别吗？

**答**：正常路径**没有区别**。try-catch 的开销只与异常抛出次数有关，与位置无关。

```java
// 写法 A：try 在循环内
for (int i = 0; i < 1000; i++) {
    try { doWork(); } catch (Exception e) { handle(e); }
}

// 写法 B：try 在循环外
try {
    for (int i = 0; i < 1000; i++) {
        doWork();
    }
} catch (Exception e) {
    handle(e);  // 一次异常就终止循环
}
```

**选择标准不是性能，而是语义**：循环内 catch 允许"单个失败继续处理"，循环外 catch 是"一次失败全部中止"。

### Q2：为什么不要用异常做流程控制？

**答**：3 个原因——

1. **性能**：异常抛出涉及对象分配 + 栈遍历，比 if 判断慢 100-1000 倍
2. **可读性**：异常是"非正常路径"，用来做流程控制违反语义
3. **调试干扰**：真正的异常和"流程控制异常"混在一起，增加排查难度

```java
// ❌ 用异常做流程控制
try {
    while (true) {
        process(array[index++]);
    }
} catch (ArrayIndexOutOfBoundsException e) {
    // 用越界异常当循环终止条件
}

// ✅ 正常写法
for (int i = 0; i < array.length; i++) {
    process(array[i]);
}
```

### Q3：`throw new RuntimeException()` 和 `throw new RuntimeException("msg")` 哪个快？

**答**：**几乎一样快**。性能瓶颈在 `fillInStackTrace()`（栈遍历），不在消息字符串。消息只是一个字符串赋值，开销可忽略。

### Q4：自定义异常怎么优化性能？

**答**：重写 `fillInStackTrace()` 跳过栈收集：

```java
public class BusinessException extends RuntimeException {
    @Override
    public synchronized Throwable fillInStackTrace() {
        return this;  // 不需要堆栈信息
    }
}
```

**适用场景**：业务异常（如"余额不足"）不需要堆栈，只需错误码 + 消息。可提升 10-50 倍。

**不适用**：系统异常（如"数据库连接失败"）需要堆栈定位问题。

### Q5：Optional / Result 模式能替代 try-catch 吗？

**答**：能替代部分场景，各有优劣：

| 方案 | 性能 | 可读性 | 适用 |
|------|------|--------|------|
| **try-catch** | 异常路径慢 | 正常路径清晰 | I/O 操作 / 第三方库 |
| **Optional** | 无异常开销 | 链式优雅 | 可能为 null 的查询 |
| **Result\<T,E\>** | 无异常开销 | 显式错误处理 | 函数式风格 / 多层错误传播 |

```java
// Optional 替代 null 检查异常
Optional<User> user = userRepository.findById(id);
user.ifPresent(u -> sendEmail(u));

// Result 模式（Vavr / Arrow 等库）
Result<Order, BusinessError> result = createOrder(request);
result.fold(
    error -> ResponseEntity.badRequest().body(error.getMessage()),
    order -> ResponseEntity.ok(order)
);
```

---

## 三、常见陷阱

**陷阱 1：在热路径上 catch 并忽略**

```java
// ❌ 热路径上的异常即使被忽略，抛出时仍有开销
for (String s : input) {
    try {
        result.add(Integer.parseInt(s));
    } catch (NumberFormatException ignored) {
        // 即使忽略，parseInt 抛异常时 fillInStackTrace 已经执行了
    }
}

// ✅ 预检查
for (String s : input) {
    if (isNumeric(s)) {
        result.add(Integer.parseInt(s));
    }
}
```

**陷阱 2：静态异常实例**

```java
// ❌ 静态异常实例 → 堆栈永远是创建时的，不是抛出时的
private static final RuntimeException ERROR = new RuntimeException("error");

public void process() {
    throw ERROR;  // 堆栈指向 static 初始化行，不是 process()
}

// ✅ 每次 new
public void process() {
    throw new RuntimeException("error");  // 堆栈指向 process()
}
```

**陷阱 3：catch 后立即 throw（无意义包装）**

```java
// ❌ 无意义的 catch-rethrow，增加一层异常包装
try {
    dao.save(entity);
} catch (SQLException e) {
    throw e;  // 什么都没做，多了一层 try-catch 开销
}

// ✅ 要么处理，要么不 catch
dao.save(entity);  // 让调用者处理
```

---

## 四、面试话术（30 秒版）

> "try-catch 在正常路径几乎零开销——它在字节码层面是异常表，不参与正常指令执行。
>
> 性能开销来自异常抛出：`new Exception()` 的对象分配 + `fillInStackTrace()` 遍历整个调用栈（占 60-80% 开销）+ 栈展开查找 handler。一次异常抛出约 800ns，比 if 判断慢 100-1000 倍。
>
> JVM 有 OmitStackTraceInFastThrow 优化——同一位置反复抛同一异常时，JIT 会用预分配的无堆栈实例替代，性能提升到 ~10ns。
>
> 自定义业务异常可以重写 `fillInStackTrace()` 返回 this，跳过栈收集，提升 10-50 倍。但不适合需要堆栈定位的系统异常。
>
> 最佳实践：异常只用于真正的异常情况，不要用异常做流程控制。可选场景用 Optional 或 Result 模式替代。"

---

## 五、交叉引用

- **异常体系**：[异常](../../../01.java/concepts/exception/README.md) — 异常层次 / checked vs unchecked / try-with-resources / Spring 全局处理
- **相关面试题**：[Error vs Exception](../error-vs-exception/README.md) — 6 维度对比 + 反模式
- **相关面试题**：[StringBuilder 重用](../reuse-of-stringbuilder/README.md) — 同类性能优化思维
- **JVM 调优**：[JVM 调优](../../../01.java/jvm/tuning.md) — OmitStackTraceInFastThrow 等 JVM 参数
- **主模块**：[`01.java`](../../../01.java/) — Java 知识体系

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · try-catch-performance](../README.md)
