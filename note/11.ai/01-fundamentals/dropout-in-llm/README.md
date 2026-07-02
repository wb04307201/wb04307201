<!--
module:
  parent: ai
  slug: ai/dropout-in-llm
  type: article
  category: 主模块子文章
  summary: Dropout 在 LLM 中的反直觉：训练范式 + 任务特性 + 规模效应
-->

# LLM 中的 Dropout —— 训练范式与正则化策略

← 返回 [LLM 基础](../README.md)

> Dropout 在 CV 小模型时代是标配，但在 LLM 大模型时代被弃用。本文从训练范式、任务特性、规模效应 3 个层面系统讲清楚这个反直觉现象，并梳理 LLM 的替代正则化方案。

> **面试场景**：这是高频 AI 面试题——很多面试者会下意识回答"防止过拟合"，但答案远不止于此。面试版（30 秒 / 60 秒话术）见 [咬文嚼字·11.ai/dropout-in-llm](../../../13.split-hairs/11.ai/dropout-in-llm/README.md)。

---

## 一、为什么 CV 时代 Dropout 是标配

### 1.1 Dropout 的工作原理（一句话）

训练时随机将部分神经元输出置零，推理时使用全部神经元。**等价于训练大量子网络的集成**。

### 1.2 CV 模型为什么需要 Dropout

- 图像数据：1-100 万张，参数量 10M-100M
- 数据/参数比 = 100-10000，**严重过拟合风险**
- Dropout 0.5 可以显著减少过拟合

### 1.3 Dropout 的两大假设

1. **特征冗余**：相邻像素/特征表示相似，丢掉一些不影响
2. **子网络集成**：每个子网络学到不同模式，集成后泛化更强

## 二、为什么 LLM 时代 Dropout 被弃用

### 2.1 训练范式反转

| 维度 | CV 模型 | LLM |
|------|---------|-----|
| 数据量 | 1-100 万 | 1T+ tokens |
| 参数量 | 10M-100M | 1B-1T |
| 数据/参数比 | ~100-10000 | ~1-10 |
| 风险 | 过拟合 | 欠拟合（容量不够）|
| 正则化需求 | 强 | 弱 |

**核心反转**：CV 是"参数太多学过头"，LLM 是"数据虽多但还学不够"。Dropout 限制容量，在 LLM 上是负作用。

### 2.2 任务特性反转

**CV 任务的特征冗余**：
- 图像相邻像素相关性 > 0.9
- Dropout 一个像素，人类眼睛看不出来
- 特征图天然有空间冗余

**LLM 任务的强依赖性**：
- token 之间有句法/语义强依赖
- Dropout 一个 token，下一个 token 的预测就崩了
- 序列任务没有"局部冗余"的概念

**反直觉类比**：
- CV Dropout = 让厨师做菜时少放 1g 盐（人类尝不出）
- LLM Dropout = 让厨师做菜时少放某道主料（直接翻车）

### 2.3 规模效应（历史演进）

| 模型 | 参数量 | Dropout 使用 | 时代 |
|------|--------|-------------|------|
| GPT-1 (2018) | 117M | embedding + attention output 0.1 | 早期 |
| GPT-2 (2019) | 1.5B | 减小到 0.1 | 过渡期 |
| GPT-3 (2020) | 175B | 几乎不用，仅 residual | 转折点 |
| LLaMA-7B (2023) | 7B | **完全不用** | 现代 |
| Mistral-7B (2023) | 7B | **完全不用** | 现代 |
| Qwen-72B (2024) | 72B | **完全不用** | 现代 |

**10B+ 模型不用 Dropout 已是业界共识**。

### 2.4 经验法则

| 模型规模 | 数据规模 | Dropout 建议 |
|---------|---------|-------------|
| < 100M | < 1M | Dropout 0.5（CV 标配）|
| 100M-1B | 1-10B | Dropout 0.1-0.3 |
| 1B-10B | 10-100B | Dropout 0.1（仅关键层）|
| 10B+ | 100B+ | **不用 Dropout** |
| RLHF PPO | < 1B | Dropout 0.1（policy/value head）|

