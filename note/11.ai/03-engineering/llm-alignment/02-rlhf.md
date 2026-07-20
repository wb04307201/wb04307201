<!--
module:
  parent: ai
  slug: ai/rlhf
  type: article
  category: 主模块子文章
  summary: RLHF 完整流水线：SFT → Reward Model → PPO
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

## ⚠️ 3 大挑战

| 挑战 | 原因 | 缓解 |
|------|------|------|
| **训练不稳定** | PPO 训练 4 个模型（actor/critic/ref/RM） | 调 LR + KL 系数 |
| **Reward Hacking** | RM 被打分高低 ≠ 真实好坏 | 多样化 RM 训练数据 |
| **计算成本高** | 4 个模型 1024 卡 21 天 | 用 LoRA PPO 节省 |

---

## 🔗 兄弟章节

- **本专题**：[SFT](01-sft.md) / [DPO](03-dpo.md) / [新方法](05-newer-methods.md)
- **L2 栈**：[推理优化大专题](../../02-technology-stack/llm-inference-optimization/README.md)
- **咬文嚼字**：[面试深挖](../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ RLHF 训练用强化学习很难 | ✅ 主要是工程问题，4 个模型协同 |
| ❌ Reward Model 越准越好 | ✅ 过于精准反而易被 hacking |
| ❌ PPO 一定优于 DPO | ✅ DPO 在小模型上已接近 PPO |
| ❌ RLHF 训练完还需要 SFT | ✅ 顺序是 SFT → RM → PPO，不是循环 |

← [返回 LLM 对齐专题](../README.md)