<!--
module:
  parent: java
  slug: java/version/ffi-api
  type: article
  category: 主模块子文章
  summary: Java FFM API（Java 22 预览）：替代 JNI 调用 native 库。
-->

# Foreign Function & Memory API (FFM)

## 引言：变更说明

Foreign Function & Memory API (FFM) 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 功能描述

Foreign Function & Memory API (FFM) 允许 Java 程序安全地调用原生代码（C/C++ 库）和操作堆外内存，是 JNI 的现代化替代方案。它通过 `Arena` 管理内存生命周期，通过 `Linker` 调用原生函数，通过 `MemorySegment` 和 `MemoryLayout` 描述内存布局，解决了 JNI 的复杂性和安全性问题。

## 基本用法（最新，Java 22+）

```java
import java.lang.foreign.*;
import java.lang.invoke.*;

// 1. 调用 C 标准库函数
public static void callCLibrary() throws Throwable {
    // 获取 C 标准库的 printf 函数符号
    Linker linker = Linker.nativeLinker();
    SymbolLookup stdlib = linker.defaultLookup();
    MethodHandle printf = linker.downcallHandle(
        stdlib.find("printf").orElseThrow(),
        FunctionDescriptor.of(JAVA_INT, ADDRESS, JAVA_INT)
    );

    // 分配原生内存并调用
    try (Arena arena = Arena.ofConfined()) {
        MemorySegment msg = arena.allocateUtf8String("Hello from Java! Value: %d\n");
        int result = (int) printf.invoke(msg, 42);
    }
}

// 2. 操作原生内存
public static void manipulateMemory() {
    try (Arena arena = Arena.ofConfined()) {
        // 分配 100 字节的原生内存
        MemorySegment segment = arena.allocate(100);

        // 写入数据
        MemoryLayout.OfInt intLayout = MemoryLayout.ValueLayout.JAVA_INT;
        segment.setAtIndex(intLayout, 0, 42);
        segment.setAtIndex(intLayout, 1, 100);

        // 读取数据
        int val = segment.getAtIndex(intLayout, 0);  // 42
    }
}

// 3. 使用 C 结构体（通过 GroupLayout）
public static void structExample() {
    // 定义 C 结构体布局：struct Point { int x; int y; double z; }
    GroupLayout pointLayout = MemoryLayout.structLayout(
        MemoryLayout.ValueLayout.JAVA_INT.withName("x"),
        MemoryLayout.ValueLayout.JAVA_INT.withName("y"),
        MemoryLayout.ValueLayout.JAVA_DOUBLE.withName("z")
    );

    try (Arena arena = Arena.ofConfined()) {
        MemorySegment point = arena.allocate(pointLayout);

        // 通过名称访问字段
        VarHandle xHandle = pointLayout.varHandle(MemoryLayout.PathElement.groupElement("x"));
        xHandle.set(point, 10);

        VarHandle yHandle = pointLayout.varHandle(MemoryLayout.PathElement.groupElement("y"));
        yHandle.set(point, 20);
    }
}

// 4. 回调函数（Java 函数传递给原生代码）
public static void callbackExample() throws Throwable {
    Linker linker = Linker.nativeLinker();

    // 创建 C 函数指针，指向 Java lambda
    FunctionDescriptor desc = FunctionDescriptor.of(JAVA_INT, JAVA_INT, JAVA_INT);
    SegmentAllocator allocator = SegmentAllocator.nativeAllocator(Arena.ofAuto());

    MemorySegment cmpFunc = linker.upcallStub(
        linker.downcallHandle(desc),
        (a, b) -> ((int) a) - ((int) b),  // Java lambda
        Arena.ofAuto(),
        desc
    );
}

// 5. 内存段视图（通过 MemorySegment 的 asSlice 操作）
public static void memoryViewExample() {
    try (Arena arena = Arena.ofConfined()) {
        MemorySegment segment = arena.allocate(64);

        // 创建不同视角的切片
        MemorySegment header = segment.asSlice(0, 16);
        MemorySegment payload = segment.asSlice(16, 48);

        // 零拷贝操作
        MemorySegment.copy(header, 0, payload, 0, 16);
    }
}
```

## 变更历史表

| Java版本  | 新特性/增强内容                                                |
|---------|---------------------------------------------------------|
| Java 22 | JEP 454: 外部函数和内存 API（正式特性）                             |
| Java 21 | JEP 442: 外部函数和内存 API（第三次预览）- Arena 生命周期管理改进          |
| Java 20 | JEP 434: 外部函数和内存 API（第二次预览）- 整合 Panama 项目的 FFM 和 Foreign-Memory API |
| Java 19 | JEP 424: 外部函数 API（预览）- Foreign Function API 和 Memory Access API 合并 |
| Java 18 | JEP 419: 外部函数 API（第二次孵化）                                   |
| Java 17 | JEP 412: 外部函数 API（孵化）+ JEP 413: 内存访问 API（第二次孵化）         |
| Java 16 | JEP 389: 外部链接器 API（孵化）+ JEP 393: 内存访问 API（第三次孵化）         |

## 功能详细介绍

### 1. Java 16-17 - 孵化起点

- **JEP 389**：引入 `MethodHandle` 方式的原生函数调用
- **JEP 393**：引入 `MemorySegment`、`MemoryAddress`、`MemoryLayout` 操作堆外内存
- **JEP 413**：内存访问 API 改进，引入 `VarHandle` 访问内存

此时 API 分为两个包：`jdk.incubator.foreign`（Foreign 和 Memory）

### 2. Java 18-19 - API 整合

- **JEP 419**：引入 `SymbolLookup` 简化原生符号查找
- **JEP 424**：将 Foreign Function API 和 Memory Access API 合并为统一的 FFM API，引入 `Linker` 作为原生交互的核心入口

### 3. Java 20-21 - 预览阶段

- **JEP 434（Java 20，第二次预览）**：引入 `Arena` 概念统一管理内存生命周期（替代 `ResourceScope`），提供 `ofConfined()`、`ofShared()`、`ofAuto()` 等不同作用域
- **JEP 442（Java 21，第三次预览）**：API 从 `jdk.incubator.foreign` 迁移到 `java.lang.foreign`，Arena 生命周期管理进一步改进

### 4. Java 22 - FFM API 转正 (JEP 454)

FFM API 成为标准特性，不再需要 `--enable-preview`。完整替代了 JNI 的核心使用场景。

## FFM API vs JNI 对比

| 特性         | JNI                | FFM API                |
|------------|--------------------|------------------------|
| 安全性       | 不安全，易导致 JVM 崩溃   | 内存区域管理，越界检测           |
| 易用性       | 需要编写 C 代码和 JNI glue | 纯 Java，无需 C 代码         |
| 性能         | 高                  | 相当或更好（MethodHandle 内联） |
| 内存管理      | 手动管理               | Arena 自动/受限/共享生命周期   |
| 编译依赖      | 需要编译 .so/.dll     | 直接加载运行时库               |

## 适用场景

1. **调用 C/C++ 库**：如 OpenSSL、libcurl、SQLite
2. **高性能序列化**：直接操作内存布局
3. **操作系统交互**：调用 POSIX API
4. **替代 JNI**：需要原生交互但不想编写 C 代码

## 总结

FFM API 从 Java 16 孵化到 Java 22 转正，为 Java 提供了安全、高效的原生代码调用和堆外内存操作能力，是 JNI 的现代化替代方案。纯 Java 即可调用原生库，无需编写 C 代码。

---

← [返回 功能版本变更历史](../README.md)
