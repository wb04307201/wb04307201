"""Fix broken cross-module links after note/12.story -> note-temp/13.story migration.

Source structure: note/12.story/X.md (flat, depth-from-note = 2)
Target structure: note-temp/13.story/X.md (flat, depth-from-note-temp = 2)

For each link, transform based on resolution:

A. Cross-module link (target NOT under 12.story/, e.g. ../11.ai/, ../04.system-design/):
   - Add 1 ../ (K+1)
   - Add note/ prefix (since source resolution went to note/, target needs ../note/)
   Source resolution: note/12.story/X.md + ../11.ai/foo -> note/11.ai/foo (works)
   Target resolution: note-temp/13.story/X.md + ../11.ai/foo -> note-temp/11.ai/foo (broken)
   Fix:          note-temp/13.story/X.md + ../../note/11.ai/foo -> note/11.ai/foo (works)

B. README.md cross-module (../README.md):
   - Same as A: ../README.md -> ../../note/README.md
   Source: note/12.story/X.md + ../README.md -> note/README.md (works)
   Target: note-temp/13.story/X.md + ../README.md -> note-temp/README.md (we want note/README.md)
   Fix:    note-temp/13.story/X.md + ../../note/README.md -> note/README.md (works)

C. Sibling link (../12.story/Y.md, explicit):
   - Strip the ../12.story/ segment (since target has flat structure, Y.md is sibling)
   Source: note/12.story/X.md + ../12.story/Y.md -> note/12.story/Y.md (works)
   Target: note-temp/13.story/X.md + ../12.story/Y.md -> note-temp/12.story/Y.md (broken)
   Fix:    note-temp/13.story/X.md + ./Y.md -> note-temp/13.story/Y.md (works)

D. Pre-existing broken ../13.split-hairs/... links (Task 10 moved 13.split-hairs -> note-temp/12.interview):
   - These were broken in source (13.split-hairs already moved by Task 10).
   - Update to point to new location: ../../note-temp/12.interview/...
   - This is a bonus fix that reduces overall broken count.
   Source: note/12.story/X.md + ../13.split-hairs/Y.md -> note/13.split-hairs/Y.md (broken since Task 10)
   Target: note-temp/13.story/X.md + ../13.split-hairs/Y.md -> note-temp/13.split-hairs/Y.md (broken)
   Fix:    note-temp/13.story/X.md + ../../note-temp/12.interview/Y.md -> note-temp/12.interview/Y.md (works)

Patterns preserved (NO change):
- ./Y.md (already sibling in 12.story, target keeps sibling structure)
"""
import os
import re
import sys

PROJECT_ROOT = r"D:\developer\IdeaProjects\wb04307201"
TARGET_DIR = os.path.join(PROJECT_ROOT, "note-temp", "13.story")

# Cross-module link pattern: ]((../)+X.Y./...)
# Group 1: opener ](, Group 2: dotdots, Group 3: module prefix, Group 4: tail path, Group 5: closer )
LINK_RE = re.compile(
    r"(\]\()((?:\.\./)+)(\d+\.[a-z][a-z0-9-]*)(/[^)\s]*)(\))"
)

# Sibling link pattern for explicit 12.story/<sub>/... (sibling within module):
# Group 1: opener, Group 2: dotdots, Group 3: sub_path, Group 4: tail, Group 5: closer
SIBLING_12STORY_RE = re.compile(
    r"(\]\()((?:\.\./)+)12\.story(/[a-zA-Z0-9_-][^)\s]*)(\))"
)

# Pre-existing broken 13.split-hairs link (update to note-temp/12.interview):
# Group 1: opener, Group 2: dotdots, Group 3: tail, Group 4: closer
SIBLING_13SH_RE = re.compile(
    r"(\]\()((?:\.\./)+)13\.split-hairs(/[^)\s]*)(\))"
)

# README.md / CONTRIBUTING.md cross-module link (depth >= 2)
README_LINK_RE = re.compile(
    r"(\]\()((?:\.\./){2,})(README\.md|CONTRIBUTING\.md)(\))"
)


