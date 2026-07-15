<!--
module:
  parent: ai
  slug: ai/lost-in-middle
  type: article
  category: 主模块子文章
  summary: Lost In the Middle 现象 + 6 大缓解方案
-->

# Lost In the Middle（中间遗忘现象）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：Lost In the Middle = **LLM 对长 Context 中间段召回率显著低于首尾**。Liu et al. 2023 ACL 论文，**所有长 Context 应用的必修课**。

---

## 🎯 现象

实验：把关键信息放在不同位置，测 LLM 召回率：

```
Context: [问题] + [10 个段落] + [问题相关答案]

位置 1 (开头): 召回 78%
位置 5 (中间): 召回 42%  ← 显著下降！
位置 10 (结尾): 召回 76%
```

**U 型曲线**：首尾回忆好，中间遗忘。

---

## 📐 实验设置（Liu et al. 2023）

| 维度 | 设置 |
|------|------|
| 模型 | GPT-3.5 / Claude 1.3 / LLaMA-7B |
| Context 长度 | 3K-10K tokens |
| 关键信息位置 | 0%, 10%, 20%, ..., 100% |
| 任务 | 抽取式问答 |
| 关键发现 | 中间 50% 位置召回率掉 20-30% |

---

## 🧠 5 大根因

1. **位置编码偏置**：RoPE/ALiBi 等对首尾位置训练信号更强
2. **注意力衰减**：长 Context 下，中间 token 的 attention 权重分散
3. **训练数据偏差**：训练时首尾位置监督信号更多
4. **KV Cache 干扰**：前文 KV Cache 占用注意力预算
5. **无显式"中段"训练目标**：模型没学"在中间找信息"

---

## 🛠️ 6 大缓解方案

### 1. 重排序（Re-ranking）

```python
# 让相关文档排在首尾
def rerank(query, docs, llm):
    scores = [llm.score(query, doc) for doc in docs]
    sorted_docs = [doc for _, doc in sorted(zip(scores, docs), reverse=True)]
    return sorted_docs[:5]  # 取 Top-5
```

### 2. 注意力偏置（Attention Bias）

```python
# 给首尾位置加额外 attention 权重
attention_bias = torch.zeros(seq_len, seq_len)
attention_bias[:, :100] += 0.3  # 前 100 token 加权
attention_bias[:, -100:] += 0.3  # 后 100 token 加权
```

### 3. 分块摘要（Hierarchical Summarization）

```
长 Context → 分成 5 块 → 每块摘要 → 5 个摘要 + 问题
```

### 4. 滑动窗口（Sliding Window）

```
10K Context → 5 个 2K 窗口 → 每个窗口独立问答 → 合并
```

### 5. 显式中段训练数据

```
训练数据中显式包含"信息在中间"的样本
微调模型识别中段位置
```

### 6. 检索增强生成（RAG）

```
不把所有信息塞 Context，只检索 Top-K 相关文档（自然集中首尾）
```

**最佳实践**：方案 1 + 6 组合（重排序 + RAG）。

---

## 📊 缓解效果实测

| 方案 | 召回率提升 | 实施难度 |
|------|-----------|---------|
| 重排序 | +18% | ⭐⭐ |
| 注意力偏置 | +12% | ⭐⭐⭐⭐ |
| 分块摘要 | +22% | ⭐⭐⭐ |
| 滑动窗口 | +15% | ⭐⭐ |
| 显式训练 | +8% | ⭐⭐⭐⭐⭐ |
| RAG | +25% | ⭐⭐ |

---

## 🔗 兄弟章节

- **本专题**：[YaRN 长度扩展](../yarn-context-extension/README.md) / [Chunking 策略](../chunking-strategies/README.md) / [Reranker](../reranker/README.md) / [Hybrid Search](../hybrid-search/README.md) / [RAG 评估](../../08-llmops/agent-evaluation/09-rag-evaluation/README.md)
- **L1**：[RoPE 位置编码](../../01-fundamentals/rope-position-encoding/README.md)
- **咬文嚼字**：[面试深挖](../../../13.split-hairs/11.ai/context-engineering-interview/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ Context 越长越好 | ✅ 超 4K 召回率开始下降 |
| ❌ 关键信息放中间也行 | ✅ 放首尾才稳妥 |
| ❌ Lost in middle 是 prompt 问题 | ✅ 是架构特性 |
| ❌ GPT-4 解决了 Lost in middle | ✅ GPT-4 改善但未根治 |
| ❌ 长 context 等于强记忆 | ✅ 长 ≠ 准，召回率仍 U 型 |

← [返回 L2 技术栈](../README.md)