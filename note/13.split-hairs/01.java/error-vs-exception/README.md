<!--
question:
  id: 01.java-error-vs-exception
  topic: 01.java
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 反直觉代码
  tags: [01.java, Error, Exception, Throwable, 异常处理]
-->

# Error 和 Exception 的区别深度剖析

> 一句话定位：Throwable 的两条分支决定了"能不能救"和"该不该救" —— 搞混了轻则代码冗余，重则掩盖 JVM 致命故障。完整概念见 [异常](../../../01.java/concepts/exception/README.md)。

> **系列定位**：经典 Java 面试题（异常处理、JVM 高频）。考察的不是"Error 严重 Exception 不严重"，而是 **类层次设计意图** + **JVM 行为差异** + **可恢复性判断** + **实战反模式**。

---

## 引子：一段反直觉代码

```java
public class CatchErrorDemo {
    public static void main(String[] args) {
        try {
            int[] arr = new int[Integer.MAX_VALUE];
        } catch (Throwable t) {
            System.out.println("catch 住了: " + t.getClass().getName());
        }
        System.out.println("程序继续运行");
    }
}
```

这段代码**能编译、能运行、能 catch 住 OutOfMemoryError**。

面试官问："Error 不是不该 catch 吗？为什么编译器不报错？catch 了会怎样？"

如果你只能回答"Error 是严重的，Exception 是不严重的"——面试就结束了。

---

## 一、核心原理

### 1.1 Throwable 类层次结构

```
Throwable
├── Error（JVM 层面的严重故障，程序通常无法恢复）
│   ├── VirtualMachineError
│   │   ├── OutOfMemoryError（堆/栈/方法区内存耗尽）
│   │   └── StackOverflowError（调用栈深度溢出）
│   ├── LinkageError（类加载/链接失败）
│   │   └── NoClassDefFoundError
│   └── AssertionError（断言失败，-ea 启用）
│
└── Exception（程序逻辑层面的异常，可以且应该处理）
    ├── Checked Exception（编译期强制处理）
    │   ├── IOException
    │   ├── SQLException
    │   └── ClassNotFoundException
    └── RuntimeException（Unchecked，编译期不强制）
        ├── NullPointerException
        ├── IllegalArgumentException
        └── IndexOutOfBoundsException
```

Java 把所有可抛出的异常都归到 `Throwable` 下，但通过两条分支划清了界限：**Error 归 JVM 管，Exception 归应用管**。

### 1.2 六维度对比

| 对比维度 | Error | Exception |
|---------|-------|-----------|
| **设计意图** | JVM 无法继续执行的严重故障 | 程序逻辑中的异常情况，预期可处理 |
| **谁产生** | JVM 自身（内存管理、类加载等内部机制） | 应用程序代码（throw / throws） |
| **可恢复性** | 通常不可恢复（OOM 后 JVM 状态不可预测） | 通常可恢复（重试 / 降级 / 用户提示） |
| **编译器约束** | 不强制 catch，也不建议 catch | Checked 必须 catch 或 throws 声明；Unchecked 可选 |
| **典型处理策略** | 排查根因 + JVM 调优（-Xmx/-Xss），不是 catch 能解决的 | try-catch 处理 / 向上抛出 / 转换为业务异常 |
| **生产影响** | 通常导致线程终止或 JVM 崩溃，需运维介入 | 通常影响单次请求，可降级或重试 |

### 1.3 设计哲学：为什么 Java 要拆成两条分支？

Java 设计者把 Throwable 拆成 Error 和 Exception，本质上是在回答两个不同的问题：

- **Error = JVM 内部故障** → 应用代码无法修复 → 所以"不该 catch"不是语法限制，而是设计约定。你无法在代码里修复一个内存耗尽的 JVM，就像你无法用创可贴修好一台发动机。
- **Exception = 应用程序可预见的异常** → 必须提供处理机制 → 所以 Checked Exception 强制你处理。文件不存在、网络超时、SQL 语法错误——这些都是**程序运行环境中可以合理预见并应对的状况**。

这种设计的深层含义是：**编译器通过 Checked Exception 逼你思考失败路径，同时通过 Error 的分立告诉你有些失败不该用代码处理**。

---

## 二、代码示例

