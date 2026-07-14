<!--
module:
  parent: ai
  slug: ai/flash-attention
  type: article
  category: 主模块子文章
  summary: Flash Attention 2/3：长上下文推理标配
-->

# Flash Attention 2/3

> ⬅️ [返回 L1 基础概念](../README.md)

> **一句话定位**：Flash Attention = **分块计算 + IO 感知**，将 Attention 显存从 O(n²) 降到 O(n)，让 128K-1M 上下文推理成为可能。Tri Dao 2022 论文，2024 年 Hopper 架构上 Flash Attention 3 再提速 2x。

---

## 🎯 学习目标

- **核心问题**：标准 Attention 为什么慢？（不是计算，是 IO）
- **关键洞察**：分块计算 + 不写回 HBM = 显存省 5-20x
- **工程实现**：CUDA kernel + Tiling + Recompute
- **3 个版本**：v1（IO 感知）/ v2（work partitioning）/ v3（FP8 + WGMMA）

---

## 🧠 核心洞察

### 标准 Attention 慢在哪

```python
# 标准实现
S = Q @ K^T              # O(n²) 显存写回 HBM
P = softmax(S)           # O(n²) 又一次写回
O = P @ V                # O(n²) 再写回
# → 3 次 O(n²) HBM 读写
```

GPU 计算速度是 HBM 带宽的 ~100x，瓶颈是**内存访问**。

### Flash Attention 解法

```
1. 把 Q/K/V 分成 16x16 的小块（block）
2. 在 SRAM（片上缓存，极快）里逐块算
3. 用 Online Softmax 累积结果
4. 只在最后写一次 O 到 HBM
→ 1 次 HBM 读写，5-20x 加速
```

---

## 📊 性能对比

| 序列长度 | 标准 Attention | Flash Attention v2 | 加速比 |
|---------|--------------|--------------------|---------|
| 1K | 5ms | 2ms | 2.5x |
| 4K | 50ms | 8ms | 6.2x |
| 16K | 800ms | 35ms | 23x |
| 64K | OOM | 200ms | ∞ |
| 128K | OOM | 700ms | ∞ |

**实测**：H100 + 7B 模型，128K context 推理从 OOM 变为可行。

---

## 📚 章节清单

| 主题 | 核心内容 | 阅读时长 |
|------|---------|---------|
| [01 Attention IO 瓶颈](01-attention-io-bottleneck.md) | Roofline 模型 + 算术强度分析 | 20 min |
| [02 分块与 Online Softmax](02-tiling-online-softmax.md) | 数学等价性证明 | 30 min |
| [03 Flash Attention v1/v2](03-flash-v1-v2.md) | 算法迭代 + CUDA 实现 | 30 min |
| [04 Flash Attention 3](04-flash-v3.md) | FP8 + WGMMA + Hopper 优化 | 25 min |

---

## 🔗 兄弟章节

- **L1 同级**：[Transformer 架构](../transformer/README.md) / [注意力机制](../attention-mechanism/README.md) / [RoPE 位置编码](../rope-position-encoding/README.md)
- **L2 栈**：[KV Cache](../../02-technology-stack/kv-cache/README.md) / [PagedAttention](../../02-technology-stack/paged-attention/README.md) / [推理性能指标](../../02-technology-stack/inference-metrics/README.md)
- **工程**：[vLLM 部署](../../02-technology-stack/inference-frameworks/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ Flash Attention 改变了 Attention 数学 | ✅ 数学等价，仅 IO 优化 |
| ❌ Flash Attention 在所有硬件都加速 | ✅ 需 SM 8.0+（A100/3090+） |
| ❌ Flash Attention 3 通用 | ✅ 仅 Hopper（H100）支持 WGMMA |
| ❌ Flash Attention 能完全消除 O(n²) | ✅ 计算仍是 O(n²)，只是显存降到 O(n) |

← [返回 L1 基础概念](../README.md)