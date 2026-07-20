# 缓存实现与最佳实践

> ⬅️ [返回缓存总览](README.md) | [缓存注解与使用](cache-annotations-and-usage.md)

Spring Cache 提供**统一抽象层**——业务代码用同样的注解，**底层可自由切换** Caffeine / Redis / Ehcache 等多种实现。本文详解 3 种主流实现、4 大高级特性、优缺点对比和 7 条最佳实践。

---

## 🎯 一句话定位

**3 种主流缓存实现 = "单机 + 分布式 + 兼容老项目"**——Caffeine（**Spring Boot 默认**，内存级、高性能）适合单机；Redis 适合集群分布式；Ehcache 兼容老项目。**业务永远面向 Cache 抽象编程**，切换实现不改业务代码。

---

## 一、3 大主流缓存实现

### 1. Caffeine（**Spring Boot 默认**）

> **高性能的 Java 内存缓存**，被 Spring 5.x 选为默认实现。

| 维度 | 说明 |
|------|------|
| **类型** | 内存缓存（堆内） |
| **性能** | 极高（纳秒级） |
| **分布式** | ❌ 单机 |
| **持久化** | ❌ 不支持 |
| **适用场景** | **单机应用**、本地缓存、对性能要求极高 |

**Maven 依赖**：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
```

**配置示例**：

```properties
# application.properties
spring.cache.type=caffeine
spring.cache.caffeine.spec=maximumSize=1000,expireAfterWrite=10m
```

**常用 spec 参数**：

| 参数 | 说明 |
|------|------|
| `maximumSize=N` | 最大条目数（超过 LRU 淘汰） |
| `expireAfterWrite=10m` | 写入后 10 分钟过期 |
| `expireAfterAccess=5m` | 最后一次访问后 5 分钟过期 |
| `refreshAfterWrite=1m` | 写入后 1 分钟自动刷新 |

### 2. Redis（**分布式**）

> **分布式内存缓存**，支持集群、持久化、丰富的数据结构。

| 维度 | 说明 |
|------|------|
| **类型** | 内存缓存（可持久化） |
| **性能** | 高（毫秒级） |
| **分布式** | ✅ 原生支持 |
| **持久化** | ✅ 支持 RDB + AOF |
| **适用场景** | **集群环境**、分布式应用、数据共享 |

**Maven 依赖**：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
```

**配置示例**：

```properties
# application.properties
spring.cache.type=redis
spring.redis.host=localhost
spring.redis.port=6379
spring.redis.password=yourpassword
spring.redis.timeout=2000ms
```

**Redis vs Caffeine 选型**：

| 维度 | Caffeine | Redis |
|------|----------|-------|
| **单线程性能** | 极快（纳秒） | 较快（毫秒） |
| **跨进程共享** | ❌ | ✅ |
| **持久化** | ❌ | ✅ |
| **内存** | 堆内（受 JVM 限制） | 独立进程（无限制） |
| **适用** | 高频读、低一致性要求 | 集群共享、跨服务缓存 |

### 3. Ehcache（**老牌、成熟**）

> **成熟的 Java 缓存框架**，可与 Spring 深度集成，支持堆内/堆外/磁盘三级存储。

| 维度 | 说明 |
|------|------|
| **类型** | 内存 + 磁盘 |
| **性能** | 中 |
| **分布式** | 通过 Terracotta 集群 |
| **持久化** | ✅ 支持 |
| **适用场景** | **老项目**、需要持久化、与 Terracotta 集群 |

**Maven 依赖**：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
<dependency>
    <groupId>net.sf.ehcache</groupId>
    <artifactId>ehcache</artifactId>
</dependency>
```

**配置示例（ehcache.xml）**：

```xml
<cache name="users"
       maxEntriesLocalHeap="1000"
       timeToLiveSeconds="600"/>
