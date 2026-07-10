#!/usr/bin/env bash
# sync-skills.sh — 从 skills/ (单一来源) 同步到各智能体的 skills 目录
#
# 用法:
#   bash scripts/sync-skills.sh              # 同步所有智能体
#   bash scripts/sync-skills.sh claude       # 只同步 .claude/skills/
#   bash scripts/sync-skills.sh codex        # 只同步 .codex/skills/
#   bash scripts/sync-skills.sh --check      # 只检查不复制（CI 用）
#   bash scripts/sync-skills.sh --check claude  # 只检查 claude
#
# 新增智能体支持：在 AGENT_MAP 中加一行即可

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# 自动配置 git hooks 路径（首次 clone 后自动生效）
CURRENT_HOOKS_PATH=$(git config core.hooksPath 2>/dev/null || echo "")
if [ "$CURRENT_HOOKS_PATH" != ".githooks" ]; then
  git config core.hooksPath .githooks
  echo -e "${GREEN}自动配置: git core.hooksPath → .githooks${NC}"
fi

# ========== 智能体 → 目录映射 ==========
# 新增智能体只需在这里加一行: "名称|目标目录"
AGENT_MAP=(
  "claude|.claude/skills"
  "codex|.codex/skills"
)

SOURCE="$REPO_ROOT/skills"

if [ ! -d "$SOURCE" ]; then
  echo -e "${RED}错误: $SOURCE 不存在${NC}"
  echo "请先创建 skills/ 目录并放入 skill 文件"
  exit 1
fi

# ========== 参数解析 ==========
CHECK_MODE=false
FILTER_AGENT=""

for arg in "$@"; do
  case "$arg" in
    --check) CHECK_MODE=true ;;
    --help|-h)
      echo "用法: bash scripts/sync-skills.sh [--check] [claude|codex]"
      echo ""
      echo "选项:"
      echo "  --check    只检查不同步（CI 用）"
      echo "  claude     只同步 .claude/skills/"
      echo "  codex      只同步 .codex/skills/"
      echo "  (无参数)   同步所有智能体"
      exit 0
      ;;
    *) FILTER_AGENT="$arg" ;;
  esac
done

# ========== 同步逻辑 ==========
DRIFT=0

for entry in "${AGENT_MAP[@]}"; do
  agent_name="${entry%%|*}"
  target_rel="${entry##*|}"
  target="$REPO_ROOT/$target_rel"

  # 如果指定了 agent 过滤，跳过不匹配的
  if [ -n "$FILTER_AGENT" ] && [ "$FILTER_AGENT" != "$agent_name" ]; then
    continue
  fi

  # 检查 target 是否有多余文件
  if [ -d "$target" ]; then
    while IFS= read -r file; do
      rel="${file#$target/}"
      if [ ! -f "$SOURCE/$rel" ]; then
        if $CHECK_MODE; then
          echo -e "${RED}多余: $target_rel/$rel（不在 skills/ 中）${NC}"
          DRIFT=$((DRIFT + 1))
        else
          rm -f "$file"
          echo -e "${YELLOW}删除多余: $target_rel/$rel${NC}"
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
        echo -e "${RED}漂移: $rel → $target_rel/ 不同步${NC}"
        DRIFT=$((DRIFT + 1))
      else
        mkdir -p "$(dirname "$target_file")"
        cp "$file" "$target_file"
        echo -e "${GREEN}同步: $rel → $target_rel/${NC}"
      fi
    fi
  done < <(find "$SOURCE" -type f -name "*.md" 2>/dev/null)
done

# ========== 结果输出 ==========
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
