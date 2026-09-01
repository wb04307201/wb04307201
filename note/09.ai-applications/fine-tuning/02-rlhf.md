<!--
module:
  parent: ai
  slug: ai/rlhf
  type: article
  category: 主模块子文章
  summary: RLHF 完整流水线：SFT → Reward Model → PPO
  depth: ⭐⭐⭐⭐⭐
-->

# RLHF（Reinforcement Learning from Human Feedback）

> ⬅️ [返回 LLM 对齐专题](../README.md)

> **一句话定位**：RLHF = **用人类偏好训练 Reward Model，再用 PPO 优化 LLM**。OpenAI 2022 年 InstructGPT 论文的核心方法，**GPT-4 / Claude 3 等顶级模型的标准对齐方法**。

---

## 📐 完整 3 步流水线

```text
Step 1: SFT（监督微调）
   高质量指令-回答对 → 微调 LLM
   ↓
Step 2: Reward Model 训练
   人类对多个回答排序 → 训练打分模型
   ↓
Step 3: PPO 强化学习
   用 RM 作为奖励信号 + KL 约束 → 优化 LLM
```

**为什么需要这 3 步？**

- **Step 1 SFT** 提供基础指令遵循能力（让模型"听得懂话"）
- **Step 2 RM** 把人类偏好蒸馏成可微信号（让模型"知道好坏"）
- **Step 3 PPO** 用 RM 信号优化策略（让模型"输出好东西"）

---

## 🧮 数学公式

### Step 2: Reward Model 损失

```python
# 偏好对 (prompt, y_chosen, y_rejected)
loss = -log sigmoid(r(y_chosen) - r(y_rejected))
# RM 学会"y_chosen 得分 > y_rejected 得分"
```

### Step 3: PPO 目标

```python
# LLM 的对数概率比
ratio = exp(log π(y|x) - log π_old(y|x))

# PPO 目标
objective = E[min(ratio * R, clip(ratio, 1-ε, 1+ε) * R)] - β * KL(π || π_ref)
#  R = Reward Model 打分
#  KL 约束：不让 LLM 偏离太远
```

**关键技巧**：

- **Reward Hacking**：RM 可能被 LLM 钻空子（高分低质）→ 加 KL 约束
- **Value Head**：Critic 网络估计期望回报
- **Generalized Advantage Estimation (GAE)**：优势函数估计

---

## 🧮 深入推导

### 完整 PPO 目标（含 KL 惩罚）

```text
L_PPO(θ) = E_(x,y)~D [
    min(
        r_t(θ) · Â_t,
        clip(r_t(θ), 1-ε, 1+ε) · Â_t
    )
] - β · KL(π_θ || π_ref)
```

其中：
- `r_t(θ) = π_θ(a_t|s_t) / π_θ_old(a_t|s_t)` — 新旧策略概率比
- `Â_t` — GAE（Generalized Advantage Estimation）估计的优势函数
- `KL(π_θ || π_ref)` — 与 SFT 模型（SFT 后的 ref policy）的 KL 散度
- `β` — KL 系数，越大越保守

### Advantage 估计（GAE）

```text
Â_t = Σ_(l=0)^∞ (γλ)^l δ_(t+l)
δ_t = r_t + γ V(s_(t+1)) - V(s_t)
```

其中：
- `r_t` = `R_RM(y_t)` = RM 打分（per-token level 通常用最后一个 token 的 reward）
- `V(s_t)` = Value Model（Critic）的状态价值估计
- `γ ∈ [0,1]` = 折扣因子（一般 = 1）
- `λ ∈ [0,1]` = GAE 平滑参数（一般 0.95）

### Reward Model 损失（Bradley-Terry 模型）

```text
L_RM(φ) = - E_(x, y_w, y_l) ~ D_preference [
    log σ( r_φ(x, y_w) - r_φ(x, y_l) )
]
```

其中 `σ` 是 sigmoid，`r_φ` 是 RM 的标量输出。这是 Bradley-Terry pairwise 比较模型的标准形式。

---

## 📊 关键超参数

