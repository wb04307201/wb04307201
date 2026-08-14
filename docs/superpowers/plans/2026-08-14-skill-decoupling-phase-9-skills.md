# Skill 解耦 + Note 重构 Plan 3：3 个 Skill 重构（Phase 9）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构 `skills/note-precipitation-planning`、`skills/note-health`、`skills/note-knowledge-qa` 三个 SKILL.md，去掉硬编码定义（模块列表、6 维度评分、11 类扫描、commit 格式、50+ 词映射表），改为运行时读 `note/SPEC.md` + `<module>/SPEC.md`。同时把硬编码定义全部迁入 `note/SPEC.md` 或新增的 L2 SPEC.md。

**Architecture:** 三步走：(1) 把硬编码定义从 skill 迁入 note/SPEC.md（L0 + 已有 L1/L2 SPEC.md 已基本就位，补缺失维度）；(2) 重写 3 个 SKILL.md 只留算法骨架（含缺失 SPEC.md 行为、Phase 1–N 流程）；(3) 同步镜像到 `.claude/skills/` 和 `.codex/skills/`。

**Tech Stack:** Markdown / Git / Bash / find / grep

## Global Constraints

来自 `docs/superpowers/specs/2026-08-11-skill-decoupling-and-note-restructure-design.md` §6：

- SKILL.md 只剩算法骨架，**不含任何 note 特定定义**
- 14 模块列表改为运行时扫目录
- 6 维度 + A/B/C/D/E 评估表全部迁入 `note/SPEC.md`（已在）
- 11 类扫描规则全部迁入 `note/SPEC.md`（已在）
- commit 格式迁入 `note/SPEC.md`（已在）
- 工作分支：`refactor/skill-note-decouple`
- commit 格式：沿用 `feat(skill): ...` / `refactor(skill): ...` / `fix(skill): ...`
- 改 skill 只改 `skills/`，pre-commit hook 自动同步 `.claude/skills/` + `.codex/skills/`

---

## Phase 9.0：note/SPEC.md 维度定义补全（前置）

### Task 1: 核对 note/SPEC.md 已含的全局规则

**Files:**
- Read: `note/SPEC.md`
- Modify: `note/SPEC.md`（如缺项）

**目的:** 确认 L0 SPEC.md 已经覆盖 SKILL.md 即将迁移的所有定义，避免漏迁。

- [ ] **Step 1: 列出当前 note/SPEC.md 已含章节**

```bash
grep -n "^##" note/SPEC.md
```

期望包含：
- 全局规范
- 命名约定
- commit 格式
- 互链规则
- frontmatter 规范
- G1-G6 通用评分维度
- 11 类基础扫描规则

- [ ] **Step 2: 如发现缺失章节，按 Plan 1 Task 2 Step 1 的模板补全**

对照 Plan 1 任务的模板（commit `1fe88b0a`），补缺失章节。

- [ ] **Step 3: 验证**

```bash
wc -l note/SPEC.md
```

期望：≥ 100 行。

---

### Task 2: 把 SKILL.md 中硬编码的 commit 格式映射表迁入 note/SPEC.md

**Files:**
- Read: `skills/note-health/SKILL.md`、`skills/note-knowledge-qa/SKILL.md`、`skills/note-precipitation-planning/SKILL.md`
- Modify: `note/SPEC.md`（追加章节）

**目的:** 把 SKILL.md 中"硬编码"但实际是 note 规范的 commit 格式定义，集中存到 note/SPEC.md。

- [ ] **Step 1: 在三个 SKILL.md 中搜 "feat(note" 或 commit 格式相关硬编码**

```bash
grep -n "feat(" skills/*/SKILL.md | head -20
```

- [ ] **Step 2: 提取所有硬编码的 commit 格式片段**

记录每个 skill 文件中"commit 格式"或类似章节的位置和内容。

- [ ] **Step 3: 在 note/SPEC.md 末尾追加"commit 格式与模块映射"章节（如缺）**

```markdown
### 7. commit 格式与模块映射

| 类别 | 格式 | 用途 |
|------|------|------|
| 内容新增 | `feat(<module>): ...` | 新增 README / 子文章 |
| 内容修复 | `fix(<module>): ...` | 数字校对 / 链接修复 |
| 内容润色 | `style(<module>): ...` | 模板清理 / 错别字 |
| 结构重构 | `refactor(<module>): ...` | 目录调整 / SPEC.md 重组 |
| 文档 | `docs(<scope>): ...` | 顶层 README / CONTRIBUTING |
| 琐事 | `chore: ...` | .gitkeep / 工具脚本 |

`<module>` 为模块英文 slug（如 `01.java-and-jvm`、`13.story`）。
跨模块操作可用 `feat(note): ...` 总目录级别。
```

