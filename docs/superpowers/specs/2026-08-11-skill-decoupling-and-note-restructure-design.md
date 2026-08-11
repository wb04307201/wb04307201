# Skill 解耦 + note 重构 设计文档

**日期**：2026-08-11
**分支**：`refactor/skill-note-decouple`
**状态**：待用户审阅

---

## 1. Context（背景）

### 1.1 原始问题

仓库的 3 个 meta-skill（`note-health` / `note-precipitation-planning` / `note-knowledge-qa`）在 SKILL.md 和 references/ 中**硬编码了大量 note 特定定义**：

- 14 模块列表、命名约定
- 6 维度 + A/B/C/D/E 类评估规则
- 11 类扫描规则及阈值
- 50+ 词的硬编码路径映射表
- commit 格式、frontmatter 规范

**后果**：skill 与具体知识库深度耦合，无法复用到其他项目；定义在 skill 里而非在 note 里，导致**单一真相源失效**。

### 1.2 扩展目标

在解耦 skill 的同时，发现 note/ 的目录结构经过 1 年多的演化，存在：

- 子目录命名不一致（`01-fundamentals/` vs `concept/` vs `collection/`）
- 模块边界模糊（04.system-design vs 08.application-systems、05.tools vs 07.workflow）
- 11.ai 单模块 191 文件过大（基础 + 应用混杂）
- 互链不完整（单向链接、孤立 README）

用户决定借此次解耦，**同时重构 note/ 为更合理的结构**。

### 1.3 最终目标

打造一个 **LLM Wiki + Obsidian 风格** 的知识库：

- **Skill 与定义解耦**：3 个 skill 只剩算法，定义全在 note/SPEC.md
- **目录结构合理**：13 个新模块，主题聚类清晰
- **互链完整**：双向链接 + MOC 索引
- **SPEC.md 自描述**：每个目录有自己的规范

---

## 2. Goals & Non-goals

### Goals

1. **G1**：3 个 skill 重构后只剩算法流程，无 note 特定定义
2. **G2**：note 重构为 13 模块新结构（`note-temp/`）
3. **G3**：每个目录有 `SPEC.md` 自描述，继承上层规范
4. **G4**：跨模块主题用 MOC 串联，不用 tags
5. **G5**：核心概念原子化，综合主题用 MOC
6. **G6**：互链双向完整（避免单向孤岛）
7. **G7**：最后用 `note-temp/` 替换 `note/`

### Non-goals

- **NG1**：不改 git 历史（不重写 commit）
- **NG2**：不引入 frontmatter tag 系统（用 MOC 代替）
- **NG3**：不引入 Obsidian wikilinks（`[[topic]]`），只用 markdown 链接
- **NG4**：不做内容大改写（保留大纲 + 润色重写，不重写主旨）
- **NG5**：不删除旧 `note/`，直到 `note-temp/` 完全验证通过

---

## 3. 架构总览

```
note-temp/                          ← 新结构（实验场，最终替换 note/）
├── SPEC.md                         ← L0 全局规范
├── README.md                       ← L0 主导航
│
├── 01.java-and-jvm/                ← 13 个新模块
│   ├── SPEC.md                     ← L1 模块规范
│   ├── README.md                   ← L1 导航
│   └── 01-fundamentals/ ...
│
└── ...

skills/                             ← 重构后的算法骨架
├── note-health/
│   └── SKILL.md                    ← 仅含 4 相执行算法（无规则数据）
├── note-precipitation-planning/
│   └── SKILL.md                    ← 仅含 8 步流程 + Step 3.5 增强
└── note-knowledge-qa/
    └── SKILL.md                    ← 仅含 QA 检索流程
```

### 3.1 三层文件分工

| 文件 | 内容 | 谁读 |
|------|------|------|
| `README.md` | 导航 + 文章清单 | 人 |
| `index.md` | 多维导航（MOC） | 人 |
| `SPEC.md` | 内容规则 | **skill** |

### 3.2 skill 三件套闭环

