<!--
module:
  parent: ai
  slug: ai/llm-inference-optimization
  type: index
  category: 主模块子文章
  summary: LLM 推理优化大专题索引（10 章）
-->

# LLM 推理优化大专题（10 章）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：让 LLM 在生产环境跑得"**快、稳、省**"。10 章覆盖从单 token 延迟到千 QPS 吞吐的全链路优化。

---

## 📚 10 章完整目录

### L1 基础（4 章）

| # | 章节 | 一句话核心 | 关键数字 |
|---|------|----------|---------|
| 1 | [KV Cache](../kv-cache/README.md) | 推理时缓存 K/V 矩阵 | 7B 模型 8K 占 4GB |
| 2 | [Flash Attention 2/3](../../01-fundamentals/flash-attention/README.md) | 分块计算 + IO 感知 | 128K context 显存 O(n) |
| 3 | [PagedAttention](../paged-attention/README.md) | 借鉴 OS 虚拟内存分页 | 显存利用率 40% → 96% |
| 4 | [Continuous Batching](../continuous-batching/README.md) | 请求级动态调度 | 吞吐量提升 23x |

### L2 算法（3 章）

| # | 章节 | 一句话核心 | 关键数字 |
|---|------|----------|---------|
| 5 | [Speculative Decoding](../speculative-decoding/README.md) | 小模型预测 + 大模型验证 | 加速 2-3x（batch=1）|
| 6 | [权重量化](../weight-quantization/README.md) | FP16 → INT4/NF4 | 显存省 4x，几乎无损 |
| 7 | [MoE 推理优化](../moe-inference/README.md) | 专家并行 + 通信优化 | 671B 8x A100 可服务 |

### L3 工程（3 章）

| # | 章节 | 一句话核心 | 关键数字 |
|---|------|----------|---------|
| 8 | [推理性能指标](../inference-metrics/README.md) | TTFT / TPOT / Throughput | 交互式 TTFT < 200ms |
| 9 | [推理框架对比](../inference-frameworks/README.md) | vLLM / TGI / SGLang / TensorRT-LLM | 70B 选 vLLM 起步 |
| 10 | 推理部署实战 | Prometheus 监控 + 容量规划 | 7B 1 卡 A100 ≈ 30 QPS |

---

## 🎯 选型速查

```
生产 LLM 服务 = vLLM + Continuous Batching + PagedAttention + INT4 量化
长上下文 = + Flash Attention + GQA
Agent / 复杂 prompt = + SGLang RadixAttention
极致性能 = + TensorRT-LLM + FP8
```

---

## 🔗 兄弟章节

- **L1**：[Transformer](../../01-fundamentals/transformer/README.md) / [注意力机制](../../01-fundamentals/attention-mechanism/README.md) / [MoE](../../01-fundamentals/moe-architecture/README.md)
- **LLMOps**：[08-llmops](../../08-llmops/README.md) — 监控 + 安全
- **咬文嚼字**：[13.split-hairs/11.ai](../../../../13.split-hairs/11.ai/README.md) — 面试深挖版