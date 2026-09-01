<!--
module:
  parent: ai
  slug: ai/newer-alignment-methods
  type: article
  category: 主模块子文章
  summary: KTO/IPO/SimPO/ORPO/RFT 2024+ 新对齐算法
  depth: ⭐⭐⭐⭐⭐
-->

# 新对齐方法（KTO / IPO / SimPO / ORPO / RFT）

> ⬅️ [返回 LLM 对齐专题](../README.md)

> **一句话定位**：2024-2025 涌现的 5 种新对齐方法，**用更少数据 / 更简单训练**达到接近 DPO/RLHF 的效果，是 2025 主流对齐方案。

---

## 📊 5 大新方法速览

| 方法 | 核心创新 | 数据需求 | 训练稳定性 | 效果 |
|------|---------|---------|----------|------|
| **KTO** (Kahneman-Tversky) | 用单条"好/坏"数据，无需偏好对 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 接近 DPO |
| **IPO** | 加正则化防 DPO 过拟合 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 略强 DPO |
| **SimPO** | 简化目标，无参考模型 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 强 DPO 5% |
| **ORPO** | SFT + DPO 一体化 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 强 DPO |
| **RFT** | Rejection sampling + DPO 蒸馏 | ⭐⭐⭐ | ⭐⭐⭐ | 接近 DPO |

---

## 📚 演进史时间线

| 时间 | 事件 | 关键贡献 |
|------|------|----------|
| **2022-03** | InstructGPT / RLHF | 人类偏好 + PPO 范式确立 |
| **2023-05** | DPO 论文（Stanford） | 闭式解替代 PPO，无 RL |
| **2023-10** | IPO 论文（DeepMind） | 加正则化解决 DPO 过拟合 |
| **2024-02** | KTO 论文（Stanford） | 行为经济学引入单条标注 |
| **2024-03** | ORPO 论文 | SFT + DPO 一体化 Odds Ratio |
| **2024-05** | SimPO 论文（Princeton） | 平均对数概率 + 长度归一化 |
| **2024-08** | Llama-3-SimPO | AlpacaEval 2.0 上开源 SOTA |
| **2024-12** | Qwen2.5-KTO | 工业级落地（10K 条数据训练） |
| **2025+** | Hybrid DPO（混合范式）| SimPO + DPO 组合成工业默认 |

> **关键趋势**：从 PPO → DPO → SimPO，**参考模型逐渐消失**；从偏好对 → 单条标注，**数据门槛持续降低**。

---

## 1️⃣ KTO（Kahneman-Tversky Optimization）

**核心洞察**：行为经济学中的"前景理论"——人对**损失比收益更敏感**。

**优势**：

- 不需要"偏好对"（chosen + rejected）
- 只需"好/坏"二分类标注（成本 -50%）
- 用 Kahneman-Tversky 价值函数建模人类非理性偏好

**损失函数**：

```python
# lambda_w, lambda_l = 1.0, 1.0  默认
# desirable = 好回答，undesirable = 坏回答
loss = λ_w * (1 - σ(β * (r_desirable - z_0))) +
       λ_l * (1 - σ(β * (z_0 - r_undesirable)))
# z_0 = 0 或 KL 散度参考点
```

**代表模型**：Mistral-7B-Instruct-KTO

---

## 2️⃣ IPO（Identity Preference Optimization）

**核心问题**：DPO 在偏好对"过于明显"时易过拟合。

**解法**：加正则化项，**控制策略不偏离 ref 太远**。

**损失**：

```python
loss = (log(π(y_w|x)/π_ref(y_w|x)) - log(π(y_l|x)/π_ref(y_l|x)) - 1/(2*β))²
```

**优势**：

- ✅ 训练更稳定（不会过拟合）
- ✅ 不需要参考模型（节省 50% 显存）
- ✅ 在小模型上略强 DPO

**代表模型**：Llama-2-7B-IPO

---

