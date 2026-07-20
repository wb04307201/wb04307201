<!--
module:
  parent: ai
  slug: ai/newer-alignment-methods
  type: article
  category: 主模块子文章
  summary: KTO/IPO/SimPO/ORPO/RFT 2024+ 新对齐算法
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

## 🔗 兄弟章节

- **本专题**：[RLHF](02-rlhf.md) / [DPO](03-dpo.md) / [Constitutional AI](04-constitutional-ai.md)
- **L2 栈**：[推理优化大专题](../../02-technology-stack/llm-inference-optimization/README.md)
- **咬文嚼字**：[面试深挖](../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ RLHF 永远 SOTA | ✅ 2024 后 DPO 变体（SimPO/ORPO）已接近 |
| ❌ 偏好数据越多越好 | ✅ 5-10 万高质量 > 百万低质量 |
| ❌ 没有 ref 模型效果差 | ✅ SimPO 无 ref 已超 DPO |
| ❌ KTO 是 DPO 的简化版 | ✅ 基于行为经济学，数学完全不同 |
| ❌ 5 种方法可以混用 | ✅ 不同方法可能冲突（loss 叠加需谨慎） |

← [返回 LLM 对齐专题](../README.md)