<!--
question:
  id: 11.ai-transformer
  topic: 11.ai
  difficulty: ⭐⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [11.ai, Transformer, transformer]
-->

# Transformer 架构 — Self-Attention 面试深挖

> 一句话定位：Transformer 是 2017 年 Google "Attention is All You Need" 提出的架构，核心创新是 Self-Attention。完整概念见 [主模块 Transformer](../../../08.ai-foundations/03-transformer/README.md)。

---

## 引子：Google 为什么在 2017 年放弃 RNN？

2017 年前，做机器翻译只能用 RNN/LSTM。问题很要命：

- **训练慢**：必须串行处理，"100 个词的句子"比"10 个词"慢 10 倍
- **长句子崩**：第三个词的相关性到第 50 个词已经"忘光了"
- **并行不了**：100 个 GPU 跟 1 个 GPU 效果一样，钱白花

Google 的团队受不了了。他们投一个完全不同的方向——
**完全抛弃 RNN，让模型自己用注意力找相关性**。
这就是"Attention is All You Need"论文的诞生时刻，也是 Transformer 一统江湖的起点。
今天，**所有 GPT / BERT / Claude / LLaMA 都是 Transformer 的徒子徒孙**。

## 一、核心公式（一行记全）

```text
Attention(Q, K, V) = softmax(Q × K^T / √d) × V
```

- **Q（Query）**：我要找什么
- **K（Key）**：我有什么
- **V（Value）**：实际内容
- **√d**：缩放因子（防止点积过大）

---

## 二、面试陷阱

### 陷阱 1：以为 Self-Attention 就是"加权平均"
- **真相**：Self-Attention 通过 Q×K 计算相似度得到权重，再用权重对 V 加权 —— 不是简单的平均，是"动态查询"。

### 陷阱 2：以为多头是"切分维度"
- **真相**：多头是多个独立注意力头并行，每个头学习**不同的语义关系**（头 1 学主谓关系、头 2 学指代消解...），最后拼接。

### 陷阱 3：以为 Transformer 自带顺序
- **真相**：Transformer **并行计算无顺序**，必须显式注入 **Positional Encoding**（sin/cos），否则"我吃苹果"和"苹果吃我"无法区分。

### 陷阱 4：以为 √d 可省略
- **真相**：√d 是关键缩放因子 —— 不除以 √d，Q×K^T 值过大导致 softmax 梯度消失。

---

## 三、反直觉点

- **Transformer 没有"循环"**：RNN 的循环结构被 Self-Attention 完全替代，训练可全并行，速度快 N 倍。
- **Encoder / Decoder 是组合关系**：BERT（仅 Encoder）/ GPT（仅 Decoder）/ T5（Encoder+Decoder），现代 LLM 主流是 Decoder-only。
- **Multi-Head 的"头数"是超参**：典型 8-16 头，头数 × 头维度 = 模型维度。

---

## 四、2024 推理工程演进（KV Cache / 共享 K·V / Flash Attention）

> 这一节是 2024 年面试的**差异化加分项**。很多候选人能背 Attention 公式，但答不上"为什么 LLaMA-2 推理 100k 上下文不 OOM"——本质就是 KV Cache + GQA + Flash Attention 的工程组合拳。

### §1 KV Cache：推理显存省 10x 的关键

**问题**：自回归生成（auto-regressive decoding）每生成 1 个新 token，都要重新计算**所有历史 token** 的 K 和 V 矩阵。
- 复杂度：O(n²) 显存 + 算力（n = 已生成序列长度）
- 100k 上下文每生成 1 个 token 要算 100k 次 K/V —— 完全浪费

**方案**：**缓存历史 token 的 K/V 矩阵，每步只算当前新 token 的 Q**。
- 第一次 forward：`past_kv = None`
- 后续 forward：把新算出的 K/V 拼接到 `past_kv`，只需算新 token 的 Q

**显存公式**（单层）：

