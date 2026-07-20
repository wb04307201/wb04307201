<!--
module:
  parent: ai
  slug: ai/chunking-strategies
  type: article
  category: 主模块子文章
  summary: 5 大 Chunking 策略对比
-->

# Chunking 策略（文档分块）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：Chunking = **把长文档切成适合 Embedding 的小块**，**直接影响 RAG 检索质量 20-40%**。固定 / 递归 / 语义 / 滑动窗口 / Agentic 5 大策略。

---

## 🎯 为什么 Chunking 关键

```text
文档 10000 字 → 直接 Embedding
  → 1 个 8000 维向量
  → 检索时粗粒度，找不准

文档 10000 字 → 切成 50 个 200 字 chunk
  → 50 个独立向量
  → 检索时细粒度，精准定位
```

**Chunking 不当**：语义断裂、检索召回低、上下文不完整。

---

## 📊 5 大策略对比

| 策略 | 切法 | 优点 | 缺点 | 适用 |
|------|------|------|------|------|
| **固定大小** | 每 500 字切 | 简单 | 切断句子 | 通用 |
| **递归** | 按段落/句子递归切 | 保留语义结构 | 仍可能切错 | 90% 场景 |
| **语义** | 主题变化点切 | 最精准 | 慢（需 Embedding）| 高质量 RAG |
| **滑动窗口** | 切块 + 重叠 | 跨边界上下文 | 冗余多 | 长文档 |
| **Agentic** | LLM 决定如何切 | 最智能 | 贵 + 慢 | 高价值文档 |

---

## 🛠️ 1. 固定大小

```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=0,
)
chunks = splitter.split_text(long_text)
```

**问题**：可能在句子中间切断。

---

## 🛠️ 2. 递归（LangChain 默认）

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""],
)
chunks = splitter.split_text(long_text)
```

**优点**：先按段落切，再按句子，再按字符。**保留语义结构**。

---

## 🛠️ 3. 语义分块

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain.embeddings import OpenAIEmbeddings

splitter = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95,  # 主题变化 95% 阈值
)
chunks = splitter.split_text(long_text)
```

**原理**：相邻段 Embedding 余弦相似度突然下降处切分。

---

## 🛠️ 4. 滑动窗口

```python
chunks = []
for i in range(0, len(text), chunk_size - overlap):
    chunks.append(text[i:i + chunk_size])
# chunk_size=500, overlap=100
```

**参数选择**：
- `chunk_size`：500-1000（与 Embedding 模型匹配）
- `overlap`：10-20% 的 chunk_size

---

## 🛠️ 5. Agentic（LLM 驱动）

```python
prompt = """请将以下文档切分成语义独立的段落，每段 200-500 字。
返回 JSON 数组，每个元素是一段。

文档：{document}
"""
chunks = llm.generate(prompt)
```

**优点**：最智能。**缺点**：贵（每页 $0.01-0.1）+ 慢（10-100x）。

---

## 📐 选型决策树

```text
Q1: 预算？
├── 紧 → 固定 / 递归
├── 中 → 滑动窗口
└── 充足 → 语义 / Agentic

Q2: 文档结构？
├── 强结构（章节分明）→ 递归
├── 弱结构（散文）→ 滑动窗口
└── 无结构（FAQ）→ 固定

Q3: 准确性要求？
├── 通用 → 递归
└── 高质量 → 语义 / Agentic
```

---

## 📊 实测效果

RAG 检索质量（nDCG@10）：

| 策略 | 法律文档 | 学术论文 | FAQ | 代码 |
|------|---------|---------|-----|------|
| 固定 | 0.62 | 0.58 | 0.71 | 0.45 |
| 递归 | 0.75 | 0.72 | 0.78 | 0.62 |
| 滑动 | 0.77 | 0.74 | 0.76 | 0.65 |
| **语义** | **0.83** | **0.81** | **0.79** | 0.71 |
| **Agentic** | **0.85** | **0.83** | 0.80 | **0.78** |

**结论**：语义 / Agentic 强 5-15%，但慢 5-10x。

---

## 🔗 兄弟章节

- **本专题**：[Embedding 模型](../embedding-models/README.md) / [Hybrid Search](../hybrid-search/README.md) / [Reranker](../reranker/README.md) / [RAG 评估](../../08-llmops/agent-evaluation/09-rag-evaluation/README.md)
- **L1**：[Lost in middle](../lost-in-middle/README.md)
- **咬文嚼字**：[RAG 面试](../../../13.split-hairs/11.ai/rag/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ chunk 越大越好 | ✅ 越大召回率越低（粗粒度）|
| ❌ chunk 越小越好 | ✅ 越小上下文不完整 |
| ❌ Recursive 永远够用 | ✅ 复杂文档需语义/Agentic |
| ❌ Chunking 后不需要 metadata | ✅ 需保留 source / page 便于溯源 |

← [返回 L2 技术栈](../README.md)