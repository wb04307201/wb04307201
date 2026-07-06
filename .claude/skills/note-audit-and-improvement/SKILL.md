---
name: note-audit-and-improvement
description: Use when user asks "what should be improved in note" or requests a full audit — covers 8-category scan (numbers / links / index / duplicates / gaps / architecture / style / other), priority ranking (P0-P3 by impact × effort), mechanical vs judgment split, and batched execution plan
---

# note 优化审计

## Overview

当用户问"note 哪里需要优化 / 哪里需要补充 / 哪里有索引缺失 / 哪里有问题"时，对仓库根目录下的 note/ 做**系统性审计**（CWD 假设为项目根），输出**优先级分级**的优化建议报告（不是一次性 70+ 改动，而是分批可执行）。

## When to Use

**Use when**：
- 用户问"note 哪里需要优化？"
- 用户问"note 有哪些问题？"
- 用户问"审计 note 现状"
- 用户说"扫一遍 note 给我建议"

**Don't use when**：
- 用户已知具体问题（如"修复 04.system-design/05-security 重复目录"）→ 直接修复
- 用户已知具体位置要新增主题 → 用 `note-precipitation-planning` skill
- 用户问"note 整体结构" → 直接展示 README

## Project Context（必读）

**note 位置**：仓库根目录的 note/（CWD 假设 = 项目根）

**已知已修复的问题**（**扫描时必须排除**，避免重复报告）：
- ✅ 14 主模块优化（2026-07-01 spec/plan/实施）
- ✅ 时间戳标记 `最后更新`（commit `785896e`）
- ✅ `引言：反直觉代码` 模板残留（commit `30f6323`）
- ✅ Agent Memory / Dropout / Claude Code / Vector Search 三档专题沉淀

**8 大审计类别**：

| # | 类别 | 扫描命令示例 |
|---|------|------------|
| 1 | **数字一致性** | `grep -rn "篇\|个\|行" note/README.md note/*/README.md` |
| 2 | **H1 / 标题规范** | `grep -rn "^# " note/*/README.md` |
| 3 | **回链覆盖率 + 互链双向性** | `grep -rln "← \[返回\|返回.*目录" note/ | wc -l` vs `find note -name README.md \| wc -l`；外加单向链接扫描（child → parent 但 parent 不回链） |
| 3.5 | **孤岛检测 / 总目录扫描** | 扫描所有新文件（commit 时间 ≤ N 天），验证其：① 链接了 ≥ 2 个旧章节 ② 父 README / 总目录表有反向链接 ③ 同级兄弟有反向链接 |
| 4 | **索引/入口缺失** | `find note -type d -not -path "*/node_modules/*" \| wc -l` vs README 引用 |
| 5 | **内容重复** | `find note -name "*.md" \| xargs grep -l "<关键概念>" \| sort -u` |
| 6 | **内容补充缺口** | 找到深度 ≤ 50 行的 README（可能是占位）|
| 7 | **架构/分类/命名** | 目录命名风格不一致 / 编号缺失 |
| 8 | **其他**（PNG / 脚本 / 杂项）| `find note -name "*.png" \| xargs grep -L "!"` |

## 5 步核心流程

### Step 1: 现状扫描（必做）

**目的**：用真实命令收集证据，不凭印象

