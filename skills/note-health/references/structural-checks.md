> 由 note-health/SKILL.md Phase 1/4 调用

# 结构类审计扫描（structural-checks）

本文件保存 note-health skill 调用的**机械扫描 / 风险检查 / commit 拆分**原始命令与分类规则。所有命令原样保留，运行时不修改。

## 8 大审计类别

| # | 类别 | 扫描命令示例 |
|---|------|------------|
| 1 | **数字一致性** | `grep -rn "篇\|个\|行" note/README.md note/*/README.md` |
| 2 | **H1 / 标题规范** | `grep -rn "^# " note/*/README.md` |
| 3 | **回链覆盖率 + 互链双向性** | `grep -rln "← \[返回\|返回.*目录" note/ | wc -l` vs `find note -name README.md \| wc -l`；外加单向链接扫描（child → parent 但 parent 不回链） |
| 3.5 | **孤岛检测 / 总目录扫描** | 扫描所有新文件（commit 时间 ≤ N 天），验证其：① 链接了 ≥ 2 个旧章节 ② 父 README / 总目录表有反向链接 ③ 同级兄弟有反向链接 |
| 4 | **索引/入口缺失** | `find note -type d -not -path "*/node_modules/*" \| wc -l` vs README 引用 |
| 5 | **内容重复** | `find note -name "*.md" \| xargs grep -l "<关键概念>" \| sort -u` |
| 6 | **内容补充缺口** | 找到深度 ≤ 50 行的 README（可能是占位）|
| 7 | **架构/分类/命名** | 目录命名风格不一致 / 编号缺失 |
| 8 | **其他**（PNG / 脚本 / 杂项）| `find note -name "*.png" \| xargs grep -L "!"` |
| 9 | **系列完整性** | 扫描"声明了 N 个子章节但实际文件缺失"的系列（见 Step 1.9） |

## Step 1 现状扫描

**目的**：用真实命令收集证据，不凭印象

**关键操作**（**精简版 8 步**，原 22 步合并）：
```bash
cd "$(git rev-parse --show-toplevel)"

# 1. 总览
find note -name "README.md" | wc -l
find note -type f -name "*.md" | wc -l
find note -name "*.png" | wc -l

# 2. frontmatter 覆盖
no_fm=$(find note -name "README.md" -exec grep -L "^<!--" {} \; 2>/dev/null | wc -l)
echo "无 frontmatter: $no_fm / $(find note -name "README.md" | wc -l)"

# 3. 数字一致性扫描
grep -rn "篇\|个\|行" note/README.md 2>/dev/null | grep -E "[0-9]+\s*(篇|个|行)" | head -30

# 4. H1 数字编号违规
grep -rn "^# [一二三四五六七八九十]、\|^# [0-9][0-9]\." note/*/README.md 2>/dev/null | head -10

# 5. 回链覆盖率
TOTAL_READMES=$(find note -name "README.md" | wc -l)
WITH_BACKLINK=$(grep -rl "← \[返回" note/ 2>/dev/null | wc -l)
echo "回链覆盖: $WITH_BACKLINK / $TOTAL_READMES"

# 6. broken links（一次 Python 扫描）
python3 -c "
import os, re, glob
def resolve(c, t):
    if t.startswith('/'):
        return os.path.normpath(os.path.join('note', t.lstrip('/')))
    return os.path.normpath(os.path.join(os.path.dirname(c), t))
real_broken = 0
for readme in glob.glob('note/**/*.md', recursive=True):
    try:
        with open(readme, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except: continue
    for m in re.finditer(r'\]\(([^)#]+\.md)(?:#[^)]*)?\)', content):
        target_rel = m.group(1)
        if target_rel.startswith('http'): continue
        target_abs = resolve(readme, target_rel)
        if not os.path.isfile(target_abs):
            if 'xxx' not in target_rel and 'x/README' not in target_rel and 'xx/yy' not in target_rel:
                real_broken += 1
print(f'broken links: {real_broken}')
"

# 7. 索引缺失
for d in $(find note -type d -mindepth 2 -maxdepth 4 2>/dev/null); do
  if [ ! -f "$d/README.md" ]; then echo "缺 README: $d"; fi
done

# 8. 浅 README（< 50 行 leaf）
python3 -c "
import os, glob
for readme in sorted(glob.glob('note/**/README.md', recursive=True)):
    if os.path.dirname(readme).count(os.sep) < 3: continue
    with open(readme, 'r', encoding='utf-8', errors='ignore') as f:
        lines = sum(1 for _ in f)
    if lines < 50: print(f'  {lines:3d}行  {readme}')
"
```

