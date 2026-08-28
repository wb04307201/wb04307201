---
name: note-precipitation-planning
description: Use when user asks where to add or update a topic in the project's note/ knowledge base / "X 应该沉淀到 note 什么位置" / "X 怎么归档" / "放在 note 哪个位置" / "如何沉淀 X" / "新增主题到 note" — covers survey of existing structure (read at runtime), depth analysis, location decision between main module / 12.interview interview layer / 13.story narrative layer, layered precipitation strategy, and reverse-link verification
---

> **规则来源**：执行前必读 `note/SPEC.md`（G1-G6 通用评分 + 11 类扫描 + commit 格式 + 互链规则 + §7 SPEC 分层）以及目标模块的 `<module>/SPEC.md`（如 `note/01.java-and-jvm/SPEC.md`）。**若目标模块有强骨架规范**（如 `note/12.interview/QUESTION-FORMAT-SPEC.md` / `note/13.story/STORY-FORMAT-SPEC.md`），同时必读 `<module>/*-FORMAT-SPEC.md`。模块结构在运行时通过 `find note -maxdepth 1 -type d` + `cat note/<module>/README.md` 读取，不硬编码。

# note 沉淀规划

## 核心原则：**避免新文件成孤岛**

**任何新增 README 必须满足 3 个互链条件**，缺一即视为"孤岛"：

1. **新文件 → 旧章节**：新文件至少链接 2 个旧章节（避免"不知道放在哪")
2. **旧章节 → 新文件**：被链接的旧章节必须有**反向链接**（避免"单向链接")
3. **父 README / 总目录 → 新文件**：父目录 README / 总目录表 必须添加新文件链接（避免"父不知道有新成员")
4. **系列内兄弟互链**：当向已有系列添加新文章时，新文件**必须链向系列内所有已有兄弟**，且**所有已有兄弟必须回链新文件**（避免"同系列但互不知道"）

> **反直觉 1**：很多人以为"我加了反向链接就完事" —— 但**总目录扫描**经常漏掉。新文件链接了 11.ai/README.md，但 11.ai/README.md 没在目录表里加新文件 → **总目录是孤岛**。
>
> **反直觉 2**：Mistake 9 覆盖了 parent ↔ child 的反向链，但**同系列兄弟**之间是另一个维度。例如 agent-execution-patterns 有 01-react / 02-plan-execute，但 01 和 02 的文件末尾**没有链向** 03 和 04 —— 它们只链回 README。正确做法：每篇文件末尾加"系列导航表"，链向系列内所有其他文件。

## Overview

当用户问"这个主题应该新增/更新到 note 的什么位置"时，遵循 8 步流程输出沉淀方案。`note/` 是 13 主模块的体系化技术知识库，含 `01.java-and-jvm` ~ `11.product-and-pm`，每个主模块有 README + 子目录 + 已建立的双层/三层沉淀模式（13.split-hairs 面试题 + 11.ai 主模块 + 12.story 餐厅叙事）。

> 🆕 **Step 0 新增（2026-07-26 教训）**：用户输入可能是**多个主题**（如"大模型思维工程 5 个灵魂拷问"实际包含 5 个独立子主题）。Step 0 在盘点前先识别并拆分多主题，避免把 N 个独立主题错误合并成一个文件。历史案例：`production-thinking-5q` 把思维范式/成本控制/一致性/超时熔断/监控 5 个独立主题合成一个 419 行文件，后续不得不全部拆散。

> 🆕 **Step 0 强化（2026-08-10 教训）**：**多主题拆分**判定信号——当用户输入主题**包含 ≥3 个互不相关子题**且每个子题都合格，**单文件综述违反 split-hairs 单点深挖定位**。判定 checklist：
> - [ ] 文件覆盖 ≥3 个互不相关子主题？（"X 是什么"、"X 6 大"、"X 综述" 类标题）
> - [ ] 每个子主题都有自己的 30s/90s 话术？（合并文件通常每节都有完整话术模板）
> - [ ] 任一项 Yes → 拆分为多个 single-topic 文件，每个子题独立 frontmatter
>
> 历史案例：`split-hairs/02.computer-basics/machine-learning/README.md` 把 K-means / 决策树 / 梯度下降 / PCA / Boosting / 评估指标 6 大算法合成一个 126 行综述，每个算法都有完整 30s/90s 话术。已拆分为 6 个 single-topic deep-dive（每篇 146-293 行）。

## Quick Example

```
用户：我想加 "Claude Code Skills" 章节，怎么沉淀？
   ↓
skill 执行：Step 1 现状盘点 → Step 2 深度评估 → Step 3 位置决策 → Step 4 方式 → Step 5 选项
   ↓
输出（节选）：
  ## 📋 现状盘点
  - note/07.devops-and-tools/claude-code.md：已有但只覆盖 CLI 命令
  - note/08.ai-foundations/03-engineering/agent-frameworks/：相邻分类
  - 已有 3 篇 SPL（single page lesson）：SPL-2024-089/-091/-101

  ## 🎯 深度评估（3 信号）
  - 高频：✅ 多家公司在用（Anthropic 官方推）
  - 内容深：✅ ≥4 层面（架构/SKILL.md 协议/工具生态/实战）
  - 缺口真实：✅ note 当前只覆盖用法，未覆盖 SKILL.md 协议本身

  ## 💡 位置 + 方式
  - 推荐：双层 + 11.ai 联动（推荐项 A）

  ## ❓ 选项
  A. 双层沉淀 + Claude Code 协议层深度（推荐）→ 3 commit
  B. 只动 Skills 协议专题（最小改动）→ 1 commit
  C. 暂不沉淀

不同点：不直接动手 — 先盘点 + 给 2-4 选项让用户决策
```

## When to Use

**Use when**：
- 用户问"X 应该沉淀到 note 的什么位置？"
- 用户问"如何在 note 里新增/更新 X 主题？"
- 用户提供主题 + 问"放在 note 哪个位置合适？"

**Don't use when**：
- 用户已知具体位置（如"在 06.spring 加 Spring Boot 3.5 新特性"）→ 直接实施
- 用户问"note 的现状" → 直接展示，不需要沉淀规划
- 用户问"note 的整体结构" → 直接展示 README
- 用户问"修复 X 文件" → 直接修复，不需要规划

## Project Context（必读）

**note 目录位置**：仓库根目录的 note/（CWD 假设 = 项目根）

**13 主模块**：
- `01.java` / `02.computer-basics` / `03.database` / `04.system-design`
- `05.tools` / `06.spring` / `07.workflow` / `08.application-systems`
- `09.front-end` / `10.big-data` / `11.ai` / `12.story`
- `13.split-hairs` / `14.project-management`

**3 大沉淀模式**（每次都问用哪个）：

| 模式 | 适用 | 落地位置 |
|------|------|---------|
| **单文件** | 内容 < 150 行 或 极专一 | 主模块子 README / 13.split-hairs/XX/ |
| **双层沉淀**（最常用）| 面试高频 + 需深度原理 | 13.split-hairs/<topic> + 11.ai/<module>/<topic> + 互链 |
| **三层 + 12.story 联动** | 重要主题 + 有餐厅叙事价值 | 双层 + 12.story 加章节反向链 |

## 8 步核心流程

### Step 0: 主题识别与拆分（必做，第一步）

**目的**：避免多主题错误合并成一个文件（2026-07-26 历史教训：`production-thinking-5q` 把 5 个独立主题合成 419 行文件）

**判断逻辑**：

```text
用户输入包含多个独立概念？
├─ 有编号（"5 个灵魂拷问"、"3 大模式"、"N 种方案"） → 多主题
├─ 有并列（"A + B + C"、"A / B / C"、"A、B、C"） → 多主题
├─ 有"和"、"与"、"以及"连接不同领域主题 → 可能多主题
├─ 用户提到"N 个"、"几种"、"系列" → 多主题
└─ 单一概念（"RAG"、"分布式锁"、"HashMap"） → 单主题
```

**多主题时的进一步判断**：

```text
多主题识别后，判断关联强度：
├─ 强关联（同一框架的不同维度，如"LLM 生产稳定性 5 问"）
│   → 创建系列目录，每个子主题独立成文
│   → 例：llm-production-thinking/ 目录下 01-06 独立子文件
│   → 面试题也要各自独立（不要合成一个"5q"文件）
│
├─ 弱关联（只是同时提到，如"RAG + Redis 缓存 + 限流"）
│   → 各自独立沉淀，互不依赖
│   → 每个主题走独立的 Step 1-7 流程
│
└─ 部分关联（核心主题 + 边缘子话题）
    → 核心主题沉淀为主文件，边缘子话题作为章节或链接
```

**输出格式**（多主题时）：

```markdown
## 🔍 Step 0: 主题识别

识别到 **N 个独立子主题**：

| # | 子主题 | 关联强度 | 建议沉淀方式 |
|---|--------|---------|-------------|
| 1 | 思维范式（Prompt vs if-else） | 强关联（系列成员） | 独立面试题 + 系列子文件 |
| 2 | 成本控制（5 层路由） | 强关联（系列成员） | 独立面试题 + 系列子文件 |
| ... | ... | ... | ... |

**关联判断**：强关联 → 建议创建系列目录，各子主题独立成文
**面试题处理**：每个子主题各自独立一篇面试题（不要合并）
```

**单主题时**：直接进入 Step 1。

### Step 0.5: 上下文预算评估（多主题时必做）

> 🆕 **2026-07-26 教训**：一次沉淀 3 个主题（Structured Output + Planning/Acting/Monitoring + Skill 命中率）后，上下文被占满 → compact → 后续工作需手动恢复。多主题沉淀必须评估上下文消耗。

**触发条件**：Step 0 识别到 **≥ 2 个独立子主题**时，必做 Step 0.5。

**复杂度评估**（每个子主题）：

