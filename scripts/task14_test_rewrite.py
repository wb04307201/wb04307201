"""Test link rewrite logic for Task 14."""
import os, re

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

sample = [
    ('note-temp/01.java-and-jvm/02-jvm/tuning.md', '../../../note/13.split-hairs/01.java/gc-algorithms/README.md'),
    ('note-temp/01.java-and-jvm/01-language/spi/README.md', '../../../note/06.spring/04-spring-boot/spring-factories-migration.md'),
    ('note-temp/01.java-and-jvm/02-jvm/tuning.md', '../../../note/11.ai/01-fundamentals/dense-vs-moe/README.md'),
    ('note-temp/01.java-and-jvm/01-language/polymorphism/README.md', '../../../../note/13.split-hairs/01.java/polymorphism/README.md'),
    ('note-temp/01.java-and-jvm/01-language/exception/README.md', '../../../../note/12.story/README.md'),
    ('note-temp/04.spring-backend/02-boot/spring-factories-migration.md', '../../../note/01.java/concurrency/thread-pool/README.md'),
    ('note-temp/13.story/01-prequel/01-cs-student-days.md', '../../note/13.split-hairs/01.java/thread-sequential-execution/README.md'),
]


def fix_link(source_path, link):
    """Compute new relative path for a broken link."""
    # Convert Windows-style backslashes
    source_path = source_path.replace('\\', '/')
    parts = link.split('/')
    dotdot_count = 0
    while parts and parts[0] == '..':
        dotdot_count += 1
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
    exists = os.path.isfile(resolved)
    return new_link, exists, resolved


for src, link in sample:
    result = fix_link(src, link)
    if result is None:
        print(f"{src} : {link}")
        print(f"  -> None")
    else:
        new_link, exists, resolved = result
        status = "EXISTS" if exists else "MISSING"
        print(f"{src} : {link}")
        print(f"  -> {new_link}")
        print(f"  -> {resolved} [{status}]")
    print()
