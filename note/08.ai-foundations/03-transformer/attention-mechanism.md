<!--
module:
  parent: 08.ai-foundations/03-transformer
  slug: 08.ai-foundations/03-transformer/attention-mechanism
  type: article
  category: 主模块子文章
  summary: 注意力机制全家桶（Self/Cross/Multi-Head/Sparse/Linear/MQA/GQA）
  depth: ⭐⭐⭐⭐
-->

# 注意力机制（Attention Mechanism）

> ⬅️ [返回 L1 基础概念](../README.md)

> **一句话定位**：注意力机制 = **Q·K^T 算相关性 × V 加权求和**，让模型"聚焦"输入关键部分。本节覆盖 Self/Cross/Multi-Head/Sparse/Linear/MQA/GQA 全家桶，是理解所有 LLM 架构的钥匙。

---

## 🎯 学习目标

- **数学基础**：用一行公式说清 Attention(Q, K, V) = softmax(Q·K^T / √d) · V
- **变体谱系**：知道 7 大变体的差异（Self / Cross / MHA / MQA / GQA / Sparse / Linear）
- **工程价值**：能解释为什么 GQA 是 KV Cache 加速的关键
- **反直觉**：理解 Attention 的 O(n²) 复杂度为何是 LLM 推理瓶颈

---

## 📚 章节清单

| 主题 | 核心内容 | 阅读时长 |
|------|---------|---------|
| **01 Attention 数学基础** | QKV 推导 + 缩放因子 √d_k + 掩码 | 25 min |
| **02 Self / Cross / Causal** | 三种 QKV 来源 + Decoder-only 因果掩码 | 20 min |
| **03 Multi-Head Attention** | 多头并行的 4 大优势 | 20 min |
| **04 MQA / GQA** | KV Cache 加速的工业级方案 | 25 min |
| **05 Sparse Attention** | Longformer / BigBird 稀疏化 | 20 min |
| **06 Linear Attention** | O(n) 复杂度的探索 | 20 min |

---

## 🧠 核心公式速查

| 公式 | 含义 | 关键点 |
|------|------|--------|
| Attention(Q, K, V) = softmax(Q·K^T / √d_k) · V | 标准缩放点积注意力 | √d_k 防 softmax 饱和 |
| MultiHead(Q, K, V) = Concat(head_1, ..., head_h) · W^O | 多头并行 | 不同 head 学不同子空间 |
| GQA: 分组共享 KV | 8 组共享 1 份 KV | LLaMA-2/3 / Mistral 标准 |
| Flash Attention: 分块 softmax | 不写回 HBM | O(n) 显存 |

---

## 🔗 兄弟章节

- **L1 同级**：[Transformer 架构](./README.md)
- **L2 同模块**：位置编码 RoPE / MoE 架构 / Flash Attention — ⚠️ 待 Phase 1+ 迁入
- **L2 栈**：[KV Cache](../../09.ai-applications/llm-inference/kv-cache/)（推理复杂度 + MQA/GQA/MLA 对比）
- **咬文嚼字**：[`12.interview/11.ai/transformer`](../../12.interview/11.ai/transformer/) — Transformer 架构面试题

---

## ⚠️ 5 大反直觉

| 误区 | 真相 |
|------|------|
| ❌ Attention = 让模型"看"重要部分 | ✅ Attention 算的是 token 间相关性权重 |
| ❌ 头数越多越好 | ✅ 8-128 头已足够，再多收益边际递减 |
| ❌ Cross Attention 已过时 | ✅ 跨模态（CLIP/语音）仍核心 |
| ❌ Linear Attention 能取代 Softmax | ✅ 性能与表达力难以兼得，2024 仍未主流 |
| ❌ Flash Attention 改变了数学 | ✅ 数学等价，只优化 IO |

---

## 📚 参考来源

1. **Transformer 原始论文（Attention Is All You Need）**：Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin et al. *Attention Is All You Need*. NeurIPS 2017. https://arxiv.org/abs/1706.03762
2. **FlashAttention**：Tri Dao, Daniel Y. Fu, Stefano Ermon, Atri Rudra, Christopher Ré et al. *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness*. NeurIPS 2022. https://arxiv.org/abs/2205.14135
3. **MQA（Multi-Query Attention）**：Noam Shazeer et al. *Fast Transformer Decoding: One Write-Head is All You Need*. arXiv 2019. https://arxiv.org/abs/1911.02150
4. **GQA（Grouped-Query Attention）**：Joshua Ainslie, James Lee-Thorp, Michiel de Jong, Yinfei Yang, Cuthan Saharia, David Grangier et al. *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints*. EMNLP 2023. https://arxiv.org/abs/2305.13245
5. **Longformer（稀疏注意力）**：Iz Beltagy, Matthew E. Peters, Arman Cohan et al. *Longformer: The Long-Document Transformer*. arXiv 2020. https://arxiv.org/abs/2004.05150
6. **Linear Attention**：Angelos Katharopoulos, Apoorv Vyas, Nikolaos Pappas, François Fleuret et al. *Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention*. ICML 2020. https://arxiv.org/abs/2006.16236

← [返回 L1 基础概念](../README.md)