<!--
module:
  parent: java
  slug: java/java-agent
  type: article
  category: 主模块子文章
  summary: Java Agent
-->

# Java Agent

`Java Agent` 是 JVM 提供的一种字节码增强机制，从 Java 5 开始引入。它允许在不修改原始源代码的前提下，于类加载时或运行时动态修改类的字节码，从而实现性能监控、链路追踪、热更新、AOP 等能力。

所有主流 APM 工具（SkyWalking、Elastic APM、Pinpoint）、Profiler 工具（JProfiler、VisualVM）、Mock 框架（Mockito）、ORM 框架（Hibernate）等，底层都依赖 Java Agent 技术。

---
## 引言：反直觉代码
Java Agent 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 核心原理

Java Agent 的工作机制可以概括为三个要素：

| 要素 | 说明 |
|------|------|
| **Instrumentation API** | JVM 提供的字节码操作接口，Agent 通过它注册转换器、触发类重定义 |
| **入口方法** | `premain`（启动时加载）和 `agentmain`（运行时 Attach 加载） |
| **MANIFEST.MF** | JAR 包的清单文件，声明 Agent 入口类和能力属性 |

### 执行时序

```
premain 模式:
  JVM 启动 → 加载 Agent JAR → 执行 premain() → 注册 ClassFileTransformer
  → 应用类加载时触发 transform() → 执行 main()

agentmain 模式:
  JVM 运行中 → 外部进程 Attach → 加载 Agent JAR → 执行 agentmain()
  → 注册 ClassFileTransformer → 主动触发 retransformClasses()
```

---

## Instrumentation API 详解

`java.lang.instrument.Instrumentation` 是 Agent 与 JVM 交互的核心接口。以下方法按功能分为四组：

### 转换器管理

```java
// 注册转换器，类加载时会触发 transform() 回调
void addTransformer(ClassFileTransformer transformer);

// canRetransform=true 时，转换器可对已加载的类生效（需配合 retransformClasses）
void addTransformer(ClassFileTransformer transformer, boolean canRetransform);

// 移除已注册的转换器
boolean removeTransformer(ClassFileTransformer transformer);
```

### 类操作

```java
// 重新触发已加载类的转换流程（走 transform 链路）
void retransformClasses(Class<?>... classes) throws UnmodifiableClassException;

// 用全新的字节码直接替换已加载的类定义
void redefineClasses(ClassDefinition... definitions)
        throws ClassNotFoundException, UnmodifiableClassException;

// 判断某个类是否允许被修改
boolean isModifiableClass(Class<?> theClass);
```

**retransform vs redefine 的本质区别：**

| 对比项 | retransformClasses | redefineClasses |
|--------|-------------------|-----------------|
| 工作方式 | 重新走 transform 链路，由已注册的转换器生成新字节码 | 直接传入新的字节码进行替换 |
| 典型场景 | Attach 模式下让已有转换器对已加载类生效 | 热部署、IDE 热替换 |
| 对字节码的限制 | 不能增减方法/字段、不能改方法签名 | 同样有限制，但更灵活 |
| 需要转换器 | 是（依赖已注册的 ClassFileTransformer） | 否（直接提供字节码） |

### 能力检查

```java
// 是否支持 retransform（需要在 MANIFEST 中声明 Can-Retransform-Classes）
boolean isRetransformClassesSupported();

// 是否支持 redefine（需要在 MANIFEST 中声明 Can-Redefine-Classes）
boolean isRedefineClassesSupported();

// 是否支持设置 native 方法前缀
boolean isNativeMethodPrefixSupported();
```

### 类发现与工具

```java
// 获取 JVM 中所有已加载的类
Class<?>[] getAllLoadedClasses();

// 获取指定 ClassLoader 加载的所有类
Class<?>[] getInitiatedClasses(ClassLoader loader);

// 获取对象在堆中的近似大小（字节），用于内存分析
long getObjectSize(Object objectToSize);

// 追加 JAR 到 Bootstrap ClassLoader 的搜索路径（Java 8 及之前）
void appendToBootstrapClassLoaderSearch(JarFile jarfile);

// 追加 JAR 到 System ClassLoader 的搜索路径
void appendToSystemClassLoaderSearch(JarFile jarfile);
```

### Java 9+ 新增方法

Java 9 引入模块系统后，Instrumentation 增加了模块相关方法：