**关键操作**：
```bash
cd "$(git rev-parse --show-toplevel)"

# 1. 总览
find note -name "README.md" | wc -l                                    # README 数
find note -type d -not -path "*/target/*" -not -path "*/demo/*" | wc -l  # 目录数
find note -type f -name "*.md" | wc -l                                 # .md 数

# 2. 数字一致性扫描
grep -rn "^[0-9]\+ 篇\|[0-9]\+ 个\|共.*[0-9]" note/README.md note/*/README.md | head -30

# 3. H1 数字编号违规
grep -rn "^# [一二三四五六七八九十]、\|^# [0-9][0-9]\." note/*/README.md | head -10

# 4. 回链覆盖率
TOTAL_READMES=$(find note -name "README.md" | wc -l)
WITH_BACKLINK=$(grep -rl "← \[返回\|← \[主模块\]" note/ | wc -l)
echo "回链覆盖: $WITH_BACKLINK / $TOTAL_READMES"

# 4.5 单向链接扫描（parent 不回链 child）
# 原理：find 所有文件中的反向链接，记下每个"被链到"的文件
# 然后检查每个被链到的文件，是否回链了链接它的源
echo "=== 单向链接扫描（child → parent 但 parent 不回链）==="
for child in $(find note -name "*.md"); do
  # 找 child 文件链到的所有 target（粗略正则，可能有误差，需人工复核）
  grep -oE '\]\(([^)]+\.md)' "$child" 2>/dev/null | sed 's/](//' | while read target; do
    # 规范化 target 为绝对路径（去掉 ../ 等相对前缀）
    abs_target=$(realpath -m --relative-to=. "$(dirname "$child")/$target" 2>/dev/null || echo "$target")
    [ -f "$abs_target" ] || continue
    # 检查 target 是否反向链到 child（粗略：包含 child 的 basename）
    child_base=$(basename "$child")
    if ! grep -q "$child_base" "$abs_target" 2>/dev/null; then
      echo "  ⚠ child=$child → target=$target（target 未回链 child）"
    fi
  done
done
echo "=== 同级兄弟不互链扫描（示例）==="
# 在某个目录下找兄弟 README，验证是否互相链接
DIR_TO_CHECK="note/11.ai/07-llmops"
for sibling in $(find "$DIR_TO_CHECK" -name "README.md" -maxdepth 2 2>/dev/null); do
  for other in $(find "$DIR_TO_CHECK" -name "README.md" -maxdepth 2 2>/dev/null); do
    [ "$sibling" = "$other" ] && continue
    if ! grep -q "$(basename $sibling .md)" "$other" 2>/dev/null; then
      echo "  ⚠ sibling=$(basename $sibling) 未被 $(basename $other) 链接"
    fi
  done
done

# 4.6 孤岛检测 / 总目录扫描（新文件未被总目录引用）
# 原理：找最近 N 天新增的 README，验证它们是否被任何总目录表引用
echo "=== 孤岛检测 / 总目录扫描 ==="
# 找最近 7 天新增的 README（基于 git log）
SINCE_DATE=$(date -d "7 days ago" --iso-8601=seconds 2>/dev/null || date -v-7d "+%Y-%m-%dT%H:%M:%S")
NEW_FILES=$(git log --since="$SINCE_DATE" --diff-filter=A --name-only --pretty=format: 2>/dev/null | grep "\.md$" | sort -u)
for new_file in $NEW_FILES; do
  [ -z "$new_file" ] && continue
  base=$(basename "$new_file" .md)
  # 检查是否有任何 README / 总目录引用了 base
  references=$(grep -rl "\[$base\]\|\"$base\"\|/$base" note/ 2>/dev/null | wc -l)
  if [ "$references" -lt 2 ]; then
    echo "  ⚠ 新文件 $new_file 仅被 $references 处引用（建议 ≥ 2：1 个父 README + 1 个反向链）"
  fi
done

# 5. 内容重复检测（同名目录）
find note -type d -name "*engineer*" -o -name "*memory*" -o -name "*prompt*" | sort

# 6. PNG 孤儿检测
find note -name "*.png" | wc -l
grep -rl "\.png" note/ | wc -l  # 引用 PNG 的文件数
```

### Step 2: 排除已修复项（避免重复报告）

扫描结果中**必须过滤**：
- 时间戳标记（已被 commit `785896e` 清掉）
- 反直觉代码模板（已被 commit `30f6323` 清掉）
- 14 主模块的 `module:` frontmatter（已完成）
- 已沉淀的 7 个专题（dropout / claude-code / agent-memory / vector-search 三档）

**输出格式调整**：报告每条发现标注 `[NEW]`（本会话未触及）或 `[已修]`（本会话已修）。

### Step 3: ROI 分级（关键步骤）

每个发现按 **影响 × 工作量** 分到 P0/P1/P2/P3：

| 等级 | 影响 | 工作量 | 例子 |
|------|------|--------|------|
| **P0** | 高（用户易发现硬伤） | 1-2 小时 | 数字不一致 / H1 数字前缀 / 重复目录 / broken link |
| **P1** | 中（导航友好 / 深度） | 半天 | 回链覆盖率 / 同名目录歧义 / 孤儿 PNG / 双入口 |
| **P2** | 中（结构优化） | 1 天 | 子目录结构重整 / 占位 README 标注 |
| **P3** | 低（自阅读） | 1-2 小时 | CONTRIBUTING TOC / SPEC 互链 / 脚本 README |

