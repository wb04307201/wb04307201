<!--
module:
  parent: database
  slug: database/cache
  type: index
  category: 主模块子文章
  summary: 缓存通过减少数据库直接访问提升性能,核心问题是三大经典问题（穿透/击穿/雪崩）与缓存-数据库一致性,以及多级缓存与热点 Key 治理。
-->

# 缓存

> 缓存是将热点数据存储在高速存储介质(通常是内存)中的技术,通过减少对后端数据库的直接访问来提升系统性能;其核心问题是三大经典问题(穿透/击穿/雪崩)与缓存-数据库一致性。


---

## 📚 核心内容

| 主题 | 内容 | 关键点 |
|------|------|--------|
| 一、缓存分类 | 介质 / 部署 / 淘汰策略 | LRU / LFU / TTL / W-TinyLFU |
| 二、缓存三大经典问题 | 穿透 / 击穿 / 雪崩 | 布隆过滤器 + 互斥锁 + TTL 随机化 |
| 三、缓存与数据库一致性 | Cache Aside / Read-Write Through / Write Behind | 业界最常用 Cache Aside |
| 四、布隆过滤器深入 | 误判率公式 + Guava / Cuckoo / RedisBloom | Counting BF 支持删除 |
| 五、热点 Key 发现与处理 | redis-cli --hotkeys / 客户端统计 / JDHotkey | 本地缓存兜底 |
| 六、多级缓存架构(L1 + L2) | Caffeine + Redis | TTL 分层 + Pub/Sub 失效广播 |
| 七、本地缓存 3 个经典问题 | 内存上限 / 淘汰策略 / 进程间不一致 | W-TinyLFU + 短 TTL |
| 八、缓存预热方案 | 启动加载 / 灰度发布 / 定时刷新 / CDN | 让高峰时缓存已就绪 |

---

## 一、缓存分类

### 1. 按存储介质

| 类型 | 示例 | 特点 |
|------|------|------|
| **内存缓存** | Redis、Memcached、Caffeine | 速度快（纳秒~微秒），容量有限 |
| **磁盘缓存** | 本地文件缓存 | 速度慢，容量大 |

### 2. 按部署方式

| 类型 | 示例 | 特点 |
|------|------|------|
| **本地缓存** | Caffeine、Guava Cache、Ehcache | 无网络开销，最快，但无法跨进程共享 |
| **分布式缓存** | Redis Cluster、Memcached | 跨进程共享，有网络开销 |
| **多级缓存** | L1（本地）+ L2（分布式） | 兼顾速度和容量 |

### 3. 按淘汰策略

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **LRU** | Least Recently Used，淘汰最久未访问 | 通用场景 |
| **LFU** | Least Frequently Used，淘汰访问频率最低 | 热点数据稳定 |
| **FIFO** | First In First Out，先进先出 | 顺序访问 |
| **TTL** | 过期时间淘汰 | 有时效性的数据 |
| **W-TinyLFU** | Caffeine 使用，结合 LRU + LFU 优点 | 高命中率需求 |

---

## 二、缓存三大经典问题

### 1. 缓存穿透

**定义**：请求的数据在缓存和数据库中都不存在，每次请求都穿透到数据库。

**场景**：恶意攻击用不存在的 ID 大量请求。

| 解决方案 | 原理 | 优缺点 |
|---------|------|--------|
| **缓存空值** | 查询数据库为空时，缓存一个空值（TTL 较短） | ✅ 简单 ❌ 浪费内存，可能被大量不同 key 攻击 |
| **布隆过滤器** | 在缓存前置一层过滤器，快速判断 key 是否可能存在 | ✅ 内存小 ❌ 有误判率，不支持删除 |

```
请求 → 布隆过滤器 → 可能存在？ → 查缓存 → 未命中 → 查数据库
                   → 一定不存在 → 直接返回（不查库）
```

> **布隆过滤器**：用多个 Hash 函数将 key 映射到位数组。判断"不存在"是准确的，判断"存在"有误判率。