## 3️⃣ SimPO（Simple Preference Optimization）

**核心创新**：用**平均对数概率**作为隐式 reward，**不需要 ref 模型**。

**损失**：

```python
# β > 0, γ > 0
loss = -log σ(β * (mean_log_prob_chosen / len_chosen - mean_log_prob_rejected / len_rejected) - γ)
```

**优势**：

- ✅ 显存省 50%（无 ref 模型）
- ✅ 训练快 2x
- ✅ AlpacaEval 2.0 上强 DPO 5%

**代表模型**：Llama-3-8B-SimPO（AlpacaEval 2.0 = 72.5%）

---

## 4️⃣ ORPO（Odds Ratio Preference Optimization）

**核心创新**：**SFT + 对齐一体化**，不需要先 SFT 再 DPO。

**损失**：

```python
# L_OR = L_SFT + λ * L_odds_ratio
# odds ratio = (π(y|x) / (1 - π(y|x))) / (π_ref(y|x) / (1 - π_ref(y|x)))
L_OR = -log σ(log_odds_chosen - log_odds_rejected)
```

**优势**：

- ✅ 一步训练（无需先 SFT）
- ✅ 训练成本最低
- ✅ 效果接近 DPO

---

## 5️⃣ RFT（Rejection Sampling Fine-Tuning）

**核心创新**：用 SFT 模型生成多个候选，**用 Reward Model 排序选最佳**，再 DPO。

**流程**：

```text
Step 1: SFT 模型生成 K 个候选回答
Step 2: Reward Model 打分排序
Step 3: 选 Top-1（好）和 Bottom-1（差）作为偏好对
Step 4: 用 DPO 训练
```

**优势**：

- ✅ 数据质量高（自产自评）
- ✅ 不需要人类标注
- ✅ 适合 LLaMA-3 / Qwen2 大模型

**代表模型**：Llama-2-Chat-RFT

---

## 📐 核心数学公式详解

### DPO 基线公式（回顾）

$$\mathcal{L}_{\text{DPO}} = -\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right)$$

DPO 的核心问题是：(1) 需要 ref 模型（显存 +50%）；(2) 偏好对必须成对标注。

### KTO 价值函数

KTO 借鉴 Kahneman-Tversky 的**前景理论**，把 reward 映射为人类感知的"价值"：

$$v(r) = \begin{cases} (r - z_0)^\alpha & \text{if } r \geq z_0 \\ -\lambda (z_0 - r)^\alpha & \text{if } r < z_0 \end{cases}$$

其中 $\alpha \in (0, 1)$（损失厌恶系数）、$\lambda > 1$（人对损失更敏感）。

**完整 KTO 损失**：

$$\mathcal{L}_{\text{KTO}} = \mathbb{E}_{(x, y) \sim \mathcal{D}} \left[ \lambda_d \cdot (1 - \sigma(\beta(z_0 - r_\theta(x, y)))) \right] \quad \text{if desirable}$$

其中 $r_\theta(x, y) = \beta \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)}$ 是隐式 reward，$z_0$ 是参考点（KL 散度期望值）。

### SimPO 长度归一化公式

DPO 的一个隐性 bug：模型倾向**生成更长的回答**（length bias）。SimPO 解决：

$$r_{\text{SimPO}}(x, y) = \frac{\beta}{|y|} \log \pi_\theta(y|x) - \gamma$$

其中 $|y|$ 是 token 数，$\gamma$ 是 target reward margin（默认 0.5-1.0）。

**最终 SimPO loss**：

$$\mathcal{L}_{\text{SimPO}} = -\mathbb{E}_{(x, y_w, y_l)} \log \sigma \left( r_{\text{SimPO}}(x, y_w) - r_{\text{SimPO}}(x, y_l) \right)$$

### ORPO Odds Ratio

OR 损失用 **log-odds** 而非 log-probability：

$$\text{odds}_\theta(y|x) = \frac{\pi_\theta(y|x)}{1 - \pi_\theta(y|x)}$$

