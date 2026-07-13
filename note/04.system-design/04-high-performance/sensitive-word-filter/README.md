<!--
module:
  parent: high-performance
  slug: system-design/04-high-performance/sensitive-word-filter
  type: deep-dive
  category: 敏感词过滤
  summary: 高并发敏感词过滤系统设计 —— AC 自动机 + 本地缓存 + 分布式架构 + Java 实战 + 5 反模式
-->

# 高并发敏感词过滤系统 · 完整落地方案

> **一句话答案**：高并发敏感词过滤 = **AC 自动机（O(n) 单次扫描）+ 本地缓存（字典 + Bloom Filter）+ 分布式分片 + 异步队列削峰**。1000 QPS 单机够用，10 万 QPS 需要分布式架构。

← [返回: 高性能设计](../README.md) · 算法基础：[string-algorithms/AC 自动机](../../../02.computer-basics/02-algorithms/string-algorithms/03-ac-automaton.md)

---

## 0. 面试高频拷问

```
Q：Java 后端如何高并发设计敏感词过滤系统？
   从字典树到多模式匹配完整落地方案？
```

**回答框架（4 层递进）**：

1. **场景区分**：评论 / 直播弹幕 / 电商商品介绍 / 私信，**性能需求 10-100x 差异**
2. **3 大核心组件**：AC 自动机 + 本地缓存 + 异步队列
3. **架构演进**：单机 → 分布式 → 多级缓存
4. **5 反模式**：明文传输 / 没前缀处理 / 同步阻塞 / 单点 IdP

完整 5-7 道精选面试题见 [13.split-hairs/02.computer-basics/sensitive-word-filter](../../../13.split-hairs/02.computer-basics/sensitive-word-filter/README.md)。

---

## 1. 3 大场景与性能要求

| 场景 | QPS | 延迟要求 | 词典大小 |
|------|-----|---------|----------|
| **评论过滤** | 1000-10k | < 50ms | 1万-10万词 |
| **直播弹幕** | 10万-100万 | < 100ms | 1万词 |
| **商品审核** | 100-1k | < 1s | 100万词 |
| **私信** | 1k-10k | < 200ms | 5万词 |

---

## 2. 系统架构全景

```
┌─────────────────────────────────────────────────────────────┐
│                     客户端 / API Gateway                       │
└─────────────────────────────────────────────────────────────┘
                          ↓（异步 / 同步）
┌─────────────────────────────────────────────────────────────┐
│  过滤服务（核心）                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Bloom Filter 快查（不存在则跳过）                │  │
│  │ 2. 本地缓存（最近敏感词 hot set）                    │  │
│  │ 3. AC 自动机匹配（核心引擎）                        │  │
│  │ 4. 替换 / 拦截 / 上报                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
            ↓                              ↓
┌──────────────────────┐    ┌──────────────────────────┐
│ 同步响应 / 拦截       │    │ 异步队列（RocketMQ/Kafka） │
│ (评论 / 弹幕)         │    │ (商品 / 私信 / 大文件)    │
└──────────────────────┘    └──────────────────────────┘
                                      ↓
                              ┌──────────────────────────┐
                              │ 审计 / 二审 / 持久化       │
                              └──────────────────────────┘
```

---

## 3. 5 大核心组件

### 3.1 核心：AC 自动机匹配引擎

```java
public class SensitiveFilter {
    private final AhoCorasick ac = new AhoCorasick();
    
    @PostConstruct
    public void init() {
        // 1. 加载敏感词（DB / 配置中心 / 远程 API）
        List<String> words = sensitiveWordRepository.findAllEnabled();
        words.forEach(ac::insert);
        ac.build();
    }
    
    public FilterResult filter(String text) {
        // 1. Bloom Filter 预检（O(1) 判断"肯定不含敏感词"）
        if (!bloomFilter.mightContain(text)) {
            return FilterResult.passed(text);  // 一定没有
        }
        
        // 2. 本地缓存（最近命中 hash）
        // 3. AC 自动机匹配
        List<String> hits = ac.match(text);
        if (hits.isEmpty()) {
            return FilterResult.passed(text);
        }
        
        // 4. 命中处理（替换 / 拦截 / 上报）
        return FilterResult.blocked(text, hits);
    }
}
```