```java
// 让目标模块读取另一个模块（解决模块间访问限制）
void addModuleReads(Module from, Module to);

// 将模块的包导出给另一个模块（甚至所有未命名模块）
void addExports(Module from, String pkg, Module to);
// to 传 null 表示导出给所有未命名模块

// 将 JAR 追加到指定模块的引导搜索路径
void appendToBootstrapModuleSearch(Module from, JarFile jarfile);

// 让 Agent 能设置 native 方法的前缀（用于 native 方法拦截）
boolean isSetNativeMethodPrefixSupported();
void setNativeMethodPrefix(ClassFileTransformer transformer,
                           String prefix, Class<?>... classes);
```

---

## 入口方法：premain 与 agentmain

### premain —— 启动时加载

在 JVM 启动时、`main()` 方法执行之前被调用。

```java
// 完整签名（两个参数）
public static void premain(String agentArgs, Instrumentation inst)

// 简化签名（仅 Instrumentation）
public static void premain(String agentArgs, Instrumentation inst)
```

使用方式：
```shell
java -javaagent:my-agent.jar -jar my-app.jar
```

### agentmain —— 运行时加载

通过 Attach API 在 JVM 运行过程中动态加载 Agent。

```java
public static void agentmain(String agentArgs, Instrumentation inst)
```

使用方式：
```java
// 在另一个 JVM 进程中执行
VirtualMachine vm = VirtualMachine.attach(pid);
vm.loadAgent("/path/to/my-agent.jar");  // 同步加载
vm.loadAgent("/path/to/my-agent.jar", "key=value");  // 带参数
vm.detach();
```

> **注意：** `VirtualMachine` 类在 Java 8 及之前位于 `tools.jar` 中（需手动引入），Java 9 以后被模块化到 `jdk.attach` 模块中。Maven 依赖写法不同，见后文。

### 两种模式的选择

| 维度 | premain | agentmain |
|------|---------|-----------|
| 加载时机 | JVM 启动时 | JVM 运行时 |
| 是否需要重启 | 是 | 否 |
| 覆盖范围 | 所有类（含尚未加载的） | 仅已加载的类（需 retransform） |
| 典型用途 | 监控、追踪、AOP | 热修复、线上诊断 |

---

## MANIFEST.MF 属性详解

Agent JAR 的 `META-INF/MANIFEST.MF` 必须声明以下属性：

| 属性 | 说明 | 必需 |
|------|------|------|
| `Premain-Class` | premain 入口类的全限定名 | premain 模式必需 |
| `Agent-Class` | agentmain 入口类的全限定名 | agentmain 模式必需 |
| `Can-Redefine-Classes` | 是否支持 redefine，取值 `true`/`false` | 需要 redefine 时 |
| `Can-Retransform-Classes` | 是否支持 retransform，取值 `true`/`false` | 需要 retransform 时 |
| `Can-Set-Native-Method-Prefix` | 是否支持设置 native 方法前缀 | 需要拦截 native 方法时 |
| `Boot-Class-Path` | 追加到 Bootstrap ClassLoader 的 JAR 路径（空格分隔） | 需要引导类可见时 |

> `Premain-Class` 和 `Agent-Class` 可以是同一个类，一个 Agent 可同时支持两种加载模式。

### Maven 自动生成 MANIFEST

推荐使用 `maven-jar-plugin` 自动生成，避免手写出错：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-jar-plugin</artifactId>
    <configuration>
        <archive>
            <manifestEntries>
                <Premain-Class>com.example.MyAgent</Premain-Class>
                <Agent-Class>com.example.MyAgent</Agent-Class>
                <Can-Redefine-Classes>true</Can-Redefine-Classes>
                <Can-Retransform-Classes>true</Can-Retransform-Classes>
            </manifestEntries>
        </archive>
    </configuration>
</plugin>
```

---

## 手写 Java Agent：完整教程

以实现「方法执行耗时统计」为例，演示从零构建一个可运行的 Java Agent。

### 第一步：编写 Agent 入口类

```java
package com.example.agent;

import java.lang.instrument.Instrumentation;

public class MonitorAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        System.out.println("[MonitorAgent] Agent 已启动");
        inst.addTransformer(new MonitorTransformer(), true);
    }
}
```

> 第二个参数 `true` 表示该转换器支持对已加载的类进行 retransform。

### 第二步：编写 ClassFileTransformer

这里使用 Javassist 进行字节码增强：

```java
package com.example.agent;

import javassist.*;
import java.lang.instrument.ClassFileTransformer;
import java.security.ProtectionDomain;

public class MonitorTransformer implements ClassFileTransformer {

