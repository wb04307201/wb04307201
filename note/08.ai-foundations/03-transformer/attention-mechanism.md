<!--
module:
  parent: 08.ai-foundations/03-transformer
  slug: 08.ai-foundations/03-transformer/attention-mechanism
  type: article
  category: 主模块子文章
  summary: 注意力机制全家桶（Self/Cross/Multi-Head/Sparse/Linear/MQA/GQA）——数学推导 + 7 大变体 + 工业级 KV Cache 加速 + 6 家公司实战。
  depth: ⭐⭐⭐⭐⭐
  depth: ⭐⭐⭐⭐⭐
-->

# 注意力机制（Attention Mechanism）

> **一句话定位**：注意力机制 = **Q·K^T 算相关性 × V 加权求和**，让模型"聚焦"输入关键部分。本节覆盖 Self/Cross/Multi-Head/Sparse/Linear/MQA/GQA/MLA 全家桶，是理解所有 LLM 架构的钥匙。

> ⬅️ [返回 Transformer 架构](../README.md)

---

## 🎯 学习目标

完成本文后，你能够：

- **数学基础**：用一行公式说清 Attention(Q, K, V) = softmax(Q·K^T / √d) · V，并理解 √d_k 的作用
- **变体谱系**：知道 8 大变体的差异（Self / Cross / Causal / MHA / MQA / GQA / MLA / Sparse / Linear）
- **工程价值**：能解释为什么 GQA / MLA 是 KV Cache 加速的关键
- **复杂度分析**：说清 O(n²) 复杂度为何是 LLM 推理瓶颈，以及 Flash Attention 如何缓解
- **反直觉**：理解 5 大误区（Attention ≠ 看重要部分、Linear Attention 性能权衡等）

---

## 📚 章节清单

| 章节 | 核心内容 | 阅读时长 |
|------|---------|---------|
| **01 Attention 数学基础** | QKV 推导 + 缩放因子 √d_k + 掩码机制 | 25 min |
| **02 Self / Cross / Causal** | 三种 QKV 来源 + Decoder-only 因果掩码 | 20 min |
| **03 Multi-Head Attention** | 多头并行的 4 大优势 + 代码实现 | 20 min |
| **04 MQA / GQA / MLA** | KV Cache 加速的工业级方案 | 30 min |
| **05 Sparse Attention** | Longformer / BigBird 稀疏化 + 滑动窗口 | 20 min |
| **06 Linear Attention** | O(n) 复杂度的探索 + Performer / RWKV | 20 min |
| **07 Flash Attention** | IO-aware 分块 + O(n²) FLOPs / O(n) 显存 | 20 min |
| **08 实战案例与反直觉** | 6 家公司 + 5 大误区 | 15 min |

---

## 一、Attention 数学基础

### 1.1 一行核心公式

$$
\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q} \mathbf{K}^\top}{\sqrt{d_k}}\right) \mathbf{V}
$$

**符号解读**：

- $\mathbf{Q} \in \mathbb{R}^{n \times d_k}$ — Query 矩阵（n 个 token，每个 d_k 维）
- $\mathbf{K} \in \mathbb{R}^{n \times d_k}$ — Key 矩阵
- $\mathbf{V} \in \mathbb{R}^{n \times d_v}$ — Value 矩阵
- $d_k$ — Key 维度（= Q 维度）
- $d_v$ — Value 维度（可与 d_k 异同）
- $\sqrt{d_k}$ — 缩放因子，**防止 softmax 饱和**

### 1.2 直观理解（餐厅比喻）

```text
想象一家餐厅：

- Query（查询）：你想吃什么？（你想获取的信息）
- Key（菜单上的菜名）：菜品的标签
- Value（菜品本身）：实际的内容

1. 计算 Q · K^T → 你对每道菜的"感兴趣程度"
2. softmax 归一化 → 概率分布（必须加起来 = 1）
3. 用概率加权 V → 端给你的菜（重点菜多给、配菜少给）
```

### 1.3 为什么需要缩放因子 √d_k？

**数学推导**：