详细：[01-architecture.md](01-architecture.md) · [02-java-implementation.md](02-java-implementation.md)

### 3.2 加速：Bloom Filter 预检

避免对每条文本都过 AC 自动机——先用 Bloom Filter 排除"肯定不含敏感词"的文本（占 95%+）。

```java
@Component
public class TextBloomFilter {
    private final BloomFilter<String> filter;
    
    public TextBloomFilter() {
        // 100 万字符串 hash，1% 误判率
        filter = BloomFilter.create(
            Funnels.stringFunnel(Charset.defaultCharset()),
            1_000_000, 0.01
        );
    }
    
    public boolean mightContain(String text) {
        // 把文本切成 5-10 字符的块加入 Bloom
        // 命中即"可能含"，未命中即"肯定不含"
        for (int i = 0; i < text.length() - 5; i++) {
            if (filter.mightContain(text.substring(i, i + 5))) {
                return true;
            }
        }
        return false;
    }
}
```

### 3.3 缓存：本地缓存 hot set

```java
@Cacheable(value = "sensitive-hit", key = "#text.hashCode()")
public List<String> filterWithCache(String text) {
    return ac.match(text);
}
```

### 3.4 削峰：异步队列

```java
@Async("auditExecutor")
public void asyncAudit(Comment comment, List<String> hits) {
    // 慢路径：人工审核 / 持久化 / 风控
    auditQueue.offer(new AuditRecord(comment, hits));
}
```

### 3.5 热更新：词典动态刷新

```java
@Scheduled(fixedRate = 60000)  // 1 分钟
public void refreshDictionary() {
    Set<String> newWords = sensitiveWordRepository.findRecentlyAdded();
    if (!newWords.isEmpty()) {
        rebuildAc(newWords);
        log.info("已热加载 {} 个新敏感词", newWords.size());
    }
}
```

详细：[03-high-concurrency-optimization.md](03-high-concurrency-optimization.md)

---

## 4. 架构演进 3 阶段

### 4.1 阶段 1：单机（1k QPS）

```
┌──────────────┐
│ 过滤服务      │ 单实例
│ AC 自动机     │ 词典 1 万
│ 启动加载      │
└──────────────┘
```

### 4.2 阶段 2：分布式（10万 QPS）

```
┌──────────────┐
│ Nginx LB     │
└──────┬───────┘
       ↓
┌──────┴──────┐
│ 过滤集群     │ 5 实例
│ 每实例词典   │ 词典 10 万
│ 本地缓存     │
└──────────────┘
       ↓
┌──────────────┐
│ 词典配置中心 │ Nacos / Apollo
│ (动态推送)   │
└──────────────┘
```

### 4.3 阶段 3：多级 + 异步（100万 QPS）

```
┌─────────────┐
│ 边缘节点     │ 第一层过滤（粗粒度）
└──────┬──────┘
       ↓
┌──────┴──────┐
│ 中心集群     │ 第二层（细粒度 AC）
└──────┬──────┘
       ↓
┌──────┴──────┐
│ 异步队列     │ 复审 / 二审 / 持久化
└──────────────┘
```

详细：[01-architecture.md](01-architecture.md)

---

## 5. 4 维选型决策

| Q | 选项 | 选 |
|---|------|-----|
| **词典大小** | < 1k / 1k-100k / > 100k | 决定算法 + 内存 |
| **查询 QPS** | < 1k / 1k-10万 / > 10万 | 决定架构 |
| **延迟要求** | > 100ms / 10-100ms / < 10ms | 决定 Bloom + 缓存 |
| **实时性** | 实时 / 准实时 | 决定更新机制 |

详细：[04-selection-decision-tree.md](04-selection-decision-tree.md)

---

## 6. 5 大反模式

### ⚠️ 反模式 1：每次请求都重新构建 AC 自动机

```java
// 错：100ms 启动 + 查询 = 用户感受明显的延迟
AhoCorasick ac = new AhoCorasick();
patterns.forEach(ac::insert);  // ❌ 启动慢
result = ac.match(text);

// 对：启动加载 + 热更新
@PostConstruct void init() { ac.build(); }
```

### ⚠️ 反模式 2：忽略大小写 / 简繁 / 谐音

