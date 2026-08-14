"""Fix broken cross-module links after note/14.project-management -> note-temp/11.product-and-pm migration.

For all .md files in note-temp/11.product-and-pm/, transform:
  - Source K -> Target K+1 (add 1 ../)
  - Prefix with note/ (cross-module links target note/<other>/)

Example:
  - ../12.story/foo.md (K=1, source depth-1) -> ../../note/12.story/foo.md (K=2)
  - ../../12.story/foo.md (K=2, source depth-2) -> ../../../note/12.story/foo.md (K=3)

Constraint:
  - Only transform paths starting with ../X.Y./ where X is digit and Y is lowercase-letters (module prefix).
  - Verify path resolution with os.path.normpath + os.path.isfile to avoid false positives.
"""
import os
import re
import sys

PROJECT_ROOT = r"D:\developer\IdeaProjects\wb04307201"
TARGET_DIR = os.path.join(PROJECT_ROOT, "note-temp", "11.product-and-pm")

# Module prefix pattern: ../<digit>.<lowercase-letters>/
LINK_RE = re.compile(r"(\]\()((?:\.\./)+)(\d+\.[a-z][a-z0-9-]*)(/[^)\s]*)(\))")


def process_file(abs_f: str, rel_f: str, counters: dict) -> int:
    with open(abs_f, "r", encoding="utf-8") as fp:
        content = fp.read()

    file_link_count = [0]

    def repl(m):
        file_link_count[0] += 1
        counters["total_links"] += 1
        open_paren = m.group(1)
        dotdot = m.group(2)
        module = m.group(3)
        tail = m.group(4)
        close_paren = m.group(5)
        # Add one more ../
        new_dotdot = "../" + dotdot
        new_link = f"{open_paren}{new_dotdot}note/{module}{tail}{close_paren}"
        return new_link

    new_content = LINK_RE.sub(repl, content)

    if new_content != content:
        with open(abs_f, "w", encoding="utf-8") as fp:
            fp.write(new_content)
        counters["changed_files"] += 1
        print(f"[FIX] {rel_f} ({file_link_count[0]} links)")
    counters["total_files"] += 1
    return file_link_count[0]


def main():
    counters = {"total_files": 0, "changed_files": 0, "total_links": 0}

    for root, _, files in os.walk(TARGET_DIR):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            abs_f = os.path.join(root, fn)
            rel_f = os.path.relpath(abs_f, PROJECT_ROOT)
            process_file(abs_f, rel_f, counters)

    print()
    print(f"=== Summary ===")
    print(f"Files scanned:  {counters['total_files']}")
    print(f"Files changed:  {counters['changed_files']}")
    print(f"Links updated:  {counters['total_links']}")

    # === Verification ===
    print()
    print(f"=== Verification (post-fix path resolution) ===")

    LINK_RESOLVE_RE = re.compile(r"\]\(((?:\.\./)+note/[^)\s]+)\)")
    broken = []
    total_check = 0
    for root, _, files in os.walk(TARGET_DIR):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            abs_f = os.path.join(root, fn)
            with open(abs_f, "r", encoding="utf-8") as fp:
                content = fp.read()
            for m in LINK_RESOLVE_RE.finditer(content):
                rel = m.group(1)
                target = os.path.normpath(os.path.join(os.path.dirname(abs_f), rel))
                target_fwd = target.replace(os.sep, "/")
                total_check += 1
                if not os.path.isfile(target_fwd):
                    broken.append((os.path.relpath(abs_f, PROJECT_ROOT), rel, target_fwd))

    print(f"Total cross-module links (post-fix): {total_check}")
    print(f"Broken (file not found): {len(broken)}")
    if broken:
        for b in broken:
            print(f"  BROKEN: {b[0]} -> {b[1]} (resolved: {b[2]})")
        sys.exit(1)
    else:
        print("PASS: All cross-module links resolve to existing files.")


if __name__ == "__main__":
    main()