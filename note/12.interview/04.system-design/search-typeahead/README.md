<!--
question:
  id: 04.system-design-search-typeahead
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [04.system-design, typeahead, autocomplete, 搜索建议, Trie, Redis ZSet, 系统设计]
-->

# 设计搜索框 typeahead / autocomplete —— 前缀联想实时系统设计

> 一句话定位：**后端 / 架构面试经典系统设计题**。考察的不是"模糊搜索怎么查"，而是 **前缀索引选型 + 实时增量更新 + 实名商家权重 + 抗高 QPS + 防抖与限流**。深度实战见主模块 [高性能篇之 product-search](../../../06.distributed-systems/04-high-performance/product-search/README.md)（全文搜索，已沉淀 250 行）。

> **系列定位**：高频系统设计题（社招必考 / Google / Baidu / 淘宝面试原题）。配套兄弟题：[商品搜索系统设计](../product-search/README.md)（全文搜索互补）、[多字段动态排名](../multi-field-ranking/README.md)（排序权重）、[缓存热点 Key 问题](../cache-hot-key/README.md)（热门查询优化）、[限流算法](../rate-limiting/README.md)（用户输入限流）。

---

⭐⭐⭐⭐⭐ 深度级别（架构师级）
📚 前置知识：Trie 树 / Redis ZSet / Kafka / 前缀索引 / 防抖 debounce

---

## 引子：面试经典开场

面试官："设计一个电商搜索框的 typeahead 功能：用户每输入一个字，500ms 内返回 Top 10 联想建议（含商品名 / 商家名 / 分类名），要求已实名认证的商家权重提升。"

大多数人答："用 Elasticsearch 的 completion suggester / prefix query。"

面试官追问：
1. 每次输入都查 ES？性能扛得住吗？前端怎么防抖？
2. 商家实名状态变化时，typeahead 索引怎么实时更新？
3. 热门商品 / 季节性商品怎么动态调权？
4. 输入框为空 / 单字 / 长 query 行为差异怎么设计？
5. 100 万商品 + 10 万商家，索引多大？内存放得下吗？

大多数人卡在追问上。**这道题考察的不是"用 ES completion suggester"，而是"前缀索引 + 实时增量更新 + 排序权重 + 抗高 QPS + 端到端延迟优化"**。

---

## 一、核心问题拆解

### 1.1 typeahead 的核心要求

- **响应延迟**：<100ms（用户输入时实时返回，P99 99ms）
- **准确性**：Top 10 必须相关（不能出现无关商品）
- **实时性**：商家实名状态变化 → 5s 内反映到联想列表
- **高并发**：峰值 10 万 QPS（大促开抢瞬间）
- **首字命中率**：>60%（用户输入第一个字就命中推荐）

### 1.2 与全文搜索的关键区别

| 维度 | typeahead（前缀联想） | 全文搜索 |
|------|---------------------|----------|
| 输入长度 | 1-5 个字符 | 完整 query |
| 输出数量 | Top 10 固定 | Top K 不固定 |
| 响应延迟 | **<100ms** | <500ms 可接受 |
| 数据更新 | **实时增量** | 批量 + binlog |
| 索引结构 | **前缀索引**（Trie） | 倒排索引 |
| 排序信号 | 权重 + 实名 + 销量 + 时令 | 相关性 + 业务 |
| 输入时机 | 用户键入时 | 用户回车搜索时 |
| 模糊容忍 | 低（前缀必须匹配） | 高（编辑距离） |
| 实现复杂度 | 较高（实时性） | 中等（离线构建） |

**两者完全互补**：先 typeahead（前缀匹配、实时建议）→ 再全文搜索（精确查询、深入检索）。

### 1.3 5 大非功能性需求

1. **实时性**：增量更新延迟 <5s（商家实名通过 → 5s 内生效）
2. **高可用**：搜索框瘫痪 = 平台瘫痪（必须 99.99% SLA）
3. **可扩展**：商品量从 10 万 → 1000 万（索引可水平扩展）
4. **个性化**：实名商家权重 + 用户偏好 + 时令因子
5. **容错性**：ES 故障自动降级为本地缓存（不可因依赖故障影响搜索）

