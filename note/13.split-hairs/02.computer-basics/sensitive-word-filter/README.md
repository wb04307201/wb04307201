<!--
question:
  id: 02.computer-basics-sensitive-word-filter
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计 + 算法
  tags: [02.computer-basics, AC 自动机, Trie, 字典树, KMP, 高并发, 敏感词]
-->

# 高并发敏感词过滤：字典树到多模式匹配深挖

> 一句话定位：敏感词过滤 = **AC 自动机（多模式匹配 O(n)）+ Bloom Filter + 本地缓存 + 分布式架构**——从 Trie 原理到 100w QPS 高并发完整落地。完整深度见 [主模块 sensitive-word-filter 专题](../../../04.system-design/04-high-performance/sensitive-word-filter/README.md) + [字符串算法专题 AC 自动机](../../../02.computer-basics/02-algorithms/string-algorithms/03-ac-automaton.md)。

> **系列定位**：经典 Java 后端高频题（字节 / 阿里 / 美团 / 拼多多 80%+ 出现率）。考察的不是"用什么算法"，而是 **3 大核心组件**（AC + Bloom + 缓存）+ **5 反模式** + **架构 3 阶段** + **Java 完整实战**。

---

## 引子：CTO 大会上"敏感词过滤"的 3 个崩溃现场

```text
场景：2024 Q3 某内容平台 CTO 阿明——
- 痛点 1：用户评论激增 10w QPS，但敏感词检测延迟从 5ms 飙到 800ms（CPU 跑满）
- 痛点 2：明明只有 1 万敏感词，朴素方案要跑 1 亿次字符串比对
- 痛点 3：上新敏感词需重启服务，错过了某次监管事件
```

**决策现场**：
1. **架构师候选人会问**：「从字典树到多模式匹配有什么完整落地方案？」
2. **资深候选人会问**：「AC 自动机的 fail 指针怎么建？性能如何？」
3. **CTO 候选人会问**：「高并发 100w QPS 怎么设计架构？词典怎么热更新？」

普通候选人会答"用正则"——踩中"**理由模糊、缺反模式、缺架构**" 3 大雷区。
高分候选人会答：**AC 自动机（O(n) 多模式匹配）+ Bloom Filter + Caffeine + 分布式 + 热更新**。

---

## 一、核心原理（必选）

### 1.1 朴素 vs AC 自动机性能对比

| 方案 | 1万词 + 1k QPS + 500字 | 延迟 |
|------|------------------------|------|
| 朴素 KMP × 1万 | 1000 万字符比较 | ~500ms |
| 正则 × 1万 | 同上 + 编译开销 | ~600ms |
| **AC 自动机（一次扫描）** | **1 次扫描** | **~2ms** |
| **改进** | **200-300x** | - |

### 1.2 AC 自动机 3 大核心组件

```
┌──────────────────────────────────────┐
│ 1. Trie（字典树）—— 存所有 patterns    │
│   "apple" / "app" / "apply" 共享 'app'  │
└──────────────────────────────────────┘
                ↓ BFS 构建
┌──────────────────────────────────────┐
│ 2. fail 指针（失配指针）—— 类似 KMP 的 next │
│   节点 A 的 fail → A 父节点 fail 链中       │
│   能匹配的最长后缀对应的 child             │
└──────────────────────────────────────┘
                ↓
┌──────────────────────────────────────┐
│ 3. output 链 —— 合并 fail 节点的命中     │
│   "he" 和 "she" 共用 "he"              │
└──────────────────────────────────────┘
```

### 1.3 AC 自动机匹配流程

```
扫描 "hello":
h → 命中 Trie 节点 h
e → 沿 fail 跳到 e（假设 e 是 fail 的 child）
l → 命中
l → 命中
o → 沿 fail 跳到 o（"she" 的 e 的 fail 是 o）
   检查 output：命中 "hello" 和 "she"

O(n) 单次扫描，找到所有匹配 patterns
```

### 1.4 生产环境核心公式