```
沉淀 (note-precipitation-planning)
  ↓ 创建/更新 note + SPEC.md
  ↓
体检 (note-health)
  ↓ 按 SPEC.md 规则扫描 + 评分
  ↓
使用 (note-knowledge-qa)
  ↓ 检索 + 跨模块追踪
  ↓
发现缺口 → 回到沉淀
```

---

## 4. SPEC.md 架构

### 4.1 层级结构

```
L0: note-temp/SPEC.md
  ↓ inherits
L1: note-temp/<module>/SPEC.md
  ↓ inherits（可选）
L2: note-temp/<module>/<sub>/SPEC.md
```

### 4.2 SPEC.md 格式

```markdown
# SPEC for note-temp/01.java-and-jvm/

> **Inherits from**: [../../SPEC.md](../../SPEC.md)
> **Mode**: append + override（同 key 覆盖，差异追加）
> **Updated**: 2026-08-11

---

## 从 L0 继承（不重复，引用即可）

- G1-G6 通用 6 维度评分
- 11 类基础扫描规则
- commit 格式 (feat/fix/refactor...)
- frontmatter 规范 (module/question/story)
- 命名规范 ({nn}.{english}/)

---

## 本模块规则

### 模块定位
Java 语言 + JVM 原理 + 并发编程 + 设计模式。

### 评估维度（在 G1-G6 基础上追加）

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| A1 | 源码级深度 | 有源码片段 + WHY 注释 | 有代码但只解释 WHAT | 无代码 |
| A2 | 版本演进对比 | 有 JDK X vs Y 对比 | 提及差异但未展开 | 无版本意识 |
| A3 | ❌/✅ 反例对比 | 有正反例展示 | 只有正确用法 | 无对比 |
| A4 | 参数调优表 | 有实际参数 + 调优建议 | 有参数表无建议 | 无参数 |

### 写作要求
- 必须有源码片段
- 必须标注 JDK 版本
- 反模式用 ❌ 标识

### 子目录约定
- `01-fundamentals/` 语言基础
- `02-jvm/` JVM 原理
- `03-concurrency/` 并发编程
- `04-patterns/` 设计模式

### 互链要求
- 每篇文章必须链到父 README
- 至少 2 个跨模块链接
```

### 4.3 缺失 SPEC.md 的行为

skill 暂停，询问用户三选项：

```
⚠️ 未找到 note-temp/01.java-and-jvm/SPEC.md

如何继续？
A. 现在创建（skill 帮你生成 SPEC.md 模板）
B. 跳过（仅用 L0 全局规则继续）
C. 中止（你来手动创建后再跑）
```

L0（`SPEC.md`）缺失走同样流程。**不静默兜底**。

---

## 5. note-temp/ 目录结构

### 5.1 13 模块结构

