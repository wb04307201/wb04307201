<!--
question:
  id: cache-hot-key
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 生产Bug
  tags: [缓存, 热点Key, 本地缓存, 分布式锁]
-->

# 缓存热点 Key 问题深度剖析：单节点被打爆怎么办？

> 一句话定位：热点 Key 是缓存体系中最常见的"单点瓶颈" —— 一个 Key 的流量足以击穿整个 Redis 集群的某个分片。

> **系列定位**：经典系统设计面试题（缓存、高并发、大促场景高频）。考察的不是"什么是热点 Key"，而是 **热点发现能力** + **多级缓存架构** + **缓存击穿防护**。

---

## 引子：一场明星事件引发的生产事故

```text
🚨 凌晨 1:23 告警：Redis 节点 10.0.3.12 CPU 使用率 99.7%
🚨 凌晨 1:24 告警：该节点连接数突破 50000，开始拒绝新连接
🚨 凌晨 1:26 告警：下游服务超时率飙升至 42%
```

某电商平台，一位顶流明星突然官宣事件。瞬间数百万用户涌入搜索相关商品，而商品详情都依赖同一个缓存 Key `product:hot:celebrity_12345`。**所有请求都打到同一个 Redis 分片** —— 一致性哈希把这个 Key 固定映射到了 `10.0.3.12`。单节点 QPS 从 2 万瞬间飙到 50 万。

三个关键点：(1) 同一个 Key 永远落在同一个节点，加机器没用；(2) Redis 单节点能扛 10 万 QPS，50 万直接打爆；(3) 需要从"发现 → 分流 → 兜底"三层来解。

---

> 📚 **前置知识**：[Redis 集群](../../../03.database/07-redis/README.md) | [缓存穿透/击穿/雪崩](../../../03.database/06-cache/README.md)

## 一、核心原理

### 1.1 什么是热点 Key

热点 Key = **极短时间内被超高频访问的单个缓存 Key**。与普通高并发不同，它的流量无法通过扩容 Redis 节点来分散。典型场景：微博热搜、秒杀商品、顶流直播间。

### 1.2 热点 Key 的发现方式

| 方式 | 说明 | 时效 |
|------|------|------|
| **被动发现** | 节点 CPU 告警、单节点 QPS 异常 | 出事后才知道 |
| **Redis hotkeys** | `redis-cli --hotkeys`（需开启 LFU） | 秒级 |
| **业务层采样** | 滑动窗口计数，超阈值晋升为热点 | 秒级（推荐） |

```java
// 业务层热点检测：滑动窗口采样
public class HotKeyDetector {
    private final ConcurrentMap<String, LongAdder> counters = new ConcurrentHashMap<>();

    public void recordAccess(String key) {
        counters.computeIfAbsent(key, k -> new LongAdder()).increment();
    }

    public void startDetection(int threshold, Consumer<String> onHotKey) {
        Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate(() -> {
            counters.forEach((key, count) -> {
                if (count.sum() > threshold) onHotKey.accept(key);
            });
            counters.clear();
        }, 0, 5, TimeUnit.SECONDS);
    }
}
```

---

## 二、代码示例：Caffeine 本地缓存 + Redis 兜底