```
AC 自动机 + Bloom Filter + Caffeine + 分布式 + 异步队列
= 100w QPS 不卡顿

性能公式：
- 单实例 5k QPS（基础 AC + Bloom）
- 10 实例 50k QPS
- 100 实例 500k QPS（+ Redis 二级缓存）
- 1000 实例 5M QPS（+ 异步队列 + 边缘节点）
```

---

## 二、面试话术（90 秒版本 / 7 题）

> ⚠️ **模板不是背答案**——面试现场结合题目微调。

### 题目 A：Java 后端如何高并发设计敏感词过滤系统？

**高分答案**（4 层递进，60-90 秒）：

```
1. 场景区分（10 秒）：
   "敏感词过滤典型场景：评论 / 弹幕 / 商品 / 私信。
   QPS 跨度 1k-100w，词典 1万-100万。
   没有银弹，按场景选方案。"

2. 3 大核心组件（25 秒）：
   "核心 3 件套：
   - AC 自动机（O(n) 多模式匹配，200x 提升）
   - Bloom Filter（O(1) 预筛 95% 流量）
   - Caffeine 本地缓存（命中 70% 重复文本）"

3. 架构演进（20 秒）：
   "3 阶段：
   - 1k QPS：单机 AC 自动机
   - 10w QPS：分布式集群 + 二级缓存
   - 100w QPS：多级架构（边缘 + 中心 + 异步二审）"

4. Java 实战 + 反问（15 秒）：
   "Java 实战用 Spring Boot + HanLP 双数组 Trie + Bloom Filter。
   反问：贵司 QPS 量级？词典多大？延迟要求多少？"
```

### 题目 B：AC 自动机的 fail 指针是怎么构建的？

**高分答案**（50 秒）：

```
"fail 指针构建分 3 步：

1. 初始化：根节点的 fail = 根，第一层 child 的 fail = 根
2. BFS 构建其他节点：
   - 当前节点 = parent.children[c]
   - 当前节点的 fail = parent.fail 链中能匹配 c 的最近祖先
3. 合并 output：当前节点的 output = 当前节点 output + fail.output

关键：类似 KMP 的 next 数组，但用 BFS 而不是线性扫描。

匹配时：如果 char c 不在当前 child，沿 fail 跳，直到找到或回到根。

Java 实现见 HanLP AhoCorasickDoubleArrayTrie，< 100 行代码。"
```

### 题目 C：AC 自动机 vs KMP，区别和应用场景？

**高分答案**（45 秒）：

```
"AC 自动机 = Trie + fail 指针（类似 KMP 的 next）。
KMP 处理单 needle，AC 处理多 needle。

KMP：
- 1 个 needle（如 strstr）
- 时间 O(n + m)
- 内存 O(m)
- 应用：文本编辑器 Ctrl+F

AC 自动机：
- N 个 needle 同时匹配
- 时间 O(n + Σm + z)（z = 匹配数）
- 内存 O(Σm × 字符集大小）
- 应用：敏感词过滤 / 日志关键字告警 / DNA 序列匹配

敏感词过滤 = AC（99% 场景）
单 needle 搜索 = KMP（不需要 Trie）"
```

### 题目 D：Trie 树怎么实现？自动补全怎么用？

**高分答案**（50 秒）：

```
"Trie 节点 2 个关键字段：
- children（子节点字典 / 数组）
- isEnd（是否单词结尾）

Java 两种实现：
1. 数组版（紧凑，快）：children[26] for English
2. HashMap 版（灵活）：children = Map<char, Node>

关键 API：
- insert(word)：O(len(word))
- search(word)：O(len(word))
- startsWith(prefix)：O(len(prefix))
- getWordsWithPrefix(prefix)：DFS 收集所有匹配

应用：
- 自动补全（搜索框 'ap' → 'app'/'apple'/'apply'）
- 词频统计（insert 时累加 count）
- IP 路由最长前缀匹配
- AC 自动机前置（构建 Trie）"
```

### 题目 E：敏感词过滤的高并发架构怎么设计？

**高分答案**（60 秒）：

