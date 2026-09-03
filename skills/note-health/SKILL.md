---
name: note-health
description: Use when user asks to audit or improve a project's knowledge base (default `note/`, configurable via `NOTE_DIR` env var) — "note 哪里需要优化" / "note 有哪些问题" / "扫一遍 note" / "review note" / "体检" (structural audit) OR "评价 note 质量" / "这篇文章质量怎么样" / "质量验收" / "评分" OR "刚写的这篇质量如何" / "新写的 README 看看" (new-file quality). 单一分层体检：结构机械扫描 + leaf 判断式打分，全库穷举用 Workflow fan-out。
---

> **规则来源**：执行前必读 `$KB_DIR/SPEC.md` §5（G1-G6 通用评分维度）+ §6（11 类基础扫描规则）+ §7（SPEC 分层元规范）+ `<module>/SPEC.md`（如 `$KB_DIR/01.java-and-jvm/SPEC.md` 的 A 类维度）；若目标模块有强骨架规范（如 `$KB_DIR/12.interview/QUESTION-FORMAT-SPEC.md` / `$KB_DIR/13.story/STORY-FORMAT-SPEC.md`）也一并读取（已在 `references/leaf-quality.md` 等处引用其硬性要求）。模块结构通过 `find note -maxdepth 1 -type d` 运行时读取，不硬编码。

# note-health：note 知识库健康检查

对 `$KB_DIR/` 跑**单一分层体检**：结构机械扫描 + leaf 判断式打分，自底向上 4 相，输出统一 P0-P3 + 分批计划 + 逐篇评分表。重内容放在 `references/`，本文件只留决策骨架。

## Step 0：scope 判断（第一闸）

| scope | 触发例 | 行为 |
|---|---|---|
| **空 / 不存在**（🆕 2026-09-03 测试新增） | `$KB_DIR/` 不存在 / `find` 返回 0 | **直接返回**："KB_DIR 为空或不存在，无可体检内容"。不进入 Phase 1；不报错；不启动 workflow。 |
| 单篇 / 单目录 | "评价某模块下某篇" / "这篇质量怎么样" / "这篇新写的质量如何" | **只跑 Phase 2**：直接 Read + 按 `references/leaf-quality.md` 打分。**不启动 workflow**。**新文件**先读 `references/new-file-baseline.md` 拿到 7 必选 + 3 可选结构基线。 |
| 单模块 | "审一下某模块"（运行时读取 `find note -maxdepth 1 -type d`） | Phase 1 扫该模块 + Phase 2 小规模 fan-out（视 leaf 数手工切批，≤ 6 篇/批）。 |
| 全库（leaf ≤ 1000） | "note 哪里要优化" / "扫一遍 note" / "体检" | 完整 4 相；Phase 2 直接走「分层采样 + 优先级列表」策略（关键问题全评 + 各模块代表采样）。 |
| 全库（leaf > 1000） | 同上，但实时 `find note -name "*.md" \| wc -l` > 1000 | **触发 Step 0.1 策略询问**：用 `AskUserQuestion` 让用户在「采样」/「穷举」/「混合」三选一，默认采样，**不再静默切换**。 |

**🆕 空 KB_DIR 检测（2026-09-03 测试新增）**：

```bash
# Step 0 启动前必跑（< 1 秒）
KB_DIR="${NOTE_DIR:-note}"  # 默认 note/，支持 NOTE_DIR 环境变量覆盖
if [ ! -d "$KB_DIR" ] || [ -z "$(find "$KB_DIR" -maxdepth 5 -name "*.md" -print -quit 2>/dev/null)" ]; then
  echo "⚠️  KB_DIR ($KB_DIR) 为空或不存在，无可体检内容"
  echo "    提示：检查 NOTE_DIR 环境变量 / .claude/knowledge-base.config.json 配置"
  exit 0
fi
```

**原则**：单篇请求绝不启动重型机器；leaf 数 < 10 直接手工打分，不开 workflow。

> **全库策略**（leaf > 50）：
> - **优先级批**：浅 README（< 50 行）+ 无回链 + 无 frontmatter + 全部 broken link 来源（必评）
> - **采样批**：每主模块随机 3-5 篇代表 leaf
> - **leaf ≤ 1000** → 直接走采样（无需询问）
> - **leaf > 1000** → **触发 Step 0.1 策略询问**（让用户显式选择）
> - leaf 数 ≤ 50 → 按单模块（主循环手工切批）

### Step 0.1：全库规模触发的策略询问（leaf > 1000）

