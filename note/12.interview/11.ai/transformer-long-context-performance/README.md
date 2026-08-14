<!--
question:
  id: 11.ai-transformer-long-context-performance
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构性能
  tags: [11.ai, Transformer, 长上下文, O(n²), KV Cache, Flash Attention, Sparse Attention, Linear Attention, MQA, GQA]
-->

# 为什么 Transformer 架构在处理超长上下文时会变慢？

> **一句话定位**：Transformer 处理超长上下文变慢的根因是 **Self-Attention 的 O(n²) 时间/空间复杂度 + KV Cache 线性膨胀**，优化方案包括 Flash Attention / Sparse Attention / Linear Attention / MQA / GQA / Ring Attention。

> **同模块兄弟**：[transformer](../transformer/) 讲架构基础；[long-context-agent-strategy](../long-context-agent-strategy/) 讲 Agent 层面的长上下文策略；本文专注 **Transformer 架构层面的性能瓶颈与优化**。

---

## 🎯 面试高频拷问

```text
Q1：为什么 Transformer 处理超长上下文时会变慢？
Q2：Attention 的 O(n²) 复杂度具体体现在哪里？
Q3：KV Cache 是什么？为什么会导致显存爆炸？
Q4：有哪些优化方案？各自适用什么场景？
```

**回答框架（2 大根因 + 6 大方案 + 选型指南）**：

1. **根因 1**：Self-Attention 的 O(n²) 时间/空间复杂度
2. **根因 2**：KV Cache 线性膨胀（显存随上下文线性增长）
3. **6 大方案**：Flash Attention / Sparse / Linear / MQA / GQA / Ring Attention
4. **选型指南**：按上下文长度选择方案

---

## ⚠️ 根因 1：Self-Attention 的 O(n²) 复杂度

### 计算过程

```python
# Self-Attention 计算
S = Q @ K^T              # [n, d] @ [d, n] = [n, n]  ← O(n²)
P = softmax(S)           # [n, n] 逐行 softmax      ← O(n²)
O = P @ V                # [n, n] @ [n, d] = [n, d]  ← O(n²)
```

### 为什么是 O(n²)？

```text
Self-Attention 的核心：每个 token 需要"看"所有其他 token

4K token：4096 × 4096 = 16M 次计算
32K token：32768 × 32768 = 1B 次计算（64x）
128K token：131072 × 131072 = 16B 次计算（1024x）
1M token：1048576 × 1048576 = 1T 次计算（64000x）

→ 上下文翻倍，计算量翻 4 倍
```

### 显存占用

```text
Attention 矩阵显存 = n² × num_heads × 2 bytes (FP16)

n = 128K, heads = 80 (LLaMA-2 70B):
  131072² × 80 × 2 = 2,748 GB  ← 单卡不可能
```

---

## ⚠️ 根因 2：KV Cache 线性膨胀

### 什么是 KV Cache？

**自回归生成的特性**：每次生成一个新 token，都需要用到之前所有 token 的 K、V。

```text
不使用 KV Cache：
生成第 n 个 token：重新计算前 n-1 个 token 的 K、V → O(n²) 总计算

使用 KV Cache：
生成第 n 个 token：用缓存的 K₁₋ₙ₋₁, V₁₋ₙ₋₁ + 新的 Kₙ, Vₙ → O(n) 总计算
```

### KV Cache 显存占用

```text
KV Cache = 2 × num_layers × num_kv_heads × d_k × seq_len × 2 bytes

LLaMA-2 70B（GQA, kv_heads = 8）：

seq_len = 4K:
  2 × 80 × 8 × 128 × 4096 × 2 = 2.6 GB

seq_len = 128K:
  2 × 80 × 8 × 128 × 131072 × 2 = 85.9 GB  ← 超出单卡

seq_len = 1M:
  2 × 80 × 8 × 128 × 1048576 × 2 = 687 GB  ← 需要多卡
```

**核心问题**：显存随上下文**线性增长**，128K 需要 ~86 GB（仅 KV Cache）。

---

## ✅ 6 大优化方案

### 方案 1：Flash Attention（推荐）

**核心思想**：分块计算 + 不写回 HBM，只在 SRAM 中计算。

```text
标准 Attention：3 次 HBM 读写，O(n²) 显存
Flash Attention：1 次 HBM 读写，O(n) 显存
→ 2-20x 加速，不会 OOM
```

**局限性**：时间复杂度仍是 O(n²)（只是常数优化）

### 方案 2：Sparse Attention（稀疏注意力）

**核心思想**：不是每个 token 都看所有其他 token，只关注"局部 + 全局锚点"。

