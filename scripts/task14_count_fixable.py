"""Count how many broken links can be fixed with simple module rename."""
import os, re
from collections import Counter

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
    m = re.match(r'^note/(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if not m:
        return None
    old_mod = m.group(1)
    tail = m.group(2)
    src_parts = source_path.split('/')
    src_depth = len(src_parts) - 2
    new_dotdots = '../' * src_depth
    if old_mod in MODULE_MIGRATIONS:
        new_mod = MODULE_MIGRATIONS[old_mod]
        new_link = new_dotdots + new_mod + tail
    elif old_mod == '11.ai':
        new_dotdots = '../' * (src_depth + 1)
        new_link = new_dotdots + 'note/' + old_mod + tail
    else:
        return None
    src_dir = '/'.join(src_parts[:-1])
    resolved = os.path.normpath(os.path.join(src_dir, new_link)).replace(os.sep, '/')
    return new_link, os.path.isfile(resolved), resolved


# Iterate over all broken links
total = 0
fixable = 0
unfixable = Counter()
unfixable_examples = []
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
                result = fix_link(path, target_rel)
                if result is None:
                    continue
                new_link, exists, resolved = result
                if exists:
                    fixable += 1
                else:
                    # Extract old module
                    old_m = re.match(r'^(?:\.\./)*note/(\d+\.[a-z][a-z0-9-]*)', target_rel)
                    if old_m:
                        unfixable[old_m.group(1)] += 1
                        if len(unfixable_examples) < 30:
                            unfixable_examples.append((path, target_rel, new_link))

print(f"Total broken: {total}")
print(f"Fixable: {fixable}")
print(f"Unfixable: {total - fixable}")
print(f"\nUnfixable by old module:")
for mod, cnt in unfixable.most_common():
    print(f"  {mod}: {cnt}")
print(f"\nSample unfixable (showing missing internal rename):")
for src, old, new in unfixable_examples[:20]:
    print(f"  {src}")
    print(f"    OLD: {old}")
    print(f"    NEW: {new}")
