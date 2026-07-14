<!--
module:
  parent: ai
  slug: ai/speculative-decoding
  type: article
  category: 主模块子文章
  summary: Speculative Decoding 投机解码：小模型预测+大模型验证
-->

# Speculative Decoding（投机解码）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：Speculative Decoding = **小模型（draft）预测 K 个 token → 大模型（target）一次验证**，接受率 60-80% 时 **2-3x 加速**。是 batch=1 在线服务的关键技术。

---

## 🎯 核心思想

```
传统：每步生成 1 个 token，要 1 次大模型 forward
       → 100 token 要 100 次 forward

投机：每步让小模型猜 5 个 token，大模型 1 次 forward 验证 5 个
     → 100 token 只要 20-30 次大模型 forward
```

**关键洞察**：大模型 1 次 forward 算 5 个 token 的成本 ≈ 算 1 个 token（attention 是 O(n²)，n 略增不影响）

---

## 📐 算法流程

```python
# 1. 小模型（7B）预测 5 个候选 token
draft_tokens = small_model.generate(prompt, max_new=5)

# 2. 大模型（70B）一次 forward 验证
logits = large_model.forward(prompt + draft_tokens)
for i, token in enumerate(draft_tokens):
    # 验证 token 是否在 大模型 top-p 采样范围内
    if accept(token, logits[i]):
        accept_list.append(token)
    else:
        # 拒绝，重新采样
        corrected = sample_from_distribution(logits[i])
        accept_list.append(corrected)
        break

# 3. 把接受的 tokens 拼接到 prompt
prompt += accept_list
```

---

## 📊 变体对比

| 方法 | 原理 | 加速 | 复杂度 |
|------|------|------|--------|
| **原始投机** | 小模型预测 | 2-3x | 中 |
| **Medusa** | 模型加 3 个预测头，并行预测 | 2-3.5x | 高 |
| **EAGLE** | 特征层预测，不需小模型 | 2.5-4x | 高 |
| **Lookahead** | 一次预测多个分支 | 1.5-2x | 中 |
| **Self-Speculative** | 大模型早退层做 draft | 1.5-2x | 低 |

---

## 📈 适用场景

| 场景 | 是否适用 | 理由 |
|------|---------|------|
| **Batch=1 在线** | ✅ 强烈推荐 | 加速 2-3x |
| **Batch=8+ 离线** | ❌ 不推荐 | 大模型直接 batch 算已很高效 |
| **大模型 vs 小模型比例** | ✅ 5-10x 最佳 | 70B+7B 经典搭配 |
| **代码生成** | ✅ 高接受率 | 模式重复多 |
| **创意写作** | ⚠️ 中等 | 接受率低，加速 1.5x |

---

## 🔗 兄弟章节

- **本专题**：[KV Cache](../kv-cache/README.md) / [PagedAttention](../paged-attention/README.md) / [推理框架对比](../inference-frameworks/README.md)
- **咬文嚼字**：[面试深挖版](../../../../../13.split-hairs/11.ai/llm-benchmark/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 投机解码提升所有场景 | ✅ batch=1 在线最受益，batch 大无收益 |
| ❌ 接受率越高越好 | ✅ 100% 接受意味着 draft 和 target 一样，反而浪费算 draft |
| ❌ 投机解码不改变输出分布 | ✅ 数学证明：输出分布完全一致 |
| ❌ 小模型越接近大模型越好 | ✅ 需权衡：太接近算力浪费，太远接受率低 |

← [返回 L2 技术栈](../README.md)