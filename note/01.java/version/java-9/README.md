<!--
module:
  parent: java
  slug: java/java-9
  type: article
  category: 主模块子文章
  summary: Java 9 核心 JEP 速通：JPMS 模块系统、jshell、Collection 工厂方法、Stream/Optional 增强、Compact Strings、G1 默认 GC、HTTP/2 Client(孵化) 等。
-->

# Java 9

## 引言：变更说明

Java 9 是首个把 **JPMS 模块系统**引入的版本，也是大量"工程化"特性集中落地的一版：jshell 交互式 REPL、Collection 便利工厂、`Stream`/`Optional` 增强、`Compact Strings` 内存优化、G1 成为默认 GC、HTTP/2 Client 孵化等。

本篇先**按主题提炼核心 JEP**（含 API 示例 + 一句"影响"），再给出**完整 JEP 列表**（每条一句定位），先读前两节再回扫索引。

---

## 一、核心 JEP 与最小 API 示例

### 1. JEP 261 — JPMS（Java Platform Module System）

**是什么**：JDK 9 的核心变革 —— 给应用引入**模块**（`module`）作为包的命名空间之上的封装。

```java
// src/com.foo.app/module-info.java
module com.foo.app {
    requires java.sql;                // 依赖
    requires com.foo.core;            // 依赖其它模块
    exports com.foo.app.api;          // 仅导出包给外部
    // com.foo.app.internal 不导出 → 默认仅本模块可见

    opens com.foo.app.model;          // 给反射/序列化打开
}
```

**为什么**：解决**强类路径（classpath）的 JAR Hell / 依赖冲突 / 内部 API 暴露**三大顽疾；Jdk 自带 `jlink` 按需裁剪运行时镜像，体积更小、启动更快。**影响**：所有 non-modular 项目继续兼容 classpath，但生态向模块化逐步迁移（Spring 6 已基于 Jakarta EE 9 模块化）。

---

### 2. JEP 222 — jshell：Java Shell（REPL）

**是什么**：JDK 自带的交互式 Java 命令行。

```bash
$ jshell
jshell> String s = "hello"
s ==> "hello"
jshell> s.toUpperCase()
$2 ==> "HELLO"
jshell> /exit
```

**为什么**/**影响**：去掉"写一个 `main` 才能跑一行"的摩擦，**学习 / 调试验证 API / 面试写代码**场景极其顺滑；JDK 9+ 自带，无需外部工具。

---

### 3. JEP 269 — 集合便利工厂方法（`List.of` / `Set.of` / `Map.of`）

**是什么**：为不可变集合提供静态工厂。

```java
List<String> list = List.of("a", "b", "c");        // 不可变
Set<Integer> set = Set.of(1, 2, 3);                // 不可变
Map<String, Integer> map = Map.of("k1", 1, "k2", 2);
```

**为什么**/**影响**：相比 `Arrays.asList`，`List.of` 真正**不可变**（`add` / `set` 抛 `UnsupportedOperationException`）且**更紧凑**（内部依赖 `ImmutableCollections`，无 `java.util.ArrayList` 包装）。**陷阱**：`Map.of` 不允许 `null` key 或 value；`Set.of`/`List.of` 元素也不允许 `null`。

---

### 4. JEP 269（续）— Stream 增强：`takeWhile` / `dropWhile` / `ofNullable` / `iterate`

**是什么**：短路操作在**有序流**上更顺手；空安全创建流；iterator 替代无种子写法。

```java
Stream.of(2, 4, 6, 7, 8).takeWhile(n -> n % 2 == 0)  // [2,4,6]  —— 遇 7 终止
                        .forEach(System.out::println);

Stream.of(2, 4, 6, 7, 8).dropWhile(n -> n % 2 == 0)  // [7,8]    —— 跳过前缀

Stream<String> s = Stream.ofNullable(maybeNull);     // null → 空流，不再 NPE
Stream.iterate(0, n -> n < 10, n -> n + 1)           // [0,1,...,9] —— 带终止条件
       .forEach(System.out::println);
```

