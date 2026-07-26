<!--
question:
  id: 04.system-design-multi-field-ranking
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [04.system-design, 排名, 归一化, 加权, 系统设计]
-->

# 多字段动态排名该怎么设计？ —— 从归一化到动态权重的完整方案

> 一句话定位：**系统设计面试高频题**。考察的不是"ORDER BY 多个字段"，而是**归一化方法论** + **加权公式设计** + **动态权重策略** + **工程实现权衡**。深度实战见 [主模块深度章节](../../../04.system-design/04-high-performance/multi-field-ranking/README.md)。

> **系列定位**：高频系统设计题（社招必考）。配套兄弟题：[商品搜索系统设计](../product-search/README.md)、[缓存热点 Key](../cache-hot-key/README.md)、[限流算法](../rate-limiting/README.md)。

---

⭐⭐⭐⭐ 深度级别（高级工程师 / 架构师级）
📚 前置知识：Redis Sorted Set / 数据库索引 / 缓存设计 / 基本算法

---

## 引子：面试经典拷问

面试官："设计一个多字段动态排名系统，比如电商商品排序，要考虑销量、评分、价格、新鲜度等多个维度，怎么设计？"

大多数人答："ORDER BY sales DESC, rating DESC, price ASC。"

面试官追问：
1. "销量是万级，评分是 0-5，量纲不同怎么直接比较？"
2. "权重怎么动态调整？运营说要在大促期间提高销量权重。"
3. "100 万商品，每次请求都实时计算排名？"
4. "如果某个字段数据缺失怎么办？"

大多数人卡在追问上。**这道题考察的不是 SQL ORDER BY，而是归一化 + 加权 + 工程权衡。**

---

## 一、核心原理

### 1.1 为什么不能直接 ORDER BY 多字段？

| 问题 | 说明 | 示例 |
|------|------|------|
| **量纲不同** | 销量万级 vs 评分 0-5 | 销量完全主导排名 |
| **方向不同** | 销量↑好 vs 价格↓好 | 无法简单 SUM |
| **分布不同** | 销量幂律 vs 评分正态 | 同一归一化不适用 |
| **权重动态** | 不同场景权重不同 | 固定 ORDER BY 无法表达 |

### 1.2 正确思路：归一化 → 加权 → 排序

```text
原始字段（量纲不同）
    ↓ 归一化（统一量纲到 [0,1] 或 z-score）
标准分数（可比较）
    ↓ 加权（线性 / 乘法 / 分层）
综合分数
    ↓ 排序（Redis ZSet / DB ORDER BY / ES function_score）
最终排名
```

### 1.3 归一化方法选型（决策树）

```text
数据分布？
├─ 正态分布 → Z-Score: (x - μ) / σ
├─ 幂律分布（销量、点击数） → Log: log(1+x) / log(1+max)
├─ 值域已知有界（评分 0-5） → Min-Max: (x-min) / (max-min)
├─ 只关心相对位置 → 排名百分位: rank / total
└─ 业务需要离散等级 → 分段映射: 4.5-5.0 → 5分
```

### 1.4 加权公式选型

| 公式 | 适用场景 | 特点 |
|------|---------|------|
| **线性加权** score = Σ wi×fi | 电商排序、简历筛选 | 简单可控，运营可调 |
| **几何加权** score = Π fi^wi | 质量门槛场景 | 一票否决效应 |
| **分层排序** ORDER BY f1, f2, f3 | 简单场景 | 主字段优先 |
| **ML 模型** | 内容 Feed、推荐 | 自动学习特征交互 |

---

## 二、工程实现方案对比

### 2.1 方案选型决策树

```text
数据规模 + 实时性要求？
├─ < 1 万条 + 实时 → DB ORDER BY + 复合索引
├─ 1 万~100 万 + 秒级 → Redis ZSet + 定时预计算
├─ 100 万+ + 分钟级 → 预计算表 + 缓存
└─ 需要搜索 + 排名混合 → ES function_score
```

