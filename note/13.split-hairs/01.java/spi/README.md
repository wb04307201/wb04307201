<!--
question:
  id: 01.java-spi
  topic: 01.java
  difficulty: 未标
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [01.java, spi]
-->

# Java SPI 机制深度剖析

## 引子：JDBC 是怎么找到数据库驱动的？

```java
// 你只写了一行
Class.forName("com.mysql.cj.jdbc.Driver");

// 然后 DriverManager 就能连 MySQL 了
Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/test", ...);
```

奇怪：你的代码里根本没有引用 MySQL 的任何类，JDK 是怎么"认识" MySQL 驱动的？

换 PostgreSQL 呢？换 Oracle 呢？JDK 不可能预知所有数据库厂商的实现。

这就是 **SPI（Service Provider Interface）** 的设计哲学——**框架定义规则，厂商提供实现，运行时动态发现**。

---

## 一、核心原理

> 📚 **前置知识**：[SPI](../../../01.java/concepts/spi/README.md) | [类加载](../class-loading/README.md)

**SPI 是什么？**

SPI 全称 Service Provider Interface，是一种服务发现机制。其核心思想是：**框架定义接口，由第三方厂商提供具体实现**。这与 API（Application Programming Interface）形成鲜明对比——API 是"我实现，你调用"，而 SPI 是"我定义，你实现"。

**设计哲学：面向接口编程 + 动态加载**

```
┌─────────────────────────────────────────┐
│          框架层（定义接口）               │
│     public interface DatabaseDriver {}   │
└──────────────┬──────────────────────────┘
               │ SPI 契约
┌──────────────┼──────────────────────────┐
│  实现方 A    │  实现方 B    │  实现方 C   │
│  MySQL驱动   │  PostgreSQL  │  Oracle    │
└──────────────┴──────────────┴────────────┘
```

框架只需面向接口编程，无需关心具体实现；实现方只需按约定注册服务，即可被框架自动发现。这种解耦设计使得系统具备极强的可扩展性。

---

## 二、ServiceLoader 源码

`java.util.ServiceLoader` 是 JDK 提供的 SPI 核心工具类，位于 `java.util` 包下。

### 2.1 load 方法

```java
public static <S> ServiceLoader<S> load(Class<S> service, ClassLoader loader) {
    return new ServiceLoader<>(service, loader);
}
```

`load` 方法返回一个 `ServiceLoader` 实例，**此时并不会立即加载任何实现类**，而是创建了一个懒加载的迭代器。

### 2.2 迭代器懒加载

```java
public Iterator<S> iterator() {
    return new Iterator<S>() {
        public boolean hasNext() { ... }
        public S next() { ... }  // 真正触发加载
    };
}
```

只有当调用 `iterator().next()` 时，才会真正读取配置文件并实例化实现类。这种懒加载设计避免了不必要的类加载开销。

### 2.3 META-INF/services/ 配置文件

SPI 约定的配置文件位置：**`META-INF/services/`**

- **文件名**：接口的全限定名（如 `java.sql.Driver`）
- **文件内容**：实现类的全限定名，一行一个

```
# META-INF/services/java.sql.Driver
com.mysql.cj.jdbc.Driver
org.postgresql.Driver
```

`ServiceLoader` 内部通过 `ClassLoader.getResources("META-INF/services/" + serviceName)` 查找所有匹配的配置文件。

---

## 三、SPI 如何打破双亲委派

### 3.1 问题背景

JDBC 的 `java.sql.Driver` 接口位于 `rt.jar`，由 **Bootstrap ClassLoader** 加载。但 MySQL 驱动 `com.mysql.cj.jdbc.Driver` 位于 classpath，只能由 **Application ClassLoader** 加载。

按照双亲委派模型，Bootstrap ClassLoader 无法委托子类加载器去加载实现类，这就产生了矛盾。

### 3.2 解决方案：线程上下文类加载器

