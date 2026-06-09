# 数据库连接池

> 数据库连接池通过预先创建并复用连接,避免每次请求都进行 TCP 握手和身份认证,Spring Boot 2.x+ 默认使用 HikariCP,监控与防 SQL 注入场景推荐 Druid。

> 最后更新: 2026-06-09

---

## 一、为什么需要连接池

| 操作 | 耗时 |
|------|------|
| 创建数据库连接（TCP 握手 + 认证） | 1~10ms |
| 执行一条简单 SQL | 0.1~1ms |
| 关闭连接 | 0.5~2ms |

每次请求都新建连接，开销远大于 SQL 执行本身。连接池通过**复用连接**解决这个问题。

```
无连接池：请求 → 创建连接 → 执行 SQL → 关闭连接（每次 3~12ms 开销）
有连接池：请求 → 从池中获取连接 → 执行 SQL → 归还连接（几乎 0 开销）
```

---

## 二、主流连接池对比

| 特性 | HikariCP | Druid | C3P0 | DBCP2 |
|------|----------|-------|------|-------|
| **性能** | ⭐⭐⭐⭐⭐ 最快 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **稳定性** | 高 | 高 | 一般 | 一般 |
| **监控** | 基础 | 丰富（内置 Web UI） | 无 | 无 |
| **Star** | GitHub 20k+ | GitHub 28k+ | 老旧 | Apache |
| **Spring Boot 默认** | ✅ | 需手动配置 | - | - |
| **SQL 防火墙** | ❌ | ✅ | ❌ | ❌ |
| **慢 SQL 监控** | ❌ | ✅ | ❌ | ❌ |

> **Spring Boot 2.x+ 默认使用 HikariCP**，阿里内部推荐使用 Druid（监控能力强）。

---

## 三、HikariCP

### Spring Boot 配置

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=UTC
    username: root
    password: 123456
    hikari:
      maximum-pool-size: 20          # 最大连接数
      minimum-idle: 5                # 最小空闲连接
      idle-timeout: 600000           # 空闲连接超时（10分钟）
      max-lifetime: 1800000          # 连接最大生命周期（30分钟）
      connection-timeout: 30000      # 获取连接超时（30秒）
      pool-name: MyHikariPool
```

### 关键参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `maximum-pool-size` | 10 | 池中最大连接数（推荐公式：CPU 核数 * 2 + 磁盘数） |
| `minimum-idle` | 与 max 相同 | 最小空闲连接 |
| `idle-timeout` | 600000 (10min) | 空闲连接回收时间 |
| `max-lifetime` | 1800000 (30min) | 连接最大存活时间（**必须小于数据库的 wait_timeout**） |
| `connection-timeout` | 30000 (30s) | 获取连接的最大等待时间 |
| `leak-detection-threshold` | 0 (关闭) | 连接泄漏检测阈值（建议开发环境设为 2000ms） |

### 为什么 HikariCP 最快

1. **字节码精简**：使用 Javassist 生成代理，比 JDK 动态代理和 CGLIB 更快
2. **FastList**：自定义 ArrayList，去掉范围检查
3. **无锁集合**：使用 ConcurrentBag + ThreadLocal 减少锁竞争
4. **集合初始化**：预分配集合容量，避免扩容

---

## 四、Druid

### Maven 依赖

```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>druid-spring-boot-starter</artifactId>
    <version>1.2.20</version>
