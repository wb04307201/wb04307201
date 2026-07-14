<!--
question:
  id: 11.ai-claude-code-agentic-search
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 反直觉辨析
  tags: [11.ai, Claude Code, Agentic Search, RAG, 检索, AI Coding]
-->

# 为什么 Claude Code 放弃了 RAG？ — Agentic Search 取代 RAG 的反直觉革命

> 一句话定位：Claude Code（Anthropic 2025 CLI 工具）在大型代码库场景下**主动放弃了 RAG**，改用 Agentic Search —— 这是 AI Coding 范式的根本转变。深度原理见 [主模块 Agentic Search vs RAG](../../../11.ai/08-llmops/agentic-search-vs-rag/README.md) + [Claude Code 实践](../../../11.ai/03-engineering/claude-code-practices/README.md)。

> **系列定位**：经典 AI 面试题（高频、反直觉必考）。考察的不是"RAG 是什么"，而是 **AI Coding 检索范式的演进** + **RAG 在工程实践中的边界** + **Harness 取代索引的范式转变**。

---

⭐⭐⭐⭐⭐ 深度级别（架构师级）
📚 前置知识：RAG 基本架构、向量检索、Agent 与工具调用、Claude Code 基本使用

---

## 引子：面试官的"反直觉"陷阱

阿明去面试某 AI Coding 创业公司，面试官问：

> "你们的 AI Coding 工具用 RAG 检索代码库吗？"

阿明答："用了，全库 embedding 后用向量检索……"

面试官追问："如果工程师刚 commit 了代码，你的 RAG 索引什么时候能更新？"

阿明答："半小时到 1 小时吧。"

面试官："这半小时内，工程师问'刚改的函数怎么调用'，你的 RAG 检索到的还是改之前的内容。AI 给的答案可能完全错误。Claude Code 的设计者早就看到了这个问题——**他们直接放弃了 RAG**。"

阿明愣住。

**这道题的陷阱在于**：很多人以为 RAG 是 AI Coding 的标配。但 Claude Code（Anthropic 2025）官方明确说"**在大规模代码库场景下，RAG 容易失败**"。他们改用了一种全新的检索范式——**Agentic Search（智能体式搜索）**。

今天我们就讲清楚：
1. 为什么 RAG 在 AI Coding 上失败？
2. Agentic Search 是什么？
3. Claude Code 的完整 Harness 设计
4. RAG 真的被淘汰了吗？

## 一、核心原理：4 个层面

### 1.1 RAG 在大型代码库的 3 大工程问题

**问题 1：索引滞后（Index Staleness）**

- 嵌入管道（embedding pipeline）需要持续构建、维护
- 工程师改完代码 → 索引几小时/几天后才更新
- **索引反映的不是实时代码** —— 检索结果可能误导 AI

实际场景：
```
09:00 工程师 commit 修改了 auth.py 的 50 行
09:05 工程师问 AI："刚才那个 auth 改动是干嘛的？"
09:05 AI 检索 RAG 索引 → 返回的是 09:00 之前的内容
09:05 AI 答错（基于过期索引）
```

**问题 2：检索粒度错配（Granularity Mismatch）**

- 向量检索返回"语义相似"的代码片段
- 但工程师实际需要的是"**定义、实现、调用、测试**"四件套
- RAG 的"语义相似" ≠ "工程相关"

**问题 3：索引维护成本（Pipeline Cost）**

- 嵌入管道：定时任务 / 监听 git push / CI 触发
- 存储：向量数据库（百万级代码需要 GB 级向量存储）
- 监控：管道挂了没人知道 → 索引悄悄过期
- **这是一笔持续的、隐藏的、巨大的运维成本**

### 1.2 Agentic Search 的 3 大优势

**优势 1：实时（Zero Latency）**

- Agent 直接用工具（grep / read / glob / bash）查询**实时代码库**
- 没有索引滞后问题
- 工程师 commit 后立即可见

**优势 2：跟随引用（Reference Following）**

- 找到函数定义 → 跟到调用方 → 跟到测试用例 → 形成完整调用链
- 向量检索做不到这种**结构化遍历**

**优势 3：本地实例（Local Instance）**

- 每个开发者的 Claude Code 实例基于**自己的代码库快照**工作
- 不上传代码到服务器（隐私友好）
- 不需要集中式索引

### 1.3 Claude Code 的 5 大 Harness 扩展点

Anthropic 官方说："**围绕模型构建的生态系统（Harness）对 Claude Code 的表现影响更大**"。5 个扩展点（构建顺序很重要）：

| 优先级 | 扩展点 | 作用 | vs RAG 的优势 |
|--------|--------|------|--------------|
| **1** | CLAUDE.md 文件 | 每次会话自动读取的上下文 | 比 RAG 更聚焦、更可控 |
| **2** | Hooks（钩子） | 自动化检查（lint / format / stop hook）| 确定性执行，不依赖检索 |
| **3** | Skills（技能） | 渐进式披露（按需加载专业知识）| 比 RAG 的"先检索"更精准 |
| **4** | Plugins（插件） | 打包 skills + hooks + MCP | 团队复用，比共享 RAG 索引更轻量 |
| **5** | MCP 服务器 | 连接内部工具 / 数据源 / API | 结构化查询，比非结构化 RAG 更可靠 |