---

## 二、4 大主流方案演进

### 2.1 方案 1：数据库 LIKE 前缀匹配（最简单，撑不住）

**架构**：

```sql
SELECT * FROM products
WHERE name LIKE '苹%'  -- 前缀 LIKE
LIMIT 10;
```

**优点**：
- 实现极简（10 行代码搞定）
- 无额外依赖（DB 现成）
- 数据强一致

**缺点**：
- 不走索引（除非有专门的前缀索引）
- 每秒 10 万 QPS → DB 必死（单机 5000 QPS 极限）
- 无法整合实名权重（要再 JOIN 商家表）
- 网络延迟高（DB 通常在内网，但查询慢）

**适用**：仅 Demo / 内部工具 / 极小规模（<1 万商品）

---

### 2.2 方案 2：Elasticsearch completion suggester（中等规模，1-100 万）

**架构**：

```json
// ES 索引 mapping
{
  "mappings": {
    "properties": {
      "name_suggest": {
        "type": "completion",
        "contexts": [
          { "name": "verified", "type": "category" },  // 实名上下文
          { "name": "category", "type": "category" }    // 分类上下文
        ]
      },
      "verified": { "type": "boolean" },
      "sales": { "type": "long" }
    }
  }
}
```

```bash
GET products/_search
{
  "suggest": {
    "product_suggest": {
      "prefix": "苹",
      "completion": {
        "field": "name_suggest",
        "size": 10,
        "contexts": {
          "verified": ["yes", "no"]  // 实名过滤
        }
      }
    }
  }
}
```

**优点**：
- 内置 FST 索引（前缀查询 O(1)，内存极省）
- 支持 context 过滤（实名 / 分类）
- 增量更新方便（API 即可）
- 稳定性高（ES 久经考验）

**缺点**：
- ES 集群运维复杂（JVM 调优 / 分片规划）
- 大促 10 万 QPS → ES 集群压力大（需 50+ 节点）
- 自定义权重困难（需要 rebuild index）
- 实名权重动态调整不灵活（context 重建）

**适用**：1-100 万商品中型电商

---

### 2.3 方案 3：Redis Sorted Set + Trie 树预加载（推荐，10-100 万）

**架构**：

```text
商品数据 → 离线构建 Trie 树（前缀 → Top 10）
        → 序列化为 Redis 字符串
        → 加载到 Redis（按业务分 key）

查询：用户输入"苹" → 计算前缀哈希 → 查 Redis → 返回 Top 10
更新：商家实名状态变化 → Kafka 增量事件 → 重建受影响前缀的 Trie → 更新 Redis
```

**关键设计**：

- **Trie 树序列化**：每个节点存 Top 10 推荐列表（按权重排序）
- **前缀查询**：从根节点沿路径走到目标前缀节点，返回其 Top 10
- **增量更新**：商家实名变化 → 重建受影响的 N 个前缀节点（仅 N 个，非全量）
- **缓存分层**：Redis（权威）+ 本地 Caffeine（热点）

**优点**：
- 查询 O(prefix_length)，极快（<5ms）
- 支持复杂权重（实名 + 销量 + 时令 + 个性化）
- 增量更新方便（Kafka 事件驱动）
- 内存可控（10 万商品前缀树约 200MB）

**缺点**：
- 重建前缀节点成本高（热门前缀需要持续更新）
- Trie 树序列化 / 反序列化有学习成本
- 字符集需设计（中文需要双数组 Trie 树 / AC 自动机）
- 冷启动慢（首次需全量构建）

**适用**：10-100 万商品主流电商（**推荐方案**）

---

### 2.4 方案 4：搜索引擎 + 实时索引（百万商品 + 复杂查询）

**架构**：

