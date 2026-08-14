---
name: note-health
description: Use when user asks to audit or improve note/ — "note 哪里需要优化" / "note 有哪些问题" / "扫一遍 note" / "review note" / "体检" (structural audit) OR "评价 note 质量" / "这篇文章质量怎么样" / "质量验收" / "评分" OR "刚写的这篇质量如何" / "新写的 README 看看" (new-file quality). 单一分层体检：结构机械扫描 + leaf 判断式打分，全库穷举用 Workflow fan-out。
---

> **规则来源**：执行前必读 `note/SPEC.md` §5（G1-G6 通用评分维度）+ §6（11 类基础扫描规则）+ `<module>/SPEC.md`（如 `note/01.java-and-jvm/SPEC.md` 的 A 类维度）。模块结构通过 `find note -maxdepth 1 -type d` 运行时读取，不硬编码。

# note-health：note 知识库健康检查

对 `note/` 跑**单一分层体检**：结构机械扫描 + leaf 判断式打分，自底向上 4 相，输出统一 P0-P3 + 分批计划 + 逐篇评分表。重内容放在 `references/`，本文件只留决策骨架。

## Step 0：scope 判断（第一闸）

| scope | 触发例 | 行为 |
|---|---|---|
| 单篇 / 单目录 | "评价某模块下某篇" / "这篇质量怎么样" / "这篇新写的质量如何" | **只跑 Phase 2**：直接 Read + 按 `references/leaf-quality.md` 打分。**不启动 workflow**。**新文件**先读 `references/new-file-baseline.md` 拿到 7 必选 + 3 可选结构基线。 |
| 单模块 | "审一下某模块"（运行时读取 `find note -maxdepth 1 -type d`） | Phase 1 扫该模块 + Phase 2 小规模 fan-out（视 leaf 数手工切批，≤ 6 篇/批）。 |
| 全库 | "note 哪里要优化" / "扫一遍 note" / "体检" | 完整 4 相；Phase 2 用「分层采样 + 优先级列表」策略（关键问题全评 + 各模块代表采样），**不直接走 health-workflow.js 全库穷举**（成本过高）。 |

**原则**：单篇请求绝不启动重型机器；leaf 数 < 10 直接手工打分，不开 workflow。

> **全库策略**（leaf > 50）：
> - **优先级批**：浅 README（< 50 行）+ 无回链 + 无 frontmatter + 全部 broken link 来源（必评）
> - **采样批**：每主模块随机 3-5 篇代表 leaf
> - **不直接走 health-workflow.js 全库 fan-out**：1000+ leaf × 6/批 ≈ 170+ 批 ≈ 200+ subagent，token 成本数百万，边际收益低
> - leaf 数 ≤ 50 → 按单模块（主循环手工切批）

> ⚠️ **边缘 case：兄弟相对路径（如 polymorphism）**：当新增子目录（如 `polymorphism/README.md`），兄弟章节用 `[polymorphism](polymorphism/README.md)` 形式链接近似安全 —— 但 markdown 严格按相对路径解析，**从 `inner-class/README.md` 应解析到 `inner-class/polymorphism/README.md`**（不存在）。**Phase 1 §6 broken-links 扫描命中后需人工二次确认**「同目录」vs「跨目录」归属，特别是 polymorphism / distillation 这类子目录的兄弟链。**Obsidian / GitHub 可能因 auto-resolve 显示为 OK，但严格 markdown 规范下是 broken**。Phase 4 综合报告必须标 `[同目录-边缘]` 而非纯 `[真错]`。

**新文件专属入口**：当用户问的是"评价一个新沉淀的文件 / 这篇新写的质量如何"，Phase 2 在打分前必须先读 `references/new-file-baseline.md` 拿到 7 必选 + 3 可选结构模板 + 快改/深耕写作模式，作为结构基线；再用 `references/leaf-quality.md` 打分。两者结合判断"是否符合新文件基线 + 是否达到 leaf 质量门槛"。

> 判定为"新文件"的启发：用户提到"刚写的 / 新沉淀的 / 这次新加的 / 初稿"，或 git 近期新增（git log --since 近几天 --diff-filter=A）。

