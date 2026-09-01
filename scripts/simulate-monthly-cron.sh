#!/bin/bash
# scripts/simulate-monthly-cron.sh
# 模拟 CI 月度 cron 在本地运行（3 个 workflow 综合模拟）
#
# 2026-09-02 Session 7 更新：新增 structural-link-check 模拟
#   - difficulty-calibration: 03:00 cron
#   - structural-link-check:  06:00 cron
# 模拟时区：UTC（与 GitHub Actions 一致）

set -e

echo "=== 月度 cron 综合模拟 ==="
echo "时间：$(date -u '+%Y-%m-%d %H:%M UTC')"
echo ""

# 1. 结构验证
echo "[1/3] 运行结构验证..."
python << 'PYEOF'
import os, re
from collections import Counter

ROOT = 'note/12.interview'
STORIES_ROOT = 'note/13.story'
MAIN_MODULES = ['note/01-java-and-jvm', 'note/02-cs-foundations', 'note/03-data-stack',
               'note/04-spring-backend', 'note/05-frontend', 'note/06-distributed-systems',
               'note/07-devops-and-tools', 'note/08-ai-foundations', 'note/09-ai-applications',
               'note/10-business-systems', 'note/11-product-and-pm']

depth_counter = Counter()
files_checked = 0

for root_dir in [ROOT, STORIES_ROOT] + MAIN_MODULES:
    if not os.path.isdir(root_dir):
        continue
    for root, _, names in os.walk(root_dir):
        if '.health-tmp' in root or '.obsidian' in root:
            continue
        for n in names:
            if not n.endswith('.md') or n in ('SPEC.md', 'index.md'):
                continue
            norm = root.replace(chr(92), '/')
            rel = norm.replace(root_dir, '').strip('/')
            depth = len([x for x in rel.split('/') if x])
            if n == 'README.md' and depth == 0:
                continue
            p = os.path.join(root, n)
            try:
                c = open(p, encoding='utf-8', errors='ignore').read(800)
            except:
                continue
            files_checked += 1
            m = re.search(r'^\s*depth:\s*([⭐★]+)', c, re.MULTILINE)
            if m:
                stars = m.group(1).count('⭐') + m.group(1).count('★')
                if 1 <= stars <= 5:
                    depth_counter[stars] += 1

print(f'扫描 {files_checked} 文件')
print('depth 分布：')
for s in sorted(depth_counter.keys(), reverse=True):
    print(f'  {"*" * s} ({s}-star): {depth_counter[s]}')
PYEOF

echo ""

# 2. 找最新 v{n} 抽样报告
echo "[2/3] 查找最新抽样报告..."
LATEST_REPORT=$(ls -t skills/note-health/references/v*-sampling-report.md 2>/dev/null | head -1)
if [ -z "$LATEST_REPORT" ]; then
    echo "未找到 v* 抽样报告，跳过自动校准"
    exit 0
fi
echo "  使用报告：$LATEST_REPORT"
echo ""

# 3. 运行 auto-calibrate.py
echo "[3/3] 应用偏差 >= 2 校准..."
REPORT_NAME=$(basename "$LATEST_REPORT" .md | sed 's/-sampling-report//')
python scripts/auto-calibrate.py --report "$REPORT_NAME" --threshold 2 --dry-run

echo ""
echo "=== 月度 cron 校准完成（dry-run 验证） ==="
echo ""
echo "在生产环境（GitHub Actions）下，--dry-run 标志将移除并应用校准。"

# 4. structural-link-check 模拟（对应 .github/workflows/structural-link-check.yml 06:00 cron）
echo ""
echo "==============================================="
echo "[4/4] 运行 structural-link-check（06:00 cron 模拟）..."
echo "==============================================="
echo "时间：$(date -u '+%Y-%m-%d %H:%M UTC')"
echo ""

if [ -f scripts/check-broken-links.py ]; then
  echo "[A] 全库链接完整性检查..."
  python scripts/check-broken-links.py 2>&1 | tail -10
  LINK_EXIT=$?
  echo ""
  if [ "$LINK_EXIT" -eq 0 ]; then
    echo "✅ 链接完整性：0 断链"
  else
    echo "❌ 链接完整性：发现断链，请修复"
  fi
  echo ""
  echo "[B] 月度 cron 完成时间：$(date -u '+%Y-%m-%d %H:%M UTC')"
else
  echo "❌ scripts/check-broken-links.py 不存在"
fi

echo ""
echo "=== 月度 cron 综合模拟完成 ==="
echo "对应 workflow："
echo "  - 03:00 difficulty-calibration.yml（结构验证 + auto-calibrate）"
echo "  - 06:00 structural-link-check.yml（链接完整性）"
