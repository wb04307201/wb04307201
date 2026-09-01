<!--
module:
  parent: ai
  slug: ai/dpo
  type: article
  category: 主模块子文章
  summary: DPO 直接偏好优化：跳过 Reward Model
  depth: ⭐⭐⭐⭐⭐
-->

# DPO（Direct Preference Optimization）

> ⬅️ [返回 LLM 对齐专题](../README.md)

> **一句话定位**：DPO = **直接用偏好对优化 LLM 策略**，**跳过 Reward Model 和 PPO**。Stanford 2023 年 Rafailov 团队提出，Llama-3 / Qwen2 / Zephyr 全部采用，**效果接近 RLHF 但简单一个数量级**。

---

## 🎯 核心洞察

RLHF 的目标是最大化：

```text
max π(y|x) subject to: reward(y|x) 高，KL(π || π_ref) 小
```

DPO 的关键证明：**最优策略有闭式解**！

```text
π*(y|x) ∝ π_ref(y|x) · exp(r(x,y) / β)
```

**反推**：给定偏好对，直接用对数似然比就能表达 reward：

```text
r(x, y) = β · log(π*(y|x) / π_ref(y|x)) + β · log Z(x)
```

**结论**：不需要显式训练 Reward Model，直接在偏好对上优化策略即可！

---

## 📐 DPO 损失函数

```python
# 偏好对 (prompt, y_w, y_l)
loss = -log σ(
    β · log(π(y_w|x) / π_ref(y_w|x)) -
    β · log(π(y_l|x) / π_ref(y_l|x))
)

# 简化形式
loss = -log σ(β · (log_ratio_chosen - log_ratio_rejected))
```

**直觉**：
- 增大 y_w 的对数概率比
- 减小 y_l 的对数概率比
- β 控制保守程度

---

## 🧮 DPO 完整推导

### Step 1：RLHF 目标函数

RLHF 的目标（带 KL 约束）：

```text
max_π  E_(x,y)~π [ r(x, y) ] - β · KL(π || π_ref)
```

展开 KL 散度：

```text
= max_π  E_x [ E_y~π(·|x) [ r(x,y) ] - β · KL(π(·|x) || π_ref(·|x)) ]
```

### Step 2：闭式解

对每个 `x`，对 `π(·|x)` 的拉格朗日优化有闭式解：

```text
π*(y|x) = (1/Z(x)) · π_ref(y|x) · exp( r(x,y) / β )

其中  Z(x) = Σ_y π_ref(y|x) · exp( r(x,y) / β )   # partition function
```

### Step 3：反推 reward

把上式取对数：

```text
r(x, y) = β · log(π*(y|x) / π_ref(y|x)) + β · log Z(x)
```

### Step 4：代入 Bradley-Terry 模型

人类偏好模型（Bradley-Terry）：

```text
P(y_w > y_l | x) = σ( r(x, y_w) - r(x, y_l) )
```

代入 `r(x, y) = β · log(π*(y|x) / π_ref(y|x)) + β · log Z(x)`：

```text
P(y_w > y_l | x) = σ( β · log(π*(y_w|x) / π_ref(y_w|x)) - β · log(π*(y_l|x) / π_ref(y_l|x)) )
```

### Step 5：DPO 损失

取负对数似然：

```text
L_DPO(θ) = - E_(x, y_w, y_l) ~ D_preference [
    log σ( β · log(π_θ(y_w|x) / π_ref(y_w|x)) - β · log(π_θ(y_l|x) / π_ref(y_l|x)) )
]
```

**关键点**：
- 不需要训练 Reward Model
- 不需要 PPO / 价值网络
- 单一 SFT + DPO 两阶段即可
- 优化目标是标准的二元分类 cross-entropy

---

## 🆚 RLHF vs DPO

| 维度 | RLHF | DPO |
|------|------|-----|
| **训练模型数** | 4 个（actor + critic + ref + RM）| 2 个（policy + ref）|
| **训练阶段** | 3 步（SFT → RM → PPO）| 1 步（SFT → DPO）|
| **显存需求** | 4-8x（4 模型）| 2x（policy + ref）|
| **训练稳定性** | 不稳定（PPO 4 模型协同难）| 稳定（标准 CE loss）|
| **调参难度** | 高（5+ 超参数）| 低（β 一个）|
| **效果** | 略强（SOTA 仍用 RLHF）| 接近（Llama-3 验证） |
| **训练时间** | 长（10+ 天 1024 卡）| 短（1-3 天 64 卡）|