**深度模式**（按需展开，包含原 14 步的孤岛检测、单调链接扫描、系列完整性等）。

```bash
# 4.5 单向链接扫描（parent 不回链 child）
# 原理：find 所有文件中的反向链接，记下每个"被链到"的文件
# 然后检查每个被链到的文件，是否回链了链接它的源
#
# 兼容说明：原版用 `realpath -m --relative-to=.`，macOS BSD realpath 不支持 -m 参数，
#       部分 Windows 环境 realpath 行为不一致。改用嵌套 cd + pwd 回退到 python3 计算。
resolve_target() {
  local child="$1" target="$2"
  # 方法 1：GNU coreutils realpath（多数 Linux / Git Bash）
  if command -v realpath >/dev/null 2>&1; then
    realpath -m --relative-to=. "$(dirname "$child")/$target" 2>/dev/null && return
  fi
  # 方法 2：cd + pwd（POSIX 兼容，处理 ../ 与 ./）
  local abs
  abs="$(cd "$(dirname "$child")" 2>/dev/null && cd "$(dirname "$target")" 2>/dev/null && pwd -P 2>/dev/null)/$(basename "$target")"
  [ -n "$abs" ] && [ -e "$abs" ] && echo "$abs" && return
  # 方法 3：python3 兜底（处理任意深度 ../）
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "
import os, sys
print(os.path.normpath(os.path.join(os.path.dirname(sys.argv[1]), sys.argv[2])))
" "$child" "$target" 2>/dev/null && return
  fi
  # 方法 4：放弃，按相对路径回退（可能误报，但不会漏报）
  echo "$target"
}

echo "=== 单向链接扫描（child → parent 但 parent 不回链）==="
for child in $(find note -name "*.md"); do
  # 找 child 文件链到的所有 target（粗略正则，可能有误差，需人工复核）
  grep -oE '\]\(([^)]+\.md)' "$child" 2>/dev/null | sed 's/](//' | while read target; do
    # 规范化 target 为绝对路径（跨平台兼容：realpath → cd+pwd → python3 → 兜底）
    abs_target=$(resolve_target "$child" "$target")
    [ -f "$abs_target" ] || continue
    # 检查 target 是否反向链到 child（粗略：包含 child 的 basename）
    child_base=$(basename "$child")
    if ! grep -q "$child_base" "$abs_target" 2>/dev/null; then
      echo "  ⚠ child=$child → target=$target（target 未回链 child）"
    fi
  done
done
echo "=== 同级兄弟不互链扫描（示例）==="
# 在某个目录下找兄弟 README，验证是否互相链接
DIR_TO_CHECK="note/11.ai/07-llmops"
for sibling in $(find "$DIR_TO_CHECK" -name "README.md" -maxdepth 2 2>/dev/null); do
  for other in $(find "$DIR_TO_CHECK" -name "README.md" -maxdepth 2 2>/dev/null); do
    [ "$sibling" = "$other" ] && continue
    if ! grep -q "$(basename $sibling .md)" "$other" 2>/dev/null; then
      echo "  ⚠ sibling=$(basename $sibling) 未被 $(basename $other) 链接"
    fi
  done
done

# 4.6 孤岛检测 / 总目录扫描（新文件未被总目录引用）
# 原理：找最近 N 天新增的 README，验证它们是否被任何总目录表引用
echo "=== 孤岛检测 / 总目录扫描 ==="
# 找最近 7 天新增的 README（基于 git log）
SINCE_DATE=$(date -d "7 days ago" --iso-8601=seconds 2>/dev/null || date -v-7d "+%Y-%m-%dT%H:%M:%S")
NEW_FILES=$(git log --since="$SINCE_DATE" --diff-filter=A --name-only --pretty=format: 2>/dev/null | grep "\.md$" | sort -u)
for new_file in $NEW_FILES; do
  [ -z "$new_file" ] && continue
  base=$(basename "$new_file" .md)
  # 检查是否有任何 README / 总目录引用了 base
  references=$(grep -rl "\[$base\]\|\"$base\"\|/$base" note/ 2>/dev/null | wc -l)
  if [ "$references" -lt 2 ]; then
    echo "  ⚠ 新文件 $new_file 仅被 $references 处引用（建议 ≥ 2：1 个父 README + 1 个反向链）"
  fi
done

# 5. 内容重复检测（同名目录）
find note -type d -name "*engineer*" -o -name "*memory*" -o -name "*prompt*" | sort

# 6. PNG 孤儿检测
find note -name "*.png" | wc -l
grep -rl "\.png" note/ | wc -l  # 引用 PNG 的文件数

# 9. 系列完整性审计（声明了但没写的子章节）
# 原理：找包含"子章节导航"或目录表的 README，提取声明的文件名，
# 验证文件是否实际存在
echo "=== 系列完整性审计 ==="
for readme in $(grep -rl "子章节导航\|## .*目录\|## .*文章清单\|系列导航" note/ 2>/dev/null); do
  dir=$(dirname "$readme")
  # 提取表格中声明的 .md 链接
  grep -oE '\[.*?\]\(([^)]+\.md)\)' "$readme" 2>/dev/null | \
    grep -oE '\(([^)]+\.md)\)' | sed 's/[()]//g' | while read target; do
    abs_target=$(realpath -m "$dir/$target" 2>/dev/null || echo "$dir/$target")
    if [ ! -f "$abs_target" ]; then
      echo "  ⚠ $readme 声明了 $target 但文件不存在"
    fi
  done
done

# 9.1 系列内兄弟互链完整性审计
# 原理：找有编号文件（01-xxx.md）的目录，检查每篇是否链向同目录其他文件
echo "=== 系列内兄弟互链审计 ==="
for dir in $(find note -type d -exec sh -c 'ls "$1"/[0-9]*.md 2>/dev/null | head -1 | grep -q . && echo "$1"' _ {} \;); do
  file_count=$(ls "$dir"/[0-9]*.md 2>/dev/null | wc -l)
  [ "$file_count" -lt 2 ] && continue
  echo "系列: $dir ($file_count 篇)"
  for file in $(ls "$dir"/[0-9]*.md 2>/dev/null); do
    for other in $(ls "$dir"/[0-9]*.md 2>/dev/null); do
      [ "$file" = "$other" ] && continue
      other_base=$(basename "$other")
      if ! grep -q "$other_base" "$file" 2>/dev/null; then
        echo "  ⚠ $(basename $file) 未链向 $other_base"
      fi
    done
  done
done
```