- [ ] **Step 4: Commit**

```bash
git add note/SPEC.md
git commit -m "feat(note): SPEC.md 补全 commit 格式与模块映射章节（从 skill 迁入）"
```

---

## Phase 9.1：note-precipitation-planning 重构

### Task 3: 抽 note-precipitation-planning 硬编码定义

**Files:**
- Read: `skills/note-precipitation-planning/SKILL.md`（1051 行）
- Modify: `skills/note-precipitation-planning/SKILL.md`

**目的:** 提取 SKILL.md 中所有硬编码定义，识别"应迁入 note/SPEC.md"vs"应删除 vs"应保留为算法骨架"。

- [ ] **Step 1: 列出当前章节结构**

```bash
grep -n "^##\|^###" skills/note-precipitation-planning/SKILL.md
```

期望章节：Step 0 主题识别 / Step 1 现状盘点 / Step 2 深度评估 / Step 3 位置决策 / Step 4 方式决策 / Step 5 选项呈现 / Step 6 实施 / Step 7 验证。

- [ ] **Step 2: 标记每个章节的属性**

对每个章节，标记三类之一：
- `[A]` 算法骨架（保留）
- `[B]` 硬编码定义（迁入 note/SPEC.md 后删除）
- `[C]` 流程指引（保留，简化表达）

- [ ] **Step 3: 输出"删除清单"**

把 `[B]` 类章节的具体内容列出来，准备在后续 Task 中从 SKILL.md 删除。

- [ ] **Step 4: 输出"新增 Step 0.5 + Step 3.5" 骨架（来自 spec §6.2）**

确认 spec §6.2 的两个新步骤已纳入计划：
- Step 0.5: 输入类型识别（URL / markdown 文章 / 多主题 / 单主题）
- Step 3.5: 目录创建/更新决策（命中已有模块 vs 新建模块）

- [ ] **Step 5: 写"重构后 SKILL.md 结构草案"**

```markdown
# note-precipitation-planning：主题沉淀规划

> **规则来源**：读 `note/SPEC.md`（G1-G6 + 11 类扫描 + commit 格式）+ `<target-module>/SPEC.md`（模块专属 A/B/C/D/E 维度）。
> **算法**：见下文 8 步流程 + Step 0.5 输入识别 + Step 3.5 目录决策。

## Step 0：scope 与主题识别
[算法]

## Step 0.5：输入类型识别（🆕）
├─ URL → WebFetch 抓取 + 主题提取
├─ 长 markdown 文章 → frontmatter 解析 + 主题提取
├─ 多主题信号 → 拆分
└─ 单主题 → 直接 Step 1

## Step 1：现状盘点
[算法：≥5 相关文件扫描]

## Step 2：深度评估
[算法：高频 + 内容深 + 缺口真实 三信号]

## Step 3：位置决策（决策树）
[算法]

## Step 3.5：目录创建/更新决策（🆕）
├─ 命中已有模块 → Step 3.5a：是否更新该模块 SPEC.md？
└─ 没找到 → Step 3.5b：是否新建模块目录？

## Step 4：方式决策
[算法：单文件/双层/三层]

## Step 5：选项呈现
[算法：2-4 选项 AskUserQuestion]

## Step 6：实施
[算法：subagent + commit 格式]

## Step 7：验证
[算法：git diff --check + 链接抽查 + 数字校对]
```

---

### Task 4: 重写 note-precipitation-planning/SKILL.md（删除硬编码）

**Files:**
- Modify: `skills/note-precipitation-planning/SKILL.md`（大幅删减）

**目的:** 删除所有硬编码定义，只留算法骨架 + Step 0.5 / Step 3.5。

- [ ] **Step 1: 删除所有 `[B]` 类硬编码章节**

按 Task 3 Step 3 的删除清单，对照删除。

- [ ] **Step 2: 简化所有 `[C]` 类流程指引**

保留算法骨架，删除冗余示例和解释。

- [ ] **Step 3: 插入 Step 0.5 与 Step 3.5 章节**

来自 Task 3 Step 5 的结构草案。

- [ ] **Step 4: 顶部加"规则来源"指针**