def process_file(abs_f: str, rel_f: str, counters: dict) -> int:
    with open(abs_f, "r", encoding="utf-8") as fp:
        content = fp.read()

    file_link_count = [0]

    def repl_cross(m):
        file_link_count[0] += 1
        opener = m.group(1)
        dotdot = m.group(2)
        module = m.group(3)
        tail = m.group(4)
        closer = m.group(5)

        # Cross-module: K+1 + add note/ prefix
        counters["cross_total"] += 1
        new_dotdot = "../" + dotdot
        return f"{opener}{new_dotdot}note/{module}{tail}{closer}"

    def repl_sibling_12story(m):
        file_link_count[0] += 1
        counters["sibling_12story_total"] += 1
        opener = m.group(1)
        dotdot = m.group(2)
        tail = m.group(3)  # /Y
        closer = m.group(4)
        # Strip one '../' (the 12.story/ segment is removed, tail remains)
        if len(dotdot) >= 3:
            new_dotdot = dotdot[3:]
        else:
            new_dotdot = ""
        return f"{opener}{new_dotdot}{tail}{closer}"

    def repl_13sh(m):
        file_link_count[0] += 1
        counters["13sh_total"] += 1
        opener = m.group(1)
        dotdot = m.group(2)
        tail = m.group(3)
        closer = m.group(4)
        # Update: ../13.split-hairs/... -> ../../note-temp/12.interview/...
        new_dotdot = "../" + dotdot
        return f"{opener}{new_dotdot}note-temp/12.interview{tail}{closer}"

    def repl_readme(m):
        file_link_count[0] += 1
        opener = m.group(1)
        dotdot = m.group(2)
        target = m.group(3)
        closer = m.group(4)
        counters["readme_total"] += 1
        # Cross-module: K+1 + add note/ prefix
        new_dotdot = "../" + dotdot
        return f"{opener}{new_dotdot}note/{target}{closer}"

    new_content = content
    # Apply in order: README first (specific), then 13.sh (specific), then 12.story (specific), then cross-module (general)
    new_content = README_LINK_RE.sub(repl_readme, new_content)
    new_content = SIBLING_13SH_RE.sub(repl_13sh, new_content)
    new_content = SIBLING_12STORY_RE.sub(repl_sibling_12story, new_content)
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
        "sibling_12story_total": 0,
        "13sh_total": 0,
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
    print(f"Cross-module links transformed (../X.Y./ -> ../../note/X.Y./): {counters['cross_total']}")
    print(f"Sibling 12.story links transformed (../12.story/ -> ./):       {counters['sibling_12story_total']}")
    print(f"13.split-hairs links transformed (../13.split-hairs/ -> ../../note-temp/12.interview/): {counters['13sh_total']}")
    print(f"README/CONTRIBUTING transformed:                                  {counters['readme_total']}")
    total = counters["cross_total"] + counters["sibling_12story_total"] + counters["13sh_total"] + counters["readme_total"]
    print(f"Total links transformed: {total}")

    # === Verification ===
    print()
    print(f"=== Verification ===")

    import glob
    # Check 1: Cross-module links (../X.Y./) must have note/ prefix (i.e., ../../note/X.Y./)
    no_note_links = []
    for md in glob.glob(os.path.join(TARGET_DIR, "**/*.md"), recursive=True):
        with open(md, "r", encoding="utf-8") as fp:
            for ln, line in enumerate(fp, 1):
                # Find ../X.Y. patterns (not starting with ../../note/)
                for m in re.finditer(r"(\]\()((?:\.\./)+)(\d+\.[a-z][a-z0-9-]*)", line):
                    rel = m.group(2) + m.group(3)
                    if "note/" not in rel:
                        no_note_links.append((os.path.relpath(md, PROJECT_ROOT), ln, m.group(0)))

    print(f"Check 1 - Cross-module links WITHOUT note/ prefix: {len(no_note_links)}")
    if no_note_links:
        for l in no_note_links[:10]:
            print(f"  {l[0]}:{l[1]}: {l[2]}")
        sys.exit(1)
    else:
        print("  PASS: All cross-module links have note/ prefix.")

    # Check 2: NO ../12.story/ links remain (should be stripped to ./Y.md)
    sib_12st_links = []
    for md in glob.glob(os.path.join(TARGET_DIR, "**/*.md"), recursive=True):
        with open(md, "r", encoding="utf-8") as fp:
            for ln, line in enumerate(fp, 1):
                for m in re.finditer(r"\]\(((\.\./)+)12\.story", line):
                    sib_12st_links.append((os.path.relpath(md, PROJECT_ROOT), ln, m.group(0)))
    print(f"Check 2 - ../12.story/ links remaining: {len(sib_12st_links)}")
    if sib_12st_links:
        for l in sib_12st_links[:10]:
            print(f"  {l[0]}:{l[1]}: {l[2]}")
        sys.exit(1)
    else:
        print("  PASS: No ../12.story/ links remain.")

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
    if broken:
        print(f"  (Note: these may be pre-existing broken in source)")


if __name__ == "__main__":
    main()