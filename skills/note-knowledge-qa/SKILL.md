---
name: note-knowledge-qa
description: Use when user asks a technical question / "查 note" / "知识库问答" / "我有问题想问" requests interview prep / "面试题" / "出一道题" / "考考我" / "根据简历出题" / "模拟面试" / "面试非科班" wants system design guidance / "如何设计 X" or needs knowledge from the note/ knowledge base — retrieves relevant articles across 14 modules, follows cross-references, synthesizes comprehensive answers with citations
---

# note 知识库问答

## Overview

把 `note/` 知识库（14 主模块 / 670 README / 994 .md，2026-07-10 实测 671/996）变成**可检索的私人智囊**。对用户问题做：关键词提取 → 模块定位 → 文件检索 → 关联追踪 → 整合回答。

**核心原则**：**先搜后答** —— 不凭记忆回答，先从 note/ 检索相关内容，确保答案有据可查。

## Quick Example

```
用户：HashMap 为什么线程不安全？
   ↓
skill 执行：A 类型（技术问答）→ grep "HashMap" → 双层检索（01.java + 13.split-hairs）
   ↓
输出（节选）：
  ## HashMap 线程不安全

  HashMap 在并发 put 时可能导致：
  1. JDK 7 死循环（链表成环，CPU 100%）— 已修复（JDK 8 红黑树）
  2. JDK 8+ 数据丢失（覆盖 + size 错乱）

  ### 详细解释
  [源码分析 + JDK 8 修复后的残余风险]

  ### 实战建议
  1. 多线程场景用 ConcurrentHashMap
  2. 老代码里 HashMap 套 Collections.synchronizedMap 是性能最低选项

  ### 📚 知识来源
  | 来源 | 路径 | 覆盖内容 |
  | HashMap 原理 | note/01.java/collection/hashmap/README.md | 数据结构 + 树化阈值 |
  | 面试陷阱 | note/13.split-hairs/01.java/hashmap-thread-safe/ | 并发死循环细节 |

不同点：不凭 LLM 训练知识答 — 每条都附 note/ 实际文章路径

## 50+ 新词检索映射表（2026-07-14 新增）

**今天沉淀 50+ AI/ML 词汇**，按检索映射表快速定位：

### LLM 架构层（5 词）

| 词汇 | 主模块 | 13.split-hairs |
|------|--------|---------------|
| Transformer | `11.ai/01-fundamentals/transformer` | `13.split-hairs/11.ai/transformer` |
| 注意力机制 | `11.ai/01-fundamentals/attention-mechanism` | (在 attention-mechanism 中) |
| MoE 架构 | `11.ai/01-fundamentals/moe-architecture` | (在 moe-architecture 中) |
| RoPE 位置编码 | `11.ai/01-fundamentals/rope-position-encoding` | (在 rope 中) |
| Flash Attention | `11.ai/01-fundamentals/flash-attention` | (在 flash-attention 中) |

### LLM 推理优化（10 词）

| 词汇 | 主模块 | 13.split-hairs |
|------|--------|---------------|
| KV Cache | `11.ai/02-technology-stack/kv-cache` | `13.split-hairs/11.ai/llm-inference` |
| PagedAttention | `11.ai/02-technology-stack/paged-attention` | (在 llm-inference 中) |
| Continuous Batching | `11.ai/02-technology-stack/continuous-batching` | (在 llm-inference 中) |
| Speculative Decoding | `11.ai/02-technology-stack/speculative-decoding` | (在 llm-inference 中) |
| 权重量化 | `11.ai/02-technology-stack/weight-quantization` | (在 llm-inference 中) |
| MoE 推理 | `11.ai/02-technology-stack/moe-inference` | (在 llm-inference 中) |
| 推理性能指标 (TTFT/TPOT) | `11.ai/02-technology-stack/inference-metrics` | (在 llm-inference 中) |
| 推理框架对比 | `11.ai/02-technology-stack/inference-frameworks` | (在 llm-inference 中) |
| LLM 推理优化大专题 | `11.ai/02-technology-stack/llm-inference-optimization` | `12.story/46-llm-inference` |
| vLLM / TGI / SGLang | `11.ai/02-technology-stack/inference-frameworks` | - |

### LLM 训练与对齐（10 词）

| 词汇 | 主模块 | 13.split-hairs |
|------|--------|---------------|
| SFT | `11.ai/03-engineering/llm-alignment/01-sft` | `13.split-hairs/11.ai/llm-alignment` |
| RLHF | `11.ai/03-engineering/llm-alignment/02-rlhf` | (在 llm-alignment 中) |
| PPO | (在 RLHF 中) | (在 llm-alignment 中) |
| Reward Model | (在 RLHF 中) | - |
| DPO | `11.ai/03-engineering/llm-alignment/03-dpo` | (在 llm-alignment 中) |
| Constitutional AI | `11.ai/03-engineering/llm-alignment/04-constitutional-ai` | (在 llm-alignment 中) |
| KTO / IPO / SimPO | `11.ai/03-engineering/llm-alignment/05-newer-methods` | (在 llm-alignment 中) |
| ORPO / RFT | (在 newer-methods 中) | - |
| LLM 对齐专题 | `11.ai/03-engineering/llm-alignment` | (在 llm-alignment 中) |

### LLM 应用层（10 词）

| 词汇 | 主模块 | 13.split-hairs |
|------|--------|---------------|
| Lost In the Middle | `11.ai/02-technology-stack/lost-in-middle` | (在 context-engineering-interview 中) |
| YaRN / RoPE 扩展 | `11.ai/02-technology-stack/yarn-context-extension` | (在 llm-benchmark 中) |
| Chunking 策略 | `11.ai/02-technology-stack/chunking-strategies` | (在 rag 中) |
| Embedding 模型 | `11.ai/02-technology-stack/embedding-models` | (在 rag 中) |
| Hybrid Search | `11.ai/02-technology-stack/hybrid-search` | (在 rag 中) |
| Reranker | `11.ai/02-technology-stack/reranker` | (在 rag 中) |
| Query Rewrite | `11.ai/02-technology-stack/query-rewrite` | - |
| RAG Pipeline | `11.ai/02-technology-stack/rag-pipeline` | - |
| RAG 评估 | `11.ai/06-agent-evaluation/09-rag-evaluation` | - |
| RAGAS / TruLens | `11.ai/06-agent-evaluation/09-rag-evaluation` | - |

### 传统 ML 算法（10 词）

| 词汇 | 主模块 | 13.split-hairs |
|------|--------|---------------|
| K-means | `02.computer-basics/02-algorithms/clustering/k-means` | `13.split-hairs/02.computer-basics/machine-learning` |
| 梯度下降 | `02.computer-basics/02-algorithms/optimization/gradient-descent` | (在 machine-learning 中) |
| PCA | `02.computer-basics/02-algorithms/dimensionality-reduction/pca` | (在 machine-learning 中) |
| 分支界限 | `02.computer-basics/02-algorithms/search/branch-and-bound` | - |
| ID3 / C4.5 / CART | `02.computer-basics/02-algorithms/decision-tree` | (在 machine-learning 中) |
| Random Forest | `02.computer-basics/02-algorithms/ensemble` | - |
| XGBoost / LightGBM | `02.computer-basics/02-algorithms/ensemble` | - |
| 集成学习 | `02.computer-basics/02-algorithms/ensemble` | - |
| 评估指标 (F1/AUC) | (在 machine-learning 面试中) | (在 machine-learning 中) |
| ML 面试 | - | `13.split-hairs/02.computer-basics/machine-learning` |

### 自动触发流程（改进）

**当用户问"X 是什么"时**：
1. 查本映射表（X → module 路径）
2. 读主模块深度 + 13.split-hairs 面试版
3. 综合回答 + 引用

**示例**：
```
用户："DPO 是什么？"
skill：查表 → DPO 在 11.ai/03-engineering/llm-alignment/03-dpo + 13.split-hairs/11.ai/llm-alignment
回答：包含 SFT/RLHF 上下文 + DPO 数学保证 + vs RLHF 对比 + 5 大反直觉
```
```