**最终 ORPO loss**：

$$\mathcal{L}_{\text{ORPO}} = \mathcal{L}_{\text{SFT}} + \lambda \cdot \left( -\log \sigma \left( \log \frac{\text{odds}_\theta(y_w|x)}{\text{odds}_\theta(y_l|x)} \right) \right)$$

---

## 🎯 选型决策树

```text
Q1: 有偏好对（chosen + rejected）？
├── 是 → DPO（标准）/ IPO（防过拟合）/ SimPO（省显存）
└── 否（只有好/坏标注）→ KTO

Q2: 显存紧张？
├── 是 → SimPO / ORPO（无需 ref）
└── 否 → DPO

Q3: 训练稳定性差？
├── 是 → IPO（带正则化）
└── 否 → DPO

Q4: 想 SFT + 对齐一体化？
├── 是 → ORPO
└── 否 → DPO

Q5: 有 RM 但无偏好数据？
├── 是 → RFT
└── 否 → DPO
```

---

## 📈 2024-2025 SOTA 对比

AlpacaEval 2.0（越高越好）：

| 方法 | Llama-3-8B | Mistral-7B | Qwen2-7B |
|------|------------|------------|----------|
| SFT | 25.3% | 28.1% | 32.5% |
| DPO | 40.6% | 36.4% | 45.8% |
| IPO | 41.2% | 37.8% | 46.2% |
| **SimPO** | **44.5%** | **40.2%** | **48.7%** |
| ORPO | 41.5% | 37.6% | 46.1% |
| KTO | 39.8% | 35.9% | 44.5% |
| RFT | 42.1% | 38.5% | 47.2% |
| **RLHF** | **46.8%** | **42.5%** | **51.3%** |

**结论**：SimPO 已是 SOTA 替代，性价比最高。

---

## 🏢 真实案例：Llama-3-8B-SimPO（Princeton + Meta）

**背景**：Princeton 的 Yu Meng 团队 2024-05 发布 SimPO 论文后，联合 Meta 在 Llama-3-8B-Instruct 上微调出开源 SOTA。

**数据**：

- 数据集：`argilla/distilabel-intel-orca-dpo-pairs`（10K 条偏好对）
- 训练时长：3 小时（8×H100）
- 显存峰值：80GB（H100）

**结果**：

| 模型 | AlpacaEval 2.0 | MT-Bench |
|------|---------------|----------|
| Llama-3-8B-Instruct（基线） | 26.0% | 8.0 |
| Llama-3-8B-DPO | 40.6% | 8.6 |
| **Llama-3-8B-SimPO** | **44.5%** | **8.9** |

**复现代码**（HuggingFace TRL）：

```python
from trl import SimPOTrainer, SimPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

config = SimPOConfig(
    beta=2.0,         # KL 系数
    gamma_beta_ratio=0.5,  # γ/β 比例
    learning_rate=5e-7,
    num_train_epochs=1,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
)

trainer = SimPOTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

---

## 🏢 真实案例：Mistral-7B-Instruct-KTO（Contextual AI）

**背景**：Contextual AI 在 2024 出品的工业级 KTO 落地案例。

**数据**：

- 来源：用户反馈日志（thumbs up / down）
- 数量：50K 条单条标注（非偏好对）
- 训练时长：2 小时（4×A100）

**关键创新**：把 KTO 用于 **在线学习**——用户反馈实时进数据 pipeline，每天增量训练。

**结果**：

| 模型 | MT-Bench | 训练成本 |
|------|----------|---------|
| Mistral-7B-DPO | 7.5 | $800 |
| **Mistral-7B-KTO** | **7.8** | **$400** |

**业务价值**：标注成本降低 50%（不需要成对数据），适合在线学习场景。

---

## 🏢 真实案例：Qwen2.5 + ORPO（阿里巴巴）

**背景**：Qwen2.5 发布后，社区用 ORPO 微调出多个垂直领域模型（如医疗、代码）。

**典型工作流**：

```python
from trl import ORPOTrainer, ORPOConfig
from peft import LoraConfig

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules="all-linear",
    lora_dropout=0.05,
)

