<!--
module:
  parent: system-design
  slug: system-design/java
  type: article
  category: 主模块子文章
  summary: Java 代码性能优化：代码逻辑、数据结构、JVM 调优、并发设计、I/O 操作、序列化工具等多维度系统工程方法论
  depth: ⭐⭐⭐
-->

# Java代码性能优化

---

> Java代码性能优化是一个系统工程，需要从代码逻辑、数据结构、JVM调优、并发设计、I/O操作等多个维度综合施策。

## 与 03 高可用 code-quality 的关系

本文聚焦**性能优化**(`03 高可用` 的 `code-quality` 关注可读性与鲁棒性,两者互补)。前者解决"跑得快"的问题,后者解决"写得对"的问题。实践中应同时关注二者,避免过度优化牺牲可维护性。

相关章节: [03 高可用 code-quality](../../03-high-availability/code-quality/README.md)。

## 代码逻辑与算法优化

- **减少重复计算**：将循环内不变的表达式提取到外部。
  ```java
  // 优化前
  for (int i = 0; i < list.size(); i++) {
      double value = Math.PI * list.get(i); // 每次循环都计算Math.PI
  }
  
  // 优化后
  final double pi = Math.PI;
  for (int i = 0; i < list.size(); i++) {
      double value = pi * list.get(i);
  }
  ```

- **选择高效数据结构**：根据场景选择`ArrayList`（随机访问快）、`LinkedList`（频繁插入删除）或`ConcurrentHashMap`（高并发）。
  ```java
  // 高并发场景下，ConcurrentHashMap比synchronizedMap性能更好
  Map<String, Integer> map = new ConcurrentHashMap<>();
  ```

- **避免自动装箱/拆箱**：使用基本类型代替包装类，减少对象创建。
  ```java
  int sum = 0; // 优于Integer sum = 0;
  ```

## JVM调优

- **堆内存设置**：根据应用需求调整`-Xms`（初始堆）和`-Xmx`（最大堆），避免频繁GC。
  ```bash
  java -Xms512m -Xmx2048m -jar app.jar
  ```

- **选择垃圾回收器**：
    - **G1 GC**：适合大堆（>4GB）和低延迟场景（`-XX:+UseG1GC`）。
    - **ZGC**：适用于超低延迟（<10ms暂停），如`-XX:+UseZGC`。
    - **调整GC参数**：如`-XX:MaxGCPauseMillis=200`限制最大GC暂停时间。

**GC 调优场景化推荐**：
- `-Xmx` 一般设为可用内存的 60%~75%，留足系统 + 元空间余量
- 堆 < 4GB：Parallel GC 吞吐优先（JDK 8 默认）
- 堆 4~16GB + 暂停 SLA ≤ 200ms：G1 GC（JDK 9+ 默认）
- 堆 > 16GB + 暂停 SLA ≤ 10ms：ZGC / Shenandoah（JDK 17 LTS 推荐）
- 微服务冷启动敏感：考虑 GraalVM Native Image 或 JDK 21 的 CDS + AppCDS

### JDK 版本与 GC 演进对比

| **JDK 版本** | **默认 GC** | **可选新 GC** | **典型暂停时间** | **适用场景** |
|---|---|---|---|---|
| JDK 8 | Parallel GC | G1（实验） | Parallel: 数十~数百 ms | 传统单体服务 |
| JDK 11 | G1 GC | ZGC（实验）/ Shenandoah | G1: ≤ 200ms | 中大型后端服务 |
| JDK 17 (LTS) | G1 GC | ZGC（生产）/ Shenandoah | ZGC: 亚毫秒级 | 金融/实时交易 |
| JDK 21 (LTS) | G1 GC | ZGC 分代（默认新一代）| ZGC Gen: < 1ms | 大规模 LLM 推理后端 |

- **启用JIT编译优化**：使用`-XX:+TieredCompilation`（默认开启）结合解释执行与编译执行，提升热点代码性能。

## 并发编程优化

