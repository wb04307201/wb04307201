# note-health Batch 1–5 Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 note-health 报告中的导航、统计、事实、格式和 71 篇限定质量问题，并在独立分支形成可验证、可回退的分批 commit。

**Architecture:** 采用风险优先流水线：Batch 1 导航 → Batch 2 统计 → Batch 3 事实 → Batch 4 格式/结构 → Batch 5 质量。导航与围栏通过 tracked manifest 切成每块不超过 25 个文件；正文逐文件 Edit，Python/Bash 仅执行只读枚举和验证。

**Tech Stack:** Markdown、Git、Python 3.13+、Git Bash、Claude Code Read/Edit/Grep、Context7/官方网页（事实核验）。

## Global Constraints

- 实施分支固定为 `fix/note-health-remediation`；不 push、不创建 PR。
- tracked Markdown 禁止批量写脚本；脚本仅做只读枚举、统计和验证。
- 每个 commit 只处理一个 module/chunk/事实主题，一般不超过 30 个文件。
- 不修改 `.gitignore`、`.obsidian`、`.idea`、`.vscode`，不删除 tracked 文件。
- 外部事实优先官方文档、标准、项目公告或原始论文；无法核实的精确数字删除或标为示例假设。
- 三级非 README `.md` 的 frontmatter 按需；`index-only` 不因行数短扩写。
- 任一验证失败时不 commit；先修复当前 chunk。
- 每个 commit 必须以 `Co-Authored-By: Claude <noreply@anthropic.com>` 结尾。

## File / Manifest Map

| 文件 | 责任 |
|---|---|
| `docs/superpowers/specs/2026-07-20-note-health-batch-remediation-design.md` | 批次边界和验收标准 |
| `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation.md` | 初始导航问题全量快照 |
| `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md` | Batch 1 每块 ≤25 文件的精确清单 |
| `docs/superpowers/plans/manifests/2026-07-20-note-health-bare-fences.md` | 1824 处裸围栏原始行号 |
| `docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md` | Batch 4 每块 ≤25 文件的精确清单 |
| `docs/superpowers/plans/manifests/2026-07-20-note-health-structure-candidates.md` | H1、定位、浅 index、占位和模板候选 |
| `docs/superpowers/plans/manifests/2026-07-20-note-health-structure-chunks.md` | 模板/占位候选每块 ≤25 文件的精确清单 |
| `docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` | 71 篇逐文件 findings 与 Outcome |
| `docs/superpowers/plans/2026-07-20-note-health-batch-remediation-results.md` | 最终修复前后指标、commit 和未解决项 |

## Reusable Verification Commands

### V1 — README footer 自链

```bash
python - <<'PY'
import re
from pathlib import Path
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for p in Path('note').rglob('README.md'):
    if '.health-tmp' in p.parts:
        continue
    if pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(p.as_posix())
print(f'self_return_files={len(bad)}')
for p in bad:
    print(p)
PY
```

Expected after Batch 1: `self_return_files=0`.

### V2 — README / Markdown / split-hairs counts

```bash
python - <<'PY'
from pathlib import Path
note = Path('note')
md = [p for p in note.rglob('*.md') if '.health-tmp' not in p.parts]
readmes = [p for p in md if p.name == 'README.md']
print('md', len(md), 'readme', len(readmes))
root = note / '13.split-hairs'
total = 0
for d in sorted(p for p in root.iterdir() if p.is_dir()):
    n = sum(p != d / 'README.md' for p in d.rglob('README.md'))
    print(d.name, n)
    total += n
print('split_hairs_total', total)
PY
```

Expected before content additions: `md 1042`, `readme 765`, `split_hairs_total 192`.

### V3 — 裸 opening fence

```bash
python - <<'PY'
from pathlib import Path
bad = []
for p in Path('note').rglob('*.md'):
    if '.health-tmp' in p.parts:
        continue
    opened = False
    for n, line in enumerate(p.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('```'):
            if not opened and stripped == '```':
                bad.append(f'{p.as_posix()}:{n}')
            opened = not opened
print(f'bare_openings={len(bad)}')
for row in bad:
    print(row)