> 🆕 **2026-08-23 新增**：当 Step 0 判 scope = 全库且实时 `find note -name "*.md" | wc -l` > 1000 时，**必须**用 `AskUserQuestion` 让用户在 3 种策略中显式选择，**不再静默切换**为采样。

**触发前先算 leaf 数**：

```bash
LEAF_COUNT=$(find note -name "*.md" | wc -l)
[ "$LEAF_COUNT" -gt 1000 ] && echo "全库 leaf = $LEAF_COUNT，超阈值，触发 Step 0.1 询问"
```

**询问选项**（默认 Recommended = 选项 A 采样）：

| 选项 | token 估算 | 时长 | 适用场景 |
|------|-----------|------|----------|
| **A. 分层采样 + 优先级列表** (Recommended) | ~200k | 30-60min | 日常 review / 快速定位主要问题 |
| **B. 全库 fan-out 穷举** | ~3M | 4-6h | release 前最终审计 / 用户明确要求穷举 |
| **C. 混合：采样 + 高风险模块下钻** | ~300-500k | 1-2h | 平衡成本与覆盖率，先采样定位高风险区再 fan-out 补全 |

**选项触发判定**（按用户原话 / 上下文匹配）：

| 选项 | 触发信号 |
|------|----------|
| A 采样（默认） | "扫一遍" / "体检" / "哪里要优化" 等日常表述 |
| B 穷举 | "穷举" / "全部" / "每一篇" / "all" / "exhaustive" / release 前最终审计 |
| C 混合 | "重点模块下钻" / "高风险区补全" / "采样后补全" |

**询问失败降级**：

- 用户中断 / 跳过 → 默认走选项 A 采样（最低风险）
- `AskUserQuestion` 工具不可用 → 同上，log 一条「策略询问跳过，降级为默认采样」

**3 条硬性原则**：

- **询问必须在 Phase 1 启动前完成**，否则已启动的扫描会浪费 token（subagent 不能调 AskUserQuestion，工具不可用）
- **询问本身不消耗扫描成本**——`AskUserQuestion` 是对话层动作，不进入 `.health-tmp`
- **询问结果写到 report 头部**——Phase 4 输出必须含「策略选择：<选项>」一行，让用户事后能验证实际跑了哪个策略

> ⚠️ **边缘 case：兄弟相对路径（如 polymorphism）**：当新增子目录（如 `polymorphism/README.md`），兄弟章节用 `[polymorphism](polymorphism/README.md)` 形式链接近似安全 —— 但 markdown 严格按相对路径解析，**从 `inner-class/README.md` 应解析到 `inner-class/polymorphism/README.md`**（不存在）。**Phase 1 §6 broken-links 扫描命中后需人工二次确认**「同目录」vs「跨目录」归属，特别是 polymorphism / distillation 这类子目录的兄弟链。**Obsidian / GitHub 可能因 auto-resolve 显示为 OK，但严格 markdown 规范下是 broken**。Phase 4 综合报告必须标 `[同目录-边缘]` 而非纯 `[真错]`。

**新文件专属入口**：当用户问的是"评价一个新沉淀的文件 / 这篇新写的质量如何"，Phase 2 在打分前必须先读 `references/new-file-baseline.md` 拿到 7 必选 + 3 可选结构模板 + 快改/深耕写作模式，作为结构基线；再用 `references/leaf-quality.md` 打分。两者结合判断"是否符合新文件基线 + 是否达到 leaf 质量门槛"。

> 判定为"新文件"的启发：用户提到"刚写的 / 新沉淀的 / 这次新加的 / 初稿"，或 git 近期新增（git log --since 近几天 --diff-filter=A）。

## 执行引擎：自底向上 4 相

### Phase 1 — 结构扫描（主循环内，便贵）

> 执行前先建临时目录：`mkdir -p note/.health-tmp`

读 `references/structural-checks.md`，跑机械扫描：**frontmatter 覆盖、orphan 目录、孤链（.md + 目录双口径）、README 总目录章节锚点、模块均分 + 单向链接扫描 + 系列完整性审计 + 数字一致性 + 归属合理性 + 合并检测**等。
**所有大输出重定向到文件**（`> note/.health-tmp/scan-<phase>-<date>.txt`），不堆进对话。Phase 1 不调 workflow。

> **2026-07-25 起**：单向链接扫描（`Step 4.5`）+ 系列完整性审计（`Step 9` + `9.1`）从深度模式提升为默认 Phase 1.8 / 1.9 / 1.10 —— Mistake 9（parent 不回链 = 隐性孤岛）是历史教训，全库 800+ README 的体检默认应该跑，下次不会再忘。