| 超参数 | 典型值 | 说明 |
|--------|--------|------|
| KL 系数 β | 0.05-0.2 | 越大越保守 |
| Clip range ε | 0.1-0.2 | PPO 截断范围 |
| Learning rate | 1e-5（actor）/ 5e-6（critic）| LLM 和 Value 分别 |
| Batch size | 64-512 | 越大越稳定 |
| PPO epochs | 2-4 | 每 batch 训练轮数 |

---

## 📈 实战：LLaMA-2 RLHF 训练

```text
硬件：1024 x A100，训练 21 天
数据：100 万人类偏好对（HH-RLHF + 自建）
Reward Model：6B 参数（Vicuna-style ranking）
PPO 训练：70B 模型 + 6B RM + 6B Value Model
效果：HumanEval 29.3% → 48.1%（接近 GPT-4）
```

---

## 🛠️ 实操代码：HuggingFace TRL PPOTrainer

TRL 是 HuggingFace 官方 RLHF 工具链（13k+ stars，2024），完整支持 PPO 训练：

```python
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from transformers import AutoTokenizer

# 1. 加载 4 个模型
model = AutoModelForCausalLMWithValueHead.from_pretrained("Qwen/Qwen2-7B")
ref_model = AutoModelForCausalLMWithValueHead.from_pretrained("Qwen/Qwen2-7B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-7B")
reward_model = load_reward_model("reward-model-path")

# 2. PPO 配置
config = PPOConfig(
    learning_rate=1e-5,           # actor
    mini_batch_size=4,
    batch_size=64,
    ppo_epochs=2,
    kl_coef=0.1,                  # β
    cliprange=0.2,                # ε
    gamma=1.0,
    lam=0.95,
    vf_coef=0.1,                  # value loss 权重
)

ppo_trainer = PPOTrainer(
    config=config,
    model=model,
    ref_model=ref_model,
    tokenizer=tokenizer,
)

# 3. 训练循环
for batch in dataloader:
    # a) 生成回答（policy rollout）
    responses = ppo_trainer.generate(batch["input_ids"])

    # b) Reward Model 打分
    rewards = reward_model(batch["input_ids"], responses)

    # c) PPO 更新
    stats = ppo_trainer.step(
        queries=batch["input_ids"],
        responses=responses,
        scores=rewards,
    )
```

**4 个模型协同**：policy（actor）+ ref（冻结的 SFT 模型）+ reward model（冻结）+ value head（critic）。

---

## ⚠️ 3 大挑战

| 挑战 | 原因 | 缓解 |
|------|------|------|
| **训练不稳定** | PPO 训练 4 个模型（actor/critic/ref/RM） | 调 LR + KL 系数 |
| **Reward Hacking** | RM 被打分高低 ≠ 真实好坏 | 多样化 RM 训练数据 |
| **计算成本高** | 4 个模型 1024 卡 21 天 | 用 LoRA PPO 节省 |

---

## 🕰️ 演进史时间线（2022 → 2024）

```text
2022 Q1  • InstructGPT（OpenAI）
      - 首次完整定义 RLHF 三阶段
      - 175B SFT → 6B RM → 175B PPO
      - 核心论文：https://arxiv.org/abs/2203.02155

2022 Q3  • Anthropic Constitutional AI（RLAIF）
      - 用 AI 反馈替代人类反馈
      - 减少 90%+ 人类标注成本

2023 Q1  • LLaMA-2 Chat（Meta）
      - 首个开源 RLHF 全流程
      - 100 万偏好对 + 双 RM（helpfulness + safety）
      - "Llama 2: Open Foundation and Fine-Tuned Chat Models"

2023 Q3  • GPT-4（OpenAI）
      - RLHF + RBRMS（Rule-Based Reward Models）
      - 多 RM 集成（helpfulness / safety / factuality）

2024 Q1  • Llama-3 / Qwen2
      - SFT + DPO + PPO 三阶段混合
      - "DPO 后 PPO"（iterative DPO）成为新范式

2024 Q3  • DeepSeek-R1（DeepSeek）
      - GRPO（Group Relative Policy Optimization）
      - 不需要 Critic 网络，单卡友好
      - 纯 RL 也能产生推理能力

2024 Q4  • Claude 3.5 / GPT-4o
      - Constitutional AI + RLHF + 在线反馈
      - 实时人类反馈（online RLHF）
```