- 假设 $Q$ 和 $K$ 的每个分量都是**独立同分布**的 $\mathcal{N}(0, 1)$
- 则 $Q \cdot K = \sum_{i=1}^{d_k} Q_i K_i$，均值 0、方差 $d_k$
- 当 $d_k$ 很大（如 128），$Q \cdot K$ 的方差 → 128

**后果**：

- softmax 输入的数值过大 → softmax 接近 one-hot（梯度消失）

**实验**：$d_k = 64$，不缩放 vs 缩放：

| 输入分布 | softmax 输出 |
|---------|-------------|
| 不缩放：$\sigma^2 = 64$，值域 $[-40, 40]$ | one-hot（梯度 ≈ 0）|
| 缩放后：$\sigma^2 = 1$，值域 $[-3, 3]$ | 平滑分布 |

**结论**：**√d_k 把方差归一化到 1**，保证 softmax 工作在梯度友好的区域。

### 1.4 完整实现（PyTorch）

```python
import torch
import torch.nn.functional as F

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q, K: (batch, n_heads, seq_len, d_k)
    V: (batch, n_heads, seq_len, d_v)
    mask: (seq_len, seq_len) — 1 表示 attend，0 表示 mask
    """
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / (d_k ** 0.5)  # (B, H, N, N)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))  # mask 位置设为 -inf

    attn_weights = F.softmax(scores, dim=-1)  # (B, H, N, N)
    output = torch.matmul(attn_weights, V)  # (B, H, N, d_v)

    return output, attn_weights

# 使用示例
batch_size, n_heads, seq_len, d_k = 2, 8, 10, 64
Q = torch.randn(batch_size, n_heads, seq_len, d_k)
K = torch.randn(batch_size, n_heads, seq_len, d_k)
V = torch.randn(batch_size, n_heads, seq_len, d_k)
output, weights = scaled_dot_product_attention(Q, K, V)
print(f"output: {output.shape}")  # (2, 8, 10, 64)
print(f"weights: {weights.shape}")  # (2, 8, 10, 10)
```

### 1.5 掩码机制（Mask）

**两种核心掩码**：

#### 1.5.1 Padding Mask

处理变长序列，`<pad>` token 不参与 attention：

```python
# seq_len = 5, 有效长度 = 3
pad_mask = torch.tensor([1, 1, 1, 0, 0])  # 1=有效, 0=padding
scores = scores.masked_fill(pad_mask == 0, float('-inf'))
```

#### 1.5.2 Causal Mask（因果掩码）

Decoder-only 场景，token i 只能看到 ≤ i 的位置：

```python
seq_len = 5
causal_mask = torch.tril(torch.ones(seq_len, seq_len))
# tensor([[1, 0, 0, 0, 0],
#         [1, 1, 0, 0, 0],
#         [1, 1, 1, 0, 0],
#         [1, 1, 1, 1, 0],
#         [1, 1, 1, 1, 1]])

scores = scores.masked_fill(causal_mask == 0, float('-inf'))
```

**因果掩码示意**：

```text
       t1   t2   t3   t4   t5
t1  [  ✓   ✗   ✗   ✗   ✗  ]
t2  [  ✓   ✓   ✗   ✗   ✗  ]   ← token i 看 ≤ i
t3  [  ✓   ✓   ✓   ✗   ✗  ]
t4  [  ✓   ✓   ✓   ✓   ✗  ]
t5  [  ✓   ✓   ✓   ✓   ✓  ]
```

---

## 二、Self / Cross / Causal Attention

### 2.1 三种 QKV 来源

| 类型 | Q 来源 | K 来源 | V 来源 | 应用场景 |
|------|--------|--------|--------|----------|
| **Self-Attention** | 序列自身 | 序列自身 | 序列自身 | Encoder/Decoder 内部 |
| **Cross-Attention** | 一个序列 | 另一个序列 | 另一个序列 | Encoder→Decoder、CLIP 文本-图像 |
| **Causal Self-Attention** | 序列自身 | 序列自身（但带掩码） | 序列自身 | GPT 等 Decoder-only LLM |

### 2.2 Self-Attention 的"魔法"

**每个 token 都和所有 token（包括自己）计算相关性**：

