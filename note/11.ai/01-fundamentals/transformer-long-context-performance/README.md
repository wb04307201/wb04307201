<!--
module:
  parent: ai/01-fundamentals
  slug: ai/01-fundamentals/transformer-long-context-performance
  type: article
  category: 主模块子文章
  summary: Transformer 处理超长上下文变慢的根因分析（Attention O(n²) + KV Cache 内存）+ 6 大优化方案对比 + 实际案例
-->

# Transformer 超长上下文性能瓶颈：根因分析 + 6 大优化方案

← [返回: L1 基础概念](../README.md)

> **一句话定位**：Transformer 处理超长上下文变慢的根因是 **Self-Attention 的 O(n²) 时间/空间复杂度 + KV Cache 线性膨胀**，优化方案包括 Flash Attention / Sparse Attention / Linear Attention / MQA / GQA / Ring Attention。本文系统分析根因 + 对比方案 + 给出选型指南。

---

## 0. 问题背景

### 典型场景

```text
场景：用 Claude / GPT-4 处理 128K token 的代码库
预期：几秒内返回结果
实际：等待 30 秒以上，甚至 OOM

问题：为什么上下文越长，推理越慢？
```

### 性能数据（LLaMA-2 70B，A100 80GB）

| 上下文长度 | 推理延迟 | 显存占用 | 是否可行 |
|-----------|---------|---------|---------|
| 4K | ~200 ms | ~140 GB | ✅ |
| 32K | ~1.5 s | ~160 GB | ✅ |
| 128K | ~10 s | ~320 GB | ⚠️ 多卡 |
| 1M | ~80 s | ~2 TB | ❌ OOM |

**核心问题**：上下文长度翻倍 → 延迟翻 4 倍 → 显存翻 2-4 倍。为什么？

---

## 1. 根因 1：Self-Attention 的 O(n²) 复杂度

### 1.1 标准 Attention 计算过程

```python
# Transformer 的 Self-Attention 计算
def self_attention(Q, K, V):
    # Q, K, V 形状：[batch, heads, seq_len, d_k]
    # seq_len = 上下文长度 n

    S = Q @ K.transpose(-2, -1)   # Step 1: [n, d_k] @ [d_k, n] = [n, n]
    S = S / sqrt(d_k)              # Step 2: 缩放
    P = softmax(S, dim=-1)         # Step 3: [n, n] 逐行 softmax
    O = P @ V                      # Step 4: [n, n] @ [n, d_k] = [n, d_k]
    return O
```

### 1.2 复杂度分析

| 步骤 | 计算 | 时间复杂度 | 空间复杂度 |
|------|------|-----------|-----------|
| Step 1: Q × K^T | n × d_k × n | O(n² · d_k) | O(n²)  ← 瓶颈 |
| Step 3: softmax | n × n | O(n²) | O(n²)  ← 瓶颈 |
| Step 4: P × V | n × n × d_k | O(n² · d_k) | O(n²)  ← 瓶颈 |
| **总计** | | **O(n² · d)** | **O(n²)** |

### 1.3 为什么 O(n²) 是瓶颈？

```text
上下文长度 n 与计算量关系：

n = 4K    → n² = 16M     ← 基线
n = 32K   → n² = 1B      ← 64x
n = 128K  → n² = 16B     ← 1024x
n = 1M    → n² = 1T      ← 64000x

计算量随上下文平方增长！
```

### 1.4 直觉理解

**为什么每对 token 都要计算？**

```text
Self-Attention 的核心：每个 token 需要"看"所有其他 token

4 个 token：4 × 4 = 16 次计算
100 个 token：100 × 100 = 10,000 次计算
128K 个 token：128,000 × 128,000 = 16,384,000,000 次计算

→ 每个 token 需要与所有其他 token 计算相关性
→ 这是 Transformer "全局感知" 的代价
```

### 1.5 显存占用估算

