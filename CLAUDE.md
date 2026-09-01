# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Type

**双内容仓库**：
- **顶部 README.md** — 个人主页 + **11 个开源项目**展示（File View、Spring AI LoomAgent、Flexible Lock 等）
- **`note/`** — 13 主模块的体系化技术知识库（基于 Obsidian 维护），**785 个 README、1106 个 .md**（2026-09-02 实测校对，排除 `.health-tmp` / `.obsidian`）

主体是文档（Markdown），不是源代码。Java/Spring 项目的源码在外部仓库（如 `wb04307201/file-view`）。

## note/ 架构（核心）

```
note/
├── README.md                      # 总目录 + 13 模块导航
├── SPEC.md                        # 全局规范（命名 / commit / 互链 / frontmatter / G1-G6 评分）
├── 01.java-and-jvm/               # Java + JVM + 并发 + 设计模式
├── 02.cs-foundations/             # 算法 + OS + 网络 + 数学
├── 03.data-stack/                 # 数据库 + 缓存 + 大数据
├── 04.spring-backend/             # Spring + 后端框架
├── 05.frontend/                   # 前端
├── 06.distributed-systems/        # 分布式 + 微服务 + 云原生
├── 07.devops-and-tools/           # CI/CD + 监控 + 工具
├── 08.ai-foundations/             # ML + DL + Transformer + LLM 基础
├── 09.ai-applications/            # RAG + Agent + Prompt + LLM 推理
├── 10.business-systems/           # 电商 + 社交 + 金融
├── 11.product-and-pm/             # 产品 + PM + 流程（含原 14.project-management 内容）
├── 12.interview/                  # 高频面试题（10 分类 192 题，10 个主题子目录）
│   ├── 01.java/ 02.computer-basics/ 03.database/ 04.system-design/
│   ├── 05.security/ 06.spring/ 09.front-end/ 10.big-data/ 11.ai/ tools/
│   └── QUESTION-FORMAT-SPEC.md     # 面试题格式 + 反直觉 / 陷阱 / 30 秒话术
└── 13.story/                      # 「阿明餐厅」技术系列（50 篇，平铺顶层）
    └── STORY-FORMAT-SPEC.md        # 故事类章节格式（开餐厅叙事 + 技术类比）

仓库根（仓库级 meta-skill，不在 note/ 内）：
├── skills/                        # 项目级 meta-skill 单一来源（git tracked）
└── .claude/skills/                # 自动镜像（gitignored）
```

**3 大沉淀模式**（沉淀主题时按规模选）：
- **单文件**（< 150 行）：主模块子 README（如 `03.data-stack/02.cache/01.redis-persistence.md`）
- **双层**（最常用）：`12.interview/<topic>/`（高频面试题版本）+ 对应主模块 `<topic>/`（深度原理版本）+ 互链回指
- **三层 + 13.story 联动**：双层 + `13.story/<NN>-xxx.md` 加章节反向链（叙事层包装讲透）

## 关键规范引用

> **写作规范的单一入口是 `note/SPEC.md`**（顶层规范）。  
> `note/CONTRIBUTING.md` 在历史上存在过，现已被 SPEC.md 替代；如下路径若 404，请改去 `note/SPEC.md`。

| 主题 | 位置 |
|------|------|
| 全局规范（命名 / commit / 互链 / frontmatter / G1-G6 评分 / 11 类扫描规则） | `note/SPEC.md` |
| 各模块自有 SPEC（评估维度 + 写作总则 + 子目录约定；11/12/13 等已落地） | `note/{NN}.xxx/SPEC.md` |
| 模块写作模板（仅 12 面试题 / 13 故事，强骨架模块按需存在，不与 SPEC.md 合并） | `note/12.interview/QUESTION-FORMAT-SPEC.md` / `note/13.story/STORY-FORMAT-SPEC.md` |

**知识文章 frontmatter 类型**（按 `slug` 字段分 3 类，HTML 注释格式 `<!--type: ... -->` 起首 + 多行字段 + `-->` 收尾；详见 `note/SPEC.md` §4）：
- `module:`（主模块 README + 子文章，跨所有 13 模块，现状 760 篇）
- `question:`（`12.interview` 高频面试题，现状 **227 篇**）
- `story:`（`13.story` 阿明餐厅，现状 **50 篇**）

> `SPEC.md` / `index.md` 等索引页豁免 frontmatter（21 个）。

## 常用命令