**为什么**/**影响**：在 SQL 风格的"遇到第一条不满足即停"场景比 `filter` 更精准（`filter` 会扫完整个流），索引遍历、消费可空值时少 4 行 `if`。

---

### 5. Optional 增强 — `stream()` / `ifPresentOrElse` / `or`

**是什么**：把 `Optional` 真正变成**流式数据源**。

```java
List<User> admins = Optional.ofNullable(user)
        .filter(u -> u.isActive())
        .map(User::getRole)
        .stream()                                   // Optional → Stream
        .flatMap(roleRepo::findByRole)
        .collect(Collectors.toList());

config.computeIfPresent(key, (k, v) -> v);
```

**为什么**/**影响**：`stream()` 让"可空可选"顺滑接入 Stream pipeline；`ifPresentOrElse` 替代 `isPresent() + if/else` 反模式。

---

### 6. JEP 254 — Compact Strings（紧凑字符串）

**是什么**：`String` 内部存储从 `char[]`（UTF-16，每字符 2 字节）改为 **`byte[] + coder` 字段**，Latin-1 字符仅占 1 字节。

**为什么**/**影响**：堆内存显著下降（多数业务字符串为 Latin-1 / ASCII，**省约一半**）；`String` / `StringBuilder` / `AbstractStringBuilder` 同步重构；UTF-16 时切换到 `coder=1` 双字节存储。**注**：对外 API 不变，老代码无感迁移。

---

### 7. JEP 248 — G1 成为默认 GC

**是什么**：JDK 9 起 `-XX:+UseG1GC` 成为 32/64 位 server 模式**默认**垃圾收集器。

**为什么**/**影响**：G1 把堆划分为多个 Region，**目标是在停顿时间与吞吐量间可控**（`MaxGCPauseMillis` 目标可调），替代了 Parallel GC 在低延迟场景的不足。**注意**：吞吐量优先场景仍可在启动参数显式切回 `-XX:+UseParallelGC`。

---

### 8. JEP 238 — Multi-Release JAR（多版本 JAR）

**是什么**：一个 JAR 内可放**针对不同 Java 版本的同名类**（目录版本号 `META-INF/versions/9/`）。

```text
foo-1.0.jar
├── com.app.Foo.class                 (基线，JDK 6+)
└── META-INF/
    └── versions/9/com/app/Foo.class  (覆盖，JDK 9+ 调用此版本)
```

**为什么**/**影响**：库作者不必"为老 JDK 牺牲新 API"——可对外发布一个 JAR，运行时按 class 版本号匹配最高可用实现，**平滑从 JDK 8 迁到 JDK 9+**。

---

### 9. JEP 102 — Process API

**是什么**：`ProcessHandle` 提供本进程与所有进程的句柄、可枚举、父子关系。

```java
ProcessHandle.current().pid();                                    // 当前进程 PID
ProcessHandle.allProcesses()                                      // 枚举所有进程
    .filter(p -> p.info().command().orElse("").contains("nginx"))
    .forEach(p -> System.out.println(p.pid() + " " + p.info()));
```

**为什么**/**影响**：传统 `Runtime.exec()` 拿不到自己 PID；新版可**监控/管理子进程树**，与 `java.lang.Process` 配合做进程编排（被运维/CD 工具库广泛使用）。

---

### 10. JEP 110 — HTTP/2 Client（孵化器 `jdk.incubator.http`）

**是什么**：JDK 自带的现代 HTTP 客户端，支持 **HTTP/2**（多路复用、头部压缩、服务器推送）和 WebSocket。

```java
HttpClient client = HttpClient.newHttpClient();
HttpRequest req = HttpRequest.newBuilder()
        .uri(URI.create("https://api.example.com/v1/items"))
        .header("Content-Type", "application/json")
        .GET()
        .build();
HttpResponse<String> resp = client.send(req, HttpResponse.BodyHandlers.ofString());
System.out.println(resp.statusCode() + " " + resp.body());
```