| 因素 | 权重 | 说明 |
|------|------|------|
| 沉淀模式 | 单文件=1 / 双层=2 / 三层=3 | 双层涉及 2 个文件 + 2-3 个 commit |
| 父 README 更新数 | 每更新 1 个 +0.5 | 如 13.split-hairs/11.ai/README.md + 主模块 README |
| 反向链复杂度 | 简单=0 / 中等=0.5 / 复杂=1 | 跨模块链接需路径验证 |
| 系列导航表 | 需要=1 / 不需要=0 | 向已有系列新增时需更新所有兄弟 |

**复杂度分级**：
- **简单主题**（总分 ≤ 2）：单文件 + 少量反向链
- **中等主题**（总分 2.5-4）：双层沉淀 + 2-3 个父 README 更新
- **复杂主题**（总分 ≥ 4.5）：三层沉淀 + 系列导航表 + 跨模块链接

**单次沉淀上限**：

| 场景 | 建议上限 | 理由 |
|------|---------|------|
| 全简单主题 | ≤ 3 个 | 每个 ~500 行上下文，总计 ~1500 行 |
| 混合（简单+中等） | ≤ 2 个 | 避免超过 2000 行上下文 |
| 全中等主题 | ≤ 2 个 | 每个 ~800 行上下文，总计 ~1600 行 |
| 含复杂主题 | **分批**（每次 1 个） | 复杂主题可能 > 1000 行上下文 |

**输出格式**（多主题时）：

```markdown
## 🔍 Step 0.5: 上下文预算评估

| # | 子主题 | 复杂度 | 预估上下文消耗 | 建议批次 |
|---|--------|--------|--------------|---------|
| 1 | Structured Output | 中等（2.5） | ~800 行 | Batch 1 |
| 2 | Planning/Acting/Monitoring | 中等（3） | ~900 行 | Batch 1 |
| 3 | Skill 命中率 | 简单（1.5） | ~500 行 | Batch 2（如需要） |

**建议**：先沉淀 Batch 1（2 个中等主题），compact 后再处理 Batch 2。
```

**分批执行协议**：
1. **Batch 1**：沉淀前 1-2 个主题 → commit → 验证 → 输出总结
2. **主动提示用户**："Batch 1 完成。是否继续 Batch 2？（建议先 compact 再续）"
3. **Batch 2+**：用户确认后 → compact → 从 git log 恢复进度 → 继续

### Step 1: 现状盘点（必做，不能跳过）

**目的**：避免重复沉淀、找到补充位置、识别已有结构

**操作**：
```bash
# 1.1 关键词搜索
cd "$(git rev-parse --show-toplevel)"
grep -rl "<关键词>" note/ | head -10

# 1.2 主题目录扫描（如 RAG / Transformer / Memory）
find note/<module> -type d -name "*<topic>*" 2>/dev/null
ls note/<module>/

# 1.3 13.split-hairs 同栏目兄弟
ls note/12.interview/<module>/ | grep -v README

# 1.4 12.story 相关章节
grep -l "<关键词>" note/13.story/*.md 2>/dev/null

# 1.5 系列结构检查（目标目录下是否已有编号系列）
# 如果目标目录下有 01-xxx.md / 02-xxx.md 等编号文件，
# 说明是"系列"，新增文章时必须补全系列内互链
ls note/<target-dir>/[0-9]*.md 2>/dev/null
# 如果找到编号文件 → 新文章需要：
#   a. 末尾加"系列导航表"（链向所有兄弟）
#   b. 所有已有兄弟末尾加/更新"系列导航表"（链向新文件）

# 1.6 总目录入口验证（防"总目录孤岛"，对应反直觉 1）
# 原理：新文件链到主模块 README，但主模块 README 没在目录表里反向列新文件 →
#       用户从父 README 读，根本不知道有这个子章节
# 输出：每个新文件必须在目标模块 README + note/README.md 总目录都登记
TARGET_README="note/<target-module>/README.md"
NEW_FILE="note/<target-module>/<topic>.md"
NEW_BASE=$(basename "$NEW_FILE" .md)
echo "=== 总目录入口验证 ==="
if [ -f "$TARGET_README" ] && ! grep -q "\[$NEW_BASE\]" "$TARGET_README" 2>/dev/null; then
  echo "  ⚠  $NEW_FILE 未在 $TARGET_README 目录表中登记（总目录孤岛）"
  echo "      修复：在 $TARGET_README 加一行 [标题](相对路径)"
fi
if [ -f "note/README.md" ] && ! grep -q "<target-module>" "note/README.md" 2>/dev/null; then
  echo "  ⚠  目标模块 <target-module> 未在 note/README.md 总目录出现"
fi

# 1.7 计划阶段预检（commit 前的 sanity check，避免进入 Step 6 后才发现）
# 输出：PASS / FAIL + 修复清单
echo "=== Step 1 预检清单 ==="
echo "  □ 关键词已 grep（1.1）"
echo "  □ 主题目录已扫（1.2）"
echo "  □ 13.split-hairs 兄弟已列（1.3）"
echo "  □ 12.story 联动已查（1.4）"
echo "  □ 系列结构 / 总目录入口已查（1.5 + 1.6）"
echo "  □ 同模式范例已对照（1.8 🆕）"
echo "  □ Bonus 修复同源错误已 grep（1.9 🆕）"
```

