<!--
module:
  parent: ai
  slug: ai/sft
  type: article
  category: 主模块子文章
  summary: SFT 监督微调：所有对齐方法的基础
-->

# SFT（Supervised Fine-Tuning）

> ⬅️ [返回 LLM 对齐专题](../README.md)

> **一句话定位**：SFT = **用高质量指令-回答对微调预训练 LLM**，让模型从"续写"变成"对话"。**所有对齐方法的基础**——RLHF / DPO / Constitutional AI 都在 SFT 之后做。

---

## 🎯 为什么需要 SFT

预训练 LLM 的本质是"续写器"：

```
输入："今天天气"
输出："今天天气很好，我打算去公园散步..."
```

SFT 之后变成"助手"：

```
输入："今天天气"
输出："北京今天晴 25°C，适合户外活动。请问您想了解哪方面？"
```

---

## 📐 SFT 训练流程

```
Step 1: 准备数据
  格式：(instruction, input?, output)
  来源：人工编写 + Self-Instruct 生成 + 蒸馏

Step 2: 模板化
  Alpaca 格式：
  """
  Below is an instruction that describes a task...
  
  ### Instruction:
  {instruction}
  
  ### Response:
  {output}
  """
  
Step 3: 微调
  损失 = -log P(output | instruction, input)
  
Step 4: 评估
  人工评估 + AlpacaEval / MT-Bench
```

---

## 📊 高质量 SFT 数据源

| 来源 | 规模 | 质量 | 成本 |
|------|------|------|------|
| **OpenHermes 2.5** | 100 万 | ⭐⭐⭐⭐ | $0（开源）|
| **UltraChat** | 150 万 | ⭐⭐⭐ | $0 |
| **ShareGPT** | 9 万 | ⭐⭐⭐⭐⭐ | $0（清洗后）|
| **WizardLM Evol-Instruct** | 25 万 | ⭐⭐⭐⭐ | $0 |
| **Self-Instruct** | 5-50 万 | ⭐⭐⭐ | $10 GPT-4 API |
| **人工标注** | 1-10 万 | ⭐⭐⭐⭐⭐ | $0.5-5/条 |

**5 万高质量 ShareGPT > 100 万自动生成**。

---

## ⚙️ SFT 关键超参数

| 超参数 | 典型值 | 备注 |
|--------|--------|------|
| Learning rate | 1e-5 ~ 5e-5 | 比预训练小 10x |
| Batch size | 32-128 | 越大越稳定 |
| Epochs | 2-3 | 多了过拟合 |
| Sequence length | 2048-4096 | 长文任务需要更长 |
| LoRA rank | 16-64 | 推荐 LoRA 训练 |
| Warmup ratio | 0.03-0.1 | 防止早期震荡 |

---

## 🛠️ 实操：LLaMA-Factory 一键 SFT

```python
from llamafactory import Trainer

# 配置
config = {
    "model_name_or_path": "meta-llama/Llama-2-7b-hf",
    "dataset": "alpaca_zh",
    "template": "llama2",
    "lora_rank": 16,
    "lora_alpha": 32,
    "learning_rate": 1e-4,
    "num_train_epochs": 3,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "max_length": 2048,
}

trainer = Trainer(config)
trainer.train()
```

---

## 📈 SFT 局限性

| 局限 | 原因 | 解决 |
|------|------|------|
| **天花板效应** | 模仿人类标注 | RLHF / DPO 进一步优化 |
| **数据偏差** | 标注员偏好 | 多样化标注团队 |
| **幻觉** | 训练数据有错 | RAG + RLHF |
| **指令理解弱** | 简单指令 | Self-Instruct 复杂化 |
| **风格单一** | 模仿一种风格 | 多源数据混合 |

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ SFT 数据越多越好 | ✅ 5 万高质量 > 100 万低质量 |
| ❌ SFT 后模型会变笨 | ✅ 正确 SFT 仅调整格式和风格 |
| ❌ SFT 可以完全替代 RLHF | ✅ SFT 是 RLHF 的必要前置 |
| ❌ SFT 只能用人工标注 | ✅ Self-Instruct + 蒸馏可自动生成 |
| ❌ SFT 学习率应该和预训练一致 | ✅ 应小 10x（1e-5 vs 1e-4） |

---

## 🔗 兄弟章节

- **本专题**：[RLHF](02-rlhf.md) / [DPO](03-dpo.md) / [新方法](05-newer-methods.md)
- **L3 同级**：[Harness Engineering](../harness-engineering/README.md) 顺带提
- **咬文嚼字**：[面试深挖](../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)

← [返回 LLM 对齐专题](../README.md)