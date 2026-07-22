<!--
module:
  parent: ai
  slug: ai/peft-lora
  type: article
  category: 主模块子文章
  summary: PEFT / LoRA / QLoRA 参数高效微调 + DoRA / AdaLoRA 2024+ 新方法
-->

# PEFT / LoRA / QLoRA（参数高效微调）

> ⬅️ [返回 LLM 对齐专题](../README.md)

> **一句话定位**：PEFT = **冻结 99% 预训练参数，只训练 0.1-1% 增量矩阵**。LoRA 2021 年由 Microsoft 提出，**让 7B 模型在单张消费级 GPU 上完成微调**；QLoRA 进一步把 4-bit 量化 + LoRA 结合，**65B 模型在单卡 48GB 上微调成为可能**。**SFT / DPO / RLHF 全部依赖 PEFT 才能平民化**。

---

## 🎯 为什么需要 PEFT

全参微调 LLM 的痛点：

| 维度 | 全参微调 7B | LoRA r=8 | QLoRA |
|------|------------|----------|-------|
| **显存** | ~60 GB（FP16 + Adam） | ~16 GB | ~6 GB |
| **训练参数** | 7B（100%） | ~13M（0.2%） | ~13M |
| **可训练矩阵** | 全部 | 注入低秩分解 | 注入低秩分解 + 4-bit 量化 |
| **训练速度** | 1x | 1.5x | 0.8x（量化换显存） |
| **效果损失** | 基准 | ≤ 0.5% | ≤ 1% |

**结论**：LoRA 用 **0.2% 参数量** 达到 **接近全参** 的效果，已成为 SFT / DPO 的事实标准实现方式。

---

## 📐 4 大 PEFT 方法对比

| 方法 | 思路 | 参数量 | 显存 | 代表论文 |
|------|------|--------|------|----------|
| **LoRA** | 低秩矩阵分解 ΔW = BA | 0.1-5% | 16GB（7B） | Microsoft 2021 |
| **QLoRA** | 4-bit NF4 量化 + LoRA | 0.1-5% | 6GB（7B） | Dettmers 2023 |
| **Adapter** | 插入小 MLP 模块 | 3-5% | 中 | Houlsby 2019 |
| **Prefix-Tuning** | 在每层加可学习 prefix | 0.1% | 中 | Li & Liang 2021 |

**LoRA 系列** vs Adapter 系列：

- Adapter 增加**推理延迟**（串行计算），LoRA **不增加**（可合并回 W）
- Prefix-Tuning 占用**输入 token**（抢位置），LoRA 不占

---

## 🧮 LoRA 数学与原理

### 核心公式

```text
原始前向：h = W · x
LoRA 前向：h = W · x + (B · A) · x · (alpha / r)

其中：
  W：预训练权重矩阵，d × k，冻结
  A：k × r，**高斯初始化**（N(0, σ²)）
  B：d × r，**全零初始化**
  r：秩（rank），典型 4 / 8 / 16 / 32
  alpha：缩放因子，典型 2r 或 16
```

**初始化原因**：

- B=0 保证训练起点 ΔW = BA = 0 → 输出与原始模型一致
- A 高斯打破对称性，确保训练有梯度

### 为什么低秩就够？

Transformer 的权重更新有**低内在秩**（intrinsic rank）：

```text
8192 × 8192 矩阵全参：67,108,864 参数
8192 × 8192 矩阵 r=8 拆解：8192×8 + 8×8192 = 131,072 参数
压缩比：67M / 13.1万 ≈ 500x
```

经验法则：**绝大部分任务 r=8 就足够**；复杂任务（代码生成、多语言）用 r=32-64。

### alpha / r 怎么调？

| alpha/r 比 | 效果 |
|------------|------|
| **1**（如 alpha=16, r=16） | 标准设置，温和更新 |
| **2**（如 alpha=32, r=16） | 放大更新幅度，激进学习 |
| **< 1** | 保守，接近冻结 |

**推荐**：alpha = 2r（最常用），训练早期效果更明显。

### 哪些层加 LoRA？

```python
# 默认只加到 attention 层（Q / K / V）
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]

# 进阶：加到 MLP 层（效果 +1-2%，参数 +50%）
target_modules = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]
```

---

## ⚡ QLoRA = NF4 + 双重量化 + Paged Optimizer

QLoRA = **Quantized LoRA**，把 4-bit 量化与 LoRA 深度结合。