**核心洞察**：RAG 是"**先把代码库索引化，再检索**"——**中心化、滞后、粒度错配**。Harness 是"**让 Agent 直接活在代码库里**"——**去中心化、实时、跟随结构**。

### 1.4 RAG 的真实场景：什么时候仍然有效？

RAG 不是被淘汰，是**场景化**：

| 场景 | 适合方案 | 原因 |
|------|---------|------|
| **大规模代码库**（百万行+）| Agentic Search | RAG 滞后问题严重 |
| **文档问答 / 客服知识库** | RAG | 文档更新频率低 / 结构化 |
| **私人知识库（Obsidian 类）**| RAG + Agentic 混合 | 个人代码量小，可接受 RAG |
| **企业合规文档检索** | RAG + 权限过滤 | 需要严格的访问控制 |
| **代码片段搜索（Code Search）** | 传统 grep + LSP | 比 RAG 更精准 |

**反直觉结论**：RAG 仍然是**"低频更新、结构化内容"**的最佳方案；**"高频更新、强结构依赖"**的场景（如代码库），Agentic Search 完胜。

## 二、常见陷阱（面试必踩）

### 陷阱 1：把 RAG 当成"AI Coding 的标配"

错。Claude Code、Cline、Aider 等主流 AI Coding 工具**多数放弃了 RAG**。

### 陷阱 2：以为"Agentic Search = 智能 grep"

错。Agentic Search 是**循环的多步推理**（搜 → 读 → 跟引用 → 再搜 → 综合），不是单次 grep。

### 陷阱 3：以为"放弃 RAG = 不用检索"

错。Claude Code 仍然检索——但用的是**结构化工具调用**（grep / glob / LSP），不是向量检索。

### 陷阱 4：以为"所有 AI Coding 工具都不用 RAG"

错。一些工具（Sourcegraph Cody、Codeium）仍用 RAG。**关键看是否解决了"索引滞后"**。

### 陷阱 5：把"Agentic Search"和"RAG"对立

错。两者可以**组合使用**：先用 RAG 找大致范围，再用 Agentic Search 精细定位。

## 三、面试话术（90 秒版本）

面试官："为什么 Claude Code 不用 RAG？"

**30 秒简版**：

> "主要是 RAG 在大规模代码库上有 3 个工程问题：**索引滞后**（改代码后几小时/几天才同步）、**粒度错配**（返回语义相似但工程不相关）、**维护成本高**（嵌入管道持续维护）。Claude Code 改用 **Agentic Search**——让 Agent 直接用 grep/read/glob 工具查询实时代码库，跟随引用追踪调用链。再加上 CLAUDE.md / Skills / Hooks / MCP 5 层 Harness，**用规范取代了索引**。"

**60 秒扩展版**（如果面试官追问）：

> "具体来说，Anthropic 官方博客明确说'与基于 RAG 的 AI 编码工具不同……大规模场景下，这类系统容易失败'。原因是工程师每天 commit 几十次，RAG 索引几小时后才更新，**AI 给的答案基于过期信息**——这是 RAG 在 AI Coding 上的根本缺陷。
>
> Claude Code 的解法是 **Agentic Search**：Agent 在每次任务中循环调用 grep/read/glob 等工具，**实时**搜索本地代码库，跟随引用跨文件追踪。这种方式没有索引维护成本，也没有滞后问题。
>
> 不过 Claude Code 也没否定 RAG 本身——RAG 在**文档问答、低频更新场景**仍然是最佳方案。Anthropic 的核心观点是：**AI Coding 不是 RAG 的主战场，Harness 才是**。"

## 四、相关章节

**主模块**：
- [11.ai/08-llmops/agentic-search-vs-rag（深度原理）](../../../11.ai/08-llmops/agentic-search-vs-rag/README.md)
- [11.ai/03-engineering/claude-code-practices（Claude Code 实践）](../../../11.ai/03-engineering/claude-code-practices/README.md)
- [11.ai/08-llmops/01-rag-vs-finetuning（RAG vs Finetuning）](../../../11.ai/08-llmops/01-rag-vs-finetuning/README.md)

**同栏目（11.ai 高频面试题）**：
- [Transformer 架构深挖](../transformer/README.md)
- [RAG 架构设计](../rag/README.md)
- [Harness Engineering 概念辨析](../harness-engineering/README.md)
- [大模型中为什么不用 Dropout](../dropout-in-llm/README.md)

**架构视角**：
- [11.ai/04-architecture/llm-control-evolution（驾驭演进主线）](../../../11.ai/04-architecture/llm-control-evolution/README.md) — Agentic Search 是"Context"维度的新形态

---

> 📅 2026-07-03 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐

← [返回: 咬文嚼字 · claude-code-agentic-search](README.md)
