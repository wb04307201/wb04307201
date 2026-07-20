<!--
question:
  id: 11.ai-transformer
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [11.ai, Transformer, transformer]
-->

# Transformer 架构 — Self-Attention 面试深挖

> 一句话定位：Transformer 是 2017 年 Google "Attention is All You Need" 提出的架构，核心创新是 Self-Attention。完整概念见 [主模块 Transformer](../../../11.ai/01-fundamentals/transformer/README.md)。

---

## 引子：Google 为什么在 2017 年放弃 RNN？

2017 年前，做机器翻译只能用 RNN/LSTM。问题很要命：

- **训练慢**：必须串行处理，"100 个词的句子"比"10 个词"慢 10 倍
- **长句子崩**：第三个词的相关性到第 50 个词已经"忘光了"
- **并行不了**：100 个 GPU 跟 1 个 GPU 效果一样，钱白花

Google 的团队受不了了。他们投一个完全不同的方向——
**完全抛弃 RNN，让模型自己用注意力找相关性**。
这就是"Attention is All You Need"论文的诞生时刻，也是 Transformer 一统江湖的起点。
今天，**所有 GPT / BERT / Claude / LLaMA 都是 Transformer 的徒子徒孙**。

## 一、核心公式（一行记全）

```text
Attention(Q, K, V) = softmax(Q × K^T / √d) × V
```

- **Q（Query）**：我要找什么
- **K（Key）**：我有什么
- **V（Value）**：实际内容
- **√d**：缩放因子（防止点积过大）

---

## 二、面试陷阱

### 陷阱 1：以为 Self-Attention 就是"加权平均"
- **真相**：Self-Attention 通过 Q×K 计算相似度得到权重，再用权重对 V 加权 —— 不是简单的平均，是"动态查询"。

### 陷阱 2：以为多头是"切分维度"
- **真相**：多头是多个独立注意力头并行，每个头学习**不同的语义关系**（头 1 学主谓关系、头 2 学指代消解...），最后拼接。

### 陷阱 3：以为 Transformer 自带顺序
- **真相**：Transformer **并行计算无顺序**，必须显式注入 **Positional Encoding**（sin/cos），否则"我吃苹果"和"苹果吃我"无法区分。

### 陷阱 4：以为 √d 可省略
- **真相**：√d 是关键缩放因子 —— 不除以 √d，Q×K^T 值过大导致 softmax 梯度消失。

---

## 三、反直觉点

- **Transformer 没有"循环"**：RNN 的循环结构被 Self-Attention 完全替代，训练可全并行，速度快 N 倍。
- **Encoder / Decoder 是组合关系**：BERT（仅 Encoder）/ GPT（仅 Decoder）/ T5（Encoder+Decoder），现代 LLM 主流是 Decoder-only。
- **Multi-Head 的"头数"是超参**：典型 8-16 头，头数 × 头维度 = 模型维度。

---

## 四、面试速记表

| 架构 | 例子 | 任务类型 |
|------|------|---------|
| 仅 Encoder | BERT | 理解（分类、NER） |
| **仅 Decoder** | **GPT / LLaMA / Claude** | **生成（对话、写作）—— 2026 主流** |
| Encoder + Decoder | T5 / BART | 翻译、摘要 |

---

## 五、30 秒面试话术

> Transformer 是 2017 年 Google 提出的，核心创新是 Self-Attention 机制。
>
> Self-Attention 本质：每个 token 通过 Q（Query）、K（Key）、V（Value）三个矩阵，计算与其他 token 的相似度，得到加权特征。公式：`softmax(Q × K^T / √d) × V`。
>
> Multi-Head：多个注意力头并行，每个头学习不同的语义关系。
>
> Positional Encoding：用 sin/cos 注入位置信息（因为 Transformer 并行，无顺序）。
>
> 三种变体：仅 Encoder = BERT（理解任务）；仅 Decoder = GPT / LLaMA / Claude（生成任务，2026 主流）；Encoder + Decoder = T5（翻译、摘要）。
>
> Transformer 让 LLM 成为可能，是当前所有大模型的基石。

---

## 六、深度阅读

- 主模块：[Transformer 架构](../../../11.ai/01-fundamentals/transformer/README.md)
- 关联：[Token 与计费](../../../11.ai/02-technology-stack/token-billing/README.md)
- 应用：[RAG](../../../11.ai/08-llmops/01-rag-vs-finetuning/README.md)

---

> 📅 2026-06-30 · 咬文嚼字 · AI 基础必问 · ⭐⭐⭐⭐⭐

← [返回: 咬文嚼字 · transformer](../README.md)
