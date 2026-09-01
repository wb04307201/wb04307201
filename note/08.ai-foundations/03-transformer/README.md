<!--module:
  parent: 08.ai-foundations
  slug: 08.ai-foundations/03-transformer
  type: index-only
  category: AI 基础索引
  summary: Transformer 架构——注意力机制、位置编码、Self-Attention / Multi-Head / KV Cache / MQA-GQA-MLA / FlashAttention 核心组件解析。
  depth: ⭐⭐⭐⭐⭐
-->

# 03. Transformer

## 📍 一句话定位

> 现代 LLM 的基石——从 2017 年 Google "Attention is All You Need" 出发，掌握 Self-Attention、Multi-Head、位置编码（RoPE / ALiBi）与推理优化（KV Cache / MQA-GQA / FlashAttention），理解所有 GPT / BERT / LLaMA / Claude 的底层架构。

## 🎯 子模块简介

`03-transformer/` 聚焦**Transformer 架构的四大核心主题**：

- **注意力机制（Attention Mechanism）**：Self-Attention / Cross-Attention / Causal-Attention / Multi-Head / Sparse / Linear / MQA / GQA ——7 大变体的差异与工程价值。
- **位置编码（Positional Encoding）**：Sinusoidal（原始 Transformer）→ Learned（BERT）→ RoPE（LLaMA）→ ALiBi（MPT）——为什么 Transformer 需要位置信息。
- **推理优化（Inference Optimization）**：KV Cache（避免重复计算）/ MQA-GQA-MLA（KV 压缩）/ FlashAttention（IO 优化）——让 LLM 推理从"能跑"到"能商用"。
- **架构组件**：Embedding / LayerNorm / FFN / 残差连接 / MoE（Mixture of Experts）——Transformer 的模块化拼图。

本节是 04-llm / 05-tokenization-embedding 的前置——所有 LLM 行为都源于这些架构选择。

---

## 🧠 核心原理：Self-Attention 与三大数学骨架

### 1. Scaled Dot-Product Attention（原始定义）

给定 query / key / value 矩阵 $\mathbf{Q}, \mathbf{K}, \mathbf{V} \in \mathbb{R}^{n \times d_k}$，注意力输出为：

$$
\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\!\left(\frac{\mathbf{Q} \mathbf{K}^\top}{\sqrt{d_k}}\right) \mathbf{V}
$$

**缩放因子 $\sqrt{d_k}$** 是关键：当 $d_k$ 大时，$\mathbf{Q}\mathbf{K}^\top$ 的方差会随 $d_k$ 增长，softmax 会进入饱和区（梯度消失）；除以 $\sqrt{d_k}$ 让方差归一化。**这是一个不起眼但至关重要的工程 trick**。

### 2. Multi-Head Attention（MHA）

把 $d_{\text{model}}$ 维特征切成 $h$ 个 head，每个 head 独立做注意力，最后 concat：

$$
\text{MHA}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{Concat}(\text{head}_1, ..., \text{head}_h) \mathbf{W}^O, \quad \text{head}_i = \text{Attention}(\mathbf{Q}\mathbf{W}_i^Q, \mathbf{K}\mathbf{W}_i^K, \mathbf{V}\mathbf{W}_i^V)
$$

直觉上**每个 head 学习不同的"关系子空间"**——语法、语义、指代、长距离依赖分别由不同 head 捕获。

### 3. 因果掩码（Causal Mask）——GPT 系列核心

自回归生成时，第 $i$ 个 token 不能看到第 $i+1$ 之后的 token。在注意力分数矩阵上三角填 $-\infty$：

$$
M_{ij} = \begin{cases} 0 & j \le i \\ -\infty & j > i \end{cases}, \quad \text{scores} = \frac{\mathbf{Q}\mathbf{K}^\top}{\sqrt{d_k}} + M
$$

### 4. RoPE 旋转位置编码（LLaMA / Qwen / DeepSeek 标准）

把位置信息编码为复数平面上的旋转：

$$
\mathbf{q}_m = R(m\theta_l)\mathbf{q}, \quad \text{where } R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}
$$

**优势**：相对位置天然满足 $\langle \mathbf{q}_m, \mathbf{k}_n \rangle = \langle R((m-n)\theta)\mathbf{q}_m, \mathbf{k}_n \rangle$，**长度外推性极好**——这是 LLaMA 选用 RoPE 而非 Learned PE 的根本原因。

---

## 📜 演进史：8 年架构演变时间线

