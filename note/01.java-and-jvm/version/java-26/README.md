<!--
module:
  parent: java
  slug: java/version/java-26
  type: article
  category: 主模块子文章
  summary: Java 26：10 个 JEP，含结构化并发预览、紧凑头实验、流式 IO 孵化
-->

# Java 26

## 引言：变更说明

Java 26 是 10 个 JEP 的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

### 相关阅读

← [Java 25](../java-25/README.md)

---

- **JEP 500**: 准备使 final 真正表示最终
- **JEP 504**: 移除 Applet API
- **JEP 516**: 支持任何 GC 的 AOT 对象缓存
- **JEP 517**: HTTP Client API 支持 HTTP/3
- **JEP 522**: G1 GC 通过减少同步来提高吞吐量
- **JEP 524**: PEM 编码的加密对象（第二次预览）
- **JEP 525**: 结构化并发（第六次预览）
- **JEP 526**: 惰性常量（第二次预览）
- **JEP 529**: 向量 API（第十一次孵化）
- **JEP 530**: 模式、instanceof 和 switch 中的基本类型（第四次预览）

## JEP 500: 准备使 final 真正表示最终

该特性限制了深度反射操作，默认情况下通过反射修改 final 字段会在运行时产生警告。在 Java 中，final 关键字表示字段一旦赋值就不能再被修改，但通过反射机制（如 `Field.set()`）可以绕过这一限制。该特性旨在加强 final 的语义，使 final 字段真正表示"不可变"，提高代码的安全性和可预测性。

这一变化为未来版本中彻底禁止通过反射修改 final 字段做准备，有助于 JIT 编译器进行更激进的优化。

## JEP 504: 移除 Applet API

Applet API 早在 Java 9 中就被标记为弃用，Java 26 正式将其从 JDK 中移除。随着现代浏览器逐步放弃对 NPAPI 插件的支持，Java Applet 已经失去了运行环境。移除该 API 可以减少 JDK 的维护负担，并消除不再需要的安全考量。

## JEP 516: 支持任何 GC 的 AOT 对象缓存

该特性将 AOT（Ahead-of-Time）对象缓存功能扩展到支持所有垃圾回收器。此前，AOT 对象缓存仅能与特定的 GC 配合使用。通过这一改进，开发者可以使用 `-XX:AOTCache` 参数配合任意 GC（如 G1、ZGC、Shenandoah 等）来缓存 AOT 编译后的对象，从而加快应用程序的启动速度。

```bash
# 生成 AOT 缓存
java -XX:AOTCache=cache.aot -cp myapp.jar MyMainClass

# 使用 AOT 缓存运行应用
java -XX:AOTCache=cache.aot -cp myapp.jar MyMainClass
```

## JEP 517: HTTP Client API 支持 HTTP/3

该特性在 Java 的 HTTP Client API 中引入了对 HTTP/3 协议的支持。HTTP/3 基于 QUIC 传输协议，相比 HTTP/2 具有更好的弱网络环境表现和更低的连接建立延迟。

```java
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_3)
    .build();

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://example.com"))
    .build();

HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
System.out.println(response.statusCode());
```

## JEP 522: G1 GC 通过减少同步来提高吞吐量

该特性通过减少 G1 写屏障中的同步操作和内部锁的使用，提高了 G1 垃圾回收器的吞吐量。具体来说，它优化了 G1 写屏障指令的数量，减少了并发标记过程中的锁竞争，使应用程序在多线程环境下的性能得到提升。

这对于使用 G1 作为默认 GC 的服务端应用程序来说是一个重要的性能改进。

## JEP 524: PEM 编码的加密对象（第二次预览）

PEM（Privacy Enhanced Mail）是一种广泛使用的编码格式，用于表示加密对象（如密钥、证书等）。该特性提供了对 PEM 编码的加密对象的读取和写入支持，使 Java 能够更方便地与现有的加密基础设施进行集成。

在第二次预览中，可能对 API 进行了进一步的完善和优化。

## JEP 525: 结构化并发（第六次预览）

