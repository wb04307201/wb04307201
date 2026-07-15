# note-health Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `note-audit-and-improvement` + `note-content-quality` 合并为单一 `note-health` skill，采用薄 orchestrator + references 分层引擎，全库穷举用 Workflow pipeline 断点续跑。

**Architecture:** 薄 `SKILL.md`（scope 三档判断 + 4 相自底向上调度 + 综合报告）委托两份下沉规则 `references/structural-checks.md`（机械扫描）与 `references/leaf-quality.md`（判断式打分）；全库穷举跑 `references/health-workflow.js`（按 leaf 文件批 ~5-8 篇/agent fan-out）。

**Tech Stack:** Markdown（skill）、Bash/Python（扫描命令）、Workflow JS 脚本、`scripts/sync-skills.sh` 镜像同步。

## Global Constraints

- **只改 `skills/`**：`.claude/skills/`、`.codex/skills/` 是 gitignore 的自动镜像，由 `scripts/sync-skills.sh` / pre-commit hook 重建（CLAUDE.md）。
- **迁移不丢内容**：structural-checks.md 必须覆盖 audit 原 8-9 类全部扫描；leaf-quality.md 必须覆盖 content-quality 原 G1-G6 + A~G 七类 + 满分计算表 + 特殊处理。
- **commit 格式**：`refactor(skills):` / `feat(skills):` / `docs(skills):`，结尾 `Co-Authored-By: Claude <noreply@anthropic.com>`。
- **commit 时机**：仅在用户明确要求时提交（CLAUDE.md 优先于 skill 的自动提交）。若届时在默认分支，先切分支。
- **note 实测基线**：717 个含 .md 目录 / 697 README / 1029 .md / 14 模块。数字用 `find` 实时校对，不 hardcode。
- **源文件**：`skills/note-audit-and-improvement/SKILL.md`（554 行）、`skills/note-content-quality/SKILL.md`（495 行）为迁移唯一来源。

---

## File Structure

- Create: `skills/note-health/SKILL.md` — 薄 orchestrator
- Create: `skills/note-health/references/structural-checks.md` — 机械扫描规则（迁自 audit）
- Create: `skills/note-health/references/leaf-quality.md` — 判断式打分规则（迁自 content-quality）
- Create: `skills/note-health/references/health-workflow.js` — 全库穷举 Workflow 脚本
- Delete: `skills/note-audit-and-improvement/`、`skills/note-content-quality/`
- Modify: `skills/note-knowledge-qa/SKILL.md:786-787`（联动引用改名）
- Modify: `CLAUDE.md:23-25`（tree）、`:68`（4→3）、`:73-74`（两行合一）

---

## Task 1: 迁移机械扫描 → references/structural-checks.md

**Files:**
- Create: `skills/note-health/references/structural-checks.md`
- Source: `skills/note-audit-and-improvement/SKILL.md`

**Interfaces:**
- Produces: `structural-checks.md`，被 SKILL.md 的 Phase 1 引用。含具名小节：`## 8 大审计类别`、`## Step 1 现状扫描`（精简 8 步 + 深度模式）、`## Step 5.6 执行风险检查`、`## Step 5.5 commit 拆分模式`。

- [ ] **Step 1: 建目录**

```bash
mkdir -p skills/note-health/references
```

- [ ] **Step 2: 迁移扫描内容**

把 audit SKILL.md 的以下段落**原样搬入** `structural-checks.md`（保留所有 grep/find/python 命令逐字不改）：
- `## 8 大审计类别`表（audit L52-65，9 行类别表）
- `### Step 1: 现状扫描` 精简 8 步（audit L69-134）
- 深度模式：单向链接扫描、孤岛检测、内容重复、系列完整性（audit L136-247）
- `### Step 5.6: 执行风险检查` 6 项（audit L345-358）
- `### Step 5.5: Commit 拆分模式`（audit L305-343）
- audit `## Common Mistakes` 中**结构类** 9 条（Mistake 1-9，L374-461）

顶部加一行来源标注：`> 迁自 note-audit-and-improvement，由 note-health/SKILL.md Phase 1/4 调用`。

- [ ] **Step 3: 验证覆盖（9 类扫描全在）**

