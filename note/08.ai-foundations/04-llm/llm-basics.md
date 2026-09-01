<!--
module:
  parent: 08.ai-foundations/04-llm
  slug: 08.ai-foundations/04-llm/llm-basics
  type: article
  category: 主模块子文章
  summary: 大语言模型基础——从统计语言模型到 Transformer 的演进、四大训练范式、关键概念与 6 家公司 LLM 实战。
  depth: ⭐⭐⭐⭐⭐
-->

# 大语言模型基础

> **一句话定位**：大语言模型（LLM）= **基于 Transformer 架构 + 在万亿级 token 上自监督预训练 + 参数规模百亿到万亿级**的统计语言模型。本节系统梳理从 N-gram → RNN → LSTM → Transformer → LLM 的演进逻辑，帮你建立"为什么是 Transformer"的认知地基。

> ⬅️ [返回 LLM 基础](../README.md)

---

## 🎯 学习目标

完成本文后，你能够：

- **历史脉络**：说出 NLP 从规则 → 统计 → 神经网络 → Transformer → LLM 的 5 个时代差异
- **架构认知**：用一句话说清 Transformer 的 Self-Attention + QKV + 位置编码三大核心
- **训练范式**：区分预训练 / SFT / RLHF / DPO / RLAIF 5 个训练阶段的输入输出
- **关键概念**：准确解释 token / 上下文窗口 / 涌现能力 / 思维链 / 幻觉 / Scaling Laws
- **公司生态**：知道 GPT / Claude / Gemini / LLaMA / Qwen / DeepSeek 6 大主流 LLM 的特点

---

## 📚 章节清单

| 章节 | 核心内容 | 阅读时长 |
|------|---------|---------|
| **01 从 N-gram 到 Transformer** | 5 个时代演进 + 为什么 RNN/LSTM 被淘汰 | 25 min |
| **02 Transformer 架构核心** | Self-Attention + QKV + Multi-Head + 位置编码 | 25 min |
| **03 预训练与微调** | 预训练目标（MLM/CLM）+ SFT + RLHF + DPO | 25 min |
| **04 Token 与上下文窗口** | BPE / WordPiece / SentencePiece + 上下文窗口演进 | 20 min |
| **05 涌现能力与思维链** | 涌现 vs 滑鼠效应 + CoT / ReAct / ToT | 15 min |
| **06 Scaling Laws 与规模效应** | Kaplan / Chinchilla + 涌现阈值 | 15 min |
| **07 6 大公司 LLM 实战** | GPT / Claude / Gemini / LLaMA / Qwen / DeepSeek | 15 min |
| **08 反直觉与误区** | 5 大高频认知偏差 | 10 min |

---

## 一、从 N-gram 到 Transformer：5 个时代演进

### 1.1 时代 1：规则系统（1950s-1990s）

**核心思想**：人类编写语言学规则（语法、词典）。

**代表**：ELIZA（1966，MIT，早期 chatbot）、SHRDLU（1970，MIT，积木世界对话）。

**致命问题**：

- **规则爆炸**：1000 条规则覆盖不到 1% 真实语言
- **维护地狱**：每种新现象需要新规则
- **跨语言迁移**：每种语言需重写

### 1.2 时代 2：统计语言模型 N-gram（1990s-2010s）

**核心数学**：马尔可夫假设 + 最大似然估计。

$$P(w_t \mid w_1, \ldots, w_{t-1}) \approx P(w_t \mid w_{t-n+1}, \ldots, w_{t-1})$$

**举例**：Bigram 模型：

$$P(\text{我} \mid \text{开始}) = \frac{C(\text{开始 我})}{C(\text{开始})}$$

**代表**：SRILM、Kneser-Ney 平滑。

**优点**：简单、可解释、训练快。

**致命问题**：

- **维度灾难**：N 越大，$N$-gram 组合数指数爆炸
- **数据稀疏**：4-gram 以上覆盖率 < 1%
- **无泛化**："跑了"和"奔跑"的 4-gram 完全独立

### 1.3 时代 3：神经网络语言模型（2003-2017）