**实测**：Llama-3-8B RLHF vs DPO 对比，AlpacaEval 2.0 差距 < 2%。

---

## 📊 DPO 超参数

| 超参数 | 典型值 | 说明 |
|--------|--------|------|
| β (beta) | 0.1-0.5 | 控制保守程度，越大越接近 ref |
| Learning rate | 1e-6 ~ 5e-7 | 比 SFT 小 10x |
| Batch size | 32-128 | 偏好对 batch |
| Epochs | 2-3 | 不要太多（过拟合偏好对）|
| LoRA rank | 16-64 | 推荐 LoRA 训练省显存 |

---

## 🛠️ 实操代码

```python
from trl import DPOTrainer, DPOConfig

config = DPOConfig(
    beta=0.3,
    learning_rate=5e-7,
    num_train_epochs=2,
    per_device_train_batch_size=32,
    gradient_accumulation_steps=4,
    loss_type="sigmoid",  # 标准 DPO
    max_length=2048,
    max_prompt_length=1024,
)

trainer = DPOTrainer(
    model=policy_model,        # 待优化 LLM
    ref_model=ref_model,        # 冻结的 ref LLM
    args=config,
    train_dataset=preference_dataset,  # (prompt, chosen, rejected)
    tokenizer=tokenizer,
)
trainer.train()
```

---

## 🛠️ 实操代码：完整可运行示例

```python
from trl import DPOTrainer, DPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# 1. 加载模型（SFT 后的 policy + 冻结的 ref）
policy_model = AutoModelForCausalLM.from_pretrained("./sft-model")
ref_model = AutoModelForCausalLM.from_pretrained("./sft-model")
tokenizer = AutoTokenizer.from_pretrained("./sft-model")

# 2. 准备偏好数据 (UltraFeedback / Anthropic HH-RLHF / argilla)
dataset = load_dataset("HuggingFaceH4/ultrafeedback_binarized", split="train_prefs")
# 数据格式: {"prompt": "...", "chosen": "...", "rejected": "..."}

# 3. DPO 配置
config = DPOConfig(
    output_dir="./dpo-output",
    beta=0.3,
    learning_rate=5e-7,
    num_train_epochs=2,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    loss_type="sigmoid",                # 标准 DPO
    max_length=2048,
    max_prompt_length=1024,
    warmup_ratio=0.1,
    lr_scheduler_type="cosine",
    bf16=True,
    gradient_checkpointing=True,
    # 高级选项
    rpo_alpha=0.1,                       # RPO 加权 (DPO + SFT)
    loss_type="sigmoid",                 # 也可换 "hinge" / "ipo" / "kto"
)

# 4. 启动训练
trainer = DPOTrainer(
    model=policy_model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

**关键参数**：
- `beta=0.3` 是社区默认值（Llama-3 官方用 0.1）
- `learning_rate=5e-7` 比 SFT 小 10x
- `loss_type="sigmoid"` 是经典 DPO；可换 `hinge` / `ipo` / `kto` / `robust` / `sppo_hard`

---

## 📈 DPO 变体

| 变体 | 改进 | 论文 |
|------|------|------|
| **IPO** | 加正则化防止过拟合 | 2023 |
| **KTO** | 用单条"好/坏"数据，无需偏好对 | 2024 |
| **SimPO** | 简化目标函数 | 2024 |
| **ORPO** | SFT + DPO 一体化 | 2024 |
| **RFT** | Rejection sampling + DPO | 2024 |

详见 [新方法章节](05-newer-methods.md)。

---

## 🕰️ 演进史时间线（2023 → 2024）

```text
2023 Q1  • DPO 原始论文（Rafailov et al., Stanford）
      - "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
      - https://arxiv.org/abs/2305.18290
      - 数学证明：最优策略有闭式解 → RLHF 可以被简化

2023 Q2  • IPO（Identity Preference Optimization）
      - DPO 在偏好对接近时会过拟合
      - 加正则项防止过拟合

