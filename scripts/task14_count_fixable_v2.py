"""Task 14 - Count fixable broken links using rename map."""
import os, re, json

with open('scripts/task14_rename_map.json', 'r') as f:
    file_map = json.load(f)

# Build reverse map: target_filename -> list of possible old paths
target_to_old = {}
for old, new in file_map.items():
    target_to_old.setdefault(new, []).append(old)

LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
PLACEHOLDERS = ['x/README', 'xxx', '12.interview/', '13.story/']

# Also check if a file in note/ still exists (for 11.ai)
def file_exists(path):
    return os.path.isfile(path)


def fix_link(source_path, link):
    """Compute new relative path for a broken link.

    Returns: (new_link, exists_after, resolved_path)
    """
    source_path = source_path.replace('\\', '/')
    parts = link.split('/')
    while parts and parts[0] == '..':
        parts.pop(0)
    rest = '/'.join(parts)  # e.g., 'note/13.split-hairs/X.md'

    # Check if rest starts with note/X.Y.
    m = re.match(r'^note/(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if not m:
        return None, False, None
    old_mod = m.group(1)
    tail = m.group(2)
    old_path = f"note/{old_mod}{tail}"

    # Source dir
    src_parts = source_path.split('/')
    src_dir = '/'.join(src_parts[:-1])
    src_depth_from_temp = len(src_parts) - 2  # exclude 'note-temp/' and filename

    # Try to find target in rename map
    candidates = []
    if old_path in file_map:
        candidates.append(file_map[old_path])

    # Try src_dir-relative paths
    # From note-temp/<path>/file.md, to reach:
    # - note-temp/<new_module>/<tail>: use src_depth_from_temp dotdots + new_module + tail
    # - note/<old_module>/<tail>: use src_depth_from_temp + 1 dotdots + note/old_module + tail

    if candidates:
        # Use rename map: compute relative path from src_dir to candidate
        new_path = candidates[0]
        # src_dir is like 'note-temp/01.java-and-jvm/02-jvm'
        # new_path is like 'note-temp/12.interview/01.java/gc-algorithms/README.md'
        # We need: ../<N>/12.interview/01.java/gc-algorithms/README.md
        src_parts_list = src_dir.split('/')
        new_parts_list = new_path.split('/')
        # Find common prefix
        common = 0
        while (common < len(src_parts_list) and common < len(new_parts_list)
               and src_parts_list[common] == new_parts_list[common]):
            common += 1
        # dotdots = len(src_parts_list) - common
        up_count = len(src_parts_list) - common
        new_dotdots = '../' * up_count
        new_tail = '/'.join(new_parts_list[common:])
        new_link = new_dotdots + new_tail
        # Verify
        resolved = os.path.normpath(os.path.join(src_dir, new_link)).replace(os.sep, '/')
        return new_link, os.path.isfile(resolved), resolved
    else:
        # Not in rename map - check if still in note/ (e.g., 11.ai)
        if file_exists(old_path):
            # Need to add 1 .. to go from note-temp/ to repo root
            new_link = '../' * (src_depth_from_temp + 1) + old_path
            resolved = os.path.normpath(os.path.join(src_dir, new_link)).replace(os.sep, '/')
            return new_link, os.path.isfile(resolved), resolved
        return None, False, None


# Walk note-temp, find broken links, compute fixes
total = 0
fixable = 0
unfixable = []
unfixable_by_target = {}
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
                    # Compute the unresolved target for tracking
                    unfixable.append((path, target_rel, new_link))

print(f"Total broken: {total}")
print(f"Fixable: {fixable}")
print(f"Unfixable: {len(unfixable)}")
print(f"\nSample unfixable (first 30):")
for src, old, new in unfixable[:30]:
    print(f"  {src}")
    print(f"    OLD: {old}")
    print(f"    NEW: {new}")