## When to Use

**Use when**：
- 用户问技术问题（如 "JVM 参数怎么配"、"HashMap 原理"）
- 用户要面试题（如 "出一道 Java 后端面试题"）
- 用户要系统设计指导（如 "如何设计 SSO"）
- 用户要面试模拟（如 "我来答你出题"）
- 用户给简历要面试问题（如 "根据简历出题"）
- 用户问 AI 相关（如 "如何平衡 AI 成本"）
- 任何可以利用 note/ 知识库回答的问题

**Don't use when**：
- 用户问的是 note/ 里没有的主题（→ 直接用通用知识回答，说明 note 未覆盖）
- 用户问的是 note/ 结构/维护问题（→ 用其他 skill）
- 用户明确说"不要搜 note"

## 问答流程（4 步）

### Step 1: 问题分类

将用户问题归入以下类型之一：

| 类型 | 触发词 | 响应策略 |
|------|--------|---------|
| **A. 技术问答** | "什么是X"、"X原理"、"为什么X"、代码/配置问题 | 检索 → 解释 → 引用 |
| **B. 出题模式** | "出面试题"、"考考我"、"给我出题" | 检索 → 生成题目+答案 |
| **C. 设计指导** | "如何设计X"、"架构选型"、"方案对比" | 检索多模块 → 对比分析 |
| **D. 模拟面试** | "我来答你出题"、"模拟面试"、"面试练习" | 交互式：出题→等答→评价 |
| **E. 简历面试** | "根据简历出题"、"帮我准备面试他" | 解析简历（含教育背景检测）→ 匹配 note → 出题 |
| **F. 学习路径** | "怎么学X"、"学习路线" | 检索模块 README 的学习路径 |
| **G. 面试官出题** | "帮我出题面他"、"面试非科班"、"设计面试流程"、"面应届生" | 识别候选人画像 → 从问题库选题 → 输出题目+评估要点 |

