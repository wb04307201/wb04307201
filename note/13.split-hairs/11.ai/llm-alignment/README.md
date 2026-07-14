<!--
question:
  id: 11.ai-llm-alignment
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [11.ai, RLHF, DPO, PPO, Constitutional AI, 对齐, SFT]
-->

# LLM 对齐面试深挖（5 大核心）

> ⬅️ [返回 AI 咬文嚼字](../README.md) | [主模块深度专题](../../../11.ai/03-engineering/llm-alignment/README.md)

> **一句话定位**：5 大 LLM 对齐方法**面试深挖版**：SFT / RLHF / DPO / Constitutional AI / SimPO。

---

## 🎯 5 大核心题

### Q1：什么是 RLHF？3 步流水线是什么？

**陷阱**：
- ❌ 答"用人类反馈训练"（不够具体）
- ❌ 混淆训练模型数（actor/critic/ref/RM）

**30 秒话术**：
> "RLHF = **Reward Model + PPO** 强化学习。3 步：① SFT 监督微调 → ② 人类对回答排序训练 RM → ③ PPO 用 RM 分数 + KL 约束优化 LLM。"

**90 秒话术**：
> "OpenAI 2022 InstructGPT 论文提出。**4 个模型协同**：actor（待优化 LLM）+ critic（Value 网络估计回报）+ ref（冻结的 SFT 模型做 KL 约束）+ RM（人类偏好的打分模型）。PPO 目标 = E[min(ratio·R, clip(ratio, 1-ε, 1+ε)·R)] - β·KL(π||π_ref)。LLaMA-2 用 1024 张 A100 训 21 天，HumanEval 从 29% 涨到 48%。"

---

### Q2：DPO 为什么不需要 Reward Model？数学保证是什么？

**陷阱**：
- ❌ 答"用偏好对直接训练"（不理解闭式解）
- ❌ 不知道数学等价性证明

**30 秒话术**：
> "DPO 的关键证明：**最优策略有闭式解** π* ∝ π_ref · exp(r/β)，反推出 r = β·log(π*/π_ref)。所以**直接用偏好对优化对数概率比即可**，不需要显式训练 RM。"

**90 秒话术**：
> "Stanford 2023 Rafailov 等人证明：**最大化 RM 奖励 + KL 约束**等价于**最大化偏好对的似然**。DPO 损失 = -log σ(β·(log(π(y_w)/π_ref(y_w)) - log(π(y_l)/π_ref(y_l))))。只需 2 个模型（policy + ref），训练快 10x。Llama-3 验证 AlpacaEval 2.0 差距 < 2%。但 70B+ SOTA 仍用 RLHF（DPO 在大模型上易过拟合）。"

---

### Q3：Constitutional AI 和 RLHF 的本质区别？

**陷阱**：
- ❌ 答"用 AI 替代人类"（不够深）
- ❌ 不知道"自我批评"机制

**30 秒话术**：
> "RLHF 用**人类反馈**训练 RM；Constitutional AI 用**宪法原则 + AI 评估**替代人类。Anthropic 2022 提出，标注成本 -90%，Claude 2/3 全部采用。"

**90 秒话术**：
> "Constitutional AI 分 SL-CAI（监督式）+ RL-CAI（强化式）两步。**核心机制**：模型生成回答 → AI 评估是否违反宪法原则 → AI 改写 → 用改写数据训练。**50 条宪法**包括：拒绝有害内容、避免偏见、诚实等。**优势**：标注成本 $1M→$100K，零心理创伤。**劣势**：AI 评估可能偏差（自欺欺人），需人类抽检。**实际效果**：Claude 2 有害性 78%→91%，帮助性略降 1%。"

---

### Q4：SFT、RLHF、DPO 应该如何组合使用？

**陷阱**：
- ❌ 答"先用 SFT 再用 RLHF"（太笼统）
- ❌ 不知道顺序和数据需求

**30 秒话术**：
> "**SFT 必须先做**（基础），然后**二选一**：RLHF（4 模型，SOTA 但贵）或 DPO（2 模型，性价比高）。Constitutional AI 通常与 RLHF 组合。"

**90 秒话术**：
> "标准流水线：**SFT（5-10 万高质量指令）→ RLHF（100 万偏好对，4 模型）或 DPO（10-50 万偏好对，2 模型）**。SFT 用 LLaMA-Factory 一键训练；RLHF 需要 trl + accelerate + 4 卡 80G；DPO 只需 trl + 2 卡 24G。**2024-2025 趋势**：SimPO（无 ref 模型）已超 DPO，ORPO（SFT+DPO 一体化）兴起。**SOTA 仍用 RLHF**（GPT-4、Claude 3），但**开源首选 DPO/SimPO**。"

---

### Q5：为什么 RLHF 训练不稳定？3 大挑战是什么？

**陷阱**：
- ❌ 答"奖励难设计"（不准确）
- ❌ 不知道具体超参数

**30 秒话术**：
> "RLHF 不稳定源于**4 模型协同**：actor / critic / ref / RM。**3 大挑战**：① 训练不稳定（PPO 4 模型难协同）② Reward Hacking（RM 被钻空子）③ 计算成本高（4 模型 + 1024 卡 21 天）。"

**90 秒话术**：
> "**挑战 1：训练不稳定** —— PPO 4 个模型梯度相互影响，actor 学习率 1e-5，critic 5e-6，ratio 经常爆炸。**缓解**：调 LR + KL 系数 β（0.05-0.2）+ clip range ε（0.1-0.2）。**挑战 2：Reward Hacking** —— RM 可能被 LLM 钻空子（高分低质）。**缓解**：KL 约束 + 多样化 RM 训练数据 + RM Ensemble。**挑战 3：计算成本** —— LLaMA-2 70B 用 1024 卡 21 天。**缓解**：LoRA PPO（只调 0.1% 参数）+ ZeRO-3（节省显存 4x）。"

---

## 🔗 兄弟章节

- **主模块深度**：[llm-alignment](../../../11.ai/03-engineering/llm-alignment/README.md) — 5 大方法完整版
- **兄弟面试题**：[Agent 性能评估](../agent-performance-evaluation/README.md) 顺带提
- **餐厅叙事**：[12.story 对齐故事](../../../12.story/)（待补）

---

## 📊 5 题难度速查

| 题 | 难度 | 频率 | 关键数字 |
|---|------|------|---------|
| Q1 RLHF 3 步 | ⭐⭐⭐ | 高频 | 4 模型协同 |
| Q2 DPO 数学 | ⭐⭐⭐⭐⭐ | 高频 | 闭式解 |
| Q3 Constitutional AI | ⭐⭐⭐⭐ | 中频 | 成本 -90% |
| Q4 组合策略 | ⭐⭐⭐ | 高频 | SFT→RLHF/DPO |
| Q5 RLHF 挑战 | ⭐⭐⭐⭐ | 中频 | 1024 卡 21 天 |

← 返回 [AI 咬文嚼字](../README.md)