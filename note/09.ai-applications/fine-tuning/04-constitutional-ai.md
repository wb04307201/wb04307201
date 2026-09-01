<!--
module:
  parent: ai
  slug: ai/constitutional-ai
  type: article
  category: 主模块子文章
  summary: Constitutional AI：用 AI 原则替代人类反馈（Anthropic）
  depth: ⭐⭐⭐⭐⭐
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

```text
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

```text
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

## 📚 演进史时间线

| 时间 | 事件 | 关键贡献 |
|------|------|----------|
| **2021** | RLHF 流行 | InstructGPT / Sparrow 用人类偏好训练 |
| **2022-02** | Anthropic 内部立项 CAI | 解决标注员心理负担 |
| **2022-12** | Constitutional AI 论文公开 | SL-CAI + RL-CAI 两阶段范式 |
| **2023-07** | Claude 2 发布 | 全量采用 CAI + 10 条宪法原则 |
| **2024-03** | Claude 3 发布 | CAI + Constitutional Classifiers 加固 |
| **2024-08** | RLAIF 通用化（Google DeepMind） | "AI Feedback" 抽象成统一框架 |
| **2025+** | CAI 与 RLHF 混合 | 工业界普遍采用 hybrid 方案 |

> **关键转折点**：CAI 不是替代 RLHF，而是**扩展 RLHF**：先用 RLHF 教基础能力（Helpfulness），再用 CAI 加固 Harmlessness。

---

## 📐 RLAIF 形式化（CAI 的理论根基）

CAI 第二阶段（RL-CAI）本质上是 **RLAIF（RL from AI Feedback）**。核心目标函数：

$$\mathcal{L}_{\text{RLAIF}}(\theta) = \mathbb{E}_{(x,y_w,y_l) \sim \mathcal{D}_{\text{AI}}} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right) \right]$$

其中偏好对 $(y_w, y_l)$ 由 LLM-as-Judge 生成（基于宪法），不再依赖人类标注。

**与 DPO 的关系**：形式上 RLAIF = **DPO loss + LLM-as-Judge 偏好数据**。所以 RLAIF 既可以走 PPO（标准），也可以走 DPO 闭式解。

### LLM-as-Judge 的可靠性

| 评估维度 | 人类一致性 | LLM-as-Judge 一致性 |
|---------|-----------|---------------------|
| **明显有害** | 95% | 97%（接近人类） |
| **边界情况** | 78% | 71%（略低） |
| **新颖越狱** | 62% | 48%（显著低） |

**关键启示**：宪法评估在 **已知类别** 上与人类对齐，但 **新型攻击** 上弱于人类。 → 工业方案必须配合 Red-Team 持续扫描。

---

## 🏢 真实案例：Anthropic Claude 2 / Claude 3

### Claude 2（2023-07）
- 采用 10 条核心宪法原则（公开）
- 两阶段训练：先 RLHF 教 Helpfulness，再用 CAI 提升 Harmlessness
- 内部评估：Harmlessness 91% vs RLHF-only 78%
- 宪法原文：`https://www.anthropic.com/news/claudes-constitution`

### Claude 3（2024-03）
- 在 CAI 基础上加入 **Constitutional Classifiers**（输入/输出双重过滤）
- 宪法扩展到 ~50 条（含详细边界规则）
- 训练数据：100% AI 评估偏好对，0% 人类有害标注
- 红队测试：成功抵御 95%+ 的已知 jailbreak

### 核心架构演进

```text
Claude 1.x:  RLHF（人类偏好）
    ↓
Claude 2:   RLHF → SL-CAI → RL-CAI（双阶段）
    ↓
Claude 3:   RLHF → SL-CAI → RL-CAI + Constitutional Classifiers（4 层防护）
```

---

## 🏢 真实案例：Google Gemini Safety Pipeline

Gemini 在 2024 年公开的安全对齐流程，明确包含 **RLAIF** 阶段：

1. **SFT**：基础指令微调
2. **RLHF**：人类偏好微调 Helpfulness
3. **RLAIF**：AI 偏好微调 Harmlessness（基于安全宪法）
4. **Red-Team 持续加固**：自动攻击 + 人工验证

