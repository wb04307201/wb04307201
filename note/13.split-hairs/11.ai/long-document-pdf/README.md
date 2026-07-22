<!--
question:
  id: 11.ai-long-document-pdf
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: RAG 工程
  tags: [11.ai, Long Document, PDF, Contract, Chunking, Lost-in-Middle, YaRN, LongRoPE, Docling, LongLLMLingua]
-->

# 长文档与 PDF 面试深挖（4 大核心）

> ⬅️ [返回 AI 咬文嚼字](../README.md) | [主模块深度专题](../../../11.ai/02-technology-stack/long-document-processing/README.md)

> **一句话定位**：**4 大核心长文档/PDF 面试深挖**：分块策略 / 中间丢失 / 上下文扩展 / 长合同实战。

---

## 🎯 4 大核心题

### Q1：长合同 PDF 应该用什么分块策略？为什么固定窗口不行？

**陷阱**：
- ❌ 默认 RecursiveCharacterTextSplitter（合同有结构化条款，固定切分会切碎条款）
- ❌ 不知道 5 大 chunking 策略权衡

**30 秒话术**：
> "5 大分块策略：**固定 / 递归 / 语义（embedding 相似度）/ 滑动窗口 / Agentic（语义感知）**。**合同场景首选「按条款级分块 + 保留条款编号 metadata」**（正则：`第[一二三四五六七八九十]+条`）。"

**90 秒话术**：
> "**Recursive 不能用**：合同条款层级强（甲方/乙方/责任/义务），按 `\n\n` 切可能把跨条款的责任整段打散。**5 大策略权衡**：
>
> - 固定窗口（512 token）：简单但破坏条款边界 → 不用
> - 递归切分（RecursiveCharacterTextSplitter）：按 `\n\n \n . ` 层级，但对合同格式不友好 → 凑合
> - 语义分块：保留语义完整，但慢 → 推荐
> - 滑动窗口（overlap 20%）：保留 context 但 chunk 边界不准 → 备选
> - Agentic 分块（LLM 自主判断边界）：最准但贵 100x → 关键条款
>
> **合同场景最佳实践**：① Docling 提取层级结构 ② 按条款切分（保留编号）③ 每 chunk 附加 metadata（page/header/clause_id）便于溯源 ④ 嵌套 chunk（条款内段落二级切分）满足不同检索粒度。"

#### 5 大策略对比速记

| 策略 | 优势 | 劣势 | 合同适配度 |
|------|------|------|-----------|
| 固定窗口 | 实现简单 / 速度最快 | 破坏条款边界 | 不推荐 |
| 递归切分 | 多级分隔符回退 | 不识别条款编号 | 凑合 |
| 语义分块 | 语义完整 | 慢（embedding 全量调用） | 推荐 |
| 滑动窗口 | overlap 保留上下文 | chunk 边界不准 | 备选 |
| Agentic 分块 | 边界最准 | 成本 +100x | 关键条款专用 |

#### 合同场景分块四件套

1. **结构化抽取**：Docling 解析 PDF 保留目录层级、表格、页码。
2. **条款级切分**：按 `第X条` 正则切分，保留条款编号到 metadata。
3. **metadata 富化**：每个 chunk 至少含 `page` / `header` / `clause_id` 三个字段。
4. **嵌套粒度**：条款一级 + 段落二级，两套索引分别应对检索与精读。

---

### Q2：Lost-in-Middle 怎么解？为什么 Qwen/Llama 都有这问题？

**陷阱**：
- ❌ 把超长 context 当银弹（实际中间位置准确率暴跌 30%+）
- ❌ 不知道缓解方案

**30 秒话术**：
> "Lost-in-Middle = 模型对 prompt 头尾关注强，中间位置准确率暴跌 30-50%。Liu et al. 2023 论文原话。**6 大缓解**：① 把关键信息放头尾 ② 重新排序 chunk ③ Rerank ④ Map-Reduce ⑤ Context Compression ⑥ Hierarchical Summarization。"

**90 秒话术**：
> "**为什么有这问题**：Self-attention 的位置权重非均匀（U 型），头尾获得更多注意力。**2023 Liu et al.** 论文：把 20 个关键事实放到 80K context 中部，GPT-3.5/Claude-1 仅 recall 40% 左右。Gemini 1.5 1M / Claude 200K 也无法幸免——只是边界更宽。
>
> **6 大缓解**：
>
> 1. 位置策略：关键信息塞头/尾位置
> 2. 重排序：最相关 3-5 个 chunk 排最前/最后
> 3. Map-Reduce：先每 chunk 单独汇总
> 4. Context Compression：LongLLMLingua 压到 1/10
> 5. Rerank + Top-K 召回：不超过 10 个 chunk
> 6. Hierarchical Summarization：先章节摘要再全文摘要
>
> **实战**：RAG Pipeline Stage 4 = Context Compression（如 LongLLMLingua 把 2000 token 压到 500 token）。"

