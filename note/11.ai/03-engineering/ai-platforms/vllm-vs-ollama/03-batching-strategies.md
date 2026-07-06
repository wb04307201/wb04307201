<!--
module:
  parent: ai-platforms/vllm-vs-ollama
  slug: ai-platforms/vllm-vs-ollama/03-batching-strategies
  type: topic
  category: 推理调度
  summary: 静态批处理 vs 动态批处理 vs 连续批处理 —— vLLM 的连续批处理是工业部署最优解
-->

# 批处理策略 · 从静态到连续

> **一句话**：连续批处理（Continuous Batching）是 vLLM 工业级吞吐的关键，Ollama 仅有朴素实现，差距 2-5x。

← [返回: vLLM vs Ollama](../README.md)

---

## 1. 三种批处理策略

### 1.1 静态批处理（Static Batching）

```
所有序列同步开始 → 等最长序列完成 → 整批返回
┌────────────┐
│ Seq A ▓▓▓▓▓▓│
│ Seq B ▓▓▓▓▓▓▓▓▓▓│ ← 等 B 完成才返回
│ Seq C ▓▓▓▓▓│
└────────────┘
```

**特点**：
- 实现最简单（HuggingFace generate 默认）
- 显存浪费：短序列等长序列（GPU 空转）
- 吞吐：1x（基线）

### 1.2 动态批处理（Dynamic Batching）

```
到达请求凑满 batch 才开始 → 仍需等齐
┌────────────┐
│ Seq A ▓▓▓▓▓▓│
│ Seq B ▓▓▓▓▓▓▓▓▓▓│
│ Seq C ▓▓▓▓▓│
└────────────┘
```

**特点**：
- 引入「wait」队列，凑 batch_size 才推理
- 比静态省一点等待，但仍存在 padding 浪费
- 吞吐：1.2-1.5x

### 1.3 连续批处理（Continuous Batching / Iteration-level Scheduling）

```
每个 decoding step 重新拼 batch：
Step 1: [A, B, C, D]
Step 2: [B, C, D, E]  ← A 完成，立刻加入新请求 E
Step 3: [C, D, E, F]  ← B 完成，加入 F
...
```

**特点**：
- 每个 step 评估「完成的请求踢出 + 新请求加入」
- **完成一个返回一个**，端到端无 padding
- 吞吐：2-5x（典型），极端场景 10x+
- vLLM 标志性特性

---

## 2. 实测对比（LLaMA-7B + A10G + ShareGPT）

| 策略 | 吞吐量 (req/s) | 平均延迟 (s) | P99 延迟 (s) |
|------|----------------|---------------|---------------|
| 静态批处理 | 1.0x | 8.2 | 12.5 |
| 动态批处理 | 1.4x | 6.5 | 9.8 |
| **连续批处理 (vLLM)** | **3.8x** | **2.1** | **4.5** |

> 数据来源：vLLM 论文 + 社区实测（2024 Q2）。实际数随硬件 / 模型 / 负载变化。

---

## 3. 连续批处理的工作流

```
请求进入 vLLM 调度器：
  ↓
[Prefill 阶段] 处理新请求的 prompt（密集计算）
  ↓
[Decode 阶段] 自回归生成，每个 step 检查：
   - 是否 token > max_model_len（踢出 + 返回）
   - 是否 stop_token_id（踢出 + 返回）
  ↓
Batch 重组：补入新请求 + 填充未完成请求
  ↓
下一个 step
```

**核心数据结构**：
- `Scheduler` 管理 waiting / running / swapped 队列
- 每个 step 重新分配 GPU 资源
- 配合 PagedAttention 实现 block 复用

---

## 4. Ollama / llama.cpp 为什么没有连续批处理？

### 4.1 设计目标不同

| 引擎 | 优化方向 | 设计取舍 |
|------|---------|---------|
| **vLLM** | 高并发服务器 | 牺牲单机延迟，换吞吐量 |
| **Ollama / llama.cpp** | 单机 / 边缘 / 离线 | 牺牲吞吐量，换启动速度 + 低资源 |

### 4.2 实现复杂度

连续批处理需要：
- 调度器（Scheduler）：每个 step 决策入队 / 出队
- 动态显存管理：PagedAttention block 调度
- KV cache 复用：prefix sharing + eviction

Ollama 走「**单请求优化**」路线，没做调度器。

### 4.3 反直觉

- Ollama 单并发延迟可能比 vLLM **更低**（没有调度开销）
- 但 5+ 并发下 vLLM 反超
- 100+ 并发 vLLM 是 Ollama 的 **10-20x**

---

## 5. 工业部署的反模式

- ⚠️ **「连续批处理」** ≠ **「乱序返回」**：vLLM 按"各自完成时间"返回，仍是按请求顺序打包，但每个请求独立完成就推送
- ⚠️ **`max_num_seqs` 过小**：限制并发，等于关掉了连续批处理的优势
- ⚠️ **`enable_prefix_caching` 关闭**：prefix 复用是连续批处理的"搭子"，关了吞吐降 30%
- ⚠️ **忽略 prefill/decode 配比**：长 prompt + 短 response 时，prefill 占 GPU 时间，decode 排队

---

## 6. 速查 · 关键配置

| 参数 | 默认 | 推荐 |
|------|------|------|
| `--max-num-seqs` | 256 | 按显存算（公式见下） |
| `--max-num-batched-tokens` | 2048 | 长 prompt 场景调高 4096+ |
| `--enable-chunked-prefill` | False | 长 prompt + 高并发开 |
| `--scheduler-delay-factor` | 0.0 | 调度延迟敏感场景调 1.0+ |

**max_num_seqs 估算公式**：
```
max_num_seqs ≈ (总显存 × 0.9 - 模型权重) / 单请求 KV cache
```

---

## 7. 一句话总结

> **连续批处理把 GPU 从「等所有结束」改成「来一个接一个」，让 vLLM 在高并发下反超 Ollama 是必然结果。**

---

← [返回: vLLM vs Ollama](../README.md) · 上一章：[02-kv-cache-management](02-kv-cache-management.md) · 下一章：[04-quantization](04-quantization.md)