结构化并发是一种多线程编程方法，旨在简化多线程代码的管理和错误处理。它将不同线程中运行的多个任务视为单个工作单元，从而提高了代码的可读性、可维护性和可靠性。

该特性引入了 `StructuredTaskScope` 类，允许开发者将任务拆分为多个并发子任务，并在它们自己的线程中执行。

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<Integer> future1 = scope.fork(() -> doTask1());
    Future<String> future2 = scope.fork(() -> doTask2());
    scope.join();
    scope.throwIfFailed();

    Integer result1 = future1.resultNow();
    String result2 = future2.resultNow();
    // 处理结果
} catch (Exception e) {
    // 处理异常
}
```

## JEP 526: 惰性常量（第二次预览）

惰性常量是一种新的常量求值机制，允许在首次使用时才计算常量的值，而不是在类加载时立即计算。这可以减少启动时间和内存占用，特别适用于那些很少使用或计算成本较高的常量。

在第二次预览中，该特性可能进一步完善了其语义和实现。

## JEP 529: 向量 API（第十一次孵化）

向量 API 提供了一种高效的方式来进行向量计算，适用于科学计算、机器学习等领域。该特性通过引入一组新的类和接口，允许开发者使用硬件加速的向量指令来执行计算，从而提高性能。

```java
import jdk.incubator.vector.*;

VectorSpecies<Integer> SPECIES = IntVector.SPECIES_256;

IntVector vector1 = IntVector.fromArray(SPECIES, new int[]{1, 2, 3, 4}, 0);
IntVector vector2 = IntVector.fromArray(SPECIES, new int[]{5, 6, 7, 8}, 0);

IntVector result = vector1.add(vector2);

int[] output = new int[4];
result.intoArray(output, 0);

System.out.println(java.util.Arrays.toString(output)); // [6, 8, 10, 12]
```

## JEP 530: 模式、instanceof 和 switch 中的基本类型（第四次预览）

该特性扩展了模式匹配的功能，允许在 `instanceof` 操作符和 `switch` 表达式中使用基本类型。这使得代码更加简洁和易读，减少了不必要的类型转换。

```java
Object obj = 42;
if (obj instanceof int i) {
    System.out.println("It's an int: " + i);
}