```text
Attention 矩阵显存占用：

公式：n² × num_heads × 2 bytes (FP16)

n = 4K, heads = 80 (LLaMA-2 70B):
  4096² × 80 × 2 = 2.6 GB

n = 128K, heads = 80:
  131072² × 80 × 2 = 2,748 GB  ← 单卡不可能

n = 1M, heads = 80:
  1048576² × 80 × 2 = 175,921 GB  ← 完全不可能
```

---

## 2. 根因 2：KV Cache 线性膨胀

### 2.1 什么是 KV Cache？

**自回归生成的特性**：每次生成一个新 token，都需要重新计算之前所有 token 的 K、V。

```text
不使用 KV Cache：
生成第 1 个 token：计算 1 次 Attention
生成第 2 个 token：计算 2 次 Attention（token 1 + 2）
生成第 3 个 token：计算 3 次 Attention（token 1 + 2 + 3）
...
生成第 n 个 token：计算 n 次 Attention
总计：1 + 2 + 3 + ... + n = O(n²) 次计算

使用 KV Cache：
生成第 1 个 token：计算 K₁, V₁，缓存
生成第 2 个 token：计算 K₂, V₂，用缓存的 K₁, V₁ + 新的 K₂, V₂
生成第 3 个 token：计算 K₃, V₃，用缓存的 K₁₂, V₁₂ + 新的 K₃, V₃
...
每次只需要计算 1 次新 token 的 K、V
总计：O(n) 次计算
```

### 2.2 KV Cache 的内存占用

```text
KV Cache 显存占用公式：

KV Cache = 2 × num_layers × num_heads × d_k × seq_len × batch_size × 2 bytes (FP16)

LLaMA-2 70B 参数：
- num_layers = 80
- num_heads = 80（GQA = 8 KV heads）
- d_k = 128
- seq_len = 上下文长度
- batch_size = 1

seq_len = 4K:
  2 × 80 × 8 × 128 × 4096 × 1 × 2 = 2.6 GB

seq_len = 128K:
  2 × 80 × 8 × 128 × 131072 × 1 × 2 = 85.9 GB  ← 超出单卡

seq_len = 1M:
  2 × 80 × 8 × 128 × 1048576 × 1 × 2 = 687 GB  ← 需要多卡
```

### 2.3 KV Cache 为什么是瓶颈？

```text
问题 1：显存占用随上下文线性增长
  → 128K 上下文需要 ~86 GB（仅 KV Cache）
  → 模型本身 ~140 GB → 总共 ~226 GB → 需要 3× A100

问题 2：KV Cache 读写带宽瓶颈
  → 每次生成 token 都需要读取所有历史的 K、V
  → 128K 上下文：每次读取 ~86 GB
  → A100 HBM 带宽 ~2 TB/s → 读取需要 ~43 ms/token

问题 3：Prefill 阶段的计算瓶颈
  → 首次处理 prompt 时需要计算所有 token 的 K、V
  → 128K prompt：计算 128K 个 token 的 K、V → ~10 秒
```

---

## 3. 6 大优化方案对比

### 3.1 方案概览

| 方案 | 核心思路 | 时间复杂度 | 空间复杂度 | 适用场景 |
|------|---------|-----------|-----------|---------|
| **Flash Attention** | 分块计算 + IO 感知 | O(n²) | O(n) | 通用（推荐） |
| **Sparse Attention** | 稀疏化注意力矩阵 | O(n · √n) | O(n · √n) | 长文档 |
| **Linear Attention** | 核近似降复杂度 | O(n) | O(n) | 超长序列 |
| **MQA** | 多查询共享 KV | O(n²) | O(n/H) | 推理加速 |
| **GQA** | 分组查询共享 KV | O(n²) | O(n/G) | 平衡方案 |
| **Ring Attention** | 分布式分块计算 | O(n²/P) | O(n/P) | 多卡分布式 |

### 3.2 Flash Attention（推荐）