### Step 2: 关键词提取 + 模块定位

从问题中提取关键词，映射到 note/ 模块：

```
关键词提取规则：
├─ 技术术语直接映射（HashMap → 01.java, RAG → 11.ai）
├─ 配置/参数映射（JVM → 01.java/jvm, Spring → 06.spring）
├─ 架构/设计映射（SSO → 04.system-design, 微服务 → 04 + 06）
├─ AI 概念映射（成本 → 11.ai + 12.story, Agent → 11.ai）
├─ 面试方法论映射（面试官/非科班/应届生/转码/跨专业/出题 → 14.project-management/interviewing-cross-disciplinary）
└─ 跨领域问题（拆成多个关键词，分别检索）
```

**模块速查表**（按"用户提问频次"降序排列 — 高频模块在前，方便快速定位）：

| 排名 | 模块 | 擅长回答的问题类型 |
|:---:|------|------------------|
| 🥇 | `01.java` | Java 语言、JVM、并发、集合、Kotlin |
| 🥈 | `11.ai` | LLM、RAG、Agent、Prompt、Token、MCP、AI 工程 |
| 🥉 | `06.spring` | Spring Boot/Cloud、MyBatis、缓存、消息队列 |
| 4 | `03.database` | MySQL、Redis、索引、事务、SQL 优化 |
| 5 | `04.system-design` | 系统设计、高可用、分布式、安全、SSO |
| 6 | `13.split-hairs` | 面试精炼版（陷阱+话术）、咬文嚼字 |
| 7 | `02.computer-basics` | 网络、算法、数据结构、操作系统 |
| 8 | `05.tools` | Docker、K8s、Git、CI/CD |
| 9 | `14.project-management` | 项目管理、DORA、研发效能、**面试方法论、跨专业候选人评估** |
| 10 | `12.story` | 概念叙事理解（阿明餐厅系列）、架构演进故事 |
| 11 | `09.front-end` | JS/TS、React、Web Components、设计系统 |
| 12 | `08.application-systems` | ERP、CRM、EAM 等企业系统 |
| 13 | `10.big-data` | Flink、Spark、ClickHouse、数仓 |
| 14 | `07.workflow` | 流程引擎、Camunda、BPMN |

**排序依据**（参考本仓库 `wb04307201` 项目定位 Java 后端 + AI 工程）：
- 🥇 Java 后端开发最常用（语言 + 集合 + 并发）
- 🥈 AI 工程是当前热点（RAG / Agent / Prompt）
- 🥉 Spring 系是 Java 企业开发的标配
- 4-5 数据库 + 系统设计 = 后端进阶必问
- 6-7 面试题 + 科班基础 = 面试 + 校招高频
- 8-9 DevOps + 面试方法论
- 10-14 偏垂直领域，按需检索

### Step 3: 检索 + 关联追踪

**3.1 初始检索**（并行搜索）

```bash
# 1. 关键词全文搜索（取 top 10 相关文件）
grep -rl "<关键词>" note/ | head -10

# 2. 模块 README 优先读（获取全景视图）
# 先读命中模块的 README.md，了解目录结构

# 3. 精确匹配子目录
find note/<module> -type d -name "*<topic>*" 2>/dev/null
```

**3.2 深度读取**（选 3-5 篇最相关的读全文）

- 优先读 leaf 文章（深度内容）而非 README 索引
- 每读一篇，检查其"相关章节"链接，追踪 1-2 篇关联文章
- 面试题类型（被面试者视角）：同时读 `13.split-hairs` 和主模块（双层检索）
- 面试官出题类型（G 类型）：**优先读 `14/interviewing-cross-disciplinary`**（问题库），按需引用 `13.split-hairs` 作降维素材

**双层检索 grep 模板**（核心武器，直接复用）：