### 2.1 反模式：catch Error

```java
// ❌ 反模式：吞掉 Error，掩盖 JVM 致命故障
try {
    loadHugeData();
} catch (OutOfMemoryError e) {
    log.error("内存不足", e);  // 日志记录了，但程序继续跑在不确定状态
}
```

**问题**：OOM 发生后，JVM 内部状态已经不可预测。虽然 catch 住了，但后续操作可能随时再次 OOM 或产生错误结果。正确做法是让 Error 传播出去，触发 JVM 的默认处理（打印堆栈 + 退出），同时配合 `-XX:+HeapDumpOnOutOfMemoryError` 保留现场。

### 2.2 反模式：catch Throwable

```java
// ❌ 反模式：一网打尽，Error 也被吞
try {
    processOrder(order);
} catch (Throwable t) {
    log.error("处理失败", t);  // StackOverflowError 也被吞，栈已损坏
}
```

**问题**：`catch (Throwable t)` 把 Error 和 Exception 全部捕获，包括 StackOverflowError。当栈溢出发生时，栈帧已经损坏，继续执行任何代码都可能导致不可预期的行为。这是生产环境中最危险的反模式之一。

### 2.3 正确模式：只 catch Exception

```java
// ✅ 正确：只处理应用层异常，Error 由 JVM 处理
try {
    processOrder(order);
} catch (SQLException e) {
    throw new ServiceException("订单处理失败", e);  // 异常链传递
}
```

**要点**：精确 catch 具体的异常类型，转换为业务异常向上传递。Error 不在 catch 范围内，由 JVM 自行处理。

### 2.4 唯一例外：资源清理场景可 catch Error

```java
// ✅ 唯一例外：finally 风格的资源清理（但推荐 try-with-resources）
Lock lock = new ReentrantLock();
lock.lock();
try {
    criticalSection();
} finally {
    lock.unlock();  // 即使 StackOverflowError 也确保释放锁
}
```

**说明**：`finally` 块在 Error 发生时仍然会执行（除非 JVM 直接崩溃），这是 Java 语言规范保证的。因此在 `finally` 中做资源释放是安全的——但更好的做法是用 `try-with-resources`，让编译器自动生成 finally 逻辑。

---

## 三、常见陷阱

### 陷阱 1：`catch(Exception e)` 能 catch Error

**真相**：不能。Exception 和 Error 是 Throwable 的两个平行子类，`catch(Exception)` 只匹配 Exception 分支。要 catch Error 必须显式写 `catch(Error e)` 或 `catch(Throwable t)`。

```java
try {
    throw new OutOfMemoryError();
} catch (Exception e) {
    // 这里不会执行！Error 不是 Exception 的子类
    System.out.println("catch 到了");
}
// OutOfMemoryError 直接传播到 JVM，程序终止
```

### 陷阱 2：Error 都是 JVM 产生的

**真相**：大部分 Error 由 JVM 产生，但不是全部。`AssertionError` 由 `assert` 语句产生（需要 `-ea` 参数启用），属于程序员主动触发的。此外，`OutOfMemoryError` 也可能由 `Unsafe.allocateMemory` 等用户代码间接触发，不是 JVM 自动检测到的。

### 陷阱 3：StackOverflowError 永远不能恢复

**真相**：在某些场景下（如递归深度可控），catch 后减少栈深度理论上可以继续运行。但这是**极其危险的**——栈帧状态可能已损坏，局部变量可能已被覆盖，后续代码执行结果不可预测。生产环境应视为"必须重启"。

### 陷阱 4：NoClassDefFoundError 和 ClassNotFoundException 是同一个东西

**真相**：完全不同。

| 对比 | NoClassDefFoundError | ClassNotFoundException |
|------|---------------------|----------------------|
| **类型** | Error（LinkageError 子类） | Checked Exception |
| **触发时机** | 类链接阶段失败（编译时有，运行时找不到） | 运行时动态加载失败（`Class.forName()` / `ClassLoader.loadClass()`） |
| **典型场景** | 部署时漏了 jar 包，类存在但依赖的类不存在 | 插件系统动态加载类名拼写错误 |

### 陷阱 5：OOM 后 JVM 一定会崩溃