# 1.8 同模式范例对照（先例优先 — 🆕 2026-08-28 沉淀实战新增）
# 目的：避免"双层推荐"被用户挑战 —— 当已有同模式面试题 3+ 篇时，**默认单面试题版**比双层更聚焦
# 操作：
ls note/12.interview/<module>/ | grep -E "troubleshooting|incident|故障|排查" | head -10
# 统计先例行数（单面试题 troubleshooting 类通常是 200-450 行）
for f in note/12.interview/<module>/*/README.md; do
  if grep -q "troubleshooting\|排查\|故障" "$f"; then
    echo "$(wc -l < "$f") $f"
  fi
done | sort -n

# 判定：
#   - troubleshooting 类先例 ≥ 3 篇且单篇 200-450 行 → 默认单面试题版（不双层）
#   - 没有先例或先例很少 → 走原 Step 4 决策树

# 1.9 Bonus 修复同源错误 grep（沉淀前主动检查 — 🆕 2026-08-28 新增）
# 目的：沉淀新案例时，主动 grep 现有文件是否有同源反直觉错误（同一错误示范）
#       如 2026-08-28 metaspace-tuning 沉淀时，发现 jvm-memory-pitfall:370 样例代码也缺 MetaspaceSize
# 操作：
#   grep -rn "<本案例核心反直觉点关键词>" note/
#   例：grep -rn "MaxMetaspaceSize" note/ | grep -v "MetaspaceSize"  # 找只设上限不设初始值的同源错误
# 判定：
#   - 找到 1 处同源错误 → 顺手修复为单独 fix(note) commit（追加到本次沉淀的 commit 计划）
#   - 找到 2+ 处 → 评估是否批量修复（可能升级为单独任务）

**输出**：5-10 个相关文件 + 每个文件的"覆盖深度"评估（"已有详细"/"一笔带过"/"完全缺失"）+ **总目录验证结果**+ **同模式先例行数对照表** + **Bonus 修复候选清单（如有）**

### Step 2: 深度评估（值得沉淀吗？）

**值得沉淀的 3 个信号**：
1. **高频**（面试常考 / 实际生产常见）
2. **内容足够深**（4 个层面以上 + 5 个反模式 + 实战案例）
3. **缺口真实**（现有内容一笔带过 / 完全缺失 / 内容错误）

**不值得沉淀的信号**：
- 一句话就能讲清（如"什么是 HashMap"）
- 已有 5+ 重复内容
- 用户场景明确不需要

### Step 3: 位置决策（用决策树）

```
用户场景是什么？
├─ 面试题 → 13.split-hairs/<module>/<topic>.md
├─ 深度原理 → 11.ai/<module>/<topic>.md（或其他主模块）
├─ 餐厅叙事 → 12.story/<topic>.md（前传/续集/番外）
└─ 实战框架 → 11.ai/03-engineering/ai-platforms/<framework>.md
```

**特殊位置判断**：
- 架构/模式 → 主模块的 `04-architecture/` 或 `02-technology-stack/` 子目录
- 框架对比 → 主模块的 `03-engineering/ai-platforms/`
- 算法原理 → 主模块的 `01-fundamentals/` 或 `02-technology-stack/`
- 面试 Q&A → `13.split-hairs/<module>/<topic>.md`

### Step 4: 沉淀方式决策（用决策树）

```
主题深度？
├─ < 100 行内容 → 单文件（1 commit）
├─ 100-300 行 + 面试价值 → 双层沉淀（2 commit）
└─ 300+ 行 + 已有餐厅叙事相关章节 → 三层 + 12.story 联动（3+ commit）

目标模块有无强骨架规范（L1.5）？
├─ 12.interview → 必读 `QUESTION-FORMAT-SPEC.md`（30s/90s 话术 + 追问模板），新文章必含 ## 引子/## 追问
├─ 13.story → 必读 `STORY-FORMAT-SPEC.md`（编号 + 章节骨架 + 系列定位块 + 文末回链）
└─ 其他模块 → 当前无 L1.5；如本主题需强制骨架，**新建** `*-FORMAT-SPEC.md`（评估维度仍放 SPEC.md）

🆕 2026-08-28 经验补充：先例对照覆盖决策（基于 §1.8 同模式先例盘点）
├─ 同栏目 troubleshooting 类先例 ≥ 3 篇 + 用户输入是生产 Bug 案例 → **默认单面试题版**（不双层）
│   例：cpu-spike-troubleshooting / full-gc-troubleshooting / no-class-def-found-troubleshooting
│       都是 189-430 行单面试题，已足够承载排查方法论 + 反直觉点 + 90 秒话术
│   反模式：硬塞双层（主模块深读 800+ 行 + 面试题 200 行）→ 主模块过载 + 面试题泛化
├─ 同栏目无先例 + 内容跨多领域（如 Maven + JVM + 容器） → 拆分为多个单面试题
│   各自独立成文 + 互链（同 Mistake 16 多主题拆分）
└─ 内容是理论/原理（非生产 Bug 案例） → 走原 Step 3 决策树（主模块深读 / 双层）
```

**双层沉淀模板**（遵循 `note/CONTRIBUTING.md` §3 commit 规范：`<type>(note): <scope-detail> - <描述>`）：
```
Commit 1: feat(note): 13.split-hairs/<module> - 新增'<topic>'面试题 + 陷阱表
Commit 2: feat(note): <module> - 新增'<topic>'深度原理（含源码分析）
```

**三层沉淀模板**：
```
Commit 1: feat(note): 13.split-hairs/<module> - 新增'<topic>'面试题
Commit 2: feat(note): <module> - 新增'<topic>'深度原理
Commit 3: refactor(note): <related-chapter> - 加反向链（指向新文件）
```

**commit 类型说明**（与 CONTRIBUTING §3 一致）：
| 类型 | 用途 | 例子 |
|------|------|------|
| `feat(note)` | 新增章节/文章 | `feat(note): 11.ai - 新增 Claude Code Skills 章节` |
| `fix(note)` | 修复/数字校对/断链 | `fix(note): 12.story - 数字统一 46→47` |
| `refactor(note)` | 结构/反向链/结构调整 | `refactor(note): 04.system-design - PNG→Mermaid 迁移` |
| `style(note)` | 润色/模板清理 | `style(note): 13.split-hairs - 引子格式统一` |
| `docs(note)` | 文档/CONTRIBUTING 同步 | `docs(note): 同步 CONTRIBUTING §3 commit 规范` |
| `chore(note)` | 回链/琐事 | `chore(note): 13 主模块补文末回链` |

> **统一性检查**：所有 commit 必须用 `feat/fix/refactor/.../chore(note)` 形式（仓库统一 scope = `note`），不要用 `feat(11.ai)` 这种过细的 scope。

### Step 5: 选项呈现（用 AskUserQuestion，orchestrator 执行）

**关键**：如果作为 subagent 执行，**不能直接调 AskUserQuestion**，必须返回选项让 orchestrator 转交。

**选项呈现要点**：
1. **2-4 个选项**，每个选项 1-2 句说明
2. **推荐项放第一个** + 标注"(推荐)"
3. **每个选项要能独立执行**（不要有"以上全部"这种依赖项）
4. **不要列 16 种组合**（如 4×4 维度相乘）——会让用户决策瘫痪

**错误示例**：
```
A1 A2 A3 A4  ×  B1 B2 B3 B4  =  16 种组合
```

**正确示例**：
```
A. 双层沉淀 + 完整主模块推导（推荐）
B. 只动面试深挖版（最小改动）
C. 双层 + 联动（最完整）
D. 暂不沉淀
```

### Step 5.5: 知识丰富度评估（条件触发网络搜索）

**目的**：在实施前判断是否需要补充外部知识，避免"用过时/不足的知识写文章"。

**触发条件**（满足任一 → 执行 WebSearch）：

| 信号 | 说明 | 示例 |
|------|------|------|
| **快速演进领域** | AI / 云原生 / 框架版本等半年内可能变化的主题 | "大模型 JSON 输出"、"分层路由" |
| **深度缺口** | Step 1 扫描发现现有内容 < 20 行（几乎空白） | "统一权限系统设计"（note 中完全缺失） |
| **用户明确要求** | 用户说"搜索网络知识"或"给我最新方案" | "要是你的知识支持…你可以搜索网络" |
| **模型不确定** | 对主题的具体实现细节、最新 API、框架版本不确定 |  unsure about latest Spring Boot version |

**不触发条件**（直接用模型知识写）：

| 信号 | 说明 | 示例 |
|------|------|------|
| **经典 CS 知识** | 数据结构 / 算法 / 语言特性 / OS 原理 | StringBuilder、try-catch、虚拟线程 |
| **增量补充** | 现有内容 > 100 行，只需追加 | 约定优于配置（已有 12 模式速查表） |
| **面试八股文** | 答案稳定、不随时间变化 | 死锁排查、Redis 单线程 |

**执行流程**（当触发时）：

```
1. WebSearch("<topic> <year> best practice / architecture")
2. 筛选 3-5 篇高质量结果（优先：官方博客 > 论文 > 技术博客）
3. 提取：最新方案 / 框架对比 / 反模式 / 生产数据
4. 与模型知识合并 → 写文章时标注"参考来源"章节
```

> **抓取受阻 fallback**（企业网络/沙箱常见）：`WebFetch` 可能因企业策略拦截官方文档域名（如实测 `github.github.com` 被 WebFetch 拒但可访问）。此时按序降级：
> 1. `chrome-devtools` MCP `navigate_page` **重试**（首次超时常可二次成功）+ `evaluate_script` 取 `document.body.innerText`
> 2. `bing-search` MCP 搜索 → `crawl_webpage` 抓取高质量二手深度文（如掘金/InfoQ 深度对比）交叉核实
> 3. 用户已在 prompt 中提供的权威命令/参数列表 = 一手依据
> **务必**：二手来源核实的关键语义（如某命令的迭代循环行为）要在文末「参考来源」标注来源级别，并提示用户对照官方复核存疑点。

**5 个领域 query 模板**（按主题套用）：

| 领域 | Query 模板 | 示例 |
|------|----------|------|
| **AI / LLM** | `<topic> <year> benchmark / comparison` | `DPO vs RLHF 2026 best practice` |
| **Spring / Java 框架** | `<topic> <version> release notes / migration` | `Spring Boot 3.5 new features` |
| **云原生 / DevOps** | `<topic> <year> production deployment` | `Kubernetes Gateway API 2026 production` |
| **数据库 / 缓存** | `<topic> vs <alternative> benchmark` | `Redis vs DragonflyDB 2026 benchmark` |
| **架构 / 设计** | `<topic> <year> architecture pattern` | `RAG vs Long Context 2026 architecture` |

**筛选优先级**：官方博客（*.<vendor>.com） > arXiv 论文 > InfoQ/DZone/Medium 技术博客 > 个人博客

**文章中的体现**：
- 末尾增加 `## 📚 参考来源` 章节，列出搜索到的 3-5 篇参考文章（含 URL + 一句话说明）
- 正文中引用的具体数据/方案标注来源

### Step 6: 实施（dispatch subagent）

#### ⚠️ Step 6.0 关键决策：内容驱动 vs lesson 映射（2026-08-14 教训）

**核心原则**：**按内容主题分类，不要按 lesson 编号机械复制**。

```
用户输入是 → 实施策略选择：
├─ 已有结构化目录（lesson1/, lesson2/, ...）
│   ├─ 内容主题统一（整个 lesson 是同一主题）
│   │   → 按 lesson 复制即可（如 lesson11 整体是"AI 代码安全"）
│   └─ 内容主题分散（一个 lesson 跨多个主题，如 lesson7 含 Claude/Codex/OpenCode/MCP）
│       → 必须**按文件内容**分发到不同子目录
│       → 同一 lesson 的不同 .md 可能去不同位置
│
└─ 无结构化目录（散落的 .md 文件）
    → 必须**先做内容分析**，按主题分类
    → 不要按文件名/日期随便映射
```

**判断方法**：
1. 读每个文件的 `# 标题` + 第一段
2. 提取主题关键词（如 "MCP"、"Spring 安全"、"jailbreak"）
3. 按关键词决定目标子目录
4. 同一 lesson 不同文件可去不同目标（lesson 是**课程编排**，不是**内容分类**）

#### ⚠️ Step 6.1 深度重组（2026-08-14 教训·必做·不询问用户）

**核心原则**：沉淀 ≠ cp -r。沉淀必须做 **3 类主动整理**：

```
1. 合并（merge）
   ├─ 场景：同主题有 ≥2 篇文件（如 Tony Kipkemboi 推文 + Harness 2026 文章都讲"概念"）
   ├─ 操作：选最长/最权威的为基准，其余合并入主文
   ├─ 必须保留所有原始引用 + 来源标注
   └─ 禁止：留 2 篇同主题文件让用户自己选

2. 拆分（split）
   ├─ 场景：单篇 ≥ 500 行且 H2 ≥ 8 且涵盖 ≥ 2 独立主题
   ├─ 操作：按 H2 主题切分 → 多个 single-topic 文件
   └─ 判定信号：见 Mistake "多主题错误合并"

3. 错位修正（relocate）
   ├─ 场景：文件内容主题与所在目录的父 README 定位不符
   │   例：harness-cybernetics/ 下的"OpenAI Codex 零人工编码"应在 coding-agents/codex/
   ├─ 操作：移动文件到正确目录 + 加反向链
   └─ 判定：标题含与目录定位不同的关键词
```

**自动判定（不询问用户）**：
```python
for file in target_dir:
    title = read_h1(file)
    parent_dir_purpose = read_h1(f"{target_dir}/README.md")  # 父目录的定位
    if topic_match(title, parent_dir_purpose):
        # 同主题 → 合并到同主题文件
        merge_or_keep(file, parent_dir)
    else:
        # 错位 → 移到正确目录
        relocate(file, correct_topic_dir)
```

**反模式**（必须避免）：
- ❌ 留 2 篇同主题文件让用户决定（用户没义务做 skill 的工作）
- ❌ 错位文件放错目录加 TODO（必须修正）
- ❌ cp -r 后用 README 反向链接掩盖错位（README 应准确反映内容）

**报告**（实施完成后）：
- 合并了多少组（保留 N 篇 → 1 篇）
- 移动了多少错位文件
- 拆分了多少多主题大文件

**案例**（lesson11 内容驱动）：
| 文件 | 标题主题 | 旧位置（lesson 映射） | 正确位置（内容驱动） |
|------|---------|---------------------|---------------------|
| `sh-01-mcp.md` | MCP 推荐 | `02-tools/lesson7/` | `02-tools/mcp/` |
| `bio-inspired-...-jailbreak.md` | 越狱研究 | `04-quality/lesson11/` | `04-quality/agent-reliability/jailbreak-papers/` |
| `dark-code-ai-security.md` | Dark Code | `04-quality/lesson11/` | `04-quality/agent-reliability/` |

**反模式**（必须避免）：
- ❌ `cp -r training/lessonX/. training-temp/某阶段/lessonX/`（机械复制）
- ❌ 按文件名（如 `claude-code.md`）猜分类（不读内容）
- ❌ 整 lesson 复制后用"反例"覆盖（如 lesson7 内容跨 4 主题，硬塞 02-tools/lesson7/）

**实施规范**：
- 严格遵循 plan 中定义的 commit 格式（`refactor(<slug>)` / `feat(<module>)` / `fix(<module>)`）
- 互链必须在 commit 中明示（"新增章节 + 加反向链"）
- 数字声明必须在 commit 前重新数（避免虚报）
- 路径深度必须从目标文件向上数（`../` 数量 = 层级差）
- **目标路径必须实际验证**（2026-07-25 ACP 教训）：写链接前用 `find note -name "<target>" -type f` 或 `ls -la <path>` 确认目标存在，不凭脑补
- **每文件 commit 后立即跑 broken links 扫描**（2026-07-25 ACP 教训）：commit 完不要等最后才检查，发现新引入立刻修，避免累计 3+ 处后才补
- 若 Step 5.5 触发了网络搜索，文章末尾必须有 `## 📚 参考来源` 章节

**每 commit 后 broken links 扫描脚本**（Mistake 14 + 8 联合防御）：

```bash
# 每文件 commit 后立即跑（应在 Step 6 每次 git commit 后调用）
python << 'PYEOF'
import sys, os, re, glob
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

# 严格 regex
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
PLACEHOLDERS = ['x/README', 'xxx', 'xx/yy', '../11.ai/...']
real_broken = 0
# 只扫本会话新文件（按时间戳或 git diff --name-only）
new_files = subprocess.check_output(['git', 'diff', '--name-only', '--since=<本次沉淀开始时间>'], cwd='.').decode().splitlines()
for f in [x for x in new_files if x.endswith('.md')]:
    try: c = open(f, encoding='utf-8', errors='ignore').read()
    except: continue
    for m in LINK_RE.finditer(c):
        target_rel = m.group(2).strip()
        if any(p in target_rel for p in PLACEHOLDERS): continue
        # Windows 路径处理：统一分隔符
        target_sep = target_rel.replace('/', os.sep)
        target_abs = os.path.normpath(os.path.join(os.path.dirname(f), target_sep))
        if not os.path.isfile(target_abs):
            real_broken += 1
            print(f'  ⚠ {f} -> {target_rel}')
print(f'新文件 broken links: {real_broken}')
PYEOF
```

如果 `real_broken > 0`，**立即修复下一个 commit**，不要等到沉淀结束。

**subagent "silent failure" 防御（强约束）**：

> ⚠️ 历史教训：曾出现多次 subagent 报告 "11/11 PASS" 但 `git status --short` 为空 / `ls file` 不存在（commit 1 subagent 多次完全无动作）。**subagent 自我报告 ≠ 实际落地**。
>
> 🆕 **2026-07-25 升级**（Phase 4 体检 + Batch 1-5 修复经验）：~6 个 subagent **修改了文件但没 commit**（"完成"报告但 `git log` 无 commit），需 orchestrator 收尾 commit。本条防御至关重要。

- **强制使用 Write 工具**：subagent 必须**实际调用 Write 工具**写入完整文件内容（不允许 placeholder / 占位符 / 仅创建空目录）
- **commit 前三步验证**：
  1. `ls -la FILE` 确认文件**真实存在**且**非空**（用 `wc -c` 验证文件大小 > 100 字节）
  2. `git status --short` 确认 staged/unstaged 状态**符合预期**
  3. `git log --oneline -3` 确认 commit 实际**落地**（前 3 commit 含本次 commit hash）
- **commit hash 必传**：subagent final report 必含**真实 commit hash**（不是"已 commit" 而是 `7e2cab99 refactor(note): ...`）。缺失则视为 commit 失败
- **🆕 final report 必含 4 项命令输出**（避免"修改但未 commit" silent failure）：
  1. `git log --oneline -1` 的**完整输出**（不是只贴 hash）
  2. `git status --short` 的**完整输出**（working tree 状态）
  3. 实际修改文件的 `wc -l FILE` 输出
  4. 修改文件列表（`git diff --name-only HEAD~1 HEAD`）
- **🆕 orchestrator 收尾协议**：subagent 报告"完成"但 `git log` 无新 commit → **立即 abort + 收尾 commit**（不信任 subagent 自我报告）
- **失败检测规则**：如果 subagent 报告完成但 `git log` 没新 commit → 立即 abort + 重派，不要信任 subagent 自我报告
- **commit 1 必含文件创建**：commit 1 必须新增 1+ 个文件（不能用 pure README 修改代替），`find note -name "<topic>.md" -newer <commit-base>` 验证

### Step 6.6: Git author 一致性（subagent 必须用主账号）

> 🆕 **2026-07-25 升级**（Phase 4 体检 + Batch 1-5 修复经验）：peer subagent 自动注入 fallback user `note-health-batch3 <note-health@local>`，导致 2 个 commit author 错误，需 rebase 修正。

- **subagent prompt 必含**：
  ```bash
  export GIT_AUTHOR_NAME="吴博"
  export GIT_AUTHOR_EMAIL="wubo_aaa@163.com"
  export GIT_COMMITTER_NAME="吴博"
  export GIT_COMMITTER_EMAIL="wubo_aaa@163.com"
  ```
  或在 Agent prompt 中显式要求"git commit 前必须设置 author 为 `吴博 <wubo_aaa@163.com>`"
- **subagent final report 必含 author 验证**：
  ```bash
  git log -1 --format="%an <%ae>" -- FILE
  ```
  输出必含 `吴博 <wubo_aaa@163.com>`，否则视为 author 错误
- **修复方法**（如果 author 已错误）：
  ```bash
  # 修正最近 N 个 commit 的 author
  GIT_AUTHOR_NAME="吴博" GIT_AUTHOR_EMAIL="wubo_aaa@163.com" \
    git rebase -i HEAD~N --exec 'git commit --amend --no-edit --reset-author'
  ```
  ⚠️ 注意 rebase 会改 commit hash，原预期 hash 会失效

### Step 6.5: 并发 peer session 协调（共享 worktree）

> 历史教训：多 session 在同一 worktree 并发工作时，peer 可能修改 subagent 写过的文件而不 commit，或写文件后不 commit，需要协调。

- **commit hash 必须可验证**：每次 session 派发后保留 agentId 列表 + 期望 commit hash，便于后续核对
- **peer 报告需独立验证**：
  - peer 报告"commit X 已落地" → `git log --grep="<topic>" --oneline` 独立验证
  - peer 报告"working tree 干净" → `git status -s` 独立验证
- **冲突协调**：当 commit 已被 peer 部分覆盖 + working tree 还有 modifications：
  - 检查 peer 修改是否被 commit（`git log` + `git diff`）
  - 如 peer 已 commit + working tree 还有未提交修改 → 询问用户偏好（reset 重写 vs polish commit）
- **不接受 floating peer 报告**：peer 报告后用 `git log --oneline` 独立核对才声明 final pass

### Step 6.7: 并行 subagent 共享文件协调（2026-07-30 新增）

> 🆕 **2026-07-30 教训**（Batch 3）：3 个 subagent 并行时，#5 和 #7 共享同一个父 README（`13.split-hairs/09.front-end/README.md`）。#7 subagent 完成了 feat commit 但**反向链变更未 commit**（留在 working tree），且题数没有更新到正确值（27→28）。

**规则**：
1. **识别共享文件**：派发前检查哪些父 README 会被多个 subagent 修改
2. **共享文件由 orchestrator 统一更新**：subagent prompt 中明确要求"**不要修改 `<父 README 路径>`**，该文件由 orchestrator 统一更新"
3. **Orchestrator 收尾 commit**：所有 subagent 完成后，orchestrator 检查 `git status --short`，将未提交的变更（反向链 + 题数修正）统一 commit

**Subagent prompt 模板**（并行派发时）：
```
**重要**：以下文件由 orchestrator 统一更新，你**不要修改**：
- `note/12.interview/<module>/README.md`（父 README 目录表）
- 任何其他 subagent 可能修改的文件

你只需负责：
1. 创建新 README 文件
2. 给**非共享**的兄弟 README 添加反向链
3. Commit 上述变更
```

**Orchestrator 收尾检查清单**：
- [ ] `git status --short` 检查是否有未提交变更
- [ ] 父 README 题数是否与实际目录数一致
- [ ] 所有反向链是否已 commit（不是只留在 working tree）

### Step 6.8: Subagent 父 README 更新职责（2026-07-30 新增）

> 🆕 **2026-07-30 教训**（消息已读未读面试题）：subagent 创建了新文件但没有更新父 README 的题数和条目。父 README 显示"共 20 题"，实际应该是 23 题（包含历史遗留的 media-upload、砍一刀算法等）。

**规则**：
1. **单个 subagent 也必须更新父 README**：创建新文件后，必须同时更新父 README 的题数计数器和条目列表
2. **更新前验证准确性**：先统计实际目录数，再更新题数（避免"旧账新账一起算"）
3. **Orchestrator 最终验证**：所有 subagent 完成后，orchestrator 必须验证父 README 的准确性

**Subagent prompt 模板**（单个任务）：
```
**父 README 更新职责**：
1. 创建新 README 文件后，更新父 README：
   - 题数计数器：`## 文章清单（共 N 题，find 校对 YYYY-MM-DD）`
   - 添加新条目到对应分类表格
2. 更新前验证：
   ```bash
   # 统计实际目录数
   ACTUAL_COUNT=$(ls note/12.interview/<module>/ | grep -v README | wc -l)
   # 对比父 README 中的题数
   DECLARED_COUNT=$(grep -oP '共 \K\d+' note/12.interview/<module>/README.md)
   # 如果不一致，先修正历史遗留问题
   ```
3. 添加新条目：
   - 找到合适的分类（如"业务系统设计"）
   - 添加一行：`| [新文件标题](新目录名/) | ⭐⭐⭐⭐ | 核心问题描述 |`
```

**Orchestrator 最终验证清单**：
- [ ] 父 README 题数 = 实际目录数
- [ ] 父 README 条目列表完整（无遗漏）
- [ ] 所有新文件都已添加到父 README

### Step 7: 验证 + 自检（必做）

**自检清单**：
- [ ] `git diff --check` 无警告
- [ ] 抽查 5 条新加链接：`grep -RE '<pattern>' note/<module>/`
- [ ] 主 README 中章节锚点仍指向正确路径
- [ ] frontmatter 完整性：所有新增 README 都有 frontmatter
- [ ] 数字校对：声明篇数与 find 实际结果一致
- [ ] 互链成网：新内容与至少 2 个旧章节互链（避免孤儿）
- [ ] **互链双向性扫描**：每个反向链接的 parent / 同级兄弟**必须回链**到新文件（避免"单向链接"）
- [ ] **每个 PASS 都有证据**：附 commit hash + `wc -l` 输出 + 行号引用，不接受泛泛"全部 PASS"
- [ ] **严格对照用户原规格**：用户原文提到的具体链接（如 `capacity-planning` / `widevine` / `keyinfo`）必须 grep 验证
- [ ] **代码示例若规格要求**：bash / ffmpeg / openssl 等必须**实际代码块**而非文字描述
- [ ] **数字实时核对**：subagent 报告行数必须 orchestrator 独立 `wc -l` 校验，不接受 subagent 自我声明

## Quick Reference

| 场景 | 推荐模式 | 落地位置 | Commit 数 |
|------|---------|---------|----------|
| 面试题（高频）| 双层 | 13.split-hairs/ + 主模块 | 2 |
| 深度原理 | 双层 | 主模块 + 13.split-hairs/ | 2 |
| 规模阶梯（10B→100B→1T）| 三层 + 12.story | 主模块 + 12.story 联动 | 3+ |
| 餐厅叙事价值高 | 三层 + 12.story | 12.story + 主模块 + 13.split-hairs/ | 3+ |
| 单一补充（如 "X 的新特性"）| 单文件 | 主模块子 README | 1 |
| **🆕 生产 Bug 案例（同栏目 troubleshooting 先例 ≥ 3）**| 单面试题 | `note/12.interview/<module>/<现象>-troubleshooting/` | 2-3 |

### 🆕 §X: 生产 Bug 类面试题特化（2026-08-28 沉淀实战新增）

> **触发**：用户提供真实生产事故案例（"线上 X 报警" / "X 100% 失败" / "X 反复触发"）—— 故事完整、有排查过程、有根因、有调优迭代。

#### §X.1 命名约定（按现有先例排比）

| 主题类型 | 命名模板 | 已落地范例（参照排比） |
|---------|---------|------|
| 生产 Bug 排查类 | `<现象>-troubleshooting` | `cpu-spike-troubleshooting` / `full-gc-troubleshooting` / `no-class-def-found-troubleshooting` |
| 调优类 | `<对象>-tuning-troubleshooting` | `metaspace-tuning-troubleshooting` |

**原则**：命名按现有先例**排比**，不发明新格式。先 `ls note/12.interview/<module>/` 看 3 个先例再命名。

#### §X.2 7 节骨架模板（参照 cpu-spike-troubleshooting 强制结构）

```text
1. 引子（150-250 字真实场景，含具体堆栈 / 告警 / 数据）
2. 一、核心原理（含 3-5 个 WHY 反直觉点）
3. 二、排查方法论（5 步走，含 jstack / jstat / jcmd 工具命令）
4. 三、根因深挖（3-5 个反直觉点，必须有 ❌/✅ 对照）
5. 四、解决（含代码块 + 配置 diff + 前后对比）
6. 五、验证（制品层 / 环境层 / 应用层三角度）
7. 六、面试话术（90 秒版本，含关键词流）
8. 七、相关章节（≥ 3 条反向链 + ≥ 1 条同栏目兄弟链）
+ 文末 footer `← [返回: ...]`
```

#### §X.3 Bonus 修复协议（沉淀时主动检查）

沉淀新案例时，**主动 grep 现有文件是否有同源反直觉错误**（同一错误示范）：

```bash
# 找现有文件中是否有同样的反直觉点
# 例：沉淀 MetaspaceSize 案例时，grep 找有没有其他文件只设 MaxMetaspaceSize 不设 MetaspaceSize
grep -rn "<本案例核心反直觉点关键词>" note/ | grep -v "<正常示范>"

# 找现有样例代码是否有相同错误
grep -B1 -A1 "<反模式关键词>=" note/<被链文件路径>
```

**判定**：
- 找到 1 处同源错误 → 顺手修复为单独 `fix(note)` commit（追加到本次沉淀的 commit 计划）
- 找到 2+ 处 → 评估是否批量修复（可能升级为单独任务）

#### §X.4 当用户挑战"双层推荐"时的应对（2026-08-28 第一轮经验）

用户说"是不是只沉淀成面试题更合理？" → **不要直接相信**，做内部先例对照：

```bash
# 找同栏目 troubleshooting 类先例
ls note/12.interview/<module>/ | grep "troubleshooting"

# 统计行数（先例通常是 200-450 行）
wc -l note/12.interview/<module>/*troubleshooting*/README.md
```

| 判定 | 行动 |
|------|------|
| 先例 ≥ 3 篇且单篇 200-450 行 | **改推荐：单面试题版**（用户对） |
| 先例 < 3 篇 | 坚持双层推荐 + 解释为什么 |
| 内容是纯原理 / 跨多领域 | 拆分或走原决策树 |

**反模式**：看到用户挑战就立刻改方向（缺乏证据）—— 应该用先例数据支撑结论。

## Quick Reference（原表保留）

## Common Mistakes

### ❌ Mistake 1: 跳过现状盘点

**症状**：直接在某个位置创建新文件，没注意已有类似内容 → 重复沉淀

**修复**：Step 1 不可跳过；用 grep + find 扫描 ≥ 5 个相关文件

### ❌ Mistake 2: 单一深度评估

**症状**：默认"是" → 沉淀任何主题 → note 膨胀

**修复**：Step 2 用 3 信号判断（高频 + 内容深 + 缺口真实）；不满足就不沉淀

### ❌ Mistake 3: 位置错位

**症状**：把技术原理放 `12.story`（叙事）/ 把面试题放 `11.ai/01-fundamentals`（原理）/ 把算法放 `04-architecture`（架构）

**修复**：Step 3 决策树 + 检查主模块子目录的命名约定（`01-fundamentals` / `02-technology-stack` / `03-engineering` / `04-architecture`）

### ❌ Mistake 4: 缺互链

**症状**：新文件是孤岛，没有反向链到已有内容 → 知识碎片化

**修复**：Step 4 决策时**强制要求**双层/三层沉淀带互链；Step 7 自检"至少 2 个旧章节互链"

### ❌ Mistake 5: subagent 调 AskUserQuestion 失败

**症状**：subagent 试图调 AskUserQuestion 但工具不可用 → 退化为写实施

**修复**：subagent **返回结构化选项**（不是直接调工具），让 orchestrator 转交用户

### ❌ Mistake 6: 缺 commit 策略

**症状**：模糊 commit message（"update docs"） / 多个 commit 描述重叠 / 混 refactor + feat

**修复**：Step 6 严格按 `<type>(<slug>): <动作>` 格式；每个 commit 只做一类变更

### ❌ Mistake 7: 数字虚报

**症状**：commit message 说"删除 6 个孤儿目录"但实际只改 README

**修复**：Step 6 数字声明必须由 implementer 用 `find` / `wc -l` 重新数；不允许估算

### ❌ Mistake 8: 路径深度错误（2026-07-25 强化）

**症状**：12.story 链接 `../../11.ai/13.split-hairs/11.ai/...`（多一层）→ broken link

**历史案例**（2026-07-25 ACP 沉淀）：
- ❌ `mcp.md` —— 以为是独立文件，实际 MCP 在 `context-engineering/README.md` 内联
- ❌ `multi-agent-system-design` 在 `../../../03-engineering/...` —— 实际在 `13.split-hairs/11.ai/`
- 根因：**没实际验证目标路径就写**

**修复（4 步强制）**：
1. **目标路径必须实际验证**：用 `find note -name "<target>" -type f` 或 `ls -la <path>` 确认目标存在
2. **手动数层级**：从源文件向上数 `../` 数量 = 目标深度差（注意 note/ 跨模块跳数）
3. **每文件 commit 后立即跑 broken links 扫描**（见 Step 6.5）
4. **不依赖"记忆"**：每次都 grep/find 验证，不要凭印象写路径

**🆕 强化（2026-07-25 经验）**：
- subagent 写完每个 `[...](./xxx/README.md)` 链接后**必须**用 `find note -name "xxx" -type d` 验证目标目录存在
- 如目标目录不存在，使用**替代方案三选一**：① 删除链接 ② 改为指向父系统（如 CMDB → ITSM with 注释）③ 新建对应 README（如确有需求）
- subagent prompt 模板**强制要求**：每个深读链接必须在最终报告里列出 `find` 命令的实际输出
- 历史案例（2026-07-25 业务系统补深）：QMS 引用 `../06-specialized/lims/README.md`（少一层 `../`，正确应是 `../../06-specialized/lims/README.md`），独立 `find` 验证 + 修复为正确路径

**🆕 强化（2026-07-27 经验 — 父 README 目录表更新）**：
- 当 subagent 更新**父 README 目录表**（如 `13.split-hairs/11.ai/README.md` 添加新面试题条目）时，目录表中的深读链接路径最易出错
- 历史案例（2026-07-27 Batch 1）：`13.split-hairs/11.ai/README.md` 目录表新增 agent-reliability 条目，subagent 写 `../../../11.ai/03-engineering/agent-reliability/README.md`（3 层 `../`），但 `13.split-hairs/11.ai/` 到 `note/08.ai-foundations/` 只需 2 层 `../../`
- **防御规则**：更新父 README 目录表时，用 Python 验证路径：
  ```python
  import os
  src_dir = 'note/12.interview/11.ai'  # 父 README 所在目录
  tgt = 'note/08.ai-foundations/03-engineering/agent-reliability/README.md'
  rel = os.path.relpath(tgt, src_dir)  # 自动计算正确相对路径
  print(rel)  # 输出: ../../11.ai/03-engineering/agent-reliability/README.md
  ```
- 不要手动数 `../` 层数，用 `os.path.relpath` 自动计算

### ❌ Mistake 9: 单向链接（child 链 parent，parent 不回链）

**症状**：新文件链接到 parent / 同级兄弟，但**parent / 同级兄弟没有反向链**到新文件。例如：

- 沉淀"05-agent-evaluation"，链到 `07-llmops/README.md` —— 但 `07-llmops/README.md` 没反向链到新文件
- 沉淀"production-agent 实战"，链到 `11.ai/README.md` —— 但 `11.ai/README.md` 没反向链到新文件

**修复**：
- **强制规则**：每个新文件 commit 时，**主动给被链接的 parent / 同级兄弟加反向链**（单独 refactor commit）
- 双向互链是**新内容责任**，不是"以后再说"
- Step 7 自检加「互链双向性扫描」项，**不达标则 commit 不合格**

**反直觉点**：很多人以为"我加了 2 条反向链就完事" —— 实际上被链接的 parent / 兄弟文件**也要回链**，否则会出现"两个 leaf 互相知道，但 parent 完全不知道新成员"的孤岛现象。

### ❌ Mistake 10: 系列内兄弟不互链

**症状**（两种场景）：
- **场景 A**：向已有系列添加新文章后，新文件只链回 README，已有兄弟也不知道新成员的存在。
  - 例：agent-execution-patterns 系列有 01-react / 02-plan-execute，新增 05-dag / 06-multi-agent
  - 但 01 和 02 的文件末尾**没有链向** 05 和 06 —— 同系列 6 篇文章各自孤立
- **场景 B（2026-07-25 新增）**：**历史遗留**——已有编号系列，但所有文件**历史都没加过"系列导航表"**。
  - 例：`note/01.java-and-jvm/kotlin/` 有 01-basics.md / 02-oop.md / 03-functional.md / 04-advanced.md / 05-coroutines.md 共 5 篇，**全部缺链**（没有任何一篇末尾有"系列导航表"）
  - 这类问题体检时通过 `Phase 1.9 系列完整性` 扫描可发现

**修复**：
- **强制规则**：向已有系列新增文章时，**每篇文件末尾必须有"系列导航表"**
- 系列导航表 = 一个表格，列出系列内所有文件 + 一句话核心问题
- 新文件加导航表 + 所有已有兄弟加/更新导航表
- Step 7 自检加「系列导航表完整性」项

**批量修复脚本**（场景 B 适用）：
```bash
# 找所有有编号系列的目录，补齐每个系列所有文件的"系列导航表"
for dir in $(find note -type d -exec sh -c 'ls "$1"/[0-9]*.md 2>/dev/null | wc -l | grep -q "^[2-9]" && echo "$1"' _ {} \;); do
  files=$(ls "$dir"/[0-9]*.md 2>/dev/null)
  # 检查哪些文件没有"系列导航表"
  for f in $files; do
    if ! grep -q "## 系列导航" "$f"; then
      echo "缺系列导航表: $f"
    fi
  done
