<!--
module:
  parent: ai
  slug: ai/kv-cache
  type: article
  category: 主模块子文章
  summary: KV Cache 推理核心机制（内存布局 / 复杂度 / 显存优化 / MQA/GQA/MLA）
  depth: ⭐⭐⭐⭐
-->

# KV Cache

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：KV Cache = **推理时缓存已计算的 K/V 矩阵**，避免每 token 重算历史 Attention。**自回归 LLM 推理加速的核心技术**，没有 KV Cache 就无法服务在线请求。

---

## 🎯 一句话理解

推理生成第 n 个 token 时，**只需计算新 token 的 Q**，K 和 V 可从历史缓存读取 → 计算量从 O(n²) 降到 O(n)，**但显存从 O(1) 涨到 O(n)**。

---

## 📐 内存布局

每生成 1 个 token，需要在显存缓存：

```text
K 缓存: [num_layers, num_heads, seq_len, head_dim]
V 缓存: [num_layers, num_heads, seq_len, head_dim]
```

**单 token 占用**：

```text
2 × num_layers × num_heads × head_dim × dtype_size
= 2 × 32 × 32 × 128 × 2 bytes (FP16)
= 0.5 MB / token
```

---

## 📊 显存占用实测

| 模型 | num_layers | hidden | 1K context | 8K context | 32K context | 128K context |
|------|-----------|--------|-----------|-----------|------------|--------------|
| 7B (LLaMA) | 32 | 4096 | 0.5 GB | 4 GB | 16 GB | 64 GB |
| 13B | 40 | 5120 | 0.8 GB | 6.4 GB | 25.6 GB | 102 GB |
| 70B | 80 | 8192 | 2.5 GB | 20 GB | 80 GB | 320 GB (单卡放不下) |

**结论**：长 context 推理显存爆炸 → 催生 PagedAttention（vLLM）

---

## ⚙️ 三大优化方向

1. **量化**：KV 缓存从 FP16 → INT8/INT4（省 2-4x 显存）
2. **共享**：MQA / GQA / MLA 让多个 Q 头共享 1 份 KV（省 4-20x，详见下文专章）
3. **分页**：PagedAttention 借鉴 OS 虚拟内存（碎片 < 4%）

---

## 📊 推理复杂度分析：KV Cache 为什么能降低复杂度

### Self-Attention 的 O(n²) 瓶颈

标准 Self-Attention 中，每生成 1 个新 token，需重新计算所有前序 token 的 Q、K、V：

```text
无 KV Cache 的生成流程：
  token_1: 计算 Q1,K1,V1 → Attention(Q1,K1,V1) → 输出 token_2
  token_2: 计算 Q1,K1,V1,Q2,K2,V2 → Attention([Q1,Q2],[K1,K2],[V1,V2]) → 输出 token_3
  token_3: 计算 Q1,K1,V1,Q2,K2,V2,Q3,K3,V3 → Attention([Q1,Q2,Q3],...) → ...
  ...
  第 i 步：Attention 矩阵大小 i×i → O(i²)
  生成 n 个 token：Σ(i=1 to n) O(i²) = O(n³)
```

**核心瓶颈**：每步重复计算已存在 token 的 K、V。

**数值直觉**：生成 1024 个 token 时：
- 无缓存：Σ(i=1 to 1024) i² ≈ 3.59 亿次点积运算
- 有缓存：Σ(i=1 to 1024) i ≈ 52.4 万次点积运算
- **差 685x** —— 不是 10-20% 优化，是数量级差异

### KV Cache 的 O(n) 优化

核心思想：**缓存已计算的 K、V，新 token 只算自己的 K、V，与缓存拼接**。

```text
有 KV Cache 的生成流程：
  token_1: 计算 Q1,K1,V1 → 缓存 K1,V1 → Attention → 输出 token_2
  token_2: 只算 Q2,K2,V2 → 拼接缓存 [K1;K2],[V1;V2] → Attention → 输出 token_3
  token_3: 只算 Q3,K3,V3 → 拼接缓存 [K1;K2;K3],[V1;V2;V3] → Attention → ...
  ...
  第 i 步：1 个 Q × i 个 K → O(i) 向量点积
  生成 n 个 token：Σ(i=1 to n) O(i) = O(n²)
```

**从 O(n³) 降到 O(n²)** —— 是**复杂度级别**的降低，不是常数优化。