```java
@Service
public class ProductService {
    @Autowired private Cache<String, Object> localCache;       // L1: Caffeine
    @Autowired private StringRedisTemplate redisTemplate;       // L2: Redis

    public Product getProduct(String productId) {
        String key = "product:" + productId;
        // L1: 本地缓存（< 1ms）
        Product cached = (Product) localCache.getIfPresent(key);
        if (cached != null) return cached;
        // L2: Redis（< 10ms）
        String json = redisTemplate.opsForValue().get(key);
        if (json != null) {
            Product p = objectMapper.readValue(json, Product.class);
            localCache.put(key, p);  // 回填 L1
            return p;
        }
        // L3: 数据库（加分布式锁防击穿）
        return loadFromDB(key, productId);
    }

    private Product loadFromDB(String key, String productId) {
        String lockKey = "lock:" + key;
        boolean locked = Boolean.TRUE.equals(
            redisTemplate.opsForValue().setIfAbsent(lockKey, "1", 10, TimeUnit.SECONDS));
        if (!locked) { Thread.sleep(50); return getProduct(productId); }
        try {
            String json = redisTemplate.opsForValue().get(key);  // 双重检查
            if (json != null) return objectMapper.readValue(json, Product.class);
            Product product = productMapper.selectById(productId);
            if (product != null) {
                redisTemplate.opsForValue().set(key, objectMapper.writeValueAsString(product), 30, TimeUnit.MINUTES);
                localCache.put(key, product);
            }
            return product;
        } finally { redisTemplate.delete(lockKey); }
    }
}
```

**Key 拆分（分流热点）**：将 `key` 拆为 `key:0` ~ `key:9`，读时随机选子 Key 分散到不同节点，写时 Pipeline 批量写所有子 Key。

---

## 三、常见陷阱

### 陷阱 1：本地缓存数据不一致
- **真相**：Caffeine 是 JVM 内存，无法跨实例通知。需配合 Redis Pub/Sub 做失效通知，详见 [缓存一致性](../cache-consistency/README.md)。

### 陷阱 2：热点 Key 过期瞬间缓存击穿
- **真相**：热点 Key TTL 到期时数万并发同时 miss。必须用分布式锁（setnx）控制只有一个请求回源，否则数据库瞬间被打爆。

### 陷阱 3：Key 拆分后一致性
- **真相**：Key 拆分本质是数据冗余，写入时必须 Pipeline 保证所有子 Key 一致。部分写入会导致读到过期数据。

---

## 四、最佳实践

**多级缓存架构**：L1 Caffeine（仅存热点 Key，10-30s TTL） → L2 Redis Cluster → L3 MySQL。L1 只放检测到的热点 Key，避免内存浪费。

**热点 Key 自动晋升**：流量检测 → 超阈值 → 推送到各实例 L1；低于阈值 → 从 L1 移除。京东 HotKey 框架就是这个思路。

**大促预案**：提前 1 小时预热热点 Key 到 L1 + L2；进行中使用 L1 短 TTL + Pub/Sub 失效通知；兜底走分布式锁 + DB 限流。

---

## 五、面试话术（90 秒版本）

> "热点 Key 的本质是 **单 Key 流量超过单节点承载能力**，而 Redis Cluster 分片机制让同一 Key 只能落在一个节点，加机器没用。
>
> 解法分三层：**发现层** —— 用 `hotkeys` 命令或业务层滑动窗口采样，秒级发现热点；**分流层** —— 本地缓存（Caffeine）+ Redis 多级架构，热点 Key 自动晋升到各实例 L1，把 50 万 QPS 分散到 N 台应用服务器；还可以 Key 拆分，把 `key` 拆成 `key:0` ~ `key:9` 随机读取分散到不同节点；**兜底层** —— 热点 Key 过期瞬间用分布式锁防击穿，DB 层做限流。
>
> 关键取舍是本地缓存的 **一致性窗口**（通常 10-30 秒 TTL），大多数业务可接受。我经历的案例是明星事件导致单节点 QPS 飙到 50 万，加 Caffeine 后降到 5000，问题彻底解决。"

---

## 六、相关章节

- 同栏目：[`缓存一致性`](../cache-consistency/README.md) — 多级缓存一致性的详细方案
- 同栏目：[`分布式锁`](../distributed-lock/README.md) — 热点 Key 击穿时的分布式锁防护
- 主模块：[`缓存穿透/击穿/雪崩`](../../../03.database/06-cache/README.md) — 缓存三大问题与解决方案
- 主模块：[`Redis`](../../../03.database/07-redis/README.md) — Redis 集群与分片原理

← [返回系统设计咬文嚼字](../README.md)