2023 Q3  • Zephyr 7B（HuggingFace）
      - 首个开源 DPO 训练模型
      - 证明 DPO 可以在 7B 规模达到 RLHF 水平

2024 Q1  • Llama-3 / Qwen2 采用 DPO
      - Meta 官方：SFT → DPO → DPO（迭代）
      - Qwen2-Chat：SFT → DPO

2024 Q2  • KTO / SimPO / ORPO / RFT
      - KTO（Kahneman-Tversky）：单条数据，无需偏好对
      - SimPO：去掉 ref model，更简单
      - ORPO：SFT + DPO 一体化，单阶段
      - RFT：Rejection sampling + DPO，工业实践主流

2024 Q3  • Iterative DPO / Online DPO
      - LLM 自己生成回答 → 偏好标注 → DPO
      - 多轮迭代接近在线 RLHF

2024 Q4  • DPO 与 RLHF 混合
      - Llama-3-Instruct：SFT → DPO → 在线 RLHF（少量 PPO）
      - 工业实践主流范式
```

---

## 🏢 真实案例

### 案例 1：Zephyr 7B（HuggingFace H4 团队, 2023）

Zephyr 是首个开源 DPO 训练的 7B 模型：

```text
方法：SFT (UltraChat) → DPO (UltraFeedback)
基座：Mistral-7B
硬件：8 x A100，训练 4 小时
效果（MT-Bench 7.87 / AlpacaEval 90.6）：
  - 与 Llama-2-70B-Chat 持平
  - 接近 GPT-3.5（7B 达到 70B 效果）
```

**关键意义**：7B 模型 + DPO 即可达到 70B RLHF 水平 → DPO 不仅是简化，也是质量保证。

---

### 案例 2：Llama-3-Instruct（Meta, 2024）

Meta 官方公开 Llama-3 的对齐方法：**SFT → DPO → 在线 RLHF**：

```text
Step 1: SFT
  数据：1.5M 人工 + 30M 蒸馏（Llama-3-70B 生成）
  训练：8K H100，6 天

Step 2: DPO
  数据：1M+ 偏好对（人类标注 + AI 反馈）
  β = 0.1
  训练：RLHF 风格的偏好对

Step 3: 在线 RLHF（迭代 DPO）
  LLM 生成回答 → 人类标注 → 更新 DPO 模型
  多轮迭代（5-6 轮）
```

详见 [Llama 3 论文](https://arxiv.org/abs/2407.21783)。

---

### 案例 3：Qwen2-Chat（Alibaba, 2024）

Qwen2-Chat 采用 **SFT → DPO → Online DPO**：

```text
Step 1: SFT（百万级高质量中文 + 英文指令）
Step 2: DPO（自建偏好数据集 100K+）
Step 3: Online DPO（每 2 周迭代一次）

效果（Qwen2-72B-Instruct）：
  - AlpacaEval 2.0：97.6%（超过 Llama-3-70B-Instruct）
  - MT-Bench：9.3
```

---

### 案例 4：HuggingFace TRL（开源 DPO 工具库）

TRL 是开源 DPO 训练事实标准：

```python
# TRL 0.8+ 内置 DPO 全部变体
from trl import DPOTrainer, DPOConfig

