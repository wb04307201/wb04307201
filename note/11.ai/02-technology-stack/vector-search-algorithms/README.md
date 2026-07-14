<!--
module:
  parent: ai
  slug: ai/vector-search-algorithms
  type: article
  category: 主模块子文章
  summary: 向量检索算法选型：HNSW vs IVF vs DiskANN + 4 维权衡（内存/磁盘/QPS/Recall）
-->

# 向量检索算法选型 —— HNSW vs IVF vs DiskANN 与 4 维权衡

← 返回 [技术栈](../README.md)

> 向量检索是 RAG / 推荐系统 / 语义搜索的核心组件。本文从 **HNSW / IVF / DiskANN** 3 大算法的原理、规模边界、4 维权衡（内存/磁盘/QPS/Recall）系统讲清楚向量检索选型决策。

> **面试场景**：这是 AI 架构师高频面试题——很多人只学 HNSW，但 10 亿级必须换算法。面试版（30/60/90 秒话术）见 [咬文嚼字·11.ai/vector-search-algorithms](../../../13.split-hairs/11.ai/vector-search-algorithms/README.md)。

---

## 一、向量检索基础回顾

### 1.1 核心问题

给定查询向量 q，从 N 个候选向量中找到 top-k 最相似的：

```text
传统精确搜索（Flat）：
- 时间复杂度：O(N × D)
- 10 亿 × 1024 维 = 4 万亿次距离计算 → 不可能毫秒级

近似最近邻（ANN）：
- 时间复杂度：O(log N) 或 O(√N)
- 召回率 95%+ 可接受 → 工业级首选
```

### 1.2 召回率 vs 准确率

| 指标 | 含义 | 向量检索中 |
|------|------|-----------|
| **Recall@K** | top-K 中包含正确答案的比例 | 95%+ 是生产硬要求 |
| **Precision@K** | top-K 中正确率 | 通常很高（>90%）|
| **QPS** | 每秒查询数 | 单机 1K-10K 典型 |
| **P99 Latency** | 99% 查询延迟 | 毫秒级 |

**核心权衡**：Recall ↑ 往往 QPS ↓，Latency ↑。

## 二、HNSW 深度

### 2.1 原理

**Hierarchical Navigable Small World（分层可导航小世界图）**：

```text
层级 3（顶层）：稀疏连接，log N 节点
层级 2：中等等密度
层级 1：密集连接
层级 0（底层）：所有向量
```

查询时：
1. 从顶层入口节点开始
2. 贪心搜索：找最近邻
3. 下降到下一层
4. 重复直到底层
5. 底层 ef-搜索：取 top-ef 候选，排序返回

### 2.2 时间复杂度

```text
构建：O(N × log N × M × efConstruction)
查询：O(log N × M) 平均
```

### 2.3 内存占用

```text
每个向量：
- 原始向量：D × 4 字节（FP32）
- 图边：M × 4 字节 × 2（有向）= 8M 字节
- 距离缓存：~8 字节
合计：D × 4 + 8M + 8 字节

10 亿 × 1024 × 4 + 8 × 16 = 4 TB + 128 GB
```

### 2.4 HNSW 优缺点

| ✅ 优点 | ❌ 缺点 |
|---------|---------|
| 速度最快（10K+ QPS）| **全内存**（10 亿级不可行）|
| 召回率高（>95%）| 构建慢（小时级）|
| 实现成熟（hnswlib / Faiss / Milvus）| 内存 ≥ 4 × 数据大小 |
| 支持增量更新 | 不适合 > 10 亿 |

## 三、IVF 深度

### 3.1 原理

**Inverted File（倒排文件）**：聚类分桶

```text
训练阶段：
- K-means 聚类 → nlist 个聚类中心
- 每个向量分配到最近的桶

查询阶段：
1. 找最近的 nprobe 个聚类中心
2. 在这些桶内暴力搜索
3. 返回 top-k
```

### 3.2 时间复杂度

```text
构建：O(N × nlist × iter)
查询：O(nprobe × 桶大小 × D) ≈ O(nprobe × N/nlist × D)
```

### 3.3 召回率瓶颈

**10 亿级 IVF 召回率问题**：

| nlist | 桶大小（10B）| Recall@10 (nprobe=10) |
|-------|------------|---------------------|
| 1 万 | 10 万 | 60% |
| 10 万 | 1 万 | 75% |
| 100 万 | 1000 | **85%** |
| 1000 万 | 100 | 92% |

**关键问题**：nlist 大 → 桶小 → 查询快但召回低；nlist 小 → 桶大 → 召回高但查询慢。**10 亿级难以达到 95%+ Recall**。

### 3.4 IVF + PQ（量化）

**Product Quantization**：向量分块 + 聚类编码

```text
1024 维 → 切 8 段 × 128 维
每段 256 个聚类中心（1 字节）
压缩后：8 字节 / 向量
压缩比：128 倍
```

