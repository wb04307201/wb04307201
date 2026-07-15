<!--
module:
  parent: ai
  slug: ai/llm-basics
  type: article
  category: 主模块子文章
  summary: 大语言模型基础：从统计语言模型到 Transformer
-->

# 大语言模型基础

> ⬅️ [返回 L1 基础概念](../README.md)

> **一句话定位**：大语言模型（LLM）= 基于 Transformer 架构、在万亿级 token 上自监督预训练、参数规模百亿到万亿级的统计语言模型。本节系统梳理从 N-gram → RNN → LSTM → Transformer 的演进逻辑，帮你建立"为什么是 Transformer"的认知地基。

---

## 🎯 学习目标

完成本节后，你能够：

- **历史脉络**：说出 NLP 从规则 → 统计 → 神经网络 → Transformer 的 4 个时代差异
- **架构认知**：用一句话说清 Transformer 的 Self-Attention + QKV + 位置编码三大核心
- **训练范式**：区分预训练 / 微调 / RLHF / DPO 4 个训练阶段的输入输出
- **关键概念**：准确解释 token / 上下文窗口 / 涌现能力 / 思维链 / 幻觉

---

## 📚 章节清单

| 章节 | 核心内容 | 阅读时长 |
|------|---------|---------|
| [01 从 N-gram 到 Transformer](01-ngram-to-transformer.md) | 4 个时代演进 + 为什么 RNN/LSTM 被淘汰 | 25 min |
| [02 Transformer 架构核心](02-transformer-architecture.md) | Self-Attention + QKV + Multi-Head + 位置编码 | 35 min |
| [03 预训练与微调](03-pretrain-and-finetune.md) | 预训练目标（MLM/CLM）+ SFT + RLHF + DPO | 30 min |
| [04 Token 与上下文窗口](04-token-and-context.md) | BPE / WordPiece / SentencePiece + 上下文窗口演进 | 25 min |
| [05 涌现能力与思维链](05-emergent-and-cot.md) | 涌现 vs 滑鼠效应 + CoT / ReAct / ToT | 20 min |

---

## 🧠 关键概念速查

| 概念 | 一句话定义 | 反直觉点 |
|------|----------|---------|
| **Token** | 模型处理的最小语义单元，不是字符也不是单词 | 中文 1 字 ≈ 1-2 token，英文 1 词 ≈ 1.3 token |
| **Embedding** | 把 token 映射到高维向量空间，相近语义距离近 | 同义词的向量余弦相似度 > 0.85 |
| **Self-Attention** | 序列内每个位置都关注所有其他位置，计算相关性权重 | O(n²) 复杂度是长上下文瓶颈 |
| **QKV** | Query（查询）+ Key（键）+ Value（值）三矩阵投影 | Q·K^T 计算注意力权重，权重 × V 得到输出 |
| **上下文窗口** | 模型一次能处理的最大 token 数 | 4K → 32K → 128K → 1M，窗口≠记忆 |
| **涌现能力** | 模型规模超过阈值后突然出现的能力 | 部分能力是评估指标伪相关，不是真涌现 |
| **思维链 CoT** | 让模型"一步一步想"提升推理能力 | 简单题加 CoT 反而降准 |
| **幻觉** | 模型生成看似合理但事实错误的内容 | 不知道答案时会"编"，不会说"不知道" |

---

## 📐 架构演进时间线

```
2013  Word2Vec           —— 静态词向量
2014  Seq2Seq + Attention —— 引入注意力机制
2015  NMT（神经机器翻译）—— RNN + Attention 主导
2017  Transformer        —— Google "Attention is All You Need"
2018  GPT-1 / BERT       —— 预训练 + 微调范式确立
2019  GPT-2 / T5         —— 零样本能力涌现
2020  GPT-3 (175B)       —— In-context Learning
2022  ChatGPT / InstructGPT —— RLHF 对齐人类意图
2023  GPT-4 / LLaMA 2    —— 多模态 + 开源追赶
2024  GPT-4o / Claude 3.5 —— 多模态原生 + 长上下文
2025  Claude 4 / o1 系列 —— Reasoning 模型 + Agent 时代
2026  LLM Agentic        —— Reasoning + Tool Use + Planning
```

---

## 🔗 兄弟章节

- **L1 同级**：[Transformer 架构核心](../transformer/README.md)
- **L2 技术栈**：[Token 与计费原理](../../02-technology-stack/token-billing/README.md)
- **咬文嚼字**：[Transformer 架构](../../../../13.split-hairs/11.ai/transformer/README.md) / [Token 原理](../../../../13.split-hairs/11.ai/token/README.md)
- **架构演进**：[LLM 驾驭演进史](../../04-architecture/llm-control-evolution/README.md) — L1 → L8 全景图

---

## ⚠️ 高频误区

| 误区 | 真相 |
|------|------|
| ❌ LLM "理解"语义 | ✅ LLM 学习的是 token 间的统计相关性，不是语义理解 |
| ❌ 上下文窗口 = 记忆容量 | ✅ 上下文窗口是"工作记忆"，超出即遗忘 |
| ❌ 更大的模型 = 更好的推理 | ✅ 仅在某些任务涌现，不是普适规律 |
| ❌ LLM 不会重复犯错 | ✅ 训练数据偏差会稳定复现 |

← 返回 [基础概念](../README.md)