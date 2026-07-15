<!--
module:
  parent: ai
  slug: ai/weight-quantization
  type: article
  category: 主模块子文章
  summary: 权重量化 GPTQ/AWQ/GGUF/NF4：精度 vs 显存 vs 速度
-->

# 权重量化（Weight Quantization）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：权重量化 = **把 FP16/FP32 参数 → INT8/INT4/NF4**，**显存降 2-4x**、**推理速度提升 1.5-3x**。GPTQ / AWQ / GGUF / NF4 是 2024-2026 主流 4 大方案。

---

## 📊 4 大方案对比

| 方案 | 量化粒度 | 精度损失 | 显存省 | 代表 | 适用 |
|------|---------|---------|--------|------|------|
| **GPTQ** | 逐层（per-layer） | < 0.5% | 2-3x | LLaMA / Qwen | GPU 推理 |
| **AWQ** | 逐通道（per-channel） | < 0.3% | 3-4x | LLaMA / Qwen | GPU 推理（保护显著权重）|
| **GGUF** | 多种（Q4_K_M / Q8_0） | 1-2% | 2-4x | llama.cpp | CPU/Mac 推理 |
| **NF4** | 4-bit NormalFloat | 1% | 4x | QLoRA 训练 | 训练专用 |

---

## 🧮 量化数学

### INT4 对称量化

```python
# 1. 计算 scale 和 zero point
scale = (max - min) / (qmax - qmin)  # qmax=15, qmin=-15 for INT4
zero_point = qmin - min / scale

# 2. 量化
quantized = round(weight / scale) + zero_point  # → INT4

# 3. 反量化（推理时）
dequantized = (quantized - zero_point) * scale  # → FP16
```

### GPTQ 的关键：Hessian 引导

```python
# 逐层最小化重建误差
H = X^T @ X  # Hessian 矩阵
for block in layer_blocks:
    # 找到最优量化顺序
    order = inverse_hessian_order(H)
    # 量化并补偿误差到下一层
    quantize_with_error_compensation(block, order)
```

---

## 📈 性能实测（LLaMA-7B）

| 方案 | 显存 | tokens/s (A100) | 精度损失 | 量化时间 |
|------|------|----------------|---------|---------|
| FP16 | 14 GB | 1x (基准) | 0% | 0 |
| INT8 (GPTQ) | 7 GB | 1.4x | < 0.5% | 10 min |
| INT4 (GPTQ) | 4 GB | 2.0x | < 1% | 15 min |
| INT4 (AWQ) | 4 GB | 2.3x | < 0.5% | 5 min |
| Q4_K_M (GGUF) | 4.5 GB | 1.8x (CPU) | 1% | 3 min |

---

## 🛠️ 实操代码

```python
# GPTQ 量化
from auto_gptq import AutoGPTQForCausalLM
model = AutoGPTQForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantize_config={"bits": 4, "group_size": 128}
)
model.quantize(calibration_data)  # 校准数据 128 条
model.save_ quantized("llama-7b-gptq-4bit")

# AWQ 量化
from awq import AutoAWQForCausalLM
model = AutoAWQForCausalLM.from_pretrained("Qwen/Qwen2.5-7B")
model.quantize(calibration_data, quant_config={"zero_point": True, "q_group_size": 128})
```

---

## 🔗 兄弟章节

- **本专题**：[KV Cache](../kv-cache/README.md) / [推理框架对比](../inference-frameworks/README.md) / [MoE 推理](../moe-inference/README.md)
- **L1**：[量化原理](../../01-fundamentals/) 顺带提
- **咬文嚼字**：[面试深挖版](../../../13.split-hairs/11.ai/llm-benchmark/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ INT4 一定掉点很多 | ✅ AWQ + 校准集，4-bit 几乎无损 |
| ❌ 量化就是简单截断 | ✅ GPTQ/AWQ 用 Hessian 矩阵引导，精度保护 |
| ❌ 量化后推理一定更快 | ✅ 小 batch 可能更慢（反量化开销） |
| ❌ 校准集越多越好 | ✅ 128 条足够，更多收益边际递减 |
| ❌ 训练用 INT4 一定掉精度 | ✅ QLoRA 用 NF4 训练可保持性能 |

← [返回 L2 技术栈](../README.md)