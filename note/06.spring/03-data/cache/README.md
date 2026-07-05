<!--
module:
  parent: spring
  slug: spring/cache
  type: article
  category: 主模块子文章
  summary: Spring Cache 4 大模式 + 多级缓存 + 序列化选型。
-->

# Spring Cache 缓存

> ⬅️ [返回 03 数据层](../README.md)

---
---

## 🎯 一句话定位

**Spring Cache = 缓存的"抽象层"**——业务代码用统一的注解（@Cacheable、@CachePut、@CacheEvict），**底层实现可自由切换**（Caffeine、Redis、Ehcache）。通过声明式的方式实现方法结果的缓存，**业务代码与缓存实现完全解耦**。

---

## 📚 章节导航

| 章节 | 核心问题 | 阅读时长 |
|:-----|:---------|:--------:|
| [缓存注解与使用](annotations-and-usage.md) | 5 大注解怎么用？SpEL 怎么写？ | 15 min |
| [缓存实现与最佳实践](implementations-and-best-practices.md) | Caffeine/Redis/Ehcache 怎么选？4 大高级特性？ | 15 min |
| [缓存 4 大模式](patterns.md) | Cache-Aside / Read-Through / Write-Through / Write-Behind 怎么选？ | 15 min |
| [多级缓存与防护](multi-level.md) | L1+L2 架构？穿透/击穿/雪崩如何防御？ | 15 min |
| [Redis 序列化](serialization.md) | 5 大序列化器怎么选？多态与 Schema 演进？ | 12 min |
| [@Cacheable 降级与恢复](cache-degradation-and-recovery.md) | Redis 挂了怎么办？4 大方案 + 自动恢复 + 数据一致性 | 18 min |

---

## 一、什么是 Spring Cache

> **Spring Cache** 是 Spring Framework 提供的一个**抽象层**，用于简化应用程序中的缓存操作。它允许开发者在**不修改业务逻辑代码**的情况下，通过简单的注解实现方法调用结果的缓存和检索。

### 4 大核心特性

- **基于注解的配置**：使用 `@Cacheable`, `@CacheEvict` 等注解
- **统一抽象层**：支持多种缓存实现（Ehcache, Redis, Caffeine 等）
- **透明集成**：与 Spring 事务管理类似，对业务代码透明
- **细粒度控制**：支持条件缓存、过期时间、自定义 key 等

### 抽象层思想

```mermaid
graph TB
    Biz[业务代码] --> Annot[注解<br/>@Cacheable]
    Annot --> Abs[Spring Cache 抽象层<br/>CacheManager]
    Abs --> C1[Caffeine<br/>单机内存]
    Abs --> C2[Redis<br/>分布式]
    Abs --> C3[Ehcache<br/>兼容老项目]
    Abs --> C4[Hazelcast<br/>内存网格]

    style Biz fill:#e3f2fd,stroke:#1976d2
    style Abs fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

> 📌 **业务永远面向 Cache 抽象编程**——切换缓存实现**不改业务代码**。

---

## 二、为什么需要 Spring Cache

### 没有缓存时的痛点

```java
// 每个查询都要写：先查 Redis，命中返回；未命中查 DB，写入 Redis
public User getById(Long id) {
    User user = redis.get("user:" + id);
    if (user == null) {
        user = userRepository.findById(id).orElse(null);
        if (user != null) {
            redis.setex("user:" + id, 600, user);
        }
    }
    return user;
}
```

- 每个方法都要写**重复的缓存逻辑**
- 缓存逻辑和业务逻辑**混在一起**
- 改缓存策略要改 N 个文件

### 使用 Spring Cache 后的简洁

```java
@Cacheable(value = "users", key = "#id")
public User getById(Long id) {
    return userRepository.findById(id).orElse(null);
}
```

- **一行注解**搞定
- 业务代码**完全无感知**
- 切换缓存实现不改业务代码

---

## 三、3 大主流实现速览

| 实现 | 类型 | 性能 | 分布式 | 适用 |
|------|------|:----:|:------:|------|
| **Caffeine** | 内存 | ⭐⭐⭐⭐⭐ | ❌ | **单机默认** |
| **Redis** | 内存 | ⭐⭐⭐⭐ | ✅ | **分布式集群** |
| **Ehcache** | 内存+磁盘 | ⭐⭐⭐ | ✅ | 老项目、持久化 |
| **Memcached** | 内存 | ⭐⭐⭐⭐ | ✅ | 简单 K-V 缓存，多语言共享 — 详见 implementations-and-best-practices.md |
| **Hazelcast** | 内存网格 | ⭐⭐⭐⭐ | ✅ | 分布式内存计算 + 嵌入式部署 — 详见 implementations-and-best-practices.md |

> 详细对比见 [缓存实现与最佳实践](implementations-and-best-practices.md)

---

## 四、5 大注解速览

| 注解 | 作用 | 方法是否总执行 |
|------|------|:------------:|
| @Cacheable | **读缓存**（先查缓存） | ❌ 命中跳过 |
| @CachePut | **写缓存**（更新） | ✅ |
| @CacheEvict | **清缓存** | ✅ |
| @Caching | 组合多个缓存操作 | - |
| @CacheConfig | 类级缓存配置 | - |

> 详细用法见 [缓存注解与使用](annotations-and-usage.md)

```java
@Service
@CacheConfig(cacheNames = "users")
public class UserService {

