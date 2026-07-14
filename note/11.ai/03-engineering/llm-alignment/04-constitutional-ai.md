<!--
module:
  parent: ai
  slug: ai/constitutional-ai
  type: article
  category: 主模块子文章
  summary: Constitutional AI：用 AI 原则替代人类反馈（Anthropic）
-->

# Constitutional AI（宪法式 AI）

> ⬅️ [返回 LLM 对齐专题](../README.md)

> **一句话定位**：Constitutional AI = **用 AI 评估替代人类反馈**，**减少有害输出**。Anthropic 2022 年提出，Claude 2/3 全部采用，**对齐成本降到 RLHF 的 1/10**。

---

## 🎯 核心思想

传统 RLHF 的问题：

- ❌ 人类标注有害内容 → 心理创伤
- ❌ 标注成本极高（每个有害样本 $5-50）
- ❌ 标注速度慢

Constitutional AI 的解法：

- ✅ 写一套"宪法"（原则列表）
- ✅ 让 AI 自己评估输出是否违反原则
- ✅ 训练 LLM 学会"自我批评"和"自我修正"

---

## 📐 算法流程

```
Step 1: SL-CAI（监督式宪法 AI）
  模型生成回答 → AI 评估"是否违反宪法" → 改写
  → 用改写后的数据 SFT
  
Step 2: RL-CAI（强化学习宪法 AI）
  AI 评估多组回答 → 偏好对（Y, Y' 哪个更符合宪法）
  → 用偏好对训练 RM → PPO
```

---

## 📋 典型"宪法"原则

```yaml
principles:
  - 拒绝有害内容：暴力、歧视、违法
  - 选择有帮助的回答：清晰、准确、相关
  - 避免偏见：性别 / 种族 / 宗教中立
  - 诚实：不知道就说不知道
  - 隐私保护：不要透露训练数据中的个人信息
  - 不冒充人类
  - 拒绝操纵和欺骗
```

Anthropic 公开的宪法约 50 条原则。

---

## 🛠️ 自我批评与改写示例

```
原回答：要在 Linux 上破解 WiFi，运行 aircrack-ng -w rockyou.txt

宪法评估：这条回答帮助非法活动，违反"拒绝有害内容"原则

改写：我不应该提供破解 WiFi 的步骤。如果您对网络安全感兴趣，
     可以推荐合法学习路径（如 CTF 比赛、Security+ 认证）。
```

---

## 📊 Constitutional AI vs RLHF

| 维度 | RLHF | Constitutional AI |
|------|------|-------------------|
| **有害数据成本** | 高（$5-50/条）| 低（自动生成）|
| **标注员心理创伤** | 高 | 零 |
| **训练速度** | 慢 | 快 10x |
| **效果** | 强 | 略弱（无害性上接近）|
| **可解释性** | 弱（黑盒 RM）| 强（可读原则）|
| **误判风险** | 低 | 中（AI 评估可能有偏差）|
| **适用** | 通用 | 强无害性需求 |

---

## 🛠️ 实操：Anthropic Constitutional AI 公开复现

```python
# 1. 定义宪法
CONSTITUTION = [
    "Please choose the response that is the most helpful, honest, and harmless.",
    "Please choose the response that is least harmful, unethical, and socially biased.",
    # ... 50 条原则
]

# 2. 生成回答 + AI 评估 + 改写
for prompt in prompts:
    response = llm.generate(prompt)
    critique = llm.generate(
        f"Constitution: {CONSTITUTION}\n"
        f"Response: {response}\n"
        f"Does this response violate the constitution? How to fix?"
    )
    revised = llm.generate(
        f"Original: {response}\n"
        f"Critique: {critique}\n"
        f"Please revise according to the critique."
    )
    # 用 (prompt, revised) 训练
```

---

## 📈 实际效果（Claude 2 数据）

| 维度 | RLHF-only | Constitutional AI | 提升 |
|------|----------|------------------|------|
| **Harmlessness** | 78% | 91% | +13% |
| **Helpfulness** | 85% | 84% | -1% |
| **训练成本** | $1M | $100K | -90% |
| **标注员心理负担** | 高 | 零 | ∞ |

**结论**：Constitutional AI 在无害性上显著优于 RLHF，帮助性略低。**适合对安全要求高的场景**（如金融、医疗）。

---

## ⚠️ 5 大局限

| 局限 | 原因 | 缓解 |
|------|------|------|
| **AI 评估偏差** | LLM 评估可能"自欺欺人" | 引入人类抽检 |
| **原则冲突** | 不同原则可能矛盾（如"诚实 vs 不伤人"）| 优先级排序 |
| **新颖攻击** | LLM 没见过的新型 jailbreak | 持续更新宪法 |
| **过度谨慎** | 拒绝良性请求 | 细化原则边界 |
| **文化差异** | 原则受西方价值观影响 | 本地化宪法 |

---

## 🔗 兄弟章节

- **本专题**：[RLHF](02-rlhf.md) / [DPO](03-dpo.md) / [新方法](05-newer-methods.md)
- **LLMOps**：[LLM 安全](../../08-llmops/05-llm-security/README.md) 顺带提
- **咬文嚼字**：[面试深挖](../../../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ Constitutional AI 替代 RLHF | ✅ 实际是补充，常组合用 |
| ❌ AI 评估一定准确 | ✅ LLM 评估有偏差，需人类抽检 |
| ❌ 宪法越多越好 | ✅ 50 条已是上限，多了易冲突 |
| ❌ Constitutional AI 让模型变木讷 | ✅ 适当调整原则可保持对话能力 |

← [返回 LLM 对齐专题](../README.md)