### 2. 缓存击穿

**定义**：某个**热点 key** 过期的瞬间，大量并发请求同时穿透到数据库。

| 解决方案 | 原理 | 优缺点 |
|---------|------|--------|
| **互斥锁** | 只允许一个线程查库并重建缓存，其他线程等待 | ✅ 强一致 ❌ 等待导致吞吐量下降 |
| **逻辑过期** | 不设物理 TTL，在 value 中存过期时间，过期后异步更新 | ✅ 高吞吐 ❌ 短期数据不一致，实现复杂 |

**互斥锁流程**：

```
请求 → 查缓存 → 未命中 → 获取锁？
                              ├── 成功 → 查数据库 → 写缓存 → 释放锁 → 返回
                              └── 失败 → 短暂休眠 → 重试查缓存
```

### 3. 缓存雪崩

**定义**：大量缓存 key 同时过期，或缓存服务宕机，导致请求全部打到数据库。

| 原因 | 解决方案 |
|------|---------|
| 大量 key 同时过期 | TTL 加随机值，打散过期时间 |
| 缓存服务宕机 | Redis 集群 + 熔断降级 |
| 新系统冷启动 | 缓存预热（提前加载热点数据） |
| 突发流量 | 多级缓存 + 限流 |

### 三大问题对比

| | 穿透 | 击穿 | 雪崩 |
|---|------|------|------|
| 数据是否存在 | 缓存和数据库都**不存在** | 缓存**过期**，数据库存在 | 缓存**大面积过期**或宕机 |
| 攻击特征 | 大量不存在的 key | 单个热点 key 过期 | 大量 key 同时过期 |
| 核心方案 | 布隆过滤器 + 缓存空值 | 互斥锁 + 逻辑过期 | TTL 随机化 + 集群 + 预热 |

---

## 三、缓存与数据库一致性

### 1. 读写策略

| 策略 | 读操作 | 写操作 | 一致性 |
|------|--------|--------|:------:|
| **Cache Aside**（旁路缓存） | 先读缓存，未命中读库并写缓存 | **先更新数据库，再删除缓存** | 最终一致 |
| **Read/Write Through** | 读缓存，未命中由缓存组件负责加载 | 写缓存，由缓存组件同步写库 | 强一致 |
| **Write Behind**（Write Back） | 读缓存 | 写缓存，异步批量写库 | 最终一致 |

> **业界最常用的是 Cache Aside 策略**：写操作先更新数据库，再删除缓存。

### 2. 为什么是"删除缓存"而不是"更新缓存"？

| 方案 | 问题 |
|------|------|
| 先更新数据库，再**更新**缓存 | 并发写时可能 A 先写库 B 后写库，但 B 先写缓存 A 后写缓存 → 不一致 |
| 先更新数据库，再**删除**缓存 | 删除失败才会不一致（概率低），且可通过重试补偿 |

### 3. "先删缓存再更新数据库"的问题

```
线程A：删除缓存 → （此时线程B读缓存未命中，从库读到旧值并写入缓存）→ 更新数据库
结果：缓存中是旧值，数据库是新值 → 不一致
```

### 4. 保证一致性的策略

#### 延时双删

```
删除缓存 → 更新数据库 → sleep(N ms) → 再次删除缓存
```

第二次删除可以清除在"删缓存"和"更新数据库"之间被其他线程加载的旧缓存。

**缺点**：N 的取值难以确定，sleep 阻塞线程。

#### 基于消息队列的重试补偿

```
更新数据库 → 删除缓存 → 删除失败？→ 发送消息到 MQ → 消费者重试删除
```

利用 MQ 的可靠性保证最终一致性。

#### 基于 Binlog 的异步同步

```
更新数据库 → binlog 产生 → Canal 监听 binlog → 发送消息到 MQ → 消费者更新/删除缓存
```

