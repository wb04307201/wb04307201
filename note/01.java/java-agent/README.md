# Java Agent

> `Java Agent`是一种特殊的`Java`程序，从`Java 5`开始支持，它可以在`Java`虚拟机（`JVM`）启动时或运行时加载，并且能够在不修改原始源代码的情况下对字节码进行操作。

## Java Agent 原理

> `Java Agent`的核心原理是通过`Java Instrumentation API`提供的机制，在类加载时或运行时动态修改字节码。  
> 这里涉及到主要的几个技术点：
> - `Instrumentation`接口
> - `Premain()`和`Agentmain()`方法

### Instrumentation

> `Instrumentation`是`Java SE 5`在`java.lang.instrument`包下引入的一个接口，主要用于字节码操作。它提供了以下几个关键功能：
> - **类转换**：允许在类加载时对字节码进行修改。
> - **代理类生成**：可以在运行时生成新的类。
> - **对象监控**：可以获取JVM中的对象信息，如内存使用情况。
> 
> `Instrumentation`接口提供了一组用于操作类和对象的方法，以下是一些主要的方法及其说明：

#### addTransformer

> 作用：添加一个 ClassFileTransformer，用于在类加载时对字节码进行修改。源码如下：
```java
/**
 * @param transformer：要移除的字节码转换器
 */
void addTransformer(ClassFileTransformer transformer);

/**
 * @param transformer：要移除的字节码转换器
 * @param canRetransform：指示是否允许重新转换已经加载的类
 */
void addTransformer(ClassFileTransformer transformer, boolean canRetransform);
```

#### removeTransformer

> 作用：移除一个之前添加的ClassFileTransformer。源码如下：
```java
/**
  * @param transformer：要移除的字节码转换器
  * @return 如果转换器被成功移除，则返回true，否则返回false
  */
boolean removeTransformer(ClassFileTransformer transformer);
```

#### retransformClasses

> 作用：重新转换已经加载的类。源码如下：
```java
/**
  * @param classes：要重新转换的类
  * @throws 如果某个类不能被修改，则抛出UnmodifiableClassException
  */
void retransformClasses(Class<?>... classes) throws UnmodifiableClassException;
```

#### redefineClasses

> 作用：重新定义已经加载的类。源码如下：
```java
/**
  * @param definitions：包含类的定义及其新的字节码
  * @throws 如果类不能被修改或未找到，则抛出相应的异常
  */
void redefineClasses(ClassDefinition... definitions) 
            throws ClassNotFoundException, UnmodifiableClassException;
```

#### isModifiableClass

> 作用：检查一个类是否可以被修改。源码如下：
```java
/**
  * @param theClass：要检查的类
  * @return 如果类可以被修改，则返回true，否则返回false
  */
boolean isModifiableClass(Class<?> theClass);
```

#### isRetransformClassesSupported

> 作用：检查当前JVM是否支持重新转换已经加载的类。源码如下：
```java
/**
  * @return 如果支持，则返回true，否则返回false
  */
boolean isRetransformClassesSupported();
```

#### isRedefineClassesSupported

> 作用：检查当前JVM是否支持重新定义已经加载的类。源码如下：
```java
/**
  * @return 如果支持，则返回true，否则返回false
  */
boolean isRedefineClassesSupported();
```

#### getAllLoadedClasses

> 作用：获取当前JVM中所有已经加载的类。源码如下：
```java
/**
  * @return 一个包含所有已加载类的数组
  */
Class<?>[] getAllLoadedClasses();
```

#### getInitiatedClasses

> 作用：获取由指定类加载器加载的所有类。源码如下：
```java
/**
  * @param loader：类加载器
  * @return 一个包含所有由指定类加载器加载的类的数组
  */
Class<?>[] getInitiatedClasses(ClassLoader loader);
```

#### getObjectSize

> 作用：获取指定对象的内存大小。源码如下：
```java
/**
  * @param objectToSize：要获取大小的对象
  * @return 对象的内存大小（以字节为单位）
  */
long getObjectSize(Object objectToSize);
```

### Premain 和 Agentmain

