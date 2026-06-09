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
