<!--
module:
  parent: ai
  slug: ai/moe-architecture
  type: article
  category: 主模块子文章
  summary: MoE 混合专家架构（Mixtral / DeepSeek-V3 / Switch Transformer）
-->

# MoE 混合专家架构

> ⬅️ [返回 L1 基础概念](../README.md)

> **一句话定位**：MoE = **多个专家网络 + 路由器动态选择**，用稀疏激活实现"参数爆炸但计算不爆炸"。Mixtral 8x7B / DeepSeek-V3 671B / Switch Transformer 均采用此架构，是 2024-2026 主流大模型标配。

---

## 🎯 学习目标

- **核心思想**：理解"稀疏激活"如何让 671B 模型只激活 37B 计算量
- **路由机制**：Top-K Gating + 负载均衡损失
- **训练挑战**：专家不均衡（路由坍缩）+ 通信开销
- **代表实现**：Mixtral / DeepSeek-V3 / Qwen-MoE / Snowflake Arctic

---

## 📐 核心架构

### 基础 MoE 层

```text
输入 x (batch × seq × dim)
  ↓
Router(x) = softmax(W_g · x)  # 路由分数
  ↓
Top-K 选择（如选 2 个专家）
  ↓
output = Σ (g_i · Expert_i(x))  # 加权求和
```

### Switch Transformer 简化

每个 token 只路由到 **1 个**专家（Top-1），简化训练。

### DeepSeek-V3 创新

- **细粒度专家**：256 个专家激活 8 个
- **共享专家**：1 个始终激活的"通用专家"
- **Dual-Pipe 调度**：通信与计算重叠
- **无辅助损失负载均衡**：用 bias 动态调整

---

## 🆚 Dense vs MoE 对比

| 维度 | Dense 7B | MoE 47B (Mixtral 8x7B) |
|------|---------|------------------------|
| **参数量** | 7B | 47B（8×7B + Router） |
| **激活参数/token** | 7B | ~13B（2 专家激活） |
| **显存占用** | 14GB (FP16) | 90GB（必须量化部署） |
| **训练成本** | 1x | ~2x（专家+通信） |
| **推理速度** | 1x | 0.7-1x（专家调度开销） |
| **效果** | 基准 | 同计算量下显著优于 Dense |

---

## 📚 章节清单

| 主题 | 核心内容 | 阅读时长 |
|------|---------|---------|
| **01 MoE 核心思想** | 稀疏激活 + 路由 + 专家 | 25 min |
| **02 路由机制** | Top-K Gating + 负载均衡 | 25 min |
| **03 训练挑战** | 路由坍缩 + 通信优化 | 30 min |
| **04 推理优化** | 专家并行 + 缓存策略 | 25 min |
| **05 代表模型对比** | Mixtral / DeepSeek-V3 / Qwen-MoE | 20 min |

---

## 🔗 兄弟章节

- **L1 同级**：[Transformer 架构](../transformer/README.md) / [注意力机制](../attention-mechanism/README.md)
- **L2 栈**：[KV Cache](../../02-technology-stack/kv-cache/README.md) / [MoE 推理优化](../../02-technology-stack/moe-inference/README.md)
- **咬文嚼字**：[DeepSeek-V3 面试题](../../../13.split-hairs/11.ai/multi-agent-system-design/README.md) 顺带提

---

## ⚠️ 5 大反直觉

| 误区 | 真相 |
|------|------|
| ❌ MoE 参数越大效果越好 | ✅ 同等激活参数下 MoE > Dense，但显存爆炸 |
| ❌ MoE 推理比 Dense 快 | ✅ 通常更慢（专家调度 + 通信） |
| ❌ Top-K 越大越好 | ✅ K=1-2 是主流，K=4 已很罕见 |
| ❌ MoE 训练简单 | ✅ 路由坍缩是核心难题，需辅助损失或 bias |
| ❌ 专家数量越多越好 | ✅ 太多导致单专家弱 + 路由难学 |

← [返回 L1 基础概念](../README.md)