**代表**：Bengio 2003 NNLM、Mikolov 2013 Word2Vec、ELMo 2018。

**核心创新**：

- **词向量**：每个词映射到低维密集向量（语义几何保留）
- **RNN/LSTM**：序列建模，理论上可处理任意长度历史

**Word2Vec 的"语义几何"**：

```text
vec("king") - vec("man") + vec("woman") ≈ vec("queen")
vec("Paris") - vec("France") + vec("Italy") ≈ vec("Rome")
```

**但 RNN/LSTM 有 3 大致命问题**：

1. **顺序计算**：无法并行（GPU 加速难）
2. **长程依赖**：理论上 LSTM 可记忆 100 步，实测 50 步以上就崩
3. **梯度问题**：长序列反向传播梯度消失/爆炸

### 1.4 时代 4：Transformer（2017-2020）

**核心创新**：**Self-Attention 替代 RNN**——并行计算 + 全局依赖。

```text
RNN:  t1 → t2 → t3 → t4 → t5   (顺序，O(n) 步)
Transformer: [t1, t2, t3, t4, t5] → 一层 attention 全连接   (并行，O(1) 步)
```

**参数量演进**：

| 模型 | 年份 | 参数量 | 关键创新 |
|------|------|--------|---------|
| Transformer (Encoder-Decoder) | 2017 | 65M (Base) / 213M (Big) | Self-Attention |
| GPT-1 | 2018 | 117M | Decoder-only + 预训练 |
| BERT-Base | 2018 | 110M | Encoder + MLM |
| GPT-2 | 2019 | 1.5B | Zero-shot |
| T5 | 2019 | 11B | Text-to-Text 统一 |
| GPT-3 | 2020 | 175B | In-context Learning |

### 1.5 时代 5：LLM 时代（2020-2026）

**LLM 的"涌现"特征**：

- **参数规模**：100B → 1T+（GPT-4 1.8T 推测、Mistral MoE 巨大）
- **训练数据**：300B → 15T+ tokens（Qwen-2.5 用 18T）
- **训练算力**：千卡 → 10 万卡集群
- **能力涌现**：In-context Learning、CoT、Agent

**规模定律（Scaling Laws）**：

$$\mathcal{L}(N, D) \approx \left( \frac{N_c}{N} \right)^{\alpha_N} + \left( \frac{D_c}{D} \right)^{\alpha_D} + \mathcal{L}_\infty$$

- $N$：参数量
- $D$：数据量
- $\alpha_N \approx 0.076$，$\alpha_D \approx 0.095$
- $\mathcal{L}_\infty$：理论损失下界

### 1.6 完整时间线（2013-2026）

```text
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
2024  DeepSeek-V2 / V3   —— MoE + MLA
2025  Claude 4 / o1 系列 —— Reasoning 模型 + Agent 时代
2026  LLM Agentic        —— Reasoning + Tool Use + Planning
```

---

## 二、Transformer 架构核心

### 2.1 三大核心组件

```text
┌──────────────────────────────────────────────┐
│           Transformer Block                   │
│                                               │
│  x → LayerNorm → Multi-Head Attention → + → │
│  └─────────────────────────────────────────────┘
│   ↓                                            │
│  x → LayerNorm → Feed-Forward (FFN)    → + → │
│  └─────────────────────────────────────────────┘
│   ↓                                            │
│  Output                                        │
└──────────────────────────────────────────────┘
```

#### 2.1.1 Self-Attention

**公式**：

$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^\top}{\sqrt{d_k}}\right) \mathbf{V}$$

**关键点**：

- **Q/K/V 三个投影**：每个 token 都有 Q、K、V 三个向量
- **Q·K^T 算相关性**：token 间相关矩阵 $(n \times n)$
- **缩放因子 √d_k**：防止 softmax 饱和
- **加权 V 求和**：每个 token 输出是所有 token 的加权和

> 详见 [注意力机制](../03-transformer/attention-mechanism.md)

#### 2.1.2 Multi-Head Attention

**核心**：将 $d_{model}$ 维度拆成 $h$ 个 head，每个 head 独立 Attention。