```text
KV Cache 显存 = 2 × n_layers × n_kv_heads × head_dim × seq_len × bytes_per_elem
              （K + V）  （层数）   （KV 头数）  （头维度）  （序列长度）
```

**典型规模**（FP16，bytes_per_elem = 2）：
- 7B 模型（32 层 × 8 KV 头 × 128 dim）推理 100k 上下文 ≈ **30 GB** KV Cache
  - 远超模型权重 14 GB —— **显存瓶颈在 KV Cache，不在权重**
- 13B 模型（40 层 × 8 KV 头 × 128 dim）推理 100k 上下文 ≈ **60 GB** KV Cache

**Trade-off**：
- ✅ 省 O(n²) 算力（每步只算 1 个 token 的 Q，不再重算历史）
- ❌ 长上下文显存爆炸 —— 100k+ 上下文成 OOM，必须配合下面的 GQA / PagedAttention

**PyTorch 伪代码**（15 行）：

```python
# 推理循环：每次只算当前 token 的 Q，复用历史 K/V
past_kv = None
for token in new_tokens:
    q = current_token @ W_q           # 只算当前 token 的 Query
    k_new = current_token @ W_k       # 当前 token 的新 K
    v_new = current_token @ W_v       # 当前 token 的新 V
    if past_kv is None:
        past_kv = (k_new, v_new)
    else:
        past_kv = (torch.cat([past_kv[0], k_new], dim=seq_dim),
                   torch.cat([past_kv[1], v_new], dim=seq_dim))
    attn = softmax(q @ past_kv[0].T / sqrt(d_k)) @ past_kv[1]
    output = attn @ W_o
```

面试话术：*"KV Cache 用 O(n) 显存换 O(1) 的每步算力 —— 是 LLM 推理从'跑不动'到'跑起来'的第一个工程突破。"*

---

### §2 MQA / GQA / MLA：共享 K/V 的演进

核心思路：**多个 Q 头共享一组 K/V 头**，减少 KV Cache 头数 → 直接砍显存。

| 方案 | KV 头数 | 显存节省 | 代表模型 | 性能影响 |
|------|---------|---------|---------|---------|
| **MHA**（Multi-Head Attention）原始 | `n_heads` | 1x（baseline）| BERT / 原始 Transformer | 基准 |
| **MQA**（Multi-Query Attention）| **1** 个共享 KV 头 | **n_heads 倍**（8x）| Falcon / PaLM | 轻微质量下降（生成略不稳） |
| **GQA**（Grouped-Query Attention）| `n_heads / group_size` | **group_size 倍**（常用 8x）| **LLaMA-2 70B / Mistral / Qwen** | 几乎无质量下降，**2023-2024 主流折中** |
| **MLA**（Multi-Latent Attention）| 隐空间压缩（低秩联合压缩 KV）| **5-10x**（甚至更多）| **DeepSeek-V2 / V3** | **质量反超 MHA**（解耦 RoPE）|

**关键洞察**：

1. **GQA 是 2023-2024 LLM 主流折中**：`group_size = n_heads / n_kv_heads`，常见 `group_size = 8`（即 64 头 Q 共享 8 头 KV）。
   LLaMA-2 70B：64 Q 头 / 8 KV 头 → KV Cache 缩到 1/8。

2. **MLA 是 2024 年新突破**（DeepSeek-V2 论文）：把 K、V **联合压缩到一个低秩隐向量**，推理时再向上投影恢复。
   - 优势：KV Cache 比 GQA 还小 5-10x，且**质量不降反升**（因为解耦了 RoPE）
   - HuggingFace config 里关键参数：`num_key_value_heads`（KV 头数，注意**不是** `num_attention_heads`！）

3. **面试常考点**：`num_key_value_heads = num_attention_heads` → 这是 MHA；`num_key_value_heads = 1` → MQA；其他 → GQA。
   看 HuggingFace config JSON 一眼就能判断模型用哪种注意力。

---

### §3 Flash Attention / PagedAttention：算子级 + 系统级优化