```bash
# 用法：bash double_layer_search.sh "<关键词>"
KEYWORD="${1:?需要 1 个参数：关键词}"

# === 主模块命中（深度原理）===
echo "═══ 主模块命中（按命中数倒序，最多 10 个）═══"
grep -rl "$KEYWORD" note/ --include="*.md" 2>/dev/null \
  | grep -v "/13.split-hairs/" \
  | xargs -I {} sh -c 'count=$(grep -c "$0" "{}" 2>/dev/null); echo "$count {}"' "$KEYWORD" \
  | sort -rn \
  | head -10 \
  | awk '{print "  " $1 " 处命中  →  " $2}'

# === 13.split-hairs 命中（被面试者视角）===
echo ""
echo "═══ 13.split-hairs 命中（面试陷阱版，最多 5 个）═══"
grep -rl "$KEYWORD" note/13.split-hairs/ 2>/dev/null \
  | xargs -I {} sh -c 'count=$(grep -c "$0" "{}" 2>/dev/null); echo "$count {}"' "$KEYWORD" \
  | sort -rn \
  | head -5 \
  | awk '{print "  " $1 " 处命中  →  " $2}'

# === 12.story 命中（叙事类比版）===
echo ""
echo "═══ 12.story 命中（阿明餐厅版，最多 3 个）═══"
grep -rl "$KEYWORD" note/12.story/ 2>/dev/null \
  | head -3 \
  | awk '{print "  →  " $1}'

# === 14.project-management 命中（仅面试方法论问题）===
echo ""
echo "═══ 14.project-management 命中（面试官视角，最多 3 个）═══"
grep -rl "$KEYWORD" note/14.project-management/ 2>/dev/null \
  | head -3 \
  | awk '{print "  →  " $1}'

# === 候选阅读顺序（主模块优先，13.split-hairs 双层，12.story 收尾）===
echo ""
echo "═══ 建议阅读顺序：主模块 → 13.split-hairs → 12.story（叙事辅助）═══"
```

**双层调度决策**（根据问题类型选择检索顺序）：

| 问题类型 | 主模块 | 13.split-hairs | 12.story | 14.project-management |
|---------|:---:|:---:|:---:|:---:|
| **A 技术问答** | 第 1 读 | 可选 | 可选 | — |
| **B 出题** | 第 2 读（参答案） | **第 1 读** | 可选 | — |
| **C 设计指导** | **第 1 读** | 可选 | 收尾叙事 | — |
| **D 模拟面试** | **第 1 读** | **第 2 读** | 可选 | — |
| **E 简历面试** | **第 1 读** | 第 2 读 | 可选 | **第 2 读**（检测专业） |
| **F 学习路径** | **第 1 读**（Level 1-2） | 第 2 读（验证） | Level 4 收尾 | — |
| **G 面试官出题** | 第 3 读 | 降维对照 | — | **第 1 读**（问题库） |

**3.3 关联追踪**（跟着链接走）

```
读完文章 A → 发现"相关章节"链接到 B、C
├─ 如果 B/C 的标题与问题相关 → 读 B/C
├─ 如果 A 有"面试陷阱速览" → 读对应 13.split-hairs 版本
└─ 如果 A 有"故事联动" → 读对应 12.story 版本（获取叙事视角）
```

**3.4 检索终止条件**

- 已读 ≥ 3 篇深度文章
- 已覆盖问题的主要维度
- 关联文章的标题不再与问题相关
- 总读取量 ≤ 8 篇（避免过载）

### Step 4: 整合回答

根据问题类型选择回答模板：

---

#### A. 技术问答 模板

```markdown
## {问题简述}

{直接回答核心结论，1-2 句话}

### 详细解释

{基于 note/ 内容的详细解答，用表格/代码/图辅助}

### 实战建议

{基于 note/ 最佳实践的可操作建议}

### 📚 知识来源

| 来源 | 位置 | 覆盖内容 |
|------|------|---------|
| {文章标题} | `{note/路径}` | {覆盖了什么} |
| ... | ... | ... |

> 💡 **延伸学习**：{推荐 1-2 篇关联文章}
```

#### B. 出题模式 模板

```markdown
## 📝 面试题：{题目}

**难度**：⭐⭐⭐⭐ | **来源模块**：`{note/路径}`

### 题目

{场景化题目描述，不是干巴巴的"请解释X"}

### 参考答案

{分层次的完整答案}

**第一层（及格）**：{基础回答}
**第二层（良好）**：{深入分析}
**第三层（优秀）**：{源码级/实战级}

### 常见陷阱

| 陷阱 | 真相 |
|------|------|
| {陷阱1} | {真相1} |

### 面试话术（90 秒版）

> {可以直接在面试中说的话}

### 📚 知识来源

- {note/路径1}
- {note/路径2}
```

#### C. 设计指导 模板

