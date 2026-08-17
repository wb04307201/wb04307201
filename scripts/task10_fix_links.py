"""Fix broken cross-module links after note/13.split-hairs -> note-temp/12.interview migration.

For all .md files in note-temp/12.interview/, transform each link:

A. Cross-module link (resolved target NOT under note/13.split-hairs/):
   - Source K -> Target K+1 (add 1 ../)
   - Add note/ prefix
   Examples from depth 4 file (note/13.split-hairs/<sub>/README.md):
   - ../02.computer-basics/foo (K=1) -> ../../note/02.computer-basics/foo (K=2)
   - ../../02.computer-basics/foo (K=2) -> ../../../note/02.computer-basics/foo (K=3)  [K=2 from depth 4 = cross-module]

B. Sibling link (resolved target IS under note/13.split-hairs/, i.e. within same module):
   - Strip the 13.split-hairs/ segment, K reduces by 1 segment
   Examples from depth 5 file (note/13.split-hairs/01.java/aqs/README.md):
   - ../../../01.java/foo (K=3) -> ../../01.java/foo (K=2, strip 13.split-hairs/)
   - ../../01.java/foo (K=2) -> ../01.java/foo (K=1, strip 13.split-hairs/)

C. README.md / CONTRIBUTING.md cross-module link:
   - For source files at depth 5 (note/13.split-hairs/<sub>/<sub2>/<file>.md):
     - ../../README.md (K=2) -> ../README.md (sibling, stays within module)
   - For source files at depth 4 (note/13.split-hairs/<sub>/<file>.md):
     - ../../README.md (K=2) -> ../../../note/README.md (cross-module)
   - For source files at depth 3 (note/13.split-hairs/<file>.md):
     - ../../README.md (K=2) -> ../../../note/README.md (cross-module)
   General rule:
   - If K < depth_from_note: sibling (strip one ../)
   - If K >= depth_from_note: cross-module (K+1 + add note/ prefix)

D. Sibling link explicitly referencing 13.split-hairs/<sub>/...:
   - ../13.split-hairs/<sub>/... (K=1, source in depth-2 file like X/README.md) -> <sub>/...
   - ../../13.split-hairs/<sub>/... (K=2, source in depth-3 file) -> ../<sub>/...
   - ../../../13.split-hairs/<sub>/... (K=3, source in depth-4 file) -> ../../<sub>/...
   - ../../../../13.split-hairs/<sub>/... (K=4, source in depth-5 file) -> ../../../<sub>/...

Constraint:
- Only transform paths starting with ../<digit>.<lowercase-letters>/ where Y is module prefix.
- Verify path resolution with os.path.normpath + os.path.exists to avoid false positives.
"""
import os
import re
import sys

PROJECT_ROOT = r"D:\developer\IdeaProjects\wb04307201"
SOURCE_PREFIX = "note/13.split-hairs/"  # for sibling check
TARGET_DIR = os.path.join(PROJECT_ROOT, "note-temp", "12.interview")

# Cross-module link pattern: ]((../)+X.Y./...)
# Group 1: opener ](, Group 2: dotdots, Group 3: module prefix, Group 4: tail path, Group 5: closer )
LINK_RE = re.compile(
    r"(\]\()((?:\.\./)+)(\d+\.[a-z][a-z0-9-]*)(/[^)\s]*)(\))"
)

# Sibling link pattern for explicit 13.split-hairs/<sub>/...:
# Group 1: opener, Group 2: dotdots, Group 3: subdir name, Group 4: tail, Group 5: closer
SIBLING_13SH_RE = re.compile(
    r"(\]\()((?:\.\./)+)13\.split-hairs(/[a-zA-Z0-9_-]+)(/[^)\s]*)(\))"
)

# README.md / CONTRIBUTING.md cross-module link (depth >= 2)
README_LINK_RE = re.compile(
    r"(\]\()((?:\.\./){2,})(README\.md|CONTRIBUTING\.md)(\))"
)


