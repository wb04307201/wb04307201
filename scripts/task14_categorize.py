"""Categorize remaining broken links."""
import os, re
from collections import Counter

LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
PLACEHOLDERS = ['x/README', 'xxx', '12.interview/', '13.story/']

cats = Counter()
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
                # Categorize
                if 'note/' in target_rel and any(x in target_rel for x in ['01.java/', '02.computer-basics/', '03.database/', '04.system-design/', '05.frontend/', '06.spring/', '07.workflow/', '08.application-systems/', '09.front-end/', '10.big-data/', '12.story/', '13.split-hairs/', '14.project-management/']):
                    cats['old_module_in_note'] += 1
                elif target_rel.startswith('../'):
                    cats['relative_no_dotdots'] += 1
                elif 'note-temp/' in target_rel:
                    cats['note-temp_internal'] += 1
                elif 'note/11.ai/' in target_rel:
                    cats['11.ai_in_note'] += 1
                elif 'note/01.java/' in target_rel:
                    cats['01.java_legacy_path'] += 1
                else:
                    cats['other'] += 1

for cat, cnt in cats.most_common():
    print(f'  {cat}: {cnt}')