```markdown
> **规则来源**：执行前必读 `note/SPEC.md`（G1-G6 通用评分 + 11 类扫描 + commit 格式）以及目标模块的 `<module>/SPEC.md`（如 `note/01.java-and-jvm/SPEC.md`）。SKILL.md 不重复任何定义。
```

- [ ] **Step 5: 行数验证**

```bash
wc -l skills/note-precipitation-planning/SKILL.md
```

期望：从 1051 行大幅缩减到 ≤ 300 行（仅算法骨架）。

- [ ] **Step 6: Commit**

```bash
git add skills/note-precipitation-planning/SKILL.md
git commit -m "refactor(skill): note-precipitation-planning 重构为算法骨架（删除硬编码定义）"
```

---

## Phase 9.2：note-health 重构

### Task 5: 抽 note-health 硬编码定义

**Files:**
- Read: `skills/note-health/SKILL.md`（237 行）
- Read: `skills/note-health/references/leaf-quality.md`（363 行）
- Read: `skills/note-health/references/structural-checks.md`（1102 行）

**目的:** SKILL.md 本身相对干净（237 行），但 references/ 中含大量硬编码（leaf-quality.md 的 G1-G6 + A-G 维度、structural-checks.md 的 11 类扫描阈值）。

- [ ] **Step 1: 列出 SKILL.md 与 references/ 已含的定义**

```bash
echo "=== SKILL.md 章节 ==="
grep -n "^##\|^###" skills/note-health/SKILL.md

echo "=== leaf-quality.md 维度表 ==="
grep -nE "^\| (G[1-9]|A[1-9]|[BCDEF][1-9]) " skills/note-health/references/leaf-quality.md

echo "=== structural-checks.md 扫描规则 ==="
grep -nE "^### [0-9]+\." skills/note-health/references/structural-checks.md
```

- [ ] **Step 2: 对比 note/SPEC.md 已含维度**

```bash
grep -nE "^\| (G[1-9]|A[1-9]) " note/SPEC.md
```

**期望**：G1-G6 都在 note/SPEC.md，A1-A4 等模块专属在对应 L1/L2 SPEC.md。如果有维度在 skill 而不在 note/，迁过去。

- [ ] **Step 3: 写出"维度迁移清单"**

对每个 leaf-quality.md 中的维度：
- 若 note/SPEC.md 已含 → 删除 skill 定义
- 若只在 skill 独有 → 迁入 note/SPEC.md（如果全局）或对应 L1 SPEC.md（如果模块专属）

---

### Task 6: 迁移 leaf-quality.md 中独有的维度定义到 note/SPEC.md 或 L1 SPEC.md

**Files:**
- Modify: `note/SPEC.md`（如需追加）
- Modify: 对应 L1 SPEC.md（如需追加）

**目的:** 确保所有评估维度定义在 note 里，skill 只引用。

- [ ] **Step 1: 对照 Task 5 Step 3 的清单执行**

每个要迁的维度：
1. 在目标 SPEC.md 找到对应章节
2. 添加维度定义（2 分 / 1 分 / 0 分表格）
3. 从 leaf-quality.md 删除

- [ ] **Step 2: 验证 note/SPEC.md 含全部 G 维度**

```bash
grep -cE "^\| G[1-9] " note/SPEC.md
```

期望：6（G1-G6）

- [ ] **Step 3: Commit**

```bash
git add note/SPEC.md skills/note-health/references/leaf-quality.md
git commit -m "refactor(skill): leaf-quality 维度定义迁入 note/SPEC.md"
```

---

### Task 7: 重写 note-health/SKILL.md 与 references/

**Files:**
- Modify: `skills/note-health/SKILL.md`
- Modify: `skills/note-health/references/leaf-quality.md`
- Modify: `skills/note-health/references/structural-checks.md`
- Modify: `skills/note-health/references/new-file-baseline.md`

**目的:** SKILL.md 只留 4-7 相算法骨架，references/ 改为指针文件。

- [ ] **Step 1: SKILL.md 顶部加"规则来源"指针**

```markdown
> **规则来源**：执行前必读 `note/SPEC.md`（G1-G6 + 11 类扫描阈值）+ `<target-module>/SPEC.md`（模块专属 A/B/C/D 维度）+ `<topic>/SPEC.md`（如有 L2 强特异性）。
```

- [ ] **Step 2: 把 references/leaf-quality.md 改为指针文件**

