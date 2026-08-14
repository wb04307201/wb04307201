#!/usr/bin/env python3
"""Task 7 + Task 8 fix verification — focused checks per brief.

Brief asks:
  (1) Resolve all ../ paths in 07.devops-and-tools/ and confirm 0 broken (no note/ prefix)
  (2) Check 13 fixed files' ../ counts are correct per file depth
  (3) Spot-check Task 8 leaf file content integrity
"""

import os
import re
from pathlib import Path
from collections import defaultdict

REPO = Path("D:/developer/IdeaProjects/wb04307201").resolve()

LINK_RE = re.compile(r"\]\(([^\)]+)\)")

# Pattern 1: cross-module link WITHOUT note/ prefix (this is the "broken" pattern)
CROSS_MOD_NO_NOTE = re.compile(r"^(?:\.\./)+([0-9]+\.[a-z][a-z-]*)")
# Pattern 2: cross-module link WITH note/ prefix (correct post-fix pattern)
CROSS_MOD_WITH_NOTE = re.compile(r"^(?:\.\./)+note/([0-9]+\.[a-z-]+)/?(.*)$")


def file_depth(filepath: Path) -> int:
    rel = filepath.relative_to(REPO)
    return len(rel.parts) - 1


def analyze(filepath: Path):
    depth = file_depth(filepath)
    rel = filepath.relative_to(REPO)
    content = filepath.read_text(encoding="utf-8")

    broken_no_note = []  # cross-module ref without note/ prefix (BAD)
    with_note_refs = []  # cross-module ref with note/ prefix (GOOD, verify upcount)

    for m in LINK_RE.finditer(content):
        path_str = m.group(1)
        if path_str.startswith(("http://", "https://", "#", "mailto:", "tel:")):
            continue
        if not path_str.startswith("../"):
            continue
        # Count ups
        upcount = 0
        for seg in path_str.split("/"):
            if seg == "..":
                upcount += 1
            else:
                break

        m_no = CROSS_MOD_NO_NOTE.match(path_str)
        m_with = CROSS_MOD_WITH_NOTE.match(path_str)
        if m_no and not m_with:
            # It's a cross-module ref WITHOUT note/ prefix = BROKEN
            broken_no_note.append((path_str, upcount))
        elif m_with:
            with_note_refs.append((path_str, m_with.group(1), m_with.group(2), upcount))

    return {
        "file": str(rel),
        "depth": depth,
        "broken_no_note": broken_no_note,
        "with_note_refs": with_note_refs,
    }


