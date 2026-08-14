"""Analyze broken link patterns in target."""
import re
import os
import glob
from collections import Counter

TARGET_DIR = r'D:\developer\IdeaProjects\wb04307201\note-temp\12.interview'
PROJECT_ROOT = r'D:\developer\IdeaProjects\wb04307201'
LINK_RE = re.compile(r'\]\(((?:\.\./)+[^)\s]+)\)')

broken = []
total = 0
for root, _, files in os.walk(TARGET_DIR):
    for fn in files:
        if not fn.endswith('.md'):
            continue
        abs_f = os.path.join(root, fn)
        with open(abs_f, 'r', encoding='utf-8') as fp:
            content = fp.read()
        for m in LINK_RE.finditer(content):
            rel = m.group(1)
            total += 1
            target = os.path.normpath(os.path.join(os.path.dirname(abs_f), rel))
            if not os.path.exists(target):
                broken.append((os.path.relpath(abs_f, PROJECT_ROOT), rel, target))

print(f'Total broken: {len(broken)}')

target_patterns = Counter()
for b in broken:
    parts = b[2].replace('\\', '/').split('/')
    pattern = '/'.join(parts[3:6]) if len(parts) > 5 else '/'.join(parts)
    target_patterns[pattern] += 1

print('\nTop broken target patterns:')
for p, c in target_patterns.most_common(20):
    print(f'  {c}: {p}')

# Sample by category
print('\nSamples:')
for b in broken[:5]:
    print(f'  {b[0]} -> {b[1]} (resolved: {b[2]})')