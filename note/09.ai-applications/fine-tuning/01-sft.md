<!--
module:
  parent: ai
  slug: ai/sft
  type: article
  category: 主模块子文章
  summary: SFT 监督微调：所有对齐方法的基础
  depth: ⭐⭐⭐⭐⭐
-->

# SFT（Supervised Fine-Tuning）

> ⬅️ [返回 LLM 对齐专题](../README.md)

> **一句话定位**：SFT = **用高质量指令-回答对微调预训练 LLM**，让模型从"续写"变成"对话"。**所有对齐方法的基础**——RLHF / DPO / Constitutional AI 都在 SFT 之后做。

---

## 🎯 为什么需要 SFT

预训练 LLM 的本质是"续写器"：

```text
输入："今天天气"
输出："今天天气很好，我打算去公园散步..."
```

SFT 之后变成"助手"：

```text
输入："今天天气"
输出："北京今天晴 25°C，适合户外活动。请问您想了解哪方面？"
```

**本质转变**：SFT 把 LLM 从「预测下一个 token」调整为「理解指令 → 生成有用回答」。这一步是后续所有对齐工作的基石——没有 SFT，RLHF 的奖励模型无从打分、DPO 没有初始 policy 可优化、Constitutional AI 的自批评也没有基座。

---

## 📐 SFT 训练流程

```text
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

## 🧮 SFT 核心数学：交叉熵损失

SFT 本质上是带掩码的语言建模（masked LM loss）：

```text
L_SFT(θ) = - E_{(x,y)~D} [ Σ_t  log π_θ(y_t | x, y_<t) ]
```

其中：
- `x` = prompt（指令 + 可选 input）
- `y` = target output
- `y_<t` = 截至 t-1 位置的所有 target token
- 仅对 **response 部分**计算损失（prompt 部分 mask 掉，label = -100）

**关键细节**：

```python
# HuggingFace Trainer 内部对 response-only 损失的处理
labels = input_ids.clone()
labels[:, :prompt_len] = -100  # 屏蔽 prompt
loss = CrossEntropyLoss(reduction="mean")(logits.view(-1, V), labels.view(-1))
```

**为什么只对 response 计算损失？** 否则模型会"学会模仿自己的 prompt 分布"，反而降低泛化。Alpaca、ShareGPT、OpenHermes 等公开数据集的处理逻辑一致。

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

## 🛠️ 实操：HuggingFace TRL SFTTrainer

TRL 是 HuggingFace 官方推出的 RLHF/DPO/SFT 全家桶，SFTTrainer 是其核心组件之一：

```python
from trl import SFTTrainer, SFTConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-7B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-7B")

# 数据：每条样本 {"text": "<full conversation>"}
dataset = load_dataset("HuggingFaceH4/no_robots", split="train")

config = SFTConfig(
    output_dir="./qwen2-sft",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    max_length=2048,
    packing=True,                  # 短样本拼接提升吞吐
    dataset_text_field="text",
    gradient_checkpointing=True,   # 省显存
    bf16=True,                     # A100/H100 用 bf16
)

trainer = SFTTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

**关键参数**：
- `packing=True`：把多条短样本拼到 `max_length`，TPS 提升 3-5x
- `gradient_checkpointing=True`：长序列必开，省 30%+ 显存
- `bf16`：A100/H100 支持，数值稳定；V100/A10 只能用 fp16

---

## 🛠️ 实操：PEFT + LoRA 节省显存

70B 模型全参微调需要 8x A100 80G；LoRA 可以把显存降到单卡：

```python
from peft import LoraConfig, get_peft_model, TaskType

lora_config = LoraConfig(
    r=16,                          # LoRA rank
    lora_alpha=32,
    target_modules=[               # 注入到注意力 + MLP
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 40M || all params: 6.7B || trainable%: 0.59%
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

## 🕰️ 演进史时间线（2017 → 2024）

```text
2017  • 早期微调（Fine-tuning BERT / GPT-1）
      - 任务特定 fine-tuning（分类 / 序列标注）
      - 全参微调主流

2018-2020  • GPT-2 / GPT-3 时代
      - "Prompt engineering" 替代 fine-tuning 成为主流
      - in-context learning 被发现

2022 Q1  • InstructGPT 论文（Ouyang et al., OpenAI）
      - 正式定义 3 阶段对齐：SFT → RM → RLHF
      - 175B SFT → 6B RM → 175B PPO
      - 奠定现代 LLM 对齐范式