done
```

**检测方法**：
```bash
# 找系列目录（有编号文件的目录）
for dir in $(find note -type d -exec sh -c 'ls "$1"/[0-9]*.md 2>/dev/null | head -1 | grep -q . && echo "$1"' _ {} \;); do
  echo "系列: $dir"
  for file in $(ls "$dir"/[0-9]*.md 2>/dev/null); do
    for other in $(ls "$dir"/[0-9]*.md 2>/dev/null); do
      [ "$file" = "$other" ] && continue
      other_base=$(basename "$other")
      if ! grep -q "$other_base" "$file" 2>/dev/null; then
        echo "  ⚠ $(basename $file) 未链向 $other_base"
      fi
    done
  done
done
```

### ❌ Mistake 11：subagent silent failure（自报 PASS 但文件不存在）

**症状**：subagent 报告 "X/Y self-check PASS" / "11/11 PASS" / "全部完成"，但 `git status --short` 为空、`git log` 无新 commit、目标文件不存在

**修复**：
- orchestrator 不能相信 subagent 自我报告，必须独立验证：`ls -la FILE` + `git status --short` + `git log --oneline -3`
- subagent 报告缺失 commit hash → 视为 commit 失败，立即 abort + 重派
- 注意 commit 1 章节的 subagent 失败概率最高（首次创建文件复杂操作）

**🆕 红旗识别（2026-07-25 经验）**：
- subagent 最终报告出现 **"如果需要...我可以..."** / **"可以..."** / **"建议你..."** / **"等你下一步指令"** 等委婉语 → **silent failure 红旗**，**立即 abort + 重派**，不需要等 `ls -la` 验证（红旗本身已足够判定）
- 真实 commit 完成的报告必含**实际 commit hash + `ls -la` / `wc -l` 命令输出**（不是"已完成"等模糊表述）
- 历史案例（2026-07-25 客服系统首次 subagent）：报告结尾"如果需要，我可以接着..."，但 `git log` 显示无新 commit、`ls -la call-center/README.md` 显示文件不存在 → 1 次重派即成功

### ❌ Mistake 12：git reset --soft + git commit --amend 错位

**症状**：`git reset --soft BASE` 撤销 3 个 commit 后重新 commit 1/2/3，HEAD 此时在 commit 3。后续 `git commit --amend` **修改的 HEAD（commit 3）**，而非你以为的 commit 1。结果 3 个 commit hash 全变

**修复**：
- reset 后**不要使用 `git commit --amend`**——直接 `git commit -m "..."` 创建新 commit
- 如必须 amend 早 commit，先 `git reset --soft TARGET_COMMIT^` + 重新 stage → commit（不复用 amend）
- 每次 reset 后**用 `git log --oneline` 确认 HEAD 位置**再决定 amend / commit

### ❌ Mistake 13：过度宣称 PASS（"所有项 PASS" 但用户规格未对齐）

**症状**：final report 宣告"11 项 PASS"、"全部完成"，但 peer 严格审计后发现用户原规格中的具体细节（特定链接 / 特定工具 / 特定代码示例）缺失

**修复**：
- orchestrator 的 final report **必须**逐项对照用户原始 question，把用户提到的每个具体名词 grep 验证
- 例：用户问"高可用高并发图片视频" → final report 必须 grep `WebP`、`AVIF`、`HLS`、`DRM`、`高可用`、`4 层防线` 全部存在
- 反例：final 报告"10 节齐全 PASS" 实际未 grep "4 层防线" "AES-128 "代码示例"" 实际是否落地

### ❌ Mistake 14：新内容引入新 broken links（2026-07-25 历史教训）

**症状**：沉淀 6 个新文件到 note/ 后，新文件中的 markdown 链接路径写错（相对路径多/少一层 ../），引入新的 broken links。**即使新内容质量满分（20/20），broken links 增量仍然是结构性硬伤**。

**历史案例**（2026-07-25 coding-agents 沉淀）：
- 6 个新文件 + 8 commit 后，**新引入 0 broken links**（验证通过 ✅）
- 但反例风险：在 note/03.java/01-foo/02-bar/README.md 写 `../baz/README.md` 而不是 `../../baz/README.md`，会让 note 出现真错

**🆕 强化（2026-07-25 经验）**：
- subagent 写新 README 引用任何系统前**必须**先 `grep -r "<system>" note/08.application-systems/` 确认该系统是否独立存在
- 如果**不是独立系统**（如 CMDB 是 ITSM 子模块、APR/MRP 是 ERP 子模块），应使用替代方案：① 删除链接 ② 改为指向父系统 with 注释（如 `[ITSM 深读](../../06-specialized/itsm/README.md)`（含 CMDB））
- 历史案例（2026-07-25 业务系统补深）：EAM 引用 `../../06-specialized/cmdb/README.md`（CMDB 不是独立系统，是 ITSM 子模块），独立验证 `ls -la note/08.application-systems/06-specialized/` 发现 cmdb 目录不存在 → 修复为 ITSM with 注释

**修复（沉淀完成后的简单兜底）**：

```bash
# 沉淀完成后立即跑 broken links 扫描（严格 regex 版）
# 期望输出：broken links: 0
python -c "
import os, re, glob
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
PLACEHOLDERS = ['x/README', 'xxx', 'xx/yy', '../11.ai/...']
real_broken = 0
new_files = [f for f in glob.glob('note/**/*.md', recursive=True)
             if os.path.exists(f) and int(os.stat(f).st_mtime) > <沉淀开始时间戳>]
