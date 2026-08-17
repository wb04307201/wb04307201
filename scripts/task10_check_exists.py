"""Check broken links target patterns - simpler version."""
import re
import os
import glob
from collections import Counter

TARGET_DIR = r'D:\developer\IdeaProjects\wb04307201\note-temp\12.interview'
PROJECT_ROOT = r'D:\developer\IdeaProjects\wb04307201'
LINK_RE = re.compile(r'\]\(((?:\.\./)+[^)\s]+)\)')

broken = []
for root, _, files in os.walk(TARGET_DIR):
    for fn in files:
        if not fn.endswith('.md'):
            continue
        abs_f = os.path.join(root, fn)
        with open(abs_f, 'r', encoding='utf-8') as fp:
            content = fp.read()
        for m in LINK_RE.finditer(content):
            rel = m.group(1)
            target = os.path.normpath(os.path.join(os.path.dirname(abs_f), rel))
            if not os.path.exists(target):
                broken.append(target)

print(f'Total broken: {len(broken)}')

# Group by first 4 path components
patterns = Counter()
for t in broken:
    parts = t.replace('\\', '/').split('/')
    # Take parts after PROJECT_ROOT
    idx = parts.index('wb04307201') if 'wb04307201' in parts else 3
    key = '/'.join(parts[idx:idx+3]) if len(parts) > idx+2 else '/'.join(parts[idx:])
    patterns[key] += 1

print('\nTop patterns:')
for p, c in patterns.most_common(20):
    # Check if parent dir exists
    parent = os.path.dirname(p)
    print(f'  {c}: {p} (parent exists: {os.path.isdir(parent)})')