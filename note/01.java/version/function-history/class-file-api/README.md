# Class-File API

## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

Class-File API 本应该很简单，Class-File API 是 Java 24 转正的标准化类文件处理 API，提供对 Java 字节码文件的解析、生成和转换能力。它替代了过去对第三方库（如 ASM、BCEL）的依赖，为框架开发、代码生成工具和 AOP 实现提供了官方标

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---


## 功能描述

Class-File API 是 Java 24 转正的标准化类文件处理 API，提供对 Java 字节码文件的解析、生成和转换能力。它替代了过去对第三方库（如 ASM、BCEL）的依赖，为框架开发、代码生成工具和 AOP 实现提供了官方标准方案。

## 基本用法（最新，Java 24+）

```java
import java.lang.classfile.*;
import java.lang.classfile.attribute.*;
import java.lang.classfile.instruction.*;
import static java.lang.classfile.ClassFile.*;

// 1. 解析类文件
byte[] bytes = Files.readAllBytes(Path.of("MyClass.class"));
ClassFile cf = ClassFile.of();
ClassModel classModel = cf.parse(bytes);

System.out.println("Class name: " + classModel.thisClass().asInternalName());
classModel.methods().forEach(mm ->
    System.out.println("Method: " + mm.methodName()));

// 2. 构建新类文件 - 移除 debug 开头的方法
byte[] newBytes = cf.build(classModel.thisClass().asSymbol(),
    classBuilder -> {
        for (ClassElement ce : classModel) {
            if (!(ce instanceof MethodModel mm
                    && mm.methodName().stringValue().startsWith("debug"))) {
                classBuilder.with(ce);
            }
        }
    });

// 3. 从零构建类文件
byte[] helloBytes = ClassFile.of().build(
    "com.example.Hello",
    cb -> cb.with(
        MethodBuilder.of("greet", MethodFlags.PUBLIC_STATIC,
            "(Ljava/lang/String;)V",
            mb -> mb.with(
                CodeBuilder.of(mb,
                    code -> {
                        code.getstatic(System.out)
                            .ldc("Hello, ")
                            .aload(0)
                            .invokevirtual(String.concat)
                            .invokevirtual(System.out.getClass().getMethod("println", String.class))
                            .return_();
                    })
            )
        )
    )
);

// 4. 转换类文件 - 添加注解
byte[] annotatedBytes = cf.transform(classModel,
    classBuilder -> {
        classBuilder.with(classModel);
        classBuilder.with(RuntimeVisibleAnnotationsAttribute.of(
            Annotation.of(Deprecated.class)));
    });
```

## 变更历史表

| Java版本  | 新特性/增强内容                                            |
|---------|-----------------------------------------------------|
| Java 24 | JEP 484: Class-File API 转正为标准特性                      |
| Java 23 | JEP 466: Class-File API 第二次预览 - API 微调和功能增强            |
| Java 22 | JEP 457: Class-File API 首次预览 - 引入标准化的类文件处理 API     |
| Java 1  | java.lang.Class 和反射 API，提供基础的运行时类信息访问              |

## 功能详细介绍

### 1. Java 1-21 - 反射和第三方字节码库

在 Class-File API 出现之前，Java 开发者依赖以下方式处理类文件：

- **反射 API**（`java.lang.reflect.*`）：运行时访问类信息，但无法生成或修改字节码
- **第三方库**：ASM、BCEL、Javassist 等提供字节码操作能力，但 API 各异且非标准
- **`jdk.internal.org.objectweb.asm`**：JDK 内部使用了 ASM，但不对外公开

### 2. Java 22 - Class-File API 首次预览 (JEP 457)

首次引入标准化的类文件处理 API，核心组件：

- **`ClassFile`**：操作入口，提供 parse、build、transform 等方法
- **`ClassModel`**：解析后的类文件模型，只读访问
- **`ClassBuilder`**：构建新类文件的 DSL
- **`CodeBuilder`**：构建方法体字节码的 DSL
- **`ClassElement`/`MethodModel`/`FieldModel`**：类结构元素

包结构：`java.lang.classfile.*`（标准）和 `jdk.incubator.classfile.*`（孵化器，已废弃）

### 3. Java 23 - Class-File API 第二次预览 (JEP 466)

根据用户反馈进行 API 微调：
- 简化 `CodeBuilder` 的指令生成方式
- 改进属性（Attribute）的构建 API
- 优化大文件的解析性能

### 4. Java 24 - Class-File API 转正 (JEP 484)

从预览特性转为标准特性，API 稳定。主要优势：

1. **官方标准**：不再依赖第三方库
2. **API 设计**：现代化的 DSL 风格 API
3. **不可变模型**：`ClassModel` 是只读的，避免意外修改
4. **转换安全**：`transform` 方法基于已有模型构建，保证字节码结构正确

## 适用场景

1. **框架开发**：Spring、Hibernate 等框架的字节码增强
2. **代码生成**：Protocol Buffers、Lombok 等工具
3. **AOP 实现**：方法拦截、日志注入
4. **字节码分析**：静态分析工具、代码质量检测

## 总结

Class-File API 从 Java 22 预览到 Java 24 成熟，为 Java 提供了标准化的字节码处理能力，填补了 JDK 长久以来在官方字节码操作 API 上的空白。
