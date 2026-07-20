<!--
module:
  parent: ai-platforms/vllm-vs-ollama
  slug: ai-platforms/vllm-vs-ollama/01-paged-attention
  type: topic
  category: vLLM 核心创新
  summary: PagedAttention —— vLLM 借鉴 OS 虚拟内存分页机制解决 KV cache 显存碎片化，吞吐量提升 14-24 倍
-->

# PagedAttention · vLLM 核心创新原理

> **一句话**：把操作系统的「虚拟内存分页」思想搬到 KV cache 上，把连续的逻辑 KV 切成固定大小的「物理 block」，显存不再碎片化，从而支持更长上下文 + 更大并发。

← [返回: vLLM vs Ollama](../README.md)

---

## 1. 问题：KV cache 显存碎片化

### 1.1 传统方案的困境

Transformer 自回归推理时，每生成一个新 token 都要把 KV cache 存下来给后续 attention 用。问题：

```text
┌─────────────────────────────────────────┐
│ 序列 A  ┌────┐ ← 输出 token 5            │
│         │ KV │                            │
│ 序列 B          ┌──────┐ ← 输出 token 12   │
│                 │ KV   │ ← 中间浪费！      │
│ 序列 C                  ┌─────┐ ← token 3 │
│                        │ KV  │            │
└─────────────────────────────────────────┘
```

每个序列长度不一致，**预分配连续显存**导致：
- 显存浪费率 60-80%（必须按最大长度预分配）
- 长序列独占一大块显存，即使大部分空着
- 并发数上不去（多序列共享不足）

### 1.2 量化数据

| 模型 | 上下文长度 | KV cache/请求 (FP16) | 预分配浪费率 |
|------|-----------|---------------------|--------------|
| LLaMA-7B | 2048 | ~1.3 GB | ~70% |
| LLaMA-13B | 4096 | ~5.2 GB | ~80% |
| Qwen-72B | 32768 | ~30 GB | ~90% |

**算力翻倍但显存不够用 → 推理服务化卡在「并发 = 显存利用率」**。

---

## 2. 解法：PagedAttention（vLLM SOSP'23）

### 2.1 核心类比

| OS 虚拟内存 | vLLM KV cache |
|------------|---------------|
| 进程虚拟地址空间 | 序列逻辑 KV 位置 |
| 物理页（4KB） | Physical KV block（固定 token 数） |
| 页表（Page Table） | Block Table（每序列一张） |
| MMU 硬件查页表 | attention kernel 内查 block table |

**核心机制**：
1. 把每个序列的 KV 切成**固定大小**的 block（默认 16 token / block）
2. 每个序列维护一张 **block table**，记录「逻辑 block → 物理 block」映射
3. attention 计算时查 block table，**逻辑上连续、物理上离散**
4. block 池在所有序列间共享，不再独占

### 2.2 显存利用率提升

| 指标 | 传统 (HuggingFace) | vLLM PagedAttention |
|------|---------------------|---------------------|
| 显存浪费率 | 60-80% | **< 4%** |
| 同显存并发数 | 1x | **2-4x** |
| 端到端吞吐 | 1x | **14-24x** |

> 注：14-24x 来源于 vLLM 论文与社区 benchmark，仅指 LLaMA-7B + A10G + ShareGPT 数据集。

---

## 3. 进阶：Prefix Sharing（共享前缀）

### 3.1 场景

```text
系统 prompt（500 token）+ 用户问题（50 token）= 共用前缀 500 token
```

多条请求共享同一系统 prompt，PagedAttention 让这些**共享前缀只存一份**。

### 3.2 实现

- 同一前缀的多个序列 → 它们的 block table 前 N 条指向**同一组物理 block**
- 新序列只需分配后半段的 block
- 显存再省 30-50%（视共享率）

### 3.3 实测效果（vLLM 0.4.0）

| 场景 | 显存节省 |
|------|---------|
| 多轮对话（共享 system prompt）| ~40% |
| RAG（共享 long context）| ~60% |
| Few-shot（共享示例 prefix）| ~50% |

---

## 4. 反模式 · 这些情况下 PagedAttention 优势变小

- ⚠️ **极短序列（< 100 token）**：block 切得再细也有固定开销，命中率提升 < 2x
- ⚠️ **小模型（< 1B 参数）+ 大 batch**：HuggingFace 静态方案差距 30% 以内
- ⚠️ **CPU 推理**：Ollama/llama.cpp 在 CPU 上反而比 vLLM 快（vLLM 强依赖 CUDA）

---

## 5. 速查 · 关键算子

- **`block_size`**：默认 16，可调至 8 / 32。越小越细，浪费越少但 block table 越大
- **`num_gpu_blocks`**：总物理 block 数 = 显存预算 / 单 block 大小
- **`max_num_seqs`**：并发上限，受 num_gpu_blocks 约束
- **`enable_prefix_caching`**：开启 prefix sharing（vLLM 0.4+ 默认开启）

---

## 6. 一句话总结

> **PagedAttention 把显存从「独占连续块」改成「共享离散块」，让 KV cache 显存利用率从 20-40% 跃升到 96%+，这是 vLLM 14-24x 吞吐提升的根因。**

---

← [返回: vLLM vs Ollama](../README.md) · 上一章：[README 总目录](../README.md) · 下一章：[02-kv-cache-management](02-kv-cache-management.md)
