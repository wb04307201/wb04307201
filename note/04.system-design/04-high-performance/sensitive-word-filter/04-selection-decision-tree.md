<!--
module:
  parent: system-design/sensitive-word-filter
  slug: system-design/04-high-performance/sensitive-word-filter/04-decision-tree
  type: topic
  category: 选型决策
  summary: 敏感词过滤选型决策树 + 5 维场景配置矩阵 + 实施 checklist
-->

# 敏感词过滤选型决策树 · 5 维场景配置矩阵

> **一句话**：选型核心公式 = **QPS + 词典大小 + 延迟要求 + 实时性 + 团队能力**——给一张「5 分钟决策树」+「场景配置矩阵」+「checklist」。

← [返回: sensitive-word-filter 总目录](../README.md)

---

## 1. 5 分钟决策树

```
Q1：业务 QPS 量级？
├─ < 1k → 单机 AC 自动机即可
├─ 1k-10k → 单机 AC + 本地缓存 + Bloom
├─ 10k-100k → 分布式集群 + 二级缓存
└─ > 100k → 多级架构（边缘 + 中心 + 异步二审）

Q2：词典大小？
├─ < 1000 词 → 朴素 HashMap Trie 足够
├─ 1000-10万 → 双数组 Trie（DAT）
├─ 10万-100万 → DAT + 词典分片
└─ > 100万 → DAT + 分类多词典 + AI 兜底

Q3：延迟要求？
├─ > 100ms（评论审核） → 同步即可
├─ 30-100ms（弹幕） → Bloom + Caffeine 预热
└─ < 30ms（电商详情） → 边缘节点 + 多级缓存

Q4：词典实时性（加新词能多快上线）？
├─ 分钟级 → 文件 + 定时 reload
├─ 30s → Redis Pub-Sub
├─ 秒级 → Nacos + Watch
└─ 即时 → 实时推送（少量）

Q5：业务类型？
├─ 评论 / 弹幕 → 100% 过滤（同步 + 拦截）
├─ 商品描述 → 同步过滤 + 异步二审（重词人工）
├─ 私信 → 异步过滤（不阻塞用户）
└─ 文档审核 → 异步二审（90% 通过 + 10% 人工）
```

---

## 2. 5 维场景配置矩阵

| 业务 | QPS | 词典 | 延迟 | 架构 | 替换策略 |
|------|-----|------|------|------|----------|
| **评论区** | 1k-10k | 1万 | < 50ms | 单机 AC + Caffeine | 同步拦截 |
| **直播弹幕** | 10万 | 1万 | < 30ms | 分布式 + Bloom | 异步二审 |
| **商品描述** | 100 | 100万 | < 200ms | 单机 + DAT | 同步 + AI 兜底 |
| **私信** | 5k | 5万 | < 100ms | 单机 + Caffeine | 异步过滤 |
| **电商搜索** | 100k | 10万 | < 10ms | 多级 + 边缘 | Bloom 预筛 |

---

## 3. 推荐配置（最优 80% 场景）

### 3.1 通用方案（评论 / 私信 / 中型应用）

```
- AC 自动机（DAT）：处理 1万-10万词
- Bloom Filter：预筛 95% 流量
- Caffeine：本地缓存 70% 重复文本
- 单实例：5k-10k QPS
```

### 3.2 大流量（直播 / 大厂）

```
- DAT + 分布式集群（5-50 实例）
- Redis 二级缓存
- 异步队列削峰 + 二审
- 边缘节点 + 中心层
```

### 3.3 重审核（金融 / 合规）

```
- 同步 AC + 异步 AI / 人工二审
- 词典 + AI 模型并行判定
- 审计日志全留存
```

---

## 4. 实施 Checklist

### 4.1 设计阶段

- [ ] 估算 QPS（用历史数据 / 同业类比）
- [ ] 估算词典大小（业务类型决定）
- [ ] 选型：AC / DAT / Bloom / Cache
- [ ] 决定架构：单机 / 分布式 / 多级

### 4.2 工程阶段

- [ ] 集成 HanLP 双数组 Trie
- [ ] Bloom Filter（Guava）
- [ ] Caffeine 本地缓存
- [ ] Spring Boot Filter / AOP 集成
- [ ] 词典动态加载（@Scheduled / Nacos watch）
- [ ] 替换策略可配置

### 4.3 运维阶段

- [ ] 监控埋点（延迟 / 命中率 / QPS）
- [ ] 告警阈值（延迟 P99 > 30ms / Bloom 命中率 < 90%）
- [ ] 灰度发布（双词典）
- [ ] 事故演练（词典加载失败 / 服务挂掉）

---

## 5. 反模式速查（5 大错）

| 反模式 | 场景 | 修复 |
|--------|------|------|
| 朴素 KMP 多次 | 词典 1万 + 1k QPS | 用 AC 自动机 |
| 每次请求构建 AC | 启动慢 100ms | @PostConstruct |
| 没 Bloom | 90% 流量走 AC | 加 Bloom |
| 同步阻塞 | 用户评论 5s 不响应 | 同步轻量词 + 异步二审 |
| 词典加载慢 | 启动 5 分钟 | 用 Nacos + 灰度加载 |

---

## 6. 一句话总结

> **选型公式：QPS × 词典大小 × 延迟要求 → 单机 / 分布式 / 多级。80% 场景：AC 自动机 + Bloom + Caffeine + Spring Boot Filter。100w QPS：加分布式 + 二级缓存 + 异步队列。**

---

← [返回: sensitive-word-filter 总目录](../README.md) · 上一章：[03-high-concurrency-optimization](03-high-concurrency-optimization.md) · 专题结束