$$\text{MultiHead}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) \mathbf{W}^O$$

**优势**：

- 多子空间并行学习不同语义关系
- 表达力增强
- 头数通常 32-96

#### 2.1.3 位置编码

**为什么需要**：Transformer 本身无顺序概念（attention 是 permutation-invariant）。

**两种方案**：

| 方案 | 公式 | 优势 | 劣势 |
|------|------|------|------|
| **绝对位置编码** | $PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d})$ | 简单、可解释 | 外推性差 |
| **RoPE**（旋转位置编码）| 二维旋转矩阵 $\mathbf{R}_m$ | 相对位置 + 长度外推 | 需自定义实现 |
| **ALiBi** | 线性 bias 加到 attention | 训练时未见过长度仍可工作 | 性能略低 |

**RoPE（LLaMA、Qwen、DeepSeek 使用）**：

```text
对 token 在位置 m 的向量 q，应用旋转矩阵 R(m, θ)
R(m, θ) = [[cos(mθ), -sin(mθ)], [sin(mθ), cos(mθ)]]

效果：q 与 k 的内积只依赖它们的相对位置 (m-n)，不依赖绝对位置
优势：训练时见过 4096 长度，可外推到 32K-128K（配合 YaRN）
```

### 2.2 Encoder vs Decoder vs Encoder-Decoder

| 类型 | 结构 | Attention 模式 | 代表 | 任务 |
|------|------|----------------|------|------|
| **Encoder-only** | 自注意力双向 | 全连接 | BERT、RoBERTa | 分类、检索、Embedding |
| **Decoder-only** | 自注意力单向 | Causal Mask | GPT、LLaMA、Claude | 文本生成（LLM 主流）|
| **Encoder-Decoder** | 双向 + Cross | 双向 + Cross | T5、BART、Whisper | 翻译、摘要、ASR |

**2024 趋势**：**Decoder-only 一统天下**（LLaMA、Qwen、Claude、DeepSeek、Mistral 全是 Decoder-only）。

---

## 三、预训练与微调（5 个训练阶段）

### 3.1 训练阶段全景图

```text
┌─────────────────────────────────────────────────────┐
│ Stage 1：预训练（Pre-training）                      │
│ • 数据：万亿级无标注文本                            │
│ • 目标：next-token prediction (CLM)              │
│ • 算力：1000+ GPU × 30 天                        │
│ • 产出：base 模型（如 LLaMA-3-70B-base）         │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│ Stage 2：监督微调（SFT, Supervised Fine-Tuning）   │
│ • 数据：10万-100万 (prompt, response) 高质量示范   │
│ • 目标：模仿人类示范                                │
│ • 算力：100 GPU × 1-7 天                          │
│ • 产出：SFT 模型（如 LLaMA-3-70B-Instruct）        │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│ Stage 3：奖励建模（Reward Model）                   │
│ • 数据：人类偏好标注（A vs B 哪个更好）            │
│ • 目标：训练奖励模型预测人类偏好                    │
│ • 产出：reward model                                │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│ Stage 4：RLHF（PPO 强化学习）                       │
│ • 数据：prompt → SFT 模型生成多个 response        │
│ • 奖励：reward model 打分                            │
│ • 目标：PPO 最大化 reward                            │
│ • 产出：aligned LLM（GPT-4、Claude-3.5）           │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│ Stage 5：DPO（可选替代 RLHF）                       │
│ • 数据：偏好对 (prompt, y_w, y_l)                  │
│ • 目标：直接优化偏好，无需 reward model              │
│ • 优势：训练稳定 2-3x，无需在线采样                  │
│ • 产出：DPO LLM（Mistral、Zephyr）                  │
└─────────────────────────────────────────────────────┘
```

### 3.2 预训练目标

#### 3.2.1 CLM（Causal Language Modeling）

**GPT 系**用 next-token prediction：

$$\mathcal{L}_{CLM} = -\sum_{t=1}^{T} \log P(w_t \mid w_{<t}; \theta)$$

#### 3.2.2 MLM（Masked Language Modeling）

**BERT 系**用 masked token prediction：