def main():
    scan_dirs = [
        REPO / "note-temp" / "07.devops-and-tools",
        REPO / "note-temp" / "10.business-systems",
    ]

    # Check 1: 0 broken (no note/ prefix) in 07.devops-and-tools/
    print("=" * 80)
    print("CHECK 1: Task 7 fix — 0 broken cross-module refs (without note/ prefix)")
    print("         Scope: note-temp/07.devops-and-tools/")
    print("=" * 80)
    scan_dir = REPO / "note-temp" / "07.devops-and-tools"
    results_t7 = []
    for md in sorted(scan_dir.rglob("*.md")):
        results_t7.append(analyze(md))

    total_broken_t7 = sum(len(r["broken_no_note"]) for r in results_t7)
    files_with_broken_t7 = [r for r in results_t7 if r["broken_no_note"]]
    print(f"Files scanned: {len(results_t7)}")
    print(f"Total broken (../X.Y/ without note/ prefix): {total_broken_t7}")
    if files_with_broken_t7:
        print("BROKEN files:")
        for r in files_with_broken_t7:
            print(f"  {r['file']}: {r['broken_no_note']}")
    else:
        print("PASS: 0 broken cross-module refs")

    print()

    # Check 2: ../ count correct per file depth
    print("=" * 80)
    print("CHECK 2: ../ count correct for each file's depth")
    print("         Expected: upcount == depth (for note/X/ refs)")
    print("=" * 80)
    print()
    print("Quick math: From a file at depth N (parts-1), need N ../ to reach repo root,")
    print("then 'note/X/' is one path segment, so the link starts with N ../'s then 'note/'.")
    print()
    print("Examples:")
    print("  depth=2 (note-temp/07.devops-and-tools/README.md) -> ../../note/X/")
    print("  depth=3 (note-temp/07.devops-and-tools/01-tools/README.md) -> ../../../note/X/")
    print("  depth=4 (note-temp/07.devops-and-tools/01-tools/03-java/README.md) -> ../../../../note/X/")
    print("  depth=7 (note-temp/07.devops-and-tools/02-workflow/process-engine/camunda/camunda-8/zeebe/README.md) -> ../../../../../../../note/X/")
    print()

    all_refs = []
    for r in results_t7:
        if r["with_note_refs"]:
            for path_str, module, subpath, upcount in r["with_note_refs"]:
                all_refs.append((r["file"], r["depth"], path_str, module, upcount))

    print(f"Total cross-module refs (with note/ prefix): {len(all_refs)}")
    issues = []
    for f, depth, path_str, module, upcount in all_refs:
        expected = depth  # need depth `../` to reach repo root from a depth-N file
        if upcount != expected:
            issues.append((f, depth, path_str, upcount, expected))

    if issues:
        print(f"FAIL: {len(issues)} upcount mismatches")
        for f, depth, path_str, upcount, expected in issues:
            print(f"  {f} (depth={depth}): expected {expected} ups, got {upcount}: [{path_str}]")
    else:
        print(f"PASS: All {len(all_refs)} refs have correct upcount for their file depth")

    print()

    # Per-file summary
    print("--- Per-file cross-module refs in 07.devops-and-tools/ ---")
    refs_by_file = defaultdict(list)
    for f, depth, path_str, module, upcount in all_refs:
        refs_by_file[f].append((depth, upcount, path_str))
    for f in sorted(refs_by_file.keys()):
        entries = refs_by_file[f]
        depths = list(set(d for d, _, _ in entries))
        upcounts = list(set(u for _, u, _ in entries))
        print(f"  depth={depths[0]}  ups={upcounts[0]}  {f}  ({len(entries)} refs)")

    print()

    # Check 3: Task 8 same check
    print("=" * 80)
    print("CHECK 3: Task 8 spec — 0 broken cross-module refs (without note/ prefix)")
    print("         Scope: note-temp/10.business-systems/")
    print("=" * 80)
    scan_dir = REPO / "note-temp" / "10.business-systems"
    results_t8 = []
    for md in sorted(scan_dir.rglob("*.md")):
        results_t8.append(analyze(md))

    total_broken_t8 = sum(len(r["broken_no_note"]) for r in results_t8)
    files_with_broken_t8 = [r for r in results_t8 if r["broken_no_note"]]
    print(f"Files scanned: {len(results_t8)}")
    print(f"Total broken (../X.Y/ without note/ prefix): {total_broken_t8}")
    if files_with_broken_t8:
        print("BROKEN files:")
        for r in files_with_broken_t8:
            print(f"  {r['file']}: {r['broken_no_note']}")
    else:
        print("PASS: 0 broken cross-module refs")

    print()
    print("--- Per-file cross-module refs in 10.business-systems/ ---")
    refs_by_file = defaultdict(list)
    for r in results_t8:
        if r["with_note_refs"]:
            for path_str, module, subpath, upcount in r["with_note_refs"]:
                refs_by_file[r["file"]].append((r["depth"], upcount, path_str))
    for f in sorted(refs_by_file.keys()):
        entries = refs_by_file[f]
        depths = list(set(d for d, _, _ in entries))
        upcounts = list(set(u for _, u, _ in entries))
        print(f"  depth={depths[0]}  ups={upcounts[0]}  {f}  ({len(entries)} refs)")

    print()
    # Check 4: Task 8 broken link count
    print("=" * 80)
    print("CHECK 4: Task 8 broken link repair count")
    print("         Expected per report: 4 leaf files / 9 broken link repairs")
    print("=" * 80)
    leaf_files_with_fixes = ["cms", "bi", "qms", "pms"]
    counts = {}
    for leaf in leaf_files_with_fixes:
        # Find the corresponding path
        matches = [r for r in results_t8 if leaf in r["file"] and "06-specialized" not in r["file"] or
                   (leaf == "pms" and r["file"].endswith("pms/README.md"))]
        if not matches:
            matches = [r for r in results_t8 if r["file"].endswith(f"/{leaf}/README.md")]
        if matches:
            counts[leaf] = len(matches[0]["with_note_refs"])

    total_leaf_refs = sum(counts.values())
    print(f"Per-file 'note/X' link counts (post-fix):")
    for leaf, count in counts.items():
        print(f"  {leaf}: {count} refs")
    print(f"Total leaf broken link fixes: {total_leaf_refs}")
    if total_leaf_refs == 9:
        print("PASS: matches report claim of 9 broken link repairs in 4 leaf files")
    else:
        print(f"NOTE: expected 9 per report, actual {total_leaf_refs}")


if __name__ == "__main__":
    main()
