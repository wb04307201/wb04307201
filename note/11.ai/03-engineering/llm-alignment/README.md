<!--
module:
  parent: ai
  slug: ai/llm-alignment
  type: index
  category: 主模块子文章
  summary: LLM 对齐专题（RLHF / DPO / PPO / Reward Model / Constitutional AI）
-->

# LLM 对齐专题（6 大方法）

> ⬅️ [返回 L3 工程实践](../README.md)

> **一句话定位**：LLM 对齐 = **让模型输出符合人类意图**。6 大方法：SFT → RLHF → DPO → Constitutional AI → KTO/IPO/SimPO → PEFT/LoRA。从"鹦鹉学舌"到"理解意图"的演进。

---

## 📚 6 大方法目录

| # | 章节 | 核心思想 | 论文 | 年份 |
|---|------|---------|------|------|
| 1 | [SFT](01-sft.md) | 监督微调 + 高质量指令数据 | InstructGPT | 2022 |
| 2 | [RLHF](02-rlhf.md) | Reward Model + PPO 强化学习 | InstructGPT | 2022 |
| 3 | [DPO](03-dpo.md) | 直接偏好优化，跳过 Reward Model | Stanford | 2023 |
| 4 | [Constitutional AI](04-constitutional-ai.md) | 用 AI 原则替代人类反馈 | Anthropic | 2022 |
| 5 | [KTO/IPO/SimPO](05-newer-methods.md) | 2024-2025 新对齐算法 | 多家 | 2024+ |
| 6 | [PEFT/LoRA/QLoRA](06-peft-lora.md) | 参数高效微调，0.2% 参数接近全参效果 | He et al. 2022 | 2022 |

---

## 🎯 对齐目标

| 目标 | 含义 | 衡量 |
|------|------|------|
| **Helpfulness** | 回答有用 | 人工评估 + 任务完成率 |
| **Harmlessness** | 无害（不输出有害内容） | 安全 benchmark |
| **Honesty** | 诚实（不知就说不知） | 幻觉率 |
| **Factuality** | 准确性 | RAG 评估 + 事实核查 |

**3H 原则**（Anthropic 提出）：Helpful + Harmless + Honest

---

## 📊 6 大方法横评

| 方法 | 训练成本 | 实施难度 | 效果 | 代表模型 |
|------|---------|---------|------|---------|
| SFT | 中 | ⭐ | 基础 | 所有 Instruct 模型 |
| RLHF | 高 | ⭐⭐⭐⭐ | 最强 | GPT-4 / Claude 3 |
| DPO | 低 | ⭐⭐ | 接近 RLHF | Llama-3 / Qwen2 |
| Constitutional AI | 高 | ⭐⭐⭐ | 强（无害性） | Claude 2+ |
| KTO/IPO/SimPO | 低 | ⭐⭐ | 接近 DPO | Mistral / Qwen2.5 |
| **PEFT/LoRA** | **低** | **⭐⭐** | **接近全参** | **LLaMA-2 / Qwen2.5** |

---

## 🧠 数学统一视角

所有对齐方法本质是 **学习一个 reward 函数**：

```text
SFT:     L = -log π(y|x)            # 最大似然
RLHF:    L = -E[log π(y|x)] + β·KL  # 期望奖励 + KL 约束
DPO:     L = -log σ(β·log(π_ref/π)·(y_w - y_l))  # 偏好对
KTO:     L = λ_w·σ(r_w) + λ_l·σ(-r_l)  # 价值函数
```

核心都是：**让"好的回答"概率高，"坏的回答"概率低**。

**横向关联**：所有对齐方法（SFT/RLHF/DPO/KTO）都依赖 **PEFT/LoRA** 才能在消费级显卡上平民化，详见 [PEFT/LoRA/QLoRA 章节](06-peft-lora.md)。

---

## 🔗 兄弟章节

- **L1 同级**：[Transformer 架构](../../01-fundamentals/transformer/README.md) / [MoE](../../01-fundamentals/moe-architecture/README.md)
- **L2 栈**：[推理优化大专题](../../02-technology-stack/llm-inference-optimization/README.md)
- **LLMOps**：[08-llmops](../../08-llmops/README.md) — 安全 + 评测
- **L7 研究**：[知识蒸馏](../../07-research/distillation/README.md) — Teacher-Student 模型蒸馏，常与 SFT/RLHF 组合（先蒸馏降参，再对齐）
- **咬文嚼字**：[面试深挖](../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md) 顺带提

---

## ⚠️ 5 大反直觉

| 误区 | 真相 |
|------|------|
| ❌ SFT 已过时 | ✅ 仍是所有对齐方法的基础 |
| ❌ RLHF 永远最强 | ✅ DPO/KTO 已接近 RLHF 且更简单 |
| ❌ 对齐只关心无害 | ✅ 3H：有用 / 无害 / 诚实 |
| ❌ 对齐后模型变笨 | ✅ 正确对齐让模型更"听话"但不变笨 |
| ❌ 偏好数据越多越好 | ✅ 5-10 万高质量 > 百万低质量 |

← [返回 L3 工程实践](../README.md)