```markdown
## {设计主题}

### 核心挑战

{这个设计问题的核心难点是什么}

### 方案对比

| 维度 | 方案 A | 方案 B | 方案 C |
|------|--------|--------|--------|
| ... | ... | ... | ... |

### 推荐方案

{基于 note/ 内容的推荐 + 理由}

### 关键设计点

{3-5 个关键决策点 + 建议}

### 📚 知识来源

- {note/路径列表}
```

#### D. 模拟面试 流程

```
1. 确认面试方向（Java后端 / 系统设计 / AI 工程师 / 前端...）
2. 确认难度（初级 / 中级 / 高级 / 架构师）
3. 从 note/ 检索对应模块，准备 5-8 道题目

交互流程（每题循环）：
┌─ 出题 → 等用户回答
│
├─ 评价用户答案：
│   ├─ ✅ 答对的部分（鼓励 + 标注覆盖深度：概念/原理/源码/实战）
│   ├─ ⚠️ 遗漏的点（补充 + 标注对应 note/ 文章）
│   ├─ 🔴 答错的部分（纠正 + 给出正确解释）
│   ├─ 📊 深度评估（当前回答在哪个层次）
│   └─ 💬 话术优化建议（面试中怎么说更好，给出 90 秒话术）
│
├─ 🔄 追问链生成（核心能力，见下方详细规则）：
│   ├─ 根据用户答案的薄弱点 → 从 note/ 检索关联文章 → 生成追问
│   ├─ 追问不是随机出题，而是沿着用户的知识缺口深挖
│   └─ 每轮追问后继续评估 → 继续追问（最多 3 轮深挖）
│
├─ 给出参考答案 + 面试话术
├─ 出下一题
└─ 5 题后给总结评价 + 知识地图
```

**追问链生成规则**（D/E 模式通用）：

```
用户回答 → 分析薄弱点 → 生成追问

═══ 科班路线追问（CS 专业候选人）═══

薄弱点识别方法：
├─ 只答了"是什么"没答"为什么" → 追问原理层
│   例：答了"HashMap 用红黑树"但没说为什么阈值是 8
│   → 追问："为什么树化阈值是 8 而不是 4 或 16？"
│
├─ 只答了概念没答源码 → 追问源码层
│   例：答了"synchronized 会锁升级"但没说 Mark Word 结构
│   → 追问："锁升级过程中 Mark Word 的 bit 布局怎么变？"
│
├─ 只答了正常路径没答异常/边界 → 追问异常层
│   例：答了"线程池任务提交流程"但没提拒绝策略
│   → 追问："如果队列满了且线程达到 maximum，4 种拒绝策略分别怎么处理？"
│
├─ 答错了具体知识点 → 纠正后追问关联知识
│   例：混淆了 submit 和 execute 的异常行为
│   → 追问："submit 吞掉的异常存在 FutureTask 的哪个字段？怎么监控？"
│
└─ 答得很好 → 追问实战/架构层
    例：线程池参数答得很全
    → 追问："如果线上线程池需要动态调参不重启，你怎么设计？"

═══ 非科班路线追问（跨专业候选人）═══

薄弱点识别方法：
├─ 只答了概念没答思维过程 → 追问"怎么想到的"
│   例：答了"用字典存数据"但没说为什么选字典
│   → 追问："你是怎么想到用字典的？还有别的存法吗？对比过吗？"
│
├─ 只答了正常流程没答边界 → 追问"如果出了问题怎么办"
│   例：设计了点单系统但没考虑取消订单
│   → 追问："如果用户下了单又取消呢？奶茶已经做了呢？"
│
├─ 答得好 → 追问跨专业优势 + 学习深度
│   例：系统设计拆出了 4 个模块
│   → 追问："你原专业的思维方式，帮你做了哪些设计决策？"
│   → 追问："这个方案你是从哪学来的？看了什么资料？"
│
└─ 答不出 → 给提示看反应（测领悟力）
    例：完全不知道怎么存数据
    → 给提示："如果你有一个电话簿，你会怎么查找？"
    → 评估：能顺着提示推导 = 高潜力；无动于衷 = 低潜力
```

追问检索流程：
1. 从薄弱点提取关键词
2. grep 搜索 note/13.split-hairs/ 和主模块
3. 读取命中的文章，找到对应段落
4. 基于 note/ 内容构造追问（确保追问有标准答案）
5. 追问时附"参考：{note/路径}"以便用户事后学习
```

**追问链输出格式**：

```markdown
### 🔄 追问（第 N 轮）

**你的薄弱点**：{分析用户答案中哪个层次缺失}

**追问**：{基于 note/ 内容的追问}