```java
// DriverManager 静态块中
static {
    loadInitialDrivers();  // 内部使用 ServiceLoader
}

private static void loadInitialDrivers() {
    ServiceLoader<Driver> loadedDrivers = ServiceLoader.load(Driver.class);
    // 关键：使用 Thread.currentThread().getContextClassLoader()
}
```

`ServiceLoader` 内部获取类加载器的逻辑：

```java
this.loader = (loader == null) 
    ? Thread.currentThread().getContextClassLoader() 
    : loader;
```

**Thread Context ClassLoader** 默认是 Application ClassLoader，它作为一座"桥"，让 Bootstrap ClassLoader 加载的代码能够访问 Application ClassLoader 加载的类，从而打破了双亲委派的限制。

---

## 四、实际应用

### 4.1 JDBC Driver 加载

`DriverManager` 是最经典的 SPI 应用场景：

```java
// 传统方式需要手动注册
Class.forName("com.mysql.cj.jdbc.Driver");

// SPI 方式自动发现
Connection conn = DriverManager.getConnection("jdbc:mysql://...");
```

JDK 6+ 之后，只要驱动 jar 包中存在正确的 SPI 配置文件，就无需手动 `Class.forName`。

### 4.2 SLF4J 的 StaticLoggerBinder

SLF4J 通过 SPI 绑定具体日志实现：

```java
// slf4j-api 中的绑定机制
private static ILoggerFactory bind() {
    Set<URL> staticLoggerBinderPathSet = findPossibleStaticLoggerBinderPathSet();
    // 查找 org/slf4j/impl/StaticLoggerBinder.class
}
```

虽然 SLF4J 没有直接使用 `ServiceLoader`，但其思想与 SPI 一致：API 层定义接口，实现层提供 `StaticLoggerBinder` 进行绑定。

### 4.3 Dubbo SPI（增强版）

Dubbo 对原生 SPI 进行了大幅增强，详见第五节。

### 4.4 Spring Boot 自动配置

Spring Boot 的 `@EnableAutoConfiguration` 本质也是 SPI 思想：

```properties
# META-INF/spring.factories
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.example.MyAutoConfiguration
```

Spring Boot 3.x 迁移到新的导入文件：
```
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

---

## 五、Dubbo SPI vs Java SPI

| 维度 | Java SPI | Dubbo SPI |
|------|----------|-----------|
| **加载策略** | 全量加载（一次性实例化所有实现） | 按需加载（只实例化用到的实现） |
| **配置格式** | 纯文件名列表 | KV 格式（key=实现类全限定名） |
| **扩展能力** | 无 | @SPI 注解 + ExtensionLoader |
| **自适应** | 不支持 | @Adaptive 自适应扩展 |
| **包装器** | 不支持 | Wrapper 类（AOP 思想） |

### Dubbo SPI 配置示例

```properties
# META-INF/dubbo/org.apache.dubbo.rpc.Protocol
dubbo=com.apache.dubbo.rpc.protocol.dubbo.DubboProtocol
http=com.apache.dubbo.rpc.protocol.http.HttpProtocol
```

通过 `ExtensionLoader.getExtensionLoader(Protocol.class).getExtension("dubbo")` 按需加载指定实现，避免了资源浪费。

---

## 六、面试话术（30 秒版）

> "SPI 是服务提供者接口机制，框架定义接口，第三方通过 `META-INF/services/` 下的配置文件注册实现。`ServiceLoader` 采用懒加载方式，只在遍历迭代器时才实例化实现类。JDBC 是典型应用，通过线程上下文类加载器打破双亲委派，让 Bootstrap 加载的 `DriverManager` 能够加载 App ClassLoader 中的驱动实现。Dubbo 在此基础上做了增强，支持按需加载和自适应扩展。"

---

## 七、交叉引用

- 主模块：[`01.java`](../../../01.java/) — Java 知识体系
- [类加载机制](../class-loading/README.md) — 类加载与双亲委派
- [JDBC](../../../01.java/jdbc/README.md) — JDBC 深入
- [SPI 设计模式](../../../01.java/concepts/spi/README.md) — SPI 机制详解

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · spi](README.md)