```markdown
# leaf-quality 评分维度

**本文件已废弃**——所有维度定义已迁入 `note/SPEC.md`（G1-G6）和对应 `<module>/SPEC.md`。

**用法**：本文件保留作为旧版本兼容指针，新评分请直接读 SPEC.md。
```

- [ ] **Step 3: 把 references/structural-checks.md 改为指针文件**

```markdown
# structural-checks 结构扫描规则

**本文件已废弃**——所有 11 类扫描阈值已迁入 `note/SPEC.md`。

**用法**：直接读 `note/SPEC.md` §"11 类基础扫描规则"。
```

- [ ] **Step 4: SKILL.md 移除所有硬编码表格 / 列表**

例如把"6 维度评分表"改为：
```markdown
读 `note/SPEC.md` 的 G1-G6 维度，按各维度 2/1/0 标准打分。
```

- [ ] **Step 5: 行数验证**

```bash
echo "=== SKILL.md 行数 ==="
wc -l skills/note-health/SKILL.md
echo "=== leaf-quality.md 行数 ==="
wc -l skills/note-health/references/leaf-quality.md
echo "=== structural-checks.md 行数 ==="
wc -l skills/note-health/references/structural-checks.md
```

期望：
- SKILL.md ≤ 200 行
- leaf-quality.md ≤ 50 行（指针文件）
- structural-checks.md ≤ 50 行（指针文件）

- [ ] **Step 6: Commit**

```bash
git add skills/note-health/
git commit -m "refactor(skill): note-health SKILL.md + references/ 改为算法骨架 + 指针"
```

---

## Phase 9.3：note-knowledge-qa 重构

### Task 8: 抽 note-knowledge-qa 硬编码定义

**Files:**
- Read: `skills/note-knowledge-qa/SKILL.md`（841 行）

**目的:** QA skill 含 14 模块列表、模块映射、引用格式等硬编码。

- [ ] **Step 1: 列出章节结构**

```bash
grep -n "^##\|^###" skills/note-knowledge-qa/SKILL.md
```

- [ ] **Step 2: 标记每个章节属性**

按 `[A]` 算法 / `[B]` 硬编码定义 / `[C]` 流程指引 标记。

- [ ] **Step 3: 输出删除清单**

---

### Task 9: 重写 note-knowledge-qa/SKILL.md

**Files:**
- Modify: `skills/note-knowledge-qa/SKILL.md`

**目的:** 删除硬编码，只留 QA 检索算法骨架。

- [ ] **Step 1: 删除所有 `[B]` 类硬编码章节**

- [ ] **Step 2: 顶部加"规则来源"指针**

```markdown
> **规则来源**：检索 `note/` 时使用 grep + find，模块结构读 `note/SPEC.md` L0 + `<module>/SPEC.md` L1 + `<topic>/SPEC.md` L2。互链规则读 `note/SPEC.md` §3。
```

- [ ] **Step 3: 算法骨架保留**

QA 检索 5 步：
1. 主题解析（提取关键词）
2. 跨模块 grep + find 找候选
3. SPEC.md 读取（验证匹配）
4. 内容 Read + 交叉验证
5. 答案合成（带引用）

- [ ] **Step 4: 行数验证**

```bash
wc -l skills/note-knowledge-qa/SKILL.md
```

期望：从 841 行大幅缩减到 ≤ 300 行。

- [ ] **Step 5: Commit**

```bash
git add skills/note-knowledge-qa/SKILL.md
git commit -m "refactor(skill): note-knowledge-qa 重构为算法骨架（删除硬编码定义）"
```

---

## Phase 9.4：同步镜像

### Task 10: 同步 skills → .claude/skills + .codex/skills

**Files:**
- Modify: `.claude/skills/note-precipitation-planning/`
- Modify: `.claude/skills/note-health/`
- Modify: `.claude/skills/note-knowledge-qa/`
- Modify: `.codex/skills/`（同上 3 个）

**目的:** 让 Claude / Codex 能读到重构后的 skill。

- [ ] **Step 1: 跑 sync-skills.sh**

```bash
bash scripts/sync-skills.sh
```

- [ ] **Step 2: 验证镜像**

```bash
echo "=== .claude/skills 行数 ==="
wc -l .claude/skills/*/SKILL.md
echo "=== .codex/skills 行数 ==="
wc -l .codex/skills/*/SKILL.md
echo "=== skills/ 行数 ==="
wc -l skills/*/SKILL.md
```

