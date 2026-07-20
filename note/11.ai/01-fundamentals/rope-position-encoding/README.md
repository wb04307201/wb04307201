<!--
module:
  parent: ai
  slug: ai/rope-position-encoding
  type: article
  category: 主模块子文章
  summary: RoPE 旋转位置编码：LLaMA / Mistral / Qwen 标配
-->

# RoPE 旋转位置编码

> ⬅️ [返回 L1 基础概念](../README.md)

> **一句话定位**：RoPE = **通过旋转矩阵编码位置**，核心优势是**相对位置可通过 Q·K 点积自然表达**，且支持**长度外推**。LLaMA / Mistral / Qwen / DeepSeek 等主流 LLM 的标配。

---

## 🎯 学习目标

- **数学直觉**：理解"旋转"如何编码位置（不是叠加，是乘旋转矩阵）
- **相对位置**：知道 Q·K 点积只依赖相对距离 m-n
- **长度外推**：理解为什么 RoPE 比绝对位置编码更易扩展
- **变体**：区分 RoPE / ALiBi / YaRN / NTK-aware 4 大流派

---

## 📐 核心数学

### 1D 简化版

对位置为 m 的 query 向量 q，旋转角度 mθ：

```text
q_rotated = [q_0 cos(mθ) - q_1 sin(mθ), q_0 sin(mθ) + q_1 cos(mθ)]
```

### 完整公式（每个维度独立旋转）

```text
RoPE(x, m) = 
  x_0 cos(mθ_0) - x_1 sin(mθ_0)
  x_1 cos(mθ_1) - x_2 sin(mθ_1)
  x_2 cos(mθ_2) - x_3 sin(mθ_2)
  ...
```

其中 θ_i = base^(-2i/d)，base 默认 10000。

### 相对位置证明

`<q_m, k_n> = q^T R(m-n) k`，仅依赖相对距离 m-n！

---

## 🆚 4 大位置编码流派

| 方法 | 代表模型 | 优势 | 劣势 |
|------|---------|------|------|
| **绝对位置** | BERT / GPT-2 | 简单 | 不可外推 |
| **RoPE** | LLaMA / Qwen | 相对位置 + 易外推 | base 选择影响大 |
| **ALiBi** | BLOOM | 训练时直接加 bias | 不支持动态长度 |
| **YaRN** | Qwen-72B / Llama-3 | 百万级 context 扩展 | 需微调 |

---

## 📚 章节清单

| 主题 | 核心内容 | 阅读时长 |
|------|---------|---------|
| **01 位置编码发展史** | 绝对 → 相对 → 旋转 4 阶段 | 20 min |
| **02 RoPE 数学推导** | 旋转矩阵 + 相对位置证明 | 30 min |
| **03 长度外推技术** | PI / NTK-aware / YaRN / ABF | 25 min |
| **04 RoPE 变体对比** | xPos / CoPE / LongRoPE | 20 min |

---

## 🔗 兄弟章节

- **L1 同级**：[Transformer 架构](../transformer/README.md) / [注意力机制](../attention-mechanism/README.md) / [Flash Attention](../flash-attention/README.md)
- **L2 栈**：[YaRN 长度扩展专题](../../02-technology-stack/yarn-context-extension/README.md)
- **咬文嚼字**：[Transformer 面试题](../../../13.split-hairs/11.ai/transformer/README.md)

---

## ⚠️ 常见误区

| 误区 | 真相 |
|------|------|
| ❌ RoPE 是绝对位置编码 | ✅ RoPE 编入相对位置信息 |
| ❌ RoPE 可以无成本外推到任意长度 | ✅ 需配合 YaRN / NTK-aware 才有 1M context |
| ❌ RoPE 不同维度旋转角度都一样 | ✅ 不同维度用不同 θ_i，base^(-2i/d) |

← [返回 L1 基础概念](../README.md)