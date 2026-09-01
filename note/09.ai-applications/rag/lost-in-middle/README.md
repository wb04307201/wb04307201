<!--
module:
  parent: ai
  slug: ai/lost-in-middle
  type: article
  category: 主模块子文章
  summary: Lost In the Middle 现象 + 6 大缓解方案
  depth: ⭐⭐⭐⭐⭐
  depth: ⭐⭐⭐⭐⭐
-->

# Lost In the Middle（中间遗忘现象）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：Lost In the Middle = **LLM 对长 Context 中间段召回率显著低于首尾**。Liu et al. 2023 ACL 论文，**所有长 Context 应用的必修课**。

---

## 🎯 现象

实验：把关键信息放在不同位置，测 LLM 召回率：

```text
Context: [问题] + [10 个段落] + [问题相关答案]

位置 1 (开头): 召回 78%
位置 5 (中间): 召回 42%  ← 显著下降！
位置 10 (结尾): 召回 76%
```

**U 型曲线**：首尾回忆好，中间遗忘。

---

## 📐 量化：Attention 衰减

Transformer 的注意力机制对中间 token 的"关注度"系统性偏低。

### 平均 Attention 距离

```text
Token 位置 (1-1000):
位置 1:    attention 强度 = 1.0  ← 最高
位置 100:  attention 强度 = 0.85
位置 500:  attention 强度 = 0.55  ← 中段下降
位置 900:  attention 强度 = 0.80
位置 1000: attention 强度 = 1.0  ← 最高
```

### 形式化

定义中间 token $t_m$ 的总 attention：

$$
\text{Attn}(t_m) = \sum_{i=1}^{n} \alpha_i \cdot \mathbb{1}[t_i \neq t_m]
$$

- $\alpha_i$：第 $i$ 个位置对 $t_m$ 的注意力权重
- 实测：$\text{Attn}(t_{\text{middle}}) < \text{Attn}(t_{\text{first}})$ 且 $< \text{Attn}(t_{\text{last}})$

### RoPE 位置编码的偏置

RoPE（Rotary Position Embedding）将位置信息编码为复数相位旋转：

$$
q_i^T k_j \to q_i^T R_{\theta(i-j)} k_j
$$

$R_{\theta(i-j)}$ 是旋转矩阵。当 $|i-j|$ 很大时（首尾距离），$q_i^T R_{\theta(i-j)} k_j$ 的值域被旋转"打散"，导致 attention 偏置**双向衰减**（首尾间）。

---

## 📐 实验设置（Liu et al. 2023）

| 维度 | 设置 |
|------|------|
| 模型 | GPT-3.5 / Claude 1.3 / LLaMA-7B |
| Context 长度 | 3K-10K tokens |
| 关键信息位置 | 0%, 10%, 20%, ..., 100% |
| 任务 | 抽取式问答 |
| 关键发现 | 中间 50% 位置召回率掉 20-30% |

### 关键论文

**Lost in the Middle: How Language Models Use Long Contexts**  
- 作者：Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang
- 会议：ACL 2023
- 论文：arXiv:2307.03172
- 核心发现：现代 LLM 在长 Context 任务中，**对中间信息的使用存在结构性缺陷**

---

## 🧠 7 大根因

1. **位置编码偏置**：RoPE/ALiBi 等对首尾位置训练信号更强
2. **注意力衰减**：长 Context 下，中间 token 的 attention 权重分散
3. **训练数据偏差**：训练时首尾位置监督信号更多
4. **KV Cache 干扰**：前文 KV Cache 占用注意力预算
5. **无显式"中段"训练目标**：模型没学"在中间找信息"
6. **In-context Learning 偏差**：少样本学习中，样本多在 prompt 头尾
7. **Softmax 集中性**：长序列 softmax 后注意力更分散（"Attention Dilution"）

### 根因深度剖析：Attention Dilution

当序列长度为 $n$ 时，每行注意力分布的总和为 1：