期望：三处行数一致。

- [ ] **Step 3: 验证 .gitignore 正确**

```bash
grep -E "\.claude/skills|\.codex/skills" .gitignore
```

期望：两行都被忽略（不提交到 git）。

- [ ] **Step 4: 手动 commit 镜像（如 sync-skills.sh 自动提交）**

```bash
git status --short
# sync-skills.sh 应已自动提交；若无，手动：
git add .claude/skills/ .codex/skills/
git commit -m "chore: 同步重构后的 3 个 skill 到 .claude/skills/ + .codex/skills/"
```

---

## Phase 9.5：验证

### Task 11: 验证 3 个 skill 在新结构上能跑

**Files:**
- Test: 跑 3 个 skill 的最小用例

**目的:** 验证重构后 skill 仍能正常工作。

- [ ] **Step 1: 跑 note-precipitation-planning 测试用例**

模拟一个用户问："我想沉淀 LLM Quantization" — 应能：
1. 读 `note/SPEC.md` 拿全局规则
2. 扫目录定位 `note/09.ai-applications/llm-inference/weight-quantization/`（如已存在）
3. 输出沉淀方案

```bash
# 触发 skill（手动模拟）：
echo "模拟调用 note-precipitation-planning"
ls note/09.ai-applications/llm-inference/weight-quantization/ 2>/dev/null
```

- [ ] **Step 2: 跑 note-health 测试用例**

模拟"扫一遍 note" — 应能：
1. 读 `note/SPEC.md` 拿 11 类扫描
2. 跑 Phase 1 结构扫描

```bash
echo "=== Phase 1 结构扫描（验证 skill 算法） ==="
# 检查 frontmatter 覆盖率
python -c "
import os
total = ok = 0
for root, _, files in os.walk('note'):
    for f in files:
        if f != 'README.md': continue
        path = os.path.join(root, f)
        total += 1
        try:
            c = open(path, encoding='utf-8').read(200)
            if c.lstrip().startswith('<!--'): ok += 1
        except: pass
print(f'frontmatter 覆盖: {ok}/{total} = {ok*100/total:.1f}%')
"
```

- [ ] **Step 3: 跑 note-knowledge-qa 测试用例**

模拟"查 Transformer 自注意力机制" — 应能：
1. grep 找候选文件
2. 读 SPEC.md 验证
3. 输出答案带引用

```bash
echo "=== Transformer 自注意力 ==="
grep -rl "Self-Attention\|self-attention" note/08.ai-foundations/ | head -3
```

- [ ] **Step 4: 验证无硬编码定义残留**

```bash
echo "=== 检查残留硬编码 ==="
echo "--- 14 模块列表残留（应该只在 note/SPEC.md） ---"
grep -E "01\.java|11\.ai|13\.split-hairs" skills/*/SKILL.md | grep -v "note/SPEC.md" | head -5
echo "--- 6 维度表格残留（应该只在 note/SPEC.md） ---"
grep -E "^\| G[1-6] " skills/*/SKILL.md | head -5
echo "--- 11 类扫描残留（应该只在 note/SPEC.md） ---"
grep -E "11 类|11类" skills/*/SKILL.md | head -5
```

期望：所有残留指向 `note/SPEC.md` 的引用，无独立硬编码。

- [ ] **Step 5: Commit（如果有任何修复）**

```bash
git status --short
git add -A
git commit -m "fix(skill): 验证残留硬编码定义（按需修复）" || echo "无需 commit"
```

---

## 验证清单（Plan 3 完成时必过）

- [ ] 3 个 SKILL.md 都不含 14 模块列表、6 维度表格、11 类扫描、commit 格式硬编码
- [ ] 所有评估维度 / 扫描规则都在 `note/SPEC.md` 或对应 L1/L2 SPEC.md
- [ ] 3 个 SKILL.md 顶部都含"规则来源"指针
- [ ] 行数：note-precipitation-planning ≤ 300, note-health ≤ 200, note-knowledge-qa ≤ 300
- [ ] `.claude/skills/` 与 `.codex/skills/` 镜像与 `skills/` 一致
- [ ] 3 个 skill 最小测试用例通过
- [ ] pre-commit hook 自动同步正常

---

## 后续 Plans

- **Plan 4**：合并 `refactor/skill-note-decouple` → master
- **Plan 5（可选）**：note/ 剩余 broken links 批量修复（Plan 2 验收遗留）
