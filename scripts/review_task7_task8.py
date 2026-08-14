#!/usr/bin/env python3
"""Task 7 + Task 8 fix verification script.

For each .md file under note-temp/07.devops-and-tools/ and note-temp/10.business-systems/:
  1. Extract all relative `../` style paths (looking inside markdown links)
  2. Resolve them against the file's directory
  3. For paths that include `note/<module>/`, verify the target file exists
  4. For paths that don't include `note/` but DO reference other modules (e.g. `../01.java/`), flag as broken
  5. Report per-file `../` count vs file depth
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

REPO = Path("D:/developer/IdeaProjects/wb04307201").resolve()

# Scan directories
SCAN_DIRS = [
    REPO / "note-temp" / "07.devops-and-tools",
    REPO / "note-temp" / "10.business-systems",
]

# Match markdown links like [text](path) where path starts with ../
LINK_RE = re.compile(r"\]\(([^\)]+)\)")

# Cross-module link pattern: matches ../X.Y/ where X is 1-14 and Y is module-name
# These need to be flagged as broken (without note/ prefix)
CROSS_MOD_RE = re.compile(r"^(\.\./)+(?:[0-9]+\.[a-z][a-z-]*)")

# Target module pattern for verification
TARGET_RE = re.compile(r"^(?:(?:\.\./)+)note/([0-9]+\.[a-z-]+)/?(.*)$")


def file_depth(filepath: Path) -> int:
    """Compute directory depth relative to repo root.

    e.g.:
      note-temp/07.devops-and-tools/README.md => 1
      note-temp/07.devops-and-tools/01-tools/README.md => 2
      note-temp/07.devops-and-tools/01-tools/01-git/README.md => 3
      note-temp/07.devops-and-tools/01-tools/01-git/command/README.md => 4
    """
    rel = filepath.relative_to(REPO)
    return len(rel.parts) - 1  # minus the filename


def check_file(filepath: Path):
    """Scan one .md file for relative-path links and verify them."""
    depth = file_depth(filepath)
    rel = filepath.relative_to(REPO)

    content = filepath.read_text(encoding="utf-8")
    broken_cross = []
    resolved_targets = []
    upcount_total = 0

    for m in LINK_RE.finditer(content):
        path_str = m.group(1)
        # Skip absolute URLs and anchors-only
        if path_str.startswith(("http://", "https://", "#", "mailto:", "tel:")):
            continue
        # Skip non-relative
        if not path_str.startswith("../"):
            continue
        # Count `../` segments
        upcount = 0
        for seg in path_str.split("/"):
            if seg == "..":
                upcount += 1
            else:
                break
        upcount_total += upcount

        # Resolve against file's directory
        target_abs = (filepath.parent / path_str).resolve()

        # Categorize:
        # 1. References `note/<module>/` => resolved target should exist
        # 2. References other module like `../01.java/...` directly (no note/ prefix) => BROKEN
        # 3. Internal navigation (e.g., ../README.md, ../sibling/) => OK if target exists
        m_target = TARGET_RE.match(path_str)
        if m_target:
            module_name = m_target.group(1)
            sub_path = m_target.group(2)
            resolved_targets.append((path_str, module_name, sub_path, target_abs, upcount))
        else:
            # Check if it looks like a cross-module reference
            m_cross = CROSS_MOD_RE.match(path_str)
            if m_cross:
                broken_cross.append((path_str, upcount))

    return {
        "file": str(rel),
        "depth": depth,
        "broken_cross": broken_cross,
        "resolved_targets": resolved_targets,
        "upcount_total": upcount_total,
    }


def main():
    results = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            print(f"[skip] {scan_dir} not found")
            continue
        for md_file in sorted(scan_dir.rglob("*.md")):
            results.append(check_file(md_file))

    # ====== Summary ======
    total_files = len(results)
    broken_cross_total = sum(len(r["broken_cross"]) for r in results)
    resolved_targets_total = sum(len(r["resolved_targets"]) for r in results)

    print(f"=== Summary ===")
    print(f"Files scanned: {total_files}")
    print(f"Broken cross-module refs (no note/ prefix): {broken_cross_total}")
    print(f"Resolved note/ refs to verify: {resolved_targets_total}")
    print()

    # ====== Broken cross-module ======
    if broken_cross_total > 0:
        print("=== BROKEN CROSS-MODULE LINKS ===")
        for r in results:
            if r["broken_cross"]:
                print(f"  {r['file']} (depth={r['depth']})")
                for path_str, upcount in r["broken_cross"]:
                    print(f"    [{path_str}]  (upcount={upcount})")
        print()
    else:
        print("OK: 0 broken cross-module links (without note/ prefix)")
        print()

    # ====== Verify resolved targets exist ======
    target_missing = []
    for r in results:
        for path_str, module_name, sub_path, target_abs, upcount in r["resolved_targets"]:
            if not target_abs.exists():
                target_missing.append((r["file"], path_str, target_abs))

    if target_missing:
        print("=== MISSING TARGETS ===")
        for f, path_str, target_abs in target_missing:
            print(f"  {f}: [{path_str}] => {target_abs}")
    else:
        print("OK: All resolved targets exist on disk")
        print()

    # ====== Per-file ../ count check ======
    print("=== Per-file ../ count ===")
    # Files that have at least one resolved target
    files_with_refs = [r for r in results if r["resolved_targets"]]

    # Expected: for a file at depth N (1=top), a `note/<X>/` reference from leaf
    # of depth N needs N+1 `../`. We verify max upcount vs depth.
    # Actually expected:
    #   depth-1 README (e.g. 10.business-systems/README.md): 2 ups to reach note/ (../../note/X)
    #   depth-2 leaf (e.g. 01-tools/README.md): 3 ups (../../../note/X)
    #   depth-3 leaf (e.g. 01-tools/01-git/README.md): 4 ups
    #   depth-4 leaf (e.g. 01-tools/01-git/command/README.md): 5 ups
    # The expected formula is: required ups = depth + 2 (since `note/X` is two levels above note-temp/<module>/)
    # Wait - let me think. From note-temp/07.devops-and-tools/01-tools/README.md (depth=2 in our model, relative to repo it's note-temp/07.devops-and-tools/01-tools/README.md):
    #   ../ = note-temp/07.devops-and-tools/01-tools/  -> ..  (up 1)
    #   ../../ = note-temp/07.devops-and-tools/  -> up 2
    #   ../../../ = note-temp/  -> up 3
    #   ../../../../ = note/  -> up 4  ✓
    # So from a depth-2 file (relative to repo), need 4 ups.
    # Pattern: needed ups = depth + 2.
    # Verify this is consistent with all files.

    issues = []
    for r in files_with_refs:
        for path_str, module_name, sub_path, target_abs, upcount in r["resolved_targets"]:
            expected = r["depth"] + 2
            if upcount != expected:
                issues.append({
                    "file": r["file"],
                    "depth": r["depth"],
                    "path_str": path_str,
                    "upcount": upcount,
                    "expected": expected,
                })

    if issues:
        print(f"=== ../ count mismatches ({len(issues)}) ===")
        for i in issues:
            print(f"  {i['file']} (depth={i['depth']}, expected upcount={i['expected']}, actual={i['upcount']}): [{i['path_str']}]")
    else:
        print(f"OK: All {resolved_targets_total} resolved targets have correct ../ count for their file depth")

    # Per-file upcount tally for inspection
    print()
    print("=== Files with cross-module references (sorted by depth) ===")
    files_with_refs_sorted = sorted(files_with_refs, key=lambda r: (r["depth"], r["file"]))
    for r in files_with_refs_sorted:
        unique_upcounts = sorted(set(upc for _, _, _, _, upc in r["resolved_targets"]))
        print(f"  depth={r['depth']}  ups={unique_upcounts}  {r['file']}  ({len(r['resolved_targets'])} refs)")


if __name__ == "__main__":
    main()