### Step 4: 机械 vs 需判断分类（关键步骤）

每个 P0/P1 发现标注 **执行模式**：

- **🤖 机械（可派 subagent 批量）**：回链补全 / PNG 清理 / H1 改写 / 占位 README 标注
- **🧠 需判断（要 orchestrator 决策）**：目录合并 / 内容合并 / 命名风格统一 / 索引缺失补建

**机械任务**：可一次性派 subagent 执行（如"补 455 个 README 的回链"）
**判断任务**：必须 orchestrator 与用户决策后逐个处理

### Step 5: 分批执行计划（关键步骤）

**不要一次性输出 70+ 改动**！按以下方式分批：

**第一批（1 周内可完成，P0 全部）**：
- 数字一致性校对（跑 grep + sed）
- H1 数字前缀去除（5-6 个 README）
- 04.system-design/05-security 重复目录合并（1 个明确动作）
- CONTRIBUTING 引用的 docs/ + .mlc_config.json 补全

**第二批（2 周，P1 机械部分）**：
- 455 个 leaf README 补回链（脚本批量）
- 11.ai vs 13.split-hairs 同名目录加前缀
- 76 个孤儿 PNG 清理（保留 38 张教学截图）

**第三批（按需，P1/P2 判断部分）**：
- 目录合并（orchestrator 决策）
- 命名风格统一（orchestrator 决策）
- 索引缺失补建

**第四批（P3 自优化）**：
- CONTRIBUTING TOC
- SPEC 互链
- 脚本 README

## Quick Reference

| 用户问 | 输出 |
|--------|------|
| "note 哪里需要优化？" | 8 类别扫描 + P0/P1/P2/P3 优先级 + 分批执行计划 |
| "数字对吗？" | 只跑 Step 1.2（数字一致性） + Step 2 过滤 + Step 3 分级 |
| "链接有问题吗？" | 只跑 Step 1.4（回链） + Step 4 机械分类 |
| "重复内容多吗？" | 只跑 Step 1.5（重复检测） + Step 3 P2 分类 |
| "哪里缺内容？" | 只跑 Step 1.6（缺口检测） + Step 3 P1 分类 |

## Common Mistakes

### ❌ Mistake 1: 输出 70+ 改动一次性

**症状**：扫描出 70 个问题，全部列出让用户决策 → 用户瘫痪

**修复**：Step 5 必须**分批**输出；只 P0 + 关键 P1 进入第一批决策；其他延后

### ❌ Mistake 2: 不排除已修复项

**症状**：报告 270 个 "反直觉代码模板残留"（实际已被清）

**修复**：Step 2 强制过滤；本会话 commit 列表 → 排除

### ❌ Mistake 3: 用印象不用命令

**症状**：说"应该有 7 个 leaf"但没实际 find → 数字错

**修复**：Step 1 必须用 grep / find / wc 收集证据；每条发现附 file:line

### ❌ Mistake 4: 不区分机械 vs 判断

**症状**：让用户决策"455 个 README 补回链"的每一个 → 用户放弃

**修复**：Step 4 必须分类；机械任务让 subagent 自动跑；判断任务才让用户决策

### ❌ Mistake 5: ROI 标准不清晰

**症状**：P0/P1/P2/P3 是 ad-hoc 判断 → 不一致

**修复**：Step 3 用明确标准（影响 × 工作量）；标准写在本 skill "Quick Reference" 表中

### ❌ Mistake 6: 报告里只列问题不给方案

**症状**：报告"目录命名不一致"，没说怎么修

**修复**：每条发现必须配可执行方案（"重命名为 X" / "删除 Y" / "合并为 Z"）

### ❌ Mistake 7: 不验证已修状态

**症状**：报告"应该重命名 13.split-hairs/11.ai/transformer/"（实际已与主模块对齐）

**修复**：Step 2 排除本会话 commit 列表；用 git log 验证

### ❌ Mistake 8: 缺少 commit 策略

**症状**：建议"删除 76 个孤儿 PNG"，但没说用哪个 commit

**修复**：每个建议附 commit message（"chore(note): 删除孤儿 PNG"）

### ❌ Mistake 9: 单向链接扫描缺失

**症状**：审计只检查"无回链"（leaf → parent 缺失），不检查"单向回链"（parent → leaf 缺失）。例如：