    @Cacheable(key = "#id")                              // 读
    public User getById(Long id) { ... }

    @CachePut(key = "#user.id")                          // 写
    public User update(User user) { ... }

    @CacheEvict(key = "#id")                             // 删
    public void delete(Long id) { ... }
}
```

---

## 五、整体知识图谱

```mermaid
graph TB
    SC[Spring Cache] --> Annot[5 大注解]
    SC --> Abs[CacheManager 抽象]
    SC --> Best[7 大最佳实践]

    Annot --> Cacheable[@Cacheable<br/>读]
    Annot --> CachePut[@CachePut<br/>写]
    Annot --> CacheEvict[@CacheEvict<br/>删]
    Annot --> Caching[@Caching<br/>组合]
    Annot --> CacheConfig[@CacheConfig<br/>类级]

    Abs --> Caffeine
    Abs --> Redis
    Abs --> Ehcache
    Abs --> Custom[自定义]

    Best --> TTL[合理过期时间]
    Best --> PEN[防穿透]
    Best --> AVA[防雪崩]
    Best --> BR[防击穿]
```

---

## 六、缓存适用场景与不适用场景

### ✅ 适用场景

- 读多写少（**典型：商品详情、用户信息**）
- 性能要求高（**减少 DB 查询**）
- 数据容忍短时不一致（**最终一致性**）
- 重复计算昂贵（**复杂查询、聚合统计**）

### ❌ 不适用场景

- 写多读少（缓存命中率低）
- 强一致性要求（**金融账户、库存**——需用分布式锁）
- 实时性要求极高（**毫秒级更新**）
- 数据频繁变动（**数据易过期，反而降低性能**）

---

## 七、最佳实践（速览）

1. **合理设置过期时间**：根据业务特点设置适当的缓存过期策略
2. **避免缓存过大对象**：大对象会消耗大量内存
3. **考虑缓存穿透**：对不存在的数据也进行适当缓存或使用布隆过滤器
4. **处理缓存雪崩**：使用随机过期时间或分级缓存策略
5. **监控缓存命中率**：通过监控了解缓存效果
6. **测试缓存行为**：编写单元测试验证缓存逻辑
7. **考虑分布式锁**：在高并发更新场景下使用分布式锁

> 详细方案见 [缓存实现与最佳实践](implementations-and-best-practices.md#五7-大最佳实践)

---

## 🤔 思考

1. **Spring Cache vs Redis Template 怎么选？** 简单场景用 Spring Cache（注解驱动），复杂场景（分布式锁、复杂数据结构）用 RedisTemplate。
2. **缓存和数据库双写一致性问题？** 没有完美方案——Cache Aside 模式（先更新 DB，再失效缓存）最常用。
3. **多级缓存怎么设计？** L1（Caffeine 本地）+ L2（Redis 分布式），**读时 L1 → L2 → DB**，写时**先清 L1，再清 L2**。
4. **Spring Cache 的本质是什么？** AOP 切面 + CacheManager 抽象 + KeyGenerator。

---

## 相关章节

- ⬅️ [返回 03 数据层](../README.md)
- [缓存注解与使用](annotations-and-usage.md)
- [缓存实现与最佳实践](implementations-and-best-practices.md)
- [缓存 4 大模式](patterns.md)
- [多级缓存与防护](multi-level.md)
- [Redis 序列化](serialization.md)
- [07 可观测性/Micrometer](../../07-observability/micrometer.md) — 缓存命中率监控
- [08 注解/AOP 注解](../../08-annotations/aop.md) — 缓存本质是 AOP
- [04 系统设计/缓存设计模式](../../../04.system-design/04-high-performance/cache-patterns/README.md) — 缓存架构与高可用场景见 04.sysdes，本节聚焦 Spring Cache 注解与 Redis/Caffeine 实现
