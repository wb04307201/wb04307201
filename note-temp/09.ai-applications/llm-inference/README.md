# LLM Inference（LLM 推理工程）

> **定位**：MOC——LLM 推理工程主题索引，覆盖 KV Cache / Flash Attention / 推理框架 / 推理指标 / 推理优化 / vLLM vs Ollama / MoE 推理 / Paged Attention / 推测解码 / 连续批处理 / 权重量化。
> **继承规范**：[../SPEC.md](../SPEC.md)

## 主题清单

| # | 子主题 | 路径 | 摘要 |
|---|--------|------|------|
| 1 | Flash Attention | [flash-attention/](flash-attention/README.md) | Flash Attention 算法 + IO 复杂度优化 |
| 2 | KV Cache | [kv-cache/](kv-cache/README.md) | KV Cache 原理 + MQA / GQA / MLA |
| 3 | Paged Attention | [paged-attention/](paged-attention/README.md) | vLLM 的分页注意力机制 |
| 4 | 连续批处理 | [continuous-batching/](continuous-batching/README.md) | Continuous Batching + 动态批处理 |
| 5 | 推测解码 | [speculative-decoding/](speculative-decoding/README.md) | Speculative Decoding 加速推理 |
| 6 | 权重量化 | [weight-quantization/](weight-quantization/README.md) | INT8 / INT4 / GPTQ / AWQ / bitsandbytes |
| 7 | 推理框架 | [inference-frameworks/](inference-frameworks/README.md) | vLLM / TGI / LMDeploy / TensorRT-LLM 框架对比 |
| 8 | 推理指标 | [inference-metrics/](inference-metrics/README.md) | TTFT / TPOT / Throughput / 显存占用 |
| 9 | 推理优化专题 | [llm-inference-optimization/](llm-inference-optimization/README.md) | 10 章推理优化综述 |
| 10 | MoE 推理 | [moe-inference/](moe-inference/README.md) | Mixture of Experts 推理特性 |
| 11 | vLLM vs Ollama | [vllm-vs-ollama/](vllm-vs-ollama/README.md) | 8 章 vLLM 与 Ollama 横评 + 决策树 |

## 阅读路径

```text
先建全景            llm-inference-optimization（10 章综述）+ inference-metrics（指标）
    ↓
核心机制             flash-attention（IO 优化）+ kv-cache（显存复用）+ paged-attention（分页）
    ↓
加速策略             continuous-batching（吞吐）+ speculative-decoding（延迟）+ weight-quantization（显存）
    ↓
框架选型             inference-frameworks（框架对比）+ vllm-vs-ollama（生产 vs 本地）
    ↓
特殊架构             moe-inference（MoE 推理特性）
```

## 关联主题

- [../agent/](../agent/) — Agent 架构（推理是 Agent 基础设施）
- [../rag/](../rag/) — RAG（检索 + 推理协同）
- [../prompts/](../prompts/) — Prompt 工程
- [../../08.ai-foundations/](../../../note-temp/08.ai-foundations/) — AI 基础（Transformer / Attention）

## 尚未迁移的推理相关章节

以下推理相关主题仍在 `note/11.ai/`，待后续任务迁入本 MOC：

- `note/11.ai/01-fundamentals/attention-mechanism/` — Attention 机制基础
- `note/11.ai/01-fundamentals/transformer/` — Transformer 架构
- `note/11.ai/01-fundamentals/moe-architecture/` — MoE 架构基础
- `note/11.ai/01-fundamentals/rope-position-encoding/` — RoPE 位置编码
- `note/11.ai/04-architecture/llm-control-evolution/` — LLM 控制演进

---

← [返回 09.ai-applications](../README.md)