**核心思想**：分块计算 + 不写回 HBM（高带宽内存），只在 SRAM（片上缓存）中计算。

```text
标准 Attention：
1. Q × K^T → 写入 HBM（O(n²) 显存）
2. softmax → 从 HBM 读，写入 HBM
3. P × V → 从 HBM 读，写入 HBM
→ 3 次 HBM 读写，O(n²) 显存

Flash Attention：
1. 把 Q/K/V 分成 16×16 的小块
2. 在 SRAM（片上缓存，极快）中逐块计算
3. 用 Online Softmax 累积结果
4. 只在最后写一次 O 到 HBM
→ 1 次 HBM 读写，O(n) 显存
```

**性能提升**：

| 上下文长度 | 标准 Attention | Flash Attention | 加速比 |
|-----------|---------------|----------------|--------|
| 2K | 1.0x | 2.5x | 2.5x |
| 8K | 1.0x | 5.0x | 5.0x |
| 32K | OOM | 10.0x | ∞ |
| 128K | OOM | 20.0x | ∞ |

**局限性**：
- 时间复杂度仍是 O(n²)（只是常数优化）
- 128K 以上仍然慢（只是不会 OOM）

> 详细原理见 [Flash Attention](./flash-attention/)

### 3.3 Sparse Attention（稀疏注意力）

**核心思想**：不是每个 token 都需要看所有其他 token，只关注"局部 + 全局锚点"。

```text
标准 Attention（密集）：
每个 token 看所有其他 token → O(n²)

Sparse Attention（稀疏）：
每个 token 只看：
1. 局部窗口（如前后 256 个 token）
2. 全局锚点（如每 128 个 token 一个）
→ O(n · √n) 或 O(n · log n)
```

**典型实现**：

| 模型 | 稀疏模式 | 复杂度 |
|------|---------|--------|
| Longformer | 滑动窗口 + 全局 token | O(n · w) |
| BigBird | 窗口 + 全局 + 随机 | O(n · √n) |
| Sparse Transformer | 固定模式（strided/fixed） | O(n · √n) |

**性能对比**：

```text
n = 128K：
标准 Attention：128K² = 16B 次计算
Longformer（w=256）：128K × 256 = 32M 次计算 → 500x 加速
BigBird：128K × √128K = 45M 次计算 → 350x 加速
```

**适用场景**：
- ✅ 长文档（法律/论文/代码库）
- ✅ 局部依赖为主的任务
- ❌ 需要全局依赖的任务（如长距离推理）

### 3.4 Linear Attention（线性注意力）

**核心思想**：用核函数近似 softmax，将 O(n²) 降为 O(n)。

```text
标准 Attention：
Attention(Q, K, V) = softmax(Q × K^T / √d) × V
                   = O(n²)  ← softmax 需要计算所有 token 对

Linear Attention：
Attention(Q, K, V) = φ(Q) × (φ(K)^T × V)
                   = O(n)   ← 通过结合律改变计算顺序

其中 φ 是核函数（如 ReLU、elu 等）
```

**性能对比**：

| 上下文长度 | 标准 Attention | Linear Attention | 加速比 |
|-----------|---------------|-----------------|--------|
| 4K | 1.0x | 1.0x | 1.0x |
| 32K | 1.0x | 8.0x | 8.0x |
| 128K | OOM | 32.0x | ∞ |
| 1M | OOM | 256.0x | ∞ |

**局限性**：
- 近似误差：核函数无法完美近似 softmax
- 性能下降：长距离依赖能力减弱
- 训练不稳定：某些核函数导致梯度问题

### 3.5 MQA（Multi-Query Attention）

**核心思想**：所有注意力头共享一组 K、V，减少 KV Cache。

```text
标准 MHA（Multi-Head Attention）：
每个头有独立的 Q、K、V
→ num_heads 组 KV Cache

MQA（Multi-Query Attention）：
所有头共享一组 K、V，只有 Q 是多头的
→ 1 组 KV Cache

KV Cache 减少：num_heads 倍
```

