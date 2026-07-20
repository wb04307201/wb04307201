<!--
module:
  parent: ai
  slug: ai/embedding-models
  type: article
  category: 主模块子文章
  summary: Embedding 模型横评（BGE / M3E / Qwen / OpenAI）
-->

# Embedding 模型横评

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：**BGE / M3E / Qwen / OpenAI text-embedding-3** 4 大主流 Embedding 模型横评，帮 RAG 系统选对 Embedding 提升 20-30% 召回。

---

## 📊 4 大模型对比

| 模型 | 维度 | 多语言 | 上下文 | MTEB 中文 | MTEB 英文 | 商业许可 | 显存 |
|------|------|--------|--------|----------|----------|---------|------|
| **BGE-M3** | 1024 | ✅ 100+ 语言 | 8K | **68.2** | 65.4 | MIT | 2GB |
| **M3E-large** | 1024 | ✅ 中英 | 512 | 64.3 | 60.1 | Apache | 1.5GB |
| **Qwen3-Embedding-8B** | 4096 | ✅ 多语言 | 32K | **70.5** | 70.8 | Apache | 16GB |
| **text-embedding-3-large** | 3072 | ✅ 多语言 | 8K | 65.8 | **68.4** | OpenAI API | - |

**MTEB**（Massive Text Embedding Benchmark）：2024 标准评测。

---

## 🆚 选型决策

```text
Q1: 预算？
├── 紧 → BGE-M3（开源免费）/ M3E
└── 充足 → OpenAI / Qwen3-8B

Q2: 多语言？
├── 仅中英 → M3E
└── 多语言（100+）→ BGE-M3

Q3: 上下文长度？
├── < 512 → M3E
├── 512-8K → BGE-M3
└── > 8K → Qwen3-8B

Q4: 准确性优先？
├── 通用 → BGE-M3
└── 极致 → Qwen3-8B（中文 SOTA）
```

---

## 🛠️ 1. BGE-M3（推荐默认）

**最强开源 Embedding**，2024 中文 SOTA。

```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

# 编码
embeddings = model.encode(
    ["文档1", "文档2", "查询"],
    batch_size=12,
    max_length=512,
)['dense_vecs']

# 计算相似度
import numpy as np
query_emb = embeddings[-1]
doc_embs = embeddings[:-1]
scores = query_emb @ doc_embs.T
```

**特性**：
- 支持 dense / sparse / multi-vector 三种检索
- 100+ 语言
- 长文本（8K）

---

## 🛠️ 2. M3E（Moka 开源）

**轻量级中文 Embedding**。

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('moka-ai/m3e-large')
embeddings = model.encode(["文档1", "查询"])
```

**优点**：1.5GB 显存，中文友好  
**缺点**：仅中英

---

## 🛠️ 3. Qwen3-Embedding-8B（极致性能）

**2024 阿里最强 Embedding**，4096 维。

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('Qwen/Qwen3-Embedding-8B')
embeddings = model.encode(["文档1", "查询"])
```

**优点**：MTEB 双榜 SOTA  
**缺点**：16GB 显存

---

## 🛠️ 4. OpenAI text-embedding-3

```python
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-large",
    input=["文档1", "查询"],
    dimensions=3072,  # 可降至 256
)
```

**优点**：质量稳定  
**缺点**：$0.13/1M tokens，数据出企业

---

## 📊 MTEB 排行榜（前 5 名）

| 排名 | 模型 | MTEB Score | 维度 | 显存 |
|------|------|-----------|------|------|
| 1 | Qwen3-Embedding-8B | 70.8 | 4096 | 16GB |
| 2 | text-embedding-3-large | 68.4 | 3072 | API |
| 3 | BGE-M3 | 65.4 | 1024 | 2GB |
| 4 | bge-large-en-v1.5 | 64.2 | 1024 | 1.5GB |
| 5 | M3E-large | 60.1 | 1024 | 1.5GB |

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 维度越高越好 | ✅ 1024 是性价比甜蜜点 |
| ❌ Embedding 越新越好 | ✅ 取决于场景（中文 BGE 仍强）|
| ❌ OpenAI 一定最强 | ✅ 中文场景 BGE-M3 更优 |
| ❌ Embedding 训练一次永远用 | ✅ 需按场景 fine-tune |

---

## 🔗 兄弟章节

- **本专题**：[Chunking 策略](../chunking-strategies/README.md) / [Hybrid Search](../hybrid-search/README.md) / [Reranker](../reranker/README.md) / [RAG 评估](../../08-llmops/agent-evaluation/09-rag-evaluation/README.md)
- **L1**：[Embedding vs Vectorization](../../01-fundamentals/embedding-vs-vectorization/README.md)
- **咬文嚼字**：[RAG 面试](../../../13.split-hairs/11.ai/rag/README.md)

← [返回 L2 技术栈](../README.md)