```python
# 输入：5 个 token，每个 64 维
x = torch.randn(5, 64)  # (seq_len, d_model)

# 三个投影矩阵
W_Q = torch.randn(64, 64)
W_K = torch.randn(64, 64)
W_V = torch.randn(64, 64)

Q = x @ W_Q  # (5, 64)
K = x @ W_K  # (5, 64)
V = x @ W_V  # (5, 64)

# Self-Attention
output = scaled_dot_product_attention(Q, K, V)  # (5, 64)
```

### 2.3 Cross-Attention 实战案例（Encoder-Decoder）

```text
┌──────────────┐                ┌──────────────┐
│   Encoder    │                │   Decoder    │
│              │                │              │
│  "Hello,    │                │  目标: "你好"│
│   how are   │                │              │
│   you?"     │                │              │
└──────┬───────┘                └──────┬───────┘
       │ K, V (5, 64)               │ Q (3, 64)
       │                              │
       └────────────┬─────────────────┘
                    ▼
            Cross-Attention
        Decoder 用 Q 检索 Encoder 的 K, V
```

### 2.4 Causal Self-Attention 的工程意义

**Decoder-only LLM（如 GPT、LLaMA、Claude）只用 Causal Self-Attention**：

- 训练：可并行（整句所有 token 一起算 + 因果掩码）
- 推理：自回归（KV Cache 缓存历史）
- **优势**：架构统一，简化训练和推理

**反直觉点**：**Encoder-Decoder 架构（T5、BART）逐渐式微**，Decoder-only 成为 LLM 主流（GPT、LLaMA、Claude、Qwen、DeepSeek）。

---

## 三、Multi-Head Attention（MHA）

### 3.1 核心思想

将 $d_{\text{model}}$ 维度拆成 $h$ 个头，每个头独立做 Attention：

$$
\text{MultiHead}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) \mathbf{W}^O
$$

其中：

$$
\text{head}_i = \text{Attention}(\mathbf{Q} \mathbf{W}^Q_i, \mathbf{K} \mathbf{W}^K_i, \mathbf{V} \mathbf{W}^V_i)
$$

### 3.2 4 大优势

1. **多子空间并行**：不同 head 学习不同语义关系（句法、指代、长程依赖等）
2. **表达力增强**：$h$ 倍参数空间，捕捉更丰富特征
3. **训练稳定**：梯度分散到多个 head，避免单一 head 主导
4. **可解释性**：可视化 head 注意力分布可解释模型行为

### 3.3 PyTorch 完整实现

```python
import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model=512, n_heads=8):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)

    def forward(self, x, mask=None):
        batch_size = x.size(0)

        # 投影 + 拆头: (B, N, D) → (B, H, N, d_k)
        Q = self.W_Q(x).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_K(x).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_V(x).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)

        # Scaled Dot-Product Attention
        scores = (Q @ K.transpose(-2, -1)) / (self.d_k ** 0.5)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        attn = torch.softmax(scores, dim=-1)
        x = (attn @ V).transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)

        return self.W_O(x)

# 使用
mha = MultiHeadAttention(d_model=512, n_heads=8)
x = torch.randn(2, 10, 512)  # (batch=2, seq=10, d=512)
output = mha(x)
print(output.shape)  # (2, 10, 512)
```

### 3.4 头数选择经验

| 模型 | 层数 | 头数 | head_dim | 备注 |
|------|------|------|----------|------|
| **GPT-2 Small** | 12 | 12 | 64 | 小模型 |
| **GPT-3 175B** | 96 | 96 | 128 | 标准大模型 |
| **LLaMA-2 70B** | 80 | 64 (GQA: 8 KV) | 128 | GQA |
| **LLaMA-3 70B** | 80 | 64 (GQA: 8 KV) | 128 | GQA |
| **Claude 3 Opus** | - | - | 128 | GQA |
| **GPT-4** | - | - | 128 | 推测 |

**经验法则**：`head_dim = 128` 是最优 sweet spot；头数 8-128，再多边际收益递减。

---

## 四、MQA / GQA / MLA — KV Cache 加速的工业级方案

### 4.1 问题：KV Cache 显存爆炸

**推理场景**（自回归生成）：

