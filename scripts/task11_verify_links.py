"""Verify Task 11 link fix matches Task 10 pattern.

Checks:
  1. ZERO cross-module links (../X.Y./ where X.Y. is module prefix) WITHOUT note/ prefix
  2. ZERO sibling ../12.story/ links remain (should be converted to ./Y.md)
  3. ZERO ../13.split-hairs/ links remain (should be converted to ../../note-temp/12.interview/)
  4. Pre-existing broken count (target doesn't exist) compared to source baseline

Note: Uses os.path.exists (accepts both files and directories).
"""
import os
import re
import sys
import subprocess

PROJECT_ROOT = r"D:\developer\IdeaProjects\wb04307201"
TARGET_DIR = os.path.join(PROJECT_ROOT, "note-temp", "13.story")
SOURCE_PREFIX = "note/12.story/"


def git_show(ref, path):
    """Get file content from git ref."""
    result = subprocess.run(
        ["git", "-C", PROJECT_ROOT, "show", f"{ref}:{path}"],
        capture_output=True, encoding="utf-8"
    )
    return result.stdout if result.returncode == 0 else ""


def git_ls_files(ref, path_prefix):
    """List all tracked .md files under path_prefix in ref."""
    result = subprocess.run(
        ["git", "-C", PROJECT_ROOT, "ls-tree", "-r", "--name-only", ref, path_prefix],
        capture_output=True, encoding="utf-8"
    )
    return [f for f in result.stdout.strip().split("\n") if f.endswith(".md")]


def collect_links_from_ref(ref: str, path_prefix: str) -> tuple[int, list]:
    """Collect relative markdown links from all .md files in ref:path_prefix."""
    LINK_RE = re.compile(r"\]\(((?:\.\./)+[^)\s]+)\)")
    files = git_ls_files(ref, path_prefix)

    broken = []
    total = 0
    for rel_f in files:
        content = git_show(ref, rel_f)
        for m in LINK_RE.finditer(content):
            rel = m.group(1)
            total += 1
            target = os.path.normpath(os.path.join(os.path.dirname(rel_f), rel)).replace(os.sep, "/")
            abs_target = os.path.join(PROJECT_ROOT, target)
            if not os.path.exists(abs_target):
                broken.append((rel_f, rel, target))
    return total, broken


def collect_links_from_target() -> tuple[int, list]:
    """Collect relative markdown links from all .md files in target dir (working tree)."""
    LINK_RE = re.compile(r"\]\(((?:\.\./)+[^)\s]+)\)")
    broken = []
    total = 0
    for root, _, files in os.walk(TARGET_DIR):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            abs_f = os.path.join(root, fn)
            with open(abs_f, "r", encoding="utf-8") as fp:
                content = fp.read()
            for m in LINK_RE.finditer(content):
                rel = m.group(1)
                total += 1
                target = os.path.normpath(os.path.join(os.path.dirname(abs_f), rel))
                if not os.path.exists(target):
                    broken.append((os.path.relpath(abs_f, PROJECT_ROOT), rel, target))
    return total, broken


# === Check 1: Cross-module links without note/ prefix ===
print("=== Check 1: Cross-module links without note/ prefix (Task 10 pattern) ===")
import glob
no_note_links = []
for md in glob.glob(os.path.join(TARGET_DIR, "**/*.md"), recursive=True):
    with open(md, "r", encoding="utf-8") as fp:
        for ln, line in enumerate(fp, 1):
            for m in re.finditer(r"(\]\()((?:\.\./)+)(\d+\.[a-z][a-z0-9-]*)", line):
                rel = m.group(2) + m.group(3)
                if "note/" not in rel:
                    no_note_links.append((os.path.relpath(md, PROJECT_ROOT), ln, m.group(0)))

print(f"Links missing note/ prefix: {len(no_note_links)}")
if no_note_links:
    for l in no_note_links[:10]:
        print(f"  {l[0]}:{l[1]}: {l[2]}")
    sys.exit(1)
else:
    print("PASS: All cross-module links have note/ prefix.")

# === Check 2: Sibling ../12.story/ links should be removed ===
print()
print("=== Check 2: Sibling ../12.story/ links should be removed ===")
sib_links = []
for md in glob.glob(os.path.join(TARGET_DIR, "**/*.md"), recursive=True):
    with open(md, "r", encoding="utf-8") as fp:
        for ln, line in enumerate(fp, 1):
            for m in re.finditer(r"\]\(((\.\./)+)12\.story", line):
                sib_links.append((os.path.relpath(md, PROJECT_ROOT), ln, m.group(0)))
print(f"Sibling ../12.story/ links remaining: {len(sib_links)}")
if sib_links:
    for l in sib_links[:10]:
        print(f"  {l[0]}:{l[1]}: {l[2]}")
    sys.exit(1)
else:
    print("PASS: No sibling ../12.story/ links remain.")

# === Check 3: ../13.split-hairs/ links should be updated ===
print()
print("=== Check 3: ../13.split-hairs/ links should be updated ===")
sh_links = []
for md in glob.glob(os.path.join(TARGET_DIR, "**/*.md"), recursive=True):
    with open(md, "r", encoding="utf-8") as fp:
        for ln, line in enumerate(fp, 1):
            for m in re.finditer(r"\]\(((\.\./)+)13\.split-hairs", line):
                sh_links.append((os.path.relpath(md, PROJECT_ROOT), ln, m.group(0)))
print(f"../13.split-hairs/ links remaining: {len(sh_links)}")
if sh_links:
    for l in sh_links[:10]:
        print(f"  {l[0]}:{l[1]}: {l[2]}")
    sys.exit(1)
else:
    print("PASS: No ../13.split-hairs/ links remain.")

# === Check 4: Broken link count vs source baseline ===
print()
print("=== Check 4: Broken link count vs source baseline (git HEAD~1) ===")
src_total, src_broken = collect_links_from_ref("HEAD~1", SOURCE_PREFIX)
print(f"Source (HEAD~1): {src_total} relative links, {len(src_broken)} broken")

tgt_total, tgt_broken = collect_links_from_target()
print(f"Target:          {tgt_total} relative links, {len(tgt_broken)} broken")

# Delta
print()
print("=== Delta ===")
delta = len(tgt_broken) - len(src_broken)
print(f"Source broken: {len(src_broken)}, Target broken: {len(tgt_broken)}, Delta: {delta:+d}")
if delta > 0:
    print(f"FAIL: Migration introduced {delta} new broken links.")
    # Show new broken
    src_broken_set = set((b[1], b[2]) for b in src_broken)
    new_broken = [(t[0], t[1], t[2]) for t in tgt_broken if (t[1], t[2]) not in src_broken_set]
    print(f"New broken details (first 30):")
    for b in new_broken[:30]:
        print(f"  NEW_BROKEN: {b[0]} -> {b[1]} (resolved: {b[2]})")
    sys.exit(1)
else:
    print("PASS: Migration did not introduce new broken links.")

# Show fixed broken samples
if delta < 0:
    src_broken_set = set((b[1], b[2]) for b in src_broken)
    fixed = [(t[0], t[1], t[2]) for t in tgt_broken if (t[1], t[2]) in src_broken_set]
    print(f"Fixed (was broken in source, now works): {len(fixed)}")

# Show remaining broken (likely pre-existing)
if tgt_broken:
    print(f"\nRemaining broken (first 20):")
    for b in tgt_broken[:20]:
        print(f"  {b[0]} -> {b[1]} (resolved: {b[2]})")