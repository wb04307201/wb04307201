"""Verify Task 9 link fix matches Task 8 pattern.

Checks:
  1. ZERO cross-module links (../X.Y./ where X.Y. is module prefix) WITHOUT note/ prefix
  2. Pre-existing broken count (target file doesn't exist) compared to source baseline
"""
import os
import re
import sys
import subprocess

PROJECT_ROOT = r"D:\developer\IdeaProjects\wb04307201"
TARGET_DIR = os.path.join(PROJECT_ROOT, "note-temp", "11.product-and-pm")
SOURCE_PREFIX = "note/14.project-management/"


def git_cat_file_exists(ref: str, path: str) -> bool:
    """Check if path exists in git ref."""
    result = subprocess.run(
        ["git", "-C", PROJECT_ROOT, "cat-file", "-e", f"{ref}:{path}"],
        capture_output=True
    )
    return result.returncode == 0


def collect_links_from_ref(ref: str, path_prefix: str) -> tuple[int, list]:
    """Collect relative markdown links from all .md files in ref:path_prefix."""
    LINK_RE = re.compile(r"\]\(((?:\.\./)+[^)\s]+)\)")
    result = subprocess.run(
        ["git", "-C", PROJECT_ROOT, "ls-tree", "-r", "--name-only", ref, path_prefix],
        capture_output=True, encoding="utf-8"
    )
    files = [f for f in result.stdout.strip().split("\n") if f.endswith(".md")]

    broken = []
    total = 0
    for rel_f in files:
        content = subprocess.run(
            ["git", "-C", PROJECT_ROOT, "show", f"{ref}:{rel_f}"],
            capture_output=True, encoding="utf-8"
        ).stdout
        for m in LINK_RE.finditer(content):
            rel = m.group(1)
            total += 1
            target_rel = os.path.normpath(os.path.join(os.path.dirname(rel_f), rel)).replace(os.sep, "/")
            if not git_cat_file_exists(ref, target_rel):
                broken.append((rel_f, rel, target_rel))
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
                target_fwd = target.replace(os.sep, "/")
                if not os.path.isfile(target_fwd):
                    broken.append((os.path.relpath(abs_f, PROJECT_ROOT), rel, target_fwd))
    return total, broken


# === Check 1: Task 8 pattern - no migration-related broken ===
print("=== Check 1: Cross-module links without note/ prefix (Task 8 pattern) ===")
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

# === Check 2: Pre-existing broken count (against git HEAD~1 baseline) ===
print()
print("=== Check 2: Broken link count vs source baseline (git HEAD~1) ===")
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
    sys.exit(1)
else:
    print("PASS: Migration did not introduce new broken links.")