```bash
# 验证 markdown 链接（CI 已自动跑，本地可手动）
# 注意：note 里的 `target/`、`.idea/`、`.claude/settings.local.json` 已在 .gitignore

# 模块结构概览
ls note/

# 单模块速览
ls note/01.java-and-jvm/ && cat note/01.java-and-jvm/README.md | head -50

# 找特定主题（grep + frontmatter 联动）
grep -rl "RAG" note/09.ai-applications/ | head -10

# 检查 frontmatter 覆盖
find note -name "README.md" -exec grep -L "^<!--" {} \;
```

## Meta-Skills（项目级）

`skills/` 为 3 个 skill 的**单一来源**（自动镜像到 `.claude/skills/`，gitignored）：

| Skill | 何时用 |
|-------|--------|
| `note-precipitation-planning` | 用户问"X 应该沉淀到 note 什么位置？" |
| `note-health` | 用户问"note 哪里需要优化？" / "这篇文章质量怎么样？"（结构体检 + 内容打分） |
| `note-knowledge-qa` | 用户问技术问题，从 note/ 检索回答 |

**改 skill 只改 `skills/`**，pre-commit hook 会自动同步到 `.claude/skills/`。
手动同步：`bash scripts/sync-skills.sh`

新沉淀主题时，优先用 `note-precipitation-planning` 输出"位置 + 方式"方案。

## 新环境初始化（clone 后必做）

```bash
bash setup.sh   # 一键配置 git hooks + 生成 skill 镜像
```

`setup.sh` 会自动：
1. 配置 `git core.hooksPath → .githooks`（启用 skill 同步 hook）
2. 运行 `scripts/sync-skills.sh`（从 skills/ 生成 `.claude/skills/` 镜像）

**重要**：`.claude/skills/` 已在 `.gitignore` 中，不提交到 git。clone 后必须跑 `setup.sh` 才能使用 skill。

## Git Hooks（本地防护）

`.githooks/`（**2 个 hook，本地 commit 时立即反馈**）：

| Hook | 触发时机 | 职责 |
|------|---------|------|
| **`pre-commit`** | `git commit` 时 | 1) `skills/` 变更 → 自动同步到 `.claude/skills/` 镜像；2) staged `note/*.md` → `check-broken-links.py` 单文件校验（断链 > 0 拒绝 commit）|
| **`commit-msg`** | commit message 写入后 | 1) Conventional Commits 格式校验（type + scope + 描述，支持中文 scope）；2) 数字虚报警告（篇/处/个/项/次/分/pp/%）|

**与 CI 的层级关系**：

```
commit-msg  →  pre-commit  →  §7.2 自检  →  push/PR  →  monthly cron
(格式)       (本地链接)     (单文件)     (GH Actions)  (全库扫描)
```

5 层防护：commit-msg → pre-commit → §7.2 → GH Actions → 月度 cron

## CI Workflows

`.github/workflows/`（**4 个 workflow，每月 1 日阶梯式触发 + push/PR 即时反馈**）：

| Workflow | 触发时机 | 职责 |
|----------|---------|------|
| **`grs.yml`** | 每月 1 日 02:00 + workflow_dispatch | 更新 `profile/stats.svg` + `top-langs.svg`（GitHub README 卡片）|
| **`difficulty-calibration.yml`** | 每月 1 日 03:00 + PR（修改 note + scripts 时）| 5 维 depth 字段格式验证 + 月度 auto-calibrate.py 自动校准 |
| **`link-check.yml`** | 每月 1 日 04:00 + push/PR | 第三方 action 校验 HTTP/HTTPS 外链（`.mlc_config.json` 配置忽略规则）|
| **`structural-link-check.yml`** | 每月 1 日 06:00 + push/PR | 自研 `scripts/check-broken-links.py` 校验 note/ 内部相对路径（双口径：.md + 目录链接）|

**cron 阶梯**：02:00 / 03:00 / 04:00 / 06:00 — 4 个 job 在 4 小时内串行完成。

## 工作流惯例

**沉淀新主题时的标准流程**（参考 `note-precipitation-planning` skill）：
1. **现状盘点**：grep / find 扫描 ≥ 5 个相关文件
2. **深度评估**：3 信号判断（高频 + 内容深 + 缺口真实）
3. **位置决策**：决策树（面试题→`12.interview` / 深度原理→对应主模块（`08.ai-foundations` / `09.ai-applications` / `03.data-stack` / `06.distributed-systems` 等）/ 叙事→`13.story`）
4. **方式决策**：单 / 双 / 三层（按内容深度）
5. **选项呈现**：2-4 个选项让用户选
6. **实施**：派 subagent + 严格 commit 格式（`feat(<slug>)` / `fix(<slug>)` / `style(<slug>)`）
7. **验证**：git diff --check + 链接抽查 + 数字校对