---

## 🏢 真实案例

### 案例 1：OpenAI InstructGPT（2022）

原始 InstructGPT 论文（Ouyang et al.）是 RLHF 的奠基工作：

```text
数据规模：
  SFT 数据：13K 高质量标注（标注员手写）
  RM 数据：33K 偏好对（标注员对 SFT 模型 4-9 个回答排序）
  PPO 数据：31K prompts（无标注，纯 RM 信号）

硬件：
  SFT：32 x V100，训练 1 天
  RM：32 x V100，训练 1 天
  PPO：32 x V100，训练 2 天

效果（175B SFT 模型 vs GPT-3 175B）：
  - 输出有用性 +85%
  - 真实性 +25%
  - 有害性 ↓ 2x
  - InstructGPT 175B 在人类偏好上优于 GPT-3 175B
```

**关键洞察**：33K 偏好对足以训练出强大的 RM；不一定要百万级数据。

---

### 案例 2：LLaMA-2 Chat（Meta, 2023）

首个开源 RLHF 全流程工业级实现：

```text
硬件：1024 x A100 80G
训练时长：21 天
RM 训练数据：1M+ 人类偏好对
RM 数量：2 个（helpfulness + safety）
PPO 训练：70B 模型 + 6B RM + 6B Value Model

效果（70B 模型）：
  HumanEval：29.3% → 48.1%
  MMLU：63.4% → 68.9%
  TruthfulQA：40.6% → 50.3%
```

详见 Meta AI 官方论文 + 技术报告。

---

### 案例 3：HuggingFace TRL（开源 RLHF 工具库）

