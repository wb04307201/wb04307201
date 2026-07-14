<!--
module:
  parent: ai
  slug: ai/yarn-context-extension
  type: article
  category: 主模块子文章
  summary: YaRN / RoPE 扩展：百万级 context 长度
-->

# YaRN / RoPE 长度扩展

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：YaRN = **"调整频率基数" + NTK-aware + 注意力缩放**，**把 LLaMA 2K context 扩展到 128K-1M**。Nous Research 2023，Qwen-72B / Llama-3-8B-1M 全部采用。

---

## 🎯 问题：RoPE 的长度外推困境

RoPE 训练在 2K context，推理时想用 32K 会怎样？

```
训练时旋转角度：mθ, m ∈ [0, 2047]
推理时旋转角度：mθ, m ∈ [0, 32767]

→ 高维度（i 较大）旋转太快 → 注意力模式混乱 → PPL 爆炸
```

**结论**：RoPE 训练完后，无法直接用更长 context。

---

## 📐 4 大扩展方案

### 1. Position Interpolation（PI，Meta 2023）

**核心**：把所有位置除以 scale factor。

```python
# scale = 32768 / 4096 = 8
m_new = m / 8  # 把 32K 位置映射回 4K 范围
```

**优点**：简单，仅需微调 1000 步  
**缺点**：高频信息丢失

### 2. NTK-aware（Reddit 2023）

**核心**：只调整频率基数 base，不缩放位置。

```python
# base 从 10000 → 10000 * scale^(d/(d-2))
base_new = 10000 * (32768/4096) ^ (d/(d-2))
```

**优点**：保留高频信息，无需微调  
**缺点**：短 context 性能略降

### 3. YaRN（Nous Research 2023）

**核心**：PI + NTK-aware + 注意力缩放三者结合。

```python
def yarn_get_mscale(scale=1, mscale=0.1):
    if scale <= 1:
        return 1.0
    return 0.1 * math.log(scale) + 1.0

# 三步：
# 1. 低维度用 NTK-aware
# 2. 高维度用 PI
# 3. 注意力除以 sqrt(d) * mscale
```

**优点**：效果最好，可扩展到 128K-1M  
**缺点**：实现复杂，需少量微调

### 4. ABF（Adjusted Base Frequency，Meta 2024）

**核心**：动态调整 base，加上 NTK-by-parts。

```python
# 根据维度分段用不同 base
ramp = max(0, (dim/2 - i) / (dim/2))  # 0 → 1 渐变
base_new = base * scale^(1 - ramp)
```

**优点**：Llama-3 8B 1M context SOTA 方案

---

## 📊 4 大方案对比

| 方案 | 训练成本 | 1M 效果 | 实施 | 代表 |
|------|---------|---------|------|------|
| PI | 中 | ⭐⭐ | ⭐⭐⭐⭐⭐ | LLaMA-1-32K |
| NTK-aware | 无 | ⭐⭐⭐ | ⭐⭐⭐⭐ | CodeLlama-100K |
| **YaRN** | 低 | ⭐⭐⭐⭐ | ⭐⭐⭐ | Qwen-72B-128K |
| ABF | 低 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Llama-3-8B-1M |

**YaRN + ABF 是 2024 SOTA**。

---

## 🛠️ 实操：Qwen-72B 应用 YaRN

```python
from transformers import AutoModelForCausalLM

# 1. 加载模型
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-72B")

# 2. 应用 YaRN 配置
model.config.rope_scaling = {
    "type": "yarn",
    "factor": 4.0,  # 32K → 128K
    "original_max_position_embeddings": 32768,
}

# 3. 微调（可选，1000 步足够）
# 推荐数据：长文 QA / 长文摘要
```

---

## 🧠 数学直觉

**频率基数 base 影响什么？**

```python
θ_i = base^(-2i/d)  # 第 i 维的旋转速度

# base 越大 → θ_i 越小 → 旋转越慢 → 长位置仍能保持稳定
# base 越小 → θ_i 越大 → 旋转越快 → 短位置精度高
```

**YaRN 关键洞察**：
- **低维度**（i 小）：频率小，旋转慢，长位置问题不大 → 用 NTK-aware 调整
- **高维度**（i 大）：频率大，旋转快，长位置会"转过圈" → 用 PI 缩放

---

## 🔗 兄弟章节

- **L1**：[RoPE 位置编码](../../01-fundamentals/rope-position-encoding/README.md)
- **本专题**：[Lost in middle](../lost-in-middle/README.md) / [KV Cache](../kv-cache/README.md)
- **咬文嚼字**：[面试深挖](../../../../../13.split-hairs/11.ai/llm-benchmark/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 训练 2K 就能用 32K | ✅ 直接用 PPL 爆炸 |
| ❌ YaRN 不用微调 | ✅ 通常仍需 1000 步微调 |
| ❌ Context 越长越好 | ✅ 召回率仍受 Lost in middle 限制 |
| ❌ 长度扩展是模型本身能力 | ✅ 是位置编码 + 微调的组合 |

← [返回 L2 技术栈](../README.md)