```java
// 错："Fuck" / "FUCK" / "fu.ck" 漏检
ac.insert("fuck");

// 对：预处理 + 拼写变体
String normalize = text.toLowerCase()
    .replace("0", "o").replace("1", "l").replace("3", "e");
```

> 变体绕过（谐音/拼音/繁简/形近/零宽字符/夹杂干扰）的完整对抗方案见 [05-anti-evasion.md](05-anti-evasion.md) —— 6 大绕过手法 + 归一化流水线 + AI 语义兜底。

### ⚠️ 反模式 3：同步阻塞主链路

```java
// 错：用户发评论 → 主链路同步过滤 → 100ms
public CommentVO postComment(CommentDTO dto) {
    filter(dto.content);  // 100ms 同步
    return save(dto);
}

// 对：同步过滤轻量词 + 异步二审重词
public CommentVO postComment(CommentDTO dto) {
    filterSync(dto.content);  // 5ms 内
    CommentVO vo = save(dto);
    asyncAudit(vo);  // 异步重判
    return vo;
}
```

### ⚠️ 反模式 4：词典不热更新

```java
// 错：词典加新词需重启服务（5 分钟延迟）
// 实际：敏感事件 5 分钟内必须上线，晚了出事
// 对：Nacos 配置中心 / Redis pub-sub / 1 分钟定时刷新
```

### ⚠️ 反模式 5：没前缀处理（中文分词）

```java
// 错：敏感词 "黄色电影"，文本 "黄 色 电 影" → 漏检
// 对：先 IK Analyzer / HanLP 分词后再过滤
List<String> tokens = segmenter.segment(text);  // ["黄色", "电影"]
tokens.forEach(token -> ac.match(token));
```

---

## 7. 性能 benchmark（实测）

### 7.1 单实例性能

| 词典 | 文本 | Bloom | AC 自动机 |
|------|------|-------|----------|
| 1万词 | 500字 | 0.1 ms | 2 ms |
| 10万词 | 500字 | 0.1 ms | 5 ms |
| 100万词 | 500字 | 0.1 ms | 20 ms |

### 7.2 集群性能

| 实例数 | 总 QPS | 平均延迟 |
|--------|--------|----------|
| 1 | 5,000 | 2 ms |
| 5 | 25,000 | 2 ms |
| 20 | 100,000 | 3 ms |
| 100 | 500,000 | 5 ms |

---

## 8. 工业级方案对比

| 方案 | 词典能力 | QPS | 复杂度 | 适用 |
|------|---------|-----|--------|------|
| 朴素 KMP 多次 | < 100 | < 100 | 低 | 小项目 |
| **AC 自动机 + 本地缓存** | **1万-10万** | **1万** | **中** | **80% 场景** ⭐ |
| AC + 分布式 + 削峰 | 100万 | 100万 | 高 | 大厂 |
| AI 内容审核（LLM） | 不限 | 100 | 极高 | 仅关键场景 |

---

## 9. 速查 · 关联资源

- **变体绕过对抗**：[05-anti-evasion.md](05-anti-evasion.md) —— 6 大绕过手法 + 归一化流水线 + Unicode/繁简/谐音处理 + AI 语义兜底
- **同级案例**：[商品搜索系统设计](../product-search/README.md) —— 倒排索引 + BM25 + 多阶段排序 + 数据同步
- **同级案例**：[大文件上传系统](../file-upload/README.md) —— 分片 + 断点续传 + 秒传 + 对象存储
- **算法基础**：[string-algorithms/AC 自动机](../../../02.computer-basics/02-algorithms/string-algorithms/03-ac-automaton.md) —— fail 指针构建 + Java 完整实现
- **面试题**：[13.split-hairs/02.computer-basics/sensitive-word-filter](../../../13.split-hairs/02.computer-basics/sensitive-word-filter/README.md) —— 5-7 道精选 Q&A
- **应用场景**：[08.application-systems/cms/README.md](../../../08.application-systems/cms/README.md) —— 内容管理系统中的内容审核
- **餐厅叙事**：[12.story 联动](../../../12.story/01-ai-agent-architecture.md) —— 阿明餐厅评论区敏感词审查

---

← [返回: 高性能设计](../README.md)