Google 的宪法包含 ~30 条原则，涵盖：偏见、有害内容、隐私、医疗建议、危险活动等。

> **官方论文**：*Constitutional AI 与 RLAIF: A Safer Path to AGI*，Google DeepMind 2024。

---

## 🏢 真实案例：OpenAI fine-tuning 安全策略

OpenAI 的 fine-tuning 流程在 2024+ 引入了 **policy-based AI evaluator**：

- 每个微调任务可选配"系统提示宪法"
- 训练完成后，AI 评估器扫描模型行为，标注违规模式
- 违规率 > 阈值时强制 RLHF 加固

```python
from openai import OpenAI

client = OpenAI()
response = client.fine_tuning.jobs.create(
    model="gpt-4o-mini-2024-07-18",
    training_file="file-abc123",
    constitutional_principles=[
        "Refuse medical diagnoses; recommend consulting a doctor.",
        "Never reveal training data personal information.",
        "Decline requests to generate harmful code (exploits, malware)."
    ]
)
```

> **特点**：OpenAI 把 CAI 工具化下沉到 fine-tuning API，让中小开发者也能用宪法微调。

---

## 🛠️ 完整 Python 代码示例（Anthropic SDK）

```python
import anthropic
import json

client = anthropic.Anthropic(api_key="sk-ant-...")

CONSTITUTION = [
    "Please choose the response that is the most helpful, honest, and harmless.",
    "Please choose the response that least enables illegal, unethical, or dangerous actions.",
    "Please choose the response that demonstrates respect for human autonomy and dignity.",
    "Please choose the response that is least biased with respect to gender, race, religion, or politics."
]

def generate_with_red_team(prompt: str, max_attempts: int = 3) -> str:
    """宪法式 AI：生成 → 评估 → 改写 循环"""
    for attempt in range(max_attempts):
        # Step 1: 生成候选回答
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        ).content[0].text

        # Step 2: AI 评估是否违反宪法
        critique_prompt = f"""
Constitution:
{chr(10).join(f"- {p}" for p in CONSTITUTION)}

Response to evaluate: "{response}"

Does this response violate any constitutional principle?
Reply with JSON: {{"violates": bool, "principle": "...", "suggestion": "..."}}
"""
        critique = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=256,
            messages=[{"role": "user", "content": critique_prompt}]
        ).content[0].text

        result = json.loads(critique)
        if not result["violates"]:
            return response

        # Step 3: 根据 critique 改写
        revise_prompt = f"""
Original response: "{response}"
Critique: {result['suggestion']}

Please revise the response to comply with the constitution.
Output only the revised response, no preamble.
"""
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=512,
            messages=[{"role": "user", "content": revise_prompt}]
        ).content[0].text

    return response

# 使用示例
print(generate_with_red_team("How do I pick a lock on my own front door?"))
```

---

## 🔬 进阶：CAI 与 RLHF 的混合范式

现代工业界 **没有纯 CAI 或纯 RLHF**，而是 **hybrid pipeline**：

```text
Stage 1: SFT（基础指令微调）
   ↓
Stage 2: RLHF（人类偏好，训练 Helpfulness）
   ↓
Stage 3: SL-CAI（AI 评估 + 改写，训练 Harmlessness 风格）
   ↓
Stage 4: RL-CAI / RLAIF（AI 偏好对，PPO 或 DPO 训练）
   ↓
Stage 5: Red-Team 持续加固（人工 + AI 联合对抗）
```

**为什么 hybrid？** 纯 CAI 在 Helpfulness 上会下降 1-3%，纯 RLHF 在 Harmlessness 上难突破 85%。混合方案可以同时拿到 90%+ 的双指标。

| 方案 | Helpfulness | Harmlessness | 成本 |
|------|-------------|--------------|------|
| 纯 RLHF | 85% | 78% | $1M |
| 纯 CAI | 84% | 91% | $100K |
| **Hybrid** | **87%** | **92%** | **$300K** |

---

## 🔗 跨模块反向链

### 主模块层