```text
batch=32, seq_len=4096, n_heads=64, head_dim=128

KV Cache 显存（FP16）：
= 2 (K+V) × 32 × 4096 × 64 × 128 × 2 bytes
= 4.3 GB per request
= 138 GB per 32 requests
```

**瓶颈**：长上下文 + 大 batch → KV Cache 占 GPU 显存大头。

### 4.2 MQA（Multi-Query Attention, 2019）

**核心思想**：**所有 head 共享 1 份 K 和 V**。

```text
MHA:  Q: [h × d_k]  K: [h × d_k]  V: [h × d_v]  ← 64 份 KV
MQA:  Q: [h × d_k]  K: [1 × d_k]  V: [1 × d_v]  ← 1 份 KV
```

**效果**：

- KV Cache 显存：$\frac{1}{h}$（如 h=64 → 1/64）
- 推理速度：+30%
- **代价**：质量下降（因为 KV 不再多样）

### 4.3 GQA（Grouped-Query Attention, 2023）

**核心思想**：**分组共享 KV**——g 个组，每组共享 1 份 KV，Q 仍分为 h 个 head。

```text
h=64, g=8：
- 64 个 Q head 分 8 组
- 每组 8 个 Q head 共享 1 份 K, V
- KV Cache 显存 = 8 份（介于 MHA 和 MQA 之间）
```

**LLaMA-2 70B 配置**：

```python
{
    "hidden_size": 8192,
    "num_attention_heads": 64,
    "num_key_value_heads": 8,  # GQA
    "head_dim": 128
}
# KV Cache 显存节省 8 倍
```

**经验**：g = h/8 是最优（如 64 head → 8 KV groups）。

### 4.4 MLA（Multi-head Latent Attention, DeepSeek-V2）

**核心思想**：**把 KV 压缩到低维潜在空间**——KV Cache 不是存 K、V 本身，而是存"潜在向量"。

**DeepSeek-V2 架构**：

```text
MHA:  KV Cache = h × d_k × d_v × 2 (per token)
MLA:  KV Cache = d_c × 2 (per token)，d_c << h × d_k
```

**DeepSeek-V2 量化数据**：

- 参数量：236B 总 / 21B 激活
- KV Cache 压缩比：$\frac{236B \times 128}{4096 \times 2} = 5.9\%$（5%）
- 实际推理显存：**比 LLaMA-2 70B 少 80%**

### 4.5 三种方案对比

| 方案 | KV Cache 数量 | 质量 | 速度 | 代表 |
|------|--------------|------|------|------|
| **MHA** | h 份 | 最优 | 基准 | GPT-3 / BERT |
| **MQA** | 1 份 | 略降 | +30% | PaLM / StarCoder |
| **GQA** | g 份（h/8）| 接近 MHA | +25% | **LLaMA-2/3 / Mistral / Claude** |
| **MLA** | d_c 份（≈1）| 等价 MHA | +30% | **DeepSeek-V2/V3** |

**反直觉点**：**MLA 用低维潜在表示做到了 MHA 质量 + MQA 速度**，是 2024 年最具创新性的 Attention 改进。

---

## 五、Sparse Attention — Longformer / BigBird

### 5.1 长序列的 O(n²) 困境

**n = 4096**：

- Attention 矩阵：4096 × 4096 = 16M 元素
- 单层 Attention FLOPs：$O(n^2 d) = 4 \times 10^9$
- 显存：$O(n^2) = 64$ MB（FP32，仅 attention 矩阵）

**n = 100K**（如 GPT-4 长上下文）：

- Attention 矩阵：100K × 100K = 10G 元素
- 显存：40 GB（**不可能存下**）

### 5.2 Longformer 的稀疏模式

**三种 attention 模式**：

```text
1. 滑动窗口（Sliding Window）：
   每个 token 只看左右 window 个 token（如 w=512）

2. 全局 attention：
   特定 token（如 [CLS]）看所有 token

3. 膨胀滑动窗口（Dilated Sliding Window）：
   间隔 w 个 token 看一次（类似膨胀卷积）

4. 随机 attention：
   随机选 r 个 token
```

**效果**：

- 复杂度：$O(n \times w)$（w 为窗口大小，远小于 n）
- 质量：接近 dense attention（Longformer 论文 GLUE/WikiHop SOTA）
- **应用**：长文档理解（法律、学术论文）