**代价**：显存占用从 O(1) 涨到 **O(n × d_model × 2)**（每 token 存 K + V 两份）。

### 显存 vs 计算的 Trade-off 可视化

```text
计算复杂度：     O(n³) ──────────────▶ O(n²)  ████████████████ → ████████  (降 2 级)
显存占用：       O(1)  ──────────────▶ O(n)   █ → ████████████████████████ (涨 n 倍)
```

### 复杂度对比表

| 方案 | 计算复杂度 | 显存占用 | 适用场景 |
|------|-----------|---------|---------|
| 无缓存（naive） | O(n³) | O(1) | 理论分析 |
| KV Cache | O(n²) | O(n × d × 2) | 工业标准 |
| KV Cache + MQA | O(n²) | O(n × d × 2 / n_heads) | 显存敏感 |
| KV Cache + GQA | O(n²) | O(n × d × 2 / n_groups) | 精度+显存平衡 |
| KV Cache + MLA | O(n²) | O(n × d_r × 2) | 长上下文 |

> **d** = head_dim × num_heads，**d_r** = MLA 低秩压缩维度（d_r << d）

### KV Cache 的生命周期

```text
Prefill 阶段（处理 prompt）：
  输入: "你好，请介绍一下自己"
  计算所有 token 的 K,V → 一次性写入 KV Cache → O(prompt_len²)

Decoding 阶段（逐 token 生成）：
  每步: 新 token 的 K,V → 追加到 KV Cache → 与历史拼接做 Attention → O(seq_len)
  seq_len 从 prompt_len 逐步增长到 prompt_len + max_new_tokens
```

---

## 🔬 MQA / GQA / MLA 深度对比

### MHA（Multi-Head Attention）—— 基线

- **KV 份数**：每个 Q 头独占 1 份 KV → n_heads 份 KV
- **KV 显存**：100%（基准）
- **精度**：最高（每头独立学习）
- **代表模型**：GPT-2、LLaMA-1、BERT

### MQA（Multi-Query Attention）

- **核心**：所有 n_heads 个 Q 头共享 **1 份** KV → KV 显存降 n_heads 倍
- **解决的问题**：显存瓶颈（大 batch / 长上下文）
- **代价**：精度明显下降（所有头共享同一份 KV，表达能力受限）
- **代表模型**：Falcon、PaLM、StarCoder
- **公式**：Q: [n_heads, d_head] / K,V: [1, d_head]
- **KV 显存**：~1/n_heads（32 头 → 省 32x）

### GQA（Grouped-Query Attention）

- **核心**：n_heads 个 Q 头分成 n_groups 组，每组共享 1 份 KV → KV 显存降 n_heads/n_groups 倍
- **解决的问题**：MQA 精度下降太多 → GQA 在显存和精度之间找平衡
- **代价**：比 MQA 精度高，比 MHA 显存省
- **代表模型**：LLaMA-2/3、Mistral、Qwen-2
- **公式**：Q: [n_heads, d_head] / K,V: [n_groups, d_head]（n_groups 通常 = 8）
- **KV 显存**：~n_groups/n_heads（32 头 / 8 组 → 省 4x）
- **工业地位**：2025-2026 年主流方案

### MLA（Multi-head Latent Attention）

- **核心**：K/V 通过低秩投影压缩到 d_r 维（d_r << d_model）→ KV 显存降 d_model/d_r 倍
- **解决的问题**：GQA 仍不够省 → MLA 用低秩压缩进一步压
- **代价**：需额外训练低秩投影矩阵；推理时需解压（计算略增）
- **代表模型**：DeepSeek-V2/V3
- **公式**：K,V 先投影到 d_r 维缓存，推理时解压恢复
- **KV 显存**：~d_r/d_model（DeepSeek-V2 中 d_r=64, d_model=512 → 省 ~8x，叠加分组后总省 10-20x）
- **对比**：GQA 省 4-8x / MLA 省 10-20x（但需训练预算）

### 4 种方案速查表

| 方案 | Q 头数 | KV 份数 | KV 显存（相对） | 精度 | 训练成本 | 代表模型 |
|------|-------|---------|---------------|------|---------|---------|
| MHA | 32 | 32 | 100% | 最高 | 标准 | GPT-2, LLaMA-1 |
| MQA | 32 | 1 | 3% | 明显下降 | 标准 | Falcon, PaLM |
| GQA | 32 | 8 | 25% | 接近 MHA | 标准 | LLaMA-2/3, Qwen-2 |
| MLA | 32 | 低秩压缩 | 5-10% | 接近 MHA | 需训练 | DeepSeek-V2/V3 |