for readme in new_files:  # 优先扫本会话新文件
    content = open(readme, encoding='utf-8', errors='ignore').read()
    for m in LINK_RE.finditer(content):
        target_rel = m.group(2).strip()
        if any(p in target_rel for p in PLACEHOLDERS): continue
        target_abs = os.path.normpath(os.path.join(os.path.dirname(readme), target_rel))
        if not os.path.isfile(target_abs):
            real_broken += 1
            print(f'  ⚠ {readme} -> {target_rel}')
print(f'新文件 broken links: {real_broken}')
"
```

**最终报告**：final report 必须包含"broken links: 0"作为硬指标。

### ❌ Mistake 15：同 README 内重复维护多个等价表格（2026-07-25 历史教训）

**症状**：沉淀新章节时，作者**独立维护了 2+ 张等价信息源**（如"目录表" + "明细表"）。下游体检只扫**跨文件** / **文件级**重复，发现不了**同文件内冗余**。

**历史案例**（2026-07-25 12.story/README.md）：
- line 26-36：8 集群目录表（含"一句话"列）—— 完整 + 信息密度高
- line 336-353（已删除）：49 篇明细表（按类型分组）—— 100% 重叠 + 编号混乱（line 353 注释显式承认"11 = 续集二 / 14 = 番外二"）
- 两张表 49 篇文章编号需同时维护 → 维护成本翻倍 + 易漂移

**修复（沉淀时主动避免）**：
- **强制规则**：沉淀新 README 时，**每张表格只承载一个职责**，不要做"明细表"补完
- 多视角需要时，**用 section 标题区分**（"## 目录导航" + "## 速查表"），而不是重复表格
- Step 7 自检加项：grep `\|---` 表格分隔行数 ≥ 2 的 README，人工检查表格列是否重叠

**历史兜底**：体检时如果发现同 README 内 2+ 张表格列字段重叠 ≥ 50%，标记为 P2 应修（合并 / 删除）。

### ❌ Mistake 16：多主题错误合并成一个文件（2026-07-26 历史教训）

**症状**：用户输入包含多个独立子主题（如"大模型思维工程 5 个灵魂拷问"），skill 未识别 → 把 N 个独立主题合成一个 419 行文件。后续不得不全部拆散 + 重新定位。

**历史案例**（2026-07-26 llm-production-thinking）：
- 用户说"沉淀大模型思维工程 5 个灵魂拷问"
- Step 0 缺失 → 5 个独立主题（思维范式 / 成本控制 / 一致性 / 超时熔断 / 监控定位）被合成一个 `production-thinking-5q/README.md`
- 后续发现：每个主题都应该独立成文 + 独立面试题 → 全部拆散 + 目录重定位

**修复（Step 0 强制）**：
- **Step 0 主题识别**：在盘点前先判断用户输入是单主题还是多主题
- **多主题判断信号**：有编号（"5 个"、"3 大"）、有并列（"A + B + C"）、有"N 种"/"几种"
- **多主题处理**：每个子主题独立走 Step 1-7 流程，不要合并
- **强关联主题**：创建系列目录（如 `llm-production-thinking/`），但每个子主题独立成文（01-thinking-paradigm.md / 02-cost-control.md ...）
- **面试题处理**：每个子主题各自独立一篇面试题（`llm-thinking-paradigm/` / `llm-cost-control/` ...），不要合成"5q"文件

**检测命令**：
```bash
# 检测"多主题合并"文件（单文件 > 300 行 + 包含多个独立 H2 章节）
for f in $(find note -name "README.md" -size +10k); do
  h2_count=$(grep -c "^## " "$f" 2>/dev/null)
  if [ "$h2_count" -ge 5 ]; then
    echo "  ⚠ 可能多主题合并: $f ($h2_count 个 H2 章节)"
  fi