#### Lost-in-Middle 测试方法

- **Needle-in-a-Haystack**：把关键句子藏在 context 不同位置，看召回率。
- **Multi-Needle**：同时插入多个事实点，测试全局关联能力。
- **Passkey Retrieval**：固定 passkey 字符串藏在长上下文中。
- **指标位置**：头 0-15% / 尾 85-100% 准确率高；中间 30-70% 暴跌。

#### 工程实战 6 招落地

1. **位置策略**：合同答案相关条款放在 system prompt 末尾、query 之后。
2. **重排序**：Cross-Encoder 把最相关 Top-3 推到最前/末尾。
3. **Map-Reduce**：每个 chunk 先生成"是否相关 + 引用"再合并。
4. **压缩**：LongLLMLingua / RECOMP 2000→500 token。
5. **Rerank + Top-K**：Cross-Encoder + 限定 Top-K ≤ 10。
6. **层级摘要**：先章节级摘要（512 token / 章）再全文摘要。

---

### Q3：上下文窗口扩展到 1M 怎么办？YaRN/LongRoPE 区别？

**陷阱**：
- ❌ 只答"PI 缩放"
- ❌ 不区分 4 大方案

**30 秒话术**：
> "4 大扩展方案：**PI（位置插值）/ NTK-aware（频率基数）/ YaRN（NTK + 注意力缩放）/ LongRoPE（动态搜索）**。2026 SOTA：Qwen3.5 / Llama-3.1-1M 已原生支持 1M context。"

**90 秒话术**：
> "**为什么需要扩展**：RoPE 训练在 32K-128K，推理想用 200K 会 PPL 爆炸。
>
> **4 大方案对比**：
>
> - PI（Meta 2023）：所有位置除以 scale（8× 缩放）→ 简单但高频丢失
> - NTK-aware（Reddit 2023）：只调整频率基数 → 改进高频但低频差
> - YaRN（Nous Research 2023）：NTK + 注意力缩放 + 长度缩放 → **SOTA**
> - LongRoPE（Microsoft 2024）：动态搜索每个维度缩放因子 → 2K 训练推 2M
>
> **2024-2026 实战**：
>
> - **Qwen3.5-397B-A17B**（Gated Delta 混合架构）原生 1M context + 2 小时视频理解
> - **Llama-3.1-8B-Instruct-1M**（YaRN 后训练）
> - **Gemini-1.5-Pro** 原生 10M context
>
> **工程选型**：① 已有 Qwen/Llama → YaRN/LongRoPE 后训练 ② 新项目 → 直接选 1M 模型 ③ 注意 needle-in-a-haystack test。"

#### 4 大方案对比表

| 方案 | 提出方 / 年份 | 核心机制 | 训练成本 | 效果 |
|------|---------------|----------|----------|------|
| PI | Meta 2023 | 位置除以 scale | 低 | 高频丢失 |
| NTK-aware | Reddit 2023 | 频率基数调整 | 低 | 低频差 |
| YaRN | Nous Research 2023 | NTK + 注意力缩放 + 长度缩放 | 中 | **SOTA** |
| LongRoPE | Microsoft 2024 | 动态搜索每维度缩放因子 | 中 | 2K→2M |

#### 工程选型决策树

```text
已有 Qwen/Llama 7B-70B？
  ├─ 是 → YaRN 后训练（性价比高）
  └─ 否 → 新项目？
      ├─ 是 → 直接选 1M 模型（Qwen3.5 / Llama-3.1-1M / Gemini-1.5）
      └─ 否 → 微调 RoPE + LongLLMLingua 压缩
```

**验证手段**：needle-in-a-haystack + multi-needle + passkey retrieval 三件套。

---

### Q4：长合同实战 100 页 PDF，5 步 Pipeline？

**陷阱**：
- ❌ 只答"读 PDF 然后 RAG"
- ❌ 不知道完整 5 步

**30 秒话术**：
> "**5 步实战**：**① Docling PDF → 结构化 JSON ② 条款级分块 + metadata ③ Embedding + BM25 双路召回 ④ Cross-Encoder Rerank Top-10 ⑤ LongLLMLingua 压缩 + LLM + 引用溯源**。"