PY
```

Expected after Batch 4: `bare_openings=0`.

### V4 — 通用 diff gate

```bash
git diff --check
git status --short
```

Expected: `git diff --check` 无输出；status 只包含当前任务声明的文件。

---
### Task 1: Preflight and Baseline Freeze
**Files:**
- Modify: none (read-only preflight)
- Read: `docs/superpowers/specs/2026-07-20-note-health-batch-remediation-design.md`
- Read: all manifests in `docs/superpowers/plans/manifests/`
**Interfaces:**
- Consumes: approved spec, current branch and tracked manifests
- Produces: verified baseline and empty implementation diff
- [ ] **Step 1: Verify branch and clean baseline**

```bash
git branch --show-current
git status --short
```

Expected: branch is `fix/note-health-remediation`; status is clean after the plan commit.

- [ ] **Step 2: Run V1, V2 and V3**

Expected baseline: 225 README self-return files, 1042 Markdown, 765 README, 192 split-hairs articles, 1824 bare openings. If counts differ, update manifests and this plan in one `docs(note)` commit before editing note content.

- [ ] **Step 3: Confirm forbidden paths are untouched**

```bash
git status --short -- .gitignore note/.obsidian .idea .vscode
```

Expected: no output.
### Task 2: Batch 1 Navigation — 01.java
**Files:**
- Modify: exact files under `NAV-01` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-02` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-03` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-04` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-05` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-01, NAV-02, NAV-03, NAV-04, NAV-05
- Produces: valid return/link/index wiring for 01.java; one commit per NAV chunk
- [ ] **Step: Repair NAV-01 (collection)**
Open section `NAV-01` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(01.java): 修复 collection 导航链接 (NAV-01)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-02 (concepts)**
Open section `NAV-02` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(01.java): 修复 concepts 导航链接 (NAV-02)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-03 (concurrency)**
Open section `NAV-03` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(01.java): 修复 concurrency 导航链接 (NAV-03)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-04 (design-patterns)**
Open section `NAV-04` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(01.java): 修复 design-patterns 导航链接 (NAV-04)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-05 (io)**
Open section `NAV-05` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(01.java): 修复 io 导航链接 (NAV-05)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 3: Batch 1 Navigation — 02.computer-basics
**Files:**
- Modify: exact files under `NAV-06` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-07` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-06, NAV-07
- Produces: valid return/link/index wiring for 02.computer-basics; one commit per NAV chunk
- [ ] **Step: Repair NAV-06 (01-network)**
Open section `NAV-06` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(02.computer-basics): 修复 01-network 导航链接 (NAV-06)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-07 (02-algorithms)**
Open section `NAV-07` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(02.computer-basics): 修复 02-algorithms 导航链接 (NAV-07)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 4: Batch 1 Navigation — 03.database
**Files:**
- Modify: exact files under `NAV-08` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-08
- Produces: valid return/link/index wiring for 03.database; one commit per NAV chunk
- [ ] **Step: Repair NAV-08 (README.md)**
Open section `NAV-08` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(03.database): 修复 README.md 导航链接 (NAV-08)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 5: Batch 1 Navigation — 04.system-design
**Files:**
- Modify: exact files under `NAV-09` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-10` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-11` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-12` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-13` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-14` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-15` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-16` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-09, NAV-10, NAV-11, NAV-12, NAV-13, NAV-14, NAV-15, NAV-16
- Produces: valid return/link/index wiring for 04.system-design; one commit per NAV chunk
- [ ] **Step: Repair NAV-09 (01-foundation)**
Open section `NAV-09` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(04.system-design): 修复 01-foundation 导航链接 (NAV-09)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-10 (02-distributed)**
Open section `NAV-10` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(04.system-design): 修复 02-distributed 导航链接 (NAV-10)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-11 (03-high-availability)**
Open section `NAV-11` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(04.system-design): 修复 03-high-availability 导航链接 (NAV-11)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-12 (04-high-performance)**
Open section `NAV-12` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(04.system-design): 修复 04-high-performance 导航链接 (NAV-12)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-13 (05-security)**
Open section `NAV-13` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(04.system-design): 修复 05-security 导航链接 (NAV-13)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-14 (06-idempotency)**
Open section `NAV-14` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(04.system-design): 修复 06-idempotency 导航链接 (NAV-14)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-15 (07-deployment)**
Open section `NAV-15` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(04.system-design): 修复 07-deployment 导航链接 (NAV-15)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-16 (09-emerging-tech)**
Open section `NAV-16` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(04.system-design): 修复 09-emerging-tech 导航链接 (NAV-16)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 6: Batch 1 Navigation — 05.tools
**Files:**
- Modify: exact files under `NAV-17` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-18` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-19` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-20` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-17, NAV-18, NAV-19, NAV-20
- Produces: valid return/link/index wiring for 05.tools; one commit per NAV chunk
- [ ] **Step: Repair NAV-17 (02-docker)**
Open section `NAV-17` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(05.tools): 修复 02-docker 导航链接 (NAV-17)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-18 (04-nginx)**
Open section `NAV-18` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(05.tools): 修复 04-nginx 导航链接 (NAV-18)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-19 (05-monorepo)**
Open section `NAV-19` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(05.tools): 修复 05-monorepo 导航链接 (NAV-19)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-20 (06-ali-microservices)**
Open section `NAV-20` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(05.tools): 修复 06-ali-microservices 导航链接 (NAV-20)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 7: Batch 1 Navigation — 06.spring
**Files:**
- Modify: exact files under `NAV-21` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-22` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-23` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-24` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-25` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-21, NAV-22, NAV-23, NAV-24, NAV-25
- Produces: valid return/link/index wiring for 06.spring; one commit per NAV chunk
- [ ] **Step: Repair NAV-21 (01-core)**
Open section `NAV-21` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(06.spring): 修复 01-core 导航链接 (NAV-21)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-22 (02-web)**
Open section `NAV-22` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(06.spring): 修复 02-web 导航链接 (NAV-22)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-23 (03-data)**
Open section `NAV-23` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(06.spring): 修复 03-data 导航链接 (NAV-23)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-24 (05-spring-cloud)**
Open section `NAV-24` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(06.spring): 修复 05-spring-cloud 导航链接 (NAV-24)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-25 (06-integration)**
Open section `NAV-25` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(06.spring): 修复 06-integration 导航链接 (NAV-25)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 8: Batch 1 Navigation — 07.workflow
**Files:**
- Modify: exact files under `NAV-26` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-27` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-28` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-26, NAV-27, NAV-28
- Produces: valid return/link/index wiring for 07.workflow; one commit per NAV chunk
- [ ] **Step: Repair NAV-26 (apache-eventmesh)**
Open section `NAV-26` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(07.workflow): 修复 apache-eventmesh 导航链接 (NAV-26)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-27 (define)**
Open section `NAV-27` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(07.workflow): 修复 define 导航链接 (NAV-27)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-28 (process-engine)**
Open section `NAV-28` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(07.workflow): 修复 process-engine 导航链接 (NAV-28)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 9: Batch 1 Navigation — 08.application-systems
**Files:**
- Modify: exact files under `NAV-29` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-30` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-31` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-32` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-33` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-34` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-29, NAV-30, NAV-31, NAV-32, NAV-33, NAV-34
- Produces: valid return/link/index wiring for 08.application-systems; one commit per NAV chunk
- [ ] **Step: Repair NAV-29 (01-rd-innovation)**
Open section `NAV-29` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(08.application-systems): 修复 01-rd-innovation 导航链接 (NAV-29)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-30 (02-production)**
Open section `NAV-30` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(08.application-systems): 修复 02-production 导航链接 (NAV-30)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-31 (03-supply-chain)**
Open section `NAV-31` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(08.application-systems): 修复 03-supply-chain 导航链接 (NAV-31)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-32 (04-sales-service)**
Open section `NAV-32` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(08.application-systems): 修复 04-sales-service 导航链接 (NAV-32)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-33 (05-operations)**
Open section `NAV-33` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(08.application-systems): 修复 05-operations 导航链接 (NAV-33)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-34 (06-specialized)**
Open section `NAV-34` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(08.application-systems): 修复 06-specialized 导航链接 (NAV-34)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 10: Batch 1 Navigation — 09.front-end
**Files:**
- Modify: exact files under `NAV-35` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-35
- Produces: valid return/link/index wiring for 09.front-end; one commit per NAV chunk
- [ ] **Step: Repair NAV-35 (08-cross-platform)**
Open section `NAV-35` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(09.front-end): 修复 08-cross-platform 导航链接 (NAV-35)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 11: Batch 1 Navigation — 10.big-data
**Files:**
- Modify: exact files under `NAV-36` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-37` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-38` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-36, NAV-37, NAV-38
- Produces: valid return/link/index wiring for 10.big-data; one commit per NAV chunk
- [ ] **Step: Repair NAV-36 (03-realtime-compute)**
Open section `NAV-36` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(10.big-data): 修复 03-realtime-compute 导航链接 (NAV-36)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-37 (04-data-lake)**
Open section `NAV-37` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(10.big-data): 修复 04-data-lake 导航链接 (NAV-37)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-38 (05-olap)**
Open section `NAV-38` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(10.big-data): 修复 05-olap 导航链接 (NAV-38)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 12: Batch 1 Navigation — 11.ai
**Files:**
- Modify: exact files under `NAV-39` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-40` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-41` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-42` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-43` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-44` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-45` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-39, NAV-40, NAV-41, NAV-42, NAV-43, NAV-44, NAV-45
- Produces: valid return/link/index wiring for 11.ai; one commit per NAV chunk
- [ ] **Step: Repair NAV-39 (01-fundamentals)**
Open section `NAV-39` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(11.ai): 修复 01-fundamentals 导航链接 (NAV-39)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-40 (02-technology-stack)**
Open section `NAV-40` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(11.ai): 修复 02-technology-stack 导航链接 (NAV-40)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-41 (03-engineering)**
Open section `NAV-41` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(11.ai): 修复 03-engineering 导航链接 (NAV-41)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-42 (04-architecture)**
Open section `NAV-42` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(11.ai): 修复 04-architecture 导航链接 (NAV-42)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-43 (05-applications)**
Open section `NAV-43` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(11.ai): 修复 05-applications 导航链接 (NAV-43)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-44 (07-research)**
Open section `NAV-44` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(11.ai): 修复 07-research 导航链接 (NAV-44)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-45 (08-llmops)**
Open section `NAV-45` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(11.ai): 修复 08-llmops 导航链接 (NAV-45)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 13: Batch 1 Navigation — 12.story
**Files:**
- Modify: exact files under `NAV-46` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-47` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-48` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-49` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-50` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-51` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-52` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-53` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-54` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-55` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-56` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-57` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-58` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-59` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-60` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-61` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-62` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-63` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-64` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-65` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-66` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-67` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-46, NAV-47, NAV-48, NAV-49, NAV-50, NAV-51, NAV-52, NAV-53, NAV-54, NAV-55, NAV-56, NAV-57, NAV-58, NAV-59, NAV-60, NAV-61, NAV-62, NAV-63, NAV-64, NAV-65, NAV-66, NAV-67
- Produces: valid return/link/index wiring for 12.story; one commit per NAV chunk
- [ ] **Step: Repair NAV-46 (01-ai-agent-architecture.md)**
Open section `NAV-46` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 01-ai-agent-architecture.md 导航链接 (NAV-46)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-47 (02-system-architecture-evolution.md)**
Open section `NAV-47` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 02-system-architecture-evolution.md 导航链接 (NAV-47)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-48 (11-ai-learning-paradox.md)**
Open section `NAV-48` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 11-ai-learning-paradox.md 导航链接 (NAV-48)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-49 (25-ai-org-transformation.md)**
Open section `NAV-49` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 25-ai-org-transformation.md 导航链接 (NAV-49)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-50 (26-ai-native-startup.md)**
Open section `NAV-50` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 26-ai-native-startup.md 导航链接 (NAV-50)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-51 (27-self-evolving-company.md)**
Open section `NAV-51` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 27-self-evolving-company.md 导航链接 (NAV-51)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-52 (28-ai-hallucination-safety.md)**
Open section `NAV-52` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 28-ai-hallucination-safety.md 导航链接 (NAV-52)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-53 (29-codebase-cognitive-debt.md)**
Open section `NAV-53` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 29-codebase-cognitive-debt.md 导航链接 (NAV-53)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-54 (30-agent-harness.md)**
Open section `NAV-54` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 30-agent-harness.md 导航链接 (NAV-54)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-55 (31-ai-fatal-trio.md)**
Open section `NAV-55` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 31-ai-fatal-trio.md 导航链接 (NAV-55)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-56 (32a-ai-evaluation-fundamentals.md)**
Open section `NAV-56` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 32a-ai-evaluation-fundamentals.md 导航链接 (NAV-56)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-57 (32b-ai-evaluation-pipeline.md)**
Open section `NAV-57` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 32b-ai-evaluation-pipeline.md 导航链接 (NAV-57)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-58 (33a-mcp-protocol.md)**
Open section `NAV-58` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 33a-mcp-protocol.md 导航链接 (NAV-58)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-59 (33b-a2a-protocol.md)**
Open section `NAV-59` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 33b-a2a-protocol.md 导航链接 (NAV-59)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-60 (34a-ai-token-cost-structure.md)**
Open section `NAV-60` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 34a-ai-token-cost-structure.md 导航链接 (NAV-60)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-61 (34b-ai-token-cost-optimization.md)**
Open section `NAV-61` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 34b-ai-token-cost-optimization.md 导航链接 (NAV-61)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-62 (35-ai-observability.md)**
Open section `NAV-62` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 35-ai-observability.md 导航链接 (NAV-62)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-63 (36-rag-retrieval-augmented-generation.md)**
Open section `NAV-63` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 36-rag-retrieval-augmented-generation.md 导航链接 (NAV-63)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-64 (37-vector-database-and-embedding.md)**
Open section `NAV-64` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 37-vector-database-and-embedding.md 导航链接 (NAV-64)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-65 (38-ai-compliance-and-regulation.md)**
Open section `NAV-65` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 38-ai-compliance-and-regulation.md 导航链接 (NAV-65)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-66 (39-ai-private-deployment.md)**
Open section `NAV-66` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 39-ai-private-deployment.md 导航链接 (NAV-66)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-67 (STORY-FORMAT-SPEC.md)**
Open section `NAV-67` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(12.story): 修复 STORY-FORMAT-SPEC.md 导航链接 (NAV-67)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 14: Batch 1 Navigation — 13.split-hairs
**Files:**
- Modify: exact files under `NAV-68` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-69` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-70` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-71` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-72` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-73` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-74` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-75` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-76` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-77` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
- Modify: exact files under `NAV-78` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-68, NAV-69, NAV-70, NAV-71, NAV-72, NAV-73, NAV-74, NAV-75, NAV-76, NAV-77, NAV-78
- Produces: valid return/link/index wiring for 13.split-hairs; one commit per NAV chunk
- [ ] **Step: Repair NAV-68 (01.java)**
Open section `NAV-68` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 01.java 导航链接 (NAV-68)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-69 (01.java)**
Open section `NAV-69` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 01.java 导航链接 (NAV-69)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-70 (02.computer-basics)**
Open section `NAV-70` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 02.computer-basics 导航链接 (NAV-70)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-71 (03.database)**
Open section `NAV-71` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 03.database 导航链接 (NAV-71)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-72 (04.system-design)**
Open section `NAV-72` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 04.system-design 导航链接 (NAV-72)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-73 (05.security)**
Open section `NAV-73` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 05.security 导航链接 (NAV-73)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-74 (06.spring)**
Open section `NAV-74` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 06.spring 导航链接 (NAV-74)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-75 (09.front-end)**
Open section `NAV-75` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 09.front-end 导航链接 (NAV-75)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-76 (09.front-end)**
Open section `NAV-76` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 09.front-end 导航链接 (NAV-76)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-77 (11.ai)**
Open section `NAV-77` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 11.ai 导航链接 (NAV-77)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Repair NAV-78 (11.ai)**
Open section `NAV-78` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(13.split-hairs): 修复 11.ai 导航链接 (NAV-78)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 15: Batch 1 Navigation — 14.project-management
**Files:**
- Modify: exact files under `NAV-79` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-79
- Produces: valid return/link/index wiring for 14.project-management; one commit per NAV chunk
- [ ] **Step: Repair NAV-79 (scripts)**
Open section `NAV-79` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(14.project-management): 修复 scripts 导航链接 (NAV-79)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 16: Batch 1 Navigation — README.md
**Files:**
- Modify: exact files under `NAV-80` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`
**Interfaces:**
- Consumes: NAV chunks NAV-80
- Produces: valid return/link/index wiring for README.md; one commit per NAV chunk
- [ ] **Step: Repair NAV-80 (_root)**
Open section `NAV-80` in `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation-chunks.md`. Read every listed source and its listed/derived parent README. Apply only the defect rows in that section: replace README self-links with the actual parent path, fix broken targets to existing slugs, and add orphan/one-way child entries to the closest parent index. Do not alter ordinary `.md -> README.md` links that correctly return to a same-directory index.
- [ ] **Step: Verify this chunk before commit**
Run V4, then inspect every modified README footer with:
```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True, encoding='utf-8').splitlines()
pat = re.compile(r"\[[^\]]*返回[^\]]*\]\(README\.md\)")
bad = []
for name in files:
    p = Path(name)
    if p.name == 'README.md' and p.exists() and pat.search(p.read_text(encoding='utf-8', errors='ignore')):
        bad.append(name)
print('modified_self_links', len(bad))
print('
'.join(bad))
PY
```