done
```

### ❌ Mistake 17：多主题沉淀导致上下文溢出（2026-07-26 历史教训）

**症状**：一次沉淀 3+ 个主题（每个双层 = 2 文件 + 2-3 commit + 路径验证 + 反向链），上下文被占满 → compact → 后续工作（父 README 更新、broken links 验证、commit）需手动恢复。

**历史案例**（2026-07-26 Agent 三主题沉淀）：
- 用户问 3 个问题：Skill 命中率 / Structured Output / Planning-Acting-Monitoring
- 选择沉淀后 2 个主题（第 3 个 skip）
- 每个主题：Write 文件 + 路径验证 + 反向链 + commit = ~800 行上下文
- 3 个主题 = ~2400 行 → compact 触发 → 后续父 README 更新需手动恢复

**修复（Step 0.5 强制）**：
- **Step 0.5 上下文预算评估**：多主题时先评估每个主题的复杂度 + 预估上下文消耗
- **单次沉淀上限**：简单主题 ≤ 3 个 / 中等主题 ≤ 2 个 / 含复杂主题分批
- **分批执行协议**：Batch 1 完成 → 主动提示用户 compact → Batch 2
- **不要硬撑**：上下文 > 1500 行时主动建议分批，不要等 compact 被动触发

**检测信号**（何时该分批）：
- 已沉淀 2 个双层主题 + 还有第 3 个待处理 → 建议分批
- 每个主题涉及跨模块链接（路径验证成本高）→ 建议分批
- 需要更新多个父 README（每个 +0.5 复杂度）→ 建议分批

### ❌ Mistake 18：并行 subagent 共享父 README 导致题数漂移（2026-07-30 历史教训）

**症状**：多个 subagent 并行工作时，各自更新**同一个父 README** 的题数计数器。后完成的 subagent 看不到先完成的 subagent 的修改，导致题数不一致（如两个新文件已添加，但题数只 +1）。

**历史案例**（2026-07-30 Batch 3）：
- 3 个 subagent 并行：#5 debounce-streaming / #6 async-vs-multithread / #7 webpack-vite-migration
- #5 和 #7 都更新 `note/12.interview/09.front-end/README.md`
- #5 subagent 更新题数 26→27 ✅
- #7 subagent 添加了条目但**题数仍是 27**（应为 28）
- Orchestrator 收尾时发现并修正 27→28

**根因**：并行 subagent 基于"旧版本"的父 README 工作，后完成的 subagent 的 `git diff` 看不到先完成的 subagent 已 commit 的修改。

**修复（orchestrator 必做）**：
1. **父 README 题数更新由 orchestrator 统一收尾**，不在 subagent prompt 中要求
2. **subagent 只负责**：创建新文件 + 添加反向链到**非共享文件**（兄弟 README、主模块子文章）
3. **Orchestrator 收尾步骤**：
   ```bash
   # 1. 统计实际目录数
   ACTUAL_COUNT=$(ls note/12.interview/<module>/ | grep -v README | wc -l)
   # 2. 对比父 README 中的题数
   DECLARED_COUNT=$(grep -oP '共 \K\d+' note/12.interview/<module>/README.md)
   # 3. 如不一致，orchestrator 修正 + commit
   if [ "$ACTUAL_COUNT" != "$DECLARED_COUNT" ]; then
     # sed 替换题数
     git commit -m "fix(note): <module> - 修正题数 ${DECLARED_COUNT}→${ACTUAL_COUNT}"
   fi
   ```
4. **或者**：如果并行 subagent 涉及共享父 README，**改为串行执行**（#5 完成 → #7 开始）

**检测信号**：
- `ls note/<module>/ | grep -v README | wc -l` ≠ 父 README 中"共 N 题"
- `grep -c "^| \[" note/<module>/README.md` ≠ 父 README 中"共 N 题"

### ❌ Mistake 19：父 README 历史遗留问题（2026-07-30 新增）

**症状**：执行沉淀任务时，发现父 README 的题数计数器和实际目录数不一致，且缺少历史条目。执行后"旧账新账一起算"，导致最终状态混乱。

**历史案例**（2026-07-30 消息已读未读面试题）：
- 父 README 显示"共 20 题"
- 实际目录数：23 个（包含 media-upload、砍一刀算法等历史遗留）
- 缺少 3 个条目：media-upload、砍一刀算法、message-read-status
- Subagent 只添加了 message-read-status，没有发现历史遗留问题
- Orchestrator 收尾时发现并统一修正

**根因**：subagent 没有在执行前验证父 README 的准确性，只关注"新增"而忽略"存量"。

**修复（执行前必做）**：
1. **Step 1 现状盘点必须包含父 README 验证**：
   ```bash
   # 1. 统计实际目录数
   ACTUAL_COUNT=$(ls note/12.interview/<module>/ | grep -v README | wc -l)
   
   # 2. 读取父 README 声明的题数
   DECLARED_COUNT=$(grep -oP '共 \K\d+' note/12.interview/<module>/README.md)
   
   # 3. 对比并记录差异
   if [ "$ACTUAL_COUNT" != "$DECLARED_COUNT" ]; then
     echo "⚠️  父 README 题数不一致：声明 $DECLARED_COUNT，实际 $ACTUAL_COUNT"
     echo "   历史遗留问题：$(($ACTUAL_COUNT - $DECLARED_COUNT)) 个条目缺失"
   fi
   
   # 4. 列出实际目录 vs 父 README 条目，找出缺失项
   ls note/12.interview/<module>/ | grep -v README | sort > /tmp/actual.txt
   grep -oP '\[.*?\]\(([^)]+)/\)' note/12.interview/<module>/README.md | \
     grep -oP '(?<=\()[^)]+(?=/)' | sort > /tmp/declared.txt
   comm -23 /tmp/actual.txt /tmp/declared.txt  # 实际有但父 README 没有的
   ```

2. **Orchestrator 必须在 Step 6 前明确告知 subagent**：
   - 如果发现历史遗留问题，subagent 应该一并修正（不仅是新增）
   - 或者 orchestrator 在收尾时统一处理

3. **Subagent prompt 模板**：
   ```
   **执行前验证**：
   1. 统计实际目录数：ACTUAL_COUNT
   2. 读取父 README 题数：DECLARED_COUNT
   3. 如果不一致，列出缺失条目并一并添加
   
   **示例输出**：
   - 实际目录数：23
   - 父 README 题数：20
   - 缺失条目：media-upload、砍一刀算法
   - 本次新增：message-read-status
   - 最终题数：23
   ```

**检测信号**：
- `ls note/<module>/ | grep -v README | wc -l` ≠ 父 README 中"共 N 题"
- 缺失条目数 = 实际目录数 - 父 README 题数

**预防措施**：
- 在 Step 1 现状盘点中加入"父 README 准确性验证"步骤
- 在 Step 7 验证中加入"父 README 完整性检查"

### ❌ Mistake 20：双层沉淀的"弱关联"互链（2026-08-20 新增）

**症状**：新文件链接到"同栏目 / 同目录"兄弟，但**目标文件在被链接文件里 0 真实引用**——只是"凑兄弟题数量"，没有任何语义价值。

**历史案例**（2026-08-20 file-upload 双层审查）：
- A 文件 `12.interview/04.system-design/file-upload/README.md` 链向 `product-search`（同栏目兄弟）
- 但 A 全文 191 行 **0 处提及**"搜索 / 倒排 / 索引 / typeahead"
- 同样的问题：B 文件 `06.distributed-systems/04-high-performance/file-upload/README.md` 也链向 `product-search`
- B 全文 239 行 + 3 个子文件 **0 处提及**"搜索 / 倒排 / 索引"
- 结论：商品搜索与 file-upload 0 技术耦合，链接属"凑互链"

**根因**：开发者看到"同栏目"就自动加链接，没做"目标文件在被链接文件里是否有真实语义引用"的验证。

**与 Mistake 9 / 10 的关系**：
- **Mistake 9**（单向链接）= 结构层 —— child 链 parent，parent 不回链
- **Mistake 10**（系列不互链）= 结构层 —— 同系列兄弟互不知道
- **Mistake 20**（弱关联互链）= **语义层** —— 即使双向都链了，但链接本身无意义

**修复流程（用户怀疑 → 验证 → 决策）**：

1. **当用户说"感觉不相关 / 是不是不该链"** → 不要直接相信，做内部 grep 验证：
   ```bash
   # 在"被链接的文件"里 grep "目标文件主题关键词"
   grep -rn "<目标主题关键词>" <被链接文件目录>/
   ```

2. **判定表**：
   | grep 命中 | 用户直觉 | 行动 |
   |---|---|---|
   | 0 处 | 用户对 | 立即删除弱关联链接 |
   | ≥ 1 处 | 用户不准 | 保留并补"为什么相关"的语义描述 |

3. **互链价值判断公式**（适用于任何互链审查）：
   - **强关联**：目标文件在被链接文件内有 grep 命中（≥ 1 处）→ 留
   - **弱关联**：目标文件在被链接文件内 0 grep 命中 → 删
   - **保留原则**：强关联必留，弱关联删除（互链价值 < 维护成本）

4. **保留弱关联时的描述补强**（如果 grep 命中 ≥ 1 但描述不清晰）：
   ```markdown
   # ❌ 弱描述（看不出关联）
   - 同级案例：[敏感词过滤](../sensitive-word-filter/README.md) — AC 自动机 + 高并发过滤

   # ✅ 强描述（说明关联语义）
   - 同级案例：[敏感词过滤](../sensitive-word-filter/README.md) — AC 自动机 + 高并发过滤（上传后内容审核）
   ```

**检测脚本**（可在 Step 7 自检时跑）：
```bash
# 对每个被链接的兄弟文件，做关联强度判定
for target in $(grep -oP '\]\(\.\./[^)]+\)' note/<file>/README.md | grep -oP '\.\./[^)]+'); do
  count=$(grep -c "<target的主题关键词>" <被链接的文件>)
  if [ "$count" -eq "0" ]; then
    echo "  ⚠ 弱关联: note/<file>/ → $target（被链接文件 0 处提及）"
  fi