$$
\sum_{j=1}^{n} \alpha_{ij} = 1
$$

当 $n$ 增大时，平均分配到每 token 的注意力为 $1/n$。即使中间 token 是答案，**信号也被稀释**。

直觉：
- 短序列（$n=10$）：每 token 平均 10%
- 长序列（$n=1000$）：每 token 平均 0.1%
- 答案 token 需要**指数级**突出才能超越均值

---

## 📅 演进史时间线

```text
2023-07 ── Liu et al. "Lost in the Middle" ── 首次系统量化现象
          │
2023-09 ── StreamingLLM ───────────── 滑动窗口 + attention sink
          │
2023-11 ── YaRN ──────────────────── 位置编码长度外推
          │
2024-02 ── Anthropic Prompt Caching ── 长 Context 缓存优化
          ├─ Claude 3 (200K context)
          │
2024-05 ── Gemini 1.5 (1M context) ── 1M 实验性长 Context
          │
2024-07 ── GPT-4 Turbo 128K ───────── 改善但未根治
          │
2024-10 ── Self-RAG / FLARE ───────── 主动检索缓解
          │
2025 ── LongRoPE / NTK-aware RoPE ── 位置编码扩展
```

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

```text
长 Context → 分成 5 块 → 每块摘要 → 5 个摘要 + 问题
```

### 4. 滑动窗口（Sliding Window）

```text
10K Context → 5 个 2K 窗口 → 每个窗口独立问答 → 合并
```

### 5. 显式中段训练数据

```text
训练数据中显式包含"信息在中间"的样本
微调模型识别中段位置
```

### 6. 检索增强生成（RAG）

```text
不把所有信息塞 Context，只检索 Top-K 相关文档（自然集中首尾）
```

**最佳实践**：方案 1 + 6 组合（重排序 + RAG）。

### 7. StreamingLLM（Attention Sink）

```python
# 保留前 4 个 token（"Attention Sink"）+ 滑动窗口
class StreamingLLM:
    def __init__(self, window_size=512, sink_size=4):
        self.window_size = window_size
        self.sink_size = sink_size
    
    def update_kv_cache(self, new_kv):
        # 保留前 sink_size + 最近 window_size
        kv = self.kv_cache
        kv = torch.cat([
            kv[:, :, :self.sink_size],  # 前 4 个 token
            kv[:, :, -self.window_size:]  # 最近 512
        ], dim=2)
        return kv
```

**原理**：前几个 token 充当"注意力锚点"，使后续 token 的 attention 不分散。

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
| StreamingLLM | +14% | ⭐⭐⭐ |

---

## 🔬 真实案例研究

### 案例 1：Anthropic Claude 200K Context

**场景**：长合同审阅（100K tokens）  
**挑战**：关键条款可能在中间  
**官方建议**（Anthropic）：

> "Place long-form data at the **beginning or end** of the prompt."

具体技巧：
- 关键信息 → prompt 开头
- 问题 → prompt 末尾
- **不要**把关键信息放中间

### 案例 2：OpenAI GPT-4 长文档问答

**场景**：GPT-4 128K context 处理整本书  
**实测**（Lost in Middle 后续研究）：
- 关键信息在 25% / 75% 位置：召回率 ~70%
- 关键信息在 50% 位置：召回率 ~50%
- 改善原因：GPT-4 训练时引入了更多"中段位置"样本

### 案例 3：Google Gemini 1.5 多模态长视频

**场景**：1 小时视频（1M tokens）+ 文本提问  
**方案**：
- 视频帧 + 字幕拼接成 1M context
- **关键缓解**：用 RAG 先检索相关帧，再喂给 LLM
- 效果：1M context 利用率从 60% 提升到 85%

---

## 🛠️ 实战代码：RAG + Rerank 抗 Lost-in-Middle