- `note/11.ai/07-llmops/05-agent-evaluation/README.md` 链到 `07-llmops/README.md` —— 后者**没反向链**到前者
- `note/11.ai/03-engineering/production-agent/README.md` 链到 `11.ai/README.md` —— 后者**没反向链**到前者
- `note/11.ai/04-architecture/intelligent-system-layers/README.md` 被 `agent-architecture` 链到 —— **没反向链**

**修复**：
- **审计类别 #3 升级**："回链覆盖率" → **"回链覆盖率 + 互链双向性"**
- **Step 1.4.5 新增"单向链接扫描"**：grep 所有 child → target 链接，反查 target 是否含 child basename
- **Step 1.4.5 附"同级兄弟不互链扫描"**：在某个目录下找所有兄弟 README，验证是否互相引用

**反直觉点**：很多人以为"我加了 2 条反向链就完事" —— 实际上**新内容责任**包括：让被链接的 parent / 同级兄弟**也回链**。双向互链才能让知识网"加密"。

## Output Format

```markdown
# note 优化审计报告

> 扫描时间：YYYY-MM-DD
> 范围：仓库根目录 note/（CWD 假设）
> 排除项：本会话已修的 7 类问题（详见 Step 2）

## 总览

- README 总数：XXX
- 发现总数：XX 条
- P0：X / P1：X / P2：X / P3：X
- 机械任务：X / 判断任务：X

## 1. 数字一致性（P0，3 条）

### 1.1 [NEW] 12.story 文章数 47 vs 46
- **证据**：`note/README.md:219` 写 47；`note/12.story/index.md:3` 写 46
- **修复**：find 后统一为 47；更新 index.md
- **执行模式**：🤖 机械
- **Commit**：`fix(12.story): 数字统一 46→47`

### 1.2 [NEW] CONTRIBUTING 149 vs 116 PNG
...

## 2. H1 标题规范（P0，6 条）

...

## 3. 回链覆盖率（P1，1 条扫描）

### 3.1 [NEW] 455 / 632 README 缺回链（72%）
- **证据**：grep 统计
- **修复**：派 subagent 批量补 `← [返回: <模块>]`
- **执行模式**：🤖 机械（可脚本）
- **Commit**：`refactor(note): 全量补回链（455 文件）`

## 4. 索引缺失（P2，3 条）

...

## 分批执行计划

### 第一批（P0，1 周内）
1. 数字一致性校对（1-2 小时，🤖）
2. H1 数字前缀去除（30 分钟，🤖）
3. 04.system-design/05-security 重复目录合并（2 小时，🧠）

### 第二批（P1 机械，2 周）
1. 455 个 README 补回链（半天，🤖 脚本）
2. 76 个孤儿 PNG 清理（1 小时，🤖）

### 第三批（P1/P2 判断，按需）
1. 11.ai vs 13.split-hairs 同名目录加前缀（2 小时，🧠）
2. 13.split-hairs/03.database/ 内部结构重整（半天，🧠）

### 第四批（P3 自优化）
1. CONTRIBUTING 顶部 TOC（1 小时，🤖）
2. SPEC 互链（30 分钟，🤖）

## 风险评估

- 删除目录前确认无 frontmatter / 引用
- 数字修改前用 find 重新计数（避免虚报）
- 回链补全用脚本而非手写（避免错路径）
```

## Real-World Impact

1 次完整审计输出：~50 条发现 → 分 4 批执行 → 实际只需先做 P0（~6 项机械 + 1 项判断），其他延后。

避免的反模式：
- ❌ 70 项一次性报告（用户决策瘫痪）
- ❌ 数字虚报（与印象不一致）
- ❌ 已修项重复报告（浪费时间）
- ❌ 机械任务让用户决策（应该让 subagent 跑）

## Quick Checklist

执行前必过：
- [ ] Step 1 完成：8 类扫描全跑（grep + find）+ **3.5 孤岛检测**
- [ ] Step 2 完成：排除本会话已修项
- [ ] Step 3 完成：ROI 分级（P0/P1/P2/P3）
- [ ] Step 4 完成：机械 vs 判断分类
- [ ] Step 5 完成：分批执行计划（4 批）
- [ ] 输出报告含"总览"+"分类发现"+"分批计划"+"风险" + **孤岛清单**