**90 秒话术**：
> "**实战代码骨架**（Python）：
>
> ```python
> # 1. PDF 解析（保留层级 + 表格）
> from docling.document_converter import DocumentConverter
> converter = DocumentConverter()
> result = converter.convert('contract.pdf')
> md = result.document.export_to_markdown()
>
> # 2. 按条款分块（保留条款编号 + 页码）
> import re
> chunks = []
> for page_idx, page_text in enumerate(split_by_page(md)):
>     clauses = re.split(r'(第[一二三四五六七八九十]+条)', page_text)
>     for i in range(1, len(clauses), 2):
>         chunks.append({
>             'text': clauses[i] + clauses[i+1],
>             'metadata': {'page': page_idx+1, 'clause': clauses[i].strip()}
>         })
>
> # 3. 双路召回（向量 + BM25）
> vector_results = vector_store.similarity_search(query, k=20)
> bm25_results = bm25_index.search(query, k=20)
> combined = reciprocal_rank_fusion(vector_results, bm25_results)[:30]
>
> # 4. Rerank 精排
> from sentence_transformers import CrossEncoder
> reranker = CrossEncoder('BAAI/bge-reranker-large')
> reranked = reranker.rank(query, [r['text'] for r in combined])[:10]
>
> # 5. 压缩后送 LLM
> from llmlingua import PromptCompressor
> compressor = PromptCompressor()
> compressed = compressor.compress_prompt(
>     '\n'.join([r['text'] for r in reranked]),
>     target_token=2000
> )
> answer = llm.invoke(f'合同：{compressed['compressed_prompt']}\n问题：{query}\n要求：引用条款编号 + 页码')
> ```
>
> **关键工程细节**：① **Page metadata 必带**（合同审查法律要求溯源）② **条款编号写入 chunk**（检索关键词）③ **压缩率控制在 70%** ④ **输出引用规则**：必须返回条款编号 + 页码。"

#### 5 步 Pipeline 速记表

| 步骤 | 工具 / 库 | 关键参数 | 输出 |
|------|-----------|----------|------|
| 1. PDF 解析 | Docling | 保留表格 + 层级 | Markdown / JSON |
| 2. 条款分块 | regex `第X条` | chunk 500-1000 token | list[chunk+metadata] |
| 3. 双路召回 | BGE + BM25 | k=20 + RRF 融合 | Top-30 |
| 4. Rerank | bge-reranker-large | Top-10 | Top-10 chunks |
| 5. 压缩 + LLM | LongLLMLingua | target=2000 token | answer + citations |

#### 4 大工程细节红线

1. **Page metadata 必带**：合同审查法律要求溯源，否则审查报告无效。
2. **条款编号写入 chunk**：作为检索关键词命中率高 3x。
3. **压缩率控制在 70%**：2000→500 token，剩余 500 token 留给 prompt + answer。
4. **输出引用规则**：LLM 输出必须含 `第X条` + `第N页` 双引用。

---

## 🔗 兄弟章节

- **主模块深度**：[长文档处理（几百页 PDF 合同）](../../../11.ai/02-technology-stack/long-document-processing/README.md) — 4 大策略整合 + 实战选型决策树
- **兄弟面试题**：[LLM 对齐面试深挖](../llm-alignment/README.md) — 训练阶段如何影响长文档能力
- **兄弟面试题**：[Prompt Injection 面试深挖](../prompt-injection/README.md) — 长合同场景下 RAG 的间接注入风险
- **兄弟面试题**：[RAG 面试深挖](../rag/README.md) — RAG Pipeline 通用模板
- **兄弟面试题**：[长上下文 Agent 策略](../long-context-agent-strategy/README.md) — Agent 视角的长上下文利用
- **餐厅叙事**：[12.story 36 — RAG 检索增强生成](../../../12.story/36-rag-retrieval-augmented-generation.md) — 用阿明餐厅串起 RAG 全流程

---

## 📊 4 题难度速查表

| 题 | 难度 | 频率 | 关键数字 |
|---|------|------|---------|
| Q1 分块策略 | ⭐⭐⭐⭐ | 高频 | 5 大策略 / 4 件套 / 条款级 metadata |
| Q2 Lost-in-Middle | ⭐⭐⭐⭐⭐ | 高频 | 中部准确率 -30~50% / 6 大缓解 |
| Q3 上下文扩展 | ⭐⭐⭐⭐ | 中频 | 4 大方案 / 1M context / YaRN SOTA |
| Q4 长合同 5 步 | ⭐⭐⭐⭐⭐ | 高频 | Docling + 双路召回 + Rerank + 压缩 + 引用 |

---

## 📚 参考来源

1. [CSDN — 从 8K 到 1M 上下文的通用化：Qwen-Agent 创新实践](https://blog.csdn.net/) — Qwen 长上下文演进路线与 1M context 工程实践
2. [CSDN — llama 模型 long context 源码分析（DeepSeek 前线）](https://blog.csdn.net/) — Llama LongRoPE / YaRN 源码与训练细节
3. [NeedleInAHaystack GitHub](https://github.com/gkamradt/LLMTest_NeedleInAHaystack) — 长上下文 Lost-in-Middle 测试基准
4. [IBM Docling GitHub](https://github.com/DS4SD/docling) — PDF 文档结构化解析开源库
5. [LongLLMLingua / RECOMP 论文（Microsoft 2023）](https://arxiv.org/abs/2310.04836) — Prompt 压缩 20x / RAG 检索压缩代表方法

← 返回 [AI 咬文嚼字](../README.md)