> **🆕 2026-07-26 起**：归属合理性审计（`Step 10`）+ 合并检测（`Step 11`）从深度模式提升为默认 Phase 1.11 / 1.12 —— 主题放错位置（如训练方法论放工程层）和多主题错误合并（如 5 个灵魂拷问合成一个文件）是结构性问题，体检默认应该跑。

> **🆕 2026-08-20 起**：关联强度扫描（`Step 12`）从可选提升为默认 Phase 1.13 —— 检测"同栏目 / 同目录"兄弟互链中目标文件 0 真实引用的弱关联（见 `note-precipitation-planning` Mistake 20）。弱关联比 broken link 更隐蔽——链接存在且路径正确，但语义上是噪声，应作为 P2 问题输出。

> **🆕 2026-08-25 起**：① 断链扫描升级为**双口径**（`.md` 文件链接 + `](dir/)` 目录链接）——目录链接曾是盲区，累积 156 处未检出（见 `structural-checks.md` #6）；② Phase 1.13 弱关联扫描改用**正文内链算法**（v2），排除页脚导航表/表格/代码块，消除 1005 处误报类噪声。

> **🆕 2026-09-02 起**：Phase 1 开头必跑 `check-broken-links.py`（双口径 + 全库 + 单文件）—— Session 6 教训：230 处断链批量修复后，必须作为体检的**第一闸**而非"发现时才跑"。统一入口避免 subagent 漏跑。

**关联强度扫描脚本**（Phase 1.13 · v2 2026-08-25 正文内链版，实测校准：1005 → 382）：

> v1（全文件关键词匹配）误报率极高：G4 要求的页脚"相关章节"兄弟互链天然不在正文重复关键词，2026-08-25 体检命中 1005 处绝大多数是合规导航。v2 四步降噪：**① 切掉代码块 ② 排除表格行（导航表）③ 页脚截断**（`← 返回` / `相关章节/交叉引用/系列导航/反向链` 标题之后）④ **排除祖先回链**（`../README.md` 式返回父级）；关键词检查在**含链接文本的正文**里做（链接文本提到主题 = 强关联）。实测从 1005 噪声降到 382 条基本可执行的跨模块引用候选。

```python
# Phase 1.13 v2：弱关联扫描（只扫正文内链，排除页脚导航表 / 表格 / 代码块 / 祖先回链）
import re, os, glob, sys
sys.stdout.reconfigure(encoding='utf-8')
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')

def body_only(content):
    content = re.sub(r'```.*?```', '', content, flags=re.S)          # ① 去代码块
    lines = [l for l in content.split('\n') if not l.strip().startswith('|')]  # ② 去表格行（导航表）
    cut = len(lines)
    for i, l in enumerate(lines):                                     # ③ 页脚截断
        if re.search(r'[←⬅]\s*\[?返回', l) or re.match(r'^#{1,3}\s*(🔗\s*)?(相关章节|交叉引用|系列导航|反向链|相关链接)\s*$', l):
            cut = i
            break
    return '\n'.join(lines[:cut])

weak = 0
for f in glob.glob('$KB_DIR/**/*.md', recursive=True):
    if '.health-tmp' in f.replace(os.sep, '/'): continue
    content = open(f, encoding='utf-8', errors='ignore').read()
    body = body_only(content)
    f_dir = os.path.dirname(os.path.abspath(f))
    for m in LINK_RE.finditer(body):
        t_abs = os.path.normpath(os.path.join(os.path.dirname(f), m.group(2)))
        if not os.path.isfile(t_abs): continue                        # broken 由 #6 处理
        t_dir = os.path.dirname(os.path.abspath(t_abs))
        try:                                                          # ④ 祖先回链（返回父级）跳过
            if os.path.commonpath([t_dir, f_dir]) == t_dir: continue
        except ValueError: pass
        try:
            tc = open(t_abs, encoding='utf-8', errors='ignore').read(2000)
        except Exception: continue
        h1 = re.search(r'^#\s+(.+)$', tc, re.M)                       # ⑤ 目标主题关键词 = H1
        kws = re.findall(r'[A-Za-z][A-Za-z0-9\-]{3,}|[一-鿿]{2,6}', (h1.group(1) if h1 else ''))
        if not kws: continue
        if all(k not in body for k in kws[:6]):                       # 正文（含链接文本）0 提及
            weak += 1
            print(f"  ⚠ 弱关联: {f} -> {m.group(2)}")
print(f"弱关联（正文内链口径）: {weak} 处")
```