> 📖 这题的知识来源：`{note/路径}` — {文章标题}
> 建议事后阅读这篇补充：{关联文章路径}
```

#### E. 简历面试 流程

```
0. 教育背景检测（新增，决定出题策略）：
   ├─ 专业是 CS / SE / 软件工程 / 计算机相关？
   │   └─ 科班路线 → 正常技术深度题（原流程）
   └─ 专业是数学/金融/外语/文科/工科/其他？
       └─ 非科班路线 → 自动引入 14/interviewing-cross-disciplinary 问题库
           ├─ 技术题用降维版（从 13.split-hairs 改写）+ 场景版
           ├─ 重点考：自驱力、学习方法、逻辑思维、跨专业优势
           └─ 评估用：底线+加分模型（而非科班的标准答案深度）

1. 解析简历关键技术点（语言/框架/项目经验/行业）
2. 映射到 note/ 模块：
   ├─ 技术栈 → 对应主模块
   ├─ 项目经验 → 对应系统设计/架构模块
   ├─ 行业 → 对应应用系统模块
   └─ 非科班 → 14/interviewing-cross-disciplinary（问题库 + 评估模型）
3. 为每个技术点生成知识地图 + 问题清单

输出格式（两个部分）：

═══ 第一部分：知识地图 ═══

## 🗺️ 知识地图：{简历技术点}

{用 grep 搜索 note/ 中所有相关文章，按层次组织}

```
{技术点}
├── 基础层（概念/原理）
│   ├── `note/01.java/xxx/README.md` — {一句话概括}
│   └── `note/01.java/yyy/README.md` — {一句话概括}
├── 进阶层（源码/深度）
│   ├── `note/13.split-hairs/01.java/xxx/` — {面试题+陷阱}
│   └── `note/01.java/zzz/` — {源码分析}
├── 实战层（工程/架构）
│   ├── `note/06.spring/xxx/` — {Spring 集成}
│   └── `note/04.system-design/xxx/` — {系统设计}
└── 叙事层（故事/类比）
    └── `note/12.story/xxx.md` — {阿明餐厅类比}
```

═══ 第二部分：问题清单 + 追问链 ═══

## 🎯 面试问题清单

### {简历技术点1}：{具体内容}

| # | 问题 | 意图 | 期望答案层次 | note/ 参考 |
|---|------|------|------------|-----------|
| 1 | {基础题} | 验证基本功 | {关键词} | `{note/路径}` |
| 2 | {深度题} | 探测天花板 | {关键词} | `{note/路径}` |
| 3 | {场景题} | 验证实战 | {关键词} | `{note/路径}` |

### 🔄 预设追问链（根据候选人回答选择使用）

| 如果候选人... | 追问 | 追问来源 |
|-------------|------|---------|
| 只说了概念没说原理 | {原理追问} | `{note/路径}` |
| 只说了正常路径没说异常 | {异常追问} | `{note/路径}` |
| 回答正确但缺实战 | {实战追问} | `{note/路径}` |
| 回答全面 | {架构级追问} | `{note/路径}` |
```

**知识地图生成方法**：

```bash
# 1. 从简历提取技术关键词（如 "Redis"、"Spring Boot"、"分布式"）
# 2. 对每个关键词做全模块搜索
grep -rl "Redis" note/ | sort

# 3. 按目录分类为层次
#    01.java/xxx → 基础层
#    13.split-hairs/xxx → 进阶层（面试题）
#    06.spring/xxx → 实战层
#    04.system-design/xxx → 架构层
#    12.story/xxx → 叙事层

# 4. 读每篇文章的第一段 + summary，提取一句话概括
# 5. 组织成树形结构输出
```

#### F. 学习路径 流程

```
输出格式（两个部分）：

═══ 第一部分：知识地图 ═══

## 🗺️ {主题} 知识地图

{搜索 note/ 中所有相关文章，按学习顺序组织}

```
{主题}
├── Level 1: 入门（先读这些）
│   ├── `note/xx/yy/README.md` — {一句话}
│   └── `note/xx/zz/README.md` — {一句话}
├── Level 2: 进阶（掌握基础后读）
│   ├── `note/xx/aa/` — {一句话}
│   └── `note/13.split-hairs/xx/bb/` — {面试题，验证理解}
├── Level 3: 深入（想看源码/原理时读）
│   ├── `note/xx/cc/` — {一句话}
│   └── `note/xx/dd/` — {一句话}
└── Level 4: 实战（做项目时参考）
    ├── `note/xx/ee/` — {一句话}
    └── `note/12.story/xx.md` — {故事化理解}
```

═══ 第二部分：交互式学习路径 ═══

## 📚 推荐学习顺序

1. {第一步} → `{note/路径}`
   > 读完自测：{一个简单自测问题}
2. {第二步} → `{note/路径}`
   > 读完自测：{一个简单自测问题}
...

### 🔄 学习追问（可选）

