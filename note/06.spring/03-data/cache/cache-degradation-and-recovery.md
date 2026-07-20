<!--
module:
  parent: spring
  slug: spring/cache/cache-degradation-and-recovery
  type: article
  category: 主模块子文章
  summary: @Cacheable + Redis 挂了怎么办？4 大降级方案 + Top 2 推荐 + 自动恢复机制 + 降级期数据一致性 + 实战模板。
-->

# @Cacheable + Redis 挂了怎么办？4 大降级方案 + 自动恢复实战

> 一句话定位：Spring Boot 缓存体系的**生产应急方案**。当 Redis 挂掉，**默认行为是抛异常 → 整个请求失败**，本文给出 **4 大降级方案**对比 + **Top 2 推荐实战代码** + **自动恢复机制** + **降级期数据一致性处理**。

> **同模块兄弟**：
> - [缓存注解与使用](cache-annotations-and-usage.md) — @Cacheable / @CachePut / @CacheEvict 用法
> - [缓存实现与最佳实践](implementations-and-best-practices.md) — Redis / Caffeine / Ehcache 对比
> - [多级缓存（multi-level）](multi-level.md) — 本地 + 分布式缓存架构（一笔带过降级，本文详讲）

---

## 一、问题边界（先看清默认行为）

很多人以为"Redis 挂了 @Cacheable 自动降级到 DB" —— **错**。**Spring Cache 默认行为是抛异常**。

### 默认行为（生产事故根源）

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

**反直觉点**：**Redis 是缓存，不是数据源**。Redis 挂了应该"降级到 DB"而不是"请求失败"。

### 真正的应急方案应该是

```text
Redis 挂了的预期行为：
1. @Cacheable 自动跳过 Redis 查询
2. 直接走 DB 查询
3. 返回结果给用户（牺牲性能保可用）
4. Redis 恢复后自动切回缓存
5. 整个过程对业务代码 0 侵入
```

---

## 二、4 大降级方案对比

### 方案 1：`@Cacheable` 异常处理（最简单但不够用）

**原理**：用 try-catch 包住调用方代码（**不是注解本身**）。

```java
public User getUserSafely(Long userId) {
    try {
        return userService.getUser(userId);  // @Cacheable 在这里
    } catch (Exception e) {
        // Redis 挂了 → 降级到 DB
        return userMapper.findById(userId);
    }
}
```

**缺点**：
- ❌ **每个调用都要写 try-catch**（重复代码）
- ❌ 业务代码和降级逻辑耦合
- ❌ Redis 异常和其他异常混在一起（无法区分）

**适用**：**只在 demo 或单个调用场景**用，**生产不推荐**。

---

### 方案 2：`CacheErrorHandler`（Spring 官方推荐 · Top 2）

**原理**：自定义 `CacheErrorHandler`，**统一处理所有缓存异常**。

```java
@Component
public class CustomCacheErrorHandler implements CacheErrorHandler {

    private static final Logger log = LoggerFactory.getLogger(CustomCacheErrorHandler.class);

    @Autowired
    private CircuitBreakerRegistry circuitBreakerRegistry;

    @Override
    public void handleCacheGetError(RuntimeException e, Cache cache, Object key) {
        // Redis 读失败 → 记录日志 + 触发熔断
        log.warn("Cache GET failed: cache={}, key={}", cache.getName(), key, e);
        // 业务方法继续执行（@Cacheable 会自动走 DB）
    }

    @Override
    public void handleCachePutError(RuntimeException e, Cache cache, Object key, Object value) {
        // Redis 写失败 → 记录日志（不影响业务返回）
        log.warn("Cache PUT failed: cache={}, key={}", cache.getName(), key, e);
    }

    @Override
    public void handleCacheEvictError(RuntimeException e, Cache cache, Object key) {
        // Redis 删除失败 → 记录日志（脏数据会在下次自然过期）
        log.warn("Cache EVICT failed: cache={}, key={}", cache.getName(), key, e);
    }

    @Override
    public void handleCacheClearError(RuntimeException e, Cache cache) {
        log.warn("Cache CLEAR failed: cache={}", cache.getName(), e);
    }
}
```