### Step 5.5: Commit 拆分模式

**当用户说"拆分做 commit"时**，触发本模式：

```yaml
输入：审计完成 + 用户要求拆分 commit
输出：建议 commit 列表（先给用户看，再执行）

判断"真改动"（去 LF/CRLF 噪声）：
  for f in $(git diff --name-only); do
    if git diff "$f" | grep -qE "^[+-][^+-]"; then
      echo "$f"  # 真有内容改动
    fi
  done

按主题分组：
  fix(<module>): <动作>     → 修复类
  feat(<module>): <新文件>  → 新增类
  refactor(<module>): <结构> → 结构调整
  docs(<scope>): <文档>      → 文档类
  chore(<scope>): <琐事>    → 杂项

每 commit 模板：
  <type>(<scope>): <动作>
  
  - <改动 1>
  - <改动 2>
  
  Co-Authored-By: Claude <noreply@anthropic.com>
```

**示例（第 1 轮审计拆分 18 commit）**：
1. fix(06.spring): 新增 transaction/distributed 分类 README
2. fix(06.spring): validation/annotations 链接 6 处修正
3. fix(06.spring): validation/annotations-and-usage typo 3 处
4. fix(13.split-hairs): context-engineering 重命名遗留 10 条 broken link
5. fix(13.split-hairs): 9 个设计导览页加 index-only 注释
6. fix(13.split-hairs): 新增 05.security 分类 README
...（共 18 个）

### Step 5.6: 执行风险检查

**执行前先过 6 项风险检查**（避免昨天 .obsidian 误删的教训）：

```yaml
□ 是否会修改 .gitignore？          → 必须先确认
□ 是否会删除已 tracked 文件？     → 必须先确认
□ 是否会修改其他用户的配置？      → 必须先确认（如 .obsidian）
□ 是否会动 .idea / .vscode？      → 必须先确认
□ 是否会批量 commit > 30 个？     → 必须先确认
□ 是否会涉及外部系统（如 git push）→ 必须先确认
```