**IVF + PQ 内存**：

```text
10 亿 × 8 字节 = 8 GB（向量）
+ IVF 桶信息：~10 GB
+ 距离计算：CPU 密集
```

**召回率损失**：2-5%（相比 Flat）。

### 3.5 IVF 优缺点

| ✅ 优点 | ❌ 缺点 |
|---------|---------|
| 内存省（PQ 量化后）| **Recall 受限**（10 亿级难达 95%）|
| 实现成熟 | 需要训练聚类 |
| 适合大批量查询 | nprobe 调优敏感 |
| 适合标量过滤 | 不如 HNSW 快 |

## 四、DiskANN 深度

### 4.1 原理（微软 2023）

**核心创新**：

1. **Vamana 图索引**（比 HNSW 更适合磁盘）
   - 单调图约束：每个邻居 rank ≤ query-to-entry 距离
   - 减少随机 I/O

2. **向量压缩到磁盘**
   - 原始向量用 PQ 压缩 → 存 SSD
   - 内存只存图（GB 级）+ 缓存（按需加载）

3. **SSD 优化**
   - Page size 对齐 SSD block（4-16KB）
   - 批量化预取（async I/O）
   - 磁盘带宽饱和

### 4.2 数据布局

```text
内存（10-50 GB）：
- Vamana 图（每向量 ~16 字节 × 1B = 16 GB）
- 热门向量缓存（20-30 GB）

SSD（4 TB）：
- 压缩向量（8-16 字节 / 向量 × 10B = 80-160 GB）
- 全量原始向量（可选，用于重排）
```

### 4.3 性能（DiskANN 论文）

| 数据规模 | 算法 | QPS | Recall@10 | 内存 |
|---------|------|-----|-----------|------|
| 10M | HNSW | 10K | 99% | 8 GB |
| 100M | HNSW | 5K | 98% | 80 GB |
| **1B** | **DiskANN** | **2K-10K** | **>95%** | **10-50 GB** |
| **10B** | **DiskANN + 分布式** | **10K+** | **>95%** | **每节点 10-50 GB** |

### 4.4 DiskANN 优缺点

| ✅ 优点 | ❌ 缺点 |
|---------|---------|
| **支持 10 亿-100 亿级** | 需要 NVMe SSD |
| 内存极省（10-50 GB）| 实现复杂 |
| 召回率高（>95%）| 调优需要 SSD 经验 |
| 适合磁盘扩展 | 延迟略高于 HNSW（1-5ms）|
| 微软开源（DiskANN / SPTAG）| 索引构建慢 |

## 五、4 维权衡决策矩阵

### 5.1 决策矩阵

| 数据规模 | QPS 要求 | Recall 要求 | 推荐算法 |
|---------|---------|------------|---------|
| < 1000 万 | 任意 | > 95% | **HNSW 全内存** |
| 1000 万 - 1 亿 | 高（10K+）| > 95% | HNSW + 量化（SQ8）|
| 1000 万 - 1 亿 | 中（1K-5K）| 90%+ | IVF + Flat 重排 |
| **1 亿 - 10 亿** | **中-高** | **> 95%** | **DiskANN** ⭐ |
| **1 亿 - 10 亿** | **中** | **85%+** | **IVF + PQ** |
| > 10 亿 | 任意 | > 95% | **DiskANN + 分布式** |
| > 10 亿 | 任意 | 90%+ | **ScANN**（Google）|

### 5.2 决策树

```text
规模？
├─ < 1000 万 → HNSW 全内存
├─ 1000 万 - 1 亿 → HNSW + 量化 / IVF + Flat
├─ 1-10 亿 → Recall > 95%？→ DiskANN；否则 IVF + PQ
└─ > 10 亿 → DiskANN + 分布式
```

## 六、生产环境 3 大调优

### 6.1 调优 1：硬件选型

```text
10 亿级向量检索的硬件最低配置：
- CPU：32+ 核（向量计算密集）
- 内存：256 GB+（HNSW 需要）/ 64 GB（DiskANN）
- 存储：NVMe SSD 4 TB+（IOPS > 500K）
- 网络：10 Gbps（分布式场景）

推荐：Milvus 2.x + DiskANN + NVMe SSD
```

### 6.2 调优 2：参数调优（DiskANN 实战）

```python
# DiskANN 关键参数（以 Milvus 为例）
diskann_config = {
    "index_type": "DiskANN",
    "R": 64,                  # 图度数（越大召回越高）
    "L": 100,                 # 候选集大小（构建）
    "alpha": 1.2,             # 图修剪因子
    "search_L": 100,          # 搜索候选集
    "page_size": 8192,        # 8KB 对齐 SSD block
    "compression": "PQ",      # 向量压缩
    "compression_ratio": 0.5, # 压缩到 50%
}

# 调优经验值（10 亿级）
# - Recall 优先：R=128, L=200, search_L=200
# - QPS 优先：R=32, L=50, search_L=50
# - 平衡：R=64, L=100, search_L=100
```

