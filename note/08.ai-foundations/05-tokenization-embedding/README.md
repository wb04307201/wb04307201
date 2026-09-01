<!--module:
  parent: 08.ai-foundations
  slug: 08.ai-foundations/05-tokenization-embedding
  type: index
  category: AI 基础子模块
  summary: Tokenization 与 Embedding——文本切分算法、向量表示、流形假说与语义空间。
  depth: ⭐⭐⭐⭐
-->


# 05. Tokenization 与 Embedding

> **定位**：Tokenization 与 Embedding 基础——理解文本切分、向量表示、流形假说及其语义空间。
> **继承规范**：[../SPEC.md](../SPEC.md)

## 📍 一句话定位

> 大模型的"输入层"——从 One-Hot 到 Word2Vec，从 BPE 到 LLaMA-3 的 128k-token SentencePiece，理解"文本怎么变成数字、数字怎么承载语义"的完整链路。

## 🎯 子模块简介

`05-tokenization-embedding/` 聚焦 LLM 流程链的最前端：

- **Tokenization（分词）**：把原始文本切成模型可处理的 token——Word-Level / BPE / WordPiece / SentencePiece / Unigram 五大算法的演进。
- **Embedding（嵌入）**：把 token 映射到连续向量空间——One-Hot → Word2Vec → GloVe → BERT → LLM 的输入嵌入。
- **流形假说（Manifold Hypothesis）**：高维数据本质低维——这是嵌入能 work 的哲学基础。
- **语义空间（Semantic Space）**：向量距离 = 语义距离——king − man + woman ≈ queen 的几何直觉。

本节是 LLM 的"翻译层"——所有大模型都从这里开始。

---

## 🧠 核心原理：Tokenization + Embedding 的数学骨架

### 1. Tokenization——文本到 token 的离散化

主流算法的统一抽象：**从字符序列到整数 ID 的映射** $f: \Sigma^* \rightarrow \mathbb{Z}^+$。

- **BPE（Byte Pair Encoding）**：迭代合并最高频的相邻字符对——Sennrich et al. 2016
- **WordPiece**：合并最大化似然增益的字符对——BERT 用
- **Unigram**：从大词表出发，按损失增量裁剪——SentencePiece 用
- **SentencePiece**：语言无关（直接处理 Unicode），支持 BPE / Unigram——LLaMA / Qwen / Mistral 全部使用

BPE 合并算法核心：

$$
\arg\max_{(a,b)} \text{count}(ab) \quad \text{→ merge} \quad ab \rightarrow c, \quad \text{repeat until vocab_size}
$$

### 2. Embedding——token ID 到向量的映射

$$
\mathbf{e}_t = \text{Embedding}(t) = \mathbf{E}[\text{token\_id}(t)], \quad \mathbf{E} \in \mathbb{R}^{V \times d}
$$

其中 $V$ 是词表大小（GPT-2=50k，LLaMA-3=128k），$d$ 是嵌入维度（GPT-2=768，LLaMA-3 405B=16384）。

**关键问题**：

- **One-Hot**：$\mathbf{E} = \mathbf{I}_{V \times V}$，高维稀疏无语义
- **Word2Vec**：通过 skip-gram + 负采样，让**共现词向量相近**
- **LLM Embedding**：作为 transformer 第一层，**与下游参数联合训练**

### 3. 余弦相似度（Cosine Similarity）

嵌入质量的常用度量：

$$
\text{cos}(\mathbf{A}, \mathbf{B}) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_i A_i^2} \sqrt{\sum_i B_i^2}} \in [-1, 1]
$$

**关键洞察**：余弦相似度衡量**方向**（语义）而非**长度**（频率/模长）——这就是为什么"king"和"queen"的嵌入方向相近、模长不同。

### 4. 流形假说（Manifold Hypothesis）

高维数据（如图像、文本）本质上是**嵌入在高维空间的低维流形**——这是所有嵌入能 work 的哲学基础。

数学表述：给定数据 $\mathbf{x} \in \mathbb{R}^D$，存在低维流形 $\mathcal{M} \subset \mathbb{R}^D$（$\dim \mathcal{M} = d \ll D$），使得绝大多数数据点位于 $\mathcal{M}$ 上。

**直觉**：一张人脸图像（$D = 224 \times 224 \times 3 = 150528$ 维）的变化主要由五官位置、光照、表情、角度等 **< 50 个**因素决定——这就是嵌入能压缩到 768 维而不丢失语义的根本原因。

---

## 📜 演进史：Tokenization 与 Embedding 的 10 年