2022 Q3  • FLAN-T5 / FLAN-PaLM（Google）
      - 指令微调系统化研究：1836 个任务
      - "Scaling instruction-finetuned language models"（Chung et al.）

2023 Q1  • Self-Instruct（Wang et al., UWashington）
      - LLM 自生成指令，4 步去噪
      - 引发 Alpaca / WizardLM / UltraChat 等开源 SFT 数据浪潮

2023 Q3  • LLaMA-2 Chat（Meta）
      - 公开 SFT + RLHF 全流程，开源对齐数据集
      - "Llama 2: Open Foundation and Fine-Tuned Chat Models"

2024 Q1  • Llama-3 / Qwen2 / Yi 等
      - SFT 数据进入"千万级高质量"阶段
      - Evol-Instruct / Code-Feedback 多轮复杂指令

2024 Q4  • DeepSeek-R1 / R1-Zero
      - 纯 RL（GRPO）也能对齐（无需 SFT）→ 范式突破
      - 但工业实践仍以 SFT + RLHF/DPO 为主流
```

---

## 🏢 真实案例

### 案例 1：OpenAI fine-tuning API（2023-2024）

OpenAI 在 2023 年 8 月开放 `gpt-3.5-turbo` fine-tuning API（之后扩展到 `gpt-4`），是工业级 SFT 服务的标杆。

**数据格式**：JSONL，每行 `{"messages": [{"role": "user", ...}, {"role": "assistant", ...}]}`

```python
import openai
client = openai.OpenAI(api_key="...")

# 1. 上传训练文件
file = client.files.create(
    file=open("train.jsonl", "rb"),
    purpose="fine-tune",
)

# 2. 创建 SFT 任务
job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-3.5-turbo-0613",
    hyperparameters={"n_epochs": 3, "batch_size": 4, "learning_rate_multiplier": 0.1},
)

# 3. 轮询状态
for event in client.fine_tuning.jobs.list_events(id=job.id):
    print(event.message)
```

**关键限制**：
- 仅支持 SFT + DPO（不开放 RLHF/PPO）
- 单次训练最大 5 亿 tokens
- 收费：训练 $0.0080/1K tokens + 推理 $0.0120/1K tokens（gpt-3.5）

---

### 案例 2：Anthropic Claude（Constitutional AI）

Anthropic 用 **RLAIF（RL from AI Feedback）** 替代人类偏好标注，但前置仍然是 SFT。流程：

```text
Step 1: SFT（helpful + harmless 监督微调）
Step 2: Self-Critique → AI 生成偏好对
Step 3: RLAIF（AI 反馈 + RL）
```

详见 [Constitutional AI](04-constitutional-ai.md)。关键洞察：**SFT 数据质量决定上限**——Anthropic 内部 50+ 标注员多轮 red-teaming 才能产出可用的初始 SFT 集。

---

### 案例 3：HuggingFace TRL（开源工业标准）

TRL（Transformer Reinforcement Learning）是 HuggingFace 维护的 RLHF/DPO/SFT 工具库，GitHub Stars 13k+（2024），是开源社区事实标准：

```python
# TRL 支持的训练模式
from trl import SFTTrainer, DPOTrainer, PPOTrainer, RewardTrainer

# 统一接口 → 切换训练范式只需换 trainer 类
```

**生产经验**：
- Llama-3-Instruct 全流程开源（SFTTrainer + DPOTrainer）
- Mistral-7B-Instruct、Zephyr-7B 都是用 TRL 训练

---

### 案例 4：LLaMA-Factory（一键全流程）

[LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) 是国内最流行的开源训练框架（30k+ stars，2024），支持 100+ 模型 + 50+ 数据集：

```yaml
# LLaMA-Factory 配置文件示例（train.yaml）
model_name_or_path: Qwen/Qwen2-7B
finetuning_type: lora
lora_rank: 16
lora_target: q_proj,v_proj

dataset: alpaca_zh,identity
template: qwen
output_dir: saves/qwen2-7b-lora-sft