```text
商品 → Kafka → Flink 实时计算（权重整合）
                ↓
        ES + 自定义 rescore（实名商家加权）
                ↓
        边缘 CDN 缓存（前缀 Top 10）
```

**关键设计**：

- Flink 实时计算权重（实名 + 时令 + 销量 + 个性化）
- ES 自定义 rescore 插件整合权重（二阶段排序）
- CDN 边缘缓存高频前缀（地域化）
- 实时 binlog 同步 + 准实时索引

**优点**：
- 实时性最强（Flink 毫秒级）
- 支持个性化（用户维度权重）
- 横向扩展好（Kafka + Flink 都是分布式）

**缺点**：
- 架构复杂（Kafka + Flink + ES + CDN）
- 运维成本高（4 个组件都要维护）
- 实施周期长（需 2-3 个月）

**适用**：淘宝 / 京东 / 美团等超大平台（>100 万商品）

---

## 三、4 大方案对比矩阵

| 维度 | DB LIKE | ES completion | Redis ZSet + Trie | ES + Flink |
|------|---------|---------------|-------------------|------------|
| 适用规模 | <1 万 | 1-100 万 | **10-100 万** | 100 万+ |
| 响应延迟 | <50ms (单查询) | <50ms | **<20ms** | <100ms |
| 增量更新 | DB 写 | ES API | **Kafka + 重建前缀** | Flink 实时 |
| 实名权重 | ⚠️ 难 | ✅ context | ✅ 自定义 | ✅ rescore |
| 内存占用 | 低 | 中 | **高（需预估）** | 高 |
| 复杂度 | 极低 | 中 | **中** | 高 |
| 推荐场景 | Demo | 中型电商 | **主流电商** | 大型平台 |
| 首字命中率 | 高 | 高 | **高** | 高 |
| 个性化 | ❌ | ⚠️ 有限 | ✅ 自定义 | ✅ 强 |
| 故障降级 | ⚠️ DB 挂 = 瘫 | ⚠️ ES 挂 = 慢 | ✅ 本地缓存 | ⚠️ 链路长 |

---

## 四、typeahead 核心机制详解

### 4.1 前缀索引数据结构

**Trie 树**（字典树）：每个节点存 Top 10 + 子节点指针

```text
root
├─ p → [苹果(verified), 葡萄] (Top 2)
│   ├─ pi → [苹果] (Top 1)
│   │   ├─ pin → [苹果] (Top 1)
│   │   │   ├─ ping → [苹果, 苹果派] (Top 2)
│   │   │   └─ pingguo → [苹果] (Top 1)
│   │   └─ pin → [苹果] (Top 1)
│   └─ pu → [葡萄, 普洱茶] (Top 2)
└─ x → [西瓜, 虾] (Top 2)
```

**关键点**：
- 每个节点存 Top 10（按 score 排序）
- 查询：从根沿字符路径走，到目标节点返回 Top 10
- 时间复杂度：O(prefix_length)，与商品总量无关

**倒排索引**（ES completion）：name_suggest 字段，前缀哈希 → 文档列表

**Redis Sorted Set**：score = 权重，member = 商品 ID

```bash
# Redis 中按前缀分 key
ZADD prefix:苹 90 "product:123"  # 商品 123 权重 90
ZADD prefix:苹果 85 "product:456"
ZADD prefix:苹 95 "product:789"

# 查询 Top 10
ZRANGEBYSCORE prefix:苹 -inf +inf WITHSCORES LIMIT 0 10
```

### 4.2 排序权重公式

```python
score = base_weight              # 基础权重（商品质量分）
      + verified_weight          # 实名商家 +20
      + sales_weight             # 销量权重 +log10(sales)
      + freshness_weight         # 时令商品 +10
      + personalization_weight   # 用户偏好 +5
      - penalty                  # 违规商品 -100
```

**权重细节**：

