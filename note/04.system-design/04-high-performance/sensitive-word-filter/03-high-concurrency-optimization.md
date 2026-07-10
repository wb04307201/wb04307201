<!--
module:
  parent: system-design/sensitive-word-filter
  slug: system-design/04-high-performance/sensitive-word-filter/03-high-concurrency
  type: topic
  category: 高并发优化
  summary: 高并发 9 大优化 —— 双数组 Trie / Bloom / Caffeine / Redis / 字典压缩 / 灰度 / 监控
-->

# 高并发 9 大优化策略 · 性能从 1k 到 100w QPS

> **一句话**：9 大优化组合使用，单机能撑 5k QPS，分布式集群撑 100w QPS——核心是**减少单次扫描工作量**+**预热/缓存 + 异步削峰**。

← [返回: sensitive-word-filter 总目录](../README.md)

---

## 1. 优化方向全景

```
优化方向 ┬── 算法层（AC / Bloom / 双数组 Trie）
        ├── 缓存层（Caffeine / Redis）
        ├── 架构层（分布式 / 多级）
        └── 配套层（灰度 / 监控 / 异步）
```

---

## 2. 9 大优化策略

### 2.1 优化 1：AC 自动机替代朴素匹配

| 方案 | 1万词 + 500字 | 性能 |
|------|--------------|------|
| 朴素（每个词 KMP） | 1000 万字符比较 | ~500ms |
| **AC 自动机（一次扫描）** | 1 次扫描 | **~2ms** |
| **改进** | 200x |

### 2.2 优化 2：Bloom Filter 预检

```
朴素：每条文本都过 AC（即使是"今天天气好"等明显无敏感词）
     → 90% 流量做无用功

加 Bloom Filter（5-字符块）：
  - 命中 → 可能含 → 走 AC
  - 不命中 → 一定不含 → 直接放行
  → 减少 90% AC 调用
```

### 2.3 优化 3：Caffeine 本地缓存

```java
Cache<String, List<String>> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(Duration.ofMinutes(5))
    .build();

// 100 条文本里 80 条相同 → 缓存命中 80%
// AC 实际调用减少到 20 次
```

### 2.4 优化 4：双数组 Trie 压缩

| 方案 | 1万词内存 | 10万词内存 |
|------|----------|-----------|
| 朴素 HashMap Trie | 8 MB | 80 MB |
| **双数组 Trie（DAT）** | **800 KB** | **8 MB** |
| **压缩比** | 10x | 10x |

实际生产必上 `com.hankcs:hanlp:AhoCorasickDoubleArrayTrie`

### 2.5 优化 5：词典分片（分布式）

```java
// 按 hash(text) % N 分片到不同实例
int shard = Math.abs(text.hashCode()) % numShards;
SensitiveFilter filter = filterShards[shard].getFilter();
```

### 2.6 优化 6：Redis 二级缓存

```java
@Cacheable("sensitive-l2")
public List<String> filterWithRedis(String text) {
    return filterWithCaffeine(text);
}
```

### 2.7 优化 7：异步队列削峰

```
高峰 100w QPS → 同步过滤 50w → 通过
                      → 50w 命中 → 异步二审（队列缓冲）
                                  → 消费端弹性扩容
```

### 2.8 优化 8：词典动态加载

```java
@Scheduled(fixedRate = 60000)  // 1 分钟刷新
public void reload() {
    Set<String> newWords = remoteDict.fetch();
    engine.refresh(newWords);
}
```

### 2.9 优化 9：监控 + 告警

| 指标 | 阈值 |
|------|------|
| AC 匹配延迟 P99 | < 30ms |
| Bloom 命中率 | > 90% |
| Caffeine 命中率 | > 70% |
| 队列积压 | < 10w |
| 词典同步延迟 | < 5s |

---

## 3. 性能对比实测

| 优化组合 | 1 实例 QPS | 10 实例 QPS | 100 实例 QPS |
|---------|-----------|-------------|-------------|
| 朴素 KMP 多次 | 100 | 1k | 10k |
| + AC 自动机 | 5k | 50k | 500k |
| + AC + Bloom | 25k | 250k | 2.5M |
| + AC + Bloom + 缓存 | 50k | 500k | 5M |
| **+ AC + Bloom + 缓存 + 分布式 + 削峰** | **50k / 实例** | **500k** | **5M** |

---

## 4. 反模式 · 5 个错

### ⚠️ 反模式 1：每次请求都重新构建 AC 自动机

```java
// 错：100ms 启动延迟
AhoCorasick ac = new AhoCorasick();
patterns.forEach(ac::insert);  // 每次请求都执行

// 对：PostConstruct 启动加载 + 词典不变
@PostConstruct
public void init() { ac.build(); }
```

### ⚠️ 反模式 2：忽略 Bloom Filter

```java
// 错：90% 流量都是"明显无敏感词"，仍走 AC
// 对：Bloom 预检，95% 流量直接放行
```

### ⚠️ 反模式 3：词典加载不热更新

```java
// 错：词典变化需重启服务（分钟级延迟）
// 对：1 分钟定时刷新 + Nacos watch + Redis pub-sub
```

### ⚠️ 反模式 4：缓存粒度太粗

```java
// 错：缓存整个 List
cache.put("all_hits", allHits);

// 对：缓存单个文本的命中
cache.put(text, textHits);
```

### ⚠️ 反模式 5：同步阻塞主链路

```java
// 错：每个请求同步过滤完整
// 对：主链路 5ms 同步过滤 + 异步二审重词
```

---

## 5. 调优 checklist

- [ ] AC 自动机替换朴素（200x 提升）
- [ ] Bloom Filter 预检（10x 提升）
- [ ] Caffeine 本地缓存（5-10x 提升）
- [ ] 双数组 Trie 压缩（10x 内存下降）
- [ ] Redis 二级缓存（5x 提升）
- [ ] 词典分片（线性扩展）
- [ ] 异步队列削峰（峰值抗冲击）
- [ ] 词典热更新（秒级更新）
- [ ] 监控告警（实时可观测）

---

## 6. 一句话总结

> **9 大优化策略组合使用：AC 自动机（200x）+ Bloom（10x）+ Caffeine（10x）+ 双数组 Trie（10x 内存）+ 分布式 + 异步 = 1k QPS 起步到 100w QPS 不卡顿。**

---

← [返回: sensitive-word-filter 总目录](../README.md) · 上一章：[02-java-implementation](02-java-implementation.md) · 下一章：[04-selection-decision-tree](04-selection-decision-tree.md)