**注册到 CacheManager**：

```java
@Configuration
public class CacheConfig {

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheManager manager = RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(defaultConfig())
            .build();
        // 关键：注册自定义错误处理器
        manager.setCacheErrorHandler(new CustomCacheErrorHandler());
        return manager;
    }
}
```

**优点**：
- ✅ **统一处理所有缓存异常**（4 种回调）
- ✅ **业务代码 0 侵入**
- ✅ Spring 官方推荐

**缺点**：
- ❌ 单纯 log 没用，**需要配套熔断器**（避免持续打挂的 Redis）

---

### 方案 3：Resilience4j 熔断降级（Top 2 · 最灵活）

**原理**：用 Resilience4j 的 `CircuitBreaker` 包住缓存调用，**Redis 持续失败 → 熔断 → 直接走 DB**。

```java
@Component
public class ResilientCacheManager {

    private final CircuitBreaker circuitBreaker;

    public ResilientCacheManager() {
        this.circuitBreaker = CircuitBreaker.ofDefaults("redisCache",
            CircuitBreakerConfig.custom()
                .failureRateThreshold(50)         // 失败率 > 50% 触发熔断
                .waitDurationInOpenState(Duration.ofSeconds(30))  // 熔断 30 秒
                .slidingWindowSize(10)             // 10 次请求为滑动窗口
                .minimumNumberOfCalls(5)          // 至少 5 次调用才评估
                .build());
    }

    public <T> T executeWithFallback(Supplier<T> cacheCall, Supplier<T> dbFallback) {
        return circuitBreaker.executeSupplier(cacheCall, dbFallback);
        // Redis 正常 → 走 cacheCall
        // Redis 失败 → 自动 fallback 到 dbFallback（DB 查询）
    }
}
```

**业务代码**（包装 @Cacheable 调用）：

```java
@Service
public class UserService {

    @Autowired
    private ResilientCacheManager cacheManager;

    @Autowired
    private UserMapper userMapper;

    public User getUser(Long userId) {
        return cacheManager.executeWithFallback(
            () -> getUserFromCache(userId),     // 优先 Redis
            () -> userMapper.findById(userId)   // fallback DB
        );
    }
}
```

**关键能力：自动恢复**：

```text
Redis 状态变化：
├─ 正常 → 走 Redis
├─ 失败率 > 50% → 熔断（30 秒）
│   └─ 这 30 秒内所有请求直接走 DB（不尝试 Redis）
└─ 30 秒后 → Half-Open（半开状态）
    ├─ 试探 1 个请求 → 成功 → 关闭熔断，恢复 Redis
    └─ 试探失败 → 继续熔断 30 秒
```

**优点**：
- ✅ **自动恢复**（Half-Open 机制）
- ✅ **避免打挂刚恢复的 Redis**（熔断期不尝试）
- ✅ 业务代码简洁

**缺点**：
- ❌ 需要引入 Resilience4j 依赖
- ❌ 配置稍复杂

---

### 方案 4：Sentinel 降级规则（生产首选 · 阿里方案）

**原理**：用 Sentinel 的 `DegradeRule` 配置降级策略。

```java
@Component
public class SentinelCacheConfig {

    @PostConstruct
    public void initRules() {
        List<DegradeRule> rules = new ArrayList<>();
        rules.add(new DegradeRule("redisCache")
            .setGrade(RuleConstant.DEGRADE_GRADE_EXCEPTION_COUNT)  // 异常数降级
            .setCount(10)              // 10 个异常触发
            .setTimeWindow(30)          // 30 秒降级窗口
            .setMinRequestAmount(5));    // 至少 5 个请求
        DegradeRuleManager.loadRules(rules);
    }
}
```

**业务代码**：

