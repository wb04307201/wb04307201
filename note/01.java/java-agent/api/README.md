# 实战：统计 API 接口调用耗时

本文档演示如何从零构建一个可运行的 Java Agent，实现方法级别的耗时统计。

> 前置知识请参阅 [Java Agent 核心文档](../README.md)

---
## 引言：反直觉代码

实战：统计 API 接口调用耗时 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、项目结构

```
monitor-agent/
├── pom.xml
└── src/main/java/com/pack/agent/
    ├── MonitorAgent.java          # Agent 入口
    └── MonitorTransformer.java    # 字节码转换器
```

---

## 二、添加依赖

使用 Javassist 进行字节码操作：

```xml
<dependency>
    <groupId>org.javassist</groupId>
    <artifactId>javassist</artifactId>
    <version>3.30.2-GA</version>
</dependency>
```

---

## 三、编写 Transformer

`ClassFileTransformer` 是字节码转换的核心回调接口。

```java
package com.pack.agent;

import javassist.*;
import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.IllegalClassFormatException;
import java.security.ProtectionDomain;

/**
 * 方法耗时统计转换器
 *
 * 对 com.pack 及其子包下所有类的所有方法，注入耗时统计代码。
 */
public class MonitorTransformer implements ClassFileTransformer {

    @Override
    public byte[] transform(ClassLoader loader,
                            String className,
                            Class<?> classBeingRedefined,
                            ProtectionDomain protectionDomain,
                            byte[] classfileBuffer) throws IllegalClassFormatException {

        // className 格式为 "com/pack/MyClass"，不是 "com.pack.MyClass"
        if (className == null) {
            return null;
        }

        // 只拦截 com.pack 及其子包
        String dotClassName = className.replace('/', '.');
        if (!dotClassName.startsWith("com.pack")) {
            return null;
        }

        // 排除 Agent 自身，防止无限递归
        if (dotClassName.startsWith("com.pack.agent")) {
            return null;
        }

        try {
            // 正确做法：根据 loader 创建 ClassPool
            // 而不是直接使用 ClassPool.getDefault()
            ClassPool classPool = new ClassPool();
            if (loader != null) {
                classPool.insertClassPath(new LoaderClassPath(loader));
            } else {
                // loader == null 表示 Bootstrap ClassLoader 加载的类
                classPool.insertClassPath(new ClassClassPath(Object.class));
            }

            CtClass ctClass = classPool.get(dotClassName);
            CtMethod[] methods = ctClass.getDeclaredMethods();

            for (CtMethod method : methods) {
                int modifiers = method.getModifiers();
                // 跳过抽象方法和 native 方法
                if (javassist.Modifier.isAbstract(modifiers)
                        || javassist.Modifier.isNative(modifiers)) {
                    continue;
                }

                String methodName = method.getName();

                // 添加局部变量
                method.addLocalVariable("start", CtClass.longType);

                // 方法入口插入：记录开始时间
                method.insertBefore("start = System.currentTimeMillis();");

                // 方法出口插入：打印耗时
                // insertAfter 会在所有 return 语句前插入，包括异常抛出的情况
                method.insertAfter(
                    "System.out.println(\"" + methodName +
                    " 耗时: \" + (System.currentTimeMillis() - start) + \" ms\");"
                );
            }

            return ctClass.toBytecode();

        } catch (Exception e) {
            // 转换失败不应影响应用启动
            System.err.println("[MonitorTransformer] 转换 " + dotClassName + " 失败: " + e.getMessage());
            e.printStackTrace();
        }

        return null;
    }
}
```

> **为什么不直接用 `ClassPool.getDefault()`？**
>
> `ClassPool.getDefault()` 使用系统 ClassPath 搜索类，但在 Spring Boot（`LaunchedURLClassLoader`）、
> Tomcat（`WebappClassLoader`）等多 ClassLoader 环境下，被转换的类不在系统 ClassPath 中，
> 会抛出 `NotFoundException`。
>
> 正确做法是通过 `transform()` 回调中拿到的 `loader` 参数来创建 `ClassPool`。

---

## 四、编写 Agent 入口

