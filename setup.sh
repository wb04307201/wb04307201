#!/usr/bin/env bash
# setup.sh — 新环境初始化（clone 后跑一次就行）
#
# 用法: bash setup.sh
#
# 做什么:
#   1. 配置 git hooks 路径（启用 skill 自动同步）
#   2. 同步 skills/ → .claude/skills/ + .codex/skills/
#   3. 验证环境就绪

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

GREEN='\033[0;32m'
NC='\033[0m'

echo "=== 项目初始化 ==="

# 1. Git hooks
git config core.hooksPath .githooks
echo -e "${GREEN}✅ git hooks 已配置（.githooks）${NC}"

# 2. Skills 同步
if [ -f scripts/sync-skills.sh ]; then
  bash scripts/sync-skills.sh
  echo -e "${GREEN}✅ skills 已同步${NC}"
else
  echo "⚠️  scripts/sync-skills.sh 不存在，跳过 skill 同步"
fi

echo ""
echo "=== 初始化完成 ==="
echo "可以开始工作了。修改 skill 只需编辑 skills/ 目录。"
