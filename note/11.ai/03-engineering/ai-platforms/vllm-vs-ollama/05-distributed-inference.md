<!--
module:
  parent: ai-platforms/vllm-vs-ollama
  slug: ai-platforms/vllm-vs-ollama/05-distributed-inference
  type: topic
  category: 分布式推理
  summary: 张量并行 (TP) / 流水线并行 (PP) / 序列并行 (SP) / 数据并行 (DP) —— 多卡 / 多机部署 LLM 的四种切分方式
-->

# 分布式推理 · 多卡多机部署 LLM

> **一句话**：单卡放不下 70B / 200B 模型时，必须切分。vLLM 支持 TP/PP/SP 三维并行组合，Ollama 仅支持朴素多卡分流。

← [返回: vLLM vs Ollama](../README.md)

---

## 1. 4 种并行维度

| 维度 | 切分对象 | 切分方式 | 通信开销 |
|------|---------|---------|---------|
| **TP (Tensor Parallel)** | 单层权重矩阵按行 / 列切 | attention / FFN 内部分布到 N 张卡 | 高（每 step AllReduce）|
| **PP (Pipeline Parallel)** | 不同层切到不同卡（前 22 层 A、后 22 层 B）| 层间流水线 | 中（点对点 send/recv）|
| **SP (Sequence Parallel)** | 长序列的 KV 计算按 token 维度切 | Q / K / V 矩阵分片 | 中（与 TP 配合）|
| **DP (Data Parallel)** | 整个模型复制 N 份，各处理不同 batch | 模型并行副本 | 低（仅数据分发）|

---

## 2. 张量并行 TP（最常用）

### 2.1 切分方式

```
原始 FFN：y = x @ W1 → GeLU → @ W2（单卡）

TP=2 后：
  卡 0：y = x @ W1[前半] → GeLU → @ W2[前半]
  卡 1：y = x @ W1[后半] → GeLU → @ W2[后半]
  ↓
  AllReduce 合并
```

- attention 内 Q/K/V 投影按 head 维度切（每个卡负责部分 head）
- FFN 内 up / gate / down 投影按 hidden 维度切

### 2.2 vLLM 配置

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen2.5-72B-Instruct \
    --tensor-parallel-size 4 \
    --pipeline-parallel-size 1 \
    --gpu-memory-utilization 0.9
```

### 2.3 适用场景

- 模型权重需要切分（如 70B 单卡放不下）
- 卡间 NVLink 互联（推荐 A100 / H100 互联，PCIe 会严重拖慢）

---

## 3. 流水线并行 PP

### 3.1 切分方式

```
Layer 0-21 → 节点 A（4 张 H100）
Layer 22-43 → 节点 B（4 张 H100）
Layer 44-79 → 节点 C（4 张 H100）
```

### 3.2 Pipeline Bubble 问题

朴素 PP 有「流水线气泡」：首阶段执行后，下游还在等数据。
- 解法：micro-batch（vLLM 0.5+ 自动启用）
- 现代 PP 配合 1F1B（one-forward-one-backward）调度

### 3.3 vLLM 配置

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen2.5-200B \
    --tensor-parallel-size 8 \
    --pipeline-parallel-size 4  # 4 个节点
```

---

## 4. 序列并行 SP

### 4.1 场景

- 超长上下文（32k+）
- 单卡显存放不下 KV cache
- 把 sequence 维度切到多卡（每卡算一部分 attention）

### 4.2 与 TP 关系

- SP 与 TP 通常 **正交配合**
- TP 切权重维度，SP 切 sequence 维度
- 现代 LLM 推理（vLLM 0.6+）支持 TP×SP 二维并行

---

## 5. 数据并行 DP（请求级并行）

### 5.1 场景

- 模型已能单卡放下（如 7B / 13B）
- 需要横向扩展（10+ 张卡）
- **整个模型复制 N 份，各自处理不同 batch**

### 5.2 vLLM 配置

vLLM 0.6+ 支持 DP：

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen2.5-7B-Instruct \
    --data-parallel-size 8  # 8 个 model replica
```

---

## 6. Ollama / llama.cpp 怎么做分布式？

| 引擎 | 支持情况 | 限制 |
|------|---------|------|
| Ollama | 朴素多 GPU（模型层间分流） | 不支持 TP / PP / SP，分卡策略固定 |
| llama.cpp | 单进程多 GPU + RPC backend | 模型层分片（layer split），不是矩阵级 TP |
| LMDeploy | 多 GPU（W4A16 量化） | 支持 TP 但不及 vLLM 灵活 |

**为什么 Ollama 不做 TP？**
- 设计目标是「单机体验」，TP 的复杂度（card 间通信、调度）对单机场景是过度工程
- Ollama 把多卡视为「层间分流」，不是「权重切片」

---

## 7. 工业部署范式

### 7.1 推荐组合

| 模型规模 | 推荐方案 |
|---------|---------|
| ≤ 13B | 单卡 FP16 |
| 13B-70B | 单机 TP=2~4（NVLink 互联）|
| 70B-200B | 单机 TP=8 + 量化 |
| 200B+ | TP=8 多机 + PP=2-4 |
| 超高并发（10k+ QPS）| DP=多副本 + 负载均衡 + 缓存层 |

### 7.2 反模式

- ⚠️ **「能用 TP 就 TP」**：TP 通信成本高，14B 模型优先单卡，TP 是放不下时的方案
- ⚠️ **「PP 可以无脑堆」**：PP 有 bubble 损耗，rank 数过多反而拖慢首 token
- ⚠️ **「TP + 量化」**省显存：W4 量化后的 TP 切片是 4bit × N 卡，对 NVLink 带宽敏感
- ⚠️ **「DP = 简单横向扩展」**：DP 受模型权重复制限制，DB 越多要算 TCO（总拥有成本）

---

## 8. 速查 · 多卡切分公式

**TP 大小估算**：
```
min_TP = ceil(模型权重显存 / 单卡可用显存)
```
例如：72B BF16 = 144 GB，A100 80GB → min_TP = 2，常配 TP=4 给 KV 留余地。

**GPU 互联推荐**：
- NVLink / NVSwitch：性能最好，A100/H100 推荐
- PCIe 4.0 x16：可接受，但 TP>4 时通信成瓶颈
- InfiniBand：跨机互联，PP 必须

---

## 9. 一句话总结

> **TP 切权重救显存，PP 切层数救模型规模，SP 切序列救长上下文，DP 切请求救并发——维度正交，但工业上常常组合使用并配 NVLink 互联。**

---

← [返回: vLLM vs Ollama](../README.md) · 上一章：[04-quantization](04-quantization.md) · 下一章：[06-benchmark-data](06-benchmark-data.md)
