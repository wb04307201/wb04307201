<!--module:
  parent: 08.ai-foundations
  slug: 08.ai-foundations/03-transformer
  type: index-only
  category: AI 基础索引
  summary: Transformer 架构——注意力机制、位置编码、Self-Attention / Multi-Head / KV Cache / MQA-GQA-MLA / FlashAttention 核心组件解析。
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
- **最后更新**：2026-08-20

---

← [返回 08.ai-foundations](../README.md)