```
note-temp/
├── SPEC.md                                # L0 全局规范
├── README.md                              # L0 主导航（MOC）
│
├── 01.java-and-jvm/                       # Java 语言 + JVM + 并发 + 设计模式
│   ├── SPEC.md
│   ├── README.md
│   ├── 01-fundamentals/                   # 语言基础
│   ├── 02-jvm/                            # JVM 原理
│   ├── 03-concurrency/                    # 并发编程
│   ├── 04-patterns/                       # 设计模式
│   └── ...
│
├── 02.cs-foundations/                     # 算法 + OS + 网络 + 数学
│   ├── SPEC.md
│   ├── README.md
│   ├── 01-algorithms/
│   ├── 02-os/
│   ├── 03-network/
│   └── 04-math/
│
├── 03.data-stack/                         # 数据库 + 缓存 + 大数据
│   ├── SPEC.md
│   ├── README.md
│   ├── 01-database/
│   ├── 02-cache/
│   ├── 03-queue/
│   └── 04-big-data/
│
├── 04.spring-backend/                     # Spring + 后端框架
│   ├── SPEC.md
│   ├── README.md
│   ├── 01-core/
│   ├── 02-boot/
│   ├── 03-cloud/
│   └── 04-ecosystem/
│
├── 05.frontend/                           # 前端
│   ├── SPEC.md
│   ├── README.md
│   ├── 01-basics/
│   ├── 02-frameworks/
│   └── 03-mobile/
│
├── 06.distributed-systems/                # 分布式 + 微服务 + 云原生
│   ├── SPEC.md
│   ├── README.md
│   ├── 01-theory/
│   ├── 02-patterns/
│   ├── 03-microservices/
│   └── 04-cloud-native/
│
├── 07.devops-and-tools/                   # CI/CD + 监控 + 工具
│   ├── SPEC.md
│   ├── README.md
│   ├── 01-ci-cd/
│   ├── 02-monitoring/
│   └── 03-tools/
│
├── 08.ai-foundations/                     # ML + DL + Transformer + LLM 基础
│   ├── SPEC.md
│   ├── README.md
│   ├── 01-ml/
│   ├── 02-deep-learning/
│   ├── 03-transformer/
│   ├── 04-llm/
│   └── 05-tokenization/
│
├── 09.ai-applications/                    # RAG + Agent + Prompt + LLM 推理
│   ├── SPEC.md
│   ├── README.md
│   ├── rag/                               # MOC: RAG 主题
│   │   ├── README.md
│   │   ├── 01-retrieval.md
│   │   ├── 02-rerank.md
│   │   └── ...
│   ├── agent/                             # MOC: Agent 主题
│   │   ├── README.md
│   │   └── ...
│   ├── prompts/
│   └── llm-inference/
│
├── 10.business-systems/                   # 电商 + 社交 + 金融
│   ├── SPEC.md
│   ├── README.md
│   ├── 01-ecommerce/
│   ├── 02-social/
│   └── 03-finance/
│
├── 11.product-and-pm/                     # 产品 + PM + 流程
│   ├── SPEC.md
│   ├── README.md
│   └── ...
│
├── 12.interview/                          # 面试题
│   ├── SPEC.md
│   ├── README.md
│   └── <by-topic>/                        # 按主模块组织面试题
│
└── 13.story/                              # 阿明餐厅
    ├── SPEC.md
    ├── README.md
    ├── index.md                           # 多维导航（现状保留）
    ├── cheatsheet.md
    ├── glossary.md
    └── 01-XX.md ~ 49-XX.md
```

### 5.2 内容来源映射

| 新模块 | 来源（旧 note/ 模块） | 文件数预估 |
|--------|---------------------|----------|
| 01.java-and-jvm | 01.java 全部 | ~112 |
| 02.cs-foundations | 02.computer-basics 全部 | ~42 |
| 03.data-stack | 03.database + 10.big-data | ~31 |
| 04.spring-backend | 06.spring 全部 | ~141 |
| 05.frontend | 09.front-end 全部 | ~54 |
| 06.distributed-systems | 04.system-design + 08.application-systems（架构部分） | ~155 |
| 07.devops-and-tools | 05.tools + 07.workflow | ~44 |
| 08.ai-foundations | 11.ai 的 ML/DL/Transformer 部分 | ~60 |
| 09.ai-applications | 11.ai 的 RAG/Agent/Prompt/推理部分 | ~130 |
| 10.business-systems | 08.application-systems 业务部分 | ~30 |
| 11.product-and-pm | 14.project-management | ~12 |
| 12.interview | 13.split-hairs 全部 | ~232 |
| 13.story | 12.story 全部 | ~54 |

### 5.3 内容重写程度（"保留大纲 + 重写"）

为避免 Phase 1 后用户问"重写到什么程度"，明确边界：

| 操作 | 允许 | 不允许 |
|------|------|--------|
| 章节结构 | 重组 / 删除冗余 / 合并 | 完全推翻重写 |
| 大纲 | 保留 / 微调 | 删减核心要点 |
| 表述 | 润色 / 修正错误 / 补全缺失 | 改写主旨 / 翻译 |
| 代码示例 | 保留 | 替换为不同语言实现 |
| 数据/数字 | 保留 + 校对 | 编造新数据 |
| 互链 | 重写时同步调整 | 保留断链 |

**原则**：保留原意（"事实"和"结论"不变），优化表达（"措辞"和"结构"可调）。

### 5.4 子目录原则