$$\mathcal{L}_{MLM} = -\sum_{w_i \in \text{masked}} \log P(w_i \mid w_{\text{context}}; \theta)$$

- 15% token 被 mask（80% [MASK]、10% 随机、10% 原词）
- 双向信息（看到上下文）

#### 3.2.3 两者对比

| 维度 | CLM（GPT）| MLM（BERT）|
|------|-----------|-----------|
| 信息流 | 单向（左→右）| 双向 |
| 训练效率 | ✅ 高（每个 token 都贡献 loss）| ⚠️ 低（只有 15% token 贡献）|
| 下游任务 | 生成（ChatGPT）| 理解（分类、检索）|
| 当前主流 | ✅ | ⚠️ 仅 BERT 系 |

### 3.3 RLHF 详解

**三阶段**：见 3.1 节全景图。

**关键算法**：PPO（近端策略优化）。

```python
# RLHF PPO 简化版
def ppo_step(policy, ref_policy, reward_model, prompt, response):
    # 1. policy 生成 response
    log_probs = policy(prompt, response)  # 当前策略概率

    # 2. ref_policy（旧策略）概率（用于 KL 约束）
    ref_log_probs = ref_policy(prompt, response)

    # 3. reward model 打分
    reward = reward_model(prompt, response)

    # 4. PPO 损失（clipped surrogate）
    ratio = torch.exp(log_probs - ref_log_probs)
    advantage = reward - baseline  # 减去基线
    loss = -torch.min(
        ratio * advantage,
        torch.clamp(ratio, 0.8, 1.2) * advantage
    )

    return loss.mean()
```

### 3.4 DPO（Direct Preference Optimization，2023）

**核心**：**绕过 reward model，直接用偏好对优化策略**。

$$\mathcal{L}_{DPO} = -\mathbb{E}_{(x, y_w, y_l) \sim D} \log \sigma \left( \beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{ref}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{ref}(y_l \mid x)} \right)$$

**优势**：

- ✅ 训练稳定（无 reward model 噪声）
- ✅ 训练快 2-3x（无需在线采样）
- ✅ 效果接近 RLHF

**代表**：Mistral、Zephyr、Llama-3-Chinese。

### 3.5 RLAIF（2023，Google）

**核心**：**用 LLM 评判替代人类标注**——LLM-as-Judge。

```text
Constitutional AI（Anthropic）：

1. LLM 生成 response
2. LLM 自己评判 response 是否符合宪法（预先定义的安全原则）
4. 用 LLM 的偏好训练 DPO
5. 产出：无需人类标注的 aligned LLM
```

**意义**：**解决 RLHF 的扩展性问题**（人工标注成本高、速度慢）。

---

## 四、Token 与上下文窗口

### 4.1 什么是 Token？

**Token** = 模型处理的**最小语义单元**，**不是字符也不是单词**。

**3 种分词方式**：

| 方法 | 原理 | 代表 | 优势 | 劣势 |
|------|------|------|------|------|
| **BPE** | 字节对合并 | GPT-2/3、LLaMA | 高效、通用 | 中文支持差 |
| **WordPiece** | 似然最大化 | BERT | 与 BERT 配合 | 训练慢 |
| **SentencePiece** | 语言无关 | LLaMA、Qwen | 中文友好 | 需自己训练 |

**BPE 简化示例**：

```text
初始词表：a, b, c, d, e, ab, ac, ...
训练数据："ababab caba baba"
迭代合并：
- "ab" 出现最多 → 合并为 token "ab"
- "aba" 出现最多 → 合并为 "aba"
...
最终词表：a, b, c, d, e, ab, aba, ...
```

**Token 数量估算**：