**性能对比**（LLaMA-2 70B）：

| 方案 | KV heads | KV Cache（128K） | 推理速度 |
|------|----------|-----------------|---------|
| MHA | 80 | 86 GB | 1.0x |
| MQA | 1 | 1.1 GB | 2.5x |

**局限性**：
- 模型质量下降：单 KV 表达力不足
- 需要从头训练：无法用于现有模型

### 3.6 GQA（Grouped-Query Attention）

**核心思想**：折中方案，多个 Q 头共享一组 KV。

```text
MHA：每个头独立 KV
  heads = 80, kv_heads = 80
  KV Cache = 86 GB

MQA：所有头共享 1 组 KV
  heads = 80, kv_heads = 1
  KV Cache = 1.1 GB

GQA：每 G 个头共享 1 组 KV
  heads = 80, kv_heads = 8（G = 10）
  KV Cache = 8.6 GB  ← 折中
```

**性能对比**：

| 方案 | KV heads | KV Cache（128K） | 模型质量 | 推理速度 |
|------|----------|-----------------|---------|---------|
| MHA | 80 | 86 GB | 最佳 | 1.0x |
| GQA | 8 | 8.6 GB | ~MHA | 2.0x |
| MQA | 1 | 1.1 GB | 较差 | 2.5x |

**工业应用**：
- LLaMA-2 70B：使用 GQA（kv_heads = 8）
- LLaMA-3：使用 GQA（kv_heads = 8）
- Mistral：使用 GQA（kv_heads = 8）

> 详细对比见 [Attention 机制全家桶](./attention-mechanism/)

### 3.7 Ring Attention（分布式）

**核心思想**：将超长上下文分片到多个 GPU，环形传递 KV Cache。

```text
单卡处理 1M 上下文：
  KV Cache = 687 GB  ← 单卡不可能

Ring Attention（8 卡）：
  每张卡处理 128K token
  环形传递 KV Cache
  每张卡 KV Cache = 86 GB  ← 可行
```

**工作原理**：

```text
8 个 GPU 环形连接：

Step 1：每个 GPU 计算自己的 Q × K^T（本地 128K）
Step 2：传递 KV 到下一个 GPU
Step 3：计算 Q × K^T（接收到的 128K）
Step 4：继续传递...
Step 5：累积结果（Online Softmax）

总计算量：8 × 128K × 128K = 1M² / 8  ← 线性加速
```

**性能对比**：

| 方案 | 上下文长度 | 需要的 GPU 数 | 加速比 |
|------|-----------|--------------|--------|
| 单卡 + Flash Attention | 128K | 1 | 1.0x |
| Ring Attention | 1M | 8 | 8.0x |
| Ring Attention | 4M | 32 | 32.0x |

**局限性**：
- 通信开销：GPU 间传递 KV Cache
- 实现复杂：需要分布式训练框架
- 适用场景：超大规模模型 + 超长上下文

---

## 4. 选型指南

### 4.1 决策树

```text
你的场景是什么？
├─ 上下文 ≤ 32K
│   └─ Flash Attention 即可（推荐）
│
├─ 上下文 32K-128K
│   ├─ 需要全局依赖 → Flash Attention + GQA
│   └─ 局部依赖为主 → Sparse Attention
│
├─ 上下文 128K-1M
│   ├─ 单卡 → Linear Attention（质量下降）
│   └─ 多卡 → Ring Attention（推荐）
│
└─ 上下文 > 1M
    └─ Ring Attention + 模型并行
```

### 4.2 方案对比表