done
```

**预防措施**：
- Step 1 现状盘点：列出每个"潜在互链候选"时，**先 grep 验证关联强度**
- Step 6 实施：写互链前问"目标文件在被链接文件里有什么真实引用"，无引用则不写
- Step 7 自检：加「互链关联强度判定」项（见 Quick Checklist）

**反直觉点**：很多人以为"同栏目就是强关联"——实际上栏目只是分类，分类内的文件可能零耦合（如 file-upload 和 product-search 都是"系统设计"但完全不相关）。真正的强关联 = 真实语义引用，不是目录位置。

---

## Output Format

**作为 orchestrator**（直接面对用户）：

```
## 📋 现状盘点
（5-10 个相关文件 + 覆盖深度）

## 🎯 深度评估
（值得沉淀的 3 个信号 + 反信号）

## 💡 位置 + 方式建议
（决策树应用结果 + 推荐模式）

## ❓ 选项
（2-4 个选项 + 推荐项放第一）

[用 AskUserQuestion 呈现]
```

**作为 subagent**（让 orchestrator 转交）：

```markdown
## 报告：<topic> 沉淀分析

### 1. 现状盘点
（5-10 个相关文件 + 覆盖深度）

### 2. 深度评估
（值得/不值得 + 理由）

### 3. 位置 + 方式建议
（决策树应用结果 + 推荐模式）

