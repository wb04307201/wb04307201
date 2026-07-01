# Java 日志学习笔记

## 引言：反直觉代码
Java 日志学习笔记 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、日志级别

Java 日志体系通常包含以下六个级别，按严重程度从低到高排列：

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| `TRACE` | 最详细的追踪信息 | 细粒度调试，如循环内变量值、方法入参出参 |
| `DEBUG` | 调试信息 | 开发阶段排查问题，记录程序执行路径 |
| `INFO` | 一般运行信息 | 系统启动、关键业务操作完成、定时任务执行 |
| `WARN` | 警告信息 | 可恢复的异常、配置缺失、降级策略触发 |
| `ERROR` | 错误信息 | 不可恢复的异常、核心业务失败、外部调用异常 |
| `FATAL` | 致命错误 | 系统无法继续运行，需要立即停机处理 |

```java
// 各级别日志调用示例
logger.trace("Entering method processOrder with orderId={}", orderId);
logger.debug("Order {} status changed from {} to {}", orderId, oldStatus, newStatus);
logger.info("Application started successfully on port {}", port);
logger.warn("Connection pool size {} exceeds threshold {}", currentSize, threshold);
logger.error("Failed to process payment for order {}", orderId, exception);
logger.fatal("Database connection lost, shutting down service");
```

> **注意：** 生产环境通常将日志级别设置为 `INFO` 或 `WARN`，以避免大量调试信息占用磁盘空间和 I/O 带宽。

## 二、java.util.logging（JUL）简介

`java.util.logging`（简称 JUL）是 Java 1.4 引入的官方日志框架，位于 `java.util.logging` 包中。

### 核心组件

| 组件 | 说明 |
|------|------|
| `Logger` | 日志记录器，应用程序通过它发出日志调用 |
| `Handler` | 日志处理器，决定日志输出到哪里（控制台、文件等） |
| `Formatter` | 日志格式化器，决定日志的输出格式 |
| `Level` | 日志级别枚举 |
| `LogManager` | 日志管理器，负责配置和管理 Logger 实例 |

### 使用示例

```java
import java.util.logging.*;

public class JulExample {
    // 获取 Logger 实例
    private static final Logger logger = Logger.getLogger(JulExample.class.getName());

    public static void main(String[] args) {
        // 基本使用
        logger.info("这是一条 INFO 级别日志");
        logger.warning("这是一条 WARN 级别日志");
        logger.severe("这是一条 ERROR 级别日志");

        // 配置 ConsoleHandler
        ConsoleHandler handler = new ConsoleHandler();
        handler.setLevel(Level.ALL);
        handler.setFormatter(new SimpleFormatter());

        logger.setLevel(Level.ALL);
        logger.addHandler(handler);

        // 带异常的日志
        try {
            int result = 10 / 0;
        } catch (ArithmeticException e) {
            logger.log(Level.SEVERE, "计算异常", e);
        }
    }
}
```

### JUL 的局限性

- 性能较差，不支持异步日志
- 功能单一，缺少 Log4j/Logback 的高级特性
- 社区活跃度低，极少用于生产项目
- 日志级别命名与其他框架不一致（如 `SEVERE` 而非 `ERROR`）

## 三、Log4j 2 简介

Apache Log4j 2 是 Log4j 1.x 的升级版，在性能和功能上都有显著提升。

### 核心特性

1. **异步日志**：基于 LMAX Disruptor 无锁队列，吞吐量是 Log4j 1.x 和 Logback 的 10 倍以上
2. **零 GC 模式**：在 Java 8+ 上运行时可做到完全无垃圾回收压力
3. **插件式架构**：支持自定义 Appender、Layout、Filter 等
4. **自动重载配置**：支持配置文件热更新
5. **多 API 支持**：同时支持 Log4j 2 API、SLF4J、java.util.logging 等

### 依赖引入

```xml
<!-- Log4j 2 核心依赖 -->
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.24.1</version>
</dependency>
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-api</artifactId>
    <version>2.24.1</version>
</dependency>

<!-- SLF4J 桥接 -->
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-slf4j2-impl</artifactId>
    <version>2.24.1</version>
</dependency>
```