```
"3 阶段架构演进：

阶段 1（1k QPS）：单机
┌────────────────┐
│ Java 应用       │
│ AC + Caffeine  │
└────────────────┘

阶段 2（10w QPS）：分布式
┌─────────────────┐
│ Nginx + AC 集群  │ × 10
│ + Redis 缓存     │
└─────────────────┘

阶段 3（100w QPS）：多级
┌──────────────────────────┐
│ 边缘层（Bloom + 粗筛）│
│   ↓ 不命中               │
│ 中心层（DAT + 细筛）    │
│   ↓ 命中重词             │
│ 异步队列二审             │
└──────────────────────────┘

3 大辅助能力：
1. 词典热更新（1 分钟 reload / Nacos watch）
2. Bloom Filter 预筛（95% 流量不命中）
3. 灰度发布（双词典切换）

Java 实战：HanLP DAT + Guava Bloom + Caffeine 三件套。"
```

### 题目 F：Bloom Filter 在敏感词过滤中怎么用？

**高分答案**（40 秒）：

```
"Bloom Filter 用于'预筛不可能含敏感词的文本'。

原理：把文本切成 5-10 字符块加入 Bloom。
- 命中 → 可能含敏感词 → 走 AC
- 不命中 → 一定不含 → 直接放行

效果：95% 流量直接放行，AC 调用减少 10x。

反模式：把整个 text 加 Bloom（误判率高）
正解：切 5 字符块 → Bloom（误判率 1%）

Java 实现：com.google.guava BloomFilter。

性能：1 万次检查 < 1ms（O(1)）。"
```

### 题目 G：敏感词系统的 5 大反模式？

**高分答案**（50 秒）：

```
"5 大反模式（生产事故老坑）：

1. 每次请求构建 AC：
   - 错：100ms 启动延迟
   - 对：@PostConstruct 启动加载 + 词典不变

2. 没用 Bloom Filter：
   - 错：90% 流量（'今天天气好'）走 AC
   - 对：Bloom 预筛 95% 直接放行

3. 忽略中文分词：
   - 错：'黄色电影' → '黄 色 电 影' 漏检
   - 对：IK Analyzer / HanLP 先分词

4. 同步阻塞主链路：
   - 错：用户评论 5s 不响应
   - 对：同步轻量词 + 异步二审重词

5. 词典不热更新：
   - 错：词典变化需重启
   - 对：@Scheduled 1 分钟 reload + Nacos watch

5 反模式都是性能 + 实时性 + 准确性三大踩坑。"
```

---

## 三、常见陷阱（必选，5 个核心反模式）

### 陷阱 1：朴素 KMP 多次匹配

- **错误**：每个敏感词用 KMP 跑一次
- **真相**：1万词 + 500字 = 1000万字符比较 = 500ms
- **代价**：用户评论 30s 不响应

### 陷阱 2：每次请求构建 AC 自动机

- **错误**：在 filter 方法内 `ac = new AhoCorasick()`
- **真相**：AC 构建需 100ms-1s（看词典）
- **代价**：每个请求多 100ms 启动延迟

### 陷阱 3：忽略中文分词

- **错误**：直接匹配原文本
- **真相**：`"黄色电影"` 与 `"黄 色 电 影"` 不匹配
- **代价**：漏检 10-30% 命中

### 陷阱 4：同步阻塞主链路

- **错误**：所有请求同步过滤完整 → 100ms 延迟
- **真相**：用户感受卡顿
- **代价**：用户流失 10-30%

### 陷阱 5：词典不热更新

- **错误**：词典变化需重启
- **真相**：监管事件需分钟级上线
- **代价**：错过合规窗口

---

## 四、最佳实践（4 大工业方案）

### 方案 A：通用评论过滤（80% 场景）

```java
@Component
public class CommentFilter {
    private final AhoCorasickDoubleArrayTrie<String> ac;
    private final BloomFilter<String> bloom;
    private final Cache<String, List<String>> cache;
    
    public FilterResult filter(String text) {
        if (!mightContain(text)) return FilterResult.passed(text);
        List<String> hits = ac.parseText(text);
        return hits.isEmpty() ? FilterResult.passed(text) : FilterResult.blocked(text, hits);
    }
}
```

### 方案 B：直播弹幕（高 QPS）

