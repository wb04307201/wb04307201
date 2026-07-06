# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Type

**双内容仓库**：
- **顶部 README.md** — 个人主页 + 12 个开源项目展示（File View、Spring AI LoomAgent、Flexible Lock 等）
- **`note/`** — 14 主模块的体系化技术知识库（基于 Obsidian 维护），638 个 README，900 个 .md

主体是文档（Markdown），不是源代码。Java/Spring 项目的源码在外部仓库（如 `wb04307201/file-view`）。

## note/ 架构（核心）

```
note/
├── README.md                      # 总目录 + 14 模块导航
├── CONTRIBUTING.md                # 写作规范（8-section 模板 / frontmatter / 命名 / 章节风格）
├── 01.java/ 02.computer-basics/   # 14 主模块，编号 + 英文 + 短横线
├── ...
├── 13.split-hairs/                # 高频面试题库（咬文嚼字，6 大分类 134+ 题）
├── 14.project-management/
└── .claude/skills/                # 项目级 meta-skill
    ├── note-precipitation-planning/
    └── note-audit-and-improvement/
```

**3 大沉淀模式**（沉淀主题时按规模选）：
- **单文件**（< 150 行）：主模块子 README
- **双层**（最常用）：13.split-hairs/<topic>/ + 11.ai/<module>/<topic>/ + 互链
- **三层 + 12.story 联动**：双层 + 12.story 加章节反向链

## 关键规范引用

| 主题 | 位置 |
|------|------|
| 模块命名 / 模板 / frontmatter / 章节风格 | `note/CONTRIBUTING.md` |
| 故事类章节格式（阿明餐厅） | `note/12.story/STORY-FORMAT-SPEC.md` |
| 面试题格式（咬文嚼字） | `note/13.split-hairs/QUESTION-FORMAT-SPEC.md` |
| 模块 README 标准结构（§12） | `note/CONTRIBUTING.md` §12 |

**所有模块 README 必备 frontmatter**（HTML 注释），3 种类型：
- `<!--module: ... -->`（主模块 + 子文章）
- `<!--question: ... -->`（13.split-hairs）
- `<!--story: ... -->`（12.story）

## 常用命令

```bash
# 验证 markdown 链接（CI 已自动跑，本地可手动）
# 注意：note 里的 `target/`、`.idea/`、`.claude/settings.local.json` 已在 .gitignore

# 模块结构概览
ls note/

# 单模块速览
ls note/01.java/ && cat note/01.java/README.md | head -50

# 找特定主题（grep + frontmatter 联动）
grep -rl "RAG" note/11.ai/ | head -10

# 检查 frontmatter 覆盖
find note -name "README.md" -exec grep -L "^<!--" {} \;
```

## Meta-Skills（项目级）

`.claude/skills/` 下 2 个项目共享 skill：

| Skill | 何时用 |
|-------|--------|
| `note-precipitation-planning` | 用户问"X 应该沉淀到 note 什么位置？" |
| `note-audit-and-improvement` | 用户问"note 哪里需要优化？" |

新沉淀主题时，优先用 `note-precipitation-planning` 输出"位置 + 方式"方案。

## CI Workflows

`.github/workflows/`：
- **`grs.yml`** — 每日 00:00 自动更新 `profile/stats.svg` + `top-langs.svg`（GitHub README 卡片）
- **`link-check.yml`** — push/PR/每周一 06:00 跑 markdown link check（`.mlc_config.json` 配置忽略规则）

## 工作流惯例

**沉淀新主题时的标准流程**（参考 `note-precipitation-planning` skill）：
1. **现状盘点**：grep / find 扫描 ≥ 5 个相关文件
2. **深度评估**：3 信号判断（高频 + 内容深 + 缺口真实）
3. **位置决策**：决策树（面试题→13.split-hairs / 深度原理→11.ai / 叙事→12.story）
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

- ❌ 不要在 commit message 虚报（"删除 6 个孤儿目录"但 git diff 没删）
- ❌ 不要 hardcode 数字（如 "47 篇"）—— 用 `find` 实时校对
- ❌ 不要忽略 `note/README.md` 总目录的章节锚点（每模块一行）
- ❌ 新建 leaf README 必须有 `← [返回: <模块>]` 回链
- ❌ subagent 不能直接调 `AskUserQuestion`（工具不可用），必须返回结构化选项

## 关键统计

- 14 主模块 / 638 README / 900 .md
- frontmatter 覆盖 100%（621/621 main + 13 专题 + 8 12.story）
- 116 PNG（教学截图保留，其他应 Mermaid 化）