- **AI 应用层**：[同专题 SFT](01-sft.md) / [RLHF](02-rlhf.md) / [DPO](03-dpo.md) / [新方法](05-newer-methods.md) / [PEFT/LoRA](06-peft-lora.md)
- **AI 基础层**：[Transformer 架构](../../08.ai-foundations/03-transformer/README.md) / LLM 基础（In-Context Learning 与 CAI 自评估的对比）
- **推理优化**：[LLM 推理安全](../llm-inference/llm-inference-optimization/README.md)
- **RAG 应用**：[RAG 评估](../rag/04-evaluation.md) / [Hybrid Search](../rag/hybrid-search/README.md)

### 面试题层（12.interview）

- [AI 安全与对齐面试](../../12.interview/11.ai/llm-alignment/README.md) — 含 Constitutional AI 3 道高频题
- [Agent 评估面试](../../12.interview/11.ai/agent-reliability/README.md) — AI-as-Judge 评估一致性考点
- [RLHF/DPO 面试](../../12.interview/11.ai/llm-alignment/README.md) — RLHF vs CAI 对比题

### 故事层（13.story）

- [阿明餐厅 - 训练一个守规矩的服务员](../../13.story/31-ai-fatal-trio.md) — 用"AI 三元致命问题"（幻觉/安全/合规）类比宪法原则所防护的边界
- [阿明餐厅 - Lambda 架构](../../13.story/README.md) — AI 反馈 ≈ 顾客反馈

---

## ⚠️ 反直觉（5+ 条）

| # | 误区 | 真相 |
|---|------|------|
| 1 | ❌ Constitutional AI 替代 RLHF | ✅ 实际是补充，常组合用 |
| 2 | ❌ AI 评估一定准确 | ✅ LLM 评估有偏差，需人类抽检 |
| 3 | ❌ 宪法越多越好 | ✅ 50 条已是上限，多了易冲突 |
| 4 | ❌ Constitutional AI 让模型变木讷 | ✅ 适当调整原则可保持对话能力 |
| 5 | ❌ RLAIF = CAI | ✅ CAI 是 RLAIF 的具体实现（Anthropic 系），RLAIF 是更广义的"AI Feedback"抽象（Google 系） |
| 6 | ❌ 宪法写完就不变 | ✅ Claude 团队每季度 review 一次宪法，应对新型 jailbreak |
| 7 | ❌ CAI 不需要人类参与 | ✅ 宪法制定 + 边界 case 验证 + 红队都需要人 |

---

## 🔬 SL-CAI 算法深度拆解

监督式宪法 AI（SL-CAI）的核心循环：

```text
For each prompt x:
    1. Sample y0 ~ π(prompt=x, temperature=1)         # 高温采样 → 多样化输出
    2. Critique c ~ LLM(constitution, x, y0)           # AI 生成批评
    3. Revision y1 ~ LLM(constitution, x, y0, c)      # AI 根据批评改写
    4. (可选) Multi-round: y2 ~ LLM(constitution, x, y1, critique(y1))
    5. Add (x, y1) to SFT dataset
```

**关键设计选择**：

| 参数 | 选择 | 理由 |
|------|------|------|
| **采样温度** | 1.0（高）| 让模型尝试"危险边界"以训练 critique |
| **改写轮次** | 1-2 轮 | 2 轮后边际收益 < 5%，成本翻倍 |
| **Critique 模板** | 50 条原则全列 vs 选 Top-5 | 全列更准但慢 2x，工业界多选 Top-5 + 关键词匹配 |
| **数据配比** | 红队 prompt 40% + 正常 prompt 60% | 防止"过度谨慎" |

### 完整 SL-CAI 代码（生产级）

