<!--
question:
  id: 06.spring-cache-degradation
  topic: 06.spring
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 生产应急 / 工程权衡
  tags: [06.spring, Cacheable, Redis降级, Resilience4j, CacheErrorHandler, 自动恢复]
-->

# @Cacheable + Redis 挂了怎么办？如何降级？如何恢复？

> 一句话定位：**Spring Boot 项目生产必问** —— 当 Redis 挂了，**默认行为是抛异常 → 整个请求失败**。考察的不是"会用 @Cacheable"，而是**应急降级 + 自动恢复**的工程能力。深度实战见 [主模块深度章节](../../../06.spring/03-data/cache/cache-degradation-and-recovery.md)。

> **系列定位**：高频生产应急题（社招 / 资深工程师必问）。考察"系统设计"能力 + 应急思维。配套兄弟题：[事务陷阱](../transactional-pitfalls/README.md) / [AOP 原理](../aop-principle/README.md)。

---

⭐⭐⭐⭐ 深度级别（高级架构师级）
📚 前置知识：@Cacheable / Redis / Resilience4j / 熔断器 / 缓存一致性基础

---

## 引子：面试官的"生产事故"陷阱

面试官："你们的 Spring Boot 项目用 @Cacheable 缓存，如果 Redis 挂了，会发生什么？"

阿明答："Redis 挂了？应该会自动降级到 DB 吧..."

面试官追问："**Spring Cache 默认行为是抛异常 → 整个请求 5xx**，业务代码完全没机会走到 DB。你设计的'自动降级'是怎么实现的？"

阿明答："……try-catch 包一下？"

面试官："**每个调用都写 try-catch？** Redis 恢复后怎么自动切回缓存？降级期数据一致性怎么处理？"

阿明愣住。

**这道题的陷阱**：考察的不是"Redis 怎么用"，而是**Redis 挂了整个系统的应急能力** —— 大部分候选人只懂注解不懂降级。

---

## Q1：@Cacheable 默认行为是什么？Redis 挂了会怎样？

**答**：**Spring Cache 默认行为是抛异常 → 请求 5xx**（生产事故根源）。

```java
@Cacheable(value = "user", key = "#userId")
public User getUser(Long userId) {
    return userMapper.findById(userId);
}

// Redis 挂了的实际行为：
// 1. RedisConnectionFailureException 抛出
// 2. 整个请求失败（5xx 给前端）
// 3. DB 完全没被查询（请求被异常中断）
// 4. 用户看到 500 错误
```

**反直觉点**：**很多人以为 Redis 挂了会自动降级 —— 错**。需要主动实现降级逻辑。

**真正的应急方案**：
1. @Cacheable 跳过 Redis 查询 → 直接走 DB
2. Redis 恢复后自动切回缓存
3. 业务代码 0 侵入
4. 整个过程对用户透明

---

## Q2：4 大降级方案的优劣对比？怎么选？

**答**：根据项目情况选：

| 方案 | 代码侵入性 | 自动恢复 | 复杂度 | 推荐度 |
|------|---------|---------|------:|------:|
| try-catch | ❌ 高 | ❌ 无 | ⭐ | ⭐ |
| **CacheErrorHandler** | ✅ 0 侵入 | ⚠️ 需配套熔断 | ⭐⭐ | ⭐⭐⭐⭐ |
| **Resilience4j 熔断** | ✅ 低 | ✅ **自动恢复** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Sentinel 降级 | ✅ 低 | ✅ 自动恢复 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Top 1 推荐组合**：**CacheErrorHandler + Resilience4j**（轻量 + 自动恢复）

```java
// 1. CacheErrorHandler（统一异常处理，0 侵入）
@Component
public class CustomCacheErrorHandler implements CacheErrorHandler {
    @Override
    public void handleCacheGetError(RuntimeException e, Cache cache, Object key) {
        log.warn("[Cache GET] 失败: cache={}, key={}", cache.getName(), key, e);
        // 不抛异常 → 业务方法继续走 DB
    }

    @Override
    public void handleCachePutError(RuntimeException e, Cache cache, Object key, Object value) {
        log.warn("[Cache PUT] 失败: cache={}, key={}", cache.getName(), key, e);
    }

    @Override
    public void handleCacheEvictError(RuntimeException e, Cache cache, Object key) {
        log.warn("[Cache EVICT] 失败: cache={}, key={}", cache.getName(), key, e);
    }

    @Override
    public void handleCacheClearError(RuntimeException e, Cache cache) {
        log.warn("[Cache CLEAR] 失败: cache={}", cache.getName(), e);
    }
}

// 2. Resilience4j 熔断（自动恢复核心）
CircuitBreaker circuitBreaker = CircuitBreaker.of("redisCache",
    CircuitBreakerConfig.custom()
        .failureRateThreshold(50)
        .waitDurationInOpenState(Duration.ofSeconds(30))
        .slidingWindowSize(10)
        .minimumNumberOfCalls(5)
        .build());

// 3. 业务封装
public User getUser(Long userId) {
    return circuitBreaker.executeSupplier(
        () -> getUserFromCache(userId),
        () -> userMapper.findById(userId)
    );
}
```