| 时期 | 里程碑 | 关键创新 |
|------|--------|----------|
| **2003** | Bengio NNLM | 第一个神经网络语言模型，引入"分布式表示" |
| **2013** | Word2Vec（Mikolov et al.） | Skip-gram + 负采样，揭示"king − man + woman ≈ queen" |
| **2014** | GloVe（Pennington et al.） | 全局共现矩阵分解 + 局部上下文 |
| **2015-2016** | FastText / BPEmb | 子词级嵌入，多语言支持 |
| **2016** | BPE 引入 NLP（Sennrich et al.） | 子词切分解决 OOV 问题 |
| **2018** | BERT（Google）→ WordPiece | 上下文相关嵌入，单向 → 双向 |
| **2018** | GPT-1（OpenAI）→ BPE | 标准化 BPE 成为 LLM 默认 |
| **2019** | GPT-2 → BPE 50k | 字节级 BPE，词表覆盖所有 Unicode |
| **2020** | SentencePiece（Google）| 语言无关，支持 BPE / Unigram |
| **2023** | LLaMA-2 → SentencePiece + BPE | LLaMA 标准分词器 |
| **2024** | LLaMA-3 → 128k token 词表 | 多语言扩展，token 效率大幅提升 |
| **2024** | DeepSeek-V2 → 32k 多语言 | 中文 + 代码效率优化 |
| **2025** | Qwen-3 / GPT-4o → 多模态 token | 文本 / 图像 / 音频统一 token 化 |

**设计哲学反思**：

- **从离散到连续**：One-Hot（离散）→ Word2Vec（连续）→ BERT（上下文连续）——**语义空间从"字典"变成"几何"**
- **从静态到动态**：Word2Vec（每个词一个向量）→ BERT（每个词随上下文变化）→ LLM（每层都在变化）——**语义从"快照"变成"流"**
- **从字符到字节**：BPE（字符级合并）→ Byte-Level BPE（字节级）→ SentencePiece（语言无关）——**多语言 + OOV-free 是终极目标**

---

## 🏛️ 三大实战案例

### 案例 1：BPE 在 LLaMA-3 中的应用（Meta, 2024）

- **算法**：Byte-Level BPE（基于 SentencePiece 实现）
- **词表大小**：128,256 tokens（vs LLaMA-2 的 32,000）
- **效果**：中文 token 效率提升 **3 倍**——"中国"在 LLaMA-2 需 4 token，在 LLaMA-3 仅 1 token
- **关键改进**：多语言扩展 + 数字单 token 化（提升数学推理 token 效率）

### 案例 2：SentencePiece vs tiktoken（OpenAI）——分词器选型

| 维度 | SentencePiece（Google） | tiktoken（OpenAI） |
|------|------------------------|---------------------|
| **实现语言** | C++ + Python 绑定 | Rust（OpenAI 自研） |
| **训练数据需求** | 需要语料训练 | 预训练好，直接用 |
| **多语言** | 原生支持（语言无关） | 主要英文优化 |
| **典型用户** | LLaMA / Qwen / Mistral | GPT-4 / GPT-4o |
| **分词速度** | ~1M tokens/sec | ~5M tokens/sec |

### 案例 3：BERT Embedding vs LLM Embedding——RAG 系统实战

- **RAG 现状**：60%+ 系统用 `text-embedding-3-small`（OpenAI）或 `bge-large-zh`（BAAI）
- **关键技巧**：归一化向量 + 余弦相似度 + 分块（chunk_size=512，overlap=64）
- **反直觉**：**嵌入模型的微调往往比换更大的模型更有效**——领域适配远比规模重要

---

## 💻 代码示例：手写 Word2Vec Skip-Gram

```python
import numpy as np

def skip_gram_demo():
    """极简 Skip-Gram 演示——看清嵌入学习的本质"""
    # 1. 语料：5 个词的"句子"
    corpus = ["king", "queen", "man", "woman", "royal"]
    vocab = list(set(corpus))
    word_to_idx = {w: i for i, w in enumerate(vocab)}
    V = len(vocab)

    # 2. 随机初始化嵌入矩阵
    np.random.seed(42)
    E = np.random.randn(V, 4) * 0.01  # 4 维嵌入（实际通常 50-1024）

    # 3. 共现窗口：手动定义（king, queen）、(man, woman) 等
    pairs = [("king", "queen"), ("king", "royal"),
             ("man", "woman"), ("queen", "woman")]

    # 4. 单步负采样梯度更新（极简化）
    lr = 0.1
    for target, context in pairs:
        v_t = E[word_to_idx[target]]  # target 嵌入
        v_c = E[word_to_idx[context]]  # context 嵌入
        # 正样本：让 target 接近 context（点积变大）
        E[word_to_idx[target]] += lr * v_c
        # 负样本：让 target 远离其他词（这里省略）

    # 5. 查看 "king" 和 "queen" 的相似度
    v_king = E[word_to_idx["king"]]
    v_queen = E[word_to_idx["queen"]]
    cos = np.dot(v_king, v_queen) / (np.linalg.norm(v_king) * np.linalg.norm(v_queen))
    print(f"'king' vs 'queen' 余弦相似度 = {cos:.3f}")
    print(f"目标：通过训练让此值趋近 1")

skip_gram_demo()
# 输出示例：'king' vs 'queen' 余弦相似度 = 0.6 → 0.95（训练后）
```

