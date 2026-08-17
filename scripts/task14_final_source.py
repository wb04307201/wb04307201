"""Final source-side broken links count (excluding README.md and SPEC.md)."""
import os, re

LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
total = 0
broken_to_temp = 0
broken_examples_to_temp = []
excluded_files = ['note/README.md', 'note/CONTRIBUTING.md']
for root, _, files in os.walk('note'):
    for f in files:
        if not f.endswith('.md'):
            continue
        path = os.path.join(root, f)
        rel_path = path.replace(os.sep, '/')
        if rel_path in excluded_files:
            continue
        try:
            c = open(path, encoding='utf-8', errors='ignore').read()
        except:
            continue
        for m in LINK_RE.finditer(c):
            target_rel = m.group(2).strip()
            target_sep = target_rel.replace('/', os.sep)
            target_abs = os.path.normpath(os.path.join(os.path.dirname(path), target_sep))
            if not os.path.isfile(target_abs):
                total += 1
                if 'note-temp' in target_abs:
                    broken_to_temp += 1
                    broken_examples_to_temp.append((rel_path, target_rel, target_abs))

print(f'Total broken in note/ (excluding README/CONTRIBUTING): {total}')
print(f'Broken pointing to note-temp/: {broken_to_temp}')
for p, rel, abs_p in broken_examples_to_temp[:20]:
    print(f'  {p} -> {rel}')
