<!--
module:
  parent: ai
  slug: ai/dpo
  type: article
  category: 主模块子文章
  summary: DPO 直接偏好优化：跳过 Reward Model
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

## 🔗 本专题兄弟章节

| # | 章节 | 一句话定位 |
|---|------|-----------|
| 1 | [SFT](01-sft.md) | 监督微调 = 所有对齐方法的基础（InstructGPT 2022） |
| 2 | [RLHF](02-rlhf.md) | Reward Model + PPO 强化学习（4 模型协同） |
| 3 | [DPO](03-dpo.md) | 直接偏好优化，跳过 Reward Model（闭式解） |
| 4 | [Constitutional AI](04-constitutional-ai.md) | 用 AI 原则替代人类反馈（Anthropic 2022） |
| 5 | [新方法](05-newer-methods.md) | KTO/IPO/SimPO/ORPO 2024+ |
| 6 | [PEFT/LoRA](06-peft-lora.md) | 参数高效微调 = 用 <1% 参数适配大模型（DoRA 强 LoRA 5-10%） |

- **L2 栈**：[推理优化大专题](../../02-technology-stack/llm-inference-optimization/README.md)
- **咬文嚼字**：[面试深挖](../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ DPO 永远不如 RLHF | ✅ 中小模型上已接近（Llama-3 验证）|
| ❌ DPO 不需要高质量偏好数据 | ✅ DPO 同样依赖人类偏好质量 |
| ❌ β 越大越好 | ✅ 太大 → 接近 ref = 退化为 SFT |
| ❌ DPO 可以完全替代 RLHF | ✅ SOTA（GPT-4）仍用 RLHF 或 DPO+RLHF 混合 |

← [返回 LLM 对齐专题](../README.md)