```python
def compute_score(product, user):
    score = 0
    # 基础权重（商品静态质量分）
    score += product.quality_score * 1.0
    
    # 实名权重（核心差异化）
    if product.merchant.verified:
        score += 20  # 实名商家统一 +20
    
    # 销量权重（热度因子）
    score += math.log10(product.sales + 1) * 2
    
    # 时令权重（季节性）
    if product.is_seasonal_now():
        score += 10
    
    # 个性化权重（用户偏好）
    if user.has_purchased_category(product.category):
        score += 5
    
    # 违规惩罚
    if product.has_violation():
        score -= 100
    
    return score
```

**权重计算时机**：
- 实时计算（Flink 流式）：<1s 延迟
- 离线计算（T+1）：适合不敏感字段
- 增量更新（Kafka 事件）：实名 / 销量变化

### 4.3 增量更新流程

```text
商家状态变化（实名 / 下架 / 改价）
  ↓
Kafka 事件（topic=product_update）
  ↓
增量更新服务消费
  ├─ 计算受影响的 N 个前缀（商家所有商品名的所有前缀）
  ├─ 重建这 N 个前缀的 Top 10（拉取最新商家 + 商品数据）
  ├─ 更新 Redis（Pipeline 批量写入）
  └─ 失效本地缓存
```

**示例**：商家"苹果旗舰店"通过实名认证

```text
1. Kafka 事件：{ merchant_id: 123, verified: true }
2. 查出商家所有商品名：["苹果", "苹果 12", "苹果笔记本"]
3. 计算所有前缀：
   - "苹果" → ["苹", "苹果"]
   - "苹果 12" → ["苹", "苹果", "苹果 ", "苹果 1", "苹果 12"]
   - "苹果笔记本" → ["苹", "苹果", "苹果笔", "苹果记", "苹果笔", ...]
4. 重建这 N 个前缀节点的 Top 10
5. Pipeline 写入 Redis（500 个 key 批量）
6. 失效本地 Caffeine 缓存
```

**延迟估算**：500 前缀重建 + Redis 写入 ≈ 200ms

### 4.4 防抖与限流

**前端防抖**：

```javascript
let timer;
function onInput(text) {
  clearTimeout(timer);
  timer = setTimeout(() => {
    fetch(`/api/typeahead?q=${text}`);
  }, 300);  // 300ms 内不重复请求
}
```

**后端限流**（每用户每秒最多 10 次查询）：

```java
// 令牌桶限流
RateLimiter limiter = RateLimiter.create(10);  // 10 QPS per user
if (!limiter.tryAcquire(100, TimeUnit.MILLISECONDS)) {
    return Result.error("RATE_LIMITED");
}
```

**结果去重**（前端缓存）：

```javascript
const cache = new Map();
function getTypeahead(text) {
  if (cache.has(text) && Date.now() - cache.get(text).time < 30000) {
    return cache.get(text).data;  // 30s 内不重复请求
  }
  // ... fetch ...
}
```

---

## 五、性能与抗高并发

### 5.1 缓存分层

```text
用户输入"苹"
  ↓
L1 本地 Caffeine（5s TTL，size=10万）→ 命中返回（80% 流量）
  ↓ miss
L2 Redis Sorted Set（查 Top 10）→ 命中返回（19% 流量）
  ↓ miss（极少见）
L3 实时计算 ES / Trie → 返回（1% 流量，冷门前缀）
```

**流量分布**：
- L1 命中：80%（热点前缀热点 query）
- L2 命中：19%（L1 过期但 Redis 命中）
- L3 计算：1%（冷门前缀）

### 5.2 大促压测数据（参考）

| 组件 | 单机 QPS | 集群规模 | 峰值应对 |
|------|---------|---------|---------|
| L1 Caffeine | 50 万 | 10 台 | 500 万 QPS |
| L2 Redis | 5 万 | 4 分片 | 20 万 QPS |
| L3 Trie 计算 | 1000 | 50 台 | 5 万 QPS |