```java
@Service
public class UserService {

    @SentinelResource(value = "redisCache", blockHandler = "dbFallback")
    public User getUser(Long userId) {
        return getUserFromCache(userId);  // Redis 调用
    }

    // fallback 方法：Redis 降级时走 DB
    public User dbFallback(Long userId, BlockException e) {
        log.warn("Redis degraded, fallback to DB", e);
        return userMapper.findById(userId);
    }
}
```

**优点**：
- ✅ Sentinel 是阿里生产级方案
- ✅ Dashboard 实时监控
- ✅ 多维度降级策略（异常数 / 异常率 / RT）

**缺点**：
- ❌ 引入 Sentinel 较重
- ❌ Dashboard 部署成本

---

## 三、4 方案对比表

| 方案 | 代码侵入性 | 自动恢复 | 复杂度 | 适用场景 | 推荐度 |
|------|---------|---------|------:|---------|------:|
| try-catch | ❌ 高（每个调用） | ❌ 无 | ⭐ | demo | ⭐ |
| **CacheErrorHandler** | ✅ 0 侵入 | ⚠️ 需配套熔断 | ⭐⭐ | **简单场景首选** | ⭐⭐⭐⭐ |
| **Resilience4j** | ✅ 低 | ✅ **自动恢复** | ⭐⭐⭐ | **生产环境首选** | ⭐⭐⭐⭐⭐ |
| Sentinel | ✅ 低 | ✅ 自动恢复 | ⭐⭐⭐⭐ | 阿里生态 | ⭐⭐⭐⭐ |

**选型决策树**：

```text
你的项目情况？
├─ 简单 Spring Boot / 不想引入额外依赖
│   └─ CacheErrorHandler + Resilience4j（轻量组合）
├─ 生产环境 / 追求自动恢复
│   └─ Resilience4j CircuitBreaker（推荐）
├─ 阿里生态 / 已有 Sentinel
│   └─ Sentinel DegradeRule
└─ 极简 demo
    └─ try-catch（不推荐生产）
```

---

## 四、Top 1 推荐方案：CacheErrorHandler + Resilience4j 组合

### 4.1 完整代码（生产级）

```java
// 1. 自定义 CacheErrorHandler（统一异常处理）
@Component
public class CustomCacheErrorHandler implements CacheErrorHandler {
    private static final Logger log = LoggerFactory.getLogger(CustomCacheErrorHandler.class);

    @Autowired
    private CacheMetricsCollector metricsCollector;

    @Override
    public void handleCacheGetError(RuntimeException e, Cache cache, Object key) {
        log.warn("[Cache GET] 失败: cache={}, key={}", cache.getName(), key, e);
        metricsCollector.recordCacheError(cache.getName(), "GET");
    }

    @Override
    public void handleCachePutError(RuntimeException e, Cache cache, Object key, Object value) {
        log.warn("[Cache PUT] 失败: cache={}, key={}", cache.getName(), key, e);
        metricsCollector.recordCacheError(cache.getName(), "PUT");
    }

    @Override
    public void handleCacheEvictError(RuntimeException e, Cache cache, Object key) {
        log.warn("[Cache EVICT] 失败: cache={}, key={}", cache.getName(), key, e);
        metricsCollector.recordCacheError(cache.getName(), "EVICT");
    }

    @Override
    public void handleCacheClearError(RuntimeException e, Cache cache) {
        log.warn("[Cache CLEAR] 失败: cache={}", cache.getName(), e);
    }
}

// 2. CacheManager 配置
@Configuration
public class CacheConfig {
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory connectionFactory,
                                      CustomCacheErrorHandler errorHandler) {
        RedisCacheManager manager = RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(defaultConfig())
            .build();
        manager.setCacheErrorHandler(errorHandler);
        return manager;
    }
}

// 3. Resilience4j 熔断（自动恢复核心）
@Configuration
public class ResilienceConfig {
    @Bean
    public CircuitBreaker redisCircuitBreaker() {
        return CircuitBreaker.of("redisCache",
            CircuitBreakerConfig.custom()
                .failureRateThreshold(50)
                .waitDurationInOpenState(Duration.ofSeconds(30))
                .slidingWindowSize(10)
                .minimumNumberOfCalls(5)
                .build());
    }
}

// 4. 业务封装（@Cacheable + 熔断 + DB fallback）
@Service
public class UserService {

    @Autowired
    private CircuitBreaker redisCircuitBreaker;

    @Autowired
    private UserMapper userMapper;

    @Cacheable(value = "user", key = "#userId")
    public User getUser(Long userId) {
        return redisCircuitBreaker.executeSupplier(
            () -> userMapper.findById(userId)  // 注：这里只是占位，实际查询放业务方法
        );
    }
}
```