```

```properties
spring.cache.type=ehcache
spring.cache.ehcache.config=classpath:ehcache.xml
```

---

## 二、3 大实现对比

| 特性 | Caffeine | Redis | Ehcache |
|------|:--------:|:-----:|:-------:|
| **类型** | 内存 | 内存 | 内存+磁盘 |
| **性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **分布式** | ❌ | ✅ | ✅ (Terracotta) |
| **持久化** | ❌ | ✅ | ✅ |
| **集群** | ❌ | ✅ | ✅ |
| **数据结构** | K-V | 丰富（String/Hash/List/Set/ZSet） | K-V |
| **运维成本** | 低 | 中（需独立部署） | 中 |
| **适用规模** | 单机 | 大型分布式 | 中型 |
| **推荐度（Spring Boot）** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

> 📌 **经验法则**：单机用 Caffeine，集群用 Redis，老项目用 Ehcache。

---

## 三、4 大高级配置

### 1. 条件缓存

```java
@Cacheable(value = "products", 
           condition = "#name.length() < 32",                  // 执行前判断
           unless = "#result == null || #result.price < 10")  // 执行后判断
public Product findProductByName(String name) {
    return productRepository.findByName(name);
}
```

### 2. 同步缓存（防击穿）

> 使用 `sync = true` 避免缓存击穿（**高并发下只有一个线程执行方法**）。

```java
@Cacheable(value = "hotProducts", key = "#category", sync = true)
public List<Product> getHotProducts(String category) {
    Thread.sleep(1000);  // 模拟耗时
    return productRepository.findHotByCategory(category);
}
```

### 3. 自定义 Key 生成器

> 实现 `KeyGenerator` 接口自定义 key 生成逻辑。

```java
@Configuration
public class CacheConfig {

    @Bean("customKeyGenerator")
    public KeyGenerator keyGenerator() {
        return (target, method, params) -> {
            StringBuilder sb = new StringBuilder();
            sb.append(target.getClass().getSimpleName());
            sb.append(".");
            sb.append(method.getName());
            for (Object param : params) {
                sb.append(".").append(param.toString());
            }
            return sb.toString();
        };
    }
}

// 使用
@Cacheable(value = "customCache", keyGenerator = "customKeyGenerator")
public Object customCacheMethod(String param1, Integer param2) {
    // ...
}
```

### 4. 自定义缓存管理器

> 实现 `CacheManager` 接口可集成其他缓存系统（如 Hazelcast、Memcached）。

```java
@Configuration
public class CustomCacheConfig {

    @Bean
    public CacheManager cacheManager() {
        // 自定义实现
        return new ConcurrentMapCacheManager("users", "orders", "products");
    }
}
```

---

## 四、优缺点分析

### 优点

- **简化开发**：通过注解即可实现缓存，减少样板代码
- **解耦**：业务代码与缓存实现**解耦**，便于切换缓存后端
- **声明式**：配置驱动，易于理解和维护
- **集成性好**：与 Spring 生态无缝集成
- **性能提升**：显著减少重复计算或数据库查询

### 缺点

- **调试困难**：缓存行为可能使调试变得复杂
- **一致性挑战**：在分布式环境中维护缓存一致性较难
- **内存消耗**：不当的缓存配置可能导致内存溢出
- **过期策略**：需要手动管理缓存过期，否则可能导致数据不一致
- **不适合所有场景**：对于频繁更新的数据，缓存可能适得其反

---

## 五、7 大最佳实践

### 1. 合理设置过期时间

```java
// 配合 application.yml
spring.cache.caffeine.spec=maximumSize=1000,expireAfterWrite=10m
```

业务原则：
- 变化频繁 → 短过期（1-5 分钟）
- 变化缓慢 → 长过期（30-60 分钟）
- 静态数据 → 永不过期

### 2. 避免缓存过大对象

- 单个缓存对象 **< 1MB**
- 避免缓存 List 超过 10000 条
- 考虑分页缓存（按 page 缓存）

### 3. 防止缓存穿透

> 缓存**不存在的数据**（如 id=-1 查不到）。

```java
@Cacheable(value = "users", key = "#id", unless = "#result == null")
public User findById(Long id) {
    return userRepository.findById(id).orElse(null);
}
```

进阶方案：布隆过滤器 + 空值缓存。

### 4. 防止缓存雪崩

> **大量缓存同时过期**导致请求全部打到数据库。

```java
// 方案 1：随机过期时间
spring.cache.caffeine.spec=maximumSize=1000,expireAfterWrite=10m
// 通过 Random TTL 工具类加 ±2min 随机

