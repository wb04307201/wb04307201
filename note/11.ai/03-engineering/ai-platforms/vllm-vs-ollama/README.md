<!--
module:
  parent: ai-platforms
  slug: ai-platforms/vllm-vs-ollama
  type: deep-dive
  category: 工业级 LLM 部署
  summary: 为什么工业级部署优先选 vLLM 而不是 Ollama —— PagedAttention / 连续批处理 / 量化 / 分布式 / 4 引擎横向对比 / 场景化决策树
-->

# vLLM vs Ollama · 工业级 LLM 部署选型深度专题

> **一句话答案**：Ollama 是「个人电脑的 USB 充电器」—— 即插即用、单机友好；vLLM 是「数据中心的机柜式电源」—— 高吞吐、低延迟、可水平扩展。**场景错配时**任何一方都显得"差"——选型的本质是「**场景 × 负载 × 团队能力**」三维匹配，不是技术先进性排序。

← [返回: AI 平台对比](../README.md)

---

## 0. 面试高频拷问

```
Q：工业级大模型部署，你为什么优先选 vLLM，而不是极简的 Ollama？
```

**回答框架（按 4 层递进）**：

1. **场景区分**：先澄清"Ollama 不是被 vLLM 替代，是各自服务不同人群"
2. **核心差异**：PagedAttention + 连续批处理 → 吞吐量 14-24 倍 vs Ollama
3. **反模式**：列举 Ollama 在工业场景下 5 大失效点（无分布式 / 无 PagedAttention / 调度粗糙 / 监控缺失 / 协议单薄）
4. **何时反选 Ollama**：边缘 / 隐私 / 开发机 / 单 demo / 团队没有 GPU 运维能力

完整 5-7 道精选面试题见 [13.split-hairs/11.ai/inference-engine-selection](../../../13.split-hairs/11.ai/inference-engine-selection/README.md)。

---

## 1. 子章节导航

| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [PagedAttention 原理](01-paged-attention.md) | vLLM 为什么比传统方案快 14-24 倍？KV cache 显存碎片化怎么解？ |
| 02 | [KV cache 管理](02-kv-cache-management.md) | 显存碎片化、prefix sharing、beam search 显存爆炸如何处理？ |
| 03 | [批处理策略对比](03-batching-strategies.md) | 静态批处理 vs 动态批处理 vs 连续批处理，谁是工业部署最优？ |
| 04 | [量化与显存估算](04-quantization.md) | GPTQ / AWQ / FP8 / INT4 / INT8 怎么选？4 种量化对吞吐的影响？ |
| 05 | [分布式推理](05-distributed-inference.md) | 单卡放不下时，张量并行 / 流水线并行 / 序列并行怎么组合？ |
| 06 | [Benchmark 数据](06-benchmark-data.md) | 实测吞吐量 / 首 token 延迟 / 显存占用，A100/H100/4090 横向对比 |
| 07 | [四引擎横向对比](07-vs-tgi-lmdeploy.md) | vLLM / TGI / LMDeploy / Ollama 全维度对比表 |
| 08 | [场景化决策树](08-decision-tree.md) | 「我是 X 场景，应该选 Y」的流程图 + 推荐配置 |

---

## 2. 一句话选型速查

| 场景 | 推荐引擎 | 配置示例 |
|------|---------|---------|
| 个人开发机 / 笔记本 | **Ollama** | `ollama run qwen2.5:7b` |
| 边缘设备 / 隐私（数据不出本地）| **Ollama** + 量化 | `ollama run qwen2.5:7b-q4` |
| 中小企业内网（≤100 QPS）| **vLLM** 单卡 | `python -m vllm.entrypoints.openai.api_server --model Qwen2.5-7B-Instruct --gpu-memory-utilization 0.9` |
| 工业级 API（100-1k QPS）| **vLLM** + 多卡 TP | 同上加 `--tensor-parallel-size 4` |
| 超大规模（10k+ QPS）| **vLLM** + 分布式 + 缓存 + 负载均衡 | 多节点 TP+PP + vLLM + Redis prefix cache + APISIX |
| HuggingFace 生态重度用户 | TGI | 优先集成 transformers 生态 |
| 国内中文推理极致优化 | LMDeploy（上海 AI Lab）| 国产引擎，TurboMind 后端 |
| 多模态 + 服务端推理 | vLLM 0.6+ | 已支持 LLaVA / Qwen-VL |

---

## 3. 反直觉点

- ⚠️ **Ollama 不是"低配版 vLLM"**：底层 llama.cpp（C++），优化方向是「单进程 CPU/GPU 混合推理 + 模型量化的极致压缩」。vLLM 底层是 PyTorch + 自定义 CUDA 算子（PagedAttention + FlashAttention），优化方向是「高并发 GPU 服务化」。
- ⚠️ **「Ollama 简单」不等于「Ollama 慢」**：在 4090 单卡 7B 模型上 Ollama 和 vLLM 差距 < 30%；一旦上多卡 + 高并发，vLLM 反超 Ollama 14-24 倍（参考 [06-benchmark](06-benchmark-data.md)）。
- ⚠️ **「vLLM 工业级」不代表「永远最优」**：LMDeploy 在中文模型上有时比 vLLM 快（TurboMind 自研 kernel）；TGI 在 transformers 集成度上最丝滑。

---

## 4. 关键源头引用

- [vLLM Paper (SOSP'23)](https://arxiv.org/abs/2309.06180) —— PagedAttention 原始论文
- [vLLM 官方文档](https://docs.vllm.ai/) —— 含 benchmark + 部署指南
- [Ollama 官方文档](https://ollama.com/) —— 模型库 + REST API
- [LMDeploy 官方仓库](https://github.com/InternLM/lmdeploy) —— 上海 AI Lab
- [TGI 官方文档](https://huggingface.co/docs/text-generation-inference) —— HuggingFace

---

## 5. 速查 · 关联资源

- **餐厅叙事**：[12.story/39-ai-private-deployment.md](../../../../12.story/39-ai-private-deployment.md) —— 阿明餐厅从 Ollama 本地试跑到 vLLM 上生产的演进
- **面试题**：[13.split-hairs/11.ai/inference-engine-selection](../../../13.split-hairs/11.ai/inference-engine-selection/README.md) —— 5-7 道精选题
- **同类平台**：[coze](../coze.md) · [dify](../dify.md) · [langgraph](../langgraph.md) · [spring-ai-vs-platforms](../spring-ai-vs-platforms.md)

← [返回: AI 平台对比](../README.md)