```java
@Configuration
@EnableAsync
public class BulletFilterConfig {
    @Bean("filterExecutor")
    public Executor filterExecutor() {
        // 独立线程池，不阻塞主链路
        return Executors.newFixedThreadPool(20);
    }
}

@Async("filterExecutor")
public CompletableFuture<FilterResult> asyncFilter(String bullet) {
    return CompletableFuture.completedFuture(filter(bullet));
}
```

### 方案 C：商品审核（重审核）

```java
public FilterResult filter(String desc) {
    // 1. 同步 AC 过滤（5ms）
    FilterResult result = acFilter.filter(desc);
    
    // 2. 命中 → 异步 AI 兜底
    if (!result.isPassed()) {
        executor.submit(() -> aiFilter.audit(desc, result.getHits()));
    }
    return result;
}
```

### 方案 D：词典动态加载

```java
@Scheduled(fixedRate = 60000)
public void refreshDictionary() {
    Set<String> newWords = remoteDictApi.fetchAll();
    // 原子替换（双词典灰度）
    AhoCorasickDoubleArrayTrie<String> newAc = build(newWords);
    if (validate(newAc)) {
        this.engine = newAc;  // 原子替换
    }
}
```

---

## 五、相关章节（强制）

### 主模块深度专题

- [sensitive-word-filter 总目录](../../../04.system-design/04-high-performance/sensitive-word-filter/README.md)
- [01-architecture](../../../04.system-design/04-high-performance/sensitive-word-filter/01-architecture.md) —— 3 阶段架构演进
- [02-java-implementation](../../../04.system-design/04-high-performance/sensitive-word-filter/02-java-implementation.md) —— Spring Boot + HanLP 完整代码
- [03-high-concurrency-optimization](../../../04.system-design/04-high-performance/sensitive-word-filter/03-high-concurrency-optimization.md) —— 9 大优化策略
- [04-selection-decision-tree](../../../04.system-design/04-high-performance/sensitive-word-filter/04-selection-decision-tree.md) —— 5 维选型矩阵
- [05-anti-evasion](../../../04.system-design/04-high-performance/sensitive-word-filter/05-anti-evasion.md) —— 变体绕过对抗（谐音/拼音/繁简/形近/零宽字符/归一化流水线）

### 算法基础（02.computer-basics）

- [string-algorithms 总目录](../../../02.computer-basics/02-algorithms/string-algorithms/README.md) —— 3 大字符串算法综述
- [01-trie-data-structure](../../../02.computer-basics/02-algorithms/string-algorithms/01-trie-data-structure.md) —— Trie 字典树
- [02-kmp-algorithm](../../../02.computer-basics/02-algorithms/string-algorithms/02-kmp-algorithm.md) —— KMP 单模式匹配
- [03-ac-automaton](../../../02.computer-basics/02-algorithms/string-algorithms/03-ac-automaton.md) —— AC 自动机

### 主模块兄弟

- [04.system-design/04-high-performance/cache-patterns](../../../04.system-design/04-high-performance/cache-patterns/README.md) —— 缓存一致性
- [04.system-design/04-high-performance/README](../../../04.system-design/04-high-performance/README.md) —— 高性能模块
- [08.application-systems/cms/](../../../08.application-systems/cms/README.md) —— 内容审核系统

---

## 六、面试反问（让候选人反客为主）

```
Q1：贵司 QPS 量级？词典大小？
    → < 1k：单机；1k-10w：分布式；> 10w：多级
Q2：贵司延迟要求？
    → > 100ms：同步；< 30ms：Bloom + 多级
Q3：贵司词典更新频率？
    → 每日：定时 reload；实时：Nacos + 灰度
Q4：贵司是否需要 AI 兜底？
    → 是：同步 AC + 异步 AI 二审
    → 否：纯 AC 即可
Q5：贵司用 Java 还是其他语言？
    → Java：HanLP / Guava / Caffeine
    → Go：ahocorasick / bloom
    → Python：pyahocorasick
```

---

> 📅 2026-07-07 · 咬文嚼字 · 02.computer-basics · ⭐⭐⭐⭐⭐ · 7 道精选 Q&A · 含 90 秒话术模板 + 5 反模式 + 4 工业方案

← [返回: 咬文嚼字 · 02.computer-basics](../README.md)
