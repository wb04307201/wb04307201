# Task 14 Report — Batch 1 Navigation — 13.split-hairs

Status: DONE

## Chunks (11 commits, all on `fix/note-health-remediation`)

| Chunk | Short Hash | Files Touched | Subgroup |
|-------|-----------|---------------|----------|
| NAV-68 | 4541f537 | 24 | 13.split-hairs / 01.java (集合/并发/JVM/语言基础) |
| NAV-69 | 0a677258 | 14 | 13.split-hairs / 01.java (设计模式/技巧/线程进阶) |
| NAV-70 | 5416b691 | 2  | 13.split-hairs / 02.computer-basics (端口复用/ML) |
| NAV-71 | 573cc0f2 | 11 | 13.split-hairs / 03.database |
| NAV-72 | 7efa67bb | 7  | 13.split-hairs / 04.system-design |
| NAV-73 | 9f9768c9 | 3  | 13.split-hairs / 05.security |
| NAV-74 | 2b47308a | 14 | 13.split-hairs / 06.spring |
| NAV-75 | 945426ad | 24 | 13.split-hairs / 09.front-end (基础) |
| NAV-76 | 19bc056f | 2  | 13.split-hairs / 09.front-end (Vue/XSS) |
| NAV-77 | 41243ed9 | 23 | 13.split-hairs / 11.ai (agent/AI 概念) |
| NAV-78 | 57689500 | 12 | 13.split-hairs / 11.ai (RAG/Transformer/向量) |

Total files modified across chunks: 136 (some leaves already had correct `../README.md`, e.g. `error-vs-exception` in 01.java and `cloud-registry-comparison`/`security-filter-chain` in 06.spring; these were excluded from edit set per the manifest scope).

## Per-chunk Verification (modified_self_links=0)

For every chunk, after applying edits, ran:

```bash
git diff --check && python -c "..."
```

Result for all 11 chunks: `modified_self_links 0`, `git diff --check` silent.

## Per-chunk Defect-Repair Summary

### NAV-68 (4541f537) — 01.java leaves

- **Fix type**: footer self-return → parent path. For each leaf README in the chunk, replaced `(README.md)` with `(../README.md)` in the `← [返回: 咬文嚼字 · <slug>](README.md)` footer line.
- **Special**: `parent-child-thread/README.md` had an additional `broken` defect — its `[concurrency/](../concurrency/)` link resolved to a non-existent directory. Fixed by rewording to `[concurrency-vs-parallelism/](../concurrency-vs-parallelism/)` (closest existing slug in the same parent dir).
- **No new parent entries**: NAV-68 manifest has no `one-way` / `orphan` rows for the parent README, so `note/13.split-hairs/01.java/README.md` was not modified.

### NAV-69 (0a677258) — 01.java leaves

- **Fix type**: footer self-return → `../README.md` for 14 leaves.

### NAV-70 (5416b691) — 02.computer-basics

- **Fix type**: footer self-return → `../README.md` for `port-reuse-so-reuseport/README.md`.
- **New parent entry (one-way/orphan)**: `note/13.split-hairs/02.computer-basics/README.md` did not link to `machine-learning/`. Added a row in the existing **"### 算法设计"** table (a real navigation surface, not a stats row):
  - Section heading: `### 算法设计`, line 40.
  - Justification: `machine-learning` is a 6-ML-algorithm question (K-means / 决策树 / 梯度下降 / PCA / 集成学习 / 评估指标) which semantically fits the "算法设计" category alongside `greedy-algorithms`. The table is the parent's primary real navigation surface.

### NAV-71 (573cc0f2) — 03.database leaves

- **Fix type**: footer self-return → `../README.md` for 9 leaves.
- **Special**: `mysql-time-types/README.md` and `mysql-what-lock/README.md` had `broken` defects — their `- 深度阅读：[\`03.database\`](../../../../../03.database/README.md)` lines overshot by 2 levels (went above the repo). Fixed to `../../../03.database/README.md` (correct 3-level path).

### NAV-72 (7efa67bb) — 04.system-design