**大促 10 万 QPS 应对**：
- L1 命中 80% → 8 万 QPS 直接返回（10 台 × 50 万 / 10 = 50 万，余量充裕）
- L2 命中 19% → 2 万 QPS（4 分片 × 5 万 = 20 万，余量充裕）
- L3 计算 1% → 1000 QPS（50 台 × 1000 = 5 万，余量充裕）

### 5.3 实名商家权重实时调整

**场景**：实名商家商品提交审核 → 通过 → 权重 +20

**实现**：

```java
// 1. 审核通过事件
productService.verify(merchantId);

// 2. 重算权重
double newScore = computeScore(product, verified=true);

// 3. 更新 Redis（原子操作）
redisTemplate.opsForZSet().add(
    "prefix:" + prefix, 
    "product:" + productId, 
    newScore
);

// 4. 失效本地缓存
localCache.invalidate(prefix);
```

**延迟**：从审核通过到联想列表生效 < 5s

### 5.4 长查询优化

**问题**：用户输入"苹果手机壳 iPhone 15 Pro Max 256G"（30 字符），前缀 Trie 太深

**优化**：
- 仅匹配前 5 个字符（前缀截断）
- 后缀匹配用 N-gram（如双字符 N-gram）
- 中文用 AC 自动机（多模式匹配）

---

## 六、5 大反模式

### ❌ 反模式 1：每按一个键都查后端

**错**：
```javascript
// 错：keydown 每个字符都发请求
input.addEventListener('keydown', (e) => {
  fetch(`/api/typeahead?q=${input.value}`);
});
```

**对**：
```javascript
// 对：debounce 300ms
let timer;
input.addEventListener('input', (e) => {
  clearTimeout(timer);
  timer = setTimeout(() => {
    fetch(`/api/typeahead?q=${input.value}`);
  }, 300);
});
```

**后果**：每键 1 次 → 每 300ms 1 次，QPS 降低 90%

---

### ❌ 反模式 2：没有缓存层

**错**：每次查都打 Redis / ES

**对**：本地 Caffeine + Redis 双层缓存

**后果**：L1 80% 流量 → 后端流量降低 80%

---

### ❌ 反模式 3：实名权重写死

**错**：实名商家固定 +20

**对**：实名权重可配置 + A/B 测试调优

```yaml
# 配置文件
typeahead:
  weights:
    verified: 20  # 可调
    sales_factor: 2
    seasonal: 10
```

**好处**：A/B 测试 + 不同业务线不同权重

---

### ❌ 反模式 4：增量更新走全量重建

**错**：每次商家变化重建全量索引（10 万商品全量重建 5 分钟）

**对**：只重建受影响的 N 个前缀节点

```java
// 错：全量
void rebuildAll() {
  for (Product p : allProducts) {
    buildIndex(p);
  }
}

// 对：增量
void rebuildAffected(merchantId) {
  List<Product> products = getMerchantProducts(merchantId);
  Set<String> affectedPrefixes = new HashSet<>();
  for (Product p : products) {
    for (int i = 1; i <= p.name.length(); i++) {
      affectedPrefixes.add(p.name.substring(0, i));
    }
  }
  for (String prefix : affectedPrefixes) {
    rebuildPrefix(prefix);
  }
}
```

**效果**：5 分钟 → 200ms

---

### ❌ 反模式 5：忽略大促压测

**错**：没压测直接上线，大促被打挂

**对**：提前压测 + 弹性扩容 + 降级预案

**压测 5 步走**：
1. 流量评估（预估峰值 QPS）
2. 单机压测（确定单节点能力）
3. 全链路压测（找出瓶颈）
4. 弹性扩容（K8s HPA）
5. 降级预案（Redis 挂 → ES 兜底 → 本地缓存兜底）

---

## 七、面试高频追问

### Q1：typeahead 与全文搜索有什么区别？

**核心回答**：
- typeahead：前缀匹配、实时建议、Top 10 固定、<100ms
- 全文搜索：完整 query、Top K 不固定、<500ms
- 两者**完全互补**：先 typeahead（前缀匹配）→ 再全文（精确查询）

