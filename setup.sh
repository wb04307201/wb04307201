#!/usr/bin/env bash
# setup.sh — 新环境初始化（clone 后跑一次就行）
#
# 用法:
#   bash setup.sh           # 初始化 .claude/skills/（默认行为）
#   bash setup.sh claude    # 同上（保留显式入参）
#
# 做什么:
#   1. 配置 git hooks 路径（启用 skill 自动同步）
#   2. 同步 skills/ → .claude/skills/
#   3. 验证环境就绪

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

AGENT="${1:-}"

if [ "$AGENT" = "--help" ] || [ "$AGENT" = "-h" ]; then
  echo "用法: bash setup.sh [claude]"
  echo ""
  echo "参数:"
  echo "  (无参数)  初始化 .claude/skills/（默认）"
  echo "  claude    同上（显式指定）"
  exit 0
fi

if [ -n "$AGENT" ] && [ "$AGENT" != "claude" ]; then
  echo "错误: 未知参数 '$AGENT'" >&2
  echo "有效参数: (空) 或 'claude'" >&2
  exit 2
fi

echo "=== 项目初始化 ${AGENT:+(仅 $AGENT)} ==="

# 1. Git hooks
git config core.hooksPath .githooks
echo -e "${GREEN}✅ git hooks 已配置（.githooks）${NC}"

# 2. Skills 同步
if [ -f scripts/sync-skills.sh ]; then
  if [ -n "$AGENT" ]; then
    bash scripts/sync-skills.sh "$AGENT"
  else
    bash scripts/sync-skills.sh
  fi
  echo -e "${GREEN}✅ skills 已同步${NC}"
else
  echo -e "${YELLOW}⚠️  scripts/sync-skills.sh 不存在，跳过 skill 同步${NC}"
fi

echo ""
echo "=== 初始化完成 ==="
echo "修改 skill 只需编辑 skills/ 目录，pre-commit hook 会自动同步。"