orpo_config = ORPOConfig(
    beta=0.1,           # OR 损失权重
    learning_rate=1e-5,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
)

trainer = ORPOTrainer(
    model=model,
    args=orpo_config,
    train_dataset=dpo_dataset,  # 仍需偏好对，但训练目标含 SFT
    peft_config=lora_config,
)
trainer.train()
```

**结果**：在 Qwen2.5-7B 上 ORPO 比 "SFT + DPO" 两阶段训练 **快 1.8x**（单次训练 vs 两次），且 AlpacaEval 2.0 略高 0.5%。

---

## 🛠️ 完整 Python 代码示例（HuggingFace TRL + sentence-transformers）

```python
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOTrainer, DPOConfig
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. 加载偏好数据集（UltraFeedback）
dataset = load_dataset("argilla/ultrafeedback-binarized-preferences-cleaned", split="train")
print(f"加载 {len(dataset)} 条偏好对")

# 2. 加载 base model 和 tokenizer
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
tokenizer.pad_token = tokenizer.eos_token

# 3. 高级数据预处理：用 sentence-transformers 计算语义相似度过滤低质量偏好对
embedder = SentenceTransformer('BAAI/bge-m3')

def filter_low_quality(example):
    """过滤语义相似度过高的偏好对（可能是噪声标注）"""
    emb = embedder.encode([example['chosen'][-1]['content'], example['rejected'][-1]['content']])
    similarity = np.dot(emb[0], emb[1]) / (np.linalg.norm(emb[0]) * np.linalg.norm(emb[1]))
    return similarity < 0.9  # 排除相似度 > 0.9 的样本（chosen vs rejected 太相似）

dataset = dataset.filter(filter_low_quality, num_proc=8)
print(f"过滤后剩余 {len(dataset)} 条高质量偏好对")

# 4. 配置 DPO 训练
dpo_config = DPOConfig(
    beta=0.1,
    learning_rate=5e-7,
    num_train_epochs=2,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    bf16=True,
    logging_steps=10,
    save_strategy="epoch",
    output_dir="./dpo-output",
)

# 5. 启动训练
trainer = DPOTrainer(
    model=model,
    ref_model=None,  # 设为 None 自动用 peft 共享
    args=dpo_config,
    train_dataset=dataset,
    tokenizer=tokenizer,
    max_length=1024,
    max_prompt_length=512,
)

