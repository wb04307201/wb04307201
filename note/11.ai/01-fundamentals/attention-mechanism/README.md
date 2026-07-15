<!--
module:
  parent: ai
  slug: ai/attention-mechanism
  type: article
  category: 主模块子文章
  summary: 注意力机制全家桶（Self/Cross/Multi-Head/Sparse/Linear/MQA/GQA）
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

- **L1 同级**：[Transformer 架构](../transformer/README.md) / [位置编码 RoPE](../rope-position-encoding/README.md) / [MoE 架构](../moe-architecture/README.md) / [Flash Attention](../flash-attention/README.md)
- **L2 栈**：[KV Cache](../../02-technology-stack/kv-cache/README.md)
- **咬文嚼字**：[Transformer 面试题](../../../13.split-hairs/11.ai/transformer/README.md)

---

## ⚠️ 5 大反直觉

| 误区 | 真相 |
|------|------|
| ❌ Attention = 让模型"看"重要部分 | ✅ Attention 算的是 token 间相关性权重 |
| ❌ 头数越多越好 | ✅ 8-128 头已足够，再多收益边际递减 |
| ❌ Cross Attention 已过时 | ✅ 跨模态（CLIP/语音）仍核心 |
| ❌ Linear Attention 能取代 Softmax | ✅ 性能与表达力难以兼得，2024 仍未主流 |
| ❌ Flash Attention 改变了数学 | ✅ 数学等价，只优化 IO |

← [返回 L1 基础概念](../README.md)