```java
package com.pack.agent;

import java.lang.instrument.Instrumentation;

/**
 * Agent 入口类
 *
 * 执行顺序：premain() → 应用 main()
 */
public class MonitorAgent {

    /**
     * JVM 启动时由 -javaagent 参数触发
     *
     * @param agentArgs      -javaagent:xxx=后面的参数，如 -javaagent:agent.jar=config=value
     * @param instrumentation JVM 提供的 Instrumentation 实例
     */
    public static void premain(String agentArgs, Instrumentation instrumentation) {
        System.out.println("[MonitorAgent] === Agent 已启动 ===");
        System.out.println("[MonitorAgent] 参数: " + agentArgs);

        // 注册转换器，第二个参数 true 表示支持 retransform
        instrumentation.addTransformer(new MonitorTransformer(), true);
    }
}
```

---

## 五、构建 JAR

### 方式一：Maven 插件（推荐）

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-jar-plugin</artifactId>
            <configuration>
                <archive>
                    <manifestEntries>
                        <Premain-Class>com.pack.agent.MonitorAgent</Premain-Class>
                        <Can-Redefine-Classes>true</Can-Redefine-Classes>
                        <Can-Retransform-Classes>true</Can-Retransform-Classes>
                    </manifestEntries>
                </archive>
            </configuration>
        </plugin>

        <!-- 将依赖打包进 fat jar -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-shade-plugin</artifactId>
            <version>3.5.1</version>
            <executions>
                <execution>
                    <phase>package</phase>
                    <goals><goal>shade</goal></goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

```shell
mvn clean package
# 输出: target/monitor-agent-1.0.jar（包含 Javassist 依赖）
```

### 方式二：手动打包

```shell
# 1. 编译
javac -cp javassist.jar -d out src/com/pack/agent/*.java

# 2. 创建 MANIFEST.MF
cat > MANIFEST.MF << 'EOF'
Manifest-Version: 1.0
Premain-Class: com.pack.agent.MonitorAgent
Can-Redefine-Classes: true
Can-Retransform-Classes: true
EOF

# 3. 打包
jar cmf MANIFEST.MF CostAgent.jar -C out .
```

---

## 六、测试应用

编写一个简单的 Spring Boot Controller：

```java
package com.pack.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Random;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/demos")
public class DemoController {

    private final Random random = new Random();

    @GetMapping("/index")
    public Object index() throws Exception {
        // 随机休眠 0~4 秒，模拟耗时操作
        TimeUnit.SECONDS.sleep(random.nextInt(5));
        return "success";
    }
}
```

打包为 `test.jar`。

---

## 七、运行与验证

### 启动命令

```shell
java -javaagent:CostAgent.jar -jar test.jar
```

### 访问测试接口

```shell
curl http://localhost:8080/demos/index
```

### 预期输出

```
[MonitorAgent] === Agent 已启动 ===
index 耗时:0 ms
index 耗时:0 ms
index 耗时:1008 ms
index 耗时:2012 ms
index 耗时:3015 ms
```

每次请求都会触发 Controller 方法的重新执行（Spring 的 Handler 机制），
耗时统计结果对应每次方法调用的实际执行时间。

---

## 八、常见问题

### Q: 为什么有些方法没有打印耗时？

可能原因：
1. 该类不在 `com.pack` 包下，被过滤条件排除了
2. 该方法是抽象方法或 native 方法，已被跳过
3. 该类在 Agent 注册转换器之前就已经被加载（premain 模式通常不会有此问题）

### Q: Spring Boot 启动报错 NotFoundException？

这是因为 `ClassPool.getDefault()` 找不到 Spring Boot fat jar 中嵌套的类。
解决方案见本文档第三节的 `ClassPool` 创建方式。

### Q: 如何排除特定方法（如 getter/setter）？

```java
// 在循环中增加过滤
if (methodName.startsWith("get") || methodName.startsWith("set")
        || methodName.equals("toString") || methodName.equals("hashCode")) {
    continue;
}
```

### Q: 如何统计到更细粒度的调用栈？

当前方案只在方法入口和出口各插一次代码。如果需要方法调用链追踪，
建议使用成熟的 APM 框架（SkyWalking、Elastic APM 等），
或使用 ByteBuddy 的 `Advice` API 实现更精细的控制。