**选型决策树**：
- 简单 Spring Boot / 不想引入额外依赖 → CacheErrorHandler + Resilience4j（推荐）
- 生产环境 / 追求自动恢复 → Resilience4j CircuitBreaker
- 阿里生态 / 已有 Sentinel → Sentinel DegradeRule
- 极简 demo → try-catch（不推荐生产）

---

## Q3：如何实现自动恢复？3 种机制对比

**答**：3 种机制 —— **Resilience4j Half-Open 是首选**（主动恢复 + 避免打挂刚恢复的 Redis）。

### 机制 1：Spring Boot Actuator Health（被动）

```java
@Component
public class RedisHealthIndicator implements HealthIndicator {
    @Override
    public Health health() {
        try {
            factory.getConnection().ping();
            return Health.up().build();
        } catch (Exception e) {
            return Health.down().build();
        }
    }
}
```

**特点**：✅ 内置 | ❌ **被动监控**（不自动切回缓存）

### 机制 2：Resilience4j Half-Open（推荐 · 主动）

```
熔断状态机：
├─ CLOSED（关闭）→ 正常走 Redis
├─ OPEN（打开）→ 30 秒内直接走 DB
└─ HALF_OPEN（半开）→ 30 秒后试探 1 个请求
    ├─ 成功 → CLOSED（恢复 Redis）
    └─ 失败 → OPEN（继续熔断 30 秒）
```

**特点**：✅ **主动恢复** | ✅ **避免打挂刚恢复的 Redis**

### 机制 3：定时心跳检测（兜底）

```java
@Scheduled(fixedRate = 30000)
public void checkRedis() {
    try {
        redisTemplate.opsForValue().set("health:probe", "1");
        if (circuitBreaker.getState() == OPEN) {
            circuitBreaker.reset();  // 强制恢复
        }
    } catch (Exception e) {
        log.warn("Redis 仍不可用");
    }
}
```

**特点**：✅ 主动恢复 | ❌ 需要写定时任务

**核心洞察**：**Redis 恢复后不能"立即切回"** —— 可能 Redis 是"假恢复"（网络抖动瞬时可用），立即切回会把请求打过去再次挂。**必须试探机制（Half-Open）**。

---

## Q4：降级期数据一致性怎么处理？（最棘手的问题）

**答**：**降级期写不更新缓存 + Redis 恢复后异步清理脏数据**。

### 核心问题

```
Redis 挂了，降级期所有读直接走 DB：
├─ 问题 1：写操作不更新缓存（@CachePut 失败）
├─ 问题 2：下次 Redis 恢复，缓存是旧的脏数据
└─ 问题 3：降级期数据不一致时间窗口不可控
```

### 解决方案

```java
@Service
public class UserService {

    @Autowired
    private BlockingQueue<String> dirtyKeyQueue;

    public User updateUser(Long userId, User newUser) {
        User updated = userMapper.update(userId, newUser);

        // 关键：无论 Redis 是否可用，都尝试清除缓存
        try {
            redisTemplate.delete("user::" + userId);
        } catch (Exception e) {
            // Redis 挂了 → 记录到"待清理队列"
            dirtyKeyQueue.add("user::" + userId);
        }

        return updated;
    }

    // 定时任务：Redis 恢复后清理脏数据
    @Scheduled(fixedRate = 60000)
    public void cleanupDirtyKeys() {
        if (circuitBreaker.getState() == CLOSED) {
            while (!dirtyKeyQueue.isEmpty()) {
                String key = dirtyKeyQueue.poll();
                try {
                    redisTemplate.delete(key);
                } catch (Exception e) {
                    dirtyKeyQueue.add(key);  // 重新入队
                    break;
                }
            }
        }
    }
}
```

**核心原则**：
- ✅ **写操作不依赖 Redis**（DB 是真理）
- ✅ **降级期脏数据异步清理**（Redis 恢复后批量删）
- ✅ **不阻塞业务**（降级期写操作正常返回）

**反直觉点**：**很多人担心"Redis 挂了写不更新缓存会数据不一致"** —— 其实**降级期只能接受短暂不一致**，因为 Redis 已经挂了没别的选择。**关键是恢复后及时清理**。

---

## Q5：实战推荐方案是什么？完整代码 + 监控？

**答**：**CacheErrorHandler + Resilience4j + 监控 + 脏数据清理队列**。

### 完整方案清单