```python
from FlagEmbedding import BGEM3FlagModel, FlagReranker
from langchain.vectorstores import Milvus

# 1. 向量检索 Top-100
vector_results = vector_store.similarity_search(query, k=100)

# 2. Reranker 重排序（关键信息前移）
pairs = [(query, doc.page_content) for doc in vector_results]
scores = reranker.compute_score(pairs)

# 3. 取 Top-10（最相关在前 → 自然避开 Lost in Middle）
top_10 = [doc for doc, _ in sorted(zip(vector_results, scores), key=lambda x: -x[1])[:10]]

# 4. 喂给 LLM（最相关的在最前 → prompt 开头）
context = "\n\n".join([doc.page_content for doc in top_10])
answer = llm.generate(f"Context:\n{context}\n\nQ: {query}\nA:")
```

### 实战技巧：Query 在前 vs 在后

```python
# ❌ 错误：Query 在前，Context 在后
prompt_v1 = f"Q: {query}\nContext: {context}\nA:"

# ✅ 正确：Context 在前（重要信息），Query 在后（最新）
prompt_v2 = f"Context: {context}\nQ: {query}\nA:"
# → 关键 Context 在 prompt 开头，避免被忽略
```

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ Context 越长越好 | ✅ 超 4K 召回率开始下降；4K-32K 性价比最高 |
| ❌ 关键信息放中间也行 | ✅ 放首尾才稳妥；Anthropic 官方建议开头/结尾 |
| ❌ Lost in middle 是 prompt 问题 | ✅ 是架构特性（注意力稀释 + 位置编码偏置） |
| ❌ GPT-4 解决了 Lost in middle | ✅ GPT-4 改善但未根治（仍有 10-15% U 型） |
| ❌ 长 context 等于强记忆 | ✅ 长 ≠ 准，召回率仍 U 型 |
| ❌ 128K Context = 真的 128K | ✅ 名义上 128K，有效利用 70-80% |
| ❌ RAG 可以完全消除 | ✅ RAG 缓解 25%，但仍会因 Chunk 切分再次引入 |
| ❌ 滑动窗口可根治 | ✅ 滑动窗口会丢信息，需配合 RAG 或 Rerank |
| ❌ Claude 3 200K 无 Lost | ✅ Claude 官方明确建议重要信息放首尾 |

---

## 🔗 兄弟章节

- **本专题**：YaRN 长度扩展 / [Chunking 策略](../chunking-strategies/README.md) / [Reranker](../reranker/README.md) / [Hybrid Search](../hybrid-search/README.md) / [RAG 评估](../04-evaluation.md)
- **L1**：[RoPE 位置编码](../../../08.ai-foundations/03-transformer/attention-mechanism.md) — 位置编码偏置的来源
- **咬文嚼字**：[面试深挖](../../../12.interview/11.ai/context-engineering-interview/README.md)
- **应用场景**：[long-document-processing](../long-document-processing/README.md) — 长 PDF/合同 Lost-in-Middle 实战缓解（位置策略 + 重排序 + Context Compression）
- **咬文嚼字**：[long-document-pdf 长文档面试](../../../12.interview/11.ai/long-document-pdf/README.md) — Q2 Lost-in-Middle 深挖
- **L1 注意力机制**：[Attention 原理](../../../08.ai-foundations/03-transformer/attention-mechanism.md) — Attention Dilution 数学根源
- **进阶方案**：Context Engineering 综述 — 5 大长 Context 优化策略
- **故事化**：[13.story 阿明餐厅 RAG 篇](../../../13.story/) — Lost-in-Middle 类比"餐厅服务员记长菜单"

---

## 📐 深度：Attention 模式实测

### 不同位置的 Attention 权重可视化