per_device_train_batch_size: 4
gradient_accumulation_steps: 4
learning_rate: 1.0e-4
num_train_epochs: 3.0
max_length: 2048
warmup_ratio: 0.03
```

```bash
llamafactory-cli train train.yaml
```

**核心优势**：
- 内置 100+ 模型架构（Llama / Qwen / Mistral / GLM / Baichuan / DeepSeek）
- WebUI 可视化（`llamafactory-cli webui`）
- 一键切换 SFT / DPO / RM / PPO

---

### 案例 5：DeepSeek-R1（纯 RL 不需要 SFT）

DeepSeek-R1 / R1-Zero（2024 年 12 月）证明了**纯强化学习（GRPO）也能产生推理能力**，但工业实践仍以 **SFT → RL** 两阶段为主：

```text
DeepSeek-R1-Zero（实验）：纯 GRPO → 涌现长思维链
DeepSeek-R1（生产）：SFT + GRPO → 稳定 + 强推理
```

**对 SFT 的启示**：
- 推理类任务：SFT 提供"格式规范"，RL 优化"推理深度"
- 通用任务：SFT 仍是对齐的第一阶段，RL 是 fine-tuning

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ SFT 数据越多越好 | ✅ 5 万高质量 > 100 万低质量 |
| ❌ SFT 后模型会变笨 | ✅ 正确 SFT 仅调整格式和风格 |
| ❌ SFT 可以完全替代 RLHF | ✅ SFT 是 RLHF 的必要前置 |
| ❌ SFT 只能用人工标注 | ✅ Self-Instruct + 蒸馏可自动生成 |
| ❌ SFT 学习率应该和预训练一致 | ✅ 应小 10x（1e-5 vs 1e-4） |
| ❌ SFT 把所有参数都更新 | ✅ LoRA 只更新 <1% 参数，剩余冻结 |
| ❌ SFT 后做 DPO 就能替代 RLHF | ✅ DPO 在小模型上接近 RLHF，但 SOTA（GPT-4/Claude）仍用 RLHF 或 DPO+RLHF 混合 |
| ❌ 训练数据越多样越好 | ✅ 领域任务（如代码 / 数学）单领域数据反而效果更好 |

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

- **L3 同级**：Harness Engineering（⚠️ 待 Phase 1+ 迁入；占位 `../agent/execution-patterns/harness-engineering/`） 顺带提
- **咬文嚼字**：面试深挖（⚠️ 待 Phase 1+ 迁入；占位 `../../../12.interview/11.ai/agent-performance-evaluation/`）

← [返回 09.ai-applications/fine-tuning](../README.md)

---

## 🔗 跨模块反向链

- **08.ai-foundations**：[Transformer 架构](../../08.ai-foundations/03-transformer/transformer-architecture.md) SFT 微调的是 Transformer decoder；[LoRA 数学](06-peft-lora.md) SFT 中 LoRA 的低秩更新矩阵推导。
- **03.data-stack**：[分布式训练](../../08.ai-foundations/04-llm/llm-basics.md) SFT 在多卡场景的 ZeRO / FSDP 策略；[向量数据库](../rag/vector-search-algorithms/README.md) SFT 数据清洗的 embedding 去重。
- **12.interview**：[SFT vs RAG 对比](../../12.interview/11.ai/peft-lora/README.md) 面试高频问题；[RLHF 训练流程](../../12.interview/11.ai/llm-alignment/README.md) SFT 是 RLHF 的第一阶段。
- **13.story**：[阿明餐厅 - 训练服务员](../../13.story/35-ai-observability.md) 用 SFT 类比新员工培训。

---

## 🛠️ 实操：数据预处理与质量过滤

SFT 训练数据质量决定上限，常见清洗流程：

```python
from datasets import load_dataset
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-7B")

# 1. 加载原始数据
raw = load_dataset("OpenAssistant/oasst1", split="train")

# 2. 长度过滤（避免过长样本）
def length_filter(example):
    text = example["text"]
    tokens = tokenizer.encode(text)
    return 100 <= len(tokens) <= 2048

# 3. 去重（embedding 相似度）
import numpy as np
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedder.encode([ex["text"] for ex in raw])

# 余弦相似度去重
def deduplicate(embeddings, threshold=0.85):
    keep = []
    for i, emb in enumerate(embeddings):
        is_dup = False
        for j in keep:
            sim = np.dot(emb, embeddings[j]) / (
                np.linalg.norm(emb) * np.linalg.norm(embeddings[j])
            )
            if sim > threshold:
                is_dup = True
                break
        if not is_dup:
            keep.append(i)
    return keep

