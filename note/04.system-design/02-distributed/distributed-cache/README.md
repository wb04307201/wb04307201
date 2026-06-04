# 分布式缓存

> 分布式缓存是提升系统读写性能、减轻数据库压力的关键组件。本文涵盖 Redis Cluster 架构、缓存三大经典问题（穿透/击穿/雪崩）及其解决方案、缓存一致性策略和淘汰策略。

## 为什么需要分布式缓存

在高并发场景下，直接访问数据库会导致：

- **响应慢**：磁盘 I/O 远高于内存 I/O（磁盘 ~0.1ms，内存 ~100ns，差 1000 倍）
- **数据库压力大**：热点数据反复查询，数据库连接池耗尽
- **系统可用性低**：数据库成为性能瓶颈，拖垮整个链路

```
请求量 QPS: 100,000
数据库能力:  5,000 QPS  ──>  缓存拦截 95%+ 请求 ──> 数据库仅处理 5%
```

分布式缓存的核心价值：

1. **加速读**：将热点数据缓存到内存，毫秒级响应
2. **减轻数据库压力**：缓存命中后不再查询数据库
3. **削峰填谷**：突发流量被缓存层吸收，保护后端
4. **会话共享**：集群环境下统一存储 Session

## Redis Cluster 架构

### 数据分片 (Hash Slot)

Redis Cluster 采用 **虚拟槽分区**，将 16384 个 hash slot 分布到多个节点：

```
┌──────────────────────────────────────────────────────────┐
│                    16384 个 Hash Slot                     │
├──────────────┬───────────────┬──────────────┬────────────┤
│  节点 A       │   节点 B       │   节点 C      │   节点 D    │
│ [0-4095]     │ [4096-8191]   │ [8192-12287]  │ [12288-16383]│
└──────────────┴───────────────┴──────────────┴────────────┘
      │               │               │               │
  Master A        Master B        Master C        Master D
      │               │               │               │
  Replica A       Replica B       Replica C       Replica D
```

- `key` 经过 CRC16 哈希后对 16384 取模，确定归属的 slot
- 每个 slot 有 1 个主节点和 1+ 个从节点
- 节点间通过 Gossip 协议通信，客户端直连目标节点

### 故障转移

当某个主节点宕机时，集群会自动进行故障转移：

1. 集群中超过半数节点标记该主节点为下线（PFAIL -> FAIL）
2. 该主节点的从节点开始选举新的主节点
3. 得票最多的从节点升级为主节点，接管原主节点的 slot

## 缓存三大经典问题

### 1. 缓存穿透

**问题**：查询一个**根本不存在的数据**，缓存和数据库都没有，每次请求都会打到数据库。

```
恶意请求 ──> 缓存(miss) ──> 数据库(无数据) ──> 返回空
   │                                              │
   └────────────── 持续请求 ──────────────────────┘
```

**解决方案**：

- **布隆过滤器**：请求到达缓存前，先通过布隆过滤器判断 key 是否存在。不存在则直接返回
- **缓存空值**：数据库查询为空时，也缓存一个短 TTL 的空值（如 `{"empty": true}`, TTL=60s）
- **接口层校验**：参数合法性校验，拦截非法请求

```java
// 方案1：缓存空值
public Object getData(String key) {
    Object value = cache.get(key);
    if (value != null) {
        // 空值标记
        if (value instanceof EmptyValue) {
            return null;
        }
        return value;
    }
    value = db.query(key);
    if (value == null) {
        // 缓存空值，短 TTL
        cache.set(key, new EmptyValue(), 60, TimeUnit.SECONDS);
        return null;
    }
    cache.set(key, value, 30, TimeUnit.MINUTES);
    return value;
}

// 方案2：布隆过滤器
BloomFilter<String> bloomFilter = BloomFilter.create(
    Funnels.stringFunnel(StandardCharsets.UTF_8),
    1000000,  // 预期元素数量
    0.01      // 误判率
);

// 数据写入时加入布隆过滤器
bloomFilter.put(key);

// 查询时先判断
if (!bloomFilter.mightContain(key)) {
    return null;  // 一定不存在，直接返回
}
```

### 2. 缓存击穿

**问题**：某个**热点 key 过期**的瞬间，大量并发请求同时到达，全部穿透到数据库。

```
时间线:
  T0: 热点 key 过期
  T1: 请求1 ──> 缓存 miss ──> 查 DB
  T1: 请求2 ──> 缓存 miss ──> 查 DB
  T1: 请求3 ──> 缓存 miss ──> 查 DB   ← 并发打穿
  ...
```

**解决方案**：

