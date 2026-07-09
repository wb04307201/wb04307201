---
name: note-precipitation-planning
description: Use when user asks where to add or update a topic in the project's note/ knowledge base — covers survey of existing 14-module structure, depth analysis, location decision between main module / 13.split-hairs interview layer / 12.story narrative layer, layered precipitation strategy, and reverse-link verification
---

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

当用户问"这个主题应该新增/更新到 note 的什么位置"时，遵循 7 步流程输出沉淀方案。`note/` 是 14 主模块的体系化技术知识库，含 `01.java` ~ `14.project-management`，每个主模块有 README + 子目录 + 已建立的双层/三层沉淀模式（13.split-hairs 面试题 + 11.ai 主模块 + 12.story 餐厅叙事）。

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

**note 目录位置**：仓库根目录的 note/（assuming CWD = project root）

**14 主模块**：
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

## 7 步核心流程

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
ls note/13.split-hairs/<module>/ | grep -v README

# 1.4 12.story 相关章节
grep -l "<关键词>" note/12.story/*.md 2>/dev/null

# 1.5 系列结构检查（目标目录下是否已有编号系列）
# 如果目标目录下有 01-xxx.md / 02-xxx.md 等编号文件，
# 说明是"系列"，新增文章时必须补全系列内互链
ls note/<target-dir>/[0-9]*.md 2>/dev/null
# 如果找到编号文件 → 新文章需要：
#   a. 末尾加"系列导航表"（链向所有兄弟）
#   b. 所有已有兄弟末尾加/更新"系列导航表"（链向新文件）
```

**输出**：5-10 个相关文件 + 每个文件的"覆盖深度"评估（"已有详细"/"一笔带过"/"完全缺失"）

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
```

**双层沉淀模板**：
```
Commit 1: feat(13.split-hairs): <module> 新增'<topic>'面试题
Commit 2: feat(<module>): 新增'<topic>'深度原理
```

**三层沉淀模板**：
```
Commit 1: feat(13.split-hairs): <module> 新增'<topic>'面试题
Commit 2: feat(<module>): 新增'<topic>'深度原理
Commit 3: refactor(<module>): <related-chapter> 加反向链
```

### Step 5: 选项呈现（用 ask the user directly，orchestrator 执行）

**关键**：如果as a helper task 执行，**不能直接调 ask the user directly**，必须返回选项return structured output for the caller。

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

### Step 6: 实施（break into sequential helper tasks）

**实施规范**：
- 严格遵循 plan 中定义的 commit 格式（`refactor(<slug>)` / `feat(<module>)` / `fix(<module>)`）
- 互链必须在 commit 中明示（"新增章节 + 加反向链"）
- 数字声明必须在 commit 前重新数（避免虚报）
- 路径深度必须从目标文件向上数（`../` 数量 = 层级差）

### Step 7: 验证 + 自检（必做）

**自检清单**：
- [ ] `git diff --check` 无警告
- [ ] 抽查 5 条新加链接：`grep -RE '<pattern>' note/<module>/`
- [ ] 主 README 中章节锚点仍指向正确路径
- [ ] frontmatter 完整性：所有新增 README 都有 frontmatter
- [ ] 数字校对：声明篇数与 find 实际结果一致
- [ ] 互链成网：新内容与至少 2 个旧章节互链（避免孤儿）
- [ ] **互链双向性扫描**：每个反向链接的 parent / 同级兄弟**必须回链**到新文件（避免"单向链接"）

## Quick Reference

| 场景 | 推荐模式 | 落地位置 | Commit 数 |
|------|---------|---------|----------|
| 面试题（高频）| 双层 | 13.split-hairs/ + 主模块 | 2 |
| 深度原理 | 双层 | 主模块 + 13.split-hairs/ | 2 |
| 规模阶梯（10B→100B→1T）| 三层 + 12.story | 主模块 + 12.story 联动 | 3+ |
| 餐厅叙事价值高 | 三层 + 12.story | 12.story + 主模块 + 13.split-hairs/ | 3+ |
| 单一补充（如 "X 的新特性"）| 单文件 | 主模块子 README | 1 |

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

### ❌ Mistake 5: helper task 调 ask the user directly 失败

**症状**：helper task 试图调 ask the user directly 但工具不可用 → 退化为写实施

**修复**：**返回结构化选项**（不是直接调工具），由主任务转交用户

### ❌ Mistake 6: 缺 commit 策略

**症状**：模糊 commit message（"update docs"） / 多个 commit 描述重叠 / 混 refactor + feat

**修复**：Step 6 严格按 `<type>(<slug>): <动作>` 格式；每个 commit 只做一类变更

### ❌ Mistake 7: 数字虚报

**症状**：commit message 说"删除 6 个孤儿目录"但实际只改 README

**修复**：Step 6 数字声明必须由 implementer 用 `find` / `wc -l` 重新数；不允许估算

### ❌ Mistake 8: 路径深度错误

**症状**：12.story 链接 `../../11.ai/13.split-hairs/11.ai/...`（多一层）→ broken link

**修复**：Step 6 实施时**手动数层级**（从源文件向上数 `../` 数量 = 目标深度差）

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

**症状**：向已有系列添加新文章后，新文件只链回 README，已有兄弟也不知道新成员的存在。例如：
- agent-execution-patterns 系列有 01-react / 02-plan-execute，新增 05-dag / 06-multi-agent
- 但 01 和 02 的文件末尾**没有链向** 05 和 06 —— 同系列 6 篇文章各自孤立

**修复**：
- **强制规则**：向已有系列新增文章时，**每篇文件末尾必须有"系列导航表"**
- 系列导航表 = 一个表格，列出系列内所有文件 + 一句话核心问题
- 新文件加导航表 + 所有已有兄弟加/更新导航表
- Step 7 自检加「系列导航表完整性」项

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

## Output Format

**as the main task**（直接面对用户）：

```
## 📋 现状盘点
（5-10 个相关文件 + 覆盖深度）

## 🎯 深度评估
（值得沉淀的 3 个信号 + 反信号）

## 💡 位置 + 方式建议
（决策树应用结果 + 推荐模式）

## ❓ 选项
（2-4 个选项 + 推荐项放第一）

[用 ask the user directly 呈现]
```

**as a helper task**（return structured output for the caller）：

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

[不要用 ask the user directly — orchestrator 转交]
```

## Real-World Impact

5+ 主题已按此流程沉淀，commit 数 0 → 60+：
- dropout-in-llm（双层）
- claude-code-agentic-search（双层 + RAG 章节反向链）
- agent-memory-classification（双层 + 04-architecture 体系补全）
- vector-search-algorithms / at-scale / trillion（三层 + 12.story 联动 + 10B/100B/1T 阶梯）

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
- [ ] Step 6 计划：commit 策略 + 互链
- [ ] Step 7 计划：验证清单（5 项）+ **互链双向性扫描**

## Quick Checklist（执行后追加 — 避免新文件成孤岛）

- [ ] **新文件链接 ≥ 2 个旧章节**（避免"不知道放在哪"）
- [ ] **被链接的旧章节必须反向链回新文件**（避免"单向链接"）
- [ ] **新文件链到的同级兄弟必须回链**（避免同目录 leaf 互相不知）
- [ ] **父 README / 总目录表已加新文件链接**（避免"总目录孤岛"）
- [ ] **总目录数字（题目数 / leaf 数）已同步更新**（避免数字不一致）
- [ ] **系列内所有文件都有"系列导航表"**（当目标目录已有编号系列时，见 Mistake 10）