# VarHandle

## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

VarHandle 本应该很简单，VarHandle 是 Java 9 引入的变量句柄 API，提供了一种安全、高效的方式来访问变量、数组元素和对象字段。它是 `sun.misc.Unsafe` 的标准化替代方案，支持原子操作、内存屏障和 volatile 语义，为底层编程

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---


## 功能描述

VarHandle 是 Java 9 引入的变量句柄 API，提供了一种安全、高效的方式来访问变量、数组元素和对象字段。它是 `sun.misc.Unsafe` 的标准化替代方案，支持原子操作、内存屏障和 volatile 语义，为底层编程和并发工具开发提供了官方支持。

## 基本用法（最新，Java 21+）

```java
import java.lang.invoke.*;
import java.util.concurrent.atomic.*;

// 1. 字段 VarHandle - 替代反射和 Unsafe
public class Counter {
    private volatile int count;
    private static final VarHandle COUNT_HANDLE;

    static {
        try {
            MethodHandles.Lookup lookup = MethodHandles.lookup();
            COUNT_HANDLE = lookup.findVarHandle(Counter.class, "count", int.class);
        } catch (NoSuchFieldException | IllegalAccessException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    // 原子递增
    public void increment() {
        COUNT_HANDLE.getAndAdd(this, 1);
    }

    // volatile 读取
    public int getCount() {
        return (int) COUNT_HANDLE.getVolatile(this);
    }
}

// 2. 数组 VarHandle - 高性能数组元素访问
public class ArrayOperations {
    private static final VarHandle ARRAY_HANDLE;

    static {
        try {
            ARRAY_HANDLE = MethodHandles.arrayElementVarHandle(int[].class);
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    // 原子更新数组元素
    public static void atomicUpdate(int[] array, int index, int newValue) {
        ARRAY_HANDLE.setRelease(array, index, newValue);
    }

    // 原子比较并交换（CAS）
    public static boolean compareAndSet(int[] array, int index, int expected, int update) {
        return (boolean) ARRAY_HANDLE.compareAndSet(array, index, expected, update);
    }
}

// 3. 内存序操作
public class MemoryOrderExample {
    private static final VarHandle VALUE_HANDLE;
    private int value;

    static {
        try {
            VALUE_HANDLE = MethodHandles.lookup()
                .findVarHandle(MemoryOrderExample.class, "value", int.class);
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    // Plain 操作（无内存屏障，最快）
    public void plainWrite(int v) { VALUE_HANDLE.set(this, v); }

    // Opaque 操作（保证原子性和单变量顺序）
    public void opaqueWrite(int v) { VALUE_HANDLE.setOpaque(this, v); }

    // Release 操作（release 语义，用于发布共享数据）
    public void releaseWrite(int v) { VALUE_HANDLE.setRelease(this, v); }

    // Volatile 操作（最强保证）
    public void volatileWrite(int v) { VALUE_HANDLE.setVolatile(this, v); }
}

// 4. 原子操作替代 AtomicInteger
public class VarHandleCounter {
    private int count;
    private static final VarHandle HANDLE;

    static {
        try {
            HANDLE = MethodHandles.lookup()
                .findVarHandle(VarHandleCounter.class, "count", int.class);
        } catch (Exception e) { throw new ExceptionInInitializerError(e); }
    }

    // 等价于 AtomicInteger.getAndIncrement()
    public int getAndIncrement() {
        return (int) HANDLE.getAndIncrement(this);
    }

    // 等价于 AtomicInteger.compareAndSet()
    public boolean compareAndSet(int expect, int update) {
        return (boolean) HANDLE.compareAndSet(this, expect, update);
    }
}
```

## 变更历史表

| Java版本  | 新特性/增强内容                                              |
|---------|-------------------------------------------------------|
| Java 21 | VarHandle 在虚拟线程环境下进一步优化，支持更细粒度的内存序控制          |
| Java 17 | 改进 VarHandle 在值类型（Valhalla 项目）中的支持                 |
| Java 16 | 增强 `MethodHandles.arrayElementVarHandle()` 支持更多数组类型 |
| Java 9  | JEP 193: 引入 VarHandle API                               |

## 功能详细介绍

### 1. Java 9 - VarHandle 初始引入 (JEP 193)

作为 `java.lang.invoke` 包的一部分引入，核心概念：

- **替代 `sun.misc.Unsafe`**：提供标准化的底层变量访问 API
- **四种内存序**：
  - `set/get`：plain 操作，无内存屏障
  - `setOpaque/getOpaque`：保证原子性，不保证全局顺序
  - `setRelease/getAcquire`：release/acquire 语义，适用于生产者-消费者模式
  - `setVolatile/getVolatile`：volatile 语义，最强保证
- **原子操作**：`compareAndSet`、`getAndSet`、`getAndAdd` 等

### 2. Java 16-17 - 增强支持

- 支持更多数组类型的 `arrayElementVarHandle`
- 为 Project Valhalla 的值类型做准备

### 3. Java 21+ - 虚拟线程优化

VarHandle 的原子操作在虚拟线程环境中自动适配，无需修改代码。

## VarHandle vs 其他原子操作方案

| 方案              | 安全性 | 性能   | 灵活性  | 适用场景        |
|-----------------|-----|------|------|-------------|
| `synchronized`  | 最高  | 最低   | 中    | 复杂同步逻辑      |
| `AtomicInteger` | 高   | 高    | 低    | 简单计数器       |
| `VarHandle`     | 高   | 最高*  | 最高   | 框架开发、高性能场景  |
| `Unsafe`        | 最低  | 最高   | 最高   | 遗留代码，不推荐使用   |

*VarHandle 性能接近 Unsafe，且可被 JIT 优化

## 适用场景

1. **并发框架开发**：构建自定义锁、信号量等
2. **高性能数据结构**：无锁队列、跳表等
3. **序列化框架**：直接操作对象字段
4. **替代 Unsafe**：迁移遗留的 Unsafe 代码

## 总结

VarHandle 从 Java 9 引入以来，为 Java 提供了安全的高性能变量访问能力。它是 Unsafe 的标准化替代方案，支持多种内存序和原子操作，是并发工具开发和底层编程的核心 API。
