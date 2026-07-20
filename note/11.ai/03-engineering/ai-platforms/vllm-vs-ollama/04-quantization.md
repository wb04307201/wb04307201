<!--
module:
  parent: ai-platforms/vllm-vs-ollama
  slug: ai-platforms/vllm-vs-ollama/04-quantization
  type: topic
  category: 模型量化
  summary: GPTQ / AWQ / FP8 / INT4 量化对比 + 吞吐影响 + 何时上 INT4、风险与反模式
-->

# 模型量化 · 显存与吞吐的杠杆

> **一句话**：量化是把「显存宽裕度」变成「吞吐量」的 4-8x 杠杆 —— 关键选「4 bit 还是 8 bit」、用什么方法（GPTQ / AWQ / FP8 / GGUF）。

← [返回: vLLM vs Ollama](../README.md)

---

## 1. 量化谱

| 精度 | 单参数字节 | 7B 模型总占用 | 推理速度 | 质量损失 |
|------|----------|----------------|----------|----------|
| FP32 | 4 | 28 GB | 1x | 0% |
| FP16 / BF16 | 2 | 14 GB | 2x | < 0.1% |
| **INT8 (W8A8)** | 1 | 7 GB | 4x | < 0.5% |
| **FP8 (E4M3)** | 1 | 7 GB | 4x | < 0.5% |
| **INT4 (W4A16)** | 0.5 | **3.5 GB** | **6-8x** | < 1% |
| **INT3 (GPTQ)** | 0.375 | **2.6 GB** | 8-10x | 1-2% |
| **INT2 (experimental)** | 0.25 | 1.8 GB | 10-12x | 5%+ |

> 关键概念：**W（权重）bit × A（激活）bit**。W4A16 是「权重 4 bit、激活 16 bit」，推理时 activation 仍要反量化。

---

## 2. 主流方法对比

### 2.1 GPTQ