# 4. 质量评分（用 GPT-4 评分）
def quality_score(example):
    # 简化：用规则判断
    score = 0
    if len(example["text"]) > 200: score += 1
    if example.get("lang") == "en": score += 1
    if not example["text"].startswith("Sure"): score += 1   # 避免低质开头
    return score >= 2
```

---

## 📈 评估方法

### 自动评估

| 评测集 | 用途 | 规模 |
|--------|------|------|
| **MMLU** | 多任务知识 | 57 学科 14K 题 |
| **AlpacaEval** | 对比 GPT-4 的胜率 | 805 题 |
| **MT-Bench** | 多轮对话 | 80 题 8 类别 |
| **IFEval** | 指令遵循 | 541 题 |
| **HumanEval** | 代码生成 | 164 题 |
| **GSM8K** | 数学推理 | 8.5K 题 |

### 人工评估

- **Likert 5 分制**：有用性、真实性、无害性、流畅性
- **Pairwise 对比**：A vs B 模型对比
- **Red-teaming**：故意挑刺找漏洞

**实战经验**：AlpacaEval 与人类偏好的相关系数 ~0.85，是性价比最高的自动指标。

---

## 🔥 常见踩坑 / Debug

| 现象 | 原因 | 解决 |
|------|------|------|
| Loss 不下降 | LR 太小 / 数据格式错 | 加 LR 10x / 检查 prompt-template |
| Loss = NaN | fp16 溢出 / 梯度爆炸 | 换 bf16 / 加 grad clip=1.0 |
| 输出重复 | 多样性不足 / 重复 token 惩罚未开 | 加 `repetition_penalty=1.1` |
| 中文乱码 | tokenizer 不匹配 | 用同系列 tokenizer |
| 显存爆炸 | seq 过长 / batch 过大 | 启用 gradient checkpointing |
| 学不会格式 | prompt template 不一致 | 强制 chat_template 一致 |
| 训练时好推理时差 | 过拟合 train prompt | 加 validation set + early stop |
| 输出变简短 | 学到短回答偏置 | 数据长度均衡 + length normalization |

---

## 🏭 工业部署考虑

```python
# 模型合并 + 量化部署
from peft import PeftModel
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# 1. LoRA 合并到 base model
base = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-7B")
merged = PeftModel.from_pretrained(base, "./qwen2-7b-lora-sft").merge_and_unload()
merged.save_pretrained("./qwen2-7b-sft-merged")

# 2. 量化部署（INT4/AWQ/GPTQ）
from transformers import AutoGPTQForCausalLM
quantized = AutoGPTQForCausalLM.from_quantized("./qwen2-7b-sft-merged")

# 3. vLLM 部署（生产级）
# vllm serve ./qwen2-7b-sft-merged --tensor-parallel-size 2 --quantization awq
```

---

## 📚 参考来源

1. **Training language models to follow instructions with human feedback**：Long Ouyang et al. *InstructGPT：SFT + RLHF 三阶段对齐奠基论文，OpenAI 2022*. https://arxiv.org/abs/2203.02155
2. **Self-Instruct: Aligning Language Models with Self-Generated Instructions**：Yizhong Wang et al. *Self-Instruct 自生成指令数据方法，2022*. https://arxiv.org/abs/2212.10560
3. **LLaMA: Open and Efficient Foundation Language Models**：Hugo Touvron et al. *LLaMA 系列 + Alpaca 数据蒸馏范式，Meta 2023*. https://arxiv.org/abs/2302.13971
4. **LoRA: Low-Rank Adaptation of Large Language Models**：Edward J. Hu et al. *LoRA 参数高效微调基础，ICLR 2022*. https://arxiv.org/abs/2106.09685
5. **Scaling Instruction-Finetuned Language Models**：Hyung Won Chung et al. *FLAN-T5 / FLAN-PaLM，Google 2022*. https://arxiv.org/abs/2210.11416
6. **Llama 2: Open Foundation and Fine-Tuned Chat Models**：Hugo Touvron et al. *Meta 2023*. https://arxiv.org/abs/2307.09288
7. **DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning**：DeepSeek-AI 2024. https://arxiv.org/abs/2501.12948
8. **OpenAssistant Conversations Dataset / OASST1**：UWashington / LAION 2023. https://huggingface.co/datasets/OpenAssistant/oasst1