---

## 五、自动恢复机制（3 种对比）

### 方案 A：Spring Boot Actuator Health Indicator（被动）

```java
@Component
public class RedisHealthIndicator implements HealthIndicator {
    @Autowired
    private RedisConnectionFactory factory;

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

**特点**：
- ✅ Spring Boot 内置
- ❌ **被动监控**（不自动切回缓存）

### 方案 B：Resilience4j Half-Open（推荐 · 主动）

```text
熔断状态机：
├─ CLOSED（关闭）→ 正常走 Redis
├─ OPEN（打开）→ 30 秒内直接走 DB
└─ HALF_OPEN（半开）→ 30 秒后试探 1 个请求
    ├─ 成功 → CLOSED（恢复 Redis）
    └─ 失败 → OPEN（继续熔断 30 秒）
```

**特点**：
- ✅ **主动恢复**（试探机制）
- ✅ **避免打挂刚恢复的 Redis**（熔断期不尝试）

### 方案 C：定时心跳检测（兜底）

```java
@Scheduled(fixedRate = 30000)  // 每 30 秒
public void checkRedis() {
    try {
        redisTemplate.opsForValue().set("health:probe", "1", 10, TimeUnit.SECONDS);
        if (circuitBreaker.getState() == CircuitBreaker.State.OPEN) {
            log.info("Redis 恢复，关闭熔断");
            circuitBreaker.reset();
        }
    } catch (Exception e) {
        log.warn("Redis 仍不可用，继续熔断");
    }
}
```

**特点**：
- ✅ 主动恢复
- ❌ 需要写定时任务

---

## 六、降级期数据一致性（最棘手的问题）

### 6.1 降级期的核心问题

```text
Redis 挂了，降级期所有读直接走 DB：
├─ 问题 1：写操作不更新缓存（Redis 挂时 @CachePut 失败）
├─ 问题 2：下次 Redis 恢复，缓存是旧的脏数据
└─ 问题 3：降级期数据不一致时间窗口不可控
```

### 6.2 解决方案：降级期主动失效

```java
@Service
public class UserService {

    @Autowired
    private RedisTemplate<String, User> redisTemplate;

    public User updateUser(Long userId, User newUser) {
        User updated = userMapper.update(userId, newUser);

        // 关键：无论 Redis 是否可用，都尝试清除缓存
        try {
            redisTemplate.delete("user::" + userId);
        } catch (Exception e) {
            // Redis 挂了 → 记录到"待清理队列"
            dirtyKeyQueue.add("user::" + userId);
            log.warn("Redis 不可用，缓存清理延迟执行", e);
        }

        return updated;
    }

