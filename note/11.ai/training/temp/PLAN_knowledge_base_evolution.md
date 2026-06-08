# 知识库章节增补计划

> **For agentic workers:** 计划制定完成，等待用户审核后再开始执行。

**目标**：以 README6.md《RAG 不再是默认答案》为权威源，对 `lession1` 知识库章节进行轻量扩展（主体仍是 RAG，补充 5 种途径概览 + 对比表），并把 `lession16` 升级为"大模型知识接入技术全景"完整课程。

**范围**：两处文档的扩展与改写，不涉及代码改动，不破坏已有章节的连贯性。

---

## 现状摘要

### lession1
- **入口**：`lession1/README.md` → `lession1/README1.md`（"大模型基础能力与概念"）
- **知识库章节位置**：`lession1/README1.md` 第 164–216 行（约 53 行）
- **当前内容**：仅讲 RAG，含流程图、RAG 1.0/2.0/3.0 演进、启明 11 手机 demo、3 条"思考"
- **风格**：与 lession1 整体保持一致（实操型、含 demo 图、含思考题）

### lession16
- **入口**：`lession16/README.md` → `lession16/README1.md`
- **当前定位**：单一章节讲 Karpathy 的 LLM Wiki 模式
- **既有内容**：三层架构（Raw/Wiki/Schema）、三大操作（Ingest/Query/Lint）、工具链、Memex 渊源、社区案例
- **风格**：理论型、引用权威观点、含哲学思考

### 源文章 README6.md
- 提供 5 条技术路线：①长 Context + Caching ②生产级 RAG ③Agentic Retrieval ④SQL ⑤Deep Research
- 提供决策前置（2 个问题）、避坑指南（Eval + 数据质量）、决策清单
- 已有详细数据可引用（成本、错误率、对比矩阵）

---

## 增补目标

### lession1 目标（小改动）
- **保持**：RAG 仍是主体，启明 11 demo 与 3 条思考题全部保留
- **新增**：在原 RAG 章节末尾追加一节"📚 知识库的 5 种技术途径"（约 25–35 行）
  - 5 种途径一句话定位 + 适用场景
  - 一张紧凑对比表（数据规模 × 查询模糊度）
  - 一段引导：让读者知道"完整版在第 16 课"
- **不改**：前文 RAG 流程图、RAG 1.0/2.0/3.0 演进不调整
- **位置**：`lession1/README1.md` 知识库章节内，追加在原"### 思考"之前或之后（见 Task 1 的精确插入点）

### lession16 目标（大改动）
- **重新定位**：从单一 LLM Wiki 章节，升级为"**大模型知识接入技术全景**"完整课程
- **目录结构**（拟改为多章）：

| 章节 | 文件 | 主题 | 来源 |
|:----:|:----|:----|:----|
| 概览 | `README.md`（重写） | 课程定位、5 路径速查、章节导航 | 新写 |
| 第一章 | `README1.md`（保留） | LLM Wiki 模式（Karpathy） | 已有 |
| 第二章 | `README2.md`（新建） | 长 Context + Prompt Caching 甜蜜区 | README6 + 官方 |
| 第三章 | `README3.md`（新建） | 生产级 RAG：Hybrid + Rerank + Contextual | README6 + Anthropic 官方 |
| 第四章 | `README4.md`（新建） | Agentic Retrieval：从静态流水线到 Agent Loop | README6 |
| 第五章 | `README5.md`（新建） | 结构化数据走 SQL | README6 |
| 第六章 | `README6.md`（新建） | Deep Research 架构 | README6 |
| 第七章 | `README7.md`（新建） | 决策框架与最佳实践（Eval + 数据质量） | README6 + 实战经验 |
| 第八章 | `README8.md`（新建） | 综合示例：少府智库构建全过程 | 实战整合 |

- **每章统一结构**：
  1. 一句话定位
  2. 适用场景与不适用场景
  3. 核心原理（含 1 个 mermaid 流程图）
  4. 关键数据（成本、错误率、典型工作量）
  5. 陷阱与反模式
  6. 工具链推荐
  7. 思考题（1–3 题）
- **风格**：与现有 README1.md 保持一致（理论型、引用源、含代码示例与 mermaid 图）

---

## 详细任务分解

### Task 1：扩展 lession1/README1.md 知识库章节

**文件**：`lession1/README1.md`

**插入点**：在第 217 行（原章节最后一个"思考"结束后）追加新章节

**新增章节内容大纲**：

