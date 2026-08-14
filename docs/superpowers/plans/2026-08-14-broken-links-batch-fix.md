# Plan 5：note/ 剩余 410 Broken Links 批量修复

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 note/ 剩余 410 broken links 按 9 大模式批量修复，目标 ≤ 10。每条 Edit 用 replace_all=true 高效化（一个文件内同一模式一次 Edit）。

**Architecture:** 按"目标子目录"分类，每类一个 Task，每个 Task 内部对所有受影响文件用 Edit + replace_all 修复。模式清晰映射（`01.java` → `01.java-and-jvm`、`11.ai/X` → `08.ai-foundations/Y` 或 `09.ai-applications/Z`），按映射表机械替换。

**Tech Stack:** Markdown / Edit tool / Bash / find / grep

## Global Constraints

- 工作分支：`refactor/skill-note-decouple`
- Edit 工具每次最多 replace_all=true 处理一个文件内的同一模式
- 不引入新 frontmatter（除非要替换为占位文本）
- 占位策略：`<!-- TODO: 待 Phase 9+ 迁入 -->` 用于目标不存在的链接
- commit 格式：`fix(note): 批量修复 X 处 broken links（<模式名>）`

## 当前状态（基于 2026-08-13 验证）

| 指标 | 数值 |
|---|---|
| 总 broken | 410 |
| 受影响文件 | ~190 |
| 前 30 个目标子目录覆盖 | 364/410（89%）|
| L0 SPEC.md | 已含 6 维度 + 11 类扫描 + commit 格式 |
| L1/L2 SPEC.md | 19 个全部就位 |

## 剩余 broken 按目标分布

```
   51  12.interview/11.ai            ← 多数可达（已存在），主要是路径深度错
   45  11.ai/02-technology-stack     ← 目标不存在，需迁入或映射
   44  09.ai-applications/agent      ← 路径深度错（多了 ..）
   35  11.ai/03-engineering          ← 目标不存在
   34  11.ai/08-llmops               ← 部分已迁（production-stability）
   32  12.interview/01.java          ← 路径错（应是 ../01.java-and-jvm）
   22  12.interview/09.front-end     ← 路径错（应是 ../05.frontend）
   15  09.ai-applications/04-architecture  ← 04-architecture 应是 agent/architecture
   12  03.database/04-index          ← 04-index 不存在
   11  11.ai/04-architecture         ← 目标不存在
   11  12.interview/02.computer-basics  ← 路径错
    8  09.ai-applications/rag        ← 子目录缺失（如 vector-search-at-scale）
    6  09.ai-applications/07.workflow ← 07.workflow 不存在
    6  12.interview/tools
    5  12.interview/04.system-design
    5  11.ai/05-applications
    5  11.ai/01-fundamentals
    ...
```

---

## Phase A：机械映射模式（最简单，最优先）

### Task 1: 修复 12.interview/01.java/X 引用错误深度（32 个文件）

**Files:**
- Modify: 32 个 `note/12.interview/01.java/X/README.md`（部分已修）

**目的:** 路径 `../../../../note/01.java/X` 改为 `../../../01.java-and-jvm/X`。

- [ ] **Step 1: 扫所有 12.interview/01.java 文件的旧路径**

```bash
grep -rl "../../../../note/01.java/" note/12.interview/01.java/ | head -50
```

- [ ] **Step 2: 对每个文件用 Edit 替换**

```bash
# Edit tool per file with replace_all=true
# old_string: "../../../../note/01.java/"
# new_string: "../../../01.java-and-jvm/"
```

对每个文件：

```python
# 示例（每个文件一次 Edit）
edit(file=path, old="../../../../note/01.java/", new="../../../01.java-and-jvm/", replace_all=True)
```

- [ ] **Step 3: 也处理类似路径深度问题**

如果还有 `../../../note/01.java/`（3 dots）出现：
- `../../../note/01.java/` → `../../../01.java-and-jvm/`

- [ ] **Step 4: Commit**