### 6.3 调优 3：混合检索（向量 + 标量）

```python
# 10 亿级场景常见：相似度 + 时间过滤 + 标签
results = collection.search(
    query_vector=query_embedding,
    top_k=10,
    filter="timestamp > 2025-01-01 AND category IN ('AI', '数据库')",
)

# DiskANN 优化：图遍历时跳过不符合 filter 的节点
# - 减少 30-50% 访问节点数
# - Recall 损失 < 2%
```

## 七、业界向量库与算法支持

| 向量库 | HNSW | IVF | DiskANN | 适用规模 |
|--------|------|-----|---------|---------|
| **Milvus** | ✅ | ✅ | ✅（2.x）| < 100 亿 |
| **Qdrant** | ✅ | ⚠️ | ❌ | < 1 亿 |
| **Weaviate** | ✅ | ✅ | ❌ | < 1 亿 |
| **Pinecone** | ✅ | ⚠️ | ❌ | 托管（< 1 亿）|
| **Vespa** | ✅ | ✅ | ❌ | < 10 亿 |
| **ScANN (Google)** | ❌ | ❌ | ✅（变体）| 10 亿+ |
| **Chroma** | ✅ | ⚠️ | ❌ | < 1000 万 |
| **LanceDB** | ✅ | ❌ | ⚠️ | < 1 亿 |

**生产推荐**：
- 1 亿以下：Qdrant / Milvus / Weaviate
- **1-10 亿：Milvus 2.x + DiskANN** ⭐
- 10 亿以上：Milvus 分布式 + DiskANN / ScANN

## 八、10 亿级实战案例

### 8.1 案例 1：电商推荐系统

```text
数据：10 亿商品 Embedding（512 维，FP16）
召回：Recall@100 > 95%
延迟：P99 < 10ms
QPS：5K

方案：Milvus 2.x + DiskANN
配置：R=64, L=100, search_L=100
硬件：NVMe SSD 8TB × 4（RAID0）
```

### 8.2 案例 2：RAG 知识库

```text
数据：1 亿文档 Chunk Embedding（1024 维，FP16）
召回：Recall@10 > 95%
延迟：P99 < 50ms
QPS：1K

方案：Milvus 2.x + DiskANN
配置：R=32, L=50, search_L=50
硬件：单台 NVMe SSD 2TB
```

### 8.3 案例 3：图像搜索（亿级）

```text
数据：5 亿图片 Embedding（512 维，FP16）
召回：Recall@50 > 90%
延迟：P99 < 20ms
QPS：10K

方案：Milvus 2.x + HNSW + SQ8 量化
配置：M=32, efConstruction=400, ef=100
硬件：单台 256GB 内存（量化后 200GB 数据）
```

## 九、与"驾驭演进"主线的关联

向量检索算法演进是 [驾驭演进主线](../../04-architecture/llm-control-evolution/README.md) 在 RAG 领域的具体体现：

| 阶段 | 向量检索 | 适配规模 |
|------|---------|---------|
| Prompt | 无检索（小数据人工查）| < 1 万 |
| Context | 关键词检索 / 简单向量 | 1-100 万 |
| Harness | HNSW 全内存（首选）| < 1000 万 |
| **Loop** | **DiskANN（10 亿级）** | **1-100 亿** |

**核心范式转移**：从"全内存图"到"磁盘图"——和数据库从"内存数据库"到"磁盘数据库"是同一个故事。

## 十、相关章节

**面试题**：
- [咬文嚼字·11.ai/vector-search-algorithms（30/60/90 秒话术）](../../../13.split-hairs/11.ai/vector-search-algorithms/README.md)

**12.story 实战**：
- [12.story/37-vector-database-and-embedding（味道仓库 4 大调优）](../../../12.story/37-vector-database-and-embedding.md)

**同主模块**：
- [Context Engineering（Context 三件套）](../context-engineering/README.md)
- [Function Calling](../function-calling/README.md)

**实战应用**：
- [11.ai/08-llmops/agentic-search-vs-rag（Agentic Search）](../../08-llmops/agentic-search-vs-rag/README.md)
- [11.ai/08-llmops/01-rag-vs-finetuning（RAG 架构）](../../08-llmops/01-rag-vs-finetuning/README.md)

---

## 📊 本节统计

- **覆盖算法**：3 大类（HNSW / IVF / DiskANN）+ 4 维权衡
- **规模分级**：5 个档位（< 1000 万 → > 10 亿）
- **实战案例**：3 个（电商推荐 / RAG / 图像搜索）
- **业界向量库对比**：8 家
- **关联章节**：5 大类（面试题 / 主模块 / 实战 / 故事 / 驾驭演进）

---

> 📅 2026-07-03 · 11.ai/02-technology-stack · ⭐⭐⭐⭐⭐

← [返回: AI 知识体系 · vector-search-algorithms](README.md)