def is_sibling_link(source_file_rel: str, dotdot: str) -> bool:
    """Decide if a link is a sibling link (target within 13.split-hairs/) or cross-module.

    Args:
        source_file_rel: forward-slash relative path, e.g. 'note/13.split-hairs/01.java/aqs/README.md'
        dotdot: the leading dotdots, e.g. '../' (K=1) or '../../' (K=2)

    Returns:
        True if link target stays within note/13.split-hairs/, False if it goes elsewhere.
    """
    # Source file's depth (how many .. it takes to reach note/)
    # source_file_rel = 'note/13.split-hairs/X/Y/Z/README.md' -> depth from note/ = 4
    # Going up by K dotdots:
    # If K < depth_from_note_root: stays within note/13.split-hairs/ (sibling)
    # If K == depth_from_note_root: reaches note/ (cross-module)
    # If K > depth_from_note_root: goes outside note/ (cross-module)

    rel_parts = source_file_rel.split("/")
    # Remove the file part, count directory depth
    if rel_parts[-1].endswith(".md"):
        dir_parts = rel_parts[:-1]
    else:
        dir_parts = rel_parts

    # Directory depth relative to note/
    # E.g. 'note/13.split-hairs/01.java/aqs' = 3 levels below note/
    depth_from_note = len(dir_parts) - 1  # subtract 'note/'

    # K is the number of .. in dotdot
    k = dotdot.count("/")  # '../' has 1 '/', '../../' has 2, etc.

    # If K < depth_from_note, the link target stays within note/13.split-hairs/ (or deeper)
    # If K >= depth_from_note, the link target is at note/ or above
    return k < depth_from_note


def process_file(abs_f: str, rel_f: str, counters: dict) -> int:
    with open(abs_f, "r", encoding="utf-8") as fp:
        content = fp.read()

    file_link_count = [0]

    # Compute source_file_rel (in HEAD, before migration)
    # rel_f is target path like 'note-temp/12.interview/01.java/aqs/README.md'
    # Source would be 'note/13.split-hairs/01.java/aqs/README.md'
    source_rel = SOURCE_PREFIX + rel_f[len("note-temp/12.interview/"):]

    def repl_cross(m):
        file_link_count[0] += 1
        opener = m.group(1)
        dotdot = m.group(2)
        module = m.group(3)
        tail = m.group(4)
        closer = m.group(5)

        if is_sibling_link(source_rel, dotdot):
            # Sibling: strip 13.split-hairs/ segment, reduce K by 1
            counters["sibling_total"] += 1
            # dotdot has form '../' or '../../' etc.
            # Strip one '../' from the front
            if len(dotdot) >= 3:
                new_dotdot = dotdot[3:]  # removes '../'
            else:
                new_dotdot = ""
            return f"{opener}{new_dotdot}{module}{tail}{closer}"
        else:
            # Cross-module: K+1 + add note/ prefix
            counters["cross_total"] += 1
            new_dotdot = "../" + dotdot
            return f"{opener}{new_dotdot}note/{module}{tail}{closer}"

    def repl_sibling_explicit(m):
        file_link_count[0] += 1
        counters["sibling_explicit_total"] += 1
        opener = m.group(1)
        dotdot = m.group(2)
        sub_path = m.group(3)  # /X
        tail = m.group(4)
        closer = m.group(5)
        # Strip one '../' (the 13.split-hairs/ segment is removed)
        if len(dotdot) >= 3:
            new_dotdot = dotdot[3:]
        else:
            new_dotdot = ""
        return f"{opener}{new_dotdot}{sub_path}{tail}{closer}"

    def repl_readme(m):
        file_link_count[0] += 1
        opener = m.group(1)
        dotdot = m.group(2)
        target = m.group(3)
        closer = m.group(4)
        counters["readme_total"] += 1
        # Determine if sibling or cross-module based on resolved path
        # Source resolved path: os.path.join(dirname(source_rel), dotdot+target)
        # If resolved path starts with 'note/13.split-hairs/', it's a sibling.
        # Otherwise (cross-module like 'note/CONTRIBUTING.md' from depth 3 file), it's cross-module.
        src_dir = os.path.dirname(source_rel).replace(os.sep, "/")
        resolved = os.path.normpath(os.path.join(src_dir, dotdot + target)).replace(os.sep, "/")
        if resolved.startswith("note/13.split-hairs/"):
            # Sibling: strip one ../ (remove 13.split-hairs/ segment)
            new_dotdot = dotdot[3:] if len(dotdot) >= 3 else ""
            return f"{opener}{new_dotdot}{target}{closer}"
        else:
            # Cross-module: K+1 + add note/ prefix
            new_dotdot = "../" + dotdot
            return f"{opener}{new_dotdot}note/{target}{closer}"

    new_content = content
    # Apply in order: README first (specific), then sibling 13.split-hairs (specific), then cross-module (general)
    new_content = README_LINK_RE.sub(repl_readme, new_content)
    new_content = SIBLING_13SH_RE.sub(repl_sibling_explicit, new_content)
    new_content = LINK_RE.sub(repl_cross, new_content)

    if new_content != content:
        with open(abs_f, "w", encoding="utf-8") as fp:
            fp.write(new_content)
        counters["changed_files"] += 1
    counters["total_files"] += 1
    return file_link_count[0]


