<!--
module:
  parent: ai/agent-architecture/agent-context
  slug: ai/agent-architecture/agent-context/06-long-context-models
  type: topic
  category: 长上下文模型
  summary: Gemini 1.5 / Claude 3.5 / Qwen 2.5 等 100k+ 上下文模型的实测、Lost in the Middle 现象、YaRN 扩展技术
-->

# Long-Context Models · 直接吃长上下文的模型

> **一句话**：Gemini 1.5 Pro 1M token 听上去美好——但**Lost in the Middle** 让 P50 准确率掉 30%+，长上下文是「成本 + 注意力衰减」双刃剑。

← [返回: Agent 长上下文架构](../README.md)

---

## 1. 主流长上下文模型（2024-2025）

| 模型 | 上下文长度 | 评测实测有效长度 | 价格（输入/百万 token）|
|------|-----------|------------------|------------------------|
| **Gemini 1.5 Pro** | 1M | **100-200k** | $1.25 |
| Gemini 1.5 Flash | 1M | 100-200k | $0.075 |
| **Claude 3.5 Sonnet** | 200k | ~150k | $3.00 |
| Claude 3 Opus | 200k | ~100k | $15.00 |
| **GPT-4o** | 128k | ~80k | $2.50 |
| **Qwen 2.5** | 128k | ~80k | $0.40（开源免费）|
| LLaMA 3.1 | 128k | ~60k | 自部署成本 |
| Mistral Large 2 | 128k | ~80k | $2.00 |
| GLM-4 | 128k | ~80k | 自部署 |
| DeepSeek V2.5 | 128k | ~80k | 自部署 |

> 关键洞察：**"上下文长度 1M" ≠ "有效长度 1M"**——评测显示 LLM 在 > 60-80k 时即开始衰减。

---

## 2. Lost in the Middle 现象

**核心论文**：Liu et al., "Lost in the Middle" (2023)

**实验**：在 1-30k context 中，模型在"信息在 prompt 中间"时准确率最低，**两端信息利用最佳**。

```text
[Relevant Info] ... [4000 tokens] ... [Answer needed here] ... [4000 tokens] ... [Relevant Info]
```

| 位置 | 准确率 |
|------|--------|
| Prompt 开头 | 85% |
| Prompt 中间 | **58%** |
| Prompt 结尾 | 80% |

**反直觉**：不是"上下文越长越准"——是"重要信息放两端最准"。

---

## 3. 训练技巧（让模型用好长上下文）

### 3.1 Position Interpolation (PI)

- Microsoft Research, 2023
- 把上下文长度从 4k 扩展到 32k，仅靠位置编码插值
- Qwen / LLaMA 等都借鉴

### 3.2 YaRN（Yet another RoPE extensioN）

- 2023
- 修改 RoPE 频率 + 注意力缩放
- 4k → 128k 训练成本仅 0.1% of full retrain

### 3.3 LongLoRA

- 2023
- 微调时 shifted sparse attention
- 训练加速 2x，推理仍 full attention

### 3.4 Ring Attention

- 2024
- 把 context 分到多卡，每卡看自己段，最后跨卡 attention
- 1M+ context 训练可行

---

## 4. 实战：Agent 在 100k+ 上下文的玩法

### 4.1 文档问答（一次性）

```python
# 把 100k 文档一次性塞 prompt
response = llm.invoke(
    f"基于以下文档回答：{long_doc[:100_000]}\n\n问题：{query}"
)
```

**注意**：成本 = tokens × 0.4/M，若文档频繁使用建议 RAG。

### 4.2 代码库问答

```python
# 把整个代码库塞 prompt（小型项目可行）
files = glob("src/**/*.py", recursive=True)
all_code = "\n\n".join(open(f).read() for f in files)
response = llm.invoke(f"代码库：\n{all_code}\n\n问题：...")
```

**注意**：超 200k 要用 RAG + 检索而非全塞。

### 4.3 长对话（累积）

```python
# Agent 长期记忆
messages = [
    SystemMessage(...),
    *conversation_history,  # 累积所有轮次
    HumanMessage(query)
]
response = llm.invoke(messages)
```

**注意**：超 32k 后需 sliding window + summary。

---

## 5. Lost in the Middle 的 6 个缓解技巧

### 5.1 重要信息放两端

```python
# 不要：
prompt = f"前面背景：{bg}\n\n关键信息：{key_info}\n\n继续内容：{rest}\n\n问题：{query}"
# 反而 Lost in Middle！
# 应该：
prompt = f"关键信息：{key_info}\n\n背景：{bg}\n\n问题：{query}"
```

### 5.2 重排序（信息按相关性排序）

```python
# 用 embedding 相关性，把最相关的放开头/结尾
docs = sorted(docs, key=lambda d: cos_sim(d, query))
prompt = "\n\n".join(docs)  # 重要信息两端，中间次要
```

### 5.3 RAG 替代

- 与其塞 100k，不如检索 top-10 给 LLM
- RAG 天然规避 Lost in Middle

### 5.4 多轮 retrieve + 总结

```python
# 每轮只检索与本轮最相关部分
for turn in conversation:
    relevant = retrieve(query, top_k=5)
    prompt = f"相关历史：{relevant}\n\n当前问题：{turn}"
```

### 5.5 显式标位置

```python
# 让 LLM 知道信息在哪
prompt = "[位置 A] 这是事实 1\n[位置 B] 这是事实 2\n[位置 C] 这是答案所在\n\n问题：..."
```

### 5.6 Re-ranking

- 用 cross-encoder reranker 找出最相关 chunk
- 把 rerank 后的 top-k 放在 prompt 两端

---

## 6. 何时用 Long-Context vs RAG？

| 场景 | Long-Context 优先 | RAG 优先 |
|------|-------------------|-----------|
| 单次文档问答 | ✅ 文档 < 32k | ✅ 文档 > 100k |
| 跨文档分析 | ❌ 容易 Lost in Middle | ✅ RAG + Re-rank |
| 代码库问答 | ✅ < 50k 行 | ✅ > 100k 行 |
| 长对话 | ❌ 累积爆炸 | ✅ Memory 模块 |
| 多轮检索 | ✅ 避免多轮网络 | ✅ |
| 成本敏感 | ❌ 高 | ✅ 低 |

**黄金法则**：**先用 RAG 试，召回不足时再上 Long-Context**（而不是相反）

---

## 7. 反模式 · 5 个常见错

### ⚠️ 反模式 1：盲目追求 1M context

- 错："用 Gemini 1.5 1M，直接塞"
- 对：评测有效长度（多在 100-200k）

### ⚠️ 反模式 2：忽略 Lost in the Middle

- 错：把关键信息放中间
- 对：重要信息放两端 + 标位置

### ⚠️ 反模式 3：不评估就上

- 错："上下文 128k 一定够用"
- 对：建评测集验证 P50/P95

### ⚠️ 反模式 4：成本失控

- 错：每次都塞 100k context
- 对：用 RAG + 检索减少 context

### ⚠️ 反模式 5：Long-Context 替代 RAG

- 错：Long-Context 后就不用 RAG
- 对：两者互补，策略组合

---

## 8. 一句话总结

> **Long-Context Models 是"能力"——但 Lost in the Middle 是"局限"。Agent 部署长上下文要算 5 笔账：上下文长度 / 有效长度 / Lost in Middle 风险 / 成本 / 与其他策略的协同。**

---

← [返回: Agent 长上下文架构](../README.md) · 上一章：[05-sub-agents-decomposition](05-sub-agents-decomposition.md) · 下一章：[07-decision-tree](07-decision-tree.md)