**真相**：不一定。如果 OOM 发生在某个线程的局部操作中（比如一个大数组分配失败），其他线程可能不受影响，JVM 进程也不会自动退出。但此时 JVM 整体状态已不可预测——堆内存可能处于不一致状态，GC 可能无法正常执行。**生产环境应将任何 OOM 视为"必须重启"的信号**。

---

## 四、最佳实践

### 4.1 只 catch 你能处理的异常

`catch(Exception)` 已经够宽泛了，绝对不要 `catch(Error)` 或 `catch(Throwable)`。如果你发现自己写了 `catch(Throwable)`，先问自己：**你真的能处理 JVM 内存耗尽吗？**

### 4.2 Error 的正确应对是排查根因

- **OOM** → 分析 heap dump（`jmap -dump:live,format=b,file=heap.hprof <pid>` + Eclipse MAT）
- **StackOverflow** → 检查递归深度，增大 `-Xss` 或重构为迭代
- **NoClassDefFoundError** → 检查 classpath 和 jar 依赖版本冲突

### 4.3 全局异常处理器要排除 Error

```java
// ✅ 正确：@ControllerAdvice 只处理 Exception
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(Exception.class)
    public ResponseEntity<?> handleException(Exception e) {
        // 业务异常处理
    }
    // 不要加 @ExceptionHandler(Error.class) 或 @ExceptionHandler(Throwable.class)
}
```

### 4.4 JVM 参数预防优于 catch

```bash
# 内存上限 + OOM 自动 dump + 栈大小
-Xmx2g -Xss512k -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/dumps/
```

这些参数才是应对 Error 的正解，不是 try-catch。

### 4.5 自定义异常永远继承 RuntimeException 或 Exception

```java
// ✅ 正确
public class BusinessException extends RuntimeException { }
public class ValidationException extends Exception { }

// ❌ 错误：自定义 Error 或 Throwable 子类会破坏异常体系的约定
public class MyFatalError extends Error { }          // 不要这样做
public class MyMegaThrowable extends Throwable { }    // 更不要这样做
```

---

## 五、面试话术（90 秒版本）

> "Error 和 Exception 都是 Throwable 的子类，但设计意图完全不同。
>
> **Error** 是 JVM 层面的严重故障，比如 OutOfMemoryError、StackOverflowError，由 JVM 自身产生，表示程序已经无法继续执行。我们不应该 catch Error，因为即使 catch 住了，JVM 的内部状态也已经不可预测。
>
> **Exception** 是程序逻辑层面的异常，由应用代码抛出，分为 Checked 和 Unchecked 两类。Checked Exception 编译器强制你处理，比如 IOException；Unchecked 的 RuntimeException 编译期不强制，但通常也应该处理。
>
> 核心区别在三点：**设计意图**不同——Error 是 JVM 故障，Exception 是应用故障；**产生方**不同——Error 由 JVM 产生，Exception 由代码产生；**可恢复性**不同——Error 通常不可恢复，Exception 通常可以重试或降级。
>
> 实战中的原则是：只 catch 你能处理的 Exception，Error 通过 JVM 调优来预防。比如 `-Xmx` 防 OOM，`-XX:+HeapDumpOnOutOfMemoryError` 保留现场。
>
> 一个加分点：NoClassDefFoundError 和 ClassNotFoundException 名字像但完全不同——前者是 Error，在类链接阶段失败，通常是部署漏了 jar；后者是 Checked Exception，在 `Class.forName()` 动态加载时失败，通常是类名拼错。"

---

## 六、相关章节

- 同栏目：[`final/finally/finalize`](../final-finally-finalize/README.md) — finally 块在 Error 场景下的执行行为
- 🆕 同栏目：[`try-catch 性能`](../try-catch-performance/README.md) — 正常路径零开销 / fillInStackTrace / OmitStackTraceInFastThrow
- 主模块：[`异常体系`](../../../01.java/concepts/exception/README.md) — Java 异常完整知识体系
- 关联面试题：[`JVM 内存区域`](../jvm-memory/README.md) — OutOfMemoryError 的内存模型背景

---

> 📅 2026-07-07 · 咬文嚼字 · Error vs Exception · ⭐⭐⭐（高频面试 + 异常处理基础）

← [返回 Java 咬文嚼字](../README.md)