### 选型决策树

```text
显存够吗？
├─ 够 → MHA（标准多头，精度最高）
├─ 不够 → 能接受精度下降吗？
│   ├─ 能 → MQA（最省显存，精度下降最多）
│   └─ 不能 → 有训练预算吗？
│       ├─ 有 → MLA（最省显存 + 精度接近 MHA）
│       └─ 没有 → GQA（省 4-8x + 精度接近 MHA，工业首选）
```

### GQA 与 MQA 的关系

GQA 是 MQA 的**泛化**：当 n_groups = 1 时，GQA 退化为 MQA。工业上 n_groups = 8 是 sweet spot —— LLaMA-2 实测精度下降 < 0.5%，但 KV 显存省 4x。

### MLA 与 GQA 的本质区别

| 维度 | GQA | MLA |
|------|-----|-----|
| 原理 | 分组共享（无需训练） | 低秩投影压缩（需训练） |
| 推理 | 直接读取缓存 | 需解压恢复 |
| 训练 | 0 成本 | 需训练低秩矩阵 |
| 省显存 | 4-8x | 10-20x |
| 适用 | 已有模型直接换 | 从头训练新模型 |

---

## 🔗 兄弟章节

- **L1 同级**：[Transformer 架构](../../../08.ai-foundations/03-transformer/transformer-architecture.md) / [注意力机制](../../../08.ai-foundations/03-transformer/attention-mechanism.md) / [Flash Attention](../flash-attention/README.md)
- **本专题**：[PagedAttention](../paged-attention/README.md) / [推理性能指标](../inference-metrics/README.md) / [推理框架对比](../inference-frameworks/README.md)
- **咬文嚼字**：KV Cache + MQA/GQA/MLA 面试题（⚠️ 待 Phase 1+ 迁入；占位 `../../../../12.interview/11.ai/kv-cache-mqa-gqa-mla/`）

---

## ⚠️ 5 大反直觉

| 误区 | 真相 |
|------|------|
| ❌ KV Cache 越大越好 | ✅ 受显存约束，70B + 128K 需 4 张 A100 |
| ❌ 训练时也需要 KV Cache | ✅ 训练是并行算全部，推理是逐 token |
| ❌ KV Cache 只是省计算 | ✅ 是**复杂度级别**降低：O(n³) → O(n²) |
| ❌ MQA = GQA | ✅ MQA 是所有头共享 1 份 KV，GQA 是分组共享（n_groups = 1 时退化为 MQA） |
| ❌ MLA 是 GQA 的升级版 | ✅ MLA 用低秩压缩需训练，GQA 用分组共享无需训练，选型取决于训练预算 |

---

## 💡 工业实践建议

### 1. KV Cache 量化
- **INT8 量化**：显存省 2x，精度损失 < 0.3%（推荐优先尝试）
- **INT4 量化**：显存省 4x，精度损失 ~1-2%（长上下文场景可用）
- **FP8 量化**：Hopper 架构原生支持，显存省 2x 几乎无损

### 2. KV Cache 淘汰策略
- **LRU**：淘汰最久未使用的 token（简单，适合对话场景）
- **滑动窗口**：只保留最近 N 个 token（适合流式推理）
- **重要性评分**：基于 Attention 权重淘汰低分 token（精度最高但计算开销大）
- **混合策略**：LRU + 滑动窗口（工业常用）

### 3. KV Offloading
- 当 GPU 显存不足时，将部分 KV Cache 迁移到 CPU 内存
- 代价：CPU-GPU 带宽有限（PCIe 4.0 ~ 64 GB/s），会引入延迟
- 适用：长上下文推理但并发不高（非实时场景）

---

## 📚 参考来源

- FlashAttention-2: [Tri Dao, 2023](https://arxiv.org/abs/2307.08691)
- GQA: [Ainslie et al., 2023](https://arxiv.org/abs/2305.13245) "GQA: Training Generalized Multi-Query Transformer Models"
- MLA: [DeepSeek-V2 Technical Report, 2024](https://arxiv.org/abs/2405.04434)
- PagedAttention: [Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- vLLM: [GitHub](https://github.com/vllm-project/vllm)

← [返回 L2 技术栈](../README.md)
