#!/usr/bin/env bash
# verify-case-study.sh — 验证单篇 AI 案例文章的结构与约束
# 用法: ./tools/verify-case-study.sh <path-to-README.md>

set -e
FILE="$1"

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "FAIL: 文件不存在: $FILE"
  exit 1
fi

ERRORS=()

# 1. 字数检查 (中文字符数, 排除 frontmatter 区与代码块)
WORDS=$(awk '
  /^---$/ { in_fm = !in_fm; next }
  in_fm { next }
  /^```/ { in_code = !in_code; next }
  in_code { next }
  { gsub(/[ \t\r\n]/, ""); print }
' "$FILE" | wc -m | tr -d ' ')

if [ "$WORDS" -lt 1800 ] || [ "$WORDS" -gt 2500 ]; then
  ERRORS+=("字数 $WORDS 不在 1800-2500 区间")
fi

# 2. 5 节 H2 检查
for h in "## 一、" "## 二、" "## 三、" "## 四、" "## 五、"; do
  if ! grep -qF "$h" "$FILE"; then
    ERRORS+=("缺少 H2 节: $h")
  fi
done

# 3. 一句话总结
if ! grep -qE '^\s*>\s*\*\*一句话总结\*\*' "$FILE"; then
  ERRORS+=("缺少 '> **一句话总结**' 标记")
fi

# 4. 领域标签 (顶部 50 行内至少 3 个 #xxx)
HEAD_TAGS=$(head -50 "$FILE" | grep -oE '#(编程|客服|法律|教育|金融|办公|销售|医疗|制造)' | sort -u | wc -l | tr -d ' ')
if [ "$HEAD_TAGS" -lt 3 ]; then
  ERRORS+=("领域标签不足 3 个（当前: $HEAD_TAGS）")
fi

# 5. 原文链接
if ! grep -qE '原文链接\s*[:：]' "$FILE"; then
  ERRORS+=("缺少 '原文链接:' 字段")
fi
if ! grep -qE 'https?://[^\s)]+' "$FILE"; then
  ERRORS+=("缺少 http(s) 链接")
fi

# 6. 致谢/出处尾签
if ! grep -qE '本文基于.*整理|本文整理自' "$FILE"; then
  ERRORS+=("缺少 '本文基于 ... 整理' 致谢尾签")
fi

# 7. 第五节禁用词检查
BANNED='File View|LoomAgent|MethodTraceLog|灵梭|灵锁|巧路由|灵动调度|动态加载器|美化日志|CHMCache|CHMRLock|dynamo-spring|SQL Forge|SQL 工坊|Method Trace Log|方法追踪日志|Flexible Lock|Smart Router|FlexSchedule|pretty-log|loader-util'
if grep -E "$BANNED" "$FILE" > /dev/null; then
  HIT=$(grep -oE "$BANNED" "$FILE" | head -3 | tr '\n' ',')
  ERRORS+=("第五节出现禁用词: $HIT")
fi

# 报告
if [ ${#ERRORS[@]} -eq 0 ]; then
  echo "OK: $FILE  (字数: $WORDS)"
  exit 0
else
  echo "FAIL: $FILE"
  for e in "${ERRORS[@]}"; do
    echo "  - $e"
  done
  exit 1
fi