**主目录按概念**（如 `09.ai-applications/rag/`），**子目录按深度**（如 `09.ai-applications/rag/` 下用 `01-retrieval.md` 数字编号）。

**MOC 例外**：复杂主题用 MOC 目录 + 原子笔记。

---

## 6. Skill 重构

### 6.1 重构后的 SKILL.md 结构

每个 skill 的 SKILL.md 只剩**算法骨架**：

```markdown
# note-health（重构后）

> 规则来源：读 note-temp/SPEC.md + <module>/SPEC.md
> 算法：见下文 4 相执行

## 缺失 SPEC.md 行为
[三选项询问流程]

## Phase 1 — 结构扫描
[算法步骤]

## Phase 2 — Leaf 质量
[算法步骤]

## Phase 3 — 上卷
[算法步骤]

## Phase 4 — 报告
[算法步骤]
```

### 6.2 note-precipitation-planning 新增 Step 0.5（输入类型识别）+ Step 3.5

**Step 0.5：输入类型识别**（在原 Step 0 主题识别之前）：

```
Step 0.5: 输入类型识别
├─ 检测输入是 URL
│  └─ WebFetch 抓取 → 提取核心主题 → 走原 Step 0 → Step 1
├─ 检测输入是 markdown 文章（长文本 / 已有 frontmatter）
│  └─ 解析 frontmatter + 标题 + 章节 → 提取主题 → 走原 Step 0 → Step 1
├─ 检测输入含多主题（"5 个 X"、"A + B + C"、"X 系列"等模式）
│  └─ 原 Step 0 拆分流程
└─ 检测输入是单主题
   └─ 直接进入 Step 1
```

**Step 3.5：目录创建 / 更新决策**：

```
Step 3（位置决策）：
├─ 命中已有模块
│  └─ Step 3.5a：是否需要更新该模块 SPEC.md？
│     ├─ 内容超出当前 SPEC 覆盖范围 → 询问
│     └─ 完全在 SPEC 范围内 → 不询问
│
└─ 没找到匹配的模块
   └─ Step 3.5b：是否新建模块目录？
      ├─ 用户确认 → 创建 + 生成 SPEC.md 骨架
      └─ 用户拒绝 → 放在最相似模块下
```

**输入类型示例**：

| 用户输入 | 类型 | 处理 |
|---------|------|------|
| "我想沉淀 RAG" | 单主题 | 直接 Step 1 |
| "5 个 LLM 推理工程问题" | 多主题 | Step 0 拆分 |
| 粘贴一篇长文 markdown | 文章 | 解析 + 提取主题 |
| `https://arxiv.org/abs/...` | URL | WebFetch + 提取主题 |

### 6.3 关键删除

| 内容 | 处理 |
|------|------|
| 50+ 词硬编码映射表 | **删除**（用 grep 替代） |
| 14 模块列表 | **删除**（运行时扫目录） |
| 6 维度评分表 | **移到 SPEC.md** |
| 11 类扫描规则 | **移到 SPEC.md** |
| commit 格式 | **移到 SPEC.md** |

---

## 7. 迁移计划（分阶段）

### Phase 0：骨架（先做这个）

| 任务 | commit |
|------|--------|
| 创建 `note-temp/` 目录 | `chore: 创建 note-temp/ 实验目录` |
| 创建 `note-temp/SPEC.md`（L0 全局规范） | `feat(note-temp): 创建 L0 全局 SPEC.md` |
| 创建 13 个模块占位目录 | `feat(note-temp): 13 模块占位骨架` |
| 每个模块放 `SPEC.md`（初始模板）+ `README.md`（占位） | 合并上面 |

**Phase 0 产出**：note-temp/ 有完整 13 模块骨架，每个模块有 SPEC.md + README.md。

### Phase 1：11.ai 试点（最关键）

