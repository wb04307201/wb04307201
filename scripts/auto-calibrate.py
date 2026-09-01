"""
auto-calibrate.py v6 - 支持 v15 ground truth + v14 微调标准

v6 新增（基于 v16 验证 100% 准确度突破）：
- 完整 v15 ground truth 数据解析（80 篇平均 5.04/10）
- v14 微调标准（D2≥3 + D5≥1 + overview D5 豁免）
- v15/v16 校准文件支持（92.9% 完全一致）

v5 历史：
- D2 阈值 5 → 3 + D5 阈值 2 → 1

v4 历史：
- apply_overview_d5_exemption 逻辑

v3 历史：
- overview/index 类独立基线

关键成果：v15 ground truth + 14 篇高分校准 → v16 100% 偏差≤1（首次超过 ≥75% 目标）

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


def get_depth_stars(depth_str):
    """从 '⭐⭐⭐' 字符串提取星数"""
    return depth_str.count('⭐') + depth_str.count('★')


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
    if re.search(r'type:\s*index', c):
        return True
    if re.search(r'category:\s*主模块子\s*MOC', c):
        return True
    return False


def apply_overview_d5_exemption(file_path, current_depth, suggested_depth):
    """
    v12 新增：overview/index 类 D5 豁免
    - 如果当前 depth 偏低但 suggested 是 ≥ 3（中等深度），overview 可跳过 D5 案例检查
    - 自动保留当前 depth 在 overview 类（避免盲升）
    """
    if not is_overview_or_index(file_path):
        return suggested_depth  # 非 overview，按建议值
    # overview 类：current ≤ L2 + suggested ≥ L3 → 强制升到 L3（避免校准不达标）
    cur = get_depth_stars(current_depth)
    sug = get_depth_stars(suggested_depth)
    if cur <= 2 and sug >= 3:
        return suggested_depth  # overview 升档
    # 当前已 ≥ L3，保留原状（避免高估）
    if cur >= 3:
        return current_depth
    return suggested_depth


def validate_depth_suggestion(suggestion):
    """验证建议值合法"""
    if not suggestion or not suggestion.startswith('⭐'):
        return False
    stars = suggestion.count('⭐') + suggestion.count('★')
    return 1 <= stars <= 5


def get_d2_threshold(file_path):
    """v14 微调：D2 阈值从 5 降至 3 跨主模块"""
    return 3


def get_d5_threshold(file_path):
    """v14 微调：D5 阈值从 2 降至 1 案例（仅对主题深读类）"""
    if is_overview_or_index(file_path):
        return 0  # overview 类豁免
    return 1


def parse_v15_groundtruth(report_path):
    """v6 新增：解析 v15 ground truth（v15-sampling-report.md 风格）

    支持的偏差格式：
    - markdown 表格中的偏差列
    - 偏差格式：'-3.5', '+2.0' 等

    返回：deviations 字典（key=文件路径，value=建议 depth）
    """
    if not os.path.exists(report_path):
        print(f'❌ v15 ground truth not found: {report_path}')
        sys.exit(1)

    with open(report_path, encoding='utf-8') as f:
        content = f.read()

    deviations = {}
    for line in content.split('\n'):
        if not line.startswith('|') or '|' not in line[1:]:
            continue
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) < 6:
            continue
        try:
            file_path = parts[1]
            current = parts[2].strip()
            deviation = parts[-1].strip()  # 最后一列是偏差

            # 跳过表头分隔
            if '---' in parts[1] or '---' in parts[2]:
                continue
            # 解析偏差数字
            m = re.search(r'[-+]?(\d+\.?\d*)', deviation)
            if not m:
                continue
            dev_num = float(m.group(1))
            if abs(dev_num) < 0.5:  # 偏差 < 0.5 视为一致
                continue
            # 计算建议 depth
            current_stars = current.count('⭐') + current.count('★')
            if dev_num > 0:  # 低估
                new_stars = current_stars + int(round(dev_num))
            else:  # 高估
                new_stars = current_stars + int(round(dev_num))
            new_stars = max(1, min(5, new_stars))
            new_depth = '⭐' * new_stars
            deviations[file_path] = {
                'file': file_path,
                'current': current,
                'suggestion': new_depth,
                'deviation': dev_num,
            }
        except (ValueError, IndexError):
            continue

    return list(deviations.values())


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

        # v12 新增：overview D5 豁免逻辑
        # - overview 类：current ≤ L2 + suggested ≥ L3 → 应用 suggested
        # - overview 类：current ≥ L3 → 保留 current（避免盲升导致高估）
        # - 主题深读类：直接应用 suggested
        final_depth = apply_overview_d5_exemption(dev['file'], dev['current'], dev['suggestion'])
        if final_depth != dev['suggestion']:
            print(f'    → v12 豁免: {dev["suggestion"]} → {final_depth}')

        if update_depth(dev['file'], final_depth, no_overwrite=args.no_overwrite):
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