学完每步后，可以说"考考我"触发追问链：
├─ 我会从 note/ 出一道题检验你的理解
├─ 根据你的回答分析薄弱点
├─ 推荐下一步该读哪篇（基于你的薄弱点动态调整）
└─ 如果你的回答暴露了前置知识缺失 → 推荐回退到 Level N
```

**自适应学习路径**：

```
用户说"考考我"或"我学完了"
├─ 从当前 Level 的 note/ 文章出一道自测题
├─ 用户回答后：
│   ├─ 答对 → 跳到下一 Level
│   ├─ 答错 → 分析薄弱点 → 推荐回退或补充阅读
│   └─ 部分对 → 追问链深挖 → 确认掌握后继续
└─ 每个 Level 通过后更新知识地图（标记 ✅ 已掌握）
```

#### G. 面试官出题 模板

```markdown
## 🎯 面试问题清单：{候选人画像}

**候选人背景**：{专业} → 转码 | {自学/培训班/在职} | {项目经验简述}
**出题策略**：{降维版为主 / 场景版为主 / 混合} | 重点考察 {自驱力/逻辑思维/工程实践}

### 题目列表

| # | 题目 | 类型 | 考察维度 | 评估要点 | note/ 来源 |
|---|------|------|---------|---------|-----------|
| 1 | {场景化题目} | 降维/场景 | {转码动机/基础认知/系统设计/工程实践/跨专业优势} | {优秀答案信号} | `{路径}` |
| 2 | ... | ... | ... | ... | ... |

### 🔄 预设追问链

| 如果候选人... | 追问 | 考察什么 |
|-------------|------|---------|
| {答了概念没答思维过程} | {追问"怎么想到的"} | {学习深度} |
| {答不出} | {给提示看反应} | {领悟力/韧性} |
| {答得好} | {追问跨专业优势} | {复合价值} |

### 📋 评估速查

| 底线项 | 合格标准 |
|--------|---------|
| 代码手感 | {能写基础逻辑} |
| 基本常识 | {知道前后端/Git/HTTP} |
| 工程习惯 | {打断点调试 > print} |

| 加分项 | 具体表现 |
|--------|---------|
| 极客精神 | {自己折腾过工具/项目} |
| 跨专业优势 | {原专业带来的独特视角} |
| 学习斜率 | {按目前速度 1-3 年后能超过科班} |

### 📚 知识来源

| 来源 | 路径 | 覆盖内容 |
|------|------|---------|
| 面试问题库 | `note/14.project-management/interviewing-cross-disciplinary/` | 5 场景双题库 + 评估模型 |
| {降维对照} | `note/13.split-hairs/...` | {科班版原题} |
```

---

## 特殊处理

### 当 note/ 没有相关内容时

```markdown
> ⚠️ note/ 知识库未直接覆盖此主题。以下答案基于通用知识，非 note/ 内容。
> 
> **建议**：这个主题值得沉淀到 note/，可以运行 `/note-precipitation-planning` 规划位置。

{通用知识回答}
```

### 当问题跨多个模块时

```
跨模块问题处理：
1. 拆分问题为多个子问题
2. 每个子问题检索对应模块
3. 整合时标注每个子答案的来源模块
4. 特别标注跨模块关联（如 "06.spring 的缓存方案 + 03.database 的 Redis 实践"）
```

### 引用格式

所有回答末尾附 **📚 知识来源** 表格，列出引用的 note/ 文件。格式：

```markdown
### 📚 知识来源