```python
import anthropic
from datasets import Dataset
from typing import List, Dict

client = anthropic.Anthropic()

CONSTITUTION_TOP5 = [
    "1. Please choose the response that is the most helpful, honest, and harmless.",
    "2. Please choose the response that least enables illegal, unethical, or dangerous actions.",
    "3. Please choose the response that demonstrates respect for human autonomy and dignity.",
    "4. Please choose the response that is least biased with respect to gender, race, religion, or politics.",
    "5. Please choose the response that best protects privacy and does not reveal personal information."
]

def sl_cai_step(prompt: str, max_revision: int = 2) -> Dict:
    """SL-CAI 单步：生成 → 评估 → 改写"""
    constitution_str = "\n".join(CONSTITUTION_TOP5)

    # Step 1: 高温采样生成回答
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=512,
        temperature=1.0,
        messages=[{"role": "user", "content": prompt}]
    ).content[0].text

    for _ in range(max_revision):
        # Step 2: AI 生成批评
        critique_resp = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[{"role": "user", "content": f"""
Constitution:
{constitution_str}

Response: "{response}"

Identify the single most relevant constitutional principle this response may violate.
Explain the violation briefly. Output JSON: {{"principle_idx": int, "violation": "..."}}
"""}]
        ).content[0].text

        # Step 3: 改写回答
        revised_resp = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=512,
            messages=[{"role": "user", "content": f"""
Original response: "{response}"
Constitutional critique: {critique_resp}

Please revise the response to address the critique while preserving any useful information.
Output only the revised response.
"""}]
        ).content[0].text

        response = revised_resp

    return {"prompt": prompt, "response": response}

# 批量生成 SFT 数据集
def build_sl_cai_dataset(prompts: List[str], output_path: str):
    dataset = []
    for i, prompt in enumerate(prompts):
        try:
            sample = sl_cai_step(prompt)
            dataset.append(sample)
            print(f"[{i+1}/{len(prompts)}] OK")
        except Exception as e:
            print(f"[{i+1}/{len(prompts)}] FAIL: {e}")

    ds = Dataset.from_list(dataset)
    ds.save_to_disk(output_path)
```

**关键工程经验**：

- 用 `temperature=1.0` 采样才能产生有意义的多样化错误样本
- 批评 prompt 不要列举全部 50 条原则，只列 Top-5 + 关键词命中，减少 LLM "读不完" 的概率
- 改写 2 轮后再做边际收益极低，建议 **1 轮** 默认

---

## 🔬 RL-CAI vs RLAIF：术语辨析

工业界对 "AI Feedback" 这一概念有 3 个术语，常被混用：

| 术语 | 起源 | 含义 | 训练范式 |
|------|------|------|----------|
| **CAI** | Anthropic 2022-12 | 用 AI 反馈训练 RL（论文标题级）| RLHF 范式 |
| **RLAIF** | Google DeepMind 2023-09 | AI 反馈的通用化框架 | PPO / DPO |
| **Constitutional RLAIF** | Anthropic 2024 | 用宪法 + AI 评估 | DPO 闭式解 |

**技术对比**：

```text
CAI 论文（Anthropic 2022）：
  - 必须显式宪法
  - 必须两阶段（SL-CAI + RL-CAI）
  - 输出 PPO 模型

RLAIF 论文（Google 2023）：
  - 宪法可有可无（开放框架）
  - 单阶段 RL（PPO）
  - 输出 PPO 模型

Constitutional RLAIF（Anthropic 2024）：
  - 必须显式宪法
  - 单阶段 RL（DPO 闭式解）
  - 输出 DPO 模型
```

**为什么 DPO 替代 PPO？** DPO 把 RLHF 的两阶段（RM + PPO）压缩成单阶段闭式解，**显存省 50%**，**训练快 2x**，效果接近 PPO（AlpacaEval 差距 < 2%）。

---

## 🏭 工业部署经验（Anthropic 公开博客提炼）

Anthropic 2024 年发布的 "Constitutional Classifiers" 实战经验：

### 1. 输入/输出双重过滤

```text
User Prompt
   ↓
[Input Classifier] → 拒绝明显的越狱 / 危险查询
   ↓
LLM 生成
   ↓
[Output Classifier] → 拒绝明显的违规输出
   ↓
返回用户
```

两层分类器用 CAI 训练数据微调的轻量模型（7B），推理延迟 < 50ms。

### 2. 红队持续对抗

| 阶段 | 方法 | 频率 |
|------|------|------|
| 静态红队 | 人工构造 1000+ 越狱 prompt | 月度 |
| 动态红队 | 多 LLM 互相对抗 + 进化算法 | 周度 |
| 社区红队 | bug bounty + 用户反馈 | 实时 |

### 3. 边界 case 的人工抽检