    // 定时任务：Redis 恢复后清理脏数据
    @Scheduled(fixedRate = 60000)
    public void cleanupDirtyKeys() {
        if (circuitBreaker.getState() == CircuitBreaker.State.CLOSED) {
            while (!dirtyKeyQueue.isEmpty()) {
                String key = dirtyKeyQueue.poll();
                try {
                    redisTemplate.delete(key);
                    log.info("清理脏数据: {}", key);
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
- ✅ 写操作**不依赖 Redis**（DB 是真理）
- ✅ 降级期脏数据**异步清理**（Redis 恢复后批量删）
- ✅ **不阻塞业务**（降级期写操作正常返回）

---

## 七、监控 + 告警（生产必备）

### 7.1 关键指标

| 指标 | 阈值 | 告警级别 |
|------|------|---------|
| 缓存命中率 | < 50% | P2 |
| 缓存错误率 | > 10% | P1（Redis 故障） |
| 降级期时长 | > 5 分钟 | P1 |
| 熔断器状态 | OPEN | P1 |

### 7.2 监控代码

```java
@Component
public class CacheMetricsCollector {
    private final Counter cacheHits = Counter.build()
        .name("cache_hits_total").help("Cache hits").register();
    private final Counter cacheMisses = Counter.build()
        .name("cache_misses_total").help("Cache misses").register();
    private final Counter cacheErrors = Counter.build()
        .name("cache_errors_total").help("Cache errors").register();

    public void recordCacheHit() { cacheHits.inc(); }
    public void recordCacheMiss() { cacheMisses.inc(); }
    public void recordCacheError(String cache, String operation) { cacheErrors.inc(); }
}
```

### 7.3 Grafana 仪表盘关键面板

- 缓存命中率（按 cache 分组）
- 缓存错误率（按 operation 分组：GET/PUT/DELETE）
- 熔断器状态时间序列
- 降级期时长（自上次恢复以来）

---

## 八、反模式（不要做的事）

| 反模式 | 后果 |
|--------|------|
| ❌ 用 try-catch 包住 @Cacheable 调用 | 代码重复，无法统一处理 |
| ❌ 不用 CacheErrorHandler 直接用默认 | Redis 挂了直接 5xx |
| ❌ 降级期不监控 | 不知道 Redis 什么时候挂、什么时候恢复 |
| ❌ 降级期写操作还尝试更新 Redis | 持续抛异常拖慢响应 |
| ❌ Redis 恢复后不清理脏数据 | 用户看到旧数据 |
| ❌ 熔断器没有试探机制 | Redis 恢复后永远走 DB |

---

## 九、可复用 Checklist（Redis 降级方案自查）

- [ ] 实现 `CacheErrorHandler`（统一异常处理）
- [ ] 集成 Resilience4j / Sentinel 熔断（自动恢复）
- [ ] 业务代码封装降级逻辑（执行 + fallback）
- [ ] 降级期写操作不依赖 Redis
- [ ] 降级期脏数据异步清理队列
- [ ] Redis 恢复后批量回填缓存
- [ ] 监控：命中率 / 错误率 / 熔断器状态
- [ ] 告警：错误率 > 10% / 降级期 > 5 分钟
- [ ] 压测：模拟 Redis 挂掉，验证降级链路
- [ ] 演练：每季度演练一次 Redis 故障切换

---

## 十、相关章节

**同模块兄弟**：
- [缓存注解与使用](cache-annotations-and-usage.md) — @Cacheable / @CachePut / @CacheEvict 用法
- [缓存实现与最佳实践](implementations-and-best-practices.md) — Redis / Caffeine / Ehcache 对比
- [多级缓存（multi-level）](multi-level.md) — 本地 + 分布式缓存架构

**服务降级（04.system-design）**：
- [服务降级原理](../../../04.system-design/03-high-availability/service-degradation/README.md) — Sentinel / Resilience4j 通用降级
- [熔断原理](../../../04.system-design/03-high-availability/circuit-break/README.md) — 熔断器原理

**面试题**：
- [@Cacheable + Redis 挂了 5 题](../../../13.split-hairs/06.spring/cache-degradation/README.md) — 配套面试题

**缓存穿透/击穿/雪崩**：
- [缓存三连（穿透/击穿/雪崩）](../../../13.split-hairs/03.database/cache-penetration-breakdown-avalanche/README.md) — 互补场景

---

← [返回 Spring Cache 总览](README.md)