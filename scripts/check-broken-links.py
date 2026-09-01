#!/usr/bin/env python3
"""
check-broken-links.py — note/ 链接完整性回归测试

Session 6 (2026-09-02) 创建：230 处断链批量修复后，
建立回归测试确保未来新增/修改不产生断链。

特性：
- 双口径扫描（.md 链接 + ](dir/) 目录链接）
- 支持单文件扫描（commit 前自检）和全库扫描（CI 月度检查）
- 退出码：0=通过 / 1=有断链（CI 友好）

用法：
  python scripts/check-broken-links.py                    # 全库扫描
  python scripts/check-broken-links.py file1.md file2.md  # 单文件扫描
  python scripts/check-broken-links.py --module 09.ai-applications  # 单模块
"""
import os
import re
import sys
import glob
import argparse

# Windows UTF-8 输出兼容
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 链接正则（与 Phase 1.6 一致）
LINK_FILE = re.compile(
    r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)'
)
LINK_DIR = re.compile(
    r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?)/\)'
)


def is_excluded(f: str) -> bool:
    """跳过临时目录与 .git"""
    parts = f.replace(os.sep, '/').split('/')
    return any(x in parts for x in ['.health-tmp', '.obsidian', 'target', '.git'])


def normalize_link_target(file_path: str, link_path: str) -> str:
    """把相对链接解析为绝对路径"""
    if link_path.startswith(('/', '\\')):
        return os.path.normpath(os.path.join('note', link_path.lstrip('/\\')))
    return os.path.normpath(os.path.join(os.path.dirname(file_path), link_path.replace('/', os.sep)))


def scan_file(file_path: str):
    """扫描单个文件，返回 (file_broken, dir_broken) 列表"""
    file_broken = []
    dir_broken = []
    try:
        content = open(file_path, encoding='utf-8', errors='ignore').read()
    except Exception as e:
        print(f'  ⚠ 无法读取 {file_path}: {e}')
        return file_broken, dir_broken

    for m in LINK_FILE.finditer(content):
        target = normalize_link_target(file_path, m.group(2))
        if not os.path.isfile(target):
            file_broken.append((file_path, m.group(2)))

    for m in LINK_DIR.finditer(content):
        target = normalize_link_target(file_path, m.group(2))
        if not (os.path.isdir(target) and os.path.isfile(os.path.join(target, 'README.md'))):
            dir_broken.append((file_path, m.group(2) + '/'))

    return file_broken, dir_broken


def scan_files(files, verbose=False):
    """扫描多个文件，输出报告并返回断链数"""
    file_broken = []
    dir_broken = []
    for f in files:
        fb, db = scan_file(f)
        file_broken.extend(fb)
        dir_broken.extend(db)

    total = len(file_broken) + len(dir_broken)
    if verbose or total > 0:
        print(f'扫描文件数: {len(files)}')
        print(f'.md 断链: {len(file_broken)}')
        print(f'目录断链: {len(dir_broken)}')
        print(f'总计: {total}')
        if file_broken:
            print('\n== .md 断链 ==')
            for src, tgt in file_broken[:30]:
                print(f'  ❌ {src}')
                print(f'      → {tgt}')
            if len(file_broken) > 30:
                print(f'  ... 还有 {len(file_broken)-30} 处')
        if dir_broken:
            print('\n== 目录断链 ==')
            for src, tgt in dir_broken[:30]:
                print(f'  ❌ {src}')
                print(f'      → {tgt}')
            if len(dir_broken) > 30:
                print(f'  ... 还有 {len(dir_broken)-30} 处')
    return total


def main():
    parser = argparse.ArgumentParser(description='note/ 链接完整性回归测试')
    parser.add_argument('files', nargs='*', help='指定文件（留空 = 全库扫描）')
    parser.add_argument('--module', help='单模块扫描（如 09.ai-applications）')
    parser.add_argument('--quiet', action='store_true', help='仅输出断链数与退出码（CI 友好）')
    args = parser.parse_args()

    if args.files:
        # 单文件模式：用户传入的具体文件
        targets = args.files
        for f in targets:
            if not os.path.isfile(f):
                print(f'❌ 文件不存在: {f}')
                sys.exit(2)
        total = scan_files(targets, verbose=not args.quiet)
    elif args.module:
        # 单模块模式：扫描模块下所有 .md
        targets = [
            f for f in glob.glob(f'note/{args.module}/**/*.md', recursive=True)
            if not is_excluded(f)
        ]
        if not targets:
            print(f'❌ 模块 {args.module} 未找到任何 .md')
            sys.exit(2)
        total = scan_files(targets, verbose=not args.quiet)
    else:
        # 全库扫描
        targets = [
            f for f in glob.glob('note/**/*.md', recursive=True)
            if not is_excluded(f)
        ]
        total = scan_files(targets, verbose=not args.quiet)

    if total == 0:
        if not args.quiet:
            print('\n✅ 全部链接有效')
        sys.exit(0)
    else:
        if not args.quiet:
            print(f'\n❌ 发现 {total} 处断链，请修复后重试')
        sys.exit(1)


if __name__ == '__main__':
    main()