// 方案 2：分级缓存
@Cacheable(value = "L1_cache")  // 本地 Caffeine
public User findById(Long id) { ... }
```

### 5. 防止缓存击穿

> **热点 key 过期瞬间**，大量请求打到数据库。

```java
@Cacheable(value = "hotProducts", key = "#category", sync = true)
public List<Product> getHotProducts(String category) { ... }
```

或用分布式锁。

### 6. 监控缓存命中率

```java
@Bean
public CacheManager cacheManager() {
    CaffeineCacheManager manager = new CaffeineCacheManager();
    // 启用统计
    return manager;
}
```

通过 Micrometer 暴露 metrics，监控 `cache.gets{result="hit"}`。

### 7. 测试缓存行为

```java
@SpringBootTest
class UserServiceCacheTest {

    @Autowired
    private UserService userService;

    @MockBean
    private UserRepository userRepository;

    @Test
    void testCache() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(new User(1L, "Alice")));

        // 第一次：查 DB
        User u1 = userService.getById(1L);
        verify(userRepository, times(1)).findById(1L);

        // 第二次：查缓存
        User u2 = userService.getById(1L);
        verify(userRepository, times(1)).findById(1L);  // 仍是 1 次
    }
}
```

---

## 六、典型项目结构

```text
src/main/java/
├── com.example.demo
│   ├── config
│   │   └── CacheConfig.java  # 自定义缓存配置
│   ├── model
│   │   └── User.java         # 实体类
│   ├── repository
│   │   └── UserRepository.java # 数据访问层
│   └── service
│       └── UserService.java  # 业务逻辑层，使用缓存注解
```

---

## 七、常见问题解决

### Q1：缓存不生效？

**排查清单**：
```text
✅ 1. 检查是否添加了 @EnableCaching（Spring Boot 自动添加）
✅ 2. 确认方法被 Spring 管理（有 @Service 等注解）
✅ 3. 检查缓存名称（cacheNames）是否正确
✅ 4. 确认是 public 方法（否则 AOP 不拦截）
✅ 5. 确认从外部调用（自调用失效）
```

### Q2：序列化问题？

```properties
# 报错：SerializationException
# 原因：对象未实现 Serializable
# 解决 1：让对象实现 Serializable
# 解决 2：自定义序列化（如 JSON）
spring.cache.redis.serializer=org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer
```

### Q3：多参数 key 问题？

```java
// ❌ 默认用所有参数拼 key，可能不稳定
@Cacheable(value = "users")
public User find(String name, Integer age) { ... }

// ✅ 显式指定 key
@Cacheable(value = "users", key = "#name + '_' + #age")
public User find(String name, Integer age) { ... }

// ✅ 或自定义 KeyGenerator
@Cacheable(value = "users", keyGenerator = "customKeyGenerator")
public User find(String name, Integer age) { ... }
```

### Q4：缓存更新问题？

```java
// ❌ 错误：只更新 DB 不更新缓存，导致脏数据
public void update(User user) {
    userRepository.save(user);
}

// ✅ 方案 1：@CachePut 更新缓存
@CachePut(value = "users", key = "#user.id")
public User update(User user) {
    return userRepository.save(user);
}

// ✅ 方案 2：@CacheEvict 清缓存（让下次读时重建）
@CacheEvict(value = "users", key = "#user.id")
public void update(User user) {
    userRepository.save(user);
}
```

---

## 🤔 思考

1. **Caffeine 和 Redis 怎么选？** 单机高性能用 Caffeine；集群分布式用 Redis。也可以**两级缓存**（Caffeine L1 + Redis L2）。
2. **@Cacheable 能用在 private 方法上吗？** 不能，**自调用 + 非 public** 都会失效。
3. **Spring Cache 和 Spring Data Redis 什么关系？** Spring Cache 是抽象层，Spring Data Redis 是 Redis 实现之一。
4. **缓存和数据库双写一致性？** 没有银弹——常见方案有 Cache Aside（最常用）、Read/Write Through、Write Behind。

---

## 相关章节

- ⬅️ [返回缓存总览](README.md)
- [缓存注解与使用](cache-annotations-and-usage.md) — 5 大注解 + SpEL
- [07 可观测性/Micrometer](../../07-observability/micrometer.md) — 缓存命中率监控
- [08 注解/AOP 注解](../../08-annotations/aop.md) — 缓存本质是 AOP
