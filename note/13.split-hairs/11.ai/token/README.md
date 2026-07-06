<!--
question:
  id: 11.ai-token
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [11.ai, LLM, token]
-->

# Token 与计费 — LLM 经济学面试深挖

> 一句话定位：Token 是 LLM 的最小处理单位，直接决定费用、速度和上下文窗口 —— 是所有 LLM 应用的底层经济学基础。完整概念见 [主模块 Token 与计费](../../../11.ai/02-technology-stack/token-billing/README.md)。

---

## 引子：5 个 token 收 0.001 元，PM 怒了

```text
产品经理："我们就让 AI 写个会议纪要，为什么一次跑了 0.5 元？"
你："用户输入 8000 字上下文、会议录音转写 4000 字、再加上历史对话 5000 字……17000 字按 1 字 ≈ 1.5 token 算，就是 25500 token。"
PM："我们写个会议纪要才 800 字，输入怎么会是输出的 30 倍？"
你："因为输出的 token 比输入贵 2-3 倍。"
PM："……"
```

**真相**：LLM 不按字数收费，按 **Token** 收费。

- 1 个英文单词 ≈ 1-1.5 token
- **1 个中文字 ≈ 1-2 token（中文效率天生低于英文）**
- 输入便宜，输出贵（GPT-4 输入 $0.03/1k vs 输出 $0.06/1k）
- 图片、音频转 embedding 后**也按 token 算**

不懂 Token，AI 项目成本一定爆炸。

## 一、Token 是什么（一句话）

**Token ≠ 字符 ≠ 单词**：是分词算法（Tokenizer）处理后的最小单元。

```
"Hello, world!" → ["Hello", ",", " world", "!"] → 4 token
"我爱中国"      → ["我", "爱", "中国"]          → 3 token
```

**关键比例**：
- 1 个英文单词 ≈ 1-1.5 个 token
- **1 个中文字 ≈ 1-2 个 token（中文效率低于英文）**
- 标点、空格、数字也占 token

---

## 二、面试陷阱

### 陷阱 1：以为 1 字 = 1 token
- **真相**：中文 1 字 ≈ 1-2 token；英文 1 词 ≈ 1-1.5 token；代码比自然语言更占 token。

### 陷阱 2：以为上下文窗口越大越好
- **真相**：上下文窗口越大，**注意力 O(n²) 复杂度**导致推理变慢 + 成本飙升；Lost in the Middle 现象让中间信息被忽略。

### 陷阱 3：以为输出 token 不重要
- **真相**：输出 token 通常**比输入贵 2-3 倍**（GPT-4 输入 $0.03/1k vs 输出 $0.06/1k）；模型倾向于"凑长度"，必须明确长度要求。

### 陷阱 4：不考虑图片/音频的 token 消耗
- **真相**：图片、音频嵌入后**也变成 token**，一张 1024×1024 图 ≈ 1024 个 token（按 patch 算），不可忽视。

### 陷阱 5：忽视 Prompt Cache
- **真相**：Anthropic / OpenAI 提供 Prompt Cache（相同前缀复用），cache 命中部分价格降 80%+。

---

## 三、3 大分词算法

| 算法 | 原理 | 使用者 |
|------|------|--------|
| **BPE** | 合并最频繁字符对 | GPT / LLaMA / Claude |
| **WordPiece** | 用似然度合并 | BERT / DistilBERT |
| **SentencePiece** | 无语言依赖、Unicode 上操作 | T5 / 多语言模型 |

---

## 四、Token 优化 3 大手段

1. **输入端**：RAG 只检索相关片段、压缩对话历史、删减无关内容
2. **输出端**：明确长度要求（"用一句话"比"用 300 字"省 token）
3. **缓存**：Prompt Cache（Anthropic / OpenAI）+ KV Cache（模型内部）

---

## 五、反直觉点

- **生成是串行的**：自回归模型每生成 1 个 token 都要一次完整前向传播，速度 ~50-100 token/秒。
- **中文比英文"贵"**：同样语义内容，中文 token 数约是英文的 1.5-2 倍。
- **代码更占 token**：缩进、标点、关键词让代码 token 密度比自然语言高。

---

## 六、上下文窗口速查

| 模型 | 窗口 | 约等于 |
|------|------|--------|
| GPT-3.5 | 4K | ~3000 字中文 |
| GPT-4 | 8K / 32K / 128K | ~6k / 24k / 100k 字 |
| Claude 3.5 | 200K | ~150k 字 |
| Claude 4 | 1M | ~750k 字 |
| Gemini 1.5 Pro | 1M-2M | 极大 |

---

## 七、30 秒面试话术

> Token 是 LLM 的最小处理单位，由分词算法（Tokenizer）生成。
>
> 分词算法：BPE（GPT/LLaMA/Claude，合并最频繁字符对）、WordPiece（BERT，用似然度合并）、SentencePiece（T5，无语言依赖）。
>
> Token 的重要性：上下文窗口限制（输入+输出 ≤ 模型窗口，如 GPT-4 是 128k token）、计费（按 token 计费，1 中文字 ≈ 1-2 token，1 英文词 ≈ 1-1.5 token）、生成速度（自回归模型串行生成，~50-100 token/秒）。
>
> 优化技巧：输入端 RAG 检索关键片段、压缩对话历史；输出端明确长度要求；缓存用 Prompt Cache、KV Cache。
>
> 工具：`tiktoken` 库可精确计算 token 数。

---

## 八、深度阅读

- 主模块：[Token 与计费](../../../11.ai/02-technology-stack/token-billing/README.md)
- 上游：[Transformer 架构](../../../11.ai/01-fundamentals/transformer/README.md)
- 关联：[Context Engineering](../context-engineering/README.md) — Context Window 是 Token 上限
- 关联：[RAG](../rag/README.md) — 用 RAG 减少 Token 消耗

---

> 📅 2026-06-30 · 咬文嚼字 · AI 经济学基础 · ⭐⭐⭐⭐

← [返回: 咬文嚼字 · token](README.md)