任一为"是"，**先停下来用 AskUserQuestion 确认**。

## Common Mistakes（结构类）

### ❌ Mistake 1: 输出 70+ 改动一次性

**症状**：扫描出 70 个问题，全部列出让用户决策 → 用户瘫痪

**修复**：Step 5 必须**分批**输出；只 P0 + 关键 P1 进入第一批决策；其他延后

### ❌ Mistake 2: 不排除已修复项

**症状**：报告 270 个 "反直觉代码模板残留"（实际已被清）

**修复**：Step 2 强制过滤；本会话 commit 列表 → 排除

### ❌ Mistake 3: 用印象不用命令

**症状**：说"应该有 7 个 leaf"但没实际 find → 数字错

**修复**：Step 1 必须用 grep / find / wc 收集证据；每条发现附 file:line

### ❌ Mistake 4: 不区分机械 vs 判断

**症状**：让用户决策"455 个 README 补回链"的每一个 → 用户放弃

**修复**：Step 4 必须分类；机械任务让 subagent 自动跑；判断任务才让用户决策

### ❌ Mistake 5: ROI 标准不清晰

**症状**：P0/P1/P2/P3 是 ad-hoc 判断 → 不一致

**修复**：Step 3 用明确标准（影响 × 工作量）；标准写在本 skill "Quick Reference" 表中

### ❌ Mistake 6: 报告里只列问题不给方案

**症状**：报告"目录命名不一致"，没说怎么修

**修复**：每条发现必须配可执行方案（"重命名为 X" / "删除 Y" / "合并为 Z"）

### ❌ Mistake 7: 不验证已修状态

**症状**：报告"应该重命名 13.split-hairs/11.ai/transformer/"（实际已与主模块对齐）

**修复**：Step 2 排除本会话 commit 列表；用 git log 验证

### ❌ Mistake 8: 缺少 commit 策略

**症状**：建议"删除 76 个孤儿 PNG"，但没说用哪个 commit

**修复**：每个建议附 commit message（"chore(note): 删除孤儿 PNG"）

### ❌ Mistake 8.5: Windows 行尾污染

**症状**：在 Windows 下用 sed 编辑后，`git status` 显示 700+ "warning: LF will be replaced by CRLF"，**真实改动只有 30 个但误报 700+**

**根因**：Windows 默认 Git `core.autocrlf=true`，导致 LF → CRLF 转换

**修复**：
```bash
# 1. 项目级 .gitattributes 固定行尾
echo "* text=auto eol=lf" > .gitattributes

# 2. 关闭本地自动转换
git config core.autocrlf false

# 3. 审计时过滤 LF/CRLF 噪声
git diff --ignore-cr-at-eol --ignore-space-at-eol
```

### ❌ Mistake 8.6: 误删用户配置

**症状**：自作主张清理 .obsidian 跟踪 + 加 .gitignore，用户后来说"留着它"

**修复**：
- Step 5.6 风险检查（见上）
- 任何会改 .gitignore / .obsidian / .idea 的操作**必须先确认**

### ❌ Mistake 9: 单向链接扫描缺失

**症状**：审计只检查"无回链"（leaf → parent 缺失），不检查"单向回链"（parent → leaf 缺失）。例如：

- `note/11.ai/07-llmops/05-agent-evaluation/README.md` 链到 `07-llmops/README.md` —— 后者**没反向链**到前者
- `note/11.ai/03-engineering/production-agent/README.md` 链到 `11.ai/README.md` —— 后者**没反向链**到前者
- `note/11.ai/04-architecture/intelligent-system-layers/README.md` 被 `agent-architecture` 链到 —— **没反向链**

**修复**：
- **审计类别 #3 升级**："回链覆盖率" → **"回链覆盖率 + 互链双向性"**
- **Step 1.4.5 新增"单向链接扫描"**：grep 所有 child → target 链接，反查 target 是否含 child basename
- **Step 1.4.5 附"同级兄弟不互链扫描"**：在某个目录下找所有兄弟 README，验证是否互相引用

**反直觉点**：很多人以为"我加了 2 条反向链就完事" —— 实际上**新内容责任**包括：让被链接的 parent / 同级兄弟**也回链**。双向互链才能让知识网"加密"。
