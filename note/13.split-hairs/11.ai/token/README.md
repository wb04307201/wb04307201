# Token 与计费原理

## 引子：为什么 GPT 按 Token 收费？

```
输入："Hello, world!"
→ 被分成：["Hello", ",", " world", "!"]
→ 4 个 token

输入："今天天气不错"
→ 被分成：["今天", "天气", "不错"]
→ 3 个 token（中文分词不一样）

计费：输入 $0.01 / 1K tokens，输出 $0.03 / 1K tokens
```

Token 不是"字符"也不是"单词"，而是 LLM 的**最小处理单位**。

为什么要有 Token？因为模型不能直接理解文本——必须先把文本切成小块，每块变成一个数字向量。

Token 的数量直接决定了：
- **费用**：token 越多越贵
- **速度**：token 越多越慢
- **上下文长度**：4K、8K、32K token 限制

---

## 一、什么是 Token

**Token** 不是"字符"也不是"单词"，而是**分词算法（Tokenizer）处理后的最小单元**。

### 示例

```
输入："Hello, world!"

Tokenizer 输出（以 GPT-4 为例）：
["Hello", ",", " world", "!"]  → 4 个 token

输入："我爱中国"

Tokenizer 输出（中文）：
["我", "爱", "中国"]  → 3 个 token（可能，不同 tokenizer 结果不同）
```

**关键**：
- **1 个英文单词 ≈ 1-1.5 个 token**
- **1 个中文字 ≈ 1-2 个 token**（中文效率低于英文）
- **标点、空格、数字也占 token**

---

## 二、分词算法

### 2.1 BPE（Byte-Pair Encoding）

**思想**：从字符级别开始，**合并最频繁的对**，构建词表。

```
初始词表：['a', 'b', 'c', ...]
训练数据："abab abc"

迭代 1：合并最频繁的对 "ab" → 新 token "ab"
词表：['a', 'b', 'c', ..., 'ab']

迭代 2：合并 "abc" → 新 token "abc"
词表：['a', 'b', 'c', ..., 'ab', 'abc']
```

**使用者**：GPT 系列、LLaMA、Claude

### 2.2 WordPiece

类似 BPE，但用**似然度**而非频率选择合并。

**使用者**：BERT、DistilBERT

### 2.3 SentencePiece

**无语言依赖**，直接在 Unicode 上操作，支持中日韩。

**使用者**：T5、多语言模型

---

## 三、为什么 Token 重要

### 3.1 上下文窗口限制

| 模型 | 上下文窗口（token） | 约等于 |
|------|------------------|--------|
| GPT-3.5 | 4,096 | ~3000 字中文 |
| GPT-4 | 8,192 / 32,768 / 128k | ~6k / 24k / 100k 字中文 |
| Claude 3.5 | 200,000 | ~150k 字中文 |
| LLaMA 3 | 8,192 | ~6k 字中文 |

**影响**：
- 输入 + 输出总和不能超过上下文窗口
- 长文档需要分块（RAG）

### 3.2 计费

```
计费公式：费用 = (输入 token + 输出 token) × 单价

示例（GPT-4，2024 年价格）：
- 输入：$0.03 / 1k token
- 输出：$0.06 / 1k token

100k 字中文文档（约 130k token）：
- 输入费用：130 × 0.03 = $3.9
- 如果输出 1k token：1 × 0.06 = $0.06
- 总计：~$4
```

### 3.3 生成速度

**Token 生成是串行的**（自回归模型）：
- 每生成 1 个 token 都要经过一次完整前向传播
- 生成速度：~50-100 token/秒（取决于模型大小、硬件）

---

## 四、Token 计算工具

### Python 示例

```python
import tiktoken

# GPT-4 使用 cl100k_base 编码
encoding = tiktoken.get_encoding("cl100k_base")

text = "Hello, world! 你好世界"
tokens = encoding.encode(text)

print(f"文本: {text}")
print(f"Token 数: {len(tokens)}")  # 输出：Token 数: 8
print(f"Token IDs: {tokens}")  # [9906, 11, 995, 0, 57612, 62, 52345, 244]
```

### 估算公式

```python
def estimate_tokens(text):
    # 粗略估算
    cn_chars = sum(1 for c in text if '一' <= c <= '鿿')
    other_chars = len(text) - cn_chars
    
    # 中文 ~1.5 token/字，英文 ~0.25 token/字符
    return int(cn_chars * 1.5 + other_chars * 0.25)
```

---

## 五、优化 Token 使用

### 5.1 输入端优化

```
❌ 浪费：
"请根据以下文档回答问题：[5000 字文档]。问题：文档的主题是什么？"

✅ 优化：
"总结主题：[关键段落]"
```

**技巧**：
- 删减无关内容
- 用 RAG 只检索相关片段
- 压缩历史对话

### 5.2 输出端优化

```
❌ 浪费：
"请用 300 字总结..."（模型倾向于接近上限）

✅ 优化：
"用一句话总结..."
```

### 5.3 缓存与复用

- **Prompt Cache**：Anthropic / OpenAI 提供缓存（相同前缀复用）
- **KV Cache**：模型内部缓存（透明）

---

## 六、Token 常见陷阱

| 陷阱 | 说明 |
|------|------|
| **以为 1 字 = 1 token** | 中文 1 字 ≈ 1-2 token |
| **忽略标点空格** | 每个都占 token |
| **代码效率更低** | 代码通常比自然语言占用更多 token |
| **嵌入也占 token** | 图片、音频嵌入后也变成 token |

---

## 七、面试话术（30 秒版）

> "Token 是 LLM 的最小处理单位，由**分词算法（Tokenizer）**生成。
>
> **分词算法**：
> - **BPE**（GPT、LLaMA、Claude）：合并最频繁字符对
> - **WordPiece**（BERT）：用似然度合并
> - **SentencePiece**（T5）：无语言依赖
>
> **Token 的重要性**：
> 1. **上下文窗口限制**：输入 + 输出 ≤ 模型窗口（如 GPT-4 是 128k token）
> 2. **计费**：按 token 计费，1 中文字 ≈ 1-2 token，1 英文词 ≈ 1-1.5 token
> 3. **生成速度**：自回归模型串行生成，~50-100 token/秒
>
> **优化技巧**：
> - 输入端：RAG 检索关键片段、压缩对话历史
> - 输出端：明确长度要求
> - 缓存：Prompt Cache、KV Cache
>
> **工具**：`tiktoken` 库可精确计算 token 数。"

---

## 八、交叉引用

- 主模块：[`11.ai`](../../11.ai/) — AI 知识体系
- 相关：[`13.split-hairs/11.ai/transformer/`](../transformer/) — Transformer 架构
- 相关：[`13.split-hairs/11.ai/rag/`](../rag/) — RAG（减少 token 使用）

## 相关章节

- 深度阅读：[`11.ai`](../../11.ai/README.md) — 主模块详细内容