    @Override
    public byte[] transform(ClassLoader loader,
                            String className,
                            Class<?> classBeingRedefined,
                            ProtectionDomain protectionDomain,
                            byte[] classfileBuffer) {

        // className 格式为 "com/example/MyClass"（斜杠分隔）
        if (className == null || !className.startsWith("com/example")) {
            return null; // 返回 null 表示不修改此类
        }

        // 跳过 Agent 自身的类，避免无限递归
        if (className.startsWith("com/example/agent")) {
            return null;
        }

        try {
            // 将 "com/example/MyClass" 转为 "com.example.MyClass"
            String dotClassName = className.replace('/', '.');

            // 关键：使用正确的 ClassPool 和 ClassPath
            ClassPool classPool = new ClassPool();
            if (loader != null) {
                classPool.insertClassPath(new LoaderClassPath(loader));
            } else {
                classPool.insertClassPath(new ClassClassPath(Object.class));
            }

            CtClass ctClass = classPool.get(dotClassName);
            CtMethod[] methods = ctClass.getDeclaredMethods();

            for (CtMethod method : methods) {
                // 跳过抽象方法、native 方法、构造器
                int modifiers = method.getModifiers();
                if (javassist.Modifier.isAbstract(modifiers)
                        || javassist.Modifier.isNative(modifiers)) {
                    continue;
                }

                String methodName = method.getLongName();
                method.addLocalVariable("_start", CtClass.longType);
                method.insertBefore("_start = System.currentTimeMillis();");
                method.insertAfter(
                    "System.out.println(\"[Monitor] " + methodName +
                    " 耗时: \" + (System.currentTimeMillis() - _start) + \" ms\");"
                );
            }

            return ctClass.toBytecode();

        } catch (Exception e) {
            // 转换失败不应影响应用启动，仅打印日志
            System.err.println("[MonitorTransformer] 转换 " + className + " 失败: " + e.getMessage());
        }

        return null;
    }
}
```

> **关键修复：** 原教程直接使用 `ClassPool.getDefault()`，在 Spring Boot 等复杂类加载器环境下会找不到类。正确做法是根据 `loader` 参数创建对应的 `ClassPool`。

### 第三步：构建 JAR

使用 Maven 插件自动生成 MANIFEST（见上文），或直接打包：

```shell
# 手动指定 MANIFEST
jar cmf MANIFEST.MF monitor-agent.jar -C target/classes .

# 或使用 Maven
mvn clean package
```

### 第四步：运行

```shell
java -javaagent:monitor-agent.jar -jar my-app.jar
```

### 预期输出

```
[MonitorAgent] Agent 已启动
[Monitor] com.example.service.UserService.getUser 耗时: 12 ms
[Monitor] com.example.controller.DemoController.index 耗时: 1008 ms
```

---

## ClassFileTransformer 深入理解

### transform 方法的返回值语义

| 返回值 | 含义 |
|--------|------|
| `null` | 不对该类做任何修改（**推荐做法**，JVM 直接使用原始字节码） |
| 原始 `classfileBuffer` | 等同于未修改，但产生了不必要的数组拷贝 |
| 新的 `byte[]` | 使用新字节码替换原始字节码 |
| 抛出 `IllegalClassFormatException` | 转换失败，该类加载失败 |

> **最佳实践：** 不需要修改时返回 `null`，而非返回原始 buffer。

### loader 参数的重要性

`transform()` 的第一个参数 `ClassLoader loader` 是转换该类的类加载器。理解它至关重要：

- **普通 Java 应用**：通常是 `AppClassLoader`
- **Spring Boot**：使用 `LaunchedURLClassLoader` 加载嵌套 JAR 中的类
- **Tomcat 等 Web 容器**：每个 Web 应用有独立的 `WebappClassLoader`
- **Bootstrap 类**：`loader` 为 `null`（由 Bootstrap ClassLoader 加载）

如果无视 `loader` 而直接用 `ClassPool.getDefault()`，在多 ClassLoader 环境下会报 `NotFoundException`。

---

## Attach API 详解

Attach API 允许在 JVM 运行时动态加载 Agent，实现"无侵入式"线上诊断。

### 核心类

```
jdk.internal.agent (Java 9+)  /  sun.tools.attach (实现)
  └── VirtualMachine (API 入口)
      ├── attach(pid)          → 连接到目标 JVM
      ├── loadAgent(path)      → 加载 Agent JAR
      ├── loadAgentLibrary(name, args) → 加载 native agent
      ├── detach()             → 断开连接
      └── list()               → 列出所有可连接的 JVM 实例
```

### Java 8 与 Java 9+ 的依赖差异

**Java 8（需手动引入 tools.jar）：**
```xml
<dependency>
    <groupId>com.sun</groupId>
    <artifactId>tools</artifactId>
    <version>1.8</version>
    <scope>system</scope>
    <systemPath>${java.home}/../lib/tools.jar</systemPath>