- **英文**：1 token ≈ 0.75 单词 ≈ 4 字符
- **中文**：1 token ≈ 0.6-1 字（Qwen tokenizer）

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")
text = "Hello world, 你好世界"
tokens = tokenizer.encode(text)
print(f"文本: {text}")
print(f"Tokens: {tokens}")
print(f"Token 数: {len(tokens)}")
# "Hello world, 你好世界" → 11 tokens（英文 3 token，中文每个字 1-3 token）
```

### 4.2 上下文窗口演进

```text
2018 BERT:      512 tokens
2019 GPT-2:    1024 tokens
2020 GPT-3:    2048 tokens
2023 GPT-3.5:  4096 → 16K tokens
2023 GPT-4:    8K → 32K tokens
2023 Claude 2: 100K tokens
2024 Claude 3: 200K tokens
2024 GPT-4o:   128K tokens
2024 Gemini 1.5: 1M tokens（首个百万级）
2024 Qwen-2.5: 32K → 128K (YaRN)
2025 Claude 4: 200K（稳定）
2025 GPT-4.1:  1M tokens
```

**反直觉点**：**上下文窗口 ≠ 记忆容量**——窗口是"工作记忆"，超出即遗忘，且 LLM 在长上下文中性能会下降（"lost in the middle"）。

### 4.3 长上下文技术

1. **RoPE + YaRN**（Qwen）：旋转位置编码 + 长度外推
2. **NTK-aware Scaling**（Meta）：动态缩放位置编码基数
3. **滑动窗口**（Mistral）：4096 token 窗口 + 滚动
4. **Flash Attention**：O(n²) FLOPs + O(n) 显存

---

## 五、涌现能力与思维链

### 5.1 涌现能力（Emergent Ability）

**定义**：模型规模超过某个阈值后**突然出现**的能力。

**典型涌现能力**：

- **In-context Learning**（few-shot prompting）：100B+ 涌现
- **Chain-of-Thought 推理**：100B+ 涌现
- **多语言翻译**：50B+ 涌现
- **代码生成**：10B+ 涌现

**反直觉点**：**部分能力是评估指标的伪相关**，不是真涌现。

**Stanford 2023 论文**（Are Emergent Abilities a Mirage?）：

- 涌现是**评估指标非线性选择**造成的（如 exact match）
- 用连续指标（如 token-level accuracy）则没有明显涌现

### 5.2 思维链（Chain-of-Thought, CoT）

**核心**：让模型"一步一步想"提升推理能力。

```text
标准 Prompt：
Q: "5 个苹果 + 3 个苹果 = ?"
A: "8"