### 5.3 BigBird（Google, 2020）

**三种稀疏模式叠加**：

1. **全局 token**（如 [CLS]）：看所有 token
2. **局部窗口**：看左右 w 个 token
3. **随机**：每个 token 随机看 r 个 token

**理论保证**：稀疏 + 全局 + 随机 = **图论上的完整图近似**（universal approximation）。

---

## 六、Linear Attention — O(n) 复杂度的探索

### 6.1 核心思想

通过**核函数（kernel）** 分解，绕过 softmax：

$$
\text{softmax}(\mathbf{Q}_i \mathbf{K}^\top) \mathbf{V} = \frac{\phi(\mathbf{Q}_i)^\top \phi(\mathbf{K})}{\sum \phi(\mathbf{K})} \phi(\mathbf{V})
$$

**关键变换**：

$$
\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V})_i = \frac{\sum_{j=1}^{n} \phi(\mathbf{Q}_i)^\top \phi(\mathbf{K}_j) \mathbf{V}_j}{\sum_{j=1}^{n} \phi(\mathbf{Q}_i)^\top \phi(\mathbf{K}_j)}
$$

**复杂度**：

- 标准 Attention：$O(n^2 d)$（attention 矩阵 $n \times n$）
- Linear Attention：$O(n d^2)$（与 n 线性！）

### 6.2 代表工作

| 方法 | 年份 | 复杂度 | 性能 | 应用 |
|------|------|--------|------|------|
| **Performer** | 2020 | O(n) | 略低 | Google |
| **Linear Transformer** | 2020 | O(n) | 低 | 学术 |
| **RWKV** | 2023 | O(n) | 中等 | 开源 |
| **Mamba** | 2023 | O(n) | **接近 Transformer** | 状态空间模型（SSM）|
| **Mamba-2** | 2024 | O(n) | **优于 Transformer** | 大模型训练 |

### 6.3 性能 vs 表达力

| 维度 | Softmax Attention | Linear Attention |
|------|------------------|------------------|
| **复杂度** | $O(n^2)$ | $O(n)$ |
| **表达力** | 高（softmax 是 universal approximator）| 低（核函数有损）|
| **训练稳定** | ✅ 稳定 | ⚠️ 训练难 |
| **推理速度** | 慢 | 快 |
| **2025 主流** | ✅ 主流 | ❌ 仍未主流 |

**反直觉点**：**Linear Attention 理论复杂度低，但实际难以匹敌 Softmax Attention**——因为核函数分解损失了 softmax 的"winner-take-all"特性，2024 仍未成为主流。

---

## 七、Flash Attention（2022, Tri Dao）

### 7.1 核心问题

**GPU 瓶颈不是 FLOPs，而是 IO（高带宽内存 HBM）**。

```text
标准 Attention：
1. 计算 S = Q·K^T → 写 HBM
2. softmax(S) → 写 HBM
3. 计算 O = softmax(S)·V → 写 HBM

每次读写 HBM，IO 量 = O(n²)
```

### 7.2 Flash Attention 的革命

**核心思想**：**分块 softmax + 不写回 HBM**

```text
1. 把 Q, K, V 分成小块（如 64 个 token 一块）
2. 在 SRAM（片上高速缓存）里计算 attention
3. 只把最终输出写回 HBM
```

**效果**：

- 显存：$O(n)$（vs 标准 $O(n^2)$）
- 速度：**2-4x 加速**（H100 上）
- 数学：**等价**（exact attention，不是 approximate）

### 7.3 Flash Attention 演进

| 版本 | 年份 | 关键改进 |
|------|------|---------|
| **v1** | 2022 | 分块 softmax + IO-aware |
| **v2** | 2023 | 更好并行 + causal mask 支持 |
| **v3** | 2024 | H100 异步 + FP8 支持 |
| **v4** | 2025 | 多 GPU + 更长上下文 |

### 7.4 PyTorch 调用

```python
from torch.nn.functional import scaled_dot_product_attention

# PyTorch 2.0+ 自动调用 Flash Attention
output = scaled_dot_product_attention(Q, K, V, is_causal=True)
```

---