**优点**：业务代码无侵入，利用数据库自身保证消息不丢失。
**工具**：Canal（阿里开源）+ MQ + 消费者。

### 5. 一致性方案对比

| 方案 | 一致性 | 复杂度 | 侵入性 | 适用场景 |
|------|--------|--------|--------|---------|
| 延时双删 | 最终一致 | 低 | 中 | 简单场景 |
| MQ 重试补偿 | 最终一致 | 中 | 中 | 允许引入 MQ |
| Binlog + Canal | 最终一致 | 高 | 低（无侵入） | 大规模、高可靠 |
| 强一致（分布式事务） | 强一致 | 很高 | 高 | 金融级场景 |

> 大多数业务系统只需要**最终一致性**,引入缓存的目的是提升读性能,不值得为强一致性牺牲性能。

---

## 四、布隆过滤器深入

### 1. 误判率公式

| 参数 | 含义 |
|------|------|
| `m` | 位数组大小 |
| `n` | 已加入元素数 |
| `k` | Hash 函数个数 |
| `p` | 误判率 |

最优公式:

```
m = -n * ln(p) / (ln(2))^2
k = (m/n) * ln(2)
```

### 2. Java 实战(Guava BloomFilter)

```java
import com.google.common.hash.BloomFilter;
import com.google.common.hash.Funnels;

BloomFilter<Long> filter = BloomFilter.create(
    Funnels.longFunnel(),
    1_000_000,    // 期望元素数 n
    0.001         // 误判率 0.1%
);

// 添加
filter.put(123L);

// 查询
if (filter.mightContain(456L)) {
    // 可能存在,查缓存或 DB
}
```

### 3. Counting Bloom Filter(支持删除)

普通 Bloom Filter **不支持删除**(位无法区分多个元素)。变种 **Counting Bloom Filter** 用计数器数组替代位数组,删除时计数器 -1,支持计数溢出管理。

### 4. Cuckoo Filter(进阶变种)

Cuckoo Filter 空间利用率更高(>95%),**支持删除**,误判率比 Bloom Filter 低。适合 4KB-1GB 元素的场景。

### 5. Redis 布隆过滤器(RedisBloom 模块)

```bash
# 加载模块
redis-server --loadmodule /path/to/redisbloom.so

# 使用
BF.ADD user_ids 1001
BF.EXISTS user_ids 1001
BF.MADD user_ids 1002 1003 1004
```

---

## 五、热点 Key 发现与处理

### 1. 热点 Key 的危害

- 单节点 QPS 过高,成为瓶颈
- 缓存击穿风险(过期瞬间)
- Redis Cluster 中某节点过载

### 2. 发现方案

| 方案 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **redis-cli --hotkeys** | UNLINK + DEBUG OBJECT 探测 | 简单 | 仅采样、不精准 |
| **monitor 命令** | 抓取所有命令统计 | 精准 | **生产慎用**,影响性能 |
| **客户端统计** | Jedis/Lettuce 拦截统计 | 实时精确 | 需修改业务代码 |
| **JDHotkey(京东)** | 客户端 + 服务端综合 | 开箱即用 | 引入依赖 |
| **CacheCloud(搜狐)** | 可视化监控平台 | 管理友好 | 部署复杂 |

### 3. 处理方案

| 方案 | 适用 |
|------|------|
| **本地缓存兜底**(Caffeine) | 热点 key 数量少、读取频繁 |
| **Key 拆分** `product:1001:1` `product:1001:2` | 单值过大场景 |
| **读写分离** 分散到多个 Slave | 读多写少 |
| **Key 预加载** 提前刷新 TTL | 可预知的热点(如秒杀) |

---

## 六、多级缓存架构(L1 + L2)

### 1. 经典架构

```
请求 → L1 本地缓存(Caffeine) → L2 分布式缓存(Redis) → DB
         ↑ 命中直接返回     ↑ 命中回填 L1
```

### 2. Spring Boot 整合 Caffeine + Redis