```markdown
---

## 📚 知识库的 5 种技术途径（2025 演进概览）

> 本节是 RAG 之外的"地图"——在 2025 年，RAG 已不是默认答案。  
> 完整 5 路径深度解析见 [第 16 课：LLM 驱动的个人知识库](../lession16/README.md)

### 一句话定位

1. **长 Context + Prompt Caching** — 几百份文档内最甜，0 工程
2. **生产级 RAG**（Hybrid + Rerank + Contextual）— 万级文档才上重型武器
3. **Agentic Retrieval** — 代码/多跳推理让 Agent 自己查
4. **结构化 SQL** — 业务数据别 dump 文档，让模型写 SQL
5. **Deep Research** — 复杂研究类问题，多轮检索综合成报告

### 决策矩阵：数据规模 × 查询模糊度

| | 小数据 (<200 份) | 大数据 (10K+ 份) |
|:--|:--|:--|
| **精确匹配** | 直接问 LLM / grep | Agent + SQL / grep |
| **语义模糊** | 长 Context + Caching | 重型 RAG (Hybrid + Rerank) |

### 为什么 RAG 不再是默认答案？

- 长 Context 让"塞 prompt"成为新甜蜜区（Claude 1M、Gemini 2M）
- 生产级 RAG 需 Hybrid + Rerank + Contextual 三件套，基础 RAG 上线即翻车
- Agent 路线在代码与多跳任务上效果碾压（42% → 89%）

> 📌 决策原则：**先问数据规模，再问查询模糊度，最后选方案。** 别再"先建向量库"。
```

**校验**：
- [ ] 保留原 RAG 章节（行 164–216）内容不变
- [ ] 新增章节行数 25–35 行
- [ ] 与已有 mermaid 风格保持一致
- [ ] 给出引导链接到 lession16

---

### Task 2：重写 lession16/README.md（课程总览）

**文件**：`lession16/README.md`（全量重写）

**新内容大纲**：

```markdown
# 第 16 课：大模型知识接入技术全景

> **5 条技术路线 × 决策框架 × 最佳实践** — 从"上 RAG"到"先想清楚再选工具"

## 学习目标
（4–5 条，理解 5 条路线、决策框架、LLM Wiki 模式、Eval 与数据质量）

## 前置条件
（lession1 知识库章节 / RAG 基础）

## 5 路径速查表
（一张紧凑的对比表，让读者一眼看到 5 条路线的定位）

## 章节导航
（8 个章节，标注时长）

## 核心架构图
（mermaid：5 路径挂在一张决策矩阵上）

## 补充资料
（README6.md、Anthropic 官方链接、社区项目）
```

---

### Task 3：新建 lession16/README2.md — 长 Context + Prompt Caching

**新建文件**：`lession16/README2.md`

**内容大纲**（与 README1 同样理论型风格）：

```markdown
# 长 Context + Prompt Caching：2025 的甜蜜区

## 一句话定位
几百份文档内的最优解；不建向量库，全塞 prompt，靠缓存省钱。

## 适用 vs 不适用
- ✅ < 200 份文档、知识相对稳定
- ❌ 文档经常更新（缓存失效成本高）
- ❌ 文档总量超过 200 万 token

## 核心原理
- 上下文窗口演进（Claude 1M / Gemini 2M / 实际换算）
- Prompt Caching 工作机制
  - 写入：25% 溢价
  - 读取：10% 基础价（-90%）
- mermaid 流程图

## 关键数据（来自 Anthropic 官方）
- 100K token 长文档问答：延迟 11.5s → 2.4s（-79%），成本 -90%
- 适用场景清单

## 陷阱：Lost in the Middle
- 长 context 不等于短 context 效果
- 关键信息放两头
- 控制在 200 份文档"甜蜜区"

## 工具链
- Claude / Gemini / OpenAI 各家缓存策略
- Claude 定价示例（带数据）

## 思考题
```

**参考来源**：
- https://www.anthropic.com/engineering/contextual-retrieval （"200,000 tokens ≈ 500 pages"）
- https://claude.com/blog/prompt-caching （缓存定价、用例）

---

### Task 4：新建 lession16/README3.md — 生产级 RAG

**新建文件**：`lession16/README3.md`

**内容大纲**：

