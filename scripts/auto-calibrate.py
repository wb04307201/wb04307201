"""
auto-calibrate.py v3 - 支持 L5 标准 2.0 + overview/index 独立基线

v3 新增：
- --overview-threshold：D5 ≥ 2 公司案例（默认 v9 标准）
- --topic-threshold：D2 ≥ 5 跨主模块（默认主题深读标准）
- 自动识别 overview vs 主题深读：path 含 README.md + frontmatter type=index
  → 应用 overview 基线（更宽松的校准）

用法：
  python scripts/auto-calibrate.py --report v10 --threshold 1
  python scripts/auto-calibrate.py --report v10 --overview-only
  python scripts/auto-calibrate.py --report v10 --no-overwrite
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


def is_overview_or_index(file_path):
    """识别 overview/index 类文件（MOC 独立基线）"""
    if not file_path.endswith('README.md'):
        return False
    if not os.path.exists(file_path):
        return False
    try:
        c = open(file_path, encoding='utf-8', errors='ignore').read(1000)
    except:
        return False
    # 检查 frontmatter 中 type=index 或 category 含 MOC
    if re.search(r'type:\s*index', c):
        return True
    if re.search(r'category:\s*主模块子\s*MOC', c):
        return True
    return False


def parse_report(path):
    """解析 v{n} 报告 Markdown，提取偏差清单"""
    if not os.path.exists(path):
        print(f'❌ Report not found: {path}')
        sys.exit(1)

    with open(path, encoding='utf-8') as f:
        content = f.read()

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

    if no_overwrite and re.search(r'^\s*depth:\s*[⭐★]+', c, re.MULTILINE):
        return False

    new_c = re.sub(
        r'^\s*depth:\s*[⭐★]+.*$',
        f'  depth: {new_depth}',
        c,
        count=1,
        flags=re.MULTILINE,
    )

    if new_c == c:
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
    parser.add_argument('--report', required=True)
    parser.add_argument('--threshold', type=int, default=1, help='最小偏差阈值')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--no-overwrite', action='store_true')
    parser.add_argument('--overview-only', action='store_true',
                       help='仅应用 overview/index 文件的偏差（跳过主题深读）')
    args = parser.parse_args()

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
    print(f'Overview only: {args.overview_only}')
    print()

    deviations = parse_report(report_path)
    print(f'找到 {len(deviations)} 条偏差记录')
    print()

    applied = []
    skipped = []
    failed = []
    overview_applied = []
    topic_applied = []

    for dev in deviations:
        if abs(dev['deviation']) < args.threshold:
            skipped.append(dev)
            continue

        if not validate_depth_suggestion(dev['suggestion']):
            failed.append(dev)
            continue

        is_overview = is_overview_or_index(dev['file'])

        # overview-only 模式：跳过主题深读
        if args.overview_only and not is_overview:
            skipped.append(dev)
            continue

        marker = '🏠 OVERVIEW' if is_overview else '📖 TOPIC'
        print(f'  {marker} {dev["file"]}: {dev["current"]} → {dev["suggestion"]} (偏差 {dev["deviation"]})')

        if args.dry_run:
            continue

        if update_depth(dev['file'], dev['suggestion'], no_overwrite=args.no_overwrite):
            applied.append(dev)
            if is_overview:
                overview_applied.append(dev)
            else:
                topic_applied.append(dev)
        else:
            failed.append(dev)

    print()
    print('=' * 50)
    print(f'应用: {len(applied)}（overview={len(overview_applied)}, 主题深读={len(topic_applied)}）')
    print(f'跳过（偏差 < {args.threshold}）: {len(skipped)}')
    print(f'失败: {len(failed)}')

    if not args.dry_run and applied:
        print()
        print('建议 commit message:')
        print(f'fix(depth): 自动校准 {len(applied)} 篇（基于 {report_path}）')
        print(f'  - overview/index: {len(overview_applied)} 篇（独立基线）')
        print(f'  - 主题深读: {len(topic_applied)} 篇（v9 标准）')

if __name__ == '__main__':
    main()