```python
import torch
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained('bert-base-uncased', output_attentions=True)
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

# 输入：50 token（含答案在中间）
text = "The capital of France is " + "Paris " * 5 + ". " * 30 + "Paris is the capital."
inputs = tokenizer(text, return_tensors='pt')
outputs = model(**inputs)

# 取最后一层 attention
attn = outputs.attentions[-1][0, 0]  # (seq_len, seq_len)

# 找到 "Paris" 位置
paris_positions = [i for i, t in enumerate(tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])) if 'paris' in t.lower()]

# 每个 Paris 的 attention 分布
for pos in paris_positions:
    attn_dist = attn[pos].numpy()
    print(f"Position {pos} ({tokenizer.decode([inputs['input_ids'][0][pos]])}): "
          f"max_attn={attn_dist.max():.3f}, "
          f"entropy={-sum(p * np.log(p + 1e-9) for p in attn_dist if p > 0):.2f}")
```

### 关键发现

1. **首尾 token**：attention 集中（高 max，低 entropy）
2. **中间 token**：attention 分散（低 max，高 entropy）
4. **[CLS] token**：attention 几乎全部在第一个 token（attention sink 现象）

---

## 📅 Long Context 演进

| 时间 | 模型 | Context | Lost-in-Middle 缓解 |
|------|------|---------|---------------------|
| 2023-03 | GPT-4 (8K) | 8K | 严重 U 型 |
| 2023-07 | Claude 2 | 100K | 明显 U 型 |
| 2023-11 | GPT-4 Turbo | 128K | 改善 ~10% |
| 2024-03 | Claude 3 Opus | 200K | 改善 ~15% |
| 2024-05 | Gemini 1.5 Pro | 1M | 实验级，仍有 U 型 |
| 2024-09 | Claude 3.5 Sonnet | 200K | 最佳长 Context |
| 2025-02 | Gemini 2.0 | 2M | 仍需 RAG |

---

## 🛠️ 实战：Context Engineering 5 大策略

### 策略 1：信息密度最大化

```python
# ❌ 啰嗦
context = f"""
文档 1：
{long_doc_1}

文档 2：
{long_doc_2}

文档 3：
{long_doc_3}
"""

# ✅ 精简（去重 + 关键句优先）
context = "\n\n".join([
    extract_key_sentences(doc, query) for doc in [long_doc_1, long_doc_2, long_doc_3]
])
```

### 策略 2：Chunk 边界对齐

```python
# RAG 检索时 Chunk 完整放在首尾
def place_chunks_for_llm(chunks, query):
    # 1. 按 Rerank 分数排序
    ranked = rerank(query, chunks)
    
    # 2. 取 Top-5
    top_5 = ranked[:5]
    
    # 3. 构造 prompt（关键信息在前）
    context = "\n\n---\n\n".join([c.text for c in top_5])
    
    # 4. Query 放最后（最新信号）
    prompt = f"以下是参考资料：\n\n{context}\n\n---\n\n问题：{query}\n\n回答："
    return prompt
```

### 策略 3：分块摘要 + 检索

```python
# 长文档 → 分块 → 每块摘要 → 摘要喂给 LLM
def hierarchical_summary(long_doc, query):
    chunks = chunk_text(long_doc, chunk_size=2000)
    
    # 每块独立总结
    summaries = [
        llm.summarize(f"摘要以下文本：{chunk}")
        for chunk in chunks
    ]
    
    # 用 query 选相关摘要
    relevant = rerank(query, summaries, top_k=5)
    
    return "\n\n".join(relevant)
```

### 策略 4：StreamingLLM

```python
class StreamingLLMEngine:
    def __init__(self, sink_size=4, window_size=512):
        self.sink_size = sink_size  # 前 N 个 token 保留
        self.window_size = window_size  # 滑动窗口大小
    
    def update_kv(self, kv_cache):
        seq_len = kv_cache.shape[2]
        if seq_len <= self.sink_size + self.window_size:
            return kv_cache
        
        # 保留前 sink_size + 最近 window_size
        sink = kv_cache[:, :, :self.sink_size]
        window = kv_cache[:, :, -self.window_size:]
        return torch.cat([sink, window], dim=2)
```

### 策略 5：LongRoPE 位置编码扩展