| 方案 | 复杂度 | 质量 | 速度 | 实现难度 | 推荐场景 |
|------|--------|------|------|---------|---------|
| Flash Attention | O(n²) | 最佳 | 2-20x | 中 | 通用（首选） |
| Sparse Attention | O(n√n) | 较好 | 100-500x | 中 | 长文档 |
| Linear Attention | O(n) | 较差 | 10-256x | 高 | 超长序列 |
| MQA | O(n²) | 较差 | 2.5x | 低 | 推理加速 |
| GQA | O(n²) | 好 | 2x | 低 | 平衡方案（推荐） |
| Ring Attention | O(n²/P) | 最佳 | P 倍 | 高 | 多卡分布式 |

### 4.3 工业实践

```text
现代 LLM 的标准配置：

LLaMA-3 (8B/70B/405B):
- GQA（kv_heads = 8）
- RoPE 位置编码
- Flash Attention
- 上下文 128K

Claude 3.5:
- GQA（推测）
- Flash Attention
- 上下文 200K

GPT-4:
- 推测使用 GQA / MQA
- Flash Attention
- 上下文 128K

Gemini 1.5:
- MoE + 稀疏注意力
- 上下文 1M-10M
```

---

## 5. 实战案例

### 案例 1：128K 代码库问答

```text
场景：用户上传 128K token 的代码库，问"这个函数的调用链是什么？"
需求：需要全局依赖（跨文件追踪）
方案：
1. 使用 Flash Attention + GQA
2. 上下文 128K → KV Cache ~8.6 GB（GQA）
3. 推理延迟 ~10 秒（A100）
4. 质量：最佳（全局依赖）
```

### 案例 2：1M 法律文档分析

```text
场景：用户上传 1M token 的法律文档，问"第 50 页和第 500 页的矛盾点"
需求：局部 + 全局依赖
方案：
1. 使用 Sparse Attention（局部窗口 + 全局锚点）
2. 或 Ring Attention（8 卡分布式）
3. 推理延迟 ~30 秒
4. 质量：较好
```

### 案例 3：实时对话（长会话）

```text
场景：100 轮对话，每轮 1K token → 总计 100K token
需求：低延迟 + 实时响应
方案：
1. 使用 GQA（减少 KV Cache）
2. Flash Attention（加速推理）
3. 或 Sliding Window（只保留最近 32K）
4. 推理延迟 ~2 秒/token
```

---

## 6. 一句话速查

```text
"Transformer 处理超长上下文变慢的根因：
1. Self-Attention 的 O(n²) 复杂度（每个 token 看所有其他 token）
2. KV Cache 线性膨胀（显存随上下文线性增长）

6 大优化方案：
1. Flash Attention：分块计算 + IO 感知（推荐，通用）
2. Sparse Attention：稀疏化注意力矩阵（长文档）
3. Linear Attention：核近似降复杂度（超长序列）
4. MQA：多查询共享 KV（推理加速）
5. GQA：分组查询共享 KV（平衡方案，推荐）
6. Ring Attention：分布式分块计算（多卡分布式）

选型指南：
- ≤ 32K → Flash Attention
- 32K-128K → Flash Attention + GQA
- 128K-1M → Ring Attention
- > 1M → Ring Attention + 模型并行"
```

---

## 7. 交叉引用

- **同模块兄弟**：
  - [Transformer 架构核心](./transformer/) — Self-Attention + QKV + Multi-Head
  - [Attention 机制全家桶](./attention-mechanism/) — MHA / MQA / GQA / Sparse / Linear
  - [Flash Attention](./flash-attention/) — 分块计算 + IO 感知详解
  - [RoPE 位置编码](./rope-position-encoding/) — 长上下文位置编码

- **相关章节**：
  - [Transformer 面试题](../../../13.split-hairs/11.ai/transformer/) — 架构基础面试拷问
  - [Agent 长上下文策略](../../../13.split-hairs/11.ai/long-context-agent-strategy/) — Agent 层面的长上下文处理
  - [Transformer 长上下文性能面试题](../../../13.split-hairs/11.ai/transformer-long-context-performance/) — 本主题的面试版

---

← [返回: L1 基础概念](../README.md) · [返回: 11.ai](../../README.md)