## 执行引擎：自底向上 4 相

### Phase 1 — 结构扫描（主循环内，便贵）

> 执行前先建临时目录：`mkdir -p note/.health-tmp`

读 `references/structural-checks.md`，跑机械扫描：**frontmatter 覆盖、orphan 目录、孤链、README 总目录章节锚点、模块均分 + 单向链接扫描 + 系列完整性审计 + 数字一致性 + 归属合理性 + 合并检测**等。
**所有大输出重定向到文件**（`> note/.health-tmp/scan-<phase>-<date>.txt`），不堆进对话。Phase 1 不调 workflow。

> **2026-07-25 起**：单向链接扫描（`Step 4.5`）+ 系列完整性审计（`Step 9` + `9.1`）从深度模式提升为默认 Phase 1.8 / 1.9 / 1.10 —— Mistake 9（parent 不回链 = 隐性孤岛）是历史教训，全库 800+ README 的体检默认应该跑，下次不会再忘。

> **🆕 2026-07-26 起**：归属合理性审计（`Step 10`）+ 合并检测（`Step 11`）从深度模式提升为默认 Phase 1.11 / 1.12 —— 主题放错位置（如训练方法论放工程层）和多主题错误合并（如 5 个灵魂拷问合成一个文件）是结构性问题，体检默认应该跑。

### Phase 2 — Leaf 质量 fan-out

- **单篇 / 单目录 / 单模块**：直接 Read + 按 `references/leaf-quality.md` 的 G1–G6 + A~G 维度打分，**不开 workflow**。
- **全库**：先用以下命令枚举 leaf 文件清单，再把清单通过 `args.files` 传给 workflow：

```bash
find note -name "*.md" | python -c "import sys,os; [print(l.strip()) for l in sys.stdin if l.count('/')>=3]"
```

> 注：Windows 环境用 `python`（3.13+），macOS/Linux 也可用 `python3`。脚本应兼容两者。

然后调用 `references/health-workflow.js`（`args={files:[...], batchSize:6}`）。脚本按 ~6 篇/批 fan-out，每 agent 按 `references/leaf-quality.md` 打分并返回 `{file, moduleClass, total, maxScore, grade, findings}`。

**⚠️ Workflow 空结果降级**：如果 workflow 返回 `scored.length === 0`（常见原因：harness 调度失败、agent 全返回空），**不要卡住**，立即降级为手工 dispatch：
1. 把 files 清单按 ~6 篇/批切分
2. 用 `Agent` 工具逐批 dispatch（每批一个 agent），prompt 同 workflow 内的 agent prompt
3. 收集各 agent 返回的 JSON 结果，合并为 scored[]
4. 继续 Phase 3 上卷

降级时 log 一条：`workflow 返回空，降级为手工 dispatch N 批`。

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

### Phase 5 — 修复后验证（2026-07-27 新增）

> 执行 Batch 1+ 修复后必跑，确保修复实际落地而非"报告完成但 git 没 commit"。

**标准化验证流程**：

1. **commit 落地确认**：
   ```bash
   git log --oneline -N   # N = 本轮 commit 数，确认每条 commit 都有真实 hash
   ```

2. **工作树干净**：
   ```bash
   git status --short     # 应输出空（无 unstaged/untracked）
   ```

3. **内容质量达标**：
   ```bash
   wc -l FILE             # 扩充后文件行数 ≥ 目标值（如 ≥ 300 行）
   ```

4. **无新断链**：
   ```bash
   # 对本轮修改的每个文件跑 broken links 扫描
   python << 'PYEOF'
   import sys, os, re, glob
   if sys.platform == 'win32':
       try: sys.stdout.reconfigure(encoding='utf-8')
       except: pass
   LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
   for f in <本轮修改的文件列表>:
       c = open(f, encoding='utf-8', errors='ignore').read()
       for m in LINK_RE.finditer(c):
           target_abs = os.path.normpath(os.path.join(os.path.dirname(f), m.group(2).replace('/', os.sep)))
           if not os.path.isfile(target_abs):
               print(f'  ⚠ {f} -> {m.group(2)}')
   PYEOF
   ```

