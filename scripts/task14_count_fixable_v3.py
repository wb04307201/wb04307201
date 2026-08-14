"""Task 14 v3 - Extended fix script to handle no-note/ prefix links."""
import os, re, json

with open('scripts/task14_rename_map.json', 'r') as f:
    file_map = json.load(f)

LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
PLACEHOLDERS = ['x/README', 'xxx', '12.interview/', '13.story/']

MODULE_MIGRATIONS = {
    "01.java": "01.java-and-jvm",
    "02.computer-basics": "02.cs-foundations",
    "03.database": "03.data-stack",
    "04.system-design": "06.distributed-systems",
    "05.frontend": "05.frontend",
    "06.spring": "04.spring-backend",
    "07.workflow": "07.devops-and-tools",
    "08.application-systems": "10.business-systems",
    "09.front-end": "05.frontend",
    "10.big-data": "03.data-stack",
    "12.story": "13.story",
    "13.split-hairs": "12.interview",
    "14.project-management": "11.product-and-pm",
}


def fix_link(source_path, link):
    """Compute new relative path for a broken link."""
    source_path = source_path.replace('\\', '/')
    parts = link.split('/')
    while parts and parts[0] == '..':
        parts.pop(0)
    rest = '/'.join(parts)

    src_parts = source_path.split('/')
    src_dir = '/'.join(src_parts[:-1])
    src_depth_from_temp = len(src_parts) - 2

    # Try patterns in order:
    # 1. note/X.Y./path (with note/ prefix)
    # 2. X.Y./path (without note/ prefix, was probably relative to note/)
    # 3. note-temp/X.Y./path (already in note-temp but pointing to wrong location)

    m_note = re.match(r'^note/(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    m_noprefix = re.match(r'^(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    m_temp = re.match(r'^note-temp/(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)

    target_old_path = None
    target_mod = None
    target_tail = None

    if m_note:
        target_old_path = f"note/{m_note.group(1)}{m_note.group(2)}"
        target_mod = m_note.group(1)
        target_tail = m_note.group(2)
    elif m_noprefix:
        target_old_path = f"note/{m_noprefix.group(1)}{m_noprefix.group(2)}"
        target_mod = m_noprefix.group(1)
        target_tail = m_noprefix.group(2)
    elif m_temp:
        # Link is already in note-temp but broken - check if file exists somewhere in note-temp
        target_mod = m_temp.group(1)
        target_tail = m_temp.group(2)
        # Try to find the target file in note-temp
        for f in os.listdir('note-temp'):
            if f.startswith(target_mod[:2]) or f == target_mod:
                # Look for files with matching suffix
                candidate_base = 'note-temp/' + f + target_tail
                if os.path.isfile(candidate_base):
                    # Found a candidate
                    src_parts_list = src_dir.split('/')
                    new_parts_list = candidate_base.split('/')
                    common = 0
                    while (common < len(src_parts_list) and common < len(new_parts_list)
                           and src_parts_list[common] == new_parts_list[common]):
                        common += 1
                    up_count = len(src_parts_list) - common
                    new_dotdots = '../' * up_count
                    new_tail = '/'.join(new_parts_list[common:])
                    new_link = new_dotdots + new_tail
                    resolved = os.path.normpath(os.path.join(src_dir, new_link)).replace(os.sep, '/')
                    return new_link, os.path.isfile(resolved), resolved
        return None, False, None
    else:
        return None, False, None

    # Now try to find the target in rename map
    if target_old_path in file_map:
        new_path = file_map[target_old_path]
        # Compute relative path from src_dir to new_path
        src_parts_list = src_dir.split('/')
        new_parts_list = new_path.split('/')
        common = 0
        while (common < len(src_parts_list) and common < len(new_parts_list)
               and src_parts_list[common] == new_parts_list[common]):
            common += 1
        up_count = len(src_parts_list) - common
        new_dotdots = '../' * up_count
        new_tail = '/'.join(new_parts_list[common:])
        new_link = new_dotdots + new_tail
        resolved = os.path.normpath(os.path.join(src_dir, new_link)).replace(os.sep, '/')
        return new_link, os.path.isfile(resolved), resolved

    # Target not in rename map. Check if still exists in note/ (e.g., 11.ai)
    if os.path.isfile(target_old_path):
        # Need to add 1 .. to go from note-temp/ to repo root
        new_link = '../' * (src_depth_from_temp + 1) + target_old_path
        resolved = os.path.normpath(os.path.join(src_dir, new_link)).replace(os.sep, '/')
        return new_link, os.path.isfile(resolved), resolved

    return None, False, None


# Walk note-temp, find broken links, compute fixes
total = 0
fixable = 0
unfixable = []
unfixable_examples = {}
for root, _, files in os.walk('note-temp'):
    for f in files:
        if not f.endswith('.md'):
            continue
        path = os.path.join(root, f).replace('\\', '/')
        try:
            c = open(path, encoding='utf-8', errors='ignore').read()
        except:
            continue
        for m in LINK_RE.finditer(c):
            target_rel = m.group(2).strip()
            if any(p in target_rel for p in PLACEHOLDERS):
                continue
            target_sep = target_rel.replace('/', os.sep)
            target_abs = os.path.normpath(os.path.join(os.path.dirname(path), target_sep))
            if not os.path.isfile(target_abs):
                total += 1
                new_link, exists, resolved = fix_link(path, target_rel)
                if new_link is None:
                    unfixable.append((path, target_rel, 'no_candidate'))
                elif exists:
                    fixable += 1
                else:
                    unfixable.append((path, target_rel, new_link))

print(f"Total broken: {total}")
print(f"Fixable: {fixable}")
print(f"Unfixable: {len(unfixable)}")
print(f"\nSample unfixable (first 30):")
for src, old, new in unfixable[:30]:
    print(f"  {src}")
    print(f"    OLD: {old}")
    print(f"    NEW: {new}")