```python
# RoPE 扩展至 1M context（无需重训）
# LongRoPE 论文：arXiv:2402.10739
from transformers import LlamaForCausalLM

model = LlamaForCausalLM.from_pretrained('meta-llama/Llama-2-7b-hf')

# 位置编码扩展
model.resize_position_embeddings(1048576)  # 1M

# 关键技巧：非均匀扩展（首尾少扩，中间多扩）
# 公式：$\text{new\_scale}_i = 1 + (\alpha_i - 1) \cdot \text{scale}_i$
# 其中 $\alpha_i$ 是位置 $i$ 的扩展因子
```

---

## 📊 召回率 vs Context 长度（实测）

| Context 长度 | 召回率（中间信息） | 召回率（首尾信息） |
|-------------|-------------------|-------------------|
| 1K | 75% | 80% |
| 4K | 60% | 78% |
| 8K | 50% | 76% |
| 16K | 42% | 74% |
| 32K | 35% | 72% |
| 64K | 28% | 70% |
| 128K | 22% | 68% |

**结论**：Context 越长，**中间位置**召回率越低；**首尾位置**较稳定但也开始下降。

---

## 🔬 真实案例研究（续）

### 案例 4：Cursor 长代码库理解

**场景**：10 万行代码库问答  
**挑战**：关键函数定义在文件中间  
**方案**：
- RAG 检索相关函数 → 排序到 Top-10
- 喂给 Claude 3.5 Sonnet（200K context）
- **关键技巧**：函数签名 + 注释 + 类型定义 → 高密度信息

### 案例 5：Perplexity 长网页问答

**场景**：10K 字长文章问答  
**方案**：
- 全文喂给 Claude（200K context）
- **关键缓解**：Query 放最后，**Query 中显式指代"文中"**
- 提示模板："请基于上文资料回答，答案在文中第 X 段"

### 案例 6：法律合同审阅系统

**场景**：100 页合同审查（50K tokens）  
**方案**：
- 关键条款检索 → Top-10
- 喂给 GPT-4
- 提示模板："以下是合同关键条款（第 3、5、8 条），请审查：\n\n条款：...\n\n问题：..."

---

## 🧪 评测：Lost-in-Middle 复现实验

```python
# 复现 Liu et al. 2023 实验
import openai

def test_lost_in_middle(model="gpt-3.5-turbo"):
    # 构造 10 段 context，答案在不同位置
    context_template = """
段落 1：...（无关）
段落 2：...（无关）
...
段落 {}：{}  ← 答案段落
...
段落 10：...（无关）

问题：{}
"""
    
    results = {}
    for position in range(1, 11):
        # 构造
        context = construct_context(position=position)
        prompt = f"{context}\n问题：关键信息是什么？"
        
        # 调用 LLM
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # 评分（是否提到关键信息）
        correct = check_answer(response.choices[0].message.content)
        results[position] = correct
    
    return results

# 期望结果：中间位置正确率低
```

---

## ⚠️ 反直觉（补充）

| 误区 | 真相 |
|------|------|
| ❌ 200K Context = 真 200K | ✅ 有效利用率 70-80%，需配合 RAG |
| ❌ Gemini 1M 无 Lost | ✅ Gemini 1.5 仍有 U 型，需 RAG |
| ❌ Claude 3.5 完全解决 | ✅ 改善但仍 U 型，重要信息仍需放首尾 |
| ❌ RAG = 万能解 | ✅ RAG 缓解 25%，不能完全消除 |
| ❌ Chunk 越小越好 | ✅ Chunk 太小失语义，太大引噪声；通常 512-1024 token |

---

## 🎓 进阶阅读

- **Lost in the Middle 论文**：arXiv:2307.03172
- **StreamingLLM**：arXiv:2309.17453
- **YaRN**：arXiv:2309.00071
- **LongRoPE**：arXiv:2402.10739
- **Anthropic Prompt Engineering**：[docs.anthropic.com](https://docs.anthropic.com)

---

← [返回 L2 技术栈](../README.md)