# 缓存设计模式

> 缓存是提升系统性能最有效的手段之一。不同的业务场景需要选择不同的缓存模式，本模块详解四种经典缓存模式及多级缓存架构。
>
> 最后更新: 2026-06-09

## 目录

- [1. 缓存模式概览](#1-缓存模式概览)
- [2. Cache-Aside 旁路缓存模式](#2-cache-aside-旁路缓存模式)
- [3. Read-Through 读穿透模式](#3-read-through-读穿透模式)
- [4. Write-Through 写穿透模式](#4-write-through-写穿透模式)
- [5. Write-Behind 写回模式](#5-write-behind-写回模式)
- [6. 多级缓存设计](#6-多级缓存设计)
- [7. 缓存预热策略](#7-缓存预热策略)
- [8. 缓存三大问题](#8-缓存三大问题)

---

## 1. 缓存模式概览

四种经典缓存模式的核心区别在于 **谁负责读写缓存** 以及 **写操作的同步/异步性**。

| 模式 | 读操作 | 写操作 | 缓存一致性 | 实现复杂度 | 典型场景 |
|------|--------|--------|-----------|-----------|---------|
| **Cache-Aside** | 应用层负责 | 应用层先写DB再删缓存 | 最终一致 | 低 | 通用场景，最常用 |
| **Read-Through** | 缓存层负责(含回源) | 应用层直接写缓存 | 最终一致 | 中 | 读多写少，如商品详情 |
| **Write-Through** | 缓存层负责 | 缓存层同步写DB+缓存 | 强一致 | 中 | 强一致要求场景 |
| **Write-Behind** | 缓存层负责 | 缓存层异步批量写DB | 弱一致 | 高 | 写多读少，容忍丢失 |

---

## 2. Cache-Aside 旁路缓存模式

Cache-Aside 是最常用的缓存模式，应用代码直接管理缓存和数据库。

### 2.1 原理

**读流程:**
```
1. 先查缓存
2. 缓存命中 → 直接返回
3. 缓存未命中 → 查数据库 → 写入缓存 → 返回结果
```

**写流程:**
```
1. 先更新数据库
2. 再删除缓存(不是更新缓存！)
```

### 2.2 为什么是"删缓存"而不是"更新缓存"

```
如果更新缓存:
  线程A: 更新DB (val=100)
  线程B: 更新DB (val=200)  ← 在线程A之前提交
  线程A: 更新缓存 (val=100) ← 覆盖了线程B的值！缓存脏数据

如果删除缓存:
  线程A: 更新DB (val=100) → 删缓存
  线程B: 更新DB (val=200) → 删缓存
  → 下次读时回源，获取最新值
```

### 2.3 时序图

```
Client          App           Cache           DB
  |              |              |              |
  |--读请求------>|              |              |
  |              |--GET(k)----->|              |
  |              |<--miss-------|              |
  |              |                           |--查询
  |              |<--result---------------------|
  |              |--SET(k,v)-->|              |
  |              |<--OK---------|              |
  |<--result------|              |              |
  |              |              |              |
  |--写请求------>|              |              |
  |              |--------------------------|--UPDATE
  |              |<--OK-----------------------|
  |              |--DEL(k)----->|              |
  |              |<--OK---------|              |
  |<--OK---------|              |              |
```

### 2.4 Java 代码示例

```java
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private StringRedisTemplate redisTemplate;

    private static final String USER_KEY_PREFIX = "user:";
    private static final Duration TTL = Duration.ofMinutes(30);

    /**
     * 读: Cache-Aside 模式
     */
    public User getUserById(Long id) {
        String key = USER_KEY_PREFIX + id;
        
        // 1. 先查缓存
        String json = redisTemplate.opsForValue().get(key);
        if (json != null) {
            return JSON.parseObject(json, User.class);
        }
        
        // 2. 缓存未命中,查数据库
        User user = userRepository.findById(id).orElse(null);
        if (user != null) {
            // 3. 写入缓存
            redisTemplate.opsForValue().set(key, JSON.toJSONString(user), TTL);
        }
        return user;
    }

    /**
     * 写: 先更新DB,再删除缓存
     */
    @Transactional
    public User updateUser(User user) {
        // 1. 先更新数据库
        User updated = userRepository.save(user);
        
        // 2. 再删除缓存
        String key = USER_KEY_PREFIX + user.getId();
        redisTemplate.delete(key);
        
        return updated;
    }
}
```

### 2.5 优缺点

| 优点 | 缺点 |
|------|------|
| 实现简单，代码直观 | 第一次读必然未命中 |
| 缓存只存热点数据，节省空间 | DB 更新和缓存删除之间有时间窗口 |
| 某个节点故障不影响整体 | 需要处理缓存穿透/击穿/雪崩问题 |

### 2.6 缓存删除失败怎么办

```
解决方案: 延迟双删 + 消息队列重试

1. 先删缓存(第一次)
2. 更新数据库
3. 休眠 N 毫秒(等待主从同步)
4. 再删缓存(第二次，延迟双删)
5. 若仍失败 → 发消息到 MQ → 消费者重试删除
```

---

## 3. Read-Through 读穿透模式

Read-Through 将"缓存未命中时回源查数据库"的逻辑封装到缓存层内部，对应用透明。

### 3.1 原理

```
应用只和缓存层交互，缓存层自己决定是否回源。
缓存组件内部有一个 Data Loader，负责从数据库加载数据。
```

### 3.2 时序图

```
Client          App           Cache(含Loader)    DB
  |              |              |                 |
  |--read(k)----->|              |                 |
  |              |--GET(k)----->|                 |
  |              |              |--miss,load------>|
  |              |              |<--data------------|
  |              |              |--SET(k,v,auto)-->|
  |              |<--data--------|                 |
  |<--data--------|              |                 |
```

### 3.3 Java 代码示例 (Spring Cache 模拟)

```java
@Service
public class ReadThroughService {

    // Spring @Cacheable 本质上就是 Read-Through 模式
    @Cacheable(value = "users", key = "#id", unless = "#result == null")
    public User getUserById(Long id) {
        // 这个方法只在缓存未命中时执行
        // 缓存层会自动调用这里加载数据
        return userRepository.findById(id).orElse(null);
    }
}
```

### 3.4 适用场景

- 读多写少的场景（商品详情、用户信息）
- 希望缓存逻辑与业务逻辑解耦
- 团队有统一的缓存基础设施

### 3.5 与 Cache-Aside 的区别

| Cache-Aside | Read-Through |
|-------------|-------------|
| 应用代码管理缓存回源 | 缓存组件内部管理回源 |
| 灵活性高，可定制逻辑 | 应用代码更简洁 |
| 缓存逻辑散布在业务代码中 | 缓存逻辑集中管理 |

---

## 4. Write-Through 写穿透模式

Write-Through 确保写操作同时更新缓存和数据库，由缓存层负责同步写入。

### 4.1 原理

```
应用写数据到缓存层 → 缓存层同步更新数据库 → 两个都成功后返回。
```

### 4.2 时序图

```
Client          App           Cache(含Writer)    DB
  |              |              |                 |
  |--write(k,v)--->|              |                 |
  |              |--PUT(k,v)-->|                 |
  |              |              |--同步写入------->|
  |              |              |<--OK-------------|
  |              |<--OK---------|                 |
  |<--OK----------|              |                 |
```

### 4.3 Java 代码示例

```java
@Component
public class WriteThroughCache<K, V> {

    private final Cache<K, V> cache;
    private final BiConsumer<K, V> dbWriter;

    public WriteThroughCache(Cache<K, V> cache, BiConsumer<K, V> dbWriter) {
        this.cache = cache;
        this.dbWriter = dbWriter;
    }

    public void put(K key, V value) {
        // 1. 先写缓存
        cache.put(key, value);
        // 2. 同步写数据库
        dbWriter.accept(key, value);
    }
}
```

### 4.4 适用场景

- 对数据一致性要求较高的场景
- 写操作频率不高，可以承受同步写入的开销
- 金融交易、订单状态等强一致性场景

### 4.5 优缺点

| 优点 | 缺点 |
|------|------|
| 缓存与数据库始终保持一致 | 写性能较差(需同步等待DB写入) |
| 不会出现缓存与DB不一致 | 数据库成为写入瓶颈 |
| 实现相对简单 | 数据库故障会导致写入失败 |

---

## 5. Write-Behind 写回模式

Write-Behind（也叫 Write-Back / 异步写）是 Write-Through 的异步版本。

### 5.1 原理

```
应用写数据到缓存 → 缓存立即返回成功 → 缓存层异步批量刷入数据库。
```

### 5.2 时序图

```
Client          App           Cache            DB
  |              |              |               |
  |--write(k,v)--->|              |               |
  |              |--PUT(k,v)-->|               |
  |              |<--OK(立即返回) |               |
  |<--OK----------|              |               |
  |              |              |  ... 异步 ...  |
  |              |              |--批量写入----->|
  |              |              |<--OK-----------|
```

### 5.3 Java 代码示例

```java
@Component
public class WriteBehindCache<K, V> {

    private final Map<K, V> buffer = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private final Consumer<Map<K, V>> batchWriter;

    public WriteBehindCache(Consumer<Map<K, V>> batchWriter) {
        this.batchWriter = batchWriter;
        // 每 5 秒批量刷入一次
        scheduler.scheduleAtFixedRate(this::flush, 0, 5, TimeUnit.SECONDS);
    }

    public void put(K key, V value) {
        // 立即写入缓冲区，快速返回
        buffer.put(key, value);
    }

    private synchronized void flush() {
        if (buffer.isEmpty()) return;
        Map<K, V> snapshot = new ConcurrentHashMap<>(buffer);
        try {
            batchWriter.accept(snapshot);
            snapshot.forEach(buffer::remove);
        } catch (Exception e) {
            // 写入失败，保留数据等待下次重试
            log.error("Write-Behind flush failed", e);
        }
    }
}
```

### 5.4 适用场景

- 写多读少，且写操作可以容忍短暂不一致
- 需要极高写入吞吐量的场景
- 日志收集、计数器、用户行为记录等
- 可以接受少量数据丢失（配合持久化缓冲）

### 5.5 风险

| 风险 | 说明 | 缓解措施 |
|------|------|---------|
| **数据丢失** | 缓存宕机时未刷入的数据会丢失 | 使用 AOF 持久化或 Write-Ahead Log |
| **数据不一致** | DB 中的数据滞后于缓存 | 适用于最终一致即可的场景 |
| **写入放大** | 同一 key 多次写入只保留最后值 | 合并写入，减少 DB 压力 |

---

## 6. 多级缓存设计

### 6.1 L1 + L2 架构

```
                   ┌─────────────┐
                   │   Client    │
                   └──────┬──────┘
                          │
                   ┌──────▼──────┐
                   │  L1 本地缓存 │  ← Caffeine (毫秒级)
                   │  (进程内)    │
                   └──────┬──────┘
                          │ miss
                   ┌──────▼──────┐
                   │  L2 分布式缓存│  ← Redis (毫秒~十毫秒级)
                   └──────┬──────┘
                          │ miss
                   ┌──────▼──────┐
                   │   数据库     │  ← MySQL (十毫秒~百毫秒级)
                   └─────────────┘
```

### 6.2 Java 代码示例

```java
@Service
public class MultiLevelCacheService {

    // L1: 本地缓存,容量1000,TTL 5分钟
    private final Cache<String, Object> localCache = Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(5, TimeUnit.MINUTES)
            .build();

    @Autowired
    private StringRedisTemplate redisTemplate;

    public Object getData(String key) {
        // 1. 查 L1 本地缓存
        Object value = localCache.getIfPresent(key);
        if (value != null) {
            return value;
        }

        // 2. 查 L2 Redis 缓存
        String json = redisTemplate.opsForValue().get(key);
        if (json != null) {
            Object obj = JSON.parseObject(json);
            localCache.put(key, obj);  // 回填 L1
            return obj;
        }

        // 3. 查数据库
        Object dbResult = loadFromDB(key);
        if (dbResult != null) {
            redisTemplate.opsForValue().set(key, JSON.toJSONString(dbResult), Duration.ofMinutes(30));
            localCache.put(key, dbResult);  // 回填 L1
        }
        return dbResult;
    }
}
```

### 6.3 多级缓存一致性问题

| 问题 | 解决方案 |
|------|---------|
| L1 和 L2 数据不一致 | L1 设置较短 TTL，L2 作为权威来源 |
| 多实例 L1 不一致 | Redis Pub/Sub 通知各实例失效本地缓存 |
| 缓存穿透 | 布隆过滤器 + 空值缓存 |
| 缓存雪崩 | 随机化过期时间 |

---

## 7. 缓存预热策略

缓存预热是在系统启动或流量高峰前，提前将热点数据加载到缓存中。

### 7.1 预热策略

| 策略 | 描述 | 适用场景 |
|------|------|---------|
| **全量预热** | 启动时加载所有数据到缓存 | 数据量不大(百万级以内) |
| **热点预热** | 只预热 Top-N 热点数据 | 数据量大，二八分布明显 |
| **定时预热** | 低峰期定时刷新缓存 | 数据更新不频繁 |
| **按需预热** | 用户访问前异步预热 | 可预测的用户行为 |

### 7.2 Java 代码示例: 应用启动预热

```java
@Component
public class CacheWarmUpRunner implements ApplicationRunner {

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private StringRedisTemplate redisTemplate;

    @Override
    public void run(ApplicationArguments args) {
        log.info("开始缓存预热...");

        // 预热热门商品 (最近7天销量Top 1000)
        List<Product> hotProducts = productRepository.findHotProducts(1000);
        
        hotProducts.forEach(product -> {
            String key = "product:" + product.getId();
            redisTemplate.opsForValue().set(key, JSON.toJSONString(product), Duration.ofHours(2));
        });
        
        log.info("缓存预热完成, 共预热 {} 条数据", hotProducts.size());
    }
}
```

### 7.3 预热注意事项

1. **预热时机**: 选择业务低峰期，避免与正常请求争抢资源
2. **预热范围**: 不要全量预热，根据访问统计选择热点数据
3. **预热速率**: 控制预热速率，避免对数据库造成冲击
4. **预热监控**: 记录预热耗时和数据量，持续优化预热策略

---

## 8. 缓存三大问题

使用缓存时最常遇到的三个经典问题：**缓存穿透**、**缓存击穿**、**缓存雪崩**。

### 8.1 缓存穿透 (Cache Penetration)

**场景**: 查询一个**数据库中根本不存在的数据**，缓存永远不命中，请求直接打到数据库。

**风险**: 恶意攻击者可以反复查询不存在的 key，把数据库打满。

**解决方案**:

```java
// 方案 1: 缓存空值 (适用于 key 有限且重复查询)
public User getUserById(Long id) {
    String key = "user:" + id;
    String cached = redisTemplate.opsForValue().get(key);
    if (cached != null) {
        if ("NULL".equals(cached)) return null;        // 空值标记
        return JSON.parseObject(cached, User.class);
    }
    User user = userRepository.findById(id).orElse(null);
    if (user == null) {
        redisTemplate.opsForValue().set(key, "NULL", Duration.ofMinutes(5));  // 缓存空值 5 分钟
        return null;
    }
    redisTemplate.opsForValue().set(key, JSON.toJSONString(user), Duration.ofMinutes(30));
    return user;
}

// 方案 2: 布隆过滤器 (适用于 key 海量, 误判率可控)
@Component
public class BloomFilterService {
    private final BloomFilter<Long> filter = BloomFilter.create(
        Funnels.longFunnel(), 10_000_000, 0.001);

    @PostConstruct
    public void init() {
        // 启动时将所有有效 user_id 加载到布隆过滤器
        userRepository.findAllIds().forEach(filter::put);
    }

    public boolean mightContain(Long userId) {
        return filter.mightContain(userId);
    }
}

public User getUserById(Long id) {
    if (!bloomFilterService.mightContain(id)) {
        return null;  // 一定不存在,直接返回
    }
    // 走正常查询流程 ...
}
```

### 8.2 缓存击穿 (Cache Breakdown)

**场景**: 某个**热点 key 突然过期**，此时大量并发请求同时打到数据库。

**解决方案**:

```java
// 方案 1: 分布式锁 (单线程回源)
public User getHotUser(Long id) {
    String key = "user:" + id;
    User user = (User) redisTemplate.opsForValue().get(key);
    if (user != null) return user;

    // 只让一个线程去查 DB, 其他线程等待
    String lockKey = "lock:user:" + id;
    boolean locked = redisTemplate.opsForValue().setIfAbsent(lockKey, "1", Duration.ofSeconds(3));
    if (locked) {
        try {
            user = userRepository.findById(id).orElse(null);
            redisTemplate.opsForValue().set(key, JSON.toJSONString(user), Duration.ofMinutes(30));
        } finally {
            redisTemplate.delete(lockKey);
        }
    } else {
        Thread.sleep(50);
        return getHotUser(id);  // 重试
    }
    return user;
}

// 方案 2: 逻辑过期 (后台异步刷新, 永不过期)
@Data
public class CacheItem<T> {
    private T data;
    private long expireAt;  // 逻辑过期时间
}

public User getHotUserV2(Long id) {
    String key = "user:" + id;
    CacheItem<User> item = (CacheItem<User>) redisTemplate.opsForValue().get(key);
    if (item == null) {
        // 缓存重建
        return rebuildCache(id);
    }
    if (item.getExpireAt() < System.currentTimeMillis()) {
        // 已过期, 异步刷新 (不阻塞当前请求)
        asyncRefreshExecutor.execute(() -> rebuildCache(id));
    }
    return item.getData();  // 始终返回旧数据
}
```

### 8.3 缓存雪崩 (Cache Avalanche)

**场景**: **大量 key 同时过期** 或 **缓存服务宕机**，导致所有请求直接打到数据库。

**解决方案**:

```yaml
# 方案 1: 过期时间随机化 (避免同时过期)
```

```java
// 给过期时间加一个随机抖动
int baseTtl = 30;  // 基础 30 分钟
int jitter = ThreadLocalRandom.current().nextInt(0, 10);  // 0~10 分钟随机
Duration ttl = Duration.ofMinutes(baseTtl + jitter);
redisTemplate.opsForValue().set(key, value, ttl);
```

```yaml
# 方案 2: 多级缓存 (L1 本地 + L2 分布式)
# 方案 3: 熔断降级 (Hystrix/Sentinel 限制直接访问 DB 的并发数)
# 方案 4: 缓存高可用 (Redis Cluster / Sentinel 防止缓存整体宕机)
```

### 8.4 三者对比

| 维度 | 缓存穿透 | 缓存击穿 | 缓存雪崩 |
|------|---------|---------|---------|
| **原因** | 查询不存在的数据 | 单个热点 key 过期 | 大量 key 同时过期/缓存宕机 |
| **危害** | 数据库承受恶意请求 | 单 key 突发打 DB | 整个系统雪崩 |
| **方案** | 布隆过滤器 / 空值缓存 | 分布式锁 / 逻辑过期 | 随机 TTL / 多级缓存 / 高可用 |
| **复杂度** | 中 | 中 | 高 |

---

## 相关章节

- [CDN 加速](../cdn/README.md) — 边缘缓存，与应用层缓存互补
- [负载均衡](../load-balance/README.md) — 缓存层的负载均衡
- [数据库分库分表](../database-optimization/db-sharding/README.md) — 缓存淘汰后由分库分表抗住流量
- [连接池优化](../connection-pool/README.md) — 缓存后端连接 (Redis Lettuce 池)
- [Java 性能优化](../java/README.md) — 本地缓存 (Caffeine) 的 JVM 调优
- [Spring Cache 注解与 Caffeine/Redis 集成示例](../../../06.spring/03-data/cache/README.md) — Spring Cache 抽象层与多种缓存实现的可插拔集成