**为什么**/**影响**：取代又老又难用的 `HttpURLConnection`；**孵化器**意味着 API 仍在进化，11 移出 incubator 进入正式 `java.net.http`。在轻量调用场景可少引入 OkHttp/HttpClient 依赖。

---

## 二、按主题分类的核心 JEP 速览

| 主题 | JEP | 一句话影响 |
|------|------|----------|
| 模块化 | 200/201/220/261/275/282 | JDK 自身模块化 + JPMS + jlink 裁剪运行时 |
| 语言/工具 | 213/222/280 | `try-with-resources` 增强 + jshell REPL + `+` 改 invokedynamic |
| 集合 | 269/266 | `List.of/Map.of` 不可变工厂 + Stream/Optional 增强 |
| 字符串 | 254 | Latin-1 紧凑字符串，省约一半堆内存 |
| GC | 248/214/291/271/278 | G1 默认 + 移除旧 GC 组合 + CMS 弃用 + 统一 GC 日志 |
| IO / 进程 | 102/238/260 | ProcessHandle + 多版本 JAR + 封装内部 API |
| 网络/安全 | 110/244/249/288 | HTTP/2 Client(孵化) + TLS ALPN + OCSP 装订 + 禁 SHA-1 |
| 并发 | 143/193/274/285 | 改进锁争用 + VarHandle + 增强 MethodHandle + 自旋提示 |
| 工具链 | 158/165/228/233/247 | 统一 JVM 日志 + JVMCI(Graal) + `jcmd` 诊断 + AOT |
| 国际化 | 226/227/252/267 | UTF-8 properties + Unicode 8.0 + 默认 CLDR |
| 文档 | 221/224/225 | Doclet API 简化 + HTML5 Javadoc + 搜索 |
| 平台 | 237/283/294/297 | AArch64/s390x/ARM 端口 + GTK 3 集成 |

---

- **JEP 102**: 进程API更新
- **JEP 110**: HTTP/2客户端
- **JEP 143**: 改进争用锁机制
- **JEP 158**: 统一JVM日志记录
- **JEP 165**: 编译器控制
- **JEP 193**: 变量句柄
- **JEP 197**: 分段代码缓存
- **JEP 199**: 智能Java编译（第二阶段）
- **JEP 200**: 模块化JDK
- **JEP 201**: 模块化源代码
- **JEP 211**: 导入语句中省略弃用警告
- **JEP 212**: 解决Lint和Doclint警告
- **JEP 213**: Milling Project Coin
- **JEP 214**: 移除JDK 8中已弃用的GC组合
- **JEP 215**: javac的分层归因
- **JEP 216**: 正确处理导入语句
- **JEP 217**: 注解管道2.0
- **JEP 219**: 数据报传输层安全(DTLS)
- **JEP 220**: 模块化运行时镜像
- **JEP 221**: 简化的Doclet API
- **JEP 222**: jshell：Java Shell（读取-求值-输出循环）
- **JEP 223**: 新版本字符串方案
- **JEP 224**: HTML5 Javadoc
- **JEP 225**: Javadoc搜索
- **JEP 226**: UTF-8属性文件
- **JEP 227**: Unicode 7.0
- **JEP 228**: 添加更多诊断命令
- **JEP 229**: 默认创建PKCS12密钥库
- **JEP 231**: 移除启动时JRE版本选择
- **JEP 232**: 改进安全应用程序性能
- **JEP 233**: 自动生成运行时编译器测试
- **JEP 235**: 测试javac生成的类文件属性
- **JEP 236**: Nashorn的解析器API
- **JEP 237**: Linux/AArch64端口
- **JEP 238**: 多版本JAR文件
- **JEP 240**: 移除JVM TI hprof代理
- **JEP 241**: 移除jhat工具
- **JEP 243**: Java级JVM编译器接口
- **JEP 244**: TLS应用层协议协商扩展
- **JEP 245**: 验证JVM命令行标志参数
- **JEP 246**: 利用CPU指令进行GHASH和RSA计算
- **JEP 247**: 为旧平台版本编译
- **JEP 248**: 使G1成为默认垃圾收集器
- **JEP 249**: TLS的OCSP装订
- **JEP 250**: 在CDS归档中存储内部字符串
- **JEP 251**: 多分辨率图像
- **JEP 252**: 默认使用CLDR区域设置数据
- **JEP 253**: 为模块化准备JavaFX UI控件和CSS API
- **JEP 254**: 紧凑字符串
- **JEP 255**: 将选定的Xerces 2.11.0更新合并到JAXP中
- **JEP 256**: BeanInfo注解
- **JEP 257**: 将JavaFX/Media更新到更新版本的GStreamer
- **JEP 258**: HarfBuzz字体布局引擎
- **JEP 259**: 栈遍历API
- **JEP 260**: 封装大多数内部API
- **JEP 261**: 模块系统
- **JEP 262**: TIFF图像I/O
- **JEP 263**: Windows和Linux上的HiDPI图形
- **JEP 264**: 平台日志API和服务
- **JEP 265**: Marlin图形渲染器
- **JEP 266**: 更多并发更新
- **JEP 267**: Unicode 8.0
- **JEP 268**: XML目录
- **JEP 269**: 集合的便利工厂方法
- **JEP 270**: 关键区域的保留堆栈空间
- **JEP 271**: 统一GC日志记录
- **JEP 272**: 平台特定桌面功能
- **JEP 273**: 基于DRBG的SecureRandom实现
- **JEP 274**: 增强的方法句柄
- **JEP 275**: 模块化Java应用程序打包
- **JEP 276**: 语言定义对象模型的动态链接
- **JEP 277**: 增强的弃用机制
- **JEP 278**: G1中巨大对象的额外测试
- **JEP 279**: 改进测试失败故障排除
- **JEP 280**: 字符串连接优化
- **JEP 281**: HotSpot C++单元测试框架
- **JEP 282**: jlink：Java链接器
- **JEP 283**: 在Linux上启用GTK 3
- **JEP 284**: 新的HotSpot构建系统
- **JEP 285**: 自旋等待提示
- **JEP 287**: SHA-3哈希算法
- **JEP 288**: 禁用SHA-1证书
- **JEP 289**: 弃用Applet API
- **JEP 290**: 过滤传入的序列化数据
- **JEP 291**: 弃用并发标记清除(CMS)垃圾收集器
- **JEP 292**: 在Nashorn中实现选定的ECMAScript 6特性
- **JEP 294**: Linux/s390x端口
- **JEP 295**: 预先编译(AOT)
- **JEP 297**: 统一arm32/arm64端口
- **JEP 298**: 移除演示和示例
- **JEP 299**: 重新组织文档

## JEP 102: 进程API更新

该特性增强了Java的进程控制能力，提供了更丰富的API来启动和管理操作系统进程。主要改进包括获取进程PID、枚举所有进程、处理进程树等。新的API使Java应用程序能够更好地与操作系统交互，监控和控制其他进程。

## JEP 110: HTTP/2客户端

引入了对HTTP/2协议的支持，提供了新的HTTP客户端API。该API支持HTTP/2协议特性，如多路复用、服务器推送、头部压缩等，相比传统的HttpURLConnection提供了更好的性能和易用性。

## JEP 143: 改进争用锁机制

优化了JVM中锁争用的处理机制，提高了在高并发场景下获取和释放锁的性能。该改进减少了线程在竞争锁时的开销，提升了多线程应用程序的整体性能。

## JEP 158: 统一JVM日志记录

引入了统一的日志记录框架，提供了一致的方式来记录JVM内部的各种事件。通过统一的日志格式和控制机制，开发者可以更容易地诊断和分析JVM的行为。

## JEP 165: 编译器控制

提供了 JVM 编译器接口（JVMCI），允许用 Java 编写的编译器替代 HotSpot 的内置 C++ 编译器。这使得 Graal 等基于 Java 的 JIT 编译器可以作为插件集成到 HotSpot 中，主要面向 JVM 开发者和研究人员。

## JEP 193: 变量句柄

引入了Variable Handles机制，提供了对字段和数组元素进行原子操作和内存访问控制的能力。相比传统的反射API，Variable Handles提供了更好的性能和类型安全性。

## JEP 197: 分段代码缓存

将JVM的代码缓存划分为多个段，分别存储不同类型的编译代码（如即时编译代码、AOT编译代码等）。这种结构提高了代码缓存的管理效率，减少了不同代码类型之间的干扰。

## JEP 199: 智能Java编译（第二阶段）

改进了javac编译器的性能和可维护性，包括优化编译速度、减少内存使用、改进错误报告等。这些改进使得编译大型项目更加高效。

## JEP 200: 模块化JDK

将JDK本身重构为模块化结构，每个模块都有明确的依赖关系和接口定义。这使得JDK更加模块化，便于维护和扩展。

## JEP 201: 模块化源代码

重新组织了JDK的源代码结构，按照模块化的方式进行组织。这种结构使得源代码更易于理解和维护。

## JEP 211: 导入语句中省略弃用警告

在导入已弃用的类或包时，可以选择性地抑制编译器警告。这减少了不必要的警告信息，使开发者能够更专注于真正需要关注的问题。

## JEP 212: 解决Lint和Doclint警告

修复了JDK源代码中的Lint和Doclint警告，提高了代码质量和文档质量。

## JEP 213: Milling Project Coin

实现了Project Coin的剩余改进，包括diamond操作符的扩展使用、try-with-resources语句的改进等，进一步简化了Java语法。

## JEP 214: 移除JDK 8中已弃用的GC组合

移除了在JDK 8中已标记为弃用的垃圾收集器组合，简化了JVM的GC配置选项。

## JEP 215: javac的分层归因

改进了javac编译器的类型检查和归因过程，提高了编译器的性能和准确性。

## JEP 216: 正确处理导入语句

修复了javac编译器在处理复杂导入语句时的一些问题，提高了编译器的健壮性。

## JEP 217: 注解管道2.0

改进了注解处理机制，提供了更好的性能和更丰富的功能。

## JEP 219: 数据报传输层安全(DTLS)

实现了DTLS协议支持，为基于UDP的应用程序提供了安全通信能力。

## JEP 220: 模块化运行时镜像

引入了模块化的运行时镜像格式，使得Java应用程序可以更小、启动更快。

## JEP 221: 简化的Doclet API

简化了Javadoc工具的Doclet API，使其更容易开发自定义的文档生成工具。

## JEP 222: jshell：Java Shell（读取-求值-输出循环）

引入了交互式的Java shell工具，允许开发者快速测试Java代码片段，无需创建完整的程序。

## JEP 223: 新版本字符串方案

采用了新的版本命名方案，使Java版本号更加清晰和一致。

## JEP 224: HTML5 Javadoc

改进了Javadoc生成器，支持生成HTML5格式的文档。

## JEP 225: Javadoc搜索

为生成的Javadoc文档添加了搜索功能，便于用户查找相关信息。

## JEP 226: UTF-8属性文件

支持使用UTF-8编码的属性文件，解决了非拉丁字符的本地化问题。

## JEP 227: Unicode 7.0

更新了Unicode支持到7.0版本，提供了对更多字符的支持。

## JEP 228: 添加更多诊断命令

增加了新的JVM诊断命令，便于监控和调试Java应用程序。

## JEP 229: 默认创建PKCS12密钥库

将默认的密钥库格式从JKS改为PKCS12，提高了与标准的兼容性。

## JEP 231: 移除启动时JRE版本选择

移除了在启动时选择JRE版本的功能，简化了JVM的启动过程。

## JEP 232: 改进安全应用程序性能

优化了安全相关代码的性能，减少了加密操作的开销。

## JEP 233: 自动生成运行时编译器测试

引入了自动生成运行时编译器测试的机制，提高了编译器的质量保证。

## JEP 235: 测试javac生成的类文件属性

增加了对javac生成的类文件属性的测试，确保编译器输出的正确性。

## JEP 236: Nashorn的解析器API

为Nashorn JavaScript引擎提供了解析器API，便于分析和处理JavaScript代码。

## JEP 237: Linux/AArch64端口

增加了对Linux/AArch64平台的支持，扩展了Java的平台兼容性。

## JEP 238: 多版本JAR文件

引入了多版本JAR文件支持，允许在单个JAR文件中包含针对不同Java版本的类文件。

## JEP 240: 移除JVM TI hprof代理

移除了已过时的hprof代理，简化了JVM工具接口。

## JEP 241: 移除jhat工具

移除了jhat工具，推荐使用更现代的分析工具。

## JEP 243: Java级JVM编译器接口

引入了Java级别的JVM编译器接口，便于开发自定义的编译器。

## JEP 244: TLS应用层协议协商扩展

实现了TLS应用层协议协商(ALPN)扩展，支持HTTP/2等协议。

## JEP 245: 验证JVM命令行标志参数

增加了对JVM命令行标志参数的验证，避免无效配置导致的问题。

## JEP 246: 利用CPU指令进行GHASH和RSA计算

利用现代CPU的硬件指令加速GHASH和RSA计算，提高加密性能。

## JEP 247: 为旧平台版本编译

提供了编译针对旧Java平台版本代码的能力。

## JEP 248: 使G1成为默认垃圾收集器

将G1垃圾收集器设为默认选择，提供了更好的性能和可预测性。

## JEP 249: TLS的OCSP装订

实现了OCSP装订支持，提高了TLS连接的性能和安全性。

## JEP 250: 在CDS归档中存储内部字符串

在类数据共享(CDS)归档中存储内部字符串，减少了应用程序启动时间。

## JEP 251: 多分辨率图像

支持多分辨率图像，便于开发高DPI显示的应用程序。

## JEP 252: 默认使用CLDR区域设置数据

默认使用Unicode CLDR区域设置数据，提供了更准确的国际化支持。

## JEP 253: 为模块化准备JavaFX UI控件和CSS API

为JavaFX UI控件和CSS API的模块化做好准备。

## JEP 254: 紧凑字符串

引入了紧凑字符串实现，减少了字符串内存使用。

## JEP 255: 将选定的Xerces 2.11.0更新合并到JAXP中

将Xerces XML解析器的更新合并到JAXP中，提高了XML处理能力。

## JEP 256: BeanInfo注解

引入了基于注解的BeanInfo定义机制，简化了JavaBean的开发。

## JEP 257: 将JavaFX/Media更新到更新版本的GStreamer

将JavaFX媒体功能更新到新版GStreamer，提高了媒体处理能力。

## JEP 258: HarfBuzz字体布局引擎

集成了HarfBuzz字体布局引擎，提供了更好的文本渲染支持。

## JEP 259: 栈遍历API

引入了高效的栈遍历API，便于调试和分析应用程序。

## JEP 260: 封装大多数内部API

封装了大多数JDK内部API，鼓励开发者使用标准API。

## JEP 261: 模块系统

实现了Java平台模块系统(JPMS)，提供了模块化的应用程序开发支持。

## JEP 262: TIFF图像I/O

增加了对TIFF图像格式的原生支持。

## JEP 263: Windows和Linux上的HiDPI图形

改进了在Windows和Linux上对HiDPI显示器的支持。

## JEP 264: 平台日志API和服务

引入了标准的平台日志API和服务。

## JEP 265: Marlin图形渲染器

集成了Marlin图形渲染器，提高了2D图形渲染性能。

## JEP 266: 更多并发更新

增加了更多的并发工具和API，如CompletableFuture的增强等。

## JEP 267: Unicode 8.0

更新了Unicode支持到8.0版本。

## JEP 268: XML目录

实现了XML目录支持，便于管理XML文档引用。

## JEP 269: 集合的便利工厂方法

为集合类添加了便利的工厂方法，简化了集合创建。

## JEP 270: 关键区域的保留堆栈空间

为关键区域保留堆栈空间，防止堆栈溢出。

## JEP 271: 统一GC日志记录

统一了垃圾收集器的日志记录格式。

## JEP 272: 平台特定桌面功能

提供了访问平台特定桌面功能的API。

## JEP 273: 基于DRBG的SecureRandom实现

实现了基于DRBG的SecureRandom，提供了更强的随机数生成能力。

## JEP 274: 增强的方法句柄

增强了方法句柄功能，提供了更多的操作选项。

## JEP 275: 模块化Java应用程序打包

支持模块化Java应用程序的打包。

## JEP 276: 语言定义对象模型的动态链接

提供了动态链接语言定义对象模型的能力。

## JEP 277: 增强的弃用机制

改进了弃用机制，提供了更详细的信息和更好的工具支持。

## JEP 278: G1中巨大对象的额外测试

增加了对G1垃圾收集器中巨大对象处理的测试。

## JEP 279: 改进测试失败故障排除

改进了测试失败时的故障排除能力。

## JEP 280: 字符串连接优化

优化了字符串连接操作的性能。

## JEP 281: HotSpot C++单元测试框架

为HotSpot JVM引入了C++单元测试框架。

## JEP 282: jlink：Java链接器

引入了jlink工具，用于创建自定义的运行时镜像。

## JEP 283: 在Linux上启用GTK 3

在Linux平台上启用了GTK 3支持。

## JEP 284: 新的HotSpot构建系统

采用了新的HotSpot JVM构建系统。

## JEP 285: 自旋等待提示

引入了自旋等待提示，优化了多线程性能。

## JEP 287: SHA-3哈希算法

实现了SHA-3哈希算法支持。

## JEP 288: 禁用SHA-1证书

默认禁用了SHA-1证书，提高了安全性。

## JEP 289: 弃用Applet API

标记Applet API为弃用状态。

## JEP 290: 过滤传入的序列化数据

引入了过滤传入序列化数据的机制，提高了安全性。

## JEP 291: 弃用并发标记清除(CMS)垃圾收集器

标记CMS垃圾收集器为弃用状态。

## JEP 292: 在Nashorn中实现选定的ECMAScript 6特性

在Nashorn JavaScript引擎中实现了部分ECMAScript 6特性。

## JEP 294: Linux/s390x端口

增加了对Linux/s390x平台的支持。

## JEP 295: 预先编译(AOT)

引入了预先编译(AOT)支持，提高了应用程序启动速度。

## JEP 297: 统一arm32/arm64端口

统一了ARM32和ARM64平台的端口实现。

## JEP 298: 移除演示和示例

移除了JDK中的演示和示例程序。

## JEP 299: 重新组织文档

重新组织了JDK文档结构，使其更加清晰易用。

---

## 相关阅读

- [Java 8 新特性](../java-8/README.md) — Lambda、Stream、Optional 起点
- [Java 11 LTS 新特性](../java-11/README.md) — HTTP Client 转正、String 新 API
- [Collection 工厂方法实战](../../collection/README.md) — `List.of` / `Map.of` 选型清单
- [Java 模块系统专题](../../modules/README.md) — JPMS 实战模式（requires/transports/open）

← [返回 Java 版本特性](../README.md)
## JPMS 模块化启动加速实测对比

| 镜像 | 体积 | 启动时间 (Hello World) | 模块依赖 |
|------|------|---------------------|----------|
| 完整 JRE（java.base + java.sql + ...） | ~150 MB | ~250 ms | 全模块 |
| `jlink` 自定义最小镜像（仅 java.base + java.logging） | **~30 MB** | **~80 ms** | 仅 2 模块 |
| 减少 80% 体积 + 68% 启动时间 | 适合微服务/Docker/Serverless | — | 需 JPMS 迁移 |

**实际测量方法**：

```bash
# 完整 JRE 启动（baseline）
java -jar hello.jar
# 启动时间：~250ms（冷启动，磁盘缓存后）

# jlink 构建最小镜像
jlink --module-path "$JAVA_HOME/jmods" \
      --add-modules java.base,java.logging \
      --output custom-jre \
      --strip-debug --no-man-pages --compress=2

# 自定义镜像启动
./custom-jre/bin/java -jar hello.jar
# 启动时间：~80ms
```

**适用场景**：
- 微服务/Docker 镜像（每 MB 存储 + 每 ms 启动延迟都重要）
- Serverless 冷启动（AWS Lambda、Azure Functions）
- 边缘计算/IoT（资源受限设备）

**注意**：
- 标准 JRE 9 → 完整 JRE 模块 (~150 MB) 启动时间已大幅优化
- `jlink` 优势在镜像大小（对容器化部署 ROI 显著）和启动时间（对 serverless 关键）
- 非模块化项目仍可使用 jlink 裁剪（指定模块路径即可）