### 配置示例（log4j2.xml）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="WARN" monitorInterval="30">
    <Properties>
        <Property name="LOG_DIR">logs</Property>
        <Property name="PATTERN">%d{yyyy-MM-dd HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n</Property>
    </Properties>

    <Appenders>
        <!-- 控制台输出 -->
        <Console name="Console" target="SYSTEM_OUT">
            <PatternLayout pattern="${PATTERN}"/>
        </Console>

        <!-- 异步文件输出 -->
        <RollingFile name="RollingFile"
                     fileName="${LOG_DIR}/app.log"
                     filePattern="${LOG_DIR}/app-%d{yyyy-MM-dd}-%i.log.gz">
            <PatternLayout pattern="${PATTERN}"/>
            <Policies>
                <TimeBasedTriggeringPolicy interval="1"/>
                <SizeBasedTriggeringPolicy size="100 MB"/>
            </Policies>
            <DefaultRolloverStrategy max="30"/>
        </RollingFile>
    </Appenders>

    <Loggers>
        <Logger name="com.example" level="debug" additivity="false">
            <AppenderRef ref="Console"/>
            <AppenderRef ref="RollingFile"/>
        </Logger>
        <Root level="info">
            <AppenderRef ref="Console"/>
        </Root>
    </Loggers>
</Configuration>
```

### 零 GC 模式原理

Log4j 2 的零 GC（Garbage Collector Free）模式通过以下方式减少对象分配：

- 使用 `ThreadLocal` 复用 `StringBuilder` 和缓冲区
- 避免创建 `String` 对象，直接使用字符数组
- 日志消息延迟到真正写入时才格式化（Lambda 支持）
- 使用内存映射文件（MemoryMappedFile）减少 I/O 对象创建

```java
// 使用 Lambda 延迟字符串拼接，减少不必要的对象创建
logger.debug("User {} performed action {} at time {}",
    () -> userId,
    () -> actionName,
    () -> timestamp);
```

## 四、Logback 简介

Logback 由 Log4j 的创始人 Ceki Gulcu 创建，是 Log4j 1.x 的精神继承者，也是 **Spring Boot 的默认日志框架**。

### 核心模块

| 模块 | 说明 |
|------|------|
| `logback-core` | 核心模块，提供基础功能 |
| `logback-classic` | 经典模块，包含 SLF4J 集成 |
| `logback-access` | HTTP 访问日志模块（与 Jetty/Tomcat 集成） |

### 核心特性

1. **原生支持 SLF4J**：无需桥接层，性能更好
2. **自动重载配置**：`scan="true"` 实现配置热更新
3. **条件配置**：支持 `<if>` / `<then>` / `<else>` 条件判断
4. **丰富的过滤器**：支持基于级别、Marker、MDC 的过滤
5. **自动压缩**：滚动日志自动 gzip 压缩

### 依赖引入（Spring Boot 项目默认包含）

```xml
<!-- Spring Boot Starter 已自动引入 Logback -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-logging</artifactId>
</dependency>
```

### 使用示例

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LogbackExample {
    private static final Logger log = LoggerFactory.getLogger(LogbackExample.class);

    public void processOrder(String orderId) {
        log.info("开始处理订单: {}", orderId);
        try {
            // 业务逻辑
            log.debug("订单 {} 处理完成", orderId);
        } catch (Exception e) {
            log.error("订单 {} 处理失败", orderId, e);
        }
    }
}
```

## 五、SLF4J 门面（日志抽象层）

SLF4J（Simple Logging Facade for Java）是一个日志门面，它为各种日志框架提供统一的 API。

### 架构设计

```
应用程序
    |
    v
  SLF4J API (slf4j-api.jar)
    |
    v
  SLF4J Binding (适配器层)
    |
    +---> logback-classic (直接实现)
    +---> log4j-slf4j-impl (Log4j 2 适配)
    +---> jul-to-slf4j (JUL 桥接)
    +---> jcl-over-slf4j (Commons Logging 桥接)
    |
    v
  具体日志框架实现
```

### 核心优势

| 优势 | 说明 |
|------|------|
| **解耦** | 业务代码不依赖具体日志实现，可自由切换框架 |
| **占位符** | `{}` 占位符避免不必要的字符串拼接 |
| **统一 API** | 一个 API 适配所有主流日志框架 |
| **桥接能力** | 可将 JUL、JCL 等日志调用重定向到 SLF4J |

### 常用 API

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class Slf4jApiExample {

    private static final Logger log = LoggerFactory.getLogger(Slf4jApiExample.class);

    // 1. 占位符日志（推荐）
    public void method1() {
        log.info("用户 {} 登录成功，IP: {}", username, ipAddress);
    }

    // 2. 条件日志（耗时计算场景）
    public void method2() {
        if (log.isDebugEnabled()) {
            log.debug("复杂计算结果: {}", expensiveComputation());
        }
    }

    // 3. MDC（Mapped Diagnostic Context）用于链路追踪
    public void method3(String traceId) {
        MDC.put("traceId", traceId);
        try {
            log.info("处理业务请求");
        } finally {
            MDC.remove("traceId");
        }
    }

    // 4. Marker 标记日志
    public void method4() {
        Marker securityMarker = MarkerFactory.getMarker("SECURITY");
        log.warn(securityMarker, "检测到异常登录尝试");
    }
}
```

### 桥接与排除冲突

当项目中混用多个日志框架时，需要通过桥接和排除来解决冲突：

```xml
<!-- 排除 Commons Logging，桥接到 SLF4J -->
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-core</artifactId>
    <exclusions>
        <exclusion>
            <groupId>commons-logging</groupId>
            <artifactId>commons-logging</artifactId>
        </exclusion>
    </exclusions>
</dependency>

<!-- JUL 桥接到 SLF4J -->
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>jul-to-slf4j</artifactId>
</dependency>
```

## 六、各日志框架对比

| 对比维度 | JUL | Log4j 1.x | Log4j 2 | Logback |
|----------|-----|-----------|---------|---------|
| **发布年份** | 2002 (Java 1.4) | 2001 | 2014 | 2006 |
| **维护状态** | JDK 内置维护 | 已停止维护 | 活跃维护 | 活跃维护 |
| **异步日志** | 不支持 | 不支持 | 支持（Disruptor） | 支持（AsyncAppender） |
| **零 GC** | 不支持 | 不支持 | 支持 | 不支持 |
| **自动重载** | 不支持 | 不支持 | 支持 | 支持 |
| **配置格式** | properties | XML/properties | XML/JSON/YAML | XML/Groovy |
| **过滤器** | 简单 | 有限 | 丰富 | 丰富 |
| **性能排名** | 最差 | 较差 | 最优 | 中等偏上 |
| **Spring Boot 默认** | 否 | 否 | 否 | 是 |
| **API 设计** | 原生 API | 原生 API | 独立 API + SLF4J | SLF4J 原生 |
| **滚动策略** | 有限 | 有限 | 非常灵活 | 灵活 |
| **社区活跃度** | 低 | 已停止 | 高 | 高 |

### 性能对比（吞吐量，越高越好）

```
Log4j 2 (Async)  ████████████████████████████████████████ ~5,000,000 条/秒
Log4j 2 (Sync)   ███████████████████~ 1,500,000 条/秒
Logback (Async)  █████████████~       1,200,000 条/秒
Logback (Sync)   █████████~            800,000 条/秒
JUL              ███~                  300,000 条/秒
```

## 七、SLF4J + Logback 配置示例

### 完整 logback-spring.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration scan="true" scanPeriod="60 seconds">

    <!-- Spring Profile 支持 -->
    <springProfile name="dev">
        <property name="LOG_LEVEL" value="DEBUG"/>
    </springProfile>
    <springProfile name="prod">
        <property name="LOG_LEVEL" value="INFO"/>
    </springProfile>

    <!-- 日志格式定义 -->
    <property name="CONSOLE_PATTERN"
              value="%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %highlight(%-5level) %cyan(%logger{36}) - %msg%n"/>
    <property name="FILE_PATTERN"
              value="%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"/>

    <!-- 控制台 Appender -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>${CONSOLE_PATTERN}</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>

    <!-- 文件 Appender（按天滚动） -->
    <appender name="FILE_INFO" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/app-info.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/app-info.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
            <totalSizeCap>3GB</totalSizeCap>
        </rollingPolicy>
        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <level>INFO</level>
            <onMatch>ACCEPT</onMatch>
            <onMismatch>DENY</onMismatch>
        </filter>
        <encoder>
            <pattern>${FILE_PATTERN}</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>

    <!-- 文件 Appender（错误日志单独输出） -->
    <appender name="FILE_ERROR" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/app-error.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/app-error.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>90</maxHistory>
        </rollingPolicy>
        <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
            <level>ERROR</level>
        </filter>
        <encoder>
            <pattern>${FILE_PATTERN}</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>

    <!-- 异步 Appender（包裹文件 Appender） -->
    <appender name="ASYNC_FILE" class="ch.qos.logback.classic.AsyncAppender">
        <queueSize>512</queueSize>
        <discardingThreshold>0</discardingThreshold>
        <includeCallerData>true</includeCallerData>
        <appender-ref ref="FILE_INFO"/>
    </appender>

    <!-- Logger 配置 -->
    <logger name="com.example.service" level="DEBUG" additivity="false">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="ASYNC_FILE"/>
    </logger>

    <logger name="org.springframework" level="WARN"/>
    <logger name="org.hibernate" level="WARN"/>

    <!-- Root Logger -->
    <root level="${LOG_LEVEL}">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE_INFO"/>
        <appender-ref ref="FILE_ERROR"/>
    </root>

</configuration>
```

### application.yml 简化配置

```yaml
logging:
  level:
    root: INFO
    com.example: DEBUG
    org.springframework: WARN
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: logs/application.log
    max-size: 100MB
    max-history: 30
```

## 八、日志格式（JSON vs 文本）

### 文本格式

传统的文本格式适合人类阅读，使用 PatternLayout 定义输出模板：

```
2025-06-04 10:30:45.123 [main] INFO  c.e.service.OrderService - 订单 12345 创建成功, 用户: user_001
```

```xml
<!-- 文本格式配置 -->
<pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
```

| 优点 | 缺点 |
|------|------|
| 人类可读性好 | 机器解析困难 |
| 简单的 grep/awk 即可查询 | 结构化查询能力差 |
| 日志文件体积小 | 多行异常堆栈解析复杂 |

### JSON 格式

JSON 格式适合机器处理，是日志聚合系统（ELK、Splunk）的首选：

```json
{
  "timestamp": "2025-06-04T10:30:45.123+08:00",
  "level": "INFO",
  "thread": "main",
  "logger": "com.example.service.OrderService",
  "message": "订单 12345 创建成功",
  "traceId": "abc-123-def",
  "userId": "user_001",
  "orderId": "12345",
  "serviceName": "order-service",
  "environment": "production"
}
```

#### Logback JSON 配置（使用 logstash-logback-encoder）

```xml
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>7.4</version>
</dependency>
```

```xml
<appender name="JSON_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>logs/app.json.log</file>
    <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
        <fileNamePattern>logs/app.json.%d{yyyy-MM-dd}.log</fileNamePattern>
        <maxHistory>30</maxHistory>
    </rollingPolicy>
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
        <customFields>{"serviceName":"order-service","environment":"production"}</customFields>
        <includeMdcKeyName>traceId</includeMdcKeyName>
        <includeMdcKeyName>userId</includeMdcKeyName>
    </encoder>
</appender>
```

#### Log4j 2 JSON 配置

```xml
<JsonLayout compact="true" eventEol="true" stacktraceAsString="true"
            includeTimeMillis="true" locationInfo="true">
    <KeyValuePair key="serviceName" value="order-service"/>
    <KeyValuePair key="environment" value="${env:ENVIRONMENT}"/>
</JsonLayout>
```

### 格式选择建议

| 场景 | 推荐格式 | 原因 |
|------|----------|------|
| 本地开发调试 | 文本 | 直观、易读 |
| 生产环境 + ELK | JSON | 结构化、便于索引和查询 |
| 生产环境 + 日志文件审计 | 文本 + JSON 双写 | 兼顾人工审计和机器分析 |
| 容器化部署（stdout） | JSON | 容器日志采集系统友好 |

## 九、异步日志原理

### 为什么需要异步日志

同步日志的瓶颈在于 I/O 操作：每次写日志都需要等待磁盘 I/O 完成，阻塞业务线程。异步日志将写日志操作交给后台线程处理，业务线程只需将日志事件放入队列即可继续执行。

### 架构模型

```
业务线程                    后台 I/O 线程
   |                            |
   |  1. 创建 LogEvent          |
   |  2. 放入队列 (RingBuffer)  |
   |  3. 立即返回，继续业务 ----|
   |                            |---- 4. 从队列取 LogEvent
   |                            |---- 5. 格式化日志消息
   |                            |---- 6. 写入磁盘/网络
   |                            |---- 7. 处理下一个
```

### 实现方式对比

| 实现方式 | 队列类型 | 特点 |
|----------|----------|------|
| Log4j 2 Async | LMAX Disruptor RingBuffer | 无锁、高吞吐、低延迟 |
| Logback AsyncAppender | ArrayBlockingQueue | 有锁、实现简单 |
| 手动异步 | CompletableFuture | 灵活但需注意异常处理 |

### Log4j 2 AsyncAppender 配置

```xml
<Configuration>
    <Appenders>
        <Console name="Console" target="SYSTEM_OUT">
            <PatternLayout pattern="%d %-5level %logger - %msg%n"/>
        </Console>

        <RollingFile name="File" fileName="logs/async.log"
                     filePattern="logs/async.%d{yyyy-MM-dd}.log">
            <PatternLayout pattern="%d %-5level %logger - %msg%n"/>
            <Policies>
                <TimeBasedTriggeringPolicy interval="1"/>
            </Policies>
        </RollingFile>

        <!-- 异步 Appender，使用 Disruptor 无锁队列 -->
        <Async name="Async" bufferSize="262144" includeLocation="false">
            <AppenderRef ref="File"/>
            <AppenderRef ref="Console"/>
        </Async>
    </Appenders>

    <Loggers>
        <Root level="info">
            <AppenderRef ref="Async"/>
        </Root>
    </Loggers>
</Configuration>
```

### 关键参数说明

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `bufferSize` | RingBuffer 大小（必须为 2 的幂） | 262144 (256K) |
| `includeLocation` | 是否包含代码位置信息（影响性能） | `false`（生产环境） |
| `blocking` | 队列满时是否阻塞 | `true`（不丢日志） |
| `queueSize` | Logback AsyncAppender 队列大小 | 512-2048 |
| `discardingThreshold` | Logback 丢弃阈值 | 0（不丢弃） |

### RingBuffer 核心原理

```
         +---+---+---+---+---+---+---+---+
         | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |  <-- 预分配的数组
         +---+---+---+---+---+---+---+---+
           ^                       ^
        consumer                 producer

1. RingBuffer 是一个固定大小的循环数组
2. 生产者（业务线程）通过 CAS 操作获取下一个序列号
3. 将日志事件写入对应槽位
4. 消费者（I/O 线程）按顺序读取并处理
5. 无锁设计：生产者和消费者各自维护独立的指针
6. 缓存行填充（Cache Line Padding）避免伪共享
```

### 性能影响

```
同步写日志: 业务线程 --[写日志 2ms]--> 继续执行
            总耗时: 业务逻辑 + 2ms

异步写日志: 业务线程 --[入队 0.001ms]--> 继续执行
                          |
                    后台线程 --[写日志 2ms]--> 完成
            总耗时: 业务逻辑 + 0.001ms
```

> **注意：** `includeLocation="true"` 会捕获线程栈信息以获取类名、方法名、行号，这会显著影响性能。生产环境建议关闭。

## 十、最佳实践

### 1. 日志级别选择原则

| 场景 | 级别 | 示例 |
|------|------|------|
| 方法入口/出口 | `DEBUG` | `log.debug("entering processOrder, param={}", param)` |
| 关键业务节点 | `INFO` | `log.info("订单 {} 支付成功", orderId)` |
| 外部接口调用 | `INFO`（成功）/ `ERROR`（失败） | `log.info("调用支付接口成功, cost={}ms", cost)` |
| 可自动恢复的异常 | `WARN` | `log.warn("数据库连接超时，尝试重连")` |
| 需要人工介入的错误 | `ERROR` | `log.error("订单创建失败，数据库异常", e)` |
| 系统级致命错误 | `FATAL` / `ERROR` | `log.error("无法启动服务，端口被占用", e)` |

### 2. 禁止使用字符串拼接

```java
// 错误：无论级别如何，字符串都会拼接
log.debug("Order: " + orderId + ", Status: " + status);

// 正确：使用占位符，仅在实际输出时拼接
log.debug("Order: {}, Status: {}", orderId, status);

// 更优：使用 Lambda 延迟计算（Log4j 2 / SLF4J 2.0）
log.debug("Order: {}, Status: {}",
    () -> getOrderId(),
    () -> getStatus());
```

### 3. 敏感信息脱敏

```java
import org.apache.commons.lang3.StringUtils;

public class SensitiveDataMasker {

    // 手机号脱敏: 138****1234
    public static String maskPhone(String phone) {
        if (StringUtils.isBlank(phone) || phone.length() < 7) {
            return phone;
        }
        return phone.substring(0, 3) + "****" + phone.substring(phone.length() - 4);
    }

    // 身份证号脱敏: 110***********1234
    public static String maskIdCard(String idCard) {
        if (StringUtils.isBlank(idCard) || idCard.length() < 8) {
            return idCard;
        }
        return idCard.substring(0, 3) + "***********" + idCard.substring(idCard.length() - 4);
    }

    // 银行卡号脱敏: **** **** **** 1234
    public static String maskBankCard(String bankCard) {
        if (StringUtils.isBlank(bankCard) || bankCard.length() < 4) {
            return bankCard;
        }
        return "**** **** **** " + bankCard.substring(bankCard.length() - 4);
    }

    // 邮箱脱敏: u***@example.com
    public static String maskEmail(String email) {
        if (StringUtils.isBlank(email) || !email.contains("@")) {
            return email;
        }
        String[] parts = email.split("@");
        String name = parts[0];
        if (name.length() <= 1) {
            return name + "***@" + parts[1];
        }
        return name.charAt(0) + "***@" + parts[1];
    }
}

// 使用示例
log.info("用户下单，手机号: {}, 邮箱: {}",
    SensitiveDataMasker.maskPhone(phone),
    SensitiveDataMasker.maskEmail(email));
```

### 4. 异常日志正确写法

```java
// 错误：异常信息丢失（堆栈不会输出）
log.error("操作失败: " + e.getMessage());

// 错误：打印堆栈但不包含有意义的消息
log.error("", e);

// 正确：消息 + 异常对象
log.error("订单 {} 支付失败，原因: {}", orderId, e.getMessage(), e);

// 推荐：使用占位符，异常作为最后一个参数
log.error("处理请求失败, userId={}, requestId={}", userId, requestId, e);
```

### 5. 日志量控制

```java
// 避免在循环中打印日志
// 错误
for (Order order : orders) {
    log.debug("处理订单: {}", order.getId()); // 可能产生海量日志
}

// 正确：使用采样或汇总
if (log.isDebugEnabled() && orders.size() < 100) {
    for (Order order : orders) {
        log.debug("处理订单: {}", order.getId());
    }
} else {
    log.info("批量处理 {} 个订单", orders.size());
}

// 使用限流日志
private static final RateLimiter LOG_RATE_LIMITER = RateLimiter.create(10); // 每秒10条

public void logWithRateLimit(String message) {
    if (LOG_RATE_LIMITER.tryAcquire()) {
        log.warn(message);
    }
}
```

### 6. 结构化日志 + MDC 链路追踪

```java
import org.slf4j.MDC;
import javax.servlet.*;
import java.io.IOException;
import java.util.UUID;

public class TraceIdFilter implements Filter {

    private static final String TRACE_ID_KEY = "traceId";

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {
        String traceId = UUID.randomUUID().toString().replace("-", "");
        try {
            MDC.put(TRACE_ID_KEY, traceId);
            chain.doFilter(request, response);
        } finally {
            MDC.remove(TRACE_ID_KEY);
        }
    }
}
```

配合日志格式，每条日志自动带上 traceId：

```
2025-06-04 10:30:45.123 [http-8080-1] INFO  OrderService [traceId=a1b2c3d4] - 订单创建成功
```

### 7. 生产环境检查清单

| 检查项 | 说明 |
|--------|------|
| 日志级别 | 生产环境至少 `INFO`，避免 `DEBUG` |
| 敏感信息 | 手机号、身份证、密码等必须脱敏 |
| 异常堆栈 | `ERROR` 级别必须包含异常堆栈 |
| 异步日志 | 高并发场景必须使用异步日志 |
| 日志滚动 | 必须配置按天滚动和大小限制 |
| 磁盘空间 | 监控日志目录大小，设置总容量上限 |
| includeLocation | 生产环境关闭代码位置信息 |
| 统一格式 | 全公司统一日志格式（推荐 JSON） |
| 日志集中化 | 接入 ELK/日志平台，不要只存在本地磁盘 |