```bash
git add note/12.interview/01.java/
git commit -m "fix(note): 修复 12.interview/01.java 32 个文件的旧 01.java 引用深度错误"
```

---

### Task 2: 修复 12.interview/09.front-end/X 引用（22 个文件）

**Files:**
- Modify: 22 个 `note/12.interview/09.front-end/X/README.md`

**目的:** `09.front-end/` → `05.frontend/`。

- [ ] **Step 1: 扫旧引用**

```bash
grep -rl "../../.*note/09.front-end/\|09.front-end/" note/12.interview/09.front-end/ | head -30
```

- [ ] **Step 2: 对每个文件用 Edit 替换**

```
旧: ../../../../note/09.front-end/X
新: ../../../../05.frontend/X    # 路径深度不变（4 dots + note）但 note 模块已改名
```

或根据源文件深度调整：
- 源在 `note/12.interview/09.front-end/X/README.md`（depth 4）
- 目标 `note/05.frontend/X/README.md`（depth 2）
- 路径：`../../../05.frontend/X/README.md`（3 dots）

- [ ] **Step 3: Commit**

```bash
git add note/12.interview/09.front-end/
git commit -m "fix(note): 修复 12.interview/09.front-end 22 个文件的旧 frontend 引用"
```

---

### Task 3: 修复 12.interview/02.computer-basics/X 引用（11 个文件）

**Files:**
- Modify: 11 个 `note/12.interview/02.computer-basics/X/README.md`

**目的:** `02.computer-basics/` → `02.cs-foundations/`。

- [ ] **Step 1: 扫 + 替换**

```
旧: ../../../../note/02.computer-basics/X
新: ../../../02.cs-foundations/X
```

- [ ] **Step 2: Commit**

```bash
git add note/12.interview/02.computer-basics/
git commit -m "fix(note): 修复 12.interview/02.computer-basics 引用"
```

---

### Task 4: 修复 12.interview/04.system-design/X 引用（5 个文件）

**Files:**
- Modify: 5 个 `note/12.interview/04.system-design/X/README.md`

**目的:** `04.system-design/` → `06.distributed-systems/`。

- [ ] **Step 1: 扫 + 替换**

```
旧: ../../../../note/04.system-design/X
新: ../../../06.distributed-systems/X
```

- [ ] **Step 2: Commit**

```bash
git add note/12.interview/04.system-design/
git commit -m "fix(note): 修复 12.interview/04.system-design 引用"
```

---

## Phase B：跨模块深度错误（中等复杂度）

### Task 5: 修复 09.ai-applications/agent 子目录的深度错误（44 个）

**Files:**
- Modify: 多个 `note/09.ai-applications/agent/X/README.md`

**目的:** 这类文件的 broken 多是因为引用 `04-architecture/X`（应改为 `agent/architecture/X`）或深度错。

- [ ] **Step 1: 列出所有 09.ai-applications/agent/X/README.md 的 broken**

```bash
python -c "
import os, re
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
for root, _, files in os.walk('note/09.ai-applications/agent'):
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        c = open(path, encoding='utf-8', errors='ignore').read()
        for m in LINK_RE.finditer(c):
            target_rel = m.group(2).strip()
            target_abs = os.path.normpath(os.path.join(os.path.dirname(path), target_rel.replace('/', os.sep)))
            if not os.path.isfile(target_abs):
                print(f'  {path} -> {target_rel}')
" | head -50
```

- [ ] **Step 2: 按映射表修复**

常见映射：
- `04-architecture/X` → `agent/architecture/X`（深度相应调整）
- `03-engineering/X` → `agent/X`（如 ai-platforms/loop-engineering）

- [ ] **Step 3: 对每个文件用 Edit 替换**

- [ ] **Step 4: Commit**

```bash
git add note/09.ai-applications/agent/
git commit -m "fix(note): 修复 agent/ 子目录的深度错误"
```

---

### Task 6: 修复 12.interview/11.ai 引用深度（51 个）

**Files:**
- Modify: 多个 `note/12.interview/11.ai/X/README.md` 和 `note/12.interview/11.ai/README.md`