- **互斥锁**：只有一个线程去查数据库，其他线程等待或返回旧值
- **逻辑过期**：value 中记录过期时间，不依赖 Redis TTL，后台异步更新

```java
// 方案1：分布式互斥锁
public Object getDataWithLock(String key) {
    Object value = cache.get(key);
    if (value != null) {
        return value;
    }
    // 获取分布式锁
    boolean locked = redisLock.tryLock(key + ":lock", 10, TimeUnit.SECONDS);
    if (locked) {
        try {
            // 双重检查
            value = cache.get(key);
            if (value != null) return value;
            value = db.query(key);
            cache.set(key, value, 30, TimeUnit.MINUTES);
        } finally {
            redisLock.unlock(key + ":lock");
        }
    } else {
        // 未获取到锁，等待后重试
        Thread.sleep(50);
        return getDataWithLock(key);
    }
    return value;
}

// 方案2：逻辑过期 + 异步更新
public Object getDataWithLogicalExpire(String key) {
    CacheItem item = cache.get(key);
    if (item == null) {
        return buildAndCache(key);
    }
    if (item.isExpired()) {
        // 后台异步刷新，当前请求返回旧值
        CompletableFuture.runAsync(() -> buildAndCache(key));
    }
    return item.getValue();
}
```

### 3. 缓存雪崩

**问题**：**大量 key 同时过期**，或**缓存服务宕机**，导致请求全部打到数据库，可能压垮数据库。

```
        过期 key 数量
          │
     大量  │    ╱╲
          │   ╱  ╲    ← 大量 key 同时过期
          │  ╱    ╲
     少量 │ ╱      ╲
          │╱        ╲____
          └──────────────────> 时间
                ↑
            同时过期点
```

**解决方案**：

- **随机 TTL**：设置过期时间时加上随机偏移，避免集中过期
- **集群高可用**：Redis Sentinel / Redis Cluster，避免单点故障
- **限流降级**：数据库层面限流，缓存不可用时降级返回默认值
- **多级缓存**：本地缓存(Caffeine/Guava) + Redis 多级缓存

```java
// 方案1：随机 TTL
public void setCache(String key, Object value) {
    int baseTTL = 30 * 60;  // 基础 30 分钟
    int randomOffset = ThreadLocalRandom.current().nextInt(600); // 随机 0~10 分钟
    cache.set(key, value, baseTTL + randomOffset, TimeUnit.SECONDS);
}

// 方案2：多级缓存
public Object getDataMultiLevel(String key) {
    // 1. 本地缓存
    Object value = localCache.get(key);
    if (value != null) return value;

    // 2. Redis 缓存
    value = redisCache.get(key);
    if (value != null) {
        localCache.put(key, value, 5, TimeUnit.MINUTES);
        return value;
    }

    // 3. 数据库
    value = db.query(key);
    if (value != null) {
        redisCache.set(key, value, 30, TimeUnit.MINUTES);
        localCache.put(key, value, 5, TimeUnit.MINUTES);
    }
    return value;
}
```

### 三大问题速查对比

| 问题 | 触发原因 | 核心特征 | 主要解决方案 |
|------|---------|---------|-------------|
| **缓存穿透** | 查询不存在的数据 | 每次都打到 DB | 布隆过滤器、缓存空值 |
| **缓存击穿** | 热点 key 过期 | 并发打到 DB | 互斥锁、逻辑过期 |
| **缓存雪崩** | 大量 key 同时过期 | 流量洪峰打垮 DB | 随机 TTL、多级缓存、限流 |

## 缓存一致性策略

### Cache-Aside Pattern (缓存旁路)

**最常用的模式**：先更新数据库，再删除缓存。

```
更新流程:
  1. 更新数据库 ──> DB
  2. 删除缓存   ──> Redis (del key)

读取流程:
  1. 查缓存 ──> 命中则返回
  2. 未命中 ──> 查数据库 ──> 写入缓存 ──> 返回
```

```java
// Cache-Aside 写操作
public void updateUser(User user) {
    // 1. 先更新数据库
    userMapper.update(user);
    // 2. 再删除缓存（不是更新！）
    redisTemplate.delete("user:" + user.getId());
}

// Cache-Aside 读操作
public User getUser(Long id) {
    String key = "user:" + id;
    User user = (User) redisTemplate.opsForValue().get(key);
    if (user != null) {
        return user;
    }
    // 缓存未命中，查数据库
    user = userMapper.selectById(id);
    if (user != null) {
        redisTemplate.opsForValue().set(key, user, 30, TimeUnit.MINUTES);
    }
    return user;
}
```

**为什么是删除而不是更新缓存？**
- 写操作可能频繁但读操作不读取，更新缓存浪费性能
- 频繁写时可能导致缓存写并发冲突
- 懒加载思想：等真正读取时再加载