- **全名**：Generalized Post-Training Quantization
- **bit**：4 / 3 / 8
- **算法**：二阶优化（OBD），最小化量化前后输出误差
- **数据**：需校准集（128-256 条）
- **耗时**：单卡几十分钟
- **论文/库**：[Frantar et al., ICLR 2023](https://arxiv.org/abs/2210.17323)；[AutoGPTQ](https://github.com/AutoGPTQ/AutoGPTQ)
- **缺点**：4bit 以下的细粒度（小模型）容易掉点

### 2.2 AWQ

- **全名**：Activation-aware Weight Quantization
- **bit**：4
- **算法**：保护「高频激活对应权重」，避开敏感 1% 权重
- **数据**：需校准集
- **优势**：4bit 质量优于 GPTQ，推理速度接近 FP16
- **论文/库**：[Lin et al., MLSys 2024](https://arxiv.org/abs/2306.00978)；[mit-han-lab/llm-awq](https://github.com/mit-han-lab/llm-awq)
- **趋势**：2024 后主流方案

### 2.3 FP8（E4M3 / E5M2）

- **bit**：8 / 1 byte
- **硬件**：H100 / H200 原生支持（Tensor Core FP8）
- **算法**：直接量化，无需复杂校准
- **优势**：硬件原生加速，无反量化开销
- **参考**：[NVIDIA Hopper FP8 whitepaper](https://www.nvidia.com/en-us/data-center/h100/)
- **趋势**：2024 推理引擎默认支持（H100 时代）

### 2.4 SmoothQuant

- **bit**：W8A8（权重 8 + 激活 8）
- **算法**：迁移 activation 量化难度到 weight 端
- **优势**：A8 也能完整量化，推理速度接近 FP8
- **场景**：H100 / A100 通用方案

### 2.5 GGUF（llama.cpp / Ollama 专用）

- **bit**：Q2 / Q3 / Q4 / Q5 / Q6 / Q8_K
- **算法**：混合精度 + 分组量化
- **优势**：CPU/GPU 都能跑，模型可单文件分发
- **场景**：Ollama / LM Studio / 移动端

---

## 3. vLLM 量化实战

### 3.1 支持列表

| 格式 | vLLM 支持 | 来源 |
|------|-----------|------|
| FP16 / BF16 | ✅ | 原生 |
| FP8（E4M3）| ✅ | H100/H200 原生 |
| GPTQ | ✅ | auto-gptq 库 |
| AWQ | ✅ | autoawq 库 |
| SmoothQuant | ✅ | NVIDIA TensorRT-LLM 后端 |
| BitsAndBytes（NF4）| ✅ | 推理时量化，加载慢 |
| GGUF | ❌（需先转 HF）| llama.cpp 后端 |

### 3.2 推荐配置

| 硬件 | 模型大小 | 推荐量化 |
|------|---------|---------|
| H100 80GB | 70B 以下 | BF16（无必要量化）|
| H100 80GB | 70-200B | FP8 |
| A100 80GB | 13-70B | BF16 / INT8 |
| A100 40GB | 7-13B | AWQ-INT4 |
| 4090 24GB | 7-13B | AWQ-INT4 |
| 4090 24GB | 70B | GPTQ-INT4（多卡 TP）|

---

## 4. Ollama 量化实战

### 4.1 模型命名约定

```text
qwen2.5:7b              → Q4_0 (默认)
qwen2.5:7b-q4_K_M       → Q4_K 中等质量
qwen2.5:7b-q8_0         → Q8 (高质量)
qwen2.5:7b-instruct-q5_K_M → 指令微调版
```

### 4.2 优势 / 限制

- ✅ 一键拉取 / 自动量化
- ✅ CPU 也能跑（内存 > 16 GB 就能跑 7B Q4）
- ⚠️ GPU 加速相对弱（vLLM 比 Ollama GPU 推理快 2-3x）
- ⚠️ 不支持 FP8 / SmoothQuant

---

## 5. 反模式

### ⚠️ 反模式 1：INT3 / INT2 量化「为了显存不顾质量」

- INT3 推理质量掉 1-2% 不致命，但某些下游任务（精准推理、数字计算）会断崖式下降
- 工业场景：**默认 INT4**，非要 INT3 需严格 A/B 测试

### ⚠️ 反模式 2：忽略「反量化开销」

- W4A16 = 权重 4bit、激活 16bit
- **推理时反量化权重到 FP16** → 计算仍是 FP16
- 显存节省主要来自权重的 4x，激活仍占用全精度显存
- 长上下文场景：激活 KV cache 占比 60%+，W4A16 显存省不到 4x

### ⚠️ 反模式 3：测试一致性 → 上线掉点

- 量化在某些 prompt 上质量下降，肉眼难发现
- 必走流程：内部 benchmark + A/B 测试 + 监控质量指标

### ⚠️ 反模式 4：FP8 强行上 A100

- A100 不支持 FP8 Tensor Core，会回落到 FP16 + 软件模拟
- FP8 仅 H100 / H200 真有效

---

## 6. 速查 · 选型决策

```text
你的硬件是？
├─ H100/H200 → 直接 BF16 或 FP8
├─ A100 80G → BF16（70B 内） / INT8（13B 以下）
├─ A100 40G → AWQ-INT4
├─ 4090 24G → AWQ-INT4（7B-13B）
├─ 4090 24G → GPTQ-INT4（30B-70B 多卡）
└─ 只有 CPU → Ollama Q4_K_M (GGUF)
```

---

## 7. 一句话总结

> **量化是性价比最高的显存杠杆，但要在「质量损失」「硬件适配」「反量化开销」三角约束中选最优点——盲上最激进的 INT4 反而是反模式。**

---

← [返回: vLLM vs Ollama](../README.md) · 上一章：[03-batching-strategies](03-batching-strategies.md) · 下一章：[05-distributed-inference](05-distributed-inference.md)
