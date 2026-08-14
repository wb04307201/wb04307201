"""Find fixable but unresolved links."""
import os, re, json

with open('scripts/task14_rename_map.json', 'r') as f:
    file_map = json.load(f)

MODULE_README_MAP = {
    "note/02.computer-basics/README.md": "note-temp/02.cs-foundations/README.md",
    "note/04.system-design/README.md": "note-temp/06.distributed-systems/README.md",
    "note/06.spring/README.md": "note-temp/04.spring-backend/README.md",
    "note/07.workflow/README.md": "note-temp/07.devops-and-tools/02-workflow/README.md",
    "note/05.tools/README.md": "note-temp/07.devops-and-tools/01-tools/README.md",
    "note/08.application-systems/README.md": "note-temp/10.business-systems/README.md",
    "note/12.story/README.md": "note-temp/13.story/README.md",
    "note/13.split-hairs/README.md": "note-temp/12.interview/README.md",
}
file_map.update(MODULE_README_MAP)

LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
PLACEHOLDERS = ['x/README', 'xxx', '12.interview/', '13.story/']


def compute_relative(src_dir, target_path):
    src_parts = src_dir.replace(os.sep, '/').split('/')
    tgt_parts = target_path.replace(os.sep, '/').split('/')
    common = 0
    while (common < len(src_parts) and common < len(tgt_parts)
           and src_parts[common] == tgt_parts[common]):
        common += 1
    up_count = len(src_parts) - common
    return '../' * up_count + '/'.join(tgt_parts[common:])


def fix_href(source_path, href):
    parts = href.split('/')
    while parts and parts[0] == '..':
        parts.pop(0)
    rest = '/'.join(parts)
    src_dir = os.path.dirname(source_path).replace(os.sep, '/')
    src_parts = source_path.replace(os.sep, '/').split('/')
    src_depth_from_temp = len(src_parts) - 2

    m_note = re.match(r'^note/(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if m_note:
        old_path = f"note/{m_note.group(1)}{m_note.group(2)}"
        if old_path in file_map:
            new_path = file_map[old_path]
            return compute_relative(src_dir, new_path), os.path.isfile(new_path)
        if os.path.isfile(old_path):
            return '../' * (src_depth_from_temp + 1) + old_path, True
        return None, False

    m_noprefix = re.match(r'^(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if m_noprefix:
        old_path = f"note/{m_noprefix.group(1)}{m_noprefix.group(2)}"
        if old_path in file_map:
            new_path = file_map[old_path]
            return compute_relative(src_dir, new_path), os.path.isfile(new_path)
        if os.path.isfile(old_path):
            return '../' * (src_depth_from_temp + 1) + old_path, True
        return None, False

    m_temp = re.match(r'^note-temp/(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if m_temp:
        mod = m_temp.group(1)
        tail = m_temp.group(2)
        for entry in os.listdir('note-temp'):
            if entry.startswith(mod[:2]) and entry.endswith(mod.split('.', 1)[1] if '.' in mod else mod):
                candidate_base = f"note-temp/{entry}{tail}"
                if os.path.isfile(candidate_base):
                    return compute_relative(src_dir, candidate_base), True
        candidate_base = f"note-temp/{mod}{tail}"
        if os.path.isfile(candidate_base):
            return compute_relative(src_dir, candidate_base), True
        return None, False
    return None, False


# Find fixable but unresolved
count_resolves = 0
count_missing = 0
for root, _, files in os.walk('note-temp'):
    for f in files:
        if not f.endswith('.md'):
            continue
        path = os.path.join(root, f).replace(os.sep, '/')
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
                new_link, exists = fix_href(path, target_rel)
                if new_link is not None and exists:
                    count_resolves += 1
                    print(f"RESOLVES: {path}")
                    print(f"  OLD: {target_rel}")
                    print(f"  NEW: {new_link}")
                elif new_link is not None:
                    count_missing += 1
                    print(f"MISSING: {path}")
                    print(f"  OLD: {target_rel}")
                    print(f"  NEW: {new_link}")

print(f"\nResolves: {count_resolves}, Missing: {count_missing}")
