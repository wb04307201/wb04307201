"""
auto-calibrate.py
自动应用 5-dim 评分偏差 ≥ 1 的 depth 校准。

输入：v{n} 抽样报告（Markdown）
输出：应用所有偏差 ≥1 校准 + 生成 commit message + 更新 README depth 表

用法：
  python scripts/auto-calibrate.py --report skills/note-health/references/v6-sampling-report.md
  python scripts/auto-calibrate.py --report v5 --threshold 2  # 仅应用偏差 ≥2
  python scripts/auto-calibrate.py --report v6 --dry-run       # 试运行不写入
"""
import os, re, sys, json, argparse
from collections import defaultdict
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

# depth 映射
L_TO_STARS = {
    'L1': '⭐', 'L2': '⭐⭐', 'L3': '⭐⭐⭐',
    'L4': '⭐⭐⭐⭐', 'L5': '⭐⭐⭐⭐⭐',
}
STARS_TO_L = {v: k for k, v in L_TO_STARS.items()}

def parse_report(path):
    """解析 v{n} 报告 Markdown，提取偏差清单"""
    if not os.path.exists(path):
        print(f'❌ Report not found: {path}')
        sys.exit(1)

    with open(path, encoding='utf-8') as f:
        content = f.read()

    deviations = []
    # 解析表格：| # | 文件 | 当前 | 5-dim | 建议 | 偏差 |
    for line in content.split('\n'):
        if not line.startswith('|') or '|' not in line[1:]:
            continue
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) < 6 or parts[0].startswith('#'):
            continue
        try:
            # 跳过表头分隔行
            if '---' in parts[2] or '---' in parts[1]:
                continue
            file_path = parts[1]
            current = parts[2].strip()
            suggestion = parts[4].strip()
            deviation = parts[5].strip()

            # 跳过 OK（✓）和无偏差行
            if deviation == '✓' or deviation == '0':
                continue
            # 解析偏差数值
            m = re.search(r'[-+]?(\d+)', deviation)
            if not m:
                continue
            dev_num = int(m.group(1))
            deviations.append({
                'file': file_path,
                'current': current,
                'suggestion': suggestion,
                'deviation': dev_num,
            })
        except (ValueError, IndexError):
            continue

    return deviations

def update_depth(file_path, new_depth):
    """更新文件 frontmatter 的 depth 字段"""
    if not os.path.exists(file_path):
        print(f'❌ Not found: {file_path}')
        return False

    try:
        c = open(file_path, encoding='utf-8', errors='ignore').read()
    except:
        return False

    # 替换现有 depth 字段
    new_c = re.sub(
        r'^\s*depth:\s*[⭐★]+.*$',
        f'  depth: {new_depth}',
        c,
        count=1,
        flags=re.MULTILINE,
    )

    if new_c == c:
        # 没有 depth 字段，插入到 module: 块末尾
        m = re.search(r'(<!--\s*\nmodule:.*?\n)(-->)', c, re.DOTALL)
        if not m:
            m = re.search(r'(<!--\s*module:.*?\n)(-->)', c, re.DOTALL)
        if not m:
            print(f'❌ No module frontmatter: {file_path}')
            return False
        frontmatter = m.group(1)
        closing = m.group(2)
        new_frontmatter = frontmatter.rstrip('\n') + f'\n  depth: {new_depth}\n'
        new_c = c.replace(frontmatter + closing, new_frontmatter + closing, 1)

    open(file_path, 'w', encoding='utf-8').write(new_c)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', required=True, help='Path to v{n} report or just v{n}')
    parser.add_argument('--threshold', type=int, default=1, help='最小偏差阈值（默认 1）')
    parser.add_argument('--dry-run', action='store_true', help='试运行不写入')
    args = parser.parse_args()

    # 支持 "v5" 简写
    report_path = args.report
    if not os.path.exists(report_path):
        # 尝试 v{n}-sampling-report.md 格式
        for cand in [
            f'skills/note-health/references/{report_path}-sampling-report.md',
            f'note/.health-tmp/{report_path}-sampling-report.md',
        ]:
            if os.path.exists(cand):
                report_path = cand
                break

    print(f'Report: {report_path}')
    print(f'Threshold: |偏差| ≥ {args.threshold}')
    print(f'Dry run: {args.dry_run}')
    print()

    deviations = parse_report(report_path)
    print(f'找到 {len(deviations)} 条偏差记录')
    print()

    applied = []
    skipped = []
    failed = []

    for dev in deviations:
        if abs(dev['deviation']) < args.threshold:
            skipped.append(dev)
            continue

        new_stars = dev['suggestion']
        if not new_stars.startswith('⭐'):
            print(f'⚠ 跳过 {dev["file"]}: 建议值非 ⭐ ({new_stars})')
            failed.append(dev)
            continue

        print(f'  {dev["file"]}: {dev["current"]} → {new_stars} (偏差 {dev["deviation"]})')

        if args.dry_run:
            continue

        if update_depth(dev['file'], new_stars):
            applied.append(dev)
        else:
            failed.append(dev)

    print()
    print('=' * 50)
    print(f'应用: {len(applied)}')
    print(f'跳过（偏差 < {args.threshold}）: {len(skipped)}')
    print(f'失败: {len(failed)}')

    if not args.dry_run and applied:
        print()
        print('建议 commit message:')
        print(f'fix(depth): 自动校准 {len(applied)} 篇（基于 {report_path}）')
        print()
        for dev in applied:
            print(f'  - {dev["file"]}: {dev["current"]} → {dev["suggestion"]}')

if __name__ == '__main__':
    main()
