<!--
module:
  parent: ai/agent-architecture/agent-context
  slug: ai/agent-architecture/agent-context/02-rag-in-agent
  type: topic
  category: Agent 中的 RAG
  summary: Agent 视角下 RAG vs 长上下文的边界 —— RAG 何时有效、何时被错误替代、Agentic RAG 与传统 RAG 区别
-->

# RAG 在 Agent 中的角色 · 长上下文时代的边界

> **一句话**：RAG 不是"长上下文的银弹"——它是"按需检索 + 过滤噪声"的工具，但在 Agent 场景下 RAG 不能取代所有长上下文。

← [返回: Agent 长上下文架构](../README.md)

---

## 1. RAG 在 Agent 场景的 3 大局限

### 1.1 不能取代会话上下文

会话上下文包含：
- 用户意图轨迹（"我刚才问的是 X"）
- 多轮反馈修正（"用更通俗的语言"）
- 临时信息（用户在第 3 轮提到的名字）

**RAG 解决不了**：这些信息不在外部知识库，是 prompt 内的"上下文状态"。

### 1.2 不能取代多步推理的中间状态

Agent 跑 ReAct / Plan-Execute 时：
- 步骤 1 的中间结果 → 步骤 2 的输入
- Tool call 的返回值 → 下一步决策依据

**RAG 解决不了**：这种"工作内存"必须存在 prompt 内（或 memory 模块），不能用"搜索外部文档"替代。

### 1.3 不能取代系统提示

System prompt 包含角色定义、输出格式、约束规则——这些是固定上下文，RAG 没有意义（甚至会污染）。

---

## 2. Agentic RAG vs 传统 RAG

### 2.1 传统 RAG（被动）

```
Query → Embed → 检索 top-k → 拼接到 prompt → LLM
```

**特点**：单轮静态

### 2.2 Agentic RAG（主动）

```
Query → Agent 决策：
  ├─ 检索？→ 改写 query → 检索 → 判断是否够 → 不够继续改写
  ├─ 直接回答？→ 跳过 RAG
  └─ 多次检索？→ multi-hop retrieval（递归）
                   ↓
                  综合结果 → LLM
```

**特点**：多轮动态，Agent 自己决定"用不用 RAG / 用几次 / 怎么改写"

### 2.3 关键差异

| 维度 | 传统 RAG | Agentic RAG |
|------|---------|--------------|
| 检索轮数 | 1 轮 | 1-N 轮 |
| Query 改写 | 静态 | 动态 |
| 决策权 | 写死流程 | Agent 自决 |
| 适用 | 单次问答 | 复杂多跳查询 |
| 成本 | 低 | 中高（多次检索）|

---

## 3. RAG + 长上下文混合方案

### 3.1 模式 A：RAG 兜底 + Long-Context 优先

```
Agent 收到长输入 → 优先塞进 prompt（用 100k+ 模型）
  ↓
答案质量不够？→ 触发 RAG 检索补充
```

**适用**：长输入 90% 答案靠上下文，10% 需要 RAG 补全
**优势**：主流程快，RAG 只在失败时兜底

### 3.2 模式 B：Long-Context 兜底 + RAG 优先

```
Agent 收到问题 → 先 RAG 检索 top-k
  ↓
RAG 结果不足 → 把 top-k + 完整文档（受 long-context 限制）都给 LLM
```

**适用**：知识库为主，偶尔需要看原文
**优势**：成本可控（默认 RAG 便宜）

### 3.3 模式 C：双轨（Hybrid）

```
并行执行：
- 路径 1：RAG（top-k 检索）
- 路径 2：Long-Context（直接塞）
  ↓
结果交叉验证 → 输出置信度
```

**适用**：金融 / 医疗等高准确性场景
**优势**：双保险

---

## 4. RAG 召回失败的 5 个常见原因

| 失败类型 | 原因 | 修复 |
|---------|------|------|
| **答非所问** | chunk 没命中 | 调 embedding 模型 / 改 query |
| **漏召回** | top-k 太小 / chunk 太大 | top-k 提到 20-50 |
| **噪声过多** | chunk 含无关内容 | Re-rank 模型 / 加过滤 |
| **过时** | 知识库未更新 | 加文档版本 + TTL |
| **片段不完整** | chunk 切断关键信息 | 调 chunk size + overlap |

**调优流程**：建评测集 → 监控召回率 → 调 embedding / chunking / re-rank

---

## 5. Re-rank 重排序（关键步骤）

RAG 三步走：**粗召回 → 重排 → 拼 prompt**

```python
# Step 1: 粗召回（向量相似度）
hits = vector_store.search(query, top_k=50)

# Step 2: 重排（cross-encoder）
from sentence_transformers import CrossEncoder
reranker = CrossEncoder('BAAI/bge-reranker-large')
scores = reranker.predict([(query, h.text) for h in hits])
hits = sorted(zip(hits, scores), key=lambda x: -x[1])[:5]
```

**为什么需要 Re-rank？**
- 向量相似度 ≠ 真实相关性（不同任务、不同 query 类型）
- Cross-Encoder 同时看 query + doc，给出更准确分数
- 经验值：粗召回 50，重排 top 5

---

## 6. 多跳 RAG（Multi-hop）

**场景**：问题涉及多个文档交叉

```
Q："X 产品的竞品 Y 在 2023 年的销量是什么？"
  - 跳 1：检索 X 产品的竞品 → Y
  - 跳 2：检索 Y 在 2023 年的销量
  - 综合 → 答案
```

**实现**：Agent 循环执行 RAG，每轮把上轮结果加入 query。

---

## 7. 反模式 · RAG 应用的 5 个错

### ⚠️ 反模式 1：RAG 替代一切长上下文

- 错："反正 RAG 便宜，所有上下文都用 RAG"
- 对：会话上下文 + 多步推理状态必须用 prompt context

### ⚠️ 反模式 2：忽略 Re-rank

- 错：粗召回 top-5 直接拼 prompt
- 对：粗召回 top-50 + Re-rank top-5

### ⚠️ 反模式 3：chunking 不评估

- 错：chunking 切完直接上线
- 对：建 50+ query 评测集监控

### ⚠️ 反模式 4：embedding 模型不更新

- 错：用旧 embedding 模型（如 ada-002）几年不换
- 对：2024 主流 bge-large / text-embedding-3

### ⚠️ 反模式 5：RAG 与 Fine-tuning 选错

- 错：用 RAG 给模型加新知识（实则 Fine-tune 才对）
- 对：详见 [12.story/39-ai-private-deployment](../../../12.story/39-ai-private-deployment.md) 的"先 RAG 再微调"

---

## 8. 一句话总结

> **RAG 在 Agent 场景下是「按需检索」工具，不是「长上下文替代」——它解决外部知识查询，不能解决会话状态和推理中间结果。Agentic RAG + Re-rank + 多跳 是工业级方案。**

---

← [返回: Agent 长上下文架构](../README.md) · 上一章：[01-chunking](01-chunking.md) · 下一章：[03-memory-strategies](03-memory-strategies.md)