CoT Prompt：
Q: "5 个苹果 + 3 个苹果 = ? 让我一步一步想：先有 5 个苹果，再加上 3 个，一共 8 个。"
A: "5 + 3 = 8，所以答案是 8"
```

**3 种 CoT 模式**：

| 模式 | 说明 | 代表 |
|------|------|------|
| **Few-shot CoT** | 给几个带推理过程的示例 | Wei et al. 2022 |
| **Zero-shot CoT** | 加 "Let's think step by step" | Kojima et al. 2022 |
| **Auto-CoT** | 自动生成 CoT 示例 | Zhang et al. 2022 |

### 5.3 进阶推理范式

| 范式 | 核心思想 | 应用 |
|------|----------|------|
| **CoT** | 逐步推理 | 数学、逻辑 |
| **ReAct** | Reasoning + Acting | Agent、工具调用 |
| **ToT**（Tree of Thoughts）| 多路径搜索 | 复杂规划 |
| **Reflexion** | 反思 + 记忆 | 自我迭代 |
| **Self-Consistency** | 多采样投票 | 推理准确度 |
| **Constitutional AI** | 原则约束 | 安全对齐 |

---

## 六、Scaling Laws 与规模效应

### 6.1 Kaplan 定律（2020，OpenAI）

**核心结论**：

$$\mathcal{L}(N) \propto N^{-\alpha_N}$$

- 损失随参数量幂律下降
- $\alpha_N \approx 0.076$
- 模型规模比数据规模更重要

### 6.2 Chinchilla 定律（2022，DeepMind）

**反驳 Kaplan**：模型规模和数据规模需要**均衡增长**。

$$\text{最优 } N / D \approx 20 \text{ (token per parameter)}$$

**例子**：

- GPT-3（2020）：175B 参数 / 300B tokens → **欠训练**（应有 3.5T tokens）
- Chinchilla（70B / 1.4T）→ **训练充分**
- LLaMA-2-70B（70B / 2T）→ **接近 Chinchilla 最优**

**2024 反思**：实际 LLM 训练已**超过** Chinchilla 最优（如 Qwen-2.5 72B / 18T → 250 tokens/param），数据质量提升可支持更多 epoch。

### 6.3 涌现阈值（Emergence Threshold）

| 能力 | 涌现阈值（参数量） |
|------|------------------|
| 基本问答 | 1B |
| 简单推理 | 10B |
| In-context Learning | 100B |
| CoT 推理 | 100B+ |
| 代码生成 | 1B+（Code-Specific）|
| 复杂多步推理 | 500B+ |

**反直觉点**：**涌现阈值不是固定的**——通过改进训练数据 / 算法可降低（如 DeepSeek 用 67B 做到 GPT-4 80% 性能）。

---

## 七、6 大公司 LLM 实战

### 7.1 OpenAI — GPT 系列

**关键时间线**：

| 模型 | 年份 | 参数量 | 关键创新 |
|------|------|--------|---------|
| GPT-1 | 2018 | 117M | Decoder-only 路线 |
| GPT-2 | 2019 | 1.5B | Zero-shot |
| GPT-3 | 2020 | 175B | In-context Learning |
| GPT-3.5 | 2022 | 未披露 | RLHF + ChatGPT |
| GPT-4 | 2023 | 1.8T (推测) | 多模态、专家混合 |
| GPT-4o | 2024 | 未披露 | 多模态原生 |
| o1 / o3 | 2024-2025 | 未披露 | Reasoning 推理链 |
| GPT-4.1 | 2025 | 未披露 | 1M 上下文 |

**关键洞察**：

- GPT-4 引入 Mixture-of-Experts（推测）
- o1 引入**推理时计算**（test-time compute）
- 闭源 + 商用 + API 为主

### 7.2 Anthropic — Claude 系列

**关键特性**：

- **Claude 3 Opus**（2024）：MMLU 90%+，长文档理解最强
- **Claude 3.5 Sonnet**（2024）：SWE-Bench 编码 SOTA
- **Claude 4**（2025）：Computer Use、Artifacts、Reasoning
- **Constitutional AI**（自研）：用原则约束替代部分人类标注
- **200K 上下文** + 长文档 Recall 领先

### 7.3 Google DeepMind — Gemini 系列

| 模型 | 关键特性 |
|------|---------|
| **Gemini 1.0**（2023）| 多模态原生、原生视频理解 |
| **Gemini 1.5**（2024）| 1M 上下文（首个）、MoE 架构 |
| **Gemini 2.0**（2024）| Agent 时代、Flash 性价比高 |
| **Gemini 2.5**（2025）| Reasoning 能力 |

**核心优势**：TPU 算力 + 多模态原生训练 + 学术生态（JAX/Flax）。

### 7.4 Meta — LLaMA 系列

**LLaMA-1（2023）**：开源 LLM 标杆，论文引爆开源浪潮。

**LLaMA-2（2023）**：2T tokens 训练 + RLHF + 商业可用许可。

**LLaMA-3（2024）**：15T tokens 训练 + GQA + 多模态（3.1 引入）。

**生态影响**：

- 衍生模型 10000+（Alpaca、Vicuna、Qwen、DeepSeek 等都基于 LLaMA 起步）
- HuggingFace 下载量第一

### 7.5 Qwen（阿里）— 中文 LLM 标杆

**Qwen-1.5**（2024）：7B / 72B，10T tokens 训练。

**Qwen-2**（2024）：开源 SOTA，支持 128K 上下文。

**Qwen-2.5**（2024-2025）：18T tokens 训练，72B 模型开源 SOTA：

- **Qwen2.5-72B**：开源最强，与 GPT-4 持平
- **Qwen2.5-Coder**：代码 SOTA
- **Qwen2.5-Math**：数学 SOTA

**Qwen3**（2025）：原生 32K 上下文，多模态。

**关键创新**：中英双语平衡 + 多尺寸（0.5B-110B）+ 全开源（Apache 2.0）。

### 7.6 DeepSeek — 国产开源之光

**DeepSeek-V1（2024）**：67B MoE，对标 GPT-3.5。

**DeepSeek-V2（2024）**：236B MoE / 21B 激活，**首创 MLA（Multi-head Latent Attention）**。

**DeepSeek-V3（2024-2025）**：671B MoE / 37B 激活，训练成本仅 $5.5M。

**关键创新**：

- **MLA**：KV Cache 压缩 93%
- **MoE**：21B 激活 vs 671B 总参数
- **开源彻底**：MIT 协议 + 全栈开源（论文、代码、训练数据）
- **训练成本**：GPT-4 的 1/100（$5.5M vs $100M+）

---

## 八、5 大反直觉点

### 误区 1：❌ LLM "理解"语义

**真相**：**LLM 学习的是 token 间的统计相关性，不是语义理解**

- LLM 是"超大规模统计模式匹配器"
- 没有意识、没有意图、没有真正的"理解"
- **哲学争议**：哲学家认为 LLM 的统计建模本身就是"理解"的一种形态

### 误区 2：❌ 上下文窗口 = 记忆容量

**真相**：**上下文窗口是"工作记忆"，超出即遗忘**

- 128K 上下文 ≠ 128K 永久记忆
- "Lost in the middle"：长上下文中段信息 Recall 显著下降（[Liu et al. 2023](https://arxiv.org/abs/2307.03172)）
- 永久记忆需 RAG / 外部知识库

### 误区 3：❌ 更大的模型 = 更好的推理

**真相**：**仅在某些任务涌现，不是普适规律**

- 涌现是评估指标伪相关（Stanford 2023 论文）
- 用连续指标（如 token-level accuracy）则没有明显涌现
- **小模型 + 优质数据 + CoT** 也能做到大模型水平

### 误区 4：❌ LLM 不会重复犯错

**真相**：**训练数据偏差会稳定复现**

- "9.11 大于 9.9" —— GPT-4 也可能答错
- 训练数据中"9.11 > 9.9"从未出现
- **修正方法**：RLHF / Constitutional AI / 数据增强

### 误区 5：❌ LLM = AGI

**真相**：**LLM 距离 AGI 还有 4-5 个关键差距**

| LLM 现状 | AGI 需要 |
|---------|---------|
| 文本理解 | 多模态原生（已部分实现） |
| 推理能力 | 强推理（o1 改进） |
| 工具使用 | 复杂 Agent 规划（ReAct、ToT） |
| 长期记忆 | RAG + 记忆架构（尚不成熟） |
| 真实世界行动 | 具身智能（机器人） |
| 自我改进 | 自我反思 + 元学习（远期） |

**LLM 是 AGI 的重要前置技术，但还不是 AGI**。

---

## 九、跨模块反向链（10+）

| 主题 | 链接 |
|------|------|
| **Transformer 架构** | [08.ai-foundations/03-transformer/transformer-architecture](../03-transformer/transformer-architecture.md) |
| **注意力机制** | [08.ai-foundations/03-transformer/attention-mechanism](../03-transformer/attention-mechanism.md) |
| **Embedding** | [08.ai-foundations/05-tokenization-embedding/embedding](../05-tokenization-embedding/embedding.md) |
| **Dropout 实证** | [08.ai-foundations/04-llm/dropout-in-llm/single-epoch-and-config-evidence](../04-llm/dropout-in-llm/single-epoch-and-config-evidence.md) |
| **深度学习框架** | [08.ai-foundations/02-deep-learning/deep-learning-frameworks](../02-deep-learning/deep-learning-frameworks.md) |
| **RL / RLHF** | [08.ai-foundations/01-ml/ml-to-rl](../01-ml/ml-to-rl.md) |
| **RLHF 算法** | [09.ai-applications/llm-alignment](../../09.ai-applications/fine-tuning/02-rlhf.md) |
| **KV Cache** | [09.ai-applications/llm-inference/kv-cache](../../09.ai-applications/llm-inference/kv-cache/README.md) |
| **推理引擎选型** | [09.ai-applications/llm-inference/inference-engine-selection](../../09.ai-applications/llm-inference/inference-frameworks/README.md) |
| **微调 LoRA / DPO** | 09.ai-applications/fine-tuning |
| **面试题：Transformer** | [12.interview/11.ai/transformer](../../12.interview/11.ai/transformer/README.md) |
| **面试题：LLM 基础** | [12.interview/11.ai/token](../../12.interview/11.ai/token/README.md) |
| **故事：LLM 推理** | [13.story/46-llm-inference](../../13.story/46-llm-inference.md) |
| **故事：AI 致命三胞胎** | [13.story/31-ai-fatal-trio](../../13.story/31-ai-fatal-trio.md) |
| **分布式 LLM 训练** | [06.distributed-systems/distributed-training](llm-basics.md) |
| **GPU 集群调度** | [06.distributed-systems/gpu-cluster-scheduling](../../07.devops-and-tools/02-workflow/README.md) |

---

## 十、面试 Checklist（30 秒话术）

**问题 1：LLM 与传统 NLP 的核心区别？**

- 答：**LLM 基于 Transformer + 万亿级 token 自监督预训练 + 涌现能力**（In-context Learning、CoT）。传统 NLP 用 RNN/LSTM + 小规模有标注数据。1 行答完。

**问题 2：什么是 Token？BPE / WordPiece / SentencePiece 区别？**

- 答：**Token 是模型处理的最小语义单元**。BPE 用字节对合并（GPT），WordPiece 用似然最大化（BERT），SentencePiece 语言无关（LLaMA、Qwen）。1 行答完。

**问题 3：RLHF 三阶段是什么？**

- 答：**SFT（监督微调）→ Reward Model（奖励建模）→ PPO（强化学习）**。ChatGPT、Claude、GPT-4 都用此对齐。1 行答完。

**问题 4：DPO 相对 RLHF 的优势？**

- 答：**无需 reward model，直接优化偏好**，训练稳定 2-3x，效果接近 RLHF。Mistral、Zephyr 已采用。1 行答完。

**问题 5：为什么 Transformer 替代了 RNN？**

- 答：**并行计算（Self-Attention 全连接，O(1) 步）vs RNN 顺序计算（O(n) 步）**。长程依赖 + GPU 友好。1 行答完。

---

## 📚 参考来源

1. **Transformer 原始论文**：Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit et al. *Attention Is All You Need*. NeurIPS 2017. https://arxiv.org/abs/1706.03762
2. **GPT-3（in-context learning 奠基）**：Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah et al. *Language Models are Few-Shot Learners*. NeurIPS 2020. https://arxiv.org/abs/2005.14165
3. **Scaling Laws**：Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B. Brown et al. *Scaling Laws for Neural Language Models*. 2020. https://arxiv.org/abs/2001.08361
4. **Chinchilla 定律**：Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch et al. *Training Compute-Optimal Large Language Models*. NeurIPS 2022. https://arxiv.org/abs/2203.15556
5. **InstructGPT / RLHF**：Long Ouyang, Jeff Wu, Xu Jiang, Diogo Almeida et al. *Training Language Models to Follow Instructions with Human Feedback*. NeurIPS 2022. https://arxiv.org/abs/2203.02155
6. **DPO（替代 RLHF）**：Rafael Rafailov, Archit Sharma, Eric Mitchell, Stefano Ermon et al. *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*. NeurIPS 2023. https://arxiv.org/abs/2305.18290
7. **LLaMA（开源 LLM 标杆）**：Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet et al. *LLaMA: Open and Efficient Foundation Language Models*. 2023. https://arxiv.org/abs/2302.13971
8. **Chain-of-Thought**：Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma et al. *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS 2022. https://arxiv.org/abs/2201.11903
9. **RoFormer (RoPE)**：Jianlin Su, Yu Lu, Shengfeng Pan, Bo Wen, Yunfeng Liu. *RoFormer: Enhanced Transformer with Rotary Position Embedding*. Neurocomputing 2024. https://arxiv.org/abs/2104.09864
10. **DeepSeek-V2 / MLA**：DeepSeek-AI. *DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model*. 2024. https://arxiv.org/abs/2405.04434

---

← [返回: 基础概念](../README.md)