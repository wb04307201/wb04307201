<!--
module:
  parent: ai
  slug: ai/kv-cache
  type: article
  category: 主模块子文章
  summary: KV Cache 推理核心机制（内存布局 / 复杂度 / 显存优化）
-->

# KV Cache

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：KV Cache = **推理时缓存已计算的 K/V 矩阵**，避免每 token 重算历史 Attention。**自回归 LLM 推理加速的核心技术**，没有 KV Cache 就无法服务在线请求。

---

## 🎯 一句话理解

推理生成第 n 个 token 时，**只需计算新 token 的 Q**，K 和 V 可从历史缓存读取 → 计算量从 O(n²) 降到 O(n)，**但显存从 O(1) 涨到 O(n)**。

---

## 📐 内存布局

每生成 1 个 token，需要在显存缓存：

```
K 缓存: [num_layers, num_heads, seq_len, head_dim]
V 缓存: [num_layers, num_heads, seq_len, head_dim]
```

**单 token 占用**：

```
2 × num_layers × num_heads × head_dim × dtype_size
= 2 × 32 × 32 × 128 × 2 bytes (FP16)
= 0.5 MB / token
```

---

## 📊 显存占用实测

| 模型 | num_layers | hidden | 1K context | 8K context | 32K context | 128K context |
|------|-----------|--------|-----------|-----------|------------|--------------|
| 7B (LLaMA) | 32 | 4096 | 0.5 GB | 4 GB | 16 GB | 64 GB |
| 13B | 40 | 5120 | 0.8 GB | 6.4 GB | 25.6 GB | 102 GB |
| 70B | 80 | 8192 | 2.5 GB | 20 GB | 80 GB | 320 GB (单卡放不下) |

**结论**：长 context 推理显存爆炸 → 催生 PagedAttention（vLLM）

---

## ⚙️ 三大优化方向

1. **量化**：KV 缓存从 FP16 → INT8/INT4（省 2-4x 显存）
2. **共享**：MQA / GQA 让多个 Q 头共享 1 份 KV（省 4-8x）
3. **分页**：PagedAttention 借鉴 OS 虚拟内存（碎片 < 4%）

---

## 🔗 兄弟章节

- **L1 同级**：[Transformer 架构](../../01-fundamentals/transformer/README.md) / [注意力机制](../../01-fundamentals/attention-mechanism/README.md) / [Flash Attention](../../01-fundamentals/flash-attention/README.md)
- **本专题**：[PagedAttention](README.md) / [推理性能指标](../inference-metrics/README.md) / [推理框架对比](../inference-frameworks/README.md)
- **咬文嚼字**：[KV Cache 面试题](../../../13.split-hairs/11.ai/llm-benchmark/README.md) 顺带提

---

## ⚠️ 5 大反直觉

| 误区 | 真相 |
|------|------|
| ❌ KV Cache 越大越好 | ✅ 受显存约束，70B + 128K 需 4 张 A100 |
| ❌ 训练时也需要 KV Cache | ✅ 训练是并行算全部，推理是逐 token |
| ❌ KV Cache 越多越快 | ✅ 显存增加，attention 计算仍是 O(n²) |
| ❌ KV Cache 可以无限延长 context | ✅ 实际 70B 模型超过 32K 就明显变慢 |
| ❌ FP16 KV Cache 够用 | ✅ 实际生产多用 INT8 KV 缓存省显存 |

← [返回 L2 技术栈](../README.md)