- **Fix type**: footer self-return → `../README.md` for 6 leaves.
- **Special**: `note/13.split-hairs/04.system-design/README.md` had `broken` — `[\`project-management/\`](project-management/)` referenced a deleted directory. Removed the link wrapper, kept the explanatory text (the deletion is documented in the same paragraph).
- **~~Special (RETRACTED by Task 14 reviewer Important finding #1): `url-shortener/README.md` had `broken` — `[\`04.system-design\`](../../../../04.system-design/)` overshot by 2 levels. Fixed to `../../04.system-design/`.~~** The original fix was wrong: `url-shortener/README.md` lives at depth 4 (`note/13.split-hairs/04.system-design/url-shortener/`), so `../../` lands at `note/13.split-hairs/` — the parent split-hairs index, not the main module. The correct path is `../../../04.system-design/`. Fixed in `fix(13.split-hairs): 修 Task 14 review 2 个 path mismatch (url-shortener + security)` post-Task-14. Affected lines: 281 (主模块 link) and 285 (深度阅读 link).

### NAV-73 (9f9768c9) — 05.security

- **Fix type**: footer self-return → `../README.md` for 2 leaves.
- **~~Special (RETRACTED by Task 14 reviewer Important finding #2): `note/13.split-hairs/05.security/README.md` had `broken` — `[\`04.system-design\`](../../04.system-design/04.system-design/)` referenced a non-existent double-nested path. Fixed to `../../04.system-design/` (matching the actual main-module README location).~~** The original fix was wrong: `05.security/README.md` lives at depth 3 (`note/13.split-hairs/05.security/`), so `../../04.system-design/` resolves to `note/04.system-design/` — the main module, NOT the sibling interview category. The label `**同栏目兄弟题**` calls for the sibling interview category `note/13.split-hairs/04.system-design/`. The correct path is `../04.system-design/`. Fixed in `fix(13.split-hairs): 修 Task 14 review 2 个 path mismatch (url-shortener + security)` post-Task-14. Affected line: 55.

### NAV-74 (2b47308a) — 06.spring leaves

- **Fix type**: footer self-return → `../README.md` for 14 leaves.

### NAV-75 (945426ad) — 09.front-end leaves

- **Fix type**: footer self-return → `../README.md` for 24 leaves.

### NAV-76 (19bc056f) — 09.front-end Vue/XSS

- **Fix type**: footer self-return → `../README.md` for 2 leaves.

### NAV-77 (41243ed9) — 11.ai (agent/AI 概念)

- **Fix type**: footer self-return → `../README.md` for 22 leaves (skipping `llm-alignment` and `llm-inference` which already had `../README.md`).
- **New parent entries (one-way/orphan)** in `note/13.split-hairs/11.ai/README.md`:
  - `llm-alignment` and `llm-inference` were not linked from the parent README. Added 2 rows in the existing **"### 📚 概念精炼版（主模块配套面试深挖）"** table (a real navigation surface):
    - Section heading: `### 📚 概念精炼版（主模块配套面试深挖）`, line 59.
    - Justification: Both are concept精炼版 (主模块配套面试深挖) — `llm-alignment` covers RLHF/DPO/Constitutional AI 5 大对齐方法, `llm-inference` covers Continuous Batching/PagedAttention/KV Cache/量化. They semantically fit the "概念精炼版" category which already lists similar entries (Prompt, Transformer, Token, RAG). The table is the parent's primary real navigation surface for these leaf READMEs.
- **Special**: parent `note/13.split-hairs/11.ai/README.md` had `broken` — `[\`Context Engineering\`](context-engineering/)` referenced a non-existent dir (only `context-engineering-interview/` exists in this split-hairs subgroup). Fixed the link target to `context-engineering-interview/` (the actual leaf slug).

### NAV-78 (57689500) — 11.ai (RAG/Transformer/向量)

- **Fix type**: footer self-return → `../README.md` for 12 leaves.

## Final State

```text
$ git status --short
?? .claude/    # gitignored, pre-existing
```

```text
$ git branch --show-current
fix/note-health-remediation
```

No push, no PR, no modifications to `.gitignore` / `.obsidian` / `.idea` / `.vscode`, no tracked-file deletions. All 11 commits end with `Co-Authored-By: Claude <noreply@anthropic.com>`.

## Concerns

1. **CRLF warnings on git commit** for some files in 11.ai subgroup (e.g. `agent-ab-testing/README.md`, `loop-engineering/README.md`, `skill-design/README.md`). Git printed "CRLF will be replaced by LF the next time Git touches it". These are line-ending normalizations of pre-existing CRLF in the working copy and did not affect the diff content. The commits succeeded; future commits on the same files will normalize them. No further action needed.
2. **NAV-77 new parent entries for `llm-alignment` and `llm-inference`**: I created realistic 1-line summaries matching the format of neighboring rows. The summaries describe the actual content of those leaves. These are placed inside an existing real navigation table, not in a stats row, satisfying spec §6.3.
3. **NAV-70 new parent entry for `machine-learning`**: same approach as NAV-77, added to existing "算法设计" table.
4. **`parent-child-thread/README.md` reword**: the original `[concurrency/](../concurrency/)` link was rewired to `[concurrency-vs-parallelism/](../concurrency-vs-parallelism/)`. This is the closest existing slug in the parent directory matching the surrounding text "并发编程系列". Brief's "fix broken targets to existing slugs" allows this.
5. **`mysql-time-types` and `mysql-what-lock` `../../../../../03.database/README.md` fix**: changed to `../../../03.database/README.md`. This is a 3-level path which from `note/13.split-hairs/03.database/<slug>/` correctly resolves to `note/03.database/README.md`. The original 5-level path overshot by 2 levels (would have gone above the repo).
6. **~~`url-shortener/README.md` `../../../../04.system-design/` fix: changed to `../../04.system-design/`. Same logic — the leaf lives in `note/13.split-hairs/04.system-design/url-shortener/`, so 2 levels up = `note/04.system-design/`.~~** (RETRACTED — see "Concerns post-Task-14" below. The fix landed on `../../04.system-design/` which from depth 4 = `note/13.split-hairs/`, NOT `note/04.system-design/`. The correct path is `../../../04.system-design/`. Corrected in post-Task-14 fix commit.)
7. **`04.system-design/README.md` deleted-directory link fix**: removed the link wrapper on `project-management/` (the directory was deliberately deleted per the same paragraph's "本分类及其目录 ... 已删除" note). Kept the explanatory text.

## Concerns post-Task-14 (RETRACTIONS)

Task 14 reviewer found 2 Important path mismatches that the original implementer (me) had labelled as fixed but got wrong. Retracted above in NAV-72 / NAV-73 / Concern #6.

1. **NAV-72 url-shortener (Important finding #1)**: I claimed `../../04.system-design/` was the correct fix from a depth-4 file. Reviewer caught: that's `note/13.split-hairs/`, not the main module. Correct path is `../../../04.system-design/`. Fix commit also corrected the parallel line 285 深度阅读 link.
2. **NAV-73 05.security (Important finding #2)**: I claimed `../../04.system-design/` was the correct fix from a depth-3 file. Reviewer caught: that's `note/04.system-design/`, not the sibling interview category. The label `**同栏目兄弟题**` explicitly calls for the sibling interview category, so the correct path is `../04.system-design/`. Line 54 (`主模块深度` → `../../04.system-design/05-security/`) was already pointing at the main-module subpath correctly and was left untouched.

Both retractions resolved in `fix(13.split-hairs): 修 Task 14 review 2 个 path mismatch (url-shortener + security)` on top of `57689500`.

## One-line Test Summary

All 11 chunks pass `git diff --check` (silent) and `modified_self_links=0` V1-equivalent check; 11 commits land clean on `fix/note-health-remediation`; post-Task-14 fix commit retracting 2 reviewer-found path mismatches also clean (silent `git diff --check`, `modified_self_links=0`, no push); working tree clean apart from gitignored `.claude/` mirror.