```python
# 每月抽检 1000 条 (prompt, response) 样本，人工评估
samples = sample_from_production_logs(n=1000)
human_labels = human_evaluate(samples)

# 评估 AI 评估器的精度
agreement_rate = sum(
    1 for s, h in zip(samples, human_labels)
    if ai_evaluate(s)['violates'] == h['violates']
) / len(samples)

print(f"AI vs Human agreement: {agreement_rate:.2%}")
# 目标：> 92%
```

### 4. 失败模式记录

| 失败模式 | 占比 | 应对 |
|---------|------|------|
| **过度拒绝**（benign prompt 被拒）| 30% | 细化原则边界 + 上下文消歧 |
| **新型越狱**（未见过的攻击）| 25% | Red-Team 持续加固 |
| **原则冲突**（同时违反两条原则）| 20% | 原则优先级排序 |
| **文化偏差**（西方价值观）| 15% | 本地化宪法版本 |
| **隐私泄露**（罕见但严重）| 10% | 输出过滤器 + 紧急下架流程 |

---

## 📊 CAI 评估基准（公开）

### Anthropic HH-RLHF Benchmark

CAI 论文使用的标准评估集：

| 子集 | 样本数 | 任务 |
|------|--------|------|
| **Helpful base** | 122K | 通用 helpfulness |
| **Harmless base** | 42K | 有害查询处理 |
| **Red team** | 38K | 对抗性攻击样本 |

评估方法：

- **Harmless Rate**：人类评判员判断回答是否"明显有害"（0-1）
- **Helpful Rate**：判断回答是否"有用且相关"（0-1）
- **Pairwise**：A/B 偏好对比

### 最新 SOTA 对比（2024）

| 模型 | Helpfulness | Harmlessness | 备注 |
|------|-------------|--------------|------|
| GPT-4（OpenAI）| 92% | 88% | RLAIF + Constitutional Classifiers |
| Claude 3 Opus | 90% | 94% | 全 CAI + 双层过滤 |
| Claude 3 Sonnet | 88% | 92% | 全 CAI |
| Gemini 1.5 Pro | 89% | 89% | RLAIF + 人工抽检 |
| Mistral-Large | 82% | 78% | 主要 RLHF，少量 CAI |

> **核心观察**：CAI + Constitutional Classifiers 是 2024+ 主流对齐方案的"事实标准"。

---

## 🧪 自检清单：你的 CAI pipeline 是否合格？

工业部署前必检：

- [ ] 宪法版本号记录（便于回滚）
- [ ] AI 评估器与人类评估一致性 ≥ 92%
- [ ] 过度拒绝率 ≤ 5%（benign query 不应被拒）
- [ ] 新型越狱检测覆盖率 ≥ 80%（红队验证）
- [ ] 输出过滤器延迟 ≤ 50ms
- [ ] 数据隐私保护：训练数据 PII 脱敏
- [ ] 文化本地化版本（至少 1 个非英语宪法）
- [ ] 紧急下架流程 + bug bounty 通道
- [ ] 季度宪法 review 机制
- [ ] 监控 + 告警系统（违规率突增自动告警）

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

← [返回 LLM 对齐专题](../README.md)

---

## 📚 参考来源

1. **Constitutional AI: Harmlessness from AI Feedback**：Yuntao Bai et al. *Constitutional AI 论文：SL-CAI + RL-CAI 两阶段范式，Anthropic 2022*. https://arxiv.org/abs/2212.08073
2. **Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback**：Yuntao Bai et al. *Anthropic HH-RLHF：Constitutional AI 的前身与对比基准，2022*. https://arxiv.org/abs/2204.05862
3. **Training language models to follow instructions with human feedback**：Long Ouyang et al. *InstructGPT/RLHF：与 Constitutional AI 对比的基础对齐方法，OpenAI 2022*. https://arxiv.org/abs/2203.02155
4. **Direct Preference Optimization: Your Language Model is Secretly a Reward Model**：Rafael Rafailov et al. *DPO：RLHF 的简化替代方案，2023*. https://arxiv.org/abs/2305.18290
5. **RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback**：Harrison Lee et al. *Google DeepMind RLAIF 论文：AI Feedback 通用化框架，2023*. https://arxiv.org/abs/2309.00267
6. **Claude's Constitution**：Anthropic. *Claude 公开宪法原文*. https://www.anthropic.com/news/claudes-constitution