### Read-Through Pattern

缓存代理数据库的读取操作。应用只和缓存交互，缓存负责从数据库加载数据。

```
应用 ──> 缓存层 ──> 数据库
         (自动回源)
```

### Write-Through Pattern

写入时同时更新缓存和数据库，由缓存层保证一致性。

```
应用 ──> 缓存层 ──> 同时写入缓存和数据库
```

### 策略对比

| 策略 | 读流程 | 写流程 | 一致性 | 复杂度 | 适用场景 |
|------|--------|--------|--------|--------|---------|
| Cache-Aside | 查缓存 miss 则查 DB | 更新 DB + 删缓存 | 最终一致 | 低 | 通用场景 |
| Read-Through | 缓存自动回源 | - | 最终一致 | 中 | 读多写少 |
| Write-Through | 正常读 | 缓存+DB 同时写 | 强一致 | 高 | 写后需立即读 |

### 延迟双删（解决读写并发不一致）

```java
// 延迟双删：写操作先删一次缓存，更新 DB 后延迟再删一次
public void updateUserWithDoubleDelete(User user) {
    String key = "user:" + user.getId();
    // 1. 先删除缓存
    redisTemplate.delete(key);
    // 2. 更新数据库
    userMapper.update(user);
    // 3. 延迟删除（给读取操作留出加载缓存的时间）
    CompletableFuture.delayedExecutor(500, TimeUnit.MILLISECONDS)
        .execute(() -> redisTemplate.delete(key));
}
```

## 缓存淘汰策略

### Redis 内置淘汰策略

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **noeviction** | 不淘汰，写满报错 | 数据不能丢失的场景 |
| **allkeys-lru** | 所有 key 中淘汰最近最少使用的 | 通用缓存场景 |
| **allkeys-lfu** | 所有 key 中淘汰使用频率最低的 | 读热点稳定的场景 |
| **allkeys-random** | 随机淘汰 | 不关心命中率 |
| **volatile-lru** | 仅淘汰设置了 TTL 的 key | 部分数据需要持久 |
| **volatile-lfu** | 仅淘汰设置了 TTL 的 LFU key | 部分数据需要持久 |
| **volatile-ttl** | 淘汰 TTL 最短的 key | 优先清理即将过期的 |
| **volatile-random** | 仅淘汰设置了 TTL 的随机 key | - |

配置方式：
```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 常见算法实现

#### LRU (Least Recently Used)

淘汰最近最少使用的数据。

```java
// LinkedHashMap 实现 LRU
public class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    public LRUCache(int capacity) {
        // accessOrder=true 表示按访问顺序排序
        super(capacity, 0.75f, true);
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }
}
```

#### LFU (Least Frequently Used)

淘汰使用频率最低的数据。

```java
// 简易 LFU 实现
public class LFUCache<K, V> {
    private final int capacity;
    private final Map<K, V> data = new HashMap<>();
    private final Map<K, Integer> freq = new HashMap<>();

    public LFUCache(int capacity) {
        this.capacity = capacity;
    }

    public V get(K key) {
        if (!data.containsKey(key)) return null;
        freq.put(key, freq.get(key) + 1);
        return data.get(key);
    }

    public void put(K key, V value) {
        if (data.size() >= capacity && !data.containsKey(key)) {
            // 淘汰频率最低的
            K evictKey = freq.entrySet().stream()
                .min(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse(null);
            if (evictKey != null) {
                data.remove(evictKey);
                freq.remove(evictKey);
            }
        }
        data.put(key, value);
        freq.put(key, 1);
    }
}
```

### 淘汰策略选型建议

- **通用缓存**：`allkeys-lru`（兼顾命中率和实现简单）
- **读热点稳定**：`allkeys-lfu`（热点数据更稳定）
- **不能丢数据**：`noeviction` + 监控告警
- **本地缓存**：Caffeine（基于 W-TinyLFU，命中率更高）

```java
// Caffeine 本地缓存（推荐替代 Guava Cache）
Cache<String, User> cache = Caffeine.newBuilder()
    .maximumSize(10_000)              // 最大 10000 条
    .expireAfterWrite(10, TimeUnit.MINUTES)  // 写入后 10 分钟过期
    .recordStats()                    // 开启统计
    .build();

User user = cache.get("user:1", key -> {
    return userMapper.selectById(1);  // 缓存未命中时自动加载
});
```

## 参考链接

- [Redis 官方文档](https://redis.io/docs/)
- [Redis 设计与实现](http://redisbook.com/)
- [Caffeine Cache](https://github.com/ben-manes/caffeine)