```text
标准 Attention：每个 token 看所有 token → O(n²)
Sparse Attention：每个 token 看局部窗口 + 全局锚点 → O(n√n)
→ 100-500x 加速
```

**适用场景**：长文档（法律/论文/代码库）

### 方案 3：Linear Attention（线性注意力）

**核心思想**：用核函数近似 softmax，将 O(n²) 降为 O(n)。

```text
标准 Attention：softmax(Q × K^T) × V → O(n²)
Linear Attention：φ(Q) × (φ(K)^T × V) → O(n)
→ 10-256x 加速
```

**局限性**：近似误差，质量下降

### 方案 4：MQA（Multi-Query Attention）

**核心思想**：所有注意力头共享一组 K、V。

```text
MHA：num_heads 组 KV Cache
MQA：1 组 KV Cache
→ KV Cache 减少 num_heads 倍
```

**局限性**：模型质量下降

### 方案 5：GQA（Grouped-Query Attention）

**核心思想**：折中方案，多个 Q 头共享一组 KV。

```text
MHA：80 组 KV → 86 GB
GQA：8 组 KV → 8.6 GB（10x 减少）
MQA：1 组 KV → 1.1 GB
→ GQA 是最佳平衡
```

**工业应用**：LLaMA-2/3、Claude、Mistral 都使用 GQA

### 方案 6：Ring Attention（分布式）

**核心思想**：将超长上下文分片到多个 GPU，环形传递 KV Cache。

```text
单卡处理 1M：KV Cache = 687 GB（不可能）
Ring Attention（8 卡）：每卡 86 GB（可行）
→ P 倍加速（P = GPU 数）
```

**适用场景**：128K-1M 上下文 + 多卡环境

---

## 🧠 选型指南

### 决策树

```text
你的上下文长度？
├─ ≤ 32K → Flash Attention 即可
├─ 32K-128K → Flash Attention + GQA
├─ 128K-1M → Ring Attention（多卡）
└─ > 1M → Ring Attention + 模型并行
```

### 方案对比表

| 方案 | 复杂度 | 质量 | 速度 | 推荐场景 |
|------|--------|------|------|---------|
| Flash Attention | O(n²) | 最佳 | 2-20x | 通用（首选） |
| Sparse Attention | O(n√n) | 较好 | 100-500x | 长文档 |
| Linear Attention | O(n) | 较差 | 10-256x | 超长序列 |
| MQA | O(n²) | 较差 | 2.5x | 推理加速 |
| GQA | O(n²) | 好 | 2x | 平衡方案（推荐） |
| Ring Attention | O(n²/P) | 最佳 | P 倍 | 多卡分布式 |

---

## 💡 30 秒面试话术

> "Transformer 处理超长上下文变慢有 2 大根因：
>
> **第一**：Self-Attention 的 O(n²) 复杂度。每个 token 需要与所有其他 token 计算相关性，上下文翻倍，计算量翻 4 倍。128K 上下文的 Attention 矩阵需要 2.7 TB 显存，单卡不可能。
>
> **第二**：KV Cache 线性膨胀。自回归生成时，每次生成新 token 都需要用到之前所有 token 的 K、V。KV Cache 随上下文线性增长，128K 需要 ~86 GB（仅 KV Cache）。
>
> 优化方案有 6 个：
>
> **Flash Attention**：分块计算 + IO 感知，O(n) 显存，2-20x 加速（推荐，通用）。
>
> **Sparse Attention**：稀疏化注意力矩阵，O(n√n) 复杂度，100-500x 加速（长文档）。
>
> **Linear Attention**：核近似降复杂度，O(n) 复杂度，但质量下降。
>
> **MQA / GQA**：共享 KV Cache，减少显存。GQA 是最佳平衡（LLaMA-2/3 都用）。
>
> **Ring Attention**：分布式分块计算，多卡处理 128K-1M 上下文。
>
> **选型指南**：≤ 32K 用 Flash Attention；32K-128K 用 Flash + GQA；128K-1M 用 Ring Attention。"

---

## 📚 深度阅读

- [主模块深度文章](../transformer-long-context-performance/README.md) — 完整根因分析 + 6 大方案对比 + 选型指南
- [Transformer 架构核心](../../../../08.ai-foundations/04-llm/transformer/) — Self-Attention + QKV + Multi-Head
- [Attention 机制全家桶](../../../../08.ai-foundations/04-llm/attention-mechanism/) — MHA / MQA / GQA / Sparse / Linear
- [Flash Attention](../../../../08.ai-foundations/04-llm/flash-attention/) — 分块计算 + IO 感知详解
- [Agent 长上下文策略](../long-context-agent-strategy/) — Agent 层面的长上下文处理

---

← [返回: 11.ai 咬文嚼字](../README.md)