| 任务 | commit |
|------|--------|
| 设计 `08.ai-foundations/` 子目录结构 | `feat(note-temp): 08.ai-foundations 子目录设计` |
| 迁移 ML / DL / Transformer 内容 | `feat(note-temp): 08.ai-foundations 迁移 ML/DL/Transformer` |
| 迁移 LLM 基础（Tokenization/Embedding） | `feat(note-temp): 08.ai-foundations 迁移 LLM 基础` |
| 填实 `08.ai-foundations/SPEC.md` | `feat(note-temp): 08.ai-foundations/SPEC.md 填实` |
| 设计 `09.ai-applications/` 子目录结构（含 MOC） | `feat(note-temp): 09.ai-applications 子目录设计` |
| 迁移 RAG 主题（MOC 模式） | `feat(note-temp): 09.ai-applications 迁移 RAG` |
| 迁移 Agent / Prompt / 推理 | `feat(note-temp): 09.ai-applications 迁移 Agent/Prompt/推理` |
| 填实 `09.ai-applications/SPEC.md` | `feat(note-temp): 09.ai-applications/SPEC.md 填实` |

**Phase 1 产出**：08 + 09 完整迁移，验证 SPEC.md / MOC / 互链 / 原子化机制。

**Phase 1 验证**：
- 跑 note-health 在 `08.ai-foundations/` 上，看 SPEC.md 规则是否生效
- 跑 note-knowledge-qa 提问"什么是 RAG"，看是否能从 `09.ai-applications/rag/` 检索
- 跑 note-precipitation-planning 模拟沉淀新主题（如 "MCP 协议"），看 Step 3.5 是否正确触发

### Phase 2：基础模块迁移（01-03）

| 任务 | commit |
|------|--------|
| 迁移 01.java-and-jvm | `feat(note-temp): 01.java-and-jvm 完整迁移` |
| 迁移 02.cs-foundations | `feat(note-temp): 02.cs-foundations 完整迁移` |
| 迁移 03.data-stack | `feat(note-temp): 03.data-stack 完整迁移` |

### Phase 3：中间模块迁移（04-07）

| 任务 | commit |
|------|--------|
| 迁移 04.spring-backend | `feat(note-temp): 04.spring-backend 完整迁移` |
| 迁移 05.frontend | `feat(note-temp): 05.frontend 完整迁移` |
| 迁移 06.distributed-systems | `feat(note-temp): 06.distributed-systems 完整迁移` |
| 迁移 07.devops-and-tools | `feat(note-temp): 07.devops-and-tools 完整迁移` |

### Phase 4：应用模块迁移（10-11）

| 任务 | commit |
|------|--------|
| 迁移 10.business-systems | `feat(note-temp): 10.business-systems 完整迁移` |
| 迁移 11.product-and-pm | `feat(note-temp): 11.product-and-pm 完整迁移` |

### Phase 5：职业模块迁移（12-13）

| 任务 | commit |
|------|--------|
| 迁移 12.interview | `feat(note-temp): 12.interview 完整迁移` |
| 迁移 13.story | `feat(note-temp): 13.story 完整迁移` |

### Phase 6：Skill 重构

| 任务 | commit |
|------|--------|
| 重构 note-health/SKILL.md（精简 + 读 SPEC.md） | `refactor(skills): note-health 重构为算法骨架` |
| 重构 note-precipitation-planning/SKILL.md（含 Step 3.5） | `refactor(skills): note-precipitation-planning 重构 + Step 3.5` |
| 重构 note-knowledge-qa/SKILL.md | `refactor(skills): note-knowledge-qa 重构` |
| 删除 skills/note-health/references/（内容已迁 SPEC.md） | `chore(skills): 删除 note-health/references/` |

### Phase 7：旧文件清理

| 任务 | commit |
|------|--------|
| 删除 note/CONTRIBUTING.md（内容已并入 SPEC.md） | `chore: 删除 CONTRIBUTING.md（已并入 SPEC.md）` |
| 删除 note/12.story/STORY-FORMAT-SPEC.md（已并入 13.story/SPEC.md） | `chore: 删除 STORY-FORMAT-SPEC.md` |
| 删除 note/13.split-hairs/QUESTION-FORMAT-SPEC.md | `chore: 删除 QUESTION-FORMAT-SPEC.md` |

### Phase 8：替换 note/

