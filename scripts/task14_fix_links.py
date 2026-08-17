"""Task 14 - Fix broken links in note-temp using rename map.

Approach:
1. Build per-file rename map from git history (1017 renames)
2. For each broken link in note-temp:
   - Pattern 1: note/X.Y./path - check if X.Y./path exists in rename map
   - Pattern 2: X.Y./path (no note/ prefix) - try same lookup with implicit note/ prefix
   - Pattern 3: note-temp/X.Y./path - already in note-temp, may need sibling fix
3. Apply minimal regex substitution to fix links

This only rewrites file paths in markdown links.
"""
import os, re, json, sys

with open('scripts/task14_rename_map.json', 'r') as f:
    file_map = json.load(f)

# Build path component map: for any old path, what was the new path?
# We need to be able to compute "old_link -> new_link"

LINK_RE = re.compile(r'(\]\()((?:\.\./)+)([^)\s]+?\.md)((?:#[^)]*)?)(\))')
# Match ](.../X.md...) - capture group 1=opener, 2=dotdots, 3=path, 4=anchor, 5=closer


def compute_relative(src_dir, target_path):
    """Compute relative path from src_dir to target_path."""
    src_parts = src_dir.replace('\\', '/').split('/')
    tgt_parts = target_path.replace('\\', '/').split('/')
    common = 0
    while (common < len(src_parts) and common < len(tgt_parts)
           and src_parts[common] == tgt_parts[common]):
        common += 1
    up_count = len(src_parts) - common
    new_dotdots = '../' * up_count
    new_tail = '/'.join(tgt_parts[common:])
    return new_dotdots + new_tail


def fix_href(source_path, href):
    """Compute new href for a broken link.

    Returns (new_href, was_changed) tuple.
    """
    # Split anchor and query
    anchor = ''
    query = ''
    body = href
    if '#' in body:
        body, anchor = body.split('#', 1)
        anchor = '#' + anchor
    if '?' in body:
        body, query = body.split('?', 1)
        query = '?' + query

    # Strip leading ../
    parts = body.split('/')
    while parts and parts[0] == '..':
        parts.pop(0)
    rest = '/'.join(parts)

    src_dir = os.path.dirname(source_path).replace('\\', '/')
    src_parts = source_path.replace('\\', '/').split('/')
    src_depth_from_temp = len(src_parts) - 2  # exclude 'note-temp/' and filename

    # Pattern: note/X.Y./path
    m_note = re.match(r'^note/(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if m_note:
        old_path = f"note/{m_note.group(1)}{m_note.group(2)}"
        if old_path in file_map:
            new_path = file_map[old_path]
            new_body = compute_relative(src_dir, new_path)
            return new_body + query + anchor, True
        # Not in rename map - check if still exists in note/
        if os.path.isfile(old_path):
            new_body = '../' * (src_depth_from_temp + 1) + old_path
            return new_body + query + anchor, True
        return href, False

    # Pattern: X.Y./path (no note/ prefix - was originally relative to note/)
    m_noprefix = re.match(r'^(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if m_noprefix:
        old_path = f"note/{m_noprefix.group(1)}{m_noprefix.group(2)}"
        if old_path in file_map:
            new_path = file_map[old_path]
            new_body = compute_relative(src_dir, new_path)
            return new_body + query + anchor, True
        # Not in rename map - check if still exists in note/
        if os.path.isfile(old_path):
            new_body = '../' * (src_depth_from_temp + 1) + old_path
            return new_body + query + anchor, True
        return href, False

    # Pattern: note-temp/X.Y./path (broken intra-note-temp link)
    m_temp = re.match(r'^note-temp/(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if m_temp:
        mod = m_temp.group(1)
        tail = m_temp.group(2)
        # Try to find a matching module dir in note-temp
        for entry in os.listdir('note-temp'):
            if entry.startswith(mod[:2]) and entry.endswith(mod.split('.', 1)[1] if '.' in mod else mod):
                # Candidate module
                candidate_base = f"note-temp/{entry}{tail}"
                if os.path.isfile(candidate_base):
                    new_body = compute_relative(src_dir, candidate_base)
                    return new_body + query + anchor, True
        # Also try direct match
        candidate_base = f"note-temp/{mod}{tail}"
        if os.path.isfile(candidate_base):
            new_body = compute_relative(src_dir, candidate_base)
            return new_body + query + anchor, True
        return href, False

    return href, False


PLACEHOLDERS = ['x/README', 'xxx', '12.interview/', '13.story/']


def process_file(abs_f, counters):
    with open(abs_f, 'r', encoding='utf-8', errors='ignore') as fp:
        content = fp.read()

    file_changes = 0

    def repl(m):
        nonlocal file_changes
        opener, dotdots, href_body, anchor, closer = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        href = dotdots + href_body
        if any(p in href for p in PLACEHOLDERS):
            return m.group(0)
        # Skip URLs, mailtos
        if href_body.startswith(('http://', 'https://', 'mailto:')):
            return m.group(0)

        new_href, was_changed = fix_href(abs_f, href)
        if was_changed and new_href != href:
            file_changes += 1
            counters['changed_links'] += 1
            return opener + new_href + closer
        return m.group(0)

    new_content = LINK_RE.sub(repl, content)

    if new_content != content:
        with open(abs_f, 'w', encoding='utf-8') as fp:
            fp.write(new_content)
        counters['changed_files'] += 1
    counters['total_files'] += 1


def main():
    counters = {'total_files': 0, 'changed_files': 0, 'changed_links': 0}
    for root, _, files in os.walk('note-temp'):
        for fn in files:
            if not fn.endswith('.md'):
                continue
            abs_f = os.path.join(root, fn)
            process_file(abs_f, counters)

    print(f"=== Summary ===")
    print(f"Files scanned:  {counters['total_files']}")
    print(f"Files changed:  {counters['changed_files']}")
    print(f"Links fixed:    {counters['changed_links']}")


if __name__ == '__main__':
    main()