### Phase 6 — 5 维评分（用户提的"过于简单"判定）

> 🆕 **2026-08-10 新增**：当用户问"X 题是否过于简单"或"split-hairs 哪些该迁出"时，触发本阶段。在 Phase 1/2/5 之上做**内容质量评分**，与 E1-E6 格式完整性互补。

**5 维度定义**（每维 0-2 分，总分 0-10）：

| 维度 | 含义 |
|------|------|
| **D1 知识深度** | 源码级 + JVM/字节码 + 版本演进 |
| **D2 知识广度** | 跨主模块联动 |
| **D3 面试频次** | 真实面试出现频率 |
| **D4 追问空间** | 面试官可追问几层 |
| **D5 反直觉/陷阱** | 反直觉陷阱 / 生产事故案例 |

**阈值**：≥7 保留 / 4-6 灰色 / ≤3 迁出

**配套 E7-E11 评分表**：见 `references/leaf-quality.md` 末尾（E7-E11 节）。

**4 个实战教训**（2026-08-10 总结）：

1. **⚠️ 标题/文件名预筛 false positive 高达 70%**——`closure`、`prototype-chain`、`mysql-int-define`、`redis-eviction` 等看着基础但实际深度评分 8-10。**禁止仅基于文件名/行数判定**，必须 Read 全文。

2. **frontmatter `difficulty` 标记偏乐观**——本次发现 19 处 frontmatter difficulty 与实际内容深度不一致（16 处低估 + 3 处高估）。Phase 1 应加 **frontmatter 一致性校准**（见 structural-checks.md Step 15）。

3. **按子目录分批 dispatch 是高效模式**——避免单 agent 全库评估时的疲劳偏差（11.ai 体量大易被误杀）。按子目录 6-15 篇/agent，每个 agent 上下文清晰。

4. **灰色地带处置模式**——4-6 分的题有 3 种处置：① 保留（内容够）② 加 frontmatter 校准（difficulty 反映实际深度）③ 拆分综述（多主题合并文件违反 split-hairs 单点深挖定位）④ 迁出（保留 30s/90s 话术作为"速记卡"追加主模块）

### Phase 7 — 拆分检测（多主题错误合并）

> 🆕 **2026-08-10 新增**：原 split-hairs `02.computer-basics/machine-learning/README.md` 是 6 大算法综述（违反 split-hairs 单点深挖定位），已拆分为 6 个 single-topic deep-dive。

**判定标准**（任一为是 → 拆分）：

| 信号 | 阈值 |
|------|------|
| 文件覆盖 ≥3 个互不相关子主题 | 30s 话术对应不同子主题 |
| 标题过于宽泛 | "X 是什么"、"X 综述"、"X 全景"、"X 6 大" |
| 每个子主题都合格 | 但合并后违反单点定位 |

**拆分后**：
- 每个子主题 → 独立 `<topic>/README.md` + frontmatter（question 类型）
- 原综述文件删除（或保留为索引页，引用 6 个 deep-dive）
- 父 README 目录表更新

**验证通过标准**：
- ✅ 每条 commit 有真实 hash（不是"已 commit" 文字）
- ✅ `git status --short` 输出为空
- ✅ 扩充后行数 ≥ 300 行（或目标值）
- ✅ broken links 扫描输出为空（或只有预期的边缘 case）

**验证失败处理**：
- commit hash 缺失 → 立即补 commit
- 工作树有未提交修改 → 决定是否 commit 或 discard
- broken links → 立即修复，不要累积

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
→ Phase 2: find + python 枚举 leaf，调 health-workflow.js（args.files=...，batchSize=6）
→ Phase 3: 上卷
→ Phase 4: 写 note/.health-tmp/report-<date>.md

# 单篇质量验收
"评价 11.ai/RAG/README.md 这篇质量怎么样"
→ Step 0: 单篇
→ Phase 2: 直接 Read + leaf-quality.md 打分，不开 workflow
→ 直接在对话里给评分表 + findings
```