**目的:** 这类文件大部分在 `note/12.interview/11.ai/`，引用同级目录或主模块时深度错。

- [ ] **Step 1: 列出剩余 broken**

```bash
python -c "
import os, re
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
for root, _, files in os.walk('note/12.interview/11.ai'):
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        c = open(path, encoding='utf-8', errors='ignore').read()
        for m in LINK_RE.finditer(c):
            target_rel = m.group(2).strip()
            target_abs = os.path.normpath(os.path.join(os.path.dirname(path), target_rel.replace('/', os.sep)))
            if not os.path.isfile(target_abs):
                print(f'  {path} -> {target_rel}')
" | head -50
```

- [ ] **Step 2: 按通用映射修复**

例如：
- `../../../note/11.ai/X` → `../../../09.ai-applications/Y/Z`（重映射）
- `../../11.ai/X`（3 dots 错误）→ `../11.ai/X`（深度调整）

- [ ] **Step 3: 对每个文件 Edit + replace_all**

- [ ] **Step 4: Commit**

```bash
git add note/12.interview/11.ai/
git commit -m "fix(note): 修复 12.interview/11.ai 多个 README 的引用深度错误"
```

---

## Phase C：缺失目标文件（最复杂，需迁移或占位）

### Task 7: 迁移 11.ai/02-technology-stack/vector-search-at-scale 等 RAG 子目录

**Files:**
- Create: `note/09.ai-applications/rag/vector-search-at-scale/README.md`
- Create: `note/09.ai-applications/rag/vector-search-trillion/README.md`

**目的:** RAG 子主题下缺 2 个 README。

- [ ] **Step 1: 从 master 提取**

```bash
git show master:note/11.ai/02-technology-stack/vector-search-at-scale/README.md > note/09.ai-applications/rag/vector-search-at-scale/README.md
git show master:note/11.ai/02-technology-stack/vector-search-trillion/README.md > note/09.ai-applications/rag/vector-search-trillion/README.md
```

- [ ] **Step 2: 加 frontmatter**

每个文件加 frontmatter（如 `references/leaf-quality.md` 的 G1-G6）。

- [ ] **Step 3: 修复 broken 链接（从 `11.ai/02-technology-stack/X` 指向这些新文件）**

```bash
grep -rl "11.ai/02-technology-stack/vector-search" note/ | head -20
```

- [ ] **Step 4: 更新 RAG MOC README 引用**

`note/09.ai-applications/rag/README.md` 加上这 2 个新文件。

- [ ] **Step 5: Commit**

```bash
git add note/09.ai-applications/rag/
git commit -m "feat(note): 补 RAG MOC 的 vector-search-at-scale + trillion 子目录"
```

---

### Task 8: 11.ai 缺失文件迁移（按需，剩余 ~30 篇）

**Files:**
- Create: 多个目标位置

**目的:** 11.ai/01-fundamentals、03-engineering、04-architecture、05-applications、07-research、08-llmops 中还有 ~30 篇未迁入新结构。

- [ ] **Step 1: 列出仍缺失的 11.ai 文件**

```bash
python -c "
import os, subprocess
master_paths = [p.replace('note/11.ai/', '') for p in subprocess.check_output(['git', 'ls-tree', '-r', 'master', '--name-only'], text=True).splitlines() if p.startswith('note/11.ai/')]
current_basenames = set()
for root, _, files in os.walk('note'):
    for f in files:
        if f.endswith('.md'): current_basenames.add(f)
missing = [m for m in master_paths if os.path.basename(m) not in current_basenames]
print('\n'.join(missing))
"
```

- [ ] **Step 2: 对每个缺失文件，决定目标位置并迁移**

| 源 | 目标 |
|---|---|
| `11.ai/01-fundamentals/X/Y` | `08.ai-foundations/X/Y` |
| `11.ai/03-engineering/X/Y` | `09.ai-applications/agent/X/Y` |
| `11.ai/04-architecture/X/Y` | `09.ai-applications/agent/X/Y` |
| `11.ai/05-applications/X/Y` | `09.ai-applications/agent/X/Y` |
| `11.ai/07-research/X/Y` | `09.ai-applications/fine-tuning/X/Y` |
| `11.ai/08-llmops/X/Y` | `09.ai-applications/agent/X/Y` |