### 4. 选项（请用户选择 A/B/C/D）

#### A. 双层沉淀 + 双向联动（推荐）
- 改动：3 文件 + 3 commit
- 优点：闭环最完整
- 缺点：改动略多

#### B. 只动面试深挖版
- 改动：1 文件 + 1 commit
- 优点：最小改动
- 缺点：缺深度原理层

#### C. 暂不沉淀
- 优点：避免冗余
- 缺点：现有缺口保留

### 5. 风险评估（如有）
（如：可能影响 X 章节的锚点 / 可能与 Y 章节重复）

### 6. 验证清单
（实施后需检查的 5 项）

[不要用 AskUserQuestion — orchestrator 转交]
```

## Real-World Impact

5+ 主题已按此流程沉淀，commit 数 0 → 60+：

| 主题 | 沉淀模式 | 验证命令（按主题名 grep） |
|------|---------|--------------------------|
| dropout-in-llm | 双层 | `git log --grep='dropout-in-llm' --oneline` |
| claude-code-agentic-search | 双层 + RAG 反向链 | `git log --grep='skill' --oneline \| head -5` |
| agent-memory-classification | 双层 + 04-architecture 补全 | `git log --grep='agent-memory' --oneline` |
| vector-search-algorithms | 三层 + 12.story 联动 | `git log --grep='vector-search' --oneline` |
| vector-search-at-scale / trillion | 三层 + 10B/100B/1T 阶梯 | `git log --grep='at-scale' --oneline` |

> **可核实性**：每个主题的实际 commit hash 以 `git log --grep="<topic>"` 实时查询为准。上表不再硬编码 commit hash（避免 hash 被回滚后误导用户）。用户复制验证命令到本地 `note/..` 仓库即可查到该系列首条 feat commit。

避免的失败：
- ❌ 没重复沉淀（如 RAG / Dropout 已有 → 不重复）
- ❌ 没位置错位（如 dropout 放 02 而非 01-fundamentals）
- ❌ 没孤岛文件（每个新 README 至少 2 个反向链）
- ❌ 没空 commit（4 commits/module 严格执行）

## Quick Checklist（执行前必过）

- [ ] Step 1 完成：现状盘点（5-10 文件）
- [ ] Step 2 完成：深度评估（3 信号检查）
- [ ] Step 3 完成：位置决策（决策树应用）
- [ ] Step 4 完成：方式决策（单/双/三层）
- [ ] Step 5 完成：选项呈现（2-4 项 + 推荐）
- [ ] Step 5.5 评估：知识丰富度（触发搜索 or 直接写）
- [ ] Step 6 计划：commit 策略 + 互链 + 参考来源（如有搜索）
- [ ] Step 7 计划：验证清单（5 项）+ **互链双向性扫描**

## Quick Checklist（执行后追加 — 避免新文件成孤岛）

- [ ] **新文件链接 ≥ 2 个旧章节**（避免"不知道放在哪"）
- [ ] **被链接的旧章节必须反向链回新文件**（避免"单向链接"）
- [ ] **新文件链到的同级兄弟必须回链**（避免同目录 leaf 互相不知）
- [ ] **父 README / 总目录表已加新文件链接**（避免"总目录孤岛"）
- [ ] **总目录数字（题目数 / leaf 数）已同步更新**（避免数字不一致）
- [ ] **系列内所有文件都有"系列导航表"**（当目标目录已有编号系列时，见 Mistake 10）
- [ ] **互链关联强度判定**（见 Mistake 20）：每个被链接的兄弟文件，grep "目标主题关键词"≥ 1 处才算强关联；弱关联（0 命中）即使"同栏目"也应删除
- [ ] **新 README 文末必须含 `← [返回:` footer 回链**（避免格式约定违反，2026-07-25 教训：本会话新文件 coding-agent-mode-selection 漏 footer 回链）
  - 自检命令：`grep -L "← \[返回:" $(find note -name "README.md" -newer <commit-base>)`
  - **新 README 必须有**，根目录 README（`note/README.md`）除外
- [ ] **新 README 内每张表格只承载一个职责**（避免同 README 内重复维护多张等价表，见 Mistake 15）
  - 自检：grep 新 README 的 `\|---` 表格分隔行数 ≥ 2 → 人工检查表格列字段是否重叠 ≥ 50%
  - 历史教训：12.story/README.md 历史上同时维护 8 集群目录表 + 49 篇明细表，100% 等价