Run:
```bash
for kw in "数字一致" "H1" "回链" "孤岛" "索引" "内容重复" "架构" "系列完整" "风险检查"; do
  grep -q "$kw" skills/note-health/references/structural-checks.md && echo "OK: $kw" || echo "MISSING: $kw"
done
```
Expected: 9 行全 `OK:`，无 `MISSING:`。

- [ ] **Step 4: 验证扫描命令无丢失**

Run:
```bash
echo "源 python3 扫描块数:"; grep -c "python3 -c" skills/note-audit-and-improvement/SKILL.md
echo "目标 python3 扫描块数:"; grep -c "python3 -c" skills/note-health/references/structural-checks.md
```
Expected: 目标 ≥ 源中属于扫描的数量（≥3）。

---

## Task 2: 迁移判断式打分 → references/leaf-quality.md

**Files:**
- Create: `skills/note-health/references/leaf-quality.md`
- Source: `skills/note-content-quality/SKILL.md`

**Interfaces:**
- Produces: `leaf-quality.md`，被 SKILL.md 的 Phase 2 及 health-workflow.js 引用。含具名小节：`## 通用 6 维度`（G1-G6）、`## 模块专属维度`（A~G 七类表）、`## 满分计算`、`## 特殊处理`、`## 评分等级`。

- [ ] **Step 1: 迁移打分内容**

把 content-quality SKILL.md 以下段落**原样搬入** `leaf-quality.md`：
- `### Step 2: 通用维度评分` G1-G6 表（cq L152-163）
- `### Step 3: 模块专属维度` 路径→规则决策表 + A/B/C/D/E/F/G 七类表（cq L165-261）
- `#### 满分计算`（cq L346-356）
- `#### 评分等级`表（cq L336-344）
- `## 特殊处理`（引子缺失=P0 / 叙事缺失=放错位置 / 新沉淀特殊关注，cq L360-383）
- `## Common Mistakes` 中**内容类**反模式表 + 流程 Mistake 1-7（cq L388-436）
- 单篇/批量报告格式（cq L265-334）

顶部加：`> 迁自 note-content-quality，由 note-health/SKILL.md Phase 2 与 health-workflow.js 调用`。

- [ ] **Step 2: 验证 7 类模块规则全在**

Run:
```bash
for cls in "A 类" "B 类" "C 类" "D 类" "E 类" "F 类" "G 类"; do
  grep -q "$cls" skills/note-health/references/leaf-quality.md && echo "OK: $cls" || echo "MISSING: $cls"
done
```
Expected: 7 行全 `OK:`。

- [ ] **Step 3: 验证维度条目数（G+A~G 无丢）**

Run:
```bash
echo "G 维度(应=6):"; grep -cE "^\| G[1-6] " skills/note-health/references/leaf-quality.md
echo "专属维度行(A1..G5):"; grep -cE "^\| [A-G][1-6] " skills/note-health/references/leaf-quality.md
```
Expected: G 维度 = 6；专属维度行 ≥ 31（A4+B4+C4+D6+E6+F4+G5 = 33，含 G1-G6 通用则更多——以 ≥31 为底线，人工核对 A~G 各类齐全）。

- [ ] **Step 4: 验证满分表与等级表在**

Run:
```bash
grep -q "满分" skills/note-health/references/leaf-quality.md && grep -q "⭐⭐⭐⭐⭐" skills/note-health/references/leaf-quality.md && echo "OK: 满分+等级表" || echo "MISSING"
```
Expected: `OK: 满分+等级表`。

---

## Task 3: 全库穷举 Workflow 脚本 → references/health-workflow.js

**Files:**
- Create: `skills/note-health/references/health-workflow.js`

**Interfaces:**
- Consumes: `args`（可选 `{ batchSize?: number }`，默认 6）。
- Produces: 可复用 workflow 脚本，全库 scope 时由 SKILL.md 指示调用；每 agent 按 `leaf-quality.md` 规则给一批文件打分，返回 `{file, moduleClass, total, grade, findings[]}` 数组；主循环聚合并写报告文件。

- [ ] **Step 1: 写 workflow 脚本**