## 八、6 大公司实战案例

### 8.1 Google DeepMind — Transformer / AlphaFold / JAX

- **Transformer 2017**：原始 Attention 架构（Vaswani 等 8 人）
- **AlphaFold 2**：用 Attention 建模蛋白质氨基酸对相互作用（Evoformer 模块）
- **JAX + Flash Attention**：研究标配

### 8.2 OpenAI — GPT 系列 / Flash Attention

- **GPT-3 (2020)**：175B 参数，纯 MHA + 96 层
- **Flash Attention 集成**：v2 起 OpenAI 推理集成 Flash Attention，速度 2-3x

### 8.3 Anthropic — Claude 系列（GQA）

- **Claude 3 / 3.5 / 4**：全部使用 GQA
- **长上下文**：200K 上下文 + Flash Attention + Paged KV Cache

### 8.4 DeepSeek — MLA（Multi-head Latent Attention）

- **DeepSeek-V2 (2024)**：236B 总参 / 21B 激活，MLA 创新
- **DeepSeek-V3 (2024)**：MoE + MLA，KV Cache 显存比 MHA 少 93%
- **开源**：DeepSeek-V2/V3 完全开源，MLA 已成为 Attention 研究热点

### 8.5 Qwen（阿里）— GQA + 长上下文

- **Qwen-2.5 72B**：GQA + YaRN 长上下文扩展
- **Qwen3**：原生支持 32K 上下文，128K with YaRN

### 8.6 Mistral AI — Sliding Window Attention + GQA

- **Mistral 7B (2023)**：Sliding Window Attention（4096 窗口）+ GQA
- **关键创新**：**用滑动窗口替代 Dropout 做正则化**（参 [Dropout 实证](../04-llm/dropout-in-llm/single-epoch-and-config-evidence.md)）

---

## 九、5 大反直觉点

### 误区 1：❌ Attention = 让模型"看"重要部分

**真相**：**Attention 算的是 token 间相关性权重**，不是"看"。

- Attention weights 只是相关性指标，不直接等于"重要性"
- 高 attention 不一定意味着"有用"——可能模型在做某种无意义 pattern matching
- **正确理解**：Attention 是"weighted sum"操作

### 误区 2：❌ 头数越多越好

**真相**：**8-128 头已足够**，再多边际收益递减

- GPT-3 用了 96 头，但 LLaMA-2 70B 只用 64 头，效果相当
- 头数太多反而训练不稳定（小 batch 训练）

### 误区 3：❌ Cross Attention 已过时

**真相**：**跨模态（CLIP、语音）仍核心**

- CLIP：文本-图像 Cross Attention
- Whisper：语音-文本 Cross Attention
- Stable Diffusion：文本-图像 Cross Attention

### 误区 4：❌ Linear Attention 能取代 Softmax

**真相**：**性能与表达力难以兼得**，2024 仍未主流

- Mamba 是 SSM 的改进（非纯 Linear Attention），但仍非 LLM 主流
- Linear Attention 训练困难，量化精度差

### 误区 5：❌ Flash Attention 改变了数学

**真相**：**数学等价，只优化 IO**

- Flash Attention 输出与标准 Attention 数值上几乎完全一致（FP32 下完全一致）
- 改进的是显存和速度，**不**是表达力

---

## 十、跨模块反向链（10+）

| 主题 | 链接 |
|------|------|
| **Transformer 架构** | [08.ai-foundations/03-transformer/transformer-architecture](../03-transformer/transformer-architecture.md) |
| **LLM 基础** | [08.ai-foundations/04-llm/llm-basics](../04-llm/llm-basics.md) |
| **Embedding（QKV 投影）** | [08.ai-foundations/05-tokenization-embedding/embedding](../05-tokenization-embedding/embedding.md) |
| **Dropout 实证（Attention 替代正则化）** | [08.ai-foundations/04-llm/dropout-in-llm/single-epoch-and-config-evidence](../04-llm/dropout-in-llm/single-epoch-and-config-evidence.md) |
| **深度学习框架（PyTorch 实现）** | [08.ai-foundations/02-deep-learning/deep-learning-frameworks](../02-deep-learning/deep-learning-frameworks.md) |
| **KV Cache 加速（MQA/GQA/MLA）** | [09.ai-applications/llm-inference/kv-cache-mqa-gqa-mla](../09.ai-applications/llm-inference/kv-cache-mqa-gqa-mla.md) |
| **推理引擎选型** | [09.ai-applications/llm-inference/inference-engine-selection](../09.ai-applications/llm-inference/inference-engine-selection.md) |
| **长上下文 Transformer** | [12.interview/11.ai/transformer-long-context-performance](../12.interview/11.ai/transformer-long-context-performance/) |
| **面试题：Transformer** | [12.interview/11.ai/transformer](../12.interview/11.ai/transformer/) |
| **故事：AI 推理** | [13.story/46-llm-inference](../../13.story/46-llm-inference.md) |
| **分布式 Attention 计算** | [06.distributed-systems/distributed-training](../06.distributed-systems/distributed-training/) |

