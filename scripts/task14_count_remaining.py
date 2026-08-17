"""Task 14 v4 - Add module README mappings to handle missing entries."""
import os, re, json, sys

with open('scripts/task14_rename_map.json', 'r') as f:
    file_map = json.load(f)

# Add module-level README mappings (for files where git didn't detect rename)
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

LINK_RE = re.compile(r'(\]\()((?:\.\./)+)([^)\s]+?\.md)((?:#[^)]*)?)(\))')


def compute_relative(src_dir, target_path):
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
    anchor = ''
    query = ''
    body = href
    if '#' in body:
        body, anchor = body.split('#', 1)
        anchor = '#' + anchor
    if '?' in body:
        body, query = body.split('?', 1)
        query = '?' + query

    parts = body.split('/')
    while parts and parts[0] == '..':
        parts.pop(0)
    rest = '/'.join(parts)

    src_dir = os.path.dirname(source_path).replace('\\', '/')
    src_parts = source_path.replace('\\', '/').split('/')
    src_depth_from_temp = len(src_parts) - 2

    # Pattern: note/X.Y./path
    m_note = re.match(r'^note/(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if m_note:
        old_path = f"note/{m_note.group(1)}{m_note.group(2)}"
        if old_path in file_map:
            new_path = file_map[old_path]
            new_body = compute_relative(src_dir, new_path)
            return new_body + query + anchor, True
        if os.path.isfile(old_path):
            new_body = '../' * (src_depth_from_temp + 1) + old_path
            return new_body + query + anchor, True
        return href, False

    m_noprefix = re.match(r'^(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if m_noprefix:
        old_path = f"note/{m_noprefix.group(1)}{m_noprefix.group(2)}"
        if old_path in file_map:
            new_path = file_map[old_path]
            new_body = compute_relative(src_dir, new_path)
            return new_body + query + anchor, True
        if os.path.isfile(old_path):
            new_body = '../' * (src_depth_from_temp + 1) + old_path
            return new_body + query + anchor, True
        return href, False

    m_temp = re.match(r'^note-temp/(\d+\.[a-z][a-z0-9-]*)(/.*)$', rest)
    if m_temp:
        mod = m_temp.group(1)
        tail = m_temp.group(2)
        # Try to find a matching module dir in note-temp
        for entry in os.listdir('note-temp'):
            if entry.startswith(mod[:2]) and entry.endswith(mod.split('.', 1)[1] if '.' in mod else mod):
                candidate_base = f"note-temp/{entry}{tail}"
                if os.path.isfile(candidate_base):
                    new_body = compute_relative(src_dir, candidate_base)
                    return new_body + query + anchor, True
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