**Flash Attention（Dao-AILab，2022 首发）**：

- **问题**：标准 Attention 显存 O(n²)（要存 n×n 的 attention matrix），长上下文直接 OOM。
- **方案**：**分块计算（tiling）+ 重计算（recomputation）** —— 不存 attention matrix，靠 GPU SRAM 分块流式算完。
  - IO 复杂度仍 O(n²)（算量没省），但**显存 O(n)**
- **版本演进**：
  - Flash Attention 1（2022）：解决显存 O(n²) → O(n)
  - Flash Attention 2（2023）：2-4x 加速（更好的并行 + 减少非 matmul FLOPs）
  - Flash Attention 3（2024）：**Hopper GPU 专用**（H100 的 WGMMA + TMA 指令），FP8 + 异步
- **面试话术**：*"Flash Attention 的核心是 IO-aware —— 不存 attention matrix，而是通过分块 + 重计算换 IO。算法复杂度没变，但 HBM 访问量降一个数量级。"*

**PagedAttention（vLLM，2023）**：

- **问题**：KV Cache 显存**碎片化**。不同请求长度差异极大（有的 100 token，有的 10k），传统连续分配浪费 **60-80%** 显存。
- **方案**：**借鉴操作系统虚拟内存分页** —— 把 KV Cache 切成 16 token 的 block，`block_table` 维护逻辑→物理映射。
- **收益**：vLLM 推理吞吐提升 **14-24x**（vs HuggingFace naive 实现）；论文 SOSP 2023 最佳论文。
- **面试话术**：*"PagedAttention 把 KV Cache 分页管理，消除碎片化 —— vLLM 的核心就是这个。今天生产环境推理引擎（vLLM / TGI / TensorRT-LLM）都用了类似思想。"*

**三者组合拳**（2024 主流推理栈）：
```text
GQA（省 KV 头数）× Flash Attention（省 attention 显存）× PagedAttention（省碎片）
→ 100k 上下文能在单卡 A100 上跑起来
```

---

- 兄弟：[KV Cache 显存优化详解](../llm-inference/README.md) / [PagedAttention 原理](../llm-inference/README.md)

---

## 五、面试速记表

| 架构 | 例子 | 任务类型 |
|------|------|---------|
| 仅 Encoder | BERT | 理解（分类、NER） |
| **仅 Decoder** | **GPT / LLaMA / Claude** | **生成（对话、写作）—— 2026 主流** |
| Encoder + Decoder | T5 / BART | 翻译、摘要 |

---

## 六、30 秒面试话术

> Transformer 是 2017 年 Google 提出的，核心创新是 Self-Attention 机制。
>
> Self-Attention 本质：每个 token 通过 Q（Query）、K（Key）、V（Value）三个矩阵，计算与其他 token 的相似度，得到加权特征。公式：`softmax(Q × K^T / √d) × V`。
>
> Multi-Head：多个注意力头并行，每个头学习不同的语义关系。
>
> Positional Encoding：用 sin/cos 注入位置信息（因为 Transformer 并行，无顺序）。
>
> 三种变体：仅 Encoder = BERT（理解任务）；仅 Decoder = GPT / LLaMA / Claude（生成任务，2026 主流）；Encoder + Decoder = T5（翻译、摘要）。
>
> Transformer 让 LLM 成为可能，是当前所有大模型的基石。

---

## 七、深度阅读

- 主模块：[Transformer 架构](../../../08.ai-foundations/03-transformer/README.md)
- 关联：[Token 与计费](../../../../note/11.ai/02-technology-stack/token-billing/README.md)
- 应用：[RAG](../../../09.ai-applications/rag/03-rag-vs-finetuning.md)
- **推理工程进阶**：[LLM 推理优化](../llm-inference/README.md)

---

> 📅 2026-08-10 · 增量更新 2024 推理工程 · 咬文嚼字 · AI 基础必问 · ⭐⭐⭐⭐⭐

← [返回: 咬文嚼字 · transformer](../README.md)