| 来源 | 路径 | 覆盖内容 |
|------|------|---------|
| JVM 调优 | `note/01.java/jvm/tuning.md` | JVM 参数详解 |
| Loop Engineering | `note/11.ai/03-engineering/loop-engineering/README.md` | 循环调用原理 |
```

## Common Mistakes

**❌ Mistake 1: 直接凭印象答（核心反模式）**

- **症状**：用户问"JVM 参数怎么配"直接答，不 grep note/ → 答的是训练知识，事后与 note/ 不一致
- **修复**：Step 3.1 必须先 grep，即使是高频问题也要确认 note 怎么写

**❌ Mistake 2: 单一来源 = 薄弱回答**

- **症状**：只读 1 篇就整合；用户问"HashMap 原理"只引一篇
- **修复**：Step 3.4 终止条件是 ≥ 3 篇深度 + ≥ 1 篇追踪，不达标则继续读

**❌ Mistake 3: 忽略 13.split-hairs 双层（被面试者视角）**

- **症状**：用户出"为什么树化阈值是 8"，只引 01.java 主模块 → 缺面试陷阱视角
- **修复**：必须同时引 `13.split-hairs/<module>/<topic>/`（面试陷阱版）+ 主模块深度版

**❌ Mistake 4: 漏写知识来源表**

- **症状**：回答末尾没有 📚 知识来源表 → 用户无法追溯 → 失去本 skill 的核心价值
- **修复**：必填项；输错一步是 invalid output；模板见"引用格式"小节

**❌ Mistake 5: 跨模块问题不拆解**

- **症状**：用户问"如何设计 SSO"，单点答完一个模块就结束 → 漏掉 SAML/CAS 等
- **修复**：见"当问题跨多个模块时"流程：拆分子问题 → 各自检索 → 标注模块来源

**❌ Mistake 6: 候选人专业漏检（E/G 类型专属）**

- **症状**：简历面试忘了检测非科班 → 自动用科班路线题压人 → 应聘者被错杀
- **修复**：见 E 类型 Step 0 教育背景检测；非科班自动用 `14/interviewing-cross-disciplinary` 问题库 + 非科班追问链

**❌ Mistake 7: 模拟面试不追问（D/E 类型专属）**

- **症状**：D 模式下一题一答就跳下一题，没追问链 → 失去核心价值（深度评估）
- **修复**：追问链是 D/E 的差异化能力；每轮必续追问链，最多 3 轮深挖；见"追问链生成规则"

**❌ Mistake 8: 注水重复 cite**

- **症状**：📚 知识来源表里同一篇文章 cite 3 次（基础/进阶/实战都填同一篇）
- **修复**：每个来源必须覆盖**不同维度**（基础/原理/实战/面试题/故事层各一篇），避免重复

**❌ Mistake 9: G 类型出题用科班题库**

- **症状**：面试非科班候选人，直接搬 13.split-hairs 原题 → 应聘者答不出 → 错杀潜力股
- **修复**：见 G 模板"降维版为主 + 重点考察自驱力/逻辑思维/跨专业优势"

---

## Real-World Impact

本 skill 是"**非通用 AI**"的区分点 —— 强制 LLM 把 note/ 当作私有知识库使用，而不是凭训练知识答。

**典型场景 + 预期产出**：

| 类型 | 触发场景 | 期望产出 | 耗时 |
|------|---------|---------|------|
| **A. 技术问答** | "HashMap 原理" | 找 3+ 篇 + 整合代码示例 + 📚 知识来源 | ~2 分钟 |
| **B. 出面试题** | "出一道 JVM 题" | 场景化题 + 三层答案 + 90 秒话术 | ~5 分钟 |
| **C. 设计指导** | "如何设计 SSO" | 3 方案对比表 + 推荐 + 关键设计点 | ~8 分钟 |
| **D. 模拟面试** | "我来答你出题" | 题目 + 评估 + 追问链 3 轮 + 总结 | 持续 |
| **E. 简历面试** | "根据简历出 5 题" | 教育检测 + 知识地图 + 5 题清单 + 追问库 | ~10 分钟 |
| **F. 学习路径** | "怎么学 RAG" | 知识地图（Level 1-4）+ 路径 + 自测题 | ~6 分钟 |
| **G. 面试官出题** | "面非科班应届" | 候选人画像 + 双题库 + 评估速查表 | ~10 分钟 |

**避免的失败**：
- ❌ 凭训练知识答（用户事后发现与 note/ 不一致 → Mistake 1）
- ❌ 漏知识来源表（用户无法自我纠错 → Mistake 4）
- ❌ 跨模块问题只答一半（如 SSO 只答 OAuth 不答 SAML → Mistake 5）
- ❌ 简历面试一刀切（科班/非科班混用题库 → Mistake 6/9）
- ❌ 模拟面试变"答题器"（无追问 → Mistake 7）

**联动 skill**：
- 上游：`note-precipitation-planning`（每答一次 A 类都暴露缺口 → 触发沉淀新主题）
- 上游：`note-health`（文章质量验收 + 结构体检 → 间接影响本 skill 的答案质量）
- 下游：`note-health`（本 skill 暴露的高频"note 未覆盖"主题可作为缺口数据）

---

## Quick Checklist（回答前必过）

- [ ] 问题已分类（A/B/C/D/E/F/G 类型）
- [ ] 关键词已提取并映射到模块
- [ ] 已搜索 note/（至少 grep 一次）
- [ ] 已读 ≥ 3 篇相关文章
- [ ] 已追踪 ≥ 1 篇关联文章
- [ ] 回答末尾有 📚 知识来源
- [ ] 如果 note/ 未覆盖，已标注并建议沉淀
- [ ] **E/G 类型**：已检测候选人教育背景（科班 vs 非科班）
- [ ] **E/G 非科班**：出题来源是 `14/interviewing-cross-disciplinary`（不是 `13.split-hairs`）
- [ ] **E/G 非科班**：追问链使用非科班规则（思维过程/给提示看反应/跨专业优势）