int value = 2;
String result = switch (value) {
    case 1 -> "One";
    case 2 -> "Two";
    case 3 -> "Three";
    default -> "Unknown";
};
System.out.println(result);
```

在第四次预览中，该特性可能进一步调整了语法和语义，为正式发布做准备。

---

## 其他新特性（非 JEP）

Java 26 还包含大量非 JEP 的改进，以下列出对开发者最实用的特性：

### 核心库 — java.lang

#### Process 实现 AutoCloseable

`java.lang.Process` 新增 `close()` 方法并实现 `AutoCloseable`/`Closeable`，支持 try-with-resources 自动终止进程和释放流。

#### Comparator.min(T, T) / max(T, T)

`Comparator` 新增默认方法，用于查找两个值中的较小/较大者，无需更改比较器实现。

#### Thread.stop() 移除

不安全的 `Thread.stop()` 方法已完全移除（自 JDK 18 起弃用，JDK 20 起抛 `UnsupportedOperationException`）。使用该方法的代码不再能编译。

### 核心库 — java.net / 网络

#### Windows 连接积压 > 200

`ServerSocket`、`ServerSocketChannel` 和 `AsynchronousServerSocketChannel` 现在在 Windows 上支持大于 200 的积压值（之前被钳制）。

#### BodyPublishers.ofFileChannel

新增方法，通过 HttpClient 上传文件的指定区域（切片），无需将整个文件读入内存。

#### HTTP Client 超时覆盖响应体

`HttpRequest.Builder::timeout` 现在适用于响应体消费，而不仅仅是头部。

#### 空请求不再发送 Content-Length: 0

HttpClient 在非 POST/PUT 方法且请求体为空时停止发送 `Content-Length: 0`，符合 RFC 9110。

#### HttpCookie 处理冲突的 Expires 和 Max-Age

`Max-Age` 现在正确地优先于 `Expires`，符合 RFC 6265。

#### CookieStore 返回不可变列表

`CookieStore.getURIs()`/`get(URI)` 现在返回不可变列表，与规范一致。

#### HttpClient 支持 TLS 命名组和签名方案

HttpClient 在 TLS 协商期间使用 `SSLParameters` 配置的签名方案和命名组（之前被忽略）。

#### ByteOrder 转换为枚举

`ByteOrder` 现在是枚举，可用于 switch 表达式和模式匹配。

#### 移除的特性

- InfiniBand SDP 支持（过时的 Sockets Direct Protocol）
- `MulticastSocket.setTTL(byte)`/`getTTL(byte)`（终弃方法）
- `SocketPermission` 弃用待移除
- `Socket.setPerformancePreferences` 弃用待移除

### 核心库 — java.sql (JDBC)

#### JDBC 4.5 MR 支持

新增 `DECFLOAT` 和 `JSON` 到 `JDBCType`/`Types`，弃用 `SQLPermission`，增强 `Array`/`Blob`/`Clob`/`Nclob`/`SQLXML` 实现 `AutoCloseable`。

### 核心库 — java.text

#### DecimalFormat 宽松减号解析

当 `isStrict()` 为 false（默认）时，识别替代减号（如 U+2212 MINUS SIGN）。

#### DecimalFormat 使用 Double.toString 算法

浮点格式化现在匹配 `Double.toString`/`Formatter`。旧算法可通过 `-Djdk.compat.DecimalFormat=true` 使用。

### 核心库 — java.time

#### Instant.plusSaturating(Duration)

使用饱和算术添加 Duration——返回 `Instant.MIN` 或 `Instant.MAX` 而不是溢出。

#### Duration.MIN / Duration.MAX 常量

新增可表示的最小/最大 duration 常量。

### 核心库 — java.util

#### UUIDv7 支持

`UUID.ofEpochMillis(long)` 从 Unix 纪元时间戳创建时间有序的类型 7 UUID。

```java
UUID uuid7 = UUID.ofEpochMillis(System.currentTimeMillis());
```

### 核心库 — java.io

#### PrintStream/PrintWriter 对 InterruptedIOException 报错

当抛出 `InterruptedIOException` 时，流现在标记为错误状态（`checkError()` 返回 true）。

### 核心库 — java.lang.classfile

#### 类文件 API 拒绝不可表示的整数数据

积极验证防止 int 值在写入较窄的类文件字段时被静默截断。

### 核心库 — java.math

#### BigDecimal.sqrt 标度修正

修正首选标度计算，与 IEEE 754 对齐。

### 国际化

#### Unicode 17.0 支持

新增 4,803 个字符（总计 159,801），4 种新脚本（Sidetic、Tolong Siki、Beria、Erfe Tai Yo）。`Character`、`Bidi`、`Normalizer` 和 `java.util.regex` 已更新。

#### CLDR v48

语言环境数据更新到 Unicode CLDR v48。主要变更：冰岛每周第一天（周一→周日）、新增欧洲英语语言环境、新增 en_JP、修正瑞士分组分隔符等。

### 安全

#### ML-KEM / ML-DSA 私钥编码更新

默认编码从 `expandedKey` 改为 `seed`，符合 RFC 9935/9881。

#### 签名 JAR 支持 ML-DSA

JAR 文件现在可以使用后量子 ML-DSA 算法签名（PKCS #7, RFC 9882）。

#### 混合公钥加密 (HPKE)

新增 `"HPKE"` Cipher 算法，符合 RFC 9180，结合 KEM + KDF + AEAD。

#### jdk.crypto.disabledAlgorithms 安全属性

新增安全属性，可在 JCE 层禁用 `Cipher`、`KeyStore`、`MessageDigest`、`Signature` 服务的算法。

#### JKS/JCEKS 密钥库弃用警告

`keytool`、`jarsigner` 和 KeyStore API 在使用遗留密钥库时发出警告。

#### XPath 在 XML 签名中禁用

XPath 转换默认禁用；请改用 XPath Filter 2.0。

#### CRL 大小限制

`com.sun.security.crl.maxSize` 限制 CRL 下载大小（默认 20 MiB）。

#### keytool/jarsigner 密码处理增强

重定向 stdout 时不再回显密码。

### 工具

#### javadoc 暗色主题

API 文档现在具有可切换的暗色主题（浅色 / 暗色 / 系统）。

#### javac Lambda/方法引用捕获转换

javac 现在对方法引用兼容性检查应用 JLS 要求的捕获转换（某些模式的破坏性变更）。

#### jlink 更严格的交叉链接版本检查

模块版本和供应商必须完全匹配才能进行交叉链接。

#### Windows 安装程序版本目录 + 连接点

LTS 系列安装到版本特定目录，带有指向系列中最新版本的 "latest" 连接点。

### HotSpot / JVM

#### G1 主动回收有引用的巨型对象

G1 现在可以在没有完全并发标记的情况下回收有引用的巨型对象。

#### G1 UseGCOverheadLimit 支持

G1 现在在 GC 开销超过 98% 且空闲堆 < 2% 持续 5 次 GC 时抛出 OOME（与 Parallel GC 行为一致）。

#### 默认初始堆大小 = MinHeapSize

不再默认为物理 RAM 的 1/64；使用最小堆大小，改善启动性能。可通过 `-XX:InitialRAMPercentage=1.5625` 恢复旧行为。

#### C2 编译大参数数量方法

C2 JIT 不再对参数过多的方法放弃编译。

#### 透明大页恢复

`-XX:+UseTransparentHugePages` 在配置为 `madvise` 的系统上恢复与 G1 配合使用。

#### -Xlog:cpu CPU 时间统计

VM 退出时打印按组件划分的 CPU 时间（GC、VM Thread 等）。

#### jmethodID 内存释放

`jmethodID` 现在是唯一标识符（不是直接指针）；破坏此抽象的本机代码将停止工作。

#### JFR 事件默认禁用

`jdk.ModuleExport`、`jdk.SymbolTableStatistics`、`jdk.StringTableStatistics` 在默认配置中禁用以减少开销。

#### 线程转储包含 Park Blocker 所有者

`jcmd Thread.dump_to_file` 和 `HotSpotDiagnosticMXBean.dumpThreads` 现在显示 park blocker 的所有者。

#### 弃用的 JVM 标志

`-Xmaxjitcodesize`、`AlwaysActAsServerClassMachine`/`NeverActAsServerClassMachine`、`AggressiveHeap`。

### Java 管理 (JMX)

#### MemoryPoolMXBean.getTotalGcCpuTime()

新增方法返回累计 GC CPU 时间（纳秒）。

#### JMXServiceURL 需要显式协议

移除了默认 "jmxmp" 协议的历史行为。

### 更新版本 (26.0.1 / 26.0.2)

| 版本 | 特性 | 领域 |
|------|------|------|
| 26.0.1 | FreeType 2.14.2（版本报告修正） | client-libs/2d |
| 26.0.2 | ML-KEM/ML-DSA 私钥编码默认改为 seed | security-libs |
| 26.0.2 | WISeKey Global Root GB/GC CA 证书添加 | security-libs |
| 26.0.2 | DTLS cookie 包含客户端主机/端口（RFC 6347） | security-libs |
| 26.0.2 | JFR jdk.OldObjectSample 对分代 ZGC 禁用 | hotspot/jfr |
| 26.0.2 | CRL 下载大小限制（默认 20 MiB） | security-libs |
| 26.0.2 | IANA TZ Data 2026b | core-libs |

### 移除特性汇总

| 特性 | 详情 |
|------|------|
| `Thread.stop()` | 完全移除；代码不再能编译 |
| InfiniBand SDP | 移除；多年已过时 |
| `MulticastSocket.setTTL(byte)`/`getTTL(byte)` | 移除终弃方法 |
| `javax.imageio.stream` 终结支持 | 移除以预期终结移除 |
| macOS Unicode Normalization Format D | 不再支持（APFS 不执行规范化） |

---

← [返回 Java 版本特性](../README.md)