```markdown
# 生产级 RAG：Hybrid + Rerank + Contextual

## 一句话定位
重型武器，三条件缺一不可（大数据量 + 语义模糊 + 没法塞 context）。

## Baseline RAG 反模式
网上教程教的那套（切块→Embedding→向量库→检索→生成）做 demo 可以，做产品即翻车。

## 三大必做升级
1. **Hybrid Search** — BM25 + Embedding 双路召回
2. **Reranker** — 性价比最高的一次升级（+25pp vs 换 embedding +2pp）
3. **Contextual Retrieval** — Anthropic 2024 提案（-49% 失败率，+rerank -67%）

## Anthropic 官方数据
- Contextual Embeddings 单独：-35% 失败率
- Contextual Embeddings + Contextual BM25：-49%
- 再加 Reranking：-67%
- 成本：$1.02 / 百万文档 token（用 prompt caching）
- 推荐 embedding：Voyage / Gemini
- 推荐 reranker：Cohere / Voyage

## 流程图
mermaid：原始 → Contextualizer (Claude Haiku) → Embedding + BM25 → 检索 → Reranker → Top-K → LLM

## 工具链
- LangChain / LlamaIndex
- Qdrant / Weaviate / Pinecone
- Cohere Rerank / Voyage Rerank
- Claude Haiku 做 Contextualizer

## 思考题
```

**参考来源**：
- https://www.anthropic.com/engineering/contextual-retrieval （已抓取，含完整数据）
- README6.md 路线二

---

### Task 5：新建 lession16/README4.md — Agentic Retrieval

**新建文件**：`lession16/README4.md`

**内容大纲**：

```markdown
# Agentic Retrieval：从静态流水线到 Agent Loop

## 一句话定位
让 LLM 自己做"查不查、查什么、查够没"的判断；代码/多跳任务碾压 RAG。

## 范式转变
- 传统：retrieve → generate 静态流水线
- Agentic：loop（思考 → 工具 → 观察 → 思考 → ...）

## 代码场景全面碾压
- 内部数据：传统 RAG 42% vs Agent (grep + read) 89%
- Cursor / Claude Code 都走 agent 路线
- 原因：代码有结构、关键词天然准、多跳推理轻量

## 典型架构
mermaid：Planner → Search Tools → Read Tools → Critic → Loop

## 陷阱
1. **贵** — 每步 = 一次完整 LLM 调用（10 步 = $0.40 vs RAG $0.02）
2. **弱模型灾难** — 不会判断"够了"、不会换策略、死循环（门槛 ≥ Sonnet / GPT-4o）
3. **延迟** — 多步串行，5–15 分钟常见

## 工具集
- Claude Code / Cursor / Devin
- LangGraph / AutoGen
- Grep / Glob / Read（代码场景）
- Web Search / SQL（通用场景）

## 思考题
```

---

### Task 6：新建 lession16/README5.md — 结构化数据走 SQL

**新建文件**：`lession16/README5.md`

**内容大纲**：

```markdown
# 结构化数据走 SQL：业务数据的正确打开方式

## 一句话定位
业务表 dump 成文档 → 进向量库是反模式；让模型生成 SQL 直接查。

## 反模式
- 把 MySQL 表导出成 markdown，丢进向量库
- 精度爆死 + 实时性归零

## 正解：Text-to-SQL
- 模型理解 schema
- 生成 SELECT
- 调 API 或直连执行
- 返回结果给模型做分析/可视化

## 工具链
- Vanna（开源 Text-to-SQL）
- LlamaIndex SQL Query Engine
- 自拼：DDL + few-shot + Sonnet

## 实战示例
（接续 lession1 README1 的 NL2SQL 案例，扩展为端到端实现）

## 何时用 SQL，何时用 RAG？
| | SQL | RAG |
|:--|:--|:--|
| 数据形态 | 结构化表 | 非结构化文档 |
| 查询类型 | 聚合/过滤/统计 | 语义相似度 |
| 实时性 | 数据库新鲜即新鲜 | 取决于索引更新 |

## 思考题
```

---

### Task 7：新建 lession16/README6.md — Deep Research 架构

**新建文件**：`lession16/README6.md`

**内容大纲**：

```markdown
# Deep Research：一次查询 = 一篇报告

## 一句话定位
最重一档；多轮检索 + 综合生成，给尽调、学术综述、复杂研究用。

## 架构四件套
1. **Planner** — 拆解问题为子问题
2. **Search** — 独立检索（Web / DB / API）
3. **Reader** — 深度理解文档
4. **Aggregator** — 综合生成带引用的报告

mermaid 流程图

## 成本与延迟
- 一次查询 $5–$20
- 40+ LLM 调用 + 30+ Web Search
- 延迟 5–15 分钟

## 适用场景
- 尽调报告
- 学术综述
- 行业研究
- 复杂多跳问题

## 行业产品
- OpenAI Deep Research
- Google Gemini Deep Research
- Perplexity Pro Research
- **没一个是 RAG**

## 思考题
```

---

### Task 8：新建 lession16/README7.md — 决策框架与最佳实践

**新建文件**：`lession16/README7.md`