Expected: `modified_self_links 0`.
- [ ] **Step: Commit this chunk**
```bash
git add note
git commit -m "fix(README.md): 修复 _root 导航链接 (NAV-80)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Run module gate**
Run V1 and filter output for this module; no path from the completed module may remain. Run `git diff --check` and confirm the worktree is clean after the last chunk commit.
### Task 17: Batch 1 Global Navigation Gate
**Files:**
- Read: `docs/superpowers/plans/manifests/2026-07-20-note-health-navigation.md`
- Modify: only files still reported by the final navigation scan
**Interfaces:**
- Consumes: all Batch 1 module commits
- Produces: selfReturnFiles=0, wrongLeafReturnLinks=0, brokenLinks=0, orphanMarkdown=0, leafReturnCoverage=634/634
- [ ] **Step 1: Run V1 and full local-link/return scan**

Run V1. Then run the note-health structural scan from the approved design/report environment; if `note/.health-tmp/structural_scan.py` is unavailable, regenerate the read-only scanner from `skills/note-health/references/structural-checks.md`.

Expected: `selfReturnFiles=0`, `wrongLeafReturnLinks=0`, `brokenLinks=0`, `orphanMarkdown=0`, `leafReturnCoverage=634/634`.

- [ ] **Step 2: Close residuals**

For each residual, read source and closest parent, fix it as a dedicated module commit, and rerun the same scan. Do not proceed to Batch 2 while any Batch 1 metric is nonzero.
### Task 18: Batch 2 Index and Statistics Consistency
**Files:**
- Modify: `note/README.md`
- Modify: `note/13.split-hairs/README.md`
- Modify: `note/13.split-hairs/01.java/README.md`
- Modify: `note/13.split-hairs/11.ai/README.md`
- Modify: other `note/13.split-hairs/*/README.md` that declare article counts
- Modify: `note/CONTRIBUTING.md`
**Interfaces:**
- Consumes: Batch 1 clean navigation and V2 live counts
- Produces: all displayed counts equal live enumeration
- [ ] **Step 1: Run V2 and capture actual counts**

Expected baseline is 1042 Markdown, 765 README, and split-hairs 39/6/26/19/10/16/26/6/40/4 = 192. Use live values if preceding valid edits changed counts.

- [ ] **Step 2: Update every duplicated count surface**

Update root prose, navigation tables, module positioning text, frontmatter summaries, child list headings, CONTRIBUTING headings/progress notes, and dated count statements. Keep one explicit “find 校对” date per statistics block.

- [ ] **Step 3: Verify sums and stale-number absence**

Run V2. Search the touched files for stale `174`, `697`, `18 题`, `38 题`, `20 题`, and category counts that no longer match V2; each match must either be historical context labeled as such or be updated.

- [ ] **Step 4: Commit Batch 2**
```bash
git add note/README.md note/13.split-hairs note/CONTRIBUTING.md
git commit -m "fix(indexes): 校准 split-hairs 与 README 统计" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 19: Batch 3 — Spring facts and executable validation examples
**Files:**
- Modify: `note/06.spring/03-data/transaction/propagation-and-isolation.md`
- Modify: `note/06.spring/06-integration/validation/cross-field.md`
**Interfaces:**
- Consumes: approved P0/P1 verification and official primary sources
- Produces: correct, sourced or explicitly illustrative claims
- [ ] **Step 1: Read the complete files and primary references**
For library/framework details use Context7 first; for project timelines/case data use official project or organization sources. Record clickable sources in the Markdown, not only in the commit message.
- [ ] **Step 2: Change the MySQL InnoDB default isolation statement to REPEATABLE_READ everywhere; qualify REQUIRES_NEW connection behavior by TransactionManager.**
- [ ] **Step 3: Change ScriptAssert object access from `_` to `_this`; explain JSR-223 engine requirements and recommend a class-level custom validator for modern JDKs.**
- [ ] **Step: Validate examples and links**
Check code/config syntax by inspection against the cited version; run the local-link scan and V4. No exact number may remain without source, environment or explicit “示例假设” label.
- [ ] **Step: Commit this fact group**
```bash
git add note/06.spring/03-data/transaction/propagation-and-isolation.md note/06.spring/06-integration/validation/cross-field.md
git commit -m "fix(06.spring): 修正事务与跨字段校验事实" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 20: Batch 3 — Workflow facts and runnable snippets
**Files:**
- Modify: `note/07.workflow/apache-eventmesh/README.md`
- Modify: `note/07.workflow/apache-eventmesh/cloud-flow/README.md`
- Modify: `note/07.workflow/process-engine/README.md`
- Modify: `note/07.workflow/workflow-and-microservice-orchestration/README.md`
**Interfaces:**
- Consumes: approved P0/P1 verification and official primary sources
- Produces: correct, sourced or explicitly illustrative claims
- [ ] **Step 1: Read the complete files and primary references**
For library/framework details use Context7 first; for project timelines/case data use official project or organization sources. Record clickable sources in the Markdown, not only in the commit message.
- [ ] **Step 2: Source or remove exact 12306/EventMesh QPS, benefit and timeline claims; distinguish workflow version from specVersion.**
- [ ] **Step 3: Pin runnable command prerequisites/version/endpoints, or label snippets as illustrative; complete Temporal imports and Activity/Worker/Client flow.**
- [ ] **Step: Validate examples and links**
Check code/config syntax by inspection against the cited version; run the local-link scan and V4. No exact number may remain without source, environment or explicit “示例假设” label.
- [ ] **Step: Commit this fact group**
```bash
git add note/07.workflow/apache-eventmesh/README.md note/07.workflow/apache-eventmesh/cloud-flow/README.md note/07.workflow/process-engine/README.md note/07.workflow/workflow-and-microservice-orchestration/README.md
git commit -m "fix(07.workflow): 修正时间线、案例数据与示例" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 21: Batch 3 — Application-system evidence and benchmark claims
**Files:**
- Modify: `note/08.application-systems/01-rd-innovation/cms/README.md`
- Modify: `note/08.application-systems/01-rd-innovation/pdm/README.md`
- Modify: `note/08.application-systems/04-sales-service/scrm/README.md`
**Interfaces:**
- Consumes: approved P0/P1 verification and official primary sources
- Produces: correct, sourced or explicitly illustrative claims
- [ ] **Step 1: Read the complete files and primary references**
For library/framework details use Context7 first; for project timelines/case data use official project or organization sources. Record clickable sources in the Markdown, not only in the commit message.
- [ ] **Step 2: Add URL, title, year and scope to PDM public-case claims; otherwise convert them to explicit examples.**
- [ ] **Step 3: Remove unsupported CMS multiplier arithmetic/QPS and SCRM 3–10x claims, or add reproducible benchmark/report evidence.**
- [ ] **Step: Validate examples and links**
Check code/config syntax by inspection against the cited version; run the local-link scan and V4. No exact number may remain without source, environment or explicit “示例假设” label.
- [ ] **Step: Commit this fact group**
```bash
git add note/08.application-systems/01-rd-innovation/cms/README.md note/08.application-systems/01-rd-innovation/pdm/README.md note/08.application-systems/04-sales-service/scrm/README.md
git commit -m "fix(08.application-systems): 修正案例来源与性能表述" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 22: Batch 3 — React and BFF correctness/security
**Files:**
- Modify: `note/09.front-end/03-frameworks/react/README.md`
- Modify: `note/09.front-end/05-architecture/bff/README.md`
- Modify: `note/09.front-end/05-architecture/state-management/README.md`
**Interfaces:**
- Consumes: approved P0/P1 verification and official primary sources
- Produces: correct, sourced or explicitly illustrative claims
- [ ] **Step 1: Read the complete files and primary references**
For library/framework details use Context7 first; for project timelines/case data use official project or organization sources. Record clickable sources in the Markdown, not only in the commit message.
- [ ] **Step 2: Replace mutating `items.sort()` with `toSorted()` or `[...items].sort()`; rename the Effect anti-pattern accurately; constrain suppressHydrationWarning.**
- [ ] **Step 3: Replace absolute XSS/auth statements with layered controls; source or remove 80%/90% and “2026 consensus” claims.**
- [ ] **Step: Validate examples and links**
Check code/config syntax by inspection against the cited version; run the local-link scan and V4. No exact number may remain without source, environment or explicit “示例假设” label.
- [ ] **Step: Commit this fact group**
```bash
git add note/09.front-end/03-frameworks/react/README.md note/09.front-end/05-architecture/bff/README.md note/09.front-end/05-architecture/state-management/README.md
git commit -m "fix(09.front-end): 修正 React 示例与 BFF 安全边界" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 23: Batch 3 — Big-data concept layers and executable ingestion
**Files:**
- Modify: `note/10.big-data/03-realtime-compute/01-flink-vs-spark-streaming/README.md`
- Modify: `note/10.big-data/04-data-lake/01-iceberg-vs-delta-vs-hudi/README.md`
- Modify: `note/10.big-data/05-olap/01-clickhouse-vs-doris-vs-starrocks/README.md`
**Interfaces:**
- Consumes: approved P0/P1 verification and official primary sources
- Produces: correct, sourced or explicitly illustrative claims
- [ ] **Step 1: Read the complete files and primary references**
For library/framework details use Context7 first; for project timelines/case data use official project or organization sources. Record clickable sources in the Markdown, not only in the commit message.
- [ ] **Step 2: Distinguish DStream/Structured Streaming and use real Flink keys.**
- [ ] **Step 3: Separate query engine/table format/file format, remove ASF/CNCF confusion, replace fake Kafka SELECT with Routine Load/Stream Load, and remove unit/absolute-ranking errors.**
- [ ] **Step: Validate examples and links**
Check code/config syntax by inspection against the cited version; run the local-link scan and V4. No exact number may remain without source, environment or explicit “示例假设” label.
- [ ] **Step: Commit this fact group**
```bash
git add note/10.big-data/03-realtime-compute/01-flink-vs-spark-streaming/README.md note/10.big-data/04-data-lake/01-iceberg-vs-delta-vs-hudi/README.md note/10.big-data/05-olap/01-clickhouse-vs-doris-vs-starrocks/README.md
git commit -m "fix(10.big-data): 修正流计算、表格式与 OLAP 示例" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 24: Batch 4 Structure — H1 and main-module positioning
**Files:**
- Modify: `note/05.tools/README.md`
- Modify: `note/09.front-end/README.md`
- Modify: `note/10.big-data/README.md`
- Modify: `note/11.ai/README.md`
- Modify: `note/14.project-management/README.md`
- Modify: `note/03.database/README.md`
- Modify: `note/04.system-design/README.md`
- Modify: `note/06.spring/README.md`
**Interfaces:**
- Consumes: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-candidates.md` and current CONTRIBUTING rules
- Produces: closed structure candidates without index-only over-expansion
- [ ] **Step 1: Read every candidate in scope and its parent index**
- [ ] **Step 2: Remove prohibited numeric prefixes from the five H1s; shorten the four flagged positioning lines to ≤80 Chinese characters without losing scope.**
- [ ] **Step 3: Verify structure**
Run V1, V2, V4 and the module link scan. Search the modified files for unresolved generic template text or unintended numeric H1s.
- [ ] **Step 4: Commit the structure group**
```bash
git add note
git commit -m "style(note): 统一主模块标题与定位句" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 25: Batch 4 Structure — Algorithm indexes and WCAG metadata
**Files:**
- Modify: `note/02.computer-basics/02-algorithms/README.md`
- Modify: `note/02.computer-basics/02-algorithms/clustering/README.md`
- Modify: `note/02.computer-basics/02-algorithms/clustering/k-means/README.md`
- Modify: `note/02.computer-basics/02-algorithms/dimensionality-reduction/README.md`
- Modify: `note/02.computer-basics/02-algorithms/dimensionality-reduction/pca/README.md`
- Modify: `note/02.computer-basics/02-algorithms/optimization/README.md`
- Modify: `note/02.computer-basics/02-algorithms/optimization/gradient-descent/README.md`
- Modify: `note/02.computer-basics/01-network/wcag/README.md`
**Interfaces:**
- Consumes: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-candidates.md` and current CONTRIBUTING rules
- Produces: closed structure candidates without index-only over-expansion
- [ ] **Step 1: Read every candidate in scope and its parent index**
- [ ] **Step 2: Keep index-only pages concise; add real parent navigation, replace same-target pseudo-links with plain future-topic text or existing real pages, and clean WCAG summary without moving it.**
- [ ] **Step 3: Verify structure**
Run V1, V2, V4 and the module link scan. Search the modified files for unresolved generic template text or unintended numeric H1s.
- [ ] **Step 4: Commit the structure group**
```bash
git add note
git commit -m "fix(02.computer-basics): 接入算法索引并清理伪链接" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 26: Batch 4 Structure — Template and Placeholder Chunks
**Files:**
- Modify: exact files under `TEMPLATE-01` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-chunks.md`
- Modify: exact files under `TEMPLATE-02` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-chunks.md`
- Modify: exact files under `PLACEHOLDER-01` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-chunks.md`
**Interfaces:**
- Consumes: TEMPLATE-01, TEMPLATE-02, PLACEHOLDER-01 and `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-candidates.md` evidence lines
- Produces: each candidate reviewed; valid hooks/examples retained; generic residue or true backlog closed
- [ ] **Step: Review and repair TEMPLATE-01**
Open `TEMPLATE-01` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-chunks.md` and the matching evidence in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-candidates.md`. Read every listed file. For TEMPLATE chunks, keep topic-specific architecture dilemmas and rewrite only generic reusable boilerplate. For PLACEHOLDER chunks, keep state-machine/example terminology, move real backlog to an existing Roadmap section or complete the content, and remove stale promises.
- [ ] **Step: Verify and commit this structure chunk**
Run V1, V2, V4 and the module link scan. The diff must contain at most the files listed in this chunk and their directly affected parent indexes.
```bash
git add note
git commit -m "style(note): 清理结构候选 (TEMPLATE-01)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Review and repair TEMPLATE-02**
Open `TEMPLATE-02` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-chunks.md` and the matching evidence in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-candidates.md`. Read every listed file. For TEMPLATE chunks, keep topic-specific architecture dilemmas and rewrite only generic reusable boilerplate. For PLACEHOLDER chunks, keep state-machine/example terminology, move real backlog to an existing Roadmap section or complete the content, and remove stale promises.
- [ ] **Step: Verify and commit this structure chunk**
Run V1, V2, V4 and the module link scan. The diff must contain at most the files listed in this chunk and their directly affected parent indexes.
```bash
git add note
git commit -m "style(note): 清理结构候选 (TEMPLATE-02)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Review and repair PLACEHOLDER-01**
Open `PLACEHOLDER-01` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-chunks.md` and the matching evidence in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-structure-candidates.md`. Read every listed file. For TEMPLATE chunks, keep topic-specific architecture dilemmas and rewrite only generic reusable boilerplate. For PLACEHOLDER chunks, keep state-machine/example terminology, move real backlog to an existing Roadmap section or complete the content, and remove stale promises.
- [ ] **Step: Verify and commit this structure chunk**
Run V1, V2, V4 and the module link scan. The diff must contain at most the files listed in this chunk and their directly affected parent indexes.
```bash
git add note
git commit -m "style(note): 清理结构候选 (PLACEHOLDER-01)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 27: Batch 4 Bare Fences — 01.java
**Files:**
- Modify: exact files under `FENCE-01` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-02` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-03` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-04` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-05` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-06` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-07` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-08` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-09` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-10` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-11` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-12` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-13` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-01, FENCE-02, FENCE-03, FENCE-04, FENCE-05, FENCE-06, FENCE-07, FENCE-08, FENCE-09, FENCE-10, FENCE-11, FENCE-12, FENCE-13
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-01 (build-tools)**
Open `FENCE-01` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 build-tools 围栏语言 (FENCE-01)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-02 (collection)**
Open `FENCE-02` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 collection 围栏语言 (FENCE-02)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-03 (concepts)**
Open `FENCE-03` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 concepts 围栏语言 (FENCE-03)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-04 (concurrency)**
Open `FENCE-04` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 concurrency 围栏语言 (FENCE-04)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-05 (io)**
Open `FENCE-05` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 io 围栏语言 (FENCE-05)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-06 (java-agent)**
Open `FENCE-06` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 java-agent 围栏语言 (FENCE-06)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-07 (jdbc)**
Open `FENCE-07` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 jdbc 围栏语言 (FENCE-07)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-08 (jvm)**
Open `FENCE-08` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 jvm 围栏语言 (FENCE-08)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-09 (logging)**
Open `FENCE-09` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 logging 围栏语言 (FENCE-09)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-10 (modules)**
Open `FENCE-10` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 modules 围栏语言 (FENCE-10)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-11 (network)**
Open `FENCE-11` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 network 围栏语言 (FENCE-11)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-12 (testing)**
Open `FENCE-12` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 testing 围栏语言 (FENCE-12)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-13 (version)**
Open `FENCE-13` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(01.java): 补齐 version 围栏语言 (FENCE-13)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 28: Batch 4 Bare Fences — 02.computer-basics
**Files:**
- Modify: exact files under `FENCE-14` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-15` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-16` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-14, FENCE-15, FENCE-16
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-14 (01-network)**
Open `FENCE-14` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(02.computer-basics): 补齐 01-network 围栏语言 (FENCE-14)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-15 (02-algorithms)**
Open `FENCE-15` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(02.computer-basics): 补齐 02-algorithms 围栏语言 (FENCE-15)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-16 (06-operating-system)**
Open `FENCE-16` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(02.computer-basics): 补齐 06-operating-system 围栏语言 (FENCE-16)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 29: Batch 4 Bare Fences — 03.database
**Files:**
- Modify: exact files under `FENCE-17` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-18` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-19` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-20` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-21` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-22` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-23` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-24` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-25` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-26` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-27` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-28` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-17, FENCE-18, FENCE-19, FENCE-20, FENCE-21, FENCE-22, FENCE-23, FENCE-24, FENCE-25, FENCE-26, FENCE-27, FENCE-28
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-17 (02-sql)**
Open `FENCE-17` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 02-sql 围栏语言 (FENCE-17)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-18 (03-transaction)**
Open `FENCE-18` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 03-transaction 围栏语言 (FENCE-18)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-19 (04-index)**
Open `FENCE-19` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 04-index 围栏语言 (FENCE-19)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-20 (05-mysql)**
Open `FENCE-20` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 05-mysql 围栏语言 (FENCE-20)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-21 (06-cache)**
Open `FENCE-21` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 06-cache 围栏语言 (FENCE-21)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-22 (07-redis)**
Open `FENCE-22` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 07-redis 围栏语言 (FENCE-22)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-23 (08-nosql)**
Open `FENCE-23` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 08-nosql 围栏语言 (FENCE-23)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-24 (09-connection-pool)**
Open `FENCE-24` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 09-connection-pool 围栏语言 (FENCE-24)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-25 (10-data-migration)**
Open `FENCE-25` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 10-data-migration 围栏语言 (FENCE-25)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-26 (11-monitoring)**
Open `FENCE-26` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 11-monitoring 围栏语言 (FENCE-26)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-27 (12-cloud-database)**
Open `FENCE-27` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 12-cloud-database 围栏语言 (FENCE-27)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-28 (13-postgresql)**
Open `FENCE-28` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(03.database): 补齐 13-postgresql 围栏语言 (FENCE-28)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 30: Batch 4 Bare Fences — 04.system-design
**Files:**
- Modify: exact files under `FENCE-29` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-30` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-31` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-32` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-33` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-34` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-35` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-36` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-37` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-29, FENCE-30, FENCE-31, FENCE-32, FENCE-33, FENCE-34, FENCE-35, FENCE-36, FENCE-37
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-29 (01-foundation)**
Open `FENCE-29` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(04.system-design): 补齐 01-foundation 围栏语言 (FENCE-29)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-30 (02-distributed)**
Open `FENCE-30` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(04.system-design): 补齐 02-distributed 围栏语言 (FENCE-30)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-31 (03-high-availability)**
Open `FENCE-31` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(04.system-design): 补齐 03-high-availability 围栏语言 (FENCE-31)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-32 (04-high-performance)**
Open `FENCE-32` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(04.system-design): 补齐 04-high-performance 围栏语言 (FENCE-32)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-33 (05-security)**
Open `FENCE-33` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(04.system-design): 补齐 05-security 围栏语言 (FENCE-33)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-34 (06-idempotency)**
Open `FENCE-34` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(04.system-design): 补齐 06-idempotency 围栏语言 (FENCE-34)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-35 (07-deployment)**
Open `FENCE-35` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(04.system-design): 补齐 07-deployment 围栏语言 (FENCE-35)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-36 (08-observability)**
Open `FENCE-36` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(04.system-design): 补齐 08-observability 围栏语言 (FENCE-36)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-37 (09-emerging-tech)**
Open `FENCE-37` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(04.system-design): 补齐 09-emerging-tech 围栏语言 (FENCE-37)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 31: Batch 4 Bare Fences — 05.tools
**Files:**
- Modify: exact files under `FENCE-38` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-39` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-40` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-38, FENCE-39, FENCE-40
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-38 (devops)**
Open `FENCE-38` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(05.tools): 补齐 devops 围栏语言 (FENCE-38)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-39 (iac)**
Open `FENCE-39` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(05.tools): 补齐 iac 围栏语言 (FENCE-39)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-40 (kubernetes)**
Open `FENCE-40` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(05.tools): 补齐 kubernetes 围栏语言 (FENCE-40)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 32: Batch 4 Bare Fences — 06.spring
**Files:**
- Modify: exact files under `FENCE-41` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-42` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-43` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-44` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-45` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-46` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-47` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-48` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-49` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-50` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-41, FENCE-42, FENCE-43, FENCE-44, FENCE-45, FENCE-46, FENCE-47, FENCE-48, FENCE-49, FENCE-50
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-41 (01-core)**
Open `FENCE-41` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(06.spring): 补齐 01-core 围栏语言 (FENCE-41)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-42 (02-web)**
Open `FENCE-42` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(06.spring): 补齐 02-web 围栏语言 (FENCE-42)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-43 (03-data)**
Open `FENCE-43` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(06.spring): 补齐 03-data 围栏语言 (FENCE-43)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-44 (04-spring-boot)**
Open `FENCE-44` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(06.spring): 补齐 04-spring-boot 围栏语言 (FENCE-44)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-45 (05-spring-cloud)**
Open `FENCE-45` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(06.spring): 补齐 05-spring-cloud 围栏语言 (FENCE-45)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-46 (06-integration)**
Open `FENCE-46` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(06.spring): 补齐 06-integration 围栏语言 (FENCE-46)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-47 (07-observability)**
Open `FENCE-47` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(06.spring): 补齐 07-observability 围栏语言 (FENCE-47)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-48 (08-annotations)**
Open `FENCE-48` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(06.spring): 补齐 08-annotations 围栏语言 (FENCE-48)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-49 (09-security)**
Open `FENCE-49` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(06.spring): 补齐 09-security 围栏语言 (FENCE-49)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-50 (README.md)**
Open `FENCE-50` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(06.spring): 补齐 README.md 围栏语言 (FENCE-50)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 33: Batch 4 Bare Fences — 07.workflow
**Files:**
- Modify: exact files under `FENCE-51` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-52` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-51, FENCE-52
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-51 (process-engine)**
Open `FENCE-51` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(07.workflow): 补齐 process-engine 围栏语言 (FENCE-51)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-52 (temporal)**
Open `FENCE-52` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(07.workflow): 补齐 temporal 围栏语言 (FENCE-52)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 34: Batch 4 Bare Fences — 08.application-systems
**Files:**
- Modify: exact files under `FENCE-53` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-54` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-55` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-56` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-57` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-53, FENCE-54, FENCE-55, FENCE-56, FENCE-57
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-53 (02-production)**
Open `FENCE-53` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(08.application-systems): 补齐 02-production 围栏语言 (FENCE-53)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-54 (03-supply-chain)**
Open `FENCE-54` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(08.application-systems): 补齐 03-supply-chain 围栏语言 (FENCE-54)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-55 (04-sales-service)**
Open `FENCE-55` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(08.application-systems): 补齐 04-sales-service 围栏语言 (FENCE-55)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-56 (05-operations)**
Open `FENCE-56` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(08.application-systems): 补齐 05-operations 围栏语言 (FENCE-56)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-57 (06-specialized)**
Open `FENCE-57` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(08.application-systems): 补齐 06-specialized 围栏语言 (FENCE-57)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 35: Batch 4 Bare Fences — 09.front-end
**Files:**
- Modify: exact files under `FENCE-58` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-59` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-60` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-58, FENCE-59, FENCE-60
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-58 (02-language)**
Open `FENCE-58` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(09.front-end): 补齐 02-language 围栏语言 (FENCE-58)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-59 (07-security)**
Open `FENCE-59` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(09.front-end): 补齐 07-security 围栏语言 (FENCE-59)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-60 (08-cross-platform)**
Open `FENCE-60` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(09.front-end): 补齐 08-cross-platform 围栏语言 (FENCE-60)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 36: Batch 4 Bare Fences — 10.big-data
**Files:**
- Modify: exact files under `FENCE-61` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-62` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-63` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-61, FENCE-62, FENCE-63
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-61 (03-realtime-compute)**
Open `FENCE-61` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(10.big-data): 补齐 03-realtime-compute 围栏语言 (FENCE-61)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-62 (04-data-lake)**
Open `FENCE-62` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(10.big-data): 补齐 04-data-lake 围栏语言 (FENCE-62)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-63 (05-olap)**
Open `FENCE-63` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(10.big-data): 补齐 05-olap 围栏语言 (FENCE-63)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 37: Batch 4 Bare Fences — 11.ai
**Files:**
- Modify: exact files under `FENCE-64` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-65` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-66` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-67` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-68` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-69` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-70` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-71` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-64, FENCE-65, FENCE-66, FENCE-67, FENCE-68, FENCE-69, FENCE-70, FENCE-71
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-64 (01-fundamentals)**
Open `FENCE-64` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(11.ai): 补齐 01-fundamentals 围栏语言 (FENCE-64)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-65 (02-technology-stack)**
Open `FENCE-65` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(11.ai): 补齐 02-technology-stack 围栏语言 (FENCE-65)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-66 (03-engineering)**
Open `FENCE-66` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(11.ai): 补齐 03-engineering 围栏语言 (FENCE-66)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-67 (03-engineering)**
Open `FENCE-67` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(11.ai): 补齐 03-engineering 围栏语言 (FENCE-67)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-68 (04-architecture)**
Open `FENCE-68` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(11.ai): 补齐 04-architecture 围栏语言 (FENCE-68)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-69 (05-applications)**
Open `FENCE-69` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(11.ai): 补齐 05-applications 围栏语言 (FENCE-69)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-70 (07-research)**
Open `FENCE-70` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(11.ai): 补齐 07-research 围栏语言 (FENCE-70)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-71 (08-llmops)**
Open `FENCE-71` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(11.ai): 补齐 08-llmops 围栏语言 (FENCE-71)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 38: Batch 4 Bare Fences — 12.story
**Files:**
- Modify: exact files under `FENCE-72` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-73` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-74` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-75` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-76` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-77` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-78` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-79` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-72, FENCE-73, FENCE-74, FENCE-75, FENCE-76, FENCE-77, FENCE-78, FENCE-79
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-72 (02-system-architecture-evolution.md)**
Open `FENCE-72` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(12.story): 补齐 02-system-architecture-evolution.md 围栏语言 (FENCE-72)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-73 (37-vector-database-and-embedding.md)**
Open `FENCE-73` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(12.story): 补齐 37-vector-database-and-embedding.md 围栏语言 (FENCE-73)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-74 (42-ai-engineer-responsibility.md)**
Open `FENCE-74` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(12.story): 补齐 42-ai-engineer-responsibility.md 围栏语言 (FENCE-74)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-75 (43-ai-productivity-paradox.md)**
Open `FENCE-75` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(12.story): 补齐 43-ai-productivity-paradox.md 围栏语言 (FENCE-75)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-76 (44-tech-debt-career-trap.md)**
Open `FENCE-76` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(12.story): 补齐 44-tech-debt-career-trap.md 围栏语言 (FENCE-76)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-77 (45-skill-scheduling-restaurant.md)**
Open `FENCE-77` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(12.story): 补齐 45-skill-scheduling-restaurant.md 围栏语言 (FENCE-77)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-78 (46-llm-inference.md)**
Open `FENCE-78` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(12.story): 补齐 46-llm-inference.md 围栏语言 (FENCE-78)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-79 (STORY-FORMAT-SPEC.md)**
Open `FENCE-79` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(12.story): 补齐 STORY-FORMAT-SPEC.md 围栏语言 (FENCE-79)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 39: Batch 4 Bare Fences — 13.split-hairs
**Files:**
- Modify: exact files under `FENCE-80` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-81` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-82` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-83` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-84` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-85` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-86` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-87` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-88` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-89` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-80, FENCE-81, FENCE-82, FENCE-83, FENCE-84, FENCE-85, FENCE-86, FENCE-87, FENCE-88, FENCE-89
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-80 (01.java)**
Open `FENCE-80` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(13.split-hairs): 补齐 01.java 围栏语言 (FENCE-80)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-81 (02.computer-basics)**
Open `FENCE-81` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(13.split-hairs): 补齐 02.computer-basics 围栏语言 (FENCE-81)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-82 (03.database)**
Open `FENCE-82` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(13.split-hairs): 补齐 03.database 围栏语言 (FENCE-82)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-83 (04.system-design)**
Open `FENCE-83` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(13.split-hairs): 补齐 04.system-design 围栏语言 (FENCE-83)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-84 (05.security)**
Open `FENCE-84` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(13.split-hairs): 补齐 05.security 围栏语言 (FENCE-84)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-85 (06.spring)**
Open `FENCE-85` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(13.split-hairs): 补齐 06.spring 围栏语言 (FENCE-85)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-86 (09.front-end)**
Open `FENCE-86` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(13.split-hairs): 补齐 09.front-end 围栏语言 (FENCE-86)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-87 (11.ai)**
Open `FENCE-87` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(13.split-hairs): 补齐 11.ai 围栏语言 (FENCE-87)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-88 (11.ai)**
Open `FENCE-88` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(13.split-hairs): 补齐 11.ai 围栏语言 (FENCE-88)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-89 (QUESTION-FORMAT-SPEC.md)**
Open `FENCE-89` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(13.split-hairs): 补齐 QUESTION-FORMAT-SPEC.md 围栏语言 (FENCE-89)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 40: Batch 4 Bare Fences — 14.project-management
**Files:**
- Modify: exact files under `FENCE-90` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: exact files under `FENCE-91` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-90, FENCE-91
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-90 (agile-metrics)**
Open `FENCE-90` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(14.project-management): 补齐 agile-metrics 围栏语言 (FENCE-90)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step: Annotate FENCE-91 (risk-register)**
Open `FENCE-91` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(14.project-management): 补齐 risk-register 围栏语言 (FENCE-91)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 41: Batch 4 Bare Fences — CONTRIBUTING.md
**Files:**
- Modify: exact files under `FENCE-92` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
**Interfaces:**
- Consumes: FENCE chunks FENCE-92
- Produces: all opening fences in this module have truthful language labels; one commit per chunk
- [ ] **Step: Annotate FENCE-92 (_root)**
Open `FENCE-92` in `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`. Read context around every listed opening fence after prior line shifts. Use `text` for ASCII/command output/decision trees, `bash` for shell, `yaml|json|xml|properties` for real configuration, the actual programming language for code, and `mermaid` only for valid Mermaid. Do not change closing fences or code content.
- [ ] **Step: Verify and commit this fence chunk**
Run V3 and confirm none of the files in this chunk remain in its output. Run V4, then commit.
```bash
git add note
git commit -m "style(CONTRIBUTING.md): 补齐 _root 围栏语言 (FENCE-92)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 42: Batch 4 Global Format Gate
**Files:**
- Read: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-fence-chunks.md`
- Modify: only files still emitted by V3
**Interfaces:**
- Consumes: all FENCE chunk commits
- Produces: bare_openings=0 and no Markdown fence imbalance
- [ ] **Step 1: Run V3**

Expected: `bare_openings=0`.

- [ ] **Step 2: Validate fence balance**

For every Markdown file, verify opening/closing triple-backtick fences balance. If a file uses four-backtick nesting, inspect it manually rather than rewriting delimiters.

- [ ] **Step 3: Commit any residual module-specific fixes**

Residual fixes must remain split by module and ≤30 files; rerun V3 after each commit.
### Task 43: Batch 5 Quality Findings — 01.java
**Files:**
- Modify: `note/01.java/collection/LinkedHashSet/README.md`
- Modify: `note/01.java/collection/WeakHashMap/README.md`
- Modify: `note/01.java/concepts/spi/README.md`
- Modify: `note/01.java/io/zero-copy/README.md`
- Modify: `note/01.java/version/java-10/README.md`
- Modify: `note/01.java/version/java-9/README.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 01.java
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 01.java section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/01.java/collection/LinkedHashSet/README.md note/01.java/collection/WeakHashMap/README.md note/01.java/concepts/spi/README.md note/01.java/io/zero-copy/README.md note/01.java/version/java-10/README.md note/01.java/version/java-9/README.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(01.java): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 44: Batch 5 Quality Findings — 02.computer-basics
**Files:**
- Modify: `note/02.computer-basics/01-network/03-dns/README.md`
- Modify: `note/02.computer-basics/01-network/04-https-tls/README.md`
- Modify: `note/02.computer-basics/01-network/tcp-ip-model/README.md`
- Modify: `note/02.computer-basics/01-network/wcag/README.md`
- Modify: `note/02.computer-basics/02-algorithms/clustering/README.md`
- Modify: `note/02.computer-basics/02-algorithms/decision-tree/README.md`
- Modify: `note/02.computer-basics/02-algorithms/dimensionality-reduction/README.md`
- Modify: `note/02.computer-basics/02-algorithms/ensemble/README.md`
- Modify: `note/02.computer-basics/02-algorithms/optimization/README.md`
- Modify: `note/02.computer-basics/02-algorithms/string-algorithms/03-ac-automaton.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 02.computer-basics
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 02.computer-basics section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/02.computer-basics/01-network/03-dns/README.md note/02.computer-basics/01-network/04-https-tls/README.md note/02.computer-basics/01-network/tcp-ip-model/README.md note/02.computer-basics/01-network/wcag/README.md note/02.computer-basics/02-algorithms/clustering/README.md note/02.computer-basics/02-algorithms/decision-tree/README.md note/02.computer-basics/02-algorithms/dimensionality-reduction/README.md note/02.computer-basics/02-algorithms/ensemble/README.md note/02.computer-basics/02-algorithms/optimization/README.md note/02.computer-basics/02-algorithms/string-algorithms/03-ac-automaton.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(02.computer-basics): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 45: Batch 5 Quality Findings — 03.database
**Files:**
- Modify: `note/03.database/08-nosql/elasticsearch/README.md`
- Modify: `note/03.database/08-nosql/mongodb/README.md`
- Modify: `note/03.database/08-nosql/neo4j/README.md`
- Modify: `note/03.database/README.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 03.database
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 03.database section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/03.database/08-nosql/elasticsearch/README.md note/03.database/08-nosql/mongodb/README.md note/03.database/08-nosql/neo4j/README.md note/03.database/README.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(03.database): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 46: Batch 5 Quality Findings — 04.system-design
**Files:**
- Modify: `note/04.system-design/01-foundation/02-evolution/02-serverless-architecture/README.md`
- Modify: `note/04.system-design/01-foundation/system-design-basics/architecture-diagram/README.md`
- Modify: `note/04.system-design/01-foundation/system-design-basics/it4it/functional-components.md`
- Modify: `note/04.system-design/02-distributed/api-gateway/README.md`
- Modify: `note/04.system-design/02-distributed/consensus-algorithms/README.md`
- Modify: `note/04.system-design/04-high-performance/product-search/03-ranking.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 04.system-design
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 04.system-design section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/04.system-design/01-foundation/02-evolution/02-serverless-architecture/README.md note/04.system-design/01-foundation/system-design-basics/architecture-diagram/README.md note/04.system-design/01-foundation/system-design-basics/it4it/functional-components.md note/04.system-design/02-distributed/api-gateway/README.md note/04.system-design/02-distributed/consensus-algorithms/README.md note/04.system-design/04-high-performance/product-search/03-ranking.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(04.system-design): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 47: Batch 5 Quality Findings — 05.tools
**Files:**
- Modify: `note/05.tools/02-docker/command/README.md`
- Modify: `note/05.tools/04-nginx/README.md`
- Modify: `note/05.tools/05-monorepo/README.md`
- Modify: `note/05.tools/06-ali-microservices/README.md`
- Modify: `note/05.tools/devops/README.md`
- Modify: `note/05.tools/kubernetes/08-operator-and-gitops/README.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 05.tools
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 05.tools section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/05.tools/02-docker/command/README.md note/05.tools/04-nginx/README.md note/05.tools/05-monorepo/README.md note/05.tools/06-ali-microservices/README.md note/05.tools/devops/README.md note/05.tools/kubernetes/08-operator-and-gitops/README.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(05.tools): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 48: Batch 5 Quality Findings — 06.spring
**Files:**
- Modify: `note/06.spring/01-core/ioc/dependency-injection.md`
- Modify: `note/06.spring/03-data/transaction/propagation-and-isolation.md`
- Modify: `note/06.spring/06-integration/validation/cross-field.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 06.spring
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 06.spring section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/06.spring/01-core/ioc/dependency-injection.md note/06.spring/03-data/transaction/propagation-and-isolation.md note/06.spring/06-integration/validation/cross-field.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(06.spring): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 49: Batch 5 Quality Findings — 07.workflow
**Files:**
- Modify: `note/07.workflow/apache-eventmesh/README.md`
- Modify: `note/07.workflow/apache-eventmesh/cloud-flow/README.md`
- Modify: `note/07.workflow/process-engine/README.md`
- Modify: `note/07.workflow/workflow-and-microservice-orchestration/README.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 07.workflow
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 07.workflow section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/07.workflow/apache-eventmesh/README.md note/07.workflow/apache-eventmesh/cloud-flow/README.md note/07.workflow/process-engine/README.md note/07.workflow/workflow-and-microservice-orchestration/README.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(07.workflow): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 50: Batch 5 Quality Findings — 08.application-systems
**Files:**
- Modify: `note/08.application-systems/01-rd-innovation/cms/README.md`
- Modify: `note/08.application-systems/01-rd-innovation/pdm/README.md`
- Modify: `note/08.application-systems/04-sales-service/scrm/README.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 08.application-systems
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 08.application-systems section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/08.application-systems/01-rd-innovation/cms/README.md note/08.application-systems/01-rd-innovation/pdm/README.md note/08.application-systems/04-sales-service/scrm/README.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(08.application-systems): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 51: Batch 5 Quality Findings — 09.front-end
**Files:**
- Modify: `note/09.front-end/03-frameworks/react/README.md`
- Modify: `note/09.front-end/05-architecture/bff/README.md`
- Modify: `note/09.front-end/05-architecture/state-management/README.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 09.front-end
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 09.front-end section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/09.front-end/03-frameworks/react/README.md note/09.front-end/05-architecture/bff/README.md note/09.front-end/05-architecture/state-management/README.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(09.front-end): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 52: Batch 5 Quality Findings — 10.big-data
**Files:**
- Modify: `note/10.big-data/03-realtime-compute/01-flink-vs-spark-streaming/README.md`
- Modify: `note/10.big-data/04-data-lake/01-iceberg-vs-delta-vs-hudi/README.md`
- Modify: `note/10.big-data/05-olap/01-clickhouse-vs-doris-vs-starrocks/README.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 10.big-data
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 10.big-data section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/10.big-data/03-realtime-compute/01-flink-vs-spark-streaming/README.md note/10.big-data/04-data-lake/01-iceberg-vs-delta-vs-hudi/README.md note/10.big-data/05-olap/01-clickhouse-vs-doris-vs-starrocks/README.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(10.big-data): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 53: Batch 5 Quality Findings — 11.ai
**Files:**
- Modify: `note/11.ai/02-technology-stack/paged-attention/README.md`
- Modify: `note/11.ai/03-engineering/ai-platforms/vllm-vs-ollama/04-quantization.md`
- Modify: `note/11.ai/04-architecture/intelligent-system-layers/system-three-layers.md`
- Modify: `note/11.ai/05-applications/case-studies/09-glean-enterprise-search/README.md`
- Modify: `note/11.ai/07-research/efficiency/README.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 11.ai
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 11.ai section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/11.ai/02-technology-stack/paged-attention/README.md note/11.ai/03-engineering/ai-platforms/vllm-vs-ollama/04-quantization.md note/11.ai/04-architecture/intelligent-system-layers/system-three-layers.md note/11.ai/05-applications/case-studies/09-glean-enterprise-search/README.md note/11.ai/07-research/efficiency/README.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(11.ai): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 54: Batch 5 Quality Findings — 12.story
**Files:**
- Modify: `note/12.story/08-qa-testing-strategy.md`
- Modify: `note/12.story/11-ai-learning-paradox.md`
- Modify: `note/12.story/34b-ai-token-cost-optimization.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 12.story
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 12.story section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/12.story/08-qa-testing-strategy.md note/12.story/11-ai-learning-paradox.md note/12.story/34b-ai-token-cost-optimization.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(12.story): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 55: Batch 5 Quality Findings — 13.split-hairs
**Files:**
- Modify: `note/13.split-hairs/01.java/parent-child-thread/README.md`
- Modify: `note/13.split-hairs/03.database/README.md`
- Modify: `note/13.split-hairs/03.database/mysql-time-types/README.md`
- Modify: `note/13.split-hairs/03.database/mysql-what-lock/README.md`
- Modify: `note/13.split-hairs/04.system-design/README.md`
- Modify: `note/13.split-hairs/04.system-design/url-shortener/README.md`
- Modify: `note/13.split-hairs/05.security/README.md`
- Modify: `note/13.split-hairs/09.front-end/playwright-vs-selenium/README.md`
- Modify: `note/13.split-hairs/09.front-end/xss-csrf/README.md`
- Modify: `note/13.split-hairs/11.ai/README.md`
- Modify: `note/13.split-hairs/11.ai/llm-alignment/README.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 13.split-hairs
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 13.split-hairs section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/13.split-hairs/01.java/parent-child-thread/README.md note/13.split-hairs/03.database/README.md note/13.split-hairs/03.database/mysql-time-types/README.md note/13.split-hairs/03.database/mysql-what-lock/README.md note/13.split-hairs/04.system-design/README.md note/13.split-hairs/04.system-design/url-shortener/README.md note/13.split-hairs/05.security/README.md note/13.split-hairs/09.front-end/playwright-vs-selenium/README.md note/13.split-hairs/09.front-end/xss-csrf/README.md note/13.split-hairs/11.ai/README.md note/13.split-hairs/11.ai/llm-alignment/README.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(13.split-hairs): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 56: Batch 5 Quality Findings — 14.project-management
**Files:**
- Modify: `note/14.project-management/interviewing-cross-disciplinary/README.md`
- Modify: `note/14.project-management/outsourcing-pitfalls/README.md`
- Modify: `note/14.project-management/scripts/README.md`
- Modify: `note/14.project-management/team-sizing-3x-buffer/README.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` outcome entries for 14.project-management
**Interfaces:**
- Consumes: full findings under `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` 14.project-management section and all Batch 1–4 changes
- Produces: every finding closed as fixed/no_change_needed/skipped-with-reason
- [ ] **Step 1: Read each full file and every finding in the module section**
Do not trust the original priority blindly. Apply the reviewed rules: index-only depth and optional third-level frontmatter are no-change-needed; broken navigation/facts/format should already be fixed by earlier batches and must be verified.
- [ ] **Step 2: Close findings one file at a time**
For each finding, make the smallest substantive edit: add a primary source or remove an unsupported number; add version evolution only when behavior/selection changes; add a real failure/success contrast; shorten positioning to ≤80 characters; add a recommendation to comparison tables. Update that file’s `Outcome: pending` line in the manifest to one concrete status: `Outcome: fixed — file:line evidence or source URL`, `Outcome: no_change_needed — explicit rule and reason`, or `Outcome: skipped — named external blocker and retry condition`.
- [ ] **Step 3: Verify the module**
Run module local-link checks, V3, and V4. Search the module manifest section and require zero `Outcome: pending`.
- [ ] **Step 4: Commit module quality fixes and outcomes**
```bash
git add note/14.project-management/interviewing-cross-disciplinary/README.md note/14.project-management/outsourcing-pitfalls/README.md note/14.project-management/scripts/README.md note/14.project-management/team-sizing-3x-buffer/README.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(14.project-management): 关闭 note-health 质量 findings" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
### Task 57: Final Re-audit, Rescore and Results Report
**Files:**
- Create: `docs/superpowers/plans/2026-07-20-note-health-batch-remediation-results.md`
- Modify: `C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md` only if residual outcomes need correction
- Read: all note Markdown and all remediation manifests
**Interfaces:**
- Consumes: all Batch 1–5 commits
- Produces: verified before/after metrics, 71-file rescore, clean worktree, no push
- [ ] **Step 1: Run all global gates**

Run V1, V2, V3, the full structural link/orphan/return scan, and `git diff --check`. Required: self-return 0, wrong leaf returns 0, broken links 0, orphan Markdown 0, leaf return 634/634, bare openings 0, count tables consistent.

- [ ] **Step 2: Verify all 71 outcomes are closed**

Search `2026-07-20-note-health-quality-71.md` for `Outcome: pending`; expected zero. Any skipped finding must name an external blocker and cannot be used to claim complete remediation.

- [ ] **Step 3: Re-run note-health scoring for the exact 71 paths**

Use the tracked quality manifest paths, not a new sample. Normalize max scores by module and compare pre/post totals. Preserve both scores in the results report; do not claim a full-library average.

- [ ] **Step 4: Write the results report**

The report must include: branch and commit list; before/after structural metrics; per-module pre/post sample scores; fixed/no-change/skipped counts; any remaining limitation; proof that no forbidden paths or deletions occurred; statement that no push happened.

- [ ] **Step 5: Commit final evidence**
```bash
git add docs/superpowers/plans/2026-07-20-note-health-batch-remediation-results.md C:/developer/IdeaProjects/wb04307201/docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md
git commit -m "docs(note): 记录 Batch 1-5 修复验证结果" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
- [ ] **Step 6: Verify final repository state**

```bash
git status --short
git log --oneline --decorate -20
git branch --show-current
```

Expected: clean status, branch `fix/note-health-remediation`, all remediation commits visible, no push performed.

---

## Explicit 71-File Scope

The exact 71 files and every original finding are listed in `docs/superpowers/plans/manifests/2026-07-20-note-health-quality-71.md`. Module counts are:
- `01.java`: 6 files
- `02.computer-basics`: 10 files
- `03.database`: 4 files
- `04.system-design`: 6 files
- `05.tools`: 6 files
- `06.spring`: 3 files
- `07.workflow`: 4 files
- `08.application-systems`: 3 files
- `09.front-end`: 3 files
- `10.big-data`: 3 files
- `11.ai`: 5 files
- `12.story`: 3 files
- `13.split-hairs`: 11 files
- `14.project-management`: 4 files
Total: **71 files**. This tracked manifest is part of this implementation plan and is mandatory input to every Batch 5 task.