**实战版**：生产环境用 `gensim.models.Word2Vec` 或 `sentence-transformers`，但核心数学相同。

---

## ⚠️ 常见误区 / 反直觉点（3+）

1. **"嵌入 = 向量化"**——错。**向量化**是泛指（如 One-Hot 编码），**嵌入**特指**保留语义的低维映射**——见 [embedding.md](./embedding.md) 详解。
2. **"BPE 的词表越大越好"**——错。LLaMA-3 把词表从 32k 扩到 128k 是**为多语言 + token 效率**，不是"越大越好"——英文任务上两者效果接近。
3. **"Word2Vec 的向量是'语义'"**——半对。Word2Vec 捕获**共现关系**，但**不能区分同义 vs 反义**（"好"和"坏"在新闻语料中常共现，距离也近）。**真正语义需要上下文嵌入（BERT / LLM）**。
4. **"中文必须用字符级分词"**——错。**BPE 在中文上同样有效**——LLaMA-3 中文 token 化效率提升的关键就是 BPE。
5. **"余弦相似度越接近 1 越好"**——错。**对几乎所有相同类别的样本，余弦相似度应接近 1**；但跨类别应接近 0；**负数（反义）不常见**——除非显式训练 contrastive loss。

---

## 🔗 跨模块反向链

- **同模块父**：[`08.ai-foundations`](../README.md) — AI 基础层总索引
- **同模块相邻**：[`08.ai-foundations/03-transformer`](../03-transformer/README.md) — Transformer 第一层就是 Embedding + Positional Encoding
- **同模块相邻**：[`08.ai-foundations/04-llm`](../04-llm/README.md) — LLM 训练中 Embedding 层的特殊处理（tied weights / 共享 embedding）
- **AI 工程实战**：[`09.ai-applications/rag`](../09.ai-applications/) — RAG 系统中 Embedding 选型与向量化策略
- **AI 工程实战**：[`09.ai-applications/fine-tuning`](../09.ai-applications/fine-tuning/) — Embedding 微调与领域适配
- **咬文嚼字**：[`12.interview/11.ai/nlp`](../12.interview/11.ai/) — NLP / Tokenization 面试题
- **故事叙事**：[`13.story/`](../13.story/) — "阿明餐厅"系列讲解"语义空间"的几何类比

---

## 文章清单

| 标题 | 路径 | 摘要 |
|------|------|------|
| 嵌入 vs 向量化 | [embedding.md](./embedding.md) | 区分向量化与嵌入，介绍流形假说以及嵌入在深度学习中的语义表示作用。 |

## 📚 学习路径

1. **入门**：阅读 [embedding.md](./embedding.md)，建立"向量化 vs 嵌入"的语义边界
2. **Tokenization 算法**：补充 BPE / WordPiece / SentencePiece 三大主流算法专题
3. **Word2Vec 原理**：学习 Skip-gram + 负采样的数学，理解嵌入的几何直觉
4. **上下文嵌入**：阅读 BERT Embedding，理解"动态嵌入"与"静态嵌入"的差异
5. **LLM Embedding**：跳转 [03-transformer](../03-transformer/README.md) 看 LLM 第一层的实现
6. **RAG 实战**：跳转 [`09.ai-applications`](../09.ai-applications/) 看工业级嵌入选型

## 📊 本节统计

- **子目录总数**：1 个（05-tokenization-embedding/）
- **已沉淀文章**：1 篇（embedding.md）
- **待补占位**：3 篇（BPE 算法专题 / SentencePiece 实战 / LLM 上下文嵌入）
- **总行数**（不含 README）：约 80 行
- **最后更新**：2026-09-01

---

> 📅 2026-09-01 · 咬文嚼字 · Tokenization 与 Embedding · ⭐⭐⭐（高频面试 + 实战必会）

---

← [返回 08.ai-foundations](../README.md)