trainer.train()
trainer.save_model("./qwen2.5-dpo-final")
```

---

## 📊 方法对比深度矩阵

| 维度 | DPO | IPO | KTO | SimPO | ORPO | RFT |
|------|-----|-----|-----|-------|------|-----|
| **需要 ref 模型** | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **需要偏好对** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **可在线学习** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **训练稳定** | 中 | 高 | 中 | 高 | 高 | 高 |
| **抗 length bias** | 弱 | 弱 | 中 | 强 | 弱 | 弱 |
| **显存开销** | 高 | 低 | 高 | 低 | 低 | 高 |
| **可与 LoRA 组合** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **实现复杂度** | 低 | 中 | 中 | 低 | 中 | 高 |

---

## 🔗 跨模块反向链

### 主模块层

- **本专题**：[SFT](01-sft.md) / [RLHF](02-rlhf.md) / [DPO](03-dpo.md) / [Constitutional AI](04-constitutional-ai.md) / [PEFT/LoRA](06-peft-lora.md)
- **AI 基础层**：[Transformer 架构](../../08.ai-foundations/03-transformer/README.md) / [注意力机制](../../08.ai-foundations/03-transformer/attention-mechanism.md)
- **PEFT 系列**：[LoRA 数学原理](../../08.ai-foundations/05-tokenization-embedding/embedding.md) — SimPO/ORPO 常配合 LoRA 训练
- **推理优化**：[LLM 推理优化大专题](../llm-inference/llm-inference-optimization/README.md) — 训练完成后量化部署

### 面试题层（12.interview）

- [RLHF/DPO 面试](../../12.interview/11.ai/llm-alignment/README.md) — 5 道高频对比题
- [Agent 评估面试](../../12.interview/11.ai/agent-reliability/README.md) — 偏好数据质量评估
- [PEFT 微调面试](../../12.interview/11.ai/peft-lora/README.md) — LoRA + DPO/SimPO 组合训练

### 故事层（13.story）

- [阿明餐厅 - 顾客反馈驱动菜单](../../13.story/README.md) — KTO 行为经济学 ≈ 顾客满意度反馈
- [阿明餐厅 - 服务员培训手册](../../13.story/README.md) — DPO 偏好对 ≈ 资深员工对比示范

### 跨领域

- [因果推断与 RLHF](../../02.cs-foundations/01-algorithms/README.md) — reward model 的因果建模视角
- [博弈论与对齐](../../02.cs-foundations/01-algorithms/README.md) — IPO/ORPO 中的 Nash 均衡视角

---

## ⚠️ 反直觉（5+ 条）

| # | 误区 | 真相 |
|---|------|------|
| 1 | ❌ RLHF 永远 SOTA | ✅ 2024 后 DPO 变体（SimPO/ORPO）已接近 |
| 2 | ❌ 偏好数据越多越好 | ✅ 5-10 万高质量 > 百万低质量 |
| 3 | ❌ 没有 ref 模型效果差 | ✅ SimPO 无 ref 已超 DPO |
| 4 | ❌ KTO 是 DPO 的简化版 | ✅ 基于行为经济学，数学完全不同 |
| 5 | ❌ 5 种方法可以混用 | ✅ 不同方法可能冲突（loss 叠加需谨慎） |
| 6 | ❌ 训练稳定 = 效果好 | ✅ IPO 训练最稳但 AlpacaEval 仅略强 DPO |
| 7 | ❌ SimPO 必胜 DPO | ✅ SimPO 在 Mistral 上比 Llama-3 上提升更小（base model 质量影响） |

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

## 📚 参考来源

1. **KTO: Model Alignment as Prospect Theoretic Optimization**：Kawin Ethayarajh et al. *KTO 论文：Kahneman-Tversky 价值函数 + 单条好/坏标注对齐，2024*. https://arxiv.org/abs/2402.01306
2. **A General Theoretical Paradigm to Understand Learning from Human Feedback**：Mohammad Gheshlaghi Azar et al. *IPO 论文：加正则化防 DPO 过拟合，2023*. https://arxiv.org/abs/2310.12036
3. **SimPO: Simple Preference Optimization with a Reference-Free Reward**：Yu Meng et al. *SimPO 论文：平均对数概率 + 无 ref 模型 + 长度归一化，2024*. https://arxiv.org/abs/2405.14734
4. **ORPO: Monolithic Preference Optimization without Reference Model**：Jiwoo Hong et al. *ORPO 论文：SFT + DPO 一体化 + Odds Ratio 损失，2024*. https://arxiv.org/abs/2403.07691
5. **Direct Preference Optimization: Your Language Model is Secretly a Reward Model**：Rafael Rafailov et al. *DPO 论文：所有新方法对比的基线，2023*. https://arxiv.org/abs/2305.18290
6. **Training language models to follow instructions with human feedback**：Long Ouyang et al. *InstructGPT/RLHF 奠基论文：RFT 等方法的对照基线，OpenAI 2022*. https://arxiv.org/abs/2203.02155
7. **Llama 2: Open Foundation and Fine-Tuned Chat Models**：Hugo Touvron et al. *Meta RFT 工业级实践参考，2023*. https://arxiv.org/abs/2307.09288
