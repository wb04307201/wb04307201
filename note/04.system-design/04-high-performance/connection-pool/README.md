# 连接池优化

> 连接池是管理数据库/Redis 连接复用的核心组件。合理的连接池配置能显著提升系统吞吐量，不当配置则可能导致连接泄漏、连接耗尽等严重问题。
>
> 最后更新: 2026-06-09

## 目录

- [1. 为什么需要连接池](#1-为什么需要连接池)
- [2. HikariCP 核心参数详解](#2-hikaricp-核心参数详解)
- [3. 连接池调优建议](#3-连接池调优建议)
- [4. 常见问题与解决方案](#4-常见问题与解决方案)
- [5. 数据库连接池 vs Redis 连接池](#5-数据库连接池-vs-redis-连接池)

---

## 1. 为什么需要连接池

### 1.1 连接的成本

创建一个数据库连接需要经历：
```
TCP 三次握手(1个RTT) → MySQL 握手认证 → 分配连接资源 → 初始化 Session
```
一次完整的连接建立通常需要 **20~30ms**，在高并发场景下，如果每次请求都新建连接，连接建立将成为性能瓶颈。

### 1.2 连接池的价值

| 指标 | 无连接池 | 有连接池 |
|------|---------|---------|
| 获取连接耗时 | 20~30ms | < 1ms |
| 连接复用 | 无 | 有，复用已有连接 |
| 连接数控制 | 不可控，可能打满DB | 精确控制最大连接数 |
| 连接泄漏检测 | 困难 | 自动检测+回收 |

### 1.3 工作原理

```
应用线程                连接池                    数据库
  |                      |                          |
  |--borrowConnection--->|                          |
  |                      |←─从空闲队列取连接─────────|
  |<──connection(已存在)──|                          |
  |                      |                          |
  |──执行业务SQL────────────────────────────────────>|
  |<──返回结果───────────────────────────────────────|
  |                      |                          |
  |--returnConnection---->|                          |
  |                      |←─归还到空闲队列───────────|
```

---

## 2. HikariCP 核心参数详解

HikariCP 是目前最快的 Java 数据库连接池，也是 Spring Boot 2.0+ 的默认连接池。

### 2.1 核心参数

| 参数 | 默认值 | 推荐值 | 说明 |
|------|--------|--------|------|
| **maximumPoolSize** | 10 | `CPU核心数 × 2 + 磁盘数` | 池中最大连接数，最重要的参数 |
| **minimumIdle** | 与 maximumPoolSize 相同 | 与 maximumPoolSize 相同 | 最小空闲连接数，建议不设空闲 |
| **connectionTimeout** | 30000ms | 3000~5000ms | 获取连接超时时间 |
| **idleTimeout** | 600000ms(10min) | 600000ms | 空闲连接存活时间 |
| **maxLifetime** | 1800000ms(30min) | 比DB超时小30s | 连接最大生命周期 |
| **validationTimeout** | 5000ms | 3000ms | 连接有效性检查超时 |
| **leakDetectionThreshold** | 0(关闭) | 60000ms | 连接泄漏检测阈值 |

### 2.2 参数详解

#### maximumPoolSize — 最大连接数

HikariCP 作者 Brett Wooldridge 给出的公式：

```
pool size = CPU核心数 × 2 + 磁盘数
```

**原因**: 数据库连接大部分时间在等待 I/O，不是 CPU 密集型。连接数过多反而会增加数据库的锁竞争和上下文切换开销。

> **存储介质参考值**: SSD 推荐 8-16;HDD 或远程 DB 需更保守,通常 4-8。这是因为 SSD IOPS 高(数万~数十万),可承受更多并发连接;HDD 随机 IOPS 有限(数百),过多连接会因磁盘争用导致延迟飙升。

```yaml
# application.yml 示例
spring:
  datasource:
    hikari:
      maximum-pool-size: 20    # 8核 × 2 + 1(SSD) ≈ 17,取20
      minimum-idle: 20         # 不设空闲,保持满载
```

**常见误区**: 认为连接池越大越好。实际上 MySQL 默认 `max_connections=151`，如果一个应用池配 100，3 个应用就能把 DB 打满。

#### minimumIdle — 最小空闲连接数

- HikariCP 推荐设为与 `maximumPoolSize` 相同（即固定大小连接池）
- 不设空闲连接可以避免连接数频繁伸缩带来的性能抖动

#### connectionTimeout — 获取连接超时

- 默认 30s 太长，建议 **3~5 秒**
- 超时说明连接池已满且没有空闲连接，应该快速失败而不是长时间等待
- 超时后应触发告警，而不是默默等待

#### maxLifetime — 连接最大生命周期

```
maxLifetime 必须 < MySQL wait_timeout
```

- MySQL 默认 `wait_timeout = 28800s(8小时)`
- 建议设置为 `28800 - 30 = 28770s` 或直接使用默认的 30 分钟
- 短生命周期有助于及时释放有问题的连接

#### leakDetectionThreshold — 连接泄漏检测

```yaml
spring:
  datasource:
    hikari:
      leak-detection-threshold: 60000  # 60秒未归还视为泄漏
```

开启后，如果连接超过指定时间未归还，会在日志中打印警告并输出获取连接的堆栈。

### 2.3 完整配置示例

```yaml
spring:
  datasource:
    hikari:
      # 核心参数
      maximum-pool-size: 20
      minimum-idle: 20
      connection-timeout: 5000
      idle-timeout: 600000
      max-lifetime: 1800000
      # 高级参数
      validation-timeout: 3000
      leak-detection-threshold: 60000
      connection-test-query: SELECT 1  # JDBC4驱动可省略
      pool-name: MyHikariPool
```

---

## 3. 连接池调优建议

### 3.1 调优步骤

```
Step 1: 监控当前连接池使用情况
   ├── 活跃连接数
   ├── 等待队列长度
   ├── 连接获取耗时
   └── 连接泄漏告警

Step 2: 分析数据库端瓶颈
   ├── 慢查询分析
   ├── 锁等待分析
   └── 连接数使用率

Step 3: 逐步调整连接池大小
   ├── 从默认 10 开始
   ├── 压测观察 QPS 和延迟
   ├── 逐渐增大直到 QPS 不再提升
   └── 记住：不是越大越好

Step 4: 验证调整效果
   ├── 压测对比(调整前后)
   ├── 监控告警数量变化
   └── 确认无连接泄漏
```

### 3.2 调优参考表

| 业务类型 | maximumPoolSize | connectionTimeout | 说明 |
|---------|----------------|-------------------|------|
| 低并发后台管理 | 5~10 | 5000ms | 请求少，小池即可 |
| 一般业务服务 | 15~25 | 5000ms | 8核服务器的推荐值 |
| 高并发读服务 | 20~30 | 3000ms | 查询多，可适当增大 |
| 高并发写服务 | 10~15 | 3000ms | 写入慢，不宜连接太多 |
| 微服务调用链 | 10~15 | 2000ms | 链路长，需快速失败 |

---

## 4. 常见问题与解决方案

### 4.1 连接泄漏(Connection Leak)

**现象**: 连接池连接逐渐耗尽，最终所有请求超时。

**原因**: 代码中获取连接后未在 finally 块中关闭/归还。

```java
// ❌ 错误写法: 异常时连接不会归还
Connection conn = dataSource.getConnection();
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT ...");
// 如果这里抛异常, conn 不会归还

// ✅ 正确写法: try-with-resources
try (Connection conn = dataSource.getConnection();
     Statement stmt = conn.createStatement();
     ResultSet rs = stmt.executeQuery("SELECT ...")) {
    while (rs.next()) {
        // 处理结果
    }
} // 自动归还连接
```

**检测**: 开启 `leakDetectionThreshold`，定期审查告警日志。

### 4.2 连接风暴(Connection Storm)

**现象**: 系统重启或连接池重置后，大量线程同时申请连接，瞬间打满连接池。

**原因**: 连接池初始化策略不当，所有连接在启动后集中创建。

**解决方案**:
- 设置 `initializationFailTimeout = -1` 延迟初始化
- 使用 `minimumIdle` 预热部分连接
- 逐步增加连接（HikariCP 默认行为）

### 4.3 连接耗尽(Connection Exhaustion)

**现象**: 应用日志出现 `HikariPool-1 - Connection is not available, request timed out after 30000ms`

**排查步骤**:
```
1. 检查 maximumPoolSize 是否合理
2. 检查是否有慢查询占用连接过久
3. 检查是否有连接泄漏
4. 检查 DB 端 max_connections 是否已满
5. 检查是否有连接未正确归还(MyBatis/Spring事务管理问题)
```

### 4.4 连接失效(Connection Stale)

**现象**: 从池中取出的连接已断开，执行 SQL 时报错。

**原因**: 数据库端超时断开了连接，但连接池不知道。

**解决方案**:
```yaml
spring:
  datasource:
    hikari:
      max-lifetime: 1800000    # 设置合理的连接生命周期
      validation-timeout: 3000 # 获取连接前快速验证
      # 或使用 connection-test-query 主动检测
      connection-test-query: SELECT 1
```

---

## 5. 数据库连接池 vs Redis 连接池

| 维度 | 数据库连接池 (HikariCP) | Redis 连接池 (Lettuce/Jedis) |
|------|------------------------|------------------------------|
| **连接成本** | 高(20~30ms, 握手+认证+Session) | 低(1~3ms, 简单TCP) |
| **连接池大小** | CPU × 2 + 磁盘数(较小) | 可更大(50~200)，因为操作快 |
| **连接复用** | 必须(成本高) | 必须(避免频繁创建) |
| **推荐池** | HikariCP | Lettuce(Netty,异步)/JedisPool |
| **超时设置** | 3~5s | 1~3s(应该更快) |
| **健康检查** | connection-test-query | PING 命令 |
| **管道支持** | 无 | Lettuce 支持 Pipeline |
| **集群支持** | 通常单数据源 | Lettuce 原生支持 Cluster/哨兵 |

### 5.1 Lettuce 连接池配置示例 (Spring Boot)

```yaml
spring:
  data:
    redis:
      lettuce:
        pool:
          max-active: 50      # 最大连接数
          max-idle: 20        # 最大空闲连接
          min-idle: 5         # 最小空闲连接
          max-wait: 2000ms    # 获取连接超时
        shutdown-timeout: 100ms
```

### 5.2 关键区别总结

1. **连接池大小**: 数据库连接池宜小(10~25)，Redis 连接池可大(20~100)，因为 Redis 操作更快、连接成本更低
2. **超时时间**: 数据库连接超时 3~5s，Redis 应该 1~2s（Redis 操作应该是亚毫秒级）
3. **集群**: 数据库通常单数据源或主从，Redis 需要支持 Cluster/哨兵/分片
4. **Pipeline**: Redis 支持 Pipeline 批量操作，可以大幅减少连接获取次数

## 相关章节

- [数据库分库分表](../database-optimization/db-sharding/README.md) — 分片后多数据源连接池管理
- [数据库读写分离](../database-optimization/read-write-splitting/README.md) — 主从库各自的连接池配置
- [缓存设计模式](../cache-patterns/README.md) — Redis 连接池与缓存策略的搭配
- [SQL 优化](../database-optimization/sql/README.md) — 减少慢查询以降低连接池压力
- [Java 性能优化](../java/README.md) — 连接泄漏检测与 JVM 调优