### Q2：Trie 树 vs ES completion suggester 怎么选？

**核心回答**：
- Trie 树：自定义权重灵活、内存可控、但需自己实现
- ES completion：开箱即用、稳定、但权重调整不灵活
- 选型：10 万商品、复杂权重 → Trie；1-100 万、稳定优先 → ES completion

### Q3：商家实名状态变化，typeahead 索引怎么实时更新？

**核心回答**：
1. Kafka 事件（topic=product_update）
2. 计算受影响的 N 个前缀（商家所有商品名的所有前缀）
3. 重建这 N 个前缀的 Top 10
4. Pipeline 批量写入 Redis
5. 失效本地缓存
6. 延迟 <5s

### Q4：怎么把"实名商家"权重融合到 typeahead？

**核心回答**：
- 权重公式加一项：`verified_weight = 20 if verified else 0`
- 实时更新：Flink 流式计算 or Kafka 事件驱动重建
- A/B 测试调优权重系数
- 实名商家不强制置顶（避免信任滥用），但优先级提升

### Q5：10 万 QPS 怎么抗？

**核心回答**：
- L1 本地缓存（80% 流量）
- L2 Redis（19% 流量）
- L3 实时计算（1% 流量）
- 缓存分层 + 前端防抖 + 后端限流

### Q6：客户端防抖和服务端限流怎么配合？

**核心回答**：
- 前端 debounce 300ms（降低请求频次）
- 后端令牌桶限流（每用户 10 QPS，防止恶意刷）
- 配合：前端降低正常流量，后端兜底恶意流量

### Q7：Trie 树序列化和反序列化怎么做？

**核心回答**：
- 序列化：每个节点 ⟨前缀字符, Top 10 列表, 子节点指针⟩
- 存储：Protobuf / FlatBuffers（紧凑）
- 加载：mmap 内存映射（零拷贝）
- 增量更新：只重建变化的子树

### Q8：热门前缀查询和冷门前缀查询怎么区分优化？

**核心回答**：
- 热门前缀（"苹"、"iPhone"）：本地 Caffeine 缓存 + Redis
- 冷门前缀（"xhjs"）：直接 Trie 树查询
- 冷热分离：热门前缀独立 Redis 实例（避免相互影响）

### Q9：怎么保证 typeahead 索引与商品库的数据一致性？

**核心回答**：
- 强一致：写商品库 + 写 typeahead 索引 同一事务（性能差）
- 最终一致：Kafka 异步同步 + 周期性对账（推荐）
- 对账：每小时扫描商品库 vs typeahead 索引，找差异修复

### Q10：CDN 缓存怎么应用在 typeahead？

**核心回答**：
- 边缘节点缓存高频前缀 Top 10（5min TTL）
- 地域化：不同地域返回不同结果（地方特色商品）
- 个性化商品不进 CDN（避免全局缓存）
- 缓存键：地域 + 前缀 + 用户画像 hash

---

## 相关章节

- [商品搜索系统设计](../product-search/README.md) — 全文搜索（与 typeahead 互补）
- [多字段动态排名](../multi-field-ranking/README.md) — 排序权重策略
- [缓存热点 Key 问题](../cache-hot-key/README.md) — 热门查询优化
- [限流算法](../rate-limiting/README.md) — 用户输入限流

## 📚 参考来源

1. [ES completion suggester 官方文档](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters.html#completion-suggester)
2. [Trie 树实现 typeahead — Google 工程实践](https://ai.googleblog.com/2006/06/all-our-n-gram-are-belong-to-you.html)
3. [美团搜索框 typeahead 架构 — 美团技术团队](https://tech.meituan.com/2019/09/19/search-suggestion.html)
4. [Flink 实时计算搜索权重 — 阿里云](https://developer.aliyun.com/article/798656)
5. [Trie 树序列化方案对比 — GitHub awesome-tries](https://github.com/yyyguiqing/Awesome-Tries)

← [返回: 系统设计咬文嚼字](../../README.md)
