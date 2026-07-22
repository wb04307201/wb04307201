<!--
question:
  id: 11.ai-peft-lora
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [11.ai, PEFT, LoRA, QLoRA, DoRA, NF4, 参数高效微调]
-->

# PEFT / LoRA / QLoRA 面试深挖（4 大核心）

> ⬅️ [返回 AI 咬文嚼字](../README.md) | [主模块深度专题](../../../11.ai/03-engineering/llm-alignment/06-peft-lora.md)

> **一句话定位**：4 大核心 PEFT 题**面试深挖版**：LoRA 数学 / QLoRA NF4 / DoRA / Full-FT vs PEFT 选型。

---

## 🎯 4 大核心题

### Q1：LoRA 核心数学？（α/r 那个公式）

**陷阱**：
- ❌ 只答"低秩分解"（不够，需要写出公式）
- ❌ 不知道 α 和 r 的比值怎么定

**30 秒话术**：
> "LoRA 把权重更新分解成低秩：h = W·x + (B·A)·x × (alpha/r)，其中 r 是秩（4/8/16），alpha 是缩放因子（典型 2r），B 矩阵全零初始化保证起点与原模型一致。训练参数量 = 0.1-5%，但效果接近全参。"

**90 秒话术**：
> "LoRA 核心公式：**h = W·x + (B·A)·x × (alpha/r)**。W 是冻结的 d×k 预训练权重，A 是 k×r（高斯初始化），B 是 d×r（全零初始化），r 是秩。**B=0 保证训练起点 ΔW=BA=0**，输出与原始模型完全一致；A 高斯打破对称性。**alpha/r 比值怎么选**：=1 是温和更新（alpha=16, r=16），=2 是激进学习（alpha=32, r=16），<1 是保守接近冻结。**经验法则**：r=8 已足够 90% 任务，复杂任务（代码/多语言）才用 r=32-64。8192×8192 矩阵 r=8 拆解压缩 500x（67M → 13.1万参数）。训练后可**合并回 W**，推理零额外开销。"

---

### Q2：QLoRA 怎么把 65B 装进单卡？

**陷阱**：
- ❌ 只答"4-bit 量化"（不够，QLoRA 是 3 件套）
- ❌ 不知道 NF4 是怎么设计的

**30 秒话术**：
> "QLoRA = **NF4 量化 + LoRA adapter + Paged Optimizer** 三件套。NF4 是**针对正态分布权重**设计的 4-bit 数据类型，比 INT4/FP4 误差小；Paged Optimizer 把 Adam 的 m/v 状态分页到 CPU 内存，OOM 时自动卸载。65B 模型单卡 48GB 可微调。"

**90 秒话术**：
> "QLoRA（Dettmers 2023）由 **3 个组件**组成：**① NF4（NormalFloat）** —— 4-bit 量化数据类型，把权重归一化到 [-1,1] 后用 **16 个分位点**量化（针对 LLM 权重近似正态分布的特性优化），比 INT4/FP4 误差小 50%+。**② 双重量化（Double Quant）** —— 对 NF4 的量化常数本身再做一次量化，节省 0.4 bit/参数。**③ Paged Optimizer** —— 用 bitsandbytes 的 `paged_adamw_8bit`，训练时 Adam 状态在 GPU，OOM 时**自动卸载到 CPU 内存**（NVIDIA 统一内存页交换），显存压力降 60-70%。**实操**：Llama-2-7B QLoRA 单张 24GB 消费级显卡（4090）可跑；65B QLoRA 单卡 48GB（A6000-48G）可微调。**效果**：7B 模型 AlpacaEval 达到全参 97-98% 水平，差距 ≤ 1%。"

---

### Q3：DoRA 为什么能超 LoRA？

**陷阱**：
- ❌ 答"分解方式不同"（太笼统）
- ❌ 不知道 magnitude × direction 的几何意义

**30 秒话术**：
> "DoRA 把权重分解成 **magnitude（标量幅度）× direction（单位方向向量）** 两部分独立微调。direction 用 LoRA 低秩处理，magnitude 是单参数。解耦后 magnitude 和 direction 不再耦合干扰，比纯 LoRA 在常见 benchmark 强 5-10%。"