```javascript
export const meta = {
  name: 'note-health-exhaustive',
  description: '全库穷举内容质量打分：按 leaf 文件批 fan-out，每 agent 5-8 篇',
  phases: [{ title: 'Score', detail: '每批 leaf 文件按 leaf-quality.md 打分' }],
}

// 主循环先把 leaf 文件清单通过 args 传入（避免脚本内跑 shell）
// args = { files: string[], batchSize?: number }
const files = (args && args.files) || []
const batchSize = (args && args.batchSize) || 6

if (files.length === 0) {
  log('未收到 leaf 文件清单，退出（请由 SKILL.md 先枚举后传入 args.files）')
  return { scored: [] }
}

// 切批：~batchSize 篇/agent
const batches = []
for (let i = 0; i < files.length; i += batchSize) {
  batches.push(files.slice(i, i + batchSize))
}
log(`共 ${files.length} 篇 → ${batches.length} 批（每批 ~${batchSize} 篇）`)

const SCHEMA = {
  type: 'object',
  properties: {
    results: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          moduleClass: { type: 'string' },
          total: { type: 'number' },
          maxScore: { type: 'number' },
          grade: { type: 'string' },
          findings: { type: 'array', items: { type: 'string' } },
        },
        required: ['file', 'moduleClass', 'total', 'grade'],
      },
    },
  },
  required: ['results'],
}

phase('Score')
const scored = await pipeline(
  batches,
  (batch, _orig, idx) => agent(
    `你是 note 内容质量评审。严格按 skills/note-health/references/leaf-quality.md 的规则给下列文件逐篇打分。\n` +
    `先按路径判断模块类型(A~G)，再用「通用 6 维度 + 该模块专属维度」评分，输出每篇的 total/maxScore/grade + 修复建议 findings。\n` +
    `文件清单(批 ${idx + 1}):\n${batch.map(f => '- ' + f).join('\\n')}`,
    { label: `score:batch-${idx + 1}`, phase: 'Score', schema: SCHEMA }
  ).then(r => (r && r.results) || [])
)

const flat = scored.filter(Boolean).flat()
log(`打分完成：${flat.length} 篇`)
return { scored: flat }
```

- [ ] **Step 2: 语法自检（node 解析）**

Run:
```bash
node --check skills/note-health/references/health-workflow.js && echo "OK: 语法通过"
```
Expected: `OK: 语法通过`。

- [ ] **Step 3: Commit（若用户已授权提交，否则跳过至最后统一处理）**

```bash
git add skills/note-health/references/
git commit -m "$(cat <<'EOF'
feat(skills): note-health references（结构扫描 + leaf 打分 + workflow）

- structural-checks.md 迁自 note-audit-and-improvement
- leaf-quality.md 迁自 note-content-quality
- health-workflow.js 全库穷举 fan-out（~6 篇/agent）

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: 薄 orchestrator → skills/note-health/SKILL.md

**Files:**
- Create: `skills/note-health/SKILL.md`

**Interfaces:**
- Consumes: `references/structural-checks.md`、`references/leaf-quality.md`、`references/health-workflow.js`。
- Produces: skill 入口，frontmatter `name: note-health`，触发词为两旧 skill 并集。

- [ ] **Step 1: 写 frontmatter + 触发描述**

```markdown
---
name: note-health
description: Use when user asks to audit or improve note/ — "note 哪里需要优化" / "note 有哪些问题" / "扫一遍 note" / "review note" / "体检" (structural audit) OR "评价 note 质量" / "这篇文章质量怎么样" / "质量验收" / "评分" (content quality). 单一分层体检：结构机械扫描 + leaf 判断式打分，全库穷举用 Workflow fan-out。
---
```

- [ ] **Step 2: 写 §1 scope 三档判断（进门第一闸）**

```markdown
## Step 0: scope 判断（第一闸）

| scope | 触发例 | 行为 |
|---|---|---|
| 单篇/单目录 | "评价 11.ai/RAG" | 只跑 Phase 2 leaf 打分（直接 Read + 按 leaf-quality.md 打分，**不启动 workflow**） |
| 单模块 | "审一下 06.spring" | Phase 1 结构扫该模块 + Phase 2 小规模 fan-out |
| 全库 | "note 哪里要优化" | 完整 4 相 + health-workflow.js 穷举 |

**原则**：单篇请求绝不启动重型机器。
```

- [ ] **Step 3: 写 §3 四相引擎 + references 指针**

```markdown
## 执行引擎：自底向上 4 相

### Phase 1 结构扫描（主循环内，便宜）
读 `references/structural-checks.md`，跑机械扫描。**大输出重定向到文件**（`> note/.health-tmp/scan-*.txt`），不堆进对话。