| 时期 | 关键论文 / 模型 | 架构创新 |
|------|----------------|----------|
| **2017.06** | "Attention is All You Need" (Vaswani et al.) | Transformer 原始论文，提出 Sinusoidal PE + MHA |
| **2018.06** | GPT-1 (OpenAI) | Decoder-only + Causal Mask → 生成范式 |
| **2018.10** | BERT (Google) | Encoder-only + Masked LM → 理解范式 |
| **2019-2020** | GPT-2 / GPT-3 | 规模定律（Scaling Laws）首次系统化 |
| **2020** | T5 (Google) | Encoder-Decoder 统一框架 |
| **2021** | Switch Transformer (Google) | MoE 进入万亿参数 |
| **2022** | FlashAttention (Tri Dao) | IO 感知 attention，HBM 访问减少 9× |
| **2022** | ALiBi (MPT) | 线性偏置代替位置编码，外推性强 |
| **2023.02** | LLaMA-1 (Meta) | RoPE + Pre-Norm + SwiGLU，成为开源标杆 |
| **2023.07** | FlashAttention-2 | 减少非矩阵乘法 FLOPs，吞吐再翻倍 |
| **2023.07** | MQA (Mistral) → GQA (LLaMA-2) | KV 压缩，显存 -50% |
| **2024** | MLA (DeepSeek-V2) | 多头潜在注意力，KV 压缩到极致 |
| **2024-2025** | FlashAttention-3 / 4 | Hopper / Blackwell GPU 上的 WGMMA 优化 |

**设计哲学反思**：

- "注意力机制能不能完全替代 RNN/LSTM？"——**Yes**，因为注意力是 $O(n^2)$ 全局访问 + 可并行，RNN 是 $O(n)$ 顺序依赖（2017 已解决）
- "位置编码为什么需要？"——因为注意力是**置换不变**（permutation invariant）的，必须额外注入顺序信息
- "为什么 RoPE 胜出？"——**相对位置天然 + 长度外推 + 数学优雅**（复数几何）
- "为什么 KV Cache 是推理优化的第一性原理？"——因为生成是自回归的，**每一步都在重复计算历史 token 的 K/V**

---

## 🏛️ 三大实战案例

### 案例 1：LLaMA-3（405B）架构选型（Meta, 2024）

- **核心组件**：RoPE + GQA（8 KV head / 128 attention head）+ Pre-RMSNorm + SwiGLU
- **推理优化**：KV Cache 量化（INT4）+ GQA 让 405B 模型单卡 24GB 可装 KV
- **意义**：**RoPE + GQA + RMSNorm + SwiGLU 已成为开源 LLM 的事实标准**

### 案例 2：DeepSeek-V2 / V3——MLA（多头潜在注意力）

- **痛点**：传统 MHA 的 KV Cache 显存爆炸（405B 模型 KV 占 ~120GB）
- **MLA 方案**：把 KV 压缩到**低秩潜在向量** $c_t = W^K \text{RMSNorm}(W^{DK} h_t)$，推理时只存 $c_t$ 不存原始 K/V
- **收益**：DeepSeek-V2 236B 模型 KV 显存仅为 LLaMA-3 70B 的 **1/10**
- **论文**：DeepSeek-AI, *Multi-Head Latent Attention*, 2024

### 案例 3：FlashAttention-3（2024）——Hopper GPU 上的极优化

- **传统 attention 的瓶颈**：HBM 带宽（不是 FLOPs），每次 attention 读写 $O(n^d)$ 内存
- **核心 trick**：把 attention 计算**融合到 SRAM**，避免 HBM 往返
- **Hopper 增强**：利用 WGMMA 指令（Hopper 独有）+ 异步 pipeline
- **收益**：H100 上 attention 速度 **4× vs FlashAttention-2**；BF16 精度下等价
- **意义**：**没有 FlashAttention 就没有 100k+ 上下文窗口**——它是长上下文 LLM 的物理基础

---

## 💻 代码示例：PyTorch 手写 Causal Self-Attention

```python
import torch
import torch.nn.functional as F

def causal_self_attention(Q, K, V, mask=None):
    """
    Q, K, V: (batch, n_heads, seq_len, d_k)
    mask:    (seq_len, seq_len) 上三角 -inf 掩码
    """
    d_k = Q.size(-1)
    # 1. 缩放点积 + 因果掩码
    scores = (Q @ K.transpose(-2, -1)) / (d_k ** 0.5)  # (B, H, N, N)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # 2. softmax（沿最后一维）
    attn = F.softmax(scores, dim=-1)  # (B, H, N, N)

    # 3. 加权求和
    out = attn @ V  # (B, H, N, d_k)
    return out, attn


# 构造因果掩码（n x n，上三角为 0）
def causal_mask(n):
    return torch.tril(torch.ones(n, n))  # 下三角为 1


# 实战：4 头、64 维、序列长 128
B, H, N, D = 2, 4, 128, 64
Q = torch.randn(B, H, N, D)
K = torch.randn(B, H, N, D)
V = torch.randn(B, H, N, D)
mask = causal_mask(N)

out, attn = causal_self_attention(Q, K, V, mask)
print(f"输出 shape: {out.shape}")  # (2, 4, 128, 64)
```

---

## ⚠️ 常见误区 / 反直觉点（3+）

