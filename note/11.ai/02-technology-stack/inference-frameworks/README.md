<!--
module:
  parent: ai
  slug: ai/inference-frameworks
  type: article
  category: 主模块子文章
  summary: 推理框架对比 vLLM / TGI / SGLang / TensorRT-LLM
-->

# 推理框架对比

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：**vLLM / TGI / SGLang / TensorRT-LLM** 四大推理框架横评，帮你根据模型大小 × 硬件 × 场景选型。

---

## 📊 4 大框架横评

| 框架 | 维护方 | 核心特性 | 性能 | 易用性 | 适用 |
|------|--------|---------|------|--------|------|
| **vLLM** | UC Berkeley | PagedAttention + Continuous Batching | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 通用首选 |
| **TGI** | HuggingFace | Rust 实现，HF 生态最深 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | HF 模型 |
| **SGLang** | UC Berkeley | RadixAttention 复杂 prompt | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Agent / 复杂模板 |
| **TensorRT-LLM** | NVIDIA | FP8 极致优化 | ⭐⭐⭐⭐⭐ | ⭐⭐ | NVIDIA 硬件 + 极致性能 |

---

## 🏆 选型决策树

```
Q1: 硬件？
├── NVIDIA A100/H100 → 全部可用
├── AMD MI300 → vLLM / SGLang
├── Apple Silicon (M1/M2/M3) → llama.cpp
└── 国产芯片（昇腾/寒武纪）→ MindIE / vLLM-Ascend

Q2: 模型？
├── LLaMA / Qwen / Mistral 系列 → vLLM 最佳
├── HF 官方模型 → TGI
├── 自定义模型（含复杂模板）→ SGLang
└── 极致性能需求 → TensorRT-LLM

Q3: 场景？
├── 通用聊天 / RAG → vLLM
├── Agent 多轮对话 → SGLang（RadixAttention）
├── 离线批处理 → vLLM
└── 边缘部署 → llama.cpp
```

---

## 📈 性能基准（LLaMA-3-70B，A100x4，128K context）

| 框架 | 吞吐量 (req/s) | TTFT (P50) | TPOT (P50) |
|------|---------------|-----------|-----------|
| vLLM 0.6.0 | 8.5 | 220 ms | 65 ms |
| TGI 2.3.0 | 7.8 | 240 ms | 70 ms |
| SGLang 0.3.0 | 9.1 | 200 ms | 60 ms |
| TensorRT-LLM 0.10 | 10.2 | 180 ms | 55 ms |

---

## 🛠️ vLLM 一键部署示例

```bash
# 安装
pip install vllm

# 启动 OpenAI 兼容服务
vllm serve Qwen/Qwen2.5-72B-Instruct \
  --tensor-parallel-size 4 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.92 \
  --quantization awq \
  --enable-prefix-caching

# 测试
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen2.5-72B-Instruct","messages":[{"role":"user","content":"hi"}]}'
```

---

## 🔗 兄弟章节

- **本专题**：[KV Cache](../kv-cache/README.md) / [PagedAttention](../paged-attention/README.md) / [推理指标](../inference-metrics/README.md)
- **L1**：[MoE 架构](../../01-fundamentals/moe-architecture/README.md) / [Flash Attention](../../01-fundamentals/flash-attention/README.md)
- **LLMOps**：[推理监控](../../08-llmops/) 顺带提

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ TensorRT-LLM 永远最快 | ✅ 编译时间长，小模型 vLLM 反而更快 |
| ❌ SGLang 只适合 Agent | ✅ 通用场景也很快，复杂 prompt 模板是其杀手锏 |
| ❌ TGI 已过时 | ✅ 2.0 后 Rust 重写，性能逼近 vLLM |
| ❌ llama.cpp 只用于 CPU | ✅ Apple Silicon / 部分 GPU 也很强 |