### Phase 2 Leaf 质量 fan-out
- 单篇/单模块：直接 Read + 按 `references/leaf-quality.md` 打分。
- 全库：枚举 leaf 文件清单，调用 `references/health-workflow.js`（`args={files:[...], batchSize:6}`），断点续跑用 `resumeFromRunId`。

枚举 leaf 文件：
\`\`\`bash
find note -name "*.md" | python3 -c "import sys,os; [print(l.strip()) for l in sys.stdin if l.count('/')>=3]"
\`\`\`

### Phase 3 逐层上卷
leaf findings → topic（兄弟互链/系列，来自 Phase 1）→ module（均分/README）→ repo（跨模块数字/架构，来自 Phase 1）。

### Phase 4 综合
结构 findings（Phase 1）+ 质量 findings（Phase 2/3）合并 → 统一 P0-P3 + 机械/判断分类 + 分批计划 → 写报告到 `note/.health-tmp/report-<date>.md`。
```

- [ ] **Step 4: 写 §5 综合输出格式 + Common Mistakes 指针**

搬入 audit 的「分批执行计划 + P0-P3 + 机械/判断分类」输出骨架（audit L463-532）与 content-quality 的「逐篇评分表 + 亮点」骨架（cq L307-334），合成统一 Output Format 小节。Common Mistakes 不重复正文，写：`结构类见 references/structural-checks.md；内容类见 references/leaf-quality.md`。

- [ ] **Step 5: 验证 SKILL.md 完整**

Run:
```bash
grep -q "^name: note-health" skills/note-health/SKILL.md && \
grep -q "scope" skills/note-health/SKILL.md && \
grep -q "Phase 1" skills/note-health/SKILL.md && grep -q "Phase 4" skills/note-health/SKILL.md && \
grep -q "health-workflow.js" skills/note-health/SKILL.md && \
grep -q "references/leaf-quality.md" skills/note-health/SKILL.md && \
echo "OK: SKILL.md 结构完整" || echo "MISSING 某项"
```
Expected: `OK: SKILL.md 结构完整`。

- [ ] **Step 6: 验证薄壳（行数受控）**

Run:
```bash
wc -l skills/note-health/SKILL.md
```
Expected: ≤ ~200 行（薄 orchestrator，重内容在 references）。

---

## Task 5: 删旧 skill + 更新交叉引用

**Files:**
- Delete: `skills/note-audit-and-improvement/`、`skills/note-content-quality/`
- Modify: `skills/note-knowledge-qa/SKILL.md:786-787`
- Modify: `CLAUDE.md:23-25, 68, 73-74`

**Interfaces:**
- Produces: 全仓 0 处指向旧 skill 名的引用；CLAUDE.md skill 表为 3 项。

- [ ] **Step 1: 删两个旧 skill 目录**

```bash
git rm -r skills/note-audit-and-improvement skills/note-content-quality 2>/dev/null || rm -rf skills/note-audit-and-improvement skills/note-content-quality
```

- [ ] **Step 2: 改 note-knowledge-qa 联动引用**

`skills/note-knowledge-qa/SKILL.md` L786-787 原文：
```
- 上游：`note-content-quality`（已沉淀的文章质量验收 → 间接影响本 skill 的答案质量）
- 下游：`note-audit-and-improvement`（本 skill 暴露的高频"note 未覆盖"主题可作为缺口数据）
```
改为：
```
- 上游：`note-health`（文章质量验收 + 结构体检 → 间接影响本 skill 的答案质量）
- 下游：`note-health`（本 skill 暴露的高频"note 未覆盖"主题可作为缺口数据）
```

- [ ] **Step 3: 改 CLAUDE.md tree（L23-25）**

原文：
```
├── .claude/skills/                # 项目级 meta-skill
    ├── note-precipitation-planning/
    └── note-audit-and-improvement/
```
改为：
```
├── .claude/skills/                # 项目级 meta-skill
    ├── note-precipitation-planning/
    └── note-health/
```

- [ ] **Step 4: 改 CLAUDE.md skill 计数 + 表（L68, L73-74）**