```
必备 4 件套：
├─ 1. CacheErrorHandler（统一异常处理）
├─ 2. Resilience4j 熔断器（自动恢复）
├─ 3. 脏数据清理队列（降级期写一致性）
└─ 4. Prometheus 监控（命中率 / 错误率 / 熔断器状态）
```

### 关键监控指标

| 指标 | 阈值 | 告警级别 |
|------|------|---------|
| 缓存命中率 | < 50% | P2 |
| 缓存错误率 | > 10% | **P1**（Redis 故障）|
| 降级期时长 | > 5 分钟 | **P1** |
| 熔断器状态 | OPEN | **P1** |

### 实战 Checklist

- [ ] 实现 `CacheErrorHandler`（统一异常处理）
- [ ] 集成 Resilience4j 熔断器（自动恢复）
- [ ] 降级期脏数据清理队列（LinkedBlockingQueue）
- [ ] Redis 恢复后批量回填（@Scheduled）
- [ ] 监控：命中率 / 错误率 / 熔断器状态
- [ ] 告警：错误率 > 10% / 降级期 > 5 分钟
- [ ] **压测**：模拟 Redis 挂掉，验证降级链路
- [ ] **演练**：每季度演练一次 Redis 故障切换

---

## 总结：面试答这题的 3 层结构

**30 秒简版**：
> "Spring Cache 默认行为是 Redis 挂了直接抛异常 → 5xx。**降级方案**是 `CacheErrorHandler`（统一异常处理）+ Resilience4j 熔断器（自动恢复）。**自动恢复**靠 Half-Open 状态机——熔断 30 秒后试探 1 个请求，成功就切回 Redis，失败继续熔断。**降级期数据一致性**靠脏数据清理队列——Redis 挂了写不更新缓存时入队，恢复后批量删。"

**60 秒扩展版**（面试官追问细节）：
> "具体来说，4 大降级方案：**try-catch**（每个调用都要写，不推荐）；**CacheErrorHandler**（Spring 官方，0 侵入）；**Resilience4j**（自动恢复核心，Half-Open 试探机制）；**Sentinel**（阿里生态）。
>
> **自动恢复的关键**：Redis 恢复后**不能立即切回**——可能 Redis 是假恢复（网络抖动），立即切回会把请求打过去再次挂。**Half-Open 试探机制**是关键：熔断 30 秒后试探 1 个请求，成功才切回，失败继续熔断。
>
> **降级期数据一致性**：Redis 挂了写操作不更新缓存时，**入脏数据队列**（LinkedBlockingQueue）。Redis 恢复后，**定时任务**批量清理脏 key。
>
> **核心原则**：**DB 是真理**，Redis 只是缓存。Redis 挂了**只能接受短暂不一致**，关键是恢复后及时清理。"

**踩分点提醒**：
- ✅ 提"默认抛异常 → 5xx" → 显式知道生产事故根源
- ✅ 提"CacheErrorHandler + Resilience4j" → 显式 Top 1 推荐方案
- ✅ 提"Half-Open 试探机制" → 显式自动恢复核心
- ✅ 提"脏数据清理队列" → 显式数据一致性
- ✅ 提"DB 是真理" → 显式核心原则

---

## 相关章节

**主模块**：
- [cache-degradation-and-recovery 深度章节](../../../06.spring/03-data/cache/cache-degradation-and-recovery.md) — 4 方案对比 + Top 1 推荐组合 + 自动恢复 3 机制 + 数据一致性 + 监控告警
- [@Cacheable 注解用法](../../../06.spring/03-data/cache/cache-annotations-and-usage.md) — 注解基础
- [缓存实现对比](../../../06.spring/03-data/cache/implementations-and-best-practices.md) — Redis / Caffeine / Ehcache
- [多级缓存架构](../../../06.spring/03-data/cache/multi-level.md) — 本地 + 分布式架构

**服务降级（04.system-design）**：
- [服务降级原理](../../../04.system-design/03-high-availability/service-degradation/README.md) — Sentinel / Resilience4j 通用降级
- [熔断原理](../../../04.system-design/03-high-availability/circuit-break/README.md) — 熔断器原理

**同栏目兄弟**：
- [事务陷阱](../transactional-pitfalls/README.md) — Spring 事务常见坑
- [AOP 原理](../aop-principle/README.md) — @Cacheable 底层实现
- [Spring Bean 生命周期](../bean-lifecycle/README.md) — CacheManager 初始化

**缓存三连**：
- [缓存穿透/击穿/雪崩](../../../13.split-hairs/03.database/cache-penetration-breakdown-avalanche/README.md) — 互补场景

---

> 📅 2026-07-06 · 咬文嚼字 · 06.spring · ⭐⭐⭐⭐

← [返回: 咬文嚼字 · cache-degradation](../README.md)
