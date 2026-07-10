<!--
module:
  parent: system-design/sensitive-word-filter
  slug: system-design/04-high-performance/sensitive-word-filter/01-architecture
  type: topic
  category: 系统架构
  summary: 敏感词过滤 3 阶段架构演进（单机→分布式→多级异步）+ 5 大组件
-->

# 敏感词过滤系统架构 · 3 阶段演进

> **一句话**：敏感词过滤系统架构 = **核心匹配引擎 + 加速层 + 削峰层 + 词典层**，从单机的 1k QPS 到分布式的 100w QPS，需要逐级演进。

← [返回: sensitive-word-filter 总目录](../README.md)

---

## 1. 阶段 1：单机架构（1k-5k QPS）

```
┌─────────────────────────────────┐
│           Java 应用              │
│  ┌─────────────────────────┐  │
│  │ AC 自动机（启动加载）     │  │
│  │ 本地缓存                  │  │
│  │ 词典：MySQL/Redis         │  │
│  └─────────────────────────┘  │
│              ↓                  │
│         AC.match(text)          │
└─────────────────────────────────┘
```

**适用**：小项目 / 中小公司
**QPS**：1k-5k
**延迟**：< 10ms
**缺点**：单机挂掉全挂

---

## 2. 阶段 2：分布式集群（10w QPS）

```
┌─────────────────────────────────────────────────────────┐
│  Nginx / SLB 负载均衡                                     │
└──────┬─────────────────────────────────┬───────────────┘
       ↓                                 ↓
┌──────┴──────┐                  ┌──────┴──────┐
│ 过滤实例 1   │                  │ 过滤实例 2   │
│ AC 自动机     │                  │ AC 自动机     │
│ 本地缓存     │                  │ 本地缓存     │
└──────────────┘                  └──────────────┘
       ↓                                 ↓
┌───────────────────────────────────────────────┐
│           共享词典（Nacos / Apollo）                │
│  - 启动拉取                                    │
│  - 1 分钟 watch 推送                            │
└───────────────────────────────────────────────┘
```

**适用**：中大公司
**QPS**：10w
**延迟**：< 10ms
**新问题**：词典推送一致性 / 词典过大内存

### 2.1 关键决策

| Q | 选项 |
|---|------|
| **词典分发** | Nacos / Apollo / Redis Pub-Sub / 文件 + rsync |
| **内存优化** | 双数组 Trie（DAT）/ AhoCorasickDoubleArrayTrie |
| **缓存层** | Caffeine 本地 + Redis 二级 |
| **灰度** | 词典灰度（旧+新并存）|

---

## 3. 阶段 3：多级 + 异步（100w QPS）

```
┌────────────────────────────────────────────┐
│  边缘层（CDN / API GW）                       │
│  - 粗粒度：高频词 + Bloom Filter            │
│  - 命中即放行 / 不命中降级到中心              │
└────────────────┬───────────────────────────┘
                 ↓
┌────────────────┴───────────────────────────┐
│  中心过滤集群（10 实例）                    │
│  - AC 自动机（完整词典）                    │
│  - 本地缓存 + 分布式缓存                     │
└────────────────┬───────────────────────────┘
                 ↓
┌────────────────┴───────────────────────────┐
│  异步队列（RocketMQ / Kafka）               │
│  - 重判 / 二审 / 复审                        │
│  - 持久化 / 审计日志                        │
└────────────────────────────────────────────┘
```

**适用**：超大公司（字节 / 阿里 / 阿里云盾）
**QPS**：100w+
**延迟**：主链路 < 30ms / 重判异步

### 3.1 三层职责

| 层 | 职责 | 延迟要求 |
|----|------|----------|
| **边缘层** | 粗筛（高频词 + Bloom）| < 5ms |
| **中心层** | 细筛（AC 自动机完整）| < 30ms |
| **异步层** | 重判 / 二审 | 秒级 |

---

## 4. 5 大组件完整设计

### 4.1 匹配引擎：AC 自动机

```java
@Component
public class SensitiveMatchEngine {
    private final AhoCorasick ac = new AhoCorasick();
    
    public List<String> match(String text) {
        return ac.match(text);  // O(n) 单次扫描
    }
}
```

### 4.2 加速层：Bloom Filter + 本地缓存

```java
@Component
public class FilterPreCheck {
    private final BloomFilter<String> bloom;
    
    public boolean fastCheck(String text) {
        return bloom.mightContain(text);  // O(1)
    }
}

@Cacheable("sensitive-hit")
public List<String> filterCache(String text) {
    return engine.match(text);
}
```

### 4.3 词典管理层

```java
@Service
public class DictionaryService {
    @NacosValue("${sensitive.words.refresh-rate:60000}")
    private long refreshRate;
    
    @Scheduled(fixedRateString = "${sensitive.words.refresh-rate:60000}")
    public void refresh() {
        Set<String> words = remoteDictApi.fetchAll();
        engine.rebuild(words);  // 原子替换
    }
}
```

### 4.4 异步队列（削峰）

```java
@Async("auditExecutor")
public void asyncAudit(String text, List<String> hits) {
    AuditRecord record = new AuditRecord(text, hits);
    auditQueue.send(record);  // RocketMQ / Kafka
}

// 消费端
@RocketMQMessageListener(topic = "sensitive-audit")
public void processAudit(AuditRecord record) {
    manualReviewService.submit(record);  // 人工复审
}
```

### 4.5 监控层

| 指标 | 阈值 |
|------|------|
| AC 自动机匹配延迟 P99 | < 30ms |
| Bloom Filter 命中率 | > 90% |
| 本地缓存命中率 | > 70% |
| 命中词频次 Top 10 | 实时 |
| 词典同步延迟 | < 5s |

---

## 5. 关键决策对比

| 场景 | 单机 | 分布式 | 多级异步 |
|------|------|--------|----------|
| **QPS** | < 5k | 5k-50k | > 50k |
| **词典大小** | < 100k | 100k-1M | > 1M |
| **延迟要求** | > 100ms | 30-100ms | < 30ms |
| **实时性** | 分钟级 | 分钟级 | 秒级 |

---

## 6. 反模式 · 5 个常见错

### ⚠️ 反模式 1：单机架构想撑百万 QPS

```java
// 错：单机 AC 自动机 + MySQL 词典 → 100ms 延迟
// 对：100k QPS 必须分布式
```

### ⚠️ 反模式 2：词典不分片

```java
// 错：所有实例加载全量词典（100 MB / 实例 × 100 实例 = 10GB）
// 对：分片（按 hash(text) % N 路由到不同实例）
```

### ⚠️ 反模式 3：异步队列积压

```java
// 错：高峰期 QPS 10w 但只 1 个消费线程 → 积压到亿级
// 对：消费端弹性扩容（K8s HPA）+ 死信队列
```

### ⚠️ 反模式 4：没灰度新词典

```java
// 错：新词典直接全量替换 → 一旦有误判，影响全量
// 对：双词典（old + new）+ 按用户 id 灰度
```

### ⚠️ 反模式 5：没分词直接匹配中文

```java
// 错："黄 色 电 影" 漏检 "黄色电影"
// 对：先 IK Analyzer / HanLP 分词
```

---

## 7. 一句话总结

> **敏感词过滤系统架构 = 3 阶段（单机→分布式→多级异步）+ 5 大组件（AC 引擎 + Bloom 加速 + 本地缓存 + 异步队列 + 词典动态加载）。QPS 100w 级需要完整的多级架构 + 灰度发布 + 监控体系。**

---

← [返回: sensitive-word-filter 总目录](../README.md) · 下一章：[02-java-implementation](02-java-implementation.md)