</dependency>
```

### Spring Boot 配置

```yaml
spring:
  datasource:
    type: com.alibaba.druid.pool.DruidDataSource
    druid:
      initial-size: 5                # 初始连接数
      min-idle: 5                    # 最小空闲连接
      max-active: 20                 # 最大活跃连接
      max-wait: 60000                # 获取连接最大等待时间
      # 监控配置
      stat-view-servlet:
        enabled: true
        url-pattern: /druid/*
        login-username: admin
        login-password: admin123
      filter:
        stat:
          enabled: true
          slow-sql-millis: 2000      # 慢 SQL 阈值
        wall:
          enabled: true              # SQL 防火墙
```

### Druid 独有功能

| 功能 | 说明 |
|------|------|
| **SQL 监控** | 统计每条 SQL 的执行次数、耗时、结果集行数 |
| **慢 SQL 监控** | 自动识别超过阈值的慢 SQL |
| **SQL 防火墙** | 防 SQL 注入、限制危险操作（如 DROP TABLE） |
| **URI 监控** | 按 URL 统计数据库访问情况 |
| **Session 监控** | 查看当前活跃 Session |
| **Spring 监控** | 按 Spring Bean 统计数据库调用 |

> 访问 `http://localhost:8080/druid/` 查看 Druid 监控面板。

---

## 五、连接池参数调优

### 最大连接数计算

**PostgreSQL 官方公式**：

```
connections = (core_count * 2) + effective_spindle_count
```

- `core_count`：CPU 核数
- `effective_spindle_count`：磁盘数（SSD 算 1）

示例：8 核 CPU + 1 块 SSD → `max_pool_size = 8 * 2 + 1 = 17`

### 常见配置建议

| 场景 | max-active | 说明 |
|------|:----------:|------|
| 小型应用 | 10~20 | 低并发 |
| 中型应用 | 20~50 | 中等并发 |
| 大型应用 | 50~100 | 高并发（配合读写分离） |

> **连接数不是越大越好**！过多连接会导致数据库端上下文切换增加，反而降低吞吐。

### 连接泄漏检测

```yaml
# HikariCP
hikari:
  leak-detection-threshold: 5000   # 连接获取后 5 秒未归还则报警

# Druid
druid:
  remove-abandoned: true
  remove-abandoned-timeout: 30     # 30 秒未归还则强制回收
  log-abandoned: true              # 记录日志
```

---

## 六、最佳实践

1. **Spring Boot 项目默认使用 HikariCP**，无需额外配置
2. **需要监控能力时选择 Druid**，特别是生产环境排查问题
3. **max-lifetime 必须小于数据库端的连接超时时间**（MySQL 默认 `wait_timeout = 28800s`）
4. **开发环境开启连接泄漏检测**，防止连接未归还
5. **合理设置最大连接数**，参考 CPU 核数公式
6. **配合数据库监控**,观察连接池状态和 SQL 执行情况

---

## 七、连接池监控指标详解

### 1. 核心指标

| 指标 | 含义 | 告警阈值 |
|------|------|---------|
| **活跃连接数** | 正在执行 SQL 的连接 | 持续接近 max-pool-size |
| **空闲连接数** | 池中可用连接 | 接近 min-idle 即可 |
| **等待连接数** | `getConnection()` 阻塞中线程 | > 0 持续 5s 需告警 |
| **获取连接耗时 P99** | `getConnection()` 99 分位耗时 | > 100ms 需关注 |
| **连接使用率** | 活跃/总数 | > 80% 需扩容 |

### 2. HikariCP 指标(Micrometer)

```yaml
# application.yml
management:
  metrics:
    enable:
      hikaricp: true
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
```

```bash
# 访问 Prometheus 端点
curl http://localhost:8080/actuator/prometheus | grep hikaricp
# hikaricp_connections_active 12.0
# hikaricp_connections_idle 3.0
# hikaricp_connections_pending 0.0
# hikaricp_connections_usage_seconds_max 0.045
```

### 3. Druid 监控面板

Druid 自带 Web 界面(`/druid/`),可查看:
- 数据源实时状态(活跃/空闲/等待数)
- SQL 执行统计(次数、耗时、慢 SQL)
- URI 监控
- Spring 监控(按 Bean 统计)
- Session 监控

---

## 八、连接池常见问题排查

### 1. 连接泄漏(Connection Leak)

**现象**:活跃连接数缓慢增长直至打满,新请求阻塞。

**定位**:
```java
// 启用 HikariCP 泄漏检测
hikari:
  leak-detection-threshold: 5000  // 5 秒未归还则报警
```

日志输出示例:
```
Connection leak detection triggered for connection
org.sql.core.Connection@12345, stack trace follows
    at com.example.UserDao.insert(UserDao.java:42)
    at com.example.UserService.create(UserService.java:18)
    ...
```

**根因**:连接未在 `finally` 块关闭,或 Spring `@Transactional` 失效。

**修复**:
```java
// 正确写法
try (Connection conn = dataSource.getConnection()) {
    // 业务代码
}  // 自动 close

// 或使用 Spring 模板
jdbcTemplate.update("INSERT ...", params);
```

### 2. 慢 SQL 阻塞连接池

**现象**:单条慢 SQL 执行 30s+,期间所有连接被占用,新请求超时。

**诊断**:
```sql
-- MySQL 查看正在执行的 SQL
SHOW PROCESSLIST;

-- 查看锁等待
SELECT * FROM information_schema.INNODB_TRX;
```

**修复**:
- SQL 优化(加索引、避免全表扫描)
- 设置 `connection-timeout` 快速失败
- 读写分离,慢查询走从库

### 3. 连接数打满

**现象**:`HikariPool-1 - Connection is not available, request timed out after 30000ms`

**根因清单**:
- max-pool-size 设置过小
- 应用服务器数量 × max-pool-size > 数据库 `max_connections`
- 连接泄漏(见上)
- 慢 SQL 占用

**修复步骤**:
1. 检查活跃连接数(`hikaricp_connections_active`)
2. 检查 MySQL `SHOW PROCESSLIST`
3. 分析是否存在泄漏
4. 评估是否扩容或读写分离

---

## 九、其他主流连接池

| 连接池 | 特点 | 适用 |
|--------|------|------|
| **HikariCP** | Java 性能最快,极简 | **Spring Boot 默认** |
| **Druid** | 监控 + SQL 防火墙,功能全面 | 阿里系、复杂生产 |
| **Tomcat JDBC Pool** | Tomcat 内置,功能中规中矩 | Tomcat 部署 |
| **Vibur DBCP** | 异步支持,监控完善 | 中小项目 |
| **FlexyPool** | 连接池指标分析,故障注入测试 | 调优诊断 |
| **Dbcp2** | Apache Commons 经典 | 旧项目维护 |

### Tomcat JDBC Pool 关键配置

```yaml
spring:
  datasource:
    type: org.apache.tomcat.jdbc.pool.DataSource
    tomcat:
      max-active: 50
      max-idle: 20
      min-idle: 5
      max-wait: 10000
      test-on-borrow: true        # 借出时校验(影响性能)
      test-while-idle: true       # 空闲时校验
      time-between-eviction-runs-millis: 30000
```

---

## 十、Druid 加密密码

生产环境数据库密码必须加密,避免明文配置泄露。

```bash
# 1. 生成加密密码
java -cp druid-1.2.20.jar com.alibaba.druid.filter.config.ConfigTools your_password
# 输出: privateKey / publicKey / password

# 2. application.yml
spring:
  datasource:
    druid:
      username: admin
      password: ${加密后的密码}
      filters: config       # 启用配置过滤
      connection-properties: config.decrypt=true;config.decrypt.key=${publicKey}
```

> **进阶**:**密码托管到 Vault/K8s Secret**,应用启动时从密钥管理服务拉取,实现"代码与密钥分离"。

---

## 十一、分库分表场景下的连接池

使用 ShardingSphere-JDBC 等分库分表中间件时,**每个分片都是独立连接池**。

### ShardingSphere 配置

```yaml
spring:
  shardingsphere:
    datasource:
      names: ds0,ds1,ds2,ds3
      ds0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://10.0.0.1:3306/order_0
        maximum-pool-size: 20
      ds1:
        # ... 同上,指向 order_1
    rules:
      sharding:
        tables:
          orders:
            actual-data-nodes: ds${0..3}.orders_${0..15}
            table-strategy:
              standard:
                sharding-column: user_id
                sharding-algorithm-name: user-mod
            key-generate-strategy:
              column: id
              key-generator-name: snowflake
```

### 关键原则

- **每个分片连接池独立配置**(避免某个分片打满牵连其他)
- **小表广播表**(字典表)使用单独的连接池
- **连接数总预算**:应用实例数 × 实例 max-pool × 分片数 ≤ DB `max_connections`

---

## 十二、连接池与事务的协作

### 1. Spring `@Transactional` 何时归还连接

```java
@Transactional
public void orderProcess() {
    updateOrder();        // 持有连接
    callPaymentService(); // 嵌套调用,可能获取新连接或加入当前
    sendNotification();   // 同事务,共享连接
    // 方法返回 → 事务提交 → 连接归还
}
```

- `@Transactional` 方法执行期间,连接被**独占**
- 方法返回(无论成功或异常)后,连接**释放**到池
- 异常 + `@Transactional(rollbackFor=...)` → 回滚 → 连接归还

### 2. 事务内外部调用连接池行为

```java
@Transactional
public void outer() {
    // 持有连接
    otherService.call();  // 独立事务/无事务,可能获取新连接
    // outer 事务结束 → 归还
}
```

若 `otherService` 也是 `@Transactional(REQUIRED)`,则加入当前事务(共用连接);若 `REQUIRES_NEW`,则新开连接。

### 3. 异步与连接池

`@Async` 方法在独立线程执行,**新事务 + 新连接**。若异步方法内部持锁操作,需注意:

```java
@Transactional
public void syncMethod() {
    // 主线程,连接 A
    asyncService.processAsync();  // 异步线程,连接 B
}
```

> **避免**在 `@Transactional` 中调用本服务的 `@Async` 方法(代理失效,实际是同步调用)。

---

## 相关章节

- [数据库基础知识](../01-fundamentals/README.md) — 数据库核心概念
- [MySQL](../05-mysql/README.md) — MySQL `wait_timeout` 与连接池参数协调
- [事务与并发控制](../03-transaction/README.md) — 事务与连接池的协作
- [系统设计 · 连接池](../../04.system-design/04-high-performance/connection-pool/README.md) — 架构视角的连接池调优

## 参考资料

- [HikariCP GitHub README](https://github.com/brettwooldridge/HikariCP)
- [HikariCP - About Pool Sizing](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing)
- [Druid 官方 Wiki](https://github.com/alibaba/druid/wiki)
- [PostgreSQL Wiki - Tuning Your PostgreSQL Server](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server) — 连接数公式来源
