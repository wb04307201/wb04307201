---
name: note-health
description: Use when user asks to audit or improve note/ — "note 哪里需要优化" / "note 有哪些问题" / "扫一遍 note" / "review note" / "体检" (structural audit) OR "评价 note 质量" / "这篇文章质量怎么样" / "质量验收" / "评分" OR "刚写的这篇质量如何" / "新写的 README 看看" (new-file quality). 单一分层体检：结构机械扫描 + leaf 判断式打分，全库穷举用 Workflow fan-out。
---

# note-health：note 知识库健康检查

对 `note/` 跑**单一分层体检**：结构机械扫描 + leaf 判断式打分，自底向上 4 相，输出统一 P0-P3 + 分批计划 + 逐篇评分表。重内容放在 `references/`，本文件只留决策骨架。

## Step 0：scope 判断（第一闸）

| scope | 触发例 | 行为 |
|---|---|---|
| 单篇 / 单目录 | "评价 11.ai/RAG" / "这篇质量怎么样" | **只跑 Phase 2**：直接 Read + 按 `references/leaf-quality.md` 打分。**不启动 workflow**。 |
| 单模块 | "审一下 06.spring" | Phase 1 扫该模块 + Phase 2 小规模 fan-out（视 leaf 数手工切批，≤ 6 篇/批）。 |
| 全库 | "note 哪里要优化" / "扫一遍 note" / "体检" | 完整 4 相 + `references/health-workflow.js` 穷举。 |

**原则**：单篇请求绝不启动重型机器；leaf 数 < 10 直接手工打分，不开 workflow。

> leaf 数 ≤ 50 → 按单模块（主循环手工切批）；> 50 → 按全库走 health-workflow.js。

**新文件专属入口**：当用户问的是"评价一个新沉淀的文件 / 这篇新写的质量如何"，Phase 2 在打分前必须先读 `references/new-file-baseline.md` 拿到 10 段结构模板 + 快改/深耕写作模式，作为结构基线；再用 `references/leaf-quality.md` 打分。两者结合判断"是否符合新文件基线 + 是否达到 leaf 质量门槛"。

## 执行引擎：自底向上 4 相

### Phase 1 — 结构扫描（主循环内，便宜）

> 执行前先建临时目录：`mkdir -p note/.health-tmp`

读 `references/structural-checks.md`，跑机械扫描：frontmatter 覆盖、orphan 目录、孤链、README 总目录章节锚点、模块均分等。**所有大输出重定向到文件**（`> note/.health-tmp/scan-<phase>-<date>.txt`），不堆进对话。Phase 1 不调 workflow。

### Phase 2 — Leaf 质量 fan-out

- **单篇 / 单目录 / 单模块**：直接 Read + 按 `references/leaf-quality.md` 的 G1–G6 + A~G 维度打分，**不开 workflow**。
- **全库**：先用以下命令枚举 leaf 文件清单，再把清单通过 `args.files` 传给 workflow：

```bash
find note -name "*.md" | python3 -c "import sys,os; [print(l.strip()) for l in sys.stdin if l.count('/')>=3]"
```

然后调用 `references/health-workflow.js`（`args={files:[...], batchSize:6}`）。脚本按 ~6 篇/批 fan-out，每 agent 按 `references/leaf-quality.md` 打分并返回 `{file, moduleClass, total, maxScore, grade, findings}`。

**断点续跑**：脚本本身不做状态持久化；如需续跑，由调用方给 Workflow 工具传 `resumeFromRunId`，让 harness 从上次中断的批次开始。本 skill 不写任何续跑逻辑。

### Phase 3 — 逐层上卷

> 数据来源：Phase 2 的 workflow 返回值 scored[]（全库）或直接打分结果（单篇/单模块）。逐层上卷 = 在主循环内对 scored[] 按 topic 目录 / module 分组聚合，无需重读正文。

把 leaf findings 逐层上卷：
- **leaf** → 同 topic 兄弟互链 / 系列完整性（来自 Phase 1）
- **topic** → 模块级均分 / README 索引（来自 Phase 1）
- **module** → 跨模块数字 / 架构一致性（来自 Phase 1 跨模块扫描）
- **repo** → 总目录 / CONTRIBUTING / frontmatter 规范

### Phase 4 — 综合输出

把结构 findings（Phase 1）+ 质量 findings（Phase 2/3）合并成统一报告，写到 `note/.health-tmp/report-<date>.md`。详见下文「Output Format」。

## Output Format（统一报告骨架）

合并两套旧 skill 的输出：

### 1. 分批执行计划（P0-P3 + 机械/判断分类）

| 优先级 | 类别 | 含义 | 例 |
|---|---|---|---|
| P0 | 机械 | 必修，脚本可全自动改 | frontmatter 缺失、orphan 目录、孤链 |
| P0 | 判断 | 必修，需人审 | 与规范冲突的核心表述 |
| P1 | 机械 | 应修，批量可改 | README 章节锚点漂移 |
| P1 | 判断 | 应修，需重写 | 系列不完整、断章 |
| P2 | 机械 | 可修 | dead image 引用、过期链接 |
| P2 | 判断 | 可修 | 内容深度不够、可读性差 |
| P3 | 任意 | 锦上添花 | 亮点保留 / 未来沉淀方向 |

**分批执行计划表**（按 commit 批次组织）：

```
Batch 1 (P0 机械): <N 项> — 一条 commit 全部搞定
Batch 2 (P0 判断): <N 项> — 每项一条 commit
Batch 3 (P1 机械 + 判断): <N 项>
Batch 4 (P2): <N 项> — 集中改
Batch 5 (P3 / 亮点): 不动或单列
```

### 2. 逐篇评分表（来自 leaf-quality）

| 文件 | moduleClass | 总分 / 满分 | 等级 | 主要 findings |
|---|---|---|---|---|

### 3. 亮点（保留 / 不动）

列出不该改的优秀片段，作为后续沉淀的范例。

## Common Mistakes

**不重复正文，写指针**：
- **结构类**问题（frontmatter、orphan、孤链、目录结构）：见 `references/structural-checks.md`。
- **内容类**问题（深度、可读性、系列完整性）：见 `references/leaf-quality.md`。
- **新文件结构基线**（10 段模板 + 快改/深耕模式）：见 `references/new-file-baseline.md`。

执行本 skill 时遇到常见错误模式先查 references，再决定是否纳入 P0/P1。

## 调用示例

```
# 全库体检
"扫一遍 note 看看哪里要优化"
→ Step 0: 全库
→ Phase 1: 跑 structural-checks.md 扫描，结果落 note/.health-tmp/scan-1-<date>.txt
→ Phase 2: find + python3 枚举 leaf，调 health-workflow.js（args.files=...，batchSize=6）
→ Phase 3: 上卷
→ Phase 4: 写 note/.health-tmp/report-<date>.md

# 单篇质量验收
"评价 11.ai/RAG/README.md 这篇质量怎么样"
→ Step 0: 单篇
→ Phase 2: 直接 Read + leaf-quality.md 打分，不开 workflow
→ 直接在对话里给评分表 + findings
```