**常见 commit 格式**：
- `refactor(<slug>): ...`（结构调整）
- `feat(<module>): ...`（新增内容）
- `fix(<module>): ...`（修复 / 数字校对）
- `style(<module>): ...`（润色 / 模板清理）
- `docs(<scope>): ...`（文档）

## 沉淀笔记时常见陷阱

- ❌ 不要在 commit message 虚报（"删除 6 个孤儿目录"但 git diff 没删）→ `commit-msg` hook 会警告
- ❌ 不要 hardcode 数字（如 "47 篇"）—— 用 `find` 实时校对
- ❌ 不要忽略 `note/README.md` 总目录的章节锚点（每模块一行）
- ❌ 新建 leaf README 必须有 `← [返回: <模块>]` 回链
- ❌ subagent 不能直接调 `AskUserQuestion`（工具不可用），必须返回结构化选项
- ❌ 不要在 commit 前不跑链接校验（`§7.1` 路径校验 + `§7.2` 单文件自检）—`pre-commit` hook 会兜底拦截

## 沉淀流程防护链（Session 6-9 新增）

**任何新增内容必须经过 4 道防护**：

| 步骤 | 触发时机 | 工具 | 详见 |
|------|---------|------|------|
| §7.1 链接路径校验 | 引用其他模块路径时 | Python 脚本模板 | `skills/note-precipitation-planning/SKILL.md` §7.1 |
| §7.2 单文件自检 | Step 6 subagent 完成后 | `check-broken-links.py` | `skills/note-precipitation-planning/SKILL.md` §7.2 |
| pre-commit hook | `git commit` 时 | `check-broken-links.py` 单文件 | `.githooks/pre-commit` |
| structural-link-check.yml | push/PR + 每月 1 日 06:00 | 全库扫描 + 增量 | `.github/workflows/structural-link-check.yml` |

**Session 6 教训**：230 处断链 = 87% 来自"结构重组遗留路径错位"。**唯一可靠标准是 `os.path.isfile(target_abs)`**，不要相信"我觉得路径是对的"。

## 健康度闭环（5 层防护）

```
commit-msg  →  pre-commit  →  §7.2 自检  →  push/PR  →  monthly cron
(格式)       (本地链接)     (单文件)     (GH Actions)  (全库扫描)
```

| 层 | 工具 | 阻塞时机 |
|----|------|---------|
| L1 | commit-msg | commit message 格式 |
| L2 | pre-commit | staged files 链接 |
| L3 | note-precipitation-planning §7.2 | orchestrator 自检 |
| L4 | structural-link-check.yml | PR 合并前 |
| L5 | 月度 cron + auto-calibrate | 持续监控 |

## 关键统计

### note/ 仓库（2026-09-02 实测）

- **13 主模块** / **785 README** / **1106 .md**（排除 .health-tmp / .obsidian）
- frontmatter 覆盖 **98.1%**（1085 / 1106：module 760 + question 227 + story 50 + 其他 48；剩余 21 为 SPEC.md / index.md 等索引页，按规范可豁免）
- 总 leaves：**925 篇**

### 健康度（Session 6-9 闭环）

| 维度 | 状态 | 达成轮次 |
|------|:---:|:---:|
| **结构断链** | **0** | Session 6（230→0）|
| **orphan 目录** | **0** | Session 6（1→0）|
| **实质弱关联** | **0** | Session 6（9→0）|
| **frontmatter 覆盖** | **98.1%** | 持续 |
| **5 维深度准确度** | **100%**（v18 验证 80/80）| Session 5-9（v4 43% → v18 100%）|
| **CI / Hook 层数** | **5 层** | Session 7-9 |
| **总 commits** | **111** | Session 5-9 累计 |

### 关键文档

- 5 PNG（教学截图保留，其他应 Mermaid 化）
- `skills/note-health/references/v18-sampling-report.md` — 最新 5 维验证
- `skills/note-health/references/health-metrics-convergence.md` — 3 指标收敛曲线
- `note/.health-tmp/report-2026-09-02.md` — Session 6 完整结构体检报告（本地保留）

### 自动校准工具链

- `scripts/auto-calibrate.py` v6 — 支持 v15 ground truth + v14 微调标准
- `scripts/check-broken-links.py` — 链接完整性回归测试（CI / Hook / 自检统一入口）
- `scripts/simulate-monthly-cron.sh` — 4 个 workflow 综合模拟