| 任务 | commit |
|------|--------|
| 最终验证 note-temp/ 完整性 | - |
| 全库 broken links 检查 | - |
| **策略 A（推荐）**：`rm -rf note/ && mv note-temp/ note/` | `feat: note-temp/ 重命名为 note/` |
| 策略 B（备选）：逐文件 `git mv note-temp/X → note/X`，再删除 note/ 残留 | `feat: note-temp 内容迁入 note/` |

**Phase 8 选策略 A**：物理重命名更快，commit 历史清晰（一次大 rename + 后续小调整）。**先**用 `git tag v1-pre-note-restructure` 标记当前状态做快照，**再**执行替换，**最后**跑全库 link-check + skill 回归测试。

---

## 8. 决策日志（本次 session 已确定）

| # | 决策 | 选择 | 理由 |
|---|------|------|------|
| 1 | 模块数量 | D 完全自由 | 用户决定 |
| 2 | 模块内部结构 | D 混合（主按概念，子按深度） | 灵活 |
| 3 | 互链机制 | B 只用 markdown | 明确 |
| 4 | 原子化程度 | C 混合（核心原子化，综合保留整篇） | 灵活 |
| 5 | 标签系统 | C 用 MOC 代替 | 可控 |
| 6 | 试点策略 | C 先做 11.ai（拆 08 + 09） | 验证后推广 |
| 20 | 输入类型 | 4 种（单主题/多主题/文章/URL） | 用户补充 |
| 7 | SPEC.md 命名 | B 短名 `SPEC.md`（全局也用 SPEC.md） | 统一 |
| 8 | INDEX.md | A 不强制，按需 | 12.story 模式 |
| 9 | 继承机制 | C 显式 + 隐式双保险 | 鲁棒 |
| 10 | L0 `SPEC.md` 范围 | C 仅 6 维度 + 11 扫描（其他散各模块 SPEC.md） | 极简 L0 |
| 11 | 现有 SPEC.md 处理 | B 重写为统一格式 | 一致 |
| 12 | CONTRIBUTING.md | B 合并到 SPEC.md，删除 | 单一来源 |
| 13 | L2 子模块 SPEC | A 仅当子模块有强特异性时 | 按需 |
| 14 | SPEC.md frontmatter | C 无 frontmatter | 避免污染 |
| 15 | 迁移顺序 | A 一次性迁移 3 个 skill | 同步 |
| 16 | 缺失 SPEC.md 行为 | 三选项（创建 / 跳过 / 中止） | 交互 |
| 17 | references/ 内容 | A 全部移到 note/ | 彻底解耦 |
| 18 | note-temp → note | 替换 | 最终目标 |
| 19 | 阶段跨度 | 分阶段 | 可控 |

---

## 9. 风险与缓解

| 风险 | 缓解 |
|------|------|
| 内容迁移遗漏 | 用 find + 对比表逐模块核对 |
| 互链断裂 | 每个迁移阶段后跑 broken links 检查 |
| SPEC.md 不一致 | Phase 0 先定全局模板，Phase 1 验证后冻结 |
| Skill 在新结构失效 | Phase 1 跑全流程验证，Phase 6 才重构 skill |
| 替换 note/ 后回滚困难 | Phase 8 前用 git tag 标记 note-temp 完整快照 |

---

## 10. 后续可能讨论点（不在本次范围）

- MOC 与 frontmatter tag 的最终权衡（已决定用 MOC）
- 是否引入 Obsidian wikilinks（已决定不用）
- 子模块 SPEC.md 的具体触发条件（Phase 1 验证后定）
- 内容重写的具体程度（Phase 1 试点后定）
- Skill 缺失 SPEC.md 时的"自动生成"模板内容（Phase 6 才需要）

---

## 11. 验证清单（Phase 8 前必过）

- [ ] 13 模块 SPEC.md 全部填实
- [ ] 所有模块 README.md 有导航表
- [ ] 复杂主题（08/09/13）有 MOC
- [ ] 全库 broken links = 0
- [ ] 3 个 skill 在新结构上跑通全流程
- [ ] 缺失 SPEC.md 时询问流程正常
- [ ] note-precipitation-planning 的 Step 3.5 正常触发
- [ ] 数字一致性校对通过（find 校对）