### 2.2 Redis ZSet 方案（最常用）

```text
// 预计算综合分数，存入 ZSet
score = normalize(sales) * 0.3 + normalize(rating) * 0.4 + normalize(freshness) * 0.3
ZADD rank:products {score} product:{id}

// 查询 Top N
ZREVRANGE rank:products 0 19 WITHSCORES

// 查询某商品排名
ZREVRANK rank:products product:{id}
```

**优点**：O(log N) 更新，O(log N) 查排名，O(N) 查范围
**缺点**：字段更新需重算分数

### 2.3 数据库方案

```sql
-- 预计算分数列 + 索引
ALTER TABLE products ADD COLUMN rank_score DECIMAL(10,4);
CREATE INDEX idx_rank_score ON products(rank_score DESC);

-- 查询
SELECT * FROM products ORDER BY rank_score DESC LIMIT 20;
```

### 2.4 增量更新策略

```text
字段变化（如销量 +1）
    ↓ MQ 异步通知
排名计算服务
    ↓ 只重算该条目的综合分数
Redis ZADD / DB UPDATE
```

避免全量重算，只更新变化的条目。

---

## 三、动态权重策略

| 策略 | 实现方式 | 适用场景 |
|------|---------|---------|
| **运营配置** | 权重存数据库/配置中心 | 变化不频繁 |
| **上下文驱动** | 场景标签 × 权重表 | 大促/日常/新品 |
| **用户偏好** | 用户画像 × 权重向量 | 个性化推荐 |
| **时间衰减** | score × decay^age | 新闻/社交 Feed |
| **A/B 测试** | 多组权重并行 | 持续优化 |

---

## 四、5 大陷阱

### 陷阱 1：不做归一化直接加权

```text
❌ score = sales * 0.5 + rating * 0.5
// 销量 10000 vs 评分 4.5 → 销量完全主导

✅ score = normalize(sales) * 0.5 + normalize(rating) * 0.5
```

### 陷阱 2：所有字段用同一种归一化

```text
❌ 幂律分布的销量用 Min-Max → 头部 1% 商品占据 99% 分数区间
✅ 销量用 Log 归一化，评分用 Min-Max
```

### 陷阱 3：固定权重不调整

```text
❌ 上线后权重永远不变
✅ 运营可调 + 定期 A/B 测试
```

### 陷阱 4：实时计算全量排名

```text
❌ 每次请求都计算 100 万条的综合分数 → 超时
✅ 预计算 + 增量更新 + 缓存
```

### 陷阱 5：忽略缺失值

```text
❌ 新品没有销量 → 分数为 0 → 永远排最后
✅ 缺失值填充（中位数 / 类目平均值 / 不参与计算）
```

---

## 五、面试话术（30 秒版）

> "多字段动态排名的核心是**归一化 + 加权 + 工程权衡**。
>
> 首先，不同字段量纲不同，不能直接加权。需要根据数据分布选择归一化方法：幂律分布用 Log，正态分布用 Z-Score，有界值用 Min-Max。
>
> 然后，根据场景选择加权公式：简单可控用线性加权，一票否决用几何加权，特征交互复杂用 ML 模型。
>
> 工程实现上，小数据量用 DB ORDER BY + 复合索引，百万级用 Redis ZSet + 预计算，搜索混合场景用 ES function_score。权重通过运营后台配置 + A/B 测试持续优化。
>
> 关键要避免 5 个陷阱：不归一化、统一归一化、固定权重、实时全量计算、忽略缺失值。"

---

## 六、深度阅读

- [主模块深度章节](../../../04.system-design/04-high-performance/multi-field-ranking/README.md) — 归一化方法论 + 加权公式 + 动态权重 + 6 大典型场景 + 6 大反模式
- [商品搜索排序](../product-search/README.md) — 搜索场景的排序策略（BM25 + 多阶段管道）

---

← [返回: 04.system-design](../README.md)
