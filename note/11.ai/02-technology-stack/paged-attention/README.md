<!--
module:
  parent: ai
  slug: ai/paged-attention
  type: article
  category: 主模块子文章
  summary: PagedAttention vLLM 核心：解决 KV Cache 碎片化
-->

# PagedAttention（vLLM 核心）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：PagedAttention = **借鉴 OS 虚拟内存，按页（block）分配 KV Cache**，把显存浪费从 60-80% 降到 < 4%，**吞吐量提升 4-24x**。vLLM 2023 年 SOSP 论文，已成为 LLM 推理引擎事实标准。

---

## 🎯 问题：KV Cache 碎片化

不同请求的 sequence 长度差异巨大（100 token vs 8000 token）：

```text
传统连续分配：
  Request A: 100 token → 申请 100 位置
  Request B: 8000 token → 申请 8000 位置
  中间空闲 7900 位置浪费（无法给 A 用）
  显存利用率 < 40%
```

---

## 💡 方案：虚拟分页

```text
1. 把 KV Cache 切成固定大小 block（默认 16 token / block）
2. 每个 block 物理上不连续，但通过 block_table 映射
3. 类似 OS 虚拟内存的页表机制
4. Request A 用 7 个 block，Request B 用 500 个 block，无碎片
```

---

## 📊 性能对比

| 引擎 | 显存利用率 | 吞吐量（req/s） | 首 token 延迟 |
|------|-----------|----------------|-------------|
| HuggingFace | 40% | 1x | 1x |
| FasterTransformer | 55% | 2x | 1.1x |
| **vLLM (PagedAttention)** | **96%** | **4-24x** | **0.9x** |
| vLLM + Continuous Batching | 98% | 23x | 0.7x |

**实测**：LLaMA-7B，A100 80GB，ShareGPT 数据集。

---

## 🔧 关键代码

```python
# vllm/v1/core/block_manager.py
class BlockManager:
    def __init__(self, num_blocks, block_size=16):
        self.block_size = block_size  # 16 token / block
        self.free_blocks = list(range(num_blocks))
        self.block_tables = {}  # request_id → list of block ids
    
    def append_token(self, request_id, kv_cache):
        block_table = self.block_tables[request_id]
        # 当前 block 满了吗？
        if len(kv_cache) % self.block_size == 0:
            # 分配新 block
            new_block = self.free_blocks.pop()
            block_table.append(new_block)
        # 写入 KV 到 block_table[-1] 的对应位置
        block_idx = (len(kv_cache) - 1) % self.block_size
        self.write_kv(block_table[-1], block_idx, kv_cache)
```

---

## 🔗 兄弟章节

- **本专题**：[KV Cache](../kv-cache/README.md) / [Continuous Batching](../continuous-batching/README.md) / [推理框架对比](../inference-frameworks/README.md)
- **L1**：[Flash Attention](../../01-fundamentals/flash-attention/README.md) — 同样 IO 优化思路
- **12.story**：[46-llm-inference](../../../12.story/46-llm-inference.md)（餐厅叙事版）

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ PagedAttention 是为了节省显存 | ✅ 主要是为了提高利用率→吞吐量 |
| ❌ PagedAttention 增加推理延迟 | ✅ 实际首 token 延迟略低（预分配） |
| ❌ 任何模型都能用 PagedAttention | ✅ 需支持可变长度 attention（大多数都支持） |
| ❌ Block size 越大越好 | ✅ 16-64 是 sweet spot，太大碎片，太小 block table 大 |

← [返回 L2 技术栈](../README.md)