## 三、LLM 的替代正则化方案

### 3.1 参数级正则化（Weight Decay）

所有 LLM 必备，典型值 0.1。

```python
# PyTorch 示例
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=1e-4,
    weight_decay=0.1  # L2 正则化
)
```

**作用**：控制参数幅度，防止个别权重过大。

### 3.2 激活分布正则化（RMSNorm / LayerNorm）

所有 LLM 必备。

**作用**：标准化每层激活分布，让训练更稳定。

### 3.3 稀疏激活（MoE）

**Mixtral 8x7B / DeepSeek-V3 / Qwen-MoE** 等模型使用。

```python
# 简化示意：每次只激活部分专家
router_weights = softmax(W @ hidden_state)
top_k_weights, top_k_indices = topk(router_weights, k=2)
output = sum(weight * expert(hidden_state) for weight, expert in zip(top_k_weights, top_k_experts))
```

**天然正则化**：每次只激活部分参数，等价于隐式 Dropout 但更高效。

### 3.4 数据级正则化（高质量数据）

**比 Dropout 更根本**：
- 数据清洗（去重 / 去毒）
- 数据过滤（高质量 source）
- 数据配比（领域均衡）

LLaMA 论文核心结论："**数据质量 > 模型架构 > Dropout**"。

### 3.5 训练技巧正则化

| 技巧 | 作用 |
|------|------|
| Learning Rate Warmup | 防止早期训练不稳定 |
| Cosine Decay | 后期收敛更平稳 |
| Gradient Clipping | 防止梯度爆炸 |
| Mixed Precision (bf16/fp16) | 隐式正则化（精度有限）|

## 四、Dropout 在 LLM 中的例外场景

### 4.1 RLHF 阶段（小模型 PPO）

- Policy network / Value network：参数量小（GPT-4 也是几亿参数）
- 训练数据少（人类反馈样本）
- 过拟合风险高 → **会加 Dropout 0.1**

### 4.2 输出层（lm_head）

部分 LLM 在最后的 lm_head 层加少量 Dropout（防止词表过拟合）。

### 4.3 Embedding 层（特定场景）

小模型 + 罕见词场景，可能在 token embedding 层加 Dropout。

## 五、与"驾驭演进"主线的关联

LLM 不用 Dropout，本质是**训练范式的升级**——和 [驾驭演进主线（Prompt → Context → Harness → Loop）](../../04-architecture/llm-control-evolution/README.md) 是同一个故事的不同维度：

- **Prompt 阶段**：人在调 Prompt（小数据 / 人工调优）
- **Dropout 时代**：训练时正则化（小数据 / CV 模型）
- **LLM 时代**：抛弃 Dropout，靠数据 + 规模 + 架构（大数据 / 大模型）
- **Harness 时代**：训练完后的行为约束

**范式升级的内核**：每一步都把"约束"的责任从更细的层级（神经元级 Dropout）转移到更宏观的层级（数据 / 架构 / 规范）。

## 六、相关章节

**面试题**：
- [咬文嚼字·11.ai/dropout-in-llm（30/60/90 秒话术）](../../../13.split-hairs/11.ai/dropout-in-llm/README.md)

**同主模块**：
- [LLM 基础](../llm-basics/README.md)
- [Transformer 架构](../transformer/README.md)
- [神经网络层原理](../neural-layers/README.md)
- [Dense vs MoE](../dense-vs-moe/README.md)

**架构视角**：
- [11.ai 驾驭演进主线](../../04-architecture/llm-control-evolution/README.md)

---

## 📊 本节统计

- **覆盖深度**：4 个层面（范式 / 任务 / 规模 / 例外）
- **历史演进**：5 个模型（GPT-1 → LLaMA → Qwen-72B）
- **替代方案**：5 类（weight decay / RMSNorm / MoE / 数据 / 训练技巧）
- **关联章节**：2 大类（面试题 + 主模块）

---

> 📅 2026-07-02 · 11.ai/01-fundamentals · ⭐⭐⭐⭐