---

## 十一、面试 Checklist（30 秒话术）

**问题 1：Attention 的核心公式是什么？为什么有 √d_k？**

- 答：**Attention(Q,K,V) = softmax(Q·K^T / √d_k)·V**，√d_k 把 Q·K^T 方差归一化到 1，防止 softmax 饱和。1 行答完。

**问题 2：Self-Attention 与 Cross-Attention 的区别？**

- 答：**Self Q=K=V 同序列；Cross Q 来自一个序列，K、V 来自另一个**。Encoder-Decoder 用 Cross，CLIP 文本-图像也用 Cross。1 行答完。

**问题 3：为什么需要 Multi-Head？**

- 答：**多子空间并行学习不同语义关系**（句法、指代、长程），表达力增强 + 训练稳定。1 行答完。

**问题 4：MQA / GQA / MLA 的差异？**

- 答：**MQA 所有 head 共享 1 份 KV（显存 1/h）；GQA g 组共享（h/g）；MLA 把 KV 压到潜在空间（≈1）**。LLaMA 用 GQA、DeepSeek 用 MLA。1 行答完。

**问题 5：Flash Attention 改变了数学吗？**

- 答：**数学等价，只优化 IO**。分块 softmax + SRAM 计算，显存 O(n²) → O(n)，速度 2-4x。1 行答完。

---

## 📚 参考来源

1. **Transformer 原始论文**：Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin et al. *Attention Is All You Need*. NeurIPS 2017. https://arxiv.org/abs/1706.03762
2. **FlashAttention**：Tri Dao, Daniel Y. Fu, Stefano Ermon, Atri Rudra, Christopher Ré et al. *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness*. NeurIPS 2022. https://arxiv.org/abs/2205.14135
3. **MQA（Multi-Query Attention）**：Noam Shazeer et al. *Fast Transformer Decoding: One Write-Head is All You Need*. arXiv 2019. https://arxiv.org/abs/1911.02150
4. **GQA（Grouped-Query Attention）**：Joshua Ainslie, James Lee-Thorp, Michiel de Jong, Yinfei Yang, Cuthan Saharia, David Grangier et al. *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints*. EMNLP 2023. https://arxiv.org/abs/2305.13245
5. **MLA（Multi-head Latent Attention）**：DeepSeek-AI. *DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model*. 2024. https://arxiv.org/abs/2405.04434
6. **Longformer（稀疏注意力）**：Iz Beltagy, Matthew E. Peters, Arman Cohan et al. *Longformer: The Long-Document Transformer*. arXiv 2020. https://arxiv.org/abs/2004.05150
7. **BigBird**：Manzil Zaheer, Guru Guruganesh, Avinava Dubey, Joshua Ainslie et al. *Big Bird: Transformers for Longer Sequences*. NeurIPS 2020. https://arxiv.org/abs/2007.14062
8. **Linear Attention**：Angelos Katharopoulos, Apoorv Vyas, Nikolaos Pappas, François Fleuret et al. *Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention*. ICML 2020. https://arxiv.org/abs/2006.16236
9. **Mamba**：Albert Gu, Tri Dao. *Mamba: Linear-Time Sequence Modeling with Selective State Spaces*. COLM 2024. https://arxiv.org/abs/2312.00752

---

← [返回 L1 基础概念](../README.md)