> `Java Agent`的入口是两个特殊的方法：`premain()`和`agentmain()`，这两个方法分别用于在 JVM启动时和运行时加载`Agent`。
> - **`premain`**：在`JVM`启动时执行。类似于`C`语言中的`main`函数。
> - **`agentmain`**：在`JVM`运行时通过`Attach`机制加载`Agent`。

```java
public class MyAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        // 在JVM启动时执行的代码
    }

    public static void agentmain(String agentArgs, Instrumentation inst) {
        // 在JVM运行时加载Agent时执行的代码
    }
}
```

## 手写 Java Agent

> 手写一个`Java Agent`主要包括以下 4个步骤：
> 1. **编写`Agent`类**：包含`premain()`或`agentmain()`方法。
> 2. **编写`MANIFEST.MF`文件**：指定`Agent`的入口类。
> 3. **打包成`JAR`文件**：包含`Agent`类和`MANIFEST`文件。
> 4. **使用`Agent`**：通过指定`JVM`参数或`Attach`机制加载`Agent`。
> 
> 下面以在 方法进入和退出时打印日志 为例，演示如何手写一个`Java Agent`。

### 编写 Agent类
> 首先，我们需要编写一个包含 premain()方法的 Agent类，示例代码如下：
```java
import java.lang.instrument.Instrumentation;
import java.lang.instrument.ClassFileTransformer;
import java.security.ProtectionDomain;

public class LoggingAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        inst.addTransformer(new LoggingTransformer());
    }
}

class MyTransformer implements ClassFileTransformer {
    @Override
    public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined,
                            ProtectionDomain protectionDomain, byte[] classfileBuffer) {
        if (className.equals("com/example/JavaAgentTest")) {
            // 使用 ASM或 Javassist进行字节码操作
            return addLogging(classfileBuffer);
        }
        return classfileBuffer;
    }

    private byte[] addLogging(byte[] classfileBuffer) {
        // 使用 ASM或 Javassist库进行字节码修改
        // 这里只是一个简单的示例，实际操作会复杂得多
        return classfileBuffer;
    }
}
```

### 编写 MANIFEST.MF文件
> 接着，我们需要在 MANIFEST.MF 文件中指定 Agent 的入口类，如下信息：
```manifest
Manifest-Version: 1.0
Premain-Class: LoggingAgent
```

### 打包成 JAR文件
> 然后，将 Agent 类和 MANIFEST.MF 文件打包成一个 JAR 文件，指令如下：
```shell
jar cmf MANIFEST.MF loggingagent.jar LoggingAgent.class LoggingTransformer.class
```

### 使用 Agent
> 最后，通过指定 JVM 参数来加载 Agent，指令如下：
```shell
java -javaagent:loggingagent.jar -jar myapp.jar
```
> 或者通过 Attach 机制在运行时加载 Agent，示例代码如下：
```java
import com.sun.tools.attach.VirtualMachine;

public class AttachAgent {
    public static void main(String[] args) throws Exception {
        String pid = args[0]; // 目标 JVM 的进程ID
        VirtualMachine vm = VirtualMachine.attach(pid);
        vm.loadAgent("path/to/myagent.jar");
        vm.detach();
    }
}
```

## 验证

> 最后写一个测试类来验证上面的 Java Agent：
```java
package com.example;
public class JavaAgentTest {
    public void methodTest() {
        System.out.println("Hello, World!");
    }

    public static void main(String[] args) {
        JavaAgentTest test = new JavaAgentTest();
        test.methodTest();
    }
}
```

## Java Agent使用场景

> Java Agent 在实际应用中有很多重要的使用场景，主要包括性能监控、调试、日志增强、安全检查、AOP等，以下是一些具体的应用场景及其详细说明。

### 性能监控

> 通过Java Agent，可以在不修改应用代码的情况下，动态地收集性能指标，如方法执行时间、内存使用情况、线程状态等。
> 
> 比如，许多 Java Profiling工具，如 VisualVM、YourKit、JProfiler等，都使用 Java Agent 来收集性能数据。这些工具通过 Agent 动态注入代码来记录方法调用、CPU 使用率、内存分配等信息。