- **线程池合理配置**：避免线程过多导致上下文切换开销。
  ```java
  // 使用ThreadPoolExecutor，设置核心线程数、最大线程数、队列容量
  ExecutorService executor = new ThreadPoolExecutor(
      10, // 核心线程数
      50, // 最大线程数
      60, TimeUnit.SECONDS,
      new ArrayBlockingQueue<>(1000) // 任务队列
  );
  ```

- **无锁数据结构**：在高竞争场景下，使用`AtomicInteger`、`LongAdder`或`ConcurrentHashMap`减少锁竞争。
  ```java
  // 高并发计数场景，LongAdder比AtomicLong性能更好
  LongAdder counter = new LongAdder();
  counter.increment();
  ```

- **减少锁粒度**：使用分段锁（如`ConcurrentHashMap`）或锁升级（偏向锁→轻量级锁→重量级锁）。

## I/O与网络优化

- **使用缓冲流**：减少I/O次数，提升文件读写效率。
  ```java
  try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"))) {
      String line;
      while ((line = reader.readLine()) != null) {
          // 处理行数据
      }
  }
  ```

- **异步非阻塞I/O**：使用Java NIO或Netty框架处理高并发网络请求。
  ```java
  // NIO示例：使用Selector监听多个Channel
  Selector selector = Selector.open();
  ServerSocketChannel serverChannel = ServerSocketChannel.open();
  serverChannel.register(selector, SelectionKey.OP_ACCEPT);
  ```

## 内存与对象管理

- **对象复用**：对昂贵对象（如数据库连接、线程）使用对象池（如`HikariCP`连接池）。
  ```java
  // HikariCP连接池配置
  HikariConfig config = new HikariConfig();
  config.setJdbcUrl("jdbc:mysql://localhost:3306/db");
  config.setMaximumPoolSize(20);
  HikariDataSource dataSource = new HikariDataSource(config);
  ```

- **避免内存泄漏**：及时释放资源（如`Closeable`接口的`close()`方法），使用弱引用（`WeakReference`）管理缓存。

## 工具辅助分析

- **性能分析工具**：
    - **JProfiler/VisualVM**：分析CPU、内存、GC、线程等指标。
    - **JMH（Java Microbenchmark Harness）**：精准测量代码微基准性能。
    - **Arthas**：在线诊断工具，支持堆栈跟踪、内存泄漏检测。

- **日志优化**：避免循环内打印日志，使用占位符（如SLF4J的`{}`）减少字符串拼接。
  ```java
  log.debug("Processing order: {}", orderId); // 优于log.debug("Processing order: " + orderId);
  ```

## 其他高级优化

- **编译优化**：使用GraalVM提前编译（AOT）为本地镜像，减少启动时间。
- **序列化优化**：使用Kryo、Protobuf等高效序列化框架，替代Java原生序列化。
- **缓存策略**：本地缓存（如Guava Cache）或分布式缓存（如Redis）减少重复计算。

### 序列化框架对比

| **维度** | **Java 原生** | **Kryo** | **Protobuf** |
|---|---|---|---|
| **序列化体积** | 大（含完整类元数据） | 小（约原生的 1/3~1/5） | 小（约原生的 1/3~1/2） |
| **吞吐量** | 低 | 高（单线程可达数十 MB/s） | 高 |
| **跨语言** | ❌ 仅 Java | ❌ 仅 JVM 系 | ✅ 官方支持 10+ 语言 |
| **Schema 演进** | ❌ 字段变动易不兼容 | ⚠ 需注册 ID | ✅ field number 天然向前兼容 |
| **典型场景** | RMI/EJB 遗留 | Dubbo 内部 RPC、缓存序列化 | gRPC、跨语言 API、持久化 |

> **建议**：JVM 内部高性能场景首选 Kryo；跨语言/对外 API/长期持久化首选 Protobuf；避免在生产系统继续使用 Java 原生序列化。

**总结**：性能优化需结合具体场景，通过性能测试工具定位瓶颈，再针对性优化。优先优化热点代码（帕累托法则：20%的代码消耗80%的资源），避免过度优化。同时，保持代码可读性与可维护性，避免为了性能牺牲代码质量。

← [返回 高性能设计](../README.md)
