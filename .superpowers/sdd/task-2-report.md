# Task 2 Report — Batch 1 Navigation — 01.java

- **Status:** DONE_WITH_CONCERNS
- **Branch:** `fix/note-health-remediation`
- **Base:** e5906016

## Chunks

| Chunk | Commit hash | Defects | Files touched |
|-------|-------------|---------|----------------|
| NAV-01 (collection) | `91700e57` | 8 | 1 (`note/01.java/collection/README.md`) |
| NAV-02 (concepts)  | `1e27aac6` | 1 | 1 (`note/01.java/concepts/README.md`) |
| NAV-03 (concurrency) | `6f678fee` | 11 | 5 (`note/01.java/concurrency/{README.md,concurrent-collections/{README.md,copy-on-write/README.md,queue/README.md,skip-list/README.md}}`) |
| NAV-04 (design-patterns) | `b7c3a492` | 6 | 3 (`note/01.java/design-patterns/{behavioral,creation,structural}/README.md`) |
| NAV-05 (io) | `6c5243eb` | 3 | 1 (`note/01.java/io/README.md`) |

## Per-chunk verification

All 5 chunks recorded `modified_self_links=0` (V1-equivalent per brief §Step 4) before commit.

| Chunk | self_links=0 | git diff --check |
|-------|--------------|------------------|
| NAV-01 | yes | silent |
| NAV-02 | yes | silent |
| NAV-03 | yes | silent |
| NAV-04 | yes | silent |
| NAV-05 | yes | silent |

## Final state

```
git status --short   → (empty)
git branch --show-current → fix/note-health-remediation
no push performed
```

`git log --oneline -6` shows the 5 expected `fix(01.java)` commits plus the base `e5906016`:

```
91700e57 fix(01.java): 修复 collection 子 README 父索引反链 (NAV-01)
6f678fee fix(01.java): 修复 concurrency 自链 footer + 父索引反链 (NAV-03)
1e27aac6 fix(01.java): 修复 concepts date-time 子 README 父索引反链 (NAV-02)
6c5243eb fix(01.java): 修复 io 子 README 父索引反链 (NAV-05)
b7c3a492 fix(01.java): 修复 design-patterns 子 README 自链 footer (NAV-04)
e5906016 docs(note): 实施 Batch 1-5 修复计划 + 6 份 tracked manifest
```

## Fix strategy

For each defect type, applied the minimal edit:

1. **invalid-return / self-return** (NAV-03, NAV-04) — footer `[...](README.md)` rewritten to `[...](../README.md)` (depth 2→3 traversal of parent index). No prose touched.
2. **one-way / orphan** (NAV-01, NAV-02, NAV-03, NAV-05) — leaf footer was already correct; defect is "parent index has no back-link". Added reciprocal entries in the closest parent index. The most minimal surface was the existing `📊 本节统计` table row that already listed leaf names as plain text. Converted those textual mentions into markdown links:
   - NAV-01: 6 leaf entries inside `collection/README.md` §本节统计。
   - NAV-02: `date-time` entry inside `concepts/README.md` §本节统计 (no categorized table fit).
   - NAV-03: added 3 new rows (十一/十二/十三) to `concurrency/README.md` §三 专题导航 table for `thread-basics` / `juc-locks` / `utilities` (existing rows 一-十 covered the other leaves).
   - NAV-05: 2 leaf entries (`nio`, `zero-copy`) inside `io/README.md` §本节统计.

Leaves themselves were edited only when their footer was a self-link (NAV-03 + NAV-04). For NAV-01, NAV-02, NAV-05 no leaf files were modified — the footer links were already valid; only the parent index needed a reciprocal link.

## Concerns

1. **Ambiguous location for orphan back-links.** For NAV-01 and NAV-02 the parent index has multiple possible insertion surfaces (categorized tables, statistics table, "相关章节" bullets). I picked the smallest, least-prose-affecting place: the existing `📊 本节统计` row that already named the leaf. This means the resulting back-links are visible only at the bottom of the parent README, not in a top-level navigation table. Acceptable but not ideal for discoverability.
2. **NAV-01 leaves with both `one-way` and `orphan` defects.** `LinkedHashSet` and `WeakHashMap` had two defect rows in the manifest. My single-link fix (parent index entry) addresses both, but if the health-check tool later distinguishes them, the "orphan" dimension may not register as fully resolved without a separate structural change (e.g., adding a dedicated leaf-index section). Worth confirming with the health-check author before treating the row as fully closed.
3. **NAV-02 `date-time` not in any categorized section.** The leaf is about the date/time API which doesn't map naturally to the parent's 4 categories (语言基础 / 面向对象 / 类型系统 / 核心机制). I only added it to the stats table link; the leaf still has no entry in a top-level navigation table. Confirm this is acceptable.
4. **Untracked `.python-version` / skill mirror files.** The plain `python` interpreter on PATH works (verified by running the V1 script inline), so the brief's 30/225 baseline was honored without setup script execution. No ambient edits made.
5. **Concern #5 retracted: `collection/README.md:348 -> concurrent.md` is not in the broken-links-2026-07-19.txt list; concurrent.md exists; link is valid. Original observation was a false positive.**

## One-line test summary

5 commits on `fix/note-health-remediation`, 5 chunks × `modified_self_links=0`, working tree clean, not pushed.
