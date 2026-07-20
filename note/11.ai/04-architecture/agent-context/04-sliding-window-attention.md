<!--
module:
  parent: ai/agent-architecture/agent-context
  slug: ai/agent-architecture/agent-context/04-sliding-window-attention
  type: topic
  category: 注意力滑动窗口
  summary: Sliding Window Attention + StreamingLLM + LongLoRA + Landmark Attention —— 注意力层面处理长上下文的 4 大技术
-->

# Sliding Window Attention · 注意力层面的长上下文

> **一句话**：Sliding Window Attention 不是"丢弃旧 token"那么简单——它解决**KV cache 显存爆炸**的根本问题，与 PagedAttention 互补。

← [返回: Agent 长上下文架构](../README.md)

---

## 1. 为什么需要 Sliding Window？

**全注意力（Full Attention）的成本**：
- Context = n 时，每个 token 的 attention 计算 O(n)
- 单 token 存储 KV cache 占用 ~0.4 MB（LLaMA-7B FP16）
- 100k context：单请求 ~40 GB KV cache → 单请求独占 1.5 张 H100 80GB

**Sliding Window Attention 的解法**：
- 每个 token 只看最近的 w 个 token（w = window size）
- 计算量 O(n × w)，与 context 长度**线性相关**而非平方
- KV cache 占用上限 = w 个 token

| 上下文长度 | Full Attn KV cache | Sliding Window KV cache |
|-----------|---------------------|--------------------------|
| 4k | 1.6 GB | 0.05 GB（w=128）|
| 32k | 12.8 GB | 0.05 GB |
| 128k | 51.2 GB | 0.05 GB |

---

## 2. 4 大 Sliding Window 技术

### 2.1 朴素 Sliding Window

```text
token 0 1 2 3 4 5 6 7 8 9 ...
attends: ↑ ↑ ↑ ↑
       [0]
   [0 1 2 3]
       [3 4 5 6]
```

- 每个 token 只看 w 个前向 token
- 优点：实现简单，KV cache 上限固定
- 缺点：完全遗忘 w 之外的旧信息，**对话早期信息丢失**

### 2.2 StreamingLLM（2024，MIT）

**核心洞察**：attention 中存在"attention sinks"——某些特定 token（通常是第一个 token）即使被滑窗丢弃，仍有残存的 attention 流量。

```text
Window + 4 sink tokens：
[SINK][SINK][SINK][SINK][token 0 ... token w-1][滑动窗口]
```

**效果**：
- 32k 上下文部署成本降到 4k 等价
- 性能损失 < 5%（在标准 benchmark）
- 已被 Llama 2 / Mistral / Claude 借鉴

### 2.3 LongLoRA（2023）

**核心**：微调时引入**shifted sparse attention**，训练成本降低，推理时仍是 full attention。

```text
训练时：window 局部 attention（dense + shifted）
推理时：full attention
```

**优点**：训练加速，推理无损
**缺点**：仍是 full attention 推理（显存问题没解）

### 2.4 Landmark Attention（RAG 优化）

**核心**：保留"地标"（landmark）token，让远处 token 也能间接 attend。

```text
[LANDMARK 1]... window ...[LANDMARK 2]... window ...
```

**适用**：长文档 RAG，让 LLM 能"索引跳转"
**实现**：在 chunk 之间插入 landmark 标记

---

## 3. 与 PagedAttention 的关系

| 技术 | 解决问题 | 层级 |
|------|---------|------|
| **PagedAttention** | KV cache 碎片化 | 显存分配（vLLM 0.4+）|
| **Sliding Window** | KV cache 总量 | 注意力算法（Mistral 等）|
| **两者可叠加** | **双重显存优化** | vLLM + Mistral 组合 |

详见 [vllm-vs-ollama 02-kv-cache-management](../../03-engineering/ai-platforms/vllm-vs-ollama/02-kv-cache-management.md)。

---

## 4. Agent 场景的应用

### 4.1 长期对话

```text
场景：Agent 跑了 100 轮

朴素 Sliding Window：
- LLM 看不到 100 轮前的用户偏好 → 答非所问

StreamingLLM：
- sink tokens 保留早期关键信息 → 推荐"系统提示"

推荐方案：Sliding Window + sink + Memory 模块
```

### 4.2 工具调用返回值

```text
工具返回 10k token JSON → 不能全塞 prompt

方案：
1. 工具调用前：selective summarization
2. 工具调用后：滑动窗口保留最新 + summary
```

---

## 5. 反模式 · 5 个常见错

### ⚠️ 反模式 1：window size 调太小

- 错：w=128（信息丢失率高）
- 对：w=4096（标准）或 w=8192（高质量）

### ⚠️ 反模式 2：忘记 attention sinks

- 错：朴素 sliding window（早期 token 完全丢失）
- 对：保留 sink tokens（[0, 1, 2, 3]）作为 attention 锚点

### ⚠️ 反模式 3：忽略 Long Context 评估

- 错：在大上下文模型上忽略 Lost in the Middle 评估
- 对：建评测集验证 P50/P95 准确率

### ⚠️ 反模式 4：sliding window 替代所有

- 错："window 8k 就够了，不用 32k"
- 对：业务需求决定（按需选用，混合策略）

### ⚠️ 反模式 5：训练与推理不一致

- 错：训练时 full attention，推理 sliding window
- 对：训练时即用 sliding window（LongLoRA 思想）

---

## 6. 速查 · 选型决策

| 模型 | 默认 attention | 推荐用法 |
|------|----------------|---------|
| LLaMA 2 | Full | 加 streamingLLM 改造 |
| Mistral 7B | **Sliding Window w=4096** | 开箱即用（启发了 Mistral 后续所有）|
| Qwen 2.5 | Full + YaRN 扩展 | 1M context，YaRN 必备 |
| Gemini 1.5 | Full 1M | 不需要 sliding window（成本大但能用）|
| Claude 3.5 | Full 200k | 不需要 sliding window |

---

## 7. 一句话总结

> **Sliding Window Attention 是"减显存不减太多质量"的工程权衡——StreamingLLM + sink tokens 让 32k 部署成本降到 4k 等价；Agent 场景需配合 Memory 模块补早期信息损失。**

---

← [返回: Agent 长上下文架构](../README.md) · 上一章：[03-memory-strategies](03-memory-strategies.md) · 下一章：[05-sub-agents-decomposition](05-sub-agents-decomposition.md)
