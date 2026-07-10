#!/usr/bin/env bash
# sync-skills.sh — 从 skills/ (单一来源) 同步到 .claude/skills/ 和 .codex/skills/
#
# 用法:
#   bash scripts/sync-skills.sh          # 手动同步
#   bash scripts/sync-skills.sh --check  # 只检查不复制（CI 用）
#
# 工作原理:
#   skills/ 是 source of truth
#   .claude/skills/ 和 .codex/skills/ 是它的镜像
#   每次修改 skills/ 后运行此脚本，或在 pre-commit hook 中自动运行

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

# 自动配置 git hooks 路径（首次 clone 后自动生效，无需手动操作）
CURRENT_HOOKS_PATH=$(git config core.hooksPath 2>/dev/null || echo "")
if [ "$CURRENT_HOOKS_PATH" != ".githooks" ]; then
  git config core.hooksPath .githooks
  echo -e "${GREEN}自动配置: git core.hooksPath → .githooks${NC}"
fi
SOURCE="$REPO_ROOT/skills"
TARGETS=("$REPO_ROOT/.claude/skills" "$REPO_ROOT/.codex/skills")

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

if [ ! -d "$SOURCE" ]; then
  echo -e "${RED}错误: $SOURCE 不存在${NC}"
  echo "请先创建 skills/ 目录并放入 skill 文件"
  exit 1
fi

CHECK_MODE=false
if [ "${1:-}" = "--check" ]; then
  CHECK_MODE=true
fi

DRIFT=0

for target in "${TARGETS[@]}"; do
  target_name=$(echo "$target" | sed "s|$REPO_ROOT/||")

  # 检查 target 是否有 source 中不存在的文件（多余文件）
  if [ -d "$target" ]; then
    while IFS= read -r file; do
      rel="${file#$target/}"
      if [ ! -f "$SOURCE/$rel" ]; then
        if $CHECK_MODE; then
          echo -e "${RED}多余: $target_name/$rel（不在 skills/ 中）${NC}"
          DRIFT=$((DRIFT + 1))
        else
          rm -f "$file"
          echo -e "${YELLOW}删除多余: $target_name/$rel${NC}"
        fi
      fi
    done < <(find "$target" -type f -name "*.md" 2>/dev/null)
  fi

  # 同步 source → target
  while IFS= read -r file; do
    rel="${file#$SOURCE/}"
    target_file="$target/$rel"

    if [ ! -f "$target_file" ] || ! diff -q "$file" "$target_file" > /dev/null 2>&1; then
      if $CHECK_MODE; then
        echo -e "${RED}漂移: $rel → $target_name/ 不同步${NC}"
        DRIFT=$((DRIFT + 1))
      else
        mkdir -p "$(dirname "$target_file")"
        cp "$file" "$target_file"
        echo -e "${GREEN}同步: $rel → $target_name/${NC}"
      fi
    fi
  done < <(find "$SOURCE" -type f -name "*.md" 2>/dev/null)
done

if $CHECK_MODE; then
  if [ "$DRIFT" -gt 0 ]; then
    echo -e "\n${RED}发现 $DRIFT 处漂移，请运行: bash scripts/sync-skills.sh${NC}"
    exit 1
  else
    echo -e "${GREEN}所有 skill 目录一致 ✅${NC}"
    exit 0
  fi
else
  echo -e "${GREEN}同步完成 ✅${NC}"
fi
