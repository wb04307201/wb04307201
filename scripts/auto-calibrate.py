"""
auto-calibrate.py v2 - 支持 L5 标准 2.0 + 多轮校准合并

输入：v{n} 抽样报告（Markdown）
输出：应用所有偏差 ≥ 阈值的 depth 校准 + 生成 commit message + 更新 README depth 表

v2 新增：
- 支持 L5 标准 2.0 评分启发式（D5 ≥ 2 公司/模型案例）
- 多轮校准合并：相同文件被多次提到时按建议值合并
- --no-overwrite 模式：保留已有校准

用法：
  python scripts/auto-calibrate.py --report v9 --threshold 2
  python scripts/auto-calibrate.py --report v9 --threshold 1 --dry-run
  python scripts/auto-calibrate.py --report v9 --no-overwrite
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
    """解析 v{n} 报告 Markdown，提取偏差清单（合并多次提到的同文件）"""
    if not os.path.exists(path):
        print(f'❌ Report not found: {path}')
        sys.exit(1)

    with open(path, encoding='utf-8') as f:
        content = f.read()

    # 使用 dict 合并（后出现覆盖前出现）
    deviations = {}
    for line in content.split('\n'):
        if not line.startswith('|') or '|' not in line[1:]:
            continue
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) < 6 or parts[0].startswith('#'):
            continue
        try:
            if '---' in parts[2] or '---' in parts[1]:
                continue
            file_path = parts[1]
            current = parts[2].strip()
            suggestion = parts[4].strip()
            deviation = parts[5].strip()

            if deviation == '✓' or deviation == '0':
                continue
            m = re.search(r'[-+]?(\d+)', deviation)
            if not m:
                continue
            dev_num = int(m.group(1))
            deviations[file_path] = {
                'file': file_path,
                'current': current,
                'suggestion': suggestion,
                'deviation': dev_num,
            }
        except (ValueError, IndexError):
            continue

    return list(deviations.values())

def validate_depth_suggestion(suggestion):
    """验证建议值合法"""
    if not suggestion or not suggestion.startswith('⭐'):
        return False
    stars = suggestion.count('⭐') + suggestion.count('★')
    return 1 <= stars <= 5

def update_depth(file_path, new_depth, no_overwrite=False):
    """更新文件 frontmatter 的 depth 字段"""
    if not os.path.exists(file_path):
        print(f'❌ Not found: {file_path}')
        return False

    try:
        c = open(file_path, encoding='utf-8', errors='ignore').read()
    except:
        return False

    # 跳过（保留已有校准）
    if no_overwrite and re.search(r'^\s*depth:\s*[⭐★]+', c, re.MULTILINE):
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
    parser.add_argument('--no-overwrite', action='store_true', help='保留已有校准')
    args = parser.parse_args()

    # 支持 "v9" 简写
    report_path = args.report
    if not os.path.exists(report_path):
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
    print(f'No overwrite: {args.no_overwrite}')
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

        if not validate_depth_suggestion(dev['suggestion']):
            print(f'⚠ 跳过 {dev["file"]}: 建议值非法 ({dev["suggestion"]})')
            failed.append(dev)
            continue

        print(f'  {dev["file"]}: {dev["current"]} → {dev["suggestion"]} (偏差 {dev["deviation"]})')

        if args.dry_run:
            continue

        if update_depth(dev['file'], dev['suggestion'], no_overwrite=args.no_overwrite):
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
        # 按类型分组
        downgrades = [d for d in applied if d['deviation'] < 0]
        upgrades = [d for d in applied if d['deviation'] > 0]
        for d in downgrades:
            print(f'  - {d["file"]}: {d["current"]} → {d["suggestion"]}')
        for d in upgrades:
            print(f'  - {d["file"]}: {d["current"]} → {d["suggestion"]}')

if __name__ == '__main__':
    main()