</dependency>
```

**Java 9+（模块系统）：**
```xml
<dependency>
    <groupId>net.java.dev.jna</groupId>
    <artifactId>jna</artifactId>
    <version>5.14.0</version>
</dependency>
<dependency>
    <groupId>net.java.dev.jna</groupId>
    <artifactId>jna-platform</artifactId>
    <version>5.14.0</version>
</dependency>
```

> Java 9 以后 `jdk.attach` 模块默认不可用，需要通过 `--add-exports` 开放访问。更简单的方案是使用第三方库如 `byte-buddy-agent`，它内部处理了跨版本兼容。

### 列出可 Attach 的 JVM

```java
import com.sun.tools.attach.VirtualMachineDescriptor;
import java.util.List;

public class ListJvms {
    public static void main(String[] args) {
        List<VirtualMachineDescriptor> vms = VirtualMachine.list();
        for (VirtualMachineDescriptor vm : vms) {
            System.out.printf("PID: %s, 名称: %s%n", vm.id(), vm.displayName());
        }
    }
}
```

---

## Java Agent 的局限性

Java Agent 虽然强大，但并非无所不能：

1. **不能修改类的基本结构**：不能新增/删除方法、不能新增/删除字段、不能修改方法签名
2. **不能转换某些类**：数组类、原始类型类、部分 JDK 核心类不可被转换
3. **Bootstrap 类限制**：默认不能转换由 Bootstrap ClassLoader 加载的类，需特殊配置
4. **已初始化的静态状态不受影响**：redefine 后类的静态变量保持原值，静态初始化块不会重新执行
5. **方法调用栈中的方法不能 redefine**：如果某方法正在执行中（在调用栈上），则不能被 redefine
6. **性能开销**：字节码增强会引入额外的方法调用，高频场景需权衡

---

## 使用场景

| 场景 | 说明 | 代表工具 |
|------|------|---------|
| **性能监控** | 无侵入采集方法耗时、内存、线程等指标 | JProfiler, VisualVM, Arthas |
| **分布式链路追踪** | 自动注入 TraceId，追踪请求在微服务间的流转 | SkyWalking, Pinpoint, Elastic APM |
| **AOP / 横切逻辑** | 在编译后、运行前织入切面逻辑 | AspectJ LTW, Spring Instrument |
| **Mock / 测试** | 运行时替换方法实现用于测试隔离 | Mockito (ByteBuddy), PowerMock |
| **热更新 / 热修复** | 线上不重启修复 bug | Arthas redefine, JRebel |
| **测试覆盖率** | 注入代码统计行/分支覆盖情况 | JaCoCo, Cobertura |
| **安全增强** | 动态插入权限校验、数据脱敏 | 各企业自研安全 Agent |
| **日志增强** | 自动为方法添加入参/出参日志 | 自研 Agent |

---

## 常用字节码操作库

### ASM（底层、高性能）

- **定位**：最底层的字节码操作库，直接读写 class 文件格式
- **特点**：性能极高、API 复杂、学习曲线陡峭
- **用户**：Spring、Hibernate、Groovy、Kotlin 编译器等
- **适用场景**：追求极致性能的生产级 Agent

### Javassist（高层、易用）

- **定位**：通过类似 Java 源码的方式操作字节码
- **特点**：API 简单直观、支持源码级字符串注入
- **适用场景**：快速开发、对性能要求不极端的场景

### ByteBuddy（现代、推荐）

- **定位**：当前最主流的动态字节码生成库，API 流式设计
- **特点**：类型安全、链式 API、内置 Agent 构建器、完善测试
- **用户**：Mockito、Hibernate、Spring Boot 3.x、Jackson、Log4j 2.x
- **适用场景**：**新建 Agent 项目的首选**

```java
// ByteBuddy 示例：方法耗时统计
new AgentBuilder.Default()
    .type(ElementMatchers.nameStartsWith("com.example"))
    .transform((builder, typeDescription, classLoader, module) ->
        builder.visit(Advice.to(MonitorAdvice.class)
            .on(ElementMatchers.isMethod())))
    .installOn(instrumentation);
```

### AspectJ（AOP 导向）

- **定位**：成熟的 AOP 框架，支持编译期/编译后/加载时织入
- **特点**：通过 `@Aspect` 注解定义切面，Spring AOP 的底层实现之一
- **适用场景**：已有 AspectJ 使用习惯的团队

### Spring Instrument

- **定位**：Spring 框架提供的 Agent 实现
- **特点**：专为 Spring 的 LTW（Load-Time Weaving）设计
- **适用场景**：Spring 项目中需要 @Configurable 等特性时

---

## 实战案例

详见 [api/README.md](api/README.md) —— 完整的 API 接口调用耗时统计 Agent 实现。