- [ ] **Step 3: 用 git mv 或 cp + add**

- [ ] **Step 4: 更新引用这些文件的 broken links**

- [ ] **Step 5: Commit**

```bash
git add note/
git commit -m "feat(note): 补 11.ai 剩余 ~30 篇缺失内容"
```

---

### Task 9: 占位处理：目标完全不存在且无合适映射

**Files:**
- Modify: 多个含无法修复链接的文件

**目的:** 对于目标文件不存在且没有合适迁移位置的 broken link，把链接替换为占位文本。

- [ ] **Step 1: 列出剩余无法迁移的 broken**

跑全库扫描后人工审核（找无合适目标的）。

- [ ] **Step 2: 对每个，替换为占位**

```
旧: [目标描述](../../../path/to/missing.md)
新: 目标描述（<!-- TODO: 待 Phase 9+ 迁入 -->）
```

- [ ] **Step 3: Commit**

```bash
git add note/
git commit -m "fix(note): 无合适目标的 broken 替换为 TODO 占位"
```

---

## Phase D：最终验证

### Task 10: 全库 broken links 终扫 + 数字校对

- [ ] **Step 1: 跑最终 broken links 扫描**

```bash
python -c "
import os, re
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
total = 0
for root, _, files in os.walk('note'):
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        c = open(path, encoding='utf-8', errors='ignore').read()
        for m in LINK_RE.finditer(c):
            target_rel = m.group(2).strip()
            target_abs = os.path.normpath(os.path.join(os.path.dirname(path), target_rel.replace('/', os.sep)))
            if not os.path.isfile(target_abs):
                total += 1
print(f'Total broken: {total}')
"
```

期望：≤ 10

- [ ] **Step 2: 数字校对**

```bash
echo "总 .md 数: $(find note -name '*.md' | wc -l)"     # 期望 ~1064
echo "SPEC.md 数: $(find note -name 'SPEC.md' | wc -l)" # 期望 19
echo "README 数: $(find note -name 'README.md' | wc -l)" # 期望 ~748
echo "frontmatter 覆盖: $(find note -name 'README.md' -exec grep -l '^<!--' {} \; | wc -l)/$(find note -name 'README.md' | wc -l)"
```

- [ ] **Step 3: SPEC.md 继承验证**

```bash
python -c "
import os, re
INHERIT_RE = re.compile(r'Inherits from[^>]*?\[([^\]]+)\]\(([^)]+)\)')
broken = 0
for root, _, files in os.walk('note'):
    for f in files:
        if f != 'SPEC.md': continue
        path = os.path.join(root, f)
        c = open(path, encoding='utf-8', errors='ignore').read()
        m = INHERIT_RE.search(c)
        if not m: continue
        target = m.group(2).strip()
        target_abs = os.path.normpath(os.path.join(os.path.dirname(path), target.replace('/', os.sep)))
        if not os.path.isfile(target_abs):
            broken += 1
            print(f'  BROKEN: {path} -> {target}')
print(f'Inherits broken: {broken}')
"
```

期望：0 broken。

- [ ] **Step 4: 最终 commit（如有修复）**

```bash
git add note/
git commit -m "fix(note): Plan 5 终扫与数字校对" || echo "无需 commit"
```

---

## 验证清单（Plan 5 完成时必过）

- [ ] note/ broken links ≤ 10
- [ ] 所有原 `01.java` / `02.computer-basics` / `04.system-design` / `09.front-end` 引用已迁移
- [ ] 所有原 `11.ai` 子目录引用要么迁入新位置，要么 TODO 占位
- [ ] 13 模块 + 19 SPEC.md 完整
- [ ] frontmatter 覆盖 100%
- [ ] 工作树干净（`git status --short` 空）

---

## 后续 Plans

- **Plan 4**：合并 `refactor/skill-note-decouple` → master