**内容大纲**：

```markdown
# 决策框架与最佳实践：Eval 与数据质量

## 决策清单（5 选 1）
1. 小数据 + 稳定 → 长 Context + Caching
2. 大数据 + 语义模糊 → Hybrid RAG + Rerank + Contextual
3. 代码/结构化/多跳 → Agent + grep / SQL
4. 复杂研究 + 用户付得起 → Deep Research
5. 以上都不确定 → **先建 Eval · 先洗数据**

## 避坑 1：没建 Eval
- 改 prompt 测试集 +18%，下周真实日志 -15%
- Eval 比换 embedding 模型重要 10x
- 工具：RAGAS / Phoenix / TruLens
- 第一天就建，100 个真实 query 起步

## 避坑 2：数据质量 < 算法
- 文档脏、表格碎、版本乱，架构再先进也救不回
- Chunking 之前的"脏活"：
  - 格式归一（md/html/pdf → 统一 markdown）
  - 表格单独处理（不切块，走 text-to-SQL）
  - Metadata 设计（来源/时间/部门/版本）
  - 冲突/过时机制

## 残酷真相
三个月项目，算法工作 ~2 周，数据洗涮 ~10 周。

## 逃生舱
不想洗数据 → 回去看长 Context + Caching，让模型自己消化原始文档。

## 思考题
```

---

### Task 9：新建 lession16/README8.md — 综合示例

**新建文件**：`lession16/README8.md`

**内容大纲**：

```markdown
# 综合示例：构建"少府智库"个人知识库的完整决策

## 背景
100 份 PDF 学术论文 + 1000 条印象笔记 + 50 段播客转录

## 第一步：数据盘点
（用前几章的决策框架逐步分析）

## 第二步：方案选择
混合方案：
- 学术论文 → RAG (Hybrid + Rerank + Contextual)
- 印象笔记 → 长 Context + Caching
- 播客转录 → Deep Research 综合

## 第三步：搭建
（粗线条描述 Obsidian + Claude + qmd 工具链）

## 第四步：Eval
（RAGAS 跑 100 个 query，迭代 3 轮）

## 思考题
```

---

### Task 10：执行 git commit

**操作**：
```bash
git add note/11.ai/training/lession1/ note/11.ai/training/lession16/
git commit -m "docs(training): 扩展知识库章节 - 增补 5 路径技术全景"
```

---

## 关键参考数据汇总

来自权威源的关键数据，写入新章节时直接引用：

| 数据点 | 来源 | 用途 |
|:--|:--|:--|
| Contextual Retrieval -49% 失败率，+rerank -67% | Anthropic 官方 | README3 |
| Prompt Caching 成本 -90%、延迟 -85% | Anthropic 官方 | README2 |
| Cache write 25% 溢价 / read 10% 基础价 | Anthropic 官方 | README2 |
| 200K tokens ≈ 500 pages = "直接塞 prompt" | Anthropic 官方 | README2 |
| 100K 文档问答：11.5s → 2.4s（-79%） | Anthropic 官方 | README2 |
| Claude 3.5 Sonnet 200K 窗口 / 1M Sonnet 4.5 | 官方/行业 | README2 |
| Gemini 2M tokens | Google 官方 | README2 |
| 传统 RAG vs Agent 42% vs 89%（代码） | README6 | README4 |
| 一次 Deep Research $5–$20、5–15 min | README6 | README6 |
| 数据洗涮 10 周 vs 算法 2 周 | README6 | README7 |

---

## 执行顺序

1. Task 1（lession1 扩展）— **独立任务，可单独交付**
2. Task 2（README.md 重写）— 必须先于其他新章节
3. Task 3–9（README2–8 新建）— **互相独立，可并行**（但建议按顺序保证内容连贯）
4. Task 10（git commit）— 最后

---

## 待用户确认

- [ ] lession1 的扩展位置：放在"### 思考"之前 vs 之后？（**推荐**：之后，避免破坏原阅读流）
- [ ] lession16 是否要拆为多文件？（**推荐**：是，便于 5 路径独立阅读；保持 README1 不动）
- [ ] 是否保留 README1.md 的 LLM Wiki 内容？（**推荐**：是，Karpathy 的视角独特，与 5 路径互补）
- [ ] 是否需要中英对照？（**推荐**：否，纯中文，风格统一）
- [ ] 是否需要 mermaid 图？（**推荐**：是，每章至少一张，与现有风格一致）
- [ ] 综合示例的"少府智库"是否合适？（**推荐**：是，结合用户写作风格的中文名）

---

> ⏸ **等待用户审核后再开始执行 Task 1–10**
