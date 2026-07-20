<!--
module:
  parent: ai/agent-architecture/agent-context
  slug: ai/agent-architecture/agent-context/01-chunking
  type: topic
  category: 文本切片
  summary: Chunking 4 大策略对比：fixed / recursive / semantic / agentic / late chunking + chunk size 选型
-->

# Chunking · 文本切片 4 大策略

> **一句话**：Chunking 不是"按 500 字切一刀"那么简单——选错粒度 RAG 召回准确率掉 40%。

← [返回: Agent 长上下文架构](../README.md)

---

## 1. 为什么 Chunking 如此重要？

RAG 召回的"最小单元"就是 chunk——切得太粗，召回噪声大；切得太细，跨段语义丢失。

| 切分粒度 | 召回准确率 | 上下文效率 | 推荐度 |
|---------|-----------|-----------|--------|
| 段落级（500 字）| 65% | 中 | ⭐⭐ |
| 句子级（100 字）| 78% | 低 | ⭐⭐⭐ |
| 语义级（按主题）| **88%** | 高 | ⭐⭐⭐⭐⭐ |
| Agentic 级（按问题）| **92%** | 高 | ⭐⭐⭐⭐⭐ |

---

## 2. 4 大 Chunking 策略

### 2.1 Fixed Chunking（固定切分）

```python
# 最简单：按 500 字符切
chunks = [text[i:i+500] for i in range(0, len(text), 500)]
```

**优点**：实现简单，O(n) 复杂度
**缺点**：可能切断句子、段落、表格
**适用**：纯文本日志 / 文档结构不明确

### 2.2 Recursive Chunking（递归切分）

```python
# 按 ["\n\n", "\n", "。", " "] 优先级回退切分
separator_hierarchy = ["\n\n", "\n", "。", ".", " ", ""]
```

**优点**：保留段落 / 句子完整性
**缺点**：仍是字符级，跨段语义切断
**适用**：大多数文档（Markdown / HTML / PDF 文本）

### 2.3 Semantic Chunking（语义切分）

**核心**：先用 embedding 给句子打分，相邻句子相似度 < 阈值就切。

```python
# pseudocode
def semantic_chunk(sentences, threshold=0.5):
    chunks = [[sentences[0]]]
    for s in sentences[1:]:
        sim = cos_sim(embed(s), embed(chunks[-1][-1]))
        if sim < threshold:
            chunks.append([s])
        else:
            chunks[-1].append(s)
    return chunks
```

**优点**：保留语义连贯性，RAG 召回最佳
**缺点**：计算成本高（O(n²) embedding）
**适用**：高质量 RAG / 知识库问答

### 2.4 Agentic Chunking（智能体切片）

**核心**：用 LLM 自身判断"哪里该切"。

```python
# 用 LLM 判断
prompt = """请将以下文档切成 3-5 个语义块，要求：
- 每块围绕一个核心主题
- 不切断句子
- 保留关键实体（人名 / 时间 / 数字）

文档：[...]
"""
chunks = llm.invoke(prompt).split("[CHUNK]")
```

**优点**：质量最优（理解语义）
**缺点**：慢（每块 LLM 调用）、贵（token 成本）、不可重现
**适用**：低 QPS 高质量场景（如企业内知识库）

### 2.5 Late Chunking（延迟切片，2024 新）

**核心**：先 embedding 完整文档（保留全局上下文），再切分。

```python
# 1. 完整文档 embedding
doc_emb = embed(full_doc)  # sequence-level
# 2. 用 doc_emb 做 chunk 内的 token embedding
# 3. chunk_emb = pool(doc_emb[chunk_start:chunk_end])
```

**优点**：chunk embedding 含全局上下文
**缺点**：实现复杂（需长上下文 embedding 模型）
**适用**：需要"块内文本+全局上下文"双重要求

---

## 3. Chunk Size 选型决策

| chunk size | 适用 | 召回 | 成本 |
|-----------|------|------|------|
| 100-200 token | 精确问答（数字 / 时间）| 80% | 高（块多）|
| 500-1000 token | 一般问答 | 75% | 中 |
| 1500-2000 token | 综述 / 长答 | 70% | 低 |
| > 2000 token | 不推荐（块太大）| < 60% | 低但损失 |

**反直觉**：chunk size 越大 ≠ 越好。当 chunk > 1500 token，RAG 召回准确率开始断崖式下降（噪声信息增多）。

---

## 4. Chunk Overlap（重叠窗口）

```text
[----chunk 1----]
            [----chunk 2----]
                  [----chunk 3----]
```

**为什么需要 overlap**：防止重要信息正好被切断在边界。

**推荐值**：chunk size 的 10-20%（500 字 chunk → overlap 50-100 字）

**反模式**：
- ⚠️ Overlap = chunk size（完全重复，浪费 50% 成本）
- ⚠️ Overlap = 0（边界信息丢失率 5-10%）

---

## 5. Chunk 元数据增强

每个 chunk 加 metadata：

```json
{
  "chunk_id": "doc1_chunk5",
  "text": "...",
  "metadata": {
    "source_doc": "annual_report_2024.pdf",
    "page": 12,
    "section": "财务摘要",
    "chunk_index": 5,
    "total_chunks": 23,
    "embedding_model": "text-embedding-3-small",
    "created_at": "2024-12-01"
  }
}
```

**作用**：
- 召回后可定位原文
- 过滤 / 重排时保留来源信息
- 调试 RAG 失败 case

---

## 6. 反模式 · 5 个常见错

### ⚠️ 反模式 1：固定 500 字符切，不分文档类型

- 错：所有文档统一 fixed chunk 500 字符
- 对：Markdown recursive chunk；PDF 用 layout-aware；对话用 turns

### ⚠️ 反模式 2：chunk size 调很大（2000+）

- 错：图省事，chunk size 调 3000 token
- 对：500-1000 token 召回最佳

### ⚠️ 反模式 3：Overlap 太大

- 错：overlap = 200 token（占 40%）
- 对：overlap = 50-100 token（10-20%）

### ⚠️ 反模式 4：忽略 chunk 元数据

- 错：chunk 只有 text
- 对：加 source_doc / page / section 至少 3 个 metadata

### ⚠️ 反模式 5：chunk 切完不评估

- 错：RAG 上线后不管召回率
- 对：建评测集（query → 期望 chunk），定期重测

---

## 7. 一句话总结

> **Chunking = 召回准确率的根——选对策略（semantic / agentic）+ 选对 size（500-1000）+ 加 overlap（10-20%）+ 加 metadata（4 个字段），RAG 准确率才能跑出来。**

---

← [返回: Agent 长上下文架构](../README.md) · 下一章：[02-rag-in-agent](02-rag-in-agent.md)