**关联强度输出**：
- 弱关联列表 → 报告 P2 项 + 推荐"删除或补语义描述"（正文补一句目标主题与本文的关系）
- 不输出"强关联"（避免噪音）
- **页脚/表格内的导航互链永不判弱关联**——它们是 G4 互链要求的合规载体，语义关联由正文承载
- 历史案例：2026-08-20 file-upload 双层 → product-search（弱关联 0 命中），已修复

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

**与 difficulty 深度校准的衔接（🆕 2026-08-25）**：本阶段产出的五维分同时是 `difficulty` 深度校准的数据源——五维总分映射建议星级（9-10→⭐⭐⭐⭐ / 7-8→⭐⭐⭐ / 5-6→⭐⭐ / ≤4→⭐），偏差 ≥1 星进校准清单。完整执行流程见 `references/structural-checks.md` Step 15「深度校准流程」。全库打分时 `health-workflow.js` 已自动采集 `fiveDim`，无需单独再跑一轮五维评分。

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

## Phase 8 — 链接完整性强制校验（2026-09-02 新增）

> **触发条件**：任何"全库"或"单模块"scope 的体检，**Phase 1 启动前必跑**。

**目的**：Session 6 教训：230 处断链批量修复后，体检必须**第一闸**就是链接完整性，避免"subagent 自己写扫描脚本"导致扫描口径漂移。

**执行命令**：

```bash
# 全库扫描
python scripts/check-broken-links.py

# 或单模块
python scripts/check-broken-links.py --module 09.ai-applications
```

**接受标准**：

| 检查项 | 通过条件 |
|--------|---------|
| 断链数 | **= 0**（CI 月度 cron 模式）|
| 断链数 | **≤ 5**（单模块体检，允许边界 case）|
| 双口径 | .md 链接 + ](dir/) 目录链接 均扫描 |

**断链数 > 0 时处置**：

| 情况 | 处置 |
|------|------|
| 全库扫描 | **Phase 1 不启动**，先把断链修完再跑体检 |
| 单模块扫描 | 把断链列入 Phase 4 P0 必修项，与 Phase 2 评分同步修复 |
| 边界 case（如 README 同目录）| 标 `[同目录-边缘]`，人工二次确认 |

**与 §3.5 note-knowledge-qa 的区别**：

| 维度 | note-health §3.5 | note-knowledge-qa §3.5 |
|------|:---:|:---:|
| 时机 | 体检时（结构维度）| 检索时（QA 维度）|
| 范围 | 全库扫描 | 单次检索的目标文件 |
| 失败处置 | Phase 1 拒绝启动 | 在回答里标注"路径待修复" |
| 触发者 | orchestrator 跑体检 | 用户提问时检索 |

**反直觉 5**："subagent 自己写的扫描脚本更灵活" —— 灵活 ≠ 一致。Session 6 教训：subagent 自己写了 `scan-broken-links.py`，但口径与 Phase 1.6 略有差异，导致需要二次校验。**统一入口是 check-broken-links.py**，subagent 不应自创扫描脚本。

## Common Mistakes

**不重复正文，写指针**：
- **结构类**问题（frontmatter、orphan、孤链、目录结构）：见 `references/structural-checks.md`。
- **内容类**问题（深度、可读性、系列完整性）：见 `references/leaf-quality.md`。
- **新文件结构基线**（10 段模板 + 快改/深耕模式）：见 `references/new-file-baseline.md`。

执行本 skill 时遇到常见错误模式先查 references，再决定是否纳入 P0/P1。

## 调用示例

```
# 全库体检（leaf ≤ 1000）
"扫一遍 note 看看哪里要优化"
→ Step 0: 全库（leaf ≤ 1000），直接走采样
→ Phase 1: 跑 structural-checks.md 扫描，结果落 $KB_DIR/.health-tmp/scan-1-<date>.txt
→ Phase 2: find + python 枚举 leaf，调 health-workflow.js（args.files=...，batchSize=6）
→ Phase 3: 上卷
→ Phase 4: 写 $KB_DIR/.health-tmp/report-<date>.md，header 含「策略选择：A 采样」

# 全库体检（leaf > 1000）
"扫一遍 note 看看哪里要优化"
→ Step 0: 全库（leaf > 1000），触发 Step 0.1 策略询问
→ AskUserQuestion: 用户选 A/B/C（默认 A）
→ Phase 1-4 同上，header 含「策略选择：<选项>」

# 单篇质量验收
"评价 11.ai/RAG/README.md 这篇质量怎么样"
→ Step 0: 单篇
→ Phase 2: 直接 Read + leaf-quality.md 打分，不开 workflow
→ 直接在对话里给评分表 + findings
```