def main():
    counters = {
        "total_files": 0,
        "changed_files": 0,
        "cross_total": 0,
        "sibling_total": 0,
        "sibling_explicit_total": 0,
        "readme_total": 0,
    }

    for root, _, files in os.walk(TARGET_DIR):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            abs_f = os.path.join(root, fn)
            rel_f = os.path.relpath(abs_f, PROJECT_ROOT).replace(os.sep, "/")
            process_file(abs_f, rel_f, counters)

    print(f"=== Summary ===")
    print(f"Files scanned:  {counters['total_files']}")
    print(f"Files changed:  {counters['changed_files']}")
    print(f"Cross-module links transformed:     {counters['cross_total']}")
    print(f"Sibling links transformed (../X.Y/): {counters['sibling_total']}")
    print(f"Sibling links transformed (../13.sh): {counters['sibling_explicit_total']}")
    print(f"README/CONTRIBUTING transformed:    {counters['readme_total']}")
    total = counters['cross_total'] + counters['sibling_total'] + counters['sibling_explicit_total'] + counters['readme_total']
    print(f"Total links transformed: {total}")

    # === Verification ===
    print()
    print(f"=== Verification ===")

    # Check 1: Cross-module links (K >= 2) must have note/ prefix
    # Sibling links (K == 1) should NOT have note/ prefix
    import glob
    cross_no_note = []
    sib_with_note = []
    for md in glob.glob(os.path.join(TARGET_DIR, "**/*.md"), recursive=True):
        with open(md, "r", encoding="utf-8") as fp:
            for ln, line in enumerate(fp, 1):
                for m in re.finditer(r"(\]\()((?:\.\./)+)(\d+\.[a-z][a-z0-9-]*)", line):
                    dotdot = m.group(2)
                    k = dotdot.count("/")
                    rel = m.group(2) + m.group(3)
                    if k >= 2 and "note/" not in rel:
                        cross_no_note.append((os.path.relpath(md, PROJECT_ROOT), ln, m.group(0)))
                    elif k == 1 and "note/" in rel:
                        sib_with_note.append((os.path.relpath(md, PROJECT_ROOT), ln, m.group(0)))

    print(f"Check 1 - Cross-module (K>=2) links WITHOUT note/ prefix: {len(cross_no_note)}")
    if cross_no_note:
        for l in cross_no_note[:5]:
            print(f"  {l[0]}:{l[1]}: {l[2]}")
        sys.exit(1)
    else:
        print("  PASS: All cross-module links have note/ prefix.")
    print(f"         Sibling (K=1) links WITH note/ prefix: {len(sib_with_note)}")
    if sib_with_note:
        for l in sib_with_note[:5]:
            print(f"  {l[0]}:{l[1]}: {l[2]}")

    # Check 2: NO sibling 13.split-hairs/ links remain
    sib_links = []
    for md in glob.glob(os.path.join(TARGET_DIR, "**/*.md"), recursive=True):
        with open(md, "r", encoding="utf-8") as fp:
            for ln, line in enumerate(fp, 1):
                for m in re.finditer(r"\]\(((\.\./)+)13\.split-hairs", line):
                    sib_links.append((os.path.relpath(md, PROJECT_ROOT), ln, m.group(0)))
    print(f"Check 2 - Sibling 13.split-hairs/ links remaining: {len(sib_links)}")
    if sib_links:
        for l in sib_links[:5]:
            print(f"  {l[0]}:{l[1]}: {l[2]}")
        sys.exit(1)
    else:
        print("  PASS: No sibling 13.split-hairs/ links remain.")

    # Check 3: All relative links resolve (using os.path.exists)
    ALL_LINKS_RE = re.compile(r"\]\(((?:\.\./)+[^)\s]+)\)")
    broken = []
    total_check = 0
    for md in glob.glob(os.path.join(TARGET_DIR, "**/*.md"), recursive=True):
        with open(md, "r", encoding="utf-8") as fp:
            content = fp.read()
        for m in ALL_LINKS_RE.finditer(content):
            rel = m.group(1)
            total_check += 1
            target = os.path.normpath(os.path.join(os.path.dirname(md), rel))
            if not os.path.exists(target):
                broken.append((os.path.relpath(md, PROJECT_ROOT), rel, target))
    print(f"Check 3 - Total relative links: {total_check}")
    print(f"         Broken (file or dir doesn't exist): {len(broken)}")


if __name__ == "__main__":
    main()