### 三件套

| 组件 | 作用 | 原理 |
|------|------|------|
| **NF4**（4-bit NormalFloat） | 4-bit 量化基础权重 | 针对**正态分布**权重设计的非均匀量化 |
| **双重量化**（Double Quant） | 节省量化常数显存 | 对量化常数本身再做一次量化 |
| **Paged Optimizer** | 防 OOM | 优化器状态**分页到 CPU 内存**，OOM 时自动卸载 |

### NF4 量化原理

```text
FP16 权重 → 4-bit NormalFloat
  1. 把权重归一化到 [-1, 1]
  2. 用 16 个分位点量化（针对正态分布优化）
  3. 反量化时线性插值
结果：每参数 4 bits + 共享量化常数
```

NF4 比 FP4 / INT4 误差更小，因为**LLM 权重近似正态分布**。

### Paged Optimizer

```text
训练时：optimizer state (Adam 的 m / v) 在 GPU
        → OOM 时自动卸载到 CPU 内存（页交换）
        → 显存压力降低 60-70%
```

NVIDIA 统一内存 + bitsandbytes 的 `paged_adamw_8bit` 实现。

### QLoRA 实操：LLaMA-Factory 一行启动

```yaml
# LLaMA-Factory config
model_name_or_path: meta-llama/Llama-2-7b-hf
quantization_bit: 4              # NF4 4-bit 量化
quantization_method: bitsandbytes
lora_rank: 16
lora_alpha: 32
lora_target: q_proj,v_proj       # 只加 Q / V
learning_rate: 1.0e-4
gradient_checkpointing: true     # 进一步省显存
optim: paged_adamw_8bit          # 分页优化器
batch_size: 2
```

**硬件门槛**：Llama-2-7B QLoRA 只需 **单张 24GB 消费级显卡**（如 4090）。

---

## 🚀 DoRA / AdaLoRA / LoRA+ 2024-2026 新方法

### DoRA（Weight-Decomposed Low-Rank Adaptation）

**论文**：Liu et al. 2024（NVIDIA）

**核心创新**：把权重分解为**幅度（magnitude）+ 方向（direction）**：

```text
W = m * (V / ||V||)
W' = m * ((W + BA) / ||W + BA||)   # 只更新方向，冻结 m
```

**为什么有效**：LoRA 同时更新幅度和方向会**耦合干扰**；DoRA 解耦后更稳定。

**效果**：在 LLaMA-2-7B / Mistral-7B 多 benchmark 上**比 LoRA 强 5-10%**。

```python
from peft import LoraConfig
config = LoraConfig(
    use_dora=True,    # 启用 DoRA
    r=16, lora_alpha=32,
    target_modules="all-linear",
)
```

### AdaLoRA（Adaptive LoRA）

**论文**：Zhang et al. ICML 2023

**核心创新**：**每个矩阵自适应分配 rank**（重要的层多预算，不重要的层少预算）。

```text
预算初始化：总参数量 = 8M
每层 rank 初始化：r=12
训练中：通过 SVD 重要性评分 → 重要层升 r=24，不重要层降 r=4
```

**效果**：相同参数预算下，效果**强 LoRA 2-3%**。

### LoRA+（2024）

**论文**：Hayou et al. 2024

**核心创新**：**A 和 B 用不同学习率**（B 是 A 的 λ 倍，λ ≈ 2^4 = 16）。

```text
A 矩阵：学习率 η
B 矩阵：学习率 η × λ（λ=16）
```

理论依据：**初始化时 BA=0，需要 B 学得快才能让 ΔW 离开零**。

### LongLoRA（2024）

**论文**：Chen et al. 2024

**核心创新**：**长上下文（100K-1M）的 LoRA**——用 shift-short attention 近似 full attention。

**代表模型**：Llama-2-7B-LongLoRA（100K context）

### LoRA 微调方法选型决策树

```text
Q1: 显存极度紧张（< 16GB）？
├── 是 → QLoRA（4-bit + LoRA）
└── 否 → LoRA（FP16 + LoRA）

Q2: 追求 SOTA 效果？
├── 是 → DoRA（解耦幅度方向）
└── 否 → 标准 LoRA

Q3: 参数预算固定，想每个矩阵自适应 rank？
├── 是 → AdaLoRA
└── 否 → LoRA 固定 r

Q4: 长上下文（> 32K）？
├── 是 → LongLoRA
└── 否 → LoRA
```