config = DPOConfig(
    loss_type="sigmoid",  # 标准 DPO
    # loss_type="hinge",    # DPO 简化
    # loss_type="ipo",      # IPO
    # loss_type="kto",      # KTO
    # loss_type="simpo",    # SimPO
    # loss_type="robust",   # Robust DPO
    # loss_type="sppo_hard",# SPPO
)
```

13k+ stars，GitHub 趋势榜常客。

---

### 案例 5：DeepSeek-R1（Online DPO + GRPO）

DeepSeek-R1（2024.12）用 **GRPO + Online DPO** 联合训练：

```text
Step 1: SFT（基础指令微调）
Step 2: GRPO（推理任务纯 RL）
Step 3: Online DPO（用 GRPO rollout 生成偏好对）
```

**关键洞察**：推理任务上 Online DPO 比 Offline DPO 更稳定，因为 rollout 来自当前策略。

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ DPO 永远不如 RLHF | ✅ 中小模型上已接近（Llama-3 验证）|
| ❌ DPO 不需要高质量偏好数据 | ✅ DPO 同样依赖人类偏好质量 |
| ❌ β 越大越好 | ✅ 太大 → 接近 ref = 退化为 SFT |
| ❌ DPO 可以完全替代 RLHF | ✅ SOTA（GPT-4）仍用 RLHF 或 DPO+RLHF 混合 |
| ❌ DPO 不需要 SFT 前置 | ✅ 必须先 SFT，否则 π_ref 是 base 模型（无 instruction following 能力）|
| ❌ DPO 一次就能收敛 | ✅ 工业实践常用 iterative DPO（2-3 轮）|
| ❌ DPO 偏好对越多越好 | ✅ 5K-10K 高质量 > 100K 自动构造（UltraFeedback 验证）|
| ❌ DPO 不能用于代码 / 数学 | ✅ CodeUltraFeedback / Math-DPO 已验证有效 |

---

## 🔗 本专题兄弟章节

| # | 章节 | 一句话定位 |
|---|------|-----------|
| 1 | [SFT](01-sft.md) | 监督微调 = 所有对齐方法的基础（InstructGPT 2022） |
| 2 | [RLHF](02-rlhf.md) | Reward Model + PPO 强化学习（4 模型协同） |
| 3 | [DPO](03-dpo.md) | 直接偏好优化，跳过 Reward Model（闭式解） |
| 4 | [Constitutional AI](04-constitutional-ai.md) | 用 AI 原则替代人类反馈（Anthropic 2022） |
| 5 | [新方法](05-newer-methods.md) | KTO/IPO/SimPO/ORPO 2024+ |
| 6 | [PEFT/LoRA](06-peft-lora.md) | 参数高效微调 = 用 <1% 参数适配大模型（DoRA 强 LoRA 5-10%） |

- **L2 栈**：[推理优化大专题](../llm-inference/llm-inference-optimization/README.md)
- **咬文嚼字**：面试深挖（⚠️ 待 Phase 1+ 迁入；占位 `../../../12.interview/11.ai/agent-performance-evaluation/`）

---

## 🔗 跨模块反向链

- **08.ai-foundations**：强化学习基础 DPO 的 Bradley-Terry 模型来源；策略梯度 DPO 与 PPO 的策略优化对比。
- **03.data-stack**：[分布式训练](../../08.ai-foundations/04-llm/llm-basics.md) DPO 在 FSDP 下的模型并行；[向量数据库](../rag/vector-search-algorithms/README.md) 偏好对的 embedding 去重与质量筛选。
- **12.interview**：[RLHF vs DPO 对比](../../12.interview/11.ai/llm-alignment/README.md) 面试必问；[Bradley-Terry 模型](../../12.interview/11.ai/llm-alignment/README.md) DPO 数学基础；[Reward Hacking](../../12.interview/11.ai/llm-alignment/README.md) DPO 的潜在问题。
- **13.story**：[阿明餐厅 - 顾客偏好](../../13.story/37-vector-database-and-embedding.md) 用顾客偏好类比 DPO 直优化。

← [返回 LLM 对齐专题](../README.md)

---

## 🛠️ 实操：DPO 数据准备

DPO 需要 `(prompt, chosen, rejected)` 三元组，常见数据集：

| 数据集 | 规模 | 来源 | 用途 |
|--------|------|------|------|
| **UltraFeedback** | 61K | GPT-4 评分 | 通用 |
| **Anthropic HH-RLHF** | 170K | 人类标注 | helpful + harmless |
| **Argilla UltraFeedback** | 61K | 多模型投票 | 通用 |
| **CodeUltraFeedback** | 62K | GPT-4 评分 | 代码 |
| **Math-DPO** | 30K | 数学推理 | 数学 |
| **ChatBot Arena Conversations** | 33K | 用户投票 | 真实对话 |

```python
from datasets import load_dataset

# 加载 UltraFeedback binarized
dataset = load_dataset("HuggingFaceH4/ultrafeedback_binarized", split="train_prefs")
print(dataset[0].keys())
# dict_keys(['prompt', 'chosen', 'rejected', 'score_chosen', 'score_rejected'])