### 调试

> Java Agent 可以用于增强调试功能，在运行时收集更多的调试信息。
> 
> 在调试复杂问题时，可能需要额外的日志信息，通过Java Agent，可以在不修改原始代码的情况下，动态地添加日志语句。

### 日志增强

> 日志是软件开发中非常重要的一部分，通过Java Agent可以在不修改代码的情况下，增强日志功能。
> - **全局日志**：通过`Java Agent`，可以在每个方法入口和出口处添加日志记录，捕获方法调用的参数和返回值，方便问题排查。
> - **动态配置**：`Java Agent`可以根据配置文件动态调整日志级别和日志内容，而不需要重启应用程序。

### 安全检查方法

> - **权限检查**：在方法调用前，`Java Agent`可以动态检查调用者的权限，防止未授权的操作
> - **数据校验**：在数据处理前，`Java Agent`可以动态添加数据校验逻辑，确保输入数据的合法性和完整性。

### AOP

> AOP（面向切面编程） 是一种编程范式，通过Java Agent可以实现动态AOP，增强代码的灵活性和可维护性。
> - **事务管理**：通过`Java Agent`，可以在方法调用前后动态添加事务管理逻辑，确保数据的一致性。
> - **缓存**：在方法调用前，`Java Agent`可以检查缓存，如果有缓存数据则直接返回，避免重复计算。

### 其他应用

> - **热部署**：`Java Agent`可以实现类的热替换，支持应用程序在不重启的情况下更新代码。
> - **测试覆盖率**：通过`Java Agent`，可以动态收集测试覆盖率信息，生成覆盖率报告，帮助开发者了解测试的完整性。

## Java Agent框架

### Javassist

> Javassist 是一个高层次的Java字节码操作库，提供了简单易用的API，允许开发者通过类似于操作Java源代码的方式来操作字节码。  
> Javassist 的特点：
> - **易于使用**：提供了高层次的API，简化了字节码操作。
> - **灵活**：支持动态生成和修改类。
> - **广泛应用**：被许多Java框架和工具使用，如Hibernate、JBoss等。

### AspectJ

> AspectJ 是一个功能强大的AOP（面向切面编程）框架，允许开发者通过定义切面（Aspect）来增强Java代码。AspectJ可以通过Java Agent来实现动态AOP。  
> AspectJ 的特点：
> - **AOP支持**：提供了强大的AOP支持，简化了横切关注点的处理。
> - **灵活**：支持静态织入和动态织入。
> - **广泛应用**：被许多企业级应用和框架使用，如Spring AOP。

### Spring Instrument

> Spring Instrument 是Spring框架提供的一个工具，用于在运行时增强Spring应用的功能。它使用Java Agent来实现类加载时的字节码操作，常用于Spring AOP和Spring Load-Time Weaving（LTW）。  
> Spring Instrument 的特点：
> - **与 Spring集成**：无缝集成到 Spring框架中，简化了 Spring应用的增强。
> - **支持 LTW**：支持运行时织入，增强 Spring应用的动态功能。
> - **易于配置**：通过 Spring配置文件或注解进行配置。

### ASM

> ASM 是一个低级别的 Java字节码操作库，功能强大但API相对复杂。它允许开发者以最细粒度的方式操作字节码。  
> ASM的特点：
> - **高效**：直接操作字节码，性能极高。
> - **灵活**：支持复杂的字节码修改和生成。
> - **广泛应用**：被许多其他字节码库和框架所使用，如ByteBuddy、CGLIB等。

### 链路追踪框架
> 链路追踪（Distributed Tracing）是分布式系统中用于追踪请求流经不同服务的过程的技术，为了实现这一点，许多链路追踪框架利用了 Java Agent 技术来动态地注入代码，从而在不修改应用程序代码的情况下实现对请求的追踪，这种方法通常被称为“字节码增强”或“字节码注入”。  
> 常见的链路追踪框架有：Apache SkyWalking，Elastic APM，Pinpoint，Zipkin，Jaeger 等，它们内部通过 Java Agent 技术实现了对应用程序的无侵入式监控。