L68：`skills/` 为 4 个 skill 的**单一来源** → 改 `3 个 skill`。
L73-74 两行：
```
| `note-audit-and-improvement` | 用户问"note 哪里需要优化？" |
| `note-content-quality` | 用户问"这篇文章质量怎么样？" |
```
合并为一行：
```
| `note-health` | 用户问"note 哪里需要优化？" / "这篇文章质量怎么样？"（结构体检 + 内容打分） |
```

- [ ] **Step 5: 验证 0 残留引用**

Run:
```bash
grep -rn "note-audit-and-improvement\|note-content-quality" skills/ CLAUDE.md docs/ | grep -v "docs/superpowers/specs/2026-07-15\|docs/superpowers/plans/2026-07-15"
```
Expected: 无输出（设计/计划文档中的历史提及不算残留）。

- [ ] **Step 6: 验证 CLAUDE.md 表为 3 项**

Run:
```bash
grep -cE "^\| \`note-" CLAUDE.md
```
Expected: `3`（note-precipitation-planning / note-health / note-knowledge-qa）。

---

## Task 6: 同步镜像 + 最终验收

**Files:** 无新增（运行脚本 + 全量验收）

**Interfaces:**
- Consumes: Task 1-5 全部产物。
- Produces: 重建的 `.claude/skills/`、`.codex/skills/` 镜像（gitignore，不提交）；通过 spec 的迁移完整性清单。

- [ ] **Step 1: 跑 sync-skills.sh**

Run:
```bash
bash scripts/sync-skills.sh
```
Expected: 无 error 退出；输出含 note-health 同步成功。

- [ ] **Step 2: 验证镜像无旧 skill 残留（sync 若不 prune 则手动清）**

Run:
```bash
ls .claude/skills/ .codex/skills/ 2>/dev/null | sort -u
# 若出现 note-audit-and-improvement / note-content-quality，手动删：
# rm -rf .claude/skills/note-audit-and-improvement .claude/skills/note-content-quality
# rm -rf .codex/skills/note-audit-and-improvement .codex/skills/note-content-quality
```
Expected: 镜像含 `note-health`，不含两个旧名。

- [ ] **Step 3: 跑 spec 迁移完整性清单**

Run:
```bash
echo "1. 结构类 9 项:"; grep -cE "数字一致|H1|回链|孤岛|索引|内容重复|架构|系列完整|风险检查" skills/note-health/references/structural-checks.md
echo "2. 模块 7 类:"; grep -cE "[A-G] 类" skills/note-health/references/leaf-quality.md
echo "3. 旧引用残留:"; grep -rc "note-audit-and-improvement\|note-content-quality" skills/ CLAUDE.md | grep -v ":0" || echo "  0 残留"
echo "4. workflow 语法:"; node --check skills/note-health/references/health-workflow.js && echo "  OK"
echo "5. CLAUDE.md 表项:"; grep -cE "^\| \`note-" CLAUDE.md
```
Expected: 1≥9；2≥7；3 显示"0 残留"；4 显示 OK；5=3。

- [ ] **Step 4: Commit（用户授权后）**

```bash
git add -A
git commit -m "$(cat <<'EOF'
refactor(skills): 合并 audit + content-quality 为 note-health 分层体检

- 新 note-health：薄 orchestrator + references 分层引擎
- 删除 note-audit-and-improvement / note-content-quality
- 更新 note-knowledge-qa 联动引用 + CLAUDE.md skill 表(4→3)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review

**Spec 覆盖核对：**
- §1 scope 三档 → Task 4 Step 2 ✓
- §2 分层文件结构 → Task 1/2/3/4 创建 4 文件 ✓
- §3 四相引擎 → Task 4 Step 3 ✓
- §4 fan-out ~5-8 篇/agent → Task 3 workflow batchSize=6 ✓
- §5 综合输出（audit 分批 + cq 评分表）→ Task 4 Step 4 ✓
- §6 迁移清理（删旧/改引用/CLAUDE.md/sync）→ Task 5 + Task 6 ✓
- 迁移完整性清单 → Task 6 Step 3 ✓

**Placeholder 扫描：** 无 TBD/TODO；迁移步骤给出精确源行范围 + 目标小节 + 验证命令；新代码（workflow.js）给出完整脚本。

**类型/命名一致性：** health-workflow.js schema 字段（file/moduleClass/total/grade/findings）在 Task 3 定义，Task 4 Phase 2 与 Task 6 验收引用一致；references 文件名在 File Structure、各 Task、SKILL.md 指针中拼写一致。