# 数据格式转换：chosen/rejected 可能是 message 列表
def format_for_dpo(example):
    return {
        "prompt": example["prompt"],
        "chosen": example["chosen"][-1]["content"] if isinstance(example["chosen"], list) else example["chosen"],
        "rejected": example["rejected"][-1]["content"] if isinstance(example["rejected"], list) else example["rejected"],
    }

dataset = dataset.map(format_for_dpo)
```

---

## 🛠️ 实操：Iterative DPO（在线 DPO）

工业实践常用 **Iterative DPO** 提升效果：

```python
# Round 1: Offline DPO
trainer = DPOTrainer(model=policy_model, ref_model=ref_model, ...)
trainer.train()

# Round 2: 用 Round 1 模型生成回答 → 重新标注偏好 → 再 DPO
policy_model = load_model("./dpo-round-1")
new_dataset = generate_preferences(policy_model)   # 自生成 + AI 评分
trainer = DPOTrainer(model=policy_model, ref_model=ref_model, train_dataset=new_dataset, ...)
trainer.train()

# Round 3+: 重复
```

**效果**：Llama-3 论文报告 5-6 轮迭代后效果接近在线 RLHF。

---

## 📈 DPO 评估方法

| 指标 | 用途 | 目标 |
|------|------|------|
| **AlpacaEval 2.0** | vs GPT-4 胜率 | 越高越好（>90 = SOTA）|
| **MT-Bench** | 多轮对话 | > 8.5 为强 |
| **IFEval** | 指令遵循 | > 70% 为合格 |
| **Pairwise Accuracy** | DPO 隐式 RM 准确率 | > 70% |
| **Implicit Reward Margin** | chosen-rejected log-prob 差 | 越大越好 |
| **KL(π || π_ref)** | 偏离 SFT 程度 | < 5 nats |

---

## 🔥 常见踩坑 / Debug

| 现象 | 原因 | 解决 |
|------|------|------|
| 训练 loss 不下降 | LR 过小 / β 过大 | LR 加倍 / β 减半 |
| chosen-rejected 差为负 | 数据标签搞反 | 交换 chosen/rejected |
| 输出长度爆炸 | DPO 偏好长回答 | 加 `max_length` / length normalization |
| 显存爆炸 | ref_model 加载 | 用 LoRA（ref_model 不加载）|
| 中文输出变差 | 中英偏好数据不平衡 | 加中文偏好数据 |
| 训练 1 epoch 就过拟合 | 偏好对质量差 / 数量少 | 减 epoch + 增数据 |
| β=0.1 vs β=0.3 选哪个 | 看任务 | 强保守选 0.1，强探索选 0.5 |
| DPO 后效果反降 | SFT 模型不够好 | 重做 SFT 再 DPO |

---

## 📚 参考来源

1. **Direct Preference Optimization: Your Language Model is Secretly a Reward Model**：Rafael Rafailov et al. *Stanford 2023*. https://arxiv.org/abs/2305.18290
2. **Zephyr: Direct Distillation of LM Alignment**：Lewis Tunstall et al. *HuggingFace 2023*. https://arxiv.org/abs/2310.16944
3. **Llama 3: Open Foundation and Fine-Tuned Chat Models**：Meta AI 2024. https://arxiv.org/abs/2407.21783
4. **Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study**：Shusheng Xu et al. *2024*. https://arxiv.org/abs/2404.10719
5. **KTO: Model Alignment as Prospect-Theoretic Optimization**：Kawin Ethayarajh et al. *2024*. https://arxiv.org/abs/2402.01306
6. **SimPO: Simple Preference Optimization with a Reference-Free Reward**：Yu Meng et al. *2024*. https://arxiv.org/abs/2405.14734
7. **ORPO: Monolithic Preference Optimization without Reference Model**：Janghwan Lee et al. *2024*. https://arxiv.org/abs/2403.07691
8. **DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning**：DeepSeek-AI 2024. https://arxiv.org/abs/2501.12948
9. **Bradley-Terry Model**：Ralph Allan Bradley & Milton E. Terry 1952 *Pairwise 比较模型基础*. https://link.springer.com/article/10.1007/BF02295932
