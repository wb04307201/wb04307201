"""Precise compare source vs target broken links.

For each link in source/target, compute the canonical resolved path.
Compare resolved paths to find:
  - source broken (didn't resolve in source) that also don't resolve in target (same broken set)
  - target broken (didn't resolve in target) that are NEW (not in source broken set)
"""
import re
import os
import subprocess

PROJECT_ROOT = r"D:\developer\IdeaProjects\wb04307201"
SOURCE_PREFIX = "note/13.split-hairs/"
TARGET_DIR = os.path.join(PROJECT_ROOT, "note-temp", "12.interview")
LINK_RE = re.compile(r"\]\(((?:\.\./)+[^)\s]+)\)")


def normalize_path(rel_f: str, rel_link: str) -> str:
    """Compute canonical resolved path (forward slashes, no trailing slash)."""
    # rel_f and rel_link are forward-slash relative paths
    target = os.path.normpath(os.path.join(os.path.dirname(rel_f), rel_link))
    return target.replace(os.sep, "/")


def get_source_links():
    """Get all source links from HEAD~1 source files."""
    result = subprocess.run(
        ["git", "-C", PROJECT_ROOT, "ls-tree", "-r", "--name-only", "HEAD~1", SOURCE_PREFIX],
        capture_output=True, encoding="utf-8"
    )
    files = [f for f in result.stdout.strip().split("\n") if f.endswith(".md")]
    links = []
    for rel_f in files:
        content = subprocess.run(
            ["git", "-C", PROJECT_ROOT, "show", f"HEAD~1:{rel_f}"],
            capture_output=True, encoding="utf-8"
        ).stdout
        for m in LINK_RE.finditer(content):
            target = normalize_path(rel_f, m.group(1))
            links.append((rel_f, m.group(1), target))
    return links


def get_target_links():
    """Get all target links from current working tree."""
    links = []
    for root, _, files in os.walk(TARGET_DIR):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            abs_f = os.path.join(root, fn)
            with open(abs_f, "r", encoding="utf-8") as fp:
                content = fp.read()
            for m in LINK_RE.finditer(content):
                # Convert abs_f to forward-slash rel path
                rel_f = os.path.relpath(abs_f, PROJECT_ROOT).replace(os.sep, "/")
                target = normalize_path(rel_f, m.group(1))
                links.append((rel_f, m.group(1), target))
    return links


src_links = get_source_links()
tgt_links = get_target_links()

# Group by canonical target path (since same target may have multiple link texts)
def classify(links):
    broken_set = set()
    for src_f, link_text, target in links:
        abs_target = os.path.join(PROJECT_ROOT, target)
        if not os.path.exists(abs_target):
            broken_set.add(target)
    return broken_set

src_broken = classify(src_links)
tgt_broken = classify(tgt_links)

print(f"Source: {len(src_links)} links, {len(src_broken)} unique broken targets")
print(f"Target: {len(tgt_links)} links, {len(tgt_broken)} unique broken targets")

new_broken = tgt_broken - src_broken
fixed_broken = src_broken - tgt_broken

print(f"\n=== Delta ===")
print(f"New broken targets (introduced): {len(new_broken)}")
print(f"Fixed broken targets: {len(fixed_broken)}")

if new_broken:
    print(f"\nNew broken samples:")
    for t in sorted(new_broken)[:30]:
        print(f"  {t}")

if fixed_broken:
    print(f"\nFixed broken samples:")
    for t in sorted(fixed_broken)[:30]:
        print(f"  {t}")

# Per-link analysis (most accurate)
print(f"\n=== Per-link analysis ===")
# Note: source link texts may differ from target link texts after our fix
# But the resolved target paths should be the same modulo the note/ prefix

# Build source broken targets by resolved target
# For source, before fix: ../X.Y./... -> note/X.Y./... (add note/ prefix)
# For target, after fix: ../../note/X.Y./... (already has note/ prefix)

# So we should compare by stripping/adding note/ prefix
print("Comparing source resolved targets (pre-fix paths) to target (post-fix paths)...")

# For source: each resolved path is relative to source file
# After migration, source file is at new path with same relative structure (same ../X.Y./ -> ../note/X.Y./)
# So source links should be re-resolved from new locations
def re_resolve_source_links():
    """Re-resolve source links as if they were in target location (same depth + 1)."""
    relinks = []
    for src_f, link_text, target in src_links:
        # src_f: note/13.split-hairs/X/Y/Z/...
        # new location: note-temp/12.interview/X/Y/Z/...
        # So new resolved target = target + 1 ../ prefix (to go from 12.interview/X to note-temp)
        # Actually: target is absolute path (resolved)
        # The link text needs to be updated, but the target absolute path is the same
        # So just use the same target (since target is absolute)
        relinks.append((src_f, link_text, target))
    return relinks

# OK source links resolved targets == target links resolved targets (in terms of absolute file paths)
# Since both source and target reference the same actual file paths

# Let me re-compute by per-link analysis
src_broken_per_link = set()
for src_f, link_text, target in src_links:
    abs_target = os.path.join(PROJECT_ROOT, target)
    if not os.path.exists(abs_target):
        # Use link_text as the key (since same target may be reached via different link texts)
        src_broken_per_link.add((src_f, link_text, target))

tgt_broken_per_link = set()
for src_f, link_text, target in tgt_links:
    abs_target = os.path.join(PROJECT_ROOT, target)
    if not os.path.exists(abs_target):
        tgt_broken_per_link.add((src_f, link_text, target))

print(f"Per-link source broken: {len(src_broken_per_link)}")
print(f"Per-link target broken: {len(tgt_broken_per_link)}")

# Compute per-link delta
new_per_link = tgt_broken_per_link - src_broken_per_link
fixed_per_link = src_broken_per_link - tgt_broken_per_link
print(f"Per-link new broken: {len(new_per_link)}")
print(f"Per-link fixed broken: {len(fixed_per_link)}")

if new_per_link:
    print("\nNEW per-link broken samples:")
    for b in sorted(new_per_link)[:30]:
        print(f"  {b[0]} -> {b[1]} (resolved: {b[2]})")