---

## 🛠️ 实操：PEFT + bitsandbytes 一键微调

```python
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# Step 1: 4-bit 量化配置
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",          # NF4 量化
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,    # 双重量化
)

# Step 2: 加载量化模型
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)

# Step 3: 准备 k-bit 训练（注入 LoRA 前的预处理）
model = prepare_model_for_kbit_training(model)

# Step 4: 配置 LoRA
lora_config = LoraConfig(
    r=16,                              # rank
    lora_alpha=32,                     # 缩放因子
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    use_dora=False,                    # True 启用 DoRA
)

# Step 5: 注入 LoRA adapter
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# 输出：trainable params: 13,107,200 || all params: 6,738,415,616 || trainable%: 0.1945
```

**完整 7B QLoRA 训练**：单卡 24GB 可跑；14B QLoRA 需要 40GB（A100-40G）。

---

## 📊 显存与效果对照（7B 模型）

| 方案 | 显存 | 训练时间 | 效果（AlpacaEval） | 硬件门槛 |
|------|------|----------|-------------------|---------|
| **全参 FP16 + Adam** | ~60 GB | 1x | 基准 100% | A100-80G |
| **全参 BF16 + 8bit Adam** | ~40 GB | 1.1x | 99.5% | A100-40G |
| **LoRA FP16** | ~16 GB | 1.5x | 99% | 3090 / 4090 |
| **QLoRA NF4** | ~6 GB | 0.8x | 97-98% | 消费级 24G |
| **QLoRA + DoRA** | ~6 GB | 0.8x | 98-99% | 消费级 24G |

**关键洞察**：

- LoRA 训练**比全参快**（更少参数更新 + 更少优化器状态）
- QLoRA 牺牲**约 20% 训练速度**换 60% 显存节省
- DoRA 用**同等显存**提升 5-10% 效果

---

## ⚠️ 5 大反直觉

| 误区 | 真相 |
|------|------|
| ❌ LoRA 只能用于 SFT | ✅ 同样适用 RLHF / DPO（LoRA PPO / LoRA DPO） |
| ❌ r 越大效果越好 | ✅ r=8 已足够，r>32 易过拟合 |
| ❌ QLoRA 效果远差于全参 | ✅ 差距 ≤ 1%，完全可用 |
| ❌ LoRA 推理时也有额外开销 | ✅ 训练后可**合并回 W**，零开销 |
| ❌ PEFT 只是为了省显存 | ✅ 还防灾难性遗忘 + 便于多任务切换 |

---

## 📚 参考来源

1. **LoRA 原论文**：Hu et al. *LoRA: Low-Rank Adaptation of Large Language Models*. ICLR 2022. https://arxiv.org/abs/2106.09685
2. **QLoRA 论文**：Dettmers et al. *QLoRA: Efficient Finetuning of Quantized LLMs*. NeurIPS 2023. https://arxiv.org/abs/2305.14314
3. **DoRA 论文**：Liu et al. *DoRA: Weight-Decomposed Low-Rank Adaptation*. ICML 2024. https://arxiv.org/abs/2402.09353
4. **Hugging Face PEFT 官方文档**：https://huggingface.co/docs/peft
5. **bitsandbytes 官方文档**（NF4 + 8-bit Optimizer）：https://github.com/TimDettmers/bitsandbytes

---

## 🔗 系列导航表

| # | 章节 | 一句话定位 |
|---|------|-----------|
| 1 | [SFT](01-sft.md) | 用高质量指令-回答对微调预训练 LLM，让模型从"续写"变成"对话" |
| 2 | [RLHF](02-rlhf.md) | 用人类偏好训练 Reward Model + PPO，GPT-4 / Claude 3 标准对齐方法 |
| 3 | [DPO](03-dpo.md) | 直接用偏好对优化策略，跳过 Reward Model，效果接近 RLHF |
| 4 | [Constitutional AI](04-constitutional-ai.md) | 用 AI 评估替代人类反馈，Claude 2/3 全部采用 |
| 5 | [新方法](05-newer-methods.md) | KTO/IPO/SimPO/ORPO/RFT 2024-2025 新对齐算法 |
| 6 | **PEFT / LoRA / QLoRA** | **参数高效微调，让 7B 模型在单卡 24GB 训练** |

← [返回 LLM 对齐专题](../README.md)