TRL（[huggingface/trl](https://github.com/huggingface/trl)）是开源社区 RLHF 事实标准：

```python
from trl import (
    SFTTrainer,         # Step 1
    RewardTrainer,      # Step 2
    PPOTrainer,         # Step 3
)

# 三阶段训练示例
# Stage 1: SFT
sft_trainer = SFTTrainer(model=base_model, ...)
sft_trainer.train()

# Stage 2: RM
rm_trainer = RewardTrainer(model=base_model, ...)
rm_trainer.train()

# Stage 3: PPO
ppo_trainer = PPOTrainer(
    model=sft_model,
    ref_model=sft_model,        # 冻结
    reward_model=rm_model,       # 冻结
    ...
)
ppo_trainer.train()
```

---

### 案例 4：DeepSeek-R1（GRPO 替代 PPO）

DeepSeek-R1（2024.12）提出 **GRPO（Group Relative Policy Optimization）**，去掉 Critic 网络：

```text
传统 PPO：policy + ref + reward + value（4 模型）
GRPO：policy + ref + reward（3 模型，无 Value Head）

优势：
  - 显存节省 25%+
  - 训练更稳定
  - 推理任务上效果与 PPO 持平甚至更好
```

GRPO 用「同一 prompt 的多个回答相对评分」替代 Advantage 估计，是 PPO 的高效变体。

---

### 案例 5：Anthropic RLAIF（Constitutional AI）

Anthropic 用 **AI 反馈** 替代人类反馈，大幅降低标注成本：

```text
Step 1: SFT（人类标注 helpful + harmless 数据）
Step 2: Self-Critique（AI 根据宪法原则批评自己输出）
Step 3: AI 生成偏好对（chosen = 修改后的好回答）
Step 4: RM 训练（在 AI 偏好对上）
Step 5: RL（AI feedback + RM 信号）
```

**优势**：人类标注减少 90%+，且 AI 反馈在 harmlessness 维度上比人类更一致。

详见 [Constitutional AI](04-constitutional-ai.md)。

---

## 🔗 兄弟章节

- **本专题**：[SFT](01-sft.md) / [DPO](03-dpo.md) / [新方法](05-newer-methods.md)
- **L2 栈**：[推理优化大专题](../llm-inference/llm-inference-optimization/README.md)
- **咬文嚼字**：面试深挖（⚠️ 待 Phase 1+ 迁入；占位 `../../../12.interview/11.ai/agent-performance-evaluation/`）

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ RLHF 训练用强化学习很难 | ✅ 主要是工程问题，4 个模型协同 |
| ❌ Reward Model 越准越好 | ✅ 过于精准反而易被 hacking |
| ❌ PPO 一定优于 DPO | ✅ DPO 在小模型上已接近 PPO |
| ❌ RLHF 训练完还需要 SFT | ✅ 顺序是 SFT → RM → PPO，不是循环 |
| ❌ RLHF 数据越多越好 | ✅ 33K InstructGPT 偏好对足以训练强 RM |
| ❌ RM 是从零训练 | ✅ 通常从 SFT 模型初始化 + 加 regression head |
| ❌ PPO 一定要用 Value Head | ✅ GRPO / RLOO 等无 Critic 变体也能工作 |
| ❌ KL 系数越大越好 | ✅ 过大 → 退化为 SFT；过小 → Reward Hacking |

---

## 🔗 跨模块反向链

- **08.ai-foundations**：[Transformer 注意力](../../08.ai-foundations/03-transformer/transformer-architecture.md) RM 通常基于 Transformer 最后一层 hidden state + regression head；强化学习基础 PPO 的策略梯度理论。
- **03.data-stack**：[分布式训练](../../08.ai-foundations/04-llm/llm-basics.md) RLHF 4 模型在 ZeRO-3 / FSDP 下的显存切分；[推理优化](../rag/vector-search-algorithms/README.md) PPO rollout 阶段的 KV-cache 复用。
- **12.interview**：[RLHF vs DPO 对比](../../12.interview/11.ai/llm-alignment/README.md) 面试高频题；[Reward Hacking](../../12.interview/11.ai/llm-alignment/README.md) 经典面试陷阱。
- **13.story**：[阿明餐厅 - 顾客打分](../../13.story/36-rag-retrieval-augmented-generation.md) 用餐厅顾客打分类比 RM 训练。

← [返回 LLM 对齐专题](../README.md)

---

## 🛠️ 实操：Reward Model 训练

RM 训练通常从 SFT 模型初始化 + 加 scalar regression head：

```python
from trl import RewardTrainer, RewardConfig
from transformers import AutoModelForSequenceClassification

# 1. 加载 SFT 模型作为 base
model = AutoModelForSequenceClassification.from_pretrained(
    "./sft-model",
    num_labels=1,                          # 输出标量
    problem_type="regression",
)

# 2. RM 配置
config = RewardConfig(
    output_dir="./reward-model",
    num_train_epochs=2,
    per_device_train_batch_size=8,
    learning_rate=1e-5,
    max_length=2048,
    bf16=True,
    gradient_checkpointing=True,
)

# 3. 数据格式：(input_ids_chosen, input_ids_rejected)
# 数据集来自 UltraFeedback / Anthropic HH-RLHF
trainer = RewardTrainer(
    model=model,
    args=config,
    train_dataset=preference_dataset,        # {"input_ids_chosen": ..., "input_ids_rejected": ...}
    tokenizer=tokenizer,
)
trainer.train()
```

**关键技巧**：
- RM 初始 loss 应在 `ln(2) ≈ 0.693`（随机猜测）
- Loss 降到 0.5 说明 RM 学到偏好
- 训练时监控 chosen-rejected 分数差（应递增）

---

## 📈 RLHF 评估方法

| 维度 | 指标 | 说明 |
|------|------|------|
| **有用性** | AlpacaEval / MT-Bench | vs GPT-4 胜率 |
| **真实性** | TruthfulQA | 减少幻觉 |
| **无害性** | HarmBench / AdvBench | 抵御恶意 prompt |
| **人类偏好** | Chatbot Arena Elo | 真实用户投票 |
| **RM 准确性** | Pairwise Accuracy | RM 对偏好对的预测准确率 |
| **KL 偏离** | `KL(π || π_ref)` | 不应过大（一般 < 10 nats） |

---

## 🔥 常见踩坑 / Debug

| 现象 | 原因 | 解决 |
|------|------|------|
| PPO loss 震荡 | LR 过大 / KL 系数过小 | LR 减半 / β 加倍 |
| Reward 一直涨但输出变差 | Reward Hacking | 加 KL 约束 / 多 RM 集成 |
| Value loss 不下降 | Critic 学习率不够 | Critic LR 加倍（5e-6 → 1e-5）|
| 生成文本长度失控 | RM 偏好长回答 | 加 length normalization |
| 训练 2 天无进展 | PPO 步数过多 | 减 PPO epochs 到 1-2 |
| 中文乱码 / 输出格式错 | RM 训练数据未涵盖 | 补 RM 训练数据 |
| 模型对 prompt 过敏感 | SFT 模型不够稳 | 加 SFT 训练 epoch |
| 显存爆炸 | 4 模型同时加载 | 用 LoRA-PPO / 8-bit 优化器 |

---

## 🆚 RLHF vs DPO vs GRPO 对比

| 维度 | RLHF (PPO) | DPO | GRPO |
|------|-----------|-----|------|
| **提出** | OpenAI 2022 | Stanford 2023 | DeepSeek 2024 |
| **训练模型数** | 4（actor+critic+ref+RM）| 2（policy+ref）| 3（policy+ref+reward）|
| **价值网络** | 必须 | 不要 | 不要 |
| **超参数数** | 5+ | 1（β）| 2（β+group_size）|
| **训练稳定性** | 低 | 高 | 中 |
| **显存开销** | 4-8x | 2x | 2.5x |
| **效果** | 略强 | 接近 | 推理任务持平甚至更强 |
| **代表模型** | GPT-4 / Claude 3 | Llama-3 / Zephyr | DeepSeek-R1 |

---

## 🏭 工业部署：RLHF 训练成本与硬件

```text
训练 70B 模型 + 6B RM + 6B Value（参考 LLaMA-2）：

  显存需求：
    Policy（70B）：  ~140 GB（bf16）
    Reference（70B）：~140 GB（冻结，可卸载）
    Reward Model（6B）：~12 GB
    Value Model（6B）：~12 GB
    Optimizer state：~280 GB（Adam，全参）
    总计：~580 GB → 8 x A100 80G（ZeRO-3 拆分）

  时间成本：
    1024 x A100 80G，21 天 = ~50 万 GPU 小时
    折合云成本：~$1.5M（按 $3/GPU·h 计）

  节省方案：
    LoRA PPO：policy 只训 LoRA（<1% 参数）→ 显存降到 1/3
    GRPO：去掉 Value Model → 节省 25% 显存
    ZeRO-3 + CPU offload：单节点多卡可行
```

**实战建议**：
- 7B 模型 + LoRA + 单机 8 卡 A100：可行
- 70B 模型 + 全参 RLHF：必须多机 + 千卡级
- 推荐路径：**7B/13B LoRA PPO 验证 → 70B 全参 RLHF**

---

## 📚 参考来源

1. **Training language models to follow instructions with human feedback**：Long Ouyang et al. *InstructGPT 论文，OpenAI 2022*. https://arxiv.org/abs/2203.02155
2. **Proximal Policy Optimization Algorithms**：John Schulman et al. *PPO 算法原始论文，OpenAI 2017*. https://arxiv.org/abs/1707.06347
3. **Llama 2: Open Foundation and Fine-Tuned Chat Models**：Hugo Touvron et al. *Meta 2023*. https://arxiv.org/abs/2307.09288
4. **Constitutional AI: Harmlessness from AI Feedback**：Yuntao Bai et al. *Anthropic 2022*. https://arxiv.org/abs/2212.08073
5. **DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models**：Zhipu AI 2024 *GRPO 算法原始论文*. https://arxiv.org/abs/2402.03300
6. **DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning**：DeepSeek-AI 2024. https://arxiv.org/abs/2501.12948
7. **Bradley-Terry Model**：Ralph Allan Bradley & Milton E. Terry 1952 *Pairwise 比较模型基础*. https://link.springer.com/article/10.1007/BF02295932