1. **"注意力是 $O(n^2)$，所以 Transformer 不能处理长序列"**——错。**FlashAttention** 通过 IO 优化把实际显存访问降到 $O(n)$，加上 **Sparse Attention / Linear Attention / Sliding Window**（Mistral），处理百万 token 已是工业常态。
2. **"Multi-Head 比单头强"**——半对。**单头更大维度** vs **多头小维度** 在表达能力上等价，但多头**更易训练**（不同 head 的 loss landscape 平坦），所以工程上胜出。
4. **"KV Cache 只是推理加速，不影响训练"**——错。训练时**也要**算 KV（只是没用 cache），所以长序列训练的**显存瓶颈 = KV + 激活值**——这就是为什么 LLM 训练需要 FSDP / ZeRO-3 来分片。
5. **"位置编码只能用 Sinusoidal"**——错。RoPE / ALiBi / Learned PE / No-PE（NoPE, 2023）**都被验证有效**；关键看是否需要长度外推。
6. **"MQA/GQA 一定会掉精度"**——半对。GQA（Grouped Query Attention）保留分组共享，**精度损失 <0.5%**，但 KV 显存减半——是 2023 年后 LLM 的标配。

---

## 🔗 跨模块反向链

- **同模块相邻**：[02-deep-learning](../02-deep-learning/README.md) — 深度学习框架（PyTorch 是 Transformer 实现的载体）
- **同模块相邻**：[04-llm](../04-llm/README.md) — LLM 基础（Dropout / 训练技巧）
- **AI 工程实战**：[`09.ai-applications/llm-inference/kv-cache`](../../09.ai-applications/llm-inference/kv-cache/) — 推理复杂度与 KV Cache 实战
- **AI 工程实战**：[`09.ai-applications/llm-inference/flash-attention`](../../09.ai-applications/llm-inference/) — FlashAttention 推理优化
- **咬文嚼字**：[`12.interview/11.ai/transformer`](../../12.interview/11.ai/transformer/) — Transformer 面试题
- **兄弟主题**：[`08.ai-foundations/03-transformer/transformer-architecture`](./transformer-architecture.md) — 架构详解 + Self-Attention 代码
- **兄弟主题**：[`08.ai-foundations/03-transformer/attention-mechanism`](./attention-mechanism.md) — 7 大注意力变体对比
- **故事叙事**：[`13.story/`](../../13.story/) — "阿明餐厅"系列以餐饮服务类比 Self-Attention 的"顾客排队"直觉

---

## 🗂️ 文章清单

| 标题 | 路径 | 状态 | 摘要 |
|------|------|------|------|
| 注意力机制 | [attention-mechanism.md](./attention-mechanism.md) | ✅ 已完成（69 行） | 系统梳理 Self / Cross / Multi-Head / Sparse / Linear / MQA / GQA 等注意力变体及其工程价值。 |
| Transformer 架构 | [transformer-architecture.md](./transformer-architecture.md) | ✅ 已完成（212 行） | 架构详解 + Self-Attention 代码：解决 RNN/LSTM 痛点 → 完全基于注意力机制 + 5 个核心 trade-off。 |

> **覆盖说明**：当前 `03-transformer/` 已沉淀 2 篇（attention-mechanism.md / transformer-architecture.md），覆盖注意力机制与架构概览；KV Cache 优化、MQA-GQA-MLA、FlashAttention 是面试高频 + 工业级核心，建议尽快补齐。

## 🔗 关联主题

- **父模块**：[08.ai-foundations](../README.md) — AI 基础层总索引
- **同模块相邻**：[02-deep-learning](../02-deep-learning/README.md) — 深度学习框架与训练范式
- **同模块相邻**：[04-llm](../04-llm/README.md) — LLM 基础（Dropout / 训练技巧）
- **AI 工程实战**：[`09.ai-applications/llm-inference/kv-cache`](../../09.ai-applications/llm-inference/kv-cache/) — 推理复杂度与 KV Cache 实战
- **咬文嚼字**：[`12.interview/11.ai/transformer`](../../12.interview/11.ai/transformer/) — Transformer 面试题

## 📚 学习路径

1. **入门**：阅读 [transformer-architecture.md](./transformer-architecture.md)，理解架构 5 大组件（Embedding / PE / MHA / FFN / Add&Norm）
2. **核心机制**：阅读 [attention-mechanism.md](./attention-mechanism.md)，掌握 7 大注意力变体
3. **位置编码**：补充 Sinusoidal / RoPE / ALiBi 专题，理解为什么 Transformer 需要位置信息
4. **推理优化**：补 KV Cache 优化 + MQA / GQA / MLA 专题，掌握 LLM 推理瓶颈
5. **底层优化**：补 FlashAttention 专题，理解 IO 优化对长上下文的决定性作用
6. **LLM 实战**：跳转 [04-llm](../04-llm/README.md) 看 LLM 预训练与微调

## 📊 本节统计

- **子目录总数**：1 个（03-transformer/）
- **已沉淀文章**：2 篇（attention-mechanism.md / transformer-architecture.md）
- **待补占位**：3 篇（KV Cache 优化 / MQA-GQA-MLA / FlashAttention 深度）
- **总行数**（不含 README）：约 281 行
- **最后更新**：2026-09-01

---

> 📅 2026-09-01 · 咬文嚼字 · Transformer 架构 · ⭐⭐⭐（高频面试 + 实战必会）

---

← [返回 08.ai-foundations](../README.md)