```java
@Configuration
public class CacheConfig {
    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager mgr = new CaffeineCacheManager();
        mgr.setCaffeine(Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterWrite(60, TimeUnit.SECONDS));
        return mgr;
    }
}
```

```java
@Cacheable(value = "users", key = "#id", cacheManager = "caffeineCacheManager")
public User getUser(Long id) {
    return userMapper.selectById(id);
}

@Cacheable(value = "users", key = "#id", cacheManager = "redisCacheManager")
public User getUserFromRedis(Long id) { ... }
```

### 3. 一致性保障

- L1 TTL < L2 TTL(如 L1 = 60s, L2 = 600s)
- L1 失效后查 L2,再回填 L1
- 写操作:先更新 DB → 删除 L2 → **Pub/Sub 通知其他节点删除 L1**

---

## 七、本地缓存的 3 个经典问题

| 问题 | 表现 | 解决方案 |
|------|------|---------|
| **内存上限** | JVM 频繁 Full GC | Caffeine `maximumSize`/`maximumWeight` |
| **淘汰策略** | 误删热点数据 | 选 W-TinyLFU(Caffeine) |
| **进程间不一致** | 多节点缓存值不同 | 短 TTL + Pub/Sub 失效广播 |

---

## 八、缓存预热方案

| 场景 | 方案 |
|------|------|
| **系统启动** | 启动时 Job 加载热点数据到 Redis |
| **灰度发布** | 旧版本保留,新版本预热完成后切换流量 |
| **定时刷新** | `ScheduledTask` 周期性刷新(如配置数据) |
| **CDN 预热** | 主动调用 URL 触发 CDN 边缘节点缓存 |

> **核心原则**:**预热不是让缓存立即生效,而是让流量高峰时缓存已就绪**。

---

## 🔗 相关章节

- [数据库基础知识](../01-fundamentals/README.md) — 数据库基础
- [MySQL](../05-mysql/README.md) — MySQL 自带查询缓存(8.0 已移除)
- [Redis](../07-redis/README.md) — Redis 持久化、内存管理
- [系统设计 · 缓存设计模式](../../04.system-design/04-high-performance/cache-patterns/README.md) — 4 大缓存模式深入

---

## 📊 本节统计

- **leaf README 数**：1（本文即为分类 leaf，单 README 长文聚合 8 主题）
- **本节主题数**：8（缓存分类、3 大经典问题、一致性、布隆过滤器、热点 Key、多级缓存、本地缓存问题、预热方案）
- **frontmatter 状态**：✅ 已对齐 CONTRIBUTING §12 标准（summary ≤ 80 字 / type=index）
- **统计口径**：本目录无嵌套子目录，所有内容聚合在本 README

---

## 📖 参考资料

- [Redis Caching Strategies](https://redis.io/docs/manual/client-side-caching/)
- [Designing Data-Intensive Applications - Chapter 5](https://dataintensive.net/) — 数据系统经典
- [Caffeine - A high performance Java caching library](https://github.com/ben-manes/caffeine)
- [Bilibili - 缓存设计模式讲解](https://github.com/doocs/advanced-java) — 互联网工程师进阶知识库

---

## 🆕 深度扩展：Redis-DB 一致性（Java 后端视角）

完整的 4 策略 + 3 场景 + A/B/C 方案（延迟双删 / Binlog 监听）+ 30 秒话术面试题，已沉淀到：

- **面试题（通用策略）**：[13.split-hairs/04.system-design/high-performance/cache-consistency](../../13.split-hairs/04.system-design/cache-consistency/README.md) —— 244 行深度，Java 后端必问。
- **主模块深度（Java 后端视角）**：[04.system-design/04-high-performance/cache-patterns/#java 后端实战章节](../../04.system-design/04-high-performance/cache-patterns/README.md) —— 253 行，5 大 Spring 注解陷阱 + 多级缓存 + 反模式深度。

← [返回 03.database 主模块](../README.md)