**90 秒话术**：
> "DoRA（Liu et al. NVIDIA 2024）的核心洞察：LoRA 同时更新幅度和方向会**耦合干扰**。数学表达：**W = m × (V / ||V||)**，其中 m 是 magnitude（标量），V/||V|| 是 direction（单位向量）。**训练时**：W' = m × ((W + BA) / ||W + BA||)，方向用 LoRA 低秩处理 ΔV=BA，幅度 m 单独学习（单参数）。**几何意义**：把高维权重更新看成在球面上调方向（direction）+ 沿径向调半径（magnitude），**两者梯度方向正交**，不互相干扰。**实现**：`LoraConfig(use_dora=True, ...)`，peft 库原生支持。**效果**：在 LLaMA-2-7B / Mistral-7B 多 benchmark（GSM8K、MMLU、HumanEval）上**比 LoRA 强 5-10%**，**显存几乎相同**（仅多 1 个 magnitude 参数/层）。**实测**：LLaMA-2-7B + DoRA r=16 在 HumanEval 比 LoRA r=16 提升 3.2 个百分点。"

---

### Q4：Full Fine-tuning vs LoRA 怎么选？

**陷阱**：
- ❌ 一律推荐 LoRA（不是银弹）
- ❌ 不分场景

**30 秒话术**：
> "**默认选 LoRA**：显存省 4-10x，可热插拔 adapter。Full-FT 用于 3 类场景：① 数据极多（百万级）② 模型本就小（<7B）③ 需要显著改变 base 行为。QLoRA 在 24GB 单卡上 65B 也能玩。"

**90 秒话术**：
> "**选型决策树**：**默认 LoRA**（99% 场景）：7B 模型 LoRA FP16 只需 16GB（3090/4090），训练参数 0.2%，效果达全参 99%，**训练后可合并回 W 推理零开销**，**多个 adapter 热插拔切换**。**Full-FT 仅在 3 类场景必须**：① 数据量极大（百万级指令对）且需极致效果 ② 模型小（<7B 如 1B/3B），LoRA 收益不大 ③ 需要**显著改变 base 行为**（从英文模型学中文 / 从通用模型学垂直领域推理范式）。**QLoRA**：当显存 <24GB 时首选，Llama-2-7B QLoRA 6GB 显存可跑，65B QLoRA 48GB 单卡可微调，**效果损失 ≤ 1%**。**DoRA**：当追求 SOTA 时替代 LoRA（成本不变，效果 +5-10%）。**反直觉**：LoRA 训练**比全参快**（更少参数 + 更少优化器状态），是 2024-2026 SFT/DPO 训练的事实标准。**5 大反直觉**：① LoRA 不止用于 SFT（同样适用 RLHF/DPO） ② r>32 易过拟合 ③ QLoRA 效果损失 < 1% ④ 推理时 LoRA 可合并零开销 ⑤ PEFT 防灾难性遗忘 + 便于多任务切换。"

---

## 🔗 兄弟章节

- **主模块深度**：[PEFT / LoRA / QLoRA 深度专题](../../../11.ai/03-engineering/llm-alignment/06-peft-lora.md) — 4 大方法完整版 + DoRA/AdaLoRA/LoRA+/LongLoRA 2024-2026 新方法
- **兄弟面试题**：[LLM 对齐方法深挖](../llm-alignment/README.md) — SFT/RLHF/DPO/Constitutional AI 5 大对齐方法（SFT/DPO 几乎必须配合 LoRA 使用）
- **兄弟面试题**：[LLM 推理优化深挖](../llm-inference/README.md) — Continuous Batching / PagedAttention / KV Cache / 量化（量化基础）
- **餐厅叙事**：[12.story 系列目录](../../../12.story/README.md)（PEFT 主题餐厅叙事篇待补）

---

## 📊 4 题难度速查

| 题 | 难度 | 频率 | 关键数字 |
|---|------|------|---------|
| Q1 LoRA 数学 | ⭐⭐⭐⭐ | 高频 | α/r=1~2，r=8，0.2% 参数 |
| Q2 QLoRA NF4 | ⭐⭐⭐⭐⭐ | 高频 | 65B 单卡 48GB，三件套 |
| Q3 DoRA | ⭐⭐⭐⭐ | 中频 | +5-10%，magnitude × direction |
| Q4 选型决策 | ⭐⭐⭐⭐ | 高频 | LoRA 默认，Full-FT 三场景 |

← 返回 [AI 咬文嚼字](../README.md)

← [返回: 咬文嚼字](../README.md)