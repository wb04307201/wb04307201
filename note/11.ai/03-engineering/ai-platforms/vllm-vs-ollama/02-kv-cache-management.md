<!--
module:
  parent: ai-platforms/vllm-vs-ollama
  slug: ai-platforms/vllm-vs-ollama/02-kv-cache-management
  type: topic
  category: KV cache 显存管理
  summary: KV cache 显存碎片化 + prefix sharing + beam search 显存爆炸 + cache eviction 策略
-->

# KV cache 管理 · 显存碎片化与共享

> **一句话**：工业部署下 KV cache 占显存 60-80%，管理策略直接决定并发上限。三大技术点：分页（PagedAttention）+ 共享（Prefix Sharing）+ 替换（Eviction Policy）。

← [返回: vLLM vs Ollama](../README.md)

---

## 1. KV cache 显存占用公式

```text
KV cache 大小 ≈ 2 × num_layers × num_heads × head_dim × seq_len × batch_size × dtype_bytes
```

| 模型 | 单 token KV cache (FP16) | 4096 上下文 / seq |
|------|--------------------------|---------------------|
| LLaMA-7B | ~0.4 MB | **1.6 GB** |
| LLaMA-70B | ~4.0 MB | **16 GB** |
| Qwen-72B | ~5.0 MB | **20 GB** |

> 70B 模型单请求 16 GB，4090 24 GB 显存 → **只能并发 1 个**！KV cache 管理成生死问题。

---

## 2. 三大核心机制

### 2.1 分页（PagedAttention）

详见 [01-paged-attention](01-paged-attention.md)。核心是**逻辑连续 / 物理离散 + 共享 block 池**。

### 2.2 共享（Prefix Sharing）

- **场景**：系统 prompt / Few-shot 示例 / RAG 长文档
- **机制**：多个序列的前 N 个 block 指向**同一组物理 block**，写时复制（Copy-on-Write）
- **显存收益**：30-60%
- **启用**：vLLM 默认开启（0.4+），TGI 通过 `max_batch_prefill_tokens` 控制，Ollama / llama.cpp 不支持

### 2.3 替换（Eviction Policy）

显存不够时的淘汰策略（仅适用于 prefix cache，非主 KV cache）：

| 策略 | 描述 | 命中率 |
|------|------|--------|
| LRU | 最近最少使用 | 中 |
| LFU | 最不经常使用 | 中高 |
| Static | 不淘汰，按 prefix 复用 | 高（负载稳定时）|
| ARC | 自适应替换缓存 | 最高 |

vLLM 默认 LRU；自研引擎可定制。

---

## 3. 反模式 · Beam Search 显存爆炸

### 3.1 问题

Beam search 在每个 step 保留 top-k 候选，所有候选都要 KV cache：

```text
beam_size=4, seq_len=2048, LLaMA-7B:
单 beam KV cache = 1.6 GB
4 个 beam = 6.4 GB（不考虑共享）
```

### 3.2 vLLM 解法：Beam Search 的 block 共享

- 不同 beam 在分歧点之前**共享前缀 block**
- 仅分歧后各自独立 block
- 显存从 `beam_size × full_seq` 降到 `full_seq + beam_size × divergence`

### 3.3 实测对比

| 引擎 | beam=4, 2048 ctx | 显存占用 |
|------|------------------|---------|
| HuggingFace generate | 6.4 GB | - |
| vLLM（带 block 共享）| **2.1 GB** | -67% |

---

## 4. 长上下文策略

### 4.1 显存瓶颈

| 上下文长度 | LLaMA-7B KV cache |
|-----------|---------------------|
| 4k | 1.6 GB |
| 32k | 12.8 GB |
| 128k | 51.2 GB |
| 1M | 410 GB（不可能单卡） |

### 4.2 工业方案

| 方案 | 适用 | 显存收益 |
|------|------|---------|
| **PagedAttention + KV 量化** | 4k-32k | 4x |
| **FlashAttention 2** | 任意 | 计算 O(n²) → O(n log n) |
| **Sliding Window** | > 32k | 仅保留近 N token |
| **Sparse Attention** | > 100k | LongLoRA / Landmark |
| **Mamba / SSM 替代** | > 1M | 状态空间模型 |

---

## 5. 速查 · 关键参数

| 参数 | 默认 | 含义 |
|------|------|------|
| `--gpu-memory-utilization` | 0.9 | 显存利用率上限 |
| `--block-size` | 16 | KV block 大小（token 数） |
| `--max-num-seqs` | 256 | 最大并发序列数 |
| `--max-model-len` | 模型上下文 | 单请求最大长度 |
| `--enable-prefix-caching` | True | 启用 prefix sharing |
| `--swap-space` | 0 GB | 卸载到 CPU 内存的容量 |

---

## 6. 反模式 · 调参陷阱

- ⚠️ **`gpu-memory-utilization=1.0`**：会导致 OOM，预留 5-10% 给 CUDA context
- ⚠️ **`block-size` 越小越好**：太小（4 以下）block table 过大，吞吐反而下降
- ⚠️ **max-num-seqs 越大越好**：超过 KV 容量会触发 swap，反而降速
- ⚠️ **prefix caching 在混乱负载下适得其反**：命中率 < 30% 时关掉

---

## 7. 一句话总结

> **KV cache 管理 = 分页（利用率）+ 共享（命中率）+ 替换（淘汰策略），三机制叠加才能撑住工业级并发。**

---

← [返回: vLLM vs Ollama](../README.md) · 上一章：[01-paged-attention](01-paged-attention.md) · 下一章：[03-batching-strategies](03-batching-strategies.md)
